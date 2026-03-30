# Vercel Site Audit Report
**Site:** https://master-crm-web-eight.vercel.app
**Date:** 2026-03-28
**Total Pages in Repo:** 96 HTML + 2 JS = 98 files

---

## CRITICAL ISSUE: vercel.json Catch-All Rewrite

The `vercel.json` contains a rewrite rule `"source": "/(.*)", "destination": "/index.html"` that silently serves `index.html` for any non-existent path. This means broken links return HTTP 200 with the index page instead of 404. Users clicking broken links see the homepage with no error indication.

**Fix:** Replace the catch-all rewrite with explicit rewrites for SPA routes, or remove it entirely since all pages are static HTML files at root level.

---

## 1. Landing Page (index.html) -- PASS with issues

| Check | Status | Notes |
|-------|--------|-------|
| Page loads | PASS | HTTP 200, 4283 bytes |
| 6 company cards visible | PASS | HR.com, AquaScience, Springer Floor, Air Control, Design Precast, Wieser Concrete |
| Cards link to hub pages | PASS | All 6 hub pages exist and load correctly |
| deal_side badges | PASS | SELL (4 companies), BUY (2 companies: Design Precast, Wieser) |
| Dashboard nav link | WARN | Links to `dashboard_2026-03-29.html` (dated variant) instead of `dashboard.html` -- works but inconsistent |
| EBITDA Levers nav link | FAIL | **Missing** -- no link to ebitda-levers.html in nav |
| Feature Roadmap nav link | FAIL | **Missing** -- no link to feature-roadmap.html in nav |
| Version History nav link | PASS | Links to version-history.html |

### Issues:
1. **Missing nav links:** Index only has Dashboard and Version History in nav. Missing EBITDA Levers and Feature Roadmap.
2. **Dashboard link uses dated URL:** `dashboard_2026-03-29.html` instead of `dashboard.html`. These are different pages with different layouts.

---

## 2. Company Hub Pages (6 pages) -- PASS with broken links

All 6 hub pages load at `/{company}-hub.html`:

| Company | Loads | comment-widget.js | version-widget.js | Section Anchors | deal_side |
|---------|-------|-------------------|-------------------|-----------------|-----------|
| aquascience | PASS | PASS | PASS | 9 sections | SELL |
| air-control | PASS | PASS | PASS | 9 sections | SELL |
| hrcom-ltd | PASS | PASS | PASS | 9 sections | SELL |
| springer-floor | PASS | PASS | PASS | 9 sections | SELL |
| wieser-concrete-products-inc | PASS | PASS | PASS | 9 sections | BUY |
| design-precast-and-pipe-inc | PASS | PASS | PASS | 9 sections | BUY |

### Section Anchor IDs (all hub pages):
Present: `#overview`, `#contacts`, `#proposal`, `#buyers`, `#scripts`, `#plays`, `#files`, `#history`, `#narrative`

Note: Hub pages use different anchor names than checklist expected. Actual anchors include: `#buyer-outreach-strategy`, `#contacts`, `#documents-amp-files`, `#history`, `#outreach-scripts`, `#overview`, `#pipeline-history`, `#plays-amp-emails-sent`, `#potential-acquirers-35`, `#your-company-story`

### BROKEN LINKS on all 6 hub pages (18 total):

Every hub page has 3 broken `/company/` path links that resolve to index.html via the catch-all rewrite:

| Broken Link | Should Be |
|-------------|-----------|
| `/company/{slug}/proposal` | `{slug}.html` (Confidential Assessment) |
| `/company/{slug}/dataroom` | No standalone data room page exists |
| `/company/{slug}/meeting` | No standalone meeting page exists |

These links appear in the "Documents & Files" section of each hub page. They silently show the homepage instead of the intended content.

