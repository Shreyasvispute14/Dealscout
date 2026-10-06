@echo off
REM DealScout quick setup for Windows — double-click this file.
title DealScout quick setup
cd /d "%~dp0"

where node >nul 2>nul
if %errorlevel% neq 0 (
  echo Node.js was not found. Please install it from https://nodejs.org/ ^(LTS version^) and run this file again.
  pause
  exit /b 1
)

for /f "tokens=*" %%v in ('node --version') do set NODE_VERSION=%%v
echo Node.js %NODE_VERSION% found.
echo Starting DealScout at http://localhost:3000 ...
start "" http://localhost:3000
node server.js
pause
