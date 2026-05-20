#!/usr/bin/env python3
"""Validate the Dominium test tier contract."""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised only on older Python.
    tomllib = None  # type: ignore[assignment]


REQUIRED_TIERS = ("T0", "T1", "T2", "T3", "T4")
REQUIRED_GATES = ("fast_strict", "extended", "release", "full")
ALLOWED_GATES = REQUIRED_GATES + ("release_candidate",)
CONTRACT_REL = Path("contracts") / "testing" / "test_tiers.contract.toml"
SCHEMA_REL = Path("contracts") / "testing" / "test_tiers.schema.json"


def _repo_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parents[3]


def _load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return _load_toml_fallback(path)
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("contract root must be a TOML table")
    return payload


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if char == "#" and not in_string:
            return line[:index]
    return line


def _parse_value(text: str) -> Any:
    value = text.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        return value


def _target(root: dict[str, Any], parts: list[str]) -> dict[str, Any]:
    current = root
    for part in parts:
        child = current.setdefault(part, {})
        if not isinstance(child, dict):
            raise ValueError(f"TOML table conflicts with scalar: {'.'.join(parts)}")
        current = child
    return current


def _logical_lines(path: Path) -> list[str]:
    lines: list[str] = []
    pending = ""
    balance = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if pending:
            pending += " " + line
        else:
            pending = line
        balance += line.count("[") - line.count("]")
        if balance <= 0:
            lines.append(pending)
            pending = ""
            balance = 0
    if pending:
        lines.append(pending)
    return lines


