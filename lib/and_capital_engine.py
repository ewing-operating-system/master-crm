#!/usr/bin/env python3
"""
and_capital_engine.py — AND Capital Entity Support
Feature #60: LP fundraising, fund decks, investor CRM.
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


LP_STAGES = ["prospect", "intro_meeting", "due_diligence", "term_sheet", "committed", "funded"]


def get_fund_overview():
    """Fetch fund metrics from Supabase."""
    funds = _sb_get("and_targets", "entity=eq.and_capital&select=*&limit=100")
    total_target = sum(float(f.get("target_raise", 0) or 0) for f in funds)
    total_committed = sum(float(f.get("committed_capital", 0) or 0) for f in funds)
    return {
        "total_funds": len(funds),
        "target_raise": total_target,
        "committed_capital": total_committed,
        "pct_raised": round(total_committed / total_target * 100, 1) if total_target else 0,
        "funds": funds,
    }


def get_lp_pipeline():
    """LP funnel by stage."""
    investors = _sb_get("and_contacts", "entity=eq.and_capital&select=*&order=stage.asc")
    pipeline = {stage: [] for stage in LP_STAGES}
    for inv in investors:
        stage = inv.get("stage", "prospect")
        if stage in pipeline:
            pipeline[stage].append(inv)
    return {
        "total_lps": len(investors),
        "by_stage": {s: len(v) for s, v in pipeline.items()},
        "pipeline": pipeline,
    }


def track_deck_distribution(lp_id, fund_id):
    """Log fund deck send to an LP."""
    return _sb_post("step_log", {
        "target_id": lp_id,
        "step": "deck_sent",
        "entity": "and_capital",
        "metadata": json.dumps({"fund_id": fund_id, "sent_at": datetime.utcnow().isoformat()}),
        "completed_at": datetime.utcnow().isoformat(),
    })


def create_lp_outreach(lp_id, campaign="AND-LP-LETTER"):
    """Generate LP outreach sequence."""
    lps = _sb_get("contacts", f"id=eq.{lp_id}&limit=1")
    if not lps:
        return {"error": f"LP not found: {lp_id}"}
    lp = lps[0]
    return _sb_post("plays", {
        "entity": "and_capital",
        "target_id": lp_id,
        "signal_source": "outreach",
        "signal_type": "lp_outreach",
        "play_name": campaign,
        "contact_name": f"{lp.get('first_name', '')} {lp.get('last_name', '')}",
        "urgency": 6,
        "status": "staged",
        "created_at": datetime.utcnow().isoformat(),
    })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AND Capital Engine")
    parser.add_argument("--overview", action="store_true")
    parser.add_argument("--pipeline", action="store_true")
    parser.add_argument("--outreach", help="Create LP outreach for lp_id")
    args = parser.parse_args()
    if args.overview:
        print(json.dumps(get_fund_overview(), indent=2, default=str))
    elif args.pipeline:
        print(json.dumps(get_lp_pipeline(), indent=2, default=str))
    elif args.outreach:
        print(json.dumps(create_lp_outreach(args.outreach), indent=2, default=str))
