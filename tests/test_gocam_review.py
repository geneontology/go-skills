"""gocam-review: the fetch script's id handling (no network) and the QC script
on a fixture (a production model as served by Noctua on 2026-10-14), offline."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/gocam-review"
FETCH = SKILL / "scripts/fetch_model.sh"
QC = SKILL / "scripts/gocam_qc.py"
FIX = ROOT / "tests/fixtures/gocam-review"
TTL = FIX / "ZFIN_ZDB-GENE-991207-22.ttl"
GPAD = FIX / "ZFIN_ZDB-GENE-991207-22.gpad"


class FetchIdTests(unittest.TestCase):
    def dry(self, *args):
        return subprocess.run(["bash", str(FETCH), *args, "--dry-run"], capture_output=True, text=True)

    def test_id_forms_resolve_to_the_same_model(self):
        forms = [
            "gomodel:ZFIN_ZDB-GENE-991207-22",
            "ZFIN_ZDB-GENE-991207-22",
            "http://noctua.geneontology.org/editor/graph/gomodel:ZFIN_ZDB-GENE-991207-22",
            "http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel:ZFIN_ZDB-GENE-991207-22&x=1",
            "http://noctua.geneontology.org/download/gomodel:ZFIN_ZDB-GENE-991207-22/owl",
        ]
        for f in forms:
            r = self.dry(f)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("gomodel:ZFIN_ZDB-GENE-991207-22 from http://noctua.geneontology.org", r.stdout, f)

    def test_messy_browser_forms(self):
        for f in [
            "http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel:5b91dbd100002057#summary",
            "http://noctua.geneontology.org/download/gomodel:5b91dbd100002057/owl?x=1",
            "http://noctua.geneontology.org/editor/graph/gomodel:5b91dbd100002057#",
            "gomodel:5b91dbd100002057/",
            "5b91dbd100002057//",
        ]:
            r = self.dry(f)
            self.assertEqual(r.returncode, 0, (f, r.stderr))
            self.assertIn("gomodel:5b91dbd100002057 from http://noctua.geneontology.org", r.stdout, f)

    def test_dev_environment(self):
        self.assertIn("http://noctua-dev.berkeleybop.org", self.dry("gomodel:5b91dbd100002057", "dev").stdout)
        self.assertIn("http://noctua-dev.berkeleybop.org", self.dry("gomodel:5b91dbd100002057", "--dev").stdout)
        # a dev URL names its own server, whatever else is said
        r = self.dry("http://noctua-dev.berkeleybop.org/editor/graph/gomodel:5b91dbd100002057", "production")
        self.assertIn("http://noctua-dev.berkeleybop.org", r.stdout)
        self.assertIn("using that rather than", r.stderr)

    def test_outdir_in_any_position(self):
        r = self.dry("gomodel:5b91dbd100002057", "/tmp/somewhere")
        self.assertIn("into /tmp/somewhere", r.stdout)
        r = self.dry("gomodel:5b91dbd100002057", "dev", "/tmp/elsewhere")
        self.assertIn("into /tmp/elsewhere", r.stdout)

    def test_bad_input(self):
        self.assertEqual(self.dry("not a model id!").returncode, 2)
        self.assertEqual(self.dry("../etc/passwd").returncode, 2)
        self.assertEqual(subprocess.run(["bash", str(FETCH)], capture_output=True).returncode, 2)


sys.path.insert(0, str(SKILL / "scripts"))
import gocam_qc  # noqa: E402  (rdflib comes from tests/requirements.txt)

PREFIXES = """
@prefix : <http://model.geneontology.org/T#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix lego: <http://geneontology.org/lego/> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix m: <http://model.geneontology.org/T/> .
@prefix pav: <http://purl.org/pav/> .
<http://model.geneontology.org/T> a owl:Ontology ; dc:title "t" ; lego:modelstate "development" ; dc:contributor "https://orcid.org/0000-0000-0000-0000" ; pav:providedBy "http://geneontology.org" .
m:a a owl:NamedIndividual, obo:GO_0003674 .
m:b a owl:NamedIndividual, obo:GO_0003674 .
m:gp a owl:NamedIndividual, <http://identifiers.org/mgi/MGI:97490> .
m:ev a owl:NamedIndividual, obo:ECO_0000314 ; dc:source "PMID:1" .
m:a obo:RO_0002333 m:gp .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002333 ; owl:annotatedTarget m:gp ; lego:evidence m:ev ] .
"""


def analyse(ttl: str, sparql=True):
    g = gocam_qc.Graph(); g.parse(data=ttl, format="turtle")
    f = gocam_qc.Findings()
    out = gocam_qc.analyse(g, gocam_qc.Terms(offline=True), f, FIX / "sparql" if sparql else None)
    return out, f


class CurieTests(unittest.TestCase):
    def test_forms(self):
        c = gocam_qc.curie
        self.assertEqual(c("http://identifiers.org/zfin/ZDB-GENE-991207-22"), "ZFIN:ZDB-GENE-991207-22")
        self.assertEqual(c("http://identifiers.org/uniprot/P12345"), "UniProtKB:P12345")
        self.assertEqual(c("http://identifiers.org/mgi/MGI:97490"), "MGI:MGI:97490")   # GO writes MGI ids doubled
        self.assertEqual(c("http://purl.obolibrary.org/obo/GO_0003674"), "GO:0003674")
        self.assertEqual(c("http://purl.obolibrary.org/obo/RO_0002333"), "RO:0002333")
        self.assertEqual(c("http://model.geneontology.org/X/abc"), "X/abc")


class SyntheticModelTests(unittest.TestCase):
    def errors(self, f):
        return [x["message"] for x in f.by("error")]

    def test_clean_edge_with_evidence(self):
        ttl = PREFIXES + """
