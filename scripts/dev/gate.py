#!/usr/bin/env python3
"""Canonical autonomous gate runner with deterministic remediation."""

import argparse
import glob
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
GATE_POLICY_REGISTRY_REL = os.path.join("data", "registries", "gate_policy.json")
UI_BIND_CACHE_REL = os.path.join(VERIFY_BUILD_DIR_REL, "gate_ui_bind_cache.json")

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
    try:
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
    except OSError as exc:
        return {
            "command": list(cmd),
            "returncode": 127,
            "output": "refuse.command_unresolvable: {}".format(exc),
        }
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


def _load_gate_policy(repo_root):
    path = os.path.join(repo_root, GATE_POLICY_REGISTRY_REL)
    if not os.path.isfile(path):
        return {"gate_classes": {}, "gates": []}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {"gate_classes": {}, "gates": []}

    record = payload.get("record", {})
    classes = {}
    for item in record.get("gate_classes", []):
        class_id = str(item.get("class_id", "")).strip()
        if not class_id:
            continue
        classes[class_id] = item

    gates = []
    for gate in record.get("gates", []):
        gate_id = str(gate.get("gate_id", "")).strip()
        if not gate_id:
            continue
        gates.append(gate)
    return {"gate_classes": classes, "gates": gates}


def _policy_gates_for_classes(policy, class_ids):
    selected = []
    wanted = set(class_ids or [])
    for gate in policy.get("gates", []):
        gate_class = str(gate.get("gate_class", "")).strip()
        if gate_class in wanted:
            selected.append(gate)
    return selected


def _format_gate_command(command_tokens, repo_root):
    out = []
    for idx, token in enumerate(command_tokens):
        resolved = str(token).format(repo_root=repo_root)
        if idx == 0 and resolved.lower() in ("python", "python3"):
            resolved = sys.executable
        out.append(resolved)
    return out


def _targets_from_command(tokens):
    targets = []
    if "--target" not in tokens:
        return targets
    idx = tokens.index("--target") + 1
    while idx < len(tokens):
        token = tokens[idx]
        if str(token).startswith("-"):
            break
        targets.append(str(token).strip())
        idx += 1
    return [item for item in targets if item]


def _collect_requested_targets(repo_root, gates):
    targets = set()
    for gate in gates:
        command = gate.get("command", [])
        if not isinstance(command, list):
            continue
        resolved = _format_gate_command(command, repo_root)
        for target in _targets_from_command(resolved):
            targets.add(target)
    return sorted(targets)


def _resolve_command_executable(command, env):
    if not command:
        return command
    executable = str(command[0]).strip()
    if not executable:
        return command
    if "/" in executable or "\\" in executable or ":" in executable:
        return command

    resolved = resolve_tool(executable, env)
    if resolved:
        command[0] = resolved
        return command

    if os.name == "nt":
        dom_tools_path = env.get("DOM_TOOLS_PATH", "")
        if dom_tools_path:
            probe = os.path.join(dom_tools_path, executable + ".exe")
            if os.path.isfile(probe):
                command[0] = probe
    return command


def _run_capture(repo_root, args):
    try:
        proc = subprocess.run(
            args,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _normalize_rel(path):
    return path.replace("\\", "/").strip("/")


def _changed_files_from_git(repo_root):
    baseline_ref = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    out = _run_capture(
        repo_root,
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "{}...HEAD".format(baseline_ref)],
    )
    if out is None:
        out = _run_capture(repo_root, ["git", "status", "--porcelain"])
        if out is None:
            return None
        files = []
        for line in out.splitlines():
            line = line.rstrip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            files.append(_normalize_rel(parts[1]))
        return sorted(set(files))

    files = [_normalize_rel(line) for line in out.splitlines() if line.strip()]
    return sorted(set(files))


def _cache_payload(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    records = payload.get("records", {})
    if not isinstance(records, dict):
        return {}
    return records


def _write_cache_payload(path, records):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"records": records}, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _changed_files_from_timestamp_cache(repo_root, globs):
    cache_path = os.path.join(repo_root, UI_BIND_CACHE_REL)
    previous = _cache_payload(cache_path)

    current = {}
    changed = set()
    for pattern in globs:
        pattern_abs = os.path.join(repo_root, pattern.replace("/", os.sep))
        for path in glob.glob(pattern_abs, recursive=True):
            if os.path.isdir(path):
                continue
            rel = _normalize_rel(os.path.relpath(path, repo_root))
            try:
                stamp = os.path.getmtime(path)
            except OSError:
                continue
            current[rel] = stamp
            if rel not in previous or previous.get(rel) != stamp:
                changed.add(rel)

    for rel in previous:
        if rel not in current:
            changed.add(rel)

    _write_cache_payload(cache_path, current)
    return sorted(changed)


