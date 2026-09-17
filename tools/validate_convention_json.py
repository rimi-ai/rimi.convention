#!/usr/bin/env python3
"""Validate convention.json, and every frozen copy, against the schema.

Usage:
    python3 tools/validate_convention_json.py [files...]

With no argument, validates convention.json and versions/*/convention.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "schemas" / "convention.schema.json"


def default_targets() -> list[Path]:
    return [REPO_ROOT / "convention.json", *sorted(REPO_ROOT.glob("versions/*/convention.json"))]


def main(argv: list[str]) -> int:
    try:
        import jsonschema
    except ImportError:
        print("jsonschema is not installed: pip install jsonschema", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    targets = [Path(argument) for argument in argv] or default_targets()
    if not targets:
        print("nothing to validate", file=sys.stderr)
        return 2

    failures = 0
    for path in targets:
        try:
            jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), schema)
        except jsonschema.ValidationError as error:
            location = "/".join(str(part) for part in error.absolute_path) or "(root)"
            print(f"{path}: invalid at {location}: {error.message}", file=sys.stderr)
            failures += 1
        else:
            print(f"{path}: valid")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
