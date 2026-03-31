"""SaintSal Labs — Business Intelligence Endpoints (Section 3.5-3.6)"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import os
import json
import asyncio

router = APIRouter(prefix="/api/business", tags=["business"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def _claude_generate(prompt: str, system: str = "", model: str = "claude-sonnet-4-20250514"):
    if not ANTHROPIC_API_KEY:
        return "AI unavailable"
    async with httpx.AsyncClient(timeout=90) as http:
        try:
            r = await http.post("https://api.anthropic.com/v1/messages", json={
                "model": model, "max_tokens": 4096,
                "system": system, "messages": [{"role": "user", "content": prompt}]
            }, headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                        "content-type": "application/json"})
            return r.json().get("content", [{}])[0].get("text", "Error")
        except Exception as e:
            return f"Error: {e}"


async def _exa_search(query: str, num_results: int = 5):
    if not EXA_API_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as http:
        try:
            r = await http.post("https://api.exa.ai/search", json={
                "query": query, "numResults": num_results, "useAutoprompt": True
            }, headers={"Authorization": f"Bearer {EXA_API_KEY}"})
            return r.json().get("results", [])
        except Exception:
            return []


async def _tavily_search(query: str, max_results: int = 5):
    if not TAVILY_API_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as http:
        try:
            r = await http.post("https://api.tavily.com/search", json={
                "api_key": TAVILY_API_KEY, "query": query,
                "search_depth": "advanced", "max_results": max_results
            })
            return r.json().get("results", [])
        except Exception:
            return []


# 3.5 — Business Plan AI (SSE streaming)
@router.post("/plan")
async def business_plan(request: Request):
    """Generate a comprehensive business plan with SSE streaming."""
    body = await request.json()
    idea = body.get("idea_description", "")
    target_market = body.get("target_market", "")
    stage = body.get("stage", "pre-revenue")

    if not idea:
        return JSONResponse({"error": "idea_description is required"}, status_code=400)

    async def generate_plan():
        sections = [
            ("executive_summary", f"Write an executive summary for: {idea}. Target market: {target_market}. Stage: {stage}."),
            ("market_analysis", f"Write a detailed market analysis for: {idea}. Include TAM/SAM/SOM, growth trends, and market dynamics. Target: {target_market}."),
            ("competitive_landscape", f"Analyze the competitive landscape for: {idea}. Include direct/indirect competitors, positioning, and competitive advantages."),
            ("product_service", f"Describe the product/service for: {idea}. Include features, value proposition, and differentiation."),
            ("business_model", f"Define the business model for: {idea}. Include revenue streams, pricing strategy, and unit economics."),
            ("go_to_market", f"Create a go-to-market strategy for: {idea}. Include channels, customer acquisition, and launch plan."),
            ("financial_projections", f"Create 3-5 year financial projections for: {idea}. Include P&L, cash flow, break-even analysis. Stage: {stage}."),
            ("team_slide", f"Describe the ideal team structure for: {idea}. Include key roles, hiring priorities, and organizational design."),
            ("funding_ask", f"Create a funding ask section for: {idea}. Stage: {stage}. Include use of funds, milestones, and investment terms."),
        ]

        system = """You are a top-tier business strategy consultant who creates investor-grade business plans.
Use specific data, real market numbers, and professional formatting. Be thorough and actionable."""

        # Do market research first
        research = await _tavily_search(f"{idea} market size competition {target_market}", max_results=5)
        research_context = "\n".join([f"- {r.get('title', '')}: {r.get('content', '')[:200]}" for r in research])

        for section_name, prompt in sections:
            yield f"data: {json.dumps({'event': 'section_start', 'section': section_name})}\n\n"

            full_prompt = f"""{prompt}

MARKET RESEARCH CONTEXT:
{research_context}

Write this section in professional business plan format with headers, bullet points, and specific data.
Be thorough — this is for investor presentation."""

            content = await _claude_generate(full_prompt, system)
            yield f"data: {json.dumps({'event': 'section_complete', 'section': section_name, 'content': content})}\n\n"

        yield f"data: {json.dumps({'event': 'complete', 'sections_generated': len(sections)})}\n\n"

    return StreamingResponse(generate_plan(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# 3.6 — IP / Patent Intelligence
@router.post("/patent-search")
async def patent_search(request: Request):
    """Search for prior art and patent intelligence."""
    body = await request.json()
    tech_description = body.get("technology_description", "")
    competitors = body.get("competitors", [])

    if not tech_description:
        return JSONResponse({"error": "technology_description is required"}, status_code=400)

    # Search USPTO and Google Patents via Exa
    patent_results = await _exa_search(f"patent {tech_description} USPTO Google Patents prior art", num_results=8)
    competitor_patents = []
    for comp in competitors[:3]:
        comp_results = await _exa_search(f"{comp} patents {tech_description}", num_results=3)
        competitor_patents.extend(comp_results)

    system = """You are a patent attorney and IP strategist. Analyze technology descriptions
for patentability, prior art conflicts, and licensing opportunities. Be specific and cite sources."""

    prompt = f"""Analyze patent landscape for this technology:

TECHNOLOGY: {tech_description}
COMPETITORS: {', '.join(competitors)}

PATENT SEARCH RESULTS:
{json.dumps([{'title': r.get('title', ''), 'url': r.get('url', '')} for r in patent_results], indent=2)}

COMPETITOR PATENTS:
{json.dumps([{'title': r.get('title', ''), 'url': r.get('url', '')} for r in competitor_patents], indent=2)}

Return JSON with:
- prior_art: array of relevant prior art references with title, url, relevance_score
- fto_analysis: freedom-to-operate assessment text
- valuation_range: estimated IP value range
- licensing_opportunities: array of potential licensing targets

Return ONLY valid JSON."""

    result = await _claude_generate(prompt, system)

    try:
        parsed = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception:
        parsed = {
            "prior_art": [{"title": r.get("title", ""), "url": r.get("url", "")} for r in patent_results],
            "fto_analysis": result,
            "valuation_range": {"low": "Unable to determine", "high": "Unable to determine"},
            "licensing_opportunities": []
        }

    return JSONResponse(parsed)
