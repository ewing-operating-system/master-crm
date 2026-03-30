# Next 10 Features — Execution Plan
**Date**: 2026-03-30 14:30 MST
**Status**: Ready to build starting NOW
**Priority**: Meeting Page v2 FIRST (feeds everything downstream)

---

## THE NEXT 10 FEATURES (Ranked by Impact)

### FEATURE 1 (CRITICAL): Meeting Page v2 — Data Collection Engine 🔴 BUILD NOW
**Why First**: Every downstream document (letter, proposal, buyer targeting, valuation) is 10x better if meeting data is captured. This is the bottleneck.

**What it does**:
- **During-Meeting Form**: Live note-taking with structured capture
- **Post-Meeting Auto-Gen**: Instant summary + data completeness score
- **Downstream Data Flow**: Meeting notes → letter generation → proposal quality

**Form Fields to Capture** (During meeting):
```
Owner Motivation
- Dropdown: Looking to exit? Growing? Raising capital? Exploring options?
- Verbatim quote: [text area]

Timeline
- Dropdown: 3 months? 6 months? 12 months? No timeline?
- Confidence score: [slider 1-10]

Revenue Breakdown
- Annual revenue estimate: [number]
- Service %: [slider]  Install %: [slider]
- Recurring revenue %: [slider]
- Growth rate YoY: [number]

Margin Profile
- Estimated EBITDA: [number]
- EBITDA margin %: [slider]
- Owner perks/add-backs: [text area]

Key Employees
- Tech lead: [name, can they stay?]
- Operations lead: [name, can they stay?]
- Sales lead: [name, can they stay?]
- Critical person dependencies: [text area]

Deal Breakers
- Checkboxes: Acquire me, don't buy my customer list, keep me as operator, need full proceeds now
- Hidden deal killers: [text area]

Emotional Temperature
- Scale 1-10: Excited → Skeptical → Desperate
- Personality: [Analytical / Gut-trusting / Data-driven / Story-driven]

Story Elements Captured
- Why they started: [text area]
- Biggest challenge overcome: [text area]
- Community involvement: [text area]
- Team culture: [text area]

Post-Meeting Auto-Gen Output:
- Meeting summary (3 paragraphs, auto-generated from notes)
- Data completeness score ("You captured 11/12 fields")
- What this unlocks: "With this data, we can estimate valuation, identify ideal buyer, generate personalized letter"
- Action items: [auto-populated from conversation]
- Generate letter link: [button that pre-fills letter engine with captured data]
- Generate proposal link: [button that creates personalized proposal]
```

**Technical Implementation**:
- HTML5 form with localStorage auto-save
- Real-time data completeness tracker (visual progress bar)
- Post-meeting: fetch form data → LLM summary → display
- Buttons to trigger downstream (letter generation, proposal creation)

**Success Criteria**:
- Form captures all 12 fields
- Data saved after every field change
- Post-meeting summary is readable prose (not bullet points)
- Completeness score accurate
- Rep can hit "Generate Letter" button and get pre-filled letter within 5 seconds

**Estimated Time**: 4-5 hours (form + auto-save + LLM summary)
**Cost**: $0.10-0.15 per meeting (1 LLM call for summary)
**Blocks on**: Nothing (independent)
**Unblocks**: Letter Template quality, Proposal generation quality, Buyer targeting

---

### FEATURE 2: Letter Template Engine (with Meeting Data Integration) 🔴 BUILD NOW
**Why**: Transform meeting notes + research into operator-friendly personalized letters

**Integration**:
- Pulls meeting data captured in #1
- Pulls research from RESEARCHER agent
- Combines into narrative letter

**Output**: `letter_text`, `personalization_score`, ready for Lob

**Estimated Time**: 3-4 hours
**Cost**: $0.10/letter
**Blocks on**: Feature #1 (meeting data)
**Unblocks**: Lob Integration

---

### FEATURE 3: Lob API Integration 🟡 TOMORROW
**What it does**: Physical letter mailing via Lob API

