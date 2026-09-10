#!/usr/bin/env python3
"""
analyse.py — Step 4 of the Sessler archive pipeline.

Which words are Marc Sessler's, rather than the beat's?

Compares two corpora already in the archive: articles with byline_verdict
"sessler" (target) against byline_verdict "other" (control). Same beat, same
publication — so in principle what separates them is voice, not subject.

Method: log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi
and Quinn 2008, "Fightin' Words"), over unigrams, bigrams and trigrams. The
prior is the pooled target+control corpus, so a term is only distinctive when
it beats what the whole newsroom does with it.

Three things in this archive defeat the plain comparison, and each has a flag:

  --era-matched       The corpora are NOT the same era. The control stops in
                      2018; the target runs to 2024. 181 of 437 target pieces
                      (41%) have no control to be compared against, so "2022",
                      "burrow" and "herbert" score as voice. Keeps the years
                      both corpora cover: 2012-2018, 256 target articles.
  --per-article       20 NFL QB Index pieces carry identical stat tables and
                      are 20% of all target words. Under raw term frequency
                      they put "yds", "rush td", "pass yds" and "ypa" in the
                      top 15. Weighting by document frequency ends that.
  --strip-boilerplate "Follow Marc Sessler on Twitter" sits in the body of 210
                      of 437 target pieces and 143 of 1,438 control pieces, so
                      the sign-off ranks as the writer's most personal phrase.

  --voice             All three. This is the fair comparison.

Fully deterministic. No model calls, no network. Writes analysis.json only —
nothing here touches article frontmatter, index.json or recovered bodies.

    python3 analyse.py                                   # as specified
    python3 analyse.py --voice --out analysis-voice.json # corpus-corrected
"""

import argparse
import collections
import glob
import json
import math
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

from build_reader import parse_md, norm_date

ROOT = Path(__file__).resolve().parent.parent
INDIR = str(ROOT / "articles")
OUT = str(ROOT / "data" / "analysis.json")
NGRAMS = (1, 2, 3)
NGRAMS_WIDE = (1, 2, 3, 4)   # --quadgrams: lets the collapse reach "a laundry list of"
MIN_TARGET_ARTICLES = 3      # a term must appear in at least this many target pieces
METHOD = "log-odds-ratio-informative-dirichlet-prior (Monroe, Colaresi & Quinn 2008)"

# ---------------------------------------------------------------- furniture
# Three kinds of non-prose sit inside the recovered body text. All of them read
# as "voice" to a bag-of-words method while being the opposite of it.

# 1. The author sign-off and house promo blocks. In 210 of 437 target bodies
#    and 143 of 1,438 control bodies.
BOILERPLATE = re.compile(
    r"(?im)^\s*(?:"
    r"follow .{0,60}? on twitter.*"
    r"|the latest (?:edition of )?.{0,4}?around the (?:nfl|league) podcast.*"
    r"|find more around the (?:nfl|league) content.*"
    r"|download the .{0,40}?podcast.*"
    r"|listen to the episode.*|subscribe on .*"
    r")\s*$")

# 2. NFL QB Index stat tables: one pipe-delimited row per quarterback, 702
#    lines in all, alternating with the prose that ranks him. Stripping the row
#    keeps the column; dropping the article would lose the column.
STAT_ROW = re.compile(r"(?im)^\s*\d{4}\s+(?:stats|final ranking)\s*:.*$")

# 3. NFL.com in-article navigation modules -- "ROSTER RESET > NFC: North |
#    East | West | South". These are why "east and nfc" scored as Sessler's
#    voice. Markdown list rows carrying arrow glyphs or pipe-separated links.
NAV_GLYPH = re.compile(r"[\u25b6\u25b7\u25b9\u25c0\u25b8]")
NUMERIC = re.compile(r"\A[\d,.\-]+\Z")


def _is_stat_row(line):
    """A pipe-delimited row that is mostly numbers, not a sentence."""
    tokens = line.split()
    if line.count("|") < 2 or not tokens:
        return False
    return sum(bool(NUMERIC.match(t)) for t in tokens) / len(tokens) > 0.25


