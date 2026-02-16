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
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_resync_strategy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "data/registries/anti_cheat_module_registry.json",
    "data/registries/worldgen_constraints_registry.json",
    "data/registries/worldgen_module_registry.json",
    "packs",
    "bundles",
    "docs/contracts",
    "docs/net",
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

CONTRACT_TOKEN_ALLOWED_PATH_PREFIXES = (
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
    "docs/scale/",
    "schema/scale/",
    "schemas/domain_foundation_registry.schema.json",
    "schemas/domain_contract_registry.schema.json",
    "schemas/solver_registry.schema.json",
    "tools/domain/",
    "tools/xstack/testx/tests/",
)

NEGATIVE_SCAN_ROOTS = (
    "engine",
    "game",
    "client",
    "server",
    "tools",
    "launcher",
    "setup",
)

NEGATIVE_SCAN_EXCLUDED_PREFIXES = (
    "tools/xstack/out/",
    "tools/xstack/testdata/",
    "tools/xstack/testx/tests/",
    "tools/auditx/cache/",
    "build/",
    "dist/",
    "docs/",
    "data/",
)

NEGATIVE_SCAN_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".py",
    ".cmd",
}

SCHEMA_READ_ALLOWED_PREFIXES = (
    "tools/xstack/compatx/",
    "tools/xstack/schema_validate.py",
    "tools/domain/",
)

SESSION_PIPELINE_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/",
    "tools/xstack/session_boot.py",
    "tools/xstack/session_control.py",
    "tools/xstack/session_server.py",
    "tools/xstack/session_surface.py",
)

CONTROL_MUTATION_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/testx/tests/",
)

BODY_MUTATION_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/testx/tests/",
)

REPRESENTATION_RENDER_ONLY_FILES = (
    "tools/xstack/sessionx/render_model.py",
)

COSMETIC_SEMANTIC_FORBIDDEN_TOKENS = (
    "collision_layer",
    "shape_type",
    "shape_parameters",
    "body_move_attempt",
    "speed_scalar",
    "velocity_mm_per_tick",
)

PLAYER_LITERAL_ALLOWED_PATH_PREFIXES = (
    "data/",
    "docs/",
    "schemas/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
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

MULTIPLAYER_NET_SCHEMA_NAMES = (
    "net_intent_envelope",
    "net_tick_intent_list",
    "net_hash_anchor_frame",
    "net_snapshot",
    "net_delta",
    "net_perceived_delta",
    "net_handshake",
    "net_anti_cheat_event",
)

MULTIPLAYER_POLICY_REGISTRY_FILES = (
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_resync_strategy_registry.json",
    "data/registries/net_server_policy_registry.json",
    "data/registries/securex_policy_registry.json",
    "data/registries/server_profile_registry.json",
    "data/registries/shard_map_registry.json",
    "data/registries/perception_interest_policy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "data/registries/anti_cheat_module_registry.json",
)

ANTI_CHEAT_REQUIRED_POLICY_IDS = (
    "policy.ac.detect_only",
    "policy.ac.casual_default",
    "policy.ac.rank_strict",
    "policy.ac.private_relaxed",
)
ANTI_CHEAT_ALLOWED_ACTIONS = (
    "audit",
    "refuse",
    "throttle",
    "terminate",
    "require_attestation",
)

NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES = (
    "data/registries/",
    "docs/net/",
    "docs/contracts/",
    "schemas/",
    "tools/xstack/testx/tests/",
    "tools/auditx/",
    "tools/xstack/registry_compile/",
    "tools/xstack/sessionx/",
    "tools/xstack/repox/",
)

AUDITX_FINDINGS_PATH = "docs/audit/auditx/FINDINGS.json"
AUDITX_RUNTIME_PROBE_OUTPUT_ROOT = ".xstack_cache/auditx/repox_probe"
AUDITX_HIGH_RISK_CONFIDENCE = 0.85
AUDITX_HIGH_RISK_THRESHOLD = 15

CI_LANE_WORKFLOW_PATH = ".github/workflows/xstack_lanes.yml"
CI_LANE_REQUIRED_JOBS = (
    "ci-dev",
    "ci-verify",
    "ci-dist",
)
CI_DEV_FORBIDDEN_PACKAGING_TOKENS = (
    "tools/setup/build",
    "tools/setup/build.py",
    "build_dist_layout",
    "packaging.verify",
    "dist/",
    "build/dist",
)

REGRESSION_LOCK_PATH = "data/regression/observer_baseline.json"
REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "bundle_id",
    "composite_hash_anchor",
    "pack_lock_hash",
    "registry_hashes",
    "update_policy",
)

MULTIPLAYER_REGRESSION_LOCK_PATH = "data/regression/multiplayer_baseline.json"
MULTIPLAYER_REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "bundle_id",
    "policy_baselines",
    "ranked_handshake_matrix_hash",
    "anti_cheat_fingerprint_hashes",
    "update_policy",
)

CONSISTENCY_MATRIX_PATH = "docs/audit/CROSS_SYSTEM_CONSISTENCY_MATRIX.md"
CONSISTENCY_MATRIX_REQUIRED_SYSTEMS = (
    "Engine",
    "Game",
    "Client",
    "Server",
    "Launcher",
    "Setup",
    "Tools",
    "Packs",
    "Schemas",
    "Registries",
    "UI IR",
    "Worldgen",
    "SRZ",
    "XStack (RepoX/TestX/AuditX/PerformX/CompatX/SecureX)",
)
CONSISTENCY_MATRIX_REQUIRED_COLUMNS = (
    "State mutation authority",
    "Artifact generation",
    "Registry consumption",
    "Schema validation",
    "Capability enforcement",
    "Determinism enforcement",
    "Refusal emission",
    "Packaging interaction",
    "Versioning/BII stamping",
    "Logging/run-meta",
    "Derived artifact production",
)

STATUS_NOW_PATH = "docs/STATUS_NOW.md"
STATUS_NOW_REQUIRED_SECTIONS = (
    "## REAL",
    "## SOON",
    "## STUB",
    "## DEFERRED",
)

RUNTIME_PATH_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "launcher/",
    "setup/",
    "libs/",
)

DERIVED_PROVENANCE_REQUIRED_FIELDS = (
    "artifact_type_id",
    "source_pack_id",
    "source_hash",
    "generator_tool_id",
    "generator_tool_version",
    "schema_version",
    "input_merkle_hash",
    "pack_lock_hash",
    "deterministic",
)

