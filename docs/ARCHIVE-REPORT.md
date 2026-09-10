# Marc Sessler archive — method and record

A personal archive of NFL.com writing by Marc Sessler and the newsroom around
him, recovered one Wayback capture at a time, plus a deterministic analysis of
what separates his prose from theirs. Coverage is incomplete by construction:
what survives is what the Internet Archive happened to capture.

This section is the closing record. The dated working log follows it.

## What was recovered

| | |
|---|---:|
| Articles recovered | **1,903** |
| Words | 1,050,201 (median article 321) |
| From Wayback captures | 1,715 |
| From live nfl.com | 188 |
| HTTP 200 on every recovered body | 1,903 |

| Discovery route | Articles |
|---|---:|
| Section / pagination captures | 1,715 |
| Author-page captures | 188 |

| Scope | Articles | | Byline verdict | Articles |
|---|---:|---|---|---:|
| `atl-blog` | 1,456 | | `other` | 1,438 |
| `sessler` | 437 | | `sessler` | 437 |
| `unresolved` | 10 | | `none-written` | 18 |
| | | | `unparsed` | 10 |

Sessler's own 437 pieces are 463,143 words. `none-written` is the ATN podcast
notes, which carry no byline because none was ever written; `unparsed` is
reserved for genuine byline-parse failures, of which 10 remain.

| Format | Articles |
|---|---:|
| news brief | 1,569 |
| column | 257 |
| ranking | 54 |
| podcast-note | 21 |
| obituary | 2 |

## The masthead

Forty-two distinct credits. Counts are article credits, so a joint byline
appears under each of its names as well as in its own row.

| Writer | Articles | | Writer | Articles |
|---|---:|---|---|---:|
| Marc Sessler | 434 | | Andie Hagemann | 5 |
| Kevin Patra | 347 | | Simon Samano | 4 |
| Dan Hanzus | 199 | | Lakisha Jackson | 4 |
| Gregg Rosenthal | 184 | | Adam Maya | 3 |
| Chris Wesseling | 164 | | Jason B. Hirschhorn | 3 |
| Herbie Teope | 75 | | Manouk Akopyan | 2 |
| Conor Orr | 71 | | Mark E. Ortega | 2 |
| Jeremy Bergman | 67 | | Matt Clarida | 2 |
| Kareem Copeland | 56 | | Tyler Dragon | 1 |
| Austin Knoblauch | 50 | | Dave Dameshek | 1 |
| Nick Shook | 49 | | Marcas Grant | 1 |
| Brian McIntyre | 23 | | Grant Gordon | 1 |
| Edward Lewis | 21 | | Ian Rapoport | 1 |
| Mike Coppinger | 14 | | Ralph Warner | 1 |
| Max Meyer | 13 | | Matt Harmon | 1 |

Generic house credits, kept distinct from named writers because the individual
authors are unresolved: **Around The NFL staff** 58, **Around the NFL staff** 6,
**Around the League** 1, **Around The NFL Team** 1, **Around The NFL** 1. The
capitalisation variants are preserved as they were published rather than
normalised — they are evidence of how the desk signed its own work.

Joint credits, all seven:

| Credit | Articles |
|---|---:|
| Gregg Rosenthal and Chris Wesseling | 3 |
| Gregg Rosenthal, Chris Wesseling and Kevin Patra | 1 |
| Gregg Rosenthal, Marc Sessler, Dan Hanzus and Kevin Patra | 1 |
| Marc Sessler and Gregg Rosenthal | 1 |
| Gregg Rosenthal and Marc Sessler | 1 |
| Ian Rapoport and Albert Breer | 1 |
| Lyle, the Around The League intern | 1 |

434 solo Sessler credits plus the 3 joint credits naming him make the 437 in the
`sessler` bucket.

## Publication-year coverage, and the 2014–2018 gap

Years are parsed from each article's own published date, not from the capture
timestamp. All 1,903 have a parsed date.

| Year | From the 5 seeds | Added by frontier expansion | Total |
|---|---:|---:|---:|
| 2010 | 1 | 0 | 1 |
| 2011 | 0 | 0 | **0** |
| 2012 | 227 | 33 | 260 |
| 2013 | 124 | 25 | 149 |
| 2014 | 0 | 348 | 348 |
| 2015 | 0 | 175 | 175 |
| 2016 | 1 | 100 | 101 |
| 2017 | 1 | 157 | 158 |
| 2018 | 4 | 525 | 529 |
| 2019 | 55 | 0 | 55 |
| 2020 | 49 | 0 | 49 |
| 2021 | 33 | 0 | 33 |
| 2022 | 30 | 0 | 30 |
| 2023 | 14 | 0 | 14 |
| 2024 | 1 | 0 | 1 |
| | 540 | 1,363 | 1,903 |

**The original five seeds reached 6 articles published between 2014 and 2018.
After frontier expansion there are 1,311 — 69% of the whole archive.** Sessler's
own 2014–2018 output went from 6 pieces to 176 the same way.

The gap was never a gap in the record; it was a gap in the seed list. The author
page captures cover 2019 onward and the early blog era, and the bare
`news/around-the-league` section captures cover 2012–13. Everything in between
lived on numbered pagination pages (`around-the-league/1`,
`around-the-league_11/959`) that no seed named. One CDX wildcard query over
`nfl.com/news/around-the-league*` returned 54 monthly rows and 1,365 new content
IDs. 2011 remains genuinely empty.

Capture years are not publication years, and this table is publication years.

## What was lost, and how

Of 1,936 index entries: 1,903 recovered, 22 never article candidates (15 section
indexes, 5 navigation links, 2 pagination stubs — correctly classified and not
fetched), and 11 failures.

The failures are not one bucket. A thin body is a page we hold that did not
parse; a no-capture is a page nobody ever archived. Averaging them would hide
the only permanent losses in the set.

| Class | Count | Nature |
|---|---:|---|
| `failed:no-capture` | **5** | **Permanent. No capture exists anywhere.** |
| `failed:thin-body` | 3 | We hold the HTML; extraction fell short |
| `failed:request` | 3 | Pagination navigation stubs, not articles |

Earlier passes resolved 7 further `failed:thin-body` cases from cache with
`--repair`; those are recovered and counted in the 1,903.

Of the 6 remaining thin-body and request failures, 4 are navigation furniture
("Next Articles", "Previous Articles", "Back to top") that should never have
entered the queue. Only 2 are real articles we hold but could not parse:

