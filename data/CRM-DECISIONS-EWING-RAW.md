# CRM DECISIONS — 2026-03-30

**Decided:** 97/97

---

## HARD — Only You Can Answer

### Q1. HVAC company + family office investor: NC or AND Capital?
**Answer:** 1. NC always if there is a next chapter fit. Investors in big funds likely aren't buying HVAC companies. 2. Family office in this case is a potential buyer of another HVAC company that we can go get an agreement for that company and take them to this buyer. 3. Yes, but this is a major exception and will require user intervention and decision. The system should never assume a NC fit lead in any way is an AND capital lead. always Next Chapter first. And is never automated

### Q15. Buy-side clients (Weiser, Design Precast) — what does the "proposal" look like?
**Answer:** 1. Targets are companies to buy that meet their desired criteria. We need to add to any first meeting with a buy-side client the criteria selectors for their industry. On this page we need the ability to add criterion ad-hoc, fill in the answer, and this should push back to the engines that search and find companies for weiser. For instance, weiser might say, "Find me companies in Iowa that have their own concrete plant (which can be seen from google earth), and serves industrial and civil clients undergrown with pipe and product.
2. It is a match-making pitch with a fee of 2% to 3% success fee. It is a pitch to show them that we can do the work efficiently and effectively. It shows them that we can "pitch their narrative" in a way that hooks people to want to sell their business to that narrative. That's why narrative is so important for both buy side and sell side. In this case the narrative is "why sell to Weiser".
3. We are sourcing targets and also taking suggestions from them of companies they already know they want to buy. When we do get client input, we need to use that as training to inform our searches and research agents that we have lookalikes to use to enhance our fit score.

### Q19. Buy-side: "all about the targets" or "all about the buyer's growth strategy"?
**Answer:** 1. How this fits your selection criteria, and what they probably think they are worth, and what ebitda levers they score positively and negatively against
2. Buy side clients just want to buy a company to capture ebitda, market share, and add locations served. It's not necessarily a "growth strategy" as much as it is "a contract to help us identify and negotiate with a company to buy"
3. No, this is not a mckinsey or BCG project. They already want to buy a company. We are filling the order, not changing their strategy. We may enhance this later, but not now.

### Q27. Buy-side: how do you source acquisition targets?
**Answer:** 1. Phone calls, letters in the mail, emails, invites to lunch, networking through common connections, public listings. 
2. Age, years in business are good but I need to build a separate agent that identifies and acquires buying signals by watching these companies over time. Perhaps apify on the company instagram account is one tactic that we should explore.
3. Weiser wants 5 vetted targets set up on his calendar ready to deal make with him and sell their business this year.

### Q33. 30/60/90 timeline — who executes each step?
**Answer:** 1. We use APIs in agents to send them automatically. Right now we have sent 50 letters by hand, and 12 of them called us on our cell phone upon receipt.
2. Yes, salesfinity is always the calling system, it records and gives us leverage of time.
3. I used linked Helper on desktop for now. I need manual instructions for lists to load, campaigns to create. I need a linkedin sub-agent master that is always telling me to load new connection request campaigns that coincide with attack plans. This could be part of orchestration agent.
4. Individual letters that go in the mail, with custom researched information threaded in nicely.

### Q38. Competitive situations — how aggressive?
**Answer:** 1. Yes, we need to urgently build the attack plan with detailed research. That's what is going to set us apart. Not an email that promises to deliver great service. that doesn't mean anything.
2. No need to directly address competition. But emphasize, "we can dial this list tomorrow"
3. We walk away when we get a message that says there is no longer an opportunity.

### Q39. Guarantee structure for different deal sizes?
**Answer:** 1. The fee should be $10k minimum and 10% of the transaction unless the business value and transaction commission would be $500k or more at 5% success fee. The smaller ones we have to charge more.
2. fixed dollar for engagement fee to pay for data and calling. success fee % that slides with deal size.
3. Buy side deal fees are normally 2-3%. Sell-side is normally 5%-7%. Engagement fees are separate

### Q61. Primary feedback provider — Mark or Ewing?
**Answer:** 1. yes. learn patterns from each. Mark is the wordsmith, final copywriting reviewer. Ewing is the system architect. But only Ewing has closed any transactions. Mark never has. So right now we need to slightly lean towards Ewing on the "content structure, layout, and components" and lean towards Mark on the english, words, facts, and final ready to send conclusion.
2. Final say will usually be Mark because he works downstream from Ewing.
3. Yes, learn patterns from each realizing each person's role.

