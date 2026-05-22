#!/usr/bin/env python3
"""Validate Dominium portability contracts, matrices, and fixtures."""

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


CONTRACT_REL = Path("contracts/platform/portability_matrix.contract.toml")
PLATFORM_REGISTRY_REL = Path("contracts/platform/platform_floor.registry.json")
ARCH_REGISTRY_REL = Path("contracts/platform/architecture.registry.json")
TOOLCHAIN_REGISTRY_REL = Path("contracts/platform/toolchain.registry.json")
PLATFORM_CAPABILITY_SCHEMA_REL = Path("contracts/platform/platform_capability.schema.json")
EVIDENCE_SCHEMA_REL = Path("contracts/platform/portability_evidence.schema.json")
RUNTIME_MATRIX_REL = Path("contracts/platform/runtime_portability.matrix.json")
RENDERER_MATRIX_REL = Path("contracts/platform/renderer_portability.matrix.json")
PRODUCT_MODE_MATRIX_REL = Path("contracts/platform/product_mode_portability.matrix.json")
PACKAGE_MATRIX_REL = Path("contracts/platform/package_portability.matrix.json")
STATUS_REGISTRY_REL = Path("contracts/platform/portability_status.registry.json")
REFUSAL_POLICY_REL = Path("contracts/platform/portability_refusal_policy.contract.toml")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
PROVIDER_REGISTRY_REL = Path("contracts/provider/provider.registry.json")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
FIXTURE_DIR_REL = Path("tests/contract/portability/fixtures")

JSON_RELS = [
    PLATFORM_REGISTRY_REL,
    ARCH_REGISTRY_REL,
    TOOLCHAIN_REGISTRY_REL,
    PLATFORM_CAPABILITY_SCHEMA_REL,
    EVIDENCE_SCHEMA_REL,
    RUNTIME_MATRIX_REL,
    RENDERER_MATRIX_REL,
    PRODUCT_MODE_MATRIX_REL,
    PACKAGE_MATRIX_REL,
    STATUS_REGISTRY_REL,
]
TOML_RELS = [CONTRACT_REL, REFUSAL_POLICY_REL]
MATRIX_RELS = [RUNTIME_MATRIX_REL, RENDERER_MATRIX_REL, PRODUCT_MODE_MATRIX_REL, PACKAGE_MATRIX_REL]

