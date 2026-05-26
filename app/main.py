from fastapi import FastAPI

from app.api.routes_review import router as review_router

app = FastAPI(
    title="PharmaFind AI",
    description="AI-assisted pharmacovigilance signal-review system.",
    version="0.1.0",
)

app.include_router(review_router)
