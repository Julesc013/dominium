#!/usr/bin/env python3
"""Inventory known Dominium tooling surfaces without executing them."""

import argparse
import json
import sys
from pathlib import Path


KNOWN_TOOLING_PATHS = [
    "tools/xstack",
    "tools/xstack/auditx",
    "tools/repox",
    "tools/testx",
    "tools/build",
    "tools/validators",
    "scripts/dev",
    "scripts/ci",
    ".aide/tools",
]


def count_files(path):
    if path.is_file():
        return 1
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def examples(path, repo_root, limit=12):
    if not path.exists():
        return []
    if path.is_file():
        return [str(path.relative_to(repo_root)).replace("\\", "/")]
    values = []
    for item in sorted(path.rglob("*"), key=lambda p: str(p).lower()):
        if item.is_file():
            values.append(str(item.relative_to(repo_root)).replace("\\", "/"))
            if len(values) >= limit:
                break
    return values


def inventory(repo_root):
    records = []
    for rel in KNOWN_TOOLING_PATHS:
        path = repo_root / rel
        present = path.exists()
        records.append({
            "path": rel,
            "present": present,
            "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            "classification": "candidate_tooling" if present else "missing_candidate_tooling",
            "execution_inferred_safe": False,
            "executed": False,
            "file_count": count_files(path),
            "examples": examples(path, repo_root),
        })
    summary = {
        "known_paths": len(records),
        "present": sum(1 for record in records if record["present"]),
        "missing": sum(1 for record in records if not record["present"]),
        "executed": 0,
    }
    return {
        "schema_version": "dominium.aide.tooling_inventory.v1",
        "repo_root": str(repo_root),
        "summary": summary,
        "records": records,
    }


def emit_human(data):
    print("Existing tooling inventory")
    print("==========================")
    for record in data["records"]:
        print("{path}\t{kind}\t{classification}\tfiles={file_count}\texecuted={executed}".format(**record))


def write_text_lf(path, text):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON.")
    parser.add_argument("--out", help="Write deterministic JSON to this path.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    data = inventory(repo_root)
    json_text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(out_path, json_text)
    if args.json:
        sys.stdout.write(json_text)
    else:
        emit_human(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
