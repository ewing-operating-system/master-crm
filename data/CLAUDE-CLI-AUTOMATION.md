# Claude CLI Automation Layer — Design Specification

**Author:** Argus (Claude Opus 4.6)
**Date:** 2026-03-28
**Status:** PROPOSAL — requires Ewing approval before implementation
**Companion docs:** Entity Classification Guide, Infrastructure Map, Extracted Business Rules

---

## Overview

Claude CLI (`claude -p --output-format text`) is the "brain" of the automation system. It runs locally on the Mac mini, costs $0.00 via subscription, and produces the highest-quality output of any available model. OpenClaw agents handle high-volume, structured tasks (research, validation, data plumbing). Claude CLI handles everything that requires judgment, synthesis, or customer-facing quality.

**Invocation pattern (all roles):**
```bash
echo "$PROMPT" | claude -p --output-format text
```
Prompts are ALWAYS piped via stdin. Never passed as CLI args (15K+ char prompts will timeout as args). Timeout: 300 seconds. Output captured via stdout.

**Fallback pattern (all roles):**
When Claude CLI fails (timeout, error, exit code != 0), DUAL FALLBACK fires — both OpenAI GPT-4o Mini AND DeepSeek Chat run the same prompt via OpenRouter. Results are cross-checked: prefer the one that parses as clean JSON; otherwise use the longer response. This is already implemented in `lib/llm_client.py` and must not be changed to single fallback.

---

## ROLE 1: HIGH-QUALITY SYNTHESIS

Customer-facing content generation. Every piece of text a prospect, LP, or hiring manager reads must pass through Claude CLI.

### 1A. Letter Writing (NC-SELL-LETTER, AND-LP-LETTER)

**Trigger:** Event — OpenClaw pipeline sets `dossier_status = 'CERTIFIED'` on a `dossier_final` row.

**What it reads from Supabase:**
- `dossier_final` — full certified dossier for the target company
- `dossier_provenance` — source URLs and excerpts for every fact
- `targets` — company metadata, entity tag, campaign assignment
- `campaigns` — campaign record (entity prefix determines content engine)
- `sent_log` — check for prior letters to this target (dedup)

**Prompt pattern:**
```
SYSTEM_CONTEXT=$(cat <<'SYSEOF'
You are writing a personalized certified mail letter. Entity: {entity}.
Campaign: {campaign_id}.

ENTITY-SPECIFIC RULES:
[If NC-SELL-LETTER]: From Mark DeChant, Managing Director of Next Chapter M&A Advisory.
  Tone: personal, respectful of owner's legacy, not pushy.
  Terms: success fees on closed M&A transactions.
  Framing: "We seek to bring you qualified buyers for your business."
  NEVER say "private equity." Say: former business owners who cashed out
  and buy companies because they believe in owners, not the stock market.
  Sign: Ewmarcus / Next Chapter M&A Advisory / 818-747-9668
  CTA: Personalized URL https://nextchapter.deal/{slug}

[If AND-LP-LETTER]: From Ewing Gillaspy or Mark DeChant.
  Tone: institutional, sophisticated, warm but credible.
  Terms: 2% management, 20% carried interest, 8% preferred return, GP co-investment.
  Fund verticals: Health & Wellness Innovation Fund (GP: Denise Brown, MD)
                   Energy Transition Fund (GP: Joe Park)
  Framing: institutional-grade governance, alignment of interests.

HARD RULES:
- 300-400 words
- Reference specific verified facts from the dossier
- Include valuation range (NC) or fund thesis alignment (AND)
- "This person actually researched us" feeling
- Every fact used MUST have a source_url in the provenance data
- Do NOT use any fact flagged HIGH severity in validator output
SYSEOF
)

DOSSIER_DATA=$(curl -s "$SUPABASE_URL/rest/v1/dossier_final?target_id=eq.$TARGET_ID" \
  -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY")

PROVENANCE=$(curl -s "$SUPABASE_URL/rest/v1/dossier_provenance?target_id=eq.$TARGET_ID" \
  -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY")

PROMPT="$SYSTEM_CONTEXT

=== DOSSIER ===
$DOSSIER_DATA

=== PROVENANCE ===
$PROVENANCE

Return JSON: {\"letter_text\": \"...\", \"hook_fact_used\": \"...\",
\"hook_source_url\": \"...\", \"personalized_url_slug\": \"...\",
\"mailing_address\": \"...\", \"letter_score\": 0-100}
Return ONLY valid JSON."

echo "$PROMPT" | claude -p --output-format text
```

