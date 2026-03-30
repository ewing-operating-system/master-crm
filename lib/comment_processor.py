#!/usr/bin/env python3
"""
D→C Feedback Conversation Processor (Steps 6-9)

Polls page_comments for pending/responded comments every 60 seconds.
Uses Claude CLI to generate clarifying questions and revised content.

Statuses:
  pending           → New comment, needs clarifying question
  awaiting_response → Clarifying question sent, waiting for user reply
  responded         → User answered clarifying question, generate revision
  revision_ready    → Revised content generated, ready for review
  acknowledged      → Approval comments, no clarification needed
  applied           → Revision accepted and applied
  rejected          → Revision rejected
"""

import json, os, sys, time, subprocess, logging, urllib.request, ssl
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "feedback_system.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("comment_processor")

# ---------------------------------------------------------------------------
# Supabase connection — hardcoded to master-crm instance
# (env vars may point to old instance, so we pin to the correct one)
# ---------------------------------------------------------------------------
import urllib.request, ssl
_ctx = ssl.create_default_context()

SUPA_URL = "https://dwrnfpjcvydhmhnvyzov.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s"

def _headers(prefer=None):
    h = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}", "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    return h

def patch_comment(comment_id, updates):
    """PATCH a single page_comment by ID."""
    url = f"{SUPA_URL}/rest/v1/page_comments?id=eq.{comment_id}"
    payload = json.dumps(updates, default=str).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers("return=representation"), method="PATCH")
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())

def supa_get(table, params=""):
    """GET from a Supabase table."""
    url = f"{SUPA_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_headers())
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())

def supa_insert(table, data):
    """POST to a Supabase table."""
    url = f"{SUPA_URL}/rest/v1/{table}"
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers("return=representation"), method="POST")
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())

def get_comments_by_status(status):
    """Fetch all page_comments with a given status."""
    return supa_get("page_comments", f"status=eq.{status}&order=created_at.asc")

def insert_notification(data):
    """Insert into notifications table (entity-exempt)."""
    url = f"{SUPA_URL}/rest/v1/notifications"
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers("return=representation"), method="POST")
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read())

# ---------------------------------------------------------------------------
# Claude CLI wrapper
# ---------------------------------------------------------------------------
def ask_claude(prompt, max_tokens=1000):
    """Run Claude CLI with a prompt via stdin, return the response text."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            log.error(f"Claude CLI error: {result.stderr[:500]}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log.error("Claude CLI timed out after 120s")
        return None
    except FileNotFoundError:
        log.error("Claude CLI not found at 'claude'")
        return None

# ---------------------------------------------------------------------------
# Clarifying question templates (used as fallback if Claude CLI fails)
# ---------------------------------------------------------------------------
CLARIFYING_TEMPLATES = {
    "fact_correction": "Thanks for flagging this. A few questions to make sure we get it right:\n\n1. Where did you find this information? (Call, email, website, public filing?)\n2. Can you share a link or reference we can verify against?\n3. Should this update apply only to this section, or does it affect other parts of the dossier?",
    "tone_adjustment": "Got it — the tone needs work. Help us dial it in:\n\n1. Can you describe the tone you'd prefer? (More formal? More personal? More confident?)\n2. Is there a specific phrase or sentence that feels off?\n3. Can you give an example of how you'd say it?",
    "addition_request": "Understood — something's missing. A few clarifications:\n\n1. What specifically should be added?\n2. Do you have the data already, or should we research it?\n3. Where in this section should it go — beginning, end, or replacing existing text?",
    "feedback": "Thanks for the feedback. To make the right changes:\n\n1. Can you be more specific about what should change?\n2. What would the ideal version look like?\n3. Is this a priority fix or a nice-to-have?",
}

# ---------------------------------------------------------------------------
# Step 6: Process pending comments → generate clarifying questions
# ---------------------------------------------------------------------------
def process_pending():
    """For each pending comment, generate a clarifying question and store it."""
    pending = get_comments_by_status("pending")
    if not pending:
        return

    log.info(f"Found {len(pending)} pending comments to process")

    for comment in pending:
        cid = comment["id"]
        ctype = comment["comment_type"]
        ctext = comment["comment_text"]
        section = comment["section_id"]
        company = comment["company_name"]
        commenter = comment["commenter"]

        # Step 9: Approval comments — skip clarification
        if ctype == "approval":
            handle_approval(comment)
            continue

        # Generate clarifying question via Claude CLI
        prompt = f"""You are a CRM assistant helping refine feedback on a company dossier page.

