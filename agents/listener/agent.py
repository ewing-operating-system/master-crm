#!/usr/bin/env python3
"""
listener/agent.py — The Listener: Lead Intelligence & Play Execution Agent

Scans 5 channels every 5 minutes. For each signal: SCAN → EXTRACT → MATCH →
DIAGNOSE → PRESCRIBE → PERSONALIZE → STAGE → NOTIFY.

Never sends without human approval. Everything stays DRAFT.
Telegram notifications for urgency >= 7.

Channels:
  a. Salesfinity — poll call outcomes via salesfinity_client
  b. Gmail       — check for reply emails (Gmail API)
  c. Lob         — check delivery webhooks / status
  d. Calendar    — check for newly booked meetings
  e. Slack       — check for manual notes/signals

Run: python3 agents/listener/agent.py
     python3 agents/listener/agent.py --once   (single scan, no loop)
"""

import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from lib import supabase as db
from lib.salesfinity_client import get_active_lists, get_call_outcomes

# ── Config ────────────────────────────────────────────────────────────────────

POLL_INTERVAL_SECONDS = 300  # 5 minutes
TELEGRAM_CHAT_ID = os.environ.get("EWING_TELEGRAM_CHAT_ID", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.environ.get("SLACK_LISTENER_CHANNEL", "#deals")
GMAIL_TOKEN = os.environ.get("GMAIL_ACCESS_TOKEN", "")
CALENDAR_TOKEN = os.environ.get("GOOGLE_CALENDAR_TOKEN", "")
LOB_API_KEY = os.environ.get("LOB_API_KEY", "")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")

ctx = ssl.create_default_context()

# ── Urgency scoring weights ───────────────────────────────────────────────────

URGENCY_SCORES = {
    # Signal type → base urgency (1-10)
    "inbound_inquiry": 10,
    "reply_wants_valuation": 9,
    "reply_who_buys": 9,
    "reply_send_email": 8,
    "reply_send_info": 8,
    "meeting_scheduled": 8,
    "reply_competitor_mention": 8,
    "meeting_cancelled": 7,
    "reply_timeline_mention": 7,
    "reply_spouse_involved": 6,
    "connected_call": 6,
    "meeting_completed": 6,
    "letter_opened_no_reply": 5,
    "email_opened_no_reply": 5,
    "reply_call_back": 5,
    "lob_delivered": 4,
    "voicemail_left": 3,
    "gatekeeper_block": 3,
    "reply_not_now": 2,
    "no_answer": 1,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    req = urllib.request.Request(url, headers=h)
    resp = urllib.request.urlopen(req, context=ctx, timeout=20)
    return json.loads(resp.read())


def _sb_insert(table, data, entity=None):
    if entity:
        data["entity"] = entity
    payload = json.dumps(data, default=str).encode()
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}", data=payload, headers=h, method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=20)
    return json.loads(resp.read())


def _sb_upsert(table, data, entity=None):
    if entity:
        data["entity"] = entity
    payload = json.dumps(data, default=str).encode()
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates",
    }
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}", data=payload, headers=h, method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=20)
    return json.loads(resp.read())


def _send_telegram(message):
    """Send message via openclaw telegram channel."""
    if not TELEGRAM_CHAT_ID:
        print(f"[listener] Telegram: EWING_TELEGRAM_CHAT_ID not set. Message: {message}")
        return False
    try:
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", "telegram",
                "--target", TELEGRAM_CHAT_ID,
                "--message", f"[Argus] {message}",
            ],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[listener] Telegram send failed: {e}")
        return False


def _log_scan(channel, signals_found, scan_start, entity="all"):
    """Write listener_scan_log entry."""
    try:
        _sb_insert("listener_scan_log", {
            "channel": channel,
            "signals_found": signals_found,
            "scanned_at": scan_start,
            "entity": entity,
        })
    except Exception:
        pass  # scan log is best-effort


def _get_last_scan_time(channel):
    """Return ISO timestamp of last scan for this channel (default: 6 hours ago)."""
    try:
        rows = _sb_get(
            "listener_scan_log",
            f"channel=eq.{channel}&order=scanned_at.desc&limit=1"
        )
        if rows:
            return rows[0].get("scanned_at")
    except Exception:
        pass
    # Default lookback: 6 hours
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    return since.isoformat()


