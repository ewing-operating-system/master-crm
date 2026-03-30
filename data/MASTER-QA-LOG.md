# Master Question & Answer Log

**Purpose:** Every question asked of Ewing or Mark, and every answer provided, lives here permanently. This is the institutional memory of all decisions. Agents check this before asking duplicate questions. The orchestrator ensures new Q&A entries create downstream business rules.

**Rules:**
1. Every question asked → logged here with timestamp
2. Every answer → logged here with the question it answers
3. After each answer → create or update the appropriate business rule/memory file
4. Orchestrator audits this log weekly for unenforced rules

---

## SESSION 1: 2026-03-28 to 2026-03-29 (Full System Audit + Rebuild)

### ROUND 1: Listener Agent — Yes/No (5 questions)

**Q1 (2026-03-29):** When the Listener finds a signal in Fireflies and the same person also emailed — should it combine those into ONE situation diagnosis or two separate plays?
**A1:** Yes — combine into ONE diagnosis with richer data. Not two separate plays.
**Rule created:** feedback_listener_rules.md #1

**Q2:** "Send me an email" with zero context — always the full play or sometimes simpler?
**A2:** Always the full play. Dossier subset + market multiples delighter + data room link. Never a simple one-liner.
**Rule created:** feedback_listener_rules.md #2

**Q3:** Should the Listener scan Mark's Salesfinity calls the same way as Ewing's?
**A3:** Yes. All callers by default. Plays map to each entity.
**Rule created:** feedback_listener_rules.md #3

**Q4:** Auto-trust threshold — 5 human approvals or more? Does a minor edit reset?
**A4:** 10 approvals, not 5. Any edit (even minor) resets to zero.
**Rule created:** feedback_listener_rules.md #4

**Q5:** Data room — Lovable or simpler?
**A5:** Start simple. Lovable comes later to display the same data better. Be ready for it.
**Rule created:** feedback_listener_rules.md #5

---

### ROUND 2: Listener Agent — Yes/No (5 questions)

**Q1 (2026-03-29):** New situation the Listener hasn't seen — pause and wait or draft best-guess?
**A1:** Draft best-guess, create the play, name it, define it, provide editable knobs. Label as new. Don't block the pipeline.
**Rule created:** feedback_listener_rules_2.md #1

**Q2:** Proposal include fee structure explicitly or verbal only?
**A2:** 5 configurable fee modes: none, framework_only, median_market_disclosure, proposed_working_fee, interactive_models. Each serves a different purpose.
**Rule created:** feedback_listener_rules_2.md #2

**Q3:** Competitor mention — immediate escalation or normal cadence?
**A3:** Immediate escalation. Compile industry package + "90 days, no fee, 2 qualified buyers or we fire ourselves" risk-free offer. Create page, notify Mark/Ewing/ops channel.
**Rule created:** feedback_listener_rules_2.md #3

**Q4:** Client portal — show all buyer targets or curated subset?
**A4:** Admin/client dual views on EVERY page. Admin sees everything. Toggle to client view to filter. We always control what the customer sees.
**Rule created:** feedback_listener_rules_2.md #4

**Q5:** Same company mentioned by two reps — auto-merge or flag for human?
**A5:** Auto-merge and notify both immediately via iMessage.
**Rule created:** feedback_listener_rules_2.md #5

---

### ROUND 3: Open-Ended Theory Guardrails (5 questions)

**Q1 (2026-03-29):** What does "done" look like for a perfect Next Chapter engagement?
**A1:** Letter triggers inbound call (recorded). Customer says "send me info." System builds deal room + plan page. Customer plays with knobs, clicks "let's get started." Contract signed. Letters, call lists, LinkedIn, agent calls — all automated from a single phone call. Zero human work after the initial call.
**Rule created:** feedback_nc_theory_guardrails.md #1

**Q2:** Where's the line between "impressively thorough" and "creepily invasive"?
**A2:** Public info is fair game. Industry data, podcasts, interviews, awards, BBB, Google reviews. NEVER negative facts (divorce, lawsuits, closures, arrests). Always disclose methodology for estimates. Education is king.
**Rule created:** feedback_nc_theory_guardrails.md #2

**Q3:** When two businesses could serve the same person, how to handle?
**A3:** RevsUp first. Next Chapter second. AND Capital third. Smaller sale comes first. Earn trust, then expand. Never multi-entity on first contact.
**Rule created:** feedback_nc_theory_guardrails.md #3

**Q4:** What kills a deal?
**A4:** #1: Hallucinated personalization (wrong facts in letter). #2: Wildly inaccurate estimates. #3: Sending with nothing to go on. Fix: multi-agent double verification, always. Worth the money.
**Rule created:** feedback_nc_theory_guardrails.md #4

**Q5:** If this system runs perfectly for a year, what does Monday morning look like?
**A5:** 9-section dashboard: campaigns to run, quality tuning, new rules needed, agent performance, outbound activity, revenue metrics, problem identification, agent requests, spend by category/vendor/stage.
**Rule created:** feedback_nc_theory_guardrails.md #5

