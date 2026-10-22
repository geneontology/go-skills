---
name: paint-family-review
description: Review a PANTHER family for PAINT/IBA phylogenetic annotation — find MF/BP/CC gaps on nodes containing human or other model-organism genes, replace binding-only MFs with functional ones, QC existing IBAs and their seeds, and propose node annotations backed by experimental evidence on in-tree species. Use when a curator names a PANTHER family (PTHRxxxxx), asks for a PAINT review, a node annotation proposal, IBA QC, or a functional replacement for a "binding-only" MF in a PAINT context. Read-only; it proposes, the curator annotates in PAINT.
license: BSD-3-Clause
argument-hint: "<PTHRxxxxx> [focus: MF|BP|CC|QC]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/paint-family-review
---

# PAINT family review

Analyse one PANTHER family and **propose** node annotations (and removals) for
the curator to make in PAINT. This skill never writes annotations anywhere.

## The curator's own rules come first

The rules below are distilled from many PAINT review sessions, but every curator
settles their own conventions. If the curator keeps a notes or memory file of
their PAINT decisions (ask once if unsure), read it before starting; **where it
is more specific than this skill, it wins.** When a new rule is settled in a
session, offer to add it to that file.

Related skills: `pubmed-eutils` (literature), `uniprot-database`, `amigo`; the
OLS MCP for term lookup (never guess a GO ID; check for obsolete terms).

## Workflow

1. **Check the release.** PAINT works on a specific PANTHER release (19 at the
   time of writing; the treeinfo response carries `"version"`). UniProt's
   PANTHER cross-references may come from a newer release: family IDs can be off
   by one, and families can split, merge or shift members (C2H2 ZNFs notably).
   State which release every fact comes from, and verify that the family the
   curator quotes contains the genes they expect.
