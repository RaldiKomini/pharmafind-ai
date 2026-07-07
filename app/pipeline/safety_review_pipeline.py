from dataclasses import dataclass
from typing import Any

from openai import OpenAIError

from app.clients.faers_client import FaersClient
from app.clients.pubmed_client import PubMedClient
from app.llm.evidence_synthesizer import generate_grounded_evidence_synthesis
from app.pipeline.evidence_grader import build_evidence_summary
from app.pipeline.faers_signal_pipeline import (
    FaersSignalReviewConfig,
    run_faers_signal_review,
)
from app.pipeline.literature_retriever import (
    LiteratureRetrievalConfig,
    retrieve_relevant_literature,
)
from app.pipeline.review_summary import ReviewSummary, build_review_summary
from app.pipeline.safety_signal import build_safety_signal


@dataclass(frozen=True)
class SafetyReviewConfig:
    """Top-level configuration for a PRR/ROR plus PubMed review."""

    drug_name: str
    analysis_days: int = 365
    min_case_count: int = 5
    min_prr: float = 2.0
    min_ror_ci_lower: float = 1.0
    max_signals: int = 10
    pubmed_candidate_count: int = 25
    max_pubmed_papers_per_signal: int = 5
    use_embeddings: bool = True
    use_llm: bool = False


def run_safety_review(
    config: SafetyReviewConfig,
    faers_client: FaersClient | None = None,
    pubmed_client: PubMedClient | None = None,
    openai_client: Any | None = None,
) -> ReviewSummary:
    """Run deterministic disproportionality first, then bounded literature RAG."""
    pubmed_client = pubmed_client or PubMedClient()
    faers_client = faers_client or FaersClient()
    faers_result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name=config.drug_name,
            analysis_days=config.analysis_days,
            min_case_count=config.min_case_count,
            min_prr=config.min_prr,
            min_ror_ci_lower=config.min_ror_ci_lower,
            max_signals=config.max_signals,
        ),
        client=faers_client,
    )

    pubmed_drug_terms = [config.drug_name]
    if faers_result.signals and config.max_pubmed_papers_per_signal > 0:
        pubmed_drug_terms = faers_client.resolve_drug_aliases(config.drug_name)

    safety_signals = []
    for signal in faers_result.signals:
        retrieval = retrieve_relevant_literature(
            drug_name=config.drug_name,
            reaction=signal.reaction,
            drug_aliases=pubmed_drug_terms[1:],
            config=LiteratureRetrievalConfig(
                candidate_count=config.pubmed_candidate_count,
                max_results=config.max_pubmed_papers_per_signal,
                use_embeddings=config.use_embeddings,
            ),
            pubmed_client=pubmed_client,
            openai_client=openai_client,
        )

        synthesis = None
        synthesis_status = "not_requested"
        if config.use_llm:
            synthesis_status = "no_abstracts"
            if any(paper.abstract.strip() for paper in retrieval.papers):
                try:
                    synthesis = generate_grounded_evidence_synthesis(
                        drug_name=config.drug_name,
                        reaction=signal.reaction,
                        papers=retrieval.papers,
                        client=openai_client,
                    )
                    synthesis_status = "completed" if synthesis else "no_abstracts"
                except (OpenAIError, ValueError, KeyError):
                    # Retrieved papers remain available even when synthesis fails
                    # or the model returns an invalid/out-of-set PMID.
                    synthesis_status = "unavailable"

        evidence = build_evidence_summary(
            total_result_count=retrieval.total_result_count,
            papers=retrieval.papers,
            ranking_method=retrieval.ranking_method,
            synthesis=synthesis,
            synthesis_status=synthesis_status,
        )
        safety_signals.append(build_safety_signal(signal, evidence))

    return build_review_summary(
        drug_name=faers_result.drug_name,
        analysis_start=faers_result.analysis_start,
        analysis_end=faers_result.analysis_end,
        total_report_count=faers_result.total_report_count,
        drug_report_count=faers_result.drug_report_count,
        pubmed_search_terms=pubmed_drug_terms,
        signals=safety_signals,
    )