DERIVED_JSON_PATH_PREFIX = "packs/derived/"


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


def _iter_negative_code_files(repo_root: str) -> List[str]:
    out: List[str] = []
    for root in NEGATIVE_SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            for name in files:
                _, ext = os.path.splitext(name.lower())
                if ext not in NEGATIVE_SCAN_EXTENSIONS:
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(NEGATIVE_SCAN_EXCLUDED_PREFIXES):
                    continue
                out.append(rel_path)
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


def _append_multiplayer_contract_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in MULTIPLAYER_POLICY_REGISTRY_FILES:
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
                message="required multiplayer policy registry file is missing",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )

    try:
        from tools.xstack.compatx.validator import validate_schema_example
    except Exception:
        validate_schema_example = None

    if validate_schema_example is None:
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/xstack/compatx/validator.py",
                line_number=1,
                snippet="",
                message="unable to import schema validator for multiplayer schema checks",
                rule_id="INV-NET-SCHEMAS-VALID",
            )
        )
    else:
        for schema_name in MULTIPLAYER_NET_SCHEMA_NAMES:
            checked = validate_schema_example(repo_root=repo_root, schema_name=schema_name)
            if not bool(checked.get("valid", False)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="schemas/{}.schema.json".format(schema_name),
                        line_number=1,
                        snippet="",
                        message="multiplayer schema example validation failed for '{}'".format(schema_name),
                        rule_id="INV-NET-SCHEMAS-VALID",
                    )
                )

    if missing:
        return

    replication_payload, replication_err = _load_json_object(repo_root, "data/registries/net_replication_policy_registry.json")
    resync_payload, resync_err = _load_json_object(repo_root, "data/registries/net_resync_strategy_registry.json")
    server_policy_payload, server_policy_err = _load_json_object(repo_root, "data/registries/net_server_policy_registry.json")
    shard_map_payload, shard_map_err = _load_json_object(repo_root, "data/registries/shard_map_registry.json")
    perception_interest_payload, perception_interest_err = _load_json_object(
        repo_root,
        "data/registries/perception_interest_policy_registry.json",
    )
    anti_cheat_policy_payload, anti_cheat_policy_err = _load_json_object(repo_root, "data/registries/anti_cheat_policy_registry.json")
    anti_cheat_module_payload, anti_cheat_module_err = _load_json_object(repo_root, "data/registries/anti_cheat_module_registry.json")
    securex_policy_payload, securex_policy_err = _load_json_object(repo_root, "data/registries/securex_policy_registry.json")
    server_profile_payload, server_profile_err = _load_json_object(repo_root, "data/registries/server_profile_registry.json")
    if (
        replication_err
        or resync_err
        or server_policy_err
        or shard_map_err
        or perception_interest_err
        or anti_cheat_policy_err
        or anti_cheat_module_err
        or securex_policy_err
        or server_profile_err
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/net_replication_policy_registry.json",
                line_number=1,
                snippet="",
                message="one or more multiplayer policy registries are invalid JSON",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )
        return

    replication_rows = (((replication_payload.get("record") or {}).get("policies")) or [])
    resync_rows = (((resync_payload.get("record") or {}).get("strategies")) or [])
    server_policy_rows = (((server_policy_payload.get("record") or {}).get("policies")) or [])
    shard_map_rows = (((shard_map_payload.get("record") or {}).get("shard_maps")) or [])
    perception_interest_rows = (((perception_interest_payload.get("record") or {}).get("policies")) or [])
    anti_cheat_policy_rows = (((anti_cheat_policy_payload.get("record") or {}).get("policies")) or [])
    anti_cheat_module_rows = (((anti_cheat_module_payload.get("record") or {}).get("modules")) or [])
    securex_policy_rows = (((securex_policy_payload.get("record") or {}).get("policies")) or [])
    server_profile_rows = (((server_profile_payload.get("record") or {}).get("profiles")) or [])
    if (
        not isinstance(replication_rows, list)
        or not isinstance(resync_rows, list)
        or not isinstance(server_policy_rows, list)
        or not isinstance(shard_map_rows, list)
        or not isinstance(perception_interest_rows, list)
        or not isinstance(anti_cheat_policy_rows, list)
        or not isinstance(anti_cheat_module_rows, list)
        or not isinstance(securex_policy_rows, list)
        or not isinstance(server_profile_rows, list)
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/net_replication_policy_registry.json",
                line_number=1,
                snippet="",
                message="multiplayer policy registry record lists are missing",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )
        return

    shard_map_ids = set(
        str(row.get("shard_map_id", "")).strip()
        for row in shard_map_rows
        if isinstance(row, dict) and str(row.get("shard_map_id", "")).strip()
    )
    perception_policy_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in perception_interest_rows
        if isinstance(row, dict) and str(row.get("policy_id", "")).strip()
    )

    resync_ids = set()
    for row in resync_rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("strategy_id", "")).strip()
        if token:
            resync_ids.add(token)

    replication_ids = set()
    for row in replication_rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        replication_ids.add(policy_id)
        strategy_id = str(row.get("resync_strategy_id", "")).strip()
        if strategy_id and strategy_id not in resync_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_replication_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="replication policy '{}' references missing resync strategy '{}'".format(policy_id, strategy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )

    for row in resync_rows:
        if not isinstance(row, dict):
            continue
        strategy_id = str(row.get("strategy_id", "")).strip()
        for policy_id in sorted(set(str(item).strip() for item in (row.get("supported_policies") or []) if str(item).strip())):
            if policy_id not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_resync_strategy_registry.json",
                        line_number=1,
                        snippet=strategy_id,
                        message="resync strategy '{}' references missing replication policy '{}'".format(strategy_id, policy_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )

    module_ids = set()
    for row in anti_cheat_module_rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("module_id", "")).strip()
        if token:
            module_ids.add(token)

    anti_cheat_ids = set()
    for row in anti_cheat_policy_rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("policy_id", "")).strip()
        if policy_id:
            anti_cheat_ids.add(policy_id)
        else:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet="",
                    message="anti-cheat policy entry is missing policy_id",
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )
            continue
        modules_enabled = sorted(set(str(item).strip() for item in (row.get("modules_enabled") or []) if str(item).strip()))
        if not modules_enabled:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="anti-cheat policy '{}' must declare non-empty modules_enabled".format(policy_id),
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )
        for module_id in modules_enabled:
            if module_id not in module_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/anti_cheat_policy_registry.json",
                        line_number=1,
                        snippet=policy_id,
                        message="anti-cheat policy '{}' references missing module '{}'".format(policy_id, module_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        default_actions = row.get("default_actions")
        if isinstance(default_actions, dict):
            for module_id in sorted(default_actions.keys()):
                token = str(module_id).strip()
                if token and token not in module_ids:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet=policy_id,
                            message="anti-cheat policy '{}' default_actions references missing module '{}'".format(
                                policy_id,
                                token,
                            ),
                            rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                        )
                    )
                action_token = str(default_actions.get(module_id, "")).strip()
                if action_token and action_token not in ANTI_CHEAT_ALLOWED_ACTIONS:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet="{}={}".format(token, action_token),
                            message="anti-cheat policy '{}' default action '{}' is not allowed".format(policy_id, action_token),
                            rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                        )
                    )
            for module_id in modules_enabled:
                if module_id not in default_actions:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet=policy_id,
                            message="anti-cheat policy '{}' is missing default action for enabled module '{}'".format(
                                policy_id,
                                module_id,
                            ),
                            rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                        )
                    )
        else:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="anti-cheat policy '{}' default_actions must be an object".format(policy_id),
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )

    for policy_id in sorted(set(ANTI_CHEAT_REQUIRED_POLICY_IDS) - set(anti_cheat_ids)):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/anti_cheat_policy_registry.json",
                line_number=1,
                snippet=policy_id,
                message="required anti-cheat policy '{}' is missing".format(policy_id),
                rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
            )
        )

    securex_policy_ids = set(
        str(row.get("securex_policy_id", "")).strip()
        for row in securex_policy_rows
        if isinstance(row, dict) and str(row.get("securex_policy_id", "")).strip()
    )

    for row in server_policy_rows:
        if not isinstance(row, dict):
            continue
        server_policy_id = str(row.get("policy_id", "")).strip()
        for policy_id in row.get("allowed_replication_policy_ids") or []:
            token = str(policy_id).strip()
            if token and token not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' references missing replication policy '{}'".format(server_policy_id, token),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        allowed_anti_cheat_ids = []
        for policy_id in row.get("allowed_anti_cheat_policy_ids") or []:
            token = str(policy_id).strip()
            if token:
                allowed_anti_cheat_ids.append(token)
            if token and token not in anti_cheat_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' references missing anti-cheat policy '{}'".format(server_policy_id, token),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        required_anti_cheat_policy_id = str(row.get("required_anti_cheat_policy_id", "")).strip()
        if required_anti_cheat_policy_id and required_anti_cheat_policy_id not in allowed_anti_cheat_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_server_policy_registry.json",
                    line_number=1,
                    snippet=server_policy_id,
                    message="server policy '{}' required anti-cheat policy is not present in allowed_anti_cheat_policy_ids".format(
                        server_policy_id
                    ),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        securex_policy_id = str(row.get("securex_policy_id", "")).strip()
        if securex_policy_id and securex_policy_id not in securex_policy_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_server_policy_registry.json",
                    line_number=1,
                    snippet=server_policy_id,
                    message="server policy '{}' references missing securex policy '{}'".format(server_policy_id, securex_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        allowed_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_replication_policy_ids") or []) if str(item).strip())
        )
        if "policy.net.srz_hybrid" in allowed_replication_ids:
            extensions = dict(row.get("extensions") or {})
            shard_map_id = str(extensions.get("default_shard_map_id", "")).strip()
            if not shard_map_id or shard_map_id not in shard_map_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' must declare a valid extensions.default_shard_map_id when srz_hybrid is allowed".format(
                            server_policy_id
                        ),
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                    )
                )
            perception_policy_id = str(extensions.get("perception_interest_policy_id", "")).strip()
            if not perception_policy_id or perception_policy_id not in perception_policy_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' must declare a valid extensions.perception_interest_policy_id when srz_hybrid is allowed".format(
                            server_policy_id
                        ),
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                )
            )

    for row in server_profile_rows:
        if not isinstance(row, dict):
            continue
        server_profile_id = str(row.get("server_profile_id", "")).strip()
        securex_policy_id = str(row.get("securex_policy_id", "")).strip()
        anti_cheat_policy_id = str(row.get("anti_cheat_policy_id", "")).strip()
        allowed_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_replication_policy_ids") or []) if str(item).strip())
        )
        required_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("required_replication_policy_ids") or []) if str(item).strip())
        )
        allowed_law_profile_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_law_profile_ids") or []) if str(item).strip())
        )
        if securex_policy_id not in securex_policy_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' references missing securex policy '{}'".format(server_profile_id, securex_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        if anti_cheat_policy_id not in anti_cheat_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' references missing anti-cheat policy '{}'".format(server_profile_id, anti_cheat_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        for policy_id in allowed_replication_ids + required_replication_ids:
            if policy_id not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/server_profile_registry.json",
                        line_number=1,
                        snippet=server_profile_id,
                        message="server profile '{}' references missing replication policy '{}'".format(server_profile_id, policy_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        if not allowed_law_profile_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' must declare non-empty allowed_law_profile_ids".format(server_profile_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )

    required_registry_refs = (
        (
            "tools/xstack/sessionx/net_handshake.py",
            (
                "replication_registry",
                "anti_cheat_registry",
                "server_policy_registry",
                "securex_policy_registry",
                "server_profile_registry",
            ),
        ),
    )
    for rel_path, required_tokens in required_registry_refs:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="net handshake implementation file is missing",
                    rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="unable to read net handshake implementation for registry-usage invariant",
                    rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                )
            )
            continue
        for token in required_tokens:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="net handshake implementation is missing required registry reference token '{}'".format(token),
                        rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                    )
                )

    token_severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    hardcoded_policy_literal_pattern = re.compile(r"(policy\.net\.[a-z0-9_.-]+|policy\.ac\.[a-z0-9_.-]+)", re.IGNORECASE)
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if any(rel_norm.startswith(prefix) for prefix in NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES):
            continue
        _, ext = os.path.splitext(rel_norm.lower())
        if ext not in {".py", ".c", ".cc", ".cpp", ".h", ".hpp", ".hh", ".cxx", ".hxx"}:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            if hardcoded_policy_literal_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=token_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded network policy literal detected outside registry-governed paths",
                        rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                    )
                )

    flag_pattern = re.compile(r"\bif\s*\([^)]*(lockstep|server_authoritative|srz_hybrid)[^)]*\)", re.IGNORECASE)
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if any(rel_norm.startswith(prefix) for prefix in NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES):
            continue
        _, ext = os.path.splitext(rel_norm.lower())
        if ext not in {".py", ".c", ".cc", ".cpp", ".h", ".hpp", ".hh", ".cxx", ".hxx"}:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            if flag_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=token_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded network policy branch detected; select replication policy by policy_id",
                        rule_id="INV-NO-HARDCODED-NET-POLICY-FLAGS",
                    )
                )

    truth_net_pattern = re.compile(
        r"(truthmodel|truth_model).*(serialize|json|packet|socket|network|replication|delta|snapshot)"
        r"|"
        r"(serialize|json|packet|socket|network|replication|delta|snapshot).*(truthmodel|truth_model)",
        re.IGNORECASE,
    )
    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/", "tools/xstack/auditx/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "truth_snapshot_hash" in lower:
                continue
            if truth_net_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="TruthModel network serialization smell detected; transmit PerceivedModel/snapshot hashes only",
                        rule_id="INV-NO-TRUTH-OVER-NET",
                    )
                )
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="network payload path must remain PerceivedModel-only and avoid TruthModel serialization",
                        rule_id="INV-NET-PERCEIVED-ONLY",
                    )
                )

    perceived_required = (
        ("src/net/policies/policy_server_authoritative.py", ("observe_truth(", "schema_name=\"net_perceived_delta\"")),
        ("src/net/srz/shard_coordinator.py", ("observe_truth(", "schema_name=\"net_perceived_delta\"")),
    )
    for rel_path, required_tokens in perceived_required:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="network perceived-only invariant target file is missing",
                    rule_id="INV-NET-PERCEIVED-ONLY",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="unable to read file for perceived-only invariant",
                    rule_id="INV-NET-PERCEIVED-ONLY",
                )
            )
            continue
        for token in required_tokens:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="network path missing required perceived-only token '{}'".format(token),
                        rule_id="INV-NET-PERCEIVED-ONLY",
                    )
                )

    law_registry_path = "data/registries/law_profiles.json"
    law_registry_payload, law_registry_err = _load_json_object(repo_root, law_registry_path)
    law_rows = []
    if not law_registry_err:
        law_rows = (((law_registry_payload.get("record") or {}).get("profiles")) or [])
        if isinstance(law_rows, list):
            for idx, row in enumerate(law_rows):
                if not isinstance(row, dict):
                    continue
                law_profile_id = str(row.get("law_profile_id", "")).strip() or "<unknown>"
                if not str(row.get("epistemic_policy_id", "")).strip():
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=law_registry_path,
                            line_number=1,
                            snippet=law_profile_id,
                            message="law profile '{}' is missing epistemic_policy_id".format(law_profile_id),
                            rule_id="INV-EPISTEMIC-POLICY-REQUIRED",
                        )
                    )
                if "survival" in law_profile_id.lower():
                    allowed_lenses = sorted(
                        set(str(item).strip().lower() for item in (row.get("allowed_lenses") or []) if str(item).strip())
                    )
                    if any("nondiegetic" in token for token in allowed_lenses):
                        findings.append(
                            _finding(
                                severity="warn",
                                file_path=law_registry_path,
                                line_number=1,
                                snippet=law_profile_id,
                                message="survival profile '{}' should default to diegetic lenses only".format(law_profile_id),
                                rule_id="INV-DIEGETIC-DEFAULTS-SURVIVAL",
                            )
                        )

    packs_law_root = os.path.join(repo_root, "packs", "law")
    if os.path.isdir(packs_law_root):
        for walk_root, dirs, files in os.walk(packs_law_root):
            dirs[:] = sorted(dirs)
            if "pack.json" not in files:
                continue
            data_root = os.path.join(walk_root, "data")
            if not os.path.isdir(data_root):
                continue
            for name in sorted(os.listdir(data_root)):
                if not str(name).lower().endswith(".json"):
                    continue
                abs_file = os.path.join(data_root, name)
                rel_file = _norm(os.path.relpath(abs_file, repo_root))
                payload, err = _load_json_object(repo_root, rel_file)
                if err:
                    continue
                if not str(payload.get("law_profile_id", "")).strip():
                    continue
                law_profile_id = str(payload.get("law_profile_id", "")).strip()
                if not str(payload.get("epistemic_policy_id", "")).strip():
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_file,
                            line_number=1,
                            snippet=law_profile_id,
                            message="pack law profile '{}' is missing epistemic_policy_id".format(law_profile_id),
                            rule_id="INV-EPISTEMIC-POLICY-REQUIRED",
                        )
                    )

    authoritative_rel = "src/net/policies/policy_server_authoritative.py"
    authoritative_abs = os.path.join(repo_root, authoritative_rel.replace("/", os.sep))
    if not os.path.isfile(authoritative_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=authoritative_rel,
                line_number=1,
                snippet="",
                message="server-authoritative policy implementation file is missing",
                rule_id="INV-AUTHORITATIVE-USES-PERCEIVED-ONLY",
            )
        )
    else:
        try:
            authoritative_lines = open(authoritative_abs, "r", encoding="utf-8").read().splitlines()
        except OSError:
            authoritative_lines = []
        authoritative_text = "\n".join(authoritative_lines)
        if "observe_truth(" not in authoritative_text or "schema_name=\"net_perceived_delta\"" not in authoritative_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=authoritative_rel,
                    line_number=1,
                    snippet="observe_truth/net_perceived_delta",
                    message="server-authoritative policy must derive outbound state through Observation Kernel perceived deltas",
                    rule_id="INV-AUTHORITATIVE-USES-PERCEIVED-ONLY",
                )
            )
        authoritative_truth_leak_pattern = re.compile(
            r"(send|socket|packet|transport|wire|payload_ref).*(truth_model|truthmodel|universe_state)"
            r"|"
            r"(truth_model|truthmodel|universe_state).*(send|socket|packet|transport|wire)",
            re.IGNORECASE,
        )
        for line_no, line in enumerate(authoritative_lines, start=1):
            lower = str(line).lower()
            if "truth_snapshot_hash" in lower:
                continue
            if authoritative_truth_leak_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=authoritative_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="server-authoritative policy must not transmit TruthModel/universe_state payload over net path",
                        rule_id="INV-AUTHORITATIVE-NO-TRUTH-TRANSMISSION",
                    )
                )

    srz_routing_rel = "src/net/srz/routing.py"
    srz_routing_abs = os.path.join(repo_root, srz_routing_rel.replace("/", os.sep))
    if not os.path.isfile(srz_routing_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=srz_routing_rel,
                line_number=1,
                snippet="",
                message="SRZ routing module is missing",
                rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
            )
        )
    else:
        try:
            srz_routing_text = open(srz_routing_abs, "r", encoding="utf-8").read()
        except OSError:
            srz_routing_text = ""
        required_tokens = ("def route_intent_envelope", "shard_index(", "shard_map", "site_registry")
        for token in required_tokens:
            if token not in srz_routing_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=srz_routing_rel,
                        line_number=1,
                        snippet=token,
                        message="SRZ routing must resolve targets from shard_map-driven metadata",
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                    )
                )

    srz_coordinator_rel = "src/net/srz/shard_coordinator.py"
    srz_coordinator_abs = os.path.join(repo_root, srz_coordinator_rel.replace("/", os.sep))
    if not os.path.isfile(srz_coordinator_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=srz_coordinator_rel,
                line_number=1,
                snippet="",
                message="SRZ shard coordinator module is missing",
                rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
            )
        )
    else:
        try:
            srz_coordinator_text = open(srz_coordinator_abs, "r", encoding="utf-8").read()
        except OSError:
            srz_coordinator_text = ""
        if "owner_shard_id != target_shard_id" not in srz_coordinator_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=srz_coordinator_rel,
                    line_number=1,
                    snippet="owner_shard_id != target_shard_id",
                    message="SRZ coordinator must enforce owner-target shard mismatch checks before commit",
                    rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
                )
            )
        if "refusal.net.cross_shard_unsupported" not in srz_coordinator_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=srz_coordinator_rel,
                    line_number=1,
                    snippet="refusal.net.cross_shard_unsupported",
                    message="SRZ coordinator must refuse unsupported cross-shard direct writes deterministically",
                    rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
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


