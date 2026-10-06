// Simple REST API router. Every route lives under /api and exchanges JSON.
const { searchProducts } = require("./products");
const auth = require("./auth");
const { summarize } = require("./analytics");

function sendJson(res, status, data, extraHeaders = {}) {
  const body = JSON.stringify(data);
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Content-Length": Buffer.byteLength(body), ...extraHeaders });
  res.end(body);
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 10_000) { reject(new Error("Body too large")); req.destroy(); }
    });
    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch { reject(new Error("Invalid JSON body")); }
    });
    req.on("error", reject);
  });
}

async function handleApi(req, res, url) {
  const route = `${req.method} ${url.pathname.replace(/\/$/, "") || "/api"}`;

  switch (route) {
    case "GET /api":
      return sendJson(res, 200, { message: "DealScout API", ok: true });

    case "GET /api/products/search": {
      const query = (url.searchParams.get("q") || "").trim();
      const category = url.searchParams.get("category") || "All";
      const mode = url.searchParams.get("mode") === "live" ? "live" : "demo";
      if (query.length < 2 || query.length > 80) {
        return sendJson(res, 400, { detail: "Query must be between 2 and 80 characters" });
      }
      if (!["All", "Mobiles", "Laptops", "General"].includes(category)) {
        return sendJson(res, 400, { detail: "Unknown category" });
      }
      return sendJson(res, 200, await searchProducts(query, category, mode));
    }

    case "POST /api/auth/login": {
      let body;
      try { body = await readJsonBody(req); } catch (error) { return sendJson(res, 400, { detail: error.message }); }
      const session = await auth.login(body.email, body.password);
      if (!session) return sendJson(res, 401, { detail: "Use the demo credentials shown on the login page" });
      return sendJson(res, 200, { user: session.user, message: "Welcome back" }, { "Set-Cookie": auth.sessionCookie(session.token) });
    }

    case "GET /api/auth/me":
      return sendJson(res, 200, auth.currentUser(req));

    case "POST /api/auth/logout":
      auth.logout(req);
      return sendJson(res, 200, { message: "Logged out" }, { "Set-Cookie": auth.clearCookie() });

    case "GET /api/analytics": {
      if (!auth.currentUser(req)) return sendJson(res, 401, { detail: "Login required to view collected data" });
      return sendJson(res, 200, await summarize());
    }

    default:
      return sendJson(res, 404, { detail: `No API route for ${route}` });
  }
}

module.exports = { handleApi };
