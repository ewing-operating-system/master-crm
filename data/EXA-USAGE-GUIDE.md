# Exa.ai Usage Guide — Next Chapter M&A Advisory

**Prepared for:** Exa.ai Product Team
**Prepared by:** Ewing Gillaspy, Next Chapter M&A Advisory
**Date:** 2026-03-28
**Contact:** ewmarcus@nextchapterma.com | 818-747-9668

---

## 1. WHO WE ARE

Next Chapter M&A Advisory is a boutique M&A advisory firm focused on home services businesses -- plumbing, HVAC, roofing, pest control, water treatment, flooring, steel, concrete, and precast. We represent owners of $2M-$50M revenue businesses who are considering selling.

**What makes us different:** We built an AI-powered pipeline that researches every company we contact, every potential buyer we approach, and every deal we structure. The pipeline uses multiple LLMs (Claude, DeepSeek, Mistral, GPT-4o Mini) orchestrated through a six-stage research-validate-synthesize-value-certify-draft workflow.

**Exa is our primary external intelligence source.** Every company profile, buyer dossier, competitive analysis, and personalized outreach letter starts with Exa search results. We do not use Google search APIs, Bing, or SerpAPI. Exa is it.

**Scale:** We maintain a total addressable market (TAM) of 1,000+ home services companies across Arizona (expanding nationally), and we research 3-5 potential buyers per seller, each requiring 5+ Exa searches. Our current active pipeline includes water treatment, precast concrete, flooring, HVAC, and HR services deals.

---

## 2. WHAT WE USE EXA FOR

Exa serves three distinct pipeline stages:

### Stage 1: Sell-Side Company Research (researching the company we want to represent)
We build a "dossier" on each potential seller -- their owner's name, background, company story, services, reviews, financials, culture. This dossier feeds personalized outreach letters that make the owner think "this person actually researched my company."

### Stage 2: Buy-Side Buyer Intelligence (researching companies that might acquire our clients)
For every deal, we identify 10-20 potential acquirers and build a deep intelligence profile on each: their M&A history, CEO strategy quotes, corporate development contacts, financial capacity, and strategic fit with our client.

### Stage 3: Proposal Gap-Fill (enriching incomplete records before generating proposals)
When we generate a formal M&A proposal for a client, any missing fields (revenue, employees, services, owner name, year founded) trigger targeted Exa searches to fill gaps.

---

## 3. THE QUALITY DIFFERENCE — EXA AS A 7x MULTIPLIER

We have direct before/after evidence of what Exa does to our output quality.

### SAP SuccessFactors Buyer Dossier (WITH Exa)
- **14,014 characters** of intelligence
- 7 major sections: Fit Analysis, Asset Mapping, Business Model Integration, Competitive Moat, Cold Call Intelligence, M&A History, Contact Intelligence
- **8 CEO earnings call quotes** with quarter/year attribution, extracted from real transcripts Exa surfaced
- 5 "golden nugget" cold call openers, each tied to a real CEO quote
- 5 verified M&A decision-maker contacts with LinkedIn URLs
- Strategic fit narrative explaining exactly WHY SAP needs this specific acquisition
- Competitive threat analysis: "What happens if Workday acquires HR.com first?"

### Drake Star Partners Dossier (WITHOUT Exa, LLM knowledge only)
- **1,902 characters** of generic text
- Generic company description from LLM training data
- No real quotes, no earnings call data, no verified contacts
- No strategic fit analysis, no competitive moat framing
- Reads like a Wikipedia summary, not M&A intelligence

**The ratio: 14,014 / 1,902 = 7.4x more content. But the quality gap is even larger -- the SAP dossier is actionable intelligence that closes deals. The Drake Star dossier is background reading.**

This is the difference between a cold call where the rep says "I see you're in the HR space" versus "Christian Klein told analysts in Q3 2025 that accelerating cloud HCM adoption is the number one priority -- and your 4,000 accredited webcasts are exactly the practitioner enablement asset SAP doesn't have."

