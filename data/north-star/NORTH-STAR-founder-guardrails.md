# FOUNDER GUARDRAILS — Ewing Gillaspy

**Source:** 15 design decisions across 4 rounds of questioning, 2026-03-29
**Status:** NORTH STAR — every agent, engine, template, and page must comply with these rules
**Authority:** These override any default behavior, any model suggestion, any optimization shortcut

---

## SECTION 1: THE STANDARD

### The Gold Standard Engagement
A letter triggers an inbound call (recorded from the start — every touch recorded, transcribed, logged, merged, deduped, always on). Customer says "not sure, send me info." System builds their deal room + plan page. Customer plays with knobs, assumptions, storybuilder. Likes what they see. Clicks "let's get started now!" Picks a contract option. Instantly gets letters to edit, approve, send. Salesfinity lists load. LinkedIn automation fires. Agent fact-finding calls begin. Information from every touch refines targeting automatically. Zero human work after the initial call.

**Every feature is measured against this standard.**

### The Core Principle: All About Them, Nothing About Us
Every touchpoint — letter, email, call, meeting, proposal, data room, outreach — is framed around THEIR business, THEIR options, THEIR story. Never about us. We are the invisible engine that makes them look like the smartest decision-maker in the room.

---

## SECTION 2: PERSONALIZATION RULES

### Fair Game (use freely)
- Industry data, market multiples, M&A activity in their vertical
- Public information: podcasts, interviews, press mentions, awards, BBB, Google reviews
- Calculated estimates WITH DISCLOSED METHODOLOGY
- Company facts: years in business, service area, certifications, licenses
- Growth signals from public sources

### Off Limits (never use, even if found)
- Divorce, family disputes, personal legal issues
- Store closures, employee arrests, lawsuits
- Negative sentiment scoring or negative facts of ANY kind
- Anything that could be perceived as harmful personalization

### Transparency Rule
When estimating or calculating, ALWAYS disclose the method: "Since it's hard to find information about you, I used industry standard [formula]." Education is king. They appreciate knowing HOW you got the number as much as WHAT the number is. Never guess blindly.

### Insufficient Data Cascade
When the system can't find enough data to personalize:
1. **First (C):** Send with explicit honesty. Frame the gap as a compliment: "We couldn't find much about your company online, which usually means you're running a tight ship without needing to market. Here's what we know about companies like yours in [city]..."
2. **Second (B):** If even industry data is thin, send a shorter education-focused letter with market multiples and vertical trends.
3. **Last resort (A):** Skip entirely until more data is found.
4. **NEVER send low quality.** Quality score >= 80 → full personalized. Score 50-79 → honesty frame. Score 30-49 → industry education. Score < 30 → skip.

---

## SECTION 3: DEAL KILLERS

These must NEVER happen. They destroy trust permanently.

1. **Hallucinated personalization.** A letter that references a fact about the wrong company, wrong owner, wrong city. If the first thing they read is wrong, trust is destroyed permanently.
2. **Wildly inaccurate estimates.** Revenue, employee count, or locations that are obviously wrong.
3. **Sending with nothing to go on.** Don't send a generic letter pretending it's personalized.

### The Fix
Multi-agent double verification is worth the money. ALWAYS. Every fact that appears in customer-facing content must be confirmed by two independent LLMs from different model families. Certifier must REJECT if any customer-facing fact lacks dual-LLM verification. Minimum data threshold: company_name + owner_name + city + at least ONE of (revenue estimate, employee count, years in business) OR the letter doesn't generate.

---

## SECTION 4: ENTITY PRIORITY

**RevsUp first. Next Chapter second. AND Capital third.**

Smaller sale comes first. Earn trust, then expand. If a person could be served by multiple entities:
1. Start with the smallest/simplest engagement
2. Deliver results
3. THEN introduce the larger opportunity
4. Never pitch two entities simultaneously on first contact

---

## SECTION 5: LISTENER AGENT RULES

### Channel Behavior
- Multi-channel signals about the same person/company merge into ONE diagnosis, not separate plays
- "Send me an email" ALWAYS gets the full play: dossier subset + market multiples delighter + data room link. Never a simple one-liner.
- ALL callers scanned by default: Mark, Ewing, John. Entity routing uses person-to-entity rules.

### Auto-Trust
- 10 consecutive human approvals with zero edits before a play can auto-execute
- ANY edit (even minor) resets the approval count to zero
- Auto-execute ALWAYS runs final inspection agent (Claude CLI certification with timestamp)
- If inspection FAILS, falls back to draft mode and notifies human
- If human REJECTS a previously auto-approved play, resets approval count to zero permanently

### New Situations
- Draft a best-guess play, create it in the play library, name it, define it
- Label as [NEW PLAY — first time seen, review carefully]
- Provide editable knobs for easy modification
- Flag for review but don't block the pipeline

### Multi-Rep Overlap
- Auto-merge into one unified record
- Notify both reps immediately via iMessage
- "[Argus] Overlap detected: {company} — Mark had a call 3/15, Ewing got an email 3/18. Merged."

---

## SECTION 6: FEE STRUCTURE MODES

Every play can be configured with one of five fee disclosure modes:

