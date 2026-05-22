#!/usr/bin/env python3
"""Validate Dominium native architecture policy, tiers, and fixtures."""

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


ARCH_POLICY_REL = Path("contracts/platform/architecture_policy.contract.toml")
ARCH_TIER_REGISTRY_REL = Path("contracts/platform/architecture_tier.registry.json")
ARCH_REGISTRY_REL = Path("contracts/platform/architecture.registry.json")
POINTER_WIDTH_SCHEMA_REL = Path("contracts/platform/pointer_width_policy.schema.json")
ENDIAN_POLICY_REL = Path("contracts/platform/endian_policy.contract.toml")
ARCH_CLAIM_SCHEMA_REL = Path("contracts/platform/architecture_claim.schema.json")
PORTABILITY_CONTRACT_REL = Path("contracts/platform/portability_matrix.contract.toml")
PLATFORM_FLOOR_REGISTRY_REL = Path("contracts/platform/platform_floor.registry.json")
RUNTIME_MATRIX_REL = Path("contracts/platform/runtime_portability.matrix.json")
RENDERER_MATRIX_REL = Path("contracts/platform/renderer_portability.matrix.json")
PRODUCT_MODE_MATRIX_REL = Path("contracts/platform/product_mode_portability.matrix.json")
PACKAGE_MATRIX_REL = Path("contracts/platform/package_portability.matrix.json")
PUBLIC_SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
DIAGNOSTIC_REGISTRY_REL = Path("contracts/diagnostic/diagnostic_code.registry.json")
REFUSAL_REGISTRY_REL = Path("contracts/refusal/refusal_code.registry.json")
CAPABILITY_REGISTRY_REL = Path("contracts/capability/capability.registry.json")
FIXTURE_DIR_REL = Path("tests/contract/architecture_policy")

JSON_RELS = [
    ARCH_TIER_REGISTRY_REL,
    ARCH_REGISTRY_REL,
    POINTER_WIDTH_SCHEMA_REL,
    ARCH_CLAIM_SCHEMA_REL,
    PLATFORM_FLOOR_REGISTRY_REL,
    RUNTIME_MATRIX_REL,
    RENDERER_MATRIX_REL,
    PRODUCT_MODE_MATRIX_REL,
    PACKAGE_MATRIX_REL,
    DIAGNOSTIC_REGISTRY_REL,
    REFUSAL_REGISTRY_REL,
    CAPABILITY_REGISTRY_REL,
]
TOML_RELS = [ARCH_POLICY_REL, ENDIAN_POLICY_REL, PORTABILITY_CONTRACT_REL, PUBLIC_SURFACE_REGISTRY_REL]
MATRIX_RELS = [RUNTIME_MATRIX_REL, RENDERER_MATRIX_REL, PRODUCT_MODE_MATRIX_REL, PACKAGE_MATRIX_REL]

