from dataclasses import dataclass, replace
import os
from typing import Any
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


@dataclass(frozen=True)
class PubMedSearchConfig:
    """PubMed candidate-retrieval settings for one drug/reaction pair."""

    drug_name: str
    reaction: str
    drug_aliases: tuple[str, ...] = ()
    candidate_count: int = 25
    sort: str = "relevance"


@dataclass(frozen=True)
class PubMedPaperSummary:
    """PubMed metadata and abstract used for retrieval and grounded synthesis."""

    pmid: str
    title: str
    source: str = ""
    pub_date: str = ""
    abstract: str = ""
    doi: str | None = None
    publication_types: tuple[str, ...] = ()
    relevance_score: float | None = None

    @property
    def url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


@dataclass(frozen=True)
class PubMedSearchResult:
    """Total query hits plus the bounded candidate records retrieved."""

    total_result_count: int
    papers: list[PubMedPaperSummary]


def _retrying_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def _pubmed_term(value: str) -> str:
    return " ".join(value.replace('"', " ").split())


def _build_pubmed_query(config: PubMedSearchConfig) -> str:
    drug_terms: list[str] = []
    for value in (config.drug_name, *config.drug_aliases):
        cleaned = _pubmed_term(value)
        if cleaned and cleaned.casefold() not in {term.casefold() for term in drug_terms}:
            drug_terms.append(cleaned)
    reaction = _pubmed_term(config.reaction)
    drug_query = " OR ".join(
        f'"{drug}"[Title/Abstract] OR "{drug}"[MeSH Terms]'
        for drug in drug_terms
    )
    return (
        f'({drug_query}) AND '
        f'("{reaction}"[Title/Abstract] OR "{reaction}"[MeSH Terms])'
    )


class PubMedClient:
    """NCBI E-utilities client that retrieves relevance-ranked abstracts."""

    def __init__(
        self,
        timeout: int = 30,
        session: requests.Session | None = None,
    ):
        self.timeout = timeout
        self.session = session or _retrying_session()

    def _identity_params(self) -> dict[str, str]:
        params: dict[str, str] = {
            "tool": os.getenv("NCBI_TOOL", "pharmafind-ai"),
        }
        if os.getenv("NCBI_EMAIL"):
            params["email"] = os.environ["NCBI_EMAIL"]
        if os.getenv("NCBI_API_KEY"):
            params["api_key"] = os.environ["NCBI_API_KEY"]
        return params

    def search_papers(self, config: PubMedSearchConfig) -> PubMedSearchResult:
        """Search by relevance and fetch full abstracts for the returned PMIDs."""
        total, ids = self._search_pubmed_ids(config)
        return PubMedSearchResult(
            total_result_count=total,
            papers=self._fetch_abstracts(ids),
        )

    def _search_pubmed_ids(
        self,
        config: PubMedSearchConfig,
    ) -> tuple[int, list[str]]:
        if config.candidate_count <= 0:
            return 0, []
        params: dict[str, Any] = {
            "db": "pubmed",
            "term": _build_pubmed_query(config),
            "retmode": "json",
            "retmax": config.candidate_count,
            "sort": config.sort,
            **self._identity_params(),
        }
        response = self.session.get(
            PUBMED_ESEARCH_URL,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        result = response.json().get("esearchresult", {})
        return int(result.get("count", 0)), list(result.get("idlist", []))

    def _fetch_abstracts(self, ids: list[str]) -> list[PubMedPaperSummary]:
        if not ids:
            return []
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
            **self._identity_params(),
        }
        response = self.session.get(
            PUBMED_EFETCH_URL,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return parse_pubmed_xml(response.content, ids)


def parse_pubmed_xml(
    xml_content: bytes | str,
    requested_ids: list[str] | None = None,
) -> list[PubMedPaperSummary]:
    """Parse PubMed XML while preserving the requested PMID order."""
    root = ET.fromstring(xml_content)
    papers_by_id: dict[str, PubMedPaperSummary] = {}
    for article_record in root.findall(".//PubmedArticle"):
        citation = article_record.find("MedlineCitation")
        article = citation.find("Article") if citation is not None else None
        pmid = _element_text(citation.find("PMID") if citation is not None else None)
        if not pmid or article is None:
            continue

        abstract_parts: list[str] = []
        for abstract_node in article.findall("./Abstract/AbstractText"):
            text = _element_text(abstract_node)
            if not text:
                continue
            label = abstract_node.attrib.get("Label")
            abstract_parts.append(f"{label}: {text}" if label else text)

        journal = article.find("Journal")
        pub_date = journal.find("./JournalIssue/PubDate") if journal is not None else None
        date_parts = []
        if pub_date is not None:
            for field in ("Year", "MedlineDate", "Month", "Day"):
                value = _element_text(pub_date.find(field))
                if value:
                    date_parts.append(value)

        doi = None
        for article_id in article_record.findall("./PubmedData/ArticleIdList/ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = _element_text(article_id) or None
                break

        publication_types = tuple(
            text
            for text in (
                _element_text(node)
                for node in article.findall("./PublicationTypeList/PublicationType")
            )
            if text
        )
        papers_by_id[pmid] = PubMedPaperSummary(
            pmid=pmid,
            title=_element_text(article.find("ArticleTitle")),
            source=_element_text(journal.find("Title") if journal is not None else None),
            pub_date=" ".join(date_parts),
            abstract="\n".join(abstract_parts),
            doi=doi,
            publication_types=publication_types,
        )

    ordered_ids = requested_ids or list(papers_by_id)
    return [papers_by_id[pmid] for pmid in ordered_ids if pmid in papers_by_id]


def with_relevance_score(
    paper: PubMedPaperSummary,
    score: float,
) -> PubMedPaperSummary:
    """Return an immutable paper record annotated with a retrieval score."""
    return replace(paper, relevance_score=score)
