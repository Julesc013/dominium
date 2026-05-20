#!/usr/bin/env python3
"""Generate ignored local CMake user presets from build tuples and probe data."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Mapping, Tuple

from build_contract_common import entry_map, load_build_contracts, norm, utc_now, write_json


DEFAULT_OUT = os.path.join(".dominium.local", "CMakeUserPresets.generated.json")


def _load_json(path: str) -> Dict[str, Any]:
    if not path or not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _preset_name(tuple_id: str) -> str:
    return "tuple.{}".format(tuple_id)


def _generator_for_tuple(tuple_id: str, row: Mapping[str, Any], toolchains: Mapping[str, Dict[str, Any]], probe: Mapping[str, Any]) -> Tuple[str, str, Dict[str, str], str]:
    toolchain_id = str(row.get("toolchain") or "")
    toolchain = dict(toolchains.get(toolchain_id) or {})
    generator = str(toolchain.get("cmake_generator") or "")
    architecture = "x64" if str(row.get("arch") or "") == "x64" else ""
    cache: Dict[str, str] = {
        "DOM_BUILD_MODE": "Debug" if str(row.get("config") or "") == "debug" else "Release",
        "DOM_BUILD_TOOLS": "ON",
        "DOM_BUILD_SETUP": "ON",
        "DOM_BUILD_LAUNCHER": "ON",
        "DOM_BUILD_GAME": "ON",
        "DOM_BUILD_TESTS": "ON" if str(row.get("intent") or "") == "verify" else "OFF",
        "CMAKE_C_STANDARD": "17",
        "CMAKE_C_STANDARD_REQUIRED": "ON",
        "CMAKE_C_EXTENSIONS": "OFF",
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_STANDARD_REQUIRED": "ON",
        "CMAKE_CXX_EXTENSIONS": "OFF",
    }
    inherits = ""
    if toolchain_id == "msvc143":
        inherits = "verify-win-vs2026" if str(row.get("intent") or "") == "verify" else "dev-win-vs2026"
        generator = ""
    elif toolchain_id == "msvc145":
        generator = "Visual Studio 18 2026"
    elif toolchain_id == "gcc":
        generator = "Ninja"
        cache["CMAKE_C_COMPILER"] = "gcc"
        cache["CMAKE_CXX_COMPILER"] = "g++"
    elif toolchain_id == "clang":
        generator = "Ninja"
        if dict(probe.get("clang_cl") or {}).get("found"):
            cache["CMAKE_C_COMPILER"] = "clang-cl"
            cache["CMAKE_CXX_COMPILER"] = "clang-cl"
        else:
            cache["CMAKE_C_COMPILER"] = "clang"
            cache["CMAKE_CXX_COMPILER"] = "clang++"
    elif toolchain_id == "host_default":
        available = list(probe.get("available_toolchain_ids") or [])
        if "msvc143" in available:
            inherits = "verify-win-vs2026"
            generator = ""
        elif "gcc" in available:
            generator = "Ninja"
            cache["CMAKE_C_COMPILER"] = "gcc"
            cache["CMAKE_CXX_COMPILER"] = "g++"
        elif "clang" in available:
            generator = "Ninja"
            cache["CMAKE_C_COMPILER"] = "clang"
            cache["CMAKE_CXX_COMPILER"] = "clang++"
    return generator, architecture, cache, inherits


def build_user_presets(repo_root: str, probe: Mapping[str, Any]) -> Dict[str, Any]:
    contracts = load_build_contracts(repo_root)
    tuples = entry_map(contracts["tuples"], "tuples")
    toolchains = entry_map(contracts["toolchains"], "toolchains")
    available = set(str(item) for item in list(probe.get("available_toolchain_ids") or []))
    configure_presets: List[Dict[str, Any]] = []
    build_presets: List[Dict[str, Any]] = []
    test_presets: List[Dict[str, Any]] = []
    mapping: Dict[str, Dict[str, str]] = {}
    blocked: Dict[str, str] = {}
    for tuple_id, row in sorted(tuples.items()):
        toolchain_id = str(row.get("toolchain") or "")
        if toolchain_id not in available:
            blocked[tuple_id] = "toolchain {} is not available in probe output".format(toolchain_id)
            continue
        name = _preset_name(tuple_id)
        generator, architecture, cache, inherits = _generator_for_tuple(tuple_id, row, toolchains, probe)
        configure: Dict[str, Any] = {
            "name": name,
            "displayName": "Generated {}".format(tuple_id),
            "description": "Generated local preset for Dominium tuple {}; not source authority.".format(tuple_id),
            "binaryDir": "${sourceDir}/.dominium.local/build/${presetName}",
            "cacheVariables": cache,
        }
        if inherits:
            configure["inherits"] = inherits
        if generator:
            configure["generator"] = generator
        if architecture:
            configure["architecture"] = architecture
        configure_presets.append(configure)
        build_presets.append({"name": name, "configurePreset": name, "configuration": "Debug" if str(row.get("config") or "") == "debug" else "Release"})
        test_presets.append(
            {
                "name": name,
                "configurePreset": name,
                "configuration": "Debug" if str(row.get("config") or "") == "debug" else "Release",
                "output": {"outputOnFailure": True},
            }
        )
        mapping[tuple_id] = {"configurePreset": name, "buildPreset": name, "testPreset": name}
    return {
        "version": 6,
        "cmakeMinimumRequired": {"major": 3, "minor": 21, "patch": 0},
        "configurePresets": configure_presets,
        "buildPresets": build_presets,
        "testPresets": test_presets,
        "vendor": {
            "dominium.local/generated": {
                "generated": True,
                "generated_at_utc": utc_now(),
                "source": "tools/build/generate_user_presets.py",
                "tuples": mapping,
                "blocked_tuples": blocked,
            }
        },
    }


def _summary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    vendor = dict(payload.get("vendor") or {}).get("dominium.local/generated") or {}
    return {
        "generated_configure_presets": [row.get("name") for row in list(payload.get("configurePresets") or [])],
        "generated_tuple_ids": sorted(dict(vendor.get("tuples") or {}).keys()),
        "blocked_tuple_ids": sorted(dict(vendor.get("blocked_tuples") or {}).keys()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Dominium local CMake user presets.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--probe", default="")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    probe_path = args.probe
    if probe_path and not os.path.isabs(probe_path):
        probe_path = os.path.join(repo_root, probe_path)
    probe = _load_json(probe_path)
    payload = build_user_presets(repo_root, probe)
    summary = _summary(payload)
    out_path = args.out
    if not os.path.isabs(out_path):
        out_path = os.path.join(repo_root, out_path)
    if args.dry_run:
        print(json.dumps({"result": "dry_run", "out": norm(os.path.relpath(out_path, repo_root)), **summary}, indent=2, sort_keys=True))
        return 0
    if os.path.basename(out_path) == "CMakeUserPresets.json" and os.path.exists(out_path) and not args.force:
        print("refusing to overwrite existing CMakeUserPresets.json without --force")
        return 2
    write_json(out_path, payload)
    print(json.dumps({"result": "written", "out": norm(os.path.relpath(out_path, repo_root)), **summary}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
