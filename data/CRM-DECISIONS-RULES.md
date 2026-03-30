# CRM Decisions — System Rules
**Source:** CRM-DECISIONS-EWING-RAW.md (2026-03-30)
**Decisions:** 97/97
**Generated:** 2026-03-28

---

## HARD DECISIONS (13)

### Rule Q1: NC Always First Over AND Capital
**Decision:** Next Chapter always wins if there is a fit. Family offices are potential buyers, not AND Capital investors. System never auto-classifies NC leads as AND. AND Capital is never automated.
**System impact:** Classification engine must check NC fit first. AND Capital classification requires explicit human intervention. Family office contacts route to NC buyer pipeline.
**Affected:** `lib/classification.py`, `targets`, `human_review_queue`
**Status:** immediate

### Rule Q15: Buy-Side Proposal = Criteria Selectors + Matchmaking Pitch
**Decision:** Buy-side proposals show target companies matching buyer criteria. First meeting includes criteria selectors for their industry. Ad-hoc criterion input that feeds search engines. Pitch is matchmaking with 2-3% success fee. Buyer suggestions become lookalikes for fit score training.
**System impact:** Need criteria selector UI for buy-side clients. Ad-hoc criterion fields push to search engines. Buyer suggestions feed fit score lookalike training. Buy-side proposal template differs from sell-side.
**Affected:** `proposals`, `engagement_buyers`, buy-side page templates, search engines
**Status:** needs_build

### Rule Q19: Buy-Side = Fill The Order, Not Strategy Consulting
**Decision:** Buy-side is about selection criteria, estimated worth, EBITDA levers. Not a growth strategy project. We fill the order, not change their strategy. Show how targets fit selection criteria.
**System impact:** Buy-side page templates focus on: criteria fit, estimated value, EBITDA lever scores (positive and negative). No McKinsey-style strategy content.
**Affected:** Buy-side proposal templates, buyer 1-pager templates
**Status:** immediate

### Rule Q27: Target Sourcing = Multi-Channel + Buying Signal Agent
**Decision:** Source targets via phone calls, letters, emails, lunch invites, networking, public listings. Need separate agent for buying signals (watch companies over time, e.g., Apify on Instagram). Weiser wants 5 vetted targets on calendar this year.
**System impact:** Build buying signal agent (Phase 2). Apify Instagram integration for target monitoring. Weiser pipeline target: 5 vetted, calendar-ready targets.
**Affected:** New agent needed, `tam_businesses`, `acquisition_targets`
**Status:** needs_build

### Rule Q33: Outreach Execution = APIs + Salesfinity + LinkedIn Helper
**Decision:** Letters sent via API automatically. Salesfinity is always the calling system. LinkedIn Helper on desktop with manual list loading. Need LinkedIn sub-agent master for campaign orchestration.
**System impact:** Letter sending automated via API. Salesfinity integration confirmed as primary dialer. LinkedIn campaigns require manual instructions for list loading. Need LinkedIn orchestration sub-agent.
**Affected:** `outreach_queue`, `sent_log`, `dialer_queue`, Salesfinity integration
**Status:** immediate

### Rule Q38: Competitive Response = Urgency + Research Depth
**Decision:** Build attack plan with detailed research immediately. Don't directly address competition but emphasize "we can dial this list tomorrow." Walk away only on explicit "no opportunity" message.
**System impact:** Competitive mention triggers urgent attack plan build. Emphasis on speed-to-dial capability in messaging. Pipeline status only moves to lost on explicit rejection.
**Affected:** `play_templates`, `situation_library`, pipeline status logic
**Status:** immediate

### Rule Q39: Fee Structure
**Decision:** $10K minimum, 10% of transaction. If commission would be $500K+ at 5%, use 5%. Fixed dollar engagement fee for data/calling. Success fee % slides with deal size. Buy-side 2-3%. Sell-side 5-7%. Engagement fees separate.
**System impact:** Fee calculator in proposals. Sliding scale logic: min($10K, 10%) for small deals, 5% for large deals (>$500K commission threshold). Buy-side vs sell-side fee tiers. Engagement fee as separate line item.
**Affected:** `proposals`, fee calculation engine, proposal templates
**Status:** immediate

### Rule Q61: Feedback Provider Roles — Mark vs Ewing
**Decision:** Learn patterns from each. Mark = wordsmith, final copy reviewer. Ewing = system architect, has closed transactions. Lean Ewing on content structure/layout/components. Lean Mark on English/words/facts/final send. Final say usually Mark (works downstream).
**System impact:** `feedback_log` must track who provided feedback. Weight differently by domain: structure feedback from Ewing, copy feedback from Mark. Mark has final say on customer-facing content.
**Affected:** `feedback_log`, learning engine, `rule_sets`
**Status:** immediate

