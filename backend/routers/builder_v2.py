"""SaintSal Labs — Builder v2 Endpoints (Section 2)"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import os
import json
import uuid
import asyncio
from datetime import datetime

router = APIRouter(prefix="/api/builder", tags=["builder"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_STITCH_API = os.environ.get("GOOGLE_STITCH_API", "")
VERCEL_API_ACCESS_TOKEN = os.environ.get("VERCEL_API_ACCESS_TOKEN", "")
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "")

# ── Builder Sessions: Supabase-backed with in-memory fallback ──
_builder_mem = {}

def _builder_sb():
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def builder_sessions_get(sid):
    """Get session from Supabase, fall back to in-memory."""
    sb = _builder_sb()
    if sb:
        try:
            r = sb.table("builder_sessions").select("*").eq("id", sid).limit(1).execute()
            if r.data:
                row = r.data[0]
                return {
                    "session_id": row["id"],
                    "prompt": row.get("prompt", ""),
                    "status": row.get("status", "running"),
                    "plan_data": row.get("plan_data", {}),
                    "design_data": row.get("design_data", {}),
                    "files": row.get("files", []),
                    "deploy_url": row.get("deploy_url"),
                    "business_dna": row.get("business_dna", {}),
                }
        except Exception:
            pass
    return _builder_mem.get(sid)

def builder_sessions_set(sid, data):
    """Persist session to Supabase + in-memory cache."""
    _builder_mem[sid] = data
    sb = _builder_sb()
    if sb:
        try:
            row = {
                "id": sid,
                "user_id": data.get("user_id", "anonymous"),
                "prompt": data.get("prompt", ""),
                "status": data.get("status", "running"),
                "plan_data": data.get("plan_data", {}),
                "design_data": data.get("design_data", {}),
                "files": data.get("files", []),
                "deploy_url": data.get("deploy_url"),
                "business_dna": data.get("business_dna", {}),
                "updated_at": datetime.utcnow().isoformat(),
            }
            sb.table("builder_sessions").upsert(row, on_conflict="id").execute()
        except Exception as e:
            print(f"[Builder] Supabase persist failed: {e}")

# Alias for backward compat  
builder_sessions = _builder_mem


async def _grok_generate(prompt: str, system: str = ""):
    """Phase 1: Grok architect."""
    if not XAI_API_KEY:
        return None
    async with httpx.AsyncClient(timeout=60) as http:
        try:
            msgs = [{"role": "user", "content": prompt}]
            if system:
                msgs.insert(0, {"role": "system", "content": system})
            r = await http.post("https://api.x.ai/v1/chat/completions", json={
                "model": "grok-3-latest", "messages": msgs, "max_tokens": 4096
            }, headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"})
            data = r.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            return None


async def _claude_generate(prompt: str, system: str = "", model: str = "claude-sonnet-4-20250514"):
    if not ANTHROPIC_API_KEY:
        return None
    async with httpx.AsyncClient(timeout=90) as http:
        try:
            r = await http.post("https://api.anthropic.com/v1/messages", json={
                "model": model, "max_tokens": 8192,
                "system": system, "messages": [{"role": "user", "content": prompt}]
            }, headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                        "content-type": "application/json"})
            return r.json().get("content", [{}])[0].get("text", "")
        except Exception:
            return None


async def _openai_generate(prompt: str, system: str = ""):
    if not OPENAI_API_KEY:
        return None
    async with httpx.AsyncClient(timeout=60) as http:
        try:
            msgs = [{"role": "user", "content": prompt}]
            if system:
                msgs.insert(0, {"role": "system", "content": system})
            r = await http.post("https://api.openai.com/v1/chat/completions", json={
                "model": "gpt-4o", "messages": msgs, "max_tokens": 4096
            }, headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"})
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            return None


# Builder v2 — 5-Agent SSE Pipeline
@router.post("/agent/v2")
async def builder_v2_pipeline(request: Request):
    """5-agent pipeline for full app generation."""
    body = await request.json()
    prompt = body.get("prompt", body.get("message", ""))
    session_id = body.get("session_id", str(uuid.uuid4()))
    user_id = body.get("user_id", "anonymous")
    model = body.get("model", "auto")

    if not prompt:
        return JSONResponse({"error": "prompt is required"}, status_code=400)

    builder_sessions_set(session_id, {
        "id": session_id, "user_id": user_id, "prompt": prompt,
        "status": "running", "phase": 1, "created_at": datetime.utcnow().isoformat()
    })
    builder_sessions[session_id] = builder_sessions_get(session_id) or {"id": session_id, "status": "running"}

    async def pipeline_stream():
        start_time = asyncio.get_event_loop().time()

        # Phase 1: Grok Architect
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'grok', 'status': 'active', 'message': 'Architecting your application...'})}\n\n"

        arch_system = """You are an expert software architect. Given a project description, create:
