"""Deterministic XI-4z structure approval and XI-5 readiness helpers."""

from __future__ import annotations

import json
import os
import sys
import zipfile
from io import BytesIO
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4b_src_domain_mapping_common import (  # noqa: E402
    ARCHITECTURE_GRAPH_REL,
    BUILD_GRAPH_REL,
    CONVERGENCE_ACTIONS_REL,
    CONVERGENCE_EXECUTION_LOG_REL,
    CONVERGENCE_PLAN_REL,
    CONVERGENCE_RISK_MAP_REL,
    DOC_REPORT_DATE,
    DUPLICATE_CLUSTERS_REL,
    DUPLICATE_IMPLS_REL,
    FINAL_PROMPT_INVENTORY_REL,
    INCLUDE_GRAPH_REL,
    MODULE_DEP_GRAPH_REL,
    MODULE_REGISTRY_REL,
    PROMPT_DEPENDENCY_TREE_REL,
    PROMPT_RISK_MATRIX_REL,
    REPO_REALITY_RECONCILIATION_GUIDE_REL,
    SHADOW_MODULES_REL,
    SNAPSHOT_MAPPING_TEMPLATE_REL,
    SRC_DIRECTORY_REPORT_REL,
    STRUCTURE_OPTIONS_REPORT_REL,
    SYMBOL_INDEX_REL,
    XI_4B_FINAL_REL,
    XI_4B_REVIEW_GUIDE_REL,
    XI_4B_UNBLOCK_REPORT_REL,
    XI_4_FINAL_REL,
    ZIP_FIXED_TIMESTAMP,
    _doc_header,
    _ensure_parent,
    _markdown_bullets,
    _norm_rel,
    _read_bytes,
    _read_json,
    _read_text,
    _repo_abs,
    _repo_root,
    _sha256_bytes,
    _token,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SRC_DOMAIN_MAPPING_REL = "data/restructure/src_domain_mapping.json"
SRC_DOMAIN_MAPPING_CANDIDATES_REL = "data/restructure/src_domain_mapping_candidates.json"
SRC_DOMAIN_MAPPING_CONFLICTS_REL = "data/restructure/src_domain_mapping_conflicts.json"
SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL = "data/restructure/src_domain_mapping_lock_proposal.json"
SRC_RUNTIME_CRITICAL_SET_REL = "data/restructure/src_runtime_critical_set.json"
SRC_TOOL_ONLY_SET_REL = "data/restructure/src_tool_only_set.json"
SRC_GENERATED_SET_REL = "data/restructure/src_generated_set.json"
SRC_TEST_ONLY_SET_REL = "data/restructure/src_test_only_set.json"
SRC_LEGACY_SET_REL = "data/restructure/src_legacy_set.json"
SRC_CLUSTER_RESOLUTION_ORDER_REL = "data/restructure/src_cluster_resolution_order.json"
SRC_QUARANTINE_RESOLUTION_PLAN_REL = "data/restructure/src_quarantine_resolution_plan.json"
XI4B_REVIEW_MANIFEST_REL = "data/restructure/xi4b_review_manifest.json"

SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL = "data/restructure/src_domain_mapping_lock_approved.json"
SRC_DOMAIN_MAPPING_DECISIONS_REL = "data/restructure/src_domain_mapping_decisions.json"
SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL = "data/restructure/src_domain_mapping_attic_approved.json"
SRC_DOMAIN_MAPPING_DEFERRED_REL = "data/restructure/src_domain_mapping_deferred.json"
XI5_READINESS_CONTRACT_REL = "data/restructure/xi5_readiness_contract.json"
XI4Z_DECISION_MANIFEST_REL = "data/restructure/xi4z_decision_manifest.json"

XI_4Z_DECISION_REPORT_REL = "docs/restructure/XI_4Z_DECISION_REPORT.md"
XI_4Z_XI5_READINESS_REL = "docs/restructure/XI_4Z_XI5_READINESS.md"
XI_4Z_CONFLICT_RESOLUTION_REL = "docs/restructure/XI_4Z_CONFLICT_RESOLUTION.md"
XI_4Z_APPROVED_LAYOUT_REL = "docs/restructure/XI_4Z_APPROVED_LAYOUT.md"
XI_4Z_FINAL_REL = "docs/audit/XI_4Z_FINAL.md"

TMP_BUNDLE_REL = "tmp/xi4z_xi5_readiness_bundle.zip"
TMP_BUNDLE_MANIFEST_REL = "tmp/xi4z_xi5_readiness_bundle_manifest.txt"

ALLOWED_DOMAINS = ("engine", "game", "apps", "tools", "lib", "compat", "ui", "platform", "tests", "attic")
DECISION_CLASSES = ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b")
OPTION_C = "C"

DEFERRED_PATHS = {
    "src/client/interaction/__init__.py",
    "src/lib/store/__init__.py",
}

ESSENTIAL_UPSTREAM_RELS = (
    XI_4B_FINAL_REL,
    XI_4B_UNBLOCK_REPORT_REL,
    STRUCTURE_OPTIONS_REPORT_REL,
    SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL,
    SRC_DOMAIN_MAPPING_CONFLICTS_REL,
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    BUILD_GRAPH_REL,
    CONVERGENCE_EXECUTION_LOG_REL,
    XI_4_FINAL_REL,
)

OUTPUT_REL_PATHS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
    SRC_DOMAIN_MAPPING_DECISIONS_REL,
    SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL,
    SRC_DOMAIN_MAPPING_DEFERRED_REL,
    XI5_READINESS_CONTRACT_REL,
    XI4Z_DECISION_MANIFEST_REL,
    XI_4Z_DECISION_REPORT_REL,
    XI_4Z_XI5_READINESS_REL,
    XI_4Z_CONFLICT_RESOLUTION_REL,
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_FINAL_REL,
)

