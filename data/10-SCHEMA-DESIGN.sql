-- ============================================================
-- MASTER CRM — New Supabase Schema
-- Instance: dwrnfpjcvydhmhnvyzov (master-crm)
-- Designed from: Entity Classification Guide + Infrastructure Map
-- ============================================================

-- ─── ENUMS ──────────────────────────────────────────────────

CREATE TYPE entity_type AS ENUM (
    'next_chapter',
    'and_capital',
    'revsup',
    'the_forge',
    'biolev',
    'sea_sweet',
    'precision_exploration',
    'system'
);

CREATE TYPE lead_stage AS ENUM (
    'raw_lead',
    'marketing_unqualified',
    'marketing_qualified',
    'sales_qualified',
    'opportunity',
    'signed_client',
    'active',
    'closed_won',
    'closed_lost',
    'nurture'
);

CREATE TYPE campaign_channel AS ENUM (
    'direct_mail',
    'cold_call',
    'email',
    'linkedin',
    'referral',
    'transcript_mining',
    'scraping',
    'meeting'
);

CREATE TYPE pipeline_status AS ENUM (
    'pending',
    'researched',
    'validated',
    'synthesized',
    'valued',
    'certified',
    'letter_drafted',
    'sent',
    'responded',
    'exhausted'
);

-- ─── CORE: CONTACTS & COMPANIES (normalized, shared) ────────

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    company_name TEXT NOT NULL,
    domain TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'US',
    phone TEXT,
    email TEXT,
    website TEXT,
    industry TEXT,
    vertical TEXT,
    employee_count INTEGER,
    estimated_revenue NUMERIC,
    estimated_ebitda NUMERIC,
    ebitda_confidence TEXT,
    google_rating NUMERIC,
    google_review_count INTEGER,
    gbp_url TEXT,
    lead_stage lead_stage DEFAULT 'raw_lead',
    entity_confidence NUMERIC,
    entity_reason TEXT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    company_id UUID REFERENCES companies(id),
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    title TEXT,
    email TEXT,
    phone TEXT,
    cell_phone TEXT,
    linkedin_url TEXT,
    city TEXT,
    state TEXT,
    lead_stage lead_stage DEFAULT 'raw_lead',
    entity_confidence NUMERIC,
    entity_reason TEXT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ─── ENTITY-SPECIFIC RELATIONSHIP TABLES ────────────────────

-- Next Chapter: business owner profiles (sell-side targets)
CREATE TABLE nc_owner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id),
    company_id UUID REFERENCES companies(id),
    owner_name TEXT,
    owner_title TEXT,
    owner_quotes TEXT,
    owner_vision TEXT,
    owner_background TEXT,
    culture_signals TEXT,
    years_in_business INTEGER,
    retirement_timeline TEXT,
    succession_status TEXT,
    sde NUMERIC,
    az_roc_license TEXT,
    bbb_rating TEXT,
    best_reviews TEXT,
    community_involvement TEXT,
    awards TEXT,
    data_quality_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- AND Capital: investor profiles (LP targets)
CREATE TABLE and_investor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id),
    company_id UUID REFERENCES companies(id),
    investor_type TEXT,  -- superconnector, direct_investor, family_office, ria, institutional
    aum NUMERIC,
    finra_risk TEXT,
    fund_tags TEXT[],
    archetypes TEXT[],
    thesis_alignment TEXT,
    openers TEXT,
    scripts TEXT,
    propensity_score NUMERIC,
    sector_alignment TEXT[],  -- Oil & Gas, Healthcare, etc.
    fund_vertical TEXT,  -- health_wellness or energy_transition
    created_at TIMESTAMPTZ DEFAULT now()
);

-- AND Capital: events and networking
CREATE TABLE and_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name TEXT NOT NULL,
    event_date DATE,
    location TEXT,
    event_type TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE and_event_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES and_events(id),
    contact_id UUID REFERENCES contacts(id),
    rsvp_status TEXT,
    priority INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RevsUp: placement tracking
CREATE TABLE ru_placements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id),  -- the hiring manager
    company_id UUID REFERENCES companies(id),  -- the company hiring
    role_title TEXT,
    role_type TEXT,  -- AE, SDR, BDR, CSM, VP Sales, CRO
    search_fee NUMERIC,
    salary_percentage NUMERIC,
    success_fee NUMERIC,
    candidate_name TEXT,
    candidate_linkedin TEXT,
    status TEXT,  -- open, sourcing, interviewing, placed, cancelled
    placed_date DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Standalone: The Forge (Boomerang)
