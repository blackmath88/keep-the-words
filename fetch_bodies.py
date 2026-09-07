#!/usr/bin/env python3
"""Recover NFL articles with capture evidence and deterministic metadata."""
import copy, csv, hashlib, io, json, os, random, re, sys, time, unicodedata
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from harvest_index import request_with_backoff, now

INDEX = "index.json"
OUTDIR = "articles"
SLEEP = 1.5
BODY_SELECTORS = [
    ".articleText",  # observed in archived 2012–2015 article views
    ".nfl-c-article__container", ".nfl-c-body-part", ".article-body",
    "[itemprop=articleBody]", "article .content", ".story-content",
]


def slugify(url):
    tail = re.sub(r"[^a-z0-9-]+", "-", url.rstrip("/").split("/")[-1].lower()).strip("-")[:90]
    return f"{tail or 'article'}-{hashlib.md5(url.encode()).hexdigest()[:6]}"


def pick_body(soup):
    # Current NFL pages split the story into one rich-text block per paragraph.
    parts = soup.select(".story-part-rich-text-editor-wrapper")
    if parts:
        body = soup.new_tag("div")
        for part in parts:
            body.append(copy.deepcopy(part))
        return body, ".story-part-rich-text-editor-wrapper (all blocks)"
    for sel in BODY_SELECTORS:
        el = soup.select_one(sel)
        if el and len(el.find_all("p")) >= 2:
            return el, sel
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
    def meta(*names):
        for n in names:
            t = soup.find("meta", property=n) or soup.find("meta", attrs={"name": n}) or soup.find("meta", id=n)
            if t and t.get("content"):
                return t["content"].strip()
        return ""
    title = meta("og:title", "articleTitle", "twitter:title") or (soup.title.get_text(strip=True) if soup.title else "")
    dek = meta("og:description", "description")
    published = meta("article:published_time", "publish-date", "date", "pubdate", "datePublished")
    date_selector = "meta" if published else ""
    if not published:
        for sel in ["#article-time", ".published abbr", "[itemprop=datePublished]", ".nfl-c-article__date", "time", ".published", ".publish-date"]:
            t = soup.select_one(sel)
            if t:
                published = t.get("datetime") or t.get("content") or t.get("title") or t.get_text(" ", strip=True)
                if published:
                    date_selector = sel
                    break
    byline = meta("authorName", "author", "article:author")
    byline_selector = "meta" if byline else ""
    if not byline:
        for sel in ["#article-hdr-meta-author", ".nfl-c-author__name", ".byline", "[rel=author]", ".author"]:
            el = soup.select_one(sel)
            if el:
                byline = re.sub(r"^By\s+", "", el.get_text(" ", strip=True), flags=re.I).strip()
                if byline:
                    byline_selector = sel
                    break
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            obj = json.loads(tag.string or tag.get_text())
        except ValueError:
            continue
        nodes = obj if isinstance(obj, list) else [obj]
        for node in nodes[:]:
            if isinstance(node, dict):
                nodes.extend(node.get("@graph", []))
        for node in nodes:
            if not isinstance(node, dict) or not any(t in str(node.get("@type", "")) for t in ("Article", "BlogPosting")):
                continue
            if not published and node.get("datePublished"):
                published, date_selector = node["datePublished"], "jsonld:datePublished"
            if not byline and node.get("author"):
                authors = node["author"] if isinstance(node["author"], list) else [node["author"]]
                byline = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in authors)
                byline_selector = "jsonld:author"
    byline = re.sub(r"^By\s+", "", byline, flags=re.I).strip()
    if byline.lower() in ("no author name", "unknown", "n/a", "none"):
        byline = ""
    status = "sessler" if re.search(r"\b(?:marc\s+)?sessler\b", byline, re.I) else "other:" + byline if byline and not byline.startswith("http") else "unparsed"
    return dict(title=title, dek=dek, date=published, byline=byline, byline_status=status,
                date_selector=date_selector, byline_selector=byline_selector)


