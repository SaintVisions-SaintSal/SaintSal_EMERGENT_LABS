"""SaintSal Labs — Metering & Tier Gating (Section 7)"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime

router = APIRouter(prefix="/api/metering", tags=["metering"])

# Tier configuration
TIER_LIMITS = {
    "free": {"compute_minutes": 100, "overage_rate": 0.05},
    "starter": {"compute_minutes": 500, "overage_rate": 0.25},
    "pro": {"compute_minutes": 2000, "overage_rate": 0.75},
    "teams": {"compute_minutes": 10000, "overage_rate": 1.00},
    "enterprise": {"compute_minutes": -1, "overage_rate": 0}  # Unlimited
}

TIER_RANK = {"free": 0, "starter": 1, "pro": 2, "teams": 3, "enterprise": 4}

# In-memory usage tracking (production: use Supabase)
usage_log = {}


async def check_tier(user_id: str, required_tier: str):
    """Check if user has required tier access."""
    # In production, this checks Supabase profiles table
    user_tier = "pro"  # Default for development
    if TIER_RANK.get(user_tier, 0) < TIER_RANK.get(required_tier, 0):
        raise HTTPException(403, f"Requires {required_tier} plan. Current: {user_tier}")
    return user_tier


@router.post("/log")
async def log_usage(request: Request):
    """Log compute usage for metering."""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    action = body.get("action", "")
    compute_minutes = body.get("compute_minutes", 0)
    model_used = body.get("model_used", "")

    if user_id not in usage_log:
        usage_log[user_id] = {"entries": [], "total_minutes": 0}

    entry = {
        "action": action,
        "compute_minutes": compute_minutes,
        "model_used": model_used,
        "timestamp": datetime.utcnow().isoformat()
    }

    usage_log[user_id]["entries"].append(entry)
    usage_log[user_id]["total_minutes"] += compute_minutes

    # Check if over tier limit
    user_tier = "pro"  # Default
    tier_config = TIER_LIMITS.get(user_tier, TIER_LIMITS["free"])
    limit = tier_config["compute_minutes"]
    total = usage_log[user_id]["total_minutes"]

    overage = max(0, total - limit) if limit > 0 else 0
    overage_cost = overage * tier_config["overage_rate"]

    return JSONResponse({
        "logged": True,
        "user_id": user_id,
        "total_minutes_used": total,
        "tier_limit": limit,
        "remaining": max(0, limit - total) if limit > 0 else "unlimited",
        "overage_minutes": overage,
        "overage_cost": round(overage_cost, 2)
    })


@router.get("/usage")
async def get_usage(request: Request):
    """Get user's current usage."""
    user_id = request.query_params.get("user_id", "anonymous")
    data = usage_log.get(user_id, {"entries": [], "total_minutes": 0})

    user_tier = "pro"
    tier_config = TIER_LIMITS.get(user_tier, TIER_LIMITS["free"])

    return JSONResponse({
        "user_id": user_id,
        "tier": user_tier,
        "total_minutes": data["total_minutes"],
        "limit": tier_config["compute_minutes"],
        "remaining": max(0, tier_config["compute_minutes"] - data["total_minutes"]) if tier_config["compute_minutes"] > 0 else "unlimited",
        "recent_entries": data["entries"][-10:]
    })
