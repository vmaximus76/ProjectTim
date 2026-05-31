#!/bin/sh
# Starts Governor, Draftsman, and nginx (public port 8080).

PORT=8081 python -m governor.app &
GOV_PID=$!

PORT=8082 python -m draftsman.app &
DRFT_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

wait -n
EXIT_CODE=$?
kill $GOV_PID $DRFT_PID $NGINX_PID 2>/dev/null || true
exit $EXIT_CODE