| Mode | What It Says | When To Use |
|------|-------------|-------------|
| `none` | No fee mention at all | Early outreach, cold letters |
| `framework_only` | "We work on a success-fee basis, aligned with your outcome" | First meetings, qualification |
| `median_market_disclosure` | "Typical advisory fees in your market range from X to Y" | Education-focused follow-ups |
| `proposed_working_fee` | Specific fee proposal for this client | Proposals, engagement setup |
| `interactive_models` | 3 fee structure options on interactive page | Premium proposals, competitive situations |

---

## SECTION 7: COMPETITOR RESPONSE

When a prospect mentions talking to another broker:
1. IMMEDIATE escalation — priority CRITICAL
2. Compile industry package for their vertical
3. Generate risk-free offer: "90 days, no fee, 2 qualified buyers or we fire ourselves"
4. Create customer-facing page with the package
5. Notify Mark, Ewing, or ops channel to review
6. Never auto-execute competitive responses (too high stakes)

The guarantee is real but deal-size dependent:
- Below threshold: full guarantee as stated
- Above threshold: negotiated terms (longer timeline, more buyers, different structure)
- Threshold is a configurable knob

---

## SECTION 8: PAGE ARCHITECTURE

### Every Page Has Dual Views
- **Admin view:** See everything. All targets, all data, all internal notes, all strategy.
- **Client view:** Curated. Only what we choose to show. Toggle per page, per session.
- We control what the customer sees at all times
- Internal strategy never leaks to client view

### Prospect Control Level
- Before signing: view only (they see the plan, can't change it)
- After signing: light editing (revenue, employee count, service mix — plan regenerates)
- They CANNOT change narrative, strategy, buyer targeting, or outreach approach
- Admin can edit everything always

---

## SECTION 9: RESPONSE SPEED

### Speed is Gated by Quality Score
- Quality >= 80 AND urgency = hot → send within the hour
- Quality 50-79 OR urgency = warm → hold for improvement, same business day
- Quality < 50 → hold for human review, do not auto-send
- NEVER send a low quality score regardless of urgency

### Real-Time Call Intel
- During live calls: push silent notification to rep's screen with relevant data
- Simultaneously: draft follow-up email so it's ready the SECOND the call ends
- Rep sounds smarter on the call, follow-up lands while conversation is still fresh

---

## SECTION 10: THE MONDAY MORNING DASHBOARD

Ewing opens laptop and sees 9 sections:

1. **Campaigns to RUN** — approve new batches, activate paused campaigns
2. **Quality tuning** — which systems need output quality adjustment
3. **New rules needed** — questions from last week's runs that need human decisions
4. **Agent performance** — time saved, research completed, letters sent, proposals built, quality scores
5. **Outbound activity** — touches by channel: agent-phone, human-phone, LinkedIn, email, letter
6. **Revenue metrics** — contracts signed, revenue closed, revenue moved stages
7. **Problem identification** — flagged calls or transcripts to review
8. **Agent requests** — agents requesting new tools, skills, or plays they couldn't find
9. **Spend** — total system spend by category, by vendor, by sales stage

---

## SECTION 11: COMMUNICATION RULES

### Language
- NEVER say "private equity." Say: "former business owners who cashed out and buy companies because they believe in owners, not the stock market."
- Letters are about THEM. "We help business owners like you plan their next chapter."
- Frame problems from THEIR perspective: "prevent leaks" not "replace roof." "Plan your next chapter" not "sell your business."

### iMessage Format
- Start with [Argus]
- Include lettered choices (A, B, C)
- Describe temporary vs permanent consequences
- Keep short — they're reading on a phone

### Reporting
- NEVER generate reports from memory. ALWAYS read actual data first.
- ALWAYS disclose NEEDS_REVIEW validation status. Never hide it.
- ALWAYS use actual cost averages from logs for projections. Never round down.
- Mark DeChant reviews everything.

---

## SECTION 12: TECHNICAL RULES

### Data
- Every row in every transactional table MUST carry an `entity` field
- DNC is universal — one block = blocked everywhere, all entities, all channels
- Campaign names carry entity prefix: AND-, NC-, RU-
- Old names are WRONG — always use the Name Crosswalk
- Never wipe records. Store incrementally. Re-run, don't wipe.

### Pipeline
- Letters send BEFORE phone calls. Enrichment is post-letter investment.
- Multi-LLM consensus required before any customer-facing document
- is_step_done() before every API call — never duplicate spend
- Claude CLI ($0.00) for all quality-critical work. Paid APIs for fast extraction only.
- If Claude CLI fails: DUAL fallback — both OpenAI AND DeepSeek run the same prompt, cross-check results
- If a key fails: STOP and report. Do NOT sign up for a replacement.

### Cost
- NC: $5/day cap, AND: $3/day, RU: $1/day, System: $2/day
- 80% alert via iMessage. 100% pauses paid APIs (Claude CLI continues free).
- Per-record cost tracking: company costs separate from contact costs
- Log every API call with tool, operation, cost, timestamp

---

*This document is the supreme authority for agent behavior. When in doubt, check here first. When guardrails conflict with efficiency, guardrails win.*
