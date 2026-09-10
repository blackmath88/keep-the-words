#!/usr/bin/env python3
"""
build_site.py — assemble the public Cloudflare Pages site and the gated payload.

Public (public/):   essay, method, findings, about, and the reader shell with
                    its metadata — titles, dates, bylines, entities, word
                    counts, provenance links, facets, year distribution.
Gated (dist-private/): article bodies and the search index, one gzip blob,
                    uploaded to KV and served only by functions/api/bodies.js.

The split is the point: the reader is fully browsable without the passphrase,
which shows the archive is real and complete without republishing a word of it.

    python3 build_site.py            # build
    python3 build_site.py --check    # build, then run the leak check
"""

import base64
import gzip
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READER = ROOT / "reader" / "archive.html"
OUT = ROOT / "public"
PRIVATE = ROOT / "dist-private"

# The six quotations cleared for publication in essay/autumn.md. Everything
# else that overlaps the corpus is a leak.
APPROVED_QUOTATIONS = [
    "a 5-foot-10, 190-pound cover man",
    "looking for work come autumn",
    "per Kent Somers of The Arizona Republic",
    "rough-and-tumble underdog puncher",
    "a flock of beguiled interior linemen",
    "the once-physical and reliable cover man",
]

NAV = [
    ("/", "Essay"),
    ("/archive", "Archive"),
    ("/findings", "Findings"),
    ("/method", "Method"),
    ("/about", "About"),
]


# --------------------------------------------------------------- markdown ---

