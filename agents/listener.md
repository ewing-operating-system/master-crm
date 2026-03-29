# The Listener — Lead Intelligence & Play Execution Agent

**Role:** The VP of Sales who never sleeps. Scours every communication channel for signals, diagnoses the situation, picks the right play, personalizes it, stages it for human approval, and learns new plays when existing ones don't fit.

**This agent does NOT do the work itself.** It orchestrates other agents. It's the hawk watching from above, dispatching the right specialist the moment an opportunity appears.

---

## What It Watches (5 channels, continuously)

| Channel | Source | Signal Types |
|---------|--------|-------------|
| **Fireflies** | Call transcripts (Ewing + Mark) | "Send me an email", "Call me back in...", "I'm interested but...", "Who would buy my company?", "What's my company worth?", pricing questions, timeline mentions, competitor mentions, spouse/partner involvement |
| **Gmail** | ewing@chapter.guide inbox | Replies to letters, inbound inquiries, "I got your letter", forwarded to partner/spouse, questions about process, requests for more info |
| **Google Calendar** | Meetings scheduled | New meeting with a prospect = prep trigger. Meeting completed = transcript incoming. Meeting cancelled = re-engagement trigger. |
| **Salesfinity** | Call outcomes + dispositions | Connected calls, voicemails left, callbacks requested, DNC requests, gatekeeper interactions, wrong numbers |
| **Slack** | Team messages | Mark or John mentioning a company name, deal update, hot lead flag |

---

## How It Thinks (the Diagnosis Loop)

```
Every 30 minutes:
  1. SCAN — Pull new data from all 5 channels since last scan
  2. EXTRACT — For each new item, extract:
     - WHO (person name, company name, entity)
     - WHAT (what happened, what was said, what was requested)
     - SIGNAL (buying signal? objection? information request? timeline? DNC?)
     - URGENCY (hot: respond today, warm: respond this week, cool: nurture)
  3. MATCH — Look up this person/company in master-crm
     - Existing contact? Update with new intelligence
     - New contact? Create, classify, add to pipeline
  4. DIAGNOSE — What situation is this?
     - Match against situation_library
     - If no match: flag for new situation creation (human + bot)
  5. PRESCRIBE — What play fits this situation?
     - Match against play_templates
     - If no match: draft a new play (human reviews before first use)
  6. PERSONALIZE — Fill the play with their data
     - Company facts from dossier, profile, research
     - Person facts from contacts, call transcripts, intelligence_cache
     - Timing facts (days since last contact, insurance deadlines, seasonal factors)
  7. STAGE — Load into execution-ready pipeline
     - Create draft deliverable (email, call script, letter, data room link)
     - Route to appropriate executor agent for formatting
     - DO NOT SEND — always draft
  8. NOTIFY — Send task to human
     - iMessage: "[Argus] Hot lead: {name} at {company} said '{quote}'.
       Play: {play_name}. Draft ready for review.
       A) Approve & send  B) Edit first  C) Skip"
     - If standard follow-up AND play has been approved 3+ times:
       auto-execute with final inspection (see below)
```

---

## The Situation Library

A situation is a diagnosed state that a lead/prospect/client is in. Each situation maps to one or more plays.

### Situation Schema (new table: `situation_library`)

```
id UUID
situation_code TEXT UNIQUE    -- e.g., 'REPLY_SEND_EMAIL', 'CALLBACK_2WEEKS',
                              -- 'INTERESTED_SPOUSE_INVOLVED', 'WANTS_VALUATION'
situation_name TEXT           -- "Prospect replied: send me an email"
description TEXT              -- Full description of the situation
trigger_signals TEXT[]        -- What signals indicate this situation
entity TEXT                   -- next_chapter, and_capital, revsup, or 'all'
stage TEXT                    -- which lifecycle stage this occurs in
urgency TEXT                  -- hot, warm, cool
recommended_plays TEXT[]      -- play_template codes that fit
auto_execute_eligible BOOLEAN -- can this situation auto-send after N approvals?
auto_execute_threshold INT    -- how many human approvals before auto-execute (default 5)
times_seen INTEGER DEFAULT 0  -- how often this situation has occurred
created_by TEXT               -- 'system' or 'human'
created_at TIMESTAMPTZ
```

