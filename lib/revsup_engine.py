#!/usr/bin/env python3
"""
revsup_engine.py — RevsUp Entity Support
Feature #61: Recruiting client outreach, candidate pipeline, placement tracking.
"""

import json, os
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


CANDIDATE_STAGES = ["sourced", "screened", "submitted", "interviewed", "offered", "placed"]


def get_active_engagements():
    """Current client recruiting engagements."""
    return _sb_get("ru_targets", "entity=eq.revsup&status=eq.active&select=*")


def get_candidate_pipeline(engagement_id=None):
    """Candidate funnel, optionally for a specific engagement."""
    params = "entity=eq.revsup&order=stage.asc"
    if engagement_id:
        params += f"&engagement_id=eq.{engagement_id}"
    candidates = _sb_get("ru_contacts", params)
    pipeline = {stage: [] for stage in CANDIDATE_STAGES}
    for c in candidates:
        stage = c.get("stage", "sourced")
        if stage in pipeline:
            pipeline[stage].append(c)
    return {
        "total": len(candidates),
        "by_stage": {s: len(v) for s, v in pipeline.items()},
        "candidates": pipeline,
    }


def track_placement(candidate_id, client_id, fee):
    """Log a placement with revenue."""
    return _sb_post("step_log", {
        "target_id": candidate_id,
        "step": "placement_completed",
        "entity": "revsup",
        "metadata": json.dumps({
            "client_id": client_id,
            "fee": fee,
            "placed_at": datetime.utcnow().isoformat(),
        }),
        "completed_at": datetime.utcnow().isoformat(),
    })


def generate_client_outreach(client_id):
    """Create outreach play for a recruiting client."""
    clients = _sb_get("contacts", f"id=eq.{client_id}&limit=1")
    if not clients:
        return {"error": f"Client not found: {client_id}"}
    client = clients[0]
    return _sb_post("plays", {
        "entity": "revsup",
        "target_id": client_id,
        "signal_source": "outreach",
        "signal_type": "client_outreach",
        "play_name": "RU-CLIENT",
        "contact_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
        "urgency": 6,
        "status": "staged",
        "created_at": datetime.utcnow().isoformat(),
    })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RevsUp Engine")
    parser.add_argument("--engagements", action="store_true")
    parser.add_argument("--pipeline", help="Candidate pipeline for engagement_id")
    parser.add_argument("--outreach", help="Create outreach for client_id")
    args = parser.parse_args()
    if args.engagements:
        print(json.dumps(get_active_engagements(), indent=2, default=str))
    elif args.pipeline:
        print(json.dumps(get_candidate_pipeline(args.pipeline), indent=2, default=str))
    elif args.outreach:
        print(json.dumps(generate_client_outreach(args.outreach), indent=2, default=str))