def _match_glob(rel_path, pattern):
    pattern_norm = _normalize_rel(pattern)
    path_norm = _normalize_rel(rel_path)
    if pattern_norm.endswith("/*"):
        prefix = pattern_norm[:-1]
        return path_norm.startswith(prefix)
    return glob.fnmatch.fnmatch(path_norm, pattern_norm)


def _gate_applies(gate, repo_root, requested_targets):
    conditions = gate.get("applies_when", [])
    if not isinstance(conditions, list) or not conditions:
        return True

    changed = _changed_files_from_git(repo_root)
    if changed is None:
        patterns = []
        for cond in conditions:
            if isinstance(cond, dict) and cond.get("kind") == "changed_glob":
                values = cond.get("values", [])
                if isinstance(values, list):
                    patterns.extend(str(item) for item in values if str(item).strip())
        changed = _changed_files_from_timestamp_cache(repo_root, patterns)
    changed_set = set(changed or [])
    target_set = set(requested_targets or [])

    for cond in conditions:
        if not isinstance(cond, dict):
            continue
        kind = str(cond.get("kind", "")).strip()
        values = cond.get("values", [])
        if not isinstance(values, list):
            values = []
        negate = bool(cond.get("negate", False))

        matched = False
        if kind == "always":
            matched = any(str(item).strip().lower() == "true" for item in values) or not values
        elif kind == "changed_glob":
            for pattern in values:
                pattern = str(pattern).strip()
                if not pattern:
                    continue
                if any(_match_glob(rel, pattern) for rel in changed_set):
                    matched = True
                    break
        elif kind == "requested_target":
            for target in values:
                if str(target).strip() in target_set:
                    matched = True
                    break

        if negate:
            matched = not matched
        if matched:
            return True
    return False


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
    if "INV-IDENTITY-FINGERPRINT" in text:
        return "DERIVED_ARTIFACT_STALE"
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
        stage_lower = stage_name.lower()
        if "repox" in stage_lower:
            result = _run(
                [sys.executable, os.path.join("tools", "ci", "tool_identity_fingerprint.py"), "--repo-root", repo_root],
                repo_root,
                env,
            )
            result["strategy"] = strategy_class
            result["targets"] = ["identity_fingerprint"]
            return result

        tool = resolve_tool("tool_ui_bind", env)
        if not tool:
            return None
        result = _run([tool, "--repo-root", repo_root, "--write"], repo_root, env)
        result["strategy"] = strategy_class
        result["targets"] = ["ui_bind_write"]
        return result

    if strategy_class == "build_wiring":
        stage_lower = stage_name.lower()
        if "dist" in stage_lower:
            targets = ("dist_all",)
        elif "testx" in stage_lower:
            targets = ("testx_all",)
        elif "build" in stage_lower or "toolchain" in stage_lower:
            targets = ("domino_engine", "dominium_game", "dominium_client")
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


def _remediate_until_progress(repo_root, env, stage_name, command, playbooks, auto_remediate=True):
    actions = []
    attempted = set()
    result = _run(command, repo_root, env)
    score = _failure_score(result)
    blocker_type = "ok"
    if result["returncode"] == 0:
        return result, actions, blocker_type
    if not auto_remediate:
        blocker_type = _diagnose_blocker(stage_name, result.get("output", ""))
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


