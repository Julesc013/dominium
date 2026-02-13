"""Deterministic execution plan generator for XStack gate runs."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Tuple

from .impact_graph import build_impact_graph
from .merkle_tree import compute_repo_state_hash
from .profiler import end_phase, start_phase
from .time_estimator import estimate_plan


GATE_POLICY_REL = os.path.join("data", "registries", "gate_policy.json")
TESTX_GROUPS_REL = os.path.join("data", "registries", "testx_groups.json")
AUDITX_GROUPS_REL = os.path.join("data", "registries", "auditx_groups.json")
XSTACK_COMPONENTS_REL = os.path.join("data", "registries", "xstack_components.json")


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _load_json(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_groups(path: str) -> Dict[str, dict]:
    payload = _load_json(path)
    rows = ((payload.get("record") or {}).get("groups") or [])
    out = {}
    for row in rows:
        if isinstance(row, dict):
            group_id = str(row.get("group_id", "")).strip()
            if group_id:
                out[group_id] = row
    return out


def _profile_defaults(gate_command: str, gate_policy_payload: dict) -> str:
    defaults = (((gate_policy_payload.get("record") or {}).get("extensions") or {}).get("default_mode_by_command") or {})
    if isinstance(defaults, dict):
        value = str(defaults.get(gate_command, "")).strip().upper()
        if value:
            return value
    if gate_command == "strict":
        return "STRICT"
    if gate_command in {"full", "dist"}:
        return "FULL"
    return "FAST"


def _detect_strict_depth(changed_paths: List[str]) -> str:
    deep_prefixes = ("schema/", "data/registries/", "repo/repox/", "scripts/ci/")
    for rel in changed_paths:
        token = _norm(rel)
        if any(token.startswith(prefix) for prefix in deep_prefixes):
            return "STRICT_DEEP"
    return "STRICT_LIGHT"


def _command_tokens(raw: object) -> List[str]:
    if isinstance(raw, list):
        out = []
        for idx, item in enumerate(raw):
            token = str(item)
            if idx == 0 and token in ("python", "python3"):
                out.append("python")
            else:
                out.append(token)
        return out
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def _build_group_nodes(
    groups: Dict[str, dict],
    impacted_ids: List[str],
    include_all: bool,
    profile: str,
    prefix: str,
) -> List[dict]:
    out: List[dict] = []
    selected = sorted(groups.keys()) if include_all else sorted(set(impacted_ids))
    for group_id in selected:
        row = groups.get(group_id, {})
        default_profile = str(row.get("default_profile", "fast")).strip().upper()
        if profile == "FAST" and default_profile not in {"FAST"}:
            continue
        if profile == "STRICT" and default_profile not in {"FAST", "STRICT"}:
            continue
        node = {
            "node_id": "{}::{}".format(prefix, group_id),
            "runner_id": str(row.get("runner_id", "{}_runner".format(prefix))).strip() or "{}_runner".format(prefix),
            "group_id": group_id,
            "command": _command_tokens(row.get("runner_command")),
            "expected_artifacts": sorted(set(str(item) for item in (row.get("expected_artifacts") or []) if str(item).strip())),
            "parallelizable": True,
            "depends_on": ["repox.base"],
        }
        out.append(node)
    return out


def _plan_hash(plan_payload: Dict[str, object]) -> str:
    canonical = json.dumps(plan_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _set_levels(nodes: List[dict]) -> List[dict]:
    by_id = {str(row.get("node_id", "")): row for row in nodes}

    def level_for(node: dict, memo: Dict[str, int]) -> int:
        node_id = str(node.get("node_id", ""))
        if node_id in memo:
            return memo[node_id]
        deps = [str(item) for item in (node.get("depends_on") or []) if str(item).strip() in by_id]
        if not deps:
            memo[node_id] = 0
            return 0
        level = 1 + max(level_for(by_id[dep], memo) for dep in sorted(deps))
        memo[node_id] = level
        return level

    memo: Dict[str, int] = {}
    for row in nodes:
        row["level"] = level_for(row, memo)
    return nodes


def _enforce_artifact_write_order(nodes: List[dict]) -> List[dict]:
    owners: Dict[str, str] = {}
    ordered = sorted(nodes, key=lambda row: str(row.get("node_id", "")))
    for row in ordered:
        node_id = str(row.get("node_id", "")).strip()
        deps = [str(item).strip() for item in (row.get("depends_on") or []) if str(item).strip()]
        for artifact in sorted(str(item).replace("\\", "/").strip() for item in (row.get("expected_artifacts") or []) if str(item).strip()):
            owner = owners.get(artifact, "")
            if owner and owner != node_id and owner not in deps:
                deps.append(owner)
            owners[artifact] = node_id
        row["depends_on"] = sorted(set(deps))
    return nodes


def build_execution_plan(
    repo_root: str,
    gate_command: str,
    requested_profile: str = "",
    workspace_id: str = "",
    cache_root: str = "",
) -> Dict[str, object]:
    start_phase("plan.generate", {"gate_command": gate_command, "requested_profile": requested_profile})
    try:
        gate_policy = _load_json(os.path.join(repo_root, GATE_POLICY_REL))
        testx_groups = _load_groups(os.path.join(repo_root, TESTX_GROUPS_REL))
        auditx_groups = _load_groups(os.path.join(repo_root, AUDITX_GROUPS_REL))
        xstack_components = _load_groups(os.path.join(repo_root, XSTACK_COMPONENTS_REL))

        impact = build_impact_graph(
            repo_root,
            os.path.join(repo_root, TESTX_GROUPS_REL),
            os.path.join(repo_root, AUDITX_GROUPS_REL),
            os.path.join(repo_root, XSTACK_COMPONENTS_REL),
        )

        merkle = compute_repo_state_hash(repo_root, cache_root=cache_root)
        profile = (requested_profile or _profile_defaults(gate_command, gate_policy)).strip().upper() or "FAST"
        strict_depth = _detect_strict_depth(impact.get("changed_paths") or [])
        include_all = profile == "FULL" and str(os.environ.get("DOM_GATE_FULL_ALL", "")).strip().lower() in {
            "1",
            "true",
            "yes",
        }

        nodes: List[dict] = [
            {
                "node_id": "repox.base",
                "runner_id": "repox_runner",
                "command": ["python", "scripts/ci/check_repox_rules.py", "--repo-root", "{repo_root}"],
                "expected_artifacts": ["docs/audit/proof_manifest.json"],
                "parallelizable": False,
                "depends_on": [],
            }
        ]

        nodes.extend(_build_group_nodes(testx_groups, impact.get("impacted_testx_groups") or [], include_all, profile, "testx"))
        nodes.extend(_build_group_nodes(auditx_groups, impact.get("impacted_auditx_groups") or [], include_all, profile, "auditx"))

        required_runners = impact.get("required_runners") or []
        if profile == "FULL":
            for runner_id in ("performx_runner", "compatx_runner", "securex_runner"):
                if runner_id in required_runners or profile == "FULL":
                    nodes.append(
                        {
                            "node_id": runner_id,
                            "runner_id": runner_id,
                            "command": _command_tokens(xstack_components.get(runner_id, {}).get("runner_command")),
                            "expected_artifacts": xstack_components.get(runner_id, {}).get("expected_artifacts") or [],
                            "parallelizable": True,
                            "depends_on": ["repox.base"],
                        }
                    )

        nodes = _enforce_artifact_write_order(nodes)
        nodes = _set_levels(nodes)
        nodes = sorted(
            nodes,
            key=lambda row: (
                int(row.get("level", 0)),
                "0" if not bool(row.get("parallelizable", False)) else "1",
                str(row.get("runner_id", "")),
                str(row.get("node_id", "")),
            ),
        )

        plan_payload = {
            "schema_version": "1.0.0",
            "gate_command": gate_command,
            "profile": profile,
            "strict_variant": strict_depth if profile == "STRICT" else "",
            "workspace_id": workspace_id,
            "repo_state_hash": str(merkle.get("repo_state_hash", "")),
            "merkle_roots": merkle.get("roots", {}),
            "impact": impact,
            "nodes": nodes,
        }
        plan_payload["estimate"] = estimate_plan(plan_payload)
        plan_hash = _plan_hash(plan_payload)
        plan_payload["plan_hash"] = plan_hash

        plans_dir = os.path.join(cache_root or os.path.join(repo_root, ".xstack_cache"), "plans")
        if not os.path.isdir(plans_dir):
            os.makedirs(plans_dir, exist_ok=True)
        plan_path = os.path.join(plans_dir, "{}.json".format(plan_hash))
        with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(plan_payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        plan_payload["plan_path"] = plan_path
        return plan_payload
    finally:
        end_phase("plan.generate")
