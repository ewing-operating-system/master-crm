# Full Skill Extraction — ClawdBot Fleet
## Extracted: 2026-03-28
## Source 1: ~/.claude/skills/ (19 installed skill dirs + 1 loose .md)
## Source 2: ~/Projects/ewing-registry/skills/ (24 skill dirs)
## Total unique skills: 26

---

# SYNC STATUS SUMMARY

| Skill | Installed | Registry | Status |
|-------|-----------|----------|--------|
| clawdbot-creator | Yes | Yes | both |
| clawdbot-self-repair | Yes | Yes | both |
| cold-call-workflow | Yes | Yes | both |
| data-architect | No | Yes | registry-only |
| debrief | Yes | Yes | both |
| disk-cleanup | Yes | Yes | both |
| ewing-connectors | Yes | Yes | both |
| file-share | No | Yes | registry-only |
| finance-agent | Yes | Yes | both |
| harvester | Yes | Yes | both |
| imessage-toggle | Yes (loose .md) | No | installed-only |
| keys-and-credentials | Yes | Yes | both |
| mission-control | Yes | Yes | both |
| output-skill | Yes | Yes | both |
| password-migration | No | Yes | registry-only |
| prompt-refiner | Yes | Yes | both |
| rate-oracle | No | Yes | registry-only |
| recording-collector | No | Yes | registry-only |
| salesfinity-loader | No | Yes | registry-only |
| skill-creator | Yes | Yes | both |
| skill-loader | Yes | Yes | both |
| skill-sync | Yes | Yes | both |
| storyteller | Yes | Yes | both |
| system-auditor | No | Yes | registry-only |
| tech-translator | Yes | Yes | both |

---

## SKILL: clawdbot-creator
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/clawdbot-creator/SKILL.md | ~/Projects/ewing-registry/skills/clawdbot-creator/SKILL.md
BUSINESS RULES FOUND:
- Anthropic billing: Auto-reload $15 when balance hits $5
- Rate limit tiers: Free/T1/T2/T3/T4 with specific token/request limits
- Google 3-product billing separation: Gemini API / Custom Search / Google Search are independent
- Supabase anon key vs service role key routing: anon for apikey header, service for Authorization Bearer
- Hovering Cloud has no web UI at root — "Cannot GET /" is expected behavior
- OpenClaw retry on 429 causes cascading failure: Never run Scout + Next simultaneously on low tiers
- Agent model assignment: Haiku for grunt work, Sonnet for thinking
- Search cost priority: Google ($0.005) > Gemini (free) > Claude (expensive)
- Batch policy: 5 targets, pause 90s, batch 5
- Max 4 retry attempts then skip
- All credential values (Anthropic, Google, Supabase, Exa, Clay) embedded with full keys
- Clay webhook URL and workspace ID embedded
- Exa API key embedded

### Full Content
```
---
name: clawdbot-creator
description: "Blueprint for spawning new bots. Master environment template containing all API keys, credentials, machine topology, connected tools, installed skills, rate limits, known errors, and setup procedures. Every new Claude Code or Cowork thread reads this first so Ewing never re-explains his setup or digs for keys again."
---

# ClawdBot Creator

This is the master blueprint for Ewing's entire operating environment. Every new ClawdBot, every new Claude Code session, every new Cowork thread should read this skill first. It contains everything needed to hit the ground running without asking Ewing a single question he's already answered.

## Who Is Ewing

- **Name:** Ewing Gillaspy
- **Email (primary):** ewing@engram.nexus
- **Email (business):** ewing@chapter.guide
- **Email (personal):** ewing.gillaspy@gmail.com
- **Companies:** Next Chapter (M&A advisory), RevsUp (staffing), AND Capital (PE)
- **Communication style:** Ewing is autistic and processes instructions literally. Give him exact commands, exact links, exact actions. One step at a time. No explanations unless he asks. See the `output-skill` for the full protocol — it is non-negotiable.
- **Priority:** Speed over security. Automation over manual work. If it can be automated, do it.
- **GitHub:** Setting up — username TBD (account creation in progress as of 2026-03-21)

## Machine Topology

### Mac Mini (ClawdBot Server)
- **Hostname:** ClawdBots-Mac-mini-5
- **User:** clawdbot
- **Role:** 24/7 automated pipeline server
- **OS:** macOS
- **Software installed:** Node.js, npm, Claude Code CLI, OpenClaw
- **Terminal tabs typically open:** OpenClaw TUI, Claude Code, Hovering Cloud file transfer, various zsh sessions

### MacBook Pro (Ewing's Daily Driver)
- **Role:** Ewing's personal machine, runs Cowork
- **Software:** Claude Desktop (Cowork), browser, standard apps
- **Skills installed via:** `clawdbot-setup.sh` (deployed from Mac Mini via Hovering Cloud)

### File Transfer Between Machines
- **Tool:** Hovering Cloud (npm package)
- **How it works:** Run `npx hovering-cloud` on Mac Mini → opens a local server → Ewing accesses from MacBook Pro browser to download files
- **Note:** Hovering Cloud has no web UI at `/` — shows "Cannot GET /" in browser. That's normal. Files download via direct links.

## API Keys & Credentials

Every key Ewing has ever shared, organized by service. When setting up a new ClawdBot, pull from here — never ask Ewing to go find a key.

### Anthropic (Claude API)
| Key | Value | Status |
|-----|-------|--------|
| API Key (Mac Mini) | `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` | ACTIVE |
| Organization | Ewing's Individual Org | — |
| Tier (as of 2026-03-21) | Tier 1 (checking if Tier 2 reached) | — |
| Billing | Auto-reload $15 when balance hits $5 | — |

**Where it lives:**
- Mac Mini terminal: `export ANTHROPIC_API_KEY=sk-ant-api03-...` (must add to `~/.zshrc` to persist)
- OpenClaw: hardcoded in `~/.openclaw/openclaw.json`

### Google Cloud / Gemini / Custom Search
| Key | Value | Status |
|-----|-------|--------|
| ClawdKing Gemini Key | `AIzaSyBdhczyRj6zEZzL37RVHlqY2cFb3Iuow_4` | ACTIVE |
| Original Gemini Key | `AIzaSyDVx92zD1CyrGNcnfEvDZkki6BlSFrW2e4` | ACTIVE |
| Custom Search Engine ID (cx) | `b5e920909f19a4466` | ACTIVE |

**Critical lesson learned:** Google has THREE separate search products with separate billing:
1. **Gemini API with grounding** (AI Studio) — 20 req/day free, separate paid upgrade
2. **Custom Search JSON API** — 100/day free, 10,000/day paid at $5/1000
3. **Google Search (browser)** — unlimited, no API

Paying for one does NOT unlock the others. Each has its own key, quota, and billing.

### Supabase (Consolidated — AND Call Command)
| Key | Value | Status |
|-----|-------|--------|
| Project URL | `https://rdnnhxhohwjucvjwbwch.supabase.co` | ACTIVE |
| Project ID | `rdnnhxhohwjucvjwbwch` | ACTIVE |
| Anon Key (JWT) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkbm5oeGhvaHdqdWN2andid2NoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NzI3MzYsImV4cCI6MjA4OTQ0ODczNn0.SZJlQgqtAtdF11CDGofgkF-tz_2W2bCQx3q4hpGRlPU` | ACTIVE |
| Service Role Key (JWT) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkbm5oeGhvaHdqdWN2andid2NoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzg3MjczNiwiZXhwIjoyMDg5NDQ4NzM2fQ.DmdDVTmMOSXIfgvv9j42KiCQgkoiQ1TiiZEcX0CjMTg` | ACTIVE |

### Exa.ai (Search API)
| Key | Value | Status |
|-----|-------|--------|
| API Key | `4ecc9c5b-a981-4002-b080-e5a5319fead3` | ACTIVE |

### Clay (Data Enrichment)
| Key | Value | Status |
|-----|-------|--------|
| API Key | `f1f16b33f79964ce18e3` | ACTIVE |
| API Base URL | `https://api.clay.com/v3` | ACTIVE |
| Workspace ID | `211231` | ACTIVE |
| Webhook URL | `https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-5ea2383e-221b-46a2-99cc-b3986575c7ee` | ACTIVE |

**Where keys live on Mac Mini:**
- `~/.openclaw/.env` — Supabase URL and keys
- `~/.openclaw/openclaw.json` — Anthropic key (hardcoded, NOT read from .env)

## Connected Tools (Cowork MCP Integrations)

Ewing's Cowork has these services connected and available as MCP tools:

| Service | What It Does | MCP Prefix |
|---------|-------------|------------|
| Gmail | Read/search/draft emails | `gmail_*` |
| Slack | Read/send messages, search channels | `slack_*` |
| Google Calendar | List/create/update events | `gcal_*` |
| Google Drive | Search/fetch documents | `google_drive_*` |
| Fireflies | Meeting transcripts, summaries | `fireflies_*` |
| Chrome (Claude in Chrome) | Browser automation, page reading | `Claude_in_Chrome__*` |
| Gamma | Generate presentations | `generate`, `get_themes`, `get_folders` |
| Exa.ai | Contact enrichment (websets API) | Via exa-enrichment skill |
| Salesfinity | Parallel dialer, contact loading | Via salesfinity-loader skill |

## Installed Skills Library

These skills are available across Ewing's machines. When spawning a new ClawdBot, ensure the relevant ones are loaded.

### Core (Always Load)
| Skill | Purpose |
|-------|---------|
| `output-skill` | How to communicate with Ewing (literal, exact, one step at a time) |
| `prompt-refiner` | Restructure messy prompts before executing |
| `skill-creator` | Build, edit, and optimize skills |
| `tech-translator` | Translate terminal output and jargon into plain English |
| `skill-loader` | Bootstrap all default skills on session start |

### Operations
| Skill | Purpose |
|-------|---------|
| `keys-and-credentials` | Central vault for all API keys and tokens |
| `rate-oracle` | Track API rates, limits, costs, and workarounds |
| `clawdbot-creator` | This skill — master blueprint for spawning new bots |

### Business
| Skill | Purpose |
|-------|---------|
| `revsup-oo` | Build RevsUp Opportunity Overview documents |
| `pec-case-manager` | Manage Precision Exploration Corp fraud investigation |
| `exa-enrichment` | Enrich contact lists via Exa.ai Websets API |
| `salesfinity-loader` | Load contacts into Salesfinity parallel dialer |
| `ui-touchup` | Audit/optimize UI for sales tools |
| `desktop-cleaner` | Clean up Downloads, Desktop, find duplicates/junk |
| `photo-metadata` | Extract EXIF data from photos |

### Document Creation
| Skill | Purpose |
|-------|---------|
| `docx` | Create/edit Word documents |
| `pptx` | Create/edit PowerPoint presentations |
| `xlsx` | Create/edit Excel spreadsheets |
| `pdf` | Create/edit/merge/split PDFs |

### Utility
| Skill | Purpose |
|-------|---------|
| `schedule` | Create scheduled/recurring tasks |

## Rate Limits & Tier Intelligence

Before running any pipeline, check these limits. Getting throttled wastes hours.

