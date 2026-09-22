#!/usr/bin/env python3
"""Tests for the projection of en.md into convention.json.

Run: python3 -m unittest discover -s tools -p 'test_*.py' -v
"""

from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import build_convention_json as build_module

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "en.md"
COMMITTED = REPO_ROOT / "convention.json"
SCHEMA = REPO_ROOT / "schemas" / "convention.schema.json"

A_TIME = "2026-01-01T00:00:00Z"
ANOTHER_TIME = "2030-12-31T23:59:59Z"


class Determinism(unittest.TestCase):
    def test_same_text_gives_the_same_bytes(self):
        first = build_module.serialise(build_module.build(SOURCE, A_TIME))
        second = build_module.serialise(build_module.build(SOURCE, A_TIME))
        self.assertEqual(first, second)

    def test_only_generated_at_depends_on_the_run(self):
        early = build_module.build(SOURCE, A_TIME)
        late = build_module.build(SOURCE, ANOTHER_TIME)
        self.assertNotEqual(early["generated_at"], late["generated_at"])
        self.assertEqual(
            build_module.serialise(build_module.body_of(early)),
            build_module.serialise(build_module.body_of(late)),
        )

    def test_the_committed_file_is_the_projection_of_the_text(self):
        self.assertEqual(0, build_module.main(["--check"]))

    def test_a_build_elsewhere_leaves_the_published_files_alone(self):
        frozen = build_module.frozen_path(build_module.build(SOURCE, A_TIME))
        before = [path.read_bytes() for path in (COMMITTED, frozen)]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "convention.json"
            self.assertEqual(0, build_module.main(["--output", str(output)]))
            self.assertTrue(output.exists())
            self.assertEqual(2, build_module.main(["--output", str(output), "--freeze"]))
        self.assertEqual(before, [path.read_bytes() for path in (COMMITTED, frozen)])


class Shape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = build_module.build(SOURCE, A_TIME)
        cls.rules = cls.document["rules"]

    def test_identifiers_are_unique(self):
        identifiers = [rule["id"] for rule in self.rules]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_rules_are_ordered_by_part_then_number(self):
        keys = [
            (build_module.PART_ORDER[rule["part"]], int(rule["id"].split("-")[1]))
            for rule in self.rules
        ]
        self.assertEqual(keys, sorted(keys))

    def test_every_rule_carries_what_a_test_runner_needs(self):
        for rule in self.rules:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["part"], ("A", "B", "C"))
                self.assertIn(rule["status"], ("Draft", "Proposed", "Accepted", "Stable", "Retired"))
                self.assertIsInstance(rule["wave"], int)
                self.assertRegex(rule["principle"], r"^P-\d{2}$")
                self.assertTrue(rule["summary"])
                self.assertTrue(rule["obligations"])
                self.assertRegex(rule["rule_sha256"], r"^[0-9a-f]{64}$")
                for obligation in rule["obligations"]:
                    self.assertIn(obligation["level"], build_module.OBLIGATION_LEVELS)
                    self.assertIn(obligation["level"], obligation["text"])

    def test_only_parts_a_and_b_carry_a_type(self):
        for rule in self.rules:
            with self.subTest(rule=rule["id"]):
                if rule["part"] == "C":
                    self.assertIsNone(rule["type"])
                else:
                    self.assertIn(rule["type"], set(build_module.TYPE_LABELS.values()))

    def test_fingerprints_follow_the_text(self):
        self.assertEqual(
            self.document["text_sha256"],
            build_module.hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        )
        fingerprints = {rule["rule_sha256"] for rule in self.rules}
        self.assertEqual(len(fingerprints), len(self.rules))

    def test_thresholds_and_levels_come_from_the_protocol(self):
        thresholds = self.document["thresholds"]
        self.assertGreater(thresholds["must_pass_rate"], thresholds["should_pass_rate"])
        self.assertEqual(
            ["A", "AA", "AAA"], [level["id"] for level in self.document["levels"]["conformance"]]
        )
        self.assertEqual(
            ["S1", "S2", "S3"], [level["id"] for level in self.document["levels"]["frugality"]]
        )


