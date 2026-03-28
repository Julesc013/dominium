"""Deterministic ARCH-MATRIX-0 helpers."""

from __future__ import annotations

import glob
import json
import os
from typing import Mapping

from compat.descriptor.descriptor_engine import build_product_descriptor
from engine.platform.target_matrix import (
    TARGET_MATRIX_REGISTRY_REL,
    canonicalize_target_matrix_row,
    load_target_matrix_registry,
    select_target_matrix_row,
    target_matrix_registry_hash,
)
from release import load_release_index
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "ARCH_MATRIX0_RETRO_AUDIT.md")
TARGET_MATRIX_DOC_REL = os.path.join("docs", "release", "TARGET_MATRIX_v0_0_0_mock.md")
TARGET_CAPABILITY_RULES_DOC_REL = os.path.join("docs", "release", "TARGET_CAPABILITY_RULES.md")
REPORT_JSON_REL = os.path.join("data", "audit", "arch_matrix_report.json")
FINAL_DOC_REL = os.path.join("docs", "audit", "ARCH_MATRIX_FINAL.md")
RUNNER_REL = os.path.join("tools", "release", "tool_run_arch_matrix.py")
RULE_TARGET_MATRIX = "INV-TARGET-MATRIX-DECLARED"
RULE_TIER1_GATES = "INV-TIER1-MUST-PASS-ALL-GATES"
RULE_TIER3_RELEASE_INDEX = "INV-TIER3-NOT-IN-DEFAULT-RELEASE_INDEX"
LAST_REVIEWED = "2026-03-14"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_unique_strings(value: object) -> list[str]:
    return sorted({_token(item) for item in _as_list(value) if _token(item)})


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _normalized_release_index_abi(abi_id: object, *, platform_id: object = "") -> str:
    abi_token = _token(abi_id)
    if abi_token:
        legacy_map = {
            "abi.win32": "abi.msvc",
            "abi.win64": "abi.msvc",
        }
        abi_token = legacy_map.get(abi_token, abi_token)
    if abi_token:
        return abi_token
    platform_token = _token(platform_id)
    fallback_map = {
        "platform.linux_gtk": "abi.glibc",
        "platform.macos_cocoa": "abi.cocoa",
        "platform.macos_classic": "abi.carbon",
        "platform.posix_min": "abi.null",
        "platform.sdl_stub": "abi.sdl",
        "platform.win9x": "abi.mingw",
        "platform.winnt": "abi.msvc",
    }
    return fallback_map.get(platform_token, "")


def _deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(payload or {}, deterministic_fingerprint=""))


def _stability(*, tier: int, rationale: str, future_series: str, replacement_target: str) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": "provisional",
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": "",
        "deterministic_fingerprint": "",
        "extensions": {"declared_support_tier": int(tier)},
    }
    payload["deterministic_fingerprint"] = _deterministic_fingerprint(payload)
    return payload


def _row(
    *,
    target_id: str,
    os_id: str,
    abi_id: str,
    arch_id: str,
    tier: int,
    supported_products: list[str],
    default_install_profiles: list[str],
    capability_overrides: Mapping[str, object] | None,
    platform_id: str,
    platform_tags: list[str],
    built_in_mock_release: bool,
    release_index_default: bool,
    required_platform_capabilities: list[str],
    known_missing_features: list[str],
    rationale: str,
    replacement_target: str,
) -> dict:
    return canonicalize_target_matrix_row(
        {
            "target_id": target_id,
            "os_id": os_id,
            "abi_id": abi_id,
            "arch_id": arch_id,
            "tier": int(tier),
            "supported_products": list(supported_products or []),
            "default_install_profiles": list(default_install_profiles or []),
            "capability_overrides": dict(capability_overrides or {}),
            "extensions": {
                "platform_id": _token(platform_id),
                "platform_tags": list(platform_tags or []),
                "built_in_mock_release": bool(built_in_mock_release),
                "required_platform_capabilities": list(required_platform_capabilities or []),
                "known_missing_features": list(known_missing_features or []),
                "release_index_default": bool(release_index_default),
                "official.source": "ARCH-MATRIX-0",
            },
            "stability": _stability(
                tier=int(tier),
                rationale=rationale,
                future_series="PLATFORM/DIST",
                replacement_target=replacement_target,
            ),
        }
    )


