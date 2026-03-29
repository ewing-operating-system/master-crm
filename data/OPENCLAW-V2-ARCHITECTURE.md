# OpenClaw v2 Architecture — Continuous Autonomous Agent System

**Author:** Argus (Claude Opus 4.6)
**Date:** 2026-03-28
**Status:** PROPOSAL — requires Ewing approval before implementation
**Prerequisite:** Phase 1 entity tagging (add `entity` column to all transactional tables) must complete first

---

## DESIGN PRINCIPLES

1. **Always-on, not batch-and-die.** Agents run continuously on Mac mini (24GB). They sleep, wake on schedule or event, process, sleep again. No human starts them.
2. **Shared engine, separate content.** One pipeline codebase. Entity-specific config (tone, terms, templates, business rules) loaded per campaign_id at runtime.
3. **Entity tagging is oxygen.** Every row written carries an `entity` field. Every query filters by entity. No exceptions.
4. **Claude CLI is the workhorse.** At $0.00/call via subscription, Claude handles all quality-critical and narrative work. Paid APIs handle fast extraction and cross-checking only.
5. **Letters before calls. Always.** Enrichment (cell + email) is a post-letter investment, not a pre-letter gate.
6. **Never wipe. Only append.** Incremental storage after every step. Resume from any failure point.
7. **Trust requires independence.** The model that researches a fact never validates it. Different model families, always.
8. **Human approval is non-negotiable for outbound.** 100% of letters, 10% random sampling of research. Nothing sends without a human saying yes.

---

## SYSTEM OVERVIEW

```
                          +------------------+
                          |   ORCHESTRATOR   |  (cron + event bus)
                          +--------+---------+
                                   |
            +----------+-----------+-----------+-----------+
            |          |           |           |           |
       +----v----+ +---v----+ +---v-----+ +--v------+ +--v-------+
       | SCOUT   | |CLASSIFY| |RESEARCH | |VALIDATE | | EXECUTE  |
       | (discover)| (route) | (extract)| (trust)  | (deliver) |
       +---------+ +--------+ +---------+ +---------+ +----------+
            |          |           |           |           |
            +----------+-----------+-----------+-----------+
                                   |
                          +--------v---------+
                          |     SUPABASE     |  (master-crm instance)
                          |  dwrnfpjcvydhmh  |
                          +--------+---------+
                                   |
            +----------+-----------+-----------+-----------+
            |          |           |           |           |
       +----v----+ +---v----+ +---v-----+ +--v------+ +--v-------+
       | APPROVE | |DISPATCH| | TRACK   | |NURTURE  | | LEARN    |
       | (human) | (outreach)| (response)| (re-engage)| (feedback)|
       +---------+ +--------+ +---------+ +---------+ +----------+
```

---

## SUPABASE SCHEMA (master-crm instance: `dwrnfpjcvydhmhnvyzov`)

### New Tables for v2

| Table | Purpose | Key Columns |
|---|---|---|
| `agent_runs` | Every agent execution logged | `id`, `agent_name`, `campaign_id`, `entity`, `target_id`, `status`, `started_at`, `finished_at`, `cost_usd`, `error_msg`, `tokens_in`, `tokens_out` |
| `agent_queue` | Event-driven work queue | `id`, `agent_name`, `target_id`, `campaign_id`, `entity`, `priority`, `payload_json`, `status` (pending/claimed/done/failed), `claimed_at`, `claimed_by` |
| `approval_queue` | Human review queue | `id`, `target_id`, `entity`, `campaign_id`, `deliverable_type` (letter/research/call_script), `content_json`, `status` (pending/approved/rejected/revised), `reviewer`, `reviewed_at`, `notes` |
| `response_log` | Track all inbound responses | `id`, `target_id`, `entity`, `campaign_id`, `channel` (call/email/letter/linkedin), `response_type` (interested/not_now/dnc/no_answer/voicemail), `raw_content`, `created_at` |
| `feedback_log` | Human overrides that train the system | `id`, `agent_name`, `target_id`, `entity`, `original_output_json`, `corrected_output_json`, `correction_type` (tone/fact/classification/valuation), `created_at` |
| `cost_budget` | Per-entity daily/monthly spend caps | `id`, `entity`, `period` (daily/monthly), `budget_usd`, `spent_usd`, `last_reset` |
| `intelligence_cache` | Accumulated knowledge per target | `id`, `target_id`, `entity`, `key` (owner_preference/best_time/competitor_intel/etc), `value_json`, `source_agent`, `updated_at` |
| `nurture_schedule` | Cooling period re-engagement | `id`, `target_id`, `entity`, `campaign_id`, `reason` (not_now/call_back_later/seasonal), `next_touch_date`, `touch_type`, `status` |

### Existing Tables (with mandatory `entity` column added in Phase 1)

All existing tables (`targets`, `dossier_final`, `dossier_runs`, `dossier_provenance`, `sent_log`, `outreach_queue`, `dialer_queue`, `call_analysis`, `pipeline_log`, `campaigns`, `dossier_cost_log`) retain their structure with `entity` column added. No schema breaks.

### Views for v2

| View | Purpose |
|---|---|
| `v_pipeline_status` | Per-entity pipeline funnel: raw -> researched -> validated -> letter_drafted -> approved -> sent |
| `v_daily_cost` | Per-entity daily spend across all agents |
| `v_approval_backlog` | Pending human reviews with age and priority |
| `v_campaign_performance` | Per-campaign: sent, responded, converted, exhausted |
| `v_agent_health` | Per-agent: success rate, avg cost, avg duration, error rate (last 24h) |

### SQL Functions

| Function | Purpose | Called By |
|---|---|---|
| `is_step_done(target_id, step_name)` | Check if a pipeline step already completed for this target | All agents before starting work |
| `log_step(target_id, step_name, agent, status, output_json, cost)` | Record a completed step | All agents after finishing work |
| `log_verification_pair(target_id, researcher_output, validator_output, verdict)` | Store dual-LLM verification pair | Validator |
| `claim_next_work(agent_name, entity, campaign_id)` | Atomically claim next item from agent_queue | All agents (prevents double-processing) |
| `check_dnc(phone, email, company)` | Universal DNC check across all fields | Dispatcher before any outreach |
| `check_budget(entity, cost_estimate)` | Returns true if spend is within budget | Orchestrator before dispatching paid work |
| `advance_lifecycle(target_id, new_stage)` | Move target to next lifecycle stage with audit trail | Controller after milestone events |
| `get_entity_config(campaign_id)` | Load entity-specific business rules, tone, terms | All agents at start of work |

---

## AGENT SPECIFICATIONS

### 1. ORCHESTRATOR (The Brain)

