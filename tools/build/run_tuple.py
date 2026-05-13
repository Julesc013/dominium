#!/usr/bin/env python3
"""Run a generated Dominium build tuple through CMake."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Mapping

from build_contract_common import command_line, norm, run_command


DEFAULT_PRESET_FILES = (
    os.path.join(".dominium.local", "CMakeUserPresets.generated.json"),
    "CMakeUserPresets.json",
)


def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _find_mapping(repo_root: str, tuple_id: str) -> Dict[str, Any]:
    checked: List[str] = []
    for rel_path in DEFAULT_PRESET_FILES:
        path = os.path.join(repo_root, rel_path)
        checked.append(rel_path)
        payload = _load_json(path)
        vendor = dict(payload.get("vendor") or {}).get("dominium.local/generated") or {}
        tuples = dict(vendor.get("tuples") or {})
        blocked = dict(vendor.get("blocked_tuples") or {})
        if tuple_id in tuples:
            row = dict(tuples[tuple_id])
            row["preset_file"] = norm(rel_path)
            return row
        if tuple_id in blocked:
            return {"blocked": str(blocked[tuple_id]), "preset_file": norm(rel_path)}
    return {"blocked": "no generated local preset mapping found; run tools/build/generate_user_presets.py", "checked": checked}


def _phase_commands(mapping: Mapping[str, Any], phases: List[str]) -> List[List[str]]:
    commands: List[List[str]] = []
    if "configure" in phases:
        commands.append(["cmake", "--preset", str(mapping.get("configurePreset") or "")])
    if "build" in phases:
        commands.append(["cmake", "--build", "--preset", str(mapping.get("buildPreset") or "")])
    if "test" in phases:
        commands.append(["ctest", "--preset", str(mapping.get("testPreset") or "")])
    return commands


def build_report(repo_root: str, tuple_id: str, phases: List[str], execute: bool) -> Dict[str, Any]:
    mapping = _find_mapping(repo_root, tuple_id)
    if mapping.get("blocked"):
        return {
            "tuple": tuple_id,
            "result": "blocked",
            "blocked_reason": mapping.get("blocked"),
            "mapping": mapping,
            "commands": [],
            "runs": [],
        }
    commands = _phase_commands(mapping, phases)
    runs = []
    for command in commands:
        if execute:
            result = run_command(command, cwd=repo_root, timeout=1200)
            runs.append(
                {
                    "command": command_line(command),
                    "returncode": result["returncode"],
                    "ok": result["ok"],
                    "stdout_tail": "\n".join((result["stdout"] or "").splitlines()[-25:]),
                    "stderr_tail": "\n".join((result["stderr"] or "").splitlines()[-25:]),
                }
            )
            if result["returncode"] != 0:
                break
        else:
            runs.append({"command": command_line(command), "returncode": None, "ok": None})
    status = "pass"
    if not execute:
        status = "dry_run"
    elif any(not bool(row.get("ok")) for row in runs):
        status = "fail"
    return {"tuple": tuple_id, "result": status, "mapping": mapping, "commands": [command_line(cmd) for cmd in commands], "runs": runs}


def _print_text(report: Mapping[str, Any]) -> None:
    print("Dominium tuple run")
    print("tuple: {}".format(report.get("tuple")))
    print("result: {}".format(report.get("result")))
    if report.get("blocked_reason"):
        print("blocked_reason: {}".format(report.get("blocked_reason")))
        return
    for command in report.get("commands") or []:
        print("- {}".format(command))
    for row in report.get("runs") or []:
        if row.get("returncode") is not None:
            print("  returncode {}: {}".format(row.get("returncode"), row.get("command")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a generated Dominium build tuple.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--tuple", required=True, dest="tuple_id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--configure", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    phases: List[str] = []
    if args.all:
        phases = ["configure", "build", "test"]
    else:
        if args.configure:
            phases.append("configure")
        if args.build:
            phases.append("build")
        if args.test:
            phases.append("test")
    if not phases:
        phases = ["configure", "build", "test"]
    execute = not args.dry_run and any((args.configure, args.build, args.test, args.all))
    report = build_report(repo_root, args.tuple_id, phases, execute)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    if report.get("result") == "blocked":
        return 2
    if report.get("result") == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
