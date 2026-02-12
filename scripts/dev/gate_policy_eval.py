#!/usr/bin/env python3
"""Impact-based gate mode evaluation for FAST/STRICT/FULL routing."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from typing import Dict, List, Tuple


FAST_MODE = "FAST"
STRICT_MODE = "STRICT"
FULL_MODE = "FULL"


_DOC_ONLY_PREFIXES = (
    "docs/",
    ".github/",
    ".vscode/",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "GOVERNANCE.md",
)

_UI_ONLY_PREFIXES = (
    "schema/ui/",
    "docs/ui/",
    "client/ui/",
    "libs/ui_",
    "tools/ui_",
)

_FAST_CODE_PREFIXES = (
    "client/",
    "game/",
)

_STRICT_PREFIXES = (
    "schema/",
    "data/registries/",
    "repo/repox/",
    "tests/",
    "scripts/ci/",
)

_PACKAGING_PREFIXES = (
    "scripts/pkg/",
    "scripts/dist/",
    "cmake/dist",
    "dist/",
    "updates/",
)


def _run_capture(repo_root: str, args: List[str]) -> str | None:
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
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _normalize_rel(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def changed_files_from_git(repo_root: str) -> List[str]:
    baseline_ref = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    out = _run_capture(
        repo_root,
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "{}...HEAD".format(baseline_ref)],
    )
    if out is None:
        out = _run_capture(repo_root, ["git", "status", "--porcelain"])
        if out is None:
            return []
        files = []
        for line in out.splitlines():
            line = line.rstrip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            files.append(_normalize_rel(parts[1]))
        return sorted(set(files))
    files = [_normalize_rel(line) for line in out.splitlines() if line.strip()]
    return sorted(set(files))


def _all_under(paths: List[str], prefixes: Tuple[str, ...]) -> bool:
    if not paths:
        return False
    for rel in paths:
        rel_norm = _normalize_rel(rel)
        if not any(rel_norm.startswith(prefix) for prefix in prefixes):
            return False
    return True


def _any_under(paths: List[str], prefixes: Tuple[str, ...]) -> bool:
    for rel in paths:
        rel_norm = _normalize_rel(rel)
        if any(rel_norm.startswith(prefix) for prefix in prefixes):
            return True
    return False


def classify_change_impact(changed_files: List[str]) -> str:
    if not changed_files:
        return "NO_CHANGES"
    if _all_under(changed_files, _DOC_ONLY_PREFIXES):
        return "DOCS_ONLY"
    if _all_under(changed_files, _UI_ONLY_PREFIXES):
        return "UI_ONLY"
    if _all_under(changed_files, _FAST_CODE_PREFIXES):
        return "CLIENT_GAME_ONLY"
    if _any_under(changed_files, _STRICT_PREFIXES):
        return "STRICT_REQUIRED"
    if _any_under(changed_files, _PACKAGING_PREFIXES):
        return "PACKAGING_TOUCHED"
    return "FAST_DEFAULT"


def evaluate_gate_mode(
    repo_root: str,
    gate_command: str,
    force_strict: bool = False,
    force_full: bool = False,
) -> Dict[str, object]:
    changed_files = changed_files_from_git(repo_root)
    impact = classify_change_impact(changed_files)

    if gate_command == "dist":
        mode = FULL_MODE
        reason = "dist_lane"
    elif gate_command == "full":
        mode = FULL_MODE
        reason = "explicit_full_command"
    elif gate_command == "strict":
        mode = STRICT_MODE
        reason = "explicit_strict_command"
    elif force_full:
        mode = FULL_MODE
        reason = "forced_full_flag"
    elif force_strict:
        mode = STRICT_MODE
        reason = "forced_strict_flag"
    elif impact in ("STRICT_REQUIRED",):
        mode = STRICT_MODE
        reason = "strict_required_paths"
    elif impact == "PACKAGING_TOUCHED":
        # Packaging changes only escalate to FULL for dist/--full.
        mode = STRICT_MODE
        reason = "packaging_touched_non_dist"
    else:
        mode = FAST_MODE
        reason = "fast_default"

    return {
        "mode": mode,
        "impact": impact,
        "reason": reason,
        "changed_files": changed_files,
    }


def load_gate_policy_version(repo_root: str, gate_policy_rel: str) -> str:
    path = os.path.join(repo_root, gate_policy_rel)
    if not os.path.isfile(path):
        return "missing"
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return "unreadable"
    record = payload.get("record", {})
    schema_version = str(payload.get("schema_version", "")).strip()
    registry_version = str(record.get("registry_version", "")).strip()
    return "{}|{}".format(schema_version, registry_version)


def _diff_blob(repo_root: str, args: List[str]) -> str:
    out = _run_capture(repo_root, args)
    return out or ""


def compute_workspace_state_hash(
    repo_root: str,
    gate_policy_version: str,
) -> str:
    head = _run_capture(repo_root, ["git", "rev-parse", "HEAD"]) or ""
    head = head.strip()
    unstaged = _diff_blob(repo_root, ["git", "diff", "--no-ext-diff", "--binary", "--", "."])
    staged = _diff_blob(repo_root, ["git", "diff", "--cached", "--no-ext-diff", "--binary", "--", "."])
    status = _run_capture(repo_root, ["git", "status", "--porcelain=v1", "--untracked-files=normal"]) or ""
    diff_hash = hashlib.sha256(
        ("\n".join([unstaged, staged, status])).encode("utf-8", errors="replace")
    ).hexdigest()
    payload = "\n".join([head, diff_hash, gate_policy_version]).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()