**Name:** `orchestrator`
**Role:** Master scheduler and event router. Runs continuously on Mac mini. Decides what work needs doing, when, and dispatches to agent_queue.
**LLM Model:** None for scheduling logic. Python + cron. Uses Claude CLI ($0.00) only for ambiguous priority decisions.
**Trigger:** Cron (runs every 5 minutes) + Supabase webhook on new rows in `targets`, `response_log`, `call_analysis`.
**Reads from:** `targets`, `dossier_final`, `agent_runs`, `agent_queue`, `approval_queue`, `cost_budget`, `campaigns`, `nurture_schedule`
**Writes to:** `agent_queue`, `agent_runs`, `pipeline_log`
**SQL Functions:** `check_budget()`, `claim_next_work()`, `get_entity_config()`
**Interacts with:** Dispatches work to all other agents via `agent_queue`. Never does LLM work itself.
**Campaigns:** All 17. Entity-agnostic scheduler, entity-aware routing.
**Cost per run:** $0.00 (pure Python logic, no LLM calls in normal operation)

**Scheduling Logic:**

```
Every 5 minutes:
  1. Check agent_queue for stuck items (claimed > 30min ago, no completion) -> reset to pending
  2. Check cost_budget -> if any entity over daily cap, pause that entity's queue
  3. Scan targets where dossier_status != APPROVED and no pending agent_queue item -> create work items
  4. Scan nurture_schedule where next_touch_date <= today -> create re-engagement work items
  5. Scan response_log for new responses -> route to appropriate follow-up agent

Every hour:
  6. Pull Salesfinity call log -> write to call_analysis with entity tag
  7. Pull Fireflies transcripts -> mine for leads, write to targets with entity tag

Daily 6AM:
  8. Generate daily briefing per entity -> post to Slack
  9. Rebuild dialer queue priorities
  10. DNC sync to Salesfinity
  11. Cost report to Ewing via iMessage if spend > 80% of any entity budget

Weekly Sunday 5PM:
  12. Full pipeline health report
  13. Agent performance summary
  14. Stale target recycling (contacted > 90 days, no response, not exhausted -> back to queue)
```

**Error Recovery Pattern:**
- If an agent fails, the orchestrator marks the agent_queue item as `failed` with error message
- After 3 failures on the same target, the target is flagged for human review
- After 10 consecutive failures from the same agent, the orchestrator pauses that agent and alerts Ewing via iMessage
- The orchestrator itself has a watchdog: a separate cron job that checks if the orchestrator process is alive every 15 minutes, restarts if dead

---

### 2. SCOUT (The Hunter)

**Name:** `scout`
**Role:** Discovers new targets from three sources: TAM scraping, transcript mining, and referral intake. Feeds raw leads into the pipeline.
**LLM Model:** Gemini 2.5 Flash Lite via OpenRouter ($0.001/call) for entity extraction from transcripts. No LLM needed for TAM scraping (structured data).
**Trigger:** Scheduled. TAM scraping: daily 2AM. Transcript mining: hourly. Referral intake: event-driven (new email/form).
**Reads from:** `tam_businesses`, `tam_final`, `tam_scrape_runs`, `call_analysis`, `targets` (to dedup), `do_not_call`
**Writes to:** `targets` (new raw leads), `tam_businesses`, `tam_scrape_runs`, `agent_queue` (trigger classification), `pipeline_log`
**SQL Functions:** `check_dnc()`, `log_step()`
**Interacts with:** Writes targets, then creates `agent_queue` items for the Classifier.
**Campaigns served:**
- `NC-TAM` — Google Places, Exa, state records scraping for home services businesses
- `NC-TRANSCRIPT` — Fireflies transcript mining for NC deal signals
- `AND-DEAL-SOURCE` — Transcript mining for AND Capital deal flow signals
- `AND-LP-LINKEDIN` — Exa enrichment for LP prospect discovery
- `RU-REFERRAL` — Email/form intake for RevsUp referrals
**Cost per run:** ~$0.05/run (TAM scraping: Exa at $0.006/result x ~5 results/company. Transcript mining: $0.001/transcript for entity extraction.)

**Source-Specific Logic:**

TAM Scraping (NC-TAM):
```
1. Load scrape config: verticals (HVAC, plumbing, roofing, pest, water treatment, flooring, steel, concrete)
2. For each vertical + geography combo:
   a. Google Places API search (or Exa fallback)
   b. Dedup against tam_businesses + targets
   c. DNC check
   d. Write to tam_businesses with entity=next_chapter
   e. Queue for classification (should auto-route to NC based on vertical)
3. Rate limit: 10-second delay between companies
```

Transcript Mining (NC-TRANSCRIPT, AND-DEAL-SOURCE):
```
1. Pull unprocessed Fireflies transcripts via API
2. For each transcript:
   a. Extract company mentions, person names, intent signals
   b. Classify intent: hiring -> RU, transaction -> NC, capital -> AND
   c. Dedup against targets
   d. DNC check
   e. Write to targets with entity tag
   f. Queue for classification agent (for verification)
3. Entity routing: deal/buyer-seller context -> NC, fund/LP context -> AND, recruiting -> RU
```

---

### 3. CLASSIFIER (The Router)

**Name:** `classifier`
**Role:** Implements the deterministic Entity Classification Guide decision tree. Every record passes through this agent before any work begins. Python-first with LLM fallback for ambiguous cases.
**LLM Model:** Python deterministic engine (`lib/classification.py`) for 90%+ of cases. Claude CLI ($0.00) for ambiguous cases where confidence < 2.0.
**Trigger:** Event-driven. Fires when new items appear in `agent_queue` with `agent_name=classifier`.
**Reads from:** `targets`, `campaigns`, `do_not_call`
**Writes to:** `targets` (entity tag, confidence, classification_method), `agent_queue` (trigger researcher), `pipeline_log`
**SQL Functions:** `check_dnc()`, `log_step()`, `get_entity_config()`, `advance_lifecycle()`
**Interacts with:** Receives from Scout. Dispatches to Researcher via `agent_queue`.
**Campaigns served:** All 17. This is the universal router.
**Cost per run:** $0.00 for deterministic classification. ~$0.00 for LLM fallback (Claude CLI, rare).

**Decision Tree (priority order, from Entity Classification Guide):**

1. Campaign prefix: `NC-` -> next_chapter, `AND-` -> and_capital, `RU-` -> revsup (instant, confidence 3.0)
2. Person routing: Chris Rex -> and_capital ONLY, John Kelly -> NEVER and_capital
3. Intent: Hiring? -> revsup
4. Intent: Transaction (buy/sell)? -> next_chapter
5. Intent: Capital (invest/fundraise)? -> and_capital
6. Company type fallback: trades/home services -> NC, healthcare/energy/assets -> AND, SaaS (if hiring) -> RU
7. No signal -> NO TAG, confidence 0. Never force classification.

**Fail-safes:**
- RevsUp ONLY if hiring is present
- Next Chapter ONLY if a transaction is happening
- AND Capital ONLY if capital is involved
- Tag only if confidence >= 2.0
- ACTION beats INDUSTRY 100% of the time