def _match_situation(signal_type, entity):
    """Look up situation_library for matching situation code."""
    try:
        rows = _sb_get(
            "situation_library",
            f"trigger_signals=cs.{{{signal_type}}}&entity=in.(all,{entity})&order=urgency.desc&limit=1"
        )
        return rows[0] if rows else None
    except Exception:
        return None


def _get_play_template(play_code):
    """Fetch a play template by code."""
    try:
        rows = _sb_get("play_templates", f"play_code=eq.{play_code}&limit=1")
        return rows[0] if rows else None
    except Exception:
        return None


def _lookup_contact(company_name=None, phone=None, email=None):
    """Try to find existing contact in CRM."""
    try:
        if phone:
            rows = _sb_get("contacts", f"phone=eq.{urllib.parse.quote(phone)}&limit=1")
            if rows:
                return rows[0]
        if email:
            rows = _sb_get("contacts", f"email=eq.{urllib.parse.quote(email)}&limit=1")
            if rows:
                return rows[0]
        if company_name:
            rows = _sb_get(
                "contacts",
                f"company_name=ilike.{urllib.parse.quote(company_name)}&limit=1"
            )
            if rows:
                return rows[0]
    except Exception:
        pass
    return None


def _score_urgency(signal_type, context=None):
    """Return urgency score 1-10."""
    base = URGENCY_SCORES.get(signal_type, 3)
    # Boost for timing context
    if context:
        notes_lower = str(context).lower()
        if any(w in notes_lower for w in ("today", "urgent", "asap", "now", "call me")):
            base = min(10, base + 2)
        if any(w in notes_lower for w in ("retirement", "selling", "ready", "this year")):
            base = min(10, base + 1)
    return base


