---
name: gocam-qc
description: Quality-check (QC) an existing GO-CAM model and report the issues without editing it. Use when a curator asks to "QC", "check", "review" or "validate" a GO-CAM model, by id (gomodel:...) or as an exported OWL/Turtle or minerva JSON file. Covers evidence/with consistency, ISS sources, species of the data, references reused out of context, causal relations, term specificity and locations, and changes since an earlier QC or a parent model. Produces a Markdown + HTML report and an interactive tick-box checklist with ready-to-paste Noctua comments.
license: BSD-3-Clause
argument-hint: "[gomodel:ID or path to .ttl/.owl/.json]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/gocam-qc
  maintainer: geneontology
---

# gocam-qc

Review a GO-CAM model the way a second curator would, and hand back a report the curator can act on in Noctua.

**This skill is read-only. It never edits the model**, on any server. The curator makes the changes. If they want to experiment with a fix, that happens in a new model on noctua-dev (see the `noctua` skill), not in theirs.

Related skills: `noctua` (fetch from dev), `amigo` (ISS source annotations), `pubmed-eutils` (abstracts), `gocam-best-practice` (the guidelines the model is judged against; read its `references/` for the activity types in the model).

## Step 1: get the model

Work in a folder per QC, e.g. `~/qc-<first 8 chars of id>/`. Accept, in this order:

1. **A file from the curator** (Noctua "Export OWL"/Turtle, often pasted as `.txt`; or minerva JSON). Copy it into the folder with a timestamped name: curators re-upload under the same name, and you must know which version you checked.
2. **A model id.**
   - Production: `curl -sf -o model.ttl https://raw.githubusercontent.com/geneontology/noctua-models/master/models/<id>.ttl`.
   - Dev: `noctua barista export-model --model <id> -o model.json` (minerva JSON; token per the `noctua` skill). If dev says `UnknownIdentifierException`, the model isn't on dev. Say so plainly (don't call it indexing lag) and use production if it's there.
   - If both exist and differ, ask which one the curator means.

Record the source (file + mtime, or URL + date) in the report header.

## Step 2: dump it

```bash
uv run -q --with rdflib python ${CLAUDE_SKILL_DIR}/scripts/gocam_dump.py <model.ttl|model.json> > dump.txt
```

This prints metadata, individuals (shortened to `…1234` handles), every fact with `code|reference|with`, comments, the lists of classes, entities and `with` values, and **FLAGS**: no evidence, disconnected evidence, duplicated axioms, IC without `with`, circular `with`, recipe/code mismatches, malformed references, title length, leftover model comments. The flags are a starting point. Each one still needs reading in context, and most real issues aren't mechanical.

## Step 3: gather context before judging

Do these in parallel where possible:

- **Earlier QC rounds.** `ls ~ ~/qc-* | grep -i <id prefix>`. Read any `*checklist*.md`, especially `*-done.md`: what the curator solved, what they declined and **why** (the Notes field). Don't re-raise declined items, except references out of context (check E).
- **Parent model.** If the metadata has `wasDerivedFrom`, fetch the parent's current TTL, dump it, and diff the facts (`sed 's/\[…[0-9]*\]//g' | grep -- '-->' | sort`). Fixes made to the parent after the copy are often missing from the child.
- **Terms.** Check the label and obsoletion of every class (OLS MCP / OLS API, or `runoak`). For CC terms used as locations or enablers, look at their parents.
- **ISS sources.** For every ortholog in `with`: `noctua amigo search-annotations -b <ID> -l 300`, and look for an experimental annotation to the same or a more specific term.
- **Literature.** Title and abstract for every PMID (pubmed-eutils). Ask the curator for PDFs of the papers the model rests on. Never fill in figure-level detail from an abstract.

## Step 4: apply the checks

Go through `references/qc-checks.md`:

| | Check group |
|---|---|
| A | Hygiene |
| B | Evidence codes and the `with` field (circular, copy-paste, missing, recipe mismatch) |
| C | ISS / orthology |
| D | Species of the data vs model taxon |
| E | **References reused out of context** (standing check, every PMID) |
| F | Causal relations (direct/indirect need a known mechanism) |
| G | Term choice, specificity, locations, enablers |
| H | Lineage: earlier rounds, parent model, duplicate models |
| I | Literature honesty |

Each finding is: where (the fact, with `…` handles and the evidence), what's wrong (cite paper + figure when you have the full text), the concrete fix in Noctua, and when useful a short Noctua comment (PMID + figure, one or two sentences). Also list **what's fine**; curators need to know which parts passed.

## Step 5: write the deliverables

See `references/deliverables.md` for file names, the `issues.json` schema and the report skeleton.

```bash
S=${CLAUDE_SKILL_DIR}/scripts
# write qc-report-<slug>-<id>-<date>.md and issues.json (from Python, json.dump)
uv run -q --with markdown python $S/md2html.py qc-report-<slug>-<id>-<date>.md
uv run -q python $S/qc_checklist.py issues.json qc-checklist-<slug>-<id>-<date>.html
```

Always deliver all of: report `.md` + `.html`, checklist `.html` + `.md`. Tell the curator to use **"Open in New Browser Tab"** for the checklist's tick boxes. The `.md` checklist is the durable tracker. To send their answers to a reviewer they use the checklist's **Shareable report** (copy into a new `.html`) or **Print / PDF view**; the curator-facing walkthrough is `references/checklist-for-curators.md`.

## Step 6: report back

In the conversation:
- **Where the model came from**, and whether it exists on dev / production.
- **Counts by severity** and the major/critical items, one line each.
- **What changed** since the last QC or the parent.
- **The literature caveat**: full text vs abstract.
- **File paths.**

Keep it short; the detail is in the report.

## Follow-up

- **Curator returns a completed checklist** (pasted export or edited `.md`): save it as `...-done.md` and render the share version with `uv run -q python $S/checklist_md_to_html.py ...-done.md`. Reply to their Notes, especially where they say they don't understand a point (explain it more plainly; don't repeat the same wording).
- **Curator asks how to use, keep or share the checklist**: walk them through `references/checklist-for-curators.md`. The page cannot write files (Jupyter sandbox); don't promise an automatic save.
- **New version of the model**: re-run, keep issue IDs stable where the issue is the same, and add a "What changed since <date>" table.
- **If an earlier report was wrong** (e.g. a parser misread a field), say so at the top of the next report and withdraw the affected findings explicitly.
