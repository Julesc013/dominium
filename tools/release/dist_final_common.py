"""Deterministic Ω-10 DIST final plan helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


OMEGA10_RETRO_AUDIT_REL = os.path.join("docs", "audit", "OMEGA10_RETRO_AUDIT.md")
DIST_FINAL_PLAN_DOC_REL = os.path.join("docs", "release", "DIST_FINAL_PLAN_v0_0_0_mock.md")
DIST_FINAL_CHECKLIST_DOC_REL = os.path.join("docs", "release", "DIST_FINAL_CHECKLIST.md")
DIST_FINAL_EXPECTED_ARTIFACTS_REL = os.path.join("data", "release", "dist_final_expected_artifacts.json")
DIST_FINAL_DRYRUN_DOC_REL = os.path.join("docs", "audit", "DIST_FINAL_DRYRUN.md")
DIST_FINAL_DRYRUN_TOOL_REL = os.path.join("tools", "release", "tool_dist_final_dryrun")
DIST_FINAL_DRYRUN_TOOL_PY_REL = os.path.join("tools", "release", "tool_dist_final_dryrun.py")
OMEGA10_FINAL_DOC_REL = os.path.join("docs", "audit", "OMEGA10_FINAL.md")

DEFAULT_RELEASE_ID = "v0.0.0-mock"
DEFAULT_PLATFORM_TAG = "win64"

REQUIRED_TOOL_PATHS = (
    os.path.join("tools", "convergence", "tool_run_convergence_gate.py"),
    os.path.join("tools", "audit", "tool_run_arch_audit.py"),
    os.path.join("tools", "worldgen", "tool_verify_worldgen_lock"),
    os.path.join("tools", "worldgen", "tool_verify_worldgen_lock.py"),
    os.path.join("tools", "mvp", "tool_verify_baseline_universe"),
    os.path.join("tools", "mvp", "tool_verify_baseline_universe.py"),
    os.path.join("tools", "mvp", "tool_verify_gameplay_loop"),
    os.path.join("tools", "mvp", "tool_verify_gameplay_loop.py"),
    os.path.join("tools", "mvp", "tool_run_disaster_suite"),
    os.path.join("tools", "mvp", "tool_run_disaster_suite.py"),
    os.path.join("tools", "mvp", "tool_verify_ecosystem"),
    os.path.join("tools", "mvp", "tool_verify_ecosystem.py"),
    os.path.join("tools", "mvp", "tool_run_update_sim"),
    os.path.join("tools", "mvp", "tool_run_update_sim.py"),
    os.path.join("tools", "security", "tool_run_trust_strict_suite"),
    os.path.join("tools", "security", "tool_run_trust_strict_suite.py"),
    os.path.join("tools", "perf", "tool_run_performance_envelope.py"),
    os.path.join("tools", "performx", "performx.py"),
    os.path.join("tools", "setup", "setup_cli.py"),
    os.path.join("tools", "dist", "tool_assemble_dist_tree.py"),
    os.path.join("tools", "dist", "tool_verify_distribution.py"),
    os.path.join("tools", "dist", "tool_run_clean_room.py"),
    os.path.join("tools", "dist", "tool_run_platform_matrix.py"),
    os.path.join("tools", "dist", "tool_run_version_interop.py"),
    os.path.join("tools", "release", "tool_generate_release_manifest.py"),
    os.path.join("tools", "release", "tool_run_release_index_policy.py"),
    os.path.join("tools", "release", "tool_run_archive_policy.py"),
    os.path.join("tools", "release", "tool_build_offline_archive"),
    os.path.join("tools", "release", "tool_build_offline_archive.py"),
    os.path.join("tools", "release", "tool_verify_offline_archive"),
    os.path.join("tools", "release", "tool_verify_offline_archive.py"),
    DIST_FINAL_DRYRUN_TOOL_REL,
    DIST_FINAL_DRYRUN_TOOL_PY_REL,
)

REQUIRED_REGISTRY_PATHS = (
    os.path.join("data", "registries", "component_graph_registry.json"),
    os.path.join("data", "registries", "install_profile_registry.json"),
    os.path.join("data", "registries", "release_resolution_policy_registry.json"),
    os.path.join("data", "registries", "archive_policy_registry.json"),
    os.path.join("data", "registries", "worldgen_lock_registry.json"),
    os.path.join("data", "registries", "trust_root_registry.json"),
    os.path.join("data", "registries", "migration_policy_registry.json"),
    os.path.join("data", "registries", "toolchain_matrix_registry.json"),
    os.path.join("data", "registries", "toolchain_test_profile_registry.json"),
    os.path.join("data", "registries", "omega_artifact_registry.json"),
    os.path.join("data", "governance", "governance_profile.json"),
)

REQUIRED_DOC_PATHS = (
    OMEGA10_RETRO_AUDIT_REL,
    DIST_FINAL_PLAN_DOC_REL,
    DIST_FINAL_CHECKLIST_DOC_REL,
    os.path.join("docs", "release", "DISTRIBUTION_MODEL.md"),
    os.path.join("docs", "release", "DIST_BUNDLE_ASSEMBLY.md"),
    os.path.join("docs", "release", "DIST_VERIFICATION_RULES.md"),
    os.path.join("docs", "release", "RELEASE_INDEX_RESOLUTION_POLICY.md"),
    os.path.join("docs", "release", "ARCHIVE_AND_RETENTION_POLICY.md"),
    os.path.join("docs", "release", "OFFLINE_ARCHIVE_MODEL_v0_0_0.md"),
    os.path.join("docs", "omega", "OMEGA_PLAN.md"),
    os.path.join("docs", "omega", "OMEGA_GATES.md"),
)

REQUIRED_BASELINE_PATHS = (
    os.path.join("data", "baselines", "worldgen", "baseline_worldgen_snapshot.json"),
    os.path.join("data", "audit", "worldgen_lock_verify.json"),
    os.path.join("data", "baselines", "universe", "baseline_universe_snapshot.json"),
    os.path.join("data", "audit", "baseline_universe_verify.json"),
    os.path.join("data", "baselines", "gameplay", "gameplay_loop_snapshot.json"),
    os.path.join("data", "audit", "gameplay_verify.json"),
    os.path.join("data", "regression", "disaster_suite_baseline.json"),
    os.path.join("data", "audit", "disaster_suite_run.json"),
    os.path.join("data", "regression", "ecosystem_verify_baseline.json"),
    os.path.join("data", "audit", "ecosystem_verify_run.json"),
    os.path.join("data", "regression", "update_sim_baseline.json"),
    os.path.join("data", "audit", "update_sim_run.json"),
    os.path.join("data", "regression", "trust_strict_baseline.json"),
    os.path.join("data", "audit", "trust_strict_run.json"),
    os.path.join("data", "regression", "archive_baseline.json"),
    os.path.join("data", "audit", "offline_archive_verify.json"),
    os.path.join("docs", "audit", "TOOLCHAIN_MATRIX_BASELINE.md"),
    os.path.join("artifacts", "toolchain_runs", "winnt-msvc-x86_64-vs2026", "run.5ea8970d1739f5c2", "run_manifest.json"),
    os.path.join("artifacts", "toolchain_runs", "winnt-msvc-x86_64-vs2026", "run.5ea8970d1739f5c2", "hashes.json"),
    os.path.join("docs", "audit", "PERFORMANCE_ENVELOPE_BASELINE.md"),
    os.path.join("docs", "audit", "performance", "PERFORMX_BASELINE.json"),
    os.path.join("data", "regression", "mvp_stress_baseline.json"),
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return _norm(repo_root)
    if os.path.isabs(token):
        return _norm(token)
    return _norm(os.path.join(repo_root, token.replace("/", os.sep)))


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    _ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _path_row(repo_root: str, rel_path: str, category: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    return {
        "category": _token(category),
        "path": _norm_rel(rel_path),
        "exists": os.path.exists(abs_path),
    }


def _collect_rows(repo_root: str, rel_paths: tuple[str, ...], category: str) -> list[dict]:
    return [_path_row(repo_root, rel_path, category) for rel_path in list(rel_paths or ())]


def load_expected_artifacts(repo_root: str) -> dict:
    return _load_json(_repo_abs(repo_root, DIST_FINAL_EXPECTED_ARTIFACTS_REL))


def _expected_artifact_issues(payload: Mapping[str, object] | None) -> list[dict]:
    item = _as_map(payload)
    issues: list[dict] = []
    if _token(item.get("release_id")) != DEFAULT_RELEASE_ID:
        issues.append(
            {
                "code": "release_id_mismatch",
                "message": "expected-artifacts release_id must match the frozen mock release id",
            }
        )
    outputs = list(item.get("expected_outputs") or [])
    if not outputs:
        issues.append(
            {
                "code": "expected_outputs_missing",
                "message": "expected-artifacts checklist must declare expected_outputs",
            }
        )
        return issues
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for row in outputs:
        artifact = _as_map(row)
        artifact_id = _token(artifact.get("artifact_id"))
        path = _norm_rel(artifact.get("path"))
        if not artifact_id:
            issues.append({"code": "artifact_id_missing", "message": "expected artifact row is missing artifact_id"})
        elif artifact_id in seen_ids:
            issues.append({"code": "artifact_id_duplicate", "message": "expected artifact id '{}' is duplicated".format(artifact_id)})
        seen_ids.add(artifact_id)
        if not path:
            issues.append({"code": "artifact_path_missing", "message": "expected artifact row '{}' is missing path".format(artifact_id or "<unknown>")})
        elif path in seen_paths:
            issues.append({"code": "artifact_path_duplicate", "message": "expected artifact path '{}' is duplicated".format(path)})
        seen_paths.add(path)
    if not list(item.get("omega_inputs") or []):
        issues.append(
            {
                "code": "omega_inputs_missing",
                "message": "expected-artifacts checklist must declare omega_inputs",
            }
        )
    return issues


def build_dist_final_dryrun_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    required_docs = _collect_rows(root, REQUIRED_DOC_PATHS, "doc")
    required_tools = _collect_rows(root, REQUIRED_TOOL_PATHS, "tool")
    required_registries = _collect_rows(root, REQUIRED_REGISTRY_PATHS, "registry")
    required_baselines = _collect_rows(root, REQUIRED_BASELINE_PATHS, "baseline")
    expected_artifacts = load_expected_artifacts(root)
    artifact_issues = _expected_artifact_issues(expected_artifacts)
    missing_paths = sorted(
        row["path"]
        for row in list(required_docs + required_tools + required_registries + required_baselines)
        if not bool(row.get("exists"))
    )
    report = {
        "artifact_issue_count": len(artifact_issues),
        "artifact_issues": artifact_issues,
        "deterministic_fingerprint": "",
        "expected_artifact_count": len(list(_as_map(expected_artifacts).get("expected_outputs") or [])),
        "expected_artifacts_path": _norm_rel(DIST_FINAL_EXPECTED_ARTIFACTS_REL),
        "missing_count": len(missing_paths),
        "missing_paths": missing_paths,
        "release_id": DEFAULT_RELEASE_ID,
        "required_baselines": required_baselines,
        "required_docs": required_docs,
        "required_registries": required_registries,
        "required_tools": required_tools,
        "result": "complete" if not missing_paths and not artifact_issues else "refused",
        "stage_id": "OMEGA-10",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_dist_final_dryrun(report: Mapping[str, object] | None) -> str:
    rows = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-26",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Ω-11 execution ledger and final mock signoff",
        "",
        "# DIST Final Dry Run",
        "",
        "- result: `{}`".format(_token(rows.get("result")) or "refused"),
        "- release_id: `{}`".format(_token(rows.get("release_id")) or DEFAULT_RELEASE_ID),
        "- missing_count: `{}`".format(int(rows.get("missing_count", 0) or 0)),
        "- artifact_issue_count: `{}`".format(int(rows.get("artifact_issue_count", 0) or 0)),
        "- expected_artifact_count: `{}`".format(int(rows.get("expected_artifact_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(rows.get("deterministic_fingerprint"))),
        "",
        "## Required Docs",
        "",
    ]
    for row in list(rows.get("required_docs") or []):
        item = _as_map(row)
        lines.append("- `{}` -> exists=`{}`".format(_token(item.get("path")), "yes" if bool(item.get("exists")) else "no"))
    lines.extend(["", "## Required Tools", ""])
    for row in list(rows.get("required_tools") or []):
        item = _as_map(row)
        lines.append("- `{}` -> exists=`{}`".format(_token(item.get("path")), "yes" if bool(item.get("exists")) else "no"))
    lines.extend(["", "## Required Registries", ""])
    for row in list(rows.get("required_registries") or []):
        item = _as_map(row)
        lines.append("- `{}` -> exists=`{}`".format(_token(item.get("path")), "yes" if bool(item.get("exists")) else "no"))
    lines.extend(["", "## Required Baselines", ""])
    for row in list(rows.get("required_baselines") or []):
        item = _as_map(row)
        lines.append("- `{}` -> exists=`{}`".format(_token(item.get("path")), "yes" if bool(item.get("exists")) else "no"))
    lines.extend(["", "## Missing Paths", ""])
    missing_paths = list(rows.get("missing_paths") or [])
    if not missing_paths:
        lines.append("- none")
    else:
        for path in missing_paths:
            lines.append("- `{}`".format(_token(path)))
    lines.extend(["", "## Expected Artifact Checklist Issues", ""])
    artifact_issues = list(rows.get("artifact_issues") or [])
    if not artifact_issues:
        lines.append("- none")
    else:
        for row in artifact_issues:
            item = _as_map(row)
            lines.append("- `{}`: {}".format(_token(item.get("code")), _token(item.get("message"))))
    lines.append("")
    return "\n".join(lines)


def write_dist_final_dryrun_doc(repo_root: str, report: Mapping[str, object] | None, *, doc_path: str = "") -> str:
    root = _norm(repo_root)
    target = _repo_abs(root, doc_path or DIST_FINAL_DRYRUN_DOC_REL)
    return _write_text(target, render_dist_final_dryrun(report) + "\n")


__all__ = [
    "DEFAULT_PLATFORM_TAG",
    "DEFAULT_RELEASE_ID",
    "DIST_FINAL_CHECKLIST_DOC_REL",
    "DIST_FINAL_DRYRUN_DOC_REL",
    "DIST_FINAL_DRYRUN_TOOL_PY_REL",
    "DIST_FINAL_DRYRUN_TOOL_REL",
    "DIST_FINAL_EXPECTED_ARTIFACTS_REL",
    "DIST_FINAL_PLAN_DOC_REL",
    "OMEGA10_FINAL_DOC_REL",
    "OMEGA10_RETRO_AUDIT_REL",
    "build_dist_final_dryrun_report",
    "load_expected_artifacts",
    "render_dist_final_dryrun",
    "write_dist_final_dryrun_doc",
]
