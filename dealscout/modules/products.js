// Product search, normalization and best-deal selection.
const https = require("https");
const crypto = require("crypto");
const { readJson, appendJson } = require("./filestore");

let catalogCache = null;

// Load products.json once and convert every row into a normalized ProductOffer object.
async function loadCatalog() {
  if (catalogCache) return catalogCache;
  const rows = await readJson("products.json", []);
  catalogCache = rows.map((row, index) => normalizeOffer({ ...row, id: `offer-${index + 1}`, mode: "demo" }));
  return catalogCache;
}

// Every source (sample catalog or live provider) is converted to this one structure.
function normalizeOffer(raw) {
  const price = Number(raw.price);
  const original = raw.original_price ? Number(raw.original_price) : null;
  const discount = original && original > price ? Math.round((1 - price / original) * 100) : null;
  return {
    id: raw.id || crypto.randomUUID(),
    product_name: raw.product_name,
    category: raw.category || "General",
    source: raw.source,
    seller: raw.seller || raw.source,
    price,
    original_price: original,
    currency: "INR",
    rating: raw.rating ?? null,
    delivery: raw.delivery || null,
    discount,
    product_url: raw.product_url || null,
    mode: raw.mode || "demo",
    is_live: Boolean(raw.is_live),
    is_mocked: Boolean(raw.is_mocked),
    retrieved_at: new Date().toISOString(),
  };
}

// A product matches when every word of the query appears in "name + category".
function matches(offer, query, category) {
  const haystack = `${offer.product_name} ${offer.category}`.toLowerCase();
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  const categoryOk = category === "All" || offer.category === category;
  return categoryOk && words.every((word) => haystack.includes(word));
}

// Used when Live mode is selected but no provider key is configured.
function livePreview(catalog, query, category) {
  return catalog
    .filter((offer, index) => matches(offer, query, category) && index % 3 !== 0)
    .map((offer, index) => normalizeOffer({
      ...offer,
      id: `live-${index + 1}-${crypto.randomUUID()}`,
      source: `Live Preview · ${offer.source}`,
      seller: `${offer.seller} (preview)`,
      price: Math.round(offer.price * (0.98 + (index % 4) * 0.01)),
      mode: "live",
      is_live: false,
      is_mocked: true,
    }));
}

// Optional live provider (SerpApi Google Shopping) using the core https module.
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, { timeout: 8000 }, (response) => {
      let body = "";
      response.on("data", (chunk) => { body += chunk; });
      response.on("end", () => {
        try { resolve(JSON.parse(body)); } catch (error) { reject(error); }
      });
    });
    request.on("timeout", () => request.destroy(new Error("Provider timeout")));
    request.on("error", reject);
  });
}

async function liveProviderSearch(query, category) {
  const key = process.env.SERPAPI_KEY;
  if (!key) return [];
  const params = new URLSearchParams({ engine: "google_shopping", q: query, api_key: key, num: "10", hl: "en", gl: "in" });
  const data = await fetchJson(`https://serpapi.com/search?${params.toString()}`);
  return (data.shopping_results || [])
    .map((item, index) => {
      const digits = String(item.price || "").replace(/[^0-9.]/g, "");
      if (!digits) return null;
      return normalizeOffer({
        id: `live-${index}-${crypto.randomUUID()}`,
        product_name: item.title || query,
        category: category === "All" ? "General" : category,
        source: item.source || "Live provider",
        seller: item.source || "Online seller",
        price: Number(digits),
        rating: item.rating ?? null,
        delivery: item.delivery || "Check seller",
        product_url: item.link || null,
        mode: "live",
        is_live: true,
      });
    })
    .filter(Boolean);
}

// Main search: filter -> normalize -> find minimum price -> save a search log -> respond.
async function searchProducts(query, category, mode) {
  const catalog = await loadCatalog();
  let results = catalog.filter((offer) => matches(offer, query, category)).map((offer) => normalizeOffer({ ...offer }));
  let notice = "Demo catalog results collected from the local project dataset.";
  const providerAvailable = Boolean(process.env.SERPAPI_KEY);

  if (mode === "live") {
    let liveResults = [];
    try { liveResults = await liveProviderSearch(query, category); } catch (error) { console.error("Live provider failed:", error.message); }
    if (liveResults.length) {
      results = liveResults;
      notice = "Live results returned by the configured shopping provider.";
    } else {
      results = livePreview(catalog, query, category);
      notice = "LIVE PREVIEW is MOCKED because no shopping provider key is configured.";
    }
  }

  // Best deal = the offer with the lowest numeric price.
  const best = results.reduce((lowest, offer) => (lowest === null || offer.price < lowest.price ? offer : lowest), null);

  await appendJson("searches.json", {
    id: crypto.randomUUID(),
    query,
    category,
    mode,
    result_count: results.length,
    best_price: best ? best.price : null,
    searched_at: new Date().toISOString(),
    sources: results.map((offer) => offer.source),
  });

  return {
    query,
    category,
    mode,
    results,
    best_deal_id: best ? best.id : null,
    live_provider_available: providerAvailable,
    notice,
  };
}

module.exports = { searchProducts };