def _derived_artifact_files(repo_root: str) -> List[str]:
    root = os.path.join(repo_root, "packs", "derived")
    rows: List[str] = []
    if not os.path.isdir(root):
        return rows
    for walk_root, dirs, files in os.walk(root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not str(name).lower().endswith(".json"):
                continue
            if str(name).lower() == "pack.json":
                continue
            abs_path = os.path.join(walk_root, name)
            rows.append(_norm(os.path.relpath(abs_path, repo_root)))
    return sorted(set(rows))


def _append_derived_provenance_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    for rel_path in _derived_artifact_files(repo_root):
        payload, err = _load_json_object(repo_root, rel_path)
        if err:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="derived artifact payload must be valid JSON object",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )
            continue
        provenance = payload.get("provenance")
        if not isinstance(provenance, dict):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="derived artifact is missing required provenance object",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )
            continue
        for field in DERIVED_PROVENANCE_REQUIRED_FIELDS:
            token = provenance.get(field)
            if token is None or (isinstance(token, str) and not str(token).strip()):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=str(field),
                        message="derived provenance missing required field '{}'".format(field),
                        rule_id="INV-DERIVED-HAS-PROVENANCE",
                    )
                )
        if bool(provenance.get("deterministic", False)) is not True:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="deterministic={}".format(str(provenance.get("deterministic"))),
                    message="derived provenance deterministic flag must be true",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )

        source_hash = str(provenance.get("source_hash", "")).strip()
        input_merkle_hash = str(provenance.get("input_merkle_hash", "")).strip()
        if source_hash.startswith("placeholder.") or input_merkle_hash.startswith("placeholder."):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="source_hash={} input_merkle_hash={}".format(source_hash, input_merkle_hash)[:140],
                    message="derived artifact appears hand-edited (placeholder provenance hashes)",
                    rule_id="INV-NO-HAND_EDITED-DERIVED",
                )
            )

        generator_tool = str(provenance.get("generator_tool_id", "")).strip()
        if generator_tool and not os.path.isfile(os.path.join(repo_root, generator_tool.replace("/", os.sep))):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=generator_tool,
                    message="derived provenance references missing generator tool path",
                    rule_id="INV-NO-HAND_EDITED-DERIVED",
                )
            )


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


