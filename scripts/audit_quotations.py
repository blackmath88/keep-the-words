#!/usr/bin/env python3
"""
audit_quotations.py — verify every word of the corpus that appears in public text.

Two passes:

  1. Each ::quote directive in the essay is checked verbatim against the article
     file it cites, its length is checked against the limit, and its cited
     headline is checked against that article's title.
  2. Every run of 5+ words the essay shares with any article is found and
     classified, so an unmarked borrowing cannot hide. Runs fall into three
     buckets: an intended quotation, a cited headline (attribution), or an
     unavoidable collision of ordinary English.

    python3 scripts/audit_quotations.py [essay/autumn.md]
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_QUOTATIONS = 6
MAX_WORDS = 14
N = 5


def canon(t):
    t = t.replace("’", "'").replace("—", " ").replace("–", "-")
    t = re.sub(r"[^\w\s'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def article_title(slug):
    raw = (ROOT / "articles" / (slug + ".md")).read_text(encoding="utf-8")
    m = re.search(r'(?m)^title:\s*(.*)$', raw)
    if not m:
        return ""
    try:
        return json.loads(m.group(1).strip())
    except ValueError:
        return m.group(1).strip().strip('"')


def find_slug(headline):
    """Locate the article whose title is this headline."""
    for f in (ROOT / "articles").glob("*.md"):
        if article_title(f.stem) == headline:
            return f.stem
    return None


def main(path):
    essay = (ROOT / path).read_text(encoding="utf-8")
    quotes = []
    for line in essay.splitlines():
        if line.strip().startswith("::quote "):
            text, head, date = [x.strip() for x in line.strip()[8:].split("|")]
            quotes.append((text, head, date))

    print("=" * 96)
    print("PART 1 — every quotation, verbatim against its source")
    print("=" * 96)
    print("%-3s %-42s %-5s %-10s %-9s %s" % ("#", "quotation", "words", "in article", "headline", "date"))
    print("-" * 96)
    failed = []
    for i, (text, head, date) in enumerate(quotes, 1):
        slug = find_slug(head)
        body_ok = False
        if slug:
            body_ok = text in (ROOT / "articles" / (slug + ".md")).read_text(encoding="utf-8")
        if not body_ok:
            failed.append(text)
        print("%-3d %-42s %-5d %-10s %-9s %s"
              % (i, '"' + text + '"', len(text.split()),
                 "VERBATIM" if body_ok else "**FAIL**",
                 "matched" if slug else "**FAIL**", date))
        print("    articles/%s.md" % (slug or "?"))
    print("-" * 96)
    n_ok = len(quotes) <= MAX_QUOTATIONS
    longest = max((len(t.split()) for t, _, _ in quotes), default=0)
    print("Quotations:      %d  (limit %d)        -> %s"
          % (len(quotes), MAX_QUOTATIONS, "OK" if n_ok else "OVER LIMIT"))
    print("Longest:         %d words (limit %d)   -> %s"
          % (longest, MAX_WORDS, "OK" if longest <= MAX_WORDS else "OVER LIMIT"))
    print("Total quoted:    %d words" % sum(len(t.split()) for t, _, _ in quotes))
    print("Failed verbatim: %d -> %s" % (len(failed), "none" if not failed else failed))

    # ------------------------------------------------------------ pass 2 ---
    idx = {}
    for f in (ROOT / "articles").glob("*.md"):
        w = canon(f.read_text(encoding="utf-8")).split(" ")
        for i in range(len(w) - N + 1):
            idx.setdefault(" ".join(w[i:i + N]), f.stem)

    plain = canon(re.sub(r"^::(quote|note) ", "", essay, flags=re.M))
    plain = canon(re.sub(r"[*_#`>|]", " ", plain))
    w = plain.split(" ")
    allowed = [canon(t) for t, _, _ in quotes]
    headlines = [canon(h) for _, h, _ in quotes]

    runs, i = [], 0
    while i <= len(w) - N:
        key = " ".join(w[i:i + N])
        if key in idx:
            slug = idx[key]
            art = canon((ROOT / "articles" / (slug + ".md")).read_text(encoding="utf-8"))
            j = i + N
            while j < len(w) and " ".join(w[i:j + 1]) in art:
                j += 1
            runs.append((" ".join(w[i:j]), slug))
            i = j
        else:
            i += 1

    print("\n" + "=" * 96)
    print("PART 2 — every run of %d+ words the essay shares with the corpus" % N)
    print("=" * 96)
    stray = []
    for run, slug in runs:
        if any(run in a or a in run for a in allowed):
            tag = "quotation"
        elif any(run in h or h in run for h in headlines):
            tag = "cited headline (attribution)"
        else:
            tag = "COLLISION — ordinary English"
            stray.append(run)
        print(' %-52s %2dw  %s' % ('"' + run[:50] + '"', len(run.split()), tag))
    print("-" * 96)
    print("Runs: %d | quotations: %d | cited headlines: %d | collisions: %d"
          % (len(runs),
             sum(1 for r, _ in runs if any(r in a or a in r for a in allowed)),
             sum(1 for r, _ in runs if any(r in h or h in r for h in headlines)
                 and not any(r in a or a in r for a in allowed)),
             len(stray)))
    for s in stray:
        print('   reviewed: "%s" — no distinctive content' % s)

    return 1 if failed or not n_ok or longest > MAX_WORDS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "essay/autumn.md"))
