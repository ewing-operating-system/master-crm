#!/usr/bin/env python3
"""
Company Hub — single page per company linking every asset we've ever created.

One URL, one company, everything: proposal, data room, meeting pages, buyer list,
profile, emails, call scripts, timeline, intelligence, costs.

Admin view shows everything. Client view shows curated subset.
"""

import json, os, sys, time, psycopg2
from datetime import datetime

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"
HUB_DIR = os.path.expanduser("~/Projects/master-crm/data/company-hubs")
DL_DIR = os.path.expanduser("~/Downloads/master-crm-proposals")
os.makedirs(HUB_DIR, exist_ok=True)

def log(msg):
    print(f"{datetime.utcnow().isoformat()} | HUB | {msg}", flush=True)


def get_all_company_assets(company_name):
    """Pull every asset we have for a company from every table."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    assets = {"company_name": company_name}

    # Company record
    cur.execute("SELECT * FROM companies WHERE company_name ILIKE %s LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        company = dict(zip(cols, row))
        assets["company"] = {k: v for k, v in company.items() if v is not None and str(v).strip()}
        assets["company_id"] = str(company.get("id", ""))

    # Contacts
    if assets.get("company_id"):
        cur.execute("SELECT full_name, title, email, phone, cell_phone, linkedin_url FROM contacts WHERE company_id = %s", (assets["company_id"],))
        assets["contacts"] = [{"name": r[0], "title": r[1], "email": r[2], "phone": r[3], "cell": r[4], "linkedin": r[5]} for r in cur.fetchall()]

    # Proposal
    cur.execute("""SELECT id, company_name, owner_name, vertical, city, state, estimated_revenue, employee_count,
                          top_3_strengths, company_narrative, market_analysis, valuation_range, attack_plan,
                          outreach_strategy, timeline, fee_mode, status, quality_score, certified_by, certified_at,
                          client_signed_at, contract_option_chosen
                   FROM proposals WHERE company_name ILIKE %s ORDER BY quality_score DESC LIMIT 1""", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        assets["proposal"] = {k: (str(v) if v is not None else None) for k, v in zip(cols, row)}

    # Buyers
    cur.execute("""SELECT eb.buyer_company_name, eb.buyer_contact_name, eb.buyer_type, eb.buyer_city, eb.buyer_state,
                          eb.fit_score, eb.fit_narrative, eb.approach_strategy, eb.approach_script,
                          eb.letter_sent_at, eb.email_sent_at, eb.called_at, eb.linkedin_sent_at,
                          eb.response, eb.response_date, eb.meeting_scheduled, eb.dnc_clear, eb.status
                   FROM engagement_buyers eb JOIN proposals p ON eb.proposal_id = p.id
                   WHERE p.company_name ILIKE %s ORDER BY eb.fit_score DESC NULLS LAST""", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    assets["buyers"] = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Profile from intelligence cache
    cur.execute("""SELECT value FROM intelligence_cache WHERE key = 'company_profile'
                   AND company_id IN (SELECT id FROM companies WHERE company_name ILIKE %s)
                   ORDER BY created_at DESC LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    if row:
        assets["profile"] = row[0] if isinstance(row[0], dict) else json.loads(str(row[0])) if row[0] else {}

    # Engagement plan from intelligence cache
    cur.execute("""SELECT value FROM intelligence_cache WHERE key = 'engagement_plan'
                   AND company_id IN (SELECT id FROM companies WHERE company_name ILIKE %s)
                   ORDER BY created_at DESC LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    if row:
        assets["engagement_plan"] = row[0] if isinstance(row[0], dict) else {}

    # Follow-up emails from play_executions
    cur.execute("""SELECT play_code, deliverable_content, status, quality_score, created_at
                   FROM play_executions WHERE target_name ILIKE %s ORDER BY created_at DESC""", (f"%{company_name}%",))
    assets["plays"] = [{"play": r[0], "content": r[1], "status": r[2], "quality": r[3], "date": str(r[4])} for r in cur.fetchall()]

    # Targets data
    cur.execute("""SELECT pipeline_status, research_completed_at, validation_completed_at, letter_completed_at,
                          last_error, last_error_step, notes, report_url, extra_fields
                   FROM targets WHERE company_name ILIKE %s LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    if row:
        assets["target"] = {
            "pipeline_status": row[0], "research_done": str(row[1]) if row[1] else None,
            "validation_done": str(row[2]) if row[2] else None, "letter_done": str(row[3]) if row[3] else None,
            "last_error": row[4], "last_error_step": row[5], "notes": row[6], "report_url": row[7],
        }

    # Step log (pipeline history)
    cur.execute("""SELECT step_type, tool, status, result_summary, cost_usd, completed_at
                   FROM step_log WHERE record_id IN (
                       SELECT id FROM companies WHERE company_name ILIKE %s
                       UNION SELECT id FROM targets WHERE company_name ILIKE %s
                   ) ORDER BY completed_at DESC LIMIT 20""",
                (f"%{company_name}%", f"%{company_name}%"))
    assets["step_history"] = [{"step": r[0], "tool": r[1], "status": r[2], "summary": r[3],
                                "cost": float(r[4]) if r[4] else 0, "date": str(r[5])} for r in cur.fetchall()]

    # Cost tracking
    if assets.get("company_id"):
        cur.execute("SELECT total_cost_usd, cost_log_entries FROM companies WHERE id = %s", (assets["company_id"],))
        row = cur.fetchone()
        if row:
            assets["total_cost"] = float(row[0]) if row[0] else 0
            assets["cost_entries"] = row[1] if isinstance(row[1], list) else []

    # Dossier
    cur.execute("""SELECT owner_name, owner_background, narrative, letter_html, cold_call_script,
                          cold_email_body, linkedin_message, mailing_address, overall_score, certifier_verdict
                   FROM dossier_final WHERE company_name ILIKE %s LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    if row:
        assets["dossier"] = {
            "owner_name": row[0], "owner_background": row[1], "narrative": row[2],
            "letter_html": row[3], "cold_call_script": row[4], "cold_email_body": row[5],
            "linkedin_message": row[6], "mailing_address": row[7],
            "score": row[8], "verdict": row[9]
        }

    # Local HTML files
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    assets["files"] = {}
    slug_for_links = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    for subdir, label, route in [("proposals", "Proposal", "proposal"), ("data-rooms", "Data Room", "dataroom"), ("meetings", "Meeting Prep", "meeting")]:
        dirpath = os.path.expanduser(f"~/Projects/master-crm/data/{subdir}")
        if os.path.exists(dirpath):
            for f in os.listdir(dirpath):
                if slug in f.lower() or company_name.split()[0].lower() in f.lower():
                    assets["files"][f"{label}: {f}"] = f"/company/{slug_for_links}/{route}"

    conn.close()
    return assets


def generate_hub_html(company_name, assets):
    """Generate the single-page company hub."""
    company = assets.get("company", {})
    proposal = assets.get("proposal", {})
    profile = assets.get("profile", {})
    contacts = assets.get("contacts", [])
    buyers = assets.get("buyers", [])
    plays = assets.get("plays", [])
    dossier = assets.get("dossier", {})
    files = assets.get("files", {})
    target = assets.get("target", {})
    step_history = assets.get("step_history", [])

    owner = proposal.get("owner_name") or company.get("owner_name") or dossier.get("owner_name") or "—"
    vertical = proposal.get("vertical") or company.get("vertical") or "—"
    city = proposal.get("city") or company.get("city") or "—"
    state = proposal.get("state") or company.get("state") or "—"
    revenue = proposal.get("estimated_revenue") or company.get("estimated_revenue") or "—"
    employees = proposal.get("employee_count") or company.get("employee_count") or "—"
    quality = proposal.get("quality_score") or "—"
    status = proposal.get("status") or target.get("pipeline_status") or "—"
    total_cost = assets.get("total_cost", 0)

    # Strengths
    strengths = proposal.get("top_3_strengths")
    if isinstance(strengths, str):
        try: strengths = json.loads(strengths)
        except: strengths = []
    strengths_html = "".join(f"<li>{s}</li>" for s in (strengths or []))

    # Contacts table
    contacts_html = ""
    for c in contacts:
        contacts_html += f"<tr><td>{c.get('name','')}</td><td>{c.get('title','')}</td><td>{c.get('email','')}</td><td>{c.get('phone') or c.get('cell','')}</td></tr>"

    # Buyers table — with links to individual buyer pages
    buyers_html = ""
    company_slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    buyer_dir = os.path.expanduser("~/Projects/master-crm/data/buyer-1pagers")
    for b in buyers[:15]:
        fit = str(b.get("fit_score", "")) if b.get("fit_score") else "—"
        dnc = "✅" if b.get("dnc_clear") else "🚫"
        has_script = "📝" if b.get("approach_script") else "—"
        bstatus = b.get("status", "identified")
        buyer_name = b.get('buyer_company_name', '')

        # Find matching buyer page file
        buyer_slug = buyer_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and").replace("(", "").replace(")", "")[:40]
        buyer_link = None
        if os.path.exists(buyer_dir):
            for f in os.listdir(buyer_dir):
                if (company_slug[:10] in f.lower() and buyer_slug[:10] in f.lower()) or buyer_slug[:15] in f.lower():
                    buyer_link = f
                    break

        name_cell = f'<a href="{buyer_link}" style="color:#58a6ff;text-decoration:none">{buyer_name}</a>' if buyer_link else buyer_name
        buyers_html += f"<tr><td>{name_cell}</td><td>{b.get('buyer_type','')}</td><td>{b.get('buyer_city','')}, {b.get('buyer_state','')}</td><td>{fit}</td><td>{dnc}</td><td>{has_script}</td><td>{bstatus}</td></tr>"

    # Files links
    files_html = ""
    for label, path in files.items():
        files_html += f'<li><a href="{path}" target="_blank">{label}</a></li>'
    if not files_html:
        files_html = "<li>No files generated yet</li>"

    # Plays
    plays_html = ""
    for p in plays:
        plays_html += f"<tr><td>{p.get('play','')}</td><td>{p.get('status','')}</td><td>{p.get('quality','')}</td><td>{p.get('date','')[:10]}</td></tr>"

    # Step history
    steps_html = ""
    for s in step_history[:10]:
        steps_html += f"<tr><td>{s.get('step','')}</td><td>{s.get('tool','')}</td><td>{s.get('status','')}</td><td>${s.get('cost',0):.4f}</td><td>{(s.get('date',''))[:16]}</td></tr>"

    # Outreach scripts (from first buyer with scripts)
    scripts = {}
    for b in buyers:
        if b.get("approach_script"):
            try:
                scripts = json.loads(b["approach_script"]) if isinstance(b["approach_script"], str) else b["approach_script"]
            except:
                pass
            break

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} — Company Hub</title>
<meta name="company-name" content="{company_name}">
<meta name="page-type" content="hub">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f6fa; color: #1a1a2e; }}
  .top {{ background: linear-gradient(135deg, #16213e, #1a5276); color: white; padding: 25px 30px; position: sticky; top: 0; z-index: 100; }}
  .top h1 {{ font-size: 24px; }}
  .top .meta {{ font-size: 13px; opacity: 0.8; margin-top: 3px; }}
  .top .badges {{ margin-top: 8px; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-right: 6px; }}
  .badge.green {{ background: #27ae60; }}
  .badge.orange {{ background: #f39c12; }}
  .badge.blue {{ background: #3498db; }}
  .badge.red {{ background: #e74c3c; }}
  nav {{ background: #16213e; padding: 0 30px; display: flex; gap: 0; border-bottom: 2px solid #30363d; overflow-x: auto; }}
  nav a {{ color: #8b949e; text-decoration: none; padding: 10px 15px; font-size: 13px; white-space: nowrap; border-bottom: 2px solid transparent; }}
  nav a:hover, nav a.active {{ color: white; border-bottom-color: #58a6ff; }}
  .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
  .section {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
  .section h2 {{ font-size: 16px; color: #16213e; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #f0f2f5; }}
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .grid3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
  .stat {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
  .stat .num {{ font-size: 28px; font-weight: bold; color: #16213e; }}
  .stat .label {{ font-size: 12px; color: #888; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 8px; background: #f8f9fa; font-weight: 600; color: #555; }}
  td {{ padding: 8px; border-bottom: 1px solid #f0f2f5; }}
  .script-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; white-space: pre-wrap; font-size: 13px; line-height: 1.6; }}
  .script-label {{ font-weight: 600; color: #16213e; margin-bottom: 5px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 4px 0; }}
  a {{ color: #3498db; }}
  .footer {{ text-align: center; padding: 20px; color: #999; font-size: 11px; }}
</style>
</head>
<body>

<div class="top">
  <h1>{company_name}</h1>
  <div class="meta">{owner} | {city}, {state} | {vertical} | Est. Revenue: {revenue} | Employees: {employees}</div>
  <div class="badges">
    <span class="badge {'green' if status == 'engagement_active' else 'orange' if status == 'certified' else 'blue'}">{status}</span>
    <span class="badge blue">Quality: {quality}</span>
    <span class="badge {'green' if total_cost < 1 else 'orange'}">Cost: ${total_cost:.2f}</span>
    <span class="badge blue">{len(buyers)} Buyers</span>
    <span class="badge blue">{len(contacts)} Contacts</span>
  </div>
</div>

<nav>
  <a href="#overview">Overview</a>
  <a href="#contacts">Contacts</a>
  <a href="#proposal">Proposal</a>
  <a href="#buyers">Buyers ({len(buyers)})</a>
  <a href="#scripts">Outreach Scripts</a>
  <a href="#plays">Plays & Emails</a>
  <a href="#files">Files</a>
  <a href="#history">History</a>
</nav>

<div class="container">

  <div class="section" id="overview">
    <h2>Overview</h2>
    <div class="grid3">
      <div class="stat"><div class="num">{len(buyers)}</div><div class="label">Buyers Identified</div></div>
      <div class="stat"><div class="num">{sum(1 for b in buyers if b.get('approach_script'))}</div><div class="label">Scripts Ready</div></div>
      <div class="stat"><div class="num">{len(files)}</div><div class="label">Documents</div></div>
    </div>
    {f'<div style="margin-top:15px"><strong>Top 3 Strengths:</strong><ol>{strengths_html}</ol></div>' if strengths_html else ''}
  </div>

  <div class="section" id="contacts">
    <h2>Contacts</h2>
    <table><tr><th>Name</th><th>Title</th><th>Email</th><th>Phone</th></tr>{contacts_html or '<tr><td colspan="4">No contacts on file</td></tr>'}</table>
  </div>

  <div class="section" id="proposal">
    <h2>Proposal & Attack Plan</h2>
    <p>{proposal.get('company_narrative', dossier.get('narrative', 'No narrative generated yet.'))[:800]}</p>
    {f'<div style="margin-top:15px"><strong>Market Analysis:</strong><p>{proposal.get("market_analysis", "")[:500]}</p></div>' if proposal.get("market_analysis") else ''}
    {f'<div style="margin-top:15px"><strong>Attack Plan:</strong><p>{proposal.get("attack_plan", "")[:500]}</p></div>' if proposal.get("attack_plan") else ''}
    {f'<div style="margin-top:15px"><strong>Timeline:</strong><p>{proposal.get("timeline", "")[:300]}</p></div>' if proposal.get("timeline") else ''}
  </div>

  <div class="section" id="buyers">
    <h2>Buyer Targets ({len(buyers)})</h2>
    <table><tr><th>Buyer</th><th>Type</th><th>Location</th><th>Fit</th><th>DNC</th><th>Script</th><th>Status</th></tr>{buyers_html}</table>
  </div>

  <div class="section" id="scripts">
    <h2>Sample Outreach Scripts</h2>
    {f'<div class="script-label">📧 Email</div><div class="script-box">{scripts.get("email", "No scripts generated")}</div>' if scripts else '<p>No scripts generated yet</p>'}
    {f'<div class="script-label">📞 Call Script</div><div class="script-box">{scripts.get("call_script", "")}</div>' if scripts.get("call_script") else ''}
    {f'<div class="script-label">💼 LinkedIn</div><div class="script-box">{scripts.get("linkedin", "")}</div>' if scripts.get("linkedin") else ''}
    {f'<div class="script-label">✉️ Letter</div><div class="script-box">{scripts.get("letter", "")[:500]}</div>' if scripts.get("letter") else ''}
  </div>

  <div class="section" id="plays">
    <h2>Plays & Emails Sent</h2>
    <table><tr><th>Play</th><th>Status</th><th>Quality</th><th>Date</th></tr>{plays_html or '<tr><td colspan="4">No plays executed yet</td></tr>'}</table>
  </div>

  <div class="section" id="files">
    <h2>Documents & Files</h2>
    <ul>{files_html}</ul>
  </div>

  <div class="section" id="history">
    <h2>Pipeline History</h2>
    <table><tr><th>Step</th><th>Tool</th><th>Status</th><th>Cost</th><th>Date</th></tr>{steps_html or '<tr><td colspan="5">No pipeline history</td></tr>'}</table>
  </div>

  <div class="footer">
    {company_name} — Company Hub | Generated {datetime.now().strftime('%B %d, %Y %I:%M %p')}<br>
    Next Chapter M&A Advisory | INTERNAL — Admin View
  </div>

</div>
<script src="/comment-widget.js"></script>
<script src="/version-widget.js"></script>
</body>
</html>"""

    return html


def generate_hub(company_name):
    """Generate company hub for one company."""
    log(f"Building hub: {company_name}")
    assets = get_all_company_assets(company_name)

    html = generate_hub_html(company_name, assets)

    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    filepath = os.path.join(HUB_DIR, f"{slug}-hub.html")
    with open(filepath, 'w') as f:
        f.write(html)

    dl = os.path.join(DL_DIR, f"{slug}-hub.html")
    with open(dl, 'w') as f:
        f.write(html)

    log(f"  Hub saved: {filepath}")
    return filepath


def generate_all_hubs():
    """Generate hubs for all companies with proposals."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company_name FROM proposals ORDER BY company_name")
    companies = [r[0] for r in cur.fetchall()]
    conn.close()

    log(f"Generating hubs for {len(companies)} companies")
    for company in companies:
        try:
            generate_hub(company)
        except Exception as e:
            log(f"  ERROR on {company}: {e}")

    log("All hubs generated")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_hub(" ".join(sys.argv[1:]))
    else:
        generate_all_hubs()
