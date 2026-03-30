# Agent Playbook: Research-to-React Page Creator

## What This Is

This is the exact, repeatable process for building structured React/Vercel webpages from raw research. It has been used twice successfully:

1. **Sell-Side M&A Advisory Proposal** — home services vertical (HVAC, plumbing, pest, roofing)
2. **Buy-Side Target Criteria** — precast concrete vertical (underground, highway, agricultural)

Any agent or LLM can follow this playbook to produce the same quality output for any new vertical, client, or page type.

---

## PHASE 1: DEEP RESEARCH

### 1.1 — Parallel Web Searches (Run All at Once)

Every page starts with 4–8 simultaneous web searches. The goal is breadth first, depth second. You are looking for industry-specific data, fee structures, valuation multiples, deal terms, market size, key players, and terminology.

**Search pattern — always run these categories simultaneously:**

| Category | Search Query Template | Example (Precast Concrete) |
|----------|----------------------|---------------------------|
| Industry + M&A | `"[vertical] company acquisition criteria M&A buy side due diligence [year]"` | `"precast concrete company acquisition criteria M&A buy side due diligence 2025 2026"` |
| Valuation | `"[vertical] industry valuation multiples EBITDA private equity acquisitions"` | `"precast concrete industry valuation multiples EBITDA private equity acquisitions"` |
| Target Screening | `"[vertical] manufacturer acquisition target screening criteria bolt-on platform"` | `"precast concrete manufacturer acquisition target screening criteria bolt-on platform"` |
| Certifications | `"[industry body] [vertical] certification requirements plant quality compliance"` | `"NPCA ACPA precast concrete certification requirements plant quality compliance"` |
| Market Size | `"[vertical] market size growth infrastructure spending [current drivers] [year]"` | `"precast concrete market size growth infrastructure spending IIJA data centers 2025 2026"` |
| Recent Deals | `"[major buyer] [vertical] acquisition strategy [target company] bolt-on criteria"` | `"CMC Commercial Metals precast acquisition strategy Foley Products CP&P bolt-on criteria"` |
| Fee Structure | `"[vertical] M&A advisory fee structure engagement fee success fee retainer [deal size]"` | `"home services M&A advisory fee structure engagement fee success fee retainer sell side buy side"` |
| Process/Timeline | `"M&A advisory [side] process timeline phases marketing [vertical]"` | `"M&A advisory sell side process timeline phases marketing CIM buyer outreach"` |

**How to find the right queries:**

1. Start with the vertical name + "M&A" + "acquisition" + current year
2. Look at what comes back — identify the major industry associations (NPCA, ACPA, PCI for precast; ACCA for HVAC; NPMA for pest)
3. Look for the biggest recent deals in the space — search those specifically
4. Look for industry-specific valuation reports — First Page Sage, Capstone Partners, BMI Mergers, and Equidam publish these

### 1.2 — WebFetch Deep Dives (Run 3–4 After Initial Searches)

After the initial searches return URLs, fetch the 3–4 most data-rich pages for detailed extraction:

**What to fetch:**
- Valuation multiple reports (First Page Sage, Capstone Partners, BMI Mergers)
- M&A market update reports (Capstone Partners publishes monthly by sector)
- Industry association certification pages (NPCA, ACPA, etc.)
- Recent deal announcements (PR Newswire, company press releases)

**What to extract from each page:**
- Exact numbers: multiples, deal values, market size, growth rates
- Named companies: buyers, sellers, platforms, targets
- Fee ranges: by deal size, by service type
- Timelines: deal process phases, typical durations
- Terminology: industry-specific terms the client will expect to see

### 1.3 — Internal Data Mining (MCP Tools)

If the agent has access to the client's tools (Gmail, Fireflies, Google Drive, Salesfinity, Slack), mine them in parallel with web research.

