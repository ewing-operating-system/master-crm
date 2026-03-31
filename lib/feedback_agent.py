#!/usr/bin/env python3
"""
Feature #45 — D→C Feedback Conversation Agent

"Always on, always ready, always has a fallback."

Multi-model agentic framework. Never single-threaded to one LLM.
Polls page_comments every 60 seconds. For each pending comment,
determines if clarifying questions are needed, generates them via
fallback chain, and drives the thread through to revision.

Fallback chain (question generation):
  1. Claude CLI  (`claude -p` via subprocess)
  2. OpenRouter  DeepSeek V3  (deepseek/deepseek-chat-v3-0324)
  3. Template    QUESTION_TEMPLATES dict

Statuses:
  pending           → New comment, needs clarifying question
  clarifying        → Clarifying question being generated (transient)
  awaiting_response → Clarifying Q sent, waiting for user reply
  revision_ready    → Revised content ready for review
  applied           → Revision accepted and applied
  rejected          → User or admin rejected the revision

Extra fields stored in page_comments:
  clarifying_questions  JSONB  list of question strings
  user_response         TEXT   user's answer to the questions
  revision_applied      BOOL   True once applied
"""

import json
import logging
import os
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "feedback_agent.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("feedback_agent")

# ---------------------------------------------------------------------------
# Supabase — master-crm instance (service role for backend agent)
# ---------------------------------------------------------------------------
_ctx = ssl.create_default_context()

SUPA_URL = "https://dwrnfpjcvydhmhnvyzov.supabase.co"
SUPA_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)

# ---------------------------------------------------------------------------
# OpenRouter config — DeepSeek V3 fallback
# ---------------------------------------------------------------------------
OPENROUTER_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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",
)
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------------------------------------------------------
# Template fallbacks (Tier 3) — always succeeds
# ---------------------------------------------------------------------------
QUESTION_TEMPLATES = {
    "fact_correction": (
        "Thanks for flagging this. To make sure we get it right:\n\n"
        "1. Where did you find this information? (call, email, website, filing?)\n"
        "2. Can you share a link or reference we can verify against?\n"
        "3. Should this update apply only to this section, or does it affect "
        "other parts of the dossier?"
    ),
    "tone_adjustment": (
        "Got it — the tone needs work. Help us dial it in:\n\n"
        "1. Can you describe the tone you'd prefer? (More formal? More personal? "
        "More confident?)\n"
        "2. Is there a specific phrase or sentence that feels off?\n"
        "3. Can you give an example of how you'd say it?"
    ),
    "addition_request": (
        "Understood — something's missing. A few clarifications:\n\n"
        "1. What specifically should be added?\n"
        "2. Do you have the data, or should we research it?\n"
        "3. Where in this section should it go — beginning, end, or replacing "
        "existing text?"
    ),
    "deletion_request": (
        "Happy to remove that. Quick checks:\n\n"
        "1. Should this be deleted entirely, or replaced with something else?\n"
        "2. Does removing it affect other sections that reference it?\n"
        "3. Any reason it shouldn't appear anywhere in the dossier going forward?"
    ),
    "feedback": (
        "Thanks for the feedback. To make the right changes:\n\n"
        "1. Can you be more specific about what should change?\n"
        "2. What would the ideal version look like?\n"
        "3. Is this a priority fix or a nice-to-have?"
    ),
}

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


def patch_comment(comment_id, updates):
    return supa_patch("page_comments", f"id=eq.{comment_id}", updates)


# ---------------------------------------------------------------------------
# LLM Tier 1: Claude CLI
# ---------------------------------------------------------------------------

def _ask_claude_cli(prompt, timeout=120):
    """Call Claude CLI via subprocess. Returns text or None."""
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
        log.warning(f"Claude CLI non-zero exit: {result.stderr[:200]}")
        return None
    except subprocess.TimeoutExpired:
        log.warning("Claude CLI timed out")
        return None
    except FileNotFoundError:
        log.warning("Claude CLI not found in PATH")
        return None
    except Exception as e:
        log.warning(f"Claude CLI exception: {e}")
        return None


# ---------------------------------------------------------------------------
# LLM Tier 2: OpenRouter DeepSeek V3
# ---------------------------------------------------------------------------

