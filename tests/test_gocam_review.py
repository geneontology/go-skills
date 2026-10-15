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

    def test_dev_environment(self):
        r = self.dry("gomodel:5b91dbd100002057", "dev")
        self.assertIn("http://noctua-dev.berkeleybop.org", r.stdout)

    def test_bad_input(self):
        self.assertEqual(self.dry("not a model id!").returncode, 2)
        self.assertEqual(self.dry("gomodel:x", "staging").returncode, 2)
        self.assertEqual(subprocess.run(["bash", str(FETCH)], capture_output=True).returncode, 2)


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