**What it writes to Supabase:**
- `dossier_final` — updates `letter_text`, `letter_score`, sets `dossier_status = 'LETTER_DRAFTED'`
- `pipeline_log` — logs the generation event with entity tag, model used, cost ($0.00)
- `cost_log` — logs $0.00 entry with entity tag

**Handoff to OpenClaw:**
The executor agent picks up `LETTER_DRAFTED` rows. It does NOT send — it queues to `outreach_queue` with status `DRAFT_PENDING_REVIEW`. Nothing sends until human approval.

**Timeout/fallback:** 300s. On failure, dual OpenAI + DeepSeek fallback. Letter quality from fallback models is flagged `NEEDS_REVIEW_LLM_FALLBACK` for human inspection.

### 1B. Cold Call Scripts (NC-SELL-CALL, AND-LP-CALL, AND-DEAL-SOURCE)

**Trigger:** Event — enrichment stage finds a verified cell phone for a target.

**What it reads:** Same as 1A plus enrichment results (phone, email, LinkedIn).

**Prompt pattern:** Uses the outreach prompt template from `prompts/outreach_prompt.py` (Section 3.7 of business rules). Generates full outreach suite: cold email, call script, LinkedIn message, voicemail, direct mail.

**Entity-specific content:**
- NC: "How did you find that?" opener referencing owner's story, reviews, founding year
- AND: LP thesis alignment, fund performance, institutional credibility
- RU: Not currently automated (Mark and John handle manually)

**What it writes:** `dossier_final.outreach_suite` (JSON), `dossier_final.dossier_status = 'OUTREACH_DRAFTED'`

### 1C. Email Copy (All campaigns with enriched contacts)

**Trigger:** Event — outreach suite generated, email address available.

**Prompt pattern:** Subset of 1B — extracts and polishes the `cold_email_subject` and `cold_email_body` fields. Applies entity-specific signature and tone.

**What it writes:** `outreach_queue` entry with `channel = 'email'`, `status = 'DRAFT'`, `entity` tag.

### 1D. Narrative Generation (Dossier Synthesis)

**Trigger:** Event — OpenClaw validator sets `dossier_status = 'VALIDATED'`.

**What it reads:** Researcher output, validator output, all provenance.

**Prompt pattern:** Synthesizer prompt (Section 3.3 of business rules). Writes executive summary, owner profile, company narrative, competitive moat, acquisition appeal, risk factors, cold call opener.

**What it writes:** `dossier_final.narrative_*` fields, sets `dossier_status = 'SYNTHESIZED'`.

---

## ROLE 2: COMPLEX CLASSIFICATION (LLM Fallback)

When `lib/classification.py` returns confidence < 2.0, the record is ambiguous and needs LLM judgment.

**Trigger:** Event — Python classifier writes `classification_confidence < 2.0` to a record.

**What it reads from Supabase:**
- The unclassified record (from `targets`, `call_analysis`, `dialer_queue`, `pipeline_log`, or any transactional table)
- The Entity Classification Guide (read from disk: `data/north-star/NORTH-STAR-entity-classification-guide.md`)

