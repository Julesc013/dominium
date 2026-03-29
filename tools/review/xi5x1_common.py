"""Deterministic Xi-5x1 residual convergence helpers."""

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

XI5X1_CLASSIFICATION_LOCK_REL = "data/restructure/xi5x1_residual_classification_lock.json"
XI5X1_BATCH_PLAN_REL = "data/restructure/xi5x1_batch_plan.json"
XI5X1_EXECUTION_LOG_REL = "data/restructure/xi5x1_execution_log.json"
XI5X1_POSTMOVE_RESIDUAL_REPORT_REL = "data/restructure/xi5x1_postmove_residual_src_report.json"
XI5X1_XI6_GATE_MODEL_REL = "data/restructure/xi5x1_xi6_gate_model.json"

XI_5D_RESIDUAL_LOCK_REPORT_REL = "docs/audit/XI_5D_RESIDUAL_LOCK_REPORT.md"
XI_5B_SAFE_BATCH_REPORT_REL = "docs/audit/XI_5B_SAFE_BATCH_REPORT.md"
XI_5C_MERGE_AND_MANUAL_REVIEW_REPORT_REL = "docs/audit/XI_5C_MERGE_AND_MANUAL_REVIEW_REPORT.md"
XI_5E_COMPLETION_REPORT_REL = "docs/audit/XI_5E_COMPLETION_REPORT.md"
XI_5X1_FINAL_REL = "docs/audit/XI_5X1_FINAL.md"

VALIDATION_FAST_REL = "data/audit/validation_report_FAST.json"
VALIDATION_STRICT_REL = "data/audit/validation_report_STRICT.json"
ARCH_AUDIT2_REL = "data/audit/arch_audit2_report.json"

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

WORLDGEN_INIT_SOURCE = "src/worldgen/__init__.py"
WORLDGEN_INIT_TARGET = "worldgen/__init__.py"
WORLDGEN_INIT_QUARANTINE = "attic/src_quarantine/src/worldgen/__init__.py"

BATCH_SAFE_1 = "BATCH_SAFE_1"
BATCH_SAFE_2 = "BATCH_SAFE_2"
BATCH_MERGE_1 = "BATCH_MERGE_1"
BATCH_HIGH_RISK_1 = "BATCH_HIGH_RISK_1"
BATCH_MANUAL_REVIEW = "BATCH_MANUAL_REVIEW"
BATCH_ALLOWED_RESIDUALS = "BATCH_ALLOWED_RESIDUALS"
BATCH_BLOCKED_PRECONDITIONS = "BATCH_BLOCKED_PRECONDITIONS"


class Xi5x1InputsMissing(RuntimeError):
    """Raised when authoritative Xi-5a inputs are unavailable."""


def _read_json_required(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        payload = None
    if not isinstance(payload, dict) or not payload:
        raise Xi5x1InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5x1.missing_inputs",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _required_inputs() -> tuple[str, ...]:
    return (
        XI_5A_FINAL_REL,
        XI5A_EXECUTION_LOG_REL,
        XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        "docs/canon/constitution_v1.md",
        "docs/canon/glossary_v1.md",
        "AGENTS.md",
    )


def ensure_inputs(repo_root: str) -> None:
    missing = [rel for rel in _required_inputs() if not os.path.exists(_repo_abs(repo_root, rel))]
    if missing:
        raise Xi5x1InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5x1.missing_inputs",
                    "missing_inputs": sorted(set(missing)),
                },
                indent=2,
                sort_keys=True,
            )
        )


def _load_residual_rows(repo_root: str) -> list[dict[str, object]]:
    payload = _read_json_required(repo_root, XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL)
    return [dict(item or {}) for item in list(payload.get("deferred_to_xi5b_remaining") or [])]


def _file_exists(repo_root: str, rel_path: str) -> bool:
    return os.path.exists(_repo_abs(repo_root, rel_path))


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


def _worldgen_merge_safe(repo_root: str) -> bool:
    source_abs = _repo_abs(repo_root, WORLDGEN_INIT_SOURCE)
    target_abs = _repo_abs(repo_root, WORLDGEN_INIT_TARGET)
    if not os.path.exists(source_abs) or not os.path.exists(target_abs):
        return False
    try:
        source_text = open(source_abs, "r", encoding="utf-8").read().strip()
        target_text = open(target_abs, "r", encoding="utf-8").read().strip()
    except OSError:
        return False
    return source_text.startswith('"""') and "Deterministic world generation domain helpers." in source_text and bool(target_text)


