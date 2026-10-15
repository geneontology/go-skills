---
name: gocam-review
description: Review or quality-check an existing GO-CAM model by its id or Noctua URL, read-only. Use when a curator asks to review, check, QC, audit or assess a model, especially one in production ("review gomodel:...", "check this model", "what is wrong with this model"). Fetches the model from Noctua's public download route (production by default, noctua-dev on request), runs structural checks and term lookups, applies the GO-CAM validation checklist, and writes a report into the curator's home. It never edits a model and never asks for a Noctua token.
license: BSD-3-Clause
argument-hint: "<gomodel id or Noctua URL> [--dev]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/gocam-review
---

# GO-CAM model review (read-only)

## What this is, and is not

A review of a model that already exists: a production model, or a development
model on noctua-dev that a colleague asked you to look at. The output is a
written report the curator can act on. **This skill changes nothing.** If the
curator wants an edit made, that is their own work in Noctua (production) or
the `noctua` skill on noctua-dev for a model they own; say so and stop there.

Ground rules, in order of importance:

1. **Never ask for, accept or use a production Noctua token.** Reading a
   production model needs none: Noctua serves every model at a public URL.
   If the curator offers a token, decline it and continue without.
2. **Never run `barista`/`noctua` with `--live`**, and never write to any
   model from this skill, including noctua-dev. The only commands this skill
   runs are its own two scripts and read-only lookups.
3. **Say what you checked and what you did not.** Structural checks are
   deterministic; biological judgement is yours and is labelled as such.

## Step 1: identify the model and the environment

Accept any of: `gomodel:ZFIN_ZDB-GENE-991207-22`, a bare id, or a Noctua URL
(editor, form, or download link). Production is the default. Use `--dev`
(noctua-dev) only when the curator says the model is a development model or
gives a noctua-dev URL. If the id is ambiguous, ask once.

Make a working directory for this review:

```bash
R=~/reviews/$(date +%Y-%m-%d)-<id without gomodel:>; mkdir -p "$R"
```

## Step 2: fetch the model

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/fetch_model.sh" "<id or URL>" production "$R"
# or: ... "<id or URL>" dev "$R"
```

This downloads `<id>.ttl` (Noctua's `/download/<id>/owl` route; the body is
Turtle) and `<id>.gpad` over plain HTTP, with no credential. A 400 from Noctua
means the id does not exist there; check the environment and the id before
anything else.

## Step 3: run the structural checks

```bash
uv run --quiet --script "${CLAUDE_SKILL_DIR}/scripts/gocam_qc.py" "$R/<id>.ttl" \
    --gpad "$R/<id>.gpad" --markdown "$R/qc.md" --json "$R/qc.json"
```

Takes a few seconds (longer the first time: term labels come from the OLS
API and are cached under `~/.cache/gocam-review/`). With no network, add
`--offline`; the report then says that terms were not checked. To include
the noctua-models QC queries exactly as production runs them, fetch them
first and pass the directory:

```bash
mkdir -p "$R/sparql" && for q in check-disconnected-individuals check-multiply-reified-edges; do
  curl -fsS -o "$R/sparql/$q.rq" "https://raw.githubusercontent.com/geneontology/noctua-models/master/sparql/$q.rq"; done
# then add:  --sparql-dir "$R/sparql"
```

Read `qc.md`. It gives the model header (title, state, contributors, dates),
every activity with its enabler, process, component, inputs and outputs, the
causal edges between activities with their evidence, the evidence codes and
sources used, every ontology term with its label, obsolete flag and GO
subsets, and a findings list by severity:

- **error**: structural defects production QC rejects (disconnected
  individual, multiply reified edge), obsolete or unknown terms, terms in
  `gocheck_do_not_annotate`.
- **warning**: facts without evidence, evidence without a source, activities
  with no enabler or no process, no causal edge between activities, an
  obsoletion-candidate term.
- **info**: legacy forms (an activity reaching its process by "causally
  upstream of or within" instead of `part of`), component counts, what was
  skipped.

A model converted from classic annotations (one activity per annotation, no
edges between activities, processes reached by "causally upstream of or
within") is a legitimate production model and will show several warnings of
the "no causal edge" kind. Say that plainly rather than listing them as
defects; the review question for such a model is whether it should become a
connected GO-CAM, not whether it is broken.

## Step 4: the judgement pass

Now apply the **Validation Checklist** in the `gocam-best-practice` skill
(read it; do not work from memory) to what `qc.md` shows. For each item,
record one of: holds, does not hold (with the activity or edge concerned),
cannot tell from the model alone. The items that need biology, not structure:

- Is each molecular function the most specific term the evidence supports?
- Do the causal relations match the mechanism (direct vs indirect; `provides
  input for` only when the molecule is not modelled)?
- Are inputs the direct targets?
- Does each evidence code fit what the cited paper shows? For a cited PMID,
  fetch its abstract with the `pubmed-eutils` skill and compare. An abstract
  can refute an evidence code; it cannot confirm one that needs the full
  paper. Write "abstract consistent with" or "abstract does not mention", never
  "confirmed", unless the curator supplies the paper.
- Is the organism consistent across enablers (a cross-organism entity is
  worth a sentence)?
- Are complexes represented per the guidelines?

Do not re-derive the annotations from scratch and do not propose new biology
the curator did not ask about; this is a review of what is there.

## Step 5: write the report

Write `"$R/review.md"` with exactly these sections, then tell the curator the
path and give a three-line summary in the conversation:

```markdown
# Review of gomodel:<id>  (<title>)
Reviewed <date> by Claude (automated checks + reading), read-only. Model state: <state>. Contributors: <...>.

## Summary
Two to five sentences: what the model represents, the most important findings, and whether anything blocks production use.

## Structural findings
The error and warning lines from qc.md, each with one sentence on what it means for this model. Omit infos unless they matter.

## Checklist
One line per item of the gocam-best-practice Validation Checklist: holds / does not hold (where) / cannot tell.

## Evidence
Per causal edge and per key fact: evidence code, source, and whether the abstract (if read) is consistent. State clearly which papers were not read.

## Suggestions for the curator
Concrete, ordered by consequence. Each names the activity or edge and the change. No edits were made.

## What was checked
Scripts run, queries run, terms checked (or "offline"), papers read (abstracts only).
```

Attach nothing to Noctua. If the curator wants to share the review, they can
paste it into the model's Noctua comments themselves, send it to the model's
contributor, or open an issue in the repository their group uses for
annotation review; offer those, do not do them.

## If something fails

- `fetch_model.sh` exits 1 with "no model": wrong id or wrong environment.
  Try the other environment only if the curator agrees that is where it is.
- `gocam_qc.py` exits 2: the file is not Turtle (the route changed, or a
  proxy page was returned). Show the first lines to the curator.
- OLS lookups fail: rerun with `--offline`, and say in the report that term
  validity was not checked.
