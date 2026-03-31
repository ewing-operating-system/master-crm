-- Migration: Final features tables
-- Features: #40 Why Sell, #49+#50 Activity Feed
-- Date: 2026-03-30

-- ═══════════════════════════════════════════
-- #49+#50: Activity Feed — Guardrail Violations
-- ═══════════════════════════════════════════

CREATE TABLE IF NOT EXISTS guardrail_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    violation_type TEXT NOT NULL CHECK (violation_type IN (
        'dnc_bypass', 'entity_misroute', 'cost_overspend',
        'hallucination_flag', 'trust_threshold', 'rate_limit', 'schema_violation'
    )),
    entity TEXT,
    target_id UUID,
    details JSONB DEFAULT '{}',
    severity TEXT NOT NULL DEFAULT 'warning' CHECK (severity IN ('critical', 'warning', 'info')),
    action_taken TEXT,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_guardrail_violations_created ON guardrail_violations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_guardrail_violations_severity ON guardrail_violations(severity);
CREATE INDEX IF NOT EXISTS idx_guardrail_violations_entity ON guardrail_violations(entity);

-- RLS: allow anon read, service role write
ALTER TABLE guardrail_violations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_guardrail_violations" ON guardrail_violations FOR SELECT TO anon USING (true);
CREATE POLICY "service_role_all_guardrail_violations" ON guardrail_violations FOR ALL TO service_role USING (true);

-- ═══════════════════════════════════════════
-- #49+#50: Activity Feed — User Sessions
-- ═══════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    user_name TEXT,
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    session_count INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);

ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_user_sessions" ON user_sessions FOR SELECT TO anon USING (true);
CREATE POLICY "service_role_all_user_sessions" ON user_sessions FOR ALL TO service_role USING (true);

-- ═══════════════════════════════════════════
-- #40: Why Sell Narratives
-- ═══════════════════════════════════════════

CREATE TABLE IF NOT EXISTS why_sell_narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    entity TEXT DEFAULT 'next_chapter',
    market_timing TEXT,
    owner_lifecycle TEXT,
    competitive_pressure TEXT,
    value_maximization TEXT,
    risk_of_waiting TEXT,
    narrative_summary TEXT,
    generated_by TEXT DEFAULT 'claude',
    quality_score NUMERIC,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'reviewed', 'approved', 'sent')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_why_sell_company ON why_sell_narratives(company_id);
CREATE INDEX IF NOT EXISTS idx_why_sell_entity ON why_sell_narratives(entity);

ALTER TABLE why_sell_narratives ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_why_sell_narratives" ON why_sell_narratives FOR SELECT TO anon USING (true);
CREATE POLICY "service_role_all_why_sell_narratives" ON why_sell_narratives FOR ALL TO service_role USING (true);

-- ═══════════════════════════════════════════
-- #40: Why Sell Buyer Pitches
-- ═══════════════════════════════════════════

CREATE TABLE IF NOT EXISTS why_sell_buyer_pitches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    buyer_id UUID NOT NULL,
    entity TEXT DEFAULT 'next_chapter',
    pitch_narrative TEXT,
    buyer_fit_reasons TEXT,
    acquisition_history TEXT,
    strategic_rationale TEXT,
    generated_by TEXT DEFAULT 'claude',
    quality_score NUMERIC,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'reviewed', 'approved', 'sent')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_why_sell_buyer_pitch ON why_sell_buyer_pitches(company_id, buyer_id);
CREATE INDEX IF NOT EXISTS idx_why_sell_buyer_entity ON why_sell_buyer_pitches(entity);

ALTER TABLE why_sell_buyer_pitches ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_why_sell_buyer_pitches" ON why_sell_buyer_pitches FOR SELECT TO anon USING (true);
CREATE POLICY "service_role_all_why_sell_buyer_pitches" ON why_sell_buyer_pitches FOR ALL TO service_role USING (true);
