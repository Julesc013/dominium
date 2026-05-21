#!/usr/bin/env python3
"""Validate Dominium service conformance law contracts and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on older Python
    tomllib = None


SERVICE_CONTRACT_REL = Path("contracts/service/service_conformance.contract.toml")
SERVICE_SCHEMA_REL = Path("contracts/service/service_conformance.schema.json")
SERVICE_CLASS_REGISTRY_REL = Path("contracts/service/service_class.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/service_conformance/fixtures")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
MODULE_CONTRACT_REL = Path("contracts/module/module_surface.contract.toml")

EXPECTED_CONTRACT_ID = "dominium.service.conformance.v1"
EXPECTED_SCHEMA_ID = "dominium.service.conformance.v1"
EXPECTED_SCHEMA_VERSION = "1.0.0"
EXPECTED_SERVICE_CLASSES = {
    "execution_coordination",
    "observation_inspection",
    "presentation_support",
    "control_integration",
    "persistence_replay_support",
    "compatibility_policy_support",
    "domain_support",
    "product_support",
}

SERVICE_ID_RE = re.compile(r"^service\.[a-z0-9][a-z0-9_.-]*$")
PATHLIKE_RE = re.compile(r"[/\\]|^[A-Za-z]:|\.{2}|\.json$|\.toml$|\.py$|\.exe$", re.IGNORECASE)
DOM_REFUSAL_RE = re.compile(r"^dominium\.refusal\.[a-z0-9][a-z0-9_.-]+$")
DOM_DIAGNOSTIC_RE = re.compile(r"^DOM-[A-Z0-9]+(?:-[A-Z0-9]+)*$")


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


def _logical_toml_lines(text: str) -> List[Tuple[int, str]]:
    logical: List[Tuple[int, str]] = []
    pending: List[str] = []
    start_lineno = 0
    depth = 0
    in_quote = False
    escaped = False
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line and not pending:
            continue
        if pending:
            pending.append(line)
        else:
            pending = [line]
            start_lineno = lineno
        for ch in line:
            if escaped:
                escaped = False
                continue
            if ch == "\\" and in_quote:
                escaped = True
                continue
            if ch == '"':
                in_quote = not in_quote
                continue
            if not in_quote:
                if ch == "[":
                    depth += 1
                elif ch == "]" and depth:
                    depth -= 1
        if depth == 0 and not in_quote:
            merged = " ".join(part for part in pending if part).strip()
            if merged:
                logical.append((start_lineno, merged))
            pending = []
    if pending:
        logical.append((start_lineno, " ".join(pending).strip()))
    return logical


def _minimal_toml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
    for lineno, line in _logical_toml_lines(text):
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
            raise ValueError(f"invalid TOML line {lineno}: {line}")
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


def string_set(values: Iterable[Any]) -> Set[str]:
    return {str(value) for value in values if isinstance(value, str) and value}


def finding(level: str, code: str, message: str, path: Optional[str] = None, service_id: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    if service_id:
        item["service_id"] = service_id
    return item


def path_exists(repo_root: Path, raw_path: str) -> bool:
    path = Path(raw_path)
    if path.is_absolute():
        return path.exists()
    return (repo_root / path).exists()


def registry_service_classes(registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(registry.get("classes"))
        if isinstance(item, dict) and item.get("id")
    }


def registry_refusals(registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("code") or item.get("refusal_id"))
        for item in as_list(registry.get("codes"))
        if isinstance(item, dict) and (item.get("code") or item.get("refusal_id"))
    }


def registry_diagnostic_codes(registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("code"))
        for item in as_list(registry.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def registry_capabilities(registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("capability_id"))
        for item in as_list(registry.get("capabilities"))
        if isinstance(item, dict) and item.get("capability_id")
    }


def contract_commands(contract: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(contract.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


def contract_modules(contract: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("module_id"))
        for item in as_list(contract.get("module"))
        if isinstance(item, dict) and item.get("module_id")
    }


def validate_contract_surfaces(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    loaded: Dict[str, Any] = {}

    for rel in [SERVICE_CONTRACT_REL, SERVICE_SCHEMA_REL, SERVICE_CLASS_REGISTRY_REL]:
        if not (repo_root / rel).exists():
            findings.append(finding("error", "service_surface_missing", f"required service conformance surface is missing: {rel.as_posix()}", rel.as_posix()))

    try:
        contract = load_toml(repo_root / SERVICE_CONTRACT_REL)
        loaded["contract"] = contract
    except Exception as exc:
        findings.append(finding("error", "service_contract_invalid_toml", f"{SERVICE_CONTRACT_REL.as_posix()} does not parse as TOML: {exc}", SERVICE_CONTRACT_REL.as_posix()))
        contract = {}

    try:
        schema = load_json(repo_root / SERVICE_SCHEMA_REL)
        loaded["schema"] = schema
    except Exception as exc:
        findings.append(finding("error", "service_schema_invalid_json", f"{SERVICE_SCHEMA_REL.as_posix()} does not parse as JSON: {exc}", SERVICE_SCHEMA_REL.as_posix()))
        schema = {}

    try:
        class_registry = load_json(repo_root / SERVICE_CLASS_REGISTRY_REL)
        loaded["class_registry"] = class_registry
    except Exception as exc:
        findings.append(finding("error", "service_class_registry_invalid_json", f"{SERVICE_CLASS_REGISTRY_REL.as_posix()} does not parse as JSON: {exc}", SERVICE_CLASS_REGISTRY_REL.as_posix()))
        class_registry = {}

    if contract:
        if contract.get("contract", {}).get("id") != EXPECTED_CONTRACT_ID:
            findings.append(finding("error", "service_contract_bad_id", "service conformance contract id is unexpected", SERVICE_CONTRACT_REL.as_posix()))
        policy = contract.get("policy", {})
        expected_false = [
            "runtime_implementation_authorized",
            "provider_calls_authorized",
            "product_feature_authorized",
            "services_are_semantic_owners",
            "services_are_product_owners",
            "services_may_mutate_truth_directly",
            "silent_migration_allowed",
            "projection_may_redefine_schema_law",
        ]
        for key in expected_false:
            if policy.get(key) is not False:
                findings.append(finding("error", "service_contract_policy_drift", f"policy.{key} must be false", SERVICE_CONTRACT_REL.as_posix()))
        expected_true = [
            "truth_mutation_requires_process",
            "truth_perceived_render_separation_required",
            "capability_gating_required",
            "deterministic_refusal_or_degradation_required",
        ]
        for key in expected_true:
            if policy.get(key) is not True:
                findings.append(finding("error", "service_contract_policy_drift", f"policy.{key} must be true", SERVICE_CONTRACT_REL.as_posix()))
        for key in ["schema", "service_class_registry"]:
            raw_path = str(contract.get("contract", {}).get(key, ""))
            if raw_path and not path_exists(repo_root, raw_path):
                findings.append(finding("error", "service_contract_missing_reference", f"contract reference does not exist: {raw_path}", SERVICE_CONTRACT_REL.as_posix()))
        for raw_path in string_set(contract.get("required", {}).get("doctrine", [])):
            if not path_exists(repo_root, raw_path):
                findings.append(finding("error", "service_required_doctrine_missing", f"required doctrine path does not exist: {raw_path}", SERVICE_CONTRACT_REL.as_posix()))

    if schema:
        if schema.get("$id") != EXPECTED_SCHEMA_ID:
            findings.append(finding("error", "service_schema_bad_id", "service conformance schema $id is unexpected", SERVICE_SCHEMA_REL.as_posix()))
        required = string_set(schema.get("required", []))
        for key in ["schema_id", "schema_version", "service_id", "service_law", "required_constraints", "upstream_doctrine", "interfaces", "diagnostics", "proof"]:
            if key not in required:
                findings.append(finding("error", "service_schema_missing_required_key", f"schema required list must include {key}", SERVICE_SCHEMA_REL.as_posix()))

    if class_registry:
        if class_registry.get("schema_id") != "dominium.service.class.registry.v1":
            findings.append(finding("error", "service_class_registry_bad_id", "service class registry schema_id is unexpected", SERVICE_CLASS_REGISTRY_REL.as_posix()))
        actual_classes = registry_service_classes(class_registry)
        missing_classes = sorted(EXPECTED_SERVICE_CLASSES - actual_classes)
        extra_classes = sorted(actual_classes - EXPECTED_SERVICE_CLASSES)
        if missing_classes:
            findings.append(finding("error", "service_class_registry_missing_class", f"missing service classes: {', '.join(missing_classes)}", SERVICE_CLASS_REGISTRY_REL.as_posix()))
        if extra_classes:
            findings.append(finding("warning", "service_class_registry_extra_class", f"extra service classes require doctrine review: {', '.join(extra_classes)}", SERVICE_CLASS_REGISTRY_REL.as_posix()))

    return findings, loaded


def load_optional_surfaces(repo_root: Path) -> Dict[str, Set[str]]:
    surfaces: Dict[str, Set[str]] = {
        "refusals": set(),
        "diagnostics": set(),
        "capabilities": set(),
        "commands": set(),
        "modules": set(),
    }
    try:
        surfaces["refusals"] = registry_refusals(load_json(repo_root / REFUSAL_REGISTRY_REL))
    except Exception:
        pass
    try:
        surfaces["diagnostics"] = registry_diagnostic_codes(load_json(repo_root / DIAGNOSTIC_REGISTRY_REL))
    except Exception:
        pass
    try:
        surfaces["capabilities"] = registry_capabilities(load_json(repo_root / CAPABILITY_REGISTRY_REL))
    except Exception:
        pass
    try:
        surfaces["commands"] = contract_commands(load_toml(repo_root / COMMAND_CONTRACT_REL))
    except Exception:
        pass
    try:
        surfaces["modules"] = contract_modules(load_toml(repo_root / MODULE_CONTRACT_REL))
    except Exception:
        pass
    return surfaces


def validate_service_descriptor(
    data: Dict[str, Any],
    *,
    path: str,
    contract: Dict[str, Any],
    service_classes: Set[str],
    known_surfaces: Dict[str, Set[str]],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    service_id = str(data.get("service_id") or "")

    required_top = [
        "schema_id",
        "schema_version",
        "service_id",
        "owner",
        "version",
        "stability",
        "service_class",
        "required_constraints",
        "upstream_doctrine",
        "service_law",
        "determinism",
        "compatibility",
        "interfaces",
        "diagnostics",
        "proof",
    ]
    for key in required_top:
        if key not in data:
            findings.append(finding("error", "service_missing_field", f"service declaration is missing required field {key}", path, service_id))

    if data.get("schema_id") != EXPECTED_SCHEMA_ID:
        findings.append(finding("error", "service_bad_schema_id", "schema_id must be dominium.service.conformance.v1", path, service_id))
    if data.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "service_bad_schema_version", "schema_version must be 1.0.0", path, service_id))

    if not service_id or not SERVICE_ID_RE.match(service_id) or PATHLIKE_RE.search(service_id):
        findings.append(finding("error", "service_bad_id", f"service_id is not governed service.* identity: {service_id}", path, service_id))

    for key in ["owner", "version", "stability", "service_class"]:
        if not isinstance(data.get(key), str) or not data.get(key):
            findings.append(finding("error", "service_bad_field", f"{key} must be a non-empty string", path, service_id))

    allowed = contract.get("allowed", {})
    stability = str(data.get("stability") or "")
    if stability and stability not in string_set(allowed.get("stability", [])):
        findings.append(finding("error", "service_bad_stability", f"unsupported service stability: {stability}", path, service_id))

    service_class = str(data.get("service_class") or "")
    if service_class and service_class not in service_classes:
        findings.append(finding("error", "service_bad_class", f"unknown service_class: {service_class}", path, service_id))

    declared_constraints = string_set(data.get("required_constraints", []))
    required_constraints = string_set(contract.get("required", {}).get("constraints", []))
    missing_constraints = sorted(required_constraints - declared_constraints)
    unknown_constraints = sorted(declared_constraints - required_constraints)
    if missing_constraints:
        findings.append(finding("error", "service_missing_required_constraint", f"missing required constraints: {', '.join(missing_constraints)}", path, service_id))
    if unknown_constraints:
        findings.append(finding("error", "service_unknown_constraint", f"unknown service constraints: {', '.join(unknown_constraints)}", path, service_id))

    declared_doctrine = string_set(data.get("upstream_doctrine", []))
    required_doctrine = string_set(contract.get("required", {}).get("doctrine", []))
    missing_doctrine = sorted(required_doctrine - declared_doctrine)
    if missing_doctrine:
        findings.append(finding("error", "service_missing_required_doctrine", f"missing required doctrine refs: {', '.join(missing_doctrine)}", path, service_id))

    service_law = data.get("service_law")
    if not isinstance(service_law, dict):
        findings.append(finding("error", "service_law_shape", "service_law must be an object", path, service_id))
        service_law = {}

    false_law = [
        "runtime_implementation_authorized",
        "provider_calls_authorized",
        "product_feature_authorized",
        "owns_truth",
        "owns_semantic_doctrine",
        "owns_product_shell",
        "silent_migration_allowed",
        "projection_redefines_schema_law",
    ]
    for key in false_law:
        if service_law.get(key) is not False:
            findings.append(finding("error", "service_law_forbidden_true", f"service_law.{key} must be false", path, service_id))

    true_law = [
        "truth_perceived_render_separation",
        "capability_gated",
        "deterministic_refusal_or_degradation",
    ]
    for key in true_law:
        if service_law.get(key) is not True:
            findings.append(finding("error", "service_law_required_true", f"service_law.{key} must be true", path, service_id))

    truth_mutation = str(service_law.get("truth_mutation") or "")
    if truth_mutation not in string_set(allowed.get("truth_mutation", [])):
        findings.append(finding("error", "service_bad_truth_mutation", f"unsupported truth_mutation: {truth_mutation}", path, service_id))
    missing_capability_behavior = str(service_law.get("missing_capability_behavior") or "")
    if missing_capability_behavior not in string_set(allowed.get("missing_capability_behavior", [])):
        findings.append(finding("error", "service_bad_missing_capability_behavior", f"unsupported missing_capability_behavior: {missing_capability_behavior}", path, service_id))

    determinism = data.get("determinism")
    if not isinstance(determinism, dict):
        findings.append(finding("error", "service_determinism_shape", "determinism must be an object", path, service_id))
        determinism = {}
    if determinism.get("ordering") not in string_set(allowed.get("ordering", [])):
        findings.append(finding("error", "service_bad_ordering", "determinism.ordering must be deterministic_declared", path, service_id))
    if determinism.get("thread_count_invariant") is not True:
        findings.append(finding("error", "service_thread_count_not_invariant", "determinism.thread_count_invariant must be true", path, service_id))
    if determinism.get("named_rng_streams") not in string_set(allowed.get("named_rng_streams", [])):
        findings.append(finding("error", "service_bad_rng_policy", "determinism.named_rng_streams must be none or declared", path, service_id))

    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict):
        findings.append(finding("error", "service_compatibility_shape", "compatibility must be an object", path, service_id))
        compatibility = {}
    if compatibility.get("schema_impact") not in string_set(allowed.get("schema_impact", [])):
        findings.append(finding("error", "service_bad_schema_impact", "compatibility.schema_impact must be declared", path, service_id))
    if not compatibility.get("migration_policy"):
        findings.append(finding("error", "service_missing_migration_policy", "compatibility.migration_policy is required", path, service_id))
    if not compatibility.get("replacement_policy"):
        findings.append(finding("error", "service_missing_replacement_policy", "compatibility.replacement_policy is required", path, service_id))

    interfaces = data.get("interfaces")
    if not isinstance(interfaces, dict):
        findings.append(finding("error", "service_interfaces_shape", "interfaces must be an object", path, service_id))
        interfaces = {}
    capabilities = string_set(interfaces.get("capabilities", []))
    refusals = string_set(interfaces.get("refusals", []))
    commands = string_set(interfaces.get("commands", []))
    modules = string_set(interfaces.get("modules", []))

    if capabilities and not refusals:
        findings.append(finding("error", "service_capability_without_refusal", "services with capabilities must declare refusal codes", path, service_id))
    if missing_capability_behavior == "typed_refusal" and not refusals:
        findings.append(finding("error", "service_typed_refusal_missing_codes", "typed_refusal behavior requires refusal codes", path, service_id))

    for refusal in sorted(refusals):
        if not DOM_REFUSAL_RE.match(refusal):
            findings.append(finding("error", "service_bad_refusal_id", f"refusal id must be dominium.refusal.*: {refusal}", path, service_id))
    unknown_refusals = sorted(refusals - known_surfaces["refusals"])
    if known_surfaces["refusals"] and unknown_refusals:
        findings.append(finding("error", "service_unknown_refusal", f"unknown refusal codes: {', '.join(unknown_refusals)}", path, service_id))

    unknown_capabilities = sorted(capabilities - known_surfaces["capabilities"])
    if known_surfaces["capabilities"] and unknown_capabilities:
        findings.append(finding("error", "service_unknown_capability", f"unknown capabilities: {', '.join(unknown_capabilities)}", path, service_id))

    unknown_commands = sorted(commands - known_surfaces["commands"])
    if known_surfaces["commands"] and unknown_commands:
        findings.append(finding("error", "service_unknown_command", f"unknown commands: {', '.join(unknown_commands)}", path, service_id))

    unknown_modules = sorted(modules - known_surfaces["modules"])
    if known_surfaces["modules"] and unknown_modules:
        findings.append(finding("error", "service_unknown_module", f"unknown modules: {', '.join(unknown_modules)}", path, service_id))

    diagnostics = string_set(data.get("diagnostics", []))
    if not diagnostics:
        findings.append(finding("error", "service_missing_diagnostics", "diagnostics must declare at least one DOM-* code", path, service_id))
    for diagnostic in sorted(diagnostics):
        if not DOM_DIAGNOSTIC_RE.match(diagnostic):
            findings.append(finding("error", "service_bad_diagnostic_code", f"diagnostic must be DOM-* uppercase code: {diagnostic}", path, service_id))
    unknown_diagnostics = sorted(diagnostics - known_surfaces["diagnostics"])
    if known_surfaces["diagnostics"] and unknown_diagnostics:
        findings.append(finding("error", "service_unknown_diagnostic", f"unknown diagnostics: {', '.join(unknown_diagnostics)}", path, service_id))

    if not string_set(data.get("proof", [])):
        findings.append(finding("error", "service_missing_proof", "service conformance declarations must carry proof commands or evidence refs", path, service_id))

    return findings


def fixture_paths(repo_root: Path) -> List[Path]:
    return sorted((repo_root / FIXTURE_DIR_REL).glob("*.json"))


def validate_fixture_files(repo_root: Path, contract: Dict[str, Any], service_classes: Set[str], known_surfaces: Dict[str, Set[str]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []
    paths = fixture_paths(repo_root)
    if not paths:
        return [finding("error", "service_fixture_dir_empty", f"no service conformance fixtures found under {FIXTURE_DIR_REL.as_posix()}")], {"status": "fail", "fixture_count": 0, "valid": 0, "invalid": 0, "fixtures": []}

    valid_count = 0
    invalid_count = 0
    for path in paths:
        rel = path.relative_to(repo_root).as_posix()
        expect_invalid = path.name.startswith("invalid_")
        if expect_invalid:
            invalid_count += 1
        else:
            valid_count += 1
        try:
            data = load_json(path)
            if not isinstance(data, dict):
                item_findings = [finding("error", "service_fixture_root", "fixture root must be a JSON object", rel)]
            else:
                item_findings = validate_service_descriptor(data, path=rel, contract=contract, service_classes=service_classes, known_surfaces=known_surfaces)
        except Exception as exc:
            item_findings = [finding("error", "service_fixture_invalid_json", f"fixture does not parse as JSON: {exc}", rel)]
        error_count = sum(1 for item in item_findings if item.get("level") == "error")
        passed_expectation = bool(error_count) == expect_invalid
        status = "pass" if passed_expectation else "fail"
        if not passed_expectation:
            if expect_invalid:
                findings.append(finding("error", "service_invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
            else:
                findings.append(finding("error", "service_valid_fixture_failed", f"valid fixture failed validation: {rel}", rel))
        results.append({
            "fixture": rel,
            "expected": "invalid" if expect_invalid else "valid",
            "status": status,
            "errors": error_count,
            "findings": item_findings,
        })

    if not valid_count or not invalid_count:
        findings.append(finding("error", "service_fixture_set_incomplete", "service conformance fixtures must include valid and invalid cases"))

    return findings, {
        "status": "pass" if not findings else "fail",
        "fixture_count": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "fixtures": results,
    }


def summarize(findings: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "errors": sum(1 for item in findings if item.get("level") == "error"),
        "warnings": sum(1 for item in findings if item.get("level") == "warning"),
    }


def validate_all(repo_root: Path, include_fixtures: bool) -> Dict[str, Any]:
    findings, loaded = validate_contract_surfaces(repo_root)
    contract = loaded.get("contract", {})
    class_registry = loaded.get("class_registry", {})
    service_classes = registry_service_classes(class_registry) if isinstance(class_registry, dict) else set()
    known_surfaces = load_optional_surfaces(repo_root)
    fixtures: Dict[str, Any] = {"status": "not_run", "fixture_count": 0, "valid": 0, "invalid": 0, "fixtures": []}
    if include_fixtures:
        fixture_findings, fixtures = validate_fixture_files(repo_root, contract, service_classes, known_surfaces)
        findings.extend(fixture_findings)
    counts = summarize(findings)
    return {
        "validator": "check_service_conformance",
        "status": "fail" if counts["errors"] else "pass",
        "contract": SERVICE_CONTRACT_REL.as_posix(),
        "schema": SERVICE_SCHEMA_REL.as_posix(),
        "service_class_registry": SERVICE_CLASS_REGISTRY_REL.as_posix(),
        "service_classes": sorted(service_classes),
        "summary": counts,
        "findings": findings,
        "fixtures": fixtures,
    }


def print_list(service_classes: Sequence[str]) -> None:
    for service_class in service_classes:
        print(service_class)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Return nonzero on validation errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--fixtures", action="store_true", help="Validate service conformance fixtures")
    parser.add_argument("--list-classes", action="store_true", help="List registered service classes")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    result = validate_all(repo_root, include_fixtures=args.fixtures)
    if args.list_classes:
        print_list(result["service_classes"])
    elif args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"service_conformance: {result['status']}")
        print(f"service_classes: {len(result['service_classes'])}")
        print(f"errors: {result['summary']['errors']}")
        print(f"warnings: {result['summary']['warnings']}")
        if args.fixtures:
            fixtures = result["fixtures"]
            print(f"fixtures: {fixtures['status']} count={fixtures['fixture_count']} valid={fixtures['valid']} invalid={fixtures['invalid']}")
        for item in result["findings"]:
            print(f"{item['level'].upper()}: {item['code']}: {item['message']}")

    if args.strict and result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
