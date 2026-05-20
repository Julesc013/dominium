#!/usr/bin/env python3
"""Validate Dominium versioning and deprecation law contracts and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - Python 3.8 fallback
    tomllib = None


VERSIONING_CONTRACT_REL = Path("contracts/versioning/versioning.contract.toml")
LIFECYCLE_REGISTRY_REL = Path("contracts/versioning/lifecycle_state.registry.json")
VERSION_COMPATIBILITY_SCHEMA_REL = Path("contracts/versioning/version_compatibility.schema.json")
DEPRECATION_NOTICE_SCHEMA_REL = Path("contracts/versioning/deprecation_notice.schema.json")
DEPRECATION_POLICY_REL = Path("contracts/versioning/deprecation_policy.contract.toml")
RETIREMENT_POLICY_REL = Path("contracts/versioning/retirement_policy.contract.toml")
REMOVAL_POLICY_REL = Path("contracts/versioning/removal_policy.contract.toml")
COMPATIBILITY_RANGE_SCHEMA_REL = Path("contracts/versioning/compatibility_range.schema.json")
VERSION_TRANSITION_SCHEMA_REL = Path("contracts/versioning/version_transition.schema.json")
SURFACE_LIFECYCLE_REL = Path("contracts/versioning/surface_lifecycle.contract.toml")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/versioning/fixtures")

JSON_RELS = [
    LIFECYCLE_REGISTRY_REL,
    VERSION_COMPATIBILITY_SCHEMA_REL,
    DEPRECATION_NOTICE_SCHEMA_REL,
    COMPATIBILITY_RANGE_SCHEMA_REL,
    VERSION_TRANSITION_SCHEMA_REL,
]
TOML_RELS = [
    VERSIONING_CONTRACT_REL,
    DEPRECATION_POLICY_REL,
    RETIREMENT_POLICY_REL,
    REMOVAL_POLICY_REL,
    SURFACE_LIFECYCLE_REL,
]
EXPECTED_CONTRACT_IDS = {
    VERSIONING_CONTRACT_REL: "dominium.versioning.law.v1",
    DEPRECATION_POLICY_REL: "dominium.versioning.deprecation_policy.v1",
    RETIREMENT_POLICY_REL: "dominium.versioning.retirement_policy.v1",
    REMOVAL_POLICY_REL: "dominium.versioning.removal_policy.v1",
    SURFACE_LIFECYCLE_REL: "dominium.versioning.surface_lifecycle.v1",
}
REQUIRED_LIFECYCLE_STATES = {
    "experimental",
    "provisional",
    "stable",
    "deprecated",
    "retired",
    "removed",
    "generated",
    "fixture",
    "historical",
}
REQUIRED_PUBLIC_SURFACES = {
    "dominium.versioning.law.v1",
    "dominium.lifecycle.state.registry.v1",
    "dominium.deprecation.notice.v1",
    "dominium.version.compatibility.v1",
    "dominium.version_deprecation.validator.v1",
}
REQUIRED_DIAGNOSTICS = {
    "DOM-VERSION-INCOMPATIBLE",
    "DOM-VERSION-UNSUPPORTED",
    "DOM-LIFECYCLE-INVALID-TRANSITION",
    "DOM-DEPRECATION-MISSING-REPLACEMENT",
    "DOM-RETIREMENT-MISSING-POLICY",
    "DOM-REMOVAL-WITHOUT-RETIREMENT",
    "DOM-STABLE-SURFACE-MISSING-COMPATIBILITY",
    "DOM-BREAKING-CHANGE-MISSING-MIGRATION",
}
REQUIRED_REFUSALS = {
    "dominium.refusal.version.unsupported",
    "dominium.refusal.version.incompatible",
    "dominium.refusal.surface.retired",
    "dominium.refusal.surface.removed",
    "dominium.refusal.migration.required",
    "dominium.refusal.replacement.required",
}
COMPATIBILITY_MODES = {"exact", "minimum", "maximum", "range", "any_provisional", "incompatible_refuse"}
SURFACE_ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)+$")


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


def registry_ids(data: Dict[str, Any], key: str, id_key: str) -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
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


def read_optional_registry(path: Path, key: str, id_key: str) -> Set[str]:
    if not path.exists():
        return set()
    try:
        return registry_ids(load_json(path), key, id_key)
    except Exception:
        return set()


def validate_json_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_json_contract", f"missing JSON contract: {rel.as_posix()}", rel.as_posix()))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_json", f"{rel.as_posix()} does not parse as JSON: {exc}", rel.as_posix()))
            continue
        if not isinstance(data, dict):
            findings.append(finding("error", "json_root_not_object", f"{rel.as_posix()} must be a JSON object", rel.as_posix()))
    return findings


def validate_toml_contracts(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in TOML_RELS:
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_toml_contract", f"missing TOML contract: {rel.as_posix()}", rel.as_posix()))
            continue
        try:
            data = load_toml(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_toml", f"{rel.as_posix()} does not parse as TOML: {exc}", rel.as_posix()))
            continue
        contract = data.get("contract", {})
        if not isinstance(contract, dict) or contract.get("id") != EXPECTED_CONTRACT_IDS[rel]:
            findings.append(finding("error", "unexpected_contract_id", f"{rel.as_posix()} has unexpected or missing contract id", rel.as_posix()))
    return findings


def read_lifecycle(repo_root: Path) -> Tuple[Set[str], Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    data = load_json(repo_root / LIFECYCLE_REGISTRY_REL)
    states = registry_ids(data, "states", "state")
    allowed = {
        (str(item.get("from")), str(item.get("to")))
        for item in as_list(data.get("allowed_transitions"))
        if isinstance(item, dict) and item.get("from") and item.get("to")
    }
    forbidden = {
        (str(item.get("from")), str(item.get("to")))
        for item in as_list(data.get("forbidden_transitions"))
        if isinstance(item, dict) and item.get("from") and item.get("to")
    }
    return states, allowed, forbidden


def validate_lifecycle_registry(repo_root: Path) -> Tuple[List[Dict[str, Any]], int]:
    findings: List[Dict[str, Any]] = []
    try:
        states, allowed, forbidden = read_lifecycle(repo_root)
    except Exception as exc:
        return [finding("error", "lifecycle_registry_unreadable", f"lifecycle registry cannot be read: {exc}")], 0
    missing = sorted(REQUIRED_LIFECYCLE_STATES - states)
    if missing:
        findings.append(finding("error", "lifecycle_states_missing", f"required lifecycle states missing: {', '.join(missing)}", LIFECYCLE_REGISTRY_REL.as_posix()))
    required_transitions = {
        ("experimental", "provisional"),
        ("provisional", "stable"),
        ("stable", "deprecated"),
        ("deprecated", "retired"),
        ("retired", "removed"),
        ("generated", "provisional"),
        ("generated", "stable"),
    }
    missing_transitions = sorted(required_transitions - allowed)
    if missing_transitions:
        rendered = ", ".join(f"{src}->{dst}" for src, dst in missing_transitions)
        findings.append(finding("error", "lifecycle_transitions_missing", f"required allowed transitions missing: {rendered}", LIFECYCLE_REGISTRY_REL.as_posix()))
    if ("stable", "removed") not in forbidden:
        findings.append(finding("error", "lifecycle_forbidden_transition_missing", "stable->removed must be explicitly forbidden", LIFECYCLE_REGISTRY_REL.as_posix()))
    return findings, len(states)


def validate_public_surface_registration(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / PUBLIC_SURFACE_REGISTRY_REL
    if not path.exists():
        return [finding("warning", "public_surface_registry_missing", "public surface registry not present")]
    ids = public_surface_ids(path)
    missing = sorted(REQUIRED_PUBLIC_SURFACES - ids)
    if missing:
        return [finding("error", "version_public_surfaces_missing", f"version/deprecation public surfaces missing: {', '.join(missing)}", PUBLIC_SURFACE_REGISTRY_REL.as_posix())]
    return []


def validate_diagnostic_refusal_registration(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    diagnostic_path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if diagnostic_path.exists():
        diagnostics = read_optional_registry(diagnostic_path, "codes", "code")
        missing = sorted(REQUIRED_DIAGNOSTICS - diagnostics)
        if missing:
            findings.append(finding("error", "version_diagnostics_missing", f"version/deprecation diagnostics missing: {', '.join(missing)}", DIAGNOSTIC_REGISTRY_REL.as_posix()))
    else:
        findings.append(finding("warning", "diagnostics_registry_missing", "diagnostic registry not present"))
    refusal_path = repo_root / REFUSAL_REGISTRY_REL
    if refusal_path.exists():
        refusals = read_optional_registry(refusal_path, "codes", "code")
        missing = sorted(REQUIRED_REFUSALS - refusals)
        if missing:
            findings.append(finding("error", "version_refusals_missing", f"version/deprecation refusals missing: {', '.join(missing)}", REFUSAL_REGISTRY_REL.as_posix()))
    else:
        findings.append(finding("warning", "refusal_registry_missing", "refusal registry not present"))
    return findings


def validate_surface_id(value: str, path: str) -> List[Dict[str, Any]]:
    if not value:
        return [finding("error", "missing_surface_id", "surface_id is required", path)]
    if not SURFACE_ID_RE.match(value):
        return [finding("error", "bad_surface_id", f"surface_id is not lowercase dotted ID: {value}", path)]
    if "/" in value or "\\" in value or ":" in value:
        return [finding("error", "path_as_surface_id", f"surface_id must not be path-like: {value}", path)]
    return []


def compatibility_range_valid(value: Any, path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if not isinstance(value, dict):
        return [finding("error", "missing_compatibility_range", "compatibility_range object is required", path)]
    mode = str(value.get("mode") or "")
    if mode not in COMPATIBILITY_MODES:
        findings.append(finding("error", "unknown_compatibility_mode", f"unknown compatibility range mode: {mode}", path))
    if mode == "exact" and not value.get("exact"):
        findings.append(finding("error", "exact_range_missing_version", "exact compatibility range requires exact", path))
    if mode == "minimum" and not value.get("minimum"):
        findings.append(finding("error", "minimum_range_missing_version", "minimum compatibility range requires minimum", path))
    if mode == "maximum" and not value.get("maximum"):
        findings.append(finding("error", "maximum_range_missing_version", "maximum compatibility range requires maximum", path))
    if mode == "range" and not (value.get("minimum") and value.get("maximum")):
        findings.append(finding("error", "range_missing_bounds", "range compatibility requires minimum and maximum", path))
    if mode == "incompatible_refuse" and not as_list(value.get("refusal_codes")):
        findings.append(finding("error", "incompatible_range_missing_refusal", "incompatible_refuse requires refusal_codes", path))
    return findings


def validate_version_compatibility(data: Dict[str, Any], *, path: str, lifecycle_states: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_surface_id(str(data.get("surface_id") or ""), path))
    for key in ["kind", "version", "owner", "lifecycle_state", "stability", "introduced_in", "migration_policy", "refusal_policy", "proof"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "version_policy_missing_field", f"version compatibility policy missing {key}", path))
    lifecycle_state = str(data.get("lifecycle_state") or "")
    if lifecycle_state and lifecycle_state not in lifecycle_states:
        findings.append(finding("error", "unknown_lifecycle_state", f"unknown lifecycle_state: {lifecycle_state}", path))
    stable = lifecycle_state == "stable" or str(data.get("stability") or "") == "stable"
    if stable:
        if "compatibility_range" not in data:
            findings.append(finding("error", "stable_surface_missing_compatibility", "stable surface requires compatibility_range", path))
        elif not as_list(data.get("proof")):
            findings.append(finding("error", "stable_surface_missing_proof", "stable surface requires proof", path))
    if "compatibility_range" in data:
        findings.extend(compatibility_range_valid(data.get("compatibility_range"), path))
    return findings


def validate_deprecation_notice(
    data: Dict[str, Any],
    *,
    path: str,
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_surface_id(str(data.get("surface_id") or ""), path))
    for key in ["deprecated_version", "deprecated_date", "migration_path", "refusal_behavior_after_retirement", "removal_policy", "owner", "proof", "evidence"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "deprecation_notice_missing_field", f"deprecation notice missing {key}", path))
    if not data.get("replacement") and not data.get("no_replacement_reason"):
        findings.append(finding("error", "deprecation_missing_replacement", "deprecation requires replacement or no_replacement_reason", path))
    behavior = data.get("refusal_behavior_after_retirement")
    if isinstance(behavior, dict):
        for code in [str(item) for item in as_list(behavior.get("diagnostic_codes")) if item]:
            if diagnostic_codes and code not in diagnostic_codes:
                findings.append(finding("error", "unknown_diagnostic_code", f"unknown diagnostic code: {code}", path))
        for code in [str(item) for item in as_list(behavior.get("refusal_codes")) if item]:
            if refusal_codes and code not in refusal_codes:
                findings.append(finding("error", "unknown_refusal_code", f"unknown refusal code: {code}", path))
    removal = data.get("removal_policy")
    if isinstance(removal, dict) and removal.get("retirement_required") is not True:
        findings.append(finding("error", "deprecation_removal_without_retirement", "deprecation removal_policy must require retirement", path))
    return findings


def version_major(version: str) -> Optional[int]:
    match = re.match(r"^(\d+)(?:\.|$)", version)
    if not match:
        return None
    return int(match.group(1))


def migration_is_explicit(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    mode = str(value.get("mode") or value.get("policy") or "")
    return mode not in {"", "none", "deferred"}


def refusal_is_explicit(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return bool(value.get("required") is True and (as_list(value.get("codes")) or value.get("code")))


def validate_version_transition(
    data: Dict[str, Any],
    *,
    path: str,
    lifecycle_states: Set[str],
    allowed_transitions: Set[Tuple[str, str]],
    forbidden_transitions: Set[Tuple[str, str]],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_surface_id(str(data.get("surface_id") or ""), path))
    for key in ["from_version", "to_version", "from_lifecycle_state", "to_lifecycle_state", "change_type", "compatibility_impact", "migration_policy", "refusal_policy", "proof"]:
        if data.get(key) in (None, "", []):
            findings.append(finding("error", "version_transition_missing_field", f"version transition missing {key}", path))
    from_state = str(data.get("from_lifecycle_state") or "")
    to_state = str(data.get("to_lifecycle_state") or "")
    if from_state and from_state not in lifecycle_states:
        findings.append(finding("error", "unknown_lifecycle_state", f"unknown from_lifecycle_state: {from_state}", path))
    if to_state and to_state not in lifecycle_states:
        findings.append(finding("error", "unknown_lifecycle_state", f"unknown to_lifecycle_state: {to_state}", path))
    transition = (from_state, to_state)
    if transition in forbidden_transitions:
        findings.append(finding("error", "lifecycle_invalid_transition", f"forbidden lifecycle transition: {from_state}->{to_state}", path))
    elif from_state != to_state and transition not in allowed_transitions:
        findings.append(finding("error", "lifecycle_invalid_transition", f"transition is not allowed: {from_state}->{to_state}", path))
    if to_state == "removed" and from_state != "retired":
        findings.append(finding("error", "removal_without_retirement", "removed transition requires prior retired state", path))

    breaking = data.get("change_type") == "breaking" or data.get("compatibility_impact") == "breaking"
    if breaking:
        from_major = version_major(str(data.get("from_version") or ""))
        to_major = version_major(str(data.get("to_version") or ""))
        major_bumped = from_major is not None and to_major is not None and to_major > from_major
        if not major_bumped and not (migration_is_explicit(data.get("migration_policy")) or refusal_is_explicit(data.get("refusal_policy"))):
            findings.append(finding("error", "breaking_change_missing_migration", "breaking change requires major version bump, migration, or refusal policy", path))
    return findings


def fixture_expectations() -> Dict[str, bool]:
    return {
        "valid_version_compatibility.json": True,
        "valid_deprecation_notice.json": True,
        "valid_version_transition.json": True,
        "invalid_deprecation_missing_replacement.json": False,
        "invalid_removal_without_retirement.json": False,
        "invalid_stable_surface_without_compatibility.json": False,
        "invalid_breaking_change_without_major_or_migration.json": False,
    }


def fixture_kind(filename: str) -> str:
    if "deprecation" in filename:
        return "deprecation_notice"
    if "transition" in filename or "removal" in filename or "breaking_change" in filename:
        return "version_transition"
    return "version_compatibility"


def run_fixture_checks(repo_root: Path, fixture_dir: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    base = repo_root / fixture_dir
    expected = fixture_expectations()
    if not base.exists():
        return [finding("error", "version_fixture_dir_missing", f"missing fixture directory: {fixture_dir.as_posix()}", fixture_dir.as_posix())], {"status": "fail", "valid": 0, "invalid": 0}

    lifecycle_states, allowed, forbidden = read_lifecycle(repo_root)
    diagnostic_codes = read_optional_registry(repo_root / DIAGNOSTIC_REGISTRY_REL, "codes", "code")
    refusal_codes = read_optional_registry(repo_root / REFUSAL_REGISTRY_REL, "codes", "code")
    valid_count = 0
    invalid_count = 0
    fixture_results: List[Dict[str, Any]] = []

    for filename, should_pass in expected.items():
        path = base / filename
        rel = f"{fixture_dir.as_posix()}/{filename}"
        if not path.exists():
            findings.append(finding("error", "version_fixture_missing", f"missing fixture: {rel}", rel))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            item_findings = [finding("error", "version_fixture_invalid_json", f"{rel} does not parse as JSON: {exc}", rel)]
        else:
            kind = fixture_kind(filename)
            if kind == "version_compatibility":
                item_findings = validate_version_compatibility(data, path=rel, lifecycle_states=lifecycle_states)
            elif kind == "deprecation_notice":
                item_findings = validate_deprecation_notice(data, path=rel, diagnostic_codes=diagnostic_codes, refusal_codes=refusal_codes)
            elif kind == "version_transition":
                item_findings = validate_version_transition(data, path=rel, lifecycle_states=lifecycle_states, allowed_transitions=allowed, forbidden_transitions=forbidden)
            else:
                item_findings = [finding("error", "unknown_fixture_kind", f"unknown fixture kind: {kind}", rel)]
        errors = [item for item in item_findings if item["level"] == "error"]
        if should_pass and errors:
            findings.extend(item_findings)
            findings.append(finding("error", "version_valid_fixture_failed", f"valid fixture failed validation: {rel}", rel))
        elif not should_pass and not errors:
            findings.append(finding("error", "version_invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
        if should_pass:
            valid_count += 1
        else:
            invalid_count += 1
        fixture_results.append({"path": rel, "expected": "valid" if should_pass else "invalid", "errors": len(errors)})
    return findings, {
        "status": "pass" if not findings else "fail",
        "valid": valid_count,
        "invalid": invalid_count,
        "fixtures": fixture_results,
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


def classify_inventory_path(path: str) -> Optional[str]:
    lowered = path.lower()
    if lowered.startswith("contracts/public_surface/"):
        return "surface_with_version"
    if lowered.startswith("contracts/artifact/"):
        return "artifact_with_version"
    if lowered.startswith(("contracts/schema/", "contracts/protocol/")):
        return "schema_protocol_with_version"
    if lowered.startswith("contracts/command/"):
        return "command_with_version"
    if lowered.startswith(("contracts/provider/", "contracts/module/", "contracts/workbench/", "contracts/app/")):
        return "descriptor_with_version"
    if lowered.startswith("contracts/replacement/"):
        return "replacement_policy_with_version"
    if lowered.endswith("pack.manifest.json"):
        return "pack_manifest_with_version"
    if lowered.startswith(("release/", "docs/release/")):
        return "release_surface_with_version"
    if lowered.startswith("docs/repo/audits/"):
        return "historical_or_audit_lifecycle"
    if "/fixtures/" in lowered or lowered.startswith("tests/contract/"):
        return "fixture_schema"
    return None


def inventory(repo_root: Path) -> Dict[str, Any]:
    files = git_ls_files(repo_root)
    counts: Dict[str, int] = {}
    examples: Dict[str, List[str]] = {}
    for path in files:
        category = classify_inventory_path(path)
        if category is None:
            continue
        counts[category] = counts.get(category, 0) + 1
        examples.setdefault(category, [])
        if len(examples[category]) < 8:
            examples[category].append(path)
    return {
        "status": "warning" if counts else "pass",
        "files_scanned": len(files),
        "version_like_files": sum(counts.values()),
        "by_category": counts,
        "examples": examples,
        "note": "Inventory is descriptive only; existing versions are not migrated by VERSION-DEPRECATION-LAW-01.",
    }


def validate_all(repo_root: Path, *, include_fixtures: bool, include_inventory: bool) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    lifecycle_findings, state_count = validate_lifecycle_registry(repo_root)
    findings.extend(lifecycle_findings)
    findings.extend(validate_public_surface_registration(repo_root))
    findings.extend(validate_diagnostic_refusal_registration(repo_root))

    fixtures: Dict[str, Any] = {"status": "not_run", "valid": 0, "invalid": 0}
    if include_fixtures:
        fixture_findings, fixtures = run_fixture_checks(repo_root, FIXTURE_DIR_REL)
        findings.extend(fixture_findings)
    inventory_result = inventory(repo_root) if include_inventory else {"status": "not_run"}

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "schema_version": "dominium.versioning.validation_result.v1",
        "validator": "check_version_deprecation",
        "status": "pass" if not errors else "fail",
        "lifecycle_states_registered": state_count,
        "findings": findings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "fixtures": fixtures,
        "inventory": inventory_result,
    }


def print_text(result: Dict[str, Any]) -> None:
    print(f"version/deprecation law: {result['status']}")
    print(f"lifecycle_states: {result.get('lifecycle_states_registered', 0)}")
    print(f"errors: {result['summary']['errors']}")
    print(f"warnings: {result['summary']['warnings']}")
    fixtures = result.get("fixtures", {})
    if fixtures.get("status") != "not_run":
        print(f"fixtures: {fixtures.get('status')} valid={fixtures.get('valid', 0)} invalid={fixtures.get('invalid', 0)}")
    inventory_result = result.get("inventory", {})
    if inventory_result.get("status") != "not_run":
        print(f"inventory: {inventory_result.get('status')} files_scanned={inventory_result.get('files_scanned', 0)} version_like={inventory_result.get('version_like_files', 0)}")
        for category, count in sorted(inventory_result.get("by_category", {}).items()):
            print(f"- {category}: {count}")
    for item in result.get("findings", []):
        path = f"{item.get('path')}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Validate contracts, registries, and fixture expectations")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fixtures", action="store_true", help="Validate version/deprecation fixtures")
    parser.add_argument("--inventory", action="store_true", help="Inventory version and lifecycle surfaces")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    result = validate_all(repo_root, include_fixtures=args.fixtures or args.strict, include_inventory=args.inventory)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if result["status"] != "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
