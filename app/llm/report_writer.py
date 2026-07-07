from app.pipeline.review_summary import ReviewSummary
from app.reports.markdown_renderer import render_markdown_report


def generate_llm_safety_brief(summary: ReviewSummary) -> str:
    """Compatibility wrapper for the former free-form report writer.

    Literature synthesis now happens per signal from retrieved abstracts. Final
    report assembly remains deterministic so statistics and citations cannot be
    rewritten or dropped by a free-form generation step.
    """
    return render_markdown_report(summary)
