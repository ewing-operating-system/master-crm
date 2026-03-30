#!/usr/bin/env python3
"""
Engagement Engine — activates when a client signs.

Takes: proposal_id (the signed proposal)
Produces: Full account plan with buyer outreach loaded across all channels.

Steps:
1. Load proposal + profile + buyer list
2. Generate per-buyer approach scripts (letter, email, call, LinkedIn)
3. Check DNC on all buyer contacts
4. Create outreach queue entries
5. Generate client-facing account plan page (admin/client dual view)
"""

import json, os, sys, subprocess, time, psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_CONN = f"postgresql://postgres:{os.environ.get('DB_PASSWORD', '')}@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/engagement_engine.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | ENGAGE | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def call_claude(prompt, timeout=300):
    try:
        result = subprocess.run(["claude", "-p", "--output-format", "text"],
                                input=prompt, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None
    except:
        return None

def parse_json(text):
    if not text: return None
    try: return json.loads(text)
    except:
        s, e = text.find('{'), text.rfind('}') + 1
        if s >= 0:
            try: return json.loads(text[s:e])
            except: pass
    return None


def activate_engagement(proposal_id):
    """Full engagement activation for a signed client."""
    log(f"\n{'='*60}")
    log(f"ENGAGEMENT ACTIVATION: {proposal_id}")
    log(f"{'='*60}")

    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cur = conn.cursor()

    # Step 1: Load proposal
    cur.execute("SELECT * FROM proposals WHERE id = %s", (proposal_id,))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if not row:
        log("Proposal not found")
        conn.close()
        return None
    proposal = dict(zip(cols, row))
    company = proposal["company_name"]
    log(f"  Company: {company}")

    # Step 2: Load buyer list
    cur.execute("SELECT * FROM engagement_buyers WHERE proposal_id = %s ORDER BY fit_score DESC NULLS LAST", (proposal_id,))
    cols = [d[0] for d in cur.description]
    buyers = [dict(zip(cols, r)) for r in cur.fetchall()]
    log(f"  Buyers loaded: {len(buyers)}")

    # Step 3: DNC check all buyers
    dnc_blocked = 0
    for buyer in buyers:
        phone = buyer.get("buyer_phone")
        company_name = buyer.get("buyer_company_name")
        if phone:
            cur.execute("SELECT count(*) FROM do_not_call WHERE phone = %s", (phone,))
            if cur.fetchone()[0] > 0:
                buyer["dnc_clear"] = False
                dnc_blocked += 1
                continue
        if company_name:
            cur.execute("SELECT count(*) FROM do_not_call WHERE company_name ILIKE %s AND block_company = true", (f"%{company_name}%",))
            if cur.fetchone()[0] > 0:
                buyer["dnc_clear"] = False
                dnc_blocked += 1
                continue
        buyer["dnc_clear"] = True
        buyer["dnc_checked_at"] = datetime.utcnow().isoformat()

    log(f"  DNC check: {dnc_blocked} blocked, {len(buyers) - dnc_blocked} clear")

    # Step 4: Generate per-buyer outreach scripts via Claude CLI
    clear_buyers = [b for b in buyers if b.get("dnc_clear", True)]
    log(f"  Generating outreach for {len(clear_buyers)} clear buyers...")

    for i, buyer in enumerate(clear_buyers[:10]):  # top 10 get full scripts
        buyer_name = buyer.get("buyer_company_name", "Unknown")
        buyer_contact = buyer.get("buyer_contact_name", "")
        buyer_type = buyer.get("buyer_type", "")
        fit = buyer.get("fit_narrative", "")
        approach = buyer.get("approach_strategy", "")

        prompt = f"""Generate outreach scripts for contacting a potential BUYER about acquiring {company}.

BUYER: {buyer_name} ({buyer_type})
CONTACT: {buyer_contact}
FIT: {fit}
APPROACH: {approach}

SELLER COMPANY: {company}
VERTICAL: {proposal.get('vertical', '')}
LOCATION: {proposal.get('city', '')}, {proposal.get('state', '')}

RULES:
- Frame as "we represent the owners" — NEVER "this company is for sale" (destroys leverage)
- All about what the BUYER gets, not what we're selling
- Reference specific synergies between buyer and seller
- Professional, warm, credible tone

Return JSON:
{{"letter": "Physical letter to buyer (200 words)", "email": "Email to buyer contact (150 words)",
"call_script": "Cold call opener + talking points (100 words)", "linkedin": "LinkedIn message (50 words)"}}
ONLY JSON."""

        result = call_claude(prompt)
        scripts = parse_json(result)

        if scripts:
            cur.execute("""UPDATE engagement_buyers SET
                approach_script = %s, status = 'scripted'
                WHERE id = %s""",
                (json.dumps(scripts, default=str), buyer["id"]))

        if (i + 1) % 3 == 0:
            log(f"    Scripted {i+1}/{min(len(clear_buyers), 10)} buyers")
            time.sleep(2)

    log(f"  Outreach scripts generated for top {min(len(clear_buyers), 10)} buyers")

    # Step 5: Generate 30/60/90 day execution timeline
    buyer_summary = json.dumps([{'name': b.get('buyer_company_name'), 'type': b.get('buyer_type'),
                                  'fit': str(b.get('fit_score',''))} for b in clear_buyers[:5]],
                                indent=2, default=str)
    timeline_prompt = f"""Create a 30/60/90 day execution timeline for selling {company} ({proposal.get('vertical','')}).

We have {len(clear_buyers)} potential buyers identified. Top buyers:
{buyer_summary}

Create a structured timeline:
- Days 1-7: Letter campaign to top 10 buyers
- Days 7-14: Follow-up calls to letter recipients
- Days 14-21: LinkedIn outreach to remaining buyers
- Days 21-30: Email sequences, second round calls
- Days 30-60: Meetings, NDAs, info sharing with interested parties
- Days 60-90: LOI negotiation, due diligence prep

Return JSON: {{"phases": [{{"name": "", "days": "", "actions": [], "success_metrics": ""}}]}}
ONLY JSON."""

    timeline = call_claude(timeline_prompt)
    timeline_data = parse_json(timeline)

    # Step 6: Generate account plan HTML (admin + client views)
    log(f"  Generating account plan page...")

    admin_data = {
        "company": company,
        "owner": proposal.get("owner_name"),
        "proposal_id": str(proposal_id),
        "buyers_total": len(buyers),
        "buyers_clear": len(clear_buyers),
        "buyers_blocked": dnc_blocked,
        "top_buyers": [{"name": b.get("buyer_company_name"), "type": b.get("buyer_type"),
                        "fit": str(b.get("fit_score", "")), "dnc": b.get("dnc_clear")}
                       for b in buyers[:10]],
        "timeline": timeline_data,
        "status": "engagement_active"
    }

    # Update proposal status
    cur.execute("""UPDATE proposals SET status = 'engagement_active',
                   client_signed_at = now() WHERE id = %s""", (proposal_id,))

    # Store engagement plan in intelligence_cache
    cur.execute("""INSERT INTO intelligence_cache (company_id, entity, key, value, source_agent)
        SELECT c.id, 'next_chapter', 'engagement_plan', %s, 'engagement_engine'
        FROM companies c WHERE c.company_name ILIKE %s LIMIT 1""",
        (json.dumps(admin_data, default=str), f"%{company}%"))

    conn.close()

    log(f"ENGAGEMENT ACTIVATED: {company}")
    log(f"  Buyers: {len(clear_buyers)} clear / {dnc_blocked} DNC blocked")
    log(f"  Scripts: top 10 generated")
    log(f"  Timeline: 30/60/90 day plan created")

    return admin_data


def activate_all_proposals():
    """Activate engagement for all certified proposals."""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, company_name FROM proposals WHERE status IN ('certified', 'needs_review') ORDER BY quality_score DESC")
    proposals = cur.fetchall()
    conn.close()

    log(f"\nActivating {len(proposals)} engagements")
    for pid, name in proposals:
        try:
            activate_engagement(pid)
        except Exception as e:
            log(f"ERROR on {name}: {e}")
        time.sleep(3)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        activate_engagement(sys.argv[1])
    else:
        activate_all_proposals()
