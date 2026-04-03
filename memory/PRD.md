# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform. 8 intelligence verticals, Builder v2, Career & Business suites, Creative Studio, Launch Pad, CookinCards, Pricing/Metering.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML served via CRA public/
- **Database**: Supabase PostgreSQL + in-memory (keys pending)

## Implemented Features

### Metering & Tier Gating (Production Spec v3)
- 5 tiers: Free $0 / Starter $27 / Pro $97 / Teams $297 / Enterprise $497 with real Stripe IDs
- 4 compute levels: SAL Mini $0.05 / Pro $0.25 / Max $0.75 / Max Fast $1.00
- 65+ integrations catalog, 42 action cost types, hard/soft cap logic
- Real-time sidebar widget + topbar credits + tier gate modal

### Social/Creative Studio (8 tabs — FIXED Apr 3)
- Content Engine (platform select, AI generation, templates)
- Image Gen (DALL-E 3, Google Stitch, Grok Imagine, Replicate SDXL)
- Video Studio (Quick Clips + Template Engine + Premium Cinematic)
- Social Calendar (calendar view, history, bulk schedule)
- Ad Creative (campaign brief, audience targeting)
- Brand Profiles (create/import/AI generate)
- Marketing Auto (GHL integration, review management, 4 workflow automations)
- Plans & Usage (tier display, compute meter, feature access)
- **Fixed scroll**: .view.active { overflow-y: auto }
- **7 new endpoints**: brand/generate-ai, image/save-library, marketing/ghl/connect, reviews, review-response, workflows, workflows/toggle

### Business Center (9 tabs)
- Overview, Formation (10-step wizard), Domains, Resume, Signatures
- Business Plan AI (SSE streaming), IP/Patent Intelligence
- Meetings, Analytics

### Career Suite (13 tabs)
- Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper + 9 more

### CookinCards (5 tabs)
- Price, Camera Scan (AI ID + grade), Deals, Portfolio, Rare

### Real Estate Intelligence (4 tabs)
- Search (full property detail), Portfolio, Deal Analyzer, Ask SAL

### Builder IDE v2
- 5-agent pipeline, agent cards, design preview, terminal

### Command Palette (Cmd+K)
- 30+ items, fuzzy search, Recently Used tracking

### GHL Bridge
- SAAS Configurator, Smart Sync, Lead Bridge, Bridge Controls

## Prioritized Backlog

### P0 (Blocked)
- Supabase ANON_KEY + SERVICE_KEY for persistent storage
- GHL API key refresh (currently 401)

### P1
- Stripe Checkout integration for tier upgrades
- Settings page with Integrations marketplace UI
- E2E testing of Builder v2, Launch Pad, CookinCards flows

### P2
- Usage history visualization
- Stripe webhooks for automated tier changes

### P3
- iOS app sync, ElevenLabs voice, white-label/HACP