**Fireflies — transcript search:**
```
keyword:"[company name]" scope:all limit:20
keyword:"[contact name]" scope:all limit:20
keyword:"[vertical keyword]" scope:all limit:20
```
Then fetch individual transcripts by ID and extract:
- Product preferences (what they want, what they exclude)
- Geographic targets (states, regions, markets)
- Financial criteria (EBITDA range, revenue range, multiple tolerance)
- Deal structure preferences (buyout %, owner transition, retention)
- Named target companies
- Deal breakers (explicit hard stops)
- Certifications discussed

**Gmail — email search:**
```
from:[contact_email]
to:[contact_email]
subject:[company name]
[company name] OR [vertical keyword]
```
Read every email thread. Extract:
- Criteria shared in writing (these are the most reliable — the client typed them)
- Target company names mentioned
- Fee structures agreed to
- Pipeline stats (how many scored, narrowed, activated)
- Anything the client pushed back on or explicitly excluded

**Google Drive — document search:**
```
[company name]
[vertical keyword]
[contact name]
```
Look for: proposals, engagement letters, target lists, scoring sheets, CIMs.

**Salesfinity — call logs:**
```
python <skill-path>/scripts/salesfinity_api.py --action get-call-logs
```
Look for cold call recordings and notes that may contain initial criteria from discovery calls.

### 1.4 — What You're Building From Research

By the end of Phase 1, you should have a data file (mental or actual) with:

| Data Point | Source Priority | Example |
|-----------|----------------|---------|
| Product criteria (must/nice/excluded) | Client transcripts > Client emails > Industry research | Storm pipe: REQUIRED. Architectural: EXCLUDED. |
| Geographic targets | Client transcripts > Client emails | Primary: MS, AL, GA, SC, NC, TN. Excluded: AR. |
| EBITDA / Revenue ranges | Client transcripts > Client emails > Industry benchmarks | $1M–$5M EBITDA |
| Valuation multiples | Industry research > Client intel > Recent deals | Building Materials $1–3M: 7.3x |
| Deal structure | Client transcripts > Client emails | 100% buyout, owner exits, team stays |
| Certifications | Client transcripts > Industry research | NPCA required, PCI excluded |
| Named targets | Client emails > Client transcripts | Lee's Precast, Triple M, Precast Solutions NC |
| Deal breakers | Client transcripts > Client emails | Zoning issues, wrong product mix, cultural mismatch |
| Fee structure | Client emails > Engagement letter > Industry benchmarks | 2% existing deals, 2.5% sourced, $30K retainer |
| Market context | Industry research only | $160B+ market, 4.2–6.3% CAGR |
| Recent comparable deals | Industry research only | CMC/Foley $1.84B at 10.3x |
| Process timeline | Industry research > Prior engagement experience | 4 phases, 6–9 months |

**Source priority rule:** Client's own words > Client's written communications > Industry research. Never let research override what the client explicitly said.

---

## PHASE 2: DATA ARCHITECTURE

### 2.1 — The CONFIG Object Pattern

Every page is powered by a single JavaScript object at the top of the file. This is the key architectural decision — it means:
- Agents only need to swap one object to create a new page
- The React components never change
- The template version has `{{variables}}`, the populated versions have real data
- Any LLM can generate a valid CONFIG object from research findings

**Template version (agents fill in the blanks):**
```javascript
const CONFIG = {
  client: {
    companyName: "{{company_name}}",
    contactName: "{{contact_name}}",
    // ...
  },
  products: {
    mustHave: [
      // { name: "Product Name", description: "Why it's required" }
    ],
    // ...
  },
};
```

**Populated version (real client data):**
```javascript
const CONFIG = {
  client: {
    companyName: "Design Precast & Pipe",
    contactName: "Chris Fore",
    // ...
  },
  products: {
    mustHave: [
      { name: "Storm & Sewer Pipe", description: "RCP, elliptical, arch pipe for storm and sanitary sewer" },
    ],
    // ...
  },
};
```

### 2.2 — CONFIG Object Sections (Buy-Side Criteria)

