#!/usr/bin/env python3
"""Canonical autonomous gate runner with deterministic remediation."""

import argparse
import glob
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime

_XSTACK_CORE_READY = False
_XSTACK_IMPORT_ERROR = ""
try:
    _REPO_HINT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    if _REPO_HINT not in sys.path:
        sys.path.insert(0, _REPO_HINT)
    from tools.xstack.core.execution_ledger import (
        append_entry as append_ledger_entry,
    )
    from tools.xstack.core.execution_ledger import (
        build_entry as build_ledger_entry,
    )
    from tools.xstack.core.execution_ledger import (
        canonical_artifact_hashes as canonical_ledger_artifact_hashes,
    )
    from tools.xstack.core.execution_ledger import (
        export_snapshot_markdown as export_ledger_snapshot_markdown,
    )
    from tools.xstack.core.plan import build_execution_plan
    from tools.xstack.core.profiler import export_json as export_profile_json
    from tools.xstack.core.profiler import reset as reset_profile
    from tools.xstack.core.scheduler import execute_plan

    _XSTACK_CORE_READY = True
except Exception as exc:  # pragma: no cover
    _XSTACK_IMPORT_ERROR = str(exc)

from env_tools_lib import (
    CANONICAL_TOOL_IDS,
    WORKSPACE_ID_ENV_KEY,
    canonical_build_dirs,
    canonicalize_env_for_workspace,
    canonical_workspace_id,
    detect_repo_root,
    resolve_tool,
    select_verify_build_dir,
)
from gate_policy_eval import (
    FAST_MODE,
    FULL_MODE,
    STRICT_MODE,
    compute_workspace_state_hash,
    evaluate_gate_mode,
    load_gate_policy_version,
)


VERIFY_BUILD_DIR_REL = os.path.join("out", "build", "vs2026", "verify")
REMEDIATION_ROOT_REL = os.path.join("docs", "audit", "remediation")
REPOX_SCRIPT_REL = os.path.join("scripts", "ci", "check_repox_rules.py")
PLAYBOOK_REGISTRY_REL = os.path.join("data", "registries", "remediation_playbooks.json")
GATE_POLICY_REGISTRY_REL = os.path.join("data", "registries", "gate_policy.json")
UI_BIND_CACHE_REL = os.path.join(VERIFY_BUILD_DIR_REL, "gate_ui_bind_cache.json")
DERIVED_ARTIFACT_REGISTRY_REL = os.path.join("data", "registries", "derived_artifacts.json")
TRACKED_WRITE_MANIFEST_SUFFIX = os.path.join("gate", "TOUCHED_FILES_MANIFEST.json")
SNAPSHOT_REPORT_REL = os.path.join("docs", "audit", "system", "SNAPSHOT_REPORT.md")
LEDGER_SNAPSHOT_REL = os.path.join("docs", "audit", "system", "LEDGER_SNAPSHOT.md")

MECHANICAL_BLOCKER_TYPES = (
    "TOOL_DISCOVERY",
    "DERIVED_ARTIFACT_STALE",
    "DIST_OUTPUT_MISSING",
    "PKG_INDEX_MISSING",
    "SCHEMA_MISMATCH",
    "BUILD_OUTPUT_MISSING",
    "PATH_CWD_DEPENDENCY",
    "ENVIRONMENT_CONTRACT",
    "WORKSPACE_COLLISION",
    "VERSIONING_POLICY_MISMATCH",
)


# Gate throughput hotfix:
# - verify defaults to FAST lane (precheck + task dependency)
# - add explicit FULL lane for exhaustive verification
# - short-circuit repeated invocations on identical repo state
GATE_STATE_CACHE_REL = os.path.join("gate", "gate_last_ok.json")
DEFAULT_FAST_VERIFY = True

def _repo_root(arg_value):
    if arg_value:
        return os.path.normpath(os.path.abspath(arg_value))
    return detect_repo_root(os.getcwd(), __file__)


def _norm(path):
    return os.path.normpath(path)


def _norm_case(path):
    return os.path.normcase(_norm(path))


def _canonical_env(repo_root, base_env=None, ws_id=""):
    env_in = dict(base_env or os.environ)
    resolved_ws = (ws_id or "").strip() or env_in.get(WORKSPACE_ID_ENV_KEY, "")
    resolved_ws = resolved_ws or canonical_workspace_id(repo_root, env=env_in)
    env, ws_dirs = canonicalize_env_for_workspace(
        env_in,
        repo_root,
        ws_id=resolved_ws,
    )
    tools_dir = env.get("DOM_CANONICAL_TOOLS_DIR", "") or env.get("DOM_TOOLS_PATH", "")
    return env, tools_dir, ws_dirs


def _xstack_cache_root(repo_root, workspace_id=""):
    ws_id = str(workspace_id or "").strip() or canonical_workspace_id(repo_root, env=os.environ)
    root = os.path.join(repo_root, ".xstack_cache", ws_id)
    if not os.path.isdir(root):
        os.makedirs(root, exist_ok=True)
    return root


