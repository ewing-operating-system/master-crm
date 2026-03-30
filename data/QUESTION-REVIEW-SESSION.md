# MASTER CRM — 100 QUESTIONS REVIEW SESSION

**Generated:** 2026-03-29
**Format:** Three tiers — Easy (answer provided), Nuanced (3 options), Hard (questions for Ewing)

---

## TIER 1: EASY ANSWERS (52 questions)
Obvious choice. Written answer provided. Ewing reviews and approves or overrides.

---

### Q2. Should the classifier ever auto-reclassify a record that a human manually tagged?
**Answer:** No. Human always wins. If the classifier would disagree, log the disagreement to `classification_corrections` table for monthly review, but never overwrite a human tag. Add a `manually_tagged` boolean to targets — classifier skips those rows entirely.

### Q5. Is there a classification confidence floor below which the pipeline should STOP?
**Answer:** Yes. Floor = 1.5. Below 1.5, the record enters `human_review_queue` with type `classification_uncertain`. No downstream work (research, proposals, engagement) proceeds until a human tags it. Current threshold of 2.0 for LLM fallback is fine — the 1.5 floor catches records where even the LLM fallback was low confidence.

### Q7. For person routing, should new reps be auto-detected or manually configured?
**Answer:** Manually configured for now. Add a `person_routing` Supabase table. When a new name appears in call logs that isn't in the routing table, create a `human_review_queue` item: "New person detected: {name}. Assign entity routing." Phase 2: auto-suggest routing based on which campaigns they appear in.

### Q9. How should the system handle companies that operate in multiple verticals?
**Answer:** Primary vertical wins. Every company gets ONE `primary_vertical` field (the vertical that drives the most revenue or is the reason NC is pursuing them). Add `secondary_verticals` as a text array for context. Classification, proposals, and multiples all key off `primary_vertical`. The profile can mention secondary verticals, but the system routes on primary.

### Q10. Should entity classification be visible to the client?
**Answer:** No. Internal only. Clients see "Next Chapter Advisory" branding, not "entity: next_chapter." The entity system is operational infrastructure, not client-facing.

### Q11. When Mark says "revenue is $5M" but Exa says $2.25M, which wins?
**Answer:** Human input always wins for the stored value. But flag the discrepancy: store both values in the profile with source attribution. Profile shows: "Revenue: $5M (owner-reported)" with a footnote: "Web estimate: $2.25M — variance may indicate unreported revenue streams or estimation error." Mark sees the flag; client sees only the owner-reported number.

### Q13. Should each field show a confidence indicator?
**Answer:** Yes. Three levels: CONFIRMED (human-stated or verified source), ESTIMATED (LLM-derived from available data), UNKNOWN (no data). Show these in admin view. Client view shows confirmed and estimated without the labels — just present the data naturally with methodology footnotes.

### Q16. When quality_score is 50-79, should proposals go to clients?
**Answer:** Never. Quality < 80 = draft only. The proposal sits in `needs_review` status until either: (a) the certifier upgrades it on re-run with better data, or (b) a human manually reviews and approves. No client-facing page, no engagement activation, no buyer scripts generated from sub-80 proposals.

### Q21. Should the system track how often its estimates were wrong?
**Answer:** Yes. Create an `estimate_accuracy` table: company_name, field_name, estimated_value, actual_value, variance_pct, discovered_at. When a human corrects an estimated field, log the delta. Monthly: aggregate by field type to identify systematic biases (e.g., "employee count estimates average 30% high").

### Q22. When two LLMs disagree on a fact, what happens?
**Answer:** Route to human review. Store both values with their sources in `verification_pairs`. The human_review_queue item shows: "LLM A says X, LLM B says Y. Which is correct?" Human picks one, and the losing answer is logged for prompt improvement.

### Q23. Should the system show estimate methodology on every page?
**Answer:** Yes. This IS the brand. "All about them" means showing your work. Every estimated field gets a small methodology note: "Estimated from employee count × industry average revenue per employee." Admin view shows full methodology. Client view shows a lighter version: "Based on market analysis and public data."

### Q24. For sensitive verticals (medical, energy), are there additional personalization restrictions?
**Answer:** No special restrictions beyond existing guardrails. The "never include negative facts" and "all about them" rules are sufficient. Medical and energy companies get the same treatment. If a specific compliance issue arises (HIPAA for medical, SEC for energy), handle it case-by-case rather than building preemptive restrictions.

### Q28. Should buyer research be refreshed periodically?
**Answer:** Yes. Quarterly. Add `buyer_research_date` to proposals. If > 90 days old, flag as stale on the company hub. Orchestrator can queue a refresh. For active engagements (client has signed), refresh monthly.

### Q34. Should DNC'd buyers appear in the client-facing view?
**Answer:** No. Hide completely from client view. Admin view shows them greyed out with the reason. The client should never see a buyer they can't reach — it undermines confidence. If the client independently knows the buyer, they can contact them on their own.

### Q36. Should buyer fit scores be visible to clients?
**Answer:** No. Scores are internal prioritization tools. Clients see buyers ranked by fit (order implies priority) but not the numerical score. A client seeing "fit_score: 45" for a buyer they personally know is a great fit would question the system's judgment.

