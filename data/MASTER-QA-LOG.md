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

---

## SESSION 2: 2026-03-30 (97 CRM Decisions)

### HARD — Only Ewing Can Answer (13 questions)

**Q1 (2026-03-30):** HVAC company + family office investor: NC or AND Capital?
**A1:** NC always if there is a next chapter fit. Family office = potential buyer we can match to another company. AND Capital is never automated. System never assumes NC lead is AND lead.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q1

**Q15 (2026-03-30):** Buy-side clients (Weiser, Design Precast) — what does the "proposal" look like?
**A15:** Targets meeting buyer criteria. First meeting includes criteria selectors. Ad-hoc criterion input pushes to search engines. Matchmaking pitch with 2-3% fee. Buyer suggestions become lookalikes for fit score training.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q15

**Q19 (2026-03-30):** Buy-side: "all about the targets" or "all about the buyer's growth strategy"?
**A19:** About selection criteria, estimated worth, EBITDA levers. Not McKinsey — we fill the order, not change strategy.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q19

**Q27 (2026-03-30):** Buy-side: how do you source acquisition targets?
**A27:** Phone, letters, emails, lunch, networking, public listings. Need buying signal agent (Apify on Instagram). Weiser wants 5 vetted targets this year.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q27

**Q33 (2026-03-30):** 30/60/90 timeline — who executes each step?
**A33:** APIs send automatically. Salesfinity is the calling system. LinkedIn Helper on desktop, need sub-agent for campaign orchestration.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q33

**Q38 (2026-03-30):** Competitive situations — how aggressive?
**A38:** Build attack plan with detailed research urgently. Don't address competition directly but emphasize "we can dial this list tomorrow." Walk away only on explicit no-opportunity message.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q38

**Q39 (2026-03-30):** Guarantee structure for different deal sizes?
**A39:** $10K minimum, 10% of transaction. 5% if >$500K commission. Fixed engagement fee + sliding success fee. Buy-side 2-3%. Sell-side 5-7%.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q39

**Q61 (2026-03-30):** Primary feedback provider — Mark or Ewing?
**A61:** Learn from each. Mark = wordsmith/final copy. Ewing = system architect/content structure. Final say usually Mark (downstream). Lean Ewing on structure, Mark on words.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q61

**Q62 (2026-03-30):** Differentiate learning from Mark vs Ewing?
**A62:** Yes, differentiate. Both swarm everything client-facing for now.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q62

**Q81 (2026-03-30):** Web server internet-accessible?
**A81:** Yes. Clients must access data rooms. Public URLs. Email gating. Default passwords = website domain.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q81

**Q82 (2026-03-30):** Authentication story?
**A82:** Clients get access. Wide open for now. Mark and Ewing both admins.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q82

**Q86 (2026-03-30):** Maximum daily spend across all entities?
**A86:** Monthly ceiling $500. Alerts at every $50 milestone. Slack + SMS. Need cost monitoring agent to prevent runaway API calls.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q86

**Q91 (2026-03-30):** Listener channel priority — if only ONE?
**A91:** Salesfinity transcripts first, then email, then Fireflies. Letters + phone are the two methods that work. Email/LinkedIn distant.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q91

**Q96 (2026-03-30):** Research transparency — internal or external?
**A96:** Build it in. Clients love knowing. Transparency is the brand. Methodology, rigor, precision.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q96

**Q99 (2026-03-30):** Minimum viable data room — what's the floor?
**A99:** Page showing what we know about them. Who we are, who we represent, what separates us, success history, plan. Interactive (sliders, edits) — store their changes for behavioral learning.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q99

**Q100 (2026-03-30):** When is NC "done enough" for AND Capital & RevsUp?
**A100:** NC = representing businesses to sell. AND is distant 2nd. Data must be coherent, attack lists built, research engines ready to audit existing data.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q100

---

### NUANCED — Pick A, B, or C (28 questions)

**Q3 (2026-03-30):** Multi-entity people (Mark spans all 3): classify by CAMPAIGN or CONTENT?
**A3:** Choice C — Hybrid. Both campaign and content context.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q3

**Q4 (2026-03-30):** Entity transitions (NC deal becomes AND investment)?
**A4:** Choice C — Dual-tag. Both entity tags preserved.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q4

