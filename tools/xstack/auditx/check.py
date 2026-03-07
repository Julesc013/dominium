#!/usr/bin/env python3
"""XStack wrapper for the full AuditX semantic scan pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _severity_rank(token: str) -> int:
    value = str(token or "").strip().lower()
    if value == "warn":
        return 0
    if value == "fail":
        return 1
    if value == "refusal":
        return 2
    return 9


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")).strip().lower() for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


STRICT_PROMOTED_ANALYZERS = {
    "E179_INLINE_RESPONSE_CURVE_SMELL": "fail",
    "E208_DIRECT_VELOCITY_WRITE_SMELL": "fail",
    "E212_DIRECT_ENERGY_WRITE_SMELL": "fail",
    "E214_INLINE_DEGRADATION_SMELL": "fail",
    "E215_ENTROPY_BYPASS_SMELL": "fail",
    "E216_MISSING_TIER_CONTRACT_SMELL": "fail",
    "E217_UNDECLARED_COUPLING_SMELL": "fail",
    "E218_MISSING_EXPLAIN_CONTRACT_SMELL": "fail",
    "E229_WALLCLOCK_USE_SMELL": "fail",
    "E230_FUTURE_RECEIPT_REFERENCE_SMELL": "fail",
    "E231_UNDECLARED_TEMPORAL_DOMAIN_SMELL": "fail",
    "E232_DIRECT_TIME_WRITE_SMELL": "fail",
    "E233_IMPLICIT_CIVIL_TIME_SMELL": "fail",
    "E234_IMPLICIT_CLOCK_SYNC_SMELL": "fail",
    "E235_DIRECT_DOMAIN_TIME_WRITE_SMELL": "fail",
    "E236_IMPLICIT_FLOAT_USAGE_SMELL": "fail",
    "E237_MISSING_TOLERANCE_SMELL": "fail",
    "E238_DIRECT_DIVISION_WITHOUT_ROUND_SMELL": "fail",
    "E239_CANONICAL_ARTIFACT_COMPACTION_SMELL": "fail",
    "E240_UNCLASSIFIED_ARTIFACT_SMELL": "fail",
    "E241_MISSING_COMPACTION_MARKER_SMELL": "fail",
    "E242_INLINE_FUEL_BURN_SMELL": "fail",
    "E243_UNREGISTERED_COMBUSTION_SMELL": "fail",
    "E244_INLINE_YIELD_LOGIC_SMELL": "fail",
    "E245_RECIPE_BYPASS_SMELL": "fail",
    "E246_INLINE_CORROSION_SMELL": "fail",
    "E247_CROSS_DOMAIN_BYPASS_SMELL": "fail",
    "E252_DIRECT_CONCENTRATION_WRITE_SMELL": "fail",
    "E253_UNBOUNDED_CELL_LOOP_SMELL": "fail",
    "E254_DIRECT_EXPOSURE_WRITE_SMELL": "fail",
    "E255_OMNISCIENT_POLLUTION_UI_LEAK_SMELL": "fail",
    "E266_UNLOGGED_TIER_CHANGE_SMELL": "fail",
    "E267_TEMPLATE_BYPASS_SMELL": "fail",
    "E268_UNVERSIONED_TEMPLATE_SMELL": "fail",
    "E269_DIRECT_SPEC_BYPASS_SMELL": "fail",
    "E270_UNLOGGED_CERTIFICATE_ISSUE_SMELL": "fail",
    "E271_HIDDEN_FAILURE_LOGIC_SMELL": "fail",
    "E272_UNLOGGED_SHUTDOWN_SMELL": "fail",
    "E280_OUTPUT_DEPENDS_ON_UNDECLARED_FIELD_SMELL": "fail",
    "E281_UNREGISTERED_WORKFLOW_SMELL": "fail",
    "E282_PROCESS_STEP_WITHOUT_COST_SMELL": "fail",
    "E283_INLINE_YIELD_SMELL": "fail",
    "E284_DEFECT_FLAG_BYPASS_SMELL": "fail",
    "E285_IMPLICIT_QC_LOGIC_SMELL": "fail",
    "E286_NONDETERMINISTIC_SAMPLING_SMELL": "fail",
    "E287_HIDDEN_UNLOCK_SMELL": "fail",
    "E288_UNDECLARED_MATURITY_TRANSITION_SMELL": "fail",
    "E289_SILENT_CAPSULE_EXECUTION_SMELL": "fail",
    "E290_CAPSULE_USED_OUT_OF_DOMAIN_SMELL": "fail",
    "E291_SILENT_DRIFT_SMELL": "fail",
    "E292_CAPSULE_USED_WHILE_INVALID_SMELL": "fail",
    "E293_MAGIC_UNLOCK_SMELL": "fail",
    "E294_UNDECLARED_INFERENCE_SMELL": "fail",
    "E305_UNMETERED_LOOP_SMELL": "fail",
    "E306_SILENT_THROTTLE_SMELL": "fail",
    "E307_ELECTRICAL_BIAS_IN_LOGIC_SMELL": "fail",
    "E308_UNMETERED_LOGIC_COMPUTE_SMELL": "fail",
    "E309_OMNISCIENT_LOGIC_DEBUG_SMELL": "fail",
}


def _report_findings(repo_root: str, profile: str) -> List[Dict[str, object]]:
    findings_path = os.path.join(repo_root, "docs", "audit", "auditx", "FINDINGS.json")
    if not os.path.isfile(findings_path):
        return []
    try:
        payload = json.load(open(findings_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = payload.get("findings")
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, object]] = []
    token = str(profile or "").strip().upper()
    strict_mode = token in {"STRICT", "FULL"}
    for row in rows:
        if not isinstance(row, dict):
            continue
        analyzer_id = str(row.get("analyzer_id", "")).strip()
        severity = "warn"
        if strict_mode and analyzer_id in STRICT_PROMOTED_ANALYZERS:
            severity = str(STRICT_PROMOTED_ANALYZERS[analyzer_id]).strip().lower() or "fail"
        out.append(
            {
                "severity": severity,
                "code": "auditx.finding",
                "message": "{} {} {}".format(
                    str(row.get("severity", "")).strip() or "UNKNOWN",
                    analyzer_id or "analyzer",
                    str(row.get("finding_id", "")).strip() or "finding",
                ).strip(),
                "file_path": _norm(str((row.get("location") or {}).get("file_path", ""))),
                "line_number": int(((row.get("location") or {}).get("line_start", 0) or 0)),
            }
        )
    return sorted(
        out,
        key=lambda item: (
            _severity_rank(str(item.get("severity", ""))),
            str(item.get("file_path", "")),
            int(item.get("line_number", 0) or 0),
            str(item.get("message", "")),
        ),
    )


def run_auditx_check(repo_root: str, profile: str) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    changed_only = token == "FAST"

    from tools.auditx.auditx import run_auditx_scan

    scan = run_auditx_scan(
        repo_root=repo_root,
        changed_only=changed_only,
        output_root="",
        output_format="both",
    )
    payload = scan.get("payload") if isinstance(scan.get("payload"), dict) else {}
    result = str(scan.get("result", "")).strip()
    exit_code = int(scan.get("exit_code", 1))

    findings: List[Dict[str, object]] = []
    if result == "scan_complete":
        findings.extend(_report_findings(repo_root, token))
        status = _status_from_findings(findings)
        return {
            "status": status,
            "message": "auditx scan complete (changed_only={}, findings={}, promoted_blockers={})".format(
                "true" if changed_only else "false",
                int(payload.get("findings_count", 0) or 0),
                len([row for row in findings if str(row.get("severity", "")).strip().lower() in {"fail", "refusal"}]),
            ),
            "findings": findings,
        }

    refusal_code = str(payload.get("refusal_code", "")).strip()
    refusal_reason = str(payload.get("reason", "")).strip()
    if result == "refused":
        findings.append(
            {
                "severity": "warn",
                "code": refusal_code or "auditx.refusal",
                "message": refusal_reason or "auditx refused",
                "file_path": "tools/auditx/auditx.py",
                "line_number": 1,
            }
        )
        return {
            "status": "pass",
            "message": "auditx scan refused non-gating ({})".format(refusal_code or "unknown"),
            "findings": findings,
        }

    findings.append(
        {
            "severity": "fail",
            "code": "auditx.scan_internal_error",
            "message": "auditx scan failed (exit_code={})".format(exit_code),
            "file_path": "tools/auditx/auditx.py",
            "line_number": 1,
        }
    )
    return {
        "status": _status_from_findings(findings),
        "message": "auditx scan failed",
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AuditX semantic scan through xstack wrapper.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_auditx_check(repo_root=repo_root, profile=str(args.profile))
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
