from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.agent.agent_runner import run_agent
from app.api.schemas import AgentChatRequest, AgentChatResponse
from app.agent.session_state import SESSION_STATE

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agent(request: AgentChatRequest) -> AgentChatResponse:
    """Send a message to the tool-using agent and return cached state metadata."""
    answer = run_agent(request.message)

    return AgentChatResponse(
        answer=answer,
        last_drug_name=SESSION_STATE.last_drug_name,
        last_pdf_path=SESSION_STATE.last_pdf_path,
    )


@router.get("/pdf")
def download_agent_pdf() -> FileResponse:
    """Download the latest PDF produced by the agent tool layer."""
    if SESSION_STATE.last_pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="No PDF has been generated yet.",
        )

    pdf_path = Path(SESSION_STATE.last_pdf_path)

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file no longer exists.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