- `Rodgers calls out 'idiot trolls' over grape…` (`0ap3000000434461`)
- `Eagles LB Nigel Bradham suspended for one g…` (`0ap3000000939057`)

### The five that are simply gone

All five were discovered as links on `nfl.com/news/around-the-league` captures,
so we know they were published. No capture of the article itself exists.

| Content ID | Slug |
|---|---|
| `09000d5d82af4df3` | `vikings-john-carlson-sprained-mcl-…` |
| `0ap1000000056925` | `roberto-wallace-chris-hogan-among-…` |
| `0ap1000000057154` | `san-diego-chargers-finalize-roster…` |
| `0ap1000000057351` | `eagles-acquire-safety-david-sims-f…` |
| `0ap1000000134097` | `chris-culliver-will-work-with-gay-…` (49ers CB Culliver to work with gays and lesbians) |

Four of the five are from the same 2012 preseason roster-cutdown window. This is
the archive's floor: 5 articles out of 1,908 known to exist, 0.26%, that no
amount of further work can recover.

## Negative results kept as findings

Work that produced nothing is recorded here because "we looked and there was
nothing" is a different and more useful statement than silence.

**Comments were never captured, because they were never in the HTML.** Three
archived comment views were inspected by hand across three years and two
platforms. All three are third-party widgets that rendered client-side:
Pluck/SiteLife on the 2010 page (`#comments-list` holds template placeholders),
Facebook Comments on the 2012 and 2013 pages (`.fb-comments` is an empty
container). Zero comment records are present in any of them. This is not a claim
that the live discussions were empty — it is a claim that the discussion is not
in the archive and no extraction code could find it there. No comment-extraction
code was written on the strength of it. 1,722 index entries retain their
`comments_url` purely as an alternate recovery route for the article body; in
the end no recovered body came through that route.

**All 1,826 mechanical daily-URL candidates returned no capture.** The 2014–2018
section pages used a dated URL form, so every date in that span was enumerated
and queried — `around-the-league/01-01-2014` through the end of 2018, covered by
five year-filtered prefix CDX queries with `collapse=urlkey`, season dates
prioritised. Outcome: `no_capture` on all 1,826, without exception. Guessing URL
shapes is not a substitute for asking CDX what it actually holds; the wildcard
query that did work found the pages under names no scheme would have predicted.

**Link density cannot detect page furniture in this corpus.** The standard test
for a section landing page fetched as an article is that its body is mostly link
text. Every body in this archive contains exactly zero Markdown link markup —
the extractor strips destinations — so the measure is 0.00 for all 1,903 and
discriminates nothing. Recorded so the test is not designed again from scratch.
Three other signals were swept instead (generic title strings, short-line ratio,
entity-per-word ratio) and found no furniture at all: the one entry that looked
like a section page was a genuine 1,345-word column with a broken title.

## Corrections — the things read wrong first

The most transferable part of this record. Each of these produced a confident,
wrong number that survived until something forced a second look.

### 1. `/comments/` URLs misread as junk

NFL.com served the same story under `/news/story/<id>/article/<slug>` and
`/news/story/<id>/comments/<slug>`. The comments form was initially discarded as
a non-article URL. It is not junk: it is the same content ID, and treating it as
junk both loses a recovery route and — worse — breaks deduplication, because the
two forms are one article and were being counted as two. The harvester's URL
pattern now captures `(article|comments)` in one expression and folds both onto
the content ID. 1,722 entries carry a `comments_url` as a result.

The honest postscript: the fallback it enabled recovered nothing. Its real value
was the deduplication, not the second route.

### 2. Rate-limit refusals misread as dead captures

`429 Too Many Requests` and `503` from web.archive.org were being recorded as
"no capture exists." They mean "ask again later." Every such response was
permanently marking a live, archived article as lost. The request policy now
treats 429, 503, connection errors and timeouts as retryable behind a 5/10/20/40
second backoff, paces replay requests, and — importantly — persists *every*
attempt to the entry's history, so a success after three refusals still shows
the three refusals. Failed attempts remain in the record even when a later retry
succeeds; otherwise the archive would flatter itself.

The general form of this error: a transport-layer refusal and a
content-layer absence are different facts, and code that collapses them will
quietly delete evidence.

### 3. Byline parsing coupled to body extraction

Byline parsing ran only after body extraction succeeded. So an article whose
body failed to parse lost its byline too — even when the byline was sitting in a
`<meta>` tag that had parsed perfectly. Two articles were classified "byline
unread" on those grounds while their author was in the HTML we already held.

Byline parsing now runs before body validation and stores its evidence
independently, so the two facts fail independently. A cache re-audit of 253
saved pages confirmed the fix and found no further recoverable names.

The general form: when a pipeline stage can succeed on its own, do not make it a
child of a stage that can fail.

### 4. The crew-versus-staff scope error

Recovered articles were being sorted by *who the writer was* — Around The League
podcast crew on one side, other NFL.com staff on the other. That is a judgement
about people, and it required a whitelist of names that nobody could justify.

The archive's actual structure is about *where a piece was found*: everything
discovered through the Around The League section and pagination captures is
`atl-blog`, regardless of who filed it; Sessler credits, including joint ones,
are `sessler`; absent bylines are `unresolved`. This is a fact about provenance
rather than an opinion about staffing, and it needs no whitelist. All 244
existing records were migrated without touching their bodies.

The general form: prefer the classification your evidence actually supports over
the one you wish it supported.

### 5. Three flaws in the first stylometry spec

The first specification for the distinctive-term analysis was: Sessler's 437
articles against 1,438 by colleagues — "same beat, same publication, same era —
so what surfaces is voice, not subject" — scored by log-odds with an informative
Dirichlet prior over unigrams, bigrams and trigrams, lowercased, punctuation
stripped, keeping terms in 3+ target articles.

Three things in that paragraph were wrong, and the first run's top 60 was almost
entirely artefact: `yds`, `rush`, `td`, `2022`, `rush td`, `pass yds`, `pct`,
`ypa`, and five fragments of *Follow Marc Sessler on Twitter*.

**"Same era" was false.** The control corpus stops in 2018; his own output runs
to 2024. 181 of 437 target articles — 41% — sat in years with zero control
articles, so `2022`, `burrow` and `herbert` scored as his voice. The fix at the
time was to restrict both sides to 2012–2018, which worked but cost 41% of his
output. Check the premise before trusting the design that rests on it.

