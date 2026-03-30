# Master CRM Buildout Scope — Reprocessed for Real Vision
**Date**: 2026-03-30
**Status**: CORRECTED PRIORITIES
**Vision**: Research agent finds buyers → letter engine writes in operator language with EBITDA framing → Lob mails humanlessly → Salesfinity calls 5x → prospect picks up → share URL → deal closes

---

## THE REAL NEXT 10 — Execution Machine, Not Plumbing

The previous buildout list prioritized internal guardrails, conflict resolution, and diff views. This list prioritizes the **customer-facing execution pipeline**. These 10 items turn the machine on.

### Priority 1: LETTER TEMPLATE ENGINE ⭐ START TONIGHT
**Why this first**: Every execution downstream depends on a personalized letter. This is the heartbeat.

**What it does**:
- Takes validated research (story cards, founder context, company data) from RESEARCHER
- Generates operator-friendly letters with EBITDA framing, not financial jargon
- Customizes greeting, lead story, call-to-action per entity (NC/AND/RU)
- Produces letter_text that feels personal, not templated
- Quality gate: reads like a peer (not a bot), mentions 1-2 specific stories, concrete metrics

**Inputs** (from RESEARCHER via queue):
- `target_id`, `story_cards` (array of 5 story categories)
- `founder_name`, `company_name`, `acquisition_status`
- `entity` (next_chapter|and_capital|revsup)
- `competitive_context`, `research_quality_score`

**Outputs** (to proposals table):
- `letter_text` (600-800 words, ready for Lob)
- `personalization_score` (0.0-1.0, how personal)
- `call_to_action` (entity-specific: "call me", "let's meet", "candidate profile")
- `tone_signal` (operator|investor|hiring_manager)

**Letter structure** (per entity):
- **NC**: "Saw [Story] in your market. Here's what's happening in [Industry]. You should know: [Metric]. Let's talk: [Phone]. -[Name]"
- **AND**: "Portfolio company thesis: [Market]. Your LPs saw [Return]. New deal we're underwriting in [Sector]. [Founder quote]. Meeting? [Calendar link]"
- **RU**: "Building [Team] with [Experience]. Saw your [Challenge]. Have 3 candidates who've solved this. 20-min call? [Time]"

**Success criteria**:
- No jargon (EBITDA yes, "synergy" no)
- One specific story per letter
- Reads like personal note, not form letter
- Mentions concrete metric or fact from research
- <800 words

**Execution approach**:
- Prompt engineering for entity-specific tone
- Few-shot examples of good letters by entity
- Validation check: does it pass "dinner party test"?
- Cost: ~$0.10 per letter (1 LLM call, no external APIs)

**Blocks on**: RESEARCHER must complete, confidence ≥2.0, research_quality_score ≥0.70
**Hands off to**: LOB INTEGRATION (prints physical letter)

---

### Priority 2: LOB API INTEGRATION
**Why this second**: Letters are worthless if they don't arrive in mailbox.

**What it does**:
- Takes certified letter_text from CERTIFIER
- Sends to Lob.com API with address from targets table
- Tracks delivery status (sent, delivered, returned)
- Costs $1.50-2.00 per letter (physical mail)
- Returns tracking ID for engagement correlation

**Inputs**:
- `letter_text`, `target_id`, `address` (physical)
- `entity`, `founder_name`

**Outputs**:
- `lob_tracking_id`
- `expected_delivery_date`
- `status` (sent|in_transit|delivered)
- Log cost to pipeline_log

**Integration points**:
- After CERTIFIER approves (certification_status = certified)
- Before NURTURER schedules follow-up emails/calls
- Listen for delivery webhooks from Lob (marks "arrived" in plays table)

**Blocks on**: CERTIFIER must approve, address validation pass
**Hands off to**: NURTURER (sequence follow-ups on delivery)

---

### Priority 3: CAMPAIGN MANAGER
**Why this third**: Need a central control panel to coordinate the machine. Without this, no visibility into what's sending, when, to whom.

**What it does**:
- UI to create campaigns (batch of targets + coordinated send schedule)
- Shows queue depth, processing status, delivery timeline
- Adjusts send cadence (batch by geography, time zone, day of week)
- Pauses problematic campaigns (DNC hits, failed addresses)
- Dashboard: targets ready → sent → delivered → responses in

**Tables**:
- `campaigns` (name, entity, target_count, send_schedule, status)
- `campaign_targets` (FK to campaigns & targets, status per target)
- `campaign_metrics` (sent_count, delivery_rate, response_rate, cost_total)

**UI components**:
- Campaign creation (select targets, set send dates)
- Queue monitor (live status of letters in flight)
- Delivery dashboard (map of where letters are)
- Response tracker (call answers, email opens, meeting bookings)