The buy-side criteria CONFIG has these sections. Every section must be populated or left as `{{variable}}`:

```
CONFIG
├── client          — Company name, contact, HQ, strategy, prior acquisitions
├── products        — mustHave[], niceToHave[], excluded[], minimumOverlapPct, notes
├── geography       — primaryStates[], secondaryStates[], excludedStates[], maxShipRadius, notes
├── financials      — ebitdaMin/Max, revenueMin/Max, marginMin, multipleRange, maxMultiple, notes
├── dealStructure   — acquisitionType, ownerTransition, earnout, retention, holdPeriod, rollupIntent
├── certifications  — required[], preferred[], excluded[], dotApproval, notes
├── facility        — plantSize, yard, crane, batchPlant, environmental, fleet
├── workforce       — headcount, keyRoles[], laborPreference, retention, safety
├── customers       — minCount, maxConcentration, endMarkets[], contractType, backlog, govtPct
├── dealBreakers    — string[] of hard stops
├── namedTargets    — { name, location, status, priority, notes }[]
└── marketContext   — industrySize, growthRate, keyDrivers[], multiples{}, recentDeals[], trends{}
```

### 2.3 — CONFIG Object Sections (Sell-Side Proposal)

The proposal CONFIG is called `PROPOSAL` and has these sections:

```
PROPOSAL
├── firm        — name, tagline, phone, email, website
├── client      — ownerName, companyName, vertical, revenue, EBITDA, margins, etc.
├── engagement  — type, fees, timeline, exclusivity
├── valuation   — multiples (low/mid/high), EV range, adjustments
├── market      — multiple range, active buyers, comps[]
├── process     — phases[] with title, weeks, color, tasks[]
├── buyers      — strategic[], pePlatforms[], peAddOns[], independents[]
├── fees        — scenarios[] with EV, successFee, retainer, total
└── credentials — deals[], team[], testimonials[]
```

### 2.4 — Status Indicator System

Every populated field gets a visual status:
- **Green dot** = field has real data (not a `{{variable}}`)
- **Amber dot** = field has partial data
- **Gray dot** = field is still a `{{variable}}` or empty

The component checks this with:
```javascript
const isSet = (v) => v && !v.startsWith("{{");
const statusOf = (v) => isSet(v) ? "set" : "unset";
```

This lets the client and the agent see at a glance what's populated and what still needs work.

---

## PHASE 3: REACT/VERCEL PAGE ARCHITECTURE

### 3.1 — File Structure

Every page is a single `.jsx` file. No external CSS. No external dependencies beyond React. This makes it:
- Deployable to Vercel with zero config
- Readable by any agent
- Editable by swapping the CONFIG object only

### 3.2 — Design System (Reuse This Exactly)

```javascript
const colors = {
  navy: "#0F1A2E",          // Headers, backgrounds
  navyLight: "#1B2A45",     // Gradient endpoint
  accent: "#2563EB",        // Links, highlights
  gold: "#D4A843",          // Brand accent, labels
  green: "#059669",          // Set/required/active
  red: "#DC2626",            // Excluded/deal breaker
  amber: "#D97706",          // Partial/warning
  surface: "#FFFFFF",        // Card backgrounds
  surfaceMuted: "#F8FAFC",   // Page background
  border: "#E2E8F0",         // Card borders
  textPrimary: "#0F172A",    // Main text
  textSecondary: "#475569",  // Descriptions
  textMuted: "#94A3B8",      // Labels, timestamps
};

const fonts = {
  heading: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",  // Numbers, values
};
```

### 3.3 — Component Library (Reuse These)

Every page reuses these components. Do not reinvent them:

