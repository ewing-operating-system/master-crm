#!/usr/bin/env python3
"""
Diff Engine — Feature #44
==========================
Version history and section-level diff for all generated HTML pages.
Every page build creates a new version. No blocking — just build, version, and log.

Tables used:
  page_versions — id, page_path, version_number, html_hash, html_content,
                  diff_summary (JSON), entity, created_at
"""

import hashlib
import json
import os
import re
import subprocess
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# ---------------------------------------------------------------------------
# Supabase config (mirrors lib/supabase.py pattern)
# ---------------------------------------------------------------------------
_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)
_ctx = ssl.create_default_context()

TELEGRAM_TARGET = os.environ.get("EWING_TELEGRAM_CHAT_ID", "8706175267")
DIFF_VIEW_BASE = os.environ.get(
    "DIFF_VIEW_BASE",
    "https://master-crm-web.vercel.app/diff-viewer.html",
)


def _headers(prefer=None):
    h = {
        "apikey": _KEY,
        "Authorization": f"Bearer {_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _db_get(table, params=""):
    url = f"{_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_headers())
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


def _db_insert(table, data):
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{_URL}/rest/v1/{table}",
        data=payload,
        headers=_headers("return=representation"),
        method="POST",
    )
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


def _db_update(table, match_params, data):
    payload = json.dumps(data, default=str).encode()
    url = f"{_URL}/rest/v1/{table}?{match_params}"
    req = urllib.request.Request(
        url,
        data=payload,
        headers=_headers("return=representation"),
        method="PATCH",
    )
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Section extraction helpers
# ---------------------------------------------------------------------------

def _extract_sections(html):
    """
    Parse HTML into named sections using <h2> tags as section markers.
    Returns OrderedDict: {section_title: text_content_string}
    The special key "__preamble__" holds content before the first h2.
    """
    from collections import OrderedDict

    sections = OrderedDict()

    # Strip script/style blocks before parsing text
    clean = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<style[^>]*>.*?</style>", "", clean, flags=re.DOTALL | re.IGNORECASE)

    # Split on h2 tags; capture the heading text and what follows
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", clean, flags=re.DOTALL | re.IGNORECASE)

    current_title = "__preamble__"
    buffer = []

    for part in parts:
        h2_match = re.match(r"<h2[^>]*>(.*?)</h2>", part, re.DOTALL | re.IGNORECASE)
        if h2_match:
            # Save previous buffer
            sections[current_title] = _strip_tags(buffer)
            current_title = _strip_tags([h2_match.group(1)]).strip()
            buffer = []
        else:
            buffer.append(part)

    sections[current_title] = _strip_tags(buffer)
    return sections


def _strip_tags(fragments):
    """Remove all HTML tags from a list of strings and join."""
    text = " ".join(fragments)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _html_hash(html):
    return hashlib.sha256(html.encode("utf-8", errors="replace")).hexdigest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def snapshot_page(page_path):
    """
    Read the current on-disk HTML and store as a version record.
    Returns the version record dict, or None if the file does not exist.
    """
    if not os.path.exists(page_path):
        return None

    with open(page_path, "r", encoding="utf-8", errors="replace") as fh:
        html = fh.read()

    # Determine next version number
    encoded = urllib.parse.quote(page_path, safe="")
    existing = _db_get(
        "page_versions",
        f"page_path=eq.{encoded}&select=version_number&order=version_number.desc&limit=1",
    )
    version_number = (existing[0]["version_number"] + 1) if existing else 1

    record = {
        "page_path": page_path,
        "version_number": version_number,
        "html_hash": _html_hash(html),
        "html_content": html,
        "diff_summary": json.dumps({}),
        "entity": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    result = _db_insert("page_versions", record)
    return result[0] if isinstance(result, list) else result


def compute_diff(old_html, new_html):
    """
    Section-level diff between two HTML strings.
    Returns:
      {
        "added":   [section_title, ...],
        "removed": [section_title, ...],
        "changed": [{"section": title, "old_text": ..., "new_text": ...}, ...]
      }
    """
    old_sections = _extract_sections(old_html)
    new_sections = _extract_sections(new_html)

    old_keys = set(old_sections.keys())
    new_keys = set(new_sections.keys())

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []

    for key in old_keys & new_keys:
        old_text = old_sections[key]
        new_text = new_sections[key]
        if old_text != new_text:
            changed.append({"section": key, "old_text": old_text, "new_text": new_text})

    return {"added": added, "removed": removed, "changed": changed}


def get_change_percentage(diff_result):
    """
    Returns an approximate percentage (0–100) of content changed.
    Calculated as: changed_sections / total_unique_sections * 100.
    """
    total = len(
        set(diff_result.get("added", []))
        | set(diff_result.get("removed", []))
        | {c["section"] for c in diff_result.get("changed", [])}
    )
    # We need a denominator; use changed+removed+added vs a minimum baseline of 1
    denominator = max(
        total
        + len({c["section"] for c in diff_result.get("changed", [])})
        + len(diff_result.get("removed", [])),
        1,
    )
    # Simpler: changed sections (in any way) as share of total touched
    touched = (
        len(diff_result.get("added", []))
        + len(diff_result.get("removed", []))
        + len(diff_result.get("changed", []))
    )
    # Estimate total sections = changed + unchanged; we only know changed count,
    # so we use touched as numerator over touched + 5 baseline sections as denominator
    # to avoid 100% on tiny pages. Cap at 100.
    pct = min(round(touched / max(touched + 3, 1) * 100), 100)
    return pct


def _send_telegram(page_path, pct):
    """Send a Telegram notification when change percentage exceeds threshold."""
    page_name = os.path.basename(page_path)
    url = f"{DIFF_VIEW_BASE}?page={urllib.parse.quote(page_name)}"
    message = f"[Argus] Page {page_name} changed {pct}% — review at {url}"
    try:
        subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", "telegram",
                "--target", TELEGRAM_TARGET,
                "--message", message,
            ],
            timeout=15,
            check=False,
        )
    except Exception:
        pass  # Non-blocking — notification failure must never interrupt a build