**Flow**:
- Letter Template produces HTML
- Lob renders + prints + mails
- Webhook confirms delivery
- Tracking ID logged to Supabase
- Salesfinity notified (call list auto-populates)

**Success Criteria**:
- 5 test letters ordered
- Tracking status visible in Supabase
- Webhook logs delivery confirmation

**Estimated Time**: 3-4 hours
**Cost**: $1.50-2.00 per letter (Lob)
**Blocks on**: Feature #2
**Unblocks**: Campaign Manager

---

### FEATURE 4: Campaign Manager UI 🟡 WED-THU
**What it does**: Central control for 250/150 rule

**Rule**:
- Send up to 250 letters per batch
- Pause until 150 of those 250 have been called 5x each
- Salesfinity syncs call outcomes
- Campaign Manager shows progress

**Dashboard Elements**:
- Batch status: "Batch 1: 250 sent. 87/150 called 5x. Need 63 more."
- Batch history table
- Pause/Resume buttons
- Telegram notification on key milestones

**Estimated Time**: 5-6 hours
**Cost**: $0.00
**Blocks on**: Feature #3
**Unblocks**: Salesfinity Integration

---

### FEATURE 5: Meeting Page v2 Auto-Summary (Post-Meeting Flow) 🟡 WED
**What it does**: LLM-powered summary generation after meeting

**Input**: Form data from Feature #1
**Output**:
- Professional meeting summary (3 paragraphs)
- Data completeness scoring
- Next steps list
- Links to generate letter/proposal

**Estimated Time**: 2-3 hours
**Cost**: $0.10-0.15 per meeting
**Blocks on**: Feature #1
**Unblocks**: Downstream generation

---

### FEATURE 6: Salesfinity Integration 🟡 FRI-MON
**What it does**: Load contacts + track call outcomes

**Flow**:
- Lob delivery webhook → auto-populate Salesfinity contact
- Rep makes call → outcome logged
- Outcome syncs back to Supabase `plays` table
- Campaign Manager reads outcome count

**Estimated Time**: 4-5 hours
**Cost**: $0.00 (API integration)
**Blocks on**: Feature #3
**Unblocks**: Campaign Manager automation

---

### FEATURE 7: Interactive Proposal Auto-Generation 🟡 THU-FRI
**What it does**: Meeting data + Research → Interactive proposal in <5 seconds

**Flow**:
1. Meeting form complete + data captured
2. User clicks "Generate Proposal"
3. LLM synthesizes meeting + research
4. HTML proposal template populated
5. Page renders live