EXPECTED_CONTRACT_IDS = {
    ARCH_POLICY_REL: "dominium.platform.architecture_policy.v1",
    ENDIAN_POLICY_REL: "dominium.platform.endian_policy.v1",
    PORTABILITY_CONTRACT_REL: "dominium.portability.matrix.v1",
}
REQUIRED_TIERS = {"source_native_64", "constrained_native_32", "contract_projection", "archive_runner"}
MAINLINE_ARCHITECTURES = {"x86_64", "arm64"}
ARCHITECTURE_ALIASES = {"x64": "x86_64"}
NON_MAINLINE_32_BIT_ARCHITECTURES = {"x86", "armv7", "wasm32"}
FULL_NATIVE_EVIDENCE_KINDS = {"build", "smoke", "product", "package", "release"}
FULL_NATIVE_SUPPORT_STATUSES = {"product_proven", "release_candidate", "supported"}
EVIDENCE_SUPPORT_STATUSES = {"build_proven", "smoke_proven", "product_proven", "release_candidate", "supported"}
PROJECTION_WORD_SIZES = {"host_declared", "host_or_artifact_declared", "declared_by_projection", "declared_by_runner"}
PROJECTION_ENDIANNESS = {
    "host_declared",
    "host_or_artifact_declared",
    "declared_by_projection",
    "declared_by_runner",
    "big_or_little_declared_by_target",
}
REQUIRED_DIAGNOSTICS = {
    "DOM-ARCH-32BIT-FULL-NATIVE-REFUSED",
    "DOM-ARCH-POINTER-WIDTH-PERSISTED-FORMAT",
    "DOM-ARCH-ENDIAN-UNSUPPORTED",
    "DOM-ARCH-CLAIM-EVIDENCE-MISSING",
    "DOM-ARCH-LEGACY-REQUIRES-PROJECTION",
}
REQUIRED_REFUSALS = {
    "dominium.refusal.architecture.full_native_32bit",
    "dominium.refusal.architecture.pointer_width_persisted",
    "dominium.refusal.architecture.endian_unsupported",
    "dominium.refusal.architecture.support_evidence_missing",
    "dominium.refusal.architecture.legacy_requires_projection",
}
REQUIRED_CAPABILITIES = {
    "dominium.platform.source_native_64",
    "dominium.platform.constrained_native_32",
    "dominium.platform.contract_projection",
    "dominium.platform.archive_runner",
}
REQUIRED_PUBLIC_SURFACES = {
    "dominium.platform.architecture_policy.v1",
    "dominium.platform.architecture_tier.registry.v1",
    "dominium.platform.pointer_width_policy.schema.v1",
    "dominium.platform.endian_policy.v1",
    "dominium.platform.architecture_claim.schema.v1",
    "dominium.platform.architecture_policy.validator.v1",
    "dominium.platform.architecture_policy.fixture_suite.v1",
}
FORBIDDEN_PERSISTED_TYPES = {
    "size_t",
    "ptrdiff_t",
    "long",
    "unsigned long",
    "intptr_t",
    "uintptr_t",
    "raw_pointer",
    "native_object_layout",
    "native_padding",
    "pointer_order",
    "address_hash",
}
ALLOWED_STABLE_DATA_TYPES = {
    "u8",
    "u16",
    "u32",
    "u64",
    "i8",
    "i16",
    "i32",
    "i64",
    "fixed32",
    "fixed64",
    "le_u16",
    "le_u32",
    "le_u64",
    "le_i32",
    "le_i64",
}
FIXTURE_EXPECTATIONS = {
    "valid_source_native_64.json": True,
    "valid_constrained_native_32.json": True,
    "valid_contract_projection.json": True,
    "invalid_32bit_full_native.json": False,
    "invalid_missing_word_size.json": False,
    "invalid_missing_endian.json": False,
    "invalid_pointer_width_persisted_format.json": False,
}
INVENTORY_PATTERNS = {
    "size_t": re.compile(r"\bsize_t\b"),
    "uintptr_t": re.compile(r"\buintptr_t\b"),
    "intptr_t": re.compile(r"\bintptr_t\b"),
    "sizeof_void_pointer": re.compile(r"sizeof\s*\(\s*void\s*\*\s*\)"),
    "int_cast": re.compile(r"\(\s*int\s*\)"),
    "long_cast": re.compile(r"\(\s*long\s*\)"),
    "pointer_hash": re.compile(r"pointer[_-]?hash|hash[_-]?pointer", re.IGNORECASE),
    "address_hash": re.compile(r"address[_-]?hash|hash[_-]?address", re.IGNORECASE),
    "pointer_sort": re.compile(r"pointer[_-]?sort|sort[_-]?pointer", re.IGNORECASE),
}
INVENTORY_SUFFIXES = {".h", ".hpp", ".hh", ".c", ".cc", ".cpp", ".cxx", ".inl", ".md", ".toml", ".json"}


class CheckResult:
    def __init__(self) -> None:
        self.findings: List[Dict[str, Any]] = []
        self.info: Dict[str, Any] = {}

    @property
    def errors(self) -> List[Dict[str, Any]]:
        return [item for item in self.findings if item["level"] == "error"]

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return [item for item in self.findings if item["level"] == "warning"]

    def add(
        self,
        level: str,
        code: str,
        message: str,
        path: Optional[Path | str] = None,
        field: Optional[str] = None,
        expected: Optional[Any] = None,
        actual: Optional[Any] = None,
        remediation: Optional[str] = None,
    ) -> None:
        item: Dict[str, Any] = {"level": level, "code": code, "message": message}
        if path is not None:
            item["path"] = str(path).replace("\\", "/")
        if field is not None:
            item["field"] = field
        if expected is not None:
            item["expected"] = expected
        if actual is not None:
            item["actual"] = actual
        if remediation is not None:
            item["remediation"] = remediation
        self.findings.append(item)

    def error(self, code: str, message: str, **kwargs: Any) -> None:
        self.add("error", code, message, **kwargs)

    def warn(self, code: str, message: str, **kwargs: Any) -> None:
        self.add("warning", code, message, **kwargs)


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


def effective_architecture(architecture: Any) -> str:
    text = str(architecture)
    return ARCHITECTURE_ALIASES.get(text, text)


def evidence_kinds(row: Dict[str, Any]) -> Set[str]:
    kinds: Set[str] = set()
    for item in as_list(row.get("test_evidence")) + as_list(row.get("evidence")):
        if isinstance(item, dict) and item.get("kind"):
            kinds.add(str(item["kind"]))
    return kinds


