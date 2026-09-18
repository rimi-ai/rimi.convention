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

TAG = "v9.9.9"
TEXT_AT_TAG = "# convention\n\nVersion 9.9.9 · text as published\n"
TEXT_AFTER = "# convention\n\nVersion 9.9.9 · text quietly changed\n"


def frozen_document(text: str, version: str = "9.9.9") -> str:
    return json.dumps(
        {
            "convention_version": version,
            "generated_at": "2026-01-01T00:00:00Z",
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "rules": [],
        },
        indent=2,
    )


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

    def freeze(self, text: str, version: str = "9.9.9", tag: str = TAG):
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
        self.assertIn("no longer projects the text published at v9.9.9", output)
        self.assertIn("gh release download", output)  # the repair is spelled out

    def test_a_version_that_contradicts_its_folder_is_caught(self):
        self.freeze(TEXT_AT_TAG, version="9.9.8")
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
