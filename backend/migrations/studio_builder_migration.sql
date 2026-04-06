-- ============================================================
-- SaintSal Labs — Builder + Creative Studio Enhancement Migration
-- Run in: Supabase Dashboard -> SQL Editor -> New Query -> Paste -> Run
-- ============================================================

-- 1. WEBSITE CRAWLS
CREATE TABLE IF NOT EXISTS website_crawls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    brand_extraction JSONB DEFAULT '{}'::jsonb,
    seo_audit JSONB DEFAULT '{}'::jsonb,
    content_analysis JSONB DEFAULT '{}'::jsonb,
    marketing_opportunities JSONB DEFAULT '[]'::jsonb,
    competitor_suggestions TEXT[] DEFAULT '{}',
    crawl_status TEXT DEFAULT 'completed'
        CHECK (crawl_status IN ('pending', 'crawling', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_website_crawls_user ON website_crawls(user_id);

-- 2. MARKETING CAMPAIGNS
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    brand_dna_id UUID,
    website_crawl_id UUID REFERENCES website_crawls(id) ON DELETE SET NULL,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT CHECK (campaign_type IN (
        'product_launch', 'awareness', 'lead_gen', 'event',
        'seasonal', 'promotion', 'content', 'retargeting'
    )),
    goal TEXT,
    duration_days INTEGER DEFAULT 14,
    platforms TEXT[] DEFAULT '{}',
    budget TEXT,
    strategy JSONB DEFAULT '{}'::jsonb,
    content_calendar JSONB DEFAULT '[]'::jsonb,
    email_sequence JSONB DEFAULT '[]'::jsonb,
    ad_creatives JSONB DEFAULT '[]'::jsonb,
    kpis JSONB DEFAULT '{}'::jsonb,
    actual_results JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_user ON marketing_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON marketing_campaigns(user_id, status);

-- 3. GENERATED ASSETS
CREATE TABLE IF NOT EXISTS generated_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    asset_type TEXT NOT NULL CHECK (asset_type IN (
        'image', 'video', 'document', 'email',
        'ad_creative', 'social_post', 'landing_page', 'carousel'
    )),
    platform TEXT,
    prompt TEXT,
    provider TEXT,
    asset_url TEXT,
    thumbnail_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_user ON generated_assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_campaign ON generated_assets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON generated_assets(user_id, asset_type);

-- 4. BUILDER SESSIONS
CREATE TABLE IF NOT EXISTS builder_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT,
    build_type TEXT DEFAULT 'app'
        CHECK (build_type IN ('app', 'landing_page', 'dashboard', 'marketing', 'widget', 'api')),
    status TEXT DEFAULT 'running'
        CHECK (status IN ('running', 'awaiting_approval', 'approved', 'complete', 'cancelled', 'failed')),
    phase INTEGER DEFAULT 1,
    plan_data JSONB DEFAULT '{}'::jsonb,
    design_data JSONB DEFAULT '{}'::jsonb,
    files JSONB DEFAULT '[]'::jsonb,
    deploy_url TEXT,
    deploy_platform TEXT,
    business_dna JSONB DEFAULT '{}'::jsonb,
    website_context JSONB DEFAULT '{}'::jsonb,
    agents_used TEXT[] DEFAULT '{}',
    total_time_seconds FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_builder_user ON builder_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_builder_status ON builder_sessions(user_id, status);

-- 5. EMAIL SEQUENCES
CREATE TABLE IF NOT EXISTS email_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    brand_dna_id UUID,
    sequence_name TEXT NOT NULL DEFAULT 'Untitled Sequence',
    sequence_type TEXT NOT NULL CHECK (sequence_type IN (
        'welcome', 'nurture', 'launch', 'abandoned_cart',
        're_engagement', 'onboarding', 'upsell', 'event'
    )),
    goal TEXT,
    audience TEXT,
    emails JSONB DEFAULT '[]'::jsonb,
    estimated_performance JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sequences_user ON email_sequences(user_id);

-- RLS POLICIES
ALTER TABLE website_crawls ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE builder_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;

-- User policies
CREATE POLICY "Users own website_crawls" ON website_crawls FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users own marketing_campaigns" ON marketing_campaigns FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users own generated_assets" ON generated_assets FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users own builder_sessions" ON builder_sessions FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users own email_sequences" ON email_sequences FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Service role policies (backend uses service_role key)
CREATE POLICY "Service role website_crawls" ON website_crawls FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
CREATE POLICY "Service role marketing_campaigns" ON marketing_campaigns FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
CREATE POLICY "Service role generated_assets" ON generated_assets FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
CREATE POLICY "Service role builder_sessions" ON builder_sessions FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
CREATE POLICY "Service role email_sequences" ON email_sequences FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Auto-update triggers (reuse existing function if available)
DO $$
BEGIN
    -- Create the updated_at trigger function if it doesn't exist
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $func$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;

    -- Apply to tables with updated_at
    CREATE TRIGGER trg_campaigns_updated BEFORE UPDATE ON marketing_campaigns
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    CREATE TRIGGER trg_builder_updated BEFORE UPDATE ON builder_sessions
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    CREATE TRIGGER trg_sequences_updated BEFORE UPDATE ON email_sequences
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Some triggers already exist, continuing...';
END $$;
