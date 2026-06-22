import argparse

from app.clients.pubmed_client import PubMedClient, PubMedSearchConfig
from app.pipeline.evidence_grader import grade_pubmed_evidence
from app.pipeline.faers_signal_pipeline import (
    FaersSignalReviewConfig,
    run_faers_signal_review,
)
from app.pipeline.safety_signal import build_safety_signal

import json

from app.pipeline.review_summary import (
    build_review_summary,
    review_summary_to_dict,
)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--max-papers", type=int, default=5)
    args = parser.parse_args()

    faers_result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name=args.drug,
            max_reports_per_window=args.limit,
        )
    )

    pubmed_client = PubMedClient()

    safety_signals = []

    for signal in faers_result.signals:
        papers = pubmed_client.search_papers(
            PubMedSearchConfig(
                drug_name=args.drug,
                reaction=signal.reaction,
                max_results=args.max_papers,
            )
        )

        evidence = grade_pubmed_evidence(papers)
        safety_signals.append(build_safety_signal(signal, evidence))

    print(f"Drug: {args.drug}")
    print(f"Signals with PubMed evidence:\n")

    for signal in safety_signals:
        print(
            f"- {signal.reaction}: "
            f"recent={signal.recent_count}, "
            f"baseline={signal.baseline_count}, "
            f"ratio={signal.ratio:.2f}, "
            f"score={signal.signal_score:.2f}, "
            f"pubmed={signal.evidence.paper_count}, "
            f"evidence={signal.evidence.evidence_grade}"
        )

        for paper in signal.evidence.papers[:2]:
            print(f"  - {paper.title} ({paper.pub_date})")


    summary = build_review_summary(
        drug_name=faers_result.drug_name,
        recent_start=faers_result.recent_start,
        recent_end=faers_result.recent_end,
        baseline_start=faers_result.baseline_start,
        baseline_end=faers_result.baseline_end,
        recent_report_count=faers_result.recent_report_count,
        baseline_report_count=faers_result.baseline_report_count,
        signals=safety_signals,
    )

    print(json.dumps(review_summary_to_dict(summary), indent=2))

if __name__ == "__main__":
    main()