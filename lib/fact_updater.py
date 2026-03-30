#!/usr/bin/env python3
"""
Fact Updater — Step 12 of the feedback loop.

SYSTEM RULE: Every page, every section, every element must have feedback capability.
The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
Any page generation engine that creates HTML must include <script src="comment-widget.js"></script> before </body>.
No exceptions. This is how we learn.

When a comment with type='fact_correction' reaches status='revision_ready':
1. Parse what field was corrected
2. Update the canonical source (proposals table)
3. Store BOTH old and new values in companies.human_corrections JSONB
4. Log to estimate_accuracy if it's a number correction
5. Mark the page as stale for lazy rebuild
"""

import json, os, sys, re, urllib.request, ssl
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/feedback_steps_10_14.log")

ctx = ssl.create_default_context()

# Section-to-field mapping for proposals table
SECTION_FIELD_MAP = {
    "valuation": ["estimated_revenue", "estimated_ebitda", "valuation_range",
                   "estimated_ev_low", "estimated_ev_mid", "estimated_ev_high"],
    "revenue": ["estimated_revenue"],
    "ebitda": ["estimated_ebitda"],
    "buyers": ["buyer_profile", "buyer_narrative"],
    "buyer": ["buyer_profile", "buyer_narrative"],
    "narrative": ["company_narrative"],
    "company_narrative": ["company_narrative"],
    "strengths": ["top_3_strengths"],
    "top_3_strengths": ["top_3_strengths"],
    "market": ["market_analysis"],
    "market_analysis": ["market_analysis"],
    "attack_plan": ["attack_plan"],
    "outreach": ["outreach_strategy"],
    "timeline": ["timeline"],
    "fee": ["fee_content", "fee_type", "engagement_fee", "success_fee_pct"],
}


