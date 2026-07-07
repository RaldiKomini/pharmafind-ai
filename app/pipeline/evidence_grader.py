from dataclasses import dataclass

from app.clients.pubmed_client import PubMedPaperSummary


VALID_EVIDENCE_STANCES = {"supports", "refutes", "mixed", "unclear"}


@dataclass(frozen=True)
class EvidenceClaim:
    """One literature claim tied only to retrieved PMIDs."""

    text: str
    stance: str
    pmids: list[str]


@dataclass(frozen=True)
class EvidenceSynthesis:
    """Grounded synthesis generated only from retrieved abstracts."""

    summary: str
    overall_stance: str
    claims: list[EvidenceClaim]
    limitations: list[str]


@dataclass(frozen=True)
class EvidenceSummary:
    """Transparent PubMed retrieval and optional grounded synthesis."""

    total_result_count: int
    retrieved_paper_count: int
    ranking_method: str
    papers: list[PubMedPaperSummary]
    synthesis: EvidenceSynthesis | None = None
    synthesis_status: str = "not_requested"


def validate_evidence_synthesis(
    synthesis: EvidenceSynthesis,
    papers: list[PubMedPaperSummary],
) -> EvidenceSynthesis:
    """Reject invented citations and malformed evidence stances."""
    allowed_pmids = {paper.pmid for paper in papers}
    if synthesis.overall_stance not in VALID_EVIDENCE_STANCES:
        raise ValueError(f"Invalid overall evidence stance: {synthesis.overall_stance}")
    if not synthesis.claims:
        raise ValueError("Evidence synthesis must contain at least one PMID-cited claim")
    for claim in synthesis.claims:
        if claim.stance not in VALID_EVIDENCE_STANCES:
            raise ValueError(f"Invalid evidence stance: {claim.stance}")
        if not claim.pmids:
            raise ValueError("Every literature claim must cite at least one PMID")
        unknown_pmids = set(claim.pmids) - allowed_pmids
        if unknown_pmids:
            raise ValueError(
                "Evidence synthesis cited PMIDs outside the retrieved set: "
                + ", ".join(sorted(unknown_pmids))
            )
    return synthesis


def build_evidence_summary(
    total_result_count: int,
    papers: list[PubMedPaperSummary],
    ranking_method: str,
    synthesis: EvidenceSynthesis | None = None,
    synthesis_status: str = "not_requested",
) -> EvidenceSummary:
    """Assemble literature evidence without inferring strength from paper count."""
    if synthesis is not None:
        validate_evidence_synthesis(synthesis, papers)
    return EvidenceSummary(
        total_result_count=total_result_count,
        retrieved_paper_count=len(papers),
        ranking_method=ranking_method,
        papers=papers,
        synthesis=synthesis,
        synthesis_status=synthesis_status,
    )
