# Extracted Campaign Definitions — From North Star Documents
# Source: Entity Classification Guide + Infrastructure Map
# Extracted: 2026-03-28

## Campaign Registry (17 total)

### Next Chapter Campaigns (5)

#### NC-SELL-LETTER — Owner Letter Campaign
- **Entity:** next_chapter
- **Audience:** Business owners in trades/services (plumbing, HVAC, roofing, pest, water treatment, flooring, steel, concrete)
- **Channel:** Direct mail (physical letters)
- **Purpose:** Ask if they're considering selling
- **Fee structure:** Success fees on closed M&A transactions
- **Tone:** Personal, respectful of owner's legacy, not pushy
- **Tables:** targets, sent_log, outreach_queue, campaigns, pipeline_log
- **Repos:** dossier-pipeline, and-call-command-pipeline (misnomer)
- **Lovable apps:** Next Chapter Reports (rebuilding)
- **Pipeline flow:** TAM scrape → dossier research → letter generation → mail
- **Business rule:** Letters send BEFORE phone calls. Enrichment (cell+email) is post-letter investment, not pre-letter gate.

#### NC-SELL-CALL — Prospect Cold Calling
- **Entity:** next_chapter
- **Audience:** Business owners (HVAC, plumbing, pest, etc.)
- **Channel:** Salesfinity parallel dialer
- **Purpose:** Qualify interest in selling
- **Tables:** dialer_queue, call_analysis, do_not_call (universal), pipeline_log
- **Skills:** cold-call-workflow, salesfinity-loader
- **Scheduled tasks:** call-ingest-hourly, call-sync, daily-maintenance, daily-tasks-created, dnc-salesfinity-sync, priority-rebuild, queue-autocheck
- **Business rule:** DNC check required before loading contacts. 3 emails + 2 calls + 1 letter with no response = exhausted.

#### NC-BUY-OUTREACH — Buy-Side Outreach
- **Entity:** next_chapter
- **Audience:** Acquirers, PE roll-ups in home services, strategic acquirers
- **Channel:** Cold call, email, referral
- **Purpose:** Match buyers to available businesses
- **Tables:** deal_research (67), acquisition_targets (9), targets (buy-side subset)
- **Repos:** blank-canvas-proposal, sunshine-code-forge
- **Active opportunity:** Debbie McGrath / HR.com — proposal due 2026-03-31
- **Partner:** CII (~1,500 buyers) — used per-deal, NOT a campaign. Not part of every deal.

#### NC-TRANSCRIPT — Transcript Mining
- **Entity:** next_chapter
- **Audience:** Internal — Fireflies call recordings
- **Channel:** Internal review
- **Purpose:** Extract leads from conversations
- **Tables:** call_analysis (NC subset), pipeline_log
- **Skills:** cold-call-workflow
- **Scheduled tasks:** daily-tasks-created

#### NC-TAM — TAM Engine
- **Entity:** next_chapter
- **Audience:** Home services market (HVAC primarily)
- **Channel:** Automated scraping (Google Places, Exa, state records)
- **Purpose:** Build total addressable market of businesses to sell
- **Tables:** tam_businesses (1000+), tam_final (1000+), tam_verifications (1000+), tam_owner_profiles (306), tam_scrape_runs (287)
- **Repos:** phoenix-tam-engine
- **Status:** All tables clean NC. No contamination.

---

### AND Capital Campaigns (5)

#### AND-LP-LETTER — LP Letter Campaign
- **Entity:** and_capital
- **Audience:** Family office principals, RIAs, allocators
- **Channel:** Direct mail (physical letters)
- **Purpose:** Introduce AND Capital funds, request meeting
- **Tables:** targets (AND subset), sent_log (AND subset), outreach_queue (AND subset), campaigns, pipeline_log
- **Business rule:** Shared letter ENGINE, different CONTENT engine. AND letters discuss fund structure (2% mgmt, 20% carry, 8% preferred return), institutional governance, GP co-investment.
- **Two fund verticals:**
  - AND Capital Health & Wellness Innovation Fund (GP: Denise Brown, MD)
  - AND Capital Energy Transition Fund (GP: Joe Park)

#### AND-LP-CALL — LP Cold Calling
- **Entity:** and_capital
- **Audience:** Family offices, wealth advisors
- **Channel:** Salesfinity parallel dialer
- **Purpose:** Book meetings for fund presentations
- **Tables:** dialer_queue (AND subset), call_analysis (AND subset), do_not_call (universal)
- **Lovable apps (rebuilding):** Marks NYC Hunt, NYC Outreach Hub
- **Skills:** cold-call-workflow, salesfinity-loader
- **Reps:** Mark DeChant (primary), Ewing (secondary)

#### AND-LP-LINKEDIN — LP LinkedIn Outreach
- **Entity:** and_capital
- **Audience:** Teruel/Ewing/Mark/Denise connections
- **Channel:** LinkedIn + Exa enrichment
- **Purpose:** Warm introductions to qualified LPs
- **Tables:** No dedicated tables found — needs buildout
- **Status:** Minimal infrastructure. Needs tables in v2.

#### AND-DEAL-SOURCE — Deal Sourcing Cold Calls
- **Entity:** and_capital
- **Audience:** Investment bankers
- **Channel:** Salesfinity parallel dialer
- **Purpose:** Source deal flow for fund verticals (hospitals, energy, med-tech)
- **Tables:** dialer_queue (AND subset), call_analysis (AND subset)
- **Lovable apps (rebuilding):** NYC Deal Maker

