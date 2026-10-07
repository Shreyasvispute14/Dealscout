"""UML / ER diagram renderer for the DealScout report (PIL only).

Each function draws one diagram following standard UML notation so that the
figures match the definitions given in the college's project instructions.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK = "#111827"
LINE = "#374151"
FILL = "#FFFFFF"
SOFT = "#F3F4F6"
ACCENT = "#0F766E"
W, H = 1600, 1000


def font(size: int, bold: bool = False):
    for path in [
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/freefont/FreeSans{'Bold' if bold else ''}.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


F = {"title": font(34, True), "h": font(22, True), "b": font(20), "s": font(17), "si": font(16), "tiny": font(15)}


def new_canvas(title: str):
    image = Image.new("RGB", (W, H), FILL)
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, W - 10, H - 10), outline="#9CA3AF", width=2)
    draw.text((30, 24), title, fill=INK, font=F["title"])
    draw.line((30, 70, 30 + draw.textlength(title, font=F["title"]), 70), fill=ACCENT, width=4)
    return image, draw


def text_center(draw, cx, cy, text, fnt=None, fill=INK, underline=False):
    fnt = fnt or F["b"]
    width = draw.textlength(text, font=fnt)
    draw.text((cx - width / 2, cy - fnt.size / 2), text, fill=fill, font=fnt)
    if underline:
        draw.line((cx - width / 2, cy + fnt.size / 2 + 2, cx + width / 2, cy + fnt.size / 2 + 2), fill=fill, width=2)


def dashed_line(draw, p1, p2, dash=12, width=3, fill=LINE):
    (x1, y1), (x2, y2) = p1, p2
    length = math.hypot(x2 - x1, y2 - y1)
    if not length:
        return
    steps = int(length // dash)
    for index in range(0, steps, 2):
        t1, t2 = index / steps, min((index + 1) / steps, 1)
        draw.line((x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1, x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2), fill=fill, width=width)


def arrow_head(draw, p_from, p_to, size=16, filled=True, fill=LINE):
    (x1, y1), (x2, y2) = p_from, p_to
    angle = math.atan2(y2 - y1, x2 - x1)
    left = (x2 - size * math.cos(angle - 0.45), y2 - size * math.sin(angle - 0.45))
    right = (x2 - size * math.cos(angle + 0.45), y2 - size * math.sin(angle + 0.45))
    if filled:
        draw.polygon([(x2, y2), left, right], fill=fill)
    else:
        draw.line([left, (x2, y2), right], fill=fill, width=3)


def connector(draw, p1, p2, dashed=False, head="filled", label=None, label_offset=(0, -22), fill=LINE):
    if dashed:
        dashed_line(draw, p1, p2, fill=fill)
    else:
        draw.line((*p1, *p2), fill=fill, width=3)
    if head:
        arrow_head(draw, p1, p2, filled=head == "filled", fill=fill)
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + label_offset[0], (p1[1] + p2[1]) / 2 + label_offset[1]
        text_center(draw, mx, my, label, F["si"], fill)


def edge_point(rect, toward):
    """Point on the border of rect in the direction of `toward`."""
    x1, y1, x2, y2 = rect
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = toward[0] - cx, toward[1] - cy
    if not dx and not dy:
        return cx, cy
    scale = min(abs((x2 - x1) / 2 / dx) if dx else 9e9, abs((y2 - y1) / 2 / dy) if dy else 9e9)
    return cx + dx * scale, cy + dy * scale


def link(draw, rect_a, rect_b, **kwargs):
    ca = ((rect_a[0] + rect_a[2]) / 2, (rect_a[1] + rect_a[3]) / 2)
    cb = ((rect_b[0] + rect_b[2]) / 2, (rect_b[1] + rect_b[3]) / 2)
    connector(draw, edge_point(rect_a, cb), edge_point(rect_b, ca), **kwargs)


# --------------------------------------------------------------------------- class diagram
def class_box(draw, x, y, name, attributes, methods, width=330):
    line_h = 26
    h1, h2, h3 = 44, max(1, len(attributes)) * line_h + 12, max(1, len(methods)) * line_h + 12
    rect = (x, y, x + width, y + h1 + h2 + h3)
    draw.rectangle(rect, fill=FILL, outline=INK, width=3)
    draw.rectangle((x, y, x + width, y + h1), fill=SOFT, outline=INK, width=3)
    text_center(draw, x + width / 2, y + h1 / 2, name, F["h"])
    draw.line((x, y + h1 + h2, x + width, y + h1 + h2), fill=INK, width=3)
    for index, attribute in enumerate(attributes or ["—"]):
        draw.text((x + 14, y + h1 + 8 + index * line_h), attribute, fill=INK, font=F["s"])
    for index, method in enumerate(methods or ["—"]):
        draw.text((x + 14, y + h1 + h2 + 8 + index * line_h), method, fill=INK, font=F["s"])
    return rect


def class_diagram(path):
    image, draw = new_canvas("Class Diagram — DealScout")
    auth = class_box(draw, 60, 110, "AuthService", ["- sessions : Map<token, Session>", "- SESSION_HOURS : number = 8"], ["+ login(email, password) : Session", "+ currentUser(req) : User", "+ logout(req) : void", "+ sessionCookie(token) : string"])
    products = class_box(draw, 630, 110, "ProductService", ["- catalogCache : ProductOffer[]"], ["+ searchProducts(q, category, mode)", "- normalizeOffer(raw) : ProductOffer", "- matches(offer, q, category) : bool", "- livePreview(catalog, q, category)", "- liveProviderSearch(q, category)"])
    analytics = class_box(draw, 1200, 110, "AnalyticsService", ["- LIMIT : number = 100"], ["+ summarize() : AnalyticsSummary", "- countBy(items) : [key, count][]"])
    user = class_box(draw, 60, 560, "User", ["+ id : string", "+ name : string", "+ email : string", "+ role : string"], ["(stored in users.json)"], 300)
    offer = class_box(draw, 420, 560, "ProductOffer", ["+ id : string", "+ product_name : string", "+ source, seller : string", "+ price, original_price : number", "+ rating : number | null", "+ delivery : string | null", "+ discount : number | null", "+ mode : 'demo' | 'live'"], ["(normalized from products.json)"], 330)
    log = class_box(draw, 810, 560, "SearchLog", ["+ id : string", "+ query, category, mode : string", "+ result_count : number", "+ best_price : number | null", "+ searched_at : string (ISO)", "+ sources : string[]"], ["(stored in searches.json)"], 330)
    store = class_box(draw, 1200, 560, "FileStore", ["- DATA_DIR : string", "- writeQueue : Promise"], ["+ readJson(file, fallback) : any", "+ writeJson(file, data) : void", "+ appendJson(file, record, limit)"], 340)
    link(draw, auth, user, head="open", label="1  validates  0..*")
    link(draw, products, offer, head="open", label="1  builds  0..*", label_offset=(-70, -20))
    link(draw, products, log, head="open", label="1  appends  1", label_offset=(80, -20))
    link(draw, analytics, log, head="open", label="reads 0..*", label_offset=(-60, 0))
    link(draw, analytics, store, dashed=True, head="open", label="«use»", label_offset=(60, 0))
    link(draw, products, store, dashed=True, head="open", label="«use»", label_offset=(0, -40))
    link(draw, auth, store, dashed=True, head="open", label="«use»", label_offset=(0, 30))
    draw.text((60, 940), "Notation: solid line = association with multiplicity, dashed arrow = dependency («use»). Modules in /modules act as the classes.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- object diagram
def object_box(draw, x, y, title, slots, width=420):
    h1, line_h = 44, 26
    rect = (x, y, x + width, y + h1 + len(slots) * line_h + 14)
    draw.rectangle(rect, fill=FILL, outline=INK, width=3)
    draw.line((x, y + h1, x + width, y + h1), fill=INK, width=3)
    text_center(draw, x + width / 2, y + h1 / 2, title, F["h"], underline=True)
    for index, slot in enumerate(slots):
        draw.text((x + 14, y + h1 + 8 + index * line_h), slot, fill=INK, font=F["s"])
    return rect


def object_diagram(path):
    image, draw = new_canvas("Object Diagram — one iPhone 15 comparison at run time")
    user = object_box(draw, 60, 110, "previewUser : User", ['id = "preview-user-001"', 'name = "DealScout User"', 'email = "preview@dealscout.local"', 'role = "student"'])
    search = object_box(draw, 600, 110, "iphoneSearch : SearchLog", ['query = "iPhone 15"', 'category = "All"', 'mode = "demo"', "result_count = 3", "best_price = 68499", 'searched_at = "2026-10-06T19:25:11Z"'], 460)
    best = object_box(draw, 1130, 110, "flipkartOffer : ProductOffer", ['source = "Flipkart"', "price = 68499", "original_price = 79900", "rating = 4.5", "discount = 14"], 420)
    amazon = object_box(draw, 60, 600, "amazonOffer : ProductOffer", ['source = "Amazon"', "price = 69999", "rating = 4.6", 'delivery = "Tomorrow"'])
    croma = object_box(draw, 600, 600, "cromaOffer : ProductOffer", ['source = "Croma"', "price = 70990", "rating = 4.4", 'delivery = "3 days"'], 460)
    link(draw, user, search, head=None, label="performs")
    link(draw, search, best, head=None, label="best_deal_id")
    link(draw, search, amazon, head=None, label="results[0]", label_offset=(-70, 0))
    link(draw, search, croma, head=None, label="results[2]", label_offset=(60, 0))
    draw.rectangle((1130, 600, 1540, 760), fill="#FFFBEB", outline="#B45309", width=3)
    draw.polygon([(1510, 600), (1540, 630), (1510, 630)], fill="#FDE68A", outline="#B45309")
    for index, line in enumerate(["Note: best_deal_id points to the", "offer with the minimum price", "(68499 < 69999 < 70990), so the", "Flipkart row is highlighted as Best."]):
        draw.text((1148, 622 + index * 28), line, fill=INK, font=F["s"])
    draw.text((60, 940), "Notation: underlined header = object : Class, slots = attribute values, lines = links between objects.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- component diagram
def component_box(draw, x, y, name, sub=None, width=260, height=110):
    rect = (x, y, x + width, y + height)
    draw.rectangle(rect, fill=FILL, outline=INK, width=3)
    # UML component icon (rectangle with two small tabs)
    ix, iy = x + width - 40, y + 12
    draw.rectangle((ix, iy, ix + 24, iy + 30), fill=FILL, outline=INK, width=2)
    draw.rectangle((ix - 7, iy + 6, ix + 7, iy + 12), fill=FILL, outline=INK, width=2)
    draw.rectangle((ix - 7, iy + 18, ix + 7, iy + 24), fill=FILL, outline=INK, width=2)
    text_center(draw, x + width / 2 - 10, y + 36 if sub else y + height / 2, "«component»", F["si"], LINE)
    text_center(draw, x + width / 2 - 10, y + 66, name, F["h"])
    if sub:
        text_center(draw, x + width / 2 - 10, y + 92, sub, F["tiny"], LINE)
    return rect


def component_diagram(path):
    image, draw = new_canvas("Component Diagram — DealScout modules")
    ui = component_box(draw, 50, 420, "Browser UI", "index.html · style.css · app.js", 290)
    server = component_box(draw, 450, 420, "server.js", "http.createServer · static files")
    api = component_box(draw, 790, 420, "api.js", "REST router (/api)")
    prod = component_box(draw, 1120, 150, "products.js", "search · normalize · best deal")
    auth = component_box(draw, 1120, 420, "auth.js", "login · cookie sessions")
    ana = component_box(draw, 1120, 690, "analytics.js", "summarize searches")
    store = component_box(draw, 1120, 880, "filestore.js", "readJson · appendJson", 260, 90)
    # required/provided interface (lollipop + socket) between UI and server
    draw.line((340, 475, 400, 475), fill=LINE, width=3)
    draw.ellipse((400, 460, 430, 490), fill=FILL, outline=LINE, width=3)
    draw.arc((405, 452, 455, 498), 120, 240, fill=LINE, width=3)
    draw.line((450, 475, 450, 475), fill=LINE, width=3)
    text_center(draw, 395, 530, "HTTP / JSON", F["si"], LINE)
    text_center(draw, 395, 552, "GET /api/products/search", F["tiny"], LINE)
    link(draw, server, api, head="open", label="routes /api/*")
    link(draw, api, prod, head="open", label="searchProducts()", label_offset=(-40, -16))
    link(draw, api, auth, head="open", label="login() · currentUser()")
    link(draw, api, ana, head="open", label="summarize()", label_offset=(-30, 16))
    for module in (prod, auth, ana):
        link(draw, module, store, dashed=True, head="open")
    text_center(draw, 1420, 850, "«use»", F["si"], LINE)
    # artifacts
    for index, (name, y) in enumerate([("products.json", 120), ("users.json", 300), ("searches.json", 480)]):
        rect = (1430, y, 1570, y + 90)
        draw.rectangle(rect, fill="#ECFDF5", outline=INK, width=2)
        draw.polygon([(1545, y), (1570, y + 25), (1545, y + 25)], fill=FILL, outline=INK)
        text_center(draw, 1500, y + 40, "«artifact»", F["tiny"], LINE)
        text_center(draw, 1500, y + 65, name, F["si"])
        link(draw, store, rect, dashed=True, head="open")
    text_center(draw, 1500, 600, "data/ folder (fs module)", F["tiny"], LINE)
    # optional external provider
    ext = (450, 120, 740, 230)
    dashed_line(draw, (450, 120), (740, 120)); dashed_line(draw, (740, 120), (740, 230)); dashed_line(draw, (740, 230), (450, 230)); dashed_line(draw, (450, 230), (450, 120))
    text_center(draw, 595, 150, "«external system»", F["si"], LINE)
    text_center(draw, 595, 180, "Shopping Provider API", F["h"])
    text_center(draw, 595, 208, "(optional, live mode, https module)", F["tiny"], LINE)
    link(draw, prod, ext, dashed=True, head="open", label="HTTPS (SERPAPI_KEY)", label_offset=(0, -22))
    draw.text((50, 940), "Notation: boxes with the component icon = modules; dashed arrows = dependencies; lollipop/socket = provided/required interface.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- deployment diagram
def node_box(draw, x, y, width, height, stereotype, name, depth=22):
    draw.polygon([(x, y), (x + depth, y - depth), (x + width + depth, y - depth), (x + width, y)], fill=SOFT, outline=INK)
    draw.polygon([(x + width, y), (x + width + depth, y - depth), (x + width + depth, y + height - depth), (x + width, y + height)], fill="#E5E7EB", outline=INK)
    draw.rectangle((x, y, x + width, y + height), fill=FILL, outline=INK, width=3)
    text_center(draw, x + width / 2, y + 24, stereotype, F["si"], LINE)
    text_center(draw, x + width / 2, y + 52, name, F["h"])
    return (x, y, x + width, y + height)


def artifact(draw, x, y, name, width=250):
    rect = (x, y, x + width, y + 52)
    draw.rectangle(rect, fill=FILL, outline=INK, width=2)
    draw.polygon([(x + width - 18, y), (x + width, y + 18), (x + width - 18, y + 18)], fill=SOFT, outline=INK)
    draw.text((x + 10, y + 15), "«artifact» " + name, fill=INK, font=F["s"])
    return rect


def deployment_diagram(path):
    image, draw = new_canvas("Deployment Diagram — single-machine or LAN deployment")
    client = node_box(draw, 70, 170, 480, 560, "«device»", "Client Computer / Smartphone")
    browser = node_box(draw, 110, 260, 400, 420, "«execution environment»", "Web Browser (Chrome / Firefox / Edge)", 14)
    for index, name in enumerate(["index.html · login.html", "style.css", "app.js · login.js · common.js"]):
        artifact(draw, 160, 350 + index * 80, name, 300)
    text_center(draw, 310, 640, "runs HTML, CSS and ES6+ JavaScript", F["tiny"], LINE)
    server = node_box(draw, 760, 170, 620, 560, "«device»", "Server (any laptop with Node.js)")
    node = node_box(draw, 800, 260, 540, 300, "«execution environment»", "Node.js runtime (v14+) — port 3000", 14)
    artifact(draw, 840, 350, "server.js", 220)
    artifact(draw, 1090, 350, "modules/*.js", 220)
    artifact(draw, 840, 430, "package.json (npm start)", 470)
    folder = (800, 600, 1340, 700)
    draw.rectangle(folder, fill="#ECFDF5", outline=INK, width=3)
    text_center(draw, 1070, 625, "«folder» data/", F["si"], LINE)
    text_center(draw, 1070, 660, "products.json · users.json · searches.json", F["s"])
    connector(draw, (1070, 560), (1070, 600), head="filled", label="fs.promises read / write", label_offset=(180, 0))
    # communication path
    draw.line((550, 450, 760, 450), fill=LINE, width=4)
    text_center(draw, 655, 420, "«HTTP»", F["si"], LINE)
    text_center(draw, 655, 480, "fetch() → JSON", F["tiny"], LINE)
    # cloud
    cloud = (1080, 800, 1500, 930)
    for cx, cy, r in [(1150, 870, 55), (1230, 840, 70), (1330, 845, 75), (1420, 875, 55), (1290, 890, 60)]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SOFT, outline=INK, width=2)
    draw.ellipse((1105, 830, 1470, 910), fill=SOFT)
    text_center(draw, 1290, 855, "«external» Shopping Provider API", F["si"])
    text_center(draw, 1290, 885, "(optional live mode)", F["tiny"], LINE)
    dashed_line(draw, (1070, 730), (1200, 815))
    text_center(draw, 1000, 790, "«HTTPS» only when", F["tiny"], LINE)
    text_center(draw, 1000, 812, "SERPAPI_KEY is set", F["tiny"], LINE)
    draw.text((70, 940), "Notation: 3-D boxes = nodes (devices / execution environments); artifacts = deployed files; lines = communication paths.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- use case diagram
def actor(draw, x, y, name):
    draw.ellipse((x - 22, y - 70, x + 22, y - 26), outline=INK, width=4)
    draw.line((x, y - 26, x, y + 40), fill=INK, width=4)
    draw.line((x - 40, y - 5, x + 40, y - 5), fill=INK, width=4)
    draw.line((x, y + 40, x - 35, y + 95), fill=INK, width=4)
    draw.line((x, y + 40, x + 35, y + 95), fill=INK, width=4)
    text_center(draw, x, y + 120, name, F["h"])
    return (x - 45, y - 70, x + 45, y + 130)


def use_case(draw, cx, cy, text, rx=150, ry=42):
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=FILL, outline=INK, width=3)
    text_center(draw, cx, cy, text, F["s"])
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def use_case_diagram(path):
    image, draw = new_canvas("Use Case Diagram — DealScout")
    boundary = (380, 110, 1220, 930)
    draw.rectangle(boundary, fill="#FAFAFA", outline=INK, width=3)
    text_center(draw, 800, 140, "DealScout Web Application", F["h"])
    guest = actor(draw, 160, 330, "Shopper (Guest)")
    member = actor(draw, 160, 720, "Signed-in Shopper")
    provider = actor(draw, 1440, 330, "Shopping Provider")
    text_center(draw, 1440, 480, "«external system»", F["tiny"], LINE)
    search = use_case(draw, 640, 230, "Search Product")
    select = use_case(draw, 980, 230, "Select Category & Mode")
    compare = use_case(draw, 640, 400, "View Comparison Table")
    best = use_case(draw, 980, 400, "View Best Deal")
    live = use_case(draw, 980, 560, "Fetch Live Prices")
    signin = use_case(draw, 640, 560, "Sign In")
    insights = use_case(draw, 640, 720, "View Insights")
    signout = use_case(draw, 980, 720, "Sign Out")
    download = use_case(draw, 800, 870, "Download Resources", 170)
    for target in (search, compare, signin, download):
        link(draw, guest, target, head=None)
    link(draw, guest, select, head=None)
    for target in (insights, signout):
        link(draw, member, target, head=None)
    link(draw, provider, live, head=None)
    link(draw, best, search, dashed=True, head="open", label="«include»", label_offset=(0, -20))
    link(draw, compare, search, dashed=True, head="open", label="«include»", label_offset=(-80, 0))
    link(draw, live, search, dashed=True, head="open", label="«extend»", label_offset=(80, 0))
    link(draw, insights, signin, dashed=True, head="open", label="«include»", label_offset=(-80, 0))
    # generalisation: signed-in shopper is a shopper
    connector(draw, (160, 590), (160, 470), head="open")
    draw.text((50, 940), "Notation: stick figures = actors, ovals = use cases, «include» / «extend» dashed arrows, hollow arrow = generalisation.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- activity diagram
def action(draw, cx, cy, text, width=300, height=64):
    rect = (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2)
    draw.rounded_rectangle(rect, radius=28, fill=FILL, outline=INK, width=3)
    lines = text.split("\n")
    for index, line in enumerate(lines):
        text_center(draw, cx, cy + (index - (len(lines) - 1) / 2) * 22, line, F["s"])
    return rect


def decision(draw, cx, cy, text, size=48):
    draw.polygon([(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)], fill=FILL, outline=INK, width=3)
    text_center(draw, cx, cy - size - 20, text, F["si"])
    return (cx - size, cy - size, cx + size, cy + size)


def activity_diagram(path):
    image, draw = new_canvas("Activity Diagram — product comparison workflow (swimlanes)")
    draw.line((800, 90, 800, 930), fill=LINE, width=2)
    draw.rectangle((40, 90, 1560, 130), fill=SOFT, outline=LINE)
    text_center(draw, 420, 110, "Browser (HTML / CSS / JavaScript)", F["h"])
    text_center(draw, 1180, 110, "Node.js Server (server.js + modules)", F["h"])
    # browser lane
    draw.ellipse((405, 150, 435, 180), fill=INK)
    a1 = action(draw, 420, 240, "Enter product name,\nchoose category & mode", 330)
    d1 = decision(draw, 420, 360, "query length ≥ 2 ?")
    err = action(draw, 150, 360, "Show validation\nmessage", 200)
    a2 = action(draw, 420, 470, "fetch('/api/products/search')")
    a3 = action(draw, 420, 760, "Render best-deal card\nand comparison table", 330)
    draw.ellipse((400, 860, 440, 900), outline=INK, width=4)
    draw.ellipse((410, 870, 430, 890), fill=INK)
    connector(draw, (420, 180), (420, 208))
    connector(draw, (420, 272), (420, 312))
    connector(draw, (372, 360), (250, 360), label="[no]", label_offset=(0, -20))
    connector(draw, (150, 328), (150, 240), head=None); connector(draw, (150, 240), (255, 240))
    connector(draw, (420, 408), (420, 438), label="[yes]", label_offset=(50, 0))
    connector(draw, (420, 792), (420, 860))
    # server lane
    s1 = action(draw, 1180, 240, "Validate q, category, mode", 320)
    d2 = decision(draw, 1180, 360, "mode = live ?")
    s_live = action(draw, 1420, 470, "Call provider or\nbuild preview", 240)
    s_demo = action(draw, 960, 470, "Filter products.json\n(matches)", 260)
    s3 = action(draw, 1180, 580, "Normalize offers → ProductOffer[]", 360)
    s4 = action(draw, 1180, 670, "reduce() → minimum price", 320)
    s5 = action(draw, 1180, 760, "appendJson('searches.json')", 340)
    s6 = action(draw, 1180, 850, "Respond 200 JSON (SearchResponse)", 380)
    connector(draw, (585, 470), (800, 470), head=None); connector(draw, (800, 470), (800, 200), head=None); connector(draw, (800, 200), (1020, 200), head=None); connector(draw, (1020, 200), (1020, 240), head=None)
    draw.line((1020, 240, 1020, 240), fill=LINE)
    connector(draw, (1180, 272), (1180, 312))
    connector(draw, (1228, 360), (1420, 360), head=None); connector(draw, (1420, 360), (1420, 438), label="[yes]", label_offset=(40, 0))
    connector(draw, (1132, 360), (960, 360), head=None); connector(draw, (960, 360), (960, 438), label="[no]", label_offset=(-40, 0))
    connector(draw, (1420, 502), (1420, 548), head=None); connector(draw, (1420, 548), (1180, 548), head=None)
    connector(draw, (960, 502), (960, 548), head=None); connector(draw, (960, 548), (1180, 548), head=None); connector(draw, (1180, 548), (1180, 548))
    draw.line((1000, 548, 1360, 548), fill=INK, width=8)  # merge bar
    connector(draw, (1180, 612), (1180, 638))
    connector(draw, (1180, 702), (1180, 728))
    connector(draw, (1180, 792), (1180, 818))
    connector(draw, (990, 850), (800, 850), head=None); connector(draw, (800, 850), (800, 650), head=None); connector(draw, (800, 650), (600, 650), head=None); connector(draw, (600, 650), (600, 760), head=None); connector(draw, (600, 760), (585, 760))
    draw.text((50, 940), "Notation: filled circle = start, bullseye = end, rounded boxes = actions, diamonds = decisions, thick bar = merge/join, lanes = who performs the step.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- sequence diagram
def sequence_diagram(path):
    image, draw = new_canvas("Sequence Diagram — Compare prices request")
    lifelines = [("Shopper", 130, True), ("Browser\napp.js", 420, False), ("server.js /\napi.js", 720, False), ("products.js", 1020, False), ("filestore.js\n(JSON files)", 1330, False)]
    xs = {}
    for name, x, is_actor in lifelines:
        xs[name.split("\n")[0]] = x
        if is_actor:
            actor(draw, x, 150, "")
            text_center(draw, x, 265, name, F["h"])
        else:
            draw.rectangle((x - 110, 100, x + 110, 170), fill=SOFT, outline=INK, width=3)
            for index, line in enumerate(name.split("\n")):
                text_center(draw, x, 135 + (index - (len(name.split("\n")) - 1) / 2) * 24, line, F["h"])
        dashed_line(draw, (x, 290 if is_actor else 170), (x, 900), dash=10, width=2)
    # activation bars
    for x, y1, y2 in [(420, 330, 860), (720, 400, 790), (1020, 440, 740), (1330, 470, 520), (1330, 650, 700)]:
        draw.rectangle((x - 10, y1, x + 10, y2), fill="#D1FAE5", outline=INK, width=2)
    messages = [
        (130, 420, 330, "1. type query, click Compare", False),
        (420, 720, 400, "2. GET /api/products/search?q=&category=&mode=", False),
        (720, 1020, 440, "3. searchProducts(q, category, mode)", False),
        (1020, 1330, 470, "4. readJson('products.json')", False),
        (1330, 1020, 520, "5. catalog rows", True),
        (1020, 1020, 580, "6. matches() → normalizeOffer() → reduce(min)", False),
        (1020, 1330, 650, "7. appendJson('searches.json', log)", False),
        (1330, 1020, 700, "8. saved", True),
        (1020, 720, 740, "9. { results, best_deal_id, notice }", True),
        (720, 420, 790, "10. 200 OK  application/json", True),
        (420, 420, 830, "11. renderResults() → best-deal card + table", False),
        (420, 130, 860, "12. comparison shown", True),
    ]
    for x1, x2, y, label, is_return in messages:
        if x1 == x2:  # self message
            draw.line((x1 + 10, y, x1 + 60, y, x1 + 60, y + 30, x1 + 10, y + 30), fill=LINE, width=3)
            arrow_head(draw, (x1 + 60, y + 30), (x1 + 12, y + 30))
            draw.text((x1 + 70, y - 2), label, fill=INK, font=F["si"])
            continue
        start = (x1 + (10 if x2 > x1 else -10), y)
        end = (x2 - (10 if x2 > x1 else -10), y)
        if is_return:
            dashed_line(draw, start, end, dash=10)
            arrow_head(draw, start, end, filled=False)
        else:
            draw.line((*start, *end), fill=LINE, width=3)
            arrow_head(draw, start, end)
        text_center(draw, (x1 + x2) / 2, y - 16, label, F["si"])
    draw.text((50, 940), "Notation: boxes = participants, dashed vertical lines = lifelines, green bars = activations, solid arrows = calls, dashed arrows = returns.", fill=LINE, font=F["tiny"])
    image.save(path)


# --------------------------------------------------------------------------- ER diagram (Chen)
def entity(draw, cx, cy, name, width=230, height=74):
    rect = (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2)
    draw.rectangle(rect, fill=SOFT, outline=INK, width=3)
    text_center(draw, cx, cy, name, F["h"])
    return rect


def attribute(draw, cx, cy, name, owner, key=False):
    rx, ry = max(60, int(draw.textlength(name, font=F["si"]) / 2 + 18)), 26
    draw.line((cx, cy, *edge_point(owner, (cx, cy))), fill=LINE, width=2)
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=FILL, outline=INK, width=2)
    text_center(draw, cx, cy, name, F["si"], underline=key)


def relationship(draw, cx, cy, name, a, b, card_a, card_b):
    size = 54
    diamond = (cx - size, cy - size, cx + size, cy + size)
    link(draw, a, diamond, head=None)
    link(draw, diamond, b, head=None)
    draw.polygon([(cx, cy - size), (cx + size + 20, cy), (cx, cy + size), (cx - size - 20, cy)], fill=FILL, outline=INK, width=3)
    text_center(draw, cx, cy, name, F["si"])
    for rect, card in ((a, card_a), (b, card_b)):
        px, py = edge_point(rect, (cx, cy))
        horizontal = abs(cx - px) > abs(cy - py)
        text_center(draw, px + (cx - px) * 0.25 + (0 if horizontal else 26), py + (cy - py) * 0.25 + (-22 if horizontal else 0), card, F["h"])


def er_diagram(path):
    image, draw = new_canvas("Entity Relationship Diagram — DealScout data (JSON files)")
    user = entity(draw, 230, 520, "USER")
    log = entity(draw, 760, 520, "SEARCH_LOG")
    offer = entity(draw, 1320, 520, "PRODUCT_OFFER", 250)
    store = entity(draw, 1320, 860, "STORE", 200)
    for cx, cy, name, key in [(90, 330, "id", True), (200, 250, "name", False), (330, 250, "email", False), (400, 350, "role", False)]:
        attribute(draw, cx, cy, name, user, key)
    for cx, cy, name, key in [(560, 320, "id", True), (640, 230, "query", False), (770, 200, "category", False), (900, 230, "mode", False), (980, 330, "result_count", False), (640, 400, "best_price", False), (900, 410, "searched_at", False)]:
        attribute(draw, cx, cy, name, log, key)
    for cx, cy, name, key in [(1110, 330, "id", True), (1180, 240, "product_name", False), (1330, 200, "price", False), (1470, 240, "rating", False), (1530, 340, "discount", False), (1470, 410, "delivery", False), (1140, 420, "seller", False)]:
        attribute(draw, cx, cy, name, offer, key)
    attribute(draw, 1080, 860, "name", store, True)
    attribute(draw, 1540, 860, "product_url", store, False)
    relationship(draw, 495, 520, "performs", user, log, "1", "M")
    relationship(draw, 1040, 520, "returns", log, offer, "1", "M")
    relationship(draw, 1320, 690, "lists", store, offer, "1", "M")
    draw.text((50, 940), "Chen notation: rectangles = entities (JSON files), ellipses = attributes (underlined = key), diamonds = relationships with cardinality.", fill=LINE, font=F["tiny"])
    image.save(path)


def build_all(folder: Path) -> dict[str, str]:
    folder.mkdir(parents=True, exist_ok=True)
    builders = {"er": er_diagram, "class": class_diagram, "object": object_diagram, "component": component_diagram, "deployment": deployment_diagram, "usecase": use_case_diagram, "activity": activity_diagram, "sequence": sequence_diagram}
    paths = {}
    for key, builder in builders.items():
        path = folder / f"{key}-diagram.png"
        builder(str(path))
        paths[key] = str(path)
    return paths


if __name__ == "__main__":
    out = build_all(Path(__file__).resolve().parents[1] / "dealscout" / "public" / "downloads" / "report-assets")
    print("\n".join(out.values()))
