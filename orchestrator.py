#!/usr/bin/env python3
"""
Orchestrator — master scheduler and event router.
Runs continuously on Mac mini. Scans for work, dispatches to agent_queue.
"""

import json, os, time, sys, psycopg2
from datetime import datetime, timedelta

DB_CONN = os.environ.get("DATABASE_URL", "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres")
LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/orchestrator.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

POLL_INTERVAL = 300  # 5 minutes
STUCK_THRESHOLD_MIN = 30

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | ORCH | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_conn():
    return psycopg2.connect(DB_CONN)

def reset_stuck_items(conn):
    """Reset queue items claimed > 30 min ago with no completion."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE agent_queue SET status = 'pending', claimed_at = NULL, claimed_by = NULL,
               retry_count = retry_count + 1
        WHERE status = 'claimed' AND claimed_at < now() - interval '%s minutes'
        RETURNING id, agent_name, record_id
    """, (STUCK_THRESHOLD_MIN,))
    stuck = cur.fetchall()
    conn.commit()
    if stuck:
        log(f"Reset {len(stuck)} stuck items: {[(s[1], str(s[2])[:8]) for s in stuck]}")
    return len(stuck)

def check_budgets(conn):
    """Check if any entity is over daily budget. Returns set of paused entities."""
    cur = conn.cursor()
    cur.execute("SELECT entity, budget_usd, spent_usd FROM cost_budget WHERE period = 'daily'")
    paused = set()
    for entity, budget, spent in cur.fetchall():
        pct = (spent / budget * 100) if budget > 0 else 0
        if pct >= 100:
            paused.add(entity)
            log(f"BUDGET PAUSE: {entity} at {pct:.0f}% (${spent:.2f}/${budget:.2f})")
        elif pct >= 80:
            log(f"BUDGET WARN: {entity} at {pct:.0f}% (${spent:.2f}/${budget:.2f})")
    return paused

def scan_targets_needing_work(conn, paused_entities):
    """Find targets that need pipeline steps and create queue items."""
    cur = conn.cursor()
    queued = 0

    # Targets with no entity tag → need classification
    cur.execute("""
        SELECT t.id, t.company_name FROM targets t
        WHERE (t.entity IS NULL OR t.entity::text = 'unknown')
        AND NOT EXISTS (SELECT 1 FROM agent_queue aq WHERE aq.record_id = t.id AND aq.agent_name = 'classifier' AND aq.status IN ('pending', 'claimed'))
        LIMIT 50
    """)
    for tid, name in cur.fetchall():
        cur.execute("""INSERT INTO agent_queue (agent_name, record_type, record_id, priority, payload)
                       VALUES ('classifier', 'target', %s, 'normal', %s)""",
                    (tid, json.dumps({"company_name": name})))
        queued += 1

    # Targets classified but not researched → need research
    cur.execute("""
        SELECT t.id, t.company_name, t.entity::text FROM targets t
        WHERE t.entity IS NOT NULL AND t.entity::text != 'unknown'
        AND t.research_completed_at IS NULL
        AND NOT EXISTS (SELECT 1 FROM agent_queue aq WHERE aq.record_id = t.id AND aq.agent_name = 'researcher' AND aq.status IN ('pending', 'claimed'))
        AND t.entity::text NOT IN %s
        LIMIT 20
    """, (tuple(paused_entities) if paused_entities else ('__none__',),))
    for tid, name, entity in cur.fetchall():
        cur.execute("""INSERT INTO agent_queue (agent_name, record_type, record_id, entity, priority, payload)
                       VALUES ('researcher', 'target', %s, %s, 'normal', %s)""",
                    (tid, entity, json.dumps({"company_name": name})))
        queued += 1

    # Proposals in draft that need certification
    cur.execute("""
        SELECT p.id, p.company_name FROM proposals p
        WHERE p.status = 'draft' AND p.certified_at IS NULL
        AND NOT EXISTS (SELECT 1 FROM agent_queue aq WHERE aq.record_id = p.id AND aq.agent_name = 'certifier' AND aq.status IN ('pending', 'claimed'))
        LIMIT 10
    """)
    for pid, name in cur.fetchall():
        cur.execute("""INSERT INTO agent_queue (agent_name, record_type, record_id, entity, priority, payload)
                       VALUES ('certifier', 'proposal', %s, 'next_chapter', 'normal', %s)""",
                    (pid, json.dumps({"company_name": name})))
        queued += 1

    # Nurture schedule — items due today
    cur.execute("""
        SELECT ns.id, ns.target_id, ns.play_code FROM nurture_schedule ns
        WHERE ns.next_touch_date <= CURRENT_DATE AND ns.status = 'scheduled'
        AND NOT EXISTS (SELECT 1 FROM agent_queue aq WHERE aq.record_id = ns.target_id AND aq.agent_name = 'nurturer' AND aq.status IN ('pending', 'claimed'))
        LIMIT 10
    """)
    for nsid, tid, play in cur.fetchall():
        cur.execute("""INSERT INTO agent_queue (agent_name, record_type, record_id, priority, payload)
                       VALUES ('nurturer', 'target', %s, 'normal', %s)""",
                    (tid, json.dumps({"nurture_id": str(nsid), "play_code": play})))
        queued += 1

    conn.commit()
    if queued > 0:
        log(f"Dispatched {queued} new queue items")
    return queued

def get_queue_stats(conn):
    """Get current queue depth."""
    cur = conn.cursor()
    cur.execute("""
        SELECT agent_name, status, count(*)
        FROM agent_queue
        GROUP BY agent_name, status
        ORDER BY agent_name, status
    """)
    stats = {}
    for agent, status, count in cur.fetchall():
        stats.setdefault(agent, {})[status] = count
    return stats

def run_cycle(conn):
    """One orchestrator cycle."""
    reset_stuck_items(conn)
    paused = check_budgets(conn)
    queued = scan_targets_needing_work(conn, paused)
    stats = get_queue_stats(conn)

    if stats:
        pending = sum(s.get('pending', 0) for s in stats.values())
        claimed = sum(s.get('claimed', 0) for s in stats.values())
        done = sum(s.get('done', 0) for s in stats.values())
        failed = sum(s.get('failed', 0) for s in stats.values())
        log(f"Queue: pending={pending} claimed={claimed} done={done} failed={failed}")

def main():
    log("=" * 50)
    log("ORCHESTRATOR STARTED")
    log(f"Poll interval: {POLL_INTERVAL}s")
    log("=" * 50)

    while True:
        try:
            conn = get_conn()
            conn.autocommit = True
            run_cycle(conn)
            conn.close()
        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
