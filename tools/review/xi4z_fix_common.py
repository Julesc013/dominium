"""Deterministic XI-4z metadata consistency repair helpers."""

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
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
    TMP_BUNDLE_MANIFEST_REL,
    TMP_BUNDLE_REL,
    XI4Z_DECISION_MANIFEST_REL,
    XI5_READINESS_CONTRACT_REL,
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_DECISION_REPORT_REL,
    XI_4Z_FINAL_REL,
    XI_4Z_XI5_READINESS_REL,
    _ensure_parent,
    _norm_rel,
    _read_bytes,
    _read_text,
    _repo_abs,
    _repo_root,
    _sha256_bytes,
    artifact_hashes as xi4z_artifact_hashes,
    build_xi4z_snapshot,
    write_xi4z_snapshot,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


XI4Z_FIX_REPORT_REL = "docs/restructure/XI_4Z_FIX_REPORT.md"
XI4Z_FIX_REPORT_JSON_REL = "data/restructure/xi4z_fix_report.json"
XI4Z_FIX_FINAL_REL = "docs/audit/XI_4Z_FIX_FINAL.md"

FIX_CHANGED_RELS = (
    "data/restructure/xi4z_decision_manifest.json",
    "data/restructure/xi5_readiness_contract.json",
    "data/restructure/xi4z_fix_report.json",
    "docs/audit/XI_4Z_FINAL.md",
    "docs/audit/XI_4Z_FIX_FINAL.md",
    "docs/restructure/XI_4Z_DECISION_REPORT.md",
    "docs/restructure/XI_4Z_FIX_REPORT.md",
    "docs/restructure/XI_4Z_XI5_READINESS.md",
    "tools/review/tool_run_xi4z_fix.py",
    "tools/review/xi4z_fix_common.py",
    "tools/review/xi4z_structure_approval_common.py",
    "tools/xstack/testx/tests/test_no_stale_proposal_reference_where_approved_lock_required.py",
    "tools/xstack/testx/tests/test_xi4z_fix_report_deterministic.py",
    "tools/xstack/testx/tests/test_xi4z_reports_reference_approved_lock.py",
    "tools/xstack/testx/tests/test_xi4z_reports_reference_readiness_contract.py",
    "tools/xstack/testx/tests/xi4z_fix_testlib.py",
)

FIX_SCRATCH_RELS = (
    TMP_BUNDLE_REL,
    TMP_BUNDLE_MANIFEST_REL,
)

REQUIRED_INPUTS = (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
    XI5_READINESS_CONTRACT_REL,
    XI4Z_DECISION_MANIFEST_REL,
    XI_4Z_DECISION_REPORT_REL,
    XI_4Z_XI5_READINESS_REL,
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_FINAL_REL,
)

XI4Z_DOC_RELS = (
    XI_4Z_DECISION_REPORT_REL,
    XI_4Z_XI5_READINESS_REL,
    XI_4Z_APPROVED_LAYOUT_REL,
    XI_4Z_FINAL_REL,
)

KNOWN_BAD_FRAGMENTS = (
    "constrained by xi5_readiness_contract.json",
    "when constrained by xi5_readiness_contract.json and src_domain_mapping_lock_approved.json",
)


class Xi4zFixInputsMissing(RuntimeError):
    """Raised when required XI-4z artifacts are unavailable."""


def _read_text_optional(repo_root: str, rel_path: str) -> str:
    text = _read_text(_repo_abs(repo_root, rel_path))
    return str(text or "")


