from fastapi import APIRouter
from multimodal_moderation.analytics_store import STORE

router = APIRouter()

@router.get("/analytics/summary")
def analytics_summary():
    return STORE.summary()

@router.get("/analytics/recent")
def analytics_recent(limit: int = 50):
    return {"events": STORE.list_recent(limit=limit)}