**Prompt pattern:**
```
GUIDE=$(cat ~/Projects/master-crm/data/north-star/NORTH-STAR-entity-classification-guide.md)

PROMPT=$(cat <<PEOF
You are the entity classification engine for Ewing Gillaspy's three businesses.

=== CLASSIFICATION GUIDE ===
$GUIDE

=== RECORD TO CLASSIFY ===
Company: $COMPANY_NAME
Domain: $DOMAIN
Person: $PERSON_NAME
Title: $PERSON_TITLE
Industry: $INDUSTRY
Context: $CONTEXT
Source campaign: $SOURCE_CAMPAIGN

Apply the decision tree. Priority: Intent > Company Type > Person Role > Channel.

FAIL-SAFE RULES:
- RevsUp ONLY if hiring is present
- Next Chapter ONLY if a transaction is happening
- AND Capital ONLY if capital is involved
- If NONE apply, return entity: null. Do NOT force classification.

Return JSON:
{"entity": "next_chapter|and_capital|revsup|null",
 "sub_type": "LP|Investment|Sell-Side|Buy-Side|Recruiting|null",
 "confidence": "High|Medium|Low",
 "confidence_score": 0.0-3.0,
 "reason": "one sentence, intent-based",
 "decision_path": "Step X > Step Y > result"}

Return ONLY valid JSON.
PEOF
)

echo "$PROMPT" | claude -p --output-format text
```

**What it writes to Supabase:**
- Updates the record's `entity` field
- Updates `classification_method = 'llm_fallback'`
- Updates `classification_confidence` with the LLM's score
- Logs to `pipeline_log` with full decision rationale

**Handoff:** If LLM confidence is still < 2.0 (the LLM itself is uncertain), the record goes to `review_queue` with `reason = 'CLASSIFICATION_AMBIGUOUS'` for human decision.

**Throughput note:** Classification prompts are small (~3K chars including the guide). Can batch 50+ per minute. The guide is read from disk once and reused across the batch.

---

## ROLE 3: CERTIFICATION (Final QA Pass)

The last automated checkpoint before human review. Claude CLI reads the entire dossier, checks every fact against provenance, and produces a certification verdict.

**Trigger:** Event — OpenClaw valuator sets `dossier_status = 'VALUED'`.

**What it reads from Supabase:**
- `dossier_final` — all accumulated fields (researcher, validator, synthesizer, valuator output)
- `dossier_provenance` — every source URL and excerpt
- `dossier_runs` — step history for this target

**Prompt pattern:** Certifier prompt (Section 3.5 of business rules):
```
Certify dossier for {company}.

RESEARCHER: {researcher_output}
VALIDATOR: {validator_output}
SYNTHESIZER: {synthesizer_output}
VALUATOR: {valuator_output}

Verify every fact has a source URL.
Check that validator flags were respected (flagged facts not used in narrative).
Score completeness (0-100).
Catch hallucinations (facts with no provenance that appear in narrative).
Write a certified cold call opener.

Return JSON:
{"verdict": "APPROVED|NEEDS_REVIEW|REJECTED",
 "completeness_score": 0-100,
 "hallucination_count": 0,
 "hallucinations_found": [],
 "validator_flags_respected": true|false,
 "missing_fields": [],
 "certified_cold_call_opener": "opener text",
 "certified_owner_name": "name or null",
 "certified_owner_vision": "vision or null",
 "issues": [{"issue": "what", "severity": "HIGH|MEDIUM|LOW"}],
 "final_score": 0-100}

Be strict. Return ONLY valid JSON.
```

**What it writes:**
- `dossier_final.certification_verdict`, `certification_score`, `certified_opener`
- `dossier_final.dossier_status = 'CERTIFIED'` (if APPROVED) or `'NEEDS_REVIEW'` (if not)
- `pipeline_log` — certification event

**Hard rules:**
- Never approve a dossier with HIGH severity flags unresolved
- Never remove a flag because the data "seems right"
- NEEDS_REVIEW status is ALWAYS disclosed — never hidden

**Handoff:** APPROVED dossiers flow to letter writing (Role 1A). NEEDS_REVIEW dossiers go to `review_queue` for human triage. REJECTED dossiers get logged and skipped.

---

## ROLE 4: STRATEGIC ANALYSIS

Pipeline health, campaign performance, cost efficiency, win rates.

### 4A. Weekly Pipeline Report

**Trigger:** Cron — Sunday 8:00 PM MST.