2. **Fetch data** into a working directory in the home, e.g. `~/paint-PTHRxxxxx/`:
   ```bash
   F=PTHRxxxxx; mkdir -p ~/paint-$F && cd ~/paint-$F
   curl -s "https://www.pantherdb.org/services/oai/pantherdb/treeinfo?family=$F" > treefull.json
   python3 "${CLAUDE_SKILL_DIR}/scripts/clade.py" treefull.json "$(python3 -c "import json;print(json.load(open('treefull.json'))['search']['tree_topology']['annotation_node']['persistent_id'])")" > leaves.tsv
   cut -f1 leaves.tsv | grep -v '^-$' > acc_all.txt
   ```
   - Existing annotations: QuickGO TSV,
     `https://www.ebi.ac.uk/QuickGO/services/annotation/downloadSearch?geneProductId=<comma-separated accs>`
     with header `Accept: text/tsv`; batch the accessions (a few hundred per call)
     and concatenate into `goa_all.tsv`.
   - UniProt (reviewed status, organism, PMIDs, TM, Pfam):
     `https://rest.uniprot.org/uniprotkb/search?query=xref:panther-$F&format=tsv&fields=...`
     (note: this is UniProt's release of PANTHER, see step 1).
3. **Map the tree** with the scripts below: node outline, human-leaf paths,
   existing IBAs with their seeds, which leaves each candidate node adds.
4. **Collect experimental evidence** per clade: GOA EXP-class annotations plus the
   literature for well-studied members. For big families (hundreds of leaves),
   split the literature work by major clade across background agents, each
   writing a `findings.md`. Never infer a paper's content from its abstract; say
   when only the abstract was available. Map proteins in papers to tree leaves by
   sequence (`bestmatch.py`, `kmerhit.py`) when the identifier is ambiguous.
5. **Propose**, per node: GO term, node (PTN id, species, event type, leaf count),
   seeds (species, gene, PMID, evidence), rationale. Then a **leave blank** list,
   a **QC** list (existing IBAs or leaf annotations that look wrong, and EXP
   papers missing from GOA), and at most a few clearly secondary options.
6. **Record**: write the proposal and outcome to a session log in the home
   directory; build a PDF report only when the curator asks for one
   (`report_build.py`).

## Annotation rules

### Molecular function
- Functional MFs over bare `protein binding` or other binding terms. Adaptor,
  scaffold, inhibitor, regulator, sequestering, insertase and similar terms
  count as non-binding (under molecular function regulator or structural
  molecule activity, not GO:0005488).
- Choosing the term and qualifier:
  - performs the activity alone → `enables`
  - the activity belongs to a complex it is part of → `contributes_to`
  - only holds a complex together → scaffold activity GO:0140378, not the
    borrowed catalytic term
  - bridges two molecules so a reaction can happen → molecular adaptor activity
    GO:0060090
  - modulates a separate enzyme → a regulator MF (if only an outcome is shown,
    use BP)
  - if the catalytic subunit of the complex (protein or ribozyme RNA) is known,
    the other subunits do not get `contributes_to` on the catalytic term (GO
    complex guideline, case 1; ribosomal-protein precedent). Give them their own
    MF or leave MF blank.
- Decline a broad substrate-class transporter term when papers show only some
  members of the class are transported.
- Grouping MFs that add little over a broader term already at the root are low
  value; mention them, don't push them.

### Biological process
- No BP that just restates the MF as a one-step process (e.g. a protein
  isomerization term for an isomerase); require a real multi-step process.
- No "regulation of X" on a node whose ancestor already carries X; pick one level.
- An existing node BP that rests on a single species: prefer removing it to
  retyping or moving it, until more evidence exists.

### Cellular component
- Never propagate a bacterial-only CC (e.g. cytosol) to eukaryotes, especially
  across a horizontal-transfer node: proteins of bacterial origin are often
  mitochondrial or plastid in eukaryotes.
- Reject CC that rests on microsomal fractionation alone, or on a paper that
  asserts but does not show the location. Treat high-throughput proteomics
  locations with caution.
- Decline a CC that depends on a processing event (e.g. cleavage then secretion)
  shown in only one species.
- Check transmembrane segments across the clade before placing a membrane CC;
  soluble subfamilies exclude the node above them.
- The curator may already have done CC; check before proposing it.

### Evidence
- Seeds must be experimental annotations on species **present in the tree**
  (check; common lab species such as rabbit may be absent).
- Avoid With/From-dependent codes (IGI, IPI, IC, OPI) for new leaf annotations
  meant to seed an IBA; plain EXP-class codes (IDA, IMP, EXP...) are safer.
- List papers with experimental data not yet in GOA as "missing EXP" QC.

### Node placement
- **Never annotate a duplication node directly.** Duplication nodes can vanish
  or split between PANTHER releases, and a function may arise after the
  duplication. Use the speciation node just below, and block after loss of
  function.
- Before endorsing a node, list which leaves it actually adds; a node can bring
  in unexpected clades or kingdoms.
- Place a node annotation at the widest clade the evidence supports (e.g. to
  include early-branching metazoa).
- Root of a big family: a general MF with a matching CC is acceptable when
  experimental evidence is spread across several clades or kingdoms and there is
  no counter-evidence. Check for NOT annotations and non-catalytic (e.g.
  kinase-dead) clades first; loss in a lineage is possible but not assumed.
- No root MF when only one member has experimental support or the topology is
  doubtful: annotate a root BP only and flag the topology.
- When members have very different functions not confirmed in several
  organisms, do not annotate internal nodes; still write the per-node analysis
  down as reference material, clearly separated from what goes into PAINT.
- A single-species node CC or BP can be acceptable when coherent with sister
  clades; present such tiers separately from the well-supported ones.

### Style
- Large families: mention small term-choice differences, don't chase them.
- Keep options few and clearly secondary; unconfirmed options count as declined.
- Leaving MF or BP blank when evidence is absent is a valid outcome; say so.

## Scripts

In `${CLAUDE_SKILL_DIR}/scripts/`; Python 3, standard library unless noted. The
tree scripts read the PANTHER treeinfo JSON. Each prints to stdout; none writes
into the skill directory.

| Script | Usage | Output |
|---|---|---|
| `outline.py` | `outline.py tree.json MIN_LEAVES [PTN]` | indented node outline: PTN, event, species, SF, leaf count, model-organism genes; nodes below MIN_LEAVES collapsed |
| `tree.py` | `tree.py tree.json` | ancestor path of every human leaf, with leaf/organism counts and human members per node |
| `path.py` | `path.py tree.json ACC [ACC...]` | ancestor path of the given UniProt leaves |
| `clade.py` | `clade.py tree.json PTN` | every leaf under a node: accession, organism, symbol, definition, last three ancestors |
| `iba.py` | `iba.py goa_all.tsv` | existing IBAs (QuickGO TSV) grouped by node, aspect, qualifier and term, with genes and seeds |
| `bestmatch.py` | `bestmatch.py query.fa db.fa` | best global-alignment identity hits (needs Biopython: `uv run --with biopython`) |
| `kmerhit.py` | `kmerhit.py query.fa db.fa` | fast shared 5-mer hits, for big families |
| `report_build.py` | `report_build.py file.md` | `file.html` + A4 PDF beside it (`uv run --with markdown --with xhtml2pdf`) |
| `report_build_landscape.py` | `report_build_landscape.py file.md` | landscape variant for wide QC tables |