EXPECTED_CONTRACT_IDS = {
    CONTRACT_REL: "dominium.portability.matrix.v1",
    REFUSAL_POLICY_REL: "dominium.portability.refusal_policy.v1",
}
REQUIRED_PLATFORM_FLOORS = {
    "winnt10_x64",
    "winnt7_x64",
    "winxp_x86",
    "linux_x64",
    "macos_x64",
    "macos_arm64",
    "headless_host",
    "portable_package",
}
REQUIRED_ARCHITECTURES = {"x86", "x64", "x86_64", "arm64", "armv7", "ppc", "wasm32", "host"}
REQUIRED_TOOLCHAINS = {
    "msvc143",
    "msvc141",
    "msvc141_xp",
    "msvc100",
    "vc6",
    "gcc",
    "clang",
    "xcode",
    "codewarrior",
    "host_default",
}
REQUIRED_STATUSES = {
    "unsupported",
    "planned",
    "research",
    "experimental",
    "provisional",
    "build_proven",
    "smoke_proven",
    "product_proven",
    "release_candidate",
    "supported",
    "deprecated",
    "retired",
    "historical",
}
REQUIRED_PUBLIC_SURFACES = {
    "dominium.portability.matrix.v1",
    "dominium.platform.floor.registry.v1",
    "dominium.platform.toolchain.registry.v1",
    "dominium.runtime.portability.matrix.v1",
    "dominium.renderer.portability.matrix.v1",
    "dominium.product_mode.portability.matrix.v1",
    "dominium.package.portability.matrix.v1",
    "dominium.portability.validator.v1",
}
REQUIRED_DIAGNOSTICS = {
    "DOM-PORTABILITY-UNSUPPORTED-PLATFORM",
    "DOM-PORTABILITY-UNSUPPORTED-ARCH",
    "DOM-PORTABILITY-UNSUPPORTED-TOOLCHAIN",
    "DOM-PORTABILITY-BUILD-PROOF-MISSING",
    "DOM-PORTABILITY-SMOKE-PROOF-MISSING",
    "DOM-PORTABILITY-PRODUCT-PROOF-MISSING",
    "DOM-PORTABILITY-RELEASE-PROOF-MISSING",
    "DOM-PORTABILITY-PROVIDER-UNAVAILABLE",
    "DOM-PORTABILITY-MODE-UNSUPPORTED",
}
REQUIRED_REFUSALS = {
    "dominium.refusal.portability.platform_unsupported",
    "dominium.refusal.portability.arch_unsupported",
    "dominium.refusal.portability.toolchain_unsupported",
    "dominium.refusal.portability.provider_unavailable",
    "dominium.refusal.portability.product_mode_unsupported",
    "dominium.refusal.portability.release_not_proven",
}
OPTIONAL_CAPABILITIES = {
    "domino.platform.headless",
    "domino.platform.win32",
    "domino.platform.posix",
    "domino.toolchain.msvc143",
    "domino.package.portable",
    "dominium.product.mode.cli",
    "dominium.product.mode.headless",
    "dominium.product.mode.rendered",
}
TARGET_KINDS = {
    "platform_floor",
    "architecture",
    "toolchain",
    "build_tuple",
    "runtime_provider",
    "renderer_provider",
    "product_mode",
    "package_mode",
    "release_artifact",
    "test_fixture",
    "historical",
}
NON_SUPPORT_STATUSES = {"unsupported", "planned", "research", "experimental", "provisional", "historical"}
SUPPORTED_REQUIRED_EVIDENCE = {"build", "smoke", "product", "package", "release"}
STATUS_REQUIRED_EVIDENCE = {
    "build_proven": {"build"},
    "smoke_proven": {"smoke"},
    "product_proven": {"product"},
    "release_candidate": {"release"},
}
DOTTED_ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)+$")
PATH_LIKE_RE = re.compile(r"[/\\]|(^|\.)\.($|\.)")


class CheckResult:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


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


def registry_ids(data: Dict[str, Any], key: str, id_key: str) -> Set[str]:
    return {
        str(item.get(id_key))
        for item in as_list(data.get(key))
        if isinstance(item, dict) and item.get(id_key)
    }


def public_surface_ids(data: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("id"))
        for item in as_list(data.get("surface"))
        if isinstance(item, dict) and item.get("id")
    }


def evidence_kinds(row: Dict[str, Any]) -> Set[str]:
    kinds: Set[str] = set()
    for item in as_list(row.get("test_evidence") or row.get("evidence")):
        if isinstance(item, dict) and item.get("kind"):
            kinds.add(str(item["kind"]))
    return kinds


def check_required_paths(repo_root: Path, result: CheckResult) -> None:
    for rel in JSON_RELS + TOML_RELS:
        if not (repo_root / rel).exists():
            result.error(f"missing required portability artifact: {rel.as_posix()}")


