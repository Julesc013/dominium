#!/usr/bin/env python3
"""Validate Dominium public surface registry contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


SCHEMA_REL = Path("contracts/public_surface/surface.schema.json")
KIND_REL = Path("contracts/public_surface/surface_kind.registry.json")
STABILITY_REL = Path("contracts/public_surface/surface_stability.registry.json")
CONTRACT_REL = Path("contracts/public_surface/public_surface.contract.toml")
ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+\.v[0-9]+$")
STABLE_CLASSES = {
    "frozen_abi",
    "stable_api",
    "stable_data_contract",
    "stable_command_contract",
    "stable_protocol",
}
FORBIDDEN_PREFIXES = (".dominium.local/", ".aide.local/")


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out = []
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


def _parse_value(raw: str):
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


def _minimal_toml_load(text: str) -> dict:
    root: dict = {}
    current = root
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            if section != "surface":
                raise ValueError(f"unsupported array table at line {lineno}: {section}")
            current = {}
            root.setdefault("surface", []).append(current)
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


def load_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm_path(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def finding(level: str, code: str, message: str, surface_id: str | None = None) -> dict:
    item = {"level": level, "code": code, "message": message}
    if surface_id:
        item["surface_id"] = surface_id
    return item


def registry_ids(data: dict, key: str) -> set[str]:
    values = data.get(key)
    if not isinstance(values, list):
        return set()
    return {str(item.get("id")) for item in values if isinstance(item, dict) and item.get("id")}


def kind_allowed_stability(data: dict) -> dict[str, set[str]]:
    values = data.get("kinds")
    if not isinstance(values, list):
        return {}
    allowed: dict[str, set[str]] = {}
    for item in values:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        raw = item.get("allowed_stability", [])
        allowed[str(item["id"])] = {str(value) for value in raw if isinstance(value, str)}
    return allowed


def validate_registry_shapes(kind_registry: dict, stability_registry: dict, schema: dict) -> list[dict]:
    findings: list[dict] = []
    if not isinstance(kind_registry.get("kinds"), list):
        findings.append(finding("error", "kind_registry_shape", "kind registry must contain a kinds array"))
    if not isinstance(stability_registry.get("classes"), list):
        findings.append(finding("error", "stability_registry_shape", "stability registry must contain a classes array"))
    if schema.get("type") != "object":
        findings.append(finding("error", "schema_shape", "surface schema must describe an object root"))
    return findings


def validate_surface(
    surface: dict,
    repo_root: Path,
    kind_ids: set[str],
    stability_ids: set[str],
    allowed_by_kind: dict[str, set[str]],
    check_paths: bool,
    seen: set[str],
) -> list[dict]:
    findings: list[dict] = []
    required = ["id", "kind", "path", "owner", "stability", "proof", "compatibility", "replacement_policy", "notes"]
    surface_id = str(surface.get("id", "<missing-id>"))
    for key in required:
        if key not in surface or surface.get(key) in ("", None):
            findings.append(finding("error", f"missing_{key}", f"surface is missing required field {key}", surface_id))

    if surface_id in seen:
        findings.append(finding("error", "duplicate_id", "surface id is duplicated", surface_id))
    seen.add(surface_id)

    if not ID_RE.match(surface_id):
        findings.append(finding("error", "invalid_id", "surface id must be a dotted domino/dominium id ending in .vN", surface_id))

    kind = str(surface.get("kind", ""))
    stability = str(surface.get("stability", ""))
    if kind not in kind_ids:
        findings.append(finding("error", "invalid_kind", f"unknown surface kind: {kind}", surface_id))
    if stability not in stability_ids:
        findings.append(finding("error", "invalid_stability", f"unknown stability class: {stability}", surface_id))
    if kind in allowed_by_kind and stability in stability_ids and stability not in allowed_by_kind[kind]:
        findings.append(finding("error", "stability_not_allowed_for_kind", f"{stability} is not allowed for kind {kind}", surface_id))

    path_value = norm_path(str(surface.get("path", "")))
    if not path_value:
        findings.append(finding("error", "empty_path", "surface path must not be empty", surface_id))
    if Path(path_value).is_absolute() or ":" in path_value:
        findings.append(finding("error", "absolute_path", "surface path must be repository-relative", surface_id))
    if path_value.startswith(FORBIDDEN_PREFIXES):
        findings.append(finding("error", "local_output_path", "surface path must not live under local/generated private roots", surface_id))

    proof = surface.get("proof")
    if not isinstance(proof, list):
        findings.append(finding("error", "proof_not_array", "proof must be an array", surface_id))
        proof = []
    if stability in STABLE_CLASSES and not proof:
        findings.append(finding("error", "stable_without_proof", "stable/frozen surfaces require non-empty proof", surface_id))

    compatibility = str(surface.get("compatibility", ""))
    if stability in STABLE_CLASSES and compatibility in ("", "not_yet_stable", "none", "internal_no_public_promise"):
        findings.append(finding("error", "stable_without_compatibility", "stable/frozen surfaces require a compatibility policy", surface_id))

    if stability == "generated":
        if not surface.get("source") or not surface.get("generator"):
            findings.append(finding("error", "generated_without_source", "generated surfaces require source and generator", surface_id))

    if stability == "retired":
        if not surface.get("retirement_reason"):
            findings.append(finding("error", "retired_without_reason", "retired surfaces require retirement_reason", surface_id))
        if not surface.get("replacement_policy"):
            findings.append(finding("error", "retired_without_replacement", "retired surfaces require replacement_policy", surface_id))

    if stability == "fixture" or kind == "test_fixture":
        if not (path_value.startswith("tests/") or path_value.startswith("tools/validators/suite/fixtures/")):
            findings.append(finding("error", "fixture_outside_tests", "fixture surfaces must live under tests or validator fixtures", surface_id))

    if stability == "historical":
        if not (path_value.startswith("archive/") or path_value.startswith("docs/")):
            findings.append(finding("error", "historical_active_path", "historical surfaces must live under archive/docs or be reclassified", surface_id))

    if path_value.startswith("archive/") and stability not in {"historical", "retired", "generated"} and kind != "archive_record":
        findings.append(finding("error", "active_archive_surface", "archive paths must not be active public surfaces", surface_id))

    path_exists = (repo_root / path_value).exists()
    if check_paths and not path_exists and stability not in {"retired", "historical"} and not surface.get("placeholder"):
        findings.append(finding("error", "path_missing", f"surface path does not exist: {path_value}", surface_id))

    return findings


def validate_contract_data(
    data: dict,
    repo_root: Path,
    kind_ids: set[str],
    stability_ids: set[str],
    allowed_by_kind: dict[str, set[str]],
    check_paths: bool,
) -> tuple[list[dict], dict]:
    findings: list[dict] = []
    contract = data.get("contract")
    policy = data.get("policy")
    surfaces = data.get("surface")
    if not isinstance(contract, dict):
        findings.append(finding("error", "missing_contract", "contract table is required"))
    if not isinstance(policy, dict):
        findings.append(finding("error", "missing_policy", "policy table is required"))
    if not isinstance(surfaces, list):
        findings.append(finding("error", "missing_surfaces", "surface array is required"))
        surfaces = []
    if isinstance(contract, dict):
        for key in ("id", "status", "owner", "purpose"):
            if not contract.get(key):
                findings.append(finding("error", f"contract_missing_{key}", f"contract table missing {key}"))
    if isinstance(policy, dict):
        for key in ("paths_are_identity", "implementation_is_contract", "generated_output_is_source_truth", "default_stability", "stable_requires_proof", "stable_requires_compatibility_policy"):
            if key not in policy:
                findings.append(finding("error", f"policy_missing_{key}", f"policy table missing {key}"))
        for key in ("paths_are_identity", "implementation_is_contract", "generated_output_is_source_truth"):
            if policy.get(key) is not False:
                findings.append(finding("error", f"policy_{key}", f"policy {key} must be false"))
        if policy.get("stable_requires_proof") is not True:
            findings.append(finding("error", "policy_stable_requires_proof", "stable_requires_proof must be true"))

    seen: set[str] = set()
    for surface in surfaces:
        if isinstance(surface, dict):
            findings.extend(validate_surface(surface, repo_root, kind_ids, stability_ids, allowed_by_kind, check_paths, seen))
        else:
            findings.append(finding("error", "surface_not_table", "surface entries must be tables"))

    counts = {
        "surface_count": len(surfaces),
        "stable_count": sum(1 for item in surfaces if isinstance(item, dict) and item.get("stability") in STABLE_CLASSES),
        "by_stability": {},
        "by_kind": {},
    }
    for surface in surfaces:
        if not isinstance(surface, dict):
            continue
        stability = str(surface.get("stability", ""))
        kind = str(surface.get("kind", ""))
        counts["by_stability"][stability] = counts["by_stability"].get(stability, 0) + 1
        counts["by_kind"][kind] = counts["by_kind"].get(kind, 0) + 1
    return findings, counts


def run_fixture_checks(
    fixture_dir: Path,
    repo_root: Path,
    kind_ids: set[str],
    stability_ids: set[str],
    allowed_by_kind: dict[str, set[str]],
) -> list[dict]:
    findings: list[dict] = []
    if not fixture_dir.exists():
        return [finding("error", "fixture_dir_missing", f"fixture directory missing: {fixture_dir}")]
    for fixture in sorted(fixture_dir.glob("*.toml")):
        expected_valid = fixture.name.startswith("valid_")
        expected_invalid = fixture.name.startswith("invalid_")
        if not expected_valid and not expected_invalid:
            findings.append(finding("warning", "fixture_name_unclassified", f"fixture name does not declare valid/invalid expectation: {fixture.name}"))
            continue
        try:
            data = load_toml(fixture)
            fixture_findings, _ = validate_contract_data(data, repo_root, kind_ids, stability_ids, allowed_by_kind, check_paths=False)
            is_valid = not any(item["level"] == "error" for item in fixture_findings)
        except Exception as exc:  # noqa: BLE001 - report parser failure as fixture result
            fixture_findings = [finding("error", "fixture_parse_error", f"{fixture.name}: {exc}")]
            is_valid = False
        if expected_valid and not is_valid:
            findings.append(finding("error", "fixture_expected_valid_failed", f"{fixture.name} should be valid"))
            findings.extend(fixture_findings)
        if expected_invalid and is_valid:
            findings.append(finding("error", "fixture_expected_invalid_passed", f"{fixture.name} should be invalid"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--strict", action="store_true", help="fail on registry violations")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    parser.add_argument("--list", action="store_true", help="list registered surfaces")
    parser.add_argument("--check-paths", action="store_true", help="check non-retired surface paths even outside strict mode")
    parser.add_argument("--fixture-dir", help="run valid_/invalid_ fixture checks")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    schema_path = repo_root / SCHEMA_REL
    kind_path = repo_root / KIND_REL
    stability_path = repo_root / STABILITY_REL
    contract_path = repo_root / CONTRACT_REL
    findings: list[dict] = []

    try:
        schema = load_json(schema_path)
        kind_registry = load_json(kind_path)
        stability_registry = load_json(stability_path)
    except Exception as exc:  # noqa: BLE001
        result = {
            "schema_version": "dominium.public_surface.validation_result.v1",
            "status": "FAIL",
            "error": str(exc),
            "findings": [finding("error", "registry_read_failed", str(exc))],
        }
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"public surface validation: FAIL\n{exc}")
        return 1

    findings.extend(validate_registry_shapes(kind_registry, stability_registry, schema))
    kind_ids = registry_ids(kind_registry, "kinds")
    stability_ids = registry_ids(stability_registry, "classes")
    allowed_by_kind = kind_allowed_stability(kind_registry)

    try:
        contract_data = load_toml(contract_path)
        contract_findings, counts = validate_contract_data(
            contract_data,
            repo_root,
            kind_ids,
            stability_ids,
            allowed_by_kind,
            check_paths=args.check_paths or args.strict,
        )
        findings.extend(contract_findings)
    except Exception as exc:  # noqa: BLE001
        counts = {"surface_count": 0, "stable_count": 0, "by_stability": {}, "by_kind": {}}
        findings.append(finding("error", "contract_read_failed", str(exc)))
        contract_data = {}

    if args.fixture_dir:
        findings.extend(run_fixture_checks(repo_root / args.fixture_dir, repo_root, kind_ids, stability_ids, allowed_by_kind))

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    status = "PASS" if not errors else "FAIL"
    result = {
        "schema_version": "dominium.public_surface.validation_result.v1",
        "status": status,
        "strict": bool(args.strict),
        "surface_count": counts["surface_count"],
        "stable_count": counts["stable_count"],
        "by_stability": counts["by_stability"],
        "by_kind": counts["by_kind"],
        "kind_count": len(kind_ids),
        "stability_class_count": len(stability_ids),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }

    if args.list and isinstance(contract_data.get("surface"), list):
        for surface in contract_data["surface"]:
            print(f"{surface.get('id')} [{surface.get('kind')}] {surface.get('stability')} -> {surface.get('path')}")

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif not args.list:
        print(f"public surface validation: {status}")
        print(f"surfaces: {counts['surface_count']} stable: {counts['stable_count']} kinds: {len(kind_ids)} stability_classes: {len(stability_ids)}")
        for item in findings:
            print(f"{item['level'].upper()} {item['code']}: {item['message']}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
