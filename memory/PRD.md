# SaintSal Labs Platform — Product Requirements Document

## Original Problem Statement
Build a full-stack business intelligence platform (SaintSal Labs) with 8 intelligence verticals, Builder v2, Career & Business suites, Creative Studio, Launch Pad, CookinCards, and Pricing/Metering. Retain dark/gold aesthetic. FastAPI backend + Vanilla JS frontend.

## Architecture
- **Backend**: FastAPI on port 8001 (`/app/backend/server.py` + `/app/backend/routers/`)
- **Frontend**: Vanilla JS served from `/app/frontend/public/` via React wrapper
- **Database**: Supabase (primary), MongoDB (legacy)
- **Payments**: Stripe (live keys configured)
- **CRM**: Go High Level (connected)
- **APIs**: RentCast, PropertyAPI, Ximilar, GoDaddy, CorpNet, Alpaca, Exa/Tavily

## What's Been Implemented

### Phase 0: Infrastructure (DONE)
- Cloned repo, adapted to Emergent environment
- Modular backend routers for all verticals
- Supabase + GHL + Stripe keys configured

### Phase 1: Frontend Restoration (DONE)
- Cmd+K command palette, Career/Business/Real Estate tabs restored
- CookinCards, LaunchPad, Social Studio UI built

### Phase 2: Metering System (DONE)
- 5-tier pricing, compute levels, feature gating, rate limiting
- Stripe checkout, 65+ integrations marketplace

### Phase 3: Business DNA + Revenue System (DONE — April 3, 2026)
- 5-step DNA onboarding wizard, SAL HQ Dashboard
- Credit limit modals, top-up checkout, GHL env fix

### Phase 4: Career Suite Supabase Migration (DONE — April 4, 2026)
- Full Supabase migration (all Career data off MongoDB)
- Resume/Cover Letter PDF/DOCX export
- DNA autofill, headshot/background upload, job tracker kanban

### Phase 5: Auth Fix (DONE — April 4, 2026)
- Auto-confirm emails on signup AND login via Supabase Admin API
- ryan@cookin.io password reset, topbar Sign In button

### Phase 6: Career Suite P0 Complete (DONE — April 5, 2026)
- **Resume PDF/DOCX downloads**: Save & AI Enhance → PDF/DOCX export buttons appear
- **Cover Letter PDF/DOCX downloads**: Generate → Save & Export → PDF/DOCX buttons
- **Email Signature Copy HTML**: One-click clipboard copy
- **Job Search**: Exa-powered with Monster/Indeed/LinkedIn/Glassdoor domain filters, save to tracker
- **8-Column Kanban**: saved → applied → phone_screen → interview_scheduled → interview_completed → offer_received → job_won → rejected
- **DNA Autofill**: Auto-populates resume from Business DNA on tab open
- **Supabase Storage uploads**: Headshot/background → career-uploads bucket (persistent across deploys)
- **Interview Prep Auto-Generation**: Moving to interview_scheduled triggers prep pack (checklist, common Qs, company-specific AI Qs, power tips)
- **Stage Coaching**: Every pipeline transition triggers SAL guidance popup with tips
- **Builder Session Persistence**: Sessions saved to Supabase (in-memory fallback)
- **Architecture fixes**: Singleton Supabase client, JWT user_id extraction, interview status constraint, dead pymongo/motor removed

## Upcoming — Builder + Creative Studio Enhancement

### Phase 7: Website Intelligence Engine (NEXT)
- POST /api/studio/website-intel: crawl URL → extract brand, colors, fonts, SEO audit, content analysis
- Save to Brand DNA, use as context for all generation

### Phase 8: DNA-Powered Builder
- Inject Business DNA + website crawl into Builder v2 pipeline
- Brand-matched builds (colors, fonts, voice)
- Deploy to Vercel + Cloudflare Pages + Render static

### Phase 9: Marketing Campaign Builder
- Full multi-platform campaign generation
- Content calendar, email sequences, ad creatives
- KPI targets and budget allocation

### Phase 10: Enhanced Creative Studio
- Multi-provider image generation (DALL-E 3, Flux, Runway)
- Email Sequence Builder
- Ad Creative Generator
- Analytics dashboard

### Supabase Tables Needed
- website_crawls, marketing_campaigns, generated_assets, builder_sessions, email_sequences

## P2 — Backlog
- Investment & Lending Portfolios (Alpaca API)
- iOS app sync, ElevenLabs voice agent
- White-label / HACP provisioning
- Smart Memory System (pgvector)
- Rate limiting on AI endpoints (metering integration)