def load_inputs(repo_root: Path, result: CheckResult) -> Dict[Path, Any]:
    data: Dict[Path, Any] = {}
    for rel in TOML_RELS:
        path = repo_root / rel
        if not path.exists():
            result.error(
                "ARCH-MISSING-FILE",
                "Required architecture policy TOML file is missing.",
                path=rel,
                remediation="Add the required contract or registry file.",
            )
            continue
        try:
            data[rel] = load_toml(path)
        except Exception as exc:
            result.error("ARCH-TOML-PARSE", f"Could not parse TOML: {exc}", path=rel)
    for rel in JSON_RELS:
        path = repo_root / rel
        if not path.exists():
            result.error(
                "ARCH-MISSING-FILE",
                "Required architecture policy JSON file is missing.",
                path=rel,
                remediation="Add the required contract, registry, schema, or matrix file.",
            )
            continue
        try:
            data[rel] = load_json(path)
        except Exception as exc:
            result.error("ARCH-JSON-PARSE", f"Could not parse JSON: {exc}", path=rel)
    return data


def check_contracts(data: Dict[Path, Any], result: CheckResult) -> None:
    for rel, expected_id in EXPECTED_CONTRACT_IDS.items():
        document = data.get(rel)
        if not isinstance(document, dict):
            continue
        contract = document.get("contract")
        actual_id = contract.get("id") if isinstance(contract, dict) else document.get("id")
        if actual_id != expected_id:
            result.error(
                "ARCH-CONTRACT-ID",
                "Contract ID does not match expected architecture policy identity.",
                path=rel,
                field="contract.id",
                expected=expected_id,
                actual=actual_id,
            )

    policy = data.get(ARCH_POLICY_REL, {})
    policy_section = policy.get("policy") if isinstance(policy, dict) else {}
    if isinstance(policy_section, dict):
        if policy_section.get("mainline_tier") != "source_native_64":
            result.error(
                "ARCH-MAINLINE-TIER",
                "Architecture policy must declare source_native_64 as the mainline native tier.",
                path=ARCH_POLICY_REL,
                field="policy.mainline_tier",
                expected="source_native_64",
                actual=policy_section.get("mainline_tier"),
            )
        if set(as_list(policy_section.get("mainline_architectures"))) != MAINLINE_ARCHITECTURES:
            result.error(
                "ARCH-MAINLINE-ARCHITECTURES",
                "Architecture policy must declare exactly x86_64 and arm64 as mainline architectures.",
                path=ARCH_POLICY_REL,
                field="policy.mainline_architectures",
                expected=sorted(MAINLINE_ARCHITECTURES),
                actual=policy_section.get("mainline_architectures"),
            )
        if policy_section.get("mainline_word_size") != 64:
            result.error(
                "ARCH-MAINLINE-WORD-SIZE",
                "Mainline native policy must require 64-bit word size.",
                path=ARCH_POLICY_REL,
                field="policy.mainline_word_size",
                expected=64,
                actual=policy_section.get("mainline_word_size"),
            )
        if policy_section.get("mainline_endianness") != "little":
            result.error(
                "ARCH-MAINLINE-ENDIAN",
                "Mainline native policy must require little endian.",
                path=ARCH_POLICY_REL,
                field="policy.mainline_endianness",
                expected="little",
                actual=policy_section.get("mainline_endianness"),
            )

    aliases = policy.get("architecture_aliases") if isinstance(policy, dict) else {}
    if not isinstance(aliases, dict) or aliases.get("x64") != "x86_64":
        result.error(
            "ARCH-ALIAS-MISSING",
            "Architecture policy must declare x64 as a compatibility alias for x86_64.",
            path=ARCH_POLICY_REL,
            field="architecture_aliases.x64",
            expected="x86_64",
            actual=aliases.get("x64") if isinstance(aliases, dict) else None,
        )

    tiers = policy.get("tiers") if isinstance(policy, dict) else {}
    if not isinstance(tiers, dict):
        result.error("ARCH-TIERS-MISSING", "Architecture policy must define tier sections.", path=ARCH_POLICY_REL)
    else:
        missing = REQUIRED_TIERS - set(tiers)
        if missing:
            result.error(
                "ARCH-TIER-MISSING",
                "Architecture policy is missing required architecture tiers.",
                path=ARCH_POLICY_REL,
                field="tiers",
                expected=sorted(REQUIRED_TIERS),
                actual=sorted(tiers),
            )

    endian = data.get(ENDIAN_POLICY_REL, {})
    endian_policy = endian.get("policy") if isinstance(endian, dict) else {}
    if isinstance(endian_policy, dict):
        if endian_policy.get("mainline_endianness") != "little":
            result.error(
                "ARCH-ENDIAN-MAINLINE",
                "Endian policy must declare little endian as mainline.",
                path=ENDIAN_POLICY_REL,
                field="policy.mainline_endianness",
                expected="little",
                actual=endian_policy.get("mainline_endianness"),
            )
        if endian_policy.get("persisted_formats_use_explicit_little_endian") is not True:
            result.error(
                "ARCH-ENDIAN-PERSISTED",
                "Endian policy must require explicit little-endian persisted formats.",
                path=ENDIAN_POLICY_REL,
                field="policy.persisted_formats_use_explicit_little_endian",
                expected=True,
                actual=endian_policy.get("persisted_formats_use_explicit_little_endian"),
            )
    else:
        result.error("ARCH-ENDIAN-POLICY-MISSING", "Endian policy section is missing.", path=ENDIAN_POLICY_REL)


