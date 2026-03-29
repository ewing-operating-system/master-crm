#!/usr/bin/env python3
"""Buyer 1-Pager Pipeline: Query buyers, generate dossiers, save HTML, update DB."""

import psycopg2
import psycopg2.extras
import json
import subprocess
import os
import re
import sys
import datetime
import traceback
import time
import requests

# --- Config ---
DB_URL = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"
OUTPUT_DIR = os.path.expanduser("~/Projects/master-crm/data/buyer-1pagers")
COPY_DIR = os.path.expanduser("~/Downloads/master-crm-proposals")
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/buyer_1pagers.log")
OPENROUTER_KEY = "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"
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(COPY_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def slugify(s):
    if not s:
        return "unknown"
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:60]

def call_claude_cli(prompt):
    """Try Claude CLI first."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            log(f"  Claude CLI failed (rc={result.returncode}): {result.stderr[:200]}")
            return None
    except Exception as e:
        log(f"  Claude CLI exception: {e}")
        return None

def call_openrouter(prompt):
    """Fallback to OpenRouter DeepSeek."""
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=90
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"  OpenRouter fallback failed: {e}")
        return None

def generate_json(prompt):
    """Generate via Claude CLI, fallback to OpenRouter. Extract JSON from response."""
    raw = call_claude_cli(prompt)
    if not raw:
        log("  Falling back to OpenRouter DeepSeek...")
        raw = call_openrouter(prompt)
    if not raw:
        return None
    # Extract JSON from response (may be wrapped in markdown code block)
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            log(f"  JSON parse failed, attempting repair...")
            # Try to fix common issues
            text = json_match.group()
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            try:
                return json.loads(text)
            except:
                log(f"  JSON repair failed")
                return None
    return None

def generate_html(buyer_data, one_pager_json, seller_name):
    """Generate polished HTML dossier."""
    buyer_name = buyer_data.get('buyer_company_name', 'Unknown Buyer')
    contact = buyer_data.get('buyer_contact_name', '')
    buyer_type = buyer_data.get('buyer_type', '')
    buyer_city = buyer_data.get('buyer_city', '')
    buyer_state = buyer_data.get('buyer_state', '')
    fit_score = buyer_data.get('fit_score', '')
    location = f"{buyer_city}, {buyer_state}" if buyer_city and buyer_state else (buyer_city or buyer_state or '')

    narrative = one_pager_json.get('buyer_narrative', '')
    acq_history = one_pager_json.get('acquisition_history', [])
    why_seller = one_pager_json.get('why_this_seller', '')
    approach = one_pager_json.get('approach_angle', '')
    talking_points = one_pager_json.get('talking_points', [])
    risk_factors = one_pager_json.get('risk_factors', [])
    one_line = one_pager_json.get('one_line_pitch', '')

    acq_html = ""
    if acq_history:
        acq_items = "".join(f"<li>{a}</li>" for a in acq_history)
        acq_html = f"""
        <div class="section">
            <h2>Acquisition History</h2>
            <ul>{acq_items}</ul>
        </div>"""

    tp_html = ""
    if talking_points:
        tp_items = "".join(f"<li>{t}</li>" for t in talking_points)
        tp_html = f"""
        <div class="section">
            <h2>Talking Points</h2>
            <ul>{tp_items}</ul>
        </div>"""

    risk_html = ""
    if risk_factors:
        risk_items = "".join(f"<li>{r}</li>" for r in risk_factors)
        risk_html = f"""
        <div class="section">
            <h2>Risk Factors</h2>
            <ul class="risks">{risk_items}</ul>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Dossier: {buyer_name} for {seller_name}</title>