**Q6 (2026-03-30):** "Smallest entity first" vs urgency?
**A6:** Choice B — Urgency always first.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q6

**Q8 (2026-03-30):** DNC list include "soft DNC"?
**A8:** Choice C — Binary + inbound exception. DNC blocks outbound, but inbound responses allowed.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q8

**Q12 (2026-03-30):** How often regenerate profiles?
**A12:** Choice C — Trigger + 24hr cooldown.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q12

**Q14 (2026-03-30):** Minimum data completeness for "ready" profile?
**A14:** Choice B — 70%.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q14

**Q17 (2026-03-30):** Wrong valuation: deal-killer or conversation-starter?
**A17:** Choice C — Range + framing.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q17

**Q18 (2026-03-30):** Multiples vary by geography, size, recency?
**A18:** Choice B — Full segmentation.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q18

**Q20 (2026-03-30):** Revenue from employee count — margin of error?
**A20:** Choice B — Only with corroboration.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q20

**Q25 (2026-03-30):** Owner-operators — special handling?
**A25:** Choice B — Treat normally.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q25

**Q26 (2026-03-30):** How many buyers per deal?
**A26:** Choice C — Adaptive by vertical.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q26

**Q29 (2026-03-30):** Multi-deal buyers: coordinated or independent?
**A29:** Choice B — Coordinated.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q29

**Q30 (2026-03-30):** Buyer declines — remove from ALL lists?
**A30:** Choice B — That deal only.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q30

**Q35 (2026-03-30):** Buyer responds positively — what triggers next stage?
**A35:** Choice C — Multi-signal.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q35

**Q46 (2026-03-30):** Live calls — what data pushed to screen?
**A46:** Choice B — Smart card.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q46

**Q47 (2026-03-30):** Post-meeting outcomes — how captured?
**A47:** Choice B — Transcript analysis.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q47

**Q49 (2026-03-30):** Back-to-back meetings with different companies?
**A49:** Choice B — Context-switch alerts.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q49

**Q52 (2026-03-30):** Dashboard revenue metrics?
**A52:** Choice B — Pipeline + fees.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q52

**Q57 (2026-03-30):** Budget alert threshold?
**A57:** Choice C — Anomaly-based.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q57

**Q63 (2026-03-30):** Feedback propagate to similar companies?
**A63:** Choice B — Suggest, don't auto-apply.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q63

**Q65 (2026-03-30):** Pause auto-learning to prevent rule bloat?
**A65:** Choice B — Pause at 30 rules.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q65

**Q71 (2026-03-30):** Human review % before auto-approval trusted?
**A71:** Choice B — Per-vertical graduation.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q71

**Q73 (2026-03-30):** Review queue SLA?
**A73:** Choice B — 24hr + escalation.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q73

**Q74 (2026-03-30):** Dual-LLM certification worth it at scale?
**A74:** Choice A — Always dual.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q74

**Q76 (2026-03-30):** Queue items per day at target scale?
**A76:** Choice B — 200/day.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q76

**Q87 (2026-03-30):** Budget caps: per-company or per-entity?
**A87:** Choice B — Per-company within entity.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q87

**Q92 (2026-03-30):** Auto-trust thresholds vary by entity?
**A92:** Choice C — Stake-based.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q92

**Q93 (2026-03-30):** Listener unknown situation: speed or quality?
**A93:** Choice C — Tier by urgency.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q93

**Q95 (2026-03-30):** Contradictory signals — how resolved?
**A95:** Choice B — Source hierarchy.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q95

---

### EASY — Approve or Override (42 questions)

**Q2 (2026-03-30):** Classifier auto-reclassify human-tagged record?
**A2:** APPROVED — No. Human always wins. Log disagreements. Add `manually_tagged` boolean.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q2

**Q5 (2026-03-30):** Confidence floor below which pipeline STOPS?
**A5:** APPROVED — Floor = 1.5 → human_review_queue. No downstream work.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q5

**Q7 (2026-03-30):** New reps: auto-detected or manual?
**A7:** APPROVED — Manual for now. New name → human_review_queue. Phase 2: auto-suggest.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q7

**Q9 (2026-03-30):** Companies in multiple verticals?
**A9:** OVERRIDDEN — Priority: NC > RU > AND.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q9