def byline_fields(a, raw):
    sources = [a.get("discovered_via", "")] + [m.get("discovered_via", "") for m in a.get("merged_records", [])]
    source = a.get("byline_source") or ("author-page" if any("sessler" in s and ("/author/" in s or "/writer/" in s) for s in sources) else "section-page")
    verdict = "sessler" if re.search(r"\b(?:marc\s+)?sessler\b", raw, re.I) else "other" if raw else "unparsed"
    atl = any(re.search(r"/(?:news|blogs)/around-the-(?:league|nfl)(?:[/_]|$)", s) for s in sources)
    scope = "sessler" if verdict == "sessler" else "atl-blog" if raw and (atl or raw.lower() == "around the nfl staff") else "unresolved"
    return dict(byline_raw=raw, byline_verdict=verdict, byline_status="other:" + raw if verdict == "other" else verdict,
                byline_source=source, scope=scope)


def record_byline(a, meta, raw_file, retrieved_url, phase="byline"):
    # A body failure cannot erase a readable byline from another saved response.
    raw = meta["byline"] if meta["byline_status"] != "unparsed" else ""
    previous = a.get("byline_raw", "")
    if raw or not previous:
        a.update(byline_fields(a, raw))
        a["byline_evidence"] = dict(raw_file=raw_file, retrieved_url=retrieved_url, selector=meta["byline_selector"])
    a.setdefault("fetch_history", []).append(dict(at=now(), phase=phase, raw_file=raw_file,
        retrieved_url=retrieved_url, byline_raw=raw, byline_verdict=byline_fields(a, raw)["byline_verdict"], selector=meta["byline_selector"]))


def archive_stats(data):
    eligible = [a for a in data["articles"] if a.get("kind") not in ("index", "nav", "pagination")]
    recovered = [a for a in eligible if a.get("status") == "ok"]
    def split(entries):
        groups = {}
        for a in entries:
            g = groups.setdefault(a.get("byline_source", "missing"), {"sessler": 0, "other": 0, "unread": 0, "names": {}, "joint_bylines": {}})
            v = a.get("byline_verdict", "unparsed")
            g["unread" if v == "unparsed" else v] += 1
            raw = a.get("byline_raw", "")
            names = set(n.strip() for n in re.split(r",\s*|\s+and\s+|\s*&\s*", raw) if n.strip())
            for n in names:
                g["names"][n] = g["names"].get(n, 0) + 1
            if len(names) > 1:
                g["joint_bylines"][raw] = g["joint_bylines"].get(raw, 0) + 1
        return groups
    failures, fixed = Counter(), Counter()
    for a in eligible:
        if a.get("status", "").startswith("failed:"):
            failures[a["status"]] += 1
        if a.get("status") == "ok":
            fixed.update({h["outcome"] for h in a.get("fetch_history", []) if h.get("outcome", "").startswith("failed:")})
    attempted = [a for a in eligible if a.get("status") != "pending"]
    sections = [a for a in attempted if a.get("byline_source") == "section-page"]
    rate = round(100 * sum(a.get("byline_verdict") == "sessler" for a in sections) / len(sections), 1) if sections else None
    return dict(at=now(), articles=len(recovered), byline_source=split(recovered),
                attempted_byline_source=split(attempted), scope=dict(Counter(a.get("scope", "unresolved") for a in recovered)),
                attempted_scope=dict(Counter(a.get("scope", "unresolved") for a in attempted)),
                failures=dict(failures), fixed_failure_patterns=dict(fixed), section_sessler_percent=rate,
                coverage_note="Section-page Sessler rate differs from the 16% probe by at least 8 percentage points; uneven month/ID coverage may explain the drift." if rate is not None and abs(rate-16) >= 8 else "")