**Output written to targets row:**
```json
{
  "entity": "next_chapter",
  "sub_type": "sell_side",
  "confidence": 2.5,
  "classification_method": "intent_transaction",
  "classification_reason": "Business owner of HVAC company exploring sale"
}
```

---

### 4. RESEARCHER (The Extractor)

**Name:** `researcher`
**Role:** Extracts structured company and person intelligence from web search results. Produces fact-with-provenance JSON for every claim. Entity context changes what it looks for.
**LLM Model:**
- Primary: Gemini 2.5 Flash Lite via OpenRouter ($0.001/call) -- fast, cheap, good at structured extraction
- Secondary (cross-check): DeepSeek V3 via OpenRouter ($0.004/call) -- different model family for verification pair
- Fallback: Mistral Small via local Ollama ($0.00) -- when OpenRouter is down
**Trigger:** Event-driven. Fires when `agent_queue` items with `agent_name=researcher` appear.
**Reads from:** `targets`, `dossier_final` (resume check), `dossier_runs` (cache check -- never re-research), `campaigns`
**Writes to:** `dossier_final` (incremental after every step), `dossier_runs`, `dossier_provenance`, `dossier_cost_log`, `agent_queue` (trigger validator), `pipeline_log`
**SQL Functions:** `is_step_done()`, `log_step()`, `log_verification_pair()`, `get_entity_config()`
**Interacts with:** Receives from Classifier. Dispatches to Validator via `agent_queue`.
**Campaigns served:**
- `NC-SELL-LETTER`, `NC-SELL-CALL` -- focus on owner background, succession signals, SDE indicators, service area, BBB
- `AND-LP-LETTER`, `AND-LP-CALL` -- focus on AUM, fund structure, investment thesis, FINRA registration, sector alignment
- `AND-DEAL-SOURCE` -- focus on deal flow, investment banking relationships, sector expertise
- `RU-CLIENT` -- focus on company stage, ARR, sales team size, recent funding, hiring signals
**Cost per run:** ~$0.02/target (5 Exa searches at $0.006/each = $0.03, 2 LLM calls at $0.001-$0.004 = $0.005, total ~$0.035)

**Dual-Researcher Pattern (mandatory for verification pairs):**
```
1. Run 5 Exa searches per target (company+owner, reviews, services, financials, linkedin)
2. Researcher A (Gemini Flash Lite): Extract structured facts from search results
3. Researcher B (DeepSeek V3): Extract structured facts from SAME search results independently
4. Store both outputs as a verification pair via log_verification_pair()
5. Merge: take the union of facts, flag any contradictions between A and B
6. Write merged output to dossier_final with status=RESEARCHED
```

**Entity-Specific Extraction Templates:**

Next Chapter targets:
```
owner_name, owner_title, owner_background, owner_quotes, owner_vision,
company_story, culture_signals, services, service_area, differentiators,
years_in_business, employee_estimate, revenue_signals, certifications,
awards, bbb_rating, google_rating, review_highlights, growth_signals,
succession_context, mailing_address, phone, website_url
```

AND Capital targets:
```
firm_name, principal_name, title, aum_estimate, fund_structure,
investment_thesis, sector_focus, finra_registration, regulatory_status,
recent_deals, portfolio_companies, geographic_focus, preferred_return,
management_fee, carry, co_investment_history, linkedin_url
```

RevsUp targets:
```
company_name, stage, arr_estimate, funding_history, sales_team_size,
open_roles, hiring_signals, tech_stack, market_segment, growth_rate,
key_contacts (vp_sales, cro, vp_cs), linkedin_url, glassdoor_rating
```

**Source Trail (MANDATORY -- facts without provenance are REJECTED by validator):**
Every fact includes: `source_url`, `source_type`, `search_query`, `source_excerpt`

---

### 5. VALIDATOR (The Trust Layer)

**Name:** `validator`
**Role:** Cross-checks every fact from the Researcher with independent judgment. Catches fabrications, unsourced claims, and implausible data. The model that validates NEVER matches the model that researched.
**LLM Model:**
- Validator A: DeepSeek V3 via OpenRouter ($0.004/call) -- different family from Gemini researcher
- Validator B: Llama 3.3 70B via OpenRouter (Together, $0.002/call) -- third model family for true independence
- Merge strategy: pick the validator with MORE flags as winner, then union unique flags from the loser
**Trigger:** Event-driven. Fires when `agent_queue` items with `agent_name=validator` appear.
**Reads from:** `dossier_final` (researcher output), `dossier_runs`, `dossier_provenance`, `targets`, `campaigns`
**Writes to:** `dossier_final` (validation results appended), `dossier_provenance` (flag records), `agent_queue` (trigger executor or approval_queue), `pipeline_log`, `dossier_cost_log`
**SQL Functions:** `is_step_done()`, `log_step()`, `log_verification_pair()`, `get_entity_config()`
**Interacts with:** Receives from Researcher. Routes to either Executor (if all clear) or Approval Queue (if NEEDS_REVIEW flags).
**Campaigns served:** All campaigns that produce dossiers (NC-SELL-LETTER, NC-SELL-CALL, AND-LP-LETTER, AND-LP-CALL, AND-DEAL-SOURCE, RU-CLIENT).
**Cost per run:** ~$0.008/target (2 validator calls at $0.002-$0.004 each)

**Validation Checklist:**

For each fact from the researcher:
1. Does it have a source URL? (REJECT if not)
2. Is the source URL plausible for this type of fact?
3. Is the fact internally consistent with other facts about this company?
4. Is the financial data in a reasonable range for this industry/size?
5. Are there contradictions between Researcher A and Researcher B outputs?

**Validation Rules:**
- Revenue claims must have at least 1 supporting signal (employee count, service area, review volume)
- Owner names must appear in at least 1 public source
- Phone numbers from Google Maps are BUSINESS lines, not owner cell phones
- Years in business consistent with founding date
- BBB ratings must match the BBB website

**Severity Levels:**
- HIGH: Claims contradicted by another source. Never approve with HIGH flags unresolved.
- MEDIUM: Owner name flagged as possible pseudonym. All data from single source.
- LOW: Self-reported claims presented as verified.

**Output per fact:**
```json
{
  "fact_key": "estimated_revenue",
  "fact_value": "$2.5M",
  "verdict": "VERIFIED|PLAUSIBLE|NEEDS_REVIEW|REJECTED",
  "reason": "Consistent with 15 employees and service area covering 3 counties",
  "confidence": 0.85
}
```

**Routing after validation:**
- All VERIFIED/PLAUSIBLE -> advance to Executor
- Any NEEDS_REVIEW -> advance to Executor BUT also create approval_queue item for 10% random sampling
- Any HIGH severity flags -> STOP. Create approval_queue item for human review. Do NOT advance.

---

### 6. SYNTHESIZER (The Narrator)

