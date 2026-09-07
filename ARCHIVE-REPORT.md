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

## Pending

The body-fetch batch is running. Reader integration requires `reader-prototype.html`, which is absent from the repository and searched attachment directories.
