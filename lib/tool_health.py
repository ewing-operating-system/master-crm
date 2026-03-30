#!/usr/bin/env python3
"""
Tool Health Monitor — reports success/failure for every external tool call.
Alerts via iMessage when critical tools go down.
Provides self-diagnosis and auto-fix capabilities.
"""

import json, os, subprocess, time, psycopg2, urllib.request, ssl

DB_CONN = "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"
ctx = ssl.create_default_context()

def get_conn():
    return psycopg2.connect(DB_CONN)

def report_success(tool_name):
    """Call after any successful API call."""
    try:
        conn = get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT report_tool_success(%s)", (tool_name,))
        conn.close()
    except:
        pass  # Don't let health reporting break the main flow

def report_failure(tool_name, error_code, error_message, context=None, affected=0):
    """Call after any failed API call. Returns incident_id."""
    try:
        conn = get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT report_tool_failure(%s, %s, %s, %s, %s)",
                    (tool_name, str(error_code), str(error_message)[:500], context, affected))
        incident_id = cur.fetchone()[0]

        # Check if we need to alert
        cur.execute("SELECT consecutive_failures, is_critical, alert_sent_at FROM tool_health WHERE tool_name = %s", (tool_name,))
        row = cur.fetchone()
        if row:
            failures, critical, last_alert = row
            # Alert on 3+ consecutive failures for critical tools, if not alerted in last hour
            if failures >= 3 and critical:
                should_alert = True
                if last_alert:
                    # Don't alert more than once per hour
                    cur.execute("SELECT %s < now() - interval '1 hour'", (last_alert,))
                    should_alert = cur.fetchone()[0]

                if should_alert:
                    send_alert(tool_name, error_message, failures, affected)
                    cur.execute("UPDATE tool_health SET alert_sent_at = now() WHERE tool_name = %s", (tool_name,))

        conn.close()
        return str(incident_id)
    except:
        return None

def send_alert(tool_name, error, failures, affected):
    """Send iMessage alert for critical tool failure."""
    msg = f"[Argus] CRITICAL: {tool_name} is DOWN ({failures} consecutive failures). Error: {error[:100]}. {affected} records affected. Check immediately."
    try:
        bridge = os.path.expanduser("~/.imessage-bridge/imessage-bridge.sh")
        if os.path.exists(bridge):
            subprocess.run([bridge, msg], capture_output=True, timeout=30)
    except:
        pass  # Alert is best-effort, don't crash the system

def check_all_tools():
    """Run health checks on all tools. Returns dict of status."""
    results = {}

    # Exa
    try:
        payload = json.dumps({"query": "test", "num_results": 1, "type": "auto"}).encode()
        req = urllib.request.Request("https://api.exa.ai/search", data=payload,
            headers={"x-api-key": get_exa_key(), "Content-Type": "application/json"}, method="POST")
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        report_success("exa")
        results["exa"] = "healthy"
    except Exception as e:
        report_failure("exa", getattr(e, 'code', 'unknown'), str(e), "health_check")
        results["exa"] = f"down: {e}"

    # Claude CLI
    try:
        result = subprocess.run(["claude", "-p", "--output-format", "text"],
                                input="say OK", capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            report_success("claude_cli")
            results["claude_cli"] = "healthy"
        else:
            report_failure("claude_cli", result.returncode, result.stderr[:200], "health_check")
            results["claude_cli"] = f"error: {result.stderr[:50]}"
    except Exception as e:
        report_failure("claude_cli", "timeout", str(e), "health_check")
        results["claude_cli"] = f"down: {e}"

    # OpenRouter
    try:
        payload = json.dumps({"model": "deepseek/deepseek-chat-v3-0324",
                              "messages": [{"role": "user", "content": "say OK"}],
                              "max_tokens": 5}).encode()
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload,
            headers={"Authorization": f"Bearer {get_openrouter_key()}", "Content-Type": "application/json"},
            method="POST")
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        report_success("openrouter")
        results["openrouter"] = "healthy"
    except Exception as e:
        report_failure("openrouter", getattr(e, 'code', 'unknown'), str(e), "health_check")
        results["openrouter"] = f"down: {e}"

    # Supabase
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        report_success("supabase")
        results["supabase"] = "healthy"
    except Exception as e:
        report_failure("supabase", "conn_error", str(e), "health_check")
        results["supabase"] = f"down: {e}"

    return results

def get_exa_key():
    """Get current Exa key from tool_health config."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT config->>'api_key' FROM tool_health WHERE tool_name = 'exa'")
        key = cur.fetchone()[0]
        conn.close()
        return key
    except:
        return "97e41046-ec91-4647-8e80-f6da354e2641"

def get_openrouter_key():
    return "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"

def update_exa_key(new_key):
    """Update Exa API key in tool_health config."""
    conn = get_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""UPDATE tool_health SET
                   config = jsonb_set(config, '{api_key}', %s::jsonb),
                   consecutive_failures = 0, status = 'unknown', updated_at = now()
                   WHERE tool_name = 'exa'""", (json.dumps(new_key),))
    conn.close()
    # Test the new key
    results = check_all_tools()
    return results.get("exa", "unknown")

def get_status_report():
    """Get a formatted status report for all tools."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tool_status_dashboard")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    cur.execute("SELECT count(*) FROM tool_incidents WHERE resolved = false")
    unresolved = cur.fetchone()[0]

    conn.close()
    return {"tools": rows, "unresolved_incidents": unresolved}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        results = check_all_tools()
        for tool, status in results.items():
            print(f"  {tool}: {status}")
    elif len(sys.argv) > 2 and sys.argv[1] == "update-exa-key":
        result = update_exa_key(sys.argv[2])
        print(f"Exa key updated. Status: {result}")
    else:
        report = get_status_report()
        for tool in report["tools"]:
            emoji = "🟢" if tool["status"] == "healthy" else "🔴" if tool["status"] == "down" else "🟡"
            print(f"{emoji} {tool['tool_name']}: {tool['status']} | failures={tool['consecutive_failures']} | success_rate={tool.get('success_rate_24h', 'N/A')}%")
        print(f"\nUnresolved incidents: {report['unresolved_incidents']}")
