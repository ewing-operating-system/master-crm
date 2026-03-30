#!/usr/bin/env python3
"""
auto_regen_daemon.py — Auto-Regeneration Pipeline Daemon
Feature #66: Monitors target_research for changes, regenerates HTML pages,
commits to git, and triggers Vercel deployment.

Runs as background daemon with 5-minute poll interval.
"""

import json, os, subprocess, time, logging
from datetime import datetime
from pathlib import Path

import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
MASTER_CRM_DIR = Path(os.environ.get("MASTER_CRM_DIR", "/Users/clawdbot/projects/master-crm"))
WEB_DIR = Path(os.environ.get("WEB_DIR", "/Users/clawdbot/projects/master-crm-web"))
POLL_INTERVAL = 300  # 5 minutes
MAX_RETRIES = 3

ctx = ssl.create_default_context()
LOG_FILE = MASTER_CRM_DIR / "data" / "logs" / "auto_regen.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("auto_regen")

def _sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=representation"}

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_patch(table, params, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=_sb_headers(), method="PATCH")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())


# Track last processed timestamp
_last_check = datetime.utcnow().isoformat()


def watch_for_changes():
    """Check target_research for rows updated since last check."""
    global _last_check
    rows = _sb_get("target_research", f"updated_at=gte.{_last_check}&order=updated_at.desc&limit=50")
    _last_check = datetime.utcnow().isoformat()
    return rows


def check_dnc(company_id):
    """Skip targets on DNC list."""
    dnc = _sb_get("do_not_call", f"company_id=eq.{company_id}&limit=1")
    return bool(dnc)


def auto_regenerate_page(page_type, entity_id, company_data=None):
    """
    Regenerate an HTML page from latest data.
    page_type: hub, proposal, buyer_1pager, letter_preview
    """
    log.info(f"Regenerating {page_type} for {entity_id}")

    try:
        if page_type == "hub":
            cmd = f"cd {MASTER_CRM_DIR} && python3 lib/company_hub.py --company {entity_id}"
        elif page_type == "proposal":
            cmd = f"cd {MASTER_CRM_DIR} && python3 lib/proposal_engine.py --proposal {entity_id}"
        elif page_type == "buyer_1pager":
            cmd = f"cd {MASTER_CRM_DIR} && python3 scripts/buyer_1pager_pipeline.py --buyer {entity_id}"
        elif page_type == "dashboard":
            cmd = f"cd {MASTER_CRM_DIR} && python3 lib/dashboard.py"
        else:
            log.warning(f"Unknown page_type: {page_type}")
            return False

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            log.error(f"Regen failed for {page_type}/{entity_id}: {result.stderr[:200]}")
            return False
        log.info(f"Regen success: {page_type}/{entity_id}")
        return True

    except subprocess.TimeoutExpired:
        log.error(f"Regen timeout: {page_type}/{entity_id}")
        return False
    except Exception as e:
        log.error(f"Regen error: {page_type}/{entity_id}: {e}")
        return False


def deploy_to_vercel():
    """Commit changes to git and push to trigger Vercel deployment."""
    changes_pushed = False

    for repo_dir in [MASTER_CRM_DIR, WEB_DIR]:
        try:
            # Check for changes
            status = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, text=True, cwd=str(repo_dir)
            )
            if not status.stdout.strip():
                continue

            # Stage, commit, push
            subprocess.run(["git", "add", "-A"], cwd=str(repo_dir), check=True)

            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            subprocess.run(
                ["git", "commit", "-m", f"auto-regen: {timestamp}"],
                cwd=str(repo_dir), check=True
            )

            push_result = subprocess.run(
                ["git", "push"],
                capture_output=True, text=True, cwd=str(repo_dir), timeout=60
            )
            if push_result.returncode == 0:
                log.info(f"Pushed changes from {repo_dir.name}")
                changes_pushed = True
            else:
                log.error(f"Push failed for {repo_dir.name}: {push_result.stderr[:200]}")

        except Exception as e:
            log.error(f"Deploy error for {repo_dir.name}: {e}")

    return changes_pushed


def process_changes(changed_rows):
    """Process changed research rows — regenerate affected pages."""
    regenerated = 0
    skipped_dnc = 0

    for row in changed_rows:
        company_id = row.get("company_id")
        if not company_id:
            continue

        # DNC check
        if check_dnc(company_id):
            skipped_dnc += 1
            log.info(f"Skipping DNC company: {company_id}")
            continue

        # Regenerate hub page
        for attempt in range(MAX_RETRIES):
            success = auto_regenerate_page("hub", company_id)
            if success:
                regenerated += 1
                break
            log.warning(f"Retry {attempt + 1}/{MAX_RETRIES} for {company_id}")
            time.sleep(5)

    return {"regenerated": regenerated, "skipped_dnc": skipped_dnc}


def run_daemon():
    """Main daemon loop."""
    log.info(f"Auto-regen daemon starting — poll interval {POLL_INTERVAL}s")

    while True:
        try:
            changed = watch_for_changes()
            if changed:
                log.info(f"Found {len(changed)} changed research rows")
                result = process_changes(changed)
                log.info(f"Processed: {result['regenerated']} regenerated, {result['skipped_dnc']} DNC skipped")

                if result["regenerated"] > 0:
                    deploy_to_vercel()
            else:
                log.debug("No changes detected")

        except Exception as e:
            log.error(f"Daemon cycle error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Regeneration Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--once", action="store_true", help="Run single check")
    parser.add_argument("--deploy", action="store_true", help="Force deploy")
    args = parser.parse_args()

    if args.daemon:
        run_daemon()
    elif args.deploy:
        deploy_to_vercel()
    else:
        changed = watch_for_changes()
        print(f"Changed rows: {len(changed)}")
        if changed:
            result = process_changes(changed)
            print(json.dumps(result, indent=2))
