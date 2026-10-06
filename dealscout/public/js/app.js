// DealScout home page logic: search, comparison table, best deal, insights.

const state = {
  mode: "demo",
  section: "compare",
  user: null,
  result: null,
  searching: false,
};

const $ = (selector) => document.querySelector(selector);
const slug = (text) => text.toLowerCase().replaceAll(" ", "-");

/* ---------- Header / navigation ---------- */

function renderHeader() {
  const actions = $("#header-actions");
  if (state.user) {
    actions.innerHTML = `<span class="user-chip" data-testid="user-profile"><span class="user-avatar">${ICONS.user}</span>${escapeHtml(state.user.name)}</span>
      <button class="btn btn-outline btn-sm" id="logout-button" data-testid="header-logout-button">Sign out</button>`;
    $("#logout-button").addEventListener("click", async () => {
      await api("/auth/logout", { method: "POST" });
      state.user = null;
      renderHeader();
      if (state.section === "insights") renderInsights();
    });
  } else {
    actions.innerHTML = `<a href="/login" class="btn btn-outline" data-testid="header-login-link">${ICONS.user} Sign in</a>`;
  }
}

function showSection(section) {
  state.section = section;
  $("#compare-section").classList.toggle("hidden", section !== "compare");
  $("#insights-section").classList.toggle("hidden", section !== "insights");
  $("#nav-compare").classList.toggle("active", section === "compare");
  $("#nav-insights").classList.toggle("active", section === "insights");
  $("#mobile-nav").classList.add("hidden");
  if (section === "insights") renderInsights();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ---------- Search & results ---------- */

function modeLabel(mode, mocked) {
  if (mode === "live" && mocked) return "LIVE PREVIEW";
  return mode === "live" ? "LIVE PRICES" : "SAMPLE CATALOG";
}

function offerRow(offer, bestId) {
  const isBest = offer.id === bestId;
  return `<tr class="${isBest ? "best-row" : ""}" data-testid="comparison-row-${offer.id}">
    <td><div class="store-cell"><span class="store-initial">${escapeHtml(offer.source.slice(0, 1))}</span><div><div class="store-name">${escapeHtml(offer.source)}</div><div class="store-seller">${escapeHtml(offer.seller)}</div></div>${isBest ? '<span class="badge badge-green">Best</span>' : ""}</div></td>
    <td><div class="price-main">${money(offer.price)}</div>${offer.original_price ? `<div class="price-old">${money(offer.original_price)}</div>` : ""}</td>
    <td><span class="inline">${ICONS.star}${offer.rating ?? "—"}</span></td>
    <td><span class="inline">${ICONS.clock}${escapeHtml(offer.delivery || "Check store")}</span></td>
    <td>${offer.discount ? `<span class="discount">-${offer.discount}%</span>` : "—"}</td>
    <td class="text-right">${offer.product_url
      ? `<a class="btn btn-outline btn-sm" href="${escapeHtml(offer.product_url)}" target="_blank" rel="noopener noreferrer" data-testid="offer-view-button-${offer.id}">${ICONS.external} Open store</a>`
      : `<button class="btn btn-outline btn-sm" disabled data-testid="offer-view-button-${offer.id}">${ICONS.external} Unavailable</button>`}</td>
  </tr>`;
}

function renderResults() {
  const result = state.result;
  const section = $("#results-section");
  $("#empty-state").classList.toggle("hidden", Boolean(result));
  section.classList.toggle("hidden", !result);
  if (!result) return;

  const best = result.results.find((offer) => offer.id === result.best_deal_id);
  const mocked = result.results.some((offer) => offer.is_mocked);

  section.innerHTML = `
    <div class="results-head rise">
      <div>
        <p class="eyebrow">Results for “${escapeHtml(result.query)}”</p>
        <h2 data-testid="results-title">Your best options, side by side</h2>
        <div class="results-meta"><span data-testid="results-count">${result.results.length} offers found</span><span>·</span><span class="badge badge-outline" data-testid="results-mode-badge">${modeLabel(result.mode, mocked)}</span></div>
      </div>
      <div class="retrieval-note" data-testid="retrieval-note">${ICONS.shield} Prices checked just now</div>
    </div>
    ${result.notice.includes("MOCKED") ? `<div class="notice notice-warn rise" data-testid="mocked-live-notice"><strong>Preview prices:</strong> Live retailer access is not connected yet. These preview results show how live comparison works; use Sample prices for the verified local catalog.</div>` : ""}
    ${best ? `<div class="card best-card rise" data-testid="best-deal-card"><div class="card-body">
        <div>
          <div class="best-tags"><span class="badge badge-green">${ICONS.trendDown} Best price</span>${best.discount ? `<span class="best-save">SAVE ${best.discount}%</span>` : ""}</div>
          <h3 data-testid="best-deal-product">${escapeHtml(best.product_name)}</h3>
          <p class="best-seller" data-testid="best-deal-seller">${escapeHtml(best.source)} · ${escapeHtml(best.seller)} · ${escapeHtml(best.delivery || "Check store")}</p>
        </div>
        <div class="best-right"><p class="best-price" data-testid="best-deal-price">${money(best.price)}</p><p class="best-price-note">Lowest price in this comparison</p></div>
      </div></div>` : ""}
    ${result.results.length ? `<div class="card rise" data-testid="comparison-table-card">
        <div class="card-header"><div class="table-head-row"><div><p class="eyebrow">Price comparison</p><h3 class="card-title">All available offers</h3></div><span class="badge badge-outline">${result.results.length} offers</span></div></div>
        <div class="table-wrap"><table data-testid="comparison-table"><thead><tr><th>Store</th><th>Price</th><th>Rating</th><th>Delivery</th><th>Discount</th><th class="text-right">Details</th></tr></thead>
        <tbody>${result.results.map((offer) => offerRow(offer, result.best_deal_id)).join("")}</tbody></table></div>
      </div>` : `<div class="card rise" data-testid="no-results-card"><div class="card-body no-results">${ICONS.fileSearch}<h3>No matching offers</h3><p>Try a shorter product name such as “iPhone”, “MacBook”, or “earbuds”.</p></div></div>`}
  `;
}

async function runSearch(query) {
  if (state.searching) return;
  const category = $("#category-select").value;
  state.searching = true;
  $("#search-submit").disabled = true;
  $("#search-submit-label").textContent = "Finding offers…";
  $("#search-error").classList.add("hidden");
  try {
    const params = new URLSearchParams({ q: query, category, mode: state.mode });
    state.result = await api(`/products/search?${params.toString()}`);
    renderResults();
  } catch (error) {
    console.warn("Search failed:", error.message);
    $("#search-error").classList.remove("hidden");
  } finally {
    state.searching = false;
    $("#search-submit").disabled = false;
    $("#search-submit-label").textContent = "Compare prices";
  }
}

/* ---------- Insights ---------- */

async function renderInsights() {
  const panel = $("#insights-panel");
  if (!state.user) {
    panel.innerHTML = `<div class="card login-required" data-testid="data-login-required-card"><div class="card-body">
      <div class="feature-icon">${ICONS.history}</div>
      <h2>Your searches, neatly organized</h2>
      <p>Sign in to review recent comparisons, frequently searched products, and the stores that appeared most often.</p>
      <a href="/login" class="btn btn-dark" data-testid="data-login-link">Sign in to continue ${ICONS.arrowRight}</a>
    </div></div>`;
    return;
  }
  panel.innerHTML = `<div class="state-box" data-testid="data-loading-state">Loading your insights…</div>`;
  try {
    const summary = await api("/analytics");
    const rows = summary.recent_searches.length
      ? summary.recent_searches.map((item) => `<tr data-testid="collected-search-row-${item.id}"><td class="store-name">${escapeHtml(item.query)}</td><td><span class="badge badge-outline">${item.mode === "demo" ? "sample" : "live"}</span></td><td>${item.result_count}</td><td>${item.best_price ? money(item.best_price) : "—"}</td></tr>`).join("")
      : `<tr><td colspan="4" class="empty-row">Start comparing to build your history.</td></tr>`;
    const sources = summary.source_counts.length
      ? summary.source_counts.map((source) => `<div class="source-row" data-testid="source-count-${slug(source.source)}"><span>${escapeHtml(source.source)}</span><span>${source.count}</span></div>`).join("")
      : `<p class="muted" style="font-size:.875rem">No store data yet.</p>`;
    panel.innerHTML = `<div class="rise" data-testid="collected-data-panel">
      <div class="stat-grid">
        <div class="card stat-card" data-testid="data-total-searches-card"><div class="card-body"><p class="stat-label">Comparisons</p><p class="stat-value">${summary.total_searches}</p></div></div>
        <div class="card stat-card" data-testid="data-unique-queries-card"><div class="card-body"><p class="stat-label">Unique searches</p><p class="stat-value">${summary.unique_queries}</p></div></div>
        <div class="card stat-card" data-testid="data-top-query-card"><div class="card-body"><p class="stat-label">Most searched</p><p class="stat-value small">${escapeHtml(summary.top_query ?? "Nothing yet")}</p></div></div>
      </div>
      <div class="insights-grid">
        <div class="card" data-testid="recent-searches-card"><div class="card-header"><h3 class="card-title">Recent comparisons</h3></div><div class="table-wrap"><table data-testid="collected-data-table"><thead><tr><th>Product</th><th>Source</th><th>Offers</th><th>Best price</th></tr></thead><tbody>${rows}</tbody></table></div></div>
        <div class="card" data-testid="source-counts-card"><div class="card-header"><h3 class="card-title">Store activity</h3></div><div class="card-body source-list">${sources}</div></div>
      </div>
    </div>`;
  } catch (error) {
    console.warn("Insights failed:", error.message);
    panel.innerHTML = `<div class="state-box error" data-testid="data-error-state">Your insights could not be loaded. Please sign in again.</div>`;
  }
}

/* ---------- Wire up events ---------- */

document.addEventListener("DOMContentLoaded", async () => {
  $("#search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const query = $("#search-input").value.trim();
    if (query.length >= 2) runSearch(query);
  });

  document.querySelectorAll(".mode-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      document.querySelectorAll(".mode-button").forEach((item) => item.classList.toggle("active", item === button));
    });
  });

  document.querySelectorAll(".chip[data-example]").forEach((chip) => {
    chip.addEventListener("click", () => {
      $("#search-input").value = chip.dataset.example;
      showSection("compare");
      runSearch(chip.dataset.example);
    });
  });

  $("#nav-compare").addEventListener("click", () => showSection("compare"));
  $("#nav-insights").addEventListener("click", () => showSection("insights"));
  $("#mobile-nav-compare").addEventListener("click", () => showSection("compare"));
  $("#mobile-nav-insights").addEventListener("click", () => showSection("insights"));
  $("#back-to-compare").addEventListener("click", () => showSection("compare"));
  $("#menu-button").addEventListener("click", () => $("#mobile-nav").classList.toggle("hidden"));

  // Who is signed in? (null when nobody)
  try { state.user = await api("/auth/me"); } catch { state.user = null; }
  renderHeader();

  // Allow /#insights deep link (used after login)
  if (window.location.hash === "#insights") showSection("insights");
});