**What it reads from Supabase:**
- `dossier_final` — status distribution, scores, entity breakdown
- `targets` — total counts by entity, campaign, status
- `sent_log` — letters sent this week by entity
- `dialer_queue` — queue depth by entity and rep
- `call_analysis` — call outcomes this week by entity
- `cost_log` — total spend this week by entity and provider
- `pipeline_log` — errors, retries, aborts this week
- `do_not_call` — new DNC entries this week

**Prompt pattern:**
```
You are the strategic analyst for Ewing Gillaspy's pipeline.
Generate the weekly pipeline report for the week ending {date}.

=== RAW DATA ===
{all_supabase_data_as_json}

REPORT STRUCTURE:
1. Executive Summary (3 bullets)
2. Pipeline Funnel by Entity (NC / AND / RU)
   - Raw leads → MUL → MQL → SQL → Opportunity → Signed → Active → Closed
3. Campaign Performance
   - Letters sent, calls made, responses received per campaign
4. Cost Efficiency
   - Total spend by entity and provider
   - Cost per dossier, cost per letter, cost per qualified lead
   - Use ACTUAL per-company cost averages from cost_log. Never round down.
5. Quality Metrics
   - Certification pass rate, hallucination rate, NEEDS_REVIEW rate
6. Blockers and Risks
   - API failures, rate limits, stale data, upcoming deadlines
7. Recommendations (max 3)

HARD RULES:
- NEVER generate from memory. Use only the data provided.
- NEVER list company names unless they match actual records.
- ALWAYS disclose NEEDS_REVIEW counts.
- Use actual cost averages, not aspirational benchmarks.

Return as markdown.
```

**What it writes:**
- Sends via iMessage to Ewing: `~/.imessage-bridge/imessage-bridge.sh "[Argus] Weekly pipeline report ready. {3-line summary}. Full report in Slack."`
- Posts to Slack Consolidation Canvas (`F0ANYTBD0HW`) via Slack MCP
- Stores in `pipeline_log` with `event_type = 'weekly_report'`

### 4B. Monthly Entity Deep-Dive

**Trigger:** Cron — 1st of month, 9:00 AM MST.

**Same pattern as 4A** but with 30-day lookback, trend analysis, entity-by-entity breakdown, and recommendations for campaign allocation.

### 4C. Daily Quick Pulse

**Trigger:** Cron — Monday-Friday, 7:00 AM MST.

**Lightweight version:** Reads only today's pipeline_log, cost_log, and any NEEDS_REVIEW items. Sends a 5-line iMessage summary to Ewing.

**iMessage format:**
```
[Argus] Daily Pulse — {date}
NC: {x} dossiers processed, {y} letters drafted, {z} NEEDS_REVIEW
AND: {x} LP targets enriched, {y} calls scored
Spend: ${total} ({provider breakdown})
Action needed: {yes/no — and what}
```

---

## ROLE 5: ORCHESTRATION DECISIONS

When the pipeline hits an ambiguous routing situation.

### 5A. Dual-Campaign Routing

**Trigger:** Event — a contact appears in multiple campaign queues, or a company could serve two entities.

**What it reads:**
- The contact/company record from all tables where it appears
- Campaign definitions for all matching campaigns
- Entity Classification Guide (from disk)

**Prompt pattern:**
```
A routing conflict has been detected.

RECORD: {record_json}
APPEARS IN: {list_of_campaigns}
ENTITY SIGNALS: {classification_signals}

Apply the Entity Classification Guide decision tree.
Rule: ACTION beats INDUSTRY 100% of the time.

Resolve to ONE entity and ONE campaign. If genuinely ambiguous, route to
NEEDS_REVIEW with your best guess and reasoning.

Return JSON:
{"resolved_entity": "...", "resolved_campaign": "...",
 "confidence": "High|Medium|Low",
 "reason": "...", "alternative_considered": "..."}
```

**What it writes:** Updates the record's entity and campaign fields. Logs decision to `pipeline_log`.

### 5B. DNC Conflict Resolution

