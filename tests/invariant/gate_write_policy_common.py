import os
import sys
from typing import List


def _load_routing(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.runners import _apply_output_routing  # pylint: disable=import-error

    return _apply_output_routing


def _must_have_flag(cmd: List[str], flag: str) -> bool:
    return str(flag).strip() in [str(item).strip() for item in cmd]


def check_non_snapshot_routing(repo_root: str) -> int:
    apply_output_routing = _load_routing(repo_root)
    scenarios = [
        (
            "repox_runner",
            "",
            ["python", "scripts/ci/check_repox_rules.py", "--repo-root", repo_root, "--profile", "FAST"],
            ("--proof-manifest-out", "--profile-out"),
        ),
        (
            "testx.group.core.invariants",
            "testx.group.core.invariants",
            ["python", "scripts/dev/run_xstack_group_tests.py", "--repo-root", repo_root, "--group-id", "testx.group.core.invariants"],
            ("--summary-json", "--summary-md", "--run-meta-json"),
        ),
        (
            "auditx.group.core.policy",
            "auditx.group.core.policy",
            ["python", "tools/auditx/auditx.py", "scan", "--repo-root", repo_root, "--changed-only", "--format", "json"],
            ("--output-root",),
        ),
        (
            "performx_runner",
            "",
            ["python", "tools/performx/performx.py", "run", "--repo-root", repo_root],
            ("--output-root",),
        ),
        (
            "compatx_runner",
            "",
            ["python", "tools/compatx/compatx.py", "verify", "--repo-root", repo_root],
            ("--output-root",),
        ),
        (
            "securex_runner",
            "",
            ["python", "tools/securex/securex.py", "verify", "--repo-root", repo_root],
            ("--output-dir",),
        ),
    ]

    for runner_id, group_id, base_cmd, expected_flags in scenarios:
        routed = apply_output_routing(
            cmd=list(base_cmd),
            runner_id=runner_id,
            group_id=group_id,
            repo_root=repo_root,
            snapshot_mode=False,
        )
        for flag in expected_flags:
            if not _must_have_flag(routed, flag):
                print("{} missing expected flag {}".format(runner_id, flag))
                return 1
        joined = " ".join(routed).replace("\\", "/")
        if ".xstack_cache/artifacts/" not in joined:
            print("{} output not routed to .xstack_cache/artifacts".format(runner_id))
            return 1
    return 0


def check_snapshot_passthrough(repo_root: str) -> int:
    apply_output_routing = _load_routing(repo_root)
    scenarios = [
        ("repox_runner", "", ["python", "scripts/ci/check_repox_rules.py", "--repo-root", repo_root, "--profile", "STRICT"]),
        ("auditx.group.core.policy", "auditx.group.core.policy", ["python", "tools/auditx/auditx.py", "scan", "--repo-root", repo_root]),
        ("testx.group.core.invariants", "testx.group.core.invariants", ["python", "scripts/dev/run_xstack_group_tests.py", "--repo-root", repo_root, "--group-id", "testx.group.core.invariants"]),
    ]
    for runner_id, group_id, base_cmd in scenarios:
        routed = apply_output_routing(
            cmd=list(base_cmd),
            runner_id=runner_id,
            group_id=group_id,
            repo_root=repo_root,
            snapshot_mode=True,
        )
        if routed != base_cmd:
            print("{} should not be rewritten in snapshot mode".format(runner_id))
            return 1
    return 0

