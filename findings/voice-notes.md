# Voice notes — reading behind the top 60

Working notes, not prose. Every claim carries article ids and line numbers so it
can be checked. `slug:NN` means line NN of `articles/<slug>.md`.

Source of the term list: `data/analysis-voice.json` — 437 Sessler articles
(2012–2024) against 1,438 by colleagues (2012–2018), log-odds with an informative
Dirichlet prior, proper nouns and years removed by case.

Every Set A and Set B rate below is reproduced in `data/analysis-matched.json`,
which ships the set definitions, the member article ids and the per-term rates.

---

## The confound found first, because it changes how everything else reads

Before any pattern: the two corpora are not shaped alike, and the top-60 list is
partly measuring that shape rather than the writer.

| | pieces | median words | formats |
|---|---:|---:|---|
| Sessler 2012–2018 | 256 | 289 | 229 briefs, 23 columns, 4 rankings |
| Sessler 2019–2024 | 181 | **1,484** | 132 columns, 31 rankings, 17 briefs |
| Colleagues (all, 2012–2018) | 1,438 | 310 | 1,315 briefs, 101 columns |

**75% of his words (348,707 of 463,143) are 2019+ columns. The control corpus has
37 pieces of 1,200+ words in total and none after 2018.** So a term can rank high
simply because long columns have room for it and transaction briefs do not.

Every pattern below is therefore tested twice:

- **Set A — matched form:** his 229 news briefs from 2012–2018 (68,155 words)
  against colleagues' 1,315 news briefs from 2012–2018 (416,597 words). Same
  format, same years, same desk. This is the honest test.
- **Set B — matched length:** his 141 pieces of 1,200+ words (341,046 words)
  against the colleagues' 37 (95,950 words). Small on their side; suggestive only.

Rates below are occurrences per 10,000 words.

---

## SURVIVES — the refusal of position shorthand

The strongest finding, and the only one that is confirmed in both directions.

He does **not** avoid plain football nouns. In Set A he uses them at roughly the
colleague rate:

| plain word | his rate | their rate | ratio |
|---|---:|---:|---:|
| cornerback | 7.04 | 6.07 | 1.2× |
| wide receiver / wideout | 10.56 | 11.16 | 0.9× |
| season | 44.46 | 47.34 | 0.9× |
| offensive coordinator | 1.61 | 2.42 | 0.7× |

He keeps a *second* vocabulary running alongside it:

| elevated word | his rate | their rate | ratio |
|---|---:|---:|---:|
| play caller | 2.49 | 0.22 | **11.5×** |
| first-rounder | 1.17 | 0.17 | 7.0× |
| passer | 7.92 | 1.66 | 4.8× |
| pass catcher | 2.64 | 0.70 | 3.8× |
| under center | 3.23 | 0.84 | 3.8× |
| signal-caller | 3.81 | 1.15 | 3.3× |
| **cover man** | 1.76 | **0.00** | never |

And he declines the newsroom's shorthand. Position abbreviations across Set A:
**his 3.96 per 10k against their 8.69 — 0.46×.** QB 1.47 vs 4.34; TE, OC and DB
zero in his briefs. The inverse pair is the cleanest single piece of evidence:
he writes "first-round pick" at 0.3× the colleague rate and "first-rounder" at
7.0×. Same referent, substituted.

`cover man` is the emblem. 47 of his articles, 0 of theirs (rank 11, z=4.20), and
it is early — 8 of its uses are in 2014 alone.

Checkable instances, all in short transaction briefs:

- `browns-try-out-cfl-defensive-back-jordan-holland-c18081:37` — a 149-word
  tryout item for an undrafted CFL player. "a 5-foot-10, 190-pound cover man".
  The headline itself says *defensive back*; the body will not.
- `john-harbaugh-ravens-aaron-ross-tore-his-achilles-3c5ca2:35` — 188 words.
  "the 31-year-old cover man".
- `cortland-finnegan-will-be-released-by-st-louis-rams-8ab11f:49` — "the
  once-physical and reliable cover man".
- `brandon-flowers-reportedly-contacted-by-10-teams-c3304d:41` — Baltimore needs
  "a third cover man"; the player being replaced is named, the position is not.

