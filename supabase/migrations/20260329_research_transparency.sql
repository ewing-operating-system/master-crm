CREATE TABLE IF NOT EXISTS research_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    method_code TEXT UNIQUE NOT NULL,
    method_name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    tool TEXT,
    query_template TEXT,
    expected_output TEXT[],
    success_rate NUMERIC,
    avg_cost NUMERIC,
    discovered_by TEXT,
    discovery_context TEXT,
    times_used INTEGER DEFAULT 0,
    times_succeeded INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID,
    company_name TEXT NOT NULL,
    method_code TEXT REFERENCES research_methods(method_code),
    actual_query TEXT,
    tool TEXT,
    raw_response JSONB,
    extracted_fields JSONB,
    result_quality NUMERIC,
    result_count INTEGER,
    status TEXT DEFAULT 'complete',
    error_message TEXT,
    cost_usd NUMERIC DEFAULT 0,
    executed_at TIMESTAMPTZ DEFAULT now(),
    duration_ms INTEGER,
    source_urls TEXT[],
    source_excerpts TEXT[],
    entity TEXT DEFAULT 'next_chapter'
);

CREATE INDEX IF NOT EXISTS idx_re_company ON research_executions(company_name);
CREATE INDEX IF NOT EXISTS idx_re_method ON research_executions(method_code);
