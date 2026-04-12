"""Tests for record endpoints."""
from flask.testing import FlaskClient


def _create_record(client: FlaskClient, auth_headers: dict, title: str = "Test Record", content: str = "Sample business content with a $50 expense"):
    return client.post("/api/records", json={
        "title": title,
        "content": content,
    }, headers=auth_headers)


class TestCreateRecord:
    def test_create_text_record(self, client: FlaskClient, auth_headers: dict):
        resp = _create_record(client, auth_headers)
        assert resp.status_code == 201
        record = resp.get_json()["record"]
        assert record["title"] == "Test Record"
        assert record["input_type"] == "text"
        assert record["summary"] is not None

    def test_create_record_no_content(self, client: FlaskClient, auth_headers: dict):
        resp = client.post("/api/records", json={"title": "Empty"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_record_empty_content(self, client: FlaskClient, auth_headers: dict):
        resp = client.post("/api/records", json={
            "title": "Empty",
            "content": "   ",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_record_unauthenticated(self, client: FlaskClient):
        resp = client.post("/api/records", json={
            "title": "No Auth",
            "content": "test",
        })
        assert resp.status_code == 401


class TestListRecords:
    def test_list_empty(self, client: FlaskClient, auth_headers: dict):
        resp = client.get("/api/records", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["records"] == []
        assert data["total"] == 0

    def test_list_with_records(self, client: FlaskClient, auth_headers: dict):
        _create_record(client, auth_headers, title="Record 1")
        _create_record(client, auth_headers, title="Record 2")
        resp = client.get("/api/records", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["total"] == 2

    def test_list_pagination(self, client: FlaskClient, auth_headers: dict):
        for i in range(5):
            _create_record(client, auth_headers, title=f"Record {i}")
        resp = client.get("/api/records?per_page=2&page=1", headers=auth_headers)
        data = resp.get_json()
        assert len(data["records"]) == 2
        assert data["pages"] == 3

    def test_list_search(self, client: FlaskClient, auth_headers: dict):
        _create_record(client, auth_headers, title="Invoice for client")
        _create_record(client, auth_headers, title="Meeting notes")
        resp = client.get("/api/records?search=invoice", headers=auth_headers)
        data = resp.get_json()
        assert data["total"] == 1
        assert data["records"][0]["title"] == "Invoice for client"

    def test_list_filter_status(self, client: FlaskClient, auth_headers: dict):
        resp = _create_record(client, auth_headers, title="Active")
        record_id = resp.get_json()["record"]["id"]
        client.patch(f"/api/records/{record_id}/status",
                     json={"status": "archived"}, headers=auth_headers)
        _create_record(client, auth_headers, title="Still Active")

        resp = client.get("/api/records?status=archived", headers=auth_headers)
        data = resp.get_json()
        assert data["total"] == 1
        assert data["records"][0]["title"] == "Active"


class TestGetRecord:
    def test_get_record_success(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.get(f"/api/records/{record_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["record"]["id"] == record_id

    def test_get_record_not_found(self, client: FlaskClient, auth_headers: dict):
        resp = client.get("/api/records/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_record_other_user(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        # Create second user
        client.post("/api/auth/signup", json={
            "email": "other@example.com",
            "password": "password123",
            "full_name": "Other User",
        })
        login_resp = client.post("/api/auth/login", json={
            "email": "other@example.com",
            "password": "password123",
        })
        other_token = login_resp.get_json()["token"]
        resp = client.get(f"/api/records/{record_id}",
                          headers={"Authorization": f"Bearer {other_token}"})
        assert resp.status_code == 404


class TestDeleteRecord:
    def test_delete_success(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.delete(f"/api/records/{record_id}", headers=auth_headers)
        assert resp.status_code == 200
        # Verify soft-deleted (not returned via API)
        resp = client.get(f"/api/records/{record_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_not_found(self, client: FlaskClient, auth_headers: dict):
        resp = client.delete("/api/records/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_already_deleted(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        client.delete(f"/api/records/{record_id}", headers=auth_headers)
        resp = client.delete(f"/api/records/{record_id}", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateStatus:
    def test_update_status_success(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}/status",
                            json={"status": "archived"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["record"]["status"] == "archived"

    def test_update_status_invalid(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}/status",
                            json={"status": "invalid"}, headers=auth_headers)
        assert resp.status_code == 400


class TestUpdateRecord:
    def test_update_title(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}",
                            json={"title": "Updated Title"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["record"]["title"] == "Updated Title"

    def test_update_category(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}",
                            json={"category": "invoice"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["record"]["category"] == "invoice"

    def test_update_empty_title(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}",
                            json={"title": ""}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_invalid_category(self, client: FlaskClient, auth_headers: dict):
        create_resp = _create_record(client, auth_headers)
        record_id = create_resp.get_json()["record"]["id"]
        resp = client.patch(f"/api/records/{record_id}",
                            json={"category": "bogus"}, headers=auth_headers)
        assert resp.status_code == 400
