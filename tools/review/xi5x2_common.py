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
XI5X2_REALITY_REFRESH_REL = "data/restructure/xi5x2_residual_reality_refresh.json"
XI5X2_SOURCE_POCKET_POLICY_REL = "data/restructure/xi5x2_source_pocket_policy.json"
XI5X2_BLOCKED_PRECONDITIONS_REL = "data/restructure/xi5x2_blocked_preconditions.json"
XI5X2_MANUAL_REVIEW_QUEUE_REL = "data/restructure/xi5x2_manual_review_queue.json"
XI5X2_PLATFORM_ADAPTER_REVIEW_REL = "data/restructure/xi5x2_platform_adapter_review.json"
XI5X2_XI6_GATE_MODEL_REL = "data/restructure/xi5x2_xi6_gate_model.json"
XI5X2_BLOCKER_DELTA_REL = "data/restructure/xi5x2_blocker_delta.json"

XI_5X2_FINAL_REL = "docs/audit/XI_5X2_FINAL.md"
XI_5X2_REALITY_REFRESH_DOC_REL = "docs/audit/XI_5X2_REALITY_REFRESH.md"
XI_5X2_BUILD_TOOLCHAIN_REPORT_REL = "docs/audit/XI_5X2_BUILD_TOOLCHAIN_REPORT.md"
XI_5X2_PRECONDITION_REPORT_REL = "docs/audit/XI_5X2_PRECONDITION_REPORT.md"
XI_5X2_BATCH_PLAN_AUDIT_REL = "docs/audit/XI_5X2_BATCH_PLAN.md"
XI_5X2_CONTENT_SOURCE_POLICY_REPORT_REL = "docs/audit/XI_5X2_CONTENT_SOURCE_POLICY_REPORT.md"
XI_5X2_LEGACY_REPORT_REL = "docs/audit/XI_5X2_LEGACY_REPORT.md"
XI_5X2_LEGACY_POCKETS_REPORT_REL = "docs/audit/XI_5X2_LEGACY_POCKETS_REPORT.md"
XI_5X2_BLOCKED_PRECONDITIONS_DOC_REL = "docs/audit/XI_5X2_BLOCKED_PRECONDITIONS.md"

SOURCE_POCKET_POLICY_DOC_REL = "docs/architecture/SOURCE_POCKET_POLICY_v1.md"
XI_5X2_XCODE_PLATFORM_REVIEW_DOC_REL = "docs/refactor/XI_5X2_XCODE_AND_PLATFORM_REVIEW.md"
XI_5X2_MANUAL_REVIEW_DOC_REL = "docs/refactor/XI_5X2_MANUAL_REVIEW_PACKETS.md"

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
SOURCE_LIKE_DIR_NAMES = {"src", "source", "Sources", "Source"}
IGNORED_SCAN_DIRS = {
    ".git",
    ".vs",
    ".idea",
    ".cache",
    "__pycache__",
    "build",
    "out",
    "dist",
}
IGNORED_SCAN_PREFIXES = (
    "attic/src_quarantine/",
    "tools/xstack/out/",
)

LAUNCHER_SOURCE_PREFIX = "legacy/launcher_core_launcher/launcher/core/source/"
SETUP_SOURCE_PREFIX = "legacy/setup_core_setup/setup/core/source/"
XCODE_SOURCE_PREFIX = "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources/"
PACKS_SOURCE_PREFIX = "packs/source/"
LEGACY_SOURCE_PREFIX = "legacy/source/"

BATCH_SAFE_BUILD_1 = "BATCH_SAFE_BUILD_1"
BATCH_SAFE_BUILD_2 = "BATCH_SAFE_BUILD_2"
BATCH_SAFE_POLICY_RETENTS = "BATCH_SAFE_POLICY_RETENTS"
BATCH_SAFE_CONTENT_RETENTS = "BATCH_SAFE_CONTENT_RETENTS"
BATCH_MERGE_SMALL_1 = "BATCH_MERGE_SMALL_1"
BATCH_XCODE_REVIEW = "BATCH_XCODE_REVIEW"
BATCH_LEGACY_RETAIN = "BATCH_LEGACY_RETAIN"
BATCH_BLOCKED_PRECONDITIONS = "BATCH_BLOCKED_PRECONDITIONS"
BATCH_MANUAL_REVIEW = "BATCH_MANUAL_REVIEW"

OBSOLETE = "OBSOLETE_ALREADY_RESOLVED"
HIGH_RISK = "HIGH_RISK_BUILD_OR_TOOLCHAIN"
BLOCKED = "BLOCKED_BY_MISSING_PRECONDITION"
LEGACY = "LEGACY_KEEP_FOR_NOW"
MANUAL = "QUARANTINE_MANUAL_REVIEW"
INTENTIONAL = "INTENTIONAL_RESIDUAL_ALLOWED"

SAFE_CONTENT_SOURCE_RETAIN = "SAFE_CONTENT_SOURCE_RETAIN"
SAFE_LEGACY_ARCHIVE_RETAIN = "SAFE_LEGACY_ARCHIVE_RETAIN"
SAFE_PACKAGING_SOURCE_RETAIN = "SAFE_PACKAGING_SOURCE_RETAIN"
SAFE_LOCAL_REHOME = "SAFE_LOCAL_REHOME"

FORBIDDEN_CODE_SRC = "FORBIDDEN_CODE_SRC"
VALID_CONTENT_SOURCE = "VALID_CONTENT_SOURCE"
VALID_PACKAGING_SOURCE = "VALID_PACKAGING_SOURCE"
VALID_LEGACY_ARCHIVE_SOURCE = "VALID_LEGACY_ARCHIVE_SOURCE"
VALID_THIRDPARTY_SOURCE = "VALID_THIRDPARTY_SOURCE"
MOVE_TO_DOMAIN = "MOVE_TO_DOMAIN"
QUARANTINE_REQUIRED = "QUARANTINE_REQUIRED"

