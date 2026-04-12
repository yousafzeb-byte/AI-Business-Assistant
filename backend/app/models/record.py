from datetime import datetime, timezone
from app import db


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    input_type = db.Column(db.String(50), nullable=False)  # "text" | "file"
    original_content = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=True)

    # AI outputs
    summary = db.Column(db.Text, nullable=True)
    extracted_data = db.Column(db.JSON, nullable=True)  # dates, costs, tasks, deadlines
    action_items = db.Column(db.JSON, nullable=True)  # suggested next steps

    # Metadata
    category = db.Column(db.String(100), nullable=True, index=True)
    total_cost = db.Column(db.Float, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="processed", index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "input_type": self.input_type,
            "original_content": self.original_content,
            "file_name": self.file_name,
            "summary": self.summary,
            "extracted_data": self.extracted_data,
            "action_items": self.action_items,
            "category": self.category,
            "total_cost": self.total_cost,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