### Q37. When a buyer completes an acquisition, should they be flagged?
**Answer:** Yes. Flag as "Active Acquirer — completed acquisition in {vertical} on {date}." This INCREASES their fit score. A buyer who just closed a deal often has remaining capital, an operational playbook, and appetite for add-ons. Move them UP the list, not off it.

### Q40. Should the system auto-detect buyer acquisitions?
**Answer:** Yes. Monthly Exa scan for each buyer company + "acquisition" or "acquired." Log to `buyer_activity` table. If a buyer in our lists completed an acquisition, auto-flag and notify via dashboard.

### Q41. How far in advance should meeting prep be generated?
**Answer:** 24 hours before the meeting. If new data arrives between generation and the meeting, regenerate automatically. The Listener (when built) handles this. For now, orchestrator checks Calendar daily and generates prep for tomorrow's meetings.

### Q42. Should meeting pages be phone-optimized?
**Answer:** Yes. Key talking points at the top, collapsible sections, large tap targets, no horizontal scroll. Mark uses his phone during calls. The meeting page is a cheat sheet, not a report.

### Q43. For joint meetings, should prep include role assignments?
**Answer:** Yes. Add a `meeting_roles` section: "Ewing: relationship, big picture, valuation discussion. Mark: operational details, timeline, process questions." Based on the person routing + meeting type.

### Q44. If a meeting is rescheduled, should prep regenerate?
**Answer:** Yes. New data may have arrived since original generation. Regenerate on reschedule. Keep the old version in page_versions for comparison.

### Q45. Should meeting prep be sent via iMessage 30 minutes before?
**Answer:** Yes. Send a summary (not the full page) via iMessage: "Meeting with {company} in 30 min. Key points: {3 bullets}. Full prep: {link}." This is exactly the kind of proactive automation that justifies building the system.

### Q48. Meeting type: strict enum or free text?
**Answer:** Strict enum. Valid types: `discovery`, `qualification`, `proposal_review`, `closing`, `follow_up`, `check_in`, `data_room_walkthrough`. Each type has a specific prompt template. Unknown types get rejected with a clear error listing valid options.

### Q50. Should meeting pages include competitive intelligence?
**Answer:** Yes, if available. Add a "Competitive Context" section: who else might be talking to this prospect, which brokers/advisors are in the market, any prior M&A attempts. Source from Exa + deal_research table. Mark should never be surprised in a meeting.

### Q51. Should the dashboard be the landing page?
**Answer:** Yes. The dashboard is the command center. Company cards move to a sidebar or a secondary /companies route. When Ewing opens localhost:8080, he sees: pipeline status, pending reviews, problems, budget, and quick links to each company.

### Q53. Should the dashboard show system health?
**Answer:** Yes. Add a "System Status" section: orchestrator (last run, items queued), worker (last claim, items processed today), watchdog (last check). Green/yellow/red status badges. If the worker has been down for > 15 minutes, show a red alert.

### Q54. Is a mobile dashboard needed?
**Answer:** Yes. The Monday morning check happens from bed with a phone. Responsive design, key metrics at the top, collapsible sections. Same data, optimized layout.

### Q56. Should the dashboard have entity filters?
**Answer:** Yes. Filter buttons: [All] [NC] [AND] [RU]. Plus person presets: "Ewing's View" (NC + AND), "Mark's View" (all), "John's View" (NC + RU). Store preference in a cookie.

### Q58. Should the dashboard have a "while you were away" summary?
**Answer:** Yes. Show changes since last login: "Since Friday 5pm: 3 proposals certified, 1 new review item, 2 buyer scripts generated, $1.24 spent." Track last_viewed_at per user (when auth exists).

### Q59. Dashboard refresh frequency?
**Answer:** Live on every page load. No static HTML generation for the dashboard. Server.py queries the database and renders fresh data on each request. Add a small "Last loaded: {timestamp}" note. Optional: auto-refresh meta tag every 5 minutes if the page is left open.

### Q60. Should the dashboard show a "system confidence" metric?
**Answer:** Yes. Show: "Pipeline Data Quality: 72% confirmed, 18% estimated, 10% unknown." Calculated from the confidence indicators on all active company profiles. This tells Ewing at a glance how much of the system's knowledge is solid vs. guesswork.

### Q64. When feedback contradicts the guardrails, who wins?
**Answer:** Guardrails win. Always. The guardrails are the North Star. If Mark says "include this negative fact," the system says: "Guardrail conflict: 'Never include negative facts about the owner.' This correction has been logged. Escalating to Ewing for guardrail override decision." Only Ewing can override a guardrail, and it requires updating the North Star document.

### Q66. How far back should version history go?
**Answer:** Last 10 versions per page per company. Older versions archived to a `page_versions_archive` table (queryable but not in the UI). This keeps the version dropdown manageable while preserving full history.

### Q67. When Mark edits a section, should that auto-create a version?
**Answer:** Yes. Every edit = new version. The pre-edit state is preserved automatically. No explicit "save version" button needed. This is cheap storage and invaluable audit trail.

