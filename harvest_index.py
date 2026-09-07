#!/usr/bin/env python3
"""
harvest_index.py — Step 1 of the Sessler archive pipeline.

Enumerates article URLs by walking historical Wayback Machine captures of
Marc Sessler's author/index pages. Every discovered URL keeps a record of
which capture it was found in (provenance).

Output: index.json
"""

import json, re, sys, time, os
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

OUT = "index.json"
UA = {"User-Agent": "personal-archive-script/1.0 (private research use)"}
SLEEP = 1.0

# Author / index pages to walk through time. Add more if you find them.
SEEDS = [
    "https://www.nfl.com/author/marc-sessler-09000d5d823c1a70",
    "http://www.nfl.com/news/writer/marc-sessler",
    "http://blogs.nfl.com/author/marcsessler/",
    "http://www.nfl.com/blogs/around-the-league",
    "http://www.nfl.com/news/around-the-league",
]

# What counts as an article URL
ARTICLE_PAT = re.compile(
    r"nfl\.com/(news|blogs/around-the-league|news/story)/", re.I
)
SKIP_PAT = re.compile(
    r"/(author|writer|video|photos|watch|schedules|scores|teams)/", re.I
)


def cdx(url, collapse="timestamp:6", limit=None):
    """List Wayback captures for a URL (prefix match on the exact page)."""
    params = {
        "url": url,
        "output": "json",
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
        "collapse": collapse,
    }
    if limit:
        params["limit"] = limit
    try:
        r = requests.get("https://web.archive.org/cdx/search/cdx",
                         params=params, headers=UA, timeout=60)
        r.raise_for_status()
        rows = r.json()
    except Exception as e:
        print(f"  ! cdx failed for {url}: {e}")
        return []
    return rows[1:] if len(rows) > 1 else []


def canonical(u):
    """Strip Wayback wrapper, query strings, trailing slash."""
    m = re.search(r"/web/\d+(?:id_|im_|js_)?/(https?://.*)$", u)
    if m:
        u = m.group(1)
    u = u.split("?")[0].split("#")[0].rstrip("/")
    u = re.sub(r"^http://", "https://", u)
    u = re.sub(r"^https://nfl\.com", "https://www.nfl.com", u)
    return u


def parse_capture(ts, seed):
    """Fetch one archived author-page capture, return [(url, title), ...]."""
    wb = f"https://web.archive.org/web/{ts}/{seed}"
    try:
        r = requests.get(wb, headers=UA, timeout=60)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ! fetch failed {ts}: {e}")
        return []

    found = []
    for a in soup.find_all("a", href=True):
        href = canonical(urljoin(seed, a["href"]))
        if not ARTICLE_PAT.search(href) or SKIP_PAT.search(href):
            continue
        if urlparse(href).netloc not in ("www.nfl.com", "blogs.nfl.com"):
            continue
        title = (a.get("title") or a.get_text(" ", strip=True) or "").strip()
        title = re.sub(r"\s+", " ", title)[:300]
        found.append((href, title))
    return found


def main():
    articles = {}
    if os.path.exists(OUT):
        articles = {a["url"]: a for a in json.load(open(OUT))["articles"]}
        print(f"resuming from {OUT} with {len(articles)} known articles")

    for seed in SEEDS:
        print(f"\n== seed: {seed}")
        caps = cdx(seed)
        print(f"   {len(caps)} captures")
        for i, row in enumerate(caps, 1):
            ts = row[0]
            hits = parse_capture(ts, seed)
            new = 0
            for url, title in hits:
                if url in articles:
                    if title and len(title) > len(articles[url].get("title") or ""):
                        articles[url]["title"] = title
                    continue
                articles[url] = {
                    "url": url,
                    "title": title,
                    "discovered_via": seed,
                    "discovered_in_capture": ts,
                    "capture_url": f"https://web.archive.org/web/{ts}/{seed}",
                    "status": "pending",
                }
                new += 1
            print(f"   [{i}/{len(caps)}] {ts}  hits={len(hits)}  new={new}  total={len(articles)}")
            time.sleep(SLEEP)

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": SEEDS,
        "method": "Wayback CDX enumeration of author/index page captures",
        "count": len(articles),
        "articles": sorted(articles.values(), key=lambda a: a["url"]),
    }
    json.dump(payload, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"\nwrote {OUT} — {len(articles)} unique article URLs")


if __name__ == "__main__":
    main()
