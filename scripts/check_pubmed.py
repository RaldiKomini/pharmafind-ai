import argparse

from app.clients.pubmed_client import PubMedClient, PubMedSearchConfig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drug", required=True)
    parser.add_argument("--reaction", required=True)
    parser.add_argument("--max-results", type=int, default=5)
    args = parser.parse_args()

    client = PubMedClient()

    papers = client.search_papers(
        PubMedSearchConfig(
            drug_name=args.drug,
            reaction=args.reaction,
            candidate_count=args.max_results,
        )
    )

    print(f"Query: {args.drug} + {args.reaction}")
    print(f"Total papers found: {papers.total_result_count}")
    print(f"Abstracts retrieved: {len(papers.papers)}")

    for paper in papers.papers:
        print(f"- {paper.title} ({paper.pub_date}) [PMID {paper.pmid}]")
        print(f"  {paper.abstract[:300]}")


if __name__ == "__main__":
    main()