def _append_ci_lane_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    workflow_path = os.path.join(repo_root, CI_LANE_WORKFLOW_PATH.replace("/", os.sep))
    if not os.path.isfile(workflow_path):
        findings.append(
            _finding(
                severity=severity,
                file_path=CI_LANE_WORKFLOW_PATH,
                line_number=1,
                snippet="",
                message="required CI lane workflow is missing",
                rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
            )
        )
        return

    try:
        lines = open(workflow_path, "r", encoding="utf-8").read().splitlines()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=CI_LANE_WORKFLOW_PATH,
                line_number=1,
                snippet="",
                message="unable to read CI lane workflow",
                rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
            )
        )
        return

    lowered = "\n".join(lines).lower()
    for job_id in CI_LANE_REQUIRED_JOBS:
        marker = "\n  {}:".format(job_id)
        if marker not in ("\n" + lowered):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CI_LANE_WORKFLOW_PATH,
                    line_number=1,
                    snippet=job_id,
                    message="missing required CI lane job '{}'".format(job_id),
                    rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
                )
            )

    start = -1
    end = len(lines)
    for idx, line in enumerate(lines):
        if line.strip().lower() == "ci-dev:" and line.startswith("  "):
            start = idx
            break
    if start == -1:
        return
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if re.match(r"^\s{2}[A-Za-z0-9_-]+:\s*$", line):
            end = idx
            break
    dev_block = "\n".join(lines[start:end]).lower()
    for token in CI_DEV_FORBIDDEN_PACKAGING_TOKENS:
        if str(token).lower() in dev_block:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CI_LANE_WORKFLOW_PATH,
                    line_number=start + 1,
                    snippet=str(token),
                    message="ci-dev lane must not invoke packaging token '{}'".format(token),
                    rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
                )
            )