def validate_json_and_toml(repo_root: Path, result: CheckResult) -> Tuple[Dict[Path, Dict[str, Any]], Dict[Path, Dict[str, Any]]]:
    json_data: Dict[Path, Dict[str, Any]] = {}
    toml_data: Dict[Path, Dict[str, Any]] = {}
    for rel in JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            continue
        try:
            data = load_json(path)
            if not isinstance(data, dict):
                result.error(f"{rel.as_posix()} root must be a JSON object")
            else:
                json_data[rel] = data
        except Exception as exc:
            result.error(f"{rel.as_posix()} is not valid JSON: {exc}")
    for rel in TOML_RELS:
        path = repo_root / rel
        if not path.exists():
            continue
        try:
            data = load_toml(path)
            toml_data[rel] = data
            expected = EXPECTED_CONTRACT_IDS.get(rel)
            actual = str(data.get("contract", {}).get("id", ""))
            if expected and actual != expected:
                result.error(f"{rel.as_posix()} contract.id must be {expected}, found {actual or '<missing>'}")
        except Exception as exc:
            result.error(f"{rel.as_posix()} is not valid TOML: {exc}")
    return json_data, toml_data


def validate_registry_sets(json_data: Dict[Path, Dict[str, Any]], result: CheckResult) -> Tuple[Set[str], Set[str], Set[str], Set[str], Dict[str, Set[str]]]:
    platform_floors = registry_ids(json_data.get(PLATFORM_REGISTRY_REL, {}), "platform_floors", "platform_floor")
    architectures = registry_ids(json_data.get(ARCH_REGISTRY_REL, {}), "architectures", "architecture")
    toolchains = registry_ids(json_data.get(TOOLCHAIN_REGISTRY_REL, {}), "toolchains", "toolchain")
    statuses = registry_ids(json_data.get(STATUS_REGISTRY_REL, {}), "statuses", "status")

    for required, actual, label in [
        (REQUIRED_PLATFORM_FLOORS, platform_floors, "platform floor"),
        (REQUIRED_ARCHITECTURES, architectures, "architecture"),
        (REQUIRED_TOOLCHAINS, toolchains, "toolchain"),
        (REQUIRED_STATUSES, statuses, "portability status"),
    ]:
        missing = sorted(required - actual)
        if missing:
            result.error(f"missing required {label} entries: {', '.join(missing)}")

    status_proof: Dict[str, Set[str]] = {}
    for item in as_list(json_data.get(STATUS_REGISTRY_REL, {}).get("statuses")):
        if isinstance(item, dict) and item.get("status"):
            status_proof[str(item["status"])] = {str(value) for value in as_list(item.get("proof_required"))}
    return platform_floors, architectures, toolchains, statuses, status_proof


def validate_floor_entry(entry: Dict[str, Any], result: CheckResult, path: str, architectures: Set[str], statuses: Set[str]) -> None:
    for field in ["platform_floor", "target_kind", "os_family", "architecture", "support_status"]:
        if not entry.get(field):
            result.error(f"{path}: platform floor missing {field}")
    if entry.get("target_kind") not in {"platform_floor", "package_mode"}:
        result.error(f"{path}: platform floor target_kind must be platform_floor or package_mode")
    arch = str(entry.get("architecture", ""))
    if arch and arch not in architectures:
        result.error(f"{path}: unknown architecture {arch}")
    status = str(entry.get("support_status", ""))
    if status and status not in statuses:
        result.error(f"{path}: unknown support_status {status}")
    if status in {"supported", "release_candidate"} and not as_list(entry.get("evidence")):
        result.error(f"{path}: {status} platform floor requires evidence")


def validate_toolchain_entry(entry: Dict[str, Any], result: CheckResult, path: str, statuses: Set[str]) -> None:
    for field in ["toolchain", "compiler", "language_floor", "abi", "support_status"]:
        if not entry.get(field):
            result.error(f"{path}: toolchain entry missing {field}")
    status = str(entry.get("support_status", ""))
    if status and status not in statuses:
        result.error(f"{path}: unknown support_status {status}")
    if entry.get("support_claim") == "supported" and status != "supported":
        result.error(f"{path}: support_claim supported conflicts with status {status}")
    if status in {"build_proven", "smoke_proven", "product_proven", "release_candidate", "supported"}:
        kinds = {
            str(item.get("kind"))
            for item in as_list(entry.get("evidence"))
            if isinstance(item, dict) and item.get("kind")
        }
        required = STATUS_REQUIRED_EVIDENCE.get(status, set())
        if status == "supported":
            required = SUPPORTED_REQUIRED_EVIDENCE
        missing = sorted(required - kinds)
        if missing:
            result.error(f"{path}: {status} toolchain missing evidence kinds: {', '.join(missing)}")


