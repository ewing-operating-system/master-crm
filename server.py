#!/usr/bin/env python3
"""
Simple web server for master-crm company hubs.
Serves static HTML from data/ directories.
Run: python3 server.py
Access: http://localhost:8080
"""

import http.server
import os
import json
import psycopg2
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8080
BASE_DIR = os.path.expanduser("~/Projects/master-crm/data")
DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"


class MasterCRMHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "":
            self.serve_index()
        elif path.startswith("/company/"):
            company_slug = path.split("/company/")[1].strip("/")
            self.serve_company_hub(company_slug)
        elif path.startswith("/proposal/"):
            slug = path.split("/proposal/")[1].strip("/")
            self.serve_file("proposals", slug)
        elif path.startswith("/dataroom/"):
            slug = path.split("/dataroom/")[1].strip("/")
            self.serve_file("data-rooms", slug)
        elif path.startswith("/meeting/"):
            slug = path.split("/meeting/")[1].strip("/")
            self.serve_file("meetings", slug)
        elif path == "/dashboard":
            self.serve_latest("dashboards")
        elif path == "/api/companies":
            self.serve_companies_api()
        elif path == "/api/status":
            self.serve_status_api()
        else:
            # Try to serve static files
            self.serve_static(path)

    def serve_index(self):
        """Landing page with links to all companies."""
        try:
            conn = psycopg2.connect(DB_CONN)
            cur = conn.cursor()
            cur.execute("""SELECT p.company_name, p.status, p.quality_score, p.owner_name,
                                  p.vertical, p.city, p.state,
                                  (SELECT count(*) FROM engagement_buyers eb WHERE eb.proposal_id = p.id) as buyer_count
                           FROM proposals p ORDER BY p.quality_score DESC""")
            companies = cur.fetchall()

            cur.execute("SELECT sum(n_live_tup) FROM pg_stat_user_tables WHERE schemaname = 'public'")
            total_rows = cur.fetchone()[0]
            conn.close()

            links = ""
            for c in companies:
                slug = c[0].lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
                color = "#27ae60" if c[1] == "engagement_active" else "#f39c12" if c[1] == "certified" else "#3498db"
                links += f"""
                <a href="/company/{slug}" class="company-card">
                    <div class="name">{c[0]}</div>
                    <div class="meta">{c[3] or ''} | {c[4] or ''} | {c[5] or ''}, {c[6] or ''}</div>
                    <div class="badges">
                        <span class="badge" style="background:{color}">{c[1]}</span>
                        <span class="badge" style="background:#3498db">Q: {c[2]}</span>
                        <span class="badge" style="background:#8e44ad">{c[7]} buyers</span>
                    </div>
                </a>"""

            html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Master CRM</title>
<style>
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; }}
.header {{ background: linear-gradient(135deg, #161b22, #1a5276); padding: 30px; text-align: center; }}
.header h1 {{ color: #58a6ff; font-size: 28px; }}
.header .sub {{ color: #8b949e; margin-top: 5px; }}
.grid {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
.company-card {{ display: block; background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; text-decoration: none; color: #c9d1d9; transition: border-color 0.2s; }}
.company-card:hover {{ border-color: #58a6ff; }}
.company-card .name {{ font-size: 18px; font-weight: bold; color: #f0f6fc; margin-bottom: 5px; }}
.company-card .meta {{ font-size: 12px; color: #8b949e; margin-bottom: 10px; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; color: white; }}
.nav {{ text-align: center; padding: 15px; }}
.nav a {{ color: #58a6ff; margin: 0 15px; text-decoration: none; font-size: 14px; }}
</style></head>
<body>
<div class="header">
  <h1>Next Chapter — Master CRM</h1>
  <div class="sub">{len(companies)} active companies | {total_rows:,} total records | {datetime.now().strftime('%B %d, %Y')}</div>
</div>
<div class="nav">
  <a href="/dashboard">📊 Dashboard</a>
  <a href="/api/status">⚡ API Status</a>
</div>
<div class="grid">{links}</div>
</body></html>"""

            self.send_html(html)
        except Exception as e:
            self.send_html(f"<h1>Error</h1><pre>{e}</pre>", 500)

    def serve_company_hub(self, slug):
        """Serve a company hub page."""
        hub_dir = os.path.join(BASE_DIR, "company-hubs")
        for f in os.listdir(hub_dir):
            if slug in f.lower() and f.endswith(".html"):
                with open(os.path.join(hub_dir, f)) as fh:
                    self.send_html(fh.read())
                return
        self.send_html(f"<h1>Company not found: {slug}</h1>", 404)

    def serve_file(self, subdir, slug):
        """Serve a file from a data subdirectory."""
        dirpath = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dirpath):
            self.send_html(f"<h1>Not found</h1>", 404)
            return
        for f in os.listdir(dirpath):
            if slug in f.lower() and f.endswith(".html"):
                with open(os.path.join(dirpath, f)) as fh:
                    self.send_html(fh.read())
                return
        self.send_html(f"<h1>File not found: {slug}</h1>", 404)

    def serve_latest(self, subdir):
        """Serve the most recent file from a directory."""
        dirpath = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dirpath):
            self.send_html("<h1>Not found</h1>", 404)
            return
        files = sorted([f for f in os.listdir(dirpath) if f.endswith(".html")])
        if files:
            with open(os.path.join(dirpath, files[-1])) as fh:
                self.send_html(fh.read())
        else:
            self.send_html("<h1>No dashboard generated yet</h1>", 404)

    def serve_companies_api(self):
        """JSON API endpoint for companies."""
        try:
            conn = psycopg2.connect(DB_CONN)
            cur = conn.cursor()
            cur.execute("SELECT company_name, entity, city, state, vertical, estimated_revenue, employee_count FROM companies ORDER BY company_name")
            cols = [d[0] for d in cur.description]
            companies = [dict(zip(cols, r)) for r in cur.fetchall()]
            conn.close()
            self.send_json(companies)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def serve_status_api(self):
        """JSON API endpoint for system status."""
        try:
            conn = psycopg2.connect(DB_CONN)
            cur = conn.cursor()
            status = {}
            cur.execute("SELECT sum(n_live_tup) FROM pg_stat_user_tables WHERE schemaname = 'public'")
            status["total_rows"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM companies")
            status["companies"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM contacts")
            status["contacts"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM proposals")
            status["proposals"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM engagement_buyers")
            status["buyers"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM agent_queue WHERE status = 'pending'")
            status["queue_pending"] = cur.fetchone()[0]
            conn.close()
            self.send_json(status)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def serve_static(self, path):
        """Try to serve a static file."""
        filepath = os.path.join(BASE_DIR, path.lstrip("/"))
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            if filepath.endswith('.html'):
                self.send_header('Content-Type', 'text/html')
            elif filepath.endswith('.json'):
                self.send_header('Content-Type', 'application/json')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_html("<h1>404 Not Found</h1>", 404)

    def send_html(self, html, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), MasterCRMHandler)
    print(f"Master CRM server running at http://localhost:{PORT}")
    print(f"Company hubs: http://localhost:{PORT}/company/aquascience")
    print(f"Dashboard: http://localhost:{PORT}/dashboard")
    print(f"API: http://localhost:{PORT}/api/status")
    server.serve_forever()