### Rule Q62: Differentiate Learning from Mark vs Ewing
**Decision:** Yes, differentiate. Both swarm to everything client-facing for now.
**System impact:** Tag every feedback entry with provider. Build separate pattern models per person. Both get visibility into all client-facing content.
**Affected:** `feedback_log`, learning engine
**Status:** immediate

### Rule Q81: Web Server Must Be Internet-Accessible
**Decision:** Clients must access data rooms. Not a local application. Clients need public URLs. Email gating is fine. Default passwords = their website domain name.
**System impact:** Server must be publicly accessible. Email-gated access with domain-name default passwords. No local-only deployment.
**Affected:** Web server infrastructure, authentication system
**Status:** needs_build

### Rule Q82: Authentication — Wide Open For Now
**Decision:** Clients get access too. No login for now, wide open. Mark and Ewing are both admins with equal permissions.
**System impact:** No authentication required currently. All pages publicly accessible. Phase 2: add login. Mark and Ewing = equal admin permissions.
**Affected:** Web server, all page routes
**Status:** immediate

### Rule Q86: Monthly Spend Ceiling $500
**Decision:** Monthly ceiling $500. Alerts at every $50 milestone. Slack + SMS notifications. Need cost monitoring agent to check methods used vs methods available when costs spike. Prevent duplicate API calls on agent reset.
**System impact:** `cost_budget` table updated with $500 monthly ceiling. Alert triggers at $50, $100, $150... $500. Dual notification: Slack + SMS. Cost monitoring agent or orchestrator extension needed. Dedup API calls on agent retry.
**Affected:** `cost_budget`, `cost_log`, orchestrator, alert system
**Status:** immediate

### Rule Q91: Listener Priority — Salesfinity First
**Decision:** Salesfinity transcripts first, then email, then Fireflies. Email and Salesfinity are both MUST channels (90% of communication). Letters and phone calls are the two methods that work. Email and LinkedIn are distant in effectiveness.
**System impact:** Listener agent processes Salesfinity transcripts first priority. Email second. Fireflies third. Outreach strategy leans heavily on letters + phone calls. Email/LinkedIn secondary.
**Affected:** Listener agent, `play_templates`, outreach prioritization
**Status:** immediate

### Rule Q96: Research Transparency — Show Clients
**Decision:** Build research transparency in. Clients love knowing the methodology. Leads with transparency, methodology, research, rigor, precision.
**System impact:** Client-facing pages include research methodology sections. Lighter version for clients (full for admin). Transparency is a brand differentiator.
**Affected:** All client-facing page templates
**Status:** immediate

### Rule Q99: Minimum Viable Data Room
**Decision:** Need a page to send prospects that's part of our file on them, showing what we know. Must include: who we are, who we represent (if buy-side), what separates us, success history, plan for their goals. Interactive is key — sliders and editable fields. Store client changes for behavioral learning.
**System impact:** Build interactive data room pages. Track all client interactions (slider changes, field edits). Store behavioral data for learning. This is high-value data that replaces phone call discovery.
**Affected:** Data room templates, new client_interactions table needed, behavioral learning engine
**Status:** needs_build

### Rule Q100: NC Priority Over AND Capital
**Decision:** NC represents businesses to sell. AND Capital is a distant 2nd. Ensure data is coherent, attack lists built, research engines ready to audit existing data across 100s of companies.
**System impact:** Resource allocation: NC first. Data coherence audit needed across existing Supabase tables. Attack list builder must pull together existing research.
**Affected:** Orchestrator priority, data audit tools
**Status:** immediate

---

## NUANCED DECISIONS (28)

### Rule Q3: Multi-Entity People — Hybrid Classification
**Decision:** Choice C — Hybrid. Classify by campaign AND content context.
**System impact:** People spanning multiple entities (like Mark) get classified by the campaign they're working + the content type. Both dimensions stored.
**Affected:** `lib/classification.py`, `contacts`, `targets`
**Status:** immediate

### Rule Q4: Entity Transitions — Dual-Tag
**Decision:** Choice C — Dual-tag. NC deal that becomes AND investment gets both tags.
**System impact:** Records can carry multiple entity tags. Primary entity + secondary entity fields. Transition history preserved.
**Affected:** `targets`, `companies` (may need secondary_entity column)
**Status:** needs_build

### Rule Q6: Urgency Always Beats Entity Size
**Decision:** Choice B — Urgency always first. Process urgent items before cycling through entities.
**System impact:** Orchestrator priority: urgency tier first, entity round-robin within tiers. Hot leads process before any cold leads regardless of entity.
**Affected:** Orchestrator, `agent_queue`
**Status:** immediate

### Rule Q8: DNC = Binary + Inbound Exception
**Decision:** Choice C — Binary DNC with inbound exception. DNC blocks all outbound. But if they contact us first, we can respond.
**System impact:** Add `dnc_type` column to `do_not_call`: 'hard' or 'soft'. Add `allow_inbound_response` boolean (default true for soft). Outbound engines check DNC. Inbound processing checks for soft DNC exception.
**Affected:** `do_not_call`, outreach engines, listener agent
**Status:** immediate

