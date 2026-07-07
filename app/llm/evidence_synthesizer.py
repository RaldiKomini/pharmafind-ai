import json
import os
from typing import Any, Literal

from openai import OpenAI
from pydantic import BaseModel, Field

from app.clients.pubmed_client import PubMedPaperSummary
from app.llm.prompts import EVIDENCE_SYNTHESIS_INSTRUCTIONS
from app.pipeline.evidence_grader import (
    EvidenceClaim,
    EvidenceSynthesis,
    validate_evidence_synthesis,
)


EvidenceStance = Literal["supports", "refutes", "mixed", "unclear"]


class GroundedClaimOutput(BaseModel):
    text: str = Field(min_length=1)
    stance: EvidenceStance
    pmids: list[str] = Field(min_length=1)


class GroundedEvidenceOutput(BaseModel):
    summary: str = Field(min_length=1)
    overall_stance: EvidenceStance
    claims: list[GroundedClaimOutput] = Field(min_length=1)
    limitations: list[str]


def _paper_payload(paper: PubMedPaperSummary) -> dict[str, Any]:
    return {
        "pmid": paper.pmid,
        "title": paper.title,
        "abstract": paper.abstract,
        "journal": paper.source,
        "publication_date": paper.pub_date,
        "publication_types": list(paper.publication_types),
    }


def generate_grounded_evidence_synthesis(
    drug_name: str,
    reaction: str,
    papers: list[PubMedPaperSummary],
    client: Any | None = None,
) -> EvidenceSynthesis | None:
    """Summarize only retrieved abstracts and validate every PMID citation."""
    papers_with_abstracts = [paper for paper in papers if paper.abstract.strip()]
    if not papers_with_abstracts:
        return None

    client = client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    input_payload = {
        "drug": drug_name,
        "adverse_event": reaction,
        "retrieved_pubmed_records": [
            _paper_payload(paper) for paper in papers_with_abstracts
        ],
    }
    response = client.responses.parse(
        model=os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4.1-mini"),
        instructions=EVIDENCE_SYNTHESIS_INSTRUCTIONS,
        input=json.dumps(input_payload, ensure_ascii=False),
        text_format=GroundedEvidenceOutput,
        store=False,
    )
    parsed = response.output_parsed
    if parsed is None:
        raise ValueError("The model did not return a structured evidence synthesis")

    synthesis = EvidenceSynthesis(
        summary=parsed.summary,
        overall_stance=parsed.overall_stance,
        claims=[
            EvidenceClaim(
                text=claim.text,
                stance=claim.stance,
                pmids=claim.pmids,
            )
            for claim in parsed.claims
        ],
        limitations=parsed.limitations,
    )
    return validate_evidence_synthesis(synthesis, papers_with_abstracts)