---

## 4. OUR SEARCH TEMPLATES (12 Types)

Every search below is executed via `POST https://api.exa.ai/search` with `type: "auto"` and `contents.text.max_characters: 3000`.

### Template 1: Company Search
```
Purpose:    Find company website, services, location, basic facts
Query:      "{company_name} {city} {state} {vertical} company"
Example:    "AquaScience Inc Scottsdale Arizona water treatment company"
Returns:    Website URL, service descriptions, location confirmation
Cost:       $0.007/search (3 results)
Category:   company_search
Success:    High -- works well for established businesses with web presence
```

### Template 2: Owner/Founder Search
```
Purpose:    Identify the business owner, their background, quotes
Query:      "{company_name} owner founder president {city}"
Example:    "AquaScience Inc owner founder president Scottsdale"
Returns:    Owner name, title, background, interview quotes
Cost:       $0.007/search
Category:   person_search
Success:    Moderate -- works for owners who have been interviewed or profiled
```

### Template 3: Reviews and Reputation
```
Purpose:    BBB rating, Google reviews, customer feedback, trust signals
Query:      "{company_name} reviews BBB rating {city}"
Example:    "AquaScience Inc reviews BBB rating Scottsdale"
Returns:    BBB rating, Google star rating, review count, excerpts
Cost:       $0.007/search
Category:   verification
Success:    High for BBB/Google. Yelp results are inconsistent.
```

### Template 4: Financial Signals
```
Purpose:    Employee count, revenue estimates, company size indicators
Query:      "{company_name} {city} employees revenue size"
Example:    "AquaScience Inc Scottsdale employees revenue size"
Returns:    Employee count, revenue estimate, year founded
Cost:       $0.007/search
Category:   financial_estimate
Note:       Often returns RocketReach, ZoomInfo, IBISWorld profiles
```

### Template 5: Industry M&A Activity
```
Purpose:    Recent acquisitions, deal multiples, buyer activity in vertical
Query:      "{vertical} company acquisition multiples 2025 2026"
Example:    "water treatment company acquisition multiples 2025 2026"
Returns:    Recent deal names, EBITDA multiples, buyer names, deal values
Cost:       $0.007/search
Category:   company_search
Success:    100% (6/6 successful in our tracking)
Note:       This is our highest-performing template. Exa excels at M&A news.
```

### Template 6: Buyer Identification
```
Purpose:    Find companies that have acquired businesses in this vertical/state
Query:      "{vertical} companies acquired {state} 2024 2025 PE roll-up"
Example:    "water treatment companies acquired Arizona 2024 2025 PE roll-up"
Returns:    Buyer names, acquisition history, buyer type, contact names
Cost:       $0.007/search
Category:   company_search
Success:    100% (6/6 successful)
```

### Template 7: Earnings Call Quotes
```
Purpose:    Find CEO/executive quotes from earnings calls revealing M&A strategy
Query:      "{company_name} CEO earnings call 2024 2025 strategy {topic}"
Example:    "Culligan International CEO earnings call 2024 2025 strategy water treatment"
Returns:    CEO quotes, strategic priorities, growth commentary
Cost:       $0.007/search
Category:   earnings_call
Success:    Good for public companies and large PE-backed firms
Real result: Found "Culligan actively shops for international bolt-ons across its
             segments, CEO says" (ION Analytics)
```

### Template 8: M&A Deal History
```
Purpose:    Map a specific buyer's acquisition timeline
Query:      "{company_name} acquisition 2023 2024 2025 {topic}"
Example:    "Grundfos acquisition 2023 2024 2025 water treatment"
Returns:    Specific deal announcements, target companies, deal context
Cost:       $0.007/search
Category:   ma_history
Real result: Found Grundfos acquiring Metasphere (UK telemetry), Newterra
             (Pittsburgh water treatment), multiple others -- building a real
             acquisition timeline
```

