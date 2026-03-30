#!/usr/bin/env python3
"""
transcript_processor.py — Transcript → Action Items
Feature #59: Process Fireflies transcripts into structured action items.

Uses Claude CLI for extraction. Stores results in meeting_actions table.
"""

import json, os, subprocess
from datetime import datetime

import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ctx = ssl.create_default_context()

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


EXTRACTION_PROMPT = """Analyze this meeting transcript and extract structured data. Return valid JSON only.

{
  "action_items": [
    {"who": "person name", "what": "action description", "by_when": "date or timeframe", "priority": "high|medium|low"}
  ],
  "key_decisions": [
    {"decision": "what was decided", "context": "why"}
  ],
  "follow_up_questions": [
    "question that needs answering"
  ],
  "emotional_signals": {
    "excitement_level": 1-10,
    "concern_areas": ["list of concerns"],
    "objections": ["any objections raised"],
    "buying_signals": ["positive indicators"]
  },
  "pricing_discussions": {
    "mentioned": true/false,
    "details": "any pricing details discussed",
    "range": "any price range mentioned"
  },
  "next_meeting": {
    "scheduled": true/false,
    "date": "date if mentioned",
    "topic": "planned discussion topic"
  },
  "summary": "2-3 sentence executive summary of the meeting"
}

TRANSCRIPT:
"""


def process_transcript(transcript_text, meeting_id=None, entity="next_chapter"):
    """
    Process a transcript and extract structured action items.
    Uses Claude CLI for intelligent extraction.
    """
    prompt = EXTRACTION_PROMPT + transcript_text[:15000]  # Limit to ~15K chars

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()

        # Parse JSON from response
        json_start = output.find("{")
        json_end = output.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            extracted = json.loads(output[json_start:json_end])
        else:
            extracted = {"error": "Could not parse JSON from LLM response", "raw": output[:500]}

    except subprocess.TimeoutExpired:
        extracted = {"error": "Claude CLI timeout"}
    except json.JSONDecodeError as e:
        extracted = {"error": f"JSON parse error: {str(e)}"}
    except FileNotFoundError:
        extracted = {"error": "Claude CLI not found"}

    # Store results
    if meeting_id and "error" not in extracted:
        # Store action items
        for item in extracted.get("action_items", []):
            _sb_post("meeting_actions", {
                "meeting_id": meeting_id,
                "entity": entity,
                "action_type": "action_item",
                "who": item.get("who", ""),
                "what": item.get("what", ""),
                "by_when": item.get("by_when", ""),
                "priority": item.get("priority", "medium"),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            })

        # Store decisions
        for decision in extracted.get("key_decisions", []):
            _sb_post("meeting_actions", {
                "meeting_id": meeting_id,
                "entity": entity,
                "action_type": "decision",
                "what": decision.get("decision", ""),
                "notes": decision.get("context", ""),
                "status": "recorded",
                "created_at": datetime.utcnow().isoformat(),
            })

        # Store follow-up questions
        for question in extracted.get("follow_up_questions", []):
            _sb_post("meeting_actions", {
                "meeting_id": meeting_id,
                "entity": entity,
                "action_type": "follow_up_question",
                "what": question,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            })

        # Create play record for follow-up
        emotional = extracted.get("emotional_signals", {})
        if emotional.get("excitement_level", 0) >= 7:
            _sb_post("plays", {
                "entity": entity,
                "signal_source": "transcript",
                "signal_type": "meeting_completed",
                "play_name": "hot_lead_from_meeting",
                "urgency": min(emotional["excitement_level"], 10),
                "notes": extracted.get("summary", ""),
                "status": "staged",
                "created_at": datetime.utcnow().isoformat(),
            })

    return extracted


def process_fireflies_transcript(transcript_id):
    """Fetch and process a Fireflies transcript by ID."""
    # Check if already processed
    existing = _sb_get("step_log", f"target_id=eq.{transcript_id}&step=eq.transcript_processed&limit=1")
    if existing:
        return {"status": "already_processed", "transcript_id": transcript_id}

    # Fetch transcript from Supabase (assume stored via Fireflies webhook)
    transcripts = _sb_get("transcripts", f"fireflies_id=eq.{transcript_id}&limit=1")
    if not transcripts:
        return {"error": f"Transcript not found: {transcript_id}"}

    transcript = transcripts[0]
    text = transcript.get("text", transcript.get("transcript_text", ""))
    meeting_id = transcript.get("meeting_id")
    entity = transcript.get("entity", "next_chapter")

    result = process_transcript(text, meeting_id, entity)

    # Log completion
    _sb_post("step_log", {
        "target_id": transcript_id,
        "step": "transcript_processed",
        "entity": entity,
        "metadata": json.dumps({
            "action_items": len(result.get("action_items", [])),
            "decisions": len(result.get("key_decisions", [])),
        }),
        "completed_at": datetime.utcnow().isoformat(),
    })

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Transcript → Action Items")
    parser.add_argument("--transcript-id", help="Process Fireflies transcript by ID")
    parser.add_argument("--file", help="Process transcript from file")
    parser.add_argument("--meeting-id", help="Associated meeting ID")
    parser.add_argument("--entity", default="next_chapter")
    args = parser.parse_args()

    if args.transcript_id:
        result = process_fireflies_transcript(args.transcript_id)
        print(json.dumps(result, indent=2, default=str))
    elif args.file:
        with open(args.file) as f:
            text = f.read()
        result = process_transcript(text, args.meeting_id, args.entity)
        print(json.dumps(result, indent=2, default=str))
