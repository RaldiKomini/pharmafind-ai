import argparse

from app.clients.faers_client import FaersClient, FaersQueryConfig
from app.pipeline.reaction_extractor import extract_all_reaction_terms
from app.pipeline.reaction_aggregator import aggregate_reactions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    client = FaersClient()
    reports = client.fetch_reports(
        FaersQueryConfig(
            drug_name=args.drug,
            limit=args.limit,
        )
    )

    reaction_terms = extract_all_reaction_terms(reports)
    top_reactions = aggregate_reactions(reaction_terms, top_k=args.top_k)

    print(f"Drug: {args.drug}")
    print(f"Reports fetched: {len(reports)}")
    print(f"Reaction terms extracted: {len(reaction_terms)}")
    print("\nTop reactions:")

    for reaction, count in top_reactions:
        print(f"{reaction}: {count}")


if __name__ == "__main__":
    main()