### Rule Q12: Profile Regeneration — Trigger + 24hr Cooldown
**Decision:** Choice C — Regenerate on significant new data, but enforce 24hr cooldown between regenerations.
**System impact:** Track `last_regenerated_at` on profiles. New data triggers regen only if >24hr since last. Prevents regeneration storms during rapid data ingestion.
**Affected:** `dossier_final`, `dossier_runs`, regeneration engine
**Status:** immediate

### Rule Q14: Minimum 70% Data Completeness for "Ready"
**Decision:** Choice B — 70% completeness threshold for a profile to be considered "ready" for downstream use.
**System impact:** Calculate completeness score on profile generation. Below 70% = stays in needs_review. At/above 70% = eligible for proposals and outreach.
**Affected:** `dossier_final`, certification engine, pipeline logic
**Status:** immediate

### Rule Q17: Wrong Valuation — Range + Framing
**Decision:** Choice C — Show valuation as a range with educational framing. Not a deal-killer, not a conversation-starter alone. A range with context.
**System impact:** Valuations always presented as ranges, not point estimates. Educational framing: "based on industry multiples, similar companies..." Never a single number.
**Affected:** Valuation engine, all templates showing valuation
**Status:** immediate

### Rule Q18: Multiples — Full Segmentation
**Decision:** Choice B — Multiples vary by geography, company size, and data recency. Full segmentation applied.
**System impact:** Multiple lookup tables segmented by geography, size tier, and data vintage. Stale multiples flagged.
**Affected:** Valuation engine, `companies` (market_multiples field)
**Status:** needs_build

### Rule Q20: Revenue from Employee Count — Only With Corroboration
**Decision:** Choice B — Employee-to-revenue estimates only when corroborated by at least one other signal.
**System impact:** Revenue estimation from employee count requires corroboration. Mark as ESTIMATED with methodology note. Single-source employee-based estimates blocked.
**Affected:** Research engine, `companies` (estimated_revenue confidence)
**Status:** immediate

### Rule Q25: Owner-Operators — Treat Normally
**Decision:** Choice B — No special handling for owner-operators. Same pipeline, same process.
**System impact:** No special routing or handling flags for owner-operators. Standard pipeline processing.
**Affected:** No changes needed
**Status:** immediate

### Rule Q26: Buyers Per Deal — Adaptive by Vertical
**Decision:** Choice C — Number of buyers varies by vertical. Some verticals have more active acquirers than others.
**System impact:** Buyer list target count configured per vertical. Dense verticals get larger lists. Niche verticals get smaller, more targeted lists.
**Affected:** Buyer research engine, `engagement_buyers`, vertical config
**Status:** needs_build

### Rule Q29: Multi-Deal Buyers — Coordinated
**Decision:** Choice B — When a buyer appears on multiple deal lists, coordinate outreach across deals. Don't contact independently for each.
**System impact:** Buyer dedup across active engagements. Single coordinated outreach mentioning relevant opportunities. Flag multi-deal buyers in UI.
**Affected:** `engagement_buyers`, outreach engine, buyer overlap detection
**Status:** immediate

### Rule Q30: Buyer Decline — That Deal Only
**Decision:** Choice B — Buyer declining one deal does NOT remove them from other deal lists. Decline is deal-specific.
**System impact:** Decline status on `engagement_buyers` is per-record, not per-buyer-globally. Buyer remains active on other engagements.
**Affected:** `engagement_buyers` status logic
**Status:** immediate

### Rule Q35: Positive Buyer Response — Multi-Signal Trigger
**Decision:** Choice C — Multi-signal detection for stage advancement. Not just one email or call, but combined signals.
**System impact:** Stage advancement requires multiple positive signals (e.g., responded + expressed interest + agreed to meeting). Configurable signal weights per stage transition.
**Affected:** Pipeline stage logic, `engagement_buyers`, listener agent
**Status:** needs_build

### Rule Q46: Live Calls — Smart Card
**Decision:** Choice B — Smart card pushed to screen during live calls. Key data points, not overwhelming.
**System impact:** Call screen integration shows: company summary, key talking points, recent activity, owner details. Compact format.
**Affected:** Call prep engine, Salesfinity integration
**Status:** needs_build

### Rule Q47: Post-Meeting Outcomes — Transcript Analysis
**Decision:** Choice B — Analyze meeting transcripts to capture outcomes automatically.
**System impact:** Fireflies/Salesfinity transcripts auto-analyzed for: outcome classification, action items, commitments, next steps. Results stored and trigger pipeline updates.
**Affected:** Listener agent, `call_analysis`, transcript processing
**Status:** immediate