**Verdict: survives Set A decisively, in both directions, from 2014 onward.**

---

## SURVIVES — `autumn` for *season*

Rank 2 overall: 78 of his articles, 4 of theirs, z=5.07.

Set A: **6 occurrences in his 68,155 brief-words; 0 in their 416,597.** Small
count on his side, but the colleague figure is a true zero across a corpus six
times larger.

- `cowboys-stephen-jones-expects-kyle-orton-back-065aa7:41` (2014-03-24, 194w) —
  a backup quarterback is "looking for work come autumn".
- `michael-bush-signed-by-arizona-cardinals-9863a7:35` (2014-11-25, 206w) — a
  running back's 2013 becomes "the Windy City last autumn".
- `dolphins-grab-corner-bene-benwikere-off-waivers-21c6d5:37` (2016-10-10) —
  a secondary beaten "through the air this autumn".
- `peterson-id-pick-sam-bradford-to-start-for-cardinals-1b3011:51` (2018-07-13) —
  a team "destined to float through the autumn".

`campaign` for *season* is the same substitution, weaker: 4.11 vs 1.46 in Set A
(2.8×). Keep as supporting, not as a headline.

**Verdict: survives. State the raw counts, don't overstate.**

---

## SURVIVES — naming the reporter and the paper

His citation habit attaches the outlet to the person. Pattern `Name of The Paper`:

| | hits | words | rate |
|---|---:|---:|---:|
| Sessler, Set A briefs | 20 | 68,155 | **2.93** |
| Colleagues, Set A briefs | 22 | 416,597 | 0.53 |

Twenty instances against twenty-two, over a corpus six times the size — **5.6×**.

- `arians-justin-bethel-had-best-spring-of-anybody-c60bf8:35` (2014-07-24, 258w)
  — "per Kent Somers of The Arizona Republic".
- `fade-to-silver-black-c4c118` — a 1907 poem cited to *The Oakland Tribune* with
  its publication date.
- Most-cited in his corpus: The Athletic (6), The Plain Dealer (6), The Arizona
  Republic (3), The Palm Beach Post (3).

In the full analysis this shows up as `mary kay cabot of the plain dealer`
surviving as one collapsed term — a beat writer at a metro daily, named with her
paper, in a national outlet that had no obligation to name either.

**Verdict: survives Set A at 5.6×.**

---

## SURVIVES, WEAKENED — `rough and tumble`, `rugged`, `looms as`, `that saw`

Set A rates, his vs theirs: `rough and tumble` 0.59 vs 0.00; `rugged` 0.44 vs
0.00; `looms as` 1.47 vs 0.05 (29×); `that saw` 1.76 vs 0.07 (25×); `league wide`
1.17 vs 0.02; `finest` 1.32 vs 0.05.

The two syntactic habits — `looms as` and `that saw` — are the interesting pair,
because they are not ornament. Both are ways of putting a subordinate clause
where the beat would start a new sentence:
`cowboys-stephen-jones-expects-kyle-orton-back-065aa7:41`,
`afc-south-roster-reset-texans-colts-jaguars-titans-all-viable-0ap3000001025877-7bf669:57`.

**Verdict: survives, on counts of 3–12. Report as a group, not individually.**

---

## DIED — the "natural world" cluster as a general claim

This was my strongest Phase 1 impression and it does not survive Set A.

| term | his briefs (n, rate) | their briefs (n, rate) |
|---|---:|---:|
| chaos | 1, 0.15 | 1, 0.02 |
| starry | 1, 0.15 | 0, 0.00 |
| a flock of | 1, 0.15 | 0, 0.00 |
| eons | 2, 0.29 | 0, 0.00 |
| dark | 2, 0.29 | 5, 0.12 |
| earth | 4, 0.59 | 5, 0.12 |

One occurrence of `starry`, one of `chaos`, one of `a flock of` across 229
briefs. These are almost entirely a feature of the 2019+ columns, and the control
has essentially no columns to compare against.

