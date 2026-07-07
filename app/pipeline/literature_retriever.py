from dataclasses import dataclass
import math
import os
from typing import Any

from openai import OpenAI, OpenAIError

from app.clients.pubmed_client import (
    PubMedClient,
    PubMedPaperSummary,
    PubMedSearchConfig,
    with_relevance_score,
)


@dataclass(frozen=True)
class LiteratureRetrievalConfig:
    """Candidate and final retrieval bounds for one signal."""

    candidate_count: int = 25
    max_results: int = 5
    use_embeddings: bool = True


@dataclass(frozen=True)
class LiteratureRetrievalResult:
    """Total PubMed hits and the final grounded-context papers."""

    total_result_count: int
    papers: list[PubMedPaperSummary]
    ranking_method: str


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Embedding vectors must have equal non-zero length")
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _paper_text(paper: PubMedPaperSummary) -> str:
    return f"{paper.title}\n{paper.abstract}".strip()


def _semantic_rerank(
    drug_name: str,
    reaction: str,
    papers: list[PubMedPaperSummary],
    openai_client: Any,
) -> list[PubMedPaperSummary]:
    query = (
        f"Scientific evidence about {drug_name} and {reaction} "
        "as a reported adverse event"
    )
    inputs = [query, *[_paper_text(paper) for paper in papers]]
    response = openai_client.embeddings.create(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        input=inputs,
    )
    embeddings = [item.embedding for item in response.data]
    if len(embeddings) != len(inputs):
        raise ValueError("Embedding response did not match the requested inputs")
    query_embedding = embeddings[0]
    scored = [
        with_relevance_score(
            paper,
            cosine_similarity(query_embedding, paper_embedding),
        )
        for paper, paper_embedding in zip(papers, embeddings[1:])
    ]
    return sorted(
        scored,
        key=lambda paper: paper.relevance_score or 0.0,
        reverse=True,
    )


def retrieve_relevant_literature(
    drug_name: str,
    reaction: str,
    config: LiteratureRetrievalConfig,
    drug_aliases: list[str] | None = None,
    pubmed_client: PubMedClient | None = None,
    openai_client: Any | None = None,
) -> LiteratureRetrievalResult:
    """Retrieve PubMed candidates and optionally rerank them semantically."""
    if config.max_results <= 0:
        return LiteratureRetrievalResult(0, [], "disabled")

    pubmed_client = pubmed_client or PubMedClient()
    search_result = pubmed_client.search_papers(
        PubMedSearchConfig(
            drug_name=drug_name,
            reaction=reaction,
            drug_aliases=tuple(drug_aliases or ()),
            candidate_count=max(config.candidate_count, config.max_results),
            sort="relevance",
        )
    )
    papers = search_result.papers
    ranking_method = "pubmed_relevance"

    if config.use_embeddings and papers and (openai_client or os.getenv("OPENAI_API_KEY")):
        client = openai_client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        try:
            papers = _semantic_rerank(drug_name, reaction, papers, client)
            ranking_method = "semantic_embedding"
        except (OpenAIError, ValueError):
            # PubMed relevance is deterministic and remains a safe fallback.
            ranking_method = "pubmed_relevance_fallback"

    return LiteratureRetrievalResult(
        total_result_count=search_result.total_result_count,
        papers=papers[: config.max_results],
        ranking_method=ranking_method,
    )
