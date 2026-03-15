#!/bin/bash
# Serve daily-stack on port 8080
cd "$(dirname "$0")/.." || exit 1
echo "Serving Daily Stack at http://localhost:8080"
echo "Access from iPhone: http://$(ipconfig getifaddr en0 2>/dev/null || echo '<your-ip>'):8080"
python3 -m http.server 8080
