# MASTER INFRASTRUCTURE MAP — System Locations, IDs, Keys & Contamination Registry

**Owner:** Ewing Gillaspy
**Purpose:** This document tells any agent WHERE everything is, WHAT its ID is, WHAT entity it belongs to, and WHAT is contaminated. It is the physical map of the entire system. For business logic, entity definitions, classification rules, campaign types, person routing, and decision trees — see the **Entity Classification Guide** (separate document). This document does NOT duplicate that logic. It REFERENCES it.
**Companion document:** `Ewing_Entity_Classification_Guide - 03-28-26.docx`
**Created:** 2026-03-28
**Status:** ACTIVE — update as infrastructure changes

---

## SECTION 0: CORE INFRASTRUCTURE RULES

### Rule 1: Shared Capabilities, Separate Data
Tools are entity-agnostic. The CAPABILITY ENGINE (letter mailing system, dialer loader, enrichment pipeline, call analysis) is shared. The CONTENT ENGINE (what the letter says, what business rules apply, what tone/terms to use) lives inside each entity's business logic. Build the engine once, configure per entity.

### Rule 2: Entity Tagging is Mandatory
Every row in every transactional table MUST carry an `entity` field. Values: `next_chapter`, `and_capital`, `revsup`, `the_forge`, `biolev`, `sea_sweet`, `precision_exploration`. No row should ever be untagged. Classification logic is in the Entity Classification Guide.

### Rule 3: DNC is Universal — Cross-Entity by Design
The `do_not_call` table is a UNIVERSAL block across ALL entities. Once a person or company is DNC'd, they are blocked from Salesfinity lists, mailing campaigns, email campaigns, and ALL engagement lists for EVERY entity. No entity column needed on this table. One DNC = blocked everywhere.

### Rule 4: Campaign Naming Convention
All campaign names MUST carry an entity prefix: `AND-`, `NC-`, `RU-`. This allows any LLM to grab a campaign record and immediately link to the correct entity's business rules. Example: `NC-SELL-LETTER` → load Next Chapter letter templates, NC fee structures, NC engagement terms.

### Rule 5: Old Names Are Wrong — Always Cross-Reference
Folder names, repo names, Lovable project names, and Supabase instance names were created before entities were formally separated. Many carry incorrect labels (e.g., "AND Call Command" contains Next Chapter data). The Name Crosswalk (Section 10) maps every old name to its correct entity.

### Rule 6: Standalone Entity Infrastructure
The Forge (Boomerang), BioLev, Sea Sweet, and Precision Exploration each need standalone GitHub repos, Supabase projects, and tables — NOT new logins or accounts, but new organizations/projects under existing accounts. Until Phase 2 builds this, tag their data and ensure no pipeline touches it.

---

## SECTION 1: SUPABASE INSTANCES (10 total)

| # | Instance ID | Current Label | Correct Entity | Status | Action |
|---|---|---|---|---|---|
| 1 | `rdnnhxhohwjucvjwbwch` | AND Call Command | **SHARED — contains NC + AND + standalone data. Name is WRONG.** | **LIVE** | Add `entity` column to all transactional tables. Retroactively tag ~4,000+ rows. |
| 2 | `lhmuwrlpcdlzpfthrodm` | ColdCall Universe | **MIXED — NC + AND, intentionally built as mixed before entity separation** | **RETIRED** | Migrate data with entity tags. Repoint 2 Lovable apps. Delete after. |
| 3 | `asavljgcnresdnadblse` | Phoenix TAM Engine | Next Chapter | **RETIRED** | Already migrated to rdnn. No action. |
| 4 | `ginqabezgxaazkhuuvvw` | Empty project | None | **RETIRED** | Delete. |
| 5 | `iwcvaowfogpffdllqtld` | debugger-tool | None | **DEAD** | Delete. |
| 6 | `iumytggxqtfyaxewgghb` | Marks NYC Hunt | **AND Capital — 100% confirmed. Any NC data found is an ERROR — strip it.** | **NEW** | Consolidate into rdnn under `and_capital` tag. |
| 7 | `lsxmnowczekpdjuvrxxt` | Ewing NYC Mobile Map | None | **NEW — EMPTY** | Delete. Zero tables. |
| 8 | `wdhnsbzmcjpqbltkulwe` | NYC Deal Maker | **AND Capital — 100% confirmed. Any NC data found is an ERROR — strip it.** | **NEW** | Consolidate into rdnn under `and_capital` tag. |
| 9 | `pgoogsxaljtjhwhydqtg` | NYC Outreach Hub | **AND Capital — 100% confirmed. Any NC data found is an ERROR — strip it.** | **NEW** | Consolidate into rdnn. Most sophisticated schema — preserve views and enums. |
| 10 | (unknown — Lovable-managed) | Precision Exploration | Precision Exploration (STANDALONE) | **ACTIVE — MANUAL ONLY** | DO NOT TOUCH. Managed by Lovable env vars. |

