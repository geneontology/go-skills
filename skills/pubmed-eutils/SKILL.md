---
name: pubmed-eutils
description: Search PubMed and fetch article metadata directly through NCBI E-utilities (esearch, efetch, esummary) with curl, reporting PMIDs. Use whenever a curator needs literature for a gene, process, or claim, wants a PMID for a citation, or asks to look something up in PubMed. Do not use a PubMed MCP for this.
license: BSD-3-Clause
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/pubmed-eutils
  maintainer: geneontology
---

# PubMed searches via NCBI E-utilities

Use NCBI E-utilities directly via curl. Do NOT use a PubMed MCP.
Always include `email=help@geneontology.org&tool=go-ai-hub` in requests, and `&api_key=$NCBI_API_KEY` when that variable is set (it is on the GO AI hub; without it NCBI allows 3 requests/second).
Always report PMIDs instead of or in addition to DOIs.

Two-step workflow:

1. **Search for PMIDs** (esearch):
   ```
   curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=50&term=QUERY&retmode=json&email=help@geneontology.org&tool=go-jupyter&api_key=$NCBI_API_KEY"
   ```
   Returns JSON with a list of PMIDs in `esearchresult.idlist`.

2. **Fetch details** (esummary for metadata, efetch for full abstracts):
   ```
   curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=PMID1,PMID2,...&retmode=json&email=help@geneontology.org&tool=go-jupyter&api_key=$NCBI_API_KEY"
   ```
   Returns title, authors, journal, date, DOI per article.

   For full abstracts use efetch with XML:
   ```
   curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2,...&retmode=xml&email=help@geneontology.org&tool=go-jupyter&api_key=$NCBI_API_KEY"
   ```
