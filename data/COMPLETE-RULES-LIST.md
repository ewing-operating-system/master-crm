# COMPLETE RULES LIST — Master CRM + Dossier Pipeline

**Extraction Date:** 2026-03-28
**Sources:** 10 files across master-crm and dossier-pipeline
**Extracted By:** Argus (Claude Opus 4.6)

---

## RESEARCH METHODS (every search query, API call pattern)

**R1.** Exa company search — query template:
```
{company} {city} {state} owner founder interview
```

**R2.** Exa reputation search — query template:
```
{company} {city} reviews reputation culture
```

**R3.** Exa services search — query template:
```
site:{domain} about team services
```
Fallback when no website: `{company} {vertical} services {city} AZ`

**R4.** Exa financials search — query template:
```
{company} {city} AZ revenue employees BBB profile
```

**R5.** Exa LinkedIn search — query template:
```
{company} linkedin company {vertical} {state}
```

**R6.** Exa contact enrichment search — query template:
```
"{owner}" "{name}" {city} {state} phone email contact LinkedIn
```

**R7.** Exa proposal gap-fill — company search:
```
{company} {city} {state} {vertical} company
```

**R8.** Exa proposal gap-fill — owner search:
```
{company} owner founder president {city}
```

**R9.** Exa proposal gap-fill — size search:
```
{company} {city} employees revenue size
```

**R10.** Exa search API call pattern:
```python
POST https://api.exa.ai/search
Headers: x-api-key, Content-Type: application/json
Payload: {"query": query, "num_results": 5, "type": "auto",
          "contents": {"text": {"max_characters": 3000}}}
Cost: $0.006/result
```

**R11.** Clay contact enrichment API call pattern:
```python
POST https://api.clay.com/v1/people/enrich
Headers: Bearer token
Payload: {"first_name": first, "last_name": last, "company_name": name,
          "company_domain": domain, "city": city, "state": state}
Cost: 14 credits * $0.016/credit = $0.224/call
```

**R12.** OpenRouter multi-model LLM call pattern:
```python
POST https://openrouter.ai/api/v1/chat/completions
Headers: Authorization: Bearer token, HTTP-Referer, Content-Type
Retry: exponential backoff [15s, 30s, 60s] on 429
Timeout: 180s
```

**R13.** Claude CLI call pattern (primary, $0.00):
```python
subprocess.run(["claude", "-p", "--output-format", "text"],
               input=prompt, capture_output=True, text=True, timeout=300)
```
MUST pipe via stdin. NOT as CLI args (15K+ chars timeout).

**R14.** Ollama local LLM call pattern:
```python
POST http://localhost:11434/api/chat
Model: mistral-small, stream=False, timeout=600s, cost=$0.00
```

**R15.** Supabase REST API pattern:
```python
Headers: {"apikey": KEY, "Authorization": f"Bearer {KEY}",
          "Content-Type": "application/json", "Prefer": "return=representation"}
GET: urllib.request.Request(url, headers=sb_headers())
INSERT: POST with Prefer: return=representation
UPSERT: POST with Prefer: return=representation,resolution=merge-duplicates
UPDATE: PATCH with URL-encoded filter ?target_id=eq.{id}
```

**R16.** Salesfinity call log API pattern:
```
GET https://client-api.salesfinity.co/v1/call-log
Headers: x-api-key: sk_ff45bc29-e5c1-4a3f-b1e5-f9776d94cbe7
Pagination: 100/page, 10,535+ records
JSON quirk: use json.loads(data, strict=False) for control chars
```

**R17.** Contact extraction regexes from Exa results:
```
Email: [\w.+-]+@[\w-]+\.[\w.-]+ (excludes example, test, noreply, sentry, webpack)
Phone: (?:\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4} (10-11 digits)
LinkedIn: URL containing linkedin.com/in/
Address: \d+\s+[\w\s]+(?:St|Ave|Rd|Blvd|Dr|Ln|Way|Ct|Pl|Cir|Loop|Pkwy|Hwy)\.?[^,]*,\s*[\w\s]+,?\s*[A-Z]{2}\s*\d{5}
```

