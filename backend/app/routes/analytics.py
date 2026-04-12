from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app import db
from app.models.record import Record

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    """Return high-level analytics for the current user."""
    user_id = int(get_jwt_identity())

    base_filter = (Record.user_id == user_id, Record.deleted_at.is_(None))

    total_records = Record.query.filter(*base_filter).count()

    total_expenses = (
        db.session.query(func.coalesce(func.sum(Record.total_cost), 0))
        .filter(*base_filter, Record.total_cost.isnot(None))
        .scalar()
    )

    category_counts = (
        db.session.query(Record.category, func.count(Record.id))
        .filter(*base_filter)
        .group_by(Record.category)
        .all()
    )

    status_counts = (
        db.session.query(Record.status, func.count(Record.id))
        .filter(*base_filter)
        .group_by(Record.status)
        .all()
    )

    # Collect all action items across records
    records_with_actions = (
        Record.query.filter(
            *base_filter,
            Record.action_items.isnot(None),
            Record.status != "archived",
        )
        .order_by(Record.created_at.desc())
        .limit(50)
        .all()
    )

    pending_actions = []
    for record in records_with_actions:
        if isinstance(record.action_items, list):
            for item in record.action_items:
                pending_actions.append({
                    "record_id": record.id,
                    "record_title": record.title,
                    **item,
                })

    return jsonify({
        "total_records": total_records,
        "total_expenses": float(total_expenses),
        "categories": {cat: cnt for cat, cnt in category_counts},
        "statuses": {st: cnt for st, cnt in status_counts},
        "pending_actions": pending_actions[:20],  # limit to 20
    }), 200
