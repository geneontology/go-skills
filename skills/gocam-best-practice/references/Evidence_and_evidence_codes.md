# Evidence and evidence codes

## Evidence Codes (match what the paper shows)

Pick the evidence code for what was actually demonstrated, not for convenience. The code
must match the experiment in the cited figure, not the paper's overall conclusion:
- **IDA (ECO:0000314):** directly demonstrated (assay, imaging, direct binding/catalysis):
  a direct assay of the activity (purified protein, reconstitution, enzymology).
  Structure, clinical-mutation, trafficking and targeting papers rarely support an
  enzymatic or transport IDA.
- **IMP (ECO:0000315):** shown via a mutant / knockdown / knockout phenotype: loss of
  function showing the gene product is required (siRNA, knockout, degron, rescue). A
  knockdown that removes a reaction product is IMP, not IDA on the reaction.
- **IGI (ECO:0000316):** genetic interaction; the other gene goes in `with/from`.
- **IPI (ECO:0000353):** physical interaction; the interacting partner goes in `with/from`.
- **IEP (ECO:0000270):** expression pattern; for biological processes only.
- **IC (ECO:0000305):** curator inference — legitimate, but use deliberately. The term the
  inference rests on goes in `with/from`; it must not be the term being supported, nor
  the activity's own function.
- **ISS ortholog-transfer recipe** (e.g. building a human model from mouse experiments):
  use the target species' identifiers (human -> UniProtKB) and taxon; put every fact on
  ISS evidence:
  - **ISS = ECO:0000250**, reference **GO_REF:0000024** (manual transfer by curator sequence
    similarity), with `with/from` = the source ortholog's **MOD** accession (e.g. S. pombe: `Pombase:...`).
  - For a causal edge between two proteins, `with/from` may list both source orthologs.
  - ISS annotations can only be transferred from a sequence that has experimental evidence, not from a sequence that only has sequence similarity, phylogenetic or IEA evidence.
  - The `with/from` id must not be the gene being annotated.
- **IBA** annotations can be used, but these need to be fetched from AmiGO; they cannot be created
- **IEA** annotations: annotations from InterPro2GO, and other sources, may be used, but these must be fetched from AmiGO. IEA annotations should only be used when no other data can be found.
- **NAS (ECO:0000303) and TAS (ECO:0000304)** are allowed but weak; prefer the primary
  paper when one exists.
- **Important note: be honest about the presence and quality of the evidence. If a statement lacks support, warn the user, so they can help find evidence.**

## The with/from field

- Required for IC, IPI, IGI, ISS/ISO/ISA and IBA.
- Left empty for IDA, IEP, TAS and NAS. An IDA with a `with/from` value is usually a
  colocalisation inference mis-coded as a direct assay.
- Each value must be right for the fact it sits on: the IPI partner is the partner on
  that edge; one ortholog does not serve two different genes.

## References

- Reference ids are a prefix, a colon, and digits only, with no space and no other characters:
  - **PubMed:** `PMID:` followed by the PubMed id exactly as PubMed gives it, digits
    with no leading zeros (e.g. `PMID:12345678`, `PMID:9606`). Pattern: `PMID:[1-9][0-9]*`.
  - **GO reference:** `GO_REF:` followed by exactly 7 digits, zero-padded
    (e.g. `GO_REF:0000024`, not `GO_REF:24`). Pattern: `GO_REF:[0-9]{7}`.
- Use the PMID when one exists, not a DOI.
- One reference per evidence line; the same evidence line twice on one fact is a duplicate.
- GO_REF:0000024 goes only with ISS-family codes; IBA goes only with GO_REF:0000033.
- Cite the paper that shows the fact. A sentence such as "X does Y (Author et al.)" in
  paper P is a citation, not P's evidence: cite the original paper instead.
