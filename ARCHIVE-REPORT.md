# Archive work report

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