def _rewrite_command_paths(command, verify_build_dir):
    rewritten = []
    legacy_verify_norm = _norm_case(VERIFY_BUILD_DIR_REL)
    for token in command:
        token_text = str(token)
        token_norm = _norm_case(token_text)
        if token_norm == legacy_verify_norm:
            rewritten.append(verify_build_dir)
            continue
        rewritten.append(token_text)
    return rewritten


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


def _format_gate_command(command_tokens, repo_root, verify_build_dir="", ws_id="", dist_root=""):
    out = []
    format_ctx = {
        "repo_root": repo_root,
        "verify_build_dir": verify_build_dir,
        "ws_id": ws_id,
        "dist_root": dist_root,
    }
    for idx, token in enumerate(command_tokens):
        raw = str(token)
        try:
            resolved = raw.format(**format_ctx)
        except (IndexError, KeyError, ValueError):
            resolved = raw
        if idx == 0 and resolved.lower() in ("python", "python3"):
            resolved = sys.executable
        out.append(resolved)
    return _rewrite_command_paths(out, verify_build_dir or VERIFY_BUILD_DIR_REL)


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


def _git_tracked_status(repo_root):
    out = _run_capture(
        repo_root,
        ["git", "status", "--porcelain", "--untracked-files=no"],
    )
    rows = {}
    if out is None:
        return rows
    for raw in out.splitlines():
        line = raw.rstrip()
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        path = path.replace("\\", "/").strip("/")
        if not path:
            continue
        rows[path] = status
    return rows


def _snapshot_only_paths(repo_root):
    path = os.path.join(repo_root, DERIVED_ARTIFACT_REGISTRY_REL)
    if not os.path.isfile(path):
        return set()
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    rows = ((payload.get("record") or {}).get("artifacts") or [])
    out = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("commit_policy", "")).strip() != "SNAPSHOT_ONLY":
            continue
        rel = str(row.get("path", "")).replace("\\", "/").strip("/")
        if rel:
            out.add(rel)
    out.add(SNAPSHOT_REPORT_REL.replace("\\", "/"))
    return out


def _write_touched_manifest(repo_root, payload, workspace_id=""):
    out_path = os.path.join(_xstack_cache_root(repo_root, workspace_id=workspace_id), TRACKED_WRITE_MANIFEST_SUFFIX)
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return out_path


def _tracked_write_violations(repo_root, gate_kind, profile, before_status, after_status, snapshot_mode, workspace_id=""):
    before_status = before_status or {}
    after_status = after_status or {}
    touched = []
    for path in sorted(set(before_status.keys()) | set(after_status.keys())):
        before = before_status.get(path, "")
        after = after_status.get(path, "")
        if before == after:
            continue
        touched.append(path)

    allowed = sorted(_snapshot_only_paths(repo_root)) if snapshot_mode else []
    allowed_set = set(allowed)
    if snapshot_mode:
        violations = [path for path in touched if path not in allowed_set]
    else:
        violations = list(touched)

    manifest = {
        "artifact_class": "RUN_META",
        "status": "DERIVED",
        "gate_kind": gate_kind,
        "profile": profile,
        "snapshot_mode": bool(snapshot_mode),
        "touched_tracked_files": touched,
        "allowed_snapshot_only_files": allowed,
        "violations": violations,
    }
    manifest_path = _write_touched_manifest(repo_root, manifest, workspace_id=workspace_id)
    return violations, manifest_path


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

def _state_cache_path(repo_root, ws_dirs=None):
    ws_dirs = ws_dirs or {}
    ws_id = str(ws_dirs.get("workspace_id", "")).strip() or canonical_workspace_id(repo_root, env=os.environ)
    return os.path.join(_xstack_cache_root(repo_root, workspace_id=ws_id), GATE_STATE_CACHE_REL)


def _load_state_cache(repo_root, ws_dirs=None):
    path = _state_cache_path(repo_root, ws_dirs=ws_dirs)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    last_success = data.get("last_success", {})
    if not isinstance(last_success, dict):
        last_success = {}
    return {"last_success": last_success}


def _write_state_cache(repo_root, ws_dirs, data):
    path = _state_cache_path(repo_root, ws_dirs=ws_dirs)
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _try_short_circuit(repo_root, ws_dirs, gate_kind, gate_mode, state_hash):
    """Return 0 if we already passed this gate kind+mode on identical state."""
    cache = _load_state_cache(repo_root, ws_dirs=ws_dirs)
    key = "{}:{}".format(gate_kind, gate_mode)
    if cache.get("last_success", {}).get(key, "") == state_hash:
        return 0
    return None


def _mark_short_circuit_ok(repo_root, ws_dirs, gate_kind, gate_mode, state_hash):
    cache = _load_state_cache(repo_root, ws_dirs=ws_dirs)
    if "last_success" not in cache or not isinstance(cache["last_success"], dict):
        cache["last_success"] = {}
    key = "{}:{}".format(gate_kind, gate_mode)
    cache["last_success"][key] = state_hash
    _write_state_cache(repo_root, ws_dirs, cache)

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


