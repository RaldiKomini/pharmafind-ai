from dataclasses import dataclass
import requests
from typing import Any


PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

@dataclass(frozen=True)
class PubMedSearchConfig:
    drug_name:str
    reaction: str
    max_results: int = 5
    sort: str = "pub date"

@dataclass(frozen=True)
class PubMedPaperSummary:
    pmid: str
    title: str
    source: str
    pub_date: str


class PubMedClient:
    """
    Small PubMed client using NCBI E-utilities.

    This client searches literature only.
    It does not grade evidence or interpret medical meaning.
    """

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def search_papers(self, config: PubMedSearchConfig) -> list[PubMedPaperSummary]:
        ids = self._search_pubmed_ids(config)
        return self._fetch_summaries(ids)

    def _search_pubmed_ids(self, config: PubMedSearchConfig):

        query = f'("{config.drug_name}" [TITLE/ABSTRACT]) AND ("{config.reaction}" [TITLE/ABSTRACT])'

        params = {
            "db": "pubmed",
            "term": query,
            "retmode" : "json",
            "retmax" : config.max_results,
            "sort": config.sort,
        }

        response = requests.get(PUBMED_ESEARCH_URL, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    
    def _fetch_summaries(self, ids: list[str]) -> list[PubMedPaperSummary]:
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        }

        response = requests.get(
            PUBMED_ESUMMARY_URL,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        result = data.get("result", {})

        papers: list[PubMedPaperSummary] = []

        for pmid in ids:
            item = result.get(pmid, {})

            papers.append(
                PubMedPaperSummary(
                    pmid=pmid,
                    title=item.get("title", ""),
                    source=item.get("source"),
                    pub_date=item.get("pubdate"),
                )
            )

        return papers
