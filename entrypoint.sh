#!/bin/sh
set -e

SYNC_INTERVAL="${SYNC_INTERVAL:-300}"

cleanup() {
    echo "Shutting down..."
    kill "$NGINX_PID" 2>/dev/null || true
    exit 0
}
trap cleanup TERM INT

echo "[$(date -Iseconds)] Initial sync..."
/sync.sh

nginx -g "daemon off;" &
NGINX_PID=$!
echo "[$(date -Iseconds)] nginx started (PID $NGINX_PID), sync interval: ${SYNC_INTERVAL}s"

while kill -0 "$NGINX_PID" 2>/dev/null; do
    sleep "$SYNC_INTERVAL"
    echo "[$(date -Iseconds)] Periodic sync..."
    /sync.sh || echo "[$(date -Iseconds)] Sync failed, will retry next interval."
done