**R18.** Researcher prompt — extraction from web results:
```
You are researching {company}, a {vertical} company in {city}, {state}.
CRITICAL: Every fact MUST include source_url, source_type, search_query, source_excerpt.
Return JSON with: company_name, owner_name, owner_title, owner_quotes, company_story,
culture_signals, services, differentiators, reviews_summary, avg_rating, review_count...
```

**R19.** Validator prompt — dual-LLM fact-check:
```
You are a fact-checker validating research about {company}.
For EACH claim: check source_url exists, check plausibility, flag fabrications.
Return: facts_verified, facts_flagged, flags[], verified_data, confidence_score
```

**R20.** Synthesizer prompt — narrative generation:
```
Write intelligence narrative about {company}, a {vertical} company in {city}, AZ.
BLOCKLIST: do NOT use flagged claims.
Return: executive_summary, owner_profile, company_narrative, competitive_moat,
acquisition_appeal, risk_factors, cold_call_opener, key_quotes, narrative_score
```

**R21.** Valuator prompt — M&A valuation estimate:
```
Value {company}, a {vertical} company in AZ for M&A.
Return: ebitda_estimate, multiple_range, ev_estimate, active_buyers,
value_drivers_present, value_detractors_present, letter_worthy, valuation_score
```

**R22.** Certifier prompt — final quality audit:
```
Certify dossier for {company}. Verify sourced. Check flags respected.
Score completeness. Catch hallucinations. Write cold call opener.
Return: verdict (APPROVED/NEEDS_REVIEW/REJECTED), completeness_score,
hallucination_count, certified_cold_call_opener, final_score
```

**R23.** Letter writer prompt — personalized certified mail:
```
Write letter from Mark DeChant to {owner} at {company} in {city}, AZ.
Rules: reference specific verified facts, include valuation range,
respectful tone, CTA with personalized URL, 300-400 words.
Return: letter_text, hook_fact_used, hook_source_url, personalized_url_slug
```

**R24.** Outreach prompt — full multi-channel suite:
```
Generate: cold_email_subject, cold_email_body, handwritten_letter,
linkedin_message, cold_call_script, direct_mail, outreach_sequence,
lead_with, avoid
Sign EVERY piece as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668
```

**R25.** Proposal engine mega-prompt:
```
Generate complete JSON proposal: company_narrative, top_3_strengths,
market_analysis, valuation_range, buyer_profile, attack_plan,
outreach_strategy, letter_template, call_script, linkedin_message,
timeline, risk_factors, differentiators, quality_score
FOUNDER GUARDRAILS: ALL ABOUT THEM, disclose methodology, NO negative facts
```

**R26.** Profile engine prompt:
```
Build structured company profile JSON with: financials (revenue, EBITDA, SDE
with methodology), operations, revenue_mix, revenue_sources, top_3_strengths
(with evidence and why_it_matters_to_buyers), valuation, market_position,
owner_profile, quality_score, data_completeness_pct
```

**R27.** Engagement engine per-buyer outreach prompt:
```
Generate outreach for contacting potential BUYER about acquiring {company}.
Frame as "we represent the owners" -- NEVER "this company is for sale"
Return: letter (200w), email (150w), call_script (100w), linkedin (50w)
```

**R28.** Engagement engine timeline prompt:
```
Create 30/60/90 day execution timeline for selling {company}.
Days 1-7: letters to top 10 | 7-14: follow-up calls | 14-21: LinkedIn |
21-30: emails, second calls | 30-60: meetings, NDAs | 60-90: LOI, DD prep
```

---

## DATA ASSEMBLY RULES (how data flows from source to page)

