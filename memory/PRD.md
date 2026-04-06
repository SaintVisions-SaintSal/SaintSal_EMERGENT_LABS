# SaintSal Labs Platform — PRD

## Original Problem Statement
Extend the SaintSal Labs platform with 8 intelligence verticals, Builder v2 (5-agent pipeline), Career & Business Intelligence suites, Creative Studio, Launch Pad (Business Formation), CookinCards, and Pricing/Metering. Retain existing dark/gold aesthetic. Wire Supabase for data persistence. Integrate 3rd party APIs.

## Architecture
- **Backend**: FastAPI (Python) on port 8001, modular routers in `/app/backend/routers/`
- **Frontend**: Vanilla JS monolith (`app.js` ~15k lines) served from `/app/frontend/public/`
- **Database**: Supabase (PostgreSQL, Auth, Storage)
- **Auth**: Supabase Auth with JWT, auto-confirm on login
- **Admin**: Super Admin = ryan@cookin.io (full user/tier/account management)

## What's Been Implemented

### Phase 1-3: Core Platform (DONE)
- Full-stack FastAPI + Vanilla JS with Supabase Auth/Storage
- Career Suite: Resume Builder, Cover Letter, Email Signatures, Job Search (Tavily), Job Tracker Kanban
- Builder v2 with 5-agent pipeline and Business DNA injection
- Real Estate, Medical, Finance, Sports, News, CookinCards verticals
- Voice AI Engine
- Admin Control Panel (Super Admin w/ user management, health checks, order fulfillment)
- Command Palette (Cmd+K)
- Metering/Pricing system

### Phase 4-6: Career Suite Polish (DONE — Apr 5, 2026)
- Resume PDF/DOCX export (working E2E)
- Cover Letter PDF/DOCX export (working E2E)
- Email Signature "Copy HTML" button
- DNA autofill into Resume Builder
- Job Search returning real Tavily results
- Kanban expanded to 14 statuses (wishlist, networking, saved, applied, phone_screen, assessment, interview_scheduled, interview_completed, reference_check, offer_received, negotiating, job_won, rejected, withdrawn)
- Stage coaching tips for all 14 statuses
- Supabase Storage bucket for career uploads (headshots/backgrounds)
- Auth bug fix (auto-confirm emails, password reset for ryan@cookin.io)
- Career profile Supabase persistence

### Phase 7-9: Creative Studio (IN PROGRESS — Apr 6, 2026)
- Backend: `studio_v2.py` router with Website Intel + Campaign Builder endpoints (DONE)
- Supabase tables: website_crawls, marketing_campaigns, generated_assets, builder_sessions, email_sequences (DONE — migrated)
- Kanban status constraint migration (DONE — 14 statuses)
- Frontend UI stubs for Website Intel + Campaign Builder tabs in app.js (DONE)
- Frontend UI logic (fetch + render) needs flesh out

## Database Tables (Supabase)
### Existing
- profiles, resumes, cover_letters, email_signatures, job_applications, job_saved_searches
- conversations, business_dna, compute_usage, marketing_content

### New (Phase 7-9 — Apr 6, 2026)
- website_crawls, marketing_campaigns, generated_assets, builder_sessions, email_sequences

## Key API Endpoints
- `POST /api/auth/login` — Login with auto-confirm
- `GET /api/career/v2/tracker` — 14-status Kanban
- `GET /api/career/v2/resumes/{id}/export/{fmt}` — Resume PDF/DOCX
- `GET /api/career/v2/cover-letters/{id}/export/{fmt}` — Cover Letter PDF/DOCX
- `GET /api/career/jobs/search` — Tavily job search
- `POST /api/studio/website-intel` — Website crawl + brand extraction
- `POST /api/studio/campaigns/generate` — AI campaign generation
- `GET /api/admin/check` — Admin access verification
- `GET /api/admin/users` — User management (Super Admin)

## Upcoming Tasks (Prioritized)
### P0 — Current Focus
- Flesh out Website Intel frontend (render crawl results, brand DNA display)
- Flesh out Campaign Builder frontend (strategy, calendar, email sequence display)
- E2E test Website Intel crawl flow with Tavily

### P1 — Next
- Enhanced image generation pipeline (multi-provider: DALL-E, Flux, Runway)
- Email Sequence Builder API & UI
- Ad Creative Generator API & UI
- Rate limiting on AI enhancement endpoints

### P2 — Future
- Analytics dashboard for campaigns
- A/B testing for ad variants
- GHL integration for email sequences
- Deploy to Cloudflare Pages + custom domains
- Live data feeds + tickers
- Investment & Lending Portfolios
- Smart Memory System (pgvector)