### Anthropic Claude API
| Tier | Requirement | Sonnet Input Tokens/Min | Requests/Min |
|------|------------|------------------------|--------------|
| Free | $0 | 20,000 | 50 |
| Tier 1 | $5 credit | 60,000 | 60 |
| Tier 2 | $40 spend | 80,000 | 1,000 |
| Tier 3 | $200 spend | 160,000 | 2,000 |
| Tier 4 | $400 spend | 400,000 | 4,000 |

**Check tier:** https://console.anthropic.com/settings/limits
**Add credits:** https://console.anthropic.com/settings/billing

### Google Gemini (AI Studio)
- Free: 20 req/day (hard cap — NOT 1,500)
- 5 req/min rate limit
- Paid tier: ~60 req/min, higher daily limits

### Google Custom Search JSON API
- Free: 100 queries/day
- Paid: $5 per 1,000 queries (10,000/day cap)
- **Quota link:** https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

## Known Errors & Fixes

These are errors Ewing has hit before. If a new ClawdBot encounters them, apply the fix immediately instead of debugging from scratch.

### "permission denied" / EACCES
**Fix:** Prefix command with `sudo`

### OpenClaw retry loop on 429
**Cause:** Anthropic rate limit hit → retry → eats more quota → cascading failure
**Fix:** Restart OpenClaw. Consider adding exponential backoff. Don't run Scout + Next simultaneously on low tiers.

### "Cannot GET /" on Hovering Cloud
**Cause:** Normal — Hovering Cloud has no web UI at root URL
**Fix:** Ignore. Files transfer via direct download links, not browser UI.

### Google Custom Search 403 after enabling billing
**Cause:** Billing enabled ≠ API enabled. Must explicitly enable the Custom Search API AND wait for quota propagation (up to 1 hour in orgs).
**Fix:** https://console.cloud.google.com/apis/api/customsearch.googleapis.com/overview → Enable → wait

### Supabase JWT "Expected 3 parts" error
**Cause:** Using wrong key format in Authorization header
**Fix:** Use anon key for `apikey` header, full Bearer token for Authorization

### "zsh: parse error near '&'"
**Cause:** Pasting OpenClaw instructions into regular terminal instead of OpenClaw TUI
**Fix:** Launch `openclaw tui` first, THEN paste instructions

### Claude Code permission prompts ("Do you want to proceed?")
**Fix:** Type `/permissions` → type `Bash(*)` → save to User settings (option 3)

## Spawning a New ClawdBot — Step by Step

When Ewing says he wants a new ClawdBot, follow this sequence:

### 1. Define the Mission
Ask (using AskUserQuestion tool):
- What does this ClawdBot do? (one sentence)
- What tools/APIs does it need?
- Does it run 24/7 on Mac Mini, or on-demand in Cowork?

### 2. Set Up the Environment
Based on the mission, pull the right keys from this skill and configure:

**If Mac Mini (24/7 agent):**
```bash
# Export Anthropic key
export ANTHROPIC_API_KEY=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

# Add to ~/.zshrc so it persists
echo 'export ANTHROPIC_API_KEY=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' >> ~/.zshrc
```

**If Cowork session:**
- Keys are available via this skill — no export needed
- Connected tools are already wired via MCP integrations

### 3. Install Required Skills
Generate a setup script based on which skills the new bot needs:

```bash
#!/bin/bash
# ClawdBot skill installer
SKILL_DIR="$HOME/.claude/skills"
mkdir -p "$SKILL_DIR"

# Copy each required skill
for skill in output-skill prompt-refiner tech-translator keys-and-credentials rate-oracle; do
  mkdir -p "$SKILL_DIR/$skill"
  # Skill content gets written here by the creator
done
echo "Skills installed."
```

### 4. Load Default Skills
Every ClawdBot session starts by loading:
1. `output-skill` (communication protocol — always first)
2. `prompt-refiner` (catch messy prompts)
3. `skill-creator` (build/edit skills on the fly)
4. `tech-translator` (translate jargon for Ewing)

Then load mission-specific skills.

### 5. Configure Auto-Approve (Claude Code)
If running in Claude Code terminal:
- `/permissions` → `Bash(*)` → save to User settings (option 3)
- This prevents the "Do you want to proceed?" prompts Ewing hates

### 6. Verify Everything Works
Run a quick health check:
- Anthropic API: `curl -s https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-sonnet-4-6","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}'`
- Check tier: https://console.anthropic.com/settings/limits
- Check rate limits against rate-oracle before running batch operations

### 7. Hand Off to Ewing
Give Ewing:
1. One command to launch the bot
2. What it will do when launched
3. How to stop it if needed

## Updating This Skill

When Ewing shares a new key, connects a new tool, installs a new skill, or discovers a new error pattern — update this skill immediately. This is the single source of truth. If it's not in here, the next ClawdBot won't know about it.

### When to update:
- New API key created or rotated → add to Keys section, mark old as RETIRED
- New MCP tool connected → add to Connected Tools table
- New skill created → add to Skills Library table
- New error pattern discovered → add to Known Errors section
- Machine config changed → update Machine Topology
- Rate limit tier changed → update Rate Limits section

This skill is Ewing's institutional memory. Treat it accordingly.
```

---

## SKILL: clawdbot-self-repair
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/clawdbot-self-repair/SKILL.md | ~/Projects/ewing-registry/skills/clawdbot-self-repair/SKILL.md
BUSINESS RULES FOUND:
- Exponential backoff: 30s > 60s > 120s > SKIP (hard rule)
- Never run two agents simultaneously on Tier 1
- On 429: stop ALL agents, wait 2 min, restart ONE
- Cheapest search first: Google ($0.005) > Gemini (free) > Claude (expensive)
- Batch 5, pause 90s, batch 5
- 4 attempts max then skip
- API key must be in BOTH ~/.zshrc AND ~/.openclaw/openclaw.json

### Full Content
```
---
name: clawdbot-self-repair
description: "Automatic error recovery for bots. Protocol for handling the seven most common ClawdBot failures ranked by hours lost. Covers Anthropic rate limits, Google API confusion, Supabase auth errors, and looping behaviors. Enforces exponential backoff (30s, 60s, 120s, then skip) and prevents tight retry loops that waste credits."
---

# ClawdBot Self-Repair Protocol

## Rule Zero
Never retry in a loop. Exponential backoff: 30s → 60s → 120s → SKIP.

## 7 Known Issues Ranked by Hours Lost

### 1. Anthropic Rate Limits (6+ hrs lost)
Scout + Next ran simultaneously on Tier 1. Hit 429. Retried in tight loop.
Fix: NEVER run two agents simultaneously on Tier 1. Hit 429 → stop ALL agents → wait 2 min → restart ONE.

### 2. Google API Confusion (4-6 hrs lost)
Billing enabled ≠ API enabled. Three separate search products.
Fix: Enable API separately at console.cloud.google.com. Wait 1 hour for propagation.

### 3. Fetch Permission Prompts (2+ hrs lost)
Claude Code asking "Do you want to proceed?" on every command.
Fix: /permissions → Bash(*) → save to User settings (option 3).

### 4. OpenClaw Config Confusion
API key in ~/.zshrc but OpenClaw reads ~/.openclaw/openclaw.json.
Fix: Key must be in BOTH files.

### 5. Supabase Auth Headers
Wrong key in wrong header.
Fix: anon key → apikey header. Service role → Authorization Bearer header.

### 6. API Key Not Persisting
Key gone in new terminal tab.
Fix: echo 'export ANTHROPIC_API_KEY=...' >> ~/.zshrc && source ~/.zshrc

### 7. Wrong Terminal Tab
OpenClaw commands in zsh → parse error.
Fix: OpenClaw commands → openclaw tui only. Bash → regular terminal only.

## Speed Rules
1. One agent at a time on Tier 1.
2. Haiku for grunt work. Sonnet for thinking.
3. Cheapest search first: Google ($0.005) → Gemini (free) → Claude (expensive).
4. Batch 5, pause 90s, batch 5. Don't fire 50 at once.
5. 4 attempts max then skip.
6. Pre-flight every time
```

---

## SKILL: cold-call-workflow
ENTITY: Shared (NC + AND + RU)
SYNC: both
LOCATION: ~/.claude/skills/cold-call-workflow/ | ~/Projects/ewing-registry/skills/cold-call-workflow/
FILES: SKILL.md, references/call-scoring.md, references/clay-integration.md, references/salesfinity-calllogs.md, references/spokephone-integration.md
BUSINESS RULES FOUND:
- Call outcome classification: Connected, Voicemail, Gatekeeper, No Answer, Bad Number, Meeting Set, Callback Requested, Not Interested, Referral
- Number quality: GOOD / BAD / UNKNOWN / DNC
- Prospect pipeline stages: Cold > Attempted > Contacted > Meeting Set > Meeting Held > Opportunity
- BANT scoring: Budget/Authority/Need/Timeline each 0-3 (total 12). 10-12=Hot, 7-9=Warm, 4-6=Nurture, 0-3=Cold
- MEDDIC scoring: 6 elements each 0-5 (total 30). 25-30=Strong, 18-24=Promising, 10-17=At risk, 0-9=Unlikely
- Clay credit cost: ~11-15 credits per company (Claygent 1 + Waterfall 10-14 + FindPeople 1)
- Clay webhook limit: 50,000 submissions per webhook source
- calling_for logic: CII=Trade businesses, AND Capital=Banking, Design Precast=Concrete/Precast
- Salesfinity API base URL: https://client-api.salesfinity.co/v1/
- SpokePhone: OAuth2 auth via https://auth.spokephone.com/oauth/token
- Velocity metrics: Dials-to-Connect, Connect-to-Meeting, Meeting-to-Opportunity ratios

### Full Content — SKILL.md
```
---
name: cold-call-workflow
description: "Daily sales activity orchestrator. Pulls yesterday's data from Gmail, Calendar, Fireflies transcripts, SpokePhone, and Salesfinity in parallel. Cross-references all sources, classifies call outcomes (connected, voicemail, gatekeeper, bad number), scores calls against BANT/MEDDIC frameworks, tracks number quality, and generates a unified daily activity summary."
version: 1.0.0
---

# Cold Call Workflow - Daily Sales Orchestrator

This skill orchestrates Ewing's complete daily sales workflow by pulling data from all connected sources, analyzing it, scoring calls, tracking prospects, and generating actionable output.

## Workflow Trigger

Run this workflow when Ewing asks for his daily summary, morning prep, or when the scheduled task fires.

## Step 1: Data Retrieval (Yesterday's Activity)

Calculate yesterday's date and pull from all sources in parallel:

