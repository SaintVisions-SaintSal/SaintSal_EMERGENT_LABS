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

## Prioritized Backlog

### P0 (Critical)
- Wire Supabase ANON_KEY + SERVICE_KEY for persistent storage
- Migrate in-memory stores to Supabase tables

### P1 (High)
- Creative Studio frontend views
- Builder IDE v2 frontend upgrade (agent cards, design preview, terminal)
- CookinCards camera scan UI
- Wire "Ask SAL" and "Run Deal Analysis" buttons in property detail

### P2 (Medium)
- Launch Pad full 10-step wizard UI
- Vertical landing states per vertical
- PropertyAPI integration for deeper data

### P3 (Low/Future)
- iOS app sync
- ElevenLabs voice agent integration
- Stripe overage billing