# Closed team vocabulary, including names used during 2012–2024.
TEAM_ALIASES = {
 "Arizona Cardinals": ["Cardinals", "Arizona Cardinals"],
 "Atlanta Falcons": ["Falcons", "Atlanta Falcons"],
 "Baltimore Ravens": ["Ravens", "Baltimore Ravens"],
 "Buffalo Bills": ["Bills", "Buffalo Bills"],
 "Carolina Panthers": ["Panthers", "Carolina Panthers"],
 "Chicago Bears": ["Bears", "Chicago Bears"],
 "Cincinnati Bengals": ["Bengals", "Cincinnati Bengals"],
 "Cleveland Browns": ["Browns", "Cleveland Browns"],
 "Dallas Cowboys": ["Cowboys", "Dallas Cowboys"],
 "Denver Broncos": ["Broncos", "Denver Broncos"],
 "Detroit Lions": ["Lions", "Detroit Lions"],
 "Green Bay Packers": ["Packers", "Green Bay Packers"],
 "Houston Texans": ["Texans", "Houston Texans"],
 "Indianapolis Colts": ["Colts", "Indianapolis Colts"],
 "Jacksonville Jaguars": ["Jaguars", "Jags", "Jacksonville Jaguars"],
 "Kansas City Chiefs": ["Chiefs", "Kansas City Chiefs"],
 "Las Vegas Raiders": ["Raiders", "Oakland Raiders", "Las Vegas Raiders"],
 "Los Angeles Chargers": ["Chargers", "San Diego Chargers", "Los Angeles Chargers"],
 "Los Angeles Rams": ["Rams", "St. Louis Rams", "Los Angeles Rams"],
 "Miami Dolphins": ["Dolphins", "Miami Dolphins"],
 "Minnesota Vikings": ["Vikings", "Minnesota Vikings"],
 "New England Patriots": ["Patriots", "Pats", "New England Patriots"],
 "New Orleans Saints": ["Saints", "New Orleans Saints"],
 "New York Giants": ["Giants", "New York Giants"],
 "New York Jets": ["Jets", "New York Jets"],
 "Philadelphia Eagles": ["Eagles", "Philadelphia Eagles"],
 "Pittsburgh Steelers": ["Steelers", "Pittsburgh Steelers"],
 "San Francisco 49ers": ["49ers", "Niners", "San Francisco 49ers"],
 "Seattle Seahawks": ["Seahawks", "Seattle Seahawks"],
 "Tampa Bay Buccaneers": ["Buccaneers", "Bucs", "Tampa Bay Buccaneers"],
 "Tennessee Titans": ["Titans", "Tennessee Titans"],
 "Washington Commanders": ["Commanders", "Redskins", "Washington Football Team", "Washington Redskins", "Washington Commanders"],
}
SERIES = [
 (r"^(?:NFL )?QB Index\b", "NFL QB Index"),
 (r"^(?:NFL )?Hot or Not\b", "Hot or Not"),
 (r"^Around the League\b", "Around the League"),
 (r"^(?:(?:20\d{2} )?NFL (?:season|preseason)[: -]*)?(?:Week \d+ )?.*?\bunderdogs\b", "Underdogs"),
 (r"^Roster Reset\b", "Roster Reset"),
 (r"^(?:20\d{2} )?(?:NFL )?free agency matchmaking\b", "Free agency matchmaking"),
 (r"^Marc Sessler['’]s 10 favorite\b", "Marc Sessler's 10 favorites"),
]


def normal_text(s):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip()


def enrich(title, body, players):
    text = " " + normal_text(title + " " + body) + " "
    teams = [team for team, aliases in TEAM_ALIASES.items() if any(" " + normal_text(a) + " " in text for a in aliases)]
    matched = sorted({name for alias, name in players.items() if " " + alias + " " in text})
    series = next((name for pattern, name in SERIES if re.search(pattern, title, re.I)), "")
    if re.search(r"\b(dies|died|obituary|remembering|passes away|dead at)\b", title, re.I):
        fmt = "obituary"
    elif re.search(r"\b(rankings?|ranking|ranked|top \d+|QB Index|best and worst)\b", title, re.I):
        fmt = "ranking"
    elif re.search(r"\b(dispatch|from the (?:combine|sidelines)|on the scene|training camp report)\b", title, re.I):
        fmt = "dispatch"
    elif series or len(body.split()) >= 700 or re.search(r"\b(on my radar|why|what we learned|my favorite)\b", title, re.I):
        fmt = "column"
    else:
        fmt = "news brief"
    return dict(series=series, format=fmt, entities={"teams": sorted(teams), "players": matched})


def load_players(data, save):
    root = Path(OUTDIR) / "_rosters"
    root.mkdir(parents=True, exist_ok=True)
    players = {}
    for year in range(2012, 2025):
        path = root / f"roster_{year}.csv"
        if not path.exists():
            u = f"https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{year}.csv"
            rec = {"year": year, "url": u, "history": []}
            data.setdefault("roster_history", []).append(rec)
            r = request_with_backoff(u, rec["history"], save, "roster")
            if r is None:
                continue
            path.write_text(r.text, encoding="utf-8")
        for row in csv.DictReader(io.StringIO(path.read_text())):
            name = row.get("full_name") or row.get("player_name") or " ".join([row.get("first_name", ""), row.get("last_name", "")]).strip()
            for value in [name, row.get("football_name", "") + " " + row.get("last_name", "")]:
                alias = normal_text(value)
                if name and len(alias.split()) >= 2:
                    players.setdefault(alias, name)
    data["roster_dictionary"] = {"source": "nflverse season rosters", "seasons": "2012–2024",
                                 "aliases": len(players), "cached_seasons": len(list(root.glob("*.csv")))}
    save()
    return players


