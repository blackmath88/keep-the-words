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
    .venv/bin/python fetch_bodies.py --repair
    .venv/bin/python fetch_bodies.py
    .venv/bin/python build_reader.py

The 25-entry batch samples both legacy and modern candidates; its limit is
attempted candidates, including failures. The full pass skips existing
Markdown files. Never delete `articles/` to restart. `--repair` reuses saved
HTML to repair thin bodies and expand partial modern extractions; previous
successful versions are retained as `.md.before-repair` files.

`reader-prototype.html` is the reader's source template. The generated
`sessler-archive.html`, index, raw responses, rosters, and Markdown stay local.
The source template is the sole exception to the HTML ignore rule.

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
`sessler`, `other:<name>`, or `unparsed`. Every successful recovery is kept.
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
and byline. Other writers and unread bylines are visible in the list.

Each piece has recovered text, deterministic source/search links, and a
provenance footer. Build-time link construction makes no network requests.
The prototype's Google Fonts URLs remain; system fallbacks work offline.

Findings are in `ARCHIVE-REPORT.md`, labelled with model and date, separate
from article frontmatter. Detailed failures, absences, and histories remain
in `index.json`; archived HTML remains in `articles/_raw/`.
