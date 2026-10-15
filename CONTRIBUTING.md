# Contributing to go-skills

This repository holds the canonical GO curation skills: the versions every
curator gets. On the GO AI Hub, the skills in your `~/.claude/skills` are
read-only links to this repository, and they update within minutes of a change
being merged here. So a skill is changed here, on GitHub, not on the hub.

You can do three things, and your Claude session on the hub can draft any of
them for you.

## 1. Report a problem or suggest an improvement

Open an issue. There are three forms:

- **Skill correction**: a skill did the wrong thing, or its text is wrong or out
  of date. Say what happened and what you expected; name the model, gene or
  paper involved if there was one.
- **New skill proposal**: a task the skills do not cover. Say when it should
  start, what it should do, and which tool or data source it uses.
- **Documentation**: a reference document is wrong or missing something. Name
  the document and where it lives (see "Where the documentation lives" below).

On the hub, ask Claude to file it; it knows the context and is signed in to
GitHub as you. By hand: `gh issue create -R geneontology/go-skills`.

What happens next: a go-skills maintainer reads the issue, asks questions if
needed, and either makes the change or asks you to propose it as a pull request
(next section).

## 2. Propose a change: a pull request from a fork

A pull request is a proposed change that a maintainer reviews before it is
merged. Most curators cannot write to this repository directly, so the change
is made in a fork (your own copy of the repository on GitHub) and proposed from
there.

### In the browser, for small text changes

1. Open the file on GitHub, for example `skills/gocam-best-practice/SKILL.md`.
2. Click the pencil icon ("Edit this file"). GitHub makes the fork for you.
3. Make the change, then "Commit changes..." and "Propose changes". Write one
   sentence on what you changed and why.
4. Open the pull request.

### From a GO AI Hub session, for anything larger

Work in your fork, cloned to its own directory. Do not edit the files under
`~/.claude/skills` (they are read-only links), and do not edit a copy of a
skill elsewhere in your home: that changes only your own sessions and reaches
nobody else.

You can type these commands or ask Claude to run them. `gh` is already signed
in as you on the hub.

```bash
# once: make your fork on GitHub and clone it
gh repo fork geneontology/go-skills --clone=false
gh repo clone "$(gh api user -q .login)/go-skills" ~/go-skills-fork

# each change
cd ~/go-skills-fork
git switch -c my-change                        # a branch for this change
# ... edit skills/<name>/SKILL.md, or files under references/ or scripts/ ...
git add -A && git commit -m "noctua: say which token the store step needs"
git push -u origin my-change
gh pr create --fill                            # opens the pull request against geneontology/go-skills
```

`gh repo clone` of a fork also remembers the original repository under the
name `upstream`. Before starting your next change, bring your fork up to date:
`cd ~/go-skills-fork && git switch main && git pull upstream main`.

**Trying the change first.** Claude loads skills from a `.claude/skills`
directory inside the directory it was started in. Give your fork one, pointing
at its skills, and start Claude there:

```bash
cd ~/go-skills-fork && mkdir -p .claude && ln -sfn ../skills .claude/skills && claude
```

In that session your fork's version of a skill is loaded alongside the normal
one. To be sure which one answered, ask Claude: "Which copy of the skill are
you reading?" The `.claude/` directory is ignored by git in this repository, so
it will not end up in your pull request.

### What happens next

Automated checks run on the pull request: the skill validator and the tests. A
go-skills maintainer (see `CODEOWNERS`) reviews and merges. A merge is live for
every curator within minutes, so unfinished work stays a draft pull request.

## 3. A new skill

Start with a **New skill proposal** issue, so the name and scope are agreed
before the work. A skill you wrote for yourself on the hub (a plain directory
in your `~/.claude/skills`) is a good starting point: copy it into your fork
under `skills/<name>/`. Then follow the layout of an existing skill, add a row
to the table in `README.md`, run the tests (`README.md`, "Tests"), and open the
pull request as above.

## What a change needs

- `SKILL.md` under 500 lines; detail goes into `references/`.
- The frontmatter (the block between `---` lines at the top of `SKILL.md`):
  `name` equal to the directory name, a `description` that says when to use the
  skill, `license`, and `metadata` with `version` and `source`. Only the fields
  in the [Agent Skills specification](https://agentskills.io/specification)
  plus `argument-hint` (see `CLAUDE.md`).
- The skill works from a fresh home directory with no credentials on disk. Any
  token it needs is obtained by following the skill's own steps.
- Scripts are referenced as `${CLAUDE_SKILL_DIR}/scripts/...`, and they must
  not write into the skill directory: on the hub it is read-only.
- Unfinished work stays a draft pull request.

## Where the documentation lives

- GO-CAM annotation guidance carried by the skills: `skills/gocam-best-practice/`
  in this repository (its `references/` and
  `GO-CAM_annotation_guidelines_README.md`). Corrections are pull requests here.
- The GO-CAM annotation guidelines themselves: the Google Doc linked from
  `skills/gocam-best-practice/SKILL.md`. Corrections go to its editors (GO
  Central), not here.
- Ontology editing skills: [geneontology/go-ontology](https://github.com/geneontology/go-ontology),
  under `.claude/skills/`; issues and pull requests go there.
- The hub itself (login, sessions, files, how skills arrive):
  [geneontology/go-jupyter](https://github.com/geneontology/go-jupyter).
