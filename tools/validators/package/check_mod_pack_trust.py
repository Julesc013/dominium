#!/usr/bin/env python3
"""Validate Dominium mod/pack trust contracts, registries, and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - Python 3.8 fallback
    tomllib = None


TRUST_CONTRACT_REL = Path("contracts/trust/mod_pack_trust.contract.toml")
TRUST_LEVEL_REGISTRY_REL = Path("contracts/trust/trust_level.registry.json")
PERMISSION_KIND_REGISTRY_REL = Path("contracts/trust/permission_kind.registry.json")
TRUST_DECISION_SCHEMA_REL = Path("contracts/trust/trust_decision.schema.json")
REVIEW_POLICY_REL = Path("contracts/trust/review_policy.contract.toml")
SANDBOX_POLICY_REL = Path("contracts/trust/sandbox_policy.contract.toml")
DETERMINISM_POLICY_REL = Path("contracts/trust/determinism_impact_policy.contract.toml")
NATIVE_PROVIDER_POLICY_REL = Path("contracts/trust/native_provider_policy.contract.toml")
EXTERNAL_ADAPTER_POLICY_REL = Path("contracts/trust/external_adapter_policy.contract.toml")
MOD_DESCRIPTOR_SCHEMA_REL = Path("contracts/modding/mod_descriptor.schema.json")
MOD_CAPABILITY_POLICY_REL = Path("contracts/modding/mod_capability_policy.contract.toml")
PACK_OVERLAY_POLICY_REL = Path("contracts/modding/pack_overlay_policy.contract.toml")
MOD_LIFECYCLE_REGISTRY_REL = Path("contracts/modding/mod_lifecycle.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/mod_pack_trust/fixtures")

JSON_RELS = [
    TRUST_LEVEL_REGISTRY_REL,
    PERMISSION_KIND_REGISTRY_REL,
    TRUST_DECISION_SCHEMA_REL,
    MOD_DESCRIPTOR_SCHEMA_REL,
    MOD_LIFECYCLE_REGISTRY_REL,
]
TOML_RELS = [
    TRUST_CONTRACT_REL,
    REVIEW_POLICY_REL,
    SANDBOX_POLICY_REL,
    DETERMINISM_POLICY_REL,
    NATIVE_PROVIDER_POLICY_REL,
    EXTERNAL_ADAPTER_POLICY_REL,
    MOD_CAPABILITY_POLICY_REL,
    PACK_OVERLAY_POLICY_REL,
]
EXPECTED_CONTRACT_IDS = {
    TRUST_CONTRACT_REL: "dominium.mod_pack.trust_model.v1",
    REVIEW_POLICY_REL: "dominium.mod_pack.review_policy.v1",
    SANDBOX_POLICY_REL: "dominium.mod_pack.sandbox_policy.v1",
    DETERMINISM_POLICY_REL: "dominium.mod_pack.determinism_impact_policy.v1",
    NATIVE_PROVIDER_POLICY_REL: "dominium.mod_pack.native_provider_policy.v1",
    EXTERNAL_ADAPTER_POLICY_REL: "dominium.mod_pack.external_adapter_policy.v1",
    MOD_CAPABILITY_POLICY_REL: "dominium.mod_pack.capability_policy.v1",
    PACK_OVERLAY_POLICY_REL: "dominium.mod_pack.overlay_policy.v1",
}
REQUIRED_TRUST_LEVELS = {
    "data_only",
    "schema_validated",
    "scriptless_rule_data_pack",
    "workbench_authored_module",
    "external_process_adapter",
    "trusted_native_provider",
    "signed_native_provider",
}
REQUIRED_PERMISSIONS = {
    "read_pack_data",
    "write_profile",
    "write_save",
    "write_cache",
    "read_user_file",
    "write_user_file",
    "network_client",
    "network_server",
    "spawn_process",
    "native_code",
    "load_dynamic_library",
    "access_clipboard",
    "access_input",
    "access_audio",
    "access_renderer",
    "invoke_command",
    "provide_command",
    "provide_provider",
    "provide_module",
    "modify_registry",
    "modify_world_state",
    "generate_artifact",
}
REQUIRED_LIFECYCLE_STATES = {
    "draft",
    "local",
    "validated",
    "reviewed",
    "trusted",
    "signed",
    "deprecated",
    "retired",
    "blocked",
    "quarantined",
    "historical",
}
REQUIRED_PUBLIC_SURFACES = {
    "dominium.mod_pack.trust_model.v1",
    "dominium.mod_pack.trust_level.registry.v1",
    "dominium.mod_pack.permission.registry.v1",
    "dominium.mod_pack.mod_descriptor.v1",
    "dominium.mod_pack.overlay_policy.v1",
    "dominium.mod_pack.trust_validator.v1",
}
REQUIRED_DIAGNOSTICS = {
    "DOM-MOD-TRUST-INSUFFICIENT",
    "DOM-MOD-PERMISSION-UNDECLARED",
    "DOM-MOD-NATIVE-PROVIDER-BLOCKED",
    "DOM-MOD-EXTERNAL-ADAPTER-BLOCKED",
    "DOM-MOD-DETERMINISM-IMPACT-MISSING",
    "DOM-PACK-OVERLAY-CONFLICT",
    "DOM-PACK-SILENT-OVERWRITE-FORBIDDEN",
    "DOM-PACK-TRUST-LEVEL-UNKNOWN",
    "DOM-MOD-NETWORK-PERMISSION-DENIED",
    "DOM-MOD-FILESYSTEM-PERMISSION-DENIED",
}
REQUIRED_REFUSALS = {
    "dominium.refusal.mod.trust_insufficient",
    "dominium.refusal.mod.permission_undeclared",
    "dominium.refusal.mod.native_provider_blocked",
    "dominium.refusal.mod.external_adapter_blocked",
    "dominium.refusal.mod.determinism_impact_missing",
    "dominium.refusal.pack.overlay_conflict",
    "dominium.refusal.pack.silent_overwrite_forbidden",
    "dominium.refusal.mod.network_denied",
    "dominium.refusal.mod.filesystem_denied",
}
OPTIONAL_CAPABILITIES = {
    "dominium.mod.data_only",
    "dominium.mod.schema_validated",
    "dominium.mod.scriptless_rule_data",
    "dominium.mod.workbench_authored_module",
    "dominium.mod.external_process_adapter",
    "dominium.mod.trusted_native_provider",
    "dominium.mod.signed_native_provider",
    "dominium.pack.overlay",
    "dominium.pack.bundle",
}
MOD_ID_RE = re.compile(r"^(domino|dominium|org|pack|workspace|blueprints|specs|constraints|policy)(\.[a-z0-9][a-z0-9_-]*)+$")
PATH_LIKE_RE = re.compile(r"[/\\]|(^|\\.)\\.($|\\.)")
FILESYSTEM_PERMISSIONS = {"write_profile", "write_save", "write_cache", "read_user_file", "write_user_file"}
NETWORK_PERMISSIONS = {"network_client", "network_server"}
PROCESS_PERMISSIONS = {"spawn_process"}
NATIVE_PERMISSIONS = {"native_code", "load_dynamic_library"}
DATA_ONLY_ALLOWED = {"read_pack_data"}
FORBIDDEN_OVERLAY_POLICIES = {"silent_overwrite", "implicit_last_wins"}


class CheckResult:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out: List[str] = []
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


def _split_array_items(raw: str) -> List[str]:
    items: List[str] = []
    current: List[str] = []
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
    return raw


def _parse_toml_fallback(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current: Dict[str, Any] = data
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            items = data.setdefault(section, [])
            if not isinstance(items, list):
                raise ValueError("mixed scalar and array section: %s" % section)
            item: Dict[str, Any] = {}
            items.append(item)
            current = item
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = data.setdefault(section, {})
            if not isinstance(current, dict):
                raise ValueError("mixed array and table section: %s" % section)
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        current[key.strip()] = _parse_value(value)
    return data


def load_toml(path: Path) -> Dict[str, Any]:
    if tomllib is not None:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    return _parse_toml_fallback(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def validate_required_files(repo_root: Path, result: CheckResult) -> None:
    for path_rel in JSON_RELS + TOML_RELS:
        path = repo_root / path_rel
        if not path.exists():
            result.error("missing required file: %s" % path_rel.as_posix())
            continue
        try:
            if path_rel in JSON_RELS:
                load_json(path)
            else:
                load_toml(path)
        except Exception as exc:
            result.error("cannot parse %s: %s" % (path_rel.as_posix(), exc))


def validate_contract_ids(repo_root: Path, result: CheckResult) -> None:
    for path_rel, expected_id in EXPECTED_CONTRACT_IDS.items():
        path = repo_root / path_rel
        if not path.exists():
            continue
        try:
            data = load_toml(path)
        except Exception as exc:
            result.error("cannot inspect contract id in %s: %s" % (path_rel.as_posix(), exc))
            continue
        contract = data.get("contract")
        found = contract.get("id") if isinstance(contract, dict) else data.get("id")
        if found != expected_id:
            result.error("%s contract id %r != %r" % (path_rel.as_posix(), found, expected_id))


def trust_levels(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    data = load_json(repo_root / TRUST_LEVEL_REGISTRY_REL)
    levels: Dict[str, Dict[str, Any]] = {}
    for item in data.get("levels", []):
        if isinstance(item, dict) and isinstance(item.get("trust_level"), str):
            levels[item["trust_level"]] = item
    return levels


def permission_kinds(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    data = load_json(repo_root / PERMISSION_KIND_REGISTRY_REL)
    permissions: Dict[str, Dict[str, Any]] = {}
    for item in data.get("permission_kinds", []):
        if isinstance(item, dict) and isinstance(item.get("permission"), str):
            permissions[item["permission"]] = item
    return permissions


def diagnostic_codes(repo_root: Path) -> Optional[Set[str]]:
    path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if not path.exists():
        return None
    data = load_json(path)
    return {item.get("code") for item in data.get("codes", []) if isinstance(item, dict) and item.get("code")}


def refusal_codes(repo_root: Path) -> Optional[Set[str]]:
    path = repo_root / REFUSAL_REGISTRY_REL
    if not path.exists():
        return None
    data = load_json(path)
    return {item.get("refusal_id") for item in data.get("codes", []) if isinstance(item, dict) and item.get("refusal_id")}


def capability_ids(repo_root: Path) -> Optional[Set[str]]:
    path = repo_root / CAPABILITY_REGISTRY_REL
    if not path.exists():
        return None
    data = load_json(path)
    return {item.get("capability_id") for item in data.get("capabilities", []) if isinstance(item, dict) and item.get("capability_id")}


def public_surface_ids(repo_root: Path) -> Optional[Set[str]]:
    path = repo_root / PUBLIC_SURFACE_REGISTRY_REL
    if not path.exists():
        return None
    data = load_toml(path)
    surfaces = data.get("surface", [])
    ids: Set[str] = set()
    if isinstance(surfaces, list):
        for item in surfaces:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.add(item["id"])
    return ids


def validate_registries(repo_root: Path, result: CheckResult) -> None:
    levels = set(trust_levels(repo_root))
    missing_levels = sorted(REQUIRED_TRUST_LEVELS - levels)
    if missing_levels:
        result.error("missing trust levels: %s" % ", ".join(missing_levels))
    permissions = set(permission_kinds(repo_root))
    missing_permissions = sorted(REQUIRED_PERMISSIONS - permissions)
    if missing_permissions:
        result.error("missing permission kinds: %s" % ", ".join(missing_permissions))
    lifecycle = load_json(repo_root / MOD_LIFECYCLE_REGISTRY_REL)
    states = {item.get("state") for item in lifecycle.get("states", []) if isinstance(item, dict)}
    missing_states = sorted(REQUIRED_LIFECYCLE_STATES - states)
    if missing_states:
        result.error("missing mod lifecycle states: %s" % ", ".join(missing_states))
    surfaces = public_surface_ids(repo_root)
    if surfaces is None:
        result.warn("public surface registry not present; trust public surfaces not verified")
    else:
        missing_surfaces = sorted(REQUIRED_PUBLIC_SURFACES - surfaces)
        if missing_surfaces:
            result.error("missing public surface registrations: %s" % ", ".join(missing_surfaces))
    diagnostics = diagnostic_codes(repo_root)
    if diagnostics is None:
        result.warn("diagnostics registry not present; mod/pack diagnostics not verified")
    else:
        missing_diagnostics = sorted(REQUIRED_DIAGNOSTICS - diagnostics)
        if missing_diagnostics:
            result.error("missing diagnostic codes: %s" % ", ".join(missing_diagnostics))
    refusals = refusal_codes(repo_root)
    if refusals is None:
        result.warn("refusal registry not present; mod/pack refusals not verified")
    else:
        missing_refusals = sorted(REQUIRED_REFUSALS - refusals)
        if missing_refusals:
            result.error("missing refusal codes: %s" % ", ".join(missing_refusals))
    capabilities = capability_ids(repo_root)
    if capabilities is None:
        result.warn("capability registry not present; optional mod/pack capabilities not verified")
    else:
        missing_capabilities = sorted(OPTIONAL_CAPABILITIES - capabilities)
        if missing_capabilities:
            result.warn("optional mod/pack capabilities not registered: %s" % ", ".join(missing_capabilities))
    result.info["trust_levels_registered"] = len(levels)
    result.info["permission_kinds_registered"] = len(permissions)
    result.info["mod_lifecycle_states_registered"] = len(states)


def _is_path_like(value: str) -> bool:
    return bool(PATH_LIKE_RE.search(value))


def _has_payload_kind(data: Dict[str, Any], kind: str) -> bool:
    for payload in data.get("payloads", []):
        if isinstance(payload, dict) and payload.get("kind") == kind:
            return True
    return False


def validate_mod_descriptor(
    data: Dict[str, Any],
    source: str,
    levels: Dict[str, Dict[str, Any]],
    permissions: Dict[str, Dict[str, Any]],
    diagnostics: Optional[Set[str]],
    refusals: Optional[Set[str]],
    capabilities: Optional[Set[str]],
) -> List[str]:
    errors: List[str] = []
    required = [
        "mod_id",
        "mod_kind",
        "trust_level",
        "owner",
        "version",
        "capabilities",
        "permissions",
        "dependencies",
        "conflicts",
        "payloads",
        "schemas_used",
        "determinism_impact",
        "security_impact",
        "review_status",
        "compatibility_range",
        "validation_fixtures",
        "diagnostic_codes",
        "refusal_codes",
    ]
    for field in required:
        if field not in data:
            errors.append("%s missing required field %s" % (source, field))
    mod_id = data.get("mod_id")
    if isinstance(mod_id, str):
        if not MOD_ID_RE.match(mod_id):
            errors.append("%s mod_id is not lowercase dotted: %s" % (source, mod_id))
        if _is_path_like(mod_id):
            errors.append("%s mod_id must not be path-like: %s" % (source, mod_id))
    elif "mod_id" in data:
        errors.append("%s mod_id must be a string" % source)

    trust_level = data.get("trust_level")
    if trust_level not in levels:
        errors.append("%s unknown trust_level: %s" % (source, trust_level))
        allowed_permissions: Set[str] = set()
    else:
        allowed_permissions = set(levels[trust_level].get("allowed_permissions", []))

    requested_permissions = data.get("permissions")
    if not isinstance(requested_permissions, list):
        errors.append("%s permissions must be an array" % source)
        requested_permissions = []
    requested_set = {item for item in requested_permissions if isinstance(item, str)}
    unknown_permissions = sorted(requested_set - set(permissions))
    if unknown_permissions:
        errors.append("%s unknown permissions: %s" % (source, ", ".join(unknown_permissions)))
    if allowed_permissions:
        outside_allowed = sorted(requested_set - allowed_permissions)
        if outside_allowed:
            errors.append("%s permissions not allowed by trust_level %s: %s" % (source, trust_level, ", ".join(outside_allowed)))

    declared = data.get("declared_permissions")
    if not isinstance(declared, dict):
        errors.append("%s declared_permissions must be an object" % source)
        declared = {}
    undeclared = sorted(perm for perm in requested_set if perm not in declared)
    if undeclared:
        errors.append("%s permissions lack declarations: %s" % (source, ", ".join(undeclared)))

    if trust_level == "data_only":
        forbidden = sorted(requested_set - DATA_ONLY_ALLOWED)
        if forbidden:
            errors.append("%s data_only pack requested forbidden permissions: %s" % (source, ", ".join(forbidden)))
        if data.get("native_code") is True or data.get("external_process") is True:
            errors.append("%s data_only pack cannot declare native_code or external_process" % source)

    determinism = data.get("determinism_impact")
    if not isinstance(determinism, dict):
        errors.append("%s determinism_impact must be declared" % source)
    else:
        for field in ("classification", "replay_policy", "authoritative_state_impact"):
            if not determinism.get(field):
                errors.append("%s determinism_impact missing %s" % (source, field))
        if determinism.get("classification") == "unknown":
            errors.append("%s determinism_impact classification cannot be unknown" % source)

    if (requested_set & NATIVE_PERMISSIONS) or data.get("native_code") is True or data.get("mod_kind") in {"native_provider_pack", "signed_native_provider_pack"}:
        if trust_level not in {"trusted_native_provider", "signed_native_provider"}:
            errors.append("%s native authority requires trusted_native_provider or signed_native_provider trust" % source)
        if data.get("native_code") is not True:
            errors.append("%s native provider must declare native_code true" % source)
        if data.get("review_status") not in {"reviewed", "trusted", "signed"}:
            errors.append("%s native provider requires reviewed/trusted/signed review_status" % source)
        if not data.get("evidence"):
            errors.append("%s native provider requires evidence" % source)

    if trust_level == "external_process_adapter" or data.get("mod_kind") == "external_process_adapter_pack":
        if data.get("external_process") is not True:
            errors.append("%s external adapter must declare external_process true" % source)
        if not data.get("process_access") or data.get("process_access") == "none":
            errors.append("%s external adapter must declare process_access" % source)
        if not _has_payload_kind(data, "ipc_protocol"):
            errors.append("%s external adapter must declare ipc_protocol payload" % source)
        if requested_set & NETWORK_PERMISSIONS and (not data.get("network_access") or data.get("network_access") == "none"):
            errors.append("%s external adapter requested network permissions without network_access declaration" % source)
        if requested_set & FILESYSTEM_PERMISSIONS and (not data.get("filesystem_access") or data.get("filesystem_access") == "none"):
            errors.append("%s external adapter requested filesystem permissions without filesystem_access declaration" % source)

    for overlay in data.get("overlays", []):
        if not isinstance(overlay, dict):
            errors.append("%s overlay entries must be objects" % source)
            continue
        policy = overlay.get("conflict_policy")
        if policy in FORBIDDEN_OVERLAY_POLICIES:
            errors.append("%s overlay uses forbidden conflict_policy: %s" % (source, policy))
        if overlay.get("conflicts_with") and not policy:
            errors.append("%s overlay conflict missing conflict_policy" % source)

    if diagnostics is not None:
        for code in data.get("diagnostic_codes", []):
            if code not in diagnostics:
                errors.append("%s diagnostic code not registered: %s" % (source, code))
    if refusals is not None:
        for code in data.get("refusal_codes", []):
            if code not in refusals:
                errors.append("%s refusal code not registered: %s" % (source, code))
    if capabilities is not None:
        for capability in data.get("capabilities", []):
            if capability not in capabilities:
                errors.append("%s capability not registered: %s" % (source, capability))
    return errors


def validate_fixture_file(repo_root: Path, fixture: Path) -> List[str]:
    levels = trust_levels(repo_root)
    permissions = permission_kinds(repo_root)
    return validate_mod_descriptor(
        load_json(fixture),
        rel(fixture, repo_root),
        levels,
        permissions,
        diagnostic_codes(repo_root),
        refusal_codes(repo_root),
        capability_ids(repo_root),
    )


def validate_fixtures(repo_root: Path, result: CheckResult) -> None:
    expected = {
        "valid_data_only_pack.json": True,
        "valid_schema_validated_pack.json": True,
        "valid_workbench_module_pack.json": True,
        "valid_external_adapter_pack.json": True,
        "valid_native_provider_pack.json": True,
        "invalid_native_provider_without_trust.json": False,
        "invalid_network_permission_in_data_pack.json": False,
        "invalid_silent_overlay_conflict.json": False,
        "invalid_undeclared_filesystem_permission.json": False,
        "invalid_determinism_impact_missing.json": False,
    }
    fixture_dir = repo_root / FIXTURE_DIR_REL
    if not fixture_dir.exists():
        result.error("missing fixture directory: %s" % FIXTURE_DIR_REL.as_posix())
        return
    passed = 0
    for name, should_pass in expected.items():
        path = fixture_dir / name
        if not path.exists():
            result.error("missing fixture: %s" % rel(path, repo_root))
            continue
        try:
            errors = validate_fixture_file(repo_root, path)
        except Exception as exc:
            errors = ["%s parse/validation error: %s" % (rel(path, repo_root), exc)]
        if should_pass and errors:
            result.error("%s should pass but failed: %s" % (rel(path, repo_root), "; ".join(errors)))
        elif (not should_pass) and not errors:
            result.error("%s should fail but passed" % rel(path, repo_root))
        else:
            passed += 1
    result.info["fixtures_checked"] = len(expected)
    result.info["fixtures_expected_behavior_observed"] = passed


def run_git_ls_files(repo_root: Path) -> List[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def inventory(repo_root: Path) -> Dict[str, Any]:
    files = run_git_ls_files(repo_root)
    categories: Dict[str, List[str]] = {
        "data_only_pack_candidate": [],
        "schema_validated_pack_candidate": [],
        "scriptless_rule_data_candidate": [],
        "module_pack_candidate": [],
        "external_adapter_candidate": [],
        "native_provider_candidate": [],
        "trust_unknown": [],
        "fixture_historical_generated": [],
        "deferred": [],
    }
    for path in files:
        lowered = path.lower()
        if "archive/" in lowered or "archive\\" in lowered or "generated" in lowered or "/fixtures/" in lowered or "\\fixtures\\" in lowered:
            categories["fixture_historical_generated"].append(path)
        elif lowered.endswith("pack.trust.json"):
            categories["schema_validated_pack_candidate"].append(path)
        elif lowered.startswith("content/packs/") and lowered.endswith(("pack_manifest.json", "pack.json", "pack.toml")):
            categories["data_only_pack_candidate"].append(path)
        elif lowered.startswith("content/profiles/") or lowered.startswith("content/bundles/"):
            categories["data_only_pack_candidate"].append(path)
        elif lowered.startswith("contracts/schema/modding/") or lowered.startswith("contracts/schema/package/modding/"):
            categories["scriptless_rule_data_candidate"].append(path)
        elif lowered.startswith("contracts/module/") or lowered.startswith("contracts/provider/") or lowered.startswith("contracts/capability/"):
            categories["module_pack_candidate"].append(path)
        elif "external" in lowered and ("adapter" in lowered or "process" in lowered):
            categories["external_adapter_candidate"].append(path)
        elif "native" in lowered or lowered.endswith((".dll", ".so", ".dylib")):
            categories["native_provider_candidate"].append(path)
        elif lowered.startswith("docs/modding/") or lowered.startswith("docs/content/") or lowered.startswith("docs/release/"):
            categories["deferred"].append(path)
        elif lowered.startswith("contracts/package/") or lowered.startswith("contracts/artifact/") or lowered.startswith("contracts/refusal/") or lowered.startswith("contracts/diagnostics/"):
            categories["trust_unknown"].append(path)
    return {
        "files_scanned": len(files),
        "categories": {key: len(value) for key, value in categories.items()},
        "examples": {key: value[:12] for key, value in categories.items() if value[:12]},
    }


def run_checks(repo_root: Path, include_fixtures: bool, include_inventory: bool) -> CheckResult:
    result = CheckResult()
    validate_required_files(repo_root, result)
    validate_contract_ids(repo_root, result)
    if not result.errors:
        validate_registries(repo_root, result)
    if include_fixtures and not result.errors:
        validate_fixtures(repo_root, result)
    if include_inventory:
        try:
            inv = inventory(repo_root)
            result.info["inventory"] = inv
            result.warn("inventory mode is descriptive; existing packs are not migrated by this validator")
        except Exception as exc:
            result.error("inventory failed: %s" % exc)
    return result


def print_text(result: CheckResult) -> None:
    if result.errors:
        print("MOD-PACK-TRUST-MODEL-01: FAIL")
        for error in result.errors:
            print("ERROR:", error)
    else:
        print("MOD-PACK-TRUST-MODEL-01: PASS")
    for warning in result.warnings:
        print("WARN:", warning)
    if result.info:
        print("INFO:", json.dumps(result.info, indent=2, sort_keys=True))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Validate contracts, registries, and fixtures")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fixtures", action="store_true", help="Validate fixtures")
    parser.add_argument("--inventory", action="store_true", help="Report trust-like inventory without failing historical gaps")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    include_fixtures = args.strict or args.fixtures
    include_inventory = args.inventory
    result = run_checks(repo_root, include_fixtures=include_fixtures, include_inventory=include_inventory)
    if args.json:
        print(
            json.dumps(
                {
                    "status": "pass" if not result.errors else "fail",
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "info": result.info,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_text(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