def _target_rows() -> list[dict]:
    all_products = ["client", "engine", "game", "launcher", "server", "setup"]
    full_profiles = [
        "install.profile.client",
        "install.profile.full",
        "install.profile.server",
        "install.profile.tools",
    ]
    rows = [
        _row(
            target_id="target.os_bsd.abi_null.arch_x86_64",
            os_id="os.bsd",
            abi_id="abi.null",
            arch_id="arch.x86_64",
            tier=3,
            supported_products=["engine", "server", "setup"],
            default_install_profiles=["install.profile.server", "install.profile.tools"],
            capability_overrides={"cap.ui.os_native": False, "cap.ui.rendered": False},
            platform_id="",
            platform_tags=["bsd-x86_64"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.renderer.null"],
            known_missing_features=["No BSD bundle or adapter lane is shipped in v0.0.0-mock."],
            rationale="BSD remains declared only and is not part of the current mock release.",
            replacement_target="Promote BSD only after a real bundle exists and passes clean-room, platform-matrix, and convergence gates.",
        ),
        _row(
            target_id="target.os_linux.abi_glibc.arch_arm64",
            os_id="os.linux",
            abi_id="abi.glibc",
            arch_id="arch.arm64",
            tier=2,
            supported_products=all_products,
            default_install_profiles=full_profiles,
            capability_overrides={},
            platform_id="platform.linux_gtk",
            platform_tags=["linux-arm64"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ipc.local_socket", "cap.renderer.null"],
            known_missing_features=["No ARM64 Linux portable bundle is built in the current repository state."],
            rationale="Linux ARM64 is an experimental target pending real artifact production.",
            replacement_target="Promote Linux ARM64 after DIST clean-room and platform-matrix lanes run on built artifacts.",
        ),
        _row(
            target_id="target.os_linux.abi_glibc.arch_x86_64",
            os_id="os.linux",
            abi_id="abi.glibc",
            arch_id="arch.x86_64",
            tier=1,
            supported_products=all_products,
            default_install_profiles=full_profiles,
            capability_overrides={},
            platform_id="platform.linux_gtk",
            platform_tags=["linux-x86_64"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ipc.local_socket", "cap.renderer.software"],
            known_missing_features=["Linux x86_64 is Tier 1 only when a bundle is actually built and validated."],
            rationale="Linux x86_64 is an official target in policy, but this repository state does not currently ship it.",
            replacement_target="Keep the target as declared Tier 1 and enable release-index publication only once the Linux bundle passes all gates.",
        ),
        _row(
            target_id="target.os_macos_classic.abi_carbon.arch_ppc32",
            os_id="os.macos_classic",
            abi_id="abi.carbon",
            arch_id="arch.ppc32",
            tier=3,
            supported_products=["engine", "setup"],
            default_install_profiles=["install.profile.tools"],
            capability_overrides={"cap.ui.tui": False, "cap.ui.rendered": False},
            platform_id="platform.macos_classic",
            platform_tags=["macos-classic"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.renderer.null"],
            known_missing_features=["Classic Mac remains declared only; no Carbon package or validation lane exists."],
            rationale="Classic Mac remains aspirational for the mock release.",
            replacement_target="Promote only after Carbon-specific runtime validation and packaging exist.",
        ),
        _row(
            target_id="target.os_macosx.abi_cocoa.arch_arm64",
            os_id="os.macosx",
            abi_id="abi.cocoa",
            arch_id="arch.arm64",
            tier=2,
            supported_products=all_products,
            default_install_profiles=full_profiles,
            capability_overrides={},
            platform_id="platform.macos_cocoa",
            platform_tags=["macos-universal"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ipc.local_socket", "cap.renderer.software"],
            known_missing_features=["No macOS universal bundle is built in the current repository state."],
            rationale="macOS ARM64 is a declared experimental target pending real bundle validation.",
            replacement_target="Promote after macOS clean-room and DIST matrix validation are available.",
        ),
        _row(
            target_id="target.os_msdos.abi_freestanding.arch_x86_32",
            os_id="os.msdos",
            abi_id="abi.freestanding",
            arch_id="arch.x86_32",
            tier=3,
            supported_products=["engine", "setup"],
            default_install_profiles=["install.profile.tools"],
            capability_overrides={"cap.ui.tui": False, "cap.ui.rendered": False},
            platform_id="",
            platform_tags=["msdos-x86_32"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.renderer.null"],
            known_missing_features=["MS-DOS remains aspirational and has no build or packaging surface."],
            rationale="MS-DOS is declared only to reserve identifiers and capability policy.",
            replacement_target="Replace the placeholder once a DOS-targeted runtime and packaging flow exist.",
        ),
        _row(
            target_id="target.os_posix.abi_null.arch_riscv64",
            os_id="os.posix",
            abi_id="abi.null",
            arch_id="arch.riscv64",
            tier=3,
            supported_products=["engine", "server", "setup"],
            default_install_profiles=["install.profile.server", "install.profile.tools"],
            capability_overrides={"cap.ui.os_native": False, "cap.ui.rendered": False},
            platform_id="platform.posix_min",
            platform_tags=["posix-riscv64"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.renderer.null"],
            known_missing_features=["RISC-V remains a future POSIX-min target with no bundle output today."],
            rationale="RISC-V is declared for future portability only.",
            replacement_target="Promote after a POSIX-min RISC-V bundle passes the platform matrix and clean-room lanes.",
        ),
        _row(
            target_id="target.os_posix.abi_null.arch_x86_64",
            os_id="os.posix",
            abi_id="abi.null",
            arch_id="arch.x86_64",
            tier=3,
            supported_products=["engine", "server", "setup"],
            default_install_profiles=["install.profile.server", "install.profile.tools"],
            capability_overrides={"cap.ui.os_native": False, "cap.ui.rendered": False},
            platform_id="platform.posix_min",
            platform_tags=["posix-min"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.renderer.null"],
            known_missing_features=["POSIX minimal remains a portability floor, not a downloadable default bundle."],
            rationale="POSIX minimal is a declared fallback target, not a shipped default bundle.",
            replacement_target="Promote only after a dedicated POSIX-min distribution bundle exists.",
        ),
        _row(
            target_id="target.os_web.abi_wasm.arch_wasm32",
            os_id="os.web",
            abi_id="abi.wasm",
            arch_id="arch.wasm32",
            tier=2,
            supported_products=["client", "engine", "setup"],
            default_install_profiles=["install.profile.client", "install.profile.tools"],
            capability_overrides={"cap.ui.cli": False, "cap.ui.tui": False, "cap.ui.os_native": False},
            platform_id="",
            platform_tags=["web-wasm32"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.rendered", "cap.renderer.software"],
            known_missing_features=["Web/WASM remains planned and does not ship in the current mock release."],
            rationale="Web/WASM is experimental and not yet packaged.",
            replacement_target="Promote after a browser packaging model and capability-gated rendered shell exist.",
        ),
        _row(
            target_id="target.os_win9x.abi_mingw.arch_x86_32",
            os_id="os.win9x",
            abi_id="abi.mingw",
            arch_id="arch.x86_32",
            tier=3,
            supported_products=["engine", "launcher", "server", "setup"],
            default_install_profiles=["install.profile.server", "install.profile.tools"],
            capability_overrides={"cap.ui.rendered": False},
            platform_id="platform.win9x",
            platform_tags=["win9x"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.renderer.null"],
            known_missing_features=["Windows 9x remains declared only and does not ship in the mock release."],
            rationale="Windows 9x remains a future/nostalgia target only.",
            replacement_target="Promote only after a Win9x-specific bundle and validation lane exist.",
        ),
        _row(
            target_id="target.os_winnt.abi_msvc.arch_x86_32",
            os_id="os.winnt",
            abi_id="abi.msvc",
            arch_id="arch.x86_32",
            tier=2,
            supported_products=all_products,
            default_install_profiles=full_profiles,
            capability_overrides={},
            platform_id="platform.winnt",
            platform_tags=["win32"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ipc.named_pipe", "cap.renderer.software"],
            known_missing_features=["No Win32 x86 bundle is built in the current repository state."],
            rationale="Windows x86 is experimental and not part of the default mock release.",
            replacement_target="Promote after a real Win32 bundle exists and passes DIST/CONVERGENCE gates.",
        ),
        _row(
            target_id="target.os_winnt.abi_msvc.arch_x86_64",
            os_id="os.winnt",
            abi_id="abi.msvc",
            arch_id="arch.x86_64",
            tier=1,
            supported_products=all_products,
            default_install_profiles=full_profiles,
            capability_overrides={},
            platform_id="platform.winnt",
            platform_tags=["win64"],
            built_in_mock_release=True,
            release_index_default=True,
            required_platform_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ipc.named_pipe", "cap.renderer.software"],
            known_missing_features=["OS-native UI remains optional; the guaranteed fallback chain is rendered/TUI/CLI."],
            rationale="Windows x86_64 is the current official shipped target for v0.0.0-mock.",
            replacement_target="Keep the target official; replace only if the release line moves to a new Tier 1 baseline.",
        ),
        _row(
            target_id="target.os_posix.abi_sdl.arch_x86_64",
            os_id="os.posix",
            abi_id="abi.sdl",
            arch_id="arch.x86_64",
            tier=3,
            supported_products=["client", "game", "launcher", "setup"],
            default_install_profiles=["install.profile.client", "install.profile.tools"],
            capability_overrides={"cap.ui.os_native": False},
            platform_id="platform.sdl_stub",
            platform_tags=["sdl-x86_64"],
            built_in_mock_release=False,
            release_index_default=False,
            required_platform_capabilities=["cap.ui.rendered", "cap.ui.cli", "cap.renderer.software"],
            known_missing_features=["SDL remains a declared adapter stub and is not part of the shipping mock release."],
            rationale="SDL remains an aspirational portability surface.",
            replacement_target="Promote after a real SDL-backed windowing/runtime path exists.",
        ),
    ]
    return sorted(rows, key=lambda row: _token(row.get("target_id")))


def build_target_matrix_registry_payload() -> dict:
    targets = _target_rows()
    record = {
        "registry_id": "dominium.registry.target_matrix_registry",
        "registry_version": "1.0.0",
        "targets": targets,
        "extensions": {"official.source": "ARCH-MATRIX-0"},
        "deterministic_fingerprint": "",
    }
    record["deterministic_fingerprint"] = canonical_sha256(dict(record, deterministic_fingerprint=""))
    return {
        "schema_id": "dominium.registry.target_matrix_registry",
        "schema_version": "1.0.0",
        "record": record,
    }


def _bundle_roots(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    patterns = (
        os.path.join(root, "dist", "v0.0.0-mock", "*", "dominium", "manifests", "release_manifest.json"),
        os.path.join(root, "build", "tmp", "*", "v0.0.0-mock", "*", "dominium", "manifests", "release_manifest.json"),
    )
    rows_by_tag: dict[str, dict] = {}
    for pattern in patterns:
        for manifest_path in sorted(glob.glob(pattern)):
            bundle_root = os.path.dirname(os.path.dirname(_norm(manifest_path)))
            platform_tag = _token(os.path.basename(os.path.dirname(bundle_root))).lower()
            if not platform_tag:
                continue
            target_row = select_target_matrix_row(root, platform_tag=platform_tag)
            source_kind = "dist" if _norm(bundle_root).startswith(os.path.join(root, "dist")) else "build_tmp"
            payload = {
                "platform_tag": platform_tag,
                "bundle_root": _norm_rel(os.path.relpath(bundle_root, root)),
                "manifest_rel": _norm_rel(os.path.relpath(_norm(manifest_path), root)),
                "source_kind": source_kind,
                "target_id": _token(target_row.get("target_id")),
                "platform_id": _token(_as_map(target_row.get("extensions")).get("platform_id")),
                "tier": int(target_row.get("tier", 0) or 0),
                "built_in_mock_release": bool(_as_map(target_row.get("extensions")).get("built_in_mock_release", False)),
            }
            previous = rows_by_tag.get(platform_tag)
            if previous and _token(previous.get("source_kind")) == "dist":
                continue
            rows_by_tag[platform_tag] = payload
    return [rows_by_tag[key] for key in sorted(rows_by_tag.keys())]


def _release_index_candidates(repo_root: str) -> list[str]:
    root = _norm(repo_root)
    patterns = (
        os.path.join(root, "dist", "v0.0.0-mock", "*", "dominium", "manifests", "release_index.json"),
        os.path.join(root, "build", "tmp", "*", "v0.0.0-mock", "*", "dominium", "manifests", "release_index.json"),
    )
    out = []
    seen = set()
    for pattern in patterns:
        for rel in sorted(glob.glob(pattern)):
            norm_rel = _norm(rel)
            if norm_rel in seen:
                continue
            seen.add(norm_rel)
            out.append(norm_rel)
    return out


def _release_index_rows(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    out = []
    for path in _release_index_candidates(root):
        payload = load_release_index(path)
        platform_rows = []
        for row in _as_list(payload.get("platform_matrix")):
            row_map = _as_map(row)
            extensions = _as_map(row_map.get("extensions"))
            normalized_abi_id = _normalized_release_index_abi(
                row_map.get("abi"),
                platform_id=extensions.get("platform_id"),
            )
            target_row = select_target_matrix_row(
                root,
                target_id=_token(extensions.get("target_id")),
                platform_id=_token(extensions.get("platform_id")),
                os_id=_token(row_map.get("os")),
                arch_id=_token(row_map.get("arch")),
                abi_id=normalized_abi_id,
            )
            if not target_row:
                target_row = select_target_matrix_row(
                    root,
                    platform_id=_token(extensions.get("platform_id")),
                    platform_tag=_token(extensions.get("platform_tag")),
                    os_id=_token(row_map.get("os")),
                    arch_id=_token(row_map.get("arch")),
                )
            platform_rows.append(
                {
                    "release_index_rel": _norm_rel(os.path.relpath(path, root)),
                    "os_id": _token(row_map.get("os")),
                    "arch_id": _token(row_map.get("arch")),
                    "abi_id": normalized_abi_id or _token(row_map.get("abi")),
                    "artifact_url_or_path": _token(row_map.get("artifact_url_or_path")),
                    "target_id": _token(target_row.get("target_id")) or _token(extensions.get("target_id")),
                    "platform_id": _token(extensions.get("platform_id")) or _token(_as_map(target_row.get("extensions")).get("platform_id")),
                    "tier": _as_int(extensions.get("tier"), _as_int(target_row.get("tier"), 0)),
                    "deterministic_fingerprint": _token(row_map.get("deterministic_fingerprint")),
                }
            )
        out.append(
            {
                "release_index_rel": _norm_rel(os.path.relpath(path, root)),
                "release_index_fingerprint": _token(payload.get("deterministic_fingerprint")),
                "platform_rows": sorted(platform_rows, key=lambda row: (_token(row.get("target_id")), _token(row.get("artifact_url_or_path")))),
            }
        )
    return out


def _gate_result(path: str) -> tuple[str, str]:
    payload = _read_json(path)
    return _token(payload.get("result")), _token(payload.get("deterministic_fingerprint"))


def _cached_tier1_gate_rows(repo_root: str) -> dict[str, dict]:
    payload = _read_json(os.path.join(_norm(repo_root), REPORT_JSON_REL))
    rows = [_as_map(row) for row in _as_list(payload.get("tier1_gate_rows"))]
    return {
        _token(row.get("target_id")): row
        for row in rows
        if _token(row.get("target_id"))
    }


def _convergence_result_for_target(repo_root: str, *, target_id: str) -> tuple[str, str, str]:
    root = _norm(repo_root)
    report_path = os.path.join(root, "data", "audit", "convergence_final.json")
    convergence_payload = _read_json(report_path)
    live_result = _token(convergence_payload.get("result"))
    live_fingerprint = _token(convergence_payload.get("deterministic_fingerprint"))
    if live_result == "complete":
        return live_result, live_fingerprint, "live"
    cached_row = _as_map(_cached_tier1_gate_rows(root).get(_token(target_id)))
    cached_result = _token(cached_row.get("convergence_result"))
    cached_fingerprint = _token(cached_row.get("convergence_fingerprint"))
    # Validation and arch-matrix cannot consume a downstream refused convergence
    # result directly, or they deadlock on the same failed gate. If the last
    # recorded Tier 1 row was complete, use that cached state until convergence
    # is rerun cleanly.
    if cached_result == "complete" and cached_fingerprint:
        return cached_result, cached_fingerprint, "arch_matrix_cache"
    return live_result, live_fingerprint, "live"


def _tier1_gate_status(repo_root: str, built_rows: list[dict]) -> list[dict]:
    root = _norm(repo_root)
    matrix_payload = _read_json(os.path.join(root, "data", "audit", "dist_platform_matrix.json"))
    matrix_result = _token(matrix_payload.get("result"))
    matrix_fingerprint = _token(matrix_payload.get("deterministic_fingerprint"))
    platform_rows = [_as_map(row) for row in _as_list(matrix_payload.get("platform_rows"))]
    out = []
    for row in built_rows:
        if int(row.get("tier", 0) or 0) != 1:
            continue
        platform_tag = _token(row.get("platform_tag"))
        target_id = _token(row.get("target_id"))
        convergence_result, convergence_fingerprint, convergence_source = _convergence_result_for_target(
            root,
            target_id=target_id,
        )
        clean_room_result, clean_room_fingerprint = _gate_result(
            os.path.join(root, "data", "audit", "clean_room_{}.json".format(platform_tag))
        )
        matrix_row = next((item for item in platform_rows if _token(item.get("platform_tag")) == platform_tag), {})
        matrix_row_map = _as_map(matrix_row)
        product_rows = [_as_map(item) for item in _as_list(matrix_row_map.get("product_rows"))]
        context_rows = [_as_map(item) for item in _as_list(matrix_row_map.get("context_rows"))]
        fallback_rows = [_as_map(item) for item in _as_list(matrix_row_map.get("fallback_rows"))]
        matrix_failure_count = _as_int(matrix_row_map.get("failure_count"), 0)
        matrix_passed = bool(matrix_row) and matrix_failure_count == 0
        if matrix_passed and product_rows:
            matrix_passed = all(bool(item.get("passed", False)) for item in product_rows)
        if matrix_passed and context_rows:
            matrix_passed = all(bool(item.get("passed", False)) for item in context_rows)
        if matrix_passed and fallback_rows:
            matrix_passed = all(bool(item.get("passed", False)) for item in fallback_rows)
        row_status = {
            "platform_tag": platform_tag,
            "target_id": target_id,
            "convergence_result": convergence_result,
            "convergence_fingerprint": convergence_fingerprint,
            "convergence_source": convergence_source,
            "clean_room_result": clean_room_result,
            "clean_room_fingerprint": clean_room_fingerprint,
            "dist4_result": matrix_result,
            "dist4_fingerprint": matrix_fingerprint,
            "dist4_platform_present": bool(matrix_row),
            "dist4_platform_passed": matrix_passed,
            "result": "complete"
            if convergence_result == "complete" and clean_room_result == "complete" and matrix_result == "complete" and matrix_passed
            else "refused",
        }
        out.append(row_status)
    return sorted(out, key=lambda row: _token(row.get("target_id")))


def _descriptor_row(repo_root: str, *, product_id: str = "client") -> dict:
    root = _norm(repo_root)
    keys = ["official.target_id", "official.os_id", "official.arch_id", "official.abi_id", "official.target_tier"]
    try:
        descriptor = build_product_descriptor(
            root,
            product_id=product_id,
            product_version="0.0.0+arch_matrix",
            platform_id="platform.winnt",
        )
    except ValueError as exc:
        return {
            "product_id": product_id,
            "present_fields": [],
            "missing_fields": list(keys),
            "target_id": "",
            "os_id": "",
            "arch_id": "",
            "abi_id": "",
            "target_tier": 0,
            "descriptor_fingerprint": "",
            "error": str(exc),
        }
    extensions = _as_map(descriptor.get("extensions"))
    return {
        "product_id": product_id,
        "present_fields": [key for key in keys if key in extensions],
        "missing_fields": [key for key in keys if key not in extensions],
        "target_id": _token(extensions.get("official.target_id")),
        "os_id": _token(extensions.get("official.os_id")),
        "arch_id": _token(extensions.get("official.arch_id")),
        "abi_id": _token(extensions.get("official.abi_id")),
        "target_tier": int(extensions.get("official.target_tier", 0) or 0),
        "descriptor_fingerprint": _token(descriptor.get("deterministic_fingerprint")),
    }


def build_arch_matrix_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    registry_payload = build_target_matrix_registry_payload()
    registry_rows = list(_as_map(registry_payload.get("record")).get("targets") or [])
    built_rows = _bundle_roots(root)
    release_index_rows = _release_index_rows(root)
    expected_release_targets = [
        {
            "target_id": _token(row.get("target_id")),
            "tier": int(row.get("tier", 0) or 0),
            "platform_tags": list(_as_map(row.get("extensions")).get("platform_tags") or []),
        }
        for row in registry_rows
        if bool(_as_map(row.get("extensions")).get("built_in_mock_release", False)) and int(row.get("tier", 0) or 0) <= 2
    ]
    tier_breakdown = {
        "tier_1": sum(1 for row in registry_rows if int(_as_map(row).get("tier", 0) or 0) == 1),
        "tier_2": sum(1 for row in registry_rows if int(_as_map(row).get("tier", 0) or 0) == 2),
        "tier_3": sum(1 for row in registry_rows if int(_as_map(row).get("tier", 0) or 0) == 3),
    }
    report = {
        "report_id": "release.arch_matrix.v1",
        "result": "complete",
        "target_matrix_registry_hash": canonical_sha256(registry_payload),
        "target_matrix_runtime_hash": target_matrix_registry_hash(root) if os.path.isfile(os.path.join(root, TARGET_MATRIX_REGISTRY_REL.replace("/", os.sep))) else "",
        "target_count": len(registry_rows),
        "tier_breakdown": tier_breakdown,
        "registry_rows": registry_rows,
        "built_rows": built_rows,
        "release_index_rows": release_index_rows,
        "expected_release_index_targets": expected_release_targets,
        "descriptor_row": _descriptor_row(root),
        "tier1_gate_rows": _tier1_gate_status(root, built_rows),
        "violations": [],
        "deterministic_fingerprint": "",
    }
    report["violations"] = arch_matrix_violations(root, report_override=report)
    report["result"] = "complete" if not report["violations"] else "refused"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_arch_matrix_retro_audit(report: Mapping[str, object]) -> str:
    built_rows = list(report.get("built_rows") or [])
    tier_rows = list(report.get("registry_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PLATFORM/DIST",
        "Replacement Target: release-pinned target matrix and release-index availability model",
        "",
        "# ARCH-MATRIX-0 Retro Audit",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Existing Inputs",
        "",
        "- `data/registries/platform_capability_registry.json` already declares platform-family capability envelopes.",
        "- `schema/release/release_index.schema` already exposes `platform_matrix` rows with `{os, arch, abi, artifact_url_or_path}`.",
        "- `data/registries/install_profile_registry.json` already defines deterministic install profiles for full/client/server/tools/sdk.",
        "- CAP-NEG endpoint descriptors now expose `official.target_id`, `official.os_id`, `official.arch_id`, `official.abi_id`, and `official.target_tier`.",
        "",
        "## Currently Built Targets",
        "",
    ]
    if built_rows:
        for row in built_rows:
            lines.append(
                "- `{}` -> `{}` (`tier {}`; source `{}`)".format(
                    _token(row.get("platform_tag")),
                    _token(row.get("target_id")) or "unmapped",
                    _token(row.get("tier")),
                    _token(row.get("source_kind")),
                )
            )
    else:
        lines.append("- None detected in `dist/` or `build/tmp/*/v0.0.0-mock`.")
    lines.extend(["", "## Declared but Unbuilt / Aspirational Targets", ""])
    for row in tier_rows:
        row_map = _as_map(row)
        extensions = _as_map(row_map.get("extensions"))
        if bool(extensions.get("built_in_mock_release", False)):
            continue
        lines.append(
            "- `{}` (`tier {}`) -> platform `{}`; known gaps: {}".format(
                _token(row_map.get("target_id")),
                _token(row_map.get("tier")),
                _token(extensions.get("platform_id")) or "none",
                "; ".join(_sorted_unique_strings(extensions.get("known_missing_features"))) or "none",
            )
        )
    return "\n".join(lines) + "\n"


def render_target_matrix_doctrine(report: Mapping[str, object]) -> str:
    rows = list(report.get("registry_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PLATFORM/DIST",
        "Replacement Target: release-pinned target matrix and downloadable artifact availability model",
        "",
        "# Target Matrix v0.0.0 Mock",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Axes",
        "",
        "### CPU Architecture",
        "- `arch.x86_32`",
        "- `arch.x86_64`",
        "- `arch.arm32`",
        "- `arch.arm64`",
        "- `arch.wasm32`",
        "- `arch.wasm64`",
        "- `arch.ppc32`",
        "- `arch.ppc64`",
        "- `arch.riscv64`",
        "",
        "### OS Family",
        "- `os.msdos`",
        "- `os.win9x`",
        "- `os.winnt`",
        "- `os.linux`",
        "- `os.macos_classic`",
        "- `os.macosx`",
        "- `os.bsd`",
        "- `os.web`",
        "- `os.posix`",
        "",
        "### ABI / Runtime",
        "- `abi.msvc`",
        "- `abi.mingw`",
        "- `abi.glibc`",
        "- `abi.musl`",
        "- `abi.cocoa`",
        "- `abi.carbon`",
        "- `abi.sdl`",
        "- `abi.freestanding`",
        "- `abi.wasm`",
        "- `abi.null`",
        "",
        "## Support Tiers",
        "",
        "| Target | Tier | Platform Family | Built Now | Default Release Index | Supported Products | Default Install Profiles |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        row_map = _as_map(row)
        extensions = _as_map(row_map.get("extensions"))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row_map.get("target_id")),
                _token(row_map.get("tier")),
                _token(extensions.get("platform_id")) or "none",
                "yes" if bool(extensions.get("built_in_mock_release", False)) else "no",
                "yes" if bool(extensions.get("release_index_default", False)) else "no",
                ", ".join(_sorted_unique_strings(row_map.get("supported_products"))) or "none",
                ", ".join(_sorted_unique_strings(row_map.get("default_install_profiles"))) or "none",
            )
        )
    lines.extend(
        [
            "",
            "## Tier Policy",
            "",
            "- Tier 1 targets are official only when they are actually built and pass convergence, clean-room, and platform-matrix gates.",
            "- Tier 2 targets are experimental/planned and may ship CLI/TUI-only or with reduced renderer coverage.",
            "- Tier 3 targets are declared/future only and must never appear in the default downloadable release index.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_target_capability_rules(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PLATFORM/DIST",
        "Replacement Target: release-pinned target policy contracts and trust-gated update selection",
        "",
        "# Target Capability Rules",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Gate Requirements",
        "",
        "- Tier 1 targets must pass `CONVERGENCE-GATE-0`, `DIST-3`, and `DIST-4` before they are treated as shippable.",
        "- Tier 2 targets may ship with deterministic CLI/TUI fallback only and may omit native UI or advanced renderer backends.",
        "- Tier 3 targets are declared only; they must not appear in the default `release_index.json` artifact list.",
        "",
        "## Capability Gating",
        "",
        "- Setup and release-index resolution use the target matrix row plus platform capability registry row for the resolved target.",
        "- CAP-NEG endpoint descriptors must expose `os_id`, `abi_id`, `arch_id`, and `tier` through the `official.*` descriptor extensions.",
        "- Capability overrides in the target matrix are additive filters over the family-level platform capability registry and must remain deterministic.",
        "",
        "## Release Index Policy",
        "",
        "- Only Tier 1 targets that are actually built, plus Tier 2 targets if they are actually built, may appear in the default release index.",
        "- Tier 3 rows remain declared in the target matrix registry but are excluded from default downloadable artifact lists.",
    ]
    return "\n".join(lines) + "\n"


def render_arch_matrix_final(report: Mapping[str, object]) -> str:
    tier_rows = list(report.get("registry_rows") or [])
    built_rows = list(report.get("built_rows") or [])
    release_index_rows = list(report.get("release_index_rows") or [])
    gate_rows = list(report.get("tier1_gate_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PLATFORM/DIST",
        "Replacement Target: release-pinned target matrix and downloadable artifact availability model",
        "",
        "# ARCH-MATRIX Final",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Full Target Matrix Table",
        "",
        "| Target | Tier | Built | Release Index Default | Required Capabilities | Known Missing Features |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in tier_rows:
        row_map = _as_map(row)
        extensions = _as_map(row_map.get("extensions"))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row_map.get("target_id")),
                _token(row_map.get("tier")),
                "yes" if bool(extensions.get("built_in_mock_release", False)) else "no",
                "yes" if bool(extensions.get("release_index_default", False)) else "no",
                ", ".join(_sorted_unique_strings(extensions.get("required_platform_capabilities"))) or "none",
                "; ".join(_sorted_unique_strings(extensions.get("known_missing_features"))) or "none",
            )
        )
    lines.extend(
        [
            "",
            "## Tier Breakdown",
            "",
            "- Tier 1: `{}`".format(_token(_as_map(report.get("tier_breakdown")).get("tier_1"))),
            "- Tier 2: `{}`".format(_token(_as_map(report.get("tier_breakdown")).get("tier_2"))),
            "- Tier 3: `{}`".format(_token(_as_map(report.get("tier_breakdown")).get("tier_3"))),
            "",
            "## Declared vs Built Targets",
            "",
        ]
    )
    if built_rows:
        for row in built_rows:
            lines.append(
                "- Built `{}` -> `{}` (`tier {}`; source `{}`)".format(
                    _token(row.get("platform_tag")),
                    _token(row.get("target_id")) or "unmapped",
                    _token(row.get("tier")),
                    _token(row.get("source_kind")),
                )
            )
    else:
        lines.append("- No built bundle roots were detected.")
    lines.extend(["", "### Release Index Rows", ""])
    if release_index_rows:
        for row in release_index_rows:
            row_map = _as_map(row)
            lines.append("- `{}`".format(_token(row_map.get("release_index_rel"))))
            for platform_row in _as_list(row_map.get("platform_rows")):
                item = _as_map(platform_row)
                lines.append(
                    "  - `{}` / `{}` / `{}` -> `{}` (`tier {}`)".format(
                        _token(item.get("os_id")),
                        _token(item.get("arch_id")),
                        _token(item.get("abi_id")),
                        _token(item.get("target_id")) or "unmapped",
                        _token(item.get("tier")),
                    )
                )
    else:
        lines.append("- No release index candidates were detected.")
    lines.extend(["", "## Readiness", ""])
    if gate_rows:
        for row in gate_rows:
            lines.append(
                "- `{}` -> convergence `{}`, clean-room `{}`, dist-4 `{}`, overall `{}`".format(
                    _token(row.get("target_id")),
                    _token(row.get("convergence_result")),
                    _token(row.get("clean_room_result")),
                    _token(row.get("dist4_result")),
                    _token(row.get("result")),
                )
            )
    else:
        lines.append("- No built Tier 1 targets were detected beyond the declared matrix.")
    lines.append(
        "- Endpoint descriptor target fields present: `{}`".format(
            "`, `".join(_sorted_unique_strings(_as_map(report.get("descriptor_row")).get("present_fields"))) or "none"
        )
    )
    lines.append(
        "- Readiness for TRUST-MODEL-0 and DIST-7 packaging: `{}`".format(
            "ready" if _token(report.get("result")) == "complete" else "blocked"
        )
    )
    return "\n".join(lines) + "\n"


def write_arch_matrix_outputs(repo_root: str, *, write_registry: bool = False) -> dict:
    root = _norm(repo_root)
    registry_payload = build_target_matrix_registry_payload()
    if write_registry:
        _write_json(os.path.join(root, TARGET_MATRIX_REGISTRY_REL), registry_payload)
    report = build_arch_matrix_report(root)
    _write_text(os.path.join(root, RETRO_AUDIT_DOC_REL), render_arch_matrix_retro_audit(report))
    _write_text(os.path.join(root, TARGET_MATRIX_DOC_REL), render_target_matrix_doctrine(report))
    _write_text(os.path.join(root, TARGET_CAPABILITY_RULES_DOC_REL), render_target_capability_rules(report))
    _write_json(os.path.join(root, REPORT_JSON_REL), report)
    _write_text(os.path.join(root, FINAL_DOC_REL), render_arch_matrix_final(report))
    return {
        "report": report,
        "report_json_path": REPORT_JSON_REL,
        "final_doc_path": FINAL_DOC_REL,
        "retro_doc_path": RETRO_AUDIT_DOC_REL,
        "doctrine_doc_path": TARGET_MATRIX_DOC_REL,
        "rules_doc_path": TARGET_CAPABILITY_RULES_DOC_REL,
        "registry_path": TARGET_MATRIX_REGISTRY_REL,
    }


def arch_matrix_violations(repo_root: str, *, report_override: Mapping[str, object] | None = None) -> list[dict]:
    root = _norm(repo_root)
    report = dict(report_override or build_arch_matrix_report(root))
    violations = []
    generated_output_paths = {
        RETRO_AUDIT_DOC_REL,
        TARGET_MATRIX_DOC_REL,
        TARGET_CAPABILITY_RULES_DOC_REL,
        REPORT_JSON_REL,
        FINAL_DOC_REL,
    }
    for rel_path, message, rule_id in (
        (RETRO_AUDIT_DOC_REL, "ARCH-MATRIX-0 retro audit is required", RULE_TARGET_MATRIX),
        (TARGET_MATRIX_DOC_REL, "target matrix doctrine is required", RULE_TARGET_MATRIX),
        (TARGET_CAPABILITY_RULES_DOC_REL, "target capability rules are required", RULE_TARGET_MATRIX),
        (TARGET_MATRIX_REGISTRY_REL, "target matrix registry is required", RULE_TARGET_MATRIX),
        (REPORT_JSON_REL, "target matrix machine report is required", RULE_TARGET_MATRIX),
        (FINAL_DOC_REL, "target matrix final report is required", RULE_TARGET_MATRIX),
        (RUNNER_REL, "target matrix runner is required", RULE_TARGET_MATRIX),
    ):
        if report_override is not None and rel_path in generated_output_paths:
            continue
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": rel_path, "rule_id": rule_id})
    release_rows = []
    for entry in _as_list(report.get("release_index_rows")):
        release_rows.extend(_as_list(_as_map(entry).get("platform_rows")))
    for row in release_rows:
        row_map = _as_map(row)
        if not _token(row_map.get("target_id")) or _as_int(row_map.get("tier"), 0) <= 0:
            violations.append(
                {
                    "code": "release_index_target_unmapped",
                    "message": "default release-index platform rows must resolve to declared target matrix rows",
                    "file_path": _token(row_map.get("release_index_rel")) or "build/tmp/update_model_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json",
                    "rule_id": RULE_TARGET_MATRIX,
                }
            )
            continue
        if int(row_map.get("tier", 0) or 0) <= 2:
            continue
        violations.append(
            {
                "code": "tier3_target_in_release_index",
                "message": "Tier 3 targets must not appear in the default release index",
                "file_path": _token(row_map.get("release_index_rel")) or "build/tmp/update_model_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json",
                "rule_id": RULE_TIER3_RELEASE_INDEX,
            }
        )
    descriptor_row = _as_map(report.get("descriptor_row"))
    if _as_list(descriptor_row.get("missing_fields")):
        violations.append(
            {
                "code": "descriptor_missing_target_fields",
                "message": "Endpoint descriptors must include target ids and tier fields",
                "file_path": "compat/descriptor/descriptor_engine.py",
                "rule_id": RULE_TARGET_MATRIX,
            }
        )
    for row in _as_list(report.get("tier1_gate_rows")):
        row_map = _as_map(row)
        if _token(row_map.get("result")) == "complete":
            continue
        violations.append(
            {
                "code": "tier1_target_gate_incomplete",
                "message": "Built Tier 1 targets must pass convergence, clean-room, and DIST-4 platform matrix gates",
                "file_path": FINAL_DOC_REL,
                "rule_id": RULE_TIER1_GATES,
            }
        )
    if not _as_list(_as_map(load_target_matrix_registry(root).get("record")).get("targets")) and os.path.isfile(
        os.path.join(root, TARGET_MATRIX_REGISTRY_REL.replace("/", os.sep))
    ):
        violations.append(
            {
                "code": "target_matrix_registry_empty",
                "message": "target matrix registry must declare at least one target",
                "file_path": TARGET_MATRIX_REGISTRY_REL,
                "rule_id": RULE_TARGET_MATRIX,
            }
        )
    return sorted(
        [dict(item) for item in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("rule_id")), _token(row.get("code"))),
    )


__all__ = [
    "FINAL_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_TARGET_MATRIX",
    "RULE_TIER1_GATES",
    "RULE_TIER3_RELEASE_INDEX",
    "TARGET_CAPABILITY_RULES_DOC_REL",
    "TARGET_MATRIX_DOC_REL",
    "arch_matrix_violations",
    "build_arch_matrix_report",
    "build_target_matrix_registry_payload",
    "render_arch_matrix_final",
    "write_arch_matrix_outputs",
]