### Q81. Web server internet-accessible?
**Answer:** 1. Clients must access this data room. This is not a local application. That will not serve our needs. 
2. Same local network.
3. Clients need public URLs. email gating is fine. Passwords can default to their website domain name.

### Q82. Authentication story?
**Answer:** 1. Clients too.
2. Login eventually, but for now make them wide open.
3. No, same permissions. We are both admins that need to provide feedback.

### Q86. Maximum daily spend across all entities?
**Answer:** 1. Monthly ceiling for now set to $500. Send alerts when crossing every $50 milestone. Send to slack and SMS.
2. Yes this is realistic but doesnt seem accurate for exa.
3. see answer to #1. Let's work monthly and by $50 increments for notifications. 
*put a note that we need to build a cost monitoring agent or add to the orchestration agent. Something needs to be checking methods used vs. methods available when costs start adding up beyond our expectations. For instance recently we found that exa was called 6,000 times in one day because downstream agents were failing and upon reset, we ran exa again even though we had the data.

### Q91. Listener channel priority — if only ONE?
**Answer:** 1. This will come from salesfinity transcripts.
2. We lose at list building, proposal creation, and engaging lists efficiently with letters and phone calls - the only two methods that worked for us so far. Email and linkedin are distant in effectiveness based on our findings thus far. It could just be we are bad at these tools and messaging.
3. Salesfinity and email are both a MUST. this is where we do 90% of our communication. We will also see a lot of signal from fireflies. These are the exhaust pipes. Email, salesfinity, fireflies.

### Q96. Research transparency — internal or external?
**Answer:** 1. This is a great tactic. We should build this in. They love knowing. 
2. This is a great tactic. Yes we should add it.
3. Transparency is baked in throughout. It builds trust. We lead with transparency, methodology, research, rigor, precision. all the way through.

### Q99. Minimum viable data room — what's the floor?
**Answer:** 1. We send nothing today. We need a page to send them that's part of our file on them, which then gives them the ability to poke around and see what we know about them. This is an opportunity to delight them majorly.
2. They want to see who we are, who we represent (if buy side), what we do that separates us from other brokers, a little bit about our success history, and our plan to help them achieve their goals.
3. Interactive is very key. It creates the engagement. Static doesnt allow us to get feedback from what they changed. When the clients change the data or sliders, we need to store that so we learn from their behavior. This is data we don't have to acquire on a phone call. That's why it's so valuable.

### Q100. When is NC "done enough" for AND Capital & RevsUp?
**Answer:** 1. represeting businesses to sell.
2. No, and capital is a distant 2nd to next chapter in focus right now.
3. Make sure their data is coherent, organized, attack lists are built, and research engines are ready to audit what we already built for 100s of companies. It's all in the supbase tables, but nobody has ever pulled it all together.

### Q62. Differentiate learning from Mark vs Ewing?
**Answer:** 1. yes. 
2. yes. 
3. No. We both swarm to everything client facing for now.

## NUANCED — Pick A, B, or C