def _create_play(signal, situation, entity):
    """
    Stage a play record in Supabase.
    Always DRAFT — never sends without human approval.
    """
    play_code = (situation.get("recommended_plays") or [""])[0] if situation else None
    template = _get_play_template(play_code) if play_code else None

    play = {
        "entity": entity,
        "play_type": signal.get("signal_type", "unknown"),
        "status": "draft",
        "source": signal.get("channel", "unknown"),
        "urgency_score": signal.get("urgency_score", 3),
        "situation_code": situation.get("situation_code", "UNKNOWN") if situation else "UNKNOWN",
        "play_code": play_code or "manual_review",
        "contact_company": signal.get("company_name", ""),
        "contact_first_name": signal.get("first_name", ""),
        "contact_last_name": signal.get("last_name", ""),
        "contact_phone": signal.get("phone", ""),
        "contact_email": signal.get("email", ""),
        "signal_summary": signal.get("summary", ""),
        "raw_signal": json.dumps(signal, default=str),
        "template_used": play_code,
        "auto_execute_eligible": template.get("auto_execute_approved", False) if template else False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = _sb_insert("plays", play, entity=entity)
        return result[0] if result else play
    except Exception as e:
        print(f"[listener] Failed to create play: {e}")
        return play


# ══════════════════════════════════════════════════════════════════════════════
# CHANNEL SCANNERS
# ══════════════════════════════════════════════════════════════════════════════

# ── Channel A: Salesfinity ────────────────────────────────────────────────────

def scan_salesfinity(since_iso):
    """Scan Salesfinity call outcomes for new signals since last scan."""
    signals = []
    scan_start = datetime.now(timezone.utc).isoformat()

    try:
        lists = get_active_lists()
    except Exception as e:
        print(f"[salesfinity] Failed to get lists: {e}")
        _log_scan("salesfinity", 0, scan_start)
        return signals

    for sf_list in lists:
        list_id = sf_list.get("id")
        if not list_id:
            continue
        try:
            outcomes = get_call_outcomes(list_id)
            for outcome in outcomes:
                # Only process outcomes newer than last scan
                called_at = outcome.get("called_at") or ""
                if called_at and called_at < since_iso:
                    continue

                raw = outcome.get("outcome", "no_answer")
                signal_type_map = {
                    "connected": "connected_call",
                    "voicemail": "voicemail_left",
                    "gatekeeper": "gatekeeper_block",
                    "bad_number": "no_answer",
                    "no_answer": "no_answer",
                }
                signal_type = signal_type_map.get(raw, "no_answer")

                # Check for DNC in notes
                notes_lower = (outcome.get("notes") or "").lower()
                if any(p in notes_lower for p in ("do not call", "dnc", "remove")):
                    signal_type = "dnc_request"

                entity = outcome.get("entity") or "next_chapter"
                urgency = _score_urgency(signal_type, outcome.get("notes"))

                signals.append({
                    "channel": "salesfinity",
                    "signal_type": signal_type,
                    "entity": entity,
                    "urgency_score": urgency,
                    "company_name": outcome.get("company_name", ""),
                    "first_name": outcome.get("first_name", ""),
                    "last_name": outcome.get("last_name", ""),
                    "phone": outcome.get("phone", ""),
                    "email": "",
                    "summary": (
                        f"Salesfinity {raw}: {outcome.get('company_name','')} "
                        f"({outcome.get('duration_seconds',0)}s)"
                    ),
                    "raw": outcome,
                    "timestamp": called_at or scan_start,
                })
        except Exception as e:
            print(f"[salesfinity] Error on list {list_id}: {e}")

    _log_scan("salesfinity", len(signals), scan_start)
    return signals


# ── Channel B: Gmail ──────────────────────────────────────────────────────────

def scan_gmail(since_iso):
    """Check Gmail inbox for reply emails and inbound inquiries."""
    signals = []
    scan_start = datetime.now(timezone.utc).isoformat()

    if not GMAIL_TOKEN:
        _log_scan("gmail", 0, scan_start)
        return signals

    try:
        # Convert ISO to Gmail query timestamp
        since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
        since_epoch = int(since_dt.timestamp())

        query = f"after:{since_epoch} in:inbox -from:me"
        encoded_q = urllib.parse.quote(query)
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={encoded_q}&maxResults=50"

        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {GMAIL_TOKEN}", "Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        data = json.loads(resp.read())

        messages = data.get("messages") or []
        for msg_ref in messages:
            msg_id = msg_ref.get("id")
            if not msg_id:
                continue
            try:
                msg_url = (
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
                    "?format=metadata&metadataHeaders=From&metadataHeaders=Subject"
                    "&metadataHeaders=To&metadataHeaders=Date"
                )
                msg_req = urllib.request.Request(
                    msg_url,
                    headers={"Authorization": f"Bearer {GMAIL_TOKEN}"}
                )
                msg_resp = urllib.request.urlopen(msg_req, context=ctx, timeout=20)
                msg_data = json.loads(msg_resp.read())

                headers_list = (msg_data.get("payload") or {}).get("headers") or []
                headers_dict = {h["name"]: h["value"] for h in headers_list}

                sender = headers_dict.get("From", "")
                subject = headers_dict.get("Subject", "").lower()
                snippet = msg_data.get("snippet", "").lower()

                # Classify signal type from subject/snippet
                if any(w in snippet + subject for w in ("got your letter", "received your letter")):
                    signal_type = "inbound_inquiry"
                    urgency = 9
                elif any(w in snippet for w in ("what's my company worth", "what is my company worth")):
                    signal_type = "reply_wants_valuation"
                    urgency = 9
                elif any(w in snippet for w in ("who would buy", "who buys")):
                    signal_type = "reply_who_buys"
                    urgency = 9
                elif any(w in snippet for w in ("send me more", "more information")):
                    signal_type = "reply_send_info"
                    urgency = 8
                elif any(w in snippet for w in ("send me an email", "email me")):
                    signal_type = "reply_send_email"
                    urgency = 8
                elif any(w in snippet for w in ("not interested", "not right now", "remove me")):
                    signal_type = "reply_not_now"
                    urgency = 2
                elif any(w in snippet for w in ("retiring", "thinking about selling", "ready to sell")):
                    signal_type = "reply_timeline_mention"
                    urgency = 7
                else:
                    signal_type = "inbound_inquiry"
                    urgency = _score_urgency("inbound_inquiry", snippet)

                # Extract email address from From header
                email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", sender)
                email_addr = email_match.group(0) if email_match else ""

                signals.append({
                    "channel": "gmail",
                    "signal_type": signal_type,
                    "entity": "next_chapter",  # Gmail is NC inbox
                    "urgency_score": urgency,
                    "company_name": "",
                    "first_name": "",
                    "last_name": "",
                    "phone": "",
                    "email": email_addr,
                    "summary": f"Gmail: {subject[:80]} from {sender[:60]}",
                    "raw": {"from": sender, "subject": headers_dict.get("Subject", ""), "snippet": msg_data.get("snippet", "")},
                    "timestamp": scan_start,
                })
            except Exception as e:
                print(f"[gmail] Error on message {msg_id}: {e}")

    except Exception as e:
        print(f"[gmail] Scan failed: {e}")

    _log_scan("gmail", len(signals), scan_start)
    return signals


# ── Channel C: Lob ────────────────────────────────────────────────────────────

def scan_lob(since_iso):
    """Check Lob letter delivery status for recent letters."""
    signals = []
    scan_start = datetime.now(timezone.utc).isoformat()

    if not LOB_API_KEY:
        _log_scan("lob", 0, scan_start)
        return signals

    try:
        import base64
        creds = base64.b64encode(f"{LOB_API_KEY}:".encode()).decode()
        url = "https://api.lob.com/v1/letters?limit=20&sort_by=date_created:desc"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Basic {creds}",
                "Accept": "application/json",
            }
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        data = json.loads(resp.read())

        letters = data.get("data") or []
        for letter in letters:
            send_date = letter.get("date_created") or letter.get("send_date") or ""
            if send_date and send_date < since_iso:
                continue

            tracking = letter.get("tracking_events") or []
            status = letter.get("status") or "mailed"

            # Map Lob status to signal
            if status == "delivered":
                signal_type = "lob_delivered"
                urgency = _score_urgency("lob_delivered")
            elif status == "returned":
                signal_type = "lob_returned"
                urgency = 4
            else:
                continue  # Only care about delivered/returned

            meta = letter.get("metadata") or {}
            signals.append({
                "channel": "lob",
                "signal_type": signal_type,
                "entity": meta.get("entity", "next_chapter"),
                "urgency_score": urgency,
                "company_name": meta.get("company_name", ""),
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": "",
                "summary": f"Lob letter {status}: {letter.get('description', '')} [{letter.get('id','')}]",
                "raw": {"letter_id": letter.get("id"), "status": status, "metadata": meta},
                "timestamp": send_date or scan_start,
            })

    except Exception as e:
        print(f"[lob] Scan failed: {e}")

    _log_scan("lob", len(signals), scan_start)
    return signals