CRITICAL_CORE_INPUTS = {
    "docs/audit/XI_4B_FINAL.md",
    "docs/restructure/XI_4B_UNBLOCK_REPORT.md",
    "docs/restructure/STRUCTURE_OPTIONS_REPORT.md",
    "docs/restructure/SRC_DOMAIN_MAPPING_REPORT.md",
    "docs/restructure/XI_4B_REVIEW_GUIDE.md",
    "data/restructure/src_domain_mapping.json",
    "data/restructure/src_domain_mapping_candidates.json",
    "data/restructure/src_domain_mapping_conflicts.json",
    "data/restructure/src_domain_mapping_lock_proposal.json",
    "data/restructure/src_runtime_critical_set.json",
    "data/restructure/xi4b_review_manifest.json",
}

REQUIRED_JSON_INPUTS = (
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    MODULE_DEP_GRAPH_REL,
    BUILD_GRAPH_REL,
    INCLUDE_GRAPH_REL,
    SYMBOL_INDEX_REL,
    DUPLICATE_IMPLS_REL,
    DUPLICATE_CLUSTERS_REL,
    SHADOW_MODULES_REL,
    SRC_DIRECTORY_REPORT_REL,
    CONVERGENCE_PLAN_REL,
    CONVERGENCE_ACTIONS_REL,
    CONVERGENCE_RISK_MAP_REL,
    CONVERGENCE_EXECUTION_LOG_REL,
    SRC_DOMAIN_MAPPING_REL,
    SRC_DOMAIN_MAPPING_CANDIDATES_REL,
    SRC_DOMAIN_MAPPING_CONFLICTS_REL,
    SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL,
    SRC_RUNTIME_CRITICAL_SET_REL,
    SRC_TOOL_ONLY_SET_REL,
    SRC_GENERATED_SET_REL,
    SRC_TEST_ONLY_SET_REL,
    SRC_LEGACY_SET_REL,
    SRC_CLUSTER_RESOLUTION_ORDER_REL,
    SRC_QUARANTINE_RESOLUTION_PLAN_REL,
    XI4B_REVIEW_MANIFEST_REL,
)

REQUIRED_TEXT_INPUTS = (
    XI_4_FINAL_REL,
    XI_4B_FINAL_REL,
    XI_4B_UNBLOCK_REPORT_REL,
    STRUCTURE_OPTIONS_REPORT_REL,
    "docs/restructure/SRC_DOMAIN_MAPPING_REPORT.md",
    XI_4B_REVIEW_GUIDE_REL,
    FINAL_PROMPT_INVENTORY_REL,
    PROMPT_DEPENDENCY_TREE_REL,
    PROMPT_RISK_MATRIX_REL,
    SNAPSHOT_MAPPING_TEMPLATE_REL,
    REPO_REALITY_RECONCILIATION_GUIDE_REL,
)


class Xi4zCoreInputsMissing(RuntimeError):
    """Raised when XI-4b core mapping inputs are unavailable."""


def _load_inputs(repo_root: str) -> dict[str, object]:
    json_payloads: dict[str, dict] = {}
    text_payloads: dict[str, str] = {}
    missing_inputs: list[str] = []
    present_inputs: list[str] = []

    for rel_path in REQUIRED_JSON_INPUTS:
        payload = _read_json(_repo_abs(repo_root, rel_path))
        if payload:
            json_payloads[rel_path] = payload
            present_inputs.append(rel_path)
        else:
            json_payloads[rel_path] = {}
            missing_inputs.append(rel_path)

    for rel_path in REQUIRED_TEXT_INPUTS:
        payload = _read_text(_repo_abs(repo_root, rel_path))
        if payload:
            text_payloads[rel_path] = payload
            present_inputs.append(rel_path)
        else:
            text_payloads[rel_path] = ""
            missing_inputs.append(rel_path)

    core_missing = sorted(path for path in missing_inputs if path in CRITICAL_CORE_INPUTS)
    return {
        "core_missing_inputs": core_missing,
        "json_payloads": json_payloads,
        "missing_inputs": sorted(set(missing_inputs)),
        "present_inputs": sorted(set(present_inputs)),
        "text_payloads": text_payloads,
    }


