# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform at saintsallabs.com. Adding 32+ new backend endpoints across 8 sections with 88+ API integrations.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML (index.html + app.js + style.css + modules) served via CRA public/
- **Database**: Supabase PostgreSQL + in-memory for new features (Supabase keys pending)
- **Auth**: Supabase Auth (magic link + OAuth)

## What's Been Implemented

### March 31, 2026 — Initial Build
- 32+ new backend endpoints across 8 sections
- Career Suite: 4 new tabs (Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper)
- Builder v2 with 5-agent pipeline, agent cards, design preview, terminal
- Creative Studio (Social Studio) with content generation
- Metering & Tier Gating system

### April 3, 2026 — Session 1: Property Search Fix + Cmd+K
- Fixed Real Estate full property detail view with Legal, Tax, Ownership, Comps data
- Built Cmd+K Command Palette with 30+ navigation items, fuzzy search, keyboard nav

### April 3, 2026 — Session 2: Frontend Restoration
- Re-integrated Command Palette into index.html
- Verified Career Suite, Real Estate, Business Center all intact after git pull overwrite

### April 3, 2026 — Session 3: Major Feature Buildout
- **Business Plan AI tab** in Business Center — Full SSE streaming with AI-generated investor-grade plans (Exec Summary, Market Analysis, Competitive Landscape, Financial Projections)
- **IP / Patent Intelligence tab** in Business Center — FTO analysis, prior art search, IP valuation, licensing opportunities
- **10-Step Formation Wizard** — Business Type → Name Check → Entity Advisor → Package → Details → Submit → EIN → Domain & DNS → SSL & Email → Compliance Calendar
- **CookinCards Camera Scan** — Upload photo or paste URL to AI-identify and grade trading cards. Sub-grades for centering, corners, edges, surface. Add to portfolio.
- **Command Palette "Recently Used"** — localStorage-based tracking of last 5 used items, shown at top on palette open
- **LaunchPad CSS fix** — Added overflow-y:auto for proper scrolling
- **Duplicate endpoint cleanup** — Removed duplicate /api/cards/scan from server.py (router version takes priority)
- **Testing**: Backend 24/24 (100%), Frontend 100%

## Already Built (No Changes Needed)
- Builder IDE v2: Agent cards, design preview, terminal, 5-agent pipeline ✅
- Creative Studio: Content generation (image, video, audio), social posting ✅
- PropertyAPI distressed deals integration ✅
- Metering & Tier Gating ✅
- Real Estate Intelligence: Search, Portfolio, Deal Analyzer, Ask SAL ✅
- Career Suite: 13 tabs including Cover Letter AI, LinkedIn, Salary, Network ✅

## Prioritized Backlog

### P0 (Blocked — Awaiting User Input)
- Wire Supabase ANON_KEY + SERVICE_KEY for persistent storage (keys empty in .env)

### P1 (Post-Supabase)
- Migrate in-memory stores to Supabase tables (card_collections, builder_sessions, metering)
- E2E testing of Builder v2 pipeline (5-agent SSE)
- E2E testing of Launch Pad full 10-step formation flow
- E2E testing of CookinCards scan → grade → portfolio flow

### P2 (Polish)
- Vertical landing states per vertical
- Advanced property detail comparables
- Real-time metering dashboard widget

### P3 (Future)
- iOS app sync
- ElevenLabs voice agent integration
- Stripe overage billing
