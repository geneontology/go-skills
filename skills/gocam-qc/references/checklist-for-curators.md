# Using the QC checklist: a guide for curators

Hand this to a curator who has received a QC from this skill, or summarise it for them. Claude can also do every step on request.

## 1. What a QC produces

One folder per model, e.g. `~/qc-680ad142/`:

| File | What it is |
|---|---|
| `qc-report-<name>-<id>-<date>.md` / `.html` | the report: findings, what's fine, literature caveat |
| `qc-checklist-<name>-<id>-<date>.html` | the interactive checklist: status, notes, Noctua comments |
| `qc-checklist-<name>-<id>-<date>.md` | the same checklist as editable text, saved on disk |
| `issues.json` | the issue list the checklist is built from |

The QC is read-only: Claude never edits the model. The curator makes the changes in Noctua.

## 2. Filling in the checklist

In the JupyterLab file browser, right-click the checklist `.html` → **Open in New Browser Tab**. A plain double-click shows it read-only, without the controls.

For each issue:
- set the **Status**: Open / Checked (seen, not fixed) / Solved in Noctua / Won't fix / disagree;
- edit the **Noctua comment** if needed, and use **Copy comment** to paste it into Noctua;
- write **notes**: what you checked, why you disagree, what you changed.

The bar at the top shows progress and filters the issues.

**The page cannot save.** Jupyter serves it sandboxed, so ticks and notes last only while the tab is open. Use section 3 or 4 before closing it.

## 3. The shareable report (for a senior curator)

**HTML file**
1. In the checklist, click **Shareable report**, then **Copy**.
2. In JupyterLab: File → New → Text File.
3. Paste, then save it in the same folder with a `.html` name, e.g. `qc-checklist-...-reviewed.html`.
4. Double-click to check it. To send it, right-click → Download, then attach it to an email.

**PDF**
1. Click **Print / PDF view**.
2. Ctrl+P (Cmd+P) → Save as PDF.
3. **Back to checklist** returns to the form, with the answers still there.

The report is read-only: a summary (solved / won't fix / checked / open), then one card per issue with status, severity, Where, Problem, Suggested fix, Noctua comment and notes. It has no scripts, so it opens in any browser and works as an attachment. Send the QC report (`qc-report-....html`) with it, so the reviewer can see the evidence.

A one-click "save to the folder" button was tried (JupyterLab's trusted HTML viewer plus the contents API). It failed in a curator's browser on the hub, so the copy step is deliberate.

## 4. Keeping progress to continue later

- **Export progress (JSON)** → Copy, and paste it into a text file. Next time: **Import progress**, paste, then **Load pasted JSON**.
- **Export progress (Markdown)** gives a readable text version, including the Problem lines.
- Or paste the export to Claude: it saves it as `...-done.md` and renders the read-only HTML (SKILL.md, Follow-up).

## 5. Alternative: the `.md` checklist (saves on disk)

Open `qc-checklist-....md` in the JupyterLab editor. For each issue, change `[ ]` to `[x]`, set `**Status:**` and fill `**My notes:**`, then save with Ctrl+S. To render it:

```bash
uv run python ${CLAUDE_SKILL_DIR}/scripts/checklist_md_to_html.py <checklist.md>
```

This writes an `.html` with the same name next to the `.md`.
