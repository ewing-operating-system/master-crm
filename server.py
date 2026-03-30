#!/usr/bin/env python3
"""
Master CRM Web Server — Full page-tree navigation with sidebar.
Run: python3 server.py
Access: http://localhost:8080
"""

import http.server
import os
import json
import re
import subprocess
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
from decimal import Decimal

PORT = 8080
BASE_DIR = os.path.expanduser("~/Projects/master-crm/data")
DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"

# Kill any existing server on 8080
subprocess.run(["pkill", "-f", "server.py"], capture_output=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(name):
    """Convert company name to URL slug."""
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-').replace('&', 'and').replace(',', '').replace('.', ''))[:40]


def get_db():
    return psycopg2.connect(DB_CONN)


def fetch_companies():
    """Return list of company dicts with slug, buyer count, etc."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.id, p.company_name, p.status, p.quality_score, p.owner_name,
               p.vertical, p.city, p.state, p.estimated_revenue, p.employee_count,
               (SELECT count(*) FROM engagement_buyers eb WHERE eb.proposal_id = p.id) as buyer_count
        FROM proposals p ORDER BY p.quality_score DESC
    """)
    companies = cur.fetchall()
    conn.close()
    for c in companies:
        c['slug'] = slugify(c['company_name'])
    return companies


def fetch_company_by_slug(slug):
    """Return a single company dict matching the slug."""
    companies = fetch_companies()
    for c in companies:
        if c['slug'] == slug:
            return c
    return None


def fetch_buyers(proposal_id):
    """Return list of buyer dicts for a proposal."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT * FROM engagement_buyers WHERE proposal_id = %s ORDER BY fit_score DESC
    """, (str(proposal_id),))
    buyers = cur.fetchall()
    conn.close()
    return buyers


def fetch_proposal_full(proposal_id):
    """Return full proposal row."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM proposals WHERE id = %s", (str(proposal_id),))
    row = cur.fetchone()
    conn.close()
    return row


def page_versions_exist():
    """Check if page_versions table exists."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='page_versions')")
        exists = cur.fetchone()[0]
        conn.close()
        return exists
    except:
        return False


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


# ---------------------------------------------------------------------------
# CSS / Layout
# ---------------------------------------------------------------------------