def _load_toml_fallback(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current = root
    for line in _logical_lines(path):
        if line.startswith("[[") and line.endswith("]]"):
            key = line[2:-2].strip()
            if key != "commands":
                raise ValueError(f"fallback TOML reader supports only [[commands]], not [[{key}]]")
            commands = root.setdefault("commands", [])
            if not isinstance(commands, list):
                raise ValueError("commands must be an array")
            current = {}
            commands.append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            parts = [part.strip() for part in line[1:-1].split(".") if part.strip()]
            current = _target(root, parts)
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML assignment: {line}")
        key, value = line.split("=", 1)
        current[key.strip()] = _parse_value(value)
    return root


def _add(findings: list[dict[str, str]], severity: str, code: str, message: str) -> None:
    findings.append({"severity": severity, "code": code, "message": message})


def validate_contract(repo_root: Path, strict: bool) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    contract_path = repo_root / CONTRACT_REL
    schema_path = repo_root / SCHEMA_REL

    if not contract_path.is_file():
        _add(findings, "error", "missing_contract", f"missing {CONTRACT_REL.as_posix()}")
        return _result(findings, None, strict)
    if not schema_path.is_file():
        _add(findings, "error", "missing_schema", f"missing {SCHEMA_REL.as_posix()}")
    else:
        try:
            with schema_path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # noqa: BLE001 - report parse failure as contract evidence.
            _add(findings, "error", "schema_parse_failed", f"{SCHEMA_REL.as_posix()}: {exc}")

    try:
        payload = _load_toml(contract_path)
    except Exception as exc:  # noqa: BLE001
        _add(findings, "error", "contract_parse_failed", f"{CONTRACT_REL.as_posix()}: {exc}")
        return _result(findings, None, strict)

    if payload.get("schema_version") != "dominium.test_tiers.v1":
        _add(findings, "error", "schema_version", "schema_version must be dominium.test_tiers.v1")
    contract = payload.get("contract")
    if not isinstance(contract, dict):
        _add(findings, "error", "contract_missing", "contract table is required")
    else:
        for key in ("id", "status", "owner", "purpose"):
            if not str(contract.get(key, "")).strip():
                _add(findings, "error", "contract_field_missing", f"contract missing {key}")

    tiers = payload.get("tiers")
    if not isinstance(tiers, dict):
        _add(findings, "error", "tiers_missing", "tiers table is required")
        tiers = {}
    for tier_id in REQUIRED_TIERS:
        tier = tiers.get(tier_id)
        if not isinstance(tier, dict):
            _add(findings, "error", "tier_missing", f"missing tier {tier_id}")
            continue
        for key in (
            "name",
            "purpose",
            "owner",
            "timeout_guidance",
            "failure_policy",
            "known_debt_policy",
            "promotion_rule",
        ):
            if not str(tier.get(key, "")).strip():
                _add(findings, "error", "tier_field_missing", f"{tier_id} missing {key}")
        for key in ("normal_gate_member", "release_gate_member", "full_gate_member"):
            if not isinstance(tier.get(key), bool):
                _add(findings, "error", "tier_membership_missing", f"{tier_id} missing boolean {key}")

    gates = payload.get("gates")
    if not isinstance(gates, dict):
        _add(findings, "error", "gates_missing", "gates table is required")
        gates = {}
    for gate_id in REQUIRED_GATES:
        gate = gates.get(gate_id)
        if not isinstance(gate, dict):
            _add(findings, "error", "gate_missing", f"missing gate {gate_id}")
            continue
        gate_tiers = gate.get("tiers")
        if not isinstance(gate_tiers, list):
            _add(findings, "error", "gate_tiers_missing", f"{gate_id} missing tiers list")
        for key in ("name", "purpose", "default_command", "failure_policy"):
            if not str(gate.get(key, "")).strip():
                _add(findings, "error", "gate_field_missing", f"{gate_id} missing {key}")
        if not isinstance(gate.get("target_seconds"), int):
            _add(findings, "error", "gate_target_missing", f"{gate_id} missing integer target_seconds")

    fast_tiers = list((gates.get("fast_strict") or {}).get("tiers") or [])
    for tier_id in ("T0", "T1", "T2"):
        if tier_id not in fast_tiers:
            _add(findings, "error", "fast_strict_membership", f"fast_strict must include {tier_id}")
    if "T4" in fast_tiers:
        _add(findings, "error", "fast_strict_full_tier", "fast_strict must exclude T4")
    release_tiers = list((gates.get("release") or {}).get("tiers") or [])
    if "T4" not in release_tiers:
        _add(findings, "error", "release_membership", "release gate must include selected T4")
    full_tiers = list((gates.get("full") or {}).get("tiers") or [])
    if "T4" not in full_tiers:
        _add(findings, "error", "full_membership", "full gate must include T4")

    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        _add(findings, "error", "commands_missing", "commands array is required")
        commands = []

    seen_ids: set[str] = set()
    commands_by_tier = {tier_id: 0 for tier_id in REQUIRED_TIERS}
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            _add(findings, "error", "command_shape", f"command {index} must be a table")
            continue
        command_id = str(command.get("id", "")).strip()
        if not command_id:
            _add(findings, "error", "command_id_missing", f"command {index} missing id")
        elif command_id in seen_ids:
            _add(findings, "error", "command_id_duplicate", f"duplicate command id {command_id}")
        seen_ids.add(command_id)

        tier = str(command.get("tier", "")).strip()
        if tier not in REQUIRED_TIERS:
            _add(findings, "error", "command_tier_invalid", f"{command_id or index} has invalid tier {tier!r}")
        else:
            commands_by_tier[tier] += 1

        for key in ("owner", "failure_policy", "missing_policy", "warning_policy"):
            if not str(command.get(key, "")).strip():
                _add(findings, "error", "command_field_missing", f"{command_id or index} missing {key}")
        if not isinstance(command.get("timeout_seconds"), int) or int(command.get("timeout_seconds", 0)) <= 0:
            _add(findings, "error", "command_timeout_missing", f"{command_id or index} missing positive timeout_seconds")
        if not isinstance(command.get("required"), bool):
            _add(findings, "error", "command_required_missing", f"{command_id or index} missing boolean required")

        command_type = str(command.get("type", "")).strip()
        if command_type == "argv":
            argv = command.get("argv")
            if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
                _add(findings, "error", "command_argv_missing", f"{command_id or index} missing argv list")
        elif command_type == "builtin":
            if not str(command.get("builtin", "")).strip():
                _add(findings, "error", "command_builtin_missing", f"{command_id or index} missing builtin name")
        else:
            _add(findings, "error", "command_type_invalid", f"{command_id or index} has invalid type {command_type!r}")

        gates_value = command.get("gates")
        if not isinstance(gates_value, list) or not gates_value:
            _add(findings, "error", "command_gates_missing", f"{command_id or index} missing gates")
        else:
            for gate_id in gates_value:
                if gate_id not in ALLOWED_GATES:
                    _add(findings, "error", "command_gate_invalid", f"{command_id or index} has invalid gate {gate_id!r}")

        if command_id == "t4.full_ctest" and "fast_strict" in list(gates_value or []):
            _add(findings, "error", "full_ctest_normal_gate", "full CTest must not be part of fast_strict")
        for output in command.get("evidence_outputs") or []:
            if not isinstance(output, str):
                continue
            normalized = output.replace("\\", "/")
            if (
                normalized.startswith(".dominium.local/")
                or normalized.startswith(".aide.local/")
                or normalized.startswith("out/")
                or normalized.startswith("build/")
                or normalized.startswith("dist/")
            ) and "local" not in normalized.lower():
                _add(findings, "warning", "generated_output_evidence", f"{command_id or index} lists generated output evidence: {output}")

    for tier_id, count in commands_by_tier.items():
        if count == 0:
            _add(findings, "error", "tier_without_commands", f"{tier_id} has no commands")

    if strict:
        normal_required = [
            str(command.get("id", ""))
            for command in commands
            if isinstance(command, dict)
            and command.get("required") is True
            and str(command.get("tier", "")) in {"T0", "T1", "T2"}
            and "fast_strict" not in list(command.get("gates") or [])
        ]
        for command_id in normal_required:
            _add(findings, "error", "normal_command_not_in_fast_strict", f"{command_id} must be in fast_strict")
        full_ctest = [command for command in commands if isinstance(command, dict) and command.get("id") == "t4.full_ctest"]
        if not full_ctest:
            _add(findings, "error", "full_ctest_missing", "T4 full CTest command is required")

    return _result(findings, payload, strict)


def _result(findings: list[dict[str, str]], payload: dict[str, Any] | None, strict: bool) -> dict[str, Any]:
    errors = [item for item in findings if item["severity"] == "error"]
    warnings = [item for item in findings if item["severity"] == "warning"]
    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "schema_version": "dominium.test_tier_validation_result.v1",
        "status": status,
        "strict": bool(strict),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
        "contract_schema_version": None if payload is None else payload.get("schema_version"),
        "default_gate": None if payload is None else payload.get("default_gate"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args(argv)

    result = validate_contract(_repo_root(args.repo_root), strict=bool(args.strict))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"test tier contract validation: {result['status']}")
        for item in result["findings"]:
            print(f"- {item['severity'].upper()} {item['code']}: {item['message']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
