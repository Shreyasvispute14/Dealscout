from pydantic import BaseModel

from models.products import SearchLog


class SourceCount(BaseModel):
    source: str
    count: int


class AnalyticsSummary(BaseModel):
    total_searches: int
    unique_queries: int
    average_results: float
    top_query: str | None = None
    source_counts: list[SourceCount]
    recent_searches: list[SearchLog]