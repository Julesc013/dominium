#!/usr/bin/env python3
"""Validate Dominium provider model contracts, registries, and fixtures."""

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


PROVIDER_CONTRACT_REL = Path("contracts/provider/provider.contract.toml")
PROVIDER_SCHEMA_REL = Path("contracts/provider/provider.schema.json")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
PROVIDER_KIND_REGISTRY_REL = Path("contracts/provider/provider_kind.registry.json")
PROVIDER_LIFECYCLE_REGISTRY_REL = Path("contracts/provider/provider_lifecycle.registry.json")
PROVIDER_DESCRIPTOR_SCHEMA_REL = Path("contracts/provider/provider_descriptor.schema.json")
PROVIDER_SELECTION_REQUEST_SCHEMA_REL = Path("contracts/provider/provider_selection_request.schema.json")
PROVIDER_SELECTION_DECISION_SCHEMA_REL = Path("contracts/provider/provider_selection_decision.schema.json")
PROVIDER_CONFORMANCE_REL = Path("contracts/provider/provider_conformance.contract.toml")
PROVIDER_CAPABILITY_POLICY_REL = Path("contracts/provider/provider_capability_policy.contract.toml")
PROVIDER_TRUST_POLICY_REL = Path("contracts/provider/provider_trust_policy.contract.toml")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/provider/fixtures")

JSON_RELS = [
    PROVIDER_SCHEMA_REL,
    PROVIDER_REGISTRY_REL,
    PROVIDER_KIND_REGISTRY_REL,
    PROVIDER_LIFECYCLE_REGISTRY_REL,
    PROVIDER_DESCRIPTOR_SCHEMA_REL,
    PROVIDER_SELECTION_REQUEST_SCHEMA_REL,
    PROVIDER_SELECTION_DECISION_SCHEMA_REL,
]
TOML_RELS = [
    PROVIDER_CONTRACT_REL,
    PROVIDER_CONFORMANCE_REL,
    PROVIDER_CAPABILITY_POLICY_REL,
    PROVIDER_TRUST_POLICY_REL,
]
EXPECTED_CONTRACT_IDS = {
    PROVIDER_CONTRACT_REL: "dominium.provider.model.v1",
    PROVIDER_CONFORMANCE_REL: "dominium.provider.conformance.v1",
    PROVIDER_CAPABILITY_POLICY_REL: "dominium.provider.capability_policy.v1",
    PROVIDER_TRUST_POLICY_REL: "dominium.provider.trust_policy.v1",
}
PROVIDER_ID_RE = re.compile(r"^(domino|dominium)\.provider(\.[a-z0-9][a-z0-9_-]*)+$")


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


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def registry_ids(data: Dict[str, Any], key: str, id_key: str = "id") -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def read_provider_vocab(repo_root: Path) -> Tuple[Set[str], Set[str], Set[str], Set[str], Set[str]]:
    kinds = load_json(repo_root / PROVIDER_KIND_REGISTRY_REL)
    lifecycle = load_json(repo_root / PROVIDER_LIFECYCLE_REGISTRY_REL)
    return (
        registry_ids(kinds, "kinds"),
        {str(v) for v in as_list(kinds.get("decision_values")) if isinstance(v, str)},
        {str(v) for v in as_list(lifecycle.get("lifecycle_states")) if isinstance(v, str)},
        {str(v) for v in as_list(lifecycle.get("trust_levels")) if isinstance(v, str)},
        {str(v) for v in as_list(kinds.get("abi_values")) if isinstance(v, str)},
    )


def read_capability_ids(repo_root: Path) -> Set[str]:
    path = repo_root / CAPABILITY_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("capability_id"))
        for item in as_list(data.get("capabilities"))
        if isinstance(item, dict) and item.get("capability_id")
    }


