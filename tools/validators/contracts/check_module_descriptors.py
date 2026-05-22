#!/usr/bin/env python3
"""Validate Dominium module composition contracts, descriptors, and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - Python 3.8 fallback
    tomllib = None


MODULE_SCHEMA_REL = Path("contracts/module/module.schema.json")
MODULE_COMPOSITION_SCHEMA_REL = Path("contracts/module/module_composition.schema.json")
MODULE_KIND_REGISTRY_REL = Path("contracts/module/module_kind.registry.json")
MODULE_SURFACE_REL = Path("contracts/module/module_surface.contract.toml")
MODULE_DEPENDENCY_POLICY_REL = Path("contracts/module/module_dependency_policy.contract.toml")
PACK_MODULE_POLICY_REL = Path("contracts/module/pack_provided_module_policy.contract.toml")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/module/fixtures")

JSON_RELS = [MODULE_SCHEMA_REL, MODULE_COMPOSITION_SCHEMA_REL, MODULE_KIND_REGISTRY_REL]
TOML_RELS = [MODULE_SURFACE_REL, MODULE_DEPENDENCY_POLICY_REL, PACK_MODULE_POLICY_REL]
EXPECTED_CONTRACT_IDS = {
    MODULE_SURFACE_REL: "dominium.module.surface.v1",
    MODULE_DEPENDENCY_POLICY_REL: "dominium.module.dependency_policy.v1",
    PACK_MODULE_POLICY_REL: "dominium.module.pack_provided_policy.v1",
}
MODULE_ID_RE = re.compile(r"^(domino|dominium)\.(module|workbench)(\.[a-z0-9][a-z0-9_-]*)+$")
PATHLIKE_RE = re.compile(r"[/\\]|\.\.(?:/|\\)|\.(json|toml)$")
FORBIDDEN_IMPLEMENTATION_PREFIXES = {
    "modules": "contracts/module for declarations, owner root for implementation, content/packs for payloads",
    "plugins": "content/packs for payloads or tools/runtime adapter owners for behavior",
    "services": "runtime/service owner, contracts/service, or the precise owning runtime root",
    "workspaces": "apps/workbench/workspace, data/workspaces for dev overlays, or contracts/workspace",
    "content/modules": "content/packs/<category>/<pack_id>",
}
KIND_IMPLEMENTATION_PREFIXES = {
    "workbench_module": ("apps/workbench/module",),
    "workbench_workspace": ("apps/workbench/workspace",),
    "content_pack_module": ("content/packs",),
    "app_composition": ("apps", "contracts/app"),
    "runtime_service": ("runtime",),
    "runtime_provider": ("runtime/provider", "runtime"),
}
KIND_OWNER_EXPECTATIONS = {
    "workbench_module": "apps.workbench",
    "workbench_workspace": "apps.workbench",
    "content_pack_module": "content.packs",
}
MODULE_POLICY_EXPECTATIONS = {
    "module_identity_is_path": False,
    "workbench_is_authority": False,
    "modules_depend_on_private_paths": False,
    "pack_modules_require_declared_descriptor": True,
    "module_declarations_live_in_contracts_or_pack_manifests": True,
    "workbench_modules_are_presentation_only": True,
    "reusable_behavior_lives_under_ownership_root": True,
    "module_payloads_are_pack_delivered": True,
    "top_level_modules_root_allowed": False,
    "top_level_plugins_root_allowed": False,
    "top_level_services_root_allowed": False,
    "top_level_workspaces_root_allowed": False,
    "runtime_module_root_is_service_only": True,
    "content_modules_root_allowed": False,
    "apps_compose_modules_do_not_own_reusable_behavior": True,
}
PACK_POLICY_EXPECTATIONS = {
    "pack_module_descriptor_required": True,
    "pack_module_id_is_path": False,
    "data_only_packs_may_provide_native_code": False,
    "silent_module_activation_allowed": False,
    "pack_modules_live_under_content_packs": True,
    "content_modules_root_allowed": False,
    "pack_module_may_declare_payloads_not_native_behavior": True,
    "reusable_behavior_requires_service_provider_or_domain_owner": True,
}


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


def normalize_repo_path(value: Any) -> str:
    return str(value or "").replace("\\", "/").strip("/")


def has_path_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def registry_ids(data: Dict[str, Any], key: str, id_key: str = "id") -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def read_command_ids(repo_root: Path) -> Set[str]:
    path = repo_root / COMMAND_CONTRACT_REL
    if not path.exists():
        return set()
    data = load_toml(path)
    return {
        str(item.get("id"))
        for item in as_list(data.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


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


def read_provider_ids(repo_root: Path) -> Set[str]:
    path = repo_root / PROVIDER_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("provider_id"))
        for item in as_list(data.get("providers"))
        if isinstance(item, dict) and item.get("provider_id")
    }


def validate_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json", f"missing {rel}", str(rel)))
            continue
        try:
            load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel}: {exc}", str(rel)))
    for rel in TOML_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_toml", f"missing {rel}", str(rel)))
            continue
        try:
            data = load_toml(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_toml", f"{rel}: {exc}", str(rel)))
            continue
        contract = data.get("contract", {})
        if contract.get("id") != EXPECTED_CONTRACT_IDS[rel]:
            findings.append(finding("error", "unexpected_contract_id", f"{rel}: unexpected contract id", str(rel)))
        policy = data.get("policy", {})
        expectations = MODULE_POLICY_EXPECTATIONS if rel == MODULE_SURFACE_REL else PACK_POLICY_EXPECTATIONS if rel == PACK_MODULE_POLICY_REL else {}
        for key, expected in expectations.items():
            if policy.get(key) != expected:
                findings.append(finding("error", "module_policy_mismatch", f"{rel}: policy {key} must be {expected}", str(rel)))
    return findings


def validate_module(item: Dict[str, Any], path: str, kinds: Set[str], command_ids: Set[str], capability_ids: Set[str], provider_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    module_id = str(item.get("module_id") or "")
    module_kind = str(item.get("module_kind") or "")
    implementation_path = normalize_repo_path(item.get("implementation_path"))
    if not module_id:
        findings.append(finding("error", "module_missing_id", "module_id is required", path))
    elif PATHLIKE_RE.search(module_id) or not MODULE_ID_RE.match(module_id):
        findings.append(finding("error", "module_bad_id", f"module_id is not a governed dotted ID: {module_id}", path))
    if module_kind not in kinds:
        findings.append(finding("error", "module_unknown_kind", f"unknown module_kind: {module_kind}", path))
    owner = str(item.get("owner") or "")
    if not owner:
        findings.append(finding("error", "module_missing_owner", "owner is required", path))
    expected_owner = KIND_OWNER_EXPECTATIONS.get(module_kind)
    if expected_owner and owner and owner != expected_owner:
        findings.append(finding("error", "module_owner_mismatch", f"{module_kind} owner must be {expected_owner}", path))
    if not item.get("stability"):
        findings.append(finding("error", "module_missing_stability", "stability is required", path))
    if item.get("implementation_path_is_identity") is True:
        findings.append(finding("error", "module_path_identity", "implementation_path_is_identity must not be true", path))
    if implementation_path:
        for prefix, target in sorted(FORBIDDEN_IMPLEMENTATION_PREFIXES.items()):
            if has_path_prefix(implementation_path, prefix):
                findings.append(finding("error", "module_forbidden_implementation_root", f"implementation_path uses forbidden root {prefix}; use {target}", path))
        allowed_prefixes = KIND_IMPLEMENTATION_PREFIXES.get(module_kind)
        if allowed_prefixes and not any(has_path_prefix(implementation_path, prefix) for prefix in allowed_prefixes):
            findings.append(
                finding(
                    "error",
                    "module_wrong_implementation_root",
                    f"{module_kind} implementation_path must live under one of: {', '.join(allowed_prefixes)}",
                    path,
                )
            )
    if item.get("private_tool_calls") or item.get("private_dependencies"):
        findings.append(finding("error", "module_private_dependency", "modules must not declare private tool/path dependencies", path))
    commands = [str(v) for v in as_list(item.get("required_commands")) if v]
    if module_kind in {"workbench_module", "command_module"} and not commands:
        findings.append(finding("error", "module_missing_required_command", "workbench/command modules require command bindings", path))
    if module_kind == "workbench_module":
        if item.get("reusable_behavior") is True:
            findings.append(finding("error", "workbench_module_reusable_behavior", "Workbench modules must be presentation only; reusable behavior belongs under the owning runtime/game/tool/app root", path))
        if item.get("presentation_only") is False:
            findings.append(finding("error", "workbench_module_not_presentation_only", "Workbench module descriptors must not deny presentation-only ownership", path))
        ownership_layer = item.get("ownership_layer")
        if ownership_layer and ownership_layer != "workbench_presentation":
            findings.append(finding("error", "workbench_module_bad_ownership_layer", "Workbench module ownership_layer must be workbench_presentation", path))
    if module_kind == "content_pack_module":
        if item.get("native_code") is True:
            findings.append(finding("error", "pack_module_native_code", "Pack-provided modules may declare payloads, not native behavior", path))
        ownership_layer = item.get("ownership_layer")
        if ownership_layer and ownership_layer != "pack_payload":
            findings.append(finding("error", "pack_module_bad_ownership_layer", "Pack-provided module ownership_layer must be pack_payload", path))
        if not as_list(item.get("packs")):
            findings.append(finding("error", "pack_module_missing_pack_ref", "Pack-provided modules must name at least one pack", path))
    for command_id in commands:
        if command_ids and command_id not in command_ids:
            findings.append(finding("error", "module_unknown_command", f"unknown command ID: {command_id}", path))
    for capability_id in [str(v) for v in as_list(item.get("required_capabilities")) if v]:
        if capability_ids and capability_id not in capability_ids:
            findings.append(finding("error", "module_unknown_capability", f"unknown capability ID: {capability_id}", path))
    for provider_id in [str(v) for v in as_list(item.get("required_providers")) if v]:
        if provider_ids and provider_id not in provider_ids:
            findings.append(finding("error", "module_unknown_provider", f"unknown provider ID: {provider_id}", path))
    if item.get("stability") == "stable" and not as_list(item.get("proof")):
        findings.append(finding("error", "module_stable_without_proof", "stable modules require proof", path))
    return findings


def validate_registry_modules(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    kinds = registry_ids(load_json(repo_root / MODULE_KIND_REGISTRY_REL), "kinds")
    command_ids = read_command_ids(repo_root)
    capability_ids = read_capability_ids(repo_root)
    provider_ids = read_provider_ids(repo_root)
    data = load_toml(repo_root / MODULE_SURFACE_REL)
    seen: Set[str] = set()
    for item in as_list(data.get("module")):
        if not isinstance(item, dict):
            continue
        module_id = str(item.get("module_id") or "")
        if module_id in seen:
            findings.append(finding("error", "module_duplicate_id", f"duplicate module_id: {module_id}", str(MODULE_SURFACE_REL)))
        seen.add(module_id)
        findings.extend(validate_module(item, str(MODULE_SURFACE_REL), kinds, command_ids, capability_ids, provider_ids))
    return findings


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    fixture_dir = repo_root / FIXTURE_DIR_REL
    findings: List[Dict[str, Any]] = []
    kinds = registry_ids(load_json(repo_root / MODULE_KIND_REGISTRY_REL), "kinds")
    command_ids = read_command_ids(repo_root)
    capability_ids = read_capability_ids(repo_root)
    provider_ids = read_provider_ids(repo_root)
    count = 0
    for path in sorted(fixture_dir.glob("*.json")):
        count += 1
        data = load_json(path)
        item_findings = validate_module(data, str(path.relative_to(repo_root)), kinds, command_ids, capability_ids, provider_ids)
        expect_invalid = path.name.startswith("invalid_")
        if expect_invalid and not item_findings:
            findings.append(finding("error", "fixture_expected_failure", f"invalid fixture passed: {path.name}", str(path.relative_to(repo_root))))
        if not expect_invalid:
            findings.extend(item_findings)
    return {"status": "fail" if findings else "pass", "fixture_count": count, "findings": findings}


def inventory(repo_root: Path) -> Dict[str, Any]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=str(repo_root), check=True, text=True, stdout=subprocess.PIPE)
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        files = [str(path.relative_to(repo_root)).replace("\\", "/") for path in repo_root.rglob("*") if path.is_file()]
    categories: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}

    def add(category: str, path: str) -> None:
        categories[category] = categories.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 8:
            examples[category].append(path)

    for path in files:
        normalized = path.replace("\\", "/")
        if normalized.startswith("apps/workbench/module/"):
            add("workbench_module_candidate", normalized)
        elif normalized.startswith("apps/workbench/workspace/"):
            add("workbench_workspace_candidate", normalized)
        elif normalized.startswith(("apps/client/", "apps/server/", "apps/launcher/", "apps/setup/", "apps/tools/")):
            add("app_composition_candidate", normalized)
        elif normalized.startswith(("runtime/ui/", "contracts/view/", "contracts/document/")):
            add("command_view_document_candidate", normalized)
        elif normalized.startswith(("runtime/shell/", "runtime/package/", "runtime/profile/")):
            add("runtime_service_candidate", normalized)
        elif normalized.startswith("content/packs/"):
            add("pack_provided_module_candidate", normalized)
        elif normalized.startswith(("contracts/command/", "tools/validators/")):
            add("command_module_candidate", normalized)
        elif normalized.startswith("contracts/provider/"):
            add("provider_relationship", normalized)
        elif normalized.startswith("contracts/capability/"):
            add("capability_relationship", normalized)
    return {
        "status": "warning",
        "files_scanned": len(files),
        "categories": categories,
        "examples": examples,
        "note": "Inventory is descriptive only; MODULE-COMPOSITION-LAW-01 does not migrate current app/workbench/runtime systems.",
    }


def run(repo_root: Path, run_fixtures: bool, run_inventory: bool) -> Dict[str, Any]:
    findings = validate_contracts(repo_root)
    findings.extend(validate_registry_modules(repo_root))
    fixtures = validate_fixtures(repo_root) if run_fixtures else {"status": "not_run", "fixture_count": 0}
    if fixtures.get("status") == "fail":
        findings.extend(fixtures.get("findings", []))
    kinds = registry_ids(load_json(repo_root / MODULE_KIND_REGISTRY_REL), "kinds")
    result = {
        "validator": "check_module_descriptors",
        "status": "fail" if any(f["level"] == "error" for f in findings) else "pass",
        "summary": {
            "errors": sum(1 for f in findings if f["level"] == "error"),
            "warnings": sum(1 for f in findings if f["level"] == "warning"),
        },
        "module_kinds_registered": len(kinds),
        "findings": findings,
        "fixtures": fixtures,
        "inventory": inventory(repo_root) if run_inventory else {"status": "not_run"},
    }
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    result = run(repo_root, args.fixtures, args.inventory)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"module descriptors: {result['status']}")
        print(f"module_kinds: {result['module_kinds_registered']}")
        print(f"errors: {result['summary']['errors']}")
        print(f"warnings: {result['summary']['warnings']}")
        if args.fixtures:
            print(f"fixtures: {result['fixtures']['status']} count={result['fixtures']['fixture_count']}")
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