### Buyer Links:
All hub pages have clickable buyer links. Sample counts:
- aquascience: 3 buyers linked (Culligan, Grundfos, Pentair)
- air-control: 3 buyers linked
- hrcom-ltd: 5 buyers linked (Paychex, Thoma Bravo, ADP, SAP, Workday)
- springer-floor: 4 buyers linked
- wieser-concrete-products-inc: 10 buyers linked (1 existing + 9 target companies)
- design-precast-and-pipe-inc: 10 buyers linked (2 existing + 8 target companies)

### EBITDA Levers Link:
- aquascience-hub links to `/aquascience-ebitda-levers.html` which **does not exist** (returns index.html fallback)
- Should link to `ebitda-levers-water-treatment.html` or `ebitda-levers.html`

### Research Link:
- Hub pages do NOT link to research pages, even though all 6 research pages exist (`{company}-research.html`)

---

## 3. Buyer Pages -- PASS

5 buyer pages tested across companies:

| Page | Status | Size |
|------|--------|------|
| aquascience_culligan-international.html | PASS | 11,190 bytes |
| air-control_watchtower-capital-via-ally-services.html | PASS | 10,460 bytes |
| hr-com-ltd_paychex.html | PASS | 11,640 bytes |
| springer-floor_the-riverside-company-millicare.html | PASS | 11,175 bytes |
| wieser-concrete-products-inc_mid-states-concrete-industries.html | PASS | 7,719 bytes |

Additional tested:
- design-precast-pipe-inc_the-shaddix-company.html: 7,486 bytes PASS
- wieser-concrete_target_brown-precast.html: 8,036 bytes PASS
- aquascience_bdt-msd-partners.html: 10,955 bytes PASS
- hr-com-ltd_workday.html: 16,462 bytes PASS
- springer-floor_marsden-holding.html: 10,771 bytes PASS

All buyer pages have substantial content (7-16KB).

---

## 4. Proposal Pages -- MIXED

### Actual Proposal Pages (root level, Confidential Assessments):

| Page | Status | Size | EBITDA Content |
|------|--------|------|----------------|
| aquascience.html | PASS | 23,097 bytes | 6 mentions |
| air-control.html | PASS | 22,776 bytes | 5 mentions |
| hrcom-ltd.html | PASS | 21,506 bytes | 3 mentions |
| springer-floor.html | PASS | 22,425 bytes | 4 mentions |
| wieser-concrete-products-inc.html | PASS | 23,605 bytes | 4 mentions |
| design-precast-and-pipe-inc.html | PASS | 23,350 bytes | 5 mentions |

All have EBITDA lever sections. PASS.

### /companies/{slug}/proposal.html Path:
These all return index.html fallback (4,283 bytes). The `/companies/` directory does not exist. **FAIL -- broken routing artifact.**

---

## 5. Data Room Pages -- FAIL

| Path Tested | Status | Notes |
|-------------|--------|-------|
| /companies/{slug}/data-room.html | FAIL | Returns index.html fallback (4,283 bytes) for all 6 |
| /company/{slug}/dataroom | FAIL | Returns index.html fallback (4,816 bytes) for all 6 |

**No standalone data room pages exist in the repo.** The hub pages link to `/company/{slug}/dataroom` but those paths resolve to the index page.

- No email gate found
- No EBITDA lever sections
- Zero actual data room content is deployed

---

## 6. Meeting Pages -- FAIL

| Path Tested | Status | Notes |
|-------------|--------|-------|
| /companies/{slug}/meeting-prep.html | FAIL | Returns index.html fallback for all 6 |
| /company/{slug}/meeting | FAIL | Returns index.html fallback for all 6 |

**No standalone meeting prep pages exist in the repo.**

However, 6 **discovery call** pages DO exist and load correctly:
- `{company}_2026-03-29_discovery.html` -- all 6 present (11-12KB each)

---

## 7. Dashboard -- PASS

| Check | Status | Notes |
|-------|--------|-------|
| dashboard.html loads | PASS | HTTP 200 |
| Revenue forecast with $ amounts | PASS | $914K weighted, $5.2M total pipeline |
| All 6 companies shown | PASS | HR.com, AquaScience, Wieser, Air Control, Design Precast, Springer Floor |
| KPIs visible | PASS | 6 Active Deals, 193 Buyers, 2,191 Contacts |
| Nav links | PASS | Links to index, ebitda-levers, version-history |

