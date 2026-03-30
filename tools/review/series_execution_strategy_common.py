"""Deterministic PI-1 series execution strategy helpers."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SERIES_DEP_GRAPH_REL = "data/blueprint/series_dependency_graph.json"
CAPABILITY_DEP_GRAPH_REL = "data/blueprint/capability_dependency_graph.json"
READINESS_MATRIX_REL = "data/blueprint/readiness_matrix.json"
PIPE_DREAMS_MATRIX_REL = "data/blueprint/pipe_dreams_matrix.json"

SERIES_EXECUTION_STRATEGY_REL = "data/blueprint/series_execution_strategy.json"
FOUNDATION_PHASES_REL = "data/blueprint/foundation_phases.json"
STOP_CONDITIONS_REL = "data/blueprint/stop_conditions.json"
MANUAL_REVIEW_GATES_REL = "data/blueprint/manual_review_gates.json"

SERIES_EXECUTION_STRATEGY_DOC_REL = "docs/blueprint/SERIES_EXECUTION_STRATEGY.md"
FOUNDATION_PHASES_DOC_REL = "docs/blueprint/FOUNDATION_PHASES.md"
STOP_CONDITIONS_DOC_REL = "docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md"
MANUAL_REVIEW_GATES_DOC_REL = "docs/blueprint/MANUAL_REVIEW_GATES.md"
PRE_POST_SNAPSHOT_DOC_REL = "docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md"
PI_1_FINAL_REL = "docs/audit/PI_1_FINAL.md"

OUTPUT_REL_PATHS = {
    SERIES_EXECUTION_STRATEGY_REL,
    FOUNDATION_PHASES_REL,
    STOP_CONDITIONS_REL,
    MANUAL_REVIEW_GATES_REL,
    SERIES_EXECUTION_STRATEGY_DOC_REL,
    FOUNDATION_PHASES_DOC_REL,
    STOP_CONDITIONS_DOC_REL,
    MANUAL_REVIEW_GATES_DOC_REL,
    PRE_POST_SNAPSHOT_DOC_REL,
    PI_1_FINAL_REL,
}

REQUIRED_INPUTS = {
    "capability_dependency_graph": CAPABILITY_DEP_GRAPH_REL,
    "pipe_dreams_matrix": PIPE_DREAMS_MATRIX_REL,
    "readiness_matrix": READINESS_MATRIX_REL,
    "series_dependency_graph": SERIES_DEP_GRAPH_REL,
}

DOC_REPORT_DATE = "2026-03-31"
PHASE_SEQUENCE = ("A", "B", "C", "D", "E")
PHASE_ORDER = {value: index for index, value in enumerate(PHASE_SEQUENCE)}
SERIES_ORDER = {"OMEGA": 0, "XI": 1, "SIGMA": 2, "PHI": 3, "UPSILON": 4, "ZETA": 5}
PROFILE_ORDER = {"FAST": 0, "STRICT": 1, "FULL": 2}
PRIORITY_LABELS = {
    0: "Must happen before any live-runtime ambitions",
    1: "Makes controlled live replacement possible",
    2: "Makes advanced Z capabilities possible",
    3: "Distributed and extreme operations",
}
READINESS_ORDER = {
    "ready_now": 0,
    "foundation_ready_but_not_implemented": 1,
    "requires_new_foundation": 2,
    "unrealistic_currently": 3,
    "unknown": 4,
}
PLANNING_BUCKET_ORDER = {
    "foundation_ready": 0,
    "future_plausible": 1,
    "not_yet_safe_to_implement": 2,
}


class PiInputMissingError(RuntimeError):
    """Raised when the required PI inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing PI inputs")
        self.missing_paths = sorted({_norm_rel(path) for path in missing_paths if _token(path)})
        self.refusal_code = "refusal.pi.missing_inputs"


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


def _required_inputs(repo_root: str) -> dict[str, dict]:
    root = _repo_root(repo_root)
    payloads: dict[str, dict] = {}
    missing = []
    for key, rel_path in sorted(REQUIRED_INPUTS.items()):
        abs_path = _repo_abs(root, rel_path)
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
            continue
        payload = _read_json(abs_path)
        if not payload:
            missing.append(rel_path)
            continue
        payloads[key] = payload
    if missing:
        raise PiInputMissingError(missing)
    return payloads


def _phase_sort_key(row: Mapping[str, object]) -> tuple[int, str]:
    return (PHASE_ORDER.get(_token(row.get("phase_id")), 99), _token(row.get("phase_id")))


def _series_sort_key(series_id: object) -> tuple[int, str]:
    token = _token(series_id)
    return (SERIES_ORDER.get(token, 99), token)


def _fingerprinted(payload: Mapping[str, object]) -> dict[str, object]:
    row = dict(payload)
    row["deterministic_fingerprint"] = canonical_sha256(row)
    return row


def _priority_item_snapshot_requirement(item_id: object) -> str:
    token = _token(item_id)
    explicit = {
        "SIGMA.0_agent_governance": "pre_snapshot_safe",
        "SIGMA.1_agent_mirrors": "pre_snapshot_safe",
        "SIGMA.2_natural_language_task_bridge": "pre_snapshot_safe",
        "PHI.0_runtime_kernel_model": "pre_snapshot_safe",
        "PHI.1_component_model": "pre_snapshot_safe",
        "PHI.2_module_loader": "post_snapshot_required",
        "PHI.3_runtime_services": "post_snapshot_required",
        "PHI.4_state_externalization": "pre_snapshot_safe",
        "PHI.5_lifecycle_manager": "post_snapshot_required",
        "PHI.6_framegraph": "post_snapshot_required",
        "PHI.7_render_device_abstraction": "post_snapshot_required",
        "PHI.8_hotswap_boundaries": "post_snapshot_required",
        "PHI.9_asset_pipeline": "post_snapshot_required",
        "PHI.10_sandboxing": "post_snapshot_required",
        "PHI.11_multi_version_coexistence": "post_snapshot_required",
        "UPSILON.0_build_graph_lock": "post_snapshot_required",
        "UPSILON.1_preset_toolchain_consolidation": "post_snapshot_required",
        "UPSILON.2_versioning_policy": "pre_snapshot_safe",
        "UPSILON.3_release_index_policy_refinement": "pre_snapshot_safe",
        "UPSILON.4_release_transaction_log": "pre_snapshot_safe",
        "UPSILON.5_canary_blue_green_rollout_policy": "pre_snapshot_safe",
        "UPSILON.6_disaster_downgrade_policy": "pre_snapshot_safe",
    }
    if token in explicit:
        return explicit[token]
    return "post_snapshot_required" if token.startswith("ZETA.") else "post_snapshot_required"