DARK_CSS = """
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #1c2128;
    --border: #30363d;
    --text-primary: #f0f6fc;
    --text-secondary: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-hover: #79c0ff;
    --green: #27ae60;
    --yellow: #f39c12;
    --purple: #8e44ad;
    --red: #e74c3c;
    --sidebar-w: 280px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-primary); color: var(--text-secondary);
    display: flex; min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

/* Sidebar */
.sidebar {
    width: var(--sidebar-w); min-width: var(--sidebar-w);
    background: var(--bg-secondary); border-right: 1px solid var(--border);
    overflow-y: auto; padding: 16px 0; position: fixed; top: 0; left: 0;
    height: 100vh; z-index: 100; transition: transform 0.3s;
}
.sidebar-header {
    padding: 12px 16px; font-size: 15px; font-weight: 700;
    color: var(--accent); border-bottom: 1px solid var(--border);
    margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
}
.sidebar-header img, .sidebar-header span.logo { font-size: 18px; }
.nav-section { margin-bottom: 4px; }
.nav-item {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 16px 6px 24px; font-size: 13px; color: var(--text-muted);
    border-left: 3px solid transparent; cursor: pointer; transition: all 0.15s;
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-secondary); }
.nav-item.active { border-left-color: var(--accent); color: var(--accent); background: rgba(88,166,255,0.08); }
.nav-company {
    padding: 8px 16px; font-size: 13px; font-weight: 600;
    color: var(--text-primary); cursor: pointer; display: flex; align-items: center; gap: 6px;
}
.nav-company:hover { background: var(--bg-tertiary); }
.nav-company.active { color: var(--accent); }
.nav-sub { padding-left: 12px; }
.nav-sub .nav-item { padding-left: 36px; font-size: 12px; }
.nav-sub .nav-item.buyer-link { padding-left: 52px; font-size: 11px; }
.nav-toggle {
    display: none; position: fixed; top: 12px; left: 12px; z-index: 200;
    background: var(--bg-secondary); border: 1px solid var(--border);
    color: var(--text-primary); padding: 8px 12px; border-radius: 6px;
    cursor: pointer; font-size: 18px;
}
@media (max-width: 900px) {
    .sidebar { transform: translateX(-100%); }
    .sidebar.open { transform: translateX(0); }
    .nav-toggle { display: block; }
    .main { margin-left: 0 !important; }
}

/* Main content */
.main {
    margin-left: var(--sidebar-w); flex: 1; padding: 24px 32px;
    max-width: 1200px; width: 100%;
}
.breadcrumb {
    font-size: 13px; color: var(--text-muted); margin-bottom: 20px;
    display: flex; align-items: center; gap: 6px;
}
.breadcrumb a { color: var(--text-muted); }
.breadcrumb a:hover { color: var(--accent); }
.breadcrumb .sep { color: #484f58; }
.page-title { font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 20px; }
.card {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 16px;
}
.card h3 { color: var(--text-primary); margin-bottom: 12px; font-size: 16px; }
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; color: white; font-weight: 600;
}
.badge-green { background: var(--green); }
.badge-yellow { background: var(--yellow); }
.badge-blue { background: var(--accent); }
.badge-purple { background: var(--purple); }
.badge-red { background: var(--red); }

/* Grid for landing page */
.company-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px; margin-top: 16px;
}
.company-card {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; transition: border-color 0.2s;
    display: block; color: var(--text-secondary);
}
.company-card:hover { border-color: var(--accent); }
.company-card .name { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.company-card .meta { font-size: 12px; color: var(--text-muted); margin-bottom: 10px; }
.company-card .badges { display: flex; gap: 6px; flex-wrap: wrap; }

/* Table */
table.data-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
}
table.data-table th {
    text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border);
    color: var(--text-muted); font-weight: 600; font-size: 11px; text-transform: uppercase;
}
table.data-table td {
    padding: 10px 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary);
}
table.data-table tr:hover td { background: var(--bg-tertiary); }

/* Version history */
.version-controls {
    display: flex; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap;
}
.version-controls select, .version-controls button {
    background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-secondary);
    padding: 8px 14px; border-radius: 6px; font-size: 13px; cursor: pointer;
}
.version-controls button:hover { border-color: var(--accent); color: var(--accent); }

/* Embedded HTML frame */
.embedded-content {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 10px; padding: 24px; margin-top: 16px;
    overflow: auto;
}
.embedded-content h1, .embedded-content h2, .embedded-content h3 { color: var(--text-primary); }
.coming-soon {
    text-align: center; padding: 60px; color: var(--text-muted); font-size: 18px;
}
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.stat-box {
    background: var(--bg-tertiary); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 20px; flex: 1; min-width: 140px;
}
.stat-box .label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; }
.stat-box .value { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-top: 2px; }

/* Markdown-like content */
.content-block { line-height: 1.7; }
.content-block p { margin-bottom: 12px; }
.content-block ul, .content-block ol { margin: 8px 0 12px 20px; }
.content-block li { margin-bottom: 4px; }
.content-block strong { color: var(--text-primary); }

/* Hub nav tiles */
.hub-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px; margin-top: 16px;
}
.hub-tile {
    display: flex; align-items: center; gap: 12px;
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px; transition: border-color 0.2s;
    color: var(--text-secondary);
}
.hub-tile:hover { border-color: var(--accent); color: var(--accent); }
.hub-tile .icon { font-size: 24px; }
.hub-tile .label { font-size: 14px; font-weight: 600; }
"""

SIDEBAR_JS = """
<script>
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}
// Close sidebar on nav click (mobile)
document.querySelectorAll('.sidebar a').forEach(a => {
    a.addEventListener('click', () => {
        if (window.innerWidth <= 900) document.querySelector('.sidebar').classList.remove('open');
    });
});
</script>
"""


