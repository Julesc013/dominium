#!/usr/bin/env python3
"""Validate the PACKAGE-MOUNT-SLICE-01 contract, fixtures, and proof chain."""

from __future__ import annotations

import argparse
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
INPUT_SCHEMA_REL = Path("contracts/package/package_mount_input.schema.json")
RESULT_SCHEMA_REL = Path("contracts/package/package_mount_result.schema.json")
COMMAND_SURFACE_REL = Path("contracts/command/command_surface.contract.toml")
PACKAGE_LOCK_REL = Path("contracts/package/locks/pack_lock.mvp_default.json")
PROFILE_REGISTRY_REL = Path("contracts/profile/profile.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
TRUST_LEVEL_REGISTRY_REL = Path("contracts/trust/trust_level.registry.json")
EVIDENCE_SCHEMA_REL = Path("contracts/evidence/evidence_packet.schema.json")
PUBLIC_SURFACE_REL = Path("contracts/public_surface/public_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/package/fixtures")

VALID_RESULT_REL = FIXTURE_DIR_REL / "valid_package_mount_result.json"
VALID_INPUT_REL = FIXTURE_DIR_REL / "valid_package_mount_input.json"
VALID_MANIFEST_REL = FIXTURE_DIR_REL / "valid_package_manifest.json"

EXPECTED_SCHEMA_IDS = {
    INPUT_SCHEMA_REL: "dominium.package.mount_plan_input.v1",
    RESULT_SCHEMA_REL: "dominium.package.mount_plan_result.v1",
}
REQUIRED_PUBLIC_SURFACES = {
    "dominium.package.mount.command.v1",
    "dominium.package.mount.schemas.v1",
    "dominium.package.mount.validator.v1",
    "dominium.package_mount.fixture_suite.v1",
}
FORBIDDEN_OVERLAY_BEHAVIORS = {
    "silent_overwrite",
    "implicit_last_wins",
    "ignored",
    "best_effort",
}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")
PATHLIKE_RE = re.compile(r"[/\\]|^[A-Za-z]:|\.(json|toml|py|exe|dll|so|dylib)$", re.IGNORECASE)


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


def is_pathlike(value: str) -> bool:
    return bool(PATHLIKE_RE.search(value))


def valid_id(value: str) -> bool:
    return bool(value and ID_RE.match(value) and not is_pathlike(value))


def rel_exists(repo_root: Path, raw_path: str) -> bool:
    path = Path(raw_path)
    if path.is_absolute():
        return path.exists()
    return (repo_root / path).exists()


def read_registry_ids(repo_root: Path, rel_path: Path, array_key: str, id_key: str) -> set[str]:
    data = load_json(repo_root / rel_path)
    return {
        str(item.get(id_key))
        for item in as_list(data.get(array_key))
        if isinstance(item, dict) and item.get(id_key)
    }


def read_command(repo_root: Path) -> dict[str, Any] | None:
    data = load_toml(repo_root / COMMAND_SURFACE_REL)
    for item in as_list(data.get("command")):
        if isinstance(item, dict) and item.get("id") == COMMAND_ID:
            return item
    return None


def read_known_pack_ids(repo_root: Path) -> set[str]:
    data = load_json(repo_root / PACKAGE_LOCK_REL)
    ids = set(strings(data.get("ordered_pack_ids")))
    for pack in as_list(data.get("ordered_packs")):
        if isinstance(pack, dict) and pack.get("pack_id"):
            ids.add(str(pack["pack_id"]))
        if isinstance(pack, dict):
            for source in as_list(pack.get("source_packs")):
                if isinstance(source, dict) and source.get("pack_id"):
                    ids.add(str(source["pack_id"]))
    return ids


def read_context(repo_root: Path) -> dict[str, set[str]]:
    refusals = read_registry_ids(repo_root, REFUSAL_REGISTRY_REL, "codes", "code")
    return {
        "packs": read_known_pack_ids(repo_root),
        "profiles": read_registry_ids(repo_root, PROFILE_REGISTRY_REL, "profiles", "profile_id"),
        "capabilities": read_registry_ids(repo_root, CAPABILITY_REGISTRY_REL, "capabilities", "capability_id"),
        "diagnostics": read_registry_ids(repo_root, DIAGNOSTIC_REGISTRY_REL, "codes", "code"),
        "refusals": refusals,
        "trust_levels": read_registry_ids(repo_root, TRUST_LEVEL_REGISTRY_REL, "levels", "trust_level"),
    }


def validate_required_files(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    required = [
        INPUT_SCHEMA_REL,
        RESULT_SCHEMA_REL,
        COMMAND_SURFACE_REL,
        PACKAGE_LOCK_REL,
        PROFILE_REGISTRY_REL,
        CAPABILITY_REGISTRY_REL,
        REFUSAL_REGISTRY_REL,
        DIAGNOSTIC_REGISTRY_REL,
        TRUST_LEVEL_REGISTRY_REL,
        EVIDENCE_SCHEMA_REL,
        VALID_INPUT_REL,
        VALID_MANIFEST_REL,
        VALID_RESULT_REL,
    ]
    for rel_path in required:
        path = repo_root / rel_path
        if not path.exists():
            findings.append(finding("error", "missing_required_file", f"missing {rel_path.as_posix()}", rel_path.as_posix()))
            continue
        try:
            if rel_path.suffix == ".toml":
                load_toml(path)
            else:
                load_json(path)
        except Exception as exc:
            findings.append(finding("error", "parse_error", f"{rel_path.as_posix()} does not parse: {exc}", rel_path.as_posix()))
    for rel_path, expected_id in EXPECTED_SCHEMA_IDS.items():
        path = repo_root / rel_path
        if path.exists():
            data = load_json(path)
            if data.get("$id") != expected_id:
                findings.append(finding("error", "schema_bad_id", f"{rel_path.as_posix()} $id must be {expected_id}", rel_path.as_posix()))
    return findings


def validate_command_surface(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    command = read_command(repo_root)
    if command is None:
        return [finding("error", "command_missing", f"{COMMAND_ID} is not registered", COMMAND_SURFACE_REL.as_posix())]
    expected = {
        "kind": "package",
        "input_schema": INPUT_SCHEMA_REL.as_posix(),
        "result_schema": RESULT_SCHEMA_REL.as_posix(),
        "evidence_schema": EVIDENCE_SCHEMA_REL.as_posix(),
        "service_owner": "tools.validators.package",
    }
    for key, value in expected.items():
        if command.get(key) != value:
            findings.append(finding("error", "command_field_mismatch", f"{COMMAND_ID} {key} must be {value}", COMMAND_SURFACE_REL.as_posix()))
    surfaces = set(strings(command.get("surfaces")))
    if not {"cli", "headless", "aide", "test"}.issubset(surfaces):
        findings.append(finding("error", "command_missing_surface", "package mount command must expose cli/headless/aide/test surfaces", COMMAND_SURFACE_REL.as_posix()))
    proof = " ".join(strings(command.get("proof")))
    if "tools/validators/package/check_package_mount_slice.py" not in proof:
        findings.append(finding("error", "command_missing_proof", "package mount command proof must cite the package mount slice validator", COMMAND_SURFACE_REL.as_posix()))
    return findings


def validate_public_surface(repo_root: Path) -> list[dict[str, Any]]:
    if not (repo_root / PUBLIC_SURFACE_REL).exists():
        return []
    data = load_toml(repo_root / PUBLIC_SURFACE_REL)
    ids = {
        str(item.get("id"))
        for item in as_list(data.get("surface"))
        if isinstance(item, dict) and item.get("id")
    }
    missing = sorted(REQUIRED_PUBLIC_SURFACES - ids)
    if missing:
        return [finding("error", "public_surface_missing", f"missing public surface registrations: {', '.join(missing)}", PUBLIC_SURFACE_REL.as_posix())]
    return []


def collect_identity_failures(value: Any, path: str, findings: list[dict[str, Any]], trail: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            next_trail = f"{trail}.{key}"
            if key in {"id", "package_id", "pack_id", "lock_id", "report_id", "composition_plan_id", "composition_decision_id"} and isinstance(item, str):
                if not valid_id(item):
                    findings.append(finding("error", "path_as_identity", f"path-like or invalid identity at {next_trail}: {item}", path))
            collect_identity_failures(item, path, findings, next_trail)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            collect_identity_failures(item, path, findings, f"{trail}[{index}]")


def validate_package_ref(package_ref: dict[str, Any], path: str, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    package_id = str(package_ref.get("id") or package_ref.get("package_id") or "")
    if not valid_id(package_id):
        findings.append(finding("error", "path_as_identity", f"bad package identity: {package_id}", path))
    elif package_id not in ctx["packs"]:
        findings.append(finding("error", "unknown_package_ref", f"unknown package ref: {package_id}", path))
    if package_ref.get("source_ref_is_authority") is not False:
        findings.append(finding("error", "source_ref_is_authority", "source_ref must be evidence only", path))
    return findings


def validate_manifest(data: dict[str, Any], path: str, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    package_id = str(data.get("package_id") or "")
    if package_id not in ctx["packs"]:
        findings.append(finding("error", "unknown_package_ref", f"manifest package_id is not registered in pack lock: {package_id}", path))
    trust_level = str(data.get("trust_level") or "")
    if trust_level not in ctx["trust_levels"]:
        findings.append(finding("error", "unsupported_trust_level", f"unknown trust level: {trust_level}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_support_claim", "package fixture must not claim product support", path))
    for cap in strings(data.get("capabilities_provided")) + strings(data.get("capabilities_required")):
        if cap not in ctx["capabilities"]:
            findings.append(finding("error", "unknown_capability", f"unknown capability: {cap}", path))
    for code in strings(data.get("diagnostic_codes")):
        if code not in ctx["diagnostics"]:
            findings.append(finding("error", "unknown_diagnostic", f"unknown diagnostic: {code}", path))
    for code in strings(data.get("refusal_codes")):
        if code not in ctx["refusals"]:
            findings.append(finding("error", "unknown_refusal", f"unknown refusal: {code}", path))
    return findings


def validate_plan(data: dict[str, Any], path: str, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.composition.plan":
        findings.append(finding("error", "plan_bad_schema", "package mount plan must use dominium.composition.plan", path))
    if data.get("plan_kind") != "package_mount":
        findings.append(finding("error", "plan_bad_kind", "package mount plan_kind must be package_mount", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_support_claim", "package mount plan must not claim support", path))
    for pack in strings(data.get("pack_refs")):
        if pack not in ctx["packs"]:
            findings.append(finding("error", "unknown_package_ref", f"unknown pack_ref: {pack}", path))
    for profile in strings(data.get("profile_refs")):
        if profile not in ctx["profiles"]:
            findings.append(finding("error", "unknown_profile_ref", f"unknown profile_ref: {profile}", path))
    for item in as_list(data.get("capability_requests")):
        if isinstance(item, dict) and item.get("capability_ref") not in ctx["capabilities"]:
            findings.append(finding("error", "unknown_capability", f"unknown capability_ref: {item.get('capability_ref')}", path))
    return findings


def validate_decision(data: dict[str, Any], path: str, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.composition.decision":
        findings.append(finding("error", "decision_bad_schema", "package mount decision must use dominium.composition.decision", path))
    if data.get("status") == "degraded" and not as_list(data.get("fallback_trace")):
        findings.append(finding("error", "degraded_fallback_without_trace", "degraded package mount decision requires fallback_trace", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_support_claim", "package mount decision must not claim support", path))
    for pack in strings(data.get("selected_pack_refs")):
        if pack not in ctx["packs"]:
            findings.append(finding("error", "unknown_package_ref", f"unknown selected_pack_ref: {pack}", path))
    for profile in strings(data.get("selected_profile_refs")):
        if profile not in ctx["profiles"]:
            findings.append(finding("error", "unknown_profile_ref", f"unknown selected_profile_ref: {profile}", path))
    for code in strings(data.get("diagnostic_refs")):
        if code not in ctx["diagnostics"]:
            findings.append(finding("error", "unknown_diagnostic", f"unknown diagnostic_ref: {code}", path))
    for code in strings(data.get("refusal_refs")):
        if code not in ctx["refusals"]:
            findings.append(finding("error", "unknown_refusal", f"unknown refusal_ref: {code}", path))
    return findings


def validate_lock_or_report(data: dict[str, Any], path: str, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("artifact_class") != "derived_evidence":
        findings.append(finding("error", "artifact_not_derived", "lock/report artifact_class must be derived_evidence", path))
    if data.get("source_truth") is not False:
        findings.append(finding("error", "lockfile_source_truth", "lock/report source_truth must be false", path))
    if data.get("support_claim") is True:
        findings.append(finding("error", "fixture_support_claim", "lock/report must not claim support", path))
    for code in strings(data.get("diagnostics")):
        if code not in ctx["diagnostics"]:
            findings.append(finding("error", "unknown_diagnostic", f"unknown diagnostic: {code}", path))
    schema_id = str(data.get("schema_id") or "")
    if schema_id == "dominium.lock.pack_mount":
        for entry in as_list(data.get("entries")):
            if isinstance(entry, dict) and entry.get("pack_ref") not in ctx["packs"]:
                findings.append(finding("error", "unknown_package_ref", f"unknown lock pack_ref: {entry.get('pack_ref')}", path))
        for overlay in as_list(data.get("overlays")):
            if not isinstance(overlay, dict):
                findings.append(finding("error", "overlay_shape", "overlay must be an object", path))
                continue
            behavior = str(overlay.get("conflict_behavior") or overlay.get("conflict_policy") or "")
            if behavior in FORBIDDEN_OVERLAY_BEHAVIORS:
                findings.append(finding("error", "silent_overlay_overwrite", f"forbidden overlay conflict behavior: {behavior}", path))
            if len(strings(overlay.get("contributors"))) > 1 and not behavior:
                findings.append(finding("error", "overlay_conflict_missing_behavior", "overlap requires explicit conflict behavior", path))
    if schema_id == "dominium.report.capability":
        for entry in as_list(data.get("entries")):
            if not isinstance(entry, dict):
                continue
            for cap in strings(entry.get("available")) + strings(entry.get("missing")) + strings(entry.get("degraded")) + strings(entry.get("refused")):
                if cap not in ctx["capabilities"]:
                    findings.append(finding("error", "unknown_capability", f"unknown capability: {cap}", path))
            if strings(entry.get("missing")):
                findings.append(finding("error", "missing_required_capability", "required capability is missing", path))
    if schema_id == "dominium.report.refusal":
        for entry in as_list(data.get("entries")):
            if isinstance(entry, dict) and entry.get("refusal_code") not in ctx["refusals"]:
                findings.append(finding("error", "unknown_refusal", f"unknown refusal_code: {entry.get('refusal_code')}", path))
    if schema_id == "dominium.report.trust":
        for entry in as_list(data.get("entries")):
            if isinstance(entry, dict) and entry.get("trust_level") not in ctx["trust_levels"]:
                findings.append(finding("error", "unsupported_trust_level", f"unknown trust_level: {entry.get('trust_level')}", path))
    return findings


def validate_input(data: dict[str, Any], path: str, repo_root: Path, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.package.mount_plan_input":
        findings.append(finding("error", "input_bad_schema", "input schema_id must be dominium.package.mount_plan_input", path))
    if data.get("command_id") != COMMAND_ID:
        findings.append(finding("error", "input_bad_command", f"input command_id must be {COMMAND_ID}", path))
    package_ref = data.get("target_package_ref")
    if not isinstance(package_ref, dict):
        findings.append(finding("error", "input_missing_package_ref", "target_package_ref must be an object", path))
    else:
        findings.extend(validate_package_ref(package_ref, path, ctx))
        source_ref = str(package_ref.get("source_ref") or "")
        if source_ref and not rel_exists(repo_root, source_ref):
            findings.append(finding("error", "missing_source_ref", f"source_ref does not exist: {source_ref}", path))
    for profile in strings(data.get("requested_profile_refs")):
        if profile not in ctx["profiles"]:
            findings.append(finding("error", "unknown_profile_ref", f"unknown requested profile: {profile}", path))
    for cap in strings(data.get("requested_capability_refs")):
        if cap not in ctx["capabilities"]:
            findings.append(finding("error", "unknown_capability", f"unknown requested capability: {cap}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_support_claim", "input fixture must not claim support", path))
    return findings


def validate_artifact_ref(ref_data: Any, path: str, repo_root: Path, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(ref_data, dict):
        return [finding("error", "artifact_ref_shape", "artifact ref must be an object", path)]
    collect_identity_failures(ref_data, path, findings)
    if ref_data.get("artifact_class") != "derived_evidence" or ref_data.get("source_truth") is not False:
        findings.append(finding("error", "artifact_ref_not_derived", "artifact ref must be derived evidence and source_truth=false", path))
    raw_path = str(ref_data.get("path") or "")
    if not raw_path or not rel_exists(repo_root, raw_path):
        findings.append(finding("error", "artifact_ref_missing_path", f"artifact ref path missing: {raw_path}", path))
        return findings
    data = load_json(repo_root / raw_path)
    if data.get("schema_id") != ref_data.get("schema_id"):
        findings.append(finding("error", "artifact_ref_schema_mismatch", f"artifact ref schema mismatch for {raw_path}", path))
    schema_id = str(data.get("schema_id") or "")
    if schema_id == "dominium.composition.plan":
        findings.extend(validate_plan(data, raw_path, ctx))
    elif schema_id == "dominium.composition.decision":
        findings.extend(validate_decision(data, raw_path, ctx))
    elif schema_id.startswith("dominium.lock.") or schema_id.startswith("dominium.report."):
        findings.extend(validate_lock_or_report(data, raw_path, ctx))
    else:
        findings.append(finding("error", "artifact_ref_unknown_schema", f"unexpected artifact ref schema: {schema_id}", path))
    return findings


def validate_result(data: dict[str, Any], path: str, repo_root: Path, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    collect_identity_failures(data, path, findings)
    if data.get("schema_id") != "dominium.package.mount_plan_result":
        findings.append(finding("error", "result_bad_schema", "result schema_id must be dominium.package.mount_plan_result", path))
    if data.get("command_id") != COMMAND_ID:
        findings.append(finding("error", "result_bad_command", f"result command_id must be {COMMAND_ID}", path))
    if data.get("support_claim") is not False:
        findings.append(finding("error", "fixture_support_claim", "package mount result must not claim support", path))
    for key in ("runtime_mounting_implemented", "package_runtime_implemented", "mod_loader_implemented", "provider_runtime_implemented"):
        if data.get(key) is not False:
            findings.append(finding("error", "runtime_claim", f"{key} must be false", path))
    package_ref = data.get("package_ref")
    if isinstance(package_ref, dict):
        findings.extend(validate_package_ref(package_ref, path, ctx))
    else:
        findings.append(finding("error", "result_missing_package_ref", "package_ref must be an object", path))
    for profile in strings(data.get("profile_refs")):
        if profile not in ctx["profiles"]:
            findings.append(finding("error", "unknown_profile_ref", f"unknown profile_ref: {profile}", path))
    for key in ("composition_plan_ref", "composition_decision_ref", "pack_mount_lock_ref", "capability_report_ref", "refusal_report_ref", "compatibility_report_ref", "trust_report_ref"):
        findings.extend(validate_artifact_ref(data.get(key), f"{path}#{key}", repo_root, ctx))
    for item in as_list(data.get("diagnostics")):
        if isinstance(item, dict) and item.get("code") not in ctx["diagnostics"]:
            findings.append(finding("error", "unknown_diagnostic", f"unknown result diagnostic: {item.get('code')}", path))
    refusal = data.get("refusal")
    if isinstance(refusal, dict) and refusal.get("code") not in ctx["refusals"]:
        findings.append(finding("error", "unknown_refusal", f"unknown result refusal: {refusal.get('code')}", path))
    evidence_ref = data.get("evidence_ref")
    if not isinstance(evidence_ref, dict):
        findings.append(finding("error", "missing_evidence_ref", "result requires evidence_ref", path))
    else:
        if evidence_ref.get("packet_schema") != EVIDENCE_SCHEMA_REL.as_posix():
            findings.append(finding("error", "bad_evidence_schema", "evidence_ref must cite evidence packet schema", path))
        for report_path in strings(evidence_ref.get("report_paths")):
            if not rel_exists(repo_root, report_path):
                findings.append(finding("error", "missing_evidence_report", f"evidence report path missing: {report_path}", path))
    return findings


def canonical_result_bytes(repo_root: Path) -> bytes:
    data = load_json(repo_root / VALID_RESULT_REL)
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def build_mount_result_from_fixture(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / VALID_RESULT_REL)


def validate_valid_chain(repo_root: Path, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    input_data = load_json(repo_root / VALID_INPUT_REL)
    manifest = load_json(repo_root / VALID_MANIFEST_REL)
    result = load_json(repo_root / VALID_RESULT_REL)
    findings.extend(validate_input(input_data, VALID_INPUT_REL.as_posix(), repo_root, ctx))
    findings.extend(validate_manifest(manifest, VALID_MANIFEST_REL.as_posix(), ctx))
    findings.extend(validate_result(result, VALID_RESULT_REL.as_posix(), repo_root, ctx))
    if input_data.get("target_package_ref", {}).get("id") != result.get("package_ref", {}).get("id"):
        findings.append(finding("error", "input_result_package_mismatch", "input and result package refs must match", VALID_RESULT_REL.as_posix()))
    if len(canonical_result_bytes(repo_root)) == 0:
        findings.append(finding("error", "deterministic_serialization_empty", "canonical result serialization is empty", VALID_RESULT_REL.as_posix()))
    return findings


def validate_invalid_case(data: dict[str, Any], path: str, repo_root: Path, ctx: dict[str, set[str]]) -> list[dict[str, Any]]:
    schema_id = str(data.get("schema_id") or "")
    if schema_id == "dominium.package.mount_plan_input":
        return validate_input(data, path, repo_root, ctx)
    if schema_id == "dominium.package.mount_plan_result":
        return validate_result(data, path, repo_root, ctx)
    if schema_id == "dominium.package.fixture.manifest":
        return validate_manifest(data, path, ctx)
    if schema_id == "dominium.composition.plan":
        return validate_plan(data, path, ctx)
    if schema_id == "dominium.composition.decision":
        return validate_decision(data, path, ctx)
    if schema_id.startswith("dominium.lock.") or schema_id.startswith("dominium.report."):
        return validate_lock_or_report(data, path, ctx)
    return [finding("error", "unknown_fixture_schema", f"unknown fixture schema_id: {schema_id}", path)]


def validate_fixtures(repo_root: Path, ctx: dict[str, set[str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings = validate_valid_chain(repo_root, ctx)
    fixture_results: list[dict[str, Any]] = []
    valid_count = 1
    invalid_count = 0
    for path in sorted((repo_root / FIXTURE_DIR_REL).glob("invalid_*.json")):
        invalid_count += 1
        rel_path = rel(path, repo_root)
        data = load_json(path)
        expected = set(strings(data.get("expected_failures")))
        item_findings = validate_invalid_case(data, rel_path, repo_root, ctx)
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
        "status": "pass" if not [item for item in findings if item["level"] == "error"] else "fail",
        "valid_fixtures": valid_count,
        "invalid_fixtures": invalid_count,
        "fixtures": fixture_results,
    }


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> dict[str, Any]:
    findings = validate_required_files(repo_root)
    ctx = read_context(repo_root) if not findings else {"packs": set(), "profiles": set(), "capabilities": set(), "diagnostics": set(), "refusals": set(), "trust_levels": set()}
    if not findings:
        findings.extend(validate_command_surface(repo_root))
        findings.extend(validate_public_surface(repo_root))
    fixtures = {"status": "not_run", "valid_fixtures": 0, "invalid_fixtures": 0, "fixtures": []}
    if include_fixtures and not [item for item in findings if item["level"] == "error"]:
        fixture_findings, fixtures = validate_fixtures(repo_root, ctx)
        findings.extend(fixture_findings)
    inventory = {"status": "not_run"}
    if include_inventory:
        inventory = {
            "status": "warning",
            "note": "Inventory is descriptive only; package runtime mounting is not implemented.",
            "registered": {
                "packs": len(ctx["packs"]),
                "profiles": len(ctx["profiles"]),
                "capabilities": len(ctx["capabilities"]),
                "diagnostics": len(ctx["diagnostics"]),
                "refusals": len(ctx["refusals"]),
                "trust_levels": len(ctx["trust_levels"]),
            },
            "command": COMMAND_ID if read_command(repo_root) else None,
            "fixtures_dir": FIXTURE_DIR_REL.as_posix(),
        }
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_package_mount_slice",
        "status": "pass" if not errors else "fail",
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "command_id": COMMAND_ID,
        "input_schema": INPUT_SCHEMA_REL.as_posix(),
        "result_schema": RESULT_SCHEMA_REL.as_posix(),
        "valid_result": VALID_RESULT_REL.as_posix(),
        "findings": findings,
        "fixtures": fixtures,
        "inventory": inventory,
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"package mount slice: {result['status']}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
    print(f"command: {result['command_id']}")
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
    parser.add_argument("--fixtures", action="store_true", help="Validate package mount fixtures")
    parser.add_argument("--inventory", action="store_true", help="Describe package mount inventory")
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