def _classification_for_row(repo_root: str, row: Mapping[str, object]) -> dict[str, object]:
    source_path = _norm_rel(row.get("source_path"))
    target_path = _norm_rel(row.get("target_path"))
    prior_phase_class = _token(row.get("deferred_phase_class"))
    payload: dict[str, object] = {
        "source_path": source_path,
        "intended_target_path": target_path,
        "prior_deferred_phase_class": prior_phase_class,
        "evidence_refs": [XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL],
        "live_source_exists_at_lock": _file_exists(repo_root, source_path),
        "live_target_exists_at_lock": bool(target_path) and _file_exists(repo_root, target_path),
        "manual_review_required": False,
        "move_allowed_now": False,
        "shim_required": False,
        "batchable": False,
        "xi6_relevant": True,
    }

    if source_path == WORLDGEN_INIT_SOURCE:
        payload.update(
            {
                "classification": "MERGE_REQUIRED",
                "intended_target_path": WORLDGEN_INIT_QUARANTINE,
                "semantic_risk_level": "medium",
                "future_phase_owner": "xi5c",
                "proposed_batch_id": BATCH_MERGE_1,
                "move_allowed_now": _worldgen_merge_safe(repo_root),
                "batchable": True,
                "rationale": (
                    "The only remaining top-level src file conflicts with an active canonical worldgen package initializer. "
                    "The source file is a stale docstring-only duplicate, so the safe action is to preserve the canonical package "
                    "and quarantine the obsolete shadow copy."
                ),
                "evidence_refs": [
                    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
                    WORLDGEN_INIT_SOURCE,
                    WORLDGEN_INIT_TARGET,
                ],
            }
        )
        return payload

    if source_path.startswith("libs/build_identity/src/") or source_path.startswith("libs/ui_backends/win32/src/"):
        payload.update(
            {
                "classification": "SAFE_LOCAL_REHOME",
                "semantic_risk_level": "low",
                "future_phase_owner": "xi5b",
                "proposed_batch_id": BATCH_SAFE_1,
                "move_allowed_now": True,
                "batchable": True,
                "rationale": "Component-local source file with a collision-free target and narrowly scoped local build rewires.",
                "evidence_refs": [
                    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
                    "libs/build_identity/CMakeLists.txt" if source_path.startswith("libs/build_identity/src/") else "libs/ui_backends/win32/CMakeLists.txt",
                ],
            }
        )
        return payload

    if source_path.startswith("tools/ui_shared/src/"):
        payload.update(
            {
                "classification": "SAFE_LOCAL_REHOME",
                "semantic_risk_level": "medium",
                "future_phase_owner": "xi5b",
                "proposed_batch_id": BATCH_SAFE_2,
                "move_allowed_now": True,
                "batchable": True,
                "rationale": (
                    "Component-local UI shared tree with clean direct target paths. Active references are limited to build and include "
                    "paths under CMake and tool targets."
                ),
                "evidence_refs": [
                    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
                    "CMakeLists.txt",
                    "tests/ux/CMakeLists.txt",
                    "tools/ui_bind/CMakeLists.txt",
                ],
            }
        )
        return payload

    if source_path.startswith("packs/source/"):
        payload.update(
            {
                "classification": "BLOCKED_BY_MISSING_PRECONDITION",
                "semantic_risk_level": "medium",
                "future_phase_owner": "later",
                "proposed_batch_id": BATCH_BLOCKED_PRECONDITIONS,
                "manual_review_required": True,
                "rationale": (
                    "Current import tools and determinism tests still treat packs/source as the live source-pack root, so attic routing "
                    "would require an explicit source-pack path policy rather than a pure mechanical move."
                ),
                "evidence_refs": [
                    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
                    "tools/data/tool_srtm_import.py",
                    "tools/data/tool_spice_import.py",
                    "tools/xstack/testx/tests/test_srtm_import_determinism.py",
                    "tools/xstack/testx/tests/test_spice_import_determinism.py",
                ],
            }
        )
        return payload

    if source_path.startswith("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources/"):
        payload.update(
            {
                "classification": "BLOCKED_BY_MISSING_PRECONDITION",
                "semantic_risk_level": "high",
                "future_phase_owner": "manual",
                "proposed_batch_id": BATCH_MANUAL_REVIEW,
                "manual_review_required": True,
                "rationale": (
                    "The macOS adapter source root is wired into an Xcode project file and cannot be safely renamed without synchronizing "
                    "the project surface."
                ),
                "evidence_refs": [
                    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
                    "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMac.xcodeproj/project.pbxproj",
                ],
            }
        )
        return payload

    if source_path.startswith("legacy/launcher_core_launcher/launcher/core/source/") or source_path.startswith("legacy/setup_core_setup/setup/core/source/"):
        payload.update(
            {
                "classification": "HIGH_RISK_BUILD_OR_TOOLCHAIN",
                "semantic_risk_level": "high",
                "future_phase_owner": "xi5c",
                "proposed_batch_id": BATCH_HIGH_RISK_1,
                "manual_review_required": True,
                "rationale": (
                    "Legacy source pocket sits under active product/core trees. The mirrored target is obvious, but build-system ownership "
                    "and legacy integration need explicit review before mass local rehome."
                ),
                "evidence_refs": [XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL],
            }
        )
        return payload

    if source_path.startswith("legacy/source/"):
        payload.update(
            {
                "classification": "LEGACY_KEEP_FOR_NOW",
                "semantic_risk_level": "medium",
                "future_phase_owner": "later",
                "proposed_batch_id": BATCH_ALLOWED_RESIDUALS,
                "rationale": (
                    "Legacy umbrella source tree is not a dangerous active shadow root after Xi-5a, but it still requires a deliberate "
                    "convergence or quarantine policy before Xi-6."
                ),
                "evidence_refs": [XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL],
            }
        )
        return payload

    payload.update(
        {
            "classification": "OTHER_UNMAPPED_RESIDUAL",
            "semantic_risk_level": "high",
            "future_phase_owner": "manual",
            "proposed_batch_id": BATCH_MANUAL_REVIEW,
            "manual_review_required": True,
            "rationale": "Residual row did not match a known Xi-5x1 class and requires explicit review.",
            "evidence_refs": [XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL],
        }
    )
    return payload


