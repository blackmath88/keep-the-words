# keep-the-words

A recovered archive of Marc Sessler's NFL.com writing, the newsroom around him,
and a deterministic analysis of what separates his prose from theirs.

Around 2016 NFL.com changed content systems and the URL scheme changed with it.
The old addresses stopped resolving. Nothing was taken down; it stopped being
addressable. This rebuilds what the Internet Archive kept: **1,903 articles**,
437 of them his, with the provenance of every one recorded.

- **Essay** — [`essay/autumn.md`](essay/autumn.md)
- **Findings** — [`findings/voice-notes.md`](findings/voice-notes.md), what
  survived the matched comparison and what did not
- **Method** — [`docs/METHOD.md`](docs/METHOD.md), how to rebuild all of it,
  with the corrections log at the top
- **Working log** — [`docs/ARCHIVE-REPORT.md`](docs/ARCHIVE-REPORT.md)

## The three tiers

The split is deliberate. It shows the archive is real and complete without
republishing a word of it.

| Tier | What | Where | Distributed? |
|---|---|---|---|
| **Public** | Essay, findings, method; the reader shell; per-article titles, dates, bylines, entities, word counts, provenance and original URLs | `public/`, `data/` | yes |
| **Gated** | Article bodies and the full-text search index, one gzip blob | Cloudflare KV, served by `functions/api/bodies.js` | passphrase |
| **Local only** | The recovered corpus itself | `articles/`, `reader/`, `dist-private/` | **no** — rebuilt from the Internet Archive, gitignored |

The reader loads and is fully browsable without the passphrase. Facets work, the
year bar renders, every original URL is clickable. Opening a piece or searching
full text prompts for a passphrase; the metadata never does.

Article text is copyright NFL Enterprises and the writers. The code is MIT; the
corpus is not covered and is not distributed here. See [LICENSE](LICENSE).

## Layout

```
essay/autumn.md               the essay
findings/voice-notes.md       phase-1 readings and phase-2 verdicts
docs/METHOD.md                reproducibility document + corrections log
docs/ARCHIVE-REPORT.md        dated working log
scripts/                      the pipeline (see below)
data/                         the public data tier
functions/                    Cloudflare Pages Functions: the gate
public/                       generated site (gitignored)
articles/                     recovered corpus (gitignored, not distributed)
```

### data/

| File | Contents |
|---|---|
| `metadata.json` | per article — no bodies, no deks |
| `index.json` | every discovered URL, its provenance, the failure log |
| `analysis.json` | the naive first method, kept as the record of what it produced |
| `analysis-voice.json` | the analysis that ships: proper nouns dropped by case |
| `analysis-voice-eramatched.json` | the era-matched alternative |
| `analysis-matched.json` | Set A and Set B: definitions, member ids, per-term rates |
| `reader-terms.json` | collapsed top 300 terms, embedded in the reader |

Every figure in the essay traces to one of these. `analysis.json` and
`analysis-voice.json` are large (40 MB and 28 MB) and gitignored; regenerate
them with the commands below.

## Reproducing

Python 3.9+, `pip install -r requirements.txt`. Run from the repository root,
sequentially — several stages write `index.json`.

```sh
python3 scripts/harvest_index.py                 # seed captures -> index.json
python3 scripts/harvest_index.py --frontier      # wildcard CDX expansion
python3 scripts/fetch_bodies.py                  # bodies and bylines -> articles/
python3 scripts/analyse.py --out data/analysis.json
python3 scripts/analyse.py --voice --out data/analysis-voice.json
python3 scripts/analyse.py --voice --keep 300 --out data/reader-terms.json
python3 scripts/build_data.py                    # the public data tier
python3 scripts/build_reader.py                  # reader/archive.html
python3 scripts/build_site.py --check            # public/ + leak check
```

Never delete `articles/` to restart: the fetcher skips existing Markdown and
records previous failures before retrying. Failed attempts stay in the history
even when a later retry succeeds.

`scripts/analyse.py` is deterministic — no model calls, no network. Re-running
produces a byte-identical file apart from `run_at`.

## The site

Static on Cloudflare Pages; the body payload is gated by a Pages Function.

```sh
npx wrangler kv namespace create ARCHIVE          # id -> wrangler.jsonc
npx wrangler kv key put payload --path dist-private/payload.bin \
    --binding ARCHIVE --remote
npx wrangler pages secret put ARCHIVE_KEY   --project-name keep-the-words
npx wrangler pages secret put COOKIE_SECRET --project-name keep-the-words
npx wrangler pages deploy public --project-name keep-the-words
```

The payload lives in KV, never in `public/`, so there is no URL under the site
that serves it. `ARCHIVE_KEY` is the passphrase; `COOKIE_SECRET` signs the
12-hour session cookie and must be a long random value. Neither is ever in the
repository.

`python3 scripts/build_site.py --check` runs the leak check: any run of 8+ words
shared between the public build and `articles/`, excluding the six approved
quotations, fails the build.
