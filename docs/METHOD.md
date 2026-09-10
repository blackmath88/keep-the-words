# Method

How the corpus was built and how to rebuild it, what the numbers mean, and what
was got wrong on the way. With the scripts in `scripts/` and a network
connection you should be able to reproduce every figure in the essay and the
findings. Where you cannot, that is a defect in this document.

The corpus itself is not distributed. `articles/` is 1,903 recovered NFL.com
pieces, copyright NFL Enterprises and the writers; the pipeline rebuilds it from
the Internet Archive rather than copying it.

---

## Corrections — the things read wrong first

Kept at the top because it is the most transferable part of the document. Each
of these produced a confident, wrong number that survived until something forced
a second look.

### `/comments/` URLs misread as junk

NFL.com served each story under both `/news/story/<id>/article/<slug>` and
`/news/story/<id>/comments/<slug>`. The comments form was discarded as a
non-article URL. It is the same content ID, so discarding it did not just lose a
recovery route — it broke deduplication, and one article was being counted as
two. The harvester now captures `(article|comments)` in one expression and folds
both onto the content ID. 1,722 entries carry a `comments_url` as a result.

The honest postscript: the fallback route recovered nothing. Its value was the
deduplication.

### Rate-limit refusals read as dead captures

`429 Too Many Requests` and `503` from web.archive.org were being recorded as
*no capture exists*. They mean *ask again later*. Every such response was
permanently marking a live, archived article as lost. The request policy now
treats 429, 503, connection errors and timeouts as retryable behind a
5/10/20/40-second backoff, paces replay requests, and persists **every** attempt
to the entry's history — so a success after three refusals still shows the three
refusals.

The general form: a transport-layer refusal and a content-layer absence are
different facts, and code that collapses them deletes evidence.

### Byline parsing coupled to body extraction

Byline parsing ran only after body extraction succeeded, so an article whose
body failed to parse lost its byline too — even when the byline was sitting in a
`<meta>` tag that had parsed perfectly. Two articles were filed as "byline
unread" while their author was in HTML we already held. Byline parsing now runs
before body validation and stores its evidence independently. A re-audit of 253
cached pages confirmed the fix and found no further recoverable names.

When a stage can succeed on its own, do not make it a child of a stage that can
fail.

### The crew-versus-staff scope error

Articles were being sorted by *who wrote them* — Around The League podcast crew
on one side, other NFL.com staff on the other. That is a judgement about people
and it needed a whitelist of names nobody could justify. The archive's actual
structure is *where a piece was found*: everything discovered through the Around
The League section and pagination captures is `atl-blog`, Sessler credits
(including joint ones) are `sessler`, absent bylines are `unresolved`. A fact
about provenance rather than an opinion about staffing, and it needs no
whitelist.

### Three flaws in the first stylometry spec

The first specification was: 437 Sessler articles against 1,438 by colleagues —
*same beat, same publication, same era* — scored by log-odds with an informative
Dirichlet prior over uni-, bi- and trigrams, lowercased, punctuation stripped,
keeping terms in 3+ target articles. The first run's top 60 was almost entirely
artefact: `yds`, `rush`, `td`, `2022`, `rush td`, `pass yds`, `pct`, `ypa`, and
five fragments of *Follow Marc Sessler on Twitter*.

1. **"Same era" was false.** The control corpus stops in 2018; his output runs to
   2024. 181 of 437 target articles — 41% — sat in years with no control at all,
   so `2022`, `burrow` and `herbert` scored as his voice. Check the premise
   before trusting the design that rests on it.

2. **"Terms in 3+ articles" was assumed to stop template text.** It does not,
   because templates live in *articles*. Twenty NFL QB Index columns carry an
   identical stat table — 20% of all his words — each contributing some 640
   occurrences of `pass yds`. Twenty articles clear a three-article threshold
   effortlessly. Document-frequency weighting is what kills it; stripping the
   tables as furniture is what lets those columns keep their prose.

3. **"Lowercase" threw away the answer.** `Burrow` the quarterback and `burrow`
   the verb are the same token only because the pipeline lowercased before
   scoring. The corpus had already marked every proper noun for us, in the
   capitalisation, and the first thing we did was discard it — then spent two
   rounds trying to reconstruct it from an entity list and a 235,000-word system
   dictionary, both of which leak on exactly the names that matter, because
   `burrow`, `herbert`, `jackson`, `baker` and `tua` are ordinary English words.

   Normalisation is destruction. Do it as late as possible, and know what each
   step throws away.

