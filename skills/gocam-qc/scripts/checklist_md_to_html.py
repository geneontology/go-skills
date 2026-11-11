"""Render a completed QC checklist (Markdown, as exported by qc_checklist.py or edited by hand) as a read-only, shareable HTML.

Usage: uv run python ${CLAUDE_SKILL_DIR}/scripts/checklist_md_to_html.py done.md [out.html]
No JavaScript: it works in any browser, inside JupyterLab, or as an email attachment.
"""
import re, sys, pathlib, html, collections

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".html")
text = src.read_text()
e = html.escape
title = re.search(r"^# (.+)$", text, re.M).group(1)
sub = (re.search(r"^# .+\n\n(.+?)\n", text, re.M) or [None, ""])[1]
items = []
for blk in re.split(r"^## ", text, flags=re.M)[1:]:
    head, *rest = blk.strip().split("\n")
    m = re.match(r"\[( |x|X)?\]\s+(\S+)\s+\((\w+)\):\s+(.*)", head)
    if not m: continue
    fields = dict(re.findall(r"^- \*\*(.+?):\*\*\s*(.*)$", "\n".join(rest), re.M))
    items.append(dict(done=(m[1] or "").lower() == "x", id=m[2], sev=m[3], title=m[4], **{k.lower(): v.strip() for k, v in fields.items()}))

def status_key(s):
    s = (s or "open").lower()
    return "solved" if "solved" in s else "wontfix" if ("won" in s or "disagree" in s) else "checked" if "checked" in s else "open"
LABEL = {"solved": "Solved in Noctua", "wontfix": "Won't fix / disagree", "checked": "Checked, not fixed", "open": "Open"}
cnt = collections.Counter(status_key(i.get("status")) for i in items)

rows = []
for i in items:
    k = status_key(i.get("status"))
    extra = ""
    for f, lab in [("where", "Where"), ("problem", "Problem"), ("suggested fix", "Suggested fix"), ("noctua comment", "Noctua comment")]:
        if i.get(f) and "(none suggested)" not in i[f]:
            extra += f"<dt>{lab}</dt><dd{' class=nc' if f == 'noctua comment' else ''}>{e(i[f])}</dd>"
    notes = i.get("notes") or i.get("my notes")
    if notes: extra += f"<dt>Curator notes</dt><dd class=notes>{e(notes)}</dd>"
    rows.append(f"""<div class="card {e(i['sev'])} {k}"><div class="head"><span class="st {k}">{'☑' if i['done'] else '☐'} {LABEL[k]}</span>
<span class="tag {e(i['sev'])}">{e(i['sev'])}</span><span class="id">{e(i['id'])}</span><h3>{e(i['title'])}</h3></div><dl>{extra}</dl></div>""")

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{e(title)}</title><style>
:root{{--crit:#b3261e;--maj:#c26a00;--min:#4a6fa5;--opt:#6b7280;--ok:#1e7d4f}}
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:1.5em auto;padding:0 1em;color:#222;line-height:1.45}}
h1{{font-size:1.45em;border-bottom:2px solid #2a6;padding-bottom:.3em}}.sub{{color:#555}}
.sum{{display:flex;gap:.6em;flex-wrap:wrap;margin:1em 0}}.sum span{{padding:.3em .7em;border-radius:5px;font-weight:600;font-size:.9em}}
.solved{{--c:var(--ok)}}.wontfix{{--c:#7a4fa5}}.checked{{--c:#c26a00}}.open{{--c:#b3261e}}
.sum span,.st{{background:color-mix(in srgb,var(--c) 14%,white);color:var(--c);border:1px solid var(--c)}}
.card{{border:1px solid #ddd;border-left:6px solid var(--min);border-radius:6px;margin:.9em 0;padding:.6em 1em}}
.card.critical{{border-left-color:var(--crit)}}.card.major{{border-left-color:var(--maj)}}.card.optional{{border-left-color:var(--opt)}}
.head{{display:flex;gap:.6em;align-items:center;flex-wrap:wrap}}.head h3{{margin:0;font-size:1.02em;flex:1}}
.st{{font-size:.8em;padding:.1em .5em;border-radius:4px;font-weight:600}}
.tag{{font-size:.72em;font-weight:600;text-transform:uppercase;padding:.1em .5em;border-radius:4px;color:#fff;background:var(--min)}}
.tag.critical{{background:var(--crit)}}.tag.major{{background:var(--maj)}}.tag.optional{{background:var(--opt)}}.id{{font-family:monospace;color:#777}}
dl{{display:grid;grid-template-columns:8.5em 1fr;gap:.25em .8em;margin:.5em 0}}dt{{font-weight:600;color:#444}}dd{{margin:0}}
dd.nc{{font-family:ui-monospace,monospace;font-size:.86em;background:#fffdf3;padding:.2em .4em;border-radius:4px}}
dd.notes{{background:#eef6ff;padding:.2em .4em;border-radius:4px;font-style:italic}}
@media print{{.card{{break-inside:avoid}}}}
</style></head><body><h1>{e(title)}</h1><div class="sub">{e(sub)}</div>
<div class="sum"><span class="solved">Solved: {cnt['solved']}</span><span class="wontfix">Won't fix / disagree: {cnt['wontfix']}</span>
<span class="checked">Checked, not fixed: {cnt['checked']}</span><span class="open">Open: {cnt['open']}</span><span style="--c:#444">Total: {len(items)}</span></div>
{''.join(rows)}</body></html>"""
out.write_text(page); print(out, dict(cnt), len(items), "items")
