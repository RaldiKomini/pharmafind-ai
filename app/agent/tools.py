from typing import Any
from app.agent.session_state import SESSION_STATE
from app.pipeline.review_summary import review_summary_to_dict
from app.pipeline.safety_review_pipeline import (
    SafetyReviewConfig,
    run_safety_review,
)

from pathlib import Path
from app.reports.pdf_renderer import render_pdf_from_markdown
from app.reports.markdown_renderer import render_markdown_report

def run_safety_review_tool(
    drug_name: str,
    recent_days: int = 90,
    baseline_days: int = 365,
    max_reports_per_window: int = 1000,
    max_signals: int = 10,
    max_pubmed_papers_per_signal: int = 3,
) -> dict[str, Any]:
    """
    Run the deterministic review pipeline and cache the result for follow-ups.
    """
    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=drug_name,
            recent_days=recent_days,
            baseline_days=baseline_days,
            max_reports_per_window=max_reports_per_window,
            max_signals=max_signals,
            max_pubmed_papers_per_signal=max_pubmed_papers_per_signal,
        )
    )

    summary_dict = review_summary_to_dict(summary)
    markdown_report = render_markdown_report(summary)

    # Agent tools share a simple process-local cache so "explain that signal"
    # and "generate a PDF" can refer to the review that just ran.
    SESSION_STATE.last_drug_name = drug_name
    SESSION_STATE.last_review_summary = summary_dict
    SESSION_STATE.last_markdown_report = markdown_report
    return summary_dict


def render_cached_pdf_tool() -> dict[str, Any]:
    """
    Render a PDF from the last cached safety review.

    Does not rerun FAERS or PubMed.
    """
    if SESSION_STATE.last_markdown_report is None:
        return {
            "success": False,
            "error": "No cached review available. Run a safety review first.",
        }

    drug_name = SESSION_STATE.last_drug_name or "review"
    safe_name = drug_name.strip().lower().replace(" ", "_")

    output_path = Path("reports") / f"{safe_name}_safety_review.pdf"

    render_pdf_from_markdown(
        markdown_text=SESSION_STATE.last_markdown_report,
        output_path=output_path,
    )

    SESSION_STATE.last_pdf_path = str(output_path)

    return {
        "success": True,
        "pdf_path": str(output_path),
    }


def explain_signal_tool(reaction: str) -> dict[str, Any]:
    """
    Explain why a specific reaction was flagged in the last cached review.

    Does not rerun FAERS or PubMed.
    """
    if SESSION_STATE.last_review_summary is None:
        return {
            "success": False,
            "error": "No cached review available. Run a safety review first.",
        }

    signals = SESSION_STATE.last_review_summary.get("signals", [])

    reaction_lower = reaction.strip().lower()

    for signal in signals:
        if signal.get("reaction", "").lower() == reaction_lower:
            return {
                "success": True,
                "reaction": signal.get("reaction"),
                "recent_count": signal.get("recent_count"),
                "baseline_count": signal.get("baseline_count"),
                "recent_rate": signal.get("recent_rate"),
                "baseline_rate": signal.get("baseline_rate"),
                "ratio": signal.get("ratio"),
                "signal_score": signal.get("signal_score"),
                "evidence": signal.get("evidence"),
                "explanation": (
                    "This reaction was flagged because its recent reporting rate "
                    "was higher than its baseline reporting rate and it passed the "
                    "configured minimum count and ratio thresholds. This is a "
                    "reporting-pattern signal for human review, not evidence of causality."
                ),
            }

    return {
        "success": False,
        "error": f"No cached signal found for reaction: {reaction}",
    }


def compare_drugs_tool(
    drug_a: str,
    drug_b: str,
    recent_days: int = 90,
    baseline_days: int = 365,
    max_reports_per_window: int = 1000,
    max_signals: int = 10,
    max_pubmed_papers_per_signal: int = 3,
) -> dict[str, Any]:
    """
    Compare flagged safety signals for two drugs.

    This runs two deterministic safety reviews.
    """
    summary_a = run_safety_review(
        SafetyReviewConfig(
            drug_name=drug_a,
            recent_days=recent_days,
            baseline_days=baseline_days,
            max_reports_per_window=max_reports_per_window,
            max_signals=max_signals,
            max_pubmed_papers_per_signal=max_pubmed_papers_per_signal,
        )
    )

    summary_b = run_safety_review(
        SafetyReviewConfig(
            drug_name=drug_b,
            recent_days=recent_days,
            baseline_days=baseline_days,
            max_reports_per_window=max_reports_per_window,
            max_signals=max_signals,
            max_pubmed_papers_per_signal=max_pubmed_papers_per_signal,
        )
    )

    dict_a = review_summary_to_dict(summary_a)
    dict_b = review_summary_to_dict(summary_b)

    return {
        "drug_a": dict_a,
        "drug_b": dict_b,
        "comparison_note": (
            "This compares reporting-pattern signals from FAERS and PubMed evidence. "
            "It does not compare true medical risk or incidence."
        ),
    }