def log(msg):
    line = f"{datetime.utcnow().isoformat()} | FACT_UPDATE | {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def _supabase_request(method, table, params="", data=None):
    """Generic Supabase REST request."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = json.dumps(data, default=str).encode() if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


def _get(table, params):
    return _supabase_request("GET", table, params)


def _patch(table, params, data):
    return _supabase_request("PATCH", table, params, data)


def _post(table, data):
    return _supabase_request("POST", table, "", data)


def extract_number(text):
    """Try to extract a dollar amount or number from text."""
    # Match patterns like $10M, $10 million, 10M, $10,000,000
    patterns = [
        r'\$?([\d,]+(?:\.\d+)?)\s*(?:million|mil|M)\b',
        r'\$?([\d,]+(?:\.\d+)?)\s*(?:billion|bil|B)\b',
        r'\$([\d,]+(?:\.\d+)?)',
        r'([\d,]+(?:\.\d+)?)',
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).replace(',', '')
            num = float(val)
            if 'billion' in text.lower() or 'bil' in text.lower() or text.endswith('B'):
                num *= 1_000_000_000
            elif 'million' in text.lower() or 'mil' in text.lower() or text.upper().endswith('M'):
                num *= 1_000_000
            return num
    return None


def identify_fields(section_id, comment_text):
    """Determine which proposal fields a comment refers to."""
    section_lower = section_id.lower().replace('-', '_')

    # Direct section match
    for key, fields in SECTION_FIELD_MAP.items():
        if key in section_lower:
            return fields

    # Keyword-based fallback from comment text
    text_lower = comment_text.lower()
    if any(w in text_lower for w in ["revenue", "sales", "top line"]):
        return ["estimated_revenue"]
    if any(w in text_lower for w in ["ebitda", "profit", "earnings", "margin"]):
        return ["estimated_ebitda"]
    if any(w in text_lower for w in ["valuation", "multiple", "ev ", "enterprise value"]):
        return ["valuation_range", "estimated_ev_low", "estimated_ev_mid", "estimated_ev_high"]
    if any(w in text_lower for w in ["buyer", "acquirer", "strategic"]):
        return ["buyer_profile", "buyer_narrative"]
    if any(w in text_lower for w in ["narrative", "story", "about"]):
        return ["company_narrative"]
    if any(w in text_lower for w in ["strength", "competitive", "advantage"]):
        return ["top_3_strengths"]

    log(f"Could not identify fields for section '{section_id}', defaulting to company_narrative")
    return ["company_narrative"]


def update_proposal(company_name, fields, comment_text, resolution):
    """Update the proposals table with corrected data."""
    # Get current proposal
    proposals = _get("proposals", f"company_name=eq.{company_name}&limit=1&order=created_at.desc")
    if not proposals:
        log(f"No proposal found for {company_name}")
        return None

    proposal = proposals[0]
    old_values = {}
    new_values = {}
    content = resolution or comment_text

    for field in fields:
        old_val = proposal.get(field)
        old_values[field] = old_val

        # For text fields, use the resolution/comment as the new value
        if field in ("company_narrative", "buyer_profile", "buyer_narrative",
                     "market_analysis", "attack_plan", "outreach_strategy",
                     "timeline", "fee_content"):
            # Only update if the correction clearly provides new content
            new_values[field] = content
        elif field == "estimated_revenue":
            num = extract_number(content)
            if num:
                new_values[field] = f"${num/1_000_000:.1f}M" if num >= 1_000_000 else f"${num:,.0f}"
        elif field == "estimated_ebitda":
            num = extract_number(content)
            if num:
                new_values[field] = f"${num/1_000_000:.1f}M" if num >= 1_000_000 else f"${num:,.0f}"
        elif field in ("estimated_ev_low", "estimated_ev_mid", "estimated_ev_high"):
            num = extract_number(content)
            if num:
                new_values[field] = num
        elif field == "top_3_strengths":
            # Parse comma or newline separated list
            items = re.split(r'[,\n]+', content)
            items = [i.strip().lstrip('0123456789.-) ') for i in items if i.strip()]
            if items:
                new_values[field] = items[:5]

    # Apply updates to proposal
    if new_values:
        try:
            _patch("proposals", f"id=eq.{proposal['id']}", new_values)
            log(f"Updated proposal for {company_name}: {list(new_values.keys())}")
        except Exception as e:
            log(f"Failed to update proposal: {e}")

    return {"old": old_values, "new": new_values, "proposal_id": proposal["id"]}


def store_human_correction(company_name, old_values, new_values, commenter, comment_id):
    """Store correction history in companies.human_corrections JSONB."""
    companies = _get("companies", f"company_name=eq.{company_name}&limit=1")
    if not companies:
        log(f"No company record for {company_name}, skipping human_corrections store")
        return

    company = companies[0]
    corrections = company.get("human_corrections") or []
    if isinstance(corrections, str):
        try:
            corrections = json.loads(corrections)
        except:
            corrections = []

    correction_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "commenter": commenter,
        "comment_id": str(comment_id),
        "old_values": old_values,
        "new_values": new_values
    }
    corrections.append(correction_entry)

    try:
        _patch("companies", f"id=eq.{company['id']}",
               {"human_corrections": json.dumps(corrections, default=str)})
        log(f"Stored human correction for {company_name}")
    except Exception as e:
        log(f"Failed to store human correction: {e}")


def log_estimate_accuracy(company_name, field, old_value, new_value, commenter):
    """Log numeric corrections to estimate_accuracy table."""
    old_num = extract_number(str(old_value)) if old_value else None
    new_num = extract_number(str(new_value)) if new_value else None

    if old_num is not None and new_num is not None and old_num != 0:
        pct_error = abs(old_num - new_num) / old_num * 100
        try:
            _post("estimate_accuracy", {
                "company_name": company_name,
                "field_name": field,
                "estimated_value": old_num,
                "actual_value": new_num,
                "pct_error": round(pct_error, 2),
                "correction_source": commenter,
                "corrected_at": datetime.utcnow().isoformat()
            })
            log(f"Logged estimate accuracy for {company_name}.{field}: {pct_error:.1f}% error")
        except Exception as e:
            log(f"Failed to log estimate accuracy: {e}")


def mark_page_stale(company_name, page_type="proposal", reason="fact_correction_applied"):
    """Mark a page_version as stale so the next refresh cycle regenerates it."""
    try:
        versions = _get("page_versions",
            f"company_name=eq.{company_name}&page_type=eq.{page_type}&order=version.desc&limit=1")
        if versions:
            _patch("page_versions", f"id=eq.{versions[0]['id']}",
                   {"is_stale": True, "stale_reason": reason})
            log(f"Marked {page_type} page stale for {company_name}")
    except Exception as e:
        log(f"Failed to mark page stale: {e}")


def process_fact_corrections():
    """
    Main entry point: find all fact_correction comments that are revision_ready
    and apply the corrections.
    """
    log("Processing fact corrections...")

    try:
        comments = _get("page_comments",
            "comment_type=eq.fact_correction&status=eq.revision_ready&order=created_at.asc")
    except Exception as e:
        log(f"Failed to fetch fact corrections: {e}")
        return

    if not comments:
        log("No pending fact corrections found")
        return

    for comment in comments:
        company = comment.get("company_name")
        section = comment.get("section_id", "")
        text = comment.get("comment_text", "")
        resolution = comment.get("resolution", "")
        commenter = comment.get("commenter", "")
        comment_id = comment.get("id")

        log(f"Processing correction: {company} / {section} by {commenter}")

        # 1. Identify which fields to update
        fields = identify_fields(section, text)

        # 2. Update proposals table
        result = update_proposal(company, fields, text, resolution)

        if result and result["new"]:
            # 3. Store old+new in companies.human_corrections
            store_human_correction(company, result["old"], result["new"],
                                   commenter, comment_id)

            # 4. Log numeric corrections to estimate_accuracy
            for field in result["new"]:
                if field in ("estimated_revenue", "estimated_ebitda",
                             "estimated_ev_low", "estimated_ev_mid", "estimated_ev_high"):
                    log_estimate_accuracy(company, field,
                                          result["old"].get(field),
                                          result["new"].get(field),
                                          commenter)

            # 5. Mark page as stale
            page_type = comment.get("page_type", "proposal")
            mark_page_stale(company, page_type)
            # Also mark hub as stale
            mark_page_stale(company, "hub")

        # Mark comment as applied
        try:
            _patch("page_comments", f"id=eq.{comment_id}",
                   {"status": "applied"})
            log(f"Comment {comment_id} marked as applied")
        except Exception as e:
            log(f"Failed to mark comment as applied: {e}")

    log(f"Processed {len(comments)} fact corrections")


if __name__ == "__main__":
    process_fact_corrections()
