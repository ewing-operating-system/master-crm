#!/usr/bin/env python3
"""
Profile Engine — turns a phone call into structured data.

Takes: company name + any known data (from call, transcript, research)
Produces: structured company profile with slider-bar fields, top 3 strengths,
          narrative, and battle plan foundation.

The profile feeds: proposals, data rooms, buyer targeting, outreach scripts.
"""

import json, os, sys, subprocess, time, psycopg2
from datetime import datetime

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/profile_engine.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | PROFILE | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def call_claude(prompt, timeout=300):
    try:
        result = subprocess.run(["claude", "-p", "--output-format", "text"],
                                input=prompt, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None
    except:
        return None

def parse_json(text):
    if not text: return None
    try: return json.loads(text)
    except:
        s, e = text.find('{'), text.rfind('}') + 1
        if s >= 0:
            try: return json.loads(text[s:e])
            except: pass
    return None


def build_profile(company_name, known_data=None):
    """
    Build a structured company profile from whatever data we have.

    known_data: dict with any of:
        owner_name, city, state, vertical, revenue, employees, years_in_business,
        services, service_area, commercial_pct, residential_pct, inbound_pct,
        outbound_pct, locations, transcript_notes, call_notes
    """
    if known_data is None:
        known_data = {}

    log(f"Building profile for {company_name}")

    # Step 1: Pull existing data from master-crm
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Companies table
    cur.execute("SELECT * FROM companies WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    db_data = dict(zip(cols, row)) if row else {}

    # Targets table (extra_fields has rich data)
    cur.execute("SELECT extra_fields FROM targets WHERE company_name ILIKE %s AND extra_fields IS NOT NULL LIMIT 1", (f"%{company_name}%",))
    row = cur.fetchone()
    if row and row[0] and isinstance(row[0], dict):
        for k, v in row[0].items():
            if v and k not in db_data:
                db_data[k] = v

    # Dossier final
    cur.execute("SELECT narrative, owner_name, owner_background, culture_signals, valuation_analysis, overall_score FROM dossier_final WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    row = cur.fetchone()
    dossier = {}
    if row:
        dossier = {"narrative": row[0], "owner_name": row[1], "owner_background": row[2], "culture_signals": row[3], "valuation": row[4], "overall_score": row[5]}

    # Proposals (may have richer data from Claude CLI generation)
    cur.execute("""SELECT company_narrative, top_3_strengths, market_analysis, valuation_range,
                          attack_plan, buyer_profile, estimated_revenue, employee_count,
                          service_mix, revenue_sources, commercial_vs_residential
                   FROM proposals WHERE company_name ILIKE %s ORDER BY quality_score DESC LIMIT 1""",
                (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    proposal = dict(zip(cols, row)) if row else {}

    conn.close()

    # Merge all sources: known_data > proposal > dossier > db_data
    merged = {}
    for source in [db_data, dossier, proposal, known_data]:
        for k, v in source.items():
            if v is not None and v != '' and v != 'None':
                merged[k] = v

    merged["company_name"] = company_name

    log(f"  Data sources: db={'Y' if db_data else 'N'}, dossier={'Y' if dossier else 'N'}, proposal={'Y' if proposal else 'N'}, known={'Y' if known_data else 'N'}")

    # Step 2: Generate the profile via Claude CLI
    prompt = f"""You are building a structured company profile for M&A advisory.

KNOWN DATA:
{json.dumps({k: str(v)[:300] for k, v in merged.items() if v}, indent=2, default=str)}

Generate a complete company profile JSON. For fields where data is missing, use your best estimate
and ALWAYS disclose methodology (e.g., "Estimated based on X employees × $Y/employee").
For fields where you truly cannot estimate, use null.

GUARDRAILS:
- Education is king — show your work on estimates
- No negative facts (divorce, lawsuits, closures)
- Frame everything from THEIR perspective

Return this exact JSON structure:
{{
    "company_name": "{company_name}",
    "owner_name": "",
    "owner_title": "",

    "location": {{
        "city": "",
        "state": "",
        "address": ""
    }},

    "vertical": "",
    "sub_vertical": "",

    "financials": {{
        "estimated_revenue": null,
        "revenue_methodology": "How this was estimated",
        "estimated_ebitda": null,
        "ebitda_margin_pct": null,
        "ebitda_methodology": "",
        "sde": null,
        "sde_methodology": ""
    }},

    "operations": {{
        "employee_count": null,
        "years_in_business": null,
        "year_founded": null,
        "locations_served": null,
        "service_area_description": "",
        "services_offered": []
    }},

    "revenue_mix": {{
        "commercial_pct": null,
        "residential_pct": null,
        "government_pct": null,
        "methodology": ""
    }},

    "revenue_sources": {{
        "inbound_marketing_pct": null,
        "outbound_sales_pct": null,
        "referral_pct": null,
        "repeat_customer_pct": null,
        "methodology": ""
    }},

    "top_3_strengths": [
        {{"strength": "", "evidence": "", "why_it_matters_to_buyers": ""}},
        {{"strength": "", "evidence": "", "why_it_matters_to_buyers": ""}},
        {{"strength": "", "evidence": "", "why_it_matters_to_buyers": ""}}
    ],

    "valuation": {{
        "estimated_low": null,
        "estimated_mid": null,
        "estimated_high": null,
        "multiple_type": "EBITDA or SDE",
        "multiple_range": "",
        "methodology": "",
        "key_drivers": [],
        "key_risks": []
    }},

    "market_position": {{
        "competitive_advantages": [],
        "market_trends": "",
        "buyer_activity_level": "",
        "recent_transactions_in_vertical": ""
    }},

    "owner_profile": {{
        "background": "",
        "succession_signals": "",
        "likely_motivation": "",
        "best_approach_angle": ""
    }},

    "quality_score": 0,
    "data_completeness_pct": 0,
    "fields_estimated": [],
    "fields_missing": []
}}

Return ONLY valid JSON."""

    log(f"  Generating profile via Claude CLI...")
    result = call_claude(prompt)
    profile = parse_json(result)

    if not profile:
        log(f"  Claude CLI failed or unparseable — trying DeepSeek")
        import urllib.request, ssl
        ctx = ssl.create_default_context()
        payload = json.dumps({"model": "deepseek/deepseek-chat-v3-0324",
                              "messages": [{"role": "user", "content": prompt}],
                              "max_tokens": 6000, "temperature": 0.2}).encode()
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload,
                headers={"Authorization": "Bearer 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",
                         "Content-Type": "application/json"}, method="POST")
            resp = urllib.request.urlopen(req, context=ctx, timeout=120)
            result = json.loads(resp.read())["choices"][0]["message"]["content"]
            profile = parse_json(result)
        except:
            pass

    if not profile:
        log(f"  FAILED to generate profile for {company_name}")
        return None

    # Step 3: Store in Supabase
    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cur = conn.cursor()

    # Update companies table with profile data
    financials = profile.get("financials", {})
    operations = profile.get("operations", {})
    location = profile.get("location", {})

    cur.execute("""UPDATE companies SET
        vertical = COALESCE(%s, vertical),
        city = COALESCE(%s, city),
        state = COALESCE(%s, state),
        employee_count = COALESCE(%s, employee_count),
        year_founded = COALESCE(%s, year_founded),
        updated_at = now()
        WHERE company_name ILIKE %s""",
        (profile.get("vertical"), location.get("city"), location.get("state"),
         operations.get("employee_count"), operations.get("year_founded"),
         f"%{company_name}%"))

    # Store full profile in intelligence_cache
    cur.execute("""INSERT INTO intelligence_cache (company_id, entity, key, value, source_agent)
        SELECT c.id, c.entity, 'company_profile', %s, 'profile_engine'
        FROM companies c WHERE c.company_name ILIKE %s
        ON CONFLICT DO NOTHING""",
        (json.dumps(profile, default=str), f"%{company_name}%"))

    conn.close()

    quality = profile.get("quality_score", 0)
    completeness = profile.get("data_completeness_pct", 0)
    log(f"  Profile COMPLETE: {company_name} | Quality: {quality} | Completeness: {completeness}%")

    return profile


def build_profiles_for_all_proposals():
    """Build profiles for all companies that have proposals."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company_name FROM proposals ORDER BY company_name")
    companies = [r[0] for r in cur.fetchall()]
    conn.close()

    log(f"\n{'='*60}")
    log(f"BUILDING PROFILES FOR {len(companies)} COMPANIES")
    log(f"{'='*60}")

    results = {}
    for company in companies:
        profile = build_profile(company)
        results[company] = "SUCCESS" if profile else "FAILED"
        time.sleep(2)  # breathing room between Claude CLI calls

    log(f"\nResults:")
    for company, status in results.items():
        log(f"  {company}: {status}")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        company = " ".join(sys.argv[1:])
        profile = build_profile(company)
        if profile:
            print(json.dumps(profile, indent=2, default=str))
    else:
        build_profiles_for_all_proposals()