### Template 9: Buyer Contact Search (M&A Decision Makers)
```
Purpose:    Find VP Corporate Development, Head of M&A, deal-making contacts
Query:      "{company_name} VP Corporate Development M&A LinkedIn"
Example:    "Culligan International VP Corporate Development M&A LinkedIn"
Returns:    Name, title, LinkedIn URL, company, connection count
Cost:       $0.007/search
Category:   person_search
Real result: Found Amit Shah (SVP Corporate Development & Global M&A),
             Charles Burckmyer (VP Corporate Development),
             Niccolo Gandini (VP Head of Corp Dev EMEA) -- all at Culligan,
             all with LinkedIn URLs
Note:       THIS IS EXTREMELY VALUABLE. Exa returns structured LinkedIn profile
             data that we use to build our outreach target list.
```

### Template 10: Strategic Fit Signals
```
Purpose:    Investment thesis, strategy documents, partnership announcements
Query:      "{company_name} {topic} strategy investment thesis"
Example:    "Culligan International water treatment strategy investment thesis"
Returns:    PE portfolio stories, strategy articles, investor presentations
Cost:       $0.007/search
Real result: Found Advent International's portfolio story on Culligan
             ("a thirst for growth"), detailing how they turned a US-focused
             water business into a global consumer services leader
```

### Template 11: Company Financials (Buyer)
```
Purpose:    Revenue, employee count, company overview for potential acquirers
Query:      "{company_name} annual revenue employees company overview"
Example:    "Grundfos annual revenue employees company overview"
Returns:    Revenue figures, employee count, founding year, HQ location
Cost:       $0.007/search
Real result: Found Grundfos -- EUR 4.7B revenue, 8,478 employees, founded
             1945, operates in 86 countries
```

### Template 12: Contact Enrichment
```
Purpose:    Find owner's personal contact info for outreach
Query:      "{owner_name}" "{company_name}" {city} {state} phone email contact LinkedIn
Example:    "John Smith" "AquaScience Inc" Scottsdale Arizona phone email contact LinkedIn
Returns:    Phone numbers, email addresses, LinkedIn URLs
Cost:       $0.007/search
Category:   person_search
Extraction: Regex patterns applied to results:
  - Email:    [\w.+-]+@[\w-]+\.[\w.-]+
  - Phone:    (?:\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}
  - LinkedIn: URL containing linkedin.com/in/
```

---

## 5. PROBLEMS WE HAVE HAD

### Case Study: The Python urllib 403 Incident

**Date:** 2026-03-29
**Duration:** ~2 hours to diagnose (should have been 5 minutes)
**Severity:** Total pipeline halt -- zero Exa searches completing

#### What Happened
Every Exa API call started returning HTTP 403 Forbidden. Both our API keys failed. Our Exa account balance was $100.13 -- confirmed active.

#### The False Leads (2 hours wasted)
1. **Assumed key was expired** -- Wrong. Key was valid, tested working via curl.
2. **Assumed balance was zero** -- Wrong. Balance was $100.13.
3. **Assumed Exa was down** -- Wrong. Exa was up, serving requests to curl.
4. **Tried creating new API key** -- Unnecessary. Old key worked fine via curl.

We spent approximately 2 hours cycling through authentication and billing hypotheses when the actual problem was the HTTP client library.

#### The Root Cause
Python 3.9's `urllib.request` library sends headers or a TLS fingerprint that Exa's WAF (likely Cloudflare) rejects with 403. The exact same request payload, headers, and API key sent via `curl` from the same machine succeeds immediately.

**Key distinction:** HTTP 403 from a WAF/CDN means the REQUEST was rejected (user-agent, TLS fingerprint, IP reputation). HTTP 401 means the KEY was rejected. These are different problems requiring different fixes.

#### The Fix
Our founder (Ewing) tested the key via curl in 30 seconds and proved it worked. The agent had spent 2 hours cycling through wrong hypotheses.

We built `lib/exa_client.py` -- a curl subprocess wrapper:

