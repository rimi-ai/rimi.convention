#!/usr/bin/env python3
"""Check that every frozen copy still projects the text of its own tag.

`versions/v<x.y.z>/convention.json` is the file published, and signed, with the
release `v<x.y.z>`. The text of a tag never changes, so its projection must not
change either.

Nothing else catches this. An ordinary build rewrites the frozen copy of the
current version as soon as its folder exists, so editing en.md without raising
the version number silently replaces a published file — and `--check` still
passes, because it compares the frozen copy with the text as it is now, not
with the text as it was tagged.

This check compares each frozen copy against the text at its own tag, twice:

    1. the fingerprint  — versions/v0.3.0/convention.json .text_sha256
                          ==  sha256(en.md at tag v0.3.0)
    2. the content      — the projection rebuilt from en.md at that tag
                          ==  the frozen file, field by field

The second comparison exists because the first one does not see the file's own
body. An obligation inside a frozen copy can be turned from MUST into SHOULD
and `text_sha256` still answers for the text, which has not moved: the
fingerprint covers the source, never the projection. That was demonstrated on
a copy of this repository in September 2026, and it is what step 2 closes.

The rebuild uses the builder of that tag when the tag carries one, and this
repository's builder otherwise — the first tags were cut before the builder
existed. Which one was used is printed, never assumed.

A released version that has no frozen copy at all (a release made before this
tooling existed) is reported, not counted as a failure.

Usage:
    python3 tools/check_frozen_versions.py [--repo PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r"^v\d+\.\d+\.\d+$")


def git(repo: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments], capture_output=True, text=False
    )


def released_tags(repo: Path) -> list[str]:
    result = git(repo, "tag", "--list", "v*")
    if result.returncode != 0:
        return []
    tags = [t for t in result.stdout.decode().split("\n") if TAG_RE.match(t.strip())]
    return sorted(tags)


def text_at_tag(repo: Path, tag: str) -> bytes | None:
    result = git(repo, "show", f"{tag}:en.md")
    return result.stdout if result.returncode == 0 else None


def builder_at_tag(repo: Path, tag: str, into: Path) -> tuple[Path, str]:
    """The builder that belongs to this tag, or this repository's, said plainly.

    The whole `tools/` tree of the tag is extracted, not the one file: the
    builder imports its neighbours, and a lone script fails on the first
    import. Found on v0.3.1, the first tag to carry a builder at all.
    """
    result = git(repo, "archive", tag, "tools")
    if result.returncode == 0:
        with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
            archive.extractall(into, filter="data")
        builder = into / "tools" / "build_convention_json.py"
        if builder.exists():
            return builder, f"the builder at {tag}"
    return REPO_ROOT / "tools" / "build_convention_json.py", (
        f"this repository's builder ({tag} carries none)"
    )


def rebuild(repo: Path, tag: str, source: bytes, into: Path) -> tuple[dict | None, str]:
    """Project the text of a tag with the right builder. Returns (document, how)."""
    text = into / "en.md"
    text.write_bytes(source)
    builder, how = builder_at_tag(repo, tag, into)
    output = into / "rebuilt.json"
    result = subprocess.run(
        ["python3", str(builder), "--source", str(text), "--output", str(output)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not output.exists():
        return None, f"{how}; it could not build: {result.stderr.strip().splitlines()[-1:] or ['no output']}"
    return json.loads(output.read_text(encoding="utf-8")), how


def first_difference(rebuilt: object, frozen: object, path: str = "") -> str | None:
    """Where the two documents part company, named so a reader can go and look."""
    if isinstance(rebuilt, dict) and isinstance(frozen, dict):
        for key in sorted(set(rebuilt) | set(frozen)):
            if key == "generated_at":
                continue
            if key not in rebuilt:
                return f"{path}.{key}: absent from the rebuild, present in the frozen copy"
            if key not in frozen:
                return f"{path}.{key}: present in the rebuild, absent from the frozen copy"
            found = first_difference(rebuilt[key], frozen[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(rebuilt, list) and isinstance(frozen, list):
        if len(rebuilt) != len(frozen):
            return f"{path}: {len(rebuilt)} entries rebuilt, {len(frozen)} in the frozen copy"
        for index, (a, b) in enumerate(zip(rebuilt, frozen)):
            found = first_difference(a, b, f"{path}[{index}]")
            if found:
                return found
        return None
    if rebuilt != frozen:
        return f"{path}: rebuilt {rebuilt!r}, frozen copy {frozen!r}"
    return None


def repair_instructions(tag: str) -> str:
    return (
        f"    Repair, preferably from the file that was signed:\n"
        f"      gh release download {tag} --pattern convention.json --dir versions/{tag}\n"
        f"    or rebuild it from the text of that tag:\n"
        f"      git show {tag}:en.md > /tmp/en-{tag}.md\n"
        f"      python3 tools/build_convention_json.py --source /tmp/en-{tag}.md \\\n"
        f"          --output versions/{tag}/convention.json"
    )


def check(repo: Path) -> int:
    versions = repo / "versions"
    frozen_copies = sorted(versions.glob("*/convention.json")) if versions.exists() else []
    tags = released_tags(repo)

    if not tags:
        print(
            "no release tag is visible: fetch them before checking "
            "(actions/checkout needs fetch-depth: 0).",
        )
        return 2

    failures = 0
    for path in frozen_copies:
        tag = path.parent.name
        if not TAG_RE.match(tag):
            print(f"{path}: {tag!r} is not a release tag name (expected vX.Y.Z).")
            failures += 1
            continue

        source = text_at_tag(repo, tag)
        if source is None:
            print(
                f"{path}: there is no tag {tag} in this repository, so this frozen copy "
                f"belongs to no release.",
            )
            failures += 1
            continue

        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"{path}: cannot be read as JSON: {error}")
            print(repair_instructions(tag))
            failures += 1
            continue

        expected = hashlib.sha256(source).hexdigest()
        found = document.get("text_sha256")
        version = document.get("convention_version")

        if found != expected:
            print(
                f"{path}: this frozen copy no longer projects the text published at {tag}.\n"
                f"    en.md at {tag} : {expected}\n"
                f"    file claims    : {found}\n"
                f"    The published file has been rewritten — most likely by an ordinary build\n"
                f"    after en.md changed without the version being raised.",
            )
            print(repair_instructions(tag))
            failures += 1
            continue

        if version != tag[1:]:
            print(
                f"{path}: version {version!r} inside a folder named {tag!r}.",
            )
            print(repair_instructions(tag))
            failures += 1
            continue

        # The fingerprint answers for the text. Only rebuilding answers for the file.
        with tempfile.TemporaryDirectory() as workspace:
            rebuilt, how = rebuild(repo, tag, source, Path(workspace))
            if rebuilt is None:
                print(
                    f"{path}: the projection could not be rebuilt from the text at {tag}, "
                    f"so its content was not compared — {how}",
                )
                failures += 1
                continue
            difference = first_difference(rebuilt, document)

        if difference:
            print(
                f"{path}: this frozen copy is not what the text at {tag} projects.\n"
                f"    first difference — {difference}\n"
                f"    rebuilt with {how}, generated_at ignored.\n"
                f"    text_sha256 still matches: the fingerprint answers for the text,\n"
                f"    and the text has not moved. The file itself has.",
            )
            print(repair_instructions(tag))
            failures += 1
            continue

        print(f"{path}: projects en.md at {tag}, fingerprint and content ({expected[:12]}…, {how})")

    frozen_tags = {path.parent.name for path in frozen_copies}
    for tag in tags:
        if tag not in frozen_tags:
            print(f"note: release {tag} has no frozen copy (released before versions/ existed).")

    if failures:
        print(f"\n{failures} frozen copy/copies no longer match their tag.")
        return 1

    print(f"{len(frozen_copies)} frozen copy/copies checked against their tags — fingerprint and content, rebuilt from the text of each tag.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return check(args.repo.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
