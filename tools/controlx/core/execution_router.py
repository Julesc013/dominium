"""Execution router that forces gate.py orchestration."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, Dict, List


MECHANICAL_MARKERS = (
    "INV-TOOLS-DIR-MISSING",
    "INV-DIST-MISSING",
    "INV-DERIVED-STALE",
    "INV-PKG-INDEX-MISSING",
    "refuse.command_unresolvable",
    "UI_BIND_ERROR",
)


def _run_command(repo_root: str, command: List[str], env: Dict[str, str]) -> Dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return {
        "command": list(command),
        "returncode": int(proc.returncode),
        "output": proc.stdout or "",
    }


def _is_mechanical_failure(output: str) -> bool:
    text = str(output or "")
    for marker in MECHANICAL_MARKERS:
        if marker in text:
            return True
    return False


def run_gate(repo_root: str, ws_id: str, gate_command: str, env: Dict[str, str]) -> Dict[str, Any]:
    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    command = [sys.executable, gate_script, gate_command, "--repo-root", repo_root, "--workspace-id", ws_id]
    return _run_command(repo_root, command, env)


def route_execution(
    repo_root: str,
    ws_id: str,
    env: Dict[str, str],
    dry_run: bool = False,
    simulate_mechanical_failure: bool = False,
) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []

    if dry_run:
        steps.append(
            {
                "command": ["python", "scripts/dev/gate.py", "precheck"],
                "returncode": 1 if simulate_mechanical_failure else 0,
                "output": "INV-TOOLS-DIR-MISSING" if simulate_mechanical_failure else "dry-run pass",
            }
        )
        if simulate_mechanical_failure:
            steps.append(
                {
                    "command": ["python", "scripts/dev/gate.py", "remediate"],
                    "returncode": 0,
                    "output": "dry-run remediation applied",
                }
            )
            steps.append(
                {
                    "command": ["python", "scripts/dev/gate.py", "precheck"],
                    "returncode": 0,
                    "output": "dry-run pass after remediation",
                }
            )
        steps.append(
            {
                "command": ["python", "scripts/dev/gate.py", "exitcheck"],
                "returncode": 0,
                "output": "dry-run pass",
            }
        )
        return {
            "returncode": 0,
            "steps": steps,
            "mechanical_failure": bool(simulate_mechanical_failure),
            "semantic_failure": False,
        }

    precheck = run_gate(repo_root, ws_id, "precheck", env)
    steps.append(precheck)
    if precheck["returncode"] != 0:
        if _is_mechanical_failure(precheck.get("output", "")):
            remediate = run_gate(repo_root, ws_id, "remediate", env)
            steps.append(remediate)
            precheck_retry = run_gate(repo_root, ws_id, "precheck", env)
            steps.append(precheck_retry)
            if precheck_retry["returncode"] != 0:
                return {
                    "returncode": int(precheck_retry["returncode"]),
                    "steps": steps,
                    "mechanical_failure": True,
                    "semantic_failure": False,
                }
        else:
            return {
                "returncode": int(precheck["returncode"]),
                "steps": steps,
                "mechanical_failure": False,
                "semantic_failure": True,
            }

    exitcheck = run_gate(repo_root, ws_id, "exitcheck", env)
    steps.append(exitcheck)
    if exitcheck["returncode"] != 0 and _is_mechanical_failure(exitcheck.get("output", "")):
        remediate = run_gate(repo_root, ws_id, "remediate", env)
        steps.append(remediate)
        exit_retry = run_gate(repo_root, ws_id, "exitcheck", env)
        steps.append(exit_retry)
        return {
            "returncode": int(exit_retry["returncode"]),
            "steps": steps,
            "mechanical_failure": True,
            "semantic_failure": int(exit_retry["returncode"]) != 0,
        }

    return {
        "returncode": int(exitcheck["returncode"]),
        "steps": steps,
        "mechanical_failure": False,
        "semantic_failure": int(exitcheck["returncode"]) != 0,
    }

