"""Deterministic unified validation pipeline."""

from __future__ import annotations

import json
import os
import shutil
import sys
from collections import Counter
from functools import lru_cache
from typing import Callable, Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat import build_product_descriptor, negotiate_product_endpoints, verify_recorded_negotiation  # noqa: E402
from src.lib.artifact import validate_artifact_manifest  # noqa: E402
from src.lib.instance import validate_instance_manifest  # noqa: E402
from src.lib.install import default_install_registry_path, verify_install_registry, validate_install_manifest  # noqa: E402
from src.lib.save import validate_save_manifest  # noqa: E402
from src.meta.identity import validate_identity_repo  # noqa: E402
from src.meta.stability import validate_all_registries, validate_pack_compat  # noqa: E402
from tools.audit.arch_audit_common import run_arch_audit, scan_determinism  # noqa: E402
from tools.compatx.core.semantic_contract_validator import (  # noqa: E402
    build_default_universe_contract_bundle,
    load_semantic_contract_registry,
    registry_hash,
    validate_semantic_contract_registry,
    validate_universe_contract_bundle,
)
from tools.mvp import build_pack_lock_payload, validate_pack_lock_payload  # noqa: E402
from tools.mvp.cross_platform_gate_common import maybe_load_cached_mvp_cross_platform_report  # noqa: E402
from tools.review.repo_inventory_common import load_or_run_inventory_report  # noqa: E402
from tools.time.time_anchor_common import verify_compaction_anchor_alignment, verify_longrun_ticks  # noqa: E402
from tools.meta.identity_common import BASELINE_DOC_REL as IDENTITY_BASELINE_DOC_REL  # noqa: E402
from tools.meta.identity_common import REPORT_JSON_REL as IDENTITY_REPORT_JSON_REL  # noqa: E402
from tools.meta.identity_common import STRICT_MISSING_POLICY_ACTIVE  # noqa: E402
from tools.meta.identity_common import write_identity_artifacts  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.compatx.check import run_compatx_check  # noqa: E402
from tools.xstack.compatx.validator import validate_instance  # noqa: E402


VALIDATION_SUITE_REGISTRY_REL = os.path.join("data", "registries", "validation_suite_registry.json")
VALIDATION_INVENTORY_DOC_PATH = os.path.join("docs", "audit", "VALIDATION_INVENTORY.md")
VALIDATION_PIPELINE_DOC_PATH = os.path.join("docs", "validation", "VALIDATION_PIPELINE.md")
VALIDATION_REPORT_DOC_TEMPLATE = os.path.join("docs", "audit", "VALIDATION_REPORT_{profile}.md")
VALIDATION_REPORT_JSON_TEMPLATE = os.path.join("data", "audit", "validation_report_{profile}.json")
VALIDATION_FINAL_DOC_TEMPLATE = os.path.join("docs", "audit", "VALIDATION_UNIFY_FINAL.md")
VALIDATION_REPORT_ID = "validation.pipeline.v1"
VALIDATION_INVENTORY_ID = "validation.inventory.v1"
PROFILE_ORDER = ("FAST", "STRICT", "FULL")
VALIDATION_WORK_ROOT_REL = os.path.join("build", "tmp", "validation_unify")
GOVERNED_SCHEMA_NAMES: tuple[str, ...] = (
    "epoch_anchor_record",
    "manifest",
    "pack_compat_manifest",
    "pack_compatibility_report",
    "pack_lock",
    "pack_manifest",
    "stability_marker",
    "universal_identity_block",
    "universe_contract_bundle",
    "validation_result",
)
PACK_COMPAT_FILENAMES = ("pack.compat.json",)
RELEASE_LIBRARY_ROOTS = ("dist", "installs", "instances", "saves", "artifacts")
RELEASE_PACK_LOCK_REL = os.path.join("dist", "locks", "pack_lock.mvp_default.json")