**Name:** `synthesizer`
**Role:** Produces the intelligence narrative from validated facts. This is the bridge between raw data and customer-facing deliverables. Also produces the valuation estimate (NC targets only) and the certified cold call opener.
**LLM Model:**
- Narrative: Claude CLI ($0.00) -- best quality for prose, free via subscription
- Valuation: GPT-4o Mini via OpenRouter ($0.002/call) -- reliable at structured financial estimates
- Certifier: Claude CLI ($0.00) -- final hallucination check
**Trigger:** Event-driven. Fires after Validator completes with no HIGH flags.
**Reads from:** `dossier_final` (researcher + validator outputs), `campaigns`, `targets`
**Writes to:** `dossier_final` (narrative, valuation, certification appended), `agent_queue` (trigger executor), `pipeline_log`, `dossier_cost_log`
**SQL Functions:** `is_step_done()`, `log_step()`, `get_entity_config()`
**Interacts with:** Receives from Validator. Dispatches to Executor.
**Campaigns served:** All dossier-producing campaigns.
**Cost per run:** ~$0.002/target (Claude CLI free, one GPT-4o Mini call for valuation)

**Three-step synthesis pipeline:**

Step 1 -- Narrative (Claude CLI, $0.00):
```
Inputs: validated researcher output, validator flags (to avoid blocked claims)
Outputs: executive_summary, owner_profile, company_narrative, competitive_moat,
         acquisition_appeal, risk_factors, cold_call_opener, key_quotes, narrative_score
```

Step 2 -- Valuation (GPT-4o Mini, $0.002) [NC targets only]:
```
Inputs: researcher output + narrative
Outputs: vertical, ebitda_estimate (range + confidence), multiple_range,
         ev_estimate (conservative/base/bull), active_buyers, value_drivers,
         value_detractors, letter_worthy (bool), valuation_score
```

Step 3 -- Certification (Claude CLI, $0.00):
```
Inputs: ALL previous outputs (researcher, validator, narrative, valuation)
Outputs: verdict (APPROVED/NEEDS_REVIEW/REJECTED), completeness_score,
         hallucination_count, hallucinations_found, validator_flags_respected,
         missing_fields, certified_cold_call_opener, certified_owner_name,
         certified_owner_vision, issues, final_score
```

**Abort rules:**
- If Steps 1-3 of the full pipeline (Research, Validate, Synthesize) fail -> abort this company entirely
- Valuation and Certification can fail non-fatally (the dossier is still usable for calls/emails)

---

### 7. EXECUTOR (The Craftsman)

**Name:** `executor`
**Role:** Produces customer-facing deliverables from validated dossier data. Letters, emails, call scripts, LinkedIn messages, voicemail scripts. Entity-specific tone and content.
**LLM Model:**
- Letters: Claude CLI ($0.00) -- best narrative quality, highest stakes document
- Call scripts: GPT-4o Mini via OpenRouter ($0.002/call) -- reliable at format following
- Emails/LinkedIn: GPT-4o Mini via OpenRouter ($0.002/call)
- Fallback: Claude CLI for everything (it is free and highest quality)
**Trigger:** Event-driven. Fires after Synthesizer completes (or directly after Validator for non-dossier campaigns).
**Reads from:** `dossier_final` (full dossier), `campaigns`, `targets`, `intelligence_cache`
**Writes to:** `approval_queue` (ALL deliverables start as DRAFT), `outreach_queue`, `sent_log`, `pipeline_log`, `dossier_cost_log`
**SQL Functions:** `is_step_done()`, `log_step()`, `get_entity_config()`, `check_dnc()`
**Interacts with:** Receives from Synthesizer. Writes to approval_queue for human review. After approval, writes to Dispatcher.
**Campaigns served:** All outreach campaigns.
**Cost per run:** ~$0.004/target (1-2 GPT-4o Mini calls, Claude CLI free for letters)

**Entity-Specific Deliverables:**

NC-SELL-LETTER:
```
- Physical letter to business owner (300-400 words)
- Personal, warm, respectful of owner's legacy
- References specific verified facts (review quote, founding year, award, personal detail)
- Includes valuation range
- CTA with personalized URL: https://nextchapter.deal/{slug}
- Signed as Mark DeChant, Managing Director, Next Chapter M&A Advisory
- Handwritten for $10M+ EV companies ($3-6), printed for sub-$10M ($0.50-2)
```

NC-SELL-CALL:
```
- Cold call script opener referencing the letter
- Make them say "how did you find that?"
- Voicemail: name and number at START and END
- Signed as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668
```

AND-LP-LETTER:
```
- Letter to family office/LP introducing AND Capital funds
- Institutional, professional, disciplined tone
- "$10B+ in transactions" / "Institutional-grade governance"
- NEVER say "private equity" -- use "former business owners who cashed out and buy companies because they believe in owners, not the stock market"
- Two fund pitches: Health & Wellness Innovation Fund (GP: Denise Brown, MD) and Energy Transition Fund (GP: Joe Park)
- Fee structure: 2% mgmt, 20% carry, 8% preferred return, GP co-investment
```

AND-LP-CALL:
```
- Call script for Mark/Ewing referencing the letter
- Book a fund presentation meeting
- Same tone rules as letter
```

RU-CLIENT:
```
- Email to VP Sales/CRO at SaaS company
- Mark's voice: "I've been an ad tech and marketing tech sales recruiter for 22 years"
- Direct, recruiter cadence
- Fee structure: flat search fee + % of salary + 6-month success fee
```

**Rules:**
- ALL documents stay DRAFT until manually approved
- Never include unverified facts in customer-facing content
- Only APPROVED or NEEDS_REVIEW (with caveats) data in documents
- Every document logged in sent_log with content_hash and provenance snapshot
- NEVER sound like a template. Every piece must reference at least ONE specific detail from the research.

---

### 8. APPROVER (The Human Gate)

**Name:** `approver`
**Role:** Human-in-the-loop review interface. Not an LLM agent -- this is a Lovable app + iMessage notification system.
**LLM Model:** None. This is a UI + notification layer.
**Trigger:** Event-driven. New items in `approval_queue`.
**Reads from:** `approval_queue`, `dossier_final`, `targets`
**Writes to:** `approval_queue` (status update), `feedback_log` (if human makes corrections), `agent_queue` (trigger dispatcher after approval)
**SQL Functions:** `advance_lifecycle()`

**Review Requirements:**

| What | Who Reviews | Sample Rate | SLA |
|---|---|---|---|
| Letters (all entities) | Ewing or Mark | 100% -- every letter | 24 hours |
| Research dossiers | Mark | 10% random sample | 48 hours |
| Call scripts | Mark | 10% random sample | 24 hours |
| Valuations (NC) | Ewing | 100% for $10M+ EV | 48 hours |
| Classification overrides | Ewing | Only when confidence < 2.0 | 72 hours |