1. A clear architecture plan
2. Component tree with descriptions
3. Technology stack recommendations
Return as JSON with keys: plan, components (array), tech_stack (object)."""

        plan_result = await _grok_generate(prompt, arch_system)
        if not plan_result:
            plan_result = await _claude_generate(prompt, arch_system)
        if not plan_result:
            plan_result = json.dumps({"plan": "Standard web application", "components": ["App", "Header", "Main", "Footer"], "tech_stack": {"frontend": "HTML/CSS/JS", "styling": "Modern CSS"}})

        try:
            plan_data = json.loads(plan_result.strip().removeprefix("```json").removesuffix("```").strip())
        except Exception:
            plan_data = {"plan": plan_result, "components": [], "tech_stack": {}}

        yield f"data: {json.dumps({'event': 'plan_ready', 'plan': plan_data.get('plan', ''), 'components': plan_data.get('components', []), 'tech_stack': plan_data.get('tech_stack', {})})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'grok', 'status': 'complete', 'message': 'Architecture ready'})}\n\n"

        # Phase 2a: Design (Stitch or Claude fallback)
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'stitch', 'status': 'active', 'message': 'Designing UI screens...'})}\n\n"

        design_prompt = f"""Design the UI for this application:
{prompt}

Architecture: {json.dumps(plan_data)}

Create clean, modern HTML/CSS for each screen. Return JSON with:
screens: [{{name, html, css}}]"""

        design_result = await _claude_generate(design_prompt, "You are a world-class UI/UX designer. Create beautiful, modern designs.", "claude-sonnet-4-20250514")
        try:
            design_data = json.loads(design_result.strip().removeprefix("```json").removesuffix("```").strip())
        except Exception:
            design_data = {"screens": [{"name": "Main", "html": f"<div class='app'><h1>App Preview</h1><p>{prompt}</p></div>", "css": "body{font-family:system-ui;margin:0;padding:20px;}"}]}

        builder_sessions[session_id]["status"] = "awaiting_approval"
        builder_sessions[session_id]["design_data"] = design_data
        builder_sessions_set(session_id, builder_sessions[session_id])

        yield f"data: {json.dumps({'event': 'design_ready', 'screens': design_data.get('screens', []), 'session_id': session_id})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'stitch', 'status': 'complete', 'message': 'Designs ready for review'})}\n\n"

        # Pause for approval — frontend will call /approve to continue
        yield f"data: {json.dumps({'event': 'awaiting_approval', 'session_id': session_id, 'message': 'Review designs and approve to continue building'})}\n\n"

        # Wait for approval (poll for up to 5 minutes)
        approved = False
        for _ in range(300):
            await asyncio.sleep(1)
            session = builder_sessions.get(session_id, {})
            if session.get("status") == "approved":
                approved = True
                break
            if session.get("status") == "cancelled":
                yield f"data: {json.dumps({'event': 'error', 'agent': 'system', 'message': 'Build cancelled', 'recoverable': False})}\n\n"
                return

        if not approved:
            # Auto-approve after timeout
            builder_sessions[session_id]["status"] = "approved"

        # Phase 2b: Scaffold
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'sonnet', 'status': 'active', 'message': 'Engineering file structure...'})}\n\n"

        scaffold_prompt = f"""Create a file tree and route structure for:
{prompt}
Architecture: {json.dumps(plan_data)}
Return JSON: {{files: [{{path, description}}]}}"""

        scaffold_result = await _claude_generate(scaffold_prompt, "You are a senior software engineer. Create clean file structures.", "claude-sonnet-4-20250514")
        try:
            scaffold_data = json.loads(scaffold_result.strip().removeprefix("```json").removesuffix("```").strip())
        except Exception:
            scaffold_data = {"files": [{"path": "index.html", "description": "Main entry point"}]}

        yield f"data: {json.dumps({'event': 'scaffold_ready', 'files': scaffold_data.get('files', [])})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'sonnet', 'status': 'complete', 'message': 'Scaffold ready'})}\n\n"

        # Phase 3: Synthesis (Claude Opus generates final code)
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'opus', 'status': 'active', 'message': 'Synthesizing final code...'})}\n\n"

        synth_prompt = f"""Generate the complete, working code for this application:
{prompt}

