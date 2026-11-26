---
name: annotation-review-ticket-close
description: Check whether a geneontology/go-annotation "annotation review" ticket (term obsoletion or annotation move) is done, using the editors' version of GO, Noctua and the live mapping sources, and if so propose closing it with a standard comment. Read-only until the curator approves the exact ticket and the exact comment. Use when a curator asks to check, close, or clean up one or more go-annotation review tickets, e.g. "can #6353 be closed?". Duplicate/superseded tickets are out of scope (separate skill).
license: BSD-3-Clause
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/annotation-review-ticket-close
---

# Annotation review ticket close

For one ticket at a time (or a short list the curator names), establish from the
data whether the review the ticket asked for is finished, report it, and propose
a closing comment. The curator decides. Nothing is posted without approval.

Out of scope: duplicate/superseded tickets, go-ontology tickets, mapping-only
tickets (labels containing ARBA, EC, RHEA, HAMAP, InterPro, UniRule, PAINT),
policy or discussion tickets.

## Rules

1. **Read-only until approved.** No `gh issue close/comment/edit/reopen` until the
   curator has approved, in this conversation, the exact ticket number(s) and the
   exact comment text. A go-ontology note needs its own separate approval.
2. **Every GO ID carries its name**, everywhere: "GO:0031388 obsolete organic acid
   phosphorylation", never a bare ID.
3. **Read the whole ticket** (body and every comment) before judging. Not the
   title, not the template: placeholders are often left unfilled.
