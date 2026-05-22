#!/usr/bin/env python3
"""Validate Dominium schema/protocol evolution contracts and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


SCHEMA_EVOLUTION_REL = Path("contracts/schema/schema_evolution.contract.toml")
PROTOCOL_EVOLUTION_REL = Path("contracts/protocol/protocol_evolution.contract.toml")
REGISTRY_EVOLUTION_REL = Path("contracts/registry/registry_evolution.contract.toml")
SERIALIZATION_REL = Path("contracts/serialization/canonical_serialization.contract.toml")
MIGRATION_REL = Path("contracts/migration/migration_policy.contract.toml")
SCHEMA_POLICY_SCHEMA_REL = Path("contracts/schema/schema_policy.schema.json")
PROTOCOL_POLICY_SCHEMA_REL = Path("contracts/protocol/protocol_policy.schema.json")
REGISTRY_POLICY_SCHEMA_REL = Path("contracts/registry/registry_policy.schema.json")
SCHEMA_STABILITY_REL = Path("contracts/schema/schema_stability.registry.json")
FIELD_POLICY_REL = Path("contracts/schema/field_policy.registry.json")
PROTOCOL_STABILITY_REL = Path("contracts/protocol/protocol_stability.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/schema_protocol/fixtures")

JSON_RELS = [
    SCHEMA_POLICY_SCHEMA_REL,
    PROTOCOL_POLICY_SCHEMA_REL,
    REGISTRY_POLICY_SCHEMA_REL,
    SCHEMA_STABILITY_REL,
    FIELD_POLICY_REL,
    PROTOCOL_STABILITY_REL,
]

TOML_RELS = [
    SCHEMA_EVOLUTION_REL,
    PROTOCOL_EVOLUTION_REL,
    REGISTRY_EVOLUTION_REL,
    SERIALIZATION_REL,
    MIGRATION_REL,
]

EXPECTED_CONTRACT_IDS = {
    SCHEMA_EVOLUTION_REL: "dominium.schema.evolution.v1",
    PROTOCOL_EVOLUTION_REL: "dominium.protocol.evolution.v1",
    REGISTRY_EVOLUTION_REL: "dominium.registry.evolution.v1",
    SERIALIZATION_REL: "dominium.serialization.canonical.v1",
    MIGRATION_REL: "dominium.migration.policy.v1",
}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*(\.[a-z0-9][a-z0-9_.-]*)*$")
STABLE_VALUES = {"stable"}
PATHLIKE_SUFFIXES = (".json", ".toml", ".yaml", ".yml", ".schema")


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


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def registry_ids(data: Dict[str, Any], key: str) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get("id")
    }


def id_is_path_like(value: str) -> bool:
    return "/" in value or "\\" in value or ":" in value or value.endswith(PATHLIKE_SUFFIXES)


def read_policy_sets(repo_root: Path) -> Dict[str, Set[str]]:
    field_data = load_json(repo_root / FIELD_POLICY_REL)
    schema_stability = load_json(repo_root / SCHEMA_STABILITY_REL)
    protocol_stability = load_json(repo_root / PROTOCOL_STABILITY_REL)
    return {
        "schema_stability": registry_ids(schema_stability, "values"),
        "protocol_stability": registry_ids(protocol_stability, "values"),
        "unknown_field": registry_ids(field_data, "unknown_field_policies"),
        "required_field": registry_ids(field_data, "required_field_policies"),
        "default": registry_ids(field_data, "default_policies"),
        "canonical": registry_ids(field_data, "canonical_serialization_policies"),
        "migration": registry_ids(field_data, "migration_policies"),
        "refusal": registry_ids(field_data, "refusal_policies"),
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


def validate_schema_policy(data: Dict[str, Any], rel: str, policies: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    schema_id = str(data.get("schema_id", ""))
    if not schema_id:
        findings.append(finding("error", "schema_missing_id", "schema policy missing schema_id", rel))
    elif id_is_path_like(schema_id) or not ID_RE.match(schema_id):
        findings.append(finding("error", "schema_invalid_id", f"schema_id is not a semantic dotted id: {schema_id}", rel))
    for key in ["owner", "version", "stability", "compatibility_range", "unknown_field_policy", "required_field_policy", "default_policy", "canonical_serialization", "migration_policy", "refusal_policy"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "schema_missing_required_field", f"schema policy missing {key}", rel))
    if data.get("stability") and data.get("stability") not in policies["schema_stability"]:
        findings.append(finding("error", "schema_unknown_stability", f"unknown schema stability: {data.get('stability')}", rel))
    if data.get("unknown_field_policy") and data.get("unknown_field_policy") not in policies["unknown_field"]:
        findings.append(finding("error", "schema_unknown_field_policy", f"unknown field policy: {data.get('unknown_field_policy')}", rel))
    if data.get("required_field_policy") and data.get("required_field_policy") not in policies["required_field"]:
        findings.append(finding("error", "schema_unknown_required_policy", f"unknown required field policy: {data.get('required_field_policy')}", rel))
    if data.get("default_policy") and data.get("default_policy") not in policies["default"]:
        findings.append(finding("error", "schema_unknown_default_policy", f"unknown default policy: {data.get('default_policy')}", rel))
    if data.get("canonical_serialization") and data.get("canonical_serialization") not in policies["canonical"]:
        findings.append(finding("error", "schema_unknown_canonical_policy", f"unknown canonical serialization policy: {data.get('canonical_serialization')}", rel))
    if data.get("migration_policy") and data.get("migration_policy") not in policies["migration"]:
        findings.append(finding("error", "schema_unknown_migration_policy", f"unknown migration policy: {data.get('migration_policy')}", rel))
    if data.get("refusal_policy") and data.get("refusal_policy") not in policies["refusal"]:
        findings.append(finding("error", "schema_unknown_refusal_policy", f"unknown refusal policy: {data.get('refusal_policy')}", rel))
    if data.get("default_policy") == "silent_default" or data.get("defaults_are_silent") is True:
        findings.append(finding("error", "schema_silent_default_forbidden", "silent defaults are forbidden", rel))
    if data.get("stability") in STABLE_VALUES:
        if not data.get("fixtures") or not data.get("negative_fixtures") or not data.get("proof"):
            findings.append(finding("error", "stable_schema_missing_proof", "stable schema policy requires fixtures, negative fixtures, and proof", rel))
    return findings


def validate_protocol_policy(data: Dict[str, Any], rel: str, policies: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    protocol_id = str(data.get("protocol_id", ""))
    if not protocol_id:
        findings.append(finding("error", "protocol_missing_id", "protocol policy missing protocol_id", rel))
    elif id_is_path_like(protocol_id) or not ID_RE.match(protocol_id):
        findings.append(finding("error", "protocol_invalid_id", f"protocol_id is not a semantic dotted id: {protocol_id}", rel))
    for key in ["owner", "version", "stability", "message_kinds", "compatibility_range", "unknown_message_policy", "unknown_field_policy", "required_field_policy", "ordering_policy", "canonical_encoding", "migration_policy", "refusal_policy"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "protocol_missing_required_field", f"protocol policy missing {key}", rel))
    if data.get("stability") and data.get("stability") not in policies["protocol_stability"]:
        findings.append(finding("error", "protocol_unknown_stability", f"unknown protocol stability: {data.get('stability')}", rel))
    if data.get("unknown_field_policy") and data.get("unknown_field_policy") not in policies["unknown_field"]:
        findings.append(finding("error", "protocol_unknown_field_policy", f"unknown field policy: {data.get('unknown_field_policy')}", rel))
    if data.get("required_field_policy") and data.get("required_field_policy") not in policies["required_field"]:
        findings.append(finding("error", "protocol_unknown_required_policy", f"unknown required field policy: {data.get('required_field_policy')}", rel))
    if data.get("canonical_encoding") and data.get("canonical_encoding") not in policies["canonical"]:
        findings.append(finding("error", "protocol_unknown_canonical_policy", f"unknown canonical encoding: {data.get('canonical_encoding')}", rel))
    if data.get("migration_policy") and data.get("migration_policy") not in policies["migration"]:
        findings.append(finding("error", "protocol_unknown_migration_policy", f"unknown migration policy: {data.get('migration_policy')}", rel))
    if data.get("refusal_policy") and data.get("refusal_policy") not in policies["refusal"]:
        findings.append(finding("error", "protocol_unknown_refusal_policy", f"unknown refusal policy: {data.get('refusal_policy')}", rel))
    if data.get("unknown_message_policy") and data.get("unknown_message_policy") not in {"reject", "ignore_with_diagnostic", "allow_if_extension_declared"}:
        findings.append(finding("error", "protocol_unknown_message_policy", f"unknown message policy: {data.get('unknown_message_policy')}", rel))
    if data.get("stability") in STABLE_VALUES and (not data.get("fixtures") or not data.get("proof")):
        findings.append(finding("error", "stable_protocol_missing_proof", "stable protocol policy requires fixtures and proof", rel))
    return findings


def validate_migration_policy(data: Dict[str, Any], rel: str, policies: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    section = data.get("migration", data)
    if not isinstance(section, dict):
        findings.append(finding("error", "migration_root_invalid", "migration policy must be a table", rel))
        return findings
    for key in ["id", "owner", "version", "source_schema_id", "target_schema_id", "migration_policy", "refusal_policy"]:
        if section.get(key) in (None, "", []):
            findings.append(finding("error", "migration_missing_required_field", f"migration policy missing {key}", rel))
    if section.get("migration_policy") and section.get("migration_policy") not in policies["migration"]:
        findings.append(finding("error", "migration_unknown_policy", f"unknown migration policy: {section.get('migration_policy')}", rel))
    if section.get("refusal_policy") and section.get("refusal_policy") not in policies["refusal"]:
        findings.append(finding("error", "migration_unknown_refusal_policy", f"unknown refusal policy: {section.get('refusal_policy')}", rel))
    return findings


def validate_fixture_files(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    policies = read_policy_sets(repo_root)
    fixtures: List[Dict[str, Any]] = []

    cases = [
        ("valid_schema_policy.json", "schema", True),
        ("invalid_schema_missing_id.json", "schema", False),
        ("invalid_schema_silent_default.json", "schema", False),
        ("valid_protocol_policy.json", "protocol", True),
        ("invalid_protocol_missing_version.json", "protocol", False),
        ("valid_migration_policy.toml", "migration", True),
        ("invalid_migration_missing_refusal.toml", "migration", False),
    ]
    for name, kind, expected_valid in cases:
        path = repo_root / FIXTURE_DIR_REL / name
        rel = path.relative_to(repo_root).as_posix() if path.exists() else (FIXTURE_DIR_REL / name).as_posix()
        try:
            if kind == "migration":
                data = load_toml(path)
                case_findings = validate_migration_policy(data, rel, policies)
            else:
                data = load_json(path)
                if kind == "schema":
                    case_findings = validate_schema_policy(data, rel, policies)
                else:
                    case_findings = validate_protocol_policy(data, rel, policies)
        except Exception as exc:
            case_findings = [finding("error", "fixture_parse_failed", f"fixture parse failed: {exc}", rel)]
        errors = [item for item in case_findings if item["level"] == "error"]
        fixtures.append({"path": rel, "expected": "valid" if expected_valid else "invalid", "errors": len(errors), "findings": case_findings})
        if expected_valid and errors:
            findings.append(finding("error", "valid_fixture_failed", f"valid fixture failed: {rel}", rel))
        if not expected_valid and not errors:
            findings.append(finding("error", "invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))

    return findings, {
        "status": "pass" if not findings else "fail",
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
    }


def validate_diagnostic_codes(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if not path.exists():
        return [finding("warning", "diagnostics_registry_missing", "diagnostics registry is missing; schema/protocol diagnostics not checked")]
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "diagnostics_registry_invalid", f"diagnostics registry does not parse: {exc}")]
    codes = {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }
    required = {
        "DOM-SCHEMA-MISSING-ID",
        "DOM-SCHEMA-UNSUPPORTED-VERSION",
        "DOM-SCHEMA-UNKNOWN-FIELD",
        "DOM-SCHEMA-REQUIRED-FIELD-MISSING",
        "DOM-SCHEMA-SILENT-DEFAULT-FORBIDDEN",
        "DOM-PROTOCOL-UNSUPPORTED-VERSION",
        "DOM-PROTOCOL-UNKNOWN-MESSAGE",
        "DOM-PROTOCOL-INCOMPATIBLE",
        "DOM-MIGRATION-REQUIRED",
        "DOM-MIGRATION-MISSING",
        "DOM-REGISTRY-DUPLICATE-ID",
        "DOM-REGISTRY-UNKNOWN-ENTRY",
    }
    missing = sorted(required - codes)
    if missing:
        return [finding("warning", "schema_protocol_diagnostics_missing", f"schema/protocol diagnostic codes not registered: {', '.join(missing)}")]
    return []


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
    except Exception:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _load_id_version(path: Path) -> Tuple[bool, bool]:
    try:
        if path.suffix == ".json":
            data = load_json(path)
            if not isinstance(data, dict):
                return False, False
            has_id = any(data.get(key) for key in ["$id", "id", "schema_id", "protocol_id", "registry_id"])
            has_version = any(data.get(key) for key in ["version", "schema_version", "protocol_version", "registry_version"])
            return bool(has_id), bool(has_version)
        if path.suffix == ".toml":
            data = load_toml(path)
            contract = data.get("contract", {})
            has_id = bool(data.get("id") or (isinstance(contract, dict) and contract.get("id")))
            has_version = bool(data.get("version") or data.get("schema_version"))
            return has_id, has_version
    except Exception:
        return False, False
    return False, False


def inventory(repo_root: Path) -> Dict[str, Any]:
    files = git_ls_files(repo_root)
    candidates: List[str] = []
    for path in files:
        norm = path.replace("\\", "/")
        if (
            norm.startswith("contracts/schema/")
            or norm.startswith("contracts/protocol/")
            or norm.startswith("contracts/registry/")
            or norm.startswith("contracts/result/")
            or norm.startswith("contracts/event/")
            or norm.startswith("contracts/refusal/")
            or norm.startswith("contracts/diagnostic/")
            or norm.startswith("contracts/evidence/")
            or norm.startswith("contracts/artifact/")
            or norm.startswith("tests/contract/")
            or norm.startswith("content/packs/")
            or norm.startswith("release/")
        ) and (
            norm.endswith(".schema.json")
            or norm.endswith(".schema")
            or norm.endswith(".registry.json")
            or norm.endswith(".contract.toml")
            or norm.endswith(".manifest.json")
            or norm.endswith(".json")
            or norm.endswith(".toml")
        ):
            candidates.append(norm)

    categories = {
        "manifest_backed_schema": 0,
        "likely_public_schema": 0,
        "internal_schema": 0,
        "generated_schema": 0,
        "fixture_schema": 0,
        "historical_schema": 0,
        "registry": 0,
        "protocol": 0,
        "deferred": 0,
    }
    examples: Dict[str, List[str]] = {key: [] for key in categories}
    missing_id = 0
    missing_version = 0

    for norm in candidates:
        if norm.startswith("tests/"):
            key = "fixture_schema"
        elif norm.startswith("archive/"):
            key = "historical_schema"
        elif "/generated/" in norm or norm.startswith(".aide/reports/"):
            key = "generated_schema"
        elif norm.startswith("contracts/protocol/") or "protocol" in norm:
            key = "protocol"
        elif norm.startswith("contracts/registry/") or norm.endswith(".registry.json"):
            key = "registry"
        elif norm.endswith(".manifest.json") or "manifest" in norm:
            key = "manifest_backed_schema"
        elif norm.startswith("contracts/schema/"):
            key = "likely_public_schema"
        elif norm.startswith("contracts/"):
            key = "internal_schema"
        else:
            key = "deferred"
        categories[key] += 1
        if len(examples[key]) < 8:
            examples[key].append(norm)
        has_id, has_version = _load_id_version(repo_root / norm)
        if not has_id:
            missing_id += 1
        if not has_version:
            missing_version += 1

    return {
        "files_scanned": len(files),
        "schema_protocol_like_files": len(candidates),
        "categories": categories,
        "examples": examples,
        "missing_id_like_field": missing_id,
        "missing_version_like_field": missing_version,
        "status": "warning",
        "note": "Inventory is descriptive only; SCHEMA-PROTOCOL-LAW-01 does not migrate existing schemas or registries.",
    }


def validate_all(repo_root: Path, include_fixtures: bool) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    fixture_summary = {"status": "not_run", "fixture_count": 0}
    policy_counts: Dict[str, int] = {}
    if not any(item["level"] == "error" for item in findings):
        try:
            policies = read_policy_sets(repo_root)
        except Exception as exc:
            findings.append(finding("error", "policy_registry_load_failed", f"could not load policy registries: {exc}"))
            policies = {}
        if policies:
            policy_counts = {key: len(value) for key, value in policies.items()}
            required_counts = {
                "schema_stability": 8,
                "protocol_stability": 8,
                "unknown_field": 4,
                "required_field": 4,
                "default": 4,
                "canonical": 5,
                "migration": 5,
                "refusal": 3,
            }
            for key, expected in required_counts.items():
                if len(policies.get(key, set())) < expected:
                    findings.append(finding("error", "policy_registry_incomplete", f"{key} policy registry is incomplete"))
            if include_fixtures:
                fixture_findings, fixture_summary = validate_fixture_files(repo_root)
                findings.extend(fixture_findings)
    findings.extend(validate_diagnostic_codes(repo_root))
    return findings, {"fixtures": fixture_summary, "policy_counts": policy_counts}


def print_list(repo_root: Path) -> None:
    policies = read_policy_sets(repo_root)
    for key in sorted(policies):
        print(f"{key}:")
        for item in sorted(policies[key]):
            print(f"- {item}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero on errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--fixtures", action="store_true", help="Validate schema/protocol fixtures.")
    parser.add_argument("--inventory", action="store_true", help="Run descriptive schema/protocol inventory.")
    parser.add_argument("--list", action="store_true", help="List policy registry values.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if args.list:
        print_list(repo_root)
        return 0

    findings, summary = validate_all(repo_root, include_fixtures=args.fixtures)
    inv = inventory(repo_root) if args.inventory else {"status": "not_run"}
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    status = "pass" if not errors else "fail"

    result = {
        "validator": "check_schema_protocol_evolution",
        "status": status,
        "policy_counts": summary["policy_counts"],
        "fixtures": summary["fixtures"],
        "inventory": inv,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "findings": findings,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"schema/protocol evolution: {status}")
        print(f"errors: {len(errors)}")
        print(f"warnings: {len(warnings)}")
        if args.fixtures:
            print(f"fixtures: {summary['fixtures']['status']} count={summary['fixtures']['fixture_count']}")
        if args.inventory:
            print(f"inventory: {inv['status']} schema_protocol_like_files={inv['schema_protocol_like_files']} files_scanned={inv['files_scanned']}")
        for item in findings[:80]:
            location = f" {item['path']}:" if item.get("path") else ""
            print(f"{item['level'].upper()} {item['code']}:{location} {item['message']}")

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
