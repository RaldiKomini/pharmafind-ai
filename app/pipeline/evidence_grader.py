from dataclasses import dataclass

from app.clients.pubmed_client import PubMedPaperSummary

@dataclass(frozen=True)
class EvidenceSummary:
    paper_count: int
    evidence_grade: str
    papers: list[PubMedPaperSummary]


def grade_pubmed_evidence(papers):
    """
    Simple literature evidence grading.

    This does not prove causality.
    It only summarizes how much PubMed literature was found.
    """

    paper_count = len(papers)
    if paper_count == 0:
        grade = "none"
    elif paper_count <= 2:
        grade = "weak"
    elif paper_count <= 5:
        grade = "moderate"
    else:
        grade = "strong"

    return EvidenceSummary(
        paper_count=paper_count,
        evidence_grade=grade,
        papers=papers,
    )

