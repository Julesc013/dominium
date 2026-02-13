"""Runner adapters for XStack gate execution."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple

from .profiler import end_phase, start_phase

_SCRIPTS_DEV = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts", "dev"))
if _SCRIPTS_DEV not in sys.path:
    sys.path.insert(0, _SCRIPTS_DEV)

from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace  # pylint: disable=wrong-import-position


def _run(repo_root: str, command: List[str], env: Dict[str, str], runner_id: str = "") -> Tuple[int, str]:
    phase_name = "subprocess.{}".format(runner_id or "runner")
    is_build = bool(command) and str(command[0]).lower().endswith("cmake") and "--build" in command
    build_phase = "build.{}".format(runner_id or "runner")
    start_phase(phase_name, {"argv": list(command)})
    if is_build:
        start_phase(build_phase, {"argv": list(command)})
    try:
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
    except OSError as exc:
        if is_build:
            end_phase(build_phase, {"returncode": 127})
        end_phase(phase_name, {"returncode": 127})
        return 127, "refuse.command_unresolvable: {}".format(exc)
    if is_build:
        end_phase(build_phase, {"returncode": int(proc.returncode)})
    end_phase(phase_name, {"returncode": int(proc.returncode)})
    return int(proc.returncode), proc.stdout or ""


def _artifact_hash(exit_code: int, output: str, artifacts: List[str]) -> str:
    payload = {
        "exit_code": int(exit_code),
        "output": output,
        "artifacts": sorted(set(artifacts)),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _runner_result(runner_id: str, exit_code: int, output: str, artifacts: List[str]) -> Dict[str, object]:
    return {
        "runner_id": runner_id,
        "exit_code": int(exit_code),
        "output": output,
        "artifacts_produced": sorted(set(artifacts)),
        "output_hash": _artifact_hash(exit_code, output, artifacts),
        "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _coerce_optional_refusal(runner_id: str, exit_code: int, output: str) -> Tuple[int, str]:
    if int(exit_code) == 0:
        return int(exit_code), output
    token = str(runner_id).strip()
    if token != "compatx_runner":
        return int(exit_code), output
    text = str(output or "").strip()
    if not text:
        return int(exit_code), output
    try:
        payload = json.loads(text)
    except ValueError:
        return int(exit_code), output
    if not isinstance(payload, dict):
        return int(exit_code), output
    if str(payload.get("result", "")).strip() != "refused":
        return int(exit_code), output
    refusal_codes = payload.get("refusal_codes") or []
    if not isinstance(refusal_codes, list):
        return int(exit_code), output
    codes = {str(item).strip() for item in refusal_codes if str(item).strip()}
    if "refuse.bundle_optional_flag" not in codes:
        return int(exit_code), output
    payload["result"] = "skipped_optional"
    payload["non_gating"] = True
    payload["original_exit_code"] = int(exit_code)
    return 0, json.dumps(payload, sort_keys=True)


def _resolve_env(repo_root: str, workspace_id: str = "") -> Dict[str, str]:
    ws_id = workspace_id or canonical_workspace_id(repo_root, env=os.environ)
    env, _dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)
    return env


def _execute_command_node(node: Dict[str, object], repo_root: str, env: Dict[str, str]) -> Dict[str, object]:
    runner_id = str(node.get("runner_id", "")).strip()
    command = node.get("command") or []
    if not isinstance(command, list) or not command:
        return _runner_result(runner_id, 2, "refuse.invalid_runner_command", [])
    cmd = []
    for idx, token in enumerate(command):
        value = str(token)
        if idx == 0 and value in ("python", "python3"):
            cmd.append(sys.executable)
        else:
            cmd.append(value.format(repo_root=repo_root))
    exit_code, output = _run(repo_root, cmd, env, runner_id=runner_id)
    exit_code, output = _coerce_optional_refusal(runner_id, exit_code, output)
    artifacts = [str(item) for item in (node.get("expected_artifacts") or []) if str(item).strip()]
    return _runner_result(runner_id, exit_code, output, artifacts)


def repox_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def testx_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def auditx_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def performx_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def compatx_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def securex_runner(node: Dict[str, object], repo_root: str, workspace_id: str = "") -> Dict[str, object]:
    env = _resolve_env(repo_root, workspace_id=workspace_id)
    return _execute_command_node(node, repo_root, env)


def resolve_adapter(runner_id: str):
    key = str(runner_id).strip()
    if key == "repox_runner":
        return repox_runner
    if key.startswith("testx."):
        return testx_runner
    if key.startswith("auditx."):
        return auditx_runner
    if key.startswith("performx."):
        return performx_runner
    if key.startswith("compatx."):
        return compatx_runner
    if key.startswith("securex."):
        return securex_runner
    if key == "testx_runner":
        return testx_runner
    if key == "auditx_runner":
        return auditx_runner
    if key == "performx_runner":
        return performx_runner
    if key == "compatx_runner":
        return compatx_runner
    if key == "securex_runner":
        return securex_runner
    return repox_runner