def check_tier_registry(data: Dict[Path, Any], result: CheckResult) -> None:
    registry = data.get(ARCH_TIER_REGISTRY_REL, {})
    tiers = [item for item in as_list(registry.get("tiers")) if isinstance(item, dict)]
    tier_ids = {str(item.get("tier_id")) for item in tiers if item.get("tier_id")}
    missing = REQUIRED_TIERS - tier_ids
    if missing:
        result.error(
            "ARCH-TIER-REGISTRY-MISSING",
            "Architecture tier registry is missing required tiers.",
            path=ARCH_TIER_REGISTRY_REL,
            field="tiers",
            expected=sorted(REQUIRED_TIERS),
            actual=sorted(tier_ids),
        )
    for item in tiers:
        tier_id = str(item.get("tier_id"))
        allowed = {str(arch) for arch in as_list(item.get("allowed_architectures"))}
        if tier_id == "source_native_64":
            if allowed != MAINLINE_ARCHITECTURES:
                result.error(
                    "ARCH-SOURCE-NATIVE-ALLOWED",
                    "source_native_64 tier must allow only x86_64 and arm64.",
                    path=ARCH_TIER_REGISTRY_REL,
                    field="tiers.source_native_64.allowed_architectures",
                    expected=sorted(MAINLINE_ARCHITECTURES),
                    actual=sorted(allowed),
                )
            if item.get("required_word_size") != 64:
                result.error(
                    "ARCH-SOURCE-NATIVE-WORD-SIZE",
                    "source_native_64 tier must require 64-bit word size.",
                    path=ARCH_TIER_REGISTRY_REL,
                    field="tiers.source_native_64.required_word_size",
                    expected=64,
                    actual=item.get("required_word_size"),
                )
            if item.get("required_endianness") != "little":
                result.error(
                    "ARCH-SOURCE-NATIVE-ENDIAN",
                    "source_native_64 tier must require little endian.",
                    path=ARCH_TIER_REGISTRY_REL,
                    field="tiers.source_native_64.required_endianness",
                    expected="little",
                    actual=item.get("required_endianness"),
                )
        if tier_id == "constrained_native_32":
            if item.get("required_word_size") != 32:
                result.error(
                    "ARCH-CONSTRAINED-WORD-SIZE",
                    "constrained_native_32 tier must require 32-bit word size.",
                    path=ARCH_TIER_REGISTRY_REL,
                    field="tiers.constrained_native_32.required_word_size",
                    expected=32,
                    actual=item.get("required_word_size"),
                )


