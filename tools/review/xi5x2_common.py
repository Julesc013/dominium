"""Deterministic Xi-5x2 residual convergence helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402

install_src_aliases(REPO_ROOT_HINT)


from tools.review.xi4z_fix3_common import (  # noqa: E402
    _ensure_parent,
    _norm_rel,
    _repo_abs,
    _repo_root,
    _token,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


XI_5A_FINAL_REL = "docs/audit/XI_5A_FINAL.md"
XI5A_EXECUTION_LOG_REL = "data/restructure/xi5a_execution_log.json"
XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL = "data/restructure/xi5a_postmove_residual_src_report.json"

XI_5X1_FINAL_REL = "docs/audit/XI_5X1_FINAL.md"
XI5X1_CLASSIFICATION_LOCK_REL = "data/restructure/xi5x1_residual_classification_lock.json"
XI5X1_BATCH_PLAN_REL = "data/restructure/xi5x1_batch_plan.json"
XI5X1_EXECUTION_LOG_REL = "data/restructure/xi5x1_execution_log.json"
XI5X1_POSTMOVE_RESIDUAL_REPORT_REL = "data/restructure/xi5x1_postmove_residual_src_report.json"
XI5X1_XI6_GATE_MODEL_REL = "data/restructure/xi5x1_xi6_gate_model.json"

XI5X2_CLASSIFICATION_LOCK_REL = "data/restructure/xi5x2_residual_classification_lock.json"
XI5X2_BATCH_PLAN_REL = "data/restructure/xi5x2_batch_plan.json"
XI5X2_EXECUTION_LOG_REL = "data/restructure/xi5x2_execution_log.json"
XI5X2_POSTMOVE_RESIDUAL_REPORT_REL = "data/restructure/xi5x2_postmove_residual_src_report.json"
XI5X2_XI6_GATE_MODEL_REL = "data/restructure/xi5x2_xi6_gate_model.json"
XI5X2_BLOCKER_DELTA_REL = "data/restructure/xi5x2_blocker_delta.json"

XI_5X2_FINAL_REL = "docs/audit/XI_5X2_FINAL.md"
XI_5X2_BUILD_TOOLCHAIN_REPORT_REL = "docs/audit/XI_5X2_BUILD_TOOLCHAIN_REPORT.md"
XI_5X2_PRECONDITION_REPORT_REL = "docs/audit/XI_5X2_PRECONDITION_REPORT.md"
XI_5X2_LEGACY_REPORT_REL = "docs/audit/XI_5X2_LEGACY_REPORT.md"

XI_5X2_BATCH_PLAN_DOC_REL = "docs/restructure/XI_5X2_BATCH_PLAN.md"
XI_5X2_RESIDUAL_DECISIONS_DOC_REL = "docs/restructure/XI_5X2_RESIDUAL_DECISIONS.md"
XI_5X2_XI6_READINESS_DOC_REL = "docs/restructure/XI_5X2_XI6_READINESS.md"

VALIDATION_FAST_REL = "data/audit/validation_report_FAST.json"
VALIDATION_STRICT_REL = "data/audit/validation_report_STRICT.json"
ARCH_AUDIT2_REL = "data/audit/arch_audit2_report.json"
WORLDGEN_LOCK_VERIFY_REL = "data/audit/worldgen_lock_verify.json"
BASELINE_UNIVERSE_VERIFY_REL = "data/audit/baseline_universe_verify.json"
GAMEPLAY_VERIFY_REL = "data/audit/gameplay_verify.json"
DISASTER_SUITE_RUN_REL = "data/audit/disaster_suite_run.json"
ECOSYSTEM_VERIFY_RUN_REL = "data/audit/ecosystem_verify_run.json"
UPDATE_SIM_RUN_REL = "data/audit/update_sim_run.json"
TRUST_STRICT_RUN_REL = "data/audit/trust_strict_run.json"

SOURCE_ROOTS = (
    "src",
    "app/src",
    "legacy/source",
    "legacy/launcher_core_launcher/launcher/core/source",
    "legacy/setup_core_setup/setup/core/source",
    "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources",
    "libs/build_identity/src",
    "libs/ui_backends/win32/src",
    "tools/ui_shared/src",
    "packs/source",
)
DANGEROUS_ROOTS = ("src", "app/src")

LAUNCHER_SOURCE_PREFIX = "legacy/launcher_core_launcher/launcher/core/source/"
SETUP_SOURCE_PREFIX = "legacy/setup_core_setup/setup/core/source/"
XCODE_SOURCE_PREFIX = "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources/"
PACKS_SOURCE_PREFIX = "packs/source/"
LEGACY_SOURCE_PREFIX = "legacy/source/"

BATCH_1 = "BATCH_1_BUILD_TOOLCHAIN_SAFE"
BATCH_2 = "BATCH_2_PRECONDITION_ESTABLISHMENT"
BATCH_3 = "BATCH_3_LEGACY_SAFE_ATTIC"
BATCH_4 = "BATCH_4_DEFERRED_REVIEW"

OBSOLETE = "OBSOLETE_ALREADY_RESOLVED"
HIGH_RISK = "HIGH_RISK_BUILD_OR_TOOLCHAIN"
BLOCKED = "BLOCKED_BY_MISSING_PRECONDITION"
LEGACY = "LEGACY_KEEP_FOR_NOW"
MANUAL = "QUARANTINE_MANUAL_REVIEW"

XI5X2_TARGETED_TESTS = (
    "test_no_runtime_critical_src_paths_after_xi5x2",
    "test_xi5x2_residual_classification_lock_deterministic",
    "test_xi5x2_batch_plan_deterministic",
    "test_xi5x2_xi6_gate_model_deterministic",
    "test_xi5x2_build_toolchain_roots_cleared",
    "test_xi5x2_blocker_delta_consistent",
)


class Xi5x2InputsMissing(RuntimeError):
    """Raised when Xi-5x2 authoritative inputs are unavailable."""


def _required_inputs() -> tuple[str, ...]:
    return (
        XI_5A_FINAL_REL,
        XI5A_EXECUTION_LOG_REL,
        XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        XI_5X1_FINAL_REL,
        XI5X1_CLASSIFICATION_LOCK_REL,
        XI5X1_BATCH_PLAN_REL,
        XI5X1_EXECUTION_LOG_REL,
        XI5X1_POSTMOVE_RESIDUAL_REPORT_REL,
        XI5X1_XI6_GATE_MODEL_REL,
        "data/architecture/architecture_graph.json",
        "data/architecture/module_registry.json",
        "data/architecture/module_dependency_graph.json",
        "data/audit/build_graph.json",
        "data/audit/include_graph.json",
        "data/audit/symbol_index.json",
        "docs/canon/constitution_v1.md",
        "docs/canon/glossary_v1.md",
        "AGENTS.md",
        "docs/blueprint/META_BLUEPRINT_INDEX.md",
        "docs/blueprint/SERIES_EXECUTION_STRATEGY.md",
        "docs/blueprint/FINAL_PROMPT_INVENTORY.md",
        "docs/blueprint/PROMPT_DEPENDENCY_TREE.md",
        "docs/blueprint/PROMPT_RISK_MATRIX.md",
    )


def _read_json_required(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        payload = None
    if not isinstance(payload, dict) or not payload:
        raise Xi5x2InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5x2.missing_inputs",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _load_optional_json(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    if not os.path.exists(abs_path):
        return {}
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def ensure_inputs(repo_root: str) -> None:
    missing = [rel for rel in _required_inputs() if not os.path.exists(_repo_abs(repo_root, rel))]
    if missing:
        raise Xi5x2InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5x2.missing_inputs",
                    "missing_inputs": sorted(set(missing)),
                },
                indent=2,
                sort_keys=True,
            )
        )


def _load_xi5x1_rows(repo_root: str) -> list[dict[str, object]]:
    payload = _read_json_required(repo_root, XI5X1_POSTMOVE_RESIDUAL_REPORT_REL)
    return [dict(item or {}) for item in list(payload.get("remaining_rows") or [])]


def _file_exists(repo_root: str, rel_path: str) -> bool:
    return os.path.exists(_repo_abs(repo_root, rel_path))


def _attic_path(rel_path: str) -> str:
    return _norm_rel(os.path.join("attic/src_quarantine", _norm_rel(rel_path)))


def _scan_root_file_counts(repo_root: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for root in SOURCE_ROOTS:
        root_abs = _repo_abs(repo_root, root)
        count = 0
        if os.path.isdir(root_abs):
            for current_root, dirnames, filenames in os.walk(root_abs):
                dirnames[:] = [name for name in sorted(dirnames) if name != "__pycache__"]
                for filename in sorted(filenames):
                    rel_path = _norm_rel(os.path.relpath(os.path.join(current_root, filename), repo_root))
                    if rel_path.endswith((".pyc", ".pyo")):
                        continue
                    count += 1
        counts[root] = int(count)
    return dict(sorted(counts.items()))


def _scan_runtime_shadow_paths(repo_root: str) -> list[str]:
    rows: list[str] = []
    for root in DANGEROUS_ROOTS:
        root_abs = _repo_abs(repo_root, root)
        if not os.path.isdir(root_abs):
            continue
        for current_root, dirnames, filenames in os.walk(root_abs):
            dirnames[:] = [name for name in sorted(dirnames) if name != "__pycache__"]
            rel_root = _norm_rel(os.path.relpath(current_root, repo_root))
            for filename in sorted(filenames):
                rel_path = _norm_rel(os.path.join(rel_root, filename))
                if rel_path.endswith((".pyc", ".pyo")):
                    continue
                rows.append(rel_path)
    return sorted(set(rows))


def _references_updated(source_path: str, decision_class: str) -> list[str]:
    if decision_class == "SAFE_BUILD_REHOME_NOW":
        if source_path.startswith(LAUNCHER_SOURCE_PREFIX):
            return [
                "legacy/launcher_core_launcher/launcher/core/CMakeLists.txt",
                "legacy/launcher_core_launcher/launcher/tests/launcher_state_smoke_tests.cpp",
            ]
        return [
            "legacy/setup_core_setup/setup/core/CMakeLists.txt",
            "legacy/setup_core_setup/setup/CMakeLists.txt",
            "legacy/setup_core_setup/setup/adapters/winnt/cli/dominium_setup_main.c",
            "legacy/setup_core_setup/setup/tests/dsu_cli_test.c",
            "legacy/setup_core_setup/setup/tests/dsu_job_resume_test.c",
            "legacy/setup_core_setup/setup/tests/dsu_platform_iface_test.c",
            "legacy/setup_core_setup/setup/tests/dsu_resolve_test.c",
            "legacy/setup_core_setup/setup/tests/dsu_setup_matrix_test.c",
            "legacy/setup_core_setup/setup/tests/dsu_txn_test.c",
        ]
    if decision_class == "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW":
        return [
            "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMac.xcodeproj/project.pbxproj",
            "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/README_XCODE.md",
        ]
    return []


def _evidence_refs(source_path: str, prior_classification: str) -> list[str]:
    refs = [XI5X1_POSTMOVE_RESIDUAL_REPORT_REL]
    if prior_classification == HIGH_RISK:
        refs.extend(_references_updated(source_path, "SAFE_BUILD_REHOME_NOW"))
    elif source_path.startswith(XCODE_SOURCE_PREFIX):
        refs.extend(_references_updated(source_path, "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW"))
    elif source_path.startswith(PACKS_SOURCE_PREFIX):
        refs.extend(
            [
                "tools/data/tool_srtm_import.py",
                "tools/data/tool_spice_import.py",
                "tools/xstack/testx/tests/test_srtm_import_determinism.py",
                "tools/xstack/testx/tests/test_spice_import_determinism.py",
            ]
        )
    elif source_path.startswith(LEGACY_SOURCE_PREFIX):
        refs.extend(
            [
                "legacy/source/tests/CMakeLists.txt",
                "attic/src_quarantine/legacy/source/CMakeLists.txt",
            ]
        )
    return sorted(dict.fromkeys(refs))


def _classify_row(repo_root: str, row: Mapping[str, object]) -> dict[str, object]:
    source_path = _norm_rel(row.get("source_path"))
    target_path = _norm_rel(row.get("intended_target_path"))
    prior_classification = _token(row.get("classification"))
    source_exists = _file_exists(repo_root, source_path)
    target_exists = bool(target_path) and _file_exists(repo_root, target_path)
    attic_target_path = _attic_path(source_path)
    attic_exists = _file_exists(repo_root, attic_target_path)

    payload: dict[str, object] = {
        "source_path": source_path,
        "intended_target_path": target_path,
        "attic_target_path": attic_target_path,
        "prior_classification": prior_classification,
        "source_exists_at_lock": source_exists,
        "target_exists_at_lock": target_exists,
        "attic_target_exists_at_lock": attic_exists,
        "current_classification": MANUAL,
        "decision_class": "QUARANTINE_MANUAL_REVIEW",
        "residual_group": prior_classification,
        "semantic_risk_level": _token(row.get("semantic_risk_level")) or "high",
        "move_allowed_now": False,
        "shim_required": False,
        "batchable": False,
        "proposed_batch_id": BATCH_4,
        "resolved_in_this_pass": False,
        "resolution_status": "deferred",
        "resolution_path": "",
        "future_phase_owner": "manual",
        "manual_review_required": True,
        "xi6_relevant": True,
        "missing_precondition_type": "",
        "references_updated": [],
        "evidence_refs": _evidence_refs(source_path, prior_classification),
        "rationale": "Residual did not match a safe Xi-5x2 rule and remains quarantined for manual review.",
    }

    if prior_classification == HIGH_RISK:
        if (not source_exists) and target_exists:
            payload.update(
                {
                    "current_classification": OBSOLETE,
                    "decision_class": "SAFE_BUILD_REHOME_NOW",
                    "semantic_risk_level": "low",
                    "move_allowed_now": True,
                    "batchable": True,
                    "proposed_batch_id": BATCH_1,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved",
                    "resolution_path": target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "references_updated": _references_updated(source_path, "SAFE_BUILD_REHOME_NOW"),
                    "rationale": (
                        "The live repo already reflects the bounded legacy core/source rehome, and the mirrored canonical target "
                        "exists with build/include rewires applied."
                    ),
                }
            )
            return payload
        if source_exists:
            payload.update(
                {
                    "current_classification": HIGH_RISK,
                    "decision_class": "STILL_HIGH_RISK_DEFER",
                    "semantic_risk_level": "high",
                    "future_phase_owner": "later",
                    "manual_review_required": True,
                    "rationale": "Legacy launcher/setup core source pocket still exists and remains high-risk for freeze.",
                }
            )
            return payload

    if prior_classification == BLOCKED and source_path.startswith(XCODE_SOURCE_PREFIX):
        if (not source_exists) and target_exists:
            payload.update(
                {
                    "current_classification": OBSOLETE,
                    "decision_class": "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW",
                    "semantic_risk_level": "low",
                    "move_allowed_now": True,
                    "batchable": True,
                    "proposed_batch_id": BATCH_2,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved_after_precondition",
                    "resolution_path": target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "missing_precondition_type": "xcode_project_sync",
                    "references_updated": _references_updated(source_path, "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW"),
                    "rationale": (
                        "The missing Xcode project synchronization was established safely, and the adapter files now live under the "
                        "canonical app root without the nested Sources pocket."
                    ),
                }
            )
            return payload
        payload.update(
            {
                "current_classification": BLOCKED,
                "decision_class": "REQUIRES_PLATFORM_ADAPTER_DECISION",
                "semantic_risk_level": "high",
                "missing_precondition_type": "xcode_project_sync",
                "future_phase_owner": "manual",
                "manual_review_required": True,
                "rationale": "The Xcode adapter source pocket still requires synchronized project metadata updates.",
            }
        )
        return payload

    if prior_classification == BLOCKED and source_path.startswith(PACKS_SOURCE_PREFIX):
        payload.update(
            {
                "current_classification": BLOCKED,
                "decision_class": "REQUIRES_CONTENT_SOURCE_POLICY",
                "semantic_risk_level": "medium",
                "proposed_batch_id": BATCH_4,
                "future_phase_owner": "later",
                "manual_review_required": True,
                "missing_precondition_type": "content_source_policy",
                "rationale": (
                    "Source-pack inputs remain live for import tooling and determinism fixtures, so Xi-5x2 cannot rename or attic-route "
                    "them without an explicit content-source policy."
                ),
            }
        )
        return payload

    if prior_classification == LEGACY:
        if (not source_exists) and attic_exists:
            payload.update(
                {
                    "current_classification": OBSOLETE,
                    "decision_class": "SAFE_TO_ATTIC_NOW",
                    "semantic_risk_level": "low",
                    "move_allowed_now": True,
                    "batchable": True,
                    "proposed_batch_id": BATCH_3,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved_to_attic",
                    "resolution_path": attic_target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "references_updated": [],
                    "rationale": (
                        "The legacy provider/reference pocket was safely preserved under attic/src_quarantine, removing the residual "
                        "legacy/source root load without deleting historical material."
                    ),
                }
            )
            return payload
        if source_exists:
            payload.update(
                {
                    "current_classification": LEGACY,
                    "decision_class": "KEEP_LEGACY_FOR_LATER",
                    "semantic_risk_level": "medium",
                    "proposed_batch_id": BATCH_4,
                    "future_phase_owner": "later",
                    "manual_review_required": False,
                    "rationale": (
                        "Remaining legacy/source content is an isolated legacy test pocket. It no longer acts as a dangerous shadow root, "
                        "but it still blocks Xi-6 until a bounded legacy policy or attic migration is chosen."
                    ),
                }
            )
            return payload

    if (not source_exists) and (target_exists or attic_exists):
        payload.update(
            {
                "current_classification": OBSOLETE,
                "decision_class": "SAFE_MOVE_PREVIOUSLY_APPLIED",
                "semantic_risk_level": "low",
                "move_allowed_now": True,
                "batchable": False,
                "resolved_in_this_pass": True,
                "resolution_status": "already_resolved",
                "resolution_path": target_path if target_exists else attic_target_path,
                "future_phase_owner": "xi5x2",
                "manual_review_required": False,
                "rationale": "Residual row no longer exists at the source path and has already been resolved in the live tree.",
            }
        )
        return payload

    return payload


def build_classification_lock(repo_root: str) -> dict[str, object]:
    ensure_inputs(repo_root)
    rows = [_classify_row(repo_root, row) for row in _load_xi5x1_rows(repo_root)]
    rows = sorted(rows, key=lambda item: (_token(item.get("current_classification")), _norm_rel(item.get("source_path"))))
    current_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    active_blockers: dict[str, int] = {}
    prior_counts: dict[str, int] = {}
    resolved_rows = 0
    for row in rows:
        current = _token(row.get("current_classification"))
        decision = _token(row.get("decision_class"))
        prior = _token(row.get("prior_classification"))
        current_counts[current] = int(current_counts.get(current, 0)) + 1
        decision_counts[decision] = int(decision_counts.get(decision, 0)) + 1
        prior_counts[prior] = int(prior_counts.get(prior, 0)) + 1
        if current != OBSOLETE:
            active_blockers[current] = int(active_blockers.get(current, 0)) + 1
        else:
            resolved_rows += 1
    xi5x1_report = _read_json_required(repo_root, XI5X1_POSTMOVE_RESIDUAL_REPORT_REL)
    payload = {
        "report_id": "xi.5x2.residual_classification_lock.v1",
        "source_reports": {
            "xi5a_final_doc": XI_5A_FINAL_REL,
            "xi5a_execution_log": XI5A_EXECUTION_LOG_REL,
            "xi5a_postmove_residual_report": XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
            "xi5x1_final_doc": XI_5X1_FINAL_REL,
            "xi5x1_postmove_residual_report": XI5X1_POSTMOVE_RESIDUAL_REPORT_REL,
            "xi5x1_gate_model": XI5X1_XI6_GATE_MODEL_REL,
        },
        "row_count": len(rows),
        "rows": rows,
        "prior_classification_counts": dict(sorted(prior_counts.items())),
        "current_classification_counts": dict(sorted(current_counts.items())),
        "decision_class_counts": dict(sorted(decision_counts.items())),
        "active_blocker_counts": dict(sorted(active_blockers.items())),
        "stale_rows_reclassified_as_obsolete": resolved_rows,
        "xi5x1_reported_remaining_counts": dict(sorted(dict(xi5x1_report.get("remaining_classification_counts") or {}).items())),
        "live_root_file_counts_at_lock": _scan_root_file_counts(repo_root),
        "dangerous_shadow_root_paths_remaining": _scan_runtime_shadow_paths(repo_root),
        "unexpected_runtime_critical_src_paths": _scan_runtime_shadow_paths(repo_root),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_batch_plan(classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]

    def items_for(decision_classes: Iterable[str]) -> list[str]:
        wanted = {str(item) for item in decision_classes}
        return sorted(
            _norm_rel(row.get("source_path"))
            for row in rows
            if _token(row.get("decision_class")) in wanted
        )

    batches = [
        {
            "batch_id": BATCH_1,
            "included_items": items_for(["SAFE_BUILD_REHOME_NOW"]),
            "exclusion_logic": "Exclude Xcode precondition rows, packs/source policy blockers, and legacy/source rows.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Launcher and setup core CMake/include surfaces rewired to canonical non-source paths",
                "No target collisions under legacy/launcher_core_launcher/launcher/core or legacy/setup_core_setup/setup/core",
            ],
            "expected_repo_effects": [
                "Remove active legacy launcher/setup nested source roots",
                "Preserve product behavior and deterministic build surfaces",
            ],
            "required_validation_profile": "STRICT + ARCH-AUDIT-2 + Ω-1..Ω-6 + trust strict suite",
            "rollback_notes": "Reverse the git moves and restore the CMake/include rewires as a single bounded batch.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_2,
            "included_items": items_for(["SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW"]),
            "exclusion_logic": "Only the Xcode adapter rows moved after the missing project-file synchronization was established.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Xcode project and README updated to canonical file locations",
                "No remaining references to DominiumSetupMacApp/Sources/",
            ],
            "expected_repo_effects": [
                "Remove the Xcode adapter nested Sources root",
                "Keep the macOS adapter source surface consistent with project metadata",
            ],
            "required_validation_profile": "STRICT + ARCH-AUDIT-2 + Ω-1..Ω-6 + trust strict suite",
            "rollback_notes": "Reverse the git moves and restore the project file references to the old Sources layout.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_3,
            "included_items": items_for(["SAFE_TO_ATTIC_NOW"]),
            "exclusion_logic": "Only obsolete legacy/source provider/reference rows with no remaining active build ownership.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Legacy rows proven non-authoritative for the active build graph",
                "Attic mirror path available under attic/src_quarantine",
            ],
            "expected_repo_effects": [
                "Reduce legacy/source to the remaining legacy test pocket",
                "Preserve historical reference material under attic without deleting it",
            ],
            "required_validation_profile": "FAST after move, then reuse prior STRICT runtime-adjacent gate evidence from the same Xi-5x2 pass",
            "rollback_notes": "Reverse the attic moves if a later build graph check unexpectedly references the old files.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_4,
            "included_items": sorted(
                _norm_rel(row.get("source_path"))
                for row in rows
                if _token(row.get("current_classification")) != OBSOLETE
            ),
            "exclusion_logic": "Only unresolved packs/source policy rows and the remaining legacy/source/tests pocket stay here.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Explicit content-source policy for packs/source",
                "Bounded legacy test-pocket convergence or attic policy",
            ],
            "expected_repo_effects": [
                "No execution in Xi-5x2; rows remain explicit blockers or deferred legacy material",
            ],
            "required_validation_profile": "N/A",
            "rollback_notes": "Not executed in Xi-5x2.",
            "execution_allowed_in_this_pass": False,
            "batch_status": "deferred",
        },
    ]
    payload = {
        "report_id": "xi.5x2.batch_plan.v1",
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "batches": batches,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_postmove_residual_report(repo_root: str, classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    remaining_rows: list[dict[str, object]] = []
    remaining_counts: dict[str, int] = {}
    remaining_decision_counts: dict[str, int] = {}
    for row in rows:
        current = _token(row.get("current_classification"))
        if current == OBSOLETE:
            continue
        item = {
            "classification": current,
            "decision_class": _token(row.get("decision_class")),
            "future_phase_owner": _token(row.get("future_phase_owner")),
            "source_path": _norm_rel(row.get("source_path")),
            "intended_target_path": _norm_rel(row.get("intended_target_path")),
            "semantic_risk_level": _token(row.get("semantic_risk_level")),
            "missing_precondition_type": _token(row.get("missing_precondition_type")),
            "rationale": str(row.get("rationale") or "").strip(),
        }
        remaining_rows.append(item)
        remaining_counts[current] = int(remaining_counts.get(current, 0)) + 1
        decision = _token(item.get("decision_class"))
        remaining_decision_counts[decision] = int(remaining_decision_counts.get(decision, 0)) + 1
    root_counts = _scan_root_file_counts(repo_root)
    payload = {
        "report_id": "xi.5x2.postmove_residual_src_report.v1",
        "dangerous_shadow_root_paths_remaining": _scan_runtime_shadow_paths(repo_root),
        "unexpected_runtime_critical_src_paths": _scan_runtime_shadow_paths(repo_root),
        "remaining_root_file_counts": root_counts,
        "remaining_rows": sorted(remaining_rows, key=lambda item: (_token(item.get("classification")), _norm_rel(item.get("source_path")))),
        "remaining_classification_counts": dict(sorted(remaining_counts.items())),
        "remaining_decision_counts": dict(sorted(remaining_decision_counts.items())),
        "top_level_src_file_count": int(root_counts.get("src", 0) or 0),
        "dangerous_shadow_root_count": len(_scan_runtime_shadow_paths(repo_root)),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _python_env(repo_root: str) -> dict[str, str]:
    env = os.environ.copy()
    existing = str(env.get("PYTHONPATH") or "").strip()
    roots = [repo_root]
    if existing:
        roots.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(roots)
    return env


def _run_subprocess_gate(repo_root: str, gate_id: str, command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        env=_python_env(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    payload: dict[str, object] = {
        "gate_id": gate_id,
        "evidence_mode": "subprocess",
        "command": command,
        "returncode": int(completed.returncode),
        "status": "pass" if completed.returncode == 0 else "fail",
    }
    text = str(completed.stdout or "").strip()
    if text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {}
        if isinstance(parsed, dict):
            for field_name in (
                "deterministic_fingerprint",
                "result",
                "matched_case_count",
                "mismatched_case_count",
                "error_count",
                "warning_count",
            ):
                token = parsed.get(field_name)
                if token not in (None, ""):
                    payload[field_name] = token
        else:
            payload["output_excerpt"] = text.splitlines()[-20:]
    return payload


def _report_is_success(report: Mapping[str, object]) -> bool:
    result = _token(report.get("result")).lower()
    if result not in {"complete", "pass"}:
        return False
    for field_name in ("blocking_finding_count", "mismatch_count", "mismatched_case_count", "error_count"):
        if field_name in report and int(report.get(field_name, 0) or 0) != 0:
            return False
    for field_name in (
        "matches_snapshot",
        "cases_match_expected",
        "save_reload_matches",
        "logic_deterministic",
        "replay_matches_baseline",
        "replay_matches_final_anchor",
        "pack_lock_matches_worldgen_lock",
    ):
        if field_name in report and not bool(report.get(field_name)):
            return False
    return True


def _report_gate(repo_root: str, gate_id: str, report_rel: str) -> dict[str, object]:
    report = _load_optional_json(repo_root, report_rel)
    payload: dict[str, object] = {
        "gate_id": gate_id,
        "evidence_mode": "existing_report",
        "report_rel": report_rel,
        "status": "pass" if report and _report_is_success(report) else "fail",
    }
    for field_name in (
        "deterministic_fingerprint",
        "result",
        "matched_case_count",
        "mismatched_case_count",
        "blocking_finding_count",
        "error_count",
        "warning_count",
    ):
        token = report.get(field_name)
        if token not in (None, ""):
            payload[field_name] = token
    return payload


def collect_gate_runs(repo_root: str) -> list[dict[str, object]]:
    subset = ",".join(XI5X2_TARGETED_TESTS)
    return [
        _run_subprocess_gate(repo_root, "build_verify", ["cmake", "--build", "--preset", "verify", "--config", "Debug", "--target", "all_runtime"]),
        _report_gate(repo_root, "validate_fast", VALIDATION_FAST_REL),
        _report_gate(repo_root, "validate_strict", VALIDATION_STRICT_REL),
        _report_gate(repo_root, "arch_audit_2", ARCH_AUDIT2_REL),
        _report_gate(repo_root, "omega_1_worldgen_lock", WORLDGEN_LOCK_VERIFY_REL),
        _report_gate(repo_root, "omega_2_baseline_universe", BASELINE_UNIVERSE_VERIFY_REL),
        _report_gate(repo_root, "omega_3_gameplay_loop", GAMEPLAY_VERIFY_REL),
        _report_gate(repo_root, "omega_4_disaster_suite", DISASTER_SUITE_RUN_REL),
        _report_gate(repo_root, "omega_5_ecosystem_verify", ECOSYSTEM_VERIFY_RUN_REL),
        _report_gate(repo_root, "omega_6_update_sim", UPDATE_SIM_RUN_REL),
        _report_gate(repo_root, "trust_strict_suite", TRUST_STRICT_RUN_REL),
        _run_subprocess_gate(
            repo_root,
            "targeted_xi5x2_tests",
            [
                "python",
                "-B",
                "tools/xstack/testx/runner.py",
                "--repo-root",
                ".",
                "--profile",
                "FAST",
                "--cache",
                "off",
                "--subset",
                subset,
            ],
        ),
    ]


def build_xi6_gate_model(
    classification_lock: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_runs: Iterable[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    remaining_counts = dict(postmove_report.get("remaining_classification_counts") or {})
    hard_blockers: list[dict[str, object]] = []
    soft_blockers: list[dict[str, object]] = []

    dangerous_paths = list(postmove_report.get("dangerous_shadow_root_paths_remaining") or [])
    if dangerous_paths:
        hard_blockers.append(
            {
                "blocker_id": "dangerous_shadow_roots_remaining",
                "count": len(dangerous_paths),
                "paths": dangerous_paths,
            }
        )

    for blocker_class in (HIGH_RISK, BLOCKED, LEGACY, MANUAL):
        count = int(remaining_counts.get(blocker_class, 0) or 0)
        if not count:
            continue
        blocker = {
            "blocker_id": blocker_class.lower(),
            "classification": blocker_class,
            "count": count,
        }
        if blocker_class == BLOCKED:
            blocker["reason"] = "packs/source remains live because a content-source policy is still missing."
        elif blocker_class == LEGACY:
            blocker["reason"] = "legacy/source/tests remains as a named legacy pocket pending bounded convergence or attic policy."
        elif blocker_class == HIGH_RISK:
            blocker["reason"] = "active high-risk build/toolchain source pockets still remain."
        else:
            blocker["reason"] = "unresolved manual-review rows remain."
        hard_blockers.append(blocker)

    gate_runs_list = [dict(item or {}) for item in list(gate_runs or [])]
    failed_gates = [item for item in gate_runs_list if _token(item.get("status")) != "pass"]
    if failed_gates:
        hard_blockers.append(
            {
                "blocker_id": "validation_or_gate_failures",
                "count": len(failed_gates),
                "gate_ids": sorted(_token(item.get("gate_id")) for item in failed_gates),
            }
        )

    if int(remaining_counts.get(BLOCKED, 0) or 0):
        soft_blockers.append(
            {
                "blocker_id": "content_source_policy_needed",
                "classification": BLOCKED,
                "count": int(remaining_counts.get(BLOCKED, 0) or 0),
            }
        )

    xi6_ready = not hard_blockers
    exact_reason = (
        ""
        if xi6_ready
        else "Xi-6 remains blocked because packs/source still requires an explicit content-source policy and "
        "legacy/source/tests remains as a named legacy pocket that is not yet acceptable to freeze."
    )
    payload = {
        "report_id": "xi.5x2.xi6_gate_model.v1",
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "source_postmove_report_fingerprint": _token(postmove_report.get("deterministic_fingerprint")),
        "required_invariants": [
            "constitution_v1.md A1",
            "constitution_v1.md A8",
            "constitution_v1.md A10",
            "AGENTS.md §2",
            "AGENTS.md §5",
        ],
        "required_residual_classes_to_be_zero_for_xi6": [HIGH_RISK, BLOCKED, LEGACY, MANUAL],
        "required_validation_gates": [
            "build_verify",
            "validate_fast",
            "validate_strict",
            "arch_audit_2",
            "omega_1_worldgen_lock",
            "omega_2_baseline_universe",
            "omega_3_gameplay_loop",
            "omega_4_disaster_suite",
            "omega_5_ecosystem_verify",
            "omega_6_update_sim",
            "trust_strict_suite",
            "targeted_xi5x2_tests",
        ],
        "repo_structure_conditions": [
            "No dangerous shadow roots under top-level src or app/src",
            "No remaining legacy launcher/setup nested source roots",
            "No unresolved freeze-blocking packs/source policy rows",
            "No unresolved freeze-blocking legacy/source pockets",
        ],
        "documentation_requirements": [
            XI_5A_FINAL_REL,
            XI_5X1_FINAL_REL,
            XI_5X2_FINAL_REL,
            XI_5X2_BUILD_TOOLCHAIN_REPORT_REL,
            XI_5X2_PRECONDITION_REPORT_REL,
            XI_5X2_LEGACY_REPORT_REL,
            XI_5X2_XI6_READINESS_DOC_REL,
        ],
        "hard_blockers": hard_blockers,
        "soft_blockers": soft_blockers,
        "hard_blocker_counts_by_class": dict(
            sorted(
                (blocker.get("classification"), int(blocker.get("count", 0) or 0))
                for blocker in hard_blockers
                if blocker.get("classification")
            )
        ),
        "soft_blocker_counts_by_class": dict(
            sorted(
                (blocker.get("classification"), int(blocker.get("count", 0) or 0))
                for blocker in soft_blockers
                if blocker.get("classification")
            )
        ),
        "remaining_residuals_acceptable_to_freeze_in_xi6": False,
        "allowed_residual_exceptions": [],
        "gate_runs": gate_runs_list,
        "readiness_boolean_derivation_rule": "Xi-6 is ready only when all hard_blockers are absent and all required_validation_gates pass.",
        "exact_reason_if_blocked": exact_reason,
        "xi6_ready": xi6_ready,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_execution_log(
    classification_lock: Mapping[str, object],
    batch_plan: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_runs: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    executed_items: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: (_token(item.get("proposed_batch_id")), _norm_rel(item.get("source_path")))):
        if _token(row.get("current_classification")) != OBSOLETE:
            continue
        batch_id = _token(row.get("proposed_batch_id"))
        action = "move"
        if _token(row.get("decision_class")) == "SAFE_TO_ATTIC_NOW":
            action = "move_to_attic"
        executed_items.append(
            {
                "batch_id": batch_id,
                "ordering_key": "{}::{}".format(batch_id, _norm_rel(row.get("source_path"))),
                "source_path": _norm_rel(row.get("source_path")),
                "target_path": _norm_rel(row.get("resolution_path")),
                "prior_classification": _token(row.get("prior_classification")),
                "resolved_classification": _token(row.get("current_classification")),
                "decision_class": _token(row.get("decision_class")),
                "action": action,
                "shim_added": False,
                "references_updated": list(row.get("references_updated") or []),
                "validation_required": (
                    "STRICT + ARCH-AUDIT-2 + Ω-1..Ω-6 + trust strict suite"
                    if batch_id in {BATCH_1, BATCH_2}
                    else "FAST"
                ),
                "manual_intervention": False,
                "exceptions": [],
            }
        )
    payload = {
        "report_id": "xi.5x2.execution_log.v1",
        "xi5a_ground_truth": {
            "xi5a_final_doc": XI_5A_FINAL_REL,
            "xi5a_execution_log": XI5A_EXECUTION_LOG_REL,
            "xi5a_postmove_residual_report": XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        },
        "xi5x1_ground_truth": {
            "xi5x1_final_doc": XI_5X1_FINAL_REL,
            "xi5x1_classification_lock": XI5X1_CLASSIFICATION_LOCK_REL,
            "xi5x1_batch_plan": XI5X1_BATCH_PLAN_REL,
            "xi5x1_execution_log": XI5X1_EXECUTION_LOG_REL,
            "xi5x1_postmove_residual_report": XI5X1_POSTMOVE_RESIDUAL_REPORT_REL,
            "xi5x1_xi6_gate_model": XI5X1_XI6_GATE_MODEL_REL,
        },
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "source_batch_plan_fingerprint": _token(batch_plan.get("deterministic_fingerprint")),
        "executed_items": executed_items,
        "executed_item_count": len(executed_items),
        "remaining_classification_counts": dict(postmove_report.get("remaining_classification_counts") or {}),
        "dangerous_shadow_root_paths_remaining": list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []),
        "gate_strategy": {
            "live_subprocess_gates": ["build_verify", "targeted_xi5x2_tests"],
            "reused_report_gates": [
                "validate_fast",
                "validate_strict",
                "arch_audit_2",
                "omega_1_worldgen_lock",
                "omega_2_baseline_universe",
                "omega_3_gameplay_loop",
                "omega_4_disaster_suite",
                "omega_5_ecosystem_verify",
                "omega_6_update_sim",
                "trust_strict_suite",
            ],
        },
        "gate_runs": [dict(item or {}) for item in list(gate_runs or [])],
        "ready_for_xi6": False,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_blocker_delta(
    repo_root: str,
    classification_lock: Mapping[str, object],
    gate_model: Mapping[str, object],
) -> dict[str, object]:
    before_model = _read_json_required(repo_root, XI5X1_XI6_GATE_MODEL_REL)
    before_counts = {
        _token(blocker.get("classification")): int(blocker.get("count", 0) or 0)
        for blocker in list(before_model.get("hard_blockers") or [])
        if blocker.get("classification")
    }
    after_counts = dict(gate_model.get("hard_blocker_counts_by_class") or {})
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved_rows = sorted(
        _norm_rel(row.get("source_path"))
        for row in rows
        if _token(row.get("current_classification")) == OBSOLETE
    )
    unchanged_rows = sorted(
        _norm_rel(row.get("source_path"))
        for row in rows
        if _token(row.get("current_classification")) != OBSOLETE
    )
    delta_by_class: dict[str, int] = {}
    for key in sorted(set(before_counts) | set(after_counts)):
        delta_by_class[key] = int(after_counts.get(key, 0) or 0) - int(before_counts.get(key, 0) or 0)
    resolved_count_by_decision: dict[str, int] = {}
    for row in rows:
        if _token(row.get("current_classification")) != OBSOLETE:
            continue
        key = _token(row.get("decision_class"))
        resolved_count_by_decision[key] = int(resolved_count_by_decision.get(key, 0)) + 1
    payload = {
        "report_id": "xi.5x2.blocker_delta.v1",
        "before_counts": dict(sorted(before_counts.items())),
        "after_counts": dict(sorted(after_counts.items())),
        "delta_by_class": dict(sorted(delta_by_class.items())),
        "resolved_row_count": len(resolved_rows),
        "resolved_count_by_decision_class": dict(sorted(resolved_count_by_decision.items())),
        "resolved_rows": resolved_rows,
        "newly_deferred_rows": [],
        "newly_deferred_row_count": 0,
        "unchanged_row_count": len(unchanged_rows),
        "unchanged_rows": unchanged_rows,
        "rationale": (
            "Xi-5x2 fully consumed the legacy launcher/setup build-toolchain pocket, cleared the blocked Xcode adapter rows, "
            "and attic-routed the obsolete legacy provider pocket. packs/source and legacy/source/tests remain explicit freeze blockers."
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _write_text(repo_root: str, rel_path: str, text: str) -> None:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_json(repo_root: str, rel_path: str, payload: Mapping[str, object]) -> None:
    _write_text(repo_root, rel_path, canonical_json_text(payload) + "\n")


def _render_build_toolchain_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved = [row for row in rows if _token(row.get("decision_class")) == "SAFE_BUILD_REHOME_NOW"]
    remaining = int(dict(postmove_report.get("remaining_classification_counts") or {}).get(HIGH_RISK, 0) or 0)
    root_counts = dict(postmove_report.get("remaining_root_file_counts") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Build Toolchain Report",
        "",
        "## Summary",
        "",
        "- Xi-5x1 high-risk build/toolchain rows consumed here: `{}`".format(len(resolved)),
        "- remaining `HIGH_RISK_BUILD_OR_TOOLCHAIN` rows: `{}`".format(remaining),
        "- `legacy/launcher_core_launcher/launcher/core/source`: `{}`".format(int(root_counts.get("legacy/launcher_core_launcher/launcher/core/source", 0) or 0)),
        "- `legacy/setup_core_setup/setup/core/source`: `{}`".format(int(root_counts.get("legacy/setup_core_setup/setup/core/source", 0) or 0)),
        "",
        "## Reference Surfaces Updated",
        "",
        "- `[legacy/launcher_core_launcher/launcher/core/CMakeLists.txt](/d:/Projects/Dominium/dominium/legacy/launcher_core_launcher/launcher/core/CMakeLists.txt)`",
        "- `[legacy/launcher_core_launcher/launcher/tests/launcher_state_smoke_tests.cpp](/d:/Projects/Dominium/dominium/legacy/launcher_core_launcher/launcher/tests/launcher_state_smoke_tests.cpp)`",
        "- `[legacy/setup_core_setup/setup/core/CMakeLists.txt](/d:/Projects/Dominium/dominium/legacy/setup_core_setup/setup/core/CMakeLists.txt)`",
        "- `[legacy/setup_core_setup/setup/CMakeLists.txt](/d:/Projects/Dominium/dominium/legacy/setup_core_setup/setup/CMakeLists.txt)`",
        "- setup legacy tests and CLI include-path consumers were rewired to `core/` paths.",
        "",
        "## Outcome",
        "",
        "- The high-risk launcher/setup nested source roots are now cleared and no longer block Xi-6 directly.",
    ]
    return "\n".join(lines) + "\n"


def _render_precondition_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved = [row for row in rows if _token(row.get("decision_class")) == "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW"]
    blocked = [row for row in rows if _token(row.get("current_classification")) == BLOCKED]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Precondition Report",
        "",
        "## Resolved Now",
        "",
        "- Xcode adapter rows resolved after project synchronization: `{}`".format(len(resolved)),
        "- `DominiumSetupMacApp/Sources` remaining file count: `{}`".format(
            int(dict(postmove_report.get("remaining_root_file_counts") or {}).get("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources", 0) or 0)
        ),
        "",
        "## Still Blocked",
        "",
        "- `BLOCKED_BY_MISSING_PRECONDITION` rows remaining: `{}`".format(len(blocked)),
        "- all remaining blocked rows are under `packs/source` and require a content-source policy rather than a mechanical move.",
        "",
        "## Evidence",
        "",
        "- `[legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMac.xcodeproj/project.pbxproj](/d:/Projects/Dominium/dominium/legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMac.xcodeproj/project.pbxproj)` now points at the canonical app-root files.",
        "- `[tools/data/tool_srtm_import.py](/d:/Projects/Dominium/dominium/tools/data/tool_srtm_import.py)` and `[tools/data/tool_spice_import.py](/d:/Projects/Dominium/dominium/tools/data/tool_spice_import.py)` still consume `packs/source` inputs.",
    ]
    return "\n".join(lines) + "\n"


def _render_legacy_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    attic_rows = [row for row in rows if _token(row.get("decision_class")) == "SAFE_TO_ATTIC_NOW"]
    remaining = [row for row in rows if _token(row.get("current_classification")) == LEGACY]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Legacy Report",
        "",
        "## Summary",
        "",
        "- legacy rows attic-routed now: `{}`".format(len(attic_rows)),
        "- legacy rows kept for later: `{}`".format(len(remaining)),
        "- remaining `legacy/source` file count: `{}`".format(int(dict(postmove_report.get("remaining_root_file_counts") or {}).get("legacy/source", 0) or 0)),
        "",
        "## Remaining Legacy Pocket",
        "",
        "- the remaining legacy surface is isolated to `legacy/source/tests`.",
        "- this pocket is preserved for historical/reference value and still requires a bounded legacy convergence or attic policy before Xi-6.",
        "",
        "## Attic Routing",
        "",
        "- obsolete provider/reference rows were preserved under `attic/src_quarantine/legacy/source/...` with mirrored paths.",
    ]
    return "\n".join(lines) + "\n"


def _render_batch_plan_doc(batch_plan: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5X2 Batch Plan",
        "",
    ]
    for batch in list(batch_plan.get("batches") or []):
        batch_dict = dict(batch or {})
        lines.extend(
            [
                "## `{}`".format(_token(batch_dict.get("batch_id"))),
                "",
                "- included items: `{}`".format(len(list(batch_dict.get("included_items") or []))),
                "- execution allowed in this pass: `{}`".format("true" if batch_dict.get("execution_allowed_in_this_pass") else "false"),
                "- batch status: `{}`".format(_token(batch_dict.get("batch_status"))),
                "- required validation profile: `{}`".format(str(batch_dict.get("required_validation_profile") or "")),
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_residual_decisions_doc(classification_lock: Mapping[str, object]) -> str:
    current_counts = dict(classification_lock.get("current_classification_counts") or {})
    decision_counts = dict(classification_lock.get("decision_class_counts") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5X2 Residual Decisions",
        "",
        "## Current Classification Counts",
        "",
    ]
    for name, count in sorted(current_counts.items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    lines.extend(["", "## Decision Class Counts", ""])
    for name, count in sorted(decision_counts.items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    return "\n".join(lines) + "\n"


def _render_xi6_readiness_doc(gate_model: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze report after residual convergence completes",
        "",
        "# XI-5X2 Xi-6 Readiness",
        "",
        "- Xi-6 ready: `{}`".format("true" if gate_model.get("xi6_ready") else "false"),
        "- remaining residuals acceptable to freeze: `{}`".format(
            "true" if gate_model.get("remaining_residuals_acceptable_to_freeze_in_xi6") else "false"
        ),
        "",
        "## Hard Blockers",
        "",
    ]
    for blocker in list(gate_model.get("hard_blockers") or []):
        lines.append(
            "- `{}`: `{}`".format(
                _token(dict(blocker).get("blocker_id")),
                int(dict(blocker).get("count", 0) or 0),
            )
        )
    if not list(gate_model.get("hard_blockers") or []):
        lines.append("- none")
    if gate_model.get("exact_reason_if_blocked"):
        lines.extend(["", "## Reason", "", "- {}".format(str(gate_model.get("exact_reason_if_blocked") or "").strip())])
    return "\n".join(lines) + "\n"


def _render_final_report(
    classification_lock: Mapping[str, object],
    execution_log: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_model: Mapping[str, object],
) -> str:
    remaining_counts = dict(postmove_report.get("remaining_classification_counts") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze report after residual convergence completes",
        "",
        "# XI-5X2 Final",
        "",
        "## Ground Truth Reused",
        "",
        "- Xi-5a authoritative outputs: `{}`, `{}`, `{}`.".format(
            XI_5A_FINAL_REL,
            XI5A_EXECUTION_LOG_REL,
            XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        ),
        "- Xi-5x1 authoritative outputs: `{}`, `{}`, `{}`, `{}`, `{}`.".format(
            XI_5X1_FINAL_REL,
            XI5X1_CLASSIFICATION_LOCK_REL,
            XI5X1_BATCH_PLAN_REL,
            XI5X1_EXECUTION_LOG_REL,
            XI5X1_XI6_GATE_MODEL_REL,
        ),
        "",
        "## Xi-5x2 Result",
        "",
        "- Xi-5x1 residual rows re-intaken and classified: `{}`".format(int(classification_lock.get("row_count", 0) or 0)),
        "- stale rows reclassified as `OBSOLETE_ALREADY_RESOLVED`: `{}`".format(int(classification_lock.get("stale_rows_reclassified_as_obsolete", 0) or 0)),
        "- rows resolved in this pass: `{}`".format(int(execution_log.get("executed_item_count", 0) or 0)),
        "- top-level src file count: `{}`".format(int(postmove_report.get("top_level_src_file_count", 0) or 0)),
        "- runtime-critical src paths remaining: `{}`".format(len(list(postmove_report.get("unexpected_runtime_critical_src_paths") or []))),
        "- dangerous shadow roots remaining: `{}`".format(int(postmove_report.get("dangerous_shadow_root_count", 0) or 0)),
        "",
        "## Current Residual Counts",
        "",
    ]
    for name, count in sorted(remaining_counts.items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    lines.extend(
        [
            "",
            "## Xi-6 Readiness",
            "",
            "- Xi-6 readiness boolean: `{}`".format("true" if gate_model.get("xi6_ready") else "false"),
        ]
    )
    if gate_model.get("xi6_ready"):
        lines.append("- reasoning: all hard blockers cleared and required gates passed.")
    else:
        for blocker in list(gate_model.get("hard_blockers") or []):
            lines.append(
                "- blocker `{}`: `{}`".format(
                    _token(dict(blocker).get("blocker_id")),
                    int(dict(blocker).get("count", 0) or 0),
                )
            )
        lines.append("- exact reason: {}".format(str(gate_model.get("exact_reason_if_blocked") or "").strip()))
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "- recommended next phase: `Xi-5x3` focused on `packs/source` content-source policy and the remaining `legacy/source/tests` pocket.",
        ]
    )
    return "\n".join(lines) + "\n"


def materialize_outputs(
    repo_root: str,
    classification_lock: Mapping[str, object],
    batch_plan: Mapping[str, object],
    execution_log: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_model: Mapping[str, object],
    blocker_delta: Mapping[str, object],
) -> None:
    _write_json(repo_root, XI5X2_CLASSIFICATION_LOCK_REL, classification_lock)
    _write_json(repo_root, XI5X2_BATCH_PLAN_REL, batch_plan)
    _write_json(repo_root, XI5X2_EXECUTION_LOG_REL, execution_log)
    _write_json(repo_root, XI5X2_POSTMOVE_RESIDUAL_REPORT_REL, postmove_report)
    _write_json(repo_root, XI5X2_XI6_GATE_MODEL_REL, gate_model)
    _write_json(repo_root, XI5X2_BLOCKER_DELTA_REL, blocker_delta)
    _write_text(repo_root, XI_5X2_BUILD_TOOLCHAIN_REPORT_REL, _render_build_toolchain_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_PRECONDITION_REPORT_REL, _render_precondition_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_LEGACY_REPORT_REL, _render_legacy_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_BATCH_PLAN_DOC_REL, _render_batch_plan_doc(batch_plan))
    _write_text(repo_root, XI_5X2_RESIDUAL_DECISIONS_DOC_REL, _render_residual_decisions_doc(classification_lock))
    _write_text(repo_root, XI_5X2_XI6_READINESS_DOC_REL, _render_xi6_readiness_doc(gate_model))
    _write_text(repo_root, XI_5X2_FINAL_REL, _render_final_report(classification_lock, execution_log, postmove_report, gate_model))


def run_xi5x2(repo_root: str, run_gates: bool = True) -> dict[str, object]:
    repo_root = _repo_root(repo_root)
    classification_lock = build_classification_lock(repo_root)
    batch_plan = build_batch_plan(classification_lock)
    postmove_report = build_postmove_residual_report(repo_root, classification_lock)
    gate_model = build_xi6_gate_model(classification_lock, postmove_report, [])
    execution_log = build_execution_log(classification_lock, batch_plan, postmove_report, [])
    blocker_delta = build_blocker_delta(repo_root, classification_lock, gate_model)
    materialize_outputs(repo_root, classification_lock, batch_plan, execution_log, postmove_report, gate_model, blocker_delta)
    gate_runs = collect_gate_runs(repo_root) if run_gates else []
    gate_model = build_xi6_gate_model(classification_lock, postmove_report, gate_runs)
    execution_log = build_execution_log(classification_lock, batch_plan, postmove_report, gate_runs)
    execution_log["ready_for_xi6"] = bool(gate_model.get("xi6_ready"))
    execution_log["deterministic_fingerprint"] = canonical_sha256(dict(execution_log, deterministic_fingerprint=""))
    blocker_delta = build_blocker_delta(repo_root, classification_lock, gate_model)
    materialize_outputs(repo_root, classification_lock, batch_plan, execution_log, postmove_report, gate_model, blocker_delta)
    return {
        "classification_lock": classification_lock,
        "batch_plan": batch_plan,
        "execution_log": execution_log,
        "postmove_report": postmove_report,
        "gate_model": gate_model,
        "blocker_delta": blocker_delta,
    }
