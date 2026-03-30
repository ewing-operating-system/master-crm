#!/usr/bin/env python3
"""
situation_library.py — Situation Library + Play Templates
Feature #51: Auto-detect situations, pick plays, graduated trust scoring.

Usage:
    from lib.situation_library import match_situation, create_play, get_active_plays
"""

import json, os
from datetime import datetime

import urllib.request, ssl

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

ctx = ssl.create_default_context()

def _sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def _sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_sb_headers())
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=_sb_headers(), method="POST")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())

def _sb_patch(table, params, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, data=json.dumps(data, default=str).encode(), headers=_sb_headers(), method="PATCH")
    return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())


# ---------------------------------------------------------------------------
# Situation types
# ---------------------------------------------------------------------------
SITUATIONS = {
    "letter_delivered": {"category": "outreach", "default_urgency": 5, "auto_play": "follow_up_call"},
    "letter_returned": {"category": "data_quality", "default_urgency": 6, "auto_play": "address_correction"},
    "call_connected": {"category": "engagement", "default_urgency": 8, "auto_play": "post_call_nurture"},
    "call_voicemail": {"category": "outreach", "default_urgency": 4, "auto_play": "voicemail_follow_up"},
    "call_gatekeeper": {"category": "outreach", "default_urgency": 5, "auto_play": "gatekeeper_bypass"},
    "call_bad_number": {"category": "data_quality", "default_urgency": 3, "auto_play": "data_enrichment"},
    "email_replied": {"category": "engagement", "default_urgency": 8, "auto_play": "email_response_handler"},
    "email_opened": {"category": "engagement", "default_urgency": 6, "auto_play": "warm_call_trigger"},
    "meeting_booked": {"category": "conversion", "default_urgency": 9, "auto_play": "meeting_prep_auto"},
    "meeting_completed": {"category": "conversion", "default_urgency": 8, "auto_play": "post_meeting_processing"},
    "competitor_detected": {"category": "competitive", "default_urgency": 9, "auto_play": "competitive_rapid_response"},
    "price_objection": {"category": "objection", "default_urgency": 7, "auto_play": "value_reframe"},
    "timing_not_right": {"category": "objection", "default_urgency": 4, "auto_play": "nurture_sequence"},
    "interested_but_later": {"category": "nurture", "default_urgency": 4, "auto_play": "nurture_sequence"},
    "warm_referral": {"category": "inbound", "default_urgency": 9, "auto_play": "referral_fast_track"},
    "inbound_inquiry": {"category": "inbound", "default_urgency": 10, "auto_play": "inbound_response"},
    "website_visit": {"category": "engagement", "default_urgency": 5, "auto_play": "warm_call_trigger"},
}