def read_refusal_codes(repo_root: Path) -> Set[str]:
    path = repo_root / REFUSAL_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def read_diagnostic_codes(repo_root: Path) -> Set[str]:
    path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def validate_json_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json_contract", f"missing JSON contract: {rel.as_posix()}"))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}"))
            continue
        if not isinstance(data, dict):
            findings.append(finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object"))
    return findings


def validate_toml_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in TOML_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_toml_contract", f"missing TOML contract: {rel.as_posix()}"))
            continue
        try:
            data = load_toml(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_toml", f"{rel.as_posix()} does not parse as TOML: {exc}"))
            continue
        contract = data.get("contract", {})
        if not isinstance(contract, dict) or contract.get("id") != EXPECTED_CONTRACT_IDS[rel]:
            findings.append(finding("error", "unexpected_contract_id", f"{rel.as_posix()} has unexpected or missing contract id"))
    return findings


def path_like_provider_id(provider_id: str) -> bool:
    lowered = provider_id.lower()
    return (
        "/" in provider_id
        or "\\" in provider_id
        or ":" in provider_id
        or lowered.endswith((".json", ".toml", ".py", ".c", ".cpp", ".h", ".hpp"))
    )


def validate_provider_descriptor(
    provider: Dict[str, Any],
    *,
    path: str,
    kinds: Set[str],
    lifecycle: Set[str],
    trust_levels: Set[str],
    abi_values: Set[str],
    capability_ids: Set[str],
    refusal_codes: Set[str],
    diagnostic_codes: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    provider_id = str(provider.get("provider_id") or "")
    if not provider_id:
        findings.append(finding("error", "provider_missing_id", "provider is missing provider_id", path))
    elif not PROVIDER_ID_RE.match(provider_id):
        findings.append(finding("error", "provider_bad_id", f"provider_id is not lowercase dotted provider id: {provider_id}", path))
    elif path_like_provider_id(provider_id):
        findings.append(finding("error", "provider_path_as_id", f"provider_id must not be path-like: {provider_id}", path))

    kind = str(provider.get("provider_kind") or "")
    if kind not in kinds:
        findings.append(finding("error", "provider_unknown_kind", f"unknown provider_kind: {kind}", path))

    if not provider.get("owner"):
        findings.append(finding("error", "provider_missing_owner", "provider owner is required", path))

    stability = str(provider.get("stability") or "")
    if stability not in lifecycle:
        findings.append(finding("error", "provider_unknown_stability", f"unknown provider stability: {stability}", path))

    provided = [str(item) for item in as_list(provider.get("capabilities_provided")) if item]
    if not provided:
        findings.append(finding("error", "provider_missing_capability", "provider must declare at least one capability provided", path))
    if capability_ids:
        for capability_id in provided + [str(item) for item in as_list(provider.get("capabilities_required")) if item]:
            if capability_id not in capability_ids:
                findings.append(finding("error", "provider_unknown_capability", f"provider references unknown capability: {capability_id}", path))

    trust_level = str(provider.get("trust_level") or "")
    if trust_level not in trust_levels:
        findings.append(finding("error", "provider_unknown_trust_level", f"unknown provider trust_level: {trust_level}", path))

    abi = str(provider.get("abi") or "")
    if abi not in abi_values:
        findings.append(finding("error", "provider_unknown_abi", f"unknown provider ABI value: {abi}", path))

    if provider.get("implementation_path_is_identity") is True:
        findings.append(finding("error", "implementation_path_as_identity", "implementation_path must be non-authoritative", path))

    conformance_tests = as_list(provider.get("conformance_tests"))
    if stability == "stable" and not conformance_tests:
        findings.append(finding("error", "stable_provider_missing_conformance", "stable provider requires conformance_tests", path))

    if refusal_codes:
        for refusal_code in [str(item) for item in as_list(provider.get("refusal_codes")) if item]:
            if refusal_code not in refusal_codes:
                findings.append(finding("error", "provider_unknown_refusal", f"provider references unknown refusal code: {refusal_code}", path))

    if diagnostic_codes:
        for diagnostic_code in [str(item) for item in as_list(provider.get("diagnostic_codes")) if item]:
            if diagnostic_code not in diagnostic_codes:
                findings.append(finding("error", "provider_unknown_diagnostic", f"provider references unknown diagnostic code: {diagnostic_code}", path))

    return findings


def validate_provider_registry(repo_root: Path) -> Tuple[List[Dict[str, Any]], int]:
    findings: List[Dict[str, Any]] = []
    try:
        kinds, _, lifecycle, trust_levels, abi_values = read_provider_vocab(repo_root)
        capability_ids = read_capability_ids(repo_root)
        refusal_codes = read_refusal_codes(repo_root)
        diagnostic_codes = read_diagnostic_codes(repo_root)
        data = load_json(repo_root / PROVIDER_REGISTRY_REL)
    except Exception as exc:
        return [finding("error", "provider_registry_unreadable", f"provider registry cannot be read: {exc}")], 0

    providers = [item for item in as_list(data.get("providers")) if isinstance(item, dict)]
    seen: Set[str] = set()
    for index, provider in enumerate(providers):
        provider_id = str(provider.get("provider_id") or "")
        if provider_id:
            if provider_id in seen:
                findings.append(finding("error", "duplicate_provider_id", f"duplicate provider_id: {provider_id}", PROVIDER_REGISTRY_REL.as_posix()))
            seen.add(provider_id)
        findings.extend(validate_provider_descriptor(
            provider,
            path=f"{PROVIDER_REGISTRY_REL.as_posix()}#{index}",
            kinds=kinds,
            lifecycle=lifecycle,
            trust_levels=trust_levels,
            abi_values=abi_values,
            capability_ids=capability_ids,
            refusal_codes=refusal_codes,
            diagnostic_codes=diagnostic_codes,
        ))
    return findings, len(providers)


def validate_selection_request(data: Dict[str, Any], *, path: str, kinds: Set[str], capability_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for key in ["request_id", "requested_by", "provider_kind"]:
        if not data.get(key):
            findings.append(finding("error", "selection_request_missing_field", f"selection request missing {key}", path))
    if str(data.get("provider_kind") or "") not in kinds:
        findings.append(finding("error", "selection_request_unknown_kind", f"unknown provider_kind: {data.get('provider_kind')}", path))
    for capability_id in [str(item) for item in as_list(data.get("required_capabilities")) if item]:
        if capability_ids and capability_id not in capability_ids:
            findings.append(finding("error", "selection_request_unknown_capability", f"unknown capability: {capability_id}", path))
    return findings


def validate_selection_decision(
    data: Dict[str, Any],
    *,
    path: str,
    decisions: Set[str],
    provider_ids: Set[str],
    capability_ids: Set[str],
    refusal_codes: Set[str],
    diagnostic_codes: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    decision = str(data.get("decision") or "")
    if decision not in decisions:
        findings.append(finding("error", "selection_decision_unknown", f"unknown provider selection decision: {decision}", path))
    if decision == "selected":
        if not data.get("selected_provider"):
            findings.append(finding("error", "selected_missing_provider", "selected decision requires selected_provider", path))
        if not as_list(data.get("selected_capabilities")):
            findings.append(finding("error", "selected_missing_capabilities", "selected decision requires selected_capabilities", path))
    if decision == "degraded":
        for key in ["selected_provider", "degraded_from", "degraded_to", "evidence_ref"]:
            if not data.get(key):
                findings.append(finding("error", "degraded_missing_field", f"degraded decision missing {key}", path))
        if not as_list(data.get("diagnostic_codes")):
            findings.append(finding("error", "degraded_missing_diagnostic", "degraded decision requires diagnostic_codes", path))
    if decision in {"refused", "unavailable"}:
        if not data.get("refusal_code"):
            findings.append(finding("error", "refused_missing_refusal", f"{decision} decision requires refusal_code", path))
        recovery = data.get("recovery")
        if not isinstance(recovery, dict) or not recovery.get("action"):
            findings.append(finding("error", "refused_missing_recovery", f"{decision} decision requires recovery action", path))

    selected_provider = str(data.get("selected_provider") or "")
    if selected_provider and provider_ids and selected_provider not in provider_ids:
        findings.append(finding("error", "selection_unknown_provider", f"unknown selected_provider: {selected_provider}", path))
    for provider_key in ["degraded_from", "degraded_to"]:
        provider_id = str(data.get(provider_key) or "")
        if provider_id and provider_ids and provider_id not in provider_ids:
            findings.append(finding("error", "selection_unknown_provider", f"unknown {provider_key}: {provider_id}", path))
    for capability_id in [str(item) for item in as_list(data.get("selected_capabilities")) if item]:
        if capability_ids and capability_id not in capability_ids:
            findings.append(finding("error", "selection_unknown_capability", f"unknown selected capability: {capability_id}", path))
    refusal_code = str(data.get("refusal_code") or "")
    if refusal_code and refusal_codes and refusal_code not in refusal_codes:
        findings.append(finding("error", "selection_unknown_refusal", f"unknown refusal_code: {refusal_code}", path))
    for diagnostic_code in [str(item) for item in as_list(data.get("diagnostic_codes")) if item]:
        if diagnostic_codes and diagnostic_code not in diagnostic_codes:
            findings.append(finding("error", "selection_unknown_diagnostic", f"unknown diagnostic code: {diagnostic_code}", path))
    return findings


def fixture_kind(path: Path, data: Dict[str, Any]) -> str:
    explicit = data.get("fixture_kind")
    if isinstance(explicit, str):
        return explicit
    name = path.name
    if "selection_request" in name:
        return "selection_request"
    if "selection_" in name:
        return "selection_decision"
    return "provider_descriptor"


def validate_fixtures(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    fixture_dir = repo_root / FIXTURE_DIR_REL
    findings: List[Dict[str, Any]] = []
    if not fixture_dir.exists():
        return [finding("error", "missing_fixture_dir", f"missing fixture dir: {FIXTURE_DIR_REL.as_posix()}")], {"status": "fail", "fixture_count": 0}

    kinds, decisions, lifecycle, trust_levels, abi_values = read_provider_vocab(repo_root)
    capability_ids = read_capability_ids(repo_root)
    refusal_codes = read_refusal_codes(repo_root)
    diagnostic_codes = read_diagnostic_codes(repo_root)
    provider_registry = load_json(repo_root / PROVIDER_REGISTRY_REL)
    provider_ids = {
        str(item.get("provider_id"))
        for item in as_list(provider_registry.get("providers"))
        if isinstance(item, dict) and item.get("provider_id")
    }

    fixture_results: List[Dict[str, Any]] = []
    for path in sorted(fixture_dir.glob("*.json")):
        expected_invalid = path.name.startswith("invalid_")
        try:
            data = load_json(path)
        except Exception as exc:
            item_findings = [finding("error", "invalid_fixture_json", f"fixture does not parse: {exc}", path.as_posix())]
        else:
            kind = fixture_kind(path, data)
            if kind == "provider_descriptor":
                item_findings = validate_provider_descriptor(
                    data,
                    path=path.as_posix(),
                    kinds=kinds,
                    lifecycle=lifecycle,
                    trust_levels=trust_levels,
                    abi_values=abi_values,
                    capability_ids=capability_ids,
                    refusal_codes=refusal_codes,
                    diagnostic_codes=diagnostic_codes,
                )
            elif kind == "selection_request":
                item_findings = validate_selection_request(data, path=path.as_posix(), kinds=kinds, capability_ids=capability_ids)
            elif kind == "selection_decision":
                item_findings = validate_selection_decision(
                    data,
                    path=path.as_posix(),
                    decisions=decisions,
                    provider_ids=provider_ids,
                    capability_ids=capability_ids,
                    refusal_codes=refusal_codes,
                    diagnostic_codes=diagnostic_codes,
                )
            else:
                item_findings = [finding("error", "unknown_fixture_kind", f"unknown fixture kind: {kind}", path.as_posix())]
        errors = [item for item in item_findings if item["level"] == "error"]
        passed = bool(errors) if expected_invalid else not errors
        if not passed:
            findings.append(finding("error", "fixture_expectation_failed", f"fixture expectation failed for {path.as_posix()}"))
        fixture_results.append({
            "path": path.as_posix(),
            "expected": "invalid" if expected_invalid else "valid",
            "errors": len(errors),
            "findings": item_findings,
        })
    return findings, {
        "status": "pass" if not findings else "fail",
        "fixture_count": len(fixture_results),
        "fixtures": fixture_results,
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


def classify_inventory_path(path: str) -> Optional[str]:
    lowered = path.lower()
    if lowered.startswith("runtime/render/"):
        return "backend_candidate"
    if lowered.startswith("runtime/platform/"):
        return "backend_candidate"
    if lowered.startswith(("runtime/storage/", "runtime/network/", "runtime/audio/", "runtime/input/")):
        return "backend_candidate"
    if lowered.startswith(("runtime/package/", "runtime/profile/", "runtime/ui/")):
        return "service_candidate"
    if lowered.startswith("apps/workbench/module/"):
        return "workbench_module_candidate"
    if lowered.startswith(("tools/package/", "tools/release/")):
        return "external_adapter_candidate"
    if lowered.startswith("tools/validators/"):
        return "command_handler_candidate"
    if lowered.startswith("contracts/capability/"):
        return "capability_relationship"
    if lowered.startswith("content/packs/"):
        return "pack_hint_not_provider"
    return None


def build_inventory(repo_root: Path) -> Dict[str, Any]:
    categories: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}
    files = git_ls_files(repo_root)
    for path in files:
        category = classify_inventory_path(path)
        if not category:
            continue
        categories[category] = categories.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 8:
            examples[category].append(path)
    return {
        "status": "warning",
        "files_scanned": len(files),
        "categories": categories,
        "examples": examples,
        "note": "Inventory is descriptive only; PROVIDER-MODEL-01 does not migrate or implement providers.",
    }


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    registry_findings, provider_count = validate_provider_registry(repo_root)
    findings.extend(registry_findings)
    fixtures: Dict[str, Any] = {"status": "not_run", "fixture_count": 0}
    if include_fixtures:
        fixture_findings, fixtures = validate_fixtures(repo_root)
        findings.extend(fixture_findings)
    inventory = build_inventory(repo_root) if include_inventory else {"status": "not_run"}
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_provider_model",
        "status": "pass" if not errors else "fail",
        "providers_registered": provider_count,
        "provider_kinds_registered": len(read_provider_vocab(repo_root)[0]) if not errors or (repo_root / PROVIDER_KIND_REGISTRY_REL).exists() else 0,
        "findings": findings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "fixtures": fixtures,
        "inventory": inventory,
    }


def print_text(result: Dict[str, Any]) -> None:
    print(f"provider model: {result['status']}")
    print(f"providers: {result.get('providers_registered', 0)}")
    print(f"provider_kinds: {result.get('provider_kinds_registered', 0)}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
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
    parser.add_argument("--fixtures", action="store_true", help="Validate provider fixtures")
    parser.add_argument("--inventory", action="store_true", help="Inventory provider-like surfaces")
    parser.add_argument("--list", action="store_true", help="List registered providers and exit")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if args.list:
        data = load_json(repo_root / PROVIDER_REGISTRY_REL)
        for item in as_list(data.get("providers")):
            if isinstance(item, dict):
                print(item.get("provider_id", ""))
        return 0

    result = validate_all(repo_root, include_fixtures=args.fixtures, include_inventory=args.inventory)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