def check_pointer_width_policy(data: Dict[Path, Any], result: CheckResult) -> None:
    policy = data.get(ARCH_POLICY_REL, {})
    pointer_policy = policy.get("pointer_width_policy") if isinstance(policy, dict) else {}
    if not isinstance(pointer_policy, dict):
        result.error("ARCH-POINTER-POLICY-MISSING", "Pointer-width policy is missing.", path=ARCH_POLICY_REL)
        pointer_policy = {}
    forbidden = set(str(item) for item in as_list(pointer_policy.get("forbidden_in_persisted_formats")))
    missing_forbidden = FORBIDDEN_PERSISTED_TYPES - forbidden
    if missing_forbidden:
        result.error(
            "ARCH-POINTER-FORBIDDEN-MISSING",
            "Pointer-width policy does not forbid all required persisted native-width constructs.",
            path=ARCH_POLICY_REL,
            field="pointer_width_policy.forbidden_in_persisted_formats",
            expected=sorted(FORBIDDEN_PERSISTED_TYPES),
            actual=sorted(forbidden),
        )
    allowed = set(str(item) for item in as_list(pointer_policy.get("allowed_stable_data_types")))
    missing_allowed = ALLOWED_STABLE_DATA_TYPES - allowed
    if missing_allowed:
        result.error(
            "ARCH-POINTER-STABLE-TYPES",
            "Pointer-width policy is missing required fixed-width stable data types.",
            path=ARCH_POLICY_REL,
            field="pointer_width_policy.allowed_stable_data_types",
            expected=sorted(ALLOWED_STABLE_DATA_TYPES),
            actual=sorted(allowed),
        )

    schema = data.get(POINTER_WIDTH_SCHEMA_REL, {})
    schema_forbidden = set(str(item) for item in as_list(schema.get("x-dominium-forbidden_persisted_types")))
    if FORBIDDEN_PERSISTED_TYPES - schema_forbidden:
        result.error(
            "ARCH-POINTER-SCHEMA-FORBIDDEN",
            "Pointer-width schema must list required forbidden persisted types.",
            path=POINTER_WIDTH_SCHEMA_REL,
            field="x-dominium-forbidden_persisted_types",
            expected=sorted(FORBIDDEN_PERSISTED_TYPES),
            actual=sorted(schema_forbidden),
        )
    schema_allowed = set(str(item) for item in as_list(schema.get("x-dominium-allowed_stable_types")))
    if ALLOWED_STABLE_DATA_TYPES - schema_allowed:
        result.error(
            "ARCH-POINTER-SCHEMA-ALLOWED",
            "Pointer-width schema must list required fixed-width stable data types.",
            path=POINTER_WIDTH_SCHEMA_REL,
            field="x-dominium-allowed_stable_types",
            expected=sorted(ALLOWED_STABLE_DATA_TYPES),
            actual=sorted(schema_allowed),
        )


def check_architecture_registry(data: Dict[Path, Any], result: CheckResult) -> None:
    registry = data.get(ARCH_REGISTRY_REL, {})
    rows = [item for item in as_list(registry.get("architectures")) if isinstance(item, dict)]
    by_arch = {str(item.get("architecture")): item for item in rows if item.get("architecture")}
    for required in {"x86_64", "x64", "arm64", "x86", "armv7", "host"}:
        if required not in by_arch:
            result.error(
                "ARCH-REGISTRY-MISSING",
                "Architecture registry is missing a required architecture or compatibility alias.",
                path=ARCH_REGISTRY_REL,
                field="architectures",
                expected=required,
                actual=sorted(by_arch),
            )
    for row in rows:
        arch = str(row.get("architecture"))
        tier = row.get("architecture_tier")
        effective = effective_architecture(arch)
        if arch == "x64" and row.get("alias_for") != "x86_64":
            result.error(
                "ARCH-ALIAS-REGISTRY",
                "x64 registry row must be marked as an alias for x86_64.",
                path=ARCH_REGISTRY_REL,
                field="architectures.x64.alias_for",
                expected="x86_64",
                actual=row.get("alias_for"),
            )
        if tier == "source_native_64":
            if effective not in MAINLINE_ARCHITECTURES:
                result.error(
                    "ARCH-FULL-NATIVE-ARCH",
                    "Only x86_64 and arm64 may be source_native_64.",
                    path=ARCH_REGISTRY_REL,
                    field=f"architectures.{arch}.architecture_tier",
                    expected=sorted(MAINLINE_ARCHITECTURES),
                    actual=arch,
                )
            if row.get("word_size") != 64:
                result.error(
                    "ARCH-FULL-NATIVE-WORD-SIZE",
                    "source_native_64 architecture rows must declare word_size 64.",
                    path=ARCH_REGISTRY_REL,
                    field=f"architectures.{arch}.word_size",
                    expected=64,
                    actual=row.get("word_size"),
                )
            if row.get("endianness") != "little":
                result.error(
                    "ARCH-FULL-NATIVE-ENDIAN",
                    "source_native_64 architecture rows must declare little endian.",
                    path=ARCH_REGISTRY_REL,
                    field=f"architectures.{arch}.endianness",
                    expected="little",
                    actual=row.get("endianness"),
                )
        if effective in NON_MAINLINE_32_BIT_ARCHITECTURES and tier == "source_native_64":
            result.error(
                "ARCH-32BIT-FULL-NATIVE",
                "32-bit architecture rows must not claim source_native_64.",
                path=ARCH_REGISTRY_REL,
                field=f"architectures.{arch}.architecture_tier",
                expected="constrained_native_32, contract_projection, archive_runner, research, planned, or unsupported",
                actual=tier,
            )


