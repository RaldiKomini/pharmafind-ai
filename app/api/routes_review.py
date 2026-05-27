import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAIError, RateLimitError

from app.api.schemas import SafetyReviewRequest, SafetyReviewResponse
from app.llm.report_writer import generate_llm_safety_brief
from app.pipeline.review_summary import review_summary_to_dict
from app.pipeline.safety_review_pipeline import (
    SafetyReviewConfig,
    run_safety_review,
)
from app.reports.markdown_renderer import render_markdown_report
from app.reports.pdf_renderer import render_pdf_from_markdown

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=SafetyReviewResponse)
def create_safety_review(request: SafetyReviewRequest) -> SafetyReviewResponse:
    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=request.drug_name,
            recent_days=request.recent_days,
            baseline_days=request.baseline_days,
            max_reports_per_window=request.max_reports_per_window,
            max_signals=request.max_signals,
            max_pubmed_papers_per_signal=request.max_pubmed_papers_per_signal,
        )
    )

    if request.use_llm:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
        try:
            markdown_report = generate_llm_safety_brief(summary)
        except RateLimitError:
            markdown_report = (
                "> LLM report generation was skipped because OpenAI rate-limited the request.\n\n"
                + render_markdown_report(summary)
            )
        except OpenAIError as exc:
            raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc.__class__.__name__}") from exc
    else:
        markdown_report = render_markdown_report(summary)

    return SafetyReviewResponse(
        summary=review_summary_to_dict(summary),
        markdown_report=markdown_report,
    )


@router.post("/pdf")
def create_safety_review_pdf(request: SafetyReviewRequest) -> FileResponse:
    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=request.drug_name,
            recent_days=request.recent_days,
            baseline_days=request.baseline_days,
            max_reports_per_window=request.max_reports_per_window,
            max_signals=request.max_signals,
            max_pubmed_papers_per_signal=request.max_pubmed_papers_per_signal,
        )
    )

    markdown_report = render_markdown_report(summary)

    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    safe_drug_name = request.drug_name.strip().lower().replace(" ", "_")
    output_path = output_dir / f"{safe_drug_name}_safety_review.pdf"

    render_pdf_from_markdown(
        markdown_text=markdown_report,
        output_path=output_path,
    )

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=output_path.name,
    )
