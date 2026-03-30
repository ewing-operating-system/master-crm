#!/usr/bin/env python3
"""
Company Hub — single page per company linking every asset we've ever created.

One URL, one company, everything: proposal, data room, meeting pages, buyer list,
profile, emails, call scripts, timeline, intelligence, costs.

Admin view shows everything. Client view shows curated subset.

Uses the master page template system (lib/page_template.py) for consistent styling.
"""

import json, os, sys, time, psycopg2
from datetime import datetime
from page_template import wrap_page, get_page_framing

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

    # Proposal (including deal_side and buyer_narrative)
    cur.execute("""SELECT id, company_name, owner_name, vertical, city, state, estimated_revenue, employee_count,
                          top_3_strengths, company_narrative, market_analysis, valuation_range, attack_plan,
                          outreach_strategy, timeline, fee_mode, status, quality_score, certified_by, certified_at,
                          client_signed_at, contract_option_chosen, deal_side, buyer_narrative
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


def _esc(val):
    """Escape HTML entities in a value."""
    if val is None:
        return ''
    s = str(val)
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_hub_html(company_name, assets):
    """Generate the single-page company hub using master template."""
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
    deal_side = proposal.get("deal_side") or "sell_side"
    buyer_narrative = proposal.get("buyer_narrative") or ""

    framing = get_page_framing(deal_side)

    # Strengths
    strengths = proposal.get("top_3_strengths")
    if isinstance(strengths, str):
        try: strengths = json.loads(strengths)
        except: strengths = []
    strengths_html = "".join(f"<li>{_esc(s)}</li>" for s in (strengths or []))

    # Contacts table
    contacts_html = ""
    for c in contacts:
        linkedin = f'<a href="{c.get("linkedin","")}" target="_blank">Profile</a>' if c.get("linkedin") else "—"
        contacts_html += f"""<tr>
            <td>{_esc(c.get('name',''))}</td>
            <td>{_esc(c.get('title',''))}</td>
            <td>{_esc(c.get('email',''))}</td>
            <td>{_esc(c.get('phone') or c.get('cell',''))}</td>
            <td>{linkedin}</td>
        </tr>"""

    # Buyers table
    buyers_html = ""
    company_slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    buyer_dir = os.path.expanduser("~/Projects/master-crm/data/buyer-1pagers")
    for b in buyers[:15]:
        fit = str(b.get("fit_score", "")) if b.get("fit_score") else "—"
        dnc = '<span class="badge green" style="font-size:10px">Clear</span>' if b.get("dnc_clear") else '<span class="badge red" style="font-size:10px">DNC</span>'
        has_script = '<span class="badge blue" style="font-size:10px">Ready</span>' if b.get("approach_script") else "—"
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

        name_cell = f'<a href="{buyer_link}">{_esc(buyer_name)}</a>' if buyer_link else _esc(buyer_name)
        status_badge = 'green' if bstatus in ('contacted','meeting_scheduled','closed') else 'orange' if bstatus in ('letter_sent','called') else 'gray'
        buyers_html += f"""<tr>
            <td>{name_cell}</td>
            <td>{_esc(b.get('buyer_type',''))}</td>
            <td>{_esc(b.get('buyer_city',''))}, {_esc(b.get('buyer_state',''))}</td>
            <td>{fit}</td>
            <td>{dnc}</td>
            <td>{has_script}</td>
            <td><span class="badge {status_badge}" style="font-size:10px">{_esc(bstatus)}</span></td>
        </tr>"""

    # Files links
    files_html = ""
    for label, path in files.items():
        files_html += f'<li><a href="{path}" target="_blank">{_esc(label)}</a></li>'
    if not files_html:
        files_html = "<li style='color:#8b949e'>No files generated yet</li>"

    # Plays
    plays_html = ""
    for p in plays:
        plays_html += f"""<tr>
            <td>{_esc(p.get('play',''))}</td>
            <td>{_esc(p.get('status',''))}</td>
            <td>{_esc(p.get('quality',''))}</td>
            <td>{_esc(p.get('date',''))[:10]}</td>
        </tr>"""

    # Step history
    steps_html = ""
    for s in step_history[:10]:
        steps_html += f"""<tr>
            <td>{_esc(s.get('step',''))}</td>
            <td>{_esc(s.get('tool',''))}</td>
            <td>{_esc(s.get('status',''))}</td>
            <td>${s.get('cost',0):.4f}</td>
            <td>{(s.get('date',''))[:16]}</td>
        </tr>"""

    # Outreach scripts (from dossier or first buyer with scripts)
    scripts = {}
    if dossier.get("cold_call_script") or dossier.get("cold_email_body"):
        scripts["call_script"] = dossier.get("cold_call_script", "")
        scripts["email"] = dossier.get("cold_email_body", "")
        scripts["linkedin"] = dossier.get("linkedin_message", "")
        scripts["letter"] = dossier.get("letter_html", "")
    else:
        for b in buyers:
            if b.get("approach_script"):
                try:
                    scripts = json.loads(b["approach_script"]) if isinstance(b["approach_script"], str) else b["approach_script"]
                except:
                    pass
                break

    # --- Build body HTML sections ---
    body_parts = []

    # Status bar badges
    status_class = 'green' if status in ('engagement_active','active') else 'orange' if status == 'certified' else 'blue'
    cost_class = 'green' if total_cost < 1 else 'orange'
    body_parts.append(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px">
        <span class="badge {status_class}">{_esc(status)}</span>
        <span class="badge blue">Quality: {_esc(quality)}</span>
        <span class="badge {cost_class}">Cost: ${total_cost:.2f}</span>
        <span class="badge blue">{len(buyers)} {framing['buyer_section']}</span>
        <span class="badge blue">{len(contacts)} Contacts</span>
    </div>""")

    # Overview
    body_parts.append(f"""
    <div class="card" id="overview">
        <h2>Overview</h2>
        <div class="grid4">
            <div class="stat"><div class="num">{len(buyers)}</div><div class="label">{framing['buyer_section']}</div></div>
            <div class="stat"><div class="num">{sum(1 for b in buyers if b.get('approach_script'))}</div><div class="label">Scripts Ready</div></div>
            <div class="stat"><div class="num">{sum(1 for b in buyers if b.get('letter_sent_at'))}</div><div class="label">Letters Sent</div></div>
            <div class="stat"><div class="num">{len(files)}</div><div class="label">Documents</div></div>
        </div>
        {'<div style="margin-top:16px"><strong style="color:#f0f6fc">Top 3 Strengths:</strong><ol style="margin-top:8px">' + strengths_html + '</ol></div>' if strengths_html else ''}
    </div>""")

    # Buy-side narrative OR sell-side company story
    if deal_side == 'buy_side' and buyer_narrative:
        narrative_title = framing['narrative_label'].replace('{company}', company_name.split(',')[0].split('Inc')[0].strip())
        body_parts.append(f"""
    <div class="highlight-card" id="narrative">
        <h2>{_esc(narrative_title)}</h2>
        <div class="narrative-box">{_esc(buyer_narrative)}</div>
        <p style="font-size:12px;color:#8b949e;margin-top:10px">This narrative appears on all outreach to acquisition targets.</p>
    </div>""")
    else:
        narrative_text = proposal.get('company_narrative') or dossier.get('narrative') or ''
        if narrative_text:
            body_parts.append(f"""
    <div class="highlight-card" id="narrative">
        <h2>{framing['narrative_label']}</h2>
        <div class="narrative-box">{_esc(narrative_text[:1200])}</div>
    </div>""")

    # Contacts
    body_parts.append(f"""
    <div class="card" id="contacts">
        <h2>Contacts</h2>
        <table>
            <tr><th>Name</th><th>Title</th><th>Email</th><th>Phone</th><th>LinkedIn</th></tr>
            {contacts_html or '<tr><td colspan="5" style="color:#8b949e">No contacts on file</td></tr>'}
        </table>
    </div>""")

    # Proposal & Attack Plan
    narrative_text = proposal.get('company_narrative') or dossier.get('narrative') or 'No narrative generated yet.'
    body_parts.append(f"""
    <div class="card" id="proposal">
        <h2>{framing['attack_label']}</h2>
        <p>{_esc(narrative_text[:800])}</p>
        {'<div style="margin-top:15px"><strong style="color:#f0f6fc">Market Analysis:</strong><p style="margin-top:6px">' + _esc(proposal.get("market_analysis", "")[:500]) + '</p></div>' if proposal.get("market_analysis") else ''}
        {'<div style="margin-top:15px"><strong style="color:#f0f6fc">Attack Plan:</strong><p style="margin-top:6px">' + _esc(proposal.get("attack_plan", "")[:500]) + '</p></div>' if proposal.get("attack_plan") else ''}
        {'<div style="margin-top:15px"><strong style="color:#f0f6fc">Timeline:</strong><p style="margin-top:6px">' + _esc(proposal.get("timeline", "")[:300]) + '</p></div>' if proposal.get("timeline") else ''}
    </div>""")

    # Buyers / Targets table
    body_parts.append(f"""
    <div class="card" id="buyers">
        <h2>{framing['buyer_section']} ({len(buyers)})</h2>
        <table>
            <tr><th>Company</th><th>Type</th><th>Location</th><th>Fit</th><th>DNC</th><th>Script</th><th>Status</th></tr>
            {buyers_html or '<tr><td colspan="7" style="color:#8b949e">No targets identified yet</td></tr>'}
        </table>
    </div>""")

    # Outreach Scripts
    scripts_content = ""
    if scripts:
        if scripts.get("email"):
            scripts_content += f'<div class="script-label">Email</div><div class="script-box">{_esc(scripts["email"])}</div>'
        if scripts.get("call_script"):
            scripts_content += f'<div class="script-label">Call Script</div><div class="script-box">{_esc(scripts["call_script"])}</div>'
        if scripts.get("linkedin"):
            scripts_content += f'<div class="script-label">LinkedIn</div><div class="script-box">{_esc(scripts["linkedin"])}</div>'
        if scripts.get("letter"):
            scripts_content += f'<div class="script-label">Letter</div><div class="script-box">{_esc(str(scripts["letter"])[:500])}</div>'
    else:
        scripts_content = '<p style="color:#8b949e">No scripts generated yet</p>'

    body_parts.append(f"""
    <div class="card" id="scripts">
        <h2>Outreach Scripts</h2>
        {scripts_content}
    </div>""")

    # Plays & Emails
    body_parts.append(f"""
    <div class="card" id="plays">
        <h2>Plays &amp; Emails Sent</h2>
        <table>
            <tr><th>Play</th><th>Status</th><th>Quality</th><th>Date</th></tr>
            {plays_html or '<tr><td colspan="4" style="color:#8b949e">No plays executed yet</td></tr>'}
        </table>
    </div>""")

    # Documents
    body_parts.append(f"""
    <div class="card" id="files">
        <h2>Documents &amp; Files</h2>
        <ul>{files_html}</ul>
    </div>""")

    # Pipeline History
    body_parts.append(f"""
    <div class="card" id="history">
        <h2>Pipeline History</h2>
        <table>
            <tr><th>Step</th><th>Tool</th><th>Status</th><th>Cost</th><th>Date</th></tr>
            {steps_html or '<tr><td colspan="5" style="color:#8b949e">No pipeline history</td></tr>'}
        </table>
    </div>""")

    body_html = "\n".join(body_parts)

    # Build subtitle
    subtitle = f"{owner} | {city}, {state} | {vertical} | Rev: {revenue} | Employees: {employees}"

    # Nav links
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    nav_links = [
        {"label": "Home", "href": "/dashboard.html"},
        {"label": "Dashboard", "href": "/dashboard.html"},
        {"label": "Company Hub", "href": f"/{slug}-hub.html", "active": True},
        {"label": "EBITDA Levers", "href": f"/{slug}-ebitda-levers.html"},
        {"label": "Version History", "href": "#history"},
    ]

    return wrap_page(
        title=company_name,
        subtitle=subtitle,
        company_name=company_name,
        deal_side=deal_side,
        nav_links=nav_links,
        body_html=body_html,
        show_comment_widget=True,
        show_version_widget=True,
    )


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
    os.makedirs(os.path.dirname(dl), exist_ok=True)
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
    paths = []
    for company in companies:
        try:
            path = generate_hub(company)
            paths.append(path)
        except Exception as e:
            log(f"  ERROR on {company}: {e}")
            import traceback
            traceback.print_exc()

    log("All hubs generated")
    return paths


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_hub(" ".join(sys.argv[1:]))
    else:
        generate_all_hubs()
