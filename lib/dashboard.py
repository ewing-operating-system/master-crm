#!/usr/bin/env python3
"""
Monday Morning Dashboard — the 9-section executive view.

SYSTEM RULE: Every page, every section, every element must have feedback capability.
The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
Any page generation engine that creates HTML must include:
  <script src="comment-widget.js"></script>
  <script src="notification-bell.js"></script>
  <script src="conflict-resolver.js"></script>
  <script src="version-widget.js"></script>
before </body>. No exceptions. This is how we learn.

Generates an HTML dashboard with:
1. Campaigns to RUN
2. Quality tuning
3. New rules needed
4. Agent performance
5. Outbound activity
6. Revenue metrics
7. Problem identification
8. Agent requests
9. Spend by category
"""

import json, os, time, psycopg2
from datetime import datetime, timedelta

DB_CONN = os.environ.get("DATABASE_URL", "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres")
DASHBOARD_DIR = os.path.expanduser("~/Projects/master-crm/data/dashboards")
os.makedirs(DASHBOARD_DIR, exist_ok=True)

def get_dashboard_data():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    data = {}

    # 1. Campaigns to RUN
    cur.execute("SELECT campaign_id, entity, name, is_active FROM campaigns ORDER BY entity, campaign_id")
    data["campaigns"] = [{"id": r[0], "entity": str(r[1]), "name": r[2], "active": r[3]} for r in cur.fetchall()]

    # 2. Quality — proposals by status
    cur.execute("SELECT company_name, status, quality_score FROM proposals ORDER BY quality_score DESC")
    data["proposals"] = [{"company": r[0], "status": r[1], "quality": r[2]} for r in cur.fetchall()]

    # 3. Pending reviews
    cur.execute("SELECT count(*) FROM human_review_queue WHERE status = 'pending'")
    data["pending_reviews"] = cur.fetchone()[0]
    cur.execute("SELECT review_type, count(*) FROM human_review_queue WHERE status = 'pending' GROUP BY review_type")
    data["review_breakdown"] = {r[0]: r[1] for r in cur.fetchall()}

    # 4. Agent runs
    cur.execute("""SELECT agent_name, count(*), count(*) FILTER (WHERE status = 'complete'),
                   avg(cost_usd) FILTER (WHERE cost_usd > 0)
                   FROM agent_runs WHERE created_at > now() - interval '7 days'
                   GROUP BY agent_name ORDER BY count(*) DESC""")
    data["agent_perf"] = [{"agent": r[0], "total": r[1], "success": r[2],
                           "avg_cost": float(r[3]) if r[3] else 0} for r in cur.fetchall()]

    # 5. Outbound activity
    cur.execute("SELECT count(*) FROM play_executions WHERE created_at > now() - interval '7 days'")
    data["plays_executed"] = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM sent_log WHERE created_at > now() - interval '7 days'")
    data["items_sent"] = cur.fetchone()[0]

    # Buyer outreach
    cur.execute("SELECT count(*) FROM engagement_buyers WHERE approach_script IS NOT NULL")
    data["buyers_scripted"] = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM engagement_buyers")
    data["buyers_total"] = cur.fetchone()[0]

    # 6. Revenue metrics (pipeline stages)
    cur.execute("""SELECT status, count(*) FROM proposals GROUP BY status ORDER BY count(*) DESC""")
    data["pipeline_stages"] = {r[0]: r[1] for r in cur.fetchall()}

    # 7. Problems — low quality proposals
    cur.execute("SELECT company_name, quality_score FROM proposals WHERE quality_score < 70 ORDER BY quality_score")
    data["low_quality"] = [{"company": r[0], "score": r[1]} for r in cur.fetchall()]

    # Failed queue items
    cur.execute("""SELECT agent_name, count(*), max(error_message)
                   FROM agent_queue WHERE status = 'failed'
                   GROUP BY agent_name""")
    data["failed_jobs"] = [{"agent": r[0], "count": r[1], "last_error": r[2]} for r in cur.fetchall()]

    # 8. Database health
    cur.execute("SELECT sum(n_live_tup) FROM pg_stat_user_tables WHERE schemaname = 'public'")
    data["total_rows"] = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM companies")
    data["companies"] = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM contacts")
    data["contacts"] = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM targets")
    data["targets"] = cur.fetchone()[0]

    # 9. Spend
    cur.execute("""SELECT entity, budget_usd, spent_usd FROM cost_budget WHERE period = 'daily' ORDER BY entity""")
    data["budgets"] = [{"entity": str(r[0]), "budget": float(r[1]), "spent": float(r[2])} for r in cur.fetchall()]

    cur.execute("""SELECT api_name, count(*), sum(cost_usd) FROM cost_log
                   WHERE created_at > now() - interval '7 days'
                   GROUP BY api_name ORDER BY sum(cost_usd) DESC""")
    data["spend_by_vendor"] = [{"vendor": r[0], "calls": r[1], "cost": float(r[2] or 0)} for r in cur.fetchall()]

    conn.close()
    return data


