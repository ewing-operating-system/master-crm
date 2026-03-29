#!/usr/bin/env python3
"""
Slack Message Generator — creates ready-to-send Slack messages for Mark.

Generates formatted messages with links to company hubs, proposals, meeting pages.
Can be called after any engine produces output.

When a tunnel (ngrok/tailscale) is configured, uses the public URL.
Until then, uses localhost (only works on local network).
"""

import json, os, psycopg2
from datetime import datetime

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
BASE_URL = os.environ.get("MASTER_CRM_URL", "http://localhost:8080")


def generate_company_update(company_name):
    """Generate a Slack message summarizing everything we have for a company."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("""SELECT p.company_name, p.owner_name, p.vertical, p.city, p.state,
                          p.status, p.quality_score,
                          (SELECT count(*) FROM engagement_buyers eb WHERE eb.proposal_id = p.id) as buyers,
                          (SELECT count(*) FROM engagement_buyers eb WHERE eb.proposal_id = p.id AND eb.approach_script IS NOT NULL) as scripted
                   FROM proposals p WHERE p.company_name ILIKE %s LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    conn.close()

    if not row:
        return f"No proposal found for {company_name}"

    name, owner, vertical, city, state, status, quality, buyers, scripted = row
    slug = name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]

    msg = f"""*{name}* — {status.upper()}
_{owner} | {vertical} | {city}, {state}_
Quality: *{quality}/100* | Buyers: *{scripted}/{buyers}* scripted

:page_facing_up: <{BASE_URL}/company/{slug}|Company Hub> — everything in one page
:bar_chart: <{BASE_URL}/proposal/{slug}|Proposal> — attack plan + valuations
:lock: <{BASE_URL}/dataroom/{slug}|Data Room> — email-gated client page
:clipboard: <{BASE_URL}/meeting/{slug}|Meeting Prep> — agenda + talking points
:chart_with_upwards_trend: <{BASE_URL}/dashboard|Dashboard> — full pipeline view"""

    return msg


def generate_daily_briefing():
    """Generate a Slack daily briefing with all active deals."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("""SELECT company_name, status, quality_score FROM proposals ORDER BY quality_score DESC""")
    proposals = cur.fetchall()

    cur.execute("SELECT count(*) FROM engagement_buyers WHERE approach_script IS NOT NULL")
    total_scripted = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM human_review_queue WHERE status = 'pending'")
    pending_reviews = cur.fetchone()[0]

    conn.close()

    lines = [f"*Daily Briefing — {datetime.now().strftime('%A, %B %d')}*\n"]

    for name, status, quality in proposals:
        emoji = "🟢" if status == "engagement_active" else "🟡" if status == "certified" else "🔵"
        slug = name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
        lines.append(f"{emoji} <{BASE_URL}/company/{slug}|{name}> — {status} (Q:{quality})")

    lines.append(f"\n📊 *{total_scripted} buyer scripts ready* | ⏳ *{pending_reviews} items need review*")
    lines.append(f"\n<{BASE_URL}/dashboard|Open Dashboard>")

    return "\n".join(lines)


def generate_all_messages():
    """Print all Slack messages — copy-paste ready."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company_name FROM proposals ORDER BY company_name")
    companies = [r[0] for r in cur.fetchall()]
    conn.close()

    print("=" * 60)
    print("DAILY BRIEFING (paste to #ops channel)")
    print("=" * 60)
    print(generate_daily_briefing())

    for company in companies:
        print(f"\n{'=' * 60}")
        print(f"COMPANY UPDATE: {company} (paste to Slack DM)")
        print("=" * 60)
        print(generate_company_update(company))


if __name__ == "__main__":
    generate_all_messages()
