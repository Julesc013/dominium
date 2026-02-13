"""Impact graph for incremental XStack planning."""

from __future__ import annotations

import json
import os
import subprocess
from fnmatch import fnmatch
from typing import Dict, List, Set, Tuple

from .artifact_contract import load_artifact_contract
from .profiler import end_phase, start_phase

DEFAULT_SUBSYSTEMS: Tuple[str, ...] = (
    "engine",
    "game",
    "client",
    "server",
    "schema",
    "data",
    "tools",
    "docs",
    "scripts",
    "repo",
    "tests",
)
IGNORE_CHANGED_PREFIXES: Tuple[str, ...] = (
    "docs/audit/",
    "docs/audit/remediation/",
    ".xstack_cache/",
    "tools/auditx/cache/",
    "tools/compatx/cache/",
    "tools/performx/cache/",
    "tools/securex/cache/",
)


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _run_capture(repo_root: str, args: List[str]) -> str:
    phase = "impact_graph.subprocess"
    if args[:2] == ["git", "diff"]:
        phase = "impact_graph.git_diff"
    elif args[:2] == ["git", "status"]:
        phase = "impact_graph.git_status"
    start_phase(phase, {"argv": list(args)})
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
        end_phase(phase)
        return ""
    if proc.returncode != 0:
        end_phase(phase)
        return ""
    out = proc.stdout or ""
    end_phase(phase, {"returncode": int(proc.returncode)})
    return out


def _artifact_skip_paths(repo_root: str) -> Set[str]:
    contract = load_artifact_contract(repo_root)
    skip: Set[str] = set()
    for row in contract.values():
        rel = _norm(str(row.get("path", "")))
        if rel:
            skip.add(rel)
    return skip


def _filter_changed_paths(repo_root: str, paths: List[str]) -> List[str]:
    artifact_paths = _artifact_skip_paths(repo_root)
    out: List[str] = []
    for rel in paths:
        token = _norm(rel)
        if not token:
            continue
        if token in artifact_paths:
            continue
        if any(token.startswith(prefix) for prefix in IGNORE_CHANGED_PREFIXES):
            continue
        if token.startswith("tools/") and "/cache/" in token:
            continue
        out.append(token)
    return sorted(set(out))


def changed_files(repo_root: str) -> List[str]:
    start_phase("impact_graph.changed_files")
    base_ref = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    out = _run_capture(repo_root, ["git", "diff", "--name-only", "--diff-filter=ACMR", "{}...HEAD".format(base_ref)])
    if out:
        rows = sorted(set(_norm(line) for line in out.splitlines() if line.strip()))
        filtered = _filter_changed_paths(repo_root, rows)
        end_phase("impact_graph.changed_files", {"count": len(filtered)})
        return filtered
    status = _run_capture(repo_root, ["git", "status", "--porcelain"])
    files: List[str] = []
    for line in status.splitlines():
        line = line.rstrip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        files.append(_norm(parts[1]))
    filtered = _filter_changed_paths(repo_root, files)
    end_phase("impact_graph.changed_files", {"count": len(filtered)})
    return filtered


def _load_group_registry(path: str) -> Dict[str, dict]:
    if not os.path.isfile(path):
        return {}
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rows = ((payload.get("record") or {}).get("groups") or [])
    out: Dict[str, dict] = {}
    for row in rows:
        if isinstance(row, dict):
            group_id = str(row.get("group_id", "")).strip()
            if group_id:
                out[group_id] = row
    return out


def _match_any(path: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        token = str(pattern).strip()
        if not token:
            continue
        if fnmatch(path, token):
            return True
    return False


def _subsystems_for_paths(paths: List[str]) -> List[str]:
    out: Set[str] = set()
    for rel in paths:
        top = _norm(rel).split("/", 1)[0] if rel else ""
        if not top:
            continue
        if top in DEFAULT_SUBSYSTEMS:
            out.add(top)
        else:
            out.add("misc")
    return sorted(out)


def build_impact_graph(
    repo_root: str,
    testx_groups_path: str,
    auditx_groups_path: str,
    xstack_components_path: str,
) -> Dict[str, object]:
    start_phase("impact_graph.build")
    rel_paths = changed_files(repo_root)
    subsystems = _subsystems_for_paths(rel_paths)
    testx_groups = _load_group_registry(testx_groups_path)
    auditx_groups = _load_group_registry(auditx_groups_path)
    component_map = _load_group_registry(xstack_components_path)

    impacted_testx: Set[str] = set()
    impacted_auditx: Set[str] = set()
    required_runners: Set[str] = {"repox_runner"}

    for rel in rel_paths:
        for group_id, row in testx_groups.items():
            if _match_any(rel, row.get("paths") or []):
                impacted_testx.add(group_id)
        for group_id, row in auditx_groups.items():
            if _match_any(rel, row.get("paths") or []):
                impacted_auditx.add(group_id)

    if not rel_paths:
        impacted_testx.add("testx.group.core.invariants")
        impacted_auditx.add("auditx.group.core.policy")

    for subsystem in subsystems:
        row = component_map.get(subsystem, {})
        for runner_id in row.get("runners") or []:
            token = str(runner_id).strip()
            if token:
                required_runners.add(token)

    required_runners.update(("testx_runner", "auditx_runner"))

    result = {
        "changed_paths": rel_paths,
        "impacted_subsystems": subsystems,
        "impacted_testx_groups": sorted(impacted_testx),
        "impacted_auditx_groups": sorted(impacted_auditx),
        "required_runners": sorted(required_runners),
    }
    end_phase(
        "impact_graph.build",
        {
            "changed_paths": len(result["changed_paths"]),
            "testx_groups": len(result["impacted_testx_groups"]),
            "auditx_groups": len(result["impacted_auditx_groups"]),
        },
    )
    return result