---

### ROUND 4: Forced Choice (7 questions)

**Q1 (2026-03-29):** Insufficient data for personalization — what happens?
**A1:** Cascade: C (honesty frame) → B (industry education) → A (skip). Never send low quality. Score >= 80 full personalized, 50-79 honesty frame, 30-49 industry education, < 30 skip.
**Rule created:** feedback_nc_forced_choices.md #1

**Q2:** Prospect control on deal room / proposal page — how much?
**A2:** B — light editing. They adjust revenue, employees, service mix. Plan regenerates. They CANNOT change narrative or strategy.
**Rule created:** feedback_nc_forced_choices.md #2

**Q3:** Response speed?
**A3:** Same hour if quality passes. Never send low quality regardless of urgency. Quality >= 80 + hot → within hour. 50-79 or warm → same business day. < 50 → hold for review.
**Rule created:** feedback_nc_forced_choices.md #3

**Q4:** Live call intel — should system do anything in real time?
**A4:** D — both. Push silent notification to rep's screen with relevant data DURING call. Simultaneously draft follow-up email so it's ready at call end.
**Rule created:** feedback_nc_forced_choices.md #4

**Q5:** "90 days, 2 buyers, fire ourselves" guarantee — binding?
**A5:** Most likely a version of D — deal-size dependent. Full guarantee below threshold, negotiated above.
**Rule created:** feedback_nc_forced_choices.md #5

---

### ROUND 5: Overnight Build Rules (7 questions)

**Q1 (2026-03-29):** LLM disagreement on facts?
**A1:** B — use higher confidence, disclose methodology.
**Rule created:** feedback_overnight_decision_tree.md #1

**Q2:** Thin Exa results?
**A2:** C — exhaust ALL search methods before marking thin. Alternate queries AND backup sources.
**Rule created:** feedback_overnight_decision_tree.md #2

**Q3:** DNC buyer in attack plan?
**A3:** D — DNC applies to OUR outreach only. Client can contact independently. Include but mark restricted.
**Rule created:** feedback_overnight_decision_tree.md #3

**Q4:** Quality score below 80?
**A4:** Cascade: B (regenerate, 3 attempts) → D (more Exa searches, fill gaps) → C (ship as draft with flag).
**Rule created:** feedback_overnight_decision_tree.md #4

**Q5:** Company already acquired?
**A5:** D — both. Log intel AND pivot approach. Acquirer may want additional acquisitions.
**Rule created:** feedback_overnight_decision_tree.md #5

**Q6:** HTML output polish level?
**A6:** C — polished, professional, print-ready. Inline CSS, logo placeholder.
**Rule created:** feedback_overnight_decision_tree.md #6

**Q7:** Buyer list sizing?
**A7:** B & A hybrid — top 10 detailed profiles + include ALL remaining as complete list.
**Rule created:** feedback_overnight_decision_tree.md #7

---

### ROUND 6: Feedback Loop System (5 questions)

**Q1 (2026-03-29):** Comment on a section — what happens?
**A1:** D then C. System asks clarifying questions FIRST ("too high compared to what?"), then drafts revised version with original preserved alongside. The conversation is the training data.
**Rule created:** feedback_commenting_system.md #1

**Q2:** Mark corrects a fact — what should that correction apply to?
**A2:** E (beyond any option). System asks Mark WHERE he found the info, dispatches agent to replicate the path, adds the technique to research_methods library. Every correction = new capability.
**Rule created:** feedback_commenting_system.md #2

**Q3:** How granular should commenting be?
**A3:** D (B+C) with emphasis on box-level. Section-level comment boxes primary, inline for fact corrections secondary.
**Rule created:** feedback_commenting_system.md #3

**Q4:** Approve a section — what happens?
**A4:** D (B+C) with human-in-the-loop on every rule change. Propose as template, weight patterns higher, BUT explicitly explain the rule change and get approval. No silent changes.
**Rule created:** feedback_commenting_system.md #4

**Q5:** Mark and Ewing disagree — how to resolve?
**A5:** Red banner across page: "CONFLICT RESOLUTION NEEDED." Arrow to problem area. Floating modal with 10 options: 3-4 combined versions if compatible, otherwise 5 best of Ewing's + 5 best of Mark's. Best idea wins regardless of who suggested it.
**Rule created:** feedback_commenting_system.md #5

---

### ROUND 7: Hosting Questions (10 questions)

**Q1-3:** Already answered in earlier rounds (covered by Listener rules).

**Q4 (2026-03-29):** Supabase-backed static site?
**A4:** Yes. The only way to go.
**Rule created:** feedback_hosting_final.md #1

**Q5:** Phone or desktop first?
**A5:** Desktop first. Phone comes when we push to clients.
**Rule created:** feedback_hosting_final.md #2

**Q6:** Internal or client-facing?
**A6:** Internal for now. Client-facing when we push to clients.
**Rule created:** feedback_hosting_final.md #3

**Q7:** Simple static HTML good enough for 30 days?
**A7:** Depends on fast user training feedback loops. Feedback loop system is the gating decision.
**Rule created:** feedback_hosting_final.md #4

