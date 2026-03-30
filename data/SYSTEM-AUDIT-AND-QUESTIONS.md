# MASTER CRM — SYSTEM-BY-SYSTEM AUDIT

**Generated:** 2026-03-28
**Author:** Argus (Claude Opus 4.6)
**Purpose:** Honest, thorough, actionable quality assurance audit of every system in the master-crm project
**Authority:** This document exists to surface real risks, real gaps, and real questions. Nothing is softened.

---

## TABLE OF CONTENTS

1. Classification Engine
2. Proposal Engine
3. Profile Engine
4. Engagement Engine
5. Meeting Engine
6. Company Hub
7. Dashboard
8. Version Engine
9. Research Transparency
10. Step Tracking
11. Cost Tracking
12. Human Audit System
13. Listener Agent
14. Orchestrator + Worker + Watchdog
15. Web Server
16. EBITDA Lever Engine
17. Buyer Research
18. Follow-up Email + Data Room
19. Feedback Loop System
20. Template Library

---

## SYSTEM 1: Classification Engine

### What It Does
Deterministic entity routing system that assigns every record entering master-crm to one of seven entities (next_chapter, and_capital, revsup, the_forge, biolev, sea_sweet, precision_exploration). Implements a priority-ordered decision tree: campaign prefix, standalone keywords, person hard-routing, intent detection (hiring/transaction/capital), then company-type keyword fallback. Returns entity, sub_type, confidence score, and reasoning.

### Where It Gets Data
- **Input arguments** -> company_name, company_description, person_name, person_title, intent, industry, campaign_id, raw_text
- **Hardcoded keyword dictionaries** -> AND_CAPITAL_KEYWORDS (30+), NEXT_CHAPTER_KEYWORDS (30+), REVSUP_KEYWORDS (15+), intent sets, person routing maps
- **Worker agent** -> feeds targets table rows (company_name, extra_fields) when processing classifier queue items

### What Decisions It Makes
- Which of 7 entities a record belongs to (or no entity if confidence < 2)
- Whether a person is hard-routed (Chris Rex -> AND Capital only) or blocked (John Kelly never AND Capital)
- Sub-type classification: sell_side vs buy_side for NC, lp vs investment for AND, recruiting for RU
- Whether to fall through to LLM fallback (when deterministic confidence < 2.0)
- Disambiguation when NC and AND both score (trades signals reduce AND score)

### What Output It Creates
- **Classification dict** -> `{"entity": str, "sub_type": str, "confidence": float, "reason": str, "method": str}`
- **Updated targets table** -> entity field set on the target record (via worker)
- **agent_runs log entry** -> classification result stored for audit trail

### What Uses This Output Next
- **Orchestrator** reads entity field to determine which pipeline steps to queue (research, proposals, etc.)
- **Worker** uses entity to route budget checks and agent assignments
- **Every downstream engine** reads entity to apply entity-specific business rules, tone, templates
- **Cost tracking** uses entity to charge the right budget bucket
- **Supabase client** uses entity to enforce entity-tagging on writes

### 5 Fatal Flaws

1. **Keyword dictionaries are static and will rot.** New companies, new verticals, new people join the orbit constantly. The keyword sets are hardcoded Python sets. When Ewing signs a new deal in electrical or landscaping, the system misclassifies until someone manually adds keywords. There is no feedback mechanism to detect misclassifications in production.

2. **ILIKE fuzzy matching in LLM fallback is dangerously loose.** When deterministic classification fails and the worker calls Claude CLI or DeepSeek for LLM fallback, the result is `.strip().lower().replace(" ", "_")` and compared against a whitelist. But the prompt just says "Return ONLY the entity name" -- LLMs regularly add explanatory text. A response like "Based on the context, this appears to be next_chapter" would fail the whitelist check and be logged as "Could not classify" even though the LLM got it right.

3. **No deal_side awareness in classification.** The classifier determines entity but not deal_side (buy-side vs sell-side). This is the exact error that caused Weiser Concrete and Design Precast to get buyer 1-pagers when they ARE the buyer. The classification engine has no concept of deal_side, and the sub_type "sell_side" vs "buy_side" detection is primitive -- it checks for keywords like "seller" or "buyer" in the raw text, which almost never appears in a company name or industry field.

4. **Person routing is incomplete and non-dynamic.** PERSON_ENTITY_MAP only has 6 people hardcoded. PERSON_NEVER_MAP has 2 entries. There is no way to add new person routing rules without editing Python source code. When a new rep joins or a person changes roles, the code must be manually updated. There is no admin interface, no database-backed person routing, no override mechanism.

5. **No feedback loop from downstream engines.** If the proposal engine generates a terrible proposal because the entity was wrong, there is no signal back to the classifier. If Mark manually re-tags a record in the database, the classifier does not learn from that correction. Classification errors accumulate silently.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Static keyword dictionaries:**
- Enhancement A: Move keyword dictionaries to a `classification_keywords` Supabase table. Admin UI or simple CRUD lets Ewing add keywords without code changes. Monthly: auto-suggest new keywords from unclassified records.
- Enhancement B: Add a weekly "classification audit" that pulls all records classified in the last 7 days, groups by entity, and flags any that had confidence < 2.0 or were later re-tagged. Push summary to Monday dashboard.

**Flaw 2 — Loose LLM fallback parsing:**
- Enhancement A: Change the LLM fallback prompt to use a structured output format: "Respond with exactly one word from this list: next_chapter, and_capital, revsup, the_forge, biolev, sea_sweet, precision_exploration, unknown". Parse only the first word of the response.
- Enhancement B: Add regex extraction that searches the LLM response for any of the valid entity names, rather than requiring the entire response to match. Log the full response for audit.

**Flaw 3 — No deal_side awareness:**
- Enhancement A: Add deal_side detection to classify_entity() as a second pass. After entity is determined, check for buy-side signals (keywords like "acquire", "roll-up", "looking to buy", "acquisition target") vs sell-side signals ("sell my business", "exit planning", "retirement"). Return deal_side in the classification result.
- Enhancement B: Add a `deal_side` column to the targets table and require it to be set (manually if needed) before any proposal engine work begins. Proposal engine checks deal_side and generates the correct direction of outreach.

**Flaw 4 — Incomplete person routing:**
- Enhancement A: Move PERSON_ENTITY_MAP and PERSON_NEVER_MAP to a `person_routing` Supabase table with columns: person_name, entity_allowed, entity_blocked, updated_by, updated_at. Classifier queries this table dynamically.
- Enhancement B: Add person routing to the Monday dashboard as a visible section. When a new person appears in call logs or Salesfinity data, flag them for routing assignment.

**Flaw 5 — No feedback loop:**
- Enhancement A: Create a `classification_corrections` table. When any engine or human changes an entity tag on a record, log the original classification, the correction, and who corrected it. Monthly: aggregate corrections into keyword suggestions for the classifier.
- Enhancement B: Add a "confidence < 2 review queue" to the human_review_queue. Records that the classifier could not confidently classify get queued for human tagging, and the human's choice feeds back into keyword dictionaries.

### 5 Toughest Questions for Ewing

1. When a company does HVAC work AND has a family office investor, should the classifier route to Next Chapter (because HVAC is a trade) or AND Capital (because the family office is an LP prospect)? What is the tiebreaker rule?
2. Should the classifier ever auto-reclassify a record that was previously classified? If Mark manually tags something as "and_capital" and the classifier would have said "next_chapter", who wins on re-run?
3. For multi-entity people (Mark spans all 3), should the classifier tag by the CAMPAIGN the record came from, or by the CONTENT of the record? What if Mark is making a RevsUp call but mentions an NC deal?
4. How should the system handle companies that start as one entity and transition to another (e.g., a company Ewing sources for NC that later becomes an AND Capital fund investment)? Re-tag? Dual-tag? Fork the record?
5. Is there a classification confidence threshold below which the system should STOP all pipeline work and wait for human input, rather than guessing? What is that threshold -- is 1.0 too low? Should 1.5 be the hard floor?

---

## SYSTEM 2: Proposal Engine

### What It Does
Generates complete sell-side M&A proposals for Next Chapter Advisory targets. Assembles data from multiple Supabase tables, enriches gaps with Exa web search, loads market multiples for the target's vertical, generates a mega-prompt for Claude CLI to produce a structured JSON proposal (narrative, strengths, market analysis, valuation range, buyer profile, attack plan, outreach scripts), then renders polished HTML and stores everything in the proposals table.

### Where It Gets Data
- **companies table** -> company record (name, city, state, vertical, entity)
- **targets table** -> pipeline status, extra_fields (rich structured data from prior processing)
- **dossier_final table** -> narrative, owner background, culture signals, valuation analysis, overall score
- **deal_research table** -> deal-specific research notes
- **contacts table** -> contact records linked to the company
- **Exa API** -> web search results for company info, owner info, financial signals ($0.006/result * ~9 results = ~$0.054 per company)
- **market_multiples.json file** -> EBITDA multiple ranges by vertical (with hardcoded defaults if file missing)
- **Claude CLI** -> $0.00 content generation (primary)
- **OpenRouter (DeepSeek V3, GPT-4o Mini)** -> fallback LLM generation ($0.004 and $0.002 per call)

### What Decisions It Makes
- Whether to enrich with Exa (only if missing: revenue, employees, services, owner, founded)
- Which LLM to use: Claude CLI first, DeepSeek fallback, GPT-4o Mini as last resort
- Whether minimum data threshold is met (needs at least 2 of: name, owner, city, metric) -- skip if < 2
- How to format money values ($2.5M, $500K, etc.)
- Quality score (generated by the LLM, not independently verified)

### What Output It Creates
- **proposals table row** -> full proposal with all fields: narrative, strengths, market analysis, valuation range, attack plan, outreach scripts, HTML, JSON, quality score
- **HTML file** -> saved to data/proposals/{slug}.html
- **Auto-refresh trigger** -> calls refresh_hub() and refresh_dashboard() after generation
- **Cost log entries** -> Exa and OpenRouter costs logged

### What Uses This Output Next
- **Profile Engine** reads proposals for richer data to merge into company profiles
- **Engagement Engine** reads proposals to generate buyer-specific outreach scripts
- **Meeting Engine** reads proposals for meeting prep data
- **Company Hub** reads proposals for the aggregated company view
- **Dashboard** reads proposal status and quality scores for pipeline overview
- **Web Server** serves proposal HTML via /proposal/{slug} route
- **Certifier agent** (via worker) reads proposals for quality certification
- **Slack messages** reference proposal data in company update messages

### 5 Fatal Flaws

1. **No deal_side handling.** The proposal engine is hardcoded for sell-side: "We represent the owners of [company]" language, buyer outreach scripts, buyer profiles. For Weiser Concrete and Design Precast (buy-side clients), this generates exactly the wrong deliverables. There is no check for deal_side before generation, and no alternate prompt for buy-side proposals. This is not a theoretical risk -- it already happened.

2. **Single-LLM quality scoring is self-grading.** The LLM that generates the proposal also generates its own quality_score (0-100). This is the fox guarding the henhouse. A model that hallucinates a perfect narrative will also give itself a 95. The certifier agent exists but runs separately and asynchronously -- proposals can be viewed and acted on before certification completes.

3. **Hardcoded deal list in run_all_deals().** The function that processes all deals has a static Python list of 6 company names. When a new deal is signed, someone must edit the Python file. This is fragile, non-scalable, and means the proposal engine cannot be triggered dynamically for new companies. The orchestrator queues work, but the proposal engine's batch function ignores the queue.

4. **MULTIPLES_FILE points to the wrong project.** `MULTIPLES_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/data-export/market_multiples.json")` -- this references the OLD dossier-pipeline project, not master-crm. If that file does not exist (which is likely on a clean deploy), it silently falls back to hardcoded defaults. Those defaults may be stale or wrong for specific verticals.

5. **JSON parsing is brittle and fails silently.** When Claude CLI returns a response that is not valid JSON (which happens regularly with large structured prompts), the engine tries to extract JSON between the first `{` and last `}`. If that fails too, it creates a `{"raw_content": result, "quality_score": 0}` -- meaning a proposal with quality 0 gets stored in the database. There is no alert, no retry with a cleaner prompt, no notification that the proposal is garbage.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No deal_side handling:**
- Enhancement A: Add a `deal_side` check at the top of generate_proposal(). If deal_side is "buy_side", use a completely different prompt that generates target company profiles and owner outreach scripts (instead of buyer profiles and buyer outreach scripts).
- Enhancement B: Create two separate prompt templates: `SELL_SIDE_PROMPT` and `BUY_SIDE_PROMPT`. The proposal engine selects the right one based on the deal_side field in the proposals or targets table. Log which template was used.

**Flaw 2 — Self-grading quality score:**
- Enhancement A: After Claude CLI generates the proposal, immediately send the JSON to a DIFFERENT LLM (DeepSeek or GPT-4o Mini) with a certification prompt. The second LLM's quality score is the one that gets stored. This is the "you can't grade your own homework" principle already documented in the agent design.
- Enhancement B: Implement a rule: proposals with quality_score < 80 cannot appear in client-facing pages or trigger engagement engine work. They sit in draft until the certifier agent runs and either upgrades or flags them.

**Flaw 3 — Hardcoded deal list:**
- Enhancement A: Replace run_all_deals() with a database query: `SELECT DISTINCT company_name FROM proposals WHERE status = 'needs_refresh' OR (status = 'draft' AND quality_score < 50)`. The proposal engine processes whatever the database says needs work, not a static list.
- Enhancement B: Integrate with the orchestrator queue. The orchestrator already creates queue items -- add a 'proposal_generator' agent to the worker's AGENTS dict that calls generate_proposal() for queued companies.

**Flaw 4 — Wrong file path for multiples:**
- Enhancement A: Move market_multiples.json to `~/Projects/master-crm/data/market_multiples.json` and update MULTIPLES_FILE. Add a startup check that logs a warning if the file is missing or older than 30 days.
- Enhancement B: Store market multiples in a Supabase table `market_multiples` with columns: vertical, ebitda_low, ebitda_med, ebitda_high, source, updated_at. The proposal engine queries the table instead of a file. This makes multiples editable without code changes and auditable.

**Flaw 5 — Brittle JSON parsing:**
- Enhancement A: Add a retry mechanism: if JSON parsing fails, send a repair prompt to the LLM: "The following text should be valid JSON but isn't. Fix it and return ONLY the corrected JSON: [raw output]". Try up to 2 repairs before falling back.
- Enhancement B: When a proposal is stored with quality_score = 0, immediately create a human_review_queue entry with status 'critical' and log an iMessage alert: "[Argus] Proposal generation failed for {company_name} -- JSON parse error. Needs manual review."

### 5 Toughest Questions for Ewing

1. For buy-side clients (Weiser, Design Precast), what does the "proposal" even look like? Is it a list of acquisition targets with profiles? A market landscape showing available businesses? Or a different format entirely?
2. When the quality_score is between 50-79, the guardrails say "send with honesty frame." But this is a PROPOSAL, not a letter. Should a mediocre proposal go to the client at all, or should it always be upgraded to 80+ before sharing?
3. The proposal includes a valuation range. If a prospect sees "$3M-$5M" and their actual value is $8M, is that a deal-killer or a conversation-starter? Should the system err high, err low, or refuse to show valuations below a confidence threshold?
4. Market multiples are currently static per vertical (e.g., HVAC always 3.5-7.0x EBITDA). Should multiples vary by geography, company size, or recency of comparable transactions? How much research investment is justified per company?
5. The "all about them, nothing about us" rule is clear for sell-side. For buy-side, the buyer IS the client. How do we frame the attack plan -- is it "all about the targets they should acquire" or "all about the buyer's growth strategy"?

---

## SYSTEM 3: Profile Engine

### What It Does
Transforms raw company data (from phone calls, transcripts, prior research) into a structured company profile with slider-bar fields, financial estimates with methodology disclosure, operational data, revenue mix breakdowns, top 3 strengths with evidence, valuation estimates, and market positioning analysis. Serves as the canonical structured data record that feeds proposals, data rooms, buyer targeting, and outreach scripts.

### Where It Gets Data
- **companies table** -> base company record
- **targets table** -> extra_fields (rich structured data)
- **dossier_final table** -> narrative, owner background, culture signals, valuation
- **proposals table** -> company_narrative, strengths, market analysis, valuation range, financial data
- **Known data argument** -> any data passed in from a call or manual entry
- **Claude CLI** -> $0.00 profile generation (primary)
- **OpenRouter (DeepSeek V3)** -> fallback LLM generation

### What Decisions It Makes
- Data source priority: known_data > proposal > dossier > db_data (later sources override earlier)
- Which LLM to use: Claude CLI first, DeepSeek V3 fallback
- Which fields to estimate vs. leave null (LLM decides based on available data)
- Quality score and data completeness percentage (self-assessed by LLM)

### What Output It Creates
- **Updated companies table** -> vertical, city, state, employee_count, year_founded
- **intelligence_cache row** -> key='company_profile', full JSON profile stored
- **Log entries** -> profile_engine.log with timings and data source inventory

### What Uses This Output Next
- **Meeting Engine** reads company_profile from intelligence_cache for meeting prep
- **Company Hub** reads company_profile for the aggregated view
- **Proposal Engine** could read it (but currently does its own data assembly independently)
- **Engagement Engine** reads profile data indirectly through proposals

### 5 Fatal Flaws

1. **Profile and Proposal engines duplicate data assembly.** Both engines independently query the same tables (companies, targets, dossier_final), merge the same data, and call the same LLMs. This creates two separate "truth" records that can diverge. The proposal might say revenue is $3M while the profile says $5M because they ran at different times or merged data in different priority orders.

2. **ILIKE fuzzy matching can hit wrong companies.** Every query uses `WHERE company_name ILIKE %{company_name}%`. If you search for "Air", you might match "Air Control", "Air Quality Systems", and "Airtight HVAC". The `LIMIT 1` means you get whichever the database returns first, which may not be the right company. This is a silent data contamination vector.

3. **intelligence_cache has no versioning.** The profile is stored with `ON CONFLICT DO NOTHING`. This means if a profile already exists, a new (potentially better) profile is silently discarded. There is no way to see how a profile changed over time, no way to revert to a prior version, and no way to know if the current profile is stale.

4. **No validation of LLM output against known facts.** The LLM generates estimated revenue, estimated EBITDA, valuation ranges -- but these are not cross-checked against the actual data that was fed in. If the known_data says 11 employees and the LLM outputs 50 employees in the profile, nobody catches it.

