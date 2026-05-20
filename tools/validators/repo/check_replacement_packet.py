#!/usr/bin/env python3
"""Validate Dominium replacement protocol contracts and packet fixtures."""

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
except ImportError:  # pragma: no cover - Python 3.8 fallback
    tomllib = None


REPLACEMENT_CONTRACT_REL = Path("contracts/replacement/replacement.contract.toml")
REPLACEMENT_PACKET_SCHEMA_REL = Path("contracts/replacement/replacement_packet.schema.json")
REPLACEMENT_KIND_REGISTRY_REL = Path("contracts/replacement/replacement_kind.registry.json")
REPLACEMENT_STATUS_REGISTRY_REL = Path("contracts/replacement/replacement_status.registry.json")
REPLACEMENT_IMPACT_SCHEMA_REL = Path("contracts/replacement/replacement_impact.schema.json")
REPLACEMENT_PROOF_SCHEMA_REL = Path("contracts/replacement/replacement_proof.schema.json")
ROLLBACK_POLICY_REL = Path("contracts/replacement/rollback_policy.contract.toml")
CONFORMANCE_POLICY_REL = Path("contracts/replacement/conformance_policy.contract.toml")
MIGRATION_REFUSAL_POLICY_REL = Path("contracts/replacement/migration_refusal_policy.contract.toml")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostics/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
ARTIFACT_KIND_REGISTRY_REL = Path("contracts/artifact/artifact_kind.registry.json")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
MODULE_KIND_REGISTRY_REL = Path("contracts/module/module_kind.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/replacement/fixtures")

JSON_RELS = [
    REPLACEMENT_PACKET_SCHEMA_REL,
    REPLACEMENT_KIND_REGISTRY_REL,
    REPLACEMENT_STATUS_REGISTRY_REL,
    REPLACEMENT_IMPACT_SCHEMA_REL,
    REPLACEMENT_PROOF_SCHEMA_REL,
]
TOML_RELS = [
    REPLACEMENT_CONTRACT_REL,
    ROLLBACK_POLICY_REL,
    CONFORMANCE_POLICY_REL,
    MIGRATION_REFUSAL_POLICY_REL,
]
EXPECTED_CONTRACT_IDS = {
    REPLACEMENT_CONTRACT_REL: "dominium.replacement.protocol.v1",
    ROLLBACK_POLICY_REL: "dominium.replacement.rollback_policy.v1",
    CONFORMANCE_POLICY_REL: "dominium.replacement.conformance_policy.v1",
    MIGRATION_REFUSAL_POLICY_REL: "dominium.replacement.migration_refusal_policy.v1",
}

REPLACEMENT_ID_RE = re.compile(r"^(domino|dominium)\.replacement(\.[a-z0-9][a-z0-9_-]*)+$")
PATHLIKE_RE = re.compile(r"[/\\]|\.\.(?:/|\\)|\.(json|toml|py|c|cpp|h|hpp)$")
PUBLIC_REPLACEMENT_KINDS = {
    "public_api",
    "abi_surface",
    "schema",
    "protocol",
    "registry",
    "artifact_format",
    "provider",
    "module",
    "workbench_workspace",
    "app_composition",
    "package_format",
    "save_format",
    "replay_format",
    "command_surface",
    "dependency_boundary",
    "directory_restructure",
}
ROLLBACK_OPTIONAL_STATUSES = {"historical", "rejected", "deferred"}
BREAKING_COMPATIBILITY_VALUES = {"breaking", "requires_migration"}
STABLE_ARTIFACT_STATES = {"stable", "locked", "published"}


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


def registry_ids(data: Dict[str, Any], key: str, id_key: str = "id") -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def string_values(data: Dict[str, Any], key: str) -> Set[str]:
    return {str(item) for item in as_list(data.get(key)) if isinstance(item, str)}


def load_optional_json(path: Path, key: str, id_key: str) -> Set[str]:
    if not path.exists():
        return set()
    try:
        return registry_ids(load_json(path), key, id_key)
    except Exception:
        return set()


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


def read_provider_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        data = load_json(path)
    except Exception:
        return set()
    return {
        str(item.get("provider_id"))
        for item in as_list(data.get("providers"))
        if isinstance(item, dict) and item.get("provider_id")
    }


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


