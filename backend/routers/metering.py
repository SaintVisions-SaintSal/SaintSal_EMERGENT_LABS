"""SaintSal Labs — Metering, Tier Gating & Compute Engine (v3 — Production Spec)
5 Tiers · 4 Compute Levels · 88+ API Connectors · Stripe Reference
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
from datetime import datetime, timezone

router = APIRouter(prefix="/api/metering", tags=["metering"])

# ═══════════════════════════════════════════════════════════════════════════════
# TIER CONFIGURATION — Exact production spec
# ═══════════════════════════════════════════════════════════════════════════════

TIERS = {
    "free": {
        "name": "Free", "price_monthly": 0, "price_annual": 0,
        "compute_minutes": 100, "cap_type": "hard",
        "overage_allowed": False, "color": "#6B7280",
        "models": ["mini"],
        "seats": 1,
        "features": [
            "search_basic", "news", "sports_1team", "tech",
            "finance_basic", "domain_search_5day"
        ],
        "rate_limit_per_hour": 30,
        "stripe": {
            "product_id": "prod_U3jCx2VJbNeXvU",
            "monthly_price_id": "price_1T5bkAL47U80vDLAslOm3HoX",
            "annual_price_id": "price_1T7p1tL47U80vDLAnxtkrGV4"
        },
        "description": "100 compute min/mo · SAL Mini models only · Basic search (10/day) · 1 team follow · 5 domain searches/day · 1 seat"
    },
    "starter": {
        "name": "Starter", "price_monthly": 27, "price_annual": 270,
        "compute_minutes": 500, "cap_type": "hard",
        "overage_allowed": False, "color": "#10B981",
        "models": ["mini", "pro"],
        "seats": 1,
        "features": [
            "search_basic", "search_exa", "news", "sports_3teams", "tech",
            "finance_basic", "finance_advanced",
            "career_overview", "career_jobs", "career_tracker", "career_resume",
            "career_coverletter", "career_linkedin",
            "realestate_search",
            "cookin_cards_price", "cookin_cards_deals",
            "business_overview", "business_domains", "business_resume", "business_signatures",
            "business_name_check",
            "builder_github", "job_tracker", "email_signatures",
            "daily_briefing", "domain_search"
        ],
        "rate_limit_per_hour": 100,
        "stripe": {
            "product_id": "prod_U3jCGSzn4WqzV3",
            "monthly_price_id": "price_1T5bkAL47U80vDLAaChP4Hqg",
            "annual_price_id": "price_1T6dHNL47U80vDLAPgfsUmtO",
            "alt_product_id": "prod_U613AWM3LH2xHS",
            "alt_monthly_price_id": "price_1T7p1sL47U80vDLAgU2shcQO",
            "alt_annual_price_id": "price_1T7p1sL47U80vDLAYEEv8Kmg"
        },
        "description": "500 compute min/mo · + SAL Pro models · + Exa search · + 3 teams · + GitHub Builder · + Job tracker · + Email signatures · + Name check · + Daily briefing · 1 seat"
    },
    "pro": {
        "name": "Pro", "price_monthly": 97, "price_annual": 970,
        "compute_minutes": 2000, "cap_type": "soft",
        "overage_allowed": True, "color": "#8B5CF6",
        "models": ["mini", "pro", "max"],
        "seats": 1,
        "features": [
            "search_basic", "search_exa", "search_deep", "news", "sports_unlimited", "tech",
            "finance_basic", "finance_advanced", "finance_dcf",
            "career_overview", "career_jobs", "career_tracker", "career_resume",
            "career_coverletter", "career_linkedin", "career_salary", "career_network",
            "career_coach", "career_interview",
            "realestate_search", "realestate_portfolio", "realestate_deal_analyzer", "realestate_ask_sal",
            "cookin_cards_price", "cookin_cards_deals", "cookin_cards_scan", "cookin_cards_grade", "cookin_cards_portfolio",
            "business_overview", "business_domains", "business_resume", "business_signatures",
            "business_meetings", "business_analytics", "business_bizplan", "business_patent",
            "business_formation", "business_domain_purchase", "business_entity_formation",
            "social_studio", "creative_studio", "voice_ai",
            "builder_full", "builder_deploy_vercel",
            "fantasy_intel", "betting_intel", "breaking_alerts",
            "ghl_subaccount",
            "daily_briefing", "domain_search", "domain_purchase"
        ],
        "rate_limit_per_hour": 300,
        "stripe": {
            "product_id": "prod_U3jC7k9rF5enMh",
            "monthly_price_id": "price_1T5bkBL47U80vDLALiVDkOgb",
            "annual_price_id": "price_1T6dHNL47U80vDLAHYxorUNk",
            "annual_v2_price_id": "price_1T84uZL47U80vDLARDZK46qE",
            "alt_product_id": "prod_U613QZiGZDVgGv"
        },
        "description": "2,000 compute min/mo · + SAL Max (Opus) · + Deep Research · + Unlimited teams · + Full Builder + Deploy (Vercel) · + Voice AI · + Creative Studio · + Career Suite · + Domain purchase · + Entity formation · + Fantasy/betting intel · + Breaking alerts · GHL sub-account included · 1 seat"
    },
    "teams": {
        "name": "Teams", "price_monthly": 297, "price_annual": 2970,
        "compute_minutes": 10000, "cap_type": "soft",
        "overage_allowed": True, "color": "#F59E0B",
        "models": ["mini", "pro", "max", "max_fast"],
        "seats": 5,
        "features": ["*"],
        "rate_limit_per_hour": 1000,
        "stripe": {
            "product_id": "prod_U3jCtHY6kyCJdC",
            "monthly_price_id": "price_1T5bkCL47U80vDLANsCa647K",
            "annual_price_id": "price_1T6dHNL47U80vDLAqTTV84lL",
            "alt_product_id": "prod_U613gLgk5ECC7U"
        },
        "description": "10,000 compute min/mo · + SAL Max Fast (parallel) · + Render/CF deploy · + Custom domains · + SAINT leads · + Ad creative · + GHL CRM full · + Compliance calendar · + Lead enrichment · + Patent FTO/valuation · 5 seats"
    },
    "enterprise": {
        "name": "Enterprise", "price_monthly": 497, "price_annual": 4970,
        "compute_minutes": -1, "cap_type": "none",
        "overage_allowed": True, "color": "#E5E5E5",
        "models": ["mini", "pro", "max", "max_fast"],
        "seats": -1,
        "features": ["*"],
        "rate_limit_per_hour": -1,
        "stripe": {
            "product_id": "prod_U3jCLNosf5FA6j",
            "monthly_price_id": "price_1T5bkDL47U80vDLANXWF33A7",
            "annual_price_id": "price_1T6dHOL47U80vDLARSODO7b1",
            "alt_product_id": "prod_U61367KBkTW1qB"
        },
        "description": "Unlimited compute · + API access · + White-label · + HACP license · + Enterprise SLA · + HIPAA BAA · + Licensing management · + Custom models · + Dedicated support · Custom seats"
    }
}

TIER_RANK = {"free": 0, "starter": 1, "pro": 2, "teams": 3, "enterprise": 4}

# ═══════════════════════════════════════════════════════════════════════════════
# 4 COMPUTE LEVELS — Model → Cost Matrix
# ═══════════════════════════════════════════════════════════════════════════════

COMPUTE_LEVELS = {
    "mini": {
        "name": "SAL Mini", "rate_per_min": 0.05, "color": "#2DD4BF",
        "min_tier": "free",
        "models": [
            {"name": "Claude Haiku 4.5", "your_cost": 0.008},
            {"name": "GPT-5 Fast", "your_cost": 0.010},
            {"name": "Gemini 2.0 Flash", "your_cost": 0.005},
            {"name": "Grok-3 Mini", "your_cost": 0.008}
        ],
        "stripe_product_id": "prod_U3jCcswitDPZGa",
        "stripe_price_id": "price_1T5bkVL47U80vDLAHHAjXmJh"
    },
    "pro": {
        "name": "SAL Pro", "rate_per_min": 0.25, "color": "#3B82F6",
        "min_tier": "starter",
        "models": [
            {"name": "Claude Sonnet 4.6", "your_cost": 0.045},
            {"name": "GPT-5 Core", "your_cost": 0.038},
            {"name": "Gemini 2.5 Pro", "your_cost": 0.030},
            {"name": "Grok-3 Biz", "your_cost": 0.035},
            {"name": "Grok 4.20 Beta", "your_cost": 0.050}
        ],
        "stripe_product_id": "prod_U3jCITpSX7gWMb",
        "stripe_price_id": "price_1T5bkWL47U80vDLA4EI3dylp"
    },
    "max": {
        "name": "SAL Max", "rate_per_min": 0.75, "color": "#8B5CF6",
        "min_tier": "pro",
        "models": [
            {"name": "Claude Opus 4.6", "your_cost": 0.150},
            {"name": "GPT-5 Extended Thinking", "your_cost": 0.120},
            {"name": "Gemini 2.5 Deep", "your_cost": 0.100},
            {"name": "DALL-E 3", "your_cost": 0.080},
            {"name": "Runway Gen-3", "your_cost": 0.200}
        ],
        "stripe_product_id": "prod_U3jCwgSsIuFazr",
        "stripe_price_id": "price_1T5bkXL47U80vDLAh6DLuS0j"
    },
    "max_fast": {
        "name": "SAL Max Fast", "rate_per_min": 1.00, "color": "#F59E0B",
        "min_tier": "teams",
        "models": [
            {"name": "Sonnet x Parallel", "your_cost": 0.180},
            {"name": "GPT-5 Fast x Batch", "your_cost": 0.080},
            {"name": "Grok-3 Biz x Parallel", "your_cost": 0.140},
            {"name": "Multi-agent pipeline", "your_cost": 0.300}
        ],
        "stripe_product_id": "prod_U3jCtc5UWeEIJx",
        "stripe_price_id": "price_1T5bkYL47U80vDLAVOs5fj75"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# ACTION COSTS (in compute minutes) + Generation Costs
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_COSTS = {
    # LLM chat — wall-clock based, these are averages
    "chat": 1, "chat_mini": 0.5, "chat_pro": 1, "chat_max": 2, "chat_max_fast": 3,
    # Search
    "search_tavily": 0.5, "search_exa": 0.5, "search_perplexity": 1, "search_deep": 3, "search_apollo": 2,
    # Career
    "cover_letter": 3, "linkedin_optimize": 2, "salary_negotiate": 2, "network_map": 2,
    # Business
    "business_plan": 10, "patent_search": 5, "entity_advisor": 3, "name_check": 1,
    # Cards
    "card_scan": 2, "card_grade": 3,
    # Real Estate
    "realestate_search": 1, "realestate_value": 1, "deal_analysis": 5,
    # Creative / Media
    "image_dalle3": 2, "image_replicate": 0.5, "image_stitch": 0, "image_grok": 1.5,
    "video_grok": 5, "video_template": 10, "video_runway": 20,
    "voice_elevenlabs": 3, "stt_deepgram": 1,
    # Builder
    "builder_quick": 5, "builder_full": 15, "builder_complex": 30,
    # Social
    "social_publish": 0, "content_generate": 2,
    # Formation
    "formation": 0, "ein_filing": 0, "dns_configure": 0, "ssl_provision": 0,
    "compliance_setup": 1,
}

# Formation products (FileForms) — Stripe IDs
FORMATION_PRODUCTS = {
    "basic_llc": {"price_id": "price_1T84WEL47U80vDLAYfgh6tne", "price": 197},
    "deluxe_llc": {"price_id": "price_1T84WFL47U80vDLAB1q3I1Me", "price": 397},
    "complete_llc": {"price_id": "price_1T84WGL47U80vDLAM7AVMeWV", "price": 449},
    "basic_corp": {"price_id": "price_1T84WHL47U80vDLA9xXux4cI", "price": 197},
    "deluxe_corp": {"price_id": "price_1T84WIL47U80vDLAKaIYgJNq", "price": 397},
    "complete_corp": {"price_id": "price_1T84WJL47U80vDLAj35gfAvk", "price": 449},
    "registered_agent": {"price_id": "price_1T84WLL47U80vDLAjC6OBz5s", "price": 224},
    "annual_report": {"price_id": "price_1T84WNL47U80vDLArGpX7xno", "price": 179},
}

# ═══════════════════════════════════════════════════════════════════════════════
# 88+ INTEGRATIONS CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

INTEGRATIONS = [
    # LLM Providers (6)
    {"id": "anthropic", "name": "Anthropic Claude", "desc": "Haiku/Sonnet/Opus", "category": "LLM", "type": "platform"},
    {"id": "azure_openai", "name": "Azure OpenAI (GPT-5)", "desc": "Core + Fast", "category": "LLM", "type": "platform"},
    {"id": "google_gemini", "name": "Google Gemini", "desc": "Flash + Pro", "category": "LLM", "type": "platform"},
    {"id": "xai_grok", "name": "xAI Grok", "desc": "3 + 4.20 Beta", "category": "LLM", "type": "platform"},
    {"id": "openai_direct", "name": "OpenAI Direct", "desc": "DALL-E 3, Whisper", "category": "LLM", "type": "user"},
    {"id": "perplexity", "name": "Perplexity", "desc": "Sonar search synthesis", "category": "LLM", "type": "platform"},
    # Search + Research (6)
    {"id": "exa", "name": "Exa Search", "desc": "Semantic neural search", "category": "Search", "type": "platform"},
    {"id": "tavily", "name": "Tavily", "desc": "Fast factual + Deep Research", "category": "Search", "type": "platform"},
    {"id": "tavily_mcp", "name": "Tavily MCP", "desc": "Agent workflow search", "category": "Search", "type": "platform"},
    {"id": "azure_search", "name": "Azure AI Search", "desc": "RAG knowledge base", "category": "Search", "type": "platform"},
    {"id": "apollo", "name": "Apollo", "desc": "CRM/lead enrichment", "category": "Search", "type": "platform"},
    {"id": "apify", "name": "Apify", "desc": "Web scraping at scale", "category": "Search", "type": "platform"},
    # Voice + Audio (6)
    {"id": "elevenlabs_tts", "name": "ElevenLabs TTS", "desc": "Voice synthesis", "category": "Voice", "type": "platform"},
    {"id": "elevenlabs_agent", "name": "ElevenLabs Agent", "desc": "Phone AI agent", "category": "Voice", "type": "platform"},
    {"id": "deepgram", "name": "Deepgram", "desc": "STT primary", "category": "Voice", "type": "platform"},
    {"id": "assemblyai", "name": "AssemblyAI", "desc": "STT fallback", "category": "Voice", "type": "platform"},
    {"id": "azure_stt", "name": "Azure Speech STT", "desc": "Enterprise STT", "category": "Voice", "type": "platform"},
    {"id": "azure_tts", "name": "Azure Speech TTS", "desc": "Enterprise TTS", "category": "Voice", "type": "platform"},
    # Media Generation (4)
    {"id": "runway", "name": "Runway ML", "desc": "Video Gen-3 Alpha", "category": "Media", "type": "platform"},
    {"id": "replicate", "name": "Replicate", "desc": "SDXL, Flux, open models", "category": "Media", "type": "platform"},
    {"id": "google_stitch", "name": "Google Stitch", "desc": "UI design generation", "category": "Media", "type": "platform"},
    {"id": "grok_imagine", "name": "Grok Imagine", "desc": "Image + video gen", "category": "Media", "type": "platform"},
    # CRM + Communication (4)
    {"id": "gohighlevel", "name": "GoHighLevel", "desc": "CRM, workflows, SaaS", "category": "CRM", "type": "user"},
    {"id": "ghl_location", "name": "GHL Location", "desc": "Sub-account ops", "category": "CRM", "type": "platform"},
    {"id": "twilio", "name": "Twilio", "desc": "SMS, voice, A2P 10DLC", "category": "CRM", "type": "platform"},
    {"id": "fileforms", "name": "FileForms", "desc": "Business formation API", "category": "CRM", "type": "platform"},
    # Database + Vector (5)
    {"id": "supabase", "name": "Supabase", "desc": "Primary DB + auth", "category": "Data", "type": "platform"},
    {"id": "azure_ai_search", "name": "Azure AI Search", "desc": "Vector + semantic", "category": "Data", "type": "platform"},
    {"id": "upstash", "name": "Upstash Vector", "desc": "Edge vector store", "category": "Data", "type": "platform"},
    {"id": "mongodb", "name": "MongoDB Atlas", "desc": "Document DB", "category": "Data", "type": "platform"},
    {"id": "databricks", "name": "Databricks", "desc": "Data lakehouse", "category": "Data", "type": "platform"},
    # Deploy + Infra (5)
    {"id": "vercel", "name": "Vercel", "desc": "Primary deploy + edge", "category": "Deploy", "type": "user"},
    {"id": "render", "name": "Render", "desc": "WS + background workers", "category": "Deploy", "type": "platform"},
    {"id": "cloudflare", "name": "Cloudflare", "desc": "Workers, D1, R2, DNS", "category": "Deploy", "type": "platform"},
    {"id": "github", "name": "GitHub", "desc": "Source control + CI/CD", "category": "Deploy", "type": "user"},
    {"id": "expo", "name": "Expo", "desc": "React Native mobile", "category": "Deploy", "type": "platform"},
    # Payment + Commerce (2)
    {"id": "stripe", "name": "Stripe", "desc": "Subscriptions + metered billing", "category": "Payment", "type": "platform"},
    {"id": "meld_crypto", "name": "Meld Crypto", "desc": "USDC payment gateway", "category": "Payment", "type": "platform"},
    # Email + Messaging (3)
    {"id": "resend", "name": "Resend", "desc": "Transactional email", "category": "Email", "type": "platform"},
    {"id": "sendgrid", "name": "SendGrid", "desc": "Bulk + marketing", "category": "Email", "type": "platform"},
    {"id": "deepl", "name": "DeepL", "desc": "Translation API", "category": "Email", "type": "platform"},
    # Real Estate Data (4)
    {"id": "rentcast", "name": "RentCast", "desc": "Rental comps + AVM", "category": "RE Data", "type": "platform"},
    {"id": "propertyradar", "name": "PropertyRadar", "desc": "Distressed leads", "category": "RE Data", "type": "platform"},
    {"id": "propertyapi", "name": "PropertyAPI", "desc": "ATTOM/Bridge data", "category": "RE Data", "type": "platform"},
    {"id": "google_maps", "name": "Google Maps", "desc": "Geo + places", "category": "RE Data", "type": "platform"},
    # Finance (1)
    {"id": "alpaca", "name": "Alpaca", "desc": "Stock/crypto market data", "category": "Finance", "type": "platform"},
    # Domain + Identity (2)
    {"id": "godaddy", "name": "GoDaddy", "desc": "Domain reg + DNS + SSL", "category": "Domain", "type": "platform"},
    {"id": "corpnet", "name": "CorpNet", "desc": "Legacy (replaced by FileForms)", "category": "Domain", "type": "platform"},
    # Analytics (3)
    {"id": "clarity", "name": "Microsoft Clarity", "desc": "Session replay", "category": "Analytics", "type": "platform"},
    {"id": "growthbook", "name": "GrowthBook", "desc": "Feature flags + A/B", "category": "Analytics", "type": "platform"},
    {"id": "gtm", "name": "Google Tag Manager", "desc": "Tag management", "category": "Analytics", "type": "platform"},
    # Dev Tools (7)
    {"id": "cursor", "name": "Cursor", "desc": "AI code editor", "category": "Dev", "type": "user"},
    {"id": "apidog", "name": "APIDOG", "desc": "API docs + testing", "category": "Dev", "type": "platform"},
    {"id": "smithery", "name": "Smithery AI", "desc": "MCP server registry", "category": "Dev", "type": "platform"},
    {"id": "kernel", "name": "Kernel", "desc": "AI kernel ops", "category": "Dev", "type": "platform"},
    {"id": "ai_gateway", "name": "AI Gateway", "desc": "Request routing", "category": "Dev", "type": "platform"},
    {"id": "airbyte", "name": "Airbyte", "desc": "Data sync + ETL", "category": "Dev", "type": "platform"},
    {"id": "mxbai", "name": "MXBAI", "desc": "Embeddings store", "category": "Dev", "type": "platform"},
    # Azure AI (6)
    {"id": "azure_safety", "name": "Content Safety", "desc": "Moderation", "category": "Azure", "type": "platform"},
    {"id": "azure_doc", "name": "Document Intelligence", "desc": "OCR + parsing", "category": "Azure", "type": "platform"},
    {"id": "azure_lang", "name": "Language", "desc": "NLP + sentiment", "category": "Azure", "type": "platform"},
    {"id": "azure_translate", "name": "Translator", "desc": "Multi-language", "category": "Azure", "type": "platform"},
    {"id": "azure_vision", "name": "Vision", "desc": "Image analysis + OCR", "category": "Azure", "type": "platform"},
    {"id": "azure_cognitive", "name": "Cognitive Services", "desc": "Umbrella API", "category": "Azure", "type": "platform"},
    # Growth (1)
    {"id": "rewardful", "name": "Rewardful", "desc": "Affiliate tracking (15%/25%)", "category": "Growth", "type": "platform"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY STATE (Production: Supabase usage_logs table)
# ═══════════════════════════════════════════════════════════════════════════════

user_data = {}

def get_user(user_id: str):
    if user_id not in user_data:
        user_data[user_id] = {
            "tier": "pro", "total_minutes": 0, "total_cost": 0.0,
            "entries": [], "rate_log": [],
            "overage_minutes": 0, "overage_cost": 0.0,
            "connectors": {}
        }
    return user_data[user_id]


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE GATING
# ═══════════════════════════════════════════════════════════════════════════════

def check_feature_access(user_tier: str, feature: str) -> dict:
    tier_config = TIERS.get(user_tier, TIERS["free"])
    features = tier_config["features"]
    if "*" in features or feature in features:
        return {"allowed": True, "user_tier": user_tier}
    min_tier = None
    for t_name, t_cfg in TIERS.items():
        if "*" in t_cfg["features"] or feature in t_cfg["features"]:
            if min_tier is None or TIER_RANK[t_name] < TIER_RANK.get(min_tier, 99):
                min_tier = t_name
    tc = TIERS.get(min_tier or "enterprise", TIERS["enterprise"])
    return {
        "allowed": False, "user_tier": user_tier,
        "required_tier": min_tier or "enterprise",
        "required_tier_name": tc["name"],
        "required_price": tc["price_monthly"],
        "upgrade_message": f"This feature requires {tc['name']} (${tc['price_monthly']}/mo) or higher.",
        "stripe_price_id": tc["stripe"]["monthly_price_id"]
    }


def check_rate_limit(user_id: str) -> dict:
    user = get_user(user_id)
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    limit = tier_config["rate_limit_per_hour"]
    if limit == -1:
        return {"allowed": True, "remaining": "unlimited", "limit": "unlimited"}
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - 3600
    recent = [e for e in user["rate_log"] if e > cutoff]
    user["rate_log"] = recent
    return {
        "allowed": len(recent) < limit,
        "used": len(recent), "limit": limit,
        "remaining": max(0, limit - len(recent)),
        "resets_in": int(3600 - (now.timestamp() - recent[0])) if recent else 3600
    }


def check_compute_budget(user_id: str) -> dict:
    user = get_user(user_id)
    tc = TIERS.get(user["tier"], TIERS["free"])
    limit = tc["compute_minutes"]
    if limit == -1:
        return {"allowed": True, "remaining": "unlimited", "cap_type": "none"}
    remaining = max(0, limit - user["total_minutes"])
    if remaining <= 0:
        if tc["cap_type"] == "hard":
            return {
                "allowed": False, "remaining": 0, "cap_type": "hard",
                "message": "Compute limit reached. Upgrade to continue.",
                "total": user["total_minutes"], "limit": limit
            }
        else:
            return {
                "allowed": True, "remaining": 0, "cap_type": "soft",
                "overage": True, "overage_rate": COMPUTE_LEVELS.get("pro", {}).get("rate_per_min", 0.25),
                "total": user["total_minutes"], "limit": limit
            }
    return {"allowed": True, "remaining": remaining, "cap_type": tc["cap_type"], "total": user["total_minutes"], "limit": limit}


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/tier-info")
async def get_tier_info():
    tiers = {}
    for name, cfg in TIERS.items():
        tiers[name] = {
            "name": cfg["name"],
            "price_monthly": cfg["price_monthly"],
            "price_annual": cfg["price_annual"],
            "compute_minutes": cfg["compute_minutes"],
            "cap_type": cfg["cap_type"],
            "color": cfg["color"],
            "models": cfg["models"],
            "seats": cfg["seats"],
            "description": cfg["description"],
            "stripe": cfg["stripe"],
            "rate_limit_per_hour": cfg["rate_limit_per_hour"]
        }
    return JSONResponse({
        "tiers": tiers,
        "compute_levels": {k: {"name": v["name"], "rate_per_min": v["rate_per_min"], "color": v["color"], "min_tier": v["min_tier"], "stripe_product_id": v["stripe_product_id"], "stripe_price_id": v["stripe_price_id"]} for k, v in COMPUTE_LEVELS.items()},
        "action_costs": ACTION_COSTS,
        "formation_products": FORMATION_PRODUCTS
    })


@router.post("/check-access")
async def check_access(request: Request):
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    feature = body.get("feature", "")
    user = get_user(user_id)

    access = check_feature_access(user["tier"], feature)
    if not access["allowed"]:
        return JSONResponse(access, status_code=403)

    rate = check_rate_limit(user_id)
    if not rate["allowed"]:
        return JSONResponse({"allowed": False, "reason": "rate_limit", "message": f"Rate limit exceeded. Resets in {rate.get('resets_in', 60)}s.", **rate}, status_code=429)

    budget = check_compute_budget(user_id)
    if not budget["allowed"]:
        return JSONResponse({"allowed": False, "reason": "compute_budget", **budget}, status_code=429)

    tc = TIERS.get(user["tier"], TIERS["free"])
    return JSONResponse({
        "allowed": True, "user_tier": user["tier"], "tier_name": tc["name"],
        "feature": feature, "remaining_minutes": budget.get("remaining", "unlimited"),
        "rate_remaining": rate.get("remaining", "unlimited"),
        "overage": budget.get("overage", False)
    })


@router.post("/log")
async def log_usage(request: Request):
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    action = body.get("action", "")
    compute_minutes = body.get("compute_minutes", ACTION_COSTS.get(action, 1))
    model_used = body.get("model_used", "")
    compute_level = body.get("compute_level", "pro")

    user = get_user(user_id)
    tc = TIERS.get(user["tier"], TIERS["free"])
    cl = COMPUTE_LEVELS.get(compute_level, COMPUTE_LEVELS["pro"])
    cost_usd = round(compute_minutes * cl["rate_per_min"], 4)

    entry = {
        "action": action, "compute_minutes": compute_minutes,
        "compute_level": compute_level, "model_used": model_used,
        "cost_usd": cost_usd,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    user["entries"].append(entry)
    if len(user["entries"]) > 500:
        user["entries"] = user["entries"][-500:]
    user["total_minutes"] += compute_minutes
    user["total_cost"] += cost_usd
    user["rate_log"].append(datetime.now(timezone.utc).timestamp())

    limit = tc["compute_minutes"]
    if limit > 0 and user["total_minutes"] > limit:
        user["overage_minutes"] = user["total_minutes"] - limit
        user["overage_cost"] = round(user["overage_minutes"] * cl["rate_per_min"], 2)

    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"
    return JSONResponse({
        "logged": True, "action": action, "cost_minutes": compute_minutes,
        "cost_usd": cost_usd, "compute_level": compute_level,
        "total_minutes_used": user["total_minutes"],
        "total_cost_usd": round(user["total_cost"], 2),
        "tier": user["tier"], "tier_name": tc["name"],
        "limit": limit, "remaining": remaining,
        "overage_minutes": user["overage_minutes"],
        "overage_cost": user["overage_cost"],
        "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0
    })


@router.get("/usage")
async def get_usage(request: Request):
    user_id = request.query_params.get("user_id", "anonymous")
    user = get_user(user_id)
    tc = TIERS.get(user["tier"], TIERS["free"])
    limit = tc["compute_minutes"]
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"
    return JSONResponse({
        "user_id": user_id, "tier": user["tier"], "tier_name": tc["name"],
        "tier_color": tc["color"], "total_minutes": user["total_minutes"],
        "total_cost_usd": round(user["total_cost"], 2),
        "limit": limit, "remaining": remaining,
        "cap_type": tc["cap_type"],
        "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0,
        "overage_minutes": user["overage_minutes"],
        "overage_cost": user["overage_cost"],
        "rate_limit": tc["rate_limit_per_hour"],
        "recent_entries": user["entries"][-20:]
    })


@router.get("/dashboard")
async def get_dashboard(request: Request):
    user_id = request.query_params.get("user_id", "anonymous")
    user = get_user(user_id)
    tc = TIERS.get(user["tier"], TIERS["free"])
    limit = tc["compute_minutes"]
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"

    action_breakdown = {}
    for entry in user["entries"]:
        act = entry["action"]
        if act not in action_breakdown:
            action_breakdown[act] = {"count": 0, "minutes": 0, "cost": 0}
        action_breakdown[act]["count"] += 1
        action_breakdown[act]["minutes"] += entry["compute_minutes"]
        action_breakdown[act]["cost"] += entry.get("cost_usd", 0)
    sorted_actions = sorted(action_breakdown.items(), key=lambda x: x[1]["minutes"], reverse=True)
    rate = check_rate_limit(user_id)

    return JSONResponse({
        "user_id": user_id, "tier": user["tier"], "tier_name": tc["name"],
        "tier_color": tc["color"], "price_monthly": tc["price_monthly"],
        "compute": {
            "used": user["total_minutes"], "limit": limit,
            "remaining": remaining, "cap_type": tc["cap_type"],
            "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0,
            "unlimited": limit == -1
        },
        "cost": {"total_usd": round(user["total_cost"], 2)},
        "overage": {
            "minutes": user["overage_minutes"], "cost": user["overage_cost"],
            "allowed": tc["overage_allowed"], "cap_type": tc["cap_type"]
        },
        "rate_limit": {
            "used": rate.get("used", 0), "limit": rate.get("limit", 0),
            "remaining": rate.get("remaining", 0)
        },
        "action_breakdown": [{"action": a, **d} for a, d in sorted_actions[:10]],
        "recent_activity": user["entries"][-5:],
        "models_available": tc["models"],
        "seats": tc["seats"],
        "total_actions": len(user["entries"])
    })


@router.post("/set-tier")
async def set_tier(request: Request):
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    new_tier = body.get("tier", "free")
    if new_tier not in TIERS:
        return JSONResponse({"error": f"Invalid tier: {new_tier}"}, status_code=400)
    user = get_user(user_id)
    old_tier = user["tier"]
    user["tier"] = new_tier
    tc = TIERS[new_tier]
    return JSONResponse({
        "success": True, "user_id": user_id, "old_tier": old_tier, "new_tier": new_tier,
        "tier_name": tc["name"], "compute_minutes": tc["compute_minutes"],
        "price_monthly": tc["price_monthly"]
    })


@router.get("/integrations")
async def get_integrations(request: Request):
    category = request.query_params.get("category", "")
    items = INTEGRATIONS
    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]
    categories = sorted(list(set(i["category"] for i in INTEGRATIONS)))
    return JSONResponse({
        "integrations": items,
        "categories": categories,
        "total": len(INTEGRATIONS)
    })


@router.get("/compute-levels")
async def get_compute_levels():
    return JSONResponse({"levels": {k: {"name": v["name"], "rate_per_min": v["rate_per_min"], "color": v["color"], "min_tier": v["min_tier"], "models": v["models"]} for k, v in COMPUTE_LEVELS.items()}})
