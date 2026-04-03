"""SaintSal Labs — Career Suite v2 (Supabase-Backed)
Full persistence for profiles, resumes, job tracker, interviews, signatures, cover letters.
PDF/DOCX export. Business DNA autofill. Monster/Indeed job search. SAL coaching.
"""
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import os, json, uuid, httpx, io
from datetime import datetime, timezone

router = APIRouter(prefix="/api/career/v2", tags=["career-v2"])

# ── Supabase client (re-use from server.py) ──
def _sb():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

def _user_id(request: Request):
    """Extract user_id from auth or generate a deterministic UUID for the session."""
    if hasattr(request.state, 'user_id'):
        uid = request.state.user_id
        # If it's already a valid UUID, return it
        try:
            uuid.UUID(str(uid))
            return str(uid)
        except (ValueError, AttributeError):
            pass
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            uuid.UUID(token[:36])
            return token[:36]
        except (ValueError, AttributeError):
            pass
    # Check query param
    qp = request.query_params.get("user_id", "")
    if qp:
        try:
            uuid.UUID(qp)
            return qp
        except (ValueError, AttributeError):
            pass
    # Generate a deterministic UUID from whatever identifier we have
    seed = qp or (auth.split(" ", 1)[1] if auth.startswith("Bearer ") else "anonymous")
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"saintsallabs.{seed}"))

def _now():
    return datetime.now(timezone.utc).isoformat()

# ── 1. CAREER PROFILE (DNA Autofill) ──

@router.get("/profile")
async def get_career_profile(request: Request):
    """Get or create career profile for user."""
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("career_profiles").select("*").eq("user_id", uid).limit(1).execute()
        if r.data:
            row = r.data[0]
            row.pop("id", None)
            return row
        # Create empty profile
        profile = {"user_id": uid, "created_at": _now(), "updated_at": _now()}
        sb.table("career_profiles").insert(profile).execute()
        return profile
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/profile")
async def save_career_profile(request: Request):
    """Save/update career profile."""
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        body["user_id"] = uid
        body["updated_at"] = _now()
        # Remove None values
        body = {k: v for k, v in body.items() if v is not None}
        r = sb.table("career_profiles").upsert(body, on_conflict="user_id").execute()
        return {"success": True, "profile": body}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/profile/autofill-dna")
async def autofill_from_dna(request: Request):
    """Auto-fill career profile from Business DNA."""
    uid = _user_id(request)
    body = await request.json()
    dna = body.get("dna", {})
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        profile = {
            "user_id": uid,
            "full_name": ((dna.get("first_name", "") + " " + dna.get("last_name", "")).strip()) or None,
            "email": dna.get("email") or None,
            "phone": dna.get("phone") or None,
            "headline": dna.get("tagline") or None,
            "summary": dna.get("bio") or None,
            "current_company": dna.get("business_name") or None,
            "industry": dna.get("industry") or None,
            "location": ((dna.get("business_city", "") + ", " + dna.get("business_state", "")).strip(", ")) or None,
            "years_experience": dna.get("years_in_business"),
            "website_url": dna.get("website") or None,
            "updated_at": _now(),
        }
        profile = {k: v for k, v in profile.items() if v is not None}
        sb.table("career_profiles").upsert(profile, on_conflict="user_id").execute()
        return {"success": True, "autofilled": list(profile.keys()), "profile": profile}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── 2. RESUMES (CRUD + SAL Enhancement + Export) ──

