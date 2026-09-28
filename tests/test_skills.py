"""Agent Skills reference validation plus the rules in CLAUDE.md."""

from pathlib import Path
import tempfile
import unittest

from skills_ref.errors import ParseError
from skills_ref.parser import parse_frontmatter
from skills_ref.validator import validate_metadata


SKILLS = Path(__file__).resolve().parents[1] / "skills"


def validate_skill(skill_dir):
    try:
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)
    except (OSError, ParseError) as error:
        return [str(error)]

    errors = []
    # This is the sole Claude Code extension permitted by CLAUDE.md.
    # Parse the original YAML first so malformed or duplicate fields still fail.
    if "argument-hint" in frontmatter:
        if not isinstance(frontmatter.pop("argument-hint"), str):
            errors.append("argument-hint must be a string")
    errors.extend(validate_metadata(frontmatter, skill_dir))

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be a mapping containing version and source")
    else:
        for field in ("version", "source"):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                errors.append(f"metadata.{field} must be a non-empty string")
    if len(content.splitlines()) >= 500:
        errors.append("SKILL.md must be under 500 lines; move detail to references/")
    return errors


class SkillValidationTests(unittest.TestCase):
    def test_repository_skills(self):
        directories = sorted(path for path in SKILLS.iterdir() if path.is_dir())
        self.assertTrue(directories, "No skill directories found")
        for directory in directories:
            with self.subTest(skill=directory.name):
                self.assertEqual(validate_skill(directory), [])

    def test_validator_accepts_permitted_extension(self):
        for extra in ('', 'argument-hint: "[GENE]"\n'):
            with self.subTest(extra=extra):
                self.assertEqual(self.validate_fixture(extra=extra), [])

    def test_validator_rejects_invalid_skills(self):
        cases = {
            "malformed YAML": {"extra": 'license: "unterminated\n'},
            "duplicate field": {"extra": 'name: sample\n'},
            "missing description": {"description": ''},
            "long description": {"description": 'description: ' + 'x' * 1025 + '\n'},
            "directory mismatch": {"name": 'other'},
            "invalid name": {"name": 'Sample'},
            "unknown field": {"extra": 'unexpected: value\n'},
            "misplaced version": {"extra": 'version: "1.0"\n'},
            "long compatibility": {"extra": 'compatibility: ' + 'x' * 501 + '\n'},
            "invalid extension": {"extra": 'argument-hint:\n  nested: value\n'},
            "missing source": {"metadata": 'metadata:\n  version: "1.0"\n'},
            "invalid metadata": {"metadata": 'metadata: invalid\n'},
            "too many lines": {"body": '# Sample\n' * 500},
            "unclosed frontmatter": {"closing": ''},
        }
        for label, kwargs in cases.items():
            with self.subTest(case=label):
                self.assertTrue(self.validate_fixture(**kwargs), label)

    def validate_fixture(
        self, *, name="sample", description="description: A sample skill.\n",
        metadata='metadata:\n  version: "1.0"\n  source: https://example.org/sample\n',
        extra="", closing="---\n", body="# Sample\n",
    ):
        with tempfile.TemporaryDirectory(prefix="skill-validation-") as scratch:
            directory = Path(scratch) / "sample"
            directory.mkdir()
            (directory / "SKILL.md").write_text(
                f"---\nname: {name}\n{description}{metadata}{extra}{closing}{body}",
                encoding="utf-8",
            )
            return validate_skill(directory)


if __name__ == "__main__":
    unittest.main()
