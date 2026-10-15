# GO-CAM review checks

The checks a second curator runs. The script (`qc.md`) covers the mechanical
part, marked **[flag]** with the tag it uses; everything else is read. The
rules the model is judged against are in the `gocam-best-practice` skill
(`references/Relation_selection.md`, `Evidence_and_evidence_codes.md`, and the
activity-type files); read the ones that match the model's activities.

## Severity

| Severity | Meaning |
|---|---|
| critical | The model says something false, or cannot stand in production as is: wrong gene, wrong species of data under an experimental code, a claim not in the paper, a missing enabler, an obsolete or do-not-annotate term. |
| major | A fact is unsupported or mis-coded: ISS without an experimental source, a direct relation with no known mechanism, a reference that does not show the fact, a fact with no evidence. |
| moderate | Correct in substance but weakly supported or imprecise: a self-referential IC, a too-general term, an unverifiable reference, missing location or process. |
| minor | Hygiene and style: malformed reference, duplicate evidence line, leftover comment. |
| note | Not a defect: a remark, a question for the curator, or something that is fine and worth saying. |

Script severities are inputs, not verdicts: an `error` is usually a critical
or major candidate, a `warning` a major or moderate candidate; read each in
context before it becomes a finding.

## A. Hygiene

- Title says what the model is about (process, key players, context). Not a
  placeholder, not a PMID. Length is not raised. **[flag]** `hygiene`
- State is the curator's call; say if it looks inconsistent (production with
  open reviewer comments). Taxon set. **[flag]** `hygiene`
- Model comments addressed to a reviewer or describing a past edit should be
  resolved before production; comments documenting a decision are fine. Read
  each. **[flag]** `hygiene: model comment to read`
- Orphans and leftovers: individuals in no fact, evidence attached to nothing,
  the same edge reified twice. **[flag]** `structure` (these are the
  noctua-models production QC checks; an error there blocks promotion)
- Every activity unit is complete: a molecular function with an enabler (the
  root MF with an enabler means "function unknown", which is allowed), a
  process by `part of`, a location by `occurs in` where known, and evidence on
  every fact. **[flag]** `activity`, `evidence`. Enumerate activities both
  ways: by `enabled by` and by MF typing; an MF node with no enabler is only
  visible the second way, and is critical.
- Single-activity model: GO expects a multi-activity flow. **[flag]** `structure`

## B. Evidence codes and the with/from field

- The code matches the experiment in the cited figure: IDA for a direct assay
  of the activity (purified protein, reconstitution, enzymology); IMP for
  loss-of-function showing the gene product is required (siRNA, knockout,
  degron, rescue), not an IDA on the reaction; IGI with the other gene in
  `with`; IPI with the partner; IEP for expression patterns, on processes
  only; IC with the grounding term in `with`. Structure, clinical-mutation,
  trafficking and targeting papers rarely support an enzymatic or transport
  IDA. **[flag]** `with: IEP`
- `with` present where the code needs it (IC, IPI, IGI, ISS/ISO/ISA, IBA) and
  absent where it must not be (IDA, IEP, TAS, NAS). An IDA with a `with` value
  is usually a colocalisation inference mis-coded as a direct assay.
  **[flag]** `with`
- Circular `with`: an IC citing the term it supports or the activity's own
  function; an ISS citing the gene being annotated. **[flag]** `with: circular`
- Copy-paste `with`: one value repeated on facts where it cannot be right (an
  IPI partner that is not the partner on that edge; one ortholog for two
  genes). Use the with/from inventory in `qc.md`.
- Recipe mismatch: GO_REF:0000024 only with ISS-family codes; IBA only with
  GO_REF:0000033. **[flag]** `with: recipe`
- Reference form: `PMID:n`, `GO_REF:nnnnnnn`; one reference per evidence line;
  a bare DOI when a PMID exists is a minor. **[flag]** `evidence`
- IEA and IBA in a GO-CAM are copied from an existing annotation, not created.
  NAS and TAS are allowed but weak; note when a primary paper exists.
- Attribution: a sentence like "X does Y (Author et al.)" in paper P is a
  citation, not P's evidence. If the model cites P for a fact P attributes to
  Q, the fix is to re-source to Q.

## C. ISS and orthology

For every ortholog in a `with` on ISS/ISO/ISA evidence:

1. The source gene has an experimental annotation (EXP, IDA, IMP, IGI, IPI,
   IEP, or HTP codes) to the same or a more specific term (`amigo` skill). An
   ISS whose source is itself ISS, ISO, IBA or IEA has no source: major.
2. For a causal edge, the source data show the same relation between the
   orthologs.
3. The `with` id is the source ortholog in its own namespace (MGI:MGI:...,
   RGD:..., ZFIN:..., UniProtKB:...) and is the true ortholog (PANTHER or the
   Alliance when in doubt, especially in families with paralogs).
4. When the transfer carries the model, check the source annotation's own
   reference; it can be wrong too, and that is worth telling the curator.

## D. Species of the data and of the entities

- An experimental code on a gene product of the model's taxon needs an
  experiment on that species' gene product. Data on the mouse protein in a
  human model is ISS from the mouse gene, not IDA. A human protein in a
  heterologous system (HEK293, CHO, yeast, Xenopus oocytes) supports IDA on
  the human protein; say which it was. Only down-code the facts that rest
  solely on the ortholog: a mouse phenotype paper can still carry a correct
  IDA from a human-protein assay in the same paper.
- Read the methods for the species of cells, animals and constructs; abstracts
  often omit it. Abstract only: species unverified.
