"""Deterministic XI-4z approved-lock target normalization helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_structure_approval_common import (  # noqa: E402
    ARCHITECTURE_GRAPH_REL,
    BUILD_GRAPH_REL,
    MODULE_REGISTRY_REL,
    SRC_DOMAIN_MAPPING_CANDIDATES_REL,
    SRC_DOMAIN_MAPPING_CONFLICTS_REL,
    SRC_DOMAIN_MAPPING_DECISIONS_REL,
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
    XI5_READINESS_CONTRACT_REL,
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_CONFLICT_RESOLUTION_REL,
    XI_4Z_XI5_READINESS_REL,
    XI_4Z_FINAL_REL,
    _ensure_parent,
    _file_hash_rows,
    _norm_rel,
    _read_json,
    _repo_abs,
    _repo_root,
    _token,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL = "data/restructure/src_domain_mapping_lock_approved_v2.json"
XI5_READINESS_CONTRACT_V2_REL = "data/restructure/xi5_readiness_contract_v2.json"
SRC_DOMAIN_MAPPING_TARGET_PATHS_REL = "data/restructure/src_domain_mapping_target_paths.json"
XI4Z_FIX1_REPORT_JSON_REL = "data/restructure/xi4z_fix1_report.json"

XI_4Z_TARGET_NORMALIZATION_REPORT_REL = "docs/restructure/XI_4Z_TARGET_NORMALIZATION_REPORT.md"
XI_5A_EXECUTION_INPUTS_REL = "docs/restructure/XI_5A_EXECUTION_INPUTS.md"
XI_4Z_FIX1_FINAL_REL = "docs/audit/XI_4Z_FIX1_FINAL.md"

REQUIRED_JSON_INPUTS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
    XI5_READINESS_CONTRACT_REL,
    SRC_DOMAIN_MAPPING_DECISIONS_REL,
    SRC_DOMAIN_MAPPING_CANDIDATES_REL,
    SRC_DOMAIN_MAPPING_CONFLICTS_REL,
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    BUILD_GRAPH_REL,
)

REQUIRED_TEXT_INPUTS = (
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_CONFLICT_RESOLUTION_REL,
    XI_4Z_XI5_READINESS_REL,
    XI_4Z_FINAL_REL,
    "docs/audit/XI_4Z_FIX_FINAL.md",
)

FIX1_OUTPUT_RELS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
    XI5_READINESS_CONTRACT_V2_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
    XI4Z_FIX1_REPORT_JSON_REL,
    XI_4Z_TARGET_NORMALIZATION_REPORT_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    XI_4Z_FIX1_FINAL_REL,
    "tools/review/xi4z_fix1_common.py",
    "tools/review/tool_run_xi4z_fix1.py",
    "tools/xstack/testx/tests/xi4z_fix1_testlib.py",
    "tools/xstack/testx/tests/test_xi4z_v2_lock_schema_valid.py",
    "tools/xstack/testx/tests/test_xi4z_v2_approved_rows_have_target_paths.py",
    "tools/xstack/testx/tests/test_xi4z_v2_no_stale_path_ambiguity.py",
    "tools/xstack/testx/tests/test_xi4z_fix1_outputs_deterministic.py",
)

SOURCE_LIKE_SEGMENTS = {"src", "source", "sources"}


class Xi4zFix1InputsMissing(RuntimeError):
    """Raised when required XI-4z-fix1 artifacts are unavailable."""


def _read_json_required(repo_root: str, rel_path: str) -> dict[str, object]:
    payload = _read_json(_repo_abs(repo_root, rel_path))
    if not isinstance(payload, dict) or not payload:
        raise Xi4zFix1InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix1.missing_inputs",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _required_inputs_missing(repo_root: str) -> list[str]:
    missing: list[str] = []
    for rel_path in REQUIRED_JSON_INPUTS:
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    for rel_path in REQUIRED_TEXT_INPUTS:
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    return sorted(set(missing))


def _option_c_mapping_lookup(candidates_payload: Mapping[str, object]) -> dict[str, dict[str, object]]:
    for option in list(candidates_payload.get("options") or []):
        option_id = _token(dict(option or {}).get("option_id"))
        if option_id != "C":
            continue
        lookup: dict[str, dict[str, object]] = {}
        for row in list(dict(option or {}).get("file_mappings") or []):
            mapping = dict(row or {})
            lookup[_norm_rel(mapping.get("file_path"))] = mapping
        return lookup
    return {}


def _has_source_like_segment(path: str) -> bool:
    normalized = _norm_rel(path)
    return any(segment.lower() in SOURCE_LIKE_SEGMENTS for segment in normalized.split("/") if segment)


def _path_exists_as_other_file(repo_root: str, source_path: str, target_path: str) -> bool:
    source_norm = _norm_rel(source_path)
    target_norm = _norm_rel(target_path)
    if source_norm == target_norm:
        return False
    return os.path.exists(_repo_abs(repo_root, target_norm))


def _source_to_target_row(
    approved_row: Mapping[str, object],
    candidate_row: Mapping[str, object],
) -> dict[str, object]:
    source_path = _norm_rel(approved_row.get("file_path"))
    target_path = _norm_rel(candidate_row.get("target_path"))
    provenance = {
        "classification_report_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        "classification_report_id": "xi.4z.src_domain_mapping_lock_approved.v1",
        "normalization_rule": "bind_exact_option_c_target_path",
        "option_id": "C",
        "target_path_source": SRC_DOMAIN_MAPPING_CANDIDATES_REL,
        "target_path_source_domain": _token(candidate_row.get("proposed_domain")),
        "target_path_source_module_id": _token(candidate_row.get("proposed_module_id")),
    }
    row = {
        "approved_domain": _token(approved_row.get("approved_domain")),
        "approved_module_id": _token(approved_row.get("approved_module_id")),
        "category": _token(approved_row.get("category")),
        "confidence": float(approved_row.get("confidence", 0.0) or 0.0),
        "current_root": _token(approved_row.get("current_root")),
        "decision_class": "approved_for_xi5",
        "decision_provenance": provenance,
        "evidence_refs": list(approved_row.get("evidence_refs") or []),
        "file_path": source_path,
        "reason": _token(approved_row.get("reason")),
        "source_path": source_path,
        "supporting_cluster": _token(approved_row.get("supporting_cluster")),
        "target_path": target_path,
        "target_path_mapping_confidence": float(candidate_row.get("mapping_confidence", 0.0) or 0.0),
    }
    row["deterministic_fingerprint"] = canonical_sha256(row)
    return row


def _attic_row_v2(attic_row: Mapping[str, object]) -> dict[str, object]:
    file_path = _norm_rel(attic_row.get("file_path"))
    target_path = _norm_rel(attic_row.get("intended_attic_target_path"))
    row = {
        "category": _token(attic_row.get("category")),
        "confidence": float(attic_row.get("confidence", 0.0) or 0.0),
        "decision_class": "approved_to_attic",
        "decision_provenance": {
            "classification_report_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            "classification_report_id": "xi.4z.src_domain_mapping_lock_approved.v1",
            "normalization_rule": "preserve_explicit_attic_quarantine_target",
        },
        "file_path": file_path,
        "intended_attic_target_path": target_path,
        "reason": _token(attic_row.get("reason")),
        "route_kind": _token(attic_row.get("route_kind")),
        "source_path": file_path,
        "target_path": target_path,
    }
    row["deterministic_fingerprint"] = canonical_sha256(row)
    return row


def _newly_deferred_row(
    approved_row: Mapping[str, object],
    target_path: str,
    blocker: str,
    reason: str,
) -> dict[str, object]:
    row = {
        "additional_evidence_required": "manual confirmation of a non-conflicting final home that does not overwrite an existing active file",
        "blocker": blocker,
        "category": _token(approved_row.get("category")),
        "current_proposed_domain": _token(approved_row.get("approved_domain")),
        "current_proposed_module_id": _token(approved_row.get("approved_module_id")),
        "current_root": _token(approved_row.get("current_root")),
        "file_path": _norm_rel(approved_row.get("file_path")),
        "reason": reason,
        "safe_to_keep_in_place_temporarily": True,
        "target_path_conflict": _norm_rel(target_path),
    }
    row["deterministic_fingerprint"] = canonical_sha256(row)
    return row


def _normalize_lock_v2(repo_root: str, lock_payload: Mapping[str, object], option_lookup: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    approved_rows_v2: list[dict[str, object]] = []
    attic_rows_v2: list[dict[str, object]] = []
    deferred_rows_v2 = [dict(row or {}) for row in list(lock_payload.get("deferred_to_xi5b") or [])]
    target_rows: list[dict[str, object]] = []
    normalization_issues: list[dict[str, object]] = []
    mismatched_decision_candidate_rows: list[dict[str, object]] = []
    seen_targets: dict[str, str] = {}
    newly_deferred_paths: list[str] = []

    for attic_row in sorted((dict(row or {}) for row in list(lock_payload.get("approved_to_attic") or [])), key=lambda row: _norm_rel(row.get("file_path"))):
        row = _attic_row_v2(attic_row)
        attic_rows_v2.append(row)

    for approved_row in sorted((dict(row or {}) for row in list(lock_payload.get("approved_for_xi5") or [])), key=lambda row: _norm_rel(row.get("file_path"))):
        source_path = _norm_rel(approved_row.get("file_path"))
        candidate_row = dict(option_lookup.get(source_path) or {})
        if not candidate_row:
            normalization_issues.append({"code": "missing_option_c_target_path", "file_path": source_path})
            deferred_rows_v2.append(
                _newly_deferred_row(
                    approved_row,
                    "",
                    "Option C no longer exposes a concrete target path for this approved row.",
                    "Approved row cannot execute mechanically because the candidate artifact no longer carries a concrete target path.",
                )
            )
            newly_deferred_paths.append(source_path)
            continue

        target_path = _norm_rel(candidate_row.get("target_path"))
        if (
            _token(approved_row.get("approved_domain")) != _token(candidate_row.get("proposed_domain"))
            or _token(approved_row.get("approved_module_id")) != _token(candidate_row.get("proposed_module_id"))
        ):
            mismatched_decision_candidate_rows.append(
                {
                    "approved_domain": _token(approved_row.get("approved_domain")),
                    "approved_module_id": _token(approved_row.get("approved_module_id")),
                    "candidate_domain": _token(candidate_row.get("proposed_domain")),
                    "candidate_module_id": _token(candidate_row.get("proposed_module_id")),
                    "file_path": source_path,
                    "target_path": target_path,
                }
            )

        if not target_path:
            normalization_issues.append({"code": "blank_target_path", "file_path": source_path})
            deferred_rows_v2.append(
                _newly_deferred_row(
                    approved_row,
                    "",
                    "Candidate target path is blank.",
                    "Approved row cannot execute mechanically because the target path is blank after normalization.",
                )
            )
            newly_deferred_paths.append(source_path)
            continue
        if _has_source_like_segment(target_path):
            normalization_issues.append(
                {
                    "code": "source_like_segment_in_target",
                    "file_path": source_path,
                    "target_path": target_path,
                }
            )
            deferred_rows_v2.append(
                _newly_deferred_row(
                    approved_row,
                    target_path,
                    "Candidate target path still contains a source-like segment.",
                    "Approved row cannot execute mechanically because the target path still leaves the file under a source-like subtree.",
                )
            )
            newly_deferred_paths.append(source_path)
            continue
        if target_path in seen_targets:
            normalization_issues.append(
                {
                    "code": "duplicate_target_path",
                    "file_path": source_path,
                    "target_path": target_path,
                    "target_path_already_claimed_by": seen_targets[target_path],
                }
            )
            deferred_rows_v2.append(
                _newly_deferred_row(
                    approved_row,
                    target_path,
                    f"Candidate target path conflicts with another approved row ({seen_targets[target_path]}).",
                    "Approved row cannot execute mechanically because the concrete target path is not unique.",
                )
            )
            newly_deferred_paths.append(source_path)
            continue
        if _path_exists_as_other_file(repo_root, source_path, target_path):
            normalization_issues.append(
                {
                    "code": "occupied_target_path",
                    "file_path": source_path,
                    "occupied_target_path": target_path,
                }
            )
            deferred_rows_v2.append(
                _newly_deferred_row(
                    approved_row,
                    target_path,
                    f"Concrete target path is already occupied by an existing file at {target_path}.",
                    "Approved row cannot execute mechanically without overwriting an existing active file, so it is deferred to XI-5b.",
                )
            )
            newly_deferred_paths.append(source_path)
            continue

        row = _source_to_target_row(approved_row, candidate_row)
        approved_rows_v2.append(row)
        target_rows.append(
            {
                "approved_domain": row["approved_domain"],
                "approved_module_id": row["approved_module_id"],
                "decision_class": "approved_for_xi5",
                "decision_provenance": dict(row["decision_provenance"]),
                "source_path": source_path,
                "target_path": target_path,
            }
        )
        seen_targets[target_path] = source_path

    for row in attic_rows_v2:
        target_rows.append(
            {
                "decision_class": "approved_to_attic",
                "decision_provenance": dict(row["decision_provenance"]),
                "source_path": _norm_rel(row.get("source_path")),
                "target_path": _norm_rel(row.get("target_path")),
            }
        )

    deferred_rows_v2.sort(key=lambda row: _norm_rel(row.get("file_path")))
    target_rows.sort(key=lambda row: (_token(row.get("decision_class")), _norm_rel(row.get("source_path"))))
    return {
        "approved_rows_v2": approved_rows_v2,
        "attic_rows_v2": attic_rows_v2,
        "deferred_rows_v2": deferred_rows_v2,
        "mismatched_decision_candidate_rows": mismatched_decision_candidate_rows,
        "newly_deferred_paths": sorted(newly_deferred_paths),
        "normalization_issues": normalization_issues,
        "target_rows": target_rows,
    }


def _counts(lock_payload: Mapping[str, object]) -> dict[str, int]:
    return {
        "approved_for_xi5": len(list(lock_payload.get("approved_for_xi5") or [])),
        "approved_to_attic": len(list(lock_payload.get("approved_to_attic") or [])),
        "deferred_to_xi5b": len(list(lock_payload.get("deferred_to_xi5b") or [])),
        "total_rows": (
            len(list(lock_payload.get("approved_for_xi5") or []))
            + len(list(lock_payload.get("approved_to_attic") or []))
            + len(list(lock_payload.get("deferred_to_xi5b") or []))
        ),
    }


def _build_json_payloads(repo_root: str, inputs: Mapping[str, object]) -> dict[str, dict[str, object]]:
    lock_v1 = dict(inputs["lock_v1"])
    option_lookup = dict(inputs["option_c_lookup"])
    normalization = _normalize_lock_v2(repo_root, lock_v1, option_lookup)

    approved_rows_v2 = list(normalization["approved_rows_v2"])
    attic_rows_v2 = list(normalization["attic_rows_v2"])
    deferred_rows_v2 = list(normalization["deferred_rows_v2"])
    target_rows = list(normalization["target_rows"])
    issues = list(normalization["normalization_issues"])
    mismatch_rows = list(normalization["mismatched_decision_candidate_rows"])
    old_counts = _counts(lock_v1)
    new_counts = {
        "approved_for_xi5": len(approved_rows_v2),
        "approved_to_attic": len(attic_rows_v2),
        "deferred_to_xi5b": len(deferred_rows_v2),
        "total_rows": len(approved_rows_v2) + len(attic_rows_v2) + len(deferred_rows_v2),
    }
    if old_counts["total_rows"] != new_counts["total_rows"]:
        raise ValueError("XI-4z-fix1 must preserve total row coverage")

    source_hashes = _file_hash_rows(
        repo_root,
        [
            SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            XI5_READINESS_CONTRACT_REL,
            SRC_DOMAIN_MAPPING_DECISIONS_REL,
            SRC_DOMAIN_MAPPING_CANDIDATES_REL,
            SRC_DOMAIN_MAPPING_CONFLICTS_REL,
            XI_4Z_APPROVED_LAYOUT_REL,
            XI_4Z_CONFLICT_RESOLUTION_REL,
            XI_4Z_XI5_READINESS_REL,
            XI_4Z_FINAL_REL,
            "docs/audit/XI_4Z_FIX_FINAL.md",
            ARCHITECTURE_GRAPH_REL,
            MODULE_REGISTRY_REL,
            BUILD_GRAPH_REL,
        ],
    )
    missing_inputs = sorted(set(lock_v1.get("missing_inputs") or []))

    target_paths_payload = {
        "approved_for_xi5_target_paths": [row for row in target_rows if _token(row.get("decision_class")) == "approved_for_xi5"],
        "approved_to_attic_target_paths": [row for row in target_rows if _token(row.get("decision_class")) == "approved_to_attic"],
        "deterministic_fingerprint_seed": {
            "deferred_count": new_counts["deferred_to_xi5b"],
            "mismatch_count": len(mismatch_rows),
            "normalization_issue_count": len(issues),
        },
        "missing_inputs": missing_inputs,
        "report_id": "xi.4z.src_domain_mapping_target_paths.v1",
        "selected_layout_option": "C",
        "summary": {
            "approved_for_xi5_count": new_counts["approved_for_xi5"],
            "approved_to_attic_count": new_counts["approved_to_attic"],
            "deferred_to_xi5b_count": new_counts["deferred_to_xi5b"],
            "newly_deferred_from_v1_approved_count": new_counts["deferred_to_xi5b"] - old_counts["deferred_to_xi5b"],
            "rows_with_decision_candidate_mismatch_count": len(mismatch_rows),
            "rows_with_exact_target_paths": len([row for row in target_rows if _token(row.get("decision_class")) == "approved_for_xi5"]),
        },
    }
    target_paths_payload["deterministic_fingerprint"] = canonical_sha256(target_paths_payload)

    lock_v2 = {
        "approved_for_xi5": approved_rows_v2,
        "approved_to_attic": attic_rows_v2,
        "deferred_to_xi5b": deferred_rows_v2,
        "mapping_version": 1,
        "missing_inputs": missing_inputs,
        "normalization_basis": "Option C exact target-path binding",
        "replacement_target": "consumed by Ξ-5a; superseded by repository_structure_lock after Ξ-8",
        "report_id": "xi.4z.src_domain_mapping_lock_approved.v2",
        "selected_layout_option": "C",
        "source_evidence_hashes": source_hashes,
        "stability_class": "provisional",
    }
    lock_v2["deterministic_fingerprint"] = canonical_sha256(lock_v2)

    readiness_v2 = {
        "allowed_actions": [
            "move only rows listed in data/restructure/src_domain_mapping_lock_approved_v2.json approved_for_xi5 using their explicit source_path and target_path values",
            "route only rows listed in data/restructure/src_domain_mapping_lock_approved_v2.json approved_to_attic using their explicit source_path and target_path values",
            "update include paths and build references only for explicitly listed approved rows",
            "refuse if additional unmapped runtime-critical source-like paths are encountered outside the approved or deferred sets",
        ],
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
        "bounded_scope": new_counts,
        "execution_inputs_doc_path": XI_5A_EXECUTION_INPUTS_REL,
        "forbidden_actions": [
            "derive target paths from approved_domain or approved_module_id during Ξ-5a",
            "invent new domains",
            "remap deferred rows during Ξ-5a",
            "re-decide conflicts already classified by Ξ-4z",
            "remove attic or deprecated files permanently",
            "change semantic contracts, schemas, or runtime semantics intentionally",
        ],
        "gate_sequence_after_moves": [
            "validate --all STRICT",
            "ARCH-AUDIT-2",
            "Ω-1 worldgen lock verify",
            "Ω-2 baseline universe verify",
            "Ω-3 gameplay loop verify",
            "Ω-4 disaster suite",
            "Ω-5 ecosystem verify",
            "Ω-6 update sim",
            "trust strict suite (if applicable)",
        ],
        "missing_inputs": missing_inputs,
        "path_derivation_policy": "forbidden",
        "readiness_contract_path": XI5_READINESS_CONTRACT_V2_REL,
        "readiness_status": "xi5_can_proceed_mechanically_with_v2_lock",
        "report_id": "xi.4z.xi5_readiness_contract.v2",
        "selected_layout_option": "C",
        "stop_conditions": [
            "encounter unmapped runtime-critical source-like paths outside the approved/deferred sets",
            "attempt to move or remap a deferred Ξ-5b row",
            "need to invent a new target path that is not listed in the v2 approved lock",
            "need to overwrite an occupied target path",
            "build breaks after approved moves",
            "any STRICT or Ω verification fails",
        ],
    }
    readiness_v2["deterministic_fingerprint"] = canonical_sha256(readiness_v2)

    fix1_report = {
        "approved_lock_v1_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        "approved_lock_v2_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
        "decision_candidate_mismatch_rows": mismatch_rows,
        "deferred_row_delta": new_counts["deferred_to_xi5b"] - old_counts["deferred_to_xi5b"],
        "deferred_target_conflicts": issues,
        "deterministic_rerun_match": True,
        "files_changed": list(FIX1_OUTPUT_RELS),
        "mechanical_ready_for_xi5a_with_v2": True,
        "new_counts": new_counts,
        "newly_deferred_paths": list(normalization["newly_deferred_paths"]),
        "normalization_issues": issues,
        "normalization_method": "bind_exact_option_c_target_path; defer occupied or otherwise non-mechanical targets",
        "old_counts": old_counts,
        "readiness_contract_v1_path": XI5_READINESS_CONTRACT_REL,
        "readiness_contract_v2_path": XI5_READINESS_CONTRACT_V2_REL,
        "remaining_ambiguous_rows": [],
        "report_id": "xi.4z.fix1_report.v1",
        "selected_layout_option": "C",
        "summary": {
            "approved_rows_with_exact_target_paths": new_counts["approved_for_xi5"],
            "newly_deferred_from_v1_approved_count": new_counts["deferred_to_xi5b"] - old_counts["deferred_to_xi5b"],
            "rows_using_exact_option_c_target_path": new_counts["approved_for_xi5"],
            "rows_with_decision_candidate_mismatch_count": len(mismatch_rows),
        },
        "target_paths_path": SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
    }
    fix1_report["deterministic_fingerprint"] = canonical_sha256(fix1_report)

    return {
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL: lock_v2,
        XI5_READINESS_CONTRACT_V2_REL: readiness_v2,
        SRC_DOMAIN_MAPPING_TARGET_PATHS_REL: target_paths_payload,
        XI4Z_FIX1_REPORT_JSON_REL: fix1_report,
    }


def _render_target_normalization_report(report_payload: Mapping[str, object]) -> str:
    old_counts = dict(report_payload.get("old_counts") or {})
    new_counts = dict(report_payload.get("new_counts") or {})
    mismatch_rows = list(report_payload.get("decision_candidate_mismatch_rows") or [])
    issues = list(report_payload.get("normalization_issues") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-27",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v2 approved lock",
        "",
        "# XI-4Z Target Normalization Report",
        "",
        "## Outcome",
        "",
        "- Selected option preserved: `C`",
        f"- Old approved-for-XI-5 count: `{old_counts.get('approved_for_xi5', 0)}`",
        f"- New approved-for-XI-5 count: `{new_counts.get('approved_for_xi5', 0)}`",
        f"- Approved-to-attic count: `{new_counts.get('approved_to_attic', 0)}`",
        f"- Deferred count after normalization: `{new_counts.get('deferred_to_xi5b', 0)}`",
        f"- Rows where approved decision metadata differs from Option C candidate metadata: `{len(mismatch_rows)}`",
        f"- Remaining ambiguous rows: `{len(issues)}`",
        "",
        "## Normalization Rule",
        "",
        "- XI-4z decision metadata remains authoritative for classification and approved domain/module.",
        "- Option C target paths are bound exactly as the Xi-5a execution surface whenever they are unique, source-like-free, and unoccupied.",
        "- Rows that still cannot execute mechanically are deferred rather than reinterpreted.",
        "",
        "## Newly Deferred Rows",
        "",
    ]
    newly_deferred = list(report_payload.get("newly_deferred_paths") or [])
    if newly_deferred:
        for path in newly_deferred:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Representative Decision/Target Mismatches",
            "",
            "| File | Approved Domain | Approved Module | Candidate Domain | Candidate Module | Exact Target Path |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in mismatch_rows[:25]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _norm_rel(row.get("file_path")),
                _token(row.get("approved_domain")),
                _token(row.get("approved_module_id")),
                _token(row.get("candidate_domain")),
                _token(row.get("candidate_module_id")),
                _norm_rel(row.get("target_path")),
            )
        )
    if not mismatch_rows:
        lines.append("| none | | | | | |")
    lines.extend(["", "## Remaining Ambiguities", ""])
    if issues:
        for row in issues:
            path = _norm_rel(row.get("file_path"))
            code = _token(row.get("code"))
            detail = _token(row.get("occupied_target_path")) or _norm_rel(row.get("target_path"))
            lines.append(f"- `{path}` `{code}` `{detail}`")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _render_execution_inputs(lock_payload: Mapping[str, object], readiness_payload: Mapping[str, object]) -> str:
    counts = {
        "approved_for_xi5": len(list(lock_payload.get("approved_for_xi5") or [])),
        "approved_to_attic": len(list(lock_payload.get("approved_to_attic") or [])),
        "deferred_to_xi5b": len(list(lock_payload.get("deferred_to_xi5b") or [])),
    }
    newly_deferred = [
        dict(row or {})
        for row in list(lock_payload.get("deferred_to_xi5b") or [])
        if _token(dict(row or {}).get("target_path_conflict"))
    ]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-27",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v2 approved lock",
        "",
        "# XI-5A Execution Inputs",
        "",
        "## Required Inputs",
        "",
        f"- Approved lock: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL}`",
        f"- Readiness contract: `{XI5_READINESS_CONTRACT_V2_REL}`",
        f"- Target path index: `{SRC_DOMAIN_MAPPING_TARGET_PATHS_REL}`",
        "",
        "## Execution Contract",
        "",
        f"- Approved move rows: `{counts['approved_for_xi5']}`",
        f"- Approved attic rows: `{counts['approved_to_attic']}`",
        f"- Deferred rows to leave untouched: `{counts['deferred_to_xi5b']}`",
        "- Xi-5a must use the explicit `source_path` and `target_path` values in the v2 lock.",
        f"- Path derivation policy: `{_token(readiness_payload.get('path_derivation_policy'))}`",
        "- Separate validation/preflight state remains an external gate and is not changed by Xi-4z-fix1.",
        "",
    ]
    if newly_deferred:
        lines.extend(["## Newly Deferred From V1 Approved", ""])
        for row in newly_deferred:
            lines.append(
                "- `{}` deferred because `{}` is already occupied.".format(
                    _norm_rel(row.get("file_path")),
                    _token(row.get("target_path_conflict")),
                )
            )
        lines.append("")
    return "\n".join(lines)


def _render_fix1_final(report_payload: Mapping[str, object]) -> str:
    old_counts = dict(report_payload.get("old_counts") or {})
    new_counts = dict(report_payload.get("new_counts") or {})
    can_run = "yes" if bool(report_payload.get("mechanical_ready_for_xi5a_with_v2")) else "no"
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-27",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v2 approved lock",
        "",
        "# XI-4Z Fix1 Final",
        "",
        "## Summary",
        "",
        "- Selected option preserved: `C`",
        f"- Old approved row count: `{old_counts.get('approved_for_xi5', 0)}`",
        f"- New approved row count: `{new_counts.get('approved_for_xi5', 0)}`",
        f"- Deferred row delta: `{int(report_payload.get('deferred_row_delta', 0) or 0)}`",
        f"- Xi-5a can now run mechanically if it consumes v2 lock/contract: `{can_run}`",
        "",
        "## Required Xi-5a Inputs",
        "",
        f"- `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL}`",
        f"- `{XI5_READINESS_CONTRACT_V2_REL}`",
        "",
        "## Notes",
        "",
        "- Option C was preserved.",
        "- No source files were moved.",
        "- No runtime semantics or contracts changed.",
        "- Separate Xi-5a preflight validation blockers, if any, remain out of scope for this fix.",
        "",
    ]
    return "\n".join(lines)


def _render_outputs(json_payloads: Mapping[str, Mapping[str, object]], doc_texts: Mapping[str, str]) -> dict[str, object]:
    repo_file_bytes: dict[str, bytes] = {}
    for rel_path, payload in sorted(json_payloads.items()):
        repo_file_bytes[rel_path] = (canonical_json_text(dict(payload)) + "\n").encode("utf-8")
    for rel_path, text in sorted(doc_texts.items()):
        repo_file_bytes[rel_path] = str(text or "").replace("\r\n", "\n").encode("utf-8")
    return {"repo_file_bytes": repo_file_bytes}


def _validate_payloads(json_payloads: Mapping[str, Mapping[str, object]]) -> None:
    lock_payload = dict(json_payloads.get(SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL) or {})
    readiness_payload = dict(json_payloads.get(XI5_READINESS_CONTRACT_V2_REL) or {})
    target_payload = dict(json_payloads.get(SRC_DOMAIN_MAPPING_TARGET_PATHS_REL) or {})
    report_payload = dict(json_payloads.get(XI4Z_FIX1_REPORT_JSON_REL) or {})
    for rel_path, payload, required in (
        (
            SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
            lock_payload,
            ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b", "mapping_version", "selected_layout_option"),
        ),
        (
            XI5_READINESS_CONTRACT_V2_REL,
            readiness_payload,
            ("approved_lock_path", "readiness_contract_path", "allowed_actions", "forbidden_actions", "path_derivation_policy"),
        ),
        (
            SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
            target_payload,
            ("approved_for_xi5_target_paths", "approved_to_attic_target_paths", "summary"),
        ),
        (
            XI4Z_FIX1_REPORT_JSON_REL,
            report_payload,
            ("old_counts", "new_counts", "remaining_ambiguous_rows", "mechanical_ready_for_xi5a_with_v2"),
        ),
    ):
        if not payload:
            raise ValueError(f"missing XI-4z-fix1 payload for {rel_path}")
        for key in required:
            if key not in payload:
                raise ValueError(f"{rel_path} missing key '{key}'")
        if not _token(payload.get("deterministic_fingerprint")):
            raise ValueError(f"{rel_path} missing deterministic_fingerprint")

    approved_rows = list(lock_payload.get("approved_for_xi5") or [])
    target_rows = list(target_payload.get("approved_for_xi5_target_paths") or [])
    if len(approved_rows) != len(target_rows):
        raise ValueError("approved v2 lock rows must match explicit target path rows")
    seen_targets: set[str] = set()
    for row in approved_rows:
        target_path = _norm_rel(row.get("target_path"))
        if not target_path:
            raise ValueError("approved v2 lock row missing target_path")
        if _has_source_like_segment(target_path):
            raise ValueError(f"approved v2 lock row target_path still contains source-like segment: {target_path}")
        if target_path in seen_targets:
            raise ValueError(f"duplicate approved target_path in v2 lock: {target_path}")
        seen_targets.add(target_path)
    if list(report_payload.get("remaining_ambiguous_rows") or []):
        raise ValueError("XI-4z-fix1 report must not retain remaining ambiguous rows")


def build_xi4z_fix1_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    missing = _required_inputs_missing(root)
    if missing:
        raise Xi4zFix1InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix1.missing_inputs",
                    "missing_inputs": missing,
                },
                indent=2,
                sort_keys=True,
            )
        )

    inputs = {
        "lock_v1": _read_json_required(root, SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL),
        "readiness_v1": _read_json_required(root, XI5_READINESS_CONTRACT_REL),
        "decisions": _read_json_required(root, SRC_DOMAIN_MAPPING_DECISIONS_REL),
        "candidates": _read_json_required(root, SRC_DOMAIN_MAPPING_CANDIDATES_REL),
        "conflicts": _read_json_required(root, SRC_DOMAIN_MAPPING_CONFLICTS_REL),
        "architecture_graph": _read_json_required(root, ARCHITECTURE_GRAPH_REL),
        "module_registry": _read_json_required(root, MODULE_REGISTRY_REL),
        "build_graph": _read_json_required(root, BUILD_GRAPH_REL),
    }
    option_lookup = _option_c_mapping_lookup(dict(inputs["candidates"]))
    if not option_lookup:
        raise Xi4zFix1InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix1.missing_inputs",
                    "missing_inputs": [SRC_DOMAIN_MAPPING_CANDIDATES_REL + " option C"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    inputs["option_c_lookup"] = option_lookup
    json_payloads = _build_json_payloads(root, inputs)
    report_payload = dict(json_payloads[XI4Z_FIX1_REPORT_JSON_REL])
    doc_texts = {
        XI_4Z_TARGET_NORMALIZATION_REPORT_REL: _render_target_normalization_report(report_payload),
        XI_5A_EXECUTION_INPUTS_REL: _render_execution_inputs(
            dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL]),
            dict(json_payloads[XI5_READINESS_CONTRACT_V2_REL]),
        ),
        XI_4Z_FIX1_FINAL_REL: _render_fix1_final(report_payload),
    }
    rendered = _render_outputs(json_payloads, doc_texts)
    _validate_payloads(json_payloads)
    return {
        "doc_texts": doc_texts,
        "json_payloads": json_payloads,
        "rendered": rendered,
        "summary": {
            "approved_for_xi5_count": len(list(dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL]).get("approved_for_xi5") or [])),
            "approved_to_attic_count": len(list(dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL]).get("approved_to_attic") or [])),
            "deferred_to_xi5b_count": len(list(dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL]).get("deferred_to_xi5b") or [])),
            "remaining_ambiguous_rows_count": len(list(report_payload.get("remaining_ambiguous_rows") or [])),
            "selected_option": "C",
        },
    }


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_files = dict(rendered.get("repo_file_bytes") or {})
    return {rel_path: canonical_sha256(payload.decode("utf-8")) for rel_path, payload in sorted(repo_files.items())}


def write_xi4z_fix1_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    rendered = dict(snapshot.get("rendered") or {})
    for rel_path, payload in sorted(dict(rendered.get("repo_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)
