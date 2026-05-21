#!/usr/bin/env python3
"""Validate the Dominium project graph service contract, helper, and fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - Python 3.8 fallback
    tomllib = None


REPO_ROOT_FROM_FILE = Path(__file__).resolve().parents[3]
if str(REPO_ROOT_FROM_FILE) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_FROM_FILE))

from runtime.project_graph import (  # noqa: E402
    PROJECT_GRAPH_SCHEMA_ID,
    PROJECT_GRAPH_SCHEMA_VERSION,
    canonicalize_project_graph,
    load_project_graph_payload,
    project_graph_fingerprint,
    topological_node_order,
    validate_project_graph_payload,
)


CONTRACT_REL = Path("contracts/project_graph/project_graph_service.contract.toml")
SCHEMA_REL = Path("contracts/project_graph/project_graph.schema.json")
RUNTIME_HELPER_REL = Path("runtime/project_graph/service.py")
RUNTIME_INIT_REL = Path("runtime/project_graph/__init__.py")
EVIDENCE_REF_SCHEMA_REL = Path("contracts/evidence/evidence_ref.schema.json")
RESULT_SCHEMA_REL = Path("contracts/result/result.schema.json")
FIXTURE_DIR_REL = Path("tests/contract/project_graph_service/fixtures")

EXPECTED_CONTRACT_ID = "dominium.project_graph.service.v1"
EXPECTED_FIXTURES = {
    "valid_project_graph.json": True,
    "valid_project_graph_shuffled.json": True,
    "invalid_dependency_cycle.json": False,
    "invalid_duplicate_node.json": False,
    "invalid_missing_dependency_target.json": False,
    "invalid_proof_without_evidence.json": False,
}


class CheckResult:
    def __init__(self) -> None:
        self.findings: List[Dict[str, Any]] = []
        self.info: Dict[str, Any] = {}

    @property
    def errors(self) -> List[Dict[str, Any]]:
        return [item for item in self.findings if item["level"] == "error"]

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return [item for item in self.findings if item["level"] == "warning"]

    def add(self, level: str, code: str, message: str, path: Optional[Path | str] = None, **fields: Any) -> None:
        item: Dict[str, Any] = {"level": level, "code": code, "message": message}
        if path is not None:
            item["path"] = str(path).replace("\\", "/")
        for key, value in fields.items():
            if value is not None:
                item[key] = value
        self.findings.append(item)

    def error(self, code: str, message: str, path: Optional[Path | str] = None, **fields: Any) -> None:
        self.add("error", code, message, path, **fields)

    def warn(self, code: str, message: str, path: Optional[Path | str] = None, **fields: Any) -> None:
        self.add("warning", code, message, path, **fields)


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
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return dict(payload)


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def check_contract_and_schema(repo_root: Path, result: CheckResult) -> None:
    required_paths = [
        CONTRACT_REL,
        SCHEMA_REL,
        RUNTIME_HELPER_REL,
        RUNTIME_INIT_REL,
        EVIDENCE_REF_SCHEMA_REL,
        RESULT_SCHEMA_REL,
    ]
    for rel in required_paths:
        if not (repo_root / rel).exists():
            result.error("PGS-MISSING-FILE", "required project graph service file is missing", rel)

    try:
        contract = load_toml(repo_root / CONTRACT_REL)
    except Exception as exc:
        result.error("PGS-CONTRACT-PARSE", f"project graph service contract does not parse: {exc}", CONTRACT_REL)
        contract = {}

    contract_section = dict(contract.get("contract") or {})
    if contract_section.get("id") != EXPECTED_CONTRACT_ID:
        result.error(
            "PGS-CONTRACT-ID",
            "project graph service contract id is incorrect",
            CONTRACT_REL,
            expected=EXPECTED_CONTRACT_ID,
            actual=contract_section.get("id"),
        )

    boundary = dict(contract.get("boundary") or {})
    expected_false = {
        "service_is_truth_owner",
        "mutates_authoritative_truth",
        "workbench_ui_scope",
        "release_projection_scope",
        "broad_project_explorer_scope",
    }
    for key in sorted(expected_false):
        if boundary.get(key) is not False:
            result.error("PGS-BOUNDARY-FLAG", f"boundary.{key} must be false", CONTRACT_REL, field=f"boundary.{key}")
    if boundary.get("process_only_truth_mutation_required_for_future_writes") is not True:
        result.error(
            "PGS-PROCESS-ONLY-FUTURE-WRITES",
            "future truth writes must remain process-only",
            CONTRACT_REL,
            field="boundary.process_only_truth_mutation_required_for_future_writes",
        )

    try:
        schema = load_json(repo_root / SCHEMA_REL)
    except Exception as exc:
        result.error("PGS-SCHEMA-PARSE", f"project graph schema does not parse: {exc}", SCHEMA_REL)
        schema = {}

    if schema.get("$id") != PROJECT_GRAPH_SCHEMA_ID:
        result.error("PGS-SCHEMA-ID", "project graph schema id is incorrect", SCHEMA_REL, expected=PROJECT_GRAPH_SCHEMA_ID, actual=schema.get("$id"))
    properties = dict(schema.get("properties") or {})
    if dict(properties.get("schema_version") or {}).get("const") != PROJECT_GRAPH_SCHEMA_VERSION:
        result.error(
            "PGS-SCHEMA-VERSION",
            "project graph schema version const is incorrect",
            SCHEMA_REL,
            expected=PROJECT_GRAPH_SCHEMA_VERSION,
            actual=dict(properties.get("schema_version") or {}).get("const"),
        )
    required = set(_as_list(schema.get("required")))
    missing_required = {"schema_id", "schema_version", "graph_id", "owner", "stability", "nodes", "edges", "dependencies", "proofs"} - required
    if missing_required:
        result.error("PGS-SCHEMA-REQUIRED", "project graph schema is missing required root fields", SCHEMA_REL, missing=sorted(missing_required))

    defs = dict(schema.get("$defs") or {})
    for key in ("node", "edge", "dependency", "proof"):
        if key not in defs:
            result.error("PGS-SCHEMA-DEF", f"project graph schema missing $defs.{key}", SCHEMA_REL)
    proof_props = dict(dict(defs.get("proof") or {}).get("properties") or {})
    proof_refs = json.dumps(proof_props, sort_keys=True)
    if "../evidence/evidence_ref.schema.json" not in proof_refs:
        result.error("PGS-EVIDENCE-REF", "proof schema must reference evidence_ref schema", SCHEMA_REL)
    if "../result/result.schema.json" not in proof_refs:
        result.error("PGS-RESULT-REF", "proof schema must reference result schema", SCHEMA_REL)


def check_fixture(repo_root: Path, rel: Path, expected_valid: bool, result: CheckResult) -> Dict[str, Any]:
    path = repo_root / rel
    if not path.exists():
        result.error("PGS-FIXTURE-MISSING", "project graph fixture is missing", rel)
        return {"path": rel.as_posix(), "expected_valid": expected_valid, "actual_valid": False, "status": "missing"}
    try:
        payload = load_project_graph_payload(path)
    except Exception as exc:
        result.error("PGS-FIXTURE-PARSE", f"project graph fixture does not parse: {exc}", rel)
        return {"path": rel.as_posix(), "expected_valid": expected_valid, "actual_valid": False, "status": "parse_error"}

    validation = validate_project_graph_payload(payload)
    actual_valid = validation.valid
    if actual_valid != expected_valid:
        result.error(
            "PGS-FIXTURE-EXPECTATION",
            "project graph fixture did not match expected validity",
            rel,
            expected=expected_valid,
            actual=actual_valid,
            diagnostics=[item.as_dict() for item in validation.findings],
        )
    return {
        "path": rel.as_posix(),
        "expected_valid": expected_valid,
        "actual_valid": actual_valid,
        "finding_count": len(validation.findings),
        "status": "pass" if actual_valid == expected_valid else "fail",
    }


def check_fixtures(repo_root: Path, result: CheckResult) -> None:
    fixture_results: List[Dict[str, Any]] = []
    for filename, expected_valid in sorted(EXPECTED_FIXTURES.items()):
        fixture_results.append(check_fixture(repo_root, FIXTURE_DIR_REL / filename, expected_valid, result))
    result.info["fixtures"] = fixture_results

    valid_rel = FIXTURE_DIR_REL / "valid_project_graph.json"
    shuffled_rel = FIXTURE_DIR_REL / "valid_project_graph_shuffled.json"
    try:
        valid_payload = load_project_graph_payload(repo_root / valid_rel)
        shuffled_payload = load_project_graph_payload(repo_root / shuffled_rel)
    except Exception as exc:
        result.error("PGS-DETERMINISM-FIXTURE-PARSE", f"could not load valid determinism fixtures: {exc}", FIXTURE_DIR_REL)
        return

    valid_validation = validate_project_graph_payload(valid_payload)
    shuffled_validation = validate_project_graph_payload(shuffled_payload)
    if not valid_validation.valid or not shuffled_validation.valid:
        result.error("PGS-DETERMINISM-FIXTURE-INVALID", "determinism fixtures must both be valid", FIXTURE_DIR_REL)
        return

    valid_hash = project_graph_fingerprint(valid_payload)
    shuffled_hash = project_graph_fingerprint(shuffled_payload)
    valid_order = topological_node_order(valid_payload)
    shuffled_order = topological_node_order(shuffled_payload)
    result.info["determinism"] = {
        "valid_hash": valid_hash,
        "shuffled_hash": shuffled_hash,
        "valid_order": valid_order,
        "shuffled_order": shuffled_order,
    }
    if valid_hash != shuffled_hash:
        result.error("PGS-HASH-NONDETERMINISTIC", "valid shuffled graph fixtures must have the same fingerprint", FIXTURE_DIR_REL)
    if valid_order != shuffled_order:
        result.error("PGS-ORDER-NONDETERMINISTIC", "valid shuffled graph fixtures must have the same topological order", FIXTURE_DIR_REL)
    canonical = canonicalize_project_graph(shuffled_payload)
    if [row.get("node_id") for row in canonical.get("nodes", [])] != sorted(row.get("node_id") for row in canonical.get("nodes", [])):
        result.error("PGS-CANONICAL-NODE-ORDER", "canonicalized nodes are not sorted by node_id", shuffled_rel)


def run_checks(repo_root: Path, include_fixtures: bool) -> CheckResult:
    result = CheckResult()
    check_contract_and_schema(repo_root, result)
    if include_fixtures:
        check_fixtures(repo_root, result)
    result.info["summary"] = {
        "errors": len(result.errors),
        "warnings": len(result.warnings),
        "fixtures_checked": len(result.info.get("fixtures", [])),
    }
    return result


def emit_text(result: CheckResult) -> None:
    status = "PASS" if not result.errors else "FAIL"
    print(f"project graph service: {status}")
    print(f"errors: {len(result.errors)}")
    print(f"warnings: {len(result.warnings)}")
    if "fixtures" in result.info:
        print(f"fixtures: {len(result.info['fixtures'])} checked")
    if "determinism" in result.info:
        order = result.info["determinism"].get("valid_order", [])
        print("topological_order: {}".format(", ".join(order)))
    for item in result.findings:
        path = f" {item['path']}" if item.get("path") else ""
        print(f"{item['level'].upper()}: {item['code']}:{path} {item['message']}")


def emit_json(result: CheckResult) -> None:
    print(
        json.dumps(
            {
                "status": "PASS" if not result.errors else "FAIL",
                "findings": result.findings,
                "info": result.info,
            },
            indent=2,
            sort_keys=True,
        )
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on project graph service errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--fixtures", action="store_true", help="Validate project graph fixtures")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    result = run_checks(repo_root, include_fixtures=bool(args.fixtures or args.strict))
    if args.json:
        emit_json(result)
    else:
        emit_text(result)
    if args.strict and result.errors:
        return 1
    if args.fixtures and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
