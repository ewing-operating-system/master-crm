#!/usr/bin/env python3
"""
Proposal Engine — generates complete NC sell-side proposals with attack plans.

Takes a company name, pulls all data from master-crm, generates:
1. Company narrative (all about them)
2. Market analysis with multiples
3. Valuation range estimate
4. Buyer profile + target list
5. Attack plan (outreach strategy, channels, timeline)
6. Letter templates, call scripts, LinkedIn messages
7. Polished HTML output

Uses Claude CLI ($0.00) for all content generation.
Falls back to OpenRouter if Claude CLI fails.
"""

import json, os, sys, subprocess, time, urllib.request, ssl, psycopg2

# ─── Config ──────────────────────────────────────────────────────────────────

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
SUPABASE_URL = "https://dwrnfpjcvydhmhnvyzov.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s"
OPENROUTER_KEY = "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"
EXA_KEY = "97e41046-ec91-4647-8e80-f6da354e2641"
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/overnight-build.log")
MULTIPLES_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/data-export/market_multiples.json")

ctx = ssl.create_default_context()
total_cost = 0.0

def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def log_cost(amount, provider, operation):
    global total_cost
    total_cost += amount
    if amount > 0:
        log(f"  COST: ${amount:.4f} ({provider}/{operation}) | Running: ${total_cost:.4f}")

# ─── LLM Callers ─────────────────────────────────────────────────────────────

def call_claude(prompt, timeout=300):
    """Claude CLI — $0.00, highest quality."""
    try:
        start = time.time()
        result = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt, capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.time() - start
        if result.returncode == 0 and result.stdout.strip():
            log_cost(0, "claude_cli", "proposal_generation")
            return result.stdout.strip(), elapsed
        else:
            log(f"  Claude CLI failed: exit={result.returncode}, stderr={result.stderr[:100]}")
            return None, elapsed
    except subprocess.TimeoutExpired:
        log(f"  Claude CLI timeout after {timeout}s")
        return None, timeout
    except Exception as e:
        log(f"  Claude CLI error: {e}")
        return None, 0

