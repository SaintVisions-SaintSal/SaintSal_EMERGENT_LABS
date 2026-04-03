# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform at saintsallabs.com. Adding 32+ new backend endpoints across 8 sections with 88+ API integrations.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML (index.html + app.js + style.css + modules) served via CRA public/
- **Database**: Supabase PostgreSQL + in-memory for new features
- **Auth**: Supabase Auth (magic link + OAuth)

## What's Been Implemented

### March 31, 2026 — Initial Build
- 32+ new backend endpoints across 8 sections
- Career Suite: 4 new tabs (Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper)
- Business Center: 2 new tabs (Business Plan AI, IP/Patent Intelligence)
- Builder v2, Creative Studio, Launch Pad, CookinCards, Metering endpoints

### April 3, 2026 — Property Search Fix + Cmd+K
- **Fixed Real Estate full property detail view**: Valuation, rental estimate, 1% rule, legal description, zoning, assessor ID, subdivision, owner info, 3-year tax assessments, property taxes, sale history, 10 comparable sales, comparable rentals
- **Built Cmd+K Command Palette**: 30+ navigation items, fuzzy search, keyboard nav, categories
- **Quick Actions topbar button** for discoverability

### April 3, 2026 (Session 2) — Re-applied Frontend After Git Pull
- **Re-integrated Command Palette into index.html**: Added CSS link, JS script tag, and Cmd+K topbar button
- **Verified Career Suite tabs intact**: Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper all working with full API integration
- **Verified Real Estate view intact**: 4-tab nav, property search, distressed deals, Ask SAL with address pre-fill
- **Verified Business Center intact**: Formation wizard, Domain search, Resume builder, Email signatures, Meeting notes, Analytics
- **Testing**: Backend 22/22 (100%), Frontend 100% pass rate
- **Bug fix**: Exposed toggleCommandPalette globally for topbar button click

## Prioritized Backlog

### P0 (Critical)
- Wire Supabase ANON_KEY + SERVICE_KEY for persistent storage (keys needed from user)
- Migrate in-memory stores to Supabase tables

### P1 (High)
- Add Business Plan AI + Patent/IP Search tabs to Business Center frontend
- Creative Studio frontend views
- Builder IDE v2 frontend upgrade (agent cards, design preview, terminal)
- CookinCards camera scan UI
- LaunchPad CSS visibility fix

### P2 (Medium)
- Launch Pad full 10-step wizard UI
- Vertical landing states per vertical
- PropertyAPI integration for deeper data
- E2E testing of Builder v2 pipeline (5-agent SSE)
- E2E testing of Launch Pad name check → formation flow
- E2E testing of CookinCards scan → grade flow
- Metering and tier gating verification

### P3 (Low/Future)
- iOS app sync
- ElevenLabs voice agent integration
- Stripe overage billing
