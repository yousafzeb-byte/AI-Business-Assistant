import logging
import os
import re
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import Config, _build_cors_origins

# ---------- Structured logging ----------
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
    )
)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)


def _is_allowed_origin(origin: str, allowed_origins: list[object]) -> bool:
    """Return True when the request origin matches configured allowed origins."""
    for allowed_origin in allowed_origins:
        if isinstance(allowed_origin, str) and allowed_origin == origin:
            return True
        if hasattr(allowed_origin, "match") and re.match(allowed_origin, origin):
            return True
    return False


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Use config-driven rate limit storage (Redis in production)
    limiter._storage_uri = app.config.get("RATELIMIT_STORAGE_URI", "memory://")
    limiter.init_app(app)

    allowed_origins = app.config.get("CORS_ORIGINS") or _build_cors_origins(app.config["FRONTEND_URL"])

    CORS(
        app,
        origins=allowed_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=600,
    )

    # Ensure upload folder exists with restricted permissions
    os.makedirs(app.config["UPLOAD_FOLDER"], mode=0o750, exist_ok=True)

    # ---------- Security headers ----------
    @app.after_request
    def set_security_headers(response):
        request_origin = request.headers.get("Origin")
        if request_origin and _is_allowed_origin(request_origin, allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = request_origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Max-Age"] = "600"
            response.headers["Vary"] = "Origin"

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        if not app.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # ---------- Global error handlers ----------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

    # ---------- JWT error handlers ----------
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization required"}), 401

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.records import records_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(records_bp, url_prefix="/api/records")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    # Health check — verifies database connectivity
    @app.route("/api/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception:
            logger.exception("Health check failed")
            return jsonify({"status": "degraded", "database": "unavailable"}), 503

    return app
