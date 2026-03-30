# INTEGRATED EXECUTION PLAN — All 10 Builds + Reprocessed Priorities
**Date**: 2026-03-30 14:00 MST
**Status**: Merged original 10 builds with new item numbering (62-69)
**Vision**: Research → Letter → Mail → Call → Deal

---

## THE 12-ITEM EXECUTION SEQUENCE

### PHASE 1: CORE EXECUTION MACHINE (Days 1-4)
**Goal**: Get from research to mailed letter to call list, with operator ready to pick up phone.

#### BUILD 1 (NEW #62): Letter Template Engine 🔴 TONIGHT
- **Owner**: Research → Letter transformation
- **Output**: `letter_text`, `personalization_score`, operator-friendly tone
- **Blocks on**: RESEARCHER (research_quality_score ≥0.70)
- **Unblocks**: Lob Integration, Meeting Page v2, Campaign Manager
- **Est. time**: 4-5 hours
- **Cost**: ~$0.10/target (1 LLM call per letter)

#### BUILD 1.5 (NEW #70): Meeting Page v2 — Data Collection Engine 🟡 SAME NIGHT
- **Owner**: During-call data capture → downstream intelligence
- **Output**: Meeting notes form, auto-gen summary, data completeness score, action items
- **Blocks on**: Nothing (parallel with Letter Engine)
- **Unblocks**: Letter Engine (owns story elements, emotional hooks), Proposal Engine (revenue/margins), Buyer Targeting
- **Est. time**: 3-4 hours
- **Cost**: $0.00 (form + local processing)

**Why both tonight**: Meeting data feeds letter generation. If captured first, letters are 10x better.

---

