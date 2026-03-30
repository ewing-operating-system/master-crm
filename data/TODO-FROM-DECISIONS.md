# TODO: Features & Changes from 97 CRM Decisions
**Source:** CRM-DECISIONS-EWING-RAW.md (2026-03-30)
**Generated:** 2026-03-28

---

## IMMEDIATE (Do Now — Schema Changes + Config Updates)

### Database Schema Changes
- [x] **Q2:** Add `manually_tagged` boolean to `targets` — classifier skips these
- [x] **Q5:** Implement confidence floor 1.5 → `human_review_queue`, no downstream work
- [x] **Q8:** Add `dnc_type` (hard/soft) and `allow_inbound_response` to `do_not_call`
- [x] **Q11:** Add `value_source` and `original_value` fields to track human corrections alongside system estimates
- [x] **Q13:** Add `field_confidence` JSONB to `dossier_final` for per-field CONFIRMED/ESTIMATED/UNKNOWN
- [x] **Q16:** Add `review_instructions` text field to `human_review_queue` for instructive details
- [x] **Q21:** Create `estimate_accuracy` table (original, corrected, delta, field, company, monthly agg)
- [x] **Q28:** Add `refresh_schedule` and `last_refreshed_at` to `engagement_buyers`

### Classification Engine Updates
- [ ] **Q1:** Update `lib/classification.py` — NC always wins over AND Capital. AND never automated.
- [ ] **Q3:** Support hybrid classification (campaign + content) for multi-entity people
- [ ] **Q6:** Orchestrator priority: urgency first, entity round-robin within tiers
- [ ] **Q9:** Multi-vertical priority order: NC > RU > AND
- [ ] **Q14:** Implement 70% completeness check for "ready" profiles

### Pipeline Logic
- [ ] **Q5:** Add confidence floor check at pipeline entry (< 1.5 → halt + human_review)
- [ ] **Q12:** Enforce 24hr regeneration cooldown on profiles
- [ ] **Q17:** Valuations always as ranges with educational framing
- [ ] **Q20:** Employee-to-revenue estimates require corroboration
- [ ] **Q22:** LLM disagreement → third LLM tiebreaker → human_review if still unclear
- [ ] **Q29:** Coordinate outreach for buyers appearing on multiple deal lists
- [ ] **Q30:** Buyer decline = that deal only, not global removal
- [ ] **Q65:** Pause auto-learning at 30 rules per category
- [ ] **Q74:** Always dual-LLM certification (never skip)
- [ ] **Q75:** 5-point pre-certification code check before LLM
- [ ] **Q77:** Orchestrator: urgency first, entity round-robin within tiers
- [ ] **Q78:** Recovery mode: 2x pacing, no burst, catch-up flag at backlog > 20
- [ ] **Q95:** Source hierarchy: Human > Salesfinity > Email > Fireflies > Exa > Estimated

### Template Updates
- [ ] **Q10:** Strip entity tags from client-facing pages. Branding = "Next Chapter Advisory"
- [ ] **Q11:** Human corrections displayed as primary value with footnote for system estimate
- [ ] **Q13:** Admin: confidence labels. Client: footnotes for estimated/unknown
- [ ] **Q16:** needs_review queue items include instructive details
- [ ] **Q23:** Every page includes methodology section (admin: full, client: lighter)
- [ ] **Q34:** DNC'd buyers visible to clients with reason
- [ ] **Q36:** Buyer fit scores visible to clients
- [ ] **Q42:** Meeting pages phone-optimized (key points top, collapsible, large taps)
- [ ] **Q43:** Joint meeting role assignments (Ewing: relationship/big picture, Mark: operational)
- [ ] **Q50:** Meeting pages include competitive intel when available
- [ ] **Q68:** Client pages show current version only (no version history)
- [ ] **Q83:** Continue static HTML alongside server pages
- [ ] **Q97:** Admin sees failed research. Client sees only wins.
- [ ] **Q98:** Hide research cost from client pages

### Fee Structure
- [ ] **Q39:** Fee calculator: $10K min, 10% success fee, 5% if commission >$500K. Buy-side 2-3%. Engagement fees separate.

### Feedback System
- [ ] **Q61/Q62:** Tag feedback by provider (Mark vs Ewing). Weight by domain.
- [ ] **Q64:** Guardrails always win. Log violations. Dashboard feed. Weekly review.
- [ ] **Q67:** Every edit = new version. ASK before regenerating.
- [ ] **Q72:** Mark override → reverts to needs_review. 3 overrides → rule proposal.

### Alert System
- [ ] **Q45:** iMessage meeting prep 30 min before. Format: company, 5 bullets, link.
- [ ] **Q73:** Review queue 24hr SLA + escalation via iMessage
- [ ] **Q86:** Monthly $500 ceiling. Alerts at $50 milestones. Slack + SMS.
- [ ] **Q89:** Weekly API key health check. 401/403 → iMessage alert.

### Listener Agent
- [ ] **Q91:** Priority order: Salesfinity transcripts → Email → Fireflies
- [ ] **Q47:** Post-meeting transcript analysis for outcome capture
- [ ] **Q93:** Unknown situations tiered by urgency (hot=fast, cold=queue)
- [ ] **Q94:** No historical scan on deploy. Start fresh.

