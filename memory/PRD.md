# SaintSal Labs Platform — PRD

## Original Problem Statement
Extend the SaintSal Labs platform with 8 intelligence verticals, Builder v2, Career & Business Intelligence suites, Creative Studio, Launch Pad, CookinCards, and Pricing/Metering. Deep GHL integration for automation. Vercel deployment pipeline. DNA-everywhere philosophy.

## Architecture
- **Backend**: FastAPI (Python) on port 8001, modular routers in `/app/backend/routers/`
- **Frontend**: Vanilla JS monolith (`app.js` ~15k lines) served from `/app/frontend/public/`
- **Database**: Supabase (PostgreSQL, Auth, Storage)
- **Auth**: Supabase Auth with JWT, auto-confirm on login
- **Admin**: Super Admin = ryan@cookin.io (full user/tier/account management)
- **APIs**: Tavily (search), RentCast (real estate), Ximilar (card grading), Google Maps/Vision, Pokemon TCG API, Anthropic/OpenAI/xAI (LLMs), Stripe, Resend, GHL

## What's Been Implemented

### Core Platform (DONE)
- FastAPI + Vanilla JS + Supabase Auth/Storage
- 8 Intelligence Verticals (Real Estate, Medical, Finance, Sports, News, etc.)
- Builder v2 with 5-agent pipeline + DNA injection
- Voice AI Engine, Admin Control Panel, Command Palette (Cmd+K)
- Metering/Pricing system

### Career Suite (DONE — Apr 5-6, 2026)
- Resume Builder with PDF/DOCX export
- Cover Letter with PDF/DOCX export
- Email Signatures with Copy HTML
- Job Search returning real Tavily results
- **14-Status Kanban** (wishlist, networking, saved, applied, phone_screen, assessment, interview_scheduled, interview_completed, reference_check, offer_received, negotiating, job_won, rejected, withdrawn)
- Stage coaching tips for all 14 statuses
- DNA autofill, Supabase Storage for uploads

### Creative Studio Phase 7-9 (DONE — Apr 6, 2026)
- `studio_v2.py` router: Website Intel + Campaign Builder endpoints
- Supabase tables: website_crawls, marketing_campaigns, generated_assets, builder_sessions, email_sequences
- **Website Intel → Business DNA auto-populate** (crawl extracts brand, saves to business_dna table)

### CookinCards Enhancement (DONE — Apr 6, 2026)
- **Real card search** via Pokemon TCG API (images, set names, rarity, prices)
- **Real pricing** via eBay (Tavily) + TCGPlayer market prices
- **Live trending** market data from Tavily (not hardcoded)
- **PSA/BGS/SGC cert verification** via web lookup
- **Google Cloud Vision** integration for enhanced recognition
- **Celebration animations**: Common (gold sparkle), Rare >$50 (confetti + value), Grail >$500 (fireworks + GRAIL ALERT), Gem Mint PSA 10 (rainbow holographic)
- **Supabase-backed collections** (pending migration)
- **Portfolio value snapshots** over time (pending migration)

### Real Estate Enhancement (DONE — Apr 6, 2026)
- **Google Maps integration** with dark theme + gold markers
- **Grid/Map view toggle** for search results
- **Property info windows** on map markers
- **Full property detail view** (Back button, valuation, rent estimate, mini map, property details grid)
- Listings include latitude/longitude for mapping

## Pending Supabase Migrations (User Must Run)
1. `card_collections` + `card_portfolio_snapshots` — `/app/backend/migrations/cookincards_tables.sql`

## Key API Endpoints
- Career: `/api/career/v2/tracker` (14 statuses), `/api/career/v2/resumes/{id}/export/{fmt}`, `/api/career/jobs/search`
- Cards: `/api/cards/search`, `/api/cards/price`, `/api/cards/market/trending`, `/api/cards/verify-cert`, `/api/cards/collection`
- Studio: `/api/studio/website-intel`, `/api/studio/campaigns/generate`
- Real Estate: `/api/realestate/listings/sale`, `/api/realestate/value`, `/api/realestate/rent`
- Admin: `/api/admin/check`, `/api/admin/users`

## Upcoming Tasks (Prioritized)
### P0 — Next
- GHL integration (contacts sync, workflow triggers on signup/billing)
- Builder deploys to Vercel (already partially wired)
- Resend welcome email verification
- DNS configuration for Builder custom domains

### P1
- Campaign Builder frontend flesh-out (strategy, calendar, email sequence display)
- Email Sequence Builder API & UI
- Ad Creative Generator
- Enhanced image generation pipeline (multi-provider)

### P2 — Future
- Analytics dashboard for campaigns
- A/B testing for ad variants
- GHL subaccount provisioning for new users
- Deploy to Cloudflare Pages + custom domains
- Live data feeds + tickers
- Investment & Lending Portfolios
- Smart Memory System (pgvector)
- Rate limiting on AI endpoints