@router.get("/resumes")
async def list_resumes(request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("resumes").select("*").eq("user_id", uid).order("updated_at", desc=True).execute()
        data = r.data or []
        for row in data:
            row.pop("id", None)
        return {"resumes": data, "total": len(data)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/resumes")
async def create_resume(request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        resume_id = str(uuid.uuid4())
        resume = {
            "id": resume_id,
            "user_id": uid,
            "resume_name": body.get("resume_name", "Untitled Resume"),
            "template_style": body.get("template_style", "professional"),
            "full_name": body.get("full_name", ""),
            "email": body.get("email", ""),
            "phone": body.get("phone", ""),
            "location": body.get("location", ""),
            "headline": body.get("headline", ""),
            "summary": body.get("summary", ""),
            "skills": body.get("skills", []),
            "certifications": body.get("certifications", []),
            "education": body.get("education", []),
            "work_experience": body.get("work_experience", []),
            "languages": body.get("languages", []),
            "is_primary": body.get("is_primary", False),
            "created_at": _now(),
            "updated_at": _now(),
        }
        sb.table("resumes").insert(resume).execute()
        # Also save work history entries
        for idx, job in enumerate(body.get("work_experience", [])):
            wh = {
                "id": str(uuid.uuid4()),
                "resume_id": resume_id,
                "user_id": uid,
                "company_name": job.get("company", ""),
                "job_title": job.get("title", ""),
                "start_date": job.get("start_date"),
                "end_date": job.get("end_date"),
                "is_current": job.get("is_current", False),
                "description": job.get("description", ""),
                "achievements": job.get("achievements", []),
                "sort_order": idx,
            }
            wh = {k: v for k, v in wh.items() if v is not None}
            try:
                sb.table("resume_work_history").insert(wh).execute()
            except Exception:
                pass
        return {"success": True, "resume_id": resume_id, "resume": resume}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.put("/resumes/{resume_id}")
async def update_resume(resume_id: str, request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        body["updated_at"] = _now()
        body.pop("id", None)
        body.pop("user_id", None)
        sb.table("resumes").update(body).eq("id", resume_id).eq("user_id", uid).execute()
        return {"success": True, "resume_id": resume_id}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/resumes/{resume_id}/enhance")
async def enhance_resume_with_sal(resume_id: str, request: Request):
    """SAL enhances the resume — rewrites summary, bullets, adds keywords."""
    uid = _user_id(request)
    body = await request.json()
    target_role = body.get("target_role", "")
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)

    # Fetch the resume
    try:
        r = sb.table("resumes").select("*").eq("id", resume_id).eq("user_id", uid).limit(1).execute()
        if not r.data:
            return JSONResponse({"error": "Resume not found"}, status_code=404)
        resume = r.data[0]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # Build context for SAL
    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_KEY:
        return JSONResponse({"error": "AI service not configured"}, status_code=500)

    resume_text = f"""
Name: {resume.get('full_name','')}
Headline: {resume.get('headline','')}
Summary: {resume.get('summary','')}
Skills: {', '.join(resume.get('skills',[]))}
Education: {json.dumps(resume.get('education',[]))}
Work Experience: {json.dumps(resume.get('work_experience',[]))}
"""

    system = """You are SaintSal, an elite career intelligence AI. You enhance resumes to be ATS-optimized,
achievement-focused, and tailored for the target role. Use metrics and specific accomplishments.
Return ONLY valid JSON with: enhanced_summary, enhanced_headline, enhanced_skills (array),
enhanced_work_experience (array of {company, title, description, achievements}), ats_score (0-100),
keywords_added (array), improvement_notes (string)."""

    prompt = f"""Enhance this resume{' for the role: ' + target_role if target_role else ''}:

{resume_text}

Make it powerful, specific, and ATS-optimized. Quantify achievements. Add industry keywords."""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-20250514", "max_tokens": 4096,
                      "system": system, "messages": [{"role": "user", "content": prompt}]})
            ai_text = resp.json().get("content", [{}])[0].get("text", "{}")
            enhanced = json.loads(ai_text.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception as e:
        return JSONResponse({"error": f"AI enhancement failed: {str(e)}"}, status_code=500)

    # Update the resume with enhanced data
    update = {
        "sal_enhanced_summary": enhanced.get("enhanced_summary", ""),
        "sal_enhanced_headline": enhanced.get("enhanced_headline", ""),
        "sal_enhanced_skills": enhanced.get("enhanced_skills", []),
        "sal_enhanced_experience": enhanced.get("enhanced_work_experience", []),
        "ats_score": enhanced.get("ats_score", 0),
        "sal_keywords_added": enhanced.get("keywords_added", []),
        "saintssal_enhanced": True,
        "last_enhanced_at": _now(),
        "updated_at": _now(),
    }
    try:
        sb.table("resumes").update(update).eq("id", resume_id).execute()
    except Exception:
        pass

    return {"success": True, "enhanced": enhanced, "resume_id": resume_id}


@router.get("/resumes/{resume_id}/export/{fmt}")
async def export_resume(resume_id: str, fmt: str, request: Request):
    """Export resume as PDF or DOCX."""
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)

    try:
        r = sb.table("resumes").select("*").eq("id", resume_id).eq("user_id", uid).limit(1).execute()
        if not r.data:
            return JSONResponse({"error": "Resume not found"}, status_code=404)
        resume = r.data[0]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    name = resume.get("full_name", "Resume")
    headline = resume.get("sal_enhanced_headline") or resume.get("headline", "")
    summary = resume.get("sal_enhanced_summary") or resume.get("summary", "")
    skills = resume.get("sal_enhanced_skills") or resume.get("skills", [])
    experience = resume.get("sal_enhanced_experience") or resume.get("work_experience", [])
    education = resume.get("education", [])
    email = resume.get("email", "")
    phone = resume.get("phone", "")
    location = resume.get("location", "")
    filename = f"{name.replace(' ', '_')}_Resume"

    if fmt == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.colors import HexColor

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.6*inch, bottomMargin=0.5*inch,
                                leftMargin=0.7*inch, rightMargin=0.7*inch)
        styles = getSampleStyleSheet()
        gold = HexColor("#D4AF37")
        dark = HexColor("#1a1a1a")

        name_style = ParagraphStyle("Name", parent=styles["Title"], fontSize=22, textColor=dark,
                                     spaceAfter=4, fontName="Helvetica-Bold")
        headline_style = ParagraphStyle("Headline", parent=styles["Normal"], fontSize=11,
                                        textColor=HexColor("#555555"), spaceAfter=6)
        contact_style = ParagraphStyle("Contact", parent=styles["Normal"], fontSize=9,
                                       textColor=HexColor("#666666"), spaceAfter=12)
        section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=12,
                                       textColor=gold, fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=14)
        body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10,
                                    textColor=dark, spaceAfter=4, leading=14)
        bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=12,
                                      bulletIndent=0, spaceAfter=2)

        story = []
        story.append(Paragraph(name, name_style))
        if headline:
            story.append(Paragraph(headline, headline_style))
        contact_parts = [p for p in [email, phone, location] if p]
        if contact_parts:
            story.append(Paragraph(" | ".join(contact_parts), contact_style))
        story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=10))

        if summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
            story.append(Paragraph(summary, body_style))

        if experience:
            story.append(Paragraph("EXPERIENCE", section_style))
            for job in experience:
                title = job.get("title", job.get("job_title", ""))
                company = job.get("company", job.get("company_name", ""))
                story.append(Paragraph(f"<b>{title}</b> — {company}", body_style))
                desc = job.get("description", "")
                if desc:
                    story.append(Paragraph(desc, body_style))
                for ach in job.get("achievements", []):
                    story.append(Paragraph(f"• {ach}", bullet_style))
                story.append(Spacer(1, 4))

        if education:
            story.append(Paragraph("EDUCATION", section_style))
            for edu in education:
                if isinstance(edu, dict):
                    story.append(Paragraph(f"<b>{edu.get('degree','')}</b> — {edu.get('school','')}", body_style))
                else:
                    story.append(Paragraph(str(edu), body_style))

        if skills:
            story.append(Paragraph("SKILLS", section_style))
            story.append(Paragraph(", ".join(skills), body_style))

        # SaintSal branding
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc"), spaceAfter=6))
        sal_style = ParagraphStyle("SAL", parent=styles["Normal"], fontSize=7,
                                   textColor=HexColor("#999999"), alignment=1)
        story.append(Paragraph("Enhanced by SaintSal Labs | saintsallabs.com", sal_style))

        doc.build(story)
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/pdf",
                                 headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'})

    elif fmt == "docx":
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        style = doc.styles["Normal"]
        style.font.size = Pt(10)
        style.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)

        # Name
        p = doc.add_heading(name, level=0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)

        if headline:
            p = doc.add_paragraph(headline)
            p.runs[0].font.size = Pt(11)
            p.runs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)

        contact_parts = [x for x in [email, phone, location] if x]
        if contact_parts:
            p = doc.add_paragraph(" | ".join(contact_parts))
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        if summary:
            doc.add_heading("PROFESSIONAL SUMMARY", level=2)
            doc.add_paragraph(summary)

        if experience:
            doc.add_heading("EXPERIENCE", level=2)
            for job in experience:
                title = job.get("title", job.get("job_title", ""))
                company = job.get("company", job.get("company_name", ""))
                p = doc.add_paragraph()
                run = p.add_run(f"{title} — {company}")
                run.bold = True
                desc = job.get("description", "")
                if desc:
                    doc.add_paragraph(desc)
                for ach in job.get("achievements", []):
                    doc.add_paragraph(f"• {ach}")

        if education:
            doc.add_heading("EDUCATION", level=2)
            for edu in education:
                if isinstance(edu, dict):
                    doc.add_paragraph(f"{edu.get('degree','')} — {edu.get('school','')}")
                else:
                    doc.add_paragraph(str(edu))

        if skills:
            doc.add_heading("SKILLS", level=2)
            doc.add_paragraph(", ".join(skills))

        # SaintSal branding
        p = doc.add_paragraph("\nEnhanced by SaintSal Labs | saintsallabs.com")
        p.runs[0].font.size = Pt(7)
        p.runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return StreamingResponse(buf,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}.docx"'})

    return JSONResponse({"error": "Format must be 'pdf' or 'docx'"}, status_code=400)


