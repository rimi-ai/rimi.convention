#!/usr/bin/env python3
"""Build convention.json, the machine-readable projection of the convention.

The normative source is en.md. This script never invents content: every field
is read from the text. When the text changes shape, the script fails loudly
rather than guessing, so that the projection can never drift from the text.

Usage:
    python3 tools/build_convention_json.py                 # write convention.json
    python3 tools/build_convention_json.py --check         # fail if the file is stale
    python3 tools/build_convention_json.py --freeze        # also write versions/v<x>/convention.json

Determinism: the same en.md always produces the same bytes. `generated_at` is
the only field that depends on the run; it is kept apart and excluded from
every comparison and from text_sha256.

A published copy is never rewritten. `versions/v<x.y.z>/convention.json` is the
file that went out with release v<x.y.z>, so:

  * an ordinary build writes convention.json and nothing else — it never touches
    versions/, whatever is already there;
  * `--freeze` writes the frozen copy, and refuses when that version is already
    tagged (`--force` overrides, for repairing a copy that was corrupted);
  * `--check` compares the frozen copy against the current text only while that
    version is unreleased. Once it is tagged, its copy answers to its tag, and
    tools/check_frozen_versions.py is what checks it.

The refusal in `--freeze` reads the repository's tags: in a shallow clone there
are none, and the refusal silently stops protecting anything. It is a
convenience, not the guarantee. The guarantee is check_frozen_versions.py in CI.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from check_frozen_versions import released_tags, text_at_tag

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "en.md"
DEFAULT_OUTPUT = REPO_ROOT / "convention.json"
VERSIONS_DIR = REPO_ROOT / "versions"

PART_ORDER = {"A": 0, "B": 1, "C": 2}

TYPE_LABELS = {
    "invariant": "invariant",
    "convention": "default_convention",
    "default convention": "default_convention",
    "informative": "informative",
    "invariant + default": "invariant_and_default",
}

OBLIGATION_LEVELS = ("MUST NOT", "MUST", "SHOULD NOT", "SHOULD", "MAY")
MODAL_RE = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
RULE_ID_RE = re.compile(r"\b(CONV|CONC|SOB)-(\d{3})\b")
WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


class SourceError(RuntimeError):
    """The text no longer has the shape the projection relies on."""


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    """Split the document on level-2 headings. Returns (heading, body lines)."""
    sections: list[tuple[str, list[str]]] = []
    heading = ""
    body: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if heading or body:
                sections.append((heading, body))
            heading = line[3:].strip()
            body = []
        else:
            body.append(line)
    sections.append((heading, body))
    return sections


def find_section(sections, predicate, what: str) -> tuple[str, list[str]]:
    matches = [s for s in sections if predicate(s[0])]
    if len(matches) != 1:
        raise SourceError(f"expected exactly one section for {what}, found {len(matches)}")
    return matches[0]


def parse_tables(lines: list[str]) -> list[dict]:
    """Return every markdown table of a block, as {header, rows, raw_rows}."""
    tables: list[dict] = []
    current: dict | None = None
    for line in lines:
        stripped = line.strip()
        is_row = stripped.startswith("|") and stripped.endswith("|")
        if not is_row:
            current = None
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if current is None:
            current = {"header": cells, "rows": [], "raw_rows": []}
            tables.append(current)
            continue
        if all(set(c) <= set("-: ") and c for c in cells):
            continue  # separator row
        if len(cells) != len(current["header"]):
            raise SourceError(
                f"table row has {len(cells)} cells, header has {len(current['header'])}: {stripped}"
            )
        current["rows"].append(dict(zip(current["header"], cells)))
        current["raw_rows"].append(line.rstrip())
    return tables


def table_with_header(tables: list[dict], *columns: str) -> dict:
    """The single table holding all the given column names."""
    matches = [t for t in tables if all(c in t["header"] for c in columns)]
    if len(matches) != 1:
        raise SourceError(
            f"expected exactly one table with columns {columns}, found {len(matches)}"
        )
    return matches[0]


def expand_rule_ids(cell: str) -> list[str]:
    """Expand 'CONV-001 to 006, 010; CONC-001, 002' into explicit identifiers."""
    ids: list[str] = []
    prefix = None
    tokens = [t.strip() for t in re.split(r"[;,]", cell) if t.strip()]
    for token in tokens:
        range_match = re.match(
            r"^(?:(CONV|CONC|SOB)-)?(\d{3})\s+to\s+(?:(CONV|CONC|SOB)-)?(\d{3})$", token
        )
        if range_match:
            start_prefix = range_match.group(1) or prefix
            end_prefix = range_match.group(3) or start_prefix
            if start_prefix is None or start_prefix != end_prefix:
                raise SourceError(f"cannot read rule range: {token!r}")
            prefix = start_prefix
            for number in range(int(range_match.group(2)), int(range_match.group(4)) + 1):
                ids.append(f"{prefix}-{number:03d}")
            continue
        single_match = re.match(r"^(?:(CONV|CONC|SOB)-)?(\d{3})$", token)
        if single_match:
            prefix = single_match.group(1) or prefix
            if prefix is None:
                raise SourceError(f"rule number without a prefix: {token!r}")
            ids.append(f"{prefix}-{int(single_match.group(2)):03d}")
            continue
        raise SourceError(f"cannot read rule reference: {token!r}")
    return ids


# --------------------------------------------------------------------------
# Obligations
# --------------------------------------------------------------------------

def split_obligations(text: str) -> list[dict]:
    """Cut a convention text into its obligations, one per modal verb."""
    obligations: list[dict] = []
    for sentence in SENTENCE_SPLIT_RE.split(" ".join(text.split())):
        sentence = sentence.strip()
        if not sentence:
            continue
        modals = list(MODAL_RE.finditer(sentence))
        if not modals:
            continue
        cuts = [0]
        for modal in modals[1:]:
            separator = max(
                (sentence.rfind(sep, cuts[-1], modal.start()) for sep in (":", ";", ".")),
                default=-1,
            )
            if separator > cuts[-1]:
                cuts.append(separator + 1)
        cuts.append(len(sentence))
        for start, end in zip(cuts, cuts[1:]):
            segment = sentence[start:end].strip().rstrip(",;:")
            modal_match = MODAL_RE.search(segment)
            if not modal_match:
                continue
            obligations.append({"level": modal_match.group(1), "text": segment})
    return obligations


# --------------------------------------------------------------------------
# Section readers
# --------------------------------------------------------------------------

def parse_version(lines: list[str]) -> str:
    for line in lines[:20]:
        match = re.match(r"^Version\s+(\d+\.\d+\.\d+)\s+·", line.strip())
        if match:
            return match.group(1)
    raise SourceError("version line not found (expected 'Version x.y.z · ...')")


def parse_structure_counts(sections) -> dict[str, dict]:
    """Expected rule counts per part, from the Structure table."""
    _, body = find_section(sections, lambda h: h == "Structure", "Structure")
    table = table_with_header(parse_tables(body), "Part", "Prefix", "v0 rules")
    counts: dict[str, dict] = {}
    for row in table["rows"]:
        part = row["Part"].split("—")[0].strip()
        cell = row["v0 rules"]
        total_match = re.match(r"^(\d+)", cell)
        if not total_match:
            raise SourceError(f"cannot read a rule count in {cell!r}")
        breakdown: dict[str, int] = {}
        for number, status in re.findall(r"(\d+)\s+(proposed|draft|accepted|stable|retired)", cell):
            breakdown[status.capitalize()] = breakdown.get(status.capitalize(), 0) + int(number)
        if not breakdown:
            status_match = re.search(r"\d+\s+(proposed|draft|accepted|stable|retired)", cell)
            if status_match:
                breakdown[status_match.group(1).capitalize()] = int(total_match.group(1))
        counts[part] = {"total": int(total_match.group(1)), "by_status": breakdown}
    return counts


def parse_waves(sections) -> dict[str, int]:
    _, body = find_section(sections, lambda h: h == "Structure", "review waves")
    table = table_with_header(parse_tables(body), "Wave", "Opens", "Rules")
    waves: dict[str, int] = {}
    for row in table["rows"]:
        wave = int(row["Wave"])
        for rule_id in expand_rule_ids(row["Rules"]):
            if rule_id in waves:
                raise SourceError(f"{rule_id} appears in two waves")
            waves[rule_id] = wave
    return waves


def parse_principles(sections) -> dict[str, str]:
    _, body = find_section(sections, lambda h: h == "Principles", "Principles")
    table = table_with_header(parse_tables(body), "Id", "Principle", "Derived rules")
    principles: dict[str, str] = {}
    for row in table["rows"]:
        principle = row["Id"].strip()
        if not re.match(r"^P-\d{2}$", principle):
            raise SourceError(f"unexpected principle identifier: {principle!r}")
        for rule_id in expand_rule_ids(row["Derived rules"]):
            if rule_id in principles:
                raise SourceError(f"{rule_id} is derived from two principles")
            principles[rule_id] = principle
    return principles


def parse_type_and_wave(cell: str) -> tuple[str, int]:
    label, _, wave = cell.partition("·")
    key = " ".join(label.split()).lower()
    if key not in TYPE_LABELS:
        raise SourceError(f"unknown rule type: {label!r}")
    if not wave.strip().isdigit():
        raise SourceError(f"unknown review wave in {cell!r}")
    return TYPE_LABELS[key], int(wave.strip())


def status_from_heading(heading: str) -> str:
    match = re.search(r"\b(draft|proposed|accepted|stable|retired)\b", heading, re.IGNORECASE)
    if not match:
        raise SourceError(f"no rule status in heading: {heading!r}")
    return match.group(1).capitalize()


def parse_templated_rule(heading: str, body: list[str]) -> dict:
    """A rule written out in full, with the complete template."""
    rule_id_match = RULE_ID_RE.search(heading)
    if not rule_id_match:
        raise SourceError(f"no rule identifier in heading: {heading!r}")
    text = "\n".join(body)

    status_match = re.search(r"\*\*Status:\s*([A-Za-z]+)\.?\*\*\s*(.+)", text)
    if not status_match:
        raise SourceError(f"no status line for {rule_id_match.group(0)}")
    status = status_match.group(1).capitalize()
    summary = status_match.group(2).strip()

    type_match = re.search(r"\*\*Type\.\*\*\s*([^.]+)\.", text)
    if not type_match:
        raise SourceError(f"no type line for {rule_id_match.group(0)}")
    type_key = " ".join(type_match.group(1).split()).lower()
    if type_key not in TYPE_LABELS:
        raise SourceError(f"unknown rule type: {type_match.group(1)!r}")

    principle_match = re.search(r"\*\*Principle\.\*\*\s*(P-\d{2})", text)
    if not principle_match:
        raise SourceError(f"no principle line for {rule_id_match.group(0)}")

    obligations: list[dict] = []
    for block_start in re.finditer(r"^\*\*(Convention|Exception[^*]*)\.?\*\*\s*$", text, re.MULTILINE):
        for line in text[block_start.end():].split("\n"):
            if re.match(r"^\s*\d+\.\s+", line):
                obligations.extend(split_obligations(re.sub(r"^\s*\d+\.\s+", "", line)))
            elif line.strip().startswith("**"):
                break
    if not obligations:
        raise SourceError(f"no obligation found for {rule_id_match.group(0)}")

    return {
        "id": rule_id_match.group(0),
        "part": "A" if rule_id_match.group(1) == "CONV" else "B",
        "type": TYPE_LABELS[type_key],
        "status": status,
        "wave": None,
        "principle": principle_match.group(1),
        "summary": summary,
        "obligations": obligations,
        "rule_sha256": sha256_text(("## " + heading + "\n" + text).rstrip() + "\n"),
    }


def parse_table_rules(heading: str, table: dict, part: str) -> list[dict]:
    status = status_from_heading(heading)
    rules: list[dict] = []
    for row, raw in zip(table["rows"], table["raw_rows"]):
        rule_id = row["Id"].strip()
        if not RULE_ID_RE.fullmatch(rule_id):
            raise SourceError(f"unexpected rule identifier: {rule_id!r}")
        if "Type · wave" in row:
            rule_type, wave = parse_type_and_wave(row["Type · wave"])
        else:
            rule_type, wave = None, int(row["Wave"])
        summary = row["Convention (summary)"]
        rules.append({
            "id": rule_id,
            "part": part,
            "type": rule_type,
            "status": status,
            "wave": wave,
            "principle": row.get("Principle", "").strip() or None,
            "summary": summary,
            "obligations": split_obligations(summary),
            "rule_sha256": sha256_text(raw.strip() + "\n"),
        })
    return rules


def parse_levels(sections) -> dict:
    _, body = find_section(sections, lambda h: h == "Conformance levels", "Conformance levels")
    tables = parse_tables(body)
    conformance = table_with_header(tables, "Level", "Requirement")
    frugality = table_with_header(tables, "Indicator", "Requirement")
    return {
        "conformance": [
            {"id": row["Level"], "requirement": row["Requirement"]} for row in conformance["rows"]
        ],
        "frugality": [
            {"id": row["Indicator"], "requirement": row["Requirement"]} for row in frugality["rows"]
        ],
    }


def parse_thresholds(sections) -> dict:
    _, body = find_section(sections, lambda h: h == "Test protocol", "Test protocol")
    table = table_with_header(parse_tables(body), "Item", "Rule")
    rows = {row["Item"]: row["Rule"] for row in table["rows"]}

    def first_int(item: str) -> int:
        match = re.search(r"(\d+)", rows.get(item, ""))
        if not match:
            raise SourceError(f"no number in the {item!r} row of the test protocol")
        return int(match.group(1))

    percentages = re.findall(r"(\d+)\s*%", rows.get("Threshold", ""))
    if len(percentages) != 2:
        raise SourceError("expected two pass rates in the Threshold row")

    stable = re.search(
        r"at least (\d+) providers and (\d+) models.*?at least (\w+) campaigns",
        "\n".join(body),
        re.IGNORECASE | re.DOTALL,
    )
    if not stable:
        raise SourceError("no Stable-status sentence in the test protocol")
    campaigns = stable.group(3).lower()
    if campaigns not in WORD_NUMBERS and not campaigns.isdigit():
        raise SourceError(f"cannot read a campaign count from {campaigns!r}")

    return {
        "must_pass_rate": int(percentages[0]) / 100,
        "should_pass_rate": int(percentages[1]) / 100,
        "min_variants_per_case": first_int("Variants"),
        "min_runs_per_variant": first_int("Runs"),
        "stable_status": {
            "min_providers": int(stable.group(1)),
            "min_models": int(stable.group(2)),
            "min_campaigns": int(campaigns) if campaigns.isdigit() else WORD_NUMBERS[campaigns],
        },
    }


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build(source: Path, generated_at: str) -> dict:
    text = source.read_text(encoding="utf-8")
    lines = text.split("\n")
    sections = split_sections(lines)

    rules: list[dict] = []
    for heading, body in sections:
        part_match = re.match(r"^Part ([ABC]) —", heading)
        if not part_match:
            continue
        part = part_match.group(1)
        tables = [t for t in parse_tables(body) if "Convention (summary)" in t["header"]]
        if tables:
            if len(tables) != 1:
                raise SourceError(f"expected one rule table under {heading!r}")
            rules.extend(parse_table_rules(heading, tables[0], part))
        else:
            rules.append(parse_templated_rule(heading, body))

    waves = parse_waves(sections)
    principles = parse_principles(sections)
    seen: set[str] = set()
    for rule in rules:
        rule_id = rule["id"]
        if rule_id in seen:
            raise SourceError(f"{rule_id} is defined twice")
        seen.add(rule_id)
        if rule_id not in waves:
            raise SourceError(f"{rule_id} is in no review wave")
        if rule["wave"] is None:
            rule["wave"] = waves[rule_id]
        elif rule["wave"] != waves[rule_id]:
            raise SourceError(
                f"{rule_id}: wave {rule['wave']} in its row, {waves[rule_id]} in the waves table"
            )
        if rule_id not in principles:
            raise SourceError(f"{rule_id} is derived from no principle")
        if rule["principle"] is None:
            rule["principle"] = principles[rule_id]
        elif rule["principle"] != principles[rule_id]:
            raise SourceError(
                f"{rule_id}: principle {rule['principle']} in its row, "
                f"{principles[rule_id]} in the principles table"
            )
        if not rule["obligations"]:
            raise SourceError(f"{rule_id} states no obligation")
    for rule_id in sorted(set(waves) | set(principles)):
        if rule_id not in seen:
            raise SourceError(f"{rule_id} is referenced but has no rule")

    expected = parse_structure_counts(sections)
    for part, counted in expected.items():
        actual = [r for r in rules if r["part"] == part]
        if len(actual) != counted["total"]:
            raise SourceError(
                f"Part {part}: {len(actual)} rules read, {counted['total']} announced in Structure"
            )
        for status, number in counted["by_status"].items():
            found = len([r for r in actual if r["status"] == status])
            if found != number:
                raise SourceError(
                    f"Part {part}: {found} rules in status {status}, {number} announced in Structure"
                )

    rules.sort(key=lambda r: (PART_ORDER[r["part"]], int(r["id"].split("-")[1])))

    return {
        "convention_version": parse_version(lines),
        "generated_at": generated_at,
        "text_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "rules": rules,
        "levels": parse_levels(sections),
        "thresholds": parse_thresholds(sections),
    }


def serialise(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def body_of(document: dict) -> dict:
    """The document without the only field that depends on the run."""
    return {k: v for k, v in document.items() if k != "generated_at"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def frozen_path(document: dict) -> Path:
    return VERSIONS_DIR / f"v{document['convention_version']}" / "convention.json"


def report_difference(path: Path, expected: dict, found: dict, advice: str) -> None:
    diff = difflib.unified_diff(
        serialise(body_of(found)).splitlines(),
        serialise(body_of(expected)).splitlines(),
        fromfile=f"{path} (committed)",
        tofile=f"{path} (rebuilt from en.md)",
        lineterm="",
        n=2,
    )
    print(f"{path} is not the projection of en.md. {advice}")
    for line in list(diff)[:60]:
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--generated-at",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        help="timestamp written to the generated_at field (UTC, excluded from every comparison)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write: fail if a committed file is not the projection of en.md",
    )
    parser.add_argument(
        "--freeze",
        action="store_true",
        help="write versions/v<version>/convention.json, the frozen copy of this version",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="with --freeze: overwrite the copy of an already released version (repair only)",
    )
    args = parser.parse_args(argv)

    try:
        document = build(args.source, args.generated_at)
    except SourceError as error:
        print(f"en.md no longer has the expected shape: {error}", file=sys.stderr)
        return 2

    frozen = frozen_path(document)
    publishing = args.output.resolve() == DEFAULT_OUTPUT.resolve()
    if args.freeze and not publishing:
        print("--freeze only makes sense with the published convention.json", file=sys.stderr)
        return 2

    tag = f"v{document['convention_version']}"
    released = publishing and tag in released_tags(REPO_ROOT)

    if args.check:
        targets = [args.output]
        if publishing and not released:
            # While a version is unreleased its frozen copy must follow the text:
            # a version bump that forgets to freeze is caught here, not at release.
            targets.append(frozen)

        failures = 0
        for path in targets:
            advice = (
                "Run: python3 tools/build_convention_json.py --freeze"
                if path == frozen
                else "Run: python3 tools/build_convention_json.py"
            )
            if not path.exists():
                print(f"{path} is missing. {advice}")
                failures += 1
                continue
            committed = load(path)
            if body_of(committed) != body_of(document):
                report_difference(path, document, committed, advice)
                failures += 1

        if released:
            print(
                f"note: version {document['convention_version']} is already released ({tag}). "
                f"Its frozen copy answers to that tag, not to the text as it is now — "
                f"tools/check_frozen_versions.py is what checks it."
            )
            published_text = text_at_tag(REPO_ROOT, tag)
            if published_text is not None and published_text != args.source.read_bytes():
                print(
                    f"      en.md has changed since {tag} went out. The clean way out is to raise "
                    f"the version number in en.md; rebuilding the published copy to match would "
                    f"rewrite a file that has been signed."
                )

        if failures:
            return 1
        print(f"convention.json is the projection of en.md ({len(document['rules'])} rules).")
        return 0

    targets = [args.output]
    if args.freeze:
        if released and not args.force:
            print(
                f"refusing to write {frozen}: {tag} is already released, and that copy is the "
                f"file published with it.\n"
                f"    If the text has changed, raise the version number in en.md.\n"
                f"    To repair a corrupted copy, restore the signed asset:\n"
                f"      gh release download {tag} --pattern convention.json --dir versions/{tag}\n"
                f"    --force overrides this refusal. It reads the repository's tags, so in a "
                f"shallow clone it protects nothing: the guarantee is check_frozen_versions.py in CI."
            )
            return 2
        targets.append(frozen)

    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialise(document), encoding="utf-8")
        print(f"wrote {path} ({len(document['rules'])} rules, version {document['convention_version']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
