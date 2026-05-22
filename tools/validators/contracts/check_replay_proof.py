#!/usr/bin/env python3
"""Validate the REPLAY-PROOF-SLICE-01 command-level replay/proof fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


COMMAND_ID = "dominium.package.mount.plan.v1"
CANONICALIZATION_POLICY = "dominium.canonical_json.sorted_utf8.v1"
HASH_ALGORITHM = "sha256"

COMMAND_SURFACE_REL = Path("contracts/command/command_surface.contract.toml")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
PUBLIC_SURFACE_REL = Path("contracts/public_surface/public_surface.contract.toml")

REPLAY_SCHEMA_RELS = [
    Path("contracts/replay/replay_input.schema.json"),
    Path("contracts/replay/replay_result.schema.json"),
    Path("contracts/replay/replay_event.schema.json"),
    Path("contracts/replay/replay_manifest.schema.json"),
    Path("contracts/replay/replay_verification_result.schema.json"),
    Path("contracts/proof/proof_hash.schema.json"),
    Path("contracts/proof/proof_manifest.schema.json"),
]

FIXTURE_DIR_REL = Path("tests/contract/replay/fixtures")
VALID_INPUT_REL = FIXTURE_DIR_REL / "valid_replay_input_package_mount.json"
VALID_RESULT_REL = FIXTURE_DIR_REL / "valid_replay_expected_result_package_mount.json"
VALID_EVENT_LOG_REL = FIXTURE_DIR_REL / "valid_replay_event_log_package_mount.json"
VALID_PROOF_HASH_REL = FIXTURE_DIR_REL / "valid_proof_hash_package_mount.json"
VALID_PROOF_MANIFEST_REL = FIXTURE_DIR_REL / "valid_proof_manifest_package_mount.json"
VALID_REPLAY_MANIFEST_REL = FIXTURE_DIR_REL / "valid_replay_manifest_package_mount.json"
VALID_VERIFICATION_REL = FIXTURE_DIR_REL / "valid_replay_verification_result_package_mount.json"

EXPECTED_SCHEMA_IDS = {
    "contracts/replay/replay_input.schema.json": "dominium.replay.input.v1",
    "contracts/replay/replay_result.schema.json": "dominium.replay.expected_result.v1",
    "contracts/replay/replay_event.schema.json": "dominium.replay.event_log.v1",
    "contracts/replay/replay_manifest.schema.json": "dominium.replay.manifest.v1",
    "contracts/replay/replay_verification_result.schema.json": "dominium.replay.verification_result.v1",
    "contracts/proof/proof_hash.schema.json": "dominium.proof.hash.v1",
    "contracts/proof/proof_manifest.schema.json": "dominium.proof.manifest.v1",
}

REQUIRED_PUBLIC_SURFACES = {
    "dominium.replay.proof.schemas.v1",
    "dominium.replay.proof.validator.v1",
    "dominium.replay_proof.fixture_suite.v1",
    "dominium.replay.proof.law.v1",
}

REQUIRED_DIAGNOSTICS = {
    "DOM-REPLAY-INPUT-INVALID",
    "DOM-REPLAY-EXPECTED-HASH-MISSING",
    "DOM-REPLAY-HASH-MISMATCH",
    "DOM-REPLAY-COMMAND-UNKNOWN",
    "DOM-REPLAY-UNSUPPORTED-TARGET",
    "DOM-REPLAY-EVIDENCE-MISSING",
    "DOM-REPLAY-NONCANONICAL-INPUT",
    "DOM-REPLAY-FIXTURE-ONLY-NO-RUNTIME-SUPPORT",
}

REQUIRED_REFUSALS = {
    "dominium.refusal.replay.input_invalid",
    "dominium.refusal.replay.expected_hash_missing",
    "dominium.refusal.replay.hash_mismatch",
    "dominium.refusal.replay.command_unknown",
    "dominium.refusal.replay.unsupported_target",
    "dominium.refusal.replay.evidence_missing",
    "dominium.refusal.replay.noncanonical_input",
    "dominium.refusal.replay.fixture_only_no_runtime_support",
}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
PATHLIKE_RE = re.compile(r"[/\\]|^[A-Za-z]:|\.(json|toml|py|exe|dll|so|dylib)$", re.IGNORECASE)
HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out: list[str] = []
    for ch in line:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            out.append(ch)
            continue
        if ch == "#" and not in_quote:
            break
        out.append(ch)
    return "".join(out).strip()


def _split_array_items(raw: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    in_quote = False
    escaped = False
    for ch in raw:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            current.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            current.append(ch)
            continue
        if ch == "," and not in_quote:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue
        current.append(ch)
    item = "".join(current).strip()
    if item:
        items.append(item)
    return items


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item) for item in _split_array_items(inner)]
    try:
        return int(raw)
    except ValueError:
        return raw


def _minimal_toml_load(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current: dict[str, Any] = root
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            current = {}
            root.setdefault(section, []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].strip().split("."):
                current = current.setdefault(part, {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line {lineno}: {original}")
        key, raw_value = line.split("=", 1)
        current[key.strip()] = _parse_value(raw_value)
    return root


def load_toml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def strings(value: Any) -> list[str]:
    return [str(item) for item in as_list(value) if item not in (None, "")]


def finding(level: str, code: str, message: str, path: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def rel(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def rel_exists(repo_root: Path, raw_path: str) -> bool:
    path = Path(raw_path)
    if path.is_absolute():
        return path.exists()
    return (repo_root / path).exists()


def is_pathlike(value: str) -> bool:
    return bool(PATHLIKE_RE.search(value))


def valid_id(value: str) -> bool:
    return bool(value and ID_RE.match(value) and not is_pathlike(value))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_file_hash(repo_root: Path, raw_path: str) -> str:
    return canonical_sha256(load_json(repo_root / raw_path))


def read_command_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    data = load_toml(repo_root / COMMAND_SURFACE_REL)
    return {
        str(item.get("id")): item
        for item in as_list(data.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


def read_diagnostic_codes(repo_root: Path) -> set[str]:
    data = load_json(repo_root / DIAGNOSTIC_REGISTRY_REL)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def read_refusal_codes(repo_root: Path) -> set[str]:
    data = load_json(repo_root / REFUSAL_REGISTRY_REL)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def read_public_surface_ids(repo_root: Path) -> set[str]:
    data = load_toml(repo_root / PUBLIC_SURFACE_REL)
    return {
        str(item.get("id"))
        for item in as_list(data.get("surface"))
        if isinstance(item, dict) and item.get("id")
    }


def collect_identity_failures(value: Any, path: str, findings: list[dict[str, Any]], trail: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            next_trail = f"{trail}.{key}"
            if key.endswith("_id") or key in {"replay_id", "proof_id", "hash_id", "verification_id", "event_log_id", "expected_result_id"}:
                if isinstance(item, str) and not valid_id(item):
                    findings.append(finding("error", "path_as_identity", f"path-like or invalid identity at {next_trail}: {item}", path))
            collect_identity_failures(item, path, findings, next_trail)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            collect_identity_failures(item, path, findings, f"{trail}[{index}]")


def check_source_refs(repo_root: Path, refs: Any, path: str, findings: list[dict[str, Any]]) -> None:
    for raw_path in strings(refs):
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "source_ref_missing", f"source ref does not exist: {raw_path}", path))


def check_hash(value: str, path: str, findings: list[dict[str, Any]], code: str = "replay_expected_hash_missing") -> None:
    if not value or not HASH_RE.match(value):
        findings.append(finding("error", code, f"invalid or missing sha256 hash: {value}", path))


def validate_registry_surfaces(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for schema_rel in REPLAY_SCHEMA_RELS:
        path = repo_root / schema_rel
        if not path.exists():
            findings.append(finding("error", "missing_replay_schema", f"missing schema: {schema_rel.as_posix()}", schema_rel.as_posix()))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "schema_parse_error", f"{schema_rel.as_posix()} does not parse: {exc}", schema_rel.as_posix()))
            continue
        expected_id = EXPECTED_SCHEMA_IDS[schema_rel.as_posix()]
        if data.get("$id") != expected_id:
            findings.append(finding("error", "schema_bad_id", f"{schema_rel.as_posix()} $id must be {expected_id}", schema_rel.as_posix()))
    command_map = read_command_map(repo_root)
    if COMMAND_ID not in command_map:
        findings.append(finding("error", "replay_command_unknown", f"target command is not registered: {COMMAND_ID}", COMMAND_SURFACE_REL.as_posix()))
    diagnostic_codes = read_diagnostic_codes(repo_root)
    missing_diags = sorted(REQUIRED_DIAGNOSTICS - diagnostic_codes)
    if missing_diags:
        findings.append(finding("error", "replay_diagnostics_missing", f"missing replay diagnostics: {', '.join(missing_diags)}", DIAGNOSTIC_REGISTRY_REL.as_posix()))
    refusal_codes = read_refusal_codes(repo_root)
    missing_refusals = sorted(REQUIRED_REFUSALS - refusal_codes)
    if missing_refusals:
        findings.append(finding("error", "replay_refusals_missing", f"missing replay refusals: {', '.join(missing_refusals)}", REFUSAL_REGISTRY_REL.as_posix()))
    surface_ids = read_public_surface_ids(repo_root)
    missing_surfaces = sorted(REQUIRED_PUBLIC_SURFACES - surface_ids)
    if missing_surfaces:
        findings.append(finding("error", "replay_public_surfaces_missing", f"missing public surfaces: {', '.join(missing_surfaces)}", PUBLIC_SURFACE_REL.as_posix()))
    return findings


def validate_replay_input(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.replay.input":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.replay.input", path))
    command_ref = str(data.get("command_ref") or "")
    command = command_map.get(command_ref)
    if command is None:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {command_ref}", path))
    elif data.get("input_schema_ref") != command.get("input_schema"):
        findings.append(finding("error", "replay_input_invalid", "input_schema_ref does not match command input_schema", path))
    input_ref = str(data.get("input_ref") or "")
    if not rel_exists(repo_root, input_ref):
        findings.append(finding("error", "replay_input_invalid", f"input_ref missing: {input_ref}", path))
    else:
        actual_hash = canonical_file_hash(repo_root, input_ref)
        if data.get("input_hash") != actual_hash:
            findings.append(finding("error", "replay_input_invalid", f"input_hash mismatch; expected {actual_hash}", path))
    if data.get("canonicalization_policy_ref") != CANONICALIZATION_POLICY:
        findings.append(finding("error", "replay_noncanonical_input", "canonicalization_policy_ref must be sorted UTF-8 canonical JSON", path))
    if data.get("hash_algorithm") != HASH_ALGORITHM:
        findings.append(finding("error", "replay_input_invalid", "hash_algorithm must be sha256", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "replay input fixture must not claim support", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_expected_result(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]], diagnostics: set[str], refusals: set[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.replay.expected_result":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.replay.expected_result", path))
    command_ref = str(data.get("command_ref") or "")
    command = command_map.get(command_ref)
    if command is None:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {command_ref}", path))
    elif data.get("result_schema_ref") != command.get("result_schema"):
        findings.append(finding("error", "result_schema_mismatch", "result_schema_ref does not match command result_schema", path))
    result_ref = str(data.get("result_ref") or "")
    if not rel_exists(repo_root, result_ref):
        findings.append(finding("error", "replay_input_invalid", f"result_ref missing: {result_ref}", path))
    else:
        actual_hash = canonical_file_hash(repo_root, result_ref)
        if data.get("result_hash") != actual_hash:
            findings.append(finding("error", "replay_hash_mismatch", f"result_hash mismatch; expected {actual_hash}", path))
    for diagnostic in strings(data.get("expected_diagnostic_refs")):
        if diagnostic not in diagnostics:
            findings.append(finding("error", "replay_input_invalid", f"unknown diagnostic ref: {diagnostic}", path))
    for refusal in strings(data.get("expected_refusal_refs")):
        if refusal not in refusals:
            findings.append(finding("error", "replay_input_invalid", f"unknown refusal ref: {refusal}", path))
    for evidence in strings(data.get("evidence_refs")):
        if not rel_exists(repo_root, evidence):
            findings.append(finding("error", "replay_evidence_missing", f"evidence ref missing: {evidence}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "expected result fixture must not claim support", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_event_log(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.replay.event_log":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.replay.event_log", path))
    events = [item for item in as_list(data.get("events")) if isinstance(item, dict)]
    sequences = [int(item.get("sequence", -1)) for item in events]
    if sequences != sorted(sequences):
        findings.append(finding("error", "replay_input_invalid", "events must be sorted by sequence", path))
    for event in events:
        command_ref = str(event.get("command_ref") or "")
        if command_ref not in command_map:
            findings.append(finding("error", "replay_command_unknown", f"unknown event command_ref: {command_ref}", path))
        for evidence in strings(event.get("evidence_refs")):
            if not rel_exists(repo_root, evidence):
                findings.append(finding("error", "replay_evidence_missing", f"event evidence ref missing: {evidence}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "event log fixture must not claim support", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def proof_material_hash(repo_root: Path, proof_hash_data: dict[str, Any]) -> str:
    material: list[dict[str, str]] = []
    for ref_data in as_list(proof_hash_data.get("material_refs")):
        if not isinstance(ref_data, dict):
            continue
        raw_path = str(ref_data.get("path") or "")
        material.append(
            {
                "role": str(ref_data.get("role") or ""),
                "path": raw_path,
                "sha256": canonical_file_hash(repo_root, raw_path) if raw_path and rel_exists(repo_root, raw_path) else "",
            }
        )
    payload = {
        "canonicalization_policy_ref": proof_hash_data.get("canonicalization_policy_ref"),
        "command_ref": proof_hash_data.get("command_ref"),
        "hash_algorithm": proof_hash_data.get("hash_algorithm"),
        "material_refs": material,
    }
    return canonical_sha256(payload)


def validate_proof_hash(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.proof.hash":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.proof.hash", path))
    if data.get("command_ref") not in command_map:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {data.get('command_ref')}", path))
    if data.get("canonicalization_policy_ref") != CANONICALIZATION_POLICY:
        findings.append(finding("error", "replay_noncanonical_input", "proof hash must use sorted UTF-8 canonical JSON", path))
    for ref_data in as_list(data.get("material_refs")):
        if not isinstance(ref_data, dict):
            findings.append(finding("error", "replay_input_invalid", "material refs must be objects", path))
            continue
        raw_path = str(ref_data.get("path") or "")
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "replay_evidence_missing", f"material ref missing: {raw_path}", path))
    check_hash(str(data.get("value") or ""), path, findings)
    if not any(item["level"] == "error" for item in findings):
        actual = proof_material_hash(repo_root, data)
        if data.get("value") != actual:
            findings.append(finding("error", "replay_hash_mismatch", f"proof hash mismatch; expected {actual}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "proof hash must not claim support", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_proof_manifest(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.proof.manifest":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.proof.manifest", path))
    if data.get("command_ref") not in command_map:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {data.get('command_ref')}", path))
    if data.get("target_scope") != "command_result_fixture":
        findings.append(finding("error", "replay_unsupported_target", "proof target_scope must remain command_result_fixture", path))
    if not strings(data.get("evidence_refs")):
        findings.append(finding("error", "replay_evidence_missing", "proof manifest requires evidence_refs", path))
    for key in ("input_ref", "expected_result_ref", "event_log_ref", "proof_hash_ref"):
        raw_path = str(data.get(key) or "")
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "replay_evidence_missing", f"{key} missing: {raw_path}", path))
    for raw_path in strings(data.get("evidence_refs")) + strings(data.get("artifact_refs")):
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "replay_evidence_missing", f"proof referenced path missing: {raw_path}", path))
    proof_hash_ref = str(data.get("proof_hash_ref") or "")
    if rel_exists(repo_root, proof_hash_ref):
        proof_hash = load_json(repo_root / proof_hash_ref)
        if data.get("expected_hash") != proof_hash.get("value"):
            findings.append(finding("error", "replay_hash_mismatch", "proof manifest expected_hash does not match proof hash value", path))
    check_hash(str(data.get("expected_hash") or ""), path, findings)
    if data.get("support_claim") is not False or data.get("replay_runtime_implemented") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "fixture proof must not claim runtime support", path))
    for key in ("world_replay_implemented", "save_replay_implemented", "gameplay_replay_implemented"):
        if data.get(key) is not False:
            findings.append(finding("error", "replay_unsupported_target", f"{key} must remain false", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_replay_manifest(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.replay.manifest":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.replay.manifest", path))
    if data.get("command_ref") not in command_map:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {data.get('command_ref')}", path))
    for key in ("input_ref", "expected_result_ref", "event_log_ref", "proof_manifest_ref"):
        raw_path = str(data.get(key) or "")
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "replay_evidence_missing", f"{key} missing: {raw_path}", path))
    proof_manifest_ref = str(data.get("proof_manifest_ref") or "")
    if rel_exists(repo_root, proof_manifest_ref):
        proof_manifest = load_json(repo_root / proof_manifest_ref)
        if data.get("expected_hash") != proof_manifest.get("expected_hash"):
            findings.append(finding("error", "replay_hash_mismatch", "replay manifest expected_hash does not match proof manifest", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "replay manifest must not claim support", path))
    for key in ("world_replay_implemented", "save_replay_implemented", "gameplay_replay_implemented"):
        if data.get(key) is not False:
            findings.append(finding("error", "replay_unsupported_target", f"{key} must remain false", path))
    check_hash(str(data.get("expected_hash") or ""), path, findings)
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_verification_result(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.replay.verification_result":
        findings.append(finding("error", "replay_input_invalid", "schema_id must be dominium.replay.verification_result", path))
    if data.get("command_ref") not in command_map:
        findings.append(finding("error", "replay_command_unknown", f"unknown command_ref: {data.get('command_ref')}", path))
    expected_hash = str(data.get("expected_hash") or "")
    observed_hash = str(data.get("observed_hash") or "")
    check_hash(expected_hash, path, findings)
    check_hash(observed_hash, path, findings)
    if expected_hash and observed_hash and expected_hash != observed_hash:
        findings.append(finding("error", "replay_hash_mismatch", "verification expected_hash and observed_hash differ", path))
    if data.get("status") == "pass" and data.get("refusal") not in (None, {}):
        findings.append(finding("error", "replay_input_invalid", "passing verification must not include refusal", path))
    for raw_path in strings(data.get("evidence_refs")):
        if not rel_exists(repo_root, raw_path):
            findings.append(finding("error", "replay_evidence_missing", f"verification evidence ref missing: {raw_path}", path))
    if data.get("support_claim") is not False or data.get("runtime_replay_implemented") is not False:
        findings.append(finding("error", "fixture_only_runtime_claim", "verification result must not claim runtime replay support", path))
    check_source_refs(repo_root, data.get("source_refs"), path, findings)
    return findings


def validate_by_schema(data: dict[str, Any], path: str, repo_root: Path, command_map: dict[str, dict[str, Any]], diagnostics: set[str], refusals: set[str]) -> list[dict[str, Any]]:
    schema_id = str(data.get("schema_id") or "")
    if schema_id == "dominium.replay.input":
        return validate_replay_input(data, path, repo_root, command_map)
    if schema_id == "dominium.replay.expected_result":
        return validate_expected_result(data, path, repo_root, command_map, diagnostics, refusals)
    if schema_id == "dominium.replay.event_log":
        return validate_event_log(data, path, repo_root, command_map)
    if schema_id == "dominium.proof.hash":
        return validate_proof_hash(data, path, repo_root, command_map)
    if schema_id == "dominium.proof.manifest":
        return validate_proof_manifest(data, path, repo_root, command_map)
    if schema_id == "dominium.replay.manifest":
        return validate_replay_manifest(data, path, repo_root, command_map)
    if schema_id == "dominium.replay.verification_result":
        return validate_verification_result(data, path, repo_root, command_map)
    return [finding("error", "replay_input_invalid", f"unknown replay/proof schema_id: {schema_id}", path)]


def validate_positive_chain(repo_root: Path, command_map: dict[str, dict[str, Any]], diagnostics: set[str], refusals: set[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel_path in (
        VALID_INPUT_REL,
        VALID_RESULT_REL,
        VALID_EVENT_LOG_REL,
        VALID_PROOF_HASH_REL,
        VALID_PROOF_MANIFEST_REL,
        VALID_REPLAY_MANIFEST_REL,
        VALID_VERIFICATION_REL,
    ):
        data = load_json(repo_root / rel_path)
        findings.extend(validate_by_schema(data, rel_path.as_posix(), repo_root, command_map, diagnostics, refusals))
    proof_hash = load_json(repo_root / VALID_PROOF_HASH_REL)
    proof_manifest = load_json(repo_root / VALID_PROOF_MANIFEST_REL)
    replay_manifest = load_json(repo_root / VALID_REPLAY_MANIFEST_REL)
    verification = load_json(repo_root / VALID_VERIFICATION_REL)
    if proof_hash.get("value") != proof_manifest.get("expected_hash"):
        findings.append(finding("error", "replay_hash_mismatch", "proof hash and proof manifest differ", VALID_PROOF_MANIFEST_REL.as_posix()))
    if proof_hash.get("value") != replay_manifest.get("expected_hash"):
        findings.append(finding("error", "replay_hash_mismatch", "proof hash and replay manifest differ", VALID_REPLAY_MANIFEST_REL.as_posix()))
    if proof_hash.get("value") != verification.get("expected_hash") or proof_hash.get("value") != verification.get("observed_hash"):
        findings.append(finding("error", "replay_hash_mismatch", "proof hash and verification result differ", VALID_VERIFICATION_REL.as_posix()))
    return findings


def validate_invalid_fixtures(repo_root: Path, command_map: dict[str, dict[str, Any]], diagnostics: set[str], refusals: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    fixture_results: list[dict[str, Any]] = []
    for path in sorted((repo_root / FIXTURE_DIR_REL).glob("invalid_*.json")):
        rel_path = rel(path, repo_root)
        data = load_json(path)
        expected = set(strings(data.get("expected_failures")))
        item_findings = validate_by_schema(data, rel_path, repo_root, command_map, diagnostics, refusals)
        observed = {str(item.get("code")) for item in item_findings if item.get("level") == "error"}
        missing = sorted(expected - observed)
        status = "pass" if expected and not missing else "fail"
        if status != "pass":
            findings.append(finding("error", "invalid_fixture_expectation_failed", f"{rel_path} missing expected failures: {', '.join(missing) or 'none declared'}", rel_path))
        fixture_results.append(
            {
                "path": rel_path,
                "expected_failures": sorted(expected),
                "observed_failures": sorted(observed),
                "status": status,
            }
        )
    return findings, {
        "status": "pass" if not findings else "fail",
        "valid_fixtures": 7,
        "invalid_fixtures": len(fixture_results),
        "fixtures": fixture_results,
    }


def validate_fixtures(repo_root: Path, command_map: dict[str, dict[str, Any]], diagnostics: set[str], refusals: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings = validate_positive_chain(repo_root, command_map, diagnostics, refusals)
    invalid_findings, invalid_summary = validate_invalid_fixtures(repo_root, command_map, diagnostics, refusals)
    findings.extend(invalid_findings)
    invalid_summary["status"] = "pass" if not [item for item in findings if item["level"] == "error"] else "fail"
    return findings, invalid_summary


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> dict[str, Any]:
    findings = validate_registry_surfaces(repo_root)
    command_map = read_command_map(repo_root) if not [item for item in findings if item["level"] == "error"] else {}
    diagnostics = read_diagnostic_codes(repo_root) if not [item for item in findings if item["level"] == "error"] else set()
    refusals = read_refusal_codes(repo_root) if not [item for item in findings if item["level"] == "error"] else set()
    fixture_summary: dict[str, Any] = {"status": "not_run", "valid_fixtures": 0, "invalid_fixtures": 0, "fixtures": []}
    if include_fixtures and not [item for item in findings if item["level"] == "error"]:
        fixture_findings, fixture_summary = validate_fixtures(repo_root, command_map, diagnostics, refusals)
        findings.extend(fixture_findings)
    inventory: dict[str, Any] = {"status": "not_run"}
    if include_inventory:
        inventory = {
            "status": "warning",
            "note": "Inventory is descriptive only; replay/proof runtime is not implemented.",
            "target_command": COMMAND_ID,
            "fixtures_dir": FIXTURE_DIR_REL.as_posix(),
            "schemas": [item.as_posix() for item in REPLAY_SCHEMA_RELS],
            "runtime_replay_implemented": False,
            "world_replay_implemented": False,
            "save_replay_implemented": False,
            "gameplay_replay_implemented": False,
        }
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_replay_proof",
        "status": "pass" if not errors else "fail",
        "target_command": COMMAND_ID,
        "canonicalization_policy": CANONICALIZATION_POLICY,
        "schemas": [item.as_posix() for item in REPLAY_SCHEMA_RELS],
        "fixtures": fixture_summary,
        "inventory": inventory,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "findings": findings,
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"replay proof slice: {result['status']}")
    print(f"target_command: {result['target_command']}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
    fixtures = result.get("fixtures", {})
    if fixtures.get("status") != "not_run":
        print(f"fixtures: {fixtures.get('status')} valid={fixtures.get('valid_fixtures')} invalid={fixtures.get('invalid_fixtures')}")
    inventory = result.get("inventory", {})
    if inventory.get("status") != "not_run":
        print(f"inventory: {inventory.get('status')}")
    for item in result.get("findings", []):
        location = f" [{item.get('path')}]" if item.get("path") else ""
        print(f"{item['level']}: {item['code']}{location}: {item['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on validation errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fixtures", action="store_true", help="Validate replay/proof fixtures")
    parser.add_argument("--inventory", action="store_true", help="Describe replay/proof inventory")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    result = validate_all(
        repo_root,
        include_fixtures=args.strict or args.fixtures,
        include_inventory=args.inventory,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
