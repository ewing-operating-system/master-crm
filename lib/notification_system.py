#!/usr/bin/env python3
"""
Notification System — Step 11 of the feedback loop.

SYSTEM RULE: Every page, every section, every element must have feedback capability.
The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
Any page generation engine that creates HTML must include <script src="comment-widget.js"></script> before </body>.
No exceptions. This is how we learn.

When a comment is posted:
1. Checks who commented (Mark or Ewing)
2. Notifies the OTHER person via:
   - Store in notifications table
   - If iMessage bridge is available, send via iMessage
"""

import json, os, sys, subprocess, urllib.request, ssl
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")
VERCEL_BASE = "https://master-crm-web-eight.vercel.app"
IMESSAGE_BRIDGE = os.path.expanduser("~/.imessage-bridge/imessage-bridge.sh")
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/feedback_steps_10_14.log")

ctx = ssl.create_default_context()

# Map commenters to their notification recipients
NOTIFY_MAP = {
    "ewing": ["mark"],
    "mark": ["ewing"],
}

# Map commenters to display names
DISPLAY_NAMES = {
    "ewing": "Ewing",
    "mark": "Mark",
}


def log(msg):
    line = f"{datetime.utcnow().isoformat()} | NOTIFY | {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def _supabase_post(table, data):
    """Insert into a Supabase table."""
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=payload,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


def _supabase_get(table, params):
    """Read from a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


def build_page_link(company_name, page_type="proposal"):
    """Build a Vercel link for a company page."""
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "").replace("&", "and")[:40]
    return f"{VERCEL_BASE}/interactive-{slug}.html"


def send_imessage(message):
    """Send an iMessage via the bridge if available."""
    if not os.path.exists(IMESSAGE_BRIDGE):
        log("iMessage bridge not available, skipping iMessage")
        return False
    try:
        result = subprocess.run(
            [IMESSAGE_BRIDGE, message],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log(f"iMessage sent successfully")
            return True
        else:
            log(f"iMessage failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"iMessage error: {e}")
        return False


def notify_on_comment(comment):
    """
    Process a new comment and notify the appropriate person.

    Args:
        comment: dict with keys: commenter, company_name, section_id,
                 comment_text, comment_type, page_type, id
    """
    commenter = comment.get("commenter", "").lower()
    recipients = NOTIFY_MAP.get(commenter, [])

    if not recipients:
        log(f"No recipients configured for commenter: {commenter}")
        return

    company = comment.get("company_name", "Unknown")
    section = comment.get("section_id", "").replace("_", " ")
    text = comment.get("comment_text", "")
    ctype = comment.get("comment_type", "feedback")
    page_link = build_page_link(company, comment.get("page_type", "proposal"))
    display_name = DISPLAY_NAMES.get(commenter, commenter.title())

    for recipient in recipients:
        # 1. Store in notifications table
        notif_data = {
            "recipient": recipient,
            "sender": commenter,
            "notification_type": "comment",
            "title": f"{display_name} commented on {company} — {section}",
            "body": f'"{text[:200]}{"..." if len(text) > 200 else ""}" (Type: {ctype})',
            "link": page_link,
            "company_name": company,
            "section_id": comment.get("section_id"),
            "comment_id": comment.get("id"),
            "is_read": False
        }

        try:
            result = _supabase_post("notifications", notif_data)
            log(f"Notification stored for {recipient}: {notif_data['title']}")
        except Exception as e:
            log(f"Failed to store notification for {recipient}: {e}")

        # 2. Send iMessage if bridge available
        imessage_text = (
            f"[Argus] {display_name} commented on {company} {section}:\n"
            f'"{text[:150]}{"..." if len(text) > 150 else ""}"\n'
            f"Type: {ctype}\n"
            f"View: {page_link}"
        )
        send_imessage(imessage_text)


def check_new_comments():
    """
    Poll for new comments that haven't been notified yet.
    Looks for comments with status='pending' that don't have a notification yet.
    """
    log("Checking for new comments to notify...")

    try:
        # Get recent pending comments (last hour)
        comments = _supabase_get("page_comments",
            "status=eq.pending&order=created_at.desc&limit=20")

        for comment in comments:
            comment_id = comment.get("id")
            # Check if we already notified for this comment
            existing = _supabase_get("notifications",
                f"comment_id=eq.{comment_id}&limit=1")

            if not existing:
                notify_on_comment(comment)
                log(f"Sent notification for comment {comment_id}")

    except Exception as e:
        log(f"Error checking new comments: {e}")


def notify_conflict(company_name, section_id, commenter_a, commenter_b):
    """Notify both parties about a conflict that needs resolution."""
    for recipient in [commenter_a.lower(), commenter_b.lower()]:
        notif_data = {
            "recipient": recipient,
            "sender": "system",
            "notification_type": "conflict",
            "title": f"Conflict on {company_name} — {section_id.replace('_', ' ')}",
            "body": f"You and {commenter_a if recipient != commenter_a.lower() else commenter_b} have conflicting feedback. Please resolve.",
            "link": build_page_link(company_name),
            "company_name": company_name,
            "section_id": section_id,
            "is_read": False
        }
        try:
            _supabase_post("notifications", notif_data)
            log(f"Conflict notification stored for {recipient}")
        except Exception as e:
            log(f"Failed to store conflict notification: {e}")


if __name__ == "__main__":
    check_new_comments()
    log("Notification check complete")