**D1.** Company data assembly priority order: companies table > targets table (extra_fields) > dossier_final > deal_research > contacts table. Each source fills gaps without overwriting existing data.

**D2.** Profile engine merge priority: known_data (live input) > proposal data > dossier data > companies table. Newer/richer data wins.

**D3.** Exa enrichment triggers only for missing critical fields: revenue, employees, services, owner_name, year_founded. If all present, skip Exa entirely.

**D4.** Market multiples loaded from `data/data-export/market_multiples.json`. Fallback to hardcoded defaults per vertical: HVAC 3.5-7.0x, plumbing 3.0-6.5x, water treatment 4.0-8.0x, pest 4.0-9.0x, etc.

**D5.** Proposal HTML is saved to both Supabase (proposals.proposal_html) and local file (`data/proposals/{slug}.html`). Slug = company name lowercased, spaces to hyphens, commas/periods removed, max 30 chars.

**D6.** Profile data flows to: companies table (vertical, city, state, employee_count, year_founded) AND intelligence_cache (full profile JSON under key 'company_profile').

**D7.** Engagement plan stored in intelligence_cache under key 'engagement_plan' linked to company_id.

**D8.** Personalized URL format: `https://nextchapter.deal/{slug}` where slug = company name lowercased, spaces to hyphens, commas and periods removed.

**D9.** Dossier_final is updated incrementally after EVERY pipeline step, not just at the end. Never wipe records.

**D10.** Research cache: check dossier_runs before calling Exa. Never re-research a company that already has results.

**D11.** Every fact in customer-facing content must trace back to: source_url, source_type, search_query, source_excerpt. No provenance = does not exist.

**D12.** Engagement buyers get: fit_narrative (first 500 chars of story_narrative), approach_strategy (call_opener), one_pager_json (full story_narrative + revenue + notes + business_strength).

**D13.** Contact data from buyer_targets JSON flows to contacts table with: full_name, first_name, last_name, title, linkedin_url, company_id (created if not exists), source='deal_research_migration'.

---

## BUSINESS RULES (fee structures, engagement terms, entity routing)

**B1.** Three entities: Next Chapter (next_chapter) = boutique M&A for home services; AND Capital (and_capital) = PE fund management + LP fundraising; RevsUp (revsup) = contingent recruiting for SaaS revenue roles.

**B2.** Entity classification uses Intent-First Routing: (1) Intent > (2) Company Type > (3) Person Role > (4) Channel/Campaign. Never classify by folder location, tool, or data source.

**B3.** Classification decision tree: Step 0 = clear action? Step 1 = hiring? (RevsUp). Step 2 = buying/selling business? (Next Chapter). Step 3 = investing/capital? (AND Capital). Step 4 = company-type fallback. Step 5 = M&A intermediary logic. Step 6 = multi-signal conflict resolution.

**B4.** Fail-safe rules: RevsUp ONLY if hiring present. Next Chapter ONLY if transaction happening. AND Capital ONLY if capital involved. If none apply, NO TAG. Do NOT force classification.

**B5.** Confidence scoring: strong signal (explicit intent) = +2, moderate (industry match) = +1, weak (keyword only) = +0.5. Tag only if score >= 2.

**B6.** People routing: Ewing = AND + NC only, NEVER RevsUp in Salesfinity. Mark = all three, classify by WHAT he's doing. John Kelly = NC + RU only, NEVER AND Capital. Chris Rex = AND only, invisible to this workspace.

**B7.** Fee disclosure modes: (1) none = early outreach, (2) framework_only = first meetings, (3) median_market_disclosure = follow-ups, (4) proposed_working_fee = proposals, (5) interactive_models = premium proposals.

**B8.** Next Chapter fee: success fees on closed M&A transactions. AND Capital fee: 2% management, 20% carried interest, 8% preferred return. RevsUp fee: flat search fee + % salary + 6-month success fee.