**Notification Flow:**
1. New item enters approval_queue
2. If Ewing is away (IMESSAGE_BRIDGE_ENABLED=true): send via `~/.imessage-bridge/imessage-bridge.sh`
3. Format: `[Argus] Letter ready for review: {company_name} ({entity}). A) Approve B) Reject C) Edit. Reply A/B/C`
4. For batch notifications: `[Argus] 5 letters pending review. View at {lovable_app_url}. Reply OK to acknowledge.`
5. If no response in 24h: escalate with reminder

**Feedback Loop:**
When a human corrects a deliverable (edits tone, fixes a fact, changes classification), the correction is logged to `feedback_log` with:
- `original_output_json` -- what the agent produced
- `corrected_output_json` -- what the human changed it to
- `correction_type` -- tone, fact, classification, valuation

These corrections are loaded as few-shot examples in future agent prompts for the same entity+campaign combination. The system literally gets smarter with every correction.

---

### 9. DISPATCHER (The Sender)

**Name:** `dispatcher`
**Role:** Executes approved outreach. Loads dialers, sends letters, queues emails. Only fires AFTER human approval.
**LLM Model:** None. Pure API integration.
**Trigger:** Event-driven. Fires when approval_queue items move to `approved` status.
**Reads from:** `approval_queue` (approved items), `outreach_queue`, `do_not_call`, `dialer_queue`, `targets`
**Writes to:** `sent_log`, `dialer_queue`, `outreach_queue` (status update), `pipeline_log`
**SQL Functions:** `check_dnc()`, `advance_lifecycle()`, `log_step()`
**Interacts with:** Receives from Approver. Feeds Tracker with sent items.
**Campaigns served:** All outreach campaigns.
**Cost per run:** $0.00 for API calls (Salesfinity, letter mailing service). Letter mailing costs are operational, not LLM costs.

**Dispatch Logic:**

```
For each approved deliverable:
  1. FINAL DNC check (DNC could have been added since research phase)
  2. Route by channel:
     - Letter: queue for mailing service, log to sent_log with content_hash
     - Call: load contact to Salesfinity dialer_queue with entity tag, rep assignment
     - Email: queue for sending, log to sent_log
     - LinkedIn: queue for manual send by Mark/Ewing (no automation)
  3. Update outreach_queue status
  4. Advance lifecycle: Raw Lead -> Marketing Unqualified Lead
  5. Log to pipeline_log with entity + campaign_id
```

**Rep Assignment (Salesfinity):**
- NC targets: Ewing or John Kelly (NEVER Mark for NC cold calls unless explicitly assigned)
- AND LP targets: Mark (primary), Ewing (secondary)
- AND Deal Source: Mark
- RU targets: Mark or John Kelly (NEVER Ewing)
- Person routing rules from Entity Classification Guide are HARD constraints

**Six Pre-Load Gates (from salesfinity-loader skill):**
1. DNC table check
2. DNC flag check on target record
3. Dedup across all active Salesfinity lists
4. Geography filter (if campaign-specific)
5. Phone number required (no blanks)
6. Entity-correct naming convention on list name

---

### 10. TRACKER (The Listener)

**Name:** `tracker`
**Role:** Monitors all inbound responses across channels. Call outcomes from Salesfinity, email opens/replies, letter responses, LinkedIn messages. Updates target lifecycle.
**LLM Model:** Gemini 2.5 Flash Lite via OpenRouter ($0.001/call) for classifying call outcomes and extracting intent from responses.
**Trigger:** Scheduled. Salesfinity pull: hourly. Email monitoring: hourly. Fireflies transcripts: every 4 hours.
**Reads from:** Salesfinity API (`/v1/call-log`), Fireflies API, Gmail API (ewing@chapter.guide), `targets`, `sent_log`, `call_analysis`
**Writes to:** `response_log`, `call_analysis`, `targets` (lifecycle update), `intelligence_cache`, `nurture_schedule`, `do_not_call` (if DNC request), `agent_queue` (trigger nurture or re-engagement), `pipeline_log`
**SQL Functions:** `advance_lifecycle()`, `log_step()`, `check_dnc()`
**Interacts with:** Updates target lifecycle. Creates nurture_schedule items. Alerts Ewing on hot leads.
**Campaigns served:** All outreach campaigns.
**Cost per run:** ~$0.005/run (1 Gemini call per new response for classification)

**Response Classification:**

| Response Type | Lifecycle Action | Next Step |
|---|---|---|
| Interested / meeting booked | Advance to MQL | Alert Ewing via iMessage immediately |
| "Call me later" / "Not now" | Move to Nurture | Create nurture_schedule item |
| "Do not contact" / DNC | Add to do_not_call | Block across all entities, all channels |
| No answer / voicemail | Stay at MUL | Track touch count |
| Gatekeeper block | Stay at MUL | Flag for different approach |
| Negative / hostile | Move to Closed/Lost | Add to do_not_call if requested |

**Exhaustion Rule:** 3 emails + 2 calls + 1 letter with no response = mark exhausted. Remove from all active queues.

**Intelligence Accumulation:**
Every response is mined for intelligence and written to `intelligence_cache`:
- Best time to call (from call patterns)
- Gatekeeper name (from call transcripts)
- Owner preferences (from conversation content)
- Competitor intel (from any mentions)
- Seasonal patterns (busy seasons, slow periods)

This intelligence is loaded by future agent runs to improve personalization.

---

### 11. NURTURER (The Patient One)

**Name:** `nurturer`
**Role:** Re-engages targets after cooling periods. Manages the "not now" pipeline. Some of the best deals come from people who said "call me in 6 months."
**LLM Model:** Claude CLI ($0.00) for generating re-engagement messaging that references previous interactions.
**Trigger:** Scheduled daily at 7AM. Checks nurture_schedule for items where next_touch_date <= today.
**Reads from:** `nurture_schedule`, `targets`, `dossier_final`, `response_log`, `intelligence_cache`, `sent_log`
**Writes to:** `agent_queue` (trigger executor for new deliverable), `nurture_schedule` (update next_touch_date), `pipeline_log`
**SQL Functions:** `check_dnc()`, `get_entity_config()`, `advance_lifecycle()`
**Interacts with:** Creates work for Executor with nurture context (previous interactions, stated preferences, time elapsed).
**Campaigns served:** All outreach campaigns with nurture-eligible targets.
**Cost per run:** $0.00 (Claude CLI for messaging, pure logic for scheduling)

**Nurture Cadence:**

| Reason | First Re-touch | Second | Third | Then |
|---|---|---|---|---|
| "Call me in X months" | Exactly X months | +2 months | +3 months | Annual check-in |
| "Not selling yet" | 6 months | 12 months | 18 months | Annual |
| Seasonal (end of busy season) | Start of slow season | 6 months later | Annual | Annual |
| No response after letter | 30 days (different channel) | 60 days | 90 days | Mark exhausted |

**Re-engagement context loaded for Executor:**
```json
{
  "previous_touches": ["letter_sent_2026-01-15", "call_voicemail_2026-02-20"],
  "previous_response": "Said call back in spring, busy with HVAC season",
  "intelligence": {"best_time": "Tuesdays 9-11am", "gatekeeper": "Linda"},
  "time_since_last_touch": "42 days",
  "original_hook": "Founded company in 1992, BBB A+ rating for 30 years"
}
```

