"""SaintSal Labs — Creative Studio v2
Website Intelligence Engine + Marketing Campaign Builder + Email Sequences + Ad Creatives
All endpoints backed by Supabase with MongoDB RAG fallback.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os, json, uuid, httpx, re
from datetime import datetime, timezone

router = APIRouter(prefix="/api/studio", tags=["studio-v2"])

# ── Singleton Supabase ──
_sb_client = None
def _sb():
    global _sb_client
    if _sb_client is None:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if url and key:
            _sb_client = create_client(url, key)
    return _sb_client

def _uid(request: Request):
    if hasattr(request.state, 'user_id') and request.state.user_id:
        return str(request.state.user_id)
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            import jwt as pyjwt
            payload = pyjwt.decode(auth.split(" ",1)[1], options={"verify_signature": False})
            return payload.get("sub", "anonymous")
        except Exception:
            pass
    return "anonymous"

def _now():
    return datetime.now(timezone.utc).isoformat()

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# ═══════════════════════════════════════════════════════════════════
# 1. WEBSITE INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════════════

@router.post("/website-intel")
async def crawl_website(request: Request):
    """Crawl a URL → extract brand, colors, SEO, content → save to Supabase."""
    body = await request.json()
    url = body.get("url", "").strip()
    if not url:
        return JSONResponse({"error": "URL is required"}, status_code=400)
    if not url.startswith("http"):
        url = "https://" + url

    uid = _uid(request)
    crawl_id = str(uuid.uuid4())

    # Phase 1: Crawl the page via Tavily
    page_content = ""
    page_title = ""
    try:
        async with httpx.AsyncClient(timeout=30) as hc:
            r = await hc.post("https://api.tavily.com/search", json={
                "api_key": TAVILY_KEY,
                "query": f"site:{url}",
                "search_depth": "advanced",
                "include_raw_content": True,
                "max_results": 3
            })
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                for res in results:
                    if res.get("raw_content"):
                        page_content += res["raw_content"][:8000] + "\n"
                    if res.get("title") and not page_title:
                        page_title = res["title"]
                    if res.get("content"):
                        page_content += res["content"] + "\n"
    except Exception as e:
        print(f"[WebIntel] Tavily crawl error: {e}")

    if not page_content:
        # Fallback: basic HTTP fetch
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as hc:
                r = await hc.get(url)
                page_content = r.text[:15000]
        except Exception as e:
            return JSONResponse({"error": f"Could not crawl {url}: {e}"}, status_code=400)

    # Phase 2: Extract brand intelligence via Claude
    brand_extraction = {}
    seo_audit = {}
    content_analysis = {}
    marketing_opportunities = []

    try:
        prompt = f"""Analyze this website content and extract comprehensive brand intelligence.

URL: {url}
Page Title: {page_title}

Content (first 10000 chars):
{page_content[:10000]}

Return a JSON object with exactly these keys:
{{
  "brand_extraction": {{
    "brand_name": "...",
    "tagline": "...",
    "value_proposition": "...",
    "colors": {{"primary": "#hex", "secondary": "#hex", "accent": "#hex"}},
    "voice_tone": "professional/casual/technical/friendly/etc",
    "industry": "...",
    "products_services": ["..."],
    "target_audience": "...",
    "cta_patterns": ["..."],
    "social_links": {{"linkedin": "", "twitter": "", "instagram": "", "facebook": "", "youtube": ""}}
  }},
  "seo_audit": {{
    "title_tag": "...",
    "meta_description": "...",
    "h1_tags": ["..."],
    "page_speed_estimate": "fast|medium|slow",
    "mobile_friendly": true,
    "missing_elements": ["..."],
    "keyword_density": {{}},
    "seo_score": 0-100,
    "recommendations": ["..."]
  }},
  "content_analysis": {{
    "pages_found": 0,
    "estimated_word_count": 0,
    "content_types": ["blog", "landing", "about", "product"],
    "content_gaps": ["..."],
    "strengths": ["..."]
  }},
  "marketing_opportunities": [
    "Specific actionable opportunity 1",
    "Specific actionable opportunity 2",
    "Specific actionable opportunity 3"
  ]
}}

