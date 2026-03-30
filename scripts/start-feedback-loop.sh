#!/bin/bash
# Start the feedback loop background services
cd /Users/clawdbot/Projects/master-crm

# Kill any existing instances
pkill -f "comment_processor.py" 2>/dev/null
pkill -f "auto_refresh.py --watch" 2>/dev/null

# Ensure log directory exists
mkdir -p data/logs

# Start comment processor (polls every 60 seconds)
nohup python3 lib/comment_processor.py > data/logs/comment_processor.log 2>&1 &
echo "Comment processor started (PID: $!)"

# Start auto-refresh watcher (polls every 5 minutes for stale pages)
nohup python3 -c "
import time, sys
sys.path.insert(0, 'lib')
from auto_refresh import process_corrections
while True:
    try:
        process_corrections()
    except Exception as e:
        print(f'auto_refresh error: {e}')
    time.sleep(300)
" > data/logs/auto_refresh.log 2>&1 &
echo "Auto-refresh watcher started (PID: $!)"

echo "Feedback loop services running."