def _check_claim_shape(row: Dict[str, Any], rel: Path, result: CheckResult) -> None:
    target = str(row.get("target_id") or row.get("platform_floor") or row.get("architecture") or "<unknown>")
    tier = row.get("architecture_tier")
    arch = row.get("architecture")
    effective = effective_architecture(arch)
    word_size = row.get("word_size")
    endian = row.get("endianness")
    support_status = str(row.get("support_status", ""))

    if tier not in REQUIRED_TIERS:
        result.error(
            "ARCH-ROW-TIER-MISSING",
            "Portability row must declare a valid architecture_tier.",
            path=rel,
            field=f"{target}.architecture_tier",
            expected=sorted(REQUIRED_TIERS),
            actual=tier,
            remediation="Classify the row as source_native_64, constrained_native_32, contract_projection, or archive_runner.",
        )
        return

    if tier == "source_native_64":
        if effective not in MAINLINE_ARCHITECTURES:
            result.error(
                "ARCH-ROW-FULL-NATIVE-ARCH",
                "source_native_64 portability rows may target only x86_64 or arm64.",
                path=rel,
                field=f"{target}.architecture",
                expected=sorted(MAINLINE_ARCHITECTURES),
                actual=arch,
            )
        if word_size != 64:
            result.error(
                "ARCH-ROW-FULL-NATIVE-WORD-SIZE",
                "source_native_64 portability rows must declare word_size 64.",
                path=rel,
                field=f"{target}.word_size",
                expected=64,
                actual=word_size,
            )
        if endian != "little":
            result.error(
                "ARCH-ROW-FULL-NATIVE-ENDIAN",
                "source_native_64 portability rows must declare little endian.",
                path=rel,
                field=f"{target}.endianness",
                expected="little",
                actual=endian,
            )
    elif tier == "constrained_native_32":
        if effective not in {"x86", "armv7"}:
            result.error(
                "ARCH-ROW-CONSTRAINED-ARCH",
                "constrained_native_32 rows may target only x86 or armv7.",
                path=rel,
                field=f"{target}.architecture",
                expected=["x86", "armv7"],
                actual=arch,
            )
        if word_size != 32:
            result.error(
                "ARCH-ROW-CONSTRAINED-WORD-SIZE",
                "constrained_native_32 rows must declare word_size 32.",
                path=rel,
                field=f"{target}.word_size",
                expected=32,
                actual=word_size,
            )
        if endian != "little":
            result.error(
                "ARCH-ROW-CONSTRAINED-ENDIAN",
                "constrained_native_32 rows must declare little endian unless future law adds research support.",
                path=rel,
                field=f"{target}.endianness",
                expected="little",
                actual=endian,
            )
    else:
        if word_size is None:
            result.error(
                "ARCH-ROW-WORD-SIZE-MISSING",
                "Projection/archive rows must still declare word size policy.",
                path=rel,
                field=f"{target}.word_size",
                expected=sorted(PROJECTION_WORD_SIZES) + [32, 64],
                actual=word_size,
            )
        if endian is None:
            result.error(
                "ARCH-ROW-ENDIAN-MISSING",
                "Projection/archive rows must still declare endian policy.",
                path=rel,
                field=f"{target}.endianness",
                expected=sorted(PROJECTION_ENDIANNESS) + ["little", "big"],
                actual=endian,
            )

    if effective in NON_MAINLINE_32_BIT_ARCHITECTURES and tier == "source_native_64":
        result.error(
            "ARCH-ROW-32BIT-FULL-NATIVE",
            "32-bit rows must not claim full native product architecture tier.",
            path=rel,
            field=f"{target}.architecture_tier",
            expected="constrained_native_32, contract_projection, or archive_runner",
            actual=tier,
        )

    if support_status in EVIDENCE_SUPPORT_STATUSES:
        required = ["architecture", "architecture_tier", "word_size", "endianness", "abi", "toolchain", "language_floor", "provider_capabilities", "known_limitations", "diagnostic_codes", "refusal_codes"]
        for field in required:
            if field not in row:
                result.error(
                    "ARCH-ROW-SUPPORT-FIELD-MISSING",
                    "Evidence-bearing support rows must declare required architecture support fields.",
                    path=rel,
                    field=f"{target}.{field}",
                    expected="present",
                    actual="missing",
                )

    if tier == "source_native_64" and support_status in FULL_NATIVE_SUPPORT_STATUSES:
        kinds = evidence_kinds(row)
        missing_evidence = FULL_NATIVE_EVIDENCE_KINDS - kinds
        if missing_evidence:
            result.error(
                "ARCH-ROW-FULL-NATIVE-EVIDENCE",
                "Full native product support claims require build, smoke, product, package, and release evidence.",
                path=rel,
                field=f"{target}.evidence",
                expected=sorted(FULL_NATIVE_EVIDENCE_KINDS),
                actual=sorted(kinds),
            )


