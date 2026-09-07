#!/usr/bin/env python3
"""
harvest_index.py — Step 1 of the Sessler archive pipeline.

Enumerates article URLs by walking historical Wayback Machine captures of
Marc Sessler's author/index pages. Every discovered URL keeps a record of
which capture it was found in (provenance).

Output: index.json
"""

import json, re, time, os
from collections import Counter
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

OUT = "index.json"
UA = {"User-Agent": "personal-archive-script/1.0 (private research use)"}
SLEEP = 5.0
BACKOFF = (5, 10, 20, 40)
LEGACY = re.compile(r"^/news/story/([^/]+)(?:/(article|comments)(?:/(.*))?)?/?$", re.I)

# Author / index pages to walk through time. Add more if you find them.
SEEDS = [
    "https://www.nfl.com/author/marc-sessler-09000d5d823c1a70",
    "http://www.nfl.com/news/writer/marc-sessler",
    "http://blogs.nfl.com/author/marcsessler/",
    "http://www.nfl.com/blogs/around-the-league",
    "http://www.nfl.com/news/around-the-league",
]

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def clean_url(u):
    u = u.strip()
    m = re.search(r"/web/\d+(?:[a-z]+_)?/(https?://.*)$", u)
    if m:
        u = m.group(1)
    u = u.split("?")[0].split("#")[0].strip().rstrip("/")
    u = re.sub(r"^(https?://[^/:]+):(?:80|443)(?=/|$)", r"\1", u)
    u = re.sub(r"^http://", "https://", u)
    return re.sub(r"^https://nfl\.com(?=/|$)", "https://www.nfl.com", u)


def canonical(u):
    """Legacy identity is the content ID, regardless of view or slug."""
    u = clean_url(u)
    m = LEGACY.fullmatch(urlparse(u).path)
    return "legacy:" + m[1].lower() if m else u


def kind(u):
    path = urlparse(clean_url(u)).path
    parts = path.strip("/").split("/")
    if any(c in u for c in "{}") or any(p in {
        "author", "writer", "series", "video", "videos", "photos", "watch",
        "schedules", "scores", "teams", "sitemap", "search"
    } for p in parts):
        return "nav"
    if path in ("/news", "/news/story", "/blogs/around-the-league", "/news/around-the-league"):
        return "index"
    if re.fullmatch(r"/(?:news|blogs)/around-the-league/\d+", path):
        return "index"
    if re.fullmatch(r"(?:\d{1,4}[-/]){2}\d{1,4}", "/".join(parts[2:])):
        return "index"
    m = LEGACY.fullmatch(path)
    if m:
        return "article" if m[3] else "index"
    if len(parts) == 2 and parts[0] == "news" and "-" in parts[1]:
        return "article"
    return "unknown"


def add_article(articles, incoming):
    u = clean_url(incoming["url"])
    key = canonical(u)
    m = LEGACY.fullmatch(urlparse(u).path)
    item = dict(incoming, url=u, kind=kind(u))
    if m:
        root = "https://www.nfl.com/news/story/" + m[1]
        suffix = "/" + m[3] if m[3] else ""
        item.update(content_id=m[1].lower(), body_url=root + "/article" + suffix,
                    comments_url=root + "/comments" + suffix)
        item["url"] = item["body_url"]
    else:
        item["body_url"] = u
    item.setdefault("status", "pending")
    observed = set(item.get("observed_urls", [])) | {u}
    if key in articles:
        old = articles[key]
        observed.update(old.get("observed_urls", []))
        if len(item.get("title") or "") > len(old.get("title") or ""):
            old["title"] = item["title"]
        # Preserve alternate records, including any fetch failures and provenance.
        if incoming not in old.setdefault("merged_records", []):
            old["merged_records"].append(incoming)
        if m and m[2] == "article":
            old.update(url=item["url"], body_url=item["body_url"])
        old["observed_urls"] = sorted(observed)
        return
    item["observed_urls"] = sorted(observed)
    articles[key] = item


def cdx(seed, payload, save):
    record = {"seed": seed, "at": now()}
    try:
        r = requests.get("https://web.archive.org/cdx/search/cdx", params={
            "url": seed, "output": "json", "fl": "timestamp,original,statuscode",
            "filter": "statuscode:200", "collapse": "timestamp:6",
        }, headers=UA, timeout=60)
        record["http_status"] = r.status_code
        r.raise_for_status()
        rows = r.json()
        record.update(outcome="ok", captures=max(0, len(rows) - 1))
    except (requests.RequestException, ValueError) as e:
        record.update(outcome="failed", error=str(e))
        rows = []
        print(f"  ! CDX failed: {e}", flush=True)
    payload.setdefault("cdx_history", []).append(record)
    save()
    return rows[1:]


