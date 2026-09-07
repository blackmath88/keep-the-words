#!/usr/bin/env python3
"""
build_reader.py — Step 3 of the Sessler archive pipeline.

Reads articles/*.md, embeds everything into one self-contained HTML file.
No server needed — double-click sessler-archive.html.
"""

import json, os, re, glob, html, time

INDIR = "articles"
OUT = "sessler-archive.html"


def parse_md(path):
    raw = open(path, encoding="utf-8").read()
    if not raw.startswith("---"):
        return None
    _, fm, body = raw.split("---", 2)
    meta, prov, in_prov = {}, {}, False
    for line in fm.strip().splitlines():
        if line.strip() == "provenance:":
            in_prov = True
            continue
        m = re.match(r'^(\s*)([a-z_]+):\s*(.*)$', line)
        if not m:
            continue
        indent, k, v = m.groups()
        v = v.strip()
        if v.startswith('"') and v.endswith('"') and len(v) > 1:
            v = v[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        (prov if (in_prov and indent) else meta)[k] = v
    meta["provenance"] = prov
    meta["body"] = body.strip()
    return meta


def norm_date(s):
    if not s:
        return ""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return m.group(0)
    m = re.search(r"([A-Z][a-z]{2})\w*\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        mo = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(m.group(1)) + 1
        return f"{m.group(3)}-{mo:02d}-{int(m.group(2)):02d}"
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return m.group(0) + "-01-01" if m else ""


def md_to_html(md):
    out = []
    for block in md.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        e = html.escape(b)
        e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
        e = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", e)
        if b.startswith("#"):
            lvl = len(b) - len(b.lstrip("#"))
            out.append(f"<h{lvl}>{e.lstrip('#').strip()}</h{lvl}>")
        elif b.startswith("- "):
            items = "".join(f"<li>{html.escape(l[2:])}</li>"
                            for l in b.splitlines() if l.startswith("- "))
            out.append(f"<ul>{items}</ul>")
        elif b.startswith("> "):
            out.append(f"<blockquote>{e.lstrip('&gt; ')}</blockquote>")
        else:
            out.append(f"<p>{e}</p>")
    return "".join(out)


def main():
    arts = []
    for p in sorted(glob.glob(os.path.join(INDIR, "*.md"))):
        m = parse_md(p)
        if not m:
            continue
        d = norm_date(m.get("date", ""))
        arts.append({
            "t": m.get("title", ""),
            "d": m.get("dek", ""),
            "date": d,
            "y": d[:4] if d else "undated",
            "by": m.get("byline", ""),
            "v": m.get("byline_verified") == "true",
            "wc": int(m.get("word_count") or 0),
            "p": m.get("provenance", {}),
            "h": md_to_html(m["body"]),
        })
    arts.sort(key=lambda a: a["date"] or "0000", reverse=True)
    years = sorted({a["y"] for a in arts}, reverse=True)
    built = time.strftime("%Y-%m-%d")

    doc = TEMPLATE.replace("__DATA__", json.dumps(arts, ensure_ascii=False)) \
                  .replace("__YEARS__", json.dumps(years)) \
                  .replace("__COUNT__", str(len(arts))) \
                  .replace("__BUILT__", built)
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"wrote {OUT} — {len(arts)} articles, {os.path.getsize(OUT)//1024} KB")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Marc Sessler — Archive</title>
<style>
:root{
  --bg:#12100e; --panel:#1a1815; --line:#2e2a26; --ink:#eae4dc;
  --dim:#8f8579; --accent:#c8622f; --accent2:#5a8b7d;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
#shell{display:grid;grid-template-columns:360px 1fr;height:100vh}
#side{border-right:1px solid var(--line);display:flex;flex-direction:column;
  background:var(--panel);min-width:0}
header{padding:20px 18px 14px;border-bottom:1px solid var(--line)}
h1{margin:0;font:600 15px/1.2 sans-serif;letter-spacing:.14em;text-transform:uppercase}
h1 span{color:var(--accent)}
.sub{color:var(--dim);font-size:12px;margin-top:6px}
.controls{padding:12px 18px;border-bottom:1px solid var(--line);display:grid;gap:8px}
input,select{width:100%;padding:9px 11px;background:var(--bg);color:var(--ink);
  border:1px solid var(--line);border-radius:5px;font-size:14px;outline:none}
input:focus,select:focus{border-color:var(--accent)}
.row{display:flex;gap:8px}
label.chk{display:flex;align-items:center;gap:7px;color:var(--dim);font-size:12px;cursor:pointer}
#list{overflow-y:auto;flex:1}
.item{padding:13px 18px;border-bottom:1px solid var(--line);cursor:pointer}
.item:hover{background:#221f1b}
.item.on{background:#241f1a;box-shadow:inset 3px 0 0 var(--accent)}
.item .ti{font-size:14px;line-height:1.35;margin-bottom:5px}
.item .me{font-size:11px;color:var(--dim);display:flex;gap:9px;flex-wrap:wrap}
.dot{width:5px;height:5px;border-radius:50%;background:var(--accent2);display:inline-block;
  align-self:center}
.dot.no{background:#6b5a4a}
#main{overflow-y:auto;padding:56px 0 120px}
article{max-width:680px;margin:0 auto;padding:0 32px;
  font-family:Georgia,"Times New Roman",serif;font-size:19px;line-height:1.72}
article h2{font-size:31px;line-height:1.22;margin:0 0 14px;font-family:inherit}
article h3,article h4{font-size:22px;margin:34px 0 10px}
article p{margin:0 0 22px}
article blockquote{margin:24px 0;padding-left:20px;border-left:3px solid var(--accent);
  color:#cfc6ba;font-style:italic}
article ul{padding-left:22px}article li{margin-bottom:10px}
.dek{color:var(--dim);font-size:18px;font-style:italic;margin:0 0 22px}
.meta{font-family:sans-serif;font-size:12px;color:var(--dim);
  padding-bottom:20px;margin-bottom:30px;border-bottom:1px solid var(--line);
  display:flex;gap:14px;flex-wrap:wrap}
.prov{margin-top:56px;padding:18px 20px;background:var(--panel);
  border:1px solid var(--line);border-radius:7px;
  font-family:ui-monospace,Menlo,monospace;font-size:11.5px;line-height:1.85;color:var(--dim)}
.prov b{color:var(--accent2);font-weight:600;letter-spacing:.1em;
  display:block;margin-bottom:9px;text-transform:uppercase;font-size:10px}
.prov a{color:var(--accent);word-break:break-all}
.prov div{display:grid;grid-template-columns:130px 1fr;gap:4px}
.empty{color:var(--dim);text-align:center;padding-top:100px;font-size:14px}
mark{background:var(--accent);color:#fff;border-radius:2px}
@media(max-width:820px){#shell{grid-template-columns:1fr}#side{height:44vh}
  #main{height:56vh}article{padding:0 20px;font-size:17px}}
</style></head><body>
<div id="shell">
  <div id="side">
    <header>
      <h1>Marc <span>Sessler</span></h1>
      <div class="sub">__COUNT__ pieces · personal archive · built __BUILT__</div>
    </header>
    <div class="controls">
      <input id="q" placeholder="Search titles and full text…">
      <div class="row">
        <select id="yr"></select>
        <select id="sort">
          <option value="new">Newest</option>
          <option value="old">Oldest</option>
          <option value="long">Longest</option>
        </select>
      </div>
      <label class="chk"><input type="checkbox" id="vo"> Verified byline only</label>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"><div class="empty">Select a piece from the left.</div></div>
</div>
<script>
const A = __DATA__, YEARS = __YEARS__;
const $ = s => document.querySelector(s);
const esc = s => (s||"").replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
$("#yr").innerHTML = '<option value="">All years</option>' +
  YEARS.map(y => `<option>${y}</option>`).join("");
let cur = null;

function filtered(){
  const q = $("#q").value.trim().toLowerCase(), y = $("#yr").value, vo = $("#vo").checked;
  let r = A.filter(a =>
    (!y || a.y === y) && (!vo || a.v) &&
    (!q || (a.t+" "+a.d+" "+a.h).toLowerCase().includes(q)));
  const s = $("#sort").value;
  if(s === "old") r = r.slice().sort((x,z) => (x.date||"9").localeCompare(z.date||"9"));
  if(s === "long") r = r.slice().sort((x,z) => z.wc - x.wc);
  return r;
}
function renderList(){
  const r = filtered();
  $("#list").innerHTML = r.length ? r.map((a,i) => `
    <div class="item${a===cur?' on':''}" data-i="${A.indexOf(a)}">
      <div class="ti">${esc(a.t)}</div>
      <div class="me"><span class="dot${a.v?'':' no'}"></span>
        <span>${a.date||'undated'}</span><span>${a.wc} words</span>
        <span>${a.p.source_type||''}</span></div>
    </div>`).join("") : '<div class="empty">No matches.</div>';
  $("#list").querySelectorAll(".item").forEach(el =>
    el.onclick = () => open(A[+el.dataset.i]));
}
function open(a){
  cur = a;
  const p = a.p || {};
  const row = (k,v) => v ? `<div><span>${k}</span><span>${v}</span></div>` : "";
  const link = u => u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>` : "";
  $("#main").innerHTML = `<article>
    <h2>${esc(a.t)}</h2>
    ${a.d ? `<p class="dek">${esc(a.d)}</p>` : ""}
    <div class="meta"><span>${a.date||'undated'}</span>
      <span>${esc(a.by)||'byline not parsed'}</span>
      <span>${a.wc} words</span>
      <span>${a.v?'byline verified':'byline UNVERIFIED'}</span></div>
    ${a.h}
    <div class="prov"><b>Provenance</b>
      ${row("original", link(p.original_url))}
      ${row("retrieved from", link(p.retrieved_from))}
      ${row("source", esc(p.source_type))}
      ${row("wayback ts", esc(p.wayback_timestamp))}
      ${row("http status", esc(p.http_status))}
      ${row("extractor", esc(p.body_selector))}
      ${row("retrieved at", esc(p.retrieved_at))}
      ${row("found via", link(p.discovery_capture))}
    </div></article>`;
  $("#main").scrollTop = 0;
  renderList();
}
["q","yr","sort","vo"].forEach(id => {
  $("#"+id).addEventListener("input", renderList);
  $("#"+id).addEventListener("change", renderList);
});
renderList();
</script></body></html>"""

if __name__ == "__main__":
    main()
