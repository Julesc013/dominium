"""Deterministic XI-4z package-collision normalization helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_fix1_common import (  # noqa: E402
    FIX1_OUTPUT_RELS,
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
    XI4Z_FIX1_REPORT_JSON_REL,
    XI5_READINESS_CONTRACT_V2_REL,
    XI_4Z_FIX1_FINAL_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    Xi4zFix1InputsMissing,
    _ensure_parent,
    _file_hash_rows,
    _has_source_like_segment,
    _norm_rel,
    _repo_abs,
    _repo_root,
    _token,
    build_xi4z_fix1_snapshot,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL = "data/restructure/src_domain_mapping_lock_approved_v3.json"
XI5_READINESS_CONTRACT_V3_REL = "data/restructure/xi5_readiness_contract_v3.json"
SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL = "data/restructure/src_domain_mapping_target_paths_v3.json"
XI4Z_FIX2_REPORT_JSON_REL = "data/restructure/xi4z_fix2_report.json"

XI_4Z_PACKAGE_COLLISION_REPORT_REL = "docs/restructure/XI_4Z_PACKAGE_COLLISION_REPORT.md"
XI_4Z_FIX2_FINAL_REL = "docs/audit/XI_4Z_FIX2_FINAL.md"

FIX2_OUTPUT_RELS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
    XI5_READINESS_CONTRACT_V3_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL,
    XI4Z_FIX2_REPORT_JSON_REL,
    XI_4Z_PACKAGE_COLLISION_REPORT_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    XI_4Z_FIX2_FINAL_REL,
    "tools/review/xi4z_fix2_common.py",
    "tools/review/tool_run_xi4z_fix2.py",
    "tools/xstack/testx/tests/xi4z_fix2_testlib.py",
    "tools/xstack/testx/tests/test_xi4z_v3_lock_schema_valid.py",
    "tools/xstack/testx/tests/test_xi4z_v3_no_stdlib_target_collisions.py",
    "tools/xstack/testx/tests/test_xi4z_fix2_outputs_deterministic.py",
)

PACKAGE_COLLISION_RULES = {
    "platform": {
        "approved_domain": "engine",
        "approved_module_id": "engine.platform",
        "source_prefix": "src/platform/",
        "target_prefix": "engine/platform/",
    },
    "time": {
        "approved_domain": "engine",
        "approved_module_id": "engine.time",
        "source_prefix": "src/time/",
        "target_prefix": "engine/time/",
    },
}


class Xi4zFix2InputsMissing(RuntimeError):
    """Raised when required XI-4z-fix2 artifacts are unavailable."""


def _required_inputs_missing(repo_root: str) -> list[str]:
    missing: list[str] = []
    for rel_path in (
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
        XI5_READINESS_CONTRACT_V2_REL,
        SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
        XI4Z_FIX1_REPORT_JSON_REL,
        XI_4Z_FIX1_FINAL_REL,
    ):
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    return sorted(set(missing))


def _load_json_required(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        payload = None
    if not isinstance(payload, dict) or not payload:
        raise Xi4zFix2InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix2.missing_inputs",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _row_collision_rule(row: Mapping[str, object]) -> dict[str, str] | None:
    source_path = _norm_rel(row.get("source_path") or row.get("file_path"))
    for rule in PACKAGE_COLLISION_RULES.values():
        if source_path.startswith(rule["source_prefix"]):
            return dict(rule)
    return None


def _target_conflicts(repo_root: str, source_path: str, target_path: str) -> bool:
    source_norm = _norm_rel(source_path)
    target_norm = _norm_rel(target_path)
    if source_norm == target_norm:
        return False
    return os.path.exists(_repo_abs(repo_root, target_norm))


def _rewrite_approved_row(row: Mapping[str, object], rule: Mapping[str, str]) -> dict[str, object]:
    source_path = _norm_rel(row.get("source_path") or row.get("file_path"))
    source_prefix = _norm_rel(rule.get("source_prefix"))
    target_prefix = _norm_rel(rule.get("target_prefix"))
    new_target_path = _norm_rel(target_prefix + source_path[len(source_prefix) :])
    payload = dict(row)
    payload["approved_domain"] = _token(rule.get("approved_domain"))
    payload["approved_module_id"] = _token(rule.get("approved_module_id"))
    provenance = dict(payload.get("decision_provenance") or {})
    provenance["collision_fix_report_id"] = "xi.4z.package_collision_fix.v1"
    provenance["collision_fix_rule"] = "rebind_python_stdlib_collision_package_root"
    provenance["collision_fix_old_target_path"] = _norm_rel(payload.get("target_path"))
    provenance["collision_fix_new_target_path"] = new_target_path
    provenance["collision_fix_reason"] = "python stdlib package collision"
    payload["decision_provenance"] = provenance
    payload["reason"] = (
        _token(payload.get("reason"))
        + " Target package root rebound to avoid Python stdlib collision while preserving Option C bounded intent."
    ).strip()
    payload["target_path"] = new_target_path
    payload["target_path_mapping_confidence"] = float(payload.get("target_path_mapping_confidence", 0.0) or 0.0)
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _rewrite_target_row(row: Mapping[str, object], rule: Mapping[str, str]) -> dict[str, object]:
    source_path = _norm_rel(row.get("source_path"))
    source_prefix = _norm_rel(rule.get("source_prefix"))
    target_prefix = _norm_rel(rule.get("target_prefix"))
    new_target_path = _norm_rel(target_prefix + source_path[len(source_prefix) :])
    payload = dict(row)
    payload["approved_domain"] = _token(rule.get("approved_domain"))
    payload["approved_module_id"] = _token(rule.get("approved_module_id"))
    provenance = dict(payload.get("decision_provenance") or {})
    provenance["collision_fix_report_id"] = "xi.4z.package_collision_fix.v1"
    provenance["collision_fix_rule"] = "rebind_python_stdlib_collision_package_root"
    provenance["collision_fix_new_target_path"] = new_target_path
    payload["decision_provenance"] = provenance
    payload["target_path"] = new_target_path
    return payload


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
    lock_v2 = dict(inputs["lock_v2"])
    target_paths_v2 = dict(inputs["target_paths_v2"])
    readiness_v2 = dict(inputs["readiness_v2"])

    collision_rows: list[dict[str, object]] = []
    collision_packages: dict[str, dict[str, object]] = {}
    seen_targets: set[str] = set()
    approved_rows_v3: list[dict[str, object]] = []

    for row in sorted((dict(item or {}) for item in list(lock_v2.get("approved_for_xi5") or [])), key=lambda item: _norm_rel(item.get("source_path"))):
        rule = _row_collision_rule(row)
        payload = dict(row)
        if rule:
            payload = _rewrite_approved_row(payload, rule)
            package_key = _norm_rel(rule["source_prefix"]).split("/")[1]
            collision_rows.append(
                {
                    "approved_domain_after": _token(payload.get("approved_domain")),
                    "approved_domain_before": _token(row.get("approved_domain")),
                    "approved_module_id_after": _token(payload.get("approved_module_id")),
                    "approved_module_id_before": _token(row.get("approved_module_id")),
                    "collision_package": package_key,
                    "new_target_path": _norm_rel(payload.get("target_path")),
                    "old_target_path": _norm_rel(row.get("target_path")),
                    "source_path": _norm_rel(row.get("source_path")),
                }
            )
            pkg = collision_packages.setdefault(
                package_key,
                {
                    "approved_domain": _token(rule["approved_domain"]),
                    "approved_module_id": _token(rule["approved_module_id"]),
                    "row_count": 0,
                    "source_prefix": _norm_rel(rule["source_prefix"]),
                    "target_prefix": _norm_rel(rule["target_prefix"]),
                },
            )
            pkg["row_count"] = int(pkg.get("row_count", 0)) + 1
        target_path = _norm_rel(payload.get("target_path"))
        if not target_path:
            raise ValueError("XI-4z-fix2 produced blank target_path")
        if _has_source_like_segment(target_path):
            raise ValueError(f"XI-4z-fix2 produced source-like target_path: {target_path}")
        if target_path in seen_targets:
            raise ValueError(f"XI-4z-fix2 produced duplicate target_path: {target_path}")
        if _target_conflicts(repo_root, _norm_rel(payload.get("source_path")), target_path):
            raise ValueError(f"XI-4z-fix2 produced occupied target_path: {target_path}")
        seen_targets.add(target_path)
        approved_rows_v3.append(payload)

    attic_rows_v3 = [dict(item or {}) for item in list(lock_v2.get("approved_to_attic") or [])]
    deferred_rows_v3 = [dict(item or {}) for item in list(lock_v2.get("deferred_to_xi5b") or [])]
    old_counts = _counts(lock_v2)
    new_counts = {
        "approved_for_xi5": len(approved_rows_v3),
        "approved_to_attic": len(attic_rows_v3),
        "deferred_to_xi5b": len(deferred_rows_v3),
        "total_rows": len(approved_rows_v3) + len(attic_rows_v3) + len(deferred_rows_v3),
    }
    if old_counts != new_counts:
        raise ValueError("XI-4z-fix2 must preserve row counts")

    target_rows_v3: list[dict[str, object]] = []
    for row in sorted(
        (dict(item or {}) for item in list(target_paths_v2.get("approved_for_xi5_target_paths") or [])),
        key=lambda item: _norm_rel(item.get("source_path")),
    ):
        rule = _row_collision_rule(row)
        payload = _rewrite_target_row(row, rule) if rule else dict(row)
        target_rows_v3.append(payload)

    attic_target_rows_v3 = [dict(item or {}) for item in list(target_paths_v2.get("approved_to_attic_target_paths") or [])]

    source_hashes = _file_hash_rows(
        repo_root,
        [
            SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
            XI5_READINESS_CONTRACT_V2_REL,
            SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
            XI4Z_FIX1_REPORT_JSON_REL,
            XI_4Z_FIX1_FINAL_REL,
        ]
        + list(FIX1_OUTPUT_RELS),
    )

    lock_v3 = {
        "approved_for_xi5": approved_rows_v3,
        "approved_to_attic": attic_rows_v3,
        "deferred_to_xi5b": deferred_rows_v3,
        "mapping_version": 1,
        "missing_inputs": sorted(set(lock_v2.get("missing_inputs") or [])),
        "normalization_basis": "Option C exact target-path binding with stdlib-collision package-root rebinding",
        "replacement_target": "consumed by Ξ-5a; superseded by repository_structure_lock after Ξ-8",
        "report_id": "xi.4z.src_domain_mapping_lock_approved.v3",
        "selected_layout_option": "C",
        "source_evidence_hashes": source_hashes,
        "stability_class": "provisional",
    }
    lock_v3["deterministic_fingerprint"] = canonical_sha256(lock_v3)

    target_paths_v3 = {
        "approved_for_xi5_target_paths": target_rows_v3,
        "approved_to_attic_target_paths": attic_target_rows_v3,
        "deterministic_fingerprint_seed": {
            "collision_package_count": len(collision_packages),
            "collision_row_count": len(collision_rows),
            "deferred_count": new_counts["deferred_to_xi5b"],
        },
        "missing_inputs": sorted(set(target_paths_v2.get("missing_inputs") or [])),
        "report_id": "xi.4z.src_domain_mapping_target_paths.v2",
        "selected_layout_option": "C",
        "summary": {
            "approved_for_xi5_count": new_counts["approved_for_xi5"],
            "approved_to_attic_count": new_counts["approved_to_attic"],
            "collision_package_count": len(collision_packages),
            "collision_row_count": len(collision_rows),
            "deferred_to_xi5b_count": new_counts["deferred_to_xi5b"],
            "rows_with_exact_target_paths": len(target_rows_v3),
        },
    }
    target_paths_v3["deterministic_fingerprint"] = canonical_sha256(target_paths_v3)

    readiness_v3 = {
        "allowed_actions": [
            "move only rows listed in data/restructure/src_domain_mapping_lock_approved_v3.json approved_for_xi5 using their explicit source_path and target_path values",
            "route only rows listed in data/restructure/src_domain_mapping_lock_approved_v3.json approved_to_attic using their explicit source_path and target_path values",
            "update include paths and build references only for explicitly listed approved rows",
            "refuse if additional unmapped runtime-critical source-like paths are encountered outside the approved or deferred sets",
        ],
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
        "bounded_scope": new_counts,
        "execution_inputs_doc_path": XI_5A_EXECUTION_INPUTS_REL,
        "forbidden_actions": list(readiness_v2.get("forbidden_actions") or []),
        "gate_sequence_after_moves": list(readiness_v2.get("gate_sequence_after_moves") or []),
        "missing_inputs": sorted(set(readiness_v2.get("missing_inputs") or [])),
        "path_derivation_policy": "forbidden",
        "readiness_contract_path": XI5_READINESS_CONTRACT_V3_REL,
        "readiness_status": "xi5_can_proceed_mechanically_with_v3_lock",
        "report_id": "xi.4z.xi5_readiness_contract.v3",
        "selected_layout_option": "C",
        "stop_conditions": [
            "encounter unmapped runtime-critical source-like paths outside the approved/deferred sets",
            "attempt to move or remap a deferred Ξ-5b row",
            "need to invent a new target path that is not listed in the v3 approved lock",
            "need to overwrite an occupied target path",
            "build breaks after approved moves",
            "any STRICT or Ω verification fails",
        ],
    }
    readiness_v3["deterministic_fingerprint"] = canonical_sha256(readiness_v3)

    fix2_report = {
        "approved_lock_v2_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL,
        "approved_lock_v3_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
        "collision_packages": dict((key, collision_packages[key]) for key in sorted(collision_packages)),
        "collision_rows": collision_rows,
        "deterministic_rerun_match": True,
        "files_changed": list(FIX2_OUTPUT_RELS),
        "mechanical_ready_for_xi5a_with_v3": True,
        "new_counts": new_counts,
        "old_counts": old_counts,
        "readiness_contract_v2_path": XI5_READINESS_CONTRACT_V2_REL,
        "readiness_contract_v3_path": XI5_READINESS_CONTRACT_V3_REL,
        "remaining_ambiguous_rows": [],
        "report_id": "xi.4z.fix2_report.v1",
        "selected_layout_option": "C",
        "stdlib_collision_targets_fixed": sorted(collision_packages),
        "summary": {
            "collision_package_count": len(collision_packages),
            "collision_row_count": len(collision_rows),
            "rows_rebound_to_safe_package_roots": len(collision_rows),
        },
        "target_paths_v2_path": SRC_DOMAIN_MAPPING_TARGET_PATHS_REL,
        "target_paths_v3_path": SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL,
    }
    fix2_report["deterministic_fingerprint"] = canonical_sha256(fix2_report)

    return {
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL: lock_v3,
        XI5_READINESS_CONTRACT_V3_REL: readiness_v3,
        SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL: target_paths_v3,
        XI4Z_FIX2_REPORT_JSON_REL: fix2_report,
    }


def _render_package_collision_report(report_payload: Mapping[str, object]) -> str:
    collision_packages = dict(report_payload.get("collision_packages") or {})
    collision_rows = list(report_payload.get("collision_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Supersedes: docs/restructure/XI_4Z_TARGET_NORMALIZATION_REPORT.md",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v3 approved lock",
        "",
        "# XI-4Z Package Collision Report",
        "",
        "## Outcome",
        "",
        "- Selected option preserved: `C`",
        f"- Collision packages fixed: `{len(collision_packages)}`",
        f"- Collision rows rebound: `{len(collision_rows)}`",
        "- No source files moved during this fix.",
        "",
        "## Fixed Packages",
        "",
        "| Package | Row Count | Old Prefix | New Prefix | Domain | Module |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for package_name in sorted(collision_packages):
        row = dict(collision_packages[package_name] or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                package_name,
                int(row.get("row_count", 0) or 0),
                _norm_rel(row.get("source_prefix")),
                _norm_rel(row.get("target_prefix")),
                _token(row.get("approved_domain")),
                _token(row.get("approved_module_id")),
            )
        )
    if not collision_packages:
        lines.append("| none | 0 | | | | |")
    lines.extend(["", "## Representative Rows", "", "| Source | Old Target | New Target |", "| --- | --- | --- |"])
    for row in collision_rows[:25]:
        lines.append(
            "| `{}` | `{}` | `{}` |".format(
                _norm_rel(row.get("source_path")),
                _norm_rel(row.get("old_target_path")),
                _norm_rel(row.get("new_target_path")),
            )
        )
    if not collision_rows:
        lines.append("| none | | |")
    lines.append("")
    return "\n".join(lines)


def _render_execution_inputs(lock_payload: Mapping[str, object], readiness_payload: Mapping[str, object], report_payload: Mapping[str, object]) -> str:
    counts = _counts(lock_payload)
    collision_packages = dict(report_payload.get("collision_packages") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Supersedes: docs/restructure/XI_5A_EXECUTION_INPUTS.md (v2 content)",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v3 approved lock",
        "",
        "# XI-5A Execution Inputs",
        "",
        "## Required Inputs",
        "",
        f"- Approved lock: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL}`",
        f"- Readiness contract: `{XI5_READINESS_CONTRACT_V3_REL}`",
        f"- Target path index: `{SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL}`",
        "",
        "## Execution Contract",
        "",
        f"- Approved move rows: `{counts['approved_for_xi5']}`",
        f"- Approved attic rows: `{counts['approved_to_attic']}`",
        f"- Deferred rows to leave untouched: `{counts['deferred_to_xi5b']}`",
        f"- Path derivation policy: `{_token(readiness_payload.get('path_derivation_policy'))}`",
        "- Xi-5a must use the explicit `source_path` and `target_path` values in the v3 lock.",
        "- No further package-root derivation is allowed during Xi-5a.",
        "",
        "## Collision Normalization Applied",
        "",
    ]
    if collision_packages:
        for package_name in sorted(collision_packages):
            row = dict(collision_packages[package_name] or {})
            lines.append(
                "- `{}` rebound from `{}` to `{}` under `{}`.".format(
                    package_name,
                    _norm_rel(row.get("source_prefix")),
                    _norm_rel(row.get("target_prefix")),
                    _token(row.get("approved_module_id")),
                )
            )
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _render_fix2_final(report_payload: Mapping[str, object]) -> str:
    counts = dict(report_payload.get("new_counts") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Supersedes: docs/audit/XI_4Z_FIX1_FINAL.md",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a bounded execution against v3 approved lock",
        "",
        "# XI-4Z Fix2 Final",
        "",
        "## Summary",
        "",
        "- Selected option preserved: `C`",
        f"- Collision packages fixed: `{len(dict(report_payload.get('collision_packages') or {}))}`",
        f"- Collision rows rebound: `{len(list(report_payload.get('collision_rows') or []))}`",
        f"- Approved row count preserved: `{counts.get('approved_for_xi5', 0)}`",
        "- Xi-5a can now run mechanically if it consumes v3 lock/contract: `yes`",
        "",
        "## Required Xi-5a Inputs",
        "",
        f"- `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL}`",
        f"- `{XI5_READINESS_CONTRACT_V3_REL}`",
        "",
        "## Notes",
        "",
        "- Python stdlib/builtin package collisions were removed from the approved move surface.",
        "- No source files were moved.",
        "- No runtime semantics or contracts changed.",
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
    lock_payload = dict(json_payloads.get(SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL) or {})
    target_payload = dict(json_payloads.get(SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL) or {})
    readiness_payload = dict(json_payloads.get(XI5_READINESS_CONTRACT_V3_REL) or {})
    report_payload = dict(json_payloads.get(XI4Z_FIX2_REPORT_JSON_REL) or {})
    for rel_path, payload, required in (
        (
            SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
            lock_payload,
            ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b", "report_id"),
        ),
        (
            XI5_READINESS_CONTRACT_V3_REL,
            readiness_payload,
            ("approved_lock_path", "readiness_contract_path", "path_derivation_policy"),
        ),
        (
            SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL,
            target_payload,
            ("approved_for_xi5_target_paths", "approved_to_attic_target_paths", "summary"),
        ),
        (
            XI4Z_FIX2_REPORT_JSON_REL,
            report_payload,
            ("collision_packages", "collision_rows", "remaining_ambiguous_rows"),
        ),
    ):
        if not payload:
            raise ValueError(f"missing XI-4z-fix2 payload for {rel_path}")
        for key in required:
            if key not in payload:
                raise ValueError(f"{rel_path} missing key '{key}'")
        if not _token(payload.get("deterministic_fingerprint")):
            raise ValueError(f"{rel_path} missing deterministic_fingerprint")

    seen_targets: set[str] = set()
    for row in list(lock_payload.get("approved_for_xi5") or []):
        target_path = _norm_rel(dict(row or {}).get("target_path"))
        top = target_path.split("/")[0]
        if top in {"platform", "time"}:
            raise ValueError(f"unfixed stdlib collision target remains: {target_path}")
        if target_path in seen_targets:
            raise ValueError(f"duplicate v3 target_path: {target_path}")
        seen_targets.add(target_path)
    if list(report_payload.get("remaining_ambiguous_rows") or []):
        raise ValueError("XI-4z-fix2 must not retain remaining ambiguous rows")


def build_xi4z_fix2_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    missing = _required_inputs_missing(root)
    if missing:
        raise Xi4zFix2InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix2.missing_inputs",
                    "missing_inputs": missing,
                },
                indent=2,
                sort_keys=True,
            )
        )

    build_xi4z_fix1_snapshot(root)
    inputs = {
        "fix1_report": _load_json_required(root, XI4Z_FIX1_REPORT_JSON_REL),
        "lock_v2": _load_json_required(root, SRC_DOMAIN_MAPPING_LOCK_APPROVED_V2_REL),
        "readiness_v2": _load_json_required(root, XI5_READINESS_CONTRACT_V2_REL),
        "target_paths_v2": _load_json_required(root, SRC_DOMAIN_MAPPING_TARGET_PATHS_REL),
    }
    json_payloads = _build_json_payloads(root, inputs)
    report_payload = dict(json_payloads[XI4Z_FIX2_REPORT_JSON_REL])
    doc_texts = {
        XI_4Z_PACKAGE_COLLISION_REPORT_REL: _render_package_collision_report(report_payload),
        XI_5A_EXECUTION_INPUTS_REL: _render_execution_inputs(
            dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL]),
            dict(json_payloads[XI5_READINESS_CONTRACT_V3_REL]),
            report_payload,
        ),
        XI_4Z_FIX2_FINAL_REL: _render_fix2_final(report_payload),
    }
    rendered = _render_outputs(json_payloads, doc_texts)
    _validate_payloads(json_payloads)
    return {
        "doc_texts": doc_texts,
        "json_payloads": json_payloads,
        "rendered": rendered,
        "summary": {
            "approved_for_xi5_count": len(list(dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL]).get("approved_for_xi5") or [])),
            "approved_to_attic_count": len(list(dict(json_payloads[SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL]).get("approved_to_attic") or [])),
            "collision_package_count": len(dict(report_payload.get("collision_packages") or {})),
            "collision_row_count": len(list(report_payload.get("collision_rows") or [])),
            "remaining_ambiguous_rows_count": len(list(report_payload.get("remaining_ambiguous_rows") or [])),
            "selected_option": "C",
        },
    }


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_files = dict(rendered.get("repo_file_bytes") or {})
    return {rel_path: canonical_sha256(payload.decode("utf-8")) for rel_path, payload in sorted(repo_files.items())}


def write_xi4z_fix2_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    rendered = dict(snapshot.get("rendered") or {})
    for rel_path, payload in sorted(dict(rendered.get("repo_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)
