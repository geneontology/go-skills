# go-skills

Agent skills for Gene Ontology curation, in the open
[Agent Skills](https://agentskills.io) `SKILL.md` format. Each skill can be installed by itself, with no repository checkout. Some are **front
doors** that set up the toolkit they depend on the first time they are used; others
are self-contained GO curation knowledge or thin wrappers over public APIs.

| Skill | Purpose | Toolkit it drives |
|---|---|---|
| [`gene-review`](skills/gene-review/) | Review a gene's GO annotations and write a validated review file | [ai4curation/ai-gene-review](https://github.com/ai4curation/ai-gene-review) |
| [`noctua`](skills/noctua/) | Read and edit GO-CAM models on the Noctua dev server through barista | [noctua-py](https://github.com/geneontology/noctua-py) `barista` CLI |
| [`save-to-drop-box`](skills/save-to-drop-box/) | Save a finished model to the drop box as a YAML + Turtle pair under its dev id | [go-cam-drop-box](https://github.com/geneontology/go-cam-drop-box) |
| [`annotate-function`](skills/annotate-function/) | Literature-grounded function annotation for named gene products | (self-contained) |
| [`amigo`](skills/amigo/) | Look up existing annotations and bioentities in AmiGO/GOlr | AmiGO API |
| [`pubmed-eutils`](skills/pubmed-eutils/) | PubMed search and metadata via NCBI E-utilities | NCBI E-utilities |
| [`uniprot-database`](skills/uniprot-database/) | UniProt REST: protein search, FASTA, ID mapping | UniProt REST API |
| [`gocam-best-practice`](skills/gocam-best-practice/) | GO-CAM annotation guidelines and reference material | (self-contained) |

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

## Tests

CI runs on pull requests and pushes to `main`. It validates every skill with the
[Agent Skills reference parser and validator](https://agentskills.io/specification#validation),
allowing only the repository's `argument-hint` extension in addition to the spec
fields. It also enforces `metadata.version`, `metadata.source`, and the under-500-line
limit, checks shell syntax and skill discovery, and runs the bootstrap regression
tests in temporary homes with real Git repositories and stubbed `uv`/`just`.

CI uses uv to manage Python and the pinned test dependencies. Run the same checks
locally with:

```bash
uv run --python 3.12 --with-requirements tests/requirements.txt python -m unittest discover -s tests -v
```

The validator fixtures check that malformed YAML, duplicate or unknown fields,
invalid names, and other invalid skill metadata fail validation. The specification
does not restrict the Markdown body; these checks validate skill structure and
frontmatter, not the quality of the instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): edit on GitHub in the browser, or from a
GO AI Hub session in your `~/go-skills` checkout, then open a pull request. Keep a
`SKILL.md` under 500 lines; move detail into `references/`. Skills should work
from a fresh home directory with no credentials.