**Q10 (2026-03-30):** Entity classification visible to client?
**A10:** APPROVED — No. Internal only. Clients see "Next Chapter Advisory."
**Rule created:** CRM-DECISIONS-RULES.md Rule Q10

**Q11 (2026-03-30):** Mark says $5M, Exa says $2.25M — who wins?
**A11:** APPROVED — Human wins. Store both with source. "$5M (owner-reported)" + footnote.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q11

**Q13 (2026-03-30):** Field confidence indicators?
**A13:** APPROVED — CONFIRMED / ESTIMATED / UNKNOWN. Admin sees labels. Client sees footnotes.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q13

**Q16 (2026-03-30):** Quality 50-79 — proposals to clients?
**A16:** OVERRIDDEN — Sits in needs_review with instructive details and manual research instructions.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q16

**Q21 (2026-03-30):** Track estimate accuracy?
**A21:** APPROVED — Create estimate_accuracy table. Log deltas. Monthly aggregate.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q21

**Q22 (2026-03-30):** Two LLMs disagree on a fact?
**A22:** OVERRIDDEN — Human or agent (third LLM) picks winner. Long-term: agent. Need training injection without blocking.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q22

**Q23 (2026-03-30):** Show methodology on every page?
**A23:** APPROVED — Yes. This IS the brand. Admin: full. Client: lighter.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q23

**Q24 (2026-03-30):** Sensitive verticals — extra restrictions?
**A24:** APPROVED — No. Existing guardrails sufficient. HIPAA/SEC case-by-case.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q24

**Q28 (2026-03-30):** Buyer research refresh?
**A28:** OVERRIDDEN — Signed = weekly. Pipeline = bi-weekly. Unresponded = quarterly.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q28

**Q34 (2026-03-30):** DNC'd buyers in client view?
**A34:** OVERRIDDEN — Visible with reason. Full disclosure.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q34

**Q36 (2026-03-30):** Buyer fit scores visible to clients?
**A36:** OVERRIDDEN — Yes. Service to them.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q36

**Q37 (2026-03-30):** Flag buyer who completes acquisition?
**A37:** APPROVED — "Active Acquirer" flag. Increases fit score.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q37

**Q40 (2026-03-30):** Auto-detect buyer acquisitions?
**A40:** APPROVED — Monthly Exa scan. Log to buyer_activity. Auto-flag + notify.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q40

**Q41 (2026-03-30):** Meeting prep timing?
**A41:** APPROVED — 24 hours before. Regenerate if new data. Orchestrator checks calendar daily.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q41

**Q42 (2026-03-30):** Meeting pages phone-optimized?
**A42:** APPROVED — Key points top, collapsible, large taps, no horizontal scroll.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q42

**Q43 (2026-03-30):** Joint meetings — role assignments?
**A43:** APPROVED — Ewing: relationship/big picture. Mark: operational/process.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q43

**Q44 (2026-03-30):** Reschedule → regenerate prep?
**A44:** APPROVED — Yes. Keep old version in page_versions.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q44

**Q45 (2026-03-30):** iMessage prep 30 min before?
**A45:** OVERRIDDEN — Yes. "Meeting with {company} in 30 min. Key: {5 bullets}. Full: {link}."
**Rule created:** CRM-DECISIONS-RULES.md Rule Q45

**Q48 (2026-03-30):** Meeting type: enum or free text?
**A48:** OVERRIDDEN — Needs further review. Meeting page template architecture needed first.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q48 (flagged for TODO)

**Q50 (2026-03-30):** Meeting pages — competitive intel?
**A50:** APPROVED — Yes if available. Brokers in market, prior M&A, other conversations.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q50

**Q51 (2026-03-30):** Dashboard as landing page?
**A51:** APPROVED — Yes. Pipeline, reviews, problems, budget, quick links. Companies to sidebar.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q51

**Q53 (2026-03-30):** Dashboard system health?
**A53:** APPROVED — Green/yellow/red. Red if worker down >15min.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q53

**Q54 (2026-03-30):** Mobile dashboard?
**A54:** APPROVED — Responsive. Key metrics top. Collapsible.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q54

**Q56 (2026-03-30):** Dashboard entity filters?
**A56:** APPROVED — [All] [NC] [AND] [RU] + person presets. Cookie-stored.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q56

