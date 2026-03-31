# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform at saintsallabs.com. Adding 32+ new backend endpoints across 8 sections with 88+ API integrations.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML (index.html + app.js + style.css + modules) served via CRA public/
- **Database**: Supabase PostgreSQL (euxrlpuegeiggedqbkiv.supabase.co) + in-memory for new features
- **Auth**: Supabase Auth (magic link + OAuth)
- **APIs**: 88+ integrations (Anthropic, xAI, Azure OpenAI, Google, Perplexity, Exa, Tavily, etc.)

## User Personas
1. **Pro User** ($97/mo) — Uses AI chat, Builder, Career Suite, Creative Studio
2. **Teams User** ($297/mo) — Multi-seat, SAINT Leads, advanced features
3. **Enterprise** ($497/mo) — API access, white-label, unlimited compute
4. **Free User** — SAL Mini only, 100 compute minutes

## What's Been Implemented (March 31, 2026)

### Backend — 32+ New Endpoints
1. **Verticals** (Section 1.4): `/api/verticals/trending` — Tavily + Exa search for vertical-specific trending content
2. **Career Suite** (Section 3.1-3.4):
   - `/api/career/cover-letter` — AI cover letter generation (Claude Sonnet)
   - `/api/career/linkedin-optimize` — LinkedIn profile optimization
   - `/api/career/salary-negotiate` — Market data + negotiation scripts (Claude + Exa)
   - `/api/career/network-map` — Apollo + Claude for network mapping
3. **Business Intelligence** (Section 3.5-3.6):
   - `/api/business/plan` — SSE streaming business plan generation
   - `/api/business/patent-search` — IP/prior art search via Exa
4. **Builder v2** (Section 2):
   - `/api/builder/agent/v2` — 5-agent SSE pipeline
   - `/api/builder/agent/v2/approve` — Design approval gate
   - `/api/builder/iterate` — Diff-based code editing
   - `/api/builder/deploy` — Multi-target deploy (Vercel/Render)
   - `/api/builder/models` — Tier-gated model list
   - `/api/builder/stitch` — Design proxy
5. **Creative Studio** (Section 4):
   - `/api/creative/generate` — Multi-type content generation
   - `/api/creative/social/post` — GHL social posting
   - `/api/creative/calendar` — 30-day content calendar
   - `/api/creative/calendar/batch-generate` — Batch content generation
   - `/api/creative/brand-profile` — Brand profile management
6. **Launch Pad** (Section 5):
   - `/api/launchpad/name-check` — Name + domain + trademark check
   - `/api/launchpad/entity-advisor` — AI entity recommendation
   - `/api/launchpad/domain/purchase` — GoDaddy domain purchase
   - `/api/launchpad/entity/form` — FileForms entity formation
   - `/api/launchpad/entity/ein` — EIN filing
   - `/api/launchpad/dns/configure` — Auto DNS setup
   - `/api/launchpad/ssl/provision` — SSL provisioning
   - `/api/launchpad/compliance/setup` — Compliance calendar
7. **CookinCards** (Section 6):
   - `/api/cards/grade` — Full PSA-style grading (Ximilar)
   - `/api/cards/quick-grade` — Quick condition check
   - `/api/cards/centering` — Centering-only check
   - `/api/cards/slab-read` — OCR slab label reading
   - `/api/cards/price` — Price lookup
   - `/api/cards/collection` — Collection management (GET)
   - `/api/cards/collection/add` — Add to collection (POST)
   - `/api/cards/market/trending` — Trending cards
8. **Metering** (Section 7):
   - `/api/metering/log` — Compute usage logging
   - `/api/metering/usage` — Usage reporting

### Frontend — New Views & Tabs
1. **Career Suite**: 4 new tabs — Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper
2. **Business Center**: 2 new tabs — Business Plan AI, IP/Patent Intelligence
3. All new views match existing dark + gold aesthetic perfectly

## Test Results
- Backend: 94.1% pass rate (16/17 endpoints working)
- Frontend: 85% pass rate (Career Suite all tabs working)

## Prioritized Backlog

### P0 (Critical — Next Session)
- Wire Supabase ANON_KEY + SERVICE_KEY for persistent storage
- Migrate in-memory stores to Supabase tables (builder_sessions, card_collections, metering)

### P1 (High — Soon)
- Creative Studio frontend views (content gen, image gen, social posting, calendar)
- Builder IDE v2 frontend upgrade (agent cards, design preview, terminal)
- Vertical landing states per vertical
- CookinCards camera scan UI integration

### P2 (Medium)
- Launch Pad full 10-step wizard UI
- Social Studio enhancements
- Content calendar batch generation UI
- Brand profile management UI

### P3 (Low/Future)
- iOS app sync (React Native/Expo)
- ElevenLabs voice agent integration for builder
- Stripe overage billing integration
- Real-time WebSocket notifications
- Admin fulfillment dashboard enhancements