#### BUILD 2 (NEW #63): Lob API Integration 🟡 TOMORROW
- **Owner**: Physical letter delivery
- **Output**: `lob_tracking_id`, delivery webhook, cost tracking
- **Blocks on**: Letter Template Engine (#62)
- **Unblocks**: Campaign Manager, Listener Agent
- **Est. time**: 3-4 hours
- **Cost**: $1.50-2.00 per letter (Lob)

#### BUILD 3 (NEW #64): Campaign Manager UI 🟡 WED-THU
- **Owner**: Central control panel for 250/150 rule (250 letters sent → pause until 150 called 5x each)
- **Output**: Queue depth visibility, delivery dashboard, send cadence controls, Telegram notifications
- **Blocks on**: Lob Integration (#63) + Salesfinity Integration (#54)
- **Unblocks**: Graduated Auto-Trust (#9)
- **Est. time**: 6-8 hours
- **Cost**: $0.00 (UI + orchestration)

**Key rule**: No new batch until 150 of previous 250 called 5x. Governor prevents spam.

---

### PHASE 2: POLISH & OPTIMIZATION (Days 5-7)
**Goal**: Make the shareable URL work flawlessly on mobile; scale from 1 to 1000.

#### BUILD 5 (NEW #71): Shareable URL Experience Polish 🟡 FRI-SAT
- **Owner**: Mobile-first optimization for interactive proposals
- **Output**: Sub-2-second load, responsive design, touch-optimized, data room gate works on mobile
- **Blocks on**: All proposal pages built (they exist)
- **Unblocks**: Full-scale rollout, rep confidence
- **Est. time**: 4-5 hours
- **Cost**: $0.00 (CSS/JS optimization)

**Test checklist**:
- iPhone 12/14 viewport (375px width)
- Slider interactions on touch
- Button tap targets ≥48px
- Page load <2s on 4G
- Data room gate flow works mobile

---

#### BUILD 6 (NEW #66): Auto-Regeneration Pipeline 🟡 SAT-SUN
- **Owner**: Research → HTML → Git → Vercel → Live URL (no human in loop)
- **Output**: Automated pipeline, triggered on research completion
- **Blocks on**: Letter Engine, Proposal Template System
- **Unblocks**: Listener Agent (closed-loop feedback)
- **Est. time**: 4-6 hours
- **Cost**: $0.00 (orchestration)

**Flow**: `target_research` row → trigger → render HTML → `git add/commit/push` → Vercel deploy → URL live in <2min

---

### PHASE 3: CALL → RESPONSE LOOP (Days 8-10)
**Goal**: Calls come in, system catches the signal, feeds it back.

#### BUILD 4 (NEW #65): SAP-Quality Research for All 193 Buyers 🟡 PARALLEL
- **Owner**: Researcher agent upgrade to 7-section depth per buyer
- **Output**: Company overview, acquisition history, strategic rationale, financial capacity, decision-makers, recent news, approach strategy
- **Blocks on**: Nothing (researcher runs autonomously)
- **Unblocks**: Salesfinity Integration (better targeting)
- **Est. time**: 40-60 hours (runs via cron, not human time)
- **Cost**: ~$0.50-0.80 per buyer (Exa.ai queries)

---

#### BUILD 7 (NEW #54): Salesfinity Integration 🟡 FRI-MON
- **Owner**: Call outcomes loop
- **Output**: Contact load, call tracking, outcome sync back to Supabase
- **Blocks on**: Campaign Manager (#64) + Lob Integration (#63)
- **Unblocks**: Graduated Auto-Trust (#9), Listener Agent (#10)
- **Est. time**: 5-7 hours
- **Cost**: $0.00 (API integration)

**Flow**: Letter arrives → Lob webhook → auto-populate Salesfinity call list → rep calls → outcome logged → plays table updated

---

#### BUILD 10 (NEW #51/68): Listener Agent 🔵 MON-TUE
- **Owner**: 5-channel signal ingestion
- **Output**: Play records, engagement scores, response routing
- **Blocks on**: Salesfinity (#54) + Email tracking
- **Unblocks**: Graduated Auto-Trust (#9)
- **Est. time**: 6-8 hours
- **Cost**: $0.02-0.05 per signal

**Channels**:
- Salesfinity: call outcomes
- Email: reply detection
- Lob: delivery confirmation
- Calendar: meeting booked
- Slack: manual notes

---

### PHASE 4: INTELLIGENCE & SCALE (Days 11-14)
**Goal**: Data quality, attribution, auto-escalation.

#### BUILD 8 (NEW #67): Source Attribution UI 🟡 LATER
- **Owner**: Footnote every fact with source URL
- **Output**: story_cards with source_url, primary/secondary tagging, corroboration flags
- **Blocks on**: RESEARCHER completion
- **Unblocks**: Audit compliance, transparency
- **Est. time**: 2-3 hours
- **Cost**: $0.00

**Format**: "Springer has 26-city coverage[1]" → click [1] → shows source URL

---

#### BUILD 9 (NEW #69): Graduated Auto-Trust 🟡 LATER
- **Owner**: Auto-send escalation based on approval history
- **Output**: Auto-send rules, inspection windows, Telegram notifications
- **Blocks on**: Campaign Manager (#64) + Listener Agent (#51)
- **Unblocks**: Scale to thousands
- **Est. time**: 2-3 hours
- **Cost**: $0.00

**Rules**:
- First 10 letters: manual approval
- 11-50: auto-send with 24-hour inspection window
- 51+: auto-send immediately, log only

---

#### BUILD 4b (NEW #65b): Multi-Entity Research Templates 🟡 PARALLEL
- **Owner**: Industry-specific story hooks by entity + sub_type
- **Output**: Trades (garage, disaster), Healthcare (compliance), SaaS (product origin), AND (fund thesis)
- **Blocks on**: Nothing (research enhancement)
- **Unblocks**: Research quality improvement
- **Est. time**: 2-3 hours
- **Cost**: $0.00

---

## EXECUTION TIMELINE

| Phase | Dates | Builds | Status | Next Gate |
|-------|-------|--------|--------|-----------|
| **Phase 1A** | Tonight | #62, #70 | READY | Letter generated for 2 test targets |
| **Phase 1B** | Tomorrow | #63 | READY | Lob API working, 5 letters mailed |
| **Phase 1C** | Wed-Thu | #64 | READY | Campaign manager live, queue visible |
| **Phase 2** | Fri-Sat | #71 | READY | Mobile test: all pages <2s load |
| **Phase 2b** | Sat-Sun | #66 | READY | Auto-regen: new research → live URL |
| **Phase 3A** | Parallel | #65 | AUTONOMOUS | Researcher running nightly |
| **Phase 3B** | Fri-Mon | #54 | READY | Salesfinity loaded, rep dialing |
| **Phase 3C** | Mon-Tue | #51 | READY | Signals flowing back, plays updating |
| **Phase 4A** | Later | #67 | READY | Source attribution live |
| **Phase 4B** | Later | #69 | READY | Auto-send enabled, scale unlocked |

---

## CRITICAL DEPENDENCIES

```
TONIGHT:
  #62 (Letter Engine) ──┬──→ #63 (Lob) ──→ #64 (Campaign Manager)
  #70 (Meeting Page) ──┘
                         ↓
  Enables: #71, #66, #54

TOMORROW/SOON:
  #63 (Lob) ──→ #64 (Campaign Manager) ──→ #54 (Salesfinity)
  #64 ──────────────────────────────────→ #51 (Listener)
  #54 ──────────────────────────────────→ #51 (Listener)
  #51 ──────────────────────────────────→ #69 (Auto-Trust)

PARALLEL (non-blocking):
  #65 (SAP Research) — autonomous, runs nightly via cron
  #71 (URL Polish) — mobile optimization
  #66 (Auto-Regen) — setup after phase 1 complete
```

---

## SUCCESS CRITERIA BY PHASE

### Phase 1 Complete (Tomorrow EOD)
- ✅ 2 test letters generated (AquaScience, Springer Floor)
- ✅ Letters pass personalization score ≥0.80
- ✅ 5 test letters mailed via Lob
- ✅ Lob tracking IDs logged to Supabase
- ✅ Campaign Manager shows 5 letters in flight

### Phase 2 Complete (Saturday EOD)
- ✅ All interactive proposals load <2s on 4G
- ✅ Sliders work on touch
- ✅ Data room gate works on mobile
- ✅ Auto-regen pipeline live: new research → URL in <2min

### Phase 3 Complete (Tuesday EOD)
- ✅ Salesfinity dialer populated with 50+ contacts
- ✅ First 5 call outcomes logged in Supabase
- ✅ Listener agent ingests Salesfinity signals
- ✅ Play records created, engagement scores calculated

### Phase 4 Complete (Next Week)
- ✅ Source attribution on all story cards
- ✅ Graduated auto-trust enabled
- ✅ System running autonomously: research → letter → mail → call → response → next action

---

## THE MACHINE AT FULL POWER

After all 12 builds:

1. **Research finds target** (RESEARCHER agent, autonomous)
2. **Meeting captured** (rep + Meeting Page v2 form)
3. **Letter written** (Letter Template Engine, personalization ≥0.80)
4. **Letter mailed** (Lob, physical delivery)
5. **Call list populated** (Salesfinity webhook from Lob delivery)
6. **Operator calls** (5x per prospect, outcomes logged)
7. **Signals ingested** (Listener: calls, emails, meetings)
8. **Auto-escalation** (Graduated Auto-Trust if score ≥10)
9. **Attribution transparent** (Source footnotes on every fact)
10. **Loop closes** (Response → regenerate pages → send next message)

**Cost per fully-processed target**: ~$2.50-3.50 (Lob $2.00 + LLM $0.50-1.00 + Exa $0.00-0.50)

**Velocity**: 250 letters → pause for 150 calls → repeat. Or with auto-trust: 2,500+ letters per month.

---

## WHAT THIS MEANS FOR TONIGHT

**Do both #62 and #70 simultaneously** (parallelizable):
- #62 (Letter Template): Build generator, test on AquaScience + Springer
- #70 (Meeting Page v2): Build form + auto-summary, test integration

**Result**: By tomorrow morning, you have:
- Working letter generator (5 test letters quality-verified)
- Data collection form that feeds letter quality
- Proof that research → personalized letter → mail works end-to-end

**Then**: Plug in Lob tomorrow and you're live.

---

**Document Created**: 2026-03-30 14:00 MST
**Version**: 1.0 — INTEGRATED (Original 10 + New Items 62-69 = 12 Total)
**Next**: Execute Phase 1A tonight
