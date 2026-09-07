#!/usr/bin/env python3
"""
fetch_bodies.py — Step 2 of the Sessler archive pipeline.

Reads index.json, fetches each article (live NFL.com first, Wayback as
fallback), extracts the body, and writes articles/<slug>.md with YAML
frontmatter including a full provenance block.

Resumable: skips anything already written. Ctrl-C safe.
"""

import json, os, re, sys, time, hashlib
import requests
from bs4 import BeautifulSoup

INDEX = "index.json"
OUTDIR = "articles"
UA = {"User-Agent": "personal-archive-script/1.0 (private research use)"}
SLEEP = 1.5
AUTHOR_HINT = "sessler"

BODY_SELECTORS = [
    ".nfl-c-article__container", ".nfl-c-body-part", ".article-body",
    "[itemprop=articleBody]", "article .content", ".story-content",
]


def slugify(url):
    tail = url.rstrip("/").split("/")[-1]
    tail = re.sub(r"[^a-z0-9\-]+", "-", tail.lower()).strip("-")[:90]
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{tail or 'article'}-{h}"


def get(url, timeout=45):
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        return r
    except Exception:
        return None


def wayback_snapshot(url):
    r = get(f"https://archive.org/wayback/available?url={url}")
    if not r or r.status_code != 200:
        return None, None
    try:
        s = r.json().get("archived_snapshots", {}).get("closest")
        if s and s.get("available"):
            return s["url"], s.get("timestamp")
    except Exception:
        pass
    return None, None


def pick_body(soup):
    for sel in BODY_SELECTORS:
        el = soup.select_one(sel)
        if el and len(el.find_all("p")) >= 2:
            return el, sel
    # fallback: the container holding the most <p> tags
    best, best_n = None, 0
    for el in soup.find_all(["div", "section", "article"]):
        n = len(el.find_all("p", recursive=False))
        if n > best_n:
            best, best_n = el, n
    return (best, "heuristic:densest-p-container") if best_n >= 2 else (None, None)


def to_markdown(el):
    out = []
    for node in el.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"]):
        txt = node.get_text(" ", strip=True)
        txt = re.sub(r"\s+", " ", txt)
        if not txt or len(txt) < 2:
            continue
        if re.search(r"(browser you are using|Advertising|Related Links|"
                     r"cookie|Subscribe to)", txt, re.I) and len(txt) < 200:
            continue
        name = node.name
        if name.startswith("h"):
            out.append("#" * min(int(name[1]) + 1, 6) + " " + txt)
        elif name == "li":
            out.append("- " + txt)
        elif name == "blockquote":
            out.append("> " + txt)
        else:
            out.append(txt)
    # de-dupe consecutive repeats (common in archived pages)
    dedup = [l for i, l in enumerate(out) if i == 0 or l != out[i - 1]]
    return "\n\n".join(dedup).strip()


def find_meta(soup):
    def m(*names):
        for n in names:
            t = (soup.find("meta", property=n) or
                 soup.find("meta", attrs={"name": n}))
            if t and t.get("content"):
                return t["content"].strip()
        return ""
    title = m("og:title", "twitter:title") or (
        soup.title.get_text(strip=True) if soup.title else "")
    dek = m("og:description", "description")
    date = m("article:published_time", "publish-date", "date", "pubdate")
    if not date:
        t = soup.find("time")
        if t:
            date = (t.get("datetime") or t.get_text(strip=True) or "").strip()
    byline = m("author", "article:author")
    if not byline:
        for sel in [".nfl-c-author__name", ".author", "[rel=author]", ".byline"]:
            el = soup.select_one(sel)
            if el:
                byline = el.get_text(" ", strip=True)
                break
    return title, dek, date, byline


def yaml_esc(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    data = json.load(open(INDEX))
    os.makedirs(OUTDIR, exist_ok=True)
    done = skipped = failed = 0

    for i, a in enumerate(data["articles"], 1):
        if a.get("kind", "unknown") not in ("article", "unknown"):
            continue
        slug = slugify(a["url"])
        path = os.path.join(OUTDIR, slug + ".md")
        if os.path.exists(path):
            skipped += 1
            continue
        if limit and done >= limit:
            break

        src, src_kind, wb_ts, status = a["url"], "live:nfl.com", "", None
        r = get(a["url"])
        status = r.status_code if r else None
        if not r or r.status_code != 200 or len(r.text) < 2000:
            wb_url, wb_ts = wayback_snapshot(a["url"])
            if wb_url:
                r = get(wb_url)
                src, src_kind = wb_url, "wayback"
                status = r.status_code if r else None

        if not r or r.status_code != 200:
            a["status"] = f"failed:{status}"
            failed += 1
            print(f"[{i}] FAIL {status} {a['url']}")
            time.sleep(SLEEP)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        title, dek, date, byline = find_meta(soup)
        body_el, sel = pick_body(soup)
        body = to_markdown(body_el) if body_el else ""

        if len(body) < 300:
            a["status"] = "failed:thin-body"
            failed += 1
            print(f"[{i}] THIN {a['url']}")
            time.sleep(SLEEP)
            continue

        blob = (title + " " + byline + " " + body[:1500]).lower()
        verified = AUTHOR_HINT in blob

        fm = [
            "---",
            f"title: {yaml_esc(title or a.get('title') or slug)}",
            f"dek: {yaml_esc(dek)}",
            f"date: {yaml_esc(date)}",
            f"byline: {yaml_esc(byline)}",
            f"byline_verified: {str(verified).lower()}",
            f"slug: {yaml_esc(slug)}",
            f"word_count: {len(body.split())}",
            "provenance:",
            f"  original_url: {yaml_esc(a['url'])}",
            f"  retrieved_from: {yaml_esc(src)}",
            f"  source_type: {yaml_esc(src_kind)}",
            f"  wayback_timestamp: {yaml_esc(wb_ts)}",
            f"  http_status: {status}",
            f"  body_selector: {yaml_esc(sel)}",
            f"  retrieved_at: {yaml_esc(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))}",
            f"  discovered_via: {yaml_esc(a.get('discovered_via', ''))}",
            f"  discovery_capture: {yaml_esc(a.get('capture_url', ''))}",
            "---",
            "",
        ]
        open(path, "w").write("\n".join(fm) + body + "\n")
        a["status"] = "ok"
        a["slug"] = slug
        done += 1
        print(f"[{i}] OK  {'AI' if not verified else '  '} {len(body.split()):5d}w  {title[:70]}")
        time.sleep(SLEEP)

        if done % 20 == 0:
            json.dump(data, open(INDEX, "w"), indent=2, ensure_ascii=False)

    json.dump(data, open(INDEX, "w"), indent=2, ensure_ascii=False)
    print(f"\ndone={done} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
