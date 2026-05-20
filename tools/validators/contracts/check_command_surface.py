#!/usr/bin/env python3
"""Validate Dominium command/result/refusal/event/evidence surface contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
COMMAND_SCHEMA_REL = Path("contracts/command/command.schema.json")
COMMAND_KIND_REL = Path("contracts/command/command_kind.registry.json")
RESULT_SCHEMA_REL = Path("contracts/result/result.schema.json")
VIEW_SCHEMA_REL = Path("contracts/view/view.schema.json")
EVENT_SCHEMA_REL = Path("contracts/event/event.schema.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
REFUSAL_SCHEMA_REL = Path("contracts/refusal/refusal.schema.json")
EVIDENCE_SCHEMA_REL = Path("contracts/evidence/evidence_packet.schema.json")

REQUIRED_JSON_RELS = [
    COMMAND_SCHEMA_REL,
    COMMAND_KIND_REL,
    RESULT_SCHEMA_REL,
    VIEW_SCHEMA_REL,
    EVENT_SCHEMA_REL,
    REFUSAL_REGISTRY_REL,
    REFUSAL_SCHEMA_REL,
    Path("contracts/document/document.schema.json"),
    EVIDENCE_SCHEMA_REL,
]

COMMAND_ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+$")
REFUSAL_ID_RE = re.compile(r"^dominium\.refusal\.[a-z0-9][a-z0-9_.-]+$")
STABLE_COMMAND_CLASSES = {"stable_command_contract"}
EVIDENCE_REQUIRED_KINDS = {"validation", "test", "package", "release"}
FORBIDDEN_PRIVATE_CALL_KEYS = {
    "implementation_path",
    "private_path",
    "tool_path",
    "direct_call",
    "handler_path",
}
VALID_STABILITY = {
    "stable_command_contract",
    "provisional",
    "internal",
    "experimental",
    "historical",
    "retired",
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
            if section not in {"command", "view", "event"}:
                raise ValueError(f"unsupported array table at line {lineno}: {section}")
            current = {}
            root.setdefault(section, []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = root
            for part in section.split("."):
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


def finding(level: str, code: str, message: str, command_id: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if command_id:
        item["command_id"] = command_id
    return item


def as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def string_set(values: Iterable[Any]) -> Set[str]:
    return {str(value) for value in values if isinstance(value, str)}


def registry_kind_ids(kind_registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(kind_registry.get("kinds"))
        if isinstance(item, dict) and item.get("id")
    }


def registry_surface_ids(kind_registry: Dict[str, Any]) -> Set[str]:
    return string_set(kind_registry.get("allowed_surfaces", []))


def refusal_codes(refusal_registry: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("code"))
        for item in as_list(refusal_registry.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def path_exists(repo_root: Path, raw_path: str) -> bool:
    if not raw_path:
        return False
    path = Path(raw_path)
    if path.is_absolute():
        return path.exists()
    return (repo_root / path).exists()


def validate_json_shapes(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in REQUIRED_JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json_surface", f"required JSON surface is missing: {rel.as_posix()}"))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}"))
            continue
        if not isinstance(data, dict):
            findings.append(finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object"))
    return findings


def validate_refusal_registry(refusal_registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, item in enumerate(as_list(refusal_registry.get("codes"))):
        if not isinstance(item, dict):
            findings.append(finding("error", "refusal_shape", f"refusal entry {index} must be an object"))
            continue
        code = str(item.get("code", ""))
        if not code:
            findings.append(finding("error", "refusal_missing_code", f"refusal entry {index} is missing code"))
            continue
        if code in seen:
            findings.append(finding("error", "refusal_duplicate_code", f"duplicate refusal code: {code}"))
        seen.add(code)
        if not REFUSAL_ID_RE.match(code):
            findings.append(finding("error", "refusal_bad_id", f"refusal code must be dominium.refusal.* dotted id: {code}"))
        for key in ("owner", "reason", "recovery", "stability"):
            if not item.get(key):
                findings.append(finding("error", "refusal_missing_field", f"{code} is missing required field {key}"))
    if not seen:
        findings.append(finding("error", "refusal_registry_empty", "refusal registry must contain at least one code"))
    return findings


def validate_commands(
    repo_root: Path,
    contract: Dict[str, Any],
    kind_ids: Set[str],
    surface_ids: Set[str],
    known_refusals: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    commands = as_list(contract.get("command"))
    if not commands:
        findings.append(finding("error", "command_registry_empty", "command surface contract must define at least one command"))
        return findings

    seen: Set[str] = set()
    for index, item in enumerate(commands):
        if not isinstance(item, dict):
            findings.append(finding("error", "command_shape", f"command entry {index} must be an object"))
            continue
        command_id = str(item.get("id", ""))
        if not command_id:
            findings.append(finding("error", "command_missing_id", f"command entry {index} is missing id"))
            continue
        if command_id in seen:
            findings.append(finding("error", "command_duplicate_id", f"duplicate command id: {command_id}", command_id))
        seen.add(command_id)
        if not COMMAND_ID_RE.match(command_id):
            findings.append(finding("error", "command_bad_id", "command id must be lowercase dotted domino.* or dominium.*", command_id))

        for key in ("version", "owner", "stability", "kind", "input_schema", "result_schema", "service_owner", "compatibility", "replacement_policy"):
            if not item.get(key):
                findings.append(finding("error", "command_missing_field", f"command is missing required field {key}", command_id))

        stability = str(item.get("stability", ""))
        if stability and stability not in VALID_STABILITY:
            findings.append(finding("error", "command_bad_stability", f"unsupported command stability {stability}", command_id))

        kind = str(item.get("kind", ""))
        if kind and kind not in kind_ids:
            findings.append(finding("error", "command_bad_kind", f"unsupported command kind {kind}", command_id))

        surfaces = string_set(item.get("surfaces", []))
        if not surfaces:
            findings.append(finding("error", "command_missing_surfaces", "command must declare at least one surface", command_id))
        unknown_surfaces = sorted(surfaces - surface_ids)
        if unknown_surfaces:
            findings.append(finding("error", "command_bad_surface", f"unknown command surfaces: {', '.join(unknown_surfaces)}", command_id))

        planned = bool(item.get("planned", False))
        input_schema = str(item.get("input_schema", ""))
        result_schema = str(item.get("result_schema", ""))
        if input_schema and not planned and not path_exists(repo_root, input_schema):
            findings.append(finding("error", "command_missing_input_schema", f"input schema does not exist: {input_schema}", command_id))
        if result_schema and not path_exists(repo_root, result_schema):
            findings.append(finding("error", "command_missing_result_schema", f"result schema does not exist: {result_schema}", command_id))

        refusals = string_set(item.get("refusals", []))
        missing_refusals = sorted(refusals - known_refusals)
        if missing_refusals:
            findings.append(finding("error", "command_unknown_refusal", f"unknown refusal codes: {', '.join(missing_refusals)}", command_id))

        proof = as_list(item.get("proof"))
        if stability in STABLE_COMMAND_CLASSES:
            if not proof:
                findings.append(finding("error", "stable_command_missing_proof", "stable command must have proof entries", command_id))
            if not refusals:
                findings.append(finding("error", "stable_command_missing_refusal_policy", "stable command must declare refusal codes", command_id))

        evidence_schema = str(item.get("evidence_schema", ""))
        if kind in EVIDENCE_REQUIRED_KINDS and not evidence_schema:
            findings.append(finding("error", "command_missing_evidence_schema", f"{kind} commands must declare evidence_schema", command_id))
        if evidence_schema and not path_exists(repo_root, evidence_schema):
            findings.append(finding("error", "command_missing_evidence_schema_path", f"evidence schema does not exist: {evidence_schema}", command_id))

        if "workbench" in surfaces:
            bad_keys = sorted(key for key in FORBIDDEN_PRIVATE_CALL_KEYS if item.get(key))
            if bad_keys:
                findings.append(finding("error", "workbench_private_direct_call", f"Workbench-facing command declares private direct-call fields: {', '.join(bad_keys)}", command_id))
        notes = str(item.get("notes", ""))
        if "private" in notes.lower() and "legacy" not in notes.lower():
            findings.append(finding("warning", "command_private_note", "command notes mention private paths; confirm this is not direct implementation authority", command_id))
    return findings


def validate_contract(repo_root: Path, contract_path: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    if not contract_path.exists():
        findings.append(finding("error", "missing_contract", f"missing command surface contract: {contract_path}"))
        return {
            "contract_path": str(contract_path),
            "commands": [],
            "findings": findings,
        }

    try:
        contract = load_toml(contract_path)
    except Exception as exc:
        return {
            "contract_path": str(contract_path),
            "commands": [],
            "findings": [finding("error", "invalid_toml", f"{contract_path} does not parse as TOML: {exc}")],
        }

    findings.extend(validate_json_shapes(repo_root))
    kind_registry = load_json(repo_root / COMMAND_KIND_REL)
    refusal_registry = load_json(repo_root / REFUSAL_REGISTRY_REL)
    kind_ids = registry_kind_ids(kind_registry)
    surface_ids = registry_surface_ids(kind_registry)
    known_refusals = refusal_codes(refusal_registry)
    findings.extend(validate_refusal_registry(refusal_registry))
    findings.extend(validate_commands(repo_root, contract, kind_ids, surface_ids, known_refusals))
    return {
        "contract_path": str(contract_path),
        "commands": [item.get("id") for item in as_list(contract.get("command")) if isinstance(item, dict)],
        "findings": findings,
    }


def validate_fixture_contract(repo_root: Path, fixture_path: Path) -> List[Dict[str, Any]]:
    try:
        contract = load_toml(fixture_path)
    except Exception as exc:
        return [finding("error", "fixture_invalid_toml", f"{fixture_path} does not parse as TOML: {exc}")]
    kind_registry = load_json(repo_root / COMMAND_KIND_REL)
    refusal_registry = load_json(repo_root / REFUSAL_REGISTRY_REL)
    return validate_commands(repo_root, contract, registry_kind_ids(kind_registry), registry_surface_ids(kind_registry), refusal_codes(refusal_registry))


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    fixture_root = repo_root / "tests/contract/command_surface/fixtures"
    results: List[Dict[str, Any]] = []
    expectations = {
        "valid_command_surface.toml": False,
        "invalid_missing_result_schema.toml": True,
        "invalid_stable_without_refusal_policy.toml": True,
    }
    for name, expect_errors in expectations.items():
        path = fixture_root / name
        if not path.exists():
            results.append({"fixture": name, "status": "fail", "findings": [finding("error", "fixture_missing", f"missing fixture {name}")]})
            continue
        findings = validate_fixture_contract(repo_root, path)
        has_errors = any(item["level"] == "error" for item in findings)
        status = "pass" if has_errors == expect_errors else "fail"
        results.append({"fixture": name, "status": status, "expected_errors": expect_errors, "findings": findings})

    for name in ("valid_result.json", "valid_refusal.json", "valid_evidence_packet.json"):
        path = fixture_root / name
        try:
            data = load_json(path)
            status = "pass" if isinstance(data, dict) else "fail"
            findings = [] if status == "pass" else [finding("error", "fixture_json_root", f"{name} must be a JSON object")]
        except Exception as exc:
            status = "fail"
            findings = [finding("error", "fixture_invalid_json", f"{name} does not parse as JSON: {exc}")]
        results.append({"fixture": name, "status": status, "findings": findings})
    return {
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "fixtures": results,
    }


def summarize(findings: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "errors": sum(1 for item in findings if item.get("level") == "error"),
        "warnings": sum(1 for item in findings if item.get("level") == "warning"),
    }


def print_list(commands: Sequence[Any]) -> None:
    for command_id in commands:
        print(command_id)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on command-surface errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--list", action="store_true", help="List registered command IDs")
    parser.add_argument("--fixtures", action="store_true", help="Validate command-surface fixtures")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    result = validate_contract(repo_root, repo_root / COMMAND_CONTRACT_REL)
    counts = summarize(result["findings"])
    fixture_result = validate_fixtures(repo_root) if args.fixtures else {"status": "not_run", "fixtures": []}

    status = "pass"
    if counts["errors"]:
        status = "fail"
    if args.fixtures and fixture_result["status"] != "pass":
        status = "fail"

    output = {
        "validator": "check_command_surface",
        "status": status,
        "contract": COMMAND_CONTRACT_REL.as_posix(),
        "commands_total": len(result["commands"]),
        "commands": result["commands"],
        "findings": result["findings"],
        "summary": counts,
        "fixtures": fixture_result,
    }

    if args.list:
        print_list(result["commands"])
    elif args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"command_surface: {status}")
        print(f"commands: {len(result['commands'])}")
        print(f"errors: {counts['errors']}")
        print(f"warnings: {counts['warnings']}")
        if args.fixtures:
            print(f"fixtures: {fixture_result['status']}")
        for item in result["findings"]:
            print(f"{item['level'].upper()}: {item['code']}: {item['message']}")

    if args.strict and status != "pass":
        return 1
    if args.fixtures and fixture_result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
