# RESEARCH → PAGE PIPELINE DECISIONS — 2026-03-30

**Decided:** 22/25

---

## Search Strategy

### 1. Exa returns articles without actual CEO quotes — what next?
**Choice: D** — Search different source (SEC, investor decks)

### 2. Private companies have no earnings calls. What's the equivalent?
**Choice: E** — All of the above in priority order (owner interviews/podcasts, industry conferences, local press, industry data)

### 3. Include buyer COMPETITOR searches? Creates urgency in pitch.
**Choice: A** — Yes — 2 competitors per buyer

### 5. Different search templates per buyer type (PE vs strategic vs consolidator)?
**Choice: A** — Yes — 3 distinct templates

## Data Assembly

### 6. Conflicting data (Exa says 15 employees, deal_research says 45) — who wins?
**Choice: C** — Show both with sources

### 7. Slider fields (revenue, employees, com/res split) — default to estimate or blank?
**Choice: C** — Estimate if confidence > MEDIUM, blank if LOW

### 8. Story narrative minimum length? System generated 3K chars instead of 14K target.
**Choice: B** — Publish what it has + flag as thin

### 9. dossier_final vs proposals table have different revenue numbers — which is truth?
**Choice: A** — proposals table is canonical

## Page Population

### 11. Proposal page order: narrative → strengths → market → valuation → attack → timeline. Right order?
**Choice: A** — Current order is right (trust first)

### 12. Buyer 1-pager has 7 SAP sections. Show all even if some are thin?
**Choice: B** — Hide sections without enough data

### 13. Data room (client-facing): show methodology by default or hide behind expandable?
**Choice: C** — Admin: full. Client: expandable

### 14. EBITDA levers: show MISSING levers as red flags or only show strengths?
**Choice: C** — Strengths prominent, gaps in separate section

### 15. Attack plan: generic ("letters to top 10") or specific ("Letter to Charles Burckmyer at Culligan")?
**Choice: A** — Specific — SAP standard

## Quality & Certification

### 17. Certifier flags NEEDS_REVIEW — what does "instructive" look like?
**Choice: C** — Both: issues + fix instructions

### 18. Confidence score badge on every page? "72% confirmed, 18% estimated, 10% unknown"
**Choice: C** — No badge — per-field indicators instead

### 19. Track which facts came from which sources? Footnotes like academic papers?
**Choice: A** — Yes — full source attribution

### 20. On page regeneration: show a diff of what changed?
**Choice: A** — Yes — always show diff

## Pipeline Orchestration

### 21. Buyer enrichment: 5 Exa searches per buyer — parallel or sequential?
**Choice: C** — 2 at a time (balanced)

### 22. New company enters pipeline — minimum research before ANY page appears?
**Choice: D** — Research + validation + certification

### 23. Research depth setting per deal?
**Choice: C** — No — same depth for everything

### 24. SAP audit found 7 missing sections. Build all at once or prioritize?
**Choice: A** — All 7 at once

### 25. Goal tracker per deal? "Weiser: 2 of 5 meetings booked" driving orchestrator priority?
**Choice: A** — Yes — drives orchestrator priority

## PREVIOUSLY SKIPPED — NOW ANSWERED

### 4. Found buyer's VP Corp Dev on LinkedIn — also search for direct email?
**Choice:** Use Exa Websets or Clay.com enrichment. These methods already exist in our research_methods table. Phone + email enrichment is a contact-level cost, not a company-level cost.

### 10. Company has old deal_research data but NO new Exa research — publish or force refresh?
**Choice:** Audit old research data. If it passes quality check, don't rerun Exa. Save the money. Only re-research if quality score is below threshold or data is older than the refresh schedule (signed=weekly, pipeline=bi-weekly, unresponded=quarterly per Q28).

### 16. Dual-LLM certification — what should the SECOND model be?
**Choice:** Build a way to manage and monitor LLMs. We need to swap them if they underperform. Always have a list of LLMs available via OpenRouter. Keep optimizing based on data and performance. This means: create an LLM registry table, track per-model performance (quality scores, latency, cost, error rate), and the system picks the best model for each task dynamically.

**Decided: 25/25 ✅**
