#!/bin/sh
set -e

CMD="python -m src.app_logic"

# If using legacy SYNC_EMBY/SYNC_JELLYFIN vars, handle them for backward compatibility
if [ "$SYNC_EMBY" = "1" ] || [ "$SYNC_JELLYFIN" = "1" ]; then
    [ "$SYNC_EMBY" = "1" ] && CMD="$CMD --sync_emby"
    [ "$SYNC_JELLYFIN" = "1" ] && CMD="$CMD --sync_jellyfin"
else
    # New approach: use SYNC_TARGET if set, otherwise use 'auto' detection
    if [ -n "$SYNC_TARGET" ]; then
        CMD="$CMD --targets $SYNC_TARGET"
    fi
fi

# Execute the command with any additional arguments
exec $CMD "$@"
