#!/usr/bin/env python3
"""Validate Dominium app descriptor and app composition contracts."""

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
except ImportError:  # pragma: no cover
    tomllib = None


APP_DESCRIPTOR_SCHEMA_REL = Path("contracts/app/app_descriptor.schema.json")
APP_COMPOSITION_SCHEMA_REL = Path("contracts/app/app_composition.schema.json")
APP_SURFACE_REL = Path("contracts/app/app_surface.contract.toml")
MODULE_SURFACE_REL = Path("contracts/module/module_surface.contract.toml")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/app/fixtures")
EXPECTED_CONTRACT_ID = "dominium.app.surface.v1"
APP_ID_RE = re.compile(r"^dominium\.[a-z0-9][a-z0-9_.-]+$")
PATHLIKE_RE = re.compile(r"[/\\]|\.\.(?:/|\\)|\.(json|toml|exe)$")
VALID_MODES = {"cli", "tui", "rendered", "native", "headless"}


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


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        return [item.strip().strip('"') for item in raw[1:-1].split(",") if item.strip()]
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


def read_module_ids(repo_root: Path) -> Set[str]:
    path = repo_root / MODULE_SURFACE_REL
    if not path.exists():
        return set()
    data = load_toml(path)
    return {str(item.get("module_id")) for item in as_list(data.get("module")) if isinstance(item, dict) and item.get("module_id")}


def read_provider_ids(repo_root: Path) -> Set[str]:
    path = repo_root / PROVIDER_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {str(item.get("provider_id")) for item in as_list(data.get("providers")) if isinstance(item, dict) and item.get("provider_id")}


def read_capability_ids(repo_root: Path) -> Set[str]:
    path = repo_root / CAPABILITY_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {str(item.get("capability_id")) for item in as_list(data.get("capabilities")) if isinstance(item, dict) and item.get("capability_id")}


def validate_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in [APP_DESCRIPTOR_SCHEMA_REL, APP_COMPOSITION_SCHEMA_REL]:
        try:
            load_json(repo_root / rel)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel}: {exc}", str(rel)))
    try:
        data = load_toml(repo_root / APP_SURFACE_REL)
        if data.get("contract", {}).get("id") != EXPECTED_CONTRACT_ID:
            findings.append(finding("error", "unexpected_contract_id", "unexpected app contract id", str(APP_SURFACE_REL)))
    except Exception as exc:
        findings.append(finding("error", "invalid_toml", f"{APP_SURFACE_REL}: {exc}", str(APP_SURFACE_REL)))
    return findings


def valid_app_id(value: str) -> bool:
    return bool(value and APP_ID_RE.match(value) and not PATHLIKE_RE.search(value))


