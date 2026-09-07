# Marc Sessler — Personal Article Archive

A three-step pipeline that enumerates, retrieves and renders Marc Sessler's
NFL.com writing (2012–2024, including the Around the League blog era) as a
browsable single-file HTML archive with full provenance on every piece.

Personal-use archive. Text remains © NFL Enterprises / the author.
Don't republish it.

## Setup

    python3 -m venv .venv && source .venv/bin/activate
    pip install requests beautifulsoup4

## Run

    python3 harvest_index.py       # ~20-60 min. Writes index.json
    python3 fetch_bodies.py 25     # test run: 25 articles -> articles/*.md
    python3 fetch_bodies.py        # full run. Resumable, Ctrl-C safe
    python3 build_reader.py        # writes sessler-archive.html

Open `sessler-archive.html` in any browser. Nothing else needed.

## How it works

**harvest_index.py** — NFL.com article URLs are slug-based with no author
token, so they can't be filtered by byline in the Wayback CDX API directly.
Instead the script walks *historical captures of his author and index pages*
(one per month, via CDX `collapse=timestamp:6`) and scrapes the article links
out of each one. Every URL records the capture it was discovered in.

Edit `SEEDS` if you find more index pages — old `blogs.nfl.com` paths,
the Around the League landing page, tag pages. More seeds, more coverage.

**fetch_bodies.py** — tries live NFL.com first (cleaner markup), falls back
to the closest Wayback snapshot. Extracts the body via known NFL.com
selectors, then a densest-paragraph-container heuristic. Writes Markdown with
a YAML frontmatter provenance block: original URL, what was actually
retrieved, source type, wayback timestamp, HTTP status, which extractor
matched, and when.

`byline_verified` is set by checking whether "sessler" appears in the title,
byline or opening text. Co-bylined Around the League posts are kept — the
reader has a "verified byline only" toggle so you can filter rather than
having to decide up front.

**build_reader.py** — embeds everything in one HTML file. Full-text search,
year and sort filters, byline toggle, serif reading column, and a provenance
footer on each piece linking back to the original and the archived source.

## Tuning

- `SLEEP` in both scripts (1.0s / 1.5s) — be polite, don't lower it.
- `collapse="timestamp:6"` in harvest = one capture per month. Change to
  `timestamp:8` for daily captures: far more coverage, far slower.
- `AUTHOR_HINT` in fetch_bodies if you want stricter byline matching.
- Failures are recorded in `index.json` as `failed:*`. Re-running only
  retries what has no `.md` file yet.

## Expected reality

Coverage of 2019–2024 should be good. The 2012–2016 Around the League era
will be patchy — those URLs died in NFL.com's CMS migrations and Wayback's
coverage of blog index pages is uneven. Run the harvest, look at the count,
then decide whether it's worth adding more seed pages.
