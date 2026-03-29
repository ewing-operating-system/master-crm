#!/usr/bin/env python3
"""
Auto-Refresh — regenerates company hubs and dashboard after any engine produces output.

Call this after any proposal, profile, engagement, or meeting page is generated.
Also runs on a schedule to keep everything current.
"""

import os, sys, time
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dashboard":
        refresh_dashboard()
    elif len(sys.argv) > 1 and sys.argv[1] == "--hub":
        company = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        if company:
            refresh_hub(company)
        else:
            refresh_all_hubs()
    else:
        refresh_all()