Be specific with colors (extract real hex codes from the content if visible).
Be actionable with recommendations."""

        async with httpx.AsyncClient(timeout=60) as hc:
            r = await hc.post("https://api.anthropic.com/v1/messages", headers={
                "x-api-key": ANTHROPIC_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }, json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                # Extract JSON from response
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    brand_extraction = parsed.get("brand_extraction", {})
                    seo_audit = parsed.get("seo_audit", {})
                    content_analysis = parsed.get("content_analysis", {})
                    marketing_opportunities = parsed.get("marketing_opportunities", [])
    except Exception as e:
        print(f"[WebIntel] Claude analysis error: {e}")

    # Phase 3: Save to Supabase (only if user is authenticated with valid UUID)
    sb = _sb()
    saved = False
    if sb and uid != "anonymous":
        try:
            sb.table("website_crawls").insert({
                "id": crawl_id,
                "user_id": uid,
                "url": url,
                "brand_extraction": brand_extraction,
                "seo_audit": seo_audit,
                "content_analysis": content_analysis,
                "marketing_opportunities": marketing_opportunities,
                "crawl_status": "completed"
            }).execute()
            saved = True
        except Exception as e:
            print(f"[WebIntel] Supabase save error: {e}")

    # Phase 4: Auto-populate Business DNA from brand extraction
    dna_saved = False
    if sb and uid != "anonymous" and brand_extraction:
        try:
            brand = brand_extraction
            dna_profile = {
                "user_id": uid,
                "business_name": brand.get("brand_name", ""),
                "industry": brand.get("industry", ""),
                "tagline": brand.get("tagline", ""),
                "value_proposition": brand.get("value_proposition", ""),
                "target_audience": brand.get("target_audience", ""),
                "products_services": brand.get("products_services", []),
                "voice_tone": brand.get("voice_tone", ""),
                "brand_colors": brand.get("colors", {}),
                "social_links": brand.get("social_links", {}),
                "cta_patterns": brand.get("cta_patterns", []),
                "website_url": url,
                "seo_score": seo_audit.get("seo_score", 0),
                "content_strengths": content_analysis.get("strengths", []),
                "marketing_opportunities": marketing_opportunities,
                "source": "website_intel_crawl",
                "crawl_id": crawl_id,
                "updated_at": _now()
            }
            # Upsert into business_dna table
            existing = sb.table("business_dna").select("id").eq("user_id", uid).limit(1).execute()
            if existing.data:
                sb.table("business_dna").update(dna_profile).eq("user_id", uid).execute()
            else:
                dna_profile["id"] = str(uuid.uuid4())
                sb.table("business_dna").insert(dna_profile).execute()
            dna_saved = True
            print(f"[WebIntel] Business DNA auto-populated for {uid} from {url}")
        except Exception as e:
            print(f"[WebIntel] DNA auto-save error: {e}")
            # Fallback: save to in-memory cache
            try:
                import importlib
                server_mod = importlib.import_module("server")
                if hasattr(server_mod, '_business_dna_cache'):
                    server_mod._business_dna_cache[uid] = dna_profile
            except Exception:
                pass

    return {
        "crawl_id": crawl_id,
        "url": url,
        "saved_to_supabase": saved,
        "dna_auto_populated": dna_saved,
        "brand_extraction": brand_extraction,
        "seo_audit": seo_audit,
        "content_analysis": content_analysis,
        "marketing_opportunities": marketing_opportunities
    }


@router.get("/website-intel/{crawl_id}")
async def get_crawl(crawl_id: str, request: Request):
    """Retrieve a previous website crawl."""
    sb = _sb()
    if sb:
        try:
            r = sb.table("website_crawls").select("*").eq("id", crawl_id).limit(1).execute()
            if r.data:
                row = r.data[0]
                row.pop("raw_html", None)
                return row
        except Exception:
            pass
    return JSONResponse({"error": "Crawl not found"}, status_code=404)


@router.get("/website-intel")
async def list_crawls(request: Request):
    """List all crawls for this user."""
    uid = _uid(request)
    sb = _sb()
    if sb:
        try:
            r = sb.table("website_crawls").select("id,url,brand_extraction,seo_audit,crawl_status,created_at").eq("user_id", uid).order("created_at", desc=True).limit(20).execute()
            return {"crawls": r.data or []}
        except Exception:
            pass
    return {"crawls": []}


# ═══════════════════════════════════════════════════════════════════
# 2. MARKETING CAMPAIGN BUILDER
# ═══════════════════════════════════════════════════════════════════

@router.post("/campaigns/generate")
async def generate_campaign(request: Request):
    """Generate a full multi-platform marketing campaign."""
    body = await request.json()
    uid = _uid(request)

    campaign_type = body.get("campaign_type", "awareness")
    goal = body.get("goal", "")
    duration = body.get("duration_days", 14)
    platforms = body.get("platforms", ["instagram", "linkedin", "twitter", "email"])
    budget = body.get("budget", "$500")
    brand_context = body.get("brand_context", {})
    website_crawl_id = body.get("website_crawl_id")

    # Pull website crawl data if provided
    crawl_data = {}
    if website_crawl_id:
        sb = _sb()
        if sb:
            try:
                r = sb.table("website_crawls").select("brand_extraction,seo_audit,content_analysis,url").eq("id", website_crawl_id).limit(1).execute()
                if r.data:
                    crawl_data = r.data[0]
            except Exception:
                pass

    # Pull Business DNA
    dna_context = body.get("business_dna", {})

    prompt = f"""You are SaintSal, an elite marketing strategist who builds campaigns that rival $50K/month agencies.

