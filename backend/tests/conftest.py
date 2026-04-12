import pytest
from app import create_app, db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
    SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
    OPENAI_API_KEY = ""
    RATELIMIT_ENABLED = False
    FRONTEND_URL = "http://localhost:5173"
    UPLOAD_FOLDER = "/tmp/test-uploads"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Register a test user and return the JWT token."""
    resp = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
    })
    return resp.get_json()["token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
