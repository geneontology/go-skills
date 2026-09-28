---
name: gene-review
description: >
  Review the Gene Ontology annotations of a gene using the ai4curation/ai-gene-review
  toolkit: fetch UniProt and EBI-GOA data, cache the literature, judge every existing
  annotation (ACCEPT / MODIFY / REMOVE / NEW ...), and write a validated
  GENE-ai-review.yaml. Use when a curator asks to "review", "audit", "check" or
  "curate" the GO annotations of a gene or gene product in any organism (e.g. "review
  DANRE fezf2", "audit the GO terms on human TP53"), or asks for a gene review, an
  annotation review, or an ai-gene-review. Works from any directory; sets up its own
  checkout of ai-gene-review on first use.
license: BSD-3-Clause
compatibility: >
  Designed for Claude Code. Requires git, network access, and either uv or curl
  (to install uv). No GitHub credentials needed to review; only to open a PR.
argument-hint: "[ORGANISM] [GENE_SYMBOL]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/gene-review
  toolkit: https://github.com/ai4curation/ai-gene-review
  maintainer: geneontology
---

# Gene review (ai-gene-review, from anywhere)

This skill is a **front door**. The review method, guidelines, validators and
scripts all live in the `ai4curation/ai-gene-review` repository; this skill makes
sure a (partial) checkout of it exists (usually in ~/ai-gene-review), then hands you over to the skills inside it. Do not
re-derive the method from memory: read the inner skills and follow them.

Arguments: `$ARGUMENTS` — a uniprot organism code and a gene symbol, e.g. `DANRE fezf2`,
`human TP53`, `PSEPK PP_4218`. If either is missing, ask before doing anything else.
Organism codes are UniProt species mnemonics (`DANRE`, `MOUSE`, `SCHPO`, ...) except
for a few lowercase GO names (`human`, `mouse`, `yeast`, `worm`).

If the user just wants to explore, then seed using DANRE as it is quite small.

## Step 1 — make sure the toolkit is ready

Run the bootstrap script. It is idempotent and prints a status block.

```bash
AIGR_ORGANISMS="<ORGANISM>" bash "${CLAUDE_SKILL_DIR}/scripts/bootstrap.sh"
```

What it does: clones `ai-gene-review` into `$AIGR_HOME` (default `~/ai-gene-review`)
as a small sparse checkout if absent, adds the organism's `genes/` directory, installs
`uv` and `just` if missing, and syncs the Python environment. First run takes a few
minutes; later runs a few seconds. Tell the user it is a one-off when it is slow.

Read the status block. In particular:

- **`deep research: unavailable`** means the automated literature-synthesis step of
  the review will fail. That is expected in many environments. You will synthesise
  the literature yourself from the cached papers and record that in the gene's
  `-notes.md` file, exactly as the inner skill instructs for that case.
- If the script fails outright, report the error verbatim and stop.

Then `cd "$AIGR_HOME"` (or `cd ~/ai-gene-review`). **Every `just` command below must
run from inside that directory.** The shell keeps its working directory between your
commands, so one `cd` is enough; re-`cd` if you move elsewhere.

## Adding another organism to the checkout

The checkout is *sparse*: only the organism directories that have been asked for
exist on disk under `genes/`. If the curator turns to a different organism (say
SCHPO after starting with DANRE), hydrate that directory first. Either re-run the
bootstrap with the new organism, or use git directly:

```bash
git -C "$AIGR_HOME" sparse-checkout add genes/SCHPO history/genes/SCHPO
```

This pulls the files for that organism from GitHub on the spot (a few seconds,
tens of MB; SCHPO has about 150 reviewed genes). `git -C "$AIGR_HOME"
sparse-checkout list` shows what is currently hydrated. If the organism has no
directory in the repository yet, the command fails harmlessly and `just fetch-gene`
creates it when the first gene is fetched.

Ignore a warning of the form *"paths are not up to date and were left despite
sparse patterns"* naming files under `publications/`. It is cosmetic: the
validator caches papers there on demand, outside the sparse set. The command
still succeeded.

## Step 2 — load the method

The repository's own instructions are not loaded automatically when you start
outside it. Read these before touching any YAML, in this order:

1. `$AIGR_HOME/CLAUDE.md` — from the heading **"Gene Review Guidelines"** to the end.
   It defines the action vocabulary, the "do not overrule curators from incomplete
   evidence" and "do not add what curators deliberately declined to add" rules, how
   IBA annotations are to be read, and how references are reviewed.
2. `$AIGR_HOME/.claude/skills/review/SKILL.md` — the step-by-step review workflow.
3. `$AIGR_HOME/.claude/skills/annotation-reviewer/SKILL.md` — how to judge each
   annotation and fill in `existing_annotations[].review`.

Follow the review skill literally, substituting `$ARGUMENTS` for its placeholders.
Where it says to invoke the annotation-reviewer subagent, do that work yourself
following the annotation-reviewer skill, unless a subagent is available to you.

## Step 3 — other tasks in the same toolkit

Route by what the curator asks for. Read the named file, then follow it.

| Curator wants | Read |
|---|---|
| review a gene's GO annotations (default) | `.claude/skills/review/SKILL.md` + `annotation-reviewer/SKILL.md` |
| ADVANCED: review computational function predictions (ProtNLM, InterPro2GO, ...) | `.claude/skills/review-function-prediction/SKILL.md` |
| ADVANCED: review a UniProt ARBA / UniRule rule | `.claude/skills/rule-reviewer/SKILL.md` |
| summarise what cited papers say about a gene | `.claude/skills/reference-findings-summarizer/SKILL.md` |
| ADVANCED: a pathway summary after a review | `.claude/skills/pathway-inference-agent/SKILL.md` |
| ADVANCED: curate a module (pathway/complex) or a GO-CAM review | `.claude/skills/module-curation/SKILL.md`, `.claude/skills/gocam-curation/SKILL.md` |

Paths are relative to `$AIGR_HOME`. Skills not listed here (`boss`, `pm`,
`aigr-pr-review`, ...) are for repository maintainers; leave them unless asked.

## Step 4 — render the review as HTML and show it to the curator

The YAML is the record, but it is not pleasant to read. Once a review validates,
render it:

```bash
just render <ORGANISM> <GENE>
```

This writes `genes/<ORGANISM>/<GENE>/<GENE>-ai-review.html` next to the YAML and
prints the path. Re-run it after any further edit; it overwrites.

Curators usually cannot open a file path you print. Walk them to it in JupyterLab:

1. In the **file browser on the left**, if it is not showing your home directory,
   click the folder icon at the top of the path bar to go there.
2. Open `ai-gene-review`, then `genes`, then the organism folder, then the gene
   folder (for `DANRE fezf2`: `ai-gene-review › genes › DANRE › fezf2`).
3. **Double-click `<GENE>-ai-review.html`.** It opens in a new tab as a rendered
   page. If JupyterLab shows the raw HTML source instead, right-click the file and
   choose **Open With › HTML Viewer**.
4. If the page shows a **"Trust HTML"** button in its toolbar, tell the curator it
   is safe to click: the file was generated locally from their review and the
   button only enables the page's own styling and scripts.
5. The `<GENE>-notes.md` in the same folder opens the same way (double-click gives
   a rendered Markdown preview; **Open With › Editor** shows the source).

If the file browser does not yet show a file you just created, click the refresh
icon at the top of the browser; it does not always update on its own.

## Rules that apply because you are running from outside the repository

- **Validate explicitly.** Inside the repo, hooks validate a review file on every
  edit. Those hooks do not fire here. After every edit to `*-ai-review.yaml`, run
  `just validate <ORGANISM> <GENE>` and fix what it reports before moving on.
- **Never hand-edit derived files** (`*-uniprot.txt`, `*-goa.tsv`,
  `*-deep-research-*.md`, `publications/*`). Regenerate them with `just fetch-gene`
  or `just fetch-gene-pmids`.
- **Never write a file named `*-deep-research-<provider>.md` yourself.** If deep
  research is unavailable, your synthesis goes in `<GENE>-notes.md`.
- **Do not commit or push unless the curator asks.** Reviewing needs no GitHub
  identity. If they do ask, check `gh auth status` and `git config user.email` first
  and tell them plainly what is missing rather than trying to work around it.
- **Report where things landed.** When done, tell the curator the absolute paths of
  the review YAML and notes file, the validation result, and whether deep research
  ran or was replaced by manual synthesis.

## If something is off

- `just: command not found` after bootstrap → `export PATH="$HOME/.local/bin:$PATH"`.
- Validation complains that `file:` references or GO_REFs cannot be resolved → the
  checkout is missing `conf/`; run `git -C "$AIGR_HOME" sparse-checkout add conf`.
- The organism directory is missing → `git -C "$AIGR_HOME" sparse-checkout add genes/<ORG>`;
  if the organism is new to the repo, `just fetch-gene` creates it.
- To force a full working tree: `AIGR_FULL=1` on the bootstrap (about 4 GB).

## Advanced — contributing a review back

**By default the checkout is read-only in practice.** It is a public clone over
HTTPS with no credentials attached, and pushing to `ai4curation/ai-gene-review`
requires the curator's GitHub account to have been added to that repository. **For
now the primary purpose of this skill is exploration**; reviews live in the
curator's home directory. If a curator would like their review to become part of
the project, the simplest route is to **contact Chris Mungall or Seth Carbon** and
they will arrange access or take the files from there. Say this before starting
any of the steps below, and only continue if the curator explicitly wants to.

If they do, every step below involves GitHub authentication and each can fail in
ways that need the curator's action. Go one step at a time, show them what you are
running, and stop at the first thing that does not work rather than improvising.

1. **GitHub login for `gh`.** `gh auth status`. If not logged in, run
   `gh auth login --hostname github.com --git-protocol https --web`, read the
   one-time code from its output, and tell the curator: *open
   https://github.com/login/device in a new browser tab, enter this code, and
   authorize*. Wait, then re-check `gh auth status`.
2. **Let git use that login.** `gh auth setup-git` (once per user). Without it
   `git push` fails with *could not read Username*.
3. **Git identity.** `git config --global user.name` and `user.email`; if either is
   empty, take the name from `gh api user --jq .name` and ask the curator which
   email to use (their GitHub noreply address is fine if they prefer privacy).
4. **Branch and commit, from inside `$AIGR_HOME`.** `git checkout -b
   review-<ORGANISM>-<GENE>`. Scaffold a history record as the repository requires:
   `just new-history --kind gene --organism <ORGANISM> --slug <GENE> --event CREATE
   --outcome changed --summary "Create review: <ORGANISM> <GENE>" --agent-tool
   claude-code --model <model> --details "<one paragraph>"`, then `just
   validate-history <path it printed>`. Add `genes/<ORGANISM>/<GENE>/`,
   `history/genes/<ORGANISM>/<GENE>/`, and the `publications/PMID_*.md` files the
   review cites; commit with a message of the form `Create gene review: <ORGANISM>
   <GENE>`.
5. **Push and open the PR.** `git push -u origin review-<ORGANISM>-<GENE>`, then
   `gh pr create --repo ai4curation/ai-gene-review --head review-<ORGANISM>-<GENE>
   --base main --fill` and edit the body to follow the repository's PR template
   (`.github/PULL_REQUEST_TEMPLATE.md`: summary, `just validate` output, test plan).
   Pass `--head` explicitly; without it `gh` sometimes claims the branch was not
   pushed.
6. **Report the PR URL** and tell the curator that CI will validate the review and a
   maintainer will look at it; they do not need to do anything further.

If the push is refused with a permissions error, the curator does not have write
access yet. Do not try to fork around it; point them back to Chris or Seth.