**"Terms in 3+ target articles" was assumed to be enough to stop template
text.** It is not, because templates live in *articles*, not in stray sentences.
Twenty NFL QB Index columns carry an identical stat table — 20% of all his words
— and each contributes some 640 occurrences of `pass yds`. Twenty articles clear
a three-article threshold effortlessly. Weighting by document frequency instead
of raw occurrence is what actually kills it; stripping the tables as furniture is
what lets those columns keep their prose. A frequency floor is not a template
defence.

**"Lowercase" threw away the answer.** This is the sharpest of the three.
`Burrow` the quarterback and `burrow` the verb are the same token only because
the pipeline lowercased before scoring. The corpus had already marked every
proper noun for us, in the capitalisation, and the first thing we did was
discard it — then spent two rounds trying to reconstruct it with an entity list
and a 235,000-word system dictionary, both of which leak on exactly the names
that matter, because `burrow`, `herbert`, `jackson`, `baker` and `tua` are
ordinary English words.

Deciding proper nouns from case instead — capitalised away from sentence start
in more than 70% of occurrences, pooled over both corpora — removes 6,851 tokens
and yields a top 60 with no subject terms in it at all. It also made the era
restriction unnecessary: the era gap had only ever leaked through *names and
years*, so once those are gone the full 437-article corpus is usable and the
z-scores rise on the larger evidence base. A workaround that costs 41% of the
data is a sign the diagnosis was wrong.

The general form: normalisation is destruction. Do it as late as possible, and
know what each step throws away.

### A fourth, from the collapse rule

The rule specified for collapsing nested n-grams was: *drop an n-gram if it is a
contiguous substring of a **higher-scoring** longer n-gram with a substantially
overlapping article set.* It fires backwards. The shorter form is almost always
the higher-scoring member of a nested pair, because it also occurs on its own —
`rash` 2.91, `rash of` 2.91, `a rash` 2.90, `a rash of` 2.90. The rule as
written collapses none of them. Keeping the maximal form regardless of which
scores higher is what was meant, and it collapses 1,918 terms rather than 789.

## The distinctive-term analysis

`analyse.py`, deterministic, no model calls and no network. His 437 articles
(2012–2024) against 1,438 by colleagues (2012–2018): same beat, same
publication. Log-odds ratio with an informative Dirichlet prior (Monroe,
Colaresi & Quinn 2008) over 1/2/3/4-grams, prior pooled from both corpora.

Before scoring: newsroom furniture removed (author sign-offs, house promos, QB
Index stat tables, in-article navigation modules); proper nouns and bare years
removed by case; text lowercased only after that. Weighted by article rather
than by occurrence. Terms kept in 3+ of his articles; nested forms collapsed to
the maximal phrase. 39,671 terms in vocabulary, 32,442 reported.

| # | term | his articles | colleagues' | z |
|---:|---|---:|---:|---:|
| 1 | `league wide` | 77 | 3 | 5.11 |
| 2 | `autumn` | 78 | 4 | 5.07 |
| 3 | `rounder` | 88 | 11 | 4.89 |
| 4 | `inside a` | 69 | 3 | 4.81 |
| 5 | `tumble` | 66 | 2 | 4.79 |
| 6 | `that saw` | 76 | 8 | 4.66 |
| 7 | `club` | 113 | 31 | 4.50 |
| 8 | `finest` | 69 | 7 | 4.46 |
| 9 | `a flock of` | 53 | 0 | 4.46 |
| 10 | `chaos` | 56 | 2 | 4.38 |
| 11 | `cover man` | 47 | 0 | 4.20 |
| 12 | `entirely` | 70 | 11 | 4.17 |
| 13 | `play caller` | 74 | 14 | 4.11 |
| 14 | `year's` | 135 | 53 | 4.10 |
| 15 | `rough and tumble` | 47 | 1 | 4.09 |
| 16 | `rugged` | 47 | 1 | 4.09 |
| 17 | `operating` | 58 | 6 | 4.08 |
| 18 | `passer` | 180 | 87 | 4.07 |
| 19 | `first rounder` | 53 | 4 | 4.05 |
| 20 | `juicy` | 53 | 4 | 4.05 |

The full 60 and the rest are in `analysis-voice.json`.

What this is not: these are not unusual words in English. They are unusual words
for him among people writing the same thing in the same place. `autumn` in 78 of
his pieces against 4 of theirs is not a rare word — it is a choice nobody else
on that desk was making.

| File | What it is |
|---|---|
| `analysis-voice.json` | **Primary.** Full corpus, proper nouns dropped by case |
| `analysis-voice-eramatched.json` | Alternative. 2012–2018 both sides, 256 target articles |
| `analysis.json` | The naive first method, kept as the record of what it produced |
| `reader-terms.json` | Collapsed top 300 with article ids, embedded in the reader |

## Reproducing

```sh
.venv/bin/python harvest_index.py            # seed captures
.venv/bin/python harvest_index.py --frontier # wildcard CDX expansion
.venv/bin/python fetch_bodies.py             # bodies and bylines
.venv/bin/python analyse.py --voice --out analysis-voice.json
.venv/bin/python analyse.py --voice --keep 300 --out reader-terms.json
.venv/bin/python build_reader.py
```

Run sequentially, never concurrently — several write `index.json`. Never delete
`articles/` to restart. Failed attempts stay in the history even when a later
retry succeeds.

---

# Working log

The dated record of how the above was arrived at, oldest first.

Analysis by GPT-6 (Codex), 2026-09-07. This report is separate from article metadata. Counts below describe observed results, not assumed author or publication-year coverage.

## Comments probe

Three archived comments views were inspected manually; no comment-extraction code was written.

| Content ID | Requested capture | Result |
| --- | --- | --- |
| 09000d5d81c2d42c | 20101130201652 | Pluck/SiteLife; `#comments-list` contains template placeholders, no rendered comments |
| 0ap1000000069298 | 20121005170455 | Facebook Comments; empty `.fb-comments` container |
| 0ap1000000156100 | 20130402084157 | Facebook Comments; empty `.fb-comments` container |

All three are widget-driven. Zero actual comment records are present in the inspected HTML; this is not a claim that the live discussions had zero comments. The two later pages also include Pluck scripts, but their actual comment container is the Facebook widget. The oldest page's publication metadata is 2010-11-28, despite its later harvested slug referring to 2011.