Generate a complete {campaign_type} marketing campaign.

GOAL: {goal}
DURATION: {duration} days
PLATFORMS: {', '.join(platforms)}
BUDGET: {budget}

{'BRAND CONTEXT: ' + json.dumps(brand_context) if brand_context else ''}
{'BUSINESS DNA: ' + json.dumps(dna_context) if dna_context else ''}
{'WEBSITE DATA: ' + json.dumps({k:v for k,v in crawl_data.items() if k != 'raw_html'}) if crawl_data else ''}

Return a JSON object:
{{
  "campaign_name": "...",
  "strategy": "2-3 sentence strategy overview",
  "content_calendar": [
    {{
      "day": 1,
      "posts": [
        {{
          "platform": "instagram",
          "type": "carousel|reel|story|post",
          "caption": "Full caption with hashtags",
          "image_prompt": "DALL-E prompt for the visual",
          "optimal_time": "10:00 AM PST",
          "cta": "..."
        }}
      ]
    }}
  ],
  "email_sequence": [
    {{
      "day": 0,
      "subject": "...",
      "preview_text": "...",
      "body_html": "Complete email body",
      "cta": {{"text": "...", "url": "..."}}
    }}
  ],
  "ad_creatives": [
    {{
      "platform": "meta|google|linkedin",
      "headline": "...",
      "primary_text": "...",
      "cta": "...",
      "audience_targeting": "...",
      "budget_split": "$X"
    }}
  ],
  "kpis": {{
    "target_reach": 0,
    "target_engagement": "X%",
    "target_leads": 0,
    "target_conversions": 0
  }}
}}

Generate at least {min(duration, 7)} days of content calendar entries.
Generate at least 3 email sequence entries if email is in platforms.
Generate at least 2 ad creatives per ad platform."""

    campaign_data = {}
    try:
        async with httpx.AsyncClient(timeout=90) as hc:
            r = await hc.post("https://api.anthropic.com/v1/messages", headers={
                "x-api-key": ANTHROPIC_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }, json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            })
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    campaign_data = json.loads(match.group())
    except Exception as e:
        print(f"[Campaign] Generation error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

    # Save to Supabase (only if user is authenticated)
    campaign_id = str(uuid.uuid4())
    sb = _sb()
    saved = False
    if sb and uid != "anonymous":
        try:
            sb.table("marketing_campaigns").insert({
                "id": campaign_id,
                "user_id": uid,
                "campaign_name": campaign_data.get("campaign_name", goal[:50]),
                "campaign_type": campaign_type,
                "goal": goal,
                "duration_days": duration,
                "platforms": platforms,
                "budget": budget,
                "strategy": {"text": campaign_data.get("strategy", "")},
                "content_calendar": campaign_data.get("content_calendar", []),
                "email_sequence": campaign_data.get("email_sequence", []),
                "ad_creatives": campaign_data.get("ad_creatives", []),
                "kpis": campaign_data.get("kpis", {}),
                "status": "draft"
            }).execute()
            saved = True
        except Exception as e:
            print(f"[Campaign] Supabase save error: {e}")

    return {
        "campaign_id": campaign_id,
        "saved": saved,
        **campaign_data
    }


@router.get("/campaigns")
async def list_campaigns(request: Request):
    uid = _uid(request)
    sb = _sb()
    if sb:
        try:
            r = sb.table("marketing_campaigns").select("id,campaign_name,campaign_type,goal,status,platforms,created_at").eq("user_id", uid).order("created_at", desc=True).limit(20).execute()
            return {"campaigns": r.data or []}
        except Exception:
            pass
    return {"campaigns": []}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, request: Request):
    sb = _sb()
    if sb:
        try:
            r = sb.table("marketing_campaigns").select("*").eq("id", campaign_id).limit(1).execute()
            if r.data:
                return r.data[0]
        except Exception:
            pass
    return JSONResponse({"error": "Campaign not found"}, status_code=404)


# ═══════════════════════════════════════════════════════════════════
# 3. EMAIL SEQUENCE BUILDER
# ═══════════════════════════════════════════════════════════════════

@router.post("/email-sequence")
async def generate_email_sequence(request: Request):
    body = await request.json()
    uid = _uid(request)

    seq_type = body.get("sequence_type", "welcome")
    emails_count = body.get("emails_count", 5)
    goal = body.get("goal", "")
    audience = body.get("audience", "")
    brand_context = body.get("brand_context", {})

    prompt = f"""Generate a {emails_count}-email {seq_type} sequence.

