// Insights computed from data/searches.json (array methods: filter, map, reduce, sort).
const { readJson } = require("./filestore");

function countBy(items) {
  const counts = new Map();
  items.forEach((item) => counts.set(item, (counts.get(item) || 0) + 1));
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
}

async function summarize() {
  const logs = (await readJson("searches.json", [])).slice(0, 100);
  const queryCounts = countBy(logs.map((log) => log.query.toLowerCase()));
  const sourceCounts = countBy(logs.flatMap((log) => log.sources || []));
  const totalResults = logs.reduce((sum, log) => sum + log.result_count, 0);
  return {
    total_searches: logs.length,
    unique_queries: queryCounts.length,
    average_results: logs.length ? Math.round((totalResults / logs.length) * 10) / 10 : 0,
    top_query: queryCounts.length ? queryCounts[0][0] : null,
    source_counts: sourceCounts.map(([source, count]) => ({ source, count })),
    recent_searches: logs.slice(0, 8).map(({ sources, ...log }) => log),
  };
}

module.exports = { summarize };
