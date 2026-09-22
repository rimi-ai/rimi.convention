#!/usr/bin/env python3
"""Tests for the translation-parity check.

Each test plants one kind of drift between the two texts and proves the check
sees it. The last one states, in code, what the check cannot see.

Run: python3 -m unittest discover -s tools -p 'test_*.py' -v
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import check_translation_parity as parity

REPO_ROOT = Path(__file__).resolve().parent.parent

ENGLISH = """# convention

| Id | Principle | Type · wave | Situation | Convention (summary) |
| --- | --- | --- | --- | --- |
| CONV-002 | P-01 | Invariant · 1 | Data absent | MUST say the data is missing. MUST NOT assert it. |
| CONV-003 | P-07 | Invariant · 1 | No result | MUST say so. SHOULD give the values. |

| Id | Novelty | Frameworks |
| --- | --- | --- |
| CONV-002 | Precise | OWASP |
| CONV-003 | New | — |
"""

FRENCH = """# convention

| Id | Principe | Type · lot | Situation | Convention (résumé) |
| --- | --- | --- | --- | --- |
| CONV-002 | P-01 | Invariant · 1 | Donnée absente | DOIT dire que la donnée manque. NE DOIT PAS l'affirmer. |
| CONV-003 | P-07 | Invariant · 1 | Aucun résultat | DOIT le dire. DEVRAIT donner les valeurs. |

| Id | Nouveauté | Cadres |
| --- | --- | --- |
| CONV-002 | Précise | OWASP |
| CONV-003 | Nouveau | — |
"""


class Parity(unittest.TestCase):
    def run_check(self, english: str, french: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            en = Path(directory) / "en.md"
            fr = Path(directory) / "fr.md"
            en.write_text(english, encoding="utf-8")
            fr.write_text(french, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = parity.check(en, fr)
            return code, output.getvalue()

    def test_two_texts_that_agree_pass(self):
        code, output = self.run_check(ENGLISH, FRENCH)
        self.assertEqual(0, code, output)

    def test_a_dropped_prohibition_is_caught(self):
        french = FRENCH.replace(" NE DOIT PAS l'affirmer.", "")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("MUST NOT: 1 vs 0", output)

    def test_a_prohibition_turned_into_an_obligation_is_caught(self):
        french = FRENCH.replace("NE DOIT PAS l'affirmer", "DOIT l'affirmer")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("CONV-002", output)

    def test_a_recommendation_hardened_into_an_obligation_is_caught(self):
        french = FRENCH.replace("DEVRAIT donner les valeurs", "DOIT donner les valeurs")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("SHOULD: 1 vs 0", output)

    def test_a_changed_principle_is_caught(self):
        french = FRENCH.replace("| CONV-003 | P-07 |", "| CONV-003 | P-05 |")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("principle", output)

    def test_a_rule_missing_from_one_text_is_caught(self):
        french = "\n".join(
            line for line in FRENCH.split("\n") if not line.startswith("| CONV-003 | P-07")
        )
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("CONV-003", output)

    def test_rules_listed_in_a_different_order_are_caught(self):
        french = FRENCH.replace("| CONV-002 | Précise | OWASP |\n| CONV-003 | Nouveau | — |",
                                "| CONV-003 | Nouveau | — |\n| CONV-002 | Précise | OWASP |")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(1, code)
        self.assertIn("same order", output)

    def test_plural_forms_count_as_their_singular(self):
        english = ENGLISH.replace("MUST say the data is missing.", "MUST say the data is missing.")
        french = FRENCH.replace("DOIT dire que la donnée manque.", "DOIVENT dire que la donnée manque.")
        code, output = self.run_check(english, french)
        self.assertEqual(0, code, output)

    def test_what_this_check_cannot_see(self):
        """Same shape, different statement: the check passes, and must not be trusted for meaning."""
        french = FRENCH.replace("Donnée absente", "Donnée présente")
        code, output = self.run_check(ENGLISH, french)
        self.assertEqual(0, code)
        self.assertIn("cannot see a difference of meaning", output)


class RuleBodies(unittest.TestCase):
    """The second fault of the follow-up review, September 2026.

    Until R30 this check read table rows only. A rule written out in full — its
    situation, its numbered obligations, its exceptions — was never compared, so
    one DOIT could become DEVRAIT inside CONV-001 in fr.md and the check stayed
    green. These tests plant that defect and require it to be seen.
    """

    def setUp(self):
        self.english = (REPO_ROOT / "en.md").read_text(encoding="utf-8")
        self.french = (REPO_ROOT / "fr.md").read_text(encoding="utf-8")

    def run_on(self, english: str, french: str):
        with tempfile.TemporaryDirectory() as workspace:
            en = Path(workspace) / "en.md"
            fr = Path(workspace) / "fr.md"
            en.write_text(english, encoding="utf-8")
            fr.write_text(french, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = parity.check(en, fr)
            return code, output.getvalue()

    def test_the_texts_as_they_stand_are_the_witness(self):
        code, output = self.run_on(self.english, self.french)
        self.assertEqual(0, code, output)
        self.assertIn("rule body", output)

    def test_an_obligation_weakened_in_a_rule_body_is_caught(self):
        french = self.french.replace(
            "Le LLM DOIT interpréter la réponse comme un choix de l'option 1.",
            "Le LLM DEVRAIT interpréter la réponse comme un choix de l'option 1.",
        )
        self.assertNotEqual(french, self.french, "the sentence to weaken was not found")
        code, output = self.run_on(self.english, french)
        self.assertEqual(1, code)
        self.assertIn("obligations differ in the rule's own body", output)
        self.assertIn("MUST: 5 vs 4", output)

    def test_an_obligation_dropped_from_a_rule_body_is_caught(self):
        french = self.french.replace(
            "3. Le LLM NE DOIT PAS reposer la même question.\n", "", 1
        )
        self.assertNotEqual(french, self.french)
        code, output = self.run_on(self.english, french)
        self.assertEqual(1, code)
        self.assertIn("MUST NOT", output)

    def test_a_rule_written_out_in_only_one_language_is_caught(self):
        english = self.english.replace(
            "## Part A — CONV-001, non-discriminating answer to an alternative",
            "## Part A — an answer that does not choose",
        )
        code, output = self.run_on(english, self.french)
        self.assertEqual(1, code)
        self.assertIn("written out in full", output)


class TheseTexts(unittest.TestCase):
    def test_the_published_texts_agree(self):
        code = parity.check(REPO_ROOT / "en.md", REPO_ROOT / "fr.md")
        self.assertEqual(0, code)


if __name__ == "__main__":
    unittest.main()