# ── Channel D: Google Calendar ────────────────────────────────────────────────

def scan_calendar(since_iso):
    """Check Google Calendar for newly booked or cancelled meetings."""
    signals = []
    scan_start = datetime.now(timezone.utc).isoformat()

    if not CALENDAR_TOKEN:
        _log_scan("calendar", 0, scan_start)
        return signals

    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        # Look for events updated since last scan
        encoded_since = urllib.parse.quote(since_iso)
        url = (
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
            f"?updatedMin={encoded_since}&orderBy=updated&singleEvents=true"
            f"&timeMin={encoded_since}&timeMax={urllib.parse.quote(now_iso)}"
        )
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {CALENDAR_TOKEN}", "Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        data = json.loads(resp.read())

        events = data.get("items") or []
        for event in events:
            status = event.get("status", "confirmed")
            summary = event.get("summary", "").lower()
            attendees = event.get("attendees") or []
            start = (event.get("start") or {}).get("dateTime", "")

            # Only process prospect meetings (not internal)
            internal_domains = ("chapter.guide", "andcapital.com", "revsup.com", "gmail.com")
            prospect_attendees = [
                a for a in attendees
                if not any(a.get("email", "").endswith(d) for d in internal_domains)
            ]
            if not prospect_attendees:
                continue

            if status == "cancelled":
                signal_type = "meeting_cancelled"
                urgency = _score_urgency("meeting_cancelled")
            elif start > now_iso:
                signal_type = "meeting_scheduled"
                urgency = _score_urgency("meeting_scheduled")
            elif start <= now_iso:
                signal_type = "meeting_completed"
                urgency = _score_urgency("meeting_completed")
            else:
                continue

            prospect_email = prospect_attendees[0].get("email", "") if prospect_attendees else ""
            signals.append({
                "channel": "calendar",
                "signal_type": signal_type,
                "entity": "next_chapter",
                "urgency_score": urgency,
                "company_name": "",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": prospect_email,
                "summary": f"Calendar {signal_type}: {event.get('summary', '')} with {prospect_email}",
                "raw": {"event_id": event.get("id"), "summary": event.get("summary"), "status": status, "start": start},
                "timestamp": event.get("updated") or scan_start,
            })

    except Exception as e:
        print(f"[calendar] Scan failed: {e}")

    _log_scan("calendar", len(signals), scan_start)
    return signals


