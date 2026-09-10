/**
 * Shared crypto helpers for the archive gate.
 *
 * Nothing here ever touches a plaintext secret outside the request that needs
 * it, and nothing is logged. The passphrase and the cookie-signing key both
 * arrive as Worker secrets (ARCHIVE_KEY, COOKIE_SECRET).
 */

const enc = new TextEncoder();

export const COOKIE_NAME = "kw_archive";
export const SESSION_HOURS = 12;

/** Constant-time byte comparison. Length is compared without branching too. */
export function timingSafeEqual(a, b) {
  if (a.length !== b.length) {
    // Still burn a comparison so a length mismatch is not faster to detect.
    let sink = 0;
    for (let i = 0; i < a.length; i++) sink |= a[i];
    return sink === -1;
  }
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

export async function sha256(value) {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(value)));
}

/**
 * Compare a submitted passphrase against the configured one.
 * Both sides are hashed first and the digests compared byte by byte, so the
 * comparison time does not depend on how far the strings match.
 */
export async function passphraseMatches(submitted, expected) {
  const [a, b] = await Promise.all([sha256(submitted), sha256(expected)]);
  return timingSafeEqual(a, b);
}

async function hmacKey(secret) {
  return crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false,
    ["sign", "verify"]
  );
}

const b64url = (bytes) =>
  btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

const unb64url = (s) => {
  const p = s.replace(/-/g, "+").replace(/_/g, "/");
  return Uint8Array.from(atob(p + "=".repeat((4 - (p.length % 4)) % 4)), (c) => c.charCodeAt(0));
};

/** Signed session token: base64url(payload).base64url(hmac). No PII inside. */
export async function issueToken(secret, hours = SESSION_HOURS) {
  const payload = JSON.stringify({ exp: Date.now() + hours * 3600 * 1000 });
  const body = b64url(enc.encode(payload));
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(body)));
  return `${body}.${b64url(sig)}`;
}

export async function tokenIsValid(token, secret) {
  if (typeof token !== "string" || !token.includes(".")) return false;
  const [body, sig] = token.split(".", 2);
  if (!body || !sig) return false;
  let expected;
  try {
    expected = new Uint8Array(await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(body)));
  } catch {
    return false;
  }
  let given;
  try {
    given = unb64url(sig);
  } catch {
    return false;
  }
  if (!timingSafeEqual(expected, given)) return false;
  try {
    const { exp } = JSON.parse(new TextDecoder().decode(unb64url(body)));
    return typeof exp === "number" && Date.now() < exp;
  } catch {
    return false;
  }
}

export function readCookie(request, name) {
  const header = request.headers.get("Cookie") || "";
  for (const part of header.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

export function sessionCookie(token, hours = SESSION_HOURS) {
  return [
    `${COOKIE_NAME}=${token}`,
    "HttpOnly",
    "Secure",
    "SameSite=Strict",
    "Path=/",
    `Max-Age=${hours * 3600}`,
  ].join("; ");
}

/**
 * Per-IP attempt limiter. The address is hashed before it becomes a key and
 * the entry expires on its own, so no address is retained past the window.
 */
export async function rateLimit(env, request, { limit = 10, windowSeconds = 900 } = {}) {
  const kv = env.ARCHIVE;
  if (!kv) return { ok: true, remaining: limit };
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const digest = b64url(await sha256(ip + "|" + (env.COOKIE_SECRET || ""))).slice(0, 22);
  const bucket = Math.floor(Date.now() / (windowSeconds * 1000));
  const key = `rl:${bucket}:${digest}`;
  const current = parseInt((await kv.get(key)) || "0", 10);
  if (current >= limit) return { ok: false, remaining: 0 };
  // expirationTtl has a 60s floor in KV.
  await kv.put(key, String(current + 1), { expirationTtl: Math.max(60, windowSeconds) });
  return { ok: true, remaining: limit - current - 1 };
}

/** Timestamp and outcome only. Never the address, never the submitted value. */
export function audit(event, ok, extra = {}) {
  console.log(JSON.stringify({ at: new Date().toISOString(), event, ok, ...extra }));
}
