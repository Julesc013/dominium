#!/usr/bin/env python3
"""Minimal deterministic RepoX policy scan for XStack profile runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Dict, Iterable, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


FORBIDDEN_IDENTIFIERS = (
    "survival_mode",
    "creative_mode",
    "hardcore_mode",
    "spectator_mode",
    "debug_mode",
    "godmode",
    "sandbox",
)

RESERVED_WORDS = (
    "deterministic",
    "law",
    "authority",
    "lens",
    "canonical",
    "identity",
    "collapse",
    "expand",
    "macro",
    "micro",
    "process",
    "refusal",
)

SCAN_ROOTS = (
    "client/observability",
    "client/presentation",
    "worldgen",
    "tools/xstack/compatx",
    "tools/xstack/pack_loader",
    "tools/xstack/pack_contrib",
    "tools/xstack/registry_compile",
    "tools/xstack/controlx",
    "tools/xstack/repox",
    "tools/xstack/auditx",
    "tools/xstack/testx",
    "tools/xstack/performx",
    "tools/xstack/securex",
    "tools/xstack/sessionx",
    "tools/domain",
    "tools/xstack/bundle_list.py",
    "tools/xstack/bundle_validate.py",
    "tools/xstack/session_create.py",
    "tools/xstack/session_boot.py",
    "tools/worldgen_offline",
    "schemas",
    "schema/worldgen",
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
    "data/registries/worldgen_constraints_registry.json",
    "data/registries/worldgen_module_registry.json",
    "packs",
    "bundles",
    "docs/contracts",
    "docs/testing",
    "docs/worldgen",
    "docs/architecture/registry_compile.md",
    "docs/architecture/lockfile.md",
    "docs/architecture/pack_system.md",
    "docs/architecture/session_lifecycle.md",
)

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".cmd",
    ".json",
    ".md",
    ".py",
    ".schema.json",
    ".schema",
    ".txt",
    ".yaml",
    ".yml",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')
RENDERER_TRUTH_INCLUDE_FORBIDDEN = {
    "domino/truth_model_v1.h",
    "domino/truth_model.h",
}

SESSION_PIPELINE_REQUIRED_FILES = (
    "schemas/session_spec.schema.json",
    "schemas/session_stage.schema.json",
    "schemas/session_pipeline.schema.json",
    "data/registries/session_stage_registry.json",
    "data/registries/session_pipeline_registry.json",
)

DOMAIN_FOUNDATION_REQUIRED_FILES = (
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
)

CONTRACT_STABILITY_BASELINE_IDS = (
    "dom.contract.mass_conservation",
    "dom.contract.energy_conservation",
    "dom.contract.charge_conservation",
    "dom.contract.ledger_balance",
    "dom.contract.epistemic_non_omniscience",
    "dom.contract.deterministic_transition",
    "dom.contract.port_contract_preservation",
)

DOMAIN_TOKEN_ALLOWED_PATH_PREFIXES = (
    "data/registries/domain_registry.json",
    "data/registries/solver_registry.json",
    "docs/scale/",
    "schema/scale/",
    "schemas/domain_",
    "schemas/solver_registry.schema.json",
    "tools/domain/",
)

WORLDGEN_CONSTRAINT_REQUIRED_FILES = (
    "schemas/worldgen_constraints.schema.json",
    "schemas/worldgen_search_plan.schema.json",
    "data/registries/worldgen_constraints_registry.json",
)

WORLDGEN_CONSTRAINT_LITERAL_ALLOWED_PATH_PREFIXES = (
    "packs/",
    "bundles/",
    "data/registries/worldgen_constraints_registry.json",
    "docs/worldgen/",
    "schema/worldgen/",
    "schemas/",
    "schemas/worldgen_constraints.schema.json",
    "schemas/worldgen_search_plan.schema.json",
    "schemas/worldgen_constraints_registry.schema.json",
    "tools/xstack/testx/tests/",
    "tools/worldgen_offline/",
    "worldgen/core/constraint_solver.py",
    "worldgen/core/constraint_commands.py",
)

WORLDGEN_SEED_POLICY_FORBIDDEN_TOKENS = (
    "import random",
    "from random import",
    "random.",
    "import secrets",
    "from secrets import",
    "secrets.",
    "uuid.uuid4(",
    "time.time(",
    "datetime.now(",
)

AUDITX_FINDINGS_PATH = "docs/audit/auditx/FINDINGS.json"
AUDITX_RUNTIME_PROBE_OUTPUT_ROOT = ".xstack_cache/auditx/repox_probe"
AUDITX_HIGH_RISK_CONFIDENCE = 0.85
AUDITX_HIGH_RISK_THRESHOLD = 15

RUNTIME_PATH_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "launcher/",
    "setup/",
    "libs/",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _severity_rank(value: str) -> int:
    token = str(value or "").strip().lower()
    if token == "warn":
        return 0
    if token == "fail":
        return 1
    if token == "refusal":
        return 2
    return 9


def _finding_id(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _finding(
    severity: str,
    file_path: str,
    line_number: int,
    snippet: str,
    message: str,
    rule_id: str,
) -> Dict[str, object]:
    token = "{}|{}|{}|{}|{}".format(rule_id, file_path, line_number, severity, message)
    return {
        "finding_id": _finding_id(token),
        "rule_id": str(rule_id),
        "severity": str(severity),
        "file_path": _norm(file_path),
        "line_number": int(line_number),
        "snippet": str(snippet),
        "message": str(message),
    }


def _scan_files(repo_root: str) -> List[str]:
    out: List[str] = []
    for root in SCAN_ROOTS:
        abs_path = os.path.join(repo_root, root.replace("/", os.sep))
        if os.path.isdir(abs_path):
            for walk_root, _dirs, files in os.walk(abs_path):
                for name in files:
                    rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    lower = rel.lower()
                    _, ext = os.path.splitext(name.lower())
                    if lower.endswith(".schema.json"):
                        out.append(rel)
                        continue
                    if ext in TEXT_EXTENSIONS:
                        out.append(rel)
        elif os.path.isfile(abs_path):
            out.append(_norm(os.path.relpath(abs_path, repo_root)))
    return sorted(set(out))


def _iter_lines(repo_root: str, rel_path: str) -> Iterable[Tuple[int, str]]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle, start=1):
                yield idx, line.rstrip("\n")
    except (OSError, UnicodeDecodeError):
        return


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")) for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


def _load_json_object(repo_root: str, rel_path: str) -> Tuple[dict, str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _invariant_severity(profile: str) -> str:
    return "refusal" if str(profile).strip().upper() in ("STRICT", "FULL") else "fail"


def _append_session_pipeline_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in SESSION_PIPELINE_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    for rel_path in sorted(missing):
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required session pipeline contract file is missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
    if missing:
        return

    stage_registry, stage_err = _load_json_object(repo_root, "data/registries/session_stage_registry.json")
    pipeline_registry, pipeline_err = _load_json_object(repo_root, "data/registries/session_pipeline_registry.json")
    if stage_err or pipeline_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="session stage/pipeline registry JSON is invalid",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    stage_rows = (stage_registry.get("record") or {}).get("stages")
    pipeline_rows = (pipeline_registry.get("record") or {}).get("pipelines")
    if not isinstance(stage_rows, list) or not isinstance(pipeline_rows, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="session stage/pipeline registry record lists are missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    stage_map = {}
    for row in stage_rows:
        if not isinstance(row, dict):
            continue
        stage_id = str(row.get("stage_id", "")).strip()
        if stage_id:
            stage_map[stage_id] = row
    default_pipeline = {}
    for row in pipeline_rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("pipeline_id", "")).strip() == "pipeline.client.default":
            default_pipeline = row
            break
    if not default_pipeline:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="default pipeline.client.default is missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    resolve_stage = dict(stage_map.get("stage.resolve_session") or {})
    allowed_from_resolve = sorted(
        set(str(item).strip() for item in (resolve_stage.get("allowed_next_stage_ids") or []) if str(item).strip())
    )
    if "stage.session_running" in allowed_from_resolve:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.resolve_session cannot directly transition to stage.session_running",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )

    ready_stage = dict(stage_map.get("stage.session_ready") or {})
    allowed_from_ready = sorted(
        set(str(item).strip() for item in (ready_stage.get("allowed_next_stage_ids") or []) if str(item).strip())
    )
    if "stage.session_running" not in allowed_from_ready:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.session_ready must allow transition to stage.session_running",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )

    order = [str(item).strip() for item in (default_pipeline.get("stages") or []) if str(item).strip()]
    required_order = ["stage.resolve_session", "stage.verify_world", "stage.session_ready", "stage.session_running"]
    if any(stage_id not in order for stage_id in required_order):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="pipeline.client.default is missing required canonical stages",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )
    else:
        indices = [int(order.index(stage_id)) for stage_id in required_order]
        if indices != sorted(indices):
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/session_pipeline_registry.json",
                    line_number=1,
                    snippet="",
                    message="pipeline.client.default stage order allows skip relative to running transition",
                    rule_id="INV-NO-STAGE-SKIP",
                )
            )

    ready_extensions = dict(ready_stage.get("extensions") or {})
    ready_tick = ready_extensions.get("ready_time_must_equal_tick")
    if int(ready_tick if ready_tick is not None else -1) != 0:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.session_ready must enforce simulation_time.tick == 0",
                rule_id="INV-SESSION-READY-TIME-ZERO",
            )
        )


def _append_domain_foundation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in DOMAIN_FOUNDATION_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    for rel_path in sorted(missing):
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required domain foundation registry file is missing",
                rule_id="INV-DOMAIN-REGISTRY-VALID",
            )
        )
    if missing:
        return

    try:
        from tools.domain.tool_domain_validate import validate_domain_foundation
    except Exception:
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/domain/tool_domain_validate.py",
                line_number=1,
                snippet="",
                message="unable to import domain foundation validator",
                rule_id="INV-DOMAIN-REGISTRY-VALID",
            )
        )
        return

    checked = validate_domain_foundation(repo_root=repo_root)
    if str(checked.get("result", "")) != "complete":
        for row in checked.get("errors") or []:
            if not isinstance(row, dict):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=str(row.get("path", "data/registries/domain_registry.json")),
                    line_number=1,
                    snippet="",
                    message=str(row.get("message", "")),
                    rule_id="INV-DOMAIN-REGISTRY-VALID",
                )
            )

    solver_payload, solver_err = _load_json_object(repo_root, "data/registries/solver_registry.json")
    if solver_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/solver_registry.json",
                line_number=1,
                snippet="",
                message="solver registry JSON is invalid",
                rule_id="INV-SOLVER-DOMAIN-BINDING",
            )
        )
    else:
        rows = solver_payload.get("records")
        if not isinstance(rows, list):
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/solver_registry.json",
                    line_number=1,
                    snippet="",
                    message="solver registry records list is missing",
                    rule_id="INV-SOLVER-DOMAIN-BINDING",
                )
            )
        else:
            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                solver_id = str(row.get("solver_id", "")).strip()
                domain_ids = [str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip()]
                contract_ids = [str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip()]
                if not domain_ids or not contract_ids:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/solver_registry.json",
                            line_number=1,
                            snippet="",
                            message="solver '{}' at records[{}] must declare non-empty domain_ids and contract_ids".format(
                                solver_id or "<unknown>",
                                idx,
                            ),
                            rule_id="INV-SOLVER-DOMAIN-BINDING",
                        )
                    )

    contract_payload, contract_err = _load_json_object(repo_root, "data/registries/domain_contract_registry.json")
    if contract_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="domain contract registry JSON is invalid",
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )
        return
    contract_rows = contract_payload.get("records")
    if not isinstance(contract_rows, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="domain contract registry records list is missing",
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )
        return
    current_ids = set(
        str(row.get("contract_id", "")).strip()
        for row in contract_rows
        if isinstance(row, dict) and str(row.get("contract_id", "")).strip()
    )
    schema_version = str(contract_payload.get("schema_version", "")).strip()
    missing_baseline = sorted(set(CONTRACT_STABILITY_BASELINE_IDS) - current_ids)
    if schema_version == "1.0.0" and missing_baseline:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="contract IDs removed/renamed without schema version bump: {}".format(",".join(missing_baseline)),
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )


def _worldgen_constraint_contributions(repo_root: str) -> List[Dict[str, str]]:
    packs_root = os.path.join(repo_root, "packs")
    if not os.path.isdir(packs_root):
        return []

    rows: List[Dict[str, str]] = []
    for walk_root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        if "pack.json" not in files:
            continue
        rel_manifest = _norm(os.path.relpath(os.path.join(walk_root, "pack.json"), repo_root))
        payload, err = _load_json_object(repo_root, rel_manifest)
        if err:
            continue
        pack_id = str(payload.get("pack_id", "")).strip()
        contributions = payload.get("contributions")
        if not isinstance(contributions, list):
            continue
        for idx, row in enumerate(contributions):
            if not isinstance(row, dict):
                continue
            if str(row.get("type", "")).strip() != "worldgen_constraints":
                continue
            contribution_id = str(row.get("id", "")).strip()
            contribution_path = str(row.get("path", "")).strip()
            rows.append(
                {
                    "manifest": rel_manifest,
                    "pack_id": pack_id,
                    "contribution_id": contribution_id,
                    "contribution_path": contribution_path,
                    "contribution_index": str(idx),
                }
            )
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("pack_id", "")),
            str(item.get("contribution_id", "")),
            str(item.get("contribution_path", "")),
            str(item.get("manifest", "")),
        ),
    )


def _append_worldgen_constraint_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    for rel_path in WORLDGEN_CONSTRAINT_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required worldgen constraints contract file is missing",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )

    try:
        from tools.xstack.compatx.validator import validate_instance
    except Exception:
        validate_instance = None

    registry_payload, registry_error = _load_json_object(repo_root, "data/registries/worldgen_constraints_registry.json")
    registry_entries = (((registry_payload.get("record") or {}).get("entries")) or []) if not registry_error else []
    registry_by_id: Dict[str, Dict[str, object]] = {}
    if registry_error:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet="",
                message="worldgen constraints registry JSON is invalid",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )
    elif not isinstance(registry_entries, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet="",
                message="worldgen constraints registry entries list is missing",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )
    else:
        for idx, row in enumerate(registry_entries):
            if not isinstance(row, dict):
                continue
            constraints_id = str(row.get("constraints_id", "")).strip()
            if not constraints_id:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/worldgen_constraints_registry.json",
                        line_number=1,
                        snippet="",
                        message="entry[{}] missing constraints_id".format(idx),
                        rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                    )
                )
                continue
            if constraints_id in registry_by_id:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/worldgen_constraints_registry.json",
                        line_number=1,
                        snippet=constraints_id,
                        message="duplicate constraints_id '{}' in registry".format(constraints_id),
                        rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                    )
                )
                continue
            registry_by_id[constraints_id] = row

    contributions = _worldgen_constraint_contributions(repo_root)
    contribution_ids = set()
    for row in contributions:
        manifest = str(row.get("manifest", ""))
        pack_id = str(row.get("pack_id", ""))
        constraints_id = str(row.get("contribution_id", ""))
        contribution_path = str(row.get("contribution_path", ""))
        contribution_ids.add(constraints_id)
        if constraints_id not in registry_by_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=constraints_id,
                    message="worldgen constraints contribution id is missing from registry",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )
            continue
        registry_entry = dict(registry_by_id.get(constraints_id) or {})
        expected_pack_id = str(registry_entry.get("pack_id", "")).strip()
        if expected_pack_id and pack_id and expected_pack_id != pack_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=constraints_id,
                    message="constraints registry pack_id mismatch for '{}'".format(constraints_id),
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )

        pack_manifest_dir = os.path.dirname(manifest)
        payload_rel_path = _norm(os.path.join(pack_manifest_dir, contribution_path))
        payload_abs_path = os.path.join(repo_root, payload_rel_path.replace("/", os.sep))
        if not os.path.isfile(payload_abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=contribution_path,
                    message="worldgen constraints contribution path does not exist",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )
            continue

        payload, payload_error = _load_json_object(repo_root, payload_rel_path)
        if payload_error:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="",
                    message="worldgen constraints payload JSON is invalid",
                    rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                )
            )
            continue

        if validate_instance is None:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="tools/xstack/compatx/validator.py",
                    line_number=1,
                    snippet="",
                    message="unable to import schema validator for worldgen constraints",
                    rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                )
            )
        else:
            checked = validate_instance(
                repo_root=repo_root,
                schema_name="worldgen_constraints",
                payload=payload,
                strict_top_level=True,
            )
            if not bool(checked.get("valid", False)):
                for err in list(checked.get("errors") or [])[:10]:
                    if not isinstance(err, dict):
                        continue
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=payload_rel_path,
                            line_number=1,
                            snippet=str(err.get("path", "")),
                            message="worldgen constraints schema violation: {}".format(str(err.get("message", ""))),
                            rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                        )
                    )

        policy = str(payload.get("deterministic_seed_policy", "")).strip()
        try:
            candidate_count = int(payload.get("candidate_count", 0))
        except (TypeError, ValueError):
            candidate_count = 0
        refusal_codes = sorted(
            set(str(item).strip() for item in (payload.get("refusal_codes") or []) if str(item).strip())
        )
        if policy not in ("single", "multi"):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet=policy,
                    message="deterministic_seed_policy must be single or multi",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        if policy == "single" and candidate_count != 1:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="candidate_count={}".format(candidate_count),
                    message="single deterministic_seed_policy requires candidate_count == 1",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        if candidate_count < 1:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="candidate_count={}".format(candidate_count),
                    message="candidate_count must be >= 1 for deterministic search",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        missing_refusals = sorted(
            set(("refusal.constraints_unsatisfiable", "refusal.search_exhausted")) - set(refusal_codes)
        )
        if missing_refusals:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet=",".join(missing_refusals),
                    message="constraints artifact missing required refusal_codes",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )

    for constraints_id in sorted(set(registry_by_id.keys()) - set(contribution_ids)):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet=constraints_id,
                message="registry constraints_id has no matching worldgen_constraints pack contribution",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )

    constraint_solver_rel = "worldgen/core/constraint_solver.py"
    for line_no, line in _iter_lines(repo_root, constraint_solver_rel):
        lower = str(line).lower()
        for token in WORLDGEN_SEED_POLICY_FORBIDDEN_TOKENS:
            if token in lower:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=constraint_solver_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="forbidden nondeterministic seed source token '{}' detected".format(token),
                        rule_id="INV-DETERMINISTIC-SEED-POLICY",
                    )
                )


def _append_constraint_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in WORLDGEN_CONSTRAINT_LITERAL_ALLOWED_PATH_PREFIXES):
        return
    match = re.search(r'["\'](constraints\.[A-Za-z0-9_.-]+)["\']', line)
    if not match:
        return
    token = str(match.group(1))
    if token.startswith("constraints.worldgen."):
        return
    lower = line.lower()
    if "constraints_id" not in lower and "constraints-id" not in lower:
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded worldgen constraints_id literal detected outside registry/pack declarations",
            rule_id="INV-NO-HARDCODED-CONSTRAINT-LOGIC",
        )
    )


def _git_status_paths(repo_root: str) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return []
    if int(proc.returncode) != 0:
        return []
    rows = []
    for line in (proc.stdout or "").splitlines():
        token = str(line[3:] if len(line) >= 3 else line).strip()
        if token:
            rows.append(_norm(token))
    return sorted(set(rows))


def _runtime_status_paths(repo_root: str) -> List[str]:
    return sorted(path for path in _git_status_paths(repo_root) if path.startswith(RUNTIME_PATH_PREFIXES))


def _append_auditx_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    abs_path = os.path.join(repo_root, AUDITX_FINDINGS_PATH.replace("/", os.sep))
    if os.path.isfile(abs_path):
        payload, err = _load_json_object(repo_root, AUDITX_FINDINGS_PATH)
        if err:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=AUDITX_FINDINGS_PATH,
                    line_number=1,
                    snippet="",
                    message="AuditX findings payload is invalid JSON",
                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                )
            )
        else:
            records = payload.get("findings")
            if not isinstance(records, list):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=AUDITX_FINDINGS_PATH,
                        line_number=1,
                        snippet="",
                        message="AuditX findings payload missing 'findings' list",
                        rule_id="INV-AUDITX-REPORT-STRUCTURE",
                    )
                )
            else:
                try:
                    from tools.auditx.model import validate_finding_record
                except Exception:
                    validate_finding_record = None
                if validate_finding_record is None:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="tools/auditx/model/finding.py",
                            line_number=1,
                            snippet="",
                            message="unable to import AuditX finding validator",
                            rule_id="INV-AUDITX-REPORT-STRUCTURE",
                        )
                    )
                else:
                    for idx, row in enumerate(records):
                        if not isinstance(row, dict):
                            findings.append(
                                _finding(
                                    severity=severity,
                                    file_path=AUDITX_FINDINGS_PATH,
                                    line_number=1,
                                    snippet="",
                                    message="finding at index {} is not an object".format(idx),
                                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                                )
                            )
                            continue
                        for message in validate_finding_record(row):
                            findings.append(
                                _finding(
                                    severity=severity,
                                    file_path=AUDITX_FINDINGS_PATH,
                                    line_number=1,
                                    snippet="",
                                    message="finding[{}]: {}".format(idx, message),
                                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                                )
                            )
                            if len(findings) >= 250:
                                break
                        if len(findings) >= 250:
                            break

                high_risk = 0
                for row in records:
                    if not isinstance(row, dict):
                        continue
                    severity_token = str(row.get("severity", "")).strip().upper()
                    if severity_token not in ("RISK", "VIOLATION"):
                        continue
                    try:
                        confidence = float(row.get("confidence", 0.0))
                    except (TypeError, ValueError):
                        confidence = 0.0
                    if confidence >= AUDITX_HIGH_RISK_CONFIDENCE:
                        high_risk += 1
                if high_risk >= AUDITX_HIGH_RISK_THRESHOLD:
                    findings.append(
                        _finding(
                            severity="warn",
                            file_path=AUDITX_FINDINGS_PATH,
                            line_number=1,
                            snippet="",
                            message="high-confidence AuditX risk findings exceed threshold ({} >= {})".format(
                                high_risk,
                                AUDITX_HIGH_RISK_THRESHOLD,
                            ),
                            rule_id="INV-AUDITX-REPORT-STRUCTURE",
                        )
                    )

    pre_runtime = _runtime_status_paths(repo_root)
    command = [
        sys.executable,
        "tools/auditx/auditx.py",
        "scan",
        "--repo-root",
        repo_root,
        "--changed-only",
        "--format",
        "json",
        "--output-root",
        AUDITX_RUNTIME_PROBE_OUTPUT_ROOT,
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError:
        findings.append(
            _finding(
                severity="warn",
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet="",
                message="AuditX probe scan unavailable in current environment",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return

    scan_output = str(proc.stdout or "")
    if int(proc.returncode) not in (0, 2):
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet=scan_output.strip()[:140],
                message="AuditX probe scan failed unexpectedly (exit={})".format(int(proc.returncode)),
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return
    if "\"refusal_code\": \"refusal.git_unavailable\"" in scan_output:
        findings.append(
            _finding(
                severity="warn",
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet="refusal.git_unavailable",
                message="AuditX changed-only probe reported git unavailable",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return

    post_runtime = _runtime_status_paths(repo_root)
    new_runtime_paths = sorted(set(post_runtime) - set(pre_runtime))
    for rel_path in new_runtime_paths:
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="AuditX scan modified tracked runtime path",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )


def _append_forbidden_identifier_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    lower = line.lower()
    for token in FORBIDDEN_IDENTIFIERS:
        pattern = r"\b{}\b".format(re.escape(token))
        if re.search(pattern, lower):
            severity = "refusal"
            if token == "sandbox" and profile == "FAST":
                severity = "warn"
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="forbidden identifier '{}' detected".format(token),
                    rule_id="repox.forbidden_identifier",
                )
            )


def _append_mode_flag_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    match = re.search(r"\b([a-zA-Z_][a-zA-Z0-9_]*_mode)\b", line)
    if not match:
        return
    lhs = str(match.group(1))
    lower = line.lower()
    is_toggle = any(flag in lower for flag in ("= true", "= false", ": true", ": false", "=0", "=1", ":0", ":1"))
    if not is_toggle:
        return
    severity = "warn" if profile == "FAST" else "refusal"
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="mode-flag heuristic matched '{}'".format(lhs),
            rule_id="repox.mode_flag_heuristic",
        )
    )


def _append_reserved_misuse_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    exempt_roots = (
        "schemas/",
        "schema/",
        "docs/",
    )
    exempt_files = (
        "data/registries/session_stage_registry.json",
        "data/registries/session_pipeline_registry.json",
    )
    if rel_norm.startswith(exempt_roots) or rel_norm in exempt_files:
        return
    for token in RESERVED_WORDS:
        pattern = r'"{}"\s*:\s*(true|false|0|1)'.format(re.escape(token))
        if re.search(pattern, line, flags=re.IGNORECASE):
            severity = "warn" if profile == "FAST" else "fail"
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="reserved word '{}' used as generic config flag".format(token),
                    rule_id="repox.reserved_word_flag_misuse",
                )
            )


def _append_domain_token_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in DOMAIN_TOKEN_ALLOWED_PATH_PREFIXES):
        return
    pattern = r'["\']dom\.domain\.[A-Za-z0-9_.-]+["\']'
    if not re.search(pattern, line):
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded domain token literal detected outside registry-governed paths",
            rule_id="INV-NO-HARDCODED-DOMAIN-TOKENS",
        )
    )


def _append_strict_placeholder_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if profile not in ("STRICT", "FULL"):
        return
    if rel_path == "tools/xstack/repox/check.py":
        return
    lower = line.lower()
    placeholder_hits = (
        "renderer_truth_include",
        "truth_renderer_include",
        "include_renderer_truth",
    )
    if any(hit in lower for hit in placeholder_hits):
        findings.append(
            _finding(
                severity="refusal",
                file_path=rel_path,
                line_number=line_no,
                snippet=line.strip()[:140],
                message="forbidden renderer/truth include placeholder detected",
                rule_id="repox.renderer_truth_placeholder",
            )
        )


def _append_renderer_truth_boundary_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if profile not in ("STRICT", "FULL"):
        return
    rel_norm = _norm(rel_path).lower()
    if not rel_norm.startswith("client/presentation/"):
        return
    match = INCLUDE_RE.match(line)
    if match:
        include_path = str(match.group(1)).replace("\\", "/").lower()
        if include_path in RENDERER_TRUTH_INCLUDE_FORBIDDEN:
            findings.append(
                _finding(
                    severity="refusal",
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="renderer include/import of TruthModel header is forbidden",
                    rule_id="repox.renderer_truth_import",
                )
            )
            return
    if "dom_truth_model_v1" in line:
        findings.append(
            _finding(
                severity="refusal",
                file_path=rel_path,
                line_number=line_no,
                snippet=line.strip()[:140],
                message="renderer usage of TruthModel symbol is forbidden",
                rule_id="repox.renderer_truth_symbol",
            )
        )


def run_repox_check(repo_root: str, profile: str) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    files = _scan_files(repo_root)
    findings: List[Dict[str, object]] = []

    for rel_path in files:
        for line_no, line in _iter_lines(repo_root, rel_path):
            _append_forbidden_identifier_findings(findings, rel_path, line_no, line, token)
            _append_mode_flag_findings(findings, rel_path, line_no, line, token)
            _append_reserved_misuse_findings(findings, rel_path, line_no, line, token)
            _append_domain_token_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_constraint_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_strict_placeholder_findings(findings, rel_path, line_no, line, token)
            _append_renderer_truth_boundary_findings(findings, rel_path, line_no, line, token)
    _append_session_pipeline_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_domain_foundation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_worldgen_constraint_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_auditx_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )

    ordered = sorted(
        findings,
        key=lambda row: (
            _severity_rank(str(row.get("severity", ""))),
            str(row.get("file_path", "")),
            int(row.get("line_number", 0) or 0),
            str(row.get("rule_id", "")),
            str(row.get("message", "")),
        ),
    )
    status = _status_from_findings(ordered)
    message = "repox scan {} (files={}, findings={})".format(
        "passed" if status == "pass" else "completed_with_findings",
        len(files),
        len(ordered),
    )
    return {
        "status": status,
        "message": message,
        "findings": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic RepoX minimal policy checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_repox_check(repo_root=repo_root, profile=str(args.profile))
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
