# System Audit Plan — OpenClaw Auditor Agent

**Date**: 2026-03-30 12:55 UTC
**Target**: Master CRM infrastructure, database, APIs, integrations
**Scope**: Full end-to-end audit of the system built in this session

---

## AUDIT OBJECTIVES

1. **Database Schema Validation** — Verify Supabase tables match code expectations
2. **API Contract Audit** — Verify endpoints exist, signatures match, error handling works
3. **Integration Verification** — Supabase ↔ Lob ↔ Salesfinity ↔ Telegram connections
4. **Data Flow Validation** — Trace data through Meeting Page → Letter → Lob → Campaign Manager
5. **Environment Configuration** — All secrets, keys, and configs in place
6. **Missing Implementation** — Flag what still needs to be built to wire everything together

---

## AUDIT SECTIONS

### 1. SUPABASE DATABASE AUDIT

**URL:** `https://dwrnfpjcvydhmhnvyzov.supabase.co`

#### Required Tables (Verify Each Exists)

```sql
-- Existing (VERIFY PRESENCE)
companies          — Sell-side targets (home services businesses)
targets            — Sell-side pipeline with status tracking
deal_research      — Buy-side research (buyers/acquirers) ✓ SAP quality exists

-- MUST CREATE (Check if exist, create if missing)
letter_approvals   — Letter approval queue
  Columns: id (UUID), company_id (FK), letter_text (TEXT), personalization_score (DECIMAL),
           status (TEXT: pending|approved|rejected), created_by (UUID), approved_by (UUID),
           approved_at (TIMESTAMP), rejected_reason (TEXT), notes (TEXT),
           created_at (TIMESTAMP), updated_at (TIMESTAMP)
  Index: company_id, status

letter_campaigns   — Campaign batch tracking for 250/150 rule
  Columns: id (UUID), batch_number (INT), status (TEXT: active|paused|completed),
           total_letters_sent (INT), letters_called_5x (INT), pause_threshold (INT),
           target_total (INT), created_at (TIMESTAMP), completed_at (TIMESTAMP)
  Index: batch_number, status

cost_ledger        — Cost tracking for Lob sends and enrichment
  Columns: id (UUID), cost_source (TEXT: lob|enrichment|research), cost_amount (DECIMAL),
           letter_id (UUID FK), company_id (UUID FK), cost_category (TEXT),
           created_at (TIMESTAMP)
  Index: cost_source, created_at
```

#### Existing Tables to Verify Structure

**For `deal_research` (buyer research):**
- Verify `extra_fields` JSONB has: notes, confidence, updated_at, call_opener, buyer_targets, story_narrative
- Verify `company_name` column exists (used for buyer name)
- Count rows: Should be ≥4 (SAP-quality buyer profiles exist)

**For `targets` (sell-side pipeline):**
- Verify columns: company_name, pipeline_status, research_completed_at, entity_confidence
- Check if `batch_number` column exists for campaign tracking (may need to add)
- Count rows: Should be ~200 (target list)

**For `companies` (home services leads):**
- Verify vertical, lead_stage, entity_confidence columns exist
- These are raw prospects, not qualified yet

#### Actions

1. Query each table with `SELECT COUNT(*)` — report row counts
2. Query table schema — compare against above spec
3. If tables missing: Generate CREATE TABLE SQL for auditor to execute
4. If columns missing: Flag which columns need to be added via ALTER TABLE
5. Check indices exist for performance-critical columns

---

### 2. API ENDPOINTS AUDIT

**Vercel Deploy:** `https://master-crm-web-eight.vercel.app` (or localhost for dev)

#### Required Endpoints (Verify Each Works)

**Letter Management:**
```
POST /api/letters/generate
  Input: { company_id, meeting_data, buyer_research_data }
  Output: { letter_text, personalization_score, tone_signal, estimated_valuation }
  Status: CREATED in this session ✓
  Test: Call with sample meeting data, verify response format

POST /api/letters/approve
  Input: { approval_id, approved_by }
  Output: { status: 'approved', approved_at }
  Status: NOT YET IMPLEMENTED
  Test: Verify endpoint exists, returns expected schema

POST /api/letters/send-to-lob
  Input: { approval_id, recipient_name, recipient_address_line1, recipient_city, recipient_state, recipient_zip }
  Output: { lob_letter_id, lob_status, tracking_url, expected_delivery_date, cost_incurred }
  Status: NOT YET IMPLEMENTED (lob-integration.js exists but not wired)
  Test: Call with test letter, verify Lob API key works

POST /api/webhooks/lob
  Input: Lob webhook payload (letter event)
  Output: { status: 200 }
  Behavior: Updates letter_approvals, inserts to cost_ledger, creates Salesfinity call task
  Status: NOT YET IMPLEMENTED
  Test: Simulate Lob webhook event, verify Supabase + Salesfinity updated
```

