"""Deterministic Ω-9 toolchain matrix helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat.capability_negotiation import (  # noqa: E402
    build_endpoint_descriptor,
    load_product_registry,
    negotiate_endpoint_descriptors,
    product_default_degrade_ladders,
    semantic_contract_rows_by_category,
    verify_negotiation_record,
)
from src.packs.compat.pack_verification_pipeline import verify_pack_set  # noqa: E402
from src.platform.platform_probe import (  # noqa: E402
    MODE_TO_CAPABILITY_ID,
    PLATFORM_CAPABILITY_KEYS,
    endpoint_descriptor_platform_snapshot,
    platform_capability_rows_by_id,
    platform_family_id,
    project_feature_capabilities_for_platform,
)
from src.release import (  # noqa: E402
    build_product_build_metadata,
    build_release_manifest,
    product_capability_default_rows_by_id,
    source_revision_id,
    verify_release_manifest,
)
from tools.convergence.convergence_gate_common import run_convergence_gate  # noqa: E402
from tools.mvp.baseline_universe_common import (  # noqa: E402
    load_baseline_universe_snapshot,
    verify_baseline_universe,
)
from tools.mvp.gameplay_loop_common import load_gameplay_snapshot  # noqa: E402
from tools.worldgen.worldgen_lock_common import (  # noqa: E402
    load_worldgen_lock_snapshot,
    verify_worldgen_lock,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


TOOLCHAIN_MATRIX_RETRO_AUDIT_REL = os.path.join("docs", "audit", "TOOLCHAIN_MATRIX0_RETRO_AUDIT.md")
TOOLCHAIN_MATRIX_MODEL_DOC_REL = os.path.join("docs", "mvp", "TOOLCHAIN_MATRIX_MODEL.md")
TOOLCHAIN_MATRIX_BASELINE_DOC_REL = os.path.join("docs", "audit", "TOOLCHAIN_MATRIX_BASELINE.md")
TOOLCHAIN_MATRIX_REGISTRY_REL = os.path.join("data", "registries", "toolchain_matrix_registry.json")
TOOLCHAIN_TEST_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "toolchain_test_profile_registry.json")
DEFAULT_TOOLCHAIN_RUNS_REL = os.path.join("artifacts", "toolchain_runs")

TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID = "dominium.registry.toolchain_matrix_registry"
TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID = "dominium.registry.toolchain_test_profile_registry"
TOOLCHAIN_RUN_MANIFEST_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_run_manifest"
TOOLCHAIN_RUN_RESULTS_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_results"
TOOLCHAIN_ENV_REPORT_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_env_report"
TOOLCHAIN_HASHES_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_hashes"
TOOLCHAIN_BUILD_IDS_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_build_ids"
TOOLCHAIN_ENDPOINT_DESCRIPTORS_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_endpoint_descriptors"
TOOLCHAIN_COMPARE_SCHEMA_ID = "dominium.schema.audit.toolchain_matrix_compare"

DEFAULT_ENV_ID = "winnt-msvc-x86_64-vs2026"
DEFAULT_PROFILE_ID = "toolchain.full"
RUN_ID_PREFIX = "run."
RUN_STEP_IDS = (
    "smoke.build_ids",
    "smoke.endpoint_descriptors",
    "smoke.release_manifest",
    "determinism_core.worldgen_lock",
    "determinism_core.baseline_universe",
    "ecosystem.pack_verify",
    "ecosystem.negotiation_smoke",
    "distribution.release_manifest_verify",
    "heavy.convergence_gate",
)
RUN_STEP_DESCRIPTIONS = {
    "smoke.build_ids": "compute deterministic build ids from the env descriptor and source identity",
    "smoke.endpoint_descriptors": "emit deterministic endpoint descriptors for the environment-supported product set",
    "smoke.release_manifest": "rebuild the release manifest for a matching dist root when packaging is present",
    "determinism_core.worldgen_lock": "rerun WORLDGEN-LOCK-0 verification",
    "determinism_core.baseline_universe": "rerun BASELINE-UNIVERSE-0 verification",
    "ecosystem.pack_verify": "run deterministic pack verification against the governed repo surface",
    "ecosystem.negotiation_smoke": "negotiate client/server endpoint descriptors and verify the negotiation record",
    "distribution.release_manifest_verify": "verify the committed release manifest when a dist root is present",
    "heavy.convergence_gate": "optionally rerun the convergence gate with cross-platform lanes disabled",
}
_DOC_ENV_IDS = (
    "winnt-msvc-x86_64-vs2026",
    "winxp-msvc-x86_32-legacy",
    "win7-msvc-x86_64",
    "win8_1-msvc-x86_64",
    "linux-gcc-x86_64-debian13",
    "linux-gcc-x86_64-arch",
    "linux-gcc-x86_64-fedora",
    "macosx-clang-x86_64-10_14",
    "macosx-clang-x86_64-10_6",
)
_DOC_PROFILE_IDS = (
    "toolchain.smoke",
    "toolchain.determinism_core",
    "toolchain.ecosystem",
    "toolchain.full",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _as_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    token = _token(value).lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(default)


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted({_token(item) for item in list(values or []) if _token(item)})


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return _norm(repo_root)
    if os.path.isabs(token):
        return _norm(token)
    return _norm(os.path.join(repo_root, token.replace("/", os.sep)))


def _relative_to(repo_root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    try:
        return _norm_rel(os.path.relpath(_norm(token), _norm(repo_root)))
    except ValueError:
        return _norm_rel(token)


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    _ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    _ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _load_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _sha256_file(path: str) -> str:
    try:
        with open(_norm(path), "rb") as handle:
            data = handle.read()
    except OSError:
        return ""
    return canonical_sha256({"bytes_sha256": data.hex()})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def _stability(*, rationale: str, replacement_target: str, future_series: str = "DIST/PLATFORM") -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": "provisional",
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": "",
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def canonicalize_toolchain_env_row(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    normalized = {
        "env_id": _token(row.get("env_id")),
        "display_name": _token(row.get("display_name")),
        "os_id": _token(row.get("os_id")),
        "arch_id": _token(row.get("arch_id")),
        "abi_id": _token(row.get("abi_id")),
        "compiler_id": _token(row.get("compiler_id")),
        "compiler_version": _token(row.get("compiler_version")),
        "toolchain_constraints": dict(_normalize_tree(_as_map(row.get("toolchain_constraints")))),
        "supported_products": _sorted_tokens(row.get("supported_products")),
        "supported_profile_ids": _sorted_tokens(row.get("supported_profile_ids")),
        "stability": dict(_normalize_tree(_as_map(row.get("stability")))),
        "extensions": dict(_normalize_tree(_as_map(row.get("extensions")))),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
    }
    normalized["deterministic_fingerprint"] = _fingerprint(normalized)
    return normalized


def canonicalize_toolchain_profile_row(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    normalized = {
        "profile_id": _token(row.get("profile_id")),
        "display_name": _token(row.get("display_name")),
        "description": _token(row.get("description")),
        "step_ids": [item for item in list(row.get("step_ids") or []) if _token(item)],
        "required_step_ids": _sorted_tokens(row.get("required_step_ids")),
        "optional_step_ids": _sorted_tokens(row.get("optional_step_ids")),
        "stability": dict(_normalize_tree(_as_map(row.get("stability")))),
        "extensions": dict(_normalize_tree(_as_map(row.get("extensions")))),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
    }
    normalized["deterministic_fingerprint"] = _fingerprint(normalized)
    return normalized


def canonicalize_toolchain_matrix_registry(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    record = _as_map(item.get("record"))
    environments = sorted(
        (
            canonicalize_toolchain_env_row(row)
            for row in _as_list(record.get("environments"))
            if _token(_as_map(row).get("env_id"))
        ),
        key=lambda row: _token(row.get("env_id")),
    )
    normalized_record = {
        "registry_id": _token(record.get("registry_id")) or TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
        "registry_version": _token(record.get("registry_version")) or "1.0.0",
        "environments": environments,
        "extensions": dict(_normalize_tree(_as_map(record.get("extensions")))),
        "deterministic_fingerprint": _token(record.get("deterministic_fingerprint")),
    }
    normalized_record["deterministic_fingerprint"] = _fingerprint(normalized_record)
    return {
        "schema_id": _token(item.get("schema_id")) or TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
        "schema_version": _token(item.get("schema_version")) or "1.0.0",
        "record": normalized_record,
    }


def canonicalize_toolchain_test_profile_registry(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    record = _as_map(item.get("record"))
    profiles = sorted(
        (
            canonicalize_toolchain_profile_row(row)
            for row in _as_list(record.get("profiles"))
            if _token(_as_map(row).get("profile_id"))
        ),
        key=lambda row: _token(row.get("profile_id")),
    )
    normalized_record = {
        "registry_id": _token(record.get("registry_id")) or TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
        "registry_version": _token(record.get("registry_version")) or "1.0.0",
        "profiles": profiles,
        "extensions": dict(_normalize_tree(_as_map(record.get("extensions")))),
        "deterministic_fingerprint": _token(record.get("deterministic_fingerprint")),
    }
    normalized_record["deterministic_fingerprint"] = _fingerprint(normalized_record)
    return {
        "schema_id": _token(item.get("schema_id")) or TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
        "schema_version": _token(item.get("schema_version")) or "1.0.0",
        "record": normalized_record,
    }


def _default_env_rows() -> list[dict]:
    full_products = ["client", "engine", "game", "launcher", "server", "setup"]
    all_profiles = list(_DOC_PROFILE_IDS)
    env_rows = [
        {
            "env_id": "winnt-msvc-x86_64-vs2026",
            "display_name": "Windows NT x86_64 / MSVC 2026",
            "os_id": "winnt",
            "arch_id": "x86_64",
            "abi_id": "msvc",
            "compiler_id": "msvc",
            "compiler_version": "2026",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++20", "c++23"],
                "notes": ["primary shipped mock lane", "deterministic reference bundle currently exists"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Current shipped mock lane and primary Ω-9 reference environment.",
                replacement_target="Replace with release-index pinned toolchain contracts once native multi-host CI exists.",
            ),
            "extensions": {
                "canonical_os_id": "os.winnt",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.msvc",
                "platform_id": "platform.winnt",
                "platform_tag": "win64",
                "target_matrix_target_id": "target.os_winnt.abi_msvc.arch_x86_64",
                "target_matrix_reference_mode": "canonical_match",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "dist/v0.0.0-mock/win64/dominium",
                "release_manifest_rel": "dist/v0.0.0-mock/win64/dominium/manifests/release_manifest.json",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "winxp-msvc-x86_32-legacy",
            "display_name": "Windows XP x86_32 / MSVC legacy",
            "os_id": "winxp",
            "arch_id": "x86_32",
            "abi_id": "msvc",
            "compiler_id": "msvc",
            "compiler_version": "legacy",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++03", "c++11"],
                "notes": ["legacy compatibility lane", "no committed dist bundle in current repo state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Legacy Win32 validation lane is planned but not a Tier 1 shipment commitment.",
                replacement_target="Replace once a Win32 legacy bundle is produced and validated under clean-room rules.",
            ),
            "extensions": {
                "canonical_os_id": "os.winnt",
                "canonical_arch_id": "arch.x86_32",
                "canonical_abi_id": "abi.msvc",
                "platform_id": "platform.winnt",
                "platform_tag": "win32",
                "target_matrix_target_id": "target.os_winnt.abi_msvc.arch_x86_32",
                "target_matrix_reference_mode": "canonical_match",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {
                    "cap.ui.os_native": False,
                },
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "win7-msvc-x86_64",
            "display_name": "Windows 7 x86_64 / MSVC",
            "os_id": "win7",
            "arch_id": "x86_64",
            "abi_id": "msvc",
            "compiler_id": "msvc",
            "compiler_version": "2019+",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++17", "c++20"],
                "notes": ["retro NT-family verification lane", "no committed dist bundle in current repo state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Windows 7 remains a provisional verification environment only.",
                replacement_target="Replace with release-pinned Win7 legacy policy if the distribution line is revived.",
            ),
            "extensions": {
                "canonical_os_id": "os.winnt",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.msvc",
                "platform_id": "platform.winnt",
                "platform_tag": "win64",
                "target_matrix_target_id": "target.os_winnt.abi_msvc.arch_x86_64",
                "target_matrix_reference_mode": "family_projection",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "win8_1-msvc-x86_64",
            "display_name": "Windows 8.1 x86_64 / MSVC",
            "os_id": "win8_1",
            "arch_id": "x86_64",
            "abi_id": "msvc",
            "compiler_id": "msvc",
            "compiler_version": "2022+",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++17", "c++20"],
                "notes": ["NT-family verification lane", "no committed dist bundle in current repo state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Windows 8.1 remains a provisional verification environment only.",
                replacement_target="Replace if a dedicated 8.1 compatibility contract is ever promoted.",
            ),
            "extensions": {
                "canonical_os_id": "os.winnt",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.msvc",
                "platform_id": "platform.winnt",
                "platform_tag": "win64",
                "target_matrix_target_id": "target.os_winnt.abi_msvc.arch_x86_64",
                "target_matrix_reference_mode": "family_projection",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "linux-gcc-x86_64-debian13",
            "display_name": "Linux x86_64 / GCC 14 / Debian 13",
            "os_id": "linux",
            "arch_id": "x86_64",
            "abi_id": "glibc",
            "compiler_id": "gcc",
            "compiler_version": "14",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++20", "c++23"],
                "notes": ["Tier 1 policy target when a Linux bundle is actually built"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Debian 13 is a planned Linux validation lane, not a shipped mock bundle in current state.",
                replacement_target="Replace after Linux clean-room and DIST publication lanes are committed.",
            ),
            "extensions": {
                "canonical_os_id": "os.linux",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.glibc",
                "platform_id": "platform.linux_gtk",
                "platform_tag": "linux-x86_64",
                "target_matrix_target_id": "target.os_linux.abi_glibc.arch_x86_64",
                "target_matrix_reference_mode": "canonical_match",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "linux-gcc-x86_64-arch",
            "display_name": "Linux x86_64 / GCC 14 / Arch",
            "os_id": "linux",
            "arch_id": "x86_64",
            "abi_id": "glibc",
            "compiler_id": "gcc",
            "compiler_version": "14",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++20", "c++23"],
                "notes": ["rolling Linux validation lane", "not a shipped mock bundle in current state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Arch is a provisional rolling-release verification lane only.",
                replacement_target="Replace if a rolling Linux support policy is ever formally pinned.",
            ),
            "extensions": {
                "canonical_os_id": "os.linux",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.glibc",
                "platform_id": "platform.linux_gtk",
                "platform_tag": "linux-x86_64",
                "target_matrix_target_id": "target.os_linux.abi_glibc.arch_x86_64",
                "target_matrix_reference_mode": "canonical_match",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "linux-gcc-x86_64-fedora",
            "display_name": "Linux x86_64 / GCC 14 / Fedora",
            "os_id": "linux",
            "arch_id": "x86_64",
            "abi_id": "glibc",
            "compiler_id": "gcc",
            "compiler_version": "14",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++20", "c++23"],
                "notes": ["RPM-family validation lane", "not a shipped mock bundle in current state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="Fedora is a provisional RPM-family verification lane only.",
                replacement_target="Replace after Linux release bundles and clean-room validation are committed.",
            ),
            "extensions": {
                "canonical_os_id": "os.linux",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.glibc",
                "platform_id": "platform.linux_gtk",
                "platform_tag": "linux-x86_64",
                "target_matrix_target_id": "target.os_linux.abi_glibc.arch_x86_64",
                "target_matrix_reference_mode": "canonical_match",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "macosx-clang-x86_64-10_14",
            "display_name": "macOS 10.14 x86_64 / Clang 12",
            "os_id": "macosx",
            "arch_id": "x86_64",
            "abi_id": "cocoa",
            "compiler_id": "clang",
            "compiler_version": "12",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++17", "c++20"],
                "notes": ["retro Cocoa verification lane", "no committed x86_64 macOS bundle in current repo state"],
            },
            "supported_products": full_products,
            "supported_profile_ids": all_profiles,
            "stability": _stability(
                rationale="macOS x86_64 10.14 remains a provisional verification lane only.",
                replacement_target="Replace after a real macOS x86_64 bundle and clean-room lane exist.",
            ),
            "extensions": {
                "canonical_os_id": "os.macosx",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.cocoa",
                "platform_id": "platform.macos_cocoa",
                "platform_tag": "macos-x86_64",
                "target_matrix_target_id": "",
                "target_matrix_reference_mode": "family_projection",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {},
                "official.source": "OMEGA-9",
            },
        },
        {
            "env_id": "macosx-clang-x86_64-10_6",
            "display_name": "macOS 10.6 x86_64 / Clang legacy",
            "os_id": "macosx",
            "arch_id": "x86_64",
            "abi_id": "cocoa",
            "compiler_id": "clang",
            "compiler_version": "legacy",
            "toolchain_constraints": {
                "cpp_standard_ids": ["c++03", "c++11"],
                "notes": ["best-effort legacy lane", "if possible only", "no committed bundle in current repo state"],
            },
            "supported_products": ["engine", "launcher", "server", "setup"],
            "supported_profile_ids": ["toolchain.smoke", "toolchain.determinism_core"],
            "stability": _stability(
                rationale="macOS 10.6 remains a best-effort provisional lane and is not a release commitment.",
                replacement_target="Replace only if an actual 10.6-capable toolchain and bundle line are restored.",
            ),
            "extensions": {
                "canonical_os_id": "os.macosx",
                "canonical_arch_id": "arch.x86_64",
                "canonical_abi_id": "abi.cocoa",
                "platform_id": "platform.macos_cocoa",
                "platform_tag": "macos-x86_64-legacy",
                "target_matrix_target_id": "",
                "target_matrix_reference_mode": "family_projection",
                "release_id": "v0.0.0-mock",
                "dist_root_rel": "",
                "release_manifest_rel": "",
                "capability_overrides": {
                    "cap.ui.os_native": False,
                },
                "official.source": "OMEGA-9",
            },
        },
    ]
    return [canonicalize_toolchain_env_row(row) for row in env_rows]


def _default_profile_rows() -> list[dict]:
    profiles = [
        {
            "profile_id": "toolchain.smoke",
            "display_name": "Smoke",
            "description": "Build identity and descriptor emission for an environment, with release-manifest generation when a dist root exists.",
            "step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "smoke.release_manifest",
            ],
            "required_step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
            ],
            "optional_step_ids": [
                "smoke.release_manifest",
            ],
            "stability": _stability(
                rationale="Toolchain test profile registry row for smoke validation coverage; support artifact remains provisional.",
                replacement_target="toolchain matrix and CI profile consolidation",
                future_series="TOOLCHAIN",
            ),
            "extensions": {
                "official.source": "OMEGA-9",
            },
        },
        {
            "profile_id": "toolchain.determinism_core",
            "display_name": "Determinism Core",
            "description": "Smoke tests plus WORLDGEN-LOCK and BASELINE-UNIVERSE short-window verification.",
            "step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "smoke.release_manifest",
                "determinism_core.worldgen_lock",
                "determinism_core.baseline_universe",
            ],
            "required_step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "determinism_core.worldgen_lock",
                "determinism_core.baseline_universe",
            ],
            "optional_step_ids": [
                "smoke.release_manifest",
            ],
            "stability": _stability(
                rationale="Toolchain test profile registry row for determinism-core validation coverage; support artifact remains provisional.",
                replacement_target="toolchain matrix and CI profile consolidation",
                future_series="TOOLCHAIN",
            ),
            "extensions": {
                "official.source": "OMEGA-9",
            },
        },
        {
            "profile_id": "toolchain.ecosystem",
            "display_name": "Ecosystem",
            "description": "Determinism-core plus deterministic pack verification and negotiation handshake smoke.",
            "step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "smoke.release_manifest",
                "determinism_core.worldgen_lock",
                "determinism_core.baseline_universe",
                "ecosystem.pack_verify",
                "ecosystem.negotiation_smoke",
            ],
            "required_step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "determinism_core.worldgen_lock",
                "determinism_core.baseline_universe",
                "ecosystem.pack_verify",
                "ecosystem.negotiation_smoke",
            ],
            "optional_step_ids": [
                "smoke.release_manifest",
            ],
            "stability": _stability(
                rationale="Toolchain test profile registry row for ecosystem validation coverage; support artifact remains provisional.",
                replacement_target="toolchain matrix and CI profile consolidation",
                future_series="TOOLCHAIN",
            ),
            "extensions": {
                "official.source": "OMEGA-9",
            },
        },
        {
            "profile_id": "toolchain.full",
            "display_name": "Full",
            "description": "Ecosystem coverage plus dist verification when packaging exists and optional heavy convergence replay.",
            "step_ids": list(RUN_STEP_IDS),
            "required_step_ids": [
                "smoke.build_ids",
                "smoke.endpoint_descriptors",
                "determinism_core.worldgen_lock",
                "determinism_core.baseline_universe",
                "ecosystem.pack_verify",
                "ecosystem.negotiation_smoke",
            ],
            "optional_step_ids": [
                "smoke.release_manifest",
                "distribution.release_manifest_verify",
                "heavy.convergence_gate",
            ],
            "stability": _stability(
                rationale="Toolchain test profile registry row for full validation coverage; support artifact remains provisional.",
                replacement_target="toolchain matrix and CI profile consolidation",
                future_series="TOOLCHAIN",
            ),
            "extensions": {
                "allow_heavy_default": False,
                "official.source": "OMEGA-9",
            },
        },
    ]
    return [canonicalize_toolchain_profile_row(row) for row in profiles]


def build_default_toolchain_matrix_registry() -> dict:
    return canonicalize_toolchain_matrix_registry(
        {
            "schema_id": TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
            "schema_version": "1.0.0",
            "record": {
                "registry_id": TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
                "registry_version": "1.0.0",
                "environments": _default_env_rows(),
                "extensions": {
                    "official.source": "OMEGA-9",
                    "target_matrix_registry_rel": "data/registries/target_matrix_registry.json",
                    "platform_capability_registry_rel": "data/registries/platform_capability_registry.json",
                    "run_id_rule": "hash(env_descriptor + profile_descriptor + git_revision_or_source_snapshot_hash)",
                },
            },
        }
    )


def build_default_toolchain_test_profile_registry() -> dict:
    return canonicalize_toolchain_test_profile_registry(
        {
            "schema_id": TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
            "schema_version": "1.0.0",
            "record": {
                "registry_id": TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
                "registry_version": "1.0.0",
                "profiles": _default_profile_rows(),
                "extensions": {
                    "official.source": "OMEGA-9",
                    "step_catalog": {
                        step_id: RUN_STEP_DESCRIPTIONS[step_id]
                        for step_id in RUN_STEP_IDS
                    },
                },
            },
        }
    )


def load_toolchain_matrix_registry(repo_root: str) -> dict:
    return canonicalize_toolchain_matrix_registry(_load_json(_repo_abs(repo_root, TOOLCHAIN_MATRIX_REGISTRY_REL)))


def load_toolchain_test_profile_registry(repo_root: str) -> dict:
    return canonicalize_toolchain_test_profile_registry(_load_json(_repo_abs(repo_root, TOOLCHAIN_TEST_PROFILE_REGISTRY_REL)))


def toolchain_matrix_registry_hash(repo_root: str) -> str:
    payload = load_toolchain_matrix_registry(repo_root)
    return canonical_sha256(payload) if payload else ""


def toolchain_test_profile_registry_hash(repo_root: str) -> str:
    payload = load_toolchain_test_profile_registry(repo_root)
    return canonical_sha256(payload) if payload else ""


def env_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload = load_toolchain_matrix_registry(repo_root)
    out: dict[str, dict] = {}
    for row in _as_list(_as_map(payload.get("record")).get("environments")):
        item = _as_map(row)
        env_id = _token(item.get("env_id"))
        if env_id:
            out[env_id] = item
    return dict((key, out[key]) for key in sorted(out.keys()))


def profile_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload = load_toolchain_test_profile_registry(repo_root)
    out: dict[str, dict] = {}
    for row in _as_list(_as_map(payload.get("record")).get("profiles")):
        item = _as_map(row)
        profile_id = _token(item.get("profile_id"))
        if profile_id:
            out[profile_id] = item
    return dict((key, out[key]) for key in sorted(out.keys()))


def select_env_row(repo_root: str, env_id: str) -> dict:
    return dict(env_rows_by_id(repo_root).get(_token(env_id)) or {})


def select_profile_row(repo_root: str, profile_id: str) -> dict:
    return dict(profile_rows_by_id(repo_root).get(_token(profile_id)) or {})


def _source_snapshot_hash(repo_root: str) -> str:
    snapshot_paths = [
        "tools/mvp/toolchain_matrix_common.py",
        "tools/mvp/tool_run_toolchain_matrix.py",
        "tools/mvp/tool_compare_toolchain_runs.py",
        "data/registries/semantic_contract_registry.json",
        "data/registries/platform_capability_registry.json",
        "data/registries/product_capability_defaults.json",
        "data/registries/product_registry.json",
        "data/registries/worldgen_lock_registry.json",
        "data/registries/toolchain_matrix_registry.json",
        "data/registries/toolchain_test_profile_registry.json",
        "data/baselines/worldgen/baseline_worldgen_snapshot.json",
        "data/baselines/universe/baseline_universe_snapshot.json",
        "data/baselines/gameplay/gameplay_loop_snapshot.json",
        "data/regression/disaster_suite_baseline.json",
        "data/regression/ecosystem_verify_baseline.json",
        "data/regression/update_sim_baseline.json",
        "data/regression/trust_strict_baseline.json",
    ]
    rows = []
    for rel_path in snapshot_paths:
        abs_path = _repo_abs(repo_root, rel_path)
        if not os.path.exists(abs_path):
            continue
        rows.append(
            {
                "path": _norm_rel(rel_path),
                "content_hash": _sha256_file(abs_path),
            }
        )
    return canonical_sha256(rows)


def build_run_input_payload(repo_root: str, env_row: Mapping[str, object], profile_row: Mapping[str, object]) -> dict:
    root = _norm(repo_root)
    snapshot_hash = _source_snapshot_hash(root)
    return {
        "env_descriptor_hash": _token(_as_map(env_row).get("deterministic_fingerprint")),
        "profile_descriptor_hash": _token(_as_map(profile_row).get("deterministic_fingerprint")),
        "toolchain_matrix_registry_hash": toolchain_matrix_registry_hash(root),
        "toolchain_test_profile_registry_hash": toolchain_test_profile_registry_hash(root),
        "source_revision_id": "",
        "source_snapshot_hash": _token(snapshot_hash),
        "source_identity_kind": "snapshot",
        "git_revision_hint": _token(source_revision_id(root)),
    }


def build_run_id(repo_root: str, env_row: Mapping[str, object], profile_row: Mapping[str, object]) -> tuple[str, dict]:
    payload = build_run_input_payload(repo_root, env_row, profile_row)
    fingerprint = canonical_sha256(payload)
    return "{}{}".format(RUN_ID_PREFIX, fingerprint[:16]), dict(payload, run_input_fingerprint=fingerprint)


def _platform_row(repo_root: str, platform_id: str) -> dict:
    rows, _error = platform_capability_rows_by_id(repo_root)
    return dict(rows.get(_token(platform_id)) or {})


def _mode_ids_for_capabilities(capability_flags: Mapping[str, object]) -> list[str]:
    enabled = {key for key, value in dict(capability_flags or {}).items() if bool(value)}
    out = [
        mode_id
        for mode_id, capability_id in sorted(MODE_TO_CAPABILITY_ID.items(), key=lambda item: str(item[0]))
        if capability_id in enabled
    ]
    return out


def build_env_platform_descriptor(repo_root: str, env_row: Mapping[str, object], *, product_id: str = "") -> dict:
    env = _as_map(env_row)
    env_extensions = _as_map(env.get("extensions"))
    platform_id = _token(env_extensions.get("platform_id"))
    row = _platform_row(repo_root, platform_id)
    capability_flags = {
        capability_id: bool(row.get(capability_id, False))
        for capability_id in PLATFORM_CAPABILITY_KEYS
    }
    capability_flags.update(
        {
            str(key): bool(value)
            for key, value in _as_map(env_extensions.get("capability_overrides")).items()
        }
    )
    supported_capability_ids = sorted(key for key, value in capability_flags.items() if bool(value))
    supported_mode_ids = _mode_ids_for_capabilities(capability_flags)
    renderer_backend_ids = []
    if capability_flags.get("cap.renderer.software"):
        renderer_backend_ids.append("software")
    if capability_flags.get("cap.renderer.null"):
        renderer_backend_ids.append("null")
    if capability_flags.get("cap.renderer.opengl"):
        renderer_backend_ids.append("opengl")
    if capability_flags.get("cap.renderer.directx"):
        renderer_backend_ids.append("directx")
    if capability_flags.get("cap.renderer.vulkan"):
        renderer_backend_ids.append("vulkan")
    if capability_flags.get("cap.renderer.metal"):
        renderer_backend_ids.append("metal")
    ipc_transport_ids = []
    if capability_flags.get("cap.ipc.named_pipe"):
        ipc_transport_ids.append("named_pipe")
    if capability_flags.get("cap.ipc.local_socket"):
        ipc_transport_ids.append("local_socket")
    payload = {
        "schema_version": "1.0.0",
        "result": "complete",
        "product_id": _token(product_id),
        "platform_id": platform_id,
        "display_name": _token(row.get("display_name")) or _token(env.get("display_name")),
        "platform_family_id": platform_family_id(platform_id),
        "support_tier": _token(row.get("support_tier")) or "full",
        "display_present": bool(capability_flags.get("cap.ui.rendered") or capability_flags.get("cap.ui.os_native")),
        "tty_present": bool(capability_flags.get("cap.ui.tui") or capability_flags.get("cap.ui.cli")),
        "gui_environment_available": bool(capability_flags.get("cap.ui.rendered") or capability_flags.get("cap.ui.os_native")),
        "stdin_tty": False,
        "stdout_tty": False,
        "stderr_tty": False,
        "wayland_present": False,
        "windows_console_window_present": False,
        "ncurses_runtime_available": bool(capability_flags.get("cap.ui.tui")),
        "cocoa_runtime_available": platform_family_id(platform_id) == "macos",
        "supported_capability_flags": capability_flags,
        "supported_capability_ids": supported_capability_ids,
        "supported_mode_ids": supported_mode_ids,
        "available_mode_ids": list(supported_mode_ids),
        "available_modes": {
            "os_native": "os_native" in supported_mode_ids,
            "rendered": "rendered" in supported_mode_ids,
            "tui": "tui" in supported_mode_ids,
            "cli": "cli" in supported_mode_ids,
        },
        "renderer_backend_ids": sorted(set(renderer_backend_ids)),
        "ipc_transport_ids": sorted(set(ipc_transport_ids)),
        "extensions": {
            "registry_row": row,
            "env_id": _token(env.get("env_id")),
            "target_matrix_target_id": _token(env_extensions.get("target_matrix_target_id")),
            "platform_tag": _token(env_extensions.get("platform_tag")),
            "canonical_os_id": _token(env_extensions.get("canonical_os_id")),
            "canonical_arch_id": _token(env_extensions.get("canonical_arch_id")),
            "canonical_abi_id": _token(env_extensions.get("canonical_abi_id")),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _product_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload, error = load_product_registry(repo_root)
    if error:
        return {}
    out: dict[str, dict] = {}
    for row in _as_list(_as_map(payload.get("record")).get("products")):
        item = _as_map(row)
        product_id = _token(item.get("product_id"))
        if product_id:
            out[product_id] = item
    return dict((key, out[key]) for key in sorted(out.keys()))


def _semantic_contract_ranges(repo_root: str) -> list[dict]:
    rows_by_category, _error = semantic_contract_rows_by_category(repo_root)
    out = []
    for category_id in sorted(rows_by_category.keys()):
        row = _as_map(rows_by_category.get(category_id))
        version = int(row.get("version", 1) or 1)
        item = {
            "schema_version": "1.0.0",
            "contract_category_id": category_id,
            "min_version": version,
            "max_version": version,
            "extensions": {},
            "deterministic_fingerprint": "",
        }
        item["deterministic_fingerprint"] = _fingerprint(item)
        out.append(item)
    return out


def _merged_semantic_contract_ranges(repo_root: str, product_rows: object) -> list[dict]:
    rows_by_category = {
        _token(row.get("contract_category_id")): row
        for row in _semantic_contract_ranges(repo_root)
        if _token(_as_map(row).get("contract_category_id"))
    }
    for item in _as_list(product_rows):
        row = _as_map(item)
        contract_category_id = _token(row.get("contract_category_id"))
        if contract_category_id:
            rows_by_category[contract_category_id] = row
    return [dict(rows_by_category[key]) for key in sorted(rows_by_category.keys())]


def build_env_product_descriptor(repo_root: str, env_row: Mapping[str, object], *, product_id: str) -> dict:
    root = _norm(repo_root)
    env = _as_map(env_row)
    env_extensions = _as_map(env.get("extensions"))
    product_rows = _product_rows_by_id(root)
    defaults_rows, _error = product_capability_default_rows_by_id(root)
    product_row = _as_map(product_rows.get(_token(product_id)))
    defaults_row = _as_map(defaults_rows.get(_token(product_id)))
    if not product_row or not defaults_row:
        raise ValueError("unknown toolchain descriptor product_id '{}'".format(_token(product_id)))
    platform_descriptor = build_env_platform_descriptor(root, env, product_id=_token(product_id))
    build_meta = build_product_build_metadata(
        root,
        _token(product_id),
        platform_tag=_token(env_extensions.get("platform_tag")),
        source_revision_id_override=_source_snapshot_hash(root),
    )
    platform_snapshot = endpoint_descriptor_platform_snapshot(platform_descriptor)
    descriptor_extensions = dict(_as_map(product_row.get("extensions")))
    descriptor_extensions.update(_as_map(defaults_row.get("extensions")))
    descriptor_extensions.update(
        {
            "official.build_id": _token(build_meta.get("build_id")),
            "official.inputs_hash": _token(build_meta.get("inputs_hash")),
            "official.git_commit_hash": _token(build_meta.get("git_commit_hash")),
            "official.semantic_contract_registry_hash": _token(build_meta.get("semantic_contract_registry_hash")),
            "official.compilation_options_hash": _token(build_meta.get("compilation_options_hash")),
            "official.source_revision_id": _token(build_meta.get("source_revision_id")),
            "official.explicit_build_number": _token(build_meta.get("explicit_build_number")),
            "official.platform_tag": _token(env_extensions.get("platform_tag")),
            "official.build_configuration": _token(build_meta.get("build_configuration")),
            "official.build_input_selection": _token(_as_map(build_meta.get("extensions")).get("official.build_input_selection")),
            "official.platform_id": _token(env_extensions.get("platform_id")),
            "official.platform_descriptor_hash": _token(platform_snapshot.get("deterministic_fingerprint")),
            "official.platform_capability_ids": list(platform_descriptor.get("supported_capability_ids") or []),
            "official.platform_descriptor": dict(platform_snapshot),
            "official.target_id": _token(env_extensions.get("target_matrix_target_id")),
            "official.os_id": _token(env_extensions.get("canonical_os_id")),
            "official.arch_id": _token(env_extensions.get("canonical_arch_id")),
            "official.abi_id": _token(env_extensions.get("canonical_abi_id")),
            "official.toolchain_env_id": _token(env.get("env_id")),
        }
    )
    resolved_version = "{}+{}".format(
        _token(_as_map(product_row.get("extensions")).get("official.default_semver")) or "0.0.0",
        _token(build_meta.get("build_id")),
    )
    return build_endpoint_descriptor(
        product_id=_token(product_id),
        product_version=resolved_version,
        protocol_versions_supported=_as_list(defaults_row.get("protocol_versions_supported")),
        semantic_contract_versions_supported=_merged_semantic_contract_ranges(
            root,
            defaults_row.get("semantic_contract_versions_supported"),
        ),
        feature_capabilities=project_feature_capabilities_for_platform(
            _as_list(defaults_row.get("feature_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        required_capabilities=project_feature_capabilities_for_platform(
            _as_list(defaults_row.get("required_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        optional_capabilities=project_feature_capabilities_for_platform(
            _as_list(defaults_row.get("optional_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        degrade_ladders=product_default_degrade_ladders(root, _token(product_id))
        or _as_list(defaults_row.get("degrade_ladders")),
        extensions=descriptor_extensions,
    )


def endpoint_descriptor_semantic_hash(descriptor: Mapping[str, object]) -> str:
    item = _as_map(descriptor)
    extensions = _as_map(item.get("extensions"))
    payload = {
        "product_id": _token(item.get("product_id")),
        "protocol_versions_supported": _as_list(item.get("protocol_versions_supported")),
        "semantic_contract_versions_supported": _as_list(item.get("semantic_contract_versions_supported")),
        "feature_capabilities": _as_list(item.get("feature_capabilities")),
        "required_capabilities": _as_list(item.get("required_capabilities")),
        "optional_capabilities": _as_list(item.get("optional_capabilities")),
        "degrade_ladders": _as_list(item.get("degrade_ladders")),
        "official.platform_id": _token(extensions.get("official.platform_id")),
        "official.os_id": _token(extensions.get("official.os_id")),
        "official.arch_id": _token(extensions.get("official.arch_id")),
        "official.abi_id": _token(extensions.get("official.abi_id")),
        "official.target_id": _token(extensions.get("official.target_id")),
        "official.platform_capability_ids": _as_list(extensions.get("official.platform_capability_ids")),
    }
    return canonical_sha256(payload)


def _descriptor_projection_row(descriptor: Mapping[str, object]) -> dict:
    item = _as_map(descriptor)
    extensions = _as_map(item.get("extensions"))
    return {
        "product_id": _token(item.get("product_id")),
        "build_id": _token(extensions.get("official.build_id")),
        "endpoint_descriptor_hash": canonical_sha256(item),
        "semantic_hash": endpoint_descriptor_semantic_hash(item),
        "descriptor": item,
    }


def _build_ids_payload(repo_root: str, env_row: Mapping[str, object], profile_row: Mapping[str, object]) -> dict:
    root = _norm(repo_root)
    env = _as_map(env_row)
    env_extensions = _as_map(env.get("extensions"))
    entries = []
    for product_id in _sorted_tokens(env.get("supported_products")):
        build_meta = build_product_build_metadata(
            root,
            product_id,
            platform_tag=_token(env_extensions.get("platform_tag")),
            source_revision_id_override=_source_snapshot_hash(root),
        )
        entries.append(
            {
                "product_id": product_id,
                "build_id": _token(build_meta.get("build_id")),
                "inputs_hash": _token(build_meta.get("inputs_hash")),
                "compilation_options_hash": _token(build_meta.get("compilation_options_hash")),
                "platform_tag": _token(env_extensions.get("platform_tag")),
                "source_revision_id": _token(build_meta.get("source_revision_id")),
            }
        )
    payload = {
        "schema_id": TOOLCHAIN_BUILD_IDS_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(env.get("env_id")),
        "profile_id": _token(profile_row.get("profile_id")),
        "entries": sorted(entries, key=lambda row: _token(row.get("product_id"))),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _endpoint_descriptors_payload(repo_root: str, env_row: Mapping[str, object], profile_row: Mapping[str, object]) -> dict:
    env = _as_map(env_row)
    projections = [
        _descriptor_projection_row(build_env_product_descriptor(repo_root, env_row, product_id=product_id))
        for product_id in _sorted_tokens(env.get("supported_products"))
    ]
    payload = {
        "schema_id": TOOLCHAIN_ENDPOINT_DESCRIPTORS_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(env.get("env_id")),
        "profile_id": _token(profile_row.get("profile_id")),
        "entries": sorted(projections, key=lambda row: _token(row.get("product_id"))),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _worldgen_snapshot_hash(repo_root: str) -> str:
    payload = load_worldgen_lock_snapshot(repo_root)
    record = _as_map(payload.get("record"))
    return _token(record.get("deterministic_fingerprint")) or canonical_sha256(payload)


def _baseline_universe_hash(repo_root: str) -> str:
    payload = load_baseline_universe_snapshot(repo_root)
    record = _as_map(payload.get("record"))
    return _token(record.get("deterministic_fingerprint")) or canonical_sha256(payload)


def _gameplay_snapshot_hash(repo_root: str) -> str:
    payload = load_gameplay_snapshot(repo_root)
    record = _as_map(payload.get("record"))
    return _token(record.get("deterministic_fingerprint")) or canonical_sha256(payload)


def _proof_anchor_hashes(repo_root: str) -> dict[str, str]:
    payload = load_baseline_universe_snapshot(repo_root)
    record = _as_map(payload.get("record"))
    out: dict[str, str] = {}
    for row in _as_list(record.get("proof_anchors")):
        item = _as_map(row)
        checkpoint_id = _token(item.get("checkpoint_id"))
        if checkpoint_id:
            out[checkpoint_id] = _token(item.get("state_hash_anchor"))
    return dict((key, out[key]) for key in sorted(out.keys()))


def _release_manifest_projection_hash(payload: Mapping[str, object]) -> str:
    item = _as_map(payload)
    rows = []
    for row in _as_list(item.get("artifacts")):
        artifact = _as_map(row)
        rows.append(
            {
                "artifact_kind": _token(artifact.get("artifact_kind")),
                "artifact_name": _token(artifact.get("artifact_name")),
                "build_id": _token(artifact.get("build_id")),
                "endpoint_descriptor_hash": _token(artifact.get("endpoint_descriptor_hash")),
            }
        )
    projection = {
        "release_id": _token(item.get("release_id")),
        "release_channel": _token(item.get("release_channel")),
        "artifact_projection": sorted(
            rows,
            key=lambda row: (_token(row.get("artifact_kind")), _token(row.get("artifact_name"))),
        ),
    }
    return canonical_sha256(projection)


def _step_row(
    step_id: str,
    *,
    result: str,
    required: bool,
    summary: Mapping[str, object] | None = None,
    reason: str = "",
) -> dict:
    row = {
        "step_id": _token(step_id),
        "description": RUN_STEP_DESCRIPTIONS.get(_token(step_id), ""),
        "required": bool(required),
        "result": _token(result),
        "reason": _token(reason),
        "summary": dict(_normalize_tree(_as_map(summary))),
        "deterministic_fingerprint": "",
    }
    row["deterministic_fingerprint"] = _fingerprint(row)
    return row


def _smoke_release_manifest_step(repo_root: str, env_row: Mapping[str, object], *, required: bool) -> tuple[dict, dict]:
    env_extensions = _as_map(_as_map(env_row).get("extensions"))
    dist_root_rel = _token(env_extensions.get("dist_root_rel"))
    dist_root = _repo_abs(repo_root, dist_root_rel) if dist_root_rel else ""
    if not dist_root or not os.path.isdir(dist_root):
        return (
            _step_row(
                "smoke.release_manifest",
                result="skipped",
                required=required,
                reason="dist_root_missing",
                summary={"dist_root_rel": dist_root_rel},
            ),
            {},
        )
    payload = build_release_manifest(
        dist_root,
        platform_tag=_token(env_extensions.get("platform_tag")),
        repo_root=_norm(repo_root),
    )
    summary = {
        "dist_root_rel": _relative_to(repo_root, dist_root),
        "release_manifest_hash": canonical_sha256(payload),
        "release_manifest_projection_hash": _release_manifest_projection_hash(payload),
        "artifact_count": len(_as_list(_as_map(payload).get("artifacts"))),
        "deterministic_fingerprint": _token(_as_map(payload).get("deterministic_fingerprint")),
    }
    return (_step_row("smoke.release_manifest", result="complete", required=required, summary=summary), summary)


def _distribution_release_manifest_verify_step(repo_root: str, env_row: Mapping[str, object], *, required: bool) -> tuple[dict, dict]:
    env_extensions = _as_map(_as_map(env_row).get("extensions"))
    dist_root_rel = _token(env_extensions.get("dist_root_rel"))
    manifest_rel = _token(env_extensions.get("release_manifest_rel"))
    dist_root = _repo_abs(repo_root, dist_root_rel) if dist_root_rel else ""
    manifest_path = _repo_abs(repo_root, manifest_rel) if manifest_rel else ""
    if (not dist_root) or (not manifest_path) or (not os.path.isdir(dist_root)) or (not os.path.isfile(manifest_path)):
        return (
            _step_row(
                "distribution.release_manifest_verify",
                result="skipped",
                required=required,
                reason="dist_manifest_missing",
                summary={"dist_root_rel": dist_root_rel, "manifest_rel": manifest_rel},
            ),
            {},
        )
    report = verify_release_manifest(dist_root, manifest_path, repo_root=_norm(repo_root))
    errors = [dict(row) for row in _as_list(_as_map(report).get("errors"))]
    warnings = [dict(row) for row in _as_list(_as_map(report).get("warnings"))]
    result = "complete" if not errors else "violation"
    summary = {
        "dist_root_rel": _relative_to(repo_root, dist_root),
        "manifest_rel": _relative_to(repo_root, manifest_path),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "verified_artifact_count": int(_as_map(report).get("verified_artifact_count", 0) or 0),
        "build_id_cross_checked": int(_as_map(report).get("build_id_cross_checked", 0) or 0),
        "manifest_hash": _token(_as_map(report).get("manifest_hash")),
    }
    return (_step_row("distribution.release_manifest_verify", result=result, required=required, summary=summary), summary)


def _worldgen_verify_step(repo_root: str, *, required: bool) -> tuple[dict, dict]:
    report = verify_worldgen_lock(_norm(repo_root))
    summary = {
        "matches_snapshot": bool(_as_map(report).get("matches_snapshot")),
        "expected_snapshot_fingerprint": _token(_as_map(report).get("expected_snapshot_fingerprint")),
        "observed_snapshot_fingerprint": _token(_as_map(report).get("observed_snapshot_fingerprint")),
        "mismatched_field_count": len(_as_list(_as_map(report).get("mismatched_fields"))),
    }
    result = "complete" if _token(_as_map(report).get("result")) == "complete" else "violation"
    return (_step_row("determinism_core.worldgen_lock", result=result, required=required, summary=summary), summary)


def _baseline_universe_verify_step(repo_root: str, *, required: bool) -> tuple[dict, dict]:
    report = verify_baseline_universe(_norm(repo_root))
    summary = {
        "matches_snapshot": bool(_as_map(report).get("matches_snapshot")),
        "save_reload_matches": bool(_as_map(report).get("save_reload_matches")),
        "expected_snapshot_fingerprint": _token(_as_map(report).get("expected_snapshot_fingerprint")),
        "observed_snapshot_fingerprint": _token(_as_map(report).get("observed_snapshot_fingerprint")),
        "loaded_save_hash": _token(_as_map(report).get("loaded_save_hash")),
        "mismatched_field_count": len(_as_list(_as_map(report).get("mismatched_fields"))),
    }
    result = "complete" if _token(_as_map(report).get("result")) == "complete" else "violation"
    return (_step_row("determinism_core.baseline_universe", result=result, required=required, summary=summary), summary)


def _pack_verify_step(repo_root: str, *, required: bool) -> tuple[dict, dict]:
    verify_result = {}
    report = {}
    errors = []
    try:
        from tools.mvp.mvp_smoke_common import build_curated_pack_runtime

        curated = _as_map(build_curated_pack_runtime(_norm(repo_root)))
        verify_result = _as_map(curated.get("verify_result"))
        report = _as_map(verify_result.get("report"))
        errors = _as_list(verify_result.get("errors"))
    except Exception:
        verify_result = verify_pack_set(repo_root=_norm(repo_root), schema_repo_root=_norm(repo_root), mod_policy_id="mod_policy.lab")
        report = _as_map(verify_result.get("report"))
        errors = _as_list(verify_result.get("errors"))
    summary = {
        "valid": bool(report.get("valid")),
        "pack_lock_hash": _token(_as_map(verify_result.get("pack_lock")).get("pack_lock_hash")),
        "report_fingerprint": _token(report.get("deterministic_fingerprint")),
        "error_count": len(errors),
        "refusal_codes": _sorted_tokens(_as_map(row).get("code") for row in errors),
    }
    result = "complete" if bool(report.get("valid")) and not errors else "violation"
    return (_step_row("ecosystem.pack_verify", result=result, required=required, summary=summary), summary)


def _negotiation_step(repo_root: str, endpoint_payload: Mapping[str, object], *, required: bool) -> tuple[dict, dict]:
    rows = {
        _token(_as_map(row).get("product_id")): _as_map(row)
        for row in _as_list(_as_map(endpoint_payload).get("entries"))
        if _token(_as_map(row).get("product_id"))
    }
    client_descriptor = _as_map(_as_map(rows.get("client")).get("descriptor"))
    server_descriptor = _as_map(_as_map(rows.get("server")).get("descriptor"))
    if not client_descriptor or not server_descriptor:
        summary = {"missing_product_ids": sorted(key for key in ("client", "server") if key not in rows)}
        return (_step_row("ecosystem.negotiation_smoke", result="violation", required=required, summary=summary), summary)
    negotiation = negotiate_endpoint_descriptors(_norm(repo_root), client_descriptor, server_descriptor)
    verify = verify_negotiation_record(
        _norm(repo_root),
        _as_map(negotiation.get("negotiation_record")),
        client_descriptor,
        server_descriptor,
    )
    summary = {
        "negotiation_result": _token(negotiation.get("result")),
        "verify_result": _token(verify.get("result")),
        "compatibility_mode_id": _token(negotiation.get("compatibility_mode_id")),
        "negotiation_record_hash": _token(negotiation.get("negotiation_record_hash")),
        "verify_hash": _token(_as_map(verify).get("negotiation_record_hash")),
    }
    result = "complete" if _token(negotiation.get("result")) == "complete" and _token(verify.get("result")) == "complete" else "violation"
    return (_step_row("ecosystem.negotiation_smoke", result=result, required=required, summary=summary), summary)


def _convergence_step(repo_root: str, env_row: Mapping[str, object], *, required: bool, allow_heavy: bool) -> tuple[dict, dict]:
    env_extensions = _as_map(_as_map(env_row).get("extensions"))
    dist_present = bool(_token(env_extensions.get("dist_root_rel")) and os.path.isdir(_repo_abs(repo_root, _token(env_extensions.get("dist_root_rel")))))
    if not allow_heavy:
        summary = {"allow_heavy": False, "include_dist_verify": dist_present}
        return (_step_row("heavy.convergence_gate", result="skipped", required=required, reason="allow_heavy_false", summary=summary), summary)
    report = run_convergence_gate(
        _norm(repo_root),
        skip_cross_platform=True,
        prefer_cached_heavy=True,
        include_dist_verify=dist_present,
    )
    summary = {
        "result": _token(report.get("result")),
        "completed_step_count": int(report.get("completed_step_count", 0) or 0),
        "stopped_at_step_id": _token(report.get("stopped_at_step_id")),
        "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
    }
    result = "complete" if _token(report.get("result")) == "complete" else "violation"
    return (_step_row("heavy.convergence_gate", result=result, required=required, summary=summary), summary)


def _hashes_payload(
    *,
    env_row: Mapping[str, object],
    profile_row: Mapping[str, object],
    run_id: str,
    run_input_payload: Mapping[str, object],
    build_ids_payload: Mapping[str, object],
    endpoint_payload: Mapping[str, object],
    step_summaries: Mapping[str, object],
    repo_root: str,
) -> dict:
    endpoint_rows = [_as_map(row) for row in _as_list(_as_map(endpoint_payload).get("entries"))]
    endpoint_hashes = {
        _token(row.get("product_id")): _token(row.get("endpoint_descriptor_hash"))
        for row in endpoint_rows
        if _token(row.get("product_id"))
    }
    endpoint_semantic_hashes = {
        _token(row.get("product_id")): _token(row.get("semantic_hash"))
        for row in endpoint_rows
        if _token(row.get("product_id"))
    }
    build_ids = {
        _token(_as_map(row).get("product_id")): _token(_as_map(row).get("build_id"))
        for row in _as_list(_as_map(build_ids_payload).get("entries"))
        if _token(_as_map(row).get("product_id"))
    }
    release_manifest_summary = _as_map(_as_map(step_summaries).get("smoke.release_manifest"))
    release_verify_summary = _as_map(_as_map(step_summaries).get("distribution.release_manifest_verify"))
    negotiation_summary = _as_map(_as_map(step_summaries).get("ecosystem.negotiation_smoke"))
    payload = {
        "schema_id": TOOLCHAIN_HASHES_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(_as_map(env_row).get("env_id")),
        "profile_id": _token(_as_map(profile_row).get("profile_id")),
        "run_id": _token(run_id),
        "run_input_fingerprint": _token(_as_map(run_input_payload).get("run_input_fingerprint")),
        "source_revision_id": _token(_as_map(run_input_payload).get("source_revision_id")),
        "source_snapshot_hash": _token(_as_map(run_input_payload).get("source_snapshot_hash")),
        "build_ids_hash": _token(_as_map(build_ids_payload).get("deterministic_fingerprint")),
        "build_ids": dict((key, build_ids[key]) for key in sorted(build_ids.keys())),
        "endpoint_descriptor_hashes": dict((key, endpoint_hashes[key]) for key in sorted(endpoint_hashes.keys())),
        "endpoint_descriptor_semantic_hashes": dict((key, endpoint_semantic_hashes[key]) for key in sorted(endpoint_semantic_hashes.keys())),
        "endpoint_descriptor_semantic_hash": canonical_sha256(endpoint_semantic_hashes),
        "worldgen_snapshot_hash": _worldgen_snapshot_hash(repo_root),
        "baseline_universe_hash": _baseline_universe_hash(repo_root),
        "gameplay_snapshot_hash": _gameplay_snapshot_hash(repo_root),
        "proof_anchor_hashes": _proof_anchor_hashes(repo_root),
        "release_manifest_hash": _token(release_manifest_summary.get("release_manifest_hash")),
        "release_manifest_projection_hash": _token(release_manifest_summary.get("release_manifest_projection_hash")),
        "release_manifest_verified_hash": _token(release_verify_summary.get("manifest_hash")),
        "negotiation_record_hash": _token(negotiation_summary.get("negotiation_record_hash")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _env_report_payload(
    *,
    env_row: Mapping[str, object],
    profile_row: Mapping[str, object],
    run_id: str,
    run_input_payload: Mapping[str, object],
    steps: Sequence[Mapping[str, object]],
    hashes_payload: Mapping[str, object],
) -> dict:
    step_rows = [_as_map(row) for row in list(steps or [])]
    failed = [_token(row.get("step_id")) for row in step_rows if _token(row.get("result")) == "violation"]
    skipped = [_token(row.get("step_id")) for row in step_rows if _token(row.get("result")) == "skipped"]
    payload = {
        "schema_id": TOOLCHAIN_ENV_REPORT_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(_as_map(env_row).get("env_id")),
        "profile_id": _token(_as_map(profile_row).get("profile_id")),
        "run_id": _token(run_id),
        "run_input_fingerprint": _token(_as_map(run_input_payload).get("run_input_fingerprint")),
        "result": "complete" if not failed else "violation",
        "failed_step_ids": failed,
        "skipped_step_ids": skipped,
        "step_count": len(step_rows),
        "completed_step_count": len([row for row in step_rows if _token(row.get("result")) == "complete"]),
        "build_ids_hash": _token(_as_map(hashes_payload).get("build_ids_hash")),
        "endpoint_descriptor_semantic_hash": _token(_as_map(hashes_payload).get("endpoint_descriptor_semantic_hash")),
        "worldgen_snapshot_hash": _token(_as_map(hashes_payload).get("worldgen_snapshot_hash")),
        "baseline_universe_hash": _token(_as_map(hashes_payload).get("baseline_universe_hash")),
        "gameplay_snapshot_hash": _token(_as_map(hashes_payload).get("gameplay_snapshot_hash")),
        "proof_anchor_hashes": dict(_as_map(hashes_payload).get("proof_anchor_hashes") or {}),
        "release_manifest_projection_hash": _token(_as_map(hashes_payload).get("release_manifest_projection_hash")),
        "negotiation_record_hash": _token(_as_map(hashes_payload).get("negotiation_record_hash")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _results_payload(
    *,
    env_row: Mapping[str, object],
    profile_row: Mapping[str, object],
    run_id: str,
    run_input_payload: Mapping[str, object],
    steps: Sequence[Mapping[str, object]],
    hashes_payload: Mapping[str, object],
) -> dict:
    env_report = _env_report_payload(
        env_row=env_row,
        profile_row=profile_row,
        run_id=run_id,
        run_input_payload=run_input_payload,
        steps=steps,
        hashes_payload=hashes_payload,
    )
    payload = {
        "schema_id": TOOLCHAIN_RUN_RESULTS_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(_as_map(env_row).get("env_id")),
        "profile_id": _token(_as_map(profile_row).get("profile_id")),
        "run_id": _token(run_id),
        "run_input_fingerprint": _token(_as_map(run_input_payload).get("run_input_fingerprint")),
        "result": _token(env_report.get("result")),
        "steps": [dict(_as_map(row)) for row in list(steps or [])],
        "summary": env_report,
        "hashes_fingerprint": _token(_as_map(hashes_payload).get("deterministic_fingerprint")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _run_manifest_payload(
    *,
    repo_root: str,
    env_row: Mapping[str, object],
    profile_row: Mapping[str, object],
    run_id: str,
    run_input_payload: Mapping[str, object],
    run_root: str,
) -> dict:
    env_root = os.path.dirname(_norm(run_root))
    payload = {
        "schema_id": TOOLCHAIN_RUN_MANIFEST_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": _token(_as_map(env_row).get("env_id")),
        "profile_id": _token(_as_map(profile_row).get("profile_id")),
        "run_id": _token(run_id),
        "run_input_fingerprint": _token(_as_map(run_input_payload).get("run_input_fingerprint")),
        "source_revision_id": _token(_as_map(run_input_payload).get("source_revision_id")),
        "source_snapshot_hash": _token(_as_map(run_input_payload).get("source_snapshot_hash")),
        "env_descriptor_hash": _token(_as_map(env_row).get("deterministic_fingerprint")),
        "profile_descriptor_hash": _token(_as_map(profile_row).get("deterministic_fingerprint")),
        "run_root_rel": _relative_to(repo_root, run_root),
        "env_root_rel": _relative_to(repo_root, env_root),
        "output_files": {
            "run_manifest_rel": _relative_to(repo_root, os.path.join(run_root, "run_manifest.json")),
            "results_rel": _relative_to(repo_root, os.path.join(run_root, "results.json")),
            "env_report_rel": _relative_to(repo_root, os.path.join(run_root, "env_report.json")),
            "hashes_rel": _relative_to(repo_root, os.path.join(run_root, "hashes.json")),
            "build_ids_rel": _relative_to(repo_root, os.path.join(run_root, "build_ids.json")),
            "endpoint_descriptors_rel": _relative_to(repo_root, os.path.join(run_root, "endpoint_descriptors.json")),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def write_toolchain_planning_surfaces(repo_root: str) -> dict:
    root = _norm(repo_root)
    registry_payload = build_default_toolchain_matrix_registry()
    profile_payload = build_default_toolchain_test_profile_registry()
    retro_path = _write_text(_repo_abs(root, TOOLCHAIN_MATRIX_RETRO_AUDIT_REL), render_toolchain_matrix_retro_audit(root))
    model_path = _write_text(_repo_abs(root, TOOLCHAIN_MATRIX_MODEL_DOC_REL), render_toolchain_matrix_model_doc(root))
    registry_path = _write_canonical_json(_repo_abs(root, TOOLCHAIN_MATRIX_REGISTRY_REL), registry_payload)
    profile_path = _write_canonical_json(_repo_abs(root, TOOLCHAIN_TEST_PROFILE_REGISTRY_REL), profile_payload)
    return {
        "retro_audit_path": retro_path,
        "model_doc_path": model_path,
        "matrix_registry_path": registry_path,
        "profile_registry_path": profile_path,
    }


def run_toolchain_matrix(
    repo_root: str,
    *,
    env_id: str = "",
    profile_id: str = "",
    output_root_rel: str = "",
    allow_heavy: bool = False,
    write_outputs: bool = True,
) -> dict:
    root = _norm(repo_root)
    env = select_env_row(root, env_id or DEFAULT_ENV_ID)
    profile = select_profile_row(root, profile_id or DEFAULT_PROFILE_ID)
    if not env:
        raise ValueError("unknown env_id '{}'".format(_token(env_id or DEFAULT_ENV_ID)))
    if not profile:
        raise ValueError("unknown profile_id '{}'".format(_token(profile_id or DEFAULT_PROFILE_ID)))
    run_id, run_input_payload = build_run_id(root, env, profile)
    output_root = _repo_abs(root, output_root_rel or DEFAULT_TOOLCHAIN_RUNS_REL)
    env_root = os.path.join(output_root, _token(env.get("env_id")))
    run_root = os.path.join(env_root, run_id)
    _ensure_dir(run_root)

    build_ids_payload = _build_ids_payload(root, env, profile)
    endpoint_payload = _endpoint_descriptors_payload(root, env, profile)
    build_ids_path = os.path.join(run_root, "build_ids.json")
    endpoint_path = os.path.join(run_root, "endpoint_descriptors.json")
    if write_outputs:
        _write_canonical_json(build_ids_path, build_ids_payload)
        _write_canonical_json(endpoint_path, endpoint_payload)

    required_ids = set(_sorted_tokens(profile.get("required_step_ids")))
    ordered_steps: list[dict] = []
    step_summaries: dict[str, dict] = {}
    for step_id in list(profile.get("step_ids") or []):
        token = _token(step_id)
        required = token in required_ids
        if token == "smoke.build_ids":
            summary = {
                "build_count": len(_as_list(build_ids_payload.get("entries"))),
                "deterministic_fingerprint": _token(build_ids_payload.get("deterministic_fingerprint")),
            }
            row = _step_row(token, result="complete", required=required, summary=summary)
        elif token == "smoke.endpoint_descriptors":
            summary = {
                "descriptor_count": len(_as_list(endpoint_payload.get("entries"))),
                "deterministic_fingerprint": _token(endpoint_payload.get("deterministic_fingerprint")),
            }
            row = _step_row(token, result="complete", required=required, summary=summary)
        elif token == "smoke.release_manifest":
            row, summary = _smoke_release_manifest_step(root, env, required=required)
        elif token == "determinism_core.worldgen_lock":
            row, summary = _worldgen_verify_step(root, required=required)
        elif token == "determinism_core.baseline_universe":
            row, summary = _baseline_universe_verify_step(root, required=required)
        elif token == "ecosystem.pack_verify":
            row, summary = _pack_verify_step(root, required=required)
        elif token == "ecosystem.negotiation_smoke":
            row, summary = _negotiation_step(root, endpoint_payload, required=required)
        elif token == "distribution.release_manifest_verify":
            row, summary = _distribution_release_manifest_verify_step(root, env, required=required)
        elif token == "heavy.convergence_gate":
            row, summary = _convergence_step(root, env, required=required, allow_heavy=bool(allow_heavy))
        else:
            summary = {"message": "unknown step_id"}
            row = _step_row(token, result="violation", required=required, summary=summary)
        ordered_steps.append(row)
        step_summaries[token] = dict(summary)

    hashes_payload = _hashes_payload(
        env_row=env,
        profile_row=profile,
        run_id=run_id,
        run_input_payload=run_input_payload,
        build_ids_payload=build_ids_payload,
        endpoint_payload=endpoint_payload,
        step_summaries=step_summaries,
        repo_root=root,
    )
    env_report = _env_report_payload(
        env_row=env,
        profile_row=profile,
        run_id=run_id,
        run_input_payload=run_input_payload,
        steps=ordered_steps,
        hashes_payload=hashes_payload,
    )
    results_payload = _results_payload(
        env_row=env,
        profile_row=profile,
        run_id=run_id,
        run_input_payload=run_input_payload,
        steps=ordered_steps,
        hashes_payload=hashes_payload,
    )
    manifest_payload = _run_manifest_payload(
        repo_root=root,
        env_row=env,
        profile_row=profile,
        run_id=run_id,
        run_input_payload=run_input_payload,
        run_root=run_root,
    )

    output_paths = {
        "run_manifest_path": os.path.join(run_root, "run_manifest.json"),
        "results_path": os.path.join(run_root, "results.json"),
        "env_report_path": os.path.join(run_root, "env_report.json"),
        "hashes_path": os.path.join(run_root, "hashes.json"),
        "build_ids_path": build_ids_path,
        "endpoint_descriptors_path": endpoint_path,
    }
    if write_outputs:
        _write_canonical_json(output_paths["run_manifest_path"], manifest_payload)
        _write_canonical_json(output_paths["results_path"], results_payload)
        _write_canonical_json(output_paths["env_report_path"], env_report)
        _write_canonical_json(output_paths["hashes_path"], hashes_payload)
        _write_canonical_json(os.path.join(env_root, "run_manifest.json"), manifest_payload)
        _write_canonical_json(os.path.join(env_root, "results.json"), results_payload)
        _write_canonical_json(os.path.join(env_root, "env_report.json"), env_report)
        _write_canonical_json(os.path.join(env_root, "hashes.json"), hashes_payload)

    return {
        "result": _token(env_report.get("result")),
        "env_row": env,
        "profile_row": profile,
        "run_id": run_id,
        "run_input_payload": run_input_payload,
        "run_root": run_root,
        "run_root_rel": _relative_to(root, run_root),
        "env_root_rel": _relative_to(root, env_root),
        "build_ids_payload": build_ids_payload,
        "endpoint_payload": endpoint_payload,
        "hashes_payload": hashes_payload,
        "env_report": env_report,
        "results_payload": results_payload,
        "manifest_payload": manifest_payload,
        "output_paths": output_paths,
    }


def _load_run_payload(run_dir: str, filename: str) -> dict:
    return _load_json(os.path.join(_norm(run_dir), filename))


def list_committed_toolchain_run_dirs(repo_root: str) -> list[str]:
    root = _repo_abs(repo_root, DEFAULT_TOOLCHAIN_RUNS_REL)
    if not os.path.isdir(root):
        return []
    rows = []
    for env_id in sorted(os.listdir(root)):
        env_root = os.path.join(root, env_id)
        if not os.path.isdir(env_root):
            continue
        for run_id in sorted(os.listdir(env_root)):
            run_root = os.path.join(env_root, run_id)
            if not os.path.isdir(run_root):
                continue
            if not run_id.startswith(RUN_ID_PREFIX):
                continue
            if os.path.isfile(os.path.join(run_root, "run_manifest.json")) and os.path.isfile(os.path.join(run_root, "results.json")) and os.path.isfile(os.path.join(run_root, "hashes.json")):
                rows.append(run_root)
    return rows


def load_toolchain_run_manifest(run_dir: str) -> dict:
    return _load_run_payload(run_dir, "run_manifest.json")


def load_toolchain_run_results(run_dir: str) -> dict:
    return _load_run_payload(run_dir, "results.json")


def load_toolchain_run_hashes(run_dir: str) -> dict:
    return _load_run_payload(run_dir, "hashes.json")


def compare_toolchain_runs(repo_root: str, left_run_dir: str, right_run_dir: str, *, write_path: str = "") -> dict:
    root = _norm(repo_root)
    left_manifest = load_toolchain_run_manifest(left_run_dir)
    right_manifest = load_toolchain_run_manifest(right_run_dir)
    left_hashes = load_toolchain_run_hashes(left_run_dir)
    right_hashes = load_toolchain_run_hashes(right_run_dir)
    same_env = _token(left_manifest.get("env_id")) == _token(right_manifest.get("env_id"))
    same_profile = _token(left_manifest.get("profile_id")) == _token(right_manifest.get("profile_id"))
    identical_inputs = _token(left_manifest.get("run_input_fingerprint")) == _token(right_manifest.get("run_input_fingerprint"))
    blocking_differences = []
    allowed_differences = []

    def compare_field(field_name: str, *, category: str, message: str, always_blocking: bool = False) -> None:
        left_value = _as_map(left_hashes).get(field_name)
        right_value = _as_map(right_hashes).get(field_name)
        if left_value == right_value:
            return
        row = {
            "category": category,
            "field_name": field_name,
            "left": left_value,
            "right": right_value,
            "message": message,
        }
        if always_blocking:
            blocking_differences.append(row)
        else:
            allowed_differences.append(row)

    compare_field(
        "worldgen_snapshot_hash",
        category="semantic.worldgen",
        message="worldgen snapshot hashes must match across all toolchain runs",
        always_blocking=True,
    )
    compare_field(
        "baseline_universe_hash",
        category="semantic.baseline_universe",
        message="baseline universe hashes must match across all toolchain runs",
        always_blocking=True,
    )
    compare_field(
        "gameplay_snapshot_hash",
        category="semantic.gameplay",
        message="gameplay snapshot hashes must match across all toolchain runs",
        always_blocking=True,
    )
    if _as_map(left_hashes).get("proof_anchor_hashes") != _as_map(right_hashes).get("proof_anchor_hashes"):
        blocking_differences.append(
            {
                "category": "semantic.proof_anchors",
                "field_name": "proof_anchor_hashes",
                "left": dict(_as_map(left_hashes).get("proof_anchor_hashes") or {}),
                "right": dict(_as_map(right_hashes).get("proof_anchor_hashes") or {}),
                "message": "proof anchor hashes must match across all toolchain runs",
            }
        )
    if _as_map(left_hashes).get("endpoint_descriptor_semantic_hashes") != _as_map(right_hashes).get("endpoint_descriptor_semantic_hashes"):
        row = {
            "category": "semantic.endpoint_descriptors",
            "field_name": "endpoint_descriptor_semantic_hashes",
            "left": dict(_as_map(left_hashes).get("endpoint_descriptor_semantic_hashes") or {}),
            "right": dict(_as_map(right_hashes).get("endpoint_descriptor_semantic_hashes") or {}),
            "message": "endpoint descriptor semantics diverged",
        }
        if same_env:
            blocking_differences.append(row)
        else:
            row["message"] = "endpoint descriptor semantics differ across distinct environment ids; informational unless comparing identical envs"
            allowed_differences.append(row)
    if _as_map(left_hashes).get("build_ids") != _as_map(right_hashes).get("build_ids"):
        row = {
            "category": "identity.build_ids",
            "field_name": "build_ids",
            "left": dict(_as_map(left_hashes).get("build_ids") or {}),
            "right": dict(_as_map(right_hashes).get("build_ids") or {}),
            "message": "build ids diverged",
        }
        if identical_inputs:
            row["message"] = "build ids must match when env, profile, and source inputs are identical"
            blocking_differences.append(row)
        else:
            row["message"] = "build id divergence is allowed because the compared inputs are not identical"
            allowed_differences.append(row)
    for field_name, message in (
        ("release_manifest_hash", "release manifest payload hash may differ across environments or package states"),
        ("release_manifest_projection_hash", "release manifest projection hash may differ when dist composition differs"),
        ("negotiation_record_hash", "negotiation record hash may differ when environment capability sets differ"),
    ):
        compare_field(field_name, category="informational.{}".format(field_name), message=message, always_blocking=False)

    semantic_fingerprints_match = not any(
        _token(_as_map(row).get("category")).startswith("semantic.")
        for row in blocking_differences
    )
    report = {
        "schema_id": TOOLCHAIN_COMPARE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "left_run_dir_rel": _relative_to(root, left_run_dir),
        "right_run_dir_rel": _relative_to(root, right_run_dir),
        "left_env_id": _token(left_manifest.get("env_id")),
        "right_env_id": _token(right_manifest.get("env_id")),
        "left_profile_id": _token(left_manifest.get("profile_id")),
        "right_profile_id": _token(right_manifest.get("profile_id")),
        "identical_inputs": identical_inputs,
        "same_env_id": same_env,
        "same_profile_id": same_profile,
        "semantic_fingerprints_match": semantic_fingerprints_match,
        "blocking_differences": blocking_differences,
        "allowed_differences": allowed_differences,
        "result": "complete" if not blocking_differences else "refused",
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _fingerprint(report)
    if _token(write_path):
        _write_canonical_json(_repo_abs(root, write_path), report)
    return report


def render_toolchain_matrix_retro_audit(repo_root: str) -> str:
    target_matrix_exists = os.path.isfile(_repo_abs(repo_root, "data/registries/target_matrix_registry.json"))
    platform_registry_exists = os.path.isfile(_repo_abs(repo_root, "data/registries/platform_capability_registry.json"))
    dist_exists = os.path.isdir(_repo_abs(repo_root, "dist/v0.0.0-mock/win64/dominium"))
    lines = [
        "# TOOLCHAIN-MATRIX-0 Retro Audit",
        "",
        "## Scope",
        "",
        "- ARCH-MATRIX-0 target matrix source: `data/registries/target_matrix_registry.json` (`exists={}`)".format(target_matrix_exists),
        "- PLATFORM-FORMALIZE capability source: `data/registries/platform_capability_registry.json` + `src/platform/platform_probe.py` (`exists={}`)".format(platform_registry_exists),
        "- RELEASE build identity source: `src/release/build_id_engine.py` (`source_revision_id`, `build_product_build_metadata`, `build_id_identity_from_input_payload`)",
        "- Release manifest generation/verification source: `src/release/release_manifest_engine.py`",
        "",
        "## Existing Gate Tooling",
        "",
        "- `CONVERGENCE-GATE`: `tools/convergence/convergence_gate_common.py`",
        "- `WORLDGEN-LOCK verify`: `tools/worldgen/worldgen_lock_common.py`",
        "- `BASELINE-UNIVERSE verify`: `tools/mvp/baseline_universe_common.py`",
        "- `GAMEPLAY verify`: `tools/mvp/gameplay_loop_common.py`",
        "- `DISASTER suite`: `tools/mvp/disaster_suite_common.py`",
        "- `release manifest verify`: `src/release/release_manifest_engine.py`",
        "",
        "## Audit Notes",
        "",
        "- Current committed mock dist root exists only for the Windows NT x86_64 lane: `{}`".format(dist_exists),
        "- Existing target policy is product support policy, not an environment run registry.",
        "- Existing platform probes are host-observed and therefore not suitable as the sole Ω-9 env descriptor source for offline cross-boot comparison.",
        "- Existing build-id rules already provide deterministic identity inputs; Ω-9 needs a canonical env/profile wrapper around them.",
        "- Existing Ω verifiers already cover worldgen/universe/gameplay/disaster semantics; Ω-9 only needs to orchestrate and archive comparable outputs.",
        "",
    ]
    return "\n".join(lines)


def render_toolchain_matrix_model_doc(repo_root: str) -> str:
    del repo_root
    env_registry = build_default_toolchain_matrix_registry()
    profile_registry = build_default_toolchain_test_profile_registry()
    env_rows = _as_list(_as_map(env_registry.get("record")).get("environments"))
    profile_rows = _as_list(_as_map(profile_registry.get("record")).get("profiles"))
    lines = [
        "# TOOLCHAIN-MATRIX-0",
        "",
        "## A) Environments",
        "",
        "Each environment records:",
        "",
        "- `env_id`",
        "- `os_id`",
        "- `arch_id`",
        "- `abi_id`",
        "- `compiler_id` + `compiler_version`",
        "- `toolchain_constraints`",
        "- `stability_class = provisional`",
        "- canonical target/platform bindings in `extensions`",
        "",
        "Planned environment ids:",
        "",
    ]
    for row in env_rows:
        env = _as_map(row)
        lines.append(
            "- `{}`: {} / {} / {} / {} {}".format(
                _token(env.get("env_id")),
                _token(env.get("os_id")),
                _token(env.get("arch_id")),
                _token(env.get("abi_id")),
                _token(env.get("compiler_id")),
                _token(env.get("compiler_version")),
            )
        )
    lines.extend(
        [
            "",
            "## B) Required Tests Per Environment",
            "",
            "- `toolchain.smoke`: build ids, endpoint descriptors, release manifest generation when dist exists",
            "- `toolchain.determinism_core`: smoke + worldgen lock verify + baseline universe verify",
            "- `toolchain.ecosystem`: determinism-core + pack verify + negotiation handshake smoke",
            "- `toolchain.full`: ecosystem + dist verify when packaging exists + optional convergence gate",
            "",
            "Profile definitions:",
            "",
        ]
    )
    for row in profile_rows:
        profile = _as_map(row)
        lines.append("- `{}`: {}".format(_token(profile.get("profile_id")), _token(profile.get("description"))))
    lines.extend(
        [
            "",
            "## C) Output Artifacts",
            "",
            "Each run writes canonical JSON under `artifacts/toolchain_runs/<env_id>/<run_id>/`:",
            "",
            "- `run_manifest.json`",
            "- `results.json`",
            "- `env_report.json`",
            "- `hashes.json`",
            "- `build_ids.json`",
            "- `endpoint_descriptors.json`",
            "",
            "Canonical output hashes include:",
            "",
            "- build-id list hash",
            "- endpoint descriptor hash set",
            "- endpoint descriptor semantic hash set",
            "- worldgen snapshot hash",
            "- baseline universe hash",
            "- gameplay snapshot hash",
            "- proof anchor hashes",
            "",
            "## Acceptance Rules",
            "",
            "- `run_id = hash(env_descriptor + profile_descriptor + git_revision_or_source_snapshot_hash)`",
            "- If inputs are identical, build ids MUST match.",
            "- For same-`env_id` comparisons, endpoint descriptor semantic hashes MUST match.",
            "- Worldgen, baseline universe, gameplay, and proof anchor hashes MUST match across all toolchain runs.",
            "- Dist verification and convergence are optional when their prerequisites are absent.",
            "",
        ]
    )
    return "\n".join(lines)


def render_toolchain_matrix_baseline_doc(
    repo_root: str,
    report: Mapping[str, object],
    *,
    compare_rules: Mapping[str, object] | None = None,
) -> str:
    del compare_rules
    registry = load_toolchain_matrix_registry(repo_root)
    profile_registry = load_toolchain_test_profile_registry(repo_root)
    env_rows = _as_list(_as_map(registry.get("record")).get("environments"))
    profile_rows = _as_list(_as_map(profile_registry.get("record")).get("profiles"))
    env_report = _as_map(_as_map(report).get("env_report"))
    hashes = _as_map(_as_map(report).get("hashes_payload"))
    run_input = _as_map(_as_map(report).get("run_input_payload"))
    lines = [
        "# TOOLCHAIN Matrix Baseline",
        "",
        "## Environments",
        "",
    ]
    for row in env_rows:
        env = _as_map(row)
        lines.append("- `{}`".format(_token(env.get("env_id"))))
    lines.extend(
        [
            "",
            "## Required Tests",
            "",
        ]
    )
    for row in profile_rows:
        profile = _as_map(row)
        lines.append("- `{}`: `{}`".format(_token(profile.get("profile_id")), ", ".join(list(profile.get("step_ids") or []))))
    lines.extend(
        [
            "",
            "## Collection Method",
            "",
            "- Run directory: `{}`".format(_token(_as_map(report).get("run_root_rel"))),
            "- Run id: `{}`".format(_token(_as_map(report).get("run_id"))),
            "- Source identity kind: `{}`".format(_token(run_input.get("source_identity_kind"))),
            "- Source snapshot hash: `{}`".format(_token(run_input.get("source_snapshot_hash"))),
            "- Git revision hint: `{}`".format(_token(run_input.get("git_revision_hint"))),
            "- Result: `{}`".format(_token(env_report.get("result"))),
            "",
            "## Current Reference Hashes",
            "",
            "- Build ids hash: `{}`".format(_token(hashes.get("build_ids_hash"))),
            "- Endpoint semantic hash: `{}`".format(_token(hashes.get("endpoint_descriptor_semantic_hash"))),
            "- Worldgen snapshot hash: `{}`".format(_token(hashes.get("worldgen_snapshot_hash"))),
            "- Baseline universe hash: `{}`".format(_token(hashes.get("baseline_universe_hash"))),
            "- Gameplay snapshot hash: `{}`".format(_token(hashes.get("gameplay_snapshot_hash"))),
            "",
            "## Comparison Method",
            "",
            "- Compare `run_manifest.json`, `results.json`, and `hashes.json` from two run directories.",
            "- Identical inputs require identical build ids.",
            "- Same-environment comparisons require identical endpoint descriptor semantic hashes.",
            "- Worldgen, baseline universe, gameplay, and proof anchor hashes are always blocking if they drift.",
            "",
            "## Readiness",
            "",
            "- Ω-9 surfaces exist and one committed reference run is archived for deterministic comparison.",
            "- Additional environments can be populated later without expanding Tier 1 commitments.",
            "- Ready for Ω-10 distribution-plan integration.",
            "",
        ]
    )
    return "\n".join(lines)


def write_toolchain_matrix_baseline_doc(repo_root: str, report: Mapping[str, object]) -> str:
    root = _norm(repo_root)
    return _write_text(
        _repo_abs(root, TOOLCHAIN_MATRIX_BASELINE_DOC_REL),
        render_toolchain_matrix_baseline_doc(root, report),
    )


__all__ = [
    "DEFAULT_ENV_ID",
    "DEFAULT_PROFILE_ID",
    "DEFAULT_TOOLCHAIN_RUNS_REL",
    "RUN_ID_PREFIX",
    "TOOLCHAIN_BUILD_IDS_SCHEMA_ID",
    "TOOLCHAIN_COMPARE_SCHEMA_ID",
    "TOOLCHAIN_ENDPOINT_DESCRIPTORS_SCHEMA_ID",
    "TOOLCHAIN_ENV_REPORT_SCHEMA_ID",
    "TOOLCHAIN_HASHES_SCHEMA_ID",
    "TOOLCHAIN_MATRIX_BASELINE_DOC_REL",
    "TOOLCHAIN_MATRIX_MODEL_DOC_REL",
    "TOOLCHAIN_MATRIX_REGISTRY_REL",
    "TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID",
    "TOOLCHAIN_MATRIX_RETRO_AUDIT_REL",
    "TOOLCHAIN_RUN_MANIFEST_SCHEMA_ID",
    "TOOLCHAIN_RUN_RESULTS_SCHEMA_ID",
    "TOOLCHAIN_TEST_PROFILE_REGISTRY_REL",
    "TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID",
    "build_default_toolchain_matrix_registry",
    "build_default_toolchain_test_profile_registry",
    "build_env_platform_descriptor",
    "build_env_product_descriptor",
    "build_run_id",
    "build_run_input_payload",
    "canonicalize_toolchain_env_row",
    "canonicalize_toolchain_matrix_registry",
    "canonicalize_toolchain_profile_row",
    "canonicalize_toolchain_test_profile_registry",
    "compare_toolchain_runs",
    "endpoint_descriptor_semantic_hash",
    "env_rows_by_id",
    "list_committed_toolchain_run_dirs",
    "load_toolchain_matrix_registry",
    "load_toolchain_run_hashes",
    "load_toolchain_run_manifest",
    "load_toolchain_run_results",
    "load_toolchain_test_profile_registry",
    "profile_rows_by_id",
    "render_toolchain_matrix_baseline_doc",
    "render_toolchain_matrix_model_doc",
    "render_toolchain_matrix_retro_audit",
    "run_toolchain_matrix",
    "select_env_row",
    "select_profile_row",
    "toolchain_matrix_registry_hash",
    "toolchain_test_profile_registry_hash",
    "write_toolchain_matrix_baseline_doc",
    "write_toolchain_planning_surfaces",
]
