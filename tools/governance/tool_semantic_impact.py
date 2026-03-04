#!/usr/bin/env python3
"""Deterministic ARCH-REF-2 semantic impact planner using topology artifacts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Iterable, List, Set, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


DEFAULT_TOPOLOGY_MAP_REL = "docs/audit/TOPOLOGY_MAP.json"

SCHEMA_ROOT_PREFIXES = ("schema/", "schemas/")
REGISTRY_ROOT_PREFIXES = ("data/registries/", "data/governance/")

CONTROL_PLANE_PREFIXES = (
    "src/net/",
    "tools/xstack/sessionx/",
    "tools/xstack/controlx/",
    "tools/xstack/run.py",
    "src/control/",
)
CTRL_MODULE_PREFIXES = (
    "src/control/",
)
CONTROL_PLANE_MODULE_NODE_ID = "module:src/control/control_plane_engine.py"
CONTROL_DEPENDENCY_SCAN_TOKENS = (
    "from src.control",
    "import src.control",
    "src.control.",
    "build_control_intent(",
    "build_control_resolution(",
)
NETWORKGRAPH_FLOW_PREFIXES = (
    "src/core/graph/",
    "src/core/flow/",
    "src/logistics/",
    "src/interior/",
    "src/mobility/",
)
EPISTEMIC_PREFIXES = (
    "src/inspection/",
    "src/interior/",
    "src/client/interaction/",
    "tools/xstack/sessionx/observation.py",
    "docs/architecture/lens_system.md",
    "docs/architecture/EPISTEMICS_MODEL.md",
)

SUITE_TO_TEST_IDS = {
    "suite.contract.registry_hard_gate": (
        "test_all_domains_have_tier_contract",
        "test_all_couplings_declared",
        "test_all_explain_contracts_present",
        "test_contract_schema_valid",
    ),
    "suite.contract.explain_engine": (
        "test_explain_artifact_deterministic",
        "test_explain_redaction_policy",
        "test_explain_artifact_generation_smoke",
    ),
    "suite.contract.tier_envelope": (
        "test_cost_envelope_never_exceeded",
        "test_T1_to_T0_downgrade_logged",
        "test_fluid_degradation_order_deterministic",
    ),
    "suite.compatx.strict": (
        "testx.compatx.schema_validate",
        "testx.lockfile.validate",
    ),
    "suite.registry.compile": (
        "testx.registry.compile",
        "testx.lockfile.validate",
    ),
    "suite.multiplayer.determinism_envelope": (
        "test_determinism_envelope_full_stack",
        "testx.net.mp_authoritative_full_stack",
        "testx.net.mp_lockstep_full_stack",
        "testx.net.mp_srz_hybrid_full_stack",
    ),
    "suite.networkgraph_flow.regression": (
        "testx.core.network_graph_deterministic_ordering",
        "testx.core.flow_engine_capacity_delay_loss_deterministic",
        "testx.materials.logistics_route_equivalence",
        "testx.materials.logistics_migration_behavior_equivalence",
        "testx.interior.volume_connectivity_deterministic",
    ),
    "suite.epistemic.lod_invariance": (
        "testx.civilisation.lod_invariance_population_size",
        "testx.materials.epistemic_no_leak_outside_roi",
        "testx.interior.epistemic_redaction_of_values",
        "testx.interior.no_truth_access_in_instruments",
    ),
    "suite.rs5.arbitration": (
        "testx.materials.multiplayer_equal_share_arbitration",
        "testx.materials.multiplayer_inspection_fairness",
        "testx.performance.arbitration_equal_share",
        "testx.performance.multiplayer_fairness_under_spread_players",
        "testx.reality.multiplayer_distributed_players_arbitration",
    ),
    "suite.replay.reenactment": (
        "testx.materials.reenactment_deterministic_hash",
        "testx.materials.reenactment_budget_degrades",
        "testx.materials.reenactment_seed_reproducible",
        "testx.srz.hash_anchor_replay",
        "testx.time.compaction_preserves_replay",
    ),
    "suite.fidelity.regression": (
        "test_fidelity_deterministic_allocation",
        "test_fidelity_downgrade_micro_to_meso",
        "test_cost_envelope_never_exceeded",
    ),
    "suite.domain.elec": (
        "test_power_flow_deterministic",
        "test_loss_to_heat_applied",
        "test_overtemp_trip",
    ),
    "suite.domain.therm": (
        "test_conduction_deterministic",
        "test_heat_capacity_updates",
        "test_overheat_when_no_cooling",
    ),
    "suite.domain.mob": (
        "test_free_motion_deterministic",
        "test_velocity_derived_from_momentum",
        "test_impulse_updates_momentum_deterministic",
    ),
    "suite.domain.sig": (
        "test_message_delivery_deterministic",
        "test_trust_update_deterministic",
        "test_receipt_created_only_on_delivery",
    ),
    "suite.domain.phys": (
        "test_energy_conservation_enforced",
        "test_entropy_increment_deterministic",
        "test_field_sampling_deterministic",
    ),
    "suite.domain.field": (
        "test_field_sampling_deterministic",
        "test_field_update_policy_respected",
        "test_gravity_force_model_applies",
    ),
    "suite.domain.mech": (
        "test_fracture_trigger",
        "test_stress_ratio_calculation",
        "test_plastic_strain_accumulates",
    ),
    "suite.domain.fluid": (
        "test_fluid_profiles_registry_valid",
        "test_fluid_null_boot_ok",
        "test_fluid_contracts_present",
    ),
}

DOMAIN_TO_SUITE_IDS = {
    "ELEC": "suite.domain.elec",
    "THERM": "suite.domain.therm",
    "MOB": "suite.domain.mob",
    "SIG": "suite.domain.sig",
    "PHYS": "suite.domain.phys",
    "FIELD": "suite.domain.field",
    "MECH": "suite.domain.mech",
    "FLUID": "suite.domain.fluid",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _run_git(repo_root: str, argv: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return 127, ""
    return int(proc.returncode), str(proc.stdout or "")


def _detect_changed_files(repo_root: str, explicit: Iterable[str]) -> List[str]:
    rows = [_norm(token) for token in explicit if _norm(token)]
    if rows:
        return sorted(set(rows))

    detected: List[str] = []
    code, out = _run_git(repo_root, ["git", "diff", "--name-only", "--diff-filter=ACMR", "origin/main...HEAD"])
    if code == 0:
        for line in str(out).splitlines():
            token = _norm(line)
            if token:
                detected.append(token)
    status_code, status_out = _run_git(repo_root, ["git", "status", "--porcelain", "-uall"])
    if status_code == 0:
        for line in str(status_out).splitlines():
            token = _norm(line[3:] if len(line) >= 3 else line)
            if token:
                detected.append(token)
    return sorted(set(detected))


def _topology_declarations(topology_payload: dict) -> Dict[str, Dict[str, str]]:
    declared: Dict[str, Dict[str, str]] = {
        "module": {},
        "schema": {},
        "registry": {},
        "tool": {},
        "process_family": {},
        "contract_set": {},
        "policy_set": {},
    }
    for node in list(topology_payload.get("nodes") or []):
        if not isinstance(node, dict):
            continue
        node_kind = str(node.get("node_kind", "")).strip()
        path = _norm(str(node.get("path") or ""))
        owner = str(node.get("owner_subsystem", "")).strip()
        node_id = str(node.get("node_id", "")).strip()
        if not node_kind or node_kind not in declared:
            continue
        if path:
            declared[node_kind][path] = owner or node_id
    return declared


def _suite_required_for_path(path: str) -> Set[str]:
    out: Set[str] = set()
    rel = _norm(path)
    if rel.startswith(SCHEMA_ROOT_PREFIXES):
        out.add("suite.compatx.strict")
    if rel.startswith(REGISTRY_ROOT_PREFIXES):
        out.add("suite.registry.compile")
    if rel.startswith(CONTROL_PLANE_PREFIXES):
        out.add("suite.multiplayer.determinism_envelope")
    if rel.startswith(CTRL_MODULE_PREFIXES):
        out.add("suite.rs5.arbitration")
        out.add("suite.replay.reenactment")
        out.add("suite.fidelity.regression")
    if rel.startswith(NETWORKGRAPH_FLOW_PREFIXES):
        out.add("suite.networkgraph_flow.regression")
    if rel.startswith(EPISTEMIC_PREFIXES):
        out.add("suite.epistemic.lod_invariance")
    return out


def _docs_required_for_path(path: str) -> Set[str]:
    out: Set[str] = set()
    rel = _norm(path)
    if rel.startswith(SCHEMA_ROOT_PREFIXES):
        out.add("docs/architecture/SCHEMA_CHANGE_NOTES.md")
    if rel.startswith(REGISTRY_ROOT_PREFIXES):
        out.add("docs/architecture/registry_compile.md")
    if rel.startswith("data/governance/"):
        out.add("docs/architecture/DEPRECATION_LIFECYCLE.md")
    if rel.startswith(CONTROL_PLANE_PREFIXES):
        out.add("docs/net/MP_VALIDATION_BASELINE.md")
    if rel.startswith(NETWORKGRAPH_FLOW_PREFIXES):
        out.add("docs/architecture/CORE_ABSTRACTIONS.md")
    if rel.startswith(EPISTEMIC_PREFIXES):
        out.add("docs/architecture/EPISTEMICS_MODEL.md")
    return out


def _migration_checks_for_path(path: str) -> Set[str]:
    out: Set[str] = set()
    rel = _norm(path)
    if rel.startswith(SCHEMA_ROOT_PREFIXES):
        out.add("check.compatx.schema_semver_route")
    if rel.startswith(REGISTRY_ROOT_PREFIXES):
        out.add("check.registry_compile_lockfile_refresh")
    if rel.startswith("data/governance/"):
        out.add("check.deprecation_registry_validation")
    if rel.startswith(CONTROL_PLANE_PREFIXES):
        out.add("check.multiplayer_determinism_envelope")
    if rel.startswith(NETWORKGRAPH_FLOW_PREFIXES):
        out.add("check.cross_domain_flow_equivalence")
    if rel.startswith(EPISTEMIC_PREFIXES):
        out.add("check.ed4_lod_invariance")
    return out


def _meta_contract_suites_for_path(repo_root: str, path: str) -> Set[str]:
    out: Set[str] = set()
    rel = _norm(path)
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    record = dict(payload.get("record") or {}) if isinstance(payload, dict) else {}

    if rel == "data/registries/tier_contract_registry.json":
        out.add("suite.contract.registry_hard_gate")
        out.add("suite.contract.tier_envelope")
        rows = list(record.get("tier_contracts") or payload.get("tier_contracts") or [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            subsystem_id = str(row.get("subsystem_id", "")).strip().upper()
            suite_id = DOMAIN_TO_SUITE_IDS.get(subsystem_id, "")
            if suite_id:
                out.add(suite_id)
        return out

    if rel == "data/registries/coupling_contract_registry.json":
        out.add("suite.contract.registry_hard_gate")
        rows = list(record.get("coupling_contracts") or payload.get("coupling_contracts") or [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in ("from_domain_id", "to_domain_id"):
                domain_id = str(row.get(key, "")).strip().upper()
                suite_id = DOMAIN_TO_SUITE_IDS.get(domain_id, "")
                if suite_id:
                    out.add(suite_id)
        return out

    if rel == "data/registries/explain_contract_registry.json":
        out.add("suite.contract.registry_hard_gate")
        out.add("suite.contract.explain_engine")
        rows = list(record.get("explain_contracts") or payload.get("explain_contracts") or [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            event_kind_id = str(row.get("event_kind_id", "")).strip().lower()
            domain_id = str(event_kind_id.split(".", 1)[0] if event_kind_id else "").strip().upper()
            suite_id = DOMAIN_TO_SUITE_IDS.get(domain_id, "")
            if suite_id:
                out.add(suite_id)
        return out

    return out


def _subsystems_for_paths(paths: Iterable[str], topology_payload: dict) -> List[str]:
    declarations = _topology_declarations(topology_payload)
    module_map = dict(declarations.get("module") or {})
    out: Set[str] = set()
    for raw in paths:
        rel = _norm(raw)
        if not rel:
            continue
        if rel in module_map:
            out.add(str(module_map.get(rel, "")).strip() or rel)
            continue
        if rel.startswith("src/"):
            parts = rel.split("/")
            if len(parts) >= 2 and parts[1]:
                out.add(parts[1])
            continue
        top = rel.split("/", 1)[0]
        if top:
            out.add(top)
    return sorted(out)


def _control_dependency_node_ids(topology_payload: dict) -> Set[str]:
    edges = list(topology_payload.get("edges") or [])
    out: Set[str] = set()
    for row in edges:
        if not isinstance(row, dict):
            continue
        if str(row.get("edge_kind", "")).strip() not in ("depends_on", "consumes"):
            continue
        if str(row.get("to_node_id", "")).strip() != CONTROL_PLANE_MODULE_NODE_ID:
            continue
        from_node_id = str(row.get("from_node_id", "")).strip()
        if from_node_id:
            out.add(from_node_id)
    return out


def _module_node_id_for_path(path: str, topology_payload: dict) -> str:
    rel = _norm(path)
    if not rel:
        return ""
    nodes = list(topology_payload.get("nodes") or [])
    module_rows: List[Tuple[str, str]] = []
    for row in nodes:
        if not isinstance(row, dict):
            continue
        if str(row.get("node_kind", "")).strip() != "module":
            continue
        node_id = str(row.get("node_id", "")).strip()
        module_path = _norm(str(row.get("path") or ""))
        if not node_id or not module_path:
            continue
        module_rows.append((module_path, node_id))
    module_rows = sorted(module_rows, key=lambda item: len(str(item[0])), reverse=True)
    for module_path, node_id in module_rows:
        if rel == module_path or rel.startswith(module_path + "/"):
            return str(node_id)
    return ""


def compute_semantic_impact(
    *,
    repo_root: str,
    changed_files: Iterable[str],
    topology_map_payload: dict,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    changed = sorted(set(_norm(path) for path in changed_files if _norm(path)))

    topology_id = str(topology_map_payload.get("topology_id", "")).strip()
    topology_nodes = list(topology_map_payload.get("nodes") or [])
    topology_edges = list(topology_map_payload.get("edges") or [])
    topology_ok = bool(topology_id and isinstance(topology_nodes, list) and isinstance(topology_edges, list))

    uncertainty_reasons: List[str] = []
    if not topology_ok:
        uncertainty_reasons.append("topology_map_missing_or_invalid")

    declarations = _topology_declarations(topology_map_payload) if topology_ok else {}
    declared_schema_paths = set((declarations.get("schema") or {}).keys())
    declared_registry_paths = set((declarations.get("registry") or {}).keys())
    declared_control_dependency_nodes = _control_dependency_node_ids(topology_map_payload) if topology_ok else set()

    impacted_subsystems = _subsystems_for_paths(changed, topology_map_payload if topology_ok else {})
    required_test_suites: Set[str] = set()
    required_docs_updates: Set[str] = set()
    required_migration_checks: Set[str] = set()

    strict_required = False
    for rel in changed:
        suites = _suite_required_for_path(rel)
        required_test_suites.update(suites)
        required_test_suites.update(_meta_contract_suites_for_path(repo_root, rel))
        required_docs_updates.update(_docs_required_for_path(rel))
        required_migration_checks.update(_migration_checks_for_path(rel))
        if rel in {
            "data/registries/tier_contract_registry.json",
            "data/registries/coupling_contract_registry.json",
            "data/registries/explain_contract_registry.json",
        }:
            required_docs_updates.add("docs/meta/TIER_COUPLING_EXPLAIN_CONTRACTS.md")
            required_migration_checks.add("check.meta_contract_registry_consistency")
        if rel.startswith(SCHEMA_ROOT_PREFIXES):
            strict_required = True
            if topology_ok and rel not in declared_schema_paths:
                uncertainty_reasons.append("undeclared_schema:{}".format(rel))
        if rel.startswith(REGISTRY_ROOT_PREFIXES):
            if topology_ok and rel not in declared_registry_paths:
                uncertainty_reasons.append("undeclared_registry:{}".format(rel))
        if rel.startswith("src/") and not rel.startswith("src/control/"):
            rel_abs = os.path.join(repo_root, rel.replace("/", os.sep))
            lowered_text = _read_text(rel_abs).lower()
            if lowered_text and any(token in lowered_text for token in CONTROL_DEPENDENCY_SCAN_TOKENS):
                required_migration_checks.add("check.topology.control_dependency_declaration")
                module_node_id = _module_node_id_for_path(rel, topology_map_payload if topology_ok else {})
                if not module_node_id:
                    uncertainty_reasons.append("control_dependency_module_undeclared:{}".format(rel))
                elif module_node_id not in declared_control_dependency_nodes:
                    uncertainty_reasons.append("missing_control_dependency_declaration:{}".format(rel))

    required_test_ids: Set[str] = set()
    for suite_id in sorted(required_test_suites):
        required_test_ids.update(set(SUITE_TO_TEST_IDS.get(suite_id, ())))

    required_verification_level = "STRICT" if strict_required else "FAST"
    if uncertainty_reasons:
        required_verification_level = "STRICT"

    impacted_subsystems_sorted = sorted(set(impacted_subsystems))
    required_test_suites_sorted = sorted(set(required_test_suites))
    required_test_ids_sorted = sorted(set(required_test_ids))
    required_docs_updates_sorted = sorted(set(required_docs_updates))
    required_migration_checks_sorted = sorted(set(required_migration_checks))
    uncertainty_sorted = sorted(set(str(reason).strip() for reason in uncertainty_reasons if str(reason).strip()))

    payload = {
        "result": "complete",
        "tool_id": "tool.governance.tool_semantic_impact",
        "topology_id": topology_id or "missing",
        "topology_node_count": len(topology_nodes) if isinstance(topology_nodes, list) else 0,
        "topology_edge_count": len(topology_edges) if isinstance(topology_edges, list) else 0,
        "changed_files": changed,
        "impacted_subsystems": impacted_subsystems_sorted,
        "required_test_suites": required_test_suites_sorted,
        "required_test_ids": required_test_ids_sorted,
        "required_docs_updates": required_docs_updates_sorted,
        "required_migration_checks": required_migration_checks_sorted,
        "required_verification_level": required_verification_level,
        "requires_strict_fallback": bool(required_verification_level == "STRICT"),
        "uncertainty_reasons": uncertainty_sorted,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    fingerprint_payload = dict(payload)
    fingerprint_payload["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(fingerprint_payload)
    return payload


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute deterministic semantic impact requirements from changed files.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--topology-map", default=DEFAULT_TOPOLOGY_MAP_REL)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else REPO_ROOT_HINT
    topology_map_rel = _norm(str(args.topology_map or DEFAULT_TOPOLOGY_MAP_REL)) or DEFAULT_TOPOLOGY_MAP_REL
    topology_map_abs = os.path.join(repo_root, topology_map_rel.replace("/", os.sep))
    topology_payload = _read_json(topology_map_abs)

    changed_files = _detect_changed_files(repo_root, list(args.changed_file or []))
    result = compute_semantic_impact(
        repo_root=repo_root,
        changed_files=changed_files,
        topology_map_payload=topology_payload,
    )

    out_rel = _norm(str(args.out or "")).strip()
    if out_rel:
        out_abs = os.path.join(repo_root, out_rel.replace("/", os.sep))
        _write_json(out_abs, result)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