In Set B — matched *length* — they do separate: `a flock of` 1.55 vs 0.00,
`starry` 1.00 vs 0.00, `chaos` 1.47 vs 0.10, `eons` 0.79 vs 0.00. But their side
is 37 pieces, mostly Rosenthal, Wesseling and Hanzus, and that is too thin to
carry a claim on its own.

**Revised claim that does survive:** this is a register he reaches for when given
room, not a tic that runs through everything. Not "he wrote about nature" but
"given 1,500 words he reached somewhere the form did not require." State it as
length-dependent or not at all.

---

## DIED — the martial/political cluster

Set A, his rate vs theirs:

| term | his | theirs |
|---|---:|---:|
| war | 0.44 | 0.41 |
| battle | 1.47 | 1.20 |
| chaos | 0.15 | 0.02 |
| armed with | **0.00** | 0.05 |

`war` and `battle` are flat — that is the sport's own idiom, not his. `armed
with` he never uses in a brief at all; it is purely column vocabulary. Only
`lashed` (3 vs 0) and `campaign` (2.8×) point his way, and neither is martial:
`campaign` is the elevated word for *season*, `lashed` the elevated word for
*criticised*. The cluster is an artefact of me grouping words by connotation
after seeing them in a list.

**Verdict: killed. Do not use.**

---

## DIED — "the turn at the end of a paragraph"

Reading four briefs, the closers looked like a signature: "If he has anything
left, that is." (`michael-bush-signed-by-arizona-cardinals-9863a7`). Measured
across all of Set A, it is the form talking, not the writer:

| | median final sentence | ≤12 words | first person / contraction |
|---|---:|---:|---:|
| Sessler briefs | 18 words | 28.4% | 15.3% |
| Colleague briefs | 18 words | **31.5%** | 16.2% |

Colleagues end short *more* often than he does. Every sports brief ends on a
short judged line; that is what the genre is.

**Verdict: killed. This was cherry-picking, and it is the reason Phase 2 exists.**

---

## DIED — period city nicknames

`Gotham`, `G-Men`, `Windy City` and friends: 11 occurrences in his briefs against
31 in theirs, 1.61 vs 0.74 per 10k. A 2.2× ratio resting on 11 instances, and
"Bay Area" actually runs *against* him (0.29 vs 0.38).

**Verdict: too thin. Drop.**

---

## What the method cannot see, and what reading adds

n-grams find words and short phrases. They cannot find structure. Three things
only reading turned up — all interpretation, flagged as such:

**1. He builds an argument out of a source the beat would never reach for.**
`fade-to-silver-black-c4c118` (2019-12-10, 3,219 words, the Raiders' last home
game in Oakland) opens by quoting a J.W. Dutton poem from *The Oakland Tribune*,
May 1907, then pivots through Gary Oldman researching Lee Harvey Oswald for
Stone's *JFK* — Oldman's "better than a relationship" becomes the piece's figure
for a city and its team, and it is picked up again two paragraphs later. That is
a metaphor introduced, deferred and resolved, in a game-week preview.

**2. The elevated word sits in the load-bearing clause, not the decoration.**
In `john-harbaugh-ravens-aaron-ross-tore-his-achilles-3c5ca2:35`, "the
31-year-old cover man" *is* the sentence that carries the news. He is not adding
colour after the facts; the facts arrive already in his register.

**3. He does it where nobody is watching.** The Jordan Holland tryout brief is
149 words about an undrafted player who never appeared in an NFL game. There is
no reader to impress. He still declined to write "defensive back".

None of this is measurable with the tools here, and the essay should say so.

---

## Summary

| Pattern | Set A verdict |
|---|---|
| Refusal of position shorthand (both directions) | **Survives — strongest** |
| `autumn` / `campaign` for *season* | Survives, small counts |
| Reporter named with paper | Survives, 5.6× |
| `looms as`, `that saw`, `rough and tumble`, `rugged` | Survives, weakened |
| Natural-world cluster | **Dies** at brief length; length-dependent only |
| Martial/political cluster | **Dies** — `war`/`battle` flat |
| Paragraph-ending turn | **Dies** — colleagues do it more |
| City nicknames | **Dies** — too thin |