def inline(text):
    """Escape, then apply the small subset of inline markdown the docs use."""
    t = html.escape(text)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(md, figures=None):
    out, lines, i = [], md.split("\n"), 0
    figures = figures or {}
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        # ::quote TEXT | HEADLINE | DATE  — the six cleared quotations, set
        # apart from running text so their number is visible at a glance.
        if s.startswith("::quote "):
            text, head, date = [x.strip() for x in s[8:].split("|")]
            out.append(
                '<figure class="pull"><blockquote>%s</blockquote>'
                '<figcaption>%s <span class="sep">·</span> %s</figcaption></figure>'
                % (inline(text), html.escape(head), html.escape(date)))
            i += 1
            continue
        # ::note TERM | HIS | THEIRS — marginal counts beside the paragraph.
        if s.startswith("::note "):
            notes = []
            while i < len(lines) and lines[i].strip().startswith("::note "):
                term, his, theirs = [x.strip() for x in lines[i].strip()[7:].split("|")]
                notes.append('<span class="mn-row"><b>%s</b><span class="mn-n">%s</span>'
                             '<span class="mn-n mn-them">%s</span></span>'
                             % (html.escape(term), html.escape(his), html.escape(theirs)))
                i += 1
            out.append('<aside class="marginnote"><span class="mn-head">his / theirs</span>'
                       + "".join(notes) + "</aside>")
            continue
        if s.startswith("```figure:"):
            key = s[len("```figure:"):].rstrip("`").strip()
            out.append(figures.get(key, ""))
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        if re.match(r"^-{3,}$", s):
            out.append("<hr>")
            i += 1
            continue
        if s.startswith("#"):
            lvl = len(s) - len(s.lstrip("#"))
            out.append(f"<h{lvl}>{inline(s.lstrip('#').strip())}</h{lvl}>")
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            body = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c or "-") for c in r)]
            if not body:
                continue
            head, rest = body[0], body[1:]
            t = ["<div class='tablewrap'><table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rest:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if s.startswith("> "):
            out.append(f"<blockquote>{inline(s[2:])}</blockquote>")
            i += 1
            continue
        para = [s]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\||#|-\s|>|```|-{3,})", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def bar_figure(pairs, caption):
    """Two horizontal bars per row: his rate against theirs. Static SVG."""
    top = max(max(a, b) for _, a, b in pairs) or 1
    rows = []
    for label, mine, theirs in pairs:
        rows.append(
            '<div class="bf-row"><div class="bf-label">%s</div>'
            '<div class="bf-bars">'
            '<div class="bf-bar bf-his"><span class="bf-track"><i style="width:%.1f%%"></i></span><em>%.2f</em></div>'
            '<div class="bf-bar bf-their"><span class="bf-track"><i style="width:%.1f%%"></i></span><em>%.2f</em></div>'
            '</div></div>'
            % (html.escape(label), 100.0 * mine / top, mine, 100.0 * theirs / top, theirs))
    return ('<figure class="barfig"><div class="bf-key">'
            '<span class="bf-k bf-his"></span>Sessler'
            '<span class="bf-k bf-their"></span>colleagues</div>'
            + "".join(rows) +
            '<figcaption>%s</figcaption></figure>' % caption)


def dead_figure(items):
    """The findings that did not survive, struck through and counted."""
    rows = "".join('<li><s>%s</s><span class="why">%s</span></li>'
                   % (html.escape(a), html.escape(b)) for a, b in items)
    return ('<figure class="deadfig"><h4>Killed by the matched comparison</h4>'
            '<ul>%s</ul><figcaption>Measured against his 229 short items and their '
            '1,315, 2012–2018. Struck lines are claims this essay does not make.'
            '</figcaption></figure>' % rows)


def year_figure(seed, frontier, caption):
    """Stacked year sparkline: what five seeds reached, what expansion added."""
    # Contiguous range, so a year with nothing in it reads as a gap rather
    # than vanishing. 2011 is genuinely empty.
    lo, hi = min(set(seed) | set(frontier)), max(set(seed) | set(frontier))
    years = [str(y) for y in range(int(lo), int(hi) + 1)]
    top = max((seed.get(y, 0) + frontier.get(y, 0)) for y in years) or 1
    H = 92
    cols = []
    for y in years:
        a, b = seed.get(y, 0), frontier.get(y, 0)
        ha, hb = H * a / top, H * b / top
        cols.append(
            '<div class="yf-col" title="%s: %d recovered (%d from the seeds, %d added by expansion)">'
            '<span class="yf-stack">'
            '<i class="yf-front" style="height:%.1fpx"></i>'
            '<i class="yf-seed" style="height:%.1fpx"></i></span>'
            '<span class="yf-year">%s</span></div>'
            % (y, a + b, a, b, hb, max(ha, 1 if a else 0), y[2:]))
    return ('<figure class="yearfig"><div class="yf-key">'
            '<span class="yf-k yf-seed"></span>reached by the five seeds'
            '<span class="yf-k yf-front"></span>added by frontier expansion</div>'
            '<div class="yf-plot">%s</div><figcaption>%s</figcaption></figure>'
            % ("".join(cols), caption))


def page(title, subtitle, body, active, wide=False):
    nav = "".join(
        f'<a href="{href}"{" class=\'on\'" if href == active else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en" data-mode="paper">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)} — Keep the Words</title>
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div class="grain a"></div><div class="grain b"></div>
<div class="sheet{' wide' if wide else ''}">
  <header class="masthead">
    <a class="wordmark" href="/"><i>M</i><i>a</i><i>r</i><i>c</i> <i>S</i><i>e</i><i>s</i><i>s</i><i>l</i><i>e</i><i>r</i></a>
    <span class="stamp">recovered</span>
    <nav class="nav">{nav}</nav>
  </header>
  <main class="doc">
    <h1 class="doctitle">{html.escape(title)}</h1>
    {f'<p class="docsub">{html.escape(subtitle)}</p>' if subtitle else ''}
    {body}
  </main>
  <footer class="foot">
    <p>Personal archive. Article text remains © NFL Enterprises and the author.
    Nothing here is republished: the reader shows what was recovered, not the writing.</p>
  </footer>
</div>
</body>
</html>
"""


# ------------------------------------------------------------------ build ---

def split_reader():
    """Return (shell_html, gzip_payload_bytes) from the built local reader."""
    if not READER.exists():
        sys.exit("reader/archive.html missing — run build_reader.py first")
    doc = READER.read_text(encoding="utf-8")
    payloads = {}
    for tag, key in (("bodies-payload", "bodies"), ("search-payload", "search")):
        m = re.search(r'<script id="%s"[^>]*>([^<]*)</script>' % tag, doc)
        if not m:
            sys.exit(f"could not find {tag} in the reader")
        payloads[key] = json.loads(gzip.decompress(base64.b64decode(m.group(1).strip())))
    # Strip both payloads out of the shell entirely.
    shell, n = re.subn(
        r'(<script id="(?:bodies|search)-payload"[^>]*>)[^<]*(</script>)',
        lambda m: "", doc)
    if n != 2:
        sys.exit(f"expected to remove 2 payload scripts, removed {n}")
    shell = strip_deks(shell)
    shell = cap_voice_terms(shell)
    blob = gzip.compress(
        json.dumps(payloads, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0)
    return shell, blob


MAX_TERM_WORDS = 7


def cap_voice_terms(shell):
    """Drop distinctive terms long enough to be prose rather than a term.

    --maximal grows a term along the token stream, which can turn a phrase into
    a sentence fragment. Every real finding is five words or fewer; anything at
    or past the leak check's 8-word threshold is body text and does not ship.
    """
    m = re.search(r"^const VOICE=(\{.*?\});$", shell, re.M)
    if not m:
        sys.exit("could not locate the VOICE payload in the reader")
    voice = json.loads(m.group(1).replace("\\u003c", "<"))
    before = len(voice["terms"])
    dropped = [t[0] for t in voice["terms"] if len(t[0].split()) > MAX_TERM_WORDS]
    voice["terms"] = [t for t in voice["terms"] if len(t[0].split()) <= MAX_TERM_WORDS]
    for t in dropped:
        print("dropped over-length voice term (%d words): %r" % (len(t.split()), t))
    print("voice terms in public payload: %d of %d" % (len(voice["terms"]), before))
    packed = json.dumps(voice, ensure_ascii=False).replace("<", "\\u003c")
    return shell[:m.start()] + "const VOICE=" + packed + ";" + shell[m.end():]


def strip_deks(shell):
    """Blank every dek in the public metadata.

    The dek is a published sentence of NFL.com copy. It is not in the list of
    fields this site publishes, and leaving it in would put roughly one
    sentence per article back on the open web.
    """
    m = re.search(r"^const DATA=(\[.*\]);$", shell, re.M)
    if not m:
        sys.exit("could not locate the DATA array in the reader")
    data = json.loads(m.group(1).replace("\\u003c", "<"))
    n = sum(1 for a in data if a.get("d"))
    for a in data:
        a["d"] = ""
    packed = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    print("stripped %d deks from the public metadata" % n)
    return shell[:m.start()] + "const DATA=" + packed + ";" + shell[m.end():]


def gate_client(shell):
    """Swap the inline unpack for a fetch of the gated endpoint."""
    def sub(a, b):
        nonlocal shell
        if shell.count(a) != 1:
            sys.exit("gate_client: expected exactly one match for %r (found %d)"
                     % (a[:70], shell.count(a)))
        shell = shell.replace(a, b)

    sub("let BODIES=null,SEARCH=null,payloadPromise=null,payloadError='',searchHits=new Set(),timer,observer;",
        "let BODIES=null,SEARCH=null,payloadPromise=null,payloadError='',searchHits=new Set(),timer,observer;\n"
        "let locked=false;")

    sub("""async function payload(){
 if(payloadPromise)return payloadPromise;
 payloadPromise=(async()=>{try{
  if(!globalThis.DecompressionStream)throw Error('This browser cannot unpack article bodies. You can still browse metadata and use the source links.');
  const start=performance.now();
  async function unpack(id){const bytes=Uint8Array.from(atob(el(id).textContent.trim()),c=>c.charCodeAt(0));return JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());}
  [BODIES,SEARCH]=await Promise.all([unpack('bodies-payload'),unpack('search-payload')]);
  performance.measure('archive-decompression',{start,end:performance.now()});
 }catch(e){payloadError=e.message;} })();return payloadPromise;
}""",
        """async function payload(force){
 if(payloadPromise&&!force)return payloadPromise;
 payloadPromise=(async()=>{try{
  payloadError='';locked=false;
  if(!globalThis.DecompressionStream)throw Error('This browser cannot unpack article bodies. You can still browse metadata and use the source links.');
  const start=performance.now();
  const r=await fetch('/api/bodies',{credentials:'same-origin'});
  if(r.status===401){locked=true;throw Error('locked');}
  if(!r.ok)throw Error('The article text could not be loaded ('+r.status+').');
  // Decompression path below is unchanged: gzip stream in, JSON out.
  const data=JSON.parse(await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).text());
  BODIES=data.bodies;SEARCH=data.search;
  performance.measure('archive-decompression',{start,end:performance.now()});
 }catch(e){if(!locked)payloadError=e.message;} })();return payloadPromise;
}
function gateHtml(msg){return `<form class="gate" id="gate">
  <h4>The writing is behind a passphrase</h4>
  <p>Everything about this archive is public: what was recovered, when each
  piece ran, who filed it, where the original lived. The text of the articles
  is not mine to republish, so it needs a passphrase. If you were given one,
  it opens every piece for twelve hours.</p>
  <label class="gate-row"><span class="sr">Passphrase</span>
    <input id="gate-input" type="password" autocomplete="current-password" placeholder="Passphrase" required>
    <button class="ghost" type="submit">Unlock</button>
  </label>
  <p class="gate-msg" role="status">${msg?esc(msg):''}</p>
  <p class="gate-alt">Or follow this piece to its source: the provenance links
  below go to the original URL and to every Wayback capture of it.</p>
</form>`;}
function bindGate(root,after){
  const f=root.querySelector('#gate');if(!f)return;
  f.onsubmit=async e=>{
    e.preventDefault();
    const input=f.querySelector('#gate-input'),msg=f.querySelector('.gate-msg');
    const btn=f.querySelector('button');
    btn.disabled=true;msg.textContent='Checking…';
    try{
      const r=await fetch('/api/unlock',{method:'POST',credentials:'same-origin',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({passphrase:input.value})});
      if(r.ok){await payload(true);if(!locked&&!payloadError){after();return;}
        msg.textContent=payloadError||'Unlocked, but the text did not load.';}
      else{const d=await r.json().catch(()=>({}));
        msg.textContent=d.error||"that passphrase doesn't open this";
        input.select();}
    }catch(err){msg.textContent='Could not reach the gate. Check your connection.';}
    btn.disabled=false;
  };
}""")

    # Once locked, stop re-requesting: piece() re-runs on every draw and
    # refresh() draws again, so without this the pair spin forever and the
    # gate never settles on screen.
    sub("if(open&&!BODIES&&!payloadError)payload().then(refresh);",
        "if(open&&!BODIES&&!payloadError&&!locked)payload().then(refresh);")

    # Locked pieces show the gate, not an error.
    sub('<div class="body">${BODIES?BODIES[a.id]:"<p role=\\"status\\">"+esc(payloadError||"Loading article…")+"</p>"}</div>',
        '<div class="body">${BODIES?BODIES[a.id]:(locked?gateHtml(""):"<p role=\\"status\\">"+esc(payloadError||"Loading article…")+"</p>")}</div>')

    sub("  highlightBody();\n  if(a)markVoice(voiceOf(a));\n  bindVoice(el('piece'));",
        "  highlightBody();\n  if(a)markVoice(voiceOf(a));\n  bindVoice(el('piece'));\n"
        "  bindGate(el('piece'),()=>{renderList();piece();});")

    # Locked search says so in the reader's own voice.
    sub("""el('search-state').textContent=q&&!SEARCH?(payloadError||'Metadata results shown. Loading body search…'):q?'Body search: all indexed query terms; titles also match phrases.':'';""",
        """el('search-state').textContent=q&&!SEARCH?(locked?'Titles, deks and series are searchable here. Full-text search needs the passphrase — open any piece to enter it.':(payloadError||'Metadata results shown. Loading body search…')):q?'Body search: all indexed query terms; titles also match phrases.':'';""")

    return shell


def essay_figures():
    """Every figure in the essay is drawn from a file in data/."""
    matched = json.loads((ROOT / "data" / "analysis-matched.json").read_text(encoding="utf-8"))
    A = matched["sets"][0]["sides"]
    his, theirs = A["sessler"]["rates_per_10k"], A["colleagues"]["rates_per_10k"]
    g = lambda side, k: side[k]["per_10k"]

    subs = bar_figure(
        [("first-round pick", g(his, "first-round pick"), g(theirs, "first-round pick")),
         ("first-rounder", g(his, "first-rounder"), g(theirs, "first-rounder"))],
        "Occurrences per 10,000 words, news briefs 2012–2018 only. "
        "data/analysis-matched.json, Set A.")

    dead = dead_figure([
        ("The natural-world register — chaos, starry, a flock of, eons",
         "one or two occurrences each across 229 briefs; it belongs to the long columns"),
        ("The martial vocabulary — war, battle",
         "0.44 vs 0.41 and 1.47 vs 1.20 per 10k: the sport's idiom, not his"),
        ("The judged little sentence at the end of a paragraph",
         "identical median length; his colleagues end short more often, 31.5% to 28.4%"),
        ("Period city nicknames — Gotham, the Windy City",
         "eleven instances in total, and Bay Area runs the other way"),
    ])

    # Year distribution, split by how each article was found.
    meta = json.loads((ROOT / "data" / "metadata.json").read_text(encoding="utf-8"))["articles"]
    SEEDS = {"https://www.nfl.com/author/marc-sessler-09000d5d823c1a70",
             "http://www.nfl.com/news/around-the-league",
             "http://www.nfl.com/news/writer/marc-sessler",
             "http://blogs.nfl.com/author/marcsessler/",
             "http://www.nfl.com/blogs/around-the-league"}
    seed, front = {}, {}
    for a in meta:
        y = (a.get("date") or "")[:4]
        if not y:
            continue
        d = seed if a.get("discovered_via") in SEEDS else front
        d[y] = d.get(y, 0) + 1
    years = year_figure(seed, front,
        "All 1,903 recovered articles by publication year. The five seeds reached six "
        "pieces from 2014–2018; one wildcard CDX query found the rest. "
        "data/metadata.json.")

    return {"substitution": subs, "dead": dead, "years": years}


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    PRIVATE.mkdir(exist_ok=True)

    shell, blob = split_reader()
    shell = gate_client(shell)
    (OUT / "archive.html").write_text(shell, encoding="utf-8")
    (PRIVATE / "payload.bin").write_bytes(blob)

    essay = (ROOT / "essay" / "autumn.md").read_text(encoding="utf-8")
    title = essay.split("\n", 1)[0].lstrip("# ").strip()
    (OUT / "index.html").write_text(page(
        title, "Recovered NFL.com writing by Marc Sessler, and what the counting found.",
        md_to_html(essay.split("\n", 1)[1], essay_figures()), "/"), encoding="utf-8")

    findings = (ROOT / "findings" / "voice-notes.md").read_text(encoding="utf-8")
    (OUT / "findings.html").write_text(page(
        "Findings", "What survived the matched comparison, and what did not.",
        md_to_html(findings.split("\n", 1)[1]), "/findings", wide=True), encoding="utf-8")

    method = (ROOT / "docs" / "METHOD.md").read_text(encoding="utf-8")
    (OUT / "method.html").write_text(page(
        "Method", "How the corpus was built, how to rebuild it, and what was got wrong first.",
        md_to_html(method.split("\n", 1)[1]), "/method", wide=True), encoding="utf-8")

    (OUT / "about.html").write_text(page("About", "", ABOUT, "/about"), encoding="utf-8")
    # Without a 404 page, Pages falls back to index.html with a 200 for every
    # unmatched path, which would make "is the payload reachable?" unanswerable.
    (OUT / "404.html").write_text(page(
        "Not here", "",
        "<p>No page at that address.</p>"
        "<p>The archive reader is at <a href=\"/archive\">/archive</a>. "
        "The article bodies are not served as a file at any URL — they come from "
        "an authenticated endpoint, and only with a passphrase.</p>",
        "", ), encoding="utf-8")
    (OUT / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    (OUT / "_headers").write_text(HEADERS, encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    sizes = {p.relative_to(OUT).as_posix(): p.stat().st_size
             for p in sorted(OUT.rglob("*")) if p.is_file()}
    print("public/ built:")
    for k, v in sizes.items():
        print("   %-22s %8.1f KB" % (k, v / 1024))
    print("gated payload: dist-private/payload.bin  %.2f MB (not in public/)"
          % (len(blob) / 1e6))
    return blob


# ------------------------------------------------------------ leak check ---

def leak_check(n=8):
    """Any run of n+ words shared between the public build and articles/."""
    def canon(t):
        t = t.replace("’", "'").replace("—", " ").replace("–", "-")
        t = re.sub(r"<[^>]+>", " ", t)
        t = html.unescape(t)
        t = re.sub(r"[^\w\s'-]", " ", t)
        return re.sub(r"\s+", " ", t).strip().lower()

    idx, front = {}, {}
    for f in (ROOT / "articles").glob("*.md"):
        raw = f.read_text(encoding="utf-8")
        # Body only: frontmatter holds the title, dek, entities and provenance,
        # all of which the architecture publishes on purpose.
        m = re.match(r"\A---\r?\n.*?\r?\n---\r?\n", raw, re.S)
        body = raw[m.end():] if m else raw
        # Keep the frontmatter too: a string present in BOTH body and
        # frontmatter (a headline restated in the lede, a quote used as the
        # title) reached the public site from the metadata, not from the prose.
        front[f.stem] = canon(raw[:m.end()] if m else "")
        w = canon(body).split(" ")
        for i in range(len(w) - n + 1):
            idx.setdefault(" ".join(w[i:i + n]), f.stem)

    approved = [canon(q) for q in APPROVED_QUOTATIONS]

    # Entity names are published metadata. An alphabetical run of them in the
    # facet list will collide with any article that also lists many teams, and
    # that collision is not prose.
    entity_tokens = set()
    for f in (ROOT / "articles").glob("*.md"):
        m = re.search(r'(?m)^entities:\s*(\{.*\})\s*$', f.read_text(encoding="utf-8"))
        if not m:
            continue
        try:
            ents = json.loads(m.group(1))
        except ValueError:
            continue
        for group in ents.values():
            for name in group:
                entity_tokens.update(canon(name).split(" "))
    entity_only = lambda run: all(t in entity_tokens for t in run.split(" "))

    hits, skipped_entity, skipped_meta = [], 0, 0
    for p in sorted(OUT.rglob("*")):
        if not p.is_file() or p.suffix not in (".html", ".css", ".txt", ".json"):
            continue
        w = canon(p.read_text(encoding="utf-8", errors="ignore")).split(" ")
        i = 0
        while i <= len(w) - n:
            key = " ".join(w[i:i + n])
            if key in idx:
                slug = idx[key]
                art = canon((ROOT / "articles" / (slug + ".md")).read_text(encoding="utf-8"))
                j = i + n
                while j < len(w) and " ".join(w[i:j + 1]) in art:
                    j += 1
                run = " ".join(w[i:j])
                if run in front.get(slug, ""):
                    skipped_meta += 1
                elif entity_only(run):
                    skipped_entity += 1
                elif not any(a in run or run in a for a in approved):
                    hits.append((p.relative_to(OUT).as_posix(), run, slug))
                i = j
            else:
                i += 1
    print("leak check: skipped %d runs present in the article's own frontmatter "
          "(title/dek/entities) and %d pure entity-name runs — both are published "
          "metadata, not body prose" % (skipped_meta, skipped_entity))
    return hits


ABOUT = """
<p>Marc Sessler wrote for NFL.com for more than a decade, most of it at Around
the League. Around 2016 the site changed content systems and the URL scheme
changed with it; the old addresses stopped resolving. Nothing was taken down.
It stopped being addressable, which on the internet is much the same thing.</p>

