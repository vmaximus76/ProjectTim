#!/bin/sh
# Simple launcher that starts both Governor and Draftsman services.
# The services listen on 8080 (Governor) and 8081 (Draftsman).

# Start Governor in background
python -m governor.app &
GOV_PID=$!

# Start Draftsman in background
python -m draftsman.app &
DRFT_PID=$!

# Wait for both processes – if either exits, propagate exit code.
wait -n
EXIT_CODE=$?
# Kill the other process if still running
kill $GOV_PID $DRFT_PID 2>/dev/null || true
exit $EXIT_CODE