Note: `dashboard_2026-03-29.html` is a **different page** ("Monday Dashboard") with different layout. Both exist and work, but index.html links to the dated one while hub pages link to `dashboard.html`.

---

## 8. EBITDA Levers Page -- PASS

| Check | Status | Notes |
|-------|--------|-------|
| ebitda-levers.html loads | PASS | 260,225 bytes |
| Sidebar navigation | PASS | 8 anchors: #water_treatment, #hvac, #flooring, #pest_control, #plumbing, #roofing, #concrete_precast, #universal |
| 7 verticals present | PASS | Water Treatment, HVAC, Flooring, Pest Control, Plumbing, Roofing, Concrete/Precast + Universal |
| Individual vertical pages | PASS | All 8 load (259K-967K bytes each) |

Individual vertical pages:
- ebitda-levers-water-treatment.html: 259,825 bytes
- ebitda-levers-hvac.html: 312,773 bytes
- ebitda-levers-flooring.html: 269,706 bytes
- ebitda-levers-pest-control.html: 277,704 bytes
- ebitda-levers-plumbing.html: 307,632 bytes
- ebitda-levers-roofing.html: 273,311 bytes
- ebitda-levers-concrete-precast.html: 283,331 bytes
- ebitda-levers-master.html: 967,586 bytes

---

## 9. Feature Roadmap -- PASS with broken doc links

| Check | Status | Notes |
|-------|--------|-------|
| feature-roadmap.html loads | PASS | 15,543 bytes |
| Shows 37 built + 24 remaining | PASS | Correctly displayed |
| Document links (.py, .md, .sql) | FAIL | 34 broken links total (15 .md, 18 .py, 1 .sql) |
| Interactive proposal link | PASS | Links to interactive-aquascience.html which exists |

**34 document links point to source code files (.py, .md, .sql) that don't exist on Vercel.** They silently resolve to index.html via the catch-all rewrite.

---

## 10. Version History -- PASS

| Check | Status | Notes |
|-------|--------|-------|
| version-history.html loads | PASS | 7,936 bytes |
| Has search/filter controls | PASS | Input and select elements present |
| Has stats cards | PASS | Stat cards with counts |

---

## 11. JavaScript Widgets -- PASS

| Widget | Status | Size | Content |
|--------|--------|------|---------|
| comment-widget.js | PASS | 12,860 bytes | Section-level commenting widget |
| version-widget.js | PASS | 9,023 bytes | Version history slider widget |

Both are real JavaScript files (not index.html fallbacks).

---

## 12. Additional Pages

### Research Pages (6 pages) -- PASS (but unreachable from navigation)
All exist and load with 18-19KB of content:
- aquascience-research.html: 18,335 bytes
- air-control-research.html: 18,232 bytes
- hrcom-ltd-research.html: 19,719 bytes
- springer-floor-research.html: 19,583 bytes
- wieser-concrete-products-inc-research.html: 18,454 bytes
- design-precast-and-pipe-inc-research.html: 18,443 bytes

**Issue:** No hub page links to these research pages. They exist but are orphaned.

### Interactive Proposal Pages (4 of 6) -- PARTIAL
- interactive-aquascience.html: 43,022 bytes PASS
- interactive-air-control.html: 42,041 bytes PASS
- interactive-hrcom-ltd.html: 38,581 bytes PASS
- interactive-springer-floor.html: 42,662 bytes PASS
- interactive-wieser-concrete-products-inc.html: FAIL (4,816 bytes = index fallback, does not exist)
- interactive-design-precast-and-pipe-inc.html: FAIL (4,816 bytes = index fallback, does not exist)

### Buy-Side Proposal Pages -- PASS
- wieser-concrete_buyside_proposal.html: 22,291 bytes PASS
- design-precast-pipe_buyside_proposal.html: 22,200 bytes PASS

