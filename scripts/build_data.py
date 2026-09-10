#!/usr/bin/env python3
"""
build_data.py — emit the public data tier under data/.

Three files are generated here; the analysis files are written by analyse.py.

  data/metadata.json          per article: everything except the body and the
                              dek. This is the same field set the reader
                              publishes, in a form that does not require
                              parsing 1,903 Markdown files.
  data/index.json             the published trim of the fetcher's state: every
                              URL, its provenance, and the failure log. The
                              fetcher's own index.json stays at the repo root
                              because it is live state, not a deliverable.
  data/analysis-matched.json  Set A and Set B: definitions, member article ids,
                              and per-term rates. Every matched-set figure in
                              the essay and the findings traces to this file.

Read-only with respect to articles/ and index.json.

    python3 scripts/build_data.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_reader import parse_md, norm_date          # noqa: E402
from analyse import strip_furniture                    # noqa: E402

OUT = ROOT / "data"

# The terms the essay and findings quote rates for. Kept explicit so the file
# is a fixed contract rather than whatever happened to rank highly today.
MATCHED_TERMS = [
    # the substitution pair — the essay's lead figure
    ("first-round pick", r"\bfirst[\s-]round\s+picks?\b", "plain"),
    ("first-rounder",    r"\bfirst[\s-]rounders?\b",      "elevated"),
    # plain nouns, to show he does not avoid them
    ("cornerback",       r"\bcornerbacks?\b",             "plain"),
    ("wide receiver / wideout", r"\b(?:wide\s+receivers?|wideouts?)\b", "plain"),
    ("season",           r"\bseasons?\b",                 "plain"),
    ("offensive coordinator", r"\boffensive\s+coordinators?\b", "plain"),
    # the second vocabulary
    ("cover man",        r"\bcover\s+m(?:a|e)n\b",        "elevated"),
    ("play caller",      r"\bplay[\s-]callers?\b",        "elevated"),
    ("passer",           r"\bpassers?\b",                 "elevated"),
    ("pass catcher",     r"\bpass[\s-]catchers?\b",       "elevated"),
    ("under center",     r"\bunder\s+center\b",           "elevated"),
    ("signal-caller",    r"\bsignal[\s-]callers?\b",      "elevated"),
    ("autumn",           r"\bautumns?\b",                 "elevated"),
    ("campaign",         r"\bcampaigns?\b",               "elevated"),
    # habits that survived, weakened
    ("looms as",         r"\blooms\s+as\b",               "habit"),
    ("that saw",         r"\bthat\s+saw\b",               "habit"),
    ("rough and tumble", r"\brough[\s-]and[\s-]tumble\b", "habit"),
    ("rugged",           r"\brugged\b",                   "habit"),
    ("league wide",      r"\bleague[\s-]wide\b",          "habit"),
    ("finest",           r"\bfinest\b",                   "habit"),
    ("a rash of",        r"\ba\s+rash\s+of\b",            "habit"),
    # the findings that died
    ("chaos",            r"\bchaos\b",                    "died"),
    ("starry",           r"\bstarry\b",                   "died"),
    ("a flock of",       r"\ba\s+flock\s+of\b",           "died"),
    ("eons",             r"\beons\b",                     "died"),
    ("earth",            r"\bearth\b",                    "died"),
    ("dark",             r"\bdark\b",                     "died"),
    ("war",              r"\bwar\b",                      "died"),
    ("battle",           r"\bbattle\b",                   "died"),
    ("armed with",       r"\barmed\s+with\b",             "died"),
]

ABBREVIATIONS = r"\b(?:CB|WR|OC|DC|DB|RB|TE|QB|LB|OL)\b"
# "Name of The Paper" — the citation habit.
ATTRIBUTION = r"\b[A-Z][a-z]+(?: [A-Z][a-z'.]+){1,2} of The [A-Z][A-Za-z. ]{2,30}"


def load():
    arts = []
    for path in sorted((ROOT / "articles").glob("*.md")):
        m = parse_md(str(path))
        if not m:
            continue
        m["_slug"] = m["slug"]
        m["_year"] = norm_date(m.get("date", ""))[:4]
        arts.append(m)
    return arts


def rate(members, pattern, flags=0):
    rx = re.compile(pattern, flags)
    n = sum(len(rx.findall(a["body"])) for a in members)
    w = sum(len(a["body"].split()) for a in members)
    return n, w, round(10000.0 * n / w, 3) if w else 0.0


def measure(members):
    out = {}
    for label, pattern, kind in MATCHED_TERMS:
        n, w, r = rate(members, pattern, re.I)
        out[label] = {"kind": kind, "occurrences": n, "per_10k": r}
    n, w, r = rate(members, ABBREVIATIONS)
    out["[position abbreviations]"] = {"kind": "abbreviation", "occurrences": n, "per_10k": r}
    n, w, r = rate(members, ATTRIBUTION)
    out["[reporter named with paper]"] = {"kind": "attribution", "occurrences": n, "per_10k": r}
    return out


def final_sentences(members):
    """The 'turn at the end of a paragraph' claim, which did not survive."""
    lens, firstp = [], 0
    for a in members:
        body = strip_furniture(a["body"]).strip()
        paras = [p for p in body.split("\n") if p.strip()]
        if not paras:
            continue
        sents = [s for s in re.split(r"(?<=[.!?])\s+", paras[-1].strip()) if s.strip()]
        if not sents:
            continue
        s = sents[-1]
        lens.append(len(s.split()))
        if re.search(r"\b(I|we|We|my|our|I'm|I'd|we'll|We'll|don't|Don't)\b", s):
            firstp += 1
    lens.sort()
    return {"n": len(lens),
            "median_words": lens[len(lens) // 2] if lens else 0,
            "pct_12_words_or_fewer": round(100.0 * sum(1 for x in lens if x <= 12) / len(lens), 1) if lens else 0,
            "pct_first_person_or_contraction": round(100.0 * firstp / len(lens), 1) if lens else 0}


def build():
    arts = load()
    OUT.mkdir(exist_ok=True)

    # ---------------------------------------------------------- metadata ---
    meta = []
    for a in arts:
        p = a.get("provenance", {})
        meta.append({
            "id": a["slug"],
            "title": a.get("title", ""),
            "date": norm_date(a.get("date", "")),
            "byline": a.get("byline_raw", ""),
            "byline_verdict": a.get("byline_verdict", ""),
            "byline_source": a.get("byline_source", ""),
            "scope": a.get("scope", ""),
            "format": a.get("format", ""),
            "series": a.get("series", ""),
            "word_count": a.get("word_count", 0),
            "entities": a.get("entities", {}),
            "original_url": p.get("original_url", ""),
            "retrieved_from": p.get("retrieved_from", ""),
            "source_type": p.get("source_type", ""),
            "wayback_timestamp": p.get("wayback_timestamp", ""),
            "http_status": p.get("http_status"),
            "discovered_via": p.get("discovered_via", ""),
            "discovery_capture": p.get("discovery_capture", ""),
            # deliberately absent: body, dek
        })
    (OUT / "metadata.json").write_text(json.dumps({
        "note": "Per-article metadata. No article body and no dek: the dek is a "
                "published sentence of NFL.com copy and is not redistributed here.",
        "count": len(meta), "articles": meta}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------- index ---
    src = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    entries = []
    for e in src.get("articles", []):
        entries.append({"url": e.get("url", ""), "kind": e.get("kind", ""),
                        "status": e.get("status", ""),
                        "capture_url": e.get("capture_url", ""),
                        "discovered_via": e.get("discovered_via", ""),
                        "discovered_in_capture": e.get("discovered_in_capture", "")})
    failures = [e for e in entries if str(e["status"]).startswith("failed")]
    (OUT / "index.json").write_text(json.dumps({
        "note": "Published trim of the harvest index: every discovered URL, how it "
                "was found, and how it ended. The fetcher's live state file stays "
                "outside the data tier.",
        "seeds": src.get("seeds", []),
        "counts": dict(Counter(e["status"] for e in entries)),
        "failure_log": failures,
        "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ----------------------------------------------------------- matched ---
    S = [a for a in arts if a.get("byline_verdict") == "sessler"]
    C = [a for a in arts if a.get("byline_verdict") == "other"]
    setA = {
        "sessler": [a for a in S if a["_year"] <= "2018" and a.get("format") == "news brief"],
        "colleagues": [a for a in C if a["_year"] <= "2018" and a.get("format") == "news brief"],
    }
    setB = {
        "sessler": [a for a in S if int(a.get("word_count") or 0) >= 1200],
        "colleagues": [a for a in C if int(a.get("word_count") or 0) >= 1200],
    }

    def describe(name, definition, sets):
        return {
            "name": name,
            "definition": definition,
            "sides": {side: {
                "articles": len(members),
                "words": sum(len(a["body"].split()) for a in members),
                "article_ids": [a["slug"] for a in members],
                "rates_per_10k": measure(members),
                "final_sentence_profile": final_sentences(members),
            } for side, members in sets.items()},
        }

    matched = {
        "generated_by": {"script": "scripts/build_data.py",
                         "source": "articles/*.md, body text only"},
        "note": "Rates are occurrences per 10,000 words of body text. Set A is the "
                "honest test: same format, same years, same desk. Set B matches on "
                "length instead and is suggestive only — the colleagues' side is 37 "
                "pieces.",
        "sets": [
            describe("Set A — matched form",
                     "news briefs published 2012-2018, both sides", setA),
            describe("Set B — matched length",
                     "articles of 1,200+ words, any year, both sides", setB),
        ],
    }
    (OUT / "analysis-matched.json").write_text(
        json.dumps(matched, ensure_ascii=False, indent=1), encoding="utf-8")

    for f in ("metadata.json", "index.json", "analysis-matched.json"):
        print("  data/%-24s %7.1f KB" % (f, (OUT / f).stat().st_size / 1024))
    a, b = matched["sets"]
    for s in (a, b):
        print("  %s: %s" % (s["name"],
              ", ".join("%s %d pieces / %d words" % (k, v["articles"], v["words"])
                        for k, v in s["sides"].items())))


if __name__ == "__main__":
    build()
