#!/usr/bin/env python3
"""
Meeting Engine — generates per-meeting custom web pages.

Takes: company_name + meeting_date + meeting_type
Produces: Custom HTML page with:
  - All relevant data for this meeting
  - Talking points and agenda
  - Checklist of objectives
  - Search box to query the data
  - Status of engagement plan
  - Recommendations from prior interactions
"""

import json, os, sys, subprocess, time, psycopg2
from datetime import datetime

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
MEETINGS_DIR = os.path.expanduser("~/Projects/master-crm/data/meetings")
LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/meeting_engine.log")
os.makedirs(MEETINGS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | MEETING | {msg}"
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


def generate_meeting_page(company_name, meeting_type="discovery", meeting_date=None):
    """Generate a custom meeting prep page."""
    if not meeting_date:
        meeting_date = datetime.now().strftime("%Y-%m-%d")

    log(f"Generating meeting page: {company_name} ({meeting_type}) for {meeting_date}")

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Gather ALL data for this company
    data = {"company_name": company_name, "meeting_type": meeting_type, "meeting_date": meeting_date}

    # Proposal
    cur.execute("SELECT * FROM proposals WHERE company_name ILIKE %s ORDER BY quality_score DESC LIMIT 1", (f"%{company_name}%",))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        proposal = dict(zip(cols, row))
        data["proposal"] = {k: str(v)[:500] if v else None for k, v in proposal.items()
                           if k not in ('proposal_html', 'data_room_html', 'proposal_json') and v}

    # Profile from intelligence_cache
    cur.execute("""SELECT value FROM intelligence_cache
                   WHERE key = 'company_profile'
                   AND company_id IN (SELECT id FROM companies WHERE company_name ILIKE %s)
                   ORDER BY created_at DESC LIMIT 1""", (f"%{company_name}%",))
    row = cur.fetchone()
    if row:
        data["profile"] = row[0] if isinstance(row[0], dict) else json.loads(str(row[0]))

    # Buyers
    cur.execute("""SELECT eb.buyer_company_name, eb.buyer_contact_name, eb.buyer_type, eb.fit_score, eb.approach_strategy, eb.status
                   FROM engagement_buyers eb
                   JOIN proposals p ON eb.proposal_id = p.id
                   WHERE p.company_name ILIKE %s
                   ORDER BY eb.fit_score DESC NULLS LAST""", (f"%{company_name}%",))
    data["buyers"] = [{"name": r[0], "contact": r[1], "type": r[2], "fit": str(r[3] or ''),
                       "approach": r[4], "status": r[5]} for r in cur.fetchall()]

    # Intelligence cache (all entries for this company)
    cur.execute("""SELECT key, value FROM intelligence_cache
                   WHERE company_id IN (SELECT id FROM companies WHERE company_name ILIKE %s)""",
                (f"%{company_name}%",))
    data["intel"] = {r[0]: r[1] for r in cur.fetchall()}

    conn.close()

    # Generate meeting content via Claude CLI
    prompt = f"""Generate a meeting preparation page for a {meeting_type} meeting with {company_name}.

COMPANY DATA:
{json.dumps(data, indent=2, default=str)[:6000]}

Create a JSON meeting prep with these sections:

{{
    "agenda": ["item 1", "item 2", "item 3"],
    "objectives": ["what we want to learn/achieve"],
    "talking_points": ["key points to cover"],
    "questions_to_ask": ["discovery questions"],
    "information_to_share": ["what we bring to the table"],
    "danger_zones": ["topics to avoid or handle carefully"],
    "success_criteria": ["how we know this meeting went well"],
    "next_steps_if_positive": ["what happens if they're interested"],
    "next_steps_if_negative": ["what happens if they're not ready"],
    "one_line_hook": "The single most compelling thing to say in the first 30 seconds"
}}

RULES:
- All about THEM. Frame everything from their perspective.
- Use specific data from the profile (revenue, employees, years)
- Reference their strengths — show we did our homework
- No negative facts
- Meeting type '{meeting_type}' determines the depth

Return ONLY valid JSON."""

    log(f"  Generating via Claude CLI...")
    result = call_claude(prompt)
    meeting_content = parse_json(result)

    if not meeting_content:
        log(f"  Claude CLI failed — using defaults")
        meeting_content = {
            "agenda": [f"Introduction and rapport building", f"Learn about {company_name}'s story",
                       "Discuss their goals and timeline", "Present our approach", "Define next steps"],
            "objectives": ["Understand their motivation", "Assess fit", "Build trust"],
            "talking_points": ["Their company's strengths", "Market conditions", "Our process"],
            "questions_to_ask": ["What prompted you to consider selling?", "What's your ideal timeline?",
                                "What matters most to you in this process?"],
            "one_line_hook": f"We've spent the last week learning everything we can about {company_name} — and we're impressed."
        }

    # Generate HTML
    owner = data.get("proposal", {}).get("owner_name", "the owner")
    vertical = data.get("proposal", {}).get("vertical", "")
    city = data.get("proposal", {}).get("city", "")
    state = data.get("proposal", {}).get("state", "")

    def list_html(items, cls=""):
        return "".join(f'<li class="{cls}">{item}</li>' for item in (items or []))

    buyers_html = ""
    if data.get("buyers"):
        buyers_html = "<h3>Identified Buyers</h3><table><tr><th>Buyer</th><th>Type</th><th>Fit</th><th>Status</th></tr>"
        for b in data["buyers"][:10]:
            buyers_html += f"<tr><td>{b['name']}</td><td>{b['type']}</td><td>{b['fit']}</td><td>{b['status']}</td></tr>"
        buyers_html += "</table>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} — Meeting Prep ({meeting_date})</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; color: #1a1a2e; background: #f5f6fa; line-height: 1.5; }}
  .top-bar {{ background: #16213e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }}
  .top-bar h1 {{ font-size: 18px; }}
  .top-bar .meta {{ font-size: 13px; opacity: 0.7; }}
  .hook {{ background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 20px 30px; text-align: center; font-size: 18px; font-style: italic; }}
  .container {{ max-width: 1000px; margin: 20px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .full {{ grid-column: 1 / -1; }}
  .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
  .card h2 {{ font-size: 16px; color: #16213e; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #f0f2f5; }}
  .card li {{ margin: 6px 0; padding-left: 5px; }}
  .card .checklist li {{ list-style: none; }}
  .card .checklist li::before {{ content: "☐ "; color: #27ae60; font-weight: bold; }}
  .danger li::before {{ content: "⚠ "; color: #e74c3c; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 8px; background: #f8f9fa; font-weight: 600; }}
  td {{ padding: 8px; border-bottom: 1px solid #f0f2f5; }}
  .footer {{ text-align: center; padding: 20px; color: #999; font-size: 11px; grid-column: 1 / -1; }}
  @media (max-width: 700px) {{ .container {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="top-bar">
  <div>
    <h1>{company_name}</h1>
    <div class="meta">{meeting_type.title()} Meeting — {meeting_date} | {owner} | {city}, {state} | {vertical}</div>
  </div>
  <div class="meta">INTERNAL — Do not share with client</div>
</div>

<div class="hook">
  "{meeting_content.get('one_line_hook', f'We know {company_name} better than anyone who will walk through that door.')}"
</div>

<div class="container">
  <div class="card">
    <h2>Agenda</h2>
    <ol>{list_html(meeting_content.get('agenda', []))}</ol>
  </div>

  <div class="card">
    <h2>Objectives ☐</h2>
    <ul class="checklist">{list_html(meeting_content.get('objectives', []))}</ul>
  </div>

  <div class="card">
    <h2>Talking Points</h2>
    <ul>{list_html(meeting_content.get('talking_points', []))}</ul>
  </div>

  <div class="card">
    <h2>Questions to Ask</h2>
    <ol>{list_html(meeting_content.get('questions_to_ask', []))}</ol>
  </div>

  <div class="card">
    <h2>What We Bring</h2>
    <ul>{list_html(meeting_content.get('information_to_share', []))}</ul>
  </div>

  <div class="card">
    <h2>Danger Zones</h2>
    <ul class="danger">{list_html(meeting_content.get('danger_zones', []))}</ul>
  </div>

  <div class="card">
    <h2>If Positive → Next Steps</h2>
    <ul class="checklist">{list_html(meeting_content.get('next_steps_if_positive', []))}</ul>
  </div>

  <div class="card">
    <h2>If Not Ready → Next Steps</h2>
    <ul>{list_html(meeting_content.get('next_steps_if_negative', []))}</ul>
  </div>

  <div class="card full">
    <h2>Success Criteria</h2>
    <ul class="checklist">{list_html(meeting_content.get('success_criteria', []))}</ul>
  </div>

  {f'<div class="card full">{buyers_html}</div>' if buyers_html else ''}

  <div class="footer">
    Generated {datetime.now().strftime('%B %d, %Y %I:%M %p')} — Next Chapter M&A Advisory<br>
    INTERNAL DOCUMENT — Meeting prep for {owner} at {company_name}
  </div>
</div>

</body>
</html>"""

    # Save
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
    filename = f"{slug}_{meeting_date}_{meeting_type}.html"
    filepath = os.path.join(MEETINGS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(html)

    log(f"  Meeting page saved: {filepath}")

    # Also copy to Downloads
    dl_path = os.path.expanduser(f"~/Downloads/master-crm-proposals/{filename}")
    with open(dl_path, 'w') as f:
        f.write(html)

    return filepath


def generate_all_meeting_pages():
    """Generate meeting pages for all active proposals."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT company_name FROM proposals ORDER BY quality_score DESC")
    companies = [r[0] for r in cur.fetchall()]
    conn.close()

    log(f"Generating meeting pages for {len(companies)} companies")
    for company in companies:
        try:
            generate_meeting_page(company, "discovery")
        except Exception as e:
            log(f"ERROR on {company}: {e}")
        time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        company = sys.argv[1]
        meeting_type = sys.argv[2] if len(sys.argv) > 2 else "discovery"
        generate_meeting_page(company, meeting_type)
    else:
        generate_all_meeting_pages()