<style>
    @media print {{
        body {{ margin: 0; }}
        .page-break {{ page-break-before: always; }}
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Georgia', 'Times New Roman', serif;
        color: #2c2c2c;
        background: #f8f8f8;
        line-height: 1.6;
    }}
    .container {{
        max-width: 800px;
        margin: 0 auto;
        background: white;
        box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    }}
    .header {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 40px;
        position: relative;
    }}
    .header::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #e94560, #f5a623, #e94560);
    }}
    .header h1 {{
        font-size: 28px;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }}
    .header .subtitle {{
        font-size: 16px;
        opacity: 0.85;
        font-style: italic;
    }}
    .meta-bar {{
        display: flex;
        gap: 24px;
        padding: 16px 40px;
        background: #f0f0f0;
        border-bottom: 1px solid #ddd;
        font-size: 14px;
        flex-wrap: wrap;
    }}
    .meta-bar .meta-item {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .meta-bar .label {{
        font-weight: bold;
        color: #666;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
    }}
    .meta-bar .value {{
        color: #1a1a2e;
        font-weight: 600;
    }}
    .fit-score {{
        display: inline-block;
        background: {('#27ae60' if str(fit_score).isdigit() and int(fit_score) >= 80 else '#f5a623' if str(fit_score).isdigit() and int(fit_score) >= 60 else '#e74c3c')};
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 13px;
    }}
    .pitch-bar {{
        padding: 20px 40px;
        background: #fafbfc;
        border-bottom: 2px solid #e94560;
        font-size: 18px;
        font-style: italic;
        color: #333;
        text-align: center;
    }}
    .content {{
        padding: 32px 40px;
    }}
    .section {{
        margin-bottom: 28px;
    }}
    .section h2 {{
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #0f3460;
        border-bottom: 2px solid #e8e8e8;
        padding-bottom: 8px;
        margin-bottom: 14px;
    }}
    .section p {{
        margin-bottom: 12px;
        text-align: justify;
    }}
    .section ul {{
        padding-left: 20px;
    }}
    .section ul li {{
        margin-bottom: 8px;
    }}
    .section ul.risks li {{
        color: #c0392b;
    }}
    .approach-box {{
        background: #f0f7ff;
        border-left: 4px solid #0f3460;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-top: 12px;
    }}
    .footer {{
        padding: 20px 40px;
        background: #1a1a2e;
        color: rgba(255,255,255,0.5);
        font-size: 11px;
        text-align: center;
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>{buyer_name}</h1>
        <div class="subtitle">Buyer Dossier &mdash; Prepared for {seller_name}</div>
    </div>
    <div class="meta-bar">
        {"<div class='meta-item'><span class='label'>Contact</span><span class='value'>" + contact + "</span></div>" if contact else ""}
        {"<div class='meta-item'><span class='label'>Type</span><span class='value'>" + buyer_type + "</span></div>" if buyer_type else ""}
        {"<div class='meta-item'><span class='label'>Location</span><span class='value'>" + location + "</span></div>" if location else ""}
        {"<div class='meta-item'><span class='label'>Fit Score</span><span class='fit-score'>" + str(fit_score) + "</span></div>" if fit_score else ""}
    </div>
    {"<div class='pitch-bar'>&ldquo;" + one_line + "&rdquo;</div>" if one_line else ""}
    <div class="content">
        <div class="section">
            <h2>Buyer Narrative</h2>
            {"".join(f"<p>{p.strip()}</p>" for p in narrative.split(chr(10)+chr(10)) if p.strip()) if narrative else "<p>No narrative available.</p>"}
        </div>
        {acq_html}
        <div class="section">
            <h2>Why This Seller</h2>
            <p>{why_seller or 'Analysis pending.'}</p>
        </div>
        <div class="section">
            <h2>Approach Angle</h2>
            <div class="approach-box">{approach or 'Strategy pending.'}</div>
        </div>
        {tp_html}
        {risk_html}
    </div>
    <div class="footer">
        Generated {datetime.datetime.now().strftime('%B %d, %Y')} &bull; Confidential
    </div>
</div>
</body>
</html>"""
    return html

def main():
    log("=" * 60)
    log("BUYER 1-PAGER PIPELINE START")
    log("=" * 60)

    # Step 1: Connect and query
    log("Step 1: Connecting to Supabase (port 6543)...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        log("  Connected successfully")
    except Exception as e:
        log(f"  FATAL: DB connection failed: {e}")
        sys.exit(1)

    # Step 6 (early): Add columns if not exist
    log("Step 6 (early): Adding columns if not exist...")
    try:
        alter_conn = psycopg2.connect(DB_URL)
        alter_conn.autocommit = True
        alter_cur = alter_conn.cursor()
        alter_cur.execute("ALTER TABLE engagement_buyers ADD COLUMN IF NOT EXISTS one_pager_html TEXT;")
        alter_cur.execute("ALTER TABLE engagement_buyers ADD COLUMN IF NOT EXISTS one_pager_json JSONB;")
        alter_cur.close()
        alter_conn.close()
        log("  Columns ensured")
    except Exception as e:
        log(f"  Column alter warning: {e}")

    log("  Querying buyers with seller info...")
    cur.execute("""SELECT eb.id, eb.buyer_company_name, eb.buyer_contact_name, eb.buyer_type,
                          eb.buyer_city, eb.buyer_state, eb.fit_score, eb.fit_narrative,
                          eb.approach_strategy, eb.approach_script,
                          p.company_name as seller, p.owner_name as seller_owner,
                          p.vertical as seller_vertical, p.city as seller_city, p.state as seller_state,
                          p.estimated_revenue as seller_revenue
                   FROM engagement_buyers eb
                   JOIN proposals p ON eb.proposal_id = p.id
                   ORDER BY p.company_name, eb.fit_score DESC NULLS LAST""")
    rows = cur.fetchall()
    log(f"  Fetched {len(rows)} buyer-seller pairs")

    if not rows:
        log("  No buyers found. Exiting.")
        cur.close()
        conn.close()
        return

    # Step 2: Group by seller, top 3 per seller
    from collections import OrderedDict
    grouped = OrderedDict()
    for row in rows:
        seller = row['seller']
        if seller not in grouped:
            grouped[seller] = []
        if len(grouped[seller]) < 3:
            grouped[seller].append(row)

    total_pairs = sum(len(v) for v in grouped.values())
    log(f"Step 2: {len(grouped)} sellers, {total_pairs} buyer-seller pairs (top 3 per seller)")

    # Steps 3-5: Generate 1-pagers
    success_count = 0
    fail_count = 0

    for seller_name, buyers in grouped.items():
        log(f"\n--- Seller: {seller_name} ({len(buyers)} buyers) ---")
        for buyer in buyers:
            buyer_name = buyer['buyer_company_name'] or 'Unknown'
            log(f"  Processing: {buyer_name} (fit_score={buyer.get('fit_score')})")

            # Build prompt
            prompt = f"""You are a mergers & acquisitions research analyst. Generate a buyer dossier 1-pager.

BUYER: {buyer_name}
BUYER CONTACT: {buyer.get('buyer_contact_name', 'N/A')}
BUYER TYPE: {buyer.get('buyer_type', 'N/A')}
BUYER LOCATION: {buyer.get('buyer_city', '')}, {buyer.get('buyer_state', '')}
FIT SCORE: {buyer.get('fit_score', 'N/A')}
FIT NARRATIVE: {buyer.get('fit_narrative', 'N/A')}
APPROACH STRATEGY: {buyer.get('approach_strategy', 'N/A')}
APPROACH SCRIPT: {buyer.get('approach_script', 'N/A')}

SELLER: {seller_name}
SELLER OWNER: {buyer.get('seller_owner', 'N/A')}
SELLER VERTICAL: {buyer.get('seller_vertical', 'N/A')}
SELLER LOCATION: {buyer.get('seller_city', '')}, {buyer.get('seller_state', '')}
SELLER ESTIMATED REVENUE: {buyer.get('seller_revenue', 'N/A')}

Based on the above, generate a JSON object with these exact keys:
- "buyer_narrative": 2-3 paragraphs about who this buyer is, their background, investment thesis, and what makes them a credible acquirer. Write as if for a seller evaluating potential buyers. These are former business owners who cashed out and buy companies because they believe in owners, not the stock market.
- "acquisition_history": array of strings, each a known or likely past acquisition or investment (if buyer type suggests they acquire companies, infer likely patterns)
- "why_this_seller": paragraph explaining why this specific seller is a fit for this buyer
- "approach_angle": the recommended angle for initial outreach
- "talking_points": array of 3-5 specific talking points for the first conversation
- "risk_factors": array of 2-3 risks or concerns to watch for
- "one_line_pitch": a single compelling sentence pitch for why this buyer should look at this seller

Return ONLY valid JSON, no markdown formatting, no extra text."""

            # Step 3: Generate JSON via LLM
            one_pager_json = generate_json(prompt)
            if not one_pager_json:
                log(f"    FAILED to generate JSON for {buyer_name}")
                fail_count += 1
                continue

            log(f"    JSON generated successfully")

            # Step 4: Generate HTML
            html = generate_html(buyer, one_pager_json, seller_name)

            # Step 5: Save files
            seller_slug = slugify(seller_name)
            buyer_slug = slugify(buyer_name)
            filename = f"{seller_slug}_{buyer_slug}.html"

            output_path = os.path.join(OUTPUT_DIR, filename)
            copy_path = os.path.join(COPY_DIR, filename)

            with open(output_path, 'w') as f:
                f.write(html)
            with open(copy_path, 'w') as f:
                f.write(html)
            log(f"    Saved: {filename}")

            # Step 6: Update DB
            try:
                cur.execute(
                    "UPDATE engagement_buyers SET one_pager_html = %s, one_pager_json = %s WHERE id = %s",
                    (html, json.dumps(one_pager_json), buyer['id'])
                )
                conn.commit()
                log(f"    DB updated for buyer id={buyer['id']}")
            except Exception as e:
                conn.rollback()
                log(f"    DB update failed: {e}")

            success_count += 1

    cur.close()
    conn.close()

    log(f"\n{'=' * 60}")
    log(f"PIPELINE COMPLETE: {success_count} success, {fail_count} failed, {total_pairs} total")
    log(f"Output: {OUTPUT_DIR}")
    log(f"Copies: {COPY_DIR}")
    log(f"{'=' * 60}")

if __name__ == "__main__":
    main()