def build_sidebar(companies, active_slug=None, active_page=None):
    """Build the sidebar HTML tree."""
    html = '<button class="nav-toggle" onclick="toggleSidebar()">&#9776;</button>\n'
    html += '<nav class="sidebar">\n'
    html += '  <div class="sidebar-header"><span class="logo">&#127968;</span> Next Chapter CRM</div>\n'
    # Home link
    active_cls = ' active' if active_slug is None and active_page is None else ''
    html += f'  <a href="/" class="nav-item{active_cls}" style="padding-left:16px;font-size:14px;font-weight:600;">&#127968; All Companies</a>\n'
    # Dashboard link
    dash_cls = ' active' if active_page == 'dashboard' else ''
    html += f'  <a href="/dashboard" class="nav-item{dash_cls}" style="padding-left:16px;font-size:14px;">&#128202; Monday Dashboard</a>\n'
    html += '  <div style="border-bottom:1px solid #30363d;margin:8px 0;"></div>\n'

    for co in companies:
        s = co['slug']
        is_active_co = (s == active_slug)
        co_cls = ' active' if is_active_co else ''
        expanded = 'true' if is_active_co else 'false'
        html += f'  <a href="/company/{s}" class="nav-company{co_cls}">{co["company_name"]}</a>\n'
        if is_active_co:
            pages = [
                ('proposal', '&#128203; Proposal'),
                ('dataroom', '&#128274; Data Room'),
                ('meeting', '&#128197; Meeting Prep'),
                ('buyers', f'&#127919; Buyers ({co["buyer_count"]})'),
                ('letters', '&#9993;&#65039; Letters'),
                ('emails', '&#128231; Emails'),
                ('scripts', '&#128222; Scripts'),
                ('plan', '&#9876;&#65039; Attack Plan'),
                ('history', '&#128336; History'),
            ]
            html += '  <div class="nav-sub">\n'
            for page_key, page_label in pages:
                p_cls = ' active' if active_page == page_key else ''
                html += f'    <a href="/company/{s}/{page_key}" class="nav-item{p_cls}">{page_label}</a>\n'
            # If on buyers page, show individual buyers
            if active_page and (active_page == 'buyers' or active_page.startswith('buyer-')):
                try:
                    buyers = fetch_buyers(co['id'])
                    for i, b in enumerate(buyers, 1):
                        b_cls = ' active' if active_page == f'buyer-{i}' else ''
                        html += f'    <a href="/company/{s}/buyers/{i}" class="nav-item buyer-link{b_cls}">{b["buyer_company_name"][:25]}</a>\n'
                except:
                    pass
            html += '  </div>\n'

    html += '</nav>\n'
    return html


def build_breadcrumb(parts):
    """parts = [("Home", "/"), ("Air Control", "/company/air-control"), ("Proposal", None)]"""
    html = '<div class="breadcrumb">'
    for i, (label, href) in enumerate(parts):
        if i > 0:
            html += '<span class="sep">&#8250;</span>'
        if href:
            html += f'<a href="{href}">{label}</a>'
        else:
            html += f'<span style="color:var(--text-secondary)">{label}</span>'
    html += '</div>'
    return html


def wrap_page(title, body_html, companies, active_slug=None, active_page=None, breadcrumb_parts=None):
    """Wrap body content in full page with sidebar, breadcrumb, dark theme."""
    sidebar = build_sidebar(companies, active_slug, active_page)
    bc = build_breadcrumb(breadcrumb_parts) if breadcrumb_parts else ''
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Next Chapter CRM</title>
<style>{DARK_CSS}</style>
</head><body>
{sidebar}
<main class="main">
{bc}
{body_html}
</main>
{SIDEBAR_JS}
</body></html>"""


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------

def render_landing(companies):
    """Landing page with all companies as cards."""
    total_buyers = sum(c['buyer_count'] for c in companies)
    body = f'<h1 class="page-title">Next Chapter — Master CRM</h1>'
    body += '<div class="stat-row">'
    body += f'<div class="stat-box"><div class="label">Companies</div><div class="value">{len(companies)}</div></div>'
    body += f'<div class="stat-box"><div class="label">Total Buyers</div><div class="value">{total_buyers}</div></div>'
    body += f'<div class="stat-box"><div class="label">Date</div><div class="value">{datetime.now().strftime("%b %d")}</div></div>'
    body += '</div>'
    body += '<div class="company-grid">'
    for c in companies:
        status_color = 'badge-green' if c['status'] == 'engagement_active' else 'badge-yellow' if c['status'] == 'certified' else 'badge-blue'
        body += f"""<a href="/company/{c['slug']}" class="company-card">
            <div class="name">{c['company_name']}</div>
            <div class="meta">{c['owner_name'] or ''} &middot; {c['vertical'] or ''} &middot; {c['city'] or ''}, {c['state'] or ''}</div>
            <div class="badges">
                <span class="badge {status_color}">{(c['status'] or '').replace('_', ' ').title()}</span>
                <span class="badge badge-blue">Q: {c['quality_score']}</span>
                <span class="badge badge-purple">{c['buyer_count']} buyers</span>
            </div>
        </a>"""
    body += '</div>'
    return wrap_page('All Companies', body, companies, breadcrumb_parts=[("Home", None)])


def render_company_hub(company, companies):
    """Company hub — everything-in-one-page overview with navigation tiles."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, None)]

    body = f'<h1 class="page-title">{name}</h1>'
    body += '<div class="stat-row">'
    body += f'<div class="stat-box"><div class="label">Status</div><div class="value" style="font-size:15px">{(company["status"] or "").replace("_"," ").title()}</div></div>'
    body += f'<div class="stat-box"><div class="label">Quality</div><div class="value">{company["quality_score"]}</div></div>'
    body += f'<div class="stat-box"><div class="label">Buyers</div><div class="value">{company["buyer_count"]}</div></div>'
    body += f'<div class="stat-box"><div class="label">Vertical</div><div class="value" style="font-size:15px">{company["vertical"] or "N/A"}</div></div>'
    body += '</div>'

    # Try to load the existing hub HTML
    hub_dir = os.path.join(BASE_DIR, "company-hubs")
    hub_html = None
    if os.path.exists(hub_dir):
        for f in os.listdir(hub_dir):
            if slug in f.lower().replace('_', '-') and f.endswith(".html"):
                with open(os.path.join(hub_dir, f)) as fh:
                    hub_html = fh.read()
                break

    # Navigation tiles
    tiles = [
        ('proposal', '&#128203;', 'Proposal'),
        ('dataroom', '&#128274;', 'Data Room'),
        ('meeting', '&#128197;', 'Meeting Prep'),
        ('buyers', '&#127919;', f'Buyers ({company["buyer_count"]})'),
        ('letters', '&#9993;&#65039;', 'Letters'),
        ('emails', '&#128231;', 'Emails'),
        ('scripts', '&#128222;', 'Scripts'),
        ('plan', '&#9876;&#65039;', 'Attack Plan'),
        ('history', '&#128336;', 'History'),
    ]
    body += '<div class="hub-grid">'
    for key, icon, label in tiles:
        body += f'<a href="/company/{slug}/{key}" class="hub-tile"><span class="icon">{icon}</span><span class="label">{label}</span></a>'
    body += '</div>'

    if hub_html:
        # Strip the existing HTML's <html><body> etc., just take the body content
        import re as _re
        inner = _re.sub(r'.*<body[^>]*>', '', hub_html, flags=_re.DOTALL)
        inner = _re.sub(r'</body>.*', '', inner, flags=_re.DOTALL)
        body += f'<div class="card" style="margin-top:20px"><h3>Full Company Hub</h3><div class="embedded-content">{inner}</div></div>'

    return wrap_page(name, body, companies, active_slug=slug, active_page='hub', breadcrumb_parts=bc)


