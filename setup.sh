#!/usr/bin/env sh
set -eu

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker Desktop is required. Install it from https://www.docker.com/products/docker-desktop/"
  exit 1
fi

docker compose up --build -d
echo "DealScout is starting at http://localhost:3000"
echo "Run 'docker compose logs -f' to view startup progress."