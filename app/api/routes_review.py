import os
from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import requests

from app.api.schemas import (
    SafetyReviewPdfRequest,
    SafetyReviewRequest,
    SafetyReviewResponse,
)
from app.pipeline.review_summary import review_summary_to_dict
from app.pipeline.safety_review_pipeline import SafetyReviewConfig, run_safety_review
from app.reports.markdown_renderer import render_markdown_report
from app.reports.pdf_renderer import render_pdf_from_markdown


router = APIRouter(prefix="/reviews", tags=["reviews"])


def _build_config(request: SafetyReviewRequest) -> SafetyReviewConfig:
    return SafetyReviewConfig(
        drug_name=request.drug_name.strip(),
        analysis_days=request.analysis_days,
        min_case_count=request.min_case_count,
        min_prr=request.min_prr,
        min_ror_ci_lower=request.min_ror_ci_lower,
        max_signals=request.max_signals,
        pubmed_candidate_count=request.pubmed_candidate_count,
        max_pubmed_papers_per_signal=request.max_pubmed_papers_per_signal,
        use_embeddings=request.use_embeddings,
        use_llm=request.use_llm,
    )


def _run_review(request: SafetyReviewRequest):
    if request.use_llm and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
    try:
        return run_safety_review(_build_config(request))
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="An external FAERS or PubMed request failed.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("", response_model=SafetyReviewResponse)
def create_safety_review(request: SafetyReviewRequest) -> SafetyReviewResponse:
    """Run the review and return typed structured data plus deterministic Markdown."""
    summary = _run_review(request)
    return SafetyReviewResponse(
        summary=review_summary_to_dict(summary),
        markdown_report=render_markdown_report(summary),
    )


@router.post("/pdf")
def create_safety_review_pdf(request: SafetyReviewPdfRequest) -> Response:
    """Render the already-generated review Markdown and return a PDF."""
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    safe_drug_name = re.sub(
        r"[^a-z0-9_-]+",
        "_",
        request.drug_name.strip().lower(),
    ).strip("_") or "review"
    download_name = f"{safe_drug_name}_safety_review.pdf"
    output_path = output_dir / f"{safe_drug_name}_{uuid4().hex}_safety_review.pdf"
    try:
        render_pdf_from_markdown(request.markdown_report, output_path)
        pdf_bytes = output_path.read_bytes()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        output_path.unlink(missing_ok=True)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
