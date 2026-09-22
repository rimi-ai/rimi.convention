#!/usr/bin/env python3
"""Tests for the frozen-copy check.

Each test plants the fault it is meant to catch, in a throwaway git repository,
and proves the check sees it. The first one is the fault that was demonstrated
on a clone of this repository: en.md edited without the version being raised,
an ordinary build rewriting the published copy, every other check still green.

Run: python3 -m unittest discover -s tools -p 'test_*.py' -v
"""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import check_frozen_versions as checker

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDER = REPO_ROOT / "tools" / "build_convention_json.py"

# The tag's text has to be text the builder can project: since R30 the check
# rebuilds it and compares the result, so a placeholder would prove nothing.
TAG = "v0.3.0"
TEXT_AT_TAG = (REPO_ROOT / "en.md").read_text(encoding="utf-8")
TEXT_AFTER = TEXT_AT_TAG.replace(
    "These thirty-four rules come from drifts observed in production",
    "These thirty-four rules come from drifts observed in production, quietly reworded",
)


def build(text: str) -> dict:
    """Project a text with this repository's builder, as the check itself does."""
    with tempfile.TemporaryDirectory() as workspace:
        source = Path(workspace) / "en.md"
        source.write_text(text, encoding="utf-8")
        output = Path(workspace) / "convention.json"
        subprocess.run(
            ["python3", str(BUILDER), "--source", str(source), "--output", str(output)],
            check=True, capture_output=True,
        )
        return json.loads(output.read_text(encoding="utf-8"))


def frozen_document(text: str, version: str = "0.3.0") -> str:
    document = build(text)
    document["convention_version"] = version
    assert document["text_sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    return json.dumps(document, indent=2, ensure_ascii=False)


class FrozenCopies(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.repo = Path(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.git("init", "--quiet", "--initial-branch=main")
        (self.repo / "en.md").write_text(TEXT_AT_TAG, encoding="utf-8")
        self.git("add", "en.md")
        self.git(
            "-c", "user.email=test@example.invalid", "-c", "user.name=test",
            "commit", "--quiet", "-m", "text",
        )
        self.git("tag", TAG)

    def git(self, *arguments: str):
        subprocess.run(
            ["git", "-C", str(self.repo), *arguments], check=True, capture_output=True
        )

    def freeze(self, text: str, version: str = "0.3.0", tag: str = TAG):
        path = self.repo / "versions" / tag / "convention.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(frozen_document(text, version), encoding="utf-8")
        return path

    def run_check(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = checker.check(self.repo)
        return code, output.getvalue()

    def test_a_frozen_copy_that_matches_its_tag_passes(self):
        self.freeze(TEXT_AT_TAG)
        code, output = self.run_check()
        self.assertEqual(0, code, output)

    def test_the_demonstrated_fault_is_caught(self):
        """en.md edited without a version bump, the frozen copy rewritten."""
        self.freeze(TEXT_AT_TAG)
        (self.repo / "en.md").write_text(TEXT_AFTER, encoding="utf-8")
        self.freeze(TEXT_AFTER)  # what an ordinary build does today
        code, output = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("no longer projects the text published at v0.3.0", output)
        self.assertIn("gh release download", output)  # the repair is spelled out

    def test_an_obligation_edited_inside_the_frozen_copy_is_caught(self):
        """The second half of the fault, found in a follow-up review, September 2026.

        The fingerprint answers for the text, and the text has not moved: an
        obligation turned from MUST into SHOULD inside the published file left
        text_sha256 intact, and the check passed. Only rebuilding the projection
        and comparing it field by field sees this.
        """
        path = self.freeze(TEXT_AT_TAG)
        document = json.loads(path.read_text(encoding="utf-8"))
        rule = next(r for r in document["rules"] if r["id"] == "CONV-002")
        self.assertEqual("MUST", rule["obligations"][0]["level"])
        rule["obligations"][0]["level"] = "SHOULD"
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")

        # The fingerprint still matches — which is exactly why it was not enough.
        self.assertEqual(
            hashlib.sha256(TEXT_AT_TAG.encode("utf-8")).hexdigest(),
            json.loads(path.read_text(encoding="utf-8"))["text_sha256"],
        )

        code, output = self.run_check()
        self.assertEqual(1, code, output)
        self.assertIn("is not what the text at v0.3.0 projects", output)
        self.assertIn("obligations[0].level: rebuilt 'MUST', frozen copy 'SHOULD'", output)

    def test_a_rule_dropped_from_the_frozen_copy_is_caught(self):
        path = self.freeze(TEXT_AT_TAG)
        document = json.loads(path.read_text(encoding="utf-8"))
        document["rules"] = [r for r in document["rules"] if r["id"] != "CONV-002"]
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
        code, output = self.run_check()
        self.assertEqual(1, code, output)
        self.assertIn("entries rebuilt", output)

    def test_a_version_that_contradicts_its_folder_is_caught(self):
        self.freeze(TEXT_AT_TAG, version="0.3.1")
        code, output = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("inside a folder named", output)

    def test_a_frozen_copy_without_a_tag_is_caught(self):
        self.freeze(TEXT_AT_TAG, tag="v1.2.3")
        code, output = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("belongs to no release", output)

    def test_unreadable_json_is_caught(self):
        path = self.freeze(TEXT_AT_TAG)
        path.write_text("{ not json", encoding="utf-8")
        code, output = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("cannot be read as JSON", output)

    def test_a_release_without_a_frozen_copy_is_reported_not_failed(self):
        self.git("tag", "v0.0.1")
        self.freeze(TEXT_AT_TAG)
        code, output = self.run_check()
        self.assertEqual(0, code, output)
        self.assertIn("release v0.0.1 has no frozen copy", output)

    def test_without_tags_the_check_refuses_to_conclude(self):
        self.git("tag", "-d", TAG)
        self.freeze(TEXT_AT_TAG)
        code, output = self.run_check()
        self.assertEqual(2, code)
        self.assertIn("fetch-depth", output)


class ThisRepository(unittest.TestCase):
    def test_the_published_copies_still_match_their_tags(self):
        repository = Path(__file__).resolve().parent.parent
        if not (repository / ".git").exists():  # pragma: no cover - source checkout only
            self.skipTest("not a git checkout")
        output = io.StringIO()
        with redirect_stdout(output):
            code = checker.check(repository)
        self.assertIn(code, (0, 2), output.getvalue())  # 2 = tags not fetched


if __name__ == "__main__":
    unittest.main()
