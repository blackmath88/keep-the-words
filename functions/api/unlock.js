import { passphraseMatches, issueToken, sessionCookie, rateLimit, audit } from "../_lib/auth.js";

const json = (body, status, headers = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...headers },
  });

export async function onRequest({ request, env }) {
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { Allow: "POST", "Cache-Control": "no-store" },
    });
  }

  if (!env.ARCHIVE_KEY || !env.COOKIE_SECRET) {
    audit("unlock", false, { reason: "unconfigured" });
    return json({ error: "The gate is not configured." }, 503);
  }

  const limit = await rateLimit(env, request);
  if (!limit.ok) {
    audit("unlock", false, { reason: "rate_limited" });
    return json({ error: "Too many attempts. Try again in a little while." }, 429,
      { "Retry-After": "900" });
  }

  let submitted = "";
  try {
    const body = await request.json();
    submitted = typeof body?.passphrase === "string" ? body.passphrase : "";
  } catch {
    submitted = "";
  }

  // An empty submission still costs an attempt and still takes the hash path,
  // so probing for "does empty behave differently" tells an attacker nothing.
  const ok = await passphraseMatches(submitted, env.ARCHIVE_KEY);
  audit("unlock", ok);

  if (!ok) return json({ error: "that passphrase doesn't open this" }, 401);

  const token = await issueToken(env.COOKIE_SECRET);
  return json({ ok: true }, 200, { "Set-Cookie": sessionCookie(token) });
}