### Rule Q49: Back-to-Back Meetings — Context-Switch Alerts
**Decision:** Choice B — Alert system for context switches between different companies in back-to-back meetings.
**System impact:** Calendar scan detects back-to-back meetings with different companies. Push context-switch alert with key differentiators between the two companies.
**Affected:** Meeting prep engine, calendar integration, iMessage alerts
**Status:** needs_build

### Rule Q52: Dashboard Revenue Metrics — Pipeline + Fees
**Decision:** Choice B — Dashboard shows pipeline value AND projected fee revenue.
**System impact:** Dashboard calculates: total pipeline value, projected fees at current conversion rates, fee breakdown by entity and deal stage.
**Affected:** Dashboard, `proposals`, `targets`, fee calculation
**Status:** needs_build

### Rule Q57: Budget Alerts — Anomaly-Based
**Decision:** Choice C — Anomaly-based alerts, not just fixed thresholds. Detect unusual spending patterns.
**System impact:** Track spending velocity. Alert when spend rate exceeds historical norm. Detect runaway API calls (like the Exa 6000-call incident).
**Affected:** `cost_log`, cost monitoring agent, alert system
**Status:** needs_build

### Rule Q63: Feedback Propagation — Suggest, Don't Auto-Apply
**Decision:** Choice B — When feedback is given on one company, suggest applying to similar companies but don't auto-apply.
**System impact:** Feedback on Company A generates suggestions: "Apply this to 5 similar companies?" User chooses which. Never silent propagation.
**Affected:** Feedback engine, `feedback_log`, `rule_sets`
**Status:** needs_build

### Rule Q65: Pause Auto-Learning at 30 Rules
**Decision:** Choice B — Pause auto-learning when rule count reaches 30 per category. Require review before adding more.
**System impact:** Rule counter per category. At 30 rules, system pauses auto-rule creation and flags for human review. Prevents rule bloat.
**Affected:** `rule_sets`, learning engine
**Status:** immediate

### Rule Q71: Auto-Approval Trust — Per-Vertical Graduation
**Decision:** Choice B — Auto-approval thresholds graduate independently per vertical. Some verticals earn trust faster.
**System impact:** Track approval rate per vertical. Verticals with high human-agreement rates graduate to auto-approval earlier. Separate counters.
**Affected:** Certification engine, `rule_sets`, per-vertical trust tracking
**Status:** needs_build

### Rule Q73: Review Queue SLA — 24hr + Escalation
**Decision:** Choice B — 24-hour SLA on review queue items. Escalate if overdue.
**System impact:** Review queue items get 24hr clock. Overdue items escalate: iMessage alert, priority bump. Track SLA metrics.
**Affected:** `human_review_queue`, orchestrator, alert system
**Status:** immediate

### Rule Q74: Always Dual-LLM Certification
**Decision:** Choice A — Always use dual-LLM certification. No exceptions, even at scale.
**System impact:** Every certification pass requires two different LLMs to agree. Never skip second LLM for cost/speed reasons. Worth the money.
**Affected:** Certification engine, `cost_log`
**Status:** immediate

### Rule Q76: Review Queue Target — 200/Day
**Decision:** Choice B — Target 200 items per day through the review queue at scale.
**System impact:** Queue processing capacity target: 200 items/day. Orchestrator pacing tuned to this throughput. Alerts if backlog grows beyond 1 day.
**Affected:** Orchestrator, `human_review_queue`
**Status:** immediate

### Rule Q87: Budget Caps — Per-Company Within Entity
**Decision:** Choice B — Budget caps are per-company, rolled up within entity. Not a single entity-wide cap.
**System impact:** `cost_budget` needs per-company granularity. Each company has a budget within its entity. Entity total is sum of company budgets.
**Affected:** `cost_budget`, `cost_log`
**Status:** needs_build

### Rule Q92: Auto-Trust Thresholds — Stake-Based
**Decision:** Choice C — Auto-trust thresholds vary by stake level. Higher-stakes decisions require more human approvals before auto-trust.
**System impact:** Classify decisions by stake level (low/medium/high). Low-stake: fewer approvals needed. High-stake (valuations, client-facing content): many more approvals required.
**Affected:** Certification engine, trust tracking, `rule_sets`
**Status:** needs_build

### Rule Q93: Unknown Situations — Tier by Urgency
**Decision:** Choice C — Unknown situations tiered by urgency. Hot = fast best-guess. Cold = queue for quality.
**System impact:** Listener agent classifies unknown situations by urgency. Hot unknowns: draft immediately, label as new, flag for review. Cold unknowns: queue for quality research.
**Affected:** Listener agent, `situation_library`, `play_templates`
**Status:** immediate

### Rule Q95: Contradictory Signals — Source Hierarchy
**Decision:** Choice B — Resolve contradictions via source hierarchy. Human > Salesfinity transcript > Email > Fireflies > Exa > Estimated.
**System impact:** Define and enforce source hierarchy for conflict resolution. Higher-ranked source wins. Log all contradictions for review.
**Affected:** Research engine, data merge logic, `dossier_provenance`
**Status:** immediate

