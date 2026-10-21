"""Turn a QC issue list (JSON) into (1) a self-contained HTML checklist and (2) an editable Markdown checklist.

Usage: uv run python ${CLAUDE_SKILL_DIR}/scripts/qc_checklist.py issues.json [out.html]

The HTML is fully readable without JavaScript (all issues are rendered statically).
JavaScript only adds status/notes/copy. Jupyter serves files with
"Content-Security-Policy: sandbox allow-scripts", which blocks localStorage,
downloads and dialogs, so: storage falls back to memory with a banner, and export
shows text in a panel to copy instead of downloading. The Markdown checklist
(same basename, -checklist.md) is the durable option: tick [x] and write
comments in the JupyterLab editor; it is saved on disk.
"Shareable report" shows a read-only HTML of the curator's answers to copy into a
new .html file; "Print / PDF view" turns the page into that report for Ctrl+P.
"""
import json, sys, pathlib, html

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "-checklist.html")
md_out = out.with_suffix(".md")
data = json.loads(src.read_text())
m, issues = data["meta"], data["issues"]
e = lambda s: html.escape(s or "")
STAT = {"open": "Open", "checked": "Checked (seen, not fixed)", "solved": "Solved in Noctua", "wontfix": "Won't fix / disagree"}

cards = []
for i in issues:
    opts = "".join(f'<option value="{k}">{v}</option>' for k, v in STAT.items())
    cards.append(f"""<div class="card {e(i['severity'])}" id="c-{e(i['id'])}" data-id="{e(i['id'])}" data-sev="{e(i['severity'])}">
 <div class="head"><input type="checkbox" class="ck js" title="Tick when checked">
  <span class="tag {e(i['severity'])}">{e(i['severity'])}</span><span class="id">{e(i['id'])}</span><h3>{e(i['title'])}</h3>
  <span class="cat">{e(i['category'])}</span><select class="stsel js">{opts}</select></div>
 <dl><dt>Where</dt><dd><span class="where">{e(i['where'])}</span></dd>
  <dt>Problem</dt><dd>{e(i['problem'])}</dd><dt>Suggested fix</dt><dd>{e(i['fix'])}</dd></dl>
 <label class="small">Noctua comment (editable; paste onto the edge/evidence or model)</label>
 <textarea class="nc" placeholder="(no comment suggested; write one if useful)">{e(i.get('comment'))}</textarea>
 <div class="row js"><button class="copy">Copy comment</button><span class="hint copied"></span></div>
 <label class="small js">My notes</label><textarea class="notes js" placeholder="What you checked, decisions, what you changed…"></textarea>
</div>""")

head = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>QC checklist – {e(m['title'])}</title>
<style>
:root{{--crit:#b3261e;--maj:#c26a00;--min:#4a6fa5;--opt:#6b7280;--ok:#1e7d4f}}
*{{box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1150px;margin:1.5em auto;padding:0 1em;color:#222;line-height:1.45}}
h1{{margin:.2em 0;font-size:1.5em;border-bottom:2px solid #2a6;padding-bottom:.3em}}
.meta{{color:#555;font-size:.92em}}.meta code{{background:#f3f3f3;padding:0 .3em;border-radius:3px}}
.banner{{background:#fff4e5;border:1px solid #e6a23c;border-radius:6px;padding:.5em .8em;margin:.6em 0;font-size:.9em}}
.bar{{position:sticky;top:0;background:#fff;z-index:5;padding:.6em 0;border-bottom:1px solid #ddd;display:flex;flex-wrap:wrap;gap:.5em;align-items:center}}
.prog{{flex:1 1 220px;height:14px;background:#eee;border-radius:7px;overflow:hidden;min-width:160px}}
.prog>div{{height:100%;background:var(--ok);width:0;transition:width .3s}}
button,select{{font:inherit;font-size:.88em;padding:.3em .7em;border:1px solid #bbb;border-radius:5px;background:#f7f7f7;cursor:pointer}}
.card{{border:1px solid #ddd;border-left:6px solid var(--min);border-radius:6px;margin:1em 0;padding:.7em 1em;background:#fff}}
.card.critical{{border-left-color:var(--crit)}}.card.major{{border-left-color:var(--maj)}}.card.optional{{border-left-color:var(--opt)}}
.card.solved,.card.wontfix{{opacity:.6;background:#f6fbf8}}
.head{{display:flex;gap:.6em;align-items:center;flex-wrap:wrap}}.head h3{{margin:0;font-size:1.05em;flex:1}}
.tag{{font-size:.75em;font-weight:600;text-transform:uppercase;padding:.1em .5em;border-radius:4px;color:#fff;background:var(--min)}}
.tag.critical{{background:var(--crit)}}.tag.major{{background:var(--maj)}}.tag.optional{{background:var(--opt)}}
.cat{{font-size:.75em;color:#555;border:1px solid #ccc;border-radius:4px;padding:.05em .4em}}.id{{font-family:monospace;color:#777}}
dl{{display:grid;grid-template-columns:7.5em 1fr;gap:.25em .8em;margin:.6em 0}}dt{{font-weight:600;color:#444}}dd{{margin:0}}
.where{{font-family:ui-monospace,monospace;font-size:.88em;background:#f5f5f5;padding:.1em .3em;border-radius:3px}}
label.small{{font-size:.85em;font-weight:600;color:#444;display:block;margin-top:.4em}}
textarea{{width:100%;font:inherit;font-size:.9em;padding:.4em;border:1px solid #ccc;border-radius:5px;min-height:3.2em;resize:vertical}}
textarea.nc{{background:#fffdf3;font-family:ui-monospace,monospace;font-size:.85em}}
.row{{display:flex;gap:.5em;align-items:center;flex-wrap:wrap}}.hint{{font-size:.8em;color:#666}}
#panel{{display:none;border:1px solid #888;border-radius:6px;padding:.6em;margin:.6em 0;background:#fafafa}}#panel textarea{{min-height:16em;font-family:ui-monospace,monospace;font-size:.8em}}
.nojs .js{{display:none!important}}
#review{{display:none}}body.reviewmode>*:not(#review):not(script){{display:none!important}}body.reviewmode #review{{display:block}}
@media print{{.bar,.copy,.noprint{{display:none!important}}.card,.rc{{break-inside:avoid}}}}
</style></head><body class="nojs">
<h1>QC checklist — {e(m['title'])}</h1>
<div class="meta">Model <code>{e(m['model'])}</code> · source <code>{e(m['file'])}</code> · QC {e(m['qc_date'])} · full report: <code>{e(m.get('report',''))}</code><br>{e(m.get('note',''))}</div>
<div class="banner nojs-msg">Interactive features (status, notes, copy) need JavaScript. If you opened this inside JupyterLab, right-click the file → <b>Open in New Browser Tab</b>, or click <b>Trust HTML</b>. The editable Markdown checklist <code>{e(md_out.name)}</code> works everywhere and saves to disk.</div>
<div class="banner js" id="storemsg" style="display:none">This page can't save to browser storage here (Jupyter serves it sandboxed). Your ticks and notes last only until you close the tab. Use <b>Export progress</b> and paste the text into a file, or use <code>{e(md_out.name)}</code> for durable tracking.</div>
<div class="bar js"><div class="prog"><div id="pg"></div></div><span id="pt"></span>
 <select id="flt"><option value="all">Show all</option><option value="open">Open / checked only</option><option value="done">Solved / won't fix</option>
 <option value="critical">Critical</option><option value="major">Major</option><option value="minor">Minor</option></select>
 <button id="cpAll">All Noctua comments</button><button id="exMd">Export progress (Markdown)</button><button id="exJs">Export progress (JSON)</button><button id="imJs">Import progress</button>
 <button id="rpt" title="Read-only page with your ticks, statuses, comments and notes, to send to a reviewer">Shareable report</button><button id="rview">Print / PDF view</button></div>
<div id="review"><div class="row noprint"><button id="rback">← Back to checklist</button><span class="hint">Ctrl/Cmd+P → Save as PDF</span></div><div id="rbody"></div></div>
<div id="panel" class="js"><div class="row"><b id="ptitle"></b><button id="psel">Select all</button><button id="pcopy">Copy</button><button id="pload" style="display:none">Load pasted JSON</button><button id="pclose">Close</button><span class="hint" id="pmsg"></span></div><textarea id="ptext"></textarea></div>
"""

js = """<script id="qcdata" type="application/json">__PAYLOAD__</script>
<script>
document.body.classList.remove('nojs');
const D = JSON.parse(document.getElementById('qcdata').textContent);
const KEY = 'qcchecklist:' + D.meta.key;
let store = null; try { store = window.localStorage; store.setItem(KEY+':t','1'); store.removeItem(KEY+':t'); } catch(e) { store = null; }
if (!store) document.getElementById('storemsg').style.display = '';
let S = {}; try { if (store) S = JSON.parse(store.getItem(KEY) || '{}'); } catch(e) {}
const STAT = {open:'Open', checked:'Checked (seen, not fixed)', solved:'Solved in Noctua', wontfix:"Won't fix / disagree"};
const byId = Object.fromEntries(D.issues.map(i => [i.id, i]));
const st = id => (S[id] = S[id] || {status:'open', notes:'', comment:(byId[id].comment||'')});
function save(){ if (store) try { store.setItem(KEY, JSON.stringify(S)); } catch(e) {} progress(); }
function progress(){ const n=D.issues.length, d=D.issues.filter(i=>['solved','wontfix'].includes(st(i.id).status)).length;
  document.getElementById('pg').style.width=(100*d/n)+'%'; document.getElementById('pt').textContent=d+' / '+n+' done'; }
function paint(c, s){ c.className = 'card ' + c.dataset.sev + ' ' + s.status; c.querySelector('.ck').checked = s.status!=='open'; c.querySelector('.stsel').value = s.status; }
function bind(){
  document.querySelectorAll('.card').forEach(c => {
    const s = st(c.dataset.id), nc = c.querySelector('.nc'), notes = c.querySelector('.notes');
    nc.value = s.comment; notes.value = s.notes; paint(c, s);
    c.querySelector('.stsel').onchange = ev => { s.status = ev.target.value; paint(c, s); save(); filter(); };
    c.querySelector('.ck').onchange = ev => { s.status = ev.target.checked ? (s.status==='open'?'checked':s.status) : 'open'; paint(c, s); save(); filter(); };
    nc.oninput = () => { s.comment = nc.value; save(); };
    notes.oninput = () => { s.notes = notes.value; save(); };
    c.querySelector('.copy').onclick = () => copyText(nc, c.querySelector('.copied'));
  });
  progress(); filter();
}
function filter(){ const f=document.getElementById('flt').value;
  document.querySelectorAll('.card').forEach(c => { const s=st(c.dataset.id).status;
    const show = f==='all' || (f==='open' && ['open','checked'].includes(s)) || (f==='done' && ['solved','wontfix'].includes(s)) || f===c.dataset.sev;
    c.style.display = show ? '' : 'none'; }); }
function copyText(ta, flag){ let ok=false;
  try { ta.focus(); ta.select(); ok = document.execCommand('copy'); } catch(e) {}
  if (!ok && navigator.clipboard) navigator.clipboard.writeText(ta.value).then(()=>{ if(flag) flag.textContent='copied ✓'; }).catch(()=>{});
  if (flag) flag.textContent = ok ? 'copied ✓' : 'selected — press Ctrl/Cmd+C';
  setTimeout(()=>{ if(flag) flag.textContent=''; }, 2500); }
function panel(title, text, loadable){ const p=document.getElementById('panel'); p.style.display='block';
  document.getElementById('ptitle').textContent=title; const t=document.getElementById('ptext'); t.value=text; t.readOnly=!loadable && !!text;
  document.getElementById('pload').style.display = loadable ? '' : 'none'; document.getElementById('pmsg').textContent='';
  if (p.scrollIntoView) try { p.scrollIntoView({behavior:'smooth'}); } catch(e) {} t.focus(); if (text) t.select(); }
function mdExport(){ let md=`# QC checklist: ${D.meta.title}\\n\\nModel ${D.meta.model}; QC ${D.meta.qc_date}; exported ${new Date().toISOString().slice(0,10)}\\n\\n`;
  for (const i of D.issues){ const s=st(i.id);
    md+=`## [${['solved','wontfix'].includes(s.status)?'x':' '}] ${i.id} (${i.severity}): ${i.title}\\n\\n- **Status:** ${STAT[s.status]}\\n- **Where:** ${i.where}\\n- **Problem:** ${i.problem}\\n- **Suggested fix:** ${i.fix}\\n`;
    if (s.comment) md+=`- **Noctua comment:** ${s.comment}\\n`; if (s.notes) md+=`- **Notes:** ${s.notes}\\n`; md+='\\n'; }
  return md; }
document.getElementById('flt').onchange=filter;
document.getElementById('cpAll').onclick=()=>panel('All Noctua comments', D.issues.filter(i=>st(i.id).comment).map(i=>`[${i.id}] ${i.title}\\n${st(i.id).comment}`).join('\\n\\n'));
document.getElementById('exMd').onclick=()=>panel('Progress (Markdown): copy and paste into a .md file', mdExport());
document.getElementById('exJs').onclick=()=>panel('Progress (JSON): copy and keep; paste back with Import', JSON.stringify({key:D.meta.key, saved:new Date().toISOString(), state:S}, null, 1));
document.getElementById('imJs').onclick=()=>panel('Paste progress JSON, then click "Load pasted JSON"', '', true);
document.getElementById('pload').onclick=()=>{ try { const j=JSON.parse(document.getElementById('ptext').value); S=j.state||j; save(); bind();
  document.getElementById('pmsg').textContent = 'loaded ✓' + (j.key && j.key!==D.meta.key ? ' (note: file was for '+j.key+')' : ''); }
  catch(e){ document.getElementById('pmsg').textContent='not valid JSON'; } };
document.getElementById('psel').onclick=()=>{ const t=document.getElementById('ptext'); t.focus(); t.select(); };
document.getElementById('pcopy').onclick=()=>copyText(document.getElementById('ptext'), document.getElementById('pmsg'));
document.getElementById('pclose').onclick=()=>document.getElementById('panel').style.display='none';
const RCSS = `:root{--crit:#b3261e;--maj:#c26a00;--min:#4a6fa5;--opt:#6b7280;--ok:#1e7d4f}
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:1.5em auto;padding:0 1em;color:#222;line-height:1.45}
#rbody h1{font-size:1.45em;border-bottom:2px solid #2a6;padding-bottom:.3em}.sub{color:#555}
.sum{display:flex;gap:.6em;flex-wrap:wrap;margin:1em 0}.sum span{padding:.3em .7em;border-radius:5px;font-weight:600;font-size:.9em}
.r-solved{--c:var(--ok)}.r-wontfix{--c:#7a4fa5}.r-checked{--c:#c26a00}.r-open{--c:#b3261e}
.sum span,.st{background:color-mix(in srgb,var(--c) 14%,white);color:var(--c);border:1px solid var(--c)}
.rc{border:1px solid #ddd;border-left:6px solid var(--min);border-radius:6px;margin:.9em 0;padding:.6em 1em}
.rc.critical{border-left-color:var(--crit)}.rc.major{border-left-color:var(--maj)}.rc.optional{border-left-color:var(--opt)}
.rh{display:flex;gap:.6em;align-items:center;flex-wrap:wrap}.rh h3{margin:0;font-size:1.02em;flex:1}
.st{font-size:.8em;padding:.1em .5em;border-radius:4px;font-weight:600}
.rt{font-size:.72em;font-weight:600;text-transform:uppercase;padding:.1em .5em;border-radius:4px;color:#fff;background:var(--min)}
.rt.critical{background:var(--crit)}.rt.major{background:var(--maj)}.rt.optional{background:var(--opt)}.rid{font-family:monospace;color:#777}
.rc dl{display:grid;grid-template-columns:8.5em 1fr;gap:.25em .8em;margin:.5em 0}.rc dt{font-weight:600;color:#444}.rc dd{margin:0}
dd.rnc{font-family:ui-monospace,monospace;font-size:.86em;background:#fffdf3;padding:.2em .4em;border-radius:4px}
dd.rnotes{background:#eef6ff;padding:.2em .4em;border-radius:4px;font-style:italic;white-space:pre-wrap}
@media print{.rc{break-inside:avoid}}`;
const esc = t => String(t||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function reportBody(){ const today=new Date().toISOString().slice(0,10), cnt={solved:0,wontfix:0,checked:0,open:0};
  const cards = D.issues.map(i => { const s=st(i.id); cnt[s.status]++;
    let dl = `<dt>Where</dt><dd>${esc(i.where)}</dd><dt>Problem</dt><dd>${esc(i.problem)}</dd><dt>Suggested fix</dt><dd>${esc(i.fix)}</dd>`;
    if (s.comment) dl += `<dt>Noctua comment</dt><dd class="rnc">${esc(s.comment)}</dd>`;
    if (s.notes) dl += `<dt>Curator notes</dt><dd class="rnotes">${esc(s.notes)}</dd>`;
    return `<div class="rc ${esc(i.severity)}"><div class="rh"><span class="st r-${s.status}">${['solved','wontfix'].includes(s.status)?'☑':'☐'} ${esc(STAT[s.status])}</span><span class="rt ${esc(i.severity)}">${esc(i.severity)}</span><span class="rid">${esc(i.id)}</span><h3>${esc(i.title)}</h3></div><dl>${dl}</dl></div>`; }).join('\\n');
  return `<h1>QC checklist (completed): ${esc(D.meta.title)}</h1><div class="sub">Model ${esc(D.meta.model)} · QC ${esc(D.meta.qc_date)} · completed ${today} · full report: ${esc(D.meta.report||'')}</div>
<div class="sum"><span class="r-solved">Solved: ${cnt.solved}</span><span class="r-wontfix">Won't fix / disagree: ${cnt.wontfix}</span><span class="r-checked">Checked, not fixed: ${cnt.checked}</span><span class="r-open">Open: ${cnt.open}</span><span style="--c:#444">Total: ${D.issues.length}</span></div>
${cards}`; }
function reportHtml(){ return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>QC checklist (completed): ${esc(D.meta.title)}</title><style>${RCSS}</style></head><body><div id="rbody">${reportBody()}</div></body></html>`; }
(()=>{ const st_=document.createElement('style'); st_.textContent=RCSS.replace(/^body\\{[^}]*\\}/m,''); document.head.appendChild(st_); })();
document.getElementById('rpt').onclick=()=>panel('Shareable report: Copy, then in JupyterLab File → New → Text File, paste, save as <name>.html', reportHtml());
document.getElementById('rview').onclick=()=>{ document.getElementById('rbody').innerHTML=reportBody(); document.body.classList.add('reviewmode'); window.scrollTo(0,0); };
document.getElementById('rback').onclick=()=>document.body.classList.remove('reviewmode');
bind();
</script></body></html>"""

payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out.write_text(head + '<div id="list">\n' + "\n".join(cards) + "\n</div>\n" + js.replace("__PAYLOAD__", payload))

# Editable Markdown checklist: durable, works in the JupyterLab editor
md = [f"# QC checklist: {m['title']}", "",
      f"Model `{m['model']}` · source `{m['file']}` · QC {m['qc_date']} · report `{m.get('report','')}`", "",
      "How to use: change `[ ]` to `[x]` when solved, set **Status** (open / checked / solved / won't fix), "
      "edit the Noctua comment, add notes. Save (Ctrl+S). Right-click → Open With → Markdown Preview for a rendered view.", ""]
for i in issues:
    md += [f"## [ ] {i['id']} ({i['severity']}): {i['title']}", "",
           f"- **Status:** open", f"- **Where:** {i['where']}", f"- **Problem:** {i['problem']}", f"- **Suggested fix:** {i['fix']}",
           f"- **Noctua comment:** {i.get('comment') or '_(none suggested)_'}", "- **My notes:** ", ""]
md_out.write_text("\n".join(md))
print(out); print(md_out)
