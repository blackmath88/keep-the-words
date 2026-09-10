import { COOKIE_NAME, readCookie, tokenIsValid, audit } from "../_lib/auth.js";

/**
 * Serves the gated payload: article bodies plus the full-text search index,
 * as one gzip blob.
 *
 * The blob lives in KV, not in the Pages output, so there is no URL under the
 * site that serves it and no build artefact to find. The bytes are returned
 * without Content-Encoding on purpose — the reader decompresses them itself
 * with DecompressionStream, and letting the browser do it too would leave the
 * client trying to gunzip plain JSON.
 */
export async function onRequest({ request, env }) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { Allow: "GET", "Cache-Control": "no-store" },
    });
  }

  if (!env.COOKIE_SECRET) {
    audit("bodies", false, { reason: "unconfigured" });
    return new Response("The gate is not configured.", {
      status: 503,
      headers: { "Cache-Control": "no-store" },
    });
  }

  const token = readCookie(request, COOKIE_NAME);
  if (!token || !(await tokenIsValid(token, env.COOKIE_SECRET))) {
    audit("bodies", false, { reason: "locked" });
    return new Response(JSON.stringify({ error: "locked" }), {
      status: 401,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }

  const payload = await env.ARCHIVE.get("payload", { type: "arrayBuffer" });
  if (!payload) {
    audit("bodies", false, { reason: "missing_payload" });
    return new Response("Payload not loaded.", {
      status: 503,
      headers: { "Cache-Control": "no-store" },
    });
  }

  audit("bodies", true, { bytes: payload.byteLength });
  return new Response(request.method === "HEAD" ? null : payload, {
    status: 200,
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Length": String(payload.byteLength),
      // Never store the article text in a shared cache.
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
