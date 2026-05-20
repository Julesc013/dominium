#!/usr/bin/env python3
"""Validate Dominium capability/refusal contracts, registries, and fixtures."""

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


CAPABILITY_CONTRACT_REL = Path("contracts/capability/capability.contract.toml")
CAPABILITY_SCHEMA_REL = Path("contracts/capability/capability.schema.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
CAPABILITY_KIND_REGISTRY_REL = Path("contracts/capability/capability_kind.registry.json")
CAPABILITY_REQUEST_SCHEMA_REL = Path("contracts/capability/capability_request.schema.json")
CAPABILITY_DECISION_SCHEMA_REL = Path("contracts/capability/capability_decision.schema.json")
DEGRADATION_POLICY_REL = Path("contracts/capability/degradation_policy.contract.toml")
RECOVERY_POLICY_REL = Path("contracts/capability/recovery_policy.contract.toml")
REFUSAL_CONTRACT_REL = Path("contracts/refusal/refusal.contract.toml")
REFUSAL_SCHEMA_REL = Path("contracts/refusal/refusal.schema.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
COMMAND_CONTRACT_REL = Path("contracts/command/command_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/capability_refusal/fixtures")

JSON_RELS = [
    CAPABILITY_SCHEMA_REL,
    CAPABILITY_REGISTRY_REL,
    CAPABILITY_KIND_REGISTRY_REL,
    CAPABILITY_REQUEST_SCHEMA_REL,
    CAPABILITY_DECISION_SCHEMA_REL,
    REFUSAL_SCHEMA_REL,
    REFUSAL_REGISTRY_REL,
]
TOML_RELS = [
    CAPABILITY_CONTRACT_REL,
    DEGRADATION_POLICY_REL,
    RECOVERY_POLICY_REL,
    REFUSAL_CONTRACT_REL,
]
EXPECTED_CONTRACT_IDS = {
    CAPABILITY_CONTRACT_REL: "dominium.capability.contract.v1",
    DEGRADATION_POLICY_REL: "dominium.capability.degradation_policy.v1",
    RECOVERY_POLICY_REL: "dominium.capability.recovery_policy.v1",
    REFUSAL_CONTRACT_REL: "dominium.refusal.contract.v1",
}
CAPABILITY_ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+$")
REFUSAL_ID_RE = re.compile(r"^dominium\.refusal\.[a-z0-9][a-z0-9_.-]+$")


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


def registry_ids(data: Dict[str, Any], key: str, id_key: str = "id") -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def read_kind_data(repo_root: Path) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    data = load_json(repo_root / CAPABILITY_KIND_REGISTRY_REL)
    return (
        registry_ids(data, "kinds"),
        {str(item) for item in as_list(data.get("decision_values")) if isinstance(item, str)},
        {str(item) for item in as_list(data.get("stability_values")) if isinstance(item, str)},
        {str(item) for item in as_list(data.get("recovery_actions")) if isinstance(item, str)},
    )


def read_diagnostic_codes(repo_root: Path) -> Set[str]:
    path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if not path.exists():
        return set()
    try:
        data = load_json(path)
    except Exception:
        return set()
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }


def read_refusal_codes(repo_root: Path) -> Set[str]:
    path = repo_root / REFUSAL_REGISTRY_REL
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
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


def validate_capability(data: Dict[str, Any], rel: str, kind_ids: Set[str], stability_values: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    cap_id = str(data.get("capability_id", ""))
    if not cap_id:
        findings.append(finding("error", "capability_missing_id", "capability is missing capability_id", rel))
    elif not CAPABILITY_ID_RE.match(cap_id) or "/" in cap_id or "\\" in cap_id:
        findings.append(finding("error", "capability_invalid_id", f"capability_id is not a lowercase dotted semantic id: {cap_id}", rel))
    for key in ["kind", "owner", "version", "stability", "description", "scope", "determinism_impact", "security_impact"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "capability_missing_required_field", f"capability missing {key}", rel))
    if data.get("kind") and data.get("kind") not in kind_ids:
        findings.append(finding("error", "capability_unknown_kind", f"unknown capability kind: {data.get('kind')}", rel))
    if data.get("stability") and data.get("stability") not in stability_values:
        findings.append(finding("error", "capability_unknown_stability", f"unknown capability stability: {data.get('stability')}", rel))
    if data.get("stability") == "stable" and not data.get("proof"):
        findings.append(finding("error", "stable_capability_missing_proof", "stable capability requires proof", rel))
    return findings


def validate_capability_registry(repo_root: Path) -> Tuple[List[Dict[str, Any]], int]:
    findings: List[Dict[str, Any]] = []
    kind_ids, _decision_values, stability_values, _recovery = read_kind_data(repo_root)
    data = load_json(repo_root / CAPABILITY_REGISTRY_REL)
    seen: Set[str] = set()
    for item in as_list(data.get("capabilities")):
        if not isinstance(item, dict):
            findings.append(finding("error", "capability_entry_not_object", "capability registry entry must be an object"))
            continue
        cap_id = str(item.get("capability_id", ""))
        if cap_id in seen:
            findings.append(finding("error", "capability_duplicate_id", f"duplicate capability_id: {cap_id}"))
        if cap_id:
            seen.add(cap_id)
        findings.extend(validate_capability(item, f"{CAPABILITY_REGISTRY_REL.as_posix()}:{cap_id or '<missing>'}", kind_ids, stability_values))
    required = {"domino.render.software", "domino.render.null", "domino.platform.win32.window", "domino.storage.local", "domino.package.validate", "dominium.workbench.validation", "dominium.command.fast_strict", "dominium.repo.validate"}
    missing = sorted(required - seen)
    if missing:
        findings.append(finding("error", "required_capabilities_missing", f"required initial capabilities missing: {', '.join(missing)}"))
    return findings, len(seen)


def diagnostic_values(item: Dict[str, Any]) -> List[str]:
    values: List[str] = []
    for key in ["diagnostic_codes", "related_diagnostic_codes"]:
        values.extend(str(value) for value in as_list(item.get(key)) if isinstance(value, str))
    return values


def recovery_action(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("action", ""))
    return ""


def validate_refusal(data: Dict[str, Any], rel: str, diagnostic_codes: Set[str], recovery_actions: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    code = str(data.get("code", ""))
    refusal_id = str(data.get("refusal_id", code))
    if not code:
        findings.append(finding("error", "refusal_missing_code", "refusal is missing code", rel))
    elif not REFUSAL_ID_RE.match(code):
        findings.append(finding("error", "refusal_invalid_code", f"refusal code is invalid: {code}", rel))
    if refusal_id and not REFUSAL_ID_RE.match(refusal_id):
        findings.append(finding("error", "refusal_invalid_id", f"refusal_id is invalid: {refusal_id}", rel))
    for key in ["owner", "category", "stability", "reason", "recovery"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "refusal_missing_required_field", f"refusal missing {key}", rel))
    if data.get("recovery") and isinstance(data.get("recovery"), dict):
        action = recovery_action(data.get("recovery"))
        if action not in recovery_actions:
            findings.append(finding("error", "refusal_unknown_recovery_action", f"unknown recovery action: {action}", rel))
    for diagnostic in diagnostic_values(data):
        if diagnostic_codes and diagnostic not in diagnostic_codes:
            findings.append(finding("error", "refusal_unknown_diagnostic", f"refusal references unknown diagnostic code: {diagnostic}", rel))
    return findings


def validate_refusal_registry(repo_root: Path) -> Tuple[List[Dict[str, Any]], int]:
    findings: List[Dict[str, Any]] = []
    _kind_ids, _decision_values, _stability, recovery_actions = read_kind_data(repo_root)
    diagnostic_codes = read_diagnostic_codes(repo_root)
    data = load_json(repo_root / REFUSAL_REGISTRY_REL)
    seen: Set[str] = set()
    for item in as_list(data.get("codes")):
        if not isinstance(item, dict):
            findings.append(finding("error", "refusal_entry_not_object", "refusal registry entry must be an object"))
            continue
        code = str(item.get("code", ""))
        if code in seen:
            findings.append(finding("error", "refusal_duplicate_code", f"duplicate refusal code: {code}"))
        if code:
            seen.add(code)
        findings.extend(validate_refusal(item, f"{REFUSAL_REGISTRY_REL.as_posix()}:{code or '<missing>'}", diagnostic_codes, recovery_actions))
    required = {
        "dominium.refusal.capability.missing",
        "dominium.refusal.capability.version_unsupported",
        "dominium.refusal.capability.conflict",
        "dominium.refusal.command.capability_missing",
        "dominium.refusal.command.unsupported_surface",
        "dominium.refusal.artifact.trust_insufficient",
        "dominium.refusal.schema.unsupported_version",
        "dominium.refusal.provider.unavailable",
        "dominium.refusal.platform.unsupported",
        "dominium.refusal.policy.denied",
    }
    missing = sorted(required - seen)
    if missing:
        findings.append(finding("error", "required_refusals_missing", f"required initial refusal codes missing: {', '.join(missing)}"))
    return findings, len(seen)


def validate_request(data: Dict[str, Any], rel: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for key in ["request_id", "requested_by", "capability_id", "required", "context", "evidence_requested"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "request_missing_required_field", f"capability request missing {key}", rel))
    cap_id = str(data.get("capability_id", ""))
    if cap_id and not CAPABILITY_ID_RE.match(cap_id):
        findings.append(finding("error", "request_invalid_capability_id", f"request capability_id is invalid: {cap_id}", rel))
    return findings


def validate_decision(data: Dict[str, Any], rel: str, decision_values: Set[str], refusal_codes: Set[str], recovery_actions: Set[str], diagnostic_codes: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for key in ["request_id", "capability_id", "decision", "diagnostic_codes", "recovery", "evidence_ref"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "decision_missing_required_field", f"capability decision missing {key}", rel))
    decision = str(data.get("decision", ""))
    if decision and decision not in decision_values:
        findings.append(finding("error", "decision_unknown_value", f"unknown decision value: {decision}", rel))
    cap_id = str(data.get("capability_id", ""))
    selected = str(data.get("selected_capability", ""))
    if cap_id and not CAPABILITY_ID_RE.match(cap_id):
        findings.append(finding("error", "decision_invalid_capability_id", f"decision capability_id is invalid: {cap_id}", rel))
    if selected and not CAPABILITY_ID_RE.match(selected):
        findings.append(finding("error", "decision_invalid_selected_capability", f"selected_capability is invalid: {selected}", rel))
    if decision == "selected":
        if not selected and not data.get("selected_provider"):
            findings.append(finding("error", "selected_missing_selection", "selected decision requires selected_capability or selected_provider", rel))
        if selected and selected != cap_id:
            findings.append(finding("error", "silent_fallback_forbidden", "selected decision changes capability without degraded decision", rel))
    if decision == "degraded":
        if not data.get("degraded_from") or not data.get("degraded_to"):
            findings.append(finding("error", "degraded_missing_from_to", "degraded decision requires degraded_from and degraded_to", rel))
        if not as_list(data.get("diagnostic_codes")):
            findings.append(finding("error", "degraded_missing_diagnostic", "degraded decision requires diagnostic_codes", rel))
    if decision in {"refused", "unavailable"}:
        refusal = str(data.get("refusal_code", ""))
        if not refusal:
            findings.append(finding("error", "refused_missing_refusal_code", f"{decision} decision requires refusal_code", rel))
        elif refusal not in refusal_codes:
            findings.append(finding("error", "decision_unknown_refusal_code", f"unknown refusal_code: {refusal}", rel))
    action = recovery_action(data.get("recovery"))
    if data.get("recovery") and isinstance(data.get("recovery"), dict) and action not in recovery_actions:
        findings.append(finding("error", "decision_unknown_recovery_action", f"unknown recovery action: {action}", rel))
    for diagnostic in as_list(data.get("diagnostic_codes")):
        if diagnostic_codes and diagnostic not in diagnostic_codes:
            findings.append(finding("error", "decision_unknown_diagnostic", f"decision references unknown diagnostic code: {diagnostic}", rel))
    return findings


def validate_fixture_files(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    kind_ids, decision_values, stability_values, recovery_actions = read_kind_data(repo_root)
    diagnostic_codes = read_diagnostic_codes(repo_root)
    refusal_codes = read_refusal_codes(repo_root)
    cases = [
        ("valid_capability.json", "capability", True),
        ("invalid_capability_missing_id.json", "capability", False),
        ("valid_capability_request.json", "request", True),
        ("valid_capability_decision_selected.json", "decision", True),
        ("valid_capability_decision_degraded.json", "decision", True),
        ("valid_capability_decision_refused.json", "decision", True),
        ("invalid_refusal_missing_recovery.json", "refusal", False),
        ("invalid_silent_fallback.json", "decision", False),
    ]
    results: List[Dict[str, Any]] = []
    for name, kind, expected_valid in cases:
        path = repo_root / FIXTURE_DIR_REL / name
        rel = path.relative_to(repo_root).as_posix() if path.exists() else (FIXTURE_DIR_REL / name).as_posix()
        try:
            data = load_json(path)
            if kind == "capability":
                case_findings = validate_capability(data, rel, kind_ids, stability_values)
            elif kind == "request":
                case_findings = validate_request(data, rel)
            elif kind == "decision":
                case_findings = validate_decision(data, rel, decision_values, refusal_codes, recovery_actions, diagnostic_codes)
            else:
                case_findings = validate_refusal(data, rel, diagnostic_codes, recovery_actions)
        except Exception as exc:
            case_findings = [finding("error", "fixture_parse_failed", f"fixture parse failed: {exc}", rel)]
        errors = [item for item in case_findings if item["level"] == "error"]
        results.append({"path": rel, "expected": "valid" if expected_valid else "invalid", "errors": len(errors), "findings": case_findings})
        if expected_valid and errors:
            findings.append(finding("error", "valid_fixture_failed", f"valid fixture failed: {rel}", rel))
        if not expected_valid and not errors:
            findings.append(finding("error", "invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
    return findings, {"status": "pass" if not findings else "fail", "fixture_count": len(results), "fixtures": results}


def validate_diagnostic_codes(repo_root: Path) -> List[Dict[str, Any]]:
    diagnostic_codes = read_diagnostic_codes(repo_root)
    if not diagnostic_codes:
        return [finding("warning", "diagnostics_registry_missing", "diagnostics registry missing or unreadable")]
    required = {
        "DOM-CAPABILITY-MISSING",
        "DOM-CAPABILITY-DEGRADED",
        "DOM-CAPABILITY-CONFLICT",
        "DOM-CAPABILITY-VERSION-UNSUPPORTED",
        "DOM-REFUSAL-ISSUED",
        "DOM-PROVIDER-UNAVAILABLE",
        "DOM-PLATFORM-UNSUPPORTED",
        "DOM-SILENT-FALLBACK-FORBIDDEN",
    }
    missing = sorted(required - diagnostic_codes)
    if missing:
        return [finding("warning", "capability_diagnostics_missing", f"capability/refusal diagnostic codes not registered: {', '.join(missing)}")]
    return []


def validate_command_cross_reference(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / COMMAND_CONTRACT_REL
    if not path.exists():
        return []
    try:
        data = load_toml(path)
    except Exception as exc:
        return [finding("warning", "command_surface_unreadable", f"could not read command surface contract: {exc}")]
    integration = data.get("integration", {})
    if not isinstance(integration, dict) or integration.get("capability_contract") != CAPABILITY_CONTRACT_REL.as_posix():
        return [finding("warning", "command_capability_cross_reference_missing", "command surface does not reference capability contract")]
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


def inventory(repo_root: Path) -> Dict[str, Any]:
    files = git_ls_files(repo_root)
    roots = {
        "runtime/render": "capability_candidate",
        "runtime/platform": "provider_candidate",
        "runtime/storage": "capability_candidate",
        "runtime/network": "capability_candidate",
        "runtime/audio": "capability_candidate",
        "runtime/input": "capability_candidate",
        "runtime/package": "artifact_trust_candidate",
        "apps/workbench": "future_provider_model_item",
        "contracts/refusal": "command_required_capability_candidate",
        "contracts/command": "command_required_capability_candidate",
        "contracts/provider": "future_provider_model_item",
        "content/packs": "artifact_trust_candidate",
        "release": "deferred",
    }
    categories = {
        "capability_candidate": 0,
        "provider_candidate": 0,
        "command_required_capability_candidate": 0,
        "artifact_trust_candidate": 0,
        "future_provider_model_item": 0,
        "deferred": 0,
    }
    examples: Dict[str, List[str]] = {key: [] for key in categories}
    for path in files:
        norm = path.replace("\\", "/")
        matched = False
        for prefix, category in roots.items():
            if norm.startswith(prefix + "/") or norm == prefix:
                categories[category] += 1
                if len(examples[category]) < 8:
                    examples[category].append(norm)
                matched = True
                break
        if not matched and ("capability" in norm or "provider" in norm or "backend" in norm):
            categories["deferred"] += 1
            if len(examples["deferred"]) < 8:
                examples["deferred"].append(norm)
    return {
        "files_scanned": len(files),
        "categories": categories,
        "examples": examples,
        "status": "warning",
        "note": "Inventory is descriptive only; CAPABILITY-REFUSAL-LAW-01 does not migrate providers or runtime behavior.",
    }


def validate_all(repo_root: Path, include_fixtures: bool) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    capability_count = 0
    refusal_count = 0
    fixture_summary = {"status": "not_run", "fixture_count": 0}
    if not any(item["level"] == "error" for item in findings):
        try:
            capability_findings, capability_count = validate_capability_registry(repo_root)
            refusal_findings, refusal_count = validate_refusal_registry(repo_root)
            findings.extend(capability_findings)
            findings.extend(refusal_findings)
            findings.extend(validate_diagnostic_codes(repo_root))
            findings.extend(validate_command_cross_reference(repo_root))
            if include_fixtures:
                fixture_findings, fixture_summary = validate_fixture_files(repo_root)
                findings.extend(fixture_findings)
        except Exception as exc:
            findings.append(finding("error", "validator_exception", f"capability/refusal validation failed: {exc}"))
    return findings, {"capabilities": capability_count, "refusals": refusal_count, "fixtures": fixture_summary}


def print_list(repo_root: Path) -> None:
    kind_ids, decision_values, _stability, recovery = read_kind_data(repo_root)
    print("capability kinds:")
    for item in sorted(kind_ids):
        print(f"- {item}")
    print("decision values:")
    for item in sorted(decision_values):
        print(f"- {item}")
    print("recovery actions:")
    for item in sorted(recovery):
        print(f"- {item}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero on errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--fixtures", action="store_true", help="Validate capability/refusal fixtures.")
    parser.add_argument("--inventory", action="store_true", help="Run descriptive capability/refusal inventory.")
    parser.add_argument("--list", action="store_true", help="List capability kinds and recovery actions.")
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
        "validator": "check_capability_refusal",
        "status": status,
        "capabilities_registered": summary["capabilities"],
        "refusal_codes_registered": summary["refusals"],
        "fixtures": summary["fixtures"],
        "inventory": inv,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"capability/refusal: {status}")
        print(f"capabilities: {summary['capabilities']}")
        print(f"refusal_codes: {summary['refusals']}")
        print(f"errors: {len(errors)}")
        print(f"warnings: {len(warnings)}")
        if args.fixtures:
            print(f"fixtures: {summary['fixtures']['status']} count={summary['fixtures']['fixture_count']}")
        if args.inventory:
            print(f"inventory: {inv['status']} files_scanned={inv['files_scanned']}")
        for item in findings[:80]:
            location = f" {item['path']}:" if item.get("path") else ""
            print(f"{item['level'].upper()} {item['code']}:{location} {item['message']}")
    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
