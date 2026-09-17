#!/usr/bin/env python3
"""Check that the published URLs serve the file this repository holds.

GitHub Pages rebuilds a few moments after a push, so each URL is retried before
being declared missing. The comparison ignores generated_at, the only field that
depends on the run that produced the file.

Usage:
    python3 tools/check_published.py --file convention.json --url https://... [--url ...]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def body(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "generated_at"}


def fetch(url: str, timeout: float) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 - fixed https URL
        return json.loads(response.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--url", action="append", required=True)
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--delay", type=float, default=30.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    expected = body(json.loads(args.file.read_text(encoding="utf-8")))
    failures = 0

    for url in args.url:
        for attempt in range(1, args.attempts + 1):
            try:
                served = body(fetch(url, args.timeout))
            except (urllib.error.URLError, ValueError) as error:
                reason = f"not served yet ({error})"
            else:
                if served == expected:
                    print(f"{url}: serves this version")
                    break
                reason = "serves an older version"
            if attempt == args.attempts:
                print(f"{url}: {reason}", file=sys.stderr)
                failures += 1
                break
            print(f"{url}: {reason}, retrying in {args.delay:.0f}s ({attempt}/{args.attempts})")
            time.sleep(args.delay)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