**Q58 (2026-03-30):** "While you were away" summary?
**A58:** APPROVED — Changes since last login. Track last_viewed_at.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q58

**Q59 (2026-03-30):** Dashboard refresh frequency?
**A59:** APPROVED — Live on load. Auto-refresh every 5 min.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q59

**Q60 (2026-03-30):** System confidence metric?
**A60:** APPROVED — "Data Quality: X% confirmed, Y% estimated, Z% unknown."
**Rule created:** CRM-DECISIONS-RULES.md Rule Q60

**Q64 (2026-03-30):** Feedback vs guardrails — who wins?
**A64:** OVERRIDDEN — Guardrails always win. Log violations. Dashboard feed. Weekly review. Only Ewing updates North Star.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q64

**Q66 (2026-03-30):** Version history depth?
**A66:** APPROVED — Last 10 per page. Older → archive (queryable, not in UI).
**Rule created:** CRM-DECISIONS-RULES.md Rule Q66

**Q67 (2026-03-30):** Edit = auto-create version?
**A67:** OVERRIDDEN — Yes, every edit = new version. But ASK before regenerating.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q67

**Q68 (2026-03-30):** Version history visible to clients?
**A68:** APPROVED — No. Current only.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q68

**Q69 (2026-03-30):** Rule change → rebuild 20 pages?
**A69:** APPROVED — Lazy. Mark stale, rebuild on view. Active engagements: background rebuild <1hr.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q69

**Q70 (2026-03-30):** Version-level commenting?
**A70:** APPROVED — One field: "Why was this changed?"
**Rule created:** CRM-DECISIONS-RULES.md Rule Q70

**Q72 (2026-03-30):** Certifier approves, Mark disagrees?
**A72:** APPROVED — Mark wins. Reverts to needs_review. 3 overrides → rule proposal.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q72

**Q75 (2026-03-30):** Pre-certification quick check?
**A75:** APPROVED — 5-point code check before LLM. Fail = skip cert, route to human.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q75

**Q77 (2026-03-30):** Orchestrator: entity or urgency priority?
**A77:** APPROVED — Urgency first, entity second. Round-robin within tiers.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q77

**Q78 (2026-03-30):** Orchestrator down 4hr — burst or pace?
**A78:** APPROVED — Pace at 2x. No bursting. Catch-up flag at backlog >20.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q78

**Q79 (2026-03-30):** Maintenance mode?
**A79:** APPROVED — active/maintenance/paused. Orchestrator stops, workers finish, watchdog runs.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q79

**Q80 (2026-03-30):** 5min orchestrator / 10sec worker correct?
**A80:** APPROVED — No change.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q80

**Q83 (2026-03-30):** Keep static HTML alongside server?
**A83:** APPROVED — Offline backup, email attachments, PDF gen. Server primary, files backup.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q83

**Q84 (2026-03-30):** Multiple simultaneous users?
**A84:** APPROVED — Flask/FastAPI. Multi-threading. Writes through queue.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q84

**Q85 (2026-03-30):** WebSockets needed?
**A85:** APPROVED — No. Page refresh + auto-refresh every 5 min.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q85

**Q88 (2026-03-30):** Budget exhausted — queue or skip?
**A88:** APPROVED — Queue for tomorrow. deferred_until timestamp. No work lost.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q88

**Q89 (2026-03-30):** API key expiration alerts?
**A89:** APPROVED — Weekly health check. 401/403 → iMessage alert.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q89

**Q90 (2026-03-30):** Deployment process?
**A90:** APPROVED — Manual git pull. Phase 2: deploy script. Phase 3: webhook.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q90

**Q94 (2026-03-30):** Listener scan historical on deploy?
**A94:** APPROVED — No. Start fresh. Historical = stale flood.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q94

**Q97 (2026-03-30):** Show failed research?
**A97:** APPROVED — Yes internally, no externally. Admin sees attempts.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q97

**Q98 (2026-03-30):** Research cost visible to clients?
**A98:** APPROVED — No. "$0.15" kills premium positioning.
**Rule created:** CRM-DECISIONS-RULES.md Rule Q98

---

## SESSION 3: Research Pipeline Decisions (2026-03-30)

