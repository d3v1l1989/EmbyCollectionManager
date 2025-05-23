#!/bin/sh
set -e

CMD="python main.py"

# If using legacy SYNC_EMBY var, handle it for backward compatibility
if [ "$SYNC_EMBY" = "1" ]; then
    CMD="$CMD --sync_emby"
else
    # New approach: use SYNC_TARGET if set, otherwise use 'auto' detection
    if [ -n "$SYNC_TARGET" ]; then
        CMD="$CMD --targets $SYNC_TARGET"
    fi
fi

# Execute the command with any additional arguments
exec $CMD "$@"
