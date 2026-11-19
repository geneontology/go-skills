---
name: go-annotation-easy-closes
description: Find "easy close" annotation-review tickets in geneontology/go-annotation — tickets whose GO terms are obsolete (or slated for obsoletion) and have no annotations left. Read-only triage that produces a categorized, evidence-backed list for a curator to approve. Use when a curator asks to clean up, triage, or find closable tickets in the go-annotation tracker. Never closes or comments without explicit approval of an exact list and exact text.
license: BSD-3-Clause
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/go-annotation-easy-closes
---

# go-annotation easy closes

Triage skill for the **go-annotation** tracker. It finds review tickets that are
safe to close because the work they asked for is already reflected in GO, and it
presents them for a curator's decision. It does **not** decide, and it does not touch
GitHub until the curator approves a specific list and specific text.

Out of scope: closing go-ontology tickets, mapping tickets (UniRule, ARBA, InterPro,
keywords, TreeGrafter, PAINT), and policy or discussion tickets. Mapping tickets need
checks against the live sources (UniProt, InterPro, QuickGO), and those belong in a
separate skill.

---

## 0. Non-negotiable rules (read before every step)

1. **Read-only by default.** No `gh issue close`, `comment`, `reopen` or `edit` until
   the curator has approved (a) an explicit list of ticket numbers and (b) the exact
   comment text, in this conversation, for this batch. This includes comments on
   go-ontology tickets (section 8b).
2. **Never widen an approved set.** Approval is per category and per list. Approving
   "Category A" does not cover Category B, the "maybe" list, or anything you find later.
   If refining the criteria adds tickets from another category, **stop**, say so
   plainly, and ask for separate approval.
   Every list you show must label each ticket with its category. Before acting,
   restate: "Closing N tickets, all Category X, numbers: …".
3. **Every GO ID gets its term name**, everywhere: tables, drafts, comments, summaries.
   Write "GO:0005615 obsolete extracellular space", never a bare "GO:0005615".
4. **Don't judge a ticket by its title or template.** Editors often leave template
   placeholders unfilled or give tickets throwaway titles (a ticket titled "test" was a
   real obsoletion request). Judge by the terms and the annotations.
