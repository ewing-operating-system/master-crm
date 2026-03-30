# Meeting Page v2 — Data Collection Engine
**Build**: Feature 1 of Next 10
**Status**: Ready for implementation
**Est. Time**: 4-5 hours
**Priority**: CRITICAL (feeds everything downstream)

---

## OVERVIEW

The meeting page transforms from a read-only agenda into a **live data capture form** that feeds research → letter generation → proposal → buyer targeting.

**Old Meeting Page**: Agenda + talking points + danger zones (read-only)
**New Meeting Page v2**: Interactive form + auto-save + post-meeting summary + downstream generation

---

## PAGE STRUCTURE

### Section 1: Meeting Setup (Top of Page)
```
Meeting Details
- Company Name: [read-only, pre-filled]
- Rep Name: [read-only, current user]
- Meeting Date: [datetime picker]
- Scheduled Duration: [duration picker, default 30 min]
- Notes: [textarea, auto-save]

Data Completeness Progress Bar
"You've captured 3/12 fields • 25% complete"
```

### Section 2: During-Meeting Form (Main Content)
**Auto-saves after every field change to localStorage**

#### Card 1: Owner Motivation
```
Why is the owner considering a transaction?

Question (Dropdown):
- [ ] Looking to exit / cash out
- [ ] Exploring options / "curious"
- [ ] Growing fast, need capital
- [ ] Burn out, want to sell
- [ ] Partner/family situation
- [ ] Tax planning

Verbatim Quote:
[textarea] "What did they literally say about why?"

Confidence (Slider 1-10):
[slider visualization]
```

#### Card 2: Timeline
```
What's their timeline for a transaction?

Question (Dropdown):
- [ ] 3 months (ASAP)
- [ ] 6 months
- [ ] 12 months
- [ ] 18+ months
- [ ] No timeline / testing waters

Confidence (Slider 1-10):
[slider visualization]

Real Timeline Notes:
[textarea] "Do they have life events driving this? Retirement date?"
```

#### Card 3: Revenue & Growth
```
Business Size & Growth Profile

Annual Revenue (est.):
[currency input] e.g., $1,200,000

Service vs. New Install Split:
Service: [slider] 60%
New Install: [slider] 40%

Recurring Revenue:
[slider] 35% (maintenance contracts, subscriptions)

Growth Rate YoY:
[number input] e.g., 15%

Growth Driver Notes:
[textarea] "How did they grow? Organic, acquisition, market, team?"
```

#### Card 4: Margin Profile
```
Profitability & Owner Perks

Estimated Annual Profit (EBITDA):
[currency input] e.g., $320,000

EBITDA Margin %:
[slider] 27%

Owner Perks (add-backs):
- Vehicle allowance: [currency input]
- Family member salary: [currency input]
- Travel / entertainment: [currency input]
- Insurance / benefits overages: [currency input]

Total Add-backs:
[auto-calculated] $85,000

Adjusted EBITDA:
[auto-calculated] $405,000

Notes:
[textarea] "Any unusual expenses or perks not listed?"
```

#### Card 5: Key People & Retention
```
Team Depth & Dependency

Technical Leader / Operations:
Name: [text input]
Years with company: [number]
Can they stay post-sale? [Yes/No radio]
Criticality: [dropdown: Essential / Important / Helpful]

Sales/Business Development Lead:
Name: [text input]
Years with company: [number]
Can they stay post-sale? [Yes/No radio]
Criticality: [dropdown: Essential / Important / Helpful]

Other Key Employee:
Name: [text input]
Role: [text input]
Years with company: [number]
Can they stay post-sale? [Yes/No radio]
Criticality: [dropdown: Essential / Important / Helpful]

Owner Dependency:
[slider] 1-10 (1 = business runs itself, 10 = owner in everything)

Owner Transition Readiness:
[textarea] "Can owner step back? Is there depth below them?"
```