**Meeting Page:**
```
POST /api/meetings/save
  Input: { company_id, meeting_data_json }
  Output: { meeting_id, saved_at }
  Status: NOT YET IMPLEMENTED
  Test: Verify saves to Supabase meetings table

POST /api/meetings/generate-summary
  Input: { company_id, form_data }
  Output: { summary (3 paragraphs), action_items [], personalization_notes }
  Status: NOT YET IMPLEMENTED (needs LLM integration)
  Test: Call with sample meeting form, verify LLM summary is readable prose
```

**Campaign Manager:**
```
POST /api/campaigns/start-batch
  Input: { total_letters: 250 }
  Output: { batch_number, batch_id, status: 'active' }
  Status: NOT YET IMPLEMENTED

PATCH /api/campaigns/{batch_id}/pause
PATCH /api/campaigns/{batch_id}/resume
PATCH /api/campaigns/{batch_id}/complete
  Status: NOT YET IMPLEMENTED

POST /api/campaigns/batch-status
  Input: { batch_id }
  Output: { total_sent, called_5x, percentage, status, action_required }
  Status: NOT YET IMPLEMENTED
```

**Telegram Notifications:**
```
POST /api/telegram-notify
  Input: { channel_id, message, level: 'info|warning|error' }
  Output: { status: 'sent', message_id }
  Status: NOT YET IMPLEMENTED
  Test: Send test message to Telegram, verify delivery
```

**Proposals:**
```
POST /api/proposals/generate
  Input: { company_id, meeting_data }
  Output: { html_proposal, personalization_score, fee_estimate }
  Status: CREATED in this session (client-side generator.js) ✓
  Test: Call with sample data, verify <5s response time
```

#### Actions

1. Check which endpoints exist in `/api/` directory
2. For missing endpoints: Flag them as "MUST BUILD"
3. For existing endpoints: Test with sample payloads
4. Verify error handling (400s, 401s, 500s)
5. Verify response schemas match documented spec above

---

### 3. ENVIRONMENT & SECRETS AUDIT

#### Required Environment Variables

**Supabase:**
- `SUPABASE_URL` = `https://dwrnfpjcvydhmhnvyzov.supabase.co`
- `SUPABASE_ANON_KEY` = (Verify present, not hardcoded in client)
- `SUPABASE_SERVICE_ROLE_KEY` = (For server-side admin operations)

**Lob (Physical Mail):**
- `LOB_API_KEY` = (Verify present, starts with `live_` for prod or `test_` for dev)
- `LOB_WEBHOOK_SECRET` = (For signature verification)

**Salesfinity (Call Tracking):**
- `SALESFINITY_API_KEY` = (Verify present)
- `SALESFINITY_API_URL` = (Base URL for their API)

**Telegram (Notifications):**
- `EWING_TELEGRAM_CHAT_ID` = (Recipient chat for alerts)
- `TELEGRAM_BOT_TOKEN` = (For @MacMiniEwingBot)

**LLM (Meeting summaries, letter generation):**
- `OPENAI_API_KEY` or `CLAUDE_API_KEY` = (For LLM calls)
- `LLM_MODEL_ID` = (Which model to use)

#### Actions

1. Check `/Users/clawdbot/Projects/master-crm-web/.env.local` exists
2. Verify all keys present (NOT empty, NOT placeholder strings)
3. Check `/Users/clawdbot/.openclaw/.env` for OpenClaw secrets
4. Verify keys are NOT hardcoded in source files (audit code for leaks)
5. Test each key with a simple API call (Supabase SELECT, Lob test letter, etc.)

---

### 4. DATA FLOW VALIDATION

#### Flow 1: Meeting Capture → Letter Generation → Approval → Mail

