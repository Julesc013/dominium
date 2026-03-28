"""Deterministic CONCURRENCY-CONTRACT-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from tools.audit.arch_audit_common import (
    build_concurrency_scan_report,
    render_concurrency_scan_report,
    run_arch_audit,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "CONCURRENCY0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "engine", "CONCURRENCY_DETERMINISM_CONTRACT.md")
SCAN_REPORT_DOC_REL = os.path.join("docs", "audit", "CONCURRENCY_SCAN_REPORT.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "CONCURRENCY_CONTRACT_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "concurrency_contract_report.json")
POLICY_REGISTRY_REL = os.path.join("data", "registries", "concurrency_policy_registry.json")
CANONICAL_MERGE_REL = os.path.join("engine", "concurrency", "canonical_merge.py")
RULE_TRUTH = "INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE"
RULE_DERIVED = "INV-PARALLEL-DERIVED-MUST-CANONICALIZE"
LAST_REVIEWED = "2026-03-14"

ALLOWED_PARALLEL_ZONES = {
    "appshell/ipc/ipc_endpoint_server.py": "Dedicated local IPC serving thread; no truth mutation.",
    "appshell/supervisor/supervisor_engine.py": "Derived log/status aggregation only; merge order canonicalized before persistence.",
    "tools/xstack/core/scheduler.py": "Validation and audit execution only; ready and final results are canonically ordered.",
}
FORBIDDEN_PARALLEL_ZONES = {
    "tools/xstack/sessionx/process_runtime.py": "Authoritative state mutation must remain deterministic and must not depend on thread completion order.",
    "tools/xstack/sessionx/scheduler.py": "Truth execution may not become parallel without an explicit deterministic shard-merge contract.",
    "src/process/": "Canonical process execution remains ordered truth execution.",
    "src/field/": "Field mutation is authoritative and may not race.",
    "src/fields/": "Field mutation is authoritative and may not race.",
    "src/logic/": "Logic truth evaluation may not depend on scheduling.",
    "src/time/": "Canonical time and proof paths may not depend on thread timing.",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _policy_rows(payload: Mapping[str, object] | None) -> list[dict]:
    rows = list(_as_map(_as_map(payload).get("record")).get("concurrency_policies") or [])
    return sorted((dict(row) for row in rows if isinstance(row, Mapping)), key=lambda row: _token(row.get("policy_id")))


def build_concurrency_contract_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    arch_report = run_arch_audit(root)
    concurrency_scan = build_concurrency_scan_report(arch_report)
    policy_registry = _read_json(os.path.join(root, POLICY_REGISTRY_REL))
    policy_rows = _policy_rows(policy_registry)
    report = {
        "report_id": "concurrency.contract.v1",
        "result": _token(concurrency_scan.get("result")) or "complete",
        "release_status": _token(concurrency_scan.get("release_status")) or "pass",
        "last_reviewed": LAST_REVIEWED,
        "concurrency_scan_report": dict(concurrency_scan),
        "concurrency_policy_registry_hash": canonical_sha256(policy_registry) if policy_registry else "",
        "concurrency_policy_ids": [_token(row.get("policy_id")) for row in policy_rows if _token(row.get("policy_id"))],
        "allowed_parallel_zones": dict(ALLOWED_PARALLEL_ZONES),
        "forbidden_parallel_zones": dict(FORBIDDEN_PARALLEL_ZONES),
        "ready_for_observability_0": not bool(concurrency_scan.get("blocking_finding_count", 0)),
        "ready_for_store_gc_0": not bool(concurrency_scan.get("blocking_finding_count", 0)),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_concurrency_contract_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    concurrency_scan = _as_map(payload.get("concurrency_scan_report"))
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned concurrency policies and shard-merge execution contracts.",
        "",
        "# Concurrency Contract Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- concurrency_policy_registry_hash: `{}`".format(_token(payload.get("concurrency_policy_registry_hash"))),
        "- concurrency_scan_fingerprint: `{}`".format(_token(concurrency_scan.get("deterministic_fingerprint"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Allowed Parallel Zones",
        "",
    ]
    for rel_path in sorted(_as_map(payload.get("allowed_parallel_zones")).keys()):
        lines.append("- `{}`: {}".format(_token(rel_path), _token(_as_map(payload.get("allowed_parallel_zones")).get(rel_path))))
    lines.extend(["", "## Forbidden Zones", ""])
    for rel_path in sorted(_as_map(payload.get("forbidden_parallel_zones")).keys()):
        lines.append("- `{}`: {}".format(_token(rel_path), _token(_as_map(payload.get("forbidden_parallel_zones")).get(rel_path))))
    lines.extend(["", "## Concurrency Policies", ""])
    for policy_id in list(payload.get("concurrency_policy_ids") or []):
        lines.append("- `{}`".format(_token(policy_id)))
    lines.extend(
        [
            "",
            "## Enforcement Coverage",
            "",
            "- ARCH-AUDIT concurrency checks: `parallel_truth_scan`, `parallel_output_scan`, `truth_atomic_scan`",
            "- RepoX rules: `INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE`, `INV-PARALLEL-DERIVED-MUST-CANONICALIZE`",
            "- AuditX analyzers: `E528`, `E529`",
            "- TestX coverage: derived merge canonicalization, validation merge canonicalization, worker invariance, threaded truth fixture detection",
            "",
            "## Readiness",
            "",
            "- OBSERVABILITY-0: `{}`".format("ready" if bool(payload.get("ready_for_observability_0", False)) else "blocked"),
            "- STORE-GC-0: `{}`".format("ready" if bool(payload.get("ready_for_store_gc_0", False)) else "blocked"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_concurrency_contract_outputs(repo_root: str) -> dict:
    root = _norm(repo_root)
    report = build_concurrency_contract_report(root)
    concurrency_scan = _as_map(report.get("concurrency_scan_report"))
    return {
        "report": report,
        "retro_audit_doc_path": _norm_rel(os.path.join(root, RETRO_AUDIT_DOC_REL)),
        "doctrine_doc_path": _norm_rel(os.path.join(root, DOCTRINE_DOC_REL)),
        "scan_report_doc_path": _norm_rel(_write_text(os.path.join(root, SCAN_REPORT_DOC_REL), render_concurrency_scan_report(concurrency_scan))),
        "baseline_doc_path": _norm_rel(_write_text(os.path.join(root, BASELINE_DOC_REL), render_concurrency_contract_baseline(report))),
        "report_json_path": _norm_rel(_write_json(os.path.join(root, REPORT_JSON_REL), report)),
    }


def concurrency_contract_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    report = build_concurrency_contract_report(root)
    violations = []
    for rel_path, message, rule_id in (
        (RETRO_AUDIT_DOC_REL, "concurrency retro audit doc is required", RULE_TRUTH),
        (DOCTRINE_DOC_REL, "concurrency determinism contract doc is required", RULE_TRUTH),
        (POLICY_REGISTRY_REL, "concurrency policy registry is required", RULE_TRUTH),
        (CANONICAL_MERGE_REL, "canonical merge utility is required for parallel derived and validation outputs", RULE_DERIVED),
        (BASELINE_DOC_REL, "concurrency baseline doc is required", RULE_DERIVED),
        (os.path.join("tools", "engine", "concurrency_contract_common.py"), "concurrency helper is required", RULE_DERIVED),
        (os.path.join("tools", "engine", "tool_run_concurrency_contract.py"), "concurrency runner is required", RULE_DERIVED),
    ):
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": rel_path, "rule_id": rule_id})
    for rel_path, token, message, rule_id in (
        ("appshell/supervisor/supervisor_engine.py", "canonicalize_parallel_mapping_rows(", "supervisor derived log merge must canonicalize output ordering", RULE_DERIVED),
        ("appshell/supervisor/supervisor_engine.py", "build_field_sort_key(", "supervisor derived log merge must use the canonical merge key builder", RULE_DERIVED),
        ("tools/xstack/core/scheduler.py", "ready.sort(", "parallel validation scheduler must canonicalize ready-node ordering", RULE_DERIVED),
        ("tools/xstack/core/scheduler.py", "ordered = sorted(", "parallel validation scheduler must canonicalize final result ordering", RULE_DERIVED),
        ("tools/xstack/sessionx/scheduler.py", "\"worker_count_effective\": 1", "truth scheduler must not silently enable parallel truth execution", RULE_TRUTH),
    ):
        text = ""
        try:
            with open(os.path.join(root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            pass
        if token in text:
            continue
        violations.append({"code": "missing_integration_hook", "message": message, "file_path": rel_path, "rule_id": rule_id})
    if _token(report.get("result")) != "complete":
        for row in list(_as_map(report.get("concurrency_scan_report")).get("blocking_findings") or []):
            item = dict(row or {})
            category = _token(item.get("category"))
            rule_id = RULE_DERIVED if category == "concurrency.parallel_output" else RULE_TRUTH
            violations.append(
                {
                    "code": "blocking_concurrency_scan",
                    "message": _token(item.get("message")) or "concurrency contract scan failed",
                    "file_path": _token(item.get("path")) or BASELINE_DOC_REL,
                    "rule_id": rule_id,
                }
            )
    return violations


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "POLICY_REGISTRY_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "SCAN_REPORT_DOC_REL",
    "RULE_DERIVED",
    "RULE_TRUTH",
    "build_concurrency_contract_report",
    "concurrency_contract_violations",
    "render_concurrency_contract_baseline",
    "write_concurrency_contract_outputs",
]