| Component | Purpose | Used In |
|-----------|---------|---------|
| `SectionDivider` | Section header with icon, title, subtitle | Every tab |
| `CriteriaCard` | Single value with label, status dot, optional subtext | Overview, Financials, Deal, Facility |
| `TagList` | Colored pill tags for lists (states, products, markets) | Geography, Products, Customers |
| `ProductRow` | Product with REQUIRED/PREFERRED/EXCLUDED badge | Products, Certifications |
| `StateMap` | Three-tier geography display (primary/secondary/excluded) | Geography |
| `TargetRow` | Named target with priority, status badge, notes | Targets |
| `DealRow` | Comparable transaction (buyer, target, value, multiple) | Market Intel |
| `MultipleBar` | Horizontal bar showing valuation range on scale | Financials, Market Intel |
| `NotesBox` | Italic notes/context box (hidden if `{{variable}}`) | Every tab |
| `MetricCard` | Large number with label (for pipeline stats) | Overview |
| `PhaseCard` | Process phase with timeline and task list | Process |
| `FeeTable` | Fee scenario comparison table | Fees |
| `ValuationBar` | Valuation range with low/mid/high markers | Valuation |

### 3.4 — Tab Navigation Pattern

Every page uses tabbed navigation. Tabs sit inside the navy header and use white background for active state:

```javascript
const TABS = [
  { id: "overview", label: "Overview" },
  { id: "products", label: "Products" },
  // ... etc
];

// Active tab: white bg, navy text, bold
// Inactive tab: transparent bg, gray text, normal weight
```

**Buy-Side Criteria tabs:** Overview, Products, Geography, Financials, Deal Structure, Facility, Certifications, Targets, Market Intel

**Sell-Side Proposal tabs:** Overview, Market, Valuation, Process, Buyers, Fees, Credentials, Next Steps

### 3.5 — Page Layout

```
┌─────────────────────────────────────────┐
│  NAVY GRADIENT HEADER                    │
│  Gold label: "Buy-Side Target Criteria"  │
│  White H1: Company Name                  │
│  Gray subtitle: Strategy description     │
│  Right: "Next Chapter Advisory" + date   │
│                                          │
│  [Tab] [Tab] [Tab] [Tab] [Tab]          │
├─────────────────────────────────────────┤
│                                          │
│  TAB CONTENT (max-width: 1100px)        │
│                                          │
│  SectionDivider → Grid of Cards         │
│  SectionDivider → List of Items         │
│  NotesBox                                │
│                                          │
├─────────────────────────────────────────┤
│  FOOTER: Company — Page Type — Conf.    │
└─────────────────────────────────────────┘
```

---

## PHASE 4: POPULATING CLIENT CONFIGS

### 4.1 — From Transcripts to CONFIG

When you have Fireflies transcripts, extract data into CONFIG fields using this mapping:

| What the client says | CONFIG field | Example |
|---------------------|-------------|---------|
| "We need storm pipe, sewer pipe, manholes" | `products.mustHave[]` | `{ name: "Storm & Sewer Pipe", description: "..." }` |
| "No architectural" / "We don't want X" | `products.excluded[]` | `{ name: "Architectural Precast Only", description: "..." }` |
| "At least 40% overlap" | `products.minimumOverlapPct` | `"40%"` |
| "Southeast — MS, AL, GA" | `geography.primaryStates[]` | `["MS", "AL", "GA"]` |
| "Not as interested in AR" | `geography.excludedStates[]` | `["AR"]` |
| "$1M to $5M EBITDA" | `financials.ebitdaMin/Max` | `"$1M"` / `"$5M"` |
| "100% buyout only" | `dealStructure.acquisitionType` | `"100% buyout only"` |
| "Owners exit, teams stay" | `dealStructure.ownerTransition` | `"Owner exits — team stays"` |
| "NPCA is damn near required" | `certifications.required[]` | `{ name: "NPCA Plant Certification", description: "..." }` |
| "NOT interested in PCI" | `certifications.excluded[]` | `{ name: "PCI Plant Certification", description: "..." }` |
| "The deal has to feel right" | `dealBreakers[]` | `"Cultural mismatch — 'the deal has to feel right'"` |
| "We're looking at Lee's Precast" | `namedTargets[]` | `{ name: "Lee's Precast", location: "North MS", status: "active", priority: 1 }` |

