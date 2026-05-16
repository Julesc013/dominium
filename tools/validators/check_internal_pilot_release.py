#!/usr/bin/env python3
"""Validate a local-only Dominium internal pilot release staging root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from typing import Dict, Iterable, List, Mapping, Optional


REQUIRED_FILES = (
    "manifest/internal_pilot_release.manifest.json",
    "manifest/provenance.json",
    "manifest/checksums.sha256",
    "proof/native_binary_proof.md",
    "proof/product_boot_proof.md",
    "proof/portable_projection_proof.md",
    "proof/warning_ledger.md",
    "proof/validation_report.json",
    "docs/README_INTERNAL_PILOT.md",
    "docs/RUNBOOK.md",
    "docs/ROLLBACK.md",
)
REQUIRED_PROJECTION_MANIFESTS = (
    "projection/install.manifest.json",
    "projection/semantic_contract_registry.json",
    "projection/release.manifest.json",
)
REQUIRED_BINARIES = (
    "projection/bin/setup.exe",
    "projection/bin/launcher.exe",
    "projection/bin/client.exe",
    "projection/bin/server.exe",
    "projection/bin/tools.exe",
)
DISALLOWED_TOP_LEVEL = (".git", ".aide", ".aide.local", ".dominium.local", "build", "out", "dist")


def _norm(path: str) -> str:
    return path.replace(os.sep, "/")


def _repo_rel(repo_root: str, path: str) -> str:
    return _norm(os.path.relpath(path, repo_root))


def _abs(repo_root: str, path: str) -> str:
    return os.path.normpath(os.path.abspath(path if os.path.isabs(path) else os.path.join(repo_root, path)))


def _is_relative_to(path: str, parent: str) -> bool:
    path_abs = os.path.normcase(os.path.normpath(os.path.abspath(path)))
    parent_abs = os.path.normcase(os.path.normpath(os.path.abspath(parent)))
    try:
        return os.path.commonpath([path_abs, parent_abs]) == parent_abs
    except ValueError:
        return False


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload) if isinstance(payload, Mapping) else {}


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_check_ignored(repo_root: str, path: str) -> bool:
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError:
        return False
    return completed.returncode == 0


def _file_row(root: str, rel_path: str) -> Dict[str, object]:
    path = os.path.join(root, rel_path.replace("/", os.sep))
    return {"path": rel_path, "present": os.path.isfile(path)}


def _parse_checksums(release_root: str) -> Dict[str, str]:
    checksum_path = os.path.join(release_root, "manifest", "checksums.sha256")
    rows: Dict[str, str] = {}
    for line in _read_text(checksum_path).splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            rows["__parse_error__"] = line
            continue
        digest, rel_path = parts
        rows[rel_path.strip()] = digest.strip()
    return rows


def _checksum_failures(release_root: str, rows: Mapping[str, str]) -> List[Dict[str, str]]:
    failures: List[Dict[str, str]] = []
    for rel_path, expected in rows.items():
        if rel_path == "__parse_error__":
            failures.append({"path": rel_path, "reason": "checksum line could not be parsed"})
            continue
        abs_path = os.path.join(release_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            failures.append({"path": rel_path, "reason": "listed checksum file is missing"})
            continue
        actual = _sha256(abs_path)
        if actual != expected:
            failures.append({"path": rel_path, "reason": "checksum mismatch"})
    return failures


def _host_path_findings(repo_root: str, release_root: str) -> List[str]:
    findings: List[str] = []
    tokens = [
        os.path.normpath(os.path.abspath(repo_root)),
        os.path.normpath(os.path.abspath(release_root)),
    ]
    for rel_path in REQUIRED_PROJECTION_MANIFESTS + (
        "manifest/internal_pilot_release.manifest.json",
        "manifest/provenance.json",
    ):
        path = os.path.join(release_root, rel_path.replace("/", os.sep))
        text = _read_text(path)
        if not text:
            continue
        for token in tokens:
            if token and (token in text or token.replace("\\", "\\\\") in text):
                findings.append(rel_path)
                break
    return sorted(set(findings))


def build_report(repo_root: str, release_root: str, strict: bool = False) -> Dict[str, object]:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    release_abs = _abs(repo_root_abs, release_root)
    allowed_root = os.path.join(repo_root_abs, ".dominium.local", "releases")
    blockers: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    if not _is_relative_to(release_abs, allowed_root):
        blockers.append({"code": "release_root_not_local", "message": "release root must be under .dominium.local/releases"})
    if not os.path.isdir(release_abs):
        blockers.append({"code": "release_root_missing", "message": "release root is missing"})
    ignored = _git_check_ignored(repo_root_abs, release_abs) if os.path.exists(release_abs) else False
    if not ignored:
        blockers.append({"code": "release_root_not_ignored", "message": "release root is not ignored by git"})

    required_files = [_file_row(release_abs, rel_path) for rel_path in REQUIRED_FILES]
    for row in required_files:
        if not bool(row.get("present")):
            blockers.append({"code": "required_file_missing", "message": "{} is required".format(row.get("path", ""))})

    projection_manifests = [_file_row(release_abs, rel_path) for rel_path in REQUIRED_PROJECTION_MANIFESTS]
    for row in projection_manifests:
        if not bool(row.get("present")):
            blockers.append({"code": "projection_manifest_missing", "message": "{} is required".format(row.get("path", ""))})

    binaries = [_file_row(release_abs, rel_path) for rel_path in REQUIRED_BINARIES]
    for row in binaries:
        if not bool(row.get("present")):
            blockers.append({"code": "product_binary_missing", "message": "{} is required".format(row.get("path", ""))})

    json_files = (
        "manifest/internal_pilot_release.manifest.json",
        "manifest/provenance.json",
        "proof/validation_report.json",
    )
    parsed_json: Dict[str, bool] = {}
    for rel_path in json_files:
        path = os.path.join(release_abs, rel_path.replace("/", os.sep))
        if not os.path.isfile(path):
            parsed_json[rel_path] = False
            continue
        try:
            _read_json(path)
            parsed_json[rel_path] = True
        except (OSError, ValueError):
            parsed_json[rel_path] = False
            blockers.append({"code": "json_parse_failed", "message": "{} did not parse as JSON".format(rel_path)})

    checksum_rows = _parse_checksums(release_abs) if os.path.isfile(os.path.join(release_abs, "manifest", "checksums.sha256")) else {}
    checksum_failures = _checksum_failures(release_abs, checksum_rows)
    for row in checksum_failures:
        blockers.append({"code": "checksum_failed", "message": "{}: {}".format(row["path"], row["reason"])})

    top_level_entries = sorted(os.listdir(release_abs)) if os.path.isdir(release_abs) else []
    leaked_roots = [name for name in top_level_entries if name in DISALLOWED_TOP_LEVEL]
    for name in leaked_roots:
        blockers.append({"code": "source_or_local_root_leaked", "message": "disallowed top-level entry leaked: {}".format(name)})

    host_paths = _host_path_findings(repo_root_abs, release_abs) if os.path.isdir(release_abs) else []
    if host_paths:
        blockers.append({"code": "absolute_host_path", "message": "host path token found in manifests: {}".format(", ".join(host_paths))})

    if strict:
        manifest_path = os.path.join(release_abs, "manifest", "internal_pilot_release.manifest.json")
        try:
            manifest = _read_json(manifest_path)
        except (OSError, ValueError):
            manifest = {}
        if str(manifest.get("publication_status", "")).strip() != "local_internal_only":
            blockers.append({"code": "publication_status_not_local", "message": "publication_status must be local_internal_only"})
        if bool(manifest.get("public_release_created")):
            blockers.append({"code": "public_release_claimed", "message": "manifest must not claim public release creation"})
    else:
        warnings.append({"code": "strict_not_requested", "message": "strict mode was not requested"})

    status = "PASS" if not blockers else "BLOCKED"
    return {
        "schema_version": "dominium.release_00.internal_pilot_validator.v1",
        "release_root": _repo_rel(repo_root_abs, release_abs),
        "ignored_by_git": ignored,
        "required_files": required_files,
        "projection_manifests": projection_manifests,
        "product_binaries": binaries,
        "json_files": parsed_json,
        "checksum_entries": len(checksum_rows),
        "checksum_failures": checksum_failures,
        "host_path_findings": host_paths,
        "blockers": blockers,
        "warnings": warnings,
        "status": status,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a local-only Dominium internal pilot release staging root.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--release-root", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, args.release_root, strict=bool(args.strict))
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write("internal pilot release validation: {}\n".format(report["status"]))
        sys.stdout.write("release_root: {}\n".format(report["release_root"]))
        sys.stdout.write("checksum_entries: {}\n".format(report["checksum_entries"]))
        for blocker in report["blockers"]:
            sys.stdout.write("BLOCKER {}: {}\n".format(blocker.get("code", ""), blocker.get("message", "")))
        for warning in report["warnings"]:
            sys.stdout.write("WARNING {}: {}\n".format(warning.get("code", ""), warning.get("message", "")))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
