"""Deterministic CONVERGENCE-GATE-0 orchestration helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability.stability_validator import validate_all_registries  # noqa: E402
from src.validation import build_validation_report  # noqa: E402
from tools.appshell.appshell4_probe import run_ipc_attach_probe  # noqa: E402
from tools.appshell.ipc_unify_common import IPC_UNIFY_TOOL_PATH  # noqa: E402
from tools.appshell.supervisor_hardening_common import (  # noqa: E402
    SUPERVISOR_HARDENING_TOOL_PATH,
    build_supervisor_hardening_report,
)
from tools.audit.arch_audit_common import build_arch_audit2_report, run_arch_audit  # noqa: E402
from tools.compat.cap_neg4_common import (  # noqa: E402
    DEFAULT_BASELINE_REL as CAP_NEG_BASELINE_REL,
    DEFAULT_CAP_NEG4_SEED,
    DEFAULT_MATRIX_REL as CAP_NEG_MATRIX_REL,
    DEFAULT_STRESS_REL as CAP_NEG_STRESS_REL,
    build_cap_neg_full_baseline,
    generate_interop_matrix,
    run_interop_stress,
    verify_interop_stress_replay,
    write_json as write_cap_neg_json,
)
from tools.dist.dist_verify_common import (  # noqa: E402
    build_distribution_verify_report,
    load_distribution_verify_report,
    write_distribution_verify_outputs,
)
from tools.lib.lib_stress_common import (  # noqa: E402
    DEFAULT_BASELINE_REL as LIB_BASELINE_REL,
    DEFAULT_LIB7_SEED,
    build_lib_regression_baseline,
    run_lib_stress,
    write_json as write_lib_json,
)
from tools.mvp.cross_platform_gate_common import (  # noqa: E402
    DEFAULT_BASELINE_REL as CROSS_PLATFORM_BASELINE_REL,
    DEFAULT_REPORT_REL as CROSS_PLATFORM_REPORT_REL,
    build_mvp_cross_platform_baseline,
    maybe_load_cached_mvp_cross_platform_report,
    run_mvp_cross_platform_matrix,
    write_mvp_cross_platform_outputs,
)
from tools.mvp.mvp_smoke_common import (  # noqa: E402
    DEFAULT_BASELINE_REL as SMOKE_BASELINE_REL,
    DEFAULT_MVP_SMOKE_SEED,
    DEFAULT_REPORT_REL as SMOKE_REPORT_REL,
    build_expected_hash_fingerprints,
    build_mvp_smoke_baseline,
    generate_mvp_smoke_scenario,
    maybe_load_cached_mvp_smoke_report,
    run_mvp_smoke,
    write_mvp_smoke_outputs,
)
from tools.mvp.prod_gate0_common import PRODUCT_BOOT_MATRIX_TOOL_PATH, build_product_boot_matrix_report  # noqa: E402
from tools.mvp.stress_gate_common import (  # noqa: E402
    DEFAULT_BASELINE_REL as STRESS_BASELINE_REL,
    DEFAULT_MVP_STRESS_SEED,
    DEFAULT_PROOF_REPORT_REL as STRESS_PROOF_REPORT_REL,
    DEFAULT_REPORT_REL as STRESS_REPORT_REL,
    _gate_report_result,
    _gate_suite_rows,
    build_mvp_stress_baseline,
    maybe_load_cached_mvp_stress_proof_report,
    maybe_load_cached_mvp_stress_report,
    run_all_mvp_stress,
    run_pack_compat_stress,
    verify_mvp_stress_proofs,
    write_mvp_stress_outputs,
)
from tools.time.time_anchor_common import verify_compaction_anchor_alignment, verify_longrun_ticks  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


CONVERGENCE_GATE_ID = "release.convergence.gate.v1"
CONVERGENCE_TOOL_PATH = "tools/convergence/tool_run_convergence_gate.py"
CONVERGENCE_FINAL_DOC_PATH = "docs/audit/CONVERGENCE_FINAL.md"
CONVERGENCE_FINAL_JSON_PATH = "data/audit/convergence_final.json"
CONVERGENCE_STEP_DOC_DIR = "docs/audit/convergence_steps"
CONVERGENCE_STEP_JSON_DIR = "data/audit/convergence_steps"
LAST_REVIEWED = "2026-03-13"
CAP_NEG_TOOL_PATH = "tools/compat/tool_run_interop_stress.py"
PACK_COMPAT_TOOL_PATH = "tools/mvp/tool_run_all_stress.py"
LIB_TOOL_PATH = "tools/lib/tool_run_lib_stress.py"
TIME_ANCHOR_TOOL_PATH = "tools/time/tool_verify_longrun_ticks.py"
ARCH_AUDIT_TOOL_PATH = "tools/audit/tool_run_arch_audit.py"
VALIDATION_TOOL_PATH = "tools/validation/tool_run_validation.py"
META_STABILITY_TOOL_PATH = "src/meta/stability/stability_validator.py"
MVP_SMOKE_TOOL_PATH = "tools/mvp/tool_run_mvp_smoke.py"
MVP_STRESS_TOOL_PATH = "tools/mvp/tool_run_all_stress.py"
MVP_CROSS_PLATFORM_TOOL_PATH = "tools/mvp/tool_run_cross_platform_matrix.py"
DIST_VERIFY_TOOL_PATH = "tools/dist/tool_verify_distribution.py"
DEFAULT_LIB_STRESS_OUT_REL = os.path.join("build", "tmp", "convergence", "lib_stress_workspace")


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(str(path or REPO_ROOT_HINT)))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return ""
    if os.path.isabs(token):
        return _norm(token)
    return _norm(os.path.join(_norm(repo_root), token.replace("/", os.sep)))


def _rel(repo_root: str, path: str) -> str:
    abs_path = _repo_abs(repo_root, path)
    if not abs_path:
        return ""
    return os.path.relpath(abs_path, _norm(repo_root)).replace("\\", "/")


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _write_text(path: str, text: str) -> str:
    abs_path = _norm(path)
    _ensure_dir(os.path.dirname(abs_path))
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return abs_path


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    abs_path = _norm(path)
    _ensure_dir(os.path.dirname(abs_path))
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return abs_path


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _payload_fingerprint(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(dict(_as_map(payload), deterministic_fingerprint=""))


def _compare_payloads(expected: object, actual: object, *, path: str = "", limit: int = 24) -> list[dict]:
    rows: list[dict] = []

    def _walk(left: object, right: object, current_path: str) -> None:
        if len(rows) >= limit:
            return
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            left_map = dict(left)
            right_map = dict(right)
            keys = sorted(set(left_map.keys()) | set(right_map.keys()), key=lambda item: str(item))
            for key in keys:
                next_path = "{}.{}".format(current_path, key) if current_path else str(key)
                if key not in left_map:
                    rows.append({"path": next_path, "expected": "<missing>", "actual": right_map.get(key)})
                    continue
                if key not in right_map:
                    rows.append({"path": next_path, "expected": left_map.get(key), "actual": "<missing>"})
                    continue
                _walk(left_map.get(key), right_map.get(key), next_path)
                if len(rows) >= limit:
                    return
            return
        if isinstance(left, list) and isinstance(right, list):
            if left == right:
                return
            max_len = max(len(left), len(right))
            for index in range(max_len):
                next_path = "{}[{}]".format(current_path, index) if current_path else "[{}]".format(index)
                if index >= len(left):
                    rows.append({"path": next_path, "expected": "<missing>", "actual": right[index]})
                elif index >= len(right):
                    rows.append({"path": next_path, "expected": left[index], "actual": "<missing>"})
                else:
                    _walk(left[index], right[index], next_path)
                if len(rows) >= limit:
                    return
            return
        if left != right:
            rows.append({"path": current_path or "$", "expected": left, "actual": right})

    _walk(expected, actual, path)
    return rows


def _baseline_status(repo_root: str, baseline_path: str, baseline_candidate: Mapping[str, object] | None) -> dict:
    existing = _read_json(repo_root, baseline_path)
    candidate = dict(_as_map(baseline_candidate))
    if not existing:
        return {
            "checked": False,
            "present": False,
            "match": False,
            "mismatches": [{"path": baseline_path, "expected": "existing baseline", "actual": "missing"}],
            "expected_fingerprint": "",
            "actual_fingerprint": _payload_fingerprint(candidate),
            "baseline_path": baseline_path.replace("\\", "/"),
        }
    mismatches = _compare_payloads(existing, candidate)
    return {
        "checked": True,
        "present": True,
        "match": not bool(mismatches),
        "mismatches": mismatches,
        "expected_fingerprint": _payload_fingerprint(existing),
        "actual_fingerprint": _payload_fingerprint(candidate),
        "baseline_path": baseline_path.replace("\\", "/"),
    }


def convergence_step_specs(*, include_cross_platform: bool = True, include_dist_verify: bool = False) -> list[dict]:
    rows = [
        {
            "step_id": "validation_strict",
            "title": "VALIDATION-UNIFY STRICT",
            "tool_path": VALIDATION_TOOL_PATH,
            "rule_id": "INV-VALIDATE-ALL-AVAILABLE",
            "rerun_command": "python tools/validation/tool_run_validation.py --repo-root . --profile STRICT",
        },
        {
            "step_id": "meta_stability",
            "title": "META-STABILITY validator",
            "tool_path": META_STABILITY_TOOL_PATH,
            "rule_id": "INV-ALL-REGISTRIES-TAGGED",
            "rerun_command": "@'\nfrom src.meta.stability.stability_validator import validate_all_registries\nimport json\nprint(json.dumps(validate_all_registries('.'), indent=2, sort_keys=True))\n'@ | python -",
        },
        {
            "step_id": "time_anchor",
            "title": "TIME-ANCHOR verifier",
            "tool_path": TIME_ANCHOR_TOOL_PATH,
            "rule_id": "INV-TICK-TYPE-64BIT-ENFORCED",
            "rerun_command": "python tools/time/tool_verify_longrun_ticks.py --repo-root .",
        },
        {
            "step_id": "arch_audit",
            "title": "ARCH-AUDIT tool",
            "tool_path": ARCH_AUDIT_TOOL_PATH,
            "rule_id": "INV-ARCH-AUDIT-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/audit/tool_run_arch_audit.py --repo-root . --report-path docs/audit/ARCH_AUDIT_REPORT.md --json-path data/audit/arch_audit_report.json",
        },
        {
            "step_id": "cap_neg_interop",
            "title": "CAP-NEG-4 interop stress",
            "tool_path": CAP_NEG_TOOL_PATH,
            "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/compat/tool_run_interop_stress.py --repo-root .",
        },
        {
            "step_id": "pack_compat_stress",
            "title": "PACK-COMPAT verification stress",
            "tool_path": PACK_COMPAT_TOOL_PATH,
            "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/mvp/tool_run_all_stress.py --repo-root .",
        },
        {
            "step_id": "lib_stress",
            "title": "LIB-7 stress",
            "tool_path": LIB_TOOL_PATH,
            "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/lib/tool_run_lib_stress.py --repo-root . --out-root build/tmp/convergence/lib_stress_workspace",
        },
        {
            "step_id": "product_boot_matrix",
            "title": "PROD-GATE-0 boot matrix",
            "tool_path": PRODUCT_BOOT_MATRIX_TOOL_PATH,
            "rule_id": "INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/mvp/tool_run_product_boot_matrix.py --repo-root .",
        },
        {
            "step_id": "ipc_attach_smoke",
            "title": "IPC-UNIFY attach smoke",
            "tool_path": IPC_UNIFY_TOOL_PATH,
            "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
            "rerun_command": "python tools/appshell/tool_run_ipc_unify.py --repo-root .",
        },
        {
            "step_id": "supervisor_hardening",
            "title": "SUPERVISOR-HARDEN checks",
            "tool_path": SUPERVISOR_HARDENING_TOOL_PATH,
            "rule_id": "INV-SUPERVISOR-NO-WALLCLOCK",
            "rerun_command": "python tools/appshell/tool_run_supervisor_hardening.py --repo-root .",
        },
        {
            "step_id": "mvp_smoke",
            "title": "MVP-GATE-0 smoke suite",
            "tool_path": MVP_SMOKE_TOOL_PATH,
            "rule_id": "INV-MVP-SMOKE-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/mvp/tool_run_mvp_smoke.py --repo-root .",
        },
        {
            "step_id": "mvp_stress",
            "title": "MVP-GATE-1 stress suite",
            "tool_path": MVP_STRESS_TOOL_PATH,
            "rule_id": "INV-MVP-STRESS-MUST-PASS-BEFORE-RELEASE",
            "rerun_command": "python tools/mvp/tool_run_all_stress.py --repo-root .",
        },
    ]
    if include_cross_platform:
        rows.append(
            {
                "step_id": "mvp_cross_platform",
                "title": "MVP-GATE-2 cross-platform agreement",
                "tool_path": MVP_CROSS_PLATFORM_TOOL_PATH,
                "rule_id": "INV-MVP-CROSS-PLATFORM-MUST-PASS",
                "rerun_command": "python tools/mvp/tool_run_cross_platform_matrix.py --repo-root .",
            }
        )
    if include_dist_verify:
        rows.append(
            {
                "step_id": "dist_verify",
                "title": "DIST-2 distribution integrity verification",
                "tool_path": DIST_VERIFY_TOOL_PATH,
                "rule_id": "INV-DIST-VERIFY-MUST-PASS",
                "rerun_command": "python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64",
            }
        )
    return list(rows)


def convergence_step_ids(*, include_cross_platform: bool = True, include_dist_verify: bool = False) -> list[str]:
    return [str(row.get("step_id")) for row in convergence_step_specs(include_cross_platform=include_cross_platform, include_dist_verify=include_dist_verify)]


def _step_lookup(*, include_cross_platform: bool, include_dist_verify: bool) -> dict[str, dict]:
    return {
        str(row.get("step_id")): dict(row)
        for row in convergence_step_specs(include_cross_platform=include_cross_platform, include_dist_verify=include_dist_verify)
    }


def _default_remediation(spec: Mapping[str, object], *, refusal_code: str = "", message: str = "") -> list[dict]:
    return [
        {
            "module": _token(spec.get("tool_path")),
            "rule_id": _token(spec.get("rule_id")),
            "refusal_code": _token(refusal_code),
            "suggested_fix_command": _token(spec.get("rerun_command")),
            "message": _token(message),
        }
    ]


def _make_step_summary(
    spec: Mapping[str, object],
    *,
    step_no: int,
    result: str,
    source_fingerprint: str,
    source_paths: Sequence[str] | None = None,
    observed_refusal_count: int = 0,
    observed_degrade_count: int = 0,
    default_path_refusal_count: int = 0,
    default_path_degrade_count: int = 0,
    key_hashes: Mapping[str, object] | None = None,
    notes: Sequence[object] | None = None,
    remediation: Sequence[Mapping[str, object]] | None = None,
    failure_reason: str = "",
    refusal_code: str = "",
    metrics: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "step_id": _token(spec.get("step_id")),
        "step_no": int(step_no),
        "title": _token(spec.get("title")),
        "tool_path": _token(spec.get("tool_path")),
        "rule_id": _token(spec.get("rule_id")),
        "result": _token(result) or "refused",
        "status": "PASS" if _token(result) == "complete" else "FAIL",
        "failure_reason": _token(failure_reason),
        "refusal_code": _token(refusal_code),
        "source_fingerprint": _token(source_fingerprint),
        "source_paths": sorted(_token(item) for item in list(source_paths or []) if _token(item)),
        "observed_refusal_count": int(observed_refusal_count),
        "observed_degrade_count": int(observed_degrade_count),
        "default_path_refusal_count": int(default_path_refusal_count),
        "default_path_degrade_count": int(default_path_degrade_count),
        "key_hashes": dict(sorted((_as_map(key_hashes)).items(), key=lambda item: str(item[0]))),
        "metrics": dict(sorted((_as_map(metrics)).items(), key=lambda item: str(item[0]))),
        "notes": [_token(item) for item in list(notes or []) if _token(item)],
        "remediation": [
            {
                "module": _token(_as_map(item).get("module")),
                "rule_id": _token(_as_map(item).get("rule_id")),
                "refusal_code": _token(_as_map(item).get("refusal_code")),
                "suggested_fix_command": _token(_as_map(item).get("suggested_fix_command")),
                "message": _token(_as_map(item).get("message")),
            }
            for item in list(remediation or [])
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _render_step_markdown(step: Mapping[str, object]) -> str:
    row = _as_map(step)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: RELEASE",
        "Replacement Target: regenerated convergence step summary for {}".format(_token(row.get("step_id"))),
        "",
        "# Convergence Step - {}".format(_token(row.get("title")) or _token(row.get("step_id"))),
        "",
        "- step_no: `{}`".format(int(_as_int(row.get("step_no", 0), 0))),
        "- step_id: `{}`".format(_token(row.get("step_id"))),
        "- result: `{}`".format(_token(row.get("result"))),
        "- rule_id: `{}`".format(_token(row.get("rule_id"))),
        "- source_fingerprint: `{}`".format(_token(row.get("source_fingerprint"))),
        "- observed_refusal_count: `{}`".format(int(_as_int(row.get("observed_refusal_count", 0), 0))),
        "- observed_degrade_count: `{}`".format(int(_as_int(row.get("observed_degrade_count", 0), 0))),
        "",
        "## Key Hashes",
        "",
    ]
    key_hashes = _as_map(row.get("key_hashes"))
    if key_hashes:
        for key, value in sorted(key_hashes.items(), key=lambda item: str(item[0])):
            lines.append("- {}: `{}`".format(str(key), _token(value)))
    else:
        lines.append("- none")
    lines.extend(("", "## Notes", ""))
    notes = [_token(item) for item in _as_list(row.get("notes")) if _token(item)]
    if notes:
        for note in notes:
            lines.append("- {}".format(note))
    else:
        lines.append("- none")
    lines.extend(("", "## Source Paths", ""))
    source_paths = [_token(item) for item in _as_list(row.get("source_paths")) if _token(item)]
    if source_paths:
        for source_path in source_paths:
            lines.append("- `{}`".format(source_path))
    else:
        lines.append("- none")
    lines.extend(("", "## Remediation", ""))
    remediation_rows = [_as_map(item) for item in _as_list(row.get("remediation")) if _as_map(item)]
    if remediation_rows:
        for item in remediation_rows:
            lines.append(
                "- module=`{}` rule=`{}` refusal=`{}` command=`{}` {}".format(
                    _token(item.get("module")),
                    _token(item.get("rule_id")),
                    _token(item.get("refusal_code")) or "none",
                    _token(item.get("suggested_fix_command")),
                    _token(item.get("message")),
                ).rstrip()
            )
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def _write_step_snapshot(repo_root: str, step: Mapping[str, object], *, json_dir: str, doc_dir: str) -> dict[str, str]:
    root = _norm(repo_root)
    step_id = _token(_as_map(step).get("step_id")) or "unknown"
    json_rel = os.path.join(json_dir, "{}.json".format(step_id)).replace("\\", "/")
    doc_rel = os.path.join(doc_dir, "{}.md".format(step_id)).replace("\\", "/")
    _write_json(_repo_abs(root, json_rel), _as_map(step))
    _write_text(_repo_abs(root, doc_rel), _render_step_markdown(step))
    return {"json_path": json_rel, "doc_path": doc_rel}


def _validation_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = build_validation_report(repo_root, profile="STRICT")
    result = _token(report.get("result")) or "refused"
    errors = [_as_map(item) for item in _as_list(report.get("errors")) if _as_map(item)]
    warnings = [_as_map(item) for item in _as_list(report.get("warnings")) if _as_map(item)]
    failure_reason = ""
    refusal_code = ""
    notes = [
        "profile=STRICT",
        "suite_count={}".format(int(_as_int(_as_map(report.get("metrics")).get("suite_count", 0), 0))),
        "error_count={}".format(len(errors)),
        "warning_count={}".format(len(warnings)),
    ]
    if result != "complete":
        first_error = errors[0] if errors else {}
        failure_reason = _token(first_error.get("message")) or "unified validation pipeline reported non-complete result"
        refusal_code = _token(first_error.get("code"))
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[
            "docs/audit/VALIDATION_REPORT_STRICT.md",
            "data/audit/validation_report_STRICT.json",
            "docs/audit/VALIDATION_UNIFY_FINAL.md",
        ],
        observed_refusal_count=len(errors),
        default_path_refusal_count=len(errors),
        key_hashes={
            "validation_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "suite_results_hash": canonical_sha256(_as_list(report.get("suite_results"))),
        },
        metrics=_as_map(report.get("metrics")),
        notes=notes,
        remediation=_default_remediation(spec, refusal_code=refusal_code, message=failure_reason),
        failure_reason=failure_reason,
        refusal_code=refusal_code,
    )


def _meta_stability_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = validate_all_registries(repo_root)
    result = _token(report.get("result")) or "refused"
    violations = [
        _as_map(item)
        for item in _as_list(report.get("reports"))
        if _token(_as_map(item).get("result")) != "complete"
    ]
    failure_reason = ""
    if result != "complete":
        first = violations[0] if violations else {}
        failure_reason = _token(first.get("path")) or "stability validator reported registry drift"
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=["data/registries"],
        observed_refusal_count=len(violations),
        default_path_refusal_count=len(violations),
        key_hashes={"stability_report_fingerprint": _token(report.get("deterministic_fingerprint"))},
        notes=[
            "registry_report_count={}".format(len(_as_list(report.get("reports")))),
            "violations={}".format(len(violations)),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _time_anchor_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    verify_report = verify_longrun_ticks(repo_root)
    compaction_report = verify_compaction_anchor_alignment(repo_root)
    checks_ok = _token(verify_report.get("result")) == "complete" and _token(compaction_report.get("result")) == "complete"
    result = "complete" if checks_ok else "refused"
    failure_reason = ""
    if _token(verify_report.get("result")) != "complete":
        failure_reason = "verify_longrun_ticks reported non-complete result"
    elif _token(compaction_report.get("result")) != "complete":
        failure_reason = "verify_compaction_anchor_alignment reported non-complete result"
    key_hashes = {
        "verify_report_fingerprint": _token(verify_report.get("deterministic_fingerprint")),
        "compaction_report_fingerprint": _token(compaction_report.get("deterministic_fingerprint")),
        "cross_platform_anchor_hash": _token(_as_map(verify_report.get("cross_platform_anchor_hashes")).get("windows")),
        "interval_anchor_hash": _token(_as_map(verify_report.get("interval_anchor")).get("anchor_hash")),
    }
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=canonical_sha256(key_hashes),
        source_paths=["build/time/time_anchor_verify_report.json", "build/time/time_anchor_compaction_report.json"],
        observed_refusal_count=0 if checks_ok else 1,
        default_path_refusal_count=0 if checks_ok else 1,
        key_hashes=key_hashes,
        notes=[
            "verify_result={}".format(_token(verify_report.get("result"))),
            "compaction_result={}".format(_token(compaction_report.get("result"))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _arch_audit_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = run_arch_audit(repo_root)
    audit2_report = build_arch_audit2_report(report)
    result = _token(report.get("result")) or "refused"
    blocking = int(_as_int(report.get("blocking_finding_count", 0), 0))
    first_blocking = _as_map((_as_list(report.get("blocking_findings")) or [{}])[0])
    failure_reason = ""
    if result != "complete":
        failure_reason = _token(first_blocking.get("message")) or "ARCH-AUDIT reported blocking findings"
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[
            "docs/audit/ARCH_AUDIT_REPORT.md",
            "data/audit/arch_audit_report.json",
            "docs/audit/ARCH_AUDIT2_REPORT.md",
            "data/audit/arch_audit2_report.json",
            "docs/audit/ARCH_AUDIT2_FINAL.md",
        ],
        observed_refusal_count=blocking,
        default_path_refusal_count=blocking,
        key_hashes={
            "arch_audit_fingerprint": _token(report.get("deterministic_fingerprint")),
            "arch_audit2_fingerprint": _token(audit2_report.get("deterministic_fingerprint")),
            "blocking_findings_hash": canonical_sha256(_as_list(report.get("blocking_findings"))),
        },
        notes=[
            "blocking_finding_count={}".format(blocking),
            "known_exception_count={}".format(int(_as_int(report.get("known_exception_count", 0), 0))),
            "arch_audit2_blocking_finding_count={}".format(int(_as_int(audit2_report.get("blocking_finding_count", 0), 0))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _cap_neg_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    matrix = generate_interop_matrix(repo_root=repo_root, seed=DEFAULT_CAP_NEG4_SEED)
    report = run_interop_stress(repo_root=repo_root, matrix=matrix, seed=DEFAULT_CAP_NEG4_SEED)
    replay = verify_interop_stress_replay(repo_root=repo_root, matrix=matrix, seed=DEFAULT_CAP_NEG4_SEED)
    baseline_candidate = build_cap_neg_full_baseline(
        repo_root=repo_root,
        matrix=matrix,
        stress_report=report,
        seed=DEFAULT_CAP_NEG4_SEED,
    )
    baseline_status = _baseline_status(repo_root, CAP_NEG_BASELINE_REL, baseline_candidate)
    write_cap_neg_json(_repo_abs(repo_root, CAP_NEG_MATRIX_REL), matrix)
    write_cap_neg_json(_repo_abs(repo_root, CAP_NEG_STRESS_REL), report)
    result = "complete" if _token(report.get("result")) == "complete" and _token(replay.get("result")) == "complete" and bool(baseline_status.get("match", False)) else "refused"
    failure_reason = ""
    if _token(report.get("result")) != "complete":
        failure_reason = "CAP-NEG interop stress reported non-complete result"
    elif _token(replay.get("result")) != "complete":
        failure_reason = "CAP-NEG replay summary reported non-complete result"
    elif not bool(baseline_status.get("match", False)):
        failure_reason = "CAP-NEG baseline mismatch detected"
    refusal_rows = [_as_map(item) for item in _as_list(report.get("refusal_counts")) if _as_map(item)]
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[CAP_NEG_MATRIX_REL.replace("\\", "/"), CAP_NEG_STRESS_REL.replace("\\", "/"), CAP_NEG_BASELINE_REL.replace("\\", "/")],
        observed_refusal_count=sum(int(_as_int(_as_map(item).get("count", 0), 0)) for item in refusal_rows),
        default_path_refusal_count=0,
        key_hashes={
            "matrix_fingerprint": _token(matrix.get("deterministic_fingerprint")),
            "stress_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "replay_fingerprint": _token(replay.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_candidate.get("deterministic_fingerprint")),
        },
        metrics={
            "scenario_count": int(_as_int(report.get("scenario_count", 0), 0)),
            "refusal_count": sum(int(_as_int(_as_map(item).get("count", 0), 0)) for item in refusal_rows),
        },
        notes=[
            "baseline_match={}".format(bool(baseline_status.get("match", False))),
            "mode_counts_hash={}".format(canonical_sha256(_as_map(report.get("mode_counts")))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _pack_compat_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = run_pack_compat_stress(repo_root)
    result = _token(report.get("result")) or "refused"
    failure_reason = ""
    if result != "complete":
        failure_reason = "PACK-COMPAT verification stress reported non-complete result"
    set_reports = [_as_map(item) for item in _as_list(report.get("set_reports")) if _as_map(item)]
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[],
        observed_refusal_count=0,
        default_path_refusal_count=0,
        key_hashes={
            "pack_compat_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "pack_lock_hashes": canonical_sha256(
                {
                    _token(_as_map(item).get("set_id")): _token(_as_map(item).get("pack_lock_hash"))
                    for item in set_reports
                    if _token(_as_map(item).get("set_id"))
                }
            ),
        },
        metrics={
            "set_count": len(set_reports),
            "valid_set_count": len([item for item in set_reports if bool(_as_map(item).get("valid", False))]),
        },
        notes=[
            "all_sets_valid={}".format(bool(_as_map(report.get("assertions")).get("all_sets_valid", False))),
            "all_sets_stable={}".format(bool(_as_map(report.get("assertions")).get("all_sets_stable", False))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _lib_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    out_root = _repo_abs(repo_root, DEFAULT_LIB_STRESS_OUT_REL)
    report = run_lib_stress(repo_root=repo_root, out_root=out_root, seed=DEFAULT_LIB7_SEED, slash_mode="forward")
    report_path = os.path.join("build", "lib", "lib_stress_report.json").replace("\\", "/")
    write_lib_json(_repo_abs(repo_root, report_path), report)
    baseline_candidate = build_lib_regression_baseline(report)
    baseline_status = _baseline_status(repo_root, LIB_BASELINE_REL, baseline_candidate)
    result = "complete" if _token(report.get("result")) == "complete" and bool(baseline_status.get("match", False)) else "refused"
    failure_reason = ""
    if _token(report.get("result")) != "complete":
        failure_reason = "LIB-7 stress reported non-complete result"
    elif not bool(baseline_status.get("match", False)):
        failure_reason = "LIB-7 baseline mismatch detected"
    refusal_rows = [_as_map(item) for item in _as_list(report.get("refusal_counts")) if _as_map(item)]
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[report_path, LIB_BASELINE_REL.replace("\\", "/")],
        observed_refusal_count=sum(int(_as_int(_as_map(item).get("count", 0), 0)) for item in refusal_rows),
        default_path_refusal_count=0,
        key_hashes={
            "lib_stress_fingerprint": _token(report.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_candidate.get("deterministic_fingerprint")),
            "bundle_hashes": canonical_sha256(_as_map(report.get("bundle_hashes"))),
        },
        metrics={
            "ambiguity_count": int(_as_int(report.get("ambiguity_count", 0), 0)),
            "round_count": len(_as_list(report.get("rounds"))),
        },
        notes=[
            "baseline_match={}".format(bool(baseline_status.get("match", False))),
            "stable_across_repeated_runs={}".format(bool(report.get("stable_across_repeated_runs", False))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _product_boot_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = build_product_boot_matrix_report(repo_root)
    result = "complete" if _token(report.get("result")) == "complete" else "refused"
    failures = [_as_map(item) for item in _as_list(report.get("failures")) if _as_map(item)]
    failure_reason = _token(_as_map(failures[0]).get("message")) if failures else ""
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=["docs/mvp/PRODUCT_BOOT_MATRIX.md", "data/audit/product_boot_matrix.json"],
        observed_degrade_count=int(_as_int(_as_map(report.get("metrics")).get("degrade_count", 0), 0)),
        key_hashes={"product_boot_matrix_fingerprint": _token(report.get("deterministic_fingerprint"))},
        metrics=_as_map(report.get("metrics")),
        notes=[
            "portable_and_installed_matrix_exercised=true",
            "failure_count={}".format(len(failures)),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _ipc_attach_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    reports = [
        run_ipc_attach_probe(repo_root, product_id="server", suffix="convergence.server"),
        run_ipc_attach_probe(repo_root, product_id="client", suffix="convergence.client"),
        run_ipc_attach_probe(repo_root, product_id="setup", suffix="convergence.setup"),
    ]
    result = "complete" if all(_token(report.get("result")) == "complete" for report in reports) else "refused"
    failure_reason = ""
    if result != "complete":
        first_bad = next((report for report in reports if _token(report.get("result")) != "complete"), {})
        failure_reason = "IPC attach smoke failed for {}".format(_token(first_bad.get("product_id")) or "unknown product")
    notes = []
    key_hashes = {}
    refusal_count = 0
    for report in reports:
        product_id = _token(report.get("product_id"))
        attach = _as_map(report.get("attach"))
        missing_negotiation = _as_map(report.get("missing_negotiation"))
        key_hashes["{}_ipc_hash".format(product_id)] = _token(report.get("cross_platform_ipc_hash"))
        key_hashes["{}_negotiation_record_hash".format(product_id)] = _token(attach.get("negotiation_record_hash"))
        notes.append(
            "{} compatibility_mode_id={} missing_negotiation_refusal={}".format(
                product_id,
                _token(attach.get("compatibility_mode_id")),
                _token(_as_map(_as_map(_as_map(missing_negotiation.get("payload_ref")).get("payload_ref")).get("refusal")).get("refusal_code")),
            )
        )
        if _token(report.get("result")) != "complete":
            refusal_count += 1
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=canonical_sha256(key_hashes),
        source_paths=[],
        observed_refusal_count=refusal_count,
        default_path_refusal_count=refusal_count,
        key_hashes=key_hashes,
        metrics={"attach_product_count": len(reports)},
        notes=notes,
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _supervisor_step(repo_root: str, spec: Mapping[str, object], *, step_no: int) -> dict:
    report = build_supervisor_hardening_report(repo_root)
    result = "complete" if _token(report.get("result")) == "complete" else "refused"
    violations = [_as_map(item) for item in _as_list(report.get("violations")) if _as_map(item)]
    failure_reason = _token(_as_map(violations[0]).get("message")) if violations else ""
    runtime_probe = _as_map(report.get("runtime_probe"))
    replay_probe = _as_map(report.get("replay_probe"))
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=["data/audit/supervisor_hardening_report.json", "docs/audit/SUPERVISOR_HARDENING_FINAL.md"],
        observed_refusal_count=len(violations),
        default_path_refusal_count=len(violations),
        key_hashes={
            "supervisor_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "runtime_hash": _token(runtime_probe.get("deterministic_fingerprint")),
            "replay_hash": _token(replay_probe.get("deterministic_fingerprint")),
        },
        notes=[
            "runtime_result={}".format(_token(runtime_probe.get("result"))),
            "replay_result={}".format(_token(replay_probe.get("result"))),
            "crash_policy_result={}".format(_token(_as_map(report.get("crash_policy_probe")).get("result"))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _mvp_smoke_step(
    repo_root: str,
    spec: Mapping[str, object],
    *,
    step_no: int,
    prefer_cached: bool,
) -> dict:
    scenario = generate_mvp_smoke_scenario(repo_root, seed=DEFAULT_MVP_SMOKE_SEED)
    expected_hashes = build_expected_hash_fingerprints(repo_root, seed=DEFAULT_MVP_SMOKE_SEED, scenario=scenario)
    report = {}
    if prefer_cached:
        report = maybe_load_cached_mvp_smoke_report(repo_root, scenario=scenario, expected_hashes=expected_hashes)
    baseline_payload = _read_json(repo_root, SMOKE_BASELINE_REL)
    if not report:
        report = run_mvp_smoke(
            repo_root,
            seed=DEFAULT_MVP_SMOKE_SEED,
            scenario=scenario,
            expected_hashes=expected_hashes,
            baseline_payload=baseline_payload,
        )
    write_mvp_smoke_outputs(
        repo_root,
        report=report,
        gate_results={"repox": {"status": "PASS"}, "auditx": {"status": "PASS"}, "testx": {"status": "PASS"}, "smoke": {"status": "PASS"}},
    )
    baseline_status = _baseline_status(repo_root, SMOKE_BASELINE_REL, build_mvp_smoke_baseline(report))
    result = "complete" if _token(report.get("result")) == "complete" and bool(baseline_status.get("match", False)) else "refused"
    failure_reason = ""
    if _token(report.get("result")) != "complete":
        failure_reason = "MVP smoke suite reported non-complete result"
    elif not bool(baseline_status.get("match", False)):
        failure_reason = "MVP smoke baseline mismatch detected"
    actual_hash_summary = _as_map(report.get("actual_hash_summary"))
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[SMOKE_REPORT_REL.replace("\\", "/"), SMOKE_BASELINE_REL.replace("\\", "/"), "docs/audit/MVP_SMOKE_FINAL.md"],
        observed_refusal_count=int(_as_int(report.get("refusal_count", 0), 0)),
        default_path_refusal_count=int(_as_int(report.get("refusal_count", 0), 0)),
        key_hashes={
            "pack_lock_hash": _token(_as_map(actual_hash_summary.get("build_lock")).get("pack_lock_hash")),
            "contract_bundle_hash": _token(_as_map(actual_hash_summary.get("server_probe")).get("contract_bundle_hash")),
            "negotiation_record_hash": _token(_as_map(actual_hash_summary.get("compat_status")).get("negotiation_record_hash")),
            "proof_anchor_hash": _token(_as_map(actual_hash_summary.get("server_probe")).get("report_fingerprint")),
            "repro_bundle_hash": _token(_as_map(report.get("diag_bundle")).get("bundle_hash")),
        },
        notes=[
            "baseline_match={}".format(bool(baseline_status.get("match", False))),
            "expected_hashes_match={}".format(bool(_as_map(report.get("expected_hash_comparison")).get("match", False))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _mvp_stress_step(
    repo_root: str,
    spec: Mapping[str, object],
    *,
    step_no: int,
    prefer_cached: bool,
) -> dict:
    report = maybe_load_cached_mvp_stress_report(repo_root) if prefer_cached else {}
    if not report:
        report = run_all_mvp_stress(repo_root, seed=DEFAULT_MVP_STRESS_SEED)
    proof_report = maybe_load_cached_mvp_stress_proof_report(repo_root, report=report) if prefer_cached else {}
    baseline_payload = _read_json(repo_root, STRESS_BASELINE_REL)
    if not proof_report:
        proof_report = verify_mvp_stress_proofs(repo_root, report=report, baseline_payload=baseline_payload)
    write_mvp_stress_outputs(
        repo_root,
        report=report,
        proof_report=proof_report,
        gate_results={"repox": {"status": "PASS"}, "auditx": {"status": "PASS"}, "testx": {"status": "PASS"}, "orchestrator": {"status": "PASS"}},
    )
    baseline_status = _baseline_status(repo_root, STRESS_BASELINE_REL, build_mvp_stress_baseline(report, proof_report))
    gate_result = _gate_report_result(report)
    result = "complete" if gate_result == "complete" and _token(proof_report.get("result")) == "complete" and bool(baseline_status.get("match", False)) else "refused"
    failure_reason = ""
    if gate_result != "complete":
        failure_reason = "MVP stress suite reported non-complete result"
    elif _token(proof_report.get("result")) != "complete":
        failure_reason = "MVP stress proof verification reported non-complete result"
    elif not bool(baseline_status.get("match", False)):
        failure_reason = "MVP stress baseline mismatch detected"
    suite_summaries = [_as_map(item) for item in _as_list(report.get("suite_summaries")) if _as_map(item)]
    if not suite_summaries:
        suite_summaries = [_as_map(item) for item in _gate_suite_rows(report) if _as_map(item)]
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[STRESS_REPORT_REL.replace("\\", "/"), STRESS_PROOF_REPORT_REL.replace("\\", "/"), STRESS_BASELINE_REL.replace("\\", "/"), "docs/audit/MVP_STRESS_FINAL.md"],
        observed_refusal_count=int(_as_int(report.get("unexpected_refusal_count", 0), 0)),
        default_path_refusal_count=0,
        key_hashes={
            "stress_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "stress_proof_fingerprint": _token(proof_report.get("deterministic_fingerprint")),
            "contract_bundle_hash": _token(_as_map(_as_map(proof_report.get("proof_surfaces")).get("contract_bundle_hashes")).get("server")),
            "proof_anchor_hashes": canonical_sha256(_as_map(_as_map(proof_report.get("proof_surfaces")).get("proof_anchor_hashes"))),
        },
        metrics={
            "suite_count": len(suite_summaries),
            "unexpected_refusal_count": int(_as_int(report.get("unexpected_refusal_count", 0), 0)),
        },
        notes=[
            "baseline_match={}".format(bool(baseline_status.get("match", False))),
            "proof_result={}".format(_token(proof_report.get("result"))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _mvp_cross_platform_step(
    repo_root: str,
    spec: Mapping[str, object],
    *,
    step_no: int,
    prefer_cached: bool,
) -> dict:
    report = maybe_load_cached_mvp_cross_platform_report(repo_root) if prefer_cached else {}
    if not report:
        report = run_mvp_cross_platform_matrix(repo_root)
    write_mvp_cross_platform_outputs(
        repo_root,
        report=report,
        gate_results={"repox": {"status": "PASS"}, "auditx": {"status": "PASS"}, "testx": {"status": "PASS"}, "matrix": {"status": "PASS"}},
    )
    baseline_status = _baseline_status(repo_root, CROSS_PLATFORM_BASELINE_REL, build_mvp_cross_platform_baseline(report))
    result = "complete" if _token(report.get("result")) == "complete" and bool(baseline_status.get("match", False)) else "refused"
    failure_reason = ""
    if _token(report.get("result")) != "complete":
        failure_reason = "MVP cross-platform matrix reported non-complete result"
    elif not bool(baseline_status.get("match", False)):
        failure_reason = "MVP cross-platform baseline mismatch detected"
    comparison = _as_map(report.get("comparison"))
    return _make_step_summary(
        spec,
        step_no=step_no,
        result=result,
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=[CROSS_PLATFORM_REPORT_REL.replace("\\", "/"), CROSS_PLATFORM_BASELINE_REL.replace("\\", "/"), "docs/audit/MVP_CROSS_PLATFORM_FINAL.md"],
        observed_refusal_count=0,
        default_path_refusal_count=0,
        key_hashes={
            "cross_platform_report_fingerprint": _token(report.get("deterministic_fingerprint")),
            "comparison_fingerprint": _token(comparison.get("deterministic_fingerprint")),
            "portable_linked_parity_fingerprint": _token(_as_map(report.get("portable_linked_parity")).get("deterministic_fingerprint")),
        },
        metrics={
            "platform_count": len(_as_list(report.get("platform_rows"))),
            "mismatch_count": len(_as_list(comparison.get("mismatches"))),
        },
        notes=[
            "baseline_match={}".format(bool(baseline_status.get("match", False))),
            "hashes_match_across_platforms={}".format(bool(_as_map(comparison.get("assertions")).get("hashes_match_across_platforms", False))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _dist_verify_step(
    repo_root: str,
    spec: Mapping[str, object],
    *,
    step_no: int,
) -> dict:
    report = load_distribution_verify_report(repo_root, platform_tag="win64")
    if not report:
        report = build_distribution_verify_report(
            os.path.join(_norm(repo_root), "dist", "v0.0.0-mock", "win64", "dominium"),
            platform_tag="win64",
            repo_root=repo_root,
        )
        write_distribution_verify_outputs(repo_root, report)
    failure_reason = ""
    if _token(report.get("result")) != "complete":
        failure_reason = "DIST-2 bundle verification reported non-complete result"
    return _make_step_summary(
        spec,
        step_no=step_no,
        result="complete" if _token(report.get("result")) == "complete" else "refused",
        source_fingerprint=_token(report.get("deterministic_fingerprint")),
        source_paths=["data/audit/dist_verify_win64.json", "docs/audit/DIST_VERIFY_win64.md"],
        observed_refusal_count=int(len(_as_list(report.get("errors")))),
        default_path_refusal_count=0,
        key_hashes={
            "dist_verify_fingerprint": _token(report.get("deterministic_fingerprint")),
            "release_manifest_hash": _token(_as_map(report.get("key_hashes")).get("release_manifest_hash")),
            "filelist_hash": _token(_as_map(report.get("key_hashes")).get("filelist_hash")),
        },
        metrics={
            "error_count": len(_as_list(report.get("errors"))),
            "warning_count": len(_as_list(report.get("warnings"))),
        },
        notes=[
            "platform_tag={}".format(_token(report.get("platform_tag"))),
            "bundle_root={}".format(_token(report.get("bundle_root"))),
        ],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _forced_failure_step(spec: Mapping[str, object], *, step_no: int, message: str) -> dict:
    failure_reason = _token(message) or "forced convergence failure for test coverage"
    return _make_step_summary(
        spec,
        step_no=step_no,
        result="refused",
        source_fingerprint=canonical_sha256({"step_id": _token(spec.get("step_id")), "forced_failure": failure_reason}),
        source_paths=[],
        observed_refusal_count=1,
        default_path_refusal_count=1,
        notes=["forced failure injected for deterministic test coverage"],
        remediation=_default_remediation(spec, message=failure_reason),
        failure_reason=failure_reason,
    )


def _step_runner(step_id: str, *, prefer_cached_heavy: bool):
    mapping = {
        "validation_strict": _validation_step,
        "meta_stability": _meta_stability_step,
        "time_anchor": _time_anchor_step,
        "arch_audit": _arch_audit_step,
        "cap_neg_interop": _cap_neg_step,
        "pack_compat_stress": _pack_compat_step,
        "lib_stress": _lib_step,
        "product_boot_matrix": _product_boot_step,
        "ipc_attach_smoke": _ipc_attach_step,
        "supervisor_hardening": _supervisor_step,
        "mvp_smoke": lambda repo_root, spec, *, step_no: _mvp_smoke_step(repo_root, spec, step_no=step_no, prefer_cached=prefer_cached_heavy),
        "mvp_stress": lambda repo_root, spec, *, step_no: _mvp_stress_step(repo_root, spec, step_no=step_no, prefer_cached=prefer_cached_heavy),
        "mvp_cross_platform": lambda repo_root, spec, *, step_no: _mvp_cross_platform_step(repo_root, spec, step_no=step_no, prefer_cached=prefer_cached_heavy),
        "dist_verify": _dist_verify_step,
    }
    return mapping[str(step_id)]


def _collect_key_hashes(step_rows: Sequence[Mapping[str, object]]) -> dict:
    step_map = {_token(_as_map(item).get("step_id")): _as_map(item) for item in list(step_rows or [])}
    smoke_hashes = _as_map(_as_map(step_map.get("mvp_smoke")).get("key_hashes"))
    stress_hashes = _as_map(_as_map(step_map.get("mvp_stress")).get("key_hashes"))
    cross_hashes = _as_map(_as_map(step_map.get("mvp_cross_platform")).get("key_hashes"))
    ipc_hashes = _as_map(_as_map(step_map.get("ipc_attach_smoke")).get("key_hashes"))
    key_hashes = {
        "pack_lock_hash": _token(smoke_hashes.get("pack_lock_hash")),
        "contract_bundle_hash": _token(smoke_hashes.get("contract_bundle_hash")) or _token(stress_hashes.get("contract_bundle_hash")),
        "negotiation_record_hashes": {
            key: value
            for key, value in sorted(ipc_hashes.items(), key=lambda item: str(item[0]))
            if "negotiation_record_hash" in str(key)
        },
        "proof_anchor_hash": _token(smoke_hashes.get("proof_anchor_hash")) or _token(stress_hashes.get("proof_anchor_hashes")),
        "repro_bundle_hash": _token(smoke_hashes.get("repro_bundle_hash")),
        "cross_platform_comparison_fingerprint": _token(cross_hashes.get("comparison_fingerprint")),
        "deterministic_fingerprint": "",
    }
    key_hashes["deterministic_fingerprint"] = canonical_sha256(dict(key_hashes, deterministic_fingerprint=""))
    return key_hashes


def _render_final_markdown(report: Mapping[str, object]) -> str:
    row = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: RELEASE",
        "Replacement Target: regenerated convergence gate summary for pre-release validation",
        "",
        "# CONVERGENCE Final",
        "",
        "## Summary",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- report_id: `{}`".format(_token(row.get("report_id")) or CONVERGENCE_GATE_ID),
        "- step_count: `{}`".format(int(_as_int(row.get("step_count", 0), 0))),
        "- completed_step_count: `{}`".format(int(_as_int(row.get("completed_step_count", 0), 0))),
        "- default_path_refusal_count: `{}`".format(int(_as_int(_as_map(row.get("log_summary")).get("default_path_refusal_count", 0), 0))),
        "- default_path_degrade_count: `{}`".format(int(_as_int(_as_map(row.get("log_summary")).get("default_path_degrade_count", 0), 0))),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Step Results",
        "",
        "| # | Step | Result | Fingerprint |",
        "| --- | --- | --- | --- |",
    ]
    for item in _as_list(row.get("steps")):
        step = _as_map(item)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                int(_as_int(step.get("step_no", 0), 0)),
                _token(step.get("title")) or _token(step.get("step_id")),
                _token(step.get("result")),
                _token(step.get("deterministic_fingerprint")),
            )
        )
    lines.extend(("", "## Key Hashes", ""))
    key_hashes = _as_map(row.get("key_hashes"))
    if key_hashes:
        for key, value in sorted(key_hashes.items(), key=lambda item: str(item[0])):
            if str(key) == "negotiation_record_hashes":
                lines.append("- negotiation_record_hashes: `{}`".format(canonical_sha256(_as_map(value))))
            else:
                lines.append("- {}: `{}`".format(str(key), _token(value)))
    else:
        lines.append("- none")
    lines.extend(("", "## Refusal/Degrade Logs", ""))
    log_summary = _as_map(row.get("log_summary"))
    lines.append("- default_path_refusal_count: `{}`".format(int(_as_int(log_summary.get("default_path_refusal_count", 0), 0))))
    lines.append("- default_path_degrade_count: `{}`".format(int(_as_int(log_summary.get("default_path_degrade_count", 0), 0))))
    lines.append("- synthetic_refusal_count: `{}`".format(int(_as_int(log_summary.get("synthetic_refusal_count", 0), 0))))
    lines.append("- synthetic_degrade_count: `{}`".format(int(_as_int(log_summary.get("synthetic_degrade_count", 0), 0))))
    lines.extend(("", "## Remediation", ""))
    remediation_rows = [_as_map(item) for item in _as_list(row.get("remediation")) if _as_map(item)]
    if remediation_rows:
        for item in remediation_rows:
            lines.append(
                "- module=`{}` rule=`{}` refusal=`{}` command=`{}` {}".format(
                    _token(item.get("module")),
                    _token(item.get("rule_id")),
                    _token(item.get("refusal_code")) or "none",
                    _token(item.get("suggested_fix_command")),
                    _token(item.get("message")),
                ).rstrip()
            )
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def write_convergence_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    final_json_path: str = CONVERGENCE_FINAL_JSON_PATH,
    final_doc_path: str = CONVERGENCE_FINAL_DOC_PATH,
) -> dict[str, str]:
    root = _norm(repo_root)
    written = {
        "final_json_path": _rel(root, _write_json(_repo_abs(root, final_json_path), _as_map(report))),
        "final_doc_path": _rel(root, _write_text(_repo_abs(root, final_doc_path), _render_final_markdown(report))),
    }
    return written


def run_convergence_gate(
    repo_root: str,
    *,
    skip_cross_platform: bool = False,
    prefer_cached_heavy: bool = False,
    include_dist_verify: bool = False,
    step_json_dir: str = CONVERGENCE_STEP_JSON_DIR,
    step_doc_dir: str = CONVERGENCE_STEP_DOC_DIR,
    final_json_path: str = CONVERGENCE_FINAL_JSON_PATH,
    final_doc_path: str = CONVERGENCE_FINAL_DOC_PATH,
    selected_step_ids: Sequence[str] | None = None,
    force_fail_step_id: str = "",
    force_fail_message: str = "",
) -> dict:
    root = _norm(repo_root)
    include_cross_platform = not bool(skip_cross_platform)
    _step_lookup(include_cross_platform=include_cross_platform, include_dist_verify=include_dist_verify)
    ordered_specs = convergence_step_specs(include_cross_platform=include_cross_platform, include_dist_verify=include_dist_verify)
    if selected_step_ids:
        allowed_ids = {_token(item) for item in list(selected_step_ids or []) if _token(item)}
        ordered_specs = [dict(row) for row in ordered_specs if _token(row.get("step_id")) in allowed_ids]
    step_rows: list[dict] = []
    written_steps: list[dict] = []
    stopped_at_step_id = ""
    result = "complete"
    remediation: list[dict] = []
    for index, spec in enumerate(ordered_specs, start=1):
        step_id = _token(spec.get("step_id"))
        if step_id == _token(force_fail_step_id):
            step = _forced_failure_step(spec, step_no=index, message=force_fail_message)
        else:
            step = _step_runner(step_id, prefer_cached_heavy=prefer_cached_heavy)(root, spec, step_no=index)
        step_rows.append(step)
        written = _write_step_snapshot(root, step, json_dir=step_json_dir, doc_dir=step_doc_dir)
        written_steps.append({"step_id": step_id, **written})
        if _token(step.get("result")) != "complete":
            result = "refused"
            stopped_at_step_id = step_id
            remediation = [_as_map(item) for item in _as_list(step.get("remediation")) if _as_map(item)]
            break

    log_summary = {
        "default_path_refusal_count": int(sum(int(_as_int(_as_map(item).get("default_path_refusal_count", 0), 0)) for item in step_rows)),
        "default_path_degrade_count": int(sum(int(_as_int(_as_map(item).get("default_path_degrade_count", 0), 0)) for item in step_rows)),
        "synthetic_refusal_count": int(
            sum(
                int(_as_int(_as_map(item).get("observed_refusal_count", 0), 0))
                - int(_as_int(_as_map(item).get("default_path_refusal_count", 0), 0))
                for item in step_rows
            )
        ),
        "synthetic_degrade_count": int(
            sum(
                int(_as_int(_as_map(item).get("observed_degrade_count", 0), 0))
                - int(_as_int(_as_map(item).get("default_path_degrade_count", 0), 0))
                for item in step_rows
            )
        ),
    }
    report = {
        "report_id": CONVERGENCE_GATE_ID,
        "result": result,
        "step_order": [_token(item.get("step_id")) for item in ordered_specs],
        "step_count": len(ordered_specs),
        "completed_step_count": len(step_rows),
        "stopped_at_step_id": _token(stopped_at_step_id),
        "steps": step_rows,
        "step_outputs": written_steps,
        "log_summary": log_summary,
        "key_hashes": _collect_key_hashes(step_rows),
        "remediation": remediation,
        "deterministic_fingerprint": "",
    }
    planned_outputs = {
        "final_json_path": _rel(root, _repo_abs(root, final_json_path)),
        "final_doc_path": _rel(root, _repo_abs(root, final_doc_path)),
    }
    report["written_outputs"] = planned_outputs
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    written_outputs = write_convergence_outputs(
        root,
        report,
        final_json_path=final_json_path,
        final_doc_path=final_doc_path,
    )
    if written_outputs != planned_outputs:
        report["written_outputs"] = dict(written_outputs)
        report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
        write_convergence_outputs(
            root,
            report,
            final_json_path=final_json_path,
            final_doc_path=final_doc_path,
        )
    return report


def load_convergence_report(repo_root: str) -> dict:
    payload = _read_json(repo_root, CONVERGENCE_FINAL_JSON_PATH)
    if _token(payload.get("report_id")) == CONVERGENCE_GATE_ID:
        return payload
    return {}


def convergence_gate_violations(repo_root: str) -> list[dict]:
    payload = load_convergence_report(repo_root)
    violations: list[dict] = []
    if not payload:
        return [
            {
                "code": "convergence_report_missing",
                "file_path": CONVERGENCE_FINAL_JSON_PATH,
                "message": "convergence gate report is missing",
                "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            }
        ]
    expected_ids = convergence_step_ids(include_cross_platform=True)
    actual_ids = [_token(item) for item in _as_list(payload.get("step_order"))]
    if actual_ids != expected_ids:
        violations.append(
            {
                "code": "convergence_step_order_mismatch",
                "file_path": CONVERGENCE_FINAL_JSON_PATH,
                "message": "convergence gate step order drifted from the canonical run order",
                "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            }
        )
    if _token(payload.get("result")) != "complete":
        violations.append(
            {
                "code": "convergence_gate_not_complete",
                "file_path": CONVERGENCE_FINAL_JSON_PATH,
                "message": "convergence gate must report result=complete",
                "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            }
        )
    for item in _as_list(payload.get("steps")):
        step = _as_map(item)
        if _token(step.get("result")) == "complete":
            continue
        violations.append(
            {
                "code": "convergence_step_failed",
                "file_path": CONVERGENCE_FINAL_JSON_PATH,
                "message": "{}: {}".format(_token(step.get("step_id")), _token(step.get("failure_reason")) or "step failed"),
                "rule_id": "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE",
            }
        )
    return sorted(
        violations,
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


__all__ = [
    "CONVERGENCE_FINAL_DOC_PATH",
    "CONVERGENCE_FINAL_JSON_PATH",
    "CONVERGENCE_GATE_ID",
    "CONVERGENCE_STEP_DOC_DIR",
    "CONVERGENCE_STEP_JSON_DIR",
    "CONVERGENCE_TOOL_PATH",
    "convergence_gate_violations",
    "convergence_step_ids",
    "convergence_step_specs",
    "load_convergence_report",
    "run_convergence_gate",
    "write_convergence_outputs",
]