**Blocks on**: LOB INTEGRATION must be live (need to actually send)
**Enables**: SALESFINITY INTEGRATION (call list populated from delivery webhook)

---

### Priority 4: SAP RESEARCH TURBOCHARGING
**Why**: Current Exa rate limit (100/day) is insufficient. Need higher-velocity research.

**What it does**:
- Request Exa.ai rate increase to 500/day (or negotiate bulk pricing)
- Implement smarter query strategy (batch by industry, reuse competitor research)
- Pre-populate common competitor/market context (avoid redundant queries)
- Cache acquisition queries (same company checked once per week max)

**Changes to RESEARCHER**:
- Query budget: 2-3 per target (acquisition detection + 1-2 story queries)
- Industry caching: "HVAC market conditions as of [date]" reused across 10 targets
- Cost discipline: $0.05-0.08 per target (down from $0.10)

**Blocks on**: Nothing (parallel with other builds)
**Enables**: Higher throughput on 201 targets

---

### Priority 5: AUTO-REGENERATION FOR FAILED TARGETS
**Why**: Some targets fail (bad address, DNC hit, research quality too low). Need smart retry logic.

**What it does**:
- AUDITOR flags targets as "fixable" vs "unfixable"
- Fixable: re-run RESEARCHER with different search angle (try founder personal site, LinkedIn, SEC filings)
- If research_quality_score still <0.60 after retry, mark manual_review
- If address invalid, attempt address validation/correction
- If DNC hit, move to future-contact list (retry in 6 months)

**Retry rules**:
- Max 2 research retries per target (cost: $0.10/retry)
- Max 1 address correction attempt (free, via USPS database)
- DNC hits: flag but don't discard (save for nurture later)

**Blocks on**: AUDITOR must output clear "why it failed"
**Enables**: Higher success rate on full 201 targets

---

### Priority 6: SALESFINITY INTEGRATION
**Why**: Calls are the second motion. Letters open conversations; calls close them.

**What it does**:
- When Lob confirms letter delivered (webhook), create call task in Salesfinity
- Sync founder contact (name, email, phone) to Salesfinity contact record
- Populate call script (from EXECUTOR) with story hooks in Salesfinity
- After call, sync call notes back to plays table (engagement signal)
- Track outcome: answered|voicemail|declined|meeting_booked

**Inputs**:
- `lob_tracking_id`, `founder_name`, `phone`, `entity`
- `call_script` (from EXECUTOR)

**Outputs** (back to plays):
- `signal_type` = phone_call
- `outcome_category` = [outcome]
- `engagement_score` update
- `next_touch_recommendation`

**Integration points**:
- After LOB confirms delivery (5-7 days post-mail)
- Sync script format to match Salesfinity UI
- Listen for call completion webhook from Salesfinity

**Blocks on**: LOB delivery confirmation
**Enables**: LISTENER (aggregate inbound signals)

---

### Priority 7: SOURCE ATTRIBUTION & STORY TRACEABILITY
**Why**: Operator needs to know: where did this story come from? Which source said it?

**What it does**:
- RESEARCHER tags each story card with source (URL, LinkedIn post, news article)
- VALIDATOR verifies source is real (2+ sources = confident)
- Story card format includes: `{story, source_url, source_type (primary|secondary), confidence}`
- Letter template optionally references source in subtle way ("saw in recent [Publication]")
- Auditor can trace claim back to source

**Changes**:
- target_research.story_cards: add source fields
- Create story_sources table (story_id FK, url, type, date_found)
- VALIDATOR marks if claim is corroborated (2+ sources) vs single-source

**Blocks on**: Nothing (parallel with Letter Engine)
**Enables**: Higher audit confidence, transparency

---

### Priority 8: GRADUATED AUTO-TRUST (Listener Signal Aggregation)
**Why**: Once we see proof (call answered, meeting booked), we should trust and accelerate.

**What it does**:
- LISTENER aggregates inbound signals (call answers, email opens, meeting bookings)
- Engagement score: call answered +3.0, meeting +5.0, email reply +1.5, link click +1.0
- Score ≥10 = "proven interest" → escalate to deal structuring
- Score 5-9 = "active conversation" → accelerate nurture sequence
- Score <5 = "early stage" → continue normal cadence

**Logic**:
- Every inbound signal creates a play record (no signal is wasted)
- NURTURER reads engagement_score and adjusts timing
- Rep sees play status in Salesfinity and prioritizes high-score targets

**Scoring table**:
| Signal | Points |
|--------|--------|
| Call answered | +3.0 |
| Meeting booked | +5.0 |
| Email reply | +1.5 |
| Link clicked in email | +1.0 |
| Objection (interested but challenge) | -1.0 but continue |
| Opt-out | -10.0 STOP |

**Blocks on**: LISTENER must ingest signals, plays table schema
**Enables**: Smarter follow-up timing

---