## Frontier expansion

The four requested wildcard CDX queries were completed and reported before promotion. `nfl.com/news/around-the-league*` returned 54 monthly rows: 2014: 0, 2015: 9, 2016: 4, 2017: 9, 2018: 32. The other three patterns returned no rows for 2014–2018. `SEEDS` was not changed.

The one-hop frontier parsed all 54 section/pagination captures plus two captures of already-known daily pages. It added 1,365 legacy content IDs: 1,722 legacy IDs total, 1,936 index entries, 1,916 fetch-eligible entries. No frontier capture remained failed. Failures preceding successful retries remain recorded.

All 1,826 mechanical daily candidates across 2014–2018 returned no capture. Five year-filtered prefix CDX queries covered the candidate set with `collapse=urlkey`; season dates were prioritized within the candidate lists. Per-candidate outcomes, query evidence, capture histories, and summary counts are retained under `index.json.frontier`.

Capture years are not publication years. The body stage must establish whether these additions fill the publication-year gap and which writers filed them.

## Deterministic enrichment

Player matching uses downloaded [nflverse season rosters](https://github.com/nflverse/nflverse-rosters) for 2012–2024: 13 CSV files and 10,193 normalized aliases. Teams use a closed 32-team dictionary with historical names and nicknames. Series and format use fixed regex rules. No model calls are involved in enrichment. String matching and format heuristics can miss aliases or match ambiguous words; they are not semantic entity recognition.

## Structural checkpoint

146 recovered articles: 132 Sessler, 12 other writers, 2 unread bylines. Fetching paused pending author-scope clarification. The reader template was located and integrated. `reader/archive.html` embeds all 146 articles exactly once. JavaScript syntax, template styles and element IDs, and placeholder checks pass. Forty links across five articles are well-formed absolute HTTP(S) URLs. Visuals were not verified.

Cumulative byline checkpoints print and persist every 200 recovered articles, including after restarts.

## Random section-page sample — 2026-09-07

Analysis: GPT-6 (Codex), 2026-09-07. Fetching stopped after exactly 100 attempts.

Population: 1,355 unrecovered article entries with exact `byline_source == section-page` and a legacy content ID. Sorted within legacy ID families (090 before 0ap), divided into 10 near-equal population bands, and selected 10 at random per band with seed `20260907`; fetch order shuffled. The selected IDs and band boundaries are recorded in the latest `index.json.fetch_runs` entry. No replacement draws. This sample excludes the 13 previously recovered section-page articles.

| Source | Sessler | Other | Unread | Total |
|---|---:|---:|---:|---:|
| section-page | 16 | 81 | 3 | 100 |

| Byline in other bucket | Count | Scope |
|---|---:|---|
| Chris Wesseling | 16 | ATL crew |
| Dan Hanzus | 7 | ATL crew |
| Gregg Rosenthal | 5 | ATL crew |
| Kevin Patra | 28 | Other NFL.com staff |
| Herbie Teope | 6 | Other NFL.com staff |
| Jeremy Bergman | 5 | Other NFL.com staff |
| Nick Shook | 4 | Other NFL.com staff |
| Austin Knoblauch | 2 | Other NFL.com staff |
| Conor Orr | 2 | Other NFL.com staff |
| Edward Lewis | 2 | Other NFL.com staff |
| Mike Coppinger | 1 | Other NFL.com staff |
| Around The NFL staff | 3 | Generic ATN staff; individual authors unresolved |

Scope totals within other: 28 named ATL crew, 50 other named NFL.com staff, 3 generic Around The NFL staff. No joint named bylines in this sample.

98 bodies recovered; 2 failed body extraction but retained readable meta bylines (Kevin Patra and Chris Wesseling). Those two count as other. The 3 unread bylines are on recovered articles. No further fetch pass was started.

## Full ATL pass — scope correction, 2026-09-07

Analysis: GPT-6 (Codex), 2026-09-07. The earlier podcast-crew versus other-staff classification is superseded by the user's discovery-based scope decision. All recovered articles are retained. Other named credits from ATL section/pagination captures, including generic Around The NFL staff credits, belong to `atl-blog`; Sessler credits (including joint bylines) belong to `sessler`; absent bylines remain `unresolved`. No writer whitelist is used.

The cache audit scanned 253 saved pages and found 0 additional previously-unread records with names. The 2 probe body failures had already gained their readable bylines in the preceding sample audit. Byline parsing now runs before body validation and preserves evidence independently of body status. All 244 existing recovered Markdown records were migrated to byline_raw, byline_verdict and scope without changing their bodies.

Comment content is absent from the active article schema and reader. The legacy comments_url remains solely as the explicitly retained article-recovery fallback. The negative widget probe above remains evidence.

A temporary reader build structurally verified 274 recovered articles while fetching continued: JavaScript syntax, unique IDs, default Sessler scope, one-click ATL/unresolved byline switches, scalar facet totals, unchanged styles/element IDs, and resolved placeholders passed. No browser or visual verification was used. The final reader will be rebuilt after fetching ends.

## Paused handoff — 2026-09-07 16:31 UTC

Analysis: GPT-6 (Codex), 2026-09-07. User requested a break. Fetch process exited with SIGINT; the run interruption is persisted. No fetch process remains active.

This full-pass segment completed 201 attempts: 199 new recoveries and 2 failures. Cumulative: 443 recovered, 4 unresolved body failures, 1,463 pending eligible entries. No articles were deleted.

| Recovered byline_source | Sessler | Other | Unread |
|---|---:|---:|---:|
| author-page | 172 | 0 | 1 |
| section-page | 47 | 217 | 6 |

Recovered scope: 219 sessler / 217 atl-blog / 7 unresolved. Across all 447 completed article outcomes, including body failures: 219 sessler / 220 atl-blog / 8 unresolved. Three failed bodies have readable non-Sessler bylines. Section-page Sessler rate is 17.2% of completed outcomes, close to the 16% probe.

Cached byline audit: 253 saved pages reparsed, 0 additional unread records gained a name. The two probe failures were already corrected before this request.

| Writer / generic credit in recovered articles | Article credits |
|---|---:|
| Marc Sessler | 219 |
| Gregg Rosenthal | 63 |
| Dan Hanzus | 57 |
| Kevin Patra | 31 |
| Brian McIntyre | 19 |
| Chris Wesseling | 16 |
| Herbie Teope | 6 |
| Jeremy Bergman | 5 |
| Nick Shook | 5 |
| Simon Samano | 4 |
| Austin Knoblauch | 4 |
| Around The NFL staff | 3 |
| Conor Orr | 2 |
| Edward Lewis | 2 |
| Mike Coppinger | 1 |
| Max Meyer | 1 |
| Andie Hagemann | 1 |

Joint pieces count once for each credited writer. Joint bylines: Gregg Rosenthal and Marc Sessler (1); Gregg Rosenthal, Chris Wesseling and Kevin Patra (1). Generic Around The NFL staff is not an individual writer.

| Extracted publication year | Recovered |
|---|---:|
| 2010 | 1 |
| 2012 | 162 |
| 2013 | 4 |
| 2014 | 27 |
| 2015 | 13 |
| 2016 | 10 |
| 2017 | 15 |
| 2018 | 43 |
| 2019 | 52 |
| 2020 | 47 |
| 2021 | 27 |
| 2022 | 28 |
| 2023 | 13 |
| 2024 | 1 |

All 443 recovered articles have parsed publication dates. The full pass is incomplete: the year counts above are a checkpoint, not evidence of exhaustive 2014–2018 coverage.

| Body failure pattern | Previously failed, now recovered | Currently unresolved |
|---|---:|---:|
| failed:thin-body | 7 | 3 |
| failed:no-capture | 0 | 1 |

Counts are per article per pattern, not HTTP retry events; transient network retries remain in fetch_history. A comments-view failure (09000d5d82a5733c) has Gregg Rosenthal metadata but no captured article body. It remains atl-blog with failed:thin-body.

Reader rebuilt at reader/archive.html with 443 unique articles. Structural checks passed: JavaScript syntax; unchanged template styles and element IDs; no unresolved placeholders; every Markdown article embedded once; scalar facets reconcile; sampled links from 10 articles are absolute HTTP(S) URLs. Earlier behavioral checks verified default Sessler scope and one-click ATL/unread access. No visual verification.

Resume from repository root:

```sh
.venv/bin/python fetch_bodies.py
.venv/bin/python build_reader.py
```

Run those sequentially, never concurrently: both write index.json. The fetcher skips existing Markdown and records previous failures before retrying. Keep articles/ intact. Use --repair only for cached body-selector repairs and --reparse-bylines for cached metadata audits. Next full checkpoint: 600 recovered.

Remaining: finish fetching; inspect/fix recoverable failure patterns from cache as warranted; rebuild and structurally verify the final reader; produce the final source/scope/masthead/year/failure report. Current scope and comments decisions are already implemented.

## Resumed pass checkpoint — 600 recovered

Analysis: GPT-6 (Codex), 2026-09-08T06:23:51Z. Full pass remains active.

| Source | Sessler | Other | Unread |
|---|---:|---:|---:|
| author-page | 172 | 0 | 1 |
| section-page | 76 | 342 | 9 |

Scope: 248 sessler / 342 atl-blog / 10 unresolved. Section-page Sessler rate: 17.4% of attempted entries, close to the 16% probe. Unresolved body outcomes: 5 no-capture, 1 CDX-request failure, 5 thin-body. Eight earlier thin-body cases and one invalid-JSON case now have recovered bodies. Full source-specific writer counts and joint credits are persisted in index.json.byline_checkpoints.

## Reader collection update — GPT-6 Codex, 2026-09-10

User-approved plan: separate Marc Sessler from all other named writers under
Around the NFL, with unread bylines separately accessible. This is a reader
collection decision; stored provenance and scope metadata remain intact.
Built 1,903 articles: 437 Sessler (including joint credits), 1,438 other
bylines, 28 unread. Collection-local filters include full byline strings.
Structural checks passed: all Markdown articles embedded exactly once,
nonempty bodies, template replacement, JavaScript syntax, collection
separation and author filtering. No visual verification performed.
The build used --no-index-update to avoid racing the seven-entry retry.

## Portable reader scaling — GPT-6 Codex, 2026-09-10

User decision: retain one self-contained file, including compressed bodies and
search postings. No HTTP data requests, external JSON files, or decompression
library. Build invoked with --no-index-update; index and fetcher untouched.

| Stage | Bytes | Decimal MB |
|---|---:|---:|
| Original | 19,232,554 | 19.23 |
| A: omit duplicate plain text only | 13,080,673 | 13.08 |
| B: gzip HTML bodies and inverted index | 10,409,231 | 10.41 |
| Final interactions | 10,417,671 | 10.42 |

Metadata is inline; bodies are stored once in a gzip/base64 script block.
A second block holds term-to-numeric-article-ID postings. search_id in metadata
maps those IDs to articles. Normalization: lowercase NFKD, punctuation split,
3+ character terms, small English stopword set. Metadata phrase search is
immediate; body search uses intersection of indexed query terms. Lazy native
DecompressionStream loads both blocks on first article open or search. Snippets
and text-node highlights follow loading; unsupported browsers retain metadata
and source/provenance links with an explanatory note.

Initial list: 60 rows; subsequent scroll batches: 60. j/k appends as needed.
Search debounce: 120 ms; search never rebuilds facets. Facets with >12 values
show top 10, with active selections pinned and searchable expansion. Year bar
shows every year in the archive range, including zero-count years within a
collection; click, shift-click, or pointer drag selects a range. Collection,
query, facets, year range, sort and piece are URL state; legacy #p<id> remains.

| Facet | Whole-corpus distinct values | Maximum collapsed values (whole-corpus reference) |
|---|---:|---:|
| Year | 14 | 14 bars |
| Series | 6 | 6 |
| Format | 4 | 4 |
| Team | 32 | 10 |
| Player | 2,852 | 10 |
| Byline | 43 | 10 |

Facets actually use the current collection. Default Sessler: 5 series, 4 formats,
32 teams (10 collapsed), 1,901 players (10 collapsed), 4 byline strings. Year
bars span all 14 corpus years, with 13 represented in Sessler. A pinned selection
can add one extra visible value. Multi-value facet counts reconcile to assignments,
not article totals; scalar facets reconcile to their collection populations.

Player audit: 2,852 before, 2,852 after; zero dropped matches. The existing
extractor already required multi-word full-name aliases, contrary to the presumed
bare-surname cause. The reproducible --repair-players command uses cached roster
full names and football-name-plus-surname aliases, excludes missing first names /
surname-only aliases, and searches visible prose with URL destinations removed.
No surname-only matching is performed, so team-name collisions and surname-only
singletons cannot qualify. All retained matches have full-name evidence.
There are no 20 dropped examples to provide: no matches were dropped. Earlier
intermediate alias experiments were corrected before the final audit; canonical
names use the existing full-name/football-name mapping. Parsed metadata and body
were checked unchanged except the authorized entities.players field.

Verification: 1,903 unique metadata IDs, 1,903 body entries, and each body equals
md_to_html of its Markdown source. No body or plain-text fields remain in metadata.
All postings refer to valid numeric IDs. Structural runtime checks passed for
initial 60 rows, append to 120, lazy loading, URL state roundtrip, body search,
and missing-DecompressionStream fallback. JavaScript parses successfully.

Timing: native Node DecompressionStream plus JSON parsing measured 279.3 ms in
the final runtime check (earlier runs 148.6–199.5 ms). This is not browser timing.
Browser first paint is unmeasured because browser use was excluded. The reader
records archive-first-render and, where Paint Timing is supported,
archive-first-contentful-paint; archive-decompression records lazy unpack time.
Filesystem portability is structurally preserved: payloads are embedded and no
fetch/server API is used. Double-click/browser behavior was not visually tested.

## UI cleanup and analysis layer — Claude Opus 5, 2026-09-10

Fetcher, index.json, recovered bodies and provenance were not touched. Reader
changes were verified by driving the built `reader/archive.html` in headless
Chrome (32 assertions, all passing); row heights below are measured from the
rendered page at 1280x1400, not estimated.

### List rows: entity chips capped

Rows rendered every matched team and player — up to 259 tags on one entry. A
140-word item ran taller than a full column. Rows now show at most 4 entities
plus a `+N` control that expands that row alone; the opened piece still lists
every entity.

| collection | before (median / mean / p90 / max) | after |
|---|---|---|
| Marc Sessler (n=240) | 191 / 207 / 335 / 727 px | 109 / 109 / 109 / 109 px |
| Around the NFL (n=240) | 108 / 137 / 191 / 521 px | 109 / 109 / 109 / 109 px |
| Byline unread (n=28) | 108 / 113 / 129 / 191 px | 109 / 107 / 109 / 109 px |

Row height is now constant: the tallest row fell from 727 px to 109 px, and the
Sessler median from 191 px to 109 px (-43%). 1,311 of 1,903 entries (69%) carried
more than 4 tags. Rows are `div`s with the title as the single stretched link, so
the `+N` button is valid nested markup and rows keep middle-click-to-new-tab.

### Year bar promoted to a full-width band

Moved out of the sidebar into its own band between the search bar and the results,
spanning the 1,092 px reading column: 15 year slots (2010–2024; 2011 has zero
articles and reads as a gap), year labels under every bar, counts in a readout on
hover and focus rather than printed under each bar. Selected range in the stamp
colour, cleared by clicking the same selection again or by the Clear years button.
Shift-click and drag still select a span.

The band now reflects the other active filters and the search, computed with the
year range itself excluded, so its total always agrees with the tally beneath it.
Two bugs surfaced while verifying that and are fixed: `DATA.filter(match)` passed
the array index into `match`'s new second parameter and switched the year range
off for every row after the first; and the band was not redrawn when the lazily
unpacked search payload landed, so under search it kept a pre-payload count while
the list showed the post-payload one.

### Podcast pages reclassified

21 pages titled `ATN Podcast:` or `Around The NFL Podcast:`, spanning **2017–2018**
(3 in 2017, 18 in 2018), 81–142 words each. All 21 now carry
`format: "podcast-note"` and `scope: "atl-blog"`.

18 of them had no byline because none was written; those moved from
`byline_verdict: "unparsed"` to `"none-written"`, a value added so that "unread"
keeps meaning a genuine byline-parse failure. The other 3 already carried an
`Around The NFL staff` byline and their byline fields were left alone. Bodies and
provenance were asserted byte-identical after the rewrite.

**Genuine byline-parse failures remaining: 10** (was 28).

| date | words | title |
|---|---|---|
| 2010-11-29 | 108 | Playoff Picture 2011 |
| 2012-01-31 | 200 | ATL at the Super Bowl: Tuesday's musings |
| 2012-04-29 | 600 | Is Tim Tebow a 'Top 100' player? |
| 2012-10-03 | 354 | Picking winners for Week 5 NFL games |
| 2013-01-02 | 609 | Ray Lewis' retirement decision causes Twitter stir |
| 2013-02-01 | 92 | ATL Debate Club: Super Bowl XLVII edition |
| 2014-09-11 | 287 | John Mara, Art Rooney II release statement |
| 2014-09-11 | 490 | NFL honors victims of 9/11 on anniversary |
| 2015-07-09 | 519 | NFL pays tribute to Ken Stabler |
| 2019-09-24 | 1345 | (title-extraction failure — see below) |

These 21 notes are a dated, topic-tagged partial index of ATN episodes and feed
the podcast phase. Each names the on-air panel and timestamps the segments, so
they carry episode running order, not just a date. They are reachable in the
reader as Around the NFL → format → podcast-note.

### Page furniture audit — no furniture found

The entry titled `| Latest NFL News, Analysis & Updates | NFL.com` is **not** a
section landing page. It is a genuine 1,345-word Marc Sessler column, slug
`eagles-reach-crossroads-daniel-jones-gives-giants-new-vigor-0ap3000001058635`,
opening "Each week between now and the Super Bowl, Marc Sessler will scan the NFL
landscape…". Only its title was captured from the site's generic `<title>`. This
is a title-extraction failure, not page furniture; no reclassification applied,
pending review.

Four signals were swept across all 1,903 entries and found no siblings:

- Titles containing `NFL.com`, a leading or trailing pipe, or a generic site
  phrase: 1 hit, the entry above.
- Bodies that are mostly link text: **zero possible** — no body in the archive
  contains any Markdown link markup, so a link-density test cannot discriminate
  here. Recorded so the test is not re-attempted as written.
- Mostly-short-line bodies (>75% of lines under 12 words, 8+ lines): 8 hits, all
  genuine short articles with ordinary paragraphs.
- Highest entity-per-word ratio: top hits are real roundups ("Updated player
  rosters for 2018 Pro Bowl", 922 w / 144 entities).

Three entries whose titles share no words with their slug were checked and are
genuine long-form Sessler features published under magazine-style slugs
(`fade-to-silver-black`, `hopelessly-devoted`, `on-a-mission`; 3,219–7,310 words).

No `kind: "index"` reclassification was applied, because nothing qualified.

### Sidebar

Zero-value facets are dropped rather than rendered as an empty header. The
sidebar's inner scrollbar and `max-height` are gone — it scrolls with the page,
and only the collections block is sticky. Every facet over 12 values now shows
its filter input up front, so player (1,901 values in the Sessler collection,
2,852 across the archive) is usable without first expanding the list; expanded
and filtered lists render at most 200 rows with a "+N more — type above to
narrow" footer, which is what allows the inner scrollbar to be removed.

### analyse.py — distinctive-term analysis

New script, deterministic, no model calls and no network. Log-odds ratio with an
informative Dirichlet prior (Monroe, Colaresi & Quinn 2008) over unigrams,
bigrams and trigrams; prior is the pooled target+control corpus. Lowercase,
punctuation stripped (intra-word apostrophes kept, so "don't" survives intact),
n-grams do not cross sentence boundaries, body text only — titles and deks are
editor-written. Terms kept when they appear in 3+ target articles. Output is
`analysis.json`; nothing is written into article frontmatter. Re-running produces
a byte-identical file apart from `run_at`.

Target 437 Sessler articles, control 1,438 other-writer articles, vocabulary
48,437 terms.

**The comparison as specified does not isolate voice.** Three properties of the
archive defeat it, and each now has a flag:

1. **The corpora are not the same era.** The control corpus stops in 2018; the
   target runs to 2024. 181 of 437 target articles (41%) sit in years with zero
   control articles. So `2022`, `2022 stats`, `burrow` and `herbert` score as
   Sessler's voice. `--era-matched` keeps 2012–2018, the years both cover.
2. **20 NFL QB Index pieces carry identical stat tables** and are 91,103 of
   463,143 target words (20%). Each contributes ~640 occurrences of `pass yds`,
   so the top 15 is `yds`, `rush`, `td`, `rush td`, `pass yds`, `pct`, `ypa`.
   The 3-article threshold cannot catch this — 20 articles clear it. Weighting
   by document frequency (`--per-article`) does.
3. **The author sign-off is inside the body.** "Follow Marc Sessler on Twitter"
   appears in 210 of 437 target bodies and 143 of 1,438 control bodies, so five
   of the top 40 terms are fragments of the tagline. `--strip-boilerplate`
   removes it and the house podcast promos.

`--voice` applies all three (256 target / 1,438 control, 11,254 terms) and is the
fair comparison. Both outputs are kept: `analysis.json` as specified,
`analysis-voice.json` corpus-corrected.

## Voice layer — Claude Opus 5, 2026-09-10 (second pass)

31 assertions against the built `reader/archive.html` in headless Chrome, all
passing. Fetcher, index.json, recovered bodies and provenance untouched.

### Nested n-grams collapsed

`collapse_nested()` drops an n-gram that is a contiguous sub-sequence of a longer
one covering substantially the same target articles (Jaccard > 0.8 on the id
sets), keeping the maximal form. 1,918 of 11,600 terms collapse away.

The rule as literally written — *drop it if the longer n-gram scores higher* — is
available as `--strict-collapse`, but it does not do the job. On the cited family
it collapses nothing: `rash` 2.91, `rash of` 2.91, `a rash` 2.90, `a rash of`
2.90. The shorter form is almost always the higher-scoring of a nested pair,
because it also occurs on its own. Strict collapses 789 terms and leaves all four
`rash` forms standing; maximal-form collapses 1,918 and leaves `a rash of`.

Two extensions were needed to make "one habit, reported once" actually hold:

- **4-grams** (`--quadgrams`). At a trigram ceiling, `a laundry list` and
  `laundry list of` both survive because neither contains the other. The true
  maximal form is the 4-gram. The bare `analysis.json` stays at 1/2/3-grams as
  specified.
- **Maximal phrase extension** (`maximalise()`). Phrases longer than the ceiling
  still fragment: `mary kay cabot of`, `kay cabot of the`, `cabot of the plain`,
  `of the plain dealer` are one attribution reported four times, and no one of
  them contains another. This walks the actual token stream outward from each
  reported term while the article set holds within the same Jaccard bound,
  yielding `mary kay cabot of the plain dealer` once.

Residual pairs like `hurry` / `a hurry` (10 and 8 articles, Jaccard exactly 0.80)
are kept deliberately — they sit on the specified threshold, not over it.

### QB Index

**`--voice` had dropped all 23 QB Index articles whole — but by era-matching, not
by any table rule.** They are all 2022–23; the control corpus ends in 2018. The
stat tables were never the reason.

Stripping is now implemented regardless, and always on in `--voice`:

- `STAT_ROW` removes `<year> stats:` / `<year> final ranking:` rows — 702 lines
  of `17 games | 67.1 pct | 5,250 pass yds | 8.1 ypa | …`.
- A generic rule removes any pipe-delimited line that is >25% numeric tokens.
- `_is_nav` removes NFL.com in-article navigation modules (`ROSTER RESET ▶ NFC:
  North | East | West | South`) — 440 lines. These put `nfc east and nfc` in the
  previous top 60.
- The house promo pattern was broadened to the older name, *Around The League
  Podcast*.

QB Index articles keep 73,629 of 95,770 words (−23.1%); all 23 are retained, and
the surrounding prose is intact. Corpus-wide the strip removes 5.3% of target
words and 3.1% of control words.

**Effect on the era-matched result** (the shipped one): vocabulary 11,687 →
11,600, terms 9,701 → 9,637, top-60 overlap 58/60 — `saying` and `the wilderness`
out, `don't expect` and `pass catcher` in. Small, because the QB Index articles
are outside that window anyway and nav modules are sparse in his 2012–18 pieces.

**Including them costs more than it buys.** Dropping `--era-matched` puts the QB
Index prose in (437 target articles, 52,279 vocabulary, 40,584 terms) but only
19 of 60 top terms survive, and 12 of the new top 60 are 2019+ subject: `2021`,
`burrow`, `2020`, `baker mayfield`, `kyler murray`, `herbert`, `tua`,
`lamar jackson`, `the niners`, `2019`, `2022`, `in 2020`. Two attempts to filter
subject terms out — corpus-frequency and a 235k-word system dictionary — both
leak on exactly the names that matter, because `burrow`, `herbert`, `jackson`,
`baker` and `tua` are ordinary English words. Era-matching remains the only
defensible control.

That run is shipped as `analysis-voice-fullcorpus.json` so the QB Index prose is
on the record; the reader and the headline result use the era-matched one.

### Title audit

**1,902 of 1,903 titles came from `og:title`. Zero came from the generic
`<title>` element.** The fallback chain was never exercised — there was no
systemic problem to find.

The single exception is entry `0ap3000001058635`, and its cause is the opposite
of the one suspected. It has two cached captures:

| capture | og:title | twitter:title | h1 | `<title>` |
|---|---|---|---|---|
| `…-1.html` (699 KB) | *generic* | *generic* | **correct** | *generic* |
| `…-5.html` (263 KB) | **correct** | correct | correct | correct |

Capture -1 is the client-rendered page, which ships the site placeholder in
every meta tag; only the `h1` carried the headline. The title was taken from
`og:title` — the preferred source — and `og:title` was wrong. **og:title won the
re-extraction** (from capture -5); `h1` would have given the same string from
either capture, and the slug fallback was not needed.

Title now reads *Eagles reach crossroads; Daniel Jones gives Giants new vigor*.
Body, provenance and every other parsed field asserted unchanged. `fetch_bodies.py`
was left alone; if it is revisited, an `h1` fallback ahead of a generic-looking
`og:title` would have caught this at fetch time.

### Row rendering — no clipping

`109px` was a coincidence of width, not a fixed height. Computed `max-height` is
`none` and `overflow` is `visible`; the 109px was the *used* height with every
title in the sample fitting one line at a 1,092px reading column.

| window | 105-char title | row height | scrollH/clientH |
|---|---|---|---|
| 1340px | 1 line | 109 px | 108/108 |
| 900px | 2 lines | **133 px** | 132/132 |
| 700px | 2 lines | **133 px** | 132/132 |

`scrollHeight == clientHeight` on every row at every width: nothing is clipped,
and rows already grow to fit a wrapped title. No change was needed.

### Voice layer in the reader

The placeholder concordance is gone. `analyse.py --voice --keep 300` writes
`reader-terms.json`; `build_reader.py` embeds it, carrying article references as
integer search ids rather than slugs — 300 terms and 2,129 references, and the
whole payload is 0.2 MB before compression.

- Default view: top 40 terms above the list, with the count of his articles using
  each and its z. The panel sits *above* the results — below 60 rows it would
  have been unreachable.
- Clicking a term filters the list to the articles containing it, appears as a
  removable `phrase` chip alongside the other facets, and round-trips through the
  URL as `t=`. The year band and tally follow it like any other filter.
- On an open piece its own distinctive terms are marked inline in the body and
  listed beside the provenance block, each clickable back into the filter.
- The panel is labelled with corpus, era, method and run date, and states the
  framing: these are not unusual words in English, they are unusual words for him
  among 1,438 articles by colleagues on the same beat in the same years.

### A rendering race, fixed

Opening an article while the search payload was still settling left the article
pane blank. `piece()` wrapped every render in `document.startViewTransition`, and
two transitions in flight at once get the second one's update callback dropped —
so the DOM kept whatever the stale draw left. Pre-existing, but easier to reach
now that `refresh()` re-renders the piece on more paths. Fixed with a sequence
number so a late draw stands down, and a busy flag so only one transition is ever
in flight; anything raised while one is running renders directly instead.

## Proper nouns by case; final record — Claude Opus 5, 2026-09-10 (third pass)

31 assertions against the built reader, all passing. Fetcher, index.json,
recovered bodies and provenance untouched.

### Case-based proper-noun detection

`sentences()` now tokenises case-preserving; `case_profile()` marks a token as a
proper noun when it is capitalised away from the start of a sentence in more
than 70% of its occurrences, pooled over both corpora. Sentence-initial words
are excluded from both sides of the fraction: they are capitalised for position,
not for being names, so they carry no evidence. `tokenize()` then lowercases and
treats a proper noun or bare 4-digit year as a *break* rather than deleting it,
so no n-gram is ever formed across `Burrow` or `2022` — deleting the token would
have made its neighbours adjacent and invented phrases nobody wrote.

6,851 tokens classified as proper. Spot check: `burrow`, `herbert`, `jackson`,
`baker`, `mayfield`, `tua`, `niners`, `brady`, `mahomes`, `wentz`, `gronkowski`
all detected; `autumn`, `tumble`, `finest`, `rugged`, `juicy`, `starry`, `eons`,
`chaos`, `flock`, `rash`, `wandering`, `lobs` all correctly left alone. Verified
structurally rather than by inspection: **0 of the 32,442 reported terms contain
a proper-noun token, and 0 contain a bare year.**

The rule is faithful to the corpus, which means it also removes capitalised
common nouns — `september`, `sunday`, `cleveland` — so `come september` and
`cleveland's` leave the top 60. That is the correct trade: they were scoring as
voice on the strength of being capitalised.

### The full corpus is now usable

The era restriction was only ever containing leakage through names and years.
With those gone it is unnecessary, and `--voice` no longer applies it.

| | era-matched (old primary) | full corpus (new primary) |
|---|---:|---:|
| Target articles | 256 | **437** |
| Vocabulary | 9,306 | 39,671 |
| Terms reported | 8,004 | 32,442 |
| Top z | 3.43 | **5.11** |
| Subject terms in top 60 | 0 | **0** |

41% of his output is back, the z-scores rise on the larger evidence base, and
the top 60 is clean. Shipped as `analysis-voice.json`; the era-matched run is
kept as `analysis-voice-eramatched.json`.

The naive `analysis.json` is byte-identical to its previous state — the year
break is gated behind the proper-noun filter so the record of the first method
is not retroactively improved.

### Reader

`reader-terms.json` regenerated from the new primary and re-embedded. The panel
label was corrected: without era matching the two corpora no longer span the
same years, so it now reads "437 Sessler-bylined articles (2012-2024) against
1438 by other writers (2012-2018)" and the framing sentence no longer claims
"in the same years". It also states that proper nouns and years are removed by
case before scoring.

### Report restructured

`ARCHIVE-REPORT.md` now opens with the closing record — totals, masthead,
year coverage and the 2014–2018 gap, failure classes with the five permanent
losses in their own bucket, negative results, and the corrections log — with
this dated working log kept beneath it.
