"""Deterministic XI-4z shadow-root execution-surface helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_fix2_common import (  # noqa: E402
    FIX2_OUTPUT_RELS,
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL,
    XI4Z_FIX2_REPORT_JSON_REL,
    XI5_READINESS_CONTRACT_V3_REL,
    XI_4Z_FIX2_FINAL_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    _ensure_parent,
    _file_hash_rows,
    _norm_rel,
    _repo_abs,
    _repo_root,
    _token,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL = "data/restructure/src_domain_mapping_lock_approved_v4.json"
XI5_READINESS_CONTRACT_V4_REL = "data/restructure/xi5_readiness_contract_v4.json"
SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL = "data/restructure/src_domain_mapping_target_paths_v4.json"
XI4Z_FIX3_REPORT_JSON_REL = "data/restructure/xi4z_fix3_report.json"

XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT_REL = "docs/restructure/XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT.md"
XI_4Z_FIX3_FINAL_REL = "docs/audit/XI_4Z_FIX3_FINAL.md"

FIX3_OUTPUT_RELS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
    XI5_READINESS_CONTRACT_V4_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL,
    XI4Z_FIX3_REPORT_JSON_REL,
    XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    XI_4Z_FIX3_FINAL_REL,
    "tools/review/xi4z_fix3_common.py",
    "tools/review/tool_run_xi4z_fix3.py",
    "tools/xstack/testx/tests/xi4z_fix3_testlib.py",
    "tools/xstack/testx/tests/test_xi4z_v4_lock_schema_valid.py",
    "tools/xstack/testx/tests/test_xi4z_v4_only_dangerous_shadow_roots_approved.py",
    "tools/xstack/testx/tests/test_xi4z_v4_missing_package_initializers_promoted.py",
    "tools/xstack/testx/tests/test_xi4z_fix3_outputs_deterministic.py",
)

DANGEROUS_SHADOW_PREFIXES = ("app/src/", "src/")
MISSING_PACKAGE_INIT_TARGETS = {
    "client/interaction/__init__.py": "client/interaction/__init__.py",
    "lib/store/__init__.py": "lib/store/__init__.py",
}
RESERVED_PACKAGE_TARGETS = ("engine/platform/", "engine/time/")


class Xi4zFix3InputsMissing(RuntimeError):
    """Raised when required XI-4z-fix3 artifacts are unavailable."""


def _required_inputs_missing(repo_root: str) -> list[str]:
    missing: list[str] = []
    for rel_path in (
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL,
        XI5_READINESS_CONTRACT_V3_REL,
        SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL,
        XI4Z_FIX2_REPORT_JSON_REL,
        XI_4Z_FIX2_FINAL_REL,
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
        raise Xi4zFix3InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix3.missing_inputs",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
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


def _source_path(row: Mapping[str, object]) -> str:
    return _norm_rel(row.get("source_path") or row.get("file_path"))


def _is_dangerous_shadow_row(row: Mapping[str, object]) -> bool:
    source_path = _source_path(row)
    return any(source_path.startswith(prefix) for prefix in DANGEROUS_SHADOW_PREFIXES)


def _phase_class(source_path: str) -> str:
    token = _norm_rel(source_path)
    if any(token.startswith(prefix) for prefix in DANGEROUS_SHADOW_PREFIXES):
        return "dangerous_shadow_root"
    if token.startswith("packs/source/"):
        return "content_source_root"
    if token.startswith("legacy/source/") or "/source/" in token:
        return "legacy_source_pocket"
    if token.startswith("libs/") and "/src/" in token:
        return "component_local_src"
    if token.startswith("tools/") and "/src/" in token:
        return "component_local_src"
    return "later_phase"


def _rephase_deferred_row(row: Mapping[str, object]) -> dict[str, object]:
    payload = dict(row)
    source_path = _source_path(payload)
    payload["additional_evidence_required"] = _token(payload.get("additional_evidence_required")) or "execute in later Xi-5 phase after dangerous shadow roots are eliminated"
    payload["blocker"] = _token(payload.get("blocker")) or "Moved out of Xi-5a-v3 to keep the pass limited to dangerous shadow roots only."
    payload["current_root"] = _token(payload.get("current_root")) or source_path.split("/", 1)[0]
    payload["decision_class"] = "deferred_to_xi5b"
    payload["deferred_phase_class"] = _phase_class(source_path)
    payload["safe_to_keep_in_place_temporarily"] = True
    return payload


def _promote_missing_init_row(source_path: str, target_path: str, sibling_row: Mapping[str, object], original_deferred_row: Mapping[str, object]) -> dict[str, object]:
    payload = dict(sibling_row)
    payload["source_path"] = _norm_rel(source_path)
    payload["file_path"] = _norm_rel(source_path)
    payload["target_path"] = _norm_rel(target_path)
    payload["decision_class"] = "approved_for_xi5"
    payload["reason"] = (
        "Package initializer promoted from deferred_to_xi5b because sibling files in the same approved target package already execute in Xi-5a-v3 "
        "and the initializer path is mechanically implied without introducing a new target."
    )
    provenance = dict(payload.get("decision_provenance") or {})
    provenance["fix3_report_id"] = "xi.4z.shadow_root_fix.v1"
    provenance["fix3_rule"] = "promote_missing_package_initializer_to_match_approved_sibling_module"
    provenance["fix3_original_decision_class"] = "deferred_to_xi5b"
    provenance["fix3_original_reason"] = _token(original_deferred_row.get("reason"))
    payload["decision_provenance"] = provenance
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _build_json_payloads(repo_root: str, inputs: Mapping[str, object]) -> dict[str, dict[str, object]]:
    lock_v3 = dict(inputs["lock_v3"])
    target_paths_v3 = dict(inputs["target_paths_v3"])
    readiness_v3 = dict(inputs["readiness_v3"])
    fix2_report = dict(inputs["fix2_report"])

    approved_rows_v3 = [dict(item or {}) for item in list(lock_v3.get("approved_for_xi5") or [])]
    attic_rows_v3 = [dict(item or {}) for item in list(lock_v3.get("approved_to_attic") or [])]
    deferred_rows_v3 = [dict(item or {}) for item in list(lock_v3.get("deferred_to_xi5b") or [])]
    approved_target_rows_v3 = [dict(item or {}) for item in list(target_paths_v3.get("approved_for_xi5_target_paths") or [])]
    attic_target_rows_v3 = [dict(item or {}) for item in list(target_paths_v3.get("approved_to_attic_target_paths") or [])]

    sibling_rows_by_dir: dict[str, dict[str, object]] = {}
    for row in approved_rows_v3:
        sibling_rows_by_dir.setdefault(os.path.dirname(_source_path(row)), dict(row))

    deferred_by_source = {_source_path(row): dict(row) for row in deferred_rows_v3}
    promoted_rows: list[dict[str, object]] = []
    promoted_sources = set()
    for source_path, target_path in sorted(MISSING_PACKAGE_INIT_TARGETS.items()):
        deferred_row = deferred_by_source.get(source_path)
        sibling_row = sibling_rows_by_dir.get(os.path.dirname(source_path))
        if deferred_row and sibling_row:
            promoted_rows.append(_promote_missing_init_row(source_path, target_path, sibling_row, deferred_row))
            promoted_sources.add(source_path)

    approved_rows_v4 = [
        dict(row)
        for row in sorted(
            [row for row in approved_rows_v3 if _is_dangerous_shadow_row(row)] + promoted_rows,
            key=lambda row: _source_path(row),
        )
    ]
    approved_sources_v4 = {_source_path(row) for row in approved_rows_v4}

    attic_rows_v4 = [
        dict(row)
        for row in sorted((row for row in attic_rows_v3 if _is_dangerous_shadow_row(row)), key=lambda row: _source_path(row))
    ]
    attic_sources_v4 = {_source_path(row) for row in attic_rows_v4}

    deferred_rows_v4 = [
        _rephase_deferred_row(row)
        for row in deferred_rows_v3
        if _source_path(row) not in promoted_sources
    ]
    deferred_rows_v4.extend(
        _rephase_deferred_row(row)
        for row in approved_rows_v3
        if _source_path(row) not in approved_sources_v4
    )
    deferred_rows_v4.extend(
        _rephase_deferred_row(row)
        for row in attic_rows_v3
        if _source_path(row) not in attic_sources_v4
    )
    deferred_rows_v4 = sorted(deferred_rows_v4, key=lambda row: (_phase_class(_source_path(row)), _source_path(row)))

    approved_target_rows_v4 = [
        dict(row)
        for row in sorted((row for row in approved_target_rows_v3 if _source_path(row) in approved_sources_v4), key=lambda row: _source_path(row))
    ]
    for promoted in promoted_rows:
        approved_target_rows_v4.append(
            {
                "approved_domain": _token(promoted.get("approved_domain")),
                "approved_module_id": _token(promoted.get("approved_module_id")),
                "decision_provenance": dict(promoted.get("decision_provenance") or {}),
                "source_path": _source_path(promoted),
                "target_path": _norm_rel(promoted.get("target_path")),
            }
        )
    approved_target_rows_v4 = sorted(approved_target_rows_v4, key=lambda row: _source_path(row))
    attic_target_rows_v4 = [
        dict(row)
        for row in sorted((row for row in attic_target_rows_v3 if _source_path(row) in attic_sources_v4), key=lambda row: _source_path(row))
    ]

    collision_targets_fixed = sorted(set(fix2_report.get("stdlib_collision_targets_fixed") or []))
    inherited_reserved_target_paths = sorted(
        {
            _norm_rel(row.get("target_path"))
            for row in approved_rows_v4
            if any(_norm_rel(row.get("target_path")).startswith(prefix) for prefix in RESERVED_PACKAGE_TARGETS)
        }
    )
    phase_counts: dict[str, int] = {}
    for row in deferred_rows_v4:
        phase = _token(row.get("deferred_phase_class"))
        phase_counts[phase] = int(phase_counts.get(phase, 0)) + 1

    lock_v4 = {
        "approved_for_xi5": approved_rows_v4,
        "approved_to_attic": attic_rows_v4,
        "deferred_to_xi5b": deferred_rows_v4,
        "dangerous_shadow_roots": ["app/src", "src"],
        "deterministic_fingerprint": "",
        "mapping_version": int(lock_v3.get("mapping_version", 1) or 1),
        "normalization_basis": "Dangerous shadow-root execution subset of v3 lock with reserved-package protections inherited from Xi-4z-fix2",
        "readiness_phase": "xi5a_v3_dangerous_shadow_roots",
        "report_id": "xi.4z.src_domain_mapping_lock_approved.v4",
        "selected_layout_option": _token(lock_v3.get("selected_layout_option")) or "C",
        "source_evidence_hashes": _file_hash_rows(repo_root, FIX2_OUTPUT_RELS),
        "stability_class": "provisional",
    }
    lock_v4["deterministic_fingerprint"] = canonical_sha256(dict(lock_v4, deterministic_fingerprint=""))

    target_paths_v4 = {
        "approved_for_xi5_target_paths": approved_target_rows_v4,
        "approved_to_attic_target_paths": attic_target_rows_v4,
        "dangerous_shadow_roots": ["app/src", "src"],
        "deterministic_fingerprint": "",
        "report_id": "xi.4z.src_domain_mapping_target_paths.v4",
        "selected_layout_option": _token(lock_v4.get("selected_layout_option")),
        "stability_class": "provisional",
    }
    target_paths_v4["deterministic_fingerprint"] = canonical_sha256(dict(target_paths_v4, deterministic_fingerprint=""))

    counts = _counts(lock_v4)
    readiness_v4 = {
        "allowed_actions": [
            "move only rows listed in data/restructure/src_domain_mapping_lock_approved_v4.json approved_for_xi5 using their explicit source_path and target_path values",
            "route only rows listed in data/restructure/src_domain_mapping_lock_approved_v4.json approved_to_attic using their explicit source_path and target_path values",
            "update include paths and build references only for explicitly listed dangerous shadow-root rows",
            "refuse if additional unmapped runtime-critical source-like paths are encountered inside top-level src/ or app/src/",
        ],
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        "bounded_scope": {
            "approved_for_xi5": int(counts["approved_for_xi5"]),
            "approved_to_attic": int(counts["approved_to_attic"]),
            "deferred_to_xi5b": int(counts["deferred_to_xi5b"]),
            "total_rows": int(counts["total_rows"]),
        },
        "dangerous_shadow_roots": ["app/src", "src"],
        "deferred_follow_on_phases": {
            "component_local_src": "xi5c",
            "content_source_root": "xi5b",
            "dangerous_shadow_root": "xi5a_v3",
            "later_phase": "xi5b",
            "legacy_source_pocket": "xi5b",
        },
        "deterministic_fingerprint": "",
        "execution_inputs_doc_path": XI_5A_EXECUTION_INPUTS_REL,
        "forbidden_actions": [
            "consume superseded v1, v2, or v3 Xi-5 readiness contracts for dangerous shadow execution",
            "derive target paths from approved_domain or approved_module_id during Xi-5a-v3",
            "move legacy/source or component-local src rows during Xi-5a-v3",
            "re-decide conflicts already classified by Xi-4z",
            "remove attic or deprecated files permanently",
            "change semantic contracts, schemas, or runtime semantics intentionally",
        ],
        "gate_sequence_after_moves": list(readiness_v3.get("gate_sequence_after_moves") or []),
        "path_derivation_policy": "forbidden",
        "readiness_contract_path": XI5_READINESS_CONTRACT_V4_REL,
        "readiness_status": "xi5a_v3_dangerous_shadow_roots_can_proceed_mechanically_with_v4_lock",
        "report_id": "xi.4z.xi5_readiness_contract.v4",
        "reserved_package_targets_inherited": collision_targets_fixed,
        "selected_layout_option": _token(lock_v4.get("selected_layout_option")),
        "stop_conditions": [
            "encounter unmapped runtime-critical paths inside top-level src/ or app/src/",
            "need to derive or invent a new target path that is not listed in the v4 approved lock",
            "need to move any legacy/source, packs/source, libs/*/src, or tools/*/src row during Xi-5a-v3",
            "need to overwrite an occupied target path",
            "build breaks after approved dangerous shadow moves",
            "any STRICT or Ω verification fails",
        ],
    }
    readiness_v4["deterministic_fingerprint"] = canonical_sha256(dict(readiness_v4, deterministic_fingerprint=""))

    report = {
        "approved_for_xi5_count_v3": int(_counts(lock_v3)["approved_for_xi5"]),
        "approved_for_xi5_count_v4": int(counts["approved_for_xi5"]),
        "approved_to_attic_count_v3": int(_counts(lock_v3)["approved_to_attic"]),
        "approved_to_attic_count_v4": int(counts["approved_to_attic"]),
        "deferred_to_xi5b_count_v3": int(_counts(lock_v3)["deferred_to_xi5b"]),
        "deferred_to_xi5b_count_v4": int(counts["deferred_to_xi5b"]),
        "dangerous_shadow_roots": ["app/src", "src"],
        "deferred_phase_counts": dict(sorted(phase_counts.items())),
        "inherited_reserved_package_targets": collision_targets_fixed,
        "inherited_reserved_target_paths": inherited_reserved_target_paths,
        "missing_package_initializers_promoted": sorted(promoted_sources),
        "non_dangerous_rows_rephased_count": int(len(deferred_rows_v4) - (len(deferred_rows_v3) - len(promoted_sources))),
        "selected_option": _token(lock_v4.get("selected_layout_option")),
        "stdlib_collision_targets_fixed": collision_targets_fixed,
        "total_rows_preserved": bool(_counts(lock_v3)["total_rows"] == counts["total_rows"]),
        "v3_readiness_status": _token(readiness_v3.get("readiness_status")),
        "v4_readiness_status": _token(readiness_v4.get("readiness_status")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))

    return {
        "lock_v4": lock_v4,
        "readiness_v4": readiness_v4,
        "target_paths_v4": target_paths_v4,
        "report": report,
    }


def _render_shadow_report(snapshot: Mapping[str, object]) -> str:
    report = dict(snapshot.get("report") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-5a-v3 dangerous shadow-root execution logs",
        "",
        "# XI-4z Shadow-Root Resolution Report",
        "",
        "## Scope Decision",
        "",
        "- Xi-5a-v3 is narrowed to dangerous shadow roots only: `src/` and `app/src/`.",
        "- Legacy `source/` pockets, component-local `src/`, and content-source roots are deferred to later Xi-5 phases.",
        "- Reserved package collisions inherited from Xi-4z-fix2 remain protected: `{}`.".format(", ".join(report.get("stdlib_collision_targets_fixed") or []) or "none"),
        "",
        "## Counts",
        "",
        "- approved_for_xi5 v3: `{}`".format(int(report.get("approved_for_xi5_count_v3", 0) or 0)),
        "- approved_for_xi5 v4: `{}`".format(int(report.get("approved_for_xi5_count_v4", 0) or 0)),
        "- approved_to_attic v3: `{}`".format(int(report.get("approved_to_attic_count_v3", 0) or 0)),
        "- approved_to_attic v4: `{}`".format(int(report.get("approved_to_attic_count_v4", 0) or 0)),
        "- deferred_to_xi5b v3: `{}`".format(int(report.get("deferred_to_xi5b_count_v3", 0) or 0)),
        "- deferred_to_xi5b v4: `{}`".format(int(report.get("deferred_to_xi5b_count_v4", 0) or 0)),
        "",
        "## Promoted Package Initializers",
        "",
    ]
    promoted = list(report.get("missing_package_initializers_promoted") or [])
    if promoted:
        for source_path in promoted:
            lines.append("- `{}`".format(_norm_rel(source_path)))
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Deferred Follow-On Phase Counts",
            "",
        ]
    )
    for phase_name, count in sorted(dict(report.get("deferred_phase_counts") or {}).items()):
        lines.append("- `{}`: `{}`".format(_token(phase_name), int(count or 0)))
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "- Xi-5a-v3 can now execute the dangerous shadow-root slice mechanically from the v4 lock without re-deciding target paths.",
            "- Xi-5b/Xi-5c remain responsible for the deferred legacy, content-source, and component-local source pockets.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_execution_inputs(snapshot: Mapping[str, object]) -> str:
    report = dict(snapshot.get("report") or {})
    readiness = dict(snapshot.get("readiness_v4") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-5a-v3 execution log and final audit report",
        "",
        "# XI-5a Execution Inputs",
        "",
        "- approved lock: `{}`".format(SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL),
        "- readiness contract: `{}`".format(XI5_READINESS_CONTRACT_V4_REL),
        "- dangerous shadow roots: `src/`, `app/src/`",
        "- approved dangerous-shadow rows: `{}`".format(int(report.get("approved_for_xi5_count_v4", 0) or 0)),
        "- approved attic rows in this phase: `{}`".format(int(report.get("approved_to_attic_count_v4", 0) or 0)),
        "- deferred rows left for later phases: `{}`".format(int(report.get("deferred_to_xi5b_count_v4", 0) or 0)),
        "- path derivation policy: `{}`".format(_token(readiness.get("path_derivation_policy"))),
        "",
        "Xi-5a-v3 must move only rows listed in the v4 lock, must not touch legacy/source or component-local src rows, and must inherit the reserved-package protections already established for `platform` and `time`.",
        "",
    ]
    return "\n".join(lines)


def _render_final_doc(snapshot: Mapping[str, object]) -> str:
    report = dict(snapshot.get("report") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-5a-v3 final execution report",
        "",
        "# XI-4z Fix3 Final",
        "",
        "- selected option preserved: `{}`".format(_token(report.get("selected_option"))),
        "- dangerous shadow roots for Xi-5a-v3: `src/`, `app/src/`",
        "- approved dangerous-shadow rows: `{}`".format(int(report.get("approved_for_xi5_count_v4", 0) or 0)),
        "- promoted package initializers: `{}`".format(", ".join(report.get("missing_package_initializers_promoted") or []) or "none"),
        "- deferred rows for Xi-5b/Xi-5c: `{}`".format(int(report.get("deferred_to_xi5b_count_v4", 0) or 0)),
        "- reserved package protections inherited: `{}`".format(", ".join(report.get("stdlib_collision_targets_fixed") or []) or "none"),
        "",
        "Xi-5a should no longer attempt the full mixed `src/source` surface. It should execute only the dangerous shadow-root slice using the v4 lock and leave later source-pocket normalization to subsequent Xi-5 phases.",
        "",
    ]
    return "\n".join(lines)


def build_xi4z_fix3_snapshot(repo_root: str) -> dict[str, object]:
    repo_root_abs = _repo_root(repo_root)
    missing = _required_inputs_missing(repo_root_abs)
    if missing:
        raise Xi4zFix3InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix3.missing_inputs",
                    "missing_inputs": missing,
                },
                indent=2,
                sort_keys=True,
            )
        )

    snapshot = _build_json_payloads(
        repo_root_abs,
        {
            "fix2_report": _load_json_required(repo_root_abs, XI4Z_FIX2_REPORT_JSON_REL),
            "lock_v3": _load_json_required(repo_root_abs, SRC_DOMAIN_MAPPING_LOCK_APPROVED_V3_REL),
            "readiness_v3": _load_json_required(repo_root_abs, XI5_READINESS_CONTRACT_V3_REL),
            "target_paths_v3": _load_json_required(repo_root_abs, SRC_DOMAIN_MAPPING_TARGET_PATHS_V3_REL),
        },
    )
    snapshot["docs"] = {
        XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT_REL: _render_shadow_report(snapshot),
        XI_5A_EXECUTION_INPUTS_REL: _render_execution_inputs(snapshot),
        XI_4Z_FIX3_FINAL_REL: _render_final_doc(snapshot),
    }
    snapshot["summary"] = {
        "approved_for_xi5_count": int(_counts(snapshot["lock_v4"])["approved_for_xi5"]),
        "approved_to_attic_count": int(_counts(snapshot["lock_v4"])["approved_to_attic"]),
        "dangerous_shadow_root_count": 2,
        "deferred_to_xi5b_count": int(_counts(snapshot["lock_v4"])["deferred_to_xi5b"]),
        "missing_package_initializers_promoted_count": len(list(snapshot["report"].get("missing_package_initializers_promoted") or [])),
        "selected_option": _token(snapshot["report"].get("selected_option")),
    }
    return snapshot


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    docs = dict(snapshot.get("docs") or {})
    return {
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL: canonical_sha256(dict(snapshot.get("lock_v4") or {})),
        XI5_READINESS_CONTRACT_V4_REL: canonical_sha256(dict(snapshot.get("readiness_v4") or {})),
        SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL: canonical_sha256(dict(snapshot.get("target_paths_v4") or {})),
        XI4Z_FIX3_REPORT_JSON_REL: canonical_sha256(dict(snapshot.get("report") or {})),
        XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT_REL: canonical_sha256(str(docs.get(XI_4Z_SHADOW_ROOT_RESOLUTION_REPORT_REL) or "")),
        XI_5A_EXECUTION_INPUTS_REL: canonical_sha256(str(docs.get(XI_5A_EXECUTION_INPUTS_REL) or "")),
        XI_4Z_FIX3_FINAL_REL: canonical_sha256(str(docs.get(XI_4Z_FIX3_FINAL_REL) or "")),
    }


def write_xi4z_fix3_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    repo_root_abs = _repo_root(repo_root)
    json_outputs = {
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL: dict(snapshot.get("lock_v4") or {}),
        XI5_READINESS_CONTRACT_V4_REL: dict(snapshot.get("readiness_v4") or {}),
        SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL: dict(snapshot.get("target_paths_v4") or {}),
        XI4Z_FIX3_REPORT_JSON_REL: dict(snapshot.get("report") or {}),
    }
    doc_outputs = dict(snapshot.get("docs") or {})
    for rel_path, payload in json_outputs.items():
        abs_path = _repo_abs(repo_root_abs, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json_text(payload))
            handle.write("\n")
    for rel_path, text in doc_outputs.items():
        abs_path = _repo_abs(repo_root_abs, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(str(text))
            if not str(text).endswith("\n"):
                handle.write("\n")