### 1.1 LIVE Instance Connection Details (`rdnnhxhohwjucvjwbwch`)
- **URL:** `https://rdnnhxhohwjucvjwbwch.supabase.co`
- **Anon key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkbm5oeGhvaHdqdWN2andid2NoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NzI3MzYsImV4cCI6MjA4OTQ0ODczNn0.SZJlQgqtAtdF11CDGofgkF-tz_2W2bCQx3q4hpGRlPU`

### 1.2 RETIRED Instance Connection Details (`lhmuwrlpcdlzpfthrodm`)
- **URL:** `https://lhmuwrlpcdlzpfthrodm.supabase.co`
- **Anon key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxobXV3cmxwY2RsenBmdGhyb2RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3MjQxNzQsImV4cCI6MjA4OTMwMDE3NH0.dcedlyfYYW25i5imrpzY0NjrwK2A0CH4U65bvaRVJqE`
- **Data remaining:** 1,844 persons, 1,068 companies, 1,829 phone numbers, 1,559 scores, 21 lists, 1,533 list assignments
- **Why it still exists:** 2 Lovable apps still point here (Cold Call Universe v2, Cold Call CRM)

### 1.3 NEW Instance Connection Details

**Marks NYC Hunt (`iumytggxqtfyaxewgghb`)**
- **URL:** `https://iumytggxqtfyaxewgghb.supabase.co`
- **Anon key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1bXl0Z2d4cXRmeWF4ZXdnZ2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4OTIyMTcsImV4cCI6MjA4ODQ2ODIxN30._sclNNI2UZSt-ajZ1FQQ9XMN2RjjwPVHrzNfzKCBdzE`
- **Tables:** `contacts` (investor CRM: AUM, FINRA risk, fund tags, archetypes, openers, scripts, thesis alignment)

**NYC Deal Maker (`wdhnsbzmcjpqbltkulwe`)**
- **URL:** `https://wdhnsbzmcjpqbltkulwe.supabase.co`
- **Anon key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndkaG5zYnptY2pwcWJsdGt1bHdlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0MDM4MDAsImV4cCI6MjA4Nzk3OTgwMH0.GOgC7L2dI_NQ5JxnrsAw-nX6ZnZuox0ZPm3MJC3WDhw`
- **Tables:** `attack_list` (NYC networking targets), `attack_notes` (notes per target), `app_config` (key-value settings)
- **Edge function:** `polish-update` (AI itinerary assistant, Gemini 2.5 Flash)

**NYC Outreach Hub (`pgoogsxaljtjhwhydqtg`)**
- **URL:** `https://pgoogsxaljtjhwhydqtg.supabase.co`
- **Anon key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBnb29nc3hhbGp0amh3aHlkcXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0OTYyNDQsImV4cCI6MjA4ODA3MjI0NH0.AuLPsHkl6hFKy7YCIH1UYbHKqEibP058OsLspncs5fI`
- **Tables:** `companies`, `people`, `events`, `event_targets`
- **Views:** `company_dashboard_view`, `people_dashboard_view`, `daily_briefing_view`
- **Enums:** 5 enum types
- **Migration date:** 2026-03-03

---

## SECTION 2: TABLE-BY-TABLE CONTAMINATION REGISTRY (LIVE instance `rdnnhxhohwjucvjwbwch`)

Every table, its row count, its current entity contamination status, and the specific method to fix it.

### 2.1 Pipeline Tables — CONTAMINATED (mixed NC + AND)

| Table | Rows | Has Entity Column? | Contamination | Fix Method |
|---|---|---|---|---|
| `campaigns` | 5 | **NO** | MIXED — 5 rows covering both NC and AND targets under shared rules | Add `entity` column. Expand to ~10 rows with `AND-` / `NC-` / `RU-` prefix naming. Each campaign record must link to correct entity business rules. |
| `targets` | 201 | **NO** | MIXED — almost all NC, but let industry determine | Add `entity` column. Classify each company by industry using Entity Classification Guide decision tree. Domain name and title are the reliable signals. |
| `dossier_final` | 10 | **NO** | Likely all NC | Add `entity` column. Check each `company_name` against decision tree. |
| `dossier_runs` | 1000+ | **NO** | Inherits from target | Add `entity` column. Tag by matching `target_id` → `targets.entity`. |
| `dossier_provenance` | 1000+ | **NO** | Inherits from target | Add `entity` column. Tag by matching `target_id` → `targets.entity`. |
| `dossier_cost_log` | 549 | **NO** | Inherits from dossier | Add `entity` column. Tag by matching `dossier_id` → `dossiers` → `targets.entity`. |
| `dossiers` | 1 | **NO** | Single row — check company | Add `entity` column. Classify by company vertical. |
| `sent_log` | 27 | **NO** | MIXED — letters to business owners (NC) and family offices (AND) in same table | Add `entity` column. Classify by recipient company type. **Note:** Letter ENGINE is shared capability. Letter CONTENT engine lives in entity business logic. Tag so system knows which content engine generated it. |
| `outreach_queue` | 82 | **NO** | MIXED | Add `entity` column. Domain name or title of person/company is the ONLY reliable classification signal. Apply entity decision tree. |
| `pipeline_log` | 1000+ | **NO** | MIXED — agent actions logged without entity context | Add `entity` column. **Needs careful audit.** Only domain name and title of the person/company will tell you the answer. Must use Entity Classification Guide to associate. |

### 2.2 Call Intelligence Tables — CONTAMINATED (mixed NC + AND + possibly RevsUp)

| Table | Rows | Has Entity Column? | Contamination | Fix Method |
|---|---|---|---|---|
| `dialer_queue` | 646 | **NO** | MIXED — Salesfinity is a shared tool, lists come from any entity | Add `entity` column. Classify each contact's company against decision tree. |
| `call_analysis` | 1000 | **NO** | MIXED — Mark's 449 convos span all 3 entities, Ewing's 195 span NC + AND | Add `entity` column. **This table should be the cleanup engine** — it scores and classifies calls but currently stores results without entity labels. Fix: call_analysis must TAG entity on output, not just score. Match company/vertical against decision tree. |
| `do_not_call` | 144 | **N/A — NOT NEEDED** | **UNIVERSAL by design** | Do NOT add entity column. DNC blocks across ALL entities, ALL channels. See Rule 3. |

### 2.3 TAM Engine Tables — CLEAN (all Next Chapter)

| Table | Rows | Entity | Notes |
|---|---|---|---|
| `tam_businesses` | 1000+ | `next_chapter` | All HVAC contractors. Clean. |
| `tam_final` | 1000+ | `next_chapter` | All HVAC contractors. Clean. |
| `tam_verifications` | 1000+ | `next_chapter` | All HVAC contractors. Clean. |
| `tam_owner_profiles` | 306 | `next_chapter` | All HVAC owner profiles. Clean. |
| `tam_scrape_runs` | 287 | `next_chapter` | Scrape run metadata. Clean. |

### 2.4 Deal Tables — LIKELY CLEAN (verify)

| Table | Rows | Likely Entity | Notes |
|---|---|---|---|
| `deal_research` | 67 | `next_chapter` | Acquirer research for HR.com deal. Verify all rows are NC buy-side work. |
| `acquisition_targets` | 9 | `next_chapter` | Named acquisition targets. Verify none are AND Capital fund targets. |

### 2.5 Standalone Entity Data — SHOULD NOT BE IN SHARED DB

| Table | Rows | Correct Entity | Problem | Fix |
|---|---|---|---|---|
| `boomerang_targets` | 227 | `the_forge` | Standalone entity data in shared database. Any pipeline touching `rdnn` could accidentally interact. | Tag as `the_forge` immediately. Move to own Supabase project in Phase 2 (new org, not new account). |

### 2.6 Debrief / System Tables — NO ENTITY TAGGING NEEDED

| Table | Rows | Notes |
|---|---|---|
| `stories` | 11 | Narrative summaries. System table. |
| `harvests` | 21 | Machine scans. System table. |
| `audits` | 2 | Audit reports. System table. |
| `analysis` | 13 | Cross-phase analysis. System table. |
| `skills_registry` | 23 | Skill assessments. System table. |

### 2.7 CRM Tables — MISSING FROM LIVE (still on RETIRED `lhmuwrlpcdlzpfthrodm`)

These tables returned ERROR on the LIVE instance. They were never migrated from the retired instance.

| Table | Rows (on lhmuw) | Contamination | Migration Notes |
|---|---|---|---|
| `persons` | 1,844 | MIXED (NC + AND) | Classify each person by their company's industry during migration. |
| `phone_numbers` | 1,829 | MIXED | Inherits from person → company. |
| `companies` | 1,068 | MIXED | Classify by industry using decision tree. |
| `person_scores` | 1,559 | MIXED | Inherits from person. |
| `linkedin_identifiers` | unknown | MIXED | Inherits from person. |
| `list_assignments` | 1,533 | MIXED | Inherits from list → campaign → entity. |
| `lists` | 21 | MIXED | Tag each list by its target audience / campaign. |
| `reps` | unknown | System | Sales rep records — entity-agnostic. |
| `call_log` | unknown | MIXED | Classify by called company type. |
| `enrichment_log` | unknown | MIXED | Inherits from person/company. |
| `outreach_funnel` | unknown | MIXED | Inherits from campaign. |

### 2.8 Tables on NEW Instances (AND Capital — consolidation targets)

**`iumytggxqtfyaxewgghb` — Marks NYC Hunt**
| Table | Entity | Notes |
|---|---|---|
| `contacts` | `and_capital` | Investor CRM: AUM, FINRA risk, fund tags, archetypes, openers, scripts, thesis alignment. Types: superconnector, direct_investor. Migration dated 2026-03-07. |

**`wdhnsbzmcjpqbltkulwe` — NYC Deal Maker**
| Table | Entity | Notes |
|---|---|---|
| `attack_list` | `and_capital` | NYC networking targets: name, company, role, LinkedIn, priority, status, photo. |
| `attack_notes` | `and_capital` | Notes per target. |
| `app_config` | `and_capital` | Key-value settings. |
| Edge function: `polish-update` | `and_capital` | AI itinerary assistant using Gemini 2.5 Flash via Lovable gateway. |

**`pgoogsxaljtjhwhydqtg` — NYC Outreach Hub**
| Table | Entity | Notes |
|---|---|---|
| `companies` | `and_capital` | Full company records with sector alignment (Oil & Gas, Healthcare). |
| `people` | `and_capital` | Contact records with propensity scoring. |
| `events` | `and_capital` | NYC events (5 seeded, Mar 2026). |
| `event_targets` | `and_capital` | RSVP and event targeting. |
| View: `company_dashboard_view` | `and_capital` | Dashboard aggregation. |
| View: `people_dashboard_view` | `and_capital` | Dashboard aggregation. |
| View: `daily_briefing_view` | `and_capital` | Daily briefing. |
| 5 enums | `and_capital` | Type definitions. |

---

## SECTION 3: GITHUB REPOS

| Repo | GitHub Account | Current Name Implies | Correct Entity | Status | Notes |
|---|---|---|---|---|---|
| `dossier-pipeline` | clawdking1-GH | Neutral | Next Chapter (primarily) | ACTIVE | Main pipeline. All current targets are NC. Needs entity tagging in code for multi-entity use. |
| `phoenix-tam-engine` | clawdking1-GH | Neutral | Next Chapter | ACTIVE | HVAC market scraping. Clean NC ownership. Uncommitted `dedup.py`. |
| `blank-canvas-proposal` | ewing-operating-system | Neutral | Next Chapter | ACTIVE | Proposal generation. Currently serving Debbie/HR.com deal. Untracked `db-export/` dir. |
| `sunshine-code-forge` | ewing-operating-system | Neutral | Next Chapter | ACTIVE | Frontend apps. |
| `ewing-registry` | clawdking1-GH | Neutral | System (all entities) | ACTIVE | Skills registry. Entity-agnostic. |
| `and-call-command-pipeline` | ewing-operating-system | **AND Capital** | **MISNOMER — pipeline serves NC targets primarily** | ACTIVE | Rename candidate. |
| `and-call-command-unified` | ewing-operating-system | **AND Capital** | **MISNOMER — same issue** | ACTIVE | Has edge functions. |
| `coldcall-universe` | ewing-operating-system | Neutral | **MIXED (NC + AND)** | ACTIVE | **Intentionally built as mixed-entity system** before formal separation. Original sin of commingling. GREEN has 3 unpushed on `v2-overnight-build`. MB-27 has 24 staged, push blocked (SSH auth broken). |
| `nyc-war-story` | ewing-operating-system | Neutral | AND Capital | ACTIVE | NYC-focused. Modified `index.html`. |
| `clawdbot-pipeline` | clawdking1-GH (openclaw/) | Neutral | System | ACTIVE | Agent orchestration. 79 reports, 11 outreach. |
| `hovering-cloud` | clawdking1-GH | Neutral | System | ACTIVE | Cross-machine clipboard. Entity-agnostic. |
| `recording-library` | ewing-operating-system | Neutral | System | DORMANT | Media cataloging. **EXPOSED GitHub PAT in remote URL:** `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` — needs rotation. |
| `debugger-tool` | ewing-operating-system | Neutral | None | DEAD | Old forensic project. Also has exposed PAT in remote. Kill. |
| `pixel-perfect-clone` | ewing-operating-system | Neutral | Next Chapter | DORMANT | Lovable app clone. |
| `overwatch` | ewing-operating-system | Neutral | System | UNKNOWN | Needs audit. |

### GitHub Accounts
| Account | Auth Method | Used On |
|---|---|---|
| `ewing-operating-system` | SSH (primary) | MacBook-27, MacBook-GREEN |
| `clawdking1-GH` | HTTPS/keyring | Mac-mini-8 |

---

## SECTION 4: LOVABLE APPS

| # | App Name | Lovable ID | Supabase Instance | Entity | Exists? | Last Edited | Status |
|---|---|---|---|---|---|---|---|
| 1 | Debbie Deal Room | `a3bf07f3-1c4c-437b-b658-f0d9f86c38dc` | `rdnnhxhohwjucvjwbwch` (LIVE) | Next Chapter | **YES** | 2 days ago | ACTIVE — proposal due Monday |
| 2 | Next Chapter Reports | `70bfa70e-e847-47d0-abfd-5845c0ba81c1` | `rdnnhxhohwjucvjwbwch` (LIVE) | Next Chapter | **YES** | 2 days ago | ACTIVE |
| 3 | Cold Call Universe v2 | `cd956a91-3866-4da3-8f18-bd3f6d085dbd` | `lhmuwrlpcdlzpfthrodm` (RETIRED) | MIXED (NC + AND) | **YES** | 2 days ago | ACTIVE — needs repoint to rdnn |
| 4 | Cold Call CRM | `8724256f-b75a-45e9-bbc0-fab38cf80322` | `lhmuwrlpcdlzpfthrodm` (RETIRED) | MIXED (NC + AND) | **YES** | 2 days ago | ACTIVE — needs repoint to rdnn |
| 5 | NMR Science Showcase | `f2fc9365-413a-4c6d-8416-53c5c140a1b4` | NONE | PEC (STANDALONE) | **YES** | 3 hours ago | MANUAL ONLY |
| 6 | Fitness Pitch Builder | `3d4ee5fc-55c2-4769-95c0-08dee9b331b7` | NONE | BioLev (STANDALONE) | **YES** | 3 hours ago | Static — 5 pitch decks |
| 7 | Executive Snapshot | `0aeaa6a0-c0bd-4a2d-be03-98e68777389e` | NONE | Next Chapter (likely) | **YES** | 3 days ago | Static — dossier viewer |
| 8 | Precision Exploration (Official) | `239c9bb2-3238-4975-a6aa-07f73e7e1a51` | Lovable-managed (unknown ID) | PEC (STANDALONE) | **YES** | 17 days ago | MANUAL ONLY |
| 9 | Remix of Precision Exploration | `63c4f5cd-738e-4dc4-bd12-00af33861ff3` | Lovable-managed | PEC (STANDALONE) | **YES** | 18 days ago | MANUAL ONLY |
| 10 | Marks NYC Hunt | `cb07d396-daf1-4fc2-afd4-bc8d2d884259` | `iumytggxqtfyaxewgghb` (NEW) | AND Capital | **YES** | 21 days ago | ACTIVE |
| 11 | Ewing NYC Mobile Map | `edd4f327-d711-40ae-bd2b-d51ca55f5424` | `lsxmnowczekpdjuvrxxt` (NEW, EMPTY) | AND Capital | **YES** | 22 days ago | DB unused — delete candidate |
| 12 | NYC Deal Maker | `672ae5a6-63ef-4433-b3f3-220bd9ef60ba` | `wdhnsbzmcjpqbltkulwe` (NEW) | AND Capital | **YES** | 23 days ago | ACTIVE |
| 13 | NYC Outreach Hub | `2821f447-6bfb-4211-9113-8002fac05209` | `pgoogsxaljtjhwhydqtg` (NEW) | AND Capital | **YES** | 26 days ago | ACTIVE |
| 14 | The Cycle's Truth | `8a3b3e48-622f-48cf-ba93-3d6f2b127953` | NONE | Personal | **YES** | 28 days ago | Ignore |
| 15 | Pixel Perfect Clone | `01b7b849-30f8-405f-b057-55974c3baba0` | `rdnnhxhohwjucvjwbwch` (LIVE, hardcoded) | Next Chapter | **MISSING** | — | Not on main Lovable page. May be in archive or Personal folder. Verify. |
| 16 | Pitch Deck Structure | `af4a85d6-b4cb-4096-97f2-c42288a66471` | NONE | Unknown | **MISSING** | — | May be in archive or Personal folder. Verify. |
| 17 | Blank Canvas Studio | `c477e7bf-9691-44ec-8cf4-c4fa0fc560a6` | NONE | Unknown | **MISSING** | — | May be in archive or Personal folder. Verify. |
| 18 | Git Resume | `88987162-f9bd-4266-b5f6-a4e7f555dc4e` | NONE | — | **DELETED** | — | Gone |
| 19 | Gym Wellness Hub | `5767f62a-45a8-40da-a7d0-05c55b4a00a1` | NONE | — | **DELETED** | — | Gone |
| 20 | Investor Compass | `69aa361d-990a-4291-82b5-220ea40bc38c` | NONE | — | **DELETED** | — | Gone |

**Lovable folders visible:** `archive`, `Personal` — 3 missing apps may be inside.

---

## SECTION 5: SKILLS — ENTITY AFFINITY

| Skill | Installed Locally? | In Registry? | Entity Affinity | Notes |
|---|---|---|---|---|
| `cold-call-workflow` | YES | YES | Shared (NC + AND + RU) | Tags calls by entity using Salesfinity data. |
| `salesfinity-loader` | NO | YES | Shared capability | Loads contacts into dialer. Must tag by entity before loading. |
| `revsup-oo` | Cowork | — | RevsUp | Builds Opportunity Overview documents for recruiting placements. |
| `pec-case-manager` | Cowork | — | PEC (STANDALONE) | MANUAL ONLY. Fraud case management. |
| `finance-agent` | YES | YES | Personal (Ewing) | Not entity-specific. |
| `clawdbot-creator` | YES | YES | System | Bot spawning. |
| `clawdbot-self-repair` | YES | YES | System | Error recovery. |
| `debrief` | YES | YES | System | Thread intelligence extraction. |
| `disk-cleanup` | YES | YES | System | Mac storage management. |
| `ewing-connectors` | YES | YES | System — credential vault | Overlaps with `keys-and-credentials`. |
| `harvester` | YES | YES | System | Machine artifact scanning. |
| `keys-and-credentials` | YES | YES | System — credential vault | Overlaps with `ewing-connectors`. |
| `mission-control` | YES | YES | System | Fleet command center. |
| `output-skill` | YES | YES | System | Communication style rules. |
| `prompt-refiner` | YES | YES | System | Prompt restructuring. |
| `skill-creator` | YES | YES | System (meta) | Skill building. |
| `skill-loader` | YES | YES | System (meta) | Session bootstrapper. |
| `skill-sync` | YES | YES | System (meta) | GitHub sync. |
| `storyteller` | YES | YES | System | Thread narrative. |
| `tech-translator` | YES | YES | System | Jargon translation. |
| `data-architect` | NO | YES | System | Data design. |
| `file-share` | NO | YES | System | Cross-machine sharing. |
| `password-migration` | NO | YES | System | Security. |
| `rate-oracle` | NO | YES | System | API cost tracking. |
| `recording-collector` | NO | YES | System | Media cataloging. |
| `system-auditor` | NO | YES | System | Overlaps with `harvester`. |

---

## SECTION 6: SCHEDULED TASKS

| Task | Machine | Schedule | Entity Contamination | Notes |
|---|---|---|---|---|
| `call-ingest-hourly` | MB-27 | Hourly | **MIXED** — pulls all Salesfinity calls untagged | Must tag entity on ingest using decision tree. |
| `call-sync` | MB-27 | Every 4 hours | **MIXED** | Same tagging requirement. |
| `daily-maintenance` | MB-27 | Daily 6AM | **MIXED** | DNC patterns, stale recycler, data quality. Operates on mixed data. |
| `daily-tasks-created` | MB-27 | Daily 8AM | **MIXED** | Cold call workflow (email, calendar, Fireflies, phone). Crosses entities. |
| `dnc-salesfinity-sync` | MB-27 | Nightly | **UNIVERSAL** | DNC is cross-entity (Rule 3). Pushes universal blocks to dialer. |
| `priority-rebuild` | MB-27 | Sun 5pm + Wed 6pm | **MIXED** | List priority rebuild. Lists should be entity-tagged. |
| `queue-autocheck` | MB-27 | Daily | **MIXED** | Queue depth per rep. Reps span entities. |
| `email-monitor` | MB-27 | Hourly :05 | Next Chapter (primary) | Scans ewing@chapter.guide. |
| `nightly-system-audit` | MB-27 | Weekly | System | Infrastructure health. Entity-agnostic. |
| `company-valuation-backfill` | MB-27 | On demand | Next Chapter | EBITDA multiples for NC sell-side targets. |
| `daily-urgent-briefing` | Cowork VM | Daily 6:06AM | **MIXED** | Crosses entities. |
| `pec-evidence-logger` | Cowork VM | Daily 9:05AM | PEC (STANDALONE) | DISABLED. Manual only. |
| `pec-fact-finder` | Cowork VM | Daily 9:34AM | PEC (STANDALONE) | DISABLED. Manual only. |

---

## SECTION 7: SHARED TOOLING — API CONNECTIONS

### Salesfinity
- **Base URL:** `https://client-api.salesfinity.co`
- **Auth header:** `x-api-key`
- **API key:** `sk_ff45bc29-e5c1-4a3f-b1e5-f9776d94cbe7`
- **Primary endpoint:** `/v1/call-log` — 10,535+ records, paginated 100/page, FULL contact data
- **Secondary endpoint:** `/v1/scored-calls` — AI-scored subset only, max 50
- **Cross-ref method:** Match `call_log._id` to scored-calls records
- **User IDs:** Ewing `680edc0d1504192884a148e0` | Mark `68d1caac41d11ac1ce5df7a2`
- **JSON quirk:** Transcription field contains control characters — use `json.loads(data, strict=False)`
- **Working endpoints:** `/v1/call-log`, `/v1/call-log/{id}`, `/v1/scored-calls`, `/v1/scored-calls/{id}`, `/v1/dispositions` (14 types), `/v1/contact-lists/csv`
- **Broken endpoints:** `/v1/webhooks` (401), `/v1/follow-up-tasks` (404), `/v1/users` (404), `/v1/analytics/overview` (500), `/v1/sdr-performance` (404)
- **Untested:** `/v1/snoozed-contacts`, `/v1/sequences`, `/v1/custom-fields`

