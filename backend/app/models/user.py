import secrets
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

RESET_TOKEN_EXPIRY_HOURS = 1


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reset_token = db.Column(db.String(128), unique=True, nullable=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    records = db.relationship("Record", backref="owner", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self) -> str:
        self.reset_token = secrets.token_urlsafe(64)
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
        return self.reset_token

    def verify_reset_token(self) -> bool:
        if not self.reset_token or not self.reset_token_expires:
            return False
        return datetime.now(timezone.utc) < self.reset_token_expires

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expires = None

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
