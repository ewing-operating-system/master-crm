#!/usr/bin/env python3
"""
Activity Feed — master-crm
Aggregates activity and guardrail violations for the "While You Were Away" dashboard.

Public API
----------
get_activity_since(last_seen_at, entity=None)
    Returns grouped activity events since the given timestamp.

get_guardrail_violations(since=None, severity=None)
    Returns guardrail violation rows, newest first.

log_guardrail_violation(violation_type, entity, target_id, details, severity)
    Writes a violation record to the guardrail_violations table.

update_last_seen(user_id)
    Stamps user_sessions with the current UTC time.

get_last_seen(user_id)
    Returns the last_seen_at timestamp for a user (or epoch if never seen).
"""

import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)
_ctx = ssl.create_default_context()


def _headers(prefer: Optional[str] = None) -> dict:
    h = {
        "apikey": _KEY,
        "Authorization": f"Bearer {_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _get(table: str, params: str = "") -> list:
    url = f"{_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_headers())
    try:
        resp = urllib.request.urlopen(req, context=_ctx)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GET {table} failed {e.code}: {body}") from e


def _post(table: str, data: dict, prefer: str = "return=representation") -> list:
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{_URL}/rest/v1/{table}",
        data=payload,
        headers=_headers(prefer),
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, context=_ctx)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"POST {table} failed {e.code}: {body}") from e


def _patch(table: str, params: str, data: dict) -> None:
    payload = json.dumps(data, default=str).encode()
    url = f"{_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(
        url, data=payload, headers=_headers("return=minimal"), method="PATCH"
    )
    try:
        urllib.request.urlopen(req, context=_ctx)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PATCH {table} failed {e.code}: {body}") from e


# ---------------------------------------------------------------------------
# Violation constants
# ---------------------------------------------------------------------------
VIOLATION_TYPES = {
    "dnc_bypass",
    "entity_misroute",
    "cost_overspend",
    "hallucination_flag",
    "trust_threshold",
    "rate_limit",
    "schema_violation",
}

SEVERITY_LEVELS = {
    "critical",   # blocked — action was prevented
    "warning",    # logged — action was allowed but flagged
    "info",       # noted — informational only
}

# ---------------------------------------------------------------------------
# Category config used by the frontend and aggregation
# ---------------------------------------------------------------------------
CATEGORIES = {
    "letters":   {"label": "Letters",   "color": "#27ae60", "icon": "✉"},
    "calls":     {"label": "Calls",     "color": "#58a6ff", "icon": "📞"},
    "research":  {"label": "Research",  "color": "#a855f7", "icon": "🔬"},
    "plays":     {"label": "Plays",     "color": "#f39c12", "icon": "🎯"},
    "costs":     {"label": "Costs",     "color": "#e74c3c", "icon": "💰"},
    "alerts":    {"label": "Alerts",    "color": "#dc3545", "icon": "🚨"},
}


# ---------------------------------------------------------------------------
# User sessions
# ---------------------------------------------------------------------------