LEGACY_VALIDATION_SURFACE_SPECS: tuple[dict, ...] = (
    {
        "surface_id": "legacy.validate_all_cpp",
        "path": "tools/validation/validate_all_main.cpp",
        "purpose": "Legacy compiled aggregate validator entrypoint.",
        "inputs": ["workspace tree", "validation fixtures"],
        "outputs": ["process exit code", "stdout report"],
        "overlaps": ["validate.determinism", "validate.arch_audit"],
        "mapped_suite_id": "validate.determinism",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "src/validation/validation_engine.py::validate.determinism",
    },
    {
        "surface_id": "legacy.validation_registry_cpp",
        "path": "tools/validation/validators_registry.cpp",
        "purpose": "Legacy validator registration table for compiled aggregate validation.",
        "inputs": ["compiled validator set"],
        "outputs": ["validator registry wiring"],
        "overlaps": ["validate.determinism"],
        "mapped_suite_id": "validate.determinism",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "data/registries/validation_suite_registry.json",
    },
    {
        "surface_id": "legacy.hygiene_validate_cli",
        "path": "tools/validate/hygiene_validate_cli.cpp",
        "purpose": "Legacy hygiene validation CLI entrypoint.",
        "inputs": ["workspace tree"],
        "outputs": ["process exit code", "stdout report"],
        "overlaps": ["validate.arch_audit"],
        "mapped_suite_id": "validate.arch_audit",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/audit/tool_run_arch_audit.py",
    },
    {
        "surface_id": "legacy.validator_main_cpp",
        "path": "tools/validator/validator_main.cpp",
        "purpose": "Legacy standalone validator main focused on schema-style checks.",
        "inputs": ["authored payloads"],
        "outputs": ["process exit code", "stdout report"],
        "overlaps": ["validate.schemas"],
        "mapped_suite_id": "validate.schemas",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/xstack/compatx/check.py",
    },
    {
        "surface_id": "legacy.coredata_validate",
        "path": "tools/coredata_validate/coredata_validate_main.cpp",
        "purpose": "Legacy coredata validation executable.",
        "inputs": ["authoring roots", "pack roots"],
        "outputs": ["process exit code", "stdout report"],
        "overlaps": ["validate.schemas", "validate.registries"],
        "mapped_suite_id": "validate.schemas",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/xstack/compatx/check.py",
    },
    {
        "surface_id": "legacy.data_validate_c",
        "path": "tools/data_validate/data_validate_main.c",
        "purpose": "Legacy data TLV validation entrypoint.",
        "inputs": ["binary payload", "schema id", "schema version"],
        "outputs": ["process exit code", "stdout report"],
        "overlaps": ["validate.schemas"],
        "mapped_suite_id": "validate.schemas",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/xstack/compatx/check.py",
    },
    {
        "surface_id": "legacy.ci_validate_all_py",
        "path": "tools/ci/validate_all.py",
        "purpose": "Legacy wrapper that locates and shells out to validate_all.",
        "inputs": ["compiled validate_all binary"],
        "outputs": ["subprocess exit code", "stdout passthrough"],
        "overlaps": ["validate.determinism"],
        "mapped_suite_id": "validate.determinism",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/validation/tool_run_validation.py",
    },
    {
        "surface_id": "legacy.compatx_cli",
        "path": "tools/compatx/compatx.py",
        "purpose": "Legacy compatibility validation CLI for schema, pack, and semantic contract checks.",
        "inputs": ["compat registries", "bundle paths"],
        "outputs": ["json to stdout", "audit docs"],
        "overlaps": ["validate.contracts", "validate.packs"],
        "mapped_suite_id": "validate.contracts",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.compatx_check",
        "path": "tools/xstack/compatx/check.py",
        "purpose": "Deterministic schema/version check surface.",
        "inputs": ["schemas", "CompatX version registry"],
        "outputs": ["structured pass/fail report"],
        "overlaps": ["validate.schemas"],
        "mapped_suite_id": "validate.schemas",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.domain_validate",
        "path": "tools/domain/tool_domain_validate.py",
        "purpose": "Domain/contract/solver structural registry validator.",
        "inputs": ["domain registries"],
        "outputs": ["structured pass/fail report"],
        "overlaps": ["validate.registries"],
        "mapped_suite_id": "validate.registries",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "src/meta/stability/stability_validator.py",
    },
    {
        "surface_id": "legacy.fab_validate",
        "path": "tools/fab/fab_validate.py",
        "purpose": "Legacy fabrication authoring validator.",
        "inputs": ["fabrication JSON payload"],
        "outputs": ["json to stdout"],
        "overlaps": ["validate.schemas", "validate.registries"],
        "mapped_suite_id": "validate.registries",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "src/meta/stability/stability_validator.py",
    },
    {
        "surface_id": "legacy.worldgen_validation_checker",
        "path": "tools/worldgen_offline/validation_checker.py",
        "purpose": "Legacy output comparison validator for offline worldgen tooling.",
        "inputs": ["expected JSON", "actual JSON"],
        "outputs": ["mismatch report"],
        "overlaps": ["validate.determinism"],
        "mapped_suite_id": "validate.determinism",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/audit/tool_run_arch_audit.py",
    },
    {
        "surface_id": "legacy.graph_validate",
        "path": "tools/core/tool_graph_validate.py",
        "purpose": "Legacy graph payload validator.",
        "inputs": ["graph payloads", "schema ids"],
        "outputs": ["json report"],
        "overlaps": ["validate.schemas"],
        "mapped_suite_id": "validate.schemas",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "tools/xstack/compatx/check.py",
    },
    {
        "surface_id": "legacy.stability_validator",
        "path": "src/meta/stability/stability_validator.py",
        "purpose": "META-STABILITY registry and pack.compat validation surface.",
        "inputs": ["registry JSON", "pack.compat manifests"],
        "outputs": ["structured validation report"],
        "overlaps": ["validate.registries"],
        "mapped_suite_id": "validate.registries",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.pack_verification_pipeline",
        "path": "src/packs/compat/pack_verification_pipeline.py",
        "purpose": "PACK-COMPAT verification and pack lock generation surface.",
        "inputs": ["dist root", "bundle selection", "contract bundle"],
        "outputs": ["pack compatibility report", "pack lock"],
        "overlaps": ["validate.packs"],
        "mapped_suite_id": "validate.packs",
        "adapter_mode": "coverage_adapter",
        "status": "deprecated",
        "replacement_target": "src/validation/validation_engine.py::validate.packs_release_lock",
    },
    {
        "surface_id": "legacy.capability_negotiation",
        "path": "src/compat/capability_negotiation.py",
        "purpose": "Capability negotiation and record verification engine.",
        "inputs": ["endpoint descriptors", "contract bundle hash"],
        "outputs": ["negotiation record", "verification result"],
        "overlaps": ["validate.negotiation"],
        "mapped_suite_id": "validate.negotiation",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.time_verify",
        "path": "tools/time/tool_verify_longrun_ticks.py",
        "purpose": "TIME-ANCHOR long-run verification entrypoint.",
        "inputs": ["time anchor policy", "anchor artifacts"],
        "outputs": ["json verification report"],
        "overlaps": ["validate.time_anchor"],
        "mapped_suite_id": "validate.time_anchor",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.time_compaction_check",
        "path": "tools/time/tool_compaction_anchor_check.py",
        "purpose": "TIME-ANCHOR compaction boundary verifier.",
        "inputs": ["provenance windows", "anchor rows"],
        "outputs": ["json compaction report"],
        "overlaps": ["validate.time_anchor"],
        "mapped_suite_id": "validate.time_anchor",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.arch_audit",
        "path": "tools/audit/tool_run_arch_audit.py",
        "purpose": "ARCH-AUDIT constitutional architecture validator.",
        "inputs": ["repo tree", "registry reports"],
        "outputs": ["markdown report", "json report"],
        "overlaps": ["validate.arch_audit", "validate.determinism"],
        "mapped_suite_id": "validate.arch_audit",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.install_validator",
        "path": "src/lib/install/install_validator.py",
        "purpose": "Install manifest and install registry validator.",
        "inputs": ["install.manifest.json", "install registry"],
        "outputs": ["structured validation report"],
        "overlaps": ["validate.library"],
        "mapped_suite_id": "validate.library",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.instance_validator",
        "path": "src/lib/instance/instance_validator.py",
        "purpose": "Instance manifest validator.",
        "inputs": ["instance.manifest.json"],
        "outputs": ["structured validation report"],
        "overlaps": ["validate.library"],
        "mapped_suite_id": "validate.library",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.save_validator",
        "path": "src/lib/save/save_validator.py",
        "purpose": "Save manifest validator.",
        "inputs": ["save.manifest.json", "contract bundle", "pack lock"],
        "outputs": ["structured validation report"],
        "overlaps": ["validate.library"],
        "mapped_suite_id": "validate.library",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
    {
        "surface_id": "legacy.artifact_validator",
        "path": "src/lib/artifact/artifact_validator.py",
        "purpose": "Artifact manifest validator.",
        "inputs": ["artifact.manifest.json"],
        "outputs": ["structured validation report"],
        "overlaps": ["validate.library"],
        "mapped_suite_id": "validate.library",
        "adapter_mode": "direct_python",
        "status": "active_adapter",
        "replacement_target": "src/validation/validation_engine.py",
    },
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = str(rel_path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _reset_dir(path: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    if os.path.isdir(target):
        shutil.rmtree(target)
    os.makedirs(target, exist_ok=True)
    return target


def _copy_file(src_path: str, dst_path: str) -> None:
    parent = os.path.dirname(dst_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    shutil.copy2(src_path, dst_path)


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return _norm(path)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm(path)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _report_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def _sorted_strings(values: Iterable[object]) -> list[str]:
    return sorted({_token(value) for value in list(values or []) if _token(value)})


def _scoped_schema_workspace(repo_root: str, *, schema_names: Iterable[str], workspace_id: str = "schema_scope") -> str:
    root = _repo_root(repo_root)
    workspace = _reset_dir(_repo_abs(root, os.path.join(VALIDATION_WORK_ROOT_REL, workspace_id)))
    schemas_dir = os.path.join(workspace, "schemas")
    version_registry_dir = os.path.join(workspace, "tools", "xstack", "compatx")
    os.makedirs(schemas_dir, exist_ok=True)
    os.makedirs(version_registry_dir, exist_ok=True)

    source_version_registry = _read_json(_repo_abs(root, os.path.join("tools", "xstack", "compatx", "version_registry.json")))
    source_entries = _as_map(source_version_registry.get("schemas"))
    scoped_entries: dict[str, object] = {}
    for schema_name in sorted({_token(name) for name in list(schema_names or []) if _token(name)}):
        src_path = _repo_abs(root, os.path.join("schemas", "{}.schema.json".format(schema_name)))
        if os.path.isfile(src_path):
            _copy_file(src_path, os.path.join(schemas_dir, "{}.schema.json".format(schema_name)))
        if schema_name in source_entries:
            scoped_entries[schema_name] = source_entries[schema_name]

    version_registry_payload = dict(source_version_registry)
    version_registry_payload["schemas"] = dict(sorted(scoped_entries.items(), key=lambda item: item[0]))
    _write_canonical_json(os.path.join(version_registry_dir, "version_registry.json"), version_registry_payload)
    return workspace


def _finding_row(*, code: str, path: str, message: str, suite_id: str, severity: str = "error") -> dict:
    return {
        "code": _token(code),
        "path": _norm(path),
        "message": _token(message),
        "suite_id": _token(suite_id),
        "severity": _token(severity) or "error",
    }


def _build_suite_result(
    *,
    suite_id: str,
    category_id: str,
    profile: str,
    suite_order: int,
    adapter_id: str,
    description: str,
    checked_paths: Iterable[str],
    result: str,
    message: str,
    errors: Iterable[Mapping[str, object]] = (),
    warnings: Iterable[Mapping[str, object]] = (),
    metrics: Mapping[str, object] | None = None,
    fingerprints: Mapping[str, object] | None = None,
    legacy_adapters: Iterable[Mapping[str, object]] = (),
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "validation_id": "validation.{}.{}".format(_token(suite_id), _token(profile).lower()),
        "suite_id": _token(suite_id),
        "category_id": _token(category_id),
        "profile": _token(profile),
        "result": _token(result),
        "message": _token(message),
        "suite_order": int(suite_order or 0),
        "adapter_id": _token(adapter_id),
        "description": _token(description),
        "checked_paths": sorted(_norm(path) for path in list(checked_paths or []) if _token(path)),
        "errors": sorted(
            [dict(row or {}) for row in list(errors or []) if isinstance(row, Mapping)],
            key=lambda row: (
                _token(row.get("path")),
                _token(row.get("code")),
                _token(row.get("message")),
                _token(row.get("suite_id")),
            ),
        ),
        "warnings": sorted(
            [dict(row or {}) for row in list(warnings or []) if isinstance(row, Mapping)],
            key=lambda row: (
                _token(row.get("path")),
                _token(row.get("code")),
                _token(row.get("message")),
                _token(row.get("suite_id")),
            ),
        ),
        "metrics": dict(metrics or {}),
        "fingerprints": dict(fingerprints or {}),
        "legacy_adapters": sorted(
            [dict(row or {}) for row in list(legacy_adapters or []) if isinstance(row, Mapping)],
            key=lambda row: (_token(row.get("path")), _token(row.get("surface_id")), _token(row.get("mapped_suite_id"))),
        ),
        "suite_results": [],
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    payload["deterministic_fingerprint"] = _report_fingerprint(payload)
    return payload


def _suite_registry_rows(repo_root: str) -> list[dict]:
    payload = _read_json(_repo_abs(repo_root, VALIDATION_SUITE_REGISTRY_REL))
    record = _as_map(payload.get("record"))
    rows = [dict(row) for row in _as_list(record.get("suites")) if isinstance(row, Mapping)]
    return sorted(rows, key=lambda row: (int(row.get("suite_order", 0) or 0), _token(row.get("suite_id"))))


def _suite_row_by_id(repo_root: str) -> dict[str, dict]:
    rows = {}
    for row in _suite_registry_rows(repo_root):
        suite_id = _token(row.get("suite_id"))
        if suite_id:
            rows[suite_id] = dict(row)
    return rows


@lru_cache(maxsize=8)
def _validation_surface_rows_cached(repo_root: str) -> tuple[dict, ...]:
    root = _repo_root(repo_root)
    inventory = load_or_run_inventory_report(root, prefer_cached=False)
    indexed_surfaces = {
        _token(row.get("path")): dict(row)
        for row in _as_list(_as_map(inventory.get("validation_surface")).get("rows"))
        if isinstance(row, Mapping)
    }
    indexed_entries = {
        _token(row.get("path")): dict(row)
        for row in _as_list(inventory.get("entries"))
        if isinstance(row, Mapping)
    }
    rows: list[dict] = []
    for spec in LEGACY_VALIDATION_SURFACE_SPECS:
        row = dict(spec)
        rel_path = _token(row.get("path"))
        inventory_row = dict(indexed_surfaces.get(rel_path) or indexed_entries.get(rel_path) or {})
        row["discovered"] = bool(inventory_row) or os.path.isfile(_repo_abs(root, rel_path))
        row["product"] = _token(inventory_row.get("product")) or ("tool" if rel_path.startswith("tools/") else "engine")
        row["layer"] = _token(inventory_row.get("layer")) or "validation"
        row["consolidation_target"] = _token(indexed_surfaces.get(rel_path, {}).get("consolidation_target")) or _token(row.get("mapped_suite_id"))
        row["deterministic_fingerprint"] = canonical_sha256(dict(dict(row), deterministic_fingerprint=""))
        rows.append(row)
    return tuple(sorted(rows, key=lambda row: (_token(row.get("path")), _token(row.get("surface_id")))))


def validation_surface_rows(repo_root: str) -> list[dict]:
    return [dict(row) for row in _validation_surface_rows_cached(_repo_root(repo_root))]


def validation_surface_findings(repo_root: str) -> list[dict]:
    rows = validation_surface_rows(repo_root)
    findings: list[dict] = []
    seen_paths: dict[str, str] = {}
    suites = _suite_row_by_id(repo_root)
    for row in rows:
        rel_path = _token(row.get("path"))
        mapped_suite_id = _token(row.get("mapped_suite_id"))
        if not bool(row.get("discovered")):
            findings.append(
                {
                    "code": "missing_validation_surface",
                    "path": rel_path,
                    "message": "validation surface is declared but not present in the repository inventory",
                    "rule_id": "INV-NO-ADHOC-VALIDATION-ENTRYPOINTS",
                }
            )
        if not mapped_suite_id or mapped_suite_id not in suites:
            findings.append(
                {
                    "code": "unmapped_validation_surface",
                    "path": rel_path,
                    "message": "validation surface is not mapped to a unified validation suite",
                    "rule_id": "INV-NO-ADHOC-VALIDATION-ENTRYPOINTS",
                }
            )
        previous = seen_paths.get(rel_path)
        if previous and previous != mapped_suite_id:
            findings.append(
                {
                    "code": "duplicate_validation_surface_mapping",
                    "path": rel_path,
                    "message": "validation surface is mapped to more than one unified suite",
                    "rule_id": "INV-NO-ADHOC-VALIDATION-ENTRYPOINTS",
                }
            )
        seen_paths[rel_path] = mapped_suite_id
    return sorted(findings, key=lambda row: (_token(row.get("path")), _token(row.get("code")), _token(row.get("message"))))


def build_validation_inventory(repo_root: str) -> dict:
    root = _repo_root(repo_root)
    rows = validation_surface_rows(root)
    mapped_counts = Counter(_token(row.get("mapped_suite_id")) for row in rows if _token(row.get("mapped_suite_id")))
    payload = {
        "inventory_id": VALIDATION_INVENTORY_ID,
        "result": "complete",
        "surface_count": len(rows),
        "rows": rows,
        "summary": {
            "active_adapter_count": sum(1 for row in rows if _token(row.get("adapter_mode")) == "direct_python"),
            "coverage_adapter_count": sum(1 for row in rows if _token(row.get("adapter_mode")) == "coverage_adapter"),
            "deprecated_surface_count": sum(1 for row in rows if _token(row.get("status")) == "deprecated"),
            "suite_coverage": dict(sorted(mapped_counts.items(), key=lambda item: item[0])),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _report_fingerprint(payload)
    return payload


def _collect_manifest_paths(repo_root: str, filenames: Iterable[str], *, roots: Iterable[str] | None = None) -> list[str]:
    out: list[str] = []
    target_names = set(str(name) for name in filenames)
    for root_name in list(roots or ("build", "dist", "exports", "instances", "installs", "saves", "artifacts")):
        abs_root = _repo_abs(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, files in os.walk(abs_root):
            dirnames[:] = sorted(dirnames)
            for name in sorted(files):
                if name not in target_names:
                    continue
                out.append(_norm(os.path.relpath(os.path.join(dirpath, name), repo_root)))
    return sorted(set(out))


def _collect_pack_compat_paths(repo_root: str, *, roots: Iterable[str]) -> list[str]:
    return _collect_manifest_paths(repo_root, PACK_COMPAT_FILENAMES, roots=roots)


def _legacy_rows_for_suite(repo_root: str, suite_id: str) -> list[dict]:
    rows = []
    for row in validation_surface_rows(repo_root):
        if _token(row.get("mapped_suite_id")) != _token(suite_id):
            continue
        rows.append(
            {
                "surface_id": _token(row.get("surface_id")),
                "path": _token(row.get("path")),
                "mapped_suite_id": _token(row.get("mapped_suite_id")),
                "adapter_mode": _token(row.get("adapter_mode")),
                "status": _token(row.get("status")),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("path")), _token(row.get("surface_id"))))


def _adapt_schema_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    scoped_root = _scoped_schema_workspace(
        repo_root,
        schema_names=GOVERNED_SCHEMA_NAMES,
        workspace_id="schema_scope_{}".format(_token(profile).lower() or "fast"),
    )
    report = run_compatx_check(repo_root=scoped_root, profile=profile)
    findings = [dict(row or {}) for row in _as_list(report.get("findings")) if isinstance(row, Mapping)]
    errors = [
        _finding_row(
            code=_token(row.get("code")) or "refusal.validation.schema",
            path=_token(row.get("schema_name")) or "schemas",
            message=_token(row.get("message")) or "schema validation failed",
            suite_id=_token(suite_row.get("suite_id")),
            severity=_token(row.get("severity")) or "error",
        )
        for row in findings
        if _token(row.get("severity")) in {"fail", "refusal"}
    ]
    warnings = [
        _finding_row(
            code=_token(row.get("code")) or "warn.validation.schema",
            path=_token(row.get("schema_name")) or "schemas",
            message=_token(row.get("message")) or "schema validation warning",
            suite_id=_token(suite_row.get("suite_id")),
            severity=_token(row.get("severity")) or "warn",
        )
        for row in findings
        if _token(row.get("severity")) not in {"fail", "refusal"}
    ]
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=[
            "schemas/{}.schema.json".format(name)
            for name in GOVERNED_SCHEMA_NAMES
        ] + ["tools/xstack/compatx/version_registry.json"],
        result="complete" if not errors else "refused",
        message=_token(report.get("message")) or "schema validation completed",
        errors=errors,
        warnings=warnings,
        metrics={
            "finding_count": len(findings),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "scoped_schema_count": len(GOVERNED_SCHEMA_NAMES),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_registry_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    report = validate_all_registries(repo_root)
    errors: list[dict] = []
    checked_paths: list[str] = []
    for row in _as_list(report.get("reports")):
        item = _as_map(row)
        rel_path = _token(item.get("file_path"))
        if rel_path:
            checked_paths.append(rel_path)
        for error in _as_list(item.get("errors")):
            error_row = _as_map(error)
            errors.append(
                _finding_row(
                    code=_token(error_row.get("code")) or "refusal.validation.registry",
                    path=rel_path or _token(error_row.get("path")),
                    message=_token(error_row.get("message")) or "registry validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=checked_paths,
        result="complete" if not errors else "refused",
        message="registry validation {} (files={}, errors={})".format(
            "passed" if not errors else "found_errors",
            len(checked_paths),
            len(errors),
        ),
        errors=errors,
        metrics={"report_count": len(_as_list(report.get("reports"))), "error_count": len(errors)},
        fingerprints={"stability_report_fingerprint": _token(report.get("deterministic_fingerprint"))},
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_identity_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    strict_missing = bool(STRICT_MISSING_POLICY_ACTIVE and str(profile).strip().upper() in {"STRICT", "FULL"})
    report = write_identity_artifacts(repo_root, strict_missing=strict_missing)
    errors = []
    warnings = []
    checked_paths: list[str] = []
    for row in _as_list(report.get("reports")):
        item = _as_map(row)
        rel_path = _token(item.get("path"))
        if rel_path:
            checked_paths.append(rel_path)
        for error in _as_list(item.get("errors")):
            error_row = _as_map(error)
            errors.append(
                _finding_row(
                    code=_token(error_row.get("code")) or "refusal.validation.identity",
                    path=rel_path or _token(error_row.get("path")),
                    message=_token(error_row.get("message")) or "universal identity validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
        for warning in _as_list(item.get("warnings")):
            warning_row = _as_map(warning)
            warnings.append(
                _finding_row(
                    code=_token(warning_row.get("code")) or "warn.validation.identity",
                    path=rel_path or _token(warning_row.get("path")),
                    message=_token(warning_row.get("message")) or "universal identity warning",
                    suite_id=_token(suite_row.get("suite_id")),
                    severity="warn",
                )
            )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=sorted(set(checked_paths + [IDENTITY_BASELINE_DOC_REL, IDENTITY_REPORT_JSON_REL])),
        result="complete" if not errors else "refused",
        message="identity validation {} (artifacts={}, warnings={}, errors={})".format(
            "passed" if not errors else "found_errors",
            int(report.get("artifact_count", 0) or 0),
            int(report.get("warning_count", 0) or 0),
            int(report.get("error_count", 0) or 0),
        ),
        errors=errors,
        warnings=warnings,
        metrics={
            "artifact_count": int(report.get("artifact_count", 0) or 0),
            "warning_count": int(report.get("warning_count", 0) or 0),
            "error_count": int(report.get("error_count", 0) or 0),
            "strict_missing": bool(strict_missing),
        },
        fingerprints={"identity_report_fingerprint": _token(report.get("deterministic_fingerprint"))},
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_contract_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    registry_payload, load_error = load_semantic_contract_registry(repo_root)
    errors: list[dict] = []
    if load_error:
        errors.append(
            _finding_row(
                code="refusal.validation.contract_registry_load",
                path="data/registries/semantic_contract_registry.json",
                message=load_error,
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
        registry_payload = {}
    for token in validate_semantic_contract_registry(registry_payload):
        errors.append(
            _finding_row(
                code=token,
                path="data/registries/semantic_contract_registry.json",
                message="semantic contract registry validation failed",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    bundle_payload = build_default_universe_contract_bundle(registry_payload)
    for token in validate_universe_contract_bundle(repo_root=repo_root, payload=bundle_payload, registry_payload=registry_payload):
        errors.append(
            _finding_row(
                code=token,
                path="schemas/universe_contract_bundle.schema.json",
                message="universe contract bundle validation failed",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=["data/registries/semantic_contract_registry.json", "schemas/universe_contract_bundle.schema.json"],
        result="complete" if not errors else "refused",
        message="contract validation {} (errors={})".format("passed" if not errors else "found_errors", len(errors)),
        errors=errors,
        metrics={"error_count": len(errors)},
        fingerprints={
            "semantic_contract_registry_hash": registry_hash(registry_payload),
            "universe_contract_bundle_hash": canonical_sha256(bundle_payload),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_pack_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    checked_paths: list[str] = []

    pack_lock_rel = _norm(RELEASE_PACK_LOCK_REL)
    pack_lock_abs = _repo_abs(repo_root, pack_lock_rel)
    pack_lock_payload = _read_json(pack_lock_abs)
    if not pack_lock_payload:
        errors.append(
            _finding_row(
                code="refusal.validation.pack_lock_missing",
                path=pack_lock_rel,
                message="release pack lock is missing",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    else:
        checked_paths.append(pack_lock_rel)
        schema_result = validate_instance(repo_root=repo_root, schema_name="pack_lock", payload=pack_lock_payload, strict_top_level=True)
        if not bool(schema_result.get("valid", False)):
            for row in _as_list(schema_result.get("errors")):
                item = _as_map(row)
                errors.append(
                    _finding_row(
                        code=_token(item.get("code")) or "refusal.validation.pack_lock_schema",
                        path=pack_lock_rel,
                        message=_token(item.get("message")) or "release pack lock schema validation failed",
                        suite_id=_token(suite_row.get("suite_id")),
                    )
                )
        for token in validate_pack_lock_payload(repo_root=repo_root, payload=pack_lock_payload):
            errors.append(
                _finding_row(
                    code=_token(token) or "refusal.validation.pack_lock_runtime",
                    path=pack_lock_rel,
                    message="release pack lock payload validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )

    rebuilt_pack_lock: dict[str, object] = {}
    rebuilt_pack_lock_errors: list[str] = []
    try:
        rebuilt_pack_lock = build_pack_lock_payload(repo_root)
        rebuilt_pack_lock_errors = list(validate_pack_lock_payload(repo_root=repo_root, payload=rebuilt_pack_lock))
    except Exception as exc:
        rebuilt_pack_lock_errors = ["refusal.validation.pack_lock_rebuild_exception"]
        errors.append(
            _finding_row(
                code="refusal.validation.pack_lock_rebuild_exception",
                path="tools/mvp/runtime_bundle.py",
                message="rebuilt runtime pack lock generation failed: {}".format(str(exc).strip() or type(exc).__name__),
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    for token in rebuilt_pack_lock_errors:
        if token == "refusal.validation.pack_lock_rebuild_exception":
            continue
        errors.append(
            _finding_row(
                code=_token(token) or "refusal.validation.pack_lock_rebuild",
                path="tools/mvp/runtime_bundle.py",
                message="rebuilt runtime pack lock validation failed",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    if not rebuilt_pack_lock:
        warnings.append(
            _finding_row(
                code="warn.validation.pack_lock_rebuild_unavailable",
                path="tools/mvp/runtime_bundle.py",
                message="rebuilt runtime pack lock was unavailable after adapter execution",
                suite_id=_token(suite_row.get("suite_id")),
                severity="warn",
            )
        )
    checked_paths.append("tools/mvp/runtime_bundle.py")

    if pack_lock_payload and rebuilt_pack_lock:
        if _token(pack_lock_payload.get("pack_lock_hash")) != _token(rebuilt_pack_lock.get("pack_lock_hash")):
            errors.append(
                _finding_row(
                    code="refusal.validation.pack_lock_hash_mismatch",
                    path=pack_lock_rel,
                    message="release pack lock hash does not match the rebuilt runtime pack lock",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
        if _token(pack_lock_payload.get("deterministic_fingerprint")) != _token(rebuilt_pack_lock.get("deterministic_fingerprint")):
            errors.append(
                _finding_row(
                    code="refusal.validation.pack_lock_fingerprint_mismatch",
                    path=pack_lock_rel,
                    message="release pack lock deterministic fingerprint does not match the rebuilt runtime pack lock",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )

    pack_compat_paths = _collect_pack_compat_paths(repo_root, roots=("packs",))
    for rel_path in pack_compat_paths:
        checked_paths.append(rel_path)
        report = validate_pack_compat(_repo_abs(repo_root, rel_path))
        if _token(report.get("result")) != "complete":
            for row in _as_list(report.get("errors")):
                item = _as_map(row)
                errors.append(
                    _finding_row(
                        code=_token(item.get("code")) or "refusal.validation.pack_compat",
                        path=rel_path,
                        message=_token(item.get("message")) or "pack compat manifest validation failed",
                        suite_id=_token(suite_row.get("suite_id")),
                    )
                )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=checked_paths,
        result="complete" if not errors else "refused",
        message="pack verification {} (errors={}, warnings={})".format(
            "passed" if not errors else "found_errors",
            len(errors),
            len(warnings),
        ),
        errors=errors,
        warnings=warnings,
        metrics={
            "error_count": len(errors),
            "warning_count": len(warnings),
            "pack_compat_manifest_count": len(pack_compat_paths),
            "ordered_pack_count": len(_as_list(rebuilt_pack_lock.get("ordered_packs"))),
        },
        fingerprints={
            "release_pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
            "rebuilt_pack_lock_hash": _token(rebuilt_pack_lock.get("pack_lock_hash")),
            "release_pack_lock_fingerprint": _token(pack_lock_payload.get("deterministic_fingerprint")),
            "rebuilt_pack_lock_fingerprint": _token(rebuilt_pack_lock.get("deterministic_fingerprint")),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_negotiation_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    endpoint_a = build_product_descriptor(repo_root, product_id="client")
    endpoint_b = build_product_descriptor(repo_root, product_id="server")
    negotiated = negotiate_product_endpoints(repo_root, endpoint_a, endpoint_b, allow_read_only=False)
    errors: list[dict] = []
    if _token(negotiated.get("result")) == "refused":
        refusal = _as_map(negotiated.get("refusal"))
        errors.append(
            _finding_row(
                code=_token(refusal.get("reason_code")) or "refusal.validation.negotiation",
                path="data/registries/product_registry.json",
                message=_token(refusal.get("message")) or "negotiation refused",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    verification = verify_recorded_negotiation(
        repo_root,
        _as_map(negotiated.get("negotiation_record")),
        endpoint_a,
        endpoint_b,
        allow_read_only=False,
    )
    if _token(verification.get("result")) != "complete":
        errors.append(
            _finding_row(
                code=_token(verification.get("reason_code")) or "refusal.validation.negotiation_record",
                path="data/registries/product_registry.json",
                message=_token(verification.get("message")) or "negotiation record verification failed",
                suite_id=_token(suite_row.get("suite_id")),
            )
        )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=["data/registries/product_registry.json", "data/registries/compat_mode_registry.json"],
        result="complete" if not errors else "refused",
        message="negotiation validation {} (mode={})".format(
            "passed" if not errors else "found_errors",
            _token(negotiated.get("compatibility_mode_id")) or "unknown",
        ),
        errors=errors,
        metrics={
            "disabled_capability_count": len(_as_list(_as_map(negotiated.get("negotiation_record")).get("disabled_capabilities"))),
            "degrade_plan_count": len(_as_list(_as_map(negotiated.get("negotiation_record")).get("degrade_plan"))),
        },
        fingerprints={
            "negotiation_record_hash": _token(negotiated.get("negotiation_record_hash")),
            "endpoint_a_hash": _token(negotiated.get("endpoint_a_hash")),
            "endpoint_b_hash": _token(negotiated.get("endpoint_b_hash")),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_library_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    checked_paths: list[str] = []

    install_registry_rel = "data/registries/install_registry.json"
    install_registry_path = default_install_registry_path(repo_root)
    registry_report = verify_install_registry(repo_root=repo_root, registry_path=install_registry_path)
    checked_paths.append(install_registry_rel)
    if _token(registry_report.get("result")) != "complete":
        for row in _as_list(registry_report.get("installs")):
            item = _as_map(row)
            for error in _as_list(item.get("errors")):
                error_row = _as_map(error)
                errors.append(
                    _finding_row(
                        code=_token(error_row.get("code")) or "refusal.validation.install",
                        path=install_registry_rel,
                        message=_token(error_row.get("message")) or "install registry validation failed",
                        suite_id=_token(suite_row.get("suite_id")),
                    )
                )

    install_paths = _collect_manifest_paths(repo_root, ("install.manifest.json",), roots=RELEASE_LIBRARY_ROOTS)
    instance_paths = _collect_manifest_paths(repo_root, ("instance.manifest.json",), roots=RELEASE_LIBRARY_ROOTS)
    save_paths = _collect_manifest_paths(repo_root, ("save.manifest.json",), roots=RELEASE_LIBRARY_ROOTS)
    artifact_paths = _collect_manifest_paths(repo_root, ("artifact.manifest.json",), roots=RELEASE_LIBRARY_ROOTS)

    for rel_path in install_paths:
        checked_paths.append(rel_path)
        validation = validate_install_manifest(repo_root=repo_root, install_manifest_path=_repo_abs(repo_root, rel_path))
        if _token(validation.get("result")) != "complete":
            errors.append(
                _finding_row(
                    code=_token(validation.get("refusal_code")) or "refusal.validation.install_manifest",
                    path=rel_path,
                    message="install manifest validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    for rel_path in instance_paths:
        checked_paths.append(rel_path)
        validation = validate_instance_manifest(repo_root=repo_root, instance_manifest_path=_repo_abs(repo_root, rel_path))
        if _token(validation.get("result")) != "complete":
            errors.append(
                _finding_row(
                    code=_token(validation.get("refusal_code")) or "refusal.validation.instance_manifest",
                    path=rel_path,
                    message="instance manifest validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    for rel_path in save_paths:
        checked_paths.append(rel_path)
        validation = validate_save_manifest(repo_root=repo_root, save_manifest_path=_repo_abs(repo_root, rel_path))
        if _token(validation.get("result")) != "complete":
            errors.append(
                _finding_row(
                    code=_token(validation.get("refusal_code")) or "refusal.validation.save_manifest",
                    path=rel_path,
                    message="save manifest validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    for rel_path in artifact_paths:
        checked_paths.append(rel_path)
        validation = validate_artifact_manifest(repo_root=repo_root, artifact_manifest_path=_repo_abs(repo_root, rel_path))
        if _token(validation.get("result")) != "complete":
            errors.append(
                _finding_row(
                    code=_token(validation.get("refusal_code")) or "refusal.validation.artifact_manifest",
                    path=rel_path,
                    message="artifact manifest validation failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    if not install_paths and not instance_paths and not save_paths and not artifact_paths:
        warnings.append(
            _finding_row(
                code="warn.validation.library_no_manifests",
                path="data/registries/install_registry.json",
                message="no install/instance/save/artifact manifests were present beyond the install registry baseline",
                suite_id=_token(suite_row.get("suite_id")),
                severity="warn",
            )
        )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=checked_paths,
        result="complete" if not errors else "refused",
        message="library validation {} (errors={}, manifests={})".format(
            "passed" if not errors else "found_errors",
            len(errors),
            len(install_paths) + len(instance_paths) + len(save_paths) + len(artifact_paths),
        ),
        errors=errors,
        warnings=warnings,
        metrics={
            "install_manifest_count": len(install_paths),
            "instance_manifest_count": len(instance_paths),
            "save_manifest_count": len(save_paths),
            "artifact_manifest_count": len(artifact_paths),
            "error_count": len(errors),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_time_anchor_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    verify_report = verify_longrun_ticks(repo_root)
    compaction_report = verify_compaction_anchor_alignment(repo_root)
    errors: list[dict] = []
    if _token(verify_report.get("result")) != "complete":
        for row in _as_list(verify_report.get("violations")):
            item = _as_map(row)
            errors.append(
                _finding_row(
                    code="refusal.validation.time_anchor",
                    path=_token(item.get("path")) or "src/time",
                    message=_token(item.get("message")) or "time anchor verification failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    if _token(compaction_report.get("result")) != "complete":
        for row in _as_list(compaction_report.get("violations")):
            item = _as_map(row)
            errors.append(
                _finding_row(
                    code="refusal.validation.time_anchor_compaction",
                    path=_token(item.get("path")) or "src/meta/provenance",
                    message=_token(item.get("message")) or "time anchor compaction verification failed",
                    suite_id=_token(suite_row.get("suite_id")),
                )
            )
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=["src/time", "src/meta/provenance/compaction_engine.py"],
        result="complete" if not errors else "refused",
        message="time anchor validation {} (errors={})".format("passed" if not errors else "found_errors", len(errors)),
        errors=errors,
        metrics={"error_count": len(errors)},
        fingerprints={
            "verify_report_fingerprint": _token(verify_report.get("deterministic_fingerprint")),
            "compaction_report_fingerprint": _token(compaction_report.get("deterministic_fingerprint")),
        },
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_arch_audit_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    report = run_arch_audit(repo_root)
    errors = [
        _finding_row(
            code="refusal.validation.arch_audit",
            path=_token(row.get("path")),
            message=_token(row.get("message")) or "architecture audit finding",
            suite_id=_token(suite_row.get("suite_id")),
        )
        for row in _as_list(report.get("blocking_findings"))
        if isinstance(row, Mapping)
    ]
    warnings = [
        _finding_row(
            code="warn.validation.arch_audit_known_exception",
            path=_token(row.get("path")),
            message=_token(row.get("message")) or "architecture audit known exception",
            suite_id=_token(suite_row.get("suite_id")),
            severity="warn",
        )
        for row in _as_list(report.get("known_exceptions"))
        if isinstance(row, Mapping)
    ]
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=["docs/audit/ARCH_AUDIT_REPORT.md", "data/audit/arch_audit_report.json"],
        result="complete" if not errors else "refused",
        message="arch audit {} (blocking={}, known={})".format(
            "passed" if not errors else "found_errors",
            int(report.get("blocking_finding_count", 0) or 0),
            int(report.get("known_exception_count", 0) or 0),
        ),
        errors=errors,
        warnings=warnings,
        metrics={
            "blocking_finding_count": int(report.get("blocking_finding_count", 0) or 0),
            "known_exception_count": int(report.get("known_exception_count", 0) or 0),
        },
        fingerprints={"arch_audit_fingerprint": _token(report.get("deterministic_fingerprint"))},
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_determinism_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    report = scan_determinism(repo_root)
    errors = [
        _finding_row(
            code="refusal.validation.determinism",
            path=_token(row.get("path")),
            message=_token(row.get("message")) or "determinism scan finding",
            suite_id=_token(suite_row.get("suite_id")),
        )
        for row in _as_list(report.get("blocking_findings"))
        if isinstance(row, Mapping)
    ]
    warnings = [
        _finding_row(
            code="warn.validation.determinism_known_exception",
            path=_token(row.get("path")),
            message=_token(row.get("message")) or "determinism scan known exception",
            suite_id=_token(suite_row.get("suite_id")),
            severity="warn",
        )
        for row in _as_list(report.get("known_exceptions"))
        if isinstance(row, Mapping)
    ]
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=_as_list(report.get("scanned_paths")),
        result="complete" if not errors else "refused",
        message="determinism scan {} (blocking={}, known={})".format(
            "passed" if not errors else "found_errors",
            int(report.get("blocking_finding_count", 0) or 0),
            int(report.get("known_exception_count", 0) or 0),
        ),
        errors=errors,
        warnings=warnings,
        metrics={
            "blocking_finding_count": int(report.get("blocking_finding_count", 0) or 0),
            "known_exception_count": int(report.get("known_exception_count", 0) or 0),
        },
        fingerprints={"determinism_scan_fingerprint": _token(report.get("deterministic_fingerprint"))},
        legacy_adapters=_legacy_rows_for_suite(repo_root, _token(suite_row.get("suite_id"))),
    )


def _adapt_platform_matrix_suite(repo_root: str, suite_row: Mapping[str, object], profile: str) -> dict:
    report = maybe_load_cached_mvp_cross_platform_report(repo_root)
    if not report:
        return _build_suite_result(
            suite_id=_token(suite_row.get("suite_id")),
            category_id=_token(suite_row.get("category_id")),
            profile=profile,
            suite_order=int(suite_row.get("suite_order", 0) or 0),
            adapter_id=_token(suite_row.get("adapter_id")),
            description=_token(suite_row.get("description")),
            checked_paths=["build/mvp/mvp_cross_platform_matrix.json"],
            result="skipped",
            message="optional platform matrix report is not present in the local workspace",
            warnings=[
                _finding_row(
                    code="warn.validation.platform_matrix_unavailable",
                    path="build/mvp/mvp_cross_platform_matrix.json",
                    message="platform matrix suite is optional and was skipped because no cached report exists",
                    suite_id=_token(suite_row.get("suite_id")),
                    severity="warn",
                )
            ],
        )
    mismatches = _as_list(report.get("mismatches"))
    errors = [
        _finding_row(
            code="refusal.validation.platform_matrix",
            path="build/mvp/mvp_cross_platform_matrix.json",
            message="cross-platform matrix mismatch detected",
            suite_id=_token(suite_row.get("suite_id")),
        )
        for _row in mismatches
    ]
    return _build_suite_result(
        suite_id=_token(suite_row.get("suite_id")),
        category_id=_token(suite_row.get("category_id")),
        profile=profile,
        suite_order=int(suite_row.get("suite_order", 0) or 0),
        adapter_id=_token(suite_row.get("adapter_id")),
        description=_token(suite_row.get("description")),
        checked_paths=["build/mvp/mvp_cross_platform_matrix.json"],
        result="complete" if not errors else "refused",
        message="platform matrix {} (platforms={})".format(
            "passed" if not errors else "found_errors",
            len(_as_list(report.get("platform_order"))),
        ),
        errors=errors,
        metrics={"platform_count": len(_as_list(report.get("platform_order")))},
        fingerprints={"platform_matrix_fingerprint": _token(report.get("deterministic_fingerprint"))},
    )


SUITE_ADAPTERS: dict[str, Callable[[str, Mapping[str, object], str], dict]] = {
    "compatx_schema_suite": _adapt_schema_suite,
    "stability_registry_suite": _adapt_registry_suite,
    "identity_suite": _adapt_identity_suite,
    "semantic_contract_suite": _adapt_contract_suite,
    "pack_verification_suite": _adapt_pack_suite,
    "negotiation_suite": _adapt_negotiation_suite,
    "library_manifest_suite": _adapt_library_suite,
    "time_anchor_suite": _adapt_time_anchor_suite,
    "arch_audit_suite": _adapt_arch_audit_suite,
    "determinism_scan_suite": _adapt_determinism_suite,
    "platform_matrix_suite": _adapt_platform_matrix_suite,
}


def build_validation_report(repo_root: str, *, profile: str = "FAST") -> dict:
    root = _repo_root(repo_root)
    profile_token = _token(profile).upper() or "FAST"
    suite_rows = []
    for row in _suite_registry_rows(root):
        profiles = _sorted_strings(_as_list(row.get("profiles")) or PROFILE_ORDER)
        if profile_token not in profiles:
            continue
        suite_rows.append(dict(row))

    suite_results: list[dict] = []
    aggregate_errors: list[dict] = []
    aggregate_warnings: list[dict] = []
    for row in suite_rows:
        adapter_id = _token(row.get("adapter_id"))
        adapter = SUITE_ADAPTERS.get(adapter_id)
        if adapter is None:
            suite_result = _build_suite_result(
                suite_id=_token(row.get("suite_id")),
                category_id=_token(row.get("category_id")),
                profile=profile_token,
                suite_order=int(row.get("suite_order", 0) or 0),
                adapter_id=adapter_id,
                description=_token(row.get("description")),
                checked_paths=[],
                result="refused",
                message="validation suite adapter is missing",
                errors=[
                    _finding_row(
                        code="refusal.validation.adapter_missing",
                        path=VALIDATION_SUITE_REGISTRY_REL,
                        message="adapter '{}' is not implemented".format(adapter_id),
                        suite_id=_token(row.get("suite_id")),
                    )
                ],
            )
        else:
            suite_result = adapter(root, row, profile_token)
        suite_results.append(suite_result)
        aggregate_errors.extend([dict(item) for item in _as_list(suite_result.get("errors")) if isinstance(item, Mapping)])
        aggregate_warnings.extend([dict(item) for item in _as_list(suite_result.get("warnings")) if isinstance(item, Mapping)])

    inventory = build_validation_inventory(root)
    suite_registry_payload = _read_json(_repo_abs(root, VALIDATION_SUITE_REGISTRY_REL))
    result_counts = Counter(_token(row.get("result")) for row in suite_results)
    report = _build_suite_result(
        suite_id="validate.all",
        category_id="validate.aggregate",
        profile=profile_token,
        suite_order=0,
        adapter_id="validation_engine",
        description="Unified validation aggregate for validate --all.",
        checked_paths=[VALIDATION_SUITE_REGISTRY_REL] + [_token(row.get("path")) for row in validation_surface_rows(root)],
        result="complete" if not aggregate_errors else "refused",
        message="validation pipeline {} (suites={}, errors={}, warnings={})".format(
            "passed" if not aggregate_errors else "found_errors",
            len(suite_results),
            len(aggregate_errors),
            len(aggregate_warnings),
        ),
        errors=aggregate_errors,
        warnings=aggregate_warnings,
        metrics={
            "suite_count": len(suite_results),
            "complete_suite_count": int(result_counts.get("complete", 0)),
            "refused_suite_count": int(result_counts.get("refused", 0)),
            "skipped_suite_count": int(result_counts.get("skipped", 0)),
            "legacy_surface_count": len(validation_surface_rows(root)),
        },
        fingerprints={
            "suite_registry_hash": canonical_sha256(suite_registry_payload),
            "validation_inventory_fingerprint": _token(inventory.get("deterministic_fingerprint")),
        },
        legacy_adapters=validation_surface_rows(root),
        extensions={
            "inventory_doc_path": _norm(VALIDATION_INVENTORY_DOC_PATH),
            "pipeline_doc_path": _norm(VALIDATION_PIPELINE_DOC_PATH),
            "report_doc_path": _norm(VALIDATION_REPORT_DOC_TEMPLATE.format(profile=profile_token)),
            "report_json_path": _norm(VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile_token)),
            "final_doc_path": _norm(VALIDATION_FINAL_DOC_TEMPLATE),
        },
    )
    report["validation_id"] = "validation.pipeline.{}.{}".format(VALIDATION_REPORT_ID, profile_token.lower())
    report["suite_results"] = suite_results
    report["deterministic_fingerprint"] = _report_fingerprint(report)
    return report


def render_validation_inventory(report: Mapping[str, object]) -> str:
    payload = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: legacy reference surface retained without current binding authority",
        "",
        "# Validation Inventory",
        "",
        "This inventory enumerates the significant validation surfaces currently present in the repository and maps each one to the unified validation pipeline.",
        "",
        "| Path | Purpose | Inputs / Outputs | Overlaps | Unified Suite | Adapter | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in _as_list(payload.get("rows")):
        item = _as_map(row)
        lines.append(
            "| `{}` | {} | {} / {} | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("path")),
                _token(item.get("purpose")) or "-",
                ", ".join(_as_list(item.get("inputs"))) or "-",
                ", ".join(_as_list(item.get("outputs"))) or "-",
                "`, `".join(_as_list(item.get("overlaps"))) or "-",
                _token(item.get("mapped_suite_id")) or "-",
                _token(item.get("adapter_mode")) or "-",
                _token(item.get("status")) or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "- Surface count: `{}`".format(int(payload.get("surface_count", 0) or 0)),
            "- Active adapters: `{}`".format(int(_as_map(payload.get("summary")).get("active_adapter_count", 0) or 0)),
            "- Coverage adapters: `{}`".format(int(_as_map(payload.get("summary")).get("coverage_adapter_count", 0) or 0)),
            "- Deprecated surfaces: `{}`".format(int(_as_map(payload.get("summary")).get("deprecated_surface_count", 0) or 0)),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_validation_report(report: Mapping[str, object]) -> str:
    payload = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: regenerated validation run artifact",
        "",
        "# Validation Report {}".format(_token(payload.get("profile")) or "UNKNOWN"),
        "",
        "- Result: `{}`".format(_token(payload.get("result")) or "unknown"),
        "- Fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint")) or "missing"),
        "- Suite count: `{}`".format(int(_as_map(payload.get("metrics")).get("suite_count", 0) or 0)),
        "",
        "| Suite | Result | Adapter | Errors | Warnings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in _as_list(payload.get("suite_results")):
        item = _as_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("suite_id")),
                _token(item.get("result")),
                _token(item.get("adapter_id")),
                len(_as_list(item.get("errors"))),
                len(_as_list(item.get("warnings"))),
            )
        )
    if _as_list(payload.get("errors")):
        lines.extend(["", "## Blocking Findings", ""])
        for row in _as_list(payload.get("errors")):
            item = _as_map(row)
            lines.append("- `{}`: {} [{}]".format(_token(item.get("suite_id")), _token(item.get("message")), _token(item.get("path"))))
    lines.append("")
    return "\n".join(lines)


def render_validation_unify_final(report: Mapping[str, object], inventory: Mapping[str, object]) -> str:
    payload = dict(report or {})
    surface_inventory = dict(inventory or {})
    suite_rows = [_as_map(row) for row in _as_list(payload.get("suite_results"))]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: release-pinned validation governance report",
        "",
        "# Validation Unify Final",
        "",
        "## Suite List",
        "",
    ]
    for row in suite_rows:
        lines.append(
            "- `{}` -> `{}` via `{}` (errors={}, warnings={})".format(
                _token(row.get("suite_id")),
                _token(row.get("result")),
                _token(row.get("adapter_id")),
                len(_as_list(row.get("errors"))),
                len(_as_list(row.get("warnings"))),
            )
        )
    lines.extend(
        [
            "",
            "## Legacy Validators Mapped",
            "",
            "- Total prior significant validation surfaces: `{}`".format(int(surface_inventory.get("surface_count", 0) or 0)),
            "- Active direct adapters: `{}`".format(int(_as_map(surface_inventory.get("summary")).get("active_adapter_count", 0) or 0)),
            "- Coverage/deprecation adapters: `{}`".format(int(_as_map(surface_inventory.get("summary")).get("coverage_adapter_count", 0) or 0)),
            "",
            "## Readiness",
            "",
            "- `validate --all` is available through AppShell for governed products.",
            "- Legacy validator surfaces are mapped to unified suites or explicitly deprecated with replacement targets.",
            "- Readiness for UI mode selection and path virtualization passes: `yes`, subject to the current scoped validation report staying clean.",
            "",
        ]
    )
    return "\n".join(lines)


def load_or_run_validation_report(repo_root: str, *, profile: str = "FAST", prefer_cached: bool = True) -> dict:
    root = _repo_root(repo_root)
    profile_token = _token(profile).upper() or "FAST"
    json_rel = VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile_token)
    if prefer_cached:
        payload = _read_json(_repo_abs(root, json_rel))
        if _token(payload.get("suite_id")) == "validate.all" and _token(payload.get("profile")) == profile_token:
            return payload
    return build_validation_report(root, profile=profile_token)


def write_validation_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    payload = dict(report or {})
    profile = _token(payload.get("profile")).upper() or "FAST"
    inventory = build_validation_inventory(root)
    written = {
        "inventory_path": _write_text(_repo_abs(root, VALIDATION_INVENTORY_DOC_PATH), render_validation_inventory(inventory)),
        "report_doc_path": _write_text(
            _repo_abs(root, VALIDATION_REPORT_DOC_TEMPLATE.format(profile=profile)),
            render_validation_report(payload),
        ),
        "report_json_path": _write_canonical_json(
            _repo_abs(root, VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile)),
            payload,
        ),
        "final_doc_path": _write_text(
            _repo_abs(root, VALIDATION_FINAL_DOC_TEMPLATE),
            render_validation_unify_final(payload, inventory),
        ),
    }
    return written


__all__ = [
    "VALIDATION_FINAL_DOC_TEMPLATE",
    "VALIDATION_INVENTORY_DOC_PATH",
    "VALIDATION_PIPELINE_DOC_PATH",
    "VALIDATION_REPORT_DOC_TEMPLATE",
    "VALIDATION_REPORT_JSON_TEMPLATE",
    "VALIDATION_SUITE_REGISTRY_REL",
    "build_validation_inventory",
    "build_validation_report",
    "load_or_run_validation_report",
    "render_validation_inventory",
    "render_validation_report",
    "render_validation_unify_final",
    "validation_surface_findings",
    "validation_surface_rows",
    "write_validation_outputs",
]
