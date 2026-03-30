#!/usr/bin/env python3
"""
linkedin_automation.py — LinkedIn Connection + Message Sequences
Feature #56: Entity-specific connection requests and 3-touch message sequences.
Safety: max 50 connections/day, max 100 messages/day.
"""

import json, os
from datetime import datetime, timedelta

import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ctx = ssl.create_default_context()

DAILY_CONNECTION_LIMIT = 50
DAILY_MESSAGE_LIMIT = 100

def _sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=representation"}

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=_sb_headers(), method="POST")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

# ---------------------------------------------------------------------------
# Connection request templates by entity
# ---------------------------------------------------------------------------
CONNECTION_TEMPLATES = {
    "next_chapter": {
        "template": "Hi {first_name}, I work with {vertical} business owners exploring their options. Noticed {company} — impressive operation. Would love to connect.",
        "tone": "peer_respect",
    },
    "and_capital": {
        "template": "Hi {first_name}, I run AND Capital — we invest in established operating businesses. Your background in {industry} caught my eye. Would value connecting.",
        "tone": "institutional_peer",
    },
    "revsup": {
        "template": "Hi {first_name}, I help growing companies build revenue teams. Looks like {company} is doing great work in {industry}. Let's connect.",
        "tone": "recruiter_partner",
    },
}

# ---------------------------------------------------------------------------
# 3-touch message sequences
# ---------------------------------------------------------------------------
MESSAGE_SEQUENCES = {
    "next_chapter": [
        {
            "touch": 1,
            "type": "connection_request",
            "delay_days": 0,
            "template": CONNECTION_TEMPLATES["next_chapter"]["template"],
        },
        {
            "touch": 2,
            "type": "value_add",
            "delay_days": 3,
            "template": "Thanks for connecting, {first_name}. Thought you might find this interesting — {vertical} M&A activity is up significantly this year. Happy to share what we're seeing in your market if useful.",
        },
        {
            "touch": 3,
            "type": "soft_ask",
            "delay_days": 7,
            "template": "{first_name}, quick question — have you ever thought about what {company} might be worth in today's market? No agenda, just curious. I put together analyses for business owners like you, and the numbers often surprise people. Worth a 15-min call?",
        },
    ],
    "and_capital": [
        {
            "touch": 1,
            "type": "connection_request",
            "delay_days": 0,
            "template": CONNECTION_TEMPLATES["and_capital"]["template"],
        },
        {
            "touch": 2,
            "type": "value_add",
            "delay_days": 3,
            "template": "Good to connect, {first_name}. We recently closed on a {industry} platform — the thesis is working well. Happy to share our perspective on the space if relevant to your work.",
        },
        {
            "touch": 3,
            "type": "soft_ask",
            "delay_days": 7,
            "template": "{first_name}, we're raising our next fund focused on {industry}. Given your background, thought you might want to see the deck. Worth a quick call?",
        },
    ],
    "revsup": [
        {
            "touch": 1,
            "type": "connection_request",
            "delay_days": 0,
            "template": CONNECTION_TEMPLATES["revsup"]["template"],
        },
        {
            "touch": 2,
            "type": "value_add",
            "delay_days": 3,
            "template": "Thanks for connecting, {first_name}. We've been seeing strong demand for {role_type} talent in {industry}. If you're ever looking to build out the team, we have some great candidates in our network.",
        },
        {
            "touch": 3,
            "type": "soft_ask",
            "delay_days": 7,
            "template": "{first_name}, we have 2-3 candidates with strong {industry} backgrounds who might be a fit for {company}. Worth a quick look? Happy to share profiles — no commitment.",
        },
    ],
}


def create_sequence(contact_id, entity):
    """Generate the 3-touch LinkedIn sequence for a contact."""
    contacts = _sb_get("contacts", f"id=eq.{contact_id}&limit=1")
    if not contacts:
        return {"error": f"Contact not found: {contact_id}"}

    contact = contacts[0]
    first_name = contact.get("first_name", "there")
    company = contact.get("company_name", contact.get("company", "your company"))
    vertical = contact.get("vertical", "home services")
    industry = contact.get("industry", vertical)
    role_type = contact.get("role", "sales")

    sequence = MESSAGE_SEQUENCES.get(entity, MESSAGE_SEQUENCES["next_chapter"])
    actions = []

    for step in sequence:
        message = step["template"].format(
            first_name=first_name,
            company=company,
            vertical=vertical,
            industry=industry,
            role_type=role_type,
        )
        send_date = (datetime.utcnow() + timedelta(days=step["delay_days"])).isoformat()

        action = {
            "contact_id": contact_id,
            "entity": entity,
            "touch_number": step["touch"],
            "action_type": step["type"],
            "message_text": message,
            "scheduled_date": send_date,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        actions.append(action)
        _sb_post("linkedin_actions", action)

    return {"contact_id": contact_id, "entity": entity, "touches_created": len(actions)}


def get_pending_actions(entity=None):
    """Get LinkedIn actions due today."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    params = f"status=eq.pending&scheduled_date=lte.{today}T23:59:59&order=scheduled_date.asc"
    if entity:
        params += f"&entity=eq.{entity}"
    return _sb_get("linkedin_actions", params)


def log_action(contact_id, action_type, status, response=None):
    """Track LinkedIn action outcome."""
    return _sb_post("linkedin_actions", {
        "contact_id": contact_id,
        "action_type": action_type,
        "status": status,
        "response": response,
        "completed_at": datetime.utcnow().isoformat(),
    })


def get_daily_counts():
    """Get today's connection and message counts for rate limiting."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    connections = _sb_get("linkedin_actions",
        f"action_type=eq.connection_request&status=eq.sent&completed_at=gte.{today}T00:00:00&select=id")
    messages = _sb_get("linkedin_actions",
        f"action_type=neq.connection_request&status=eq.sent&completed_at=gte.{today}T00:00:00&select=id")
    return {
        "connections_today": len(connections),
        "messages_today": len(messages),
        "connections_remaining": DAILY_CONNECTION_LIMIT - len(connections),
        "messages_remaining": DAILY_MESSAGE_LIMIT - len(messages),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LinkedIn Automation")
    parser.add_argument("--create", help="Create sequence: contact_id:entity")
    parser.add_argument("--pending", help="Get pending actions for entity")
    parser.add_argument("--limits", action="store_true", help="Show daily limits")
    args = parser.parse_args()

    if args.create:
        cid, entity = args.create.split(":")
        print(json.dumps(create_sequence(cid, entity), indent=2, default=str))
    elif args.pending:
        print(json.dumps(get_pending_actions(args.pending), indent=2, default=str))
    elif args.limits:
        print(json.dumps(get_daily_counts(), indent=2))