m:a obo:RO_0002629 m:b .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:ev ] .
"""
        out, f = analyse(ttl)
        self.assertEqual(out["activity_count"], 2)
        self.assertEqual(len(out["causal_edges"]), 1)
        self.assertEqual(out["causal_edges"][0]["p_label"], "directly positively regulates")
        self.assertEqual(self.errors(f), [])
        self.assertIn("enabled_by", " ".join(x["message"] for x in f.by("warning")))  # b has no enabler

    def test_disconnected_individual_is_an_error_natively_and_by_query(self):
        ttl = PREFIXES + "m:lonely a owl:NamedIndividual, obo:GO_0005634 .\n"
        out, f = analyse(ttl)
        msgs = self.errors(f)
        native = [m for m in msgs if "connected to nothing" in m]
        self.assertEqual(len(native), 2, msgs)   # lonely and b (no edge); the query says the same
        self.assertTrue(any("check-disconnected-individuals.rq: 2 row" in m for m in msgs), msgs)

    def test_multiply_reified_edge_is_an_error_natively_and_by_query(self):
        ttl = PREFIXES + """
m:a obo:RO_0002629 m:b .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:ev ] .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; dc:date "2020-01-01" ] .
"""
        out, f = analyse(ttl)
        msgs = self.errors(f)
        self.assertTrue(any("reified 2 times" in m for m in msgs), msgs)
        self.assertTrue(any("check-multiply-reified-edges.rq" in m and "row" in m for m in msgs), msgs)

    def test_axiom_only_edge_counts_and_is_not_disconnected(self):
        ttl = PREFIXES + """
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:ev ] .
"""
        out, f = analyse(ttl)
        self.assertEqual(len(out["causal_edges"]), 1)
        self.assertFalse(any("connected to nothing" in m for m in self.errors(f)), self.errors(f))
        self.assertTrue(any("reified but not asserted" in x["message"] for x in f.by("info")))

    def test_obsolete_relation_and_two_enablers(self):
        ttl = PREFIXES + """