def check_portability_rows(data: Dict[Path, Any], result: CheckResult) -> None:
    floor_registry = data.get(PLATFORM_FLOOR_REGISTRY_REL, {})
    for row in [item for item in as_list(floor_registry.get("platform_floors")) if isinstance(item, dict)]:
        _check_claim_shape(row, PLATFORM_FLOOR_REGISTRY_REL, result)

    for rel in MATRIX_RELS:
        document = data.get(rel, {})
        for row in [item for item in as_list(document.get("rows")) if isinstance(item, dict)]:
            _check_claim_shape(row, rel, result)


def check_cross_registries(data: Dict[Path, Any], result: CheckResult) -> None:
    diagnostics = registry_ids(data.get(DIAGNOSTIC_REGISTRY_REL, {}), "codes", "code")
    missing_diag = REQUIRED_DIAGNOSTICS - diagnostics
    if missing_diag:
        result.error(
            "ARCH-DIAGNOSTICS-MISSING",
            "Architecture policy diagnostics are missing from the diagnostic registry.",
            path=DIAGNOSTIC_REGISTRY_REL,
            field="codes",
            expected=sorted(REQUIRED_DIAGNOSTICS),
            actual=sorted(diagnostics & REQUIRED_DIAGNOSTICS),
        )

    refusals = registry_ids(data.get(REFUSAL_REGISTRY_REL, {}), "codes", "refusal_id")
    missing_refusal = REQUIRED_REFUSALS - refusals
    if missing_refusal:
        result.error(
            "ARCH-REFUSALS-MISSING",
            "Architecture policy refusal codes are missing from the refusal registry.",
            path=REFUSAL_REGISTRY_REL,
            field="codes",
            expected=sorted(REQUIRED_REFUSALS),
            actual=sorted(refusals & REQUIRED_REFUSALS),
        )

    capabilities = registry_ids(data.get(CAPABILITY_REGISTRY_REL, {}), "capabilities", "capability_id")
    missing_caps = REQUIRED_CAPABILITIES - capabilities
    if missing_caps:
        result.error(
            "ARCH-CAPABILITIES-MISSING",
            "Architecture policy capabilities are missing from the capability registry.",
            path=CAPABILITY_REGISTRY_REL,
            field="capabilities",
            expected=sorted(REQUIRED_CAPABILITIES),
            actual=sorted(capabilities & REQUIRED_CAPABILITIES),
        )

    public_surface = data.get(PUBLIC_SURFACE_REGISTRY_REL, {})
    surfaces = registry_ids(public_surface, "surface", "id")
    missing_surfaces = REQUIRED_PUBLIC_SURFACES - surfaces
    if missing_surfaces:
        result.error(
            "ARCH-PUBLIC-SURFACES-MISSING",
            "Architecture policy public surfaces are missing from the public surface registry.",
            path=PUBLIC_SURFACE_REGISTRY_REL,
            field="surface",
            expected=sorted(REQUIRED_PUBLIC_SURFACES),
            actual=sorted(surfaces & REQUIRED_PUBLIC_SURFACES),
        )


def check_fixture_claim(claim: Dict[str, Any], path: Path) -> List[Dict[str, Any]]:
    result = CheckResult()
    _check_claim_shape(claim, path, result)
    forbidden_types = FORBIDDEN_PERSISTED_TYPES
    for field in as_list(claim.get("stable_persisted_fields")):
        if not isinstance(field, dict):
            result.error(
                "ARCH-FIXTURE-PERSISTED-FIELD",
                "stable_persisted_fields entries must be objects.",
                path=path,
                remediation="Use objects with name and type fields.",
            )
            continue
        field_type = str(field.get("type", ""))
        if field_type in forbidden_types:
            result.error(
                "ARCH-FIXTURE-FORBIDDEN-PERSISTED-TYPE",
                "Stable persisted fields must not use native pointer-width or object-layout types.",
                path=path,
                field=f"stable_persisted_fields.{field.get('name', '<unknown>')}.type",
                expected="fixed-width explicit type",
                actual=field_type,
            )
    return result.findings


