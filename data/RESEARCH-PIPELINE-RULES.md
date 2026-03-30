# RESEARCH PIPELINE RULES
## Derived from 22 Research Pipeline Decisions (2026-03-30)

---

### Rule R1: Exa CEO Quote Fallback
**Decision:** When Exa fails to find CEO/owner quotes, search SEC filings and investor presentations (Q1 Choice D)
**Implementation:** Add fallback search chain in buyer research engine: Exa -> SEC EDGAR -> investor deck search -> skip with flag
**Affected engines:** buyer_research, exa_search, dossier_builder
**Status:** needs_code

### Rule R2: Private Company Research Priority
**Decision:** For private companies with no earnings calls, search in priority order: owner interviews/podcasts -> conference appearances -> local press -> industry data (Q2 Choice E)
**Implementation:** Research engine must attempt all four source types in order. Each source type tagged in source_attribution. Only mark "research complete" after all four attempted.
**Affected engines:** buyer_research, exa_search, dossier_builder
**Status:** needs_code

### Rule R3: Buyer Competitor Searches
**Decision:** Every buyer gets 2 competitor searches added to the research pipeline (Q3 Choice A)
**Implementation:** When a buyer is added to engagement_buyers, auto-queue 2 competitor Exa searches. Store competitor data in buyer profile. Used to create urgency in pitch materials.
**Affected engines:** buyer_research, orchestrator, proposal_generator
**Status:** needs_code

### Rule R5: Buyer Type Search Templates
**Decision:** 3 distinct search templates: PE template, strategic template, consolidator template (Q5 Choice A)
**Implementation:** Classify buyer_type on engagement_buyers. Each type gets different Exa search queries, different data extraction priorities, and different 1-pager section emphasis.
- PE template: fund size, portfolio companies, investment thesis, sector focus
- Strategic template: market position, acquisition history, synergy potential, integration approach
- Consolidator template: platform companies owned, add-on criteria, geographic footprint, roll-up thesis
**Affected engines:** buyer_research, exa_search, buyer_1pager_generator
**Status:** needs_code

### Rule R6: Conflicting Data Display
**Decision:** Show BOTH values with sources -- never silently pick one (Q6 Choice C)
**Implementation:** When data conflicts detected, store in `companies.data_conflicts` JSONB array. Format: [{"field": "employee_count", "value_a": 15, "source_a": "exa", "value_b": 45, "source_b": "deal_research"}]. Page generators must render both values with source labels. Admin view shows conflict details; client view shows higher-confidence value with footnote.
**Affected engines:** data_assembly, page_generators, dossier_builder
**Status:** applied (schema) / needs_code (rendering)

### Rule R7: Slider Field Estimation Policy
**Decision:** Estimate if confidence > MEDIUM, blank if LOW (Q7 Choice C)
**Implementation:** For revenue, employees, com/res split sliders: check field_confidence. If confidence >= MEDIUM, show estimate with "estimated" badge. If LOW, leave blank with "data pending" indicator.
**Affected engines:** proposal_generator, data_room_generator, field_confidence
**Status:** needs_code

### Rule R8: Thin Narrative Publishing
**Decision:** Publish thin narratives (<5K chars) but flag with yellow banner "THIN RESEARCH -- enrichment pending" (Q8 Choice B)
**Implementation:** If story_narrative length < 5000 chars, add `thin_research: true` flag to page metadata. Page renderer shows yellow banner at top: "THIN RESEARCH -- enrichment pending". Orchestrator auto-queues additional research for thin narratives.
**Affected engines:** proposal_generator, page_renderer, orchestrator
**Status:** needs_code

### Rule R9: Proposals Table is Canonical
**Decision:** proposals table is the single source of truth for page generation (Q9 Choice A)
**Implementation:** ALL page generators read from proposals table, never from dossier_final directly. dossier_final feeds INTO proposals via the assembly engine. If proposals and dossier_final conflict, proposals wins. Certifier validates proposals data before page generation.
**Affected engines:** ALL page generators, data_assembly, certifier
**Status:** needs_code (audit existing generators)

### Rule R11: Page Order Confirmed
**Decision:** Current page order is correct: narrative -> strengths -> market -> valuation -> attack -> timeline (Q11 Choice A)
**Implementation:** No change needed. Document as canonical order in page generation config.
**Affected engines:** proposal_generator
**Status:** applied

### Rule R12: Buyer 1-Pager Hide Empty Sections
**Decision:** Hide sections without enough data -- never show empty sections (Q12 Choice B)
**Implementation:** Buyer 1-pager generator checks each of 7 SAP sections. If section has < minimum data threshold (defined per section), omit entirely from rendered page. Never show "No data available" sections.
**Affected engines:** buyer_1pager_generator, page_renderer
**Status:** needs_code

### Rule R13: Data Room Methodology Visibility
**Decision:** Admin sees methodology by default. Client sees methodology behind expandable accordion (Q13 Choice C)
**Implementation:** Data room page has two render modes: `admin` (methodology visible) and `client` (methodology in expandable/collapsible section). Role determined by viewer authentication context.
**Affected engines:** data_room_generator, page_renderer, auth
**Status:** needs_code

### Rule R14: EBITDA Lever Display
**Decision:** Strengths prominent, gaps in separate section (Q14 Choice C)
**Implementation:** EBITDA levers page shows confirmed levers prominently at top. Missing/weak levers shown in separate "Growth Opportunities" section below. Never frame gaps as red flags -- frame as upside.
**Affected engines:** ebitda_lever_generator, page_renderer
**Status:** needs_code

