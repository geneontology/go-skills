---
name: annotate-function
description: Use when a curator names one or more genes/gene products and wants a literature-driven review of their GO function annotations — evaluate existing annotations, exhaustively search the evidence, and PROPOSE (never create) an annotation set across MF/BP/CC with supporting references and evidence.
license: BSD-3-Clause
metadata:
  version: "0.2.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/annotate-function
  maintainer: geneontology
---

# annotate-function

Given one or more genes/gene products, evaluate their existing GO annotations
against the literature, do an exhaustive evidence search, and **propose** a
well-supported annotation set (MF / BP / CC) with the references and evidence to
back each one.

**This skill only proposes annotations. It does not create or edit any
annotation, and does not build GO-CAM models.** The deliverable is a report the
curator uses to decide what to enter. If the user wants to act on the proposal,
that is a separate step with the `noctua` skill.

## Rules that apply throughout

- **Cite every paper by PMID.** If a paper is not in PubMed, cite it by DOI.
  First author and year may be added for readability (e.g. `PMID:12345678
  (Smith 2019)`), which helps when many papers are discussed, but never replace
  the PMID/DOI with them.
- **State the source of every finding: full text or abstract.** Every verdict
  on an existing annotation and every proposed annotation says which one it
  rests on. Never infer findings beyond what an abstract states.
- **Never use retracted papers.** Check each paper's publication types
  (`pubmed-eutils` esummary/efetch): if it is a `Retracted Publication`, do not
  use it as support. If an *existing* annotation cites a retracted paper, flag
  that annotation for removal and say why.
- **Do not propose binding terms as MF.** Exclude `binding` (GO:0005488) and its
  descendants (protein binding, etc.) from proposed MF annotations. When a paper
  shows only an interaction, look for the functional activity it supports
  (e.g. molecular adaptor, enzyme regulator, transporter) using
  `gocam-best-practice` `references/`; if no such activity is supported, list
  the interaction under open questions instead. Existing binding annotations are
  still evaluated in Phase 1 like any other.
  If the review finds no MF worth proposing, say so and **offer** to look for
  binding annotations; do not search for or propose them unless the user asks.
- **Gene not found in the abstract ≠ wrong reference.** When the gene symbol
  does not appear in an abstract, the likely reason is that the finding is in
  the full text, not that the PMID is a typo. Never write that a PMID is
  "almost certainly a typo" or "the wrong number". Say instead: "The gene is not
  mentioned in the abstract; the full text was [not available / not checked],
  so this annotation could not be verified." Suggest a wrong reference only on
  positive evidence (e.g. the full text was read and the gene is absent, or the
  paper is about an unrelated organism or topic), and leave the call to the
  curator.

## Before starting — pin down the inputs (ask only if ambiguous)

- **Gene/product identity and species.** Resolve to the ID space Noctua uses.
  For model organisms with a MOD, that is the **MOD ID** (MGI, RGD, ZFIN,
  FlyBase, WormBase, SGD, PomBase, dictyBase, TAIR, Xenbase, ...), not UniProtKB:
  their annotations are filed under the MOD ID in AmiGO, so a query with the
  UniProt accession misses them. Use `uniprot-database` to get the canonical
  name, sequence and cross-references (including the MOD ID), then confirm the
  entity with `amigo search-bioentities` restricted by `--taxon`, and query
  annotations with the ID AmiGO returns. UniProtKB IDs are right for human and
  other non-MOD species.
- **Scope.** All three aspects, or limit to MF / BP / CC? Default: all three.
- **Depth.** Quick pass vs. exhaustive. Default: exhaustive (steps below).

## Getting the full text

Try for the full text of every paper you rely on when the set is small (roughly
ten papers or fewer); for larger sets, prioritize the papers that carry
proposed or questioned annotations, and say which ones were read in full.

- Find a PMC copy: `elink.fcgi?dbfrom=pubmed&db=pmc&id=<PMID>` (`pubmed-eutils`).
- Fetch it: Europe PMC
  `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`
  (open-access subset), or `efetch.fcgi?db=pmc&id=<PMCID>`.
- If neither returns the body text, the paper is **abstract only** for this
  review: record it as such.

## Finding orthologs

Use the **Alliance of Genome Resources** orthology API. It covers human and the
MOD species, and returns MOD IDs that can go straight to AmiGO:

```
curl -s "https://www.alliancegenome.org/api/gene/<GENE_ID>/orthologs?filter.stringency=stringent&limit=50"
```

- `<GENE_ID>` is the gene's HGNC ID for human (from the UniProt entry's
  cross-references) or its MOD ID otherwise, e.g. `HGNC:9719`, `MGI:1098808`.
- In each result, `geneToGeneOrthologyGenerated.objectGene` holds the ortholog
  (`primaryExternalId`, `geneSymbol.displayText`, `taxon.name`).
- Keep **close orthologs only**: `isBestScore.name` = `Yes` (for a stricter,
  reciprocal set, also require `isBestScoreReverse.name` = `Yes`). Results marked "No" are
  usually paralogs (e.g. yeast PEX9 for human PEX5); mention them only if
  relevant.
- For species the Alliance does not cover, fall back to the gene's OMA group:
  take its `xref_oma` ID from the UniProt entry, then search UniProt with
  `xref:oma-<ID>`. Do not use UniProt ID mapping for this; it returns only a
  group ID, and the PANTHER and OrthoDB groups it leads to are too broad
  (they include paralogs).

