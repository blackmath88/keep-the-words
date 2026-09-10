# Marc Sessler — Personal Article Archive

Three Python scripts recover NFL.com writing into local Markdown and a
single-file reader. Article text remains © NFL Enterprises / the author.
Personal use only; do not republish it. Section-page harvesting also finds
other writers, whose recovered articles are retained and labelled.

## Setup

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt

## Run

    .venv/bin/python harvest_index.py
    .venv/bin/python harvest_index.py --frontier
    .venv/bin/python fetch_bodies.py 25
    .venv/bin/python fetch_bodies.py --reparse-bylines
    .venv/bin/python fetch_bodies.py --repair
    .venv/bin/python fetch_bodies.py
    .venv/bin/python build_reader.py
    .venv/bin/python analyse.py --voice --out analysis-voice.json
    .venv/bin/python analyse.py --voice --keep 300 --out reader-terms.json

The 25-entry batch samples both legacy and modern candidates; its limit is
attempted candidates, including failures. The full pass skips existing
Markdown files. Never delete `articles/` to restart. `--repair` reuses saved
HTML to repair thin bodies and expand partial modern extractions; previous
successful versions are retained as `.md.before-repair` files.

`reader-prototype.html` is the reader's source template. The generated
`reader/archive.html`, index, raw responses, rosters, and Markdown stay local.
The reader source template and `fetch-status.html` are tracked HTML files.

Open `fetch-status.html` with Live Server from the repository root to watch
saved fetch progress. It refreshes `index.json` every five seconds and shows
totals, recent results, failures, and the recovered byline split. Activity
is inferred from saved timestamps; the page cannot inspect the Python process.

## Harvest and frontier

`harvest_index.py` walks monthly Wayback captures of author/section pages.
Legacy `/news/story/<id>/article/<slug>` and `/comments/<slug>` URLs share
one content-ID identity. Entries retain both views and observed URLs.
Modern URLs retain their URL identity. `kind` marks article, index, nav, or
unknown entries; the fetcher excludes index/nav/pagination entries.

`--frontier` uses the reported CDX pattern evidence stored under
`index.json.frontier.pattern_reports`, promotes known daily/pagination
indexes, and batch-queries mechanical daily URLs for 2014–2018. Each year
is one prefix CDX query filtered to daily URL shapes, collapsed by URL.
It records individual no-capture outcomes and crawls one hop only.

Replay requests wait at least five seconds before each attempt. The shared
`request_with_backoff()` helper retries connection errors, timeouts, 429,
and 503: four attempts, 5/10/20-second backoff, then a 40-second cooldown.
CDX has no replay delay. Harvest/frontier failures get one final retry pass.
Parsed captures are skipped on rerun. Attempt histories survive recovery,
and index writes are atomic. Run only one index-writing script at a time.

## Bodies and metadata

Legacy URLs skip dead live routes. The fetcher queries CDX for the article
URL and takes the earliest HTTP 200 capture, falling back to the comments
view. Modern articles try live NFL.com first, then Wayback. Raw HTML and
structured HTTP/extraction outcomes are retained for diagnosis.

Body selectors include archived `.articleText`, existing NFL selectors,
and all current `.story-part-rich-text-editor-wrapper` blocks in order.
The densest direct-paragraph fallback remains for layouts not yet covered.

Bylines come from explicit metadata, author elements, or article JSON-LD:
`byline_raw` preserves the full credit and `byline_verdict` is `sessler`,
`other`, or `unparsed`, independent of body `status`. `byline_status` remains
a compatibility label. `--reparse-bylines` audits cached HTML without downloads.
Every successful recovery is kept. Scope is `sessler` (including joint credits),
`atl-blog` (other credits discovered through ATL pages), or `unresolved`.
There is no podcast-crew whitelist. Comment content is not collected; the
legacy comments-view URL remains only as an article-body recovery route.
`content_id` and `byline_source` distinguish article identity and discovery
source. Publication dates come from page metadata, including legacy
`#article-time`; slug years and capture years are not publication dates.
The reader records undated gaps under `index.json.reader_builds`.

Enrichment uses deterministic rules only: fixed title regexes for series
and format, a closed 32-team vocabulary with historical names, and full-name
matches against cached nflverse season rosters for 2012–2024. No model API
is used. These are literal matches and heuristics, not semantic analysis.

## Reader and evidence

The reader retains the prototype's paper/carbon modes, two grain layers,
hash routes, j/k/Enter/Esc/slash shortcuts, filter chips, live tally, and
View Transitions fallback. Facets cover year, series, format, team, player,
and byline within the selected collection. Sidebar tabs separate Marc Sessler,
Around the NFL, and unread bylines. Full credits remain visible in
the list, including joint credits.