def _append_regression_lock_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    payload, err = _load_json_object(repo_root, REGRESSION_LOCK_PATH)
    if err:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="observer regression baseline lock file is missing or invalid",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    for field in REGRESSION_LOCK_REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="regression lock missing required field '{}'".format(field),
                    rule_id="INV-REGRESSION-LOCK-PRESENT",
                )
            )
    registry_hashes = payload.get("registry_hashes")
    if not isinstance(registry_hashes, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="registry_hashes",
                message="regression lock registry_hashes must be an object",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for key in ("ephemeris_registry_hash", "terrain_tile_registry_hash"):
            if not str(registry_hashes.get(key, "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=key,
                        message="regression lock missing required registry hash '{}'".format(key),
                        rule_id="INV-REGRESSION-LOCK-PRESENT",
                    )
                )

    update_policy = payload.get("update_policy")
    required_tag = ""
    if isinstance(update_policy, dict):
        required_tag = str(update_policy.get("required_commit_tag", "")).strip()
    if not required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(proc.returncode) != 0:
        return
    subject = str(proc.stdout or "").strip()
    if subject and required_tag not in subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=subject[:140],
                message="latest baseline commit message must include '{}'".format(required_tag),
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )

    mp_payload, mp_err = _load_json_object(repo_root, MULTIPLAYER_REGRESSION_LOCK_PATH)
    if mp_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="multiplayer regression baseline lock file is missing or invalid",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    for field in MULTIPLAYER_REGRESSION_LOCK_REQUIRED_FIELDS:
        value = mp_payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="multiplayer regression lock missing required field '{}'".format(field),
                    rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                )
            )

    policy_rows = mp_payload.get("policy_baselines")
    if not isinstance(policy_rows, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="policy_baselines",
                message="multiplayer regression lock policy_baselines must be an object",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for policy_id in (
            "policy.net.lockstep",
            "policy.net.server_authoritative",
            "policy.net.srz_hybrid",
        ):
            row = policy_rows.get(policy_id)
            if not isinstance(row, dict):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=policy_id,
                        message="multiplayer regression lock missing policy baseline '{}'".format(policy_id),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )
                continue
            final_hash = str(row.get("final_composite_hash", "")).strip()
            if not final_hash:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=policy_id,
                        message="multiplayer regression lock requires final_composite_hash for '{}'".format(policy_id),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )

    fp_rows = mp_payload.get("anti_cheat_fingerprint_hashes")
    if not isinstance(fp_rows, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="anti_cheat_fingerprint_hashes",
                message="multiplayer regression lock anti_cheat_fingerprint_hashes must be an object",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for key in (
            "detect_only_event_fingerprint_hash",
            "rank_strict_event_fingerprint_hash",
            "rank_strict_action_fingerprint_hash",
        ):
            if not str(fp_rows.get(key, "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=key,
                        message="multiplayer regression lock missing anti-cheat fingerprint hash '{}'".format(key),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )

    mp_update_policy = mp_payload.get("update_policy")
    mp_required_tag = ""
    if isinstance(mp_update_policy, dict):
        mp_required_tag = str(mp_update_policy.get("required_commit_tag", "")).strip()
    if not mp_required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="multiplayer regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    try:
        mp_proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", MULTIPLAYER_REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(mp_proc.returncode) != 0:
        return
    mp_subject = str(mp_proc.stdout or "").strip()
    if mp_subject and mp_required_tag not in mp_subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=mp_subject[:140],
                message="latest multiplayer baseline commit message must include '{}'".format(mp_required_tag),
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )


def _append_cross_system_matrix_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    matrix_abs = os.path.join(repo_root, CONSISTENCY_MATRIX_PATH.replace("/", os.sep))
    if not os.path.isfile(matrix_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=CONSISTENCY_MATRIX_PATH,
                line_number=1,
                snippet="",
                message="cross-system consistency matrix is missing",
                rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
            )
        )
        return
    try:
        content = open(matrix_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONSISTENCY_MATRIX_PATH,
                line_number=1,
                snippet="",
                message="unable to read cross-system consistency matrix",
                rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
            )
        )
        return
    for system_name in CONSISTENCY_MATRIX_REQUIRED_SYSTEMS:
        if str(system_name) not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONSISTENCY_MATRIX_PATH,
                    line_number=1,
                    snippet=str(system_name),
                    message="matrix is missing required system row '{}'".format(system_name),
                    rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
                )
            )
    for column_name in CONSISTENCY_MATRIX_REQUIRED_COLUMNS:
        if str(column_name) not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONSISTENCY_MATRIX_PATH,
                    line_number=1,
                    snippet=str(column_name),
                    message="matrix is missing required responsibility column '{}'".format(column_name),
                    rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
                )
            )