**Trigger:** Event — a target is flagged DNC but has an active opportunity.

**Decision:** Claude CLI does NOT override DNC. It generates an alert to Ewing explaining the conflict and asking for a manual decision. DNC is universal and absolute.

### 5C. Exhaustion Detection

**Trigger:** Cron — daily, checks outreach counts per target.

**Rule:** 3 emails + 2 calls + 1 letter with no response = mark exhausted.

**What it writes:** Sets `lifecycle_status = 'exhausted'` on the target. Removes from `dialer_queue` and `outreach_queue`.

---

## ROLE 6: HUMAN COMMUNICATION

### 6A. iMessage Summaries

**Trigger:** After any significant pipeline event (batch completion, error, deadline approaching).

**Pattern:**
```bash
SUMMARY="[Argus] {event description}
{2-3 lines of context}
{action needed: A) option / B) option}"

~/.imessage-bridge/imessage-bridge.sh "$SUMMARY"
```

**Rules:**
- Start every message with `[Argus]`
- Include lettered choices when input is needed
- Describe temporary vs permanent consequences
- Keep under 5 lines (phone screen)

### 6B. Slack Updates

**Trigger:** After batch completions, weekly reports, error escalations.

**Target:** Consolidation Canvas (`F0ANYTBD0HW`) via Slack MCP tools.

### 6C. Email Drafts

**Trigger:** Manual — Ewing requests a draft to a client or partner.

**What it reads:** Relevant dossier data, prior correspondence (if available), entity context.

**What it writes:** Draft to Gmail via Gmail MCP tools, tagged with entity.

---

## CRON SCHEDULE

All times MST. All jobs run on the Mac mini.

### Hourly
| Time | Job | Claude CLI Role | Description |
|---|---|---|---|
| :00 | `call-ingest-classify` | Role 2 (Classification) | Ingest Salesfinity calls, classify entity on arrival |
| :30 | `review-queue-check` | Role 6A (iMessage) | If review_queue has items > 2 hours old, ping Ewing |

### Daily (Monday-Friday)
| Time | Job | Claude CLI Role | Description |
|---|---|---|---|
| 6:00 AM | `daily-maintenance` | (OpenClaw only) | DNC patterns, stale recycler, data quality |
| 7:00 AM | `daily-pulse` | Role 4C (Analysis) | Quick pipeline summary to Ewing via iMessage |
| 8:00 AM | `daily-tasks-created` | Role 1B, 1C (Synthesis) | Generate outreach for newly enriched contacts |
| 9:00 AM | `certification-batch` | Role 3 (Certification) | Certify any VALUED dossiers from overnight |
| 10:00 AM | `letter-batch` | Role 1A (Synthesis) | Generate letters for CERTIFIED dossiers |
| 6:00 PM | `exhaustion-check` | Role 5C (Orchestration) | Mark exhausted targets |

### Daily (Every day)
| Time | Job | Claude CLI Role | Description |
|---|---|---|---|
| 11:00 PM | `classification-sweep` | Role 2 (Classification) | Batch classify all untagged rows with confidence < 2.0 |

### Weekly
| Time | Job | Claude CLI Role | Description |
|---|---|---|---|
| Sun 8:00 PM | `weekly-report` | Role 4A (Analysis) | Full pipeline report to Slack + iMessage |
| Wed 6:00 PM | `priority-rebuild` | (OpenClaw only) | Dialer list priority rebuild |
| Sun 5:00 PM | `priority-rebuild` | (OpenClaw only) | Dialer list priority rebuild |

### Monthly
| Time | Job | Claude CLI Role | Description |
|---|---|---|---|
| 1st, 9:00 AM | `monthly-deep-dive` | Role 4B (Analysis) | Entity-level performance analysis |

---

## EVENT TRIGGERS

Events flow from OpenClaw agents to Claude CLI via status changes in Supabase. The orchestrator script polls `dossier_final` and other tables for status transitions.

