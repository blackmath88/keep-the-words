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
