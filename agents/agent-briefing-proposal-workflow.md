# Agent Briefing: Home Services M&A Advisory Proposal Workflow

## What This Agent Does
Builds a complete M&A advisory proposal for home services businesses (HVAC, plumbing, pest control, roofing, electrical) — both the structured data template and a production-ready React webpage.

---

## STEP-BY-STEP WORKFLOW

### Step 1: Deep Research (parallel web searches)
Run 4+ simultaneous web searches:
- `"M&A advisory engagement letter proposal template home services HVAC plumbing business broker"`
- `"home services M&A advisory fee structure engagement fee success fee retainer sell side buy side"`
- `"lower middle market M&A advisory proposal sections business broker home services trades"`
- `"M&A investment banking pitch book proposal template for service businesses"`

Then run 3 more:
- `"home services HVAC plumbing M&A valuation multiples EBITDA [current year]"`
- `"M&A advisory proposal sell side process timeline phases marketing CIM buyer outreach"`
- `"success fee engagement fee percentage lower middle market business broker $1M $5M $10M"`

Then WebFetch the top 3-4 results for detailed extraction:
- Morgan & Westfield broker agreements page
- First Page Sage fee structure report
- Eton VS fee guide
- Cobrief proposal template

### Step 2: Synthesize Into Rules
From all research, distill the 10 non-negotiable rules for this proposal type. Rules must cover:
1. Owner outcome first (not credentials)
2. Market data with specifics (multiples, active buyers, comps)
3. Tiered fee structure (engagement + retainer + success + minimum)
4. Process phases with timelines
5. Plain language (trades vocabulary)
6. Trade-specific factors (recurring revenue, licensing, fleet, technician retention)
7. Named buyer universe (strategic, PE, independents)
8. Preliminary valuation range
9. Single decision maker clarity
10. Clear next step with deadline

### Step 3: Build the Template
Create a markdown template with:
- 10 sections (Cover, Executive Summary, Market, Company Snapshot, Valuation, Process, Buyers, Fees, Credentials, Next Steps)
- Every dynamic field wrapped in `{{double_braces}}`
- LLM agent instructions at the bottom explaining what to collect first, what to research/auto-populate, what to calculate

### Step 4: Build the React Webpage
Create a single `.jsx` file with:
- All data in one `PROPOSAL` object at the top (agents swap this object)
- Tabbed navigation (sticky)
- Component library: SectionDivider, MetricCard, PhaseCard, ValuationBar, BuyerTag, FeeTable, TestimonialCard, DealRow
- Color system: navy + gold + blue accent
- Font system: Inter for everything, monospace for numbers
- No external CSS — all inline styles
- No localStorage — all React state

### Step 5: Deliver
- Save both files to Downloads
- Provide computer:// links
- If terminal script needed, write a `.sh` file and give one-liner to run it

---

## KEY DATA POINTS BAKED IN (from research)

### Fee Structures by Deal Size
| Deal Size | Engagement Fee | Monthly Retainer | Success Fee | Minimum Fee |
|-----------|---------------|-----------------|-------------|-------------|
| <$5M | $5K-$15K | $2.5K-$5K | 5-10% | $75K-$100K |
| $5M-$15M | $10K-$25K | $5K-$7.5K | 3-6% | $100K-$150K |
| $15M+ | $15K-$50K | $5K-$10K | 2-4% | $150K+ |

### EBITDA Multiples (Home Services 2025-2026)
| Trade | SDE Multiple | EBITDA Multiple | Premium Platform |
|-------|-------------|-----------------|-----------------|
| HVAC | 2.75x-3.25x | 4x-8x | 10x-15x |
| Plumbing | 2.47x-3.08x | 3x-7x | 8x-12x |
| Pest Control | 3x-4x | 5x-10x | 10x-14x |
| Roofing | 2x-3x | 3x-6x | 7x-10x |

### Sell-Side Process Timeline
- Phase 1 Preparation: Weeks 1-6
- Phase 2 Marketing: Weeks 7-14
- Phase 3 Negotiation: Weeks 15-22
- Phase 4 Closing: Weeks 23-36
- Total: 6-9 months typical

### What PE Buyers Want in Home Services
1. EBITDA $500K+ (add-on) or $1M+ (platform)
2. Recurring revenue from maintenance agreements
3. Low owner dependency
4. Clean financials with documented adjustments
5. Technician retention / bench depth
6. Proper licensing and compliance
7. Diversified customer base
8. Scalable operations with documented processes
9. Geographic density for route optimization
10. Multi-trade capability (HVAC + plumbing + electrical)

---

## FILES PRODUCED
1. `proposal-rules-and-template.md` — Rules + full template with {{variables}}
2. `proposal-template.jsx` — Vercel-ready React page
3. `grab-proposal-files.sh` — Terminal script to move files
4. `agent-briefing-proposal-workflow.md` — This file

---

## HOW TO REPEAT THIS WORKFLOW
1. Change the `PROPOSAL` object in the .jsx to match new client data
2. Or have an LLM agent populate the .md template's {{variables}} first, then generate the PROPOSAL object from that
3. The React component renders immediately with any valid PROPOSAL object — no rebuild needed