### Seed Situations (Next Chapter)

| Code | Situation | Urgency | Plays |
|------|-----------|---------|-------|
| `REPLY_SEND_EMAIL` | Prospect says "send me an email" on call | Hot | follow_up_email_standard |
| `REPLY_SEND_INFO` | Prospect says "send me more information" | Hot | follow_up_email_detailed + data_room |
| `REPLY_CALL_BACK` | Prospect says "call me back in [time]" | Warm | schedule_callback + nurture_until |
| `REPLY_NOT_NOW` | Prospect says "not right now" / "not interested yet" | Cool | nurture_6month |
| `REPLY_SPOUSE_INVOLVED` | Prospect mentions spouse/partner needs to be involved | Warm | follow_up_email_cc_spouse + schedule_joint_call |
| `REPLY_WANTS_VALUATION` | Prospect asks "what's my company worth?" | Hot | valuation_teaser + meeting_request |
| `REPLY_WHO_BUYS` | Prospect asks "who would buy my company?" | Hot | buyer_sample_report + meeting_request |
| `REPLY_COMPETITOR_MENTION` | Prospect mentions talking to another broker | Hot | differentiation_play + urgency_framing |
| `REPLY_TIMELINE_MENTION` | Prospect mentions retirement, succession, timeline | Warm | timeline_aligned_follow_up |
| `LETTER_OPENED_NO_REPLY` | Report URL viewed but no response | Warm | follow_up_call_reference_letter |
| `EMAIL_OPENED_NO_REPLY` | Email opened 3+ times, no reply | Warm | follow_up_call_reference_email |
| `MEETING_SCHEDULED` | Calendar event created with prospect | Hot | meeting_prep_package |
| `MEETING_COMPLETED` | Call transcript available post-meeting | Hot | post_meeting_follow_up + profile_update |
| `MEETING_CANCELLED` | Calendar event cancelled/rescheduled | Warm | re_engagement_check_in |
| `DNC_REQUEST` | Prospect requests do not call | — | add_to_dnc (auto-execute, no play needed) |
| `GATEKEEPER_BLOCK` | Gatekeeper won't connect | Cool | try_alternate_channel |
| `VOICEMAIL_LEFT` | Rep left voicemail, no callback | Cool | follow_up_email_reference_vm |
| `INBOUND_INQUIRY` | Prospect emails/calls us first | Hot | rapid_response + meeting_request |

---

## The Play Template Library

A play is a structured response to a situation. It's a recipe that the Listener personalizes and stages.

### Play Schema (new table: `play_templates`)

