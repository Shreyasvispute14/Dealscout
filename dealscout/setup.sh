#!/usr/bin/env sh
# DealScout quick setup for macOS / Linux:  chmod +x setup.sh && ./setup.sh
set -eu
cd "$(dirname "$0")"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js was not found. Install the LTS version from https://nodejs.org/ and run this script again."
  exit 1
fi

echo "Node.js $(node --version) found."
echo "Starting DealScout at http://localhost:${PORT:-3000} ..."

# Open the browser automatically when a desktop opener is available.
if command -v xdg-open >/dev/null 2>&1; then (sleep 1; xdg-open "http://localhost:${PORT:-3000}") >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then (sleep 1; open "http://localhost:${PORT:-3000}") >/dev/null 2>&1 &
fi

exec node server.js
