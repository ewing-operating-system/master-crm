# Permissions Log — Master CRM Build Session
**Created**: 2026-03-30 16:40 MST
**Purpose**: Track ALL permission issues encountered during builds so they can be solved once and for all.

---

## Feature #70: Permission Resolution Project
**Status**: ACTIVE — This IS the feature that solves permissions permanently.
**Goal**: Zero permission blocks for future builds.

---

## Permissions Needed

### 1. File Write Access — master-crm repo
| Path | Operation | Feature | Status |
|------|-----------|---------|--------|
| `/Users/clawdbot/projects/master-crm/lib/*.py` | Write new files | #62-69 | NEEDED |
| `/Users/clawdbot/projects/master-crm/scripts/*.py` | Write new files | #66 Auto-Regen | NEEDED |
| `/Users/clawdbot/projects/master-crm/agents/listener/agent.py` | Write new file | #68 Listener | NEEDED |

### 2. File Write Access — master-crm-web repo
| Path | Operation | Feature | Status |
|------|-----------|---------|--------|
| `/Users/clawdbot/projects/master-crm-web/public/*.html` | Write new pages | #63-69, #41-61 | NEEDED |
| `/Users/clawdbot/projects/master-crm-web/public/*.js` | Write new JS | #41 Interactive Proposals | NEEDED |
| `/Users/clawdbot/projects/master-crm-web/api/letters/send.js` | Write API route | #63 Lob | NEEDED |
| `/Users/clawdbot/projects/master-crm-web/lib/*.py` | Edit existing | #62 Letter Engine | NEEDED |

### 3. File Edit Access — Existing Files
| Path | Operation | Feature | Status |
|------|-----------|---------|--------|
| `/Users/clawdbot/projects/master-crm/lib/exa_client.py` | Add batch functions | #65 SAP Turbo | NEEDED |
| `/Users/clawdbot/projects/master-crm/lib/auto_refresh.py` | Add deploy functions | #66 Auto-Regen | NEEDED |
| `/Users/clawdbot/projects/master-crm-web/public/source-attribution.js` | Add load/render funcs | #67 Source Attribution | NEEDED |
| `/Users/clawdbot/projects/master-crm-web/public/feature-roadmap.html` | Update stats | Roadmap | NEEDED |
| `/Users/clawdbot/projects/master-crm/data/feature-roadmap.html` | Update stats | Roadmap | NEEDED |

### 4. Git Operations
| Operation | Repos | Status |
|-----------|-------|--------|
| `git add` | master-crm, master-crm-web | NEEDED |
| `git commit` | master-crm, master-crm-web | NEEDED |
| `git push` | master-crm, master-crm-web | NEEDED |

### 5. Shell/Bash Commands
| Command | Purpose | Status |
|---------|---------|--------|
| `openclaw message send` | Telegram notifications | GRANTED |
| `python3 <script>` | Run integration tests | NEEDED |
| `node <script>` | Run JS tests | NEEDED |
| `curl` / `urllib` | API calls (Lob, Exa, Salesfinity, Supabase) | NEEDED |

### 6. Cron/Background
| Operation | Purpose | Status |
|-----------|---------|--------|
| Cron job creation (durable) | Roadmap auto-update | GRANTED |
| Background agent spawning | Parallel builds | GRANTED |

---

## Permission Failures Encountered This Session

| Time | Agent/Task | File | Operation | Error |
|------|------------|------|-----------|-------|
| 16:35 | SAP+AutoRegen+Source agent | `lib/exa_client.py` | Edit | Permission denied — agent couldn't edit existing files |
| 16:35 | SAP+AutoRegen+Source agent | `lib/auto_refresh.py` | Edit | Permission denied |
| 16:35 | SAP+AutoRegen+Source agent | `public/source-attribution.js` | Edit | Permission denied |
| 16:35 | SAP+AutoRegen+Source agent | `lib/sap_turbo.py` | Write | Permission denied — agent couldn't create new files |
| 16:35 | SAP+AutoRegen+Source agent | `scripts/auto_regen_daemon.py` | Write | Permission denied |
| 16:35 | SAP+AutoRegen+Source agent | `public/source-attribution.html` | Write | Permission denied |
| 16:36 | Lob+CampaignMgr agent | `api/letters/send.js` | Write | Permission denied |
| 16:36 | Lob+CampaignMgr agent | `public/letter-send.html` | Write | Permission denied |

---

## Resolution Plan

### Option A: Grant blanket Write+Edit to subagents (recommended)
Add to Claude Code settings:
```json
{
  "permissions": {
    "allow": [
      "Write(/Users/clawdbot/projects/master-crm/**)",
      "Write(/Users/clawdbot/projects/master-crm-web/**)",
      "Edit(/Users/clawdbot/projects/master-crm/**)",
      "Edit(/Users/clawdbot/projects/master-crm-web/**)",
      "Bash(git *)"
    ]
  }
}
```

### Option B: Per-directory rules
Grant Write/Edit access to specific directories only:
- `lib/` — Python modules
- `public/` — HTML/JS pages
- `api/` — Vercel API routes
- `scripts/` — Automation scripts
- `agents/` — Agent code

### Option C: Pre-approve all operations for this project
Use `.claude/settings.json` to auto-approve all file operations within the master-crm project directories.

---

## Notes
- Main thread (Argus) has Write+Edit access — only subagents are blocked
- This causes 6 agents to fail and fall back to main thread, slowing builds significantly
- Solving this means future feature builds can fully parallelize