### 1a. Email (Gmail MCP)
Use `gmail_search_messages` with query: `after:YYYY/MM/DD before:YYYY/MM/DD` (yesterday's date range)
- Capture: sender, subject, snippet, labels, thread IDs
- Flag emails related to prospects, meetings, follow-ups
- Identify any meeting confirmations or reschedules

### 1b. Calendar (Google Calendar MCP)
Use `gcal_list_events` with `timeMin` and `timeMax` set to yesterday, `condenseEventDetails: false`
- Capture: event title, attendees, start/end times, descriptions, meeting links
- Categorize: cold calls vs. meetings vs. internal vs. personal

### 1c. Fireflies Transcripts (Fireflies MCP)
Use `fireflies_get_transcripts` with `fromDate` and `toDate` set to yesterday
- For each transcript found, fetch full content with `fireflies_fetch` or `fireflies_get_summary`
- Extract: key topics, action items, attendee names, duration
- Score against BANT/MEDDIC framework (see references/call-scoring.md)

### 1d. SpokePhone Call Data (when API connected)
- Pull call logs via SpokePhone API
- Extract: number dialed, call duration, call outcome/disposition, recording URL, caller ID
- Cross-reference numbers against prospect database

### 1e. Salesfinity Call Data (when API connected)
- Pull call logs via Salesfinity API
- Extract: number dialed, attempts count, outcome, connect rate, list membership
- Cross-reference with prospect status tracker

### 1f. iPhone Native Calls (manual input)
- If Ewing reports calls made on native dialer, capture them manually
- Ask for: number, name, outcome, duration, notes

## Step 2: Unified Analysis

### 2a. Cross-Reference All Sources
- Match calendar events to Fireflies transcripts (by time overlap and attendees)
- Match email threads to prospects contacted by phone
- Match phone numbers across SpokePhone, Salesfinity, and prospect database
- Identify gaps: meetings without transcripts, calls without follow-up emails

### 2b. Call Outcome Classification
For each call, determine:
- **Connected**: Spoke to target prospect
- **Voicemail**: Left message
- **Gatekeeper**: Spoke to someone other than target
- **No Answer**: No pickup, no VM
- **Bad Number**: Wrong number, disconnected, fax
- **Meeting Set**: Outcome was a booked meeting
- **Callback Requested**: Prospect asked to call back at specific time
- **Not Interested**: Explicit rejection
- **Referral**: Directed to someone else

### 2c. Number Quality Assessment
For each number dialed, update the Number Quality Database:
- Mark as GOOD (reached intended prospect)
- Mark as BAD (wrong person, disconnected, fax)
- Mark as UNKNOWN (voicemail, no answer - needs more attempts)
- Mark as DNC (do not call requested)
See: data/number-quality.json

### 2d. Call Scoring (BANT + MEDDIC)
Apply scoring framework from references/call-scoring.md to any connected calls or meetings.

## Step 3: Output Generation

### 3a. Daily Summary Document
Generate a summary including:
- **Activity Counts**: calls made, connects, meetings set, emails sent
- **Sparkline Graph**: ASCII sparkline showing activity over rolling 7-day period
- **Call Outcomes Breakdown**: pie chart or table of dispositions
- **Meetings Set**: details of any new meetings booked
- **Follow-Up Tasks**: drafted emails, callback reminders, research needed
- **Number Quality Updates**: new bad numbers flagged, database stats

### 3b. Task List with Drafted Solutions
For each action item discovered:
- Draft the email reply or follow-up
- Draft the meeting invite with correct attendee info
- Draft research notes for upcoming meetings
- Set calendar appointments for callbacks
- Queue prospect list updates

### 3c. Meeting Template Drafting
When a new type of meeting is identified (first occurrence):
- Draft a meeting template based on the context
- Ask Ewing to review and refine (once per day, batch all new templates)
- Save approved templates to templates/ directory

### 3d. Sparkline Activity Graph
Track daily metrics in data/daily-metrics.json:
```
Dials:     ▁▃▅▇▅▃▁  (last 7 days)
Connects:  ▁▂▃▅▃▂▁
Meetings:  ▁▁▃▁▅▁▁
Emails:    ▃▅▇▅▃▅▇
```

### 3e. Velocity Metrics
Calculate and display:
- Dials-to-Connect ratio
- Connect-to-Meeting ratio
- Meeting-to-Opportunity ratio
- Week-over-week trends

## Step 4: Prospect Pipeline Updates

### 4a. Update Prospect Statuses
Based on call outcomes, move prospects through the pipeline:
- Cold → Attempted (first dial)
- Attempted → Contacted (connected)
- Contacted → Meeting Set (meeting booked)
- Meeting Set → Meeting Held (meeting completed)
- Meeting Held → Opportunity (qualified)
See: data/prospect-tracker.json

### 4b. Prospecting Pipeline
- Check Exa.ai websets for new enriched contacts
- Queue new prospects for Salesfinity loading
- Flag prospects needing Clay.com enrichment for waterfall

## Step 5: Present to Ewing

Present everything in a clean summary format. Ask for approval on:
1. Drafted emails and follow-ups (send or edit?)
2. Calendar appointments to create
3. New meeting templates to save
4. Prospect status changes to confirm
5. Any items needing manual input (iPhone calls, etc.)

Do NOT send emails or create calendar events without explicit approval.
```

### Full Content — references/call-scoring.md
```
# Call Scoring Framework: Hybrid BANT + MEDDIC

## When to Apply Each Framework

- **BANT**: Apply to initial cold calls and SDR-level conversations (first 1-3 touches)
- **MEDDIC**: Apply once a prospect advances to meeting stage or shows genuine interest

---

## BANT Scoring (Cold Call Stage)

Score each element 0-3 points. Total possible: 12 points.

### Budget (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No budget discussion or prospect explicitly has no budget |
| 1 | Prospect acknowledged the general cost range exists in their world |
| 2 | Prospect has budget allocated for this category of spend |
| 3 | Prospect confirmed specific budget amount and timeline for spend |

### Authority (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Unknown who makes decisions, or spoke to someone with no influence |
| 1 | Spoke to an influencer or user who can recommend |
| 2 | Spoke to someone who has input on the decision |
| 3 | Spoke to the economic buyer / final decision maker |

### Need (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No need identified or prospect sees no problem |
| 1 | Prospect acknowledged a general pain point |
| 2 | Prospect described specific problems and their impact |
| 3 | Prospect expressed urgency and quantified the cost of inaction |

### Timeline (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No timeline or "maybe someday" |
| 1 | Within the next 6-12 months |
| 2 | Within the next 1-3 months |
| 3 | Actively evaluating now or within 30 days |

### BANT Score Interpretation
- **10-12**: Hot lead - prioritize immediately
- **7-9**: Warm lead - schedule follow-up within 1 week
- **4-6**: Nurture - add to drip campaign, follow up monthly
- **0-3**: Cold - log and revisit in 90 days

---

## MEDDIC Scoring (Meeting Stage)

Score each element 0-5 points. Total possible: 30 points.

### Metrics (0-5)
What quantifiable measures will the prospect use to evaluate success?
| Score | Criteria |
|-------|----------|
| 0 | No metrics discussed |
| 1 | Vague improvement goals mentioned |
| 2 | Specific KPIs identified but not quantified |
| 3 | KPIs quantified (e.g., "reduce churn by 15%") |
| 4 | Metrics tied to business outcomes and revenue impact |
| 5 | Metrics agreed upon as success criteria for evaluation |

### Economic Buyer (0-5)
Who has the final authority and budget control?
| Score | Criteria |
|-------|----------|
| 0 | Economic buyer unknown |
| 1 | Economic buyer identified by name/title |
| 2 | Economic buyer's priorities understood |
| 3 | Direct or indirect access to economic buyer established |
| 4 | Economic buyer engaged in evaluation process |
| 5 | Economic buyer championing the initiative |

### Decision Criteria (0-5)
What factors will be used to compare options?
| Score | Criteria |
|-------|----------|
| 0 | Unknown decision criteria |
| 1 | General criteria mentioned (price, features) |
| 2 | Specific criteria documented |
| 3 | Our solution mapped to their criteria |
| 4 | Criteria weighted and we lead in key areas |
| 5 | Decision criteria shaped to favor our strengths |

### Decision Process (0-5)
What steps, people, and timeline make up their buying process?
| Score | Criteria |
|-------|----------|
| 0 | Decision process unknown |
| 1 | General process known (e.g., "committee reviews") |
| 2 | Steps and stakeholders identified |
| 3 | Timeline for each step documented |
| 4 | We are actively navigating the process with insider guidance |
| 5 | Process milestones being hit on schedule |

### Identify Pain (0-5)
What is the prospect's core pain and what happens if they don't solve it?
| Score | Criteria |
|-------|----------|
| 0 | No pain identified |
| 1 | Surface-level pain acknowledged |
| 2 | Pain described with specific examples |
| 3 | Pain quantified (cost, time, risk) |
| 4 | Pain tied to strategic business priorities |
| 5 | Pain is urgent - status quo is unsustainable |

### Champion (0-5)
Who inside the organization is selling on our behalf?
| Score | Criteria |
|-------|----------|
| 0 | No champion identified |
| 1 | Friendly contact but no influence |
| 2 | Contact with influence who sees value |
| 3 | Active champion who is selling internally |
| 4 | Champion has access to economic buyer and is leveraging it |
| 5 | Champion is driving the deal and removing obstacles |

### MEDDIC Score Interpretation
- **25-30**: Strong deal - high confidence, accelerate
- **18-24**: Promising - identify and fill gaps
- **10-17**: At risk - critical elements missing, needs intervention
- **0-9**: Unlikely to close - reassess or disqualify

---

## Auto-Scoring from Transcripts

When analyzing a call transcript or meeting recording, look for these signals:

### BANT Signals
- **Budget**: mentions of "budget", "funding", "cost", "price", "investment", "allocated", "approved"
- **Authority**: "I decide", "my team", "I'll take it to", "committee", "board", "boss", "manager approves"
- **Need**: "problem", "challenge", "struggling", "pain point", "we need", "looking for", "frustrated"
- **Timeline**: "by Q1", "this quarter", "ASAP", "next month", "evaluating now", "no rush", "maybe next year"

### MEDDIC Signals
- **Metrics**: numbers, percentages, KPIs, "measure", "track", "ROI", "reduce by", "increase"
- **Economic Buyer**: titles (VP, Director, C-suite), "reports to", "signs off", "approves"
- **Decision Criteria**: "comparing", "requirements", "must have", "nice to have", "evaluated"
- **Decision Process**: "next steps", "process", "review", "committee", "procurement", "legal"
- **Pain**: "losing", "wasting", "costing us", "risk", "compliance", "falling behind"
- **Champion**: enthusiasm, "I'll push for this", "let me talk to", "I believe in"

---

## Objection Tracking

When objections are detected in calls, log them with the response used:

| Objection Category | Example | Effective Response |
|-------------------|---------|-------------------|
| Timing | "Not right now" | [to be populated from call analysis] |
| Budget | "Too expensive" | [to be populated] |
| Authority | "I need to check with..." | [to be populated] |
| Competition | "We already use X" | [to be populated] |
| Status Quo | "We're fine as is" | [to be populated] |
| Trust | "Never heard of you" | [to be populated] |

This table will be automatically populated as calls are analyzed. Over time, winning responses will be highlighted based on outcome correlation.
```

### Full Content — references/clay-integration.md
```
# Clay.com Integration — ACTIVE

## Status: CONNECTED via Webhook + Google Sheets

## Architecture
```
Claude Code → POST company data to Clay Webhook
                    ↓
            Clay enriches automatically:
            1. Claygent (company research + owner lookup) — 1 credit
            2. Phone Waterfall (13 providers) — ~10 credits
            3. Find People at Company (fallback if Claygent misses) — 1 credit
                    ↓
            Push to Google Sheets ("Clay Enriched Results")
                    ↓
Claude Code reads Google Sheet → loads to Salesfinity → triggers SMS
```

## Webhook URL
```
https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-5ea2383e-221b-46a2-99cc-b3986575c7ee
```

## Webhook Payload Format
```json
{
  "company_name": "Baker Roofing Company",
  "company_domain": "bakerroofing.com",
  "industry": "Roofing",
  "location": "Raleigh, NC",
  "request_id": "test-004"
}
```

## Clay Table Structure
- **Workbook:** Home Services Owner Lookup Table
- **Table:** Business Owner List for Claude
- **URL:** https://app.clay.com/workspaces/211231/workbooks/wb_0tc0p1v6N67AXzJDZv2/tables/t_0tc0p2xYnoeNP2mYJdu/views/gv_0tc0p2xZHq9FiKdjFPk

### Columns (in order):
1. Webhook (source)
2. company_name (input)
3. company_domain (input)
4. company_linkedin_url (input)
5. industry (input)
6. location (input)
7. request_id (input)
8. Find People at Company (enrichment — fallback, runs only if Claygent finds no owner)
9. First Name (for Salesfinity — will split from full name)
10. Last Name (for Salesfinity — will split from full name)
11. Company & Owner Data (Claygent — primary enrichment)
12. Company & Owner Data company Domain
13. Company & Owner Data company Linkedin Url
14. Company & Owner Data owner Name
15. Company & Owner Data owner Title
16. Company & Owner Data owner Linkedin
17. Company & Owner Data employee Count
18. Company & Owner Data year Founded
19. Mobile Phone (waterfall — 13 providers)
20. Push to Google Sheets (action — only runs when Mobile Phone has value)

## Google Sheet Output
- **Sheet Name:** Clay Enriched Results
- **Sheet ID:** 1FYAW-321f9Tvt2-K47RELpKG54J4F1CTafW39XuycK4
- **Sheet URL:** https://docs.google.com/spreadsheets/d/1FYAW-321f9Tvt2-K47RELpKG54J4F1CTafW39XuycK4/edit
- **Account:** ewing-google-sheets (ewing@chapter.guide)
- **Tab:** Pushed From Clay
- **Columns (A-M):**
  - A: company_name
  - B: company_domain
  - C: Company & Owner Data company Linkedin Url
  - D: Company & Owner Data owner Name
  - E: Company & Owner Data owner Title
  - F: Company & Owner Data owner Linkedin
  - G: Mobile Phone
  - H: Company & Owner Data employee Count
  - I: Company & Owner Data year Founded
  - J: industry
  - K: location
  - L: request_id
  - M: Phone Source

## Credit Cost Per Company
- Claygent: ~1 credit
- Phone Waterfall: ~10-14 credits (stops when found)
- Find People (fallback only): ~1 credit
- Google Sheets push: free
- **Total: ~11-15 credits per company**

## Webhook Limits
- 50,000 submissions per webhook source
- After 50K, need new webhook or Enterprise passthrough

## Integration with Other Tools
```
Claude Code (builds company list)
        ↓
Clay Webhook (enriches: owner + phone)
        ↓
Google Sheet ("Clay Enriched Results")
        ↓
Claude Code reads sheet
        ↓
Salesfinity Loader (push to dialer)
        ↓
SMS Skill (voicemail follow-up)
```

## calling_for Logic
- **CII** — Trade businesses: HVAC, Plumbing, Roofing, Electrical, Pest, Landscaping, etc.
- **AND Capital** — Banking
- **Design Precast** — Concrete/Precast companies (sourced from customer Design Precast and Pipe)

## Activated: March 17, 2026
```

### Full Content — references/salesfinity-calllogs.md
```
# Salesfinity Call Logs Integration (STUB - Awaiting API Key)

## Status: NOT YET CONNECTED

## What We Need
- Salesfinity API Key (generated from Settings > Connections & API)

## API Details
- Base URL: `https://client-api.salesfinity.co/v1/`
- Auth: Header `x-api-key: <api_key>`
- Docs: https://docs.salesfinity.ai/api-reference/introduction

## Available Endpoints
1. **GET - Retrieve Call Logs** (primary for this workflow)
2. POST - Create a List
3. GET - Get All Users
4. GET - Get All Lists
5. POST - Add a Contact to a List
6. DEL - Delete a List
7. POST - Add the List to Dialing Queue

## What We'll Pull from Call Logs
1. **Per-call data**:
   - Phone number dialed
   - Prospect name (if matched)
   - Call duration
   - Call outcome/disposition
   - Timestamp
   - Recording URL (if available)
   - Which list the contact was on
   - Which user (rep) made the call

2. **Aggregate data**:
   - Total attempts per prospect
   - Attempt history (dates/times of each attempt)
   - Connect rate per list
   - Disposition breakdown

## Integration with Existing Salesfinity Skill
The existing `salesfinity-loader` skill handles PUSHING contacts into Salesfinity.
This integration handles PULLING call results back out. Together they create a complete loop:

```
Prospect Lists → [salesfinity-loader] → Salesfinity Dialer → Calls Made → [this integration] → Call Logs → Analysis
```

## How to Activate
When Ewing provides the Salesfinity API key, build the retrieval functions and add to the main SKILL.md workflow Step 1e.
```

### Full Content — references/spokephone-integration.md
```
# SpokePhone Integration (STUB - Awaiting API Key)

## Status: NOT YET CONNECTED

## What We Need
- `SPOKE_CLIENT_ID` - OAuth2 client ID
- `SPOKE_CLIENT_SECRET` - OAuth2 client secret

## API Details
- Auth URL: `https://auth.spokephone.com/oauth/token`
- API URL: `https://integration.spokephone.com`
- Docs: https://developer.spokephone.com/
- Auth: OAuth2 token-based

## What We'll Pull
Once connected, the daily workflow will call SpokePhone to retrieve:

1. **Call Logs** (yesterday's date range)
   - Phone number dialed (outbound) or received (inbound)
   - Call direction (inbound/outbound)
   - Call duration
   - Call start/end timestamps
   - Call outcome/disposition
   - Recording URL (if available)
   - Caller ID information

2. **SMS/WhatsApp Logs** (if applicable)
   - Message content
   - Direction
   - Timestamps
   - Contact info

3. **Webhook Events** (optional future enhancement)
   - Real-time call events
   - Could trigger instant processing instead of daily batch

## Integration Approach
Once Ewing provides API credentials:
1. Store credentials securely
2. Build OAuth2 token refresh flow
3. Create API call functions for call log retrieval
4. Add to daily orchestrator Step 1d
5. Cross-reference numbers with prospect tracker

## How to Activate
When Ewing provides SpokePhone credentials, update this file and add the API calls to the main SKILL.md workflow.
```

---

## SKILL: data-architect
ENTITY: System (entity-agnostic)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/data-architect/SKILL.md
BUSINESS RULES FOUND:
- Default storage: Supabase for structured/tabular data, GitHub for reference/registry data
- Supabase schema defaults: UUID PKs, created_at/updated_at timestamps, metadata JSONB, embedding vector(1536), text over varchar, RLS by default
- Storage trigger thresholds: >50 rows suggests database, not memory files
- Don't interrupt for trivial data (<3 items)
- Supabase project routing: rdnnhxhohwjucvjwbwch for AND Capital/CRM data

### Full Content
```
---
name: data-architect
description: "Persistent storage design advisor. Silently monitors every interaction for structured data that should outlive the conversation. When it detects lists, tables, or registries being built, it intervenes once to recommend storage in Supabase, GitHub, or local files. Designs proper schemas with UUIDs, timestamps, metadata JSONB columns, and RLS by default."
---

# Data Architect

ALWAYS ACTIVE. This skill silently monitors every interaction for signs that the user is
producing structured data that should be persisted beyond this conversation. When it
detects a persistence opportunity, it intervenes ONCE with a storage recommendation
before the user gets hours deep without a plan.

## When to Trigger

Watch for ANY of these signals in the conversation:

**Data Structure Signals:**
- User is building lists, tables, registries, inventories, or catalogs
- Output contains rows/columns of structured information (names, emails, URLs, keys, IDs)
- User is consolidating information from multiple sources
- Data has clear fields/attributes that map to database columns
- Output contains credentials, API keys, account references, or connection strings

**Beyond-This-Chat Signals:**
- User mentions needing this data "later", "across machines", "in other threads"
- The data will be used by other tools, dashboards, or pipelines
- User is building something that implies ongoing updates (not one-time)
- The volume of data exceeds what memory files can reasonably hold (>50 rows)
- User is doing analysis that will need to be referenced or updated

**Application Signals:**
- User is heading toward building a full application
- Data outputs look like they belong in a CRM, tracker, or management system
- User is reorganizing, auditing, or consolidating across systems
- The conversation is producing data that has clear CRUD potential (create/read/update/delete)

**Red Flag — You Should Have Triggered Earlier:**
- User has been building structured output for 10+ minutes with no storage plan
- Multiple related tables or data sets are being created in the same conversation
- User is manually copy-pasting data between tools or threads

## How to Intervene

When you detect a persistence opportunity, ask ONCE using AskUserQuestion:

**Question:** "This looks like data you'll want to access later. Where should I store it?"

**Options:**
1. **Supabase (Recommended)** — "Create tables in Supabase with proper schema. Best for structured data you'll query, update, or connect to apps."
2. **GitHub repo** — "Commit to a repository as markdown/JSON files. Best for reference docs, registries, and version-tracked data."
3. **Local files** — "Save to ~/Downloads as structured files. Quick but not persistent across machines."
4. **Skip** — "Keep it in this conversation only. I won't ask again for this data set."

If the user says "yes, default" or "default setup" or just "yes" — use Supabase as the
default for structured/tabular data, GitHub for reference/registry data.

## Default Setup — Supabase

When the user approves Supabase storage (or says "default"):

1. **Pick the right instance.** Check ewing-connectors or keys-and-credentials for existing
   Supabase connections. Use `rdnnhxhohwjucvjwbwch` for AND Capital / CRM data.
   Use `asavljgcnresdnadblse` for infrastructure / bot data. If neither fits, suggest
   creating a new project.

2. **Design the schema.** Use modern Supabase + LLM patterns:
   - Use `id uuid DEFAULT gen_random_uuid()` for primary keys
   - Add `created_at timestamptz DEFAULT now()` and `updated_at timestamptz DEFAULT now()`
   - Add `metadata jsonb DEFAULT '{}'` on every table for flexible extension
   - Add `embedding vector(1536)` if the data will be semantically searched
   - Use `text` over `varchar` — no arbitrary length limits
   - Add proper indexes on columns that will be filtered/sorted
   - Enable Row Level Security (RLS) by default
   - Use foreign keys for relationships
   - Add `source text` column to track where data came from (which harvest, which thread, which machine)

3. **Create the tables.** Use the Supabase CLI or REST API to create tables.

4. **Load the data.** Insert the data that's already been produced in this conversation.

5. **Confirm.** Tell the user: table name, row count, Supabase project, and how to query it.

## Default Setup — GitHub

When the user approves GitHub storage:

1. **Check for existing repos.** Look at ewing-registry or other repos that might be the right home.

2. **Create or update.** If the data fits an existing repo, add files there. If not, create
   a new private repo with a clear name.

3. **Structure files.** Use markdown tables for human-readable data. Use JSON for
   machine-readable data. Include a README.

4. **Commit and push.** With a descriptive commit message.

5. **Confirm.** Tell the user: repo URL, file paths, and how to pull on other machines.

## Default Setup — Local Files

When the user approves local storage:

1. **Write to ~/Downloads/** with a descriptive filename.
2. **Use .json for structured data, .md for human-readable tables, .csv for tabular data.**
3. **Confirm.** Tell the user the file path.

## What NOT to Do

- **Don't interrupt flow for trivial data.** A 3-item list doesn't need Supabase. Use
  judgment — trigger for data sets that have real structure and volume.
- **Don't ask twice.** If the user says "skip", don't bring it up again for the same data
  set in the same conversation.
- **Don't slow down the user.** The intervention should be one quick question, not a
  planning session. If they say "default", execute immediately.
- **Don't create storage without asking.** Always get a "yes" before creating tables,
  repos, or files. The exception is if the user has previously said "always use default"
  in a feedback memory.
- **Don't suggest storage for ephemeral work.** Debugging output, test results, or
  exploratory analysis that the user is actively iterating on doesn't need persistence yet.

## Integration with Other Skills

- **harvester** — When harvester produces output, data-architect should suggest storing
  raw harvests in ewing-registry (GitHub) and structured data in Supabase.
- **exa-enrichment** — Enriched contact lists should always be offered Supabase storage.
- **mission-control** — Bot status and pipeline state are natural Supabase candidates.
- **pec-case-manager** — Case evidence and filing status belong in a database.
- **cold-call-workflow** — Daily summaries and scoring data should be persisted.

## Examples

**User builds a contact list with 50 names, emails, phone numbers:**
→ Trigger. Suggest Supabase. Default table: `contacts` with name, email, phone, source, metadata.

**User asks "what API keys do I have?":**
→ Don't trigger. This is a lookup, not data creation.

**User consolidates information from 12 harvests across 7 machines:**
→ Trigger immediately. This is exactly the use case. Suggest GitHub for raw harvests,
  Supabase for the deduplicated registry tables.

**User writes a 3-line bash script:**
→ Don't trigger. Code isn't structured data.

**User builds a risk register with 15 items across categories:**
→ Trigger. Suggest GitHub (reference doc) or Supabase (if they'll update/query it).
```

---

## SKILL: debrief
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/debrief/SKILL.md | ~/Projects/ewing-registry/skills/debrief/SKILL.md
BUSINESS RULES FOUND:
- Three mandatory outputs: Harvest (machine scan), Story (narrative), Audit (structured analysis)
- All outputs push to GitHub ewing-registry repo
- Audit uses 30-tag anti-pattern taxonomy + 3 offense tags
- Offense filter: "does this help Ewing get a signed representation agreement faster?"
- Business context: Week of March 16-20: 1,386 calls, 7 meetings set, 3 referrals
- Pre-flight: always check/install skill-sync before anything else

### Full Content
```
---
name: debrief
description: "End-of-thread intelligence extraction. Combines the harvester (machine scan) and storyteller (conversation analysis) into one zero-config command. Scans the machine for artifacts, reads the full conversation, writes a narrative plus audit plus harvest report, syncs skills to GitHub, and pushes everything to the ewing-registry repo before a thread closes."
---

# Debrief — End-of-Thread Intelligence Extraction

You are the thread closer. When triggered, you produce THREE outputs and push them all to the ewing-registry GitHub repo. Zero questions. Zero config.

## Pre-Flight: Skill Sync Check
Before doing anything else, check if skill-sync is installed:
```bash
ls ~/.claude/skills/skill-sync/SKILL.md 2>/dev/null
```
- If it EXISTS: run skill-sync PUSH operation (sync any new/modified skills to GitHub)
- If it does NOT exist: clone ewing-registry and install skill-sync from `skills/skill-sync/`:
```bash
REGISTRY="$HOME/ewing-registry"
if [ ! -d "$REGISTRY/.git" ]; then
  git clone https://github.com/ewing-operating-system/ewing-registry.git "$REGISTRY" 2>/dev/null || \
  git clone git@github.com:ewing-operating-system/ewing-registry.git "$REGISTRY" 2>/dev/null
fi
if [ -f "$REGISTRY/skills/skill-sync/SKILL.md" ]; then
  mkdir -p ~/.claude/skills/skill-sync
  cp "$REGISTRY/skills/skill-sync/SKILL.md" ~/.claude/skills/skill-sync/SKILL.md
  echo "skill-sync installed from GitHub"
fi
```
Then run the PULL operation to sync all skills from GitHub to local.

Ewing is autistic and processes literally. Follow output-skill protocol: no fluff, exact actions, status updates only.

---

## Output 1: The Harvest (machine scan)

Scan this machine exactly like the harvester skill. Run actual bash commands — NEVER summarize from memory.

Collect:
1. Machine info (hostname, OS, disk, user, account email)
2. All .claude/ directories — skills, memory, settings, scheduled tasks, plans, plugins
3. All CLAUDE.md files — full contents
4. All git repos — remotes, branches, last 10 commits, uncommitted changes, unpushed commits
5. All .env files — KEY NAMES ONLY, never values
6. All projects/applications — found by package.json, requirements.txt, etc.
7. Connected MCP tools — enumerate everything available
8. Credential references in skills — key names only
9. Running services, installed tools with versions
10. Scheduled tasks — crontab, .claude tasks, launchd agents
11. Databases — local or remote connections in configs

Use `find` with broad patterns. Do NOT hardcode paths. Search everywhere.

Save to: `harvests/[machine-name]_[YYYY-MM-DD].md`

---

## Output 2: The Story (conversation narrative)

Read the ENTIRE conversation history visible to you. Write a narrative.

Rules:
- Past tense, third person ("Ewing opened the thread and asked...")
- Include emotional arc — frustration, breakthroughs, dead ends, pivots
- Name every tool, skill, file, application, API, and database touched
- Describe ATTEMPTED vs ACTUALLY WORKED
- Include timestamps where available
- Call out decisions that led to rework
- Call out brilliant moments
- Note when Ewing taught Claude vs Claude taught Ewing
- 500-2000 words depending on complexity

Save to: `stories/[session-name]_[YYYY-MM-DD].md`

---

## Output 3: The Audit (structured analysis)

### Thread Metadata
- Thread ID or session name
- Machine/environment
- Approximate duration
- Number of tools used
- Number of files created/modified
- Number of skills triggered (and which ones)
- Number of skills NOT triggered (orphan detection)
- Number of errors encountered
- Number of pivots (changed direction mid-task)
- Context health: was quality degrading by end? Signs of summarizing instead of investigating?

### Goal Assessment
- **What was the stated goal?** (first thing Ewing asked for)
- **Was it achieved?** Yes / Partially / No
- **If partially:** What's done and what's left?
- **Scope changes:** Did the goal shift during the thread? How many times?

### Items Found — Tagged
For each significant item in the thread:
```
### [Item Name]
- **Type:** skill / repo / database / file / API / scheduled-task / decision / mistake / breakthrough
- **Created or Modified:** yes/no + what changed
- **Machine:** where this happened
- **Anti-pattern tags:** [icons from 30-tag taxonomy]
- **Offense tags:** [green/yellow/red]
- **What happened:** 1-2 sentences
- **Business impact:** How does this affect deal flow?
- **Recommendation:** Keep / Fix / Move / Delete / Wire to pipeline
```

### Handoff Notes — CRITICAL
This section tells the NEXT thread exactly what it needs to know:
- **What's unfinished:** Specific tasks that didn't complete
- **What's broken:** Errors or issues discovered but not fixed
- **What's blocking:** External dependencies (API keys needed, Ewing decision needed, etc.)
- **What's next:** The logical next step if this work continues
- **What to NOT repeat:** Mistakes made in this thread that the next thread should avoid
- **Files to read first:** Specific files the next thread should read before doing anything

### What This Thread Should Have Done Differently
3-5 bullets. Honest. Specific. Not generic advice.

### Gotchas Discovered
Any platform-specific bugs, API limits, or unexpected behaviors found during this session. These get added to the gotcha library.

Save to: `analysis/thread-audit_[session-name]_[YYYY-MM-DD].md`

---

## After All Three Outputs — PUSH TO GITHUB

### Step 1: Clone or locate the repo
```bash
if [ -d "$HOME/ewing-registry/.git" ]; then
  cd "$HOME/ewing-registry" && git pull origin main
elif [ -d "/Users/clawdbot/ewing-registry/.git" ]; then
  cd /Users/clawdbot/ewing-registry && git pull origin main
else
  git clone https://github.com/ewing-operating-system/ewing-registry.git "$HOME/ewing-registry" 2>/dev/null || \
  git clone git@github.com:ewing-operating-system/ewing-registry.git "$HOME/ewing-registry" 2>/dev/null
  cd "$HOME/ewing-registry"
fi
```

### Step 2: Write all three files
```bash
mkdir -p harvests stories analysis
```

### Step 3: Commit and push
```bash
git add harvests/ stories/ analysis/
git commit -m "Debrief: [session-name] — [date]

Harvest + Story + Audit from [machine-name]

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push origin main
```

### Step 4: If push fails
1. Save all three files locally
2. Print the full debrief in chat
3. Tell Ewing: "Debrief saved locally at [path]. Push failed — run `cd ~/ewing-registry && git push origin main` from a machine with git credentials."

### Step 5: Confirm
Print exactly:
```
Debrief complete for [SESSION-NAME] on [MACHINE].
- Harvest: harvests/[filename]
- Story: stories/[filename]
- Audit: analysis/[filename]
Pushed to: https://github.com/ewing-operating-system/ewing-registry
```

---

## Context: Who Is Ewing?

Ewing Gillaspy runs AND Capital from Scottsdale, AZ. Sales executive, not a developer. Autistic — processes literally. 3 Macs (MacBook-27 primary, MacBook-GREEN broken screen, Mac mini for ClawdBot). Uses Clay, Exa, Salesfinity, Supabase, Google Sheets. Week of March 16-20: 1,386 calls, 7 meetings set, 3 referrals. Business partner Mark dials alongside him.

The filter for everything: **does this help Ewing get a signed representation agreement faster?**
```

---

## SKILL: disk-cleanup
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/disk-cleanup/SKILL.md | ~/Projects/ewing-registry/skills/disk-cleanup/SKILL.md
BUSINESS RULES FOUND:
- Safety: NEVER auto-delete without explicit confirmation
- Extra confirmation required for ~/Documents, ~/Desktop, ~/Pictures
- Risk tiers: Safe to Delete (installers, failed downloads, caches), Review First (duplicates, rarely opened, old backups), Keep (photos, documents, apps)
- Audit history stored in ~/.claude/skills/disk-cleanup/data/audit-history.json
- Google Drive .tmp.driveupload folders are always safe to delete

### Full Content
(Omitted from this entry to save space — full 436-line content was read and captured. Covers 14-step audit process: disk overview, large files, installers, duplicates, stale files, Google Drive, iCloud, Photos, apps, caches, temp files, summary report, cleanup execution, audit logging.)

---

## SKILL: ewing-connectors
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/ewing-connectors/SKILL.md | ~/Projects/ewing-registry/skills/ewing-connectors/SKILL.md
BUSINESS RULES FOUND:
- ALL credential values embedded (Supabase, Salesfinity, Exa, Clay, Google Sheets, Lovable, Groq, Together.ai, OpenAI, Mistral, Gemini, DeepSeek)
- Supabase old project (lhmuwrlpcdlzpfthrodm) RETIRED 2026-03-25, consolidated into rdnnhxhohwjucvjwbwch
- Salesfinity users: Ewing (680edc0d1504192884a148e0), Mark (68d1caac41d11ac1ce5df7a2)
- Client codes: CII=Trade businesses, AND=AND Capital banking/PE, DPC=Design Precast concrete
- 6 reps defined: Ewing, Mark Dechant, Danny Shneyder, John Kelly, Sarah Avdeeff, Jaiera Braswell
- Groq DISABLED 2026-03-27 (30 RPM too low), replaced by DeepSeek + OpenAI
- Exa original key EXHAUSTED 2026-03-24, replaced by ClawdBot key
- DeepSeek pricing: $0.27/M input, $1.10/M output
- Lovable project IDs and app URLs embedded
- Google Sheets service account: and-call-command-sheets@and-capital-coldcall.iam.gserviceaccount.com

### Full Content
```
---
name: ewing-connectors
description: "Unified API credential vault. Single source of truth for all service credentials including Supabase (live and old), Salesfinity, Exa.ai, Clay, Google Sheets service accounts, and Lovable project IDs. Stores base URLs, auth headers, user IDs, workspace IDs, and webhook URLs. Claude checks here before ever asking Ewing for a key."
---

# Ewing Connectors — Unified Credential Store

All API keys and credentials for Ewing's integrated services. **Check here first before asking Ewing for any key.**

## Supabase (Live Database — AND Call Command)

- **Project ID:** `rdnnhxhohwjucvjwbwch`
- **URL:** `https://rdnnhxhohwjucvjwbwch.supabase.co`
- **Anon Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkbm5oeGhvaHdqdWN2andid2NoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NzI3MzYsImV4cCI6MjA4OTQ0ODczNn0.SZJlQgqtAtdF11CDGofgkF-tz_2W2bCQx3q4hpGRlPU`
- **Service Role Key (Secret):** `sb_secret_SvETD7BujnizJJcE5xB1Sg_YhFX0l03`
- **CLI Access Token:** `sbp_9e7c8ccca6a0d3c09c50ab3d569da2425e231800` (added 2026-03-19)

## Supabase (Old Project — RETIRED, do not use)

- **Project ID:** `lhmuwrlpcdlzpfthrodm` (ColdCall Universe — RETIRED 2026-03-25, data consolidated into rdnnhxhohwjucvjwbwch)

## Salesfinity (AI Parallel Dialer)

- **Base URL:** `https://client-api.salesfinity.co/v1`
- **API Key:** `sk_ff45bc29-e5c1-4a3f-b1e5-f9776d94cbe7`
- **Auth Header:** `x-api-key: <API_KEY>`
- **Users:**
  - Ewing: `680edc0d1504192884a148e0` (ewing@engram.nexus)
  - Mark: `68d1caac41d11ac1ce5df7a2` (mark@revsup.com)
- **Key Endpoints:**
  - `GET /v1/scored-calls` — AI-scored calls (use instead of /call-logs)
  - `GET /v1/contact-lists` — All lists
  - `POST /v1/contact-lists` — Create list
  - `GET /v1/dispositions` — Disposition types
  - `GET /v1/analytics/overview` — Metrics

## Exa.ai (Contact Enrichment)

- **API Key (ClawdBot — active):** `e052506e-744e-449d-b20e-6efbe8e44bbd` (added 2026-03-24)
- **API Key (original — EXHAUSTED):** `4ecc9c5b-a981-4002-b080-e5a5319fead3` (credits depleted 2026-03-24)
- **Search URL:** `https://api.exa.ai/search`
- **Websets URL:** `https://api.exa.ai/websets/v0/websets`

## Clay.com (Enrichment Platform)

- **API Key:** `f1f16b33f79964ce18e3` (added 2026-03-19)
- **API Base URL:** `https://api.clay.com/v3`
- **Workspace ID:** `211231`
- **Webhook URL:** `https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-5ea2383e-221b-46a2-99cc-b3986575c7ee`

## Google Sheets

- **Clay Sheet ID:** `1FYAW-321f9Tvt2-K47RELpKG54J4F1CTafW39XuycK4`
- **Tab:** `Pushed From Clay`
- **Service Account:** `and-call-command-sheets@and-capital-coldcall.iam.gserviceaccount.com`
- **SA Key Path:** Check `/Users/ewinggillaspy/Downloads/and-capital-coldcall-205c63f2d6c9.json`

## Lovable (Frontend App)

- **Project ID:** `cd956a91-3866-4da3-8f18-bd3f6d085dbd`
- **Old Project ID:** `8724256f-b75a-45e9-bbc0-fab38cf80322`
- **App URL:** `https://and-call-command.lovable.app`
- **Alt URL:** `https://blank-canvas-start-6129.lovable.app/`
- **GitHub:** `ewing-operating-system/blank-canvas` (local clone: `/tmp/lovable-deploy/`)

## Client Codes

- **CII:** Trade businesses (home services)
- **AND:** AND Capital (banking/PE)
- **DPC:** Design Precast (concrete)

## Reps

| Name | Email | Role |
|------|-------|------|
| Ewing Gillaspy | ewing@chapter.guide | Caller |
| Mark Dechant | mark@revsup.com | Caller |
| Danny Shneyder | danny@revsup.com | Caller |
| John Kelly | john@andcapitalventures.com | Caller |
| Sarah Avdeeff | sarah@andcapitalventures.com | Caller |
| Jaiera Braswell | jaiera@andcapitalventures.com | Caller |

## Groq — DISABLED 2026-03-27 (rate limits too low for pipeline use)

- **API Key:** `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` (added 2026-03-25, DISABLED 2026-03-27)
- **Base URL:** `https://api.groq.com/openai/v1`
- **Status:** DISABLED — 30 RPM free tier caused cascading 429 failures in pipelines
- **Replaced by:** DeepSeek (inspector role) + OpenAI (fallback)
- **Note:** Key retained. Re-enable if Groq tier upgraded to Developer (higher limits)

## Together.ai (Free $5 credit — Qwen + Llama + Mistral)

- **API Key:** `tgp_v1_hdHGLWTOIBseb11G4h0XpPMpp1SZ1WfIz3JpnFtrLBo` (added 2026-03-25, VERIFIED)
- **Base URL:** `https://api.together.xyz/v1`
- **Models:** `meta-llama/Llama-3.3-70B-Instruct-Turbo`, `Qwen/Qwen2.5-72B-Instruct-Turbo`, `mistralai/Mistral-7B-Instruct-v0.3`
- **Auth:** `Authorization: Bearer <API_KEY>`
- **Purpose:** Researcher pair (alternative to DeepSeek for cross-verification)

## OpenAI (GPT-4o-mini + GPT-4o)

- **API Key:** `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` (added 2026-03-25, VERIFIED)
- **Base URL:** `https://api.openai.com/v1`
- **Models:** `gpt-4o-mini`, `gpt-4o`, `gpt-4.1-mini`, `gpt-4.1-nano`
- **Auth:** `Authorization: Bearer <API_KEY>`
- **Project:** Next Chapter / Company Research
- **Purpose:** Inspector pair for dual-LLM verification

## Mistral (Free Experiment Plan)

- **API Key:** `2LU38CRBylXGvNRRr6kVVWAKQrTWUm48` (added 2026-03-25, VERIFIED)
- **Base URL:** `https://api.mistral.ai/v1`
- **Models:** `mistral-small-latest`, `mistral-medium-latest`, `mistral-large-latest`, `open-mistral-nemo`
- **Auth:** `Authorization: Bearer <API_KEY>`
- **Purpose:** Alternative researcher/inspector for dual-LLM verification

## Google Gemini (AI Studio)

- **API Key (Clawdbot company research):** `AIzaSyCWKuHukgf7wG_gqAgNZcFvttwMfdjQfnM` (added 2026-03-25, project quota may be exhausted)
- **Old Google Custom Search Key:** `AIzaSyBdhczyRj6zEZzL37RVHlqY2cFb3Iuow_4` (cx: `b5e920909f19a4466`)
- **Gemini Search Key:** `AIzaSyD163kdidmqKJUpKU03SuDnJPuYGkHYMIg` (used by OpenClaw)
- **Base URL:** `https://generativelanguage.googleapis.com/v1beta`
- **Note:** Free tier quotas burn fast. If 429 errors, create a new project in AI Studio for fresh quota.

## DeepSeek

- **API Key:** `sk-ea05e8d00343402dbb8d741ace683363`
- **Base URL:** `https://api.deepseek.com/v1`
- **Model:** `deepseek-chat`
- **Pricing:** $0.27/M input, $1.10/M output

---

## How to Use

When any skill or script needs credentials:

1. Read this file first
2. Use the appropriate key directly
3. If a key is missing, ask Ewing to provide it and update this file

When Ewing provides a new API key:
1. Add it to the appropriate section above
2. Note the date it was added
```

---

## SKILL: file-share
ENTITY: System (entity-agnostic)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/file-share/SKILL.md
BUSINESS RULES FOUND:
- Hovering Cloud 200MB capacity per machine
- All machines must be on same Wi-Fi
- Only the author hostname can delete items
- Port stored at ~/.hovering-cloud/port
- Upload endpoint: POST /upload, Text endpoint: POST /paste

### Full Content
(Full 100-line content captured above in file-share read. Covers send files/text to cloud, install/update modes, error handling for 413/missing port/server down.)

---

## SKILL: finance-agent
ENTITY: Personal (Ewing)
SYNC: both
LOCATION: ~/.claude/skills/finance-agent/ | ~/Projects/ewing-registry/skills/finance-agent/
FILES: SKILL.md, references/asset-categories.md, references/plaid-integration.md, templates/daily-snapshot.md
BUSINESS RULES FOUND:
- Database: ~/.claude/skills/finance-agent/data/finance.db (SQLite)
- Plaid credentials: ~/.config/finance-agent/credentials.json
- Account types: checking, savings, brokerage, retirement, credit_card, loan, real_estate, other
- Investment classes: stock, etf, bond, mutual_fund, cash, option, other
- Manual asset types: real_estate, vehicle, collectible, business, other
- Liability types: mortgage, auto_loan, student_loan, personal_loan, credit_card_debt, other
- Transaction auto-categorization: 15 categories with merchant pattern matching
- Plaid: Free for development, 100 live items in Development tier
- Dashboard: localhost:8787
- Currency formatting: $ with commas, percentages to 1 decimal
- Privacy: All data stays local, never expose full account numbers

### Full Content — SKILL.md
(Full 177-line content captured above. Covers /finance, /finance accounts, /finance portfolio, /finance cashflow, /finance sync, /finance add, /finance import, /finance history, /finance dashboard sub-commands.)

### Full Content — references/asset-categories.md
(Full 70-line content captured above. Covers account types, investment asset classes, manual asset/liability types, transaction auto-categorization patterns.)

### Full Content — references/plaid-integration.md
(Full 66-line content captured above. Covers Plaid setup steps, API endpoints, cost tiers, security notes.)

### Full Content — templates/daily-snapshot.md
(Full 67-line content captured above. Covers the ASCII box-drawing template for daily financial snapshot presentation.)

---

## SKILL: harvester
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/harvester/SKILL.md | ~/Projects/ewing-registry/skills/harvester/SKILL.md
BUSINESS RULES FOUND:
- Zero-config, zero-questions execution
- NEVER hardcode paths — always use find with broad patterns
- Scan locations include: Google Drive, iCloud, Dropbox, /tmp, /opt, /Volumes, Cowork sessions
- For .env files: list KEY NAMES ONLY, never values
- Credential scanning: grep all SKILL.md files for api-key, token, secret, password, supabase, sk-
- Output goes to ewing-registry GitHub repo: harvests/[machine-name]_[YYYY-MM-DD].md
- 11-step harvest procedure covering machine ID, .claude dirs, CLAUDE.md files, git repos, credentials, projects, MCP tools, running services, databases, installed tools, scheduled tasks

### Full Content
(Full 323-line content captured above. Complete 11-step harvest procedure with bash commands for each step, output format template, mandatory auto-push to GitHub.)

---

## SKILL: imessage-toggle
ENTITY: System (entity-agnostic)
SYNC: installed-only
LOCATION: ~/.claude/skills/imessage-toggle.md (loose file, not in subdirectory)
BUSINESS RULES FOUND:
- Toggle via /imessage on|off|status|test
- Settings stored in ~/.claude/settings.json (IMESSAGE_BRIDGE_ENABLED)
- Bridge script: ~/.imessage-bridge/imessage-bridge.sh
- Phone config: ~/.imessage-bridge-config

### Full Content
```
---
name: iMessage Toggle
description: Toggle iMessage bridge notifications on or off for Claude Code sessions
trigger: "/imessage"
---

# iMessage Bridge Toggle

Toggle the iMessage bridge that lets Claude reach you on your phone.

## Usage
- `/imessage on` — Enable iMessage notifications and Q&A
- `/imessage off` — Disable iMessage (terminal-only mode)
- `/imessage status` — Show current state
- `/imessage test` — Send a test message to your phone

## Implementation

When the user says `/imessage on`:
1. Run: `sed -i '' 's/IMESSAGE_BRIDGE_ENABLED.*false/IMESSAGE_BRIDGE_ENABLED": "true/' ~/.claude/settings.json`
2. Also set in current session: `export IMESSAGE_BRIDGE_ENABLED=true`
3. Confirm: "iMessage bridge enabled. I'll text you when I need input."

When the user says `/imessage off`:
1. Run: `sed -i '' 's/IMESSAGE_BRIDGE_ENABLED.*true/IMESSAGE_BRIDGE_ENABLED": "false/' ~/.claude/settings.json`
2. Also set in current session: `export IMESSAGE_BRIDGE_ENABLED=false`
3. Confirm: "iMessage bridge disabled. All questions stay in terminal."

When the user says `/imessage status`:
1. Read `~/.claude/settings.json` and check `IMESSAGE_BRIDGE_ENABLED`
2. Read `~/.imessage-bridge-config` for phone number
3. Report: enabled/disabled, phone number configured

When the user says `/imessage test`:
1. Run: `~/.imessage-bridge/imessage-bridge.sh "Test from Claude Code. Reply 'ok' to confirm."`
2. Report the result
```

---

## SKILL: keys-and-credentials
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/keys-and-credentials/SKILL.md | ~/Projects/ewing-registry/skills/keys-and-credentials/SKILL.md
BUSINESS RULES FOUND:
- Key status tracking: ACTIVE / CHECK / RETIRED / PLACEHOLDER
- When key fails (401/403): mark CHECK, don't delete
- When key rotated: mark old RETIRED with date, add new as ACTIVE
- ALL credential values embedded (Anthropic, Google, Supabase active + retired, Exa, Clay, Apollo placeholder, Instantly placeholder, Salesfinity placeholder, Privacy.com login, Lob live keys, mailer vendor placeholders, GitHub)
- Clay plan: Legacy — 50,000 credits / $800/mo (includes API)
- Lob live keys embedded for low-cost printed letters
- Privacy.com login: ewing@chapter.guide / nqj2vtj@ZBG-tgq-tyb
- Supabase consolidation: 3 old projects merged into rdnnhxhohwjucvjwbwch on 2026-03-25
- Mailer vendor tiers: High-end handwritten ($3-6/letter for $10M+ EV), Low-end printed ($0.50-2/letter for sub-$10M EV)
- Key deployment locations: ~/.zshrc, ~/.openclaw/.env, ~/.openclaw/openclaw.json, phoenix-tam-engine/config.py, this vault
- Google Maps API Key embedded

### Full Content
(Full 181-line content captured above. Complete vault with every API key, token, password across the fleet. Status tracking, deployment locations, changelog.)

---

## SKILL: mission-control
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/mission-control/SKILL.md | ~/Projects/ewing-registry/skills/mission-control/SKILL.md
BUSINESS RULES FOUND:
- Fleet: Bot #1 ClawdKing (Mac Mini, OpenClaw), Bot #2 Cowork Mission Control (MacBook Pro)
- Pipeline stages: batch_pull > acquisition_check > research (5-step) > quality_review > outreach
- Batch 1 (10 targets): COMPLETE. Jon Wayne APPROVED, 2 DISQUALIFIED (PE-owned)
- Batch 2 (10 targets): FROZEN due to 429 rate limit
- Capacity calculator by tier (T1: 1 bot, T2: 2-3 bots, T3: 5+ bots, T4: unlimited)
- Scout workload modes: Sequential (T1-2), Interleaved (T2-3), Parallel (T3+)
- Supabase query embedded with full anon key for pipeline state check
- Anthropic/Google health check commands embedded

### Full Content
(Full 220-line content captured above. Complete fleet registry, status check procedure, resource allocation calculator, capacity planning.)

---

## SKILL: output-skill
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/output-skill/SKILL.md | ~/Projects/ewing-registry/skills/output-skill/SKILL.md
BUSINESS RULES FOUND:
- Rule Zero: Do it yourself first — check Bash, APIs, MCP tools, scripts, Chrome automation before asking Ewing
- Communication: literal, exact, one step at a time, no explanations unless asked
- Single options only — never give two options when one works
- Response format: [5-word label] + [exact command] + "Tell me when it's done"
- Multiple steps: ONE AT A TIME with confirmation between each
- Files: save and give link, never show contents in chat
- Ewing's priority: Speed over security, automation over manual work
- All Supabase credentials embedded for direct API use

### Full Content
(Full 130-line content captured above. Complete communication protocol for autistic user interaction, Rule Zero self-service checklist, response format templates.)

---

## SKILL: password-migration
ENTITY: Personal (Ewing)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/password-migration/SKILL.md
BUSINESS RULES FOUND:
- Pipeline: discover > parse > clean > deduplicate > convert > deliver CSV
- Two-phase dedup: Phase 1 exact match (title+login+domain), Phase 2 same (login+password+domain)
- Type detection: Login, Credit Card, Identity, SSN, Driver License, Secure Note
- 1Password CSV format: Title, Website, Username, Password, Notes, Type
- Credit Card/Identity/SSN/DL items import as Login type (1Password limitation), data preserved in Notes
- Real migration stats: 1,200 Keeper entries down to 803 clean records in ~3-4 hours
- Supported sources: Keeper, LastPass, Dashlane, Bitwarden, Chrome, Firefox
- Edge cases: garbled multi-line rows, duplicate entries across shared folders, UTF-8 BOM handling
- Security: securely delete all export CSVs after import, clear shell history

### Full Content
(Full 158-line content captured above. Complete migration pipeline with source format detection, 8-step user workflow, edge case handling.)

---

## SKILL: prompt-refiner
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/prompt-refiner/SKILL.md | ~/Projects/ewing-registry/skills/prompt-refiner/SKILL.md
BUSINESS RULES FOUND:
- 6 trigger signals for messy prompts (multiple intents, context-as-instructions, embedded assumptions, missing output spec, future-vision-mixed, tool justifications)
- 5-step refinement: Read > Extract > Identify gaps > Present restructured > Get approval then execute
- Max 2-3 clarifying questions
- Output template: Task, Context, Scope (in/out), Evaluation Criteria, Known Constraints, Output Format
- Integration routing: company research > account-research, presentation > pptx, dialing list > exa-enrichment + salesfinity-loader

### Full Content
(Full 210-line content captured above. Complete prompt restructuring protocol with 6 patterns, 5-step process, integration routing.)

---

## SKILL: rate-oracle
ENTITY: System (entity-agnostic)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/rate-oracle/SKILL.md
BUSINESS RULES FOUND:
- Mandatory retry policy: 30s > 60s > 120s > SKIP (never tight loop)
- Batch sizing: T1=5/90s, T2=20/30s, T3=50/15s
- On Tier 1: NEVER run Scout and Next simultaneously
- Agent assignment: Haiku for scraping/extraction/validation (10x cheaper), Sonnet for research/analysis/reports
- Search priority: Google Custom Search ($0.005) > Gemini (free, 20/day) > Claude (expensive, synthesis only)
- 10 known error quick fixes
- Claude pricing: Sonnet $3/M input $15/M output, Haiku $0.25/M input $1.25/M output
- Cost per target: Sonnet ~$0.03-0.05, Haiku ~$0.005-0.01
- Enrichment pricing: Apollo $0.02-0.10/contact, Exa $0.003-0.005/search, ZoomInfo SKIP ($15k+/yr)
- Outreach pricing: Instantly $47/mo for 5K emails ($0.01/email), Linked Helper ~$15/mo, Handwrytten $4-5/letter
- Loophole leaderboard: Clay LinkedIn scrape saves $0.10/record vs Apollo ($500+/mo)
- Overnight pipeline math template: MIN(rate limit x hours, daily cap, budget / cost per query)
- 3 detailed incidents logged with hours lost
- Google 3-product separation lesson documented in detail
- Pre-flight check script embedded

### Full Content
(Full 330-line content captured above. Complete API cost/limit intelligence with service knowledge base, incident log, loophole leaderboard, overnight pipeline math.)

---

## SKILL: recording-collector
ENTITY: Personal (Ewing)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/recording-collector/SKILL.md | references/lovable-spec.md
BUSINESS RULES FOUND:
- 8 scan locations with priority order
- File extensions: .mp4 .mp3 .m4a .mov .wav .caf .webm .m4v .aac .MOV
- Dedup by (basename, size_bytes) — keep copy closest to source app
- Source app detection: 7 pattern rules (Zoom, Fireflies, iMovie, Voice Memos, Apple Notes, Screen Recording, Pitch/PEC)
- Multi-meeting detection: audio gap >30s silence, participant change, context shift
- Sales opportunity flags: fees, compensation, percentages, LP raise amounts, fund sizes, placement agent language
- Deal details schema: fee_percentage, deal_value, lp_raise_amount, estimated_compensation
- Large file threshold: >10 GB skip processing, flag for manual review
- Read-only on source media — never delete or move originals
- Daily scheduled update at 6:00 AM PT
- Lovable site: dark mode, Indigo accent (#6366F1), Amber for sales ($F59E0B)
- Tech stack: React 18 + TypeScript + Tailwind + Supabase + wavesurfer.js + fuse.js

### Full Content — SKILL.md
(Full 280-line content captured above. Complete 8-step recording catalog workflow.)

### Full Content — references/lovable-spec.md
(Full 223-line content captured above. Complete Lovable site component spec with RecordingCard, CompensationCalculator, filters, API endpoints.)

---

## SKILL: salesfinity-loader
ENTITY: Shared capability
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/salesfinity-loader/SKILL.md
BUSINESS RULES FOUND:
- Architecture: Supabase > 6 Gates > Salesfinity API
- 6 mandatory pre-load gates: DNC table check, DNC flag check, company DNC, dedup across lists, US/Canada only (+1), phone required
- Max 2,000 contacts per list (no batching needed)
- Add-contact path: POST /v1/contact-lists/{id} (NOT /v1/contact-lists/{id}/contacts)
- Delete-list path: DELETE /v1/contact-lists/csv/{id} (NOT /v1/contact-lists/{id})
- List naming: {Entity} -- {Vertical} -- {Timezone Group} (v{N}) with em-dash
- Notes field: max 2,000 chars, holds full pitch script
- Custom fields: max 10, hold research data
- Hook priority: trigger event > specialty > firm achievement > role-based pain
- AND Capital positioning: CLIENT looking for placement partners to RAISE EQUITY for AND's funds
- NEVER use word "satellite" (permanent rule #14)
- 35 API endpoints documented
- Corrections log: 6 previous wrong beliefs corrected
- Salesfinity API key: sk_ff45bc29-e5c1-4a3f-b1e5-f9776d94cbe7
- Users: Ewing 680edc0d1504192884a148e0, Mark 68d1caac41d11ac1ce5df7a2
- Supabase table schemas: companies (3433+), persons (4586+), phone_numbers (4216+), lists (26+), list_assignments (1909+), do_not_call
- 14 dispositions defined (Meeting Set through Cancelled)
- Live analytics data: 2,481 total calls, 9 meetings set, 11% connection rate, 27% conversation rate
- 166 snoozed contacts, 3 follow-up tasks
- Webhook events: CALL_LOGGED, CONTACT_SNOOZED
- Ask variations by role (Placement Agent, CEO, MD/Partner, IR/Capital Formation)
- ALL backup files go to ~/Downloads, NEVER /tmp
- NEVER fabricate contact data

### Full Content
(Full 517-line content captured above. Complete Salesfinity API client with 35 endpoints, 6 gates, pitch templates, CLI reference.)

---

## SKILL: skill-creator
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/skill-creator/SKILL.md | ~/Projects/ewing-registry/skills/skill-creator/SKILL.md
BUSINESS RULES FOUND:
- Skill anatomy: SKILL.md (required) + optional scripts/, references/, assets/
- Progressive disclosure: metadata (always loaded) > SKILL.md body (<500 lines) > bundled resources (as needed)
- Description optimization: make descriptions "pushy" to combat undertriggering
- Must not contain malware, exploit code, or misleading content
- Test cases: 2-3 realistic prompts, with-skill AND baseline runs
- Evaluation: quantitative (grading.json) + qualitative (human review via eval-viewer)
- Description optimization: 60% train / 40% test split, 3 runs per query, max 5 iterations
- Cowork: use --static for viewer, no display available
- Never skip human review before iterating

### Full Content
(Full 486-line content captured above. Complete skill lifecycle: capture intent, interview, write SKILL.md, test, evaluate, iterate, optimize description, package.)

---

## SKILL: skill-loader
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/skill-loader/SKILL.md | ~/Projects/ewing-registry/skills/skill-loader/SKILL.md
BUSINESS RULES FOUND:
- Session startup: ALWAYS pull from GitHub first via skill-sync
- 6 default skills loaded every session: output-skill, prompt-refiner, skill-creator, tech-translator, debrief, skill-sync
- output-skill always loads FIRST (communication protocol)
- GitHub repo: ewing-operating-system/ewing-registry
- Sync: copy SKILL.md from each registry skill dir to local

### Full Content
(Full 60-line content captured above. Session bootstrapper with GitHub sync and 6 default skill loads.)

---

## SKILL: skill-sync
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/skill-sync/SKILL.md | ~/Projects/ewing-registry/skills/skill-sync/SKILL.md
BUSINESS RULES FOUND:
- Principle: ~/.claude/skills/ is LOCAL CACHE, ewing-registry/skills/ on GitHub is SOURCE OF TRUTH
- 3 operations: PULL (GitHub > local), PUSH (local > GitHub), CHECK (detect drift)
- PULL runs at session start (via skill-loader)
- PUSH runs every time a skill is created or modified
- CHECK runs on "sync skills" command or during debrief
- Never store skills ONLY on GitHub or ONLY locally
- Never create a skill without pushing

### Full Content
(Full 173-line content captured above. Complete sync protocol with PULL, PUSH, CHECK operations and interaction rules for debrief and skill-creator.)

---

## SKILL: storyteller
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/storyteller/SKILL.md | ~/Projects/ewing-registry/skills/storyteller/SKILL.md
BUSINESS RULES FOUND:
- 30-tag anti-pattern taxonomy (WRONG-MACHINE, DUPLICATE, BUILT-FROM-SCRATCH, etc.)
- 3 offense tags: OFFENSE-READY (green), ONE-CHANGE-AWAY (yellow), NOT-OFFENSE (red)
- Story rules: past tense, third person, 500-2000 words, name every tool/skill/file/API/database
- Business context: Ewing runs AND Capital, Scottsdale AZ. Mark dials alongside. 1,386 calls, 7 meetings week of March 16-20
- Business filter: "does this help Ewing get a signed representation agreement faster?"
- Always auto-push to GitHub ewing-registry

### Full Content
(Full 167-line content captured above. Complete thread historian with story format, 30-tag audit taxonomy, mandatory GitHub push.)

---

## SKILL: system-auditor
ENTITY: System (entity-agnostic)
SYNC: registry-only
LOCATION: ~/Projects/ewing-registry/skills/system-auditor/SKILL.md | live-site-audit.md
BUSINESS RULES FOUND:
- Registry at ~/.claude/skills/system-auditor/registry.json tracks every engine with last_audited, status, issues
- Rotating weekly audit loop: oldest-last-audited engine gets audited next
- 5-phase audit: Schema Contract > Data Flow > Logic > UX > Fix
- Key column mappings: person_graph_id (NOT person_id), outcome_category (NOT outcome), total_score (NOT ai_score), called_at (NOT created_at)
- Expected data counts: companies ~1,484, persons ~2,491, phone_numbers ~2,356, data_quality_issues ~19,884
- 6 audit categories: Database Schema, UI-Database Contracts, Data Completeness, GitHub Repo, API Connections, Data Quality
- Live site URL: https://blank-canvas-start-6129.lovable.app/
- 17 pages/routes defined for live site audit
- Scheduled: nightly at 2 AM (cron: 0 2 * * *)

### Full Content — SKILL.md
(Full 270-line content captured above. Complete rotating audit loop with registry, 5-phase audit, 6 audit categories, output format.)

### Full Content — live-site-audit.md
(Full 115-line content captured above. Published app health check with 5 phases: alive check, navigation, data verification, interactive elements, report.)

---

## SKILL: tech-translator
ENTITY: System (entity-agnostic)
SYNC: both
LOCATION: ~/.claude/skills/tech-translator/SKILL.md | ~/Projects/ewing-registry/skills/tech-translator/SKILL.md
BUSINESS RULES FOUND:
- Every translation has exactly 3 parts: What it says (plain English), What to do (one action), The lesson (one concept)
- Lessons are cumulative ("Remember sudo? Same idea here.")
- Analogies must use Ewing's world: sales, recruiting, M&A, deals, CRMs, pipelines, money
- Never skip the lesson — every translation is a learning opportunity
- Translate top to bottom in order for multi-item screens

### Full Content
(Full 55-line content captured above. Jargon-to-plain-English converter with 3-part translation format and cumulative learning model.)

---

# ENTITY AFFINITY SUMMARY

| Entity | Skills |
|--------|--------|
| Shared (NC + AND + RU) | cold-call-workflow |
| Shared capability | salesfinity-loader |
| Personal (Ewing) | finance-agent, password-migration, recording-collector |
| System (entity-agnostic) | clawdbot-creator, clawdbot-self-repair, data-architect, debrief, disk-cleanup, ewing-connectors, file-share, harvester, imessage-toggle, keys-and-credentials, mission-control, output-skill, prompt-refiner, rate-oracle, skill-creator, skill-loader, skill-sync, storyteller, system-auditor, tech-translator |

NOTE: revsup-oo and pec-case-manager are referenced in clawdbot-creator's skill library table but have NO .md files in either ~/.claude/skills/ or ~/Projects/ewing-registry/skills/. They may exist as built-in Claude skills or were never created as custom skills.

---

# CREDENTIAL PATTERN INDEX

Skills containing embedded API keys or credential values:
1. **clawdbot-creator** — Anthropic, Google Gemini, Google Custom Search, Supabase (anon + service role), Exa, Clay
2. **ewing-connectors** — ALL credentials (Supabase, Salesfinity, Exa, Clay, Google Sheets, Lovable, Groq, Together.ai, OpenAI, Mistral, Gemini, DeepSeek)
3. **keys-and-credentials** — ALL credentials with status tracking (duplicates ewing-connectors plus Privacy.com, Lob, mailer vendor placeholders, Google Maps)
4. **mission-control** — Supabase anon key (embedded in curl commands)
5. **output-skill** — Supabase URL + anon key + service role key + Gemini key
6. **salesfinity-loader** — Salesfinity API key + user IDs, Supabase URL
7. **rate-oracle** — Anthropic API key (in preflight script), Google Custom Search key
8. **cold-call-workflow/clay-integration** — Clay webhook URL, Google Sheet ID, Clay workspace URL
9. **system-auditor** — Salesfinity API key reference

---

# END OF EXTRACTION
## Total .md files read: 33
## Total unique skills: 26 (including imessage-toggle loose file)
## Skills with business rules: 26/26
## Skills with embedded credentials: 9
