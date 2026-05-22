#!/usr/bin/env python3
"""Validate Dominium artifact identity contracts and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


ARTIFACT_DIR_REL = Path("contracts/artifact")
IDENTITY_CONTRACT_REL = ARTIFACT_DIR_REL / "artifact_identity.contract.toml"
MANIFEST_SCHEMA_REL = ARTIFACT_DIR_REL / "artifact_manifest.schema.json"
KIND_REGISTRY_REL = ARTIFACT_DIR_REL / "artifact_kind.registry.json"
HASH_POLICY_REL = ARTIFACT_DIR_REL / "artifact_hash_policy.contract.toml"
COMPAT_POLICY_REL = ARTIFACT_DIR_REL / "artifact_compatibility.contract.toml"
TRUST_POLICY_REL = ARTIFACT_DIR_REL / "artifact_trust_policy.contract.toml"
REF_SCHEMA_REL = ARTIFACT_DIR_REL / "artifact_ref.schema.json"
LIFECYCLE_REGISTRY_REL = ARTIFACT_DIR_REL / "artifact_lifecycle.registry.json"
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
EVIDENCE_SCHEMA_REL = Path("contracts/evidence/evidence_packet.schema.json")
FIXTURE_DIR_REL = Path("tests/contract/artifact_identity/fixtures")

JSON_RELS = [
    MANIFEST_SCHEMA_REL,
    KIND_REGISTRY_REL,
    REF_SCHEMA_REL,
    LIFECYCLE_REGISTRY_REL,
]
TOML_RELS = [
    IDENTITY_CONTRACT_REL,
    HASH_POLICY_REL,
    COMPAT_POLICY_REL,
    TRUST_POLICY_REL,
]

ARTIFACT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*(\.[a-z0-9][a-z0-9_.-]*)*$")
FORBIDDEN_FILENAME_SUFFIXES = (".json", ".toml", ".yaml", ".yml", ".manifest")
STABLE_LIFECYCLE = {"locked", "published", "deprecated"}
GENERATED_LIFECYCLE = {"generated"}
HISTORICAL_LIFECYCLE = {"historical", "retired", "quarantined"}


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


def registry_ids(data: Dict[str, Any], key: str) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get("id")
    }


def read_kind_ids(repo_root: Path) -> Set[str]:
    return registry_ids(load_json(repo_root / KIND_REGISTRY_REL), "kinds")


def read_lifecycle_ids(repo_root: Path) -> Set[str]:
    return registry_ids(load_json(repo_root / LIFECYCLE_REGISTRY_REL), "states")


def read_trust_levels(repo_root: Path) -> Set[str]:
    data = load_json(repo_root / KIND_REGISTRY_REL)
    levels = data.get("trust_levels", [])
    return {str(level) for level in levels if isinstance(level, str)}


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
    expected_ids = {
        IDENTITY_CONTRACT_REL: "dominium.artifact.identity.v1",
        HASH_POLICY_REL: "dominium.artifact.hash_policy.v1",
        COMPAT_POLICY_REL: "dominium.artifact.compatibility.v1",
        TRUST_POLICY_REL: "dominium.artifact.trust_policy.v1",
    }
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
        if not isinstance(contract, dict) or contract.get("id") != expected_ids[rel]:
            findings.append(finding("error", "unexpected_contract_id", f"{rel.as_posix()} has unexpected or missing contract id"))
    return findings


def artifact_id_is_path_like(artifact_id: str) -> bool:
    lowered = artifact_id.lower()
    if "/" in artifact_id or "\\" in artifact_id:
        return True
    if lowered.endswith(FORBIDDEN_FILENAME_SUFFIXES):
        return True
    if ":" in artifact_id:
        return True
    return False


def validate_manifest(
    manifest: Dict[str, Any],
    rel_path: str,
    kind_ids: Set[str],
    lifecycle_ids: Set[str],
    trust_levels: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    artifact_id = manifest.get("artifact_id")
    kind = manifest.get("artifact_kind")
    schema_id = manifest.get("schema_id")
    schema_version = manifest.get("schema_version")
    artifact_version = manifest.get("artifact_version")
    owner = manifest.get("owner")
    stability = manifest.get("stability")
    lifecycle = manifest.get("lifecycle") or stability
    trust_level = manifest.get("trust_level")

    if not isinstance(artifact_id, str) or not artifact_id.strip():
        findings.append(finding("error", "artifact_missing_id", "artifact_id is required", rel_path))
    elif artifact_id_is_path_like(artifact_id):
        findings.append(finding("error", "artifact_path_as_id", f"artifact_id must not be a path or filename: {artifact_id}", rel_path))
    elif not ARTIFACT_ID_RE.match(artifact_id):
        findings.append(finding("error", "artifact_id_format", f"artifact_id should be a lowercase semantic ID: {artifact_id}", rel_path))

    if not isinstance(kind, str) or not kind:
        findings.append(finding("error", "artifact_missing_kind", "artifact_kind is required", rel_path))
    elif kind not in kind_ids:
        findings.append(finding("error", "artifact_unknown_kind", f"unknown artifact_kind: {kind}", rel_path))

    if not isinstance(schema_id, str) or not schema_id:
        findings.append(finding("error", "artifact_missing_schema_id", "schema_id is required", rel_path))
    elif artifact_id_is_path_like(schema_id):
        findings.append(finding("warning", "schema_id_path_like", f"schema_id should not be path identity: {schema_id}", rel_path))

    if not isinstance(schema_version, str) or not schema_version:
        findings.append(finding("error", "artifact_missing_schema_version", "schema_version is required", rel_path))
    if not isinstance(artifact_version, str) or not artifact_version:
        findings.append(finding("error", "artifact_missing_version", "artifact_version is required", rel_path))
    if not isinstance(owner, str) or not owner:
        findings.append(finding("error", "artifact_missing_owner", "owner is required", rel_path))
    if not isinstance(stability, str) or not stability:
        findings.append(finding("error", "artifact_missing_stability", "stability is required", rel_path))
    elif stability not in lifecycle_ids and stability != "internal":
        findings.append(finding("error", "artifact_unknown_stability", f"unknown stability/lifecycle: {stability}", rel_path))
    if isinstance(lifecycle, str) and lifecycle not in lifecycle_ids and lifecycle != "internal":
        findings.append(finding("error", "artifact_unknown_lifecycle", f"unknown lifecycle: {lifecycle}", rel_path))

    lifecycle_value = str(lifecycle) if lifecycle else ""
    if lifecycle_value in STABLE_LIFECYCLE:
        for field in ("content_hash", "hash_algorithm", "compatibility_policy", "migration_policy", "refusal_policy"):
            if field not in manifest or manifest.get(field) in ("", None):
                findings.append(finding("error", "stable_artifact_missing_policy", f"{field} is required for locked/published/deprecated artifacts", rel_path))

    if lifecycle_value in GENERATED_LIFECYCLE:
        if not manifest.get("generator"):
            findings.append(finding("error", "generated_missing_generator", "generated artifacts require generator", rel_path))
        if not manifest.get("source_surface") and not manifest.get("source_artifacts"):
            findings.append(finding("error", "generated_missing_source", "generated artifacts require source_surface or source_artifacts", rel_path))

    if trust_level is not None and trust_level not in trust_levels:
        findings.append(finding("error", "artifact_unknown_trust_level", f"unknown trust_level: {trust_level}", rel_path))

    if kind == "test_fixture" and not rel_path.replace("\\", "/").startswith("tests/"):
        findings.append(finding("error", "fixture_outside_tests", "test_fixture artifacts must live under tests", rel_path))

    if lifecycle_value not in HISTORICAL_LIFECYCLE and rel_path.replace("\\", "/").startswith("archive/"):
        findings.append(finding("warning", "active_artifact_under_archive", "archive artifacts should be historical, retired, quarantined, generated, or fixture", rel_path))

    return findings


def fixture_paths(repo_root: Path) -> Tuple[List[Path], List[Path]]:
    fixture_root = repo_root / FIXTURE_DIR_REL
    valid = sorted(fixture_root.glob("valid_*.manifest.json"))
    invalid = sorted(fixture_root.glob("invalid_*.manifest.json"))
    return valid, invalid


def validate_fixture_files(repo_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    kind_ids = read_kind_ids(repo_root)
    lifecycle_ids = read_lifecycle_ids(repo_root)
    trust_levels = read_trust_levels(repo_root)
    valid_paths, invalid_paths = fixture_paths(repo_root)
    results: List[Dict[str, Any]] = []

    for path in valid_paths:
        rel = path.relative_to(repo_root).as_posix()
        try:
            manifest = load_json(path)
            manifest_findings = validate_manifest(manifest, rel, kind_ids, lifecycle_ids, trust_levels)
        except Exception as exc:
            manifest_findings = [finding("error", "fixture_invalid_json", f"fixture does not parse: {exc}", rel)]
        errors = [item for item in manifest_findings if item["level"] == "error"]
        results.append({"path": rel, "expected": "valid", "errors": len(errors), "findings": manifest_findings})
        if errors:
            findings.append(finding("error", "valid_fixture_failed", f"valid fixture failed validation: {rel}", rel))

    for path in invalid_paths:
        rel = path.relative_to(repo_root).as_posix()
        try:
            manifest = load_json(path)
            manifest_findings = validate_manifest(manifest, rel, kind_ids, lifecycle_ids, trust_levels)
        except Exception as exc:
            manifest_findings = [finding("error", "fixture_invalid_json", f"fixture does not parse: {exc}", rel)]
        errors = [item for item in manifest_findings if item["level"] == "error"]
        results.append({"path": rel, "expected": "invalid", "errors": len(errors), "findings": manifest_findings})
        if not errors:
            findings.append(finding("error", "invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))

    if not valid_paths or not invalid_paths:
        findings.append(finding("error", "fixture_set_incomplete", "artifact identity fixture set must include valid and invalid manifests"))

    summary = {
        "status": "pass" if not findings else "fail",
        "valid_fixtures": len(valid_paths),
        "invalid_fixtures": len(invalid_paths),
        "fixtures": results,
    }
    return findings, summary


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
    manifest_like = [
        path for path in files
        if path.endswith(".manifest.json")
        or path.endswith("pack_manifest.json")
        or path.endswith("pack.json")
        or path.endswith(".schema.json")
        or path.endswith(".registry.json")
        or path.endswith(".schema")
    ]
    categories = {
        "manifest_backed_candidates": 0,
        "likely_artifact_no_manifest": 0,
        "generated_evidence": 0,
        "fixture": 0,
        "historical_archive": 0,
        "schema_or_registry": 0,
        "deferred": 0,
    }
    examples: Dict[str, List[str]] = {key: [] for key in categories}
    for path in manifest_like:
        normalized = path.replace("\\", "/")
        if "pack_manifest.json" in normalized or normalized.endswith(".manifest.json") or normalized.endswith("pack.json"):
            key = "manifest_backed_candidates"
        elif normalized.startswith("archive/"):
            key = "historical_archive"
        elif normalized.startswith(".aide/reports/") or normalized.startswith("archive/generated/"):
            key = "generated_evidence"
        elif normalized.startswith("tests/"):
            key = "fixture"
        elif normalized.startswith("contracts/") and (".schema" in normalized or ".registry." in normalized):
            key = "schema_or_registry"
        else:
            key = "deferred"
        categories[key] += 1
        if len(examples[key]) < 8:
            examples[key].append(normalized)

    return {
        "files_scanned": len(files),
        "artifact_like_files": len(manifest_like),
        "categories": categories,
        "examples": examples,
        "status": "warning",
        "note": "Inventory is descriptive only; existing artifacts are not migrated by ARTIFACT-IDENTITY-LAW-01.",
    }


def validate_diagnostic_codes(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / DIAGNOSTIC_REGISTRY_REL
    if not path.exists():
        return [finding("warning", "diagnostics_registry_missing", "diagnostics registry is missing; artifact diagnostics not checked")]
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "diagnostics_registry_invalid", f"diagnostics registry does not parse: {exc}")]
    codes = {
        str(item.get("code"))
        for item in as_list(data.get("codes"))
        if isinstance(item, dict) and item.get("code")
    }
    required = {
        "DOM-ARTIFACT-MISSING-ID",
        "DOM-ARTIFACT-INVALID-KIND",
        "DOM-ARTIFACT-MISSING-SCHEMA",
        "DOM-ARTIFACT-PATH-AS-ID",
        "DOM-ARTIFACT-HASH-MISMATCH",
        "DOM-ARTIFACT-UNSUPPORTED-SCHEMA",
        "DOM-ARTIFACT-MIGRATION-REQUIRED",
        "DOM-ARTIFACT-TRUST-INSUFFICIENT",
    }
    missing = sorted(required - codes)
    if missing:
        return [finding("warning", "artifact_diagnostics_missing", f"artifact diagnostic codes not registered: {', '.join(missing)}")]
    return []


def validate_evidence_schema(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / EVIDENCE_SCHEMA_REL
    if not path.exists():
        return []
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "evidence_schema_invalid", f"evidence packet schema does not parse: {exc}")]
    properties = data.get("properties", {})
    if not isinstance(properties, dict) or "artifact_refs" not in properties:
        return [finding("warning", "evidence_schema_missing_artifact_refs", "evidence packet schema does not expose artifact_refs")]
    return []


def validate_all(repo_root: Path, include_fixtures: bool) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    fixture_summary = {"status": "not_run", "valid_fixtures": 0, "invalid_fixtures": 0}
    if not any(item["level"] == "error" for item in findings):
        try:
            kind_ids = read_kind_ids(repo_root)
            lifecycle_ids = read_lifecycle_ids(repo_root)
            trust_levels = read_trust_levels(repo_root)
        except Exception as exc:
            findings.append(finding("error", "registry_load_failed", f"could not load artifact registries: {exc}"))
        else:
            if len(kind_ids) < 23:
                findings.append(finding("error", "artifact_kind_count_low", "artifact kind registry is missing required kinds"))
            if len(lifecycle_ids) < 11:
                findings.append(finding("error", "artifact_lifecycle_count_low", "artifact lifecycle registry is missing required states"))
            if not trust_levels:
                findings.append(finding("error", "trust_levels_missing", "trust levels are missing from artifact kind registry"))
            if include_fixtures:
                fixture_findings, fixture_summary = validate_fixture_files(repo_root)
                findings.extend(fixture_findings)
    findings.extend(validate_diagnostic_codes(repo_root))
    findings.extend(validate_evidence_schema(repo_root))
    summary = {
        "kind_count": len(read_kind_ids(repo_root)) if (repo_root / KIND_REGISTRY_REL).exists() else 0,
        "lifecycle_count": len(read_lifecycle_ids(repo_root)) if (repo_root / LIFECYCLE_REGISTRY_REL).exists() else 0,
        "fixtures": fixture_summary,
    }
    return findings, summary


def print_list(repo_root: Path) -> None:
    kinds = sorted(read_kind_ids(repo_root))
    lifecycles = sorted(read_lifecycle_ids(repo_root))
    print("artifact kinds:")
    for item in kinds:
        print(f"- {item}")
    print("artifact lifecycle states:")
    for item in lifecycles:
        print(f"- {item}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero on errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--fixtures", action="store_true", help="Validate fixture manifests.")
    parser.add_argument("--inventory", action="store_true", help="Run descriptive artifact inventory.")
    parser.add_argument("--list", action="store_true", help="List artifact kinds and lifecycle states.")
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
        "validator": "check_artifact_identity",
        "status": status,
        "artifact_kinds_registered": summary["kind_count"],
        "lifecycle_states_registered": summary["lifecycle_count"],
        "fixtures": summary["fixtures"],
        "inventory": inv,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "findings": findings,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"artifact identity: {status}")
        print(f"artifact_kinds: {summary['kind_count']}")
        print(f"lifecycle_states: {summary['lifecycle_count']}")
        print(f"errors: {len(errors)}")
        print(f"warnings: {len(warnings)}")
        if args.fixtures:
            print(f"fixtures: {summary['fixtures']['status']}")
        if args.inventory:
            print(f"inventory: {inv['status']} artifact_like_files={inv['artifact_like_files']} files_scanned={inv['files_scanned']}")
        for item in findings[:80]:
            location = f" {item['path']}:" if item.get("path") else ""
            print(f"{item['level'].upper()} {item['code']}:{location} {item['message']}")

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
