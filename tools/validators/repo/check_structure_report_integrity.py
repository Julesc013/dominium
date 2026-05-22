#!/usr/bin/env python3
"""Verify tracked-only structure report bundle integrity.

The canonical finalization pass keeps task-local structure exports under the
ignored .dominium.local tree. This validator can verify such a bundle when a
manifest is supplied, and otherwise reports whether any known active tracked
dirfiles bundle artifacts are present.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import hashlib
import json
import os
import subprocess
import sys


KNOWN_BUNDLE_FILES = {
    "dirfiles_manifest.json",
    "dir_tree.json",
    "dir_tree.txt",
    "dirfiles.zip",
    "dirfiles_run.log",
}


def _configure_stdio():
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdio()


def utc_now():
    return _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def posix(path):
    return str(path).replace("\\", "/")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_files(repo_root):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_manifest(manifest_path):
    manifest_path = os.path.abspath(manifest_path)
    bundle_dir = os.path.dirname(manifest_path)
    findings = []
    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:
        return {
            "bundle_dir": posix(bundle_dir),
            "manifest": posix(manifest_path),
            "status": "BLOCKED",
            "finding_count": 1,
            "findings": [{"severity": "blocker", "path": posix(manifest_path), "message": "failed to parse manifest: {0}".format(exc)}],
        }

    if manifest.get("source_mode") != "git_tracked":
        findings.append(
            {
                "severity": "blocker",
                "path": posix(manifest_path),
                "message": "manifest source_mode must be git_tracked",
            }
        )

    entries = manifest.get("files", [])
    if not isinstance(entries, list) or not entries:
        findings.append(
            {
                "severity": "blocker",
                "path": posix(manifest_path),
                "message": "manifest must contain non-empty files[]",
            }
        )
    for entry in entries if isinstance(entries, list) else []:
        rel = entry.get("path", "")
        if not rel or os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
            findings.append(
                {
                    "severity": "blocker",
                    "path": rel,
                    "message": "manifest entry path must be relative and stay inside bundle",
                }
            )
            continue
        candidate = os.path.join(bundle_dir, *rel.replace("\\", "/").split("/"))
        if not os.path.exists(candidate):
            findings.append({"severity": "blocker", "path": rel, "message": "manifest entry is missing"})
            continue
        actual_hash = sha256_file(candidate)
        actual_size = os.path.getsize(candidate)
        if entry.get("sha256") != actual_hash:
            findings.append({"severity": "blocker", "path": rel, "message": "sha256 mismatch"})
        if entry.get("size") != actual_size:
            findings.append({"severity": "blocker", "path": rel, "message": "size mismatch"})

    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    return {
        "bundle_dir": posix(bundle_dir),
        "manifest": posix(manifest_path),
        "schema_version": manifest.get("schema_version", ""),
        "source_mode": manifest.get("source_mode", ""),
        "commit": manifest.get("commit", ""),
        "branch": manifest.get("branch", ""),
        "status": "BLOCKED" if blocker_count else "PASS",
        "finding_count": len(findings),
        "findings": findings,
    }


def inspect_tracked(repo_root):
    tracked = git_files(repo_root)
    bundle_files = [path for path in tracked if path.split("/")[-1] in KNOWN_BUNDLE_FILES]
    findings = []
    for path in bundle_files:
        findings.append(
            {
                "severity": "warning",
                "path": path,
                "message": "tracked structure report artifact needs an explicit integrity manifest",
            }
        )
    return {
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "PASS_WITH_WARNINGS" if findings else "PASS",
        "tracked_bundle_file_count": len(bundle_files),
        "finding_count": len(findings),
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify structure report bundle integrity.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", help="Path to a structure bundle manifest.json.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on blockers.")
    args = parser.parse_args()

    if args.manifest:
        report = verify_manifest(args.manifest)
    else:
        report = inspect_tracked(os.path.abspath(args.repo_root))
    report["generated_utc"] = utc_now()

    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("structure report integrity: {0}".format(report["status"]))
        for item in report.get("findings", []):
            print("{severity} {path}: {message}".format(**item))

    if args.strict and report["status"] == "BLOCKED":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