---

## EASY DECISIONS (42)

### Rule Q2: Human Tags — Classifier Skips
**Decision:** Approved. No auto-reclassification of human-tagged records. Log disagreements. Add `manually_tagged` boolean — classifier skips those.
**System impact:** Add `manually_tagged` boolean to `targets` table. Classification engine checks this flag and skips if true. Log disagreements to `feedback_log`.
**Affected:** `targets`, `lib/classification.py`
**Status:** immediate

### Rule Q5: Confidence Floor 1.5 → Human Review
**Decision:** Approved. Confidence below 1.5 sends to `human_review_queue`. No downstream work proceeds. Current 2.0 LLM fallback is fine.
**System impact:** Pipeline checks entity_confidence. Below 1.5 = route to human_review_queue, halt pipeline. Between 1.5-2.0 = LLM fallback. Above 2.0 = proceed normally.
**Affected:** Pipeline logic, `targets`, `human_review_queue`
**Status:** immediate

### Rule Q7: New Reps — Manual for Now
**Decision:** Approved. Manual person routing table. New name → human_review_queue. Phase 2: auto-suggest.
**System impact:** Use existing person_routing logic. Unknown rep names trigger human_review_queue entry. No auto-detection of new reps yet.
**Affected:** Person routing, `human_review_queue`
**Status:** immediate

### Rule Q9: Multi-Vertical Companies — NC Wins
**Decision:** Overridden. Priority order: Next Chapter > RevsUp > AND Capital.
**System impact:** When company fits multiple entities, assign: NC first, then RU, then AND. Override the original recommendation.
**Affected:** `lib/classification.py`
**Status:** immediate

### Rule Q10: Entity Classification — Internal Only
**Decision:** Approved. Entity classification never shown to clients. Clients see "Next Chapter Advisory" branding only.
**System impact:** Client-facing pages strip entity tags. All branding = "Next Chapter Advisory." Internal admin views show entity tags.
**Affected:** All client-facing templates
**Status:** immediate

### Rule Q11: Human Correction — Store Both Values
**Decision:** Approved. Human always wins. Store both values with sources. Format: "$5M (owner-reported)" + footnote for system estimate.
**System impact:** When human corrects a value, store original + correction with source attribution. Display human value as primary, system value as footnote.
**Affected:** `dossier_final`, `companies`, data correction workflow
**Status:** immediate

### Rule Q13: Field Confidence Indicators
**Decision:** Approved. Three levels: CONFIRMED / ESTIMATED / UNKNOWN. Admin sees labels. Client sees data with footnotes.
**System impact:** Add confidence level tracking per field. Admin UI shows color-coded labels. Client pages show footnotes for estimated/unknown values.
**Affected:** `dossier_final`, `companies`, all page templates
**Status:** immediate

### Rule Q16: Quality 50-79 — Needs Review with Instructions
**Decision:** Overridden. Quality 50-79 sits in needs_review with explicit details of issues and manual research instructions. Make it instructive.
**System impact:** Quality 50-79 profiles route to needs_review with structured guidance: what's missing, where to look, what to research manually. Not just "needs review" — actionable instructions.
**Affected:** `human_review_queue`, certification engine, quality scoring
**Status:** immediate

### Rule Q21: Estimate Accuracy Tracking
**Decision:** Approved. Create `estimate_accuracy` table. Log deltas on human correction. Monthly aggregate.
**System impact:** New table: `estimate_accuracy` with fields for original estimate, corrected value, delta, field name, company, date. Monthly aggregation for accuracy reporting.
**Affected:** New `estimate_accuracy` table, correction workflow
**Status:** immediate

### Rule Q22: LLM Disagreement — Human or Agent Picks Winner
**Decision:** Overridden. Either human picks winner or agent using another LLM picks winner. Long-term: agent. Need way to inject human training without blocking every record.
**System impact:** LLM disagreement → try third LLM as tiebreaker. If still unclear → human_review_queue. Human resolutions become training data. Don't block pipeline on every disagreement.
**Affected:** Certification engine, `verification_pairs`, `human_review_queue`
**Status:** immediate

### Rule Q23: Show Methodology on Every Page
**Decision:** Approved. Methodology IS the brand. Admin: full methodology. Client: lighter version.
**System impact:** Every page template includes methodology section. Two tiers: admin-full and client-light. This is a core brand differentiator.
**Affected:** All page templates
**Status:** immediate

### Rule Q24: No Extra Sensitive Vertical Restrictions
**Decision:** Approved. Existing guardrails sufficient. HIPAA/SEC handled case-by-case.
**System impact:** No new restrictions needed. Existing guardrails cover sensitive verticals. HIPAA/SEC flagged for manual review if detected.
**Affected:** No changes needed
**Status:** immediate

