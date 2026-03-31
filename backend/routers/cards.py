"""SaintSal Labs — CookinCards Endpoints (Section 6)"""
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
import httpx
import os
import json
import base64
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/cards", tags=["cards"])

XIMILAR_API_KEY = os.environ.get("XIMILAR_API_KEY", "d3af35129644fc16ae917103450991e0a3c89014")
XIMILAR_BASE = "https://api.ximilar.com"

# In-memory collections (production: use Supabase card_collections table)
card_collections = {}


def _ximilar_headers():
    return {"Authorization": f"Token {XIMILAR_API_KEY}", "Content-Type": "application/json"}


# Scan — Camera capture identification + valuation
@router.post("/scan")
async def card_scan(request: Request):
    """Identify a card from image using Ximilar."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")
    card_type = body.get("card_type", "tcg")  # tcg or sport

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = []
    if image_url:
        records = [{"_url": image_url}]
    elif image_base64:
        records = [{"_base64": image_base64}]

    endpoint = f"{XIMILAR_BASE}/collectibles/v2/tcg_id" if card_type == "tcg" else f"{XIMILAR_BASE}/collectibles/v2/sport_id"

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(endpoint, json={
                "records": records,
                "get_listings": True,
                "get_slab_detail": True
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                records_result = data.get("records", [{}])
                if records_result:
                    card_data = records_result[0]
                    best_match = card_data.get("_identification", {}).get("best_match", {})
                    listings = card_data.get("_identification", {}).get("listings", [])

                    return JSONResponse({
                        "card_name": best_match.get("name", "Unknown"),
                        "card_set": best_match.get("set_name", ""),
                        "card_number": best_match.get("number", ""),
                        "confidence": best_match.get("confidence", 0),
                        "estimated_value": listings[0].get("price", 0) if listings else None,
                        "listings": listings[:5],
                        "ximilar_data": card_data,
                        "image_url": image_url
                    })
            return JSONResponse({"error": f"Ximilar API error: {r.status_code}", "details": r.text}, status_code=502)
        except Exception as e:
            return JSONResponse({"error": f"Scan failed: {str(e)}"}, status_code=500)


# Full PSA-style grading
@router.post("/grade")
async def card_grade(request: Request):
    """Full PSA-style grading: centering, corners, edges, surface."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = [{"_url": image_url}] if image_url else [{"_base64": image_base64}]

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(f"{XIMILAR_BASE}/card-grader/v2/grade", json={
                "records": records
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                record = data.get("records", [{}])[0]
                grading = record.get("_grading", {})

                return JSONResponse({
                    "overall_grade": grading.get("grade", 0),
                    "centering": grading.get("centering", {}),
                    "corners": grading.get("corners", {}),
                    "edges": grading.get("edges", {}),
                    "surface": grading.get("surface", {}),
                    "grade_label": _grade_label(grading.get("grade", 0)),
                    "raw_data": grading
                })
            return JSONResponse({"error": f"Grading API error: {r.status_code}"}, status_code=502)
        except Exception as e:
            return JSONResponse({"error": f"Grade failed: {str(e)}"}, status_code=500)


# Quick grade (half credits)
@router.post("/quick-grade")
async def card_quick_grade(request: Request):
    """Quick condition check: NM/LP/MP/HP/D."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = [{"_url": image_url}] if image_url else [{"_base64": image_base64}]

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(f"{XIMILAR_BASE}/card-grader/v2/condition", json={
                "records": records
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                record = data.get("records", [{}])[0]
                condition = record.get("_condition", {})
                return JSONResponse({
                    "condition": condition.get("label", "Unknown"),
                    "condition_code": condition.get("code", ""),
                    "confidence": condition.get("confidence", 0),
                    "raw_data": condition
                })
            return JSONResponse({"error": f"Condition API error: {r.status_code}"}, status_code=502)
        except Exception as e:
            return JSONResponse({"error": f"Quick grade failed: {str(e)}"}, status_code=500)


# Centering only
@router.post("/centering")
async def card_centering(request: Request):
    """Centering check only — cheapest option."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = [{"_url": image_url}] if image_url else [{"_base64": image_base64}]

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(f"{XIMILAR_BASE}/card-grader/v2/centering", json={
                "records": records
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                record = data.get("records", [{}])[0]
                return JSONResponse({"centering": record.get("_centering", {}), "raw_data": record})
            return JSONResponse({"error": f"Centering API error: {r.status_code}"}, status_code=502)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)


# Slab read (OCR)
@router.post("/slab-read")
async def card_slab_read(request: Request):
    """OCR graded slab label: cert#, grade, company."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = [{"_url": image_url, "get_slab_detail": True}] if image_url else [{"_base64": image_base64, "get_slab_detail": True}]

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(f"{XIMILAR_BASE}/collectibles/v2/tcg_id", json={
                "records": records, "get_slab_detail": True
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                record = data.get("records", [{}])[0]
                slab = record.get("_slab_detail", {})
                return JSONResponse({
                    "cert_number": slab.get("cert_number", ""),
                    "grade": slab.get("grade", ""),
                    "grading_company": slab.get("company", ""),
                    "card_name": slab.get("card_name", ""),
                    "raw_data": slab
                })
            return JSONResponse({"error": f"Slab read API error: {r.status_code}"}, status_code=502)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)


# Price lookup
@router.post("/price")
async def card_price(request: Request):
    """Price lookup by card details."""
    body = await request.json()
    card_name = body.get("card_name", "")
    card_set = body.get("card_set", "")

    if not card_name:
        return JSONResponse({"error": "card_name required"}, status_code=400)

    # Use Ximilar listings or fallback search
    prices = {"card_name": card_name, "card_set": card_set, "prices": {"raw": None, "graded_psa_10": None, "graded_psa_9": None}}

    # Could integrate eBay/TCGPlayer here
    return JSONResponse(prices)


# Search cards
@router.post("/search")
async def card_search(request: Request):
    """Search card database by name/set/year."""
    body = await request.json()
    query = body.get("query", "")

    if not query:
        return JSONResponse({"error": "query required"}, status_code=400)

    # Basic search — in production this would hit a card database
    return JSONResponse({"query": query, "results": [], "note": "Card database search — connect to TCGPlayer/Pokemon TCG API for results"})


# Collection management
@router.get("/collection")
async def get_collection(request: Request):
    """Get user's card collection."""
    user_id = request.query_params.get("user_id", "anonymous")
    collection = card_collections.get(user_id, [])
    return JSONResponse({"collection": collection, "total_cards": len(collection),
                         "estimated_value": sum(c.get("estimated_value", 0) for c in collection if c.get("estimated_value"))})


@router.post("/collection/add")
async def add_to_collection(request: Request):
    """Add a card to user's collection."""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    card = {
        "id": str(uuid.uuid4()),
        "card_name": body.get("card_name", ""),
        "card_set": body.get("card_set", ""),
        "card_number": body.get("card_number", ""),
        "condition": body.get("condition", ""),
        "grade_estimate": body.get("grade_estimate"),
        "estimated_value": body.get("estimated_value"),
        "image_url": body.get("image_url", ""),
        "ximilar_data": body.get("ximilar_data", {}),
        "created_at": datetime.utcnow().isoformat()
    }

    if user_id not in card_collections:
        card_collections[user_id] = []
    card_collections[user_id].append(card)

    return JSONResponse({"status": "added", "card": card})


# Market trending
@router.get("/market/trending")
async def market_trending(request: Request):
    """Trending cards and price movers."""
    trending = [
        {"name": "Charizard VSTAR", "set": "Brilliant Stars", "price_change": "+12.5%", "current_price": 85.00, "category": "Pokemon"},
        {"name": "Michael Jordan Rookie", "set": "1986 Fleer", "price_change": "+8.2%", "current_price": 12500.00, "category": "Sports"},
        {"name": "Black Lotus", "set": "Alpha", "price_change": "+3.1%", "current_price": 45000.00, "category": "MTG"},
        {"name": "Luka Doncic Prizm Silver", "set": "2018 Prizm", "price_change": "+15.3%", "current_price": 450.00, "category": "Sports"},
        {"name": "Pikachu VMAX Alt Art", "set": "Vivid Voltage", "price_change": "+22.0%", "current_price": 320.00, "category": "Pokemon"},
    ]
    return JSONResponse({"trending": trending, "updated_at": datetime.utcnow().isoformat()})


def _grade_label(grade: float) -> str:
    if grade >= 9.5:
        return "GEM MINT (PSA 10)"
    elif grade >= 8.5:
        return "MINT (PSA 9)"
    elif grade >= 7.5:
        return "NM-MT (PSA 8)"
    elif grade >= 6.5:
        return "NM (PSA 7)"
    elif grade >= 5.5:
        return "EX-MT (PSA 6)"
    elif grade >= 4.5:
        return "EX (PSA 5)"
    elif grade >= 3.5:
        return "VG-EX (PSA 4)"
    elif grade >= 2.5:
        return "VG (PSA 3)"
    elif grade >= 1.5:
        return "GOOD (PSA 2)"
    else:
        return "POOR (PSA 1)"
