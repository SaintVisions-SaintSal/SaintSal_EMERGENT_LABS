"""SaintSal Labs — Metering, Tier Gating & Usage Dashboard (Section 7 v2)"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime, timezone
from functools import wraps

router = APIRouter(prefix="/api/metering", tags=["metering"])

# ─── Tier Configuration ──────────────────────────────────────────────────────
TIERS = {
    "free": {
        "name": "Free",
        "compute_minutes": 100,
        "overage_rate": 0.00,
        "overage_allowed": False,
        "color": "#6B7280",
        "features": [
            "search", "news", "sports", "tech", "finance_basic",
            "career_overview", "career_jobs", "career_tracker",
            "cookin_cards_price", "cookin_cards_deals"
        ],
        "rate_limit_per_hour": 30,
        "models": ["mini"]
    },
    "starter": {
        "name": "Starter",
        "compute_minutes": 500,
        "overage_rate": 0.25,
        "overage_allowed": True,
        "color": "#10B981",
        "features": [
            "search", "news", "sports", "tech", "finance_basic", "finance_advanced",
            "career_overview", "career_jobs", "career_tracker", "career_resume",
            "career_coverletter", "career_linkedin",
            "realestate_search", "realestate_portfolio",
            "cookin_cards_price", "cookin_cards_deals", "cookin_cards_scan",
            "business_overview", "business_domains", "business_resume", "business_signatures",
            "social_studio_basic"
        ],
        "rate_limit_per_hour": 100,
        "models": ["mini", "pro"]
    },
    "pro": {
        "name": "Pro",
        "compute_minutes": 2000,
        "overage_rate": 0.75,
        "overage_allowed": True,
        "color": "#8B5CF6",
        "features": [
            "search", "news", "sports", "tech",
            "finance_basic", "finance_advanced", "finance_dcf",
            "career_overview", "career_jobs", "career_tracker", "career_resume",
            "career_coverletter", "career_linkedin", "career_salary", "career_network",
            "realestate_search", "realestate_portfolio", "realestate_deal_analyzer", "realestate_ask_sal",
            "cookin_cards_price", "cookin_cards_deals", "cookin_cards_scan", "cookin_cards_grade", "cookin_cards_portfolio",
            "business_overview", "business_domains", "business_resume", "business_signatures",
            "business_meetings", "business_analytics", "business_bizplan", "business_patent",
            "business_formation",
            "social_studio_basic", "social_studio_advanced",
            "builder_basic",
            "medical_basic"
        ],
        "rate_limit_per_hour": 300,
        "models": ["mini", "pro", "max"]
    },
    "teams": {
        "name": "Teams",
        "compute_minutes": 10000,
        "overage_rate": 1.00,
        "overage_allowed": True,
        "color": "#F59E0B",
        "features": ["*"],  # All features
        "rate_limit_per_hour": 1000,
        "models": ["mini", "pro", "max", "max_pro"]
    },
    "enterprise": {
        "name": "Enterprise",
        "compute_minutes": -1,  # Unlimited
        "overage_rate": 0,
        "overage_allowed": True,
        "color": "#E5E5E5",
        "features": ["*"],
        "rate_limit_per_hour": -1,  # Unlimited
        "models": ["mini", "pro", "max", "max_pro"]
    }
}

TIER_RANK = {"free": 0, "starter": 1, "pro": 2, "teams": 3, "enterprise": 4}

# Compute costs per action type (in minutes)
ACTION_COSTS = {
    "chat": 1,
    "search": 0.5,
    "cover_letter": 3,
    "linkedin_optimize": 2,
    "salary_negotiate": 2,
    "network_map": 2,
    "business_plan": 10,
    "patent_search": 5,
    "card_scan": 2,
    "card_grade": 3,
    "realestate_search": 1,
    "realestate_value": 1,
    "deal_analysis": 5,
    "formation": 0,
    "name_check": 1,
    "entity_advisor": 3,
    "creative_generate": 5,
    "builder_run": 15,
    "image_gen": 3,
    "video_gen": 8,
    "audio_gen": 4,
    "code_gen": 5,
}

# ─── In-memory usage tracking ────────────────────────────────────────────────
user_data = {}  # { user_id: { tier, total_minutes, entries[], rate_log[] } }


def get_user(user_id: str):
    if user_id not in user_data:
        user_data[user_id] = {
            "tier": "pro",  # Default for dev — production reads from Supabase
            "total_minutes": 0,
            "total_cost": 0.0,
            "entries": [],
            "rate_log": [],
            "overage_minutes": 0,
            "overage_cost": 0.0
        }
    return user_data[user_id]


# ─── Feature Gate Check ──────────────────────────────────────────────────────
def check_feature_access(user_tier: str, feature: str) -> dict:
    """Check if a tier has access to a feature. Returns access status and minimum required tier."""
    tier_config = TIERS.get(user_tier, TIERS["free"])
    features = tier_config["features"]
    
    if "*" in features or feature in features:
        return {"allowed": True, "user_tier": user_tier}
    
    # Find minimum required tier
    min_tier = None
    for tier_name, tier_cfg in TIERS.items():
        if "*" in tier_cfg["features"] or feature in tier_cfg["features"]:
            if min_tier is None or TIER_RANK[tier_name] < TIER_RANK[min_tier]:
                min_tier = tier_name
    
    return {
        "allowed": False,
        "user_tier": user_tier,
        "required_tier": min_tier or "enterprise",
        "required_tier_name": TIERS.get(min_tier, {}).get("name", "Enterprise"),
        "upgrade_message": f"This feature requires the {TIERS.get(min_tier, {}).get('name', 'Enterprise')} plan or higher."
    }


def check_rate_limit(user_id: str) -> dict:
    """Check if user is within their hourly rate limit."""
    user = get_user(user_id)
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    limit = tier_config["rate_limit_per_hour"]
    
    if limit == -1:
        return {"allowed": True, "remaining": "unlimited"}
    
    now = datetime.now(timezone.utc)
    one_hour_ago = now.timestamp() - 3600
    recent = [e for e in user["rate_log"] if e > one_hour_ago]
    user["rate_log"] = recent  # Prune old entries
    
    return {
        "allowed": len(recent) < limit,
        "used": len(recent),
        "limit": limit,
        "remaining": max(0, limit - len(recent)),
        "resets_in": int(3600 - (now.timestamp() - recent[0])) if recent else 3600
    }


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/tier-info")
async def get_tier_info(request: Request):
    """Get all tier configurations for pricing display."""
    tiers = {}
    for name, cfg in TIERS.items():
        tiers[name] = {
            "name": cfg["name"],
            "compute_minutes": cfg["compute_minutes"],
            "overage_rate": cfg["overage_rate"],
            "color": cfg["color"],
            "rate_limit_per_hour": cfg["rate_limit_per_hour"],
            "models": cfg["models"],
            "feature_count": len(cfg["features"]) if "*" not in cfg["features"] else "All"
        }
    return JSONResponse({"tiers": tiers, "action_costs": ACTION_COSTS})


@router.post("/check-access")
async def check_access(request: Request):
    """Check if user can access a specific feature."""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    feature = body.get("feature", "")
    
    user = get_user(user_id)
    
    # Feature gate
    access = check_feature_access(user["tier"], feature)
    if not access["allowed"]:
        return JSONResponse(access, status_code=403)
    
    # Rate limit
    rate = check_rate_limit(user_id)
    if not rate["allowed"]:
        return JSONResponse({
            "allowed": False,
            "reason": "rate_limit",
            "message": f"Rate limit exceeded. {rate['remaining']} requests remaining. Resets in {rate['resets_in']}s.",
            **rate
        }, status_code=429)
    
    # Compute budget
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    limit = tier_config["compute_minutes"]
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else float('inf')
    
    action_cost = ACTION_COSTS.get(feature.split("_")[0] if "_" in feature else feature, 1)
    if remaining <= 0 and not tier_config["overage_allowed"]:
        return JSONResponse({
            "allowed": False,
            "reason": "compute_budget",
            "message": "Compute budget exhausted. Upgrade your plan for more credits.",
            "total_minutes": user["total_minutes"],
            "limit": limit,
            "remaining": 0
        }, status_code=403)
    
    return JSONResponse({
        "allowed": True,
        "user_tier": user["tier"],
        "tier_name": tier_config["name"],
        "feature": feature,
        "action_cost": action_cost,
        "remaining_minutes": remaining if limit > 0 else "unlimited",
        "rate_remaining": rate["remaining"]
    })


@router.post("/log")
async def log_usage(request: Request):
    """Log compute usage after an action completes."""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    action = body.get("action", "")
    compute_minutes = body.get("compute_minutes", ACTION_COSTS.get(action, 1))
    model_used = body.get("model_used", "")
    
    user = get_user(user_id)
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    
    entry = {
        "action": action,
        "compute_minutes": compute_minutes,
        "model_used": model_used,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    user["entries"].append(entry)
    if len(user["entries"]) > 500:
        user["entries"] = user["entries"][-500:]
    
    user["total_minutes"] += compute_minutes
    user["rate_log"].append(datetime.now(timezone.utc).timestamp())
    
    # Calculate overage
    limit = tier_config["compute_minutes"]
    if limit > 0 and user["total_minutes"] > limit:
        user["overage_minutes"] = user["total_minutes"] - limit
        user["overage_cost"] = round(user["overage_minutes"] * tier_config["overage_rate"], 2)
    
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"
    
    return JSONResponse({
        "logged": True,
        "action": action,
        "cost": compute_minutes,
        "total_minutes_used": user["total_minutes"],
        "tier": user["tier"],
        "tier_name": tier_config["name"],
        "limit": limit,
        "remaining": remaining,
        "overage_minutes": user["overage_minutes"],
        "overage_cost": user["overage_cost"],
        "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0
    })


@router.get("/usage")
async def get_usage(request: Request):
    """Get user's current usage summary."""
    user_id = request.query_params.get("user_id", "anonymous")
    user = get_user(user_id)
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    limit = tier_config["compute_minutes"]
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"
    
    return JSONResponse({
        "user_id": user_id,
        "tier": user["tier"],
        "tier_name": tier_config["name"],
        "tier_color": tier_config["color"],
        "total_minutes": user["total_minutes"],
        "limit": limit,
        "remaining": remaining,
        "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0,
        "overage_minutes": user["overage_minutes"],
        "overage_cost": user["overage_cost"],
        "rate_limit": tier_config["rate_limit_per_hour"],
        "recent_entries": user["entries"][-20:]
    })