def write_recovery(a, recovered, players, slug, path, retrieved_at=None):
    body_url = a.get("body_url") or a["url"]
    meta, body, selector, r, source_type, ts, src = recovered
    fields = byline_fields(a, a.get("byline_raw") or meta["byline"])
    meta.update(fields, byline=fields["byline_raw"])
    a.update(fields)
    byline_source = fields["byline_source"]
    content_id = a.get("content_id") or (re.search(r"-(0ap[0-9]+|09000[a-f0-9]+)$", body_url).group(1) if re.search(r"-(0ap[0-9]+|09000[a-f0-9]+)$", body_url) else "")
    date_sel, by_sel = meta.pop("date_selector"), meta.pop("byline_selector")
    meta["title"] = meta["title"] or a.get("title") or slug
    meta.update(content_id=content_id, byline_source=byline_source, slug=slug, word_count=len(body.split()))
    meta.update(enrich(meta["title"], body, players))
    actual_ts = re.search(r"/web/(\d{14})", r.url)
    prov = {"original_url": body_url,
            "requested_from": src, "retrieved_from": r.url, "source_type": source_type,
            "wayback_timestamp": actual_ts[1] if actual_ts else ts, "http_status": r.status_code,
            "body_selector": selector, "date_selector": date_sel, "byline_selector": by_sel,
            "retrieved_at": retrieved_at or now(), "discovered_via": a.get("discovered_via", ""),
            "discovery_capture": a.get("capture_url", "")}
    lines = ["---"] + [k + ": " + json.dumps(v, ensure_ascii=False) for k,v in meta.items()]
    lines += ["provenance:"] + ["  " + k + ": " + json.dumps(v, ensure_ascii=False) for k,v in prov.items()] + ["---", ""]
    path.write_text("\n".join(lines) + body + "\n", encoding="utf-8")
    a.update(status="ok", slug=slug, byline_source=byline_source, byline_status=meta["byline_status"], date=meta["date"])