# ── 3. JOB APPLICATIONS (Tracker → Supabase) ──

@router.get("/tracker")
async def get_job_tracker(request: Request):
    """Get all tracked jobs as Kanban board."""
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("job_applications").select("*").eq("user_id", uid).order("updated_at", desc=True).execute()
        jobs = r.data or []
        for j in jobs:
            j.pop("id", None)
        kanban = {
            "wishlist": [j for j in jobs if j.get("status") == "wishlist"],
            "applied": [j for j in jobs if j.get("status") == "applied"],
            "phone_screen": [j for j in jobs if j.get("status") == "phone_screen"],
            "interview": [j for j in jobs if j.get("status") == "interview"],
            "offer": [j for j in jobs if j.get("status") == "offer"],
            "accepted": [j for j in jobs if j.get("status") == "accepted"],
            "rejected": [j for j in jobs if j.get("status") == "rejected"],
        }
        return {"kanban": kanban, "total": len(jobs), "jobs": jobs}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/tracker")
async def add_to_tracker(request: Request):
    """Add a job to the tracker."""
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        app_id = str(uuid.uuid4())
        job = {
            "id": app_id,
            "user_id": uid,
            "job_title": body.get("job_title", ""),
            "company_name": body.get("company", body.get("company_name", "")),
            "job_url": body.get("url", body.get("job_url", "")),
            "location": body.get("location", ""),
            "salary_min": body.get("salary_min"),
            "salary_max": body.get("salary_max"),
            "job_type": body.get("job_type", "full_time"),
            "remote_type": body.get("remote_type", "onsite"),
            "status": body.get("status", "wishlist"),
            "notes": body.get("notes", ""),
            "source": body.get("source", "manual"),
            "applied_date": body.get("applied_date"),
            "created_at": _now(),
            "updated_at": _now(),
        }
        job = {k: v for k, v in job.items() if v is not None}
        sb.table("job_applications").insert(job).execute()
        return {"success": True, "job_id": app_id, "job": job}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.put("/tracker/{job_id}")