def _priority_item_rows() -> list[dict[str, object]]:
    rows = [
        {"item_id": "SIGMA.0_agent_governance", "phase_id": "A", "priority_band": 0, "series_id": "SIGMA", "title": "Agent governance", "summary": "Mirror AGENTS governance into stable machine-readable workflows before automation expands."},
        {"item_id": "SIGMA.1_agent_mirrors", "phase_id": "A", "priority_band": 0, "series_id": "SIGMA", "title": "Agent mirrors", "summary": "Create mirrored operator and agent surfaces so governance is inspectable from both human and tool paths."},
        {"item_id": "SIGMA.2_natural_language_task_bridge", "phase_id": "A", "priority_band": 0, "series_id": "SIGMA", "title": "Natural-language task bridge", "summary": "Bind natural-language tasks to deterministic task types, validations, and refusal paths."},
        {"item_id": "PHI.0_runtime_kernel_model", "phase_id": "B", "priority_band": 0, "series_id": "PHI", "title": "Runtime kernel model", "summary": "Freeze the kernel doctrine for services, truth separation, and lawful state movement."},
        {"item_id": "PHI.1_component_model", "phase_id": "B", "priority_band": 0, "series_id": "PHI", "title": "Component model", "summary": "Define component boundaries, identity, lifecycle hooks, and state ownership expectations."},
        {"item_id": "PHI.2_module_loader", "phase_id": "B", "priority_band": 0, "series_id": "PHI", "title": "Module loader", "summary": "Introduce capability-negotiated module loading only after exact insertion points are mapped."},
        {"item_id": "PHI.3_runtime_services", "phase_id": "B", "priority_band": 0, "series_id": "PHI", "title": "Runtime services", "summary": "Separate service responsibilities from the kernel without violating process-only mutation."},
        {"item_id": "PHI.4_state_externalization", "phase_id": "B", "priority_band": 0, "series_id": "PHI", "title": "State externalization", "summary": "Model export/import, state ownership, and replay-safe transfer boundaries before live cutovers."},
        {"item_id": "UPSILON.0_build_graph_lock", "phase_id": "C", "priority_band": 0, "series_id": "UPSILON", "title": "Build graph lock", "summary": "Lock the build graph so later control-plane work has a deterministic substrate."},
        {"item_id": "UPSILON.1_preset_toolchain_consolidation", "phase_id": "C", "priority_band": 0, "series_id": "UPSILON", "title": "Preset and toolchain consolidation", "summary": "Consolidate execution presets and toolchains into a governed release surface."},
        {"item_id": "UPSILON.2_versioning_policy", "phase_id": "C", "priority_band": 0, "series_id": "UPSILON", "title": "Versioning policy", "summary": "Freeze release numbering, compatibility, and migration obligations before rollout automation."},
        {"item_id": "UPSILON.3_release_index_policy_refinement", "phase_id": "C", "priority_band": 0, "series_id": "UPSILON", "title": "Release index policy refinement", "summary": "Refine release indexing and publication semantics before live control-plane work."},
        {"item_id": "PHI.5_lifecycle_manager", "phase_id": "B", "priority_band": 1, "series_id": "PHI", "title": "Lifecycle manager", "summary": "Add governed startup, shutdown, handoff, and rollback choreography for runtime services."},
        {"item_id": "PHI.6_framegraph", "phase_id": "D", "priority_band": 1, "series_id": "PHI", "title": "Framegraph", "summary": "Separate render intent from backend execution so renderer replacement becomes testable."},
        {"item_id": "PHI.7_render_device_abstraction", "phase_id": "D", "priority_band": 1, "series_id": "PHI", "title": "Render device abstraction", "summary": "Introduce a governed device abstraction before backend swap or mirrored execution work."},
        {"item_id": "PHI.8_hotswap_boundaries", "phase_id": "D", "priority_band": 1, "series_id": "PHI", "title": "Hotswap boundaries", "summary": "Define replacement boundaries and state handoff contracts before any live replacement feature work."},
        {"item_id": "UPSILON.4_release_transaction_log", "phase_id": "C", "priority_band": 1, "series_id": "UPSILON", "title": "Release transaction log", "summary": "Record rollout, downgrade, and rollback intent in a deterministic control-plane ledger."},
        {"item_id": "UPSILON.5_canary_blue_green_rollout_policy", "phase_id": "C", "priority_band": 1, "series_id": "UPSILON", "title": "Canary and blue-green rollout policy", "summary": "Govern staged exposure, quarantine, and reversal before live cutovers."},
        {"item_id": "UPSILON.6_disaster_downgrade_policy", "phase_id": "C", "priority_band": 1, "series_id": "UPSILON", "title": "Disaster downgrade policy", "summary": "Define rollback, yank, and degraded boot discipline before higher-risk replacement work."},
        {"item_id": "PHI.9_asset_pipeline", "phase_id": "D", "priority_band": 2, "series_id": "PHI", "title": "Asset pipeline", "summary": "Stabilize asset and shader ingestion before live mount, streaming, or mirrored execution."},
        {"item_id": "PHI.10_sandboxing", "phase_id": "D", "priority_band": 2, "series_id": "PHI", "title": "Sandboxing", "summary": "Introduce controlled isolation before untrusted mod or sidecar work."},
        {"item_id": "PHI.11_multi_version_coexistence", "phase_id": "D", "priority_band": 2, "series_id": "PHI", "title": "Multi-version coexistence", "summary": "Support controlled version overlap before live protocol, ABI, or content cutovers."},
        {"item_id": "ZETA.0_early_replaceability_features", "phase_id": "D", "priority_band": 2, "series_id": "ZETA", "title": "Early replaceability features", "summary": "Enable service restarts, controlled replacement, and shadow cutovers only after A, B, and C complete."},
        {"item_id": "ZETA.1_content_live_mount_unmount", "phase_id": "D", "priority_band": 2, "series_id": "ZETA", "title": "Content live mount and unmount", "summary": "Allow pack mount and unmount only after compatibility, rollback, and isolation controls exist."},
        {"item_id": "ZETA.2_mirrored_execution_sidecars", "phase_id": "D", "priority_band": 2, "series_id": "ZETA", "title": "Mirrored execution sidecars", "summary": "Add side-by-side validation services after service boundaries and proof hooks are frozen."},
        {"item_id": "ZETA.3_distributed_simulation", "phase_id": "E", "priority_band": 3, "series_id": "ZETA", "title": "Distributed simulation", "summary": "Expand to deterministic distributed runtime only after replay, handoff, and quorum proofs exist."},
        {"item_id": "ZETA.4_live_shard_relocation", "phase_id": "E", "priority_band": 3, "series_id": "ZETA", "title": "Live shard relocation", "summary": "Move state across shards only after deterministic replication and authority handoff are proven."},
        {"item_id": "ZETA.5_protocol_schema_live_evolution", "phase_id": "E", "priority_band": 3, "series_id": "ZETA", "title": "Protocol and schema live evolution", "summary": "Evolve protocol and schema live only after version coexistence and rollback proofs are stable."},
        {"item_id": "ZETA.6_restartless_core_engine_replacement", "phase_id": "E", "priority_band": 3, "series_id": "ZETA", "title": "Restartless core engine replacement", "summary": "Treat core replacement as a last-stage research problem, not an early delivery target."},
        {"item_id": "ZETA.7_cluster_of_clusters", "phase_id": "E", "priority_band": 3, "series_id": "ZETA", "title": "Cluster-of-clusters", "summary": "Consider cluster-of-clusters only after deterministic distributed simulation is already boring and proven."},
    ]
    for row in rows:
        row["snapshot_requirement"] = _priority_item_snapshot_requirement(row.get("item_id"))
    return sorted(rows, key=lambda row: (int(row.get("priority_band", 0)), PHASE_ORDER.get(_token(row.get("phase_id")), 99), _series_sort_key(row.get("series_id")), _token(row.get("item_id"))))


