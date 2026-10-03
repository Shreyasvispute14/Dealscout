from collections import Counter

from fastapi import APIRouter, Cookie, HTTPException

from lib.db import db
from models.analytics import AnalyticsSummary, SourceCount
from models.auth import User
from models.products import SearchLog
from routers.auth import sessions

router = APIRouter()


def _require_user(token: str | None) -> User:
    user = sessions.get(token or "")
    if user is None:
        raise HTTPException(status_code=401, detail="Login required to view collected data")
    return user


@router.get("/analytics", response_model=AnalyticsSummary)
async def analytics(sppudeal_session: str | None = Cookie(default=None)):
    _require_user(sppudeal_session)
    documents = await db.search_logs.find().sort("searched_at", -1).to_list(100)
    logs = [SearchLog(**document) for document in documents]
    query_counts = Counter(log.query.lower() for log in logs)
    source_counts = Counter(source for document in documents for source in document.get("sources", []))
    average = round(sum(log.result_count for log in logs) / len(logs), 1) if logs else 0
    return AnalyticsSummary(
        total_searches=len(logs), unique_queries=len(query_counts), average_results=average,
        top_query=query_counts.most_common(1)[0][0] if query_counts else None,
        source_counts=[SourceCount(source=source, count=count) for source, count in source_counts.most_common()],
        recent_searches=logs[:8],
    )