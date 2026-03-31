#!/usr/bin/env python3
"""Fix: Re-generate 1-pager JSON for buyers missing it (Design Precast & Wieser top 3 each)."""

import psycopg2
import psycopg2.extras
import json
import subprocess
import os
import re
import sys
import datetime
import requests

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres")
OUTPUT_DIR = os.path.expanduser("~/Projects/master-crm/data/buyer-1pagers")
COPY_DIR = os.path.expanduser("~/Downloads/master-crm-proposals")
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/buyer_1pagers.log")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324"

def log(msg):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def slugify(s):
    if not s: return "unknown"
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:60]

def call_openrouter(prompt):
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json={"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2000},
            timeout=90
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"  OpenRouter failed: {e}")
        return None

def generate_json(prompt):
    raw = call_openrouter(prompt)
    if not raw: return None
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            text = json_match.group()
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            try: return json.loads(text)
            except: return None
    return None

def generate_html(buyer_data, one_pager_json, seller_name):
    # Import from main script
    sys.path.insert(0, os.path.dirname(__file__))
    from buyer_1pager_pipeline import generate_html as gen_html
    return gen_html(buyer_data, one_pager_json, seller_name)

def main():
    log("FIX RUN: Updating Design Precast & Wieser Concrete buyers")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get top 3 per seller for the two missing sellers
    for seller_name in ['Design Precast & Pipe, Inc.', 'Wieser Concrete Products, Inc.']:
        cur.execute("""SELECT eb.id, eb.buyer_company_name, eb.buyer_contact_name, eb.buyer_type,
                              eb.buyer_city, eb.buyer_state, eb.fit_score, eb.fit_narrative,
                              eb.approach_strategy, eb.approach_script,
                              p.company_name as seller, p.owner_name as seller_owner,
                              p.vertical as seller_vertical, p.city as seller_city, p.state as seller_state,
                              p.estimated_revenue as seller_revenue
                       FROM engagement_buyers eb
                       JOIN proposals p ON eb.proposal_id = p.id
                       WHERE p.company_name = %s
                       ORDER BY eb.fit_score DESC NULLS LAST
                       LIMIT 3""", (seller_name,))
        buyers = cur.fetchall()
        log(f"\n--- {seller_name}: {len(buyers)} buyers ---")

        for buyer in buyers:
            buyer_name = buyer['buyer_company_name'] or 'Unknown'
            log(f"  Processing: {buyer_name} (fit={buyer.get('fit_score')})")

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

Generate JSON with these exact keys:
- "buyer_narrative": 2-3 paragraphs about who this buyer is, their background, investment thesis, and what makes them a credible acquirer. These are former business owners who cashed out and buy companies because they believe in owners, not the stock market.
- "acquisition_history": array of strings, each a known or likely past acquisition
- "why_this_seller": paragraph explaining why this specific seller is a fit
- "approach_angle": the recommended angle for initial outreach
- "talking_points": array of 3-5 specific talking points
- "risk_factors": array of 2-3 risks
- "one_line_pitch": a single compelling sentence pitch

Return ONLY valid JSON, no markdown, no extra text."""

            one_pager_json = generate_json(prompt)
            if not one_pager_json:
                log(f"    FAILED for {buyer_name}")
                continue

            html = generate_html(dict(buyer), one_pager_json, seller_name)

            seller_slug = slugify(seller_name)
            buyer_slug = slugify(buyer_name)
            filename = f"{seller_slug}_{buyer_slug}.html"

            for d in [OUTPUT_DIR, COPY_DIR]:
                with open(os.path.join(d, filename), 'w') as f:
                    f.write(html)
            log(f"    Saved: {filename}")

            try:
                cur.execute("UPDATE engagement_buyers SET one_pager_html = %s, one_pager_json = %s WHERE id = %s",
                            (html, json.dumps(one_pager_json), buyer['id']))
                conn.commit()
                log(f"    DB updated for id={buyer['id']}")
            except Exception as e:
                conn.rollback()
                log(f"    DB update failed: {e}")

    cur.close()
    conn.close()
    log("FIX RUN COMPLETE")

if __name__ == "__main__":
    main()