def _priority_bands(priority_items: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    for row in priority_items:
        grouped[int(row.get("priority_band", 0))].append(dict(row))
    bands = []
    for band in sorted(grouped):
        items = sorted(grouped[band], key=lambda row: (PHASE_ORDER.get(_token(row.get("phase_id")), 99), _series_sort_key(row.get("series_id")), _token(row.get("item_id"))))
        bands.append({"priority_band": band, "label": PRIORITY_LABELS.get(band, f"Priority {band}"), "items": items})
    return bands


def _foundation_primitives() -> list[dict[str, object]]:
    rows = [
        ("SIGMA.architecture_governance_mirror", "SIGMA", "Architecture governance mirror", ["SIGMA.0_agent_governance"]),
        ("SIGMA.agent_mirrors", "SIGMA", "Agent mirrors", ["SIGMA.1_agent_mirrors"]),
        ("SIGMA.task_bridge", "SIGMA", "Natural-language task bridge", ["SIGMA.2_natural_language_task_bridge"]),
        ("SIGMA.task_catalogs", "SIGMA", "Task catalogs", ["SIGMA.0_agent_governance", "SIGMA.2_natural_language_task_bridge"]),
        ("SIGMA.operator_policy_model", "SIGMA", "Operator policy model", ["SIGMA.0_agent_governance"]),
        ("SIGMA.declarative_cutover_language", "SIGMA", "Declarative cutover language", ["SIGMA.2_natural_language_task_bridge"]),
        ("SIGMA.validation_mapping", "SIGMA", "Validation mapping", ["SIGMA.0_agent_governance", "SIGMA.2_natural_language_task_bridge"]),
        ("SIGMA.manual_review_protocols", "SIGMA", "Manual review protocols", ["SIGMA.0_agent_governance"]),
        ("SIGMA.contract_change_protocol", "SIGMA", "Contract change protocol", ["SIGMA.0_agent_governance"]),
        ("SIGMA.runtime_privilege_policy", "SIGMA", "Runtime privilege policy", ["SIGMA.0_agent_governance"]),
        ("PHI.runtime_kernel_model", "PHI", "Runtime kernel model", ["PHI.0_runtime_kernel_model"]),
        ("PHI.component_model", "PHI", "Component model", ["PHI.1_component_model"]),
        ("PHI.module_loader", "PHI", "Module loader", ["PHI.2_module_loader"]),
        ("PHI.service_registry", "PHI", "Service registry", ["PHI.3_runtime_services"]),
        ("PHI.state_externalization", "PHI", "State externalization", ["PHI.4_state_externalization"]),
        ("PHI.lifecycle_manager", "PHI", "Lifecycle manager", ["PHI.5_lifecycle_manager"]),
        ("PHI.framegraph", "PHI", "Framegraph", ["PHI.6_framegraph"]),
        ("PHI.render_device", "PHI", "Render device abstraction", ["PHI.7_render_device_abstraction"]),
        ("PHI.hotswap_boundaries", "PHI", "Hotswap boundaries", ["PHI.8_hotswap_boundaries"]),
        ("PHI.asset_pipeline", "PHI", "Asset pipeline", ["PHI.9_asset_pipeline"]),
        ("PHI.sandboxing", "PHI", "Sandboxing", ["PHI.10_sandboxing"]),
        ("PHI.multi_version_coexistence", "PHI", "Multi-version coexistence", ["PHI.11_multi_version_coexistence"]),
        ("PHI.event_log", "PHI", "Deterministic event log", ["PHI.4_state_externalization", "PHI.5_lifecycle_manager"]),
        ("PHI.snapshot_service", "PHI", "Snapshot service", ["PHI.4_state_externalization", "PHI.5_lifecycle_manager"]),
        ("PHI.state_partition_protocol", "PHI", "State partition protocol", ["PHI.4_state_externalization", "PHI.11_multi_version_coexistence"]),
        ("PHI.module_abi_boundary", "PHI", "Module ABI boundary", ["PHI.1_component_model", "PHI.11_multi_version_coexistence"]),
        ("UPSILON.build_graph_lock", "UPSILON", "Build graph lock", ["UPSILON.0_build_graph_lock"]),
        ("UPSILON.toolchain_consolidation", "UPSILON", "Preset and toolchain consolidation", ["UPSILON.1_preset_toolchain_consolidation"]),
        ("UPSILON.versioning_policy", "UPSILON", "Versioning policy", ["UPSILON.2_versioning_policy"]),
        ("UPSILON.release_index_policy", "UPSILON", "Release index policy refinement", ["UPSILON.3_release_index_policy_refinement"]),
        ("UPSILON.release_transaction_log", "UPSILON", "Release transaction log", ["UPSILON.4_release_transaction_log"]),
        ("UPSILON.canary_blue_green_policy", "UPSILON", "Canary and blue-green rollout policy", ["UPSILON.5_canary_blue_green_rollout_policy"]),
        ("UPSILON.disaster_downgrade_policy", "UPSILON", "Disaster downgrade policy", ["UPSILON.6_disaster_downgrade_policy"]),
        ("UPSILON.archive_operations", "UPSILON", "Archive operations", ["UPSILON.3_release_index_policy_refinement"]),
        ("UPSILON.publication_models", "UPSILON", "Publication models", ["UPSILON.3_release_index_policy_refinement"]),
        ("UPSILON.migration_policy", "UPSILON", "Migration policy", ["UPSILON.2_versioning_policy", "UPSILON.4_release_transaction_log"]),
        ("UPSILON.operator_release_controller", "UPSILON", "Operator release controller", ["UPSILON.4_release_transaction_log", "UPSILON.5_canary_blue_green_rollout_policy"]),
        ("UPSILON.release_rehearsal_controller", "UPSILON", "Release rehearsal controller", ["UPSILON.4_release_transaction_log", "UPSILON.5_canary_blue_green_rollout_policy"]),
        ("UPSILON.trust_distribution_policy", "UPSILON", "Trust distribution policy", ["UPSILON.2_versioning_policy", "UPSILON.4_release_transaction_log"]),
        ("UPSILON.drift_attestation_pipeline", "UPSILON", "Drift attestation pipeline", ["UPSILON.0_build_graph_lock", "UPSILON.4_release_transaction_log"]),
        ("OMEGA.worldgen_lock", "OMEGA", "Worldgen lock baseline", []),
        ("OMEGA.baseline_universe", "OMEGA", "Baseline universe verify", []),
        ("OMEGA.baseline_gameplay", "OMEGA", "Baseline gameplay loop verify", []),
        ("OMEGA.disaster_suite", "OMEGA", "Disaster suite", []),
        ("OMEGA.ecosystem_verify", "OMEGA", "Ecosystem verify", []),
        ("OMEGA.update_sim", "OMEGA", "Update simulation verify", []),
        ("OMEGA.trust_strict", "OMEGA", "Trust strict suite", []),
        ("ZETA.service_restart_protocol", "ZETA", "Service restart protocol", ["ZETA.0_early_replaceability_features"]),
        ("ZETA.live_pack_mount", "ZETA", "Live pack mount", ["ZETA.1_content_live_mount_unmount"]),
        ("ZETA.shadow_service_startup", "ZETA", "Shadow service startup", ["ZETA.0_early_replaceability_features"]),
        ("ZETA.mirrored_execution_sidecars", "ZETA", "Mirrored execution sidecars", ["ZETA.2_mirrored_execution_sidecars"]),
        ("ZETA.authority_handoff_protocol", "ZETA", "Authority handoff protocol", ["ZETA.3_distributed_simulation", "ZETA.4_live_shard_relocation"]),
        ("ZETA.deterministic_replication", "ZETA", "Deterministic replication", ["ZETA.3_distributed_simulation"]),
        ("ZETA.proof_anchor_quorum", "ZETA", "Proof-anchor quorum", ["ZETA.3_distributed_simulation"]),
        ("ZETA.cluster_failover_controller", "ZETA", "Cluster failover controller", ["ZETA.7_cluster_of_clusters"]),
        ("ZETA.runtime_cutover_controller", "ZETA", "Runtime cutover controller", ["ZETA.0_early_replaceability_features"]),
    ]
    payload = []
    for foundation_id, series_id, label, derived_from in rows:
        payload.append(
            {
                "foundation_id": foundation_id,
                "series_id": series_id,
                "label": label,
                "derived_from_priority_items": sorted(derived_from),
                "snapshot_requirement": "post_snapshot_required"
                if any(_priority_item_snapshot_requirement(item_id) == "post_snapshot_required" for item_id in derived_from)
                else "pre_snapshot_safe",
            }
        )
    return sorted(payload, key=lambda row: (_series_sort_key(row.get("series_id")), _token(row.get("foundation_id"))))


def _series_execution_sequence() -> list[dict[str, object]]:
    return [
        {"execution_rank": 0, "series_id": "SIGMA", "must_start_before": ["PHI", "ZETA"], "may_overlap_with": ["UPSILON"], "why_now": "Governance, operator policy, and validation mapping must exist before aggressive automation or live cutovers."},
        {"execution_rank": 1, "series_id": "UPSILON", "must_start_before": ["ZETA"], "may_overlap_with": ["SIGMA", "PHI"], "why_now": "Release control, rollback policy, and deterministic distribution govern every later replacement workflow."},
        {"execution_rank": 2, "series_id": "PHI", "must_start_before": ["ZETA"], "may_overlap_with": ["SIGMA", "UPSILON"], "why_now": "Componentization is required for replaceability, but exact insertion points must wait for the fresh snapshot mapping."},
        {"execution_rank": 3, "series_id": "ZETA", "must_start_before": [], "may_overlap_with": [], "why_now": "Live runtime operations are downstream of governance, control-plane, and runtime component foundations."},
    ]


def _foundation_phase_rows() -> list[dict[str, object]]:
    rows = [
        {"phase_id": "A", "title": "Governance & Interface Foundations", "objective": "Stabilize the human and agent governance surface before any advanced runtime automation.", "series_focus": ["SIGMA"], "priority_item_ids": ["SIGMA.0_agent_governance", "SIGMA.1_agent_mirrors", "SIGMA.2_natural_language_task_bridge"], "prerequisites": ["XI architecture freeze, module boundaries, CI guardrails, and repository structure lock present", "OMEGA baseline verification inventory confirmed current"], "completion_criteria": ["AGENTS governance mirrored into XStack artifacts", "task types mapped to validation levels and refusal codes", "operator policy model and declarative cutover language reviewed", "manual review gate definitions frozen for high-risk areas"], "blocked_capabilities": ["agent-driven change execution at scale", "live feature flag cutovers", "runtime privilege revocation"]},
        {"phase_id": "B", "title": "Runtime Component Foundations", "objective": "Define the kernel, service, module, and state boundaries required for lawful replaceability.", "series_focus": ["PHI"], "priority_item_ids": ["PHI.0_runtime_kernel_model", "PHI.1_component_model", "PHI.2_module_loader", "PHI.3_runtime_services", "PHI.4_state_externalization", "PHI.5_lifecycle_manager"], "prerequisites": ["Phase A complete", "fresh repository snapshot mapped to exact insertion points", "runtime boundary doctrine accepted in manual design review"], "completion_criteria": ["component ownership and service registry boundaries frozen", "module loader insertion points mapped and validated", "state externalization and lifecycle semantics have replay-safe contracts", "module ABI boundaries reviewed for compatibility and rollback"], "blocked_capabilities": ["hot-swappable renderers", "partial live module reload", "shadow service startup", "non-blocking save handoff"]},
        {"phase_id": "C", "title": "Build / Release / Control Plane Foundations", "objective": "Freeze the control plane needed to ship, rehearse, roll forward, and roll back deterministically.", "series_focus": ["UPSILON"], "priority_item_ids": ["UPSILON.0_build_graph_lock", "UPSILON.1_preset_toolchain_consolidation", "UPSILON.2_versioning_policy", "UPSILON.3_release_index_policy_refinement", "UPSILON.4_release_transaction_log", "UPSILON.5_canary_blue_green_rollout_policy", "UPSILON.6_disaster_downgrade_policy"], "prerequisites": ["Phase A complete", "versioning, release index, rollback, and rollout policy surfaces designed", "fresh build graph and release surface re-audited before exact lock and preset wiring", "archive and publication policies aligned with OMEGA verification"], "completion_criteria": ["build graph lock is generated from the live repository state", "release transaction log and rollback policy exist as inspectable artifacts", "canary, blue-green, and downgrade policy pass governance review", "release rehearsal workflow defined with deterministic checkpoints"], "blocked_capabilities": ["automatic yanking with deterministic downgrade", "release rehearsal sandbox", "live trust-root rotation", "mod live mount and live cutover"]},
        {"phase_id": "D", "title": "Advanced Replaceability", "objective": "Enable the earliest safe ZETA features once governance, componentization, and release control are complete.", "series_focus": ["PHI", "UPSILON", "ZETA"], "priority_item_ids": ["PHI.6_framegraph", "PHI.7_render_device_abstraction", "PHI.8_hotswap_boundaries", "PHI.9_asset_pipeline", "PHI.10_sandboxing", "PHI.11_multi_version_coexistence", "ZETA.0_early_replaceability_features", "ZETA.1_content_live_mount_unmount", "ZETA.2_mirrored_execution_sidecars"], "prerequisites": ["Phase A complete", "Phase B complete", "Phase C complete", "OMEGA worldgen, baseline, gameplay, disaster, ecosystem, and trust gates current"], "completion_criteria": ["renderer and service replacement boundaries are proven by smoke harnesses", "early shadow services and pack mount workflows have rollback receipts", "sidecars and offscreen validation paths do not leak truth mutation", "all replacement plans use declarative cutover artifacts and transaction logs"], "blocked_capabilities": ["distributed shard relocation", "deterministic replicated simulation", "restartless core engine replacement"]},
        {"phase_id": "E", "title": "Distributed Live Operations", "objective": "Pursue distributed runtime and extreme live operations only after earlier phases are complete and boring.", "series_focus": ["ZETA"], "priority_item_ids": ["ZETA.3_distributed_simulation", "ZETA.4_live_shard_relocation", "ZETA.5_protocol_schema_live_evolution", "ZETA.6_restartless_core_engine_replacement", "ZETA.7_cluster_of_clusters"], "prerequisites": ["Phase D complete", "event log and snapshot proofs validated under rehearsal", "authority handoff model and proof-anchor quorum semantics manually approved"], "completion_criteria": ["deterministic replication and authority handoff proven under controlled rehearsal", "cluster failover, downgrade, and replay verification remain within OMEGA tolerances", "protocol and schema live evolution guarded by multi-version coexistence and rollback policy", "extreme operations remain quarantined unless every lower-level invariant still passes"], "blocked_capabilities": ["cluster-of-clusters rollout", "restartless core replacement by default", "live schema evolution by default"]},
    ]
    return sorted(rows, key=_phase_sort_key)


def _snapshot_work_items() -> list[dict[str, object]]:
    rows = [
        {"work_id": "SIGMA.governance_docs", "series_id": "SIGMA", "classification": "pre_snapshot_safe", "reason": "Governance vocabulary, task catalogs, and operator policy are architecture-level and do not require exact insertion points."},
        {"work_id": "SIGMA.agent_context_contract", "series_id": "SIGMA", "classification": "pre_snapshot_safe", "reason": "The agent context contract is a planning artifact and should be stabilized before code work."},
        {"work_id": "SIGMA.task_catalogs", "series_id": "SIGMA", "classification": "pre_snapshot_safe", "reason": "Task types, validation levels, and refusal expectations can be designed before the fresh snapshot arrives."},
        {"work_id": "SIGMA.operator_policy_model", "series_id": "SIGMA", "classification": "pre_snapshot_safe", "reason": "Policy modeling is a doctrine problem first and should guide later implementation."},
        {"work_id": "SIGMA.declarative_cutover_language", "series_id": "SIGMA", "classification": "pre_snapshot_safe", "reason": "Cutover grammar is safer to design before the repo-specific wiring begins."},
        {"work_id": "PHI.runtime_kernel_doctrine", "series_id": "PHI", "classification": "pre_snapshot_safe", "reason": "Kernel doctrine, service boundaries, and lawful state movement can be specified before code insertion points are re-mapped."},
        {"work_id": "PHI.component_model_doctrine", "series_id": "PHI", "classification": "pre_snapshot_safe", "reason": "The component model should be decided as architecture doctrine before repository-specific implementation work."},
        {"work_id": "PHI.state_externalization_model", "series_id": "PHI", "classification": "pre_snapshot_safe", "reason": "Export/import semantics and lifecycle doctrine are design artifacts first."},
        {"work_id": "UPSILON.versioning_release_policy_docs", "series_id": "UPSILON", "classification": "pre_snapshot_safe", "reason": "Versioning and release policy can be frozen ahead of repository-specific control-plane wiring."},
        {"work_id": "UPSILON.rollback_and_downgrade_policy", "series_id": "UPSILON", "classification": "pre_snapshot_safe", "reason": "Rollback and downgrade policy should lead implementation rather than follow it."},
        {"work_id": "XI.exact_file_and_module_move_plans", "series_id": "XI", "classification": "post_snapshot_required", "reason": "Exact moves depend on the fresh repository snapshot and cannot be safely guessed from planning artifacts."},
        {"work_id": "PHI.module_loader_insertion_points", "series_id": "PHI", "classification": "post_snapshot_required", "reason": "Loader insertion points must be mapped against the live codebase after convergence and freeze work."},
        {"work_id": "PHI.framegraph_integration_strategy", "series_id": "PHI", "classification": "post_snapshot_required", "reason": "Render integration depends on actual runtime boundaries in the fresh snapshot."},
        {"work_id": "UPSILON.build_graph_lock_mapping", "series_id": "UPSILON", "classification": "post_snapshot_required", "reason": "The lock artifact must be generated from the current build graph, not an older audit snapshot."},
        {"work_id": "UPSILON.preset_cleanup_inventory", "series_id": "UPSILON", "classification": "post_snapshot_required", "reason": "Preset cleanup is repository-state sensitive and must be derived from the live tree."},
        {"work_id": "UPSILON.ci_pipeline_consolidation_steps", "series_id": "UPSILON", "classification": "post_snapshot_required", "reason": "Exact CI and pipeline steps depend on the current repo layout and tool inventory."},
        {"work_id": "ZETA.live_cutover_entrypoints", "series_id": "ZETA", "classification": "post_snapshot_required", "reason": "Live cutovers require exact service boundaries and call sites from the live repo."},
        {"work_id": "ZETA.authority_handoff_insertion_points", "series_id": "ZETA", "classification": "post_snapshot_required", "reason": "Authority handoff cannot be planned as code without fresh runtime topology evidence."},
        {"work_id": "ZETA.replication_topology_mapping", "series_id": "ZETA", "classification": "post_snapshot_required", "reason": "Replication topology depends on actual state partitions, services, and products."},
        {"work_id": "ZETA.rollback_path_validation", "series_id": "ZETA", "classification": "post_snapshot_required", "reason": "Rollback validation must be wired to the current release, replay, and trust surfaces."},
    ]
    return sorted(rows, key=lambda row: (row["classification"] != "pre_snapshot_safe", _series_sort_key(row.get("series_id")), _token(row.get("work_id"))))


CAPABILITY_FOUNDATION_OVERRIDES = {
    "automatic_yanking_with_deterministic_downgrade": ["UPSILON.versioning_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "UPSILON.operator_release_controller", "OMEGA.update_sim", "OMEGA.trust_strict"],
    "attested_service_replacement": ["PHI.component_model", "PHI.service_registry", "PHI.state_externalization", "PHI.lifecycle_manager", "PHI.module_abi_boundary", "UPSILON.release_transaction_log", "UPSILON.trust_distribution_policy", "OMEGA.trust_strict", "ZETA.runtime_cutover_controller"],
    "blue_green_services": ["PHI.service_registry", "PHI.lifecycle_manager", "PHI.state_externalization", "UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "UPSILON.disaster_downgrade_policy", "ZETA.runtime_cutover_controller", "ZETA.shadow_service_startup"],
    "canary_mod_deployment": ["SIGMA.operator_policy_model", "SIGMA.declarative_cutover_language", "PHI.module_loader", "UPSILON.release_rehearsal_controller", "UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "UPSILON.versioning_policy", "ZETA.live_pack_mount"],
    "checkpoint_and_event_tail_sync": ["PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "UPSILON.release_transaction_log", "ZETA.proof_anchor_quorum"],
    "cluster_wide_proof_anchor_verification": ["SIGMA.architecture_governance_mirror", "SIGMA.validation_mapping", "UPSILON.drift_attestation_pipeline", "UPSILON.release_transaction_log", "ZETA.proof_anchor_quorum"],
    "compatibility_governed_update_rehearsal": ["UPSILON.release_rehearsal_controller", "UPSILON.versioning_policy", "UPSILON.release_transaction_log", "OMEGA.update_sim", "OMEGA.ecosystem_verify"],
    "compatibility_scored_mod_insertion": ["SIGMA.operator_policy_model", "PHI.module_loader", "PHI.sandboxing", "UPSILON.versioning_policy", "UPSILON.release_rehearsal_controller", "UPSILON.release_transaction_log", "ZETA.live_pack_mount"],
    "component_warm_standby": ["PHI.service_registry", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "ZETA.shadow_service_startup", "ZETA.runtime_cutover_controller"],
    "debug_renderer_sidecar": ["SIGMA.operator_policy_model", "PHI.component_model", "PHI.framegraph", "PHI.render_device", "PHI.hotswap_boundaries", "ZETA.mirrored_execution_sidecars"],
    "deterministic_distributed_simulation": ["PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite", "ZETA.authority_handoff_protocol", "ZETA.deterministic_replication", "ZETA.proof_anchor_quorum"],
    "deterministic_downgrade_and_yank": ["UPSILON.versioning_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "UPSILON.operator_release_controller", "OMEGA.update_sim", "OMEGA.trust_strict"],
    "deterministic_replicated_simulation": ["PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite", "ZETA.authority_handoff_protocol", "ZETA.deterministic_replication", "ZETA.proof_anchor_quorum", "ZETA.cluster_failover_controller"],
    "distributed_shard_relocation": ["PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "UPSILON.release_transaction_log", "OMEGA.worldgen_lock", "OMEGA.baseline_universe", "OMEGA.disaster_suite", "ZETA.authority_handoff_protocol", "ZETA.deterministic_replication", "ZETA.proof_anchor_quorum", "ZETA.cluster_failover_controller"],
    "hot_swappable_renderers": ["PHI.component_model", "PHI.lifecycle_manager", "PHI.render_device", "PHI.framegraph", "PHI.state_externalization", "PHI.hotswap_boundaries", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy"],
    "isolation_boundaries_for_untrusted_mods": ["SIGMA.runtime_privilege_policy", "PHI.module_loader", "PHI.module_abi_boundary", "PHI.sandboxing", "UPSILON.versioning_policy", "UPSILON.trust_distribution_policy", "OMEGA.trust_strict"],
    "live_asset_streaming": ["PHI.asset_pipeline", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "ZETA.live_pack_mount"],
    "live_feature_flag_profile_cutovers": ["SIGMA.operator_policy_model", "SIGMA.declarative_cutover_language", "UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "UPSILON.disaster_downgrade_policy", "ZETA.runtime_cutover_controller"],
    "live_logic_network_recompilation": ["PHI.component_model", "PHI.module_loader", "PHI.state_externalization", "PHI.multi_version_coexistence", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "ZETA.runtime_cutover_controller"],
    "live_privilege_capability_revocation": ["SIGMA.runtime_privilege_policy", "SIGMA.operator_policy_model", "UPSILON.release_transaction_log", "UPSILON.trust_distribution_policy", "UPSILON.disaster_downgrade_policy", "OMEGA.trust_strict"],
    "live_protocol_upgrades": ["SIGMA.contract_change_protocol", "SIGMA.declarative_cutover_language", "PHI.module_loader", "PHI.multi_version_coexistence", "PHI.state_externalization", "UPSILON.versioning_policy", "UPSILON.migration_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "OMEGA.trust_strict"],
    "live_save_migration": ["PHI.state_externalization", "PHI.snapshot_service", "UPSILON.migration_policy", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite", "ZETA.runtime_cutover_controller"],
    "live_schema_evolution": ["SIGMA.contract_change_protocol", "PHI.state_externalization", "PHI.multi_version_coexistence", "PHI.snapshot_service", "UPSILON.migration_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "OMEGA.trust_strict", "ZETA.runtime_cutover_controller"],
    "live_trust_root_rotation": ["SIGMA.runtime_privilege_policy", "UPSILON.trust_distribution_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "OMEGA.trust_strict", "ZETA.runtime_cutover_controller"],
    "mod_abi_compatibility_layers": ["PHI.module_abi_boundary", "PHI.multi_version_coexistence", "UPSILON.versioning_policy", "UPSILON.release_transaction_log", "OMEGA.trust_strict"],
    "mod_hot_activation": ["PHI.module_loader", "PHI.service_registry", "UPSILON.versioning_policy", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "ZETA.live_pack_mount", "ZETA.runtime_cutover_controller"],
}


CAPABILITY_FOUNDATION_OVERRIDES.update(
    {
        "multi_render_backend_mirrored_execution": ["PHI.render_device", "PHI.framegraph", "PHI.hotswap_boundaries", "ZETA.mirrored_execution_sidecars", "ZETA.runtime_cutover_controller"],
        "offscreen_validation_renderer": ["PHI.component_model", "PHI.framegraph", "PHI.render_device", "PHI.asset_pipeline", "UPSILON.build_graph_lock"],
        "partial_live_module_reload": ["SIGMA.declarative_cutover_language", "PHI.module_loader", "PHI.module_abi_boundary", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy"],
        "proof_anchor_health_monitor": ["SIGMA.validation_mapping", "UPSILON.drift_attestation_pipeline", "UPSILON.release_transaction_log", "ZETA.proof_anchor_quorum"],
        "proof_backed_rollback_and_replay": ["SIGMA.architecture_governance_mirror", "SIGMA.validation_mapping", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite"],
        "release_rehearsal_production_like_sandbox": ["SIGMA.operator_policy_model", "UPSILON.release_rehearsal_controller", "UPSILON.release_transaction_log", "OMEGA.ecosystem_verify", "OMEGA.update_sim"],
        "release_rehearsal_sandbox": ["SIGMA.operator_policy_model", "UPSILON.release_rehearsal_controller", "UPSILON.release_transaction_log", "OMEGA.ecosystem_verify", "OMEGA.update_sim"],
        "renderer_virtualization": ["PHI.component_model", "PHI.render_device", "PHI.framegraph", "PHI.hotswap_boundaries", "ZETA.mirrored_execution_sidecars"],
        "restartless_core_engine_replacement": ["SIGMA.contract_change_protocol", "PHI.runtime_kernel_model", "PHI.component_model", "PHI.module_abi_boundary", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy", "OMEGA.trust_strict", "ZETA.runtime_cutover_controller"],
        "runtime_drift_detection": ["SIGMA.architecture_governance_mirror", "SIGMA.validation_mapping", "UPSILON.drift_attestation_pipeline", "UPSILON.release_transaction_log", "OMEGA.baseline_universe"],
        "safe_mode_degraded_boot": ["SIGMA.operator_policy_model", "UPSILON.disaster_downgrade_policy", "OMEGA.baseline_gameplay", "OMEGA.trust_strict"],
        "shadow_service_startup_and_cutover": ["PHI.component_model", "PHI.service_registry", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "ZETA.shadow_service_startup", "ZETA.runtime_cutover_controller"],
        "snapshot_isolation_all_mutable_state": ["PHI.state_externalization", "PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "UPSILON.migration_policy", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite"],
        "snapshot_isolation_for_all_mutable_state": ["PHI.state_externalization", "PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "UPSILON.migration_policy", "UPSILON.release_transaction_log", "OMEGA.baseline_universe", "OMEGA.disaster_suite"],
        "stateful_service_mirroring": ["PHI.service_registry", "PHI.state_externalization", "PHI.lifecycle_manager", "PHI.event_log", "PHI.snapshot_service", "ZETA.shadow_service_startup", "ZETA.deterministic_replication"],
        "world_streaming_without_loading_screens": ["PHI.asset_pipeline", "PHI.state_externalization", "PHI.lifecycle_manager", "PHI.service_registry", "ZETA.runtime_cutover_controller"],
    }
)


CAPABILITY_CATEGORY_DEFAULTS = {
    "data_governance": ["PHI.state_externalization", "PHI.snapshot_service", "UPSILON.migration_policy", "UPSILON.release_transaction_log"],
    "distributed_runtime": ["PHI.event_log", "PHI.snapshot_service", "PHI.state_partition_protocol", "UPSILON.release_transaction_log"],
    "governance_operations": ["SIGMA.operator_policy_model", "SIGMA.declarative_cutover_language", "UPSILON.release_transaction_log"],
    "mod_operations": ["PHI.module_loader", "UPSILON.versioning_policy", "UPSILON.release_transaction_log"],
    "observability": ["SIGMA.validation_mapping", "OMEGA.baseline_universe"],
    "protocol_operations": ["SIGMA.contract_change_protocol", "PHI.multi_version_coexistence", "UPSILON.versioning_policy", "UPSILON.release_transaction_log"],
    "release_operations": ["UPSILON.release_transaction_log", "UPSILON.canary_blue_green_policy", "UPSILON.disaster_downgrade_policy"],
    "rendering": ["PHI.component_model", "PHI.framegraph", "PHI.render_device"],
    "resilience": ["SIGMA.operator_policy_model", "UPSILON.release_transaction_log", "UPSILON.disaster_downgrade_policy"],
    "runtime_replacement": ["PHI.component_model", "PHI.state_externalization", "PHI.lifecycle_manager", "UPSILON.release_transaction_log"],
    "runtime_streaming": ["PHI.asset_pipeline", "PHI.state_externalization", "UPSILON.release_transaction_log"],
    "trust_operations": ["SIGMA.runtime_privilege_policy", "UPSILON.trust_distribution_policy", "OMEGA.trust_strict"],
}


SERIES_BASE_FOUNDATIONS = {
    "OMEGA": ["OMEGA.baseline_universe"],
    "PHI": ["PHI.component_model"],
    "SIGMA": ["SIGMA.architecture_governance_mirror"],
    "UPSILON": ["UPSILON.release_transaction_log"],
    "ZETA": ["ZETA.runtime_cutover_controller"],
}


def _capability_execution_phase(capability_id: str, required_foundations: Sequence[str]) -> str:
    tokens = set(required_foundations)
    if capability_id in {"distributed_shard_relocation", "deterministic_distributed_simulation", "deterministic_replicated_simulation", "checkpoint_and_event_tail_sync", "cluster_wide_proof_anchor_verification", "restartless_core_engine_replacement", "stateful_service_mirroring", "live_schema_evolution"}:
        return "E"
    if any(item.startswith("ZETA.") for item in tokens):
        return "D"
    return "C"


def _planning_bucket_from_readiness(readiness: str) -> str:
    if readiness in {"ready_now", "foundation_ready_but_not_implemented"}:
        return "foundation_ready"
    if readiness == "requires_new_foundation":
        return "not_yet_safe_to_implement"
    return "future_plausible"


def _capability_sources(readiness_index: Mapping[str, Mapping[str, object]], pipe_index: Mapping[str, Mapping[str, object]]) -> list[dict[str, object]]:
    foundation_snapshot_requirements = { _token(row.get("foundation_id")): _token(row.get("snapshot_requirement")) for row in _foundation_primitives() }
    rows = []
    for capability_id in sorted(set(readiness_index) | set(pipe_index)):
        readiness_row = dict(readiness_index.get(capability_id) or {})
        pipe_row = dict(pipe_index.get(capability_id) or {})
        readiness = _token(readiness_row.get("readiness")) or "unknown"
        category = _token(pipe_row.get("category")) or "strategy"
        label = _token(readiness_row.get("capability_label")) or _token(capability_id).replace("_", " ")
        required_series = sorted({_token(item) for item in list(readiness_row.get("required_series") or []) + list(pipe_row.get("prerequisite_foundations") or []) if _token(item)}, key=_series_sort_key)
        base_foundations = []
        if capability_id in CAPABILITY_FOUNDATION_OVERRIDES:
            base_foundations.extend(CAPABILITY_FOUNDATION_OVERRIDES[capability_id])
        else:
            base_foundations.extend(CAPABILITY_CATEGORY_DEFAULTS.get(category, []))
        for series_id in required_series:
            base_foundations.extend(SERIES_BASE_FOUNDATIONS.get(series_id, []))
        required_foundations = sorted({value for value in base_foundations if value}, key=lambda item: (_series_sort_key(item.split(".", 1)[0]), item))
        source_artifacts = []
        if readiness_row:
            source_artifacts.append(READINESS_MATRIX_REL)
        if pipe_row:
            source_artifacts.append(PIPE_DREAMS_MATRIX_REL)
        planning_bucket = _planning_bucket_from_readiness(readiness if readiness != "unknown" else "requires_new_foundation")
        if not readiness_row and pipe_row:
            feasibility = _token(pipe_row.get("feasibility_tier"))
            if feasibility == "near":
                planning_bucket = "foundation_ready"
            elif feasibility in {"medium", "long", "speculative"}:
                planning_bucket = "future_plausible"
        rows.append({"capability_id": capability_id, "capability_label": label, "category": category, "execution_phase": _capability_execution_phase(capability_id, required_foundations), "manual_review_required": capability_id in {"distributed_shard_relocation", "deterministic_distributed_simulation", "deterministic_replicated_simulation", "hot_swappable_renderers", "live_protocol_upgrades", "partial_live_module_reload", "restartless_core_engine_replacement", "snapshot_isolation_all_mutable_state"}, "planning_bucket": planning_bucket, "readiness": readiness, "required_foundations": required_foundations, "required_series": required_series, "snapshot_requirement": "post_snapshot_required" if any(foundation_snapshot_requirements.get(foundation_id) == "post_snapshot_required" for foundation_id in required_foundations) else "pre_snapshot_safe", "source_artifacts": sorted(source_artifacts)})
    return sorted(rows, key=lambda row: (PLANNING_BUCKET_ORDER.get(_token(row.get("planning_bucket")), 99), READINESS_ORDER.get(_token(row.get("readiness")), 99), PHASE_ORDER.get(_token(row.get("execution_phase")), 99), _token(row.get("capability_id"))))


def _manual_review_gates() -> list[dict[str, object]]:
    rows = [
        {"gate_id": "architecture_graph_changes", "area": "Architecture graph changes", "why_human_review_required": "Changing the frozen architecture graph redefines module truth, ownership, and long-lived invariants.", "required_xstack_profile": "FULL", "required_artifacts": ["architecture graph diff", "module boundary diff", "ControlX architecture change plan"]},
        {"gate_id": "semantic_contract_changes", "area": "Semantic contract changes", "why_human_review_required": "Contract changes alter lawful meaning, compatibility duties, and downstream schema expectations.", "required_xstack_profile": "FULL", "required_artifacts": ["contract diff", "migration or refusal plan", "CompatX impact report"]},
        {"gate_id": "lifecycle_manager_semantics", "area": "Lifecycle manager semantics", "why_human_review_required": "Lifecycle semantics control replacement, rollback, and state handoff, so mistakes become repo-wide failures.", "required_xstack_profile": "FULL", "required_artifacts": ["lifecycle state machine", "state handoff contract", "rollback proof plan"]},
        {"gate_id": "module_abi_boundaries", "area": "Module ABI boundaries", "why_human_review_required": "ABI mistakes create silent breakage across loaders, sidecars, and long-lived compatibility layers.", "required_xstack_profile": "STRICT", "required_artifacts": ["module boundary spec", "ABI compatibility matrix", "rollback coverage report"]},
        {"gate_id": "trust_root_governance_changes", "area": "Trust root governance changes", "why_human_review_required": "Trust root rotation or policy changes alter who can deploy, verify, and recover.", "required_xstack_profile": "FULL", "required_artifacts": ["trust policy diff", "rotation choreography", "downgrade and revocation proof"]},
        {"gate_id": "licensing_commercialization_policy", "area": "Licensing and commercialization policy changes", "why_human_review_required": "Policy shifts here can create legal and product obligations beyond technical validation.", "required_xstack_profile": "STRICT", "required_artifacts": ["policy proposal", "licensing impact summary", "distribution change plan"]},
        {"gate_id": "distributed_authority_model_changes", "area": "Distributed authority model changes", "why_human_review_required": "Authority handoff and quorum semantics define what remains lawful in distributed execution.", "required_xstack_profile": "FULL", "required_artifacts": ["authority handoff model", "proof-anchor quorum plan", "distributed replay verification design"]},
        {"gate_id": "runtime_privilege_escalation_policies", "area": "Runtime privilege escalation policies", "why_human_review_required": "Privilege policy changes can bypass law-gated authority or degrade operator trust.", "required_xstack_profile": "STRICT", "required_artifacts": ["privilege policy diff", "capability revocation plan", "audit trail expectations"]},
        {"gate_id": "restartless_core_replacement_mechanisms", "area": "Restartless core replacement mechanisms", "why_human_review_required": "Core replacement threatens the most fragile invariants and must not be green-lit by automation alone.", "required_xstack_profile": "FULL", "required_artifacts": ["kernel replacement plan", "state export and import proof", "rollback and replay equivalence report"]},
    ]
    return sorted(rows, key=lambda row: (PROFILE_ORDER.get(_token(row.get("required_xstack_profile")), 99), _token(row.get("gate_id"))))


def _stop_conditions(phase_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    manual_gate_map = {"A": ["architecture_graph_changes", "semantic_contract_changes"], "B": ["lifecycle_manager_semantics", "module_abi_boundaries"], "C": ["licensing_commercialization_policy", "trust_root_governance_changes"], "D": ["runtime_privilege_escalation_policies", "trust_root_governance_changes"], "E": ["distributed_authority_model_changes", "restartless_core_replacement_mechanisms"]}
    phase_specific_conditions = {
        "A": ["Stop if AGENTS governance is not mirrored into XStack artifacts.", "Stop if task types are not mapped to validation levels and refusal behavior.", "Stop if architecture graph freeze status is unknown in the fresh snapshot."],
        "B": ["Stop if runtime kernel doctrine is not approved in manual review.", "Stop if module loader insertion points cannot be mapped in the fresh snapshot.", "Stop if state externalization or lifecycle semantics break replay assumptions."],
        "C": ["Stop if the build graph lock cannot be generated from the live repo state.", "Stop if release transaction log semantics are missing or ambiguous.", "Stop if downgrade and rollback policy are not inspectable artifacts."],
        "D": ["Stop if lifecycle manager is not frozen.", "Stop if state externalization is incomplete.", "Stop if the module loader is not capability-negotiated.", "Stop if OMEGA baseline gates drift during replacement rehearsals."],
        "E": ["Stop if event log and snapshot sync are not proven equivalent.", "Stop if authority handoff semantics are absent or disputed.", "Stop if proof-anchor quorum verification is absent.", "Stop if deterministic replication is not validated under rehearsal."],
    }
    escalation_steps = {
        "A": ["Convert policy ambiguity into manual design review rather than adding ad hoc prompt instructions.", "Freeze further governance automation until validation mapping exists."],
        "B": ["Escalate unresolved service or ABI uncertainty into architecture review with explicit state diagrams.", "Do not prompt through loader or lifecycle unknowns."],
        "C": ["Escalate unresolved release control semantics into operator policy review.", "Do not automate release workflows without a transaction log and rollback story."],
        "D": ["Quarantine the capability and revert to docs and validator work only.", "Require replay and rollback proof before resuming."],
        "E": ["Pause distributed ambitions and return to rehearsal-only design review.", "Do not promote speculative distributed work into implementation until proofs and governance converge."],
    }
    payload = []
    for phase in phase_rows:
        phase_id = _token(phase.get("phase_id"))
        payload.append({"phase_id": phase_id, "title": _token(phase.get("title")), "hard_stop_conditions": list(phase_specific_conditions.get(phase_id, [])), "escalation_steps": list(escalation_steps.get(phase_id, [])), "manual_review_gate_ids": list(manual_gate_map.get(phase_id, [])), "do_not_prompt_through_unknowns": True})
    payload.extend(
        [
            {"phase_id": "D", "title": "Hot-reload and live replacement guard", "capability_id": "hot_swappable_renderers", "hard_stop_conditions": ["Stop implementing hot-reload work if lifecycle manager is not frozen.", "Stop implementing hot-reload work if state externalization is incomplete.", "Stop implementing hot-reload work if the module loader is not capability-negotiated."], "escalation_steps": ["Convert the uncertainty into manual design review with a cutover and rollback packet."], "manual_review_gate_ids": ["lifecycle_manager_semantics", "module_abi_boundaries"], "do_not_prompt_through_unknowns": True},
            {"phase_id": "E", "title": "Distributed simulation guard", "capability_id": "distributed_shard_relocation", "hard_stop_conditions": ["Stop implementing distributed simulation if event log and snapshot sync are not proven.", "Stop implementing distributed simulation if authority handoff model is absent.", "Stop implementing distributed simulation if proof-anchor quorum verification is absent."], "escalation_steps": ["Return to rehearsal-only design review and proof modeling before further implementation."], "manual_review_gate_ids": ["distributed_authority_model_changes"], "do_not_prompt_through_unknowns": True},
            {"phase_id": "A", "title": "Agent automation guard", "capability_id": "SIGMA.agent_automation", "hard_stop_conditions": ["Stop implementing agent automation if AGENTS governance is not mirrored into XStack.", "Stop implementing agent automation if the architecture graph is not frozen against the fresh snapshot.", "Stop implementing agent automation if task types are not mapped to validations."], "escalation_steps": ["Convert the gap into governance design review instead of extending prompt authority."], "manual_review_gate_ids": ["architecture_graph_changes", "semantic_contract_changes"], "do_not_prompt_through_unknowns": True},
        ]
    )
    return sorted(payload, key=lambda row: (PHASE_ORDER.get(_token(row.get("phase_id")), 99), _token(row.get("capability_id")), _token(row.get("title"))))


def _current_snapshot_summary(payloads: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    series_graph = dict(payloads.get("series_dependency_graph") or {})
    readiness = dict(payloads.get("readiness_matrix") or {})
    pipe = dict(payloads.get("pipe_dreams_matrix") or {})
    current = dict(series_graph.get("current_snapshot") or {})
    omega_state = dict(current.get("omega_artifact_state") or {})
    xi_state = dict(current.get("xi_artifact_state") or {})
    return {
        "ci_profile": _token(current.get("ci_profile")),
        "ci_strict_result": _token(current.get("ci_strict_result")),
        "architecture_graph_fingerprint": _token(current.get("architecture_graph_fingerprint")),
        "module_boundary_rules_fingerprint": _token(current.get("module_boundary_rules_fingerprint")),
        "repository_structure_lock_fingerprint": _token(current.get("repository_structure_lock_fingerprint")),
        "build_target_count": int(current.get("build_target_count", 0) or 0),
        "module_count": int(current.get("module_count", 0) or 0),
        "sanctioned_source_like_root_count": int(current.get("sanctioned_source_like_root_count", 0) or current.get("source_like_directory_count", 0) or 0),
        "omega_artifact_state": {key: bool(omega_state.get(key)) for key in sorted(omega_state)},
        "xi_artifact_state": {key: bool(xi_state.get(key)) for key in sorted(xi_state)},
        "pi_0_fingerprints": {"capability_dependency_graph": _token(payloads.get("capability_dependency_graph", {}).get("deterministic_fingerprint")), "pipe_dreams_matrix": _token(pipe.get("deterministic_fingerprint")), "readiness_matrix": _token(readiness.get("deterministic_fingerprint")), "series_dependency_graph": _token(series_graph.get("deterministic_fingerprint"))},
    }


def _series_execution_strategy_payload(payloads: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    priority_items = _priority_item_rows()
    readiness_index = {_token(row.get("capability_id")): dict(row) for row in payloads.get("readiness_matrix", {}).get("rows") or [] if _token(row.get("capability_id"))}
    pipe_index = {_token(row.get("dream_id")): dict(row) for row in payloads.get("pipe_dreams_matrix", {}).get("rows") or [] if _token(row.get("dream_id"))}
    capability_foundations = _capability_sources(readiness_index, pipe_index)
    snapshot_rows = _snapshot_work_items()
    readiness_counts = Counter(_token(row.get("planning_bucket")) for row in capability_foundations)
    payload = {
        "report_id": "pi.1.series_execution_strategy.v1",
        "current_snapshot": _current_snapshot_summary(payloads),
        "phase_order": list(PHASE_SEQUENCE),
        "series_execution_order": _series_execution_sequence(),
        "priority_bands": _priority_bands(priority_items),
        "foundation_primitives": _foundation_primitives(),
        "capability_foundations": capability_foundations,
        "pre_snapshot_safe_items": [dict(row) for row in snapshot_rows if row["classification"] == "pre_snapshot_safe"],
        "post_snapshot_required_items": [dict(row) for row in snapshot_rows if row["classification"] == "post_snapshot_required"],
        "overlap_policy": [
            {"rule_id": "series_overlap.sigma_upsilon", "description": "SIGMA and UPSILON may overlap after governance vocabulary is frozen, because policy and control-plane artifacts reinforce each other."},
            {"rule_id": "series_overlap.phi_planning_only", "description": "PHI planning may overlap with SIGMA and UPSILON, but PHI implementation waits for fresh snapshot mapping."},
            {"rule_id": "series_overlap.zeta_docs_only", "description": "ZETA work may overlap only as documentation and rehearsal design until phases A, B, and C complete."},
        ],
        "operating_model": [
            {"step": 1, "rule": "Docs and schemas first."},
            {"step": 2, "rule": "Registries and policy artifacts next."},
            {"step": 3, "rule": "Tooling and validators next."},
            {"step": 4, "rule": "Implementation only after validators exist."},
            {"step": 5, "rule": "Regression baselines and smoke harnesses before enabling by default."},
            {"step": 6, "rule": "Distribution and release only after convergence and archive checks."},
        ],
        "planning_bucket_counts": {key: int(readiness_counts.get(key, 0)) for key in sorted(readiness_counts)},
    }
    return _fingerprinted(payload)


def _foundation_phases_payload(phase_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    return _fingerprinted({"report_id": "pi.1.foundation_phases.v1", "phase_order": list(PHASE_SEQUENCE), "phases": [dict(row) for row in sorted(phase_rows, key=_phase_sort_key)]})


def _stop_conditions_payload(stop_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    return _fingerprinted({"report_id": "pi.1.stop_conditions.v1", "phase_order": list(PHASE_SEQUENCE), "entries": [dict(row) for row in stop_rows]})


def _manual_review_payload(gate_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    return _fingerprinted({"report_id": "pi.1.manual_review_gates.v1", "gates": [dict(row) for row in gate_rows]})


def _completed_artifact_labels(state: Mapping[str, object]) -> str:
    labels = sorted(_token(key) for key, value in (state or {}).items() if value)
    return ", ".join(labels) if labels else "none"


def render_series_execution_strategy(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("series_execution_strategy") or {})
    current_snapshot = dict(payload.get("current_snapshot") or {})
    lines = [_doc_header("Series Execution Strategy", "snapshot-anchored execution strategy after final repository re-audit"), "## Current Boundary", "", "This document is the post-XI master sequencing plan for SIGMA, PHI, UPSILON, and ZETA.", "It is planning only and anchors itself to the live Xi-8 and OMEGA-frozen repository, while still requiring fresh snapshot remapping before any repo-specific PHI, UPSILON wiring, or ZETA implementation begins.", "", "## Current Grounding", "", f"- Architecture graph v1 fingerprint: `{_token(current_snapshot.get('architecture_graph_fingerprint'))}`", f"- Module boundary rules fingerprint: `{_token(current_snapshot.get('module_boundary_rules_fingerprint'))}`", f"- Repository structure lock fingerprint: `{_token(current_snapshot.get('repository_structure_lock_fingerprint'))}`", f"- Xi artifact state: {_completed_artifact_labels(current_snapshot.get('xi_artifact_state') or {})}", f"- OMEGA artifact state: {_completed_artifact_labels(current_snapshot.get('omega_artifact_state') or {})}", f"- CI STRICT result: `{_token(current_snapshot.get('ci_strict_result'))}` via profile `{_token(current_snapshot.get('ci_profile'))}`", f"- Sanctioned source-like roots carried by policy: `{int(current_snapshot.get('sanctioned_source_like_root_count') or 0)}`", "", "## Series Order", "", "| Rank | Series | Why It Starts Here | Overlap |", "| --- | --- | --- | --- |"]
    for row in payload.get("series_execution_order") or []:
        lines.append("| `{}` | `{}` | {} | {} |".format(int(row.get("execution_rank", 0)), _token(row.get("series_id")), _token(row.get("why_now")), ", ".join(_token(item) for item in row.get("may_overlap_with") or []) or "none"))
    lines.extend(["", "## Priority Bands", ""])
    for band in payload.get("priority_bands") or []:
        lines.append(f"### Priority {int(band.get('priority_band', 0))} - {_token(band.get('label'))}")
        lines.append("")
        for item in band.get("items") or []:
            lines.append("- `{}`: {} [{} / phase {}].".format(_token(item.get("item_id")), _token(item.get("summary")), _token(item.get("series_id")), _token(item.get("phase_id"))))
        lines.append("")
    bucket_groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in payload.get("capability_foundations") or []:
        bucket_groups[_token(row.get("planning_bucket"))].append(dict(row))
    bucket_titles = {"foundation_ready": "Foundation-ready", "future_plausible": "Future-plausible", "not_yet_safe_to_implement": "Not yet safe to implement"}
    for bucket in sorted(bucket_groups, key=lambda value: PLANNING_BUCKET_ORDER.get(value, 99)):
        lines.append(f"## {bucket_titles.get(bucket, bucket)}")
        lines.append("")
        for row in bucket_groups[bucket][:8]:
            lines.append("- `{}`: phase `{}`, required foundations `{}`.".format(_token(row.get("capability_id")), _token(row.get("execution_phase")), ", ".join(_token(item) for item in row.get("required_foundations") or [])))
        lines.append("")
    lines.extend(["## How Work Should Be Executed", ""])
    for row in payload.get("operating_model") or []:
        lines.append(f"{int(row.get('step', 0))}. {_token(row.get('rule'))}")
    lines.extend(["", "## Capability-to-Foundation Highlights", "", "| Capability | Phase | Foundations |", "| --- | --- | --- |"])
    highlight_ids = {"hot_swappable_renderers", "live_save_migration", "live_protocol_upgrades", "mod_hot_activation", "partial_live_module_reload", "runtime_drift_detection", "release_rehearsal_sandbox", "distributed_shard_relocation", "restartless_core_engine_replacement"}
    highlight_rows = [row for row in payload.get("capability_foundations") or [] if _token(row.get("capability_id")) in highlight_ids]
    for row in sorted(highlight_rows, key=lambda item: _token(item.get("capability_id"))):
        lines.append("| `{}` | `{}` | {} |".format(_token(row.get("capability_id")), _token(row.get("execution_phase")), ", ".join(_token(item) for item in row.get("required_foundations") or [])))
    lines.append("")
    return "\n".join(lines)


def render_foundation_phases(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("foundation_phases") or {})
    lines = [_doc_header("Foundation Phases", "snapshot-anchored phase execution plan after repository remapping"), "## Phase Order", "", "The work proceeds through phases A through E. Later phases may be designed early but must not be implemented before their prerequisites are satisfied.", ""]
    for row in payload.get("phases") or []:
        lines.append(f"## Phase {_token(row.get('phase_id'))} - {_token(row.get('title'))}")
        lines.append("")
        lines.append(f"Objective: {_token(row.get('objective'))}")
        lines.append("")
        lines.append("Prerequisites:")
        for item in row.get("prerequisites") or []:
            lines.append(f"- {_token(item)}")
        lines.append("")
        lines.append("Completion criteria:")
        for item in row.get("completion_criteria") or []:
            lines.append(f"- {_token(item)}")
        lines.append("")
        lines.append("Blocked capabilities:")
        for item in row.get("blocked_capabilities") or []:
            lines.append(f"- {_token(item)}")
        lines.append("")
    return "\n".join(lines)


def render_stop_conditions(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("stop_conditions") or {})
    lines = [_doc_header("Stop Conditions and Escalation", "snapshot-anchored stop condition registry after final planning"), "## Hard Rule", "", "When a stop condition is hit, convert uncertainty into manual design review. Do not prompt through architectural unknowns.", ""]
    for row in payload.get("entries") or []:
        phase_id = _token(row.get("phase_id"))
        title = _token(row.get("title"))
        heading = f"## Phase {phase_id} - {title}" if not _token(row.get("capability_id")) else f"## Phase {phase_id} - {_token(row.get('capability_id'))}"
        lines.append(heading)
        lines.append("")
        lines.append("Stop conditions:")
        for item in row.get("hard_stop_conditions") or []:
            lines.append(f"- {_token(item)}")
        lines.append("")
        lines.append("Escalation:")
        for item in row.get("escalation_steps") or []:
            lines.append(f"- {_token(item)}")
        lines.append("")
    return "\n".join(lines)


def render_manual_review_gates(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("manual_review_gates") or {})
    lines = [_doc_header("Manual Review Gates", "snapshot-anchored manual review protocol after repository remapping"), "## Required Human Review Areas", "", "| Gate | Why Human Review Is Required | Required XStack Profile | Required Artifacts |", "| --- | --- | --- | --- |"]
    for row in payload.get("gates") or []:
        lines.append("| `{}` | {} | `{}` | {} |".format(_token(row.get("gate_id")), _token(row.get("why_human_review_required")), _token(row.get("required_xstack_profile")), "; ".join(_token(item) for item in row.get("required_artifacts") or [])))
    lines.append("")
    return "\n".join(lines)


def render_pre_post_snapshot(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("series_execution_strategy") or {})
    lines = [_doc_header("Pre and Post Snapshot Phases", "snapshot-anchored work split after final repository remapping"), "## Pre-snapshot-safe", "", "These items can be designed and documented now because they are architecture-level and do not depend on exact file boundaries.", ""]
    for row in payload.get("pre_snapshot_safe_items") or []:
        lines.append("- `{}` [{}]: {}".format(_token(row.get("work_id")), _token(row.get("series_id")), _token(row.get("reason"))))
    lines.extend(["", "## Post-snapshot-required", "", "These items must wait for the fresh repository snapshot because they depend on exact module, file, build, or service insertion points.", ""])
    for row in payload.get("post_snapshot_required_items") or []:
        lines.append("- `{}` [{}]: {}".format(_token(row.get("work_id")), _token(row.get("series_id")), _token(row.get("reason"))))
    lines.append("")
    return "\n".join(lines)


def render_pi_1_final(snapshot: Mapping[str, object]) -> str:
    strategy = dict(snapshot.get("series_execution_strategy") or {})
    phase_payload = dict(snapshot.get("foundation_phases") or {})
    stop_payload = dict(snapshot.get("stop_conditions") or {})
    review_payload = dict(snapshot.get("manual_review_gates") or {})
    current_snapshot = dict(strategy.get("current_snapshot") or {})
    lines = [_doc_header("PI-1 Final", "snapshot-anchored PI-1 audit summary after strategy generation"), "## Outcome", "", "- SIGMA, PHI, UPSILON, and ZETA dependencies are coherent.", "- Pre-snapshot versus post-snapshot work is explicitly separated.", "- Stop conditions exist for every phase and for the high-risk hot-reload, distributed, and agent-automation cases.", "- The strategy is grounded on the live Xi-8 freeze and current OMEGA verification state rather than a stale pre-freeze planning baseline.", "", "## Grounding", "", f"- Architecture graph v1 fingerprint: `{_token(current_snapshot.get('architecture_graph_fingerprint'))}`", f"- Module boundary rules fingerprint: `{_token(current_snapshot.get('module_boundary_rules_fingerprint'))}`", f"- Repository structure lock fingerprint: `{_token(current_snapshot.get('repository_structure_lock_fingerprint'))}`", f"- Xi artifact state: {_completed_artifact_labels(current_snapshot.get('xi_artifact_state') or {})}", f"- OMEGA artifact state: {_completed_artifact_labels(current_snapshot.get('omega_artifact_state') or {})}", f"- CI STRICT result: `{_token(current_snapshot.get('ci_strict_result'))}`", "", "## Fingerprints", "", f"- Series execution strategy: `{_token(strategy.get('deterministic_fingerprint'))}`", f"- Foundation phases: `{_token(phase_payload.get('deterministic_fingerprint'))}`", f"- Stop conditions: `{_token(stop_payload.get('deterministic_fingerprint'))}`", f"- Manual review gates: `{_token(review_payload.get('deterministic_fingerprint'))}`", "", "## Readiness", "", f"- Capability mappings: {len(list(strategy.get('capability_foundations') or []))}", f"- Phases: {len(list(phase_payload.get('phases') or []))}", f"- Manual review gates: {len(list(review_payload.get('gates') or []))}", "- Ready for PI-2 after the fresh repository snapshot is available.", ""]
    return "\n".join(lines)


def build_series_execution_strategy_snapshot(repo_root: str) -> dict[str, object]:
    payloads = _required_inputs(repo_root)
    phase_rows = _foundation_phase_rows()
    stop_rows = _stop_conditions(phase_rows)
    gate_rows = _manual_review_gates()
    return {"series_execution_strategy": _series_execution_strategy_payload(payloads), "foundation_phases": _foundation_phases_payload(phase_rows), "stop_conditions": _stop_conditions_payload(stop_rows), "manual_review_gates": _manual_review_payload(gate_rows)}


def write_series_execution_strategy_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    written[SERIES_EXECUTION_STRATEGY_REL] = _write_canonical_json(_repo_abs(root, SERIES_EXECUTION_STRATEGY_REL), dict(snapshot.get("series_execution_strategy") or {}))
    written[FOUNDATION_PHASES_REL] = _write_canonical_json(_repo_abs(root, FOUNDATION_PHASES_REL), dict(snapshot.get("foundation_phases") or {}))
    written[STOP_CONDITIONS_REL] = _write_canonical_json(_repo_abs(root, STOP_CONDITIONS_REL), dict(snapshot.get("stop_conditions") or {}))
    written[MANUAL_REVIEW_GATES_REL] = _write_canonical_json(_repo_abs(root, MANUAL_REVIEW_GATES_REL), dict(snapshot.get("manual_review_gates") or {}))
    written[SERIES_EXECUTION_STRATEGY_DOC_REL] = _write_text(_repo_abs(root, SERIES_EXECUTION_STRATEGY_DOC_REL), render_series_execution_strategy(snapshot) + "\n")
    written[FOUNDATION_PHASES_DOC_REL] = _write_text(_repo_abs(root, FOUNDATION_PHASES_DOC_REL), render_foundation_phases(snapshot) + "\n")
    written[STOP_CONDITIONS_DOC_REL] = _write_text(_repo_abs(root, STOP_CONDITIONS_DOC_REL), render_stop_conditions(snapshot) + "\n")
    written[MANUAL_REVIEW_GATES_DOC_REL] = _write_text(_repo_abs(root, MANUAL_REVIEW_GATES_DOC_REL), render_manual_review_gates(snapshot) + "\n")
    written[PRE_POST_SNAPSHOT_DOC_REL] = _write_text(_repo_abs(root, PRE_POST_SNAPSHOT_DOC_REL), render_pre_post_snapshot(snapshot) + "\n")
    written[PI_1_FINAL_REL] = _write_text(_repo_abs(root, PI_1_FINAL_REL), render_pi_1_final(snapshot) + "\n")
    return written


__all__ = [
    "FOUNDATION_PHASES_DOC_REL",
    "FOUNDATION_PHASES_REL",
    "MANUAL_REVIEW_GATES_DOC_REL",
    "MANUAL_REVIEW_GATES_REL",
    "OUTPUT_REL_PATHS",
    "PI_1_FINAL_REL",
    "PRE_POST_SNAPSHOT_DOC_REL",
    "SERIES_EXECUTION_STRATEGY_DOC_REL",
    "SERIES_EXECUTION_STRATEGY_REL",
    "STOP_CONDITIONS_DOC_REL",
    "STOP_CONDITIONS_REL",
    "build_series_execution_strategy_snapshot",
    "write_series_execution_strategy_snapshot",
]