### Discovery Call Pages (6 pages) -- PASS
All exist with 11-12KB of content.

### Alternate Company Pages:
- weiser-concrete.html: 13,256 bytes (note: "weiser" not "wieser" -- possible duplicate/typo)
- design-precast.html: 29,356 bytes
- design-precast-&-pipe-inc.html: 18,574 bytes (URL-encoded ampersand variant)

---

## SUMMARY OF ISSUES

### Critical (broken user-facing functionality):

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | **vercel.json catch-all rewrite** masks all broken links as 200 | Users see homepage instead of errors | Remove `"source": "/(.*)"` rewrite or replace with explicit routes |
| 2 | **18 broken file links on hub pages** (`/company/{slug}/proposal`, `/dataroom`, `/meeting`) | Proposal, Data Room, Meeting links show homepage | Change to `{slug}.html`, create data-room pages, or link to discovery pages |
| 3 | **No standalone data room pages exist** | Feature listed as "built" in roadmap but pages missing | Build 6 data room pages or link to existing proposals |
| 4 | **No standalone meeting prep pages exist** | Hub "Meeting Prep" links are dead | Build meeting pages or link to discovery call pages |

### Moderate (navigation gaps):

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 5 | Index nav missing EBITDA Levers link | Users can't reach EBITDA page from homepage | Add `<a href="ebitda-levers.html">EBITDA Levers</a>` to index nav |
| 6 | Index nav missing Feature Roadmap link | Users can't reach roadmap from homepage | Add `<a href="feature-roadmap.html">Feature Roadmap</a>` to index nav |
| 7 | Hub EBITDA link points to non-existent `/aquascience-ebitda-levers.html` | Clicking EBITDA from hub shows homepage | Fix to `ebitda-levers-water-treatment.html` or `ebitda-levers.html` per company vertical |
| 8 | 6 research pages are orphaned (no navigation links to them) | Content exists but is unreachable | Add research links to hub pages |
| 9 | Index links to `dashboard_2026-03-29.html`, hubs link to `dashboard.html` (different pages) | Inconsistent dashboard experience | Standardize on one dashboard |

### Minor:

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 10 | 34 broken source code links in feature-roadmap.html | Doc links (.py, .md, .sql) show homepage | Remove doc links or host source files |
| 11 | 2 interactive proposal pages missing (Wieser, Design Precast) | Buy-side companies don't have interactive versions | Build interactive-wieser-concrete-products-inc.html and interactive-design-precast-and-pipe-inc.html |
| 12 | `weiser-concrete.html` typo variant exists alongside `wieser-concrete-products-inc.html` | Confusion, wasted space | Delete or redirect the typo variant |

---

## SCORECARD

| Section | Score | Notes |
|---------|-------|-------|
| Landing Page | 7/10 | Works but missing 2 nav links |
| Company Hub Pages (6) | 6/10 | All load, but 18 broken file links + missing EBITDA/research links |
| Buyer Pages | 10/10 | All load with real content |
| Proposal Pages | 8/10 | Root-level proposals work, /companies/ paths broken |
| Data Room Pages | 0/10 | Don't exist anywhere on site |
| Meeting Pages | 2/10 | Don't exist, but discovery call pages do |
| Dashboard | 9/10 | Works great, minor link inconsistency |
| EBITDA Levers | 10/10 | All 7+ verticals, sidebar works, individual pages load |
| Feature Roadmap | 7/10 | Counts correct, 34 broken doc links |
| Version History | 10/10 | Works |
| JS Widgets | 10/10 | Both load correctly |
| Research Pages | 5/10 | Exist but orphaned from navigation |

**Overall: 70/120 (58%)**

---

## TOP 3 FIXES (highest impact, lowest effort)

1. **Remove or fix vercel.json catch-all rewrite** -- stops masking broken links
2. **Fix hub page file links** -- change `/company/{slug}/proposal` to `{slug}.html` for all 6 companies
3. **Add missing nav links to index.html** -- add EBITDA Levers and Feature Roadmap to nav bar
