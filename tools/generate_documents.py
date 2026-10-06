"""Builds the DealScout submission documents (Word + PDF report, viva guide, setup guide).

This is a documentation build tool only; the submitted project is the Node.js app in /app/dealscout.
Sequence enforced by the college: Title Page -> Certificate -> Index -> Index-wise pages.
Exactly 50 pages in both the .docx and the .pdf.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dealscout" / "public" / "downloads"
ASSETS = OUTPUT / "report-assets"
OUTPUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

NAVY = "#0B172A"
GREEN = "#10B981"
LIGHT = "#F1F5F9"
GREY = "#64748B"
TOTAL_PAGES = 50
YEAR = "2026–27"


def font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_diagram(filename: str, title: str, boxes: list[tuple[str, int, int]], arrows: list[tuple[int, int]]) -> str:
    width, height = 1400, 700
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, width - 20, height - 20), radius=24, fill="#F8FAFC", outline="#CBD5E1", width=3)
    draw.text((55, 45), title, fill=NAVY, font=font(34, True))
    positions: list[tuple[int, int, int, int]] = []
    for label, x, y in boxes:
        box = (x, y, x + 270, y + 115)
        positions.append(box)
        draw.rounded_rectangle(box, radius=18, fill="white", outline=GREEN, width=4)
        for line_no, line in enumerate(textwrap.wrap(label, width=21)):
            draw.text((x + 24, y + 24 + line_no * 27), line, fill=NAVY, font=font(22, line_no == 0))
    for start, end in arrows:
        a, b = positions[start], positions[end]
        x1, y1 = (a[2], (a[1] + a[3]) // 2)
        x2, y2 = (b[0], (b[1] + b[3]) // 2)
        if x2 < x1:
            x1, y1 = ((a[0] + a[2]) // 2, a[3])
            x2, y2 = ((b[0] + b[2]) // 2, b[1])
        draw.line((x1, y1, x2, y2), fill="#475569", width=5)
        draw.polygon([(x2, y2), (x2 - 17, y2 - 10), (x2 - 17, y2 + 10)], fill="#475569")
    path = ASSETS / filename
    image.save(path, quality=95)
    return str(path)


DIAGRAMS = {
    "er": make_diagram("er-diagram.png", "Entity Relationship Diagram", [("User (users.json)", 70, 190), ("Search Log (searches.json)", 560, 190), ("Product Offer (products.json)", 1050, 190), ("Store Source", 560, 450)], [(0, 1), (1, 2), (1, 3)]),
    "class": make_diagram("class-diagram.png", "Class Diagram", [("User id, name, email, role", 70, 190), ("ProductService search(), normalize()", 560, 190), ("ProductOffer price, rating, seller", 1050, 190), ("AnalyticsService summarize()", 560, 450)], [(0, 1), (1, 2), (1, 3)]),
    "object": make_diagram("object-diagram.png", "Object Diagram", [("previewUser : User", 70, 190), ("iphoneSearch : SearchLog", 560, 190), ("flipkartOffer : ProductOffer", 1050, 190), ("amazonOffer : ProductOffer", 560, 450)], [(0, 1), (1, 2), (1, 3)]),
    "component": make_diagram("component-diagram.png", "Component Diagram", [("Browser UI HTML / CSS / JS", 70, 190), ("Node.js HTTP Server server.js", 560, 190), ("JSON Data Files fs module", 1050, 190), ("Shopping Provider (optional)", 560, 450)], [(0, 1), (1, 2), (1, 3)]),
    "deployment": make_diagram("deployment-diagram.png", "Deployment Diagram", [("Web Browser", 70, 190), ("Node.js Runtime port 3000", 560, 190), ("data/ folder JSON files", 1050, 190), ("Internet (live mode only)", 560, 450)], [(0, 1), (1, 2), (1, 3)]),
    "usecase": make_diagram("use-case-diagram.png", "Use Case Diagram", [("Shopper", 70, 190), ("Search Product", 480, 120), ("Compare Offers", 900, 120), ("View Best Price", 900, 420), ("View Insights", 480, 420)], [(0, 1), (1, 2), (2, 3), (0, 4)]),
    "activity": make_diagram("activity-diagram.png", "Activity Diagram", [("Enter Query", 70, 190), ("Validate", 380, 190), ("Filter Catalog", 690, 190), ("Find Minimum", 1000, 190), ("Save Log & Display", 560, 450)], [(0, 1), (1, 2), (2, 3), (3, 4)]),
    "sequence": make_diagram("sequence-diagram.png", "Sequence Diagram", [("Shopper", 70, 190), ("Browser JS fetch()", 390, 190), ("Node.js API", 710, 190), ("JSON Files", 1030, 190), ("Comparison Result", 550, 450)], [(0, 1), (1, 2), (2, 3), (3, 4)]),
}

SCREENS = {name: str(ASSETS / f"real-{name}.png") for name in ["dashboard", "results", "login", "insights", "resources"]}
for screen in SCREENS.values():
    assert Path(screen).exists(), f"Missing screenshot {screen}"


def page(chapter: str, title: str, purpose: str, points: list[str], explanation: str, image: str | None = None, code: list[str] | None = None):
    return {"type": "content", "chapter": chapter, "title": title, "purpose": purpose, "points": points, "explanation": explanation, "image": image, "code": code}


CONTENT = [
    # ---------- Front matter ----------
    page("0", "DECLARATION", "I/We hereby declare that the work presented in this report entitled “DealScout” is an original study completed for T.Y. B.Sc. (Computer Science), Semester V, under the NEP 2020 pattern of Savitribai Phule Pune University.", ["The system is implemented only with technologies taught in the Semester V curriculum: HTML, CSS, JavaScript (ES6+), Node.js and JSON file handling (CS-303-MJ-T Web Technology-I).", "The implementation and documentation are prepared for academic evaluation under CS-331-FP Project.", "All external references are acknowledged in the bibliography.", "Student names and seat numbers are intentionally left editable."], "Placeholders should be completed and signed before final submission. The declaration confirms ownership of the submitted work while recognizing official documentation and software references."),
    page("0", "ACKNOWLEDGEMENT", "The completion of DealScout was made possible through guidance, review, testing, and access to academic resources.", ["Gratitude to the Principal and Department of Computer Science.", "Thanks to the Project Guide and Course Coordinator.", "Acknowledgement of internal and external examiners.", "Appreciation for classmates, family, and the open-source Node.js and MDN communities."], "Replace this text with personal acknowledgements if required by the assigned teacher. Keep the tone formal, concise, and connected to the actual support received."),
    page("0", "ABSTRACT", "DealScout is a web application for comparing offers for the same product across multiple sellers. It combines search, normalization, best-deal recommendation, login, and search-history insights in one responsive interface built with HTML, CSS, JavaScript and Node.js.", ["Accepts product names and category filters from a browser form.", "Normalizes price, seller, rating, discount, and delivery fields into one JavaScript object structure.", "Highlights the lowest listed price as the best deal.", "Stores every search in a JSON file using the Node.js fs module.", "Supports a sample catalog and an optional live shopping provider."], "The solution reduces repeated manual searching. Its design separates the browser interface (HTML/CSS/JS), the Node.js HTTP server, and JSON data files so that each part can be explained and maintained independently."),

    # ---------- Chapter 1 ----------
    page("1", "1.1 PROBLEM IDENTIFICATION", "E-commerce platforms present similar products with different prices, discounts, ratings, seller names, and delivery estimates. Users must inspect each source separately.", ["Manual comparison consumes time.", "Different field formats create confusion.", "A low visible price may exclude context such as seller or delivery.", "Search history is normally scattered or unavailable.", "Users need a transparent explanation of the recommended deal."], "DealScout addresses these difficulties by displaying every normalized offer in one table and marking the minimum listed price. It does not claim that a preview price is live when no provider is connected."),
    page("1", "1.2 PROBLEM STATEMENT / DEFINITION", "To design and develop a responsive web system that searches product offers, converts them into a common structure, compares important values, identifies the lowest listed price, and stores search activity — using only HTML, CSS, JavaScript and Node.js.", ["Input: product query, category, and source mode.", "Process: validation, retrieval, normalization, minimum-price selection, and logging.", "Output: best-deal card, comparison table, notices, and insights.", "Constraint: live results require a valid provider key; all other features work offline."], "The problem definition is intentionally precise. It focuses on comparable offer data rather than promising purchase completion, payment handling, or guaranteed final checkout totals."),
    page("1", "1.3 PURPOSE, OBJECTIVES AND GOALS", "The purpose is to help users compare product offers with less effort and more context, while demonstrating the complete Web Technology-I skill set.", ["Provide a clean and accessible search form (HTML5 forms and validation attributes).", "Support mobile, laptop, and general-product categories.", "Display seller, price, rating, delivery, and discount.", "Calculate the lowest price using understandable JavaScript logic.", "Protect insights behind a login session.", "Keep setup trivial: install Node.js and run one command."], "Success is measured by whether a user can move from a query to a readable comparison and understand why one offer is highlighted. The interface must remain usable on desktop and mobile screens."),
    page("1", "1.4 TECHNICAL FEASIBILITY", "Every required technology is part of the Semester V syllabus, is free, and is well documented.", ["HTML5 and CSS3 build the responsive interface (Unit: Frontend Fundamentals).", "JavaScript ES6+ (let/const, arrow functions, template literals, async/await, fetch, array methods) powers the browser logic (Unit: Advanced JavaScript).", "Node.js core modules http, path, url and crypto implement the server (Unit: Node.js Fundamentals).", "The fs module reads and writes JSON data files (Unit: File Handling with Node.js).", "An optional https call supplies live shopping results."], "The sample catalog guarantees that core functionality works without any credentials or external service. No framework, database server, or third-party npm package is needed, making the architecture technically achievable for a student team."),
    page("1", "1.4 ECONOMIC, OPERATIONAL AND SCHEDULE FEASIBILITY", "Development can be completed with open-source tools and standard computer hardware, in achievable stages.", ["Economic: Node.js, browsers, and editors such as VS Code are free; the sample catalog has no API cost.", "Economic: a live provider key is optional and only needed for real-time prices.", "Operational: clear labels, visible loading states, readable errors, and sign-in needed only for private insights.", "Schedule: requirements and data files first; server routes, pages, testing and documentation follow.", "Schedule: teacher feedback is applied before submission."], "The modular sequence reduces project risk. Each stage produces a demonstrable output and supports independent correction without redesigning the entire system."),
    page("1", "1.5 PROJECT SCOPE", "DealScout covers product discovery and comparison for mobiles, laptops, and general items.", ["Search a predefined sample catalog stored in products.json.", "Optionally retrieve live shopping results.", "Compare normalized offers.", "Highlight the minimum price.", "Store and summarize search activity in searches.json.", "Provide login, responsive design, downloadable resources, and quick setup scripts."], "The scope ends before checkout. DealScout is an information and decision-support application, not a retailer, payment processor, inventory authority, or delivery service."),
    page("1", "1.5 LIMITATIONS", "Every comparison system depends on the quality, freshness, and completeness of its source data.", ["Sample prices are not current retailer prices.", "Live mode requires a configured provider key.", "Taxes, exact variant, location, and shipping may affect final checkout cost.", "The demo login is not production identity management; passwords are stored in plain text in users.json for the preview only.", "JSON files suit a single-server educational workload, not thousands of concurrent writers.", "Retailer links may be unavailable in sample mode."], "These limitations are shown honestly in the interface. Future work can add verified retailer partnerships, a database such as MongoDB (Semester V elective), hashed passwords, and variant matching."),

    # ---------- Chapter 2 ----------
    page("2", "2.1 HARDWARE REQUIREMENTS", "DealScout is lightweight enough for an ordinary student computer or a college laboratory machine.", ["Processor: dual-core 64-bit processor or better.", "Memory: minimum 2 GB RAM; 4 GB recommended.", "Storage: less than 50 MB for source code, data files and documents.", "Display: 1280×720 or higher recommended; the layout also adapts to phones.", "Network: optional — needed only for the live provider mode and for downloading Node.js once."], "Because the server is a single Node.js process reading small JSON files, no dedicated database server or container runtime is required. The same machine runs both the server and the browser."),
    page("2", "2.1 SOFTWARE REQUIREMENTS", "Only software named in the Semester V practical course (CS-306-MJ-P) is required.", ["Operating system: Windows 10/11, macOS, or Linux.", "Runtime: Node.js v14 or higher with npm (project runs without any npm package).", "Browser: Google Chrome, Mozilla Firefox, or Microsoft Edge.", "Editor: Visual Studio Code, Sublime Text, or Atom (optional for normal use).", "Documents: any PDF reader and Microsoft Word / LibreOffice for the report."], "The quick setup scripts (setup.bat / setup.sh) check that Node.js exists, start server.js, and open http://localhost:3000 in the default browser."),
    page("2", "2.2 FRONTEND TECHNICAL REQUIREMENTS", "The frontend must be responsive, accessible, and independent of hard-coded server addresses.", ["Semantic HTML5 elements: header, nav, main, section, footer, form, table.", "CSS3: custom properties, flexbox, grid, media queries, transitions and a keyframe animation.", "JavaScript ES6+: modules of functions, template literals, destructuring, spread, async/await.", "fetch() calls relative /api paths so the site works on any host or port.", "Every interactive element carries a data-testid attribute for browser testing."], "The interface renders its shell even when server data is unavailable, and DOM updates are performed with innerHTML templates built from escaped values to avoid script injection.", code=["const params = new URLSearchParams({ q: query, category, mode: state.mode });", "state.result = await api(`/products/search?${params}`);", "renderResults();"]),
    page("2", "2.2 BACKEND TECHNICAL REQUIREMENTS (NODE.JS)", "The server must serve static files, validate requests, and expose every route under /api as JSON — using only Node.js core modules.", ["http.createServer() handles every request on one port.", "The url module (URL, URLSearchParams) parses paths and query strings.", "The path module safely maps URLs to files inside /public and blocks ../ traversal.", "The fs module streams static files and reads/writes JSON data.", "The crypto module generates unique ids and session tokens."], "Routes are matched by a simple switch on “METHOD /path”, keeping the server easy to read for a viva. The provider key, when used, stays in a server environment variable and never reaches the browser.", code=["const server = http.createServer(async (req, res) => {", "  const url = new URL(req.url, `http://${req.headers.host}`);", "  if (url.pathname.startsWith(\"/api\")) await handleApi(req, res, url);", "  else await serveStatic(req, res, url.pathname);", "});", "server.listen(process.env.PORT || 3000);"]),
    page("2", "2.2 DATA STORAGE AND DEPLOYMENT REQUIREMENTS", "Search activity must survive server restarts and remain separate from source code, without installing a database server.", ["data/products.json — the sample catalog (read-only at runtime).", "data/users.json — demo login accounts.", "data/searches.json — append-only search log written with fs.promises.writeFile.", "Writes are queued one after another so concurrent searches never corrupt the file.", "Deployment = copy the folder and run node server.js; PORT and SERPAPI_KEY are optional environment variables."], "Although the college guideline describes relational tables, the implementation uses equivalent JSON collections. The report identifies entities, fields, keys, and relationships clearly.", code=["async function readJson(file, fallback = []) {", "  try { return JSON.parse(await fs.promises.readFile(dataPath(file), \"utf-8\")); }", "  catch (error) { if (error.code === \"ENOENT\") return fallback; throw error; }", "}"]),
    page("2", "2.3 FUNCTIONAL REQUIREMENTS — ACCESS", "Access requirements define how visitors and signed-in users move through the application.", ["FR-01: Visitor can open the comparison page.", "FR-02: Visitor can open the sign-in page.", "FR-03: Valid credentials create an HTTP-only session cookie.", "FR-04: Invalid credentials return HTTP 401 and a clear error.", "FR-05: Signed-in user can view shopping insights and sign out.", "FR-06: Guest cannot retrieve protected analytics data."], "Authentication protects personal search summaries while leaving the core comparison experience publicly accessible."),
    page("2", "2.3 FUNCTIONAL REQUIREMENTS — COMPARISON", "The central functional requirements describe the complete search-to-recommendation flow.", ["FR-07: Accept a query between 2 and 80 characters (HTML minlength/maxlength plus server check).", "FR-08: Filter by All, Mobiles, Laptops, or General.", "FR-09: Select Sample prices or Live search.", "FR-10: Display normalized offers in a table.", "FR-11: Identify the offer with minimum price.", "FR-12: Show a truthful notice when live data is unavailable.", "FR-13: Record every completed search in searches.json."], "The highlighted result is based on listed price only. The UI retains seller, delivery, rating, and discount so the user can make a broader judgment."),
    page("2", "2.4 DATA REQUIREMENTS", "Data requirements define the minimum information needed to compare offers and summarize searches.", ["User: id, name, email, password (preview only), and role.", "ProductOffer: id, product_name, category, source, seller, price, original_price, currency, rating, delivery, discount, product_url, mode, is_live, is_mocked, retrieved_at.", "SearchLog: id, query, category, mode, result_count, best_price, searched_at, sources.", "AnalyticsSummary: total_searches, unique_queries, average_results, top_query, source_counts, recent_searches."], "String UUID values from crypto.randomUUID() are used as identifiers. Prices are JavaScript numbers and timestamps are ISO-8601 strings generated on the server."),
    page("2", "2.4 PERFORMANCE REQUIREMENTS", "The application should feel responsive for a small educational workload.", ["Local sample searches return in well under one second.", "Live provider requests use an 8-second timeout.", "searches.json is capped at the most recent 500 records.", "Analytics reads at most 100 records.", "The UI shows “Finding offers…” while a request is pending.", "Static assets are sent with cache headers; HTML is not cached."], "Performance depends on hardware and provider availability. The design avoids unbounded file growth and does not block the event loop with synchronous file access."),
    page("2", "2.4 SECURITY REQUIREMENTS", "Security requirements protect credentials, sessions, provider keys, and server files.", ["Provider secret stays in a server environment variable.", "Sessions use HttpOnly, SameSite=Lax cookies that expire after 8 hours.", "Protected analytics validates the active session on every call.", "Query length, category and JSON body size are validated on the server.", "Static file paths are normalized and confined to the /public directory.", "All user-supplied text is HTML-escaped before rendering."], "The bundled login is explicitly a preview account. Production use would add password hashing, HTTPS, and persistent sessions."),

    # ---------- Chapter 3 ----------
    page("3", "3.1 END USERS", "Database design starts by identifying the people who use DealScout and the entities required by their actions.", ["Visitor searches and compares offers without an account.", "Signed-in shopper reviews insights.", "Future administrator edits products.json and users.json.", "Evaluator or maintainer reviews behavior and stored records."], "User roles are deliberately simple. Permissions are applied at the analytics endpoint, while comparison remains available without registration."),
    page("3", "3.2 ENTITIES AND ATTRIBUTES", "The data model contains User, ProductOffer, SearchLog, and AnalyticsSummary entities stored in or derived from JSON files.", ["User primary key: id (users.json).", "ProductOffer primary key: id, generated when products.json is loaded.", "SearchLog primary key: id (searches.json).", "SearchLog.sources is an array of store names included in a comparison.", "AnalyticsSummary is calculated from SearchLog records rather than stored."], "Entity attributes correspond directly to the JavaScript objects built in modules/products.js and consumed by public/js/app.js, so the same names appear in code, data files and this report."),
    page("3", "3.2 ER DIAGRAM", "The ER diagram shows the logical relationship between a shopper, searches, offers, and store sources.", ["A user can review many search logs.", "A search can return many product offers.", "An offer belongs to one source at retrieval time.", "Analytics aggregates many search logs."], "Each entity maps to one JSON file; adding an owner_id to searches.json is recommended for a true multi-user version.", DIAGRAMS["er"]),
    page("3", "3.3 USER FILE — users.json", "The User record represents an authenticated identity used to open protected insights.", ["id — string, primary identifier.", "name — string, display name.", "email — string, login identifier (compared case-insensitively).", "password — string, preview only.", "role — string, access role."], "A production implementation would store a password hash and use a database with a unique email index.", code=["[", "  { \"id\": \"preview-user-001\", \"name\": \"DealScout User\",", "    \"email\": \"preview@dealscout.local\", \"role\": \"student\" }", "]"]),
    page("3", "3.3 PRODUCT FILE — products.json AND ProductOffer", "products.json holds the sample catalog; each row becomes a normalized ProductOffer object.", ["price and original_price are numbers; discount is derived.", "currency defaults to INR.", "rating, delivery and product_url may be absent.", "mode identifies sample or live retrieval; is_live and is_mocked prevent misleading labels.", "retrieved_at communicates freshness."], "Normalization allows a single comparison table and one minimum-price function to work across different sources.", code=["{ \"product_name\": \"Apple iPhone 15 128GB\", \"category\": \"Mobiles\",", "  \"source\": \"Flipkart\", \"seller\": \"Flipkart Seller\",", "  \"price\": 68499, \"original_price\": 79900, \"rating\": 4.5, \"delivery\": \"2 days\" }"]),
    page("3", "3.3 SEARCH LOG FILE — searches.json", "searches.json records completed comparisons for later analysis; newest records are kept first.", ["id — UUID string.", "query, category, mode — what the user asked for.", "result_count — number of normalized offers.", "best_price — minimum price or null.", "searched_at — ISO timestamp from the server.", "sources — store names returned by the search."], "The file is rewritten atomically by a single queued writer, which is the JSON-file equivalent of a transaction.", code=["{ \"id\": \"6f1c…\", \"query\": \"iPhone 15\", \"category\": \"All\", \"mode\": \"demo\",", "  \"result_count\": 3, \"best_price\": 68499,", "  \"searched_at\": \"2026-10-06T19:25:11.000Z\", \"sources\": [\"Amazon\", \"Flipkart\", \"Croma\"] }"]),
    page("3", "3.3 RELATIONSHIPS AND DATA FLOW", "The browser submits a query, the server produces ProductOffer objects, and one SearchLog is appended before the response returns.", ["Logical User-to-SearchLog relationship: one-to-many.", "SearchLog-to-ProductOffer relationship: one-to-many during a response.", "Source-to-ProductOffer relationship: one-to-many.", "Analytics-to-SearchLog relationship: calculated aggregation using map, filter and reduce."], "The application stores summary search data rather than full third-party payloads. This keeps the data files compact and limits unnecessary retention."),

    # ---------- Chapter 4 ----------
    page("4", "4.1 CLASS DIAGRAM", "The class diagram connects data structures to the modules that use them.", ["User contains identity and role data.", "ProductOffer contains comparable fields.", "ProductService (modules/products.js) retrieves, normalizes, and compares.", "AnalyticsService (modules/analytics.js) summarizes logs.", "Auth functions (modules/auth.js) create and validate sessions."], "Although JavaScript modules are used instead of formal classes, each module has one responsibility, which is what the diagram shows.", DIAGRAMS["class"]),
    page("4", "4.2 OBJECT DIAGRAM", "The object diagram illustrates a single iPhone comparison at a moment in time.", ["previewUser is an instance of User.", "iphoneSearch is an instance of SearchLog.", "flipkartOffer and amazonOffer are ProductOffer instances.", "The search object references returned source values."], "Object diagrams help explain how data definitions become actual runtime values.", DIAGRAMS["object"]),
    page("4", "4.3 COMPONENT DIAGRAM", "The component diagram displays the major software modules.", ["Browser UI (HTML/CSS/JS) handles presentation and interaction.", "Node.js HTTP server validates and coordinates work.", "JSON data files persist catalog, users and search logs.", "Shopping provider optionally supplies live offers."], "All browser-server communication uses JSON over relative /api routes.", DIAGRAMS["component"]),
    page("4", "4.4 DEPLOYMENT DIAGRAM", "A single Node.js process serves both the web pages and the API on one machine.", ["The browser connects to localhost:3000 (or a chosen PORT).", "Node.js reads and writes the data/ folder.", "Internet access is used only in live mode.", "The same folder runs on Windows, macOS, or Linux."], "No containers, web server software, or database service are needed.", DIAGRAMS["deployment"]),
    page("4", "4.5 USE CASE DIAGRAM", "Use cases describe behavior from the shopper's point of view.", ["Search product.", "Choose category and data source.", "Compare normalized offers.", "View best price.", "Sign in / sign out.", "View comparison insights.", "Download support resources."], "Administration and purchasing are outside the current scope.", DIAGRAMS["usecase"]),
    page("4", "4.6 ACTIVITY DIAGRAM", "The main activity begins with user input and ends with a displayed and recorded comparison.", ["Enter and validate query.", "Filter the catalog or request the provider.", "Normalize accepted results.", "Find minimum price.", "Append a search log.", "Display notice, best-price card, and offer table."], "If no offers match, the UI displays a useful empty state instead of a blank page.", DIAGRAMS["activity"]),
    page("4", "4.7 SEQUENCE DIAGRAM", "The sequence diagram emphasizes message order between shopper, browser, server and files.", ["Browser JavaScript sends GET /api/products/search via fetch().", "Server reads products.json (cached after first load).", "Server builds ProductOffer objects and selects the minimum.", "Server appends to searches.json.", "Server returns SearchResponse JSON.", "Browser renders cards and table."], "Login follows a similar request sequence but creates an HTTP-only cookie.", DIAGRAMS["sequence"]),
    page("4", "4.8 SYSTEM ARCHITECTURE AND ALGORITHM", "DealScout uses a layered client-server architecture and a simple minimum-price recommendation algorithm.", ["Presentation layer: HTML pages styled with CSS, updated by JavaScript.", "API layer: Node.js http server with a route switch.", "Business layer: matching, normalization, and comparison.", "Data layer: JSON files accessed through the fs module."], "Algorithm: collect matching offers; discard entries without a usable price; compare numeric prices with reduce(); return the id of the lowest as best_deal_id; the browser highlights that row and card.", code=["const best = results.reduce(", "  (lowest, offer) => (lowest === null || offer.price < lowest.price ? offer : lowest),", "  null,", ");"]),

    # ---------- Chapter 5 ----------
    page("5", "5.1.1 LOGIN SCREEN", "The login screen grants access to private shopping insights.", ["Email input uses HTML5 type=email validation.", "Password input masks entered characters.", "Sign-in button submits credentials with fetch() POST.", "Invalid credentials display a concise error.", "Preview account details support evaluation."], "The two-column layout separates the product message from the focused sign-in card.", SCREENS["login"]),
    page("5", "5.1.2 REGISTRATION SCREEN (PROPOSED)", "Registration is not implemented in the current version because only one evaluation account is required.", ["Proposed fields: full name, email, password, confirm password.", "Proposed validation: unique email and password policy.", "Proposed output: new record in users.json and an active session.", "Passwords must be hashed before storage."], "This documented future screen satisfies the planned multi-user extension without claiming that registration is available today."),
    page("5", "5.1.3 ADD RECORD SCREEN (PROPOSED)", "Catalog editing is currently done by editing products.json rather than through a public screen.", ["Proposed administrator fields: product name, category, store, seller, price, original price, rating, delivery, and URL.", "Required validation: positive price, recognized category, safe URL.", "Actions: save, clear, cancel, and preview."], "An authenticated administrator role should be introduced before this screen is enabled."),
    page("5", "5.2.1 DASHBOARD", "The dashboard gives immediate access to navigation, mode selection, category filter, product query, examples, and feature explanation.", ["Hero communicates the service benefit.", "Search form is visually dominant.", "Sample and Live controls are clearly separated.", "Popular queries accelerate first use."], "The page uses professional, consumer-facing language.", SCREENS["dashboard"]),
    page("5", "5.2.2 SEARCH RESULT SCREEN", "Search results place the best price before the detailed comparison table.", ["Query, result count, and source label remain visible.", "Preview-mode notice prevents misleading live claims.", "Best-price card shows product, store, seller, delivery, price, and discount.", "Table scrolls horizontally on narrow screens."], "Emerald is reserved for savings and the best-price recommendation.", SCREENS["results"]),
    page("5", "5.2.3 INSIGHTS SCREEN", "The insights screen summarizes stored comparison activity for a signed-in user.", ["Comparison count, unique search count and most searched query.", "Recent comparison table.", "Store frequency list.", "Sign-in prompt for guests."], "Compact cards and tables keep the values easy to verify against searches.json.", SCREENS["insights"]),
    page("5", "5.2.4 RESOURCES AND QUICK SETUP SCREEN", "The resources page offers the documentation downloads and the quick setup instructions.", ["Word report, PDF report, viva guide, and setup guide downloads.", "Step list: install Node.js, open the folder, run setup.bat or setup.sh.", "Single-command alternative: node server.js."], "Files are served by the same Node.js static handler as every other asset.", SCREENS["resources"]),

    # ---------- Chapter 6 ----------
    page("6", "TESTING AND VALIDATION", "Testing confirms the main flow and important failure states across the API and the browser.", ["GET /api/ returns ok: true.", "Valid search returns results and best_deal_id; the best offer has the lowest price.", "One-character query returns HTTP 400.", "Valid login returns the user and sets the session cookie; wrong password returns 401.", "GET /api/analytics returns 401 for guests and a summary after login.", "Unknown page returns the custom 404 page.", "Browser flow: search → best price → live preview notice → login → insights with no console errors."], "A change is considered complete only when the exact failed check passes after correction."),
    page("6", "CONCLUSION AND FUTURE SCOPE", "DealScout demonstrates a complete comparison workflow using only the Semester V web stack: a responsive HTML/CSS interface, ES6+ browser logic, a Node.js server, and JSON file storage.", ["Connect verified retailer or shopping-provider credentials.", "Add product-variant matching and currency normalization.", "Include shipping and tax in total-cost comparison.", "Move data to MongoDB (Semester V elective CS-309) and hash passwords.", "Add price alerts, favorites, and historical trends.", "Create an administrator catalog editor."], "The current solution meets its defined objective while clearly separating implemented behavior from future enhancements."),
    page("6", "BIBLIOGRAPHY / REFERENCES", "The following sources support implementation and documentation.", ["MDN Web Docs — HTML, CSS and JavaScript reference — https://developer.mozilla.org/", "Node.js Documentation — http, fs, path, url, crypto modules — https://nodejs.org/docs/", "ECMAScript 2015+ Language Specification — https://tc39.es/ecma262/", "SerpApi Google Shopping API — https://serpapi.com/google-shopping-api", "Savitribai Phule Pune University, T.Y.B.Sc. (Computer Science) NEP syllabus, CS-303-MJ-T Web Technology-I and CS-331-FP Project.", "Kaveri College project documentation instructions supplied for academic year " + YEAR + "."], "All product and retailer names are used for demonstration. Live data use must follow the chosen provider's terms, rate limits, attribution, and caching rules."),
    page("6", "APPENDIX — SYLLABUS MAPPING AND VIVA CHECKLIST", "This final page maps the implementation to the CS-303-MJ-T units and lists what to prepare before review.", ["Unit 1 Frontend Fundamentals → index.html, login.html, resources.html, style.css.", "Unit 2 Advanced JavaScript (ES6+) → app.js, login.js, common.js (fetch, async/await, template literals, array methods).", "Unit 3 Node.js Fundamentals → server.js, modules/api.js (http, url, path, crypto, modules, npm scripts).", "Unit 4 File Handling with Node.js → modules/filestore.js and the data/*.json files.", "Fill names, seat numbers, guide, coordinator, principal, examiner, date and signatures.", "Carry the Word and PDF report, viva guide, source folder and setup guide."], "Core viva explanation: DealScout receives a query, normalizes offers to one object structure, finds the minimum numeric price with reduce(), appends a search log to a JSON file, and displays both the recommendation and the supporting comparison rows."),
]

CHAPTER_TITLES = {"0": "Front Matter", "1": "Chapter 1 — Preliminary Investigation", "2": "Chapter 2 — Requirement Specification", "3": "Chapter 3 — Database Design", "4": "Chapter 4 — System Design", "5": "Chapter 5 — Input and Output Screen Layout", "6": "Chapter 6 — Testing, Conclusion and References"}

# Sequence required by the college: Title Page -> Certificate -> Index -> Index-wise pages.
PAGES = [{"type": "title", "title": "DEALSCOUT"}, {"type": "certificate", "title": "CERTIFICATE"}, {"type": "index1", "title": "INDEX"}, {"type": "index2", "title": "INDEX (CONTINUED)"}] + CONTENT
assert len(PAGES) == TOTAL_PAGES, f"Expected {TOTAL_PAGES} pages, got {len(PAGES)}"

# Index rows: (sr, title, page no.) — page numbers derived from the actual sequence above.
KEEP_UPPER = {"ER", "I/O", "ES6+", "API", "UI", "JSON", "HTML", "CSS", "FR", "—", "/", "&"}
SMALL_WORDS = {"and", "or", "of", "the", "a", "in", "vs", "with"}


def index_title(title: str) -> str:
    words = []
    for position, word in enumerate(title.replace("NODE.JS", "Node.js").split(" ")):
        if word in KEEP_UPPER or "." in word or any(char.islower() for char in word):
            words.append(word)
        elif word.lower() in SMALL_WORDS and position > 0:
            words.append(word.lower())
        else:
            words.append(__import__("re").sub(r"[A-Za-z]+", lambda match: match.group(0).capitalize(), word))
    return " ".join(words)


INDEX_ROWS = [(str(number), index_title(item["title"]), str(PAGES.index(item) + 1)) for number, item in enumerate(CONTENT, start=1)]
INDEX_SPLIT = 23
INDEX_PARTS = {"index1": INDEX_ROWS[:INDEX_SPLIT], "index2": INDEX_ROWS[INDEX_SPLIT:]}

CERTIFICATE_TEXT = f"This is to certify that Mr. / Ms. ______________________________, T.Y. B.Sc. (Computer Science) Semester V, has successfully completed his/her Project Work titled “DealScout” in Computer Science Specialization as a part of CS-331-FP Project as prescribed by Savitribai Phule Pune University for academic year {YEAR}."


# ----------------------------------------------------------------------------- DOCX helpers
def set_cell_text(cell, text: str, bold: bool = False, size: int = 11):
    cell.text = ""
    run = cell.paragraphs[0].add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def style_run(run, size=12, bold=False, color=None, mono=False):
    name = "Courier New" if mono else "Times New Roman"
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color.replace("#", ""))


def add_footer(section):
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(paragraph.add_run("DealScout  •  "), 9, color=GREY)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


def add_doc_title(document: Document, title: str, size: int = 20):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(16)
    style_run(paragraph.add_run(title), size, True, NAVY)


def add_doc_paragraph(document: Document, text: str, bold: bool = False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    paragraph = document.add_paragraph()
    paragraph.alignment = align
    paragraph.paragraph_format.line_spacing = 1.25
    paragraph.paragraph_format.space_after = Pt(8)
    style_run(paragraph.add_run(text), 12, bold)
    return paragraph


def add_doc_bullet(document: Document, text: str):
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.space_after = Pt(4)
    style_run(paragraph.add_run(text), 12)


def add_doc_code(document: Document, lines: list[str]):
    table = document.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    cell.text = ""
    for index, line in enumerate(lines):
        paragraph = cell.paragraphs[0] if index == 0 else cell.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(0)
        style_run(paragraph.add_run(line), 9.5, mono=True)
    document.add_paragraph().paragraph_format.space_after = Pt(2)


def add_title_page(document: Document):
    for _ in range(2):
        document.add_paragraph()
    for text, size, bold in [
        ("KANNADA SANGHA PUNE'S", 14, True),
        ("KAVERI COLLEGE OF ARTS, SCIENCE & COMMERCE, PUNE", 16, True),
        ("A PROJECT REPORT ON", 20, True),
        ("DEALSCOUT", 20, True),
        ("An E-Commerce Product Comparison and Best-Deal Recommendation System", 16, False),
        ("(HTML • CSS • JavaScript • Node.js)", 12, False),
        ("T.Y.B.Sc. (Computer Science) — Semester V", 16, True),
        (f"Academic Year {YEAR}", 14, True),
    ]:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(20 if size >= 20 else 12)
        style_run(paragraph.add_run(text), size, bold, NAVY)
    add_doc_paragraph(document, "Submitted by", True, WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "Name 1: ______________________________    Seat No.: __________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "Name 2: ______________________________    Seat No.: __________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "Name 3: ______________________________    Seat No.: __________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "Under the guidance of: ______________________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "In partial fulfilment of B.Sc. (Computer Science), Savitribai Phule Pune University", align=WD_ALIGN_PARAGRAPH.CENTER)


def add_certificate(document: Document):
    add_doc_title(document, "KAVERI COLLEGE OF ARTS, SCIENCE & COMMERCE", 16)
    add_doc_paragraph(document, "PERMANENTLY AFFILIATED TO SAVITRIBAI PHULE PUNE UNIVERSITY, PUNE", True, WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_paragraph(document, "Sr. No. 36, Shri G.M. Shetty Educational Complex, Ganeshnagar, Erandwane, Pune 411038.", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_doc_title(document, "CERTIFICATE")
    add_doc_paragraph(document, CERTIFICATE_TEXT)
    add_doc_paragraph(document, "Seat No.: ____________________     Date: ____________________")
    table = document.add_table(rows=2, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for index, role in enumerate(["Project Guide", "Course Coordinator", "Principal"]):
        set_cell_text(table.cell(0, index), role, True)
        set_cell_text(table.cell(1, index), "Name: __________________\nSignature: ______________")
    document.add_paragraph()
    add_doc_paragraph(document, "Examined by", True, WD_ALIGN_PARAGRAPH.CENTER)
    exam = document.add_table(rows=2, cols=2)
    exam.style = "Table Grid"
    for index, role in enumerate(["Internal Examiner", "External Examiner"]):
        set_cell_text(exam.cell(0, index), role, True)
        set_cell_text(exam.cell(1, index), "Name: __________________\nSignature: ______________\nDate: __________________")


def add_index(document: Document, page_type: str):
    add_doc_title(document, "INDEX" if page_type == "index1" else "INDEX (CONTINUED)")
    table = document.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for index, heading in enumerate(["Sr. No.", "Title", "Page No.", "Signature of Instructor"]):
        set_cell_text(table.cell(0, index), heading, True, 10)
    for number, title, page_no in INDEX_PARTS[page_type]:
        cells = table.add_row().cells
        set_cell_text(cells[0], number, size=10)
        set_cell_text(cells[1], title, size=10)
        set_cell_text(cells[2], page_no, size=10)
        set_cell_text(cells[3], "", size=10)
    for row in table.rows:
        row.cells[0].width, row.cells[1].width, row.cells[2].width, row.cells[3].width = Inches(0.7), Inches(3.9), Inches(0.8), Inches(1.5)


def build_docx():
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(22)
    section.left_margin = section.right_margin = Mm(24)
    add_footer(section)
    if "Report Body" not in document.styles:
        body_style = document.styles.add_style("Report Body", WD_STYLE_TYPE.PARAGRAPH)
        body_style.font.name = "Times New Roman"
        body_style.font.size = Pt(12)
    for index, item in enumerate(PAGES):
        if index:
            document.add_page_break()
        page_type = item["type"]
        if page_type == "title":
            add_title_page(document)
        elif page_type == "certificate":
            add_certificate(document)
        elif page_type in INDEX_PARTS:
            add_index(document, page_type)
        else:
            add_doc_title(document, item["title"])
            add_doc_paragraph(document, item["purpose"])
            for point in item["points"]:
                add_doc_bullet(document, point)
            add_doc_paragraph(document, item["explanation"])
            if item.get("code"):
                add_doc_code(document, item["code"])
            if item.get("image"):
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(item["image"], width=Inches(5.6))
                caption = document.add_paragraph(f"Figure {index + 1}: {index_title(item['title'])}")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                style_run(caption.runs[0], 10, False, GREY)
    document.core_properties.title = "DealScout Project Report — 50 Pages"
    document.core_properties.subject = "T.Y.B.Sc. Computer Science Semester V project documentation (HTML, CSS, JavaScript, Node.js)"
    document.core_properties.author = "DealScout"
    document.save(OUTPUT / "DealScout_Project_Report_50_Pages.docx")


# ----------------------------------------------------------------------------- PDF helpers
def pdf_wrap(pdf, text: str, x: float, y: float, width_chars=96, leading=15, bullet=False):
    prefix = "• " if bullet else ""
    for line in textwrap.wrap(prefix + text, width=width_chars, subsequent_indent="  " if bullet else "") or [""]:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def pdf_header(pdf, page_no: int):
    width, height = A4
    pdf.setFillColor(HexColor(NAVY))
    pdf.rect(0, height - 28, width, 28, fill=1, stroke=0)
    pdf.setFillColor(HexColor(GREEN))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(42, height - 18, "DEALSCOUT")
    pdf.setFillColor(HexColor(GREY))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(width / 2, 22, f"DealScout  •  Page {page_no} of {TOTAL_PAGES}")


def pdf_code(pdf, lines: list[str], y: float) -> float:
    width, _ = A4
    box_height = 14 * len(lines) + 14
    pdf.setFillColor(HexColor(LIGHT)); pdf.roundRect(58, y - box_height, width - 116, box_height, 6, fill=1, stroke=0)
    pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Courier", 9)
    for line in lines:
        y -= 14
        pdf.drawString(68, y + 2, line[:92])
    pdf.setFont("Times-Roman", 12)
    return y - 16


def build_pdf():
    path = OUTPUT / "DealScout_Project_Report_50_Pages.pdf"
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    for index, item in enumerate(PAGES, start=1):
        pdf_header(pdf, index)
        page_type = item["type"]
        if page_type == "title":
            pdf.setFillColor(HexColor(NAVY)); pdf.roundRect(45, 95, width - 90, height - 150, 24, fill=1, stroke=0)
            pdf.setFillColor(white); pdf.setFont("Times-Bold", 14); pdf.drawCentredString(width / 2, height - 120, "KANNADA SANGHA PUNE'S")
            pdf.setFont("Times-Bold", 17); pdf.drawCentredString(width / 2, height - 150, "KAVERI COLLEGE OF ARTS, SCIENCE & COMMERCE, PUNE")
            pdf.setFillColor(HexColor(GREEN)); pdf.setFont("Times-Bold", 20); pdf.drawCentredString(width / 2, height - 255, "A PROJECT REPORT ON")
            pdf.setFont("Times-Bold", 36); pdf.drawCentredString(width / 2, height - 305, "DEALSCOUT")
            pdf.setFillColor(white); pdf.setFont("Times-Roman", 14); pdf.drawCentredString(width / 2, height - 340, "E-Commerce Product Comparison and Best-Deal Recommendation System")
            pdf.setFont("Times-Roman", 11); pdf.drawCentredString(width / 2, height - 362, "(HTML  •  CSS  •  JavaScript  •  Node.js)")
            pdf.setFont("Times-Bold", 15); pdf.drawCentredString(width / 2, height - 410, f"T.Y.B.Sc. (Computer Science) — Semester V  •  Academic Year {YEAR}")
            pdf.setFont("Times-Bold", 12); pdf.drawCentredString(width / 2, height - 465, "Submitted by")
            pdf.setFont("Times-Roman", 12)
            for offset, label in enumerate(["Name 1", "Name 2", "Name 3"]):
                pdf.drawCentredString(width / 2, height - 495 - offset * 28, f"{label}: __________________________   Seat No.: ______________")
            pdf.drawCentredString(width / 2, height - 600, "Under the guidance of: __________________________")
            pdf.drawCentredString(width / 2, 135, "In partial fulfilment of B.Sc. (Computer Science), Savitribai Phule Pune University")
        elif page_type == "certificate":
            pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Times-Bold", 15); pdf.drawCentredString(width / 2, height - 80, "KAVERI COLLEGE OF ARTS, SCIENCE & COMMERCE")
            pdf.setFont("Times-Roman", 9); pdf.drawCentredString(width / 2, height - 100, "PERMANENTLY AFFILIATED TO SAVITRIBAI PHULE PUNE UNIVERSITY, PUNE")
            pdf.drawCentredString(width / 2, height - 114, "Sr. No. 36, Shri G.M. Shetty Educational Complex, Ganeshnagar, Erandwane, Pune 411038.")
            pdf.setFont("Times-Bold", 20); pdf.drawCentredString(width / 2, height - 165, "CERTIFICATE")
            pdf.setFont("Times-Roman", 12); y = pdf_wrap(pdf, CERTIFICATE_TEXT, 65, height - 215, 82, 18)
            y -= 22; pdf.drawString(65, y, "Seat No.: ____________________     Date: ____________________")
            y -= 110
            for x, role in [(65, "Project Guide"), (225, "Course Coordinator"), (405, "Principal")]:
                pdf.setFont("Times-Bold", 11); pdf.drawString(x, y, role); pdf.setFont("Times-Roman", 10); pdf.drawString(x, y - 28, "Name: ______________"); pdf.drawString(x, y - 48, "Signature: ___________")
            y -= 115; pdf.setFont("Times-Bold", 16); pdf.drawCentredString(width / 2, y, "Examined by")
            for x, role in [(100, "Internal Examiner"), (360, "External Examiner")]:
                pdf.setFont("Times-Bold", 11); pdf.drawString(x, y - 55, role); pdf.setFont("Times-Roman", 10); pdf.drawString(x, y - 80, "Name: __________________"); pdf.drawString(x, y - 100, "Signature: ______________"); pdf.drawString(x, y - 120, "Date: ___________________")
        elif page_type in INDEX_PARTS:
            pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Times-Bold", 20); pdf.drawCentredString(width / 2, height - 70, item["title"])
            columns = [(48, "Sr. No."), (100, "Title"), (400, "Page No."), (462, "Signature of Instructor")]
            y = height - 105
            pdf.setFillColor(HexColor(LIGHT)); pdf.rect(45, y - 8, width - 90, 24, fill=1, stroke=0)
            pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Times-Bold", 10)
            for x, heading in columns:
                pdf.drawString(x + 4, y, heading)
            pdf.setStrokeColor(HexColor("#CBD5E1")); pdf.setLineWidth(0.6)
            for number, title, page_no in INDEX_PARTS[page_type]:
                y -= 27
                pdf.line(45, y - 9, width - 45, y - 9)
                pdf.setFont("Times-Roman", 10); pdf.drawString(58, y, number); pdf.drawString(104, y, title[:60]); pdf.drawCentredString(428, y, page_no)
            pdf.rect(45, y - 9, width - 90, height - 105 - y + 25, fill=0, stroke=1)
            for x, _ in columns[1:]:
                pdf.line(x - 4, height - 105 + 16, x - 4, y - 9)
        else:
            pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Times-Bold", 18); pdf.drawCentredString(width / 2, height - 76, item["title"])
            pdf.setStrokeColor(HexColor(GREEN)); pdf.setLineWidth(3); pdf.line(55, height - 92, width - 55, height - 92)
            pdf.setFillColor(black); pdf.setFont("Times-Roman", 12); y = height - 125
            y = pdf_wrap(pdf, item["purpose"], 58, y, 88, 16)
            y -= 12
            for point in item["points"]:
                y = pdf_wrap(pdf, point, 72, y, 84, 15, True)
                y -= 3
            y -= 8
            y = pdf_wrap(pdf, item["explanation"], 58, y, 88, 16)
            if item.get("code"):
                y = pdf_code(pdf, item["code"], y - 4)
            if item.get("image") and y > 230:
                image_height = min(250, y - 65)
                pdf.drawImage(item["image"], 60, 55, width=width - 120, height=image_height, preserveAspectRatio=True, anchor="c")
        pdf.showPage()
    pdf.save()


# ----------------------------------------------------------------------------- Companion PDFs
VIVA_PAGES = [
    ("DealScout Viva Companion", "Use this guide to explain the system in simple, accurate language. Start with the problem, show the workflow, then discuss technology and limitations.", ["One-line definition: DealScout compares normalized product offers and highlights the lowest listed price.", "Demonstration order: search → comparison → best price → login → insights.", "Technology: HTML, CSS, JavaScript (ES6+), Node.js core modules, JSON files — exactly the CS-303 Web Technology-I syllabus."]),
    ("60-Second Introduction", "DealScout reduces the effort of visiting many stores separately. A user enters a product name, chooses a category and source mode, and receives normalized offers.", ["The Node.js server validates the query.", "Offers use one common ProductOffer object structure.", "The minimum numeric price becomes the best deal.", "Each search is appended to searches.json."]),
    ("Problem and Objectives", "The main problem is inconsistent and scattered e-commerce information.", ["Save comparison time.", "Improve clarity through a common table.", "Show seller, rating, discount, and delivery with price.", "Record searches for later review.", "Run anywhere Node.js is installed."]),
    ("Architecture Answer", "The system follows a client-server architecture with no frameworks.", ["HTML, CSS and JavaScript run in the browser.", "server.js uses http.createServer to serve static files and /api routes.", "modules/*.js separate products, auth, analytics and file storage.", "JSON files in data/ store catalog, users and search logs.", "An optional https call supplies live shopping results."]),
    ("Search Algorithm", "Explain the algorithm step by step without jargon.", ["Read and trim the query.", "Reject input shorter than two characters (HTTP 400).", "Filter matching offers by query words and category.", "Normalize every accepted offer.", "Use reduce() to find the minimum price → best_deal_id.", "Append the summary to searches.json and return JSON."]),
    ("Node.js Modules Used", "Be ready to name each core module and its purpose.", ["http — create the server and handle requests/responses.", "fs (fs.promises) — read/write JSON data files and stream static files.", "path — safe file paths inside /public.", "url — URL and URLSearchParams parsing.", "crypto — randomUUID() for ids and randomBytes() for session tokens.", "https — optional live provider request."]),
    ("JavaScript (ES6+) Features Used", "Point to concrete examples in the code.", ["const/let, arrow functions, template literals.", "Destructuring and spread (...offer).", "Array methods: map, filter, reduce, find, some, flatMap.", "async/await with fetch() in the browser and fs.promises on the server.", "Map and Set, optional chaining (?.), nullish coalescing (??)."]),
    ("Database Answer", "The project stores data in JSON files, the equivalent of tables.", ["products.json → sample catalog (read-only).", "users.json → login accounts.", "searches.json → search log written by a queued writer.", "Analytics are computed on request, not stored.", "Future: migrate to MongoDB (Semester V elective)."]),
    ("Authentication Answer", "The preview login creates an HTTP-only cookie session.", ["POST /api/auth/login checks users.json.", "A random token is stored in a server-side Map with an 8-hour expiry.", "The cookie travels automatically with same-origin fetch() calls.", "GET /api/analytics returns 401 without a valid session."]),
    ("API Questions", "REST endpoints exchange JSON between the browser and server.", ["GET /api/products/search?q=&category=&mode= — search and compare.", "POST /api/auth/login — create session.", "GET /api/auth/me — return current user or null.", "POST /api/auth/logout — end session.", "GET /api/analytics — protected search insights.", "HTTP 400 means validation failed; 401 means login required."]),
    ("Live vs Sample Data", "This distinction is important during the viva.", ["Sample catalog is local, stable, and always available.", "Live search requires the SERPAPI_KEY environment variable on the server.", "Without a key, preview results are explicitly labelled and not claimed as live.", "Provider keys never appear in browser code."]),
    ("Limitations, Future Scope and Checklist", "State limitations before enhancements, then prepare the environment.", ["Limited local catalog; no checkout or payment; plain-text preview password.", "Future: verified providers, alerts, favorites, MongoDB, hashed passwords, admin tools.", "Before viva: run setup.bat / setup.sh, search iPhone 15, show best price, sign in, open Insights.", "Keep Word/PDF report, source folder and setup guide ready."]),
]

SETUP_PAGES = [
    ("Quick Setup", "DealScout needs only Node.js — no database, no npm packages, no containers.", ["Install Node.js (LTS) from https://nodejs.org/.", "Extract the dealscout folder.", "Windows: double-click setup.bat.", "macOS/Linux: run chmod +x setup.sh && ./setup.sh.", "The browser opens http://localhost:3000 automatically."]),
    ("Manual Start and Folder Layout", "Any terminal works too.", ["cd dealscout", "node server.js   (or: npm start)", "server.js — HTTP server; modules/ — api, products, auth, analytics, filestore.", "public/ — HTML, CSS, JS, downloads; data/ — products.json, users.json, searches.json.", "Change the port with PORT=4000 node server.js."]),
    ("Optional Live Provider", "Sample prices work without credentials. Live shopping requires a server-side key.", ["Get a SerpApi key.", "Windows: set SERPAPI_KEY=your_key  then  node server.js", "macOS/Linux: SERPAPI_KEY=your_key node server.js", "Never place the provider key in browser code."]),
    ("Operations and Login", "Use these notes when maintaining the local installation.", ["Stop: press Ctrl+C in the terminal window.", "Reset history: replace the contents of data/searches.json with []", "Add products: edit data/products.json and restart.", "Preview login: preview@dealscout.local / dealscout123"]),
]


def build_short_pdf(filename: str, pages: list[tuple[str, str, list[str]]], subtitle: str):
    path = OUTPUT / filename
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    total = len(pages)
    for index, (title, intro, bullets) in enumerate(pages, start=1):
        pdf.setFillColor(HexColor(NAVY)); pdf.rect(0, height - 42, width, 42, fill=1, stroke=0)
        pdf.setFillColor(HexColor(GREEN)); pdf.setFont("Helvetica-Bold", 10); pdf.drawString(45, height - 26, "DEALSCOUT")
        pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Times-Bold", 22); pdf.drawString(55, height - 95, title)
        pdf.setStrokeColor(HexColor(GREEN)); pdf.setLineWidth(3); pdf.line(55, height - 112, width - 55, height - 112)
        pdf.setFillColor(black); pdf.setFont("Times-Roman", 13); y = pdf_wrap(pdf, intro, 58, height - 150, 83, 19)
        y -= 25
        for bullet in bullets:
            y = pdf_wrap(pdf, bullet, 75, y, 78, 18, True)
            y -= 10
        pdf.setFillColor(HexColor(LIGHT)); pdf.roundRect(55, 85, width - 110, 90, 12, fill=1, stroke=0)
        pdf.setFillColor(HexColor(NAVY)); pdf.setFont("Helvetica-Bold", 11); pdf.drawString(75, 145, subtitle)
        pdf.setFont("Helvetica", 9); pdf_wrap(pdf, "Speak clearly, demonstrate the real flow, and separate implemented behavior from planned enhancements.", 75, 122, 82, 13)
        pdf.setFillColor(HexColor(GREY)); pdf.setFont("Helvetica", 9); pdf.drawCentredString(width / 2, 28, f"Page {index} of {total}")
        pdf.showPage()
    pdf.save()


if __name__ == "__main__":
    build_docx()
    build_pdf()
    build_short_pdf("DealScout_Viva_Guide.pdf", VIVA_PAGES, "VIVA TIP")
    build_short_pdf("DealScout_Setup_Guide.pdf", SETUP_PAGES, "SETUP TIP")
    print("Generated:")
    for path in sorted(OUTPUT.glob("DealScout_*")):
        print(f"- {path.name}: {path.stat().st_size} bytes")
