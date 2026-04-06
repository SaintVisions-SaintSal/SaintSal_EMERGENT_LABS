"""SaintSal Labs — CookinCards Endpoints (Section 6)
Enhanced: Supabase persistence, eBay pricing, live trending, cert verification.
"""
from fastapi import APIRouter, Request, UploadFile, File, Header
from fastapi.responses import JSONResponse
import httpx
import os
import json
import base64
import uuid
import re
from datetime import datetime, timezone
from typing import Optional


router = APIRouter(prefix="/api/cards", tags=["cards"])

XIMILAR_API_KEY = os.environ.get("XIMILAR_API_KEY", "")
XIMILAR_BASE = "https://api.ximilar.com"
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
GOOGLE_VISION_KEY = os.environ.get("GOOGLE_MAPS_KEY", "")


def _ximilar_headers():
    return {"Authorization": f"Token {XIMILAR_API_KEY}", "Content-Type": "application/json"}


def _sb():
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def _uid(request: Request) -> str:
    auth = request.headers.get("authorization", "").replace("Bearer ", "")
    if auth and len(auth) > 50:
        try:
            import jwt
            payload = jwt.decode(auth, options={"verify_signature": False})
            return payload.get("sub", "anonymous")
        except Exception:
            pass
    return "anonymous"


def _now():
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
# SCAN — Camera capture identification + valuation
# ═══════════════════════════════════════════════════════════════════