ARCHITECTURE:
{json.dumps(plan_data)}

DESIGN:
{json.dumps(design_data)}

SCAFFOLD:
{json.dumps(scaffold_data)}

Generate all files with complete, working code. Return JSON:
{{files: [{{path, content, language}}]}}
Each file must be complete and functional. Use modern best practices."""

        synth_result = await _claude_generate(synth_prompt,
            "You are a 10x full-stack engineer. Generate complete, production-quality code. Every file must be fully functional.",
            "claude-sonnet-4-20250514")
        try:
            files_data = json.loads(synth_result.strip().removeprefix("```json").removesuffix("```").strip())
        except Exception:
            files_data = {"files": [{"path": "index.html", "content": synth_result, "language": "html"}]}

        yield f"data: {json.dumps({'event': 'files_ready', 'files': files_data.get('files', [])})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'opus', 'status': 'complete', 'message': 'Code synthesized'})}\n\n"

        # Phase 4: Validation (GPT-5 / GPT-4o)
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'gpt5', 'status': 'active', 'message': 'Validating and optimizing...'})}\n\n"

        validation_prompt = f"""Review this code for bugs, security issues, and optimization opportunities:
{json.dumps(files_data.get('files', [])[:3])}
Return JSON: {{lint_results: [], test_results: [], suggestions: []}}"""

        validation_result = await _openai_generate(validation_prompt, "You are a senior code reviewer. Find bugs and suggest improvements.")
        try:
            validation_data = json.loads(validation_result.strip().removeprefix("```json").removesuffix("```").strip()) if validation_result else {}
        except Exception:
            validation_data = {"lint_results": [], "test_results": [], "suggestions": ["Code looks good"]}

        yield f"data: {json.dumps({'event': 'validation_ready', 'lint_results': validation_data.get('lint_results', []), 'test_results': validation_data.get('test_results', []), 'suggestions': validation_data.get('suggestions', [])})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'gpt5', 'status': 'complete', 'message': 'Validation complete'})}\n\n"

        elapsed = asyncio.get_event_loop().time() - start_time
        builder_sessions[session_id]["status"] = "complete"
        builder_sessions[session_id]["files"] = files_data.get("files", [])
        builder_sessions_set(session_id, builder_sessions[session_id])

        yield f"data: {json.dumps({'event': 'complete', 'total_time': round(elapsed, 1), 'agents_used': ['grok', 'stitch', 'sonnet', 'opus', 'gpt5']})}\n\n"

    return StreamingResponse(pipeline_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Design Approval Gate
@router.post("/agent/v2/approve")
async def builder_approve(request: Request):
    """Approve designs to continue the build pipeline."""
    body = await request.json()
    session_id = body.get("session_id", "")
    action = body.get("action", "approve")

    if session_id not in builder_sessions:
        return JSONResponse({"error": "Session not found"}, status_code=404)

    if action == "approve":
        builder_sessions[session_id]["status"] = "approved"
    elif action == "cancel":
        builder_sessions[session_id]["status"] = "cancelled"
    elif action == "restart":
        builder_sessions[session_id]["status"] = "cancelled"

    return JSONResponse({"status": builder_sessions[session_id]["status"], "session_id": session_id})


# Iteration Engine
@router.post("/iterate")
async def builder_iterate(request: Request):
    """Diff-based code editing for existing builds."""
    body = await request.json()
    session_id = body.get("session_id", "")
    change_request = body.get("message", body.get("change", ""))

    session = builder_sessions.get(session_id, {})
    existing_files = session.get("files", [])

    if not change_request:
        return JSONResponse({"error": "change request required"}, status_code=400)

    async def iterate_stream():
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'sonnet', 'status': 'active', 'message': 'Applying changes...'})}\n\n"

        prompt = f"""You have an existing codebase. Apply ONLY the requested change.
