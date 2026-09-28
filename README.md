# go-skills

Agent skills for Gene Ontology curation, in the open
[Agent Skills](https://agentskills.io) `SKILL.md` format. Each skill is a **front
door**: it can be installed by itself, with no repository checkout, and knows how to
set up the toolkit it depends on the first time it is used.

| Skill | Purpose | Toolkit it drives |
|---|---|---|
| [`gene-review`](skills/gene-review/) | Review a gene's GO annotations and write a validated review file | [ai4curation/ai-gene-review](https://github.com/ai4curation/ai-gene-review) |

## Install

Claude Code, for the current user, from any directory:

```bash
npx skills add geneontology/go-skills --skill gene-review -g -a claude-code
```

Then, in a session: `/gene-review DANRE fezf2`. Update later with `npx skills update`.

Other agents that read `SKILL.md` (Cursor, Codex, Gemini CLI, OpenCode, ...): replace
`-a claude-code` with the agent's identifier, or drop it to be asked.

On the GO AI hub the skills in this repo are delivered automatically; nothing to install.

## Layout

```
skills/
  <skill-name>/
    SKILL.md          # required: frontmatter + instructions
    scripts/          # optional: helpers the skill runs
    references/       # optional: docs the skill reads on demand
```

Skill names are lowercase with hyphens and must match their directory name. See the
[specification](https://agentskills.io/specification) for the frontmatter fields.

## Contributing

Open an issue or PR here. Keep a `SKILL.md` under 500 lines; move detail into
`references/`. Skills should work from a fresh home directory with no credentials.
