#!/usr/bin/env python3
"""Validate Dominium composition resolver law, schemas, and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


CONTRACT_REL = Path("contracts/composition/composition_resolver.contract.toml")
PLAN_SCHEMA_REL = Path("contracts/composition/composition_resolver_plan.schema.json")
SOURCE_KIND_REGISTRY_REL = Path("contracts/composition/composition_source_kind.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/composition_resolver/fixtures")

EXPECTED_CONTRACT_ID = "dominium.composition.resolver_law.v1"
EXPECTED_PLAN_SCHEMA_ID = "dominium.composition.resolver_plan.v1"
EXPECTED_PLAN_SCHEMA_CONST = "dominium.composition.resolver_plan"
EXPECTED_SCHEMA_VERSION = "1.0.0"
EXPECTED_ALGORITHM = "canonical_layered_stable_sort"
EXPECTED_SOURCE_ORDER = [
    "package_descriptor",
    "module_composition",
    "workbench_workspace",
    "app_composition",
]
EXPECTED_TIE_BREAKERS = [
    "source_kind_rank",
    "descriptor_id_casefold",
    "step_id_casefold",
    "source_ref_casefold",
]
ALLOWED_ACTIONS = {"include", "require", "select", "refuse", "degrade", "defer"}
ALLOWED_DECISIONS = {"refused", "degraded", "selected_by_policy", "deferred_for_review"}
FORBIDDEN_DECISIONS = {"silent_fallback", "ignored", "best_effort"}
REQUIRED_NON_GOAL_TOKENS = {"runtime_loader", "package_mounting", "schema_migration"}
PRIVATE_BINDING_KEYS = {
    "private_path",
    "private_paths",
    "private_dependencies",
    "private_tool_calls",
    "direct_call",
    "handler_path",
    "tool_path",
    "implementation_path",
}
PATHLIKE_RE = re.compile(r"[/\\]|\.\.(?:/|\\)|\.(json|toml|py|exe|dll|so|dylib)$", re.IGNORECASE)
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")


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
    current_array: Optional[List[Dict[str, Any]]] = None
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            current = {}
            current_array = root.setdefault(section, [])
            current_array.append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            current_array = None
            for part in line[1:-1].strip().split("."):
                current = current.setdefault(part, {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line {lineno}: {original}")
        if current_array is not None and current not in current_array:
            current_array.append(current)
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


def has_error(findings: Sequence[Dict[str, Any]]) -> bool:
    return any(item.get("level") == "error" for item in findings)


def normalized_ref(ref: Dict[str, Any]) -> str:
    return f"{ref.get('ref_kind', '')}:{ref.get('ref_id', '')}"


def is_token(value: str) -> bool:
    return bool(value and TOKEN_RE.match(value) and not PATHLIKE_RE.search(value))


def string_values(values: Iterable[Any]) -> List[str]:
    return [str(value) for value in values if isinstance(value, (str, int))]


def validate_source_kind_registry(data: Dict[str, Any], path: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    findings: List[Dict[str, Any]] = []
    if data.get("$id") != "dominium.composition.source_kind.registry.v1":
        findings.append(finding("error", "source_kind_registry_bad_id", "source kind registry has unexpected $id", path))
    if data.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "source_kind_registry_bad_version", "source kind registry schema_version must be 1.0.0", path))
    canonical_order = string_values(data.get("canonical_order", []))
    if canonical_order != EXPECTED_SOURCE_ORDER:
        findings.append(finding("error", "source_kind_order_mismatch", "source kind canonical_order does not match resolver law", path))

    ranks: Dict[str, int] = {}
    seen_ranks: Set[int] = set()
    for item in as_list(data.get("kinds")):
        if not isinstance(item, dict):
            findings.append(finding("error", "source_kind_shape", "source kind entry must be an object", path))
            continue
        kind = str(item.get("id") or "")
        rank = item.get("rank")
        if kind not in EXPECTED_SOURCE_ORDER:
            findings.append(finding("error", "source_kind_unknown", f"unexpected source kind: {kind}", path))
        if not isinstance(rank, int):
            findings.append(finding("error", "source_kind_rank_missing", f"{kind} missing integer rank", path))
            continue
        if rank in seen_ranks:
            findings.append(finding("error", "source_kind_rank_duplicate", f"duplicate source kind rank: {rank}", path))
        seen_ranks.add(rank)
        ranks[kind] = rank
    if [kind for kind, _rank in sorted(ranks.items(), key=lambda item: item[1])] != EXPECTED_SOURCE_ORDER:
        findings.append(finding("error", "source_kind_rank_order_mismatch", "source kind ranks do not produce canonical order", path))
    return findings, ranks


def validate_contracts(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    findings: List[Dict[str, Any]] = []
    ranks: Dict[str, int] = {kind: index for index, kind in enumerate(EXPECTED_SOURCE_ORDER)}

    for rel in [PLAN_SCHEMA_REL, SOURCE_KIND_REGISTRY_REL]:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json_contract", f"missing {rel.as_posix()}", rel.as_posix()))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}", rel.as_posix()))
            continue
        if not isinstance(data, dict):
            findings.append(finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object", rel.as_posix()))
            continue
        if rel == PLAN_SCHEMA_REL:
            if data.get("$id") != EXPECTED_PLAN_SCHEMA_ID:
                findings.append(finding("error", "resolver_plan_schema_bad_id", "resolver plan schema has unexpected $id", rel.as_posix()))
            schema_id_const = data.get("properties", {}).get("schema_id", {}).get("const")
            if schema_id_const != EXPECTED_PLAN_SCHEMA_CONST:
                findings.append(finding("error", "resolver_plan_schema_bad_const", "resolver plan schema_id const mismatch", rel.as_posix()))
        if rel == SOURCE_KIND_REGISTRY_REL:
            registry_findings, ranks = validate_source_kind_registry(data, rel.as_posix())
            findings.extend(registry_findings)

    contract_path = repo_root / CONTRACT_REL
    if not contract_path.exists():
        findings.append(finding("error", "missing_toml_contract", f"missing {CONTRACT_REL.as_posix()}", CONTRACT_REL.as_posix()))
        return findings, ranks
    try:
        contract = load_toml(contract_path)
    except Exception as exc:
        findings.append(finding("error", "invalid_toml", f"{CONTRACT_REL.as_posix()} does not parse as TOML: {exc}", CONTRACT_REL.as_posix()))
        return findings, ranks

    if contract.get("contract", {}).get("id") != EXPECTED_CONTRACT_ID:
        findings.append(finding("error", "unexpected_contract_id", "composition resolver contract id mismatch", CONTRACT_REL.as_posix()))
    policy = contract.get("policy", {})
    required_policy = {
        "runtime_loader_implemented": False,
        "app_composer_implemented": False,
        "package_mounting_implemented": False,
        "resolver_mutates_truth": False,
        "descriptor_identity_is_path": False,
        "source_ref_is_semantic_authority": False,
        "private_dependencies_allowed": False,
        "deterministic_order_required": True,
        "duplicate_provides_require_conflict": True,
        "missing_dependencies_require_conflict": True,
        "silent_fallback_allowed": False,
        "stable_plans_require_proof": True,
    }
    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            findings.append(finding("error", "policy_value_mismatch", f"policy {key} must be {expected}", CONTRACT_REL.as_posix()))

    ordering = contract.get("ordering", {})
    if ordering.get("algorithm") != EXPECTED_ALGORITHM:
        findings.append(finding("error", "ordering_algorithm_mismatch", "unexpected resolver ordering algorithm", CONTRACT_REL.as_posix()))
    if string_values(ordering.get("source_kind_order", [])) != EXPECTED_SOURCE_ORDER:
        findings.append(finding("error", "ordering_source_kind_mismatch", "contract source_kind_order mismatch", CONTRACT_REL.as_posix()))
    if string_values(ordering.get("tie_breakers", [])) != EXPECTED_TIE_BREAKERS:
        findings.append(finding("error", "ordering_tie_breaker_mismatch", "contract tie_breakers mismatch", CONTRACT_REL.as_posix()))

    conflicts = contract.get("conflicts", {})
    decisions = set(string_values(conflicts.get("allowed_decisions", [])))
    if decisions != ALLOWED_DECISIONS:
        findings.append(finding("error", "conflict_decisions_mismatch", "allowed conflict decisions mismatch", CONTRACT_REL.as_posix()))
    forbidden = set(string_values(conflicts.get("forbidden_decisions", [])))
    if not FORBIDDEN_DECISIONS.issubset(forbidden):
        findings.append(finding("error", "conflict_forbidden_missing", "forbidden decisions must include silent fallback, ignored, and best effort", CONTRACT_REL.as_posix()))
    return findings, ranks


def validate_ref(item: Any, path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if not isinstance(item, dict):
        return [finding("error", "composition_ref_shape", "reference must be an object", path)]
    ref_kind = str(item.get("ref_kind") or "")
    ref_id = str(item.get("ref_id") or "")
    if not is_token(ref_kind):
        findings.append(finding("error", "composition_ref_bad_kind", f"bad ref_kind: {ref_kind}", path))
    if not is_token(ref_id):
        findings.append(finding("error", "composition_ref_bad_id", f"bad ref_id: {ref_id}", path))
    return findings


def find_private_bindings(value: Any, path: str, findings: List[Dict[str, Any]], trail: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            next_trail = f"{trail}.{key_text}"
            if key_text in PRIVATE_BINDING_KEYS and item:
                findings.append(finding("error", "composition_private_path_binding", f"private/path binding key is forbidden: {next_trail}", path))
            if key_text == "implementation_path_is_identity" and item is True:
                findings.append(finding("error", "composition_path_identity", "implementation_path_is_identity must not be true", path))
            if key_text.endswith("_id") and isinstance(item, str) and PATHLIKE_RE.search(item):
                findings.append(finding("error", "composition_path_as_id", f"path-like ID value at {next_trail}: {item}", path))
            find_private_bindings(item, path, findings, next_trail)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            find_private_bindings(item, path, findings, f"{trail}[{index}]")


def validate_plan(data: Dict[str, Any], *, path: str, ranks: Dict[str, int]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    find_private_bindings(data, path, findings)

    required = [
        "schema_id",
        "schema_version",
        "stability",
        "plan_id",
        "owner",
        "resolver_law",
        "ordering",
        "inputs",
        "steps",
        "conflicts",
        "proof",
        "non_goals",
    ]
    for key in required:
        if key not in data:
            findings.append(finding("error", "resolver_plan_missing_field", f"missing required field: {key}", path))
    if data.get("schema_id") != EXPECTED_PLAN_SCHEMA_CONST:
        findings.append(finding("error", "resolver_plan_bad_schema_id", "schema_id must be dominium.composition.resolver_plan", path))
    if data.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        findings.append(finding("error", "resolver_plan_bad_schema_version", "schema_version must be 1.0.0", path))
    if data.get("resolver_law") != EXPECTED_CONTRACT_ID:
        findings.append(finding("error", "resolver_plan_bad_law", "resolver_law must bind to composition resolver law v1", path))
    plan_id = str(data.get("plan_id") or "")
    if not is_token(plan_id):
        findings.append(finding("error", "resolver_plan_bad_id", f"bad plan_id: {plan_id}", path))
    if data.get("stability") == "stable" and not as_list(data.get("proof")):
        findings.append(finding("error", "resolver_plan_stable_without_proof", "stable resolver plans require proof", path))

    non_goal_text = " ".join(str(item) for item in as_list(data.get("non_goals"))).lower()
    for token in REQUIRED_NON_GOAL_TOKENS:
        if token not in non_goal_text:
            findings.append(finding("error", "resolver_plan_missing_non_goal", f"non_goals must mention {token}", path))

    ordering = data.get("ordering", {})
    if not isinstance(ordering, dict):
        findings.append(finding("error", "resolver_ordering_shape", "ordering must be an object", path))
    else:
        if ordering.get("algorithm") != EXPECTED_ALGORITHM:
            findings.append(finding("error", "resolver_ordering_bad_algorithm", "ordering algorithm mismatch", path))
        if string_values(ordering.get("source_kind_order", [])) != EXPECTED_SOURCE_ORDER:
            findings.append(finding("error", "resolver_ordering_bad_source_order", "source_kind_order mismatch", path))
        if string_values(ordering.get("tie_breakers", [])) != EXPECTED_TIE_BREAKERS:
            findings.append(finding("error", "resolver_ordering_bad_tie_breakers", "tie_breakers mismatch", path))

    inputs = [item for item in as_list(data.get("inputs")) if isinstance(item, dict)]
    if len(inputs) != len(as_list(data.get("inputs"))):
        findings.append(finding("error", "resolver_input_shape", "all inputs must be objects", path))
    input_by_id: Dict[str, Dict[str, Any]] = {}
    descriptor_seen: Set[str] = set()
    provided_by_ref: Dict[str, List[str]] = {}
    required_by_ref: Dict[str, List[str]] = {}
    for index, item in enumerate(inputs):
        item_path = f"{path}#inputs[{index}]"
        kind = str(item.get("descriptor_kind") or "")
        descriptor_id = str(item.get("descriptor_id") or "")
        if kind not in ranks:
            findings.append(finding("error", "resolver_input_unknown_kind", f"unknown descriptor_kind: {kind}", item_path))
        if not is_token(descriptor_id):
            findings.append(finding("error", "resolver_input_bad_descriptor_id", f"bad descriptor_id: {descriptor_id}", item_path))
        if descriptor_id in descriptor_seen:
            findings.append(finding("error", "resolver_duplicate_descriptor", f"duplicate descriptor_id: {descriptor_id}", item_path))
        descriptor_seen.add(descriptor_id)
        input_by_id[descriptor_id] = item
        if item.get("source_ref_is_authority") is not False:
            findings.append(finding("error", "resolver_source_ref_authority", "source_ref_is_authority must be false", item_path))
        if item.get("stability") == "stable" and not as_list(item.get("proof")):
            findings.append(finding("error", "resolver_input_stable_without_proof", "stable input requires proof", item_path))
        for ref in as_list(item.get("provides")):
            findings.extend(validate_ref(ref, item_path))
            if isinstance(ref, dict):
                provided_by_ref.setdefault(normalized_ref(ref), []).append(descriptor_id)
        for ref in as_list(item.get("requires")):
            findings.extend(validate_ref(ref, item_path))
            if isinstance(ref, dict):
                required_by_ref.setdefault(normalized_ref(ref), []).append(descriptor_id)

    external_refs: Set[str] = set()
    for index, ref in enumerate(as_list(data.get("external_refs"))):
        findings.extend(validate_ref(ref, f"{path}#external_refs[{index}]"))
        if isinstance(ref, dict):
            external_refs.add(normalized_ref(ref))

    conflicts = [item for item in as_list(data.get("conflicts")) if isinstance(item, dict)]
    if len(conflicts) != len(as_list(data.get("conflicts"))):
        findings.append(finding("error", "resolver_conflict_shape", "all conflicts must be objects", path))
    conflicts_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
    conflict_order_keys: List[Tuple[str, str]] = []
    for index, conflict in enumerate(conflicts):
        item_path = f"{path}#conflicts[{index}]"
        conflict_type = str(conflict.get("conflict_type") or "")
        subject = str(conflict.get("subject") or "")
        decision = str(conflict.get("decision") or "")
        participants = string_values(conflict.get("participants", []))
        if not conflict_type:
            findings.append(finding("error", "resolver_conflict_missing_type", "conflict_type is required", item_path))
        if not is_token(subject):
            findings.append(finding("error", "resolver_conflict_bad_subject", f"bad conflict subject: {subject}", item_path))
        if decision not in ALLOWED_DECISIONS:
            findings.append(finding("error", "resolver_conflict_bad_decision", f"unsupported conflict decision: {decision}", item_path))
        if decision in FORBIDDEN_DECISIONS:
            findings.append(finding("error", "resolver_conflict_forbidden_decision", f"forbidden conflict decision: {decision}", item_path))
        if participants != sorted(participants, key=str.casefold):
            findings.append(finding("error", "resolver_conflict_participants_unsorted", "conflict participants must be sorted case-folded ascending", item_path))
        if decision == "selected_by_policy" and str(conflict.get("selected_descriptor") or "") not in participants:
            findings.append(finding("error", "resolver_conflict_missing_selected", "selected_by_policy requires selected_descriptor in participants", item_path))
        if not as_list(conflict.get("evidence")):
            findings.append(finding("error", "resolver_conflict_missing_evidence", "conflict requires evidence", item_path))
        key = (conflict_type, subject)
        if key in conflicts_by_key:
            findings.append(finding("error", "resolver_conflict_duplicate", f"duplicate conflict record: {conflict_type} {subject}", item_path))
        conflicts_by_key[key] = conflict
        conflict_order_keys.append((subject.casefold(), conflict_type.casefold()))
    if conflict_order_keys != sorted(conflict_order_keys):
        findings.append(finding("error", "resolver_conflicts_not_canonical_order", "conflicts must be sorted by subject then conflict_type", path))

    for ref, participants in provided_by_ref.items():
        unique = sorted(set(participants), key=str.casefold)
        if len(unique) <= 1:
            continue
        conflict = conflicts_by_key.get(("duplicate_provide", ref))
        if not conflict:
            findings.append(finding("error", "resolver_unresolved_duplicate_provide", f"duplicate provided ref lacks conflict: {ref}", path))
            continue
        if string_values(conflict.get("participants", [])) != unique:
            findings.append(finding("error", "resolver_duplicate_provide_participants", f"duplicate provide participants mismatch for {ref}", path))
        if conflict.get("decision") == "selected_by_policy" and not conflict.get("selected_descriptor"):
            findings.append(finding("error", "resolver_duplicate_provide_missing_selection", f"duplicate provide requires selected_descriptor: {ref}", path))

    available_refs = set(provided_by_ref) | external_refs
    for ref, participants in required_by_ref.items():
        if ref in available_refs:
            continue
        unique = sorted(set(participants), key=str.casefold)
        conflict = conflicts_by_key.get(("missing_dependency", ref))
        if not conflict:
            findings.append(finding("error", "resolver_missing_dependency", f"missing dependency lacks conflict: {ref}", path))
            continue
        if string_values(conflict.get("participants", [])) != unique:
            findings.append(finding("error", "resolver_missing_dependency_participants", f"missing dependency participants mismatch for {ref}", path))
        if conflict.get("decision") == "selected_by_policy":
            findings.append(finding("error", "resolver_missing_dependency_selected", f"missing dependency cannot be selected_by_policy: {ref}", path))

    steps = [item for item in as_list(data.get("steps")) if isinstance(item, dict)]
    if len(steps) != len(as_list(data.get("steps"))):
        findings.append(finding("error", "resolver_step_shape", "all steps must be objects", path))
    step_ids: Set[str] = set()
    step_keys: List[Tuple[int, str, str, str]] = []
    for index, step in enumerate(steps):
        item_path = f"{path}#steps[{index}]"
        order_index = step.get("order_index")
        step_id = str(step.get("step_id") or "")
        kind = str(step.get("descriptor_kind") or "")
        descriptor_id = str(step.get("descriptor_id") or "")
        source_ref = str(step.get("source_ref") or "")
        action = str(step.get("action") or "")
        if order_index != index:
            findings.append(finding("error", "resolver_step_bad_order_index", f"order_index must equal array index {index}", item_path))
        if not is_token(step_id):
            findings.append(finding("error", "resolver_step_bad_id", f"bad step_id: {step_id}", item_path))
        if step_id in step_ids:
            findings.append(finding("error", "resolver_step_duplicate_id", f"duplicate step_id: {step_id}", item_path))
        step_ids.add(step_id)
        if kind not in ranks:
            findings.append(finding("error", "resolver_step_unknown_kind", f"unknown descriptor_kind: {kind}", item_path))
        if descriptor_id not in input_by_id:
            findings.append(finding("error", "resolver_step_unknown_descriptor", f"step references unknown descriptor_id: {descriptor_id}", item_path))
        if action not in ALLOWED_ACTIONS:
            findings.append(finding("error", "resolver_step_bad_action", f"unsupported step action: {action}", item_path))
        if source_ref and descriptor_id in input_by_id and source_ref != str(input_by_id[descriptor_id].get("source_ref") or ""):
            findings.append(finding("error", "resolver_step_source_ref_mismatch", "step source_ref must match input source_ref", item_path))
        step_keys.append((ranks.get(kind, 9999), descriptor_id.casefold(), step_id.casefold(), source_ref.casefold()))
    if step_keys != sorted(step_keys):
        findings.append(finding("error", "resolver_steps_not_canonical_order", "steps are not in canonical layered stable sort order", path))

    return findings


def validate_fixture_file(path: Path, repo_root: Path, ranks: Dict[str, int]) -> Tuple[bool, List[Dict[str, Any]]]:
    rel = path.relative_to(repo_root).as_posix()
    try:
        data = load_json(path)
    except Exception as exc:
        return False, [finding("error", "fixture_invalid_json", f"fixture does not parse as JSON: {exc}", rel)]
    if not isinstance(data, dict):
        return False, [finding("error", "fixture_root_not_object", "fixture root must be an object", rel)]
    item_findings = validate_plan(data, path=rel, ranks=ranks)
    return not has_error(item_findings), item_findings


def validate_fixtures(repo_root: Path, ranks: Dict[str, int]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    fixture_dir = repo_root / FIXTURE_DIR_REL
    if not fixture_dir.exists():
        return [finding("error", "missing_fixture_dir", f"missing fixture dir: {FIXTURE_DIR_REL.as_posix()}")], {"status": "fail", "fixture_count": 0}
    findings: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []
    for path in sorted(fixture_dir.glob("*.json")):
        expected_invalid = path.name.startswith("invalid_")
        passed, item_findings = validate_fixture_file(path, repo_root, ranks)
        expectation_met = (not passed) if expected_invalid else passed
        if not expectation_met:
            findings.append(finding("error", "fixture_expectation_failed", f"fixture expectation failed: {path.relative_to(repo_root).as_posix()}"))
        results.append({
            "path": path.relative_to(repo_root).as_posix(),
            "expected": "invalid" if expected_invalid else "valid",
            "status": "pass" if expectation_met else "fail",
            "errors": sum(1 for item in item_findings if item["level"] == "error"),
            "findings": item_findings,
        })
    return findings, {
        "status": "pass" if not findings else "fail",
        "fixture_count": len(results),
        "fixtures": results,
    }


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
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def build_inventory(repo_root: Path) -> Dict[str, Any]:
    categories: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}

    def add(category: str, path: str) -> None:
        categories[category] = categories.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 8:
            examples[category].append(path)

    files = git_ls_files(repo_root)
    for path in files:
        lowered = path.lower()
        if lowered.startswith("contracts/composition/"):
            add("composition_resolver_contract", path)
        elif lowered.startswith("contracts/app/"):
            add("app_descriptor_surface", path)
        elif lowered.startswith("contracts/module/"):
            add("module_descriptor_surface", path)
        elif lowered.startswith("contracts/workbench/"):
            add("workbench_descriptor_surface", path)
        elif lowered.startswith(("contracts/package/", "contracts/schema/package/", "contracts/schema/pack_")):
            add("package_descriptor_surface", path)
    return {
        "status": "warning",
        "files_scanned": len(files),
        "categories": categories,
        "examples": examples,
        "note": "Inventory is descriptive only; COMPOSITION-RESOLVER-LAW-01 does not implement runtime loading or migrate descriptor schemas.",
    }


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> Dict[str, Any]:
    findings, ranks = validate_contracts(repo_root)
    fixtures = {"status": "not_run", "fixture_count": 0, "fixtures": []}
    if include_fixtures:
        fixture_findings, fixtures = validate_fixtures(repo_root, ranks)
        findings.extend(fixture_findings)
    inventory = build_inventory(repo_root) if include_inventory else {"status": "not_run"}
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_composition_resolver",
        "status": "pass" if not errors else "fail",
        "source_kinds": sorted(ranks, key=lambda kind: ranks[kind]),
        "findings": findings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "fixtures": fixtures,
        "inventory": inventory,
    }


def print_text(result: Dict[str, Any]) -> None:
    print(f"composition resolver: {result['status']}")
    print(f"source_kinds: {len(result.get('source_kinds', []))}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
    fixtures = result.get("fixtures", {})
    if fixtures.get("status") != "not_run":
        print(f"fixtures: {fixtures.get('status')} count={fixtures.get('fixture_count', 0)}")
    inventory = result.get("inventory", {})
    if inventory.get("status") != "not_run":
        print(f"inventory: {inventory.get('status')} files_scanned={inventory.get('files_scanned', 0)}")
    for item in result.get("findings", []):
        path = f"{item.get('path')}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on validation errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fixtures", action="store_true", help="Validate composition resolver fixtures")
    parser.add_argument("--inventory", action="store_true", help="Inventory descriptor surfaces")
    args = parser.parse_args(argv)

    result = validate_all(Path(args.repo_root).resolve(), include_fixtures=args.fixtures, include_inventory=args.inventory)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if args.strict and result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