### Rule Q28: Buyer Research Refresh Schedule
**Decision:** Overridden. Signed engagements = weekly refresh. Deal in pipeline = bi-weekly. Unresponded = quarterly.
**System impact:** Add `refresh_schedule` logic to buyer research engine. Frequency based on engagement stage. Track `last_refreshed_at` on engagement_buyers.
**Affected:** `engagement_buyers`, buyer research engine, orchestrator scheduling
**Status:** immediate

### Rule Q34: DNC'd Buyers Visible to Clients
**Decision:** Overridden. DNC buyers shown to clients with reason. Full disclosure.
**System impact:** Client views include DNC'd buyers with reason displayed. No hiding. Builds trust and keeps clients informed.
**Affected:** Client-facing buyer list templates, `engagement_buyers`, `do_not_call`
**Status:** immediate

### Rule Q36: Buyer Fit Scores Visible to Clients
**Decision:** Overridden. Fit scores visible to clients. This is a service to them.
**System impact:** Client pages show fit scores. Not hidden as internal metric. Positions as value-add service.
**Affected:** Client-facing buyer templates, `engagement_buyers`
**Status:** immediate

### Rule Q37: Active Acquirer Flag
**Decision:** Approved. Flag buyers who complete acquisitions as "Active Acquirer." Increases fit score. Move up in rankings.
**System impact:** Add `active_acquirer` boolean to `engagement_buyers`. Acquisition completion boosts fit_score. Active acquirers rank higher.
**Affected:** `engagement_buyers`, fit score calculation
**Status:** immediate

### Rule Q40: Auto-Detect Buyer Acquisitions
**Decision:** Approved. Monthly Exa scan for buyer acquisitions. Log to buyer_activity. Auto-flag + notify.
**System impact:** Monthly scheduled Exa scan across known buyers. New acquisitions logged, buyer flagged as Active Acquirer, team notified.
**Affected:** Buyer research engine, `engagement_buyers`, Exa integration, scheduling
**Status:** needs_build

### Rule Q41: Meeting Prep 24hr Before
**Decision:** Approved. Generate meeting prep 24 hours before. Regenerate if new data arrives. Orchestrator checks calendar daily.
**System impact:** Daily calendar scan. 24hr-out meetings trigger prep generation. New data arrival triggers regeneration. Orchestrator owns this schedule.
**Affected:** Meeting prep engine, orchestrator, calendar integration
**Status:** immediate

### Rule Q42: Meeting Pages Phone-Optimized
**Decision:** Approved. Key points top, collapsible sections, large taps, no horizontal scroll.
**System impact:** Meeting page templates are mobile-first. Key points above fold. Collapsible detail sections. Touch-friendly.
**Affected:** Meeting page templates
**Status:** immediate

### Rule Q43: Joint Meeting Role Assignments
**Decision:** Approved. Ewing: relationship, big picture. Mark: operational, process.
**System impact:** Joint meeting prep pages include role assignments. Ewing's section: relationship points, big picture. Mark's section: operational details, process.
**Affected:** Meeting page templates
**Status:** immediate

### Rule Q44: Reschedule → Regenerate Prep
**Decision:** Approved. Reschedule triggers regeneration. New data may exist. Keep old version in page_versions.
**System impact:** Calendar reschedule event triggers meeting prep regeneration. Old prep preserved as version. New prep uses latest data.
**Affected:** Meeting prep engine, `page_versions`, calendar integration
**Status:** immediate

### Rule Q45: iMessage Prep 30 Minutes Before
**Decision:** Overridden. Send iMessage 30 min before meeting. Format: "Meeting with {company} in 30 min. Key: {5 bullets}. Full: {link}."
**System impact:** 30-minute pre-meeting iMessage trigger. Summary format with 5 key bullets and link to full prep. Uses iMessage bridge.
**Affected:** Meeting prep engine, iMessage bridge, scheduling
**Status:** immediate

### Rule Q48: Meeting Type — Needs Architecture Review
**Decision:** Overridden. Needs further review. This is meeting page architecture. Flag in TODO.
**System impact:** Meeting type enum vs free text decision deferred. Need to design meeting page template architecture first.
**Affected:** Meeting pages (deferred)
**Status:** needs_discussion

### Rule Q50: Meeting Pages — Competitive Intel
**Decision:** Approved. Include if available: who else is talking to prospect, brokers in market, prior M&A.
**System impact:** Meeting prep includes competitive intelligence section. Populated when data available. Sources: Exa, deal_research, public listings.
**Affected:** Meeting prep templates, research engine
**Status:** immediate

### Rule Q51: Dashboard as Landing Page
**Decision:** Approved. Dashboard is the home page. Pipeline, reviews, problems, budget, quick links. Companies move to sidebar.
**System impact:** Root URL serves dashboard. Company list moves from main content to sidebar navigation. Dashboard sections: pipeline, review queue, problems, budget, quick links.
**Affected:** Web server routing, dashboard template, navigation
**Status:** immediate

