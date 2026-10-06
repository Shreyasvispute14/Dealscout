# DealScout

E-commerce product comparison and best-deal finder.
T.Y.B.Sc. (Computer Science) Semester V project — Savitribai Phule Pune University (NEP 2020 pattern), course **CS-331-FP Project**.

Built **only** with technologies from the Semester V syllabus (CS-303-MJ-T Web Technology-I):

| Syllabus unit | Where it is used |
| --- | --- |
| Frontend Fundamentals (HTML, CSS, core JavaScript) | `public/index.html`, `public/login.html`, `public/resources.html`, `public/css/style.css` |
| Advanced JavaScript (ES6+) | `public/js/app.js`, `public/js/login.js`, `public/js/common.js` — fetch, async/await, template literals, array methods |
| Node.js Fundamentals | `server.js`, `modules/api.js` — `http`, `url`, `path`, `crypto` core modules, npm scripts |
| File Handling with Node.js | `modules/filestore.js` + `data/*.json` (catalog, users, search log) |

No frameworks, no database server, no third-party npm packages.

## Quick setup

1. Install Node.js (LTS) from <https://nodejs.org/>.
2. Open this folder.
3. **Windows:** double-click `setup.bat` · **macOS / Linux:** `chmod +x setup.sh && ./setup.sh`
4. The browser opens <http://localhost:3000>.

Manual start: `node server.js` (or `npm start`). Change the port with `PORT=4000 node server.js`.

## Login (preview account)

- Email: `preview@dealscout.local`
- Password: `dealscout123`

Accounts live in `data/users.json`.

## Folder layout

```
dealscout/
├── server.js            HTTP server: static files + /api routes
├── modules/
│   ├── api.js           REST router (switch on "METHOD /path")
│   ├── products.js      catalog search, normalization, best-deal selection
│   ├── auth.js          demo login with HttpOnly cookie sessions
│   ├── analytics.js     insights computed from the search log
│   └── filestore.js     JSON read / write helpers (fs.promises)
├── data/
│   ├── products.json    sample catalog
│   ├── users.json       login accounts
│   └── searches.json    search history (written by the server)
├── public/
│   ├── index.html, login.html, resources.html, 404.html
│   ├── css/style.css
│   ├── js/common.js, app.js, login.js
│   └── downloads/       report (.docx/.pdf), viva guide, setup guide, figures
├── setup.bat / setup.sh quick setup scripts
└── package.json         npm start → node server.js
```

## API

| Method & path | Purpose |
| --- | --- |
| `GET /api/` | health check |
| `GET /api/products/search?q=&category=&mode=` | compare offers; `mode` = `demo` or `live`; 400 if `q` < 2 chars |
| `POST /api/auth/login` | `{ email, password }` → session cookie; 401 on failure |
| `GET /api/auth/me` | current user or `null` |
| `POST /api/auth/logout` | end session |
| `GET /api/analytics` | search insights (401 without login) |

## Optional live prices

Sample prices work offline. For live results set a SerpApi key before starting:

- Windows: `set SERPAPI_KEY=your_key` then `node server.js`
- macOS / Linux: `SERPAPI_KEY=your_key node server.js`

Without a key, Live search shows clearly labelled **preview** data.

## Documentation

Regenerate the 50-page report, viva guide and setup guide (build tool, not part of the submitted app):

```
python ../tools/generate_documents.py
```

Outputs go to `public/downloads/` and are available from the Resources page.
