import argparse

from app.pipeline.faers_signal_pipeline import (
    FaersSignalReviewConfig,
    run_faers_signal_review,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    args = parser.parse_args()

    result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name=args.drug,
        )
    )

    print(f"Drug: {result.drug_name}")
    print(f"Recent window: {result.recent_start} to {result.recent_end}")
    print(f"Baseline window: {result.baseline_start} to {result.baseline_end}")
    print(f"Recent reports: {result.recent_report_count}")
    print(f"Baseline reports: {result.baseline_report_count}")

    print("\nFlagged reporting signals:")

    for signal in result.signals:
        print(
            f"- {signal.reaction}: "
            f"recent={signal.recent_count}, "
            f"baseline={signal.baseline_count}, "
            f"ratio={signal.ratio:.2f}, "
            f"score={signal.signal_score:.2f}"
        )


if __name__ == "__main__":
    main()