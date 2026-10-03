import os
import uuid
from datetime import datetime, timezone
from typing import Literal

import httpx
from fastapi import APIRouter, Query

from lib.db import db
from models.products import ProductOffer, SearchResponse

router = APIRouter()


def _offer(name: str, category: str, source: str, seller: str, price: float, original: float | None,
           rating: float | None, delivery: str, mode: Literal["demo", "live"], is_live: bool = False,
           is_mocked: bool = False) -> ProductOffer:
    discount = round((1 - price / original) * 100) if original and original > price else None
    return ProductOffer(
        id=str(uuid.uuid4()), product_name=name, category=category, source=source, seller=seller,
        price=price, original_price=original, rating=rating, delivery=delivery, discount=discount,
        product_url=None, mode=mode, is_live=is_live, is_mocked=is_mocked, retrieved_at=datetime.now(timezone.utc),
    )


CATALOG = [
    _offer("Apple iPhone 15 128GB", "Mobiles", "Amazon", "Amazon Retail", 69999, 79900, 4.6, "Tomorrow", "demo"),
    _offer("Apple iPhone 15 128GB", "Mobiles", "Flipkart", "Flipkart Seller", 68499, 79900, 4.5, "2 days", "demo"),
    _offer("Apple iPhone 15 128GB", "Mobiles", "Croma", "Croma Retail", 70990, 79900, 4.4, "3 days", "demo"),
    _offer("Samsung Galaxy S24 256GB", "Mobiles", "Amazon", "Amazon Retail", 74999, 79999, 4.5, "Tomorrow", "demo"),
    _offer("Samsung Galaxy S24 256GB", "Mobiles", "Flipkart", "Flipkart Seller", 72999, 79999, 4.4, "2 days", "demo"),
    _offer("MacBook Air M2 13-inch", "Laptops", "Amazon", "Amazon Retail", 92990, 99900, 4.8, "Tomorrow", "demo"),
    _offer("MacBook Air M2 13-inch", "Laptops", "Croma", "Croma Retail", 94990, 99900, 4.7, "3 days", "demo"),
    _offer("MacBook Air M2 13-inch", "Laptops", "Reliance Digital", "Reliance Retail", 93990, 99900, 4.6, "4 days", "demo"),
    _offer("Dell Inspiron 15 Laptop", "Laptops", "Amazon", "Amazon Retail", 54990, 62990, 4.3, "2 days", "demo"),
    _offer("Dell Inspiron 15 Laptop", "Laptops", "Flipkart", "Flipkart Seller", 52990, 62990, 4.2, "3 days", "demo"),
    _offer("Noise Wireless Earbuds", "General", "Amazon", "Amazon Retail", 1499, 2499, 4.1, "Tomorrow", "demo"),
    _offer("Noise Wireless Earbuds", "General", "Flipkart", "Flipkart Seller", 1299, 2499, 4.0, "2 days", "demo"),
    _offer("College Laptop Backpack", "General", "Amazon", "Amazon Retail", 1199, 1899, 4.2, "Tomorrow", "demo"),
    _offer("College Laptop Backpack", "General", "Local Store", "Campus Store", 999, 1499, 4.0, "Pickup today", "demo"),
]


def _matches(offer: ProductOffer, query: str, category: str) -> bool:
    haystack = f"{offer.product_name} {offer.category}".lower()
    return all(token in haystack for token in query.lower().split()) and (category == "All" or offer.category == category)


def _live_preview(query: str, category: str) -> list[ProductOffer]:
    results: list[ProductOffer] = []
    for index, item in enumerate(CATALOG):
        if _matches(item, query, category) and index % 3 != 0:
            results.append(item.model_copy(update={
                "id": str(uuid.uuid4()), "source": f"Live Preview · {item.source}",
                "seller": f"{item.seller} (preview)", "price": round(item.price * (0.98 + (index % 4) * 0.01), 2),
                "mode": "live", "is_live": False, "is_mocked": True, "retrieved_at": datetime.now(timezone.utc),
            }))
    return results


async def _serpapi_search(query: str, category: str) -> list[ProductOffer]:
    key = os.environ.get("SERPAPI_KEY")
    if not key:
        return []
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://serpapi.com/search", params={
            "engine": "google_shopping", "q": query, "api_key": key, "num": 10, "hl": "en", "gl": "in",
        })
        response.raise_for_status()
        data = response.json()
    results: list[ProductOffer] = []
    for index, item in enumerate(data.get("shopping_results", [])):
        raw_price = item.get("price", "")
        digits = "".join(character for character in str(raw_price) if character.isdigit() or character == ".")
        if not digits:
            continue
        results.append(ProductOffer(
            id=f"live-{index}-{uuid.uuid4()}", product_name=item.get("title", query),
            category=category if category != "All" else "General", source=item.get("source", "Live provider"),
            seller=item.get("source", "Online seller"), price=float(digits), rating=item.get("rating"),
            delivery=item.get("delivery", "Check seller"), product_url=item.get("link"), mode="live",
            is_live=True, is_mocked=False, retrieved_at=datetime.now(timezone.utc),
        ))
    return results


@router.get("/products/search", response_model=SearchResponse)
async def search_products(q: str = Query(min_length=2, max_length=80), category: str = Query(default="All"),
                         mode: Literal["demo", "live"] = Query(default="demo")):
    query = q.strip()
    results = [item.model_copy(deep=True) for item in CATALOG if _matches(item, query, category)]
    notice = "Demo catalog results collected from the local project dataset."
    provider_available = bool(os.environ.get("SERPAPI_KEY"))
    if mode == "live":
        try:
            live_results = await _serpapi_search(query, category)
        except (httpx.HTTPError, ValueError):
            live_results = []
        if live_results:
            results, notice = live_results, "Live results returned by the configured shopping provider."
        else:
            results, notice = _live_preview(query, category), "LIVE PREVIEW is MOCKED because no shopping provider key is configured."
    best = min(results, key=lambda item: item.price, default=None)
    await db.search_logs.insert_one({
        "id": str(uuid.uuid4()), "query": query, "category": category, "mode": mode,
        "result_count": len(results), "best_price": best.price if best else None,
        "searched_at": datetime.now(timezone.utc), "sources": [item.source for item in results],
    })
    return SearchResponse(query=query, category=category, mode=mode, results=results,
                          best_deal_id=best.id if best else None, live_provider_available=provider_available, notice=notice)