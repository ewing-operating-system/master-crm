#!/usr/bin/env python3
"""
Watchdog — monitors orchestrator and worker health.
Run via cron every 15 minutes.
"""

import subprocess, os, time, sys
from datetime import datetime

LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/watchdog.log")
ORCH_SCRIPT = os.path.expanduser("~/Projects/master-crm/orchestrator.py")
WORKER_SCRIPT = os.path.expanduser("~/Projects/master-crm/worker.py")
PID_DIR = os.path.expanduser("~/Projects/master-crm/data/pids")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(PID_DIR, exist_ok=True)

def log(msg):
    line = f"{datetime.utcnow().isoformat()} | WATCH | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def is_running(name):
    """Check if a process with this script name is running."""
    result = subprocess.run(["pgrep", "-f", name], capture_output=True, text=True)
    pids = result.stdout.strip().split('\n')
    pids = [p for p in pids if p and p != str(os.getpid())]
    return len(pids) > 0, pids

def start_process(script, name):
    """Start a process in the background."""
    pid_file = os.path.join(PID_DIR, f"{name}.pid")
    log_path = os.path.expanduser(f"~/Projects/master-crm/data/logs/{name}.log")

    cmd = f"nohup python3 {script} >> {log_path} 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    running, pids = is_running(os.path.basename(script))
    if running:
        with open(pid_file, 'w') as f:
            f.write(pids[0])
        log(f"Started {name} (PID: {pids[0]})")
        return True
    else:
        log(f"FAILED to start {name}")
        return False

def main():
    log("Watchdog check")

    # Check orchestrator
    orch_running, orch_pids = is_running("orchestrator.py")
    if orch_running:
        log(f"Orchestrator: ALIVE (PIDs: {orch_pids})")
    else:
        log("Orchestrator: DEAD — restarting")
        start_process(ORCH_SCRIPT, "orchestrator")

    # Check worker
    worker_running, worker_pids = is_running("worker.py")
    if worker_running:
        log(f"Worker: ALIVE (PIDs: {worker_pids})")
    else:
        log("Worker: DEAD — restarting")
        start_process(WORKER_SCRIPT, "worker")

    log("Watchdog check complete")

if __name__ == "__main__":
    main()
