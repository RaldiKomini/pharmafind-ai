import argparse
from app.clients.faers_client import FaersClient, FaersQueryConfig


def extract_reaction_terms(report: dict) -> list[str]:
    reactions = report.get("patient", {}).get("reaction", [])

    terms = []
    for reaction in reactions:
        term = reaction.get("reactionmeddrapt")
        if term:
            terms.append(term.lower())

    return terms





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--limit", type = int, default=100)
    args = parser.parse_args()

    client = FaersClient()
    reports = client.fetch_reports(
        FaersQueryConfig(drug_name=args.drug, limit=args.limit)
    )

    all_terms = []
    
    for report in reports:
        all_terms.extend(extract_reaction_terms(report))

    print(f"Drug: {args.drug}")
    print(f"Reports fetched: {len(reports)}")
    print("First reaction terms:")

    for term in all_terms[:20]:
        print(f"- {term}")


if __name__ == "__main__":
    main()