def _append_status_now_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    status_now_abs = os.path.join(repo_root, STATUS_NOW_PATH.replace("/", os.sep))
    if not os.path.isfile(status_now_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=STATUS_NOW_PATH,
                line_number=1,
                snippet="",
                message="status snapshot file is missing",
                rule_id="INV-STATUS-NOW-PRESENT",
            )
        )
        return
    try:
        content = open(status_now_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=STATUS_NOW_PATH,
                line_number=1,
                snippet="",
                message="unable to read status snapshot file",
                rule_id="INV-STATUS-NOW-PRESENT",
            )
        )
        return
    for header in STATUS_NOW_REQUIRED_SECTIONS:
        if header not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=STATUS_NOW_PATH,
                    line_number=1,
                    snippet=header,
                    message="status snapshot missing required section '{}'".format(header),
                    rule_id="INV-STATUS-NOW-PRESENT",
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
        "packs/derived/",
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


def _append_contract_token_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in CONTRACT_TOKEN_ALLOWED_PATH_PREFIXES):
        return
    pattern = r'["\']dom\.contract\.[A-Za-z0-9_.-]+["\']'
    if not re.search(pattern, line):
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded contract token literal detected outside registry-governed paths",
            rule_id="INV-NO-HARDCODED-CONTRACT-TOKENS",
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