def validate_evidence(item: Dict[str, Any], result: CheckResult, path: str) -> None:
    for field in ["evidence_id", "kind", "path", "status"]:
        if not item.get(field):
            result.error(f"{path}: evidence missing {field}")
    evidence_id = str(item.get("evidence_id", ""))
    if evidence_id and not DOTTED_ID_RE.match(evidence_id):
        result.error(f"{path}: evidence_id must be dotted lowercase, found {evidence_id}")


def validate_row(
    row: Dict[str, Any],
    result: CheckResult,
    path: str,
    platform_floors: Set[str],
    architectures: Set[str],
    toolchains: Set[str],
    statuses: Set[str],
    status_proof: Dict[str, Set[str]],
    capability_ids: Set[str],
    provider_ids: Set[str],
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
) -> None:
    for field in ["target_id", "target_kind", "owner", "support_status", "architecture", "toolchain", "language_floor", "abi"]:
        if not row.get(field):
            result.error(f"{path}: row missing {field}")

    target_id = str(row.get("target_id", ""))
    if target_id:
        if not DOTTED_ID_RE.match(target_id):
            result.error(f"{path}: target_id must be dotted lowercase, found {target_id}")
        if PATH_LIKE_RE.search(target_id):
            result.error(f"{path}: target_id must not be path-like")

    target_kind = str(row.get("target_kind", ""))
    if target_kind and target_kind not in TARGET_KINDS:
        result.error(f"{path}: unknown target_kind {target_kind}")

    status = str(row.get("support_status", ""))
    if status and status not in statuses:
        result.error(f"{path}: unknown support_status {status}")

    floor = row.get("platform_floor")
    if floor and str(floor) not in platform_floors:
        result.error(f"{path}: unknown platform_floor {floor}")

    arch = str(row.get("architecture", ""))
    if arch and arch not in architectures:
        result.error(f"{path}: unknown architecture {arch}")

    toolchain = str(row.get("toolchain", ""))
    if toolchain and toolchain not in toolchains:
        result.error(f"{path}: unknown toolchain {toolchain}")

    claim = str(row.get("support_claim", "")).lower()
    if claim == "supported" and status != "supported":
        result.error(f"{path}: {status} row must not claim supported")
    if status in NON_SUPPORT_STATUSES and str(row.get("described_as", "")).lower() == "supported":
        result.error(f"{path}: {status} row is described as supported")

    kinds = evidence_kinds(row)
    required = set(status_proof.get(status, set()))
    if status == "supported":
        required = SUPPORTED_REQUIRED_EVIDENCE
    if row.get("stability") == "stable":
        required |= STATUS_REQUIRED_EVIDENCE.get(status, set()) or {"smoke"}
    missing = sorted(required - kinds)
    if missing:
        result.error(f"{path}: {status} row missing evidence kinds: {', '.join(missing)}")

    if target_kind == "product_mode" and status not in {"planned", "research", "unsupported", "historical"}:
        if not as_list(row.get("runtime_capabilities")):
            result.error(f"{path}: product mode rows require runtime_capabilities")

    for evidence in as_list(row.get("test_evidence")):
        if isinstance(evidence, dict):
            validate_evidence(evidence, result, path)
        else:
            result.error(f"{path}: test_evidence entries must be objects")

    if capability_ids:
        for field in ["provider_capabilities", "runtime_capabilities", "renderer_support", "storage_support", "package_support"]:
            for capability in as_list(row.get(field)):
                if not isinstance(capability, str):
                    continue
                if capability and capability not in capability_ids and capability.startswith(("domino.", "dominium.")):
                    result.error(f"{path}: {field} references unknown capability {capability}")

    provider_id = str(row.get("provider_id", ""))
    if provider_id and provider_ids and provider_id not in provider_ids and status not in {"planned", "research", "unsupported", "historical"}:
        result.error(f"{path}: provider_id {provider_id} is not registered")

    if diagnostic_codes:
        for code in as_list(row.get("diagnostic_codes")):
            if str(code) not in diagnostic_codes:
                result.error(f"{path}: unknown diagnostic code {code}")
    if refusal_codes:
        for code in as_list(row.get("refusal_codes")):
            if str(code) not in refusal_codes:
                result.error(f"{path}: unknown refusal code {code}")


