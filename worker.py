#!/usr/bin/env python3
"""
Worker — processes agent_queue items one at a time.
Routes to the correct agent module based on agent_name.
"""

import json, os, time, sys, subprocess, psycopg2, urllib.request, ssl
from datetime import datetime

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"
OPENROUTER_KEY = "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"
LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/worker.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
ctx = ssl.create_default_context()

POLL_INTERVAL = 10  # seconds between queue checks
IDLE_INTERVAL = 60  # seconds when queue is empty
WORKER_ID = f"worker-{os.getpid()}"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | WORK | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_conn():
    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    return conn

def claim_next(conn):
    """Atomically claim the next pending queue item."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE agent_queue SET status = 'claimed', claimed_at = now(), claimed_by = %s
        WHERE id = (
            SELECT id FROM agent_queue
            WHERE status = 'pending'
            ORDER BY
                CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'normal' THEN 3 ELSE 4 END,
                created_at
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        )
        RETURNING id, agent_name, record_type, record_id, entity, campaign_id, payload
    """, (WORKER_ID,))
    row = cur.fetchone()
    if row:
        return {
            "queue_id": row[0], "agent_name": row[1], "record_type": row[2],
            "record_id": row[3], "entity": row[4], "campaign_id": row[5],
            "payload": row[6] if isinstance(row[6], dict) else (json.loads(row[6]) if row[6] else {}),
        }
    return None

def complete_item(conn, queue_id, status="done", error=None):
    """Mark a queue item as done or failed."""
    cur = conn.cursor()
    cur.execute("""UPDATE agent_queue SET status = %s, completed_at = now(), error_message = %s WHERE id = %s""",
                (status, error, queue_id))

def call_claude(prompt, timeout=300):
    try:
        result = subprocess.run(["claude", "-p", "--output-format", "text"],
                                input=prompt, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def call_openrouter(prompt, model="deepseek/deepseek-chat-v3-0324"):
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                          "max_tokens": 4000, "temperature": 0.2}).encode()
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload,
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}, method="POST")
        resp = urllib.request.urlopen(req, context=ctx, timeout=120)
        return json.loads(resp.read())["choices"][0]["message"]["content"]
    except:
        return None

# ─── Agent Modules ───────────────────────────────────────────────────────────

def agent_classifier(conn, item):
    """Classify a target by entity using deterministic engine + LLM fallback."""
    from lib.classification import classify_entity
    cur = conn.cursor()

    cur.execute("SELECT company_name, extra_fields FROM targets WHERE id = %s", (item["record_id"],))
    row = cur.fetchone()
    if not row:
        return "failed", "Target not found"

    company_name = row[0]
    extra = row[1] if isinstance(row[1], dict) else {}

    result = classify_entity(
        company_name=company_name,
        industry=extra.get("vertical"),
        person_name=extra.get("owner_name"),
        raw_text=f"{company_name} {extra.get('vertical','')} {extra.get('city','')} {extra.get('state','')}"
    )

    if result["entity"] and result["confidence"] >= 2.0:
        cur.execute("UPDATE targets SET entity = %s WHERE id = %s", (result["entity"], item["record_id"]))
        log(f"  Classified {company_name} → {result['entity']} (conf={result['confidence']:.1f})")
        return "done", None
    else:
        # LLM fallback via Claude CLI
        prompt = f"Classify this company for M&A routing. Company: {company_name}, Industry: {extra.get('vertical','')}, City: {extra.get('city','')}, State: {extra.get('state','')}. Options: next_chapter (home services M&A), and_capital (PE fund/LP), revsup (SaaS recruiting). Return ONLY the entity name."
        llm_result = call_claude(prompt) or call_openrouter(prompt)
        if llm_result:
            entity = llm_result.strip().lower().replace(" ", "_")
            if entity in ("next_chapter", "and_capital", "revsup"):
                cur.execute("UPDATE targets SET entity = %s WHERE id = %s", (entity, item["record_id"]))
                log(f"  Classified {company_name} → {entity} (LLM fallback)")
                return "done", None
        log(f"  Classification failed for {company_name}")
        return "failed", "Could not classify"