**B9.** Entity priority order: RevsUp first, Next Chapter second, AND Capital third. Smaller sale comes first. Earn trust, then expand. Never pitch two entities simultaneously on first contact.

**B10.** Competitor response: IMMEDIATE escalation (priority CRITICAL). Compile industry package. Generate risk-free offer: "90 days, no fee, 2 qualified buyers or we fire ourselves." Never auto-execute competitive responses.

**B11.** CII partnership: ~1,500 buyer network. NC decides per-deal whether to engage CII. CII is a contracted partner, not employee.

**B12.** Deal side framing: sell-side = "We seek to bring you qualified buyers." Buy-side = "We represent a buyer looking for businesses like yours." Represent-side = "We help owners like you navigate an exit on your terms."

**B13.** NEVER say "private equity." Use: "former business owners who cashed out and buy companies because they believe in owners, not the stock market."

**B14.** Engagement threshold: 3 emails + 2 calls + 1 letter with no response = mark exhausted.

**B15.** Buyer outreach framing: "we represent the owners" -- NEVER "this company is for sale" (destroys leverage).

**B16.** AND Capital two fund verticals: Health & Wellness Innovation Fund (GP: Denise Brown, MD) and Energy Transition Fund (GP: Joe Park). $10B+ in prior transactions.

**B17.** 17 campaigns pre-seeded with entity prefix naming: NC-SELL-LETTER, NC-SELL-CALL, NC-BUY-OUTREACH, NC-TRANSCRIPT, NC-TAM, AND-LP-LETTER, AND-LP-CALL, AND-LP-LINKEDIN, AND-DEAL-SOURCE, AND-FUND-DISTRO, RU-CLIENT, RU-CANDIDATE, RU-REFERRAL, FORGE-BOOMERANG, BIOLEV-SALE, SEASWEET-ROOFING, PEC-FRAUD.

**B18.** PEC-FRAUD campaign: NEVER automate. Manual only.

**B19.** Next Chapter target verticals: plumbing, HVAC, roofing, pest, water treatment, flooring, concrete, steel, precast (operating businesses), HR services, air quality/environmental.

**B20.** AND Capital target verticals: hospitals (rural, critical access, specialty), medical devices, health-tech, bio-tech, med-tech, longevity, functional beverages, wellness properties, energy (hydrocarbons, midstream, renewables, critical minerals).

---

## QUALITY RULES (verification, certification, quality gates)

**Q1.** Multi-agent double verification: every fact in customer-facing content confirmed by two independent LLMs from different model families. Certifier must REJECT if any fact lacks dual-LLM verification.

**Q2.** Minimum data threshold for letters: company_name + owner_name + city + at least ONE of (revenue estimate, employee count, years in business). OR the letter does not generate.

**Q3.** Insufficient data cascade: Quality >= 80 = full personalized. 50-79 = honesty frame ("We couldn't find much about your company online, which usually means you're running a tight ship..."). 30-49 = industry education. < 30 = skip entirely. NEVER send low quality.

**Q4.** Deal killers (trust destroyed permanently): (1) Hallucinated personalization — wrong company/owner/city. (2) Wildly inaccurate estimates. (3) Sending with nothing to go on pretending it's personalized.

**Q5.** You can't grade your own homework. Validator never runs on same model as researcher. Researcher = Mistral Small (local). Validator = DeepSeek + Llama (remote). Different families, independent judgment.

**Q6.** Revenue/EBITDA estimates need 2+ corroborating signals.

**Q7.** Owner quotes need exact source URL. No paraphrasing.

**Q8.** Claims contradicted by another source = HIGH severity.

**Q9.** All data from single source = MEDIUM severity.

**Q10.** Owner name flagged as possible pseudonym = MEDIUM severity.

**Q11.** Self-reported claims presented as verified = LOW severity.

**Q12.** Never approve a dossier with HIGH severity flags unresolved.