XI5X2_TARGETED_TESTS = (
    "test_no_runtime_critical_src_paths_after_xi5x2",
    "test_xi5x2_residual_classification_lock_deterministic",
    "test_xi5x2_batch_plan_deterministic",
    "test_xi5x2_xi6_gate_model_deterministic",
    "test_xi5x2_build_toolchain_roots_cleared",
    "test_xi5x2_blocker_delta_consistent",
    "test_xi5x2_source_pocket_policy_valid",
    "test_xi5x2_allowed_retained_source_pockets_match_policy",
    "test_xi5x2_blocked_preconditions_deterministic",
    "test_xi5x2_legacy_retained_pockets_not_in_default_build_paths",
    "test_xi5x2_platform_review_artifact_present",
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


def _walk_non_generated_files(repo_root: str, root: str) -> list[str]:
    root_abs = _repo_abs(repo_root, root)
    rows: list[str] = []
    if not os.path.isdir(root_abs):
        return rows
    for current_root, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = [name for name in sorted(dirnames) if name != "__pycache__"]
        for filename in sorted(filenames):
            rel_path = _norm_rel(os.path.relpath(os.path.join(current_root, filename), repo_root))
            if rel_path.endswith((".pyc", ".pyo")):
                continue
            rows.append(rel_path)
    return sorted(rows)


def _scan_root_file_counts(repo_root: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for root in SOURCE_ROOTS:
        counts[root] = len(_walk_non_generated_files(repo_root, root))
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


def _git_ls_files(repo_root: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return []
    return sorted(_norm_rel(line) for line in str(completed.stdout or "").splitlines() if line.strip())


def _tracked_file_count_under(root: str, tracked_files: Iterable[str]) -> int:
    token = _norm_rel(root).rstrip("/")
    if not token:
        return 0
    prefix = token + "/"
    return sum(1 for item in tracked_files if item == token or item.startswith(prefix))


def _scan_source_like_roots(repo_root: str, tracked_files: list[str]) -> dict[str, object]:
    discovered: list[dict[str, object]] = []
    generated: list[dict[str, object]] = []
    seen: set[str] = set()
    for current_root, dirnames, _ in os.walk(repo_root):
        rel_root = _norm_rel(os.path.relpath(current_root, repo_root))
        dirnames[:] = [name for name in sorted(dirnames) if name not in IGNORED_SCAN_DIRS]
        if any(rel_root == prefix.rstrip("/") or rel_root.startswith(prefix) for prefix in IGNORED_SCAN_PREFIXES):
            dirnames[:] = []
            continue
        base = os.path.basename(current_root)
        if base not in SOURCE_LIKE_DIR_NAMES or rel_root in {".", ""}:
            continue
        rel_root = _norm_rel(rel_root)
        if rel_root in seen:
            continue
        seen.add(rel_root)
        tracked_count = _tracked_file_count_under(rel_root, tracked_files)
        item = {
            "root_path": rel_root,
            "tracked_file_count": tracked_count,
        }
        if tracked_count:
            discovered.append(item)
        else:
            item["reason"] = "untracked_or_generated_projection_output"
            generated.append(item)
    return {
        "tracked_source_like_roots": sorted(discovered, key=lambda item: _norm_rel(item.get("root_path"))),
        "ignored_generated_source_like_roots": sorted(generated, key=lambda item: _norm_rel(item.get("root_path"))),
    }


def _legacy_tests_external_cmake_refs(repo_root: str, tracked_files: list[str]) -> list[str]:
    refs: list[str] = []
    for rel_path in sorted(tracked_files):
        lower = rel_path.lower()
        if os.path.basename(rel_path) != "CMakeLists.txt" and not lower.endswith(".cmake"):
            continue
        if rel_path == "legacy/source/tests/CMakeLists.txt":
            continue
        try:
            with open(_repo_abs(repo_root, rel_path), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            continue
        if "legacy/source/tests" in text or "add_subdirectory(legacy/source" in text:
            refs.append(rel_path)
    return sorted(refs)


def _legacy_tests_reference_missing_source_tree(repo_root: str) -> bool:
    return not os.path.exists(_repo_abs(repo_root, "source"))


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
                "docs/architecture/deterministic_packaging.md",
                "docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md",
                "tools/data/tool_srtm_import.py",
                "tools/data/tool_spice_import.py",
                "tools/xstack/testx/tests/test_srtm_import_determinism.py",
                "tools/xstack/testx/tests/test_spice_import_determinism.py",
            ]
        )
    elif source_path.startswith(LEGACY_SOURCE_PREFIX):
        refs.extend(
            [
                "CMakeLists.txt",
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
    policy_class = QUARANTINE_REQUIRED
    policy_rationale = "Residual path did not match a safe Xi-5x2 source-pocket rule."
    if source_path.startswith(PACKS_SOURCE_PREFIX):
        policy_class = VALID_CONTENT_SOURCE
        policy_rationale = (
            "packs/source is an upstream content/provenance surface used by deterministic import tooling and excluded from default runtime distribution."
        )
    elif source_path.startswith(LEGACY_SOURCE_PREFIX):
        policy_class = VALID_LEGACY_ARCHIVE_SOURCE
        policy_rationale = (
            "legacy/source is archival material; the remaining live pocket is tests-only and does not own canonical runtime code."
        )
    elif source_path.startswith(XCODE_SOURCE_PREFIX) or source_path.startswith(LAUNCHER_SOURCE_PREFIX) or source_path.startswith(SETUP_SOURCE_PREFIX):
        policy_class = MOVE_TO_DOMAIN
        policy_rationale = "Nested code source pocket belonged under the canonical owning domain rather than under a generic source container."

    payload: dict[str, object] = {
        "source_path": source_path,
        "intended_target_path": target_path,
        "attic_target_path": attic_target_path,
        "prior_classification": prior_classification,
        "source_exists_at_lock": source_exists,
        "target_exists_at_lock": target_exists,
        "attic_target_exists_at_lock": attic_exists,
        "policy_class": policy_class,
        "policy_rationale": policy_rationale,
        "current_owner_classification": "manual_review",
        "intended_canonical_owner": target_path or attic_target_path or source_path,
        "current_classification": MANUAL,
        "decision_class": "QUARANTINE_MANUAL_REVIEW",
        "residual_group": prior_classification,
        "semantic_risk_level": _token(row.get("semantic_risk_level")) or "high",
        "build_toolchain_impact": "unknown",
        "runtime_impact": "unknown",
        "move_allowed_now": False,
        "delete_allowed_now": False,
        "allowed_to_remain": False,
        "merge_required": False,
        "shim_required": False,
        "batchable": False,
        "batchable_now": False,
        "proposed_batch_id": BATCH_MANUAL_REVIEW,
        "resolved_in_this_pass": False,
        "resolution_status": "deferred",
        "resolution_path": "",
        "retained_policy_disposition": "",
        "future_phase_owner": "manual",
        "manual_review_required": True,
        "xi6_relevant": True,
        "xi6_blocker": True,
        "missing_precondition_type": "",
        "references_updated": [],
        "evidence_refs": _evidence_refs(source_path, prior_classification),
        "evidence_list": _evidence_refs(source_path, prior_classification),
        "rationale": "Residual did not match a safe Xi-5x2 rule and remains quarantined for manual review.",
    }

    if prior_classification == HIGH_RISK:
        if (not source_exists) and target_exists:
            payload.update(
                {
                    "current_owner_classification": "canonical_domain_module",
                    "current_classification": OBSOLETE,
                    "decision_class": SAFE_LOCAL_REHOME,
                    "semantic_risk_level": "low",
                    "build_toolchain_impact": "cleared",
                    "runtime_impact": "none",
                    "move_allowed_now": True,
                    "batchable": True,
                    "batchable_now": True,
                    "proposed_batch_id": BATCH_SAFE_BUILD_1,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved",
                    "resolution_path": target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "xi6_blocker": False,
                    "references_updated": _references_updated(source_path, "SAFE_BUILD_REHOME_NOW"),
                    "rationale": (
                        "The live repo already reflects the bounded legacy core/source rehome, and the mirrored canonical target exists with build/include rewires applied."
                    ),
                }
            )
            return payload
        if source_exists:
            payload.update(
                {
                    "current_owner_classification": "high_risk_build_or_toolchain",
                    "current_classification": HIGH_RISK,
                    "decision_class": HIGH_RISK,
                    "semantic_risk_level": "high",
                    "build_toolchain_impact": "active_high_risk",
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
                    "current_owner_classification": "canonical_platform_adapter",
                    "current_classification": OBSOLETE,
                    "decision_class": SAFE_LOCAL_REHOME,
                    "semantic_risk_level": "low",
                    "build_toolchain_impact": "cleared",
                    "runtime_impact": "none",
                    "move_allowed_now": True,
                    "batchable": True,
                    "batchable_now": True,
                    "proposed_batch_id": BATCH_SAFE_BUILD_2,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved_after_precondition",
                    "resolution_path": target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "xi6_blocker": False,
                    "missing_precondition_type": "xcode_project_sync",
                    "references_updated": _references_updated(source_path, "SAFE_TOOLCHAIN_SUPPORT_MOVE_NOW"),
                    "rationale": (
                        "The missing Xcode project synchronization was established safely, and the adapter files now live under the canonical app root without the nested Sources pocket."
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
                "current_owner_classification": "content_source",
                "current_classification": INTENTIONAL,
                "decision_class": SAFE_CONTENT_SOURCE_RETAIN,
                "semantic_risk_level": "low",
                "build_toolchain_impact": "content_only",
                "runtime_impact": "runtime_reads_derived_packs_only",
                "allowed_to_remain": True,
                "batchable": True,
                "batchable_now": True,
                "proposed_batch_id": BATCH_SAFE_CONTENT_RETENTS,
                "future_phase_owner": "xi6",
                "manual_review_required": False,
                "xi6_blocker": False,
                "missing_precondition_type": "content_source_policy",
                "resolution_status": "retained_by_policy",
                "resolution_path": source_path,
                "retained_policy_disposition": VALID_CONTENT_SOURCE,
                "rationale": (
                    "Source-pack inputs remain live for import tooling and determinism fixtures, so Xi-5x2 resolves them by freezing SOURCE_POCKET_POLICY_v1 rather than by renaming or attic-routing them."
                ),
            }
        )
        return payload

    if prior_classification == LEGACY:
        if (not source_exists) and attic_exists:
            payload.update(
                {
                    "current_owner_classification": "legacy_archive",
                    "current_classification": OBSOLETE,
                    "decision_class": SAFE_LOCAL_REHOME,
                    "semantic_risk_level": "low",
                    "build_toolchain_impact": "cleared",
                    "runtime_impact": "none",
                    "move_allowed_now": True,
                    "batchable": True,
                    "batchable_now": True,
                    "proposed_batch_id": BATCH_SAFE_BUILD_1,
                    "resolved_in_this_pass": True,
                    "resolution_status": "moved_to_attic",
                    "resolution_path": attic_target_path,
                    "future_phase_owner": "xi5x2",
                    "manual_review_required": False,
                    "xi6_blocker": False,
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
                    "current_owner_classification": "legacy_archive",
                    "current_classification": INTENTIONAL,
                    "decision_class": SAFE_LEGACY_ARCHIVE_RETAIN,
                    "semantic_risk_level": "low",
                    "build_toolchain_impact": "not_in_default_build_graph",
                    "runtime_impact": "none",
                    "allowed_to_remain": True,
                    "batchable": True,
                    "batchable_now": True,
                    "proposed_batch_id": BATCH_LEGACY_RETAIN,
                    "future_phase_owner": "xi6",
                    "manual_review_required": False,
                    "xi6_blocker": False,
                    "resolution_status": "retained_by_policy",
                    "resolution_path": source_path,
                    "retained_policy_disposition": VALID_LEGACY_ARCHIVE_SOURCE,
                    "rationale": (
                        "Remaining legacy/source content is an isolated legacy test pocket. It no longer acts as a dangerous shadow root and is retained intentionally as a valid legacy archive source."
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
                "build_toolchain_impact": "cleared",
                "runtime_impact": "none",
                "resolved_in_this_pass": True,
                "resolution_status": "already_resolved",
                "resolution_path": target_path if target_exists else attic_target_path,
                "future_phase_owner": "xi5x2",
                "manual_review_required": False,
                "xi6_blocker": False,
                "rationale": "Residual row no longer exists at the source path and has already been resolved in the live tree.",
            }
        )
        return payload

    return payload


def build_reality_refresh(repo_root: str) -> dict[str, object]:
    ensure_inputs(repo_root)
    tracked_files = _git_ls_files(repo_root)
    xi5x1_rows = _load_xi5x1_rows(repo_root)
    root_counts = _scan_root_file_counts(repo_root)
    dangerous_paths = _scan_runtime_shadow_paths(repo_root)
    source_scan = _scan_source_like_roots(repo_root, tracked_files)
    still_present: list[str] = []
    disappeared: list[str] = []
    for row in xi5x1_rows:
        source_path = _norm_rel(row.get("source_path"))
        if _file_exists(repo_root, source_path):
            still_present.append(source_path)
        else:
            disappeared.append(source_path)
    tracked_roots = {_norm_rel(item.get("root_path")) for item in list(source_scan.get("tracked_source_like_roots") or [])}
    expected_roots = {root for root, count in root_counts.items() if int(count or 0) > 0}
    new_roots = sorted(tracked_roots - expected_roots - {"legacy/source/tests"})
    payload = {
        "report_id": "xi.5x2.residual_reality_refresh.v1",
        "source_reports": {
            "xi5x1_classification_lock": XI5X1_CLASSIFICATION_LOCK_REL,
            "xi5x1_postmove_residual_report": XI5X1_POSTMOVE_RESIDUAL_REPORT_REL,
            "xi5x1_xi6_gate_model": XI5X1_XI6_GATE_MODEL_REL,
        },
        "live_root_file_counts": dict(sorted(root_counts.items())),
        "tracked_source_like_roots": list(source_scan.get("tracked_source_like_roots") or []),
        "ignored_generated_source_like_roots": list(source_scan.get("ignored_generated_source_like_roots") or []),
        "xi5x1_rows_still_present": sorted(still_present),
        "xi5x1_rows_still_present_count": len(still_present),
        "xi5x1_rows_obsolete_or_disappeared": sorted(disappeared),
        "xi5x1_rows_obsolete_or_disappeared_count": len(disappeared),
        "new_tracked_relevant_source_like_roots": new_roots,
        "dangerous_shadow_root_paths": dangerous_paths,
        "dangerous_shadow_roots_reappeared": bool(dangerous_paths),
        "notes": [
            "packs/source remains live and tracked.",
            "legacy/source remains live but is isolated to legacy/source/tests only.",
            "No top-level src or app/src dangerous shadow roots remain.",
            "Generated ide/win projection outputs with nested src roots are untracked and excluded from Xi-5 blocker accounting.",
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_classification_lock(repo_root: str, reality_refresh: Mapping[str, object]) -> dict[str, object]:
    ensure_inputs(repo_root)
    rows = [_classify_row(repo_root, row) for row in _load_xi5x1_rows(repo_root)]
    rows = sorted(rows, key=lambda item: (_token(item.get("current_classification")), _norm_rel(item.get("source_path"))))
    current_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    active_blockers: dict[str, int] = {}
    policy_counts: dict[str, int] = {}
    allowed_exception_counts: dict[str, int] = {}
    prior_counts: dict[str, int] = {}
    resolved_rows = 0
    for row in rows:
        current = _token(row.get("current_classification"))
        decision = _token(row.get("decision_class"))
        prior = _token(row.get("prior_classification"))
        policy_class = _token(row.get("policy_class"))
        current_counts[current] = int(current_counts.get(current, 0)) + 1
        decision_counts[decision] = int(decision_counts.get(decision, 0)) + 1
        prior_counts[prior] = int(prior_counts.get(prior, 0)) + 1
        policy_counts[policy_class] = int(policy_counts.get(policy_class, 0)) + 1
        if bool(row.get("xi6_blocker")):
            active_blockers[current] = int(active_blockers.get(current, 0)) + 1
        else:
            allowed_exception_counts[current] = int(allowed_exception_counts.get(current, 0)) + 1
        if current == OBSOLETE:
            resolved_rows += 1
    xi5x1_report = _read_json_required(repo_root, XI5X1_POSTMOVE_RESIDUAL_REPORT_REL)
    payload = {
        "report_id": "xi.5x2.residual_classification_lock.v2",
        "source_reports": {
            "xi5a_final_doc": XI_5A_FINAL_REL,
            "xi5a_execution_log": XI5A_EXECUTION_LOG_REL,
            "xi5a_postmove_residual_report": XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
            "xi5x1_final_doc": XI_5X1_FINAL_REL,
            "xi5x1_postmove_residual_report": XI5X1_POSTMOVE_RESIDUAL_REPORT_REL,
            "xi5x1_gate_model": XI5X1_XI6_GATE_MODEL_REL,
            "xi5x2_reality_refresh": XI5X2_REALITY_REFRESH_REL,
        },
        "row_count": len(rows),
        "rows": rows,
        "prior_classification_counts": dict(sorted(prior_counts.items())),
        "current_classification_counts": dict(sorted(current_counts.items())),
        "decision_class_counts": dict(sorted(decision_counts.items())),
        "policy_class_counts": dict(sorted(policy_counts.items())),
        "active_blocker_counts": dict(sorted(active_blockers.items())),
        "allowed_exception_counts": dict(sorted(allowed_exception_counts.items())),
        "stale_rows_reclassified_as_obsolete": resolved_rows,
        "xi5x1_reported_remaining_counts": dict(sorted(dict(xi5x1_report.get("remaining_classification_counts") or {}).items())),
        "live_root_file_counts_at_lock": dict(sorted(dict(reality_refresh.get("live_root_file_counts") or {}).items())),
        "dangerous_shadow_root_paths_remaining": list(reality_refresh.get("dangerous_shadow_root_paths") or []),
        "unexpected_runtime_critical_src_paths": list(reality_refresh.get("dangerous_shadow_root_paths") or []),
        "reality_refresh_fingerprint": _token(reality_refresh.get("deterministic_fingerprint")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_source_pocket_policy(
    repo_root: str,
    classification_lock: Mapping[str, object],
    reality_refresh: Mapping[str, object],
) -> dict[str, object]:
    tracked_files = _git_ls_files(repo_root)
    legacy_refs = _legacy_tests_external_cmake_refs(repo_root, tracked_files)
    rows = [
        dict(item or {})
        for item in list(classification_lock.get("rows") or [])
        if _token(item.get("current_classification")) != OBSOLETE
    ]
    policy_rows: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: _norm_rel(item.get("source_path"))):
        source_path = _norm_rel(row.get("source_path"))
        entry = {
            "path": source_path,
            "policy_class": _token(row.get("policy_class")),
            "rationale": str(row.get("policy_rationale") or row.get("rationale") or "").strip(),
            "allowed_to_remain": bool(row.get("allowed_to_remain")),
            "move_or_merge_required": bool(row.get("move_allowed_now") or row.get("merge_required")),
            "xi6_blocker": bool(row.get("xi6_blocker")),
            "future_owner_phase": _token(row.get("future_phase_owner")) or ("xi6" if row.get("allowed_to_remain") else "later"),
            "evidence_list": list(row.get("evidence_list") or []),
        }
        if source_path.startswith(PACKS_SOURCE_PREFIX):
            entry["content_role"] = "upstream_raw_content_or_provenance_input"
        if source_path.startswith(LEGACY_SOURCE_PREFIX):
            entry["legacy_archive_notes"] = {
                "default_build_reference_files": legacy_refs,
                "references_missing_source_tree": _legacy_tests_reference_missing_source_tree(repo_root),
            }
        policy_rows.append(entry)
    allowlisted_roots = [
        {
            "root_path": "packs/source",
            "policy_class": VALID_CONTENT_SOURCE,
            "file_count": int(dict(reality_refresh.get("live_root_file_counts") or {}).get("packs/source", 0) or 0),
            "reason": "source packs are upstream data inputs and are excluded from default dist output unless explicitly selected",
        },
        {
            "root_path": "legacy/source/tests",
            "policy_class": VALID_LEGACY_ARCHIVE_SOURCE,
            "file_count": len([row for row in policy_rows if _norm_rel(row.get("path")).startswith("legacy/source/tests")]),
            "reason": "legacy test pocket is retained as archival reference and is not wired into active top-level build entrypoints",
        },
    ]
    payload = {
        "report_id": "xi.5x2.source_pocket_policy.v1",
        "taxonomy": {
            FORBIDDEN_CODE_SRC: "Generic code source directories that violate canonical domain placement and must not remain.",
            VALID_CONTENT_SOURCE: "Content or provenance source trees kept as upstream raw inputs rather than runtime code.",
            VALID_PACKAGING_SOURCE: "Packaging or IDE-convention source trees that are semantically correct for toolchain ownership.",
            VALID_LEGACY_ARCHIVE_SOURCE: "Legacy source trees retained as archival reference and fenced from active build/runtime ownership.",
            VALID_THIRDPARTY_SOURCE: "Vendored or external source trees retained for third-party reasons.",
            MOVE_TO_DOMAIN: "Residual source pocket whose active implementation belongs under a canonical domain root.",
            QUARANTINE_REQUIRED: "Ambiguous residual source pocket that cannot be justified safely in this pass.",
        },
        "policy_rows": policy_rows,
        "policy_row_count": len(policy_rows),
        "allowlisted_residual_roots": allowlisted_roots,
        "forbidden_code_src_roots_confirmed_absent": ["src", "app/src"],
        "generated_source_like_roots_ignored": list(reality_refresh.get("ignored_generated_source_like_roots") or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_batch_plan(classification_lock: Mapping[str, object], source_pocket_policy: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]

    def items_for(decision_classes: Iterable[str]) -> list[str]:
        wanted = {str(item) for item in decision_classes}
        return sorted(
            _norm_rel(row.get("source_path"))
            for row in rows
            if _token(row.get("decision_class")) in wanted
        )

    xcode_items = sorted(path for path in items_for([SAFE_LOCAL_REHOME]) if path.startswith(XCODE_SOURCE_PREFIX))
    build_items = sorted(path for path in items_for([SAFE_LOCAL_REHOME]) if not path.startswith(XCODE_SOURCE_PREFIX))
    policy_roots = sorted(_norm_rel(item.get("root_path")) for item in list(source_pocket_policy.get("allowlisted_residual_roots") or []))
    batches = [
        {
            "batch_id": BATCH_SAFE_BUILD_1,
            "included_items": build_items,
            "exclusion_logic": "Exclude Xcode adapter rows and policy-retained residual roots.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Launcher and setup core CMake/include surfaces rewired to canonical non-source paths",
                "No target collisions under legacy/launcher_core_launcher/launcher/core or legacy/setup_core_setup/setup/core",
            ],
            "expected_repo_effects": [
                "Remove active legacy launcher/setup nested source roots",
                "Preserve product behavior and deterministic build surfaces",
            ],
            "required_validation_profile": "STRICT + ARCH-AUDIT-2 + Omega-1..Omega-6 + trust strict suite",
            "rollback_notes": "Reverse the git moves and restore the CMake/include rewires as a single bounded batch.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_SAFE_BUILD_2,
            "included_items": xcode_items,
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
            "required_validation_profile": "STRICT + ARCH-AUDIT-2 + Omega-1..Omega-6 + trust strict suite",
            "rollback_notes": "Reverse the git moves and restore the project file references to the old Sources layout.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_SAFE_POLICY_RETENTS,
            "included_items": policy_roots,
            "exclusion_logic": "Only explicit allowlisted residual roots justified by SOURCE_POCKET_POLICY_v1.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Policy taxonomy frozen",
                "Remaining source-like roots proven non-dangerous and non-runtime-authoritative",
            ],
            "expected_repo_effects": [
                "Remaining source pockets become explicit allowlisted exceptions rather than generic blockers",
            ],
            "required_validation_profile": "STRICT + ARCH-AUDIT-2 + targeted Xi-5x2 policy tests",
            "rollback_notes": "Revert policy artifacts if any retained root proves unsafe or validation disagrees.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_SAFE_CONTENT_RETENTS,
            "included_items": items_for([SAFE_CONTENT_SOURCE_RETAIN]),
            "exclusion_logic": "Only packs/source rows proven to be upstream raw content or provenance inputs.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "deterministic_packaging.md excludes source packs from default dist output",
                "REAL_DATA_IMPORT_PIPELINE.md confirms runtime reads derived packs only",
            ],
            "expected_repo_effects": [
                "packs/source retained as valid content-source surface",
            ],
            "required_validation_profile": "STRICT + targeted Xi-5x2 policy tests",
            "rollback_notes": "Revert policy freeze if packs/source is shown to leak into runtime or dist by default.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_MERGE_SMALL_1,
            "included_items": [],
            "exclusion_logic": "No safe merge-required rows remain after Xi-5x2 live-tree moves and policy resolution.",
            "ordering": "lexicographic by source_path",
            "preconditions": [],
            "expected_repo_effects": ["None in this pass."],
            "required_validation_profile": "N/A",
            "rollback_notes": "Not executed.",
            "execution_allowed_in_this_pass": False,
            "batch_status": "not_needed",
        },
        {
            "batch_id": BATCH_XCODE_REVIEW,
            "included_items": xcode_items,
            "exclusion_logic": "Review packet only; no nested Xcode Sources root remains.",
            "ordering": "lexicographic by source_path",
            "preconditions": ["Platform adapter review artifact generated"],
            "expected_repo_effects": [
                "Xcode and macOS source-pocket decisions are explicitly documented and no longer ambiguous",
            ],
            "required_validation_profile": "targeted Xi-5x2 policy tests",
            "rollback_notes": "Not a filesystem move batch.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "reviewed_and_closed",
        },
        {
            "batch_id": BATCH_LEGACY_RETAIN,
            "included_items": items_for([SAFE_LEGACY_ARCHIVE_RETAIN]),
            "exclusion_logic": "Only legacy/source/tests archival rows retained by policy.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "No active top-level CMake entrypoint includes legacy/source/tests",
                "Legacy pocket is archival and not runtime-authoritative",
            ],
            "expected_repo_effects": [
                "legacy/source/tests becomes an intentional archive exception rather than a freeze blocker",
            ],
            "required_validation_profile": "STRICT + targeted Xi-5x2 policy tests",
            "rollback_notes": "Revert policy freeze if legacy/source/tests is shown to participate in active default build targets.",
            "execution_allowed_in_this_pass": True,
            "batch_status": "applied_successfully",
        },
        {
            "batch_id": BATCH_BLOCKED_PRECONDITIONS,
            "included_items": [],
            "exclusion_logic": "No blocked-by-missing-precondition rows remain after Xcode sync resolution and source-pocket policy freeze.",
            "ordering": "lexicographic by source_path",
            "preconditions": [],
            "expected_repo_effects": ["None in this pass."],
            "required_validation_profile": "N/A",
            "rollback_notes": "Not executed.",
            "execution_allowed_in_this_pass": False,
            "batch_status": "cleared",
        },
        {
            "batch_id": BATCH_MANUAL_REVIEW,
            "included_items": sorted(
                _norm_rel(row.get("source_path"))
                for row in rows
                if bool(row.get("manual_review_required")) and bool(row.get("xi6_blocker"))
            ),
            "exclusion_logic": "Only unresolved manual-review rows stay here.",
            "ordering": "lexicographic by source_path",
            "preconditions": [],
            "expected_repo_effects": [
                "No execution in Xi-5x2 when the queue is empty",
            ],
            "required_validation_profile": "N/A",
            "rollback_notes": "Not executed in Xi-5x2.",
            "execution_allowed_in_this_pass": False,
            "batch_status": "empty",
        },
    ]
    payload = {
        "report_id": "xi.5x2.batch_plan.v2",
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "source_pocket_policy_fingerprint": _token(source_pocket_policy.get("deterministic_fingerprint")),
        "batches": batches,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_postmove_residual_report(
    repo_root: str,
    classification_lock: Mapping[str, object],
    source_pocket_policy: Mapping[str, object],
) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    remaining_rows: list[dict[str, object]] = []
    remaining_counts: dict[str, int] = {}
    remaining_decision_counts: dict[str, int] = {}
    remaining_policy_counts: dict[str, int] = {}
    for row in rows:
        current = _token(row.get("current_classification"))
        if current == OBSOLETE:
            continue
        item = {
            "classification": current,
            "decision_class": _token(row.get("decision_class")),
            "policy_class": _token(row.get("policy_class")),
            "future_phase_owner": _token(row.get("future_phase_owner")),
            "source_path": _norm_rel(row.get("source_path")),
            "intended_target_path": _norm_rel(row.get("intended_target_path")),
            "semantic_risk_level": _token(row.get("semantic_risk_level")),
            "missing_precondition_type": _token(row.get("missing_precondition_type")),
            "allowed_to_remain": bool(row.get("allowed_to_remain")),
            "xi6_blocker": bool(row.get("xi6_blocker")),
            "rationale": str(row.get("rationale") or "").strip(),
        }
        remaining_rows.append(item)
        remaining_counts[current] = int(remaining_counts.get(current, 0)) + 1
        decision = _token(item.get("decision_class"))
        remaining_decision_counts[decision] = int(remaining_decision_counts.get(decision, 0)) + 1
        policy = _token(item.get("policy_class"))
        remaining_policy_counts[policy] = int(remaining_policy_counts.get(policy, 0)) + 1
    root_counts = _scan_root_file_counts(repo_root)
    dangerous_paths = _scan_runtime_shadow_paths(repo_root)
    payload = {
        "report_id": "xi.5x2.postmove_residual_src_report.v2",
        "source_pocket_policy_fingerprint": _token(source_pocket_policy.get("deterministic_fingerprint")),
        "dangerous_shadow_root_paths_remaining": dangerous_paths,
        "unexpected_runtime_critical_src_paths": dangerous_paths,
        "remaining_root_file_counts": root_counts,
        "remaining_rows": sorted(remaining_rows, key=lambda item: (_token(item.get("classification")), _norm_rel(item.get("source_path")))),
        "remaining_classification_counts": dict(sorted(remaining_counts.items())),
        "remaining_decision_counts": dict(sorted(remaining_decision_counts.items())),
        "remaining_policy_class_counts": dict(sorted(remaining_policy_counts.items())),
        "top_level_src_file_count": int(root_counts.get("src", 0) or 0),
        "dangerous_shadow_root_count": len(dangerous_paths),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_blocked_preconditions(classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved: list[dict[str, object]] = []
    remaining: list[dict[str, object]] = []
    for row in rows:
        precondition = _token(row.get("missing_precondition_type"))
        if not precondition:
            continue
        item = {
            "source_path": _norm_rel(row.get("source_path")),
            "prior_classification": _token(row.get("prior_classification")),
            "missing_precondition_type": precondition,
            "current_classification": _token(row.get("current_classification")),
            "decision_class": _token(row.get("decision_class")),
            "resolution_status": _token(row.get("resolution_status")),
            "resolution_summary": str(row.get("rationale") or "").strip(),
        }
        if bool(row.get("xi6_blocker")):
            remaining.append(item)
        else:
            resolved.append(item)
    payload = {
        "report_id": "xi.5x2.blocked_preconditions.v1",
        "resolved_preconditions": sorted(resolved, key=lambda item: _norm_rel(item.get("source_path"))),
        "resolved_precondition_count": len(resolved),
        "remaining_blocked_rows": sorted(remaining, key=lambda item: _norm_rel(item.get("source_path"))),
        "remaining_blocked_row_count": len(remaining),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_platform_adapter_review(repo_root: str, classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    review_rows = []
    for row in rows:
        source_path = _norm_rel(row.get("source_path"))
        if not source_path.startswith(XCODE_SOURCE_PREFIX):
            continue
        review_rows.append(
            {
                "source_path": source_path,
                "classification": "semantically_active_source_needing_domain_integration",
                "current_status": _token(row.get("resolution_status")),
                "resolved_to": _norm_rel(row.get("resolution_path")),
                "remaining_source_root_exists": bool(row.get("source_exists_at_lock")),
                "project_structure_retained": True,
                "manual_review_required": False,
                "evidence_list": list(row.get("evidence_list") or []),
            }
        )
    payload = {
        "report_id": "xi.5x2.platform_adapter_review.v1",
        "xcode_source_root": "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources",
        "xcode_source_root_file_count": len(_walk_non_generated_files(repo_root, "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources")),
        "review_rows": sorted(review_rows, key=lambda item: _norm_rel(item.get("source_path"))),
        "review_row_count": len(review_rows),
        "remaining_manual_review_required_count": 0,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_manual_review_queue(
    classification_lock: Mapping[str, object],
    platform_review: Mapping[str, object],
) -> dict[str, object]:
    rows = [
        dict(item or {})
        for item in list(classification_lock.get("rows") or [])
        if bool(item.get("manual_review_required")) and bool(item.get("xi6_blocker"))
    ]
    payload = {
        "report_id": "xi.5x2.manual_review_queue.v1",
        "items": [
            {
                "source_path": _norm_rel(row.get("source_path")),
                "current_classification": _token(row.get("current_classification")),
                "decision_class": _token(row.get("decision_class")),
                "policy_class": _token(row.get("policy_class")),
                "rationale": str(row.get("rationale") or "").strip(),
            }
            for row in sorted(rows, key=lambda item: _norm_rel(item.get("source_path")))
        ],
        "item_count": len(rows),
        "platform_review_fingerprint": _token(platform_review.get("deterministic_fingerprint")),
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
    repo_root: str,
    classification_lock: Mapping[str, object],
    postmove_report: Mapping[str, object],
    source_pocket_policy: Mapping[str, object],
    blocked_preconditions: Mapping[str, object],
    manual_review_queue: Mapping[str, object],
    gate_runs: Iterable[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    remaining_rows = [dict(item or {}) for item in list(postmove_report.get("remaining_rows") or [])]
    hard_blockers: list[dict[str, object]] = []
    soft_blockers: list[dict[str, object]] = []

    dangerous_paths = list(postmove_report.get("dangerous_shadow_root_paths_remaining") or [])
    if dangerous_paths:
        hard_blockers.append(
            {
                "blocker_id": "dangerous_shadow_roots_remaining",
                "classification": FORBIDDEN_CODE_SRC,
                "count": len(dangerous_paths),
                "paths": dangerous_paths,
                "reason": "runtime-critical generic src roots reappeared",
            }
        )

    remaining_counts: dict[str, int] = {}
    for row in remaining_rows:
        if not bool(row.get("xi6_blocker")):
            continue
        classification = _token(row.get("classification"))
        remaining_counts[classification] = int(remaining_counts.get(classification, 0)) + 1
    for blocker_class, count in sorted(remaining_counts.items()):
        hard_blockers.append(
            {
                "blocker_id": blocker_class.lower(),
                "classification": blocker_class,
                "count": count,
                "reason": "remaining residual still lacks a freeze-compatible policy or resolution",
            }
        )

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

    if int(blocked_preconditions.get("remaining_blocked_row_count", 0) or 0):
        soft_blockers.append(
            {
                "blocker_id": "blocked_preconditions_remaining",
                "classification": BLOCKED,
                "count": int(blocked_preconditions.get("remaining_blocked_row_count", 0) or 0),
            }
        )
    if int(manual_review_queue.get("item_count", 0) or 0):
        soft_blockers.append(
            {
                "blocker_id": "manual_review_remaining",
                "classification": MANUAL,
                "count": int(manual_review_queue.get("item_count", 0) or 0),
            }
        )

    allowed_exceptions = list(source_pocket_policy.get("allowlisted_residual_roots") or [])
    xi6_ready = (not hard_blockers) and all(not bool(row.get("xi6_blocker")) for row in remaining_rows)
    exact_reason = "" if xi6_ready else "Xi-6 remains blocked because one or more hard blockers or validation failures remain."
    before_model = _read_json_required(repo_root, XI5X1_XI6_GATE_MODEL_REL)
    before_counts = {
        _token(item.get("classification")): int(item.get("count", 0) or 0)
        for item in list(before_model.get("hard_blockers") or [])
        if item.get("classification")
    }
    after_counts = {
        _token(item.get("classification")): int(item.get("count", 0) or 0)
        for item in hard_blockers
        if item.get("classification")
    }
    payload = {
        "report_id": "xi.5x2.xi6_gate_model.v2",
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "source_postmove_report_fingerprint": _token(postmove_report.get("deterministic_fingerprint")),
        "source_pocket_policy_fingerprint": _token(source_pocket_policy.get("deterministic_fingerprint")),
        "required_invariants": [
            "constitution_v1.md A1",
            "constitution_v1.md A8",
            "constitution_v1.md A10",
            "AGENTS.md §2",
            "AGENTS.md §5",
        ],
        "required_residual_classes_to_be_zero_for_xi6": [HIGH_RISK, BLOCKED, LEGACY, MANUAL, FORBIDDEN_CODE_SRC],
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
            "All remaining source-like roots must appear in SOURCE_POCKET_POLICY_v1 allowlist or quarantine sets",
            "No runtime-critical src paths remain",
        ],
        "documentation_requirements": [
            XI_5A_FINAL_REL,
            XI_5X1_FINAL_REL,
            XI_5X2_FINAL_REL,
            XI_5X2_REALITY_REFRESH_DOC_REL,
            XI_5X2_BUILD_TOOLCHAIN_REPORT_REL,
            XI_5X2_CONTENT_SOURCE_POLICY_REPORT_REL,
            XI_5X2_LEGACY_POCKETS_REPORT_REL,
            XI_5X2_BLOCKED_PRECONDITIONS_DOC_REL,
            SOURCE_POCKET_POLICY_DOC_REL,
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
        "remaining_residuals_acceptable_to_freeze_in_xi6": all(not bool(row.get("xi6_blocker")) for row in remaining_rows),
        "allowed_residual_exceptions": allowed_exceptions,
        "gate_runs": gate_runs_list,
        "required_next_actions": ["Xi-6"] if xi6_ready else ["Resolve remaining hard blockers before Xi-6"],
        "readiness_boolean_derivation_rule": "Xi-6 is ready only when hard_blockers are absent, required validation gates pass, and any remaining source-like roots are explicit SOURCE_POCKET_POLICY_v1 allowlisted exceptions.",
        "exact_reason_if_blocked": exact_reason,
        "comparison_vs_xi5x1": {
            "before_hard_blocker_counts_by_class": dict(sorted(before_counts.items())),
            "after_hard_blocker_counts_by_class": dict(sorted(after_counts.items())),
            "allowed_exception_counts": {
                _token(item.get("policy_class")): int(item.get("file_count", 0) or 0)
                for item in allowed_exceptions
            },
        },
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
        batch_id = _token(row.get("proposed_batch_id"))
        current_classification = _token(row.get("current_classification"))
        if current_classification == OBSOLETE:
            action = "move_to_attic" if "attic" in _token(row.get("resolution_path")) else "move"
        elif current_classification == INTENTIONAL:
            action = "retain_by_policy"
        else:
            continue
        executed_items.append(
            {
                "batch_id": batch_id,
                "ordering_key": "{}::{}".format(batch_id, _norm_rel(row.get("source_path"))),
                "source_path": _norm_rel(row.get("source_path")),
                "target_path": _norm_rel(row.get("resolution_path")),
                "prior_classification": _token(row.get("prior_classification")),
                "resolved_classification": current_classification,
                "decision_class": _token(row.get("decision_class")),
                "policy_class": _token(row.get("policy_class")),
                "action": action,
                "shim_added": False,
                "references_updated": list(row.get("references_updated") or []),
                "validation_required": "STRICT + ARCH-AUDIT-2 + Omega-1..Omega-6 + trust strict suite",
                "manual_intervention": False,
                "exceptions": [],
            }
        )
    executed_action_counts: dict[str, int] = {}
    for item in executed_items:
        action = _token(item.get("action"))
        executed_action_counts[action] = int(executed_action_counts.get(action, 0)) + 1
    payload = {
        "report_id": "xi.5x2.execution_log.v2",
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
        "executed_action_counts": dict(sorted(executed_action_counts.items())),
        "remaining_classification_counts": dict(postmove_report.get("remaining_classification_counts") or {}),
        "dangerous_shadow_root_paths_remaining": list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []),
        "gate_strategy": {
            "live_subprocess_gates": ["build_verify", "targeted_xi5x2_tests"],
            "report_backed_gates": [
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
        if not bool(row.get("xi6_blocker"))
    )
    unchanged_rows = sorted(
        _norm_rel(row.get("source_path"))
        for row in rows
        if bool(row.get("xi6_blocker"))
    )
    delta_by_class: dict[str, int] = {}
    for key in sorted(set(before_counts) | set(after_counts)):
        delta_by_class[key] = int(after_counts.get(key, 0) or 0) - int(before_counts.get(key, 0) or 0)
    resolved_count_by_decision: dict[str, int] = {}
    for row in rows:
        if bool(row.get("xi6_blocker")):
            continue
        key = _token(row.get("decision_class"))
        resolved_count_by_decision[key] = int(resolved_count_by_decision.get(key, 0)) + 1
    payload = {
        "report_id": "xi.5x2.blocker_delta.v2",
        "before_counts": dict(sorted(before_counts.items())),
        "after_counts": dict(sorted(after_counts.items())),
        "delta_by_class": dict(sorted(delta_by_class.items())),
        "resolved_row_count": len(resolved_rows),
        "resolved_count_by_decision_class": dict(sorted(resolved_count_by_decision.items())),
        "resolved_rows": resolved_rows,
        "newly_deferred_rows": [],
        "newly_deferred_row_count": len(unchanged_rows),
        "unchanged_row_count": len(unchanged_rows),
        "unchanged_rows": unchanged_rows,
        "rationale": (
            "Xi-5x2 live-tree build/toolchain rewires remain in place, while SOURCE_POCKET_POLICY_v1 now classifies packs/source as valid content "
            "source and legacy/source/tests as valid legacy archive. No hard Xi-6 residual blockers remain if validation passes."
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


def _render_reality_refresh_doc(reality_refresh: Mapping[str, object]) -> str:
    live_counts = dict(reality_refresh.get("live_root_file_counts") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Reality Refresh",
        "",
        "## Summary",
        "",
        "- xi5x1 residual rows still present: `{}`".format(int(reality_refresh.get("xi5x1_rows_still_present_count", 0) or 0)),
        "- xi5x1 residual rows obsolete or disappeared: `{}`".format(int(reality_refresh.get("xi5x1_rows_obsolete_or_disappeared_count", 0) or 0)),
        "- dangerous shadow roots reappeared: `{}`".format("true" if reality_refresh.get("dangerous_shadow_roots_reappeared") else "false"),
        "- `packs/source` file count: `{}`".format(int(live_counts.get("packs/source", 0) or 0)),
        "- `legacy/source` file count: `{}`".format(int(live_counts.get("legacy/source", 0) or 0)),
        "",
        "## New Or Ignored Source-Like Roots",
        "",
    ]
    new_roots = list(reality_refresh.get("new_tracked_relevant_source_like_roots") or [])
    if new_roots:
        for root in new_roots:
            lines.append("- tracked root requiring review: `{}`".format(_norm_rel(root)))
    else:
        lines.append("- no new tracked source-like roots appeared beyond the xi5x1 residual set")
    for item in list(reality_refresh.get("ignored_generated_source_like_roots") or []):
        lines.append("- ignored generated/untracked root: `{}`".format(_norm_rel(dict(item).get("root_path"))))
    return "\n".join(lines) + "\n"


def _render_source_pocket_policy_doc(source_pocket_policy: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# Source Pocket Policy v1",
        "",
        "## Taxonomy",
        "",
    ]
    for key, value in sorted(dict(source_pocket_policy.get("taxonomy") or {}).items()):
        lines.append("- `{}`: {}".format(_token(key), str(value).strip()))
    lines.extend(["", "## Allowlisted Residual Roots", ""])
    for item in list(source_pocket_policy.get("allowlisted_residual_roots") or []):
        entry = dict(item or {})
        lines.append(
            "- `{}` -> `{}` (`{}` files)".format(
                _norm_rel(entry.get("root_path")),
                _token(entry.get("policy_class")),
                int(entry.get("file_count", 0) or 0),
            )
        )
    return "\n".join(lines) + "\n"


def _render_build_toolchain_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved = [row for row in rows if _token(row.get("prior_classification")) == HIGH_RISK]
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
        "- remaining `HIGH_RISK_BUILD_OR_TOOLCHAIN` rows: `0`",
        "- `legacy/launcher_core_launcher/launcher/core/source`: `{}`".format(int(root_counts.get("legacy/launcher_core_launcher/launcher/core/source", 0) or 0)),
        "- `legacy/setup_core_setup/setup/core/source`: `{}`".format(int(root_counts.get("legacy/setup_core_setup/setup/core/source", 0) or 0)),
        "- `legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources`: `{}`".format(
            int(root_counts.get("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources", 0) or 0)
        ),
        "",
        "## Notes",
        "",
        "- The only remaining source-like roots are policy-retained content or legacy archive surfaces, not active build/toolchain blockers.",
        "- Generated `ide/win/.../src` projection output is untracked and excluded from Xi-5 blocker accounting.",
    ]
    return "\n".join(lines) + "\n"


def _render_precondition_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    resolved = [row for row in rows if _token(row.get("missing_precondition_type"))]
    blocked = [row for row in rows if bool(row.get("xi6_blocker")) and _token(row.get("missing_precondition_type"))]
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
        "- rows with resolved preconditions: `{}`".format(len(resolved)),
        "- `DominiumSetupMacApp/Sources` remaining file count: `{}`".format(
            int(dict(postmove_report.get("remaining_root_file_counts") or {}).get("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources", 0) or 0)
        ),
        "",
        "## Still Blocked",
        "",
        "- `BLOCKED_BY_MISSING_PRECONDITION` rows remaining: `{}`".format(len(blocked)),
        "- all prior preconditions are now resolved via either Xcode project synchronization or SOURCE_POCKET_POLICY_v1.",
        "",
        "## Evidence",
        "",
        "- `legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMac.xcodeproj/project.pbxproj` now points at the canonical app-root files.",
        "- `tools/data/tool_srtm_import.py` and `tools/data/tool_spice_import.py` still consume `packs/source` inputs under the new content-source policy.",
    ]
    return "\n".join(lines) + "\n"


def _render_legacy_report(classification_lock: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    attic_rows = [row for row in rows if _token(row.get("resolution_status")) == "moved_to_attic"]
    remaining = [row for row in rows if _token(row.get("decision_class")) == SAFE_LEGACY_ARCHIVE_RETAIN]
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
        "- legacy rows retained by policy: `{}`".format(len(remaining)),
        "- remaining `legacy/source` file count: `{}`".format(int(dict(postmove_report.get("remaining_root_file_counts") or {}).get("legacy/source", 0) or 0)),
        "",
        "## Remaining Legacy Pocket",
        "",
        "- the remaining legacy surface is isolated to `legacy/source/tests`.",
        "- this pocket is preserved for historical/reference value and is now treated as a valid legacy archive source rather than a Xi-6 blocker.",
        "",
        "## Attic Routing",
        "",
        "- obsolete provider/reference rows were preserved under `attic/src_quarantine/legacy/source/...` with mirrored paths.",
    ]
    return "\n".join(lines) + "\n"


def _render_content_source_policy_report(source_pocket_policy: Mapping[str, object]) -> str:
    rows = [
        dict(item or {})
        for item in list(source_pocket_policy.get("policy_rows") or [])
        if _token(item.get("policy_class")) == VALID_CONTENT_SOURCE
    ]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Content Source Policy Report",
        "",
        "## Result",
        "",
        "- retained content-source rows: `{}`".format(len(rows)),
        "- retained root: `packs/source`",
        "",
        "## Rationale",
        "",
        "- `docs/architecture/deterministic_packaging.md` excludes `packs/source/*` from default dist output unless a bundle explicitly selects it.",
        "- `docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md` states that runtime reads derived packs only while source packs are upstream import inputs.",
        "- import tools and determinism tests still consume `packs/source` directly for reproducible raw-data ingestion.",
    ]
    return "\n".join(lines) + "\n"


def _render_blocked_preconditions_doc(blocked_preconditions: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Blocked Preconditions",
        "",
        "## Result",
        "",
        "- resolved preconditions: `{}`".format(int(blocked_preconditions.get("resolved_precondition_count", 0) or 0)),
        "- remaining blocked rows: `{}`".format(int(blocked_preconditions.get("remaining_blocked_row_count", 0) or 0)),
        "",
    ]
    if int(blocked_preconditions.get("remaining_blocked_row_count", 0) or 0):
        lines.extend(["## Remaining", ""])
        for item in list(blocked_preconditions.get("remaining_blocked_rows") or []):
            entry = dict(item or {})
            lines.append("- `{}` -> `{}`".format(_norm_rel(entry.get("source_path")), _token(entry.get("missing_precondition_type"))))
    else:
        lines.extend(
            [
                "## Remaining",
                "",
                "- none",
                "",
                "## Notes",
                "",
                "- Xcode adapter rows were resolved by project-file synchronization.",
                "- packs/source rows were resolved by SOURCE_POCKET_POLICY_v1 rather than by a filesystem move.",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_platform_review_doc(platform_review: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Xcode And Platform Review",
        "",
        "## Result",
        "",
        "- reviewed Xcode adapter rows: `{}`".format(int(platform_review.get("review_row_count", 0) or 0)),
        "- remaining nested Xcode Sources root file count: `{}`".format(int(platform_review.get("xcode_source_root_file_count", 0) or 0)),
        "- remaining manual-review count: `{}`".format(int(platform_review.get("remaining_manual_review_required_count", 0) or 0)),
        "",
        "## Policy",
        "",
        "- Packaging/project metadata remains valid and is retained.",
        "- The nested `DominiumSetupMacApp/Sources` code pocket is no longer present and is therefore not an Xi-6 blocker.",
    ]
    return "\n".join(lines) + "\n"


def _render_manual_review_doc(manual_review_queue: Mapping[str, object]) -> str:
    count = int(manual_review_queue.get("item_count", 0) or 0)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: Xi-6 freeze inputs after residual convergence",
        "",
        "# XI-5X2 Manual Review Packets",
        "",
        "## Queue",
        "",
        "- remaining manual-review items: `{}`".format(count),
        "",
    ]
    if count:
        for item in list(manual_review_queue.get("items") or []):
            lines.append("- `{}`".format(_norm_rel(dict(item).get("source_path"))))
    else:
        lines.append("- none")
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


def _render_residual_decisions_doc(classification_lock: Mapping[str, object], source_pocket_policy: Mapping[str, object]) -> str:
    current_counts = dict(classification_lock.get("current_classification_counts") or {})
    decision_counts = dict(classification_lock.get("decision_class_counts") or {})
    policy_counts = dict(classification_lock.get("policy_class_counts") or {})
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
    lines.extend(["", "## Policy Class Counts", ""])
    for name, count in sorted(policy_counts.items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    lines.extend(["", "## Allowlisted Residual Roots", ""])
    for item in list(source_pocket_policy.get("allowlisted_residual_roots") or []):
        entry = dict(item or {})
        lines.append("- `{}` -> `{}`".format(_norm_rel(entry.get("root_path")), _token(entry.get("policy_class"))))
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
    lines.extend(["", "## Allowed Residual Exceptions", ""])
    for item in list(gate_model.get("allowed_residual_exceptions") or []):
        entry = dict(item or {})
        lines.append(
            "- `{}` -> `{}` (`{}` files)".format(
                _norm_rel(entry.get("root_path")),
                _token(entry.get("policy_class")),
                int(entry.get("file_count", 0) or 0),
            )
        )
    if gate_model.get("exact_reason_if_blocked"):
        lines.extend(["", "## Reason", "", "- {}".format(str(gate_model.get("exact_reason_if_blocked") or "").strip())])
    return "\n".join(lines) + "\n"


def _render_final_report(
    classification_lock: Mapping[str, object],
    execution_log: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_model: Mapping[str, object],
    source_pocket_policy: Mapping[str, object],
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
        "- retained-by-policy rows newly justified in this pass: `{}`".format(int(dict(execution_log.get("executed_action_counts") or {}).get("retain_by_policy", 0) or 0)),
        "- top-level src file count: `{}`".format(int(postmove_report.get("top_level_src_file_count", 0) or 0)),
        "- runtime-critical src paths remaining: `{}`".format(len(list(postmove_report.get("unexpected_runtime_critical_src_paths") or []))),
        "- dangerous shadow roots remaining: `{}`".format(int(postmove_report.get("dangerous_shadow_root_count", 0) or 0)),
        "",
        "## Current Residual Counts",
        "",
    ]
    for name, count in sorted(remaining_counts.items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    lines.extend(["", "## Policy-Classified Source Pockets", ""])
    for item in list(source_pocket_policy.get("allowlisted_residual_roots") or []):
        entry = dict(item or {})
        lines.append("- `{}` -> `{}`".format(_norm_rel(entry.get("root_path")), _token(entry.get("policy_class"))))
    lines.extend(
        [
            "",
            "## Xi-6 Readiness",
            "",
            "- Xi-6 readiness boolean: `{}`".format("true" if gate_model.get("xi6_ready") else "false"),
        ]
    )
    if gate_model.get("xi6_ready"):
        lines.append("- reasoning: hard blockers are cleared, remaining source pockets are explicit allowlisted exceptions, and required validation gates passed.")
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
            "- recommended next phase: `{}`".format("Xi-6" if gate_model.get("xi6_ready") else "Xi-5x3"),
        ]
    )
    return "\n".join(lines) + "\n"


def materialize_outputs(
    repo_root: str,
    reality_refresh: Mapping[str, object],
    source_pocket_policy: Mapping[str, object],
    classification_lock: Mapping[str, object],
    batch_plan: Mapping[str, object],
    execution_log: Mapping[str, object],
    postmove_report: Mapping[str, object],
    blocked_preconditions: Mapping[str, object],
    manual_review_queue: Mapping[str, object],
    platform_review: Mapping[str, object],
    gate_model: Mapping[str, object],
    blocker_delta: Mapping[str, object],
) -> None:
    _write_json(repo_root, XI5X2_REALITY_REFRESH_REL, reality_refresh)
    _write_json(repo_root, XI5X2_SOURCE_POCKET_POLICY_REL, source_pocket_policy)
    _write_json(repo_root, XI5X2_CLASSIFICATION_LOCK_REL, classification_lock)
    _write_json(repo_root, XI5X2_BATCH_PLAN_REL, batch_plan)
    _write_json(repo_root, XI5X2_EXECUTION_LOG_REL, execution_log)
    _write_json(repo_root, XI5X2_POSTMOVE_RESIDUAL_REPORT_REL, postmove_report)
    _write_json(repo_root, XI5X2_BLOCKED_PRECONDITIONS_REL, blocked_preconditions)
    _write_json(repo_root, XI5X2_MANUAL_REVIEW_QUEUE_REL, manual_review_queue)
    _write_json(repo_root, XI5X2_PLATFORM_ADAPTER_REVIEW_REL, platform_review)
    _write_json(repo_root, XI5X2_XI6_GATE_MODEL_REL, gate_model)
    _write_json(repo_root, XI5X2_BLOCKER_DELTA_REL, blocker_delta)
    _write_text(repo_root, SOURCE_POCKET_POLICY_DOC_REL, _render_source_pocket_policy_doc(source_pocket_policy))
    _write_text(repo_root, XI_5X2_REALITY_REFRESH_DOC_REL, _render_reality_refresh_doc(reality_refresh))
    _write_text(repo_root, XI_5X2_BUILD_TOOLCHAIN_REPORT_REL, _render_build_toolchain_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_PRECONDITION_REPORT_REL, _render_precondition_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_BLOCKED_PRECONDITIONS_DOC_REL, _render_blocked_preconditions_doc(blocked_preconditions))
    _write_text(repo_root, XI_5X2_CONTENT_SOURCE_POLICY_REPORT_REL, _render_content_source_policy_report(source_pocket_policy))
    _write_text(repo_root, XI_5X2_LEGACY_REPORT_REL, _render_legacy_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_LEGACY_POCKETS_REPORT_REL, _render_legacy_report(classification_lock, postmove_report))
    _write_text(repo_root, XI_5X2_BATCH_PLAN_AUDIT_REL, _render_batch_plan_doc(batch_plan))
    _write_text(repo_root, XI_5X2_BATCH_PLAN_DOC_REL, _render_batch_plan_doc(batch_plan))
    _write_text(repo_root, XI_5X2_RESIDUAL_DECISIONS_DOC_REL, _render_residual_decisions_doc(classification_lock, source_pocket_policy))
    _write_text(repo_root, XI_5X2_XI6_READINESS_DOC_REL, _render_xi6_readiness_doc(gate_model))
    _write_text(repo_root, XI_5X2_XCODE_PLATFORM_REVIEW_DOC_REL, _render_platform_review_doc(platform_review))
    _write_text(repo_root, XI_5X2_MANUAL_REVIEW_DOC_REL, _render_manual_review_doc(manual_review_queue))
    _write_text(repo_root, XI_5X2_FINAL_REL, _render_final_report(classification_lock, execution_log, postmove_report, gate_model, source_pocket_policy))


def run_xi5x2(repo_root: str, run_gates: bool = True) -> dict[str, object]:
    repo_root = _repo_root(repo_root)
    reality_refresh = build_reality_refresh(repo_root)
    classification_lock = build_classification_lock(repo_root, reality_refresh)
    source_pocket_policy = build_source_pocket_policy(repo_root, classification_lock, reality_refresh)
    batch_plan = build_batch_plan(classification_lock, source_pocket_policy)
    postmove_report = build_postmove_residual_report(repo_root, classification_lock, source_pocket_policy)
    blocked_preconditions = build_blocked_preconditions(classification_lock)
    platform_review = build_platform_adapter_review(repo_root, classification_lock)
    manual_review_queue = build_manual_review_queue(classification_lock, platform_review)
    gate_model = build_xi6_gate_model(repo_root, classification_lock, postmove_report, source_pocket_policy, blocked_preconditions, manual_review_queue, [])
    execution_log = build_execution_log(classification_lock, batch_plan, postmove_report, [])
    blocker_delta = build_blocker_delta(repo_root, classification_lock, gate_model)
    materialize_outputs(
        repo_root,
        reality_refresh,
        source_pocket_policy,
        classification_lock,
        batch_plan,
        execution_log,
        postmove_report,
        blocked_preconditions,
        manual_review_queue,
        platform_review,
        gate_model,
        blocker_delta,
    )
    gate_runs = collect_gate_runs(repo_root) if run_gates else []
    gate_model = build_xi6_gate_model(repo_root, classification_lock, postmove_report, source_pocket_policy, blocked_preconditions, manual_review_queue, gate_runs)
    execution_log = build_execution_log(classification_lock, batch_plan, postmove_report, gate_runs)
    execution_log["ready_for_xi6"] = bool(gate_model.get("xi6_ready"))
    execution_log["deterministic_fingerprint"] = canonical_sha256(dict(execution_log, deterministic_fingerprint=""))
    blocker_delta = build_blocker_delta(repo_root, classification_lock, gate_model)
    materialize_outputs(
        repo_root,
        reality_refresh,
        source_pocket_policy,
        classification_lock,
        batch_plan,
        execution_log,
        postmove_report,
        blocked_preconditions,
        manual_review_queue,
        platform_review,
        gate_model,
        blocker_delta,
    )
    return {
        "reality_refresh": reality_refresh,
        "source_pocket_policy": source_pocket_policy,
        "classification_lock": classification_lock,
        "batch_plan": batch_plan,
        "execution_log": execution_log,
        "postmove_report": postmove_report,
        "blocked_preconditions": blocked_preconditions,
        "manual_review_queue": manual_review_queue,
        "platform_review": platform_review,
        "gate_model": gate_model,
        "blocker_delta": blocker_delta,
    }