### Q68. Should version history be visible to clients?
**Answer:** No. Clients see only the current version. Version history is admin-only. Showing 7 revisions signals uncertainty, not thoroughness. The client should feel like the deliverable is polished and final.

### Q69. If a rule change affects 20 pages, rebuild immediately or lazy?
**Answer:** Lazy rebuild. Mark all affected pages as `is_stale = true`. Rebuild when viewed. For actively-engaged clients (status = engagement_active), rebuild proactively in the background within 1 hour. For draft/certified proposals, lazy is fine.

### Q70. Is there value in version-level commenting?
**Answer:** Yes, but keep it simple. One text field per version: "Why was this changed?" Optional, not required. Useful for audit trail: "Updated after Mark's call — owner confirmed 15 employees, not 11."

### Q72. If certifier says APPROVED but Mark disagrees, what happens?
**Answer:** Mark wins. The proposal reverts to `needs_review`. The certifier's approval is logged as overridden. After 3 overrides of the same type (e.g., Mark always rejects valuations the certifier approved), create a rule proposal: "Certifier may need updated valuation criteria."

### Q75. Should there be a pre-certification quick check?
**Answer:** Yes. Before expensive LLM certification, run a 5-point checklist (code, not LLM): (1) No empty required sections, (2) Company name matches across all sections, (3) Entity tag present, (4) Valuation range exists and is reasonable ($100K-$500M), (5) deal_side matches proposal direction. Fail any = skip certification, route directly to human review. Saves LLM cost on obviously broken proposals.

### Q77. Should the orchestrator prioritize by entity or urgency?
**Answer:** Urgency first, entity second. Priority order: (1) Hot leads (buyer responded, prospect said "send me info"), (2) Active engagements needing scripts, (3) New classifications, (4) Research for pipeline targets, (5) Stale data refresh. Within the same urgency tier, round-robin across entities to prevent starvation.

### Q78. If orchestrator is down for 4 hours, process backlog immediately?
**Answer:** Pace, don't burst. Process at 2x normal speed until caught up, then return to normal. Bursting risks API rate limits and creates a flood of notifications. Add a "catch-up mode" flag that the orchestrator sets when backlog > 20 items.

### Q79. Should there be a maintenance mode?
**Answer:** Yes. Add a `system_mode` entry in a config table: `active`, `maintenance`, `paused`. Maintenance mode: orchestrator stops queuing, worker finishes current items then idles, watchdog stays running. Toggled via web server API endpoint or database update.

### Q80. Is the 5-minute orchestrator / 10-second worker balance correct?
**Answer:** Yes. The orchestrator scans for new work every 5 minutes — that's fine because new targets don't appear every second. The worker polls every 10 seconds for claimed items — that's responsive enough for processing speed. No change needed.

### Q83. Should static HTML files continue alongside the server?
**Answer:** Yes. Keep generating HTML files as offline backups and export artifacts. They're useful for: email attachments, PDF generation, viewing when the server is down, sending to people without server access. Server is primary; files are backup.

### Q84. How should multiple simultaneous users be handled?
**Answer:** Switch to Flask or FastAPI (already recommended). Multi-threading handles concurrent requests. No user-level locking needed — the data is read-mostly, and writes go through the queue system, not the web server.

### Q85. Does the server need WebSockets?
**Answer:** No. Not for v1. Page refresh is sufficient. The data changes infrequently (proposals update a few times per day, not per second). Auto-refresh meta tag every 5 minutes covers the "live feel" need. WebSockets add complexity for minimal benefit at current scale.

### Q88. When budget is exhausted, should work queue for tomorrow or be skipped?
**Answer:** Queue for tomorrow. Add `deferred_until` timestamp to agent_queue items. When budget is exhausted, new items get `deferred_until = tomorrow_midnight`. Orchestrator skips deferred items until the date arrives. No work is ever silently lost.

### Q89. Should the system detect and alert on API key expiration?
**Answer:** Yes. Add a weekly health check: test each API key with a minimal call (Exa: 1-result search, OpenRouter: tiny prompt). If any key returns 401/403, iMessage alert: "[Argus] API key failing: {provider}. Needs rotation." Log to a `system_health` table.

### Q90. What is the deployment process?
**Answer:** Manual git pull for now. Process: (1) SSH to Mac mini, (2) `cd ~/Projects/master-crm && git pull`, (3) restart orchestrator + worker + server. Phase 2: add a simple deploy script that does all 3 steps. Phase 3: GitHub webhook triggers auto-deploy. No CI/CD needed at current scale.

### Q94. Should the Listener scan historical data when first deployed?
**Answer:** No. Start fresh. Scanning 30 days of transcripts creates a flood of stale plays that overwhelm the review queue. The Listener starts scanning from deployment time forward. Any missed historical opportunities were already missed — creating stale follow-ups for them would be worse than doing nothing.

### Q97. Should failed research be shown?
**Answer:** Yes internally, no externally. Admin view shows: "Glassdoor search: no results. BBB search: no listing. Google Reviews: 4.2 stars (found)." This shows Mark what was tried. Client view only shows successful research — failed searches look like incompetence, not thoroughness.