### Clay.com
- **Status:** Active, $800/mo legacy plan
- **Google Sheet receiving webhook data:** `1FYAW-321f9Tvt2-K47RELpKG54J4F1CTafW39XuycK4`
- **Current counts from Clay enrichment:** 266 companies, 291 persons, 555 phone numbers
- **Pipeline:** Clay webhook → Google Sheet → Supabase (manual script `sheets_to_supabase.py` or Apps Script auto-sync)

### Exa.ai
- **Cost:** $0.006/result, $0.001/enrichment
- **Use:** Web search for current data. Cheaper than LLM inference for information retrieval.

### OpenClaw Agent Fleet
- **Gateway:** localhost:18789, token `0fad0f71...`, loopback only
- **Main:** DeepSeek Chat — pipeline controller (~$0.004/call)
- **Researcher:** Gemini 2.5 Flash Lite via OpenRouter (~$0.001/call)
- **Validator:** DeepSeek V3 via OpenRouter (~$0.004/call)
- **Executor:** GPT-4o Mini via OpenRouter (~$0.002/call)
- **Auditor:** DeepSeek V3 via OpenRouter (~$0.004/call)
- **Scout / Next:** Defined but no IDENTITY.md found
- **Agent identity files:** `~/.openclaw/agents/{name}/IDENTITY.md`
- **Config:** `~/.openclaw/openclaw.json`

