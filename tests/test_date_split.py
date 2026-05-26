import argparse
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.clients.faers_client import FaersClient, FaersQueryConfig
from app.pipeline.date_filter import split_recent_and_baseline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    client = FaersClient()
    reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=args.drug,
            limit=args.limit,
        )
    )

    recent_reports, baseline_reports = split_recent_and_baseline(reports)

    print(f"Drug: {args.drug}")
    print(f"Total reports fetched: {len(reports)}")
    print(f"Recent reports: {len(recent_reports)}")
    print(f"Baseline reports: {len(baseline_reports)}")


if __name__ == "__main__":
    main()