### Q98. Should per-company research cost be visible to clients?
**Answer:** No. "$0.15 researching your company" sounds cheap and undermines the premium positioning. Clients should feel like significant effort went into their research. The cost is an internal efficiency metric, not a client-facing feature.

---

## TIER 2: NUANCED QUESTIONS (32 questions)
Need more context. Three suggestions provided. Pick one or tell me your thinking.

---

### Q3. For multi-entity people (Mark spans all 3), classify by CAMPAIGN or CONTENT?

**Option A — Campaign wins:** If the record came from an NC campaign, it's NC regardless of content. Simple, deterministic, fast. Risk: Mark making an AND Capital call during NC campaign time gets misclassified.

**Option B — Content wins:** Analyze the actual content of the interaction. "Talking about LP fundraising" = AND Capital, even if Mark was logged into an NC campaign. More accurate, more complex, requires LLM analysis of every interaction.

**Option C — Hybrid (recommended):** Campaign is the default classification. But if content analysis produces a DIFFERENT entity with confidence > 3.0, flag for human review: "This record came from NC-SELL-CALL but content suggests AND Capital. Correct?" Over time, these flags train the system.

### Q4. How should entity transitions work (NC deal becomes AND investment)?

**Option A — Fork the record:** Create a new record in the new entity. Link them via a `related_records` table. Both records maintain independent pipeline status. Clean separation, some data duplication.

**Option B — Re-tag with history:** Change the entity on the existing record. Log the transition in `entity_transitions` table with old_entity, new_entity, reason, date. Simple, but downstream engines need to handle the transition (old proposals are NC, new work is AND).

**Option C — Dual-tag (recommended):** Add `secondary_entity` field. Primary entity drives pipeline work. Secondary entity is informational. When the secondary becomes primary (deal signed with AND Capital), swap them. The company hub shows both entity histories.

### Q6. "Start with smallest entity" vs urgency?

**Option A — Smallest always first:** NC before AND before RU, regardless of urgency. This ensures the smallest revenue opportunity still gets attention. Consistent with the guardrails.

**Option B — Urgency always first:** Hot leads first regardless of entity. A prospect saying "send me info" on an AND Capital call jumps the queue over a cold NC research task. Maximizes revenue capture.

**Option C — Urgency with entity floor (recommended):** Each entity gets a minimum daily allocation (NC: 60%, AND: 30%, RU: 10% of queue capacity). Within each allocation, prioritize by urgency. This prevents urgency from starving any entity while still responding to hot leads fast.

### Q8. Should the DNC list include "soft DNC"?

**Option A — Binary DNC only:** Blocked = blocked everywhere, all channels, forever. Simple, safe, no ambiguity. If someone says "stop calling," they're dead to all outreach.

**Option B — Soft DNC with channel control:** Add `blocked_channels` array to do_not_call: ["phone", "email", "linkedin"]. A company can be DNC for phone but still receive email. More flexible, more complex, more risk of error.

**Option C — Binary DNC + inbound exception (recommended):** DNC blocks all OUTBOUND contact. But if the person reaches out TO US (inbound email, inbound call), we can respond. Add an `allow_inbound` boolean (default true). This is legally safe and operationally practical.

### Q12. How often should profiles be regenerated?

**Option A — On new data:** Regenerate whenever a new data source is added (call transcript, Exa research, manual input). Most accurate, most expensive. Could trigger 5+ regenerations per company per week.

**Option B — Weekly batch:** Every Monday, regenerate all profiles for active companies. Predictable, efficient, but profiles can be up to 7 days stale.

**Option C — Trigger-based with cooldown (recommended):** Regenerate when new data arrives, but with a 24-hour cooldown. If a profile was regenerated today, queue the next regeneration for tomorrow even if more data comes in tonight. This prevents churn while staying reasonably current.

### Q14. Minimum data completeness threshold for a "ready" profile?

**Option A — 50% (low bar):** At least half the fields populated. Lets profiles enter the pipeline early, but downstream engines may produce weak outputs.

**Option B — 70% (recommended):** At least 70% of core fields (company_name, vertical, city, state, estimated_revenue, employee_count, owner_name — 5 of 7 required). This ensures proposals have enough to work with.

**Option C — Adaptive by stage:** Discovery meeting prep needs only 40%. Proposal generation needs 70%. Engagement activation needs 85%. Different thresholds for different pipeline stages.

### Q17. If estimated valuation is dramatically wrong, deal-killer or conversation-starter?

**Option A — Conversation-starter:** Show the range. If the owner says "that's way too low," the response is "tell us more — what are we missing?" The valuation opens the dialogue, not closes it.

**Option B — Omit until confirmed:** Don't show valuation until Mark has spoken to the owner and validated key inputs. Avoids the "you're wrong" reaction entirely.

**Option C — Range with framing (recommended):** Show the range with explicit framing: "Based on public market data, businesses in your vertical typically transact at $X-$Y. Your specific circumstances may differ significantly. Let's explore what makes your situation unique." This is educational, not prescriptive.

### Q18. Should multiples vary by geography, company size, and recency?

**Option A — Static per vertical:** One EBITDA range per vertical. Simple. Matches current implementation. Risk: wrong for specific situations.

