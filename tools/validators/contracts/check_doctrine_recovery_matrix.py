#!/usr/bin/env python3
"""Validate the Dominium doctrine recovery matrix registry and fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


DOC_REL = Path("docs/governance/DOMINIUM_DOCTRINE_RECOVERY_MATRIX.md")
SCHEMA_REL = Path("contracts/governance/doctrine_recovery_matrix.schema.json")
REGISTRY_REL = Path("contracts/registry/governance/doctrine_recovery_matrix.json")
FIXTURE_DIR_REL = Path("tests/contract/doctrine_recovery_matrix/fixtures")

EXPECTED_SCHEMA_ID = "dominium.governance.doctrine_recovery_matrix.v1"
EXPECTED_STATUS = "derived_non_canonical"
EXPECTED_AUTHORITY_PREFIX = [
    "docs/canon/constitution_v1.md",
    "docs/canon/glossary_v1.md",
    "AGENTS.md",
]
REQUIRED_DRIFT_KINDS = {
    "doc_drift",
    "generated_mirror_drift",
    "validator_drift",
    "status_file_drift",
}
REQUIRED_ACTIONS = {
    "preserve_higher_authority",
    "refresh_derived_projection",
    "repair_validator_contract",
    "record_status_staleness",
    "quarantine_same_tier_conflict",
    "route_human_review",
    "refuse_silent_promotion",
}
REQUIRED_REVIEW_GATES = {
    "none_if_lower_artifact_only",
    "protected_root_review",
    "contract_schema_review",
    "ownership_review_required",
    "quarantine_required",
    "human_review_required",
}
REQUIRED_PROTECTED_ROOTS = {
    "docs/canon/**",
    "AGENTS.md",
    "docs/planning/AUTHORITY_ORDER.md",
    "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md",
    "docs/planning/MERGED_PROGRAM_STATE.md",
    "docs/planning/EXTEND_NOT_REPLACE_LEDGER.md",
    "docs/planning/GATES_AND_PROOFS.md",
    "docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md",
    "specs/reality/**",
    "schema/**",
    "docs/release/**",
    "release/**",
    "repo/**",
    "updates/**",
    "security/**",
    "build/**",
    "archive/generated/artifacts/**",
    ".xstack_cache/**",
    "run_meta/**",
}
PROMOTION_FORBIDDEN_TERMS = (
    "promote to canon",
    "promote as canon",
    "treat as canon",
    "make canonical",
)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def string_values(items: Iterable[Any], key: str) -> Set[str]:
    values: Set[str] = set()
    for item in items:
        if isinstance(item, dict) and item.get(key):
            values.add(str(item[key]))
    return values


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def validate_json_surfaces(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in (SCHEMA_REL, REGISTRY_REL):
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json_surface", f"missing JSON surface: {rel.as_posix()}"))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}"))
            continue
        if not isinstance(data, dict):
            findings.append(finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object"))
    return findings


def validate_schema(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    try:
        schema = load_json(repo_root / SCHEMA_REL)
    except Exception as exc:
        return [finding("error", "schema_unreadable", f"schema is unreadable: {exc}", SCHEMA_REL.as_posix())]
    if schema.get("$id") != "dominium.governance.doctrine_recovery_matrix.schema.v1":
        findings.append(finding("error", "schema_bad_id", "schema $id is unexpected", SCHEMA_REL.as_posix()))
    required = set(as_list(schema.get("required")))
    for key in ("schema_id", "authority_order", "protected_roots", "recovery_actions", "review_gates", "matrix"):
        if key not in required:
            findings.append(finding("error", "schema_missing_required_key", f"schema does not require {key}", SCHEMA_REL.as_posix()))
    return findings


def validate_authority_order(data: Dict[str, Any], rel: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    order = as_list(data.get("authority_order"))
    if len(order) < len(EXPECTED_AUTHORITY_PREFIX):
        return [finding("error", "authority_order_too_short", "authority_order must include canon, glossary, and AGENTS.md", rel)]

    paths = [str(item.get("path", "")) for item in order if isinstance(item, dict)]
    if paths[:3] != EXPECTED_AUTHORITY_PREFIX:
        findings.append(
            finding(
                "error",
                "authority_order_prefix",
                "authority_order must begin with constitution, glossary, and AGENTS.md",
                rel,
            )
        )

    ranks: List[int] = []
    seen_paths: Set[str] = set()
    for index, item in enumerate(order):
        if not isinstance(item, dict):
            findings.append(finding("error", "authority_order_entry_shape", f"authority_order entry {index} must be an object", rel))
            continue
        rank = item.get("rank")
        path = str(item.get("path", ""))
        if not isinstance(rank, int):
            findings.append(finding("error", "authority_rank_missing", f"authority_order entry {index} has no integer rank", rel))
        else:
            ranks.append(rank)
        if not path:
            findings.append(finding("error", "authority_path_missing", f"authority_order entry {index} is missing path", rel))
        elif path in seen_paths:
            findings.append(finding("error", "authority_path_duplicate", f"duplicate authority path: {path}", rel))
        seen_paths.add(path)

    if ranks and ranks != sorted(ranks):
        findings.append(finding("error", "authority_rank_order", "authority ranks must be sorted ascending", rel))
    if ranks and sorted(ranks) != list(range(1, len(ranks) + 1)):
        findings.append(finding("error", "authority_rank_gap", "authority ranks must be contiguous from 1", rel))
    return findings


def validate_registry_core(data: Dict[str, Any], rel: str) -> Tuple[List[Dict[str, Any]], Dict[str, Set[str]]]:
    findings: List[Dict[str, Any]] = []
    if data.get("schema_id") != EXPECTED_SCHEMA_ID:
        findings.append(finding("error", "registry_bad_schema_id", "registry schema_id is unexpected", rel))
    if data.get("status") != EXPECTED_STATUS:
        findings.append(finding("error", "registry_not_derived", "registry status must be derived_non_canonical", rel))
    notice = str(data.get("non_canonical_notice", "")).lower()
    for term in ("derived", "does not change", "canon"):
        if term not in notice:
            findings.append(finding("error", "registry_notice_incomplete", f"non_canonical_notice must mention {term}", rel))

    findings.extend(validate_authority_order(data, rel))

    drift_ids = string_values(as_list(data.get("drift_kinds")), "id")
    action_ids = string_values(as_list(data.get("recovery_actions")), "id")
    gate_ids = string_values(as_list(data.get("review_gates")), "id")
    protected_paths = string_values(as_list(data.get("protected_roots")), "path")
    surface_ids = string_values(as_list(data.get("matrix")), "surface_id")

    missing_drift = sorted(REQUIRED_DRIFT_KINDS - drift_ids)
    if missing_drift:
        findings.append(finding("error", "required_drift_kinds_missing", f"missing drift kinds: {', '.join(missing_drift)}", rel))
    missing_actions = sorted(REQUIRED_ACTIONS - action_ids)
    if missing_actions:
        findings.append(finding("error", "required_recovery_actions_missing", f"missing recovery actions: {', '.join(missing_actions)}", rel))
    missing_gates = sorted(REQUIRED_REVIEW_GATES - gate_ids)
    if missing_gates:
        findings.append(finding("error", "required_review_gates_missing", f"missing review gates: {', '.join(missing_gates)}", rel))
    missing_roots = sorted(REQUIRED_PROTECTED_ROOTS - protected_paths)
    if missing_roots:
        findings.append(finding("error", "required_protected_roots_missing", f"missing protected roots: {', '.join(missing_roots)}", rel))

    for item in as_list(data.get("drift_kinds")):
        if not isinstance(item, dict):
            continue
        action = str(item.get("default_recovery_action", ""))
        if action and action not in action_ids:
            findings.append(finding("error", "drift_unknown_default_action", f"drift kind {item.get('id')} references unknown action {action}", rel))

    for item in as_list(data.get("recovery_actions")):
        if not isinstance(item, dict):
            continue
        gate = str(item.get("default_review_gate", ""))
        if gate and gate not in gate_ids:
            findings.append(finding("error", "action_unknown_default_gate", f"action {item.get('id')} references unknown gate {gate}", rel))

    for item in as_list(data.get("protected_roots")):
        if not isinstance(item, dict):
            continue
        action = str(item.get("default_recovery_action", ""))
        gate = str(item.get("review_gate", ""))
        if action and action not in action_ids:
            findings.append(finding("error", "protected_root_unknown_action", f"protected root {item.get('path')} references unknown action {action}", rel))
        if gate and gate not in gate_ids:
            findings.append(finding("error", "protected_root_unknown_gate", f"protected root {item.get('path')} references unknown gate {gate}", rel))

    return findings, {
        "drift_ids": drift_ids,
        "action_ids": action_ids,
        "gate_ids": gate_ids,
        "protected_paths": protected_paths,
        "surface_ids": surface_ids,
    }


def looks_like_generated_promotion(case: Dict[str, Any]) -> bool:
    text = " ".join(str(case.get(key, "")) for key in ("when", "disposition", "recovery_action")).lower()
    return any(term in text for term in PROMOTION_FORBIDDEN_TERMS)


def validate_matrix_entries(data: Dict[str, Any], rel: str, sets: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    covered_drift: Set[str] = set()
    entries = as_list(data.get("matrix"))
    if not entries:
        return [finding("error", "matrix_empty", "matrix must contain entries", rel)]

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(finding("error", "matrix_entry_shape", f"matrix entry {index} must be an object", rel))
            continue
        surface_id = str(entry.get("surface_id", ""))
        entry_path = f"{rel}:{surface_id or index}"
        if not surface_id:
            findings.append(finding("error", "surface_missing_id", "matrix entry missing surface_id", rel))
        elif surface_id in seen:
            findings.append(finding("error", "surface_duplicate_id", f"duplicate surface_id: {surface_id}", entry_path))
        seen.add(surface_id)

        if not as_list(entry.get("source_paths")):
            findings.append(finding("error", "surface_missing_sources", "matrix entry must include source_paths", entry_path))

        for root in as_list(entry.get("protected_roots")):
            if isinstance(root, str) and root not in sets["protected_paths"]:
                findings.append(finding("error", "surface_unknown_protected_root", f"unknown protected root: {root}", entry_path))

        cases = as_list(entry.get("drift_cases"))
        if not cases:
            findings.append(finding("error", "surface_missing_drift_cases", "matrix entry must include drift_cases", entry_path))
            continue
        for case_index, case in enumerate(cases):
            if not isinstance(case, dict):
                findings.append(finding("error", "drift_case_shape", f"drift case {case_index} must be an object", entry_path))
                continue
            drift_kind = str(case.get("drift_kind", ""))
            action = str(case.get("recovery_action", ""))
            gate = str(case.get("review_gate", ""))
            if drift_kind not in sets["drift_ids"]:
                findings.append(finding("error", "drift_case_unknown_kind", f"unknown drift kind: {drift_kind}", entry_path))
            else:
                covered_drift.add(drift_kind)
            if action not in sets["action_ids"]:
                findings.append(finding("error", "drift_case_unknown_action", f"unknown recovery action: {action}", entry_path))
            if gate not in sets["gate_ids"]:
                findings.append(finding("error", "drift_case_unknown_gate", f"unknown review gate: {gate}", entry_path))
            if gate == "":
                findings.append(finding("error", "drift_case_missing_review_gate", "drift case must make review gate explicit", entry_path))
            if drift_kind in {"generated_mirror_drift", "status_file_drift"} and looks_like_generated_promotion(case):
                findings.append(finding("error", "silent_promotion_forbidden", "generated/status drift must not promote evidence to canon", entry_path))

    missing_coverage = sorted(REQUIRED_DRIFT_KINDS - covered_drift)
    if missing_coverage:
        findings.append(finding("error", "matrix_missing_required_drift_coverage", f"matrix entries do not cover drift kinds: {', '.join(missing_coverage)}", rel))
    return findings


def validate_doc_alignment(repo_root: Path, surface_ids: Set[str], action_ids: Set[str]) -> List[Dict[str, Any]]:
    path = repo_root / DOC_REL
    if not path.exists():
        return [finding("error", "doc_missing", f"missing governance doc: {DOC_REL.as_posix()}")]
    text = path.read_text(encoding="utf-8-sig")
    findings: List[Dict[str, Any]] = []
    for required in ("Non-Canonical", "Recovery Actions", "Protected Roots", "Surface Matrix", "Review Gates"):
        if required not in text:
            findings.append(finding("error", "doc_missing_section", f"governance doc missing section text: {required}", DOC_REL.as_posix()))
    for surface_id in sorted(surface_ids):
        if surface_id not in text:
            findings.append(finding("error", "doc_missing_surface_id", f"governance doc does not mention surface_id {surface_id}", DOC_REL.as_posix()))
    for action_id in sorted(action_ids):
        if action_id not in text:
            findings.append(finding("error", "doc_missing_action_id", f"governance doc does not mention recovery action {action_id}", DOC_REL.as_posix()))
    return findings


def validate_registry(repo_root: Path, rel: Path = REGISTRY_REL) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    path = repo_root / rel
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "registry_unreadable", f"registry is unreadable: {exc}", rel.as_posix())], {}
    if not isinstance(data, dict):
        return [finding("error", "registry_root_not_object", "registry root must be an object", rel.as_posix())], {}

    findings, sets = validate_registry_core(data, rel.as_posix())
    findings.extend(validate_matrix_entries(data, rel.as_posix(), sets))
    if rel == REGISTRY_REL:
        findings.extend(validate_doc_alignment(repo_root, sets["surface_ids"], sets["action_ids"]))
    return findings, {
        "entries": len(as_list(data.get("matrix"))),
        "drift_kinds": len(sets.get("drift_ids", set())),
        "actions": len(sets.get("action_ids", set())),
        "review_gates": len(sets.get("gate_ids", set())),
        "protected_roots": len(sets.get("protected_paths", set())),
    }


def validate_fixture_entry(data: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
    registry = load_json(Path.cwd() / REGISTRY_REL) if (Path.cwd() / REGISTRY_REL).exists() else {}
    core_findings, sets = validate_registry_core(registry, REGISTRY_REL.as_posix()) if registry else ([], {})
    if core_findings:
        return [finding("error", "fixture_context_invalid", "main registry context is invalid; cannot validate entry fixture", name)]
    return validate_matrix_entries({"matrix": [data]}, name, sets)


def validate_fixtures(repo_root: Path) -> Dict[str, Any]:
    fixture_root = repo_root / FIXTURE_DIR_REL
    results: List[Dict[str, Any]] = []
    cases = [
        ("valid_matrix_entry.json", "entry", False),
        ("invalid_entry_missing_review_gate.json", "entry", True),
        ("invalid_entry_generated_promotes_canon.json", "entry", True),
        ("invalid_registry_authority_order.json", "registry", True),
        ("invalid_registry_missing_protected_roots.json", "registry", True),
    ]

    previous_cwd = Path.cwd()
    try:
        # Fixture entry validation reuses the main registry dictionaries.
        import os

        os.chdir(str(repo_root))
        for name, kind, expect_errors in cases:
            path = fixture_root / name
            rel = (FIXTURE_DIR_REL / name).as_posix()
            try:
                data = load_json(path)
                if kind == "entry":
                    findings = validate_fixture_entry(data, rel)
                    if name == "valid_matrix_entry.json":
                        findings = [
                            item
                            for item in findings
                            if item.get("code") != "matrix_missing_required_drift_coverage"
                        ]
                else:
                    findings, _summary = validate_registry(repo_root, FIXTURE_DIR_REL / name)
            except Exception as exc:
                findings = [finding("error", "fixture_unreadable", f"fixture is unreadable: {exc}", rel)]
            has_errors = any(item["level"] == "error" for item in findings)
            status = "pass" if has_errors == expect_errors else "fail"
            results.append({"fixture": rel, "status": status, "expected_errors": expect_errors, "findings": findings})
    finally:
        import os

        os.chdir(str(previous_cwd))

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
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--strict", action="store_true", help="Fail on errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--fixtures", action="store_true", help="Validate doctrine recovery matrix fixtures.")
    parser.add_argument("--list", action="store_true", help="List matrix surface IDs.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_surfaces(repo_root))
    findings.extend(validate_schema(repo_root))
    registry_findings, registry_summary = validate_registry(repo_root)
    findings.extend(registry_findings)
    fixture_result = validate_fixtures(repo_root) if args.fixtures else {"status": "not_run", "fixtures": []}

    counts = summarize(findings)
    status = "pass" if counts["errors"] == 0 else "fail"
    if args.fixtures and fixture_result["status"] != "pass":
        status = "fail"

    output = {
        "validator": "check_doctrine_recovery_matrix",
        "status": status,
        "registry": REGISTRY_REL.as_posix(),
        "registry_summary": registry_summary,
        "summary": counts,
        "fixtures": fixture_result,
        "findings": findings,
    }

    if args.list:
        data = load_json(repo_root / REGISTRY_REL)
        for surface_id in sorted(string_values(as_list(data.get("matrix")), "surface_id")):
            print(surface_id)
    elif args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"doctrine recovery matrix: {status}")
        print(f"entries: {registry_summary.get('entries', 0)}")
        print(f"drift_kinds: {registry_summary.get('drift_kinds', 0)}")
        print(f"actions: {registry_summary.get('actions', 0)}")
        print(f"review_gates: {registry_summary.get('review_gates', 0)}")
        print(f"protected_roots: {registry_summary.get('protected_roots', 0)}")
        print(f"errors: {counts['errors']}")
        print(f"warnings: {counts['warnings']}")
        if args.fixtures:
            print(f"fixtures: {fixture_result['status']}")
        for item in findings[:80]:
            location = f" {item['path']}:" if item.get("path") else ""
            print(f"{item['level'].upper()} {item['code']}:{location} {item['message']}")

    if args.strict and status != "pass":
        return 1
    if args.fixtures and fixture_result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
