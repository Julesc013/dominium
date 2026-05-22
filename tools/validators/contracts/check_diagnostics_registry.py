#!/usr/bin/env python3
"""Validate Dominium diagnostic code and evidence registries."""

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


DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
DIAGNOSTIC_SCHEMA_REL = Path("contracts/diagnostic/diagnostic_code.schema.json")
SEVERITY_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_severity.registry.json")
CATEGORY_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_category.registry.json")
POLICY_REL = Path("contracts/diagnostic/diagnostic_policy.contract.toml")
EVIDENCE_PACKET_SCHEMA_REL = Path("contracts/evidence/evidence_packet.schema.json")
EVIDENCE_REF_SCHEMA_REL = Path("contracts/evidence/evidence_ref.schema.json")
EVENT_SCHEMA_REL = Path("contracts/event/event.schema.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
PUBLIC_SURFACE_REL = Path("contracts/public_surface/public_surface.contract.toml")

JSON_RELS = [
    DIAGNOSTIC_REGISTRY_REL,
    DIAGNOSTIC_SCHEMA_REL,
    SEVERITY_REGISTRY_REL,
    CATEGORY_REGISTRY_REL,
    EVIDENCE_PACKET_SCHEMA_REL,
    EVIDENCE_REF_SCHEMA_REL,
    EVENT_SCHEMA_REL,
]

DIAGNOSTIC_ID_RE = re.compile(r"^dominium\.diagnostic\.[a-z0-9][a-z0-9_.-]+$")
DISPLAY_CODE_RE = re.compile(r"^DOM-[A-Z0-9]+(-[A-Z0-9]+)*$")
STABILITY_VALUES = {"provisional", "stable", "internal", "generated", "fixture", "historical", "retired"}
RECOVERY_OPTIONAL = {"historical", "retired"}
EVIDENCE_STATUSES = {
    "pass",
    "pass_with_warnings",
    "fail",
    "blocked",
    "not_run",
    "partial",
    "ok",
    "warning",
    "refused",
    "error",
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


def as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def string_set(values: Iterable[Any]) -> Set[str]:
    return {str(value) for value in values if isinstance(value, str)}


def finding(level: str, code: str, message: str, diagnostic_id: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if diagnostic_id:
        item["diagnostic_id"] = diagnostic_id
    return item


def registry_ids(data: Dict[str, Any], key: str, id_key: str = "id") -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def load_optional_json(path: Path, key: str, id_key: str) -> Set[str]:
    if not path.exists():
        return set()
    try:
        return registry_ids(load_json(path), key, id_key)
    except Exception:
        return set()


def command_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        data = load_toml(path)
    except Exception:
        return set()
    return {
        str(item.get("id"))
        for item in as_list(data.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


def public_surface_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        data = load_toml(path)
    except Exception:
        return set()
    return {
        str(item.get("id"))
        for item in as_list(data.get("surface"))
        if isinstance(item, dict) and item.get("id")
    }


def validate_json_surfaces(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in JSON_RELS:
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


def validate_policy(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / POLICY_REL
    if not path.exists():
        return [finding("error", "missing_policy_contract", f"missing policy contract: {POLICY_REL.as_posix()}")]
    try:
        data = load_toml(path)
    except Exception as exc:
        return [finding("error", "invalid_policy_toml", f"{POLICY_REL.as_posix()} does not parse as TOML: {exc}")]
    findings: List[Dict[str, Any]] = []
    contract = data.get("contract", {})
    policy = data.get("policy", {})
    if not isinstance(contract, dict) or contract.get("id") != "dominium.diagnostics.policy.v1":
        findings.append(finding("error", "policy_contract_id", "diagnostic policy contract id must be dominium.diagnostics.policy.v1"))
    if not isinstance(policy, dict) or policy.get("free_text_only_failures_allowed") is not False:
        findings.append(finding("error", "policy_free_text_rule", "diagnostic policy must disallow free-text-only failures"))
    return findings


def validate_diagnostic_registry(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    registry = load_json(repo_root / DIAGNOSTIC_REGISTRY_REL)
    severities = registry_ids(load_json(repo_root / SEVERITY_REGISTRY_REL), "severities")
    categories = registry_ids(load_json(repo_root / CATEGORY_REGISTRY_REL), "categories")
    refusal_codes = load_optional_json(repo_root / REFUSAL_REGISTRY_REL, "codes", "code")
    known_commands = command_ids(repo_root / COMMAND_CONTRACT_REL)
    known_surfaces = public_surface_ids(repo_root / PUBLIC_SURFACE_REL)

    seen_ids: Set[str] = set()
    seen_codes: Set[str] = set()
    codes = as_list(registry.get("codes"))
    if not codes:
        findings.append(finding("error", "diagnostic_registry_empty", "diagnostic code registry must contain codes"))

    for index, item in enumerate(codes):
        if not isinstance(item, dict):
            findings.append(finding("error", "diagnostic_shape", f"diagnostic entry {index} must be an object"))
            continue
        diag_id = str(item.get("id", ""))
        display_code = str(item.get("code", ""))
        if not diag_id:
            findings.append(finding("error", "diagnostic_missing_id", f"diagnostic entry {index} is missing id"))
            continue
        if diag_id in seen_ids:
            findings.append(finding("error", "diagnostic_duplicate_id", f"duplicate diagnostic id: {diag_id}", diag_id))
        seen_ids.add(diag_id)
        if not DIAGNOSTIC_ID_RE.match(diag_id):
            findings.append(finding("error", "diagnostic_bad_id", "diagnostic id must be dominium.diagnostic.* dotted id", diag_id))

        if not display_code:
            findings.append(finding("error", "diagnostic_missing_code", "diagnostic is missing display code", diag_id))
        elif display_code in seen_codes:
            findings.append(finding("error", "diagnostic_duplicate_code", f"duplicate display code: {display_code}", diag_id))
        else:
            seen_codes.add(display_code)
        if display_code and not DISPLAY_CODE_RE.match(display_code):
            findings.append(finding("error", "diagnostic_bad_code", "display code must be uppercase hyphenated DOM-* code", diag_id))

        for key in ("owner", "summary", "cause", "evidence_expectation"):
            if not item.get(key):
                findings.append(finding("error", "diagnostic_missing_field", f"diagnostic is missing required field {key}", diag_id))

        stability = str(item.get("stability", ""))
        if stability not in STABILITY_VALUES:
            findings.append(finding("error", "diagnostic_bad_stability", f"unsupported diagnostic stability: {stability}", diag_id))
        if stability not in RECOVERY_OPTIONAL and not item.get("recovery"):
            findings.append(finding("error", "diagnostic_missing_recovery", "diagnostic must declare recovery unless historical or retired", diag_id))

        severity = str(item.get("severity", ""))
        if severity not in severities:
            findings.append(finding("error", "diagnostic_bad_severity", f"unknown severity: {severity}", diag_id))
        category = str(item.get("category", ""))
        if category not in categories:
            findings.append(finding("error", "diagnostic_bad_category", f"unknown category: {category}", diag_id))

        if stability == "stable" and not as_list(item.get("proof")):
            findings.append(finding("error", "stable_diagnostic_missing_proof", "stable diagnostic must include proof", diag_id))

        for refusal in string_set(item.get("related_refusal_codes", [])):
            if refusal_codes and refusal not in refusal_codes:
                findings.append(finding("error", "diagnostic_unknown_refusal", f"unknown related refusal code: {refusal}", diag_id))
        for command in string_set(item.get("related_command_ids", [])):
            if known_commands and command not in known_commands:
                findings.append(finding("warning", "diagnostic_unknown_command", f"related command is not currently registered: {command}", diag_id))
        for surface in string_set(item.get("related_public_surface_ids", [])):
            if known_surfaces and surface not in known_surfaces:
                findings.append(finding("warning", "diagnostic_unknown_public_surface", f"related public surface is not currently registered: {surface}", diag_id))

    return {
        "diagnostic_codes": sorted(seen_codes),
        "diagnostic_ids": sorted(seen_ids),
        "findings": findings,
        "severity_count": len(severities),
        "category_count": len(categories),
    }


def validate_evidence_packet(data: Dict[str, Any], fixture_name: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for key in ("evidence_id", "subject_id", "subject_kind", "status", "tool", "summary", "proof"):
        if key not in data or data.get(key) in ("", None, []):
            findings.append(finding("error", "evidence_missing_field", f"{fixture_name} is missing required evidence field {key}"))
    status = str(data.get("status", ""))
    if status and status not in EVIDENCE_STATUSES:
        findings.append(finding("error", "evidence_bad_status", f"{fixture_name} has unsupported evidence status: {status}"))
    proof = data.get("proof")
    if proof is not None and not isinstance(proof, list):
        findings.append(finding("error", "evidence_bad_proof", f"{fixture_name} proof must be an array"))
    return findings


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    fixture_root = repo_root / "tests/contract/diagnostics/fixtures"
    results: List[Dict[str, Any]] = []
    diagnostic_expectations = {
        "valid_diagnostic_code.json": False,
        "invalid_missing_owner.json": True,
        "invalid_unknown_severity.json": True,
    }
    severities = registry_ids(load_json(repo_root / SEVERITY_REGISTRY_REL), "severities")
    categories = registry_ids(load_json(repo_root / CATEGORY_REGISTRY_REL), "categories")
    for name, expect_errors in diagnostic_expectations.items():
        path = fixture_root / name
        try:
            item = load_json(path)
            data = {"codes": [item]}
            temp_path = repo_root / DIAGNOSTIC_REGISTRY_REL
            findings = []
            # Reuse the core per-item checks with direct local logic to keep fixture output focused.
            code = str(item.get("code", ""))
            diag_id = str(item.get("id", ""))
            if not diag_id or not DIAGNOSTIC_ID_RE.match(diag_id):
                findings.append(finding("error", "fixture_bad_id", f"{name} has invalid diagnostic id"))
            if not code or not DISPLAY_CODE_RE.match(code):
                findings.append(finding("error", "fixture_bad_code", f"{name} has invalid display code"))
            for key in ("owner", "summary", "cause", "recovery", "evidence_expectation"):
                if not item.get(key):
                    findings.append(finding("error", "fixture_missing_field", f"{name} is missing {key}"))
            if item.get("severity") not in severities:
                findings.append(finding("error", "fixture_bad_severity", f"{name} has unknown severity"))
            if item.get("category") not in categories:
                findings.append(finding("error", "fixture_bad_category", f"{name} has unknown category"))
            if item.get("stability") not in STABILITY_VALUES:
                findings.append(finding("error", "fixture_bad_stability", f"{name} has unknown stability"))
            _ = data, temp_path  # keep variables visible to lint-free readers without external deps
        except Exception as exc:
            findings = [finding("error", "fixture_invalid_json", f"{name} does not parse as JSON: {exc}")]
        has_errors = any(item["level"] == "error" for item in findings)
        status = "pass" if has_errors == expect_errors else "fail"
        results.append({"fixture": name, "status": status, "expected_errors": expect_errors, "findings": findings})

    evidence_expectations = {
        "valid_evidence_packet.json": False,
        "invalid_evidence_missing_subject.json": True,
    }
    for name, expect_errors in evidence_expectations.items():
        path = fixture_root / name
        try:
            data = load_json(path)
            findings = validate_evidence_packet(data, name)
        except Exception as exc:
            findings = [finding("error", "fixture_invalid_json", f"{name} does not parse as JSON: {exc}")]
        has_errors = any(item["level"] == "error" for item in findings)
        status = "pass" if has_errors == expect_errors else "fail"
        results.append({"fixture": name, "status": status, "expected_errors": expect_errors, "findings": findings})

    return {
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "fixtures": results,
    }


def summarize(findings: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "errors": sum(1 for item in findings if item.get("level") == "error"),
        "warnings": sum(1 for item in findings if item.get("level") == "warning"),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on registry errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--list", action="store_true", help="List diagnostic display codes")
    parser.add_argument("--fixtures", action="store_true", help="Validate diagnostic/evidence fixtures")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_surfaces(repo_root))
    findings.extend(validate_policy(repo_root))
    registry_result = validate_diagnostic_registry(repo_root)
    findings.extend(registry_result["findings"])
    fixture_result = validate_fixtures(repo_root) if args.fixtures else {"status": "not_run", "fixtures": []}

    counts = summarize(findings)
    status = "pass"
    if counts["errors"]:
        status = "fail"
    if args.fixtures and fixture_result["status"] != "pass":
        status = "fail"

    output = {
        "validator": "check_diagnostics_registry",
        "status": status,
        "diagnostic_codes_total": len(registry_result["diagnostic_codes"]),
        "diagnostic_codes": registry_result["diagnostic_codes"],
        "severity_count": registry_result["severity_count"],
        "category_count": registry_result["category_count"],
        "findings": findings,
        "summary": counts,
        "fixtures": fixture_result,
    }

    if args.list:
        for code in registry_result["diagnostic_codes"]:
            print(code)
    elif args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"diagnostics registry: {status}")
        print(f"diagnostic_codes: {len(registry_result['diagnostic_codes'])}")
        print(f"severities: {registry_result['severity_count']}")
        print(f"categories: {registry_result['category_count']}")
        print(f"errors: {counts['errors']}")
        print(f"warnings: {counts['warnings']}")
        if args.fixtures:
            print(f"fixtures: {fixture_result['status']}")
        for item in findings:
            print(f"{item['level'].upper()}: {item['code']}: {item['message']}")

    if args.strict and status != "pass":
        return 1
    if args.fixtures and fixture_result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