**Q8:** Vercel or other?
**A8:** Mark has used Vercel successfully before. Zero learning curve.
**Rule created:** project_hosting_stack.md

**Q9:** Can localhost handle boxes, lines, bullets, headings?
**A9:** Yes, so long as it's organized with some styling. Not blobs of text.
**Rule created:** feedback_hosting_final.md #5

**Q10:** Bigger risk — data wrong or presentation ugly?
**A10:** By far data is wrong. Presentation gets better over time.
**Rule created:** feedback_hosting_final.md #6

---

### ROUND 8: V1 Release Decisions (10 questions)

**Q1 (2026-03-29):** Attack plan buyer view — map or table?
**A1:** Map with pins AND table with filters, sorting, and ajax-like quick search across whole table.
**Rule created:** feedback_v1_release_decisions.md #1

**Q2:** Old version banner?
**A2:** Yes, absolutely, with date and timestamp. "You are viewing Version 2 of 5 — NOT current. Generated March 28, 2026 3:14 PM."
**Rule created:** feedback_v1_release_decisions.md #2

**Q3:** Buyer 1-pager depth — full financials?
**A3:** Include buyer financials for now as feedback loop training bait. When Mark says "remove this for buy-side" — that's a real rule creation event. Future: "release financials" toggle.
**Rule created:** feedback_v1_release_decisions.md #3

**Q4:** Mark's templates — how to seed?
**A4:** A — pull from Google Drive. Refresh at least once per hour.
**Rule created:** feedback_v1_release_decisions.md #4

**Q5:** Rule change rebuild — all at once or queued?
**A5:** B — queue and only rebuild when user views the page. Lazy rebuild. Accumulate changes during rapid feedback loops.
**Rule created:** feedback_v1_release_decisions.md #5

**Q6:** "Let's Get Started" button does what?
**A6:** C expanded. Client picks fee option → sees attack plan with pre-written letters → clicks "Send me a proposal" → gets "check email in 24 hours" → Slack notification → proposal builder page (configurable blocks) → submit → static page with version history → email PDF + page link. Stop at email/PDF.
**Rule created:** feedback_v1_release_decisions.md #6

**Q7:** Data room shows valuation?
**A7:** D (configurable) but default to show everything. Frame educationally: "according to what most buyers will find..." Add "Levers of EBITDA" section.
**Rule created:** feedback_v1_release_decisions.md #7

**Q8:** Sidebar company order?
**A8:** D — all of the above. Drag reorder, star favorites, Active/Nurture/Archived tabs.
**Rule created:** feedback_v1_release_decisions.md #8

**Q9:** Buyer script variations?
**A9:** B — 3 variations per outreach method per buyer. User choice trains future generation.
**Rule created:** feedback_v1_release_decisions.md #9

**Q10:** Buyer on multiple seller lists?
**A10:** D — flag overlap now (B), multi-deal buyer view later (C).
**Rule created:** feedback_v1_release_decisions.md #10

---

### ADDITIONAL DECISIONS (not from structured Q&A rounds)

**Decision (2026-03-29):** Speed-to-production rule.
Publish variation 1 immediately. Batch variations 2 & 3 in background. Never block production waiting for alternatives.
**Rule created:** feedback_speed_to_production.md

**Decision (2026-03-29):** Deal side classification.
Weiser Concrete + Design Precast = BUY-SIDE. HR.com, AquaScience, Air Control, Springer Floor = SELL-SIDE.
**Rule created:** project_deal_sides.md

**Decision (2026-03-29):** Story narrative is EVERYTHING.
The deep fit analysis (14K+ chars) is THE product. Must-see-TV content. Never truncate, never lose sight.
**Rule created:** feedback_data_integrity_rules.md #3

**Decision (2026-03-29):** Always check existing data before researching.
The HR.com/SAP incident: 66 deep buyer dossiers existed but new system generated 10 thin ones from scratch. HARD RULE: check deal_research, dossier_final, intelligence_cache BEFORE any new research.
**Rule created:** feedback_check_existing_data_first.md

**Decision (2026-03-29):** Dedup to ONE record. Merge all facts. Duplicates suck ass, always.
**Rule created:** feedback_data_integrity_rules.md #1

**Decision (2026-03-29):** Run ALL research methods every time. Methods are cheap. Not every company has a podcast story, but we want to be the ones with the methods to find it when it exists.
**Rule created:** feedback_data_integrity_rules.md #5

**Decision (2026-03-29):** Google Drive is the template source. Mark works there naturally.
**Rule created:** feedback_template_library.md

**Decision (2026-03-29):** Human-curated template library for iterative refinement.
V2 feature — after engines produce output worth refining.
**Rule created:** feedback_template_library.md

**Decision (2026-03-29):** Operating philosophy: Create method. Test with data. Detailed feedback. Iterate. Evolve. Repeat.
**Rule created:** NORTH-STAR-operating-philosophy.md

---

*This log is append-only. New sessions add entries below this line.*