<p>This is what came back out of the Internet Archive: 1,903 articles, his and
his colleagues', recovered one capture at a time, with the provenance of every
one of them recorded. Alongside it is a deterministic analysis of what separates
his prose from theirs — no model, no judgement calls in the scoring, everything
reproducible from the scripts in the repository.</p>

<p>The reader here is complete and public: every title, date, byline, entity,
word count and original URL. The article text itself is not mine to republish,
so it sits behind a passphrase. If you have a reason to read it and no
passphrase, ask.</p>

<p>Built with the Internet Archive's CDX API, which is the only reason any of
this exists. Consider giving them money.</p>
"""

HEADERS = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  Permissions-Policy: geolocation=(), camera=(), microphone=()

/api/*
  Cache-Control: no-store
"""

CSS = """
:root{--paper:#E6E2D6;--ink:#16233A;--dim:#5A6373;--line:#BEB8A6;--panel:#DEDACC;--stamp:#8E2317;
--bg:var(--paper);--fg:var(--ink);--mut:var(--dim);--rule:var(--line);
--mono:"Courier Prime",Courier,monospace;--sans:system-ui,-apple-system,"Segoe UI",sans-serif;
--dirt:multiply;--dirt-op:.055}
@media (prefers-color-scheme:dark){:root{--bg:#101319;--fg:#CDD0C2;--mut:#7E8780;--rule:#2B313A;
--panel:#171C24;--stamp:#C04630;--dirt:soft-light;--dirt-op:.10}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:17px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:inherit}
.grain{position:fixed;inset:0;pointer-events:none;z-index:9;mix-blend-mode:var(--dirt);opacity:var(--dirt-op)}
.grain.a{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E")}
.grain.b{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.011' numOctaves='3'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");opacity:calc(var(--dirt-op)*2.6)}
.sheet{max-width:720px;margin:0 auto;padding:0 24px 96px;position:relative;z-index:1}
.sheet.wide{max-width:960px}
.masthead{padding:52px 0 22px;border-bottom:1px solid var(--rule);margin-bottom:36px}
.wordmark{font-size:30px;font-weight:700;letter-spacing:-.03em;text-decoration:none;display:inline-block}
.wordmark i{font-style:normal;display:inline-block}
.wordmark i:nth-child(2){transform:translateY(1.5px)}
.wordmark i:nth-child(9){opacity:.84}
.stamp{display:inline-block;margin-left:14px;vertical-align:8px;border:2px solid var(--stamp);color:var(--stamp);font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.24em;padding:3px 8px;transform:rotate(-5deg);opacity:.9}
.nav{margin-top:20px;display:flex;flex-wrap:wrap;gap:20px;font-family:var(--mono);font-size:12.5px;letter-spacing:.06em}
.nav a{color:var(--mut);text-decoration:none;padding-bottom:2px;border-bottom:1px solid transparent}
.nav a:hover{color:var(--fg)}
.nav a.on{color:var(--fg);border-bottom-color:var(--stamp)}
.doctitle{font-size:clamp(28px,5vw,40px);line-height:1.12;letter-spacing:-.02em;margin:0 0 10px}
.docsub{color:var(--mut);margin:0 0 34px;font-size:17px}
.doc h2{margin:44px 0 12px;font-size:22px;letter-spacing:-.01em}
.doc h3{margin:32px 0 10px;font-size:18px}
.doc h4{margin:26px 0 8px;font-size:15px;font-family:var(--mono);letter-spacing:.08em;color:var(--mut)}
.doc p{margin:0 0 18px}
.doc hr{border:none;border-top:1px solid var(--rule);margin:40px 0}
.doc code{font-family:var(--mono);font-size:.88em;background:var(--panel);padding:1px 5px;border-radius:2px}
.doc pre{background:var(--panel);border:1px solid var(--rule);padding:14px 16px;overflow-x:auto;border-radius:3px}
.doc pre code{background:none;padding:0}
.doc blockquote{margin:24px 0;padding-left:18px;border-left:2px solid var(--stamp);color:var(--mut)}
.doc ul{margin:0 0 18px;padding-left:22px}
.doc li{margin-bottom:6px}
.doc em{font-style:italic}
.tablewrap{overflow-x:auto;margin:0 0 22px}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{text-align:left;padding:7px 12px 7px 0;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;color:var(--mut);font-weight:700}
.foot{margin-top:72px;border-top:1px solid var(--rule);padding-top:16px;font-size:13.5px;color:var(--mut)}
.foot p{margin:0;max-width:66ch}

/* ---- essay figures. Static: nothing here moves, reveals or parallaxes. ---- */

/* The six cleared quotations. Archivo for what was read; Courier for the
   provenance line, which is machine-recorded fact. Hanging indent so the
   opening mark sits outside the measure. */
.pull{margin:26px 0 26px 0;padding-left:20px;border-left:2px solid var(--stamp)}
.pull blockquote{margin:0;font-size:20px;line-height:1.45;letter-spacing:-.01em;text-indent:-.42em}
.pull blockquote::before{content:"“"}
.pull blockquote::after{content:"”"}
.pull figcaption{margin-top:7px;font-family:var(--mono);font-size:11.5px;color:var(--mut);letter-spacing:.02em}
.pull .sep{opacity:.55;padding:0 2px}

/* Marginal counts. Beside the paragraph on wide screens, inline below it on
   narrow ones. */
.marginnote{font-family:var(--mono);font-size:11.5px;color:var(--mut);
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
  padding:8px 0;margin:0 0 18px}
.mn-head{display:block;letter-spacing:.14em;font-size:10px;opacity:.75;margin-bottom:5px}
.mn-row{display:flex;align-items:baseline;gap:8px;padding:2px 0}
.mn-row b{flex:1;font-weight:400;color:var(--fg);font-family:var(--sans);font-size:13px}
.mn-n{width:34px;text-align:right;color:var(--fg)}
.mn-them{opacity:.6}
@media (min-width:1180px){
  .marginnote{position:absolute;left:calc(100% + 34px);width:210px;margin:0;border:none;
    border-left:1px solid var(--rule);padding:2px 0 2px 14px}
  .doc{position:relative}
}

/* Two-bar figure: the substitution pair. */
.barfig{margin:22px 0 26px;border:1px solid var(--rule);border-radius:3px;padding:16px 18px 12px;background:var(--panel)}
.bf-key{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:var(--mut);margin-bottom:14px}
.bf-k{display:inline-block;width:9px;height:9px;margin:0 6px 0 0;vertical-align:baseline}
.bf-key .bf-k.bf-their{margin-left:18px}
.bf-k.bf-his{background:var(--stamp)}
.bf-k.bf-their{background:var(--mut);opacity:.45}
.bf-row{margin-bottom:12px}
.bf-label{font-size:14.5px;margin-bottom:5px}
.bf-bars{display:flex;flex-direction:column;gap:3px}
.bf-bar{display:flex;align-items:center;gap:8px;height:13px}
.bf-track{flex:1;min-width:0;display:block}
.bf-bar i{display:block;height:11px;flex:none;background:var(--stamp)}
.bf-bar.bf-their i{background:var(--mut);opacity:.45}
.bf-bar em{font-family:var(--mono);font-size:11px;font-style:normal;color:var(--mut);flex:none}
.barfig figcaption,.deadfig figcaption,.yearfig figcaption{margin-top:10px;font-family:var(--mono);font-size:11px;line-height:1.5;color:var(--mut)}

/* The findings that died. Given weight on purpose. */
.deadfig{margin:26px 0 28px;border:1px solid var(--rule);border-left:3px solid var(--stamp);border-radius:3px;padding:16px 18px 12px}
.deadfig h4{margin:0 0 10px;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:var(--stamp)}
.deadfig ul{list-style:none;margin:0;padding:0}
.deadfig li{padding:7px 0;border-bottom:1px dotted var(--rule)}
.deadfig li:last-child{border-bottom:none}
.deadfig s{display:block;font-size:15px;color:var(--fg);opacity:.72;text-decoration-thickness:1px}
.deadfig .why{display:block;font-family:var(--mono);font-size:11px;color:var(--mut);margin-top:3px}

/* Year distribution. Same visual language as the reader's year bar. */
.yearfig{margin:26px 0 28px}
.yf-key{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:var(--mut);margin-bottom:12px}
.yf-k{display:inline-block;width:9px;height:9px;margin:0 6px 0 0}
.yf-key .yf-front{margin-left:18px}
.yf-seed{background:var(--stamp)}
.yf-front{background:var(--mut);opacity:.42}
.yf-plot{display:flex;align-items:flex-end;gap:6px;border-bottom:1px solid var(--rule);padding-bottom:0}
.yf-col{flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:stretch;gap:6px}
.yf-stack{display:flex;flex-direction:column;justify-content:flex-end}
.yf-stack i{display:block;width:100%}
.yf-stack .yf-front{background:var(--mut);opacity:.42}
.yf-stack .yf-seed{background:var(--stamp)}
.yf-year{font-family:var(--mono);font-size:10px;color:var(--mut);text-align:center;padding-top:5px}
"""


if __name__ == "__main__":
    build()
    if "--check" in sys.argv:
        hits = leak_check()
        print()
        if hits:
            print("LEAK CHECK FAILED — %d run(s) of 8+ words from articles/ in public/:" % len(hits))
            for f, run, slug in hits[:20]:
                print('   %s :: "%s"  <- %s' % (f, run[:90], slug))
            sys.exit(1)
        print("leak check: no run of 8+ words from articles/ appears in public/ "
              "outside the %d approved quotations" % len(APPROVED_QUOTATIONS))
