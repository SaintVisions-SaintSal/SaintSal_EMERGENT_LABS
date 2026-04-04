# SaintSal Labs Platform — Product Requirements Document

## Original Problem Statement
Build a full-stack business intelligence platform (SaintSal Labs) with 8 intelligence verticals, Builder v2, Career & Business suites, Creative Studio, Launch Pad, CookinCards, and Pricing/Metering. Retain dark/gold aesthetic. FastAPI backend + Vanilla JS frontend.

## Architecture
- **Backend**: FastAPI on port 8001 (`/app/backend/server.py` + `/app/backend/routers/`)
- **Frontend**: Vanilla JS served from `/app/frontend/public/` via React wrapper
- **Database**: Supabase (connected), MongoDB (available)
- **Payments**: Stripe (live keys configured)
- **CRM**: Go High Level (connected)
- **APIs**: RentCast, PropertyAPI, Ximilar, GoDaddy, CorpNet, Alpaca

## What's Been Implemented

### Phase 0: Infrastructure (DONE)
- Cloned repo, adapted to Emergent environment
- Modular backend routers for all verticals
- Supabase + GHL + Stripe keys configured and connected

### Phase 1: Frontend Restoration (DONE)
- Restored Cmd+K command palette
- Restored Career Suite tabs (Cover Letter, LinkedIn, Salary, Network)
- Restored Real Estate property detail view
- Restored Business Plan AI & Patent tabs
- Built CookinCards camera scan UI
- Built LaunchPad 10-step wizard
- Fixed Social Studio scrolling bug

### Phase 2: Metering System (DONE)
- 5-tier pricing ($0/$27/$97/$297/$497)
- 4 compute levels (Mini/Pro/Max/Max Fast)
- Feature gating per tier
- Rate limiting per tier
- Stripe checkout session creation
- 65+ integrations marketplace catalog

### Phase 3: Business DNA + Revenue System (DONE — April 3, 2026)
- **5-Step Business DNA Onboarding Wizard**
  - Step 1: Personal Info (name, email, phone)
  - Step 2: Business Type (individual/LLC/Corp/nonprofit, EIN, state)
  - Step 3: Business Details (industry, revenue, employees, address)
  - Step 4: Goals & Interests (10 categories, multi-select)
  - Step 5: Tagline + Bio
  - Saves to backend `/api/user/business-dna` and localStorage
  - Data injected into AI chat system prompt for personalization
- **SAL HQ Dashboard (Command Center)**
  - Profile card with avatar, name, company, tagline, entity badge
  - Quick Actions row (8 shortcuts)
  - Business Overview (GHL contacts, pipelines, tier, billing)
  - Recent Activity feed
  - Intelligence Pillars based on DNA interests
  - Lab Assets (saved builds)
- **Credit Limit Modal System (3 types)**
  - Credits Exhausted: top-up grid ($5/$10/$25/$50/$60/$100/$250), Stripe checkout
  - Daily Limit Reached: upgrade CTA
  - Model Upgrade Required: tier-specific upgrade pricing
- **Credit Top-Up Checkout**: `/api/billing/credit-topup` -> Stripe one-time payment
- **GHL Environment Fix**: Both `GHL_API_KEY` and `GHL_PRIVATE_TOKEN` configured

### Phase 4: Career Suite Supabase Migration + P0 Enhancements (DONE — April 4, 2026)
- **Full Supabase Migration**: Moved all Career Suite data from in-memory/Mongo to Supabase

## Pending / Upcoming Tasks
- **Resume PDF/DOCX Export**: Save resume to Supabase, then export via `/api/career/v2/resumes/{id}/export/pdf|docx`
- **Business DNA Autofill**: Resume builder auto-populates from DNA profile (name, email, phone, company, skills)
- **Cover Letter PDF/DOCX Export**: Save generated cover letter, then export via `/api/career/v2/cover-letters/{id}/export/pdf|docx`
- **Email Signature Copy HTML**: One-click clipboard copy of full HTML signature
- **Headshot & Background Upload**: File upload endpoints for user photos (`/api/career/v2/upload/headshot|background`)
- **Job Tracker Kanban**: Supabase-backed with Saved/Applied/Phone Screen/Rejected columns
- **Job Search**: Wired to `/api/career/jobs/search` with save-to-tracker functionality
- **Tone Mapping**: Frontend styles (direct/storytelling/technical) mapped to valid Supabase check constraint values

### Phase 5: Auth Fix (DONE — April 4, 2026)
- **Root cause**: Supabase email confirmation was blocking users — confirmation emails never arrived via Supabase's default SMTP
- **Fix**: Auto-confirm all users on signup AND login via Supabase Admin API (`email_confirm: true`)
- **Signup flow**: Creates user → auto-confirms email → auto-signs-in → returns session token immediately
- **Login flow**: If "email not confirmed" error, auto-confirms via admin API then retries sign-in
- **ryan@cookin.io**: Password reset to `SaintSal2024!` via admin API, email confirmed
- **Topbar Sign In button**: Added prominent gold "Sign In" button in topbar (replaces with avatar after login)
- **Welcome email**: Sent via Resend after signup

### P1 — Next Up
- **Live Data Feeds + Tickers** (Step 4): Personalized data feeds in intelligence verticals based on Business DNA
- Wire Supabase billing tables (billing_profiles, credit_transactions, usage_logs)
- Full metering middleware (pre-flight/post-flight on every AI call)
- Credit balance deduction in real-time
- Stripe webhook handler for subscription lifecycle + credit purchases
- GHL contact sync on billing events (tier tags, LTV)
- E2E testing of Builder v2 pipeline, Launch Pad wizard, CookinCards

### P2 — Future
- Investment & Lending Portfolios (Step 5, Alpaca API)
- Deal Analyzer Engine (Fix & Flip + Rental/DSCR calculators)
- Lending Pipeline (CookinCapital)
- Saved Searches with alerts
- Cross-platform sync (saintsallabs.com <-> saintsal.ai)

### P3 — Backlog
- iOS app sync
- ElevenLabs voice agent
- White-label / HACP provisioning
- Smart Memory System (pgvector semantic search)
- Custom agent creation for Teams/Enterprise
