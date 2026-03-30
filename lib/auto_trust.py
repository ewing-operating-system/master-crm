#!/usr/bin/env python3
"""
auto_trust.py — Graduated Auto-Trust System
Feature #53: Score-based auto-escalation. 10 approvals → auto-execute with inspection.

Usage:
    from lib.auto_trust import should_auto_execute, record_approval, record_rejection
"""

import json, os
from datetime import datetime, timedelta

import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ctx = ssl.create_default_context()

AUTO_EXECUTE_THRESHOLD = 10
REJECTION_PENALTY = 3
MIN_TRUST = 1
MAX_TRUST = 15

# Inspection windows decrease with trust level
INSPECTION_WINDOWS = {
    10: 30,   # 30 minutes at threshold
    11: 20,
    12: 15,
    13: 10,
    14: 5,
    15: 2,    # 2 minutes at max trust
}

def _sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=_sb_headers(), method="POST")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_upsert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {**_sb_headers(), "Prefer": "return=representation,resolution=merge-duplicates"}
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=headers, method="POST")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())


def get_trust_level(action_type, entity):
    """Get current trust score for an action type + entity combo."""
    rows = _sb_get("trust_scores", f"action_type=eq.{action_type}&entity=eq.{entity}&limit=1")
    if rows:
        return rows[0].get("trust_level", MIN_TRUST)
    return MIN_TRUST


def record_approval(action_type, entity):
    """Increment trust after an approved action. Returns new level."""
    current = get_trust_level(action_type, entity)
    new_level = min(current + 1, MAX_TRUST)

    _sb_upsert("trust_scores", {
        "action_type": action_type,
        "entity": entity,
        "trust_level": new_level,
        "consecutive_approvals": current,  # approximation
        "last_approval_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    })

    _sb_post("trust_history", {
        "action_type": action_type,
        "entity": entity,
        "event": "approval",
        "old_level": current,
        "new_level": new_level,
        "created_at": datetime.utcnow().isoformat(),
    })

    return new_level


def record_rejection(action_type, entity, reason=""):
    """Decrement trust after a rejection. Returns new level."""
    current = get_trust_level(action_type, entity)
    new_level = max(current - REJECTION_PENALTY, MIN_TRUST)

    _sb_upsert("trust_scores", {
        "action_type": action_type,
        "entity": entity,
        "trust_level": new_level,
        "consecutive_approvals": 0,
        "last_rejection_at": datetime.utcnow().isoformat(),
        "rejection_reason": reason,
        "updated_at": datetime.utcnow().isoformat(),
    })

    _sb_post("trust_history", {
        "action_type": action_type,
        "entity": entity,
        "event": "rejection",
        "reason": reason,
        "old_level": current,
        "new_level": new_level,
        "created_at": datetime.utcnow().isoformat(),
    })

    return new_level


def should_auto_execute(action_type, entity):
    """Returns True if trust level meets auto-execute threshold."""
    level = get_trust_level(action_type, entity)
    return level >= AUTO_EXECUTE_THRESHOLD


def get_inspection_window(action_type, entity):
    """Returns inspection window in minutes before auto-send."""
    level = get_trust_level(action_type, entity)
    if level < AUTO_EXECUTE_THRESHOLD:
        return None  # Manual approval required
    return INSPECTION_WINDOWS.get(level, INSPECTION_WINDOWS[AUTO_EXECUTE_THRESHOLD])


def get_all_trust_levels(entity=None):
    """Get all trust levels, optionally filtered by entity."""
    params = "order=trust_level.desc"
    if entity:
        params += f"&entity=eq.{entity}"
    return _sb_get("trust_scores", params)


def get_trust_history(action_type=None, entity=None, limit=50):
    """Get trust change history."""
    params = f"order=created_at.desc&limit={limit}"
    if action_type:
        params += f"&action_type=eq.{action_type}"
    if entity:
        params += f"&entity=eq.{entity}"
    return _sb_get("trust_history", params)


def notify_auto_execute(action_type, entity, target_description, inspection_minutes):
    """Send Telegram notification about upcoming auto-execution."""
    msg = (
        f"[Argus] AUTO-EXECUTE PENDING\n"
        f"Action: {action_type}\n"
        f"Entity: {entity}\n"
        f"Target: {target_description}\n"
        f"Auto-sends in {inspection_minutes} minutes\n"
        f"Reply CANCEL to stop"
    )
    os.system(f'openclaw message send --channel telegram --target "$EWING_TELEGRAM_CHAT_ID" --message "{msg}" 2>/dev/null')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Trust System")
    parser.add_argument("--check", help="Check trust: action_type:entity")
    parser.add_argument("--approve", help="Record approval: action_type:entity")
    parser.add_argument("--reject", help="Record rejection: action_type:entity")
    parser.add_argument("--levels", help="Get all levels for entity")
    parser.add_argument("--history", action="store_true", help="Show trust history")
    args = parser.parse_args()

    if args.check:
        action, entity = args.check.split(":")
        level = get_trust_level(action, entity)
        auto = should_auto_execute(action, entity)
        window = get_inspection_window(action, entity)
        print(json.dumps({"action": action, "entity": entity, "trust_level": level,
                          "auto_execute": auto, "inspection_window_min": window}, indent=2))
    elif args.approve:
        action, entity = args.approve.split(":")
        new_level = record_approval(action, entity)
        print(f"Approved. New trust level: {new_level}")
    elif args.reject:
        action, entity = args.reject.split(":")
        new_level = record_rejection(action, entity)
        print(f"Rejected. New trust level: {new_level}")
    elif args.levels:
        print(json.dumps(get_all_trust_levels(args.levels), indent=2, default=str))
    elif args.history:
        print(json.dumps(get_trust_history(), indent=2, default=str))
