# Next Chapter — Full Lifecycle Vision

**Source:** Ewing Gillaspy, 2026-03-29
**Status:** NORTH STAR — this is the spec for how Next Chapter operates end-to-end

---

## The Core Principle: All About Them, Nothing About Us

Every touchpoint — letter, email, call, meeting, proposal, data room, outreach — is framed around THEIR business, THEIR options, THEIR story. Never about us. We are the invisible engine that makes them look like the smartest decision-maker in the room.

### The Roofing Door-Knock Analogy (the standard we're building to)

The best outbound roofers don't say "we replace roofs." They say:
1. "You got hit by hail on [specific date from Hailtrace]"
2. "Your insurance covers storm damage for [policy duration] months"
3. "Today minus storm date = you have [calculated days] left to file"
4. "Leaks from that storm won't show for [calculated weeks] because water has to penetrate [insulation → attic → sheetrock → accumulate]"
5. "I'm not surprised you don't have a leak yet"

Every fact is: real, verifiable, about THEM, strung together in a way they've never heard before. The rep becomes a wizard of relevant facts. Trust is built without disclosing a single fact about the rep's company.

**This methodology applies to Next Chapter at every stage.**

---

## The 8 Stages of Next Chapter

### Stage 1: DISCOVERY (marketing)
**What we have today:** TAM scraping, Exa enrichment, Clay, Salesfinity calls
**What we're doing:** Finding home services business owners who might sell

**The standard:** Letters that disrupt email. Content that is ALL about them:
- Their company's estimated revenue range
- Their industry's current M&A multiples
- Their specific market's buyer activity
- Their years in business and what that means for timing
- Their options based on where they are

### Stage 2: FIRST CONTACT (letter + cold call)
**What we have today:** Letter engine, cold call scripts, Salesfinity dialer
**What we're doing:** Breaking pattern, causing inspection, building trust

**The standard:**
- Letter references specific facts about THEIR business (not generic)
- Cold call opener references the letter
- Every fact is verifiable ("go check, I'll wait")
- Follow-up email is a SUBSET of collected information, explicitly mapped to their request
- Plus adjacent related information they didn't ask for but is relevant
- Plus a "delighter" — market multiples calculator, "what is your company worth" tool
- Final touch: a data room link with email gating ("click to request access")
- Nobody does this. We can. That's the differentiator.

### Stage 3: QUALIFICATION (first meeting / call)
**What we have today:** Fireflies transcripts, call analysis, manual notes
**What we're doing:** Determining if they're a fit, what they want, timeline

**The standard:**
- Structured data capture from the call
- Slider bars for their business profile (revenue, employees, service mix, geography)
- Places to put their story, uncommon information, growth levers
- Their top 3 strengths documented
- Buy-side vs sell-side determination
- Complete narrative and battle plan emerges from inputs

### Stage 4: PROPOSAL (the killer blow)
**What we have today:** blank-canvas-proposal repo, manual template editing
**What we need:** Highly customizable yet very structured template proposal engine

**The standard:**
- Single prompt + knobs/sliders/inputs → complete ready-to-send proposal
- Their company logo, website, quotes, nuances from conversation
- Attack plan for selling or buying
- What's needed from them (but not blocking us now)
- Link to sign and get started immediately
- Place for them to access and EDIT the letters we're sending to target buyers
- "Illusion of control" — they approve/edit letters, taking send approval off our plate
- If letters are bad, they'll tell us. Otherwise, we scale without being the bottleneck.

### Stage 5: ENGAGEMENT SETUP (signed client)
**What we have today:** Manual process
**What we need:** Automated account setup engine

**The standard:**
- Buy-side vs sell-side engagement configuration
- Information needed about them that we don't have yet (changes targeting)
- Sample targets found with rich information
- Storyboard built (to buyer or to seller)
- Data room about THEIR company
- Outreach scripts for contacting buyers/sellers
- Listing sites if needed
- Full account plan including:
  - DNC checks on all targets
  - Geographic map display for territory concerns
  - Contact information obtained for targets
  - Approach strategy: "we know the owners" (maintains leverage) vs "this company is for sale" (destroys leverage)
- Mind-blowing breadth, depth, detail, scripting

### Stage 6: BUYER/SELLER OUTREACH (the automated part)
**What we have today:** Basic outreach queue, dialer queue
**What we need:** "Who would buy my company?" as a self-service + on-demand engine