**Q13.** Never remove a flag because data "seems right" -- flags require source evidence to clear.

**Q14.** Dual validator merging: pick validator with MORE flags as winner, then union unique flags from loser.

**Q15.** Nothing sends until human approval. Everything stays DRAFT.

**Q16.** Never use unverified data in customer-facing content. Only APPROVED or NEEDS_REVIEW with caveats.

**Q17.** Never treat a Google Maps business phone as an owner's cell phone.

**Q18.** Every document logged in sent_log with content_hash and provenance snapshot.

**Q19.** Letter must be 300-400 words.

**Q20.** Letter must reference specific verified facts, include valuation range, respectful/knowledgeable tone, "this person actually researched us" feeling, CTA with personalized URL.

**Q21.** When estimating or calculating, ALWAYS disclose methodology: "Since it's hard to find information about you, I used industry standard [formula]." Education is king.

**Q22.** Speed gated by quality: Quality >= 80 AND hot = within 1 hour. Quality 50-79 OR warm = same business day. Quality < 50 = hold for human review.

**Q23.** Auto-trust: 10 consecutive human approvals with zero edits before a play can auto-execute. ANY edit resets count to zero. Auto-execute always runs final inspection agent. If inspection FAILS, falls back to draft. If human REJECTS, resets permanently.

**Q24.** JSON parse strategy (triple fallback): (1) direct json.loads, (2) strip markdown fences then parse, (3) regex extract first {...} then parse. If all fail, return parse_error with raw_text.

**Q25.** JSON parse retry: if first attempt fails, retry with strict "Return ONLY valid JSON" instruction appended.

---

## PIPELINE RULES (ordering, sequencing, what comes before what)

**P1.** Main pipeline waterfall: Research > Validate > Synthesize > Valuate > Certify > Letter. Status: PENDING > RESEARCHED > VALIDATED > SYNTHESIZED > VALUED > CERTIFIED > LETTER_DRAFTED > APPROVED.

**P2.** Steps 1-3 (Research, Validate, Synthesize) are fatal on failure -- abort the company. Steps 4-6 (Valuate, Certify, Letter) can fail non-fatally.

**P3.** Letters send BEFORE phone calls. Enrichment (cell + email) is post-letter investment, not pre-letter gate.

**P4.** Enrichment waterfall: Exa contact search first. Clay is fallback only when Exa finds no phone. Clay fires when: no phone from Exa AND no phone_main AND no phone_direct on record.

**P5.** After enrichment branching: letter-only (no cell/email), letter+call (verified cell = Salesfinity queue), letter+email (verified email = generate email), letter+call+email (full sequence).

**P6.** Never process companies in parallel. One at a time, sequential waterfall. M4 24GB hardware constraint.

**P7.** Never skip the Validator. Every dossier must pass through the Trust Layer.

**P8.** 10-second delay between companies for API breathing room.

**P9.** Stop entire pipeline if errors exceed 10 consecutive failures.

**P10.** Resume from any step: reads dossier_final.dossier_status to know where to pick up.

**P11.** Never overwrite existing contact data. Only fill empty fields.

**P12.** is_step_done() before every API call -- never duplicate spend.

**P13.** Claude CLI ($0.00) for all quality-critical work. Paid APIs for fast extraction only.

**P14.** If Claude CLI fails: DUAL fallback -- both OpenAI AND DeepSeek run the same prompt, cross-check results. Prefer the one that parses as clean JSON; otherwise use the longer response.

**P15.** Error isolation: one target's failure is logged and skipped, pipeline keeps going.

**P16.** Rate limit awareness: detect 402/403/429, pause, report, continue.

**P17.** Circuit breaker: opens after 3 consecutive failures. Provider disabled for 5 minutes.

**P18.** Sliding window rate limiter: 60-second window, enforced per provider RPM limit.

**P19.** Provider budgets per session: Together $4.50, OpenAI $5.00, DeepSeek $10.00, Claude unlimited (free).