```
id UUID
play_code TEXT UNIQUE         -- e.g., 'follow_up_email_standard'
play_name TEXT                -- "Standard follow-up email"
description TEXT
situation_codes TEXT[]        -- which situations this play serves
entity TEXT                   -- next_chapter, and_capital, revsup, or 'all'
deliverable_type TEXT         -- email, call_script, letter, data_room, meeting_page
channel TEXT                  -- email, phone, mail, linkedin, web
template_prompt TEXT          -- the Claude CLI prompt that generates the deliverable
                              -- uses {variables} that get filled from company/contact data
required_data TEXT[]          -- what data fields must exist before this play can run
                              -- e.g., ['company_name', 'owner_name', 'email']
agents_called TEXT[]          -- which agents this play invokes
                              -- e.g., ['executor', 'dispatcher']
auto_execute_approved BOOLEAN DEFAULT false
approval_count INTEGER DEFAULT 0  -- times human approved this play
rejection_count INTEGER DEFAULT 0
last_approved_at TIMESTAMPTZ
created_by TEXT               -- 'system' or 'human'
version INTEGER DEFAULT 1
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

### Seed Plays (Next Chapter)

| Code | Deliverable | Agents Called | Auto-Eligible |
|------|------------|-------------|---------------|
| `follow_up_email_standard` | Email — subset of collected info + delighter | executor → dispatcher | Yes (after 5 approvals) |
| `follow_up_email_detailed` | Email — deeper info + data room link | executor + data_room_engine → dispatcher | Yes (after 5) |
| `valuation_teaser` | Email — market multiples for their vertical + "what's your company worth" calculator link | executor → dispatcher | No (high stakes) |
| `buyer_sample_report` | Email — 3-5 sample buyer profiles with approach narrative | researcher + executor → dispatcher | No (high stakes) |
| `meeting_prep_package` | Web page — custom meeting page with relevant data, checklist, talking points | meeting_engine | No |
| `post_meeting_follow_up` | Email — summary of what was discussed + next steps + delighter | executor → dispatcher | Yes (after 3) |
| `schedule_callback` | Calendar — create follow-up reminder + nurture entry | orchestrator | Yes (auto) |
| `nurture_6month` | Nurture — add to nurture_schedule with 6-month re-engagement | nurturer | Yes (auto) |
| `differentiation_play` | Email — why NC is different (all about them, data-driven, no upfront fees) | executor → dispatcher | No |
| `rapid_response` | Email — acknowledge inbound within 1 hour + meeting link | executor → dispatcher | Yes (after 3) |

---

## Auto-Execute Logic (graduated trust)

The Listener starts in FULL DRAFT mode. Every play is drafted and sent to human for approval. Over time, standard plays earn trust:

```
Play approval_count < threshold → ALWAYS DRAFT, notify human
Play approval_count >= threshold AND auto_execute_eligible → AUTO-EXECUTE with inspection

Auto-execute flow:
  1. Listener diagnoses situation, picks play, personalizes
  2. Executor agent generates deliverable (Claude CLI)
  3. Inspection agent (Claude CLI) reads the deliverable and certifies:
     - Facts are accurate (checked against dossier_provenance)
     - Tone matches entity rules
     - No PII leaks, no wrong names, no competitor mentions
     - DNC not violated
     - Output: "Reviewed by Claude Opus 4.6, 2026-03-29 17:34:22 UTC. CERTIFIED."
  4. Dispatcher sends
  5. Logged to sent_log with inspection_certified_at, inspection_model, inspection_verdict

If inspection FAILS → falls back to DRAFT mode, notifies human
If human REJECTS a previously auto-approved play → resets approval_count to 0, play goes back to full draft
```

---

## What the Listener Calls (not what it does itself)

| Need | Agent Called | Why Not Do It Itself |
|------|------------|---------------------|
| Classify a new contact | classifier | Classification has a decision tree and quality gates |
| Research a company | researcher | Dual-LLM verification, source trail, cost tracking |
| Generate email/letter/script | executor | Entity-specific tone, template rules, Claude CLI quality |
| Format data room | data_room_engine | Specialized web page generation |
| Send deliverable | dispatcher | Salesfinity/Lob/email API integration |
| Schedule nurture | nurturer | Cooling period management |
| Prep meeting | meeting_engine | Per-meeting web page generation |
| Check DNC | SQL: check_dnc() | Universal, must be atomic |
| Check if already handled | SQL: is_step_done() | Prevent duplicate work |
| Log the play execution | SQL: log_step() | Audit trail |

---

## New Tables Needed

```sql
situation_library   -- diagnosed states, signal patterns, recommended plays
play_templates      -- structured response recipes with escalating auto-trust
play_executions     -- every time a play was run: situation, play, target, result
listener_scan_log   -- what was scanned, when, what signals found
```

---

## The Listener's Personality

The Listener is the VP of Sales who:
- Never misses a signal in any channel
- Instantly knows what play to run
- Personalizes everything with real data about the prospect
- Never sends without permission (until it earns trust on that specific play)
- Creates new playbooks when it encounters situations it hasn't seen before
- Gets smarter every time a human approves, edits, or rejects its work
- Documents everything — every scan, every diagnosis, every play, every outcome

It is NOT:
- A generic email sender
- A template filler
- A notification bot
- An autonomous sender (until graduated trust is earned per-play)