| Event (Status Change) | Source | Claude CLI Role Triggered | Latency |
|---|---|---|---|
| `dossier_status` -> `VALIDATED` | OpenClaw validator | Role 1D (Narrative) then Role 3 (Certification) | Immediate (within polling cycle) |
| `dossier_status` -> `VALUED` | OpenClaw valuator | Role 3 (Certification) | Immediate |
| `dossier_status` -> `CERTIFIED` | Claude CLI Role 3 | Role 1A (Letter Writing) | Immediate |
| `classification_confidence < 2.0` written | Python classifier | Role 2 (Classification) | Next hourly sweep or immediate if in batch |
| Enrichment finds cell phone | OpenClaw executor | Role 1B (Cold Call Script) | Immediate |
| Enrichment finds email | OpenClaw executor | Role 1C (Email Copy) | Immediate |
| Contact appears in 2+ campaigns | Any ingest job | Role 5A (Routing) | Immediate |
| Target DNC'd with active opportunity | DNC sync job | Role 5B (DNC Alert) | Immediate |
| Pipeline error count > 5 consecutive | OpenClaw controller | Role 6A (iMessage alert) | Immediate |
| Batch completion | OpenClaw controller | Role 6A + 6B (iMessage + Slack) | Immediate |

**Polling mechanism:** A lightweight Python orchestrator (`lib/cli_orchestrator.py`) runs as a daemon on the Mac mini. It polls Supabase every 60 seconds for status transitions and dispatches Claude CLI calls. This avoids cron granularity issues and catches events within 1 minute.

---

## COST MODEL

### Claude CLI: $0.00 but Throughput-Limited

Claude CLI runs locally via subscription. No per-token cost. The constraint is throughput:
- **Estimated RPM:** ~10 requests per minute (conservative, based on `lib/llm_client.py` config)
- **Average prompt size:** 5-15K chars (varies by role)
- **Average response time:** 30-90 seconds per call
- **Effective throughput:** ~40-80 calls per hour

### Batching Strategy

| Role | Avg Prompt Size | Avg Response Time | Daily Volume | Daily Time |
|---|---|---|---|---|
| Letter writing | 12K chars | 60s | 5-20 letters | 5-20 min |
| Classification | 3K chars | 15s | 20-100 records | 5-25 min |
| Certification | 15K chars | 90s | 5-20 dossiers | 7-30 min |
| Narrative | 10K chars | 60s | 5-20 dossiers | 5-20 min |
| Outreach suite | 8K chars | 45s | 5-15 targets | 4-11 min |
| Daily pulse | 5K chars | 30s | 1 | 0.5 min |
| Weekly report | 20K chars | 120s | 0.14 (1/week) | 0.3 min |
| **TOTAL** | | | **40-175 calls/day** | **27-107 min/day** |

This fits comfortably within the Mac mini's 24/7 availability. Peak load (~175 calls) uses under 2 hours of Claude CLI time.

### Fallback Cost (When Claude CLI Fails)

Fallback fires DUAL: OpenAI + DeepSeek both run the same prompt.

| Provider | Cost per call | Expected fallback rate | Daily fallback cost |
|---|---|---|---|
| OpenAI GPT-4o Mini | $0.002 | 5% of calls (~5/day) | $0.01 |
| DeepSeek Chat | $0.004 | 5% of calls (~5/day) | $0.02 |
| **Total fallback** | | | **$0.03/day** |

**Budget caps (per session, from config.py):**
- Together: $4.50
- OpenAI: $5.00
- DeepSeek: $10.00
- Claude CLI: unlimited (free)

All costs logged to `cost_log` with entity tag.

---

## FEEDBACK INTEGRATION

Human overrides from the review queue feed back into future prompts.

### Review Queue -> Prompt Learning Loop

1. **Human classifies an ambiguous record:** The override is stored in `review_queue` with `human_entity`, `human_reason`, `override_timestamp`.

2. **Weekly feedback extraction (Sunday, before weekly report):**
   Claude CLI reads all human overrides from the past week. It generates a "lessons learned" summary:
   ```
   Read all records from review_queue where override_timestamp > {7_days_ago}.

   For each override, identify:
   - What the classifier got wrong
   - What signal the human used that the classifier missed
   - Whether this is a pattern or one-off

   Output: list of classification rule refinements to consider.
   ```

