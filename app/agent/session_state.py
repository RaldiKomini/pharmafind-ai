from dataclasses import dataclass
from typing import Any

@dataclass 
class AgentSessionState:
    """
    In-memory cache for the current backend process.

    This lets follow-up agent actions explain or export the latest review
    without rerunning FAERS and PubMed every time.
    """

    last_drug_name: str| None = None
    last_review_summary: dict[str, Any] | None = None
    last_markdown_report: str | None = None
    last_pdf_path: str | None = None

SESSION_STATE = AgentSessionState()