```
Rep opens Meeting Page v2 (/meeting-page-v2.html)
  ↓
Form captures 12 fields (auto-save to localStorage)
  ↓
Rep clicks "Generate Summary"
  POST /api/meetings/generate-summary
  ↓ LLM returns 3-paragraph summary
  ↓
Summary displays with "Generate Letter" button
  ↓
Rep clicks "Generate Letter"
  POST /api/letters/generate (with meeting_data + buyer_research_data)
  ↓ Letter Template Engine returns letter_text + personalization_score
  ↓
Letter saved to letter_approvals (status='pending')
  ↓
Letter approval component shows at top of company page
  ↓
Rep clicks "Approve & Send"
  PATCH letter_approvals (status='approved')
  POST /api/letters/send-to-lob (letter_id, recipient_address, etc.)
  ↓ Lob API returns lob_letter_id + tracking_url
  ↓
Lob sends physical letter
  ↓
Lob webhook POST /api/webhooks/lob (letter.mailed event)
  ↓ Updates letter_approvals, inserts cost_ledger
  ↓
Lob webhook POST /api/webhooks/lob (letter.delivered event)
  ↓ Creates Salesfinity call task
  ↓
Rep sees "Call [Recipient] about their letter" in Salesfinity
```

**Audit checks:**
1. Meeting Page v2 loads with inline-editing.js and section-controls.js
2. Summary generation endpoint returns 3 paragraphs (not bullet points)
3. Letter generation returns personalization_score ≥0.80 for complete data
4. Letter approval queue shows on company pages (check data-company-id attribute)
5. Approve button triggers Lob send (verify lob-integration.js called)
6. Lob webhook signature verifies correctly
7. Salesfinity call task created with correct recipient name

---

#### Flow 2: Campaign Manager Tracking

```
Campaign Manager UI loads (/campaign-manager.html)
  ↓
Dashboard queries letter_campaigns table
  ↓ Shows: "Batch 3: 250 sent. 87/150 called 5x. Need 63 more."
  ↓
Every 30 seconds: query call_log (count calls per prospect in batch)
  ↓
When letters_called_5x reaches 150: enable "Resume" button, notify Telegram
  ↓
Rep clicks "Resume Batch"
  PATCH letter_campaigns (status='active')
  ↓
System can send next 250 letters
```

**Audit checks:**
1. letter_campaigns table populated with batch history
2. call_log table has batch_number column (for filtering)
3. 30s sync loop working (check browser console for interval logs)
4. Telegram notification sent when threshold hit
5. Resume button disabled until 150 threshold met

---

### 5. INTEGRATION VERIFICATION

#### Supabase ↔ Lob
- **Endpoint exists**: POST /api/letters/send-to-lob
- **Lob API key valid**: Test with `curl -u ${LOB_API_KEY}: https://api.lob.com/v1/us_verifications`
- **Letter format accepted**: Lob expects HTML, PDF, or raw text
- **Cost tracking accurate**: Verify cost_ledger gets populated after letter.mailed webhook

#### Lob ↔ Salesfinity
- **Webhook receiver works**: POST /api/webhooks/lob creates Salesfinity task
- **Salesfinity API reachable**: Test with sample task creation
- **Recipient name passed correctly**: Verify task shows recipient name

#### Telegram Notifications
- **Bot token valid**: Test `curl -X POST https://api.telegram.org/bot{TOKEN}/sendMessage -d chat_id={CHAT_ID}&text=test`
- **OpenClaw integration**: Verify `openclaw message send --channel telegram` works
- **Campaign milestones trigger**: Batch start, threshold hit, completion all notify

#### LLM Integration (for summaries + letter generation)
- **API key valid**: Test with sample completion request
- **Model selected**: Verify correct model ID in config
- **Prompt quality**: Run 3 test requests, check response quality
- **Latency acceptable**: Measure time for summary generation (<10s) and letter generation (<5s)

---

### 6. MISSING IMPLEMENTATIONS (Flag These)

**CRITICAL (blocks entire flow):**
- [ ] POST /api/letters/approve endpoint
- [ ] POST /api/letters/send-to-lob endpoint (wire lob-integration.js)
- [ ] POST /api/webhooks/lob endpoint (webhook receiver)
- [ ] POST /api/meetings/save endpoint (persist form to Supabase)
- [ ] POST /api/meetings/generate-summary endpoint (LLM integration)
- [ ] letter_approvals table creation (SQL)
- [ ] letter_campaigns table creation (SQL)
- [ ] cost_ledger table creation (SQL)

**HIGH PRIORITY (needed for full campaign flow):**
- [ ] POST /api/campaigns/start-batch endpoint
- [ ] PATCH /api/campaigns/{batch_id}/pause endpoint
- [ ] PATCH /api/campaigns/{batch_id}/resume endpoint
- [ ] POST /api/telegram-notify endpoint
- [ ] call_log.batch_number column (for campaign tracking)

