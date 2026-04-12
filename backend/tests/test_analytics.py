"""Tests for analytics endpoint."""
from flask.testing import FlaskClient


def _create_record(client: FlaskClient, auth_headers: dict, title: str = "Test", content: str = "Business content worth $100"):
    return client.post("/api/records", json={
        "title": title,
        "content": content,
    }, headers=auth_headers)


class TestAnalyticsSummary:
    def test_summary_empty(self, client: FlaskClient, auth_headers: dict):
        resp = client.get("/api/analytics/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_records"] == 0
        assert data["total_expenses"] == 0
        assert data["categories"] == {}
        assert data["pending_actions"] == []

    def test_summary_with_records(self, client: FlaskClient, auth_headers: dict):
        _create_record(client, auth_headers, title="Rec 1")
        _create_record(client, auth_headers, title="Rec 2")
        resp = client.get("/api/analytics/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_records"] == 2

    def test_summary_unauthenticated(self, client: FlaskClient):
        resp = client.get("/api/analytics/summary")
        assert resp.status_code == 401
