# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform at saintsallabs.com. Adding 32+ new backend endpoints across 8 sections with 88+ API integrations.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML (index.html + app.js + style.css + modules) served via CRA public/
- **Database**: Supabase PostgreSQL + in-memory for new features (Supabase keys pending)
- **Auth**: Supabase Auth (magic link + OAuth)

## What's Been Implemented

### March 31 — Initial Build
- 32+ new backend endpoints across 8 sections
- Career Suite: 4 new tabs (Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper)
- Builder v2 with 5-agent pipeline, agent cards, design preview, terminal
- Creative Studio (Social Studio) with content generation

### April 3 — Session 1: Property Search Fix + Cmd+K
- Fixed Real Estate full property detail view
- Built Cmd+K Command Palette with 30+ items, fuzzy search, keyboard nav

### April 3 — Session 2: Frontend Restoration
- Re-integrated Command Palette into index.html after git pull overwrite

### April 3 — Session 3: Major Feature Buildout
- Business Plan AI (SSE streaming), IP/Patent Intelligence
- 10-Step Formation Wizard (Business Type → Name Check → Entity Advisor → Package → Details → Submit → EIN → Domain & DNS → SSL & Email → Compliance)
- CookinCards Camera Scan (upload/URL, AI identify + grade, sub-grades, portfolio)
- Command Palette "Recently Used" (localStorage)
- Testing: Backend 24/24 (100%), Frontend 100%

### April 3 — Session 4: Full Metering & Tier Gating System
- **Backend**: Complete metering router rewrite with 6 endpoints:
  - `GET /api/metering/tier-info` — 5 tiers (Free/Starter/Pro/Teams/Enterprise) with features, limits, costs
  - `GET /api/metering/dashboard` — Real-time usage, rate limits, action breakdown
  - `POST /api/metering/check-access` — Feature gating (blocks Free from Pro features, rate limiting)
  - `POST /api/metering/log` — Usage tracking with overage calculation
  - `GET /api/metering/usage` — Usage summary
  - `POST /api/metering/set-tier` — Tier management
- **Feature-to-tier mapping**: 35+ features mapped across 5 tiers
- **Action costs**: 22 action types with compute minute costs
- **Rate limiting**: Tier-specific hourly limits (30/100/300/1000/unlimited)
- **Frontend**:
  - Real-time sidebar metering widget (tier badge, credits, progress bar, rate, upgrade link)
  - Dynamic topbar credits display (live-updating)
  - Tier gate modal (lock icon, tier comparison cards, pricing, CTA)
  - Auto-logging on AI actions (Business Plan, Patent Search, Card Scan, Cover Letter)
  - `salCheckAccess()` gate check before AI calls
  - `salLogUsage()` tracking after AI calls
  - 30-second auto-refresh of metering data
- **Testing**: Backend 16/16 (100%), Frontend 100%

## Already Built (No Changes Needed)
- Builder IDE v2: Agent cards, design preview, terminal, 5-agent pipeline
- Creative Studio: Content generation (image, video, audio), social posting
- PropertyAPI distressed deals integration
- Real Estate Intelligence: Search, Portfolio, Deal Analyzer, Ask SAL
- Career Suite: 13 tabs including Cover Letter AI, LinkedIn, Salary, Network

## Prioritized Backlog

### P0 (Blocked — Awaiting User Input)
- Wire Supabase ANON_KEY + SERVICE_KEY for persistent storage

### P1 (Post-Supabase)
- Migrate in-memory stores to Supabase tables
- E2E testing of Builder v2 pipeline (5-agent SSE)
- E2E testing of Launch Pad full 10-step formation flow
- E2E testing of CookinCards scan → grade → portfolio flow

### P2 (Polish)
- Stripe checkout integration for tier upgrades
- Vertical landing states per vertical
- Usage history visualization in account page

### P3 (Future)
- iOS app sync
- ElevenLabs voice agent integration
- Stripe overage billing automation
