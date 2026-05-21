#!/usr/bin/env python3
"""Validate command/result/view/action/projection slice contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


VIEW_REL = Path("contracts/view/validation_summary.view.json")
ACTION_REGISTRY_REL = Path("contracts/action/validation_actions.registry.json")
ACTION_SCHEMA_REL = Path("contracts/action/action.schema.json")
ACTION_CONTRACT_REL = Path("contracts/action/action_surface.contract.toml")
PROJECTION_KIND_REL = Path("contracts/presentation/projection_kind.registry.json")
PROJECTION_SCHEMA_REL = Path("contracts/presentation/projection.schema.json")
PROJECTION_SET_REL = Path("contracts/presentation/validation_summary.projections.json")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
PRESENTATION_FIXTURE_DIR_REL = Path("tests/contract/presentation/fixtures")
VIEW_FIXTURE_DIR_REL = Path("tests/contract/view/fixtures")

ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+(\.v[0-9]+)?$")
VERSIONED_ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+\.v[0-9]+$")
PATHLIKE_RE = re.compile(r"[/\\]|\.\.(?:/|\\)|\.(json|toml|py)$")
FORBIDDEN_WORKBENCH_PRIVATE_STRINGS = ("tools/validators/", "tools\\validators\\")
REQUIRED_PROJECTION_KINDS = {"cli", "text", "rendered", "native", "headless"}


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out: list[str] = []
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


def _split_array_items(raw: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
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


def _minimal_toml_load(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current = root
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


def load_toml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def finding(level: str, code: str, message: str, path: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def rel_exists(repo_root: Path, raw_path: str | None) -> bool:
    if not raw_path:
        return False
    path = Path(raw_path)
    if path.is_absolute():
        return path.exists()
    return (repo_root / path).exists()


def assert_dotted_id(value: str, path: str, kind: str, *, versioned: bool = False) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    regex = VERSIONED_ID_RE if versioned else ID_RE
    if not value:
        findings.append(finding("error", f"{kind}_missing_id", f"{kind} ID is required", path))
    elif PATHLIKE_RE.search(value) or not regex.match(value):
        findings.append(finding("error", f"{kind}_bad_id", f"{kind} ID is not a governed dotted ID: {value}", path))
    return findings


def read_command_ids(repo_root: Path) -> set[str]:
    data = load_toml(repo_root / COMMAND_CONTRACT_REL)
    return {
        str(item.get("id"))
        for item in as_list(data.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


def read_diagnostic_codes(repo_root: Path) -> set[str]:
    data = load_json(repo_root / DIAGNOSTIC_REGISTRY_REL)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def read_capability_ids(repo_root: Path) -> set[str]:
    data = load_json(repo_root / CAPABILITY_REGISTRY_REL)
    return {
        str(item.get("capability_id"))
        for item in as_list(data.get("capabilities"))
        if isinstance(item, dict) and item.get("capability_id")
    }


def projection_kind_ids(kind_registry: dict[str, Any]) -> set[str]:
    return {
        str(item.get("id"))
        for item in as_list(kind_registry.get("kinds"))
        if isinstance(item, dict) and item.get("id")
    }


def action_ids(action_registry: dict[str, Any]) -> set[str]:
    return {
        str(item.get("action_id"))
        for item in as_list(action_registry.get("actions"))
        if isinstance(item, dict) and item.get("action_id")
    }


def walk_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, list):
        for item in value:
            strings.extend(walk_strings(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            strings.append(str(key))
            strings.extend(walk_strings(item))
    return strings


def validate_view(
    repo_root: Path,
    view: dict[str, Any],
    command_ids: set[str],
    diagnostic_codes: set[str],
    capability_ids: set[str],
    action_id_set: set[str],
    path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    view_id = str(view.get("view_id") or "")
    findings.extend(assert_dotted_id(view_id, path, "view", versioned=True))
    if view.get("presentation_only") is not True or view.get("authority") is not False:
        findings.append(finding("error", "view_authority_violation", "view must be presentation-only and non-authoritative", path))
    result_schema = str(view.get("accepts_result_schema") or "")
    if not rel_exists(repo_root, result_schema):
        findings.append(finding("error", "view_missing_result_schema", f"accepts_result_schema does not exist: {result_schema}", path))
    command_id = str(view.get("command_id") or "")
    if command_id not in command_ids:
        findings.append(finding("error", "view_unknown_command", f"unknown command_id: {command_id}", path))
    for action_id in [str(value) for value in as_list(view.get("actions")) if value]:
        if action_id not in action_id_set:
            findings.append(finding("error", "view_unknown_action", f"view references unknown action: {action_id}", path))
    for binding in as_list(view.get("diagnostic_bindings")):
        if not isinstance(binding, dict):
            findings.append(finding("error", "view_bad_diagnostic_binding", "diagnostic binding must be an object", path))
            continue
        code = str(binding.get("diagnostic_code") or "")
        if code not in diagnostic_codes:
            findings.append(finding("error", "view_unknown_diagnostic", f"unknown diagnostic code: {code}", path))
    for binding in as_list(view.get("evidence_bindings")):
        if not isinstance(binding, dict):
            findings.append(finding("error", "view_bad_evidence_binding", "evidence binding must be an object", path))
            continue
        evidence_schema = str(binding.get("evidence_schema") or "")
        if not rel_exists(repo_root, evidence_schema):
            findings.append(finding("error", "view_missing_evidence_schema", f"evidence schema does not exist: {evidence_schema}", path))
    for capability_id in [str(value) for value in as_list(view.get("capability_requirements")) if value]:
        if capability_id not in capability_ids:
            findings.append(finding("error", "view_unknown_capability", f"unknown capability: {capability_id}", path))
    if view.get("accepts_document_schema") is not None:
        findings.append(finding("error", "view_unexpected_document_schema", "command-result slice must not claim a document schema", path))
    if view.get("accepts_snapshot_schema") is not None:
        findings.append(finding("error", "view_unexpected_snapshot_schema", "command-result slice must not claim a snapshot schema", path))
    return findings


def validate_action_registry(
    repo_root: Path,
    registry: dict[str, Any],
    command_ids: set[str],
    capability_ids: set[str],
    view_ids: set[str],
    path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, action in enumerate(as_list(registry.get("actions"))):
        if not isinstance(action, dict):
            findings.append(finding("error", "action_shape", f"action {index} must be an object", path))
            continue
        action_id = str(action.get("action_id") or "")
        findings.extend(assert_dotted_id(action_id, path, "action", versioned=True))
        if action_id in seen:
            findings.append(finding("error", "action_duplicate_id", f"duplicate action_id: {action_id}", path))
        seen.add(action_id)
        for view_id in [str(value) for value in as_list(action.get("view_ids")) if value]:
            if view_id not in view_ids:
                findings.append(finding("error", "action_unknown_view", f"action references unknown view: {view_id}", path))
        command_ref = action.get("command_ref")
        if command_ref is not None and str(command_ref) not in command_ids:
            findings.append(finding("error", "action_unknown_command_ref", f"unknown command_ref: {command_ref}", path))
        input_schema = action.get("input_schema")
        if input_schema is not None and not rel_exists(repo_root, str(input_schema)):
            findings.append(finding("error", "action_missing_input_schema", f"input schema does not exist: {input_schema}", path))
        for capability_id in [str(value) for value in as_list(action.get("required_capabilities")) if value]:
            if capability_id not in capability_ids:
                findings.append(finding("error", "action_unknown_capability", f"unknown capability: {capability_id}", path))
        for key in ("enabled_when", "disabled_reason", "danger_level", "transaction_policy", "refusal_behavior", "evidence_behavior"):
            if not action.get(key):
                findings.append(finding("error", "action_missing_field", f"{action_id} missing {key}", path))
        if action.get("confirmation_required") not in {True, False}:
            findings.append(finding("error", "action_confirmation_not_bool", f"{action_id} confirmation_required must be boolean", path))
    if not seen:
        findings.append(finding("error", "action_registry_empty", "action registry must contain at least one action", path))
    return findings


def validate_projection(
    repo_root: Path,
    projection: dict[str, Any],
    *,
    path: str,
    view_ids: set[str],
    action_id_set: set[str],
    command_ids: set[str],
    projection_kinds: set[str],
    diagnostic_codes: set[str],
    view_result_schema: str | None = None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    projection_id = str(projection.get("projection_id") or "")
    findings.extend(assert_dotted_id(projection_id, path, "projection", versioned=True))
    kind = str(projection.get("projection_kind") or "")
    if kind not in projection_kinds:
        findings.append(finding("error", "projection_unknown_kind", f"unknown projection_kind: {kind}", path))
    view_id = str(projection.get("view_id") or "")
    if view_id not in view_ids:
        findings.append(finding("error", "projection_unknown_view", f"unknown view_id: {view_id}", path))
    result_schema = str(projection.get("source_result_schema") or "")
    if not rel_exists(repo_root, result_schema):
        findings.append(finding("error", "projection_missing_result_schema", f"source_result_schema does not exist: {result_schema}", path))
    if view_result_schema and result_schema != view_result_schema:
        findings.append(finding("error", "projection_result_schema_mismatch", f"projection result schema {result_schema} does not match view {view_result_schema}", path))
    command_id = str(projection.get("command_id") or "")
    if command_id not in command_ids:
        findings.append(finding("error", "projection_unknown_command", f"unknown command_id: {command_id}", path))
    for action_id in [str(value) for value in as_list(projection.get("action_ids")) if value]:
        if action_id not in action_id_set:
            findings.append(finding("error", "projection_unknown_action", f"unknown action_id: {action_id}", path))
    for diagnostic_code in [str(value) for value in as_list(projection.get("diagnostic_bindings")) if value]:
        if diagnostic_code not in diagnostic_codes:
            findings.append(finding("error", "projection_unknown_diagnostic", f"unknown diagnostic binding: {diagnostic_code}", path))
    for evidence_schema in [str(value) for value in as_list(projection.get("evidence_bindings")) if value]:
        if not rel_exists(repo_root, evidence_schema):
            findings.append(finding("error", "projection_missing_evidence_schema", f"evidence binding does not exist: {evidence_schema}", path))
    if projection.get("private_tool_calls") is not False:
        findings.append(finding("error", "projection_private_tool_call", "projection must declare private_tool_calls=false", path))
    if kind in {"rendered", "native"} and projection.get("runtime_implemented") is True:
        findings.append(finding("error", "projection_forbidden_runtime_claim", f"{kind} runtime is not implemented by this task", path))
    if kind == "text" and projection.get("runtime_implemented") is True:
        findings.append(finding("error", "projection_forbidden_text_runtime_claim", "text/TUI runtime is not implemented by this task", path))
    if str(projection.get("shell_host") or "") == "workbench":
        for text in walk_strings(projection):
            normalized = text.replace("\\", "/")
            if any(forbidden.replace("\\", "/") in normalized for forbidden in FORBIDDEN_WORKBENCH_PRIVATE_STRINGS):
                findings.append(finding("error", "workbench_private_validator_path", "Workbench projection must not reference private validator implementation paths", path))
                break
    return findings


def validate_projection_set(
    repo_root: Path,
    projection_set: dict[str, Any],
    *,
    view_ids: set[str],
    action_id_set: set[str],
    command_ids: set[str],
    projection_kinds: set[str],
    diagnostic_codes: set[str],
    view_result_schema: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    path = str(PROJECTION_SET_REL)
    view_id = str(projection_set.get("view_id") or "")
    if view_id not in view_ids:
        findings.append(finding("error", "projection_set_unknown_view", f"unknown view_id: {view_id}", path))
    if str(projection_set.get("source_result_schema") or "") != view_result_schema:
        findings.append(finding("error", "projection_set_result_schema_mismatch", "projection set result schema must match semantic view", path))
    kinds_seen: set[str] = set()
    for fixture_path in [str(value) for value in as_list(projection_set.get("projection_fixtures")) if value]:
        if not rel_exists(repo_root, fixture_path):
            findings.append(finding("error", "projection_fixture_missing", f"projection fixture does not exist: {fixture_path}", path))
            continue
        projection = load_json(repo_root / fixture_path)
        kinds_seen.add(str(projection.get("projection_kind") or ""))
        findings.extend(
            validate_projection(
                repo_root,
                projection,
                path=fixture_path,
                view_ids=view_ids,
                action_id_set=action_id_set,
                command_ids=command_ids,
                projection_kinds=projection_kinds,
                diagnostic_codes=diagnostic_codes,
                view_result_schema=view_result_schema,
            )
        )
    for required_kind in [str(value) for value in as_list(projection_set.get("required_projection_kinds")) if value]:
        if required_kind not in kinds_seen:
            findings.append(finding("error", "projection_set_missing_required_kind", f"missing required projection kind fixture: {required_kind}", path))
    return findings


def validate_contracts(repo_root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for rel in [
        VIEW_REL,
        ACTION_REGISTRY_REL,
        ACTION_SCHEMA_REL,
        ACTION_CONTRACT_REL,
        PROJECTION_KIND_REL,
        PROJECTION_SCHEMA_REL,
        PROJECTION_SET_REL,
        COMMAND_CONTRACT_REL,
        DIAGNOSTIC_REGISTRY_REL,
        CAPABILITY_REGISTRY_REL,
    ]:
        if not (repo_root / rel).exists():
            findings.append(finding("error", "missing_required_surface", f"missing {rel}", str(rel)))
    if findings:
        return {"findings": findings, "views": 0, "actions": 0, "projection_kinds": 0, "projections": 0}

    command_ids = read_command_ids(repo_root)
    diagnostic_codes = read_diagnostic_codes(repo_root)
    capability_ids = read_capability_ids(repo_root)
    view = load_json(repo_root / VIEW_REL)
    action_registry = load_json(repo_root / ACTION_REGISTRY_REL)
    projection_kind_registry = load_json(repo_root / PROJECTION_KIND_REL)
    projection_set = load_json(repo_root / PROJECTION_SET_REL)

    action_id_set = action_ids(action_registry)
    view_ids = {str(view.get("view_id") or "")}
    projection_kinds = projection_kind_ids(projection_kind_registry)
    view_result_schema = str(view.get("accepts_result_schema") or "")

    if projection_kinds != REQUIRED_PROJECTION_KINDS:
        findings.append(
            finding(
                "error",
                "projection_kind_registry_mismatch",
                f"projection kind registry must contain exactly {sorted(REQUIRED_PROJECTION_KINDS)}",
                str(PROJECTION_KIND_REL),
            )
        )

    try:
        load_toml(repo_root / ACTION_CONTRACT_REL)
    except Exception as exc:
        findings.append(finding("error", "invalid_action_contract_toml", f"{ACTION_CONTRACT_REL}: {exc}", str(ACTION_CONTRACT_REL)))

    findings.extend(validate_action_registry(repo_root, action_registry, command_ids, capability_ids, view_ids, str(ACTION_REGISTRY_REL)))
    findings.extend(validate_view(repo_root, view, command_ids, diagnostic_codes, capability_ids, action_id_set, str(VIEW_REL)))
    findings.extend(
        validate_projection_set(
            repo_root,
            projection_set,
            view_ids=view_ids,
            action_id_set=action_id_set,
            command_ids=command_ids,
            projection_kinds=projection_kinds,
            diagnostic_codes=diagnostic_codes,
            view_result_schema=view_result_schema,
        )
    )
    return {
        "findings": findings,
        "views": 1,
        "actions": len(action_id_set),
        "projection_kinds": len(projection_kinds),
        "projections": len(as_list(projection_set.get("projection_fixtures"))),
    }


def validate_fixture_file(repo_root: Path, path: Path, context: dict[str, Any]) -> list[dict[str, Any]]:
    rel = path.relative_to(repo_root).as_posix()
    data = load_json(path)
    if data.get("fixture_kind") == "action_registry":
        registry = {"actions": as_list(data.get("actions"))}
        return validate_action_registry(
            repo_root,
            registry,
            context["command_ids"],
            context["capability_ids"],
            context["view_ids"],
            rel,
        )
    return validate_projection(
        repo_root,
        data,
        path=rel,
        view_ids=context["view_ids"],
        action_id_set=context["action_ids"],
        command_ids=context["command_ids"],
        projection_kinds=context["projection_kinds"],
        diagnostic_codes=context["diagnostic_codes"],
        view_result_schema=context["view_result_schema"],
    )


def validate_fixtures(repo_root: Path) -> dict[str, Any]:
    contract_result = validate_contracts(repo_root)
    findings = list(contract_result["findings"])
    if findings:
        return {"findings": findings, "valid_fixtures": 0, "invalid_fixtures": 0}

    command_ids = read_command_ids(repo_root)
    diagnostic_codes = read_diagnostic_codes(repo_root)
    capability_ids = read_capability_ids(repo_root)
    view = load_json(repo_root / VIEW_REL)
    action_registry = load_json(repo_root / ACTION_REGISTRY_REL)
    projection_kinds = projection_kind_ids(load_json(repo_root / PROJECTION_KIND_REL))
    context = {
        "command_ids": command_ids,
        "diagnostic_codes": diagnostic_codes,
        "capability_ids": capability_ids,
        "view_ids": {str(view.get("view_id"))},
        "action_ids": action_ids(action_registry),
        "projection_kinds": projection_kinds,
        "view_result_schema": str(view.get("accepts_result_schema") or ""),
    }

    valid_count = 0
    invalid_count = 0
    for path in sorted((repo_root / PRESENTATION_FIXTURE_DIR_REL).glob("*.json")):
        rel = path.relative_to(repo_root).as_posix()
        is_invalid = path.name.startswith("invalid_")
        item_findings = validate_fixture_file(repo_root, path, context)
        if is_invalid:
            invalid_count += 1
            if not any(item["level"] == "error" for item in item_findings):
                findings.append(finding("error", "invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
        else:
            valid_count += 1
            findings.extend(item_findings)

    for path in sorted((repo_root / VIEW_FIXTURE_DIR_REL).glob("*.json")):
        rel = path.relative_to(repo_root).as_posix()
        data = load_json(path)
        if data.get("expected_result") == "pass" and not rel_exists(repo_root, str(data.get("view_ref") or "")):
            findings.append(finding("error", "view_fixture_missing_ref", f"view fixture references missing view: {rel}", rel))
        valid_count += 1

    return {"findings": findings, "valid_fixtures": valid_count, "invalid_fixtures": invalid_count}


def inventory(repo_root: Path) -> dict[str, Any]:
    contract_result = validate_contracts(repo_root)
    return {
        "view": load_json(repo_root / VIEW_REL).get("view_id") if (repo_root / VIEW_REL).exists() else None,
        "actions": sorted(action_ids(load_json(repo_root / ACTION_REGISTRY_REL))) if (repo_root / ACTION_REGISTRY_REL).exists() else [],
        "projection_kinds": sorted(projection_kind_ids(load_json(repo_root / PROJECTION_KIND_REL))) if (repo_root / PROJECTION_KIND_REL).exists() else [],
        "projection_fixtures": as_list(load_json(repo_root / PROJECTION_SET_REL).get("projection_fixtures")) if (repo_root / PROJECTION_SET_REL).exists() else [],
        "findings": contract_result["findings"],
    }


def render_text(label: str, result: dict[str, Any]) -> str:
    errors = [item for item in result.get("findings", []) if item.get("level") == "error"]
    warnings = [item for item in result.get("findings", []) if item.get("level") == "warning"]
    status = "PASS" if not errors else "FAIL"
    extras = []
    for key in ("views", "actions", "projection_kinds", "projections", "valid_fixtures", "invalid_fixtures"):
        if key in result:
            extras.append(f"{key}={result[key]}")
    suffix = " " + " ".join(extras) if extras else ""
    lines = [f"command-result-view {label}: {status}{suffix} errors={len(errors)} warnings={len(warnings)}"]
    for item in errors + warnings:
        location = f" [{item.get('path')}]" if item.get("path") else ""
        lines.append(f"{item['level']}: {item['code']}{location}: {item['message']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if args.inventory:
        result = inventory(repo_root)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("command-result-view inventory:")
            print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if any(item.get("level") == "error" for item in result.get("findings", [])) else 0

    if args.fixtures:
        result = validate_fixtures(repo_root)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_text("fixtures", result))
        return 1 if any(item.get("level") == "error" for item in result.get("findings", [])) else 0

    result = validate_contracts(repo_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text("validation", result))
    return 1 if any(item.get("level") == "error" for item in result.get("findings", [])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
