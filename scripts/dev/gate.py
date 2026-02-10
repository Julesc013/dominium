#!/usr/bin/env python3
"""Canonical autonomous gate runner with deterministic remediation."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

from env_tools_lib import (
    CANONICAL_TOOL_IDS,
    canonical_build_dirs,
    canonical_tools_dir,
    default_host_path,
    detect_repo_root,
    prepend_tools_to_path,
    resolve_tool,
)


VERIFY_BUILD_DIR_REL = os.path.join("out", "build", "vs2026", "verify")
REMEDIATION_ROOT_REL = os.path.join("docs", "audit", "remediation")
REPOX_SCRIPT_REL = os.path.join("scripts", "ci", "check_repox_rules.py")
PLAYBOOK_REGISTRY_REL = os.path.join("data", "registries", "remediation_playbooks.json")

MECHANICAL_BLOCKER_TYPES = (
    "TOOL_DISCOVERY",
    "DERIVED_ARTIFACT_STALE",
    "SCHEMA_MISMATCH",
    "BUILD_OUTPUT_MISSING",
    "PATH_CWD_DEPENDENCY",
    "ENVIRONMENT_CONTRACT",
)


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
        "command": list(cmd),
        "returncode": int(proc.returncode),
        "output": proc.stdout,
    }


def _load_playbooks(repo_root):
    path = os.path.join(repo_root, PLAYBOOK_REGISTRY_REL)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    entries = payload.get("playbooks", [])
    if not isinstance(entries, list):
        return {}
    out = {}
    for entry in entries:
        blocker_type = str(entry.get("blocker_type", "")).strip()
        if not blocker_type:
            continue
        strategies = entry.get("strategy_classes", [])
        if not isinstance(strategies, list):
            continue
        out[blocker_type] = [str(item).strip() for item in strategies if str(item).strip()]
    return out


def _default_strategy_classes(blocker_type):
    defaults = {
        "TOOL_DISCOVERY": ["environment", "tooling_integration", "build_wiring"],
        "DERIVED_ARTIFACT_STALE": ["artifact_regeneration", "tooling_integration"],
        "UI_BIND_DRIFT": ["artifact_regeneration", "tooling_integration"],
        "SCHEMA_MISMATCH": ["registry_schema", "artifact_regeneration"],
        "BUILD_OUTPUT_MISSING": ["build_wiring", "tooling_integration"],
        "PATH_CWD_DEPENDENCY": ["environment", "adapter_fix"],
        "ENVIRONMENT_CONTRACT": ["environment", "adapter_fix", "build_wiring"],
        "DOC_CANON_DRIFT": ["governance_rule", "regression_test"],
    }
    return list(defaults.get(blocker_type, ["environment", "build_wiring"]))


def _diagnose_blocker(stage_name, output):
    text = output or ""
    upper = text.upper()
    if "INV-TOOLS-DIR-MISSING" in text or "TOOL_UI_BIND" in text and "NOT RECOGNIZED" in upper:
        return "TOOL_DISCOVERY"
    if "UI_BIND_ERROR" in text:
        return "UI_BIND_DRIFT"
    if "stale" in text and "ui_bind" in text:
        return "DERIVED_ARTIFACT_STALE"
    if "schema" in text.lower() and ("mismatch" in text.lower() or "invalid" in text.lower()):
        return "SCHEMA_MISMATCH"
    if "cannot find the file specified" in text.lower() or "LNK1104" in upper:
        return "BUILD_OUTPUT_MISSING"
    if "cwd" in text.lower() and "path" in text.lower():
        return "PATH_CWD_DEPENDENCY"
    if stage_name == "repox":
        return "ENVIRONMENT_CONTRACT"
    return "OTHER"


def _failure_score(result):
    output = result.get("output", "") or ""
    score = 1000 + int(result.get("returncode", 0))
    markers = (
        "INV-TOOLS-DIR-MISSING",
        "INV-TOOL-UNRESOLVABLE",
        "INV-TOOLS-DIR-EXISTS",
        "UI_BIND_ERROR",
        "schema",
        "error",
    )
    for marker in markers:
        score += output.count(marker)
    return score


def _tool_build_attempts():
    return (
        ("ui_bind_phase",),
        ("dominium-tools",),
        ("tool_ui_bind", "tool_ui_validate", "tool_ui_doc_annotate"),
    )


def _run_build_targets(repo_root, env, targets):
    return _run(
        ["cmake", "--build", VERIFY_BUILD_DIR_REL, "--config", "Debug", "--target"] + list(targets),
        repo_root,
        env,
    )


def _attempt_strategy(repo_root, env, stage_name, strategy_class, attempted):
    key = (stage_name, strategy_class)
    if key in attempted:
        return None
    attempted.add(key)

    if strategy_class == "environment":
        env2, tools_dir = _canonical_env(repo_root, env)
        env.clear()
        env.update(env2)
        return {
            "strategy": strategy_class,
            "status": "applied",
            "note": "canonical environment refreshed",
            "tools_dir": tools_dir.replace("\\", "/"),
        }

    if strategy_class == "tooling_integration":
        for targets in _tool_build_attempts():
            target_key = (stage_name, strategy_class, targets)
            if target_key in attempted:
                continue
            attempted.add(target_key)
            result = _run_build_targets(repo_root, env, targets)
            result["strategy"] = strategy_class
            result["targets"] = list(targets)
            return result
        return None

    if strategy_class == "artifact_regeneration":
        tool = resolve_tool("tool_ui_bind", env)
        if not tool:
            return None
        result = _run([tool, "--repo-root", repo_root, "--write"], repo_root, env)
        result["strategy"] = strategy_class
        result["targets"] = ["ui_bind_write"]
        return result

    if strategy_class == "build_wiring":
        if stage_name == "strict_build":
            targets = ("domino_engine", "dominium_game", "dominium_client")
        elif stage_name == "testx":
            targets = ("testx_all",)
        else:
            targets = ("ui_bind_phase",)
        result = _run_build_targets(repo_root, env, targets)
        result["strategy"] = strategy_class
        result["targets"] = list(targets)
        return result

    if strategy_class == "registry_schema":
        result = _run([sys.executable, REPOX_SCRIPT_REL, "--repo-root", repo_root], repo_root, env)
        result["strategy"] = strategy_class
        result["targets"] = ["repox_refresh"]
        return result

    if strategy_class == "adapter_fix":
        env2, tools_dir = _canonical_env(repo_root, env)
        env.clear()
        env.update(env2)
        return {
            "strategy": strategy_class,
            "status": "applied",
            "note": "adapter contract refreshed",
            "tools_dir": tools_dir.replace("\\", "/"),
        }

    return None


def _artifact_dir(repo_root, gate_name, blocker_type):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rel = os.path.join(REMEDIATION_ROOT_REL, "{}_{}_{}".format(stamp, gate_name, blocker_type))
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
                "docs/governance/UNBOUNDED_AGENTIC_DEVELOPMENT.md",
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
        handle.write("gate run with deterministic remediation\n")
        for item in verification.get("commands", []):
            command = " ".join(item.get("command", []))
            code = item.get("returncode")
            handle.write("{} => {}\n".format(command, code))
    with open(os.path.join(out_dir, "failure.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# Gate Remediation Record\n\n")
        handle.write("- gate: `{}`\n".format(gate_name))
        handle.write("- blocker_type: `{}`\n".format(blocker_type))
        handle.write("- artifact_dir: `{}`\n\n".format(out_rel))
        handle.write("## Failure Output\n\n```\n{}\n```\n".format((failure.get("output", "") or "").strip()))


def _remediate_until_progress(repo_root, env, stage_name, command, playbooks):
    actions = []
    attempted = set()
    result = _run(command, repo_root, env)
    score = _failure_score(result)
    blocker_type = "ok"
    if result["returncode"] == 0:
        return result, actions, blocker_type

    while result["returncode"] != 0:
        blocker_type = _diagnose_blocker(stage_name, result.get("output", ""))
        strategy_classes = playbooks.get(blocker_type) or _default_strategy_classes(blocker_type)
        improved = False
        for strategy_class in strategy_classes:
            action = _attempt_strategy(repo_root, env, stage_name, strategy_class, attempted)
            if action is None:
                continue
            actions.append(action)
            rerun = _run(command, repo_root, env)
            new_score = _failure_score(rerun)
            actions.append(
                {
                    "strategy": "verify_after_strategy",
                    "applied_strategy": strategy_class,
                    "stage": stage_name,
                    "returncode": rerun["returncode"],
                    "score_before": score,
                    "score_after": new_score,
                }
            )
            result = rerun
            if result["returncode"] == 0:
                improved = True
                score = 0
                break
            if new_score < score:
                improved = True
                score = new_score
                break
        if result["returncode"] == 0:
            blocker_type = "ok"
            break
        if not improved:
            break
    return result, actions, blocker_type


def _stage_command(stage_name):
    if stage_name == "repox":
        return [sys.executable, REPOX_SCRIPT_REL, "--repo-root", "{repo_root}"]
    if stage_name == "strict_build":
        return [
            "cmake",
            "--build",
            VERIFY_BUILD_DIR_REL,
            "--config",
            "Debug",
            "--target",
            "domino_engine",
            "dominium_game",
            "dominium_client",
        ]
    if stage_name == "testx":
        return ["cmake", "--build", VERIFY_BUILD_DIR_REL, "--config", "Debug", "--target", "testx_all"]
    if stage_name == "dist":
        return ["cmake", "--build", VERIFY_BUILD_DIR_REL, "--config", "Debug", "--target", "dist_all"]
    raise RuntimeError("unknown gate stage {}".format(stage_name))


def _run_gate(repo_root, gate_kind):
    env, tools_dir = _canonical_env(repo_root)
    playbooks = _load_playbooks(repo_root)
    verification = {
        "gate_kind": gate_kind,
        "repo_root": repo_root.replace("\\", "/"),
        "tools_dir": tools_dir.replace("\\", "/"),
        "commands": [],
    }
    actions = []

    if gate_kind == "doctor":
        payload = {
            "repo_root": repo_root.replace("\\", "/"),
            "tools_dir": tools_dir.replace("\\", "/"),
            "build_dirs": {k: v.replace("\\", "/") for k, v in canonical_build_dirs(repo_root).items()},
            "tools": [],
        }
        ok = True
        for tool in CANONICAL_TOOL_IDS:
            resolved = resolve_tool(tool, env)
            payload["tools"].append(
                {
                    "tool_id": tool,
                    "resolved_path": resolved.replace("\\", "/") if resolved else "",
                    "discoverable": bool(resolved),
                }
            )
            if not resolved:
                ok = False
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if ok else 2

    if gate_kind == "remediate":
        stage_order = ["repox"]
    elif gate_kind == "dev":
        stage_order = ["repox", "strict_build"]
    elif gate_kind == "verify":
        stage_order = ["repox", "strict_build", "testx"]
    elif gate_kind == "dist":
        stage_order = ["repox", "strict_build", "testx", "dist"]
    else:
        raise RuntimeError("unsupported gate command {}".format(gate_kind))

    for stage_name in stage_order:
        cmd_template = _stage_command(stage_name)
        command = [part.format(repo_root=repo_root) for part in cmd_template]
        result, stage_actions, blocker_type = _remediate_until_progress(
            repo_root, env, stage_name, command, playbooks
        )
        actions.extend(stage_actions)
        verification["commands"].append(result)
        if result["returncode"] != 0:
            _write_remediation_bundle(
                repo_root,
                gate_kind,
                blocker_type,
                result,
                actions,
                verification,
            )
            sys.stdout.write(result.get("output", ""))
            return 1

    _write_remediation_bundle(
        repo_root,
        gate_kind,
        "ok",
        {"command": [], "output": "pass", "returncode": 0},
        actions,
        verification,
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canonical gate runner with autonomous remediation.")
    parser.add_argument("command", choices=("dev", "verify", "dist", "doctor", "remediate"))
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()
    return _run_gate(_repo_root(args.repo_root), args.command)


if __name__ == "__main__":
    raise SystemExit(main())
