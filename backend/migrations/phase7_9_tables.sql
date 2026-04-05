-- SaintSal Labs — Phase 7-9 Migration
-- Run this in Supabase SQL Editor (Dashboard → SQL → New Query)

-- 1. Website Intelligence Crawls
CREATE TABLE IF NOT EXISTS website_crawls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    url TEXT NOT NULL,
    brand_extraction JSONB DEFAULT '{}'::jsonb,
    seo_audit JSONB DEFAULT '{}'::jsonb,
    content_analysis JSONB DEFAULT '{}'::jsonb,
    raw_html TEXT,
    crawl_status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Marketing Campaigns
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    brand_dna_id UUID,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT,
    goal TEXT,
    duration_days INTEGER DEFAULT 14,
    platforms TEXT[] DEFAULT '{}',
    budget TEXT,
    strategy JSONB DEFAULT '{}'::jsonb,
    content_calendar JSONB DEFAULT '[]'::jsonb,
    email_sequence JSONB DEFAULT '[]'::jsonb,
    ad_creatives JSONB DEFAULT '[]'::jsonb,
    kpis JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Generated Assets
CREATE TABLE IF NOT EXISTS generated_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    asset_type TEXT NOT NULL,
    platform TEXT,
    prompt TEXT,
    provider TEXT,
    asset_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Builder Sessions (persistent)
CREATE TABLE IF NOT EXISTS builder_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    prompt TEXT,
    build_type TEXT DEFAULT 'app',
    status TEXT DEFAULT 'running',
    phase INTEGER DEFAULT 1,
    plan_data JSONB DEFAULT '{}'::jsonb,
    design_data JSONB DEFAULT '{}'::jsonb,
    files JSONB DEFAULT '[]'::jsonb,
    deploy_url TEXT,
    deploy_platform TEXT,
    business_dna JSONB DEFAULT '{}'::jsonb,
    website_context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Email Sequences
CREATE TABLE IF NOT EXISTS email_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    brand_dna_id UUID,
    sequence_type TEXT NOT NULL,
    goal TEXT,
    emails JSONB DEFAULT '[]'::jsonb,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Service role policies (allows backend with service_role key full access)
DO $$
BEGIN
  -- Disable RLS or add service_role policies
  ALTER TABLE website_crawls ENABLE ROW LEVEL SECURITY;
  ALTER TABLE marketing_campaigns ENABLE ROW LEVEL SECURITY;
  ALTER TABLE generated_assets ENABLE ROW LEVEL SECURITY;
  ALTER TABLE builder_sessions ENABLE ROW LEVEL SECURITY;
  ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;

  CREATE POLICY "service_role_website_crawls" ON website_crawls FOR ALL TO service_role USING (true) WITH CHECK (true);
  CREATE POLICY "service_role_marketing_campaigns" ON marketing_campaigns FOR ALL TO service_role USING (true) WITH CHECK (true);
  CREATE POLICY "service_role_generated_assets" ON generated_assets FOR ALL TO service_role USING (true) WITH CHECK (true);
  CREATE POLICY "service_role_builder_sessions" ON builder_sessions FOR ALL TO service_role USING (true) WITH CHECK (true);
  CREATE POLICY "service_role_email_sequences" ON email_sequences FOR ALL TO service_role USING (true) WITH CHECK (true);
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'Some policies already exist, continuing...';
END $$;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_website_crawls_user ON website_crawls(user_id);
CREATE INDEX IF NOT EXISTS idx_marketing_campaigns_user ON marketing_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_assets_user ON generated_assets(user_id);
CREATE INDEX IF NOT EXISTS idx_builder_sessions_user ON builder_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_email_sequences_user ON email_sequences(user_id);