def render_file_page(company, companies, subdir, page_key, page_title, slug_match=None):
    """Generic page that loads an HTML file from a data subdirectory."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), (page_title, None)]

    dirpath = os.path.join(BASE_DIR, subdir)
    content_html = None
    if os.path.exists(dirpath):
        match_slug = slug_match or slug
        for f in sorted(os.listdir(dirpath)):
            if match_slug in f.lower().replace('_', '-').replace(' ', '-') and f.endswith(".html"):
                with open(os.path.join(dirpath, f)) as fh:
                    raw = fh.read()
                # Extract body content
                inner = re.sub(r'.*<body[^>]*>', '', raw, flags=re.DOTALL)
                inner = re.sub(r'</body>.*', '', inner, flags=re.DOTALL)
                content_html = inner
                break

    if content_html:
        body = f'<h1 class="page-title">{page_title}</h1><div class="embedded-content">{content_html}</div>'
    else:
        body = f'<h1 class="page-title">{page_title}</h1><div class="coming-soon">No {page_title.lower()} file generated yet for {name}.</div>'

    return wrap_page(f'{name} — {page_title}', body, companies, active_slug=slug, active_page=page_key, breadcrumb_parts=bc)


def render_buyers_list(company, companies):
    """All buyers with fit scores."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), ("Buyers", None)]
    buyers = fetch_buyers(company['id'])

    body = f'<h1 class="page-title">Buyers for {name}</h1>'
    body += f'<p style="color:var(--text-muted);margin-bottom:16px">{len(buyers)} potential buyers ranked by fit score</p>'
    body += '<div class="card"><table class="data-table"><thead><tr>'
    body += '<th>#</th><th>Company</th><th>Contact</th><th>Type</th><th>Fit Score</th><th>City</th><th>State</th><th>Status</th><th></th>'
    body += '</tr></thead><tbody>'
    for i, b in enumerate(buyers, 1):
        score = float(b['fit_score'] or 0)
        score_cls = 'badge-green' if score >= 7 else 'badge-yellow' if score >= 5 else 'badge-red'
        body += f"""<tr>
            <td>{i}</td>
            <td style="font-weight:600;color:var(--text-primary)">{b['buyer_company_name']}</td>
            <td>{b['buyer_contact_name'] or ''}</td>
            <td>{b['buyer_type'] or ''}</td>
            <td><span class="badge {score_cls}">{score}</span></td>
            <td>{b['buyer_city'] or ''}</td>
            <td>{b['buyer_state'] or ''}</td>
            <td>{(b['status'] or '').replace('_',' ').title()}</td>
            <td><a href="/company/{slug}/buyers/{i}">View &rarr;</a></td>
        </tr>"""
    body += '</tbody></table></div>'
    return wrap_page(f'{name} — Buyers', body, companies, active_slug=slug, active_page='buyers', breadcrumb_parts=bc)