def validate_matrices(
    repo_root: Path,
    json_data: Dict[Path, Dict[str, Any]],
    result: CheckResult,
    platform_floors: Set[str],
    architectures: Set[str],
    toolchains: Set[str],
    statuses: Set[str],
    status_proof: Dict[str, Set[str]],
    capability_ids: Set[str],
    provider_ids: Set[str],
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
) -> None:
    seen: Set[str] = set()
    counts: Dict[str, int] = {}
    for rel in MATRIX_RELS:
        matrix = json_data.get(rel, {})
        rows = as_list(matrix.get("rows"))
        counts[rel.name] = len(rows)
        if not rows:
            result.error(f"{rel.as_posix()} must contain at least one row")
        for index, row in enumerate(rows):
            path = f"{rel.as_posix()}#rows[{index}]"
            if not isinstance(row, dict):
                result.error(f"{path}: row must be object")
                continue
            target_id = str(row.get("target_id", ""))
            if target_id:
                if target_id in seen:
                    result.error(f"{path}: duplicate target_id {target_id}")
                seen.add(target_id)
            validate_row(row, result, path, platform_floors, architectures, toolchains, statuses, status_proof, capability_ids, provider_ids, diagnostic_codes, refusal_codes)
    result.info["matrix_rows"] = counts

    for entry in as_list(json_data.get(PLATFORM_REGISTRY_REL, {}).get("platform_floors")):
        if isinstance(entry, dict):
            validate_floor_entry(entry, result, PLATFORM_REGISTRY_REL.as_posix(), architectures, statuses)
    for entry in as_list(json_data.get(TOOLCHAIN_REGISTRY_REL, {}).get("toolchains")):
        if isinstance(entry, dict):
            validate_toolchain_entry(entry, result, TOOLCHAIN_REGISTRY_REL.as_posix(), statuses)


def optional_registry_sets(repo_root: Path, result: CheckResult) -> Tuple[Set[str], Set[str], Set[str], Set[str], Set[str]]:
    capability_ids: Set[str] = set()
    provider_ids: Set[str] = set()
    diagnostic_codes: Set[str] = set()
    refusal_codes: Set[str] = set()
    surface_ids: Set[str] = set()

    if (repo_root / CAPABILITY_REGISTRY_REL).exists():
        capability_ids = registry_ids(load_json(repo_root / CAPABILITY_REGISTRY_REL), "capabilities", "capability_id")
        missing = sorted(OPTIONAL_CAPABILITIES - capability_ids)
        if missing:
            result.warn(f"optional portability capabilities are not registered: {', '.join(missing)}")
    else:
        result.warn("capability registry absent; capability references were not checked")

    if (repo_root / PROVIDER_REGISTRY_REL).exists():
        provider_ids = registry_ids(load_json(repo_root / PROVIDER_REGISTRY_REL), "providers", "provider_id")

    if (repo_root / DIAGNOSTIC_REGISTRY_REL).exists():
        diagnostic_codes = registry_ids(load_json(repo_root / DIAGNOSTIC_REGISTRY_REL), "codes", "code")
        missing = sorted(REQUIRED_DIAGNOSTICS - diagnostic_codes)
        if missing:
            result.error(f"missing portability diagnostics: {', '.join(missing)}")
    else:
        result.warn("diagnostics registry absent; diagnostic references were not checked")

    if (repo_root / REFUSAL_REGISTRY_REL).exists():
        refusal_codes = registry_ids(load_json(repo_root / REFUSAL_REGISTRY_REL), "codes", "code")
        missing = sorted(REQUIRED_REFUSALS - refusal_codes)
        if missing:
            result.error(f"missing portability refusal codes: {', '.join(missing)}")
    else:
        result.warn("refusal registry absent; refusal references were not checked")

    if (repo_root / PUBLIC_SURFACE_REGISTRY_REL).exists():
        surface_ids = public_surface_ids(load_toml(repo_root / PUBLIC_SURFACE_REGISTRY_REL))
        missing = sorted(REQUIRED_PUBLIC_SURFACES - surface_ids)
        if missing:
            result.error(f"missing portability public surfaces: {', '.join(missing)}")
    else:
        result.warn("public surface registry absent; public surface references were not checked")

    return capability_ids, provider_ids, diagnostic_codes, refusal_codes, surface_ids