Each piece has recovered text, deterministic source/search links, and a
provenance footer. Build-time link construction makes no network requests.
The prototype's Google Fonts URLs remain; system fallbacks work offline.

Findings are in `ARCHIVE-REPORT.md`, labelled with model and date, separate
from article frontmatter. Detailed failures, absences, and histories remain
in `index.json`; archived HTML remains in `articles/_raw/`.

Full fetch checkpoints every 200 recovered articles persist source splits,
writer credits and joint bylines, scope, and cumulative failure classes.
An eight-percentage-point drift from the 16% section-page probe is flagged
as a possible month/ID coverage effect. Failed attempts remain in history
even when a later retry succeeds.

## Reader collections

Open `reader/archive.html`. The sidebar defaults to Marc Sessler (including
joint Sessler credits). Around the NFL contains every other named author and
the 21 ATN podcast notes, which carry `byline_verdict: "none-written"` because
no byline was ever written on them. Byline unread holds only genuine
byline-parse failures — 10 of them. Each collection has its own author and
topic filters. Switching collections clears search and filters.

The distinctive-terms panel sits above the results: the top 40 terms with the
number of his articles using each. Clicking one filters the list and appears as a
removable `phrase` chip, linkable as `t=` in the URL. Opening a piece marks its
own terms inline in the body and lists them beside the provenance block. The
panel states its own method, corpus, era and run date.

List rows show at most 4 entities plus a `+N` control that expands that row
alone; the opened piece lists every entity. The year band sits full width above
the results, with counts on hover; click a year, shift-click or drag for a span,
click the same selection again to clear. The sidebar scrolls with the page and
sticks only the collections block; facets over 12 values carry a filter input
and render at most 200 rows at a time.

Use `build_reader.py --no-index-update` to build while a fetch is running
without writing to its index. Rebuild after recovery finishes for new articles.

## Portable compressed reader

Build with `.venv/bin/python build_reader.py --no-index-update` and double-click
`reader/archive.html`. Corpus data stays inside the file. HTML bodies and a
build-time inverted search index are gzip/base64 payloads, lazily unpacked with
native DecompressionStream. Older browsers show metadata and source links.
There is no external JSON or runtime decompression library.

Lists begin with 60 rows and append on scroll (or Load 60 more). Search waits
120 ms after typing, shows immediate metadata results, then body results and
snippets. Facets expand and can be searched; years support ranges. Filtered
views and sort order are linkable, and browser Back restores previous state.

## Distinctive-term analysis

`analyse.py` compares Sessler-bylined articles (target) against other-writer
articles (control) using a log-odds ratio with an informative Dirichlet prior
(Monroe, Colaresi & Quinn 2008) over unigrams, bigrams and trigrams. It is fully
deterministic — no model calls, no network — and writes `analysis.json` only.
Nothing is written into article frontmatter.

Run bare, it reproduces the first specified method, artefacts and all, and is
kept as the record of what that produced. Use `--voice` for anything about voice.

`--voice` removes newsroom furniture (author sign-offs, house promos, QB Index
stat tables, in-article navigation modules), removes proper nouns and bare years
before scoring, weights by article rather than by occurrence, counts 1/2/3/4-grams
and collapses nested forms to the maximal phrase.

Proper nouns are decided by the case the corpus itself uses — capitalised away
from the start of a sentence in more than 70% of occurrences — not by a
dictionary. `Burrow` the quarterback and `burrow` the verb are one token only if
you lowercase first, which is why the earlier era restriction was needed and why
it no longer is: the full 437-article corpus now scores clean.

Stat tables and NFL.com navigation modules are stripped as furniture, so the QB
Index columns keep their prose (23 articles, 73,629 of 95,770 words retained)
instead of being excluded for what is printed between the paragraphs.

`--collapse` keeps only the maximal form of nested n-grams ("a rash of" rather
than four spellings of one habit), and `--maximal` grows a reported term along
the token stream until the article set stops holding, which is what turns four
overlapping 4-grams into `mary kay cabot of the plain dealer`.

`--era-matched` restricts both corpora to 2012-2018, the years they share. It is
no longer needed and no longer part of `--voice`; `analysis-voice-eramatched.json`
is kept as the alternative.

`analyse.py --voice --keep 300 --out reader-terms.json` writes the reader's
payload. Rebuild the reader afterwards to pick it up.

`build_reader.py --repair-players` deterministically rechecks full-name player
matches using cached rosters, changing only entities.players. It does not fetch
rosters or write index.json. The latest audit and size/timing limits are in
ARCHIVE-REPORT.md.
