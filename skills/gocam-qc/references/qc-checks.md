# GO-CAM QC: the checks

Each check has a **default severity**: critical (the model asserts something the evidence doesn't support, or it will fail validation), major (wrong or unsupported but local), minor (imprecise or untidy), optional (a choice for the curator). Adjust severity to the case, and say why.

The examples are from the QC rounds on gomodel:6aa323c700001432 (UTS2 → UTS2R → Gi/o → PI3K → PKCβ1 → L-type Ca²⁺ channel in cardiomyocytes, 2026-09-28 to 2026-10-06). That model was built from rat data (PMID:25678708) in a human model, with drug-defined complexes as enablers. It hit nearly every check below.

---

## A. Hygiene (mostly flagged by `gocam_dump.py`)

| Check | Default | Notes |
|---|---|---|
| Fact with no evidence | critical | Often evidence deleted and never re-added after an edit. Compare with the previous version if you have it. |
| Disconnected evidence individual | major | Production QC and drop-box CI reject it. |
| Same edge evidenced by two separate axioms | major | Production QC and drop-box CI reject it. |
| Individual in no fact | minor | Leftover from an edit. |
| Reference without prefix (`25678708`) | major | Won't resolve; use `PMID:25678708`. |
| Obsolete or merged term | critical | Check every class in the ONTOLOGY CLASSES line (OLS, or `runoak -i sqlite:obo:go info GO:...`). |
| Title over ~60 characters, or no `(Species)` | minor | House style, not a hard rule. |
| Model comment addressed to a reviewer | minor | Remove once answered, or replace with a short curation note. |

## B. Evidence codes and the `with` field

**How IC works** (curators have asked for this to be explained plainly): IC means "I infer X from annotation Y", and the `with` field names Y. Y must be a different, non-IC fact that logically implies X.

| Check | Default | What to look for |
|---|---|---|
| IC without `with` | minor | e.g. Ca²⁺ located in cytosol. Suggest the GO term it follows from (here the channel MF, GO:0008331). |
| Circular IC | minor | `with` = the asserted object itself: `G protein activity —enabled by→ GO:0005834` with GO:0005834 ("enabled by the complex because of the complex"). Suggest the term the fact follows from (GO:0004930 for a G protein downstream of a GPCR, the MF for a complex enabler) or an evidence comment citing the figure. |
| Wrong `with` (copy-paste) | major | `with` that has nothing to do with the fact: channel facts carrying `with GO:0046934` (the PI3K MF). Very common after copying a unit. Check every `with` against its fact. |
| `with` = the top BP on causal edges | minor | e.g. `with GO:0106134` on PI3K → PKC. The model's top BP doesn't imply a causal edge. |
| `with` = a term no longer in the model | major | e.g. `with GO:0060452` after the top BP was changed. |
| Recipe/code mismatch | major | GO_REF:0000024 is the ISS recipe and needs ECO:0000250; GO_REF:0000036 is the IC recipe and needs ECO:0000305. IDA + GO_REF:0000024 is an error. |
| IC may cite a paper | — | GO_REF:0000036 is for multi-source inference; IC can cite the paper of the supporting annotation instead. Don't flag IC + PMID as wrong. |

## C. ISS / orthology

| Check | Default | What to look for |
|---|---|---|
| ISS `with` ortholog has no source annotation | major | For each ortholog in `with`, run `noctua amigo search-annotations -b RGD:621884 -l 300` and look for an **experimental** annotation to the same or a more specific GO term. If none: unsupported ISS. If the curator says they made the annotation (e.g. in P2GO), say whether it's visible yet; new annotations appear only after the next AmiGO load. |
| ISS where a same-species paper exists | minor | e.g. receptor → G protein coupling: the human UTS2R cryo-EM paper (PMID:41062066) can be IDA directly; no ISS needed. Note context caveats (that structure is Gq; the cardiomyocyte pathway is Gi/o). |

## D. Species

| Check | Default | What to look for |
|---|---|---|
| Experimental code from another species | critical | Model `in_taxon` human, but IDA/IMP comes from rat cells. Options: (a) rebuild in the species of the data; (b) keep the species with ISS from annotated orthologs, or IC. |
| Complex classes are species-neutral | — | When the enabler is a GO complex class (GO:0005834, GO:0097651, GO:1990454) and no gene product is named, IDA from another species is defensible for that unit and for complex → complex edges. Raise species issues where a species-specific gene product is the enabler. |
| Respect the curator's decision | — | If the curator has decided to keep the model in a species (e.g. "not possible as some enablers are not defined"), don't raise it again as critical. Mention it once as context. |

## E. References out of context (standing check; curator request 2026-10-02)

The recurring problem: a reference copied from an **existing standard annotation** (AmiGO/GOA) of the gene supports the GO term for that gene in general, but not **this edge in this model's context** (cell type, tissue, pathway, stimulus, isoform, species).

For **every** PMID in the model:
1. Fetch the title and abstract (pubmed-eutils skill).
2. Compare its context with the specific fact and the model's context.
3. If they differ, raise it as category `reference-context`, even if a curator declined it before (then say so and keep the severity at major).

Examples:
- PMID:20228790 (PKCβI phosphorylates histone H3T6, androgen receptor, prostate) on `PKC activity part of protein kinase C signaling` in a U-II/cardiomyocyte pathway.
- PMID:15632189 (DGKθ in A431 cells) on `PKC occurs in cytoplasm`. The full text shows PKCβII in the cytoplasm only **at rest**; it moves to the PM on GPCR stimulation, so for the active kinase it supports the PM.
- PMID:25313067 (AngII/PKC/KLHL3, kidney) as the reference on the pathway's causal edges: unrelated paper.
- PMID:27715446 (UTS2R/CXCR4 autophagy, HEK-293/U87) for UTS2R at the PM: abstract silent on localization, so check the full text.
- PMID:41062066 (cryo-EM) on `part of GPCR signaling`: shows coupling, not a cellular pathway.

When the right paper is already in the model, suggest it with the figure (e.g. PMID:25678708 Fig. 5–6 for PKC signaling).

## F. Causal relations

Use `gocam-best-practice/references/Relation_selection.md`.

| Check | Default | What to look for |
|---|---|---|
| `directly` / `indirectly positively regulates` without a known mechanism | major | Both require the mechanism to be known. Pharmacology (inhibitor abolishes the response) shows only causality. RO:0002304 (causally upstream of, positive effect) is the honest default. |
| `indirectly` used for something other than a reused larger process | major | RO:0002407 is meant for regulation through a process not modelled (transcription, degradation). |
| Curator's mechanistic assumption | — | If the curator has a mechanistic reason ("via membrane recruitment", "via phospholipid production"), ask for a citation that shows it; without one, explain that the relation claims more than the cited paper does. Don't re-raise once declined. |
| Ligand → receptor | — | Ligand activity `has input` receptor, `directly positively regulates` receptor activity, occurs in the extracellular region. Separate receptor individuals for input and enabler. (Signaling receptor guideline.) |
| GPCR → G protein | — | Receptor `has input` heterotrimeric G-protein complex and `directly positively regulates` G protein activity (GO:0003925). Gβγ effector arm: GO:0141038 (PI3K activator activity) enabled by GO:0031680, `has input` a separate PI3K complex individual. Both are defensible. |

## G. Term choice and context

| Check | Default | What to look for |
|---|---|---|
| Generic enabler | critical | `enabled by PR:000000001 'protein'` part of a complex: when subunits are unknown, the GO complex class itself is the enabler. |
| Wrong MF for the entity | critical | e.g. Gβγ as GO:0043495 protein-membrane adaptor activity. Check the term's definition against what the paper shows. |
| Most specific term the data support | minor | Receptor: GO:0004930 → GO:0001604 urotensin II receptor activity. PI3K complex: GO:0005942 → class I GO:0097651 (CH5132799-sensitive). Cell type: CL:0000746 → CL:2000046 ventricular cardiac muscle cell. Don't go finer than the data (e.g. class IB). |
| Location contradicts the enabler or the biology | major | `occurs in cytoplasm` for a unit enabled by GO:0005834 (part of the cytoplasmic side of the PM). PI(4,5)P2 3-kinase acting in the cytoplasm. Active PKC (translocated) in the cytoplasm. Look up the CC parents in OLS. |
| CC `part of` cell type | — | The cell-type context can be IDA from the paper's Methods (e.g. isolated left ventricular myocytes). |
| BP nesting | minor | Every unit's BP should connect to the model's top process. |

## H. Model lineage and earlier rounds

- **Earlier QC of the same model**: look for `*-checklist*.md` files (especially `*-done.md`) in the curator's home. Items marked **Solved** should be verified as fixed. **Won't fix** items stay closed (note them once under "Decisions kept"), except reference-context (E).
- **Derived models** (`wasDerivedFrom`): fetch the parent's current TTL. A copy taken before the parent was fixed silently brings back old errors. Diff the facts (strip `[…1234]` handles, sort, `diff`) and list "parent fixes not carried over" separately.
- **Two models for one pathway**: optional finding. The curator decides which one to keep, and whether the other gets state `delete` or stays `internal_test`.

## I. Literature honesty

- Say exactly which papers you read in full text and which only as abstracts. Never infer figure-level detail from an abstract.
- Ask the curator for PDFs of the key papers. Europe PMC/NCBI often refuse full-text XML for publisher reasons. Name the PDFs on disk (`pdftotext` them), and note which PMID each one actually is: curators sometimes upload the wrong paper.
- A suggested Noctua comment cites PMID + figure and stays one or two sentences.
