"""Pod hosting shim — NOT part of the DealScout project.

The Emergent preview pod runs supervisor programs on fixed ports (8001 for /api,
3000 for the site). The actual project is the pure Node.js application in
/app/dealscout (HTML, CSS, JavaScript, Node.js — SPPU T.Y.B.Sc. CS Sem V syllabus).
This tiny ASGI passthrough forwards every /api request arriving on 8001 to the
Node.js server so the preview URL works without changing the read-only supervisor
configuration. Run `node server.js` inside /app/dealscout for the real thing.
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

NODE_APP_URL = os.environ.get("NODE_APP_URL", "http://127.0.0.1:3000")
HOP_BY_HOP = {"content-encoding", "transfer-encoding", "content-length", "connection"}


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    if scope["type"] != "http":
        return

    body = b""
    while True:
        message = await receive()
        body += message.get("body", b"")
        if not message.get("more_body"):
            break

    headers = [(k.decode(), v.decode()) for k, v in scope["headers"] if k.lower() not in {b"host", b"content-length"}]
    url = scope["path"] + (f"?{scope['query_string'].decode()}" if scope["query_string"] else "")
    try:
        # A fresh client per request: no shared cookie jar, so one user's session
        # cookie is never replayed on another visitor's request.
        async with httpx.AsyncClient(base_url=NODE_APP_URL, timeout=30) as client:
            upstream = await client.request(scope["method"], url, headers=headers, content=body)
        status, payload = upstream.status_code, upstream.content
        response_headers = [(k.encode(), v.encode()) for k, v in upstream.headers.multi_items() if k.lower() not in HOP_BY_HOP]
    except httpx.HTTPError:
        status, payload = 502, b'{"detail":"DealScout Node.js server is not running"}'
        response_headers = [(b"content-type", b"application/json")]
    response_headers.append((b"content-length", str(len(payload)).encode()))
    await send({"type": "http.response.start", "status": status, "headers": response_headers})
    await send({"type": "http.response.body", "body": payload})
