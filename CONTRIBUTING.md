# Contributing to go-skills

This repository holds the canonical GO curation skills. On the GO AI Hub every
curator's `~/.claude/skills` links to a read-only checkout of `main`, so a merge
here reaches all of them within minutes, and a skill cannot be changed on the hub
itself. Changes come in as issues and pull requests. Curators' agents can draft
either; the issue forms are written so an agent can fill them in.

## Report a problem or suggest an improvement

Open an issue with one of the forms:

- **Skill correction**: a skill did the wrong thing, or its text is wrong or out
  of date. Say what happened and what you expected, and name the model, gene or
  input involved if there was one.
- **New skill proposal**: a task the skills do not cover. Say when it should
  trigger, what it should do, and which tool or data source it drives.
- **Documentation**: a reference document is wrong or missing something. Name the
  document and where it lives (see "Where the documentation lives").

From a GO AI Hub session, ask Claude to file it: it has the context and `gh` is
signed in as you. By hand: `gh issue create -R geneontology/go-skills`.

## Propose a change: a pull request from a fork

For wording, guideline text, references, a fix, or a new skill.

### On GitHub, in the browser

1. Open the file, for example `skills/gocam-best-practice/SKILL.md`.
2. Click the pencil ("Edit this file"). Without write access GitHub forks the
   repository for you and creates a branch in the fork.
3. Make the change, "Commit changes...", "Propose changes", then open the pull
   request. Write one sentence on what changed and why.

### From a GO AI Hub session

Work in a fork cloned to its own directory, not in `~/.claude/skills` (those are
read-only links) and not in a copy of a skill in your home (it would reach nobody
else). You can type these commands or ask Claude to do them; `gh` is signed in as
you on the hub.

```bash
gh repo fork geneontology/go-skills --clone=false                 # once: creates github.com/<you>/go-skills
gh repo clone "$(gh api user -q .login)/go-skills" ~/go-skills-fork   # gh adds the upstream remote
cd ~/go-skills-fork
git switch -c my-change
# edit skills/<name>/SKILL.md (or files under references/ or scripts/)
git add -A && git commit -m "noctua: say which token the store step needs"
git push -u origin my-change
gh pr create --fill                                               # targets geneontology/go-skills
```

To try the change before proposing it, give the clone a project skills directory
and start a Claude session inside it: `cd ~/go-skills-fork && mkdir -p .claude &&
ln -sfn ../skills .claude/skills && claude` (`.claude/` is gitignored here). A
session started in a directory loads that directory's `.claude/skills` as project
skills alongside your personal ones; ask Claude which copy of the skill it is
reading (`CLAUDE_SKILL_DIR`) to be sure the fork's version answered. Later, bring
the fork up to date with `git pull upstream main`.

### What happens next

CI runs the skill validator and the tests; a go-skills admin (see `CODEOWNERS`)
reviews and merges. A merge is live for curators within minutes, so half-finished
work stays a draft pull request.

## A new skill

Start with a **New skill proposal** issue so the name and scope are agreed before
the work. Then copy the layout of an existing skill, add a row to the table in
`README.md`, run the tests (`README.md`, "Tests"), and open the pull request from
a fork as above. A skill you wrote for yourself on the hub (a plain directory in
`~/.claude/skills`) is the usual starting point: copy it into the fork under
`skills/<name>/`.

## What a change needs

- `SKILL.md` under 500 lines; detail goes into `references/`.
- Frontmatter: `name` equal to the directory name, a `description` that says when
  to use the skill, `license`, and `metadata` with `version` and `source`. Only
  the fields in the [Agent Skills specification](https://agentskills.io/specification)
  plus `argument-hint` (see `CLAUDE.md`).
- The skill works from a fresh home directory with no credentials on disk. Any
  token it needs is obtained by following the skill's own steps.
- Scripts referenced as `${CLAUDE_SKILL_DIR}/scripts/...`, and they must not
  write into the skill directory: on the hub it is read-only.
- Half-finished work stays in a draft pull request.

## Where the documentation lives

- GO-CAM annotation guidance that the skills carry: `skills/gocam-best-practice/`
  (its `references/` and `GO-CAM_annotation_guidelines_README.md`) in this
  repository. Corrections are pull requests here.
- The GO-CAM annotation guidelines themselves: the Google Doc linked from
  `skills/gocam-best-practice/SKILL.md`; corrections go to its editors (GO
  Central), not here.
- Ontology editing skills: [geneontology/go-ontology](https://github.com/geneontology/go-ontology),
  under `.claude/skills/`; issues and pull requests go there.
- The hub itself (login, sessions, how skills reach homes):
  [geneontology/go-jupyter](https://github.com/geneontology/go-jupyter).
