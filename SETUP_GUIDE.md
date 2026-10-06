# DealScout quick setup

The project is the **`dealscout/`** folder (HTML, CSS, JavaScript, Node.js — SPPU T.Y.B.Sc. CS Sem V syllabus only).

## Requirements

Install **Node.js (LTS)** from https://nodejs.org/. Nothing else is needed — no database, no npm packages.

## Windows

1. Open the `dealscout` folder.
2. Double-click `setup.bat`.
3. The browser opens `http://localhost:3000`.

## macOS / Linux

1. Open Terminal in the `dealscout` folder.
2. Run `chmod +x setup.sh && ./setup.sh`.
3. Open `http://localhost:3000`.

## Manual

```
cd dealscout
node server.js
```

## Login

- Email: `preview@dealscout.local`
- Password: `dealscout123`

## Optional live shopping results

Set `SERPAPI_KEY=your_key` in the environment before starting. Without it, Live search shows labelled preview data and Sample prices remain fully usable.

## About the other folders

`backend/` and `frontend/` only exist so the Emergent preview pod can host the Node.js app on its fixed ports (a tiny pass-through shim). They are **not** part of the submitted project. `tools/generate_documents.py` rebuilds the report PDFs/Word file.