### Rule R15: Attack Plans Must Be Specific
**Decision:** SAP standard -- named contacts, referenced acquisitions, actual scripts (Q15 Choice A)
**Implementation:** Attack plan section must include: specific contact names (from enrichment), their role and decision authority, reference to buyer's past acquisitions, specific outreach script/template, timeline with dates. Generic plans ("letters to top 10") are rejected by certifier.
**Affected engines:** attack_plan_generator, certifier, enrichment_engine
**Status:** needs_code

### Rule R17: Certifier Issues + Fix Instructions
**Decision:** NEEDS_REVIEW flags must include both issues found AND fix instructions (Q17 Choice C)
**Implementation:** Certifier output format: {"status": "NEEDS_REVIEW", "issues": [{"field": "revenue", "issue": "Missing source", "fix": "Run Exa search for '[company] revenue annual report'"}]}. Each issue must have actionable fix instruction.
**Affected engines:** certifier, orchestrator
**Status:** needs_code

### Rule R18: Per-Field Confidence Indicators
**Decision:** No badge -- per-field indicators instead (Q18 Choice C)
**Implementation:** field_confidence JSONB on companies and dossier_final stores per-field confidence. Page renderers show inline confidence indicators (green=CONFIRMED, yellow=ESTIMATED, gray=UNKNOWN) next to each data point. No aggregate badge.
**Affected engines:** page_renderers, field_confidence, data_assembly
**Status:** applied (schema) / needs_code (rendering)

### Rule R19: Full Source Attribution
**Decision:** Every fact gets source attribution like academic footnotes (Q19 Choice A)
**Implementation:** source_attribution JSONB on dossier_final, proposals, engagement_buyers stores array of {"fact": "revenue $8M", "source": "Exa search", "url": "https://...", "confidence": "CONFIRMED", "retrieved_at": "2026-03-30"}. Page renderers show footnote numbers linking to source list at bottom. Admin view shows full attribution; client view shows source count.
**Affected engines:** ALL research engines, ALL page generators, data_assembly
**Status:** applied (schema) / needs_code (population + rendering)

### Rule R20: Page Regeneration Diff
**Decision:** Always show diff of what changed on page regeneration (Q20 Choice A)
**Implementation:** previous_version_diff TEXT on page_versions stores human-readable diff. On regeneration: compare new HTML/content to previous version, generate diff summary, store in column. Admin UI shows "What changed" expandable with diff content.
**Affected engines:** page_version_engine, page_renderer, admin_ui
**Status:** applied (schema) / needs_code (diff generation)

### Rule R21: Buyer Enrichment Parallelism
**Decision:** 2 Exa searches at a time per buyer -- balanced approach (Q21 Choice C)
**Implementation:** Orchestrator runs buyer Exa searches with concurrency=2. Prevents rate limiting while maintaining speed. Queue system processes 2 searches in parallel, waits for both, then launches next 2.
**Affected engines:** orchestrator, exa_search, buyer_research
**Status:** needs_code

### Rule R22: Minimum Research Before Publishing
**Decision:** Research + validation + certification must all complete before ANY page appears (Q22 Choice D)
**Implementation:** Page generation is gated behind three checks: (1) research_status = 'complete', (2) validation_status = 'passed', (3) certification_status = 'certified'. Orchestrator enforces this sequence. No partial pages allowed.
**Affected engines:** orchestrator, certifier, ALL page generators
**Status:** needs_code

### Rule R23: Uniform Research Depth
**Decision:** Same depth for everything -- no shortcuts (Q23 Choice C)
**Implementation:** No per-deal research depth setting. Every deal gets the full research pipeline: all Exa searches, all source types, all validation steps. No "lite" mode.
**Affected engines:** orchestrator, research_config
**Status:** needs_code

### Rule R24: Build All 7 SAP Missing Sections
**Decision:** Build all 7 missing SAP sections at once (Q24 Choice A)
**Implementation:** SAP audit identified 7 missing sections. All must be built as a single sprint. No prioritization -- they ship together.
**Affected engines:** buyer_1pager_generator, page_renderer, proposal_generator
**Status:** needs_build

### Rule R25: Goal Tracker Drives Priority
**Decision:** Goal tracker per deal drives orchestrator priority -- deals behind targets get researched first (Q25 Choice A)
**Implementation:** deal_goals table tracks per-deal goals (meetings_booked, letters_sent, buyers_contacted, offers_received). Orchestrator queries deal_goals, calculates gap (target - current), and prioritizes deals with largest gaps. Wieser seeded: 5 meetings by 2026-12-31.
**Affected engines:** orchestrator, deal_goals table, dashboard
**Status:** applied (schema + seed) / needs_code (orchestrator integration)

---

## SKIPPED DECISIONS (3)
- **Q4:** Found buyer's VP Corp Dev on LinkedIn -- also search for direct email? (SKIPPED)
- **Q10:** Company has old deal_research data but NO new Exa research -- publish or force refresh? (SKIPPED)
- **Q16:** Dual-LLM certification -- what should the SECOND model be? (SKIPPED)

---

## DATABASE CHANGES APPLIED

| Table | Column | Type | Purpose |
|-------|--------|------|---------|
| dossier_final | source_attribution | JSONB | R19 -- fact-level source tracking |
| proposals | source_attribution | JSONB | R19 -- fact-level source tracking |
| engagement_buyers | source_attribution | JSONB | R19 -- fact-level source tracking |
| page_versions | previous_version_diff | TEXT | R20 -- diff on regeneration |
| companies | data_conflicts | JSONB | R6 -- conflicting data storage |
| companies | field_confidence | JSONB | R18 -- per-field confidence (pre-existing) |
| dossier_final | field_confidence | JSONB | R18 -- per-field confidence (pre-existing) |
| deal_goals | (new table) | -- | R25 -- goal tracker |

**Seed data:** Wieser Concrete Products -- meetings_booked goal, target=5, by 2026-12-31
