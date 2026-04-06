-- ============================================================
-- CookinCards Supabase Migration
-- Tables: card_collections, card_portfolio_snapshots
-- Run in: Supabase Dashboard -> SQL Editor -> New Query -> Run
-- ============================================================

CREATE TABLE IF NOT EXISTS card_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    card_name TEXT NOT NULL,
    card_set TEXT,
    card_number TEXT,
    card_type TEXT DEFAULT 'tcg'
        CHECK (card_type IN ('tcg', 'sport', 'mtg', 'yugioh')),
    condition TEXT,
    grade_estimate FLOAT,
    grading_company TEXT,
    cert_number TEXT,
    estimated_value FLOAT,
    purchase_price FLOAT,
    image_url TEXT,
    scan_data JSONB DEFAULT '{}'::jsonb,
    grade_data JSONB DEFAULT '{}'::jsonb,
    ximilar_data JSONB DEFAULT '{}'::jsonb,
    notes TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cards_user ON card_collections(user_id);
CREATE INDEX IF NOT EXISTS idx_cards_type ON card_collections(user_id, card_type);

ALTER TABLE card_collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own cards" ON card_collections FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role cards" ON card_collections FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Portfolio value snapshots
CREATE TABLE IF NOT EXISTS card_portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    total_cards INTEGER DEFAULT 0,
    total_value FLOAT DEFAULT 0,
    snapshot_date DATE DEFAULT CURRENT_DATE,
    breakdown JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_card_snapshots_user ON card_portfolio_snapshots(user_id);

ALTER TABLE card_portfolio_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own snapshots" ON card_portfolio_snapshots FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role snapshots" ON card_portfolio_snapshots FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