A user ({commenter}) left a "{ctype.replace('_', ' ')}" comment on the "{section}" section for {company}:

"{ctext}"

Generate 2-4 short, specific clarifying questions to gather enough detail to make the right edit. Be conversational and direct. Number each question. Do not repeat what they already said — ask what's MISSING to take action."""

        reply = ask_claude(prompt)
        if not reply:
            # Fallback to template
            reply = CLARIFYING_TEMPLATES.get(ctype, CLARIFYING_TEMPLATES["feedback"])
            log.warning(f"Claude CLI failed for {cid}, using template fallback")

        # Update the comment with the clarifying question
        thread = comment.get("conversation_thread") or []
        thread.append({
            "role": "system",
            "text": reply,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        patch_comment(cid, {
            "reply": reply,
            "status": "awaiting_response",
            "conversation_thread": json.dumps(thread)
        })

        log.info(f"Processed pending comment {cid} ({ctype}) for {company}/{section} — now awaiting_response")

# ---------------------------------------------------------------------------
# Step 7: Process responded comments → generate revised content
# ---------------------------------------------------------------------------
def process_responded():
    """For comments where user answered the clarifying question, generate a revision."""
    responded = get_comments_by_status("responded")
    if not responded:
        return

    log.info(f"Found {len(responded)} responded comments to process")

    for comment in responded:
        cid = comment["id"]
        ctype = comment["comment_type"]
        ctext = comment["comment_text"]
        user_response = comment.get("user_response", "")
        section = comment["section_id"]
        company = comment["company_name"]
        page_type = comment["page_type"]
        reply = comment.get("reply", "")

        # Try to fetch the current section content from the page
        # We'll look for existing page content in page_templates or construct context
        original_content = fetch_section_content(company, page_type, section)

        prompt = f"""You are rewriting a section of a company dossier based on user feedback.

Company: {company}
Page type: {page_type}
Section: {section}

Original section content:
{original_content if original_content else "(Content not available — generate based on feedback context)"}

Comment type: {ctype.replace('_', ' ')}
Original comment: {ctext}
Clarifying questions asked: {reply}
User's response: {user_response}

Generate the REVISED section content incorporating all the feedback. Write it as final copy — no commentary, no "here's what I changed" notes. Match the existing tone and format. If the original content is not available, write the section from scratch using the feedback as guidance."""

        revised = ask_claude(prompt)
        if not revised:
            log.error(f"Claude CLI failed generating revision for {cid}")
            continue

        # Update the comment thread
        thread = comment.get("conversation_thread") or []
        thread.append({
            "role": "system",
            "text": f"[Revision generated based on your feedback]",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        patch_comment(cid, {
            "original_content": original_content or "(not captured)",
            "revised_content": revised,
            "status": "revision_ready",
            "conversation_thread": json.dumps(thread)
        })

        log.info(f"Generated revision for comment {cid} ({company}/{section}) — now revision_ready")

        # Step 8: If fact_correction with source info, learn the research method
        if ctype == "fact_correction" and user_response:
            learn_research_method(comment, user_response)

# ---------------------------------------------------------------------------
# Step 8: Research Method Learning
# ---------------------------------------------------------------------------
def learn_research_method(comment, user_response):
    """Extract and store a new research method from a fact_correction source."""
    prompt = f"""A user corrected a fact on a company dossier and provided their source.

Comment: {comment['comment_text']}
Source/method they described: {user_response}

Extract a reusable research method from this. Return a JSON object with:
- method_code: short snake_case identifier (e.g., "owner_phone_call", "state_filing_search")
- method_name: human-readable name
- query_template: how to use this method for any company (use {{company_name}}, {{owner_name}} as placeholders)
- description: one sentence explaining what this method finds

Return ONLY valid JSON, no markdown fences."""

    result = ask_claude(prompt)
    if not result:
        log.warning(f"Could not extract research method from comment {comment['id']}")
        return

    try:
        # Strip markdown fences if present
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        method = json.loads(cleaned)
    except json.JSONDecodeError:
        log.warning(f"Could not parse research method JSON: {result[:200]}")
        return

    # Check if this method_code already exists
    existing = supa_get("research_methods", f"method_code=eq.{method.get('method_code', 'unknown')}")
    if existing:
        log.info(f"Research method '{method.get('method_code')}' already exists, skipping")
        return

    try:
        supa_insert("research_methods", {
            "method_code": method.get("method_code", "user_discovered_" + comment["id"][:8]),
            "method_name": method.get("method_name", "User-discovered method"),
            "query_template": method.get("query_template", ""),
            "description": method.get("description", ""),
            "category": "user_discovered",
            "tool": "manual",
            "discovered_by": comment["commenter"],
            "discovery_context": comment["comment_text"],
            "is_active": True,
            "expected_output": [],
        })
        log.info(f"Learned new research method: {method.get('method_code')} from {comment['commenter']}")
    except Exception as e:
        log.error(f"Failed to insert research method: {e}")

# ---------------------------------------------------------------------------
# Step 9: Handle approval → propose template + notify admin
# ---------------------------------------------------------------------------
def handle_approval(comment):
    """When a section is approved, propose it as a template and notify admin."""
    cid = comment["id"]
    section = comment["section_id"]
    company = comment["company_name"]
    page_type = comment["page_type"]
    commenter = comment["commenter"]

    # Mark as acknowledged
    thread = [{
        "role": "system",
        "text": f"Noted — {commenter} approved this section. Proposing as template for review.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]

    patch_comment(cid, {
        "reply": f"Acknowledged. This section has been flagged as approved and proposed as a template.",
        "status": "acknowledged",
        "conversation_thread": json.dumps(thread)
    })

    # Fetch current section content for the template
    content = fetch_section_content(company, page_type, section)

    # Propose as template
    try:
        supa_insert("page_templates", {
            "page_type": page_type,
            "template_name": f"{company} — {section} (approved)",
            "section_id": section,
            "template_content": content or "(content to be captured on next render)",
            "approved_by": commenter,
            "needs_human_approval": True,
            "entity": infer_entity(company),
        })
        log.info(f"Proposed template from approval: {company}/{section} by {commenter}")
    except Exception as e:
        log.error(f"Failed to propose template: {e}")

    # Create notification for admin
    try:
        insert_notification({
            "recipient": "admin",
            "notification_type": "template_proposal",
            "title": f"Template proposed: {company} — {section}",
            "message": f"{commenter} approved the '{section}' section for {company}. Review and confirm as a reusable template.",
            "link": f"/{page_type}/{company.lower().replace(' ', '-')}#{section}",
            "metadata": json.dumps({
                "comment_id": cid,
                "company": company,
                "section": section,
                "approved_by": commenter,
                "page_type": page_type,
            })
        })
        log.info(f"Notification created for template proposal: {company}/{section}")
    except Exception as e:
        log.error(f"Failed to create notification: {e}")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fetch_section_content(company, page_type, section_id):
    """Try to fetch existing section content from page_templates or rendered pages."""
    try:
        templates = supa_get("page_templates",
            f"page_type=eq.{page_type}&section_id=eq.{section_id}&order=created_at.desc&limit=1")
        if templates:
            return templates[0].get("template_content", "")
    except Exception:
        pass
    return ""

def infer_entity(company_name):
    """Infer entity from company context. Default to next_chapter for dossier companies."""
    # Most dossier companies are Next Chapter targets
    return "next_chapter"

# ---------------------------------------------------------------------------
# Main polling loop
# ---------------------------------------------------------------------------
def run_once():
    """Single pass: process all actionable comments."""
    process_pending()
    process_responded()

def main():
    """Poll every 60 seconds."""
    log.info("=" * 60)
    log.info("Comment Processor started (Steps 6-9)")
    log.info(f"Logging to: {LOG_FILE}")
    log.info("=" * 60)

    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            log.info("Shutting down comment processor")
            break
        except Exception as e:
            log.error(f"Unhandled error in processing loop: {e}", exc_info=True)

        time.sleep(60)

if __name__ == "__main__":
    if "--once" in sys.argv:
        # Single pass mode for testing
        run_once()
    else:
        main()