def _append_negative_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    io_read_tokens = ("open(", "fopen(", "ifstream", "std::ifstream", "json.load(")
    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()

            if rel_norm.startswith(("engine/", "game/")):
                if ("packs/" in lower or "packs\\" in lower) and any(token in lower for token in io_read_tokens):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="runtime code must not directly read pack files",
                            rule_id="INV-NO-DIRECT-PACK-READS-IN-RUNTIME",
                        )
                    )

            has_schema_token = ("schemas/" in lower) or ("schema/" in lower) or (".schema.json" in lower)
            if has_schema_token and any(token in lower for token in io_read_tokens):
                if not rel_norm.startswith(SCHEMA_READ_ALLOWED_PREFIXES):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="schema file parsing must route through validation layer",
                            rule_id="INV-NO-DIRECT-SCHEMA-PARSE-OUTSIDE-VALIDATION",
                        )
                    )

            if rel_norm.startswith(("client/presentation/", "client/ui/")):
                ui_bypass_tokens = (
                    "boot_session_spec(",
                    "create_session_spec(",
                    "run_intent_script(",
                    "run_process(",
                    "execute_process(",
                )
                if any(token in lower for token in ui_bypass_tokens):
                    if "command_graph" not in lower and "intent" not in lower:
                        findings.append(
                            _finding(
                                severity=severity,
                                file_path=rel_norm,
                                line_number=line_no,
                                snippet=str(line).strip()[:140],
                                message="ui logic invocation must route through command graph/intents",
                                rule_id="INV-UI-COMMAND-GRAPH-ONLY",
                            )
                        )

            if rel_norm.startswith(("tools/launcher/", "tools/setup/", "launcher/", "setup/")):
                if "add_argument(" in lower and re.search(r"--(from-stage|to-stage|stage-id)\b", lower):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="session stage jump arguments are forbidden on launcher/setup surfaces",
                            rule_id="INV-NO-SESSION-PIPELINE-BYPASS",
                        )
                    )

            if not rel_norm.startswith(CONTROL_MUTATION_ALLOWED_PREFIXES):
                control_state_write = re.search(
                    r"state\s*\[\s*[\"'](control_bindings|controller_assemblies)[\"']\s*\]\s*=",
                    str(line),
                )
                control_collection_mutation = re.search(
                    r"\b(control_bindings|controller_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if control_state_write or control_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="control bindings/controller assemblies must mutate only through control processes",
                            rule_id="INV-CONTROL-PROCESSES-ONLY",
                        )
                    )

            if not rel_norm.startswith(BODY_MUTATION_ALLOWED_PREFIXES):
                body_state_write = re.search(
                    r"state\s*\[\s*[\"']body_assemblies[\"']\s*\]\s*=",
                    str(line),
                )
                body_collection_mutation = re.search(
                    r"\bbody_assemblies\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                body_transform_mutation = re.search(
                    r"\bbody\w*\s*\[\s*[\"']transform_mm[\"']\s*\]\s*=",
                    str(line),
                )
                if body_state_write or body_collection_mutation or body_transform_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="body assemblies and body transforms must mutate only through deterministic processes",
                            rule_id="INV-BODY-MUTATION-PROCESS-ONLY",
                        )
                    )

            if not any(rel_norm.startswith(prefix) for prefix in PLAYER_LITERAL_ALLOWED_PATH_PREFIXES):
                if re.search(r"[\"']player(?:\.[a-z0-9_.-]+)?[\"']", lower):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="hardcoded single-player literal detected; control substrate must stay controller-agnostic",
                            rule_id="INV-NO-HARDCODED-PLAYER",
                        )
                    )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="control process runtime is missing; entitlement gate checks cannot be verified",
                rule_id="INV-CONTROL-ENTITLEMENT-GATED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="movement runtime is missing; cannot verify agent_move dispatches through process.body_move_attempt",
                rule_id="INV-MOVE-USES-BODY_MOVE_ATTEMPT",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="movement ownership guards are missing; cannot verify ownership enforcement for embodied movement",
                rule_id="INV-OWNERSHIP-CHECK-REQUIRED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="camera/view runtime is missing; cannot verify registry-driven view mode selection",
                rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="camera/view runtime is missing; cannot verify observer watermark enforcement",
                rule_id="INV-WATERMARK-ENFORCED",
            )
        )
    else:
        required_control_entitlements = (
            ("process.control_bind_camera", "entitlement.control.camera"),
            ("process.control_unbind_camera", "entitlement.control.camera"),
            ("process.control_possess_agent", "entitlement.control.possess"),
            ("process.control_release_agent", "entitlement.control.possess"),
            ("process.control_set_view_lens", "entitlement.control.lens_override"),
        )
        for process_id, entitlement_id in required_control_entitlements:
            if process_id not in process_runtime_text or entitlement_id not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet="{} -> {}".format(process_id, entitlement_id),
                        message="control process entitlement mapping is missing or incomplete",
                        rule_id="INV-CONTROL-ENTITLEMENT-GATED",
                    )
                )
        deterministic_pair_tokens = (
            "def _broadphase_pairs(",
            "for cell_key in sorted(grid.keys()):",
            "return sorted(list(pair_set)",
        )
        for token in deterministic_pair_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="collision broadphase must preserve deterministic pair ordering",
                        rule_id="INV-DETERMINISTIC-PAIR-ORDER",
                    )
                )

        movement_tokens = (
            "elif process_id == \"process.agent_move\":",
            "moved = _apply_body_move_attempt(",
        )
        for token in movement_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="agent movement must route through process.body_move_attempt and avoid direct transform mutation",
                        rule_id="INV-MOVE-USES-BODY_MOVE_ATTEMPT",
                    )
                )

        ownership_tokens = (
            "def _movement_context(",
            "refusal.agent.ownership_violation",
        )
        for token in ownership_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="embodied movement must enforce deterministic ownership checks in multiplayer contexts",
                        rule_id="INV-OWNERSHIP-CHECK-REQUIRED",
                    )
                )

        required_view_tokens = (
            "_view_mode_entries(navigation_indices)",
            "view mode '{}' is not declared in view mode registry",
            "control_policy.allowed_view_modes",
        )
        for token in required_view_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="camera/view validation must resolve view modes from registry payloads and control policy",
                        rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
                    )
                )

        if "refusal.view.watermark_required" not in process_runtime_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet="refusal.view.watermark_required",
                    message="observer truth-capable view modes must enforce watermark entitlement refusal",
                    rule_id="INV-WATERMARK-ENFORCED",
                )
            )

        hardcoded_view_branch = re.compile(
            r"if\s+.*(?:==|!=|in\s*\()\s*[\"']view\.[a-z0-9_.-]+[\"']",
            re.IGNORECASE,
        )
        for line_no, line in _iter_lines(repo_root, process_runtime_rel):
            if hardcoded_view_branch.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded view mode branch detected; resolve view rules through view_mode registry data",
                        rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
                    )
                )

    observation_rel = "tools/xstack/sessionx/observation.py"
    observation_abs = os.path.join(repo_root, observation_rel.replace("/", os.sep))
    try:
        observation_text = open(observation_abs, "r", encoding="utf-8").read()
    except OSError:
        observation_text = ""
    if not observation_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=observation_rel,
                line_number=1,
                snippet="",
                message="observation kernel is missing; cannot verify observer watermark channel enforcement",
                rule_id="INV-WATERMARK-ENFORCED",
            )
        )
    else:
        watermark_tokens = (
            "_observer_watermark_payload(",
            "ch.watermark.observer_mode",
            "refusal.ep.entitlement_missing",
        )
        for token in watermark_tokens:
            if token not in observation_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=observation_rel,
                        line_number=1,
                        snippet=token,
                        message="observer truth view path must emit watermark channel and enforce entitlement checks",
                        rule_id="INV-WATERMARK-ENFORCED",
                    )
                )


