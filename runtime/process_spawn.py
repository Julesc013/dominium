"""Deterministic local process spawn helpers for server and AppShell flows."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm


SERVER_MAIN_REL = os.path.join("server", "server_main.py")
SPAWN_ENV_KEYS = (
    "COMSPEC",
    "PATH",
    "PATHEXT",
    "PYTHONIOENCODING",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "WINDIR",
)


def _repo_rel_path(repo_root: str, path: str) -> str:
    token = str(path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return norm(os.path.relpath(os.path.normpath(token), os.path.normpath(repo_root)))
    return norm(token)


def _spawn_env(base_env: Mapping[str, object] | None = None) -> dict:
    source = dict(os.environ if base_env is None else base_env)
    env = {}
    for key in sorted(SPAWN_ENV_KEYS):
        value = str(source.get(key, "")).strip()
        if value:
            env[str(key)] = value
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONIOENCODING"] = str(env.get("PYTHONIOENCODING", "utf-8")).strip() or "utf-8"
    return dict((key, env[key]) for key in sorted(env.keys()))


def build_server_process_spec(
    *,
    repo_root: str,
    session_spec_path: str,
    seed: str,
    profile_bundle_path: str,
    pack_lock_path: str,
    contract_bundle_hash: str,
    server_config_id: str,
    authority_mode: str,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    session_spec_rel = _repo_rel_path(repo_root_abs, session_spec_path)
    pack_lock_rel = _repo_rel_path(repo_root_abs, pack_lock_path)
    profile_bundle_rel = _repo_rel_path(repo_root_abs, profile_bundle_path)
    args = [
        SERVER_MAIN_REL.replace("/", os.sep),
        "--repo-root",
        ".",
        "--session-spec-path",
        session_spec_rel,
        "--seed",
        str(seed or "0").strip() or "0",
        "--profile-bundle",
        profile_bundle_rel,
        "--pack-lock",
        pack_lock_rel,
        "--server-config-id",
        str(server_config_id or "server.mvp_default").strip() or "server.mvp_default",
        "--contract-bundle-hash",
        str(contract_bundle_hash or "").strip(),
        "--authority",
        str(authority_mode or "dev").strip() or "dev",
    ]
    payload = {
        "spawn_id": "spawn.server.local_singleplayer",
        "spawn_kind": "process_preferred",
        "executable": os.path.normpath(sys.executable),
        "cwd": repo_root_abs,
        "script_rel": norm(SERVER_MAIN_REL),
        "args": [str(item) for item in args],
        "env": _spawn_env(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_python_process_spec(
    *,
    repo_root: str,
    spawn_id: str,
    script_path: str,
    module_name: str = "",
    args: list[str] | tuple[str, ...],
    cwd: str = "",
    env: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    script_rel = _repo_rel_path(repo_root_abs, script_path)
    module_token = str(module_name or "").strip()
    argv = [str(item) for item in list(args or []) if str(item).strip()]
    if module_token:
        process_args = ["-m", module_token] + argv
        spawn_kind = "python_module"
    else:
        process_args = [str(script_rel).strip()] + argv
        spawn_kind = "python_process"
    payload = {
        "spawn_id": str(spawn_id or "spawn.python").strip() or "spawn.python",
        "spawn_kind": spawn_kind,
        "executable": os.path.normpath(sys.executable),
        "cwd": os.path.normpath(os.path.abspath(str(cwd or repo_root_abs))),
        "script_rel": str(script_rel).strip(),
        "module_name": module_token,
        "args": process_args,
        "env": _spawn_env(env),
        "deterministic_fingerprint": "",
        "extensions": dict((str(key), str(value)) for key, value in sorted(dict(extensions or {}).items(), key=lambda item: str(item[0]))),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def spawn_process(process_spec: Mapping[str, object]) -> dict:
    spec = dict(process_spec or {})
    executable = os.path.normpath(str(spec.get("executable", "")).strip() or sys.executable)
    cwd = os.path.normpath(str(spec.get("cwd", "")).strip() or os.getcwd())
    args = [str(item) for item in list(spec.get("args") or []) if str(item).strip()]
    env = dict((str(key), str(value)) for key, value in sorted(dict(spec.get("env") or {}).items(), key=lambda item: str(item[0])))
    process = subprocess.Popen(
        [executable] + args,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "result": "complete",
        "process": process,
        "pid": int(process.pid or 0),
        "deterministic_fingerprint": str(spec.get("deterministic_fingerprint", "")).strip(),
    }


def poll_process(process: object) -> dict:
    proc = process if isinstance(process, subprocess.Popen) else None
    if proc is None:
        return {"result": "refused", "reason": "invalid_process_handle"}
    exit_code = proc.poll()
    if exit_code is None:
        return {"result": "running", "pid": int(proc.pid or 0)}
    return {
        "result": "exited",
        "pid": int(proc.pid or 0),
        "exit_code": int(exit_code),
    }


def collect_process_output(process: object) -> dict:
    proc = process if isinstance(process, subprocess.Popen) else None
    if proc is None:
        return {"result": "refused", "reason": "invalid_process_handle"}
    status = poll_process(proc)
    if str(status.get("result", "")) != "exited":
        return {"result": "running", "pid": int(proc.pid or 0), "stdout_text": "", "stderr_text": ""}
    stdout_text, stderr_text = proc.communicate()
    return {
        "result": "complete",
        "pid": int(proc.pid or 0),
        "exit_code": int(status.get("exit_code", 0) or 0),
        "stdout_text": str(stdout_text or ""),
        "stderr_text": str(stderr_text or ""),
    }