---

## ORCHESTRATION LAYER

### Event Bus

The system uses Supabase's `agent_queue` table as a lightweight event bus. No external message broker needed.

```
agent_queue schema:
  id: uuid (PK)
  agent_name: text (scout/classifier/researcher/validator/synthesizer/executor/dispatcher/tracker/nurturer)
  target_id: uuid (FK to targets)
  campaign_id: text (NC-SELL-LETTER, AND-LP-CALL, etc.)
  entity: text (next_chapter, and_capital, revsup)
  priority: int (1=urgent, 5=normal, 10=low)
  payload_json: jsonb (agent-specific input data)
  status: text (pending/claimed/done/failed)
  created_at: timestamptz
  claimed_at: timestamptz
  claimed_by: text (hostname of worker)
  completed_at: timestamptz
  error_msg: text
```

**Claim-and-process pattern (prevents double-processing):**
```sql
-- Atomically claim next work item
UPDATE agent_queue
SET status = 'claimed', claimed_at = now(), claimed_by = $hostname
WHERE id = (
  SELECT id FROM agent_queue
  WHERE agent_name = $agent AND status = 'pending' AND entity = $entity
  ORDER BY priority ASC, created_at ASC
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING *;
```

### Pipeline Flow

```
[TAM/Transcript/Referral] -> SCOUT -> agent_queue(classifier)
                                            |
                                      CLASSIFIER -> agent_queue(researcher)
                                            |
                                      RESEARCHER -> agent_queue(validator)
                                            |
                                      VALIDATOR ---+---> agent_queue(synthesizer) [if clean]
                                                   |
                                                   +---> approval_queue [if HIGH flags]
                                            |
                                      SYNTHESIZER -> agent_queue(executor)
                                            |
                                      EXECUTOR -> approval_queue [ALL deliverables]
                                            |
                                      [HUMAN REVIEW] -> approval_queue.status = approved
                                            |
                                      DISPATCHER -> sent_log, dialer_queue
                                            |
                                      TRACKER -> response_log, intelligence_cache
                                            |
                                      NURTURER -> nurture_schedule -> back to EXECUTOR
```

### Startup Sequence

On Mac mini boot (or process restart):

```bash
# 1. Watchdog (runs first, monitors everything else)
nohup python3 watchdog.py &

# 2. Orchestrator (master scheduler)
nohup python3 orchestrator.py &

# 3. Agent workers (one per agent, all listening on agent_queue)
nohup python3 worker.py --agent scout &
nohup python3 worker.py --agent classifier &
nohup python3 worker.py --agent researcher &
nohup python3 worker.py --agent validator &
nohup python3 worker.py --agent synthesizer &
nohup python3 worker.py --agent executor &
nohup python3 worker.py --agent dispatcher &
nohup python3 worker.py --agent tracker &
nohup python3 worker.py --agent nurturer &
```

Each worker process:
1. Polls `agent_queue` every 10 seconds for items matching its agent_name
2. Claims one item at a time (sequential waterfall -- M4 24GB constraint)
3. Processes it, writes results, creates next queue item
4. Sleeps 10 seconds between items (API breathing room)
5. If no items, sleeps 60 seconds before re-polling

---

## ERROR RECOVERY

### Agent-Level Recovery

| Error | Recovery |
|---|---|
| LLM API returns 429 (rate limit) | Exponential backoff: 15s, 30s, 60s. Circuit breaker opens after 3 consecutive failures. Provider disabled for 5 minutes. |
| LLM API returns 402/403 (auth/billing) | STOP immediately. Alert Ewing via iMessage. Do NOT sign up for replacement. |
| JSON parse failure | Triple fallback: direct parse -> strip markdown fences -> regex extract first {...} -> return parse_error with raw text |
| Claude CLI timeout (300s) | Dual fallback: BOTH OpenAI AND DeepSeek run the same prompt, results cross-checked. Prefer the one that parses as clean JSON; otherwise use the longer response. |
| Exa search failure | Log and retry once. If second failure, skip this search query (5 queries per target, losing 1 is survivable). |
| Supabase write failure | Retry 3x with 5s backoff. If persistent, write to local JSON file as backup, alert Ewing. |

### Pipeline-Level Recovery

| Condition | Response |
|---|---|
| Single target fails | Log error, mark agent_queue item as failed, skip to next target. Pipeline continues. |
| Same target fails 3x | Flag for human review in approval_queue. Remove from agent_queue. |
| 10 consecutive failures (any agent) | Pause that agent. Alert Ewing via iMessage. Other agents continue. |
| Orchestrator process dies | Watchdog detects within 15 minutes, restarts. All in-progress items have claimed_at timestamps -- anything claimed > 30 min ago is reset to pending by the orchestrator on restart. |
| Mac mini reboots | LaunchAgent plist auto-starts watchdog, which starts everything else. |

### Resume-from-any-step

Every agent checks `is_step_done()` before starting work. If a target has already been researched, the researcher skips it. If it has been validated, the validator skips it. This means:
- Kill the entire system mid-batch -> restart -> it picks up exactly where it left off
- No data loss (incremental storage after every step)
- No duplicate work (cache checks on every entry)

---

## COST MONITORING

### Budget Structure

| Entity | Daily Cap | Monthly Cap | Rationale |
|---|---|---|---|
| next_chapter | $5.00 | $100.00 | ~140 targets/day at $0.035/target. Primary revenue-generating entity. |
| and_capital | $3.00 | $60.00 | Lower volume, higher-value targets. LP research is deeper. |
| revsup | $1.00 | $20.00 | Ewing is inactive. Mark/John run it manually. Minimal automation. |
| system | $2.00 | $40.00 | Transcript mining, health checks, maintenance tasks. |

### Per-Target Cost Breakdown

| Step | Provider | Model | Cost |
|---|---|---|---|
| Scout (TAM scrape) | Exa | -- | $0.030 (5 searches) |
| Classifier | Python / Claude CLI | -- | $0.000 |
| Researcher (dual) | Gemini + DeepSeek | Flash Lite + V3 | $0.005 |
| Validator (dual) | DeepSeek + Llama | V3 + 3.3-70B | $0.006 |
| Synthesizer | Claude CLI | -- | $0.000 |
| Valuation | GPT-4o Mini | -- | $0.002 |
| Certifier | Claude CLI | -- | $0.000 |
| Letter/Script | Claude CLI + GPT-4o Mini | -- | $0.002 |
| **Total per target** | | | **~$0.045** |

### Cost Logging

Every LLM call logs to `dossier_cost_log`:
```json
{
  "entity": "next_chapter",
  "campaign_id": "NC-SELL-LETTER",
  "agent_name": "researcher",
  "provider": "openrouter",
  "model": "google/gemini-2.5-flash-lite",
  "tokens_in": 3200,
  "tokens_out": 1500,
  "cost_usd": 0.001,
  "target_id": "uuid",
  "created_at": "2026-03-28T..."
}
```