def read_replacement_vocab(repo_root: Path) -> Tuple[Set[str], Set[str], Set[str], Set[str], Set[str], Set[str]]:
    kinds = load_json(repo_root / REPLACEMENT_KIND_REGISTRY_REL)
    statuses = load_json(repo_root / REPLACEMENT_STATUS_REGISTRY_REL)
    return (
        registry_ids(kinds, "kinds"),
        string_values(kinds, "compatibility_impact_values"),
        string_values(kinds, "abi_impact_values"),
        string_values(kinds, "dependency_impact_values"),
        string_values(kinds, "approval_status_values"),
        registry_ids(statuses, "statuses"),
    )


def validate_replacement_registries(repo_root: Path) -> Tuple[List[Dict[str, Any]], int, int]:
    findings: List[Dict[str, Any]] = []
    try:
        kinds, _compat, _abi, _dep, _approval, statuses = read_replacement_vocab(repo_root)
    except Exception as exc:
        return [finding("error", "replacement_registry_unreadable", f"replacement registries cannot be read: {exc}")], 0, 0

    required_kinds = {
        "private_implementation",
        "public_api",
        "abi_surface",
        "schema",
        "protocol",
        "registry",
        "artifact_format",
        "provider",
        "module",
        "workbench_workspace",
        "app_composition",
        "package_format",
        "save_format",
        "replay_format",
        "command_surface",
        "dependency_boundary",
        "directory_restructure",
        "tooling",
        "generated_surface",
    }
    required_statuses = {"draft", "planned", "approved", "applied", "proven", "rejected", "rolled_back", "superseded", "deferred", "historical"}
    missing_kinds = sorted(required_kinds - kinds)
    missing_statuses = sorted(required_statuses - statuses)
    if missing_kinds:
        findings.append(finding("error", "replacement_kinds_missing", f"required replacement kinds missing: {', '.join(missing_kinds)}"))
    if missing_statuses:
        findings.append(finding("error", "replacement_statuses_missing", f"required replacement statuses missing: {', '.join(missing_statuses)}"))
    return findings, len(kinds), len(statuses)


def has_proof(packet: Dict[str, Any]) -> bool:
    for key in ["conformance_tests", "compatibility_tests", "replay_or_determinism_tests"]:
        if as_list(packet.get(key)):
            return True
    proof = packet.get("proof")
    if isinstance(proof, dict) and (as_list(proof.get("commands")) or as_list(proof.get("evidence_refs"))):
        return True
    return False


def rollback_present(packet: Dict[str, Any]) -> bool:
    rollback = packet.get("rollback_plan")
    if not isinstance(rollback, dict):
        return False
    return bool(rollback.get("action") and rollback.get("summary") and as_list(rollback.get("steps")) and as_list(rollback.get("verification")))


def surface_id(surface: Any) -> str:
    if isinstance(surface, dict):
        return str(surface.get("id") or "")
    return ""


def migration_is_explicit(packet: Dict[str, Any]) -> bool:
    policy = packet.get("migration_policy")
    if not isinstance(policy, dict):
        return False
    mode = str(policy.get("mode") or policy.get("policy") or "")
    return mode not in {"", "none", "deferred"}


def refusal_is_explicit(packet: Dict[str, Any]) -> bool:
    policy = packet.get("refusal_policy")
    if not isinstance(policy, dict):
        return False
    return bool(policy.get("required") is True and (as_list(policy.get("codes")) or policy.get("code")))


def diagnostic_values(packet: Dict[str, Any]) -> List[str]:
    values = [str(item) for item in as_list(packet.get("diagnostic_codes")) if item]
    for policy_key in ["migration_policy", "refusal_policy"]:
        policy = packet.get(policy_key)
        if isinstance(policy, dict):
            values.extend(str(item) for item in as_list(policy.get("diagnostic_codes")) if item)
    return values


def refusal_values(packet: Dict[str, Any]) -> List[str]:
    values: List[str] = []
    policy = packet.get("refusal_policy")
    if isinstance(policy, dict):
        values.extend(str(item) for item in as_list(policy.get("codes")) if item)
        if policy.get("code"):
            values.append(str(policy.get("code")))
    return values


def stable_artifact_break(packet: Dict[str, Any]) -> bool:
    if str(packet.get("compatibility_impact") or "") in BREAKING_COMPATIBILITY_VALUES:
        for artifact in as_list(packet.get("artifacts_affected")):
            if not isinstance(artifact, dict):
                continue
            stability = str(artifact.get("stability") or "")
            compatibility = str(artifact.get("compatibility") or "")
            if stability in STABLE_ARTIFACT_STATES or compatibility in BREAKING_COMPATIBILITY_VALUES:
                return True
    return bool(packet.get("stable_artifact_break") is True)


