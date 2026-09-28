"""Offline regression tests: real Git checkouts in a scratch HOME, stub tooling.

Run with: python3 -m unittest discover -s tests -v
"""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


BOOTSTRAP = Path(__file__).resolve().parents[1] / "skills/gene-review/scripts/bootstrap.sh"
REVIEW = "genes/human/UPP1/UPP1-ai-review.yaml"
HISTORY = "history/genes/human/UPP1/event.yaml"


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="gene-review-test-")
        self.addCleanup(scratch.cleanup)
        self.home = Path(scratch.name)
        self.repo = self.home / "ai-gene-review"
        self.repo.mkdir()
        bin_dir = self.home / ".local/bin"
        bin_dir.mkdir(parents=True)
        for tool in ("uv", "just"):
            executable = bin_dir / tool
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "AIGR_HOME": str(self.repo),
            "AIGR_NO_UPDATE": "1",
            "AIGR_FULL": "0",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Bootstrap test")
        self.git("config", "commit.gpgsign", "false")
        for name in (
            "justfile", "src/tool.py", "genes/DANRE/shha/shha-ai-review.yaml",
            "genes/human/SHH/SHH-ai-review.yaml", REVIEW, HISTORY,
            "genes/BLOCKED",  # A file cannot be selected as a directory cone.
        ):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"committed content: {name}\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture")
        self.original = (self.repo / REVIEW).read_bytes()
        self.git("sparse-checkout", "set", "--cone", "src", "genes/DANRE")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], env=self.env,
            text=True, capture_output=True, check=True,
        ).stdout.strip()

    def bootstrap(self, organisms="", *, succeeds=True):
        result = subprocess.run(
            ["bash", str(BOOTSTRAP)], cwd=self.home,
            env={**self.env, "AIGR_ORGANISMS": organisms},
            text=True, capture_output=True,
        )
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def organisms(self, output):
        return next(line.split(":", 1)[1].split() for line in output.splitlines()
                    if line.strip().startswith("organisms:"))

    def test_partial_organism_is_not_reported_as_complete(self):
        self.git("sparse-checkout", "add", "genes/human/SHH")
        self.assertTrue((self.repo / "genes/human").is_dir())
        self.assertFalse((self.repo / REVIEW).exists())
        self.assertEqual(self.organisms(self.bootstrap().stdout), ["DANRE"])

    def test_partial_organism_hydrates_review_and_history(self):
        self.git("sparse-checkout", "add", "genes/human/SHH")
        self.git("cat-file", "-e", f"HEAD:{REVIEW}")
        self.assertFalse((self.repo / REVIEW).exists())
        result = self.bootstrap("human")
        self.assertEqual((self.repo / REVIEW).read_bytes(), self.original)
        self.assertTrue((self.repo / HISTORY).is_file())
        self.assertEqual(self.organisms(result.stdout), ["DANRE", "human"])
        self.assertEqual(self.git("status", "--porcelain"), "")
        # Repeated bootstrap must retain curator edits, not restore HEAD.
        edited = self.original + b"curator changes\n"
        (self.repo / REVIEW).write_bytes(edited)
        self.bootstrap("DANRE human")
        self.assertEqual((self.repo / REVIEW).read_bytes(), edited)

    def test_existing_gene_cone_also_gets_history(self):
        self.git("sparse-checkout", "add", "genes/human")
        self.assertFalse((self.repo / HISTORY).exists())
        self.bootstrap("human")
        self.assertTrue((self.repo / HISTORY).is_file())

    def test_new_organism_can_be_selected(self):
        result = self.bootstrap("NEWORG")
        self.assertIn("NEWORG", self.organisms(result.stdout))
        self.assertIn("genes/NEWORG", self.git("sparse-checkout", "list").splitlines())

    def test_failed_hydration_stops_bootstrap(self):
        result = self.bootstrap("BLOCKED", succeeds=False)
        self.assertIn("could not hydrate genes/BLOCKED", result.stderr)
        self.assertNotIn("ai-gene-review is ready", result.stdout)

    def test_full_checkout_reports_organism_directories(self):
        self.git("sparse-checkout", "disable")
        result = self.bootstrap("human")
        self.assertEqual(self.organisms(result.stdout), ["DANRE", "human"])
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_whole_genes_cone_reports_all(self):
        self.git("sparse-checkout", "set", "src", "genes")
        self.assertEqual(self.organisms(self.bootstrap().stdout), ["(all", "organisms)"])

    def test_no_organisms_reports_none(self):
        self.git("sparse-checkout", "set", "src")
        self.assertEqual(self.organisms(self.bootstrap().stdout), ["none"])


if __name__ == "__main__":
    unittest.main()