**Context:** 22 decisions from RESEARCH-PIPELINE-DECISIONS.md covering search strategy, data assembly, page population, quality/certification, and pipeline orchestration. 3 questions skipped (Q4, Q10, Q16).

### Search Strategy

**Q1 (2026-03-30):** Exa returns articles without actual CEO quotes -- what next?
**A1:** Choice D -- Search different source (SEC filings, investor decks)
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R1

**Q2 (2026-03-30):** Private companies have no earnings calls. What's the equivalent?
**A2:** Choice E -- All of the above in priority order (podcasts -> conferences -> local press -> industry data)
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R2

**Q3 (2026-03-30):** Include buyer COMPETITOR searches? Creates urgency in pitch.
**A3:** Choice A -- Yes, 2 competitors per buyer
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R3

**Q5 (2026-03-30):** Different search templates per buyer type (PE vs strategic vs consolidator)?
**A5:** Choice A -- Yes, 3 distinct templates
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R5

### Data Assembly

**Q6 (2026-03-30):** Conflicting data (Exa says 15 employees, deal_research says 45) -- who wins?
**A6:** Choice C -- Show both with sources, never silently pick one
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R6
**Schema:** Added `data_conflicts JSONB` to companies table

**Q7 (2026-03-30):** Slider fields (revenue, employees, com/res split) -- default to estimate or blank?
**A7:** Choice C -- Estimate if confidence > MEDIUM, blank if LOW
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R7

**Q8 (2026-03-30):** Story narrative minimum length? System generated 3K chars instead of 14K target.
**A8:** Choice B -- Publish what it has + flag as thin ("THIN RESEARCH -- enrichment pending")
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R8

**Q9 (2026-03-30):** dossier_final vs proposals table have different revenue numbers -- which is truth?
**A9:** Choice A -- proposals table is canonical source of truth
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R9

### Page Population

**Q11 (2026-03-30):** Proposal page order: narrative -> strengths -> market -> valuation -> attack -> timeline. Right order?
**A11:** Choice A -- Current order is right (trust first)
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R11

**Q12 (2026-03-30):** Buyer 1-pager has 7 SAP sections. Show all even if some are thin?
**A12:** Choice B -- Hide sections without enough data
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R12

**Q13 (2026-03-30):** Data room (client-facing): show methodology by default or hide behind expandable?
**A13:** Choice C -- Admin sees full methodology; client sees expandable
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R13

**Q14 (2026-03-30):** EBITDA levers: show MISSING levers as red flags or only show strengths?
**A14:** Choice C -- Strengths prominent, gaps in separate "Growth Opportunities" section
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R14

**Q15 (2026-03-30):** Attack plan: generic or specific?
**A15:** Choice A -- Specific (named contacts, referenced acquisitions, actual scripts). SAP standard.
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R15

### Quality & Certification

**Q17 (2026-03-30):** Certifier flags NEEDS_REVIEW -- what does "instructive" look like?
**A17:** Choice C -- Both issues AND fix instructions
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R17

**Q18 (2026-03-30):** Confidence score badge on every page?
**A18:** Choice C -- No badge, per-field indicators instead
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R18
**Schema:** Verified `field_confidence JSONB` exists on companies and dossier_final

**Q19 (2026-03-30):** Track which facts came from which sources? Footnotes like academic papers?
**A19:** Choice A -- Yes, full source attribution
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R19
**Schema:** Added `source_attribution JSONB` to dossier_final, proposals, engagement_buyers

**Q20 (2026-03-30):** On page regeneration: show a diff of what changed?
**A20:** Choice A -- Yes, always show diff
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R20
**Schema:** Added `previous_version_diff TEXT` to page_versions

### Pipeline Orchestration

**Q21 (2026-03-30):** Buyer enrichment: 5 Exa searches per buyer -- parallel or sequential?
**A21:** Choice C -- 2 at a time (balanced)
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R21

**Q22 (2026-03-30):** New company enters pipeline -- minimum research before ANY page appears?
**A22:** Choice D -- Research + validation + certification all complete first
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R22

**Q23 (2026-03-30):** Research depth setting per deal?
**A23:** Choice C -- No, same depth for everything
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R23

**Q24 (2026-03-30):** SAP audit found 7 missing sections. Build all at once or prioritize?
**A24:** Choice A -- All 7 at once
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R24

