from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

RESUME_TEXT = (
    "Data scientist with 4 years of professional experience. Built Python and SQL "
    "machine-learning APIs on AWS and improved model accuracy by 18 percent. "
    "Bachelor of Science in Computer Science."
)
JOB_TEXT = (
    "Required: 3+ years of experience with Python, SQL, machine learning, and REST APIs. "
    "A bachelor's degree is required. AWS and Kubernetes are preferred qualifications."
)


def test_text_analysis_contract():
    response = client.post(
        "/analyze/text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_TEXT},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["algorithm_version"] == "hybrid-explainable-v1"
    assert 0 <= payload["overall_score"] <= 100
    assert "Kubernetes" in payload["skills"]["missing_preferred_skills"]
    assert payload["experience"]["matched"] is True
    assert payload["education"]["matched"] is True
    assert payload["recommendations"]


def test_short_job_description_is_rejected():
    response = client.post(
        "/analyze/text",
        json={"resume_text": RESUME_TEXT, "job_description": "Too short"},
    )
    assert response.status_code == 422
    assert "at least" in response.json()["detail"]


def test_methodology_endpoint_documents_guardrails():
    response = client.get("/explain")
    assert response.status_code == 200
    payload = response.json()
    assert payload["algorithm_version"] == "hybrid-explainable-v1"
    assert payload["guardrails"]
