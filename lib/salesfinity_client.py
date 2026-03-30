#!/usr/bin/env python3
"""
salesfinity_client.py — Salesfinity parallel dialer integration for Master CRM.

Handles contact loading, call outcome fetching, and Supabase sync.
6 pre-load gates enforced before any contact touches the dialer.
Rate limit: max 50 contacts per load operation.

Uses urllib (no external deps). Reads SALESFINITY_API_URL + SALESFINITY_API_KEY from env.
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

SALESFINITY_API_URL = os.environ.get("SALESFINITY_API_URL", "https://api.salesfinity.io/v1")
SALESFINITY_API_KEY = os.environ.get("SALESFINITY_API_KEY", "")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")

MAX_CONTACTS_PER_LOAD = 50

# Valid US state codes for geography filter
US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
}

# Call outcome classification map — maps raw Salesfinity dispositions to canonical codes
OUTCOME_MAP = {
    # Connected
    "answered": "connected",
    "connected": "connected",
    "conversation": "connected",
    "live_answer": "connected",
    # Voicemail
    "voicemail": "voicemail",
    "left_voicemail": "voicemail",
    "vm": "voicemail",
    # Gatekeeper
    "gatekeeper": "gatekeeper",
    "receptionist": "gatekeeper",
    "transfer_failed": "gatekeeper",
    # Bad number
    "bad_number": "bad_number",
    "wrong_number": "bad_number",
    "disconnected": "bad_number",
    "not_in_service": "bad_number",
    "invalid_number": "bad_number",
    # No answer
    "no_answer": "no_answer",
    "ring_no_answer": "no_answer",
    "busy": "no_answer",
    "not_available": "no_answer",
    "callback": "no_answer",
}

ctx = ssl.create_default_context()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _sf_headers():
    """Salesfinity API auth headers."""
    return {
        "Authorization": f"Bearer {SALESFINITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _sb_headers(prefer=None):
    """Supabase REST headers."""
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _sf_get(path):
    """GET from Salesfinity API."""
    url = f"{SALESFINITY_API_URL}/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers=_sf_headers())
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _sf_post(path, data):
    """POST to Salesfinity API."""
    url = f"{SALESFINITY_API_URL}/{path.lstrip('/')}"
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers=_sf_headers(), method="POST")
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _sb_get(table, params=""):
    """GET rows from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _sb_insert(table, data):
    """Insert row into Supabase."""
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=payload,
        headers=_sb_headers("return=representation"),
        method="POST",
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _sb_upsert(table, data):
    """Upsert row into Supabase (merge on conflict)."""
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=payload,
        headers=_sb_headers("return=representation,resolution=merge-duplicates"),
        method="POST",
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    return json.loads(resp.read())


def _normalize_phone(phone):
    """Strip formatting from phone number for DNC lookup."""
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


# ── Gate 1: DNC table check ───────────────────────────────────────────────────

def _gate_dnc_table(phone):
    """Check universal do_not_call table. Returns (blocked, reason)."""
    normalized = _normalize_phone(phone)
    for value in [phone, normalized, f"+1{normalized}"]:
        results = _sb_get("do_not_call", f"phone=eq.{urllib.parse.quote(str(value))}")
        if results:
            return True, f"DNC table match: {value}"
    return False, ""


# ── Gate 2: DNC flag on contact record ───────────────────────────────────────

def _gate_dnc_flag(contact):
    """Check dnc_flag field on the contact dict itself."""
    if contact.get("dnc_flag") or contact.get("do_not_call"):
        return True, "Contact dnc_flag=true"
    return False, ""


# ── Gate 3: Dedup across existing Salesfinity lists ──────────────────────────

def _gate_dedup(phone, existing_phones):
    """Reject if phone already exists in any loaded Salesfinity list."""
    normalized = _normalize_phone(phone)
    if normalized in existing_phones:
        return True, f"Duplicate phone across Salesfinity lists: {normalized}"
    return False, ""


# ── Gate 4: Geography filter (US only) ───────────────────────────────────────