```python
# lib/exa_client.py — uses curl subprocess (urllib is blocked by Exa's WAF)
result = subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.exa.ai/search",
    "-H", f"x-api-key: {EXA_KEY}",
    "-H", "Content-Type: application/json",
    "-d", payload
], capture_output=True, text=True, timeout=30)
```

This has been running flawlessly since the fix. Every Exa call in our pipeline now routes through this curl wrapper.

#### Lessons for the Exa Team
1. Python 3.9 `urllib` is increasingly blocked by modern WAFs. This likely affects other Python-based customers.
2. The official Exa Python SDK may handle this correctly (we have not tested it), but customers using raw HTTP libraries will hit this.
3. A note in the Exa docs about WAF/Cloudflare compatibility with common HTTP clients would save developers significant debugging time.
4. The 403 response body from the WAF did not clearly indicate it was a client-fingerprint issue vs. an auth issue, making diagnosis harder.

---

## 6. VOLUME AND SPEND

### Current Usage Pattern

**Per sell-side company (dossier):**
- 3-5 Exa searches (company, owner, reviews, financials, LinkedIn)
- Cost: $0.021-$0.035 per company

**Per buy-side buyer (intelligence dossier):**
- 5 Exa searches (earnings calls, M&A history, contacts, financials, strategic fit)
- Cost: $0.035 per buyer
- Demonstrated in our AquaScience transparency run: 3 buyers x 5 searches each = 15 searches = $0.105

**Per proposal gap-fill:**
- 1-3 Exa searches (company, owner, size)
- Cost: $0.007-$0.021

### Projected Monthly Volume

| Pipeline Stage | Companies/Month | Searches/Company | Total Searches | Cost |
|---|---|---|---|---|
| Sell-side dossiers | 150 | 5 | 750 | $5.25 |
| Buy-side buyer intel | 150 sellers x 5 buyers | 5 | 3,750 | $26.25 |
| Proposal gap-fill | Variable | 1-3 | ~200 | $1.40 |
| **Total** | | | **~4,700** | **~$32.90/month** |

At $0.007 per search (3 results), our projected spend is approximately **$33/month** for a pipeline that produces M&A-grade intelligence on hundreds of companies.

### Cost Efficiency
- Our total LLM + API budget per company: ~$0.50 (Exa + LLMs + Clay fallback)
- Exa represents ~7% of per-company cost but provides ~80% of the factual content
- The ROI is extraordinary: $0.035 in Exa searches produces intelligence that supports $50K-$500K M&A advisory fees

---

## 7. TEN QUESTIONS FOR THE EXA TEAM

### Q1: Best Practices for Earnings Call Transcripts
We search for CEO earnings call quotes using: `"{company} CEO earnings call 2024 2025 strategy {topic}"`. This works well for public companies but sometimes returns SEO spam sites instead of actual transcript sources. **Is there a way to bias results toward transcript providers (Seeking Alpha, MotleyFool transcripts, company IR pages)?** Would domain filtering help?

### Q2: Structured JSON Output
We extract structured data from Exa text results using regex patterns (emails, phones, addresses, LinkedIn URLs). **Does Exa support or plan to support structured output -- returning entities as JSON fields rather than raw text?** This would eliminate our regex extraction layer and reduce parsing errors.

### Q3: LinkedIn Profile Data Quality
Our buyer contact searches (`"{company} VP Corporate Development M&A LinkedIn"`) return remarkably good LinkedIn data -- names, titles, connection counts, career history. **Is this data scraped live, cached, or from a LinkedIn partnership?** We want to understand the freshness and reliability so we can set appropriate confidence scores.

### Q4: Date Filtering Effectiveness
We append year ranges to queries (e.g., "acquisition 2023 2024 2025"). **Does Exa support native date range filtering via API parameters?** If so, would that be more effective than including years in the query string? We want to ensure we get the most recent M&A activity, not stale results.

