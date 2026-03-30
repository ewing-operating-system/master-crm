#!/usr/bin/env python3
"""
Notification system for master-crm feedback loop.

notify() inserts into the Supabase `notifications` table via REST API.
For critical notification types (revision_ready, fact_correction), also
sends a Telegram message via openclaw.

notification_type values:
  comment, fact_correction, revision_ready, approval, system
"""

import json, os, subprocess, urllib.request, ssl
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Supabase REST — same pattern as lib/supabase.py
# ---------------------------------------------------------------------------
_SUPA_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
_SUPA_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)
_ctx = ssl.create_default_context()

# Only these types trigger a Telegram message
_TELEGRAM_TYPES = {"revision_ready", "fact_correction"}


def _supa_insert(data: dict):
    """POST a single row to the notifications table."""
    url = f"{_SUPA_URL}/rest/v1/notifications"
    payload = json.dumps(data, default=str).encode()
    headers = {
        "apikey": _SUPA_KEY,
        "Authorization": f"Bearer {_SUPA_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


def _send_telegram(text: str):
    """Send a Telegram message via openclaw. Fire-and-forget."""
    chat_id = os.environ.get("EWING_TELEGRAM_CHAT_ID", "")
    if not chat_id:
        return  # Not configured — skip silently
    try:
        subprocess.run(
            [
                "openclaw",
                "message",
                "send",
                "--channel",
                "telegram",
                "--target",
                chat_id,
                "--message",
                f"[Argus] {text}",
            ],
            capture_output=True,
            timeout=15,
        )
    except Exception:
        pass  # Non-blocking — never raise


def notify(
    recipient: str,
    notification_type: str,
    title: str,
    message: str,
    link: str = None,
    company_name: str = None,
    metadata: dict = None,
) -> bool:
    """
    Insert a notification row into Supabase and, for critical types,
    also send a Telegram message.

    Returns True on success, False on failure.
    """
    row = {
        "recipient": recipient,
        "notification_type": notification_type,
        "title": title,
        "message": message,
    }
    if link:
        row["link"] = link
    if company_name:
        row["company_name"] = company_name
    if metadata:
        row["metadata"] = json.dumps(metadata, default=str)

    try:
        _supa_insert(row)
    except Exception as e:
        # Log but do not raise — notifications are best-effort
        print(f"[notification_system] Supabase insert failed: {e}", flush=True)
        return False

    # Telegram only for high-signal events
    if notification_type in _TELEGRAM_TYPES:
        telegram_text = title
        if company_name:
            telegram_text = f"{company_name} — {title}"
        if message:
            telegram_text += f": {message[:120]}"
        _send_telegram(telegram_text)

    return True