### 4.2 — From Emails to CONFIG

Emails often contain the most precise data because the client took time to write it:

| Email content type | CONFIG field | Priority |
|-------------------|-------------|----------|
| Named companies in body | `namedTargets[]` | Highest — client explicitly identified these |
| Fee agreement | `financials.notes` or separate fee section | Highest — contractual |
| Pipeline numbers ("470 scored, 200 narrowed") | Custom `pipelineStats` section | High — shows engagement depth |
| Product exclusions ("no contractors, no chemical companies") | `products.excluded[]` | Highest — client's hard no |
| Geographic requests ("Savannah is high priority") | `geography.notes` and reorder `primaryStates` | High |

### 4.3 — From Research to CONFIG (Market Context)

Research data fills the `marketContext` section. Never let it override client-stated preferences.

| Research finding | CONFIG field |
|-----------------|-------------|
| Market size ($160B+) | `marketContext.industrySize` |
| Growth rate (4.2–6.3% CAGR) | `marketContext.growthRate` |
| IIJA spending, data centers, Buy America | `marketContext.keyDrivers[]` |
| EBITDA multiples by size tier | `marketContext.ebitdaMultiples{}` |
| CMC/Foley, NWPX/Boughton's deals | `marketContext.recentDeals[]` |
| Total M&A deals, PE share, YOY growth | `marketContext.constructionMATrends{}` |
| NPCA/ACPA/PCI descriptions | `marketContext.certificationLandscape{}` |

---

## PHASE 5: FILE DELIVERY

### 5.1 — Files to Produce

Every run of this playbook produces 3+ files:

| File | Purpose | Naming Convention |
|------|---------|-------------------|
| `[type]-template.jsx` | Master template with `{{variables}}` | `buyside-criteria-template.jsx` |
| `[type]-[client-slug].jsx` | Client-specific populated page | `buyside-criteria-design-precast.jsx` |
| `grab-[type].sh` | Shell script to move files to working directory | `grab-buyside-criteria.sh` |
| `agent-playbook-[type].md` | This document (the playbook itself) | `agent-playbook-page-creator.md` |

### 5.2 — Shell Script Pattern

Always produce a shell script that copies files to a permanent working directory:

```bash
#!/bin/bash
mkdir -p ~/Documents/[project-folder]
cp ~/Downloads/[file1] ~/Documents/[project-folder]/
cp ~/Downloads/[file2] ~/Documents/[project-folder]/
cp ~/Downloads/[file3] ~/Documents/[project-folder]/
echo "Done. Files are in ~/Documents/[project-folder]/"
ls -la ~/Documents/[project-folder]/
```

### 5.3 — Delivery Format

Save every file to Downloads. Provide `computer://` links. Provide one terminal command to move them.

---

## PHASE 6: REPLICATION FOR NEW VERTICALS

### 6.1 — To Build a New Vertical's Pages

1. **Copy the template .jsx** — rename it for the new vertical
2. **Run Phase 1 searches** — replace `[vertical]` with the new industry
3. **Identify the industry's equivalents:**

| Precast Concrete | New Vertical Equivalent |
|-----------------|------------------------|
| NPCA / ACPA | [Industry certification body] |
| Storm pipe, manholes | [Core products] |
| CMC, Foley Products | [Major acquirers] |
| IIJA infrastructure | [Key demand driver] |
| 150–300 mile ship radius | [Geographic constraint] |
| DOT / municipal customers | [Primary customer type] |

4. **Rebuild the CONFIG object** with new vertical's data
5. **If adding tabs**, add to the TABS array and create new tab component
6. **If removing tabs**, remove from TABS array (component is just not rendered)

### 6.2 — Verticals Already Built

| Vertical | Template | Status |
|----------|----------|--------|
| Home Services (HVAC, plumbing, pest, roofing) | `proposal-template.jsx` | Complete — sell-side proposal |
| Precast Concrete (underground, highway, ag) | `buyside-criteria-template.jsx` | Complete — buy-side criteria |

