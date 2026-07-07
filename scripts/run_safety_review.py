import argparse
from pathlib import Path
import re

from app.pipeline.safety_review_pipeline import SafetyReviewConfig, run_safety_review
from app.reports.markdown_renderer import render_markdown_report
from app.reports.pdf_renderer import render_pdf_from_markdown


def make_safe_filename(value: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower()).strip("_") or "review"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--analysis-days", type=int, default=365)
    parser.add_argument("--min-cases", type=int, default=5)
    parser.add_argument("--max-signals", type=int, default=10)
    parser.add_argument("--max-papers", type=int, default=5)
    parser.add_argument("--use-llm", action="store_true")
    args = parser.parse_args()

    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=args.drug,
            analysis_days=args.analysis_days,
            min_case_count=args.min_cases,
            max_signals=args.max_signals,
            max_pubmed_papers_per_signal=args.max_papers,
            use_llm=args.use_llm,
        )
    )
    markdown_report = render_markdown_report(summary)
    output_path = Path("reports") / f"{make_safe_filename(args.drug)}_safety_review.pdf"
    render_pdf_from_markdown(markdown_report, output_path)
    print(f"PDF saved to: {output_path}")


if __name__ == "__main__":
    main()
