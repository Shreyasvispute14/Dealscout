# Smart Shopper living spec

## Purpose
Smart Shopper is an SPPU TYBSc Computer Science project that lets a student search for a product, compare normalized offers from multiple sellers, and see the lowest listed price as the best deal.

## Key flows
- Visitor opens Compare, searches a mobile, laptop, or general product, and sees seller, price, rating, delivery, discount, and source.
- Demo catalog mode uses the local project dataset.
- Live mode uses an optional SerpApi shopping adapter; without a provider key it clearly shows a **MOCKED LIVE PREVIEW** instead of claiming live data.
- Login opens the collected-data panel, which shows saved search logs, top query, result counts, and source frequency.
- Academic docs page contains project index, requirements, certificate/declaration templates, and report structure placeholders for college guidelines.

## Data model
- `ProductOffer`: normalized seller offer with product name, category, source, seller, price, original price, rating, delivery, discount, mode, live/mock flags, and retrieved time.
- `SearchLog`: query, category, mode, result count, best price, sources, and server timestamp.
- `User`: demo student identity used by the login page.

## Auth
Demo-only httpOnly cookie session. Login is not intended as production identity management. Working credentials are recorded in `memory/test_credentials.md`.

## Routes
- `GET /api/products/search?q=&category=&mode=`
- `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`
- `GET /api/analytics` (requires demo login)
- `GET /api/`