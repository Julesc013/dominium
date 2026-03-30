#!/usr/bin/env python3
"""Deterministic Xi-7 CI guard helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.engine.numeric_discipline_common import build_numeric_discipline_report  # noqa: E402
from tools.review.xi6_common import (  # noqa: E402
    ARCH_UPDATE_TAG,
    build_architecture_drift_report,
    build_boundary_findings,
    build_single_engine_findings,
    build_ui_truth_leak_findings,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


PROFILE_DIR_REL = "tools/xstack/ci/profiles"
GATE_DEFINITIONS_REL = "data/xstack/gate_definitions.json"
CI_REPORT_JSON_REL = "data/audit/ci_run_report.json"
CI_REPORT_MD_REL = "docs/audit/CI_RUN_REPORT.md"
WORKFLOW_REL = ".github/workflows/ci.yml"

ENTRYPOINT_REL = "tools/xstack/ci/xstack_ci_entrypoint"
ENTRYPOINT_PY_REL = "tools/xstack/ci/xstack_ci_entrypoint.py"
ENTRYPOINT_PS1_REL = "tools/xstack/ci/xstack_ci_entrypoint.ps1"

CI_GUARDRAILS_DOC_REL = "docs/xstack/CI_GUARDRAILS.md"
ARCH_DRIFT_POLICY_DOC_REL = "docs/xstack/ARCH_DRIFT_POLICY.md"

REPOX_RULE_IDS = (
    "INV-NO-SRC-DIRECTORY",
    "INV-ARCH-GRAPH-V1-PRESENT",
    "INV-MODULE-BOUNDARIES-RESPECTED",
    "INV-SINGLE-CANONICAL-ENGINES",
)

AUDITX_DETECTOR_IDS = (
    "E560_ARCHITECTURE_DRIFT_SMELL",
    "E561_FORBIDDEN_DEPENDENCY_SMELL",
    "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL",
    "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL",
    "AUDITX_NUMERIC_DISCIPLINE_SCAN",
    "E564_MISSING_CI_GUARD_SMELL",
)

PROFILE_IDS = ("FAST", "STRICT", "FULL")

REQUIRED_CI_GUARD_PATHS = (
    ENTRYPOINT_REL,
    ENTRYPOINT_PY_REL,
    ENTRYPOINT_PS1_REL,
    "tools/xstack/ci/profiles/FAST.json",
    "tools/xstack/ci/profiles/STRICT.json",
    "tools/xstack/ci/profiles/FULL.json",
    GATE_DEFINITIONS_REL,
    CI_GUARDRAILS_DOC_REL,
    ARCH_DRIFT_POLICY_DOC_REL,
    WORKFLOW_REL,
)


class Xi7InputsMissing(RuntimeError):
    """Raised when Xi-7 cannot proceed safely."""


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(path: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(path or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _write_json(repo_root: str, rel_path: str, payload: Mapping[str, object]) -> str:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return abs_path


def _write_text(repo_root: str, rel_path: str, text: str) -> str:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return abs_path


def _remove_if_exists(repo_root: str, rel_path: str) -> None:
    abs_path = _repo_abs(repo_root, rel_path)
    if os.path.isfile(abs_path):
        os.remove(abs_path)


def _read_json(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise Xi7InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": [rel_path]},
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _python_env(repo_root: str) -> dict[str, str]:
    del repo_root
    # Child audit/validation tools already derive repo root from cwd/script path.
    # Prepending the repo root to PYTHONPATH changes import precedence and makes
    # long-running disaster/archive validation paths unstable on Windows.
    return dict(os.environ)


def _sorted_unique_strings(values: Iterable[object]) -> list[str]:
    return sorted({_token(value) for value in list(values or []) if _token(value)})


def _payload_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _report_mtime_ns(abs_path: str) -> int | None:
    try:
        return os.stat(abs_path).st_mtime_ns
    except OSError:
        return None


def _apply_gate_report_payload(
    payload: dict[str, object],
    parsed: Mapping[str, object],
    *,
    report_refreshed: bool | None,
) -> dict[str, object]:
    item = dict(parsed or {})
    if item:
        payload["stdout_json"] = item
    for field_name in (
        "result",
        "deterministic_fingerprint",
        "error_count",
        "warning_count",
        "finding_count",
        "blocking_finding_count",
        "report_json_path",
        "report_doc_path",
        "release_status",
    ):
        value = item.get(field_name)
        if value not in ("", None):
            payload[field_name] = value
    if report_refreshed is False:
        payload["status"] = "fail"
        payload["failure_reason"] = "stale_report_file"
        return payload
    result_token = _token(item.get("result")).lower()
    if result_token and result_token not in {"complete", "pass", "success", "skipped"}:
        payload["status"] = "fail"
        payload["failure_reason"] = "report_result={}".format(result_token)
        return payload
    release_status = _token(item.get("release_status")).lower()
    if release_status and release_status not in {"complete", "pass", "success"}:
        payload["status"] = "fail"
        payload["failure_reason"] = "release_status={}".format(release_status)
        return payload
    if int(item.get("error_count", 0) or 0) > 0:
        payload["status"] = "fail"
        payload["failure_reason"] = "report_error_count"
        return payload
    if int(item.get("blocking_finding_count", 0) or 0) > 0:
        payload["status"] = "fail"
        payload["failure_reason"] = "report_blocking_finding_count"
    return payload


def ensure_xi7_inputs(repo_root: str) -> None:
    missing = []
    for rel_path in (
        "data/architecture/architecture_graph.v1.json",
        "data/architecture/module_boundary_rules.v1.json",
        "data/architecture/single_engine_registry.json",
        "docs/audit/XI_6_FINAL.md",
        "tools/xstack/repox/check.py",
        "tools/auditx/auditx.py",
        "tools/xstack/testx/runner.py",
        "docs/canon/constitution_v1.md",
        "docs/canon/glossary_v1.md",
        "AGENTS.md",
    ):
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    if missing:
        raise Xi7InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": sorted(set(missing))},
                indent=2,
                sort_keys=True,
            )
        )


def load_gate_definitions(repo_root: str) -> dict[str, object]:
    return _read_json(repo_root, GATE_DEFINITIONS_REL)


def load_profile_definition(repo_root: str, profile: str) -> dict[str, object]:
    token = _token(profile).upper()
    if token not in PROFILE_IDS:
        raise ValueError("unsupported profile: {}".format(profile))
    return _read_json(repo_root, "{}/{}.json".format(PROFILE_DIR_REL, token))


def validate_gate_definitions(payload: Mapping[str, object]) -> list[str]:
    item = dict(payload or {})
    errors: list[str] = []
    if _token(item.get("report_id")) != "xstack.ci.gate_definitions.v1":
        errors.append("report_id drifted")
    profile_rows = {str(dict(row or {}).get("profile_id", "")).strip() for row in list(item.get("profiles") or [])}
    missing_profiles = sorted(set(PROFILE_IDS) - profile_rows)
    if missing_profiles:
        errors.append("missing profiles: {}".format(", ".join(missing_profiles)))
    main_policy = dict(item.get("main_branch_policy") or {})
    if _token(main_policy.get("required_profile")) != "STRICT":
        errors.append("main_branch_policy.required_profile must be STRICT")
    repox_rows = {str(dict(row or {}).get("rule_id", "")).strip() for row in list(item.get("repox_rules") or [])}
    for rule_id in REPOX_RULE_IDS + ("INV-XSTACK-CI-MUST-RUN", "INV-STRICT-MUST-PASS-FOR-MAIN"):
        if rule_id not in repox_rows:
            errors.append("missing RepoX rule {}".format(rule_id))
    audit_rows = {str(dict(row or {}).get("detector_id", "")).strip() for row in list(item.get("auditx_detectors") or [])}
    for detector_id in AUDITX_DETECTOR_IDS:
        if detector_id not in audit_rows:
            errors.append("missing AuditX detector {}".format(detector_id))
    validation_rows = {str(dict(row or {}).get("gate_id", "")).strip() for row in list(item.get("validation_gates") or [])}
    for gate_id in (
        "validate_strict",
        "arch_audit_2",
        "omega_1_worldgen_lock",
        "omega_2_baseline_universe",
        "omega_3_gameplay_loop",
        "omega_4_disaster_suite",
        "omega_5_ecosystem_verify",
        "omega_6_update_sim",
        "convergence_gate",
        "performance_envelope",
        "store_verify",
        "store_gc",
        "archive_verify",
    ):
        if gate_id not in validation_rows:
            errors.append("missing validation gate {}".format(gate_id))
    return errors


def build_ci_guard_violations(repo_root: str) -> list[dict[str, object]]:
    root = _repo_root(repo_root)
    violations: list[dict[str, object]] = []
    for rel_path in REQUIRED_CI_GUARD_PATHS:
        if os.path.exists(_repo_abs(root, rel_path)):
            continue
        violations.append(
            {
                "rule_id": "INV-XSTACK-CI-MUST-RUN",
                "code": "missing_required_ci_guard_surface",
                "file_path": rel_path,
                "message": "required Xi-7 CI guard surface is missing",
                "remediation": "restore the Xi-7 CI entrypoint, profile, gate definition, docs, and workflow wiring",
            }
        )
    if violations:
        return sorted(violations, key=lambda item: (_token(item.get("rule_id")), _norm_rel(item.get("file_path")), _token(item.get("code"))))

    gate_definitions = load_gate_definitions(root)
    for message in validate_gate_definitions(gate_definitions):
        violations.append(
            {
                "rule_id": "INV-XSTACK-CI-MUST-RUN",
                "code": "gate_definitions_invalid",
                "file_path": GATE_DEFINITIONS_REL,
                "message": message,
                "remediation": "repair data/xstack/gate_definitions.json so Xi-7 CI metadata matches the committed guard surface",
            }
        )

    with open(_repo_abs(root, WORKFLOW_REL), "r", encoding="utf-8") as handle:
        workflow_norm = handle.read().replace("\r\n", "\n")
    if ENTRYPOINT_PY_REL not in workflow_norm:
        violations.append(
            {
                "rule_id": "INV-XSTACK-CI-MUST-RUN",
                "code": "workflow_missing_xstack_ci_entrypoint",
                "file_path": WORKFLOW_REL,
                "message": "GitHub workflow must invoke the Xi-7 XStack CI entrypoint",
                "remediation": "wire .github/workflows/ci.yml through tools/xstack/ci/xstack_ci_entrypoint.py",
            }
        )
    for profile_id in PROFILE_IDS:
        profile_token = "--profile {}".format(profile_id)
        if profile_token in workflow_norm:
            continue
        violations.append(
            {
                "rule_id": "INV-XSTACK-CI-MUST-RUN",
                "code": "workflow_missing_profile",
                "file_path": WORKFLOW_REL,
                "message": "GitHub workflow must expose the {} Xi-7 profile".format(profile_id),
                "remediation": "add a deterministic workflow lane that runs the {} profile through the Xi-7 entrypoint".format(profile_id),
            }
        )
    if "--profile STRICT" not in workflow_norm:
        violations.append(
            {
                "rule_id": "INV-STRICT-MUST-PASS-FOR-MAIN",
                "code": "workflow_missing_strict_main_guard",
                "file_path": WORKFLOW_REL,
                "message": "main merge lanes must run the Xi-7 STRICT profile",
                "remediation": "wire the verify or main-protection lane through --profile STRICT",
            }
        )
    main_policy = dict(gate_definitions.get("main_branch_policy") or {})
    if _token(main_policy.get("required_profile")) != "STRICT":
        violations.append(
            {
                "rule_id": "INV-STRICT-MUST-PASS-FOR-MAIN",
                "code": "gate_definitions_missing_strict_main_policy",
                "file_path": GATE_DEFINITIONS_REL,
                "message": "gate definitions must require STRICT before merge to main",
                "remediation": "set main_branch_policy.required_profile to STRICT",
            }
        )

    with open(_repo_abs(root, CI_GUARDRAILS_DOC_REL), "r", encoding="utf-8") as handle:
        ci_docs = handle.read().replace("\r\n", "\n")
    if "tools/xstack/ci/xstack_ci_entrypoint --profile FAST" not in ci_docs:
        violations.append(
            {
                "rule_id": "INV-XSTACK-CI-MUST-RUN",
                "code": "docs_missing_local_fast_command",
                "file_path": CI_GUARDRAILS_DOC_REL,
                "message": "CI guard docs must show the local FAST entrypoint command",
                "remediation": "document tools/xstack/ci/xstack_ci_entrypoint --profile FAST in docs/xstack/CI_GUARDRAILS.md",
            }
        )

    return sorted(violations, key=lambda item: (_token(item.get("rule_id")), _norm_rel(item.get("file_path")), _token(item.get("code"))))


def _provisional_allowances(repo_root: str, scope: str) -> list[dict[str, object]]:
    payload = load_gate_definitions(repo_root)
    return [
        dict(item or {})
        for item in list(payload.get("provisional_allowances") or [])
        if _token(dict(item or {}).get("scope")) == _token(scope)
    ]


def _is_allowed_architecture_drift(report: Mapping[str, object], allowances: Iterable[Mapping[str, object]]) -> bool:
    module_delta = sorted({_token(item) for item in list(report.get("module_delta_preview") or []) if _token(item)})
    if not module_delta:
        return False
    allowed = sorted({_token(dict(item or {}).get("allowed_module_id")) for item in list(allowances or []) if _token(dict(item or {}).get("allowed_module_id"))})
    return bool(allowed) and module_delta == allowed


def _filter_boundary_rows(repo_root: str, rows: Iterable[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    allowances = _provisional_allowances(repo_root, "module_boundary")
    allowed: list[dict[str, object]] = []
    blocking: list[dict[str, object]] = []
    for row in rows:
        item = dict(row or {})
        matched = False
        for allowance in allowances:
            allowance_item = dict(allowance or {})
            if (
                _token(item.get("module_id")) == _token(allowance_item.get("allowed_module_id"))
                and _token(item.get("dependency_module_id")) == _token(allowance_item.get("allowed_dependency_module_id"))
            ):
                matched = True
                break
            if (
                _token(item.get("module_id")) == _token(allowance_item.get("allowed_module_id"))
                and _token(allowance_item.get("allowed_dependency_module_id")) == ""
            ):
                matched = True
                break
        if matched:
            allowed.append(item)
        else:
            blocking.append(item)
    return blocking, allowed


def _run_subprocess_gate(
    repo_root: str,
    gate_id: str,
    command: list[str],
    *,
    optional: bool = False,
    capture_output: bool = True,
    report_json_rel: str = "",
    report_doc_rel: str = "",
) -> dict[str, object]:
    report_before_mtime_ns = None
    report_path = ""
    if report_json_rel:
        report_path = _repo_abs(repo_root, report_json_rel)
        report_before_mtime_ns = _report_mtime_ns(report_path)
    run_kwargs: dict[str, object] = {
        "args": command,
        "cwd": repo_root,
        "env": _python_env(repo_root),
        "text": True,
        "errors": "replace",
        "check": False,
    }
    if capture_output:
        run_kwargs["stdout"] = subprocess.PIPE
        run_kwargs["stderr"] = subprocess.STDOUT
    else:
        run_kwargs["stdout"] = subprocess.DEVNULL
        run_kwargs["stderr"] = subprocess.DEVNULL
    completed = subprocess.run(**run_kwargs)
    payload: dict[str, object] = {
        "gate_id": gate_id,
        "command": command,
        "optional": optional,
        "returncode": int(completed.returncode),
        "status": "pass" if completed.returncode == 0 else "fail",
    }
    if report_json_rel:
        payload["report_json_path"] = _norm_rel(report_json_rel)
    if report_doc_rel:
        payload["report_doc_path"] = _norm_rel(report_doc_rel)
    if report_json_rel:
        if os.path.isfile(report_path):
            parsed = _read_json(repo_root, report_json_rel)
            if parsed:
                payload = _apply_gate_report_payload(
                    payload,
                    parsed,
                    report_refreshed=_report_mtime_ns(report_path) != report_before_mtime_ns,
                )
                return payload
        payload["status"] = "fail"
        payload["failure_reason"] = "missing_report_file"
        return payload
    text = str(getattr(completed, "stdout", "") or "").strip()
    if text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {}
        if isinstance(parsed, dict):
            payload = _apply_gate_report_payload(payload, parsed, report_refreshed=None)
        else:
            payload["stdout_excerpt"] = text.splitlines()[-20:]
    return payload


def _rule_result(rule_id: str, status: str, findings: list[dict[str, object]], *, evidence: Iterable[object] | None = None) -> dict[str, object]:
    payload = {
        "rule_id": rule_id,
        "status": status,
        "finding_count": len(findings),
        "findings": findings,
        "evidence": _sorted_unique_strings(evidence or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_fingerprint(payload)
    return payload


def _run_no_src_directory_rule(repo_root: str) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    evidence = []
    report_path = _repo_abs(repo_root, "data/restructure/xi5x2_postmove_residual_src_report.json")
    if os.path.isfile(report_path):
        report = _read_json(repo_root, "data/restructure/xi5x2_postmove_residual_src_report.json")
        if int(report.get("dangerous_shadow_root_count", 0) or 0) != 0:
            findings.append(
                {
                    "file_path": "data/restructure/xi5x2_postmove_residual_src_report.json",
                    "message": "dangerous shadow roots remain after Xi-5x2",
                    "remediation": "resolve remaining dangerous shadow roots before continuing the Xi-7 lane",
                }
            )
        for rel_path in list(report.get("unexpected_runtime_critical_src_paths") or []):
            findings.append(
                {
                    "file_path": _norm_rel(rel_path),
                    "message": "runtime-critical src path reappeared",
                    "remediation": "remove or reclassify the reintroduced runtime-critical src path before merge",
                }
            )
        evidence.extend(
            [
                "dangerous_shadow_root_count={}".format(int(report.get("dangerous_shadow_root_count", 0) or 0)),
                "top_level_src_file_count={}".format(int(report.get("top_level_src_file_count", 0) or 0)),
                "runtime_critical_src_count={}".format(len(list(report.get("unexpected_runtime_critical_src_paths") or []))),
            ]
        )
    for rel_path in ("src", "app/src"):
        if os.path.isdir(_repo_abs(repo_root, rel_path)):
            findings.append(
                {
                    "file_path": rel_path,
                    "message": "forbidden generic src root exists",
                    "remediation": "remove the generic src root and route files into canonical domains",
                }
            )
    return _rule_result(
        "INV-NO-SRC-DIRECTORY",
        "pass" if not findings else "fail",
        findings,
        evidence=evidence,
    )


def _run_arch_graph_present_rule(repo_root: str) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    for rel_path in (
        "data/architecture/architecture_graph.v1.json",
        "data/architecture/module_registry.v1.json",
        "data/architecture/module_boundary_rules.v1.json",
        "data/architecture/single_engine_registry.json",
    ):
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            findings.append(
                {
                    "file_path": rel_path,
                    "message": "Xi-6 frozen architecture artifact is missing",
                    "remediation": "restore the Xi-6 frozen architecture artifact before continuing CI",
            }
        )
    drift_report = build_architecture_drift_report(repo_root)
    if _token(drift_report.get("status")).lower() != "pass" and (not _is_allowed_architecture_drift(drift_report, _provisional_allowances(repo_root, "architecture_drift"))):
        findings.append(
            {
                "file_path": "data/architecture/architecture_graph.v1.json",
                "message": _token(drift_report.get("reason")) or "live architecture graph drifted from Xi-6 freeze",
                "remediation": "attach ARCH-GRAPH-UPDATE and refresh the Xi-6 freeze intentionally",
            }
        )
    return _rule_result(
        "INV-ARCH-GRAPH-V1-PRESENT",
        "pass" if not findings else "fail",
        findings,
        evidence=[
            "drift_status={}".format(_token(drift_report.get("status")) or "unknown"),
            "frozen_content_hash={}".format(_token(drift_report.get("frozen_content_hash"))),
            "live_content_hash={}".format(_token(drift_report.get("live_content_hash"))),
        ],
    )


def _run_module_boundaries_rule(repo_root: str) -> dict[str, object]:
    blocking_rows, allowed_rows = _filter_boundary_rows(repo_root, build_boundary_findings(repo_root))
    findings = [
        {
            "file_path": _token(row.get("file_path")),
            "message": _token(row.get("message")) or "forbidden module dependency detected",
            "remediation": _token(row.get("remediation")) or "remove or isolate the forbidden dependency through a declared boundary surface",
        }
        for row in blocking_rows
    ]
    return _rule_result(
        "INV-MODULE-BOUNDARIES-RESPECTED",
        "pass" if not findings else "fail",
        findings,
        evidence=["known_exception_count={}".format(len(allowed_rows))],
    )


def _run_single_engine_rule(repo_root: str) -> dict[str, object]:
    findings = [
        {
            "file_path": _token(row.get("file_path")),
            "message": _token(row.get("message")) or "duplicate semantic engine detected",
            "remediation": _token(row.get("remediation")) or "remove or quarantine the duplicate semantic engine",
        }
        for row in build_single_engine_findings(repo_root)
    ]
    return _rule_result(
        "INV-SINGLE-CANONICAL-ENGINES",
        "pass" if not findings else "fail",
        findings,
    )


def _run_ci_guard_rule(repo_root: str, rule_id: str) -> dict[str, object]:
    findings = [
        {
            "file_path": _token(row.get("file_path")),
            "message": _token(row.get("message")) or "Xi-7 CI guard is incomplete",
            "remediation": _token(row.get("remediation")) or "restore the Xi-7 CI guard surface",
        }
        for row in build_ci_guard_violations(repo_root)
        if _token(dict(row or {}).get("rule_id")) == rule_id
    ]
    return _rule_result(rule_id, "pass" if not findings else "fail", findings)


def run_repox_stage(repo_root: str, rule_ids: Iterable[object]) -> dict[str, object]:
    dispatch = {
        "INV-NO-SRC-DIRECTORY": _run_no_src_directory_rule,
        "INV-ARCH-GRAPH-V1-PRESENT": _run_arch_graph_present_rule,
        "INV-MODULE-BOUNDARIES-RESPECTED": _run_module_boundaries_rule,
        "INV-SINGLE-CANONICAL-ENGINES": _run_single_engine_rule,
        "INV-XSTACK-CI-MUST-RUN": lambda path: _run_ci_guard_rule(path, "INV-XSTACK-CI-MUST-RUN"),
        "INV-STRICT-MUST-PASS-FOR-MAIN": lambda path: _run_ci_guard_rule(path, "INV-STRICT-MUST-PASS-FOR-MAIN"),
    }
    rule_runs = []
    for rule_id in _sorted_unique_strings(rule_ids):
        runner = dispatch.get(rule_id)
        if runner is None:
            rule_runs.append(
                _rule_result(
                    rule_id,
                    "fail",
                    [
                        {
                            "file_path": GATE_DEFINITIONS_REL,
                            "message": "unknown Xi-7 RepoX rule requested by profile",
                            "remediation": "repair the Xi-7 profile and gate definitions",
                        }
                    ],
                )
            )
            continue
        rule_runs.append(runner(repo_root))
    payload = {
        "stage_id": "repox",
        "status": "pass" if all(_token(item.get("status")) == "pass" for item in rule_runs) else "fail",
        "finding_count": sum(int(item.get("finding_count", 0) or 0) for item in rule_runs),
        "rule_ids": [dict(item).get("rule_id") for item in rule_runs],
        "rule_runs": rule_runs,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_fingerprint(payload)
    return payload


def _render_audit_finding(detector_id: str, *, file_path: str, message: str, remediation: str, evidence: Iterable[object]) -> dict[str, object]:
    return {
        "detector_id": detector_id,
        "file_path": _norm_rel(file_path),
        "message": _token(message),
        "remediation": _token(remediation),
        "evidence": _sorted_unique_strings(evidence),
    }


def _run_architecture_drift_detector(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    report = build_architecture_drift_report(repo_root)
    findings: list[dict[str, object]] = []
    if _token(report.get("status")).lower() != "pass" and (not _is_allowed_architecture_drift(report, _provisional_allowances(repo_root, "architecture_drift"))):
        findings.append(
            _render_audit_finding(
                "E560_ARCHITECTURE_DRIFT_SMELL",
                file_path="data/architecture/architecture_graph.v1.json",
                message=_token(report.get("reason")) or "architecture graph drift detected without ARCH-GRAPH-UPDATE",
                remediation="prepare a ControlX architecture change plan and attach ARCH-GRAPH-UPDATE before changing the frozen graph",
                evidence=[
                    "required_tag={}".format(ARCH_UPDATE_TAG),
                    "frozen_content_hash={}".format(_token(report.get("frozen_content_hash"))),
                    "live_content_hash={}".format(_token(report.get("live_content_hash"))),
                ],
            )
        )
    gate = {
        "detector_id": "E560_ARCHITECTURE_DRIFT_SMELL",
        "finding_count": len(findings),
        "status": "pass" if not findings else "fail",
        "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
        "findings": findings,
    }
    return findings, gate


def _run_forbidden_dependency_detector(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    blocking_rows, allowed_rows = _filter_boundary_rows(repo_root, build_boundary_findings(repo_root))
    findings = [
        _render_audit_finding(
            "E561_FORBIDDEN_DEPENDENCY_SMELL",
            file_path=_token(row.get("file_path")),
            message=_token(row.get("message")) or "forbidden dependency detected",
            remediation=_token(row.get("remediation")) or "remove or isolate the forbidden dependency through an allowed boundary surface",
            evidence=[
                "module_id={}".format(_token(row.get("module_id"))),
                "dependency_module_id={}".format(_token(row.get("dependency_module_id"))),
                "line_number={}".format(int(row.get("line_number", 0) or 0)),
            ],
        )
        for row in blocking_rows
    ]
    gate = {
        "detector_id": "E561_FORBIDDEN_DEPENDENCY_SMELL",
        "finding_count": len(findings),
        "known_exception_count": len(allowed_rows),
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    return findings, gate


def _run_duplicate_engine_detector(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    findings = [
        _render_audit_finding(
            "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL",
            file_path=_token(row.get("file_path")),
            message=_token(row.get("message")) or "duplicate semantic engine detected",
            remediation=_token(row.get("remediation")) or "remove or quarantine the duplicate semantic engine implementation",
            evidence=[
                "engine_id={}".format(_token(row.get("engine_id"))),
                "module_id={}".format(_token(row.get("module_id"))),
                "line_number={}".format(int(row.get("line_number", 0) or 0)),
            ],
        )
        for row in build_single_engine_findings(repo_root)
    ]
    gate = {
        "detector_id": "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL",
        "finding_count": len(findings),
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    return findings, gate


def _run_ui_truth_leak_detector(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    findings = [
        _render_audit_finding(
            "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL",
            file_path=_token(row.get("file_path")),
            message=_token(row.get("message")) or "UI truth leak detected",
            remediation=_token(row.get("remediation")) or "route UI access through declared process/runtime surfaces rather than truth-facing modules",
            evidence=[
                "module_id={}".format(_token(row.get("module_id"))),
                "dependency_module_id={}".format(_token(row.get("dependency_module_id"))),
                "line_number={}".format(int(row.get("line_number", 0) or 0)),
            ],
        )
        for row in build_ui_truth_leak_findings(repo_root)
    ]
    gate = {
        "detector_id": "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL",
        "finding_count": len(findings),
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    return findings, gate


def _run_numeric_discipline_scan(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    report_path = _repo_abs(repo_root, "data/audit/numeric_discipline_report.json")
    if os.path.isfile(report_path):
        report = _read_json(repo_root, "data/audit/numeric_discipline_report.json")
        source_mode = "committed_report"
    else:
        report = build_numeric_discipline_report(repo_root)
        source_mode = "fresh_report"
    numeric_scan = dict(report.get("numeric_scan_report") or {})
    blocking_rows = list(numeric_scan.get("blocking_findings") or [])
    findings = [
        _render_audit_finding(
            "AUDITX_NUMERIC_DISCIPLINE_SCAN",
            file_path=_token(row.get("path")),
            message=_token(row.get("message")) or "numeric discipline violation detected",
            remediation="remove the non-deterministic numeric behavior or route it through a reviewed deterministic bridge",
            evidence=[
                "rule_id={}".format(_token(row.get("rule_id"))),
                "severity={}".format(_token(row.get("severity"))),
                _token(row.get("snippet")),
            ],
        )
        for row in blocking_rows
    ]
    gate = {
        "detector_id": "AUDITX_NUMERIC_DISCIPLINE_SCAN",
        "finding_count": len(findings),
        "known_exception_count": int(numeric_scan.get("known_exception_count", 0) or 0),
        "source_mode": source_mode,
        "status": "pass" if not findings else "fail",
        "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
        "findings": findings,
    }
    return findings, gate


def _run_missing_ci_guard_detector(repo_root: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    findings = [
        _render_audit_finding(
            "E564_MISSING_CI_GUARD_SMELL",
            file_path=_token(row.get("file_path")),
            message=_token(row.get("message")) or "Xi-7 CI guard surface is missing or incomplete",
            remediation=_token(row.get("remediation")) or "restore the missing Xi-7 CI guard surface before merging",
            evidence=[
                "rule_id={}".format(_token(row.get("rule_id"))),
                "code={}".format(_token(row.get("code"))),
            ],
        )
        for row in build_ci_guard_violations(repo_root)
    ]
    gate = {
        "detector_id": "E564_MISSING_CI_GUARD_SMELL",
        "finding_count": len(findings),
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    return findings, gate


def run_auditx_stage(repo_root: str, profile: str, detector_ids: Iterable[object]) -> dict[str, object]:
    del profile
    gate_runs: list[dict[str, object]] = []
    all_findings: list[dict[str, object]] = []
    for detector_id in _sorted_unique_strings(detector_ids):
        if detector_id == "E560_ARCHITECTURE_DRIFT_SMELL":
            findings, gate = _run_architecture_drift_detector(repo_root)
        elif detector_id == "E561_FORBIDDEN_DEPENDENCY_SMELL":
            findings, gate = _run_forbidden_dependency_detector(repo_root)
        elif detector_id == "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL":
            findings, gate = _run_duplicate_engine_detector(repo_root)
        elif detector_id == "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL":
            findings, gate = _run_ui_truth_leak_detector(repo_root)
        elif detector_id == "AUDITX_NUMERIC_DISCIPLINE_SCAN":
            findings, gate = _run_numeric_discipline_scan(repo_root)
        elif detector_id == "E564_MISSING_CI_GUARD_SMELL":
            findings, gate = _run_missing_ci_guard_detector(repo_root)
        else:
            findings = [
                _render_audit_finding(
                    detector_id,
                    file_path=GATE_DEFINITIONS_REL,
                    message="unknown AuditX detector requested by Xi-7 profile",
                    remediation="repair the Xi-7 gate definitions before rerunning CI",
                    evidence=["detector_id={}".format(detector_id)],
                )
            ]
            gate = {
                "detector_id": detector_id,
                "finding_count": len(findings),
                "status": "fail",
                "findings": findings,
            }
        gate_runs.append(gate)
        all_findings.extend(findings)
    payload = {
        "stage_id": "auditx",
        "status": "pass" if all(_token(item.get("status")) == "pass" for item in gate_runs) else "fail",
        "detector_ids": [dict(item).get("detector_id") for item in gate_runs],
        "gate_runs": gate_runs,
        "finding_count": len(all_findings),
        "findings": all_findings,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_fingerprint(payload)
    return payload


def _resolve_validation_specs(gate_definitions: Mapping[str, object], gate_ids: Iterable[object]) -> list[dict[str, object]]:
    catalog = {
        _token(dict(item or {}).get("gate_id")): dict(item or {})
        for item in list(gate_definitions.get("validation_gates") or [])
        if _token(dict(item or {}).get("gate_id"))
    }
    return [catalog[gate_id] for gate_id in _sorted_unique_strings(gate_ids) if gate_id in catalog]


def _gate_should_skip(repo_root: str, spec: Mapping[str, object]) -> tuple[bool, str]:
    missing_path = _token(spec.get("skip_if_missing_path"))
    if missing_path and (not os.path.exists(_repo_abs(repo_root, missing_path))):
        return True, "missing {}".format(missing_path)
    return False, ""


def _render_ci_run_report(report: Mapping[str, object]) -> str:
    payload = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-7",
        "Replacement Target: superseded by a later explicit CI guard profile revision only",
        "",
        "# CI Run Report",
        "",
        "- profile: `{}`".format(_token(payload.get("profile"))),
        "- result: `{}`".format(_token(payload.get("result"))),
        "- deterministic fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Stage Order",
        "",
    ]
    for stage in list(payload.get("stages") or []):
        item = dict(stage or {})
        lines.append("- `{}` -> `{}`".format(_token(item.get("stage_id")), _token(item.get("status"))))
    lines.extend(["", "## Findings", ""])
    finding_rows = []
    for stage in list(payload.get("stages") or []):
        item = dict(stage or {})
        if int(item.get("finding_count", 0) or 0) > 0:
            finding_rows.append("- `{}` findings: `{}`".format(_token(item.get("stage_id")), int(item.get("finding_count", 0) or 0)))
    lines.extend(finding_rows or ["- none"])
    lines.extend(["", "## Outputs", "", "- `{}`".format(CI_REPORT_JSON_REL), "- `{}`".format(CI_REPORT_MD_REL)])
    return "\n".join(lines) + "\n"


def _write_report_outputs(repo_root: str, report: Mapping[str, object]) -> None:
    _write_json(repo_root, CI_REPORT_JSON_REL, dict(report or {}))
    _write_text(repo_root, CI_REPORT_MD_REL, _render_ci_run_report(report))


def _failed_report(profile: str, stages: list[dict[str, object]], gate_definitions: Mapping[str, object], profile_def: Mapping[str, object]) -> dict[str, object]:
    report = {
        "report_id": "xstack.ci.run_report.v1",
        "profile": _token(profile),
        "result": "failed",
        "required_invariants": [
            "constitution_v1.md A1",
            "constitution_v1.md A8",
            "constitution_v1.md A10",
            "AGENTS.md §2",
            "AGENTS.md §5",
        ],
        "gate_definitions_fingerprint": _token(gate_definitions.get("deterministic_fingerprint")),
        "profile_fingerprint": _token(profile_def.get("deterministic_fingerprint")),
        "stages": stages,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _payload_fingerprint(report)
    return report


def run_ci_profile(repo_root: str, profile: str, *, testx_subset_override: Iterable[object] | None = None) -> dict[str, object]:
    root = _repo_root(repo_root)
    ensure_xi7_inputs(root)
    _remove_if_exists(root, CI_REPORT_JSON_REL)
    _remove_if_exists(root, CI_REPORT_MD_REL)
    gate_definitions = load_gate_definitions(root)
    profile_def = load_profile_definition(root, profile)
    gate_errors = validate_gate_definitions(gate_definitions)
    if gate_errors:
        raise Xi7InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi.missing_inputs",
                    "missing_inputs": [GATE_DEFINITIONS_REL],
                    "reason": "; ".join(gate_errors),
                },
                indent=2,
                sort_keys=True,
            )
        )

    token = _token(profile_def.get("profile_id")).upper()
    stage_order = list(profile_def.get("execution_order") or [])
    stages: list[dict[str, object]] = []

    if "repox" in stage_order:
        repox_stage = run_repox_stage(root, list(profile_def.get("repox_rule_ids") or []))
        stages.append(repox_stage)
        if repox_stage["status"] != "pass":
            report = _failed_report(token, stages, gate_definitions, profile_def)
            _write_report_outputs(root, report)
            return report

    if "auditx" in stage_order:
        audit_stage = run_auditx_stage(root, token, list(profile_def.get("auditx_detector_ids") or []))
        stages.append(audit_stage)
        if audit_stage["status"] != "pass":
            report = _failed_report(token, stages, gate_definitions, profile_def)
            _write_report_outputs(root, report)
            return report

    if "testx" in stage_order:
        subset_ids = _sorted_unique_strings(testx_subset_override or profile_def.get("testx_subset_ids") or [])
        command = [
            "python",
            "-B",
            "tools/xstack/testx/runner.py",
            "--repo-root",
            ".",
            "--profile",
            _token(profile_def.get("testx_profile")) or token,
            "--cache",
            _token(profile_def.get("testx_cache")) or "off",
        ]
        if subset_ids:
            command.extend(["--subset", ",".join(subset_ids)])
        testx_stage = {
            "stage_id": "testx",
            "status": "pass",
            "finding_count": 0,
            "subset_mode": _token(profile_def.get("testx_selection")),
            "subset_ids": subset_ids,
            "gate_runs": [_run_subprocess_gate(root, "testx_runner", command)],
            "deterministic_fingerprint": "",
        }
        if any(_token(item.get("status")) != "pass" for item in list(testx_stage.get("gate_runs") or [])):
            testx_stage["status"] = "fail"
        testx_stage["deterministic_fingerprint"] = _payload_fingerprint(testx_stage)
        stages.append(testx_stage)
        if testx_stage["status"] != "pass":
            report = _failed_report(token, stages, gate_definitions, profile_def)
            _write_report_outputs(root, report)
            return report

    if "validation_and_omega" in stage_order:
        gate_runs: list[dict[str, object]] = []
        for spec in _resolve_validation_specs(gate_definitions, list(profile_def.get("validation_gate_ids") or [])):
            gate_id = _token(spec.get("gate_id"))
            should_skip, reason = _gate_should_skip(root, spec)
            if should_skip:
                gate_runs.append(
                    {
                        "gate_id": gate_id,
                        "command": list(spec.get("command") or []),
                        "status": "skipped",
                        "optional": bool(spec.get("optional", False)),
                        "reason": reason,
                    }
                )
                continue
            command = [str(item) for item in list(spec.get("command") or [])]
            gate_runs.append(
                _run_subprocess_gate(
                    root,
                    gate_id,
                    command,
                    optional=bool(spec.get("optional", False)),
                    capture_output=not bool(spec.get("prefer_report_file", False)),
                    report_json_rel=_token(spec.get("report_json_rel")),
                    report_doc_rel=_token(spec.get("report_doc_rel")),
                )
            )
        validation_stage = {
            "stage_id": "validation_and_omega",
            "status": "pass" if all(_token(item.get("status")) in {"pass", "skipped"} for item in gate_runs) else "fail",
            "finding_count": len([item for item in gate_runs if _token(item.get("status")) == "fail"]),
            "gate_runs": gate_runs,
            "deterministic_fingerprint": "",
        }
        validation_stage["deterministic_fingerprint"] = _payload_fingerprint(validation_stage)
        stages.append(validation_stage)

    report = {
        "report_id": "xstack.ci.run_report.v1",
        "profile": token,
        "result": "complete" if all(_token(stage.get("status")) == "pass" for stage in stages) else "failed",
        "required_invariants": [
            "constitution_v1.md A1",
            "constitution_v1.md A8",
            "constitution_v1.md A10",
            "AGENTS.md §2",
            "AGENTS.md §5",
        ],
        "gate_definitions_fingerprint": _token(gate_definitions.get("deterministic_fingerprint")),
        "profile_fingerprint": _token(profile_def.get("deterministic_fingerprint")),
        "stages": stages,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _payload_fingerprint(report)
    _write_report_outputs(root, report)
    return report
