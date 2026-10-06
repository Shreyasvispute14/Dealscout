// Demo login with an HTTP-only cookie session. Users are stored in data/users.json.
const crypto = require("crypto");
const { readJson } = require("./filestore");

const SESSION_COOKIE = "dealscout_session";
const SESSION_HOURS = 8;
const sessions = new Map(); // token -> { user, expires }

function parseCookies(req) {
  const header = req.headers.cookie || "";
  return Object.fromEntries(
    header.split(";").map((part) => part.trim()).filter(Boolean).map((part) => {
      const index = part.indexOf("=");
      return [part.slice(0, index), decodeURIComponent(part.slice(index + 1))];
    }),
  );
}

function publicUser(user) {
  return { id: user.id, name: user.name, email: user.email, role: user.role || "student" };
}

async function login(email, password) {
  const users = await readJson("users.json", []);
  const user = users.find((item) => item.email.toLowerCase() === String(email || "").trim().toLowerCase());
  if (!user || user.password !== password) return null;
  const token = crypto.randomBytes(24).toString("base64url");
  sessions.set(token, { user: publicUser(user), expires: Date.now() + SESSION_HOURS * 3600 * 1000 });
  return { token, user: publicUser(user) };
}

function currentUser(req) {
  const token = parseCookies(req)[SESSION_COOKIE];
  const session = sessions.get(token);
  if (!session) return null;
  if (session.expires < Date.now()) { sessions.delete(token); return null; }
  return session.user;
}

function logout(req) {
  const token = parseCookies(req)[SESSION_COOKIE];
  if (token) sessions.delete(token);
}

function sessionCookie(token) {
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${SESSION_HOURS * 3600}`;
}

function clearCookie() {
  return `${SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`;
}

module.exports = { login, currentUser, logout, sessionCookie, clearCookie };