#### Card 6: Deal Breakers
```
Non-Negotiables & Hidden Objections

What must happen (checkboxes, multiple select):
- [ ] Acquire the whole company (not just assets)
- [ ] Don't buy my customer list separately
- [ ] Need me to stay as operator / not be replaced
- [ ] Need all proceeds upfront (no earnout)
- [ ] Must keep employees on payroll
- [ ] Must maintain current location

Deal Killer Questions (Answers indicate STOP):
What would make you walk away?
[textarea] e.g., "If they won't keep my team", "If they push me out immediately"

Hidden Concerns Not Yet Stated:
[textarea] "What are they not saying but you sense?"
```

#### Card 7: Emotional Temperature
```
Owner Mindset & Personality Type

How Ready Are They? (1-10 scale)
[slider labeled:]
1: "Desperate to sell"
5: "Exploring, no pressure"
10: "Suspicious, defensive"

Personality Type (pick primary):
- [ ] Analytical (wants spreadsheets, data, proof)
- [ ] Gut-trusting (wants story, relationship, feeling)
- [ ] Data-driven (wants comparisons, benchmarks, history)
- [ ] Story-driven (wants narrative, context, meaning)

Emotional Vibe Notes:
[textarea] "How did they seem? Excited? Anxious? Confident?"
```

#### Card 8: Story Elements Captured
```
Their Company Origin & Culture

Why did they start this business?
[textarea] "What's the founder story?"

Biggest Challenge They've Overcome:
[textarea] "What near-death experience or pivot changed them?"

Community/Local Impact:
[textarea] "Sponsorships? Volunteer work? Awards? Local reputation?"

Team Culture & Workplace:
[textarea] "How do employees talk about this company? Why do they stay?"

Quirky/Memorable Details:
[textarea] "Anything unique about the company? Unusual service? Memorable name story?"

Personal Facts About Owner:
[textarea] "Background, values, what drives them beyond money?"
```

### Section 3: Post-Meeting Output (After form is complete)

#### Auto-Generated Meeting Summary
```
🤖 AI-Generated Summary (Click to edit)

[3-paragraph narrative summary, auto-generated from form data]

Paragraph 1: Who they are, what they do, why they started
Paragraph 2: Current business performance, growth story, strengths
Paragraph 3: Why they're considering a sale now, timeline, deal breakers

[Edit button for rep to refine]
```

#### Data Completeness Scorecard
```
Data Collected: 12/12 (100%)
✅ Owner Motivation: Captured
✅ Timeline: Captured
✅ Revenue & Growth: Captured
✅ Margin Profile: Captured
✅ Key People: Captured
✅ Deal Breakers: Captured
✅ Emotional Temperature: Captured
✅ Story Elements: Captured
[and 4 more...]

What This Unlocks:
✓ Personalized Letter Generation — Use this data to write operator-friendly letter
✓ Interactive Proposal — Auto-populate valuation, timeline, buyer profile
✓ Ideal Buyer Profile — Match characteristics to buyer priorities
✓ Next Action Recommendations
```

#### Next Steps & Action Items
```
Based on this meeting, here's what's next:

Recommended Next Steps (in order):
1. Generate Personalized Letter (will reference their story, their timeline)
2. Create Interactive Proposal (will show valuation range based on their margins)
3. Identify Ideal Buyers (will suggest 3-5 buyers who fit their deal structure)
4. Schedule Follow-up Call (suggest 3 dates based on their timeline preference)

Buttons (High visibility):
[GREEN BUTTON] Generate Personalized Letter
[BLUE BUTTON] Create Interactive Proposal
[GRAY BUTTON] Identify Ideal Buyers
[GRAY BUTTON] Schedule Follow-up
```

---

## TECHNICAL IMPLEMENTATION DETAILS

### Data Storage
**localStorage keys**:
- `meeting_<company_id>_form` — entire form state as JSON
- `meeting_<company_id>_lastSaved` — timestamp
- Auto-save every field change