class Guards(unittest.TestCase):
    """The build fails loudly rather than producing a projection that lies."""

    def build_from(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "en.md"
            source.write_text(text, encoding="utf-8")
            return build_module.build(source, A_TIME)

    def test_a_wave_stated_twice_must_agree(self):
        text = SOURCE.read_text(encoding="utf-8").replace(
            "| CONV-002 | P-01 | Invariant · 1 |", "| CONV-002 | P-01 | Invariant · 3 |"
        )
        with self.assertRaises(build_module.SourceError) as error:
            self.build_from(text)
        self.assertIn("CONV-002", str(error.exception))

    def test_a_rule_missing_from_the_counts_is_caught(self):
        text = SOURCE.read_text(encoding="utf-8").replace(
            "| A — LLM behaviour | The LLM during the conversation | CONV | 35 (1 proposed, 34 draft) |",
            "| A — LLM behaviour | The LLM during the conversation | CONV | 34 (1 proposed, 33 draft) |",
        )
        with self.assertRaises(build_module.SourceError) as error:
            self.build_from(text)
        self.assertIn("Part A", str(error.exception))

    def test_an_unknown_rule_type_is_refused(self):
        text = SOURCE.read_text(encoding="utf-8").replace(
            "| CONV-003 | P-07 | Invariant · 1 |", "| CONV-003 | P-07 | Guideline · 1 |"
        )
        with self.assertRaises(build_module.SourceError):
            self.build_from(text)


class Schema(unittest.TestCase):
    def test_the_generated_file_validates(self):
        try:
            import jsonschema
        except ImportError:  # pragma: no cover - the CI installs it
            self.skipTest("jsonschema is not installed")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(json.loads(COMMITTED.read_text(encoding="utf-8")), schema)


class Obligations(unittest.TestCase):
    def test_a_sentence_can_hold_several_obligations(self):
        obligations = build_module.split_obligations(
            "The system MUST answer; MUST NOT invent the answer. It SHOULD say where it looked."
        )
        self.assertEqual(
            [("MUST", "The system MUST answer"),
             ("MUST NOT", "MUST NOT invent the answer."),
             ("SHOULD", "It SHOULD say where it looked.")],
            [(o["level"], o["text"]) for o in obligations],
        )

    def test_a_sentence_without_a_modal_states_no_obligation(self):
        self.assertEqual([], build_module.split_obligations("This paragraph explains the rule."))


if __name__ == "__main__":
    unittest.main()


# Read from the text, never hard-coded: a test that bakes in the current version
# tests the version, not the tool, and breaks the day the version is raised.
VERSION = re.search(r"^Version (\d+\.\d+\.\d+)", SOURCE.read_text(encoding="utf-8"), re.M).group(1)
TAG = f"v{VERSION}"


class FrozenCopyDiscipline(unittest.TestCase):
    """A file published with a release is never rewritten by a later build.

    Each test plants the situation in a throwaway git repository whose only tag
    is the version the text declares, then exercises the tool against it.
    """

    def setUp(self):
        import shutil
        import subprocess
        from unittest.mock import patch

        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        shutil.copy(SOURCE, self.repo / "en.md")
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("add", "en.md")
        self.git(
            "-c", "user.email=test@example.invalid", "-c", "user.name=test",
            "commit", "--quiet", "-m", "text",
        )
        self.git("tag", TAG)  # the version this text declares: it is released

        for name, value in (
            ("REPO_ROOT", self.repo),
            ("DEFAULT_SOURCE", self.repo / "en.md"),
            ("DEFAULT_OUTPUT", self.repo / "convention.json"),
            ("VERSIONS_DIR", self.repo / "versions"),
        ):
            patcher = patch.object(build_module, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

        self.frozen = self.repo / "versions" / TAG / "convention.json"

    def git(self, *arguments: str):
        import subprocess

        subprocess.run(
            ["git", "-C", str(self.repo), *arguments], check=True, capture_output=True
        )

    def run_tool(self, *arguments: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = build_module.main(list(arguments))
        return code, output.getvalue()

    def freeze_from_tag(self):
        """Write the frozen copy the way a repair does: from the text at the tag."""
        self.frozen.parent.mkdir(parents=True, exist_ok=True)
        code, _ = self.run_tool("--source", str(self.repo / "en.md"), "--output", str(self.frozen))
        self.assertEqual(0, code)
        return self.frozen.read_bytes()

    def test_an_ordinary_build_never_writes_a_frozen_copy(self):
        published = self.freeze_from_tag()
        code, output = self.run_tool()
        self.assertEqual(0, code)
        self.assertEqual(published, self.frozen.read_bytes())
        self.assertNotIn(str(self.frozen), output)

    def test_an_ordinary_build_leaves_even_a_corrupted_copy_alone(self):
        self.frozen.parent.mkdir(parents=True, exist_ok=True)
        self.frozen.write_text("{}", encoding="utf-8")
        self.run_tool()
        self.assertEqual("{}", self.frozen.read_text(encoding="utf-8"))

    def test_freeze_refuses_to_overwrite_a_released_version(self):
        published = self.freeze_from_tag()
        code, output = self.run_tool("--freeze")
        self.assertEqual(2, code)
        self.assertIn("already released", output)
        self.assertIn(f"gh release download {TAG}", output)
        self.assertIn("shallow clone it protects nothing", output)
        self.assertEqual(published, self.frozen.read_bytes())

    def test_force_overrides_the_refusal_for_a_repair(self):
        self.frozen.parent.mkdir(parents=True, exist_ok=True)
        self.frozen.write_text("{}", encoding="utf-8")
        code, _ = self.run_tool("--freeze", "--force")
        self.assertEqual(0, code)
        self.assertEqual(VERSION, json.loads(self.frozen.read_text(encoding="utf-8"))["convention_version"])

    def test_check_agrees_with_the_tag_check_after_a_correct_repair(self):
        """The fault R11 demonstrated: after the right repair, both checks say the same thing."""
        import check_frozen_versions

        self.freeze_from_tag()  # the copy as published at the tag
        source = self.repo / "en.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "MUST say the data is missing or not established.",
                "MUST say the data is missing or not established, or estimate it.",
            ),
            encoding="utf-8",
        )
        self.run_tool()  # ordinary build: root only

        code, output = self.run_tool("--check")
        self.assertEqual(0, code, output)
        self.assertIn("raise the version number", output)
        self.assertNotIn("--freeze", output)

        tag_output = io.StringIO()
        with redirect_stdout(tag_output):
            tag_code = check_frozen_versions.check(self.repo)
        self.assertEqual(0, tag_code, tag_output.getvalue())

    def test_check_still_requires_the_copy_of_an_unreleased_version(self):
        source = self.repo / "en.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace(f"Version {VERSION} ·", "Version 9.9.9 ·", 1),
            encoding="utf-8",
        )
        self.run_tool()

        code, output = self.run_tool("--check")
        self.assertEqual(1, code)
        self.assertIn("is missing", output)
        self.assertIn("--freeze", output)

        self.assertEqual(0, self.run_tool("--freeze")[0])  # unreleased: allowed
        self.assertEqual(0, self.run_tool("--check")[0])