### Q3. Multi-entity people (Mark spans all 3): classify by CAMPAIGN or CONTENT?
**Choice: C** — Hybrid (rec'd)

### Q4. Entity transitions (NC deal becomes AND investment)?
**Choice: C** — Dual-tag (rec'd)

### Q6. "Smallest entity first" vs urgency?
**Choice: B** — Urgency always first

### Q8. DNC list include "soft DNC"?
**Choice: C** — Binary + inbound exception (rec'd)

### Q12. How often regenerate profiles?
**Choice: C** — Trigger + 24hr cooldown (rec'd)

### Q14. Minimum data completeness for "ready" profile?
**Choice: B** — 70% (rec'd)

### Q17. Wrong valuation: deal-killer or conversation-starter?
**Choice: C** — Range + framing (rec'd)

### Q18. Multiples vary by geography, size, recency?
**Choice: B** — Full segmentation

### Q20. Revenue from employee count — margin of error?
**Choice: B** — Only with corroboration (rec'd)

### Q25. Owner-operators — special handling?
**Choice: B** — Treat normally (rec'd)

### Q26. How many buyers per deal?
**Choice: C** — Adaptive by vertical

### Q29. Multi-deal buyers: coordinated or independent?
**Choice: B** — Coordinated (rec'd)

### Q30. Buyer declines — remove from ALL lists?
**Choice: B** — That deal only (rec'd)

### Q35. Buyer responds positively — what triggers next stage?
**Choice: C** — Multi-signal

### Q46. Live calls — what data pushed to screen?
**Choice: B** — Smart card (rec'd)

### Q47. Post-meeting outcomes — how captured?
**Choice: B** — Transcript analysis (rec'd)

### Q49. Back-to-back meetings with different companies?
**Choice: B** — Context-switch alerts (rec'd)

### Q52. Dashboard revenue metrics?
**Choice: B** — Pipeline + fees (rec'd)

### Q57. Budget alert threshold?
**Choice: C** — Anomaly-based

### Q63. Feedback propagate to similar companies?
**Choice: B** — Suggest, don't auto-apply (rec'd)

### Q65. Pause auto-learning to prevent rule bloat?
**Choice: B** — Pause at 30 rules (rec'd)

### Q71. Human review % before auto-approval trusted?
**Choice: B** — Per-vertical graduation (rec'd)

### Q73. Review queue SLA?
**Choice: B** — 24hr + escalation (rec'd)

### Q74. Dual-LLM certification worth it at scale?
**Choice: A** — Always dual

### Q76. Queue items per day at target scale?
**Choice: B** — 200/day (rec'd target)

### Q87. Budget caps: per-company or per-entity?
**Choice: B** — Per-company within entity (rec'd)

### Q92. Auto-trust thresholds vary by entity?
**Choice: C** — Stake-based

### Q93. Listener unknown situation: speed or quality?
**Choice: C** — Tier by urgency (rec'd)

### Q95. Contradictory signals — how resolved?
**Choice: B** — Source hierarchy (rec'd)

## EASY — Approve or Override

### Q2. Classifier auto-reclassify human-tagged record?
**APPROVED** — No. Human always wins. Log disagreements. Add manually_tagged boolean — classifier skips those.

### Q5. Confidence floor below which pipeline STOPS?
**APPROVED** — Yes. Floor = 1.5 → human_review_queue. No downstream work. Current 2.0 LLM fallback is fine.

### Q7. New reps: auto-detected or manual?
**APPROVED** — Manual for now. person_routing table. New name → human_review_queue. Phase 2: auto-suggest.

### Q9. Companies in multiple verticals?
**OVERRIDDEN** — Next chapter wins, followed by Revsup. AND is last

### Q10. Entity classification visible to client?
**APPROVED** — No. Internal only. Clients see "Next Chapter Advisory" branding.

### Q11. Mark says $5M, Exa says $2.25M — who wins?
**APPROVED** — Human wins. Flag discrepancy: store both with source. "$5M (owner-reported)" + footnote.

### Q13. Field confidence indicators?
**APPROVED** — Yes. CONFIRMED / ESTIMATED / UNKNOWN. Admin sees labels. Client sees data with footnotes.

### Q16. Quality 50-79 — proposals to clients?
**OVERRIDDEN** — Sits in needs review with explicit details of issues and what to manually research. make it instructive

### Q21. Track estimate accuracy?
**APPROVED** — Yes. estimate_accuracy table. Log deltas on human correction. Monthly aggregate.

### Q22. Two LLMs disagree on a fact?
**OVERRIDDEN** — Ether human picks winner or agent using another LLM picks winner. Over time we want agent. But need to find a way to inject the human to provide training without grinding the process to a halt on every record

### Q23. Show methodology on every page?
**APPROVED** — Yes. This IS the brand. Admin: full methodology. Client: lighter version.

### Q24. Sensitive verticals — extra restrictions?
**APPROVED** — No. Existing guardrails sufficient. HIPAA/SEC case-by-case.

### Q28. Buyer research refresh?
**OVERRIDDEN** — Signed engagements, weekly, deal in pipeline bi-weekly, deals unresponded quarterly.

### Q34. DNC'd buyers in client view?
**OVERRIDDEN** — Buyers see DNC with reason given. We need full disclosure to keep them up to speed

### Q36. Buyer fit scores visible to clients?
**OVERRIDDEN** — yes, visible to clients. This is a service to them.

### Q37. Flag buyer who completes acquisition?
**APPROVED** — Yes. "Active Acquirer" flag. INCREASES fit score. Move UP.

### Q40. Auto-detect buyer acquisitions?
**APPROVED** — Yes. Monthly Exa scan. Log to buyer_activity. Auto-flag + notify.

### Q41. Meeting prep timing?
**APPROVED** — 24 hours before. Regenerate if new data arrives. Orchestrator checks calendar daily.

### Q42. Meeting pages phone-optimized?
**APPROVED** — Yes. Key points top, collapsible sections, large taps, no horizontal scroll.

### Q43. Joint meetings — role assignments?
**APPROVED** — Yes. "Ewing: relationship, big picture. Mark: operational, process."

### Q44. Reschedule → regenerate prep?
**APPROVED** — Yes. New data may exist. Keep old version in page_versions.

### Q45. iMessage prep 30 min before?
**OVERRIDDEN** — Yes. Summary: "Meeting with {company} in 30 min. Key: {5 bullets}. Full: {link}."

### Q48. Meeting type: enum or free text?
**OVERRIDDEN** — Let's review this further and nail this down. This is the architecture of the meeting page. We need to build a meeting page template. Flag this in our todo list.

### Q50. Meeting pages — competitive intel?
**APPROVED** — Yes if available. Who else is talking to prospect, brokers in market, prior M&A.

### Q51. Dashboard as landing page?
**APPROVED** — Yes. Pipeline, reviews, problems, budget, quick links. Companies to sidebar.

### Q53. Dashboard system health?
**APPROVED** — Yes. Orchestrator/worker/watchdog status. Green/yellow/red. Red if worker down > 15min.

### Q54. Mobile dashboard?
**APPROVED** — Yes. Monday morning from bed. Responsive, key metrics top, collapsible.

### Q56. Dashboard entity filters?
**APPROVED** — Yes. [All] [NC] [AND] [RU] + person presets. Cookie-stored.

### Q58. "While you were away" summary?
**APPROVED** — Yes. Changes since last login. Track last_viewed_at.

### Q59. Dashboard refresh frequency?
**APPROVED** — Live on page load. Fresh queries. Auto-refresh meta tag every 5 min.

### Q60. System confidence metric?
**APPROVED** — Yes. "Data Quality: 72% confirmed, 18% estimated, 10% unknown."

### Q64. Feedback vs guardrails — who wins?
**OVERRIDDEN** — Guardrails. Always. Only Ewing overrides by updating North Star. Flag to ewing when the system wants to color outside gaurdrails. keep this log for a weekly review. publish hourly. put on dashboard as a feed/section

### Q66. Version history depth?
**APPROVED** — Last 10 per page. Older → archive table (queryable, not in UI).

### Q67. Edit = auto-create version?
**OVERRIDDEN** — Yes. Every edit = new version. Pre-edit preserved. Cheap, invaluable. However, ask the user before re-generating, they may have other edits on the same page.

### Q68. Version history visible to clients?
**APPROVED** — No. Current only. Revisions signal uncertainty.

### Q69. Rule change → rebuild 20 pages?
**APPROVED** — Lazy. Mark stale, rebuild on view. Active engagements: background rebuild within 1hr.

### Q70. Version-level commenting?
**APPROVED** — Yes. One optional text field: "Why was this changed?"

### Q72. Certifier approves, Mark disagrees?
**APPROVED** — Mark wins. Reverts to needs_review. 3 overrides → rule proposal for certifier.

### Q75. Pre-certification quick check?
**APPROVED** — Yes. 5-point code check before LLM. Fail = skip cert, route to human.

### Q77. Orchestrator: entity or urgency priority?
**APPROVED** — Urgency first, entity second. Round-robin within tiers.

### Q78. Orchestrator down 4hr — burst or pace?
**APPROVED** — Pace at 2x. No bursting. catch-up flag when backlog > 20.

### Q79. Maintenance mode?
**APPROVED** — Yes. active/maintenance/paused. Orchestrator stops, worker finishes, watchdog runs.

### Q80. 5min orchestrator / 10sec worker correct?
**APPROVED** — Yes. No change.

### Q83. Keep static HTML alongside server?
**APPROVED** — Yes. Offline backup, email attachments, PDF gen. Server primary, files backup.

### Q84. Multiple simultaneous users?
**APPROVED** — Flask or FastAPI. Multi-threading. Writes go through queue.

### Q85. WebSockets needed?
**APPROVED** — No. Page refresh + auto-refresh every 5 min.

### Q88. Budget exhausted — queue or skip?
**APPROVED** — Queue for tomorrow. deferred_until timestamp. No work lost.

### Q89. API key expiration alerts?
**APPROVED** — Yes. Weekly health check. 401/403 → iMessage alert.

### Q90. Deployment process?
**APPROVED** — Manual git pull. Phase 2: deploy script. Phase 3: webhook. No CI/CD yet.

### Q94. Listener scan historical on deploy?
**APPROVED** — No. Start fresh. Historical = flood of stale plays.

### Q97. Show failed research?
**APPROVED** — Yes internally, no externally. Admin sees attempts. Client sees wins.

### Q98. Research cost visible to clients?
**APPROVED** — No. "$0.15" kills premium positioning. Internal metric only.