async def update_tracker_job(job_id: str, request: Request):
    """Update a tracked job (status, notes, salary, etc.)."""
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        body["updated_at"] = _now()
        body.pop("id", None)
        body.pop("user_id", None)
        # Auto-set applied_date when status changes to applied
        if body.get("status") == "applied" and not body.get("applied_date"):
            body["applied_date"] = _now()
        sb.table("job_applications").update(body).eq("id", job_id).eq("user_id", uid).execute()
        return {"success": True, "job_id": job_id}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.delete("/tracker/{job_id}")
async def delete_tracker_job(job_id: str, request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        sb.table("job_applications").delete().eq("id", job_id).eq("user_id", uid).execute()
        return {"success": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── 4. INTERVIEWS (Track + SAL Coaching) ──

@router.get("/interviews/{job_id}")
async def get_interviews(job_id: str, request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("interviews").select("*").eq("job_application_id", job_id).eq("user_id", uid).order("interview_date", desc=False).execute()
        data = r.data or []
        for row in data:
            row.pop("id", None)
        return {"interviews": data, "total": len(data)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/interviews")
async def add_interview(request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        interview = {
            "id": str(uuid.uuid4()),
            "user_id": uid,
            "job_application_id": body.get("job_id", body.get("job_application_id", "")),
            "interview_type": body.get("interview_type", "phone_screen"),
            "interview_date": body.get("interview_date"),
            "interviewer_name": body.get("interviewer_name", ""),
            "interviewer_title": body.get("interviewer_title", ""),
            "notes": body.get("notes", ""),
            "status": body.get("status", "scheduled"),
            "created_at": _now(),
        }
        interview = {k: v for k, v in interview.items() if v is not None}
        sb.table("interviews").insert(interview).execute()
        # Update job application status
        try:
            sb.table("job_applications").update({"status": "interview", "updated_at": _now()}).eq("id", interview["job_application_id"]).execute()
        except Exception:
            pass
        return {"success": True, "interview": interview}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/interviews/{interview_id}/coach")
async def interview_coaching(interview_id: str, request: Request):
    """SAL generates interview prep and coaching for a specific interview."""
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)

    # Get the interview and job details
    try:
        ir = sb.table("interviews").select("*").eq("id", interview_id).eq("user_id", uid).limit(1).execute()
        interview = ir.data[0] if ir.data else {}
        job_id = interview.get("job_application_id", "")
        jr = sb.table("job_applications").select("*").eq("id", job_id).limit(1).execute()
        job = jr.data[0] if jr.data else {}
    except Exception:
        interview = {}
        job = {}

    company = job.get("company_name", body.get("company", ""))
    role = job.get("job_title", body.get("role", ""))
    interview_type = interview.get("interview_type", body.get("interview_type", ""))
    stage = body.get("stage", "prep")  # prep, during, followup

    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_KEY:
        return JSONResponse({"error": "AI service not configured"}, status_code=500)

    prompts = {
        "prep": f"""Prepare me for a {interview_type} interview at {company} for the {role} position.
Give me: 1) Company research summary, 2) 10 likely questions with STAR-method answers,
3) Questions I should ask them, 4) What to wear/bring, 5) Red flags to watch for.
Return as JSON with keys: company_research, likely_questions (array of {{question, answer_framework}}),
questions_to_ask (array), preparation_checklist (array), red_flags (array), confidence_tips (array).""",
        "during": f"""I'm in a {interview_type} interview right now at {company} for {role}.
They just asked: {body.get('question', 'a technical question')}
Help me structure a strong answer using the STAR method.
Return JSON: suggested_answer, key_points (array), follow_up_question_to_ask, body_language_tip.""",
        "followup": f"""My {interview_type} interview at {company} for {role} just ended.
Help me write a follow-up. Include: thank you email, LinkedIn connection request,
and what to do if I don't hear back in 1 week.
Return JSON: thank_you_email, linkedin_message, follow_up_timeline (array of {{day, action}}),
next_steps (array).""",
    }

    system = "You are SaintSal, an elite career coach. You give specific, actionable interview guidance. Return ONLY valid JSON."
    prompt = prompts.get(stage, prompts["prep"])

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-20250514", "max_tokens": 4096,
                      "system": system, "messages": [{"role": "user", "content": prompt}]})
            ai_text = resp.json().get("content", [{}])[0].get("text", "{}")
            coaching = json.loads(ai_text.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError:
        coaching = {"raw_response": ai_text}
    except Exception as e:
        return JSONResponse({"error": f"Coaching failed: {str(e)}"}, status_code=500)

    # Save prep notes to interview
    try:
        sb.table("interviews").update({
            "sal_prep_notes": json.dumps(coaching),
            "updated_at": _now()
        }).eq("id", interview_id).execute()
    except Exception:
        pass

    return {"success": True, "stage": stage, "coaching": coaching}


# ── 5. EMAIL SIGNATURES (Supabase) ──

@router.get("/signatures")
async def list_signatures(request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("email_signatures").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
        data = r.data or []
        for row in data:
            row.pop("id", None)
        return {"signatures": data, "total": len(data)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/signatures")
async def save_signature(request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        sig = {
            "id": str(uuid.uuid4()),
            "user_id": uid,
            "signature_name": body.get("signature_name", "My Signature"),
            "template_style": body.get("template_style", "professional"),
            "full_name": body.get("full_name", ""),
            "title": body.get("title", ""),
            "company": body.get("company", ""),
            "email": body.get("email", ""),
            "phone": body.get("phone", ""),
            "website": body.get("website", ""),
            "linkedin_url": body.get("linkedin_url", ""),
            "logo_url": body.get("logo_url", ""),
            "banner_url": body.get("banner_url", ""),
            "color_primary": body.get("color_primary", "#D4AF37"),
            "color_secondary": body.get("color_secondary", "#1a1a1a"),
            "html_content": body.get("html_content", ""),
            "is_primary": body.get("is_primary", False),
            "created_at": _now(),
        }
        sb.table("email_signatures").insert(sig).execute()
        return {"success": True, "signature": sig}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── 6. COVER LETTERS (Persist to Supabase) ──

@router.post("/cover-letters")
async def save_cover_letter(request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        cl = {
            "id": str(uuid.uuid4()),
            "user_id": uid,
            "job_application_id": body.get("job_id"),
            "resume_id": body.get("resume_id"),
            "cover_letter_name": body.get("name", "Cover Letter"),
            "content": body.get("content", ""),
            "style": body.get("style", "direct"),
            "target_company": body.get("target_company", ""),
            "target_role": body.get("target_role", ""),
            "saintssal_generated": body.get("saintssal_generated", True),
            "created_at": _now(),
        }
        cl = {k: v for k, v in cl.items() if v is not None}
        sb.table("cover_letters").insert(cl).execute()
        return {"success": True, "cover_letter": cl}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/cover-letters")
async def list_cover_letters(request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("cover_letters").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
        data = r.data or []
        for row in data:
            row.pop("id", None)
        return {"cover_letters": data, "total": len(data)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── 7. STAGE-SPECIFIC COACHING (Start → Job Won) ──

@router.post("/coach/stage-guidance")
async def stage_guidance(request: Request):
    """SAL provides stage-specific guidance based on job tracker status."""
    body = await request.json()
    status = body.get("status", "wishlist")
    company = body.get("company", "")
    role = body.get("role", "")

    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_KEY:
        return JSONResponse({"error": "AI not configured"}, status_code=500)

    guidance_prompts = {
        "wishlist": f"I'm interested in the {role} position at {company}. What should I research before applying? Give me a pre-application checklist and company research template.",
        "applied": f"I just applied for {role} at {company}. Write me a follow-up email template, tell me when to send it, and what to do while waiting.",
        "phone_screen": f"I have a phone screen for {role} at {company}. Give me prep: what they'll ask, how to answer, questions to ask them, and phone interview tips.",
        "interview": f"I have an in-person/video interview for {role} at {company}. Give me STAR-method answers for 5 likely questions, body language tips, and a day-of checklist.",
        "offer": f"I received an offer for {role} at {company}. Help me negotiate: counter-offer script, benefits to negotiate beyond salary, and decision framework.",
        "accepted": f"I accepted the {role} position at {company}! Give me a 30-60-90 day plan, first-week tips, and how to make a strong impression.",
        "rejected": f"I was rejected for {role} at {company}. Help me write a graceful response, what to learn from this, and how to keep the door open for future opportunities.",
    }

    prompt = guidance_prompts.get(status, guidance_prompts["wishlist"])
    system = "You are SaintSal, an elite career coach. Be specific, actionable, and encouraging. Return JSON with: guidance (string), action_items (array), templates (array of {type, content}), timeline (array of {day, action}), motivation (string)."

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-20250514", "max_tokens": 4096,
                      "system": system, "messages": [{"role": "user", "content": prompt}]})
            ai_text = resp.json().get("content", [{}])[0].get("text", "{}")
            coaching = json.loads(ai_text.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError:
        coaching = {"guidance": ai_text, "action_items": [], "templates": [], "motivation": "Keep pushing forward!"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"success": True, "status": status, "coaching": coaching}


# ── 8. SAVED JOB SEARCHES ──

@router.post("/saved-searches")
async def save_job_search(request: Request):
    uid = _user_id(request)
    body = await request.json()
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        search = {
            "id": str(uuid.uuid4()),
            "user_id": uid,
            "search_name": body.get("search_name", ""),
            "query": body.get("query", ""),
            "location": body.get("location", ""),
            "job_type": body.get("job_type", ""),
            "remote_only": body.get("remote_only", False),
            "salary_min": body.get("salary_min"),
            "salary_max": body.get("salary_max"),
            "alert_enabled": body.get("alert_enabled", False),
            "created_at": _now(),
        }
        search = {k: v for k, v in search.items() if v is not None}
        sb.table("job_saved_searches").insert(search).execute()
        return {"success": True, "search": search}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/saved-searches")
async def list_saved_searches(request: Request):
    uid = _user_id(request)
    sb = _sb()
    if not sb:
        return JSONResponse({"error": "Supabase not configured"}, status_code=500)
    try:
        r = sb.table("job_saved_searches").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
        data = r.data or []
        for row in data:
            row.pop("id", None)
        return {"saved_searches": data, "total": len(data)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