def _execute_gate_set(
    repo_root,
    env,
    gate_kind,
    policy,
    class_ids,
    playbooks,
    requested_targets=None,
    only_gate_ids=None,
):
    verification = {"commands": [], "skipped": [], "warnings": []}
    actions = []
    gates = _policy_gates_for_classes(policy, class_ids)
    requested_targets = set(str(item).strip() for item in (requested_targets or []) if str(item).strip())
    only_gate_ids = set(str(item).strip() for item in (only_gate_ids or []) if str(item).strip())

    for gate in gates:
        gate_id = str(gate.get("gate_id", "")).strip()
        if not gate_id:
            continue
        if only_gate_ids and gate_id not in only_gate_ids:
            verification["skipped"].append(gate_id)
            continue
        if not _gate_applies(gate, repo_root, sorted(requested_targets)):
            verification["skipped"].append(gate_id)
            continue

        command_tokens = gate.get("command", [])
        if not isinstance(command_tokens, list) or not command_tokens:
            verification["warnings"].append(
                "gate {} skipped: invalid command definition".format(gate_id)
            )
            continue
        command = _format_gate_command(command_tokens, repo_root)
        command = _resolve_command_executable(command, env)
        auto_remediate = bool(gate.get("auto_remediate", False))
        severity = str(gate.get("severity", "fail")).strip().lower()

        result, gate_actions, blocker_type = _remediate_until_progress(
            repo_root,
            env,
            gate_id,
            command,
            playbooks,
            auto_remediate=auto_remediate,
        )
        actions.extend(gate_actions)
        verification["commands"].append(result)
        if result["returncode"] == 0:
            continue
        if severity == "warn":
            verification["warnings"].append(
                "gate {} warning ({}): {}".format(gate_id, blocker_type, result.get("output", "").strip())
            )
            continue
        _write_remediation_bundle(
            repo_root,
            gate_kind,
            blocker_type,
            result,
            actions,
            verification,
        )
        sys.stdout.write(result.get("output", ""))
        return 1, verification, actions

    return 0, verification, actions


def _run_gate(repo_root, gate_kind, only_gate_ids=None):
    env, tools_dir = _canonical_env(repo_root)
    playbooks = _load_playbooks(repo_root)
    policy = _load_gate_policy(repo_root)
    verification = {
        "gate_kind": gate_kind,
        "repo_root": repo_root.replace("\\", "/"),
        "tools_dir": tools_dir.replace("\\", "/"),
        "commands": [],
        "skipped": [],
        "warnings": [],
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

    precheck_targets = ("domino_engine", "dominium_game")
    exit_targets = ("domino_engine", "dominium_game", "dominium_client", "testx_all")
    if gate_kind == "precheck":
        phase_specs = [(("PRECHECK_MIN",), precheck_targets)]
    elif gate_kind == "exitcheck":
        phase_specs = [(("TASK_DEPENDENCY", "EXIT_STRICT"), exit_targets)]
    elif gate_kind == "dev":
        phase_specs = [(("PRECHECK_MIN",), precheck_targets)]
    elif gate_kind == "verify":
        phase_specs = [
            (("PRECHECK_MIN",), precheck_targets),
            (("TASK_DEPENDENCY", "EXIT_STRICT"), exit_targets),
        ]
    elif gate_kind == "dist":
        phase_specs = [
            (("PRECHECK_MIN",), precheck_targets),
            (("TASK_DEPENDENCY", "EXIT_STRICT"), tuple(list(exit_targets) + ["dist_all"])),
        ]
    elif gate_kind == "remediate":
        phase_specs = [
            (("PRECHECK_MIN",), precheck_targets),
            (("TASK_DEPENDENCY", "EXIT_STRICT"), exit_targets),
        ]
    else:
        raise RuntimeError("unsupported gate command {}".format(gate_kind))

    for class_ids, requested_targets in phase_specs:
        code, phase_verification, phase_actions = _execute_gate_set(
            repo_root,
            env,
            gate_kind,
            policy,
            class_ids,
            playbooks,
            requested_targets=requested_targets,
            only_gate_ids=only_gate_ids,
        )
        verification["commands"].extend(phase_verification.get("commands", []))
        verification["skipped"].extend(phase_verification.get("skipped", []))
        verification["warnings"].extend(phase_verification.get("warnings", []))
        actions.extend(phase_actions)
        if code != 0:
            return code

    if actions:
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
    parser.add_argument(
        "command",
        choices=("dev", "verify", "dist", "doctor", "remediate", "precheck", "exitcheck"),
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--only-gate", action="append", default=[])
    args = parser.parse_args()
    return _run_gate(_repo_root(args.repo_root), args.command, only_gate_ids=args.only_gate)


if __name__ == "__main__":
    raise SystemExit(main())