**The standard:**
- Automated buyer discovery (should be orderable by client or triggered automatically)
- Per-buyer research dossier
- Per-buyer outreach script (approach: "we represent the owners" not "this is for sale")
- Multi-channel: letter, email, call, LinkedIn
- DNC enforcement before every touch
- Geographic targeting for buyer fit

### Stage 7: DEAL MANAGEMENT (active meetings + negotiations)
**What we have today:** Fireflies transcripts, manual notes
**What we need:** Meeting-by-meeting intelligence engine

**The standard:**
- Every meeting gets its own custom web page
- ONLY relevant to that meeting on that day
- Data and information linked, queryable in a single text box
- Master checklist and project plan objectives front and center
- Statuses, recommendations, data to support everything
- Inspecting: call transcripts, emails to/from customer
- Prepping: next phase templates, meeting preparation materials
- Handoff: qualified conversation template for next call

### Stage 8: CLOSE + POST-CLOSE
**What we have today:** Nothing automated
**What we need:** Transaction completion, fee collection, relationship maintenance

---

## The Engine Pairing Model

Every business process needs two things:
1. **Structured process definition** — what happens, in what order, with what inputs/outputs
2. **Agent ready to execute** — the automation that does the work

| Stage | Process Need | Agent/Engine |
|-------|-------------|-------------|
| Discovery | Find target companies | Scout agent + TAM engine |
| Discovery | Classify by entity | Classifier agent |
| Discovery | Research company | Researcher agent (dual-LLM) |
| Discovery | Validate facts | Validator agent |
| First Contact | Write personalized letter | Executor agent (Claude CLI) |
| First Contact | Generate cold call script | Executor agent (Claude CLI) |
| First Contact | Send letter | Dispatcher agent (Lob/Handwrytten) |
| First Contact | Load dialer | Dispatcher agent (Salesfinity API) |
| First Contact | Follow-up email | Executor agent (Claude CLI) — subset of collected info + delighter |
| First Contact | Data room generation | **NEW: data_room_engine** — email-gated page per prospect |
| Qualification | Capture call data | Tracker agent (Fireflies) |
| Qualification | Profile builder | **NEW: profile_engine** — slider bars, business profile |
| Qualification | Top 3 strengths | Claude CLI analysis from dossier + call transcript |
| Proposal | Generate proposal | **NEW: proposal_engine** — template + knobs + inputs → PDF/web |
| Proposal | Client portal | **NEW: client_portal** — logo, quotes, plan, sign link, letter editor |
| Engagement | Account setup | **NEW: engagement_engine** — buy/sell config, info gathering |
| Engagement | Target discovery | Researcher agent reused for buyer/seller discovery |
| Engagement | Storyboard generation | Claude CLI — narrative for each target |
| Engagement | Data room build | data_room_engine reused — per-engagement |
| Outreach | Buyer outreach | Executor agent — per-buyer scripts |
| Outreach | Multi-channel dispatch | Dispatcher agent — letter, email, call, LinkedIn |
| Deal Mgmt | Meeting page generator | **NEW: meeting_engine** — per-meeting web page |
| Deal Mgmt | Transcript analysis | Tracker agent — extract action items, next steps |
| Deal Mgmt | Status updates | Claude CLI — client-facing status reports |
| Deal Mgmt | Handoff templates | Claude CLI — qualified conversation handoff |

---

## What We Need to Build (NEW engines not yet designed)

1. **data_room_engine** — generates email-gated web pages per prospect/client with company-specific data
2. **profile_engine** — interactive business profile builder with slider bars and structured fields
3. **proposal_engine** — template + inputs → complete proposal with sign link and letter editor
4. **client_portal** — client-facing dashboard where they see their plan, edit letters, track progress
5. **engagement_engine** — automated account setup for signed clients (buy/sell config, targeting)
6. **meeting_engine** — per-meeting custom web page with relevant data, checklist, recommendations

---

## The Shortcut

In some cases, the system goes from lead → action plan → market-and-sell-their-business so fast and so comprehensively that:
1. The prospect sees the plan
2. They know they can't run it themselves
3. They hire the company that built it (us)
4. We skip multiple sales stages because the PLAN is the sales tool

This means the proposal engine IS the sales engine. The quality of the plan closes the deal.