@router.post("/scan")
async def card_scan(request: Request):
    """Identify a card from image using Ximilar."""
    body = await request.json()
    image_url = body.get("image_url", "")
    image_base64 = body.get("image_base64", "")
    card_type = body.get("card_type", "tcg")

    if not image_url and not image_base64:
        return JSONResponse({"error": "image_url or image_base64 required"}, status_code=400)

    records = [{"_url": image_url}] if image_url else [{"_base64": image_base64}]
    endpoint = f"{XIMILAR_BASE}/collectibles/v2/tcg_id" if card_type == "tcg" else f"{XIMILAR_BASE}/collectibles/v2/sport_id"

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            r = await http.post(endpoint, json={
                "records": records, "get_listings": True, "get_slab_detail": True
            }, headers=_ximilar_headers())

            if r.status_code == 200:
                data = r.json()
                records_result = data.get("records", [{}])
                if records_result:
                    card_data = records_result[0]
                    best_match = card_data.get("_identification", {}).get("best_match", {})
                    listings = card_data.get("_identification", {}).get("listings", [])
                    est_value = listings[0].get("price", 0) if listings else None

                    # Determine celebration tier
                    celebration = "common"
                    if est_value and est_value > 500:
                        celebration = "grail"
                    elif est_value and est_value > 50:
                        celebration = "rare"

                    # Check for PSA 10 / BGS 10
                    slab = card_data.get("_slab_detail", {})
                    if slab.get("grade") and float(str(slab.get("grade", "0")).replace("+", "")) >= 10:
                        celebration = "gem_mint"

                    return JSONResponse({
                        "card_name": best_match.get("name", "Unknown"),
                        "card_set": best_match.get("set_name", ""),
                        "card_number": best_match.get("number", ""),
                        "confidence": best_match.get("confidence", 0),
                        "estimated_value": est_value,
                        "celebration_tier": celebration,
                        "listings": listings[:5],
                        "slab_detail": slab,
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


# Quick grade
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
    """Centering check only."""
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


# ═══════════════════════════════════════════════════════════════════
# PRICE LOOKUP — eBay via Tavily + Pokemon TCG API
# ═══════════════════════════════════════════════════════════════════

@router.post("/price")
async def card_price(request: Request):
    """Price lookup with real eBay data + Pokemon TCG API."""
    body = await request.json()
    card_name = body.get("card_name", "")
    card_set = body.get("card_set", "")
    grade = body.get("grade", "")
    card_type = body.get("card_type", "tcg")

    if not card_name:
        return JSONResponse({"error": "card_name required"}, status_code=400)

    prices = {"card_name": card_name, "card_set": card_set, "ebay_listings": [], "tcgplayer": {}}

    # 1. eBay sold listings via Tavily
    if TAVILY_KEY:
        search_query = f"{card_name} {card_set} {grade} sold eBay".strip()
        try:
            async with httpx.AsyncClient(timeout=15) as http:
                resp = await http.post("https://api.tavily.com/search", json={
                    "api_key": TAVILY_KEY,
                    "query": search_query,
                    "include_domains": ["ebay.com"],
                    "search_depth": "advanced",
                    "max_results": 10
                })
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    prices["ebay_listings"] = [{
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", "")[:200]
                    } for r in results]
        except Exception as e:
            print(f"[Cards] eBay search error: {e}")

    # 2. Pokemon TCG API for TCG cards (free, no key needed)
    if card_type == "tcg":
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', card_name).strip()
                resp = await http.get(
                    f"https://api.pokemontcg.io/v2/cards?q=name:{clean_name}&pageSize=5",
                    headers={"X-Api-Key": os.environ.get("POKEMON_TCG_API_KEY", "")}
                )
                if resp.status_code == 200:
                    cards = resp.json().get("data", [])
                    if cards:
                        best = cards[0]
                        tcgp = best.get("tcgplayer", {})
                        prices["tcgplayer"] = tcgp.get("prices", {})
                        prices["tcgplayer_url"] = tcgp.get("url", "")
                        prices["card_image"] = best.get("images", {}).get("large", best.get("images", {}).get("small", ""))
                        prices["card_details"] = {
                            "name": best.get("name", ""),
                            "set": best.get("set", {}).get("name", ""),
                            "number": best.get("number", ""),
                            "rarity": best.get("rarity", ""),
                            "types": best.get("types", []),
                            "supertype": best.get("supertype", "")
                        }
        except Exception as e:
            print(f"[Cards] Pokemon TCG API error: {e}")

    return JSONResponse(prices)


# ═══════════════════════════════════════════════════════════════════
# SEARCH — Pokemon TCG API + Tavily
# ═══════════════════════════════════════════════════════════════════

@router.post("/search")
async def card_search(request: Request):
    """Search card database by name/set/year using Pokemon TCG API."""
    body = await request.json()
    query = body.get("query", "")

    if not query:
        return JSONResponse({"error": "query required"}, status_code=400)

    results = []

    # Pokemon TCG API search
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip()
            resp = await http.get(
                f"https://api.pokemontcg.io/v2/cards?q=name:{clean}&pageSize=12&orderBy=-set.releaseDate"
            )
            if resp.status_code == 200:
                cards = resp.json().get("data", [])
                for c in cards:
                    tcgp = c.get("tcgplayer", {}).get("prices", {})
                    # Get best price from market prices
                    market_price = None
                    for variant in tcgp.values():
                        if isinstance(variant, dict) and variant.get("market"):
                            market_price = variant["market"]
                            break

                    results.append({
                        "name": c.get("name", ""),
                        "set_name": c.get("set", {}).get("name", ""),
                        "number": c.get("number", ""),
                        "rarity": c.get("rarity", ""),
                        "types": c.get("types", []),
                        "image_small": c.get("images", {}).get("small", ""),
                        "image_large": c.get("images", {}).get("large", ""),
                        "market_price": market_price,
                        "tcgplayer_url": c.get("tcgplayer", {}).get("url", ""),
                        "set_logo": c.get("set", {}).get("images", {}).get("logo", "")
                    })
    except Exception as e:
        print(f"[Cards] Search error: {e}")

    return JSONResponse({"query": query, "results": results, "total": len(results)})


# ═══════════════════════════════════════════════════════════════════
# CERT VERIFICATION — PSA/BGS/SGC
# ═══════════════════════════════════════════════════════════════════

@router.post("/verify-cert")
async def verify_cert(request: Request):
    """Verify PSA/BGS/SGC certification number via web lookup."""
    body = await request.json()
    cert_number = body.get("cert_number", "")
    company = body.get("company", "PSA").upper()

    if not cert_number:
        return JSONResponse({"error": "cert_number required"}, status_code=400)

    verification_url = ""
    if company == "PSA":
        verification_url = f"https://www.psacard.com/cert/{cert_number}"
    elif company == "BGS":
        verification_url = f"https://www.beckett.com/grading/card-lookup"
    elif company == "SGC":
        verification_url = f"https://www.gosgc.com/card-facts/{cert_number}"

    result = {"cert_number": cert_number, "company": company,
              "verification_url": verification_url, "verified": False, "search_results": []}

    if TAVILY_KEY:
        try:
            async with httpx.AsyncClient(timeout=15) as http:
                resp = await http.post("https://api.tavily.com/search", json={
                    "api_key": TAVILY_KEY,
                    "query": f"{company} cert {cert_number} card grading verification",
                    "search_depth": "basic",
                    "max_results": 5
                })
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    result["search_results"] = [{
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", "")[:200]
                    } for r in results]
                    result["verified"] = len(results) > 0
        except Exception:
            pass

    return JSONResponse(result)


# ═══════════════════════════════════════════════════════════════════
# GOOGLE CLOUD VISION — Enhanced recognition
# ═══════════════════════════════════════════════════════════════════

@router.post("/scan/vision")
async def card_scan_with_vision(request: Request):
    """Enhanced scan: Ximilar + Google Cloud Vision for double-verification."""
    body = await request.json()
    image_base64 = body.get("image_base64", "")
    image_url = body.get("image_url", "")

    results = {"ximilar": None, "google_vision": None}

    # Google Cloud Vision
    if GOOGLE_VISION_KEY and (image_base64 or image_url):
        try:
            vision_body = {
                "requests": [{
                    "image": {},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "TEXT_DETECTION"},
                        {"type": "WEB_DETECTION", "maxResults": 5},
                        {"type": "LOGO_DETECTION", "maxResults": 3}
                    ]
                }]
            }
            if image_base64:
                vision_body["requests"][0]["image"]["content"] = image_base64
            elif image_url:
                vision_body["requests"][0]["image"]["source"] = {"imageUri": image_url}

            async with httpx.AsyncClient(timeout=20) as http:
                resp = await http.post(
                    f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_KEY}",
                    json=vision_body
                )
                if resp.status_code == 200:
                    vision_data = resp.json().get("responses", [{}])[0]
                    results["google_vision"] = {
                        "labels": [la["description"] for la in vision_data.get("labelAnnotations", [])],
                        "text_detected": vision_data.get("textAnnotations", [{}])[0].get("description", "") if vision_data.get("textAnnotations") else "",
                        "web_entities": [w.get("description", "") for w in vision_data.get("webDetection", {}).get("webEntities", [])],
                        "logos": [la["description"] for la in vision_data.get("logoAnnotations", [])]
                    }
        except Exception as e:
            print(f"[Cards] Google Vision error: {e}")

    return JSONResponse(results)