def validate_replacement_packet(
    packet: Dict[str, Any],
    *,
    path: str,
    kinds: Set[str],
    statuses: Set[str],
    compatibility_values: Set[str],
    abi_values: Set[str],
    dependency_values: Set[str],
    approval_values: Set[str],
    public_ids: Set[str],
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
    artifact_kinds: Set[str],
    provider_ids: Set[str],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    replacement_id = str(packet.get("replacement_id") or "")
    if not replacement_id:
        findings.append(finding("error", "replacement_missing_id", "replacement packet is missing replacement_id", path))
    elif not REPLACEMENT_ID_RE.match(replacement_id):
        findings.append(finding("error", "replacement_bad_id", f"replacement_id is not a lowercase dotted id: {replacement_id}", path))
    elif PATHLIKE_RE.search(replacement_id):
        findings.append(finding("error", "replacement_path_as_id", f"replacement_id must not be path-like: {replacement_id}", path))

    kind = str(packet.get("replacement_kind") or "")
    if kind not in kinds:
        findings.append(finding("error", "replacement_unknown_kind", f"unknown replacement_kind: {kind}", path))

    status = str(packet.get("status") or "")
    if status not in statuses:
        findings.append(finding("error", "replacement_unknown_status", f"unknown replacement status: {status}", path))

    for key in ["owner", "summary"]:
        if packet.get(key) in (None, "", []):
            findings.append(finding("error", "replacement_missing_required_field", f"replacement packet missing {key}", path))

    old_surface = surface_id(packet.get("old_surface"))
    new_surface = surface_id(packet.get("new_surface"))
    if not old_surface:
        findings.append(finding("error", "replacement_missing_old_surface", "replacement packet must name old_surface.id", path))
    if not new_surface:
        findings.append(finding("error", "replacement_missing_new_surface", "replacement packet must name new_surface.id", path))
    for surface_key in ["old_surface", "new_surface"]:
        surface = packet.get(surface_key)
        if isinstance(surface, dict) and surface.get("path_is_identity") is True:
            findings.append(finding("error", "surface_path_as_identity", f"{surface_key} must not make path authoritative", path))

    for impl_key in ["old_implementation", "new_implementation"]:
        implementation = packet.get(impl_key)
        if isinstance(implementation, dict) and implementation.get("identity_authority") is True:
            findings.append(finding("error", "implementation_path_as_identity", f"{impl_key} must not be identity authority", path))

    if str(packet.get("compatibility_impact") or "") not in compatibility_values:
        findings.append(finding("error", "replacement_unknown_compatibility", f"unknown compatibility_impact: {packet.get('compatibility_impact')}", path))
    if packet.get("abi_impact") is not None and str(packet.get("abi_impact")) not in abi_values:
        findings.append(finding("error", "replacement_unknown_abi_impact", f"unknown abi_impact: {packet.get('abi_impact')}", path))
    if packet.get("dependency_impact") is not None and str(packet.get("dependency_impact")) not in dependency_values:
        findings.append(finding("error", "replacement_unknown_dependency_impact", f"unknown dependency_impact: {packet.get('dependency_impact')}", path))
    if packet.get("approval_status") is not None and str(packet.get("approval_status")) not in approval_values:
        findings.append(finding("error", "replacement_unknown_approval", f"unknown approval_status: {packet.get('approval_status')}", path))

    if kind in PUBLIC_REPLACEMENT_KINDS and not has_proof(packet):
        findings.append(finding("error", "replacement_missing_proof", "public or compatibility-affecting replacement requires proof", path))

    if status not in ROLLBACK_OPTIONAL_STATUSES and not rollback_present(packet):
        findings.append(finding("error", "replacement_missing_rollback", "active replacement requires rollback_plan with action, steps, and verification", path))

    if stable_artifact_break(packet) and not (migration_is_explicit(packet) or refusal_is_explicit(packet)):
        findings.append(finding("error", "stable_artifact_break_without_migration", "stable artifact break requires explicit migration or refusal policy", path))

    if public_ids:
        for surface in [str(item) for item in as_list(packet.get("public_surfaces_affected")) if item]:
            if surface not in public_ids:
                findings.append(finding("error", "replacement_unknown_public_surface", f"unknown public surface: {surface}", path))

    if diagnostic_codes:
        for diagnostic in diagnostic_values(packet):
            if diagnostic not in diagnostic_codes:
                findings.append(finding("error", "replacement_unknown_diagnostic", f"unknown diagnostic code: {diagnostic}", path))

    if refusal_codes:
        for refusal in refusal_values(packet):
            if refusal not in refusal_codes:
                findings.append(finding("error", "replacement_unknown_refusal", f"unknown refusal code: {refusal}", path))

    if artifact_kinds:
        for artifact in as_list(packet.get("artifacts_affected")):
            if isinstance(artifact, dict) and artifact.get("artifact_kind") and artifact.get("artifact_kind") not in artifact_kinds:
                findings.append(finding("error", "replacement_unknown_artifact_kind", f"unknown artifact kind: {artifact.get('artifact_kind')}", path))

    if provider_ids:
        for provider_id in [str(item) for item in as_list(packet.get("providers_affected")) if item]:
            if provider_id not in provider_ids:
                findings.append(finding("error", "replacement_unknown_provider", f"unknown provider: {provider_id}", path))

    return findings


def fixture_expectations() -> Dict[str, bool]:
    return {
        "valid_private_implementation_replacement.json": True,
        "valid_provider_replacement.json": True,
        "valid_schema_replacement_with_migration.json": True,
        "valid_module_replacement.json": True,
        "invalid_replacement_missing_old_surface.json": False,
        "invalid_public_replacement_without_proof.json": False,
        "invalid_replacement_missing_rollback.json": False,
        "invalid_stable_artifact_break_without_migration.json": False,
    }


def fixture_context(repo_root: Path) -> Tuple[Set[str], Set[str], Set[str], Set[str], Set[str], Set[str], Set[str], Set[str], Set[str], Set[str], Set[str]]:
    kinds, compatibility, abi, dependency, approval, statuses = read_replacement_vocab(repo_root)
    public_ids = public_surface_ids(repo_root / PUBLIC_SURFACE_REGISTRY_REL)
    diagnostic_codes = load_optional_json(repo_root / DIAGNOSTIC_REGISTRY_REL, "codes", "code")
    refusal_codes = load_optional_json(repo_root / REFUSAL_REGISTRY_REL, "codes", "code")
    artifact_kinds = load_optional_json(repo_root / ARTIFACT_KIND_REGISTRY_REL, "kinds", "id")
    provider_ids = read_provider_ids(repo_root / PROVIDER_REGISTRY_REL)
    return kinds, compatibility, abi, dependency, approval, statuses, public_ids, diagnostic_codes, refusal_codes, artifact_kinds, provider_ids


def run_fixture_checks(repo_root: Path, fixture_dir: Path) -> Tuple[List[Dict[str, Any]], int, int]:
    findings: List[Dict[str, Any]] = []
    expected = fixture_expectations()
    base = repo_root / fixture_dir
    if not base.exists():
        return [finding("error", "replacement_fixture_dir_missing", f"missing fixture directory: {fixture_dir.as_posix()}", fixture_dir.as_posix())], 0, 0

    context = fixture_context(repo_root)
    valid_count = 0
    invalid_count = 0
    for filename, should_pass in expected.items():
        path = base / filename
        rel = f"{fixture_dir.as_posix()}/{filename}"
        if not path.exists():
            findings.append(finding("error", "replacement_fixture_missing", f"missing fixture: {rel}", rel))
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            findings.append(finding("error", "replacement_fixture_invalid_json", f"{rel} does not parse as JSON: {exc}", rel))
            continue
        packet_findings = validate_replacement_packet(
            data,
            path=rel,
            kinds=context[0],
            compatibility_values=context[1],
            abi_values=context[2],
            dependency_values=context[3],
            approval_values=context[4],
            statuses=context[5],
            public_ids=context[6],
            diagnostic_codes=context[7],
            refusal_codes=context[8],
            artifact_kinds=context[9],
            provider_ids=context[10],
        )
        errors = [item for item in packet_findings if item.get("level") == "error"]
        if should_pass and errors:
            findings.extend(packet_findings)
            findings.append(finding("error", "replacement_valid_fixture_failed", f"valid fixture failed validation: {rel}", rel))
        elif not should_pass and not errors:
            findings.append(finding("error", "replacement_invalid_fixture_passed", f"invalid fixture unexpectedly passed: {rel}", rel))
        if should_pass:
            valid_count += 1
        else:
            invalid_count += 1
    return findings, valid_count, invalid_count


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
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def classify_inventory_path(path: str) -> Optional[str]:
    lowered = path.lower()
    if not (
        lowered.startswith(".aide/reports/")
        or lowered.startswith("docs/repo/root-recycling/")
        or lowered.startswith("docs/repo/audits/")
        or lowered.startswith("contracts/repo/")
        or lowered.startswith("archive/historical/")
        or lowered.startswith("archive/generated/")
    ):
        return None
    if "move" in lowered or "root-recycling" in lowered or "restructure" in lowered:
        return "historical_directory_replacement"
    if "router" in lowered or "repair" in lowered:
        return "tooling_replacement"
    if "schema" in lowered or "protocol" in lowered:
        return "schema_protocol_replacement"
    if "provider" in lowered or "module" in lowered or "workbench" in lowered:
        return "provider_module_candidate"
    if lowered.startswith("contracts/repo/"):
        return "future_replacement_candidate"
    if lowered.startswith("archive/generated/") or lowered.startswith("archive/historical/"):
        return "archive_generated_history"
    if "canon" in lowered:
        return "governance_replacement_history"
    return "deferred"


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
        "files_scanned": len(files),
        "replacement_like_files": sum(counts.values()),
        "by_category": counts,
        "examples": examples,
        "status": "warning" if counts else "pass",
        "note": "Inventory is descriptive only; historical evidence is not retrofitted into formal packets.",
    }