def build_classification_lock(repo_root: str) -> dict[str, object]:
    ensure_inputs(repo_root)
    rows = [_classification_for_row(repo_root, row) for row in _load_residual_rows(repo_root)]
    rows = sorted(rows, key=lambda item: (_token(item.get("classification")), _norm_rel(item.get("source_path"))))
    class_counts: dict[str, int] = {}
    for row in rows:
        classification = _token(row.get("classification"))
        class_counts[classification] = int(class_counts.get(classification, 0)) + 1
    payload = {
        "report_id": "xi.5x1.residual_classification_lock.v1",
        "source_report_id": "xi.5a.postmove_residual_src_report.v4",
        "rows": rows,
        "row_count": len(rows),
        "classification_counts": dict(sorted(class_counts.items())),
        "live_root_file_counts_at_lock": _scan_root_file_counts(repo_root),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_batch_plan(classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]

    def batch_items(batch_id: str) -> list[str]:
        return sorted(_norm_rel(row.get("source_path")) for row in rows if _token(row.get("proposed_batch_id")) == batch_id)

    batches = [
        {
            "batch_id": BATCH_SAFE_1,
            "included_items": batch_items(BATCH_SAFE_1),
            "exclusion_logic": "Exclude tools/ui_shared and all legacy/content/manually blocked rows.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "No target collisions under libs/build_identity or libs/ui_backends/win32",
                "Local CMake rewires applied before validation",
            ],
            "expected_repo_effects": [
                "Remove component-local src roots under libs/build_identity and libs/ui_backends/win32",
                "Keep runtime semantics unchanged",
            ],
            "required_validation_profile": "STRICT",
            "rollback_notes": "git move reversal plus local CMake path rollback",
            "execution_allowed_in_this_pass": True,
        },
        {
            "batch_id": BATCH_SAFE_2,
            "included_items": batch_items(BATCH_SAFE_2),
            "exclusion_logic": "Exclude historical review references and keep only the live tools/ui_shared tree.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "CMake add_subdirectory/include paths updated to tools/ui_shared/ui_ir",
                "No target collisions under tools/ui_shared",
            ],
            "expected_repo_effects": [
                "Remove tools/ui_shared/src as an active component-local source root",
                "Preserve domino_ui_ir and related tool targets",
            ],
            "required_validation_profile": "STRICT",
            "rollback_notes": "git move reversal plus build/include path rollback",
            "execution_allowed_in_this_pass": True,
        },
        {
            "batch_id": BATCH_MERGE_1,
            "included_items": batch_items(BATCH_MERGE_1),
            "exclusion_logic": "Only the docstring-only worldgen package shadow remains eligible.",
            "ordering": "single item",
            "preconditions": [
                "Canonical worldgen/__init__.py exists",
                "Shadow copy is docstring-only and can be quarantined safely",
            ],
            "expected_repo_effects": [
                "Remove the last active top-level src file",
                "Preserve canonical worldgen package ownership",
            ],
            "required_validation_profile": "STRICT",
            "rollback_notes": "restore quarantined file to src/worldgen/__init__.py if needed",
            "execution_allowed_in_this_pass": True,
        },
        {
            "batch_id": BATCH_HIGH_RISK_1,
            "included_items": batch_items(BATCH_HIGH_RISK_1),
            "exclusion_logic": "Only legacy launcher/setup core source pockets remain here.",
            "ordering": "lexicographic by source_path",
            "preconditions": [
                "Legacy build ownership and include surfaces mapped explicitly",
                "Product-level review completed",
            ],
            "expected_repo_effects": [
                "Potentially remove legacy nested source roots under launcher/setup core",
            ],
            "required_validation_profile": "FULL",
            "rollback_notes": "batch must be reversible as one unit",
            "execution_allowed_in_this_pass": False,
        },
        {
            "batch_id": BATCH_MANUAL_REVIEW,
            "included_items": batch_items(BATCH_MANUAL_REVIEW),
            "exclusion_logic": "Only residuals tied to external project metadata or unresolved ownership remain here.",
            "ordering": "lexicographic by source_path",
            "preconditions": ["Human review of project metadata"],
            "expected_repo_effects": ["Resolve project-file synchronized residuals or quarantine them explicitly"],
            "required_validation_profile": "FULL",
            "rollback_notes": "do not execute without manual signoff",
            "execution_allowed_in_this_pass": False,
        },
        {
            "batch_id": BATCH_ALLOWED_RESIDUALS,
            "included_items": batch_items(BATCH_ALLOWED_RESIDUALS),
            "exclusion_logic": "Legacy umbrella source tree remains in place until a dedicated later convergence pass.",
            "ordering": "lexicographic by source_path",
            "preconditions": ["Dedicated legacy convergence plan"],
            "expected_repo_effects": ["No execution in Xi-5x1; residual remains explicitly tracked"],
            "required_validation_profile": "N/A",
            "rollback_notes": "not executed in this pass",
            "execution_allowed_in_this_pass": False,
        },
        {
            "batch_id": BATCH_BLOCKED_PRECONDITIONS,
            "included_items": batch_items(BATCH_BLOCKED_PRECONDITIONS),
            "exclusion_logic": "Rows needing source-pack path policy or external project synchronization stay here.",
            "ordering": "lexicographic by source_path",
            "preconditions": ["Explicit policy for pack source roots or project metadata synchronization"],
            "expected_repo_effects": ["No execution in Xi-5x1; residual remains blocked with named reasons"],
            "required_validation_profile": "N/A",
            "rollback_notes": "not executed in this pass",
            "execution_allowed_in_this_pass": False,
        },
    ]
    payload = {
        "report_id": "xi.5x1.batch_plan.v1",
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "batches": batches,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _execution_status(repo_root: str, row: Mapping[str, object]) -> tuple[str, str]:
    source_path = _norm_rel(row.get("source_path"))
    target_path = _norm_rel(row.get("intended_target_path"))
    source_exists = _file_exists(repo_root, source_path)
    target_exists = bool(target_path) and _file_exists(repo_root, target_path)
    if _token(row.get("classification")) == "MERGE_REQUIRED":
        if (not source_exists) and _file_exists(repo_root, WORLDGEN_INIT_TARGET) and _file_exists(repo_root, WORLDGEN_INIT_QUARANTINE):
            return ("resolved_quarantined", WORLDGEN_INIT_QUARANTINE)
    if (not source_exists) and target_exists:
        return ("executed", target_path)
    if source_exists:
        return ("pending", source_path)
    return ("missing", target_path or source_path)


def build_postmove_residual_report(repo_root: str, classification_lock: Mapping[str, object]) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    remaining_rows: list[dict[str, object]] = []
    remaining_counts: dict[str, int] = {}
    for row in rows:
        status, _ = _execution_status(repo_root, row)
        if status.startswith("executed") or status.startswith("resolved"):
            continue
        item = {
            "classification": _token(row.get("classification")),
            "future_phase_owner": _token(row.get("future_phase_owner")),
            "source_path": _norm_rel(row.get("source_path")),
            "intended_target_path": _norm_rel(row.get("intended_target_path")),
            "semantic_risk_level": _token(row.get("semantic_risk_level")),
            "rationale": str(row.get("rationale") or "").strip(),
        }
        remaining_rows.append(item)
        key = _token(item.get("classification"))
        remaining_counts[key] = int(remaining_counts.get(key, 0)) + 1
    payload = {
        "report_id": "xi.5x1.postmove_residual_src_report.v1",
        "dangerous_shadow_root_paths_remaining": _scan_runtime_shadow_paths(repo_root),
        "remaining_root_file_counts": _scan_root_file_counts(repo_root),
        "remaining_rows": sorted(remaining_rows, key=lambda item: (_token(item.get("classification")), _norm_rel(item.get("source_path")))),
        "remaining_classification_counts": dict(sorted(remaining_counts.items())),
        "unexpected_runtime_critical_src_paths": _scan_runtime_shadow_paths(repo_root),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
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


def build_xi6_gate_model(
    repo_root: str,
    classification_lock: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_runs: Iterable[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    remaining_counts = dict(postmove_report.get("remaining_classification_counts") or {})
    dangerous_shadow_count = len(list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []))
    hard_blockers: list[dict[str, object]] = []
    soft_advisories: list[dict[str, object]] = []

    if dangerous_shadow_count:
        hard_blockers.append(
            {
                "blocker_id": "dangerous_shadow_roots_remaining",
                "count": dangerous_shadow_count,
                "paths": list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []),
            }
        )

    for blocker_class in (
        "SAFE_LOCAL_REHOME",
        "MERGE_REQUIRED",
        "HIGH_RISK_BUILD_OR_TOOLCHAIN",
        "BLOCKED_BY_MISSING_PRECONDITION",
        "LEGACY_KEEP_FOR_NOW",
        "OTHER_UNMAPPED_RESIDUAL",
    ):
        count = int(remaining_counts.get(blocker_class, 0) or 0)
        if count:
            hard_blockers.append(
                {
                    "blocker_id": _token(blocker_class).lower(),
                    "count": count,
                    "classification": blocker_class,
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

    if int(remaining_counts.get("BLOCKED_BY_MISSING_PRECONDITION", 0) or 0):
        soft_advisories.append(
            {
                "advisory_id": "content_source_policy_needed",
                "count": int(remaining_counts.get("BLOCKED_BY_MISSING_PRECONDITION", 0) or 0),
            }
        )

    payload = {
        "report_id": "xi.5x1.xi6_gate_model.v1",
        "hard_blockers": hard_blockers,
        "soft_advisories": soft_advisories,
        "required_invariants": [
            "constitution_v1.md A1",
            "constitution_v1.md A8",
            "constitution_v1.md A10",
            "AGENTS.md §2",
            "AGENTS.md §5",
        ],
        "required_residual_classes_to_be_zero_for_xi6": [
            "SAFE_LOCAL_REHOME",
            "MERGE_REQUIRED",
            "HIGH_RISK_BUILD_OR_TOOLCHAIN",
            "BLOCKED_BY_MISSING_PRECONDITION",
            "LEGACY_KEEP_FOR_NOW",
            "OTHER_UNMAPPED_RESIDUAL",
        ],
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
            "targeted_xi5x1_tests",
        ],
        "repo_structure_conditions": [
            "No dangerous shadow roots under top-level src or app/src",
            "No remaining executable Xi-5 safe local rehomes",
            "No unresolved legacy source pockets or blocked preconditions",
        ],
        "documentation_requirements": [
            XI_5A_FINAL_REL,
            XI_5X1_FINAL_REL,
            XI_5D_RESIDUAL_LOCK_REPORT_REL,
            XI_5B_SAFE_BATCH_REPORT_REL,
            XI_5C_MERGE_AND_MANUAL_REVIEW_REPORT_REL,
            XI_5E_COMPLETION_REPORT_REL,
        ],
        "allowed_residual_exceptions": [],
        "readiness_boolean_derivation_rule": "Xi-6 is ready only when all hard_blockers are absent and all required_validation_gates pass.",
        "xi6_ready": not hard_blockers,
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


def _run_gate(repo_root: str, gate_id: str, command: list[str], json_report_rel: str = "") -> dict[str, object]:
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
            for field_name in ("deterministic_fingerprint", "result", "matched_case_count", "mismatched_case_count", "error_count"):
                token = parsed.get(field_name)
                if token not in (None, ""):
                    payload[field_name] = token
        else:
            payload["output_excerpt"] = text.splitlines()[-10:]
    if json_report_rel:
        report = _load_optional_json(repo_root, json_report_rel)
        if report:
            payload["report_rel"] = json_report_rel
            for field_name in ("deterministic_fingerprint", "result", "error_count", "warning_count"):
                token = report.get(field_name)
                if token not in (None, ""):
                    payload[field_name] = token
    return payload


def run_validation_gates(repo_root: str) -> list[dict[str, object]]:
    gates = [
        ("build_verify", ["cmake", "--build", "--preset", "verify", "--config", "Debug", "--target", "all_runtime"], ""),
        ("validate_fast", ["python", "-B", "tools/validation/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"], VALIDATION_FAST_REL),
        ("validate_strict", ["python", "-B", "tools/validation/tool_run_validation.py", "--repo-root", ".", "--profile", "STRICT"], VALIDATION_STRICT_REL),
        ("arch_audit_2", ["python", "-B", "tools/audit/tool_run_arch_audit.py", "--repo-root", "."], ARCH_AUDIT2_REL),
        ("omega_1_worldgen_lock", ["python", "-B", "tools/worldgen/tool_verify_worldgen_lock.py", "--repo-root", "."], ""),
        ("omega_2_baseline_universe", ["python", "-B", "tools/mvp/tool_verify_baseline_universe.py", "--repo-root", "."], ""),
        ("omega_3_gameplay_loop", ["python", "-B", "tools/mvp/tool_verify_gameplay_loop.py", "--repo-root", "."], ""),
        ("omega_4_disaster_suite", ["python", "-B", "tools/mvp/tool_run_disaster_suite.py", "--repo-root", "."], ""),
        ("omega_5_ecosystem_verify", ["python", "-B", "tools/mvp/tool_verify_ecosystem.py", "--repo-root", "."], ""),
        ("omega_6_update_sim", ["python", "-B", "tools/mvp/tool_run_update_sim.py", "--repo-root", "."], ""),
        ("trust_strict_suite", ["python", "-B", "tools/security/tool_run_trust_strict_suite.py", "--repo-root", "."], ""),
        (
            "targeted_xi5x1_tests",
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
                "test_no_dangerous_shadow_roots_after_xi5x1,test_xi5x1_safe_batches_consumed,test_xi5x1_residual_classification_lock_deterministic,test_xi5x1_batch_plan_deterministic,test_xi5x1_xi6_gate_model_deterministic",
            ],
            "",
        ),
    ]
    return [_run_gate(repo_root, gate_id, command, report_rel) for gate_id, command, report_rel in gates]


def build_execution_log(
    repo_root: str,
    classification_lock: Mapping[str, object],
    batch_plan: Mapping[str, object],
    postmove_report: Mapping[str, object],
    gate_runs: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    rows = [dict(item or {}) for item in list(classification_lock.get("rows") or [])]
    safe_reference_updates = {
        BATCH_SAFE_1: [
            "libs/build_identity/CMakeLists.txt",
            "libs/ui_backends/win32/CMakeLists.txt",
        ],
        BATCH_SAFE_2: [
            "CMakeLists.txt",
            "tests/ux/CMakeLists.txt",
            "tools/ui_bind/CMakeLists.txt",
        ],
        BATCH_MERGE_1: [],
    }
    executed_items: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: (_token(item.get("proposed_batch_id")), _norm_rel(item.get("source_path")))):
        batch_id = _token(row.get("proposed_batch_id"))
        status, resolved_target = _execution_status(repo_root, row)
        if not status.startswith("executed") and not status.startswith("resolved"):
            continue
        executed_items.append(
            {
                "source_path": _norm_rel(row.get("source_path")),
                "target_path": _norm_rel(resolved_target),
                "batch_id": batch_id,
                "classification": _token(row.get("classification")),
                "action": "quarantine_stale_duplicate" if batch_id == BATCH_MERGE_1 else "move",
                "shim_added": False,
                "references_updated": list(safe_reference_updates.get(batch_id, [])),
                "validation_required": "STRICT",
            }
        )
    remaining_counts = dict(postmove_report.get("remaining_classification_counts") or {})
    payload = {
        "report_id": "xi.5x1.execution_log.v1",
        "xi5a_ground_truth": {
            "xi5a_final_doc": XI_5A_FINAL_REL,
            "xi5a_execution_log": XI5A_EXECUTION_LOG_REL,
            "xi5a_postmove_residual_report": XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        },
        "source_classification_fingerprint": _token(classification_lock.get("deterministic_fingerprint")),
        "source_batch_plan_fingerprint": _token(batch_plan.get("deterministic_fingerprint")),
        "executed_items": executed_items,
        "executed_item_count": len(executed_items),
        "remaining_classification_counts": remaining_counts,
        "dangerous_shadow_root_paths_remaining": list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []),
        "gate_runs": [dict(item or {}) for item in list(gate_runs or [])],
        "ready_for_xi6": False,
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


def _render_residual_lock_report(classification_lock: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-29",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5D Residual Lock Report",
        "",
        "## Summary",
        "",
        "- Xi-5a residual rows locked: `{}`".format(int(classification_lock.get("row_count", 0) or 0)),
    ]
    for name, count in sorted(dict(classification_lock.get("classification_counts") or {}).items()):
        lines.append("- `{}`: `{}`".format(_token(name), int(count or 0)))
    return "\n".join(lines) + "\n"


def _render_safe_batch_report(batch_plan: Mapping[str, object], execution_log: Mapping[str, object]) -> str:
    executed = [item for item in list(execution_log.get("executed_items") or []) if _token(item.get("batch_id")) in {BATCH_SAFE_1, BATCH_SAFE_2}]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-29",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5B Safe Batch Report",
        "",
        "## Executed Safe Batches",
        "",
        "- `{}` items executed from `{}` and `{}`.".format(len(executed), BATCH_SAFE_1, BATCH_SAFE_2),
        "",
        "## Batch Counts",
        "",
    ]
    for batch in list(batch_plan.get("batches") or []):
        batch_id = _token(dict(batch).get("batch_id"))
        if batch_id not in {BATCH_SAFE_1, BATCH_SAFE_2}:
            continue
        lines.append("- `{}`: `{}`".format(batch_id, len(list(dict(batch).get("included_items") or []))))
    return "\n".join(lines) + "\n"


def _render_merge_report(execution_log: Mapping[str, object], postmove_report: Mapping[str, object]) -> str:
    merge_items = [item for item in list(execution_log.get("executed_items") or []) if _token(item.get("batch_id")) == BATCH_MERGE_1]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-29",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5C Merge And Manual Review Report",
        "",
        "## Merge Resolution",
        "",
        "- merge/quarantine items resolved now: `{}`".format(len(merge_items)),
        "- manual-review items remaining: `{}`".format(
            int(dict(postmove_report.get("remaining_classification_counts") or {}).get("BLOCKED_BY_MISSING_PRECONDITION", 0) or 0)
            + int(dict(postmove_report.get("remaining_classification_counts") or {}).get("HIGH_RISK_BUILD_OR_TOOLCHAIN", 0) or 0)
        ),
    ]
    return "\n".join(lines) + "\n"


def _render_completion_report(postmove_report: Mapping[str, object], gate_model: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-29",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 final convergence summary",
        "",
        "# XI-5E Completion Report",
        "",
        "## Postmove State",
        "",
        "- dangerous shadow roots remaining: `{}`".format(len(list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []))),
        "- remaining residual rows: `{}`".format(len(list(postmove_report.get("remaining_rows") or []))),
        "- Xi-6 ready: `{}`".format("true" if gate_model.get("xi6_ready") else "false"),
    ]
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
        "Last Reviewed: 2026-03-29",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze report after residual convergence completes",
        "",
        "# XI-5X1 Final",
        "",
        "## Ground Truth Reused",
        "",
        "- Xi-5a outputs were treated as authoritative: `{}`, `{}`, `{}`.".format(
            XI_5A_FINAL_REL,
            XI5A_EXECUTION_LOG_REL,
            XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
        ),
        "",
        "## Xi-5x1 Result",
        "",
        "- deferred residual rows classified: `{}`".format(int(classification_lock.get("row_count", 0) or 0)),
        "- safe rows executed in this pass: `{}`".format(
            len([item for item in list(execution_log.get("executed_items") or []) if _token(item.get("batch_id")) in {BATCH_SAFE_1, BATCH_SAFE_2}])
        ),
        "- merge/high-risk items resolved now: `{}`".format(
            len([item for item in list(execution_log.get("executed_items") or []) if _token(item.get("batch_id")) == BATCH_MERGE_1])
        ),
        "- runtime-critical src paths remaining: `{}`".format(len(list(postmove_report.get("unexpected_runtime_critical_src_paths") or []))),
        "- dangerous shadow roots remaining: `{}`".format(len(list(postmove_report.get("dangerous_shadow_root_paths_remaining") or []))),
        "- top-level src file count: `{}`".format(int(dict(postmove_report.get("remaining_root_file_counts") or {}).get("src", 0) or 0)),
        "",
        "## Remaining Residuals By Class",
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
    lines.extend(
        [
            "",
            "## Next Phase",
            "",
            "- recommended next phase: `Xi-5x2` focused on legacy source pockets, content-source policy, and blocked external-project residuals.",
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
) -> None:
    _write_json(repo_root, XI5X1_CLASSIFICATION_LOCK_REL, classification_lock)
    _write_json(repo_root, XI5X1_BATCH_PLAN_REL, batch_plan)
    _write_json(repo_root, XI5X1_EXECUTION_LOG_REL, execution_log)
    _write_json(repo_root, XI5X1_POSTMOVE_RESIDUAL_REPORT_REL, postmove_report)
    _write_json(repo_root, XI5X1_XI6_GATE_MODEL_REL, gate_model)

    _write_text(repo_root, XI_5D_RESIDUAL_LOCK_REPORT_REL, _render_residual_lock_report(classification_lock))
    _write_text(repo_root, XI_5B_SAFE_BATCH_REPORT_REL, _render_safe_batch_report(batch_plan, execution_log))
    _write_text(repo_root, XI_5C_MERGE_AND_MANUAL_REVIEW_REPORT_REL, _render_merge_report(execution_log, postmove_report))
    _write_text(repo_root, XI_5E_COMPLETION_REPORT_REL, _render_completion_report(postmove_report, gate_model))
    _write_text(repo_root, XI_5X1_FINAL_REL, _render_final_report(classification_lock, execution_log, postmove_report, gate_model))


def run_xi5x1(repo_root: str, run_gates: bool = True) -> dict[str, object]:
    repo_root = _repo_root(repo_root)
    classification_lock = build_classification_lock(repo_root)
    batch_plan = build_batch_plan(classification_lock)
    postmove_report = build_postmove_residual_report(repo_root, classification_lock)
    gate_model = build_xi6_gate_model(repo_root, classification_lock, postmove_report, [])
    execution_log = build_execution_log(repo_root, classification_lock, batch_plan, postmove_report, [])
    materialize_outputs(repo_root, classification_lock, batch_plan, execution_log, postmove_report, gate_model)
    gate_runs = run_validation_gates(repo_root) if run_gates else []
    gate_model = build_xi6_gate_model(repo_root, classification_lock, postmove_report, gate_runs)
    execution_log = build_execution_log(repo_root, classification_lock, batch_plan, postmove_report, gate_runs)
    execution_log["ready_for_xi6"] = bool(gate_model.get("xi6_ready"))
    execution_log["deterministic_fingerprint"] = canonical_sha256(dict(execution_log, deterministic_fingerprint=""))
    materialize_outputs(repo_root, classification_lock, batch_plan, execution_log, postmove_report, gate_model)
    return {
        "classification_lock": classification_lock,
        "batch_plan": batch_plan,
        "execution_log": execution_log,
        "postmove_report": postmove_report,
        "gate_model": gate_model,
    }