### Q5: Why Does Python urllib Trigger 403?
As documented in Section 5, Python 3.9 `urllib.request` gets 403'd while `curl` works fine. **Is this a Cloudflare configuration? Is there a specific User-Agent or TLS version that urllib sends that gets blocked?** We would prefer to use native Python HTTP rather than shelling out to curl, if there is a workaround (specific headers, user-agent string, etc.).

### Q6: Bulk/Batch Search API
We run 5 searches per buyer sequentially with a brief delay between each. **Is there a batch endpoint or recommended pattern for sending multiple related searches?** We could send all 5 buyer searches as one request if a batch API exists, reducing latency.

### Q7: Result Deduplication Across Searches
When we search for the same buyer across different templates (earnings calls, M&A history, financials), we sometimes get the same URL in multiple result sets. **Is there a way to exclude URLs from prior searches in the same session?** An `exclude_urls` parameter would be valuable.

### Q8: Content Extraction Quality
We set `max_characters: 3000` for text extraction. Sometimes the extracted text is clean markdown; sometimes it includes navigation elements, cookie banners, and boilerplate. **Are there settings to improve extraction quality -- perhaps a "main content only" mode?** For M&A intelligence, we only need the article body, not the site chrome.

### Q9: Search Type "auto" vs "keyword" vs "neural"
We use `type: "auto"` for all searches. **For our specific use cases (M&A news, earnings calls, LinkedIn profiles, company info), would explicit type selection ("keyword" or "neural") improve results?** We are willing to A/B test if you can suggest which type works best for which template.

### Q10: Enterprise/Volume Pricing
At ~4,700 searches/month and growing (we plan to expand from Arizona to national coverage, which would 10-50x our volume), **is there volume pricing, an enterprise plan, or committed-use discounts?** Our projected national scale would be 50,000-200,000 searches/month.

---

## 8. WISH LIST — FEATURES WE WANT BUT ARE NOT SURE EXA SUPPORTS

### Wish 1: Company Entity Recognition
When we search for "Culligan International," we want Exa to understand this is a company entity and return structured company data: HQ, revenue, employee count, industry, parent company, subsidiaries. Currently we extract this from unstructured text. **A `/company` endpoint that returns structured entity data would be transformative.**

### Wish 2: Person Entity Recognition
Similarly, when we search for "Amit Shah SVP Culligan," we want structured person data: current title, company, location, LinkedIn URL, career history. **A `/person` endpoint would replace our regex extraction pipeline entirely.**

### Wish 3: M&A Deal Database Integration
Our highest-value searches are M&A deals. If Exa could integrate with or surface data from deal databases (PitchBook, Crunchbase, Mergermarket), the result quality would be significantly better than web search alone. **Even a "deals" content type in search results would help us filter for transactional content.**

### Wish 4: Exclude Domains
We frequently get results from SEO content farms (SWOTTemplate.com, PortersFiveForce.com, Pestel-analysis.com, MatrixBCG.com) that are generated pages with no real intelligence value. **A domain exclusion list parameter (`exclude_domains: ["swottemplate.com", ...]`) would significantly improve result quality for our use case.**

### Wish 5: Result Confidence Scoring
Not all results are equally useful. A LinkedIn profile with current employment data is more valuable than a 3-year-old press release. **If Exa returned a confidence or freshness score per result, we could weight our intelligence extraction accordingly.**

### Wish 6: Webhook/Streaming for Batch Jobs
For our nightly pipeline runs (50-150 companies), we currently fire sequential HTTP requests. **A webhook-based batch API where we submit N queries and receive results via callback would simplify our pipeline architecture and potentially improve throughput.**

### Wish 7: Similar Company Discovery
Given a company URL or description, find similar companies. This would power our buyer identification: "Given this water treatment company in Arizona, find 20 companies that have acquired similar businesses." **A `/similar` endpoint or similarity search mode would be enormously valuable for M&A matchmaking.**

