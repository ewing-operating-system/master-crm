# Master CRM — Claude Code Instructions

## IDENTITY
You are running the Master CRM pipeline for Ewing Gillaspy's three businesses:
- **Next Chapter** (`next_chapter`) — Boutique M&A advisory for home services (plumbing, HVAC, roofing, pest, water treatment, flooring, steel, concrete)
- **AND Capital** (`and_capital`) — PE fund management, LP fundraising, hospitals, energy, med-tech, wellness
- **RevsUp** (`revsup`) — Contingent recruiting for revenue roles at SaaS companies

Plus standalone entities: `the_forge`, `biolev`, `sea_sweet`, `precision_exploration`

## NORTH STAR DOCUMENTS
The Entity Classification Guide (`data/north-star/NORTH-STAR-entity-classification-guide.md`) defines WHO and WHY — entities, classification rules, campaigns, person routing. The Infrastructure Map (`data/north-star/NORTH-STAR-infrastructure-map.md`) defines WHERE and WHAT. These are the authority. Read them before making entity or campaign decisions.

## SINGLE SOURCE OF TRUTH

### GitHub
- **This repo:** `https://github.com/ewing-operating-system/master-crm`
- **Skills repo:** `https://github.com/ewing-operating-system/ewing-registry`
- ALWAYS commit and push after changes

### Supabase (ONE instance — `master-crm`)
- **Project ID:** `dwrnfpjcvydhmhnvyzov`
- **URL:** `https://dwrnfpjcvydhmhnvyzov.supabase.co`
- **Service Role Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s`
- **Anon Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY`
- **Tables:** 33 tables, entity-tagged. 17 campaigns pre-seeded.
- **Views:** `nc_targets`, `nc_companies`, `nc_contacts`, `and_targets`, `and_companies`, `and_contacts`, `and_investors`, `and_daily_briefing`, `ru_targets`, `ru_companies`, `ru_contacts`

### Entity Rules
- Every transactional row MUST carry an `entity` field
- `do_not_call` is UNIVERSAL — no entity column. One DNC = blocked everywhere.
- Campaign names carry entity prefix: `AND-`, `NC-`, `RU-`
- Old names are WRONG — use the Name Crosswalk in the Infrastructure Map
- Shared capability / separate data: one engine, entity-specific config

### Classification Engine
Use `lib/classification.py` for deterministic entity classification. It implements the Entity Classification Guide decision tree as Python code. For ambiguous cases (confidence < 2), use LLM fallback.

### LLM Configuration
- **Claude Code CLI (`claude -p`):** Primary — $0.00 via subscription. Pipe via stdin.
- **DeepSeek V3:** OpenRouter — $0.004/call. For auditor + validator agents.
- **Gemini 2.5 Flash Lite:** OpenRouter — $0.001/call. For researcher agent.
- **GPT-4o Mini:** OpenRouter — $0.002/call. For executor agent.
- **OpenRouter Key:** `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`

### People Routing
- **Ewing Gillaspy:** AND Capital + Next Chapter only. NEVER RevsUp in Salesfinity.
- **Mark DeChant:** All three entities. Classify by WHAT he's doing, not who he is.
- **John Kelly:** Next Chapter + RevsUp ONLY. NEVER AND Capital.
- **Chris Rex:** AND Capital ONLY. Separate Microsoft stack, invisible to this workspace.

## BUYER HUB MAINTENANCE

Whenever buyers are added to `engagement_buyers` OR new buyer 1-pager HTML files are generated, run:

```bash
python3 scripts/refresh_hub_buyers.py \
  --proposal <proposal_id> \
  --hub public/<seller-slug>-hub.html \
  --prefix <seller-slug>
```

This script:
1. Backfills `buyer_city`, `buyer_state` from `HQ_MAP` (add new companies there)
2. Backfills `fit_score` from `confidence` field (HIGH=8, MEDIUM=6, LOW=4)
3. Regenerates the hub buyer table with all rows linked and sorted by fit score

**Never deploy a hub page without running this first.** If a buyer has no HQ in the map, the script exits with an error — add it before rerunning.

### Buyer Scoring Rule — Fit Score 8 Requires Confirmed Acquisition in Vertical

**A buyer scores 8 (HIGH) ONLY if they have a confirmed prior acquisition in the same or adjacent vertical as the seller.**

This rule applies universally to every deal. The top of every buyer list must be bona fide acquirers — companies that have actually written checks in this space.

