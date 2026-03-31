#!/usr/bin/env python3
"""
Feature #46 — Research Method Learning

When Mark corrects a fact (comment_type='fact_correction'), this module:
  1. Extracts the research gap pattern (what was wrong → what source was right)
  2. Proposes a new research_method entry with status='staged'
  3. Provides an approval gate before the method becomes active

Staged methods are never auto-applied — they sit in the 'staged' queue
until approved via approve_method() or the research-learning dashboard.

research_methods table columns (confirmed from live data):
  id, method_code, method_name, description, category, tool,
  query_template, expected_output, success_rate, avg_cost,
  discovered_by, discovery_context, is_active, created_at, updated_at,
  times_used, times_succeeded

Status is encoded via is_active + a soft 'status' column if added, otherwise:
  staged  → is_active = False, discovery_context starts with "[STAGED]"
  active  → is_active = True
  retired → is_active = False, discovery_context starts with "[RETIRED]"

NOTE: The table may not have a 'status' column yet. This module uses
      is_active + a [STAGED]/[RETIRED] prefix in discovery_context
      as a portable status pattern that works without a schema migration.
      If a 'status' column is later added, update _status_filter().
"""

import json
import logging
import os
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "research_learner.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("research_learner")

# ---------------------------------------------------------------------------
# Supabase — master-crm (service role)
# ---------------------------------------------------------------------------
_ctx = ssl.create_default_context()

SUPA_URL = "https://dwrnfpjcvydhmhnvyzov.supabase.co"
SUPA_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)

OPENROUTER_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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",
)
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

STAGED_PREFIX = "[STAGED]"
RETIRED_PREFIX = "[RETIRED]"


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _headers(prefer=None):
    h = {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def supa_get(table, params=""):
    url = f"{SUPA_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_headers())
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


def supa_patch(table, row_filter, updates):
    url = f"{SUPA_URL}/rest/v1/{table}?{row_filter}"
    payload = json.dumps(updates, default=str).encode()
    req = urllib.request.Request(
        url, data=payload, headers=_headers("return=representation"), method="PATCH"
    )
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


def supa_insert(table, data):
    url = f"{SUPA_URL}/rest/v1/{table}"
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        url, data=payload, headers=_headers("return=representation"), method="POST"
    )
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def _ask_claude_cli(prompt, timeout=120):
    try:
        result = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception:
        return None


def _ask_openrouter(prompt, max_tokens=800):
    try:
        body = json.dumps({
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }).encode()
        req = urllib.request.Request(
            OPENROUTER_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://master-crm.app",
                "X-Title": "Master CRM Research Learner",
            },
            method="POST",
        )
        resp = urllib.request.urlopen(req, context=_ctx, timeout=60)
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip() or None
    except Exception as e:
        log.warning(f"OpenRouter call failed: {e}")
        return None


def _call_llm(prompt):
    """Claude CLI → OpenRouter DeepSeek V3. Returns text or None."""
    result = _ask_claude_cli(prompt)
    if result:
        return result
    return _ask_openrouter(prompt)