### 6.3 — Verticals Queued for Future

These use the same playbook — just swap the research queries and CONFIG data:

- Home Services Buy-Side Criteria
- Precast Concrete Sell-Side Proposal
- Electrical Contractors (both sides)
- Landscaping / Hardscaping (both sides)
- Mechanical Contractors (both sides)

---

## EXACT SEARCHES USED (REFERENCE LOG)

### Sell-Side Proposal (Home Services) — 7 Searches + 4 Fetches

**Searches:**
1. `"M&A advisory engagement letter proposal template home services HVAC plumbing business broker"`
2. `"home services M&A advisory fee structure engagement fee success fee retainer sell side buy side"`
3. `"lower middle market M&A advisory proposal sections business broker home services trades"`
4. `"M&A investment banking pitch book proposal template for service businesses"`
5. `"home services HVAC plumbing M&A valuation multiples EBITDA 2025"`
6. `"M&A advisory proposal sell side process timeline phases marketing CIM buyer outreach"`
7. `"success fee engagement fee percentage lower middle market business broker $1M $5M $10M"`

**Fetches:**
1. Morgan & Westfield broker agreements page
2. First Page Sage fee structure report
3. Eton VS fee guide
4. Cobrief proposal template

### Buy-Side Criteria (Precast Concrete) — 8 Searches + 2 Fetches

**Searches:**
1. `"precast concrete company acquisition criteria M&A buy side due diligence 2025 2026"`
2. `"precast concrete industry valuation multiples EBITDA private equity acquisitions"`
3. `"precast concrete manufacturer acquisition target screening criteria bolt-on platform"`
4. `"NPCA ACPA precast concrete certification requirements plant quality compliance"`
5. `"precast concrete market size growth infrastructure spending IIJA data centers 2025 2026"`
6. `"CMC Commercial Metals precast acquisition strategy Foley Products CP&P bolt-on criteria"`
7. First Page Sage EBITDA multiples for construction (WebFetch)
8. Capstone Partners Construction M&A Update Feb 2026 (WebFetch)

### Client Data Mining (Both Clients)

**Design Precast & Pipe (Chris Fore):**
- Fireflies: `keyword:"design precast" scope:all limit:20` → 14 transcripts
- Fireflies: `keyword:"chris fore" scope:all limit:20` → same set
- Gmail: `from:cfore@designprecast.com` → 38 emails
- Gmail: `to:cfore@designprecast.com` → 32 emails
- Gmail: `design precast` → 70+ total threads
- Google Drive: `design precast` → 0 results (all data was in email/transcripts)

**Wieser Concrete (Andy Wieser):**
- Fireflies: `keyword:"wieser" scope:all limit:20` → found transcript "Andy Wieser + Next Chapter (11 am EST)" Dec 15, 2025
- Gmail: `wieser OR wieserconcrete` → 11 emails (note: "weiser" returns 0 — correct spelling is "wieser")
- Gmail: Mark's recap email Dec 16, 2025 contained full criteria summary
- Google Drive: `wieser` → 0 results

---

## KEY DATA EXTRACTED (REFERENCE TABLES)

### EBITDA Multiples — Building Materials / Construction (Q4 2024)

| Segment | $0–1M EBITDA | $1–3M EBITDA | $3–5M EBITDA |
|---------|-------------|-------------|-------------|
| Building Materials | 5.4x | 7.3x | 9.8x |
| Civil Engineering | 6.8x | 8.7x | 11.9x |
| PE Average (all construction) | — | 10.6x | — |
| Strategic Average (all construction) | — | 7.5x | — |

### Construction M&A Activity (2025)

| Metric | Value |
|--------|-------|
| Total deals | 562 |
| YOY growth | +18.2% |
| PE buyer share | 54.3% (first time > strategic) |
| New PE platforms | 68 |
| Sponsor-backed add-ons | 237 (+41.4% YOY) |
| Subcontractor deals | 366 (65.1% of total) |

