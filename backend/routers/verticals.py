"""SaintSal Labs — Verticals Trending Endpoint (Section 1.4)"""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
import os

router = APIRouter(prefix="/api/verticals", tags=["verticals"])

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
ALPACA_API_KEY_ID = os.environ.get("ALPACA_API_KEY_ID", "")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
RENTCAST_API_KEY = os.environ.get("RENTCAST_API_KEY", "")


async def _tavily_search(query: str, max_results: int = 5):
    if not TAVILY_API_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as http:
        try:
            r = await http.post("https://api.tavily.com/search", json={
                "api_key": TAVILY_API_KEY, "query": query,
                "search_depth": "basic", "max_results": max_results,
                "include_images": True
            })
            data = r.json()
            return [{"title": x.get("title", ""), "source": x.get("url", "").split("/")[2] if "/" in x.get("url", "") else "",
                     "url": x.get("url", ""), "thumbnail": x.get("image", ""),
                     "published_at": x.get("published_date", "")} for x in data.get("results", [])]
        except Exception:
            return []


async def _exa_search(query: str, max_results: int = 5):
    if not EXA_API_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as http:
        try:
            r = await http.post("https://api.exa.ai/search", json={
                "query": query, "numResults": max_results, "useAutoprompt": True,
                "type": "neural"
            }, headers={"Authorization": f"Bearer {EXA_API_KEY}", "Content-Type": "application/json"})
            data = r.json()
            return [{"title": x.get("title", ""), "source": x.get("url", "").split("/")[2] if "/" in x.get("url", "") else "",
                     "url": x.get("url", ""), "thumbnail": "",
                     "published_at": x.get("publishedDate", "")} for x in data.get("results", [])]
        except Exception:
            return []


async def _alpaca_movers():
    if not ALPACA_API_KEY_ID:
        return []
    async with httpx.AsyncClient(timeout=10) as http:
        try:
            r = await http.get(f"{ALPACA_BASE_URL}/assets", params={"status": "active", "asset_class": "us_equity"},
                               headers={"APCA-API-KEY-ID": ALPACA_API_KEY_ID, "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY})
            return r.json()[:10] if r.status_code == 200 else []
        except Exception:
            return []


VERTICAL_QUERIES = {
    "sports": "live sports scores today NFL NBA MLB NHL",
    "news": "breaking news headlines today world politics tech",
    "search": "trending topics today technology AI business",
    "finance": "stock market movers today S&P 500 earnings",
    "realestate": "real estate market trends housing prices 2026",
    "medical": "healthcare news FDA approvals clinical trials",
    "tech": "technology news AI startups product launches",
}


@router.get("/trending")
async def get_trending(vertical: str = Query("search"), user_id: str = Query("")):
    """Get trending content for a specific vertical."""
    query = VERTICAL_QUERIES.get(vertical, VERTICAL_QUERIES["search"])

    articles = await _tavily_search(query, max_results=8)
    if not articles:
        articles = await _exa_search(query, max_results=8)

    result = {"articles": articles}

    if vertical == "sports":
        scores = await _tavily_search("live sports scores today", max_results=5)
        result["scores"] = scores
        result["alerts"] = []

    if vertical == "finance":
        movers = await _alpaca_movers()
        result["market_movers"] = movers

    return JSONResponse(result)
