from fastapi import FastAPI

from app.api.routes_review import router as review_router
from app.api.routes_agent import router as agent_router

# The FastAPI app stays thin; review and agent behavior live in their routers.
app = FastAPI(
    title="PharmaFind AI",
    description="AI-assisted pharmacovigilance signal-review system.",
    version="0.1.0",
)

app.include_router(review_router)
app.include_router(agent_router)

@app.get("/health")
def health_check():
    """Small readiness endpoint used by the frontend status pill."""
    return {"status": "ok"}
