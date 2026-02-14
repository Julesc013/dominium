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
from .runners_base import BaseRunner, RunnerContext, RunnerResult

_SCRIPTS_DEV = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts", "dev")
)
if _SCRIPTS_DEV not in sys.path:
    sys.path.insert(0, _SCRIPTS_DEV)

from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace  # pylint: disable=wrong-import-position


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
    return _hash_text(text)


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


def _runner_profile_arg(runner_id: str, plan_profile: str) -> str:
    token = str(plan_profile).strip().upper() or "FAST"
    if str(runner_id).strip() == "repox_runner":
        if token.startswith("STRICT"):
            return "STRICT"
        if token.startswith("FULL"):
            return "FULL"
        return "FAST"
    if token == "FULL_ALL":
        return "FULL"
    return token


def _append_flag(cmd: List[str], flag: str, value: str) -> None:
    if not value:
        return
    token = str(flag).strip()
    if not token:
        return
    if token in cmd:
        return
    cmd.extend([token, value])


def _runner_artifact_root(repo_root: str, runner_id: str, group_id: str, snapshot_mode: bool) -> str:
    if snapshot_mode:
        return ""
    token = str(group_id or runner_id).replace("\\", "/").strip().replace("/", "_")
    if not token:
        token = "runner"
    root = os.path.join(repo_root, ".xstack_cache", "artifacts", token)
    os.makedirs(root, exist_ok=True)
    return root


def _apply_output_routing(
    cmd: List[str],
    runner_id: str,
    group_id: str,
    repo_root: str,
    snapshot_mode: bool,
) -> List[str]:
    routed = list(cmd)
    artifact_root = _runner_artifact_root(repo_root, runner_id, group_id, snapshot_mode)
    if not artifact_root:
        return routed

    if runner_id == "repox_runner":
        _append_flag(routed, "--proof-manifest-out", os.path.join(artifact_root, "proof_manifest.json").replace("\\", "/"))
        _append_flag(routed, "--profile-out", os.path.join(artifact_root, "REPOX_PROFILE.json").replace("\\", "/"))
        return routed

    if runner_id.startswith("testx.") or runner_id == "testx_runner":
        _append_flag(routed, "--summary-json", os.path.join(artifact_root, "TESTX_SUMMARY.json").replace("\\", "/"))
        _append_flag(routed, "--summary-md", os.path.join(artifact_root, "TESTX_SUMMARY.md").replace("\\", "/"))
        _append_flag(routed, "--run-meta-json", os.path.join(artifact_root, "TESTX_RUN_META.json").replace("\\", "/"))
        return routed

    if runner_id.startswith("auditx.") or runner_id == "auditx_runner":
        _append_flag(routed, "--output-root", artifact_root.replace("\\", "/"))
        return routed

    if runner_id == "performx_runner":
        _append_flag(routed, "--output-root", artifact_root.replace("\\", "/"))
        return routed

    if runner_id == "compatx_runner":
        _append_flag(routed, "--output-root", artifact_root.replace("\\", "/"))
        return routed

    if runner_id == "securex_runner":
        _append_flag(routed, "--output-dir", artifact_root.replace("\\", "/"))
        return routed

    return routed