CREATE TABLE forge_boomerang_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT,
    college TEXT,
    college_sport TEXT,
    grad_year INTEGER,
    current_city TEXT,
    current_team TEXT,
    estimated_career_earnings NUMERIC,
    follower_count INTEGER,
    notes TEXT,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── CAMPAIGNS ──────────────────────────────────────────────

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id TEXT UNIQUE NOT NULL,  -- e.g., NC-SELL-LETTER, AND-LP-CALL
    entity entity_type NOT NULL,
    name TEXT NOT NULL,
    audience TEXT,
    channel campaign_channel,
    purpose TEXT,
    fee_structure TEXT,
    engagement_terms TEXT,
    tone TEXT,
    template_rules TEXT,
    quality_threshold NUMERIC,
    cost_cap NUMERIC,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── PIPELINE ───────────────────────────────────────────────

CREATE TABLE targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    campaign_id TEXT REFERENCES campaigns(campaign_id),
    company_id UUID REFERENCES companies(id),
    company_name TEXT,
    pipeline_status pipeline_status DEFAULT 'pending',
    assigned_rep TEXT,
    -- Acquisition detection (for buy-side)
    acquirer_name TEXT,
    acquisition_status TEXT,
    acquisition_date DATE,
    acquisition_source TEXT,
    -- Outreach tracking
    letter_sent_at TIMESTAMPTZ,
    email_sent_at TIMESTAMPTZ,
    called_at TIMESTAMPTZ,
    responded_at TIMESTAMPTZ,
    -- Metadata
    entity_confidence NUMERIC,
    entity_reason TEXT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dossier_final (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    target_id UUID REFERENCES targets(id),
    company_name TEXT,
    run_batch TEXT,
    owner_name TEXT,
    owner_title TEXT,
    owner_quotes TEXT,
    owner_vision TEXT,
    owner_background TEXT,
    culture_signals TEXT,
    financial_snapshot JSONB,
    competitive_landscape JSONB,
    narrative TEXT,
    valuation_analysis TEXT,
    certification_result JSONB,
    letter_draft TEXT,
    letter_status TEXT DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dossier_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    target_id UUID,
    company_name TEXT,
    run_batch TEXT,
    step_number INTEGER,
    step_name TEXT,
    agent_role TEXT,
    model_provider TEXT,
    model_name TEXT,
    input_data JSONB,
    output_data JSONB,
    cost_usd NUMERIC DEFAULT 0,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dossier_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    target_id UUID,
    company_name TEXT,
    run_batch TEXT,
    fact_category TEXT,
    fact_key TEXT,
    fact_value TEXT,
    source_type TEXT,
    source_url TEXT,
    source_search_query TEXT,
    source_excerpt TEXT,
    confidence NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE cost_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    dossier_id UUID,
    campaign_id TEXT,
    api_name TEXT,
    operation TEXT,
    cost_usd NUMERIC DEFAULT 0,
    tokens_input INTEGER,
    tokens_output INTEGER,
    credits_used INTEGER,
    exa_searches INTEGER,
    exa_results INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sent_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    campaign_id TEXT REFERENCES campaigns(campaign_id),
    target_id UUID REFERENCES targets(id),
    company_name TEXT,
    document_type TEXT,
    content_hash TEXT,
    content_snapshot TEXT,
    sent_via TEXT,
    sent_to TEXT,
    status TEXT DEFAULT 'DRAFT',
    source_provenance_snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── CALL INTELLIGENCE ──────────────────────────────────────

CREATE TABLE call_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    contact_id UUID REFERENCES contacts(id),
    company_id UUID REFERENCES companies(id),
    campaign_id TEXT,
    rep_name TEXT,
    call_date TIMESTAMPTZ,
    duration_seconds INTEGER,
    direction TEXT,
    disposition TEXT,
    transcript_text TEXT,
    notes TEXT,
    salesfinity_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE call_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    call_id UUID REFERENCES call_log(id),
    transcript_text TEXT,
    opener_archetype TEXT,
    opening_sequence TEXT,
    word_volumes JSONB,
    talk_listen_ratio NUMERIC,
    sentiment_trajectory TEXT,
    objections TEXT,
    counters_used TEXT,
    engagement_level TEXT,
    audience_segment TEXT,
    waste_score NUMERIC,
    resolution TEXT,
    llm_extracted_fields JSONB,
    entity_confidence NUMERIC,
    entity_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- DNC is UNIVERSAL — no entity column (Rule 3)
CREATE TABLE do_not_call (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id),
    company_id UUID REFERENCES companies(id),
    person_name TEXT,
    company_name TEXT,
    phone TEXT,
    reason TEXT,
    reason_category TEXT,
    reason_text TEXT,
    block_company BOOLEAN DEFAULT false,
    added_by TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── OUTREACH ───────────────────────────────────────────────

CREATE TABLE outreach_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    campaign_id TEXT REFERENCES campaigns(campaign_id),
    target_id UUID REFERENCES targets(id),
    company_name TEXT,
    owner_name TEXT,
    owner_email TEXT,
    city TEXT,
    state TEXT,
    report_url TEXT,
    batch_date DATE,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dialer_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    campaign_id TEXT,
    target_id UUID REFERENCES targets(id),
    company_name TEXT,
    owner_name TEXT,
    phone TEXT,
    call_script_opener TEXT,
    call_notes TEXT,
    city TEXT,
    state TEXT,
    vertical TEXT,
    batch_date DATE,
    status TEXT DEFAULT 'pending',
    called_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE pipeline_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    target_id UUID,
    action TEXT,
    agent TEXT,
    details TEXT,
    cost_usd NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── TAM ENGINE (100% Next Chapter) ────────────────────────

CREATE TABLE tam_businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL DEFAULT 'next_chapter',
    company_name TEXT,
    category TEXT,
    city TEXT,
    state TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    discovered_via TEXT,
    accepted_source TEXT,
    enrichment_status TEXT,
    az_roc_license TEXT,
    awards_count INTEGER,
    data_quality_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tam_final (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL DEFAULT 'next_chapter',
    business_id UUID REFERENCES tam_businesses(id),
    company_name TEXT,
    category TEXT,
    city TEXT,
    state TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    discovered_via TEXT,
    accepted_source TEXT,
    data_quality_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tam_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL DEFAULT 'next_chapter',
    business_id UUID,
    owner_name TEXT,
    president_name TEXT,
    phone TEXT,
    email TEXT,
    model_name TEXT,
    confidence_score NUMERIC,
    cost_usd NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tam_owner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL DEFAULT 'next_chapter',
    business_id UUID,
    company_name TEXT,
    category TEXT,
    city TEXT,
    state TEXT,
    address TEXT,
    az_roc_license TEXT,
    bbb_rating TEXT,
    best_reviews TEXT,
    awards TEXT,
    community_involvement TEXT,
    active_buyers TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tam_scrape_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL DEFAULT 'next_chapter',
    category TEXT,
    city TEXT,
    source TEXT,
    records_found INTEGER,
    records_enriched INTEGER,
    records_verified INTEGER,
    error_message TEXT,
    metadata JSONB,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── DEALS ──────────────────────────────────────────────────

CREATE TABLE deal_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    deal_name TEXT,
    asset_name TEXT,
    asset_type TEXT,
    company_name TEXT,
    owner_name TEXT,
    category TEXT,
    city TEXT,
    state TEXT,
    website TEXT,
    research_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE acquisition_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity entity_type NOT NULL,
    slug TEXT,
    deal_id TEXT,
    client_slug TEXT,
    company_name TEXT,
    description TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'US',
    website TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ─── SYSTEM TABLES (entity-agnostic) ───────────────────────

CREATE TABLE audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT,
    content TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE harvests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT,
    machine TEXT,
    content TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT,
    title TEXT,
    thread_source TEXT,
    content TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE skills_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name TEXT UNIQUE,
    description TEXT,
    content TEXT,
    entity_affinity TEXT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ─── ENTITY-SCOPED VIEWS ───────────────────────────────────

CREATE VIEW nc_targets AS SELECT * FROM targets WHERE entity = 'next_chapter';
CREATE VIEW nc_companies AS SELECT * FROM companies WHERE entity = 'next_chapter';
CREATE VIEW nc_contacts AS SELECT * FROM contacts WHERE entity = 'next_chapter';

CREATE VIEW and_targets AS SELECT * FROM targets WHERE entity = 'and_capital';
CREATE VIEW and_companies AS SELECT * FROM companies WHERE entity = 'and_capital';
CREATE VIEW and_contacts AS SELECT * FROM contacts WHERE entity = 'and_capital';
CREATE VIEW and_investors AS
    SELECT c.*, ip.*
    FROM contacts c
    JOIN and_investor_profiles ip ON ip.contact_id = c.id
    WHERE c.entity = 'and_capital';

CREATE VIEW ru_targets AS SELECT * FROM targets WHERE entity = 'revsup';
CREATE VIEW ru_companies AS SELECT * FROM companies WHERE entity = 'revsup';
CREATE VIEW ru_contacts AS SELECT * FROM contacts WHERE entity = 'revsup';

-- Daily briefing view (AND Capital — recreated from pgoo)
CREATE VIEW and_daily_briefing AS
    SELECT
        e.event_name,
        e.event_date,
        e.location,
        c.full_name AS contact_name,
        c.title,
        co.company_name,
        ip.propensity_score,
        ip.sector_alignment,
        et.rsvp_status,
        et.priority
    FROM and_events e
    JOIN and_event_targets et ON et.event_id = e.id
    JOIN contacts c ON c.id = et.contact_id
    LEFT JOIN companies co ON co.id = c.company_id
    LEFT JOIN and_investor_profiles ip ON ip.contact_id = c.id
    WHERE e.event_date >= CURRENT_DATE
    ORDER BY e.event_date, et.priority;

-- ─── INDEXES ────────────────────────────────────────────────

CREATE INDEX idx_companies_entity ON companies(entity);
CREATE INDEX idx_contacts_entity ON contacts(entity);
CREATE INDEX idx_targets_entity ON targets(entity);
CREATE INDEX idx_targets_campaign ON targets(campaign_id);
CREATE INDEX idx_targets_status ON targets(pipeline_status);
CREATE INDEX idx_dossier_final_entity ON dossier_final(entity);
CREATE INDEX idx_call_analysis_entity ON call_analysis(entity);
CREATE INDEX idx_dialer_queue_entity ON dialer_queue(entity);
CREATE INDEX idx_sent_log_entity ON sent_log(entity);
CREATE INDEX idx_cost_log_entity ON cost_log(entity);
CREATE INDEX idx_pipeline_log_entity ON pipeline_log(entity);
CREATE INDEX idx_tam_businesses_entity ON tam_businesses(entity);
CREATE INDEX idx_do_not_call_phone ON do_not_call(phone);
CREATE INDEX idx_do_not_call_company ON do_not_call(company_name);

-- ─── SEED: CAMPAIGNS (17) ──────────────────────────────────

INSERT INTO campaigns (campaign_id, entity, name, audience, channel, purpose) VALUES
-- Next Chapter (5)
('NC-SELL-LETTER', 'next_chapter', 'Owner Letter Campaign', 'Business owners in trades/services', 'direct_mail', 'Ask if considering selling'),
('NC-SELL-CALL', 'next_chapter', 'Prospect Cold Calling', 'Business owners (HVAC, plumbing, pest, etc.)', 'cold_call', 'Qualify interest in selling'),
('NC-BUY-OUTREACH', 'next_chapter', 'Buy-Side Outreach', 'Acquirers, PE roll-ups, strategic acquirers', 'cold_call', 'Match buyers to available businesses'),
('NC-TRANSCRIPT', 'next_chapter', 'Transcript Mining', 'Internal — Fireflies call recordings', 'transcript_mining', 'Extract leads from conversations'),
('NC-TAM', 'next_chapter', 'TAM Engine', 'Home services market', 'scraping', 'Build total addressable market'),
-- AND Capital (5)
('AND-LP-LETTER', 'and_capital', 'LP Letter Campaign', 'Family office principals, RIAs, allocators', 'direct_mail', 'Introduce AND Capital funds, request meeting'),
('AND-LP-CALL', 'and_capital', 'LP Cold Calling', 'Family offices, wealth advisors', 'cold_call', 'Book meetings for fund presentations'),
('AND-LP-LINKEDIN', 'and_capital', 'LP LinkedIn Outreach', 'Teruel/Ewing/Mark/Denise connections', 'linkedin', 'Warm introductions to qualified LPs'),
('AND-DEAL-SOURCE', 'and_capital', 'Deal Sourcing Cold Calls', 'Investment bankers', 'cold_call', 'Source deal flow for fund verticals'),
('AND-FUND-DISTRO', 'and_capital', 'Fund Brochure Distribution', 'Qualified investors', 'email', 'Share fund decks'),
-- RevsUp (3)
('RU-CLIENT', 'revsup', 'Recruiting Client Outreach', 'VP Sales, CROs at SaaS companies', 'email', 'Win contingent search engagements'),
('RU-CANDIDATE', 'revsup', 'Candidate Sourcing', 'Revenue professionals', 'linkedin', 'Find candidates for open roles'),
('RU-REFERRAL', 'revsup', 'Referral Program', 'Ewing personal network', 'referral', 'Inbound leads from network'),
-- Standalone (4)
('FORGE-BOOMERANG', 'the_forge', 'Boomerang Athlete Outreach', 'Former college athletes returning to Atlanta', 'email', 'Athlete recruitment'),
('BIOLEV-SALE', 'biolev', 'BioLev Sale Process', 'Potential BioLev acquirers/partners', 'meeting', 'BioLev sale — static assets'),
('SEASWEET-ROOFING', 'sea_sweet', 'Sea Sweet Roofing Rollup', 'Roofing companies for acquisition', 'cold_call', 'Roofing rollup acquisitions'),
('PEC-FRAUD', 'precision_exploration', 'PEC Fraud Case Management', 'Internal fraud case tracking', 'meeting', 'MANUAL ONLY — never automate');
