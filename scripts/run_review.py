import argparse

from app.pipeline.faers_signal_pipeline import FaersSignalReviewConfig, run_faers_signal_review


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--analysis-days", type=int, default=365)
    parser.add_argument("--min-cases", type=int, default=5)
    parser.add_argument("--max-signals", type=int, default=10)
    args = parser.parse_args()

    result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name=args.drug,
            analysis_days=args.analysis_days,
            min_case_count=args.min_cases,
            max_signals=args.max_signals,
        )
    )
    print(f"Drug: {result.drug_name}")
    print(f"Analysis window: {result.analysis_start} to {result.analysis_end}")
    print(f"All reports: {result.total_report_count:,}")
    print(f"Drug reports: {result.drug_report_count:,}")
    print("\nFlagged reporting signals:")
    for signal in result.signals:
        print(
            f"- {signal.reaction}: cases={signal.case_count}, "
            f"PRR={signal.metrics.prr:.2f} "
            f"({signal.metrics.prr_ci_low:.2f}-{signal.metrics.prr_ci_high:.2f}), "
            f"ROR={signal.metrics.ror:.2f} "
            f"({signal.metrics.ror_ci_low:.2f}-{signal.metrics.ror_ci_high:.2f})"
        )


if __name__ == "__main__":
    main()
