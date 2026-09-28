# CLAUDE.md — go-skills

Agent skills (`SKILL.md`, https://agentskills.io) for GO curation. One directory per
skill under `skills/`. Skills here are front doors to toolkits that live in other
repositories; they must work from a fresh `$HOME` with no checkout and no credentials.

Rules:

- `name:` in the frontmatter must equal the directory name (lowercase, hyphens).
- Only spec frontmatter fields (`name`, `description`, `license`, `compatibility`,
  `metadata`, `allowed-tools`) plus Claude Code's `argument-hint`. Put version and
  source URL under `metadata`.
- Reference helpers as `${CLAUDE_SKILL_DIR}/scripts/...`; that variable is the skill
  directory itself.
- Keep `SKILL.md` under 500 lines. Detail goes in `references/`.
- Test a change with `npx skills add ./ --skill <name> -l` (discovery) and by running
  any script under a scratch `$HOME`-like location before opening a PR.
- The GO AI hub (geneontology/go-jupyter) mirrors skills to users on a timer; a merge
  here may be live for curators within minutes. Do not merge half-finished skills.