GOAL: {goal}
AUDIENCE: {audience}
{'BRAND: ' + json.dumps(brand_context) if brand_context else ''}

Return JSON:
{{
  "sequence": [
    {{
      "day": 0,
      "subject": "...",
      "preview_text": "...",
      "body_html": "Full HTML email body with inline styles, dark theme compatible",
      "cta": {{"text": "...", "url": "https://..."}},
      "send_time": "10:00 AM"
    }}
  ],
  "estimated_performance": {{
    "open_rate": "35-45%",
    "click_rate": "8-12%",
    "conversion_rate": "3-5%"
  }}
}}"""

    result = {}
    try:
        async with httpx.AsyncClient(timeout=60) as hc:
            r = await hc.post("https://api.anthropic.com/v1/messages", headers={
                "x-api-key": ANTHROPIC_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }, json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 3000,
                "messages": [{"role": "user", "content": prompt}]
            })
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    result = json.loads(match.group())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # Save
    seq_id = str(uuid.uuid4())
    sb = _sb()
    if sb and uid != "anonymous":
        try:
            sb.table("email_sequences").insert({
                "id": seq_id, "user_id": uid, "sequence_type": seq_type,
                "sequence_name": f"{seq_type.replace('_',' ').title()} Sequence",
                "goal": goal, "emails": result.get("sequence", []), "status": "draft"
            }).execute()
        except Exception:
            pass

    return {"sequence_id": seq_id, **result}


# ═══════════════════════════════════════════════════════════════════
# 4. AD CREATIVE GENERATOR
# ═══════════════════════════════════════════════════════════════════

@router.post("/ads/generate")
async def generate_ads(request: Request):
    body = await request.json()
    uid = _uid(request)

    platform = body.get("platform", "meta")
    objective = body.get("campaign_objective", "conversions")
    product = body.get("product_description", "")
    audience = body.get("target_audience", "")
    variants = body.get("variants", 3)
    brand_context = body.get("brand_context", {})

    prompt = f"""Generate {variants} ad creative variants for {platform}.

OBJECTIVE: {objective}
PRODUCT: {product}
TARGET AUDIENCE: {audience}
{'BRAND: ' + json.dumps(brand_context) if brand_context else ''}

Return JSON:
{{
  "ad_creatives": [
    {{
      "variant": "A",
      "headline": "...",
      "primary_text": "...",
      "description": "...",
      "cta": "Sign Up|Learn More|Shop Now|Get Started",
      "image_prompt": "DALL-E prompt for the ad visual",
      "audience_targeting": {{"interests": [], "demographics": "..."}},
      "estimated_cpc": "$X.XX-$X.XX",
      "hook": "The emotional/logical hook this variant uses"
    }}
  ]
}}"""

    result = {}
    try:
        async with httpx.AsyncClient(timeout=45) as hc:
            r = await hc.post("https://api.anthropic.com/v1/messages", headers={
                "x-api-key": ANTHROPIC_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }, json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    result = json.loads(match.group())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"platform": platform, "objective": objective, **result}