### Priority 9: LISTENER AGENT (Multi-Channel Signal Ingestion)
**Why**: Calls and emails come in; we need to catch them and feed them back to the system.

**What it does**:
- Listen on Salesfinity for completed calls, logged outcomes
- Listen on email for replies to sent messages
- Listen on Lob webhooks for delivery confirmation
- Create play records for each signal
- Route based on engagement_score

**Channels**:
- Salesfinity call completion webhook → signal_type = phone_call, outcome = [from call log]
- Email reply detection → signal_type = email_reply
- Lob delivery webhook → signal_type = delivery_confirmation (starts nurture timer)
- Calendar event (if meeting booked) → signal_type = meeting_booked

**Output**:
- plays table with full history
- engagement_score calculation
- next_touch_recommendation

**Blocks on**: SALESFINITY INTEGRATION, email tracking setup
**Enables**: Closed-loop feedback

---

### Priority 10: MULTI-ENTITY RESEARCH TEMPLATES
**Why**: Current research finds generic stories. Needs industry-specific hooks.

**What it does**:
- Templates for story research by entity + sub_type
- **Trades (HVAC, plumbing, electrical)**: founder origin (garage start, trade apprentice?), local reputation, trade show presence, third-gen family history, disaster recovery stories
- **Healthcare**: compliance wins, previous business exit, consolidation track record, clinical team
- **SaaS/Hiring**: product origin story, technical co-founder origin, community/open-source contributions, hiring scale-up stories
- **AND Capital targets**: fund return thesis, recent exits, LP relationships, market positioning

**Changes to RESEARCHER**:
- Query strategy customized per sub_type
- Expected story categories shift (trades emphasize local reputation; SaaS emphasize product vision)
- Research quality rubric adjusted per entity

**Blocks on**: Nothing (parallel, informational)
**Enables**: Faster, more targeted research

---

## EXECUTION PLAN — THIS WEEK

| Priority | Build | Est. Time | Owner | Blocker |
|----------|-------|-----------|-------|---------|
| 1 | Letter Template Engine | **Tonight** | [You] | None |
| 2 | Lob API Integration | Tomorrow | [You] | #1 complete |
| 3 | Campaign Manager UI | Wed-Thu | [You] | #2 working |
| 4 | SAP Turbocharging | Thu (parallel) | [You] | Exa rate increase request |
| 5 | Auto-Regeneration | Fri (parallel) | [You] | AUDITOR spec clarity |
| 6 | Salesfinity Sync | Fri-Mon | [You] | Salesfinity API docs |
| 7 | Source Attribution | Wed (parallel) | [You] | None |
| 8 | Auto-Trust Scoring | Fri (parallel) | [You] | LISTENER schema |
| 9 | Listener Agent | Mon-Tue | [You] | All signal sources integrated |
| 10 | Research Templates | Tue (parallel) | [You] | None |

---

## WHAT THIS BUILDS

After Priority 1-3 complete (3-4 days):
- **1 real letter** can flow end-to-end: research → write → certify → print → mail → track delivery
- **Campaign manager** shows the queue
- **Call list** auto-populates from delivery confirmations
- **Operator picks up phone, has script, story context**

After all 10 complete (2 weeks):
- **Full closed loop**: research → letter → mail → call → email → objection handling → meeting → deal
- **Automated signal aggregation** feeds engagement scores
- **Auto-trust** accelerates high-intent targets
- **Smart retry** recovers failed research
- **Transparency**: every story traced to source, every action logged

---

## CURRENT SYSTEM STATE

**Completed (from overnight build)**:
- ✅ OpenClaw security hardening (API keys removed)
- ✅ 9 agent CLAUDE.md specifications created
- ✅ Master CRM schema verified (37 tables, Supabase dwrnfpjcvydhmhnvyzov)
- ✅ CLASSIFIER agent live (112 targets classified, 55.7%)
- ✅ RESEARCHER agent configured (10-query acquisition protocol, dinner party test quality gate)
- ✅ Classification cron running (every 30 minutes)

**Ready for Letter Engine**:
- Queue infrastructure (queue_items, status tracking, FOR UPDATE locks)
- RESEARCHER output available (story_cards, competitive_context, research_quality_score)
- VALIDATOR specification (quality gates before EXECUTOR)
- CERTIFIER specification (final approval before Lob)
- Database schema ready (proposals table for letter output)

---

## DECISION: START WITH LETTER TEMPLATE ENGINE TONIGHT

Why tonight:
- All upstream research is done (112 targets have stories)
- No external API dependency (just LLM + template logic)
- Most valuable (letters are the heartbeat of the machine)
- 4-5 hours of focused build time

This is where the rubber meets the road.

---

**Last Updated**: 2026-03-30 12:30 MST
**Version**: 1.0 — REPROCESSED FOR REAL VISION
