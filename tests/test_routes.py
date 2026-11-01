
import pytest

from app import create_app
from backend.database import init_db


@pytest.fixture
def client(tmp_path):
    app = create_app()

    test_database = str(tmp_path / "test_reports.db")

    app.config["TESTING"] = True
    app.config["DATABASE_PATH"] = test_database

    init_db(test_database)

    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_verify_page(client):
    response = client.get("/verify")

    assert response.status_code == 200


def test_intelligence_page(client):
    response = client.get("/intelligence")

    assert response.status_code == 200


def test_health_api(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "online"


def test_empty_analysis(client):
    response = client.post(
        "/api/analyze",
        json={}
    )

    assert response.status_code == 400


def test_invalid_json(client):
    response = client.post(
        "/api/analyze",
        data="invalid",
        content_type="application/json"
    )

    assert response.status_code == 400


def test_successful_text_analysis(client):
    response = client.post(
        "/api/analyze",
        json={
            "text": "Please send your OTP."
        }
    )

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["report_id"] > 0


def test_report_is_saved(client):
    analysis_response = client.post(
        "/api/analyze",
        json={
            "text": "Please send your OTP."
        }
    )

    report_id = analysis_response.json["report_id"]

    response = client.get(
        f"/api/report/{report_id}"
    )

    assert response.status_code == 200
    assert response.json["id"] == report_id


def test_dashboard_stats_update(client):
    client.post(
        "/api/analyze",
        json={
            "text": "Please send your OTP."
        }
    )

    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json["total_reports"] == 1
    assert response.json["needs_review"] == 1


def test_reports_api(client):
    response = client.get("/api/reports")

    assert response.status_code == 200
    assert "reports" in response.json


def test_report_download(client):
    analysis_response = client.post(
        "/api/analyze",
        json={
            "text": "Please send your OTP."
        }
    )

    report_id = analysis_response.json["report_id"]

    response = client.get(
        f"/api/report/{report_id}/download"
    )

    assert response.status_code == 200
    assert "application/json" in response.content_type


def test_missing_report(client):
    response = client.get("/api/report/99999")

    assert response.status_code == 404
