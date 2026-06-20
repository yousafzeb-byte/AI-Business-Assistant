from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from marshmallow import Schema, fields, validate, ValidationError

from app import db, limiter
from app.models.user import User
from app.utils.email import send_password_reset_email

import logging
logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


# ---------- Validation Schemas ----------

class SignupSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    full_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))


signup_schema = SignupSchema()
login_schema = LoginSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()


# ---------- Routes ----------

@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("5 per minute")
def signup():
    try:
        data = signup_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=data["email"], full_name=data["full_name"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({"token": access_token, "refresh_token": refresh_token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({"token": access_token, "refresh_token": refresh_token, "user": user.to_dict()}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limiter.limit("30 per minute")
def refresh():
    """Issue a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per minute")
def forgot_password():
    try:
        data = forgot_password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()

    # Always return success to prevent email enumeration
    if not user:
        return jsonify({"message": "If that email is registered, a reset link has been sent."}), 200

    token = user.generate_reset_token()
    db.session.commit()

    frontend_url = current_app.config["FRONTEND_URL"]
    reset_link = f"{frontend_url}/reset-password?token={token}"

    smtp_host = current_app.config.get("SMTP_HOST", "")
    if smtp_host:
        sent = send_password_reset_email(
            to_email=user.email,
            reset_link=reset_link,
            smtp_host=smtp_host,
            smtp_port=current_app.config.get("SMTP_PORT", 587),
            smtp_user=current_app.config.get("SMTP_USER", ""),
            smtp_password=current_app.config.get("SMTP_PASSWORD", ""),
            smtp_from=current_app.config.get("SMTP_FROM", "noreply@example.com"),
        )
        if not sent:
            logger.warning(
                "Email delivery failed for %s — reset link: %s",
                user.email, reset_link,
            )
    else:
        # SMTP not configured: log the link so developers can still test the flow
        logger.info(
            "SMTP not configured. Password reset link for %s: %s",
            user.email, reset_link,
        )

    return jsonify({"message": "If that email is registered, a reset link has been sent."}), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password():
    try:
        data = reset_password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(reset_token=data["token"]).first()

    if not user or not user.verify_reset_token():
        return jsonify({"error": "Invalid or expired reset token"}), 400

    user.set_password(data["password"])
    user.clear_reset_token()
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully."}), 200
