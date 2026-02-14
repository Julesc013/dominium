#!/usr/bin/env python3
"""Generate deterministic repository health snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from typing import Dict, List, Tuple

try:
    from .artifact_contract import load_artifact_contract
except ImportError:
    REPO_ROOT_HINT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    if REPO_ROOT_HINT not in sys.path:
        sys.path.insert(0, REPO_ROOT_HINT)
    from tools.xstack.core.artifact_contract import load_artifact_contract

_SCRIPTS_DEV = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts", "dev")
)
if _SCRIPTS_DEV not in sys.path:
    sys.path.insert(0, _SCRIPTS_DEV)

from env_tools_lib import canonical_workspace_id


DEFAULT_JSON_OUT = os.path.join("docs", "audit", "system", "REPO_HEALTH_SNAPSHOT.json")
DEFAULT_MD_OUT = os.path.join("docs", "audit", "system", "REPO_HEALTH_SNAPSHOT.md")


PROFILE_REPORT_PATHS = {
    "FAST": os.path.join("docs", "audit", "xstack", "PROFILE_FAST.json"),
    "STRICT": os.path.join("docs", "audit", "xstack", "PROFILE_STRICT_WARM.json"),
    "FULL": os.path.join("docs", "audit", "xstack", "PROFILE_FULL.json"),
}


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: str) -> str:
    handle = open(path, "rb")
    try:
        digest = hashlib.sha256()
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    finally:
        handle.close()


def _run_capture(repo_root: str, args: List[str]) -> str:
    try:
        proc = subprocess.run(
            args,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout or ""


def _load_json(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _git_head(repo_root: str) -> str:
    return (_run_capture(repo_root, ["git", "rev-parse", "HEAD"]) or "").strip()


def _git_status(repo_root: str) -> Tuple[bool, List[str]]:
    out = _run_capture(repo_root, ["git", "status", "--porcelain=v1"])
    rows = [line.rstrip() for line in out.splitlines() if line.strip()]
    return (len(rows) == 0, rows)


def _identity_hash(repo_root: str) -> str:
    path = os.path.join(repo_root, "docs", "audit", "identity_fingerprint.json")
    if not os.path.isfile(path):
        return ""
    return _sha256_file(path)


def _profile_report_hashes(repo_root: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for profile, rel in sorted(PROFILE_REPORT_PATHS.items()):
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        out[profile] = _sha256_file(abs_path) if os.path.isfile(abs_path) else ""
    return out


def _canonical_artifact_hashes(repo_root: str) -> Tuple[Dict[str, str], List[str]]:
    contract = load_artifact_contract(repo_root)
    hashes: Dict[str, str] = {}
    missing: List[str] = []
    for artifact_id in sorted(contract.keys()):
        row = contract.get(artifact_id, {})
        if str(row.get("artifact_class", "")).strip() != "CANONICAL":
            continue
        rel = _norm(str(row.get("path", "")))
        if not rel:
            continue
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel)
            continue
        hashes[artifact_id] = _sha256_file(abs_path)
    return hashes, sorted(set(missing))


def build_snapshot(repo_root: str) -> dict:
    head_sha = _git_head(repo_root)
    clean, status_rows = _git_status(repo_root)
    canonical_hashes, canonical_missing = _canonical_artifact_hashes(repo_root)
    profile_hashes = _profile_report_hashes(repo_root)
    identity_hash = _identity_hash(repo_root)
    workspace_id = canonical_workspace_id(repo_root, env=os.environ)

    payload = {
        "schema_id": "dominium.audit.repo_health_snapshot",
        "schema_version": "1.0.0",
        "artifact_class": "CANONICAL",
        "head_sha": head_sha,
        "identity_fingerprint_hash": identity_hash,
        "git_status_clean": bool(clean),
        "git_status_entries": status_rows,
        "workspace_id": workspace_id,
        "profile_report_hashes": profile_hashes,
        "canonical_artifact_hashes": canonical_hashes,
        "canonical_artifacts_missing": canonical_missing,
    }
    return payload


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_markdown(path: str, payload: dict, json_rel: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: 2026-02-14\n")
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# Repo Health Snapshot\n\n")
        handle.write("- source_json: `{}`\n".format(json_rel))
        handle.write("- head_sha: `{}`\n".format(str(payload.get("head_sha", ""))))
        handle.write("- git_status_clean: `{}`\n".format("true" if payload.get("git_status_clean") else "false"))
        handle.write("- identity_fingerprint_hash: `{}`\n".format(str(payload.get("identity_fingerprint_hash", ""))))
        handle.write("- workspace_id: `{}`\n".format(str(payload.get("workspace_id", ""))))
        handle.write(
            "- canonical_artifact_hash_count: `{}`\n".format(
                len(payload.get("canonical_artifact_hashes") or {})
            )
        )
        handle.write(
            "- canonical_artifacts_missing: `{}`\n".format(
                len(payload.get("canonical_artifacts_missing") or [])
            )
        )
        handle.write("\n## Profile Report Hashes\n\n")
        for profile, digest in sorted((payload.get("profile_report_hashes") or {}).items()):
            handle.write("- {}: `{}`\n".format(profile, digest or "missing"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic repo health snapshot artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    json_out = os.path.join(repo_root, _norm(args.json_out).replace("/", os.sep))
    md_out = os.path.join(repo_root, _norm(args.md_out).replace("/", os.sep))
    payload = build_snapshot(repo_root)
    _write_json(json_out, payload)
    _write_markdown(md_out, payload, _norm(args.json_out))
    print(
        json.dumps(
            {
                "result": "repo_health_snapshot_written",
                "json_out": _norm(os.path.relpath(json_out, repo_root)),
                "md_out": _norm(os.path.relpath(md_out, repo_root)),
                "git_status_clean": bool(payload.get("git_status_clean")),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