4. **Only target terms decide.** Targets are the terms the ticket proposes to
   obsolete or review (title, "proposal has been made to obsolete ..." list, and
   any added in comments). Replacement terms (`replaced_by`, `consider`, or "replaced
   by ..." in the text) are expected to carry annotations and never count against the
   ticket. If a term's role is unclear, ask.
5. **Every claim traces to a query result or a quoted comment.** A 0 counts only
   if the same query returns hits on a positive control. Label speculation, or
   leave it out.
6. **Check first, draft second.**

## Sources (record the version or date of each in the report)

| Need | Source |
|---|---|
| Ticket | `gh issue view N -R geneontology/go-annotation --json number,title,state,createdAt,labels,body,comments,assignees` (re-fetch right before posting) |
| Term status | `git -C ~/go-ontology fetch -q origin && git -C ~/go-ontology show origin/master:src/ontology/go-edit.obo` (`is_obsolete`, `replaced_by`, `consider`, `alt_id`; use origin/master, the working copy may be stale; report the commit and date). The released ontology is not used: an obsoletion in go-edit is done. |
| Annotations | GOlr, last annotation release (query below) |
| Noctua models | `curl -s "http://barista.berkeleybop.org/search/models?term=GO:NNNNNNN&limit=100"` (production barista, read-only GET; all model states). If 100 models come back, say: "100 models have been found, which is the maximum number of hits. Let me know if I should fetch all models using the term(s)." Only then fetch the rest (`&count` gives the total). |
| Mappings: InterPro2GO | `curl -s -w '%{http_code}' "https://www.ebi.ac.uk/interpro/api/entry/interpro?go_term=GO:NNNNNNN&page_size=200"` → `results[].metadata.accession`, `.name`. HTTP 204 (empty body) = no entries. Version: `curl -s https://www.ebi.ac.uk/interpro/api/` → `databases.interpro.version` |
| Mappings: UniRule | `curl -s -D - "https://rest.uniprot.org/unirule/search?query=go:NNNNNNN&size=500"` (number without `GO:`) → `results[].uniRuleId`; header `x-total-results` |
| Mappings: ARBA | no GO search field: `curl -s "https://rest.uniprot.org/arba/stream?query=*&format=json"` (~200 MB, all rules) once per session, then in Python find rules whose `annotations[].dbReference` has `database: GO` and the target `id` |
| Mappings: UniProt keywords | no GO search field: `curl -s "https://rest.uniprot.org/keywords/stream?query=*&format=json"` once per session, then `results[].geneOntologies[].goId` |
| Mappings: UniProt subcellular locations | no GO search field: `curl -s "https://rest.uniprot.org/locations/stream?query=*&format=json"` once per session, then `results[].geneOntologies[].goId` (id `SL-NNNN`, `name`) |
| Mappings: Reactome | Reactome ContentService lists every GO term in the Reactome database: page through `https://reactome.org/ContentService/data/schema/{GO_BiologicalProcess,GO_MolecularFunction,GO_CellularComponent}?page=N&offset=500` (totals at `.../count`), match `accession` (number without `GO:`). Version: `https://reactome.org/ContentService/data/database/version`. Do not use reactome2go. |
| Mappings: Rfam | `curl -s https://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/rfam2go/rfam2go` (Rfam's own file; version line in the header), grep the GO ID |
| Mappings: HAMAP | `curl -s https://ftp.expasy.org/databases/hamap/hamap_rules.dat` once per session (release in the header); GO terms are on `GO   GO:NNNNNNN;` lines, the rule id on the preceding `AC   ` line |
| Mappings: EC, Rhea, MetaCyc, KEGG, RESID, UM-BBD | source of truth: the editors' version of the ontology (the same go-edit.obo at origin/master as Term status). Look for these `xref:` prefixes on the target's own stanza: `EC:`, `RHEA:`, `MetaCyc:`, `KEGG_REACTION:`, `KEGG_PATHWAY:`, `RESID:`, `UM-BBD_reactionID:`, `UM-BBD_pathwayID:`, `UM-BBD_enzymeID:` (e.g. `grep -E '^xref: (EC|RHEA|MetaCyc|KEGG_[A-Z]+|RESID|UM-BBD_[a-zA-Z]+):'`). Do not use the generated *2go files (ec2go, rhea2go, metacyc2go, kegg2go, resid2go, um-bbd*2go): they lag behind. |
| External ontologies | `runoak -i ubergraph: usages GO:NNNNNNN ...` (several IDs at once; can take a minute). Keep rows where `used_by_id` is not a GO term and the context is `UsageContext.RELATIONSHIP_OBJECT` (same filter as geneontology/annotation-query `term-usage-report.py`); report each using term and its ontology. Positive control: GO:0005634 nucleus is used in WBbt, FYPO, CL, OBA, MP. |
| Linked go-ontology ticket | `gh issue view M -R geneontology/go-ontology --json state,title,closedAt` |

Put all downloads in a `mktemp -d` directory. If `~/go-ontology` is missing, clone
https://github.com/geneontology/go-ontology (only `src/ontology/go-edit.obo` is needed).

GOlr count, one term at a time (`FIELD` = `annotation_class` for direct,
`annotation_extension_class` for extensions, `evidence_with` for "with"):
```
curl -s -A 'curl/8.5.0' 'https://golr.geneontology.org/solr/select?q=*:*&fq=document_category:annotation&fq=FIELD:%22GO:NNNNNNN%22&rows=0&wt=json&facet=true&facet.field=assigned_by&facet.field=evidence_type&facet.limit=-1&facet.mincount=1'
```
Total = `response.numFound`; groups and evidence are in `facet_counts.facet_fields`.
Positive control: GO:0005634 nucleus has hits in all three fields.

Traps:
- GOlr returns 403 without a User-Agent header (Python's default fails; curl works).
- GOlr holds the last annotation release: fixes made since are not visible, and
  annotations to obsolete terms are filtered out before loading, so GOlr cannot tell
  you whether any remain on an obsolete term.
- barista ignores unknown parameters and may return unrelated models. Count a model
  as a hit only if its `query_match` contains `http://purl.obolibrary.org/obo/GO_NNNNNNN`.
  Search is direct only (no subclasses). Report each hit's id and `state`.
- GOlr and Noctua answer different questions. GOlr hits + Noctua 0 means "fixed in
  Noctua, not yet released", not "clean". Noctua 0 clears only Noctua groups.
- Use the live mapping sources above, not the external2go files on
  current.geneontology.org: those are snapshots that can trail by months (for geneontology/go-annotation#6353,
  unirule2go still mapped UR000129101 to GO:0031388 after UniProt had removed it).
  Report the UniProt release (`x-uniprot-release` header) and the InterPro version.
- Positive controls for mappings: GO:0008887 glycerate kinase activity has InterPro
  entries (IPR004381, ...) and UniRule rules; GO:0051537 2 iron, 2 sulfur cluster
  binding is on keyword KW-0001 and in ARBA00026418; GO:0009085 L-lysine
  biosynthetic process is in HAMAP rules (MF_00102, ...); GO:0005634 nucleus is on
  subcellular location SL-0191 and in Reactome; GO:0005840 ribosome is in rfam2go
  (RF00001).
- Not checked, by curator request (geneontology/go-annotation#4559): pfam2go,
  pirsf2go, prints2go, prodom2go, prosite2go, smart2go.
- GOlr freshness: report the newest annotation date
  (`...&rows=1&sort=date%20desc&fl=date`). golr-aux.geneontology.io now redirects to
  golr.geneontology.org; it is not a fresher copy.

## Procedure

1. **Fetch the ticket** and confirm it is in scope (open; label `annotation review`
   or title starting "Review annotations"/"Annotation review"; no mapping label).
2. **List the GO IDs** from the title, body and comments, sorted into target /
   replacement / other, each with its name.
3. **Term status** of every target in go-edit (origin/master).
4. **Read the thread.** Report only comments that raise something other than the
   obsoletion itself (a question, an objection, a request nobody acted on, "please
   also ..."), quoted or summarized with author and date. Do not report sign-offs
   ("done"), groups that did not reply, or anything not in the thread. If there is
   nothing, say "none".
5. **Usage checks.** For every target: Noctua models and all live mapping sources
   (whether or not the ticket lists mappings). For a target that is **not** obsolete, also
   GOlr direct / extension / with and the external-ontology check (ubergraph).
6. **Classify and report** (below). Stop and wait for the curator.
7. **On approval only**, close (see "Closing").

### Case A: every target is obsolete in go-edit

The review is done: any remaining annotations are filtered out before loading (so GOlr/AmiGO cannot show them) and show up
in group error reports. Propose closing. Report:

- Ticket: link
- Date opened
- Linked go-ontology ticket: link, with its state
- Target terms (ID + name) with `replaced_by` / `consider`
- **Ticket comments**: the items from step 4 only, or "none".
- **Remaining usage**, a separate section built from the step 5 checks, not from
  the thread: Noctua models still using a target (id, state; at most 100, see
  Sources), and mappings still
  pointing at a target (source, its version, and the rule or entry with its name).
- **Positive controls**, a separate bullet: for each check (GOlr, Noctua, each
  mapping source) the control term (ID + name) and the hits it returned.

Anything in these two sections that needs action is listed as an action point, and
goes into the closing comment only if the curator agrees.

Default comment:
```
Closing: checked against the GO editors' version of the GO ontology (<commit date>). The term(s) reviewed in this ticket have been obsoleted. Any remaining annotations are filtered out of the release and appear in the GO error reports. If there is a further problem, please open a new ticket.
```

### Case B: some target is not obsolete in go-edit

Do not propose closing. Report the same Ticket / Date opened / Linked go-ontology
ticket bullets, Ticket comments and Positive controls as in Case A, the status of each target
(obsolete / live), then a usage table for every live target:

| Target term (ID + name) | Direct annots (manual*) | Extension | With | Noctua models | Mappings | External ontologies | Groups with annotations |
|---|---|---|---|---|---|---|---|

\* Direct annotations excluding IEA, ISS, ISO and ISM. Give the full `evidence_type`
breakdown on request.

If the newest GOlr annotation date (see Sources) is earlier than the ticket's opening
date, say so: the GOlr counts are the starting point, not progress, and groups that
signed off will still show annotations until the next release. Until then, judge
progress from the sign-offs in the thread and the live sources (Noctua, mappings,
Reactome).

List what is left and which groups to ping. Report counts only, not annotation rows:
link the review spreadsheet given in the ticket body, which is where contributors
review their annotations.

## Closing (only after approval)

- Re-fetch the ticket: still `OPEN`, no new comments since the report. If anything
  changed, stop and show the curator.
- Restate once: "Closing #N with this comment: ...".
- Write the comment to a `mktemp` file with `printf '%s\n' ...`, `cat` it, then
  `gh issue close N -R geneontology/go-annotation --reason completed --comment "$(cat "$F")"`.
  For several tickets, pause about 2 s between calls and stop at the first failure.
- Verify: `gh issue view N --json state,stateReason,comments` shows `CLOSED`,
  `COMPLETED`, and the last comment is the text you posted.
- Append a timestamped line per ticket to `~/go-annotation-closed-<YYYY-MM-DD>.txt`.
- If something went wrong, say so at once with the ticket number and offer the fix.

### Optional: note on the linked go-ontology ticket

Only if the review ticket was just closed by this skill **and** it links a
go-ontology ticket for the same terms that is **still open** (re-check just before
posting). Show the note and its target link, and get separate approval. Comment only:
never close, label or edit a go-ontology ticket. Default:
```
Annotation check for GO:NNNNNNN <term name>: <N> direct annotations and <N> uses in annotation extensions in the GO <annotation release date> annotation release; <N> Noctua models as of <date>. Reported from geneontology/go-annotation#N.
```
Every `<N>` comes from this run's query results.