def request_with_backoff(url, history, save, phase="fetch", params=None):
    """One shared request policy; replay is paced, CDX has no base delay."""
    replay = urlparse(url).hostname == "web.archive.org" and "/web/" in urlparse(url).path
    for attempt, delay in enumerate(BACKOFF, 1):
        outcome = {"at": now(), "phase": phase, "attempt": attempt, "url": url}
        retryable = False
        try:
            if replay:
                time.sleep(SLEEP)
            r = requests.get(url, params=params, headers=UA, timeout=60)
            outcome.update(http_status=r.status_code, retrieved_url=r.url)
            retryable = r.status_code in (429, 503)
            r.raise_for_status()
            outcome["outcome"] = "ok"
            history.append(outcome)
            save()
            return r
        except requests.RequestException as e:
            retryable = retryable or isinstance(e, (requests.ConnectionError, requests.Timeout))
            outcome.update(outcome="failed", error_type=type(e).__name__, error=str(e))
            history.append(outcome)
            save()
            print(f"  ! {phase} attempt={attempt}: {type(e).__name__}", flush=True)
            if not retryable:
                break
            time.sleep(delay)
    return None


def parse_capture(record, phase, save):
    r = request_with_backoff(record["capture_url"], record["history"], save, phase)
    if r is None:
        record["outcome"] = "failed"
        save()
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    if r.status_code != 200 or not soup.find("a", href=re.compile(r"nfl\.com|^/news/|^/web/")):
        record["history"].append({"at": now(), "phase": phase, "outcome": "failed",
                                  "error_type": "ReplayError", "error": "No NFL links or unexpected status"})
        record["outcome"] = "failed"
        save()
        return None
    found = []
    for a in soup.find_all("a", href=True):
        href = clean_url(urljoin(record["original"], a["href"].strip()))
        parsed = urlparse(href)
        if parsed.netloc not in ("www.nfl.com", "blogs.nfl.com"):
            continue
        if not (parsed.path == "/news" or parsed.path.startswith(("/news/", "/blogs/around-the-league"))):
            continue
        title = re.sub(r"\s+", " ", a.get("title") or a.get_text(" ", strip=True))[:300]
        found.append((href, title))
    record["history"].append({"at": now(), "phase": phase, "outcome": "parsed", "hits": len(found)})
    return found


def main():
    payload = json.load(open(OUT)) if os.path.exists(OUT) else {}
    articles = {}
    previous = payload.get("articles", [])
    payload.setdefault("initial_kind_buckets", dict(Counter(kind(a["url"]) for a in previous)))
    for a in previous:
        add_article(articles, a)
    captures = payload.setdefault("captures", {})
    run = {"started_at": now(), "attempted": 0, "parsed": 0,
           "recovered_by_retry": 0, "still_failed": 0, "skipped_parsed": 0}
    payload.setdefault("harvest_runs", []).append(run)

    def save():
        payload.update(generated_at=now(), seeds=SEEDS,
                       method="Wayback CDX enumeration of author/index page captures",
                       count=len(articles),
                       unique_legacy_content_ids=sum("content_id" in a for a in articles.values()),
                       kind_buckets=dict(Counter(a["kind"] for a in articles.values())),
                       articles=sorted(articles.values(), key=lambda a: a["url"]))
        with open(OUT + ".tmp", "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(OUT + ".tmp", OUT)

    def walk(record, phase):
        hits = parse_capture(record, phase, save)
        if hits is None:
            return False
        for url, title in hits:
            incoming = {"url": url, "title": title, "discovered_via": record["seed"],
                        "discovered_in_capture": record["timestamp"],
                        "capture_url": record["capture_url"]}
            add_article(articles, incoming)
        record["outcome"] = "parsed"
        record["hits"] = len(hits)
        record["parsed_at"] = now()
        run["parsed"] += 1
        if phase == "retry" or any(h["outcome"] == "failed" for h in record["history"]):
            run["recovered_by_retry"] += 1
        save()
        print(f"  {record['timestamp']} {phase}: parsed hits={len(hits)} identities={len(articles)}", flush=True)
        return True

    save()
    scheduled = {}
    for seed in SEEDS:
        print(f"== seed: {seed}", flush=True)
        rows = cdx(seed, payload, save)
        print(f"  {len(rows)} captures", flush=True)
        for ts, original, status in rows:
            key = seed + "|" + ts
            record = captures.setdefault(key, {
                "seed": seed, "timestamp": ts, "original": original,
                "capture_url": f"https://web.archive.org/web/{ts}/{original}",
                "outcome": "pending", "history": [],
            })
            scheduled[key] = record
    # Keep failed/pending captures eligible even if a later CDX request fails.
    scheduled.update({k: v for k, v in captures.items() if v["outcome"] != "parsed"})
    queue = []
    for record in scheduled.values():
        if record["outcome"] == "parsed":
            run["skipped_parsed"] += 1
            continue
        run["attempted"] += 1
        if not walk(record, "initial"):
            queue.append(record)
            payload["retry_queue"] = [r["capture_url"] for r in queue]
            save()
    for record in queue:
        if not walk(record, "retry"):
            run["still_failed"] += 1
        payload["retry_queue"] = [r["capture_url"] for r in queue if r["outcome"] != "parsed"]
        save()
    run["finished_at"] = now()
    save()
    print(json.dumps(run), flush=True)
    print(f"wrote {OUT}: {len(articles)} identities; {payload['unique_legacy_content_ids']} legacy content IDs", flush=True)


if __name__ == "__main__":
    main()