def _ask_openrouter(prompt, max_tokens=800):
    """Call OpenRouter DeepSeek V3. Returns text or None."""
    try:
        body = json.dumps({
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }).encode()
        req = urllib.request.Request(
            OPENROUTER_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://master-crm.app",
                "X-Title": "Master CRM Feedback Agent",
            },
            method="POST",
        )
        resp = urllib.request.urlopen(req, context=_ctx, timeout=60)
        data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"].strip()
        return text if text else None
    except Exception as e:
        log.warning(f"OpenRouter DeepSeek fallback failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Fallback chain dispatcher
# ---------------------------------------------------------------------------

def _call_llm(prompt, tier_label="question generation"):
    """
    Try Claude CLI → OpenRouter DeepSeek V3 → None.
    Caller handles None by using template fallback.
    """
    log.info(f"LLM call ({tier_label}): trying Claude CLI")
    result = _ask_claude_cli(prompt)
    if result:
        log.info(f"LLM call ({tier_label}): Claude CLI succeeded")
        return result, "claude_cli"

    log.info(f"LLM call ({tier_label}): Claude CLI failed, trying OpenRouter DeepSeek V3")
    result = _ask_openrouter(prompt)
    if result:
        log.info(f"LLM call ({tier_label}): OpenRouter succeeded")
        return result, "openrouter_deepseek"

    log.warning(f"LLM call ({tier_label}): all LLM tiers failed, caller will use template")
    return None, "none"


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def generate_clarifying_questions(comment_text, page_context):
    """
    Generate clarifying questions for a comment.

    Args:
        comment_text: the raw comment string
        page_context: dict with keys like company_name, section_id, comment_type,
                      commenter, page_type

    Returns:
        (questions_str, source) where source is 'claude_cli', 'openrouter_deepseek',
        or 'template'
    """
    ctype = page_context.get("comment_type", "feedback")
    company = page_context.get("company_name", "the company")
    section = page_context.get("section_id", "this section")
    commenter = page_context.get("commenter", "the user")

    prompt = (
        f"You are a CRM assistant refining feedback on a company dossier.\n\n"
        f"User ({commenter}) left a \"{ctype.replace('_', ' ')}\" comment on the "
        f'"{section}" section for {company}:\n\n'
        f'"{comment_text}"\n\n'
        f"Generate 2-4 short, specific clarifying questions to gather enough detail "
        f"to make the right edit. Be direct and conversational. Number each question. "
        f"Do NOT repeat what they already said — ask only what is MISSING to take action."
    )

    result, source = _call_llm(prompt, tier_label="clarifying questions")
    if result:
        return result, source

    # Tier 3: template
    template = QUESTION_TEMPLATES.get(ctype, QUESTION_TEMPLATES["feedback"])
    return template, "template"


def process_comment(comment_id):
    """
    Main entry point for processing a single comment.

    Fetches the comment, determines what action to take based on status,
    and drives it forward one step.

    Returns True if an action was taken, False if skipped.
    """
    rows = supa_get("page_comments", f"id=eq.{comment_id}&select=*")
    if not rows:
        log.warning(f"process_comment: comment {comment_id} not found")
        return False

    comment = rows[0]
    status = comment.get("status", "pending")
    ctype = comment.get("comment_type", "feedback")

    # Approvals get acknowledged without clarification
    if ctype == "approval":
        _handle_approval(comment)
        return True

    if status == "pending":
        return _step_generate_questions(comment)
    elif status == "awaiting_response" and comment.get("user_response"):
        # User has replied — trigger revision
        return _step_generate_revision(comment)
    else:
        log.debug(f"process_comment: comment {comment_id} in status={status}, no action")
        return False


def apply_revision(comment_id, revision_text=None):
    """
    Mark a revision_ready comment as applied.

    If revision_text is provided, it overrides the stored revised_content.
    Also sets revision_applied=True on the record.

    Returns the patched comment dict.
    """
    updates = {
        "status": "applied",
        "revision_applied": True,
    }
    if revision_text:
        updates["revised_content"] = revision_text

    thread_rows = supa_get("page_comments", f"id=eq.{comment_id}&select=conversation_thread,company_name,section_id")
    if thread_rows:
        thread = thread_rows[0].get("conversation_thread") or []
        thread.append({
            "role": "system",
            "text": "Revision applied.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        updates["conversation_thread"] = json.dumps(thread)

    result = patch_comment(comment_id, updates)
    log.info(f"apply_revision: comment {comment_id} marked applied")
    return result


# ---------------------------------------------------------------------------
# Internal step handlers
# ---------------------------------------------------------------------------

def _step_generate_questions(comment):
    """Step: pending → awaiting_response. Generate and store clarifying questions."""
    cid = comment["id"]
    comment_text = comment.get("comment_text", "")
    page_context = {
        "comment_type": comment.get("comment_type", "feedback"),
        "company_name": comment.get("company_name", ""),
        "section_id": comment.get("section_id", ""),
        "commenter": comment.get("commenter", ""),
        "page_type": comment.get("page_type", ""),
    }

    # Mark as clarifying (transient) to prevent double-processing
    patch_comment(cid, {"status": "clarifying"})

    questions_str, source = generate_clarifying_questions(comment_text, page_context)

    # Parse into list for clarifying_questions JSONB field
    questions_list = []
    for line in questions_str.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            questions_list.append(line.lstrip("0123456789.-) ").strip())
        elif line and not questions_list:
            questions_list.append(line)

    # Build updated thread
    thread = comment.get("conversation_thread") or []
    thread.append({
        "role": "system",
        "text": questions_str,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    patch_comment(cid, {
        "reply": questions_str,
        "status": "awaiting_response",
        "clarifying_questions": json.dumps(questions_list),
        "conversation_thread": json.dumps(thread),
    })

    log.info(
        f"_step_generate_questions: comment {cid} ({page_context['comment_type']}) "
        f"for {page_context['company_name']} — questions via {source}, "
        f"now awaiting_response"
    )
    return True


def _step_generate_revision(comment):
    """Step: awaiting_response (with user_response) → revision_ready."""
    cid = comment["id"]
    company = comment.get("company_name", "")
    section = comment.get("section_id", "")
    page_type = comment.get("page_type", "")
    ctype = comment.get("comment_type", "feedback")
    original = comment.get("original_content", "") or ""
    user_response = comment.get("user_response", "")
    reply = comment.get("reply", "")

    prompt = (
        f"You are rewriting a section of a company dossier based on user feedback.\n\n"
        f"Company: {company}\n"
        f"Page type: {page_type}\n"
        f"Section: {section}\n\n"
        f"Original section content:\n"
        f"{original if original else '(Content not available — generate from feedback context)'}\n\n"
        f"Comment type: {ctype.replace('_', ' ')}\n"
        f"Original comment: {comment.get('comment_text', '')}\n"
        f"Clarifying questions asked: {reply}\n"
        f"User's answers: {user_response}\n\n"
        f"Write the REVISED section content incorporating all feedback. "
        f"Final copy only — no commentary, no 'here is what I changed' notes. "
        f"Match the existing tone and format."
    )

    revised, source = _call_llm(prompt, tier_label="revision generation")
    if not revised:
        log.error(f"_step_generate_revision: all LLM tiers failed for comment {cid}")
        # Reset to awaiting_response so it retries next cycle
        patch_comment(cid, {"status": "awaiting_response"})
        return False

    thread = comment.get("conversation_thread") or []
    thread.append({
        "role": "system",
        "text": "[Revision generated]",
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    patch_comment(cid, {
        "revised_content": revised,
        "status": "revision_ready",
        "conversation_thread": json.dumps(thread),
    })

    log.info(
        f"_step_generate_revision: comment {cid} — revision via {source}, "
        f"now revision_ready"
    )
    return True


def _handle_approval(comment):
    """Approval comments get acknowledged; no clarification loop needed."""
    cid = comment["id"]
    commenter = comment.get("commenter", "user")
    company = comment.get("company_name", "")
    section = comment.get("section_id", "")

    thread = [{
        "role": "system",
        "text": f"Noted — {commenter} approved this section.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }]

    patch_comment(cid, {
        "reply": f"Acknowledged. {commenter} approved this section.",
        "status": "acknowledged",
        "conversation_thread": json.dumps(thread),
    })
    log.info(f"_handle_approval: {company}/{section} approved by {commenter}")


# ---------------------------------------------------------------------------
# Polling daemon
# ---------------------------------------------------------------------------

POLL_INTERVAL = 60  # seconds


def _poll_once():
    """Single pass: process all actionable comments."""
    # Pending → generate clarifying questions
    try:
        pending = supa_get("page_comments", "status=eq.pending&order=created_at.asc")
        for comment in pending:
            try:
                process_comment(comment["id"])
            except Exception as e:
                log.error(f"Error processing pending comment {comment['id']}: {e}", exc_info=True)
    except Exception as e:
        log.error(f"Error fetching pending comments: {e}")

    # awaiting_response WITH a user_response → generate revision
    try:
        awaiting = supa_get(
            "page_comments",
            "status=eq.awaiting_response&user_response=not.is.null&order=created_at.asc",
        )
        for comment in awaiting:
            if comment.get("user_response", "").strip():
                try:
                    _step_generate_revision(comment)
                except Exception as e:
                    log.error(f"Error generating revision for {comment['id']}: {e}", exc_info=True)
    except Exception as e:
        log.error(f"Error fetching awaiting_response comments: {e}")


def run_daemon():
    """
    60-second poll loop. Always on, always ready.
    Exits cleanly on KeyboardInterrupt.
    """
    log.info("=" * 60)
    log.info("Feedback Agent started (Feature #45 — D→C Feedback Conversation)")
    log.info(f"LLM chain: Claude CLI → OpenRouter DeepSeek V3 → Template")
    log.info(f"Poll interval: {POLL_INTERVAL}s")
    log.info("=" * 60)

    while True:
        try:
            _poll_once()
        except KeyboardInterrupt:
            log.info("Feedback Agent shutting down")
            break
        except Exception as e:
            log.error(f"Unhandled error in poll loop: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--once" in sys.argv:
        _poll_once()
    elif "--comment" in sys.argv:
        idx = sys.argv.index("--comment")
        if idx + 1 < len(sys.argv):
            cid = sys.argv[idx + 1]
            result = process_comment(cid)
            print(f"process_comment({cid}) → {result}")
        else:
            print("Usage: feedback_agent.py --comment <comment_id>")
    elif "--apply" in sys.argv:
        idx = sys.argv.index("--apply")
        if idx + 1 < len(sys.argv):
            cid = sys.argv[idx + 1]
            apply_revision(cid)
            print(f"Revision applied for comment {cid}")
        else:
            print("Usage: feedback_agent.py --apply <comment_id>")
    else:
        run_daemon()