def format_text(result: Dict[str, Any]) -> str:
    lines = [
        "Dominium replacement protocol validation",
        f"status: {result['status']}",
        f"replacement_kinds: {result['replacement_kinds_registered']}",
        f"replacement_statuses: {result['replacement_statuses_registered']}",
        f"findings: {len(result['findings'])}",
    ]
    if result.get("fixtures"):
        fixtures = result["fixtures"]
        lines.append(f"fixtures: valid={fixtures.get('valid')} invalid={fixtures.get('invalid')} status={fixtures.get('status')}")
    if result.get("inventory"):
        inv = result["inventory"]
        lines.append(f"inventory: files_scanned={inv.get('files_scanned')} replacement_like={inv.get('replacement_like_files')} status={inv.get('status')}")
        for category, count in sorted(inv.get("by_category", {}).items()):
            lines.append(f"- {category}: {count}")
    for item in result["findings"]:
        path = f" [{item.get('path')}]" if item.get("path") else ""
        lines.append(f"- {item['level'].upper()} {item['code']}{path}: {item['message']}")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Validate contracts, registries, and fixture expectations")
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    parser.add_argument("--fixtures", action="store_true", help="Validate replacement packet fixtures")
    parser.add_argument("--inventory", action="store_true", help="Inventory replacement-like historical evidence")
    parser.add_argument("--fixture-dir", default=str(FIXTURE_DIR_REL), help="Fixture directory")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: List[Dict[str, Any]] = []
    fixture_result: Optional[Dict[str, Any]] = None
    inventory_result: Optional[Dict[str, Any]] = None

    findings.extend(validate_json_contracts(repo_root))
    findings.extend(validate_toml_contracts(repo_root))
    registry_findings, kind_count, status_count = validate_replacement_registries(repo_root)
    findings.extend(registry_findings)

    if args.fixtures or args.strict:
        fixture_findings, valid_count, invalid_count = run_fixture_checks(repo_root, Path(args.fixture_dir))
        findings.extend(fixture_findings)
        fixture_errors = [item for item in fixture_findings if item.get("level") == "error"]
        fixture_result = {
            "valid": valid_count,
            "invalid": invalid_count,
            "status": "fail" if fixture_errors else "pass",
        }

    if args.inventory:
        inventory_result = inventory(repo_root)

    errors = [item for item in findings if item.get("level") == "error"]
    result: Dict[str, Any] = {
        "schema_version": "dominium.replacement.validation_result.v1",
        "status": "fail" if errors else "pass",
        "strict": bool(args.strict),
        "replacement_kinds_registered": kind_count,
        "replacement_statuses_registered": status_count,
        "findings": findings,
    }
    if fixture_result is not None:
        result["fixtures"] = fixture_result
    if inventory_result is not None:
        result["inventory"] = inventory_result

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_text(result))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