def render_buyer_detail(company, companies, buyer_num):
    """Individual buyer 1-pager, generated on-the-fly from Supabase."""
    slug = company['slug']
    name = company['company_name']
    buyers = fetch_buyers(company['id'])
    idx = buyer_num - 1
    if idx < 0 or idx >= len(buyers):
        body = '<div class="coming-soon">Buyer not found.</div>'
        bc = [("Home", "/"), (name, f"/company/{slug}"), ("Buyers", f"/company/{slug}/buyers"), ("Not Found", None)]
        return wrap_page(f'{name} — Buyer', body, companies, active_slug=slug, active_page='buyers', breadcrumb_parts=bc)

    b = buyers[idx]
    bname = b['buyer_company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), ("Buyers", f"/company/{slug}/buyers"), (bname, None)]

    score = float(b['fit_score'] or 0)
    score_cls = 'badge-green' if score >= 7 else 'badge-yellow' if score >= 5 else 'badge-red'

    body = f'<h1 class="page-title">{bname}</h1>'
    body += '<div class="stat-row">'
    body += f'<div class="stat-box"><div class="label">Fit Score</div><div class="value"><span class="badge {score_cls}" style="font-size:18px;padding:6px 16px">{score}/10</span></div></div>'
    body += f'<div class="stat-box"><div class="label">Type</div><div class="value" style="font-size:15px">{b["buyer_type"] or "N/A"}</div></div>'
    body += f'<div class="stat-box"><div class="label">Location</div><div class="value" style="font-size:15px">{b["buyer_city"] or ""}, {b["buyer_state"] or ""}</div></div>'
    body += f'<div class="stat-box"><div class="label">Status</div><div class="value" style="font-size:15px">{(b["status"] or "").replace("_"," ").title()}</div></div>'
    body += '</div>'

    # Contact info
    body += '<div class="card"><h3>Contact Information</h3>'
    body += f'<p><strong>Name:</strong> {b["buyer_contact_name"] or "N/A"}</p>'
    body += f'<p><strong>Title:</strong> {b["buyer_title"] or "N/A"}</p>'
    body += f'<p><strong>Email:</strong> {b["buyer_email"] or "N/A"}</p>'
    body += f'<p><strong>Phone:</strong> {b["buyer_phone"] or "N/A"}</p>'
    if b.get('buyer_linkedin'):
        body += f'<p><strong>LinkedIn:</strong> <a href="{b["buyer_linkedin"]}" target="_blank">{b["buyer_linkedin"]}</a></p>'
    body += '</div>'

    # Fit narrative
    if b.get('fit_narrative'):
        body += f'<div class="card"><h3>Fit Narrative</h3><div class="content-block"><p>{b["fit_narrative"]}</p></div></div>'

    # Approach strategy
    if b.get('approach_strategy'):
        body += f'<div class="card"><h3>Approach Strategy</h3><div class="content-block"><p>{b["approach_strategy"]}</p></div></div>'

    # Approach script
    if b.get('approach_script'):
        body += f'<div class="card"><h3>Approach Script</h3><div class="content-block" style="white-space:pre-wrap">{b["approach_script"]}</div></div>'

    # Activity log
    body += '<div class="card"><h3>Activity Log</h3><table class="data-table"><tbody>'
    activities = [
        ('Letter Sent', b.get('letter_sent_at')),
        ('Email Sent', b.get('email_sent_at')),
        ('Called', b.get('called_at')),
        ('LinkedIn Sent', b.get('linkedin_sent_at')),
        ('Response', b.get('response_date')),
    ]
    for label, ts in activities:
        val = ts.strftime('%Y-%m-%d %H:%M') if ts else '—'
        body += f'<tr><td style="font-weight:600">{label}</td><td>{val}</td></tr>'
    body += '</tbody></table></div>'

    # Nav
    body += '<div style="margin-top:20px;display:flex;gap:12px">'
    if buyer_num > 1:
        body += f'<a href="/company/{slug}/buyers/{buyer_num-1}" class="badge badge-blue" style="padding:8px 16px;font-size:13px">&larr; Previous Buyer</a>'
    if buyer_num < len(buyers):
        body += f'<a href="/company/{slug}/buyers/{buyer_num+1}" class="badge badge-blue" style="padding:8px 16px;font-size:13px">Next Buyer &rarr;</a>'
    body += '</div>'

    return wrap_page(f'{name} — {bname}', body, companies, active_slug=slug, active_page=f'buyer-{buyer_num}', breadcrumb_parts=bc)


def render_json_page(company, companies, field_name, page_key, page_title):
    """Render a page from proposal JSON fields (letters, emails, scripts, etc.)."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), (page_title, None)]
    proposal = fetch_proposal_full(company['id'])

    data = proposal.get(field_name) if proposal else None

    if data is None:
        body = f'<h1 class="page-title">{page_title}</h1><div class="coming-soon">No {page_title.lower()} data yet for {name}.</div>'
    elif isinstance(data, list):
        body = f'<h1 class="page-title">{page_title} for {name}</h1>'
        body += f'<p style="color:var(--text-muted);margin-bottom:16px">{len(data)} items</p>'
        for i, item in enumerate(data, 1):
            body += f'<div class="card"><h3>#{i}</h3>'
            if isinstance(item, dict):
                for k, v in item.items():
                    body += f'<div style="margin-bottom:8px"><strong style="color:var(--text-primary)">{k.replace("_"," ").title()}:</strong><div class="content-block" style="white-space:pre-wrap;margin-top:4px">{v}</div></div>'
            else:
                body += f'<div class="content-block" style="white-space:pre-wrap">{item}</div>'
            body += '</div>'
    elif isinstance(data, dict):
        body = f'<h1 class="page-title">{page_title} for {name}</h1>'
        body += '<div class="card">'
        for k, v in data.items():
            body += f'<div style="margin-bottom:12px"><strong style="color:var(--text-primary)">{k.replace("_"," ").title()}:</strong><div class="content-block" style="white-space:pre-wrap;margin-top:4px">{v}</div></div>'
        body += '</div>'
    else:
        body = f'<h1 class="page-title">{page_title} for {name}</h1>'
        body += f'<div class="card"><div class="content-block" style="white-space:pre-wrap">{data}</div></div>'

    return wrap_page(f'{name} — {page_title}', body, companies, active_slug=slug, active_page=page_key, breadcrumb_parts=bc)


def render_text_page(company, companies, field_name, page_key, page_title):
    """Render a page from a proposal text field (attack_plan, etc.)."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), (page_title, None)]
    proposal = fetch_proposal_full(company['id'])

    data = proposal.get(field_name) if proposal else None

    if data:
        body = f'<h1 class="page-title">{page_title} for {name}</h1>'
        body += f'<div class="card"><div class="content-block" style="white-space:pre-wrap">{data}</div></div>'
    else:
        body = f'<h1 class="page-title">{page_title}</h1><div class="coming-soon">No {page_title.lower()} data yet for {name}.</div>'

    return wrap_page(f'{name} — {page_title}', body, companies, active_slug=slug, active_page=page_key, breadcrumb_parts=bc)


def render_history(company, companies):
    """Version history page with dropdown and version navigation."""
    slug = company['slug']
    name = company['company_name']
    bc = [("Home", "/"), (name, f"/company/{slug}"), ("History", None)]

    has_versions = page_versions_exist()

    if not has_versions:
        body = f'<h1 class="page-title">Version History — {name}</h1>'
        body += '<div class="coming-soon">'
        body += '<p style="font-size:48px;margin-bottom:16px">&#128336;</p>'
        body += '<p>Version history coming soon.</p>'
        body += '<p style="font-size:14px;margin-top:8px;color:var(--text-muted)">The page_versions table is being created by another agent. Check back shortly.</p>'
        body += '</div>'
    else:
        body = f'<h1 class="page-title">Version History — {name}</h1>'
        body += """
        <div class="version-controls">
            <label style="color:var(--text-muted)">Page type:</label>
            <select id="pageType" onchange="loadVersions()">
                <option value="proposal">Proposal</option>
                <option value="data_room">Data Room</option>
                <option value="meeting">Meeting Prep</option>
                <option value="letter">Letters</option>
                <option value="email">Emails</option>
                <option value="script">Scripts</option>
                <option value="attack_plan">Attack Plan</option>
            </select>
            <button onclick="prevVersion()">&lt; Previous</button>
            <span id="versionLabel" style="color:var(--text-primary);font-weight:600">Version 1 of 1</span>
            <button onclick="nextVersion()">Next &gt;</button>
        </div>
        <div id="versionContent" class="card"><div class="coming-soon">Loading...</div></div>
        <script>
        let versions = [], currentIdx = 0;
        async function loadVersions() {
            const pageType = document.getElementById('pageType').value;
            try {
                const res = await fetch('/api/company/""" + slug + """/versions?page_type=' + pageType);
                versions = await res.json();
                currentIdx = versions.length - 1;
                renderVersion();
            } catch(e) { document.getElementById('versionContent').innerHTML = '<div class="coming-soon">Error loading versions</div>'; }
        }
        function renderVersion() {
            if (!versions.length) {
                document.getElementById('versionLabel').textContent = 'No versions';
                document.getElementById('versionContent').innerHTML = '<div class="coming-soon">No versions found for this page type.</div>';
                return;
            }
            document.getElementById('versionLabel').textContent = 'Version ' + (currentIdx+1) + ' of ' + versions.length;
            const v = versions[currentIdx];
            let html = '<div style="margin-bottom:12px;color:var(--text-muted);font-size:12px">Created: ' + (v.created_at || '') + '</div>';
            html += '<div class="embedded-content">' + (v.content_html || v.content || JSON.stringify(v)) + '</div>';
            document.getElementById('versionContent').innerHTML = html;
        }
        function prevVersion() { if (currentIdx > 0) { currentIdx--; renderVersion(); } }
        function nextVersion() { if (currentIdx < versions.length - 1) { currentIdx++; renderVersion(); } }
        loadVersions();
        </script>
        """

    return wrap_page(f'{name} — History', body, companies, active_slug=slug, active_page='history', breadcrumb_parts=bc)


def render_dashboard(companies):
    """Dashboard page — serve existing HTML or generate from data."""
    bc = [("Home", "/"), ("Dashboard", None)]
    dirpath = os.path.join(BASE_DIR, "dashboards")
    content_html = None
    if os.path.exists(dirpath):
        files = sorted([f for f in os.listdir(dirpath) if f.endswith(".html")])
        if files:
            with open(os.path.join(dirpath, files[-1])) as fh:
                raw = fh.read()
            inner = re.sub(r'.*<body[^>]*>', '', raw, flags=re.DOTALL)
            inner = re.sub(r'</body>.*', '', inner, flags=re.DOTALL)
            content_html = inner

    if content_html:
        body = f'<h1 class="page-title">Monday Dashboard</h1><div class="embedded-content">{content_html}</div>'
    else:
        body = '<h1 class="page-title">Monday Dashboard</h1><div class="coming-soon">No dashboard generated yet.</div>'

    return wrap_page('Dashboard', body, companies, active_page='dashboard', breadcrumb_parts=bc)


# ---------------------------------------------------------------------------
# Request Handler
# ---------------------------------------------------------------------------

class MasterCRMHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '':
            path = '/'

        try:
            companies = fetch_companies()
        except Exception as e:
            self.send_html(f"<h1>Database Error</h1><pre>{e}</pre>", 500)
            return

        try:
            # Landing
            if path == '/':
                return self.send_html(render_landing(companies))

            # Dashboard
            if path == '/dashboard':
                return self.send_html(render_dashboard(companies))

            # API endpoints
            if path.startswith('/api/'):
                return self.handle_api(path, parsed, companies)

            # Company routes
            m = re.match(r'^/company/([a-z0-9-]+)(?:/(.+))?$', path)
            if m:
                slug = m.group(1)
                sub = m.group(2)
                company = None
                for c in companies:
                    if c['slug'] == slug:
                        company = c
                        break
                if not company:
                    return self.send_html(self.error_page(f"Company not found: {slug}", companies), 404)

                if sub is None:
                    return self.send_html(render_company_hub(company, companies))
                elif sub == 'proposal':
                    return self.send_html(render_file_page(company, companies, 'proposals', 'proposal', 'Proposal'))
                elif sub == 'dataroom':
                    return self.send_html(render_file_page(company, companies, 'data-rooms', 'dataroom', 'Data Room'))
                elif sub == 'meeting':
                    return self.send_html(render_file_page(company, companies, 'meetings', 'meeting', 'Meeting Prep'))
                elif sub == 'buyers':
                    return self.send_html(render_buyers_list(company, companies))
                elif re.match(r'^buyers/(\d+)$', sub):
                    num = int(re.match(r'^buyers/(\d+)$', sub).group(1))
                    return self.send_html(render_buyer_detail(company, companies, num))
                elif sub == 'letters':
                    return self.send_html(render_json_page(company, companies, 'letter_templates', 'letters', 'Letters'))
                elif sub == 'emails':
                    return self.send_html(render_json_page(company, companies, 'linkedin_messages', 'emails', 'Email Drafts'))
                elif sub == 'scripts':
                    return self.send_html(render_json_page(company, companies, 'call_scripts', 'scripts', 'Call Scripts'))
                elif sub == 'plan':
                    return self.send_html(render_text_page(company, companies, 'attack_plan', 'plan', 'Attack Plan'))
                elif sub == 'history':
                    return self.send_html(render_history(company, companies))
                else:
                    return self.send_html(self.error_page(f"Page not found: /company/{slug}/{sub}", companies), 404)

            # Serve comment widget JS
            if path == '/comment-widget.js':
                js_path = os.path.join(os.path.expanduser("~/Projects/master-crm/lib"), "comment-widget.js")
                if os.path.exists(js_path):
                    with open(js_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/javascript')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(content)
                    return

            # Static file fallback
            filepath = os.path.join(BASE_DIR, path.lstrip("/"))
            if os.path.exists(filepath) and os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                ct = 'text/html' if filepath.endswith('.html') else 'application/json' if filepath.endswith('.json') else 'application/octet-stream'
                self.send_header('Content-Type', ct)
                self.end_headers()
                self.wfile.write(content)
                return

            self.send_html(self.error_page("404 — Page not found", companies), 404)

        except Exception as e:
            import traceback
            self.send_html(f"<h1>Server Error</h1><pre>{traceback.format_exc()}</pre>", 500)

    def handle_api(self, path, parsed, companies):
        """Handle /api/ routes."""
        qs = parse_qs(parsed.query)

        # GET /api/company/{slug}
        m = re.match(r'^/api/company/([a-z0-9-]+)$', path)
        if m:
            slug = m.group(1)
            company = None
            for c in companies:
                if c['slug'] == slug:
                    company = c
                    break
            if not company:
                return self.send_json({"error": "Company not found"}, 404)

            proposal = fetch_proposal_full(company['id'])
            buyers = fetch_buyers(company['id'])
            result = {
                "company": dict(company),
                "proposal": dict(proposal) if proposal else None,
                "buyers": [dict(b) for b in buyers],
            }
            return self.send_json(result)

        # GET /api/company/{slug}/versions?page_type=...
        m = re.match(r'^/api/company/([a-z0-9-]+)/versions$', path)
        if m:
            if not page_versions_exist():
                return self.send_json([])
            slug = m.group(1)
            page_type = qs.get('page_type', ['proposal'])[0]
            company = None
            for c in companies:
                if c['slug'] == slug:
                    company = c
                    break
            if not company:
                return self.send_json([])
            try:
                conn = get_db()
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute("""SELECT * FROM page_versions
                               WHERE proposal_id = %s AND page_type = %s
                               ORDER BY version_number ASC""",
                            (str(company['id']), page_type))
                versions = [dict(r) for r in cur.fetchall()]
                conn.close()
                return self.send_json(versions)
            except:
                return self.send_json([])

        # GET /api/companies
        if path == '/api/companies':
            return self.send_json([dict(c) for c in companies])

        # GET /api/status
        if path == '/api/status':
            try:
                conn = get_db()
                cur = conn.cursor()
                status = {}
                for table, key in [('companies', 'companies'), ('contacts', 'contacts'),
                                   ('proposals', 'proposals'), ('engagement_buyers', 'buyers')]:
                    cur.execute(f"SELECT count(*) FROM {table}")
                    status[key] = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM agent_queue WHERE status = 'pending'")
                status['queue_pending'] = cur.fetchone()[0]
                conn.close()
                return self.send_json(status)
            except Exception as e:
                return self.send_json({"error": str(e)}, 500)

        return self.send_json({"error": "Unknown API endpoint"}, 404)

    def error_page(self, message, companies):
        body = f'<div class="coming-soon"><p style="font-size:48px;margin-bottom:16px">&#128683;</p><p>{message}</p></div>'
        return wrap_page('Error', body, companies, breadcrumb_parts=[("Home", "/"), ("Error", None)])

    def send_html(self, html, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode() if isinstance(html, str) else html)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, cls=DecimalEncoder, default=str).encode())

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    print(f"Master CRM server starting on http://localhost:{PORT}")
    print(f"  Landing:   http://localhost:{PORT}/")
    print(f"  Dashboard: http://localhost:{PORT}/dashboard")
    print(f"  Company:   http://localhost:{PORT}/company/air-control")
    print(f"  Buyers:    http://localhost:{PORT}/company/air-control/buyers")
    print(f"  API:       http://localhost:{PORT}/api/company/air-control")
    server = http.server.HTTPServer(("0.0.0.0", PORT), MasterCRMHandler)
    server.serve_forever()