**Template Sections** (auto-populated from meeting):
- Executive Summary (uses captured story elements)
- Company Snapshot (from meeting revenue breakdown)
- Valuation (from meeting revenue + margins)
- EBITDA Levers (from industry profile)
- Process Timeline (matched to owner's timeline preference)
- Fee Structure (based on company size)

**Success Criteria**:
- Proposal generates in <5 seconds
- All fields populated from meeting data
- Personalization score ≥0.85
- Mobile responsive

**Estimated Time**: 4-5 hours
**Cost**: $0.05-0.10 per proposal (LLM synthesis)
**Blocks on**: Feature #1 (meeting data)
**Unblocks**: Scale to all targets

---

### FEATURE 8: SAP-Quality Buyer Research (All 193 Buyers) 🟡 PARALLEL (Autonomous)
**What it does**: Researcher agent fills 7 sections per buyer

**Sections**:
1. Company overview (revenue, headcount, ownership)
2. Acquisition history
3. Strategic rationale
4. Financial capacity / dry powder
5. Key decision-makers + contact info
6. Recent news & market moves
7. Approach strategy (warm intro, cold angle, story hook)

**Current State**: 20/193 buyers have this depth
**Target**: All 193

**Execution**: Cron job runs nightly, researcher agent processes batch
**Timeline**: Runs autonomously, 1-2 weeks to complete all 193
**Cost**: $0.50-0.80 per buyer (Exa.ai queries)

**Estimated Time**: 2 hours setup (rest is autonomous)
**Unblocks**: Better buyer targeting, personalized outreach

---

### FEATURE 9: Source Attribution on Every Fact 🟡 LATER
**What it does**: Footnote every claim with source URL

**Format**:
"Springer has 26-city coverage[1]" → click → shows source URL

**Implementation**:
- story_cards table: add `source_url`, `source_type` (primary/secondary), `corroboration_count`
- Proposal template: render footnotes
- Footer: auto-generate sources list

**Estimated Time**: 2-3 hours
**Cost**: $0.00
**Blocks on**: Research completion
**Unblocks**: Audit trail, transparency

---

### FEATURE 10: Graduated Auto-Trust 🟡 NEXT WEEK
**What it does**: Auto-send escalation based on approval history

**Rules**:
1. First 10 letters: manual approval via Telegram
2. Letters 11-50: auto-send with 24-hour inspection window
3. Letters 51+: auto-send immediately, log only

**Implementation**:
- Track approval count in Supabase `letter_campaigns` table
- Before send, check approval_count
- If <10: send to Telegram for approval
- If 11-50: auto-send, notify Telegram with preview link
- If 51+: auto-send silently, log only

**Estimated Time**: 2-3 hours
**Cost**: $0.00
**Blocks on**: Feature #3 (Lob Integration)
**Unblocks**: Scale to thousands

---

## EXECUTION TIMELINE

### TONIGHT (2-3 hours each, parallel possible)
- [ ] **Feature 1**: Meeting Page v2 form + auto-save
- [ ] **Feature 2**: Letter Template Engine with meeting integration

### TOMORROW (3-4 hours each)
- [ ] **Feature 3**: Lob API Integration (5 test letters)
- [ ] **Feature 5**: Post-meeting auto-summary

### WED-THU (4-6 hours each)
- [ ] **Feature 4**: Campaign Manager UI
- [ ] **Feature 7**: Interactive Proposal Auto-Generation

### FRI-MON (4-5 hours each)
- [ ] **Feature 6**: Salesfinity Integration
- [ ] **Feature 8**: SAP Buyer Research (setup, then autonomous)

### NEXT WEEK
- [ ] **Feature 9**: Source Attribution
- [ ] **Feature 10**: Graduated Auto-Trust

---

## CRITICAL SUCCESS PATH

**By Tomorrow EOD**:
- ✅ Meeting form captures 12 fields
- ✅ Letter template generates from meeting + research
- ✅ 5 test letters mailed via Lob
- ✅ Lob tracking IDs in Supabase

**By Friday EOD**:
- ✅ Campaign Manager shows batch status
- ✅ Proposals auto-generate from meeting data
- ✅ Salesfinity integration live

**By Next Week**:
- ✅ System running autonomously: research → meeting → letter → mail → call → response → next action

---

## THE MACHINE AT WORK

1. **Rep enters meeting with prospect** (opens Meeting Page v2)
2. **Rep captures owner's motivation, timeline, revenue, margins, story** (form auto-saves)
3. **Meeting ends, rep clicks "Generate Summary"** (LLM creates summary in 5 sec)
4. **Summary unlocks downstream**:
   - "Generate Personalized Proposal" button
   - "Generate Letter" button
   - "Identify Ideal Buyers" analysis
5. **Rep clicks "Generate Letter"** (Letter Template Engine pulls meeting notes + research → 4min)
6. **Rep approves letter, clicks "Mail"** (Lob sends physical letter)
7. **Lob delivery confirmed via webhook** (auto-populates Salesfinity with call task)
8. **Rep makes call** (outcomes logged)
9. **Listener Agent catches inbound signals** (email reply, meeting booked, etc.)
10. **System regenerates pages with new intel** (proposal updated, next steps suggested)

**Everything flows from meeting data capture.**

---

**Document Created**: 2026-03-30 14:30 MST
**Version**: 1.0 — NEXT 10 FEATURES
**Start**: Feature 1 (Meeting Page v2) RIGHT NOW
