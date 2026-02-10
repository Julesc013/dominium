#!/usr/bin/env python3
"""Canonical gate runner with self-healing tool discoverability."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

from env_tools_lib import (
    CANONICAL_TOOL_IDS,
    canonical_tools_dir,
    default_host_path,
    detect_repo_root,
    prepend_tools_to_path,
    resolve_tool,
)


VERIFY_BUILD_DIR_REL = os.path.join("out", "build", "vs2026", "verify")
REMEDIATION_ROOT_REL = os.path.join("docs", "audit", "remediation")
REPOX_SCRIPT_REL = os.path.join("scripts", "ci", "check_repox_rules.py")


def _repo_root(arg_value):
    if arg_value:
        return os.path.normpath(os.path.abspath(arg_value))
    return detect_repo_root(os.getcwd(), __file__)


def _canonical_env(repo_root, base_env=None):
    env = dict(base_env or os.environ)
    tools_dir = canonical_tools_dir(repo_root)
    base_path = env.get("PATH", "")
    if not base_path:
        base_path = env.get("DOM_HOST_PATH", "") or os.environ.get("PATH", "")
    if not base_path:
        base_path = default_host_path()
    env["PATH"] = base_path
    env = prepend_tools_to_path(env, tools_dir)
    env["DOM_HOST_PATH"] = base_path
    return env, tools_dir


def _run(cmd, repo_root, env):
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return {
        "command": cmd,
        "returncode": int(proc.returncode),
        "output": proc.stdout,
    }


def _failure_score(output):
    score = 0
    for marker in ("INV-TOOLS-DIR-MISSING", "INV-TOOL-UNRESOLVABLE", "INV-TOOLS-PATH-SET"):
        score += output.count(marker)
    return score


def _tool_build_attempts():
    return (
        ("ui_bind_phase",),
        ("dominium-tools",),
        ("tool_ui_bind", "tool_ui_validate", "tool_ui_doc_annotate"),
    )


def _attempt_tool_remediation(repo_root, env, attempted):
    for targets in _tool_build_attempts():
        if targets in attempted:
            continue
        attempted.add(targets)
        cmd = [
            "cmake",
            "--build",
            VERIFY_BUILD_DIR_REL,
            "--config",
            "Debug",
            "--target",
        ] + list(targets)
        result = _run(cmd, repo_root, env)
        result["strategy"] = "build_tools"
        result["targets"] = list(targets)
        return result
    return None


def _artifact_dir(repo_root, gate_name, blocker_type):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rel = os.path.join(
        REMEDIATION_ROOT_REL,
        "{}_{}_{}".format(stamp, gate_name, blocker_type),
    )
    abs_path = os.path.join(repo_root, rel)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path, rel.replace("\\", "/")


def _write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_remediation_bundle(repo_root, gate_name, blocker_type, failure, actions, verification):
    out_dir, out_rel = _artifact_dir(repo_root, gate_name, blocker_type)
    _write_json(os.path.join(out_dir, "failure.json"), failure)
    _write_json(os.path.join(out_dir, "actions_taken.json"), {"actions": actions})
    _write_json(os.path.join(out_dir, "verification.json"), verification)
    _write_json(
        os.path.join(out_dir, "prevention_links.json"),
        {
            "docs": [
                "docs/governance/GATE_AUTONOMY_POLICY.md",
                "docs/governance/REPOX_TOOL_RULES.md",
                "docs/dev/DEV_COMMANDS.md",
            ],
            "tests": [
                "tests/app/tool_discoverability_tests.py",
                "tests/invariant/repox_rules_tests.py",
            ],
        },
    )
    with open(os.path.join(out_dir, "diff_summary.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("non-mutating gate run\n")
        for item in verification.get("commands", []):
            handle.write("{} => {}\n".format(" ".join(item.get("command", [])), item.get("returncode")))
    with open(os.path.join(out_dir, "failure.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# Gate Remediation Failure\n\n")
        handle.write("- gate: `{}`\n".format(gate_name))
        handle.write("- blocker_type: `{}`\n".format(blocker_type))
        handle.write("- artifact_dir: `{}`\n\n".format(out_rel))
        handle.write("## Failure Output\n\n```\n{}\n```\n".format(failure.get("output", "").strip()))


def _run_repox(repo_root, env):
    cmd = [sys.executable, REPOX_SCRIPT_REL, "--repo-root", repo_root]
    return _run(cmd, repo_root, env)


def _run_verify(repo_root, include_dist):
    env, tools_dir = _canonical_env(repo_root)
    verification = {"commands": [], "tools_dir": tools_dir.replace("\\", "/")}
    actions = []

    repox = _run_repox(repo_root, env)
    verification["commands"].append(repox)
    last_score = _failure_score(repox.get("output", ""))
    attempted = set()

    while repox["returncode"] != 0 and "INV-TOOLS-DIR-MISSING" in (repox.get("output") or ""):
        remediation = _attempt_tool_remediation(repo_root, env, attempted)
        if remediation is None:
            break
        actions.append(remediation)
        verification["commands"].append(remediation)
        repox = _run_repox(repo_root, env)
        verification["commands"].append(repox)
        new_score = _failure_score(repox.get("output", ""))
        if repox["returncode"] == 0:
            break
        # Stop only when no measurable improvement remains.
        if new_score >= last_score:
            break
        last_score = new_score

    if repox["returncode"] != 0:
        failure = dict(repox)
        _write_remediation_bundle(
            repo_root,
            "verify",
            "tool_discovery",
            failure,
            actions,
            verification,
        )
        sys.stdout.write(repox.get("output", ""))
        return 1

    strict_build = _run(
        [
            "cmake",
            "--build",
            VERIFY_BUILD_DIR_REL,
            "--config",
            "Debug",
            "--target",
            "domino_engine",
            "dominium_game",
            "dominium_client",
        ],
        repo_root,
        env,
    )
    verification["commands"].append(strict_build)
    if strict_build["returncode"] != 0:
        _write_remediation_bundle(
            repo_root,
            "verify",
            "strict_build",
            strict_build,
            actions,
            verification,
        )
        sys.stdout.write(strict_build.get("output", ""))
        return 1

    testx = _run(
        [
            "cmake",
            "--build",
            VERIFY_BUILD_DIR_REL,
            "--config",
            "Debug",
            "--target",
            "testx_all",
        ],
        repo_root,
        env,
    )
    verification["commands"].append(testx)
    if testx["returncode"] != 0:
        _write_remediation_bundle(
            repo_root,
            "verify",
            "testx",
            testx,
            actions,
            verification,
        )
        sys.stdout.write(testx.get("output", ""))
        return 1

    if include_dist:
        dist = _run(
            [
                "cmake",
                "--build",
                VERIFY_BUILD_DIR_REL,
                "--config",
                "Debug",
                "--target",
                "dist_all",
            ],
            repo_root,
            env,
        )
        verification["commands"].append(dist)
        if dist["returncode"] != 0:
            _write_remediation_bundle(
                repo_root,
                "dist",
                "dist_lane",
                dist,
                actions,
                verification,
            )
            sys.stdout.write(dist.get("output", ""))
            return 1

    _write_remediation_bundle(
        repo_root,
        "dist" if include_dist else "verify",
        "ok",
        {"command": [], "output": "pass", "returncode": 0},
        actions,
        verification,
    )
    return 0


def _run_doctor(repo_root):
    env, tools_dir = _canonical_env(repo_root)
    payload = {
        "repo_root": repo_root.replace("\\", "/"),
        "tools_dir": tools_dir.replace("\\", "/"),
        "path_contains_tools_dir": tools_dir and tools_dir in env.get("PATH", ""),
        "tools": [],
    }

    ok = True
    for tool in CANONICAL_TOOL_IDS:
        resolved = resolve_tool(tool, env)
        if not resolved:
            ok = False
        payload["tools"].append(
            {
                "tool_id": tool,
                "resolved_path": resolved.replace("\\", "/") if resolved else "",
                "discoverable": bool(resolved),
            }
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 2


def main():
    parser = argparse.ArgumentParser(description="Canonical gate runner with autonomous tool remediation.")
    parser.add_argument("command", choices=("verify", "dist", "doctor"))
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    if args.command == "doctor":
        return _run_doctor(repo_root)
    if args.command == "dist":
        return _run_verify(repo_root, include_dist=True)
    return _run_verify(repo_root, include_dist=False)


if __name__ == "__main__":
    raise SystemExit(main())