**P20.** Prompt truncation at max_context_chars with "[TRUNCATED]" marker.

**P21.** Engagement activation sequence: load proposal > load buyer list > DNC check all buyers > generate per-buyer outreach scripts (top 10) > generate 30/60/90 timeline > generate account plan > update proposal status to engagement_active.

**P22.** DNC check in engagement: check phone against do_not_call, check company_name with block_company=true. Any match = buyer blocked.

**P23.** Proposal engine sequence: assemble data from master-crm > enrich gaps with Exa > load market multiples > check minimum data threshold > generate content via Claude CLI > parse JSON > generate HTML > store in Supabase.

**P24.** Profile engine sequence: pull from companies > targets > dossier_final > proposals > merge all sources > generate profile via Claude CLI > store in companies table + intelligence_cache.

**P25.** 8 stages of Next Chapter lifecycle: Discovery > First Contact > Qualification > Proposal > Engagement Setup > Buyer/Seller Outreach > Deal Management > Close + Post-Close.

**P26.** Cost tracking: NC $5/day cap, AND $3/day, RU $1/day, System $2/day. 80% alert via iMessage. 100% pauses paid APIs (Claude CLI continues free).

**P27.** Multi-channel signals about the same person/company merge into ONE diagnosis, not separate plays.

**P28.** "Send me an email" ALWAYS gets full play: dossier subset + market multiples delighter + data room link. Never a simple one-liner.

**P29.** Don't ask to confirm between records/steps. Run jobs to completion autonomously.

---

## CONTACT GENERATION RULES (when/how contacts are created)

**C1.** Contacts created from buyer_targets JSON during deal_research migration. Each verified contact gets: full_name, first_name, last_name, title, linkedin_url, company_id, entity='next_chapter', source='deal_research_migration'.

**C2.** Company records created when a buyer company doesn't exist in companies table. Entity = 'next_chapter', source = 'deal_research_migration'.

**C3.** Every row in every transactional table MUST carry an entity field. No untagged data enters the system.

**C4.** DNC is universal. One block = blocked everywhere, all entities, all channels. do_not_call table has NO entity column by design.

**C5.** DNC enforcement BEFORE any contact loads to any engagement list.

**C6.** Exa searches first for contact info. Clay is fallback only.

**C7.** Clay default credits per enrichment: 14 credits at $0.016/credit = $0.224/call.

**C8.** Never overwrite existing contact data. Only fill empty fields.

**C9.** Contact enrichment queries use: "{owner}" "{name}" {city} {state} phone email contact LinkedIn.

**C10.** ALL callers scanned by default: Mark, Ewing, John. Entity routing uses person-to-entity rules.

**C11.** Multi-rep overlap: auto-merge into one unified record. Notify both reps via iMessage: "[Argus] Overlap detected: {company} -- Mark had a call 3/15, Ewing got an email 3/18. Merged."

**C12.** Lead lifecycle stages: Raw Lead > MUL (Marketing Unqualified) > MQL (Marketing Qualified) > SQL (Sales Qualified) > Opportunity > Signed Client > Active/In Progress > Closed Won/Lost > Nurture. Every company must have ONE status at all times.

---

## INFRASTRUCTURE RULES (hard constraints)

**I1.** NEVER create a new Supabase project, org, or instance. One instance: master-crm (dwrnfpjcvydhmhnvyzov).

**I2.** NEVER create new API accounts or sign up for services.

**I3.** NEVER store data in /tmp, ~/Desktop, ~/Downloads outside project directory or Supabase.

**I4.** ALWAYS commit + push to ewing-operating-system/master-crm after changes.

**I5.** ALWAYS log costs to cost_log table with entity tag.

**I6.** NEVER generate reports from memory. Read actual data first.

**I7.** ALWAYS disclose NEEDS_REVIEW validation status.