m:gp2 a owl:NamedIndividual, <http://identifiers.org/uniprot/P12345> .
m:a obo:RO_0002333 m:gp2 .
m:a obo:RO_0002406 m:b .
"""
        out, f = analyse(ttl, sparql=False)
        self.assertTrue(any("RO:0002406" in m and "obsolete" in m for m in self.errors(f)))
        self.assertEqual(len(out["activities"][0]["enabled_by"]) + len(out["activities"][1]["enabled_by"]), 2)
        self.assertTrue(any("2 enablers" in x["message"] for x in f.by("info")))
        self.assertTrue(any("queries not run" in x["message"] for x in f.by("info")))


class EvidenceRuleTests(unittest.TestCase):
    """The with/from, reference and recipe rules the curators' dump flagged."""

    def findings(self, ttl, sev=None):
        out, f = analyse(ttl, sparql=False)
        return [x["message"] for x in f.items if sev is None or x["severity"] == sev]

    def test_with_required_and_forbidden(self):
        ttl = PREFIXES + """
m:ev2 a owl:NamedIndividual, obo:ECO_0000305 ; dc:source "PMID:2" .
m:ev3 a owl:NamedIndividual, obo:ECO_0000314 ; dc:source "PMID:3" ; lego:evidence-with "UniProtKB:P1" .
m:a obo:RO_0002629 m:b .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:ev2 , m:ev3 ] .
"""
        w = " | ".join(self.findings(ttl, "warning"))
        self.assertIn("IC with no with/from", w)
        self.assertIn("IDA and carries with/from", w)

    def test_circular_with_and_recipe_and_reference_form(self):
        ttl = PREFIXES + """
m:bp a owl:NamedIndividual, obo:GO_0007155 .
m:evc a owl:NamedIndividual, obo:ECO_0000305 ; dc:source "PMID:4" ; lego:evidence-with "GO:0007155" .
m:evr a owl:NamedIndividual, obo:ECO_0000314 ; dc:source "GO_REF:0000024" .
m:evm a owl:NamedIndividual, obo:ECO_0000315 ; dc:source "pmid 12345" .
m:a obo:BFO_0000050 m:bp .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:BFO_0000050 ; owl:annotatedTarget m:bp ; lego:evidence m:evc , m:evr , m:evm ] .
"""
        msgs = " | ".join(self.findings(ttl))
        self.assertIn("circular with/from", msgs)
        self.assertIn("recipe mismatch", msgs)
        self.assertIn("not in a recognised form", msgs)

    def test_species_mismatch_and_taxon(self):
        ttl = PREFIXES.replace('pav:providedBy "http://geneontology.org" .', 'pav:providedBy "http://geneontology.org" ; <https://w3id.org/biolink/vocab/in_taxon> obo:NCBITaxon_9606 .')
        msgs = " | ".join(self.findings(ttl))
        self.assertIn("MGI:MGI:97490 (MGI) implies NCBITaxon:10090", msgs)
        self.assertNotIn("model has no taxon", msgs)
        self.assertIn("model has no taxon", " | ".join(self.findings(PREFIXES)))

    def test_facts_only_strips_handles(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.ttl"; p.write_text(PREFIXES + "m:a obo:RO_0002629 m:b .\n")
            r = subprocess.run([sys.executable, str(QC), str(p), "--offline", "--facts-only"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("GO:0003674 --directly positively regulates--> GO:0003674 ::", r.stdout)
            self.assertNotIn("m:a", r.stdout)


class OnlineLikeTerms(gocam_qc.Terms):
    """A stand-in for OLS: namespaces and an obsolete term, without network."""

    def __init__(self):
        super().__init__(offline=True)
        self.offline = False

    def lookup(self, term):
        table = {"GO:0003674": ("molecular_function", None, False), "GO:0005634": ("nucleus", "cellular_component", False),
                 "GO:0007155": ("cell adhesion", "biological_process", False), "GO:0004672": ("protein kinase activity", "molecular_function", False),
                 "GO:0000001": ("old term", "biological_process", True)}
        if term in table:
            label, ns, obs = table[term]
            return {"id": term, "label": label, "namespace": ns, "obsolete": obs, "subsets": ["gocheck_do_not_annotate"] if term == "GO:0007155" else [], "found": True}
        return {"id": term, "label": None, "namespace": None, "obsolete": None, "subsets": [], "found": False}

    def save(self):
        pass


def analyse_online_like(ttl):
    g = gocam_qc.Graph(); g.parse(data=ttl, format="turtle")
    f = gocam_qc.Findings()
    out = gocam_qc.analyse(g, OnlineLikeTerms(), f, None)
    return out, f


class FlagCoverageTests(unittest.TestCase):
    def msgs(self, f, sev=None):
        return [x["message"] for x in f.items if sev is None or x["severity"] == sev]

    def test_no_evidence_on_context_and_process_edges(self):
        ttl = PREFIXES + "m:bp a owl:NamedIndividual, obo:GO_0007155 .\nm:a obo:BFO_0000050 m:bp .\nm:gp obo:RO_0002264 m:bp .\n"
        out, f = analyse(ttl, sparql=False)
        errs = " | ".join(self.msgs(f, "error"))
        self.assertIn("part of", errs); self.assertIn("has no evidence", errs)
        self.assertIn("acts upstream of or within", errs)

    def test_duplicate_evidence_line(self):
        ttl = PREFIXES + """
m:ev2 a owl:NamedIndividual, obo:ECO_0000314 ; dc:source "PMID:1" .
m:a obo:RO_0002629 m:b .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:ev , m:ev2 ] .
"""
        out, f = analyse(ttl, sparql=False)
        self.assertTrue(any("same evidence line more than once" in m for m in self.msgs(f, "minor")))

    def test_circular_with_on_the_enabler_and_comma_separated_with(self):
        ttl = PREFIXES + """
m:evs a owl:NamedIndividual, obo:ECO_0000250 ; dc:source "GO_REF:0000024" ; lego:evidence-with "UniProtKB:Q9,MGI:MGI:97490" .
m:a obo:RO_0002629 m:b .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:RO_0002629 ; owl:annotatedTarget m:b ; lego:evidence m:evs ] .
"""
        out, f = analyse(ttl, sparql=False)
        self.assertTrue(any("circular with/from" in m and "MGI:MGI:97490" in m for m in self.msgs(f)))
        self.assertIn("UniProtKB:Q9", out["with_values"])   # split, not one literal

    def test_iba_without_goref_and_single_activity(self):
        ttl = PREFIXES.replace("m:b a owl:NamedIndividual, obo:GO_0003674 .\n", "") + """
m:evb a owl:NamedIndividual, obo:ECO_0000318 ; dc:source "PMID:9" .
m:bp a owl:NamedIndividual, obo:GO_0007155 .
m:a obo:BFO_0000050 m:bp .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:BFO_0000050 ; owl:annotatedTarget m:bp ; lego:evidence m:evb ] .
"""
        out, f = analyse(ttl, sparql=False)
        w = " | ".join(self.msgs(f, "warning"))
        self.assertIn("IBA without GO_REF:0000033", w)
        self.assertIn("single-activity model", w)

    def test_title_and_comment_notes(self):
        ttl = PREFIXES.replace('dc:title "t"', 'dc:title "' + "x" * 130 + '" ; <http://www.w3.org/2000/01/rdf-schema#comment> "reviewer: please check Fig 3"')
        out, f = analyse(ttl, sparql=False)
        n = " | ".join(self.msgs(f, "note"))
        self.assertIn("130 characters", n); self.assertIn("model comment to read", n)

    def test_online_like_obsolete_subset_iep_and_mf_without_enabler(self):
        ttl = PREFIXES + """
m:k a owl:NamedIndividual, obo:GO_0004672 .
m:old a owl:NamedIndividual, obo:GO_0000001 .
m:cc a owl:NamedIndividual, obo:GO_0005634 .
m:bp a owl:NamedIndividual, obo:GO_0007155 .
m:eve a owl:NamedIndividual, obo:ECO_0000270 ; dc:source "PMID:5" .
m:a obo:BFO_0000066 m:cc .
m:a obo:BFO_0000050 m:bp .
m:k obo:BFO_0000050 m:old .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:BFO_0000066 ; owl:annotatedTarget m:cc ; lego:evidence m:eve ] .
[ a owl:Axiom ; owl:annotatedSource m:a ; owl:annotatedProperty obo:BFO_0000050 ; owl:annotatedTarget m:bp ; lego:evidence m:ev ] .
[ a owl:Axiom ; owl:annotatedSource m:k ; owl:annotatedProperty obo:BFO_0000050 ; owl:annotatedTarget m:old ; lego:evidence m:ev ] .
"""
        out, f = analyse_online_like(ttl)
        all_ = " | ".join(self.msgs(f))
        self.assertIn("GO:0000001 (old term) is obsolete", all_)
        self.assertIn("GO:0007155 (cell adhesion) is in gocheck_do_not_annotate", all_)
        self.assertIn("IEP on", all_); self.assertIn("cellular component", all_)
        self.assertTrue(any("activity k (GO:0004672) has no enabled_by" in m for m in self.msgs(f, "warning")), all_)  # found by MF namespace, not by enabler
        self.assertEqual(out["activity_count"], 3)


class SuppliedFileTests(unittest.TestCase):
    def test_a_turtle_file_is_copied_under_a_stamped_name(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(["bash", str(FETCH), str(TTL), d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("supplied file", r.stdout)
            self.assertTrue(list(Path(d).glob("supplied-*-ZFIN_ZDB-GENE-991207-22.ttl")))

    def test_a_non_turtle_file_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.txt"; p.write_text("Ontology(<x>)")
            r = subprocess.run(["bash", str(FETCH), str(p), d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("does not look like Turtle", r.stderr)


class QcTests(unittest.TestCase):
    def run_qc(self, *args):
        return subprocess.run([sys.executable, str(QC), *args], capture_output=True, text=True)

    def test_offline_report_on_a_production_model(self):
        with tempfile.TemporaryDirectory() as d:
            js = Path(d) / "qc.json"; md = Path(d) / "qc.md"
            r = self.run_qc(str(TTL), "--gpad", str(GPAD), "--offline", "--sparql-dir", str(FIX / "sparql"),
                            "--json", str(js), "--markdown", str(md))
            self.assertEqual(r.returncode, 0, r.stderr)
            out = json.loads(js.read_text())
            self.assertEqual(out["model"]["id"], "ZFIN_ZDB-GENE-991207-22")
            self.assertEqual(out["model"]["state"], "production")
            self.assertEqual(out["individual_count"], 42)
            self.assertEqual(out["activity_count"], 5)
            self.assertEqual(out["fact_count"], 16)
            self.assertEqual(out["evidence_count"], 16)
            self.assertEqual(out["causal_edges"], [])
            self.assertEqual(out["gpad"]["rows"], 10)
            self.assertEqual(out["gpad"]["model_states"], ["production"])
            sev = [f["severity"] for f in out["findings"]]
            self.assertNotIn("error", sev, out["findings"])
            msgs = " ".join(f["message"] for f in out["findings"])
            self.assertIn("no causal edge between activities", msgs)
            self.assertIn("check-disconnected-individuals.rq: clean", msgs)
            self.assertIn("check-multiply-reified-edges.rq: clean", msgs)
            self.assertIn("offline", msgs)
            text = md.read_text()
            self.assertIn("ZFIN:ZDB-GENE-991207-22", text)   # the enabler as a CURIE, not an identifiers.org IRI
            self.assertIn("read-only", text)

    def test_not_turtle(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.ttl"; p.write_text("<html>not a model</html>")
            self.assertEqual(self.run_qc(str(p), "--offline").returncode, 2)
        self.assertEqual(self.run_qc("/nonexistent.ttl").returncode, 2)


if __name__ == "__main__":
    unittest.main()