def _is_nav(line):
    s = line.strip()
    if not s.startswith("- "):
        return False
    return bool(NAV_GLYPH.search(s)) or s.count("|") >= 2


def strip_furniture(text):
    """Remove sign-offs, stat tables and nav modules; keep every sentence."""
    text = BOILERPLATE.sub("", text)
    text = STAT_ROW.sub("", text)
    return "\n".join(l for l in text.split("\n")
                     if not _is_nav(l) and not _is_stat_row(l))

# Sentence boundaries, so bigrams and trigrams never straddle two sentences.
SENTENCE = re.compile(r"[.!?;:]+|\n+|\s--\s|\s—\s")
# Strip punctuation, keep case for now; an apostrophe inside a word is kept so
# that "don't" and "Sessler's" survive as themselves, not "dont"/"seslers".
TOKEN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)*")
YEAR = re.compile(r"\A(?:19|20)\d{2}\Z")
PROPER_RATIO = 0.70


def sentences(text):
    """Yield one case-preserving token list per sentence."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.replace("\u2019", "'").replace("`", "'")
    for chunk in SENTENCE.split(text):
        tokens = TOKEN.findall(chunk)
        if tokens:
            yield tokens


def case_profile(texts, ratio=PROPER_RATIO):
    """Tokens that are proper nouns, decided by the case the corpus itself uses.

    Burrow the quarterback and burrow the verb are one token only because we
    lowercase before scoring; the capitalisation already told us which is which.
    A token counts as a proper noun when it is capitalised in more than `ratio`
    of its occurrences away from the start of a sentence -- sentence-initial
    words are capitalised for position, not for being names, so they carry no
    evidence and are excluded from both sides of the fraction.
    """
    caps, total = collections.Counter(), collections.Counter()
    for text in texts:
        for tokens in sentences(text):
            for t in tokens[1:]:                 # skip the sentence-initial word
                key = t.lower()
                total[key] += 1
                if t[0].isupper():
                    caps[key] += 1
    return {w for w, n in total.items() if caps[w] / n > ratio}


def tokenize(text, proper=None):
    """Yield lowercased token lists, split at proper nouns and bare years.

    Dropping a token would let its neighbours become adjacent and invent
    n-grams that were never written, so a dropped token ends the run instead:
    no n-gram is ever formed across "Burrow" or "2022".
    """
    for tokens in sentences(text):
        run = []
        for t in tokens:
            low = t.lower()
            if proper is not None and (low in proper or YEAR.match(low)):
                if run:
                    yield run
                run = []
            else:
                run.append(low)
        if run:
            yield run


def ngrams(text, sizes=None, proper=None):
    """Every n-gram of the configured sizes in one article, in order."""
    for tokens in tokenize(text, proper):
        for n in (sizes or NGRAMS):
            for i in range(len(tokens) - n + 1):
                yield " ".join(tokens[i:i + n])


ERA = {}


def load(indir=INDIR, era_matched=False):
    """Split the archive into the Sessler target corpus and the control.

    The two corpora are the same beat and publication but NOT the same era:
    the control stops in 2018 while the target runs to 2024, so 41% of target
    articles have no control to be compared against. --era-matched keeps only
    the years both corpora cover, which is what makes the comparison fair.
    """
    target, control = [], []
    for path in sorted(glob.glob(os.path.join(indir, "*.md"))):
        meta = parse_md(path)
        if not meta:
            continue
        verdict = meta.get("byline_verdict")
        if verdict == "sessler":
            target.append(meta)
        elif verdict == "other":
            control.append(meta)
    if era_matched:
        years = lambda c: {norm_date(m.get("date", ""))[:4] for m in c} - {""}
        shared = years(target) & years(control)
        keep = lambda c: [m for m in c if norm_date(m.get("date", ""))[:4] in shared]
        target, control = keep(target), keep(control)
        ERA["years"] = "%s-%s" % (min(shared), max(shared)) if shared else ""
    else:
        span = sorted({norm_date(m.get("date", ""))[:4] for m in target + control} - {""})
        ERA["years"] = "%s-%s" % (span[0], span[-1]) if span else ""
    def span_of(c):
        ys = sorted({norm_date(m.get("date", ""))[:4] for m in c} - {""})
        return "%s-%s" % (ys[0], ys[-1]) if ys else ""
    ERA["target_years"], ERA["control_years"] = span_of(target), span_of(control)
    return target, control


def tally(corpus, per_article=False, clean=False, sizes=None, proper=None):
    """Term -> weight, and term -> the article ids containing it.

    per_article counts each term once per article (document frequency). Without
    it, 20 QB Index pieces carrying identical stat tables contribute ~640
    occurrences of "pass yds" apiece and swamp everything a person actually
    wrote.
    """
    counts = collections.Counter()
    where = collections.defaultdict(list)
    for meta in corpus:
        body = meta.get("body", "")
        if clean:
            body = strip_furniture(body)
        seen = collections.Counter(ngrams(body, sizes, proper))
        for term, n in seen.items():
            counts[term] += 1 if per_article else n
        for term in sorted(seen):
            where[term].append(meta["slug"])
    return counts, where


def log_odds(target_counts, control_counts, vocabulary):
    """Monroe et al.'s z-scored log-odds ratio, restricted to `vocabulary`.

    The prior is the pooled corpus: alpha_w = y_w(target) + y_w(control).
    delta_w  = log( (y_w^t + a_w) / (n^t + a0 - y_w^t - a_w) )
             - log( (y_w^c + a_w) / (n^c + a0 - y_w^c - a_w) )
    var_w    = 1/(y_w^t + a_w) + 1/(y_w^c + a_w)
    z_w      = delta_w / sqrt(var_w)
    """
    prior = {w: target_counts[w] + control_counts[w] for w in vocabulary}
    # a0 and the corpus totals are taken over the analysed vocabulary, so that
    # the denominators describe the same term space the ratio is computed in.
    a0 = sum(prior.values())
    n_target = sum(target_counts[w] for w in vocabulary)
    n_control = sum(control_counts[w] for w in vocabulary)
    scores = {}
    for w in vocabulary:
        a = prior[w]
        yt, yc = target_counts[w], control_counts[w]
        odds_t = (yt + a) / (n_target + a0 - yt - a)
        odds_c = (yc + a) / (n_control + a0 - yc - a)
        delta = math.log(odds_t) - math.log(odds_c)
        var = 1.0 / (yt + a) + 1.0 / (yc + a)
        scores[w] = delta / math.sqrt(var)
    return scores


def collapse_nested(ranked, scores, where, jaccard=0.8, strict=False):
    """Collapse "a rash of / rash of / a rash / rash" down to one habit.

    Drops an n-gram when it is a contiguous sub-sequence of a longer n-gram
    covering substantially the same target articles (Jaccard over the id sets),
    keeping the maximal form.

    strict=True additionally requires the longer form to score higher, which is
    the literal rule but fires rarely: a shorter n-gram is almost always the
    higher-scoring of a nested pair, because it also occurs on its own.
    """
    sets = {w: set(where[w]) for w in ranked}
    drop = set()
    for w in ranked:
        parts = w.split()
        if len(parts) < 2:
            continue
        for n in range(1, len(parts)):
            for i in range(len(parts) - n + 1):
                sub_term = " ".join(parts[i:i + n])
                if sub_term not in sets or sub_term in drop:
                    continue
                if strict and scores[sub_term] >= scores[w]:
                    continue
                union = len(sets[sub_term] | sets[w])
                if union and len(sets[sub_term] & sets[w]) / union > jaccard:
                    drop.add(sub_term)
    return [w for w in ranked if w not in drop], drop


def maximalise(ranked, scores, where, corpus, sizes, clean, proper=None,
               jaccard=0.8, limit=12):
    """Grow each term into the longest phrase covering ~the same articles.

    The n-gram ceiling cuts long phrases into overlapping pieces: "mary kay
    cabot of", "kay cabot of the", "cabot of the plain", "of the plain dealer"
    are one attribution reported four times, and no one of them contains
    another, so the substring collapse cannot merge them. This walks the actual
    token stream outward from each term instead, which is bounded by the
    articles the term already occurs in.
    """
    sentences = {}
    for meta in corpus:
        body = strip_furniture(meta["body"]) if clean else meta["body"]
        sentences[meta["slug"]] = [tuple(t) for t in tokenize(body, proper)]

    def sites(phrase, ids):
        """Every (article, sentence, offset) where `phrase` occurs."""
        n, out = len(phrase), []
        for aid in ids:
            for si, sent in enumerate(sentences[aid]):
                for i in range(len(sent) - n + 1):
                    if sent[i:i + n] == phrase:
                        out.append((aid, si, i))
        return out

    def grow(phrase, spots, base, left):
        while len(phrase) < limit:
            nxt = collections.Counter()
            for aid, si, i in spots:
                sent = sentences[aid][si]
                j = i - 1 if left else i + len(phrase)
                if 0 <= j < len(sent):
                    nxt[sent[j]] += 1
            if not nxt:
                return phrase, spots
            token = min(nxt.items(), key=lambda kv: (-kv[1], kv[0]))[0]
            kept = [(a, si, i - 1 if left else i) for a, si, i in spots
                    if (lambda sent, j: 0 <= j < len(sent) and sent[j] == token)
                       (sentences[a][si], i - 1 if left else i + len(phrase))]
            ids = {a for a, _, _ in kept}
            if not ids or len(ids & base) / len(ids | base) <= jaccard:
                return phrase, spots
            phrase = (token,) + phrase if left else phrase + (token,)
            spots = kept
        return phrase, spots

    best, order = {}, []
    for w in ranked:
        base = set(where[w])
        phrase = tuple(w.split())
        spots = sites(phrase, base)
        if not spots:
            continue
        phrase, spots = grow(phrase, spots, base, left=False)
        phrase, spots = grow(phrase, spots, base, left=True)
        key = " ".join(phrase)
        if key not in best or scores[w] > best[key][1]:
            if key not in best:
                order.append(key)
            best[key] = (w, scores[w])
    # Report each maximal phrase once, under the best score among its pieces.
    return sorted(order, key=lambda k: (-best[k][1], k)), {k: best[k] for k in order}


def analyse(indir=INDIR, out=OUT, top=60,
            era_matched=False, per_article=False, clean=False,
            collapse=False, strict_collapse=False, keep=None, quadgrams=False,
            maximal=False, maximal_pool=600, drop_proper=False):
    target, control = load(indir, era_matched)
    if not target or not control:
        raise SystemExit("need both a target and a control corpus; found %d/%d"
                         % (len(target), len(control)))
    sizes = NGRAMS_WIDE if quadgrams else NGRAMS
    proper = None
    if drop_proper:
        # Decided over both corpora at once: whether a token is a name is a
        # property of the language, not of who is writing.
        proper = case_profile((strip_furniture(m["body"]) if clean else m["body"])
                              for m in target + control)
    target_counts, target_where = tally(target, per_article, clean, sizes, proper)
    control_counts, _ = tally(control, per_article, clean, sizes, proper)

    vocabulary = sorted(w for w, ids in target_where.items()
                        if len(ids) >= MIN_TARGET_ARTICLES)
    scores = log_odds(target_counts, control_counts, vocabulary)
    # Sort by z descending, then by term, so the file is byte-stable per corpus.
    ranked = sorted(vocabulary, key=lambda w: (-scores[w], w))
    dropped = set()
    if collapse:
        ranked, dropped = collapse_nested(ranked, scores, target_where,
                                          strict=strict_collapse)
    merged = {}
    if maximal:
        cut = max(maximal_pool, keep or 0, top)
        head, tail = ranked[:cut], ranked[cut:]
        head, merged = maximalise(head, scores, target_where, target,
                                  sizes, clean, proper)
        # Terms below the pool keep their collapsed form; the file stays a
        # complete record of the vocabulary rather than just the reported head.
        ranked = head + [w for w in tail if w not in merged]
    if keep:
        ranked = ranked[:keep]

    result = {
        "generated_by": {
            "method": METHOD,
            "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "corpus": {"target_n": len(target), "control_n": len(control)},
        "parameters": {
            "ngrams": list(sizes),
            "min_target_articles": MIN_TARGET_ARTICLES,
            "target": "byline_verdict == sessler",
            "control": "byline_verdict == other",
            "text": "article body only (titles and deks are editor-written)",
            "era_matched": era_matched,
            "era_years": ERA.get("years", ""),
            "target_years": ERA.get("target_years", ""),
            "control_years": ERA.get("control_years", ""),
            "weighting": "document frequency" if per_article else "term frequency",
            "boilerplate_stripped": clean,
            "proper_nouns_dropped": drop_proper,
            "proper_noun_tokens": len(proper) if proper is not None else 0,
            "proper_noun_rule": ("capitalised away from sentence start in >%d%% "
                                 "of occurrences; bare 4-digit years also dropped"
                                 % (PROPER_RATIO * 100)) if drop_proper else None,
            "collapsed_nested_ngrams": collapse,
            "collapse_rule": ("maximal form, Jaccard > 0.8"
                              + (", longer must outscore" if strict_collapse else ""))
                             if collapse else None,
            "vocabulary_size": len(vocabulary),
            "collapsed_away": len(dropped),
            "terms_reported": len(ranked),
        },
        "terms": [{"term": w,
                   "n_target": target_counts[merged.get(w, (w,))[0]],
                   "n_control": control_counts[merged.get(w, (w,))[0]],
                   "z": round(merged[w][1] if w in merged else scores[w], 6),
                   "articles": target_where[merged.get(w, (w,))[0]]}
                  for w in ranked],
    }
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    os.replace(out + ".tmp", out)

    print("target=%d control=%d vocabulary=%d (terms in %d+ target articles)"
          % (len(target), len(control), len(vocabulary), MIN_TARGET_ARTICLES))
    print("era_matched=%s weighting=%s boilerplate_stripped=%s"
          % (era_matched, "df" if per_article else "tf", clean))
    print("wrote %s (%.1f MB)\n" % (out, os.path.getsize(out) / 1e6))
    print("top %d distinctive terms\n%s" % (top, "-" * 74))
    print("  # %-34s %8s %8s %9s %7s" % ("term", "target", "control", "z", "arts"))
    for i, w in enumerate(ranked[:top], 1):
        src = merged.get(w, (w,))[0]
        print("%3d %-34s %8d %8d %9.2f %7d"
              % (i, w[:34], target_counts[src], control_counts[src],
                 merged[w][1] if w in merged else scores[w],
                 len(target_where[src])))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="indir", default=INDIR)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--era-matched", action="store_true",
                    help="keep only the years both corpora cover (2012-2018)")
    ap.add_argument("--per-article", action="store_true",
                    help="weight by document frequency, not raw occurrences")
    ap.add_argument("--strip-boilerplate", action="store_true",
                    help="drop author sign-offs and house promo lines")
    ap.add_argument("--collapse", action="store_true",
                    help="keep only the maximal form of nested n-grams")
    ap.add_argument("--strict-collapse", action="store_true",
                    help="collapse only when the longer form also scores higher")
    ap.add_argument("--drop-proper", action="store_true",
                    help="drop proper nouns (detected by case) and bare years")
    ap.add_argument("--maximal", action="store_true",
                    help="grow reported terms to their maximal phrase")
    ap.add_argument("--quadgrams", action="store_true",
                    help="also count 4-grams, so nested forms collapse further")
    ap.add_argument("--keep", type=int, default=None,
                    help="write only the top N terms (for the reader payload)")
    ap.add_argument("--voice", action="store_true",
                    help="the fair-comparison preset")
    args = ap.parse_args()
    analyse(args.indir, args.out, args.top,
            era_matched=args.era_matched,
            per_article=args.per_article or args.voice,
            clean=args.strip_boilerplate or args.voice,
            collapse=args.collapse or args.voice,
            strict_collapse=args.strict_collapse,
            keep=args.keep, quadgrams=args.quadgrams or args.voice,
            maximal=args.maximal or args.voice,
            drop_proper=args.drop_proper or args.voice)
