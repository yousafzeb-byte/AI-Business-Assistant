import logging
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, validate, ValidationError
import bleach

from app import db
from app.models.record import Record
from app.services.ai_service import analyze_content, AIAnalysisError
from app.utils.file_helpers import allowed_file, validate_file_mime, extract_text_from_file
from app import limiter

logger = logging.getLogger(__name__)

records_bp = Blueprint("records", __name__)


# ---------- Validation Schemas ----------

class UpdateRecordSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=255))
    category = fields.Str(validate=validate.OneOf(
        ["invoice", "receipt", "note", "task", "contract", "report", "other"]
    ))


update_schema = UpdateRecordSchema()


@records_bp.route("", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def create_record():
    """Create a new record from text input or file upload."""
    user_id = int(get_jwt_identity())
    content = None
    input_type = "text"
    file_name = None
    title = "Untitled"

    # Handle file upload
    if "file" in request.files:
        file = request.files["file"]
        if file.filename and allowed_file(file.filename):
            # Validate MIME type matches extension
            if not validate_file_mime(file):
                return jsonify({"error": "File content does not match its extension"}), 400
            input_type = "file"
            file_name = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{user_id}_{file_name}")
            file.save(file_path)
            try:
                content = extract_text_from_file(file_path, file_name)
            except ValueError:
                return jsonify({"error": "Could not extract text from the uploaded file"}), 400
            finally:
                # Clean up uploaded file after extraction
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except OSError:
                    logger.warning("Failed to clean up uploaded file: %s", file_path)
            title = bleach.clean(request.form.get("title", file_name), strip=True)
        else:
            return jsonify({"error": "File type not allowed. Use: txt, pdf, md, csv"}), 400
    else:
        # Handle text input
        data = request.get_json()
        if not data or not data.get("content"):
            return jsonify({"error": "Content is required"}), 400
        content = data["content"]
        title = bleach.clean(data.get("title", "Untitled"), strip=True)

    if not content or not content.strip():
        return jsonify({"error": "Empty content"}), 400

    content = bleach.clean(content, strip=True)

    # AI analysis
    try:
        analysis = analyze_content(content)
    except AIAnalysisError:
        return jsonify({"error": "AI analysis failed. Please try again later."}), 503

    # Parse due_date if present
    due_date = None
    if analysis.get("due_date"):
        try:
            due_date = datetime.fromisoformat(analysis["due_date"])
        except (ValueError, TypeError):
            due_date = None

    record = Record(
        user_id=user_id,
        title=title,
        input_type=input_type,
        original_content=content,
        file_name=file_name,
        summary=analysis.get("summary"),
        extracted_data=analysis.get("extracted_data"),
        action_items=analysis.get("action_items"),
        category=analysis.get("category"),
        total_cost=analysis.get("total_cost"),
        due_date=due_date,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({"record": record.to_dict()}), 201


@records_bp.route("", methods=["GET"])
@jwt_required()
def list_records():
    """List records for the current user with optional search & pagination."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)  # cap at 100

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()

    query = Record.query.filter_by(user_id=user_id, deleted_at=None)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Record.title.ilike(search_filter),
                Record.summary.ilike(search_filter),
                Record.original_content.ilike(search_filter),
            )
        )
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(Record.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "records": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


@records_bp.route("/<int:record_id>", methods=["GET"])
@jwt_required()
def get_record(record_id):
    """Get a single record by ID."""
    user_id = int(get_jwt_identity())
    record = Record.query.filter_by(id=record_id, user_id=user_id, deleted_at=None).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"record": record.to_dict()}), 200


@records_bp.route("/<int:record_id>", methods=["DELETE"])
@jwt_required()
def delete_record(record_id):
    """Soft-delete a record."""
    user_id = int(get_jwt_identity())
    record = Record.query.filter_by(id=record_id, user_id=user_id, deleted_at=None).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404
    record.soft_delete()
    db.session.commit()
    return jsonify({"message": "Record deleted"}), 200


@records_bp.route("/<int:record_id>/status", methods=["PATCH"])
@jwt_required()
def update_record_status(record_id):
    """Update record status (processed, pending, archived)."""
    user_id = int(get_jwt_identity())
    record = Record.query.filter_by(id=record_id, user_id=user_id, deleted_at=None).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ("processed", "pending", "archived"):
        return jsonify({"error": "Invalid status"}), 400

    record.status = new_status
    db.session.commit()
    return jsonify({"record": record.to_dict()}), 200


@records_bp.route("/<int:record_id>", methods=["PATCH"])
@jwt_required()
def update_record(record_id):
    """Update editable fields of a record."""
    user_id = int(get_jwt_identity())
    record = Record.query.filter_by(id=record_id, user_id=user_id, deleted_at=None).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    try:
        data = update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if not data:
        return jsonify({"error": "No valid data provided"}), 400

    if "title" in data:
        record.title = data["title"]
    if "category" in data:
        record.category = data["category"]

    db.session.commit()
    return jsonify({"record": record.to_dict()}), 200