**Option B — Full segmentation:** Vertical × geography × company size × transaction recency. Most accurate, requires significant data investment to build and maintain.

**Option C — Vertical + size tier (recommended):** Multiples vary by vertical AND revenue tier ($1-3M, $3-10M, $10-25M). Geography matters less than size for home services. Recency: only use transactions from last 3 years. This adds meaningful precision without excessive complexity.

### Q20. When estimating revenue from employee count, what margin of error is acceptable?

**Option A — Any estimate is better than none:** Show the estimate with a wide range (±50%). "Estimated revenue: $1.5M-$4.5M based on ~15 employees."

**Option B — Only estimate with corroborating data (recommended):** Employee count alone = UNKNOWN. Employee count + vertical average + geographic adjustment = LOW confidence estimate with ±40% range. Employee count + vertical + known services + Exa financial signals = MEDIUM confidence with ±25% range.

**Option C — Never estimate revenue:** Only show revenue if owner-stated or from a verified source. Mark blank fields as "Revenue: To be discussed." Most conservative, least useful.

### Q25. How should the system handle owner-operators (owner = only employee)?

**Option A — Flag as high owner-dependency risk:** The profile prominently notes "Owner-operator: extremely high owner dependency. Key risk for any buyer." Valuation adjusted downward. Buyer scripts emphasize transition planning.

**Option B — Treat normally (recommended):** Process through the same pipeline. The profile engine naturally captures owner dependency signals. The EBITDA lever engine (when built) handles the valuation impact. No special-case code needed — the existing "owner dependency" lever covers this.

**Option C — Separate track:** Owner-operators get a different proposal template focused on "business in a box" positioning rather than "growing enterprise" positioning. More work to build, but more tailored output.

### Q26. How many buyers per deal is "enough"?

**Option A — 10 detailed + unlimited list:** Match the overnight decision tree. Top 10 get full scripts and outreach. Remaining buyers are listed but not actively worked.

**Option B — 20 detailed (recommended):** Top 20 get full profiles and scripts. Research shows you need 15-20 qualified buyer conversations to find 2-3 serious offers. 10 is too few after DNC filtering and non-responses remove half.

**Option C — Adaptive by vertical:** Fragmented verticals (HVAC, plumbing) have more potential buyers — target 25. Concentrated verticals (water treatment, precast) have fewer — target 15.

### Q29/Q31. Multi-deal buyers: coordinated or independent outreach?

**Option A — Independent:** Each deal's buyer outreach is standalone. Simple. But the same buyer gets 3 separate cold calls from the same firm, which looks disorganized.

**Option B — Coordinated (recommended):** When a buyer appears on 2+ lists, create a unified outreach: "We're representing multiple opportunities in your space." The pitch is stronger, the contact is more efficient, and it positions NC as a market maker, not a one-deal shop. Flag multi-deal buyers in a `buyer_overlap` view.

**Option C — Sequential:** Work the highest-priority deal first. If the buyer passes, present the next deal. If they pass again, move on. No simultaneous pitches.

### Q30. When a buyer explicitly declines, remove from ALL lists?

**Option A — Remove from all:** One "no" = dead everywhere. Safest. But a buyer who passes on an HVAC deal might love a plumbing deal.

**Option B — Remove from that deal only (recommended):** Mark as declined for the specific deal. Keep on other deal lists. But add a note: "Declined {company_name} on {date}. Reason: {reason}." If the reason is "not acquiring" or "not in market," remove from all lists. If the reason is "wrong size" or "wrong geography," they stay on other lists.

**Option C — Soft decline with cooldown:** Mark as declined, wait 90 days before re-presenting ANY opportunity. Gives the buyer a break while preserving future optionality.

### Q35. When a buyer responds positively, what triggers the next stage?

**Option A — Manual status update:** Mark updates buyer status to "responded_positive" in the web server UI. This triggers next-stage automation (schedule follow-up, send additional materials, update deal timeline).

**Option B — Email detection (recommended):** Listener (when built) scans for buyer replies. Positive sentiment = auto-update status + draft next-stage deliverables for Mark's review. Manual update as fallback until Listener exists.

