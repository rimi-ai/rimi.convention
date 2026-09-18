#!/usr/bin/env python3
"""Check that fr.md still carries the same rules as en.md — structurally.

WHAT THIS CHECKS
  1. Every rule identifier occurs in both texts, the same number of times, in
     the same order — its own row, its row in the mapping table, every mention.
  2. Each rule's row declares the same principle (P-xx) in both texts.
  3. Each row states the same number of obligations of each level. English
     MUST / MUST NOT / SHOULD / SHOULD NOT / MAY are counted against French
     DOIT / NE DOIT PAS · PLUS · JAMAIS / DEVRAIT / NE DEVRAIT PAS / PEUT, in
     singular and plural.

WHAT THIS DOES NOT CHECK — AND NEVER WILL
  Meaning. Two sentences can pass every check above and say different things.
  A known example, still in the texts: the clause title "Until rules are
  accepted" against "Tant qu'aucune règle n'est acceptée" — same structure,
  different statement. This tool is a guard against structural drift between
  the two languages. It is not a guarantee that the translation is faithful,
  and it must never be presented as one. Only a human reading both texts can
  say that.

Usage:
    python3 tools/check_translation_parity.py [--en en.md] [--fr fr.md]
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EN = REPO_ROOT / "en.md"
DEFAULT_FR = REPO_ROOT / "fr.md"

RULE_RE = re.compile(r"\b(?:CONV|CONC|SOB)-\d{3}\b")
PRINCIPLE_RE = re.compile(r"\bP-\d{2}\b")

# English, longest first so that "MUST NOT" is never counted as "MUST".
ENGLISH_MODALS = [
    ("MUST NOT", re.compile(r"\bMUST NOT\b")),
    ("SHOULD NOT", re.compile(r"\bSHOULD NOT\b")),
    ("MUST", re.compile(r"\bMUST\b")),
    ("SHOULD", re.compile(r"\bSHOULD\b")),
    ("MAY", re.compile(r"\bMAY\b")),
]

# French negations are consumed first: "NE DOIT PAS" must not leave a "DOIT".
FRENCH_MODALS = [
    ("MUST NOT", re.compile(r"\bNE\s+(?:DOIT|DOIVENT)\s+(?:PAS|PLUS|JAMAIS)\b")),
    ("SHOULD NOT", re.compile(r"\bNE\s+(?:DEVRAIT|DEVRAIENT)\s+(?:PAS|PLUS|JAMAIS)\b")),
    ("MUST", re.compile(r"\b(?:DOIT|DOIVENT)\b")),
    ("SHOULD", re.compile(r"\b(?:DEVRAIT|DEVRAIENT)\b")),
    ("MAY", re.compile(r"\b(?:PEUT|PEUVENT)\b")),
]


def count_modals(text: str, modals) -> Counter:
    """Count obligations by level, consuming each match so none is counted twice."""
    counts: Counter = Counter()
    remaining = text
    for level, pattern in modals:
        found = pattern.findall(remaining)
        if found:
            counts[level] += len(found)
            remaining = pattern.sub(" ", remaining)
    return counts


def occurrences(text: str) -> list[tuple[str, int]]:
    """Every rule identifier in document order, with its line number."""
    found = []
    for number, line in enumerate(text.split("\n"), 1):
        for match in RULE_RE.finditer(line):
            found.append((match.group(0), number))
    return found


def rule_rows(text: str) -> dict[str, list[tuple[int, str]]]:
    """Table rows that define or list a rule, keyed by identifier, in order."""
    rows: dict[str, list[tuple[int, str]]] = {}
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        match = RULE_RE.fullmatch(cells[0])
        if match:
            rows.setdefault(match.group(0), []).append((number, stripped))
    return rows


def check(en_path: Path, fr_path: Path) -> int:
    english = en_path.read_text(encoding="utf-8")
    french = fr_path.read_text(encoding="utf-8")
    problems: list[str] = []

    # 1. Same identifiers, same number of occurrences, same order.
    en_occurrences = occurrences(english)
    fr_occurrences = occurrences(french)
    for index, ((en_id, en_line), (fr_id, fr_line)) in enumerate(
        zip(en_occurrences, fr_occurrences), 1
    ):
        if en_id != fr_id:
            problems.append(
                f"occurrence {index} of a rule identifier differs:\n"
                f"    {en_path.name}:{en_line} {en_id}\n"
                f"    {fr_path.name}:{fr_line} {fr_id}\n"
                f"    The two texts stopped following the same order here."
            )
            break
    if len(en_occurrences) != len(fr_occurrences):
        problems.append(
            f"{len(en_occurrences)} rule mentions in {en_path.name}, "
            f"{len(fr_occurrences)} in {fr_path.name}: one text mentions a rule "
            f"the other does not."
        )

    # 2 and 3. Row by row: same principle, same obligations.
    en_rows = rule_rows(english)
    fr_rows = rule_rows(french)

    for rule in sorted(set(en_rows) | set(fr_rows)):
        english_rows = en_rows.get(rule, [])
        french_rows = fr_rows.get(rule, [])
        if len(english_rows) != len(french_rows):
            problems.append(
                f"{rule}: {len(english_rows)} row(s) in {en_path.name}, "
                f"{len(french_rows)} in {fr_path.name}."
            )
            continue

        for (en_line, en_row), (fr_line, fr_row) in zip(english_rows, french_rows):
            en_principles = PRINCIPLE_RE.findall(en_row)
            fr_principles = PRINCIPLE_RE.findall(fr_row)
            if en_principles != fr_principles:
                problems.append(
                    f"{rule}: principle {en_principles or '—'} in {en_path.name}:{en_line}, "
                    f"{fr_principles or '—'} in {fr_path.name}:{fr_line}."
                )

            en_modals = count_modals(en_row, ENGLISH_MODALS)
            fr_modals = count_modals(fr_row, FRENCH_MODALS)
            if en_modals != fr_modals:
                detail = ", ".join(
                    f"{level}: {en_modals.get(level, 0)} vs {fr_modals.get(level, 0)}"
                    for level in ("MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY")
                    if en_modals.get(level, 0) != fr_modals.get(level, 0)
                )
                problems.append(
                    f"{rule}: obligations differ between "
                    f"{en_path.name}:{en_line} and {fr_path.name}:{fr_line} — {detail}."
                )

    if problems:
        print(f"{len(problems)} divergence(s) between {en_path.name} and {fr_path.name}:\n")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nThe reference text is en.md. Bring fr.md back in line with it, "
            "or fix en.md if the fault is there."
        )
        return 1

    rules = len(set(en_rows) | set(fr_rows))
    print(
        f"{en_path.name} and {fr_path.name} agree structurally: "
        f"{len(en_occurrences)} rule mentions in the same order, "
        f"{rules} rules with the same principle and the same obligations."
    )
    print(
        "Structure only: this check cannot see a difference of meaning between "
        "two sentences that have the same shape."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--en", type=Path, default=DEFAULT_EN)
    parser.add_argument("--fr", type=Path, default=DEFAULT_FR)
    args = parser.parse_args(argv)
    return check(args.en, args.fr)


if __name__ == "__main__":
    raise SystemExit(main())