### Cost Alerts

| Threshold | Action |
|---|---|
| 50% of daily budget used | Log warning in pipeline_log |
| 80% of daily budget used | iMessage to Ewing: "[Argus] {entity} at 80% daily budget (${spent}/${cap}). Slowing down." |
| 100% of daily budget used | Pause all paid API calls for that entity. Claude CLI work continues (it is free). |
| Any single target costs > $0.50 | Flag in pipeline_log. Likely indicates retry loop or runaway. |
| Monthly budget > 90% | iMessage: "[Argus] {entity} at 90% monthly budget. {days_remaining} days left. A) Continue B) Pause. Reply A or B." |

### Why Claude CLI Changes the Economics

Claude CLI via subscription is $0.00/call with 150K context window. This means:
- ALL narrative work (synthesis, letters, cold call openers) = free
- ALL certification (final hallucination check) = free
- ALL nurture re-engagement messaging = free
- ALL ambiguous classification = free

The only paid costs are:
- Exa web search ($0.006/result for fresh data)
- Fast extraction models (Gemini Flash Lite at $0.001/call)
- Cross-check models (DeepSeek at $0.004/call)
- Structured output (GPT-4o Mini at $0.002/call)

This means the system can process ~2,200 targets/month for $100 on the NC budget alone. At scale, the per-target cost approaches $0.03 as Claude CLI handles more steps.

---

## HUMAN-IN-THE-LOOP TOUCHPOINTS

### Ewing Reviews

| Touchpoint | Frequency | Medium | Response Expected |
|---|---|---|---|
| Letter approval (NC + AND) | Every letter | iMessage + Lovable app | Approve / Reject / Edit |
| Valuation review ($10M+ EV) | Per qualifying target | iMessage summary | Approve / Adjust range |
| Budget alerts | When thresholds hit | iMessage | Continue / Pause |
| Classification overrides | When confidence < 2.0 | iMessage with context | Pick entity or reject |
| Weekly pipeline report | Sunday 5PM | iMessage + Slack | Acknowledge |
| Hot lead alert | Immediate on interested response | iMessage | Call instructions |

### Mark Reviews

| Touchpoint | Frequency | Medium | Response Expected |
|---|---|---|---|
| Research dossier sampling | 10% random | Lovable app (Next Chapter Reports) | Approve / Flag issues |
| Call script review | 10% random | Lovable app | Approve / Edit |
| NEEDS_REVIEW disclosures | Every flagged dossier | Lovable app | Decide: use with caveat or re-research |
| Daily call prep | Morning briefing | Slack daily briefing | Acknowledge priorities |

### Mark DeChant reviews everything

This is an existing hard rule. The approval system is designed so Mark sees the 10% sample of research AND all deliverables flow through the Lovable apps he already uses. Nothing changes his workflow -- the system just feeds him better content, faster.

---

## FEEDBACK LOOP: HOW HUMAN OVERRIDES IMPROVE FUTURE RUNS

### The Learning Cycle

```
1. Agent produces output (letter, classification, research)
2. Human reviews and either approves or corrects
3. If corrected:
   a. Original + corrected versions saved to feedback_log
   b. Correction type tagged (tone, fact, classification, valuation)
4. On next run for same entity+campaign:
   a. Agent loads recent feedback_log entries as few-shot examples
   b. System prompt includes: "Previous corrections for this campaign type:"
   c. Agent adapts behavior based on human preferences
5. Monthly: aggregate feedback patterns into updated prompt templates
   - If 5+ tone corrections say "too formal" -> adjust base tone
   - If classification keeps getting overridden for a vertical -> add to decision tree
   - If valuation multiples consistently adjusted -> update range defaults
```

### Concrete Examples

**Tone correction:**
Ewing edits an AND Capital letter to remove "private equity" and replace with "former business owners who cashed out." This correction is logged. Next AND Capital letter prompt includes: "CORRECTION HISTORY: Do not use 'private equity.' Instead say: 'former business owners who cashed out and buy companies because they believe in owners, not the stock market.'"

**Classification correction:**
A concrete company gets classified as AND Capital (industry = construction). Ewing overrides to Next Chapter (operating business being sold, not investment asset). This adds to the decision tree: "Concrete/precast when operating business being bought/sold = Next Chapter."

**Valuation correction:**
Mark adjusts an HVAC company valuation from 4-5x EBITDA to 3-4x. The system logs this and uses the corrected range as a reference point for similar-sized HVAC companies in the same geography.

### Intelligence Accumulation

Beyond corrections, every interaction makes the system smarter:

| Signal | Where Stored | How Used |
|---|---|---|
| Owner said "call me in spring" | intelligence_cache | Nurturer waits until March to re-engage |
| Gatekeeper named "Linda" | intelligence_cache | Call script references Linda by name |
| Owner loves BBB rating | intelligence_cache | Next letter/call emphasizes their rating |
| Competitor acquired a company | intelligence_cache | Next outreach references market activity |
| Best call time: Tuesday 9am | intelligence_cache | Dispatcher schedules calls accordingly |
| Owner's son runs operations | intelligence_cache | Succession signal added to dossier |

---

## CAMPAIGN-AGENT MATRIX

Which agents serve which campaigns:

| Campaign | Scout | Classify | Research | Validate | Synthesize | Execute | Dispatch | Track | Nurture |
|---|---|---|---|---|---|---|---|---|---|
| NC-SELL-LETTER | TAM + Transcript | Yes | Full dossier | Dual LLM | Narrative + Valuation | Letter + Call Script | Mail + Dialer | Call + Mail response | Yes |
| NC-SELL-CALL | Transcript | Yes | Enrichment only | DNC check | -- | Call script | Dialer | Call outcome | Yes |
| NC-BUY-OUTREACH | Transcript | Yes | Buyer intel | Dual LLM | Buyer profile | Proposal | Email | Email response | Yes |
| NC-TRANSCRIPT | Transcript mine | Yes | -- | -- | -- | -- | -- | -- | -- |
| NC-TAM | TAM scrape | Yes | -- | -- | -- | -- | -- | -- | -- |
| AND-LP-LETTER | Exa enrichment | Yes | Full dossier (LP focus) | Dual LLM | Narrative | LP Letter | Mail | Mail response | Yes |
| AND-LP-CALL | -- | Yes | Enrichment | DNC check | -- | Call script | Dialer | Call outcome | Yes |
| AND-LP-LINKEDIN | Exa enrichment | Yes | Profile research | Light validation | -- | LinkedIn msg | Manual queue | -- | Yes |
| AND-DEAL-SOURCE | Transcript | Yes | Banker research | Dual LLM | -- | Call script | Dialer | Call outcome | Yes |
| AND-FUND-DISTRO | -- | Yes | -- | -- | -- | Fund deck email | Email | Email open/reply | -- |
| RU-CLIENT | Referral intake | Yes | Company research | Light validation | -- | Email | Email | Email response | Yes |
| RU-CANDIDATE | -- | Yes | -- | -- | -- | -- | -- | -- | -- |
| RU-REFERRAL | Referral intake | Yes | -- | -- | -- | -- | -- | -- | -- |

