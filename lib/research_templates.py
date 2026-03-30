#!/usr/bin/env python3
"""
research_templates.py — Entity-specific research prompt templates for Master CRM.

Provides Exa query prompts and narrative story hooks tuned per entity and vertical.
Used by the researcher agent and executor to produce personalized dossiers and letters.

Usage:
    from lib.research_templates import get_research_template, get_story_hooks, research_target
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")

ctx = ssl.create_default_context()

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY: next_chapter — Home services M&A advisory
# Focus: Owner story, trade-specific ops, exit readiness, recurring revenue
# ══════════════════════════════════════════════════════════════════════════════

NEXT_CHAPTER_BASE = {
    "description": "Next Chapter M&A Advisory — Home services sell-side research",
    "research_goals": [
        "Owner story: years in business, how they started, family involvement",
        "Revenue signal: size indicators from reviews, truck fleet, employee count",
        "Recurring revenue: service agreements, maintenance contracts, subscriptions",
        "Owner dependency: is the owner the business, or does it run without them?",
        "Local reputation: BBB rating, Google reviews, community ties",
        "Exit readiness: any mentions of retirement, succession, sale, or transition",
        "Certifications and licenses: state licenses, manufacturer certs, NATE, EPA",
    ],
    "exa_queries": [
        "{company_name} {city} {state} owner founder history",
        "{company_name} {city} employees technicians fleet size",
        "{company_name} reviews BBB rating Google 4 5 stars",
        "{company_name} service agreement maintenance contract recurring",
        "{company_name} {owner_name} LinkedIn background",
        "{vertical} company {city} {state} acquisition sale sold 2024 2025",
    ],
    "content_mode": "highlights",
    "num_results": 6,
}

NEXT_CHAPTER_VERTICAL_OVERRIDES = {
    "water_treatment": {
        "additional_goals": [
            "NSF/ANSI certifications (42, 44, 53, 58)",
            "Commercial vs residential split",
            "Recurring filter replacement / salt delivery routes",
            "Equipment: RO systems, water softeners, whole-home filtration",
            "Regulatory compliance: state water quality board",
        ],
        "extra_queries": [
            "{company_name} water softener RO filtration residential commercial",
            "{company_name} NSF certified water treatment",
            "water treatment company {city} {state} sold acquired roll-up 2024 2025",
        ],
    },
    "hvac": {
        "additional_goals": [
            "NATE-certified technician count",
            "Service area radius (miles from base)",
            "Equipment brands carried: Carrier, Trane, Lennox, Daikin",
            "Commercial vs residential mix",
            "Seasonal revenue patterns and off-season revenue",
        ],
        "extra_queries": [
            "{company_name} NATE certified HVAC technicians",
            "{company_name} Carrier Trane Lennox authorized dealer",
            "HVAC company {city} {state} acquisition sold PE roll-up 2024 2025",
        ],
    },
    "plumbing": {
        "additional_goals": [
            "Master plumber license status",
            "Emergency/24-hour service capacity",
            "Commercial plumbing vs residential split",
            "Specialty work: hydro-jetting, trenchless, backflow",
        ],
        "extra_queries": [
            "{company_name} master plumber licensed {state}",
            "{company_name} commercial residential plumbing",
            "plumbing company {city} {state} acquisition sold 2024 2025",
        ],
    },
    "roofing": {
        "additional_goals": [
            "GAF/CertainTeed/Owens Corning certified installer status",
            "Storm restoration vs replacement revenue mix",
            "Insurance claim work percentage",
            "Crew size and subcontractor use",
        ],
        "extra_queries": [
            "{company_name} GAF certified roofing installer",
            "{company_name} storm restoration insurance claims",
            "roofing company {city} {state} acquisition sold PE 2024 2025",
        ],
    },
    "pest_control": {
        "additional_goals": [
            "State pesticide applicator license",
            "Recurring contract base: quarterly/monthly customers",
            "Termite warranty portfolio value",
            "Route density (stops per day per tech)",
            "Specialty: termite, rodent, bed bug, wildlife",
        ],
        "extra_queries": [
            "{company_name} termite warranty quarterly pest control",
            "{company_name} pest control routes recurring contracts",
            "pest control company {city} {state} acquisition sold Rollins Rentokil 2024 2025",
        ],
    },
    "concrete_precast": {
        "additional_goals": [
            "NPCA plant certification status",
            "Product mix: pipe, box culvert, manholes, architectural, structural",
            "Geographic delivery radius",
            "DOT/municipal contract history",
            "Plant capacity vs current utilization",
        ],
        "extra_queries": [
            "{company_name} NPCA certified precast concrete plant",
            "{company_name} DOT municipal precast pipe culvert",
            "precast concrete company {state} acquisition sold 2024 2025",
        ],
    },
    "flooring": {
        "additional_goals": [
            "Commercial vs residential split",
            "Floor types carried: hardwood, LVP, tile, carpet, epoxy",
            "Installation crew count vs subcontract",
            "Builder/GC relationships",
            "Recurring commercial maintenance contracts",
        ],
        "extra_queries": [
            "{company_name} commercial residential flooring installation",
            "{company_name} flooring builder contractor relationships",
            "flooring company {city} {state} acquisition sold 2024 2025",
        ],
    },
    "healthcare": {
        "additional_goals": [
            "HIPAA compliance and EHR system",
            "Payer mix: Medicare, Medicaid, commercial insurance, self-pay",
            "Patient volume and capacity utilization",
            "Provider count and credentialing",
        ],
        "extra_queries": [
            "{company_name} healthcare patients providers {city}",
            "{company_name} Medicare Medicaid payer mix",
            "healthcare clinic {city} {state} acquisition sold 2024 2025",
        ],
    },
    "energy": {
        "additional_goals": [
            "FERC/state regulatory licenses",
            "Asset type: generation, transmission, distribution, storage",
            "Contract tenor: PPA length, offtake agreements",
            "Technology: solar, wind, natural gas, battery storage",
        ],
        "extra_queries": [
            "{company_name} energy project MW capacity {state}",
            "{company_name} PPA offtake agreement contract",
            "energy company {state} acquisition sold PE infrastructure 2024 2025",
        ],
    },
    "saas": {
        "additional_goals": [
            "ARR/MRR indicators from job postings, press releases",
            "Tech stack from job listings (engineering roles)",
            "Funding history: seed, series A/B, bootstrapped",
            "Customer segments: SMB, mid-market, enterprise",
            "Churn signals: reviews on G2, Capterra, Trustpilot",
        ],
        "extra_queries": [
            "{company_name} SaaS ARR revenue growth customers",
            "{company_name} funding series investment Crunchbase",
            "{company_name} G2 Capterra reviews rating",
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY: and_capital — PE fund management, LP fundraising
# Focus: Fund thesis, portfolio, returns, team credentials, market position
# ══════════════════════════════════════════════════════════════════════════════

AND_CAPITAL_BASE = {
    "description": "AND Capital — LP and deal source research",
    "research_goals": [
        "Fund thesis and investment criteria",
        "Portfolio companies: sectors, deal sizes, vintage",
        "Return history: exits, realized IRR, DPI where available",
        "Team credentials: deal background, operating experience",
        "Market position: differentiation from other funds",
        "LP base composition: family offices, endowments, pension, HNW",
        "Current fund status: raising, closed, deploying",
    ],
    "exa_queries": [
        "{company_name} fund thesis investment criteria portfolio",
        "{company_name} {contact_name} managing partner background",
        "{company_name} portfolio companies exits returns",
        "{company_name} limited partners family office endowment",
        "{company_name} fund size AUM raise close",
        "{vertical} private equity deal 2024 2025 {state}",
    ],
    "content_mode": "text",
    "num_results": 8,
}

AND_CAPITAL_VERTICAL_OVERRIDES = {
    "healthcare": {
        "additional_goals": [
            "Healthcare sub-sector focus: physician practice, med-tech, behavioral health",
            "Regulatory environment understanding",
            "Value-based care thesis",
        ],
        "extra_queries": [
            "{company_name} healthcare investment physician practice med-tech",
            "healthcare PE firm {state} fund raise close 2024 2025",
        ],
    },
    "energy": {
        "additional_goals": [
            "Clean energy vs traditional energy thesis",
            "Infrastructure vs operating company focus",
            "ESG commitment and reporting",
        ],
        "extra_queries": [
            "{company_name} energy infrastructure investment clean renewable",
            "energy PE fund raise close {state} 2024 2025",
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY: revsup — Contingent recruiting for SaaS revenue roles
# Focus: Company culture, tech stack, growth stage, open roles, comp benchmarks
# ══════════════════════════════════════════════════════════════════════════════

REVSUP_BASE = {
    "description": "RevsUp — SaaS revenue recruiting research",
    "research_goals": [
        "Company culture and employer brand (Glassdoor, Blind, LinkedIn)",
        "Tech stack from job postings and engineering roles",
        "Growth stage: seed, Series A/B/C, growth, pre-IPO",
        "Open revenue roles: AE, SDR, VP Sales, CRO, CSM, RevOps",
        "Compensation benchmarks for revenue roles in their market",
        "Recent funding events (signals hiring surge)",
        "Sales methodology: MEDDIC, Challenger, SPIN, PLG",
    ],
    "exa_queries": [
        "{company_name} jobs hiring sales account executive SDR",
        "{company_name} Glassdoor reviews culture compensation",
        "{company_name} funding raise series investment 2024 2025",
        "{company_name} tech stack CRM Salesforce HubSpot",
        "{company_name} revenue team VP sales CRO leadership",
        "SaaS {vertical} revenue roles compensation benchmark 2025",
    ],
    "content_mode": "highlights",
    "num_results": 6,
}

REVSUP_VERTICAL_OVERRIDES = {
    "saas": {
        "additional_goals": [
            "PLG vs sales-led vs hybrid GTM motion",
            "ACV range and deal cycle length",
            "SDR to AE ratio as team maturity signal",
        ],
        "extra_queries": [
            "{company_name} PLG sales-led growth GTM motion",
            "{company_name} ACV deal cycle sales process",
        ],
    },
    "hr_tech": {
        "additional_goals": [
            "HCM suite vs point solution positioning",
            "CHRO vs HR buyer vs operations buyer",
        ],
        "extra_queries": [
            "{company_name} HCM HRIS payroll HR tech buyers",
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# STORY HOOKS — Narrative angles for letter generation
# Per-vertical hooks that make letters feel researched, not templated
# ══════════════════════════════════════════════════════════════════════════════

STORY_HOOKS = {
    "next_chapter": {
        "water_treatment": [
            "The water treatment business you built solves a problem every family in {city} faces — clean, safe water. That kind of essential service attracts serious buyers.",
            "A recurring revenue base of filter replacements and service agreements is exactly what today's acquirers pay a premium for in water treatment.",
            "Regional operators who built their routes from scratch are becoming the most sought-after acquisition targets in the water space right now.",
        ],
        "hvac": [
            "HVAC businesses with strong maintenance agreement books are trading at the highest multiples in the trades right now — because buyers see the recurring revenue.",
            "The HVAC market in {state} is consolidating fast. Owner-operators who know their territory are exactly what PE-backed platforms are paying premium prices to acquire.",
            "After {years_in_business} years building a reputation in {city}, your customer list is an asset that strategic buyers are willing to pay for.",
        ],
        "plumbing": [
            "Plumbing businesses with trained crews and commercial relationships are in high demand from buyers who want to add a trade alongside their HVAC platform.",
            "The consolidation happening in plumbing right now is creating real exits for owners who spent decades building route density and licensed crews.",
            "A licensed plumbing business in {state} with a book of commercial clients is a different asset than most buyers encounter — and they pay accordingly.",
        ],
        "roofing": [
            "Storm restoration revenue is attractive to buyers because it's proven your team can scale fast — exactly the capability PE platforms want.",
            "Certified installer status with a major manufacturer is a durable competitive advantage that sophisticated buyers factor into their offers.",
            "Roofing businesses with strong insurance claim relationships in {state} are some of the most-approached companies in the trades M&A market.",
        ],
        "pest_control": [
            "A recurring quarterly pest control book is one of the most predictable revenue streams in all of home services — buyers know it and price it accordingly.",
            "The termite warranty portfolio you've built represents years of customer trust that rolls into a new owner at closing.",
            "Pest control businesses with route density in suburban markets like {city} are actively sought by national roll-ups right now.",
        ],
        "concrete_precast": [
            "NPCA-certified precast plants with established DOT relationships are rare assets — buyers in the infrastructure space know it.",
            "The capital equipment and plant certifications you've accumulated over {years_in_business} years represent a barrier to entry that acquirers value highly.",
            "Precast concrete businesses serving municipal markets command strong multiples because the contracts are long-term and the relationships are sticky.",
        ],
        "flooring": [
            "A commercial flooring business with builder relationships is a platform asset — buyers see the recurring project flow as a core part of the value.",
            "The installation crew you've built and the commercial accounts you've maintained make your business the kind of asset that commands strategic interest.",
            "Flooring businesses with a mix of commercial and residential revenue in growth markets like {city} are attracting attention from national services companies.",
        ],
        "default": [
            "The business you've built in {city} over {years_in_business} years is exactly the kind of asset the market is paying well for right now.",
            "Owner-operators who built their company without outside capital often find themselves with more options — and more leverage — than they expected when they decide to explore a sale.",
        ],
    },
    "and_capital": {
        "healthcare": [
            "The consolidation happening in {vertical} is creating significant opportunities for operators with the right capital structure and sector expertise.",
            "Family office and institutional LPs are increasingly allocating to healthcare because the demographics make the thesis durable across market cycles.",
        ],
        "energy": [
            "The infrastructure buildout required for clean energy transition is creating multi-decade investment opportunities that sophisticated LPs are positioning for now.",
            "Energy assets with contracted cash flows represent the kind of yield-plus-growth profile that family offices have historically found in real estate — but with better risk-adjusted returns.",
        ],
        "default": [
            "Former business owners who have liquidity often become the most aligned LPs — they understand what it means to build something and back operators who do the same.",
            "AND Capital's approach differs from institutional funds: we invest alongside operators, not over them.",
        ],
    },
    "revsup": {
        "saas": [
            "The companies growing fastest right now share one trait: they hired the right first VP of Sales before they needed one.",
            "Revenue hiring is the highest-leverage investment a Series B company makes — the wrong hire costs two years of runway, the right hire compounds.",
        ],
        "hr_tech": [
            "HR tech buyers are increasingly sophisticated — they require AEs who understand the CHRO agenda, not just the feature list.",
        ],
        "default": [
            "The best revenue talent isn't actively looking. RevsUp finds them before they're available.",
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def get_research_template(entity, vertical=None):
    """
    Return the research template dict for a given entity and vertical.

    Args:
        entity:   'next_chapter', 'and_capital', or 'revsup'
        vertical: vertical string (optional). Falls back to base template if no override.

    Returns:
        dict with keys:
          description, research_goals, exa_queries, content_mode, num_results,
          additional_goals (if vertical override), extra_queries (if vertical override)
    """
    entity_map = {
        "next_chapter": (NEXT_CHAPTER_BASE, NEXT_CHAPTER_VERTICAL_OVERRIDES),
        "and_capital": (AND_CAPITAL_BASE, AND_CAPITAL_VERTICAL_OVERRIDES),
        "revsup": (REVSUP_BASE, REVSUP_VERTICAL_OVERRIDES),
    }

    if entity not in entity_map:
        raise ValueError(f"Unknown entity '{entity}'. Valid: {list(entity_map.keys())}")

    base, overrides = entity_map[entity]
    template = dict(base)  # shallow copy

    if vertical and vertical in overrides:
        override = overrides[vertical]
        template["additional_goals"] = override.get("additional_goals", [])
        template["extra_queries"] = override.get("extra_queries", [])
        template["vertical"] = vertical
    else:
        template["additional_goals"] = []
        template["extra_queries"] = []
        template["vertical"] = vertical or "general"

    return template


def get_story_hooks(entity, vertical=None):
    """
    Return narrative story hooks for letter generation.

    Args:
        entity:   'next_chapter', 'and_capital', or 'revsup'
        vertical: vertical string. Falls back to 'default' hooks.

    Returns:
        list of hook strings (with {placeholder} variables for formatting)
    """
    entity_hooks = STORY_HOOKS.get(entity, {})
    if vertical and vertical in entity_hooks:
        return entity_hooks[vertical]
    return entity_hooks.get("default", [
        "The business you've built represents years of focused execution — that has real market value today."
    ])


def build_exa_queries(entity, vertical, context):
    """
    Build formatted Exa query strings from template + context variables.

    Args:
        entity:   entity string
        vertical: vertical string
        context:  dict with variables: company_name, city, state, owner_name,
                  contact_name, years_in_business, etc.

    Returns:
        list of formatted query strings
    """
    template = get_research_template(entity, vertical)
    all_queries = template.get("exa_queries", []) + template.get("extra_queries", [])

    formatted = []
    for q in all_queries:
        try:
            formatted.append(q.format_map(_SafeDict(context)))
        except Exception:
            formatted.append(q)  # keep raw on format error

    return formatted


class _SafeDict(dict):
    """Format dict that returns '{key}' for missing keys instead of raising."""
    def __missing__(self, key):
        return f"{{{key}}}"


def research_target(target_id):
    """
    Run the full research pipeline for a target using entity-appropriate templates.

    Looks up target from Supabase `targets` table, determines entity and vertical,
    fetches Exa queries, and stores results to `research_cache` table.

    Args:
        target_id: UUID of the target record in Supabase

    Returns:
        dict with research results and template metadata
    """
    # Load target
    url = f"{SUPABASE_URL}/rest/v1/targets?id=eq.{target_id}&limit=1"
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    req = urllib.request.Request(url, headers=h)
    resp = urllib.request.urlopen(req, context=ctx, timeout=20)
    rows = json.loads(resp.read())

    if not rows:
        raise ValueError(f"Target not found: {target_id}")

    target = rows[0]
    entity = target.get("entity", "next_chapter")
    vertical = target.get("vertical") or target.get("primary_vertical") or "default"
    company_name = target.get("company_name") or target.get("name", "")
    city = target.get("city", "")
    state = target.get("state", "")
    owner_name = target.get("owner_name") or target.get("primary_contact_name", "")

    context = {
        "company_name": company_name,
        "city": city,
        "state": state,
        "owner_name": owner_name,
        "contact_name": owner_name,
        "vertical": vertical,
        "years_in_business": target.get("years_in_business", ""),
    }

    # Build queries
    template = get_research_template(entity, vertical)
    queries = build_exa_queries(entity, vertical, context)
    hooks = get_story_hooks(entity, vertical)

    result = {
        "target_id": target_id,
        "entity": entity,
        "vertical": vertical,
        "company_name": company_name,
        "template_description": template.get("description", ""),
        "research_goals": template.get("research_goals", []) + template.get("additional_goals", []),
        "exa_queries": queries,
        "story_hooks": hooks,
        "context": context,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store to research_cache for executor to consume
    try:
        cache_payload = json.dumps({
            "target_id": target_id,
            "entity": entity,
            "vertical": vertical,
            "template_description": template.get("description", ""),
            "research_goals": result["research_goals"],
            "exa_queries": queries,
            "story_hooks": hooks,
            "context": context,
            "generated_at": result["generated_at"],
        }, default=str).encode()

        cache_h = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates",
        }
        cache_req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/research_cache",
            data=cache_payload, headers=cache_h, method="POST"
        )
        urllib.request.urlopen(cache_req, context=ctx, timeout=20)
    except Exception:
        pass  # Cache write is best-effort

    return result


def list_templates():
    """Return a summary of all available entity/vertical combinations."""
    summary = []
    combos = [
        ("next_chapter", list(NEXT_CHAPTER_VERTICAL_OVERRIDES.keys()) + ["default"]),
        ("and_capital", list(AND_CAPITAL_VERTICAL_OVERRIDES.keys()) + ["default"]),
        ("revsup", list(REVSUP_VERTICAL_OVERRIDES.keys()) + ["default"]),
    ]
    for entity, verticals in combos:
        for vertical in verticals:
            t = get_research_template(entity, vertical if vertical != "default" else None)
            summary.append({
                "entity": entity,
                "vertical": vertical,
                "description": t.get("description", ""),
                "goal_count": len(t.get("research_goals", [])) + len(t.get("additional_goals", [])),
                "query_count": len(t.get("exa_queries", [])) + len(t.get("extra_queries", [])),
                "hook_count": len(get_story_hooks(entity, vertical if vertical != "default" else None)),
            })
    return summary


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("research_templates.py — available templates\n")
    for t in list_templates():
        print(
            f"  {t['entity']:15s} | {t['vertical']:18s} | "
            f"{t['goal_count']:2d} goals | {t['query_count']:2d} queries | "
            f"{t['hook_count']:2d} hooks"
        )

    print("\nExample — next_chapter / hvac:")
    tmpl = get_research_template("next_chapter", "hvac")
    print(f"  Goals: {len(tmpl['research_goals']) + len(tmpl['additional_goals'])}")
    print(f"  Queries: {len(tmpl['exa_queries']) + len(tmpl['extra_queries'])}")
    print(f"  Sample query: {tmpl['exa_queries'][0]}")

    print("\nExample story hooks — next_chapter / hvac:")
    for hook in get_story_hooks("next_chapter", "hvac"):
        print(f"  - {hook[:90]}...")
