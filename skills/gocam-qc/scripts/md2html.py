"""Render a Markdown QC report as a styled, standalone HTML file next to it.

Usage: uv run --with markdown python ${CLAUDE_SKILL_DIR}/scripts/md2html.py report.md
"""
import sys, markdown, pathlib
src = pathlib.Path(sys.argv[1]); out = src.with_suffix(".html")
body = markdown.markdown(src.read_text(), extensions=["tables", "fenced_code", "sane_lists"])
css = """body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:2em auto;padding:0 1em;line-height:1.5;color:#222}
h1{border-bottom:2px solid #2a6;padding-bottom:.3em}h2{border-bottom:1px solid #ccc;margin-top:1.8em}h3{color:#a33}
table{border-collapse:collapse;margin:1em 0;width:100%}th,td{border:1px solid #ccc;padding:.4em .6em;vertical-align:top;text-align:left}
th{background:#eef5f0}tr:nth-child(even) td{background:#fafafa}code{background:#f3f3f3;padding:.1em .3em;border-radius:3px}"""
out.write_text(f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{src.stem}</title><style>{css}</style></head><body>{body}</body></html>")
print(out)