**Q25 (2026-03-30):** Goal tracker per deal driving orchestrator priority?
**A25:** Choice A -- Yes, drives orchestrator priority
**Rule created:** RESEARCH-PIPELINE-RULES.md Rule R25
**Schema:** Created `deal_goals` table. Seeded Wieser: meetings_booked target=5 by 2026-12-31

### Skipped (3)
- Q4: Found buyer's VP Corp Dev on LinkedIn -- also search for direct email? (DEFERRED)
- Q10: Company has old deal_research data but NO new Exa research -- publish or force refresh? (DEFERRED)
- Q16: Dual-LLM certification -- what should the SECOND model be? (DEFERRED)

---

*This log is append-only. New sessions add entries below this line.*

## SESSION 4: Proposal Template Decisions (2026-03-30)

### Proposal Template V1 Adopted
**Decision:** Adopt the 10-section proposal template as our first master template.
**Rules:**
1. Lead with owner's outcome, not credentials (Rule 1)
2. 4-phase process with week timelines: Preparation (1-6), Marketing (7-14), Negotiation (15-22), Closing (23-36)
3. Trades language, not finance language ("your real profit" not "EBITDA adjustments")
4. Fee illustration table with 3 scenarios at different sale prices
5. Buyer funnel metrics (universe → outreach → NDAs → IOIs → LOIs)
6. Monthly retainer = engagement fee paid differently. Don't say "monthly" for now. Leave until client feedback.
7. DO NOT remove custom research, narratives, or general flow. ADD these sections alongside existing content.
8. No tail period/exclusivity in the proposal page (belongs in engagement letter)
9. No anonymous deal history (only real deals or omit)
10. Credentials section only with real data (leave blank until real testimonials exist)

### Implementation Rule
**CRITICAL:** When updating proposals, ONLY ADD. Never remove custom research, story narratives, EBITDA levers, buyer analysis, or any company-specific content. The template provides STRUCTURE. The existing content provides SUBSTANCE. Both are needed.

### MASTER BUSINESS RULE: 60-Day Deal Timeline
**Decision:** Total process from engagement to close is 60 days, not 6-9 months.
**Rationale:** Our pre-work, AI research, and agent-built buyer lists eliminate weeks of traditional preparation. First contact happens in Week 1 because buyer lists are already built.
**Timeline:**
- Phase 1 — Preparation & First Contact: Week 1 (research already done, buyers identified)
- Phase 2 — Active Marketing: Weeks 2-4 (outreach, NDAs, CIM distribution)
- Phase 3 — Negotiation: Weeks 5-7 (IOIs, management meetings, LOIs)
- Phase 4 — Closing: Weeks 7-9 (due diligence, purchase agreement, close)
- TOTAL: 60 days
**This is a competitive advantage.** Traditional brokers quote 6-9 months. We quote 60 days because the technology does in hours what they do in weeks.

---

## SYSTEM RULE: Universal Feedback Capability

**RULE:** Every page, every section, every element must have feedback capability.
The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
Any page generation engine that creates HTML must include `<script src="comment-widget.js"></script>` before `</body>`.
No exceptions. This is how we learn.

Additionally, all pages must include:
- `<script src="notification-bell.js"></script>` — notification bell widget
- `<script src="conflict-resolver.js"></script>` — conflict detection and resolution
- `<script src="version-widget.js"></script>` — version history slider

**Enforced in:** proposal_engine.py, company_hub.py, meeting_engine.py, dashboard.py
**Created:** 2026-03-28
**Authority:** Ewing Gillaspy

---

## FEEDBACK LOOP: Resolved Comments (Auto-appended by Step 14)

### Comment [2026-03-29 22:16]: mark on Air Control — valuation
**Comment:** Revenue is wrong. Fred told me on our last call they do $4.2M not $3M. He also mentioned they have 8 employees now, not 5.
**Type:** fact_correction
**Response:** Fred told me directly on our call March 28. He said $4.2M in 2025 revenue, 8 full-time employees including 2 new hires in January. I have the Fireflies transcript.
**Resolution:** Applied — Now I have the full picture. The valuation section uses $3M revenue / 5 employees / $600K EBITDA. With Fred's corrected numbers ($4.2M revenue, 8 full-time employees), I need to recalculate:

- Revenu
