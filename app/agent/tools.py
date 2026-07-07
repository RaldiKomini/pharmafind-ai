from pathlib import Path
import re
from typing import Any

from app.agent.session_state import SESSION_STATE
from app.pipeline.review_summary import review_summary_to_dict
from app.pipeline.safety_review_pipeline import SafetyReviewConfig, run_safety_review
from app.reports.markdown_renderer import render_markdown_report
from app.reports.pdf_renderer import render_pdf_from_markdown


def _review_config(
    drug_name: str,
    analysis_days: int,
    min_case_count: int,
    min_prr: float,
    min_ror_ci_lower: float,
    max_signals: int,
    pubmed_candidate_count: int,
    max_pubmed_papers_per_signal: int,
) -> SafetyReviewConfig:
    return SafetyReviewConfig(
        drug_name=drug_name,
        analysis_days=analysis_days,
        min_case_count=min_case_count,
        min_prr=min_prr,
        min_ror_ci_lower=min_ror_ci_lower,
        max_signals=max_signals,
        pubmed_candidate_count=pubmed_candidate_count,
        max_pubmed_papers_per_signal=max_pubmed_papers_per_signal,
        use_embeddings=True,
        use_llm=False,
    )


def run_safety_review_tool(
    drug_name: str,
    analysis_days: int = 365,
    min_case_count: int = 5,
    min_prr: float = 2.0,
    min_ror_ci_lower: float = 1.0,
    max_signals: int = 10,
    pubmed_candidate_count: int = 25,
    max_pubmed_papers_per_signal: int = 5,
) -> dict[str, Any]:
    """Run and cache the deterministic PRR/ROR plus PubMed review."""
    summary = run_safety_review(
        _review_config(
            drug_name,
            analysis_days,
            min_case_count,
            min_prr,
            min_ror_ci_lower,
            max_signals,
            pubmed_candidate_count,
            max_pubmed_papers_per_signal,
        )
    )
    summary_dict = review_summary_to_dict(summary)
    markdown_report = render_markdown_report(summary)
    SESSION_STATE.last_drug_name = drug_name
    SESSION_STATE.last_review_summary = summary_dict
    SESSION_STATE.last_markdown_report = markdown_report
    return summary_dict


def render_cached_pdf_tool() -> dict[str, Any]:
    if SESSION_STATE.last_markdown_report is None:
        return {"success": False, "error": "No cached review available. Run a safety review first."}
    drug_name = SESSION_STATE.last_drug_name or "review"
    safe_name = re.sub(r"[^a-z0-9_-]+", "_", drug_name.strip().lower()).strip("_") or "review"
    output_path = Path("reports") / f"{safe_name}_safety_review.pdf"
    render_pdf_from_markdown(SESSION_STATE.last_markdown_report, output_path)
    SESSION_STATE.last_pdf_path = str(output_path)
    return {"success": True, "pdf_path": str(output_path)}


def explain_signal_tool(reaction: str) -> dict[str, Any]:
    """Return cached, auditable metrics and evidence for one signal."""
    if SESSION_STATE.last_review_summary is None:
        return {"success": False, "error": "No cached review available. Run a safety review first."}
    reaction_lower = reaction.strip().lower()
    for signal in SESSION_STATE.last_review_summary.get("signals", []):
        if signal.get("reaction", "").lower() == reaction_lower:
            return {
                "success": True,
                **signal,
                "explanation": (
                    "This reporting pattern passed the configured minimum case, PRR, "
                    "and ROR lower-confidence-bound thresholds. It is not evidence of incidence or causality."
                ),
            }
    return {"success": False, "error": f"No cached signal found for reaction: {reaction}"}


def compare_drugs_tool(
    drug_a: str,
    drug_b: str,
    analysis_days: int = 365,
    min_case_count: int = 5,
    min_prr: float = 2.0,
    min_ror_ci_lower: float = 1.0,
    max_signals: int = 10,
    pubmed_candidate_count: int = 25,
    max_pubmed_papers_per_signal: int = 5,
) -> dict[str, Any]:
    """Compare two independently calculated reporting-signal reviews."""
    common = (
        analysis_days,
        min_case_count,
        min_prr,
        min_ror_ci_lower,
        max_signals,
        pubmed_candidate_count,
        max_pubmed_papers_per_signal,
    )
    summary_a = run_safety_review(_review_config(drug_a, *common))
    summary_b = run_safety_review(_review_config(drug_b, *common))
    return {
        "drug_a": review_summary_to_dict(summary_a),
        "drug_b": review_summary_to_dict(summary_b),
        "comparison_note": (
            "This compares FAERS reporting disproportionality and retrieved PubMed evidence, "
            "not incidence, causal risk, or head-to-head clinical safety."
        ),
    }