def _ui_bind_cache_path(repo_root, env):
    verify_dir = ""
    if env:
        verify_dir = str(env.get("DOM_WS_VERIFY_BUILD_DIR", "")).strip()
    if verify_dir:
        if not os.path.isabs(verify_dir):
            verify_dir = os.path.join(repo_root, verify_dir)
        return os.path.join(os.path.normpath(verify_dir), "gate_ui_bind_cache.json")
    return os.path.join(repo_root, UI_BIND_CACHE_REL)


def _changed_files_from_timestamp_cache(repo_root, globs, env=None):
    cache_path = _ui_bind_cache_path(repo_root, env)
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


def _gate_applies(gate, repo_root, requested_targets, env=None):
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
        changed = _changed_files_from_timestamp_cache(repo_root, patterns, env=env)
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
        "DIST_OUTPUT_MISSING": ["build_wiring", "artifact_regeneration"],
        "PKG_INDEX_MISSING": ["build_wiring", "artifact_regeneration"],
        "UI_BIND_DRIFT": ["artifact_regeneration", "tooling_integration"],
        "SCHEMA_MISMATCH": ["registry_schema", "artifact_regeneration"],
        "BUILD_OUTPUT_MISSING": ["build_wiring", "tooling_integration"],
        "PATH_CWD_DEPENDENCY": ["environment", "adapter_fix"],
        "ENVIRONMENT_CONTRACT": ["environment", "adapter_fix", "build_wiring"],
        "WORKSPACE_COLLISION": ["environment", "build_wiring", "adapter_fix"],
        "VERSIONING_POLICY_MISMATCH": ["registry_schema", "governance_rule"],
        "DOC_CANON_DRIFT": ["governance_rule", "regression_test"],
    }
    return list(defaults.get(blocker_type, ["environment", "build_wiring"]))


def _diagnose_blocker(stage_name, output):
    text = output or ""
    upper = text.upper()
    if "INV-IDENTITY-FINGERPRINT" in text:
        return "DERIVED_ARTIFACT_STALE"
    if "INV-DERIVED-STALE" in text:
        return "DERIVED_ARTIFACT_STALE"
    if "INV-DIST-MISSING" in text:
        return "DIST_OUTPUT_MISSING"
    if "INV-PKG-INDEX-MISSING" in text:
        return "PKG_INDEX_MISSING"
    if "INV-TOOLS-DIR-MISSING" in text or "TOOL_UI_BIND" in text and "NOT RECOGNIZED" in upper:
        return "TOOL_DISCOVERY"
    if "UI_BIND_ERROR" in text:
        return "UI_BIND_DRIFT"
    if "stale" in text and "ui_bind" in text:
        return "DERIVED_ARTIFACT_STALE"
    if "schema" in text.lower() and ("mismatch" in text.lower() or "invalid" in text.lower()):
        return "SCHEMA_MISMATCH"
    if "workspace" in text.lower() and ("collision" in text.lower() or "conflict" in text.lower()):
        return "WORKSPACE_COLLISION"
    if "version" in text.lower() and ("policy" in text.lower() or "mismatch" in text.lower()):
        return "VERSIONING_POLICY_MISMATCH"
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


def _has_measurable_progress(before_result, after_result):
    before_score = _failure_score(before_result)
    after_score = _failure_score(after_result)
    if int(before_result.get("returncode", 0)) != 0 and int(after_result.get("returncode", 0)) == 0:
        return True
    return after_score < before_score


def _tool_build_attempts():
    return (
        ("ui_bind_phase",),
        ("dominium-tools",),
        ("tool_ui_bind", "tool_ui_validate", "tool_ui_doc_annotate"),
    )


def _run_build_targets(repo_root, env, targets, verify_build_dir):
    return _run(
        ["cmake", "--build", verify_build_dir, "--config", "Debug", "--target"] + list(targets),
        repo_root,
        env,
    )


def _attempt_strategy(repo_root, env, stage_name, strategy_class, attempted, verify_build_dir, blocker_type=""):
    key = (stage_name, strategy_class, blocker_type)
    if key in attempted:
        return None
    attempted.add(key)

    if strategy_class == "environment":
        env2, tools_dir, _ws_dirs = _canonical_env(repo_root, env)
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
            result = _run_build_targets(repo_root, env, targets, verify_build_dir)
            result["strategy"] = strategy_class
            result["targets"] = list(targets)
            return result
        return None

    if strategy_class == "artifact_regeneration":
        if blocker_type in ("DIST_OUTPUT_MISSING", "PKG_INDEX_MISSING"):
            result = _run_build_targets(repo_root, env, ("dist_all",), verify_build_dir)
            result["strategy"] = strategy_class
            result["targets"] = ["dist_all"]
            return result

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
        if blocker_type in ("DIST_OUTPUT_MISSING", "PKG_INDEX_MISSING"):
            targets = ("dist_all",)
        elif "dist" in stage_lower:
            targets = ("dist_all",)
        elif "testx.fast" in stage_lower:
            targets = ("testx_fast",)
        elif "testx.dist" in stage_lower:
            targets = ("testx_dist",)
        elif "testx" in stage_lower:
            targets = ("testx_verify",)
        elif "build" in stage_lower or "toolchain" in stage_lower:
            targets = ("domino_engine", "dominium_game", "dominium_client")
        else:
            targets = ("ui_bind_phase",)
        result = _run_build_targets(repo_root, env, targets, verify_build_dir)
        result["strategy"] = strategy_class
        result["targets"] = list(targets)
        return result

    if strategy_class == "registry_schema":
        result = _run([sys.executable, REPOX_SCRIPT_REL, "--repo-root", repo_root], repo_root, env)
        result["strategy"] = strategy_class
        result["targets"] = ["repox_refresh"]
        return result

    if strategy_class == "adapter_fix":
        env2, tools_dir, _ws_dirs = _canonical_env(repo_root, env)
        env.clear()
        env.update(env2)
        return {
            "strategy": strategy_class,
            "status": "applied",
            "note": "adapter contract refreshed",
            "tools_dir": tools_dir.replace("\\", "/"),
        }

    return None