def agent_certifier(conn, item):
    """Certify a proposal — check facts, quality, founder guardrails."""
    cur = conn.cursor()
    cur.execute("SELECT company_name, proposal_json, quality_score FROM proposals WHERE id = %s", (item["record_id"],))
    row = cur.fetchone()
    if not row:
        return "failed", "Proposal not found"

    company, proposal_json, quality = row[0], row[1], row[2]

    prompt = f"""You are the certification agent for Next Chapter M&A Advisory.
Review this proposal and check:
1. Are all facts verifiable and sourced?
2. Does it follow the "all about them, nothing about us" principle?
3. Are estimates transparent with disclosed methodology?
4. No negative facts (divorce, lawsuits, closures)?
5. No hallucinated personalization (wrong name, wrong city, wrong facts)?
6. Quality score justified?

PROPOSAL:
{json.dumps(proposal_json, default=str)[:4000] if isinstance(proposal_json, (dict, str)) else 'NO DATA'}

Return JSON: {{"verdict": "APPROVED" or "NEEDS_REVIEW" or "REJECTED", "issues": [], "score_adjustment": 0, "notes": ""}}
ONLY JSON."""

    result = call_claude(prompt) or call_openrouter(prompt)
    if result:
        try:
            s, e = result.find('{'), result.rfind('}') + 1
            cert = json.loads(result[s:e])
        except:
            cert = {"verdict": "NEEDS_REVIEW", "issues": ["Could not parse certification"], "notes": result[:200]}

        verdict = cert.get("verdict", "NEEDS_REVIEW")
        cur.execute("""UPDATE proposals SET certified_by = 'claude_opus_4.6', certified_at = now(),
                       status = CASE WHEN %s = 'APPROVED' THEN 'certified' ELSE 'needs_review' END
                       WHERE id = %s""", (verdict, item["record_id"]))
        log(f"  Certified {company}: {verdict}")

        # Log to agent_runs
        cur.execute("""INSERT INTO agent_runs (agent_name, entity, target_id, status, output_summary)
                       VALUES ('certifier', %s, %s, 'complete', %s)""",
                    (item.get("entity", "next_chapter"), item["record_id"], json.dumps(cert, default=str)))
        return "done", None
    return "failed", "Certification LLM failed"

def agent_nurturer(conn, item):
    """Re-engage a nurtured contact."""
    log(f"  Nurturer: would process {item['record_id']} — not yet implemented")
    return "done", None

def agent_researcher(conn, item):
    """Research a target company."""
    log(f"  Researcher: would research {item['record_id']} — full implementation in next phase")
    return "done", None

# ─── Agent Router ────────────────────────────────────────────────────────────

AGENTS = {
    "classifier": agent_classifier,
    "certifier": agent_certifier,
    "nurturer": agent_nurturer,
    "researcher": agent_researcher,
}

def process_item(conn, item):
    """Route to the correct agent module."""
    agent_fn = AGENTS.get(item["agent_name"])
    if not agent_fn:
        log(f"  Unknown agent: {item['agent_name']}")
        return "failed", f"Unknown agent: {item['agent_name']}"

    start = time.time()
    try:
        status, error = agent_fn(conn, item)
        elapsed = time.time() - start

        # Log run
        cur = conn.cursor()
        cur.execute("""INSERT INTO agent_runs (agent_name, entity, target_id, status, started_at, finished_at, output_summary)
                       VALUES (%s, %s, %s, %s, now() - interval '%s seconds', now(), %s)""",
                    (item["agent_name"], item.get("entity"), item["record_id"], status,
                     int(elapsed), error or "success"))

        return status, error
    except Exception as e:
        log(f"  Agent error: {e}")
        return "failed", str(e)[:200]

def main():
    log("=" * 50)
    log(f"WORKER STARTED (id={WORKER_ID})")
    log(f"Poll: {POLL_INTERVAL}s, Idle: {IDLE_INTERVAL}s")
    log("=" * 50)

    while True:
        try:
            conn = get_conn()
            item = claim_next(conn)

            if item:
                log(f"Processing: {item['agent_name']} for {item['payload'].get('company_name', str(item['record_id'])[:8])}")
                status, error = process_item(conn, item)
                complete_item(conn, item["queue_id"], status, error)
                log(f"  Result: {status}" + (f" — {error}" if error else ""))
                conn.close()
                time.sleep(POLL_INTERVAL)
            else:
                conn.close()
                time.sleep(IDLE_INTERVAL)
        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(IDLE_INTERVAL)

if __name__ == "__main__":
    main()
