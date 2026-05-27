from fastapi import FastAPI

from app.api.routes_review import router as review_router
from app.api.routes_agent import router as agent_router

app = FastAPI(
    title="PharmaFind AI",
    description="AI-assisted pharmacovigilance signal-review system.",
    version="0.1.0",
)

app.include_router(review_router)
app.include_router(agent_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
