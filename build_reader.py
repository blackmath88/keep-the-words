#!/usr/bin/env python3
"""
build_reader.py — Step 3 of the Sessler archive pipeline.

Reads articles/*.md, embeds everything into one self-contained HTML file.
No server needed — double-click sessler-archive.html.
"""

import json, os, re, glob, html, time
from datetime import datetime
from urllib.parse import urlencode, quote

INDIR = "articles"
OUT = "sessler-archive.html"


def parse_md(path):
    raw = open(path, encoding="utf-8").read()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", raw, re.S)
    if not match:
        return None
    meta, prov = {}, {}
    for line in match[1].splitlines():
        m = re.match(r'^(\s*)([a-z_]+):\s*(.*)$', line)
        if not m or m[2] == "provenance":
            continue
        indent, key, value = m.groups()
        try:
            value = json.loads(value)
        except ValueError:
            pass
        (prov if indent else meta)[key] = value
    meta.update(provenance=prov, body=raw[match.end():].strip())
    return meta


def norm_date(s):
    s = str(s or "").strip()
    if not s:
        return ""
    patterns = [
        (r"\b\d{4}-\d{1,2}-\d{1,2}(?!\d)", ["%Y-%m-%d"]),
        (r"\b\d{4}/\d{1,2}/\d{1,2}\b", ["%Y/%m/%d"]),
        (r"\b\d{1,2}/\d{1,2}/\d{4}\b", ["%m/%d/%Y"]),
        (r"\b\d{1,2}-\d{1,2}-\d{4}\b", ["%m-%d-%Y"]),
        (r"\b[A-Za-z]+\.?\s+\d{1,2}(?:st|nd|rd|th)?[,]?\s+\d{4}\b", ["%b %d %Y", "%B %d %Y"]),
        (r"\b\d{1,2}\s+[A-Za-z]+\.?[,]?\s+\d{4}\b", ["%d %b %Y", "%d %B %Y"]),
    ]
    for pattern, formats in patterns:
        m = re.search(pattern, s, re.I)
        if not m:
            continue
        value = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", m[0], flags=re.I)
        value = re.sub(r"\bSept\b", "Sep", value, flags=re.I).replace(",", "").replace(".", "")
        value = re.sub(r"\s+", " ", value)
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return ""


def md_to_html(md):
    out = []
    for block in md.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        e = html.escape(b)
        e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
        e = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", e)
        if b.startswith("#"):
            lvl = len(b) - len(b.lstrip("#"))
            out.append(f"<h{lvl}>{e.lstrip('#').strip()}</h{lvl}>")
        elif b.startswith("- "):
            items = "".join(f"<li>{html.escape(l[2:])}</li>"
                            for l in b.splitlines() if l.startswith("- "))
            out.append(f"<ul>{items}</ul>")
        elif b.startswith("> "):
            out.append(f"<blockquote>{e.lstrip('&gt; ')}</blockquote>")
        else:
            out.append(f"<p>{e}</p>")
    return "".join(out)


def action_links(meta):
    p = meta["provenance"]
    url = p.get("original_url", "")
    archived = p.get("retrieved_from", "")
    primary = url if str(p.get("source_type", "")).startswith("live") else archived
    cdx = "https://web.archive.org/cdx/search/cdx?" + urlencode({"url": url, "output": "json", "filter": "statuscode:200"})
    links = [
        {"label": "Read this piece", "url": primary},
        {"label": "All captures", "url": "https://web.archive.org/web/*/" + url},
        {"label": "Closest capture", "url": "https://web.archive.org/web/2/" + url},
        {"label": "Raw capture list", "url": cdx},
    ]
    date = norm_date(meta.get("date", ""))
    if date:
        month = date[:7].replace("-", "")
        links.insert(3, {"label": "Captures in publication month", "url": cdx + "&from=" + month + "&to=" + month})
    title = meta.get("title", "")
    links.extend([
        {"label": "Search title on Google", "url": "https://www.google.com/search?" + urlencode({"q": 'site:nfl.com "' + title + '"'})},
        {"label": "Search title on Wayback", "url": "https://web.archive.org/web/*/" + quote(title, safe="")},
    ])
    return links


def main():
    arts = []
    undated = []
    for path in sorted(glob.glob(os.path.join(INDIR, "*.md"))):
        m = parse_md(path)
        if not m:
            continue
        date = norm_date(m.get("date", ""))
        if not date:
            undated.append({"file": path, "raw_date": m.get("date", ""), "url": m["provenance"].get("original_url", "")})
        p = m["provenance"]
        arts.append(dict(id=m["slug"], t=m.get("title", ""), d=m.get("dek", ""),
                         date=date, y=date[:4] if date else "undated", by=m.get("byline_status", "unparsed"),
                         series=m.get("series", ""), fmt=m.get("format", "news brief"),
                         teams=m.get("entities", {}).get("teams", []), players=m.get("entities", {}).get("players", []),
                         wc=int(m.get("word_count") or 0), url=p.get("original_url", ""), cap=p.get("discovery_capture", ""),
                         src="wayback" if p.get("source_type")=="wayback" else "live", wb=p.get("wayback_timestamp", ""),
                         byline_source=m.get("byline_source", "section-page"), content_id=m.get("content_id", ""),
                         p=p, h=md_to_html(m["body"]), text=m["body"], links=action_links(m)))
    arts.sort(key=lambda a: (a["date"], a["id"]), reverse=True)
    years = sorted({a["y"] for a in arts if a["y"] != "undated"})
    coverage = "–".join([years[0], years[-1]]) if years else "undated"
    manifest = f'<span><b>{len(arts)}</b> pieces</span><span><b>{coverage}</b></span>'
    manifest += f'<span><b>{sum(a["src"]=="wayback" for a in arts)}</b> from Wayback</span>'
    manifest += f'<span><b>{sum(a["by"]=="sessler" for a in arts)}</b> Sessler bylines</span>'
    manifest += f'<span><b>{sum(a["by"].startswith("other:") for a in arts)}</b> other writers</span>'
    manifest += f'<span><b>{sum(a["by"]=="unparsed" for a in arts)}</b> bylines unread</span>'
    text = " ".join(a["text"].lower() for a in arts if a["by"] == "sessler")
    concordance = [[phrase, len(re.findall(r"\b" + re.escape(phrase) + r"\b", text))]
                   for phrase in ["berserker", "fever dream", "the football gods", "donezo", "kept a bag packed"]]
    template = open("reader-prototype.html", encoding="utf-8").read()
    doc = template.replace("__DATA__", json.dumps(arts, ensure_ascii=False).replace("<", "\\u003c"))
    doc = doc.replace("__CONCORDANCE__", json.dumps(concordance)).replace("__MANIFEST__", manifest)
    doc = doc.replace("__BUILT__", time.strftime("%Y-%m-%d"))
    open(OUT, "w", encoding="utf-8").write(doc)
    # Keep date gaps as structured evidence; do not manufacture a year-only date.
    if os.path.exists("index.json"):
        data = json.load(open("index.json"))
        data.setdefault("reader_builds", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                                      "articles": len(arts), "undated": undated})
        with open("index.json.tmp", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace("index.json.tmp", "index.json")
    print(f"wrote {OUT}: articles={len(arts)} undated={len(undated)}")


if __name__ == "__main__":
    main()
