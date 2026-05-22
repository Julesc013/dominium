#!/usr/bin/env python3
"""Validate Dominium Workbench workspace, panel, and view-binding contracts."""

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


WORKSPACE_SCHEMA_REL = Path("contracts/workbench/workspace.schema.json")
PANEL_SCHEMA_REL = Path("contracts/workbench/panel.schema.json")
VIEW_BINDING_SCHEMA_REL = Path("contracts/workbench/view_binding.schema.json")
WORKBENCH_SURFACE_REL = Path("contracts/workbench/workbench_surface.contract.toml")
GENERIC_WORKSPACE_SCHEMA_REL = Path("contracts/workspace/workspace_descriptor.schema.json")
GENERIC_WORKSPACE_SURFACE_REL = Path("contracts/workspace/workspace_surface.contract.toml")
MODULE_SURFACE_REL = Path("contracts/module/module_surface.contract.toml")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/workbench/fixtures")
JSON_RELS = [WORKSPACE_SCHEMA_REL, PANEL_SCHEMA_REL, VIEW_BINDING_SCHEMA_REL, GENERIC_WORKSPACE_SCHEMA_REL]
TOML_CONTRACT_IDS = {
    WORKBENCH_SURFACE_REL: "dominium.workbench.surface.v1",
    GENERIC_WORKSPACE_SURFACE_REL: "dominium.workspace.surface.v1",
}
ID_RE = re.compile(r"^dominium\.workbench\.[a-z0-9][a-z0-9_.-]+$")
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


def read_command_ids(repo_root: Path) -> Set[str]:
    path = repo_root / COMMAND_CONTRACT_REL
    if not path.exists():
        return set()
    data = load_toml(path)
    return {str(item.get("id")) for item in as_list(data.get("command")) if isinstance(item, dict) and item.get("id")}


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
    for rel, expected_id in TOML_CONTRACT_IDS.items():
        try:
            data = load_toml(repo_root / rel)
            if data.get("contract", {}).get("id") != expected_id:
                findings.append(finding("error", "unexpected_contract_id", f"unexpected contract id for {rel}", str(rel)))
        except Exception as exc:
            findings.append(finding("error", "invalid_toml", f"{rel}: {exc}", str(rel)))
    return findings


def valid_id(value: str) -> bool:
    return bool(value and ID_RE.match(value) and not PATHLIKE_RE.search(value))


def validate_workspace(item: Dict[str, Any], path: str, module_ids: Set[str], command_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    workspace_id = str(item.get("workspace_id") or "")
    if not valid_id(workspace_id):
        findings.append(finding("error", "workspace_bad_id", f"workspace_id is not governed: {workspace_id}", path))
    if not item.get("owner"):
        findings.append(finding("error", "workspace_missing_owner", "owner is required", path))
    if not as_list(item.get("modules")):
        findings.append(finding("error", "workspace_missing_module", "workspace requires at least one module", path))
    for module_id in [str(v) for v in as_list(item.get("modules")) if v]:
        if module_ids and module_id not in module_ids:
            findings.append(finding("error", "workspace_unknown_module", f"unknown module: {module_id}", path))
    for command_id in [str(v) for v in as_list(item.get("commands")) if v]:
        if command_ids and command_id not in command_ids:
            findings.append(finding("error", "workspace_unknown_command", f"unknown command: {command_id}", path))
    if item.get("private_tool_calls") or item.get("private_dependencies"):
        findings.append(finding("error", "workspace_private_tool_call", "workspace must not call private tools directly", path))
    if item.get("stability") == "stable" and not as_list(item.get("proof")):
        findings.append(finding("error", "workspace_stable_without_proof", "stable workspace requires proof", path))
    return findings


def validate_panel(item: Dict[str, Any], path: str, command_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if not valid_id(str(item.get("panel_id") or "")):
        findings.append(finding("error", "panel_bad_id", "panel_id is required and must be governed", path))
    if not item.get("owner"):
        findings.append(finding("error", "panel_missing_owner", "owner is required", path))
    if not item.get("view_binding"):
        findings.append(finding("error", "panel_missing_view_binding", "view_binding is required", path))
    for command_id in [str(v) for v in as_list(item.get("commands")) if v]:
        if command_ids and command_id not in command_ids:
            findings.append(finding("error", "panel_unknown_command", f"unknown command: {command_id}", path))
    return findings


def validate_view_binding(item: Dict[str, Any], path: str, command_ids: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if not valid_id(str(item.get("binding_id") or "")):
        findings.append(finding("error", "binding_bad_id", "binding_id is required and must be governed", path))
    if not item.get("view_id"):
        findings.append(finding("error", "binding_missing_view_id", "view_id is required", path))
    if not item.get("result_schema"):
        findings.append(finding("error", "binding_missing_result_schema", "result_schema is required", path))
    command_id = item.get("command_id")
    if command_id and command_ids and str(command_id) not in command_ids:
        findings.append(finding("error", "binding_unknown_command", f"unknown command: {command_id}", path))
    if item.get("private_tool_calls") or item.get("private_dependencies"):
        findings.append(finding("error", "binding_private_tool_call", "view bindings must not call private tools", path))
    return findings


def validate_fixture_file(repo_root: Path, path: Path, module_ids: Set[str], command_ids: Set[str]) -> List[Dict[str, Any]]:
    rel = str(path.relative_to(repo_root))
    data = load_json(path)
    if "workspace_id" in data:
        return validate_workspace(data, rel, module_ids, command_ids)
    if "panel_id" in data:
        return validate_panel(data, rel, command_ids)
    if "binding_id" in data:
        return validate_view_binding(data, rel, command_ids)
    return [finding("error", "unknown_fixture_shape", "unknown workbench fixture shape", rel)]


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    module_ids = read_module_ids(repo_root)
    command_ids = read_command_ids(repo_root)
    count = 0
    for path in sorted((repo_root / FIXTURE_DIR_REL).glob("*.json")):
        count += 1
        item_findings = validate_fixture_file(repo_root, path, module_ids, command_ids)
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
        if path.startswith("apps/workbench/module/"):
            add("workbench_module_candidate", path)
        elif path.startswith("apps/workbench/"):
            add("workbench_shell_or_workspace_candidate", path)
        elif path.startswith("runtime/ui/"):
            add("runtime_ui_primitive_candidate", path)
        elif path.startswith("content/packs/tool/workspace."):
            add("pack_workspace_candidate", path)
    return {"status": "warning", "files_scanned": len(files), "categories": categories, "examples": examples}


def run(repo_root: Path, run_fixtures: bool, run_inventory: bool) -> Dict[str, Any]:
    findings = validate_contracts(repo_root)
    fixtures = validate_fixtures(repo_root) if run_fixtures else {"status": "not_run", "fixture_count": 0}
    if fixtures.get("status") == "fail":
        findings.extend(fixtures.get("findings", []))
    return {
        "validator": "check_workbench_workspaces",
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
        print(f"workbench workspaces: {result['status']}")
        print(f"errors: {result['summary']['errors']}")
        print(f"warnings: {result['summary']['warnings']}")
        if args.fixtures:
            print(f"fixtures: {result['fixtures']['status']} count={result['fixtures']['fixture_count']}")
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
