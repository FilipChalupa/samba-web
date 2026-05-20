#!/bin/sh
set -e

HOST="${SMB_HOST:?SMB_HOST is required}"
SHARE="${SMB_SHARE:?SMB_SHARE is required}"
USER="${SMB_USER:-guest}"
PASS="${SMB_PASSWORD:-}"
DOMAIN="${SMB_DOMAIN:-WORKGROUP}"
REMOTE_PATH="${SMB_PATH:-/}"
DEST="/data"
TMP="${DEST}.tmp"

if [ "$USER" = "guest" ] && [ -z "$PASS" ]; then
    SMBAUTH="-N"
else
    SMBAUTH="-U ${DOMAIN}/${USER}%${PASS}"
fi

if [ -n "$REMOTE_PATH" ] && [ "$REMOTE_PATH" != "/" ] && [ "$REMOTE_PATH" != "." ]; then
    CD_CMD="cd \"${REMOTE_PATH}\";"
else
    CD_CMD=""
fi

rm -rf "$TMP"
mkdir -p "$TMP"

echo "[$(date -Iseconds)] Syncing //${HOST}/${SHARE}${REMOTE_PATH} -> ${DEST}"

# shellcheck disable=SC2086
smbclient "//${HOST}/${SHARE}" $SMBAUTH \
    -c "recurse; prompt off; ${CD_CMD} lcd \"${TMP}\"; mget *"

# Atomic swap so nginx always serves a complete snapshot
rm -rf "${DEST}.old"
[ -d "$DEST" ] && mv "$DEST" "${DEST}.old"
mv "$TMP" "$DEST"
rm -rf "${DEST}.old"

echo "[$(date -Iseconds)] Sync done."
