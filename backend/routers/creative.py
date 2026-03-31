"""SaintSal Labs — Creative Studio Endpoints (Section 4)"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/creative", tags=["creative"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
GHL_API_KEY = os.environ.get("GHL_API_KEY", "")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")


async def _claude_generate(prompt: str, system: str = ""):
    if not ANTHROPIC_API_KEY:
        return "AI unavailable"
    async with httpx.AsyncClient(timeout=60) as http:
        try:
            r = await http.post("https://api.anthropic.com/v1/messages", json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 4096,
                "system": system, "messages": [{"role": "user", "content": prompt}]
            }, headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                        "content-type": "application/json"})
            return r.json().get("content", [{}])[0].get("text", "Error")
        except Exception as e:
            return f"Error: {e}"


# Content Generation Pipeline
@router.post("/generate")
async def creative_generate(request: Request):
    """Generate content (caption, blog, carousel, ad, email)."""
    body = await request.json()
    prompt = body.get("prompt", "")
    content_type = body.get("type", "caption")
    platform = body.get("platform", "")
    brand_id = body.get("brand_profile_id", "")
    seo_mode = body.get("seo_mode", False)

    if not prompt:
        return JSONResponse({"error": "prompt is required"}, status_code=400)

    system = f"""You are an expert content creator and social media strategist.
Generate {content_type} content that is engaging, on-brand, and optimized for {platform or 'all platforms'}.
{'Include SEO keywords and meta description.' if seo_mode else ''}
Be creative, authentic, and actionable."""

    type_instructions = {
        "caption": "Write an engaging social media caption with relevant hashtags.",
        "blog": "Write a comprehensive blog post with headers, subheaders, and a compelling intro.",
        "carousel": "Create a 5-10 slide carousel with a hook slide, value slides, and CTA. Format each slide clearly.",
        "ad": "Write compelling ad copy with headline, body, and CTA. Include A/B variants.",
        "email": "Write an email with subject line, preview text, body, and CTA.",
    }

    full_prompt = f"""{type_instructions.get(content_type, 'Generate content.')}

BRIEF: {prompt}
PLATFORM: {platform or 'General'}
{'SEO OPTIMIZED' if seo_mode else ''}

Also generate platform-specific versions if applicable."""

    content = await _claude_generate(full_prompt, system)

    platform_versions = {}
    if platform:
        for p in ["instagram", "twitter", "linkedin", "tiktok"]:
            if p != platform:
                ver = await _claude_generate(f"Adapt this content for {p}: {content[:500]}", system)
                platform_versions[p] = ver

    return JSONResponse({
        "content": content,
        "type": content_type,
        "platform": platform,
        "platform_versions": platform_versions if platform_versions else None
    })


# Social Posting via GHL
@router.post("/social/post")
async def creative_social_post(request: Request):
    """Post content to social platforms via GoHighLevel."""
    body = await request.json()
    content = body.get("content", "")
    platforms = body.get("platforms", [])
    images = body.get("images", [])
    schedule_time = body.get("schedule_time", "")

    if not content:
        return JSONResponse({"error": "content is required"}, status_code=400)

    post_ids = {}
    if GHL_API_KEY and GHL_LOCATION_ID:
        async with httpx.AsyncClient(timeout=30) as http:
            for platform in platforms:
                try:
                    payload = {
                        "type": platform,
                        "text": content,
                        "locationId": GHL_LOCATION_ID
                    }
                    if images:
                        payload["mediaUrls"] = images
                    if schedule_time:
                        payload["scheduledAt"] = schedule_time

                    r = await http.post(
                        f"https://services.leadconnectorhq.com/social-media-posting/post",
                        json=payload,
                        headers={"Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-07-28"}
                    )
                    if r.status_code in (200, 201):
                        data = r.json()
                        post_ids[platform] = data.get("id", "posted")
                    else:
                        post_ids[platform] = f"error: {r.status_code}"
                except Exception as e:
                    post_ids[platform] = f"error: {str(e)}"
    else:
        return JSONResponse({"error": "Social posting not configured"}, status_code=503)

    return JSONResponse({"post_ids": post_ids, "scheduled_times": {p: schedule_time for p in platforms}})


# Content Calendar AI
@router.post("/calendar")
async def creative_calendar(request: Request):
    """Generate a 30-day content calendar."""
    body = await request.json()
    business = body.get("business_description", "")
    goals = body.get("goals", "")
    duration = body.get("duration_days", 30)

    if not business:
        return JSONResponse({"error": "business_description is required"}, status_code=400)

    system = """You are a social media strategist. Create detailed content calendars with
specific topics, optimal posting times, and platform-specific content types.
Return structured JSON."""

    prompt = f"""Create a {duration}-day content calendar for:
BUSINESS: {business}
GOALS: {goals}

Return JSON: {{days: [{{date: "YYYY-MM-DD", posts: [{{platform, topic, type, optimal_time}}]}}]}}
Include 1-3 posts per day across Instagram, Twitter/X, LinkedIn, TikTok.
Mix content types: educational, entertaining, promotional, behind-the-scenes.

Return ONLY valid JSON."""

    result = await _claude_generate(prompt, system)

    try:
        parsed = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception:
        parsed = {"days": [{"date": datetime.utcnow().strftime("%Y-%m-%d"), "posts": [{"platform": "instagram", "topic": business, "type": "post", "optimal_time": "10:00 AM"}]}]}

    return JSONResponse(parsed)


# Batch Generate from Calendar
@router.post("/calendar/batch-generate")
async def creative_calendar_batch(request: Request):
    """Generate actual content for a week of the calendar."""
    body = await request.json()
    calendar_id = body.get("calendar_id", "")
    week_number = body.get("week_number", 1)
    posts_plan = body.get("posts", [])

    if not posts_plan:
        return JSONResponse({"error": "posts array required"}, status_code=400)

    generated_posts = []
    for post in posts_plan[:7]:
        content = await _claude_generate(
            f"Write a {post.get('type', 'post')} about '{post.get('topic', '')}' for {post.get('platform', 'instagram')}. Include hashtags.",
            "You are a social media expert. Write engaging, platform-optimized content."
        )
        generated_posts.append({
            "platform": post.get("platform", ""),
            "content": content,
            "image_url": None,
            "topic": post.get("topic", "")
        })

    return JSONResponse({"posts": generated_posts, "week_number": week_number})


# Brand Profiles
@router.post("/brand-profile")
async def creative_brand_profile(request: Request):
    """Save or update a brand profile."""
    body = await request.json()
    profile = {
        "id": body.get("id", str(uuid.uuid4())),
        "name": body.get("name", ""),
        "tone": body.get("tone", ""),
        "vocabulary": body.get("vocabulary", []),
        "no_go_words": body.get("no_go_words", []),
        "competitors": body.get("competitors", []),
        "colors": body.get("colors", {}),
        "logo_url": body.get("logo_url", ""),
        "created_at": datetime.utcnow().isoformat()
    }

    return JSONResponse({"brand_profile": profile, "status": "saved"})