### The collapse rule that fired backwards

The rule specified for collapsing nested n-grams was: *drop an n-gram if it is a
contiguous substring of a **higher-scoring** longer n-gram with a substantially
overlapping article set.* The shorter form is almost always the higher-scoring
member of a nested pair, because it also occurs on its own — `rash` 2.91,
`rash of` 2.91, `a rash` 2.90, `a rash of` 2.90. As written the rule collapses
none of them. Keeping the maximal form regardless of which scores higher is what
was meant, and collapses 1,918 terms rather than 789.

### The deks that nearly shipped

The public metadata payload carried every article's dek — 1,901 of them, roughly
a sentence of NFL.com copy each. Deks are editor-written published prose and are
not in the list of fields this project publishes. They were caught by the leak
check only after it was retargeted at article *bodies*; the first version
compared against whole article files, so the deks looked like metadata matching
metadata. They are now stripped from `public/` and from `data/metadata.json`.

The same pass caught a nine-word run of body text riding in the distinctive-terms
payload: `--maximal` grows a term along the token stream and had turned promo
boilerplate into a sentence fragment. Public terms are now capped at seven words.

---

## Pipeline

Run from the repository root, sequentially — several stages write `index.json`.

| Stage | Command | Consumes | Emits |
|---|---|---|---|
| 1. Harvest | `python3 scripts/harvest_index.py` | five seed URLs | `index.json`: article URLs, capture URLs, discovery provenance |
| 2. Frontier | `python3 scripts/harvest_index.py --frontier` | `index.json`, CDX wildcard queries | 1,365 further content IDs |
| 3. Bodies | `python3 scripts/fetch_bodies.py` | `index.json` | `articles/*.md`, `articles/_raw/*.html`, fetch history |
| 4. Analysis | `python3 scripts/analyse.py --voice --out data/analysis-voice.json` | `articles/*.md` | distinctive terms |
| 5. Reader payload | `python3 scripts/analyse.py --voice --keep 300 --out data/reader-terms.json` | as above | top 300 terms |
| 6. Data tier | `python3 scripts/build_data.py` | `articles/`, `index.json` | `data/metadata.json`, `data/index.json`, `data/analysis-matched.json` |
| 7. Reader | `python3 scripts/build_reader.py` | `articles/`, `data/reader-terms.json` | `reader/archive.html` |
| 8. Site | `python3 scripts/build_site.py --check` | `reader/`, `essay/`, `findings/`, `docs/`, `data/` | `public/`, `dist-private/payload.bin` |

Never delete `articles/` to restart. The fetcher skips existing Markdown and
records previous failures before retrying.

## Wayback specifics

**Earliest 200, not closest to now.** For each content ID the pipeline takes the
*earliest* capture that returned HTTP 200, not the capture nearest today. Later
captures of an NFL.com article are progressively more likely to be the
client-rendered page, whose server HTML carries the site's placeholder metadata
rather than the article's. The one broken title in the archive came from exactly
that: a 699 KB capture whose `og:title`, `twitter:title` and `<title>` were all
`| Latest NFL News, Analysis & Updates | NFL.com`, with only the `h1` carrying
the headline. A 263 KB earlier capture had it correct everywhere.

**CDX, not the availability API.** `archive.org/wayback/available` answers "is
there a capture near this timestamp", one URL at a time, and cannot be asked
what exists under a URL *prefix*. The CDX endpoint
(`web.archive.org/cdx/search/cdx`) takes `matchType=prefix`, `filter=statuscode:200`,
`collapse=urlkey` and `from`/`to`, and returns the whole capture history as
rows. Every discovery step here is a CDX query; the availability API would not
have found the pagination pages at all.

**Rate limits.** web.archive.org returns 429 and 503 under sustained load.
Replay requests (`/web/<ts>id_/<url>`) are paced with a fixed delay; CDX queries
are not. Both go through one retry policy: four attempts, 5/10/20/40-second
backoff, retrying on 429, 503, connection errors and timeouts, and giving up
immediately on anything else. Every attempt is appended to the entry's history,
successes and failures alike.

