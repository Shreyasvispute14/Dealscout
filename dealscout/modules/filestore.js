// File handling with Node.js (fs module) — JSON files act as the project's data store.
const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");

function dataPath(fileName) {
  return path.join(DATA_DIR, fileName);
}

// Read a JSON file and parse it. Returns `fallback` when the file does not exist yet.
async function readJson(fileName, fallback = []) {
  try {
    const text = await fs.promises.readFile(dataPath(fileName), "utf-8");
    return JSON.parse(text);
  } catch (error) {
    if (error.code === "ENOENT") return fallback;
    throw error;
  }
}

// Serialize and write a JSON file (pretty-printed so it stays human readable).
async function writeJson(fileName, data) {
  await fs.promises.mkdir(DATA_DIR, { recursive: true });
  await fs.promises.writeFile(dataPath(fileName), JSON.stringify(data, null, 2), "utf-8");
}

// Append one record to a JSON array file. Writes happen one after another to avoid clashes.
let writeQueue = Promise.resolve();
function appendJson(fileName, record, limit = 500) {
  writeQueue = writeQueue.then(async () => {
    const items = await readJson(fileName, []);
    items.unshift(record); // newest first
    await writeJson(fileName, items.slice(0, limit));
  });
  return writeQueue;
}

module.exports = { readJson, writeJson, appendJson };
