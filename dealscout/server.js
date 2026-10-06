// DealScout — Node.js HTTP server
// Technologies: HTML, CSS, JavaScript (ES6+), Node.js core modules (http, fs, path, url)
// as covered in SPPU T.Y.B.Sc. (CS) Semester V, CS-303-MJ-T Web Technology-I.
// No third-party npm packages are required. Start with:  node server.js

const http = require("http");
const path = require("path");
const fs = require("fs");
const { handleApi } = require("./modules/api");

const HOST = process.env.HOST || "0.0.0.0";
const PORT = Number(process.env.PORT) || 3000;
const PUBLIC_DIR = path.join(__dirname, "public");

// MIME types for the static files served from /public
const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".pdf": "application/pdf",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
};

// Clean URLs: /login -> login.html, /resources -> resources.html
const PAGE_ROUTES = { "/": "index.html", "/login": "login.html", "/resources": "resources.html", "/docs": "resources.html" };

async function serveStatic(req, res, pathname) {
  const relative = PAGE_ROUTES[pathname] || decodeURIComponent(pathname);
  const filePath = path.normalize(path.join(PUBLIC_DIR, relative));

  // Prevent directory traversal (../) outside the public folder
  if (!filePath.startsWith(PUBLIC_DIR)) {
    return sendText(res, 403, "Forbidden");
  }

  try {
    const stat = await fs.promises.stat(filePath);
    if (stat.isDirectory()) return serveStatic(req, res, path.posix.join(pathname, "index.html"));
    const extension = path.extname(filePath).toLowerCase();
    res.writeHead(200, {
      "Content-Type": MIME_TYPES[extension] || "application/octet-stream",
      "Content-Length": stat.size,
      "Cache-Control": extension === ".html" ? "no-cache" : "public, max-age=3600",
    });
    if (req.method === "HEAD") return res.end();
    fs.createReadStream(filePath).pipe(res);
  } catch (error) {
    if (error.code === "ENOENT") {
      return serveNotFound(res);
    }
    console.error("Static file error:", error);
    sendText(res, 500, "Internal Server Error");
  }
}

function sendText(res, status, text) {
  res.writeHead(status, { "Content-Type": "text/plain; charset=utf-8" });
  res.end(text);
}

async function serveNotFound(res) {
  try {
    const page = await fs.promises.readFile(path.join(PUBLIC_DIR, "404.html"));
    res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
    res.end(page);
  } catch {
    sendText(res, 404, "Not Found");
  }
}

const server = http.createServer(async (req, res) => {
  const requestUrl = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const pathname = requestUrl.pathname;

  try {
    if (pathname === "/api" || pathname.startsWith("/api/")) {
      await handleApi(req, res, requestUrl);
    } else {
      await serveStatic(req, res, pathname);
    }
  } catch (error) {
    console.error(`Unhandled error for ${req.method} ${pathname}:`, error);
    if (!res.headersSent) {
      res.writeHead(500, { "Content-Type": "application/json; charset=utf-8" });
    }
    res.end(JSON.stringify({ detail: "Internal server error" }));
  }
});

server.listen(PORT, HOST, () => {
  console.log(`DealScout is running at http://localhost:${PORT}`);
  console.log("Press Ctrl+C to stop the server.");
});