def validate_descriptor(item: Dict[str, Any], path: str, module_ids: Set[str], provider_ids: Set[str], capability_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    app_id = str(item.get("app_id") or "")
    if not valid_app_id(app_id):
        findings.append(finding("error", "app_bad_id", f"app_id is not governed: {app_id}", path))
    if not item.get("product_id"):
        findings.append(finding("error", "app_missing_product_id", "product_id is required", path))
    if not item.get("owner"):
        findings.append(finding("error", "app_missing_owner", "owner is required", path))
    modes = {str(v) for v in as_list(item.get("modes")) if v}
    if not modes:
        findings.append(finding("error", "app_missing_modes", "modes are required", path))
    for mode in modes:
        if mode not in VALID_MODES:
            findings.append(finding("error", "app_unknown_mode", f"unknown mode: {mode}", path))
    if item.get("private_dependencies") or item.get("private_paths"):
        findings.append(finding("error", "app_private_dependency", "apps must not bind private implementation paths", path))
    for module_id in [str(v) for v in as_list(item.get("enabled_modules")) if v]:
        if module_ids and module_id not in module_ids:
            findings.append(finding("error", "app_unknown_module", f"unknown module: {module_id}", path))
    for provider_id in [str(v) for v in as_list(item.get("provider_preferences")) if v]:
        if provider_ids and provider_id not in provider_ids:
            findings.append(finding("error", "app_unknown_provider", f"unknown provider: {provider_id}", path))
    for capability_id in [str(v) for v in as_list(item.get("required_capabilities")) if v]:
        if capability_ids and capability_id not in capability_ids:
            findings.append(finding("error", "app_unknown_capability", f"unknown capability: {capability_id}", path))
    if item.get("stability") == "stable" and not as_list(item.get("proof")):
        findings.append(finding("error", "app_stable_without_proof", "stable apps require proof", path))
    return findings


def validate_composition(item: Dict[str, Any], path: str, module_ids: Set[str], provider_ids: Set[str], capability_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    composition_id = str(item.get("composition_id") or "")
    if not valid_app_id(composition_id):
        findings.append(finding("error", "composition_bad_id", f"composition_id is not governed: {composition_id}", path))
    if not item.get("product_id"):
        findings.append(finding("error", "app_missing_product_id", "product_id is required", path))
    if item.get("private_dependencies") or item.get("private_paths"):
        findings.append(finding("error", "app_private_dependency", "app composition must not bind private implementation paths", path))
    for module_id in [str(v) for v in as_list(item.get("modules")) if v]:
        if module_ids and module_id not in module_ids:
            findings.append(finding("error", "app_unknown_module", f"unknown module: {module_id}", path))
    for provider_id in [str(v) for v in as_list(item.get("providers")) if v]:
        if provider_ids and provider_id not in provider_ids:
            findings.append(finding("error", "app_unknown_provider", f"unknown provider: {provider_id}", path))
    for capability_id in [str(v) for v in as_list(item.get("capabilities")) if v]:
        if capability_ids and capability_id not in capability_ids:
            findings.append(finding("error", "app_unknown_capability", f"unknown capability: {capability_id}", path))
    return findings


def validate_fixture_file(repo_root: Path, path: Path, module_ids: Set[str], provider_ids: Set[str], capability_ids: Set[str]) -> List[Dict[str, Any]]:
    rel = str(path.relative_to(repo_root))
    data = load_json(path)
    if "composition_id" in data:
        return validate_composition(data, rel, module_ids, provider_ids, capability_ids)
    return validate_descriptor(data, rel, module_ids, provider_ids, capability_ids)


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    module_ids = read_module_ids(repo_root)
    provider_ids = read_provider_ids(repo_root)
    capability_ids = read_capability_ids(repo_root)
    count = 0
    for path in sorted((repo_root / FIXTURE_DIR_REL).glob("*.json")):
        count += 1
        item_findings = validate_fixture_file(repo_root, path, module_ids, provider_ids, capability_ids)
        expect_invalid = path.name.startswith("invalid_")
        if expect_invalid and not item_findings:
            findings.append(finding("error", "fixture_expected_failure", f"invalid fixture passed: {path.name}", str(path.relative_to(repo_root))))
        if not expect_invalid:
            findings.extend(item_findings)
    return {"status": "fail" if findings else "pass", "fixture_count": count, "findings": findings}


def inventory(repo_root: Path) -> Dict[str, Any]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=str(repo_root), check=True, text=True, stdout=subprocess.PIPE)
        files = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        files = []
    categories: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}

    def add(category: str, path: str) -> None:
        categories[category] = categories.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 8:
            examples[category].append(path)

    for path in files:
        if path.startswith(("apps/client/", "apps/server/", "apps/launcher/", "apps/setup/", "apps/workbench/")):
            add("app_product_candidate", path)
        elif path.startswith("release/"):
            add("release_profile_candidate", path)
        elif path.startswith("content/packs/"):
            add("default_pack_candidate", path)
        elif path.startswith("contracts/provider/"):
            add("provider_preference_candidate", path)
    return {"status": "warning", "files_scanned": len(files), "categories": categories, "examples": examples}


def run(repo_root: Path, run_fixtures: bool, run_inventory: bool) -> Dict[str, Any]:
    findings = validate_contracts(repo_root)
    fixtures = validate_fixtures(repo_root) if run_fixtures else {"status": "not_run", "fixture_count": 0}
    if fixtures.get("status") == "fail":
        findings.extend(fixtures.get("findings", []))
    return {
        "validator": "check_app_descriptors",
        "status": "fail" if any(f["level"] == "error" for f in findings) else "pass",
        "summary": {
            "errors": sum(1 for f in findings if f["level"] == "error"),
            "warnings": sum(1 for f in findings if f["level"] == "warning"),
        },
        "findings": findings,
        "fixtures": fixtures,
        "inventory": inventory(repo_root) if run_inventory else {"status": "not_run"},
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args(argv)
    result = run(Path(args.repo_root).resolve(), args.fixtures, args.inventory)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"app descriptors: {result['status']}")
        print(f"errors: {result['summary']['errors']}")
        print(f"warnings: {result['summary']['warnings']}")
        if args.fixtures:
            print(f"fixtures: {result['fixtures']['status']} count={result['fixtures']['fixture_count']}")
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
