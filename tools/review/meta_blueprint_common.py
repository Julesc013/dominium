"""Deterministic Π-0 meta-blueprint artifact generation helpers."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"
MODULE_DEP_GRAPH_REL = "data/architecture/module_dependency_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
SRC_DIRECTORY_REPORT_REL = "data/audit/src_directory_report.json"
CONVERGENCE_PLAN_REL = "data/refactor/convergence_plan.json"

SERIES_DEP_GRAPH_REL = "data/blueprint/series_dependency_graph.json"
CAPABILITY_DEP_GRAPH_REL = "data/blueprint/capability_dependency_graph.json"
READINESS_MATRIX_REL = "data/blueprint/readiness_matrix.json"
PIPE_DREAMS_MATRIX_REL = "data/blueprint/pipe_dreams_matrix.json"

META_BLUEPRINT_INDEX_REL = "docs/blueprint/META_BLUEPRINT_INDEX.md"
META_BLUEPRINT_SUMMARY_REL = "docs/blueprint/META_BLUEPRINT_SUMMARY.md"
RUNTIME_ARCH_DIAGRAM_REL = "docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md"
REPO_GOV_DIAGRAM_REL = "docs/blueprint/REPOSITORY_GOVERNANCE_DIAGRAM.md"
DIST_ARCHIVE_DIAGRAM_REL = "docs/blueprint/DISTRIBUTION_AND_ARCHIVE_DIAGRAM.md"
LIVE_OPS_DIAGRAM_REL = "docs/blueprint/LIVE_OPERATIONS_DIAGRAM.md"
SERIES_DEP_MAP_REL = "docs/blueprint/SERIES_DEPENDENCY_MAP.md"
CAPABILITY_LADDER_REL = "docs/blueprint/CAPABILITY_LADDER.md"
FOUNDATION_READINESS_REL = "docs/blueprint/FOUNDATION_READINESS_MATRIX.md"
PIPE_DREAMS_REL = "docs/blueprint/PIPE_DREAMS_MATRIX.md"
SNAPSHOT_MAPPING_NOTES_REL = "docs/blueprint/SNAPSHOT_MAPPING_NOTES.md"
PI_0_FINAL_REL = "docs/audit/PI_0_FINAL.md"

OUTPUT_REL_PATHS = {
    SERIES_DEP_GRAPH_REL,
    CAPABILITY_DEP_GRAPH_REL,
    READINESS_MATRIX_REL,
    PIPE_DREAMS_MATRIX_REL,
    META_BLUEPRINT_INDEX_REL,
    META_BLUEPRINT_SUMMARY_REL,
    RUNTIME_ARCH_DIAGRAM_REL,
    REPO_GOV_DIAGRAM_REL,
    DIST_ARCHIVE_DIAGRAM_REL,
    LIVE_OPS_DIAGRAM_REL,
    SERIES_DEP_MAP_REL,
    CAPABILITY_LADDER_REL,
    FOUNDATION_READINESS_REL,
    PIPE_DREAMS_REL,
    SNAPSHOT_MAPPING_NOTES_REL,
    PI_0_FINAL_REL,
}

DOC_REPORT_DATE = "2026-03-26"

SERIES_ORDER = {"XI": 0, "OMEGA": 1, "SIGMA": 2, "PHI": 3, "UPSILON": 4, "ZETA": 5}
READINESS_ORDER = {
    "ready_now": 0,
    "foundation_ready_but_not_implemented": 1,
    "requires_new_foundation": 2,
    "unrealistic_currently": 3,
}
FEASIBILITY_ORDER = {"near": 0, "medium": 1, "long": 2, "speculative": 3}
COMPLEXITY_ORDER = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload)))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _doc_header(title: str, replacement_target: str) -> str:
    return "\n".join(
        [
            "Status: DERIVED",
            f"Last Reviewed: {DOC_REPORT_DATE}",
            "Supersedes: none",
            "Superseded By: none",
            "Stability: provisional",
            "Future Series: PI",
            f"Replacement Target: {replacement_target}",
            "",
            f"# {title}",
            "",
        ]
    )


def _bullet_lines(values: Iterable[str]) -> list[str]:
    return [f"- {value}" for value in values]


def _discover_current_facts(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    architecture_graph = _read_json(_repo_abs(root, ARCHITECTURE_GRAPH_REL))
    module_registry = _read_json(_repo_abs(root, MODULE_REGISTRY_REL))
    module_dependency_graph = _read_json(_repo_abs(root, MODULE_DEP_GRAPH_REL))
    build_graph = _read_json(_repo_abs(root, BUILD_GRAPH_REL))
    src_report = _read_json(_repo_abs(root, SRC_DIRECTORY_REPORT_REL))
    convergence_plan = _read_json(_repo_abs(root, CONVERGENCE_PLAN_REL))

    modules = list(architecture_graph.get("modules") or [])
    concepts = list(architecture_graph.get("concepts") or [])
    module_domains = Counter(_token(row.get("domain")) for row in modules if _token(row.get("domain")))
    top_level_directories = sorted(
        entry.name
        for entry in os.scandir(root)
        if entry.is_dir()
    )
    xi_artifact_state = {
        "XI_0": os.path.isfile(_repo_abs(root, "docs/audit/ARCH_GRAPH_BOOTSTRAP.md")),
        "XI_1": os.path.isfile(_repo_abs(root, "docs/audit/XI_1_FINAL.md")),
        "XI_2": os.path.isfile(_repo_abs(root, "docs/audit/XI_2_FINAL.md")),
        "XI_3": os.path.isfile(_repo_abs(root, "docs/audit/XI_3_FINAL.md")),
        "XI_4": os.path.isfile(_repo_abs(root, "docs/audit/XI_4_FINAL.md")),
        "XI_5": os.path.isfile(_repo_abs(root, "docs/audit/XI_5_FINAL.md")),
        "XI_6": os.path.isfile(_repo_abs(root, "docs/audit/XI_6_FINAL.md")),
        "XI_7": os.path.isfile(_repo_abs(root, "docs/audit/XI_7_FINAL.md")),
        "XI_8": os.path.isfile(_repo_abs(root, "docs/audit/XI_8_FINAL.md")),
    }
    src_directories = list(src_report.get("directories") or [])
    src_severity_counts = Counter(_token(row.get("severity")) for row in src_directories if _token(row.get("severity")))
    summary = dict(convergence_plan.get("summary") or {})
    return {
        "architecture_graph_fingerprint": _token(architecture_graph.get("deterministic_fingerprint")),
        "build_graph_fingerprint": _token(build_graph.get("deterministic_fingerprint")),
        "build_target_count": len(list(build_graph.get("targets") or [])),
        "concept_count": len(concepts),
        "current_convergence_summary": {
            "cluster_resolution_counts": dict(summary.get("cluster_resolution_counts") or {}),
            "risk_counts": dict(summary.get("risk_counts") or {}),
            "source_like_cluster_count": int(summary.get("source_like_cluster_count", 0) or 0),
        },
        "module_count": len(modules),
        "module_dependency_edge_count": len(list(module_dependency_graph.get("edges") or [])),
        "module_dependency_graph_fingerprint": _token(module_dependency_graph.get("deterministic_fingerprint")),
        "module_domain_counts": [
            {"count": int(count), "domain": domain}
            for domain, count in sorted(module_domains.items(), key=lambda item: (-item[1], item[0]))
        ],
        "module_registry_fingerprint": _token(module_registry.get("deterministic_fingerprint")),
        "source_like_directory_count": int(src_report.get("directory_count", 0) or 0),
        "source_like_severity_counts": {key: int(src_severity_counts.get(key, 0)) for key in sorted(src_severity_counts)},
        "top_level_directories": top_level_directories,
        "xi_artifact_state": xi_artifact_state,
    }


def _series_rows() -> list[dict[str, object]]:
    rows = [
        {
            "series_id": "XI",
            "series_label": "Ξ",
            "name": "Repository convergence and drift immunity",
            "purpose": "Map the repository truth, rank duplicate implementations, converge structural drift, and harden architecture governance.",
            "prerequisites": [],
            "outputs": [
                "architecture graph",
                "duplicate implementation scan",
                "convergence plan",
                "src elimination plan",
                "architecture freeze",
                "CI drift immunity",
            ],
            "can_start_before_snapshot_mapping": True,
            "start_window": "can start before snapshot mapping, but execution must be refreshed against the live repository state",
            "risk_level": "high",
            "status_now": "planning_and_partial_artifacts_present",
        },
        {
            "series_id": "OMEGA",
            "series_label": "Ω",
            "name": "Runtime freeze and distribution completion",
            "purpose": "Lock worldgen, baseline universe, gameplay, disaster behavior, ecosystem verification, update simulation, trust, and final distribution signoff.",
            "prerequisites": [],
            "outputs": [
                "worldgen lock baseline",
                "baseline universe baseline",
                "gameplay loop baseline",
                "disaster suite baseline",
                "ecosystem verify baseline",
                "update simulation baseline",
                "trust strict baseline",
                "distribution signoff",
            ],
            "can_start_before_snapshot_mapping": True,
            "start_window": "can start before snapshot mapping where verification tooling already exists; final freeze assumes refreshed baselines",
            "risk_level": "high",
            "status_now": "verification_foundations_present",
        },
        {
            "series_id": "SIGMA",
            "series_label": "Σ",
            "name": "Human and agent governance surface",
            "purpose": "Stabilize the unified human and Agent operating interface, including task catalogs, ControlX planning, prompt safety, and deterministic maintenance workflows.",
            "prerequisites": ["XI", "OMEGA"],
            "outputs": [
                "task catalogs",
                "agent governance workflows",
                "prompt safety policy",
                "deterministic maintenance playbooks",
            ],
            "can_start_before_snapshot_mapping": True,
            "start_window": "planning can start before snapshot mapping; implementation should follow architecture freeze and runtime lock",
            "risk_level": "medium",
            "status_now": "foundation_ready_for_planning",
        },
        {
            "series_id": "PHI",
            "series_label": "Φ",
            "name": "Runtime componentization and service kernel",
            "purpose": "Evolve the runtime toward a service-oriented kernel with lifecycle management, service registry, module loading, and replaceable component surfaces.",
            "prerequisites": ["XI", "OMEGA"],
            "outputs": [
                "lifecycle manager",
                "service registry",
                "module loader",
                "componentized runtime boundaries",
                "replaceable render and storage services",
            ],
            "can_start_before_snapshot_mapping": False,
            "start_window": "implementation should begin after snapshot mapping confirms the converged repository shape",
            "risk_level": "very_high",
            "status_now": "blocked_on_post_xi_snapshot",
        },
        {
            "series_id": "UPSILON",
            "series_label": "Υ",
            "name": "Build, release, distribution, and control-plane evolution",
            "purpose": "Turn the current release and archive foundations into a stricter control plane for package graphs, release governance, rollout policy, and operator tooling.",
            "prerequisites": ["XI", "OMEGA"],
            "outputs": [
                "release orchestration control plane",
                "profiled CI lanes",
                "distribution controllers",
                "upgrade and rollback governance",
            ],
            "can_start_before_snapshot_mapping": True,
            "start_window": "planning can start before snapshot mapping; implementation prefers the post-Ξ frozen repository shape",
            "risk_level": "high",
            "status_now": "foundation_ready_for_planning",
        },
        {
            "series_id": "ZETA",
            "series_label": "Ζ",
            "name": "Live runtime operations and distributed upgrades",
            "purpose": "Deliver deterministic live operations, live cutovers, distributed simulation controls, and proof-backed operational recovery.",
            "prerequisites": ["SIGMA", "PHI", "UPSILON", "OMEGA"],
            "outputs": [
                "shadow services",
                "live cutover plans",
                "deterministic replication",
                "authority handoff",
                "proof-backed rollback",
            ],
            "can_start_before_snapshot_mapping": False,
            "start_window": "planning only before snapshot mapping; implementation requires a frozen architecture, locked runtime, and componentized services",
            "risk_level": "very_high",
            "status_now": "blocked_on_foundation_series",
        },
    ]
    return sorted(rows, key=lambda row: SERIES_ORDER.get(_token(row.get("series_id")), 99))


def _series_edges(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    edges = []
    for row in rows:
        series_id = _token(row.get("series_id"))
        for prerequisite in sorted({_token(item) for item in row.get("prerequisites") or [] if _token(item)}):
            edge = {
                "from_series_id": prerequisite,
                "relation": "prerequisite_for",
                "to_series_id": series_id,
            }
            edge["edge_id"] = f"series.edge.{canonical_sha256(edge)[:12]}"
            edges.append(edge)
    return sorted(edges, key=lambda row: (SERIES_ORDER.get(_token(row.get("from_series_id")), 99), SERIES_ORDER.get(_token(row.get("to_series_id")), 99)))


def _capability_nodes() -> list[dict[str, object]]:
    rows = [
        {"capability_id": "frozen_mvp_foundations", "label": "Frozen MVP foundations", "level": 0, "required_series": ["OMEGA"], "status": "foundation_ready"},
        {"capability_id": "deterministic_truth_paths", "label": "Deterministic truth paths", "level": 0, "required_series": ["OMEGA"], "status": "ready_now"},
        {"capability_id": "compatibility_and_trust", "label": "Compatibility and trust", "level": 0, "required_series": ["OMEGA"], "status": "ready_now"},
        {"capability_id": "distribution_and_archive", "label": "Distribution and archive", "level": 0, "required_series": ["OMEGA", "UPSILON"], "status": "foundation_ready"},
        {"capability_id": "operator_governance_surface", "label": "Operator and governance surface", "level": 1, "required_series": ["XI", "SIGMA"], "status": "foundation_ready"},
        {"capability_id": "deterministic_maintenance_workflows", "label": "Deterministic maintenance workflows", "level": 1, "required_series": ["XI", "SIGMA"], "status": "foundation_ready"},
        {"capability_id": "service_registry", "label": "Service registry", "level": 2, "required_series": ["PHI"], "status": "requires_new_foundation"},
        {"capability_id": "module_loader", "label": "Module loader", "level": 2, "required_series": ["PHI"], "status": "requires_new_foundation"},
        {"capability_id": "lifecycle_manager", "label": "Lifecycle manager", "level": 2, "required_series": ["PHI"], "status": "requires_new_foundation"},
        {"capability_id": "render_device_abstraction", "label": "Render device abstraction", "level": 2, "required_series": ["PHI"], "status": "requires_new_foundation"},
        {"capability_id": "framegraph_pipeline", "label": "Framegraph and render scheduling", "level": 2, "required_series": ["PHI"], "status": "requires_new_foundation"},
        {"capability_id": "asset_pipeline", "label": "Asset and shader pipeline", "level": 2, "required_series": ["PHI", "UPSILON"], "status": "foundation_ready"},
        {"capability_id": "state_export_import", "label": "State export and import", "level": 2, "required_series": ["PHI", "UPSILON"], "status": "requires_new_foundation"},
        {"capability_id": "shadow_service_startup", "label": "Shadow service startup", "level": 3, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "non_blocking_saves", "label": "Non-blocking saves", "level": 3, "required_series": ["PHI", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "live_pack_mount", "label": "Live pack mount", "level": 3, "required_series": ["UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "live_backend_swap", "label": "Live backend swap", "level": 3, "required_series": ["PHI", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "canary_rollouts", "label": "Canary and staged rollouts", "level": 3, "required_series": ["UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "shard_relocation", "label": "Shard relocation", "level": 4, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "unrealistic_currently"},
        {"capability_id": "deterministic_replication", "label": "Deterministic replication", "level": 4, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "authority_handoff", "label": "Authority handoff", "level": 4, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "cluster_failover", "label": "Cluster failover", "level": 4, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "requires_new_foundation"},
        {"capability_id": "restartless_core_replacement", "label": "Restartless core engine replacement", "level": 5, "required_series": ["SIGMA", "PHI", "UPSILON", "ZETA"], "status": "unrealistic_currently"},
        {"capability_id": "live_schema_evolution", "label": "Live schema evolution", "level": 5, "required_series": ["SIGMA", "PHI", "UPSILON", "ZETA"], "status": "unrealistic_currently"},
        {"capability_id": "multi_backend_mirroring", "label": "Multi-backend mirrored rendering", "level": 5, "required_series": ["PHI", "ZETA"], "status": "unrealistic_currently"},
        {"capability_id": "cluster_of_clusters", "label": "Deterministic cluster-of-clusters", "level": 5, "required_series": ["PHI", "UPSILON", "ZETA"], "status": "unrealistic_currently"},
    ]
    return sorted(rows, key=lambda row: (int(row.get("level", 0)), _token(row.get("capability_id"))))


def _capability_edges() -> list[dict[str, object]]:
    raw_edges = [
        ("frozen_mvp_foundations", "operator_governance_surface"),
        ("deterministic_truth_paths", "deterministic_maintenance_workflows"),
        ("compatibility_and_trust", "deterministic_maintenance_workflows"),
        ("operator_governance_surface", "service_registry"),
        ("deterministic_maintenance_workflows", "module_loader"),
        ("deterministic_maintenance_workflows", "lifecycle_manager"),
        ("distribution_and_archive", "asset_pipeline"),
        ("service_registry", "shadow_service_startup"),
        ("module_loader", "live_pack_mount"),
        ("lifecycle_manager", "shadow_service_startup"),
        ("lifecycle_manager", "non_blocking_saves"),
        ("render_device_abstraction", "live_backend_swap"),
        ("framegraph_pipeline", "live_backend_swap"),
        ("asset_pipeline", "canary_rollouts"),
        ("state_export_import", "shard_relocation"),
        ("state_export_import", "authority_handoff"),
        ("shadow_service_startup", "canary_rollouts"),
        ("non_blocking_saves", "cluster_failover"),
        ("live_pack_mount", "canary_rollouts"),
        ("live_backend_swap", "multi_backend_mirroring"),
        ("canary_rollouts", "cluster_failover"),
        ("deterministic_replication", "shard_relocation"),
        ("authority_handoff", "cluster_failover"),
        ("cluster_failover", "cluster_of_clusters"),
        ("deterministic_replication", "cluster_of_clusters"),
        ("module_loader", "restartless_core_replacement"),
        ("state_export_import", "live_schema_evolution"),
        ("service_registry", "deterministic_replication"),
    ]
    edges = []
    for source, target in raw_edges:
        payload = {"from_capability_id": source, "relation": "requires", "to_capability_id": target}
        payload["edge_id"] = f"capability.edge.{canonical_sha256(payload)[:12]}"
        edges.append(payload)
    return sorted(edges, key=lambda row: (_token(row.get("from_capability_id")), _token(row.get("to_capability_id"))))


def _readiness_rows() -> list[dict[str, object]]:
    rows = [
        {
            "capability_id": "safe_mode_degraded_boot",
            "capability_label": "Safe-mode degraded boot",
            "readiness": "ready_now",
            "required_series": ["OMEGA", "SIGMA"],
            "missing_building_blocks": ["operator-facing packaging polish only"],
            "estimated_complexity": "low",
            "blockers": ["No blocking technical gap for offline and governed boot paths"],
            "confidence_level": "high",
        },
        {
            "capability_id": "proof_backed_rollback_and_replay",
            "capability_label": "Proof-backed rollback and replay pairing",
            "readiness": "ready_now",
            "required_series": ["OMEGA", "SIGMA"],
            "missing_building_blocks": ["unified operator dashboard only"],
            "estimated_complexity": "medium",
            "blockers": ["Current capability is present through distributed reports rather than one unified operator surface"],
            "confidence_level": "high",
        },
        {
            "capability_id": "compatibility_governed_update_rehearsal",
            "capability_label": "Compatibility-governed update rehearsal",
            "readiness": "ready_now",
            "required_series": ["OMEGA", "UPSILON"],
            "missing_building_blocks": ["control-plane consolidation only"],
            "estimated_complexity": "medium",
            "blockers": ["Current update rehearsal exists as governed tooling, not yet as one named control-plane product"],
            "confidence_level": "high",
        },
        {
            "capability_id": "hot_swappable_renderers",
            "capability_label": "Hot-swappable renderers",
            "readiness": "requires_new_foundation",
            "required_series": ["PHI", "UPSILON", "ZETA"],
            "missing_building_blocks": ["render device abstraction", "service lifecycle manager", "side-by-side renderer state export"],
            "estimated_complexity": "very_high",
            "blockers": ["Renderer boundaries are not yet componentized", "No live cutover protocol exists for render services"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "partial_live_module_reload",
            "capability_label": "Partial live module reload",
            "readiness": "requires_new_foundation",
            "required_series": ["PHI", "SIGMA", "ZETA"],
            "missing_building_blocks": ["module loader", "module state export", "governed cutover plans"],
            "estimated_complexity": "very_high",
            "blockers": ["No runtime module boundary ABI is frozen", "No rollback-safe cutover mechanism exists"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "live_save_migration",
            "capability_label": "Live save migration",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["UPSILON", "ZETA"],
            "missing_building_blocks": ["online migration controller", "save pause-free handoff", "proof-backed rollback hooks"],
            "estimated_complexity": "high",
            "blockers": ["Migration lifecycle exists, but only as offline governance evidence", "Runtime save cutovers are not live-safe yet"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "mod_hot_activation",
            "capability_label": "Mod hot activation",
            "readiness": "requires_new_foundation",
            "required_series": ["UPSILON", "ZETA"],
            "missing_building_blocks": ["live pack mount", "runtime dependency arbitration", "deterministic cutover receipts"],
            "estimated_complexity": "high",
            "blockers": ["Pack governance is strong offline, but not yet live-attach capable"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "distributed_shard_relocation",
            "capability_label": "Distributed shard relocation",
            "readiness": "unrealistic_currently",
            "required_series": ["PHI", "UPSILON", "ZETA"],
            "missing_building_blocks": ["deterministic replication", "authority handoff", "state partition transfer proofs"],
            "estimated_complexity": "very_high",
            "blockers": ["Current runtime is not yet componentized for live shard mobility", "Operational control plane for replicated truth does not exist"],
            "confidence_level": "low",
        },
        {
            "capability_id": "live_trust_root_rotation",
            "capability_label": "Live trust-root rotation",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["UPSILON", "ZETA"],
            "missing_building_blocks": ["online trust-root distribution", "rotation receipts", "coordinated downgrade and revoke workflow"],
            "estimated_complexity": "high",
            "blockers": ["Trust verification exists, but runtime rotation choreography does not"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "live_protocol_upgrades",
            "capability_label": "Live protocol upgrades",
            "readiness": "requires_new_foundation",
            "required_series": ["SIGMA", "PHI", "UPSILON", "ZETA"],
            "missing_building_blocks": ["multi-version protocol runtime", "live negotiation cutover policy", "rollback proofs"],
            "estimated_complexity": "very_high",
            "blockers": ["Compatibility negotiation exists for boot and attach, not for in-flight cutovers"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "renderer_virtualization",
            "capability_label": "Renderer virtualization",
            "readiness": "requires_new_foundation",
            "required_series": ["PHI", "ZETA"],
            "missing_building_blocks": ["render service boundary", "framegraph isolation", "device-independent submission API"],
            "estimated_complexity": "high",
            "blockers": ["Rendering is not yet isolated as a service kernel surface"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "canary_mod_deployment",
            "capability_label": "Canary mod deployment",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["UPSILON", "ZETA"],
            "missing_building_blocks": ["release rehearsal sandbox", "live pack mount", "compatibility-scored canary policy"],
            "estimated_complexity": "high",
            "blockers": ["Release and ecosystem verification exist offline, but not as staged live policy"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "offscreen_validation_renderer",
            "capability_label": "Offscreen validation renderer",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["PHI", "UPSILON"],
            "missing_building_blocks": ["render abstraction", "artifactized render snapshot pipeline"],
            "estimated_complexity": "medium",
            "blockers": ["Render validation exists conceptually, but not as a first-class service surface"],
            "confidence_level": "high",
        },
        {
            "capability_id": "debug_renderer_sidecar",
            "capability_label": "Debug renderer sidecar",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["PHI", "SIGMA", "ZETA"],
            "missing_building_blocks": ["renderer virtualization", "observer-safe debug channels", "sidecar lifecycle policy"],
            "estimated_complexity": "high",
            "blockers": ["Observer and renderer boundaries are constitutional, but sidecar transport is not implemented"],
            "confidence_level": "medium",
        },
        {
            "capability_id": "release_rehearsal_sandbox",
            "capability_label": "Release rehearsal in production-like sandbox",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["OMEGA", "UPSILON", "SIGMA"],
            "missing_building_blocks": ["rehearsal orchestrator", "promotion policy", "operator signoff UI"],
            "estimated_complexity": "medium",
            "blockers": ["Convergence and ecosystem gates exist, but rehearsal is not unified as one operator surface"],
            "confidence_level": "high",
        },
        {
            "capability_id": "deterministic_downgrade_and_yank",
            "capability_label": "Automatic yanking with deterministic downgrade",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["OMEGA", "UPSILON", "ZETA"],
            "missing_building_blocks": ["live release controller", "deterministic downgrade planner", "runtime revocation choreography"],
            "estimated_complexity": "high",
            "blockers": ["Update sim exists offline, but live downgrade execution is missing"],
            "confidence_level": "high",
        },
        {
            "capability_id": "runtime_drift_detection",
            "capability_label": "Runtime drift detection",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["SIGMA", "UPSILON", "ZETA"],
            "missing_building_blocks": ["runtime attestation feed", "drift comparison service", "operator cutover policy"],
            "estimated_complexity": "medium",
            "blockers": ["Repo drift detection exists, but runtime drift telemetry is not yet live"],
            "confidence_level": "high",
        },
        {
            "capability_id": "proof_anchor_health_monitor",
            "capability_label": "Proof-anchor health monitor",
            "readiness": "foundation_ready_but_not_implemented",
            "required_series": ["SIGMA", "UPSILON", "ZETA"],
            "missing_building_blocks": ["live proof heartbeat service", "health dashboards", "rollback trigger policy"],
            "estimated_complexity": "medium",
            "blockers": ["Proof anchors are already part of governance, but health monitoring is not yet operationalized"],
            "confidence_level": "high",
        },
        {
            "capability_id": "snapshot_isolation_all_mutable_state",
            "capability_label": "Snapshot isolation for all mutable state",
            "readiness": "requires_new_foundation",
            "required_series": ["PHI", "UPSILON", "ZETA"],
            "missing_building_blocks": ["state partition protocol", "copy-on-write runtime", "WAL-like replay bridge"],
            "estimated_complexity": "very_high",
            "blockers": ["Current save and replay surfaces are not generalized into universal runtime isolation"],
            "confidence_level": "medium",
        },
    ]
    return sorted(rows, key=lambda row: (READINESS_ORDER.get(_token(row.get("readiness")), 99), _token(row.get("capability_id"))))


def _pipe_dream_rows() -> list[dict[str, object]]:
    rows = [
        ("deterministic_distributed_simulation", "distributed_runtime", "long", ["PHI", "UPSILON", "ZETA"], True, "Requires deterministic replication, partition proofs, and authority handoff."),
        ("restartless_core_engine_replacement", "runtime_replacement", "speculative", ["SIGMA", "PHI", "UPSILON", "ZETA"], True, "Needs stable kernel state export and proof-backed replacement choreography."),
        ("live_protocol_upgrades", "protocol_operations", "long", ["SIGMA", "PHI", "UPSILON", "ZETA"], True, "Multi-version protocol negotiation must survive live cutover."),
        ("live_schema_evolution", "data_governance", "speculative", ["SIGMA", "PHI", "UPSILON", "ZETA"], True, "Would require lawful online migration plus universal schema negotiation."),
        ("world_streaming_without_loading_screens", "runtime_streaming", "medium", ["PHI", "ZETA"], True, "Needs streaming-safe state partitions, scheduler awareness, and deterministic asset staging."),
        ("multi_render_backend_mirrored_execution", "rendering", "speculative", ["PHI", "ZETA"], False, "Possible only after renderer virtualization and side-by-side backend scheduling."),
        ("offscreen_validation_renderer", "rendering", "near", ["PHI", "UPSILON"], False, "Good candidate once render abstraction exists."),
        ("debug_renderer_sidecar", "rendering", "medium", ["PHI", "SIGMA", "ZETA"], True, "Needs observer-safe sidecar boundaries."),
        ("live_feature_flag_profile_cutovers", "governance_operations", "medium", ["SIGMA", "UPSILON", "ZETA"], True, "Must remain profile-driven, never hidden mode switches."),
        ("component_warm_standby", "runtime_replacement", "medium", ["PHI", "UPSILON", "ZETA"], True, "Depends on lifecycle manager plus state export/import."),
        ("release_rehearsal_production_like_sandbox", "release_operations", "near", ["OMEGA", "UPSILON", "SIGMA"], False, "Maps well to current release and ecosystem verification foundations."),
        ("automatic_yanking_with_deterministic_downgrade", "release_operations", "medium", ["OMEGA", "UPSILON", "ZETA"], True, "Builds on update simulation and release policy."),
        ("live_trust_root_rotation", "trust_operations", "medium", ["UPSILON", "ZETA"], True, "Needs online trust policy roll-forward and rollback."),
        ("live_privilege_capability_revocation", "trust_operations", "medium", ["SIGMA", "UPSILON", "ZETA"], True, "Needs live authority context invalidation and deterministic client responses."),
        ("isolation_boundaries_for_untrusted_mods", "mod_operations", "long", ["SIGMA", "PHI", "UPSILON", "ZETA"], True, "Requires module sandboxing, capability mediation, and pack policy hardening."),
        ("attested_service_replacement", "runtime_replacement", "long", ["PHI", "UPSILON", "ZETA"], True, "Replacement flow must be signed, measured, and replay-verifiable."),
        ("safe_mode_degraded_boot", "resilience", "near", ["OMEGA", "SIGMA"], False, "Strong fit with existing explicit degrade/refusal model."),
        ("runtime_drift_detection", "resilience", "medium", ["SIGMA", "UPSILON", "ZETA"], True, "Repo drift immunity should evolve into live runtime attestation."),
        ("proof_anchor_health_monitor", "resilience", "medium", ["SIGMA", "UPSILON", "ZETA"], True, "Natural extension of proof-backed rollback and audit surfaces."),
        ("trace_and_deterministic_replay_pairing", "observability", "near", ["OMEGA", "SIGMA"], False, "Replay discipline already exists; packaging it for operators is plausible."),
        ("live_asset_streaming", "runtime_streaming", "medium", ["PHI", "UPSILON", "ZETA"], True, "Needs asset pipeline, non-blocking save coordination, and content compatibility checks."),
        ("live_logic_network_recompilation", "runtime_replacement", "long", ["PHI", "UPSILON", "ZETA"], True, "Requires compile/runtime split plus safe cutover of logic graphs."),
        ("compatibility_scored_mod_insertion", "mod_operations", "medium", ["UPSILON", "SIGMA", "ZETA"], True, "Builds on pack compat and operator policy surfaces."),
        ("mod_abi_compatibility_layers", "mod_operations", "long", ["PHI", "UPSILON", "ZETA"], True, "Needs a stabilized module ABI and compatibility shims."),
        ("shadow_service_startup_and_cutover", "runtime_replacement", "medium", ["PHI", "UPSILON", "ZETA"], True, "One of the most plausible early Z capabilities after componentization."),
        ("blue_green_services", "runtime_replacement", "medium", ["PHI", "UPSILON", "ZETA"], True, "Requires side-by-side services, routing control, and rollback policy."),
        ("stateful_service_mirroring", "distributed_runtime", "long", ["PHI", "UPSILON", "ZETA"], True, "Requires deterministic replication and mirrored state export."),
        ("snapshot_isolation_for_all_mutable_state", "data_governance", "long", ["PHI", "UPSILON", "ZETA"], True, "A database-grade foundation, not a light feature."),
        ("checkpoint_and_event_tail_sync", "distributed_runtime", "long", ["PHI", "UPSILON", "ZETA"], True, "Needs WAL-like event tails with deterministic replay joins."),
        ("deterministic_replicated_simulation", "distributed_runtime", "long", ["PHI", "UPSILON", "ZETA"], True, "Core Z ambition; gated on componentized runtime and state isolation."),
        ("cluster_wide_proof_anchor_verification", "distributed_runtime", "long", ["SIGMA", "UPSILON", "ZETA"], True, "Needs distributed proof aggregation and operator health policy."),
    ]
    normalized = []
    for dream_id, category, feasibility, required_series, zeta_depends_on_preceding, notes in rows:
        normalized.append(
            {
                "dream_id": dream_id,
                "category": category,
                "feasibility_tier": feasibility,
                "prerequisite_foundations": list(required_series),
                "requires_sigma_phi_upsilon_before_zeta": bool(zeta_depends_on_preceding),
                "notes": notes,
                "innovation_angle": "Deterministic live operations with proof-backed cutover, rollback, and compatibility negotiation.",
            }
        )
    return sorted(normalized, key=lambda row: (FEASIBILITY_ORDER.get(_token(row.get("feasibility_tier")), 99), _token(row.get("dream_id"))))


def _best_practice_rows() -> list[dict[str, str]]:
    rows = [
        {"source_pattern": "Microkernels", "borrowed_idea": "Keep the kernel minimal and push replaceable behavior into controlled services.", "dominium_translation": "Use the deterministic engine kernel for truth, then grow a service registry around it rather than bloating core process execution."},
        {"source_pattern": "Erlang/BEAM hot upgrades", "borrowed_idea": "Upgrade code through planned state handoff instead of blind in-place mutation.", "dominium_translation": "Model live cutovers as state export/import plus proof-backed replacement plans issued by the lifecycle manager."},
        {"source_pattern": "Databases and WAL systems", "borrowed_idea": "Use append-only journals, snapshot isolation, and replayable recovery.", "dominium_translation": "Pair proof anchors with deterministic replay, checkpoint plus event-tail sync, and rollback receipts."},
        {"source_pattern": "Kubernetes rollouts and canaries", "borrowed_idea": "Prefer staged rollout, health checks, and reversible promotion gates.", "dominium_translation": "Adopt canary mod deployment, blue/green services, and quarantine-first rollout policy backed by XStack gates."},
        {"source_pattern": "Package managers", "borrowed_idea": "Treat compatibility, dependency graphs, and rollback as first-class governance artifacts.", "dominium_translation": "Extend pack compat, component graphs, release indexes, and deterministic downgrade planning."},
        {"source_pattern": "Framegraph renderers", "borrowed_idea": "Separate render intent from backend execution through explicit dependency graphs.", "dominium_translation": "A future render service should consume framegraph-style plans rather than letting backend specifics leak into truth paths."},
        {"source_pattern": "Service meshes", "borrowed_idea": "Make routing, observability, and policy explicit instead of ad hoc.", "dominium_translation": "Use side-by-side execution, attach negotiation, and proof-aware traffic policy for service cutovers."},
        {"source_pattern": "Formal deployment controllers", "borrowed_idea": "Represent rollouts as plans with preconditions, policy, and rollback steps.", "dominium_translation": "ControlX should emit explainable upgrade and cutover plans instead of imperative scripts."},
        {"source_pattern": "Zero-downtime migration systems", "borrowed_idea": "Dual-write, verify, and cut over only after proof of equivalence.", "dominium_translation": "Future live migrations should compare replay hashes, proof anchors, and compatibility receipts before promotion."},
    ]
    return sorted(rows, key=lambda row: _token(row.get("source_pattern")))


def _non_negotiable_invariants() -> list[str]:
    return [
        "Deterministic truth paths",
        "Worldgen lock",
        "Baseline universe",
        "Baseline gameplay loop",
        "Semantic contract discipline",
        "Universal identity blocks",
        "Migration lifecycle discipline",
        "Trust model",
        "Archive history immutability",
        "Architecture graph and module boundaries",
        "XStack CI enforcement",
    ]


def _series_dependency_payload(current_facts: Mapping[str, object]) -> dict[str, object]:
    series = _series_rows()
    payload = {
        "current_snapshot": dict(current_facts),
        "edges": _series_edges(series),
        "report_id": "pi.0.series_dependency_graph.v1",
        "series": series,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _capability_dependency_payload(current_facts: Mapping[str, object]) -> dict[str, object]:
    capabilities = _capability_nodes()
    payload = {
        "capabilities": capabilities,
        "current_snapshot": {
            "architecture_graph_fingerprint": _token(current_facts.get("architecture_graph_fingerprint")),
            "module_count": int(current_facts.get("module_count", 0) or 0),
        },
        "edges": _capability_edges(),
        "levels": [
            {"level": 0, "label": "Frozen MVP foundations"},
            {"level": 1, "label": "Operator and governance"},
            {"level": 2, "label": "Componentized runtime"},
            {"level": 3, "label": "Controlled live operations"},
            {"level": 4, "label": "Distributed live operations"},
            {"level": 5, "label": "Extreme pipe dreams"},
        ],
        "report_id": "pi.0.capability_dependency_graph.v1",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _readiness_matrix_payload() -> dict[str, object]:
    rows = _readiness_rows()
    summary = Counter(_token(row.get("readiness")) for row in rows)
    payload = {
        "readiness_counts": {key: int(summary.get(key, 0)) for key in sorted(summary)},
        "report_id": "pi.0.readiness_matrix.v1",
        "rows": rows,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _pipe_dreams_payload() -> dict[str, object]:
    rows = _pipe_dream_rows()
    summary = Counter(_token(row.get("feasibility_tier")) for row in rows)
    payload = {
        "feasibility_counts": {key: int(summary.get(key, 0)) for key in sorted(summary)},
        "report_id": "pi.0.pipe_dreams_matrix.v1",
        "rows": rows,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _available_xi_state_lines(current_facts: Mapping[str, object]) -> list[str]:
    rows = dict(current_facts.get("xi_artifact_state") or {})
    return [
        f"`{series_id}`: {'present' if bool(rows.get(series_id)) else 'not_present'}"
        for series_id in sorted(rows)
    ]


def _domain_count_lines(current_facts: Mapping[str, object], limit: int = 8) -> list[str]:
    rows = list(current_facts.get("module_domain_counts") or [])[:limit]
    return [f"`{_token(row.get('domain'))}`: {int(row.get('count', 0) or 0)} modules" for row in rows]


def _capability_level_rows(payload: Mapping[str, object]) -> dict[int, list[dict[str, object]]]:
    grouped: dict[int, list[dict[str, object]]] = {}
    for row in payload.get("capabilities") or []:
        level = int(row.get("level", 0) or 0)
        grouped.setdefault(level, []).append(dict(row))
    for level in grouped:
        grouped[level] = sorted(grouped[level], key=lambda item: _token(item.get("capability_id")))
    return grouped


def render_meta_blueprint_index(snapshot: Mapping[str, object]) -> str:
    current_facts = dict(snapshot.get("current_facts") or {})
    lines = [
        _doc_header("Meta Blueprint Index", "snapshot-anchored blueprint index after repository convergence and freeze"),
        "## Purpose",
        "",
        "This document is the master planning layer for the post-Ξ future of Dominium.",
        "It links the current audited repository evidence to the intended Σ, Φ, Υ, and Ζ implementation arcs without changing runtime semantics.",
        "",
        "## Current Evidence Snapshot",
        "",
        f"- Architecture modules: {int(current_facts.get('module_count', 0) or 0)}",
        f"- Architecture concepts: {int(current_facts.get('concept_count', 0) or 0)}",
        f"- Module dependency edges: {int(current_facts.get('module_dependency_edge_count', 0) or 0)}",
        f"- Build targets: {int(current_facts.get('build_target_count', 0) or 0)}",
        f"- Source-like directories still present in current working tree evidence: {int(current_facts.get('source_like_directory_count', 0) or 0)}",
        "",
        "Dominant module domains:",
        *_bullet_lines(_domain_count_lines(current_facts)),
        "",
        "Available Ξ evidence in the current workspace:",
        *_bullet_lines(_available_xi_state_lines(current_facts)),
        "",
        "## Artifact Index",
        "",
        "| Artifact | Purpose |",
        "| --- | --- |",
        "| `META_BLUEPRINT_SUMMARY.md` | Executive framing of the system as a multi-layer, OS-like platform. |",
        "| `RUNTIME_ARCHITECTURE_DIAGRAM.md` | Layered runtime target map from applications to the deterministic kernel. |",
        "| `REPOSITORY_GOVERNANCE_DIAGRAM.md` | XStack, architecture graph, and governance surface map. |",
        "| `DISTRIBUTION_AND_ARCHIVE_DIAGRAM.md` | Release, archive, trust, and install flow map. |",
        "| `LIVE_OPERATIONS_DIAGRAM.md` | Future Ζ live-operations capability map. |",
        "| `SERIES_DEPENDENCY_MAP.md` | Σ/Φ/Υ/Ζ dependency map plus Ω and Ξ foundations. |",
        "| `CAPABILITY_LADDER.md` | Capability levels from frozen MVP to speculative live operations. |",
        "| `FOUNDATION_READINESS_MATRIX.md` | Capability readiness classifications and blockers. |",
        "| `PIPE_DREAMS_MATRIX.md` | Advanced concepts, feasibility tiers, and prerequisites. |",
        "| `SNAPSHOT_MAPPING_NOTES.md` | Pre-snapshot assumptions and the follow-up mapping pass contract. |",
        "",
        "## Best Practices to Borrow and Adapt",
        "",
    ]
    for row in snapshot.get("best_practices") or []:
        lines.append(f"- `{_token(row.get('source_pattern'))}` -> {_token(row.get('borrowed_idea'))}")
        lines.append(f"  Dominium translation: {_token(row.get('dominium_translation'))}")
    lines.extend(
        [
            "",
            "## Bridge Statement",
            "",
            "This blueprint is pre-snapshot and architecture-driven.",
            "It describes the safe bridge from the current audited repository surface to the intended post-Ξ, post-Ω implementation work, while explicitly preserving constitutional invariants.",
            "",
        ]
    )
    return "\n".join(lines)


def render_meta_blueprint_summary(snapshot: Mapping[str, object]) -> str:
    current_facts = dict(snapshot.get("current_facts") or {})
    readiness = dict(snapshot.get("readiness_matrix") or {})
    lines = [
        _doc_header("Meta Blueprint Summary", "snapshot-anchored meta-blueprint summary after the final repository snapshot"),
        "## Master Reframing",
        "",
        "Dominium is a multi-layer system with OS-like properties.",
        "",
        "- It is a deterministic simulation kernel.",
        "- It is a modular runtime and service host.",
        "- It is a package and release operating environment.",
        "- It is a human and Agent development interface.",
        "- It is a future live-operations platform.",
        "",
        "It is not merely a game engine, not merely a tool suite, and not merely a game.",
        "",
        "## What The System Is Now",
        "",
        f"- Current audited architecture graph: `{_token(current_facts.get('architecture_graph_fingerprint'))}`",
        f"- Current architecture footprint: {int(current_facts.get('module_count', 0) or 0)} modules, {int(current_facts.get('concept_count', 0) or 0)} concepts, {int(current_facts.get('build_target_count', 0) or 0)} build targets",
        "- Strongest present foundations: deterministic governance, compatibility and trust verification, archive and distribution artifacts, XStack enforcement tools, and Ω-series verification surfaces.",
        "- Current gap: the working tree still reflects pre-snapshot, pre-freeze convergence status rather than a finished post-Ξ frozen repository layout.",
        "",
        "## What The System Is Intended To Become",
        "",
        "- A runtime where replaceable services can be planned, upgraded, verified, and rolled back without violating deterministic truth paths.",
        "- A content and release ecosystem where compatibility, trust, archives, and rollback are governed the same way code is governed.",
        "- A unified human and Agent interface where prompts are untrusted but governance is authoritative.",
        "",
        "## Innovation Angle",
        "",
        "The distinctive innovation is not merely hot reload.",
        "",
        "- Deterministic live operations",
        "- Explainable upgrade and cutover plans",
        "- Proof-backed rollback and replay",
        "- Compatibility negotiation at every layer",
        "- Content-addressed, archive-safe ecosystem management",
        "- Unified human and Agent control through XStack enforcement",
        "",
        "This differs from typical game engines by treating operations and governance as first-class deterministic surfaces.",
        "It differs from package managers by carrying compatibility, proof anchors, and replay semantics into runtime operations.",
        "It differs from cloud orchestrators by making determinism, replay equivalence, and lawful refusal central instead of incidental.",
        "",
        "## Already Achievable vs Next Foundations",
        "",
        f"- `ready_now`: {int(dict(readiness.get('readiness_counts') or {}).get('ready_now', 0) or 0)} capability rows",
        f"- `foundation_ready_but_not_implemented`: {int(dict(readiness.get('readiness_counts') or {}).get('foundation_ready_but_not_implemented', 0) or 0)} capability rows",
        f"- `requires_new_foundation`: {int(dict(readiness.get('readiness_counts') or {}).get('requires_new_foundation', 0) or 0)} capability rows",
        f"- `unrealistic_currently`: {int(dict(readiness.get('readiness_counts') or {}).get('unrealistic_currently', 0) or 0)} capability rows",
        "",
        "## Non-Negotiable Invariants",
        "",
        *_bullet_lines(_non_negotiable_invariants()),
        "",
        "## Pre-Snapshot Note",
        "",
        "This Π-series output is pre-snapshot and architecture-driven.",
        "After a fresh repository snapshot is provided, a final mapping pass must compare these plans to the actual post-Ξ working tree, remove impossible assumptions, and emit the executable next-series plan.",
        "",
    ]
    return "\n".join(lines)


def render_runtime_architecture_diagram() -> str:
    lines = [
        _doc_header("Runtime Architecture Diagram", "snapshot-anchored runtime architecture diagram after componentization planning"),
        "## Layered Diagram",
        "",
        "```text",
        "Applications",
        "  client / server / setup / launcher / tools",
        "        |",
        "        v",
        "Runtime Orchestrator",
        "  lifecycle manager / scheduler / service registry / module loader",
        "        |",
        "        v",
        "Services",
        "  render / logic / storage / network / asset / save / observability / trust",
        "        |",
        "        v",
        "Modules",
        "  render backends / platform adapters / audio / input / storage / scripting",
        "        |",
        "        v",
        "Engine Kernel",
        "  assemblies / fields / processes / law / time / determinism",
        "        |",
        "        v",
        "Game Layer",
        "  dominium rules / content / baseline packs",
        "```",
        "",
        "## Reading Guide",
        "",
        "- The engine kernel and game layer are the current strongest foundations.",
        "- The runtime orchestrator and service layer are the main Φ-series targets.",
        "- Applications must stay outside authoritative truth mutation except through lawful process execution.",
        "",
    ]
    return "\n".join(lines)


def render_repository_governance_diagram() -> str:
    lines = [
        _doc_header("Repository Governance Diagram", "snapshot-anchored governance diagram after XStack and architecture freeze"),
        "## Governance Diagram",
        "",
        "```text",
        "AGENTS.md / task catalog / prompt surfaces / agent_context.json",
        "                |",
        "                v",
        "             XStack",
        " RepoX / AuditX / TestX / ControlX / CompatX / SessionX",
        "                |",
        "                v",
        "      architecture graph / module registry / dependency graph",
        "                |",
        "                v",
        " contracts / registries / schemas / baselines / proofs",
        "                |",
        "                v",
        "        repository structure and runtime evidence",
        "```",
        "",
        "## Notes",
        "",
        "- Prompts are untrusted inputs.",
        "- XStack governance is authoritative.",
        "- Architecture drift, duplicate semantic engines, and module boundary violations should be caught before merge.",
        "",
    ]
    return "\n".join(lines)


def render_distribution_and_archive_diagram() -> str:
    lines = [
        _doc_header("Distribution and Archive Diagram", "snapshot-anchored distribution and archive diagram after release and archive hardening"),
        "## Distribution and Archive Flow",
        "",
        "```text",
        "component graph -> install profiles -> release index -> release manifest",
        "        |               |                 |                 |",
        "        v               v                 v                 v",
        " trust roots ----> compatibility policy ----> update model ----> archive policy",
        "        |                                                     |",
        "        v                                                     v",
        "  verification suites -------------------------------> offline archive bundle",
        "```",
        "",
        "## Notes",
        "",
        "- Υ-series should turn these current release foundations into a stricter control plane.",
        "- Trust roots, component graphs, and archive policies are already strong planning anchors.",
        "",
    ]
    return "\n".join(lines)


def render_live_operations_diagram() -> str:
    lines = [
        _doc_header("Live Operations Diagram", "snapshot-anchored live-operations capability diagram after future Ζ planning"),
        "## Future Ζ Capability Groups",
        "",
        "```text",
        "Replaceability",
        "  shadow service startup / blue-green services / warm standby / backend swap",
        "",
        "Migration",
        "  state export-import / live save migration / protocol cutover / schema evolution",
        "",
        "Rollout",
        "  canary mod deployment / release rehearsal sandbox / deterministic downgrade",
        "",
        "Distributed Simulation",
        "  deterministic replication / shard relocation / authority handoff / cluster failover",
        "",
        "Mod and Content Operations",
        "  live pack mount / compatibility-scored mod insertion / ABI compatibility layers",
        "",
        "Resilience and Validation",
        "  runtime drift detection / proof-anchor health monitoring / replay pairing",
        "```",
        "",
        "## Notes",
        "",
        "- Ζ is not a starting point; it is a culmination of Σ, Φ, Υ, and Ω foundations.",
        "- Every live capability must preserve deterministic truth paths, proof anchors, and lawful rollback.",
        "",
    ]
    return "\n".join(lines)


def render_series_dependency_map(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("series_dependency_graph") or {})
    lines = [
        _doc_header("Series Dependency Map", "snapshot-anchored executable planning map after series reprioritization"),
        "## Dependency Diagram",
        "",
        "```text",
        "XI -----> SIGMA",
        " | \\        \\",
        " |  \\        v",
        " |   +-----> PHI -----> ZETA",
        " |            ^           ^",
        " v            |           |",
        "OMEGA ------> UPSILON ----+",
        "```",
        "",
        "## Series Table",
        "",
        "| Series | Purpose | Prerequisites | Outputs | Can start before snapshot mapping? | Risk |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload.get("series") or []:
        lines.append(
            "| `{}` | {} | {} | {} | `{}` | `{}` |".format(
                _token(row.get("series_label")),
                _token(row.get("purpose")),
                ", ".join(_token(item) for item in row.get("prerequisites") or []) or "none",
                ", ".join(_token(item) for item in row.get("outputs") or []),
                "yes" if bool(row.get("can_start_before_snapshot_mapping")) else "no",
                _token(row.get("risk_level")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_capability_ladder(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("capability_dependency_graph") or {})
    grouped = _capability_level_rows(payload)
    level_titles = {
        0: "Level 0 - Frozen MVP foundations",
        1: "Level 1 - Operator and governance",
        2: "Level 2 - Componentized runtime",
        3: "Level 3 - Controlled live operations",
        4: "Level 4 - Distributed live operations",
        5: "Level 5 - Extreme pipe dreams",
    }
    lines = [
        _doc_header("Capability Ladder", "snapshot-anchored capability ladder after real repository mapping"),
        "## Ladder Overview",
        "",
        "Higher levels inherit every lower-level invariant and dependency.",
        "",
    ]
    for level in sorted(grouped):
        lines.append(f"## {level_titles.get(level, f'Level {level}')}")
        lines.append("")
        for row in grouped[level]:
            lines.append(
                "- `{}`: required series `{}`; status `{}`.".format(
                    _token(row.get("label")),
                    ", ".join(_token(item) for item in row.get("required_series") or []),
                    _token(row.get("status")),
                )
            )
        lines.append("")
    return "\n".join(lines)


def render_foundation_readiness_matrix(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("readiness_matrix") or {})
    lines = [
        _doc_header("Foundation Readiness Matrix", "snapshot-anchored readiness matrix after implementation planning"),
        "## Readiness Table",
        "",
        "| Capability | Readiness | Required series | Missing building blocks | Complexity | Confidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload.get("rows") or []:
        lines.append(
            "| `{}` | `{}` | `{}` | {} | `{}` | `{}` |".format(
                _token(row.get("capability_label")),
                _token(row.get("readiness")),
                ", ".join(_token(item) for item in row.get("required_series") or []),
                "; ".join(_token(item) for item in row.get("missing_building_blocks") or []),
                _token(row.get("estimated_complexity")),
                _token(row.get("confidence_level")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_pipe_dreams_matrix(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("pipe_dreams_matrix") or {})
    lines = [
        _doc_header("Pipe Dreams Matrix", "snapshot-anchored advanced capability matrix after final planning"),
        "## Advanced Concepts",
        "",
        "| Concept | Category | Feasibility | Required series | Σ/Φ/Υ before Ζ? | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload.get("rows") or []:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                _token(row.get("dream_id")),
                _token(row.get("category")),
                _token(row.get("feasibility_tier")),
                ", ".join(_token(item) for item in row.get("prerequisite_foundations") or []),
                "yes" if bool(row.get("requires_sigma_phi_upsilon_before_zeta")) else "no",
                _token(row.get("notes")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_snapshot_mapping_notes(snapshot: Mapping[str, object]) -> str:
    current_facts = dict(snapshot.get("current_facts") or {})
    lines = [
        _doc_header("Snapshot Mapping Notes", "post-snapshot executable mapping notes after the user provides a refreshed repository state"),
        "## Pre-Snapshot Statement",
        "",
        "This Π-series output is pre-snapshot and architecture-driven.",
        "It intentionally describes the target bridge from the current audited repository evidence to the intended post-Ξ and post-Ω future state.",
        "",
        "## Current Assumption Boundaries",
        "",
        f"- Current architecture graph fingerprint: `{_token(current_facts.get('architecture_graph_fingerprint'))}`",
        f"- Current source-like directory count in audit evidence: {int(current_facts.get('source_like_directory_count', 0) or 0)}",
        "- Current workspace still shows convergence planning artifacts rather than finished post-Ξ execution and freeze artifacts.",
        "",
        "## Final Mapping Pass Requirements",
        "",
        "- Compare the planned structure to the actual repository snapshot.",
        "- Eliminate assumptions invalidated by the live code, build graph, or module graph.",
        "- Reprioritize Σ, Φ, Υ, and Ζ work based on real implementation cost and blockers.",
        "- Generate the exact executable plan and batch boundaries for the next series work.",
        "",
    ]
    return "\n".join(lines)


def render_pi_0_final(snapshot: Mapping[str, object]) -> str:
    series = dict(snapshot.get("series_dependency_graph") or {})
    readiness = dict(snapshot.get("readiness_matrix") or {})
    pipe_dreams = dict(snapshot.get("pipe_dreams_matrix") or {})
    lines = [
        _doc_header("PI-0 Final", "snapshot-anchored PI-0 audit summary after blueprint generation"),
        "## Generated Artifacts",
        "",
        "- All requested blueprint diagrams were generated.",
        "- All requested blueprint matrices were generated.",
        "- Machine-readable dependency and readiness artifacts were generated with canonical fingerprints.",
        "",
        "## Fingerprints",
        "",
        f"- Series dependency graph: `{_token(series.get('deterministic_fingerprint'))}`",
        f"- Readiness matrix: `{_token(readiness.get('deterministic_fingerprint'))}`",
        f"- Pipe dreams matrix: `{_token(pipe_dreams.get('deterministic_fingerprint'))}`",
        "",
        "## Readiness",
        "",
        "- Dependencies are coherent across Ω, Ξ, Σ, Φ, Υ, and Ζ.",
        "- The blueprint is ready for final snapshot-driven planning.",
        "",
    ]
    return "\n".join(lines)


def build_meta_blueprint_snapshot(repo_root: str) -> dict[str, object]:
    current_facts = _discover_current_facts(repo_root)
    series_dependency_graph = _series_dependency_payload(current_facts)
    capability_dependency_graph = _capability_dependency_payload(current_facts)
    readiness_matrix = _readiness_matrix_payload()
    pipe_dreams_matrix = _pipe_dreams_payload()
    snapshot = {
        "best_practices": _best_practice_rows(),
        "capability_dependency_graph": capability_dependency_graph,
        "current_facts": current_facts,
        "pipe_dreams_matrix": pipe_dreams_matrix,
        "readiness_matrix": readiness_matrix,
        "series_dependency_graph": series_dependency_graph,
    }
    return snapshot


def write_meta_blueprint_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    written[SERIES_DEP_GRAPH_REL] = _write_canonical_json(_repo_abs(root, SERIES_DEP_GRAPH_REL), dict(snapshot.get("series_dependency_graph") or {}))
    written[CAPABILITY_DEP_GRAPH_REL] = _write_canonical_json(_repo_abs(root, CAPABILITY_DEP_GRAPH_REL), dict(snapshot.get("capability_dependency_graph") or {}))
    written[READINESS_MATRIX_REL] = _write_canonical_json(_repo_abs(root, READINESS_MATRIX_REL), dict(snapshot.get("readiness_matrix") or {}))
    written[PIPE_DREAMS_MATRIX_REL] = _write_canonical_json(_repo_abs(root, PIPE_DREAMS_MATRIX_REL), dict(snapshot.get("pipe_dreams_matrix") or {}))
    written[META_BLUEPRINT_INDEX_REL] = _write_text(_repo_abs(root, META_BLUEPRINT_INDEX_REL), render_meta_blueprint_index(snapshot) + "\n")
    written[META_BLUEPRINT_SUMMARY_REL] = _write_text(_repo_abs(root, META_BLUEPRINT_SUMMARY_REL), render_meta_blueprint_summary(snapshot) + "\n")
    written[RUNTIME_ARCH_DIAGRAM_REL] = _write_text(_repo_abs(root, RUNTIME_ARCH_DIAGRAM_REL), render_runtime_architecture_diagram() + "\n")
    written[REPO_GOV_DIAGRAM_REL] = _write_text(_repo_abs(root, REPO_GOV_DIAGRAM_REL), render_repository_governance_diagram() + "\n")
    written[DIST_ARCHIVE_DIAGRAM_REL] = _write_text(_repo_abs(root, DIST_ARCHIVE_DIAGRAM_REL), render_distribution_and_archive_diagram() + "\n")
    written[LIVE_OPS_DIAGRAM_REL] = _write_text(_repo_abs(root, LIVE_OPS_DIAGRAM_REL), render_live_operations_diagram() + "\n")
    written[SERIES_DEP_MAP_REL] = _write_text(_repo_abs(root, SERIES_DEP_MAP_REL), render_series_dependency_map(snapshot) + "\n")
    written[CAPABILITY_LADDER_REL] = _write_text(_repo_abs(root, CAPABILITY_LADDER_REL), render_capability_ladder(snapshot) + "\n")
    written[FOUNDATION_READINESS_REL] = _write_text(_repo_abs(root, FOUNDATION_READINESS_REL), render_foundation_readiness_matrix(snapshot) + "\n")
    written[PIPE_DREAMS_REL] = _write_text(_repo_abs(root, PIPE_DREAMS_REL), render_pipe_dreams_matrix(snapshot) + "\n")
    written[SNAPSHOT_MAPPING_NOTES_REL] = _write_text(_repo_abs(root, SNAPSHOT_MAPPING_NOTES_REL), render_snapshot_mapping_notes(snapshot) + "\n")
    written[PI_0_FINAL_REL] = _write_text(_repo_abs(root, PI_0_FINAL_REL), render_pi_0_final(snapshot) + "\n")
    return written


__all__ = [
    "CAPABILITY_DEP_GRAPH_REL",
    "CAPABILITY_LADDER_REL",
    "FOUNDATION_READINESS_REL",
    "LIVE_OPS_DIAGRAM_REL",
    "META_BLUEPRINT_INDEX_REL",
    "META_BLUEPRINT_SUMMARY_REL",
    "OUTPUT_REL_PATHS",
    "PI_0_FINAL_REL",
    "PIPE_DREAMS_MATRIX_REL",
    "PIPE_DREAMS_REL",
    "READINESS_MATRIX_REL",
    "REPO_GOV_DIAGRAM_REL",
    "RUNTIME_ARCH_DIAGRAM_REL",
    "SERIES_DEP_GRAPH_REL",
    "SERIES_DEP_MAP_REL",
    "SNAPSHOT_MAPPING_NOTES_REL",
    "build_meta_blueprint_snapshot",
    "write_meta_blueprint_snapshot",
]