def _parse_json_from_llm(text):
    """Strip markdown fences and parse JSON from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Drop first line (```json or ```) and last (```)
        cleaned = "\n".join(lines[1:]).rsplit("```", 1)[0].strip()
    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def extract_learning(comment_id):
    """
    Analyze a fact_correction comment to find the research gap.

    Returns a learning dict:
        {
          "comment_id": str,
          "what_was_wrong": str,
          "correct_fact": str,
          "source_described": str,
          "suggested_method_code": str,
          "suggested_method_name": str,
          "query_template": str,
          "category": str,
          "tool": str,
          "description": str,
          "entity": str | None,
          "commenter": str,
          "company_name": str,
        }

    Returns None if the comment is not a fact_correction or LLM extraction fails.
    """
    rows = supa_get("page_comments", f"id=eq.{comment_id}&select=*")
    if not rows:
        log.warning(f"extract_learning: comment {comment_id} not found")
        return None

    comment = rows[0]
    if comment.get("comment_type") != "fact_correction":
        log.info(f"extract_learning: comment {comment_id} is not a fact_correction, skipping")
        return None

    comment_text = comment.get("comment_text", "")
    user_response = comment.get("user_response", "")
    commenter = comment.get("commenter", "unknown")
    company = comment.get("company_name", "")
    section = comment.get("section_id", "")

    prompt = (
        "A user corrected a fact on a company dossier. Analyze the correction "
        "to identify a reusable research method that would have found the right "
        "information in the first place.\n\n"
        f"Company: {company}\n"
        f"Section: {section}\n"
        f"What the dossier said (wrong): {comment_text}\n"
        f"User's source / explanation: {user_response or '(no additional context provided)'}\n\n"
        "Return a JSON object with these exact keys:\n"
        "  what_was_wrong       — one sentence describing the incorrect fact\n"
        "  correct_fact         — what the correct fact is\n"
        "  source_described     — what data source the user pointed to\n"
        "  suggested_method_code — snake_case identifier (e.g. state_filing_search)\n"
        "  suggested_method_name — human-readable name\n"
        "  query_template       — how to run this search for any company; use "
        "{company_name}, {owner_name}, {city}, {state} as placeholders\n"
        "  category             — one of: company_search, person_search, financial_search, "
        "legal_search, news_search, contact_search, manual\n"
        "  tool                 — one of: exa, google, linkedin, sec_edgar, state_filings, "
        "phone_call, email, manual\n"
        "  description          — one sentence: what this method finds\n\n"
        "Return ONLY valid JSON, no markdown fences."
    )

    result = _call_llm(prompt)
    if not result:
        log.error(f"extract_learning: LLM failed for comment {comment_id}")
        return None

    try:
        extracted = _parse_json_from_llm(result)
    except (json.JSONDecodeError, ValueError) as e:
        log.error(f"extract_learning: JSON parse failed: {e} | raw: {result[:300]}")
        return None

    learning = {
        "comment_id": comment_id,
        "commenter": commenter,
        "company_name": company,
        "entity": "next_chapter",  # most dossier corrections are NC
        **extracted,
    }
    log.info(
        f"extract_learning: extracted '{learning.get('suggested_method_code')}' "
        f"from comment {comment_id} ({commenter})"
    )
    return learning


def propose_method(learning):
    """
    Create a staged research_method entry from a learning dict.

    Staged methods have is_active=False and discovery_context prefixed
    with [STAGED] so the dashboard can filter them.

    Returns the inserted row dict, or None if method_code already exists.
    """
    method_code = learning.get("suggested_method_code", "")
    if not method_code:
        log.warning("propose_method: no method_code in learning dict")
        return None

    # Idempotency check — skip if any version already exists
    existing = supa_get("research_methods", f"method_code=eq.{method_code}")
    if existing:
        log.info(f"propose_method: method_code '{method_code}' already exists, skipping")
        return None

    context = (
        f"{STAGED_PREFIX} Discovered by {learning.get('commenter', 'unknown')} "
        f"correcting {learning.get('company_name', '')} | "
        f"Comment ID: {learning.get('comment_id', '')}"
    )

    row = {
        "method_code": method_code,
        "method_name": learning.get("suggested_method_name", method_code),
        "description": learning.get("description", ""),
        "category": learning.get("category", "manual"),
        "tool": learning.get("tool", "manual"),
        "query_template": learning.get("query_template", ""),
        "expected_output": [],
        "success_rate": 0.0,
        "avg_cost": 0.0,
        "times_used": 0,
        "times_succeeded": 0,
        "is_active": False,  # staged — not active until approved
        "discovered_by": learning.get("commenter", "system"),
        "discovery_context": context,
    }

    try:
        inserted = supa_insert("research_methods", row)
        method_id = inserted[0]["id"] if isinstance(inserted, list) else inserted.get("id")
        log.info(f"propose_method: staged '{method_code}' (id={method_id})")
        return inserted[0] if isinstance(inserted, list) else inserted
    except Exception as e:
        log.error(f"propose_method: insert failed: {e}")
        return None


def approve_method(method_id):
    """
    Approve a staged method — move from staged to active.

    Clears the [STAGED] prefix and sets is_active=True.
    Returns the updated row dict.
    """
    rows = supa_get("research_methods", f"id=eq.{method_id}&select=*")
    if not rows:
        log.warning(f"approve_method: method {method_id} not found")
        return None

    method = rows[0]
    context = method.get("discovery_context", "")
    # Remove staged prefix
    if context.startswith(STAGED_PREFIX):
        context = context[len(STAGED_PREFIX):].strip()

    result = supa_patch(
        "research_methods",
        f"id=eq.{method_id}",
        {
            "is_active": True,
            "discovery_context": context,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    log.info(f"approve_method: method {method_id} ({method.get('method_code')}) approved → active")
    return result[0] if isinstance(result, list) else result


def retire_method(method_id):
    """
    Retire an active method.

    Sets is_active=False and prefixes discovery_context with [RETIRED].
    """
    rows = supa_get("research_methods", f"id=eq.{method_id}&select=*")
    if not rows:
        return None

    method = rows[0]
    context = method.get("discovery_context", "")
    if not context.startswith(RETIRED_PREFIX):
        context = f"{RETIRED_PREFIX} {context}"

    result = supa_patch(
        "research_methods",
        f"id=eq.{method_id}",
        {
            "is_active": False,
            "discovery_context": context,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    log.info(f"retire_method: method {method_id} retired")
    return result[0] if isinstance(result, list) else result


def update_success_rates():
    """
    Recalculate success_rate for all methods based on times_used / times_succeeded.

    Updates every method where times_used > 0.
    Returns the number of methods updated.
    """
    methods = supa_get("research_methods", "times_used=gt.0&select=id,times_used,times_succeeded")
    updated = 0
    for method in methods:
        used = method.get("times_used", 0) or 0
        succeeded = method.get("times_succeeded", 0) or 0
        if used > 0:
            rate = round(succeeded / used, 4)
            try:
                supa_patch(
                    "research_methods",
                    f"id=eq.{method['id']}",
                    {
                        "success_rate": rate,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                updated += 1
            except Exception as e:
                log.warning(f"update_success_rates: failed for {method['id']}: {e}")

    log.info(f"update_success_rates: updated {updated} methods")
    return updated


def get_method_leaderboard(entity=None):
    """
    Return active methods ranked by success_rate descending.

    Args:
        entity: optional string to filter by (not yet a DB column — filtered
                client-side if present in discovery_context or method_code prefix)

    Returns:
        list of method dicts, sorted by success_rate desc, then times_used desc
    """
    params = "is_active=eq.true&order=success_rate.desc,times_used.desc&select=*"
    methods = supa_get("research_methods", params)

    if entity:
        # Soft filter — entity may appear in discovery_context or method_code
        entity_lower = entity.lower()
        methods = [
            m for m in methods
            if entity_lower in (m.get("discovery_context") or "").lower()
            or entity_lower in (m.get("method_code") or "").lower()
            or entity_lower in (m.get("category") or "").lower()
        ]

    return methods


def get_staged_methods():
    """
    Return all staged (pending review) methods.

    Staged = is_active=False AND discovery_context starts with [STAGED]
    """
    inactive = supa_get(
        "research_methods",
        "is_active=eq.false&order=created_at.desc&select=*",
    )
    staged = [
        m for m in inactive
        if (m.get("discovery_context") or "").startswith(STAGED_PREFIX)
    ]
    return staged


# ---------------------------------------------------------------------------
# High-level: process a correction end-to-end
# ---------------------------------------------------------------------------

def learn_from_correction(comment_id):
    """
    Full pipeline: extract_learning → propose_method.

    Call this after a fact_correction comment has been responded to.
    Returns the proposed method row, or None if nothing was learned.
    """
    learning = extract_learning(comment_id)
    if not learning:
        return None

    proposed = propose_method(learning)
    return proposed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--learn" in sys.argv:
        idx = sys.argv.index("--learn")
        cid = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if cid:
            result = learn_from_correction(cid)
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Usage: research_learner.py --learn <comment_id>")

    elif "--approve" in sys.argv:
        idx = sys.argv.index("--approve")
        mid = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if mid:
            result = approve_method(mid)
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Usage: research_learner.py --approve <method_id>")

    elif "--staged" in sys.argv:
        staged = get_staged_methods()
        print(f"{len(staged)} staged methods:")
        for m in staged:
            print(f"  {m['id']} | {m['method_code']} | {m.get('method_name')}")

    elif "--leaderboard" in sys.argv:
        entity = None
        if "--entity" in sys.argv:
            idx = sys.argv.index("--entity")
            entity = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        board = get_method_leaderboard(entity=entity)
        print(f"{'Rank':<5} {'Code':<35} {'Rate':>6} {'Used':>6}")
        for i, m in enumerate(board, 1):
            rate = f"{m.get('success_rate', 0) * 100:.0f}%"
            print(f"{i:<5} {m['method_code']:<35} {rate:>6} {m.get('times_used', 0):>6}")

    elif "--update-rates" in sys.argv:
        n = update_success_rates()
        print(f"Updated {n} method success rates")

    else:
        print(
            "Usage:\n"
            "  research_learner.py --learn <comment_id>\n"
            "  research_learner.py --approve <method_id>\n"
            "  research_learner.py --staged\n"
            "  research_learner.py --leaderboard [--entity <entity>]\n"
            "  research_learner.py --update-rates\n"
        )