5. **build_profiles_for_all_proposals() is the only batch entry point.** It queries proposals for company names. Companies that exist in targets or companies tables but do NOT have a proposal yet will never get a profile. This creates a chicken-and-egg problem: you need a profile to build a good proposal, but you need a proposal to trigger profile building.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Duplicate data assembly:**
- Enhancement A: Make the profile engine the SINGLE source of structured data. Proposal engine should READ from the profile (intelligence_cache), not re-assemble from raw tables. Profile engine runs first, proposal engine consumes its output.
- Enhancement B: Create a shared `data_assembly.py` module that both engines use. This eliminates divergent merge logic and ensures one priority order.

**Flaw 2 — ILIKE fuzzy matching:**
- Enhancement A: Query by company_id (UUID) instead of company_name wherever possible. The proposal already has target_id and company_id -- use those for joins.
- Enhancement B: When ILIKE is necessary, add a count check: if more than one row matches, log a warning and use the one with the highest quality_score or most recent updated_at. Never silently pick the first match.

**Flaw 3 — No intelligence_cache versioning:**
- Enhancement A: Change `ON CONFLICT DO NOTHING` to `ON CONFLICT DO UPDATE` or use an INSERT with a version number. Add a `version` column to intelligence_cache and keep all historical versions.
- Enhancement B: Create a `profile_versions` table that stores every profile generation with a timestamp. The intelligence_cache always holds the latest, but history is preserved.

**Flaw 4 — No LLM output validation:**
- Enhancement A: After the LLM generates the profile, run a simple sanity check: for every field that was in the known_data or db_data, compare it against the LLM output. If the LLM changed a known fact by more than 50%, flag it as NEEDS_REVIEW.
- Enhancement B: Add a "fields_changed_from_source" list to the profile output. The profile engine compares LLM output vs input data and logs every field where the LLM deviated from the source data.

**Flaw 5 — Proposals-only batch entry:**
- Enhancement A: Change the batch query to: `SELECT DISTINCT company_name FROM companies WHERE entity = 'next_chapter' UNION SELECT DISTINCT company_name FROM targets WHERE entity = 'next_chapter'`. This catches all NC companies, not just those with proposals.
- Enhancement B: Integrate with the orchestrator. Add a 'profiler' agent to the queue. Orchestrator detects companies without profiles and queues profile generation before proposal generation.

### 5 Toughest Questions for Ewing

1. When Mark gets off a call and says "revenue is about $5M", but the Exa search found "estimated 15 employees x $150K = $2.25M" -- which number wins? Should the system always trust the human input, or flag the discrepancy?
2. How often should profiles be regenerated? Every time new data comes in? Weekly? Only when a meeting is scheduled?
3. Should the profile show Mark a "data confidence" rating per field? Like "Revenue: $5M (HIGH -- owner stated on call)" vs "Revenue: $3M (LOW -- estimated from employee count)"?
4. For the slider-bar fields (commercial_pct, residential_pct, inbound_pct), what happens when the prospect later corrects these during the data room interaction? Does the profile auto-update and cascade changes to proposals?
5. The profile generates "fields_missing" and "fields_estimated" lists. Should there be a minimum completeness threshold before a profile is considered "ready" for downstream engines? What percentage is the floor -- 50%? 70%?

---

## SYSTEM 4: Engagement Engine

### What It Does
Activates when a client signs an advisory agreement. Takes a proposal_id, loads the complete proposal + buyer list, runs DNC checks on all buyers, generates per-buyer outreach scripts (letter, email, call, LinkedIn) for the top 10 buyers via Claude CLI, creates a 30/60/90-day execution timeline, and updates the proposal status to "engagement_active". Designed to be the bridge between proposal acceptance and active deal marketing.

### Where It Gets Data
- **proposals table** -> full proposal record including company data, vertical, location
- **engagement_buyers table** -> buyer list with fit scores, types, contact info
- **do_not_call table** -> universal DNC check (phone + company name)
- **Claude CLI** -> $0.00 script generation per buyer + timeline generation

### What Decisions It Makes
- Which buyers are DNC-clear (blocks by phone AND company name match)
- Which buyers get full scripts (top 10 by fit_score)
- Script content: letter, email, call script, LinkedIn message per buyer
- 30/60/90 day execution timeline phases and actions

### What Output It Creates
- **engagement_buyers updates** -> approach_script (JSON with 4 script types), status = 'scripted'
- **proposals update** -> status = 'engagement_active', client_signed_at = now()
- **intelligence_cache row** -> key='engagement_plan', full admin data stored
- **Log entries** -> engagement_engine.log

### What Uses This Output Next
- **Company Hub** reads engagement_buyers for buyer table display and script samples
- **Meeting Engine** reads buyer data for meeting prep context
- **Web Server** serves buyer scripts via the company page tree
- **Dashboard** reads engagement_active status for pipeline overview

### 5 Fatal Flaws

1. **No buyer list generation -- assumes buyers already exist.** The engagement engine reads from engagement_buyers but never CREATES buyer records. There is no system that populates the engagement_buyers table. If generate_proposal() does not also run buyer research, the engagement engine activates with zero buyers and generates zero scripts. The buyer research pipeline is a critical gap.

2. **DNC check is insufficient.** The check only looks for exact phone match and ILIKE company name match. It does not check: owner personal phone, alternate company names, subsidiary names, individual contact DNC requests, or email opt-outs. A buyer who said "never contact me" via email but whose phone is not in the DNC table will get called.

3. **Only top 10 buyers get scripts -- no queue for the rest.** The engine generates scripts for `clear_buyers[:10]` and stops. If there are 50 clear buyers, 40 get nothing. There is no background job to generate scripts for buyers 11-50. The speed-to-production rule says "generate v1 immediately, queue the rest" -- but there is no queue mechanism.

4. **activate_all_proposals() triggers on 'needs_review' status.** The function queries `WHERE status IN ('certified', 'needs_review')`. This means proposals that the certifier flagged as NEEDS_REVIEW -- meaning they have known quality issues -- get engagement-activated. This directly violates the "never send low quality" guardrail.

5. **No deal_side awareness in script generation.** The script prompt says "contacting a potential BUYER about acquiring {company}." For buy-side clients (Weiser, Design Precast), the scripts should be contacting potential SELLERS about selling TO the client. The entire framing is inverted for buy-side deals.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No buyer list generation:**
- Enhancement A: Build a buyer_research.py module that: (1) takes a company + vertical + geography, (2) searches Exa for acquirers in the vertical, (3) identifies PE firms, strategic buyers, and competitor roll-ups, (4) stores results in engagement_buyers with fit scores. Call this BEFORE engagement activation.
- Enhancement B: Add a pre-check in activate_engagement(): if `SELECT count(*) FROM engagement_buyers WHERE proposal_id = %s` returns 0, abort activation and log "No buyers found -- run buyer research first."

**Flaw 2 — Insufficient DNC check:**
- Enhancement A: Expand do_not_call to include: email addresses, LinkedIn URLs, and a `block_all_channels` flag. Check all contact methods, not just phone.
- Enhancement B: Add a `dnc_check_comprehensive()` function that checks phone, email, company_name (with fuzzy matching), and any linked contact records. Log which specific check triggered the block.

**Flaw 3 — Only top 10 get scripts:**
- Enhancement A: After generating scripts for the top 10, create agent_queue entries for buyers 11-50 with agent_name='script_generator'. The worker processes these in the background.
- Enhancement B: Generate a lighter "approach summary" (2 sentences, not full scripts) for buyers 11-50 immediately. Full scripts get queued as background work.

**Flaw 4 — Activating needs_review proposals:**
- Enhancement A: Change the query to `WHERE status = 'certified' AND quality_score >= 80`. Remove 'needs_review' from the activation criteria entirely.
- Enhancement B: Add a pre-activation quality gate: `if quality_score < 80: log("Skipping {company} -- quality {quality} below threshold"); continue`.

**Flaw 5 — No deal_side handling:**
- Enhancement A: Check deal_side before generating scripts. If buy_side, use a different prompt: "Generate scripts for contacting a potential SELLER about selling their company to {client_company}."
- Enhancement B: Create separate prompt templates: SELL_SIDE_BUYER_SCRIPT and BUY_SIDE_TARGET_SCRIPT. The engagement engine selects the right template based on the proposal's deal_side field.

### 5 Toughest Questions for Ewing

1. When a buyer appears on multiple seller lists (e.g., CMC Group is a buyer for both Air Control and Weiser), should the engagement engine coordinate outreach or treat them as independent? What does the "multi-deal leverage" pitch look like in practice?
2. What is the minimum number of buyers needed before activation is worthwhile? Is 3 enough? 10? Should the system refuse to activate with fewer than N buyers?
3. For the 30/60/90 timeline, who actually executes each step? Is it Mark manually sending letters? Salesfinity auto-dialing? The system auto-sending emails? The timeline says "letter campaign to top 10" but does not specify the execution mechanism.
4. Should DNC'd buyers still appear in the client-facing view with the note "restricted for our outreach -- you may contact independently"? Or should they be completely hidden from the client?
5. When a buyer responds positively, what triggers the next stage? Is there a webhook from email? A manual status update? A Fireflies transcript signal? How does the system know a buyer said yes?

---

## SYSTEM 5: Meeting Engine

### What It Does
Generates per-meeting custom HTML preparation pages with agenda, objectives, talking points, questions to ask, information to share, danger zones, success criteria, and next steps (positive and negative paths). Pulls all available data for a company (proposal, profile, buyers, intelligence cache) and uses Claude CLI to synthesize meeting-specific prep content. Each meeting page is tailored by meeting_type (discovery, follow-up, closing, etc.).

### Where It Gets Data
- **proposals table** -> proposal data (narrative, financials, vertical, city, state, owner)
- **intelligence_cache** -> company_profile and other intelligence entries
- **engagement_buyers table** -> buyer list with fit scores and statuses (via proposals join)
- **companies table** -> company_id for intelligence_cache joins
- **Claude CLI** -> $0.00 meeting content generation

### What Decisions It Makes
- What data to include (truncates to 6000 chars to fit LLM context)
- Meeting content structure based on meeting_type parameter
- Fallback to default content when Claude CLI fails
- File naming and storage locations

### What Output It Creates
- **HTML file** -> saved to data/meetings/{slug}_{date}_{type}.html
- **HTML copy** -> saved to ~/Downloads/master-crm-proposals/{same filename}
- **Log entries** -> meeting_engine.log

### What Uses This Output Next
- **Web Server** could serve meeting pages (routing exists in server.py)
- **Slack messages** include meeting prep links in company updates
- **Company Hub** lists meeting files in the files section

### 5 Fatal Flaws

1. **No storage in Supabase -- HTML files only.** Meeting pages exist only as local HTML files. If the Mac mini dies, all meeting pages are lost. There is no database record of what meetings were prepped, when, or what content was generated. No version history, no ability to regenerate, no audit trail.

2. **Data truncation at 6000 chars is arbitrary and lossy.** The entire company data dict is JSON-serialized and truncated at 6000 characters before being sent to Claude CLI. For data-rich companies with long narratives and many buyers, critical information gets silently dropped. The LLM generates meeting prep based on incomplete data without knowing what was cut.

3. **Meeting type is a free-text string with no validation.** The engine accepts any string for meeting_type ("discovery", "follow-up", "closing", etc.) but there is no enum, no list of valid types, and no type-specific behavior beyond the word appearing in the prompt. A typo like "disovery" produces a generic meeting page with no error.

4. **No calendar integration.** Meeting pages are generated manually by calling generate_meeting_page(). There is no trigger from Google Calendar, no automatic prep when a meeting is scheduled. The Listener agent design document describes calendar-triggered meeting prep, but it is not implemented.

5. **No post-meeting workflow.** The meeting page has "next steps if positive" and "next steps if negative" sections, but these are just text. There is no system to track which path was taken after the meeting, no trigger to update the pipeline status, no automatic follow-up generation.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No Supabase storage:**
- Enhancement A: Store meeting content in a `meeting_pages` table with columns: company_name, meeting_type, meeting_date, content_json, html, created_at. HTML files become a cache, not the primary store.
- Enhancement B: Use the existing page_versions table (if it exists) to store meeting pages as versioned content. Each regeneration creates a new version.

**Flaw 2 — Data truncation:**
- Enhancement A: Instead of dumping the entire data dict, build a meeting-type-specific data summary. Discovery meetings need different data than closing meetings. Extract and format only the relevant fields.
- Enhancement B: Use a two-pass approach: first LLM call identifies which data fields are most relevant for this meeting type, second call generates the prep using only those fields (no truncation needed).

**Flaw 3 — No meeting type validation:**
- Enhancement A: Define a MEETING_TYPES enum: "discovery", "qualification", "proposal_review", "closing", "follow_up", "check_in". Each type has a specific prompt template and required data fields. Reject unknown types with a clear error.
- Enhancement B: Add type-specific sections: discovery gets more questions, closing gets objection handling and contract options, follow_up gets action item tracking.

**Flaw 4 — No calendar integration:**
- Enhancement A: The Listener agent (when built) should watch Google Calendar for new events with prospect company names. When detected, auto-trigger meeting_engine.generate_meeting_page() with the appropriate type.
- Enhancement B: Add a simple cron job that checks Google Calendar API every hour for meetings in the next 48 hours, cross-references company names with the proposals table, and generates any missing meeting pages.

**Flaw 5 — No post-meeting workflow:**
- Enhancement A: Add a "meeting outcome" form to the meeting page. Mark or Ewing can click "Positive", "Negative", or "Follow-up needed" after the meeting. This updates the pipeline status and triggers the appropriate next play.
- Enhancement B: Integrate with Fireflies: when a meeting transcript becomes available, auto-extract the outcome and next steps, update the company profile, and trigger follow-up generation.

### 5 Toughest Questions for Ewing

1. How far in advance should meeting prep be generated? 24 hours? 1 hour? Should it regenerate if new data comes in between generation and the meeting?
2. Should the meeting page be viewable on a phone during the meeting itself (responsive design, key talking points at the top, searchable)?
3. For joint meetings where both Mark and Ewing attend, should the prep page include role assignments (who covers which topics)?
4. If a meeting is rescheduled, should the system regenerate the prep page (in case new data arrived since the original) or keep the original?
5. Should meeting prep pages be sent to the attendee via iMessage 30 minutes before the meeting? Or is that too much automation?

---

## SYSTEM 6: Company Hub

### What It Does
Generates a single-page aggregation view for each company that links every asset ever created: proposal, data room, meeting pages, buyer list, profile, emails, call scripts, timeline, intelligence, costs, and pipeline history. Functions as the "one URL per company" destination for internal use. Supports admin view (see everything) and client view (curated subset, not yet implemented).

### Where It Gets Data
- **companies table** -> base company record + total_cost_usd + cost_log_entries
- **contacts table** -> all contacts linked to company_id
- **proposals table** -> highest quality proposal for the company
- **engagement_buyers table** -> all buyers for the company's proposal
- **intelligence_cache** -> company_profile and engagement_plan entries
- **play_executions table** -> play code, content, status, quality, date
- **targets table** -> pipeline status, research/validation/letter completion dates, errors
- **step_log table** -> pipeline history with step type, tool, status, cost, date
- **dossier_final table** -> owner info, narrative, letter HTML, scripts, verdict
- **Local filesystem** -> HTML files in data/proposals/, data/data-rooms/, data/meetings/

### What Decisions It Makes
- Which data to display (truncates long fields at 500-800 chars)
- Status badge colors based on proposal status and cost thresholds
- Which outreach script sample to show (first buyer with approach_script)
- File matching: uses slug and first word of company name to find related files

### What Output It Creates
- **HTML file** -> saved to data/company-hubs/{slug}-hub.html
- **HTML copy** -> saved to ~/Downloads/master-crm-proposals/{slug}-hub.html
- **Log entries** -> stdout with timestamp

### What Uses This Output Next
- **Web Server** serves company pages via /company/{slug} (but server.py generates its own view, not the hub HTML)
- **Slack messages** include company hub links
- **Auto-refresh** regenerates hubs after other engines produce output

### 5 Fatal Flaws

1. **Server.py renders its own company view, making the hub HTML redundant.** The web server at server.py has its own complete company page renderer with sidebar, dark theme, buyer tables, scripts, etc. The company_hub.py generates a completely separate HTML file. These two views can diverge -- server.py reads live data, hub HTML is a snapshot from generation time. Users get different information depending on whether they visit the URL or open the file.

2. **File matching is unreliable.** The code searches for local files using `if slug in f.lower() or company_name.split()[0].lower() in f.lower()`. "Air" matches "Air Control" but also "Airtight HVAC". "Design" matches "Design Precast" but also "Designer Flooring". This can link the wrong company's files to a hub.

3. **No client view implementation.** The guardrails require admin/client dual views. The hub is admin-only -- it shows everything including internal strategy, all buyer data, cost tracking, and pipeline errors. There is no client-facing version, no toggle, no `admin_only` field filtering.

4. **No real-time data.** The hub is a static HTML snapshot. Data changes between hub regeneration cycles are invisible. If a buyer responds or a new contact is added, the hub still shows the old state until auto_refresh runs. There is no timestamp showing when the hub was last generated, so users cannot tell how stale it is.

5. **cost_log_entries relies on a field that may not exist.** The hub reads `cost_log_entries` from the companies table, expecting it to be a list. But cost tracking is done through the `cost_log` table, not a field on companies. If companies.cost_log_entries is null (which it likely is), the hub silently shows no cost data even though cost records exist in cost_log.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Redundant with server.py:**
- Enhancement A: Deprecate company_hub.py entirely. Make server.py the single source of company views. It already reads live data and has a richer UI.
- Enhancement B: Keep company_hub.py but only for generating offline/export HTML files (for email attachments, PDF generation). Server.py handles all browser views.

**Flaw 2 — File matching:**
- Enhancement A: Store file references in a `company_files` table with company_id foreign key. When a file is generated, log it with the correct company_id. Hub reads from the table, not filesystem glob.
- Enhancement B: Use the full slug for matching (not first word). Add a minimum slug length requirement and exact-prefix matching.

**Flaw 3 — No client view:**
- Enhancement A: Add `is_client_visible` boolean to every data field in the hub. Admin sees all; client view filters. Implement as a URL parameter: /company/{slug}?view=client.
- Enhancement B: Generate two separate HTML files: {slug}-hub-admin.html and {slug}-hub-client.html. The client version omits: pipeline history, cost tracking, internal notes, buyer DNC status, strategy sections.

**Flaw 4 — No real-time data:**
- Enhancement A: Add a "Generated at: {timestamp}" banner to the hub. Add a "Refresh Now" button that triggers regeneration via the web server API.
- Enhancement B: Switch from static HTML to server.py database-backed views (per Flaw 1 fix). Server.py already reads live data on every request.