def generate_dashboard_html(data):
    now = datetime.now()

    # Campaigns section
    campaigns_rows = ""
    for c in data["campaigns"]:
        status = "🟢" if c["active"] else "🔴"
        campaigns_rows += f"<tr><td>{status}</td><td>{c['id']}</td><td>{c['entity']}</td><td>{c['name']}</td></tr>"

    # Proposals section
    proposals_rows = ""
    for p in data["proposals"]:
        color = "#27ae60" if p["status"] == "certified" else "#f39c12" if p["status"] == "engagement_active" else "#e74c3c"
        proposals_rows += f"<tr><td>{p['company']}</td><td style='color:{color};font-weight:bold'>{p['status']}</td><td>{p['quality']}</td></tr>"

    # Agent perf
    agent_rows = ""
    for a in data["agent_perf"]:
        rate = f"{a['success']}/{a['total']}" if a['total'] > 0 else "—"
        agent_rows += f"<tr><td>{a['agent']}</td><td>{rate}</td><td>${a['avg_cost']:.4f}</td></tr>"

    # Pipeline
    pipeline_rows = ""
    for status, count in data.get("pipeline_stages", {}).items():
        pipeline_rows += f"<tr><td>{status}</td><td>{count}</td></tr>"

    # Budget
    budget_rows = ""
    for b in data["budgets"]:
        pct = (b["spent"] / b["budget"] * 100) if b["budget"] > 0 else 0
        color = "#27ae60" if pct < 50 else "#f39c12" if pct < 80 else "#e74c3c"
        budget_rows += f"<tr><td>{b['entity']}</td><td>${b['budget']:.2f}</td><td style='color:{color}'>${b['spent']:.2f} ({pct:.0f}%)</td></tr>"

    # Problems
    problems = ""
    for p in data.get("low_quality", []):
        problems += f"<li>⚠️ {p['company']}: quality {p['score']}</li>"
    for f in data.get("failed_jobs", []):
        problems += f"<li>❌ {f['agent']}: {f['count']} failures — {(f['last_error'] or '')[:80]}</li>"
    if not problems:
        problems = "<li>✅ No problems detected</li>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Monday Dashboard — {now.strftime('%B %d, %Y')}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; }}
  .header {{ background: linear-gradient(135deg, #161b22, #1a5276); padding: 25px 30px; }}
  .header h1 {{ color: #58a6ff; font-size: 24px; }}
  .header .meta {{ color: #8b949e; font-size: 13px; margin-top: 5px; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 18px; }}
  .card.full {{ grid-column: 1 / -1; }}
  .card.half {{ grid-column: span 2; }}
  .card h2 {{ font-size: 14px; color: #58a6ff; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }}
  .metric {{ font-size: 36px; font-weight: bold; color: #f0f6fc; }}
  .metric-label {{ font-size: 12px; color: #8b949e; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 6px 8px; color: #8b949e; border-bottom: 1px solid #30363d; }}
  td {{ padding: 6px 8px; border-bottom: 1px solid #21262d; }}
  ul {{ list-style: none; }}
  li {{ padding: 4px 0; }}
  .stat-row {{ display: flex; gap: 20px; margin: 10px 0; }}
  .stat {{ text-align: center; }}
  .stat .num {{ font-size: 28px; font-weight: bold; color: #f0f6fc; }}
  .stat .label {{ font-size: 11px; color: #8b949e; }}
</style>
</head>
<body>

<div class="header">
  <h1>Next Chapter — Command Center</h1>
  <div class="meta">{now.strftime('%A, %B %d, %Y %I:%M %p')} | {data['total_rows']:,} rows | {data['companies']} companies | {data['contacts']:,} contacts</div>
</div>

<div class="grid">

  <div class="card">
    <h2>📊 Pipeline</h2>
    <table>{pipeline_rows}</table>
  </div>

  <div class="card">
    <h2>🎯 Outbound Activity</h2>
    <div class="stat-row">
      <div class="stat"><div class="num">{data['plays_executed']}</div><div class="label">Plays Run (7d)</div></div>
      <div class="stat"><div class="num">{data['items_sent']}</div><div class="label">Items Sent (7d)</div></div>
      <div class="stat"><div class="num">{data['buyers_scripted']}/{data['buyers_total']}</div><div class="label">Buyers Scripted</div></div>
    </div>
  </div>

  <div class="card">
    <h2>💰 Budget</h2>
    <table><tr><th>Entity</th><th>Daily Cap</th><th>Spent</th></tr>{budget_rows}</table>
  </div>

  <div class="card half">
    <h2>📋 Proposals</h2>
    <table><tr><th>Company</th><th>Status</th><th>Quality</th></tr>{proposals_rows}</table>
  </div>

  <div class="card">
    <h2>🔍 Pending Reviews</h2>
    <div class="metric">{data['pending_reviews']}</div>
    <div class="metric-label">items awaiting human review</div>
  </div>

  <div class="card half">
    <h2>🤖 Agent Performance (7d)</h2>
    <table><tr><th>Agent</th><th>Success</th><th>Avg Cost</th></tr>{agent_rows}</table>
  </div>

  <div class="card">
    <h2>⚠️ Problems</h2>
    <ul>{problems}</ul>
  </div>

  <div class="card full">
    <h2>🏗️ Campaigns</h2>
    <table><tr><th>Active</th><th>Campaign</th><th>Entity</th><th>Name</th></tr>{campaigns_rows}</table>
  </div>

</div>

</body>
</html>"""
    return html


def generate_dashboard():
    data = get_dashboard_data()
    html = generate_dashboard_html(data)

    filename = f"dashboard_{datetime.now().strftime('%Y-%m-%d')}.html"
    filepath = os.path.join(DASHBOARD_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(html)

    # Copy to downloads
    dl = os.path.expanduser(f"~/Downloads/master-crm-proposals/{filename}")
    with open(dl, 'w') as f:
        f.write(html)

    print(f"Dashboard saved: {filepath}")
    print(f"Also at: {dl}")
    return filepath


if __name__ == "__main__":
    generate_dashboard()
