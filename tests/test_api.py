from datetime import date

from fastapi.testclient import TestClient

from app.api import routes_review
from app.main import app
from app.pipeline.review_summary import build_review_summary


client = TestClient(app)


def test_review_endpoint_returns_typed_v2_contract(monkeypatch):
    summary = build_review_summary(
        drug_name="Example",
        analysis_start=date(2025, 1, 1),
        analysis_end=date(2025, 12, 31),
        total_report_count=1000,
        drug_report_count=10,
        pubmed_search_terms=["Example", "Example ingredient"],
        signals=[],
    )
    monkeypatch.setattr(routes_review, "run_safety_review", lambda config: summary)

    response = client.post(
        "/reviews",
        json={
            "drug_name": "Example",
            "analysis_days": 365,
            "min_case_count": 5,
            "min_prr": 2,
            "min_ror_ci_lower": 1,
            "max_signals": 10,
            "pubmed_candidate_count": 25,
            "max_pubmed_papers_per_signal": 5,
            "use_embeddings": False,
            "use_llm": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["analysis_start"] == "2025-01-01"
    assert payload["summary"]["pubmed_search_terms"] == ["Example", "Example ingredient"]
    assert "PRR" in payload["markdown_report"]


def test_review_request_rejects_invalid_thresholds():
    response = client.post(
        "/reviews",
        json={"drug_name": "Example", "min_case_count": 0},
    )
    assert response.status_code == 422


def test_grounded_synthesis_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/reviews",
        json={"drug_name": "Example", "use_llm": True},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "OPENAI_API_KEY is not set"


def test_pdf_endpoint_renders_existing_markdown_report():
    response = client.post(
        "/reviews/pdf",
        json={
            "drug_name": "Example",
            "markdown_report": "# Safety Review Brief: Example\n\n| Reaction | Cases |\n|---|---:|\n| nausea | 10 |\n",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