def check_fixtures(repo_root: Path, result: CheckResult) -> Dict[str, Any]:
    fixture_dir = repo_root / FIXTURE_DIR_REL
    summary: Dict[str, Any] = {"fixtures": []}
    if not fixture_dir.exists():
        result.error("ARCH-FIXTURE-DIR-MISSING", "Architecture fixture directory is missing.", path=FIXTURE_DIR_REL)
        return summary
    for filename, expected_valid in FIXTURE_EXPECTATIONS.items():
        rel = FIXTURE_DIR_REL / filename
        path = repo_root / rel
        if not path.exists():
            result.error("ARCH-FIXTURE-MISSING", "Required architecture policy fixture is missing.", path=rel)
            summary["fixtures"].append({"path": str(rel), "expected_valid": expected_valid, "status": "missing"})
            continue
        try:
            data = load_json(path)
        except Exception as exc:
            result.error("ARCH-FIXTURE-PARSE", f"Could not parse architecture fixture: {exc}", path=rel)
            summary["fixtures"].append({"path": str(rel), "expected_valid": expected_valid, "status": "parse_error"})
            continue
        findings = check_fixture_claim(data, rel)
        actual_valid = not findings
        summary["fixtures"].append(
            {
                "path": str(rel).replace("\\", "/"),
                "expected_valid": expected_valid,
                "actual_valid": actual_valid,
                "finding_count": len(findings),
            }
        )
        if actual_valid != expected_valid:
            result.error(
                "ARCH-FIXTURE-EXPECTATION",
                "Architecture policy fixture did not match expected validity.",
                path=rel,
                expected=expected_valid,
                actual=actual_valid,
                remediation="Repair the fixture or the validator rule so valid fixtures pass and invalid fixtures fail.",
            )
    return summary


def git_ls_files(repo_root: Path) -> List[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return []
    return [Path(line.strip()) for line in completed.stdout.splitlines() if line.strip()]


def inventory_pointer_width(repo_root: Path, max_per_kind: int = 50) -> Dict[str, Any]:
    inventory: Dict[str, Any] = {key: {"count": 0, "examples": []} for key in INVENTORY_PATTERNS}
    for rel in git_ls_files(repo_root):
        if rel.parts and rel.parts[0] in {".aide", "archive", "external", "out", "build"}:
            continue
        if rel.suffix.lower() not in INVENTORY_SUFFIXES:
            continue
        path = repo_root / rel
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for key, pattern in INVENTORY_PATTERNS.items():
                if pattern.search(line):
                    entry = inventory[key]
                    entry["count"] += 1
                    if len(entry["examples"]) < max_per_kind:
                        entry["examples"].append({"path": str(rel).replace("\\", "/"), "line": lineno, "text": line.strip()[:180]})
    return inventory


def run_checks(repo_root: Path, include_fixtures: bool, include_inventory: bool) -> CheckResult:
    result = CheckResult()
    data = load_inputs(repo_root, result)
    check_contracts(data, result)
    check_tier_registry(data, result)
    check_pointer_width_policy(data, result)
    check_architecture_registry(data, result)
    check_portability_rows(data, result)
    check_cross_registries(data, result)
    if include_fixtures:
        result.info["fixtures"] = check_fixtures(repo_root, result)
    if include_inventory:
        result.info["pointer_width_inventory"] = inventory_pointer_width(repo_root)
    result.info["summary"] = {
        "errors": len(result.errors),
        "warnings": len(result.warnings),
        "findings": len(result.findings),
        "required_tiers": sorted(REQUIRED_TIERS),
        "mainline_architectures": sorted(MAINLINE_ARCHITECTURES),
    }
    return result


def emit_text(result: CheckResult, *, inventory_only: bool = False) -> None:
    status = "PASS" if not result.errors else "FAIL"
    if inventory_only:
        status = "INVENTORY"
    print(f"architecture policy: {status}")
    print(f"errors: {len(result.errors)}")
    print(f"warnings: {len(result.warnings)}")
    for item in result.findings:
        path = f" {item['path']}" if item.get("path") else ""
        field = f" field={item['field']}" if item.get("field") else ""
        print(f"{item['level'].upper()}: {item['code']}:{path}{field} {item['message']}")
    if "fixtures" in result.info:
        fixtures = result.info["fixtures"].get("fixtures", [])
        print(f"fixtures: {len(fixtures)} checked")
    if "pointer_width_inventory" in result.info:
        print("pointer width inventory:")
        for key, entry in result.info["pointer_width_inventory"].items():
            print(f"  {key}: {entry['count']}")


def emit_json(result: CheckResult) -> None:
    payload = {
        "status": "PASS" if not result.errors else "FAIL",
        "findings": result.findings,
        "info": result.info,
    }
    print(json.dumps(payload, indent=2))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on architecture policy errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--fixtures", action="store_true", help="Validate architecture policy fixtures")
    parser.add_argument("--inventory", action="store_true", help="Emit descriptive pointer-width inventory")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    include_fixtures = bool(args.fixtures or args.strict)
    include_inventory = bool(args.inventory)
    result = run_checks(repo_root, include_fixtures=include_fixtures, include_inventory=include_inventory)
    if args.json:
        emit_json(result)
    else:
        emit_text(result, inventory_only=args.inventory and not args.strict)
    if args.strict and result.errors:
        return 1
    if args.fixtures and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