## Phase 1 — Evaluate existing annotations

- Pull existing experimental GO annotations for the gene(s) with `amigo` — MF, BP, and CC
  unless the scope was limited
- Separately check if IBA annotations exist for this gene
- For each annotation, record the **GO term, evidence code, and reference**.
- Look up every cited paper (`pubmed-eutils`), check it is not retracted, get
  the full text where available (see above), and confirm the annotation is
  actually supported — correct term, correct aspect, appropriate evidence code.
- Flag annotations that are **unsupported, over- or under-specified, or
  mis-aspected**, and suggest a concrete edit (corrected term + evidence).
- **Also pull existing annotations for close orthologs.** Get them from the
  Alliance of Genome Resources orthology API (see "Finding orthologs" below)
  and retrieve their MF/BP/CC annotations with `amigo`, using the IDs the
  Alliance returns. Note where the ortholog set is annotated to
  functions the queried gene is not — these are candidate gaps to test against
  the literature in Phase 2 — and flag functions supported only by transfer
  (e.g. ISS/IBA) vs. direct experiment.

## Phase 2 — Exhaustive literature review

- Search PubMed (`pubmed-eutils`) for any other evidence describing the gene's
  function, beyond what is already cited. Exclude retracted papers
  (add `NOT "retracted publication"[pt]` to the query, and check pubtypes of
  any paper found by other routes).
- For each reference, state whether it **supports an existing MF/BP/CC or adds a
  new/different one**.
- Prefer the **full text**. Extract the specific experiment and result that
  grounds each proposed annotation, not just the authors' claim.
- **Explicitly list every paper for which only the abstract was available**, and
  do NOT infer findings beyond what the abstract states. Curation quality
  depends on this.
- Use `gocam-best-practice` `references/` to shape the proposed annotations correctly (aspect
  boundaries, causal relations, appropriate GO terms) and the OLS MCP to pick
  and verify exact GO IDs.

## Phase 3 — Phylogenetic / orthology context

- Check whether the gene(s) or **close orthologs** are the subject of
  phylogenetic analyses. Cite those papers and summarize the key findings
  (family, conserved function, functional divergence).
- Note relevant orthology (from the Alliance, see "Finding orthologs"), the
  gene's PANTHER family and subfamily (from the UniProt entry's
  cross-references) for family-level context, and any existing
  phylogenetic (IBA / PAINT) annotations seen in Phase 1 — these say whether a
  function is inferred by descent vs. directly demonstrated.

## Deliverable — a written report

**Always** save the full report to a text file in the user's home directory —
this is required, not optional. Name the file after the gene(s), plus any other
information that makes it easy to find later (species, aspect if scoped, date).
For example: `annotation-review_mouse-Pex5_MF_2026-08-05.txt`, or for a small
set `annotation-review_Pex5-Pex7_2026-08-05.txt`. Tell the user the file path.

Structure:

1. **Current annotations** — a verdict per annotation (confirmed / edit /
   remove) with the reason, the reference (PMID/DOI), and whether the verdict
   rests on full text or abstract.
2. **Proposed annotations** — MF / BP / CC, each with GO ID, supporting
   reference(s) (PMID/DOI), suggested evidence code, and whether the support
   came from full text or abstract only. No binding MFs.
3. **Phylogenetic context** — cited and summarized.
4. **Open questions / abstract-only gaps** — where the evidence is thin,
   including interactions with no functional MF and references that could not
   be verified.
5. **Papers excluded** — retracted papers found, and why each was set aside.

### CSV when a paper was fully annotated

When the request was to annotate a whole paper (every annotatable finding in
one publication), **also** write the proposed annotations to a CSV next to the
report, same base name with `.csv`
(e.g. `annotation-review_PMID12345678_2026-08-05.csv`). One row per proposed
annotation, with these columns:

```
gene_id,gene_symbol,taxon,aspect,qualifier,go_id,go_label,evidence_code,reference,with_from,extension,source,figure_or_section,notes
```

The file is meant to be read by a curator as well as parsed, so **every ID
carries its label**: where the columns already pair them (`gene_id` +
`gene_symbol`, `go_id` + `go_label`) fill both; elsewhere write `ID (label)` in
the one cell.

- `gene_id`: in Noctua's ID space (MOD ID or UniProtKB), e.g. `MGI:1098808`;
  `gene_symbol`: e.g. `Pex5`.
- `taxon`: e.g. `NCBITaxon:10090 (Mus musculus)`.
- `aspect`: `F` / `P` / `C`; `qualifier`: e.g. `enables`, `involved_in`,
  `located_in`, `NOT|enables`.
- `go_id` / `go_label`: e.g. `GO:0016560` / `protein import into peroxisome matrix, docking`.
- `evidence_code`: e.g. `IMP (inferred from mutant phenotype)`.
- `reference`: e.g. `PMID:12345678 (Smith 2019)`, or `DOI:... (Smith 2019)`.
- `with_from`: each ID with its label, e.g. `UniProtKB:P50542 (PEX5_HUMAN)`;
  separate several with `|`.
- `extension`: relation and ID with label, e.g.
  `occurs_in(CL:0000182 (hepatocyte))`; separate several with `,`.
- `source`: `full text` or `abstract`; `figure_or_section`: where in the paper
  the result is shown, e.g. `Fig. 3B`.
- Quote any cell that contains a comma.

Tell the user both file paths.

Close by reminding the user this is a proposal; entering or modelling the
annotations is a separate, curator-driven step.
