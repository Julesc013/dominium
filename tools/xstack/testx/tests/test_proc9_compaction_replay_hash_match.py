"""FAST test: PROC-9 compaction preserves replay anchor/hash guarantees."""

from __future__ import annotations

import sys


TEST_ID = "test_compaction_replay_hash_match_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "compaction", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_verify_proc_compaction import verify_proc_compaction
    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(repo_root=repo_root, seed=99121)
    report = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(report.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "PROC-9 stress run did not pass before compaction check"}

    compaction = verify_proc_compaction(
        state_payload=report,
        shard_id="shard.proc9.test",
        start_tick=0,
        end_tick=int(max(1, int(report.get("tick_horizon", 32) or 32))),
    )
    if str(compaction.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "PROC-9 compaction verification failed"}
    replay = dict(compaction.get("replay_result") or {})
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "PROC-9 replay-from-anchor check failed"}
    return {"status": "pass", "message": "PROC-9 compaction replay hash match verified"}