3. **Prompt refinement:** If a pattern emerges (e.g., "concrete companies keep getting classified AND when they should be NC"), the insight is added to the classification prompt's edge cases section. This is a MANUAL step — Claude CLI proposes the refinement, Ewing approves it.

4. **Letter quality feedback:**
   When Ewing marks a letter as `APPROVED` (good) or `REJECTED` (bad) in the review queue, the feedback is stored. Over time, the letter prompt accumulates approved examples as style references and rejected examples as anti-patterns.

### Feedback Storage

| Table | Column | Purpose |
|---|---|---|
| `review_queue` | `human_entity` | Human override of classification |
| `review_queue` | `human_reason` | Why the human chose differently |
| `review_queue` | `letter_verdict` | APPROVED/REJECTED for letter quality |
| `review_queue` | `letter_feedback` | Free-text feedback on what to fix |
| `pipeline_log` | `feedback_applied` | Boolean — was a feedback refinement applied to this prompt |

### Anti-Patterns (What NOT to Automate)

- Do NOT auto-update classification rules based on feedback. Always propose and wait for approval.
- Do NOT auto-send letters even if the review queue is empty. Human approval is a hard gate.
- Do NOT auto-override DNC for any reason.
- Do NOT auto-classify PEC-FRAUD records. That entity is MANUAL ONLY.

---

## ORCHESTRATOR ARCHITECTURE

### File: `lib/cli_orchestrator.py`

The orchestrator is a Python daemon that bridges OpenClaw events to Claude CLI invocations.

```
┌─────────────────────────────────────────────────────────────┐
│                     Mac mini (24/7)                          │
│                                                             │
│  ┌──────────────┐    polls     ┌──────────────────────┐     │
│  │  Supabase    │◄────────────►│  cli_orchestrator.py │     │
│  │  (master-crm)│             │  (daemon, 60s loop)  │     │
│  └──────┬───────┘             └──────────┬───────────┘     │
│         │                                │                   │
│         │  status changes                │  pipes prompt     │
│         │                                │  via stdin        │
│         ▼                                ▼                   │
│  ┌──────────────┐             ┌──────────────────────┐     │
│  │  OpenClaw    │             │  claude -p           │     │
│  │  Agents      │             │  (local, $0.00)      │     │
│  │  (research,  │             │                      │     │
│  │   validate,  │             │  Roles 1-6           │     │
│  │   enrich)    │             │                      │     │
│  └──────────────┘             └──────────┬───────────┘     │
│                                          │                   │
│                               on failure │                   │
│                                          ▼                   │
│                               ┌──────────────────────┐     │
│                               │  Dual Fallback       │     │
│                               │  OpenAI + DeepSeek   │     │
│                               │  (cross-checked)     │     │
│                               └──────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Outputs: iMessage, Slack, Gmail, Supabase       │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Daemon Loop Pseudocode

```python
while True:
    # 1. Check for status transitions
    new_validated = query("dossier_final", status="VALIDATED", needs_synthesis=True)
    new_valued = query("dossier_final", status="VALUED", needs_certification=True)
    new_certified = query("dossier_final", status="CERTIFIED", needs_letter=True)
    new_enriched = query("dossier_final", has_phone=True, needs_outreach=True)
    unclassified = query("targets", classification_confidence__lt=2.0, entity__is=None)
    routing_conflicts = query("review_queue", type="ROUTING_CONFLICT", resolved=False)

    # 2. Process each queue (sequential — one company at a time, M4 hardware constraint)
    for record in new_validated:
        run_claude_cli(role="narrative", target_id=record.id)

    for record in new_valued:
        run_claude_cli(role="certification", target_id=record.id)

    for record in new_certified:
        run_claude_cli(role="letter_writer", target_id=record.id)

    for record in new_enriched:
        run_claude_cli(role="outreach_suite", target_id=record.id)

    # 3. Batch classification (cheaper, can do many)
    if unclassified:
        for batch in chunks(unclassified, size=10):
            run_claude_cli(role="classifier", records=batch)

    # 4. Routing conflicts
    for conflict in routing_conflicts:
        run_claude_cli(role="router", record=conflict)

    # 5. Check for alerts
    check_error_threshold()
    check_review_queue_age()
    check_cost_caps()

    sleep(60)
