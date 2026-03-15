"""Deterministic NUMERIC-DISCIPLINE-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from tools.audit.arch_audit_common import (
    build_numeric_scan_report,
    render_numeric_scan_report,
    run_arch_audit,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "NUMERIC_DISCIPLINE0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "engine", "NUMERIC_DISCIPLINE_MODEL.md")
SCAN_REPORT_DOC_REL = os.path.join("docs", "audit", "NUMERIC_SCAN_REPORT.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "NUMERIC_DISCIPLINE_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "numeric_discipline_report.json")
TOLERANCE_REGISTRY_REL = os.path.join("data", "registries", "tolerance_registry.json")
LAST_REVIEWED = "2026-03-14"

TRUTH_PATH_NUMERIC = (
    "src/meta/numeric.py",
    "src/time/time_mapping_engine.py",
    "src/physics/momentum_engine.py",
    "src/physics/energy/energy_ledger_engine.py",
    "src/mobility/micro/free_motion_solver.py",
    "src/astro/illumination/illumination_geometry_engine.py",
    "src/astro/ephemeris/kepler_proxy_engine.py",
)
REVIEWED_NUMERIC_BRIDGES = {
    "src/geo/kernel/geo_kernel.py": "projection/query bridge with deterministic quantization",
    "src/geo/metric/metric_engine.py": "bounded geodesic approximation bridge",
    "src/process/qc/qc_engine.py": "qc/reporting quantization bridge",
    "src/mobility/micro/constrained_motion_solver.py": "heading derivation bridge with integer output",
    "src/mobility/geometry/geometry_engine.py": "grid snap bridge with integer output",
    "src/meta/instrumentation/instrumentation_engine.py": "measurement quantization bridge",
}
RENDER_ONLY_NUMERIC = (
    "src/client/render/renderers/software_renderer.py",
    "src/platform/platform_input_routing.py",
    "src/platform/platform_window.py",
)
TOOLING_ONLY_NUMERIC = (
    "tools/audit/",
    "tools/dist/",
    "tools/release/",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


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


def _tolerance_rows(payload: Mapping[str, object] | None) -> list[dict]:
    body = _as_map(payload)
    rows = _as_list(_as_map(body.get("record")).get("tolerances"))
    return sorted((dict(row) for row in rows if isinstance(row, Mapping)), key=lambda row: _token(row.get("tol_id")))


def build_numeric_discipline_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    arch_report = run_arch_audit(root)
    numeric_scan = build_numeric_scan_report(arch_report)
    tolerance_registry = _read_json(os.path.join(root, TOLERANCE_REGISTRY_REL))
    tolerance_rows = _tolerance_rows(tolerance_registry)
    report = {
        "report_id": "numeric.discipline.v1",
        "result": _token(numeric_scan.get("result")) or "complete",
        "release_status": _token(numeric_scan.get("release_status")) or "pass",
        "last_reviewed": LAST_REVIEWED,
        "numeric_scan_report": dict(numeric_scan),
        "tolerance_registry_hash": canonical_sha256(tolerance_registry) if tolerance_registry else "",
        "tolerance_ids": [_token(row.get("tol_id")) for row in tolerance_rows if _token(row.get("tol_id"))],
        "truth_path_numeric": list(TRUTH_PATH_NUMERIC),
        "reviewed_numeric_bridges": dict(REVIEWED_NUMERIC_BRIDGES),
        "render_only_numeric": list(RENDER_ONLY_NUMERIC),
        "tooling_only_numeric": list(TOOLING_ONLY_NUMERIC),
        "ready_for_concurrency_contract_0": not bool(numeric_scan.get("blocking_finding_count", 0)),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_numeric_discipline_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    numeric_scan = _as_map(payload.get("numeric_scan_report"))
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Release-pinned engine numeric policy and compiler matrix documentation.",
        "",
        "# Numeric Discipline Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- tolerance_registry_hash: `{}`".format(_token(payload.get("tolerance_registry_hash"))),
        "- numeric_scan_fingerprint: `{}`".format(_token(numeric_scan.get("deterministic_fingerprint"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Numeric Domains",
        "",
        "### Truth-path numeric",
    ]
    for rel_path in list(payload.get("truth_path_numeric") or []):
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(["", "### Reviewed numeric bridges"])
    bridges = _as_map(payload.get("reviewed_numeric_bridges"))
    for rel_path in sorted(bridges.keys()):
        lines.append("- `{}`: {}".format(_token(rel_path), _token(bridges.get(rel_path))))
    lines.extend(["", "### Render-only numeric"])
    for rel_path in list(payload.get("render_only_numeric") or []):
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(["", "### Tooling-only numeric"])
    for rel_path in list(payload.get("tooling_only_numeric") or []):
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(["", "## Tolerances", ""])
    for tol_id in list(payload.get("tolerance_ids") or []):
        lines.append("- `{}`".format(_token(tol_id)))
    lines.extend(
        [
            "",
            "## Enforcement Coverage",
            "",
            "- ARCH-AUDIT numeric checks: `float_in_truth_scan`, `noncanonical_serialization_scan`, `compiler_flag_scan`",
            "- RepoX numeric rules: `INV-FLOAT-ONLY-IN-RENDER`, `INV-CANONICAL-NUMERIC-SERIALIZATION`, `INV-SAFE-FLOAT-COMPILER-FLAGS`",
            "- AuditX numeric analyzers: `E525`, `E526`, `E527`",
            "- TestX numeric coverage: fixed-point ops, trig lookup, hash stability, truth-namespace float scan",
            "",
            "## Readiness",
            "",
            "- CONCURRENCY-CONTRACT-0: `{}`".format("ready" if bool(payload.get("ready_for_concurrency_contract_0", False)) else "blocked"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_numeric_discipline_outputs(repo_root: str) -> dict:
    root = _norm(repo_root)
    report = build_numeric_discipline_report(root)
    numeric_scan = _as_map(report.get("numeric_scan_report"))
    return {
        "report": report,
        "retro_audit_doc_path": _norm_rel(os.path.join(root, RETRO_AUDIT_DOC_REL)),
        "doctrine_doc_path": _norm_rel(os.path.join(root, DOCTRINE_DOC_REL)),
        "scan_report_doc_path": _norm_rel(_write_text(os.path.join(root, SCAN_REPORT_DOC_REL), render_numeric_scan_report(numeric_scan))),
        "baseline_doc_path": _norm_rel(_write_text(os.path.join(root, BASELINE_DOC_REL), render_numeric_discipline_baseline(report))),
        "report_json_path": _norm_rel(_write_json(os.path.join(root, REPORT_JSON_REL), report)),
    }


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "SCAN_REPORT_DOC_REL",
    "TOLERANCE_REGISTRY_REL",
    "build_numeric_discipline_report",
    "render_numeric_discipline_baseline",
    "write_numeric_discipline_outputs",
]