def validate_fixture_document(
    item: Dict[str, Any],
    result: CheckResult,
    path: str,
    platform_floors: Set[str],
    architectures: Set[str],
    toolchains: Set[str],
    statuses: Set[str],
    status_proof: Dict[str, Set[str]],
    capability_ids: Set[str],
    provider_ids: Set[str],
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
) -> None:
    fixture_kind = str(item.get("fixture_kind", "portability_row"))
    if fixture_kind == "platform_floor":
        validate_floor_entry(item, result, path, architectures, statuses)
    elif fixture_kind == "toolchain":
        validate_toolchain_entry(item, result, path, statuses)
    elif fixture_kind == "evidence":
        validate_evidence(item, result, path)
    else:
        validate_row(item, result, path, platform_floors, architectures, toolchains, statuses, status_proof, capability_ids, provider_ids, diagnostic_codes, refusal_codes)


def validate_fixtures(
    repo_root: Path,
    result: CheckResult,
    platform_floors: Set[str],
    architectures: Set[str],
    toolchains: Set[str],
    statuses: Set[str],
    status_proof: Dict[str, Set[str]],
    capability_ids: Set[str],
    provider_ids: Set[str],
    diagnostic_codes: Set[str],
    refusal_codes: Set[str],
) -> None:
    fixture_dir = repo_root / FIXTURE_DIR_REL
    if not fixture_dir.exists():
        result.error(f"missing fixture directory: {FIXTURE_DIR_REL.as_posix()}")
        return
    valid_count = 0
    invalid_count = 0
    for path in sorted(fixture_dir.glob("*.json")):
        local = CheckResult()
        try:
            data = load_json(path)
            validate_fixture_document(
                data,
                local,
                path.relative_to(repo_root).as_posix(),
                platform_floors,
                architectures,
                toolchains,
                statuses,
                status_proof,
                capability_ids,
                provider_ids,
                diagnostic_codes,
                refusal_codes,
            )
        except Exception as exc:
            local.error(f"{path.relative_to(repo_root).as_posix()}: invalid JSON fixture: {exc}")
        expects_invalid = path.name.startswith("invalid_")
        if expects_invalid:
            invalid_count += 1
            if not local.errors:
                result.error(f"{path.relative_to(repo_root).as_posix()} was expected to fail but passed")
        else:
            valid_count += 1
            if local.errors:
                result.error(f"{path.relative_to(repo_root).as_posix()} should pass but failed: {'; '.join(local.errors)}")
    result.info["fixtures"] = {"valid": valid_count, "invalid": invalid_count}