- Entities whose namespace implies another species than the model's taxon:
  host-pathogen models are the exception. **[flag]** `species`
- Model-organism gene products use the MOD accession (MGI, RGD, ZFIN, FB,
  SGD, WB, PomBase, ...), not UniProtKB; human is the exception. MGI ids are
  written `MGI:MGI:n`. Applies to `with` too.

## E. References reused out of context (every PMID, every round)

The most common real problem, invisible to the script. Use "References, and
the facts each supports" in `qc.md`; for each PMID, fact by fact:

- Does this paper show this fact: this gene product (not a paralog or the
  family), this activity, this relation, this location or cell type?
- Is the code right for what the paper shows for this fact? A paper with IDA
  for the binding does not give IDA for the downstream process.
- Was the reference copied from another model or the parent onto edges it
  does not cover? A comment "evidence copied from ..." is the usual trace.
- A review under an experimental code: TAS or NAS at most; better, the
  primary paper.

Raise this even when a similar item was declined earlier: new edges reuse
references. Without the full text, "not verified (abstract only)".

## F. Causal relations and molecule handling

`Relation_selection.md` is the rule; the short version:

- directly positively/negatively regulates: an immediately downstream
  activity, no intervening activity, mechanism known. Without a known
  mechanism: causally upstream of, positive/negative effect. indirectly
  regulates: through a larger reusable process deliberately not drawn,
  mechanism still known. provides input for: the upstream output is the
  downstream input (only when the molecule itself is not modelled; when it is,
  `has output` and `has input` carry it). removes input for: both act on the
  same target site with opposite effect. constitutively upstream of: required,
  not regulating.
- Sign matches the data, direction is upstream to downstream, and the edge's
  reference shows the link between these two activities, not merely between
  the two proteins somewhere. A ligand to its receptor is a causal relation,
  not `has input`.
- Look at the whole chain: missing obvious steps, a regulated activity with no
  path to the process, a causal edge into a process when an activity in that
  process is known.
- Inputs are the direct targets. Do not call a `has input` redundant because a
  causal edge exists; call it missing when a substrate, regulated gene,
  receptor ligand or activated effector is absent. When `has input` is a gene
  product there is no `has output`; the relation is `directly regulates`.
- Molecule reuse: the productive handoff is good modelling. A molecule that is
  the `has output` of one activity and the `has input`, or the small-molecule
  activator or inhibitor, of a downstream activity should be the same
  individual; that shared node is what represents the handoff. Only flag reuse
  that forces one individual into contradictory roles or merges two separate
  pools. Each activity has its own `part of` process individual; a process
  node shared by several activities is a defect.
- Chemicals: reactants and products are the ChEBI ids of the enzyme's Rhea
  reaction (UniProt `cc_catalytic_activity`); one compound keeps one ChEBI id
  across a handoff; only primary substrate and product belong (cofactors,
  donors, byproducts such as UDP, ATP, ADP, H2O, H+ do not). An obligate
  coupled reaction (an exchange or antiport) is one activity with its full
  participant set and one Rhea id, not two half-transfers.
- A metabolite `located in` a compartment needs direct evidence for that
  metabolite in that place (a transporter or marker paper is not), and the
  location must be compatible with the `occurs in` of the activities that
  produce or consume it.

## G. Term choice, specificity, locations, enablers

- Labels, obsolescence, `gocheck_do_not_annotate` and obsoletion candidates
  for every class, and taxon constraints for the species. **[flag]** `terms`
- Specificity: as specific as the data support, no more. "protein binding" or
  a generic binding term where the paper shows the activity; a parent like
  "signal transduction" where the pathway is known; or a child the paper does
  not reach.
- The MF is an activity of the enabler, not a role in a process; regulators as
  regulator activities (enzyme regulator, adaptor) per the guidelines.
- Locations: `occurs in` the GO component where the activity happens (a
  receptor at the plasma membrane, not "cell"). A complex term is not a
  location. Nest the component `part of` a CL cell type or UBERON anatomy when
  the paper's system is known, and check it matches the paper (cell line,
  primary cell, tissue).
- Enablers: the gene product (UniProtKB, isoform when the paper is isoform
  specific), a ComplexPortal complex when subunits are known, the GO complex
  term when they are not, per `How_to_annotate_complexes_in_GO-CAM.md`.
- Process context: each MF `part of` the right process; nested processes make
  sense. Cytokine-signalling models: GO:0019221 in every activity unit;
  sibling cytokine-production terms collapsed to GO:0001819.

## H. Lineage

- Earlier rounds: read `checklist.md` and `checklist-done.md` under
  `~/reviews/*-<id>/`. Done items: verify they are fixed. Declined with a
  reason: do not re-raise (except E). Keep ids stable.
- Parent model ("Derived from" in the header): fetch, `--facts-only` both,
  diff. Fixes made to the parent after the copy are often missing from the
  child, and edits in the child may need carrying back.
- Dev versus production: if the model is in both and they differ, say how.

## I. Literature honesty

- For every PMID, the evidence notes record what it supports, at what level
  (biochemical, cellular loss-of-function, genetic, interaction, imaging,
  clinical), the species and protein used, and "full text" or "abstract only".
- Figure-level detail (cell type, species, construct, assay) never comes from
  an abstract. If a finding depends on it and the paper was not read, the
  finding is unverified and the curator is asked for the PDF.
- Claims in model comments ("Fig. 3B shows ...") that were not checked are
  reported as unchecked, not endorsed.
- A wrong earlier finding is withdrawn by id at the top of the next report.
