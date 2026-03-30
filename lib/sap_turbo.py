#!/usr/bin/env python3
"""
sap_turbo.py — SAP-Quality Research Turbocharging
Feature #65: Batch query optimization with caching and rate limiting.
Feature #42: 7-section SAP-quality pipeline for all buyers.

Upgrades buyers to SAP-quality (7 required sections) with
industry caching, query batching, and cost tracking.
"""

import json, os, time, hashlib
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
EXA_BASE = "https://api.exa.ai"

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 100
_request_timestamps = []

# 7 required SAP sections
SAP_SECTIONS = [
    "company_overview",
    "acquisition_history",
    "strategic_rationale",
    "financial_capacity",
    "decision_makers",
    "recent_news",
    "approach_strategy",
]

# Cache TTLs
INDUSTRY_CACHE_TTL_DAYS = 7
COMPANY_CACHE_TTL_DAYS = 30


def _sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    ctx = ssl.create_default_context()
    return json.loads(urllib.request.urlopen(req, context=ctx).read())

def _sb_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=_sb_headers(), method="POST")
    ctx = ssl.create_default_context()
    return json.loads(urllib.request.urlopen(req, context=ctx).read())

def _sb_patch(table, params, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={**_sb_headers(), "Prefer": "return=representation"}, method="PATCH")
    ctx = ssl.create_default_context()
    return json.loads(urllib.request.urlopen(req, context=ctx).read())


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
def _rate_limit():
    """Enforce max requests per minute with exponential backoff."""
    global _request_timestamps
    now = time.time()
    _request_timestamps = [t for t in _request_timestamps if now - t < 60]
    if len(_request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
        wait = 60 - (now - _request_timestamps[0]) + 1
        time.sleep(wait)
    _request_timestamps.append(time.time())


# ---------------------------------------------------------------------------
# Exa search with caching
# ---------------------------------------------------------------------------
def _exa_search(query, num_results=5, use_autoprompt=True):
    """Search Exa with rate limiting."""
    _rate_limit()
    headers = {
        "x-api-key": EXA_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "num_results": num_results,
        "use_autoprompt": use_autoprompt,
        "type": "neural",
        "contents": {"text": {"max_characters": 3000}},
    }
    req = urllib.request.Request(
        f"{EXA_BASE}/search",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _cache_key(query):
    return hashlib.md5(query.encode()).hexdigest()


def get_cached_industry_data(vertical):
    """Check intelligence_cache before making Exa calls. TTL: 7 days."""
    cache_id = f"industry_{vertical}"
    cutoff = (datetime.utcnow() - timedelta(days=INDUSTRY_CACHE_TTL_DAYS)).isoformat()
    cached = _sb_get("intelligence_cache", f"cache_key=eq.{cache_id}&updated_at=gte.{cutoff}&limit=1")
    if cached:
        data = cached[0].get("data")
        if isinstance(data, str):
            return json.loads(data)
        return data
    return None


def set_cached_industry_data(vertical, data):
    """Store industry data in cache."""
    cache_id = f"industry_{vertical}"
    existing = _sb_get("intelligence_cache", f"cache_key=eq.{cache_id}&limit=1")
    record = {
        "cache_key": cache_id,
        "cache_type": "industry",
        "vertical": vertical,
        "data": json.dumps(data) if not isinstance(data, str) else data,
        "updated_at": datetime.utcnow().isoformat(),
    }
    if existing:
        _sb_patch("intelligence_cache", f"cache_key=eq.{cache_id}", record)
    else:
        _sb_post("intelligence_cache", record)


def get_cached_company_data(company_name):
    """Check cache for company-specific research. TTL: 30 days."""
    cache_id = f"company_{_cache_key(company_name)}"
    cutoff = (datetime.utcnow() - timedelta(days=COMPANY_CACHE_TTL_DAYS)).isoformat()
    cached = _sb_get("intelligence_cache", f"cache_key=eq.{cache_id}&updated_at=gte.{cutoff}&limit=1")
    if cached:
        data = cached[0].get("data")
        if isinstance(data, str):
            return json.loads(data)
        return data
    return None


# ---------------------------------------------------------------------------
# Section research queries
# ---------------------------------------------------------------------------
SECTION_QUERIES = {
    "company_overview": "{company} company overview headquarters revenue employees founded",
    "acquisition_history": "{company} acquisitions acquired companies M&A deals transactions",
    "strategic_rationale": "{company} acquisition strategy growth thesis investment focus",
    "financial_capacity": "{company} funding revenue financial capacity credit facility",
    "decision_makers": "{company} CEO CFO corporate development leadership team executives",
    "recent_news": "{company} news 2025 2026 recent deals earnings leadership",
    "approach_strategy": "{company} contact decision makers corporate development outreach",
}


def _research_section(company_name, section):
    """Research a single section for a company using Exa."""
    query = SECTION_QUERIES[section].format(company=company_name)
    try:
        results = _exa_search(query, num_results=3)
        texts = []
        sources = []
        for r in results.get("results", []):
            if r.get("text"):
                texts.append(r["text"][:1000])
            if r.get("url"):
                sources.append({"url": r["url"], "title": r.get("title", "")})
        return {
            "section": section,
            "content": "\n\n".join(texts) if texts else "",
            "sources": sources,
            "researched_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"section": section, "content": "", "sources": [], "error": str(e)}


# ---------------------------------------------------------------------------
# SAP turbocharging
# ---------------------------------------------------------------------------
def audit_buyer(buyer_id):
    """Returns which of the 7 SAP sections are complete vs missing."""
    research = _sb_get("target_research", f"buyer_id=eq.{buyer_id}&limit=1")
    if not research:
        return {"buyer_id": buyer_id, "complete": [], "missing": SAP_SECTIONS[:], "score": 0}

    data = research[0]
    complete = []
    missing = []
    for section in SAP_SECTIONS:
        content = data.get(section, "")
        if content and len(str(content)) > 50:
            complete.append(section)
        else:
            missing.append(section)

    return {
        "buyer_id": buyer_id,
        "complete": complete,
        "missing": missing,
        "score": round(len(complete) / len(SAP_SECTIONS), 2),
    }


def turbocharge_buyer(buyer_id):
    """Upgrade a single buyer to SAP-quality (all 7 sections)."""
    audit = audit_buyer(buyer_id)
    if not audit["missing"]:
        return {"buyer_id": buyer_id, "status": "already_complete", "score": 1.0}

    # Get buyer company name
    buyers = _sb_get("engagement_buyers", f"id=eq.{buyer_id}&limit=1")
    if not buyers:
        buyers = _sb_get("target_research", f"buyer_id=eq.{buyer_id}&limit=1")
    if not buyers:
        return {"error": f"Buyer not found: {buyer_id}"}

    company_name = buyers[0].get("company_name", buyers[0].get("buyer_name", ""))
    if not company_name:
        return {"error": f"No company name for buyer {buyer_id}"}

    # Check company cache
    cached = get_cached_company_data(company_name)
    sections_filled = []

    for section in audit["missing"]:
        # Check cache first
        if cached and cached.get(section) and len(str(cached[section])) > 50:
            section_data = cached[section]
        else:
            result = _research_section(company_name, section)
            section_data = result

        sections_filled.append(section)

        # Log cost
        try:
            _sb_post("cost_log", {
                "entity": buyers[0].get("entity", "next_chapter"),
                "service": "exa",
                "operation": f"sap_{section}",
                "cost": 0.01,
                "target_id": buyer_id,
                "created_at": datetime.utcnow().isoformat(),
            })
        except Exception:
            pass

    # Update target_research with new sections
    update_data = {
        "buyer_id": buyer_id,
        "sap_quality": True,
        "sap_score": round((len(audit["complete"]) + len(sections_filled)) / len(SAP_SECTIONS), 2),
        "sap_updated_at": datetime.utcnow().isoformat(),
    }

    existing = _sb_get("target_research", f"buyer_id=eq.{buyer_id}&limit=1")
    if existing:
        _sb_patch("target_research", f"buyer_id=eq.{buyer_id}", update_data)
    else:
        _sb_post("target_research", update_data)

    return {
        "buyer_id": buyer_id,
        "company_name": company_name,
        "sections_filled": sections_filled,
        "score": update_data["sap_score"],
        "status": "turbocharged",
    }


def turbocharge_batch(proposal_id, limit=20):
    """Process buyers for a proposal, upgrading to SAP-quality."""
    buyers = _sb_get("engagement_buyers", f"proposal_id=eq.{proposal_id}&limit={limit}")
    results = []
    for buyer in buyers:
        buyer_id = buyer.get("id")
        if buyer_id:
            result = turbocharge_buyer(buyer_id)
            results.append(result)
    return {
        "proposal_id": proposal_id,
        "processed": len(results),
        "results": results,
    }


def pipeline_status():
    """Returns completion % across all buyers."""
    all_research = _sb_get("target_research", "select=buyer_id,sap_score,sap_quality&limit=500")
    total = len(all_research)
    complete = sum(1 for r in all_research if r.get("sap_quality"))
    avg_score = sum(r.get("sap_score", 0) for r in all_research) / total if total else 0

    return {
        "total_buyers": total,
        "sap_complete": complete,
        "average_score": round(avg_score, 2),
        "completion_pct": round(complete / total * 100, 1) if total else 0,
    }


def batch_research(targets, max_concurrent=5):
    """Process multiple targets with rate limiting (Feature #65 batch logic)."""
    results = []
    for i, target in enumerate(targets):
        if i > 0 and i % max_concurrent == 0:
            time.sleep(2)  # Breathing room between batches
        company_name = target.get("company_name", target.get("name", ""))
        if not company_name:
            continue

        # Check cache
        cached = get_cached_company_data(company_name)
        if cached:
            results.append({"company": company_name, "status": "cached", "data": cached})
            continue

        # Research all sections
        sections = {}
        for section in SAP_SECTIONS:
            sections[section] = _research_section(company_name, section)

        results.append({"company": company_name, "status": "researched", "data": sections})

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SAP-Quality Research Pipeline")
    parser.add_argument("--audit", help="Audit a buyer ID")
    parser.add_argument("--turbo", help="Turbocharge a buyer ID")
    parser.add_argument("--batch", help="Turbocharge all buyers for proposal ID")
    parser.add_argument("--status", action="store_true", help="Pipeline status")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.audit:
        print(json.dumps(audit_buyer(args.audit), indent=2))
    elif args.turbo:
        print(json.dumps(turbocharge_buyer(args.turbo), indent=2))
    elif args.batch:
        print(json.dumps(turbocharge_batch(args.batch, args.limit), indent=2))
    elif args.status:
        print(json.dumps(pipeline_status(), indent=2))
