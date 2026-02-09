#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
from typing import Dict, List, Tuple


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _run(cmd: List[str], cwd: str, timeout_s: int) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        timeout=timeout_s,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _bin(repo_root: str, build_root: str, name: str) -> str:
    return os.path.join(build_root, "bin", name)


def _tool(repo_root: str, name: str) -> str:
    return os.path.join(repo_root, "dist", "sys", "winnt", "x64", "bin", "tools", name)


def _check_entry(entry: Dict[str, object], cwd: str, timeout_s: int) -> Dict[str, object]:
    path = str(entry["path"])
    cmd = [path] + list(entry.get("args", []))
    allowed = set(entry.get("allowed_exit_codes", [0]))
    if not os.path.isfile(path):
        return {
            "name": entry["name"],
            "status": "missing",
            "path": _norm(path),
            "cmd": [_norm(c) for c in cmd],
            "exit_code": None,
            "allowed_exit_codes": sorted(allowed),
        }
    code, out, err = _run(cmd, cwd, timeout_s)
    ok = code in allowed
    return {
        "name": entry["name"],
        "status": "ok" if ok else "fail",
        "path": _norm(path),
        "cmd": [_norm(c) for c in cmd],
        "exit_code": code,
        "allowed_exit_codes": sorted(allowed),
        "stdout": out.strip(),
        "stderr": err.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded runtime smoke checks for app/tool surfaces.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--build-root", default="")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    if args.build_root:
        build_root = os.path.abspath(args.build_root)
    else:
        build_root = os.path.join(repo_root, "out", "build", "vs2026", "verify")
    control_registry = os.path.join(repo_root, "data", "registries", "control_capabilities.registry")

    probe_cwd = tempfile.mkdtemp(prefix="dominium_smoke_cwd_")
    checks: List[Dict[str, object]] = [
        {"name": "setup.help", "path": _bin(repo_root, build_root, "setup.exe"), "args": ["--help"]},
        {"name": "launcher.help", "path": _bin(repo_root, build_root, "launcher.exe"), "args": ["--help"]},
        {"name": "client.help", "path": _bin(repo_root, build_root, "client.exe"), "args": ["--help"]},
        {"name": "server.help", "path": _bin(repo_root, build_root, "server.exe"), "args": ["--help"]},
        {"name": "launcher_tui.help", "path": _bin(repo_root, build_root, "launcher_tui.exe"), "args": ["--help"]},
        {"name": "launcher_gui.help", "path": _bin(repo_root, build_root, "launcher_gui.exe"), "args": ["--help"]},
        {
            "name": "launcher.smoke.cli",
            "path": _bin(repo_root, build_root, "launcher.exe"),
            "args": ["--ui=none", "--control-registry", control_registry, "--smoke"],
        },
        {"name": "client.smoke.cli", "path": _bin(repo_root, build_root, "client.exe"), "args": ["--ui=none", "--smoke"]},
        {"name": "server.smoke.cli", "path": _bin(repo_root, build_root, "server.exe"), "args": ["--ui=none", "--smoke"]},
        {
            "name": "setup.smoke.cli",
            "path": _bin(repo_root, build_root, "setup.exe"),
            "args": ["--ui=none", "--control-registry", control_registry, "--smoke"],
        },
        {
            "name": "launcher.mode.tui.refusal",
            "path": _bin(repo_root, build_root, "launcher.exe"),
            "args": ["--ui=tui", "--smoke"],
            "allowed_exit_codes": [2],
        },
        {
            "name": "launcher.mode.gui.refusal",
            "path": _bin(repo_root, build_root, "launcher.exe"),
            "args": ["--ui=gui", "--headless", "--smoke"],
            "allowed_exit_codes": [2],
        },
        {"name": "tool_ui_validate.help", "path": _tool(repo_root, "tool_ui_validate.exe"), "args": ["--help"]},
        {"name": "tool_ui_doc_annotate.help", "path": _tool(repo_root, "tool_ui_doc_annotate.exe"), "args": ["--help"]},
        {"name": "tool_ui_bind.check", "path": _tool(repo_root, "tool_ui_bind.exe"), "args": ["--repo-root", repo_root, "--check"]},
    ]

    results = [_check_entry(entry, probe_cwd, args.timeout_seconds) for entry in checks]
    failures = [row for row in results if row["status"] in ("fail", "missing")]
    payload = {
        "result": "ok" if not failures else "fail",
        "repo_root": _norm(repo_root),
        "build_root": _norm(build_root),
        "probe_cwd": _norm(probe_cwd),
        "checks": results,
    }

    out_text = json.dumps(payload, indent=2, sort_keys=False)
    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(out_text)
            handle.write("\n")
    print(out_text)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
