#!/usr/bin/env python3
"""Probe local toolchains for Dominium build tuple generation."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from typing import Any, Dict, List, Optional

from build_contract_common import (
    cmake_version_from_output,
    extract_cmake_generators,
    norm,
    run_command,
    utc_now,
    write_json,
)


KNOWN_TOOLCHAINS = [
    "host_default",
    "msvc143",
    "msvc145",
    "msvc141",
    "msvc141_xp",
    "gcc",
    "clang",
    "xcode9",
    "codewarrior9",
]


def _probe_program(name: str, version_args: List[str]) -> Dict[str, Any]:
    path = shutil.which(name) or ""
    row: Dict[str, Any] = {"command": name, "found": bool(path), "path_found": bool(path), "version": "", "returncode": None}
    if path:
        result = run_command([name] + version_args, timeout=10)
        row["returncode"] = result["returncode"]
        output = (result["stdout"] or result["stderr"] or "").strip().splitlines()
        row["version"] = output[0] if output else ""
    return row


def _find_vswhere() -> str:
    direct = shutil.which("vswhere")
    if direct:
        return direct
    candidates = []
    for env_name in ("ProgramFiles(x86)", "ProgramFiles"):
        root = os.environ.get(env_name)
        if root:
            candidates.append(os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"))
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return ""


def _probe_visual_studio() -> List[Dict[str, Any]]:
    vswhere = _find_vswhere()
    if not vswhere:
        env_dir = os.environ.get("VSINSTALLDIR", "")
        if env_dir:
            return [
                {
                    "source": "VSINSTALLDIR",
                    "display_name": "Visual Studio from environment",
                    "installation_version": "",
                    "major_version": "",
                    "has_install_path": True,
                }
            ]
        return []
    result = run_command(
        [
            vswhere,
            "-all",
            "-products",
            "*",
            "-requires",
            "Microsoft.Component.MSBuild",
            "-format",
            "json",
        ],
        timeout=20,
    )
    if result["returncode"] != 0:
        return []
    try:
        raw_items = json.loads(result["stdout"] or "[]")
    except json.JSONDecodeError:
        return []
    instances = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        version = str(item.get("installationVersion") or "")
        instances.append(
            {
                "source": "vswhere",
                "display_name": str(item.get("displayName") or ""),
                "installation_version": version,
                "major_version": version.split(".", 1)[0] if version else "",
                "product_id": str(item.get("productId") or ""),
                "has_install_path": bool(item.get("installationPath")),
            }
        )
    return instances


def _msvc_available(instances: List[Dict[str, Any]], major: str) -> bool:
    for item in instances:
        if str(item.get("major_version") or "") == major:
            return True
    return False


def build_probe(repo_root: str) -> Dict[str, Any]:
    cmake_version = run_command(["cmake", "--version"], cwd=repo_root)
    cmake_help = run_command(["cmake", "--help"], cwd=repo_root)
    generators = extract_cmake_generators(cmake_help["stdout"] or "")
    ninja = _probe_program("ninja", ["--version"])
    gcc = _probe_program("gcc", ["--version"])
    gxx = _probe_program("g++", ["--version"])
    clang = _probe_program("clang", ["--version"])
    clangxx = _probe_program("clang++", ["--version"])
    clangcl = _probe_program("clang-cl", ["--version"])
    cl = _probe_program("cl", [])
    nmake = _probe_program("nmake", ["/?"])
    mingw_make = _probe_program("mingw32-make", ["--version"])
    make = _probe_program("make", ["--version"])
    xcodebuild = _probe_program("xcodebuild", ["-version"]) if platform.system() == "Darwin" else {"command": "xcodebuild", "found": False}
    msvc_instances = _probe_visual_studio() if platform.system() == "Windows" else []

    available: List[str] = []
    notes: List[str] = []
    has_build_tool = bool(ninja.get("found") or nmake.get("found") or mingw_make.get("found") or make.get("found"))
    if _msvc_available(msvc_instances, "17"):
        available.append("msvc143")
    else:
        notes.append("Visual Studio 17 2022 instance not detected.")
    if _msvc_available(msvc_instances, "18"):
        available.append("msvc145")
    else:
        notes.append("Visual Studio 18 2026 instance not detected.")
    if _msvc_available(msvc_instances, "15"):
        available.append("msvc141")
    else:
        notes.append("Visual Studio 15 2017 instance not detected.")
    if _msvc_available(msvc_instances, "15"):
        available.append("msvc141_xp")
    if gcc.get("found") and gxx.get("found") and has_build_tool:
        available.append("gcc")
    else:
        notes.append("GCC tuple unavailable because gcc/g++ and a build tool were not both detected.")
    if (clang.get("found") and clangxx.get("found") and has_build_tool) or (clangcl.get("found") and has_build_tool):
        available.append("clang")
    else:
        notes.append("Clang tuple unavailable because clang/clang++ or clang-cl plus a build tool were not detected.")
    if platform.system() == "Darwin" and xcodebuild.get("found"):
        available.append("xcode9")
    if any(item in available for item in ("msvc143", "msvc145", "gcc", "clang", "xcode9")):
        available.append("host_default")
    else:
        notes.append("No host_default tuple is available because no usable compiler/build-tool pair was detected.")
    blocked = [item for item in KNOWN_TOOLCHAINS if item not in set(available)]

    return {
        "generated_at_utc": utc_now(),
        "repo_root": ".",
        "host_platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_executable_present": bool(sys.executable),
        },
        "python_version": platform.python_version(),
        "cmake_version": cmake_version_from_output(cmake_version["stdout"] or cmake_version["stderr"] or ""),
        "cmake_generators": generators,
        "ninja": ninja,
        "msvc_instances": msvc_instances,
        "gcc": gcc,
        "gxx": gxx,
        "clang": clang,
        "clangxx": clangxx,
        "clang_cl": clangcl,
        "cl": cl,
        "nmake": nmake,
        "mingw32_make": mingw_make,
        "make": make,
        "xcode": xcodebuild,
        "available_toolchain_ids": sorted(set(available)),
        "blocked_toolchain_ids": blocked,
        "notes": notes,
    }


def _print_text(report: Dict[str, Any]) -> None:
    print("Dominium toolchain probe")
    print("host: {system} {release} {machine}".format(**dict(report.get("host_platform") or {})))
    print("python: {}".format(report.get("python_version") or ""))
    print("cmake: {}".format(report.get("cmake_version") or "not found"))
    print("available_toolchain_ids: {}".format(", ".join(report.get("available_toolchain_ids") or []) or "none"))
    print("blocked_toolchain_ids: {}".format(", ".join(report.get("blocked_toolchain_ids") or []) or "none"))
    print("")
    for note in report.get("notes") or []:
        print("- {}".format(note))


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe local Dominium build toolchains.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    report = build_probe(repo_root)
    if args.out:
        out_path = args.out
        if not os.path.isabs(out_path):
            out_path = os.path.join(repo_root, out_path)
        write_json(out_path, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