def create_version(page_path, new_html, entity=None):
    """
    Full workflow:
      1. Read & snapshot the current on-disk file (old version)
      2. Write new_html to disk
      3. Compute section-level diff
      4. Store new version record with diff summary
      5. If change > 20%, send Telegram notification

    Returns the new version record dict.
    """
    # --- 1. Read old HTML before overwriting ---
    old_html = ""
    if os.path.exists(page_path):
        with open(page_path, "r", encoding="utf-8", errors="replace") as fh:
            old_html = fh.read()

    # --- 2. Write new HTML ---
    os.makedirs(os.path.dirname(os.path.abspath(page_path)), exist_ok=True)
    with open(page_path, "w", encoding="utf-8") as fh:
        fh.write(new_html)

    # --- 3. Compute diff ---
    diff = compute_diff(old_html, new_html) if old_html else {"added": [], "removed": [], "changed": []}

    # --- 4. Determine next version number ---
    encoded = urllib.parse.quote(page_path, safe="")
    existing = _db_get(
        "page_versions",
        f"page_path=eq.{encoded}&select=version_number&order=version_number.desc&limit=1",
    )
    version_number = (existing[0]["version_number"] + 1) if existing else 1

    record = {
        "page_path": page_path,
        "version_number": version_number,
        "html_hash": _html_hash(new_html),
        "html_content": new_html,
        "diff_summary": json.dumps(diff),
        "entity": entity,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    result = _db_insert("page_versions", record)
    stored = result[0] if isinstance(result, list) else result

    # --- 5. Telegram alert if heavily changed ---
    if old_html:
        pct = get_change_percentage(diff)
        if pct > 20:
            _send_telegram(page_path, pct)

    return stored


def revert_to_version(page_path, version_id):
    """
    Restore the HTML from a previous version record identified by version_id (UUID).
    Also creates a new version record for the revert so history is never rewritten.
    Returns the new version record.
    """
    encoded_id = urllib.parse.quote(str(version_id), safe="")
    records = _db_get("page_versions", f"id=eq.{encoded_id}&select=html_content,entity")
    if not records:
        raise ValueError(f"Version ID '{version_id}' not found in page_versions.")

    target = records[0]
    html = target.get("html_content", "")
    entity = target.get("entity")

    # create_version handles writing + logging; treat revert as a new version
    new_record = create_version(page_path, html, entity=entity)
    return new_record


def get_version_history(page_path, limit=20):
    """
    Fetch the most recent `limit` versions for page_path, newest first.
    Each record includes id, version_number, html_hash, diff_summary, entity, created_at.
    html_content is NOT returned (bandwidth).
    """
    encoded = urllib.parse.quote(page_path, safe="")
    params = (
        f"page_path=eq.{encoded}"
        f"&select=id,page_path,version_number,html_hash,diff_summary,entity,created_at"
        f"&order=version_number.desc"
        f"&limit={limit}"
    )
    return _db_get("page_versions", params)
