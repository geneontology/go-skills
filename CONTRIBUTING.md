# Contributing to go-skills

Skills in this repository reach GO AI Hub curators within minutes of a merge to
`main`, so the bar for a change is "works from a fresh home directory and does
what its description says". Two ways to make a change, then what a change needs.

## Way 1: on GitHub, in the browser

For wording, guideline text, references, or a small fix.

1. Open the file on GitHub, for example `skills/gocam-best-practice/SKILL.md`.
2. Click the pencil ("Edit this file"). GitHub creates a branch in your fork or in
   this repository, depending on your access.
3. Make the change, then "Commit changes..." and "Propose changes". Write one
   sentence on what changed and why.
4. Open the pull request. CI runs the skill validator and tests; a go-skills
   admin (see `CODEOWNERS`) reviews and merges.

## Way 2: from a GO AI Hub session

For anything you want to try before proposing it. Your home has a git checkout
of this repository at `~/go-skills`, and Claude's skills (`~/.claude/skills/*`)
are links into it, so an edit there is what Claude runs next time the skill is
invoked. You can type these commands yourself or ask Claude to do them.

```bash
cd ~/go-skills
git switch -c my-change            # any branch name; this pauses automatic updates
# edit skills/<name>/SKILL.md (or files under references/ or scripts/)
# ... try the skill in your Claude session ...
git add -A
git commit -m "noctua: say which token the store step needs"
gh auth login                       # once per session, if git push asks for credentials
git push -u origin my-change
gh pr create --fill
```

While your checkout is on a branch or has uncommitted changes, the hub's
automatic update leaves it alone. When your pull request is merged (or you
abandon the change), return to the automatic track with:

```bash
cd ~/go-skills && git switch main && git pull
```

## What a change needs

- `SKILL.md` under 500 lines; detail goes into `references/`.
- Frontmatter: `name` equal to the directory name, a `description` that says when
  to use the skill, `license`, and `metadata` with `version` and `source`. Only
  the fields in the [Agent Skills specification](https://agentskills.io/specification)
  plus `argument-hint` (see `CLAUDE.md`).
- The skill works from a fresh home directory with no credentials on disk. Any
  token it needs is obtained by following the skill's own steps.
- Scripts referenced as `${CLAUDE_SKILL_DIR}/scripts/...`.
- For a new skill: copy the layout of an existing one, add a row to the table in
  `README.md`, and run the tests (`README.md`, "Tests").
- Half-finished work stays in a draft pull request. A merge is live for
  curators within minutes.

Questions or larger ideas: open an issue.