### Rule Q53: Dashboard System Health
**Decision:** Approved. Show orchestrator/worker/watchdog status. Green/yellow/red. Red if worker down > 15 minutes.
**System impact:** System health widget on dashboard. Poll `tool_health` table. Color coding: green = healthy, yellow = degraded, red = down >15min.
**Affected:** Dashboard, `tool_health`
**Status:** immediate

### Rule Q54: Mobile Dashboard
**Decision:** Approved. Monday morning from bed. Responsive design. Key metrics top. Collapsible sections.
**System impact:** Dashboard is responsive/mobile-first. Priority metrics above fold. Detail sections collapsible.
**Affected:** Dashboard template, CSS
**Status:** immediate

### Rule Q56: Dashboard Entity Filters
**Decision:** Approved. Filter buttons: [All] [NC] [AND] [RU] + person presets. Cookie-stored preference.
**System impact:** Dashboard filter bar with entity toggles. Person presets (e.g., "Ewing's view"). Last selection stored in cookie.
**Affected:** Dashboard template, cookie storage
**Status:** needs_build

### Rule Q58: "While You Were Away" Summary
**Decision:** Approved. Show changes since last login. Track last_viewed_at.
**System impact:** Track `last_viewed_at` per user. On login, show summary of changes since that timestamp. Covers: new leads, status changes, feedback received, problems detected.
**Affected:** Dashboard, user session tracking (new field or table)
**Status:** immediate

### Rule Q59: Dashboard Auto-Refresh Every 5 Minutes
**Decision:** Approved. Live data on page load. Fresh queries. Auto-refresh meta tag every 5 minutes.
**System impact:** Dashboard queries live data on every load. HTML meta refresh tag every 5 minutes. No stale cached data.
**Affected:** Dashboard template
**Status:** immediate

### Rule Q60: System Confidence Metric
**Decision:** Approved. Show "Data Quality: 72% confirmed, 18% estimated, 10% unknown."
**System impact:** Aggregate confidence levels across all fields. Display breakdown on dashboard. Per-company and system-wide metrics.
**Affected:** Dashboard, confidence calculation across `dossier_final`
**Status:** needs_build

### Rule Q64: Guardrails Always Win Over Feedback
**Decision:** Overridden. Guardrails always win. Only Ewing overrides by updating North Star. Log when system wants to break guardrails. Weekly review. Publish hourly. Put on dashboard as feed/section.
**System impact:** Guardrail violation attempts logged with context. Dashboard feed showing hourly guardrail pressure. Weekly review digest. Only Ewing can update North Star to change guardrails.
**Affected:** `rule_sets`, dashboard, guardrail engine, logging
**Status:** immediate

### Rule Q66: Version History — Last 10 Per Page
**Decision:** Approved. Last 10 versions per page in UI. Older versions move to archive table (queryable but not in UI).
**System impact:** UI shows max 10 versions. Version 11+ archived. Archive table queryable via admin. No data deletion.
**Affected:** `page_versions`, new archive mechanism
**Status:** immediate

### Rule Q67: Every Edit = New Version, But Ask Before Regenerating
**Decision:** Overridden. Every edit creates a new version. Pre-edit preserved. But ASK user before regenerating — they may have other edits pending on the same page.
**System impact:** Auto-version on every edit. Regeneration requires user confirmation ("Regenerate this page? You have unsaved edits."). Never silently overwrite user work.
**Affected:** `page_versions`, page editing workflow
**Status:** immediate

### Rule Q68: Version History — Not Visible to Clients
**Decision:** Approved. Clients see current version only. Revisions signal uncertainty.
**System impact:** Client views always show latest version. No version history UI for clients. Internal only.
**Affected:** Client-facing templates
**Status:** immediate

### Rule Q69: Rule Change Rebuild — Lazy + Background for Active
**Decision:** Approved. Lazy rebuild: mark stale, rebuild on view. Active engagements: background rebuild within 1 hour.
**System impact:** Rule changes mark affected pages as `is_stale=true`. Viewed pages rebuild on demand. Active engagement pages get background rebuild within 1hr via orchestrator.
**Affected:** `page_versions`, orchestrator, stale page logic
**Status:** immediate

### Rule Q70: Version-Level Commenting
**Decision:** Approved. One optional text field: "Why was this changed?"
**System impact:** `page_versions` already has `change_summary` field. Ensure it's exposed in UI as "Why was this changed?" prompt.
**Affected:** `page_versions`, editing UI
**Status:** immediate

### Rule Q72: Mark Override — Certifier Defers
**Decision:** Approved. Mark wins over certifier. Reverts to needs_review. 3 overrides of same type → auto-generate rule proposal for certifier improvement.
**System impact:** Mark's feedback overrides certifier approval. Track override count by pattern. At 3 similar overrides, system proposes new certifier rule.
**Affected:** Certification engine, `feedback_log`, `rule_sets`
**Status:** immediate

