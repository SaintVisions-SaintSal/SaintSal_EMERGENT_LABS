"""SaintSal Labs — Career Suite New Endpoints (Section 3.1-3.4)"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
import json

router = APIRouter(prefix="/api/career", tags=["career"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")


async def _claude_generate(prompt: str, system: str = "", model: str = "claude-sonnet-4-20250514"):
    if not ANTHROPIC_API_KEY:
        return "AI service unavailable. Please configure ANTHROPIC_API_KEY."
    async with httpx.AsyncClient(timeout=60) as http:
        try:
            messages = [{"role": "user", "content": prompt}]
            body = {"model": model, "max_tokens": 4096, "messages": messages}
            if system:
                body["system"] = system
            r = await http.post("https://api.anthropic.com/v1/messages", json=body,
                                headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
            data = r.json()
            return data.get("content", [{}])[0].get("text", "Error generating response")
        except Exception as e:
            return f"Error: {str(e)}"


async def _exa_search(query: str, num_results: int = 5):
    if not EXA_API_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as http:
        try:
            r = await http.post("https://api.exa.ai/search", json={
                "query": query, "numResults": num_results, "useAutoprompt": True, "type": "neural"
            }, headers={"Authorization": f"Bearer {EXA_API_KEY}", "Content-Type": "application/json"})
            return r.json().get("results", [])
        except Exception:
            return []


# 3.1 — Cover Letter AI
@router.post("/cover-letter")
async def cover_letter(request: Request):
    """Generate a tailored cover letter from resume + job description."""
    body = await request.json()
    resume_text = body.get("resume_text", "")
    job_description = body.get("job_description", "")
    style = body.get("style", "direct")

    if not resume_text or not job_description:
        return JSONResponse({"error": "resume_text and job_description are required"}, status_code=400)

    system = """You are an expert career consultant who writes compelling cover letters.
Match the candidate's experience to the job requirements precisely.
Use specific achievements and metrics from the resume.
Never use generic phrases. Be authentic and specific."""

    prompt = f"""Write a {style} cover letter based on this resume and job description.

STYLE: {style}
- direct: concise, achievement-focused, no fluff
- storytelling: narrative arc connecting experience to role
- technical: emphasize technical skills and projects

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return a complete, ready-to-send cover letter. Include keyword matches from the job description."""

    cover_letter_text = await _claude_generate(prompt, system)

    keywords_in_jd = set(w.lower() for w in job_description.split() if len(w) > 4)
    keywords_in_letter = set(w.lower() for w in cover_letter_text.split() if len(w) > 4)
    matched = keywords_in_jd & keywords_in_letter

    return JSONResponse({
        "cover_letter": cover_letter_text,
        "word_count": len(cover_letter_text.split()),
        "keywords_matched": list(matched)[:20],
        "style": style
    })


# 3.2 — LinkedIn Optimizer
@router.post("/linkedin-optimize")
async def linkedin_optimize(request: Request):
    """Optimize LinkedIn profile with AI rewriting."""
    body = await request.json()
    current_profile = body.get("current_profile_text", "")

    if not current_profile:
        return JSONResponse({"error": "current_profile_text is required"}, status_code=400)

    system = """You are a LinkedIn optimization expert. You know the LinkedIn algorithm, 
recruiter search patterns, and what makes profiles rank higher in searches.
Always return structured JSON."""

    prompt = f"""Analyze and optimize this LinkedIn profile. Return a JSON object with:
- headline: optimized headline (max 220 chars, keyword-rich)
- summary: rewritten About section (compelling, keyword-optimized)
- experience_rewrites: array of rewritten experience bullets (achievement-focused, metrics-driven)
- skills_to_add: array of skills to add for better visibility
- score_before: estimated profile strength score (0-100)
- score_after: estimated score after optimizations

CURRENT PROFILE:
{current_profile}