**I8.** If a key fails, STOP and report. Do NOT sign up for a replacement.

**I9.** Shared capabilities, separate data: same tool, different tables, different tags, different campaigns. Never merge.

**I10.** Campaign naming convention: entity prefix required (AND-, NC-, RU-).

**I11.** Old names are WRONG. Always cross-reference Name Crosswalk. "AND Call Command" contains NC data.

**I12.** Rule changes require: what changed, why, old rule, new rule, who approved. No silent updates.

**I13.** Everything in Supabase. Not in memory, not in local files that get lost, not in chat history.

**I14.** Every decision, correction, approval, and rule lives in permanent queryable storage.

**I15.** Dual-view pages: admin view (see everything) and client view (curated). Internal strategy never leaks.

**I16.** Before signing: prospect has view only. After signing: light editing (revenue, employees, service mix). Cannot change narrative, strategy, targeting, or approach.

**I17.** Every page is all about THEM, nothing about us. The invisible engine.

---

## COMMUNICATION RULES

**COM1.** NEVER sound like a template. If you could send the same message to 100 companies by changing the name, it's bad.

**COM2.** Every outreach piece must reference at least ONE specific detail from research (review quote, founding year, award, personal detail).

**COM3.** Cold call opener should make them say "how did you find that?"

**COM4.** Sign EVERY piece as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668.

**COM5.** LinkedIn message under 300 chars (connection request limit).

**COM6.** Voicemail must state name and number at START and END.

**COM7.** iMessage format: start with [Argus], include lettered choices (A, B, C), describe temporary vs permanent consequences.

**COM8.** Frame problems from THEIR perspective: "prevent leaks" not "replace roof." "Plan your next chapter" not "sell your business."

---

## PERSONALIZATION RULES

**PERS1.** Fair game: industry data, market multiples, M&A activity, public info (podcasts, interviews, press, awards, BBB, Google reviews), calculated estimates WITH disclosed methodology, company facts (years, service area, certifications).

**PERS2.** Off limits: divorce, family disputes, personal legal issues, store closures, employee arrests, lawsuits, negative sentiment scoring, anything perceived as harmful personalization.

**PERS3.** Transparency: when estimating, ALWAYS disclose method. "X employees x $Y/employee = estimated revenue." Education is king.

**PERS4.** Roofing door-knock standard: every fact is real, verifiable, about THEM, strung together in a way they've never heard before. The rep becomes a wizard of relevant facts.

---

## LLM CONFIGURATION RULES

**L1.** LLM role assignments: Researcher 1 = Mistral Small (96/100, $0.002). Researcher 2 = DeepSeek Chat (95.3/100, $0.004). Inspector 1 = DeepSeek Chat. Inspector 2 = GPT-4o Mini. Synthesizer = Claude CLI (free).

**L2.** Production controller overrides: Researcher = Gemini 2.5 Flash Lite. Validator A = DeepSeek V3. Validator B = Llama 3.3 70B. Synthesizer = GPT-4o Mini. Valuator = GPT-4o Mini. Certifier = Claude CLI. Letter Writer = Claude CLI.

**L3.** Fallback chains: mistral > deepseek, openai > deepseek, deepseek > openai, together > deepseek, local_claude > [openai, deepseek] (DUAL).

**L4.** Groq DISABLED (2026-03-27) -- rate limits too low.

**L5.** Master CRM LLM config: Claude Code CLI = primary ($0.00). DeepSeek V3 via OpenRouter ($0.004/call) for auditor/validator. Gemini 2.5 Flash Lite ($0.001/call) for researcher. GPT-4o Mini ($0.002/call) for executor.

---

*End of complete rules list. 28 research methods, 13 data assembly rules, 20 business rules, 25 quality rules, 29 pipeline rules, 12 contact generation rules, 17 infrastructure rules, 8 communication rules, 4 personalization rules, 5 LLM configuration rules. Total: 161 rules.*