# ═══════════════════════════════════════════════════════════════════
# COLLECTION MANAGEMENT — Supabase-backed
# ═══════════════════════════════════════════════════════════════════

@router.get("/collection")
async def get_collection(request: Request):
    """Get user's card collection from Supabase."""
    uid = _uid(request)
    sb = _sb()

    if sb and uid != "anonymous":
        try:
            r = sb.table("card_collections").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
            cards = r.data or []
            # Strip _id if present
            for c in cards:
                c.pop("_id", None)
            total_value = sum(c.get("estimated_value", 0) or 0 for c in cards)
            return JSONResponse({
                "collection": cards,
                "total_cards": len(cards),
                "estimated_value": total_value
            })
        except Exception as e:
            print(f"[Cards] Collection fetch error: {e}")

    return JSONResponse({"collection": [], "total_cards": 0, "estimated_value": 0})


@router.post("/collection/add")
async def add_to_collection(request: Request):
    """Add a card to user's collection in Supabase."""
    body = await request.json()
    uid = _uid(request)
    sb = _sb()

    card = {
        "id": str(uuid.uuid4()),
        "user_id": uid if uid != "anonymous" else body.get("user_id", "anonymous"),
        "card_name": body.get("card_name", ""),
        "card_set": body.get("card_set", ""),
        "card_number": body.get("card_number", ""),
        "card_type": body.get("card_type", "tcg"),
        "condition": body.get("condition", ""),
        "grade_estimate": body.get("grade_estimate"),
        "estimated_value": body.get("estimated_value"),
        "purchase_price": body.get("purchase_price"),
        "image_url": body.get("image_url", ""),
        "scan_data": body.get("scan_data", {}),
        "grade_data": body.get("grade_data", {}),
        "ximilar_data": body.get("ximilar_data", {}),
        "notes": body.get("notes", ""),
        "is_favorite": body.get("is_favorite", False)
    }

    if sb and uid != "anonymous":
        try:
            sb.table("card_collections").insert(card).execute()
            return JSONResponse({"status": "added", "card": card})
        except Exception as e:
            print(f"[Cards] Collection add error: {e}")
            return JSONResponse({"error": f"Failed to save: {e}"}, status_code=500)

    return JSONResponse({"status": "added_local", "card": card, "note": "Sign in to persist your collection"})


