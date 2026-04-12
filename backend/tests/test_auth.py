"""Tests for authentication endpoints."""
from flask.testing import FlaskClient  # type: ignore[import-untyped]


class TestSignup:
    def test_signup_success(self, client: FlaskClient):
        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["full_name"] == "New User"

    def test_signup_duplicate_email(self, client: FlaskClient):
        payload = {
            "email": "dup@example.com",
            "password": "password123",
            "full_name": "User One",
        }
        client.post("/api/auth/signup", json=payload)
        resp = client.post("/api/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_signup_short_password(self, client: FlaskClient):
        resp = client.post("/api/auth/signup", json={
            "email": "short@example.com",
            "password": "123",
            "full_name": "Short Pw",
        })
        assert resp.status_code == 400

    def test_signup_missing_fields(self, client: FlaskClient):
        resp = client.post("/api/auth/signup", json={"email": "a@b.com"})
        assert resp.status_code == 400

    def test_signup_invalid_email(self, client: FlaskClient):
        resp = client.post("/api/auth/signup", json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Bad Email",
        })
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client: FlaskClient):
        client.post("/api/auth/signup", json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        assert "token" in resp.get_json()

    def test_login_wrong_password(self, client: FlaskClient):
        client.post("/api/auth/signup", json={
            "email": "wrong@example.com",
            "password": "password123",
            "full_name": "Wrong Pw",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: FlaskClient):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestMe:
    def test_get_me_success(self, client: FlaskClient, auth_headers: dict):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["user"]["email"] == "test@example.com"

    def test_get_me_no_token(self, client: FlaskClient):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


class TestRefresh:
    def test_refresh_success(self, client: FlaskClient):
        signup_resp = client.post("/api/auth/signup", json={
            "email": "refresh@example.com",
            "password": "password123",
            "full_name": "Refresh User",
        })
        refresh_token = signup_resp.get_json()["refresh_token"]
        resp = client.post("/api/auth/refresh", headers={
            "Authorization": f"Bearer {refresh_token}",
        })
        assert resp.status_code == 200
        assert "token" in resp.get_json()

    def test_refresh_with_access_token_fails(self, client: FlaskClient, auth_headers: dict):
        resp = client.post("/api/auth/refresh", headers=auth_headers)
        assert resp.status_code == 422 or resp.status_code == 401
