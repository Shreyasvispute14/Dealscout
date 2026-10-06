@echo off
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop is required. Install it from https://www.docker.com/products/docker-desktop/
  pause
  exit /b 1
)
docker compose up --build -d
echo DealScout is starting at http://localhost:3000
start http://localhost:3000
pause