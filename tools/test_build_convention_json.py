#!/usr/bin/env python3
"""Tests for the projection of en.md into convention.json.

Run: python3 -m unittest discover -s tools -p 'test_*.py' -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
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
