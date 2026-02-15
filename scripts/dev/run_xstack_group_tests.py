#!/usr/bin/env python3
"""Run curated XStack test groups without invoking monolithic TestX suites."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime


GROUP_TESTS = {
    "testx.group.core.invariants": [
        ["tests/invariant/test_gate_plan_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_plan_hash_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_workspace_isolation.py", "--repo-root", "."],
        ["tests/invariant/test_performance_ceiling_detection.py", "--repo-root", "."],
        ["tests/invariant/test_gate_cache_correctness.py", "--repo-root", "."],
        ["tests/invariant/test_cache_invalidation_on_runner_change.py", "--repo-root", "."],
        ["tests/invariant/test_ledger_deterministic_when_inputs_identical.py", "--repo-root", "."],
        ["tests/invariant/test_failure_classification_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_repox_cache_equivalence.py", "--repo-root", "."],
        ["tests/invariant/test_testx_group_mapping.py", "--repo-root", "."],
        ["tests/invariant/test_auditx_group_mapping.py", "--repo-root", "."],
        ["tests/invariant/test_pack_resolution_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_pack_duplicate_pack_id_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_circular_dependency_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_duplicate_contribution_id_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_unsupported_contribution_type_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_list_ordering_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_deterministic_outputs.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_input_change_hash_change.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_cache_hit.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_conflict_refusal_deterministic.py", "--repo-root", "."],
        ["tests/invariant/test_lockfile_validate_tamper_refusal.py", "--repo-root", "."],
    ],
    "testx.group.runtime.verify": [
        ["tests/integration/test_gate_fast_strict_full_profiles.py", "--repo-root", ".", "--case", "profiles"],
        ["tests/integration/test_gate_fast_strict_full_profiles.py", "--repo-root", ".", "--case", "fast_no_full_suite"],
        ["tests/integration/test_gate_fast_strict_full_profiles.py", "--repo-root", ".", "--case", "full_shards_groups"],
        ["tests/invariant/test_intent_without_authority_refused.py", "--repo-root", "."],
        ["tests/invariant/test_survival_no_console.py", "--repo-root", "."],
        ["tests/invariant/test_survival_no_freecam.py", "--repo-root", "."],
        ["tests/invariant/test_server_rejects_capability_escalation.py", "--repo-root", "."],
        ["tests/invariant/test_survival_diegetic_only.py", "--repo-root", "."],
        ["tests/invariant/test_observer_watermark_required.py", "--repo-root", "."],
    ],
    "testx.group.full.verify": [
        ["tests/invariant/test_gate_plan_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_plan_hash_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_workspace_isolation.py", "--repo-root", "."],
        ["tests/invariant/test_performance_ceiling_detection.py", "--repo-root", "."],
        ["tests/invariant/test_gate_cache_correctness.py", "--repo-root", "."],
        ["tests/invariant/test_cache_invalidation_on_runner_change.py", "--repo-root", "."],
        ["tests/invariant/test_ledger_deterministic_when_inputs_identical.py", "--repo-root", "."],
        ["tests/invariant/test_failure_classification_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_repox_cache_equivalence.py", "--repo-root", "."],
        ["tests/invariant/test_testx_group_mapping.py", "--repo-root", "."],
        ["tests/invariant/test_auditx_group_mapping.py", "--repo-root", "."],
        ["tests/invariant/test_pack_resolution_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_pack_duplicate_pack_id_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_circular_dependency_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_duplicate_contribution_id_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_unsupported_contribution_type_refusal.py", "--repo-root", "."],
        ["tests/invariant/test_pack_list_ordering_determinism.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_deterministic_outputs.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_input_change_hash_change.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_cache_hit.py", "--repo-root", "."],
        ["tests/invariant/test_registry_compile_conflict_refusal_deterministic.py", "--repo-root", "."],
        ["tests/invariant/test_lockfile_validate_tamper_refusal.py", "--repo-root", "."],
        ["tests/integration/test_gate_fast_strict_full_profiles.py", "--repo-root", ".", "--case", "profiles"],
        ["tests/integration/test_gate_fast_strict_full_profiles.py", "--repo-root", ".", "--case", "full_shards_groups"],
        ["tests/invariant/test_intent_without_authority_refused.py", "--repo-root", "."],
        ["tests/invariant/test_survival_no_console.py", "--repo-root", "."],
        ["tests/invariant/test_survival_no_freecam.py", "--repo-root", "."],
        ["tests/invariant/test_server_rejects_capability_escalation.py", "--repo-root", "."],
        ["tests/invariant/test_survival_diegetic_only.py", "--repo-root", "."],
        ["tests/invariant/test_observer_watermark_required.py", "--repo-root", "."],
    ],
}


def _norm(path):
    return os.path.normpath(path)


def _write_json(path, payload):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_md(path, group_id, summary):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# XStack Test Group Summary\n\n")
        handle.write("- group_id: `{}`\n".format(group_id))
        handle.write("- returncode: `{}`\n".format(summary.get("returncode", 1)))
        handle.write("- selected_test_count: `{}`\n".format(summary.get("selected_test_count", 0)))
        handle.write("- suite_passed: `{}`\n".format("true" if summary.get("suite_passed") else "false"))


def _run(repo_root, argv):
    cmd = [sys.executable, _norm(os.path.join(repo_root, argv[0]))] + list(argv[1:])
    return subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Run deterministic XStack test group checks.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--group-id", required=True)
    parser.add_argument("--summary-json", default="docs/audit/testx/TESTX_SUMMARY.json")
    parser.add_argument("--summary-md", default="docs/audit/testx/TESTX_SUMMARY.md")
    parser.add_argument("--run-meta-json", default="docs/audit/testx/TESTX_RUN_META.json")
    args = parser.parse_args()

    repo_root = _norm(os.path.abspath(args.repo_root))
    group_id = str(args.group_id).strip()
    tests = GROUP_TESTS.get(group_id)
    if not tests:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.unknown_test_group", "group_id": group_id}, indent=2, sort_keys=True))
        return 2

    started = time.time()
    executed = []
    outputs = []
    returncode = 0
    for test_argv in tests:
        rel_script = str(test_argv[0]).replace("\\", "/")
        result = _run(repo_root, test_argv)
        executed.append(rel_script)
        outputs.append({"test": rel_script, "returncode": int(result.returncode), "output": result.stdout or ""})
        if result.returncode != 0 and returncode == 0:
            returncode = int(result.returncode)

    summary = {
        "artifact_class": "CANONICAL",
        "registry_id": "dominium.registry.governance.testx_groups",
        "registry_version": "1.0.0",
        "returncode": int(returncode),
        "selected_test_count": len(executed),
        "selected_tests": executed,
        "suite_id": group_id,
        "suite_passed": bool(returncode == 0),
        "warnings": [],
        "required_test_tags": ["xstack", "gate"],
        "executed_tests": executed,
    }
    run_meta = {
        "artifact_class": "RUN_META",
        "duration_ms": int((time.time() - started) * 1000.0),
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "returncode": int(returncode),
        "status": "DERIVED",
        "suite_id": group_id,
    }

    summary_json = _norm(os.path.join(repo_root, args.summary_json))
    summary_md = _norm(os.path.join(repo_root, args.summary_md))
    run_meta_json = _norm(os.path.join(repo_root, args.run_meta_json))
    _write_json(summary_json, summary)
    _write_md(summary_md, group_id, summary)
    _write_json(run_meta_json, run_meta)

    payload = {
        "result": "suite_complete",
        "group_id": group_id,
        "returncode": int(returncode),
        "selected_tests": executed,
        "summary_json": os.path.relpath(summary_json, repo_root).replace("\\", "/"),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if returncode != 0:
        for row in outputs:
            if int(row.get("returncode", 0)) != 0:
                print(row.get("output", ""))
                break
    return int(returncode)


if __name__ == "__main__":
    raise SystemExit(main())