def _gate_geography(contact, us_only=True):
    """Reject non-US contacts if us_only=True."""
    if not us_only:
        return False, ""
    state = (contact.get("state") or contact.get("address_state") or "").strip().upper()
    country = (contact.get("country") or "US").strip().upper()
    if country not in ("US", "USA", "UNITED STATES"):
        return True, f"Non-US country: {country}"
    if state and state not in US_STATES:
        return True, f"Non-US state code: {state}"
    return False, ""


# ── Gate 5: Phone number required ────────────────────────────────────────────

def _gate_phone_required(contact):
    """Reject if no phone number present."""
    phone = contact.get("phone") or contact.get("cell_phone") or contact.get("phone_number") or ""
    if not phone or not _normalize_phone(str(phone)):
        return True, "No phone number"
    return False, ""


# ── Gate 6: Naming convention enforcement ────────────────────────────────────

def _gate_naming_convention(list_name):
    """Enforce entity prefix on list name: NC-, AND-, RU-."""
    valid_prefixes = ("NC-", "AND-", "RU-", "FORGE-", "BIOLEV-", "SEASWEET-")
    if not any(list_name.upper().startswith(p) for p in valid_prefixes):
        return True, (
            f"List name '{list_name}' must start with entity prefix "
            f"({', '.join(valid_prefixes)})"
        )
    return False, ""


# ── Pre-load gate runner ──────────────────────────────────────────────────────

def run_pre_load_gates(contacts, list_name, existing_phones=None, us_only=True):
    """
    Run all 6 pre-load gates against a contact list.

    Returns (approved_contacts, rejected_contacts).
    Each rejected contact has a 'rejection_reason' field added.
    """
    if existing_phones is None:
        existing_phones = set()

    # Gate 6 (naming) applies to the whole batch — fail fast
    blocked, reason = _gate_naming_convention(list_name)
    if blocked:
        raise ValueError(f"Naming convention gate failed: {reason}")

    approved = []
    rejected = []

    for contact in contacts:
        phone = str(
            contact.get("phone") or contact.get("cell_phone") or contact.get("phone_number") or ""
        )

        gates = [
            _gate_phone_required(contact),
            _gate_dnc_flag(contact),
            _gate_geography(contact, us_only=us_only),
        ]

        # Phone-dependent gates
        if phone:
            gates += [
                _gate_dnc_table(phone),
                _gate_dedup(phone, existing_phones),
            ]

        blocked_reason = next((r for ok, r in gates if ok), None)

        if blocked_reason:
            rejected.append({**contact, "rejection_reason": blocked_reason})
        else:
            approved.append(contact)
            if phone:
                existing_phones.add(_normalize_phone(phone))

    return approved, rejected


# ── Fetch existing Salesfinity phones for dedup ───────────────────────────────

def _get_existing_salesfinity_phones():
    """Pull all phone numbers already loaded in Salesfinity for dedup."""
    try:
        lists_data = _sf_get("/lists")
        lists = lists_data.get("data") or (lists_data if isinstance(lists_data, list) else [])
        phones = set()
        for sf_list in lists:
            list_id = sf_list.get("id")
            if not list_id:
                continue
            try:
                contacts_data = _sf_get(f"/lists/{list_id}/contacts")
                contacts = (
                    contacts_data.get("data") or contacts_data
                    if isinstance(contacts_data, list) else []
                )
                for c in contacts:
                    p = str(c.get("phone") or c.get("phone_number") or "")
                    if p:
                        phones.add(_normalize_phone(p))
            except Exception:
                pass
        return phones
    except Exception:
        return set()


# ── Public API ────────────────────────────────────────────────────────────────

