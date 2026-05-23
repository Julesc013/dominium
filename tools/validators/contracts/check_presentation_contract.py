#!/usr/bin/env python3
"""Validate Dominium presentation surface and read-only view-model contracts."""

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


CONTRACT_REL = Path("contracts/presentation/presentation_surface.contract.toml")
VIEW_MODEL_SCHEMA_REL = Path("contracts/presentation/presentation_view_model.schema.json")
READ_ONLY_VIEW_MODEL_REL = Path("contracts/presentation/read_only_inspection.view_model.json")
PROJECTION_KIND_REL = Path("contracts/presentation/projection_kind.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
EVIDENCE_PACKET_REL = Path("contracts/evidence/evidence_packet.schema.json")
FIXTURE_DIR_REL = Path("tests/contract/presentation/view_model_fixtures")

ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+\.v[0-9]+$")
POINTER_RE = re.compile(r"^(/|\$)")
REQUIRED_POLICY = {
    "presentations_are_authority": False,
    "presentations_mutate_truth": False,
    "presentations_create_truth": False,
    "presentations_hide_refusals": False,
    "presentations_hide_degradation": False,
    "presentation_runtime_implemented_here": False,
    "workbench_shell_is_authority": False,
    "renderer_is_authority": False,
    "private_tool_calls_allowed": False,
    "generated_output_is_source_truth": False,
    "view_model_identity_is_path": False,
    "projection_identity_is_runtime_path": False,
    "actions_require_command_boundary_when_behavior_exists": True,
    "direct_private_tool_calls_forbidden": True,
    "read_only_inspection_mutates_truth": False,
    "read_only_inspection_requires_evidence_binding": True,
    "read_only_inspection_requires_refusal_binding": True,
    "read_only_inspection_requires_diagnostic_binding": True,
    "read_only_inspection_requires_degradation_state": True,
    "no_modal_loading_claim_requires_explicit_degradation": True,
    "no_modal_loading_claim_requires_pending_state": True,
    "late_data_must_degrade_instead_of_blocking": True,
    "renderer_mutation_forbidden": True,
    "truth_perceived_render_separation_required": True,
}
REQUIRED_READ_ONLY_SECTIONS = {
    "summary",
    "status",
    "diagnostics",
    "refusals",
    "evidence",
    "provenance",
    "degradation",
    "projection_state",
}
REQUIRED_READ_ONLY_PROJECTIONS = {"headless", "cli", "text"}
BLOCKED_RUNTIME_NON_GOALS = {
    "renderer_implementation",
    "native_gui",
    "gameplay",
    "provider_runtime",
    "package_runtime",
    "runtime_module_loader",
}
ALLOWED_STABILITY = {"provisional", "internal", "experimental", "fixture", "historical", "retired"}
ALLOWED_TRANSACTION_POLICIES = {"read_only_projection", "command_invocation_only", "read_only_export_descriptor"}


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


def projection_kinds(repo_root: Path) -> set[str]:
    data = load_json(repo_root / PROJECTION_KIND_REL)
    return {
        str(item.get("id"))
        for item in as_list(data.get("kinds"))
        if isinstance(item, dict) and item.get("id")
    }


def diagnostic_codes(repo_root: Path) -> set[str]:
    data = load_json(repo_root / DIAGNOSTIC_REGISTRY_REL)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def refusal_codes(repo_root: Path) -> set[str]:
    data = load_json(repo_root / REFUSAL_REGISTRY_REL)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def command_ids(repo_root: Path) -> set[str]:
    data = load_toml(repo_root / COMMAND_CONTRACT_REL)
    return {
        str(item.get("id"))
        for item in as_list(data.get("command"))
        if isinstance(item, dict) and item.get("id")
    }


def validate_contract(repo_root: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if data.get("schema_version") != "dominium.presentation.surface.v1":
        findings.append(finding("error", "contract_bad_schema_version", "presentation contract schema_version is invalid", str(CONTRACT_REL)))
    policy = data.get("policy")
    if not isinstance(policy, dict):
        findings.append(finding("error", "contract_missing_policy", "presentation contract must have a [policy] table", str(CONTRACT_REL)))
        return findings
    for key, expected in REQUIRED_POLICY.items():
        if policy.get(key) is not expected:
            findings.append(
                finding(
                    "error",
                    "contract_policy_violation",
                    f"policy.{key} must be {str(expected).lower()}",
                    str(CONTRACT_REL),
                )
            )
    read_only = data.get("read_only_inspection")
    if not isinstance(read_only, dict):
        findings.append(finding("error", "contract_missing_read_only_inspection", "contract must define [read_only_inspection]", str(CONTRACT_REL)))
    else:
        if read_only.get("view_model") != READ_ONLY_VIEW_MODEL_REL.as_posix():
            findings.append(finding("error", "contract_bad_view_model_ref", "read_only_inspection.view_model must reference the canonical descriptor", str(CONTRACT_REL)))
        if read_only.get("modal_loading_allowed") is not False:
            findings.append(finding("error", "contract_modal_loading_allowed", "read-only inspection cannot allow modal loading", str(CONTRACT_REL)))
        if read_only.get("runtime_implemented") is not False:
            findings.append(finding("error", "contract_runtime_claim", "PRESENTATION-CONTRACT-01 cannot claim runtime implementation", str(CONTRACT_REL)))
        required = {str(value) for value in as_list(read_only.get("required_projection_kinds"))}
        missing = sorted(REQUIRED_READ_ONLY_PROJECTIONS - required)
        if missing:
            findings.append(finding("error", "contract_missing_projection_kind", f"read-only inspection missing projection kinds: {', '.join(missing)}", str(CONTRACT_REL)))
    if not rel_exists(repo_root, EVIDENCE_PACKET_REL.as_posix()):
        findings.append(finding("error", "contract_missing_evidence_schema", f"missing {EVIDENCE_PACKET_REL}", str(CONTRACT_REL)))
    return findings


def validate_view_model(repo_root: Path, data: dict[str, Any], rel: str, *, fixture: bool = False) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if data.get("schema_version") != "dominium.presentation.view_model.v1":
        findings.append(finding("error", "view_model_bad_schema_version", "view model schema_version is invalid", rel))
    view_model_id = str(data.get("view_model_id") or "")
    if not ID_RE.match(view_model_id):
        findings.append(finding("error", "view_model_bad_id", f"invalid view_model_id: {view_model_id}", rel))
    if str(data.get("stability") or "") not in ALLOWED_STABILITY:
        findings.append(finding("error", "view_model_bad_stability", f"invalid stability: {data.get('stability')}", rel))
    for key, expected in {
        "presentation_only": True,
        "authority": False,
        "mutates_truth": False,
        "private_tool_calls": False,
    }.items():
        if data.get(key) is not expected:
            findings.append(finding("error", f"view_model_{key}_violation", f"{key} must be {str(expected).lower()}", rel))

    for source_ref in [str(value) for value in as_list(data.get("source_refs")) if value]:
        if not rel_exists(repo_root, source_ref):
            findings.append(finding("error", "view_model_missing_source_ref", f"source_ref does not exist: {source_ref}", rel))
    if not as_list(data.get("source_refs")):
        findings.append(finding("error", "view_model_missing_source_refs", "view model must declare source_refs", rel))

    sections = {str(value) for value in as_list(data.get("sections"))}
    missing_sections = sorted(REQUIRED_READ_ONLY_SECTIONS - sections)
    if missing_sections:
        findings.append(finding("error", "view_model_missing_section", f"missing sections: {', '.join(missing_sections)}", rel))

    for field in as_list(data.get("fields")):
        if not isinstance(field, dict):
            findings.append(finding("error", "view_model_field_shape", "fields must contain objects", rel))
            continue
        if not field.get("field_id"):
            findings.append(finding("error", "view_model_field_missing_id", "field is missing field_id", rel))
        pointer = str(field.get("source_pointer") or "")
        if not POINTER_RE.match(pointer):
            findings.append(finding("error", "view_model_bad_source_pointer", f"bad source_pointer: {pointer}", rel))
    if not as_list(data.get("fields")):
        findings.append(finding("error", "view_model_no_fields", "view model must define fields", rel))

    known_diagnostics = diagnostic_codes(repo_root)
    diagnostic_bindings = as_list(data.get("diagnostic_bindings"))
    if not diagnostic_bindings:
        findings.append(finding("error", "view_model_missing_diagnostics", "view model must bind diagnostics", rel))
    for binding in diagnostic_bindings:
        if not isinstance(binding, dict):
            findings.append(finding("error", "view_model_diagnostic_shape", "diagnostic binding must be an object", rel))
            continue
        code = str(binding.get("diagnostic_code") or "")
        if code not in known_diagnostics:
            findings.append(finding("error", "view_model_unknown_diagnostic", f"unknown diagnostic_code: {code}", rel))

    known_refusals = refusal_codes(repo_root)
    refusal_bindings = as_list(data.get("refusal_bindings"))
    if not refusal_bindings:
        findings.append(finding("error", "view_model_missing_refusals", "view model must bind refusals", rel))
    for binding in refusal_bindings:
        if not isinstance(binding, dict):
            findings.append(finding("error", "view_model_refusal_shape", "refusal binding must be an object", rel))
            continue
        code = str(binding.get("refusal_code") or "")
        if code not in known_refusals:
            findings.append(finding("error", "view_model_unknown_refusal", f"unknown refusal_code: {code}", rel))

    evidence_bindings = as_list(data.get("evidence_bindings"))
    if not evidence_bindings:
        findings.append(finding("error", "view_model_missing_evidence", "view model must bind evidence", rel))
    for binding in evidence_bindings:
        if not isinstance(binding, dict):
            findings.append(finding("error", "view_model_evidence_shape", "evidence binding must be an object", rel))
            continue
        evidence_schema = str(binding.get("evidence_schema") or "")
        if not rel_exists(repo_root, evidence_schema):
            findings.append(finding("error", "view_model_missing_evidence_schema", f"evidence schema does not exist: {evidence_schema}", rel))

    projection = data.get("projection_requirements")
    known_projection_kinds = projection_kinds(repo_root)
    if not isinstance(projection, dict):
        findings.append(finding("error", "view_model_missing_projection_requirements", "projection_requirements must be an object", rel))
    else:
        required_kinds = {str(value) for value in as_list(projection.get("required_projection_kinds"))}
        unknown = sorted(required_kinds - known_projection_kinds)
        if unknown:
            findings.append(finding("error", "view_model_unknown_projection_kind", f"unknown projection kinds: {', '.join(unknown)}", rel))
        missing_required = sorted(REQUIRED_READ_ONLY_PROJECTIONS - required_kinds)
        if missing_required:
            findings.append(finding("error", "view_model_missing_projection_kind", f"missing required projection kinds: {', '.join(missing_required)}", rel))
        fallback = str(projection.get("fallback_projection") or "")
        if fallback not in known_projection_kinds:
            findings.append(finding("error", "view_model_bad_fallback_projection", f"fallback projection is unknown: {fallback}", rel))
        for key, expected in {
            "modal_loading_allowed": False,
            "pending_state_required": True,
            "degradation_required": True,
            "renderer_mutation_allowed": False,
            "private_tool_calls_allowed": False,
        }.items():
            if projection.get(key) is not expected:
                findings.append(finding("error", f"view_model_projection_{key}_violation", f"projection_requirements.{key} must be {str(expected).lower()}", rel))

    known_commands = command_ids(repo_root)
    for action in as_list(data.get("action_bindings")):
        if not isinstance(action, dict):
            findings.append(finding("error", "view_model_action_shape", "action binding must be an object", rel))
            continue
        action_id = str(action.get("action_id") or "")
        if not ID_RE.match(action_id):
            findings.append(finding("error", "view_model_bad_action_id", f"invalid action_id: {action_id}", rel))
        command_ref = action.get("command_ref")
        if command_ref is not None and str(command_ref) not in known_commands:
            findings.append(finding("error", "view_model_unknown_command_ref", f"unknown command_ref: {command_ref}", rel))
        if action.get("transaction_policy") not in ALLOWED_TRANSACTION_POLICIES:
            findings.append(finding("error", "view_model_bad_transaction_policy", f"bad transaction_policy: {action.get('transaction_policy')}", rel))
        if action.get("mutates_truth") is not False:
            findings.append(finding("error", "view_model_action_mutates_truth", f"{action_id} must not mutate truth", rel))
        if action.get("private_tool_call") is not False:
            findings.append(finding("error", "view_model_action_private_tool", f"{action_id} must not call private tools", rel))
        if not action.get("refusal_behavior"):
            findings.append(finding("error", "view_model_action_missing_refusal", f"{action_id} missing refusal_behavior", rel))
        if not action.get("evidence_behavior"):
            findings.append(finding("error", "view_model_action_missing_evidence", f"{action_id} missing evidence_behavior", rel))

    if not fixture:
        non_goals = {str(value) for value in as_list(data.get("non_goals"))}
        missing_non_goals = sorted(BLOCKED_RUNTIME_NON_GOALS - non_goals)
        if missing_non_goals:
            findings.append(finding("error", "view_model_missing_non_goals", f"missing blocked non_goals: {', '.join(missing_non_goals)}", rel))
    return findings


def validate_contracts(repo_root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for rel in [
        CONTRACT_REL,
        VIEW_MODEL_SCHEMA_REL,
        READ_ONLY_VIEW_MODEL_REL,
        PROJECTION_KIND_REL,
        DIAGNOSTIC_REGISTRY_REL,
        REFUSAL_REGISTRY_REL,
        COMMAND_CONTRACT_REL,
        EVIDENCE_PACKET_REL,
    ]:
        if not (repo_root / rel).exists():
            findings.append(finding("error", "missing_required_surface", f"missing {rel}", str(rel)))
    if findings:
        return {"findings": findings, "view_models": 0}
    schema = load_json(repo_root / VIEW_MODEL_SCHEMA_REL)
    if schema.get("$id") != "dominium.presentation.view_model_schema.v1":
        findings.append(finding("error", "schema_bad_id", "presentation view model schema has the wrong $id", str(VIEW_MODEL_SCHEMA_REL)))
    findings.extend(validate_contract(repo_root, load_toml(repo_root / CONTRACT_REL)))
    findings.extend(
        validate_view_model(
            repo_root,
            load_json(repo_root / READ_ONLY_VIEW_MODEL_REL),
            READ_ONLY_VIEW_MODEL_REL.as_posix(),
        )
    )
    return {"findings": findings, "view_models": 1}


def validate_fixtures(repo_root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    valid_count = 0
    invalid_count = 0
    fixture_root = repo_root / FIXTURE_DIR_REL
    if not fixture_root.exists():
        return {"findings": [finding("error", "fixture_dir_missing", f"missing {FIXTURE_DIR_REL}")], "valid_fixtures": 0, "invalid_fixtures": 0}
    for path in sorted(fixture_root.glob("*.json")):
        rel = path.relative_to(repo_root).as_posix()
        is_invalid = path.name.startswith("invalid_")
        is_valid = path.name.startswith("valid_")
        if not is_invalid and not is_valid:
            findings.append(finding("warning", "fixture_name_unclassified", "fixture name should start with valid_ or invalid_", rel))
            continue
        item_findings = validate_view_model(repo_root, load_json(path), rel, fixture=True)
        has_errors = any(item["level"] == "error" for item in item_findings)
        if is_invalid:
            invalid_count += 1
            if not has_errors:
                findings.append(finding("error", "invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
        else:
            valid_count += 1
            findings.extend(item_findings)
    return {"findings": findings, "valid_fixtures": valid_count, "invalid_fixtures": invalid_count}


def inventory(repo_root: Path) -> dict[str, Any]:
    result = validate_contracts(repo_root)
    view_model = load_json(repo_root / READ_ONLY_VIEW_MODEL_REL) if (repo_root / READ_ONLY_VIEW_MODEL_REL).exists() else {}
    return {
        "contract": CONTRACT_REL.as_posix(),
        "view_models": [view_model.get("view_model_id")] if view_model else [],
        "projection_kinds": sorted(projection_kinds(repo_root)) if (repo_root / PROJECTION_KIND_REL).exists() else [],
        "findings": result["findings"],
    }


def render_text(label: str, result: dict[str, Any]) -> str:
    errors = [item for item in result.get("findings", []) if item.get("level") == "error"]
    warnings = [item for item in result.get("findings", []) if item.get("level") == "warning"]
    status = "PASS" if not errors else "FAIL"
    extras = []
    for key in ("view_models", "valid_fixtures", "invalid_fixtures"):
        if key in result:
            extras.append(f"{key}={result[key]}")
    suffix = " " + " ".join(extras) if extras else ""
    lines = [f"presentation-contract {label}: {status}{suffix} errors={len(errors)} warnings={len(warnings)}"]
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
            print("presentation-contract inventory:")
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