Return ONLY valid JSON, no markdown."""

    result = await _claude_generate(prompt, system, "claude-sonnet-4-20250514")

    try:
        parsed = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception:
        parsed = {
            "headline": "Error parsing result",
            "summary": result,
            "experience_rewrites": [],
            "skills_to_add": [],
            "score_before": 45,
            "score_after": 85
        }

    return JSONResponse(parsed)


# 3.3 — Salary Negotiator
@router.post("/salary-negotiate")
async def salary_negotiate(request: Request):
    """Generate salary negotiation strategy with market data."""
    body = await request.json()
    offer_details = body.get("offer_details", "")
    role = body.get("role", "")
    location = body.get("location", "")
    experience_years = body.get("experience_years", 0)

    if not role:
        return JSONResponse({"error": "role is required"}, status_code=400)

    # Research market data via Exa
    research_results = await _exa_search(
        f"salary range {role} {location} {experience_years} years experience levels.fyi glassdoor 2026",
        num_results=5
    )
    research_context = "\n".join([f"- {r.get('title', '')}: {r.get('url', '')}" for r in research_results])

    system = """You are an expert salary negotiation coach with deep knowledge of compensation data.
Always provide specific numbers and actionable scripts."""

    prompt = f"""Generate a complete salary negotiation strategy:

OFFER DETAILS: {offer_details}
ROLE: {role}
LOCATION: {location}
EXPERIENCE: {experience_years} years

MARKET RESEARCH:
{research_context}

Return a JSON object with:
- market_range: {{low, median, high, top_10_pct}} (annual salary figures)
- counter_offer_script: word-for-word script to use in negotiation
- rationale: bullet points justifying the counter
- data_sources: array of sources used
- negotiation_tips: array of tactical tips
- total_comp_considerations: things beyond base salary to negotiate

Return ONLY valid JSON."""

    result = await _claude_generate(prompt, system)

    try:
        parsed = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception:
        parsed = {
            "market_range": {"low": 0, "median": 0, "high": 0},
            "counter_offer_script": result,
            "rationale": [],
            "data_sources": [r.get("url", "") for r in research_results]
        }

    return JSONResponse(parsed)


# 3.4 — Network Mapper
@router.post("/network-map")
async def network_map(request: Request):
    """Map potential connections at a target company."""
    body = await request.json()
    target_company = body.get("target_company", "")
    user_linkedin_url = body.get("user_linkedin_url", "")

    if not target_company:
        return JSONResponse({"error": "target_company is required"}, status_code=400)

    connections = []
    if APOLLO_API_KEY:
        async with httpx.AsyncClient(timeout=15) as http:
            try:
                r = await http.post("https://api.apollo.io/v1/mixed_people/search", json={
                    "api_key": APOLLO_API_KEY,
                    "organization_name": target_company,
                    "page": 1, "per_page": 10,
                    "person_seniorities": ["director", "vp", "c_suite", "manager"]
                })
                if r.status_code == 200:
                    people = r.json().get("people", [])
                    connections = [{
                        "name": p.get("name", ""),
                        "title": p.get("title", ""),
                        "linkedin_url": p.get("linkedin_url", ""),
                        "email_status": p.get("email_status", "")
                    } for p in people[:10]]
            except Exception:
                pass

    # Generate intro templates via Claude
    system = "You are a networking expert. Generate warm, professional outreach templates."
    prompt = f"""Generate networking outreach for {target_company}.
Connections found: {json.dumps(connections[:5])}
User LinkedIn: {user_linkedin_url}

Return JSON with:
- connections: array of connection objects with name, title, linkedin_url
- intro_templates: array of 3 different intro message templates (short LinkedIn message, email, mutual connection intro)
- approach_strategy: overall strategy for connecting with people at {target_company}

Return ONLY valid JSON."""

    result = await _claude_generate(prompt, system)

    try:
        parsed = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
        if connections and not parsed.get("connections"):
            parsed["connections"] = connections
    except Exception:
        parsed = {
            "connections": connections,
            "intro_templates": [result],
            "approach_strategy": "Research the company and find mutual connections"
        }

    return JSONResponse(parsed)