# ---------------------------------------------------------------------------
# Play templates
# ---------------------------------------------------------------------------
PLAY_TEMPLATES = {
    "follow_up_call": {
        "name": "Follow-Up Call",
        "trigger": "letter_delivered",
        "actions": ["wait_3_days", "queue_salesfinity_call", "prepare_call_script"],
        "timing_rules": {"delay_days": 3, "max_attempts": 5},
        "trust_level_required": 3,
    },
    "address_correction": {
        "name": "Address Correction",
        "trigger": "letter_returned",
        "actions": ["research_correct_address", "update_contact", "resend_letter"],
        "timing_rules": {"delay_days": 0, "max_attempts": 2},
        "trust_level_required": 5,
    },
    "post_call_nurture": {
        "name": "Post-Call Nurture",
        "trigger": "call_connected",
        "actions": ["send_follow_up_email", "create_meeting_invite", "update_pipeline_stage"],
        "timing_rules": {"delay_hours": 2, "max_attempts": 1},
        "trust_level_required": 5,
    },
    "hot_lead_escalation": {
        "name": "Hot Lead Escalation",
        "trigger": "call_connected_long",
        "actions": ["notify_ewing", "create_proposal", "send_data_room", "book_meeting"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 1,
    },
    "voicemail_follow_up": {
        "name": "Voicemail Follow-Up",
        "trigger": "call_voicemail",
        "actions": ["schedule_retry_in_2_days", "send_email_touch"],
        "timing_rules": {"delay_days": 2, "max_attempts": 3},
        "trust_level_required": 5,
    },
    "gatekeeper_bypass": {
        "name": "Gatekeeper Bypass",
        "trigger": "call_gatekeeper",
        "actions": ["try_direct_line", "try_email", "try_linkedin", "try_different_time"],
        "timing_rules": {"delay_days": 1, "max_attempts": 3},
        "trust_level_required": 5,
    },
    "data_enrichment": {
        "name": "Data Enrichment",
        "trigger": "call_bad_number",
        "actions": ["enrich_phone_number", "flag_data_quality", "update_contact"],
        "timing_rules": {"delay_days": 0, "max_attempts": 1},
        "trust_level_required": 8,
    },
    "email_response_handler": {
        "name": "Email Response Handler",
        "trigger": "email_replied",
        "actions": ["classify_sentiment", "route_to_operator", "draft_response"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 3,
    },
    "warm_call_trigger": {
        "name": "Warm Call Trigger",
        "trigger": "email_opened",
        "actions": ["queue_immediate_call", "note_engagement_signal"],
        "timing_rules": {"delay_hours": 1, "max_attempts": 1},
        "trust_level_required": 5,
    },
    "meeting_prep_auto": {
        "name": "Auto Meeting Prep",
        "trigger": "meeting_booked",
        "actions": ["generate_meeting_page", "pull_latest_research", "create_agenda", "notify_team"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 3,
    },
    "post_meeting_processing": {
        "name": "Post-Meeting Processing",
        "trigger": "meeting_completed",
        "actions": ["process_transcript", "extract_action_items", "send_follow_up", "update_pipeline"],
        "timing_rules": {"delay_hours": 1, "max_attempts": 1},
        "trust_level_required": 5,
    },
    "competitive_rapid_response": {
        "name": "Competitive Rapid Response",
        "trigger": "competitor_detected",
        "actions": ["pull_competitor_intel", "adjust_proposal_positioning", "accelerate_timeline", "offer_90_day_guarantee"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 1,
    },
    "value_reframe": {
        "name": "Value Reframe",
        "trigger": "price_objection",
        "actions": ["pull_comp_data", "reframe_value_proposition", "share_case_studies"],
        "timing_rules": {"delay_hours": 4, "max_attempts": 2},
        "trust_level_required": 5,
    },
    "nurture_sequence": {
        "name": "Nurture Sequence",
        "trigger": "interested_but_later",
        "actions": ["add_to_30_day_nurture", "send_market_update_monthly", "schedule_check_in"],
        "timing_rules": {"delay_days": 30, "max_attempts": 6},
        "trust_level_required": 8,
    },
    "referral_fast_track": {
        "name": "Referral Fast Track",
        "trigger": "warm_referral",
        "actions": ["research_referred_company", "generate_letter_priority", "queue_priority_call", "thank_referrer"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 1,
    },
    "inbound_response": {
        "name": "Inbound Response",
        "trigger": "inbound_inquiry",
        "actions": ["respond_within_1_hour", "full_research", "generate_proposal", "book_meeting"],
        "timing_rules": {"delay_hours": 0, "max_attempts": 1},
        "trust_level_required": 1,
    },
}


def match_situation(signal):
    """Match a signal to a situation and return the play template."""
    signal_type = signal.get("signal_type", signal.get("situation", ""))
    situation = SITUATIONS.get(signal_type)
    if not situation:
        return None

    play_name = situation["auto_play"]
    play = PLAY_TEMPLATES.get(play_name)
    if not play:
        return None

    return {
        "situation": signal_type,
        "category": situation["category"],
        "urgency": situation["default_urgency"],
        "play": play,
    }


def create_play(situation, target_id, entity):
    """Create a play record in Supabase plays table."""
    match = match_situation({"signal_type": situation})
    if not match:
        return {"error": f"No play template for situation: {situation}"}

    play = match["play"]
    record = {
        "entity": entity,
        "target_id": target_id,
        "signal_type": situation,
        "play_name": play["name"],
        "urgency": match["urgency"],
        "actions": json.dumps(play["actions"]),
        "timing_rules": json.dumps(play["timing_rules"]),
        "trust_level_required": play["trust_level_required"],
        "status": "staged",
        "created_at": datetime.utcnow().isoformat(),
    }

    return _sb_post("plays", record)


def get_active_plays(entity=None):
    """Return all active plays, optionally filtered by entity."""
    params = "status=in.(staged,in_progress)&order=urgency.desc"
    if entity:
        params += f"&entity=eq.{entity}"
    return _sb_get("plays", params)


def get_play_history(target_id):
    """Get play history for a target."""
    return _sb_get("plays", f"target_id=eq.{target_id}&order=created_at.desc")


def list_situations():
    """List all situation types."""
    return SITUATIONS


def list_play_templates():
    """List all play templates."""
    return PLAY_TEMPLATES


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Situation Library")
    parser.add_argument("--list-situations", action="store_true")
    parser.add_argument("--list-plays", action="store_true")
    parser.add_argument("--active", help="Get active plays for entity")
    parser.add_argument("--create", help="Create play: situation:target_id:entity")
    args = parser.parse_args()

    if args.list_situations:
        print(json.dumps(list_situations(), indent=2))
    elif args.list_plays:
        print(json.dumps(list_play_templates(), indent=2))
    elif args.active:
        print(json.dumps(get_active_plays(args.active), indent=2, default=str))
    elif args.create:
        parts = args.create.split(":")
        if len(parts) == 3:
            print(json.dumps(create_play(parts[0], parts[1], parts[2]), indent=2, default=str))