def _artifact_dir(repo_root, gate_name, blocker_type, remediation_root=""):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    root = remediation_root or os.path.join(repo_root, REMEDIATION_ROOT_REL)
    if not os.path.isabs(root):
        root = os.path.join(repo_root, root)
    abs_path = os.path.join(root, "{}_{}_{}".format(stamp, gate_name, blocker_type))
    os.makedirs(abs_path, exist_ok=True)
    rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
    return abs_path, rel


def _write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_remediation_bundle(
    repo_root,
    gate_name,
    blocker_type,
    failure,
    actions,
    verification,
    remediation_root="",
):
    out_dir, out_rel = _artifact_dir(repo_root, gate_name, blocker_type, remediation_root=remediation_root)
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


def _load_queue_steps(queue_file):
    if not queue_file:
        return None, "refuse.queue_file_required"
    if not os.path.isfile(queue_file):
        return None, "refuse.queue_file_missing"

    try:
        with open(queue_file, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None, "refuse.queue_file_unreadable"

    steps = None
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = None

    if isinstance(parsed, list):
        steps = parsed
    elif isinstance(parsed, dict):
        raw_steps = parsed.get("steps")
        if isinstance(raw_steps, list):
            steps = raw_steps

    if steps is None:
        steps = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = shlex.split(line, posix=False)
            if not parts:
                continue
            steps.append({"command": parts[0], "args": parts[1:]})

    normalized = []
    for step in steps:
        if isinstance(step, str):
            normalized.append({"command": step.strip()})
            continue
        if isinstance(step, dict):
            normalized.append(step)
    if not normalized:
        return None, "refuse.queue_empty"
    return normalized, ""


def _run_queue(repo_root, queue_file, workspace_id=""):
    steps, refusal = _load_queue_steps(queue_file)
    if steps is None:
        print(json.dumps({"result": "refused", "refusal_code": refusal}, indent=2, sort_keys=True))
        return 2

    results = []
    overall_code = 0
    for idx, step in enumerate(steps, start=1):
        command = str(step.get("command", "")).strip()
        if not command:
            results.append({"index": idx, "result": "skipped", "reason": "missing_command"})
            continue
        if command == "run-queue":
            results.append({"index": idx, "command": command, "result": "failed", "reason": "nested_queue_forbidden"})
            overall_code = 1
            continue

        only_gate_ids = step.get("only_gate") or step.get("only_gates") or []
        if isinstance(only_gate_ids, str):
            only_gate_ids = [only_gate_ids]
        if not isinstance(only_gate_ids, list):
            only_gate_ids = []
        step_workspace_id = str(step.get("workspace_id", "")).strip() or workspace_id

        code = _run_gate(
            repo_root,
            command,
            only_gate_ids=only_gate_ids,
            workspace_id=step_workspace_id,
        )
        results.append(
            {
                "index": idx,
                "command": command,
                "only_gate": only_gate_ids,
                "workspace_id": step_workspace_id,
                "returncode": int(code),
            }
        )
        if code != 0:
            overall_code = 1

    env, _, ws_dirs = _canonical_env(repo_root, ws_id=workspace_id)
    remediation_root = ws_dirs.get("remediation_root", os.path.join(repo_root, REMEDIATION_ROOT_REL))
    out_dir, out_rel = _artifact_dir(repo_root, "run_queue", "summary", remediation_root=remediation_root)
    _write_json(
        os.path.join(out_dir, "verification.json"),
        {
            "status": "DERIVED",
            "last_reviewed": datetime.utcnow().strftime("%Y-%m-%d"),
            "queue_file": os.path.relpath(queue_file, repo_root).replace("\\", "/"),
            "workspace_id": ws_dirs.get("workspace_id", ""),
            "results": results,
            "overall_returncode": overall_code,
        },
    )
    print(
        json.dumps(
            {
                "result": "queue_complete",
                "workspace_id": ws_dirs.get("workspace_id", ""),
                "artifact_dir": out_rel,
                "overall_returncode": overall_code,
                "steps": results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return overall_code


def _remediate_until_progress(
    repo_root,
    env,
    stage_name,
    command,
    playbooks,
    verify_build_dir,
    auto_remediate=True,
):
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
            action = _attempt_strategy(
                repo_root,
                env,
                stage_name,
                strategy_class,
                attempted,
                verify_build_dir,
                blocker_type=blocker_type,
            )
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
            previous_result = result
            result = rerun
            if result["returncode"] == 0:
                improved = True
                score = 0
                break
            if _has_measurable_progress(previous_result, rerun):
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
    verify_build_dir,
    ws_id="",
    dist_root="",
    remediation_root="",
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
        if not _gate_applies(gate, repo_root, sorted(requested_targets), env=env):
            verification["skipped"].append(gate_id)
            continue

        command_tokens = gate.get("command", [])
        if not isinstance(command_tokens, list) or not command_tokens:
            verification["warnings"].append(
                "gate {} skipped: invalid command definition".format(gate_id)
            )
            continue
        command = _format_gate_command(
            command_tokens,
            repo_root,
            verify_build_dir=verify_build_dir,
            ws_id=ws_id,
            dist_root=dist_root,
        )
        command = _resolve_command_executable(command, env)
        auto_remediate = bool(gate.get("auto_remediate", False))
        severity = str(gate.get("severity", "fail")).strip().lower()

        result, gate_actions, blocker_type = _remediate_until_progress(
            repo_root,
            env,
            gate_id,
            command,
            playbooks,
            verify_build_dir,
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
            remediation_root=remediation_root,
        )
        sys.stdout.write(result.get("output", ""))
        return 1, verification, actions

    return 0, verification, actions


def _fast_task_targets_for_impact(impact):
    if impact == "DOCS_ONLY":
        return ()
    return ("testx_fast",)


def _phase_specs_for_gate(gate_kind, mode, impact):
    fast_task_targets = _fast_task_targets_for_impact(impact)
    strict_targets = ("toolchain_sanity", "build_strict", "testx_fast", "auditx_changed")
    full_targets = ("toolchain_sanity", "build_strict", "testx_verify", "auditx_changed")
    dist_targets = (
        "toolchain_sanity",
        "build_strict",
        "testx_verify",
        "testx_dist",
        "auditx_changed",
        "dist_all",
    )

    if gate_kind == "precheck":
        return [(("PRECHECK_MIN",), ())]

    if gate_kind == "taskcheck":
        if mode == FAST_MODE:
            return [(("TASK_DEPENDENCY",), fast_task_targets)]
        if mode == STRICT_MODE:
            return [(("TASK_DEPENDENCY",), strict_targets)]
        return [(("TASK_DEPENDENCY",), full_targets)]

    if gate_kind == "exitcheck":
        if mode == FAST_MODE:
            return [(("TASK_DEPENDENCY",), fast_task_targets)]
        if mode == STRICT_MODE:
            return [
                (("TASK_DEPENDENCY",), strict_targets),
                (("EXIT_STRICT",), strict_targets),
            ]
        return [
            (("TASK_DEPENDENCY",), full_targets),
            (("EXIT_STRICT",), full_targets),
        ]

    if gate_kind == "dev":
        return [
            (("PRECHECK_MIN",), ()),
            (("TASK_DEPENDENCY",), fast_task_targets),
        ]

    if gate_kind in ("verify", "strict", "full", "snapshot"):
        if mode == FAST_MODE:
            return [
                (("PRECHECK_MIN",), ()),
                (("TASK_DEPENDENCY",), fast_task_targets),
            ]
        if mode == STRICT_MODE:
            return [
                (("PRECHECK_MIN",), strict_targets),
                (("TASK_DEPENDENCY",), strict_targets),
                (("EXIT_STRICT",), strict_targets),
            ]
        return [
            (("PRECHECK_MIN",), full_targets),
            (("TASK_DEPENDENCY",), full_targets),
            (("EXIT_STRICT",), full_targets),
        ]

    if gate_kind == "dist":
        return [
            (("PRECHECK_MIN",), dist_targets),
            (("TASK_DEPENDENCY",), dist_targets),
            (("EXIT_STRICT",), dist_targets),
        ]

    if gate_kind == "remediate":
        return [
            (("PRECHECK_MIN",), strict_targets),
            (("TASK_DEPENDENCY",), strict_targets),
            (("EXIT_STRICT",), strict_targets),
        ]

    raise RuntimeError("unsupported gate command {}".format(gate_kind))


def _effective_mode_for_gate(repo_root, gate_kind, force_strict=False, force_full=False):
    if gate_kind == "dist":
        return {"mode": FULL_MODE, "impact": "DIST_LANE", "reason": "dist_lane", "changed_files": []}
    if gate_kind == "full":
        return {"mode": FULL_MODE, "impact": "EXPLICIT_FULL", "reason": "explicit_full", "changed_files": []}
    if gate_kind == "strict":
        return {"mode": STRICT_MODE, "impact": "EXPLICIT_STRICT", "reason": "explicit_strict", "changed_files": []}
    if gate_kind == "snapshot":
        return {"mode": STRICT_MODE, "impact": "EXPLICIT_SNAPSHOT", "reason": "explicit_snapshot", "changed_files": []}
    if gate_kind in ("verify", "exitcheck", "taskcheck", "dev"):
        return evaluate_gate_mode(
            repo_root,
            gate_kind,
            force_strict=force_strict,
            force_full=force_full,
        )
    return {"mode": FAST_MODE, "impact": "DEFAULT", "reason": "default", "changed_files": []}


def _profile_for_command(gate_kind, force_strict=False, force_full=False, force_full_all=False):
    if force_full_all:
        return "FULL_ALL"
    if force_full:
        return FULL_MODE
    if force_strict:
        return STRICT_MODE
    if gate_kind in ("full", "dist"):
        return FULL_MODE
    if gate_kind == "strict":
        return STRICT_MODE
    if gate_kind == "snapshot":
        return FULL_MODE if force_full else STRICT_MODE
    return FAST_MODE


def _write_full_plan_warning(repo_root, plan_payload, cache_root=""):
    estimate = plan_payload.get("estimate") or {}
    if not bool(estimate.get("warn_full_plan_too_large")):
        return ""
    out_path = os.path.join(cache_root or _xstack_cache_root(repo_root), "xstack", "FULL_PLAN_TOO_LARGE.md")
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# FULL Plan Size Warning\n\n")
        handle.write("- profile: `{}`\n".format(plan_payload.get("profile", "")))
        handle.write("- plan_hash: `{}`\n".format(plan_payload.get("plan_hash", "")))
        handle.write("- total_work_units: `{}`\n".format(estimate.get("total_work_units", 0)))
        handle.write("- suggested_action: `partition test/audit groups and increase sharding granularity`\n")
    return out_path


def _write_snapshot_report(repo_root, plan_payload, result, profile_path):
    out_path = os.path.join(repo_root, SNAPSHOT_REPORT_REL)
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# XStack Snapshot Report\n\n")
        handle.write("- gate_kind: `snapshot`\n")
        handle.write("- profile: `{}`\n".format(str(plan_payload.get("profile", ""))))
        handle.write("- plan_hash: `{}`\n".format(str(plan_payload.get("plan_hash", ""))))
        handle.write("- cache_hits: `{}`\n".format(int(result.get("cache_hits", 0))))
        handle.write("- cache_misses: `{}`\n".format(int(result.get("cache_misses", 0))))
        handle.write("- total_seconds: `{:.6f}`\n".format(float(result.get("total_seconds", 0.0))))
        handle.write("- profile_trace: `{}`\n".format(os.path.relpath(profile_path, repo_root).replace("\\", "/")))
        warning = str(result.get("full_plan_warning", "")).strip()
        if warning:
            handle.write("- full_plan_warning: `{}`\n".format(warning))
    return out_path


def _run_gate_xstack(
    repo_root,
    gate_kind,
    workspace_id="",
    force_strict=False,
    force_full=False,
    force_full_all=False,
    trace=False,
    profile_report=False,
    ledger_export=False,
):
    if not _XSTACK_CORE_READY:
        return None
    if gate_kind in ("doctor", "remediate", "run-queue"):
        return None

    snapshot_mode = gate_kind == "snapshot"
    _env, _tools_dir, ws_dirs = _canonical_env(repo_root, ws_id=workspace_id)
    resolved_ws = str(ws_dirs.get("workspace_id", "")).strip() or canonical_workspace_id(repo_root, env=os.environ)
    cache_root = _xstack_cache_root(repo_root, workspace_id=resolved_ws)
    tracked_before = _git_tracked_status(repo_root)
    reset_profile(trace=trace)
    profile = _profile_for_command(
        gate_kind,
        force_strict=force_strict,
        force_full=force_full,
        force_full_all=force_full_all,
    )
    plan_payload = build_execution_plan(
        repo_root=repo_root,
        gate_command=gate_kind,
        requested_profile=profile,
        workspace_id=resolved_ws,
        cache_root=cache_root,
    )
    result = execute_plan(
        repo_root=repo_root,
        plan_payload=plan_payload,
        trace=trace,
        profile_report=profile_report,
        cache_root=cache_root,
    )
    profile_path = export_profile_json(
        os.path.join(cache_root, "last_profile.json"),
        extra={
            "gate_kind": gate_kind,
            "profile": plan_payload.get("profile", ""),
            "plan_hash": plan_payload.get("plan_hash", ""),
            "cache_hits": result.get("cache_hits", 0),
            "cache_misses": result.get("cache_misses", 0),
            "total_seconds": result.get("total_seconds", 0.0),
            "exit_code": result.get("exit_code", 1),
        },
    )

    warning_path = _write_full_plan_warning(repo_root, plan_payload, cache_root=cache_root)
    output = {
        "result": "xstack_plan_complete",
        "gate_kind": gate_kind,
        "workspace_id": resolved_ws,
        "profile": plan_payload.get("profile", ""),
        "strict_variant": plan_payload.get("strict_variant", ""),
        "plan_hash": plan_payload.get("plan_hash", ""),
        "plan_path": os.path.relpath(plan_payload.get("plan_path", ""), repo_root).replace("\\", "/") if plan_payload.get("plan_path") else "",
        "cache_hits": result.get("cache_hits", 0),
        "cache_misses": result.get("cache_misses", 0),
        "failure_classes": result.get("failure_classes", []),
        "failure_summary": result.get("failure_summary", []),
        "primary_failure_class": result.get("primary_failure_class", ""),
        "total_seconds": result.get("total_seconds", 0.0),
        "exit_code": result.get("exit_code", 1),
        "full_plan_warning": os.path.relpath(warning_path, repo_root).replace("\\", "/") if warning_path else "",
        "profile_path": os.path.relpath(profile_path, repo_root).replace("\\", "/"),
    }
    try:
        runner_ids = [
            str(row.get("runner_id", "")).strip()
            for row in (result.get("results") or [])
            if isinstance(row, dict) and str(row.get("runner_id", "")).strip()
        ]
        canonical_artifacts = []
        for row in (plan_payload.get("nodes") or []):
            if not isinstance(row, dict):
                continue
            for rel in (row.get("expected_artifacts") or []):
                token = str(rel).replace("\\", "/").strip("/")
                if token:
                    canonical_artifacts.append(token)
        ledger_entry = build_ledger_entry(
            repo_state_hash=str(plan_payload.get("repo_state_hash", "")),
            plan_hash=str(plan_payload.get("plan_hash", "")),
            profile=str(plan_payload.get("profile", "")),
            runner_ids=runner_ids,
            cache_hits=int(result.get("cache_hits", 0)),
            cache_misses=int(result.get("cache_misses", 0)),
            artifact_hashes=canonical_ledger_artifact_hashes(repo_root, canonical_artifacts),
            failure_class=str(result.get("primary_failure_class", "")),
            duration_s=float(result.get("total_seconds", 0.0)),
            workspace_id=resolved_ws,
        )
        ledger_meta = append_ledger_entry(repo_root, ledger_entry, cache_root=cache_root)
        if ledger_meta.get("entry_path"):
            output["ledger_entry"] = os.path.relpath(str(ledger_meta["entry_path"]), repo_root).replace("\\", "/")
    except Exception:
        pass
    if profile_report:
        output["profile_report"] = result.get("profile_report", {})
    snapshot_report_rel = ""
    if snapshot_mode and int(result.get("exit_code", 1)) == 0:
        snapshot_path = _write_snapshot_report(repo_root, plan_payload, output, profile_path)
        snapshot_report_rel = os.path.relpath(snapshot_path, repo_root).replace("\\", "/")
        output["snapshot_report"] = snapshot_report_rel
        if ledger_export:
            try:
                ledger_snapshot_path = export_ledger_snapshot_markdown(
                    repo_root=repo_root,
                    out_path=os.path.join(repo_root, LEDGER_SNAPSHOT_REL),
                    cache_root=cache_root,
                )
                output["ledger_snapshot"] = os.path.relpath(ledger_snapshot_path, repo_root).replace("\\", "/")
            except Exception:
                pass

    tracked_after = _git_tracked_status(repo_root)
    violations, touched_manifest = _tracked_write_violations(
        repo_root=repo_root,
        gate_kind=gate_kind,
        profile=str(plan_payload.get("profile", "")),
        before_status=tracked_before,
        after_status=tracked_after,
        snapshot_mode=snapshot_mode,
        workspace_id=resolved_ws,
    )
    output["touched_manifest"] = os.path.relpath(touched_manifest, repo_root).replace("\\", "/")
    if violations:
        output["result"] = "refused"
        output["refusal_code"] = "refuse.tracked_write_outside_policy"
        output["touched_tracked_files"] = violations
        output["exit_code"] = 1
        print(json.dumps(output, indent=2, sort_keys=True))
        return 1

    print(json.dumps(output, indent=2, sort_keys=True))
    return int(result.get("exit_code", 1))


def _run_gate(
    repo_root,
    gate_kind,
    only_gate_ids=None,
    workspace_id="",
    queue_file="",
    force_strict=False,
    force_full=False,
    force_full_all=False,
    ledger_export=False,
):
    if not only_gate_ids:
        xstack_code = _run_gate_xstack(
            repo_root,
            gate_kind,
            workspace_id=workspace_id,
            force_strict=force_strict,
            force_full=force_full,
            force_full_all=force_full_all,
            trace=bool(os.environ.get("DOM_GATE_TRACE", "")),
            profile_report=bool(os.environ.get("DOM_GATE_PROFILE_REPORT", "")),
            ledger_export=ledger_export,
        )
        if xstack_code is not None:
            return xstack_code

    if gate_kind == "run-queue":
        return _run_queue(repo_root, queue_file, workspace_id=workspace_id)

    env, tools_dir, ws_dirs = _canonical_env(repo_root, ws_id=workspace_id)
    mode_eval = _effective_mode_for_gate(
        repo_root,
        gate_kind,
        force_strict=force_strict,
        force_full=(force_full or force_full_all),
    )
    gate_mode = str(mode_eval.get("mode", FAST_MODE)).strip() or FAST_MODE

    gate_policy_version = load_gate_policy_version(repo_root, GATE_POLICY_REGISTRY_REL)
    state_hash = compute_workspace_state_hash(repo_root, gate_policy_version)
    if gate_kind in ("precheck", "taskcheck", "exitcheck", "dev", "verify", "strict", "full", "dist"):
        cached = _try_short_circuit(
            repo_root,
            ws_dirs=ws_dirs,
            gate_kind=gate_kind,
            gate_mode=gate_mode,
            state_hash=state_hash,
        )
        if cached == 0:
            return 0

    verify_build_dir, ws_dirs = select_verify_build_dir(
        repo_root,
        ws_id=ws_dirs.get("workspace_id", workspace_id),
        platform_id=ws_dirs.get("platform", ""),
        arch_id=ws_dirs.get("arch", ""),
        env=env,
    )
    dist_root = ws_dirs.get("dist_root", os.path.join(repo_root, "dist"))
    remediation_root = ws_dirs.get("remediation_root", os.path.join(repo_root, REMEDIATION_ROOT_REL))
    playbooks = _load_playbooks(repo_root)
    policy = _load_gate_policy(repo_root)
    verification = {
        "gate_kind": gate_kind,
        "gate_mode": gate_mode,
        "impact": mode_eval.get("impact", ""),
        "impact_reason": mode_eval.get("reason", ""),
        "repo_root": repo_root.replace("\\", "/"),
        "tools_dir": tools_dir.replace("\\", "/"),
        "workspace_id": ws_dirs.get("workspace_id", ""),
        "verify_build_dir": verify_build_dir.replace("\\", "/"),
        "dist_root": dist_root.replace("\\", "/"),
        "commands": [],
        "skipped": [],
        "warnings": [],
    }
    actions = []

    if gate_kind == "doctor":
        payload = {
            "repo_root": repo_root.replace("\\", "/"),
            "tools_dir": tools_dir.replace("\\", "/"),
            "build_dirs": {
                k: v.replace("\\", "/")
                for k, v in canonical_build_dirs(
                    repo_root,
                    ws_id=ws_dirs.get("workspace_id", ""),
                    platform_id=ws_dirs.get("platform", ""),
                    arch_id=ws_dirs.get("arch", ""),
                    env=env,
                ).items()
            },
            "workspace_id": ws_dirs.get("workspace_id", ""),
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

    if gate_mode == FAST_MODE and gate_kind in ("verify", "exitcheck", "taskcheck"):
        verification["warnings"].append(
            "FAST mode active: strict/full checks skipped. Run `gate.py strict` or `gate.py full` for exhaustive validation."
        )

    phase_specs = _phase_specs_for_gate(gate_kind, gate_mode, str(mode_eval.get("impact", "")))

    for class_ids, requested_targets in phase_specs:
        code, phase_verification, phase_actions = _execute_gate_set(
            repo_root,
            env,
            gate_kind,
            policy,
            class_ids,
            playbooks,
            verify_build_dir,
            ws_id=ws_dirs.get("workspace_id", ""),
            dist_root=dist_root,
            remediation_root=remediation_root,
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
            remediation_root=remediation_root,
        )
    post_state_hash = compute_workspace_state_hash(repo_root, gate_policy_version)
    _mark_short_circuit_ok(
        repo_root,
        ws_dirs=ws_dirs,
        gate_kind=gate_kind,
        gate_mode=gate_mode,
        state_hash=post_state_hash,
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canonical gate runner with autonomous remediation.")
    parser.add_argument(
        "command",
        choices=(
            "dev",
            "verify",
            "strict",
            "full",
            "snapshot",
            "dist",
            "doctor",
            "remediate",
            "precheck",
            "taskcheck",
            "exitcheck",
            "run-queue",
        ),
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--workspace-id", default="")
    parser.add_argument("--only-gate", action="append", default=[])
    parser.add_argument("--queue-file", default="")
    parser.add_argument("--strict", action="store_true", help="Force STRICT mode for verify/exitcheck/taskcheck/dev.")
    parser.add_argument("--full", action="store_true", help="Force FULL mode for verify/exitcheck/taskcheck/dev.")
    parser.add_argument(
        "--full-all",
        action="store_true",
        help="Run FULL_ALL profile (all registered shards) for xstack-backed commands.",
    )
    parser.add_argument("--trace", action="store_true", help="Emit structured XStack trace events.")
    parser.add_argument("--profile-report", action="store_true", help="Include scheduler profile report in output.")
    parser.add_argument(
        "--ledger-export",
        action="store_true",
        help="Export snapshot-mode execution ledger summary to docs/audit/system/LEDGER_SNAPSHOT.md.",
    )
    args = parser.parse_args()
    if args.trace:
        os.environ["DOM_GATE_TRACE"] = "1"
    else:
        os.environ.pop("DOM_GATE_TRACE", None)
    if args.profile_report:
        os.environ["DOM_GATE_PROFILE_REPORT"] = "1"
    else:
        os.environ.pop("DOM_GATE_PROFILE_REPORT", None)
    return _run_gate(
        _repo_root(args.repo_root),
        args.command,
        only_gate_ids=args.only_gate,
        workspace_id=args.workspace_id,
        queue_file=args.queue_file,
        force_strict=args.strict,
        force_full=args.full,
        force_full_all=args.full_all,
        ledger_export=args.ledger_export,
    )


if __name__ == "__main__":
    raise SystemExit(main())