### Google Drive
- **Primary workspace:** ewing@chapter.guide (My Drive)
- **Also mounted:** ewing.gillaspy@gmail.com (personal), ewing@engram.nexus (AI platform, x2), ewing@revsup.com
- **Total Google Drive storage:** ~106 GB on MB-27

### Machines
| Machine | Role | Hostname |
|---|---|---|
| MacBook-27 (14" MBP) | Daily work — VoIP, Zoom, Claude, Lovable, deal work | ewinggillaspy / MacBook-27.local |
| MacBook-GREEN (16" MBP, broken screen) | Always-on monitoring display / war room | MacBook-GREEN |
| Mac mini (24GB RAM) | ClawdBot — 24/7 business automation server | ClawdBots-Mac-mini-8 |
| Cowork VMs | Disposable — mount skills from launching Mac | Ephemeral |

---

## SECTION 8: ACTIVE OPPORTUNITIES — TIME-SENSITIVE

| Opportunity | Entity | Deadline | Infrastructure |
|---|---|---|---|
| **Debbie McGrath / HR.com** | Next Chapter (sell-side) | **Proposal due Monday 2026-03-31** | Staging: Debbie Deal Room (`a3bf07f3`). Production: Debbiedealroom.com (domain purchased, site not yet built). Supabase: `deal_research` (67 rows), `acquisition_targets` (9 rows) on rdnn. Repos: `blank-canvas-proposal`, `sunshine-code-forge`. |

---

## SECTION 9: PHASE 1 vs PHASE 2 ACTIONS

### Phase 1 (Now — before the big build)
1. Add `entity` column to every transactional table in `rdnnhxhohwjucvjwbwch` EXCEPT `do_not_call` (universal by design)
2. Retroactively tag ~4,000+ existing rows using Entity Classification Guide decision tree. Domain name and title are the only reliable classification signals for ambiguous rows.
3. Make `call_analysis` output an entity tag with every scored call — this table is both the problem and the solution
4. Repoint Cold Call Universe v2 (`cd956a91`) and Cold Call CRM (`8724256f`) from `lhmuw` to `rdnn`
5. Migrate `lhmuw` data (1,844 persons, 1,068 companies, 1,829 phones) with entity tags applied during migration
6. Consolidate 3 NYC Supabase instances (`iumy`, `wdhn`, `pgoo`) into `rdnn` under `and_capital` tag — 100% AND Capital, strip any NC data as error
7. Delete empty/dead instances: `ginqa`, `iwcva`, `lsxmn`
8. Expand `campaigns` table from 5 to ~10+ rows with entity prefix naming (`AND-LP-LETTER`, `NC-SELL-CALL`, `RU-CLIENT`, etc.)

### Phase 2 (After audit conclusions are in Supabase)
1. Create standalone infrastructure for The Forge: new GitHub org/repo, new Supabase project — same accounts, new organizations
2. Same for BioLev, Sea Sweet, Precision Exploration
3. Move `boomerang_targets` to The Forge's own Supabase
4. Rename `and-call-command-*` repos to reflect correct entity ownership
5. Rename Supabase instance label from "AND Call Command" to entity-agnostic name
6. Build entity-scoped views/RLS policies to prevent accidental cross-entity queries
7. Enforce DNC as universal gate BEFORE any contact loads to any engagement list

---

## SECTION 10: NAME CROSSWALK — Old Names → Correct Entity

Every name an agent will encounter in the wild, mapped to the correct entity.

### Supabase Instance Names
| Name Agent Will See | Instance ID | Correct Entity |
|---|---|---|
| AND Call Command | `rdnnhxhohwjucvjwbwch` | **SHARED (NC + AND + standalone) — name is WRONG** |
| ColdCall Universe | `lhmuwrlpcdlzpfthrodm` | **MIXED (NC + AND) — retired** |
| Phoenix TAM Engine | `asavljgcnresdnadblse` | Next Chapter — retired |
| Marks NYC Hunt | `iumytggxqtfyaxewgghb` | AND Capital |
| NYC Deal Maker | `wdhnsbzmcjpqbltkulwe` | AND Capital |
| NYC Outreach Hub | `pgoogsxaljtjhwhydqtg` | AND Capital |
| Ewing NYC Mobile Map | `lsxmnowczekpdjuvrxxt` | None — empty, delete |

### Repo Names
| Name Agent Will See | Correct Entity |
|---|---|
| `and-call-command-pipeline` | **Next Chapter primarily — name is WRONG** |
| `and-call-command-unified` | **Next Chapter primarily — name is WRONG** |
| `coldcall-universe` | **MIXED (NC + AND)** |
| `dossier-pipeline` | Next Chapter (primarily) |
| `phoenix-tam-engine` | Next Chapter |
| `blank-canvas-proposal` | Next Chapter |
| `sunshine-code-forge` | Next Chapter |
| `nyc-war-story` | AND Capital |

### Lovable App Names
| Name Agent Will See | Lovable ID | Correct Entity |
|---|---|---|
| Debbie Deal Room | `a3bf07f3` | Next Chapter |
| Next Chapter Reports | `70bfa70e` | Next Chapter |
| Cold Call Universe v2 | `cd956a91` | **MIXED (NC + AND)** |
| Cold Call CRM | `8724256f` | **MIXED (NC + AND)** |
| Executive Snapshot | `0aeaa6a0` | Next Chapter (likely) |
| Pixel Perfect Clone | `01b7b849` | Next Chapter |
| Marks NYC Hunt | `cb07d396` | AND Capital |
| NYC Deal Maker | `672ae5a6` | AND Capital |
| NYC Outreach Hub | `2821f447` | AND Capital |
| Ewing NYC Mobile Map | `edd4f327` | AND Capital (empty) |
| Fitness Pitch Builder | `3d4ee5fc` | BioLev (STANDALONE) |
| NMR Science Showcase | `f2fc9365` | PEC (STANDALONE) |
| Precision Exploration | `239c9bb2` | PEC (STANDALONE) |
| Remix of Precision Exploration | `63c4f5cd` | PEC (STANDALONE) |
| The Cycle's Truth | `8a3b3e48` | Personal |

### Google Drive Folder Names
| Folder Name | Correct Entity |
|---|---|
| `02 - AND Capital/` | AND Capital |
| `_000_AND_Capital_ColdCall_Universe/` | **MIXED (NC + AND) — name says AND but contains NC prospect data. Classify by company type.** |
| `00 - BioLev Sale/` | BioLev (STANDALONE) |
| `01 - Next Chapter Main Docs/` | Next Chapter |
| `03 - Next Chapter Advisors/` | Next Chapter |
| `04 - Sea Sweet/` | Sea Sweet (STANDALONE — Jeremy Christopher) |
| `13 - New Roofing Rollup/` | **Sea Sweet (STANDALONE) — NOT Next Chapter** |
| `12 - Cold calling project/` | **MIXED (NC + AND)** |

---

## SECTION 11: CAMPAIGN REGISTRY — Infrastructure Mapping

This section maps every campaign to its physical infrastructure: which tables it touches, which repos power it, which Lovable apps serve it, which skills and scheduled tasks run it. Campaign definitions (audience, channel, purpose) are in the Entity Classification Guide. This section answers: "If I'm running campaign X, what infrastructure do I interact with?"

### Campaign Naming Convention
All campaign names MUST carry an entity prefix: `AND-`, `NC-`, `RU-`. This allows any LLM to grab a campaign record and immediately link to the correct entity's business rules, tone, engagement terms, and content logic.

**Current state:** The `campaigns` table has only 5 rows with NO entity field. The Entity Classification Guide defines 5 AND Capital campaign types + 5 Next Chapter campaign types + 3 RevsUp campaign types = 13 total. The table needs to expand from 5 to ~13+ rows with proper entity prefix naming.

**CII (~1,500 buyers) is a deal buyer SOURCE, not a campaign.** It is used per-deal at Next Chapter's discretion. Do not create a CII campaign record.

### 11.1 Next Chapter Campaigns → Infrastructure

| Campaign ID | Name | Supabase Tables | Repos | Lovable Apps | Skills | Scheduled Tasks |
|---|---|---|---|---|---|---|
| `NC-SELL-LETTER` | Owner Letter Campaign | `targets` (201), `sent_log` (27), `outreach_queue` (82), `campaigns` (subset), `pipeline_log` (1000+) | `dossier-pipeline`, `and-call-command-pipeline` (MISNOMER) | Next Chapter Reports (`70bfa70e`) | — | — |
| `NC-SELL-CALL` | Prospect Cold Calling | `dialer_queue` (646 — NC subset), `call_analysis` (1000 — NC subset), `do_not_call` (144 — universal), `pipeline_log` | `dossier-pipeline`, `and-call-command-pipeline` (MISNOMER), `coldcall-universe` (MIXED) | Cold Call Universe v2 (`cd956a91`), Cold Call CRM (`8724256f`) | `cold-call-workflow`, `salesfinity-loader` | `call-ingest-hourly`, `call-sync`, `daily-maintenance`, `daily-tasks-created`, `dnc-salesfinity-sync`, `priority-rebuild`, `queue-autocheck` |
| `NC-BUY-OUTREACH` | Buy-Side Outreach | `deal_research` (67), `acquisition_targets` (9), `targets` (buy-side subset) | `blank-canvas-proposal`, `sunshine-code-forge` | Debbie Deal Room (`a3bf07f3` — staging) | — | — |
| `NC-TRANSCRIPT` | Transcript Mining | `call_analysis` (NC subset), `pipeline_log` | `dossier-pipeline` | — | `cold-call-workflow` | `daily-tasks-created` |
| `NC-TAM` | TAM Engine | `tam_businesses` (1000+), `tam_final` (1000+), `tam_verifications` (1000+), `tam_owner_profiles` (306), `tam_scrape_runs` (287) | `phoenix-tam-engine` | Next Chapter Reports (`70bfa70e` — reads tam_owner_profiles) | — | — |

**Contamination in NC campaigns:** `NC-SELL-CALL` is the most contaminated. `dialer_queue` (646 rows) and `call_analysis` (1000 rows) contain BOTH NC and AND Capital contacts/calls in the same tables with no entity tag. The scheduled tasks (`call-ingest-hourly`, `call-sync`, etc.) pull ALL Salesfinity data without entity filtering. Every one of these tables needs an `entity` column, and the ingest tasks need to tag on arrival.

### 11.2 AND Capital Campaigns → Infrastructure

| Campaign ID | Name | Supabase Tables | Repos | Lovable Apps | Skills | Scheduled Tasks |
|---|---|---|---|---|---|---|
| `AND-LP-LETTER` | LP Letter Campaign | `targets` (AND subset), `sent_log` (AND subset), `outreach_queue` (AND subset), `campaigns` (AND subset), `pipeline_log` | `and-call-command-pipeline` (correctly named for this one), `nyc-war-story` | — | — | — |
| `AND-LP-CALL` | LP Cold Calling | `dialer_queue` (AND subset), `call_analysis` (AND subset), `do_not_call` (universal) | `coldcall-universe` (MIXED) | Marks NYC Hunt (`cb07d396`), NYC Outreach Hub (`2821f447`) | `cold-call-workflow`, `salesfinity-loader` | `call-ingest-hourly`, `call-sync`, `dnc-salesfinity-sync`, `priority-rebuild`, `queue-autocheck` |
| `AND-LP-LINKEDIN` | LP LinkedIn Outreach | No dedicated tables found | — | — | — | — |
| `AND-DEAL-SOURCE` | Deal Sourcing Cold Calls | `dialer_queue` (AND subset), `call_analysis` (AND subset) | — | NYC Deal Maker (`672ae5a6`) | — | `call-ingest-hourly`, `call-sync` |
| `AND-FUND-DISTRO` | Fund Brochure Distribution | No dedicated tables found | — | — | — | — |

**AND Capital's data is in 4 places:** 3 rogue Supabase instances (`iumy` Marks NYC Hunt, `wdhn` NYC Deal Maker, `pgoo` NYC Outreach Hub) PLUS mixed into the primary `rdnn` instance. Consolidation into `rdnn` under `and_capital` tag is Phase 1, step 6.

**AND Capital infrastructure discovered during audit that was NOT in the original 5-campaign table:**
- `iumytggxqtfyaxewgghb` — full investor CRM with FINRA/AUM data (contacts table)
- `wdhnsbzmcjpqbltkulwe` — attack_list + attack_notes + AI edge function (Gemini)
- `pgoogsxaljtjhwhydqtg` — most sophisticated DB: 4 tables, 3 views, 5 enums, daily briefing, propensity scoring

### 11.3 RevsUp Campaigns → Infrastructure

| Campaign ID | Name | Supabase Tables | Repos | Lovable Apps | Skills | Scheduled Tasks |
|---|---|---|---|---|---|---|
| `REV-CLIENT` | Recruiting Client Outreach | No dedicated tables found | — | — | `revsup-oo` | — |
| `REV-CANDIDATE` | Candidate Sourcing | No dedicated tables found | — | — | — | — |
| `REV-REFERRAL` | Referral Program | No dedicated tables found | — | — | — | — |

**RevsUp has almost zero infrastructure.** One skill (`revsup-oo` for Opportunity Overviews), one email (`ewing@revsup.com`), one Google Drive mount. Mark DeChant and John Kelly run it operationally. Any RevsUp calls through Salesfinity land in the same `call_analysis` and `dialer_queue` tables as NC and AND Capital — untagged. Ewing is inactive.

### 11.4 Standalone Campaigns → Infrastructure

| Campaign ID | Entity | Supabase Tables | Supabase Instance | Repos | Lovable Apps | Skills | Scheduled Tasks | Firewall Status |
|---|---|---|---|---|---|---|---|---|
| `FORGE-BOOMERANG` | The Forge (Atlanta) | `boomerang_targets` (227 rows) | `rdnnhxhohwjucvjwbwch` (LIVE — **SHOULD NOT BE HERE**) | None | None | None | None | **VIOLATED** — standalone data in shared DB. Needs own GitHub org + Supabase project in Phase 2. |
| `BIOLEV-SALE` | BioLev (Ewing 50% / Rex 50%) | None (static assets only) | None | None | Fitness Pitch Builder (`3d4ee5fc`) | None | None | **CLEAN** — no DB contamination. 31 PPTX + 4 Python + 1 Excel in Google Drive `00 - BioLev Sale/`. Needs own repo in Phase 2. |
| `SEASWEET-ROOFING` | Sea Sweet (Jeremy Christopher) | None | None | None | None | None | None | **CLEAN** — no DB contamination. Google Drive folders `04 - Sea Sweet` + `13 - New Roofing Rollup` only. NOT Next Chapter. Needs own repo in Phase 2. |
| `PEC-FRAUD` | Precision Exploration Corp | Unknown (Lovable-managed) | Lovable-managed (unknown instance ID) | None | Precision Exploration (`239c9bb2`), Remix (`63c4f5cd`), NMR Science Showcase (`f2fc9365`) | `pec-case-manager` | `pec-evidence-logger` (DISABLED), `pec-fact-finder` (DISABLED) | **CLEAN** — has own Supabase via Lovable. MANUAL ONLY. Never automate. |

### 11.5 Shared Capabilities — Which Tools Serve Which Campaigns

| Tool | NC Campaigns Using It | AND Campaigns Using It | RU Campaigns Using It | Routing Rule |
|---|---|---|---|---|
| **Salesfinity dialer** | NC-SELL-CALL | AND-LP-CALL, AND-DEAL-SOURCE | REV-CLIENT (Mark's calls) | Tag by target company type: home services = NC, LP/family office/hospital/energy = AND, SaaS hiring = RU |
| **Letter mailing engine** | NC-SELL-LETTER | AND-LP-LETTER | — | ENGINE is shared. CONTENT engine (tone, terms, templates) lives in entity business logic. Tag by recipient. |
| **Exa enrichment** | NC-SELL-LETTER, NC-TAM | AND-LP-LINKEDIN, AND-DEAL-SOURCE | — | Tag enrichment results with entity of target being enriched. |
| **Fireflies transcripts** | NC-TRANSCRIPT | AND-LP-CALL, AND-DEAL-SOURCE | REV-CLIENT | Tag by call context: deal calls/buyer-seller = NC, fund meetings/LP calls = AND, recruiting = RU |
| **Dossier pipeline** | NC-SELL-LETTER, NC-SELL-CALL, NC-TAM | Could serve AND but currently 100% NC | — | All current targets are NC. For multi-entity use, needs entity tagging in pipeline code. |
| **Google Drive** | Root-level + `01`, `03` folders | `02 - AND Capital/`, `_000_AND_Capital_ColdCall_Universe/` (MIXED) | ewing@revsup.com mount | AND Capital lives inside chapter.guide Drive. Classify by company type, not folder name. |
| **Supabase** | Tables on `rdnn` (NC subset) | Tables on `rdnn` (AND subset) + 3 rogue instances | No dedicated tables | Entity tag required on every row. Currently ZERO enforcement. |

### 11.6 Campaign Contamination Summary — Tables With Mixed Campaign Data

| Table | Rows | Campaigns Mixed In It | Why It's a Problem |
|---|---|---|---|
| `dialer_queue` | 646 | NC-SELL-CALL + AND-LP-CALL + AND-DEAL-SOURCE + possibly REV-CLIENT | Salesfinity is shared tool. Lists from any entity land in same table. No way to filter by campaign. |
| `call_analysis` | 1000 | NC-SELL-CALL + NC-TRANSCRIPT + AND-LP-CALL + AND-DEAL-SOURCE + possibly REV-CLIENT | Call scoring stores results without entity/campaign label. **This table should be the cleanup engine** — it classifies calls but doesn't tag entity on output. |
| `sent_log` | 27 | NC-SELL-LETTER + AND-LP-LETTER | Letters to business owners (NC) and family offices (AND) logged together. No way to report campaign performance per entity. |
| `outreach_queue` | 82 | NC-SELL-LETTER + AND-LP-LETTER | Pending sends from both entities in same queue. |
| `targets` | 201 | NC-SELL-LETTER + NC-SELL-CALL + NC-BUY-OUTREACH + possibly AND-DEAL-SOURCE | Almost all NC, but some could be AND deal-sourcing targets. Industry is the only signal. |
| `pipeline_log` | 1000+ | Every campaign that uses the pipeline | Agent actions logged without campaign or entity context. Domain name and title are the only classification signals. |
| `campaigns` | 5 | Unknown mix | Only 5 rows exist for 13+ defined campaign types. No entity prefix. No way for an LLM to know which business rules to apply. |
| `do_not_call` | 144 | ALL campaigns (universal) | This is correct by design — DNC is cross-entity. Not a contamination issue. |

### 11.7 Active Opportunity Tied to Campaign

| Campaign ID | Opportunity | Entity | Deadline | Infrastructure |
|---|---|---|---|---|
| `NC-BUY-OUTREACH` | **Debbie McGrath / HR.com** | Next Chapter (sell-side) | **Proposal due Monday 2026-03-31** | Staging: Debbie Deal Room (`a3bf07f3`). Production: Debbiedealroom.com (purchased, not built). Data: `deal_research` (67), `acquisition_targets` (9). Repos: `blank-canvas-proposal`, `sunshine-code-forge`. |

---

## SECTION 12: ROOT CAUSE

Ewing built the initial infrastructure before the entities were formally separated. ColdCall Universe was intentionally created as a single system to build campaigns, launch calls, and analyze results across all entities in one place. The names, labels, and data structures all inherited from this early phase. The Entity Classification Guide was written AFTER the infrastructure was built. This is not negligence — it's a natural consequence of building fast and formalizing later. The V2 build corrects this.

---

*This document maps the physical infrastructure and campaign-to-infrastructure relationships. For business logic, entity definitions, classification rules, campaign audiences/channels/purposes, person routing, decision trees, and lead lifecycle stages — see the Entity Classification Guide.*