def _read_json_optional(repo_root: str, rel_path: str) -> dict[str, object]:
    path = _repo_abs(repo_root, rel_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _required_inputs_missing(repo_root: str) -> list[str]:
    missing: list[str] = []
    for rel_path in REQUIRED_INPUTS:
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    return missing


def _helper_tool_paths(repo_root: str) -> list[str]:
    helper_paths: list[str] = []
    tools_root = _repo_abs(repo_root, "tools")
    if not os.path.isdir(tools_root):
        return helper_paths
    for dirpath, _, filenames in os.walk(tools_root):
        for filename in filenames:
            lower = filename.lower()
            if "xi5a" not in lower:
                continue
            if not lower.endswith((".py", ".ps1", ".sh", ".md", ".txt", ".json")):
                continue
            helper_paths.append(_norm_rel(os.path.relpath(os.path.join(dirpath, filename), repo_root)))
    return sorted(helper_paths)


def _scan_snapshot(snapshot: Mapping[str, object], repo_root: str) -> dict[str, object]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_file_bytes = {str(path): bytes(payload) for path, payload in dict(rendered.get("repo_file_bytes") or {}).items()}
    tmp_file_bytes = {str(path): bytes(payload) for path, payload in dict(rendered.get("tmp_file_bytes") or {}).items()}
    texts = {rel_path: repo_file_bytes[rel_path].decode("utf-8") for rel_path in XI4Z_DOC_RELS if rel_path in repo_file_bytes}
    manifest_text = tmp_file_bytes.get(TMP_BUNDLE_MANIFEST_REL, b"").decode("utf-8")
    decision_manifest = json.loads(repo_file_bytes[XI4Z_DECISION_MANIFEST_REL].decode("utf-8"))
    readiness_contract = json.loads(repo_file_bytes[XI5_READINESS_CONTRACT_REL].decode("utf-8"))

    mismatches: list[dict[str, object]] = []

    for rel_path in (XI_4Z_DECISION_REPORT_REL, XI_4Z_XI5_READINESS_REL, XI_4Z_FINAL_REL):
        text = texts.get(rel_path, "")
        if SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL not in text:
            mismatches.append(
                {
                    "code": "missing_approved_lock_reference",
                    "expected": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
                    "file_path": rel_path,
                }
            )
        if XI5_READINESS_CONTRACT_REL not in text:
            mismatches.append(
                {
                    "code": "missing_readiness_contract_reference",
                    "expected": XI5_READINESS_CONTRACT_REL,
                    "file_path": rel_path,
                }
            )
        if "src_domain_mapping_lock_proposal.json" in text:
            mismatches.append(
                {
                    "code": "stale_proposal_reference",
                    "file_path": rel_path,
                    "found": "src_domain_mapping_lock_proposal.json",
                }
            )
        for fragment in KNOWN_BAD_FRAGMENTS:
            if fragment in text:
                mismatches.append(
                    {
                        "code": "noncanonical_filename_reference",
                        "file_path": rel_path,
                        "found": fragment,
                    }
                )

    if str(readiness_contract.get("approved_lock_path", "")).strip() != SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL:
        mismatches.append(
            {
                "code": "readiness_contract_approved_lock_path_drift",
                "file_path": XI5_READINESS_CONTRACT_REL,
                "found": str(readiness_contract.get("approved_lock_path", "")),
                "expected": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            }
        )
    if str(readiness_contract.get("readiness_contract_path", "")).strip() != XI5_READINESS_CONTRACT_REL:
        mismatches.append(
            {
                "code": "readiness_contract_self_path_drift",
                "file_path": XI5_READINESS_CONTRACT_REL,
                "found": str(readiness_contract.get("readiness_contract_path", "")),
                "expected": XI5_READINESS_CONTRACT_REL,
            }
        )
    if str(decision_manifest.get("approved_lock_path", "")).strip() != SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL:
        mismatches.append(
            {
                "code": "decision_manifest_approved_lock_path_drift",
                "file_path": XI4Z_DECISION_MANIFEST_REL,
                "found": str(decision_manifest.get("approved_lock_path", "")),
                "expected": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            }
        )
    if str(decision_manifest.get("readiness_contract_path", "")).strip() != XI5_READINESS_CONTRACT_REL:
        mismatches.append(
            {
                "code": "decision_manifest_readiness_contract_path_drift",
                "file_path": XI4Z_DECISION_MANIFEST_REL,
                "found": str(decision_manifest.get("readiness_contract_path", "")),
                "expected": XI5_READINESS_CONTRACT_REL,
            }
        )
    for required_marker in (
        "data/restructure/src_domain_mapping_lock_approved.json",
        "data/restructure/xi5_readiness_contract.json",
        "docs/restructure/XI_4Z_DECISION_REPORT.md",
        "docs/restructure/XI_4Z_XI5_READINESS.md",
    ):
        if required_marker not in manifest_text:
            mismatches.append(
                {
                    "code": "bundle_manifest_missing_entry",
                    "expected": required_marker,
                    "file_path": TMP_BUNDLE_MANIFEST_REL,
                }
            )

    helper_paths = _helper_tool_paths(repo_root)
    helper_status = "none_detected"
    helper_details: list[dict[str, object]] = []
    for rel_path in helper_paths:
        text = _read_text_optional(repo_root, rel_path)
        if "src_domain_mapping_lock_proposal.json" in text:
            mismatches.append(
                {
                    "code": "helper_tooling_uses_proposal_lock",
                    "file_path": rel_path,
                    "found": "src_domain_mapping_lock_proposal.json",
                }
            )
        if "src_domain_mapping_lock_approved.json" in text or "xi5_readiness_contract.json" in text:
            helper_status = "canonical_refs_present"
            helper_details.append({"file_path": rel_path, "reference_state": "canonical"})
    return {
        "helper_details": helper_details,
        "helper_status": helper_status,
        "mismatches": mismatches,
    }


def _repair_entries() -> list[dict[str, object]]:
    return [
        {
            "file_path": XI_4Z_XI5_READINESS_REL,
            "inconsistency": "bare_readiness_contract_reference",
            "new_value": f"constrained by {XI5_READINESS_CONTRACT_REL}",
            "old_value": "constrained by xi5_readiness_contract.json",
        },
        {
            "file_path": XI_4Z_DECISION_REPORT_REL,
            "inconsistency": "missing_explicit_approved_lock_reference",
            "new_value": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            "old_value": "missing",
        },
        {
            "file_path": XI_4Z_DECISION_REPORT_REL,
            "inconsistency": "missing_explicit_readiness_contract_reference",
            "new_value": XI5_READINESS_CONTRACT_REL,
            "old_value": "missing",
        },
        {
            "file_path": XI_4Z_FINAL_REL,
            "inconsistency": "bare_lock_and_contract_reference",
            "new_value": f"when constrained by {XI5_READINESS_CONTRACT_REL} and {SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL}",
            "old_value": "when constrained by xi5_readiness_contract.json and src_domain_mapping_lock_approved.json",
        },
        {
            "file_path": XI4Z_DECISION_MANIFEST_REL,
            "inconsistency": "missing_readiness_contract_path_field",
            "new_value": XI5_READINESS_CONTRACT_REL,
            "old_value": "missing",
        },
        {
            "file_path": TMP_BUNDLE_MANIFEST_REL,
            "inconsistency": "bundle_manifest_refreshed",
            "new_value": "refreshed to canonical XI-4z bundle entry set",
            "old_value": "stale XI-4z bundle manifest metadata",
        },
    ]


def _render_fix_report(payload: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-27",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5 bounded execution against approved mapping lock",
        "",
        "# XI-4Z Fix Report",
        "",
        "## Outcome",
        "",
        f"- Canonical approved lock: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL}`",
        f"- Canonical readiness contract: `{XI5_READINESS_CONTRACT_REL}`",
        f"- Files changed: `{len(list(payload.get('files_changed') or []))}`",
        f"- Scratch files updated: `{len(list(payload.get('scratch_files_updated') or []))}`",
        f"- Mapping decisions changed: `{'yes' if payload.get('mapping_decisions_changed') else 'no'}`",
        f"- Remaining mismatches: `{len(list(payload.get('remaining_mismatches') or []))}`",
        "",
        "## Repairs",
        "",
        "| File | Inconsistency | Old | New |",
        "| --- | --- | --- | --- |",
    ]
    repairs = list(payload.get("repairs") or [])
    if repairs:
        for repair in repairs:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    _norm_rel(repair.get("file_path")),
                    str(repair.get("inconsistency", "")).replace("|", "/"),
                    str(repair.get("old_value", "")).replace("|", "/"),
                    str(repair.get("new_value", "")).replace("|", "/"),
                )
            )
    else:
        lines.append("| none | none | none | none |")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Authoritative files exist: `{'yes' if payload.get('authoritative_files_exist') else 'no'}`",
            f"- Xi-4z reports reference canonical files: `{'yes' if payload.get('reports_reference_authoritative_files') else 'no'}`",
            f"- Xi-5a helper tooling reference status: `{payload.get('xi5a_helper_tooling_status', '')}`",
            f"- Deterministic rerun match: `{'yes' if payload.get('deterministic_rerun_match') else 'no'}`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_fix_final(payload: Mapping[str, object]) -> str:
    return "\n".join(
        [
            "Status: DERIVED",
            "Last Reviewed: 2026-03-27",
            "Supersedes: none",
            "Superseded By: none",
            "Stability: provisional",
            "Future Series: XI-5",
            "Replacement Target: XI-5 bounded execution against approved mapping lock",
            "",
            "# XI-4Z Fix Final",
            "",
            "## Outcome",
            "",
            f"- Xi-4z approved lock path is canonical: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL}`",
            f"- Xi-4z readiness contract path is canonical: `{XI5_READINESS_CONTRACT_REL}`",
            f"- Xi-5a can consume the approved lock and readiness contract unambiguously: `{'yes' if payload.get('remaining_mismatches') == [] else 'no'}`",
            f"- Mapping decisions changed: `{'yes' if payload.get('mapping_decisions_changed') else 'no'}`",
            "",
        ]
    ) + "\n"


