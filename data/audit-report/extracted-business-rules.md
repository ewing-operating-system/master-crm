# Extracted Business Rules, API Patterns, and LLM Prompt Templates

**Extraction Date:** 2026-03-28
**Extracted By:** Argus (Claude Opus 4.6)
**Purpose:** Complete capture of all business logic before codebase rebuild

---

## TABLE OF CONTENTS

1. [Business Rules](#1-business-rules)
2. [API Integration Patterns](#2-api-integration-patterns)
3. [LLM Prompt Templates](#3-llm-prompt-templates)
4. [Campaign Logic](#4-campaign-logic)
5. [OpenClaw Agent Identities](#5-openclaw-agent-identities)
6. [Configuration Registry](#6-configuration-registry)

---

## 1. BUSINESS RULES

### 1.1 Hard Infrastructure Rules (CLAUDE.md)

RULE: NEVER create a new Supabase project, org, or instance — SOURCE: CLAUDE.md:63 — TYPE: ENFORCED — ENTITY: system

RULE: NEVER create new API accounts or sign up for services — SOURCE: CLAUDE.md:64 — TYPE: ENFORCED — ENTITY: system

RULE: NEVER store data in /tmp, ~/Desktop, ~/Downloads, or any location outside the project directory or Supabase — SOURCE: CLAUDE.md:65 — TYPE: ENFORCED — ENTITY: system

RULE: NEVER create new skills; use existing ones in ~/.claude/skills/ — SOURCE: CLAUDE.md:66 — TYPE: ENFORCED — ENTITY: system

RULE: ALWAYS commit + push to ewing-operating-system/dossier-pipeline after changes — SOURCE: CLAUDE.md:67 — TYPE: ENFORCED — ENTITY: system

RULE: ALWAYS log costs to dossier_cost_log table — SOURCE: CLAUDE.md:68 — TYPE: ENFORCED — ENTITY: system

RULE: If a key fails, STOP and report. Do NOT sign up for a replacement — SOURCE: CLAUDE.md:69 — TYPE: ENFORCED — ENTITY: system

RULE: All pipeline data goes to Supabase or ~/Projects/dossier-pipeline/data/ — SOURCE: CLAUDE.md:70 — TYPE: ENFORCED — ENTITY: system

### 1.2 Reporting Rules (CLAUDE.md — Mark DeChant reviews everything)

RULE: NEVER generate reports from memory or expectations. ALWAYS read the actual JSON dossier files first — SOURCE: CLAUDE.md:71 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: ALWAYS disclose NEEDS_REVIEW validation status. Never omit it. Explain what was flagged and the plan to fix it — SOURCE: CLAUDE.md:72 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: ALWAYS use actual per-company cost averages from JSON cost logs for projections. Never round down or use aspirational benchmarks — SOURCE: CLAUDE.md:73 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: NEVER list company names in reports unless they match actual dossier filenames on disk — SOURCE: CLAUDE.md:74 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: ALWAYS use Claude Code Desktop CLI (claude -p) for LLM calls, NEVER the Anthropic API. Cost is $0.00 via subscription — SOURCE: CLAUDE.md:75 — TYPE: ENFORCED — ENTITY: system

RULE: Pipe prompts via stdin (input=prompt), NOT as CLI arguments. Large prompts (15K+ chars) will timeout if passed as args — SOURCE: CLAUDE.md:75 — TYPE: ENFORCED — ENTITY: system

RULE: If Claude CLI fails, DUAL FALLBACK kicks in — both OpenAI AND DeepSeek run the same prompt and results are cross-checked. Do not change this to single fallback. Claude CLI timeout is 300 seconds — SOURCE: CLAUDE.md:76 — TYPE: ENFORCED — ENTITY: system

### 1.3 Pipeline Design Principles (production_controller.py)

RULE: INCREMENTAL STORAGE — dossier_final is updated after EVERY step, not just at the end — SOURCE: production_controller.py:7 — TYPE: ENFORCED — ENTITY: system

RULE: RESEARCH CACHE — checks dossier_runs before calling Exa. Never re-research a company — SOURCE: production_controller.py:8 — TYPE: ENFORCED — ENTITY: system

RULE: RESUME FROM ANY STEP — reads dossier_final.dossier_status to know where to pick up — SOURCE: production_controller.py:9 — TYPE: ENFORCED — ENTITY: system

RULE: NEVER WIPE — only skips APPROVED records. Never delete dossier_final records — SOURCE: production_controller.py:10 — TYPE: ENFORCED — ENTITY: system

RULE: ERROR ISOLATION — one target's failure is logged and skipped, pipeline keeps going — SOURCE: production_controller.py:11 — TYPE: ENFORCED — ENTITY: system

RULE: RATE LIMIT AWARENESS — detects 402/403/429, pauses, reports, continues — SOURCE: production_controller.py:12 — TYPE: ENFORCED — ENTITY: system

RULE: Abort the company if steps 1-3 (Research, Validate, Synthesize) fail. Steps 4-6 can fail non-fatally — SOURCE: openclaw_pipeline.py:261-264 — TYPE: ENFORCED — ENTITY: system

RULE: Stop the entire pipeline if errors exceed 10 consecutive failures — SOURCE: production_controller.py:705 — TYPE: ENFORCED — ENTITY: system

### 1.4 Provenance Rules

RULE: Every fact MUST include source_url, source_type, search_query, source_excerpt. No provenance = does not exist — SOURCE: openclaw_pipeline.py:91, researcher/IDENTITY.md:23 — TYPE: ENFORCED — ENTITY: system

RULE: Never fabricate a source URL — SOURCE: researcher/IDENTITY.md:24 — TYPE: ENFORCED — ENTITY: system

RULE: A fact without a source_url = NEEDS_REVIEW status — SOURCE: validator/IDENTITY.md:17 — TYPE: ENFORCED — ENTITY: system

### 1.5 Validation Rules (Trust Layer)

RULE: Revenue/EBITDA estimates need 2+ corroborating signals — SOURCE: validator/IDENTITY.md:18 — TYPE: ENFORCED — ENTITY: system

RULE: Owner quotes need exact source URL. No paraphrasing — SOURCE: validator/IDENTITY.md:19 — TYPE: ENFORCED — ENTITY: system

RULE: Owner name flagged as possible pseudonym = MEDIUM severity — SOURCE: validator/IDENTITY.md:20 — TYPE: ADVISORY — ENTITY: system

RULE: All data from a single source = MEDIUM severity — SOURCE: validator/IDENTITY.md:21 — TYPE: ADVISORY — ENTITY: system

RULE: Claims contradicted by another source = HIGH severity — SOURCE: validator/IDENTITY.md:22 — TYPE: ENFORCED — ENTITY: system

RULE: Self-reported claims presented as verified = LOW severity — SOURCE: validator/IDENTITY.md:23 — TYPE: ADVISORY — ENTITY: system

RULE: You can't grade your own homework. Validator never runs on the same model that did the research. Researcher uses Mistral Small (local). Validator uses DeepSeek and Llama (remote). Different model families, independent judgment — SOURCE: validator/IDENTITY.md:27-28 — TYPE: ENFORCED — ENTITY: system

RULE: Never approve a dossier with HIGH severity flags unresolved — SOURCE: validator/IDENTITY.md:38 — TYPE: ENFORCED — ENTITY: system

RULE: Never remove a flag because the data "seems right" — flags require source evidence to clear — SOURCE: validator/IDENTITY.md:39 — TYPE: ENFORCED — ENTITY: system

RULE: Dual validator merging: pick the validator with MORE flags as the winner, then union unique flags from the loser — SOURCE: production_controller.py:293-301 — TYPE: ENFORCED — ENTITY: system

### 1.6 Executor / Document Rules

RULE: Nothing sends until human approval. Everything stays DRAFT — SOURCE: executor/IDENTITY.md:4, main/IDENTITY.md:39 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Never use unverified data in customer-facing content. Only APPROVED or NEEDS_REVIEW with caveats — SOURCE: executor/IDENTITY.md:44 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Never treat a Google Maps business phone as an owner's cell phone — SOURCE: executor/IDENTITY.md:45 — TYPE: ENFORCED — ENTITY: system

RULE: Every document logged in sent_log with content_hash and provenance snapshot — SOURCE: executor/IDENTITY.md:46 — TYPE: ENFORCED — ENTITY: system

RULE: Letters send FIRST. Enrichment (cell + email) is post-letter investment, not pre-letter gate — SOURCE: executor/IDENTITY.md:17-18 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Letter must be 300-400 words — SOURCE: openclaw_pipeline.py:202, production_controller.py:386 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Letter must reference specific verified facts, include valuation range, respectful/knowledgeable tone, "this person actually researched us" feeling, CTA with personalized URL — SOURCE: production_controller.py:386 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Personalized URL format: https://nextchapter.deal/{slug} where slug = company name lowercased, spaces to hyphens, commas and periods removed — SOURCE: openclaw_pipeline.py:205, production_controller.py:389 — TYPE: ENFORCED — ENTITY: next_chapter

### 1.7 Outreach Rules

RULE: NEVER sound like a template. If you could send the same message to 100 companies by changing the name, it's bad — SOURCE: prompts/outreach_prompt.py:62 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Every outreach piece must reference at least ONE specific detail from the research (a review quote, founding year, award, personal detail) — SOURCE: prompts/outreach_prompt.py:63 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: The cold call opener should make them say "how did you find that?" — SOURCE: prompts/outreach_prompt.py:64 — TYPE: ADVISORY — ENTITY: next_chapter

RULE: Sign EVERY piece as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668 — SOURCE: prompts/outreach_prompt.py:65 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: LinkedIn message must be concise enough for a connection request (under 300 chars) — SOURCE: prompts/outreach_prompt.py:66 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Voicemail must state name and number at the START and END — SOURCE: prompts/outreach_prompt.py:67 — TYPE: ENFORCED — ENTITY: next_chapter

### 1.8 Pipeline Controller Rules (main/IDENTITY.md)

RULE: Never process companies in parallel. One at a time, sequential waterfall. M4 24GB hardware constraint — SOURCE: main/IDENTITY.md:37 — TYPE: ENFORCED — ENTITY: system

RULE: Never skip the Validator. Every dossier must pass through the Trust Layer — SOURCE: main/IDENTITY.md:38 — TYPE: ENFORCED — ENTITY: system

RULE: Never auto-send documents. Everything stays DRAFT until human approval — SOURCE: main/IDENTITY.md:39 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Never exceed the campaign's cost_cap without alerting Ewing — SOURCE: main/IDENTITY.md:40 — TYPE: ENFORCED — ENTITY: system

RULE: Engagement threshold: 3 emails + 2 calls + 1 letter with no response = mark exhausted — SOURCE: main/IDENTITY.md:16 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: 10-second delay between companies for API breathing room — SOURCE: main/IDENTITY.md:26 — TYPE: ENFORCED — ENTITY: system

### 1.9 Enrichment Rules

RULE: Exa searches first for contact info. Clay is fallback only when Exa finds no phone — SOURCE: lib/enrichment_client.py:1, stages/s3_enrich_contact.py:42-43 — TYPE: ENFORCED — ENTITY: system

RULE: Clay only fires when: no phone from Exa AND no phone_main AND no phone_direct on existing record — SOURCE: stages/s3_enrich_contact.py:43 — TYPE: ENFORCED — ENTITY: system

RULE: Never overwrite existing contact data. Only fill empty fields — SOURCE: stages/s3_enrich_contact.py:31-38, lib/enrichment_client.py:34-40 — TYPE: ENFORCED — ENTITY: system

RULE: Clay default credits per enrichment: 14 credits at $0.016/credit = $0.224/call — SOURCE: lib/enrichment_client.py:61-62 — TYPE: ADVISORY — ENTITY: system

### 1.10 LLM Client Rules

RULE: Circuit breaker opens after 3 consecutive failures. Provider disabled for 5 minutes — SOURCE: lib/llm_client.py:293-294 — TYPE: ENFORCED — ENTITY: system

RULE: Dual fallback for Claude CLI: when Claude fails, BOTH OpenAI AND DeepSeek run the same prompt. Results cross-checked. Prefer the one that parses as clean JSON; otherwise use the longer response — SOURCE: lib/llm_client.py:203-254 — TYPE: ENFORCED — ENTITY: system

RULE: Provider budgets enforced per session. Together: $4.50, OpenAI: $5.00, DeepSeek: $10.00, Claude: unlimited (free) — SOURCE: config.py:132-137 — TYPE: ENFORCED — ENTITY: system

RULE: Prompt truncation at max_context_chars with "[TRUNCATED]" marker — SOURCE: lib/llm_client.py:68-69 — TYPE: ENFORCED — ENTITY: system

RULE: JSON parse retry: if first attempt fails to parse, retry with strict "Return ONLY valid JSON" instruction appended — SOURCE: lib/llm_client.py:141-149 — TYPE: ENFORCED — ENTITY: system

RULE: Sliding window rate limiter: 60-second window, enforced per provider RPM limit — SOURCE: lib/llm_client.py:256-274 — TYPE: ENFORCED — ENTITY: system

### 1.11 Deal Side Framing Rules

RULE: sell-side framing: "We seek to bring you qualified buyers for your business" — SOURCE: executor/IDENTITY.md:37 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: buy-side framing: "We represent a buyer looking for businesses like yours" — SOURCE: executor/IDENTITY.md:38 — TYPE: ENFORCED — ENTITY: next_chapter

RULE: represent-side framing: "We help owners like you navigate an exit on your terms" — SOURCE: executor/IDENTITY.md:39 — TYPE: ENFORCED — ENTITY: next_chapter

### 1.12 Memory/Behavioral Rules (from MEMORY.md)

RULE: Never say "private equity." Use operator-friendly language: former business owners who cashed out and buy companies because they believe in owners, not the stock market — SOURCE: MEMORY.md feedback — TYPE: ENFORCED — ENTITY: next_chapter

RULE: Never delete dossier_final records. Store incrementally after every step. Re-run, don't wipe — SOURCE: MEMORY.md feedback — TYPE: ENFORCED — ENTITY: system

RULE: Don't ask to confirm between records/steps. Run jobs to completion autonomously — SOURCE: MEMORY.md feedback — TYPE: ENFORCED — ENTITY: system

---

## 2. API INTEGRATION PATTERNS

### 2.1 Supabase (Primary Data Store)

API: Supabase — ENDPOINT: https://rdnnhxhohwjucvjwbwch.supabase.co/rest/v1/{table} — AUTH: Bearer JWT (service_role key) + apikey header — QUIRKS: Uses PostgREST query syntax. Upsert via POST with Prefer: return=representation,resolution=merge-duplicates. PATCH for updates requires URL-encoded filter params. — SOURCE: agents/shared.py:42-68, config.py:7-14

Headers pattern:
```python
{"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
 "Content-Type": "application/json", "Prefer": "return=representation"}
```

GET: `urllib.request.Request(url, headers=sb_headers())`
INSERT (POST): `method="POST"` with Prefer `return=representation`
UPSERT (POST): `method="POST"` with Prefer `return=representation,resolution=merge-duplicates`
UPDATE (PATCH): `method="PATCH"` with URL-encoded filter `?target_id=eq.{id}`

Tables used: campaigns, targets, tam_businesses, dossier_final, dossier_runs, dossier_provenance, dossier_cost_log, sent_log, dialer_queue

### 2.2 Exa.ai (Web Search)

API: Exa.ai — ENDPOINT: https://api.exa.ai/search — AUTH: x-api-key header — QUIRKS: Rate delay 0.3s (lib) or 1-2s (agents). Cost: $1.00/1000 searches + $1.00/1000 content results. Max 3 consecutive errors then abort. Text truncated to 2000-3000 chars per result. — SOURCE: agents/shared.py:89-103, lib/exa_client.py:1-148

Payload:
```python
{"query": query, "num_results": 5, "type": "auto",
 "contents": {"text": {"maxCharacters": 3000}}}
```

Five standard search queries per company:
1. `{company} {city} {state} owner founder interview`
2. `{company} {city} reviews reputation culture`
3. `site:{domain} about team services` (or `{company} {vertical} services {city} AZ` if no website)
4. `{company} {city} AZ revenue employees BBB profile`
5. `{company} linkedin company {vertical} {state}`

Contact enrichment query:
`"{owner}" "{name}" {city} {state} phone email contact LinkedIn`

Contact extraction regexes:
- Email: `[\w.+-]+@[\w-]+\.[\w.-]+` (excludes example, test, noreply, sentry, webpack)
- Phone: `(?:\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}` (10-11 digits)
- LinkedIn: URL containing `linkedin.com/in/`
- Address: `\d+\s+[\w\s]+(?:St|Ave|Rd|Blvd|Dr|Ln|Way|Ct|Pl|Cir|Loop|Pkwy|Hwy)\.?[^,]*,\s*[\w\s]+,?\s*[A-Z]{2}\s*\d{5}`

### 2.3 OpenRouter (Multi-Model LLM Gateway)

API: OpenRouter — ENDPOINT: https://openrouter.ai/api/v1/chat/completions — AUTH: Bearer token — QUIRKS: Retry with exponential backoff [15s, 30s, 60s] on 429 errors. Timeout 180s. Referer header required. Cost estimated from usage tokens if total_cost not provided. — SOURCE: agents/shared.py:107-135

Headers:
```python
{"Authorization": f"Bearer {OPENROUTER_API_KEY}",
 "Content-Type": "application/json",
 "HTTP-Referer": "https://nextchapteradvisory.com",
 "X-Title": "Dossier Pipeline"}
```

Models routed through OpenRouter:
- `google/gemini-2.5-flash-lite` (researcher)
- `deepseek/deepseek-chat-v3-0324` (validator A, fallback)
- `meta-llama/llama-3.3-70b-instruct` (validator B)
- `openai/gpt-4o-mini` (synthesizer, valuator)

### 2.4 Ollama (Local LLM)

API: Ollama — ENDPOINT: http://localhost:11434/api/chat — AUTH: None (local) — QUIRKS: 600s timeout. stream=False for batch mode. Model: mistral-small. Cost: $0.00. — SOURCE: agents/shared.py:137-147

### 2.5 Claude CLI (Local LLM)

API: Claude Code CLI — ENDPOINT: subprocess `claude -p --output-format text` — AUTH: None (local subscription) — QUIRKS: MUST pipe via stdin, NOT CLI args (15K+ chars timeout). 300s timeout. Cost: $0.00. Token estimation: 1 token = 4 chars. — SOURCE: agents/shared.py:149-154, lib/llm_client.py:72-89

### 2.6 Clay.com (Contact Enrichment)

API: Clay — ENDPOINT: https://api.clay.com/v1/people/enrich — AUTH: Bearer token — QUIRKS: Rate delay 0.5s. 14 credits per call. $0.016/credit. Requires first_name + last_name minimum. Domain extracted by stripping protocol + www + path. Returns 404 when person not found. — SOURCE: lib/clay_client.py:1-84, config.py:22-23

Payload:
```python
{"first_name": first, "last_name": last, "company_name": name,
 "company_domain": domain, "city": city, "state": state}
```

Response mapping:
- phone: `person.phone_number` or `person.mobile_phone`
- email: `person.email` or `person.work_email`
- linkedin: `person.linkedin_url`
- address: `person.company_address` or `person.address`

### 2.7 OpenAI-Compatible Client Pattern (lib/llm_client.py)

API: All providers via OpenAI SDK — ENDPOINT: per-provider base_url — AUTH: per-provider api_key — QUIRKS: Uses Python openai.OpenAI client for all non-Claude providers. json_mode sets response_format type json_object. Automatic fallback chain with circuit breaking. — SOURCE: lib/llm_client.py:21-321

Providers registered:

| Provider | base_url | Default Model | RPM | Input $/M | Output $/M | Max Chars |
|---|---|---|---|---|---|---|
| deepseek | https://api.deepseek.com/v1 | deepseek-chat | 60 | $0.27 | $1.10 | 30K |
| mistral | https://api.mistral.ai/v1 | mistral-small-latest | 30 | $0.10 | $0.30 | 30K |
| openai | https://api.openai.com/v1 | gpt-4o-mini | 500 | $0.15 | $0.60 | 60K |
| together | https://api.together.xyz/v1 | Llama-3.3-70B-Instruct-Turbo | 60 | $0.88 | $0.88 | 30K |
| local_claude | subprocess | claude-code-desktop | 10 | $0.00 | $0.00 | 150K |

Fallback chains:
- mistral -> deepseek
- openai -> deepseek
- deepseek -> openai
- together -> deepseek
- local_claude -> [openai, deepseek] (DUAL: both run, cross-checked)
- groq: DISABLED (2026-03-27, rate limits too low)

### 2.8 OpenClaw Agent Dispatch

API: OpenClaw CLI — ENDPOINT: subprocess `openclaw agent --agent {name} --message {prompt} --timeout {timeout}` — AUTH: None (local) — QUIRKS: Returns stdout as JSON (may be wrapped in markdown fences). Extra 30s buffer on subprocess timeout vs agent timeout. — SOURCE: agents/openclaw_pipeline.py:32-48

---

## 3. LLM PROMPT TEMPLATES

### 3.1 RESEARCHER PROMPT (Extraction)

PROMPT: Extract structured company intelligence from web search results — MODEL: Mistral Small (local) or Gemini 2.5 Flash Lite (OpenRouter) — SOURCE: agents/openclaw_pipeline.py:86-97, agents/production_controller.py:235-251

```
You are researching {company}, a {vertical} company in {city}, {state}.

Here are web search results:
{json.dumps(all_results, indent=2)[:8000]}

CRITICAL: Every fact MUST include source_url, source_type, search_query, source_excerpt. No provenance = does not exist.

Return JSON with: company_name, owner_name, owner_title, owner_quotes, company_story, culture_signals, services, differentiators, reviews_summary, avg_rating, review_count, years_in_business, employee_estimate, revenue_signals, certifications, awards, community_involvement, growth_signals, competitive_position, technology_used, mailing_address, phone, website_url, sources_used.

Each field: {"value": "data", "source_url": "url", "source_type": "type", "search_query": "query", "source_excerpt": "excerpt"}

Return ONLY valid JSON.
```

### 3.2 VALIDATOR PROMPT (Fact-Check)

PROMPT: Fact-check and validate researcher output — MODEL: DeepSeek Chat + Llama 3.3 70B (dual, parallel via OpenRouter) — SOURCE: agents/openclaw_pipeline.py:108-122, agents/production_controller.py:265-275

```
You are a fact-checker validating research about {company}.

Researcher output:
{json.dumps(researcher_output, indent=2, default=str)[:6000]}

For EACH claim: check source_url exists, check plausibility, flag fabrications.

Return JSON:
{"facts_verified": 0, "facts_flagged": 0, "flags": [{"claim": "what", "issue": "why", "severity": "HIGH/MEDIUM/LOW"}], "verified_data": {...cleaned...}, "confidence_score": 0-100, "notes": "assessment"}

Return ONLY valid JSON.
```

### 3.3 SYNTHESIZER PROMPT (Narrative)

PROMPT: Write company intelligence narrative — MODEL: GPT-4o Mini (OpenRouter) or Claude CLI — SOURCE: agents/openclaw_pipeline.py:127-147, agents/production_controller.py:310-332

```
Write intelligence narrative about {company}, a {vertical} company in {city}, AZ.

Validated data:
{json.dumps(validated_data, indent=2, default=str)[:6000]}

BLOCKLIST -- do NOT use:
- [{severity}] {claim}: {issue}

Return JSON:
{"executive_summary": "2-3 sentences", "owner_profile": "who", "company_narrative": "story", "competitive_moat": "moat", "acquisition_appeal": "why", "risk_factors": [], "cold_call_opener": "opener", "key_quotes": [], "narrative_score": 0-100}

Return ONLY valid JSON.
```

### 3.4 VALUATOR PROMPT (M&A Valuation)

PROMPT: Estimate company valuation for M&A — MODEL: GPT-4o Mini (OpenRouter) — SOURCE: agents/openclaw_pipeline.py:150-164, agents/production_controller.py:336-349

```
Value {company}, a {vertical} company in AZ for M&A.

Research: {json.dumps(all_outputs.get('researcher', {}), indent=2, default=str)[:3000]}
Narrative: {json.dumps(all_outputs.get('synthesizer', {}), indent=2, default=str)[:2000]}

Return JSON:
{"vertical": "{vertical}", "ebitda_estimate": {"range": "$X-$Y", "confidence": "HIGH/MEDIUM/LOW", "basis": "why"}, "multiple_range": {"low": 0, "mid": 0, "high": 0, "basis": "why"}, "ev_estimate": {"conservative": "$X", "base": "$X", "bull": "$X"}, "active_buyers": [], "value_drivers_present": [], "value_detractors_present": [], "letter_worthy": true, "valuation_score": 0-100}

Return ONLY valid JSON.
```

### 3.5 CERTIFIER PROMPT (Final Audit)

PROMPT: Certify dossier quality — catch hallucinations, verify sourcing, score completeness — MODEL: Claude CLI (local, free) — SOURCE: agents/openclaw_pipeline.py:167-185, agents/production_controller.py:352-369

```
Certify dossier for {company}.

RESEARCHER: {json.dumps(all_outputs.get('researcher', {}), indent=2, default=str)[:3000]}
VALIDATOR: {json.dumps(all_outputs.get('validator', {}), indent=2, default=str)[:3000]}
SYNTHESIZER: {json.dumps(all_outputs.get('synthesizer', {}), indent=2, default=str)[:3000]}

Verify sourced. Check flags respected. Score completeness. Catch hallucinations. Write cold call opener.

Return JSON:
{"verdict": "APPROVED/NEEDS_REVIEW/REJECTED", "completeness_score": 0-100, "hallucination_count": 0, "hallucinations_found": [], "validator_flags_respected": true, "missing_fields": [], "certified_cold_call_opener": "opener", "certified_owner_name": "name or null", "certified_owner_vision": "vision or null", "issues": [{"issue": "what", "severity": "HIGH/MEDIUM/LOW"}], "final_score": 0-100}

Be strict. Return ONLY valid JSON.
```

### 3.6 LETTER WRITER PROMPT (Certified Mail)

PROMPT: Write personalized certified mail letter — MODEL: Claude CLI (local, free) — SOURCE: agents/openclaw_pipeline.py:189-211, agents/production_controller.py:372-394

```
Write personalized certified mail letter from Mark DeChant, Managing Director of Next Chapter M&A Advisory, to {owner} at {company} in {city}, AZ.

Context: {json.dumps(synthesizer, indent=2, default=str)[:3000]}
Valuation: {json.dumps(valuator, indent=2, default=str)[:2000]}
Opener: {opener}

Rules: reference specific verified facts, include valuation range, respectful tone, "they researched us" feeling, CTA with personalized URL, 300-400 words.

Return JSON:
{"letter_text": "full letter", "hook_fact_used": "fact", "hook_source_url": "url", "personalized_url_slug": "{slug}", "mailing_address": "address", "letter_score": 0-100}

Return ONLY valid JSON.
```

### 3.7 OUTREACH PROMPT (Full Outreach Suite)

PROMPT: Generate all outreach materials (email, call script, LinkedIn, letter, voicemail, direct mail) — MODEL: Synthesizer role (Claude CLI primary, DeepSeek fallback) — SOURCE: prompts/outreach_prompt.py:1-68

```
You are writing outreach materials for Ewmarcus at Next Chapter M&A Advisory. Your job is to create highly personalized, non-salesy outreach that sounds like a genuine human who did real research -- because the research IS real.

=== COMPANY & OWNER ===
Company: {company_name}
Owner: {owner_name}
City: {city}, {state}
Vertical: {vertical}
Founded: {founded}
Revenue: {revenue}
Employees: {employees}

=== THE STORY (already researched) ===
Best Story: {best_story}
Call Opener: {call_opener}
Story Hook: {story_hook}

=== VALUATION CONTEXT ===
Estimated EV: {ev_range}
Value Drivers: {value_drivers}

=== REVIEWS (real customer quotes) ===
{reviews_text}

=== FLAGS ===
{flags_text}

=== CONTACT INFO ===
Phone: {phone}
Email: {email}
LinkedIn: {linkedin}
Address: {address}

=== STYLE REFERENCE ===
Here is an example of the exact tone and style to match. Study it carefully:

EXAMPLE COLD EMAIL:
Subject: "41 years, 180,000 customers, Wyoming RI -- the timing is right, Larry"
Body: "Larry, In 1984, you put a promise on your website that you still stand behind today... I run Next Chapter M&A Advisory, and I work exclusively with founders who've built businesses like AquaScience -- ones with real staying power -- to make sure their next chapter is on their terms..."

EXAMPLE CALL OPENER:
"I came across AquaScience and that founding line you have kept on the website since 1984 -- we will bring the world's finest water treatment equipment directly to the public at the lowest prices."

=== YOUR TASK ===
Generate all outreach pieces as JSON. Every piece MUST reference something SPECIFIC from the research -- a review quote, a founding year, an award, a personal detail. Nothing generic.

Return JSON:
{
    "outreach_sequence": ["CALL {phone}", "EMAIL {email}", "LINKEDIN {linkedin}", "LETTER {address}"],
    "lead_with": "The strongest hook -- what topic/angle to open with",
    "avoid": "What NOT to say -- words, phrases, or topics that would kill the conversation",
    "cold_email_subject": "Personal, specific subject line -- NOT salesy. Reference a real detail.",
    "cold_email_body": "3-4 short paragraphs. Sign off as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668",
    "handwritten_letter": "Dear [Owner], 3-4 paragraphs. Sign off as Warmly, Ewmarcus / Next Chapter M&A Advisory / 818-747-9668",
    "linkedin_message": "2-3 sentences. Under 300 characters if possible.",
    "cold_call_script": "OPENING + POSITIONING + ASK + OBJECTION HANDLING + VOICEMAIL",
    "direct_mail": "Professional but warm. Reference a specific detail."
}

RULES:
- NEVER sound like a template.
- Every piece must reference at least ONE specific detail from the research.
- The call opener should make them say "how did you find that?"
- Sign EVERY piece as Ewmarcus / Next Chapter M&A Advisory / 818-747-9668
- The LinkedIn message must be under 300 chars.
- The voicemail must state name and number at the START and END.
- Return valid JSON only.
```

---

## 4. CAMPAIGN LOGIC

### 4.1 Main Pipeline Waterfall

CAMPAIGN: All campaigns — FLOW: Research -> Validate -> Synthesize -> Valuate -> Certify -> Letter — SOURCE: agents/production_controller.py:13, agents/openclaw_pipeline.py:216-223

Status progression: PENDING -> RESEARCHED -> VALIDATED -> SYNTHESIZED -> VALUED -> CERTIFIED -> LETTER_DRAFTED -> APPROVED

Step details:

| Step | Status After | Agent | Provider | Model | Abort on fail? |
|---|---|---|---|---|---|
| 1. Research | RESEARCHED | researcher | OpenRouter / Ollama | gemini-2.5-flash-lite / mistral-small | YES |
| 2. Validate | VALIDATED | validator | OpenRouter (dual parallel) | deepseek-chat + llama-3.3-70b | YES |
| 3. Synthesize | SYNTHESIZED | synthesizer | OpenRouter | gpt-4o-mini | YES |
| 4. Valuate | VALUED | valuator | OpenRouter | gpt-4o-mini | NO |
| 5. Certify | CERTIFIED | certifier | Claude CLI | claude-cli | NO |
| 6. Letter | LETTER_DRAFTED | letter_writer | Claude CLI | claude-cli | NO |

### 4.2 Enrichment Waterfall (Post-Letter)

CAMPAIGN: All sell-side campaigns — FLOW: Exa contact search -> (if no phone) Clay person enrich -> Update dossier -> Queue outreach — SOURCE: lib/enrichment_client.py:12-79, stages/s3_enrich_contact.py:9-76

After enrichment, outreach branching:
- Letter only: enrichment found no cell or email
- Letter + call: found verified cell -> queue for Salesfinity
- Letter + email: found verified email -> generate email via template
- Letter + call + email: full outreach sequence

### 4.3 Outreach Generation

CAMPAIGN: All campaigns with enriched contacts — FLOW: Load SYNTHESIZING dossiers with valuation but no outreach -> Generate full outreach suite -> Set status COMPLETE — SOURCE: stages/s6_outreach.py:119-149

Outreach outputs stored: outreach_sequence, lead_with, avoid, cold_email_subject, cold_email_body, handwritten_letter, linkedin_message, cold_call_script, direct_mail

### 4.4 Campaign Config Loading

CAMPAIGN: Dynamic — FLOW: Read campaigns table from Supabase by campaign_id -> Parse source_table, source_filters, target_profile, focus_areas, engagement_rules from JSON strings -> Load targets from source_table with filters -> Skip APPROVED targets -> Process remaining — SOURCE: agents/shared.py:70-85

### 4.5 OpenClaw Pipeline Variant

CAMPAIGN: az-openclaw-v1, az-production-v1 — FLOW: Same waterfall but LLM reasoning dispatched to OpenClaw agents via subprocess CLI, while data plumbing (Exa, Supabase) stays in Python — SOURCE: agents/openclaw_pipeline.py:1-417, agents/openclaw_controller.py:1-353

---

## 5. OPENCLAW AGENT IDENTITIES

### 5.1 Main (Pipeline Controller)

File: ~/.openclaw/agents/main/IDENTITY.md

Identity: Pipeline Controller for Next Chapter's dossier pipeline. Orchestrates Researcher, Validator, Executor agents and manages campaign lifecycle.

Reactive triggers: API rate limit -> pause + reroute | Validation fails -> flag + skip | Call transcript action signal -> dispatch Executor | New contact data -> update + queue outreach

Proactive triggers: All targets contacted -> alert Ewing | Engagement threshold (3 emails + 2 calls + 1 letter) -> mark exhausted | Cost cap approaching -> slow down + alert | Daily status report

Hardware: M4 Mac Mini, 24GB RAM, one Ollama model at a time

### 5.2 Researcher

File: ~/.openclaw/agents/researcher/IDENTITY.md

Identity: Extracts structured company intelligence from web search results. Does NOT search the web -- controller handles that.

Priority 1 (People -- competitive moat): Owner/founder name, title, background, direct quotes, culture signals, community involvement

Priority 2 (Business -- baseline): Services, certifications, ratings, revenue signals, employees, address

### 5.3 Validator (Trust Layer)

File: ~/.openclaw/agents/validator/IDENTITY.md

Identity: Cross-checks every fact from the Researcher using independent LLM judgment. Catches fabrications, unsourced claims, implausible data.

Core mechanism: Two independent inspectors validate in parallel (DeepSeek + Llama 3.3 70B). Merge results picking the stricter validator. Union unique flags.

### 5.4 Executor

File: ~/.openclaw/agents/executor/IDENTITY.md

Identity: Takes validated dossier data and produces customer-facing deliverables: letters, emails, proposals, SIMs, CIMs. Handles enrichment dispatch and dialer loading.

Document types: letter, email, proposal, sim (anonymized), cim (under NDA)

Key principle: Letters send FIRST. Enrichment is post-letter investment.

---

## 6. CONFIGURATION REGISTRY

### 6.1 Cost Rates

| Service | Rate | Source |
|---|---|---|
| Exa search | $1.00/1000 searches | config.py:28 |
| Exa content | $1.00/1000 results | config.py:29 |
| Clay credit | $0.016/credit | config.py:30 |
| Per-dossier cost cap | $0.10 | config.py:145 |
| Batch cost cap | $15.00 | config.py:144 |
| Default batch limit | 50 | config.py:143 |

### 6.2 LLM Role Assignments (SAP Benchmark 2026-03-26)

| Role | Provider | Model | Score | Cost/Call |
|---|---|---|---|---|
| Researcher 1 (extraction) | Mistral | mistral-small-latest | 96/100 | $0.002 |
| Researcher 2 (cross-check) | DeepSeek | deepseek-chat | 95.3/100 | $0.004 |
| Inspector 1 (merger) | DeepSeek | deepseek-chat | n/a | $0.001 |
| Inspector 2 (certifier) | OpenAI | gpt-4o-mini | n/a | reliable |
| Synthesizer (narrative) | Claude CLI | claude-code-desktop | 61/100 | $0.00 |

### 6.3 Production Controller Model Overrides

| Role | Model (via OpenRouter) |
|---|---|
| Researcher | google/gemini-2.5-flash-lite |
| Validator A | deepseek/deepseek-chat-v3-0324 |
| Validator B | meta-llama/llama-3.3-70b-instruct |
| Synthesizer | openai/gpt-4o-mini |
| Valuator | openai/gpt-4o-mini |
| Certifier | Claude CLI (not OpenRouter) |
| Letter Writer | Claude CLI (not OpenRouter) |

### 6.4 Outreach Config

| Key | Value | Source |
|---|---|---|
| Advisor Name | Ewmarcus | config.py:155 |
| Advisory Firm | Next Chapter M&A Advisory | config.py:156 |
| Advisor Phone | 818-747-9668 | config.py:157 |

### 6.5 Supabase Instance Registry (9 instances, 1 LIVE)

| Instance | Purpose | Status |
|---|---|---|
| rdnnhxhohwjucvjwbwch | AND Call Command -- all pipeline data | LIVE (primary) |
| lhmuwrlpcdlzpfthrodm | ColdCall Universe -- persons/companies/phones | RETIRED zombie |
| asavljgcnresdnadblse | Phoenix TAM Engine -- migrated | RETIRED |
| ginqabezgxaazkhuuvvw | Empty | RETIRED (delete) |
| iwcvaowfogpffdllqtld | debugger-tool | DEAD (delete) |
| iumytggxqtfyaxewgghb | Marks NYC Hunt -- investor CRM | NEW (consolidation TBD) |
| lsxmnowczekpdjuvrxxt | Ewing NYC Mobile Map -- empty | NEW (delete) |
| wdhnsbzmcjpqbltkulwe | NYC Deal Maker -- attack_list + Gemini | NEW (consolidation TBD) |
| pgoogsxaljtjhwhydqtg | NYC Outreach Hub -- full investor CRM | NEW (most valuable for consolidation) |

### 6.6 JSON Parsing Strategy (Triple Fallback)

1. Direct json.loads(text) attempt
2. Strip markdown fences then parse
3. Regex extract first {...} object from text then parse
4. If all fail, return {"_parse_error": True, "_raw_text": text[:2000]}

Source: agents/shared.py:170-188, lib/llm_client.py:153-180

---

## FILES NOT FOUND (skipped)

None -- all 16 specified files were successfully read and extracted.

---

*End of extraction. 91 business rules, 8 API patterns, 7 prompt templates, 5 campaign flows captured.*