```

### Sequential Processing Constraint

From the business rules: "Never process companies in parallel. One at a time, sequential waterfall. M4 24GB hardware constraint."

The orchestrator respects this. It processes one company through its full Claude CLI stage before moving to the next. Classification is the exception — those prompts are small enough to batch.

---

## IMPLEMENTATION ORDER

1. **Phase 0 (Now):** Write `lib/cli_orchestrator.py` skeleton with Supabase polling and Claude CLI subprocess dispatch.
2. **Phase 1:** Implement Role 2 (Classification) — highest immediate value, unblocks entity tagging of 4,000+ rows.
3. **Phase 2:** Implement Role 3 (Certification) — completes the dossier pipeline end-to-end.
4. **Phase 3:** Implement Role 1A (Letter Writing) — customer-facing output.
5. **Phase 4:** Implement Role 4C (Daily Pulse) — visibility for Ewing.
6. **Phase 5:** Implement Roles 1B, 1C, 5A-C — outreach and routing.
7. **Phase 6:** Implement Roles 4A, 4B, 6B, 6C — weekly/monthly reporting and Slack/email.

---

## APPENDIX: ENTITY-SPECIFIC PROMPT FRAGMENTS

These fragments are injected into prompts based on the `entity` field of the target record.

### Next Chapter (`next_chapter`)

```
Entity: Next Chapter M&A Advisory (chapter.guide)
Business: Boutique M&A advisory for home services
Target audience: Business owners in plumbing, HVAC, roofing, pest, water treatment, flooring, steel, concrete
Revenue model: Success fees on closed M&A transactions
Tone: Personal, respectful of owner's legacy, not pushy
Framing: "We seek to bring you qualified buyers for your business"
NEVER say: "private equity" — say: former business owners who cashed out and buy companies because they believe in owners, not the stock market
Signature: Ewmarcus / Next Chapter M&A Advisory / 818-747-9668
CTA: Personalized URL https://nextchapter.deal/{slug}
```

### AND Capital (`and_capital`)

```
Entity: AND Capital Ventures (andcapitalventures.com)
Business: Global investment portfolio — institutional-grade PE fund management + LP fundraising
Target audience: Family offices, RIAs, institutional allocators, hospital admins, energy executives
Revenue model: 2% management, 20% carried interest, 8% preferred return, GP co-investment
Fund verticals:
  - AND Capital Health & Wellness Innovation Fund (GP: Denise S. Brown, MD)
  - AND Capital Energy Transition Fund (GP: Joe Park)
Tone: Institutional, sophisticated, credible, warm
Track record: $10B+ in transactions, $1B+ across prior funds
Governance: Institutional-grade — investment committee, conflict management, MNPI controls, regulatory review
Key people: Teruel Carrasco (CEO), Rod Heard (Founder & MD), Ewing Gillaspy (MD, M&A), Loren Brink (President of M&A)
```

### RevsUp (`revsup`)

```
Entity: RevsUp (revsup.com)
Business: Contingent recruiting for revenue roles at SaaS companies
Target audience: VP Sales, CROs, VP CS at SaaS companies; AE/SDR/BDR candidates
Revenue model: Flat search fee + % of salary + 6-month success fee
Active reps: Mark DeChant (active), John Kelly (active), Ewing (inactive — occasional referral)
Tone: Direct, professional, no-nonsense recruiting
Note: Minimal automation. Most outreach is manual by Mark and John.
```

---

*End of specification. 6 roles, 14 sub-functions, 1 daemon, 1 cron schedule, 1 cost model, 1 feedback loop.*