**Flaw 5 — Missing cost data:**
- Enhancement A: Query `cost_log` table directly instead of relying on companies.cost_log_entries. `SELECT sum(cost_usd), count(*) FROM cost_log WHERE entity = %s AND record_id = %s`.
- Enhancement B: Create a view or materialized view `company_costs` that aggregates cost_log per company. Hub reads from the view.

### 5 Toughest Questions for Ewing

1. Is the company hub meant to replace the web server's company view, or are they different tools for different purposes (hub = export, server = live view)?
2. For the client view, what EXACTLY should be visible? Proposal narrative yes, valuation range yes/no (configurable per company), buyer names yes/no, buyer count yes, individual scripts no -- what is the full list?
3. Should the hub have a "changelog" section showing what data changed since the last time Mark viewed it?
4. Should each company hub have a unique shareable URL (with optional password protection) for sending to clients?
5. How many companies will realistically be active at once? 6? 20? 50? This affects whether a sidebar navigation approach scales or becomes unwieldy.

---

## SYSTEM 7: Dashboard

### What It Does
Generates a 9-section "Monday Morning Dashboard" HTML page that provides an executive overview across all entities. Sections: campaigns, proposals by status, pending reviews, agent performance (7-day), outbound activity, pipeline stages, problems (low quality + failed jobs), database health, and spend by vendor/entity.

### Where It Gets Data
- **campaigns table** -> campaign_id, entity, name, is_active
- **proposals table** -> company_name, status, quality_score
- **human_review_queue table** -> pending review count and breakdown by type
- **agent_runs table** -> agent performance (count, success rate, avg cost) for last 7 days
- **play_executions table** -> plays executed in last 7 days
- **sent_log table** -> items sent in last 7 days
- **engagement_buyers table** -> total buyers and scripted buyers
- **agent_queue table** -> failed jobs with error messages
- **pg_stat_user_tables** -> total row count
- **companies, contacts, targets tables** -> record counts
- **cost_budget table** -> entity budgets and spend
- **cost_log table** -> spend by vendor for last 7 days

### What Decisions It Makes
- Color coding: green/orange/red for budget utilization percentages
- Color coding for proposal status (certified=green, active=orange, other=red)
- Problem identification: proposals with quality < 70, failed queue items

### What Output It Creates
- **HTML file** -> saved to data/dashboards/dashboard_{date}.html
- **HTML copy** -> saved to ~/Downloads/master-crm-proposals/dashboard_{date}.html

### What Uses This Output Next
- **Web Server** serves dashboard via /dashboard route (but may render its own version)
- **Auto-refresh** regenerates dashboard after any engine output
- **Slack messages** include dashboard link in daily briefing

### 5 Fatal Flaws

1. **Dashboard is a static snapshot, not live.** Ewing opens his laptop Monday morning and sees a dashboard generated at 3am. Any changes between 3am and 9am are invisible. There is no auto-refresh on page load, no "last updated" timestamp, no live data. For a "command center," this defeats the purpose.