**Option C — Multi-signal:** Require 2+ signals before advancing (email reply + calendar invite, or email reply + Mark's manual confirmation). Prevents false positives.

### Q46. During live calls, what data should be pushed to the rep's screen?

**Option A — Full meeting page:** The entire prep page is available during the call. Rep scrolls to relevant sections.

**Option B — Smart card (recommended):** A compact "call card" with: company name, owner name, key metric (revenue/employees), top 3 talking points, top 3 questions to ask, and a one-line "danger zone" warning. Everything else is one tap away but not cluttering the screen.

**Option C — Nothing proactive:** Rep opens the meeting page before the call. No live push during the call. Simpler, but misses the real-time assistance opportunity.

### Q47. How should post-meeting outcomes be captured?

**Option A — Manual form:** Mark clicks a button on the meeting page: "How did it go?" Options: Positive (next steps), Negative (closed-lost), Follow-up needed, Rescheduled. Required field: one-line note.

**Option B — Transcript analysis (recommended):** Fireflies transcript is auto-analyzed for outcome signals. LLM extracts: outcome, next steps, action items, key quotes. Draft outcome is presented to Mark for confirmation. Manual form as fallback when no transcript exists.

**Option C — Slack-based:** Mark posts in Slack: "#air-control call done, positive, wants data room." Listener parses the message and updates the pipeline.

### Q49. Back-to-back meetings with different companies?

**Option A — Pre-generated all:** Generate all meeting pages the night before. Mark reviews them sequentially before each call.

**Option B — Context-switch alerts (recommended):** When the next meeting is within 30 minutes, push an iMessage: "Next up: {company_name}. Key difference from last call: {one line}." This prevents bleed-over (accidentally referencing the wrong company's data).

**Option C — Combined prep sheet:** One page showing side-by-side comparison of today's meetings. Useful if 3+ meetings in a day.

### Q52. What "revenue metrics" should the dashboard track?

**Option A — Pipeline only:** Proposal stages (draft → certified → active → signed). Count and movement between stages. No dollar values.

**Option B — Pipeline + fees (recommended):** Pipeline stages PLUS: advisory agreements signed (count + total fee value), active engagements (estimated deal sizes), and closed deals (actual fees collected). This shows Ewing if the business is making money, not just processing data.

**Option C — Full P&L view:** Pipeline + fees + system costs + net margin. Shows the business economics of the CRM itself.

### Q57. At what budget threshold should iMessage alerts fire?

**Option A — 80% of daily budget:** Alert when any entity hits 80%. Gives time to decide whether to pause or increase the cap.

**Option B — Dollar amount (recommended):** Alert on any single API call > $0.50 AND when daily total exceeds $8 across all entities. The percentage-based approach is noisy when caps are low ($3 AND budget = alert at $2.40, which is normal operations).

**Option C — Anomaly-based:** Alert when daily spend exceeds 2x the 7-day average. This auto-adjusts as usage patterns change.

### Q63. Should feedback on one company propagate to similar companies?

**Option A — Never propagate:** Each company is independent. Corrections are local.

**Option B — Suggest but don't auto-apply (recommended):** When Mark corrects a fact for an HVAC company in Virginia, the system checks: "2 other Virginia HVAC companies have the same estimated value. Should this correction apply to them too?" Present as a suggestion, not automatic. Mark clicks yes or no.

**Option C — Auto-propagate within vertical:** Same-vertical corrections auto-apply. Risky: one bad correction cascades to multiple companies.

### Q65. Should auto-learning be paused to prevent rule bloat?

**Option A — Never pause:** Let the system keep learning. If rules conflict, the newer rule wins.

**Option B — Pause at threshold (recommended):** After 30 auto-learned rules, pause new learning and present the full rule list for human review. Prune obsolete rules, confirm valuable ones, then re-enable learning. This prevents silent accumulation of contradictory rules.

**Option C — Periodic review:** Monthly review of all auto-learned rules regardless of count. No pause, but regular cleanup.

### Q71. What percentage of proposals should be human-reviewed before auto-approval is trusted?

**Option A — 100% forever:** Every proposal gets human review. The certifier assists but never decides alone.

**Option B — Per-vertical graduation (recommended):** Each vertical graduates independently. After 10 consecutive approvals with zero edits for HVAC proposals, HVAC proposals can be auto-approved. Plumbing still needs review until its own 10-approval streak. This accounts for vertical-specific patterns.

**Option C — Per-template graduation:** The auto-trust threshold applies to the specific template + model combination, not the vertical. More granular but slower to graduate.

### Q73. Should the human review queue have a SLA?

**Option A — No SLA:** Reviews happen when they happen. Low volume doesn't justify formal SLAs.

**Option B — 24-hour SLA with escalation (recommended):** Reviews should be completed within 24 hours. After 24 hours, iMessage alert to Ewing: "{count} reviews pending > 24 hours." After 48 hours, auto-approve items with quality_score >= 90 (the system is probably right). Items with quality_score < 90 stay in queue with a "STALE" flag.

**Option C — Tiered SLA:** Hot leads: 2 hours. Active deals: 12 hours. Pipeline research: 48 hours.

### Q74. Is dual-LLM certification worth it at scale?

**Option A — Always dual-LLM:** Every proposal, every time. Cost: ~$0.006 per certification (DeepSeek). At 100 companies = $0.60/day. Worth it for quality assurance.

**Option B — Risk-based (recommended):** Dual-LLM for proposals with quality_score < 90 or estimated fields > 30%. Single-LLM (different from generator) for high-confidence proposals. At 100 companies, maybe 30% need dual certification = $0.18/day. Saves cost where it's least needed.

**Option C — Dual-LLM until graduated:** Use dual-LLM for all proposals in a vertical until that vertical graduates (10 consecutive approvals). Then switch to single-LLM for that vertical.

### Q76. How many queue items per day at target scale?

**Option A — 50/day (near-term):** 6 active companies × 8 pipeline steps = ~50 items/day. Current single worker handles this in 2-3 hours.

**Option B — 200/day (medium-term, recommended target):** 25 active companies × 8 steps = ~200 items/day. Requires 3 parallel workers. Achievable with current architecture.

**Option C — 500+/day (full vision):** 50+ companies, full Listener automation, continuous buyer monitoring. Requires architectural changes: message queue (Redis/RabbitMQ), horizontal worker scaling.

### Q87. Budget caps: per-company or per-entity?

**Option A — Per-entity (current):** NC gets $5/day total. Simple, but one expensive company can eat the budget for all others.

**Option B — Per-company within entity (recommended):** NC gets $5/day total, AND no single company can use more than $1/day. This prevents one data-rich company from consuming the entire entity budget while ensuring equitable research across the pipeline.

**Option C — Dynamic per-company:** Budget allocation based on pipeline stage. Discovery-stage companies get $0.50/day. Active engagements get $2/day. This automatically prioritizes spend on deals closest to revenue.

### Q92. Should auto-trust thresholds vary by entity?

**Option A — Same threshold everywhere:** 10 consecutive approvals for all entities. Consistency.

**Option B — Entity-adjusted (recommended):** NC cold call follow-ups: 5 approvals (lower stakes, higher volume). AND Capital LP outreach: 15 approvals (higher stakes, lower volume, reputation-sensitive). RevsUp: 10 approvals (middle ground).

**Option C — Stake-based:** Threshold varies by play type, not entity. "Schedule callback" = 3 approvals. "Send proposal to client" = 15 approvals. "LP fund presentation email" = 20 approvals.

### Q93. When Listener encounters unknown situation: speed or quality?

**Option A — Speed:** Draft a best-guess play immediately. Better to send a decent response fast than a perfect response late.

**Option B — Quality:** Flag for human design. Mark creates the play template. System learns for next time.

**Option C — Tier by urgency (recommended):** If the signal is time-sensitive (prospect said "send me info," buyer replied), draft a best-guess play immediately and flag for review (speed). If the signal is not time-sensitive (prospect mentioned a competitor, buyer went quiet), flag for human design (quality).

### Q95. How should contradictory signals be resolved?

**Option A — Most recent wins:** The last signal is the current truth. If the transcript says "not now" but Slack says "great call," Slack (more recent, human-filtered) wins.

**Option B — Source hierarchy (recommended):** Trust hierarchy: human input (Mark's Slack/notes) > transcript analysis > email sentiment > call disposition. When sources conflict, use the highest-trust source and log the contradiction for review.

**Option C — Flag for human resolution:** Any contradiction = human review. Show both signals, let Mark pick. Most accurate, but creates review queue volume.

---

## TIER 3: HARD QUESTIONS (16 questions)
High impact. I have specific questions for you that only you can answer. Let's get these right.

---

### Q1. HVAC company + family office investor: Next Chapter or AND Capital?

**Why this matters:** This is the #1 classification ambiguity. Gets it wrong = wrong pipeline, wrong team, wrong deliverables.

**Questions for you:**
1. When you encounter a family office that OWNS an HVAC company, is your instinct "help them sell the HVAC company" (NC) or "pitch them on investing in your fund" (AND)?
2. Is the family office the PROSPECT or the OWNER? If they're a potential LP, it's AND. If they own the trade company and might sell, it's NC.
3. Can a single company be BOTH — an NC sell-side target AND an AND Capital LP prospect? Or must it be one or the other?

### Q15. For buy-side clients (Weiser, Design Precast), what does the "proposal" look like?

**Why this matters:** 33% of your pipeline is buy-side. The entire proposal engine is hardcoded for sell-side. This answer determines what gets built.

**Questions for you:**
1. When Weiser says "find us acquisition targets," what deliverable do they expect? A list of companies for sale? A market landscape? Individual target profiles with owner research?
2. Is the buy-side "proposal" more like a research report ("here are 15 concrete companies that might sell") or more like a matchmaking pitch ("here's why Target X is perfect for you")?
3. For buy-side, are YOU sourcing the targets (cold outreach to owners who haven't listed) or are you aggregating known listings (BizBuySell, brokers)?

### Q19. Buy-side attack plan: "all about the targets" or "all about the buyer's growth strategy"?

**Why this matters:** Determines the framing of every buy-side deliverable.

**Questions for you:**
1. When you present targets to Weiser, does the conversation center on "here's what makes this target great" or "here's how this target fits your growth plan"?
2. Do buy-side clients like Weiser already HAVE a documented growth strategy, or is part of your value helping them articulate one?
3. Should the buy-side proposal include a "why acquire" section (justifying M&A vs organic growth), or do they already know they want to buy?

### Q27. For buy-side clients, how do you source acquisition targets?

**Why this matters:** Determines whether buyer_research.py searches for "companies for sale" or "companies that COULD be sold."

**Questions for you:**
1. Do you look at public listings (BizBuySell, business brokers, deal platforms), or do you cold-approach owners who haven't listed?
2. If cold approach: what signals indicate an owner might sell? Age? Years in business? No succession plan? Recent competitor acquisitions?
3. What does Weiser actually want — 5 vetted targets with owner meetings set up, or 50 names on a spreadsheet to review?

### Q33. For the 30/60/90 timeline, who actually executes each step?

**Why this matters:** The system generates timelines but doesn't know who does the work.

**Questions for you:**
1. Does Mark manually send every letter, or is there a mail house / print service?
2. Are cold calls made through Salesfinity (auto-dialer) or manual dialing?
3. Who sends the LinkedIn messages — Mark personally, or could this be automated?
4. For the "letter campaign to top 10 buyers" — is that 10 individual letters or one mail merge?

### Q38. For competitive situations (prospect talking to other brokers), how aggressive?

**Why this matters:** The engagement engine needs different scripts for competed vs. uncontested deals.

**Questions for you:**
1. When you learn a prospect is talking to another broker, does that change the pitch? More urgent? Different value proposition? Lower fee?
2. Is it appropriate to directly address the competition ("here's how we're different from XYZ Advisors") or should it be indirect?
3. At what point do you walk away from a competitive situation? Never? Only if they've already signed with someone else?

### Q39. What is the guarantee structure for different deal sizes?

**Why this matters:** The fee mode system in the guardrails references guarantees but doesn't define them by deal size.

**Questions for you:**
1. For a $2M deal vs a $10M deal vs a $50M deal, does the guarantee structure change?
2. Is the guarantee a fixed dollar amount, a percentage of estimated value, or something else?
3. Do buy-side deals have a different guarantee structure than sell-side?

### Q61. Who is the primary feedback provider — Mark or Ewing?

**Why this matters:** Determines whose corrections train the system.

**Questions for you:**
1. In practice, who reviews proposals before they go to clients — Mark, you, or both?
2. When Mark and you disagree on a correction, who has final say?
3. Should the system learn different patterns from each person (Mark's operational corrections vs your strategic corrections)?

### Q81. Should the web server be internet-accessible?

**Why this matters:** Client data rooms require internet access. Internal tools don't. This is a security/convenience tradeoff.

**Questions for you:**
1. Do clients need to access their data room from their own computers, or do you always present it on your screen?
2. Is Mark on the same local network as the Mac mini, or does he work remotely?
3. Are you comfortable with Tailscale (private network, your devices only) or do clients need public URLs?

### Q82. What is the authentication story?

**Why this matters:** This gates whether external access is safe.

**Questions for you:**
1. How many people total need access? Just you + Mark? Or also clients?
2. For client access, is "obscured URL with a long random token" sufficient (like a Google Doc share link), or do they need a login?
3. Does Mark need different permissions than you? (e.g., Mark can't change entity routing or guardrails)

### Q86. What is the actual maximum daily spend across all entities?

**Why this matters:** Current caps ($11/day total) will throttle at 10+ companies.

**Questions for you:**
1. What's your monthly ceiling for API costs? $100? $300? $500?
2. At $0.05-$0.10 per company per pipeline run, 20 companies = $1-$2/day in Exa alone. Plus OpenRouter. Is $5-$10/day realistic for NC?
3. Is there a "no questions asked" daily budget (spend freely) vs a "check with me" threshold?

### Q91. Listener channel priority — if you could only have ONE?

**Why this matters:** Building all 5 channel integrations takes months. ONE channel can be built this week.

**Questions for you:**
1. Which channel produces the most "send me info" moments — phone calls (Fireflies), emails (Gmail), or calendar events?
2. Where do you lose the most deals to slow response — missed emails, missed follow-ups after calls, or unprepped meetings?
3. If the Listener only watched Gmail for the next 3 months, would that cover the highest-value signals?

### Q96. Research transparency — internal or external audience?

**Why this matters:** Internal = show everything (failed searches, cost, methods). External = curate for trust-building.

**Questions for you:**
1. Have you ever shown a prospect HOW you researched them? What was the reaction?
2. Is "here's exactly how we prepared for this meeting" part of the pitch, or would it distract from the content?
3. Could research transparency be a CLOSING tool? ("Look how much work we've already done — imagine what we'll do under engagement.")

### Q99. Minimum viable data room — what's the floor?

**Why this matters:** The data room is the "send me info" response. Building it wrong wastes the highest-leverage moment.

**Questions for you:**
1. When a prospect says "send me more information," what do you CURRENTLY send them? An email with attachments? A PDF? Nothing automated?
2. What 3 things does the prospect most want to see after a call?
3. Does the data room need to be INTERACTIVE (editable fields, calculators), or is a beautiful static page with their company data sufficient for v1?

### Q100. When is NC "done enough" to start AND Capital and RevsUp automation?

**Why this matters:** You have 3 businesses but one engineering pipeline. This question determines resource allocation.

**Questions for you:**
1. What's generating revenue RIGHT NOW — NC deals in motion, AND Capital LP calls, or RevsUp placements?
2. Is AND Capital blocked on anything that this CRM could solve (LP list management, fund deck distribution, meeting prep)?
3. If NC were running perfectly on autopilot, what's the FIRST thing you'd want automated for AND Capital?

---

## WORKING THROUGH THIS

**Recommended order:**
1. Start with **TIER 3 (Hard)** — your answers unlock the most architectural decisions
2. Batch-approve **TIER 1 (Easy)** — scan for any you disagree with, otherwise I implement all 52
3. Pick options on **TIER 2 (Nuanced)** — I've marked my recommendations, you confirm or redirect

When you're ready, start with the Hard questions. Take them in any order. I'll implement decisions as you make them.
