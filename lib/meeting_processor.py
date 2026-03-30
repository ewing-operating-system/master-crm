#!/usr/bin/env python3
"""
Meeting Processor — extracts structured data from Fireflies transcripts
and populates the CRM. Protects client-validated data from overwrite.

RULE: Data confirmed directly by the client (owner/seller) in a meeting
is "client_validated" and CANNOT be overwritten by system estimates,
research, or other automated processes. Only a newer client meeting
can update client-validated fields.
"""

import json, os, sys, subprocess, psycopg2, psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_CONN = f"postgresql://postgres:{os.environ.get('DB_PASSWORD', '')}@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"

def log(msg):
    print(f"{datetime.utcnow().isoformat()} | MEETING_PROCESSOR | {msg}", flush=True)

def extract_meeting_data(transcript_text, summary_data):
    """Use Claude CLI to extract structured data from a transcript."""
    prompt = f"""Extract structured business data from this meeting transcript.
This is a meeting between Next Chapter Advisory (Ewing Gillaspy, John Kelly) and a potential client.

TRANSCRIPT SUMMARY:
{json.dumps(summary_data, indent=2)}

FULL TRANSCRIPT:
{transcript_text[:15000]}

Extract the following as JSON. Only include fields where data was EXPLICITLY stated by the client (not inferred):

{{
  "client_name": "Full name of the business owner/seller",
  "client_email": "Email if mentioned or visible",
  "company_name": "Company name",
  "exit_timeline": "When they want to exit (e.g., '12-24 months', 'ASAP')",
  "exit_motivation": "Why they want to exit",
  "estimated_revenue": "Revenue figure if stated (number only, in dollars)",
  "ebitda_margin": "EBITDA margin if stated (percentage as decimal)",
  "employee_count": "Number of employees if stated",
  "vertical": "Industry/vertical",
  "city": "City",
  "state": "State",
  "assets": [
    {{"name": "asset name", "description": "what it is", "estimated_value_low": number, "estimated_value_high": number, "notes": "any details"}}
  ],
  "action_items": [
    {{"owner": "who", "task": "what", "due": "when"}}
  ],
  "key_relationships": ["names of key people mentioned and their relevance"],
  "deal_notes": "Any critical deal intelligence, emotional signals, personal details that matter",
  "competitive_intel": "Other buyers, brokers, or processes mentioned",
  "owner_personal": "Personal details relevant to deal timing (health, family, travel)"
}}

ONLY include data that was DIRECTLY STATED in the meeting. Do not infer or estimate. If a field wasn't discussed, omit it.
Return ONLY valid JSON."""

    try:
        result = subprocess.run(["claude", "-p", "--output-format", "text"],
                                input=prompt, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and result.stdout.strip():
            text = result.stdout.strip()
            # Find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
    except Exception as e:
        log(f"Claude extraction error: {e}")
    return None

def update_proposal_with_meeting(proposal_id, meeting_data, transcript_id, meeting_date):
    """
    Update proposal with meeting-extracted data.
    RULE: Only update fields that are NOT already client_validated,
    OR if the new data is ALSO client-validated (from a newer meeting).
    Mark all fields updated from this meeting as client_validated.
    """
    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get current proposal
    cur.execute("SELECT * FROM proposals WHERE id = %s", (proposal_id,))
    proposal = cur.fetchone()
    if not proposal:
        log(f"Proposal {proposal_id} not found")
        conn.close()
        return None

    current_validated = proposal.get('client_validated_fields') or {}
    current_history = proposal.get('meeting_history') or []

    # Build the meeting record
    meeting_record = {
        "date": meeting_date,
        "fireflies_id": transcript_id,
        "extracted_data": meeting_data,
        "processed_at": datetime.utcnow().isoformat(),
        "source": "fireflies_transcript"
    }
    current_history.append(meeting_record)

    # Build update fields — only update if NOT already client_validated by a MORE RECENT meeting
    updates = {}
    newly_validated = {}

    field_mapping = {
        "estimated_revenue": "estimated_revenue",
        "ebitda_margin": "ebitda_margin",
        "employee_count": "employee_count",
        "vertical": "vertical",
        "city": "city",
        "state": "state",
        "exit_timeline": "exit_timeline",
        "exit_motivation": "exit_motivation",
        "client_email": "owner_email",
        "client_name": "owner_name",
    }

    for src_field, db_field in field_mapping.items():
        value = meeting_data.get(src_field)
        if value is None or value == "":
            continue

        # Check if this field was validated by a MORE RECENT meeting
        existing_validation = current_validated.get(db_field, {})
        existing_date = existing_validation.get("validated_at", "")

        if existing_date and existing_date > meeting_date:
            log(f"  SKIP {db_field}: already validated by newer meeting ({existing_date})")
            continue

        updates[db_field] = value
        newly_validated[db_field] = {
            "validated_at": meeting_date,
            "source": "client_meeting",
            "transcript_id": transcript_id,
            "original_value": str(value)
        }
        log(f"  SET {db_field} = {value} [CLIENT VALIDATED]")

    # Merge validated fields
    current_validated.update(newly_validated)

    # Build SQL update
    set_clauses = [
        "client_validated_fields = %s",
        "meeting_history = %s",
        "last_meeting_date = %s",
        "fireflies_transcript_id = %s",
    ]
    values = [
        json.dumps(current_validated, default=str),
        json.dumps(current_history, default=str),
        meeting_date,
        transcript_id,
    ]

    if meeting_data.get("assets"):
        set_clauses.append("assets_summary = %s")
        values.append(json.dumps(meeting_data["assets"], default=str))

    if meeting_data.get("action_items"):
        set_clauses.append("action_items = %s")
        values.append(json.dumps(meeting_data["action_items"], default=str))

    for db_field, value in updates.items():
        set_clauses.append(f"{db_field} = %s")
        values.append(value)

    values.append(proposal_id)
    sql = f"UPDATE proposals SET {', '.join(set_clauses)} WHERE id = %s RETURNING *"
    cur.execute(sql, values)
    result = cur.fetchone()
    conn.close()

    return result

def store_meeting_in_cache(company_name, meeting_data, transcript_id, meeting_date):
    """Also store in intelligence_cache for the company hub."""
    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cur = conn.cursor()

    cache_data = {
        "meeting_date": meeting_date,
        "transcript_id": transcript_id,
        "summary": meeting_data.get("deal_notes", ""),
        "action_items": meeting_data.get("action_items", []),
        "assets": meeting_data.get("assets", []),
        "key_relationships": meeting_data.get("key_relationships", []),
        "competitive_intel": meeting_data.get("competitive_intel", ""),
        "owner_personal": meeting_data.get("owner_personal", ""),
        "client_validated": True,
        "processed_at": datetime.utcnow().isoformat()
    }

    cur.execute("""INSERT INTO intelligence_cache (company_id, entity, key, value, source_agent)
        SELECT c.id, 'next_chapter', %s, %s, 'meeting_processor'
        FROM companies c WHERE c.company_name ILIKE %s LIMIT 1""",
        (f"meeting_{meeting_date}", json.dumps(cache_data, default=str), f"%{company_name}%"))

    conn.close()
    log(f"  Stored meeting in intelligence_cache for {company_name}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal-id", required=True)
    parser.add_argument("--transcript-id", required=True)
    parser.add_argument("--meeting-date", required=True)
    parser.add_argument("--transcript-file", help="Path to transcript text file")
    parser.add_argument("--summary-file", help="Path to summary JSON file")
    args = parser.parse_args()

    transcript_text = ""
    summary_data = {}

    if args.transcript_file:
        with open(args.transcript_file) as f:
            transcript_text = f.read()

    if args.summary_file:
        with open(args.summary_file) as f:
            summary_data = json.load(f)

    log(f"Processing meeting {args.transcript_id} for proposal {args.proposal_id}")

    meeting_data = extract_meeting_data(transcript_text, summary_data)
    if not meeting_data:
        log("ERROR: Could not extract meeting data")
        sys.exit(1)

    log(f"Extracted: {json.dumps(meeting_data, indent=2, default=str)}")

    result = update_proposal_with_meeting(args.proposal_id, meeting_data, args.transcript_id, args.meeting_date)
    if result:
        log(f"Updated proposal: {result.get('company_name')}")

    store_meeting_in_cache(
        meeting_data.get("company_name", ""),
        meeting_data, args.transcript_id, args.meeting_date
    )

    log("DONE")