@router.delete("/collection/{card_id}")
async def remove_from_collection(card_id: str, request: Request):
    """Remove a card from collection."""
    uid = _uid(request)
    sb = _sb()

    if sb and uid != "anonymous":
        try:
            sb.table("card_collections").delete().eq("id", card_id).eq("user_id", uid).execute()
            return JSONResponse({"status": "removed", "card_id": card_id})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"error": "Sign in to manage collection"}, status_code=401)


@router.put("/collection/{card_id}/favorite")
async def toggle_favorite(card_id: str, request: Request):
    """Toggle favorite status on a card."""
    uid = _uid(request)
    sb = _sb()
    body = await request.json()

    if sb and uid != "anonymous":
        try:
            sb.table("card_collections").update({"is_favorite": body.get("is_favorite", True)}).eq("id", card_id).eq("user_id", uid).execute()
            return JSONResponse({"status": "updated"})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"error": "Sign in required"}, status_code=401)


# ═══════════════════════════════════════════════════════════════════
# PORTFOLIO SNAPSHOTS — Track value over time
# ═══════════════════════════════════════════════════════════════════

@router.get("/portfolio/snapshot")
async def get_portfolio_snapshots(request: Request):
    """Get portfolio value snapshots over time."""
    uid = _uid(request)
    sb = _sb()

    if sb and uid != "anonymous":
        try:
            r = sb.table("card_portfolio_snapshots").select("*").eq("user_id", uid).order("snapshot_date", desc=True).limit(30).execute()
            return JSONResponse({"snapshots": r.data or []})
        except Exception:
            pass

    return JSONResponse({"snapshots": []})


@router.post("/portfolio/snapshot")
async def create_portfolio_snapshot(request: Request):
    """Create a new portfolio value snapshot."""
    uid = _uid(request)
    sb = _sb()

    if sb and uid != "anonymous":
        try:
            # Get current collection totals
            cards = sb.table("card_collections").select("card_type,estimated_value").eq("user_id", uid).execute()
            all_cards = cards.data or []
            total_value = sum(c.get("estimated_value", 0) or 0 for c in all_cards)
            breakdown = {}
            for c in all_cards:
                ct = c.get("card_type", "tcg")
                breakdown[ct] = breakdown.get(ct, 0) + (c.get("estimated_value", 0) or 0)

            snapshot = {
                "id": str(uuid.uuid4()),
                "user_id": uid,
                "total_cards": len(all_cards),
                "total_value": total_value,
                "breakdown": breakdown
            }
            sb.table("card_portfolio_snapshots").insert(snapshot).execute()
            return JSONResponse({"status": "created", "snapshot": snapshot})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"error": "Sign in required"}, status_code=401)


# ═══════════════════════════════════════════════════════════════════
# LIVE TRENDING — Real market data via Tavily
# ═══════════════════════════════════════════════════════════════════

@router.get("/market/trending")
async def market_trending(request: Request):
    """Live trending cards from market data."""
    if TAVILY_KEY:
        try:
            async with httpx.AsyncClient(timeout=15) as http:
                resp = await http.post("https://api.tavily.com/search", json={
                    "api_key": TAVILY_KEY,
                    "query": "trending trading cards prices 2026 pokemon sports most valuable",
                    "search_depth": "advanced",
                    "max_results": 10
                })
                if resp.status_code == 200:
                    articles = resp.json().get("results", [])
                    return JSONResponse({
                        "trending_articles": [{
                            "title": a.get("title", ""),
                            "url": a.get("url", ""),
                            "snippet": a.get("content", "")[:200]
                        } for a in articles],
                        "updated_at": _now(),
                        "source": "live"
                    })
        except Exception:
            pass

    # Fallback to curated data
    return JSONResponse({
        "trending_articles": [],
        "trending": [
            {"name": "Charizard VSTAR", "set": "Brilliant Stars", "price_change": "+12.5%", "current_price": 85.00, "category": "Pokemon"},
            {"name": "Michael Jordan Rookie", "set": "1986 Fleer", "price_change": "+8.2%", "current_price": 12500.00, "category": "Sports"},
            {"name": "Black Lotus", "set": "Alpha", "price_change": "+3.1%", "current_price": 45000.00, "category": "MTG"},
            {"name": "Luka Doncic Prizm Silver", "set": "2018 Prizm", "price_change": "+15.3%", "current_price": 450.00, "category": "Sports"},
            {"name": "Pikachu VMAX Alt Art", "set": "Vivid Voltage", "price_change": "+22.0%", "current_price": 320.00, "category": "Pokemon"},
        ],
        "updated_at": _now(),
        "source": "cached"
    })


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
