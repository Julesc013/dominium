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
    return findings


def validate_module(item: Dict[str, Any], path: str, kinds: Set[str], command_ids: Set[str], capability_ids: Set[str], provider_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    module_id = str(item.get("module_id") or "")
    module_kind = str(item.get("module_kind") or "")
    if not module_id:
        findings.append(finding("error", "module_missing_id", "module_id is required", path))
    elif PATHLIKE_RE.search(module_id) or not MODULE_ID_RE.match(module_id):
        findings.append(finding("error", "module_bad_id", f"module_id is not a governed dotted ID: {module_id}", path))
    if module_kind not in kinds:
        findings.append(finding("error", "module_unknown_kind", f"unknown module_kind: {module_kind}", path))
    if not item.get("owner"):
        findings.append(finding("error", "module_missing_owner", "owner is required", path))
    if not item.get("stability"):
        findings.append(finding("error", "module_missing_stability", "stability is required", path))
    if item.get("implementation_path_is_identity") is True:
        findings.append(finding("error", "module_path_identity", "implementation_path_is_identity must not be true", path))
    if item.get("private_tool_calls") or item.get("private_dependencies"):
        findings.append(finding("error", "module_private_dependency", "modules must not declare private tool/path dependencies", path))
    commands = [str(v) for v in as_list(item.get("required_commands")) if v]
    if module_kind in {"workbench_module", "command_module"} and not commands:
        findings.append(finding("error", "module_missing_required_command", "workbench/command modules require command bindings", path))
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