5. **Group sign-offs don't prove a ticket is done.** Many groups never reply. "X done"
   comments are supporting evidence only. What is (or isn't) in GO is the evidence.
6. **No annotations left does not mean the work was done.** Annotations to a term
   with only `consider`, or no replacement, drop out at obsoletion without anyone
   re-annotating. Report this distinction (section 4); never hide it.
7. **Recent tickets are off limits.** Curators need time to notice an obsoletion and
   push back, and closing early rewards short notice. **Before any triage, ask the
   curator how recent a ticket must be to leave it alone**, suggesting 1 year as the
   default. Use their answer (or 1 year if they accept the default) as the **age
   cutoff** for the whole session, and state it in every report. Tickets opened
   after the latest GO release are always excluded, whatever the cutoff.
8. **Don't make things up.** Every claim in your report must trace to a query result or
   a quoted comment. If you speculate (biology, intent, who will fix what), label it as
   speculation or leave it out.
9. **Check everything before drafting anything.** Run the checks first, then write
   drafts or recommendations, never the other way round.

---

## 1. The three categories (and nothing else)

Define these exactly and keep them separate in every output.

### Category A: obsolete and nothing left
All of the following:
- every **target** term in the ticket is obsolete in the **current release**
  (go-basic.obo `data-version`) or merged (now an `alt_id`);
- **0 direct annotations** to every target term (GOlr `annotation_class`);
- **0 uses** of every target term in annotation extensions (GOlr
  `annotation_extension_class`);
- **0 Noctua models** using any target term (production barista, section 2);
- ticket older than the age cutoff (rule 7) and opened before the release date;
- passes every exclusion in section 3.

### Category B: slated for obsoletion and nothing left
All of the following:
- target term(s) obsolete or merged (now an `alt_id`) in **go-edit.obo** (latest
  `origin/master`) but **not yet in a release**. A closed go-ontology ticket is not
  evidence: tickets are closed for many reasons (obsoletion declined, merged instead,
  duplicate, partial, reverted). Report the linked ticket's state as context only;
- 0 direct annotations, 0 extension uses and 0 Noctua models (as above);
- ticket older than the age cutoff (rule 7);
- passes every exclusion in section 3.

Category B is weaker: the release hasn't happened yet, so groups may still be acting.
Present it separately and recommend waiting unless the curator says otherwise.

### Category C: superseded or duplicate
All of the following:
- another **open** ticket covers the same target terms or the same request (same title
  terms, same rule or entry, or the ticket text or a linked go-ontology ticket says one
  replaces the other);
- the curator chooses which one to keep;
- both threads have been read in full (section 6).

Category C tickets are **proposed**, never hidden, but closed only with the duplicate
procedure in section 6 (linking comment on the kept ticket, then
`--duplicate-of`), never in an A or B batch. The age cutoff does not apply to the
ticket being closed: superseding is not a notice-period question. Still report both
tickets' ages.

**Everything else is "not proposed".** List it in a separate section with the reason
it isn't proposed. "Not proposed" items are never closed in a batch.

### Target terms vs other terms in the ticket
A review ticket usually mentions **target** terms (to be obsoleted or reviewed) and
**replacement** terms (where annotations should go). Replacement terms *should* have
annotations. Never count them against a ticket.
- Target terms: those in the title, plus those listed under "proposal has been made
  to obsolete …" or equivalent.
- Replacement terms: `replaced_by` or `consider` targets of the target terms, **and**
  terms the ticket text names as replacements ("replace by …", "can be transferred
  to …"), which may not be recorded as `replaced_by`.
- Also collect GO IDs from **comments**, not just the body; follow-ups often add terms.
- If a body ID is annotated and is neither a target nor a replacement, read the ticket
  and say what role it plays. Don't guess.

---

## 2. Data sources, versions and freshness

Record, at the top of every report: the time of the check, the go-basic.obo
`data-version`, the go-edit.obo commit (`git -C ~/go-ontology fetch && git log -1
origin/master`), and the newest annotation date in GOlr.

| Need | Source | Notes |
|---|---|---|
| Released term status | `http://purl.obolibrary.org/obo/go/go-basic.obo` | `is_obsolete`, `replaced_by`, `consider`, `alt_id` |
| Pending status | `~/go-ontology/src/ontology/go-edit.obo` at **origin/master** | use `git show origin/master:src/ontology/go-edit.obo`; the working copy may be stale |
| Annotations, all groups | `https://golr.geneontology.org/solr/select` | holds the **last release** only; fixes made since then are not visible |
| Annotations, live Noctua | `http://barista.berkeleybop.org/search/models?term=GO:NNNNNNN&limit=2000` (production, read-only GET; never `--live` writes) | current, but **only groups that curate in Noctua**; no IEA, no PAINT, no groups using their own tools or Protein2GO |
| Ticket text | `gh issue view N -R geneontology/go-annotation --json …,comments` | always re-fetch just before reporting; snapshots go stale |

### GOlr count query (tested 2026-11-19)

Direct annotations (`FIELD=annotation_class`) or extension uses
(`FIELD=annotation_extension_class`) for one term, broken down by group and evidence:
```
curl -s -A 'curl/8.5.0' 'https://golr.geneontology.org/solr/select?q=*:*&fq=document_category:annotation&fq=FIELD:%22GO:NNNNNNN%22&rows=0&wt=json&facet=true&facet.field=assigned_by&facet.field=evidence_type&facet.limit=-1&facet.mincount=1'
```
Total is `response.numFound`; breakdowns are in `facet_counts.facet_fields`.
Controls: GO:0002183 cytoplasmic translational initiation has thousands of direct annotations;
GO:0005634 nucleus has thousands of extension uses; a nonexistent ID returns 0. A
misspelled field returns an error, not 0.

### Known traps (each one caused a wrong answer before)
- **GOlr returns 403 to Python's default user agent.** Send a User-Agent header (e.g.
  `curl/8.5.0`). curl works as is.
- **GOlr doesn't support pivot facets.** Query one term at a time with
  `facet.field=assigned_by` and `facet.field=evidence_type`; cache the results.
- **Absence is only meaningful if the query could have found something.** Before
  trusting a 0, run a positive control with the same query shape on something that
  should have hits.
  - Fly, mouse, worm, yeast and other MOD genes are under **MOD IDs** (FB:, MGI:MGI:,
    WB:, SGD:, PomBase:), not UniProtKB.
  - Some species aren't in GO at all.
  - TreeGrafter records the **PTN node** in `evidence_with`, not the PTHR family.
  - PomBase filters a lot of IEA, so missing pombe IEAs are uninformative.
- **Stale snapshots.** GO's external2go files and GOlr lag behind the sources. Say how
  old every dataset is; never present a snapshot as current.
- **Release vs edit.** A term can be obsolete in go-edit and live in the release. Always
  say which.
- **GOlr and Noctua answer different questions; report both, side by side.**
  - Noctua hits on a target term: someone still has live annotations. Not proposed,
    even if GOlr shows 0.
  - GOlr hits, Noctua 0: a Noctua group may have fixed theirs since the release.
    Report "fixed in Noctua, not yet released", never "clean".
  - Noctua 0 clears only Noctua groups. For everyone else the GOlr count stands.
- **barista search ignores parameters it doesn't know and returns arbitrary
  models.** `n` echoes the limit. Count a model as a hit only if its `query_match`
  contains the target term's IRI (`http://purl.obolibrary.org/obo/GO_NNNNNNN`). Use
  `&count` for the total. Positive control: a term known to be in models.
- **barista term search is direct only** (no subclasses) and includes models in every
  state (`production`, `development`, …). Report the state of each hit.

---

## 3. Exclusions (any one of these means "not proposed")

1. **Newer than the age cutoff** the curator set (rule 7), or opened after the latest
   release date.
2. **The curator has said to keep it open.** Keep a running list in the session and in
   memory, and check it every pass.
3. **Thread without a resolution.** If a ticket has **any** comments, read every one
   of them. Exclude it if the thread ends in debate, an open question, objections, "disputed", or a
   request nobody acted on. If in doubt, list it under "for you to read" with a
   two-line summary of where it stands.
4. **Unanswered question or unactioned request** in the last comments (a question
   addressed to someone who never replied; "please also remove X").
5. **A target term is still live** in both the release and go-edit. The ticket may be
   about policy or guidance, so leave it for the curator.
6. **A target term is used in an annotation extension** (`annotation_extension_class`).
7. **The ticket is superseded or a duplicate.** Not dropped: move it to **Category C**
   (section 1) and propose it there, with the section 6 procedure.
8. **The ticket is about a mapping** (UniRule, ARBA, InterPro, keywords, PAINT,
   TreeGrafter). Out of scope; needs live-source checks.

---

## 4. Auto-migrated vs re-annotated (always report)

For each proposed ticket, classify the target terms:
- **auto**: every target term has exactly one `replaced_by`, so annotations migrate
  without a curator.
- **recurate**: some target term has only `consider`, or nothing, so annotations were
  either moved by curators or **dropped**.

For **recurate** tickets:
- List the impacted groups from the ticket body and which ones **never signed off**.
- If the review spreadsheet is public (`https://docs.google.com/spreadsheets/d/<id>/export?format=csv`
  returns CSV, not HTML), check each row from a silent group. For each gene + paper,
  does that group still have an annotation **in the same aspect**? Report "moved" vs
  "nothing now" counts and examples (gene, PMID, old term with name).
- Large unconfirmed counts (e.g. MGI 57) go in the report even if the ticket is
  proposed, so the curator can choose to ping the group.

---

## 5. Procedure

0. **Ask for the age cutoff** (rule 7): "How recent should a ticket be for me to
   leave it alone? Default: 1 year." Wait for the answer before going on.
1. **Pull fresh** (in a `mktemp -d` directory):
   `gh issue list -R geneontology/go-annotation --state open --limit 3000 --json number,title,body,labels,createdAt,updatedAt,author,comments,assignees`
2. **Select review tickets**: label `annotation review`, or title starting
   "Review annotations" or "Annotation review". Leave mapping-labelled tickets out.
3. **Extract GO IDs** from the title, body and comments. Sort them into target vs
   replacement (section 1). Look up the name of every ID.
4. **Term status**: release (go-basic) and pending (go-edit origin/master).
5. **Annotations**: direct counts per target term, by `assigned_by` and
   `evidence_type`; extension counts per target term; Noctua models per target term
   (id, state, groups).
6. **Find superseded and duplicate pairs (Category C).** Among open review tickets,
   pair those with the same target terms (identical or near-identical GO-ID sets, or
   near-identical titles). Also check each ticket's linked go-ontology ticket: if it
   was closed as a duplicate of, or replaced by, another ticket, find the
   go-annotation ticket for the newer one. Check the latest go-edit: if the terms were
   already merged or obsoleted under a newer ticket, the older review is superseded.
   Read both threads (section 6).
7. **Age and exclusions** (section 3). Read every comment on every ticket that has any.
8. **Auto vs recurate** (section 4).
9. **Report** (section 7). Stop and wait.
10. **On approval only**: run the close procedure (section 8 for A/B, section 6 for C) on
    **exactly** the approved numbers.

---

## 6. Duplicates

- Duplicates are **Category C**: always proposed, but approved and closed
  separately, never part of an A or B batch.
- The curator chooses which ticket to keep.
- Before proposing, read **both** threads in full and tell the curator what the ticket
  being closed holds that the kept one lacks: alternative suggestions, discussion,
  conclusions. Check whether that content is still current (a later decision may have
  superseded it). Check whether the closed ticket's author or assignee is involved in
  the kept ticket; if not, point this out.
- Order of operations: (1) post a linking comment on the **kept** ticket, (2) close the
  other with `gh issue close N -R geneontology/go-annotation --duplicate-of M --comment "$(cat FILE)"`. **Both tickets get a
  comment.** GitHub's "closed as duplicate" marker alone gives no reason in the
  conversation, and the closed ticket's author and assignees are the ones notified.
- Default comment on the **closed** ticket (curator-approved):
  ```
  Superseded by #M (one-line reason, with GO IDs and names and any linked ticket).

  Closing as a duplicate of #M.
  ```
- Default layout for the linking comment (curator-approved):
  ```
  Related: #N (one-line description).

  **The key suggestion or conclusion carried over from #N, in bold on its own line.**

  Closing #N as a duplicate of this ticket.
  ```
- Never add recommendations that would reopen a decision already made elsewhere.
- Write plainly and directly: "recommend checking", not "worth checking", "might
  want to" or other hedges.
- Cross-repo links must be written `geneontology/go-ontology#NNNN`; a bare
  `go-ontology#NNNN` doesn't link.

---

## 7. Report format

Header: time of check; data versions (section 2); the age cutoff in use.

Then one section per category (A, B, C), each with a table:

| Ticket | Opened | Comments | Target terms (ID + name) | Release / go-edit status | auto / recurate | Direct annots (release) | Extension annots (release) | Noctua models (now) | Groups never confirmed | Flags |

Then:
- **Not proposed**, with the reason for each (the exclusion number from section 3).
- **For you to read**: two-line thread summaries.
- **Notes for linked go-ontology tickets** (section 8b), if any.
- **Gaps and caveats**: what you didn't or couldn't check (private spreadsheets,
  species not in GO, snapshot ages).
- **Proposed comment text**, shown as raw markdown.

End with a question asking which category or numbers to act on. Never end with
"Should I go ahead?" on a list that mixes categories.

Default closing comment (adjust only with approval):
```
Closing: checked against the GO <release date> release and Noctua as of <date>, no direct annotations remain to the GO term(s) in this ticket and none are used in annotation extensions. Any that reappear will be flagged in group error reports. If there is a further problem, please open a new ticket.
```

---

## 8. Close procedure (only after approval)

- **Re-verify each approved comment just before posting**, even if it was approved
  minutes ago: every GO ID has its name, every linked ticket is cited and written as a
  working link, the ticket is still `OPEN`, and the counts still hold (re-run the
  checks if more than a few hours have passed or anything was edited). If anything
  changed, stop and show the curator before posting.
- Restate the exact numbers and category, and the exact comment, once, before running.
- Build the comment in a `mktemp` file with `printf '%s\n' …` (one argument per line),
  `cat` it, and check it. **Do not put a heredoc right after a `\` line continuation:**
  that once dropped the first line of a posted comment.
- For each ticket: re-check that it is `OPEN`, then
  `gh issue close N -R geneontology/go-annotation --reason completed --comment "$(cat FILE)"`
  (`gh issue close` has no `--body-file` flag). Pause about 2 seconds between calls; **stop at the
  first failure** and report it.
- Afterwards, **verify** every ticket (state, `stateReason`, and the full text of the
  last comment) and report anything that doesn't match.
- Log each action with a timestamp to `~/go-annotation-closed-<date>.txt`, and
  update the session log.
- If something went wrong (wrong scope, malformed comment), say so at once, plainly,
  with the ticket numbers, and offer the fix (edit the comment, reopen). Don't wait to
  be asked.

---

## 8b. Friendly note on the linked go-ontology ticket

A small courtesy, not part of the main task, and rarely needed: editors usually close
the go-ontology ticket when they obsolete the term. This covers the case where they
didn't. Post a note on the go-ontology ticket **if and only if all** of these hold:
1. the go-annotation review ticket is **closed by this skill** (approved, closed and
   verified in section 8), because the review is done and no annotations remain;
2. the review ticket links a go-ontology ticket for the same terms, and that ticket
   **exists**;
3. the go-ontology ticket is **still open** (re-check its state just before posting).

Any other case: no note. In particular, no note for tickets left open, "not
proposed" tickets, or closed go-ontology tickets.

- List candidates in the report under **"Notes for linked go-ontology tickets"**, with
  the review ticket they follow from and a draft note for each.
- **Approved separately** from the go-annotation close, ticket by ticket. Approving a
  close batch never covers these.
- Never close, label, assign or edit go-ontology tickets (the curator isn't an
  ontology editor). Comment only.
- State counts, not conclusions. "No annotations" is not "done" (rule 6).
- Default note (curator-approved, 2026-11-19; keep it dry, no mention of Claude):
  ```
  Annotation check for GO:NNNNNNN <term name>: <N> direct annotations and <N> uses in annotation extensions in the GO <release date> release; <N> Noctua models as of <date>. Reported from geneontology/go-annotation#N.
  ```
  Every `<N>` is the count from the checks in this run, filled in from the query
  result. Never type a number from memory or assumption.

---

## 9. Phrases that should make you stop

- "That's in section 2 too", "while I'm at it", "these also qualify": that's
  widening the scope. Stop and ask.
- "Probably fine", "likely": you haven't checked. Check, or label it as speculation.
- A bare GO ID in your draft: add the name.
- A count of 0 you haven't validated with a positive control.
- A draft written before the checks were run.
