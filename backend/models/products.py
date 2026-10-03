from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ProductOffer(BaseModel):
    id: str
    product_name: str
    category: str
    source: str
    seller: str
    price: float
    original_price: float | None = None
    currency: str = "INR"
    rating: float | None = None
    delivery: str | None = None
    discount: int | None = None
    product_url: str | None = None
    mode: Literal["demo", "live"]
    is_live: bool = False
    is_mocked: bool = False
    retrieved_at: datetime


class SearchResponse(BaseModel):
    query: str
    category: str
    mode: Literal["demo", "live"]
    results: list[ProductOffer]
    best_deal_id: str | None = None
    live_provider_available: bool = False
    notice: str


class SearchLog(BaseModel):
    id: str
    query: str
    category: str
    mode: Literal["demo", "live"]
    result_count: int
    best_price: float | None = None
    searched_at: datetime