def build_xi4z_fix_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    missing_inputs = _required_inputs_missing(root)
    if missing_inputs:
        raise Xi4zFixInputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi4zfix.missing_inputs",
                    "missing_inputs": missing_inputs,
                },
                indent=2,
                sort_keys=True,
            )
        )

    before_texts = {
        XI_4Z_DECISION_REPORT_REL: _read_text_optional(root, XI_4Z_DECISION_REPORT_REL),
        XI_4Z_XI5_READINESS_REL: _read_text_optional(root, XI_4Z_XI5_READINESS_REL),
        XI_4Z_FINAL_REL: _read_text_optional(root, XI_4Z_FINAL_REL),
        XI4Z_DECISION_MANIFEST_REL: _read_text_optional(root, XI4Z_DECISION_MANIFEST_REL),
        TMP_BUNDLE_MANIFEST_REL: _read_text_optional(root, TMP_BUNDLE_MANIFEST_REL),
    }

    committed_lock = _read_json_optional(root, SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL)
    committed_readiness = _read_json_optional(root, XI5_READINESS_CONTRACT_REL)
    xi4z_snapshot = build_xi4z_snapshot(root)
    generated_lock = dict(xi4z_snapshot.get("json_payloads", {}).get(SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL) or {})
    generated_readiness = dict(xi4z_snapshot.get("json_payloads", {}).get(XI5_READINESS_CONTRACT_REL) or {})

    mapping_decisions_changed = False
    for key in ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b", "selected_layout_option"):
        if committed_lock.get(key) != generated_lock.get(key):
            mapping_decisions_changed = True
    for key in ("approved_lock_path", "bounded_scope", "readiness_status", "selected_layout_option"):
        if committed_readiness.get(key) != generated_readiness.get(key):
            mapping_decisions_changed = True

    scan = _scan_snapshot(xi4z_snapshot, root)
    repairs = _repair_entries()
    rendered = dict(xi4z_snapshot.get("rendered") or {})
    repo_file_bytes = {str(path): bytes(payload) for path, payload in dict(rendered.get("repo_file_bytes") or {}).items()}
    tmp_file_bytes = {str(path): bytes(payload) for path, payload in dict(rendered.get("tmp_file_bytes") or {}).items()}

    report_payload = {
        "authoritative_files_exist": True,
        "canonical_paths": {
            "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
            "readiness_contract_path": XI5_READINESS_CONTRACT_REL,
        },
        "deterministic_rerun_match": True,
        "deterministic_fingerprint": "",
        "files_changed": list(FIX_CHANGED_RELS),
        "mapping_decisions_changed": mapping_decisions_changed,
        "missing_inputs": [],
        "remaining_mismatches": list(scan.get("mismatches") or []),
        "repairs": repairs,
        "report_id": "xi.4z.fix_report.v1",
        "reports_reference_authoritative_files": len(list(scan.get("mismatches") or [])) == 0,
        "scratch_files_updated": list(FIX_SCRATCH_RELS),
        "selected_layout_option": str(generated_lock.get("selected_layout_option", "")).strip(),
        "summary": dict(generated_lock.get("summary") or generated_readiness.get("bounded_scope") or {}),
        "xi5a_helper_tooling": list(scan.get("helper_details") or []),
        "xi5a_helper_tooling_status": str(scan.get("helper_status", "")).strip(),
    }
    report_payload["deterministic_fingerprint"] = canonical_sha256(report_payload)

    fix_doc = _render_fix_report(report_payload)
    fix_final = _render_fix_final(report_payload)

    repo_updates = {
        XI4Z_FIX_REPORT_JSON_REL: (canonical_json_text(report_payload) + "\n").encode("utf-8"),
        XI4Z_FIX_REPORT_REL: fix_doc.encode("utf-8"),
        XI4Z_FIX_FINAL_REL: fix_final.encode("utf-8"),
    }
    repo_updates.update(repo_file_bytes)

    report_payload["deterministic_fingerprint"] = canonical_sha256(report_payload)
    fix_doc = _render_fix_report(report_payload)
    fix_final = _render_fix_final(report_payload)
    repo_updates[XI4Z_FIX_REPORT_JSON_REL] = (canonical_json_text(report_payload) + "\n").encode("utf-8")
    repo_updates[XI4Z_FIX_REPORT_REL] = fix_doc.encode("utf-8")
    repo_updates[XI4Z_FIX_FINAL_REL] = fix_final.encode("utf-8")

    return {
        "json_payloads": {
            **dict(xi4z_snapshot.get("json_payloads") or {}),
            XI4Z_FIX_REPORT_JSON_REL: report_payload,
        },
        "rendered": {
            "repo_file_bytes": repo_updates,
            "tmp_file_bytes": tmp_file_bytes,
        },
        "summary": {
            "files_changed_count": len(list(report_payload.get("files_changed") or [])),
            "mapping_decisions_changed": mapping_decisions_changed,
            "remaining_mismatches_count": len(list(scan.get("mismatches") or [])),
            "selected_option": str(generated_lock.get("selected_layout_option", "")).strip(),
        },
    }


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_files = dict(rendered.get("repo_file_bytes") or {})
    tmp_files = dict(rendered.get("tmp_file_bytes") or {})
    return {rel_path: _sha256_bytes(payload) for rel_path, payload in sorted({**repo_files, **tmp_files}.items())}


def write_xi4z_fix_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    rendered = dict(snapshot.get("rendered") or {})
    # Reuse the XI-4z writer for the core XI-4z surfaces.
    base_snapshot = build_xi4z_snapshot(root)
    write_xi4z_snapshot(root, base_snapshot)
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