# ── Channel E: Slack ──────────────────────────────────────────────────────────

def scan_slack(since_iso):
    """Check Slack for manual notes and deal signals from team."""
    signals = []
    scan_start = datetime.now(timezone.utc).isoformat()

    if not SLACK_BOT_TOKEN:
        _log_scan("slack", 0, scan_start)
        return signals

    try:
        since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
        since_ts = str(since_dt.timestamp())

        # Get channel ID for deals channel
        ch_url = (
            "https://slack.com/api/conversations.list?types=public_channel,private_channel&limit=200"
        )
        req = urllib.request.Request(
            ch_url,
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        ch_data = json.loads(resp.read())

        channel_name_clean = SLACK_CHANNEL.lstrip("#")
        channels = ch_data.get("channels") or []
        channel_id = next(
            (c["id"] for c in channels if c.get("name") == channel_name_clean), None
        )

        if not channel_id:
            _log_scan("slack", 0, scan_start)
            return signals

        # Fetch messages
        hist_url = (
            f"https://slack.com/api/conversations.history"
            f"?channel={channel_id}&oldest={since_ts}&limit=50"
        )
        req = urllib.request.Request(
            hist_url,
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        hist_data = json.loads(resp.read())

        messages = hist_data.get("messages") or []
        for msg in messages:
            text = msg.get("text", "").lower()
            if not text:
                continue

            # Classify signal from message content
            if any(w in text for w in ("hot lead", "🔥", "very interested", "ready to sell")):
                signal_type = "inbound_inquiry"
                urgency = 9
            elif any(w in text for w in ("valuation", "what's it worth", "what is it worth")):
                signal_type = "reply_wants_valuation"
                urgency = 8
            elif any(w in text for w in ("call me back", "wants a call", "schedule")):
                signal_type = "reply_call_back"
                urgency = 6
            elif any(w in text for w in ("not interested", "remove", "do not call")):
                signal_type = "reply_not_now"
                urgency = 2
            else:
                signal_type = "slack_note"
                urgency = 4

            signals.append({
                "channel": "slack",
                "signal_type": signal_type,
                "entity": "next_chapter",
                "urgency_score": urgency,
                "company_name": "",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": "",
                "summary": f"Slack signal [{signal_type}]: {msg.get('text', '')[:120]}",
                "raw": {"text": msg.get("text", ""), "ts": msg.get("ts"), "user": msg.get("user")},
                "timestamp": scan_start,
            })

    except Exception as e:
        print(f"[slack] Scan failed: {e}")

    _log_scan("slack", len(signals), scan_start)
    return signals


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE: SCAN → EXTRACT → MATCH → DIAGNOSE → PRESCRIBE → PERSONALIZE → STAGE → NOTIFY
# ══════════════════════════════════════════════════════════════════════════════

def process_signal(signal):
    """
    Run a single signal through the full pipeline.

    1. EXTRACT  — identify WHO/WHAT/SIGNAL/URGENCY (already done in scanner)
    2. MATCH    — look up contact in CRM
    3. DIAGNOSE — find matching situation in situation_library
    4. PRESCRIBE — find matching play template
    5. PERSONALIZE — enrich with CRM data (deferred to executor on approval)
    6. STAGE    — create DRAFT play record
    7. NOTIFY   — Telegram for urgency >= 7
    """
    entity = signal.get("entity", "next_chapter")
    signal_type = signal.get("signal_type", "unknown")
    urgency = signal.get("urgency_score", 3)

    # 2. MATCH — look up contact
    contact = _lookup_contact(
        company_name=signal.get("company_name"),
        phone=signal.get("phone"),
        email=signal.get("email"),
    )
    if contact:
        # Enrich signal with CRM data
        if not signal.get("company_name"):
            signal["company_name"] = contact.get("company_name", "")
        if not signal.get("first_name"):
            signal["first_name"] = contact.get("first_name", "")
        if not signal.get("last_name"):
            signal["last_name"] = contact.get("last_name", "")

    # 3. DIAGNOSE — match situation
    situation = _match_situation(signal_type, entity)

    # 4. PRESCRIBE — play is embedded in situation record
    # (template fetched in _create_play)

    # 5. PERSONALIZE — note: full personalization happens in executor at approval time
    # Stage captures all available context now.

    # 6. STAGE — create DRAFT play
    play = _create_play(signal, situation, entity)
    play_id = (play[0] if isinstance(play, list) else play).get("id") if play else None

    # 7. NOTIFY — Telegram for high urgency
    if urgency >= 7:
        company = signal.get("company_name") or "unknown company"
        sit_name = situation.get("situation_name", signal_type) if situation else signal_type
        play_code = (situation.get("recommended_plays") or ["manual_review"])[0] if situation else "manual_review"
        msg = (
            f"Hot signal (urgency {urgency}/10)\n"
            f"Company: {company}\n"
            f"Channel: {signal.get('channel', '?')}\n"
            f"Signal: {sit_name}\n"
            f"Summary: {signal.get('summary', '')[:100]}\n"
            f"Play: {play_code}\n"
            f"A) Approve  B) Edit first  C) Skip"
        )
        _send_telegram(msg)

    return play


def run_scan_cycle():
    """
    Full scan cycle across all 5 channels.
    Returns total signals processed.
    """
    print(f"[listener] Scan cycle starting: {datetime.now(timezone.utc).isoformat()}")

    # Get last scan times per channel
    channels = {
        "salesfinity": scan_salesfinity,
        "gmail": scan_gmail,
        "lob": scan_lob,
        "calendar": scan_calendar,
        "slack": scan_slack,
    }

    total_signals = 0
    all_signals = []

    for channel_name, scanner_fn in channels.items():
        since = _get_last_scan_time(channel_name)
        try:
            signals = scanner_fn(since)
            all_signals.extend(signals)
            total_signals += len(signals)
            if signals:
                print(f"[listener] {channel_name}: {len(signals)} signals")
        except Exception as e:
            print(f"[listener] Error scanning {channel_name}: {e}")

    # Process signals sorted by urgency (highest first)
    all_signals.sort(key=lambda s: s.get("urgency_score", 0), reverse=True)

    plays_created = 0
    for signal in all_signals:
        try:
            process_signal(signal)
            plays_created += 1
        except Exception as e:
            print(f"[listener] Error processing signal: {e}")

    print(f"[listener] Cycle complete: {total_signals} signals, {plays_created} plays staged")
    return total_signals


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    once = "--once" in sys.argv
    print(f"[listener] Starting — poll interval: {POLL_INTERVAL_SECONDS}s")
    print(f"[listener] Telegram: {'configured' if TELEGRAM_CHAT_ID else 'NOT SET'}")
    print(f"[listener] Mode: {'single scan' if once else 'continuous loop'}")

    if once:
        run_scan_cycle()
        return

    while True:
        try:
            run_scan_cycle()
        except KeyboardInterrupt:
            print("[listener] Stopped by user.")
            break
        except Exception as e:
            print(f"[listener] Unexpected error in scan cycle: {e}")
        print(f"[listener] Sleeping {POLL_INTERVAL_SECONDS}s until next scan...")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