def load_contacts_to_dialer(contacts, list_name, us_only=True):
    """
    Push contacts to Salesfinity after passing all 6 pre-load gates.

    Args:
        contacts: List of contact dicts. Each must have: phone, first_name, last_name,
                  company_name. Optional: email, state, country, entity, dnc_flag.
        list_name: Salesfinity list name. MUST start with entity prefix (NC-, AND-, RU-).
        us_only:   If True, rejects non-US contacts (default True).

    Returns:
        {
          "list_id": str,
          "list_name": str,
          "loaded": int,
          "rejected": int,
          "rejection_log": list,
        }
    """
    if not SALESFINITY_API_KEY:
        raise EnvironmentError("SALESFINITY_API_KEY not set.")

    if len(contacts) > MAX_CONTACTS_PER_LOAD:
        raise ValueError(
            f"Rate limit: max {MAX_CONTACTS_PER_LOAD} contacts per load. "
            f"Got {len(contacts)}. Split into batches."
        )

    existing_phones = _get_existing_salesfinity_phones()

    approved, rejected = run_pre_load_gates(
        contacts, list_name, existing_phones=existing_phones, us_only=us_only
    )

    rejection_log = [
        {
            "name": f"{r.get('first_name','')} {r.get('last_name','')}".strip(),
            "company": r.get("company_name", ""),
            "reason": r.get("rejection_reason", "unknown"),
        }
        for r in rejected
    ]

    if not approved:
        return {
            "list_id": None,
            "list_name": list_name,
            "loaded": 0,
            "rejected": len(rejected),
            "rejection_log": rejection_log,
        }

    # Format contacts for Salesfinity payload
    sf_contacts = []
    for c in approved:
        phone = str(c.get("phone") or c.get("cell_phone") or c.get("phone_number") or "")
        sf_contacts.append({
            "firstName": c.get("first_name", ""),
            "lastName": c.get("last_name", ""),
            "phone": phone,
            "email": c.get("email", ""),
            "companyName": c.get("company_name", ""),
            "customFields": {
                "entity": c.get("entity", ""),
                "crm_id": str(c.get("id") or c.get("contact_id") or ""),
            },
        })

    list_payload = {"name": list_name, "contacts": sf_contacts}
    result = _sf_post("/lists", list_payload)
    list_id = result.get("id") or result.get("list_id") or (result.get("data") or {}).get("id")

    # Log to cost_log
    try:
        entity_prefix = list_name.split("-")[0].lower() if "-" in list_name else "unknown"
        entity_map = {"nc": "next_chapter", "and": "and_capital", "ru": "revsup"}
        entity = entity_map.get(entity_prefix, entity_prefix)
        _sb_insert("cost_log", {
            "entity": entity,
            "operation": "salesfinity_load",
            "model": "salesfinity_api",
            "cost_usd": 0.0,
            "metadata": json.dumps({
                "list_name": list_name,
                "loaded": len(approved),
                "rejected": len(rejected),
            }),
        })
    except Exception:
        pass

    return {
        "list_id": list_id,
        "list_name": list_name,
        "loaded": len(approved),
        "rejected": len(rejected),
        "rejection_log": rejection_log,
    }


def get_call_outcomes(list_id):
    """
    Fetch call results for a Salesfinity list.

    Returns list of outcome dicts with canonical classification applied:
      contact_id, first_name, last_name, company_name, phone,
      raw_disposition, outcome, called_at, duration_seconds, notes, entity
    """
    if not SALESFINITY_API_KEY:
        raise EnvironmentError("SALESFINITY_API_KEY not set.")

    data = _sf_get(f"/lists/{list_id}/calls")
    calls = data.get("data") or (data if isinstance(data, list) else [])

    outcomes = []
    for call in calls:
        raw_disp = (call.get("disposition") or call.get("outcome") or "no_answer").lower()
        canonical = OUTCOME_MAP.get(raw_disp, "no_answer")

        outcomes.append({
            "contact_id": call.get("contactId") or call.get("contact_id"),
            "first_name": call.get("firstName") or call.get("first_name", ""),
            "last_name": call.get("lastName") or call.get("last_name", ""),
            "company_name": call.get("companyName") or call.get("company_name", ""),
            "phone": call.get("phone") or call.get("phoneNumber", ""),
            "raw_disposition": raw_disp,
            "outcome": canonical,
            "called_at": call.get("calledAt") or call.get("created_at") or call.get("timestamp"),
            "duration_seconds": call.get("durationSeconds") or call.get("duration", 0),
            "notes": call.get("notes") or call.get("agentNotes", ""),
            "entity": (call.get("customFields") or {}).get("entity", ""),
            "list_id": list_id,
        })

    return outcomes