| Score | Confidence | Meaning |
|-------|-----------|---------|
| 8 | HIGH | Bona fide acquirer — confirmed deal in the seller's vertical or directly adjacent |
| 6 | MEDIUM | Plausible buyer — operates in adjacent space but no confirmed acquisition on record |
| 4 | LOW | Weak fit — wrong vertical, pure VC (invests but doesn't acquire), advisory firm, or too small |

**Adjacent vertical definitions by seller type:**
- **Floor care / cleaning / restoration:** cleaning, restoration, janitorial, facility services, pest, home services roll-ups
- **HVAC / mechanical:** HVAC, plumbing, electrical, home services, building services, commercial mechanical
- **Water treatment:** water treatment, purification, softening, water infrastructure, water utilities, water technology
- **HR tech / B2B media:** HCM, payroll, talent management, recruiting, L&D platforms, B2B HR media/events
- **Precast concrete / building products:** precast, concrete manufacturing, infrastructure materials, pipe, building products
- **Any vertical:** PE firms count as HIGH only if they have a confirmed portfolio company OR completed deal in the seller's vertical — generalist PE without vertical evidence = MEDIUM

**How to apply:**
1. For each buyer, ask: "Can I name a specific company they acquired in this vertical?"
2. YES with a named deal → HIGH/8
3. YES but vague / unconfirmed → MEDIUM/6
4. NO → MEDIUM/6 at most; LOW/4 if clearly wrong vertical or no acquisition capacity
5. Never score above 8. Never use float scores (8.4, 9, 10) — round to 4, 6, or 8.

**Rationale:** The top of every buyer list must be actionable. Buyers who have already closed deals in the vertical understand the asset, move faster, and have internal approval to buy. Scoring 8 for "they could theoretically buy this" inflates the list and wastes outreach capacity.

When in doubt, score 6. Upgrade to 8 only after acquisition evidence is confirmed via Exa or primary source. Use `buyer_acquisition_history` field to store the evidence.

Known proposal IDs:
- HR.com Ltd: `63642786-ab16-456d-bac3-8f277f36ddc5` → prefix `hr-com-ltd`
- Springer Floor: `deed565b-156f-4d92-aa51-254802c71c6a` → prefix `springer-floor`
- AquaScience: *(look up from proposals table)*
- Air Control: *(look up from proposals table)*

## HARD RULES

1. **EVERY ROW** gets an entity tag. No exceptions. No untagged data enters the system.
2. **DNC is universal.** One block = blocked everywhere, all entities, all channels.
3. **NEVER** create a new Supabase project or instance. One instance: `master-crm`.
4. **NEVER** create new API accounts or sign up for services.
5. **ALWAYS** commit + push to `ewing-operating-system/master-crm` after changes.
6. **ALWAYS** log costs to `cost_log` table with entity tag.
7. **NEVER** generate reports from memory. Read the actual data first.
8. **ALWAYS** disclose NEEDS_REVIEW validation status.
9. Letters send BEFORE phone calls. Enrichment is post-letter investment.
10. Multi-LLM consensus required before customer-facing documents.
11. If a key fails, STOP and report. Do NOT sign up for a replacement.
12. **ALWAYS** verify Supabase tables exist before writing code that references them. Query the table with `?limit=0` via REST to confirm. If the table doesn't exist, create it via migration SQL BEFORE writing the feature code. Never ship code that references non-existent tables.
13. **ALWAYS** check actual column names in Supabase before coding. Use a probe insert or `?limit=1&select=*` to discover the real schema. Never assume column names — they may differ from your design (e.g. `last_viewed_at` not `last_seen_at`, `guardrail_log` not `guardrail_violations`).

## CAMPAIGNS (17)

| Campaign | Entity | Channel | Purpose |
|----------|--------|---------|---------|
| NC-SELL-LETTER | next_chapter | Direct mail | Ask if considering selling |
| NC-SELL-CALL | next_chapter | Cold call | Qualify interest in selling |
| NC-BUY-OUTREACH | next_chapter | Cold call/email | Match buyers to businesses |
| NC-TRANSCRIPT | next_chapter | Internal | Extract leads from calls |
| NC-TAM | next_chapter | Scraping | Build total addressable market |
| AND-LP-LETTER | and_capital | Direct mail | Introduce funds, request meeting |
| AND-LP-CALL | and_capital | Cold call | Book fund presentations |
| AND-LP-LINKEDIN | and_capital | LinkedIn | Warm LP introductions |
| AND-DEAL-SOURCE | and_capital | Cold call | Source deal flow from bankers |
| AND-FUND-DISTRO | and_capital | Email | Share fund decks |
| RU-CLIENT | revsup | Email/LinkedIn | Win recruiting engagements |
| RU-CANDIDATE | revsup | LinkedIn/boards | Find candidates |
| RU-REFERRAL | revsup | Referral | Inbound from network |
| FORGE-BOOMERANG | the_forge | Email | Athlete recruitment |
| BIOLEV-SALE | biolev | Meeting | BioLev sale (static assets) |
| SEASWEET-ROOFING | sea_sweet | Cold call | Roofing rollup |
| PEC-FRAUD | precision_exploration | Manual | NEVER automate |

## REPO STRUCTURE

```
master-crm/
├── agents/           # OpenClaw v2 agent identities
├── campaigns/        # Entity-specific business rules, templates, tone
│   ├── next_chapter/
│   ├── and_capital/
│   ├── revsup/
│   └── standalone/
├── lib/              # Shared code (supabase client, classification, LLM)
├── tam/              # TAM engine (Next Chapter)
├── data/
│   ├── north-star/   # Entity Classification Guide + Infrastructure Map
│   ├── audit-report/ # Extraction artifacts
│   └── exports/      # Migration scripts
└── CLAUDE.md         # This file
```