**`id_` suffix.** Replay URLs use the `id_` modifier
(`/web/20150605201612id_/http://...`) to get the original bytes without the
Wayback toolbar injected into the markup.

## The seed problem

The five seeds were the author page, the two writer/blog URLs, and the Around
The League section front. Between them they reached **six** articles published
2014–2018.

Everything else from those years lived on numbered pagination pages —
`around-the-league/1`, `around-the-league_11/959` — under names no scheme would
have predicted. One wildcard CDX query over `nfl.com/news/around-the-league*`
returned 54 monthly rows and 1,365 new content IDs, and took 2014–2018 from six
articles to **1,311 — 69% of the whole archive**.

Two related negative results, recorded so nobody repeats them:

- **All 1,826 mechanical daily-URL candidates returned no capture.** The
  2014–2018 section pages used a dated URL form, so every date in the span was
  enumerated and queried. Outcome: `no_capture` on all 1,826, without exception.
  Guessing URL shapes is not a substitute for asking CDX what it holds.
- **Comments were never captured, because they were never in the HTML.** Three
  archived comment views across three years and two platforms are all
  third-party widgets that rendered client-side — Pluck/SiteLife in 2010,
  Facebook Comments in 2012 and 2013 — with zero comment records in the markup.
  Not a claim that the discussions were empty; a claim that they are not in the
  archive.

## Stylometry

`scripts/analyse.py`. Deterministic: no model calls, no network. Re-running
produces a byte-identical file apart from `run_at`.

**Scoring.** Log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi
& Quinn 2008, *Fightin' Words*) over 1/2/3/4-grams, the prior pooled from both
corpora, so a term is distinctive only when it beats what the whole newsroom
does with it.

**Before scoring.** Newsroom furniture is removed: author sign-offs, house promo
blocks, QB Index stat tables (702 pipe-delimited rows), and NFL.com in-article
navigation modules (440 rows — these are why `nfc east and nfc` once scored as
voice). Proper nouns and bare four-digit years are removed. Text is lowercased
only after that.

**Proper nouns by case.** A token is a proper noun when it is capitalised away
from the start of a sentence in more than 70% of its occurrences, pooled over
both corpora. Sentence-initial words are excluded from both sides of the
fraction: they are capitalised for position, not for being names. A dropped
token becomes a *break* rather than a deletion — deleting it would make its
neighbours adjacent and invent phrases nobody wrote. 6,851 tokens qualify, and
no reported term contains one.

**Weighting.** Document frequency, not raw occurrence: a term counts once per
article. Terms are kept when they appear in three or more of his articles.
Nested forms collapse to the maximal phrase, and reported terms are grown along
the token stream until the article set stops holding.

**Why era-matching was wrong and matched-form right.** Restricting both corpora
to 2012–2018 was the first fix for the era gap. It worked, and it cost 41% of
his output — but the gap only ever leaked through *names and years*, and once
those are removed by case the full 437-article corpus scores clean, with higher
z-scores on the larger evidence base. Era-matching was treating a symptom.

The comparison that does the real work is different, and narrower.
`data/analysis-matched.json` defines it:

- **Set A — matched form.** His 229 news briefs from 2012–2018 (68,155 words)
  against their 1,315 from the same years (416,597 words). Same format, same
  length, same desk. Every claim in the essay rests on this.
- **Set B — matched length.** His 141 pieces of 1,200+ words against their 37.
  Suggestive only; 37 pieces cannot carry a claim.

Both sets ship with their member article ids and per-term rates, so any figure
can be recomputed without rebuilding the corpus.

## What the method cannot do

n-grams see words and short phrases. They do not see the shape of an argument.

The analysis can tell you that `cover man` appears in 47 of his articles and
none of his colleagues'. It cannot tell you that in *the once-physical and
reliable cover man* the borrowed register is doing the load-bearing work of the
sentence rather than decorating it. It cannot see a metaphor introduced,
deferred for two paragraphs and paid off. It cannot see that a 3,219-word game
preview opens on a 1907 newspaper poem.

Those readings are in `findings/voice-notes.md` and the essay, and they are
interpretation. The counting establishes that the words are his. What the words
are doing is an argument, and a reader is entitled to a different one.

The counting is also silent on everything the archive does not contain: 5
articles that no capture exists for, the comment threads, and whatever was
published outside the section and author pages the seeds and the frontier query
reached.
