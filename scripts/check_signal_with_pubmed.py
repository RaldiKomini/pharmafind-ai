import argparse
import json

from app.pipeline.review_summary import review_summary_to_dict
from app.pipeline.safety_review_pipeline import SafetyReviewConfig, run_safety_review


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--analysis-days", type=int, default=365)
    parser.add_argument("--max-papers", type=int, default=5)
    args = parser.parse_args()
    summary = run_safety_review(
        SafetyReviewConfig(
            drug_name=args.drug,
            analysis_days=args.analysis_days,
            max_pubmed_papers_per_signal=args.max_papers,
        )
    )
    print(json.dumps(review_summary_to_dict(summary), indent=2))


if __name__ == "__main__":
    main()