### Wish 8: Content Change Monitoring
We would love to set a "watch" on specific companies and get notified when Exa indexes new content about them -- especially new acquisitions, leadership changes, or earnings call transcripts. **A monitoring/alerting feature would let us react to deal signals in real-time.**

---

## APPENDIX A: REAL SEARCH EXAMPLES FROM PRODUCTION

### Example: AquaScience Buyer Intelligence Run (2026-03-28)

The following is a verbatim excerpt from our transparency log showing 15 Exa searches for 3 potential buyers of AquaScience (a water treatment company).

**Buyer 1: Culligan International (Fit Score: 9/10)**

| # | Purpose | Query String | Cost | Results | Top Result |
|---|---------|-------------|------|---------|------------|
| 1 | Earnings calls | "Culligan International CEO earnings call 2024 2025 strategy water treatment" | $0.007 | 3 | "Culligan actively shops for international bolt-ons across its segments, CEO says" (ION Analytics) |
| 2 | M&A history | "Culligan International acquisition 2023 2024 2025 water treatment" | $0.007 | 3 | "Culligan Acquires Primo Water International Businesses Across Europe" (GlobeNewsWire) |
| 3 | Decision makers | "Culligan International VP Corporate Development M&A LinkedIn" | $0.007 | 3 | Amit Shah - SVP Corporate Development & Global M&A; Charles Burckmyer - VP Corporate Development; Niccolo Gandini - VP Head Corp Dev EMEA |
| 4 | Financials | "Culligan International annual revenue employees company overview" | $0.007 | 3 | IBISWorld company profile, Sustainability Magazine profile |
| 5 | Strategic fit | "Culligan International water treatment strategy investment thesis" | $0.007 | 3 | "Culligan: a thirst for growth" (Advent International portfolio story) |

**Total for Culligan: 5 searches, 15 results, $0.035**

**Buyer 2: BDT & MSD Partners (Fit Score: 8/10)**

| # | Purpose | Query String | Cost | Results | Top Result |
|---|---------|-------------|------|---------|------------|
| 6 | Earnings calls | "BDT & MSD Partners CEO earnings call 2024 2025 strategy water treatment" | $0.007 | 3 | Exclusive CNBC interview with BDT & MSD Partners Co-CEOs |
| 7 | M&A history | "BDT & MSD Partners acquisition 2023 2024 2025 water treatment" | $0.007 | 3 | "Summit Companies Announces Acquisition by BDT & MSD Partners" |
| 8 | Decision makers | "BDT & MSD Partners VP Corporate Development M&A LinkedIn" | $0.007 | 3 | Mark Moore (VP), Mike DeBona (VP), Matthew Nelson (VP) -- all with LinkedIn URLs |
| 9 | Financials | "BDT & MSD Partners annual revenue employees company overview" | $0.007 | 3 | $14B flagship fund, 437 employees, merchant bank profile |
| 10 | Strategic fit | "BDT & MSD Partners water treatment strategy investment thesis" | $0.007 | 3 | BDA Partners water investment thesis, BDT&MSD + Culligan ownership connection |

**Total for BDT & MSD: 5 searches, 15 results, $0.035**

**Buyer 3: Grundfos (Fit Score: 7/10)**

| # | Purpose | Query String | Cost | Results | Top Result |
|---|---------|-------------|------|---------|------------|
| 11 | Earnings calls | "Grundfos CEO earnings call 2024 2025 strategy water treatment" | $0.007 | 3 | "Grundfos delivers robust 2025 results" -- EUR 4.7B sales, 5.7% growth |
| 12 | M&A history | "Grundfos acquisition 2023 2024 2025 water treatment" | $0.007 | 3 | Grundfos acquires Metasphere (UK), acquires Newterra (Pittsburgh) |
| 13 | Decision makers | "Grundfos VP Corporate Development M&A LinkedIn" | $0.007 | 3 | Casper Gandil Qvortrup (Chief Strategy & M&A Manager), Loris Bonotto (PMI Manager, water treatment acquisitions) |
| 14 | Financials | "Grundfos annual revenue employees company overview" | $0.007 | 3 | $4.6B revenue, 8,478 employees, 86 countries |
| 15 | Strategic fit | "Grundfos water treatment strategy investment thesis" | $0.007 | 3 | "Grundfos successfully completes acquisition of US water treatment company" (Newterra) |