### Orchestrator
- [ ] **Q69:** Lazy rebuild (mark stale, rebuild on view). Active engagements: background rebuild <1hr
- [ ] **Q79:** Maintenance mode: active/maintenance/paused states
- [ ] **Q80:** 5min orchestrator / 10sec worker confirmed — no changes
- [ ] **Q88:** Budget exhausted → queue with `deferred_until`, no work lost

### Dashboard
- [ ] **Q51:** Dashboard = landing page. Pipeline, reviews, problems, budget, quick links.
- [ ] **Q53:** System health widget: green/yellow/red. Red if worker down >15min.
- [ ] **Q54:** Mobile-responsive dashboard
- [ ] **Q56:** Entity filter buttons: [All] [NC] [AND] [RU] + person presets
- [ ] **Q58:** "While you were away" summary since last_viewed_at
- [ ] **Q59:** Auto-refresh every 5 minutes
- [ ] **Q64:** Guardrail violation feed on dashboard

### Web Infrastructure
- [ ] **Q81:** Public URLs for clients. Email gating. Domain-name default passwords.
- [ ] **Q82:** No auth for now. Wide open. Phase 2: login.
- [ ] **Q85:** No WebSockets. Page refresh + 5-min auto-refresh.
- [ ] **Q90:** Deployment: manual git pull. Future: deploy script → webhook.

---

## THIS_WEEK (Build Within 7 Days)

### Buy-Side Architecture
- [ ] **Q15:** Criteria selector UI for buy-side clients. Ad-hoc criterion fields push to search engines. Buyer suggestions → lookalike training.
- [ ] **Q19:** Buy-side templates: criteria fit, estimated value, EBITDA lever scores. Not strategy consulting.
- [ ] **Q26:** Buyer list count adaptive by vertical

### Buyer Management
- [ ] **Q35:** Multi-signal stage advancement for positive buyer responses
- [ ] **Q37:** "Active Acquirer" flag — increases fit score, moves buyer up

### Meeting System
- [ ] **Q41:** 24hr pre-meeting prep generation. Regenerate on new data.
- [ ] **Q44:** Reschedule → regenerate. Keep old version.
- [ ] **Q49:** Context-switch alerts for back-to-back meetings with different companies

### Version System
- [ ] **Q66:** Last 10 versions in UI. Older → archive table.
- [ ] **Q70:** "Why was this changed?" field exposed in UI

### Cost Monitoring
- [ ] **Q57:** Anomaly-based budget alerts (detect runaway API calls like Exa 6000-call incident)
- [ ] **Q87:** Per-company budget caps within entity

---

## NEXT_WEEK (Build Within 14 Days)

### Data Room
- [ ] **Q99:** Interactive data room pages. Track client interactions (slider changes, field edits). Store behavioral data for learning.

### Entity Transitions
- [ ] **Q4:** Dual-tag support for entity transitions. Primary + secondary entity fields.

### Multiples Engine
- [ ] **Q18:** Full segmentation of multiples by geography, size, recency

### Dashboard Advanced
- [ ] **Q52:** Pipeline + fee revenue metrics on dashboard
- [ ] **Q60:** System confidence metric: "Data Quality: X% confirmed, Y% estimated, Z% unknown"

### Auto-Approval
- [ ] **Q71:** Per-vertical graduation of auto-approval trust thresholds

### Feedback Propagation
- [ ] **Q63:** "Apply this feedback to 5 similar companies?" — suggest, never auto-apply

---

## FUTURE (Backlog / Phase 2+)

### Buying Signal Agent
- [ ] **Q27:** Separate agent for buying signals. Apify on Instagram. Watch companies over time.

### Smart Call Cards
- [ ] **Q46:** Push smart card to screen during live calls (company summary, talking points, recent activity)

### Auto-Acquirer Detection
- [ ] **Q40:** Monthly Exa scan for buyer acquisitions. Auto-flag Active Acquirer.

### Multi-User Server
- [ ] **Q84:** Flask/FastAPI with multi-threading. Writes through queue.

### Meeting Page Architecture
- [ ] **Q48:** Meeting type enum vs free text — needs architecture review first

### Auto-Trust
- [ ] **Q92:** Stake-based auto-trust thresholds (low/medium/high stakes)

### LinkedIn Orchestration
- [ ] **Q33:** LinkedIn sub-agent master for campaign orchestration (load lists, create campaigns)

### Research Transparency
- [ ] **Q96:** Client-facing research methodology sections

### NC Completion
- [ ] **Q100:** Data coherence audit across existing Supabase tables. Pull together 100s of companies.

---

## NOTES

### Needs Discussion (Flagged)
- **Q48:** Meeting type enum — needs meeting page template architecture review

### Cost Monitoring Agent (Flagged by Ewing)
- From Q86: "Need to build a cost monitoring agent or add to orchestration agent. Something needs to be checking methods used vs. methods available when costs start adding up beyond expectations."
- Root cause referenced: Exa called 6,000 times in one day because downstream agents were failing and upon reset, ran Exa again even though data existed.

### Key Principles Confirmed
- NC always wins over AND Capital (Q1, Q9, Q100)
- Urgency always beats entity priority (Q6, Q77)
- Human always wins over machine (Q2, Q11, Q72)
- Dual-LLM certification always required (Q74)
- Guardrails always win over feedback (Q64)
- Transparency is the brand (Q23, Q96, Q99)
- Letters + phone calls are the only proven outreach methods (Q91)

---

*97 decisions → 120+ action items. Biggest single rules update ever.*
