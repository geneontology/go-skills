# QC deliverables and formats

Curators read QC output in JupyterLab, in a browser. Produce, in one folder per QC (e.g. `~/qc-<model-id-prefix>/`):

| File | Made with | Purpose |
|---|---|---|
| `qc-report-<slug>-<id>-<date>.md` | written by you | the report |
| `qc-report-<slug>-<id>-<date>.html` | `md2html.py` | readable styled version |
| `issues.json` | written by you | the issue list |
| `qc-checklist-<slug>-<id>-<date>.html` | `qc_checklist.py` | interactive tick-box checklist |
| `qc-checklist-<slug>-<id>-<date>.md` | `qc_checklist.py` (written alongside) | the **durable** tracker; the curator ticks `[x]`, sets Status, writes Notes |
| `<...>-done.html` | `checklist_md_to_html.py` | read-only, shareable rendering of a completed checklist |

`<slug>` = a short name for the model (gene/pathway); `<date>` = YYYY-MM-DD.

## issues.json

```json
{
 "meta": {"model": "gomodel:6ab5999400001606", "file": "where the model came from",
          "title": "model title", "qc_date": "2026-10-06",
          "report": "qc-report-....html", "key": "unique-key-for-this-qc",
          "note": "literature caveat: which papers were read in full"},
 "issues": [
  {"id": "N1", "severity": "critical|major|minor|optional", "category": "evidence|reference-context|species|relation|term|location|hygiene|model",
   "title": "short claim", "where": "subject (…1234) —relation→ object (…5678) [code|ref|with]",
   "problem": "what is wrong and why, citing the paper",
   "fix": "concrete change in Noctua",
   "comment": "ready-to-paste Noctua evidence comment, PMID + figure, or empty"}
 ]
}
```

Write it from Python (`json.dump(..., ensure_ascii=False, indent=1)`), not by hand, so quoting stays valid. IDs: a letter per group (e.g. C critical / M major / m minor, or N new / P parent / R reference) plus a number. Keep IDs stable when you re-run a QC on a new version, so curators can match them.

## Commands

```bash
S=${CLAUDE_SKILL_DIR}/scripts
uv run -q --with markdown python $S/md2html.py qc-report-....md
uv run -q python $S/qc_checklist.py issues.json qc-checklist-....html     # also writes the .md
uv run -q python $S/checklist_md_to_html.py qc-checklist-...-done.md      # read-only share version
```

## Jupyter constraints (why the HTML is built this way)

Jupyter serves files with `Content-Security-Policy: sandbox allow-scripts`: no localStorage, no downloads, no dialogs. The JupyterLab HTML viewer also blocks scripts unless the file is trusted. So:
- every issue is rendered **statically**, and JS only adds status/notes/copy (a JS-only version showed up empty);
- export is a copy panel, not a download. The same goes for **Shareable report** (a read-only HTML of the answers, which the curator pastes into a new `.html` file). **Print / PDF view** shows that report in the page for Ctrl+P;
- tell the curator to use **"Open in New Browser Tab"** for the interactive features;
- the `.md` checklist is what persists, so read it back to know what the curator has resolved.

## Report skeleton

```markdown
# QC report: gomodel:<id>
**Title:** … **State:** … **Date:** … **Contributor:** …
**Taxon:** … **Derived from:** …
**QC date:** … | **Reviewer:** claude (read-only; no edits made)
**Source:** where the TTL/JSON came from (file + date / commit)
**Checklist:** file names

## Summary
units / individuals / facts / evidence counts; hygiene in one line; what changed since last QC; one table: ID | Sev | Issue

## Findings
### <ID>. <title> (<severity>)
fact(s) affected, the problem citing paper+figure, the fix

## Decisions kept from earlier rounds   (won't-fix items, one line each)
## What's fine
## Literature caveat   (full text vs abstract only)
```