**MEDIUM PRIORITY (nice to have):**
- [ ] POST /api/proposals/generate endpoint (wire proposal-auto-generator.js)
- [ ] Source attribution (footnotes in proposals)
- [ ] Salesfinity integration (create call tasks from webhook)

---

### 7. AUDIT EXECUTION CHECKLIST

**Phase 1: Schema Validation (30 min)**
- [ ] Query each required table, verify structure
- [ ] Flag missing tables and columns
- [ ] Generate CREATE TABLE / ALTER TABLE SQL if needed

**Phase 2: API Endpoint Validation (45 min)**
- [ ] List all endpoints in /api directory
- [ ] Test each endpoint with sample payloads
- [ ] Report which endpoints missing vs. implemented
- [ ] Test error handling (400s, 401s, 500s)

**Phase 3: Environment Validation (15 min)**
- [ ] Check all secrets present in .env.local and OpenClaw config
- [ ] Verify no hardcoded keys in source code
- [ ] Test each API key (Supabase SELECT, Lob test, Salesfinity ping)

**Phase 4: Data Flow Validation (30 min)**
- [ ] Trace end-to-end: Meeting → Letter → Approval → Lob → Salesfinity
- [ ] Test at each step with sample data
- [ ] Verify data persists correctly in Supabase

**Phase 5: Integration Verification (20 min)**
- [ ] Test Supabase ↔ Lob connection
- [ ] Test Lob ↔ Salesfinity (webhook → task creation)
- [ ] Test Telegram notifications
- [ ] Test LLM API (summary + letter generation latency)

**Phase 6: Missing Implementations Report (15 min)**
- [ ] Compile list of missing endpoints
- [ ] Compile list of missing tables
- [ ] Prioritize by criticality
- [ ] Generate implementation roadmap

---

## AUDIT OUTPUT FORMAT

After completing all sections, generate a report with:

```markdown
# System Audit Report — Master CRM
**Date**: [audit_date]
**Status**: [READY | NEEDS_FIXES | BLOCKED]

## Summary
- [X] items verified ✓
- [ ] items flagged for fix
- [ ] critical blockers

## Database Schema
✓ Existing tables: companies, targets, deal_research
✗ Missing tables: letter_approvals, letter_campaigns, cost_ledger
  → SQL to create: [generated CREATE TABLE statements]
✗ Missing columns: batch_number (in call_log)
  → SQL to add: [generated ALTER TABLE statements]

## API Endpoints
✓ Implemented: GET /api/letters (stub), POST /api/proposals/generate
✗ Missing: POST /api/letters/approve, POST /api/letters/send-to-lob, etc.
  → Implementation roadmap: [list in priority order]

## Environment Secrets
✓ Present: SUPABASE_URL, SUPABASE_ANON_KEY
✗ Missing: LOB_API_KEY, LOB_WEBHOOK_SECRET, SALESFINITY_API_KEY
  → Action: Load from OpenClaw secrets manager

## Data Flow Validation
✓ Meeting Page v2 → Summary generation: WORKING
✗ Letter approval → Lob send: BLOCKED (endpoint missing)
✗ Lob webhook → Salesfinity task: BLOCKED (webhook receiver missing)

## Integration Status
✓ Supabase reachable (verified with SELECT test)
✗ Lob API: Key missing, cannot test
✗ Salesfinity: Key missing, cannot test
✗ Telegram: Cannot test without chat ID

## Critical Blockers (MUST FIX BEFORE PRODUCTION)
1. Create letter_approvals table
2. Create letter_campaigns table
3. Implement POST /api/letters/send-to-lob
4. Implement POST /api/webhooks/lob
5. Load LOB_API_KEY from secrets

## Next Steps
1. Execute generated SQL in Supabase dashboard
2. Build 5 missing API endpoints (prioritized list)
3. Load missing environment secrets
4. Re-run audit to verify fixes
```

---

## INSTRUCTIONS FOR AUDITOR AGENT

1. **Do NOT ask questions** — audit autonomously
2. **Report facts only** — what exists, what's missing, what works, what's broken
3. **Generate SQL and code** — if something's missing, provide the implementation
4. **Prioritize by impact** — flag critical path blockers first
5. **Provide remediation** — for each issue, suggest the fix
6. **Test as you go** — verify each endpoint, table, and integration
7. **Output this audit report** — send to `/Users/clawdbot/Projects/master-crm/AUDIT-REPORT.md`

---

**Ready for OpenClaw auditor agent to execute.**
