#!/usr/bin/env python3
"""Select Dominium validation tiers from changed paths."""

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "tests" / "validation_tiers.json"


def load_manifest(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def git_lines(args):
    completed = subprocess.run(
        ["git"] + args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return None
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def changed_paths(base, include_worktree=False):
    paths = git_lines(["diff", "--name-only", "{}...HEAD".format(base)])
    if paths is None:
        paths = git_lines(["diff", "--name-only", base, "HEAD"]) or []

    selected = set(paths)
    if include_worktree:
        for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
            for path in git_lines(args) or []:
                selected.add(path)
    return sorted(selected)


def matches_any(path, patterns):
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if fnmatch.fnmatch(path, normalized):
            return True
    return False


def select_tiers(manifest, paths):
    selected = set(manifest.get("default_impacted_tiers", []))
    reasons = []
    for path in paths:
        for entry in manifest.get("path_map", []):
            if matches_any(path, entry.get("paths", [])):
                for tier in entry.get("tiers", []):
                    selected.add(tier)
                reasons.append(
                    {
                        "path": path,
                        "patterns": entry.get("paths", []),
                        "tiers": entry.get("tiers", []),
                    }
                )
    ordered = [name for name in manifest.get("tiers", {}) if name in selected]
    return ordered, reasons


def write_json(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_tiers(tiers, dry_run=False):
    command = [sys.executable, str(REPO_ROOT / "scripts" / "test_tier.py")]
    if dry_run:
        command.append("--dry-run")
    for tier in tiers:
        command.extend(["--tier", tier])
    print(" ".join(command))
    if dry_run:
        return 0
    completed = subprocess.run(command, cwd=str(REPO_ROOT))
    return completed.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--from", dest="base", default="HEAD~1")
    parser.add_argument("--include-worktree", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    manifest = load_manifest(Path(args.manifest))
    paths = changed_paths(args.base, include_worktree=args.include_worktree)
    tiers, reasons = select_tiers(manifest, paths)
    payload = {
        "schema_version": "dominium.impacted_test_selection.v1",
        "base": args.base,
        "include_worktree": args.include_worktree,
        "changed_paths": paths,
        "selected_tiers": tiers,
        "reasons": reasons,
    }

    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json_out:
        write_json(args.json_out, payload)

    if args.run:
        return run_tiers(tiers, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