def get_last_seen(user_id: str) -> datetime:
    """Return last_seen_at for user_id, or epoch if no record exists."""
    rows = _get("user_sessions", f"user_id=eq.{user_id}&select=last_seen_at")
    if rows and rows[0].get("last_seen_at"):
        ts = rows[0]["last_seen_at"].replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def update_last_seen(user_id: str) -> datetime:
    """Upsert user_sessions.last_seen_at = now(). Returns the new timestamp."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Try update first; insert if no row exists.
    existing = _get("user_sessions", f"user_id=eq.{user_id}&select=user_id")
    if existing:
        _patch("user_sessions", f"user_id=eq.{user_id}", {"last_seen_at": now_iso})
    else:
        _post(
            "user_sessions",
            {"user_id": user_id, "last_seen_at": now_iso},
            prefer="return=minimal",
        )
    return now


# ---------------------------------------------------------------------------
# Core: aggregate activity since a timestamp
# ---------------------------------------------------------------------------

def get_activity_since(
    last_seen_at: datetime, entity: Optional[str] = None
) -> dict:
    """
    Aggregate activity events from multiple tables since last_seen_at.

    Returns:
        {
            "since": ISO timestamp,
            "total": int,
            "categories": {
                "letters":  [event, ...],
                "calls":    [event, ...],
                "research": [event, ...],
                "plays":    [event, ...],
                "costs":    [event, ...],
                "alerts":   [event, ...],
            },
            "highlights": [event, ...],   # unusual / high-urgency events
        }
    """
    since_iso = last_seen_at.isoformat().replace("+00:00", "Z")
    entity_filter = f"&entity=eq.{entity}" if entity else ""

    result: dict = {
        "since": since_iso,
        "categories": {k: [] for k in CATEGORIES},
        "highlights": [],
    }

    # ---- step_log → Letters + Calls + Research --------------------------
    try:
        step_rows = _get(
            "step_log",
            f"created_at=gt.{since_iso}{entity_filter}"
            f"&select=id,created_at,step_type,status,entity,target_id,notes"
            f"&order=created_at.desc&limit=200",
        )
        for row in step_rows:
            step = (row.get("step_type") or "").lower()
            status = (row.get("status") or "").lower()
            entity_tag = row.get("entity", "")
            ts = row.get("created_at", "")
            target = row.get("target_id", "")
            notes = row.get("notes", "")

            if "letter" in step or "mail" in step or "lob" in step:
                cat = "letters"
                desc = f"Letter {status}"
                if target:
                    desc += f" for {target}"
            elif "call" in step or "dial" in step or "salesfinity" in step:
                cat = "calls"
                desc = f"Call {status}"
                if target:
                    desc += f" — {target}"
            elif "research" in step or "page" in step or "exa" in step or "buyer" in step:
                cat = "research"
                desc = f"Research: {step} [{status}]"
                if target:
                    desc += f" — {target}"
            else:
                continue  # unrecognised step type — skip

            event = _make_event(ts, cat, desc, entity_tag, target, notes)
            result["categories"][cat].append(event)
    except RuntimeError:
        pass  # table may not exist yet

    # ---- plays → Plays --------------------------------------------------
    try:
        play_rows = _get(
            "plays",
            f"created_at=gt.{since_iso}{entity_filter}"
            f"&select=id,created_at,play_type,status,entity,target_id,urgency"
            f"&order=created_at.desc&limit=100",
        )
        for row in play_rows:
            ts = row.get("created_at", "")
            play_type = row.get("play_type") or "play"
            status = row.get("status") or ""
            entity_tag = row.get("entity", "")
            target = row.get("target_id", "")
            urgency = (row.get("urgency") or "").lower()
            desc = f"Play created: {play_type}"
            if status:
                desc += f" [{status}]"
            if target:
                desc += f" — {target}"
            event = _make_event(ts, "plays", desc, entity_tag, target)
            result["categories"]["plays"].append(event)
            if urgency in ("high", "urgent"):
                event["highlight_reason"] = f"High-urgency play: {play_type}"
                result["highlights"].append(event)
    except RuntimeError:
        pass

    # ---- page_versions → Research ---------------------------------------
    try:
        pv_rows = _get(
            "page_versions",
            f"created_at=gt.{since_iso}{entity_filter}"
            f"&select=id,created_at,page_slug,version,entity,changed_by"
            f"&order=created_at.desc&limit=100",
        )
        for row in pv_rows:
            ts = row.get("created_at", "")
            slug = row.get("page_slug", "")
            ver = row.get("version", "")
            entity_tag = row.get("entity", "")
            desc = f"Page rebuilt: {slug} (v{ver})"
            event = _make_event(ts, "research", desc, entity_tag, slug)
            result["categories"]["research"].append(event)
    except RuntimeError:
        pass

    # ---- cost_ledger / cost_log → Costs ---------------------------------
    for cost_table in ("cost_ledger", "cost_log"):
        try:
            cost_rows = _get(
                cost_table,
                f"created_at=gt.{since_iso}{entity_filter}"
                f"&select=id,created_at,service,cost_usd,entity,notes"
                f"&order=created_at.desc&limit=200",
            )
            for row in cost_rows:
                ts = row.get("created_at", "")
                service = row.get("service") or row.get("tool") or "unknown"
                cost = row.get("cost_usd") or row.get("cost") or 0
                entity_tag = row.get("entity", "")
                notes = row.get("notes", "")
                desc = f"Cost logged: {service} ${cost:.4f}"
                event = _make_event(ts, "costs", desc, entity_tag, service, notes)
                result["categories"]["costs"].append(event)
                # Highlight cost spikes (> $1.00 single entry)
                try:
                    if float(cost) > 1.0:
                        event["highlight_reason"] = f"Cost spike: {service} ${cost}"
                        result["highlights"].append(event)
                except (TypeError, ValueError):
                    pass
            break  # only read one of the two cost tables
        except RuntimeError:
            continue

    # ---- guardrail_violations → Alerts ----------------------------------
    try:
        viol_rows = get_guardrail_violations(since=last_seen_at)
        if entity:
            viol_rows = [r for r in viol_rows if r.get("entity") == entity]
        for row in viol_rows:
            ts = row.get("created_at", "")
            vtype = row.get("violation_type", "")
            sev = row.get("severity", "")
            entity_tag = row.get("entity", "")
            target = row.get("target_id", "")
            details = row.get("details", "")
            desc = f"Guardrail: {vtype} [{sev}]"
            if target:
                desc += f" — {target}"
            event = _make_event(ts, "alerts", desc, entity_tag, target, details)
            event["severity"] = sev
            event["violation_type"] = vtype
            result["categories"]["alerts"].append(event)
            if sev == "critical":
                event["highlight_reason"] = f"Critical violation: {vtype}"
                result["highlights"].append(event)
    except RuntimeError:
        pass

    # ---- DNC hits → Alerts (from step_log status=dnc_blocked) ----------
    try:
        dnc_rows = _get(
            "step_log",
            f"created_at=gt.{since_iso}&status=eq.dnc_blocked{entity_filter}"
            f"&select=id,created_at,entity,target_id,notes"
            f"&order=created_at.desc&limit=50",
        )
        for row in dnc_rows:
            ts = row.get("created_at", "")
            entity_tag = row.get("entity", "")
            target = row.get("target_id", "")
            desc = f"DNC hit — outreach blocked for {target}"
            event = _make_event(ts, "alerts", desc, entity_tag, target)
            event["highlight_reason"] = "DNC hit"
            result["categories"]["alerts"].append(event)
            result["highlights"].append(event)
    except RuntimeError:
        pass

    # ---- deduplicate highlights (same id can appear from multiple sources)
    seen_ids: set = set()
    deduped = []
    for ev in result["highlights"]:
        eid = ev.get("id")
        if eid not in seen_ids:
            seen_ids.add(eid)
            deduped.append(ev)
    result["highlights"] = deduped

    total = sum(len(v) for v in result["categories"].values())
    result["total"] = total
    return result


# ---------------------------------------------------------------------------
# Guardrail violations
# ---------------------------------------------------------------------------

def get_guardrail_violations(
    since: Optional[datetime] = None,
    severity: Optional[str] = None,
) -> list:
    """
    Return guardrail violation rows, newest first.

    Args:
        since:    Only return violations after this datetime.
        severity: Filter to a specific severity level.
    """
    params = "order=created_at.desc&limit=500"
    if since:
        since_iso = since.isoformat().replace("+00:00", "Z")
        params += f"&created_at=gt.{since_iso}"
    if severity:
        if severity not in SEVERITY_LEVELS:
            raise ValueError(f"severity must be one of {SEVERITY_LEVELS}")
        params += f"&severity=eq.{severity}"
    return _get("guardrail_violations", params)


def log_guardrail_violation(
    violation_type: str,
    entity: str,
    target_id: str,
    details: str,
    severity: str,
) -> dict:
    """
    Write a guardrail violation record.

    Args:
        violation_type: One of VIOLATION_TYPES.
        entity:         Entity tag (e.g. 'next_chapter', 'and_capital').
        target_id:      ID or name of the record/operation that triggered the violation.
        details:        Free-text description of what happened and what was blocked.
        severity:       One of SEVERITY_LEVELS.

    Returns:
        The inserted row dict.
    """
    if violation_type not in VIOLATION_TYPES:
        raise ValueError(
            f"violation_type '{violation_type}' not recognised. "
            f"Must be one of: {sorted(VIOLATION_TYPES)}"
        )
    if severity not in SEVERITY_LEVELS:
        raise ValueError(
            f"severity '{severity}' not recognised. "
            f"Must be one of: {sorted(SEVERITY_LEVELS)}"
        )

    row = {
        "violation_type": violation_type,
        "entity": entity,
        "target_id": target_id,
        "details": details,
        "severity": severity,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = _post("guardrail_violations", row)
    return result[0] if isinstance(result, list) else result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(
    ts: str,
    category: str,
    description: str,
    entity: str,
    target_id: str = "",
    notes: str = "",
) -> dict:
    return {
        "id": f"{category}:{ts}:{target_id}",
        "timestamp": ts,
        "category": category,
        "category_label": CATEGORIES[category]["label"],
        "category_color": CATEGORIES[category]["color"],
        "category_icon": CATEGORIES[category]["icon"],
        "description": description,
        "entity": entity,
        "target_id": target_id,
        "notes": notes,
    }


def get_violation_trend(days: int = 7) -> list:
    """
    Return daily violation counts for the last `days` days.

    Returns:
        [{"date": "2026-03-24", "critical": 2, "warning": 5, "info": 1}, ...]
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = get_guardrail_violations(since=since)

    # Group by date and severity
    buckets: dict = {}
    for row in rows:
        ts = row.get("created_at", "")
        if not ts:
            continue
        date_str = ts[:10]  # YYYY-MM-DD
        sev = row.get("severity", "info")
        if date_str not in buckets:
            buckets[date_str] = {"date": date_str, "critical": 0, "warning": 0, "info": 0}
        if sev in buckets[date_str]:
            buckets[date_str][sev] += 1

    return sorted(buckets.values(), key=lambda x: x["date"])