def sync_outcomes_to_supabase(outcomes):
    """
    Write call outcomes to the `plays` table in Supabase.

    Each outcome becomes a play record:
      play_type = 'call_outcome', source = 'salesfinity'

    Auto-adds DNC entries when call notes contain DNC requests.

    Returns: {"synced": int, "errors": int, "error_log": list}
    """
    synced = 0
    errors = 0
    error_log = []

    status_map = {
        "connected": "connected",
        "voicemail": "voicemail_left",
        "gatekeeper": "gatekeeper_blocked",
        "bad_number": "bad_number",
        "no_answer": "no_answer",
    }

    for outcome in outcomes:
        entity = outcome.get("entity") or "next_chapter"
        play_status = status_map.get(outcome.get("outcome", "no_answer"), "no_answer")

        # Auto-DNC detection from call notes
        notes_lower = (outcome.get("notes") or "").lower()
        if any(p in notes_lower for p in ("do not call", "dnc", "remove me", "take me off")):
            try:
                phone = outcome.get("phone", "")
                if phone:
                    _sb_upsert("do_not_call", {
                        "phone": phone,
                        "source": "salesfinity_call_note",
                        "notes": outcome.get("notes", ""),
                        "added_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                error_log.append({
                    "contact": outcome.get("company_name"),
                    "error": f"DNC insert failed: {e}",
                })

        play_record = {
            "entity": entity,
            "play_type": "call_outcome",
            "status": play_status,
            "source": "salesfinity",
            "contact_first_name": outcome.get("first_name", ""),
            "contact_last_name": outcome.get("last_name", ""),
            "contact_company": outcome.get("company_name", ""),
            "contact_phone": outcome.get("phone", ""),
            "raw_disposition": outcome.get("raw_disposition", ""),
            "outcome": outcome.get("outcome", ""),
            "called_at": outcome.get("called_at"),
            "duration_seconds": outcome.get("duration_seconds", 0),
            "notes": outcome.get("notes", ""),
            "salesfinity_list_id": outcome.get("list_id", ""),
            "salesfinity_contact_id": str(outcome.get("contact_id") or ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            _sb_insert("plays", play_record)
            synced += 1
        except Exception as e:
            errors += 1
            error_log.append({
                "contact": outcome.get("company_name", "unknown"),
                "error": str(e),
            })

    return {"synced": synced, "errors": errors, "error_log": error_log}


def get_active_lists():
    """Fetch all active Salesfinity lists with metadata."""
    if not SALESFINITY_API_KEY:
        raise EnvironmentError("SALESFINITY_API_KEY not set.")
    data = _sf_get("/lists")
    return data.get("data") or (data if isinstance(data, list) else [])


def get_list_stats(list_id):
    """Get call outcome totals for a specific list."""
    outcomes = get_call_outcomes(list_id)
    stats = {
        "total_calls": len(outcomes),
        "connected": 0,
        "voicemail": 0,
        "gatekeeper": 0,
        "bad_number": 0,
        "no_answer": 0,
    }
    for o in outcomes:
        key = o.get("outcome", "no_answer")
        if key in stats:
            stats[key] += 1
    total = stats["total_calls"]
    stats["connect_rate"] = round(stats["connected"] / total * 100, 1) if total else 0.0
    return stats


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("salesfinity_client.py — configuration check")
    print(f"  API URL:  {SALESFINITY_API_URL}")
    print(f"  API Key:  {'SET' if SALESFINITY_API_KEY else 'MISSING — set SALESFINITY_API_KEY'}")
    print(f"  Max load: {MAX_CONTACTS_PER_LOAD} contacts per call")
    print(f"  Outcomes: {len(set(OUTCOME_MAP.values()))} canonical types")
    print()
    print("  Pre-load gates:")
    print("    1. DNC table check (universal do_not_call)")
    print("    2. DNC flag on contact record")
    print("    3. Dedup across existing Salesfinity lists")
    print("    4. Geography filter (US only by default)")
    print("    5. Phone number required")
    print("    6. Naming convention (NC-, AND-, RU- prefix)")