#### AND-FUND-DISTRO — Fund Brochure Distribution
- **Entity:** and_capital
- **Audience:** Qualified investors
- **Channel:** Email, meetings
- **Purpose:** Share fund decks for Health & Wellness and Energy Transition funds
- **Tables:** No dedicated tables found — needs buildout
- **Status:** Minimal infrastructure. Needs tables in v2.

---

### RevsUp Campaigns (3)

#### RU-CLIENT — Recruiting Client Outreach
- **Entity:** revsup
- **Audience:** VP Sales, CROs at SaaS companies
- **Channel:** Email, LinkedIn, referral
- **Purpose:** Win contingent search engagements
- **Tables:** No dedicated tables found — needs full buildout
- **Skills:** revsup-oo (Opportunity Overview documents)
- **Active rep:** Mark DeChant (active), John Kelly (active), Ewing (inactive — occasional referral)
- **Fee structure:** Flat search fee + % of salary + 6-month success fee

#### RU-CANDIDATE — Candidate Sourcing
- **Entity:** revsup
- **Audience:** Revenue professionals (AE, SDR, BDR, Sales Manager, VP Sales, CRO, CSM)
- **Channel:** LinkedIn, job boards, network
- **Purpose:** Find candidates for open roles
- **Tables:** No dedicated tables found — needs full buildout

#### RU-REFERRAL — Referral Program
- **Entity:** revsup
- **Audience:** Ewing's personal network (occasional)
- **Channel:** Word of mouth
- **Purpose:** Inbound leads from personal network
- **Tables:** No dedicated tables found — needs full buildout

---

### Standalone Campaigns (4)

#### FORGE-BOOMERANG — Boomerang Athlete Outreach
- **Entity:** the_forge
- **Audience:** Former college athletes returning to Atlanta
- **Tables:** boomerang_targets (227 rows — currently in rdnn, SHOULD NOT BE HERE)
- **Status:** Data exists but in wrong database. Move to v2 with entity tag.

#### BIOLEV-SALE — BioLev Sale Process
- **Entity:** biolev
- **Audience:** Potential BioLev acquirers/partners
- **Tables:** None (static assets only — 31 PPTX + 4 Python + 1 Excel in Google Drive)
- **Lovable app:** Fitness Pitch Builder (5 pitch decks — static, rebuilding)
- **Ownership:** Ewing 50% / Chris Rex 50%

#### SEASWEET-ROOFING — Sea Sweet Roofing Rollup
- **Entity:** sea_sweet
- **Audience:** Roofing companies for acquisition
- **Tables:** None
- **Google Drive:** 04 - Sea Sweet/ + 13 - New Roofing Rollup/
- **Note:** NOT Next Chapter. Standalone entity (Jeremy Christopher).

#### PEC-FRAUD — Precision Exploration Fraud Case Management
- **Entity:** precision_exploration
- **Audience:** Internal fraud case tracking
- **Tables:** Unknown (Lovable-managed Supabase, unknown instance ID)
- **Lovable apps:** Precision Exploration, Remix, NMR Science Showcase
- **Skills:** pec-case-manager (Cowork only)
- **Scheduled tasks:** pec-evidence-logger (DISABLED), pec-fact-finder (DISABLED)
- **Status:** MANUAL ONLY. Never automate. DO NOT TOUCH.

---

## Shared Capability Routing Rules

| Tool | NC Uses | AND Uses | RU Uses | Routing Rule |
|------|---------|----------|---------|-------------|
| Salesfinity dialer | NC-SELL-CALL | AND-LP-CALL, AND-DEAL-SOURCE | RU-CLIENT (Mark) | Tag by target company: home services=NC, LP/family office/hospital/energy=AND, SaaS hiring=RU |
| Letter engine | NC-SELL-LETTER | AND-LP-LETTER | — | ENGINE shared. CONTENT engine entity-specific (tone, terms, templates). Tag by recipient. |
| Exa enrichment | NC-SELL-LETTER, NC-TAM | AND-LP-LINKEDIN, AND-DEAL-SOURCE | — | Tag enrichment results with entity of target. |
| Fireflies | NC-TRANSCRIPT | AND-LP-CALL, AND-DEAL-SOURCE | RU-CLIENT | Tag by call context: deal=NC, fund/LP=AND, recruiting=RU |
| Dossier pipeline | NC-SELL-LETTER, NC-SELL-CALL, NC-TAM | Could serve AND but currently 100% NC | — | Needs entity parameter in v2. |
| DNC | ALL | ALL | ALL | Universal. One DNC = blocked everywhere. No entity column. |

## Person-to-Entity Routing

| Person | AND Capital | Next Chapter | RevsUp | Salesfinity |
|--------|------------|-------------|--------|-------------|
| Ewing Gillaspy | MD, M&A — client-facing | System architect, CTO, client-facing | Inactive — occasional referral | AND + NC ONLY |
| Mark DeChant | MD, LPs — cold calls LPs, family offices, brokers | Deal Manager | Founder — cold calls for recruiting | ALL THREE |
| John Kelly | NEVER | Active | Active | NC + RU ONLY |
| Chris Rex | CTO (separate Microsoft stack, invisible to this workspace) | — | — | AND ONLY |
| Teruel Carrasco | CEO | — | — | AND |
| Rod Heard | Founder & MD | — | — | AND |
| Loren Brink | President of M&A | May interact on NC deals | — | AND primarily |
| Denise Brown, MD | GP, Health & Wellness Fund | — | — | AND |
| Joe Park | GP, Energy Transition Fund | — | — | AND |
