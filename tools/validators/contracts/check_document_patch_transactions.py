#!/usr/bin/env python3
"""Validate Dominium document patch transaction contracts and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


CONTRACT_REL = Path("contracts/document/document_patch_transaction.contract.toml")
SCHEMA_REL = Path("contracts/document/document_patch_transaction.schema.json")
DOCUMENT_SCHEMA_REL = Path("contracts/document/document.schema.json")
RUNTIME_REL = Path("runtime/document/patch_transaction.py")
FIXTURE_DIR_REL = Path("tests/contract/document_patch_transactions/fixtures")

EXPECTED_CONTRACT_ID = "dominium.document.patch_transaction.contract.v1"
EXPECTED_SCHEMA_ID = "dominium.document.patch_transaction_schema.v1"
EXPECTED_PAYLOAD_SCHEMA_ID = "dominium.document.patch_transaction.v1"
EXPECTED_SCHEMA_VERSION = "1.0.0"
EXPECTED_STABILITY = "provisional"
EXPECTED_OPS = {"test", "add", "replace", "remove"}
TRANSACTION_ID_RE = re.compile(r"^dominium\.document\.patch_txn\.[a-z0-9][a-z0-9_.-]*$")


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


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def validate_json_file(repo_root: Path, rel: Path) -> List[Dict[str, Any]]:
    path = repo_root / rel
    if not path.exists():
        return [finding("error", "missing_json", f"missing JSON file: {rel.as_posix()}", rel.as_posix())]
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}", rel.as_posix())]
    if not isinstance(data, dict):
        return [finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object", rel.as_posix())]
    return []


def validate_schema(repo_root: Path) -> List[Dict[str, Any]]:
    findings = validate_json_file(repo_root, SCHEMA_REL)
    findings.extend(validate_json_file(repo_root, DOCUMENT_SCHEMA_REL))
    if findings:
        return findings
    schema = load_json(repo_root / SCHEMA_REL)
    if schema.get("$id") != EXPECTED_SCHEMA_ID:
        findings.append(finding("error", "schema_id_unexpected", "document patch transaction schema has unexpected $id", SCHEMA_REL.as_posix()))
    if schema.get("additionalProperties") is not False:
        findings.append(finding("error", "schema_allows_unknown_root_fields", "transaction schema must refuse unknown root fields", SCHEMA_REL.as_posix()))
    required = set(as_list(schema.get("required")))
    expected_required = {
        "schema_id",
        "schema_version",
        "stability",
        "transaction_id",
        "document_id",
        "document_schema_id",
        "expected_content_hash",
        "authority",
        "operations",
    }
    missing_required = sorted(expected_required - required)
    if missing_required:
        findings.append(finding("error", "schema_missing_required", "schema missing required fields: " + ", ".join(missing_required), SCHEMA_REL.as_posix()))

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        findings.append(finding("error", "schema_properties_invalid", "schema properties must be an object", SCHEMA_REL.as_posix()))
        return findings
    if properties.get("schema_id", {}).get("const") != EXPECTED_PAYLOAD_SCHEMA_ID:
        findings.append(finding("error", "payload_schema_id_unexpected", "schema_id const does not match expected payload schema id", SCHEMA_REL.as_posix()))
    if properties.get("schema_version", {}).get("const") != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "schema_version_unexpected", "schema_version const does not match expected version", SCHEMA_REL.as_posix()))
    if properties.get("stability", {}).get("const") != EXPECTED_STABILITY:
        findings.append(finding("error", "stability_unexpected", "stability const does not match expected stability", SCHEMA_REL.as_posix()))

    op_defs = schema.get("$defs", {}).get("operation", {}).get("oneOf", [])
    declared_ops: Set[str] = set()
    for item in as_list(op_defs):
        if isinstance(item, dict):
            op_const = item.get("properties", {}).get("op", {}).get("const")
            if isinstance(op_const, str):
                declared_ops.add(op_const)
    if declared_ops != EXPECTED_OPS:
        findings.append(finding("error", "schema_operation_set_mismatch", "schema operation set must be add/remove/replace/test", SCHEMA_REL.as_posix()))
    return findings


def validate_contract(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / CONTRACT_REL
    if not path.exists():
        return [finding("error", "missing_contract", f"missing contract: {CONTRACT_REL.as_posix()}", CONTRACT_REL.as_posix())]
    try:
        data = load_toml(path)
    except Exception as exc:
        return [finding("error", "invalid_toml", f"{CONTRACT_REL.as_posix()} does not parse as TOML: {exc}", CONTRACT_REL.as_posix())]

    findings: List[Dict[str, Any]] = []
    contract = data.get("contract", {})
    boundary = data.get("boundary", {})
    validation = data.get("validation", {})
    if not isinstance(contract, dict) or contract.get("id") != EXPECTED_CONTRACT_ID:
        findings.append(finding("error", "contract_id_unexpected", "contract id is missing or unexpected", CONTRACT_REL.as_posix()))
    if contract.get("schema_id") != EXPECTED_PAYLOAD_SCHEMA_ID:
        findings.append(finding("error", "contract_schema_id_unexpected", "contract schema_id is missing or unexpected", CONTRACT_REL.as_posix()))
    if contract.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "contract_schema_version_unexpected", "contract schema_version is missing or unexpected", CONTRACT_REL.as_posix()))
    if contract.get("schema_path") != SCHEMA_REL.as_posix():
        findings.append(finding("error", "contract_schema_path_unexpected", "contract schema_path must point to document patch transaction schema", CONTRACT_REL.as_posix()))
    if boundary.get("mutation_target") != "document.content":
        findings.append(finding("error", "contract_boundary_target_unexpected", "contract must scope mutation to document.content", CONTRACT_REL.as_posix()))
    if set(as_list(boundary.get("allowed_operations"))) != EXPECTED_OPS:
        findings.append(finding("error", "contract_operation_set_mismatch", "contract operation set must be add/remove/replace/test", CONTRACT_REL.as_posix()))
    forbidden = set(str(item) for item in as_list(boundary.get("forbidden_semantics")))
    for token in ("broad_save_system", "silent_schema_migration", "storage_commit", "ui_authority_mutation"):
        if token not in forbidden:
            findings.append(finding("error", "contract_missing_non_goal", f"contract boundary missing forbidden semantic: {token}", CONTRACT_REL.as_posix()))
    if validation.get("validator") != "tools/validators/contracts/check_document_patch_transactions.py":
        findings.append(finding("error", "contract_validator_unexpected", "contract validator path is missing or unexpected", CONTRACT_REL.as_posix()))
    return findings


def import_runtime(repo_root: Path):
    root_text = str(repo_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from runtime.document.patch_transaction import (  # pylint: disable=import-outside-toplevel
        PATCH_TRANSACTION_SCHEMA_ID,
        PATCH_TRANSACTION_SCHEMA_VERSION,
        apply_patch_transaction,
    )

    return PATCH_TRANSACTION_SCHEMA_ID, PATCH_TRANSACTION_SCHEMA_VERSION, apply_patch_transaction


def validate_runtime(repo_root: Path) -> List[Dict[str, Any]]:
    if not (repo_root / RUNTIME_REL).exists():
        return [finding("error", "missing_runtime", f"missing runtime helper: {RUNTIME_REL.as_posix()}", RUNTIME_REL.as_posix())]
    try:
        schema_id, schema_version, _apply = import_runtime(repo_root)
    except Exception as exc:
        return [finding("error", "runtime_import_failed", f"runtime helper could not be imported: {exc}", RUNTIME_REL.as_posix())]
    findings = []
    if schema_id != EXPECTED_PAYLOAD_SCHEMA_ID:
        findings.append(finding("error", "runtime_schema_id_mismatch", "runtime schema id does not match contract", RUNTIME_REL.as_posix()))
    if schema_version != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "runtime_schema_version_mismatch", "runtime schema version does not match contract", RUNTIME_REL.as_posix()))
    return findings


def validate_transaction_shape(transaction: Any, fixture_name: str) -> List[Dict[str, Any]]:
    findings = []
    if not isinstance(transaction, dict):
        return [finding("error", "fixture_transaction_not_object", "fixture transaction must be an object", fixture_name)]
    transaction_id = transaction.get("transaction_id")
    if not isinstance(transaction_id, str) or not TRANSACTION_ID_RE.match(transaction_id):
        findings.append(finding("error", "fixture_transaction_id_invalid", "fixture transaction_id does not match contract pattern", fixture_name))
    return findings


def validate_fixture(repo_root: Path, fixture_path: Path) -> Dict[str, Any]:
    rel = fixture_path.relative_to(repo_root).as_posix()
    try:
        case = load_json(fixture_path)
    except Exception as exc:
        return {"fixture": rel, "status": "fail", "findings": [finding("error", "fixture_invalid_json", f"fixture does not parse as JSON: {exc}", rel)]}
    if not isinstance(case, dict):
        return {"fixture": rel, "status": "fail", "findings": [finding("error", "fixture_root_not_object", "fixture root must be an object", rel)]}

    findings = []
    for key in ("document", "transaction", "expected_status"):
        if key not in case:
            findings.append(finding("error", "fixture_missing_field", f"fixture is missing required field: {key}", rel))
    if findings:
        return {"fixture": rel, "status": "fail", "findings": findings}
    findings.extend(validate_transaction_shape(case.get("transaction"), rel))

    try:
        _schema_id, _schema_version, apply_patch_transaction = import_runtime(repo_root)
        result = apply_patch_transaction(case["document"], case["transaction"])
    except Exception as exc:
        findings.append(finding("error", "fixture_runtime_error", f"runtime apply raised: {exc}", rel))
        return {"fixture": rel, "status": "fail", "findings": findings}

    expected_status = case.get("expected_status")
    if result.status != expected_status:
        findings.append(finding("error", "fixture_status_mismatch", f"expected {expected_status}, got {result.status}", rel))
    expected_code = case.get("expected_code")
    if expected_code:
        codes = {item.code for item in result.findings}
        if expected_code not in codes:
            findings.append(finding("error", "fixture_code_missing", f"expected finding code {expected_code}", rel))
    if result.status == "ok":
        expected_content = case.get("expected_content")
        if expected_content is not None and (not result.document or result.document.get("content") != expected_content):
            findings.append(finding("error", "fixture_content_mismatch", "patched content does not match expected content", rel))
        expected_hash = case.get("expected_after_hash")
        if expected_hash and result.after_hash != expected_hash:
            findings.append(finding("error", "fixture_hash_mismatch", "after hash does not match expected hash", rel))
    if result.status == "refused" and result.document is not None:
        findings.append(finding("error", "fixture_refusal_returned_document", "refused transaction must not return a patched document", rel))

    return {"fixture": rel, "status": "pass" if not findings else "fail", "findings": findings}


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    fixture_root = repo_root / FIXTURE_DIR_REL
    if not fixture_root.exists():
        return {
            "status": "fail",
            "fixtures": [],
            "findings": [finding("error", "fixture_root_missing", f"missing fixture root: {FIXTURE_DIR_REL.as_posix()}", FIXTURE_DIR_REL.as_posix())],
        }
    fixture_paths = sorted(fixture_root.glob("*.json"), key=lambda path: path.name)
    results = [validate_fixture(repo_root, path) for path in fixture_paths]
    findings = []
    if not fixture_paths:
        findings.append(finding("error", "fixtures_empty", "document patch transaction fixtures are missing", FIXTURE_DIR_REL.as_posix()))
    valid_count = sum(1 for item in results if Path(item["fixture"]).name.startswith("valid_"))
    invalid_count = sum(1 for item in results if Path(item["fixture"]).name.startswith("invalid_"))
    if valid_count < 1:
        findings.append(finding("error", "valid_fixture_missing", "at least one valid fixture is required", FIXTURE_DIR_REL.as_posix()))
    if invalid_count < 1:
        findings.append(finding("error", "invalid_fixture_missing", "at least one invalid fixture is required", FIXTURE_DIR_REL.as_posix()))
    status = "pass" if not findings and all(item["status"] == "pass" for item in results) else "fail"
    return {"status": status, "fixtures": results, "findings": findings}


def summarize(findings: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "errors": sum(1 for item in findings if item.get("level") == "error"),
        "warnings": sum(1 for item in findings if item.get("level") == "warning"),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail when validation findings contain errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--fixtures", action="store_true", help="Validate runtime fixtures")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_schema(repo_root))
    findings.extend(validate_contract(repo_root))
    findings.extend(validate_runtime(repo_root))
    fixture_result = validate_fixtures(repo_root) if args.fixtures else {"status": "not_run", "fixtures": [], "findings": []}
    findings.extend(fixture_result.get("findings", []))
    for fixture in fixture_result.get("fixtures", []):
        findings.extend(fixture.get("findings", []))

    counts = summarize(findings)
    status = "pass"
    if counts["errors"]:
        status = "fail"
    if args.fixtures and fixture_result.get("status") != "pass":
        status = "fail"

    output = {
        "validator": "check_document_patch_transactions",
        "status": status,
        "contract": CONTRACT_REL.as_posix(),
        "schema": SCHEMA_REL.as_posix(),
        "runtime": RUNTIME_REL.as_posix(),
        "summary": counts,
        "findings": findings,
        "fixtures": fixture_result,
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"document_patch_transactions: {status}")
        print(f"errors: {counts['errors']}")
        print(f"warnings: {counts['warnings']}")
        if args.fixtures:
            print(f"fixtures: {fixture_result.get('status')}")
        for item in findings:
            print(f"{item['level'].upper()}: {item['code']}: {item['message']}")

    if args.strict and status != "pass":
        return 1
    if args.fixtures and fixture_result.get("status") != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
