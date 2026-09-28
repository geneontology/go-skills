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
  version: "0.1.2"
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

The checkout is *sparse*: an organism directory can exist on disk while some of
its committed reviews are excluded. If the curator turns to a different organism (say
SCHPO after starting with DANRE), hydrate that directory first. Either re-run the
bootstrap with the new organism, or use git directly:

```bash
git -C "$AIGR_HOME" sparse-checkout add genes/SCHPO history/genes/SCHPO
```

This pulls the files for that organism from GitHub on the spot (a few seconds,
tens of MB; SCHPO has about 150 reviewed genes). `git -C "$AIGR_HOME"
sparse-checkout list` shows the selected cones. An exact `genes/<ORGANISM>` entry
includes the whole organism; `genes/<ORGANISM>/<GENE>` includes only one gene.
An organism not yet in the repository can still be added to the sparse selection;
`just fetch-gene` creates its directory when the first gene is fetched. If adding
the cone fails, resolve the error before fetching.

For ortholog/paralog reviews used as references, also re-run the bootstrap with
`AIGR_ORGANISMS="<ORGANISM>"`. If you add an individual gene with
`git sparse-checkout add genes/<ORGANISM>/<GENE>`, follow it by adding the whole
`genes/<ORGANISM>` and `history/genes/<ORGANISM>` cones before fetching any gene
from that organism. The bootstrap's `organisms:` line reports whole organism
cones, not partially populated directories.

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

### Before fetching: distinguish an existing review from a new gene

Before any `just fetch-gene`, check both Git and the working tree. A missing file
on disk does **not** mean a new review: it may be excluded by sparse checkout.
From `$AIGR_HOME`, substitute the actual organism and gene in these commands:

```bash
git cat-file -e HEAD:genes/<ORGANISM>/<GENE>/<GENE>-ai-review.yaml
git status --short -- genes/<ORGANISM>/<GENE>
```

- If `cat-file` succeeds, this is an **existing review to augment**. In a sparse
  checkout, run `git sparse-checkout add genes/<ORGANISM> history/genes/<ORGANISM>`
  and confirm the YAML is on disk before fetching. Read and preserve its reviews.
- If it is absent from `HEAD` but the YAML exists locally, also augment it and
  preserve the local work. If the Git check fails for any reason other than a
  missing path (for example, an invalid `HEAD`), resolve that before proceeding.
- Only if the review is absent from both `HEAD` and disk should you use
  `just fetch-gene <ORGANISM> <GENE>` to seed a new review.

For an existing review, fetch only if its derived data needs refreshing, after
confirming the YAML is present and inspecting the pre-edit status below. Then add
missing GOA rows without replacing existing annotations or their reviews:

```bash
uv run ai-gene-review seed-goa genes/<ORGANISM>/<GENE>/<GENE>-ai-review.yaml
```

Follow the inner skill's **augment an existing review** path. When refreshed GOA
changes a GO_REF, an older row can fail validation as "not in GOA". Compare it
with the replacement GOA row and, when it represents the same annotation with
updated provenance, carry the review onto that row (updating its rationale or
references as needed). Reconcile the obsolete row with the current GOA data; do
not drop the annotation just because its GO_REF changed. Validate the result.

With this existing/new decision made, follow the review skill, substituting
`$ARGUMENTS` for its placeholders.
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

- **Check before fetching or editing.** Run
  `git status --short -- genes/<ORGANISM>/<GENE>` and inspect any existing diff.
  An `M` on a review you have not edited can signal an earlier clobber by
  `fetch-gene`. Compare it with `git show HEAD:genes/<ORGANISM>/<GENE>/<GENE>-ai-review.yaml`
  before continuing. Preserve local work; do not blindly restore over it.
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
- `git add` says paths *"exist outside of your sparse-checkout definition"* → use
  `git add --sparse <paths>` for `publications/`, or add the cone for anything under
  `genes/` or `history/` (`git sparse-checkout add history/genes/<ORG>`), then re-add.
- `gh pr create` fails with *"No commits between main and <branch>"* → the branch
  was pushed with nothing on it; check `git log origin/main..HEAD`, commit, push again.

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
4. **Branch, render, history record — from inside `$AIGR_HOME`.**
   `git fetch origin main && git checkout -b review-<ORGANISM>-<GENE>`. Re-run
   `just render <ORGANISM> <GENE>` so the committed HTML matches the final YAML.
   Scaffold the history record the repository requires:
   `just new-history --kind gene --organism <ORGANISM> --slug <GENE> --event CREATE
   --outcome changed --summary "Create review: <ORGANISM> <GENE>" --agent-tool
   claude-code --model <model> --details "<one paragraph>"`, then
   `just validate-history <path it printed>`. Use `--event EDIT` and a summary such
   as `Re-review <GENE> against current GOA` when you augmented an existing review;
   add `--issue N` or `--url <URL>` for anything the work relates to. Never write
   the record's filename or session id by hand.
5. **Stage explicitly; never `git add -A`.** The sparse checkout refuses paths
   outside its cones with *"matched paths that exist outside of your
   sparse-checkout definition, so will not be updated in the index"*, and
   `publications/` is never in a cone. Run these as separate commands, not one
   `&&` chain, so a refusal cannot silently skip the commit:

   ```bash
   git add genes/<ORGANISM>/<GENE> history/genes/<ORGANISM>/<GENE>
   git add --sparse $(git status --short | awk '$1=="??" && $2 ~ /^publications\//{print $2}')
   git diff --cached --name-status
   ```

   `--sparse` (git 2.35+) stages files outside the cones without hydrating the
   whole directory. Include only the newly cached `publications/PMID_*.md` your
   review quotes; CI's reference validator needs them. Leave out `uv.lock`,
   `cache/go/terms.csv`, and re-fetched copies of already-tracked publications
   whose diff is whitespace only (`git diff --stat publications/` shows them):
   the environment sync and the validator touch these as side effects. The PR
   template says not to commit derived files, yet the repository tracks
   `*-goa.tsv`, `*-uniprot.txt` and the rendered HTML for every review; include
   the gene directory as `fetch-gene` and `render` produced it, and say so in the
   PR body. Read the staged list back before committing.
6. **Commit and confirm there is something to push.** Commit with a message of the
   form `Create gene review: <ORGANISM> <GENE>` (or `Re-review ...`). Then run
   `git log origin/main..HEAD --oneline`; if it prints nothing, the commit did not
   happen (usually a refused `git add` earlier). Do not push until it lists your
   commit.
7. **Push and open the PR.** `git push -u origin review-<ORGANISM>-<GENE>`, then
   `gh pr create --repo ai4curation/ai-gene-review --head review-<ORGANISM>-<GENE>
   --base main --fill` and edit the body to follow the repository's PR template
   (`.github/PULL_REQUEST_TEMPLATE.md`: summary with `Closes #N` if a tracking
   issue exists, `just validate` output, test plan). Pass `--head` explicitly;
   without it `gh` sometimes claims the branch was not pushed. A *"Warning: N
   uncommitted changes"* from `gh` refers to the side-effect files you left
   unstaged and is fine. *"No commits between main and <branch>"* means the
   branch was pushed empty: go back to step 6.
8. **Link the PR from the history record.** Append the PR URL to `links.prs` in
   the record from step 4, run `just validate-history` on it again, commit
   (`History record: link PR #N`), and push. Records are append-only for their
   target path, but adding links before merge is expected.
9. **Report the PR URL** and tell the curator that CI will validate the review and a
   maintainer will look at it; they do not need to do anything further.

If the push is refused with a permissions error, the curator does not have write
access yet. Do not try to fork around it; point them back to Chris or Seth.
