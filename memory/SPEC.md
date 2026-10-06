# DealScout living spec

## Purpose
DealScout is a product-comparison web app: a shopper searches a product, compares normalized offers from multiple sellers, and sees the lowest listed price as the best deal. It is a T.Y.B.Sc. (CS) Sem V project (SPPU NEP 2020, CS-331-FP) and is built **only** with Sem V syllabus technologies (CS-303-MJ-T Web Technology-I): HTML, CSS, JavaScript ES6+, Node.js core modules, and JSON file handling. No frameworks, no database server, no npm dependencies.

## Where the code lives
- **`/app/dealscout/`** — the actual project. `server.js` (http/fs/path/url), `modules/` (api, products, auth, analytics, filestore), `public/` (HTML/CSS/JS pages + downloads), `data/` (products.json, users.json, searches.json), `setup.bat`/`setup.sh` quick setup, `README.md`.
- `/app/backend/server.py` — pod-only ASGI pass-through that forwards /api on port 8001 to the Node server on 3000 (supervisor config is read-only). Not part of the project.
- `/app/frontend/` — unused Vite skeleton; its `yarn dev` script now runs `node ../dealscout/server.js` on port 3000.
- `/app/tools/generate_documents.py` — builds the 50-page report (.docx + .pdf), viva guide and setup guide into `dealscout/public/downloads/`.

## Key flows
- Visitor opens Compare (`/`), searches a mobile, laptop, or general product, sees seller, price, rating, delivery, discount, source; the lowest price is highlighted as Best.
- Sample prices mode reads `data/products.json`. Live mode calls SerpApi via `https` when `SERPAPI_KEY` is set; otherwise it returns a clearly labelled **MOCKED LIVE PREVIEW**.
- Every search appends a record to `data/searches.json` (newest first, capped at 500).
- Login (`/login`) with the demo account sets an HttpOnly cookie; Insights (nav tab, or `/#insights`) shows totals, top query, recent comparisons and store frequency. Guests see a sign-in prompt. Sign out button in header.
- Resources (`/resources`, alias `/docs`) offers the 50-page Word report, PDF report, viva guide, setup guide, and quick-setup steps.
- Unknown paths return `public/404.html`.

## Data model (JSON files)
- `User`: id, name, email, password (preview only), role.
- `ProductOffer` (built from products.json rows): id, product_name, category, source, seller, price, original_price, currency, rating, delivery, discount, product_url, mode, is_live, is_mocked, retrieved_at.
- `SearchLog`: id, query, category, mode, result_count, best_price, searched_at, sources[].
- `AnalyticsSummary` (computed): total_searches, unique_queries, average_results, top_query, source_counts[], recent_searches[].

## Auth
Demo-only session: `POST /api/auth/login` validates against users.json, stores a random token in an in-memory Map (8 h expiry), and sets cookie `dealscout_session` (HttpOnly, SameSite=Lax). Credentials are in `memory/test_credentials.md`.

## Routes (all JSON, under /api)
- `GET /api/` → `{message, ok}`
- `GET /api/products/search?q=&category=&mode=` → SearchResponse; 400 when q is <2 or >80 chars or category unknown
- `POST /api/auth/login` (401 on bad credentials), `GET /api/auth/me` (user or null), `POST /api/auth/logout`
- `GET /api/analytics` (401 without session)

## Documentation
Report sequence: Title page → Certificate → Index (2 pages, auto page numbers) → index-wise pages (Declaration, Acknowledgement, Abstract, Ch.1 Preliminary Investigation, Ch.2 Requirement Specification, Ch.3 Database Design, Ch.4 System Design, Ch.5 I/O Screen Layout with real screenshots, Ch.6 Testing/Conclusion/Bibliography/Appendix). Exactly 50 pages, Times New Roman, editable blanks for names, seat numbers, guide, coordinator, principal and examiners.