def _normalize_result(runner_id: str, exit_code: int, output: str, artifacts: List[str]) -> RunnerResult:
    return RunnerResult(
        runner_id=runner_id,
        exit_code=int(exit_code),
        output=str(output or ""),
        artifacts_produced=sorted(set(str(item) for item in artifacts if str(item).strip())),
        output_hash=_artifact_hash(exit_code, output, artifacts),
        timestamp_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


class CommandRunner(BaseRunner):
    """Default command-backed runner implementation."""

    def __init__(
        self,
        canonical_id: str,
        produced_artifacts: List[str],
        default_full: bool = False,
        grouped: bool = False,
    ):
        self._canonical_id = canonical_id
        self._produced_artifacts = list(produced_artifacts)
        self._default_full = bool(default_full)
        self._grouped = bool(grouped)

    def runner_id(self) -> str:
        return self._canonical_id

    def input_hash(self, repo_state: str, registries_hash: str, profile: str) -> str:
        payload = {
            "runner_id": self.runner_id(),
            "repo_state": str(repo_state),
            "registries_hash": str(registries_hash),
            "profile": str(profile),
        }
        return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    def produces(self) -> List[str]:
        return sorted(set(self._produced_artifacts))

    def supports_groups(self) -> bool:
        return self._grouped

    def estimate_cost(self, context: RunnerContext) -> int:
        command = context.node.get("command") or []
        if not isinstance(command, list):
            return 1
        return max(1, len(command))

    def default_full_enabled(self) -> bool:
        return self._default_full

    def run(self, context: RunnerContext) -> RunnerResult:
        node = context.node
        runner_id = str(node.get("runner_id", "")).strip() or self.runner_id()
        group_id = str(node.get("group_id", "")).strip()
        command = node.get("command") or []
        if not isinstance(command, list) or not command:
            return _normalize_result(runner_id, 2, "refuse.invalid_runner_command", [])

        profile_arg = _runner_profile_arg(runner_id, context.plan_profile)
        cmd = []
        for idx, token in enumerate(command):
            value = str(token)
            if idx == 0 and value in ("python", "python3"):
                cmd.append(sys.executable)
            else:
                cmd.append(value.format(repo_root=context.repo_root, profile=profile_arg))

        snapshot_mode = str(context.gate_command).strip() == "snapshot"
        cmd = _apply_output_routing(
            cmd=cmd,
            runner_id=runner_id,
            group_id=group_id,
            repo_root=context.repo_root,
            snapshot_mode=snapshot_mode,
        )
        env = _resolve_env(context.repo_root, workspace_id=context.workspace_id)
        env["DOM_XSTACK_SNAPSHOT_MODE"] = "1" if snapshot_mode else "0"
        env["DOM_XSTACK_GATE_COMMAND"] = str(context.gate_command).strip()
        exit_code, output = _run(context.repo_root, cmd, env, runner_id=runner_id)
        exit_code, output = _coerce_optional_refusal(runner_id, exit_code, output)
        artifacts = [str(item) for item in (node.get("expected_artifacts") or []) if str(item).strip()]
        if not artifacts:
            artifacts = self.produces()
        return _normalize_result(runner_id, exit_code, output, artifacts)


_REPOX_RUNNER = CommandRunner(
    "repox_runner",
    produced_artifacts=[
        "docs/audit/proof_manifest.json",
        "docs/audit/repox/REPOX_PROFILE.json",
    ],
)
_TESTX_RUNNER = CommandRunner(
    "testx_runner",
    produced_artifacts=[
        "docs/audit/testx/TESTX_SUMMARY.json",
        "docs/audit/testx/TESTX_RUN_META.json",
    ],
    grouped=True,
)
_AUDITX_RUNNER = CommandRunner(
    "auditx_runner",
    produced_artifacts=[
        "docs/audit/auditx/FINDINGS.json",
        "docs/audit/auditx/INVARIANT_MAP.json",
        "docs/audit/auditx/PROMOTION_CANDIDATES.json",
    ],
    grouped=True,
)
_PERFORMX_RUNNER = CommandRunner(
    "performx_runner",
    produced_artifacts=[
        "docs/audit/performance/PERFORMX_RESULTS.json",
        "docs/audit/performance/PERFORMX_REGRESSIONS.json",
    ],
    default_full=True,
)
_COMPATX_RUNNER = CommandRunner(
    "compatx_runner",
    produced_artifacts=["docs/audit/compat/COMPAT_BASELINE.json"],
    default_full=True,
)
_SECUREX_RUNNER = CommandRunner(
    "securex_runner",
    produced_artifacts=[
        "docs/audit/security/FINDINGS.json",
        "docs/audit/security/INTEGRITY_MANIFEST.json",
    ],
    default_full=True,
)


def resolve_adapter(runner_id: str) -> BaseRunner:
    token = str(runner_id).strip()
    if token == "repox_runner":
        return _REPOX_RUNNER
    if token.startswith("testx.") or token == "testx_runner":
        return _TESTX_RUNNER
    if token.startswith("auditx.") or token == "auditx_runner":
        return _AUDITX_RUNNER
    if token.startswith("performx.") or token == "performx_runner":
        return _PERFORMX_RUNNER
    if token.startswith("compatx.") or token == "compatx_runner":
        return _COMPATX_RUNNER
    if token.startswith("securex.") or token == "securex_runner":
        return _SECUREX_RUNNER
    return _REPOX_RUNNER


def runner_metadata(runner_id: str) -> Dict[str, object]:
    runner = resolve_adapter(runner_id)
    return {
        "runner_id": runner.runner_id(),
        "produces": runner.produces(),
        "supports_groups": bool(runner.supports_groups()),
        "default_full": bool(runner.default_full_enabled()),
    }


def default_full_runner_ids() -> List[str]:
    candidates = (_REPOX_RUNNER, _TESTX_RUNNER, _AUDITX_RUNNER, _PERFORMX_RUNNER, _COMPATX_RUNNER, _SECUREX_RUNNER)
    out = []
    for runner in candidates:
        if runner.default_full_enabled():
            out.append(runner.runner_id())
    return sorted(set(out))


def result_to_dict(result: RunnerResult) -> Dict[str, object]:
    return {
        "runner_id": result.runner_id,
        "exit_code": int(result.exit_code),
        "output": result.output,
        "artifacts_produced": list(result.artifacts_produced),
        "output_hash": result.output_hash,
        "timestamp_utc": result.timestamp_utc,
    }