**Supabase table** (`meetings` table):
```sql
CREATE TABLE meetings (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  rep_id UUID REFERENCES reps(id),
  meeting_date TIMESTAMP,
  owner_motivation TEXT,
  owner_motivation_confidence INT,
  timeline TEXT,
  timeline_confidence INT,
  annual_revenue DECIMAL,
  service_percentage INT,
  recurring_revenue_percentage INT,
  growth_rate INT,
  estimated_ebitda DECIMAL,
  ebitda_margin INT,
  owner_perks JSONB,
  key_people JSONB,
  deal_breakers JSONB,
  emotional_temperature INT,
  personality_type TEXT,
  story_elements JSONB,
  auto_summary TEXT,
  data_completeness_score INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Form Validation
- Required fields: Owner Motivation, Timeline, Annual Revenue, EBITDA Margin
- Optional fields: All others
- Completeness score = (filled_fields / 12) * 100

### Post-Meeting Summary Generation
1. Form data submitted
2. LLM prompt constructs narrative from captured data
3. 3 paragraphs returned (intro, current state, why selling now)
4. Display for rep to edit/approve
5. Save to Supabase `meetings.auto_summary`

### Buttons Logic
```
Generate Letter:
- POST /api/generate-letter with meeting_id + research_id
- Returns: letter_text, personalization_score
- Opens in new window: proposal page with letter pre-populated

Create Proposal:
- POST /api/generate-proposal with meeting_id + company_id
- Returns: HTML proposal
- Renders interactive proposal page

Identify Buyers:
- POST /api/match-buyers with meeting_id
- Returns: [buyer1, buyer2, buyer3] sorted by fit score
- Displays as cards with match reasoning

Schedule Follow-up:
- Opens calendar picker, suggests 3 times based on owner timeline
- Creates calendar event, sends them invite
```

---

## UI/UX DESIGN

### Color Scheme
- Progress bar: Green when >75%, Yellow 50-75%, Red <50%
- Required fields: Red asterisk, error state in pink
- Sliders: Blue thumb, gradient fill from gray to blue
- Buttons: Green (primary action), Blue (secondary), Gray (disabled)

### Responsiveness
- Mobile: Stack cards vertically, full-width form
- Tablet: 2-column grid for related fields
- Desktop: 3-column grid, sidebar with completeness tracker

### Accessibility
- All sliders labeled with min/max values
- Color not the only indicator (text labels + icons)
- Tab order follows logical flow
- Submit button disabled until required fields filled

---

## TESTING CHECKLIST

### Functionality
- [ ] Form auto-saves after every field change
- [ ] localStorage persists across page refresh
- [ ] Completeness score updates in real-time
- [ ] Required field validation works
- [ ] Sliders bind to number inputs bidirectionally
- [ ] Post-meeting summary generates without error
- [ ] LLM summary is 3 paragraphs, readable prose
- [ ] "Generate Letter" button pre-fills letter with meeting data
- [ ] "Create Proposal" button creates personalized proposal

### Mobile
- [ ] Form fields stack properly on iPhone
- [ ] Sliders work with touch
- [ ] Buttons ≥48px tap target
- [ ] Load time <3s on 4G
- [ ] No horizontal scroll needed

### Data Quality
- [ ] All 12 fields captured correctly
- [ ] Revenue/margin calculations accurate
- [ ] Perks add-backs calculate correctly
- [ ] Personality type stored and usable
- [ ] Story elements pull through to letter generation

---

## DEPLOYMENT

### Files to Create
1. `/meeting-page-v2.html` — Main form page
2. `/css/meeting-form.css` — Styling
3. `/js/meeting-form.js` — Form logic, auto-save, validation
4. `/js/meeting-summary.js` — Post-meeting LLM generation

### Files to Modify
1. `index.html` — Link to meeting page
2. `/lib/supabase-client.js` — Add meetings table methods
3. `CLAUDE.md` — Add meeting data to entity rules

### Vercel Deployment
- Push to `ewing-operating-system/master-crm-web`
- Auto-deploys to `master-crm-web-eight.vercel.app/meeting-page-v2.html`

---

**Document Created**: 2026-03-30 14:30 MST
**Version**: 1.0 — Ready for Build
**Next**: Implement as Feature 1 of Next 10