def call_openrouter(prompt, model="deepseek/deepseek-chat-v3-0324", max_tokens=8000):
    """OpenRouter fallback."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }).encode()

    backoffs = [15, 30, 60]
    for attempt in range(4):
        if attempt > 0:
            time.sleep(backoffs[attempt - 1])
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nextchapteradvisory.com",
                },
                method="POST"
            )
            start = time.time()
            resp = urllib.request.urlopen(req, context=ctx, timeout=180)
            result = json.loads(resp.read())
            elapsed = time.time() - start
            text = result["choices"][0]["message"]["content"]
            cost = result.get("usage", {}).get("total_cost", 0) or 0
            log_cost(cost, "openrouter", model.split("/")[-1])
            return text, elapsed
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            log(f"  OpenRouter error: {e.code}")
            return None, 0
    return None, 0

def generate(prompt, label="content"):
    """Try Claude CLI, fall back to DeepSeek, then GPT-4o Mini."""
    log(f"  Generating: {label}")

    # Try Claude CLI first
    result, elapsed = call_claude(prompt)
    if result:
        log(f"  Generated via Claude CLI in {elapsed:.0f}s")
        return result

    # Fallback 1: DeepSeek
    log(f"  Falling back to DeepSeek V3")
    result, elapsed = call_openrouter(prompt, "deepseek/deepseek-chat-v3-0324")
    if result:
        log(f"  Generated via DeepSeek in {elapsed:.0f}s")
        return result

    # Fallback 2: GPT-4o Mini
    log(f"  Falling back to GPT-4o Mini")
    result, elapsed = call_openrouter(prompt, "openai/gpt-4o-mini")
    if result:
        log(f"  Generated via GPT-4o Mini in {elapsed:.0f}s")
        return result

    log(f"  ALL LLMs FAILED for {label}")
    return None

# ─── Exa Search ──────────────────────────────────────────────────────────────

def exa_search(query, num_results=5):
    """Search Exa for company/industry data."""
    payload = json.dumps({
        "query": query,
        "num_results": num_results,
        "type": "auto",
        "contents": {"text": {"max_characters": 3000}}
    }).encode()

    try:
        req = urllib.request.Request(
            "https://api.exa.ai/search",
            data=payload,
            headers={
                "x-api-key": EXA_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        result = json.loads(resp.read())
        cost = num_results * 0.006
        log_cost(cost, "exa", "web_search")
        return result.get("results", [])
    except Exception as e:
        log(f"  Exa error: {e}")
        return []

# ─── Data Assembly ───────────────────────────────────────────────────────────

def get_company_data(company_name):
    """Pull all existing data for a company from master-crm."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    data = {"company_name": company_name, "sources": []}

    # Companies table
    cur.execute("SELECT * FROM companies WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        company = dict(zip(cols, row))
        data.update({k: v for k, v in company.items() if v is not None})
        data["sources"].append("companies_table")

    # Targets table (richer data in extra_fields)
    cur.execute("SELECT * FROM targets WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        target = dict(zip(cols, row))
        data["target_id"] = target.get("id")
        data["pipeline_status"] = target.get("pipeline_status")
        if target.get("extra_fields") and isinstance(target["extra_fields"], dict):
            for k, v in target["extra_fields"].items():
                if v and k not in data:
                    data[k] = v
        data["sources"].append("targets_table")

    # Dossier final
    cur.execute("SELECT * FROM dossier_final WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        dossier = dict(zip(cols, row))
        for k, v in dossier.items():
            if v and k not in data:
                data[k] = v
        data["sources"].append("dossier_final")

    # Deal research
    cur.execute("SELECT * FROM deal_research WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        deal = dict(zip(cols, row))
        data["deal_research"] = deal
        data["sources"].append("deal_research")

    # Contacts
    cur.execute("""SELECT c.* FROM contacts c
                   JOIN companies co ON c.company_id = co.id
                   WHERE co.company_name ILIKE %s LIMIT 5""", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    contacts = [dict(zip(cols, r)) for r in cur.fetchall()]
    if contacts:
        data["contacts"] = contacts
        data["sources"].append("contacts_table")

    conn.close()
    return data

def enrich_with_exa(data):
    """Fill gaps using Exa search. Only searches for missing critical fields."""
    company = data.get("company_name", "")
    city = data.get("city", "")
    state = data.get("state", "")
    owner = data.get("owner_name", "")
    vertical = data.get("vertical", "")

    missing = []
    if not data.get("estimated_revenue") and not data.get("revenue"): missing.append("revenue")
    if not data.get("employee_count") and not data.get("employees"): missing.append("employees")
    if not data.get("services") and not data.get("services_offered"): missing.append("services")
    if not data.get("owner_name"): missing.append("owner")
    if not data.get("year_founded") and not data.get("founded"): missing.append("founded")

    if not missing:
        log(f"  No Exa enrichment needed — data is complete")
        return data

    log(f"  Exa enrichment needed for: {missing}")

    queries = [
        f"{company} {city} {state} {vertical} company",
        f"{company} owner founder president {city}",
    ]
    if "revenue" in missing or "employees" in missing:
        queries.append(f"{company} {city} employees revenue size")

    exa_results = []
    for q in queries:
        results = exa_search(q, num_results=3)
        exa_results.extend(results)

    if exa_results:
        data["exa_research"] = [{"url": r.get("url", ""), "title": r.get("title", ""),
                                  "text": r.get("text", "")[:1000]} for r in exa_results]
        data["sources"].append("exa_search")

    return data

def get_market_multiples(vertical):
    """Load market multiples for this vertical."""
    if os.path.exists(MULTIPLES_FILE):
        with open(MULTIPLES_FILE) as f:
            multiples = json.load(f)
        for v in multiples.get("verticals", []):
            if vertical.lower() in v.get("vertical", "").lower():
                return v

    # Default multiples if file not ready yet
    defaults = {
        "hvac": {"ebitda_low": 3.5, "ebitda_med": 5.0, "ebitda_high": 7.0},
        "plumbing": {"ebitda_low": 3.0, "ebitda_med": 4.5, "ebitda_high": 6.5},
        "water treatment": {"ebitda_low": 4.0, "ebitda_med": 5.5, "ebitda_high": 8.0},
        "flooring": {"ebitda_low": 2.5, "ebitda_med": 4.0, "ebitda_high": 5.5},
        "concrete": {"ebitda_low": 3.0, "ebitda_med": 4.5, "ebitda_high": 6.0},
        "precast": {"ebitda_low": 3.5, "ebitda_med": 5.0, "ebitda_high": 7.0},
        "roofing": {"ebitda_low": 3.0, "ebitda_med": 4.5, "ebitda_high": 6.0},
        "pest": {"ebitda_low": 4.0, "ebitda_med": 6.0, "ebitda_high": 9.0},
    }
    for key, vals in defaults.items():
        if key in vertical.lower():
            return vals
    return {"ebitda_low": 3.0, "ebitda_med": 4.5, "ebitda_high": 6.5}

# ─── Proposal Generation ────────────────────────────────────────────────────

def generate_proposal(company_name):
    """Generate a complete proposal for a company."""
    log(f"\n{'='*60}")
    log(f"PROPOSAL: {company_name}")
    log(f"{'='*60}")

    # Step 1: Assemble data
    log("Step 1: Assembling data from master-crm...")
    data = get_company_data(company_name)
    log(f"  Data sources: {data.get('sources', [])}")

    # Step 2: Enrich gaps with Exa
    log("Step 2: Enriching gaps with Exa...")
    data = enrich_with_exa(data)

    # Step 3: Get market multiples
    vertical = data.get("vertical", "home services")
    log(f"Step 3: Loading market multiples for {vertical}...")
    multiples = get_market_multiples(vertical)
    data["market_multiples"] = multiples

    # Step 4: Check minimum data threshold
    has_name = bool(data.get("company_name"))
    has_owner = bool(data.get("owner_name"))
    has_city = bool(data.get("city"))
    has_metric = bool(data.get("estimated_revenue") or data.get("employee_count") or data.get("years_in_business") or data.get("year_founded"))

    quality_level = sum([has_name, has_owner, has_city, has_metric])
    log(f"  Data quality: {quality_level}/4 (name={has_name}, owner={has_owner}, city={has_city}, metric={has_metric})")

    if quality_level < 2:
        log(f"  INSUFFICIENT DATA — skipping per cascade rule A")
        return None

    # Step 5: Generate proposal content via Claude CLI
    log("Step 4: Generating proposal content...")

    # Build the mega-prompt
    data_json = json.dumps({k: str(v)[:500] if v else None for k, v in data.items()
                           if k not in ('exa_research', 'extra_fields', 'contacts') and v},
                          indent=2, default=str)

    exa_context = ""
    if data.get("exa_research"):
        exa_context = "\n\nADDITIONAL RESEARCH:\n" + "\n".join(
            f"Source: {r['url']}\n{r['text'][:500]}" for r in data["exa_research"][:5]
        )

    prompt = f"""You are generating a sell-side M&A proposal for Next Chapter Advisory.

COMPANY DATA:
{data_json}

MARKET MULTIPLES:
{json.dumps(multiples, indent=2, default=str)}
{exa_context}

FOUNDER GUARDRAILS (MUST FOLLOW):
- ALL ABOUT THEM, NOTHING ABOUT US
- When estimating, ALWAYS disclose methodology: "X employees × $Y/employee = estimated revenue"
- NO negative facts (divorce, lawsuits, closures, arrests)
- Use higher confidence data, disclose methodology for estimates
- Frame from THEIR perspective: "prevent leaks" not "replace roof"
- Education is king — teach them things they don't know about their own business value

Generate a complete JSON proposal with these sections:

{{
  "company_narrative": "3-4 paragraphs about their company story, strengths, market position. All about them.",
  "top_3_strengths": ["strength 1", "strength 2", "strength 3"],
  "market_analysis": "2-3 paragraphs about their vertical's M&A landscape, recent transactions, buyer activity",
  "valuation_range": {{
    "low": number,
    "mid": number,
    "high": number,
    "methodology": "How we calculated this — be transparent",
    "key_drivers": ["driver 1", "driver 2", "driver 3"]
  }},
  "buyer_profile": "Description of the ideal buyer type for this company",
  "attack_plan": "Complete outreach strategy: channels, timeline, approach for each buyer type",
  "outreach_strategy": "Specific multi-channel approach: letters, calls, LinkedIn, email sequence",
  "letter_template": "A personalized letter to a potential BUYER about this company. NOT to the owner. To the buyer. 'We represent the owners of [company]...' approach.",
  "call_script": "Cold call script for calling potential buyers about this acquisition opportunity",
  "linkedin_message": "LinkedIn connection request message to potential buyers",
  "timeline": "30/60/90 day execution timeline",
  "risk_factors": ["risk 1", "risk 2"],
  "differentiators": "Why Next Chapter vs other advisors — framed as what the OWNER gets",
  "quality_score": 0-100
}}

Return ONLY valid JSON. No markdown fences."""

    result = generate(prompt, f"proposal for {company_name}")

    if not result:
        log(f"  FAILED to generate proposal content")
        return None

    # Parse JSON
    try:
        # Try direct parse
        proposal_data = json.loads(result)
    except json.JSONDecodeError:
        # Try extracting JSON from text
        start = result.find('{')
        end = result.rfind('}') + 1
        if start >= 0 and end > start:
            try:
                proposal_data = json.loads(result[start:end])
            except:
                log(f"  FAILED to parse proposal JSON")
                proposal_data = {"raw_content": result, "quality_score": 0}
        else:
            proposal_data = {"raw_content": result, "quality_score": 0}

    # Step 6: Generate HTML
    log("Step 5: Generating polished HTML...")
    proposal_data["company_data"] = data
    html = generate_proposal_html(company_name, data, proposal_data)

    # Step 7: Store in Supabase
    log("Step 6: Storing proposal in Supabase...")
    proposal_id = store_proposal(company_name, data, proposal_data, html)

    quality = proposal_data.get("quality_score", 0)
    log(f"PROPOSAL COMPLETE: {company_name} | Quality: {quality} | ID: {proposal_id}")

    # Auto-refresh hub and dashboard
    try:
        from lib.auto_refresh import refresh_hub, refresh_dashboard
        refresh_hub(company_name)
        refresh_dashboard()
    except Exception as e:
        log(f"  Auto-refresh failed (non-blocking): {e}")

    return proposal_id

def generate_proposal_html(company_name, data, proposal):
    """Generate polished, print-ready HTML."""
    owner = data.get("owner_name", "the owner")
    city = data.get("city", "")
    state = data.get("state", "")
    vertical = data.get("vertical", "home services")

    narrative = proposal.get("company_narrative", "")
    strengths = proposal.get("top_3_strengths", [])
    market = proposal.get("market_analysis", "")
    valuation = proposal.get("valuation_range", {})
    attack = proposal.get("attack_plan", "")
    timeline = proposal.get("timeline", "")
    differentiators = proposal.get("differentiators", "")
    risks = proposal.get("risk_factors", [])

    val_low = valuation.get("low", "N/A")
    val_mid = valuation.get("mid", "N/A")
    val_high = valuation.get("high", "N/A")
    val_method = valuation.get("methodology", "")
    val_drivers = valuation.get("key_drivers", [])

    strengths_html = "".join(f"<li>{s}</li>" for s in strengths)
    drivers_html = "".join(f"<li>{d}</li>" for d in val_drivers)
    risks_html = "".join(f"<li>{r}</li>" for r in risks)

    def fmt_money(v):
        try:
            n = float(v)
            if n >= 1_000_000:
                return f"${n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"${n/1_000:.0f}K"
            return f"${n:,.0f}"
        except:
            return str(v)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} — Next Chapter Advisory</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Georgia', serif; color: #2c3e50; line-height: 1.7; max-width: 900px; margin: 0 auto; padding: 40px 30px; background: #fff; }}
  .header {{ border-bottom: 3px solid #1a5276; padding-bottom: 30px; margin-bottom: 40px; }}
  .header h1 {{ font-size: 28px; color: #1a5276; margin-bottom: 5px; }}
  .header .subtitle {{ font-size: 16px; color: #7f8c8d; font-style: italic; }}
  .header .logo-placeholder {{ float: right; width: 120px; height: 60px; border: 1px dashed #bdc3c7; text-align: center; line-height: 60px; color: #bdc3c7; font-size: 11px; }}
  .section {{ margin-bottom: 35px; }}
  .section h2 {{ font-size: 20px; color: #1a5276; border-bottom: 1px solid #d5dbdb; padding-bottom: 8px; margin-bottom: 15px; }}
  .section p {{ margin-bottom: 12px; text-align: justify; }}
  .strengths {{ background: #f8f9fa; padding: 20px 25px; border-left: 4px solid #27ae60; border-radius: 0 8px 8px 0; }}
  .strengths li {{ margin-bottom: 8px; font-weight: 500; }}
  .valuation-box {{ background: #1a5276; color: white; padding: 25px 30px; border-radius: 8px; text-align: center; margin: 20px 0; }}
  .valuation-box .range {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
  .valuation-box .method {{ font-size: 13px; opacity: 0.8; margin-top: 10px; }}
  .drivers {{ display: flex; gap: 15px; margin: 15px 0; }}
  .driver {{ flex: 1; background: #eaf2f8; padding: 12px; border-radius: 6px; text-align: center; font-size: 14px; }}
  .timeline-box {{ background: #fef9e7; padding: 20px 25px; border-left: 4px solid #f39c12; border-radius: 0 8px 8px 0; }}
  .risks {{ background: #fdedec; padding: 15px 20px; border-left: 4px solid #e74c3c; border-radius: 0 8px 8px 0; font-size: 14px; }}
  .footer {{ border-top: 2px solid #1a5276; padding-top: 20px; margin-top: 40px; font-size: 13px; color: #7f8c8d; text-align: center; }}
  .footer .cta {{ display: inline-block; background: #27ae60; color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; font-size: 16px; font-weight: bold; margin: 15px 0; }}
  .confidential {{ font-size: 11px; color: #bdc3c7; text-align: center; margin-top: 30px; }}
  @media print {{ body {{ padding: 20px; }} .footer .cta {{ border: 2px solid #27ae60; }} }}
</style>
</head>
<body>

<div class="header">
  <div class="logo-placeholder">[Company Logo]</div>
  <h1>{company_name}</h1>
  <div class="subtitle">Confidential Advisory Assessment — Prepared by Next Chapter M&A Advisory</div>
  <div class="subtitle">{city}, {state} — {vertical}</div>
</div>

<div class="section">
  <h2>Your Company Story</h2>
  <p>{narrative}</p>
</div>

<div class="section">
  <h2>Your Top 3 Strengths</h2>
  <div class="strengths">
    <ol>{strengths_html}</ol>
  </div>
</div>

<div class="section">
  <h2>Your Market Landscape</h2>
  <p>{market}</p>
</div>

<div class="section">
  <h2>Estimated Value Range</h2>
  <div class="valuation-box">
    <div style="font-size: 14px; opacity: 0.8;">Based on current market conditions</div>
    <div class="range">{fmt_money(val_low)} — {fmt_money(val_mid)} — {fmt_money(val_high)}</div>
    <div class="method">{val_method}</div>
  </div>
  <div class="drivers">
    {' '.join(f'<div class="driver">{d}</div>' for d in val_drivers[:3])}
  </div>
</div>

<div class="section">
  <h2>How We Would Sell Your Business</h2>
  <p>{attack}</p>
</div>

<div class="section">
  <h2>Execution Timeline</h2>
  <div class="timeline-box">
    <p>{timeline}</p>
  </div>
</div>

<div class="section">
  <h2>Why This Approach Works</h2>
  <p>{differentiators}</p>
</div>

{f'<div class="section"><h2>Considerations</h2><div class="risks"><ul>{risks_html}</ul></div></div>' if risks else ''}

<div class="footer">
  <p>Ready to explore your options?</p>
  <a href="#" class="cta">Let's Get Started</a>
  <p style="margin-top: 15px;">Next Chapter M&A Advisory<br>
  Mark DeChant, Managing Director<br>
  818-747-9668 | ewing@chapter.guide</p>
</div>

<div class="confidential">
  CONFIDENTIAL — Prepared exclusively for {owner} at {company_name}<br>
  Generated {time.strftime('%B %d, %Y')} — Next Chapter M&A Advisory
</div>

</body>
</html>"""

    return html

def store_proposal(company_name, data, proposal_data, html):
    """Store proposal in Supabase proposals table."""
    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cur = conn.cursor()

    valuation = proposal_data.get("valuation_range", {})

    cur.execute("""
        INSERT INTO proposals (
            target_id, company_id, entity, company_name, owner_name,
            vertical, city, state, estimated_revenue, employee_count,
            years_in_business, top_3_strengths,
            company_narrative, market_analysis, valuation_range,
            buyer_profile, attack_plan, outreach_strategy,
            letter_templates, call_scripts, linkedin_messages, timeline,
            fee_mode, proposal_html, proposal_json,
            status, quality_score
        ) VALUES (
            %(target_id)s, %(company_id)s, 'next_chapter', %(company_name)s, %(owner_name)s,
            %(vertical)s, %(city)s, %(state)s, %(estimated_revenue)s, %(employee_count)s,
            %(years_in_business)s, %(top_3_strengths)s,
            %(company_narrative)s, %(market_analysis)s, %(valuation_range)s,
            %(buyer_profile)s, %(attack_plan)s, %(outreach_strategy)s,
            %(letter_templates)s, %(call_scripts)s, %(linkedin_messages)s, %(timeline)s,
            'framework_only', %(proposal_html)s, %(proposal_json)s,
            'draft', %(quality_score)s
        ) RETURNING id
    """, {
        "target_id": data.get("target_id"),
        "company_id": data.get("id") if data.get("sources") and "companies_table" in data["sources"] else None,
        "company_name": company_name,
        "owner_name": data.get("owner_name"),
        "vertical": data.get("vertical"),
        "city": data.get("city"),
        "state": data.get("state"),
        "estimated_revenue": str(data.get("estimated_revenue", "")) or None,
        "employee_count": str(data.get("employee_count", "")) or None,
        "years_in_business": int(data["years_in_business"]) if data.get("years_in_business") and str(data["years_in_business"]).isdigit() else (int(data["year_founded"]) if data.get("year_founded") and str(data["year_founded"]).isdigit() else None),
        "top_3_strengths": proposal_data.get("top_3_strengths", []),
        "company_narrative": proposal_data.get("company_narrative"),
        "market_analysis": proposal_data.get("market_analysis"),
        "valuation_range": json.dumps(valuation, default=str),
        "buyer_profile": proposal_data.get("buyer_profile"),
        "attack_plan": proposal_data.get("attack_plan"),
        "outreach_strategy": proposal_data.get("outreach_strategy"),
        "letter_templates": json.dumps({"buyer_letter": proposal_data.get("letter_template")}, default=str),
        "call_scripts": json.dumps({"buyer_call": proposal_data.get("call_script")}, default=str),
        "linkedin_messages": json.dumps({"buyer_connect": proposal_data.get("linkedin_message")}, default=str),
        "timeline": proposal_data.get("timeline"),
        "proposal_html": html,
        "proposal_json": json.dumps(proposal_data, default=str),
        "quality_score": proposal_data.get("quality_score", 0),
    })

    proposal_id = cur.fetchone()[0]

    # Also save HTML to file
    html_dir = os.path.expanduser("~/Projects/master-crm/data/proposals")
    os.makedirs(html_dir, exist_ok=True)
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "")[:30]
    with open(f"{html_dir}/{slug}.html", "w") as f:
        f.write(html)
    log(f"  HTML saved: data/proposals/{slug}.html")

    conn.close()
    return str(proposal_id)


# ─── Main ────────────────────────────────────────────────────────────────────

def run_all_deals():
    """Process all 6 live deals."""
    deals = [
        "AquaScience",
        "HR.com",
        "Springer Floor",
        "Air Control",
        "Weiser Concrete",
        "Design Precast",
    ]

    log(f"\n{'='*60}")
    log(f"PROPOSAL ENGINE — Processing {len(deals)} deals")
    log(f"{'='*60}")

    results = {}
    for deal in deals:
        try:
            proposal_id = generate_proposal(deal)
            results[deal] = {"status": "success", "id": proposal_id}
        except Exception as e:
            log(f"ERROR on {deal}: {e}")
            results[deal] = {"status": "error", "error": str(e)}

        # Cost check
        if total_cost > 1.0:
            log(f"COST ALERT: ${total_cost:.2f} spent — investigating")

    log(f"\n{'='*60}")
    log(f"RESULTS:")
    for deal, result in results.items():
        log(f"  {deal}: {result['status']}")
    log(f"Total cost: ${total_cost:.4f}")
    log(f"{'='*60}")

    return results


if __name__ == "__main__":
    run_all_deals()