2. **Missing 4 of the 9 specified sections.** The guardrails specify: (1) campaigns to RUN, (2) quality tuning, (3) new rules needed, (4) agent performance, (5) outbound activity, (6) revenue metrics, (7) problem identification, (8) agent requests, (9) spend. The current dashboard has campaigns, proposals, reviews, agent perf, outbound, pipeline stages, problems, and budget. Missing entirely: "new rules needed" (questions from last week's runs), "agent requests" (agents requesting tools/skills), and "revenue metrics" (contracts signed, revenue closed). "Quality tuning" is partially covered by proposals.

3. **No entity filtering.** The dashboard shows everything across all entities. Ewing runs NC + AND, Mark runs all 3, John runs NC + RU. There is no per-person or per-entity view. When Ewing looks at the dashboard, he sees RevsUp data he does not manage, and cannot quickly filter to "show me only AND Capital."

4. **Budget utilization is read from cost_budget but never reset.** The `spent_usd` column in cost_budget is presumably accumulated. But there is no daily reset mechanism. If budgets are "daily" (as the `period = 'daily'` filter suggests), spent_usd must be reset to 0 at midnight. If it is not reset, the dashboard shows cumulative spend vs daily budget, which is meaningless.

5. **No actionable buttons.** The dashboard shows information but offers no actions. "Campaigns to RUN" shows campaigns but has no "Activate" button. "Pending reviews" shows a count but has no "Review now" link. "Problems" lists issues but has no "Fix" or "Investigate" action. The dashboard is a report, not a command center.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Static snapshot:**
- Enhancement A: Make the dashboard a server.py route that queries the database live on every request. No file generation needed. Add a "Last refreshed: now" timestamp.
- Enhancement B: Add auto-refresh meta tag: `<meta http-equiv="refresh" content="300">` (refresh every 5 minutes). Or use JavaScript to poll for updates.

**Flaw 2 — Missing sections:**
- Enhancement A: Add "New Rules Needed" section that queries human_review_queue for items of type 'rule_proposal' or 'question'. Add "Agent Requests" section that queries a new `agent_requests` table. Add "Revenue Metrics" that queries proposals for client_signed_at (signed deals) and any revenue tracking.
- Enhancement B: Create a `dashboard_sections` table that defines what each section queries. New sections can be added via database config, not code changes.

**Flaw 3 — No entity filtering:**
- Enhancement A: Add entity filter buttons at the top: [All] [NC] [AND] [RU]. Click to filter all sections. Store preference in a cookie or URL parameter.
- Enhancement B: Add person-based preset filters: "Ewing's View" (NC + AND), "Mark's View" (all), "John's View" (NC + RU). One click to see only relevant data.

**Flaw 4 — Budget never resets:**
- Enhancement A: Add a daily cron job that resets cost_budget.spent_usd to 0 at midnight. Or calculate daily spend dynamically: `SELECT sum(cost_usd) FROM cost_log WHERE entity = %s AND created_at >= CURRENT_DATE`.
- Enhancement B: Change the dashboard to calculate spend dynamically from cost_log rather than reading a cached total. This ensures accuracy regardless of reset timing.

**Flaw 5 — No actionable buttons:**
- Enhancement A: Add action buttons to each section: "Activate Campaign", "Review Item", "Investigate Problem". These POST to server.py API endpoints that perform the action.
- Enhancement B: Add links to the relevant detail pages: campaign config page, review queue page, problem detail page. Even without full CRUD, linking to context is better than a dead-end display.

### 5 Toughest Questions for Ewing

1. Should the dashboard be the LANDING PAGE of the web server (first thing you see at localhost:8080) or a separate route? Currently the landing page shows company cards.
2. What "revenue metrics" should the dashboard track? Is it just proposal pipeline (draft/certified/active/signed) or actual dollar values (fees earned, deals closed)?
3. Should the dashboard show a "health check" for the orchestrator/worker/watchdog? If the worker has been down for 2 hours, that needs to be visible.
4. Is there a mobile version needed? The Monday morning check might happen from a phone.
5. What time horizon matters? The current dashboard shows 7-day windows. Should it also show month-over-month trends? Year-to-date?

---

## SYSTEM 8: Version Engine

### What It Does
Designed to provide page versioning and history for all generated content (proposals, data rooms, meeting pages, attack plans). Every time a page is regenerated, a new version is stored with the old version preserved. Users can compare versions, revert to previous versions, and see what changed. A "stale" flag system marks pages for lazy rebuild when rules change.

### Where It Gets Data
- **page_versions table** (if it exists) -> version records with page_type, company reference, content, version number, generated_at
- **Server.py** checks for page_versions table existence via information_schema

### What Decisions It Makes
- Whether to show a version warning banner (when viewing non-latest version)
- Whether to trigger lazy rebuild (when is_stale = true)
- Version numbering (sequential per page)

### What Output It Creates
- **page_versions table rows** -> versioned content snapshots
- **Version UI** -> dropdown to select versions, comparison view, "Load Current Version" button

### What Uses This Output Next
- **Web Server** reads page_versions for version history display and comparison
- **Feedback Loop** (designed) would create new versions when feedback is incorporated

### 5 Fatal Flaws

1. **Not yet fully implemented.** Server.py has a `page_versions_exist()` function that checks if the table exists, implying it may not. The version_controls CSS exists in server.py, but the actual versioning logic (creating versions on regeneration, version comparison, revert) is not visible in any engine code. No engine currently writes to page_versions.

2. **No diff/comparison capability.** The design calls for showing what changed between versions, but there is no text diff engine. HTML comparison is complex (structural changes, content changes, style changes). Without this, version history is just a list of snapshots with no way to see what actually changed.

3. **Lazy rebuild depends on a stale flag that nothing sets.** The design says "rule change sets all pages to stale, server rebuilds on view." But there is no mechanism to detect rule changes, no code that sets is_stale = true, and no code in the server that checks is_stale and triggers rebuild.

4. **No rollback safety.** If a version is reverted to, what happens to the data that was generated by the newer version? If version 3 of a proposal changed the valuation range and engagement scripts were generated from that range, reverting to version 2 creates inconsistency across all downstream outputs.

5. **Storage cost of full HTML snapshots.** Each version stores the complete HTML content. With 20 companies, 5 page types, and frequent regeneration, this could grow to thousands of full HTML documents in the database. There is no cleanup policy, no expiration, no compression.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Not yet implemented:**
- Enhancement A: Add a `save_version()` function to a shared `versioning.py` module. Every engine calls `save_version(company_name, page_type, content)` after generating output. This is a 20-line function that inserts into page_versions with auto-incrementing version numbers.
- Enhancement B: Start with just proposals. Before generating a new proposal, copy the current content to page_versions as a snapshot. This is the minimum viable versioning.

**Flaw 2 — No diff capability:**
- Enhancement A: Store structured JSON alongside HTML. Diff the JSON (field-by-field comparison) rather than the HTML. Show changed fields highlighted.
- Enhancement B: Use Python's difflib to generate a side-by-side text diff of the stripped-text content (HTML tags removed). Not perfect but serviceable for v1.

**Flaw 3 — Stale flag not connected:**
- Enhancement A: Create a `rules_version` integer in a config table. When a guardrail or template changes, increment rules_version. page_versions stores the rules_version it was generated under. If page rules_version < current rules_version, the page is stale.
- Enhancement B: Simpler: add a `last_regenerated_at` timestamp to page_versions. If any source data (proposal, profile, buyer list) has `updated_at > last_regenerated_at`, the page is stale.

**Flaw 4 — No rollback safety:**
- Enhancement A: Rollback creates a NEW version (version N+1) with the content of the old version. It never deletes. This preserves the full history and makes it clear what happened.
- Enhancement B: Add a "cascade refresh" option to rollback: reverting a proposal also regenerates all dependent pages (engagement scripts, meeting prep) from the reverted content.

**Flaw 5 — Storage cost:**
- Enhancement A: Store only the JSON content in page_versions. HTML can be regenerated from JSON on demand. This reduces storage by ~80%.
- Enhancement B: Keep only the last 10 versions per page per company. Older versions are archived to a separate table or deleted.

### 5 Toughest Questions for Ewing

1. How far back does version history need to go? Is it useful to see the very first proposal draft for a company, or only the last 5 versions?
2. When Mark edits a proposal section, should that create a new version automatically, or should there be an explicit "save version" action?
3. Should version history be visible to clients in the data room, or is it admin-only? (Seeing 7 revisions might reduce confidence.)
4. If a rule change affects 20 companies' pages, should they all rebuild immediately or use lazy rebuild? The design says lazy, but stale pages could be embarrassing if someone views them before rebuild.
5. Is there value in version-level commenting? ("Why was this changed?" notes on each version for audit trail.)

---

## SYSTEM 9: Research Transparency

### What It Does
Creates an "inside-out view" of the research process for each company. Catalogs every research method available (Exa search, Google Places, Clay enrichment, LLM estimation, etc.), tracks which methods were actually executed for each company, what they found, what they cost, and what confidence level the results have. Generates per-company HTML pages showing the full research trail -- what was searched, what was found, what was missed, and how much it cost.

### Where It Gets Data
- **research_methods table** -> catalog of all known research techniques (17 seeded methods)
- **research_executions table** -> per-company execution records (method, query, result, cost, confidence)
- **Supabase REST API** -> all database operations via HTTP (not direct PostgreSQL)
- **Hardcoded COMPANY_DATA dict** -> 6 companies with vertical, city, state, owner, revenue, employees, buyer file references

### What Decisions It Makes
- Which research methods to seed (17 predefined techniques)
- How to backfill execution records from existing data
- How to generate HTML showing the research trail per company
- Whether tables exist (verification before operations)

### What Output It Creates
- **research_methods table rows** -> 17 seeded research techniques with costs, tools, expected outputs
- **research_executions table rows** -> backfilled execution records per company
- **HTML files** -> per-company research transparency pages in data/research-views/
- **HTML copies** -> in ~/Downloads/master-crm-proposals/

### What Uses This Output Next
- **Company Hub** could link to research transparency pages (not currently wired)
- **Web Server** could serve research views (not currently routed)
- **Feedback Loop** (designed) would use research_methods to learn new techniques from human corrections

### 5 Fatal Flaws

1. **Research executions are backfilled, not live-tracked.** The system creates execution records retroactively from existing data, not in real-time as research happens. The proposal engine, profile engine, and worker do NOT write to research_executions when they actually run Exa searches or LLM calls. The transparency system shows what PROBABLY happened based on the data that exists, not what ACTUALLY happened.

2. **research_methods table is disconnected from actual code.** The seed methods include techniques like "Clay person enrichment" and "Glassdoor company info" that are not implemented in any engine. The methods list represents aspirational capability, not actual capability. This creates a false impression of research breadth.

3. **DDL execution via Supabase REST API is broken.** The `sb_sql()` and `run_ddl()` functions are empty stubs (`pass`). If the research_methods or research_executions tables do not exist, the system cannot create them. It relies on tables being pre-created via `supabase db push`, which is a manual step.

4. **Hardcoded company list limits scope.** COMPANY_DATA only includes 6 companies. Any new company added to the pipeline will not get research transparency backfill unless the code is manually updated. This is the same problem as the proposal engine's hardcoded deal list.

5. **No integration with the "reverse-engineer human method" feedback loop.** The feedback system design says when Mark corrects a fact, the system should ask "how did you find this?", replicate the method, and add it to the research methods library. This connection does not exist. Research methods are static seeds, not a growing library.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Not live-tracked:**
- Enhancement A: Add a `log_research_execution()` function that every engine calls when it runs a search. Parameters: company_name, method_code, query, result_summary, cost, confidence. The proposal engine calls this after every Exa search, the profile engine after every Claude CLI call.
- Enhancement B: Create a decorator or wrapper function for Exa searches and LLM calls that automatically logs to research_executions. This avoids modifying every engine individually.

**Flaw 2 — Aspirational vs actual methods:**
- Enhancement A: Add an `is_implemented` boolean to research_methods. Only show implemented methods in the transparency view. Mark aspirational methods as "planned."
- Enhancement B: Auto-detect which methods are actually used by scanning cost_log and step_log tables. If a method_code appears in execution logs, it is real. Otherwise, flag it as "defined but never executed."

**Flaw 3 — Broken DDL:**
- Enhancement A: Remove the DDL functions. Document the required table schemas in a migration file. Use `psycopg2` to create tables if they do not exist at startup (same pattern as the rest of the codebase).
- Enhancement B: Create a simple migration script (`migrate.py`) that checks for table existence and creates missing tables. Run it before the research transparency engine.

**Flaw 4 — Hardcoded company list:**
- Enhancement A: Query companies from the database: `SELECT DISTINCT company_name, vertical, city, state FROM proposals`. Backfill executions for all companies, not just 6.
- Enhancement B: Make backfill incremental: only process companies that do not already have execution records. Run as a daily job.

**Flaw 5 — No feedback integration:**
- Enhancement A: Create a `add_research_method()` function that the feedback loop calls when a new technique is discovered. Parameters: method_code, method_name, description, discovered_by, discovery_context.
- Enhancement B: When Mark corrects a fact via the commenting system, auto-create a `research_method_proposals` queue entry. A human reviews and either promotes it to a real method or discards it.

### 5 Toughest Questions for Ewing

1. Who is the audience for research transparency pages? Is it internal (Mark reviewing what research was done) or external (showing prospects "here is how we researched your company")?
2. Should the transparency page show failed research (searches that returned nothing)? This demonstrates thoroughness but might also show incompleteness.
3. How much detail should the research trail show? Full Exa result text? Just URLs? Confidence scores per fact? Source excerpts?
4. When a new research technique is added (e.g., Mark discovers a new data source), what is the workflow for adding it? Should it require code changes or be admin-configurable?
5. Should the cost per company be visible to the client? Some clients might appreciate knowing "$0.15 was spent researching your company" (shows effort), others might think it is cheap.

---

## SYSTEM 10: Step Tracking

### What It Does
Provides pipeline checkpoint tracking to prevent duplicate API spend. Every pipeline step (research, validation, letter generation, proposal generation) is logged with a status. Before executing a step, the system checks `is_step_done()` to avoid re-running expensive operations. Records are stored in the `step_log` table with step type, tool used, status, result summary, cost, and completion timestamp.

### Where It Gets Data
- **step_log table** -> existing step records for a given record_id
- **targets table** -> research_completed_at, validation_completed_at, letter_completed_at timestamps

### What Decisions It Makes
- Whether a step has already been completed for a given record
- Whether to skip or re-run based on completion status

### What Output It Creates
- **step_log table rows** -> one row per pipeline step execution
- **targets table updates** -> completion timestamps on milestone fields

### What Uses This Output Next
- **Orchestrator** checks completion timestamps to decide what work to queue
- **Company Hub** displays step history in the pipeline history section
- **Dashboard** could aggregate step data for throughput metrics

### 5 Fatal Flaws

1. **is_step_done() is referenced in guardrails but not consistently implemented in engines.** The NORTH-STAR document says "is_step_done() before every API call -- never duplicate spend." But the proposal engine does NOT call is_step_done() before Exa searches or LLM calls. It runs every step every time, regardless of whether it already ran. Same for profile_engine and meeting_engine.

2. **step_log is not the single source of truth.** Some engines log to step_log, some log to agent_runs, some only log to their own log files. There is no unified view of "what work was done for this company." A step might be logged in step_log but not agent_runs, or vice versa.

3. **No step dependency tracking.** The system does not enforce ordering. Nothing prevents generating a proposal before research completes, or activating engagement before certification. The orchestrator QUEUES in order, but if someone manually runs an engine, there are no guardrails.

4. **Targets table timestamps are coarse-grained.** `research_completed_at` is a single timestamp for all research. But research might include 5 separate Exa searches, a Google Places lookup, and 2 LLM extractions. If one of those fails, the timestamp is not set. But there is no way to know WHICH sub-step failed -- just that "research" is incomplete.

5. **No step retry with exponential backoff.** When a step fails, it gets logged as failed. The orchestrator has a `reset_stuck_items()` that retries after 30 minutes, but it retries with the same parameters, same prompt, same everything. There is no exponential backoff, no prompt variation, no escalation to a more capable model.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Not consistently implemented:**
- Enhancement A: Create a `@check_step` decorator that wraps every API call. `@check_step("exa_search", company_name)` checks step_log, skips if done, executes and logs if not.
- Enhancement B: Add step checking to the shared LLM caller functions (call_claude, call_openrouter). Before every LLM call, check if the same prompt for the same company was already processed.

**Flaw 2 — Not single source of truth:**
- Enhancement A: Consolidate step_log and agent_runs into one table. Every pipeline action goes to one place. Add an `agent_name` column to step_log.
- Enhancement B: Create a view `pipeline_activity` that unions step_log and agent_runs into one feed. Hub and dashboard query the view.

**Flaw 3 — No dependency enforcement:**
- Enhancement A: Add a `prerequisites` field to the step definitions. Before running "proposal_generation", check that "research" and "validation" are complete. Abort with a clear error if prerequisites are missing.
- Enhancement B: The orchestrator already implicitly enforces ordering via query conditions (e.g., targets with entity but no research). Formalize this into a `pipeline_stages` table with stage number, prerequisites, and status checks.

**Flaw 4 — Coarse timestamps:**
- Enhancement A: Use step_log as the granular tracker (individual sub-steps) and targets timestamps as the summary. `research_completed_at` is set only when ALL research sub-steps are done.
- Enhancement B: Add a `sub_step` column to step_log. "research/exa_company", "research/exa_owner", "research/google_places" -- each logged separately.

**Flaw 5 — No smart retry:**
- Enhancement A: Add retry_count and max_retries to step_log. On retry, vary the approach: attempt 1 = Claude CLI, attempt 2 = DeepSeek, attempt 3 = different prompt. Cap at 3 retries before marking as permanently failed.
- Enhancement B: Add exponential backoff to the worker: retry after 5 min, then 15 min, then 60 min. Log each retry with the modified approach.

### 5 Toughest Questions for Ewing

1. If a step was completed 30 days ago but new data has come in since, should it be re-run? What is the "freshness" threshold for considering a step stale?
2. Should step tracking be visible in the company hub? Knowing "research was done March 15" vs "research was done March 28" tells Mark how current the data is.
3. When a step fails after 3 retries, what should happen? Should it block the pipeline, silently skip, or escalate to human?
4. Is it worth tracking step COST separately from step STATUS? Knowing that "research for Air Control cost $0.15 across 3 Exa searches" helps with budget forecasting.
5. Should there be a "force re-run" button in the admin UI that ignores is_step_done() and re-executes a step? Useful when data sources are updated.

---

## SYSTEM 11: Cost Tracking

### What It Does
Accumulates per-record spend across all API calls. Every LLM call, Exa search, and external API request is logged with provider, operation, cost, and timestamp. Entity-level daily budgets are enforced by the orchestrator, which pauses paid API calls when an entity hits 100% of its daily cap (Claude CLI continues free). Budget alerts fire at 80% utilization.

### Where It Gets Data
- **cost_log table** -> individual API call records with api_name, cost_usd, entity, created_at
- **cost_budget table** -> daily budget caps per entity (NC: $5, AND: $3, RU: $1, System: $2)
- **Inline cost tracking** -> each engine maintains a `total_cost` variable and calls `log_cost()`

### What Decisions It Makes
- Whether an entity is over budget (pauses paid APIs at 100%)
- Whether to alert at 80% utilization
- Which costs to attribute to which entity

### What Output It Creates
- **cost_log table rows** -> individual API call records
- **cost_budget updates** -> spent_usd accumulation
- **Log messages** -> cost alerts in orchestrator and engine logs
- **Dashboard section** -> budget utilization display

### What Uses This Output Next
- **Orchestrator** checks budgets before queuing work for paused entities
- **Dashboard** displays budget utilization and spend by vendor
- **Company Hub** shows per-company total cost (if field exists on companies table)

### 5 Fatal Flaws

1. **Cost tracking is fragmented across engines.** The proposal engine has its own `total_cost` variable and `log_cost()` function. The worker has its own cost tracking. The profile engine does not track costs at all. There is no shared cost-tracking module that all engines use consistently.

2. **cost_budget.spent_usd has no reset mechanism.** The orchestrator reads `spent_usd` from cost_budget, but nothing resets it to 0 at midnight for daily budgets. If spent_usd is never reset, the budget appears exhausted permanently after the first day of operation, blocking all paid API calls forever.

3. **Claude CLI is $0.00 but not free in reality.** The system treats Claude CLI as costless because it runs through a subscription. But Claude CLI has rate limits, concurrent session limits, and time costs. Heavy Claude CLI usage can block other Claude Code sessions on the machine. The "free" designation hides real operational cost.

4. **No per-company cost allocation.** The cost_log table tracks entity-level costs, but there is no reliable way to attribute costs to specific companies. If the proposal engine generates proposals for 6 companies in a batch, the Exa costs are logged to the entity but not to individual companies.

5. **Budget caps are extremely low for production use.** NC: $5/day, AND: $3/day, RU: $1/day. A single company's proposal generation costs ~$0.05-$0.10 in Exa searches. If NC has 20 companies to process, that is $1-$2 in Exa alone. Adding DeepSeek validation, enrichment, and buyer research, $5/day is barely enough for 10-15 companies. This cap will throttle the pipeline severely at scale.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Fragmented cost tracking:**
- Enhancement A: Create a shared `cost_tracker.py` module with a single `log_api_cost(provider, operation, cost, entity, company_name=None)` function. All engines import and use this. It writes to cost_log AND updates cost_budget.spent_usd atomically.
- Enhancement B: Wrap the external API call functions (call_openrouter, exa_search) in the shared module so cost logging happens automatically, not manually.

**Flaw 2 — No budget reset:**
- Enhancement A: Add a daily cron job (or orchestrator startup check) that resets spent_usd to 0 for all daily budgets: `UPDATE cost_budget SET spent_usd = 0 WHERE period = 'daily' AND updated_at < CURRENT_DATE`.
- Enhancement B: Calculate daily spend dynamically in the orchestrator: `SELECT sum(cost_usd) FROM cost_log WHERE entity = %s AND created_at >= CURRENT_DATE`. Never rely on a cached counter.

**Flaw 3 — Claude CLI hidden costs:**
- Enhancement A: Track Claude CLI calls in cost_log with cost_usd = 0 but include call duration and token count estimates. This makes the operational load visible even if the dollar cost is zero.
- Enhancement B: Add a "Claude CLI health" check to the watchdog. If Claude CLI calls are taking > 60 seconds or failing frequently, log an alert. Track CLI concurrency to avoid session conflicts.

**Flaw 4 — No per-company allocation:**
- Enhancement A: Add a `company_name` column to cost_log. Every API call that is made on behalf of a specific company includes the company name. Dashboard can then show per-company spend.
- Enhancement B: After each company's processing completes, calculate total spend from step_log and update companies.total_cost_usd. This gives a running per-company total.

**Flaw 5 — Budget caps too low:**
- Enhancement A: Increase caps based on actual usage data. After one week of operation, review cost_log to determine real daily spend. Set caps at 2x the average daily spend.
- Enhancement B: Make caps dynamic: $5/day per ACTIVE company (not per entity). 6 active NC companies = $30/day NC budget. This scales with pipeline size.

### 5 Toughest Questions for Ewing

1. What is the ACTUAL maximum you are willing to spend per day across all entities? $11/day (current caps) or something higher? What is the monthly ceiling?
2. Should budget caps be per-company or per-entity? If one company needs $2 in research and another needs $0.10, should the system prioritize the cheaper one?
3. When budget is exhausted, should the system queue work for the next day or skip it entirely? Queued work means a backlog builds up overnight.
4. Should cost tracking be visible in client-facing pages? Some clients might want to know "we invested $X researching your company's market."
5. At what dollar threshold should the system send an iMessage alert? $1? $5? Only on per-call spikes (e.g., a single API call costing > $0.50)?

---

## SYSTEM 12: Human Audit System

### What It Does
Implements verification pairs (two LLMs independently validate the same facts) and routes uncertain or flagged items to a human review queue. The certifier agent checks proposals for: fact verification, "all about them" compliance, methodology disclosure, negative fact filtering, hallucination detection, and quality score justification. Items that fail certification enter the human_review_queue with type, priority, and review context.

### Where It Gets Data
- **proposals table** -> proposal content for certification
- **human_review_queue table** -> pending reviews by type (proposal_review, fact_check, etc.)
- **dossier_provenance** (designed) -> source trail for fact verification
- **Claude CLI + DeepSeek** -> dual-LLM verification pattern

### What Decisions It Makes
- Certification verdict: APPROVED, NEEDS_REVIEW, or REJECTED
- Quality score adjustment (certifier can modify the score)
- Whether to route to human review queue

### What Output It Creates
- **proposals updates** -> certified_by, certified_at, status changed to 'certified' or 'needs_review'
- **agent_runs log entry** -> certification result and verdict details
- **human_review_queue entries** -> items needing human attention

### What Uses This Output Next
- **Engagement Engine** only activates certified proposals (in theory -- see Flaw 4 in Engagement Engine)
- **Dashboard** shows pending review count and breakdown
- **Web Server** displays certification status on proposal pages

### 5 Fatal Flaws

1. **Dual-LLM verification is specified but not enforced.** The guardrails say "multi-LLM consensus required before customer-facing documents" and "every fact that appears in customer-facing content must be confirmed by two independent LLMs." But the certifier agent runs a SINGLE Claude CLI call (or single DeepSeek fallback). It does not run BOTH and compare results. The "dual-LLM" pattern is aspirational, not implemented.

2. **The certifier reads proposal_json, not the HTML.** The HTML is what the client sees. The JSON is the raw data. If the HTML rendering introduces errors (wrong data in wrong fields, formatting that changes meaning), the certifier would not catch it because it only reviews the JSON.

3. **No source provenance checking.** The certifier prompt asks "are all facts verifiable and sourced?" but the certifier has no access to the original sources. It cannot check if "15 employees" came from LinkedIn or was hallucinated. There is no dossier_provenance table or source_trail data for the certifier to verify against.

4. **human_review_queue has no notification mechanism.** Items enter the queue but nobody is notified. There is no iMessage alert, no Slack notification, no email. The dashboard shows a count, but if nobody opens the dashboard, reviews pile up indefinitely.

5. **No feedback from human review back to the system.** When Mark reviews and approves or rejects an item, the queue entry status changes. But the REASON for the rejection is not captured, and no learning occurs. If Mark rejects 5 proposals for the same reason, the system does not learn to avoid that pattern.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Single-LLM certification:**
- Enhancement A: Run the certifier prompt on BOTH Claude CLI and DeepSeek. Compare verdicts. If they disagree, route to human review with both perspectives. If they agree on APPROVED, approve. If either says REJECTED, reject.
- Enhancement B: At minimum, use a DIFFERENT model than the one that generated the proposal. If Claude CLI generated the proposal, certify with DeepSeek. If DeepSeek was the fallback, certify with Claude CLI.

**Flaw 2 — JSON not HTML reviewed:**
- Enhancement A: Also send the HTML to the certifier and ask it to verify that the rendered content matches the JSON data (correct names in correct sections, valuations match, no rendering errors).
- Enhancement B: Add an HTML validation step that checks for common rendering issues: empty sections, mismatched names, broken formatting, missing sections.

**Flaw 3 — No source provenance:**
- Enhancement A: Build a `fact_provenance` table that stores each fact with its source URL, source excerpt, and extraction method. The certifier can query this table to verify claims.
- Enhancement B: Include source information in the proposal_json. Each fact should carry a `source` field that the certifier can check for plausibility.

**Flaw 4 — No notification:**
- Enhancement A: After any human_review_queue insert, send an iMessage: "[Argus] {review_type} needs review: {company_name}. {count} items in queue. Reply REVIEW to see details."
- Enhancement B: Add a Slack notification via slack_messages.py: post to an #ops channel when new review items are queued. Include a link to the web server review page.

**Flaw 5 — No feedback learning:**
- Enhancement A: Add `rejection_reason` and `correction_notes` fields to human_review_queue. When Mark rejects, capture why. Monthly: aggregate rejection reasons into prompt improvements for the proposal and certifier agents.
- Enhancement B: Create a `feedback_events` table that links human decisions to specific outputs. When patterns emerge (e.g., "Mark always rejects valuations above $10M for companies with < 10 employees"), create new validation rules automatically.

### 5 Toughest Questions for Ewing

1. What percentage of proposals should be human-reviewed before auto-approval is trusted? The guardrails say 10 consecutive approvals with zero edits. Is that per-company, per-vertical, or per-template?
2. If the certifier says APPROVED but Mark disagrees, what happens to the certifier? Should its prompt be updated? Should it be retrained on Mark's corrections?
3. Should the human review queue have a SLA? "Reviews must be completed within 24 hours or escalate." What is the escalation path?
4. Is it worth the cost to run 3 LLMs (generate + 2 verifiers) on every proposal? At current volume (6 companies) yes. At 100 companies? 500?
5. Should there be a "pre-certification" checkpoint that catches obvious errors (empty fields, wrong entity, no valuation) before the expensive LLM certification runs?

---

## SYSTEM 13: Listener Agent (Designed, Not Built)

### What It Does
The most ambitious unbuilt system. Designed as a "VP of Sales who never sleeps" that scans 5 channels (Fireflies, Gmail, Google Calendar, Salesfinity, Slack) every 30 minutes for signals. Diagnoses situations using a situation library, prescribes plays from a play template library, personalizes with company data, stages deliverables for human approval, and gradually earns auto-execute trust (10 consecutive approvals per play before auto-send).

### Where It Would Get Data
- **Fireflies** -> call transcripts, meeting recordings
- **Gmail** -> inbox messages, replies to outreach
- **Google Calendar** -> meeting events, cancellations
- **Salesfinity** -> call outcomes, dispositions
- **Slack** -> team messages, deal updates
- **situation_library table** -> diagnosed states and recommended plays
- **play_templates table** -> structured response recipes
- **All master-crm tables** -> company data for personalization

### What Decisions It Would Make
- Signal extraction: WHO, WHAT, SIGNAL type, URGENCY
- Situation diagnosis: match against situation_library
- Play selection: which template fits this situation
- Auto-execute eligibility: has this play earned enough trust?
- New situation creation: when no existing situation matches
- Multi-channel merge: combining signals from different sources about the same person

### What Output It Would Create
- **play_executions table rows** -> drafted deliverables ready for review
- **situation_library updates** -> new situations discovered
- **play_templates updates** -> new plays created, approval counts incremented
- **iMessage notifications** -> hot lead alerts with lettered choices
- **Slack notifications** -> ops channel updates

### What Would Use This Output Next
- **Executor agent** -> generates the actual deliverables (email, letter, script)
- **Meeting Engine** -> auto-triggered for calendar events
- **Engagement Engine** -> auto-triggered for signed clients
- **Nurture schedule** -> long-term follow-up queue

### 5 Fatal Flaws

1. **Nothing is built.** The entire system is a design document (agents/listener.md). No code exists. No tables have been created (situation_library, play_templates, play_executions, listener_scan_log are all unbuilt). The gap between the 225-line design spec and working code is enormous.

2. **5-channel integration is 5 separate engineering projects.** Each channel (Fireflies, Gmail, Calendar, Salesfinity, Slack) requires its own API integration, authentication, rate limiting, error handling, and data parsing. MCP tools exist for some (Gmail, Calendar, Slack) but Fireflies and Salesfinity need custom integration.

3. **30-minute scan interval may miss time-sensitive signals.** A prospect saying "send me an email" on a cold call needs a response within the hour (per guardrails). If the Listener scans at 2:00pm and the call happened at 2:05pm, the response does not start until 2:30pm. By then, 25 minutes of the "within the hour" window are gone.

4. **Auto-trust threshold of 10 is high but also brittle.** It takes 10 consecutive perfect approvals before a play auto-executes. But ONE edit (even fixing a typo) resets to zero. At current deal volume (6 companies, maybe 2-3 plays per week), reaching 10 approvals takes a month. This means the Listener is essentially always in draft mode for the foreseeable future.

5. **Multi-rep overlap detection requires fuzzy company matching.** When Mark calls "AquaScience Inc." and Ewing emails "Aqua Science LLC", the Listener must recognize these as the same company. The current classification engine uses ILIKE with wildcards, which is fragile. Without reliable fuzzy matching, duplicate outreach occurs -- the exact thing the Listener is supposed to prevent.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Nothing is built:**
- Enhancement A: Build a minimal Listener (v0) that scans ONE channel (Gmail) for replies to outreach. Match against a 3-situation library (REPLY_SEND_EMAIL, REPLY_NOT_NOW, REPLY_WANTS_VALUATION). Draft one play per situation. This is buildable in a day and proves the architecture.
- Enhancement B: Use existing MCP tools (Gmail, Calendar, Slack) to build the scan layer. Skip Fireflies and Salesfinity for v0. Build the diagnosis + play engine separately from the channel integrations.

**Flaw 2 — 5 separate integrations:**
- Enhancement A: Prioritize channels by signal density. Fireflies (call transcripts) is probably the highest-value channel because phone calls contain the richest signals. Start there with the Fireflies MCP tool.
- Enhancement B: Create a `channel_adapters/` directory with a standard interface. Each channel adapter implements `scan_since(timestamp) -> list[Signal]`. The Listener core is channel-agnostic; adapters are pluggable.

**Flaw 3 — 30-minute delay:**
- Enhancement A: Use webhooks instead of polling where available. Gmail has push notifications, Google Calendar has webhooks, Slack has event subscriptions. Only Fireflies and Salesfinity would need polling.
- Enhancement B: Reduce poll interval to 5 minutes for "hot" channels (Gmail, Salesfinity) and keep 30 minutes for "warm" channels (Calendar, Slack).

**Flaw 4 — High trust threshold:**
- Enhancement A: Lower the auto-trust threshold for low-stakes plays (schedule_callback, nurture_6month). Keep 10 for customer-facing content (emails, letters). DNC requests auto-execute immediately with no threshold.
- Enhancement B: Allow "tiered trust": at 3 approvals, auto-execute WITH human notification (iMessage: "Auto-sent follow-up to {name}. Reply UNDO to cancel."). At 10, fully silent auto-execute.

**Flaw 5 — Fuzzy matching:**
- Enhancement A: Add a `company_aliases` table that maps variations to a canonical company_id. "AquaScience Inc.", "Aqua Science LLC", "Aqua-Science" all map to the same record. Build the alias table from existing data + manual additions.
- Enhancement B: Use Levenshtein distance or trigram similarity (PostgreSQL pg_trgm extension) for fuzzy company name matching. Set a similarity threshold of 0.7 for auto-merge, 0.5-0.7 for "possible match" flagging.

### 5 Toughest Questions for Ewing

1. What is the build priority for the 5 channels? If you could only have ONE channel in the Listener, which one produces the most actionable signals?
2. For auto-trust, should the threshold vary by entity? AND Capital LP outreach is higher stakes than NC cold call follow-ups. Should AND plays require 20 approvals?
3. When the Listener encounters a situation not in the library, should it create a play immediately (speed) or flag for human design (quality)? The design says "draft best-guess" -- but a bad guess on a hot lead could damage the relationship.
4. Should the Listener scan historical data when first deployed? Going back through 30 days of Fireflies transcripts could surface missed opportunities. But it could also create a flood of stale plays.
5. How should the Listener handle contradictory signals? Mark says "great call, they're interested" on Slack, but the Fireflies transcript shows the prospect said "not right now." Which signal wins?

---

## SYSTEM 14: Orchestrator + Worker + Watchdog

### What It Does
Three-component always-on automation system. The **Orchestrator** runs every 5 minutes: resets stuck queue items, checks entity budgets, scans for targets needing work (classification, research, certification, nurture), and dispatches items to the agent_queue. The **Worker** polls every 10 seconds (60 seconds when idle): claims queue items atomically (FOR UPDATE SKIP LOCKED), routes to the correct agent function (classifier, certifier, nurturer, researcher), and logs results. The **Watchdog** runs via cron every 15 minutes: checks if orchestrator and worker are alive via pgrep, restarts dead processes.

### Where It Gets Data
- **targets table** -> targets needing classification (no entity), research (no research_completed_at)
- **proposals table** -> draft proposals needing certification
- **nurture_schedule table** -> items due today
- **agent_queue table** -> pending/claimed/done/failed items
- **cost_budget table** -> entity budgets for pause decisions
- **Process list** -> pgrep for process health checks

### What Decisions It Makes
- Which targets need classification (entity IS NULL)
- Which targets need research (entity set, research_completed_at IS NULL)
- Which proposals need certification (status = 'draft', certified_at IS NULL)
- Which nurture items are due (next_touch_date <= today)
- Budget pause decisions (entity at 100% = pause)
- Stuck item detection (claimed > 30 min = reset)
- Queue priority: critical > high > normal

### What Output It Creates
- **agent_queue items** -> dispatched work items with agent_name, record_type, record_id, priority, payload
- **agent_runs records** -> execution logs per agent per task
- **Process restarts** -> watchdog revives dead processes

### What Uses This Output Next
- **Worker** processes every queue item by routing to agent functions
- **Dashboard** displays queue stats, agent performance, failed jobs
- **Company Hub** shows pipeline history from agent_runs

### 5 Fatal Flaws

1. **Worker has only 4 agent implementations, and 2 are stubs.** agent_classifier and agent_certifier are functional. agent_researcher just logs "would research -- full implementation in next phase" and returns done. agent_nurturer logs "would process -- not yet implemented" and returns done. This means the orchestrator queues research and nurture work that the worker silently pretends to complete.

2. **Single worker, no parallelism.** The worker processes items one at a time, waiting for each to finish before claiming the next. Claude CLI calls can take 60-300 seconds. If 50 items are queued, the last one waits hours. There is no mechanism to run multiple workers in parallel (though the atomic SKIP LOCKED claim pattern supports it).

3. **Watchdog uses pgrep with script name, which is fragile.** `pgrep -f "orchestrator.py"` matches any process with "orchestrator.py" in its command line -- including text editors viewing the file, grep commands searching for it, and the watchdog itself (which it tries to exclude by PID). Multiple false-positive matches prevent proper health detection.

4. **No dead-letter queue.** When a queue item fails, it is marked 'failed' and stays in the queue forever. Failed items are never retried (except stuck items). There is no mechanism to review failed items, understand why they failed, or decide whether to retry or discard them.

5. **Server.py kills itself on startup.** Line 24: `subprocess.run(["pkill", "-f", "server.py"], capture_output=True)`. This kills ALL processes matching "server.py" -- including the process that is just starting. Combined with the watchdog restarting things, this can create a cycle of start-kill-restart.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Stub agents:**
- Enhancement A: Implement agent_researcher by calling the Exa search + LLM extraction pattern from proposal_engine.py. The code already exists -- it just needs to be extracted into a reusable function and called from the worker.
- Enhancement B: Implement agent_nurturer with a simple pattern: load the nurture_schedule entry, check the play_code, generate a "check-in" email via Claude CLI, store in play_executions as a draft. This is a 30-line function.

**Flaw 2 — Single worker:**
- Enhancement A: Run 3 worker instances. The SKIP LOCKED pattern already prevents double-claiming. The watchdog should check for and maintain 3 worker processes.
- Enhancement B: Use Python's concurrent.futures.ThreadPoolExecutor within a single worker to process 3 items simultaneously. This avoids multi-process management while still achieving parallelism.

**Flaw 3 — Fragile pgrep:**
- Enhancement A: Use PID files. Each process writes its PID to data/pids/{name}.pid on startup. The watchdog reads the PID file and checks if that specific PID is alive with `os.kill(pid, 0)`.
- Enhancement B: Use a heartbeat table in Supabase. Each process writes `{name, pid, last_heartbeat}` every 60 seconds. The watchdog checks heartbeat freshness, not process names.

**Flaw 4 — No dead-letter queue:**
- Enhancement A: After 3 failures (retry_count >= 3), move the item to a `dead_letter_queue` table with the last error. Dashboard shows dead-letter items prominently. Admin can click "Retry" or "Discard."
- Enhancement B: Add an exponential backoff retry: failed items with retry_count < 3 get status reset to 'pending' with a `not_before` timestamp (5 min, 30 min, 2 hours). Worker skips items where not_before > now().

**Flaw 5 — Server self-kill:**
- Enhancement A: Remove the pkill line entirely. If port 8080 is in use, detect it and either fail with a clear error or increment to 8081.
- Enhancement B: Use `lsof -ti:8080 | xargs kill` instead of pkill. This kills only the specific process holding port 8080, not every process whose command line contains "server.py".

### 5 Toughest Questions for Ewing

1. How many queue items per day should the system process? At current volume (6 companies), the queue is small. At 50 companies, the queue could be 200+ items daily. What is the target throughput?
2. Should the orchestrator prioritize by entity (NC before AND before RU) or by urgency (hot leads before cold research)?
3. If the orchestrator is down for 4 hours, should it process the backlog immediately when it comes back (burst), or pace itself at normal speed (avoiding API rate limits)?
4. Should there be a "maintenance mode" that pauses all automation? For deployments, database migrations, or when Ewing wants everything to stop.
5. The orchestrator polls every 5 minutes, the worker every 10 seconds. Is this the right balance? More frequent orchestrator = less latency. Less frequent worker = less database load.

---

## SYSTEM 15: Web Server

### What It Does
HTTP server on port 8080 with full page-tree navigation. Serves a dark-themed, sidebar-navigated web application with: landing page (all companies as cards), per-company hub pages with sub-pages (proposal, data room, meeting, buyers, letters, emails, scripts, attack plan, history), individual buyer detail pages, and a Monday dashboard. Reads all data live from Supabase. Built with raw Python http.server, no framework.

### Where It Gets Data
- **proposals table** -> company list, proposal content, all fields
- **engagement_buyers table** -> buyer data per proposal
- **contacts table** -> contact records (if hub read exists)
- **human_review_queue** -> pending review counts
- **page_versions table** -> version history (if table exists)
- **Direct PostgreSQL** -> uses port 6543 (connection pooler, different from other engines using 5432)

### What Decisions It Makes
- URL routing: /, /company/{slug}, /company/{slug}/{page}, /company/{slug}/buyers/{n}
- Sidebar construction: which companies, which sub-pages, active state highlighting
- Status badge colors and text based on proposal status
- Page content rendering per sub-page type
- Mobile responsive layout (sidebar toggle at 900px)

### What Output It Creates
- **Live HTML pages** -> served on every request from live database data
- **Dark-themed UI** -> consistent design system with CSS variables
- **Sidebar navigation** -> hierarchical page tree with expandable company sections

### What Uses This Output Next
- **All Slack messages** include links to server URLs
- **Meeting pages** and hub pages reference server URLs
- **Client access** (future) would use server URLs with authentication

### 5 Fatal Flaws

1. **No authentication or access control.** Anyone on the local network (or internet if port-forwarded) can see everything: proposals, buyer lists, valuations, client data, pipeline status, cost data. There is no login, no session management, no client/admin role separation. The guardrails require admin/client dual views, but the server has one view for everyone.

2. **Raw http.server is not production-grade.** Python's http.server is designed for development, not production. It is single-threaded (one request at a time), has no HTTPS, no request logging, no error handling middleware, no CSRF protection. A slow database query blocks all other requests.

3. **pkill -f server.py on startup kills itself.** Line 24 runs `subprocess.run(["pkill", "-f", "server.py"])` before binding the port. This kills the currently starting process. In practice, it may work because the pkill runs before the main module is fully loaded, but it is a race condition that causes intermittent startup failures.

4. **Database connection per request, no pooling.** Every HTTP request calls `get_db()` which creates a new PostgreSQL connection. At any meaningful traffic level, this exhausts Supabase connection limits. The connection uses port 6543 (pooler), which helps, but the pattern is still wasteful.

5. **No API endpoints for programmatic access.** The server only serves HTML pages. There are no JSON API endpoints for: updating proposal status, approving review items, triggering regeneration, marking pages as stale, or any other action. The "actionable dashboard" cannot be built without API endpoints.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No authentication:**
- Enhancement A: Add basic HTTP auth with two passwords: one for admin (see everything), one for client (filtered view). Store hashed passwords in a config file.
- Enhancement B: Add a simple session system: /login page with username/password, set a cookie, check cookie on every request. Admin users see all data; client users see only their company with admin_only fields hidden.

**Flaw 2 — Not production-grade:**
- Enhancement A: Switch to Flask or FastAPI. This is a ~2 hour migration (all the HTML generation code stays the same). Gains: multi-threading, HTTPS, logging, error handling, JSON API endpoints, middleware.
- Enhancement B: If staying with http.server, add ThreadingMixIn for concurrent requests. Add a try/except around every handler for error recovery. Add request logging.

**Flaw 3 — Self-kill on startup:**
- Enhancement A: Remove the pkill line. Use try/except around socket binding: if port is in use, log the PID holding it and exit with a clear message.
- Enhancement B: Use `SO_REUSEADDR` socket option and check if a server is already running before starting a new one.

**Flaw 4 — No connection pooling:**
- Enhancement A: Create a connection pool at module level using psycopg2.pool.SimpleConnectionPool (min=1, max=10). Each request borrows and returns a connection.
- Enhancement B: Switch to the Supabase REST API (like research_transparency.py does) instead of direct PostgreSQL. REST API handles pooling server-side.

**Flaw 5 — No API endpoints:**
- Enhancement A: Add JSON API routes: POST /api/proposals/{id}/approve, POST /api/proposals/{id}/refresh, GET /api/companies/{slug}/data. These power both the dashboard action buttons and any future mobile/integration clients.
- Enhancement B: Add a webhook endpoint: POST /api/webhook that accepts events from external systems (Fireflies, Salesfinity) and routes them to the Listener (when built).

### 5 Toughest Questions for Ewing

1. Should the web server be accessible from the internet (via ngrok/Tailscale) or only local network? Client-facing data rooms require internet access. Internal tools do not.
2. What is the authentication story? Simple password? Google OAuth? Magic link emails? Different for admin vs client?
3. Should the server be the ONLY way to view company data, or should static HTML files continue to be generated as backups/exports?
4. How should the server handle multiple simultaneous users? Mark and Ewing viewing different companies at the same time?
5. Should the server support real-time updates (WebSockets) or is page-refresh sufficient?

---

## SYSTEM 16: EBITDA Lever Engine (In Progress)

### What It Does
Designed to provide vertical-specific valuation research showing what increases and decreases a company's EBITDA multiples. For each vertical (HVAC, plumbing, water treatment, etc.), catalogs the "levers" buyers care about: recurring revenue percentage, owner dependency, customer concentration, technician retention, service agreement base, geographic coverage, etc. These levers feed into proposals and data rooms as educational content.

### Where It Gets Data
- **market_multiples.json** -> baseline EBITDA ranges by vertical
- **Exa research** -> industry reports, M&A transaction data, buyer preference surveys
- **Claude CLI** -> lever identification and impact analysis

### What Decisions It Makes
- Which levers matter for each vertical
- Relative impact of each lever on multiples (e.g., "60%+ recurring revenue adds 1.5x to EBITDA multiple")
- How to frame levers educationally ("here is what increases your company's value")

### What Output It Creates
- **Proposal sections** -> "Levers of EBITDA" educational content per company
- **Data room content** -> interactive lever exploration (planned)

### What Uses This Output Next
- **Proposal Engine** would embed lever content in proposals
- **Data Room** (planned) would make levers interactive

### 5 Fatal Flaws

1. **Not yet implemented as a standalone engine.** The lever concept is referenced in the v1 release decisions ("Levers of EBITDA" section in proposals) but there is no `ebitda_lever_engine.py` file or module. The proposal engine includes valuation ranges but does not break down what drives them.

2. **Lever data is vertical-specific but verticals are not consistently defined.** The proposal engine uses `data.get("vertical", "home services")` as a default. If the vertical field is missing or generic ("home services" instead of "HVAC"), the lever engine cannot provide specific levers. "Home services" is too broad -- HVAC levers are different from pest control levers.

3. **No source for real transaction data.** EBITDA levers should be derived from actual M&A transactions. "Companies with 60% recurring revenue sell for 2x more" should come from real data, not LLM estimation. Without a transaction database or reliable M&A data source, lever claims are unverifiable.

4. **The "interactive models" fee mode depends on this engine.** The guardrails define 5 fee modes, including "interactive_models" where the client explores 3 fee structures. This requires lever calculations to show how different assumptions change valuation. Without the lever engine, the interactive mode cannot work.

5. **No per-company lever scoring.** Even if general levers exist per vertical, there is no system to score how a SPECIFIC company performs on each lever. "AquaScience has 40% recurring revenue vs industry average of 25%" requires knowing both the company's actual metrics and the industry benchmark.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Not yet implemented:**
- Enhancement A: Create `lib/ebitda_levers.py` with a `get_levers(vertical)` function. Start with hardcoded levers for each of the 8 NC verticals. Return a list of `{lever_name, description, impact_range, evidence}` dicts.
- Enhancement B: Add a `valuation_levers` table in Supabase. Seed with 5-8 levers per vertical. The proposal engine queries this table and includes the levers section in the proposal.

**Flaw 2 — Inconsistent verticals:**
- Enhancement A: Create a `verticals` enum or lookup table with standardized vertical names. The classifier and profile engine must use this standardized list. "Home services" is not a valid vertical -- it must be specific (HVAC, plumbing, etc.).
- Enhancement B: When vertical is generic, use the company's services_offered to infer the specific vertical. "AC repair, heating installation" -> HVAC.

**Flaw 3 — No transaction data:**
- Enhancement A: Build a `comparable_transactions` table seeded from Exa research of recent M&A deals in each vertical. Store: buyer, seller, vertical, deal size, EBITDA multiple, date, source URL.
- Enhancement B: Partner with or scrape M&A data aggregators (BizBuySell, DealStats, GF Data) for transaction data. Store in a structured format for lever validation.

**Flaw 4 — Interactive mode dependency:**
- Enhancement A: Build the lever engine BEFORE building the interactive fee mode. The interactive page can launch with static levers and be made dynamic later.
- Enhancement B: For v1, the "interactive models" fee mode can show 3 fixed scenarios without dynamic lever calculation. The user picks Scenario A/B/C, not custom lever adjustments.

**Flaw 5 — No per-company scoring:**
- Enhancement A: The profile engine already estimates revenue_mix, service_agreement_pct, owner_dependency_signals. Feed these into the lever engine to score each company on each lever: "You score 7/10 on recurring revenue (industry avg: 5/10)."
- Enhancement B: Add lever questions to the data room's editable fields. The owner fills in their recurring revenue percentage, and the lever scoring updates live.

### 5 Toughest Questions for Ewing

1. Should lever data be visible to the prospect BEFORE they sign? Showing "here is what makes your company more valuable" is a powerful educational tool, but it also teaches them to negotiate harder.
2. How often do EBITDA multiples change? Annual? Quarterly? Should the system auto-update multiples from market data, or is manual review required?
3. For buy-side clients (Weiser, Design Precast), should levers show what makes an ACQUISITION TARGET more valuable (helping them evaluate targets) rather than what makes the buyer's own company valuable?
4. Should the lever engine produce a numerical "overall attractiveness score" or just qualitative assessments? A number is more actionable but also more arguable.
5. How should the system handle vertical-specific levers that the company cannot change? "Geographic monopoly" is a lever but not something the owner can improve. Should it still be shown?

---

## SYSTEM 17: Buyer Research

### What It Does
Identifies and profiles potential buyers (for sell-side deals) or acquisition targets (for buy-side deals). Uses Exa search to find companies that have acquired businesses in the target's vertical and geography. Generates fit scores, fit narratives, and approach strategies for each buyer. Stores results in the engagement_buyers table for use by the engagement engine.

### Where It Gets Data
- **Exa API** -> buyer/acquirer search by vertical, geography, recent M&A activity
- **proposals table** -> seller company data (vertical, city, state, revenue range)
- **Claude CLI** -> buyer profile generation, fit scoring, approach strategy
- **Buyer list JSON files** -> pre-researched buyer lists in data/buyer-lists/

### What Decisions It Makes
- Which search queries to run for buyer identification
- Fit scoring: how well does this buyer match this seller
- Buyer type classification: PE, strategic, competitor, family office, individual
- Top 10 ranking and detailed profile generation

### What Output It Creates
- **engagement_buyers table rows** -> buyer records with fit_score, fit_narrative, approach_strategy, contact info
- **Buyer list JSON files** -> raw buyer research saved locally
- **Buyer 1-pagers** (planned) -> per-buyer HTML summaries

### What Uses This Output Next
- **Engagement Engine** reads buyers for script generation
- **Company Hub** displays buyer table
- **Meeting Engine** includes buyer data in meeting prep
- **Web Server** shows buyers on company detail pages

### 5 Fatal Flaws

1. **No dedicated buyer research module exists.** There is no `buyer_research.py` file. Buyer data appears in engagement_buyers, but the process that populates it is not in the codebase. The research_transparency system references buyer searches, and the proposal engine mentions buyer profiles, but neither actually writes buyer records to engagement_buyers.

2. **Sell-side and buy-side buyer research is fundamentally different.** For sell-side (HR.com), we search for "who would buy an HRIS company." For buy-side (Weiser Concrete), we search for "what concrete companies are available to acquire." These are opposite research directions. The system has no way to distinguish which direction to run.

3. **Fit scoring has no calibration.** The Claude CLI generates fit_score (0-100), but there is no historical data to validate these scores. A company scored 85 might be a terrible fit. Without feedback from actual buyer responses, fit scores are LLM opinions, not data-driven predictions.

4. **No deduplication across deals.** If CMC Group is a good buyer for both Air Control AND AquaScience, it gets researched twice, scored independently, and may have different fit narratives for the same buyer. There is no canonical buyer record that spans multiple deals.

5. **Buyer contact information is likely incomplete.** Exa searches return company names and descriptions, but rarely include specific decision-maker names, direct phone numbers, or email addresses. The engagement engine generates scripts addressed to "buyer_contact_name" which may be empty.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No module exists:**
- Enhancement A: Create `lib/buyer_research.py` that takes (company_name, vertical, city, state, deal_side) and: (1) searches Exa for acquirers/targets, (2) generates fit scores and profiles via Claude CLI, (3) stores in engagement_buyers. Wire it into the orchestrator queue.
- Enhancement B: Extract the buyer search logic from the proposal engine's Exa queries (which already search for M&A activity in the vertical) and formalize it as a standalone buyer research step.

**Flaw 2 — Sell-side vs buy-side:**
- Enhancement A: The buyer research module accepts a deal_side parameter. Sell-side: search for "companies that have acquired {vertical} businesses." Buy-side: search for "{vertical} companies for sale OR owner retirement OR succession planning."
- Enhancement B: Create separate Exa query templates: SELL_SIDE_BUYER_QUERIES and BUY_SIDE_TARGET_QUERIES. Different search strategies for fundamentally different goals.

**Flaw 3 — Uncalibrated fit scoring:**
- Enhancement A: Add buyer response tracking. When a buyer responds (positive, negative, no response), update the engagement_buyer record. Over time, correlate fit_score with actual response rates. Use this data to calibrate future scoring.
- Enhancement B: Replace LLM fit scoring with a weighted checklist: same vertical (+20), same geography (+15), recent acquisitions (+20), appropriate size (+15), known acquirer (+20). This is transparent, auditable, and improvable.

**Flaw 4 — No deduplication:**
- Enhancement A: Create a `buyer_companies` table as a canonical buyer registry. engagement_buyers references buyer_company_id. When the same buyer appears for multiple deals, they share one canonical record.
- Enhancement B: Before inserting a new buyer, check engagement_buyers for existing records with the same company name. If found, link to the existing buyer and flag the overlap: "Also a buyer for {other_company}."

**Flaw 5 — Incomplete contact info:**
- Enhancement A: After buyer companies are identified, run a second enrichment pass using Clay or LinkedIn to find decision-maker names and contact info. This is the "post-letter investment" -- only spend on contacts for companies already identified as good fits.
- Enhancement B: For buyers without contact info, generate a "company approach" strategy instead of a "person approach" strategy. "Call the main number and ask for the VP of Corporate Development" instead of "Call John Smith at 555-1234."

### 5 Toughest Questions for Ewing

1. How many buyers per deal is "enough"? The overnight decision tree says "top 10 detailed + full list." But is 10 enough for a real engagement? 20? 50?
2. For buy-side clients, how do you source acquisition targets? Public listings (BizBuySell)? Cold outreach to owners who have not listed? Both?
3. Should buyer research be refreshed periodically? A buyer identified in March might have completed their own acquisition by May and be off the market.
4. For multi-deal buyers (CMC on multiple lists), should there be a coordinated outreach strategy? "We have 3 opportunities in your vertical" is a stronger pitch than 3 separate cold contacts.
5. When a buyer explicitly declines (says "not interested"), should they be removed from ALL seller lists or just the one they responded to?

---

## SYSTEM 18: Follow-up Email + Data Room

### What It Does
Generates post-call deliverables when a prospect says "send me an email" or "send me more information." The follow-up includes: a subset of the dossier (company narrative, market analysis, valuation teaser), a "market multiples delighter" (industry-specific M&A data the owner has never seen), and a link to a data room page where they can explore their company's data and adjust assumptions. The data room has dual views (admin/client) and is designed to be email-gated.

### Where It Gets Data
- **play_executions table** -> play code, deliverable content, status
- **proposals table** -> company narrative, market analysis, valuation range
- **intelligence_cache** -> company profile, engagement plan
- **dossier_final** -> owner info, narrative, letter HTML, scripts

### What Decisions It Makes
- Which data to include in the follow-up (subset, not everything)
- Fee mode for the follow-up (none, framework_only, etc.)
- Data room content: what is client-visible vs admin-only
- Whether to auto-send or draft for review

### What Output It Creates
- **play_executions rows** -> drafted follow-up deliverables
- **Data room HTML** (planned) -> client-facing interactive page
- **Email content** -> ready-to-send follow-up emails

### What Uses This Output Next
- **Company Hub** displays play executions
- **Engagement Engine** references data room links in buyer outreach
- **Client** (future) interacts with the data room

### 5 Fatal Flaws

1. **No data room engine exists.** There is no `data_room_engine.py`, no data room HTML generation, no email-gated page system. The concept is extensively designed (Listener agent spec references it, play templates reference it, guardrails describe it) but zero code exists.

2. **No email sending capability.** The system generates email content (play_executions, cold_email_body in dossier_final) but cannot actually send emails. There is no SMTP integration, no Gmail API send, no Mailgun/SendGrid. Emails are "draft" deliverables that require manual copy-paste.

3. **The "send me info" response is the highest-leverage moment and has no automation.** The guardrails say this is the differentiator: "Nobody else sends a pre-built data room after a cold call." But the system cannot detect this signal (Listener not built), cannot generate the data room (engine not built), and cannot send the email (no send capability). The entire competitive advantage is unbuilt.

4. **No email tracking.** Even if emails were sent, there is no way to know if they were opened, clicked, or responded to. The Listener design includes "email opened 3+ times, no reply" as a situation, but there is no email tracking integration.

5. **Data room interactivity is undefined.** The guardrails say prospects can "adjust assumptions" and "play with knobs" after signing. But what are the knobs? Revenue? EBITDA margin? Multiple range? Service mix? How do changes cascade to the valuation? This logic does not exist.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No data room engine:**
- Enhancement A: Build `lib/data_room.py` that takes a proposal_id and generates a client-facing HTML page with: company narrative, market analysis, valuation range (if enabled), levers of EBITDA, and a "Let's Get Started" CTA. Email-gate it with a simple token in the URL.
- Enhancement B: Use the existing company_hub.py as a starting point. Create a client-filtered version that strips admin-only data. This is 80% of a data room with 20% of the effort.

**Flaw 2 — No email sending:**
- Enhancement A: Use the Gmail MCP tool (available in the environment) to send emails via ewing@chapter.guide. Draft emails in play_executions, then use mcp__claude_ai_Gmail__gmail_create_draft to stage them.
- Enhancement B: Integrate with a transactional email service (SendGrid, Mailgun) for automated sending. Use Gmail only for manual/high-stakes emails.

**Flaw 3 — No "send me info" automation:**
- Enhancement A: Build the minimum viable Listener (Gmail scan only) that detects "send me info" replies. Auto-generate the data room + follow-up email. Stage as draft for Mark's approval.
- Enhancement B: Even without the Listener, create a manual trigger: Mark clicks a button on the company hub page ("Generate Follow-Up Package") and the system produces the data room + email in 60 seconds.

**Flaw 4 — No email tracking:**
- Enhancement A: Embed a tracking pixel in follow-up emails (1x1 transparent image hosted on the web server). Log loads to a `email_opens` table.
- Enhancement B: Use a link redirect through the web server for all data room links. `/track/{token}` redirects to the data room and logs the click.

**Flaw 5 — Undefined interactivity:**
- Enhancement A: Start with 3 editable fields: estimated revenue, EBITDA margin, number of employees. When changed, the valuation range recalculates using the market multiples. This is the minimum "knob-turning" experience.
- Enhancement B: Build a simple JavaScript calculator on the data room page that adjusts valuation based on lever inputs (recurring revenue %, owner dependency, customer concentration). No server round-trip needed.

### 5 Toughest Questions for Ewing

1. What is the minimum viable data room? Is it a static HTML page with company data, or does it NEED interactivity to be useful?
2. Should the data room URL expire? After 30 days? Never? Should it be password-protected or just obscured (long random token)?
3. When a prospect clicks "Let's Get Started" on the data room, what EXACTLY happens? Email to Mark? Slack notification? Calendar link? All three?
4. Should the follow-up email come from ewing@chapter.guide or mark@chapter.guide? Does it matter which rep had the call?
5. How much of the valuation should be in the data room? The guardrails say "show everything, educational framing." But some prospects might screenshot the valuation and use it against us in negotiation.

---

## SYSTEM 19: Feedback Loop System (Designed, Not Built)

### What It Does
Designed as a comprehensive system for capturing, processing, and learning from human corrections to machine outputs. Implements the D->C pattern: when a user comments on a section, the system first asks clarifying questions (D), then drafts a revised version with the original preserved alongside (C). Fact corrections trigger reverse-engineering of the human's research method. Conflicting feedback between users triggers a 10-option resolution quiz.

### Where It Would Get Data
- **User comments** -> box-level and inline comments on any page section
- **feedback_conversations table** (designed) -> full exchange per feedback event
- **feedback_log table** (designed) -> original value, corrected value, correction source, method
- **research_methods table** -> existing research techniques (for learning new ones)
- **verification_pairs** (designed) -> dual-LLM verification records

### What Decisions It Would Make
- What clarifying questions to ask (D phase)
- How to draft a revised version incorporating feedback (C phase)
- Whether to propose the approved output as a template
- How to resolve conflicting feedback (10-option quiz generation)
- When to propagate corrections to other companies in the same vertical

### What Output It Would Create
- **feedback_conversations rows** -> full exchange records
- **research_methods updates** -> new techniques learned from human corrections
- **Updated outputs** -> revised proposals, profiles, scripts
- **Rule change proposals** -> "Based on your approval, should this become a template for all HVAC companies?"
- **Conflict resolution records** -> which option was chosen and why

### What Would Use This Output Next
- **All engines** -> improved prompts from aggregated feedback patterns
- **Research Transparency** -> new research methods added to the library
- **Certifier** -> updated validation rules from correction patterns
- **Template Library** -> approved outputs become templates

### 5 Fatal Flaws

1. **Nothing is built.** No tables, no code, no UI. The design is documented across 3 memory files totaling ~200 lines of specification. The gap between spec and implementation is the largest of any system in the project.

2. **The D->C pattern requires real-time conversation, which the current architecture does not support.** The system generates static HTML pages. For a user to comment, get a clarifying question, respond, and see a revised draft -- all within the same session -- requires WebSocket or polling-based real-time interaction. The current http.server cannot do this.

3. **Conflicting feedback resolution is complex and rare.** The 10-option quiz modal for Mark vs Ewing disagreements is over-engineered for current volume. With 6 active deals and 2 reviewers, conflicts will be rare. The engineering cost of building the conflict resolution system is not justified by the expected frequency of conflicts.

4. **"Reverse-engineer the human's method" is extremely ambitious.** When Mark says "I found 15 employees on LinkedIn," the system should: (1) identify the research technique, (2) replicate it programmatically, (3) verify the result, (4) add it to the research methods library. This requires natural language understanding of correction context, programmatic access to the data source (LinkedIn is notoriously difficult to scrape), and reliable technique extraction.

5. **Feedback aggregation requires significant volume.** "Monthly: aggregate patterns into updated prompt templates" assumes enough feedback events to identify patterns. With 6 companies and ~5 corrections per company, there are ~30 data points per month. That is not enough for statistical pattern detection. The system may learn the wrong lessons from small samples.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Nothing is built:**
- Enhancement A: Build the minimum viable feedback loop: a comment box per section on the web server pages. Comments are stored in a `feedback_comments` table with: page_type, section_id, company_name, comment_text, commenter, created_at. No D->C conversation, just capture comments.
- Enhancement B: Add a "correct this fact" button next to every data field on company pages. Click -> edit the value -> system saves the correction to `fact_corrections` table with old_value, new_value, corrected_by. This is inline feedback without the conversation layer.

**Flaw 2 — No real-time support:**
- Enhancement A: Use simple AJAX polling. Comment box submits to a /api/comment endpoint. Response includes clarifying question. User responds in the same text box. No WebSocket needed for turn-by-turn conversation.
- Enhancement B: Accept that v1 feedback is asynchronous. User leaves a comment, system processes it in the background, revised version appears on next page load. Not real-time, but functional.

**Flaw 3 — Over-engineered conflict resolution:**
- Enhancement A: For v1, conflict resolution is simple: last edit wins, previous versions preserved. Both users can see the edit history. No quiz needed.
- Enhancement B: When feedback conflicts, create a human_review_queue item with both perspectives. The designated resolver (Ewing) picks one. Simple and sufficient for current volume.

**Flaw 4 — Ambitious method reverse-engineering:**
- Enhancement A: Start with manual method capture. When Mark corrects a fact, the system asks "How did you find this?" in a text box. The response is stored as a note on the correction. A human reviews notes monthly and manually adds promising techniques to research_methods.
- Enhancement B: For common data sources (LinkedIn, BBB, Google Reviews), build specific lookup integrations. When Mark says "I checked LinkedIn," the system does not need to reverse-engineer -- it already knows how to check LinkedIn.

**Flaw 5 — Volume too low for patterns:**
- Enhancement A: Instead of statistical pattern detection, use explicit rule capture. When Mark corrects the same TYPE of error 3 times (e.g., always lowering employee count estimates), create a rule: "Employee count estimates tend to be high by 20-30%. Apply a conservative adjustment."
- Enhancement B: Aggregate feedback across ALL companies in the same vertical, not per-company. "In HVAC companies, Mark corrected revenue upward 4 out of 5 times" is a pattern even with low per-company volume.

### 5 Toughest Questions for Ewing

1. Who is the primary feedback provider -- Mark or Ewing? If Mark reviews every proposal and Ewing reviews strategy, they have different correction patterns. Should the system learn different rules from each person?
2. How fast does feedback need to be incorporated? If Mark corrects a fact at 9am, should the proposal be updated by 10am? Or is next-day acceptable?
3. Should feedback on one company's proposal automatically propagate to similar companies? If Mark says "HVAC companies in Virginia should not include residential revenue estimates," should that rule apply to all Virginia HVAC companies?
4. What happens when feedback contradicts the North Star guardrails? If Mark says "include this negative fact about the owner," the guardrails say never include negative facts. Who wins?
5. Is there a point where auto-learning should be paused? If the system has learned 50 rules from feedback, should new rules be reviewed more carefully to prevent rule bloat?

---

## SYSTEM 20: Template Library (Designed, Not Built)

### What It Does
Designed as Mark's master pattern repository. When Mark approves a proposal section, script, or letter, it can be proposed as a template for future use. Templates are tagged by vertical, entity, deal type, and situation. The system pulls templates from Google Drive hourly and also learns templates from approved feedback loop outputs. Templates evolve through versioning as feedback refines them.

### Where It Would Get Data
- **Google Drive** -> Mark's manually created/refined templates (letters, scripts, proposals)
- **Approved play_executions** -> outputs that passed human review
- **Approved feedback revisions** -> revised versions that Mark accepted
- **page_templates table** (designed) -> template catalog

### What Decisions It Would Make
- Whether an approved output should become a template (proposed, not automatic)
- Which existing template best matches a new situation
- How to merge feedback-driven improvements into template versions
- Template applicability: which verticals, entities, deal types a template serves

### What Output It Would Create
- **page_templates table rows** -> versioned template catalog
- **Template suggestions** -> "Use the Air Control HVAC template as a starting point for this new HVAC company"
- **Template evolution** -> version history showing how templates improve over time

### What Would Use This Output Next
- **Proposal Engine** -> starts from the best matching template instead of blank prompt
- **Engagement Engine** -> uses approved script templates per buyer type
- **Executor agent** -> loads templates for letter/email/script generation
- **Feedback Loop** -> approved outputs feed back into templates

### 5 Fatal Flaws

1. **Nothing is built.** No page_templates table, no Google Drive integration, no template matching logic. Templates are mentioned in guardrails, v1 release decisions, and Listener design, but no code implements them.

2. **Google Drive hourly sync is a non-trivial integration.** Requires Google Drive API authentication, file change detection, content parsing (templates may be in Docs, Sheets, or PDF format), and reliable sync. The Google service account credentials exist in the environment but the integration code does not.

3. **Template matching is a hard problem.** "Which template best fits this new HVAC company in Virginia?" requires multi-dimensional matching: vertical, geography, company size, deal side, fee mode, meeting type. Without a robust matching algorithm, the system either picks wrong templates or defaults to generic ones.

4. **Template versioning creates complexity.** When a template is updated, should all existing proposals generated from the old version be regenerated? What about proposals that were manually edited after generation? The cascading update problem is significant.

5. **Templates risk homogenization.** If every HVAC proposal starts from the same template, prospects who compare notes will see identical structure and language. The "wizard of facts" positioning depends on feeling bespoke, not templated.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Nothing is built:**
- Enhancement A: Create a `page_templates` table with: template_code, template_name, entity, vertical, deal_side, page_type, content_template (with {variable} placeholders), version, created_by, approved_by. Seed with 3-5 templates extracted from the best existing proposals.
- Enhancement B: Even simpler: create a `templates/` directory in the repo with markdown files organized by type (letters/, proposals/, scripts/). The proposal engine reads the appropriate template file as context for the LLM prompt.

**Flaw 2 — Google Drive sync:**
- Enhancement A: Start with manual template import: a script that an admin runs to pull the latest templates from a specific Drive folder. Not hourly, but on-demand.
- Enhancement B: Use the Google Drive API with a service account. Watch a single folder for changes. Download changed files and upsert into page_templates. Schedule via cron every hour.

**Flaw 3 — Template matching:**
- Enhancement A: Simple priority matching: exact vertical match > same entity match > generic. If multiple templates match, use the one with the highest approval count.
- Enhancement B: Store template match criteria as JSON tags: `{"vertical": "hvac", "deal_side": "sell_side", "company_size": "small"}`. Match templates with the most overlapping tags.

**Flaw 4 — Cascading updates:**
- Enhancement A: Templates do not cascade to existing outputs. They only affect NEW generations. Old proposals keep their content; new proposals use the latest template.
- Enhancement B: Add an `is_stale` flag (from the version engine design). When a template is updated, mark all pages generated from that template as stale. Lazy rebuild on view.

**Flaw 5 — Homogenization risk:**
- Enhancement A: Templates provide STRUCTURE, not CONTENT. The template defines sections and ordering, but the LLM generates unique content per company. This ensures consistent quality without identical output.
- Enhancement B: Generate 3 variations per template application (per the speed-to-production rule). This ensures diversity even when starting from the same template.

### 5 Toughest Questions for Ewing

1. Where do Mark's current templates live? Google Drive? Local files? Email drafts? What format are they in?
2. Should templates be shared across entities or entity-specific? An AND Capital LP letter template is fundamentally different from an NC sell-side letter template. But some structural patterns (opening, CTA, sign-off) might be shared.
3. How many template categories are needed? By page type (letter, email, call script, proposal section) x entity x vertical x deal side = hundreds of potential categories. Is that manageable?
4. When Mark edits a generated output, should the system automatically propose the edit as a template improvement? Or should template updates be explicitly requested?
5. Should templates include tone/style guidance or just content structure? "This letter should feel warm and personal" vs "Paragraph 1: company story, Paragraph 2: market data, Paragraph 3: CTA."

---

## SUPPLEMENTAL SYSTEM: Supabase Client (lib/supabase.py)

### What It Does
Entity-aware database client that wraps all Supabase REST API calls. Enforces the core rule that every transactional row must carry an entity tag. Provides get(), insert(), upsert(), insert_batch(), dnc_check(), and get_campaign() functions. Maintains a list of entity-exempt tables (do_not_call, audits, harvests, campaigns, etc.) that do not require entity tags.

### Where It Gets Data
- **Environment variables or hardcoded defaults** -> SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
- **Supabase REST API** -> all database operations via HTTP

### What Decisions It Makes
- Whether a table requires an entity tag (ENTITY_EXEMPT set check)
- Whether to raise an error for missing entity (ValueError on entity-required tables)
- DNC check: phone exact match OR company_name exact match with block_company flag

### What Output It Creates
- **Database rows** -> inserts and upserts with enforced entity tags
- **Query results** -> JSON responses from Supabase REST API
- **Errors** -> ValueError when entity is missing on transactional tables

### What Uses This Output Next
- **Any module** that imports lib.supabase for database operations
- In practice: only research_transparency.py uses the REST client pattern. Most engines use direct psycopg2.

### 5 Fatal Flaws

1. **Most engines bypass supabase.py entirely.** The proposal engine, profile engine, engagement engine, meeting engine, company hub, dashboard, orchestrator, worker, and server all use direct psycopg2 connections. The supabase.py entity enforcement is irrelevant if nobody uses it. The entity tag rule is only enforced for code that imports this module.

2. **DNC check is exact match only.** `dnc_check()` uses REST API filter `phone=eq.{phone}` and `company_name=eq.{company_name}`. This means "555-1234" does not match "(555) 123-4567". "AquaScience Inc" does not match "Aqua Science LLC." Phone normalization and fuzzy company matching are essential for DNC to work reliably.

3. **No connection pooling or retry logic.** Every API call opens a new HTTPS connection via urllib. There is no retry on network errors, no timeout handling (relies on system defaults), no backoff on 429 rate limits. A network blip causes silent data loss.

4. **Service role key grants full database access.** The client uses the service_role key, which bypasses all Row Level Security (RLS) policies. This is appropriate for server-side operations but means any bug in any engine can read or write any table without restriction. There is no principle of least privilege.

5. **ENTITY_EXEMPT list is hardcoded and may be incomplete.** If a new table is created that should be entity-exempt, someone must manually add it to the Python set. If they forget, the first insert attempt raises a ValueError that blocks the entire operation.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Most engines bypass supabase.py:**
- Enhancement A: Refactor all engines to use supabase.py (or a psycopg2 equivalent that enforces entity tags) instead of direct connections. The entity enforcement is too important to be optional.
- Enhancement B: Add entity enforcement at the DATABASE level with a trigger: `CREATE TRIGGER enforce_entity BEFORE INSERT ON {table} FOR EACH ROW WHEN (NEW.entity IS NULL) EXECUTE FUNCTION reject_null_entity()`. This catches violations regardless of which client library is used.

**Flaw 2 — Exact match DNC:**
- Enhancement A: Normalize phone numbers before comparison: strip all non-digits, compare last 10 digits. This handles format variations.
- Enhancement B: Use PostgreSQL similarity or ILIKE for company name DNC: `company_name ILIKE %{normalized_name}%`. Accept a higher false-positive rate on DNC (blocking a company that should not be blocked is safer than contacting a blocked company).

**Flaw 3 — No retry logic:**
- Enhancement A: Add a retry wrapper with exponential backoff: 3 attempts with 1s, 3s, 10s delays. Log each retry.
- Enhancement B: Add explicit timeout to all urllib calls (currently no timeout parameter on most requests). 30 seconds for reads, 60 seconds for writes.

**Flaw 4 — Service role key:**
- Enhancement A: Use the anon key for read operations and service_role key only for writes. This limits the blast radius of read-path bugs.
- Enhancement B: Create Supabase database functions (RPC) for sensitive operations. The client calls the function, not the table directly. Functions can enforce business rules server-side.

**Flaw 5 — Hardcoded exempt list:**
- Enhancement A: Query information_schema to determine which tables have an entity column. Tables without entity columns are auto-exempt. No manual list needed.
- Enhancement B: Store the exempt list in a Supabase table or config file, not in Python source code.

### 5 Toughest Questions for Ewing

1. Should supabase.py be the ONLY database access path (enforcing entity tags everywhere), or should psycopg2 remain available for performance-critical operations?
2. For DNC, what is the acceptable false-positive rate? Is it better to occasionally block a valid contact (safe) or occasionally miss a DNC entry (risky)?
3. Should there be a "soft DNC" that blocks outbound but allows inbound? A company that says "don't call us" might still email us.
4. Are there tables that should have entity tags but currently do not? Is the exempt list correct?
5. Should the supabase client log every database operation for audit purposes, or is that too much overhead?

---

## SUPPLEMENTAL SYSTEM: Slack Notification System (lib/slack_messages.py)

### What It Does
Generates formatted Slack messages with links to company hubs, proposals, meeting pages, and dashboards. Provides two message types: per-company update messages (for DMs to Mark) and a daily briefing message (for #ops channel). Messages include Slack markdown formatting, emoji status indicators, and clickable links to all page types.

### Where It Gets Data
- **proposals table** -> company data, status, quality score, buyer counts
- **engagement_buyers table** -> scripted buyer count
- **human_review_queue table** -> pending review count
- **BASE_URL env var** -> defaults to http://localhost:8080

### What Decisions It Makes
- Emoji status coding: green circle for engagement_active, yellow for certified, blue for other
- Which links to include per company (hub, proposal, data room, meeting, dashboard)
- Daily briefing format and content selection

### What Output It Creates
- **Formatted Slack message strings** -> ready for copy-paste or API send
- **stdout output** -> when run directly, prints all messages for manual copy

### What Uses This Output Next
- **auto_refresh.py** references Slack notification (not wired)
- **Manual copy-paste** -> the primary usage currently

### 5 Fatal Flaws

1. **No actual Slack integration.** The module generates message TEXT but does not SEND to Slack. There is no Slack API call, no webhook, no bot token. Messages must be manually copied and pasted into Slack. The Slack MCP tool is available in the environment but is not wired to this module.

2. **BASE_URL defaults to localhost.** Links in Slack messages point to http://localhost:8080, which only works if the person clicking is on the same machine. For Mark (who may be on a different device), these links are dead. No tunnel (ngrok/Tailscale) is configured.

3. **No message scheduling or automation.** The daily briefing must be manually triggered by running the script. There is no cron job, no orchestrator integration, no automatic morning delivery. The "Monday morning dashboard" experience requires someone to remember to run the script.

4. **Message content is NC-only.** The company update function only queries proposals (NC deals). AND Capital fund updates, RevsUp recruiting metrics, and standalone entity status are not represented. The Slack messages give a partial picture.

5. **No thread/conversation context.** Each message is standalone. There is no threading (post updates as replies to the original company thread), no message editing (update a prior message with new status), no message deletion (remove stale updates). Over time, the channel fills with disconnected snapshots.

### 2 Best Enhancements Per Flaw

**Flaw 1 — No actual sending:**
- Enhancement A: Use the Slack MCP tool (mcp__claude_ai_Slack__slack_send_message) to send messages directly. The tool is available in the environment.
- Enhancement B: Use a Slack incoming webhook URL. One POST request per message, no SDK needed. Store the webhook URL in environment variables.

**Flaw 2 — Localhost links:**
- Enhancement A: Set up Tailscale on the Mac mini and use the Tailscale hostname as BASE_URL. This gives a stable URL accessible from any device on the tailnet.
- Enhancement B: Use ngrok for a public URL. Store the ngrok URL in an environment variable that auto_refresh and slack_messages read.

**Flaw 3 — No scheduling:**
- Enhancement A: Add a daily briefing job to the orchestrator's run_cycle(). If current time is between 7:00-7:05 AM and today's briefing has not been sent, generate and send.
- Enhancement B: Add a cron job: `0 7 * * 1-5 python3 ~/Projects/master-crm/lib/slack_messages.py` (weekdays at 7am).

**Flaw 4 — NC-only content:**
- Enhancement A: Add entity-specific message generators: `generate_and_update()`, `generate_ru_update()`. The daily briefing includes sections for all active entities.
- Enhancement B: Query across all entity-tagged data. Show AND Capital LP pipeline, RevsUp placement pipeline alongside NC deal pipeline.

**Flaw 5 — No conversation context:**
- Enhancement A: Store Slack message timestamps in a `slack_messages` table. When updating a company, edit the existing message instead of posting a new one.
- Enhancement B: Use Slack threads. Each company gets one top-level message. All updates are replies in the thread. This keeps the channel clean while preserving history.

### 5 Toughest Questions for Ewing

1. Should Slack messages go to a shared #ops channel or individual DMs? Mark might not want deal updates in a shared channel.
2. What time should the daily briefing be sent? Is 7am right? Should it adjust if no one reads it until 9am?
3. Should Slack messages include action buttons (Slack Block Kit) like "Approve", "Review", "Skip"? This would let Mark take action without opening the web server.
4. When a deal status changes (certified -> engagement_active), should an automatic Slack update fire? Or only the morning briefing?
5. Should there be separate channels per entity (#nc-ops, #and-ops, #ru-ops) or one unified #master-crm channel?

---

## SUPPLEMENTAL SYSTEM: Auto-Refresh (lib/auto_refresh.py)

### What It Does
Coordinates page regeneration after any engine produces output. Provides thin wrapper functions (refresh_hub, refresh_all_hubs, refresh_dashboard, refresh_all) that import and call the appropriate engine modules. Also includes a Slack notification function (not wired to actual Slack). Designed to keep hubs and dashboards current as data changes.

### Where It Gets Data
- **company_hub.py** -> imported dynamically for hub regeneration
- **dashboard.py** -> imported dynamically for dashboard regeneration

### What Decisions It Makes
- Which hub to refresh (single company or all)
- Whether to also refresh the dashboard
- Notification message formatting

### What Output It Creates
- **Refreshed hub HTML files** -> via company_hub.generate_hub()
- **Refreshed dashboard HTML** -> via dashboard.generate_dashboard()
- **Log entries** -> auto_refresh.log

### What Uses This Output Next
- **Proposal Engine** calls refresh_hub() and refresh_dashboard() after generating a proposal
- **Manual invocation** -> CLI with --dashboard, --hub flags

### 5 Fatal Flaws

1. **Refresh is synchronous and blocks the calling engine.** When the proposal engine calls refresh_hub() after generating a proposal, it waits for the hub to regenerate (including all database queries) before continuing to the next proposal. In a 6-company batch, this adds significant latency.

2. **No selective refresh based on what changed.** refresh_all() regenerates EVERY hub and the dashboard, even if only one company's data changed. With 20+ companies, this is wasteful.

3. **Slack notification is a stub.** notify_slack() generates a message string but does not send it. The comment says "Slack integration is a future wire-up."

4. **No error isolation.** If hub regeneration fails for one company (database error, missing data), it can crash the entire refresh_all() call, leaving subsequent companies unrefreshed.

5. **Circular import risk.** auto_refresh imports company_hub and dashboard at function call time (not module load time) to avoid circular imports. But if those modules import auto_refresh (which they do not currently), the system would break.

### 2 Best Enhancements Per Flaw

**Flaw 1 — Synchronous blocking:**
- Enhancement A: Queue refresh jobs in agent_queue instead of running them inline. The worker processes refreshes in the background.
- Enhancement B: Use Python threading: `threading.Thread(target=refresh_hub, args=(company_name,)).start()`. Fire and forget; the main engine continues.

**Flaw 2 — No selective refresh:**
- Enhancement A: refresh_hub() only for the specific company that changed. refresh_dashboard() only if pipeline status or key metrics changed.
- Enhancement B: Track "last data change" timestamps per company. Only refresh if `last_change > last_refresh`.

**Flaw 3 — Slack stub:**
- Enhancement A: Wire to Slack MCP tool.
- Enhancement B: Wire to iMessage bridge for critical notifications (hot lead, quality alert).

**Flaw 4 — No error isolation:**
- Enhancement A: Wrap each hub regeneration in try/except. Log errors but continue to the next company.
- Enhancement B: Return a results dict: `{"Air Control": "success", "AquaScience": "error: connection timeout"}`.

**Flaw 5 — Circular import risk:**
- Enhancement A: Keep the lazy import pattern (import inside function, not at module level). This is the correct approach and should be documented as intentional.
- Enhancement B: Create a `refresh_queue` table instead of direct function calls. Engines write to the queue, a separate refresh worker processes it.

### 5 Toughest Questions for Ewing

1. How current do hubs need to be? Is a 5-minute delay acceptable, or does the hub need to reflect the latest data on every page load?
2. Should auto-refresh trigger iMessage notifications? "Hub updated for Air Control -- new buyer data added."
3. When a hub refresh fails, should anyone be notified? Or just logged silently?
4. Should the dashboard refresh on a schedule (every hour) regardless of data changes?
5. Is it worth building a "what changed" summary into the refresh notification? "Air Control hub refreshed: 2 new buyers added, quality score updated to 85."

---

## CROSS-SYSTEM ANALYSIS

### System Maturity Matrix

| System | Code Exists | Functional | Production-Ready | Guardrail-Compliant |
|--------|:-----------:|:----------:|:----------------:|:-------------------:|
| Classification Engine | YES | YES | MOSTLY | YES |
| Proposal Engine | YES | YES | NO | NO (deal_side) |
| Profile Engine | YES | YES | NO | MOSTLY |
| Engagement Engine | YES | PARTIAL | NO | NO (deal_side) |
| Meeting Engine | YES | YES | NO | MOSTLY |
| Company Hub | YES | YES | NO | NO (no client view) |
| Dashboard | YES | YES | NO | NO (missing sections) |
| Version Engine | PARTIAL | NO | NO | NO |
| Research Transparency | YES | PARTIAL | NO | MOSTLY |
| Step Tracking | PARTIAL | PARTIAL | NO | NO |
| Cost Tracking | PARTIAL | PARTIAL | NO | NO |
| Human Audit System | YES | PARTIAL | NO | NO (single LLM) |
| Listener Agent | DESIGN ONLY | NO | NO | N/A |
| Orchestrator+Worker+Watchdog | YES | MOSTLY | NO | MOSTLY |
| Web Server | YES | YES | NO | NO (no auth) |
| EBITDA Lever Engine | NO | NO | NO | N/A |
| Buyer Research | NO | NO | NO | N/A |
| Follow-up Email + Data Room | NO | NO | NO | N/A |
| Feedback Loop System | DESIGN ONLY | NO | NO | N/A |
| Template Library | DESIGN ONLY | NO | NO | N/A |

**Summary:** 15 of 20 systems have code. 12 are at least partially functional. 0 are production-ready. 5 are guardrail-compliant. 5 exist only as design documents.

### Critical Path Dependencies (What Must Be Built in What Order)

**Phase 0 -- Fix Active Errors (This Week)**
1. Add `deal_side` field to proposals and targets tables
2. Tag existing deals: HR.com, AquaScience, Air Control, Springer Floor = sell_side; Weiser, Design Precast = buy_side
3. Add deal_side check to proposal_engine.py and engagement_engine.py
4. Fix MULTIPLES_FILE path from dossier-pipeline to master-crm

**Phase 1 -- Close Critical Gaps (Next 2 Weeks)**
5. Build `lib/buyer_research.py` for sell-side buyer identification
6. Build `lib/data_room.py` for client-facing data room pages
7. Wire Gmail MCP tool for email draft creation
8. Implement dual-LLM certification (different model than generator)
9. Fix cost_budget daily reset mechanism
10. Implement agent_researcher properly (not a stub)

**Phase 2 -- Production Hardening (Weeks 3-4)**
11. Add authentication to web server (admin vs client)
12. Move from http.server to Flask/FastAPI
13. Add connection pooling to all database-using modules
14. Implement page versioning (save_version on every engine output)
15. Run multiple worker instances for parallelism
16. Build per-company cost tracking (company_name on cost_log)

**Phase 3 -- Automation Layer (Weeks 5-8)**
17. Build minimal Listener (Gmail scan only, 3 situations)
18. Build feedback comment capture (box-level, no D->C conversation yet)
19. Build EBITDA lever engine with hardcoded levers per vertical
20. Build template library with manual template import
21. Add calendar integration for meeting prep auto-trigger
22. Add Slack notification for review queue items

**Phase 4 -- Full Vision (Months 3-6)**
23. Full Listener with 5 channels
24. Full feedback loop with D->C conversation
25. Interactive data rooms with editable fields
26. Auto-trust graduation for plays
27. Template evolution from feedback
28. Multi-deal buyer coordination

### The Three Most Dangerous Gaps

1. **No buyer research pipeline.** The engagement engine assumes buyers exist. They do not get created automatically. This is a show-stopper for the entire sell-side workflow. Without buyers, the engagement engine activates with zero scripts, the company hub shows an empty buyer table, and the attack plan has no targets. The competitive promise -- "we identify and approach buyers for you" -- has no backing system.

2. **No email sending capability.** The system generates beautiful follow-up emails that cannot be sent. Every email requires manual copy-paste. This destroys the "respond within the hour" speed advantage. The guardrails describe "send me an email" as the highest-leverage moment in the sales cycle. The Listener, play templates, executor agent, and dispatcher agent are all designed around automated email delivery. None of it works without a send mechanism. The Gmail MCP tool is available in the environment and could be wired in quickly.

3. **No deal_side handling.** Two of the six active deals are buy-side (Weiser, Design Precast). The system generates exactly the wrong deliverables for 33% of the pipeline. This is not a future risk -- it already happened. The proposal engine generated "who would buy Weiser Concrete" when Weiser IS the buyer looking for targets. Every downstream engine (engagement, meeting, hub) propagated the error. A single `deal_side` field and conditional prompt selection would fix this permanently.

### The Five Most Fragile Integration Points

1. **ILIKE fuzzy matching across all engines.** Every engine queries by `company_name ILIKE %{name}%`. This is the most common pattern in the codebase and the most fragile. "Air" matches multiple companies. "Design" matches multiple companies. One wrong match silently contaminates all downstream outputs. The fix is to use company_id (UUID) for all joins and reserve ILIKE only for initial search.

2. **Claude CLI subprocess dependency.** Every engine calls `subprocess.run(["claude", "-p", "--output-format", "text"])`. If the Claude CLI binary is not installed, not authenticated, rate-limited, or slow, EVERY engine fails. There is no health check, no circuit breaker, no graceful degradation. The fallback to OpenRouter exists but is not tested regularly.

3. **Direct PostgreSQL vs Supabase REST API split.** Some modules use psycopg2 with direct PostgreSQL connections (proposal_engine, profile_engine, engagement_engine, meeting_engine, company_hub, dashboard, orchestrator, worker, server). Others use urllib-based Supabase REST API (supabase.py, research_transparency.py). They use different connection strings (port 5432 vs 6543). This creates inconsistent behavior, different error modes, and double the surface area for connection failures.

4. **Log file paths across two projects.** proposal_engine.py logs to `~/Projects/dossier-pipeline/data/audit-logs/`. Research transparency logs to the same dossier-pipeline path. All other engines log to `~/Projects/master-crm/data/logs/`. This means log history is split across two project directories, making it difficult to reconstruct what happened for a given company.

5. **Auto-refresh cascade.** When the proposal engine finishes, it calls `refresh_hub()` and `refresh_dashboard()`. These functions import and call company_hub.py and dashboard.py, which both open new database connections. If the proposal engine is in the middle of a batch (6 companies), each one triggers hub + dashboard regeneration -- that is 12 additional database sessions and 12 file writes per batch. This is wasteful and can cause connection exhaustion.

### Guardrail Compliance Scorecard

| Guardrail | Status | Violation Details |
|-----------|--------|-------------------|
| Every row gets entity tag | PARTIAL | Supabase client enforces on writes. But engines using direct psycopg2 can bypass the check. |
| DNC is universal | PARTIAL | DNC check exists but only covers phone + company name. No email, LinkedIn, or channel-specific blocks. |
| Never create new Supabase instance | COMPLIANT | One instance used consistently. |
| Never create new API accounts | COMPLIANT | All keys are existing accounts. |
| Always commit + push | NOT ENFORCED | No automated git commit after changes. Relies on human discipline. |
| Always log costs | PARTIAL | Proposal engine logs. Profile engine does not. Worker partially logs. |
| Never generate from memory | COMPLIANT | All engines read from database before generating. |
| Always disclose NEEDS_REVIEW | PARTIAL | Certifier sets the status, but no notification mechanism ensures humans see it. |
| Letters before calls | NOT ENFORCED | No system prevents calling before a letter is sent. Orchestrator queues in order but does not block. |
| Multi-LLM consensus before customer-facing | NOT IMPLEMENTED | Certifier uses single LLM. Dual-LLM pattern exists in design but not in code. |
| is_step_done() before every API call | NOT IMPLEMENTED | No engine consistently checks for completed steps before running. |
| Never say "private equity" | NOT ENFORCED | AND Capital scripts may contain the term. No automatic content filter. |
| Quality >= 80 before sending | PARTIALLY ENFORCED | Engagement engine activates needs_review proposals (quality < 80). |
| 10 consecutive approvals for auto-trust | NOT BUILT | Auto-trust system does not exist. |
| Daily budget caps enforced | PARTIAL | Orchestrator checks budgets but cost_budget.spent_usd is never reset. |

### Data Architecture Concerns

**Tables Referenced But Possibly Non-Existent:**
- `page_versions` -- server.py explicitly checks if it exists, suggesting it may not
- `situation_library` -- Listener design only
- `play_templates` -- Listener design only, but play_executions references it
- `listener_scan_log` -- Listener design only
- `feedback_conversations` -- Feedback design only
- `feedback_log` -- Feedback design only
- `company_aliases` -- Does not exist, needed for fuzzy matching

**Tables With Potential Schema Issues:**
- `companies.cost_log_entries` -- referenced by hub, may not exist as a column
- `companies.total_cost_usd` -- referenced by hub, may need manual population
- `cost_budget.spent_usd` -- accumulated but never reset for daily periods
- `proposals.deal_side` -- critical field that does not yet exist
- `targets.entity` -- may be text or enum; orchestrator casts to `::text` suggesting type uncertainty

**Connection String Inconsistencies:**
- proposal_engine.py: port 5432 (direct)
- server.py: port 6543 (pooler)
- supabase.py: REST API (no port)
- All others: port 5432 (direct)
- The pooler port (6543) is preferred for web server traffic. Direct port (5432) is fine for batch operations but can exhaust connection limits under load.

### Security Concerns

1. **Database password in plaintext in 8+ files.** `MakeMoneyNow1!` appears in: proposal_engine.py, profile_engine.py, engagement_engine.py, meeting_engine.py, company_hub.py, dashboard.py, orchestrator.py, worker.py, server.py, slack_messages.py, research_transparency.py. It should be in an environment variable, read once.

2. **Supabase service role key in plaintext in 5+ files.** The service role key (which has FULL admin access to the database) is hardcoded in: CLAUDE.md, proposal_engine.py, supabase.py, research_transparency.py, and potentially others. This key appears in git history and is visible to anyone with repo access.

3. **OpenRouter API key in plaintext in 3+ files.** Same issue. Hardcoded in CLAUDE.md, proposal_engine.py, worker.py.

4. **Exa API key in plaintext.** Hardcoded in proposal_engine.py.

5. **No HTTPS on web server.** All data transmitted in plaintext. If the server is ever internet-accessible, all company data, valuations, buyer lists, and client information is visible to network observers.

### What Works Well (Credit Where Due)

1. **Classification Engine** is well-designed with proper fail-safes (confidence thresholds, person routing, campaign prefixes). The deterministic approach is correct. The priority ordering (campaign > person > intent > industry > fallback) is sound and mirrors real-world entity resolution logic.

2. **Founder Guardrails** are comprehensive, specific, and consistently referenced across all engines. The "all about them" principle, deal-killer prevention, insufficient data cascade, and fee mode system are well-thought-out. This is the strongest document in the project.

3. **Cost tracking architecture** (entity budgets, per-call logging, daily caps) is sound even if implementation is incomplete. The design scales from $11/day to much higher budgets without structural changes.

4. **Orchestrator + Worker + Watchdog** pattern is solid. The SKIP LOCKED atomic claiming, priority queuing, and stuck-item reset are production-quality patterns. The three-component separation (scheduler, executor, health monitor) is the right architecture.

5. **Web Server** dark-themed UI with sidebar navigation is polished and functional for the current scale. The page tree (company > proposal > buyers > individual buyer) is the right information architecture. Mobile responsiveness at 900px breakpoint is thoughtful.

6. **Agent identity documents** are clear and well-structured. Each agent has defined: what it does, what models it uses, what rules it follows, and what it does NOT do. The separation of concerns (classifier does not research, researcher does not validate, validator does not execute) is clean.

7. **Research transparency concept** is unique and valuable. Most CRM systems hide their research process. Showing clients "here is exactly how we researched your company" builds trust and demonstrates thoroughness. This is a genuine competitive advantage once implemented.

8. **Multi-entity architecture** is well-designed. One database, entity-tagged rows, entity-specific views, shared engines with entity config. This scales from 3 entities to 10+ without structural changes.

### Recommended Priority Actions (Top 10)

1. **Add deal_side to proposals and targets. Tag existing deals. Gate proposal generation on deal_side.** (1 hour, fixes 33% pipeline error)
2. **Move all credentials to environment variables.** (30 minutes, eliminates security risk)
3. **Build buyer_research.py.** (1 day, unlocks engagement engine for sell-side)
4. **Fix cost_budget daily reset.** (15 minutes, prevents permanent budget lockout)
5. **Implement dual-LLM certification.** (2 hours, satisfies the most critical guardrail)
6. **Fix MULTIPLES_FILE path.** (5 minutes, prevents silent fallback to stale defaults)
7. **Replace ILIKE company matching with company_id joins.** (4 hours across all engines, prevents data contamination)
8. **Implement agent_researcher properly.** (4 hours, removes the most impactful worker stub)
9. **Add authentication to web server.** (2 hours, enables safe external access)
10. **Wire Gmail MCP for email drafts.** (2 hours, enables the "respond within the hour" promise)

---

*This document is the quality assurance backbone of the master-crm project. Every flaw identified here is real, every question is hard, and every enhancement is actionable. The system has strong architectural foundations -- the entity model, the agent separation, the guardrail framework, the orchestrator pattern -- but significant implementation gaps remain, particularly around buyer research, email delivery, deal_side handling, and the unbuilt Listener/Feedback/Template systems.*

*The honest assessment: the system is approximately 40% built relative to the full vision documented in the guardrails and design specs. The 40% that exists is generally well-designed but not production-hardened. The remaining 60% is designed but not coded.*

*Priority should be: (1) fix the deal_side error that affects active deals today, (2) build buyer research to make the engagement engine functional, (3) enable email sending to deliver on the speed promise, (4) then tackle the Listener as the gateway to full automation.*

---

## APPENDIX A: THE 100 TOUGHEST QUESTIONS (CONSOLIDATED)

Every system's 5 toughest questions, consolidated and grouped by theme. Answering these questions definitively would resolve the majority of open design decisions.

### Entity & Classification (Questions 1-10)

1. When a company does HVAC work AND has a family office investor, what is the tiebreaker: Next Chapter or AND Capital?
2. Should the classifier ever auto-reclassify a record that a human manually tagged?
3. For multi-entity people (Mark spans all 3), should classification follow the CAMPAIGN or the CONTENT?
4. How should entity transitions work (NC deal becomes AND investment)?
5. Is there a classification confidence floor below which the pipeline should STOP and wait for human input?
6. When a company could be served by multiple entities, the guardrails say "start with the smallest." But what if the larger engagement is more urgent?
7. For person routing, should new reps be auto-detected or manually configured?
8. Should the DNC list include "soft DNC" (no outbound, but accept inbound)?
9. How should the system handle companies that operate in multiple verticals (HVAC + electrical)?
10. Should entity classification be visible to the client, or is it internal-only?

### Data Quality & Personalization (Questions 11-25)

11. When Mark says "revenue is $5M" but Exa says $2.25M, which wins?
12. How often should profiles be regenerated as new data arrives?
13. Should each field show a confidence indicator ("HIGH -- owner stated" vs "LOW -- estimated")?
14. What is the minimum data completeness threshold for a profile to be "ready"?
15. For buy-side clients, what does the "proposal" look like?
16. When quality_score is 50-79, should proposals go to clients or be upgraded first?
17. If estimated valuation is dramatically wrong, is that a deal-killer or a conversation-starter?
18. Should multiples vary by geography, company size, and recency?
19. For buy-side clients, is the attack plan "all about the targets" or "all about the buyer's growth strategy"?
20. When the system estimates revenue from employee count, what margin of error is acceptable?
21. Should the system track how often its estimates were wrong (for calibration)?
22. When two LLMs disagree on a fact, what happens besides "use the higher confidence"?
23. Should the system show clients its estimate methodology on every page, or only when asked?
24. For sensitive verticals (medical, energy), are there additional personalization restrictions?
25. How should the system handle companies where the owner is also the only employee?

### Buyer & Engagement (Questions 26-40)

26. How many buyers per deal is "enough"?
27. For buy-side clients, how do you source acquisition targets -- public listings, cold outreach, or both?
28. Should buyer research be refreshed periodically?
29. For multi-deal buyers, should there be a coordinated outreach strategy?
30. When a buyer explicitly declines, are they removed from ALL seller lists?
31. When a buyer appears on multiple seller lists, should engagement be coordinated or independent?
32. What is the minimum number of buyers needed before activation is worthwhile?
33. For the 30/60/90 timeline, who actually executes each step?
34. Should DNC'd buyers appear in client-facing view with a "you may contact independently" note?
35. When a buyer responds positively, what triggers the next stage?
36. Should buyer fit scores be visible to clients?
37. When a buyer completes an acquisition, should they be flagged as "recently acquired -- may want more"?
38. For competitive situations (prospect talking to other brokers), how aggressive should the response be?
39. What is the guarantee structure for different deal sizes?
40. Should the system auto-detect when a buyer completes an acquisition (via news monitoring)?

### Meeting & Real-Time (Questions 41-50)

41. How far in advance should meeting prep be generated?
42. Should meeting pages be phone-optimized for use during meetings?
43. For joint meetings, should the prep include role assignments?
44. If a meeting is rescheduled, should prep regenerate?
45. Should meeting prep be sent via iMessage 30 minutes before?
46. During live calls, what data should be pushed to the rep's screen?
47. How should post-meeting outcomes be captured (form? transcript analysis?)?
48. Should meeting type be a strict enum or free text?
49. For back-to-back meetings with different companies, how should the system handle rapid context switching?
50. Should the meeting page include competitive intelligence about the prospect's current broker?

### Dashboard & Monitoring (Questions 51-60)

51. Should the dashboard be the landing page of the web server?
52. What "revenue metrics" should the dashboard track?
53. Should the dashboard show orchestrator/worker/watchdog health?
54. Is a mobile version of the dashboard needed?
55. What time horizon matters most -- 7 days? Monthly? YTD?
56. Should the dashboard have entity filters (NC/AND/RU)?
57. At what budget threshold should iMessage alerts fire?
58. Should the dashboard include "what happened while you were away" summary?
59. What is the ideal dashboard refresh frequency?
60. Should the dashboard show a "system confidence" metric (how much of the data is estimated vs verified)?

### Feedback & Learning (Questions 61-75)

61. Who is the primary feedback provider -- Mark or Ewing?
62. How fast does feedback need to be incorporated?
63. Should feedback on one company propagate to similar companies?
64. When feedback contradicts the guardrails, who wins?
65. Is there a point where auto-learning should be paused to prevent rule bloat?
66. How far back should version history go?
67. When Mark edits a section, should that auto-create a new version?
68. Should version history be visible to clients?
69. If a rule change affects 20 pages, should they all rebuild immediately?
70. Is there value in version-level commenting?
71. What percentage of proposals should be human-reviewed before auto-approval is trusted?
72. If the certifier says APPROVED but Mark disagrees, what happens?
73. Should the human review queue have a SLA?
74. Is dual-LLM certification worth the cost at scale (100+ companies)?
75. Should there be a "pre-certification" quick check before expensive LLM certification?

### Infrastructure & Operations (Questions 76-90)

76. How many queue items per day should the system process at target scale?
77. Should the orchestrator prioritize by entity or by urgency?
78. If the orchestrator is down for 4 hours, should it process the backlog immediately?
79. Should there be a "maintenance mode" that pauses all automation?
80. Is the 5-minute orchestrator / 10-second worker polling balance correct?
81. Should the web server be internet-accessible or local-only?
82. What is the authentication story for the web server?
83. Should static HTML files continue as backup/exports alongside the web server?
84. How should multiple simultaneous users be handled?
85. Does the server need WebSockets for real-time updates?
86. What is the actual maximum daily spend across all entities?
87. Should budget caps be per-company or per-entity?
88. When budget is exhausted, should work queue for tomorrow or be skipped?
89. Should the system detect and alert on API key expiration before it happens?
90. What is the process for deploying code changes -- manual git pull or automated?

### Vision & Strategy (Questions 91-100)

91. What is the Listener channel priority if you could only have ONE?
92. Should auto-trust thresholds vary by entity (AND Capital higher stakes)?
93. When the Listener encounters an unknown situation, speed or quality?
94. Should the Listener scan historical data when first deployed?
95. How should contradictory signals be resolved (Slack vs transcript)?
96. Who is the audience for research transparency pages -- internal or external?
97. Should failed research be shown to demonstrate thoroughness?
98. Should per-company research cost be visible to clients?
99. For the data room, what is the minimum viable feature set?
100. At what point should NC be "done" enough to start building AND Capital and RevsUp automation?

---

## APPENDIX B: ESTIMATED BUILD EFFORT

| System | Current State | Effort to Production-Ready | Effort to Full Vision |
|--------|--------------|---------------------------|----------------------|
| Classification Engine | 85% functional | 4 hours | 2 days |
| Proposal Engine | 70% functional | 1 day | 3 days |
| Profile Engine | 60% functional | 1 day | 2 days |
| Engagement Engine | 40% functional | 2 days | 1 week |
| Meeting Engine | 60% functional | 1 day | 3 days |
| Company Hub | 50% functional | 1 day | 3 days |
| Dashboard | 50% functional | 1 day | 3 days |
| Version Engine | 10% functional | 2 days | 1 week |
| Research Transparency | 30% functional | 2 days | 1 week |
| Step Tracking | 20% functional | 1 day | 3 days |
| Cost Tracking | 30% functional | 4 hours | 2 days |
| Human Audit System | 40% functional | 1 day | 1 week |
| Listener Agent | 0% (design only) | 2 weeks | 2 months |
| Orchestrator+Worker+Watchdog | 70% functional | 2 days | 1 week |
| Web Server | 60% functional | 3 days | 2 weeks |
| EBITDA Lever Engine | 0% | 2 days | 1 week |
| Buyer Research | 0% | 2 days | 1 week |
| Follow-up Email + Data Room | 0% | 3 days | 2 weeks |
| Feedback Loop System | 0% (design only) | 1 week | 1 month |
| Template Library | 0% (design only) | 3 days | 2 weeks |

**Total estimated effort to production-ready:** ~6 weeks of focused engineering
**Total estimated effort to full vision:** ~5 months of focused engineering

---

*END OF AUDIT DOCUMENT*
*Generated by Argus (Claude Opus 4.6) on 2026-03-28*
*Next review: after Phase 0 and Phase 1 completion*