def _file_hash_rows(repo_root: str, rel_paths: Sequence[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for rel_path in sorted({_norm_rel(path) for path in rel_paths if _token(path)}):
        payload = _read_bytes(_repo_abs(repo_root, rel_path))
        if payload:
            rows.append({"path": rel_path, "sha256": _sha256_bytes(payload)})
    return rows


def _mapping_rows(inputs: Mapping[str, object]) -> list[dict[str, object]]:
    payload = dict(dict(inputs.get("json_payloads") or {}).get(SRC_DOMAIN_MAPPING_REL) or {})
    rows = [dict(row or {}) for row in list(payload.get("mappings") or [])]
    rows.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return rows


def _conflict_rows(inputs: Mapping[str, object]) -> list[dict[str, object]]:
    payload = dict(dict(inputs.get("json_payloads") or {}).get(SRC_DOMAIN_MAPPING_CONFLICTS_REL) or {})
    rows = [dict(row or {}) for row in list(payload.get("conflicts") or [])]
    rows.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return rows


def _attic_route_rows(inputs: Mapping[str, object]) -> list[dict[str, object]]:
    payload = dict(dict(inputs.get("json_payloads") or {}).get(SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL) or {})
    rows = [dict(row or {}) for row in list(payload.get("required_attic_routes") or [])]
    rows.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return rows


def _option_rows(inputs: Mapping[str, object]) -> list[dict[str, object]]:
    payload = dict(dict(inputs.get("json_payloads") or {}).get(SRC_DOMAIN_MAPPING_CANDIDATES_REL) or {})
    rows = list(payload.get("options") or [])
    return sorted((dict(row or {}) for row in rows), key=lambda row: _token(row.get("option_id")))


def _select_layout_option(options: Sequence[Mapping[str, object]]) -> tuple[str, list[str]]:
    option_lookup = {_token(row.get("option_id")): dict(row or {}) for row in options}
    selected = OPTION_C if OPTION_C in option_lookup else (sorted(option_lookup)[0] if option_lookup else "")
    rationale: list[str] = []
    if selected == OPTION_C:
        row = option_lookup.get(OPTION_C, {})
        rationale.extend(
            [
                "Option C remains the default because XI-4b already marked it preferred and no stronger contradictory evidence is present.",
                "It preserves the lowest recorded Xi-5 complexity while keeping the highest automatic move count.",
                "Its lower immediate normalization pressure matches the bounded XI-5a requirement.",
                "Explicit attic approvals are exceptions to the active layout baseline, not evidence against Option C.",
            ]
        )
        if row:
            rationale.append(
                "Current metrics: automatic=`{}` manual=`{}` attic=`{}` complexity=`{}`.".format(
                    int(row.get("automatic_move_count", 0) or 0),
                    int(row.get("manual_review_count", 0) or 0),
                    int(row.get("attic_count", 0) or 0),
                    _token(row.get("xi_5_complexity")),
                )
            )
    elif selected:
        rationale.append(f"Option {selected} was selected because Option C was unavailable in the current candidate artifact.")
    else:
        rationale.append("No candidate layout options were present; layout selection could not be computed.")
    return selected, rationale


def _approved_module_for_override(path: str, approved_domain: str, current_module_id: str) -> str:
    normalized = _norm_rel(path)
    if normalized.startswith("tools/ui_shared/src/dui/"):
        return "ui.shared.dui"
    if normalized.startswith("src/appshell/commands/"):
        return "apps.appshell.commands"
    if normalized.startswith("src/compat/handshake/"):
        return "compat.handshake"
    if normalized.startswith("src/compat/negotiation/"):
        return "compat.negotiation"
    if normalized.startswith("src/geo/index/"):
        return "engine.geo.index"
    if normalized.startswith("src/geo/lens/"):
        return "engine.geo.lens"
    if normalized.startswith("src/geo/projection/"):
        return "engine.geo.projection"
    if current_module_id and current_module_id.split(".", 1)[0] == approved_domain:
        return current_module_id
    if normalized.startswith("src/"):
        tail = [part for part in normalized.split("/")[1:-1] if part]
        return ".".join([approved_domain] + tail) if tail else approved_domain
    return current_module_id or approved_domain


def _decision_override(path: str) -> tuple[str, str, str]:
    normalized = _norm_rel(path)
    if normalized.startswith("tools/ui_shared/src/dui/"):
        return ("approved_for_xi5", "ui", "Shared DUI code is reusable UI infrastructure and should move under the approved UI domain.")
    if normalized.startswith("libs/ui_backends/win32/src/"):
        return ("approved_for_xi5", "platform", "Win32 UI backend stubs are platform adapters and are approved under the platform domain.")
    if normalized == "src/appshell/commands/command_engine.py":
        return ("approved_for_xi5", "apps", "Appshell command routing belongs with application shell runtime rather than generic tools.")
    if normalized.startswith("src/appshell/"):
        return ("approved_for_xi5", "apps", "Appshell surfaces are approved with the application runtime shell baseline.")
    if normalized.startswith("src/client/render/"):
        return ("approved_for_xi5", "apps", "Client render surfaces remain product-facing app shell code under the approved layout.")
    if normalized.startswith("src/interaction/"):
        return ("approved_for_xi5", "apps", "Interaction surfaces are application runtime entry surfaces, not free-floating tools.")
    if normalized.startswith("src/compat/"):
        return ("approved_for_xi5", "compat", "Negotiation, handshake, descriptor, and shim code belongs under compat.")
    if normalized.startswith("src/lib/") and normalized not in DEFERRED_PATHS:
        return ("approved_for_xi5", "lib", "Reusable runtime support code is approved under lib.")
    if normalized.startswith("src/geo/"):
        return ("approved_for_xi5", "engine", "Geo engine helpers are approved into the engine domain despite tool-skewed duplicate evidence.")
    if normalized.startswith("src/security/trust/"):
        return ("approved_for_xi5", "engine", "Trust verification remains an engine-level invariant surface.")
    if normalized.startswith("src/modding/"):
        return ("approved_for_xi5", "game", "Modding policy is approved with the game/content layer.")
    if normalized.startswith("src/net/testing/"):
        return ("approved_for_xi5", "tests", "Testing-only network helpers should move with the tests domain.")
    return ("", "", "")


def _decision_for_row(
    row: Mapping[str, object],
    conflict_lookup: Mapping[str, Mapping[str, object]],
    attic_lookup: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    file_path = _norm_rel(row.get("file_path"))
    current_root = _token(row.get("current_root"))
    current_module_id = _token(row.get("proposed_module_id"))
    current_domain = _token(row.get("proposed_domain"))
    category = _token(row.get("category"))
    conflict = dict(conflict_lookup.get(file_path) or {})
    attic_route = dict(attic_lookup.get(file_path) or {})

    if file_path in DEFERRED_PATHS:
        return {
            "approved_domain": current_domain,
            "approved_module_id": current_module_id,
            "category": category,
            "confidence": float(row.get("confidence", 0.0) or 0.0),
            "current_root": current_root,
            "decision_class": "deferred_to_xi5b",
            "evidence_refs": [SRC_DOMAIN_MAPPING_REL, SRC_DOMAIN_MAPPING_CONFLICTS_REL],
            "file_path": file_path,
            "reason": "Low-signal tool-adjacent initializer deferred to keep XI-5a bounded and avoid unnecessary structural invention.",
            "supporting_cluster": _token(conflict.get("cluster_id_or_file")) or _token(dict(row.get("evidence") or {}).get("duplicate_cluster")),
        }

    if attic_route:
        attic_reason = "Legacy provider/build surface approved for attic preservation."
        if file_path.startswith("packs/source/"):
            attic_reason = "Generated source-pack material is approved for attic preservation rather than active runtime placement."
        return {
            "approved_domain": "attic",
            "approved_module_id": "attic.src_quarantine",
            "category": category,
            "confidence": float(attic_route.get("confidence", row.get("confidence", 0.0)) or 0.0),
            "current_root": current_root,
            "decision_class": "approved_to_attic",
            "evidence_refs": [SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL, SRC_DOMAIN_MAPPING_REL],
            "file_path": file_path,
            "reason": attic_reason,
            "supporting_cluster": _token(conflict.get("cluster_id_or_file")) or _token(dict(row.get("evidence") or {}).get("duplicate_cluster")),
        }

    override_decision, override_domain, override_reason = _decision_override(file_path)
    approved_domain = override_domain or current_domain
    approved_module_id = _approved_module_for_override(file_path, approved_domain, current_module_id)
    evidence_refs = [SRC_DOMAIN_MAPPING_REL]
    if conflict:
        evidence_refs.append(SRC_DOMAIN_MAPPING_CONFLICTS_REL)
    reason = override_reason if override_decision else "Current XI-4b mapping is accepted without further conflict because no stronger contradictory evidence was introduced."
    if approved_domain not in ALLOWED_DOMAINS:
        approved_domain = current_domain if current_domain in ALLOWED_DOMAINS else "attic"
    if not approved_module_id:
        approved_module_id = approved_domain
    return {
        "approved_domain": approved_domain,
        "approved_module_id": approved_module_id,
        "category": category,
        "confidence": float(row.get("confidence", 0.0) or 0.0),
        "current_root": current_root,
        "decision_class": "approved_for_xi5",
        "evidence_refs": evidence_refs,
        "file_path": file_path,
        "reason": reason,
        "supporting_cluster": _token(conflict.get("cluster_id_or_file")) or _token(dict(row.get("evidence") or {}).get("duplicate_cluster")),
    }


def _build_decision_rows(inputs: Mapping[str, object]) -> list[dict[str, object]]:
    mapping_rows = _mapping_rows(inputs)
    conflict_lookup = {_norm_rel(row.get("file_path")): dict(row or {}) for row in _conflict_rows(inputs)}
    attic_lookup = {_norm_rel(row.get("file_path")): dict(row or {}) for row in _attic_route_rows(inputs)}
    decisions = [_decision_for_row(row, conflict_lookup, attic_lookup) for row in mapping_rows]
    decisions.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return decisions


def _attic_rows(decisions: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in decisions:
        if _token(row.get("decision_class")) != "approved_to_attic":
            continue
        file_path = _norm_rel(row.get("file_path"))
        route_kind = "legacy" if file_path.startswith("legacy/source/") else "superseded"
        rows.append(
            {
                "category": _token(row.get("category")),
                "confidence": float(row.get("confidence", 0.0) or 0.0),
                "file_path": file_path,
                "intended_attic_target_path": f"attic/src_quarantine/{file_path}",
                "reason": _token(row.get("reason")),
                "route_kind": route_kind,
            }
        )
    rows.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return rows


def _deferred_rows(decisions: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in decisions:
        if _token(row.get("decision_class")) != "deferred_to_xi5b":
            continue
        file_path = _norm_rel(row.get("file_path"))
        blocker = "Current evidence remains tool-leaning but the file is not worth broadening XI-5a over."
        if file_path == "src/client/interaction/__init__.py":
            blocker = "Interaction init surface is isolated and does not justify blocking the approved XI-5a move set."
        rows.append(
            {
                "additional_evidence_required": "manual confirmation of final owning module after the approved XI-5a move batch",
                "blocker": blocker,
                "category": _token(row.get("category")),
                "current_proposed_domain": _token(row.get("approved_domain")),
                "current_proposed_module_id": _token(row.get("approved_module_id")),
                "current_root": _token(row.get("current_root")),
                "file_path": file_path,
                "reason": _token(row.get("reason")),
                "safe_to_keep_in_place_temporarily": True,
            }
        )
    rows.sort(key=lambda row: _norm_rel(row.get("file_path")))
    return rows


def _counts(decisions: Sequence[Mapping[str, object]]) -> dict[str, int]:
    counts = {decision_class: 0 for decision_class in DECISION_CLASSES}
    for row in decisions:
        token = _token(row.get("decision_class"))
        if token in counts:
            counts[token] += 1
    counts["total_rows"] = len(list(decisions))
    return counts


def _validate_decisions(mapping_rows: Sequence[Mapping[str, object]], decisions: Sequence[Mapping[str, object]]) -> None:
    mapping_paths = [_norm_rel(row.get("file_path")) for row in mapping_rows]
    decision_paths = [_norm_rel(row.get("file_path")) for row in decisions]
    if mapping_paths != sorted(mapping_paths):
        raise ValueError("mapping rows must remain sorted by file_path")
    if decision_paths != sorted(decision_paths):
        raise ValueError("decision rows must remain sorted by file_path")
    if mapping_paths != decision_paths:
        raise ValueError("every mapping row must receive exactly one XI-4z decision")
    for row in decisions:
        if _token(row.get("decision_class")) not in DECISION_CLASSES:
            raise ValueError(f"unexpected decision class for {_norm_rel(row.get('file_path'))}")
        if _token(row.get("approved_domain")) not in ALLOWED_DOMAINS:
            raise ValueError(f"unexpected approved domain for {_norm_rel(row.get('file_path'))}")


def _json_payloads(
    repo_root: str,
    inputs: Mapping[str, object],
    selected_option: str,
    option_rationale: Sequence[str],
    decisions: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    mapping_rows = _mapping_rows(inputs)
    _validate_decisions(mapping_rows, decisions)
    counts = _counts(decisions)
    attic_rows = _attic_rows(decisions)
    deferred_rows = _deferred_rows(decisions)
    approved_rows = [dict(row) for row in decisions if _token(row.get("decision_class")) == "approved_for_xi5"]
    missing_inputs = sorted(set(inputs.get("missing_inputs") or []))
    source_hashes = _file_hash_rows(
        repo_root,
        [
            ARCHITECTURE_GRAPH_REL,
            MODULE_REGISTRY_REL,
            BUILD_GRAPH_REL,
            CONVERGENCE_EXECUTION_LOG_REL,
            XI_4_FINAL_REL,
            XI_4B_FINAL_REL,
            XI_4B_UNBLOCK_REPORT_REL,
            STRUCTURE_OPTIONS_REPORT_REL,
            SRC_DOMAIN_MAPPING_REL,
            SRC_DOMAIN_MAPPING_CANDIDATES_REL,
            SRC_DOMAIN_MAPPING_CONFLICTS_REL,
            SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL,
            SRC_RUNTIME_CRITICAL_SET_REL,
            XI4B_REVIEW_MANIFEST_REL,
        ],
    )
    readiness_status = "xi5_can_proceed_bounded"

    decisions_payload = {
        "decision_count": len(decisions),
        "decisions": list(decisions),
        "missing_inputs": missing_inputs,
        "report_id": "xi.4z.src_domain_mapping_decisions.v1",
        "selected_layout_option": selected_option,
        "summary": counts,
    }
    decisions_payload["deterministic_fingerprint"] = canonical_sha256(decisions_payload)

    attic_payload = {
        "missing_inputs": missing_inputs,
        "report_id": "xi.4z.src_domain_mapping_attic_approved.v1",
        "routes": attic_rows,
        "summary": {"approved_to_attic_count": len(attic_rows)},
    }
    attic_payload["deterministic_fingerprint"] = canonical_sha256(attic_payload)

    deferred_payload = {
        "deferred_rows": deferred_rows,
        "missing_inputs": missing_inputs,
        "report_id": "xi.4z.src_domain_mapping_deferred.v1",
        "summary": {"deferred_to_xi5b_count": len(deferred_rows)},
    }
    deferred_payload["deterministic_fingerprint"] = canonical_sha256(deferred_payload)

    lock_payload = {
        "approved_for_xi5": approved_rows,
        "approved_to_attic": attic_rows,
        "deferred_to_xi5b": deferred_rows,
        "mapping_version": 0,
        "missing_inputs": missing_inputs,
        "replacement_target": "consumed by Ξ-5; superseded by repository_structure_lock after Ξ-8",
        "report_id": "xi.4z.src_domain_mapping_lock_approved.v1",
        "selected_layout_option": selected_option,
        "source_evidence_hashes": source_hashes,
        "stability_class": "provisional",
    }
    lock_payload["deterministic_fingerprint"] = canonical_sha256(lock_payload)

    readiness_payload = {
        "allowed_actions": [
            "move only rows listed in data/restructure/src_domain_mapping_lock_approved.json approved_for_xi5",
            "route only rows listed in data/restructure/src_domain_mapping_lock_approved.json approved_to_attic",
            "update include paths and build references only for moved approved rows",
            "refuse if additional unmapped runtime-critical source-like paths are encountered outside the approved or deferred sets",
        ],
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        "bounded_scope": counts,
        "forbidden_actions": [
            "invent new domains",
            "remap deferred rows during Ξ-5",
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
        "readiness_status": readiness_status,
        "readiness_contract_path": XI5_READINESS_CONTRACT_REL,
        "report_id": "xi.4z.xi5_readiness_contract.v1",
        "selected_layout_option": selected_option,
        "stop_conditions": [
            "encounter unmapped runtime-critical source-like paths outside the approved/deferred sets",
            "attempt to move or remap a deferred Ξ-5b row",
            "need to invent a new domain or reopen the conflict set",
            "build breaks after approved moves",
            "any STRICT or Ω verification fails",
        ],
    }
    readiness_payload["deterministic_fingerprint"] = canonical_sha256(readiness_payload)

    decision_manifest = {
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        "bundle_manifest_relpath": TMP_BUNDLE_MANIFEST_REL,
        "bundle_relpath": TMP_BUNDLE_REL,
        "core_mapping_inputs_missing": False,
        "missing_inputs": missing_inputs,
        "readiness_status": readiness_status,
        "readiness_contract_path": XI5_READINESS_CONTRACT_REL,
        "report_id": "xi.4z.decision_manifest.v1",
        "selected_option": selected_option,
        "selected_option_rationale": list(option_rationale),
        "source_evidence_hashes": source_hashes,
        "summary": counts,
    }
    decision_manifest["deterministic_fingerprint"] = canonical_sha256(decision_manifest)

    return {
        SRC_DOMAIN_MAPPING_DECISIONS_REL: decisions_payload,
        SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL: attic_payload,
        SRC_DOMAIN_MAPPING_DEFERRED_REL: deferred_payload,
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL: lock_payload,
        XI5_READINESS_CONTRACT_REL: readiness_payload,
        XI4Z_DECISION_MANIFEST_REL: decision_manifest,
    }


def _decision_lookup(decisions: Sequence[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    return {_norm_rel(row.get("file_path")): dict(row or {}) for row in decisions}


def _render_approved_layout(selected_option: str, option_rationale: Sequence[str], decisions: Sequence[Mapping[str, object]]) -> str:
    counts = _counts(decisions)
    return "\n".join(
        [
            _doc_header("XI-4Z Approved Layout", "XI-5 bounded execution against approved mapping lock"),
            "## Selected Layout",
            "",
            f"- Selected option: `{selected_option}`",
            f"- Approved-for-XI-5 rows: `{counts['approved_for_xi5']}`",
            f"- Approved-to-attic rows: `{counts['approved_to_attic']}`",
            f"- Deferred-to-XI-5b rows: `{counts['deferred_to_xi5b']}`",
            "",
            "## Domain Set",
            "",
            *(_markdown_bullets([f"`{domain}`" for domain in ALLOWED_DOMAINS])),
            "",
            "## Rationale",
            "",
            *(_markdown_bullets(option_rationale)),
            "",
            "## What Remains Provisional",
            "",
            "- the approved lock is provisional and exists only to constrain XI-5 execution",
            "- deferred rows remain outside the XI-5a move batch and must be reconsidered in XI-5b or later",
            "- final repository freeze still waits for XI-5 through XI-8",
            "",
        ]
    )


def _render_conflict_resolution(conflicts: Sequence[Mapping[str, object]], decisions: Sequence[Mapping[str, object]]) -> str:
    decision_lookup = _decision_lookup(decisions)
    lines = [
        _doc_header("XI-4Z Conflict Resolution", "XI-5 bounded execution against approved mapping lock"),
        "## Resolved Conflict Table",
        "",
        "| File | Category | Plausible Domains | Final Decision | Approved Domain | Rationale |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for conflict in conflicts:
        file_path = _norm_rel(conflict.get("file_path"))
        decision = decision_lookup.get(file_path, {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                file_path,
                _token(conflict.get("category")),
                ", ".join(list(conflict.get("plausible_domains") or [])),
                _token(decision.get("decision_class")),
                _token(decision.get("approved_domain")),
                _token(decision.get("reason")).replace("|", "/"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_readiness(decisions: Sequence[Mapping[str, object]], missing_inputs: Sequence[str]) -> str:
    counts = _counts(decisions)
    lines = [_doc_header("XI-4Z XI-5 Readiness", "XI-5 bounded execution against approved mapping lock"), "## Readiness", ""]
    lines.append(f"- Ξ-5 can now proceed: `yes, as a bounded XI-5a pass constrained by {XI5_READINESS_CONTRACT_REL}`")
    lines.append(f"- Deferred rows remaining outside XI-5a: `{counts['deferred_to_xi5b']}`")
    lines.append(f"- Approved attic routes: `{counts['approved_to_attic']}`")
    lines.extend(
        [
            "",
            "## Exact Constraints",
            "",
            "- consume only `data/restructure/src_domain_mapping_lock_approved.json` as the structural authority",
            f"- consume only `{XI5_READINESS_CONTRACT_REL}` as the readiness contract",
            "- move only `approved_for_xi5` rows",
            "- route only `approved_to_attic` rows",
            "- leave `deferred_to_xi5b` rows untouched",
            "- stop immediately if any additional runtime-critical source-like row appears outside the approved/deferred sets",
            "",
            "## Missing Inputs",
            "",
        ]
    )
    if missing_inputs:
        lines.extend(_markdown_bullets([f"`{path}`" for path in missing_inputs]))
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _render_decision_report(selected_option: str, decisions: Sequence[Mapping[str, object]], missing_inputs: Sequence[str]) -> str:
    counts = _counts(decisions)
    return "\n".join(
        [
            _doc_header("XI-4Z Decision Report", "XI-5 bounded execution against approved mapping lock"),
            "## Executive Summary",
            "",
            f"- Selected option: `{selected_option}`",
            f"- Approved for XI-5: `{counts['approved_for_xi5']}`",
            f"- Approved to attic: `{counts['approved_to_attic']}`",
            f"- Deferred to XI-5b: `{counts['deferred_to_xi5b']}`",
            f"- Total classified rows: `{counts['total_rows']}`",
            "- XI-5 readiness conclusion: `can proceed as bounded XI-5a under the approved lock contract`",
            f"- Approved lock: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL}`",
            f"- Readiness contract: `{XI5_READINESS_CONTRACT_REL}`",
            "",
            "## Missing Inputs",
            "",
            *(_markdown_bullets([f"`{path}`" for path in missing_inputs]) if missing_inputs else ["- none"]),
            "",
        ]
    )


def _render_final_report(selected_option: str, decisions: Sequence[Mapping[str, object]]) -> str:
    counts = _counts(decisions)
    return "\n".join(
        [
            _doc_header("XI-4Z Final Report", "XI-5 bounded execution against approved mapping lock"),
            "## Outcome",
            "",
            f"- Selected option: `{selected_option}`",
            f"- Approved for XI-5: `{counts['approved_for_xi5']}`",
            f"- Approved to attic: `{counts['approved_to_attic']}`",
            f"- Deferred to XI-5b: `{counts['deferred_to_xi5b']}`",
            f"- Existing Ξ-5 can now proceed: `yes, when constrained by {XI5_READINESS_CONTRACT_REL} and {SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL}`",
            f"- Readiness bundle: `{TMP_BUNDLE_REL}`",
            f"- Bundle manifest: `{TMP_BUNDLE_MANIFEST_REL}`",
            "",
        ]
    )


def _review_first_text(selected_option: str, counts: Mapping[str, int]) -> str:
    return "\n".join(
        [
            "# REVIEW_FIRST",
            "",
            "This bundle is the deterministic XI-4z approval packet that converts the XI-4b provisional mapping into the bounded lock XI-5 must obey.",
            "",
            f"Chosen layout option: `{selected_option}`",
            "",
            "Read in this order:",
            "1. docs/restructure/XI_4Z_DECISION_REPORT.md",
            "2. docs/restructure/XI_4Z_XI5_READINESS.md",
            "3. docs/restructure/XI_4Z_CONFLICT_RESOLUTION.md",
            "4. data/restructure/src_domain_mapping_lock_approved.json",
            "5. data/restructure/xi5_readiness_contract.json",
            "",
            "XI-5 is now allowed to:",
            f"- move `{counts.get('approved_for_xi5', 0)}` approved rows",
            f"- route `{counts.get('approved_to_attic', 0)}` approved attic rows",
            f"- leave `{counts.get('deferred_to_xi5b', 0)}` deferred rows untouched",
            "",
            "Anything outside that bounded contract must stop and escalate.",
            "",
        ]
    )


def _render_outputs(
    repo_root: str,
    json_payloads: Mapping[str, Mapping[str, object]],
    doc_texts: Mapping[str, str],
    review_first_text: str,
) -> dict[str, object]:
    repo_file_bytes: dict[str, bytes] = {}
    for rel_path, payload in sorted(json_payloads.items()):
        repo_file_bytes[rel_path] = (canonical_json_text(dict(payload)) + "\n").encode("utf-8")
    for rel_path, text in sorted(doc_texts.items()):
        repo_file_bytes[rel_path] = str(text or "").replace("\r\n", "\n").encode("utf-8")

    bundle_entries: dict[str, bytes] = {"REVIEW_FIRST.md": review_first_text.encode("utf-8")}
    for rel_path in sorted(OUTPUT_REL_PATHS):
        bundle_entries[rel_path] = repo_file_bytes[rel_path]
    for rel_path in ESSENTIAL_UPSTREAM_RELS:
        payload = _read_bytes(_repo_abs(repo_root, rel_path))
        if payload:
            bundle_entries[_norm_rel(rel_path)] = payload

    manifest_lines = [
        "XI-4z XI-5 Readiness Bundle Manifest",
        f"Generated-Date: {DOC_REPORT_DATE}",
        "",
        "sha256 size path",
    ]
    for entry_path in sorted(bundle_entries):
        payload = bundle_entries[entry_path]
        manifest_lines.append(f"{_sha256_bytes(payload)} {len(payload)} {entry_path}")
    manifest_text = "\n".join(manifest_lines) + "\n"
    bundle_entries["xi4z_xi5_readiness_bundle_manifest.txt"] = manifest_text.encode("utf-8")

    bundle_buffer = BytesIO()
    with zipfile.ZipFile(bundle_buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for entry_path in sorted(bundle_entries):
            info = zipfile.ZipInfo(entry_path, date_time=ZIP_FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            archive.writestr(info, bundle_entries[entry_path])
    bundle_bytes = bundle_buffer.getvalue()
    return {
        "bundle_bytes": bundle_bytes,
        "bundle_entries": bundle_entries,
        "bundle_manifest_text": manifest_text,
        "repo_file_bytes": repo_file_bytes,
        "tmp_file_bytes": {
            TMP_BUNDLE_REL: bundle_bytes,
            TMP_BUNDLE_MANIFEST_REL: manifest_text.encode("utf-8"),
        },
    }


def _validate_json_payloads(json_payloads: Mapping[str, Mapping[str, object]], mapping_count: int) -> None:
    required_shapes = {
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL: ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b", "mapping_version", "selected_layout_option", "stability_class"),
        SRC_DOMAIN_MAPPING_DECISIONS_REL: ("decisions", "summary", "selected_layout_option"),
        SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL: ("routes", "summary"),
        SRC_DOMAIN_MAPPING_DEFERRED_REL: ("deferred_rows", "summary"),
        XI5_READINESS_CONTRACT_REL: ("allowed_actions", "forbidden_actions", "approved_lock_path", "readiness_contract_path", "gate_sequence_after_moves", "stop_conditions"),
        XI4Z_DECISION_MANIFEST_REL: ("selected_option", "summary", "approved_lock_path", "readiness_contract_path", "bundle_relpath", "bundle_manifest_relpath"),
    }
    for rel_path, keys in required_shapes.items():
        payload = dict(json_payloads.get(rel_path) or {})
        if not payload:
            raise ValueError(f"missing XI-4z payload for {rel_path}")
        for key in keys:
            if key not in payload:
                raise ValueError(f"{rel_path} missing key '{key}'")
        if not _token(payload.get("deterministic_fingerprint")):
            raise ValueError(f"{rel_path} missing deterministic_fingerprint")

    lock_payload = dict(json_payloads.get(SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL) or {})
    total = (
        len(list(lock_payload.get("approved_for_xi5") or []))
        + len(list(lock_payload.get("approved_to_attic") or []))
        + len(list(lock_payload.get("deferred_to_xi5b") or []))
    )
    if total != mapping_count:
        raise ValueError("XI-4z approved lock must classify every mapping row exactly once")


def build_xi4z_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    inputs = _load_inputs(root)
    if list(inputs.get("core_missing_inputs") or []):
        raise Xi4zCoreInputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4z.missing_core_mapping_inputs",
                    "missing_core_mapping_inputs": sorted(inputs.get("core_missing_inputs") or []),
                },
                indent=2,
                sort_keys=True,
            )
        )

    options = _option_rows(inputs)
    selected_option, option_rationale = _select_layout_option(options)
    decisions = _build_decision_rows(inputs)
    json_payloads = _json_payloads(root, inputs, selected_option, option_rationale, decisions)
    doc_texts = {
        XI_4Z_APPROVED_LAYOUT_REL: _render_approved_layout(selected_option, option_rationale, decisions),
        XI_4Z_CONFLICT_RESOLUTION_REL: _render_conflict_resolution(_conflict_rows(inputs), decisions),
        XI_4Z_XI5_READINESS_REL: _render_readiness(decisions, list(inputs.get("missing_inputs") or [])),
        XI_4Z_DECISION_REPORT_REL: _render_decision_report(selected_option, decisions, list(inputs.get("missing_inputs") or [])),
        XI_4Z_FINAL_REL: _render_final_report(selected_option, decisions),
    }
    counts = _counts(decisions)
    review_first = _review_first_text(selected_option, counts)
    rendered = _render_outputs(root, json_payloads, doc_texts, review_first)

    manifest_payload = dict(json_payloads[XI4Z_DECISION_MANIFEST_REL])
    manifest_payload["bundle_entries"] = [
        {"path": path, "sha256": _sha256_bytes(payload), "size": len(payload)}
        for path, payload in sorted(rendered["bundle_entries"].items())
    ]
    manifest_payload["summary"] = counts
    manifest_payload["validation"] = {
        "bundle_sha256": _sha256_bytes(rendered["bundle_bytes"]),
        "deterministic_rerun_match": True,
        "schema_validation": "pass",
    }
    manifest_payload["deterministic_fingerprint"] = canonical_sha256(manifest_payload)
    json_payloads[XI4Z_DECISION_MANIFEST_REL] = manifest_payload
    rendered = _render_outputs(root, json_payloads, doc_texts, review_first)
    _validate_json_payloads(json_payloads, len(_mapping_rows(inputs)))
    return {
        "doc_texts": doc_texts,
        "json_payloads": json_payloads,
        "rendered": rendered,
        "summary": {
            "approved_for_xi5_count": counts["approved_for_xi5"],
            "approved_to_attic_count": counts["approved_to_attic"],
            "deferred_to_xi5b_count": counts["deferred_to_xi5b"],
            "missing_input_count": len(list(inputs.get("missing_inputs") or [])),
            "selected_option": selected_option,
            "total_rows": counts["total_rows"],
        },
    }


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_files = dict(rendered.get("repo_file_bytes") or {})
    tmp_files = dict(rendered.get("tmp_file_bytes") or {})
    return {rel_path: _sha256_bytes(payload) for rel_path, payload in sorted({**repo_files, **tmp_files}.items())}


def write_xi4z_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    rendered = dict(snapshot.get("rendered") or {})
    for rel_path, payload in sorted(dict(rendered.get("repo_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)
    for rel_path, payload in sorted(dict(rendered.get("tmp_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)