Standalone campaigns (FORGE-BOOMERANG, BIOLEV-SALE, SEASWEET-ROOFING) are NOT automated. PEC-FRAUD is NEVER automated.

---

## IMPLEMENTATION PHASES

### Phase 0: Infrastructure (Week 1)
- [ ] Complete Phase 1 entity tagging on all transactional tables
- [ ] Create new v2 tables: `agent_runs`, `agent_queue`, `approval_queue`, `response_log`, `feedback_log`, `cost_budget`, `intelligence_cache`, `nurture_schedule`
- [ ] Create SQL functions: `is_step_done`, `log_step`, `log_verification_pair`, `claim_next_work`, `check_dnc`, `check_budget`, `advance_lifecycle`, `get_entity_config`
- [ ] Create views: `v_pipeline_status`, `v_daily_cost`, `v_approval_backlog`, `v_campaign_performance`, `v_agent_health`
- [ ] Seed `cost_budget` with initial caps
- [ ] Seed `campaigns` table with all 17 campaigns, entity-prefixed

### Phase 1: Core Pipeline (Week 2-3)
- [ ] Build `worker.py` base class (poll, claim, process, report pattern)
- [ ] Build `orchestrator.py` (cron scheduling + event routing)
- [ ] Build `watchdog.py` (process monitor + auto-restart)
- [ ] Port existing researcher, validator, synthesizer logic into worker pattern
- [ ] Port existing letter writer into executor worker
- [ ] Wire up classifier with `lib/classification.py` deterministic engine
- [ ] Build approval_queue notification system (iMessage bridge integration)
- [ ] Test end-to-end: single NC-SELL-LETTER target from raw to approved letter

### Phase 2: Discovery + Tracking (Week 4)
- [ ] Build scout agent: TAM scraping, transcript mining, referral intake
- [ ] Build tracker agent: Salesfinity pull, Fireflies pull, email monitoring
- [ ] Build dispatcher agent: dialer loading, letter mailing, email sending
- [ ] Wire up response_log -> lifecycle updates
- [ ] Wire up intelligence_cache accumulation

### Phase 3: Nurture + Learning (Week 5)
- [ ] Build nurturer agent: cooling period management, re-engagement
- [ ] Build feedback loop: correction logging, few-shot example loading
- [ ] Build daily briefing generation per entity
- [ ] Build weekly pipeline health report
- [ ] Build cost monitoring alerts

### Phase 4: Multi-Entity Expansion (Week 6)
- [ ] Extend all agents for AND Capital campaigns (LP letters, LP calls, deal sourcing)
- [ ] Extend all agents for RevsUp campaigns (client outreach, candidate sourcing)
- [ ] Consolidate 3 NYC Supabase instances into master-crm
- [ ] Build entity-scoped views and RLS policies
- [ ] Load test: run 50 NC + 20 AND + 10 RU targets simultaneously

### Phase 5: Continuous Operation (Week 7+)
- [ ] Set up LaunchAgent plist for Mac mini auto-start on boot
- [ ] Monitor for 1 week with full logging
- [ ] Tune polling intervals based on actual throughput
- [ ] Tune budget caps based on actual costs
- [ ] Hand off daily operations to the system

---

## MACHINE ALLOCATION

| Machine | Role in v2 |
|---|---|
| Mac mini (24GB, always-on) | All agent workers, orchestrator, watchdog. This is the production server. |
| MacBook-27 (Ewing's daily driver) | Approval UI via Lovable apps. Manual overrides. Claude CLI for ad-hoc queries. |
| MacBook-GREEN (broken screen, always-on) | War room display. Pipeline dashboards. Real-time agent_health view. |
| Cowork VMs | Disposable. Used only for one-off tasks (data migration, bulk backfill). NOT for continuous agents. |

---

## REPO STRUCTURE (master-crm)

```
master-crm/
├── agents/                    # Agent identity documents (v1 -- kept for reference)
│   ├── controller.md
│   ├── classifier.md
│   ├── researcher.md
│   ├── validator.md
│   └── executor.md
├── v2/                        # OpenClaw v2 agent system
│   ├── orchestrator.py        # Master scheduler + event router
│   ├── watchdog.py            # Process monitor + auto-restart
│   ├── worker.py              # Base worker class (poll, claim, process)
│   ├── agents/                # Agent implementations
│   │   ├── scout.py
│   │   ├── classifier.py
│   │   ├── researcher.py
│   │   ├── validator.py
│   │   ├── synthesizer.py
│   │   ├── executor.py
│   │   ├── dispatcher.py
│   │   ├── tracker.py
│   │   └── nurturer.py
│   ├── prompts/               # Entity-specific prompt templates
│   │   ├── next_chapter/
│   │   ├── and_capital/
│   │   └── revsup/
│   └── config/                # Campaign configs, budget caps, model assignments
│       ├── campaigns.json
│       ├── budgets.json
│       └── models.json
├── lib/                       # Shared code
│   ├── supabase_client.py     # Supabase connection + helpers
│   ├── classification.py      # Deterministic entity classifier
│   ├── llm_client.py          # Multi-provider LLM client with fallbacks
│   ├── exa_client.py          # Exa.ai web search
│   ├── enrichment_client.py   # Exa + Clay enrichment
│   └── cost_tracker.py        # Budget enforcement
├── campaigns/                 # Entity-specific business rules
│   ├── next_chapter/
│   ├── and_capital/
│   ├── revsup/
│   └── standalone/
├── data/
│   ├── north-star/            # Authority documents
│   ├── OPENCLAW-V2-ARCHITECTURE.md  # This document
│   └── exports/
└── CLAUDE.md                  # System instructions
```

---

## WHAT THIS REPLACES

| v1 (Current) | v2 (This Proposal) |
|---|---|
| `python3 pipeline.py run-all --limit 50` (batch, dies after) | Continuous worker polling agent_queue |
| Manual `claude -p` invocations | Automated Claude CLI calls within worker processes |
| No entity tagging | Entity column on every row, every query |
| Single pipeline for NC only | Multi-entity pipeline serving all 17 campaigns |
| No approval workflow | approval_queue with iMessage notifications |
| No response tracking | response_log + intelligence_cache |
| No nurture | nurture_schedule with automatic re-engagement |
| No cost monitoring | cost_budget with real-time enforcement and alerts |
| No feedback loop | feedback_log with few-shot learning |
| Crash = start over | Resume from any step via is_step_done() |

---

*This document is the blueprint. It does not execute anything. Implementation begins only after Ewing approves.*
