# SaintSal Labs Platform v2 — PRD

## Original Problem Statement
Full vertical buildout of SaintSal Labs Platform. Existing vanilla JS + FastAPI + Supabase platform at saintsallabs.com. Adding 32+ new backend endpoints across 8 sections with 88+ API integrations.

## Architecture
- **Backend**: Python/FastAPI (server.py + /routers/) on port 8001
- **Frontend**: Vanilla JS + HTML (index.html + app.js + style.css + modules) served via CRA public/
- **Database**: Supabase PostgreSQL + in-memory for new features (keys pending)
- **Auth**: Supabase Auth (magic link + OAuth)

## Implemented Features

### Core Platform
- 32+ backend endpoints across 8 vertical sections
- Cmd+K Command Palette with 30+ items, fuzzy search, "Recently Used" tracking
- Dark/gold aesthetic throughout

### Career Suite (13 tabs)
- Overview, Job Search, Tracker, Resume, Cover Letter AI, LinkedIn Optimizer, Salary Negotiator, Network Mapper, Cards, Signatures, Coach, Interview, Backgrounds

### Real Estate Intelligence
- Search with full property detail (Legal, Tax, Ownership, Comps), Portfolio, Deal Analyzer, Ask SAL with address pre-fill

### Business Center (9 tabs)
- Overview, Formation (10-step wizard), Domains, Resume, Signatures, Business Plan AI (SSE), IP/Patent Intelligence, Meetings, Analytics

### CookinCards
- Price search, Camera Scan (upload/URL, AI ID + grade with sub-grades), Deals, Portfolio, Rare Candy

### Builder IDE v2
- 5-agent pipeline, agent cards, design preview, terminal

### Creative Studio / Social Studio
- Content generation (image, video, audio), social publishing, calendar

### GHL Bridge
- SAAS Configurator, Smart Sync (Contacts/Pipelines/Tasks/Reputation), Lead Bridge, Bridge Controls

### Metering & Tier Gating (Production Spec v3)
**5 Subscription Tiers:**
| Tier | Price | Compute | Cap | Stripe Product |
|------|-------|---------|-----|----------------|
| Free | $0/mo | 100 min | Hard | prod_U3jCx2VJbNeXvU |
| Starter | $27/mo | 500 min | Hard | prod_U3jCGSzn4WqzV3 |
| Pro | $97/mo | 2,000 min | Soft | prod_U3jC7k9rF5enMh |
| Teams | $297/mo | 10,000 min | Soft | prod_U3jCtHY6kyCJdC |
| Enterprise | $497/mo | Unlimited | None | prod_U3jCLNosf5FA6j |

**4 Compute Levels:**
| Level | Rate | Min Tier |
|-------|------|----------|
| SAL Mini | $0.05/min | Free |
| SAL Pro | $0.25/min | Starter |
| SAL Max | $0.75/min | Pro |
| SAL Max Fast | $1.00/min | Teams |

**Features:**
- Real-time sidebar widget (tier badge, credits, progress bar, rate limit)
- Dynamic topbar credits display
- Tier gate modal with Starter/Pro/Teams pricing comparison
- Auto-logging on AI actions (salCheckAccess + salLogUsage)
- Hard cap (Free/Starter → 429) vs Soft cap (Pro/Teams → overage billing)
- 65+ integrations catalog across 16 categories
- 42 action cost types with wall-clock compute pricing
- 8 formation products with Stripe price IDs

## Prioritized Backlog

### P0 (Blocked)
- Supabase ANON_KEY + SERVICE_KEY for persistent storage

### P1
- Stripe Checkout integration (tier upgrades + metered billing)
- Settings page with Integrations marketplace UI
- Migrate in-memory stores to Supabase
- E2E testing of Builder v2, Launch Pad, CookinCards flows

### P2
- Usage history visualization in account page
- Stripe webhooks for automated tier changes
- Advanced property comparables

### P3
- iOS app sync
- ElevenLabs voice agent integration
- Stripe overage billing automation
- White-label / HACP licensing (Enterprise)