def main():
    repair = "--repair" in sys.argv
    bylines_only = "--reparse-bylines" in sys.argv
    section_sample = "--section-sample" in sys.argv
    limit = int(sys.argv[2]) if section_sample else (int(sys.argv[1]) if len(sys.argv) > 1 and not repair and not bylines_only else 0)
    data = json.load(open(INDEX))
    Path(OUTDIR, "_raw").mkdir(parents=True, exist_ok=True)
    def save():
        with open(INDEX + ".tmp", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(INDEX + ".tmp", INDEX)
    if bylines_only:
        gained = []
        scanned = 0
        for a in data["articles"]:
            if a.get("kind") in ("index", "nav", "pagination"):
                continue
            before = a.get("byline_verdict") or ("other" if a.get("byline_status", "").startswith("other:") else a.get("byline_status", "unparsed"))
            seen = set()
            for h in a.get("fetch_history", [])[:]:
                raw_file = h.get("raw_file", "")
                if not raw_file or raw_file in seen or not Path(raw_file).is_file():
                    continue
                seen.add(raw_file)
                meta = find_meta(BeautifulSoup(Path(raw_file).read_text(), "html.parser"))
                record_byline(a, meta, raw_file, h.get("retrieved_url", h.get("url", "")), "cached-byline")
                scanned += 1
            if not seen:
                a.update(byline_fields(a, a.get("byline_raw", "")))
            if before in ("unparsed", "unread") and a["byline_verdict"] != "unparsed":
                gained.append({"url": a["url"], "byline_raw": a["byline_raw"], "body_status": a.get("status")})
            a.pop("comments", None)
            path = Path(OUTDIR, (a.get("slug") or slugify(a["url"])) + ".md")
            if path.exists():
                text = path.read_text()
                head, body = text.split("\n---\n", 1)
                head = re.sub(r"(?m)^comments:.*(?:\n[ \t]+.*)*\n?", "", head)
                head = re.sub(r"(?m)^  comments_url:.*\n?", "", head)
                for k, v in dict(byline_fields(a, a["byline_raw"]), byline=a["byline_raw"]).items():
                    line = k + ": " + json.dumps(v, ensure_ascii=False)
                    pattern = r"(?m)^" + k + r":.*$"
                    head = re.sub(pattern, lambda m: line, head) if re.search(pattern, head) else head + "\n" + line
                path.write_text(head + "\n---\n" + body)
        audit = {"at": now(), "cached_pages": scanned, "previously_unread_gained_name": len(gained), "gained": gained}
        data.setdefault("byline_reparse_runs", []).append(audit)
        save()
        print(json.dumps(audit), flush=True)
        return
    players = load_players(data, save)
    if repair:
        repaired = 0
        for a in data["articles"]:
            if a.get("status") not in ("failed:thin-body", "ok"):
                continue
            slug = a.get("slug") or slugify(a["url"])
            path = Path(OUTDIR, slug + ".md")
            previous_body = ""
            if path.exists():
                from build_reader import parse_md
                previous_body = parse_md(path)["body"]
            for old in reversed(a.get("fetch_history", [])[:]):
                if old.get("phase") != "extraction" or not Path(old.get("raw_file", "")).is_file():
                    continue
                soup = BeautifulSoup(Path(old["raw_file"]).read_text(), "html.parser")
                record_byline(a, find_meta(soup), old["raw_file"], old.get("retrieved_url", old["url"]), "cached-byline")
                save()
                el, selector = pick_body(soup)
                body = to_markdown(el) if el else ""
                if len(body) < 300 or (previous_body and (selector != ".story-part-rich-text-editor-wrapper (all blocks)" or len(body) <= len(previous_body))):
                    continue
                if previous_body:
                    backup = path.with_suffix(".md.before-repair")
                    if not backup.exists():
                        backup.write_text(path.read_text(), encoding="utf-8")
                url = old.get("retrieved_url", old["url"])
                ts = re.search(r"/web/(\d{14})", url)
                r = SimpleNamespace(url=url, status_code=200)
                recovered = (find_meta(soup), body, selector, r, "wayback" if ts else "live:nfl.com", ts[1] if ts else "", old["url"])
                write_recovery(a, recovered, players, slug, path, old["at"])
                a["fetch_history"].append({"at": now(), "phase": "cached-repair", "outcome": "ok", "selector": selector, "raw_file": old["raw_file"], "body_chars": len(body)})
                repaired += 1
                save()
                print(f"repaired {a['url']} via {selector}", flush=True)
                break
        print(f"cached repairs={repaired}", flush=True)
        return
    done = failed = skipped = attempted = 0
    run = {"started_at": now(), "limit": limit, "articles": []}
    data.setdefault("fetch_runs", []).append(run)
    pending = [a for a in data["articles"] if a.get("kind") not in ("index", "nav", "pagination")
               and not Path(OUTDIR, (a.get("slug") or slugify(a["url"])) + ".md").exists()]
    entries = data["articles"]
    if section_sample:
        pool = [a for a in pending if a.get("byline_source") == "section-page" and a.get("content_id")]
        pool.sort(key=lambda a: (0 if a["content_id"].startswith("090") else 1, a["content_id"]))
        if limit != 100 or len(pool) < limit:
            raise ValueError("Section sample requires 100 entries and at least 100 eligible records")
        seed = 20260907
        rng = random.Random(seed)
        entries = []
        strata = []
        for i in range(10):
            band = pool[i*len(pool)//10:(i+1)*len(pool)//10]
            selected = rng.sample(band, 10)
            entries.extend(selected)
            strata.append({"population": len(band), "first_id": band[0]["content_id"], "last_id": band[-1]["content_id"]})
        rng.shuffle(entries)
        run["sample"] = {"method": "10 random entries per legacy ID population decile; shuffled fetch order",
                         "seed": seed, "population": len(pool), "byline_source": "section-page",
                         "excludes": "already recovered articles", "strata": strata,
                         "selected": [{"url": a["url"], "content_id": a["content_id"]} for a in entries]}
        save()
    elif limit:
        legacy = [a for a in pending if "/news/story/" in a.get("body_url", a["url"])]
        modern = [a for a in pending if a not in legacy]
        entries = []
        for group, n in [(legacy, (limit+1)//2), (modern, limit//2)]:
            entries.extend(group[i*len(group)//min(n,len(group))] for i in range(min(n,len(group))))
        entries.extend(a for a in pending if a not in entries and len(entries) < limit)
        entries = entries[:limit]
    for a in entries:
        if a.get("kind") in ("index", "nav", "pagination"):
            continue
        body_url = a.get("body_url") or a["url"]
        slug = a.get("slug") or slugify(a["url"])
        path = Path(OUTDIR, slug + ".md")
        if path.exists():
            skipped += 1
            continue
        if limit and attempted >= limit:
            break
        attempted += 1
        history = a.setdefault("fetch_history", [])
        if str(a.get("status", "")).startswith("failed:"):
            history.append({"at": now(), "phase": "previous-status", "outcome": a["status"]})
        history.append({"at": now(), "phase": "attempt-start", "previous_status": a.get("status", "pending")})
        save()
        legacy = "/news/story/" in body_url
        candidates = [] if legacy else [(body_url, "live:nfl.com", "")]
        # Discover archived routes lazily after live fails, earliest capture first.
        routes = [body_url] + ([a["comments_url"]] if a.get("comments_url") else [])
        recovered = None
        last_failure = "failed:no-capture"
        for route in ([None] + routes):
            if route is not None:
                r = request_with_backoff("https://web.archive.org/cdx/search/cdx", history, save, "article-cdx",
                    {"url": route, "output": "json", "fl": "timestamp,original", "filter": "statuscode:200", "collapse": "timestamp:6"})
                if r is None:
                    last_failure = "failed:cdx-request"
                    continue
                try:
                    rows = r.json()[1:]
                except ValueError:
                    history.append({"at": now(), "phase": "article-cdx", "outcome": "failed:invalid-json", "url": route})
                    save()
                    last_failure = "failed:cdx-json"
                    continue
                history.append({"at": now(), "phase": "article-cdx-result", "url": route,
                                "outcome": "captures" if rows else "no-capture", "count": len(rows)})
                save()
                if not rows:
                    continue
                ts, original = min(rows, key=lambda row: row[0])
                candidates = [(f"https://web.archive.org/web/{ts}id_/{original}", "wayback", ts)]
            for src, source_type, ts in candidates:
                r = request_with_backoff(src, history, save, "body")
                if r is None:
                    last_failure = "failed:request"
                    continue
                raw = Path(OUTDIR, "_raw", slug + "-" + str(len(history)) + ".html")
                raw.write_text(r.text, encoding="utf-8")
                soup = BeautifulSoup(r.text, "html.parser")
                meta = find_meta(soup)
                record_byline(a, meta, str(raw), r.url)
                save()
                el, selector = pick_body(soup)
                body = to_markdown(el) if el else ""
                result = {"at": now(), "phase": "extraction", "url": src, "retrieved_url": r.url,
                          "raw_file": str(raw), "selector": selector, "body_chars": len(body),
                          "outcome": "ok" if len(body) >= 300 else "failed:thin-body"}
                history.append(result)
                save()
                if len(body) < 300:
                    last_failure = "failed:thin-body"
                    continue
                recovered = (meta, body, selector, r, source_type, ts, src)
                break
            if recovered:
                break
            candidates = []
        if not recovered:
            a["status"] = last_failure
            history.append({"at": now(), "phase": "result", "outcome": last_failure})
            failed += 1
        else:
            write_recovery(a, recovered, players, slug, path)
            done += 1
        run["articles"].append({"url": body_url, "outcome": a["status"]})
        # Cumulative recovered-article checkpoints survive restarts.
        if recovered:
            archived = [entry for entry in data["articles"] if entry.get("status") == "ok"]
            total = len(archived)
            checkpoints = data.setdefault("byline_checkpoints", [])
            if total % 200 == 0 and not any(c["articles"] == total for c in checkpoints):
                checkpoint = archive_stats(data)
                checkpoints.append(checkpoint)
                print("BYLINE CHECKPOINT " + json.dumps(checkpoint), flush=True)
        save()
        print(f"[{attempted}] {a['status']} {body_url}", flush=True)
        time.sleep(SLEEP)
    run.update(finished_at=now(), attempted=attempted, done=done, failed=failed, skipped=skipped)
    save()
    print(f"done={done} failed={failed} skipped={skipped} attempted={attempted}", flush=True)


if __name__ == "__main__":
    main()
