#!/usr/bin/env python3
"""Validate Dominium composition plan, decision, lock, report, and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


COMPOSITION_CONTRACT_REL = Path("contracts/composition/composition_resolver.contract.toml")
PLAN_SCHEMA_REL = Path("contracts/composition/composition_plan.schema.json")
DECISION_SCHEMA_REL = Path("contracts/composition/composition_decision.schema.json")
PLAN_KIND_REGISTRY_REL = Path("contracts/composition/composition_plan_kind.registry.json")
STATUS_REGISTRY_REL = Path("contracts/composition/composition_status.registry.json")
ORDER_POLICY_REGISTRY_REL = Path("contracts/composition/deterministic_order_policy.registry.json")
OVERLAY_POLICY_REGISTRY_REL = Path("contracts/composition/overlay_conflict_policy.registry.json")
REPORT_KIND_REGISTRY_REL = Path("contracts/composition/composition_report_kind.registry.json")
PROFILE_SCHEMA_REL = Path("contracts/profile/profile_composition.schema.json")
PROFILE_REGISTRY_REL = Path("contracts/profile/profile.registry.json")
PACKAGE_LOCK_REL = Path("contracts/package/locks/pack_lock.mvp_default.json")
APP_FIXTURE_DIR_REL = Path("tests/contract/app/fixtures")
MODULE_SURFACE_REL = Path("contracts/module/module_surface.contract.toml")
MODULE_FIXTURE_DIR_REL = Path("tests/contract/module/fixtures")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
PROVIDER_KIND_REGISTRY_REL = Path("contracts/provider/provider_kind.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
TRUST_LEVEL_REGISTRY_REL = Path("contracts/trust/trust_level.registry.json")
COMPOSITION_FIXTURE_DIR_REL = Path("tests/contract/composition/fixtures")
LOCK_FIXTURE_DIR_REL = Path("tests/contract/lock/fixtures")
PROFILE_FIXTURE_DIR_REL = Path("tests/contract/profile/fixtures")

LOCK_SCHEMA_RELS = [
    Path("contracts/lock/app_composition_lock.schema.json"),
    Path("contracts/lock/pack_mount_lock.schema.json"),
    Path("contracts/lock/module_plan_lock.schema.json"),
    Path("contracts/lock/provider_selection_lock.schema.json"),
    Path("contracts/lock/capability_report.schema.json"),
    Path("contracts/lock/refusal_report.schema.json"),
    Path("contracts/lock/compatibility_report.schema.json"),
    Path("contracts/lock/trust_report.schema.json"),
]

EXPECTED_SCHEMA_IDS = {
    PLAN_SCHEMA_REL: "dominium.composition.plan.v1",
    DECISION_SCHEMA_REL: "dominium.composition.decision.v1",
    PROFILE_SCHEMA_REL: "dominium.profile.composition.v1",
    Path("contracts/lock/app_composition_lock.schema.json"): "dominium.lock.app_composition.v1",
    Path("contracts/lock/pack_mount_lock.schema.json"): "dominium.lock.pack_mount.v1",
    Path("contracts/lock/module_plan_lock.schema.json"): "dominium.lock.module_plan.v1",
    Path("contracts/lock/provider_selection_lock.schema.json"): "dominium.lock.provider_selection.v1",
    Path("contracts/lock/capability_report.schema.json"): "dominium.report.capability.v1",
    Path("contracts/lock/refusal_report.schema.json"): "dominium.report.refusal.v1",
    Path("contracts/lock/compatibility_report.schema.json"): "dominium.report.compatibility.v1",
    Path("contracts/lock/trust_report.schema.json"): "dominium.report.trust.v1",
}

SCHEMA_ID_TO_LOCK_SCHEMA = {
    "dominium.lock.app_composition": "app_composition_lock",
    "dominium.lock.pack_mount": "pack_mount_lock",
    "dominium.lock.module_plan": "module_plan_lock",
    "dominium.lock.provider_selection": "provider_selection_lock",
    "dominium.report.capability": "capability_report",
    "dominium.report.refusal": "refusal_report",
    "dominium.report.compatibility": "compatibility_report",
    "dominium.report.trust": "trust_report",
}

COMMON_DERIVED_REQUIRED = {
    "source_plan_ref",
    "decision_ref",
    "source_artifact_refs",
    "schema_version",
    "generated_by",
    "entries",
    "diagnostics",
    "evidence_ref",
    "limitations",
    "status",
}

TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")
PATHLIKE_RE = re.compile(r"[/\\]|\.(json|toml|py|exe|dll|so|dylib)$|^[A-Za-z]:", re.IGNORECASE)
FORBIDDEN_OVERLAY_BEHAVIORS = {"silent_overwrite", "implicit_last_wins", "ignored", "best_effort"}
NO_SUPPORT_STATUSES = {"fixture_only", "planned"}


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
    try:
        return int(raw)
    except ValueError:
        return raw


def _minimal_toml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
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


def load_toml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def strings(value: Any) -> List[str]:
    return [str(item) for item in as_list(value) if item not in (None, "")]


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def has_error(findings: Sequence[Dict[str, Any]]) -> bool:
    return any(item.get("level") == "error" for item in findings)


def is_pathlike(value: str) -> bool:
    return bool(PATHLIKE_RE.search(value))


def valid_id(value: str) -> bool:
    return bool(value and TOKEN_RE.match(value) and not is_pathlike(value))


def read_json_if_exists(repo_root: Path, rel: Path) -> Dict[str, Any]:
    path = repo_root / rel
    if not path.exists():
        return {}
    try:
        data = load_json(path)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def read_known_app_ids(repo_root: Path) -> Set[str]:
    ids: Set[str] = set()
    for path in sorted((repo_root / APP_FIXTURE_DIR_REL).glob("valid_*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        app_id = data.get("app_id")
        if isinstance(app_id, str):
            ids.add(app_id)
        for item in strings(data.get("apps")):
            ids.add(item)
    return ids


def read_known_profile_ids(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, PROFILE_REGISTRY_REL)
    return {str(item.get("profile_id")) for item in as_list(data.get("profiles")) if isinstance(item, dict) and item.get("profile_id")}


def read_known_pack_ids(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, PACKAGE_LOCK_REL)
    ids = set(strings(data.get("ordered_pack_ids")))
    for item in as_list(data.get("ordered_packs")):
        if isinstance(item, dict) and item.get("pack_id"):
            ids.add(str(item["pack_id"]))
        for source in as_list(item.get("source_packs") if isinstance(item, dict) else None):
            if isinstance(source, dict) and source.get("pack_id"):
                ids.add(str(source["pack_id"]))
    return ids


def read_known_module_ids(repo_root: Path) -> Set[str]:
    ids: Set[str] = set()
    path = repo_root / MODULE_SURFACE_REL
    if path.exists():
        try:
            data = load_toml(path)
            ids.update(str(item.get("module_id")) for item in as_list(data.get("module")) if isinstance(item, dict) and item.get("module_id"))
        except Exception:
            pass
    for path in sorted((repo_root / MODULE_FIXTURE_DIR_REL).glob("valid_*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        module_id = data.get("module_id")
        if isinstance(module_id, str):
            ids.add(module_id)
    return ids


def read_provider_data(repo_root: Path) -> Tuple[Dict[str, Set[str]], Set[str], Set[str]]:
    registry = read_json_if_exists(repo_root, PROVIDER_REGISTRY_REL)
    providers: Dict[str, Set[str]] = {}
    for item in as_list(registry.get("providers")):
        if isinstance(item, dict) and item.get("provider_id"):
            providers[str(item["provider_id"])] = set(strings(item.get("capabilities_provided")))
    kinds_data = read_json_if_exists(repo_root, PROVIDER_KIND_REGISTRY_REL)
    kinds = {str(item.get("id")) for item in as_list(kinds_data.get("kinds")) if isinstance(item, dict) and item.get("id")}
    decisions = {str(item) for item in as_list(kinds_data.get("decision_values")) if isinstance(item, str)}
    return providers, kinds, decisions


def read_capability_ids(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, CAPABILITY_REGISTRY_REL)
    return {str(item.get("capability_id")) for item in as_list(data.get("capabilities")) if isinstance(item, dict) and item.get("capability_id")}


def read_refusal_codes(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, REFUSAL_REGISTRY_REL)
    values: Set[str] = set()
    for item in as_list(data.get("codes")):
        if isinstance(item, dict):
            if item.get("code"):
                values.add(str(item["code"]))
            if item.get("refusal_id"):
                values.add(str(item["refusal_id"]))
    return values


def read_diagnostic_codes(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, DIAGNOSTIC_REGISTRY_REL)
    return {str(item.get("code")) for item in as_list(data.get("codes")) if isinstance(item, dict) and item.get("code")}


def read_trust_levels(repo_root: Path) -> Set[str]:
    data = read_json_if_exists(repo_root, TRUST_LEVEL_REGISTRY_REL)
    return {str(item.get("trust_level")) for item in as_list(data.get("levels")) if isinstance(item, dict) and item.get("trust_level")}


def build_context(repo_root: Path) -> Dict[str, Any]:
    providers, provider_kinds, provider_decisions = read_provider_data(repo_root)
    return {
        "apps": read_known_app_ids(repo_root),
        "profiles": read_known_profile_ids(repo_root),
        "packs": read_known_pack_ids(repo_root),
        "modules": read_known_module_ids(repo_root),
        "providers": providers,
        "provider_ids": set(providers),
        "provider_kinds": provider_kinds,
        "provider_decisions": provider_decisions,
        "capabilities": read_capability_ids(repo_root),
        "refusals": read_refusal_codes(repo_root),
        "diagnostics": read_diagnostic_codes(repo_root),
        "trust_levels": read_trust_levels(repo_root),
    }


def validate_schema_file(repo_root: Path, rel: Path) -> List[Dict[str, Any]]:
    path = repo_root / rel
    if not path.exists():
        return [finding("error", "missing_schema", f"missing {rel.as_posix()}", rel.as_posix())]
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "invalid_json", f"{rel.as_posix()} does not parse: {exc}", rel.as_posix())]
    findings: List[Dict[str, Any]] = []
    expected_id = EXPECTED_SCHEMA_IDS.get(rel)
    if expected_id and data.get("$id") != expected_id:
        findings.append(finding("error", "schema_bad_id", f"{rel.as_posix()} $id must be {expected_id}", rel.as_posix()))
    if rel in LOCK_SCHEMA_RELS:
        required = set(as_list(data.get("required")))
        missing = sorted(COMMON_DERIVED_REQUIRED - required)
        if missing:
            findings.append(finding("error", "lock_schema_missing_required", f"{rel.as_posix()} missing required fields: {', '.join(missing)}", rel.as_posix()))
        properties = data.get("properties", {})
        artifact_class = properties.get("artifact_class", {}) if isinstance(properties, dict) else {}
        source_truth = properties.get("source_truth", {}) if isinstance(properties, dict) else {}
        if artifact_class.get("const") != "derived_evidence":
            findings.append(finding("error", "lock_schema_not_derived", "lock/report schema must const artifact_class derived_evidence", rel.as_posix()))
        if source_truth.get("const") is not False:
            findings.append(finding("error", "lock_schema_source_truth", "lock/report schema must const source_truth false", rel.as_posix()))
    return findings


def validate_contracts(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in [PLAN_SCHEMA_REL, DECISION_SCHEMA_REL, PROFILE_SCHEMA_REL] + LOCK_SCHEMA_RELS:
        findings.extend(validate_schema_file(repo_root, rel))

    registries: Dict[str, Any] = {}
    for rel in [PLAN_KIND_REGISTRY_REL, STATUS_REGISTRY_REL, ORDER_POLICY_REGISTRY_REL, OVERLAY_POLICY_REGISTRY_REL, REPORT_KIND_REGISTRY_REL, PROFILE_REGISTRY_REL]:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_registry", f"missing {rel.as_posix()}", rel.as_posix()))
            continue
        try:
            registries[rel.as_posix()] = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_registry_json", f"{rel.as_posix()} does not parse: {exc}", rel.as_posix()))

    plan_kinds = {str(item.get("id")) for item in as_list(registries.get(PLAN_KIND_REGISTRY_REL.as_posix(), {}).get("plan_kinds")) if isinstance(item, dict) and item.get("id")}
    required_plan_kinds = {"product_launch", "workbench_workspace", "package_mount", "profile_load", "provider_selection", "module_enablement", "release_projection", "test_fixture"}
    missing_plan_kinds = sorted(required_plan_kinds - plan_kinds)
    if missing_plan_kinds:
        findings.append(finding("error", "plan_kind_missing", f"missing plan kinds: {', '.join(missing_plan_kinds)}", PLAN_KIND_REGISTRY_REL.as_posix()))

    statuses = registries.get(STATUS_REGISTRY_REL.as_posix(), {})
    for key, required in [
        ("decision_statuses", {"selected", "degraded", "refused", "partial", "fixture_only", "planned"}),
        ("lock_statuses", {"selected", "degraded", "refused", "partial", "fixture_only", "planned", "stale", "invalid"}),
    ]:
        values = {str(item) for item in as_list(statuses.get(key)) if isinstance(item, str)}
        missing = sorted(required - values)
        if missing:
            findings.append(finding("error", "status_missing", f"{key} missing: {', '.join(missing)}", STATUS_REGISTRY_REL.as_posix()))

    overlay = registries.get(OVERLAY_POLICY_REGISTRY_REL.as_posix(), {})
    forbidden = {str(item) for item in as_list(overlay.get("forbidden_conflict_behaviors")) if isinstance(item, str)}
    if not FORBIDDEN_OVERLAY_BEHAVIORS.issubset(forbidden):
        findings.append(finding("error", "overlay_forbidden_missing", "overlay registry must forbid silent overwrite, implicit last-wins, ignored, and best-effort", OVERLAY_POLICY_REGISTRY_REL.as_posix()))

    contract_path = repo_root / COMPOSITION_CONTRACT_REL
    if not contract_path.exists():
        findings.append(finding("error", "missing_contract", f"missing {COMPOSITION_CONTRACT_REL.as_posix()}", COMPOSITION_CONTRACT_REL.as_posix()))
    else:
        try:
            contract = load_toml(contract_path)
        except Exception as exc:
            findings.append(finding("error", "invalid_contract_toml", f"composition contract does not parse: {exc}", COMPOSITION_CONTRACT_REL.as_posix()))
        else:
            policy = contract.get("policy", {})
            expected = {
                "runtime_loader_implemented": False,
                "app_composer_implemented": False,
                "package_mounting_implemented": False,
                "resolver_mutates_truth": False,
                "descriptor_identity_is_path": False,
                "source_ref_is_semantic_authority": False,
                "lockfile_is_source_truth": False,
                "product_identity_is_executable": False,
                "silent_fallback_allowed": False,
                "silent_overlay_overwrite_allowed": False,
                "provider_fallback_requires_trace": True,
                "degraded_decisions_require_diagnostics": True,
                "fixture_only_implies_support": False,
            }
            for key, value in expected.items():
                if policy.get(key) is not value:
                    findings.append(finding("error", "composition_policy_mismatch", f"policy {key} must be {value}", COMPOSITION_CONTRACT_REL.as_posix()))
    return findings, registries


def identity_field_name(key: str) -> bool:
    return key in {"lock_id", "report_id", "composition_plan_id", "composition_decision_id", "profile_id"} or key.endswith("_id")


def find_path_identity(value: Any, path: str, findings: List[Dict[str, Any]], trail: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            next_trail = f"{trail}.{key}"
            if identity_field_name(str(key)) and isinstance(item, str) and is_pathlike(item):
                findings.append(finding("error", "path_as_identity", f"path-like identity at {next_trail}: {item}", path))
            if str(key) in {"identity_kind", "identity_source"} and item == "raw_path":
                findings.append(finding("error", "raw_path_identity", f"raw path identity is forbidden at {next_trail}", path))
            find_path_identity(item, path, findings, next_trail)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            find_path_identity(item, path, findings, f"{trail}[{index}]")


def check_known(value: str, known: Set[str], code: str, label: str, path: str, findings: List[Dict[str, Any]]) -> None:
    if value and known and value not in known:
        findings.append(finding("error", code, f"unknown {label}: {value}", path))


def check_support_claim(data: Dict[str, Any], status: str, path: str, findings: List[Dict[str, Any]]) -> None:
    if status in NO_SUPPORT_STATUSES and data.get("support_claim") is True:
        findings.append(finding("error", "fixture_or_planned_support_claim", f"{status} rows must not claim support", path))


def validate_plan(data: Dict[str, Any], path: str, ctx: Dict[str, Any], registries: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    find_path_identity(data, path, findings)
    required = {"schema_id", "schema_version", "composition_plan_id", "plan_kind", "app_ref", "profile_refs", "pack_refs", "module_refs", "provider_requests", "capability_requests", "artifact_inputs", "requested_outputs", "evidence_policy_ref", "deterministic_order_policy_ref", "source_refs", "status"}
    for key in sorted(required):
        if key not in data:
            findings.append(finding("error", "plan_missing_field", f"missing field: {key}", path))
    if data.get("schema_id") != "dominium.composition.plan":
        findings.append(finding("error", "plan_bad_schema_id", "schema_id must be dominium.composition.plan", path))
    if data.get("schema_version") != "1.0.0":
        findings.append(finding("error", "plan_bad_schema_version", "schema_version must be 1.0.0", path))
    plan_id = str(data.get("composition_plan_id") or "")
    if not valid_id(plan_id):
        findings.append(finding("error", "plan_bad_id", f"bad composition_plan_id: {plan_id}", path))

    plan_kinds = {str(item.get("id")) for item in as_list(registries.get(PLAN_KIND_REGISTRY_REL.as_posix(), {}).get("plan_kinds")) if isinstance(item, dict) and item.get("id")}
    if str(data.get("plan_kind") or "") not in plan_kinds:
        findings.append(finding("error", "plan_unknown_kind", f"unknown plan_kind: {data.get('plan_kind')}", path))
    plan_statuses = {str(item) for item in as_list(registries.get(STATUS_REGISTRY_REL.as_posix(), {}).get("plan_statuses")) if isinstance(item, str)}
    status = str(data.get("status") or "")
    if status not in plan_statuses:
        findings.append(finding("error", "plan_unknown_status", f"unknown plan status: {status}", path))
    check_support_claim(data, status, path, findings)

    app_ref = data.get("app_ref")
    if isinstance(app_ref, str):
        check_known(app_ref, ctx["apps"], "plan_unknown_app", "app_ref", path, findings)
    for profile in strings(data.get("profile_refs")):
        check_known(profile, ctx["profiles"], "plan_unknown_profile", "profile_ref", path, findings)
    for pack in strings(data.get("pack_refs")):
        check_known(pack, ctx["packs"], "plan_unknown_pack", "pack_ref", path, findings)
    for module in strings(data.get("module_refs")):
        check_known(module, ctx["modules"], "plan_unknown_module", "module_ref", path, findings)
    module_refs = strings(data.get("module_refs"))
    if module_refs != sorted(module_refs, key=str.casefold):
        findings.append(finding("error", "plan_modules_not_sorted", "module_refs must be sorted case-folded ascending", path))

    provider_requests = [item for item in as_list(data.get("provider_requests")) if isinstance(item, dict)]
    if len(provider_requests) != len(as_list(data.get("provider_requests"))):
        findings.append(finding("error", "provider_request_shape", "provider_requests must contain objects", path))
    request_ids = strings([item.get("request_id") for item in provider_requests])
    if request_ids != sorted(request_ids, key=str.casefold):
        findings.append(finding("error", "provider_requests_not_sorted", "provider_requests must be sorted by request_id", path))
    for index, item in enumerate(provider_requests):
        item_path = f"{path}#provider_requests[{index}]"
        if str(item.get("provider_kind") or "") not in ctx["provider_kinds"]:
            findings.append(finding("error", "plan_unknown_provider_kind", f"unknown provider_kind: {item.get('provider_kind')}", item_path))
        preferred = item.get("preferred_provider_ref")
        if isinstance(preferred, str):
            check_known(preferred, ctx["provider_ids"], "plan_unknown_provider", "provider_ref", item_path, findings)
        for cap in strings(item.get("required_capabilities")) + strings(item.get("optional_capabilities")):
            check_known(cap, ctx["capabilities"], "plan_unknown_capability", "provider capability", item_path, findings)

    for index, item in enumerate(as_list(data.get("capability_requests"))):
        item_path = f"{path}#capability_requests[{index}]"
        if not isinstance(item, dict):
            findings.append(finding("error", "capability_request_shape", "capability_requests must contain objects", item_path))
            continue
        cap = str(item.get("capability_ref") or "")
        check_known(cap, ctx["capabilities"], "plan_unknown_capability", "capability_ref", item_path, findings)
    return findings


def validate_decision(data: Dict[str, Any], path: str, ctx: Dict[str, Any], registries: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    find_path_identity(data, path, findings)
    required = {"schema_id", "schema_version", "composition_decision_id", "plan_ref", "status", "selected_profile_refs", "selected_pack_refs", "selected_module_refs", "selected_provider_refs", "capability_decisions", "refusal_refs", "diagnostic_refs", "conflict_reports", "lockfile_refs", "evidence_ref", "fallback_trace", "limitations", "source_refs", "generated_by", "deterministic_order_key"}
    for key in sorted(required):
        if key not in data:
            findings.append(finding("error", "decision_missing_field", f"missing field: {key}", path))
    if data.get("schema_id") != "dominium.composition.decision":
        findings.append(finding("error", "decision_bad_schema_id", "schema_id must be dominium.composition.decision", path))
    decision_id = str(data.get("composition_decision_id") or "")
    if not valid_id(decision_id):
        findings.append(finding("error", "decision_bad_id", f"bad composition_decision_id: {decision_id}", path))
    statuses = {str(item) for item in as_list(registries.get(STATUS_REGISTRY_REL.as_posix(), {}).get("decision_statuses")) if isinstance(item, str)}
    status = str(data.get("status") or "")
    if status not in statuses:
        findings.append(finding("error", "decision_unknown_status", f"unknown decision status: {status}", path))
    check_support_claim(data, status, path, findings)
    if status in {"degraded", "partial"} and not as_list(data.get("fallback_trace")):
        findings.append(finding("error", "degraded_missing_fallback_trace", "degraded or partial decisions require fallback_trace", path))
    if status == "degraded" and not as_list(data.get("diagnostic_refs")):
        findings.append(finding("error", "degraded_missing_diagnostic", "degraded decisions require diagnostic_refs", path))

    selected_app = data.get("selected_app_ref")
    if isinstance(selected_app, str):
        check_known(selected_app, ctx["apps"], "decision_unknown_app", "selected_app_ref", path, findings)
    for profile in strings(data.get("selected_profile_refs")):
        check_known(profile, ctx["profiles"], "decision_unknown_profile", "selected_profile_ref", path, findings)
    for pack in strings(data.get("selected_pack_refs")):
        check_known(pack, ctx["packs"], "decision_unknown_pack", "selected_pack_ref", path, findings)
    for module in strings(data.get("selected_module_refs")):
        check_known(module, ctx["modules"], "decision_unknown_module", "selected_module_ref", path, findings)
    for provider in strings(data.get("selected_provider_refs")):
        check_known(provider, ctx["provider_ids"], "decision_unknown_provider", "selected_provider_ref", path, findings)
    for refusal in strings(data.get("refusal_refs")):
        check_known(refusal, ctx["refusals"], "decision_unknown_refusal", "refusal_ref", path, findings)
    for diagnostic in strings(data.get("diagnostic_refs")):
        check_known(diagnostic, ctx["diagnostics"], "decision_unknown_diagnostic", "diagnostic_ref", path, findings)
    for index, item in enumerate(as_list(data.get("capability_decisions"))):
        item_path = f"{path}#capability_decisions[{index}]"
        if not isinstance(item, dict):
            findings.append(finding("error", "capability_decision_shape", "capability_decisions must contain objects", item_path))
            continue
        if item.get("capability_ref"):
            check_known(str(item["capability_ref"]), ctx["capabilities"], "decision_unknown_capability", "capability_ref", item_path, findings)
        if item.get("selected_provider_ref"):
            check_known(str(item["selected_provider_ref"]), ctx["provider_ids"], "decision_unknown_provider", "selected_provider_ref", item_path, findings)
    return findings


def validate_profile(data: Dict[str, Any], path: str, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    find_path_identity(data, path, findings)
    if data.get("schema_id") != "dominium.profile.composition":
        findings.append(finding("error", "profile_bad_schema_id", "schema_id must be dominium.profile.composition", path))
    profile_id = str(data.get("profile_id") or "")
    if not valid_id(profile_id):
        findings.append(finding("error", "profile_bad_id", f"bad profile_id: {profile_id}", path))
    check_support_claim(data, str(data.get("stability") or ""), path, findings)
    for cap in strings(data.get("capabilities")):
        check_known(cap, ctx["capabilities"], "profile_unknown_capability", "capability", path, findings)
    for pack in strings(data.get("pack_refs")):
        check_known(pack, ctx["packs"], "profile_unknown_pack", "pack_ref", path, findings)
    for provider in strings(data.get("provider_preferences")):
        check_known(provider, ctx["provider_ids"], "profile_unknown_provider", "provider_preference", path, findings)
    return findings


def validate_derived_header(data: Dict[str, Any], path: str, registries: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    find_path_identity(data, path, findings)
    schema_id = str(data.get("schema_id") or "")
    if schema_id not in SCHEMA_ID_TO_LOCK_SCHEMA:
        findings.append(finding("error", "derived_unknown_schema_id", f"unknown lock/report schema_id: {schema_id}", path))
    for key in COMMON_DERIVED_REQUIRED:
        if key not in data:
            findings.append(finding("error", "derived_missing_field", f"missing field: {key}", path))
    identity = str(data.get("lock_id") or data.get("report_id") or "")
    if not identity:
        findings.append(finding("error", "derived_missing_identity", "lock/report requires lock_id or report_id", path))
    elif not valid_id(identity):
        findings.append(finding("error", "derived_bad_identity", f"bad lock/report identity: {identity}", path))
    if data.get("artifact_class") != "derived_evidence":
        findings.append(finding("error", "derived_artifact_class", "lock/report artifact_class must be derived_evidence", path))
    if data.get("source_truth") is not False:
        findings.append(finding("error", "derived_source_truth", "lock/report source_truth must be false", path))
    statuses = {str(item) for item in as_list(registries.get(STATUS_REGISTRY_REL.as_posix(), {}).get("lock_statuses")) if isinstance(item, str)}
    status = str(data.get("status") or "")
    if status not in statuses:
        findings.append(finding("error", "derived_unknown_status", f"unknown lock/report status: {status}", path))
    check_support_claim(data, status, path, findings)
    return findings


def validate_lock_or_report(data: Dict[str, Any], path: str, ctx: Dict[str, Any], registries: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = validate_derived_header(data, path, registries)
    schema_id = str(data.get("schema_id") or "")
    for diagnostic in strings(data.get("diagnostics")):
        check_known(diagnostic, ctx["diagnostics"], "derived_unknown_diagnostic", "diagnostic", path, findings)
    entries = [item for item in as_list(data.get("entries")) if isinstance(item, dict)]
    if len(entries) != len(as_list(data.get("entries"))):
        findings.append(finding("error", "derived_entry_shape", "entries must contain objects", path))

    if schema_id == "dominium.lock.app_composition":
        for index, entry in enumerate(entries):
            item_path = f"{path}#entries[{index}]"
            if entry.get("app_ref"):
                check_known(str(entry["app_ref"]), ctx["apps"], "app_lock_unknown_app", "app_ref", item_path, findings)
            for profile in strings(entry.get("profiles")):
                check_known(profile, ctx["profiles"], "app_lock_unknown_profile", "profile", item_path, findings)
            for pack in strings(entry.get("packs")):
                check_known(pack, ctx["packs"], "app_lock_unknown_pack", "pack", item_path, findings)
            for module in strings(entry.get("modules")):
                check_known(module, ctx["modules"], "app_lock_unknown_module", "module", item_path, findings)
            for provider in strings(entry.get("providers")):
                check_known(provider, ctx["provider_ids"], "app_lock_unknown_provider", "provider", item_path, findings)

    if schema_id == "dominium.lock.pack_mount":
        for index, entry in enumerate(entries):
            if entry.get("pack_ref"):
                check_known(str(entry["pack_ref"]), ctx["packs"], "pack_lock_unknown_pack", "pack_ref", f"{path}#entries[{index}]", findings)
        for index, overlay in enumerate(as_list(data.get("overlays"))):
            item_path = f"{path}#overlays[{index}]"
            if not isinstance(overlay, dict):
                findings.append(finding("error", "overlay_shape", "overlays must contain objects", item_path))
                continue
            behavior = str(overlay.get("conflict_behavior") or overlay.get("conflict_policy") or "")
            if behavior in FORBIDDEN_OVERLAY_BEHAVIORS:
                findings.append(finding("error", "silent_overlay_forbidden", f"forbidden overlay conflict behavior: {behavior}", item_path))
            if len(strings(overlay.get("contributors"))) > 1 and not behavior:
                findings.append(finding("error", "overlay_conflict_missing_behavior", "overlapping contributors require conflict behavior", item_path))

    if schema_id == "dominium.lock.module_plan":
        for index, entry in enumerate(entries):
            item_path = f"{path}#entries[{index}]"
            if entry.get("module_ref"):
                check_known(str(entry["module_ref"]), ctx["modules"], "module_lock_unknown_module", "module_ref", item_path, findings)
            for cap in strings(entry.get("required_capabilities")) + strings(entry.get("optional_capabilities")):
                check_known(cap, ctx["capabilities"], "module_lock_unknown_capability", "capability", item_path, findings)
            for provider in strings(entry.get("required_providers")):
                check_known(provider, ctx["provider_ids"], "module_lock_unknown_provider", "provider", item_path, findings)

    if schema_id == "dominium.lock.provider_selection":
        for index, entry in enumerate(entries):
            item_path = f"{path}#entries[{index}]"
            if str(entry.get("provider_kind") or "") not in ctx["provider_kinds"]:
                findings.append(finding("error", "provider_lock_unknown_kind", f"unknown provider_kind: {entry.get('provider_kind')}", item_path))
            for provider in strings(entry.get("candidate_providers")) + strings(entry.get("rejected_providers")):
                check_known(provider, ctx["provider_ids"], "provider_lock_unknown_provider", "provider", item_path, findings)
            selected = str(entry.get("selected_provider") or "")
            if selected:
                check_known(selected, ctx["provider_ids"], "provider_lock_unknown_provider", "selected_provider", item_path, findings)
            required_caps = set(strings(entry.get("required_capabilities")))
            selected_caps = set(strings(entry.get("selected_capabilities")))
            for cap in sorted(required_caps | selected_caps | set(strings(entry.get("optional_capabilities")))):
                check_known(cap, ctx["capabilities"], "provider_lock_unknown_capability", "capability", item_path, findings)
            if selected and required_caps:
                provider_caps = ctx["providers"].get(selected, set())
                missing_from_selection = sorted(required_caps - selected_caps)
                missing_from_provider = sorted(required_caps - provider_caps)
                if missing_from_selection:
                    findings.append(finding("error", "selected_provider_missing_required_capability", f"selected_capabilities omit required capabilities: {', '.join(missing_from_selection)}", item_path))
                if missing_from_provider:
                    findings.append(finding("error", "selected_provider_descriptor_missing_capability", f"selected provider does not declare required capabilities: {', '.join(missing_from_provider)}", item_path))
            if entry.get("degradation") and not as_list(entry.get("fallback_trace")) and str(data.get("status")) == "degraded":
                findings.append(finding("error", "provider_degraded_missing_fallback_trace", "degraded provider lock entries require fallback_trace", item_path))

    if schema_id == "dominium.report.capability":
        for index, entry in enumerate(entries):
            item_path = f"{path}#entries[{index}]"
            for key in ["requested", "selected"]:
                value = entry.get(key)
                if isinstance(value, str) and value:
                    check_known(value, ctx["capabilities"], "capability_report_unknown_capability", key, item_path, findings)
            for key in ["available", "missing", "degraded", "refused"]:
                for cap in strings(entry.get(key)):
                    check_known(cap, ctx["capabilities"], "capability_report_unknown_capability", key, item_path, findings)

    if schema_id == "dominium.report.refusal":
        for index, entry in enumerate(entries):
            item_path = f"{path}#entries[{index}]"
            refusal = str(entry.get("refusal_code") or "")
            if not refusal:
                findings.append(finding("error", "refusal_report_missing_refusal_code", "refusal report entry requires refusal_code", item_path))
            else:
                check_known(refusal, ctx["refusals"], "refusal_report_unknown_refusal", "refusal_code", item_path, findings)
            diagnostics = strings(entry.get("diagnostic_codes"))
            if not diagnostics:
                findings.append(finding("error", "refusal_report_missing_diagnostic", "refusal report entry requires diagnostic_codes", item_path))
            for diagnostic in diagnostics:
                check_known(diagnostic, ctx["diagnostics"], "refusal_report_unknown_diagnostic", "diagnostic_code", item_path, findings)

    if schema_id == "dominium.report.trust":
        for index, entry in enumerate(entries):
            value = entry.get("trust_level")
            if isinstance(value, str) and value:
                check_known(value, ctx["trust_levels"], "trust_report_unknown_trust_level", "trust_level", f"{path}#entries[{index}]", findings)

    return findings


def validate_fixture_file(path: Path, repo_root: Path, ctx: Dict[str, Any], registries: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    rel = path.relative_to(repo_root).as_posix()
    try:
        data = load_json(path)
    except Exception as exc:
        return False, [finding("error", "fixture_invalid_json", f"fixture does not parse: {exc}", rel)]
    if not isinstance(data, dict):
        return False, [finding("error", "fixture_root_not_object", "fixture root must be an object", rel)]
    schema_id = str(data.get("schema_id") or "")
    if schema_id == "dominium.composition.plan":
        item_findings = validate_plan(data, rel, ctx, registries)
    elif schema_id == "dominium.composition.decision":
        item_findings = validate_decision(data, rel, ctx, registries)
    elif schema_id == "dominium.profile.composition":
        item_findings = validate_profile(data, rel, ctx)
    elif schema_id in SCHEMA_ID_TO_LOCK_SCHEMA:
        item_findings = validate_lock_or_report(data, rel, ctx, registries)
    else:
        item_findings = [finding("error", "fixture_unknown_schema_id", f"unknown schema_id: {schema_id}", rel)]
    return not has_error(item_findings), item_findings


def validate_fixtures(repo_root: Path, ctx: Dict[str, Any], registries: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []
    fixture_dirs = [COMPOSITION_FIXTURE_DIR_REL, LOCK_FIXTURE_DIR_REL, PROFILE_FIXTURE_DIR_REL]
    for rel_dir in fixture_dirs:
        fixture_dir = repo_root / rel_dir
        if not fixture_dir.exists():
            findings.append(finding("error", "fixture_dir_missing", f"missing fixture directory: {rel_dir.as_posix()}", rel_dir.as_posix()))
            continue
        for path in sorted(fixture_dir.glob("*.json")):
            expected_invalid = path.name.startswith("invalid_")
            passed, item_findings = validate_fixture_file(path, repo_root, ctx, registries)
            expectation_met = (not passed) if expected_invalid else passed
            rel = path.relative_to(repo_root).as_posix()
            if not expectation_met:
                findings.append(finding("error", "fixture_expectation_failed", f"fixture expectation failed: {rel}", rel))
            results.append({
                "path": rel,
                "expected": "invalid" if expected_invalid else "valid",
                "status": "pass" if expectation_met else "fail",
                "errors": sum(1 for item in item_findings if item["level"] == "error"),
                "findings": item_findings,
            })
    return findings, {
        "status": "pass" if not findings else "fail",
        "fixture_count": len(results),
        "fixtures": results,
    }


def git_ls_files(repo_root: Path) -> List[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=str(repo_root),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def build_inventory(repo_root: Path) -> Dict[str, Any]:
    categories: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}

    def add(category: str, path: str) -> None:
        categories[category] = categories.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 10:
            examples[category].append(path)

    for path in git_ls_files(repo_root):
        lowered = path.lower()
        if lowered.startswith("contracts/composition/"):
            add("composition_contract", path)
        elif lowered.startswith("contracts/lock/"):
            add("lock_report_schema", path)
        elif lowered.startswith("contracts/profile/"):
            add("profile_contract", path)
        elif lowered.startswith("contracts/package/"):
            add("package_contract_or_lock", path)
        elif lowered.startswith("contracts/provider/"):
            add("provider_contract", path)
        elif lowered.startswith("contracts/module/"):
            add("module_contract", path)
        elif lowered.startswith("contracts/capability/"):
            add("capability_contract", path)
        elif lowered.startswith(("tests/contract/composition/", "tests/contract/lock/", "tests/contract/profile/")):
            add("composition_fixture", path)
        elif lowered.startswith("docs/architecture/") and "composition" in lowered:
            add("composition_doc", path)
    return {
        "status": "warning",
        "files_scanned": len(git_ls_files(repo_root)),
        "categories": categories,
        "examples": examples,
        "note": "Inventory is descriptive only; this validator does not implement a runtime composition resolver.",
    }


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> Dict[str, Any]:
    findings, registries = validate_contracts(repo_root)
    ctx = build_context(repo_root)
    fixtures = {"status": "not_run", "fixture_count": 0, "fixtures": []}
    if include_fixtures:
        fixture_findings, fixtures = validate_fixtures(repo_root, ctx, registries)
        findings.extend(fixture_findings)
    inventory = build_inventory(repo_root) if include_inventory else {"status": "not_run"}
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_composition_plan",
        "status": "pass" if not errors else "fail",
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "registered": {
            "apps": len(ctx["apps"]),
            "profiles": len(ctx["profiles"]),
            "packs": len(ctx["packs"]),
            "modules": len(ctx["modules"]),
            "providers": len(ctx["provider_ids"]),
            "provider_kinds": len(ctx["provider_kinds"]),
            "capabilities": len(ctx["capabilities"]),
            "refusals": len(ctx["refusals"]),
            "diagnostics": len(ctx["diagnostics"]),
            "trust_levels": len(ctx["trust_levels"]),
        },
        "findings": findings,
        "fixtures": fixtures,
        "inventory": inventory,
    }


def print_text(result: Dict[str, Any]) -> None:
    print(f"composition plan: {result['status']}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
    reg = result.get("registered", {})
    print("registered: " + ", ".join(f"{key}={value}" for key, value in sorted(reg.items())))
    fixtures = result.get("fixtures", {})
    if fixtures.get("status") != "not_run":
        print(f"fixtures: {fixtures.get('status')} count={fixtures.get('fixture_count', 0)}")
    inventory = result.get("inventory", {})
    if inventory.get("status") != "not_run":
        print(f"inventory: {inventory.get('status')} files_scanned={inventory.get('files_scanned', 0)}")
    for item in result.get("findings", []):
        path = f"{item.get('path')}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on validation errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fixtures", action="store_true", help="Validate composition fixtures")
    parser.add_argument("--inventory", action="store_true", help="Inventory composition-adjacent surfaces")
    args = parser.parse_args(argv)

    result = validate_all(
        Path(args.repo_root).resolve(),
        include_fixtures=args.fixtures or args.strict,
        include_inventory=args.inventory,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