def inventory(repo_root: Path, result: CheckResult) -> None:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        files = proc.stdout.splitlines()
    except Exception as exc:
        result.warn(f"inventory skipped; git ls-files failed: {exc}")
        return

    categories: Dict[str, List[str]] = {
        "build_proven_target": [],
        "smoke_proven_target": [],
        "product_proven_target": [],
        "release_proven_target": [],
        "planned_target": [],
        "research_target": [],
        "unsupported": [],
        "historical": [],
        "unknown_deferred": [],
    }
    for rel in files:
        lower = rel.lower()
        if lower.endswith("cmakepresets.json") or lower.startswith("contracts/build/") or lower.startswith("tools/build/"):
            categories["build_proven_target"].append(rel)
        elif "fast-strict" in lower or "smoke" in lower or "platform_contract_tests" in lower:
            categories["smoke_proven_target"].append(rel)
        elif "product_boot" in lower or "runtime_bundle" in lower:
            categories["product_proven_target"].append(rel)
        elif lower.startswith("docs/release/") or lower.startswith("release/"):
            categories["release_proven_target"].append(rel)
        elif "target_matrix" in lower or "toolchain_matrix" in lower or "platform_matrix" in lower:
            categories["planned_target"].append(rel)
        elif "legacy" in lower or "vc6" in lower or "codewarrior" in lower or "xp" in lower:
            categories["research_target"].append(rel)
        elif lower.startswith("archive/"):
            categories["historical"].append(rel)
        elif any(part in lower for part in ["platform", "toolchain", "renderer", "portable"]):
            categories["unknown_deferred"].append(rel)

    result.info["inventory"] = {key: len(value) for key, value in categories.items()}
    result.info["inventory_examples"] = {key: value[:12] for key, value in categories.items() if value}


def run_checks(repo_root: Path, include_fixtures: bool, include_inventory: bool) -> CheckResult:
    result = CheckResult()
    check_required_paths(repo_root, result)
    json_data, _toml_data = validate_json_and_toml(repo_root, result)
    platform_floors, architectures, toolchains, statuses, status_proof = validate_registry_sets(json_data, result)
    capability_ids, provider_ids, diagnostic_codes, refusal_codes, _surface_ids = optional_registry_sets(repo_root, result)

    validate_matrices(
        repo_root,
        json_data,
        result,
        platform_floors,
        architectures,
        toolchains,
        statuses,
        status_proof,
        capability_ids,
        provider_ids,
        diagnostic_codes,
        refusal_codes,
    )
    if include_fixtures:
        validate_fixtures(
            repo_root,
            result,
            platform_floors,
            architectures,
            toolchains,
            statuses,
            status_proof,
            capability_ids,
            provider_ids,
            diagnostic_codes,
            refusal_codes,
        )
    if include_inventory:
        inventory(repo_root, result)

    result.info.setdefault("platform_floors_registered", len(platform_floors))
    result.info.setdefault("architectures_registered", len(architectures))
    result.info.setdefault("toolchains_registered", len(toolchains))
    result.info.setdefault("statuses_registered", len(statuses))
    return result


def print_text(result: CheckResult) -> None:
    if result.errors:
        print("PORTABILITY-MATRIX: FAIL")
        for error in result.errors:
            print(f"ERROR: {error}")
    else:
        print("PORTABILITY-MATRIX: PASS")
    for warning in result.warnings:
        print(f"WARN: {warning}")
    if result.info:
        print(json.dumps(result.info, indent=2, sort_keys=True))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--strict", action="store_true", help="Validate contracts, matrices, registries, and fixtures.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    parser.add_argument("--fixtures", action="store_true", help="Validate fixtures.")
    parser.add_argument("--inventory", action="store_true", help="Report portability inventory without failing on historical gaps.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    include_fixtures = args.strict or args.fixtures
    include_inventory = args.inventory
    result = run_checks(repo_root, include_fixtures=include_fixtures, include_inventory=include_inventory)

    if args.json:
        payload = {
            "status": "fail" if result.errors else "pass",
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