### Rule Q75: Pre-Certification Quick Check
**Decision:** Approved. 5-point code check before LLM certification. Fail = skip cert, route to human.
**System impact:** Programmatic pre-check before expensive LLM certification: completeness, formatting, required fields, data freshness, dedup. Failures skip LLM and go straight to human.
**Affected:** Certification engine
**Status:** immediate

### Rule Q77: Orchestrator Priority — Urgency First
**Decision:** Approved. Urgency first, entity second. Round-robin within urgency tiers.
**System impact:** Queue ordering: urgency tier → entity round-robin within tier. Hot items always process before warm, regardless of entity.
**Affected:** Orchestrator, `agent_queue`
**Status:** immediate

### Rule Q78: Orchestrator Recovery — Pace at 2x, No Burst
**Decision:** Approved. After downtime, pace at 2x normal rate. No bursting. Catch-up flag when backlog > 20.
**System impact:** Orchestrator recovery mode: 2x processing rate. Never burst (prevents API hammering). Catch-up flag visible on dashboard when backlog > 20.
**Affected:** Orchestrator
**Status:** immediate

### Rule Q79: Maintenance Mode
**Decision:** Approved. Three states: active / maintenance / paused. Maintenance: orchestrator stops, workers finish current tasks, watchdog continues.
**System impact:** System state enum: active, maintenance, paused. Maintenance mode: graceful worker completion, no new work dispatched, watchdog monitors.
**Affected:** Orchestrator, system state management
**Status:** immediate

### Rule Q80: 5min Orchestrator / 10sec Worker — Confirmed
**Decision:** Approved. No changes to timing.
**System impact:** None. Current intervals confirmed correct.
**Affected:** None
**Status:** immediate

### Rule Q83: Keep Static HTML Alongside Server
**Decision:** Approved. Static HTML as offline backup, email attachments, PDF generation. Server is primary, files are backup.
**System impact:** Continue generating static HTML files. Server serves dynamic pages as primary. Static files for: offline access, email attachments, PDF generation.
**Affected:** Page generation pipeline
**Status:** immediate

### Rule Q84: Multi-User Support — Flask/FastAPI
**Decision:** Approved. Flask or FastAPI with multi-threading. Writes go through queue.
**System impact:** Web server handles concurrent users. Write operations queued to prevent conflicts. Read operations concurrent.
**Affected:** Web server architecture
**Status:** needs_build

### Rule Q85: No WebSockets
**Decision:** Approved. Page refresh + auto-refresh every 5 minutes. No WebSockets needed.
**System impact:** No WebSocket implementation. HTTP polling via page refresh. Auto-refresh meta tag at 5-minute intervals.
**Affected:** Web server
**Status:** immediate

### Rule Q88: Budget Exhausted — Queue for Tomorrow
**Decision:** Approved. Queue work for tomorrow with `deferred_until` timestamp. No work lost.
**System impact:** When budget ceiling hit, new work gets `deferred_until = tomorrow`. Work queued, not skipped. Resumes when budget resets.
**Affected:** Orchestrator, `agent_queue`
**Status:** immediate

### Rule Q89: API Key Expiration Alerts
**Decision:** Approved. Weekly health check on all API keys. 401/403 responses trigger iMessage alert.
**System impact:** Weekly scheduled check of all API keys. Any auth failure → immediate iMessage alert to Ewing. Proactive, not reactive.
**Affected:** `tool_health`, `tool_incidents`, alert system
**Status:** immediate

### Rule Q90: Deployment — Manual Git Pull
**Decision:** Approved. Manual git pull for now. Phase 2: deploy script. Phase 3: webhook. No CI/CD yet.
**System impact:** Current deployment: manual `git pull` on server. Future phases planned but not now.
**Affected:** Deployment process (no code changes)
**Status:** immediate

### Rule Q94: No Historical Listener Scan on Deploy
**Decision:** Approved. Start fresh on deploy. Historical data would flood with stale plays.
**System impact:** Listener agent starts from current timestamp on deployment. No backfill of historical data.
**Affected:** Listener agent
**Status:** immediate

### Rule Q97: Show Failed Research Internally
**Decision:** Approved. Admin sees failed research attempts. Client sees only successful results.
**System impact:** Research failures logged and visible in admin UI. Client pages only show confirmed data. Failed attempts = useful debugging info.
**Affected:** Admin templates, `research_executions`
**Status:** immediate

### Rule Q98: Research Cost Hidden from Clients
**Decision:** Approved. "$0.15" kills premium positioning. Internal metric only.
**System impact:** Cost data never appears on client-facing pages. Internal admin sees per-company research costs. Cost is an internal optimization metric.
**Affected:** Client-facing templates, `cost_log`
**Status:** immediate

---

*End of rules. 97 decisions processed.*