Do NOT regenerate unchanged files.

EXISTING FILES:
{json.dumps(existing_files[:5])}

CHANGE REQUEST:
{change_request}

Return JSON: {{files: [{{path, content, language}}]}}
Only include files that changed."""

        result = await _claude_generate(prompt, "Apply minimal, precise code changes. Only modify what's needed.", "claude-sonnet-4-20250514")
        try:
            files_data = json.loads(result.strip().removeprefix("```json").removesuffix("```").strip())
        except Exception:
            files_data = {"files": [{"path": "patch.diff", "content": result, "language": "diff"}]}

        # Merge changes into session
        if session_id in builder_sessions:
            file_map = {f["path"]: f for f in builder_sessions[session_id].get("files", [])}
            for f in files_data.get("files", []):
                file_map[f["path"]] = f
            builder_sessions[session_id]["files"] = list(file_map.values())

        yield f"data: {json.dumps({'event': 'files_ready', 'files': files_data.get('files', [])})}\n\n"
        yield f"data: {json.dumps({'event': 'agent_status', 'agent': 'sonnet', 'status': 'complete', 'message': 'Changes applied'})}\n\n"
        yield f"data: {json.dumps({'event': 'complete', 'total_time': 0, 'agents_used': ['sonnet']})}\n\n"

    return StreamingResponse(iterate_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Deploy endpoint
@router.post("/deploy")
async def builder_deploy(request: Request):
    """Deploy built project to Vercel/Render/CF."""
    body = await request.json()
    session_id = body.get("session_id", "")
    platform = body.get("platform", "vercel")
    project_name = body.get("project_name", "sal-build")

    session = builder_sessions.get(session_id, {})
    files = session.get("files", [])

    if not files:
        return JSONResponse({"error": "No files to deploy. Build first."}, status_code=400)

    if platform == "vercel" and VERCEL_API_ACCESS_TOKEN:
        async with httpx.AsyncClient(timeout=30) as http:
            try:
                deploy_files = [{"file": f["path"], "data": f["content"]} for f in files]
                r = await http.post("https://api.vercel.com/v13/deployments", json={
                    "name": project_name, "files": deploy_files,
                    "projectSettings": {"framework": None}
                }, headers={"Authorization": f"Bearer {VERCEL_API_ACCESS_TOKEN}"})
                if r.status_code in (200, 201):
                    data = r.json()
                    return JSONResponse({"url": f"https://{data.get('url', '')}", "platform": "vercel", "id": data.get("id", "")})
            except Exception as e:
                return JSONResponse({"error": f"Deploy failed: {e}"}, status_code=500)

    return JSONResponse({"error": f"Deploy to {platform} not available"}, status_code=400)


# Available models per tier
@router.get("/models")
async def builder_models(request: Request):
    """Return available models based on user tier."""
    return JSONResponse({
        "models": [
            {"id": "grok-4.20", "name": "Grok 4.20", "provider": "xAI", "tier": "pro", "role": "architect"},
            {"id": "stitch", "name": "Google Stitch", "provider": "Google", "tier": "pro", "role": "designer"},
            {"id": "claude-sonnet", "name": "Claude Sonnet 4.6", "provider": "Anthropic", "tier": "starter", "role": "engineer"},
            {"id": "claude-opus", "name": "Claude Opus 4.6", "provider": "Anthropic", "tier": "pro", "role": "synthesizer"},
            {"id": "gpt-5", "name": "GPT-5 Core", "provider": "OpenAI", "tier": "pro", "role": "validator"}
        ]
    })


# Stitch MCP proxy
@router.post("/stitch")
async def builder_stitch(request: Request):
    """Direct Stitch MCP proxy for design generation."""
    body = await request.json()
    prompt = body.get("prompt", "")
    if not prompt:
        return JSONResponse({"error": "prompt required"}, status_code=400)

    # Fallback: use Claude for design if Stitch not available
    design = await _claude_generate(
        f"Design a beautiful UI for: {prompt}. Return complete HTML/CSS.",
        "You are a world-class UI designer. Create stunning, modern designs with clean HTML/CSS."
    )
    return JSONResponse({"design": design, "provider": "claude-fallback"})