def _append_representation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""

    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime is missing; cosmetic process-only representation checks cannot be verified",
                rule_id="INV-NO-COSMETIC-SEMANTICS",
            )
        )
    else:
        required_cosmetic_tokens = (
            "elif process_id == \"process.cosmetic_assign\":",
            "representation_state = _representation_state(policy_context)",
            "skip_state_log = True",
        )
        for token in required_cosmetic_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="cosmetic assignment must remain representation-side and process-driven",
                        rule_id="INV-NO-COSMETIC-SEMANTICS",
                    )
                )

        for line_no, line in _iter_lines(repo_root, process_runtime_rel):
            lower = str(line).lower()
            if "cosmetic" not in lower:
                continue
            if "refusal.cosmetic" in lower:
                continue
            if "representation_state" in lower:
                continue
            if any(token in lower for token in COSMETIC_SEMANTIC_FORBIDDEN_TOKENS):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="cosmetic path must not touch authoritative movement/collision fields",
                        rule_id="INV-NO-COSMETIC-SEMANTICS",
                    )
                )

    truth_render_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
    for rel_path in REPRESENTATION_RENDER_ONLY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="representation render adapter file is missing",
                    rule_id="INV-REPRESENTATION-RENDER-ONLY",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            if truth_render_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="representation/render adapter must not import or reference TruthModel/universe state",
                        rule_id="INV-REPRESENTATION-RENDER-ONLY",
                    )
                )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/", "docs/")):
            continue
        if "representation" not in rel_norm and "render_model.py" not in rel_norm:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "truth_model" in lower or "truthmodel" in lower:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="representation code path references TruthModel symbol",
                        rule_id="INV-REPRESENTATION-RENDER-ONLY",
                    )
                )


def _append_ranked_governance_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    registry_rel = "data/registries/server_profile_registry.json"
    registry_payload, registry_err = _load_json_object(repo_root, registry_rel)
    if registry_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=registry_rel,
                line_number=1,
                snippet="",
                message="server profile registry is missing or invalid JSON",
                rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
            )
        )
    else:
        profile_rows = (((registry_payload.get("record") or {}).get("profiles")) or [])
        if not isinstance(profile_rows, list):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=registry_rel,
                    line_number=1,
                    snippet="",
                    message="server profile registry record.profiles is missing",
                    rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                )
            )
        else:
            ranked_profile = {}
            for row in profile_rows:
                if not isinstance(row, dict):
                    continue
                if str(row.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
                    ranked_profile = dict(row)
                    break
            if not ranked_profile:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=registry_rel,
                        line_number=1,
                        snippet="server.profile.rank_strict",
                        message="ranked server profile is missing",
                        rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                    )
                )
            else:
                securex_policy_id = str(ranked_profile.get("securex_policy_id", "")).strip()
                anti_cheat_policy_id = str(ranked_profile.get("anti_cheat_policy_id", "")).strip()
                if securex_policy_id != "securex.policy.rank_strict":
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=registry_rel,
                            line_number=1,
                            snippet=securex_policy_id,
                            message="ranked server profile must reference securex.policy.rank_strict",
                            rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                        )
                    )
                if anti_cheat_policy_id != "policy.ac.rank_strict":
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=registry_rel,
                            line_number=1,
                            snippet=anti_cheat_policy_id,
                            message="ranked server profile must reference policy.ac.rank_strict",
                            rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                        )
                    )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "ranked_mode" not in lower:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="ranked governance must be data-driven; ranked_mode flags are forbidden",
                    rule_id="INV-NO-RANKED-FLAGS",
                )
            )


def _append_hidden_ban_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    anti_engine_rel = "src/net/anti_cheat/anti_cheat_engine.py"
    anti_engine_abs = os.path.join(repo_root, anti_engine_rel.replace("/", os.sep))
    if not os.path.isfile(anti_engine_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=anti_engine_rel,
                line_number=1,
                snippet="",
                message="anti-cheat engine is missing",
                rule_id="INV-NO-HIDDEN-BAN",
            )
        )
        return
    try:
        anti_engine_text = open(anti_engine_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=anti_engine_rel,
                line_number=1,
                snippet="",
                message="unable to read anti-cheat engine for hidden-ban invariant",
                rule_id="INV-NO-HIDDEN-BAN",
            )
        )
        return

    required_tokens = (
        "anti_cheat_events",
        "anti_cheat_enforcement_actions",
        "_record_refusal_injection(",
        "terminated_peers",
    )
    for token in required_tokens:
        if token not in anti_engine_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=anti_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="anti-cheat termination path must emit event/action/refusal artifacts",
                    rule_id="INV-NO-HIDDEN-BAN",
                )
            )

    termination_paths = (
        "src/net/policies/policy_server_authoritative.py",
        "src/net/srz/shard_coordinator.py",
        "src/net/policies/policy_lockstep.py",
    )
    for rel_path in termination_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            continue
        if "terminate" not in text:
            continue
        if rel_path.endswith("policy_lockstep.py"):
            required = ("refusal_from_decision(",)
        else:
            required = ("_apply_enforcement_result(", "anti_cheat_enforcement_actions")
        for token in required:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="terminate handling must route through explicit anti-cheat enforcement pipeline",
                        rule_id="INV-NO-HIDDEN-BAN",
                    )
                )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith("src/net/"):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "terminated_peers" not in lower:
                continue
            if rel_norm == anti_engine_rel:
                continue
            if '"terminated_peers": []' in lower or "'terminated_peers': []" in lower:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="peer termination must be emitted by anti-cheat engine with policy action log",
                    rule_id="INV-NO-HIDDEN-BAN",
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
            _append_contract_token_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_constraint_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_strict_placeholder_findings(findings, rel_path, line_no, line, token)
            _append_renderer_truth_boundary_findings(findings, rel_path, line_no, line, token)
    _append_session_pipeline_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_multiplayer_contract_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_ranked_governance_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_hidden_ban_invariant_findings(
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
    _append_derived_provenance_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_auditx_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_ci_lane_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_regression_lock_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_cross_system_matrix_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_status_now_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_representation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_negative_invariant_findings(
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
