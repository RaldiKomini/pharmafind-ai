import argparse
from datetime import date, timedelta

from app.clients.faers_client import FaersClient, FaersQueryConfig
from app.pipeline.reaction_extractor import extract_all_reaction_terms
from app.pipeline.reaction_aggregator import count_reactions
from app.pipeline.baseline_comparator import compare_reaction_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--min-recent-count", type=int, default=5)
    args = parser.parse_args()

    client = FaersClient()

    today = date.today()

    recent_start = today - timedelta(days=90)
    recent_end = today

    baseline_end = recent_start - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=365)

    recent_reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=args.drug,
            start_date=recent_start,
            end_date=recent_end,
            limit=args.limit,
        )
    )

    baseline_reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=args.drug,
            start_date=baseline_start,
            end_date=baseline_end,
            limit=args.limit,
        )
    )

    recent_terms = extract_all_reaction_terms(recent_reports)
    baseline_terms = extract_all_reaction_terms(baseline_reports)

    recent_counts = count_reactions(recent_terms)
    baseline_counts = count_reactions(baseline_terms)



    comparisons = compare_reaction_counts(
        recent_counts=recent_counts,
        baseline_counts=baseline_counts,
        total_recent_reports=len(recent_reports),
        total_baseline_reports=len(baseline_reports),
    )

    from app.pipeline.signal_detector import detect_signals, SignalDetectionConfig

    signals = detect_signals(
        comparisons,
        SignalDetectionConfig(
            min_recent_count=10,
            min_baseline_count=3,
            min_ratio=2.0,
            max_signals=20,
        ),
    )
    print(f"Drug: {args.drug}")
    print(f"Recent reports: {len(recent_reports)}")
    print(f"Baseline reports: {len(baseline_reports)}")
    print("\nTop increased reactions:")

    printed = 0
    for item in signals:
        if item.recent_count < args.min_recent_count:
            continue
        if item.baseline_count == 0:
            continue
        if printed >= 30:
            break

        ratio = "inf" if item.ratio == float("inf") else f"{item.ratio:.2f}"

        print(
            f"{item.reaction}: "
            f"recent={item.recent_count}, "
            f"baseline={item.baseline_count}, "
            f"ratio={item.ratio:.2f}, "
            f"score={item.signal_score:.2f}"
        )
        printed += 1


if __name__ == "__main__":
    main()