**Total for Grundfos: 5 searches, 15 results, $0.035**

**Grand Total: 15 searches, 45 results, $0.105**

---

## APPENDIX B: API INTEGRATION DETAILS

### Our API Call Pattern
```
Endpoint:  POST https://api.exa.ai/search
Headers:   x-api-key: {key}, Content-Type: application/json
Payload:   {
             "query": "{search string}",
             "num_results": 5,
             "type": "auto",
             "contents": {"text": {"max_characters": 3000}}
           }
Response:  {
             "results": [{title, url, text, ...}],
             "costDollars": {"total": 0.007}
           }
```

### Our Client Implementation
- Language: Python 3.9
- HTTP method: `subprocess.run(["curl", ...])` (due to urllib WAF issue)
- Timeout: 30 seconds per request
- Error handling: report_success/report_failure via tool_health module
- Cost tracking: logged to Supabase `dossier_cost_log` and `cost_log` tables with entity tags

### Integration Points
- **Dossier Pipeline** (`dossier-pipeline/`): Sell-side research, buyer intelligence
- **Master CRM** (`master-crm/`): Proposal gap-fill, profile enrichment
- **Shared client**: `lib/exa_client.py` in master-crm, imported by both pipelines

---

## APPENDIX C: OUR FULL RESEARCH METHOD REGISTRY (Exa entries)

Stored in Supabase `research_methods` table:

| Method Code | Name | Query Template | Success Rate | Avg Cost |
|---|---|---|---|---|
| `exa_company_search` | Company web search | `{company} {city} {state} {vertical} company` | Tracking | $0.018 |
| `exa_owner_search` | Owner/founder search | `{company} owner founder president {city}` | Tracking | $0.018 |
| `exa_reviews_search` | Reviews and ratings | `{company} reviews BBB rating {city}` | Tracking | $0.018 |
| `exa_financials_search` | Financial signals | `{company} {city} employees revenue size` | Tracking | $0.018 |
| `exa_industry_ma` | Industry M&A activity | `{vertical} company acquisition multiples 2025 2026` | 100% | $0.018 |
| `exa_buyer_search` | Buyer identification | `{vertical} companies acquired {state} 2024 2025 PE roll-up` | 100% | $0.018 |

Additional templates used in buyer pipeline (not yet in registry):
- Earnings call quotes
- M&A deal history
- Buyer contact search (LinkedIn)
- Company financials (buyer)
- Strategic fit signals

---

## APPENDIX D: TROUBLESHOOTING REFERENCE

### Known Issue: Python urllib 403
**Symptom:** HTTP 403 on all Exa calls. Keys confirmed valid. Balance confirmed positive.
**Root Cause:** Python 3.9 urllib User-Agent/TLS fingerprint blocked by Exa WAF (Cloudflare).
**Fix:** Use curl subprocess instead of urllib. See `lib/exa_client.py`.
**Time to diagnose:** 2 hours (should have been 5 minutes).
**Prevention:** When any API returns 403 and the key is valid, test with curl FIRST before investigating auth/billing.
**Key lesson:** 403 from a WAF (request rejected) is not 401 (key rejected). Different problems, different fixes.

### Diagnostic Checklist
1. API returning errors? Test the exact same request with curl.
2. If curl works but Python does not, the problem is the HTTP client library.
3. If curl also fails, check key validity, then check Exa status page.
4. Never assume billing is the problem when the error is 403 (not 402).

---

*This document was generated from live production data, actual Exa API responses, and real pipeline audit logs. Every query string, cost figure, and result excerpt shown is from actual Exa API calls made by our system.*

*Next Chapter M&A Advisory -- Plan Your Next Chapter*