@router.get("/dashboard")
async def get_dashboard(request: Request):
    """Get comprehensive dashboard data for the metering widget."""
    user_id = request.query_params.get("user_id", "anonymous")
    user = get_user(user_id)
    tier_config = TIERS.get(user["tier"], TIERS["free"])
    limit = tier_config["compute_minutes"]
    remaining = max(0, limit - user["total_minutes"]) if limit > 0 else "unlimited"
    
    # Group usage by action type
    action_breakdown = {}
    for entry in user["entries"]:
        act = entry["action"]
        if act not in action_breakdown:
            action_breakdown[act] = {"count": 0, "minutes": 0}
        action_breakdown[act]["count"] += 1
        action_breakdown[act]["minutes"] += entry["compute_minutes"]
    
    # Sort by minutes desc
    sorted_actions = sorted(action_breakdown.items(), key=lambda x: x[1]["minutes"], reverse=True)
    
    rate = check_rate_limit(user_id)
    
    return JSONResponse({
        "user_id": user_id,
        "tier": user["tier"],
        "tier_name": tier_config["name"],
        "tier_color": tier_config["color"],
        "compute": {
            "used": user["total_minutes"],
            "limit": limit,
            "remaining": remaining,
            "pct_used": round((user["total_minutes"] / limit * 100), 1) if limit > 0 else 0,
            "unlimited": limit == -1
        },
        "overage": {
            "minutes": user["overage_minutes"],
            "cost": user["overage_cost"],
            "rate": tier_config["overage_rate"],
            "allowed": tier_config["overage_allowed"]
        },
        "rate_limit": {
            "used": rate.get("used", 0),
            "limit": rate.get("limit", 0),
            "remaining": rate.get("remaining", 0)
        },
        "action_breakdown": [{"action": a, **d} for a, d in sorted_actions[:10]],
        "recent_activity": user["entries"][-5:],
        "models_available": tier_config["models"],
        "total_actions": len(user["entries"])
    })


@router.post("/set-tier")
async def set_tier(request: Request):
    """Set user's tier (for testing/admin). Production: Stripe webhook."""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    new_tier = body.get("tier", "free")
    
    if new_tier not in TIERS:
        return JSONResponse({"error": f"Invalid tier: {new_tier}. Valid: {list(TIERS.keys())}"}, status_code=400)
    
    user = get_user(user_id)
    old_tier = user["tier"]
    user["tier"] = new_tier
    
    tier_config = TIERS[new_tier]
    
    return JSONResponse({
        "success": True,
        "user_id": user_id,
        "old_tier": old_tier,
        "new_tier": new_tier,
        "tier_name": tier_config["name"],
        "compute_minutes": tier_config["compute_minutes"],
        "features_count": len(tier_config["features"]) if "*" not in tier_config["features"] else "All"
    })
