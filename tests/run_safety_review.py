import argparse
from pathlib import Path

from app.pipeline.safety_review_pipeline import (
    SafetyReviewConfig,
    run_safety_review,
)
from app.reports.markdown_renderer import render_markdown_report
from app.reports.pdf_renderer import render_pdf_from_markdown


def make_safe_filename(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--recent-days", type=int, default=90)
    parser.add_argument("--baseline-days", type=int, default=365)
    parser.add_argument("--max-signals", type=int, default=20)
    parser.add_argument("--max-papers", type=int, default=5)
    args = parser.parse_args()

    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=args.drug,
            recent_days=args.recent_days,
            baseline_days=args.baseline_days,
            max_reports_per_window=args.limit,
            max_signals=args.max_signals,
            max_pubmed_papers_per_signal=args.max_papers,
        )
    )

    markdown_report = render_markdown_report(summary)

    output_path = Path("reports") / f"{make_safe_filename(args.drug)}_safety_review.pdf"

    render_pdf_from_markdown(
        markdown_text=markdown_report,
        output_path=output_path,
    )

    print(f"PDF saved to: {output_path}")


if __name__ == "__main__":
    main()