### Recent Precast Concrete Deals

| Buyer | Target | Value | Multiple | Year |
|-------|--------|-------|----------|------|
| CMC (Commercial Metals) | Foley Products | $1.84B | 10.3x EBITDA | 2025 |
| CMC | Concrete Pipe & Precast (CP&P) | Undisclosed | ~10x est. | 2025 |
| CP&P (pre-CMC) | Dellinger / Winchester / Precast Supply | Undisclosed | N/A | 2024 |
| NWPX Infrastructure | Boughton's Precast | Undisclosed | N/A | 2026 |

### Precast Concrete Market Drivers

| Driver | Data Point |
|--------|-----------|
| IIJA infrastructure | $1.2T through 2026+ |
| Data center construction | +138% YOY to $53.7B (2025) |
| Buy America / BABA | Domestic manufacturing mandated for federal projects |
| EPA wastewater infrastructure | $271B needed |
| Construction labor shortage | 80%+ of contractors report hiring difficulty |
| Input cost inflation | +3.4% YOY |

### Certification Landscape

| Certification | What It Covers | Recognition |
|--------------|---------------|-------------|
| NPCA Plant Certification | All precast products | 40+ states, 75+ municipalities, ANSI-accredited |
| ACPA Quality Cast | Concrete pipe specifically | Pipe-focused state DOT requirements |
| PCI | Prestressed structural (bridges, beams) | Different market — structural, not underground |

---

## RULES FOR THE AGENT

1. **Run all searches in parallel.** Never run one search, wait, then run the next. Batch 4–8 at once.
2. **Client data overrides research.** If Chris Fore says "NPCA is damn near required" and your research says "NPCA is optional," the CONFIG says REQUIRED.
3. **Use the exact design system.** Navy, gold, Inter, monospace for numbers. Do not redesign.
4. **One CONFIG object per file.** All data lives at the top. Components never change.
5. **Template uses `{{variables}}`.** Populated versions use real strings. The `isSet()` function handles both.
6. **Every field has a status dot.** Green = populated. Gray = template variable. This is visual feedback for the client.
7. **Notes fields are free-text context.** Use them to capture nuance that doesn't fit structured fields ("Chris specifically requested Lee's Precast in North MS").
8. **marketContext is research-only.** Fill it from web searches and WebFetch. It provides industry context the client didn't explicitly state.
9. **namedTargets come from the client.** Never add targets the client didn't mention unless asked to.
10. **dealBreakers are the client's exact words** where possible. Quote them ("the deal has to feel right").
11. **Produce 3 files minimum:** template, populated config, shell script.
12. **Save to Downloads. Provide computer:// links. Provide one terminal command.**
13. **Spelling matters.** Wieser not Weiser. Design Precast not DesignPrecast. Verify before searching.
14. **If a data source returns 0 results, try alternate spellings and search terms before giving up.**
15. **The shell script must be a file, not a raw command.** Save it as `.sh` and tell the user to run `bash ~/Downloads/[filename].sh`.

---

## QUICK-START FOR A NEW PAGE

**Agent receives:** "Build a buy-side criteria page for [Client Name] in [Vertical]."

**Agent does:**

1. Run 6–8 parallel web searches for the vertical (copy query templates from Phase 1)
2. Run Fireflies search for client name + vertical keywords
3. Run Gmail search for client contact email (from: and to:)
4. Run Google Drive search for client name
5. WebFetch top 3–4 data-rich URLs from search results
6. Read all transcripts and emails — extract criteria into CONFIG field mapping (Phase 4)
7. Fill marketContext from research data (Phase 4.3)
8. Copy `buyside-criteria-template.jsx` → rename for client
9. Replace CONFIG object with populated data
10. Save to Downloads
11. Write shell script
12. Deliver with computer:// links

**Total time:** 5–10 minutes if tools are fast. The bottleneck is always transcript/email reading, not page building.
