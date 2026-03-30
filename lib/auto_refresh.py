#!/usr/bin/env python3
"""
Auto-Refresh — regenerates company hubs and dashboard after any engine produces output.

SYSTEM RULE: Every page, every section, every element must have feedback capability.
The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
Any page generation engine that creates HTML must include <script src="comment-widget.js"></script> before </body>.
No exceptions. This is how we learn.

Call this after any proposal, profile, engagement, or meeting page is generated.
Also runs on a schedule to keep everything current.
Includes process_corrections() for the feedback loop (Step 13).
"""

import json, os, sys, time, urllib.request, ssl
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/auto_refresh.log")

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | REFRESH | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def refresh_hub(company_name):
    """Regenerate a single company hub."""
    from lib.company_hub import generate_hub
    log(f"Refreshing hub: {company_name}")
    generate_hub(company_name)


def refresh_all_hubs():
    """Regenerate all company hubs."""
    from lib.company_hub import generate_all_hubs
    log("Refreshing all hubs")
    generate_all_hubs()


def refresh_dashboard():
    """Regenerate the dashboard."""
    from lib.dashboard import generate_dashboard
    log("Refreshing dashboard")
    generate_dashboard()


def refresh_all():
    """Full refresh — all hubs + dashboard."""
    log("Full refresh starting")
    refresh_all_hubs()
    refresh_dashboard()
    log("Full refresh complete")


def notify_slack(company_name, asset_type, url=None):
    """
    Send a Slack notification about a new asset.
    Uses the Slack MCP tool if available, otherwise logs for manual send.
    """
    if not url:
        slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:30]
        url = f"http://localhost:8080/company/{slug}"

    message = f"[Argus] New {asset_type} ready for {company_name}: {url}"
    log(f"Slack notification: {message}")

    # Try to send via Slack MCP (if available in this session)
    # For now, just log it — Slack integration is a future wire-up
    return message


def process_corrections():
    """
    Check for applied corrections and regenerate stale pages.
    This runs as part of the orchestrator's 5-minute cycle.
    When a correction is applied (step 12 fact_updater), the page is marked stale.
    Next cycle picks it up and regenerates.
    """
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")
    _ctx = ssl.create_default_context()

    def _get(table, params):
        url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        })
        resp = urllib.request.urlopen(req, context=_ctx)
        return json.loads(resp.read())

    def _patch(table, params, data):
        url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
        payload = json.dumps(data, default=str).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }, method="PATCH")
        resp = urllib.request.urlopen(req, context=_ctx)
        return json.loads(resp.read())

    log("Checking for stale pages to regenerate...")

    try:
        stale_pages = _get("page_versions",
            "is_stale=eq.true&order=created_at.desc")
    except Exception as e:
        log(f"Failed to fetch stale pages: {e}")
        return

    if not stale_pages:
        log("No stale pages found")
        return

    regenerated = 0
    for page in stale_pages:
        company = page.get("company_name")
        page_type = page.get("page_type")
        version = page.get("version", 1)
        page_id = page.get("id")

        log(f"Regenerating stale page: {company} / {page_type} (v{version})")

        try:
            if page_type == "hub":
                refresh_hub(company)
            elif page_type in ("proposal", "data_room"):
                # Re-run proposal engine for this company
                try:
                    from lib.proposal_engine import generate_proposal
                    generate_proposal(company)
                except ImportError:
                    log(f"proposal_engine not importable, refreshing hub instead")
                    refresh_hub(company)
            elif page_type == "meeting":
                # Meeting pages are event-specific, just mark as refreshed
                log(f"Meeting page for {company} marked — manual regeneration needed")
            else:
                refresh_hub(company)

            # Clear stale flag
            _patch("page_versions", f"id=eq.{page_id}",
                   {"is_stale": False, "stale_reason": None})
            regenerated += 1

        except Exception as e:
            log(f"Failed to regenerate {company}/{page_type}: {e}")

    log(f"Regenerated {regenerated}/{len(stale_pages)} stale pages")

    # Also refresh dashboard if any pages were regenerated
    if regenerated > 0:
        try:
            refresh_dashboard()
        except Exception as e:
            log(f"Dashboard refresh failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dashboard":
        refresh_dashboard()
    elif len(sys.argv) > 1 and sys.argv[1] == "--hub":
        company = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        if company:
            refresh_hub(company)
        else:
            refresh_all_hubs()
    elif len(sys.argv) > 1 and sys.argv[1] == "--corrections":
        process_corrections()
    else:
        refresh_all()
