"""FAST test: PROC-7 replay tools report stable research hash chains."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_research_hash_match"
TEST_TAGS = ["fast", "proc", "proc7", "replay", "proof"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_research_sequence(repo_root: str) -> dict:
    from tools.xstack.testx.tests.proc7_testlib import (
        cloned_state,
        execute_process,
        run_experiment_cycle,
        run_reverse_action,
    )

    state = cloned_state(repo_root)
    experiment = run_experiment_cycle(
        repo_root=repo_root,
        state=state,
        run_id="run.proc7.replay.001",
    )
    if str((dict(experiment.get("complete") or {})).get("result", "")).strip() != "complete":
        return {"result": "failed_experiment", "state": state}

    reverse = run_reverse_action(
        repo_root=repo_root,
        state=state,
        target_item_id="item.proc7.replay.target",
        method="assay",
        research_policy_id="research.default",
    )
    if str(reverse.get("result", "")).strip() != "complete":
        return {"result": "failed_reverse", "state": state}

    candidate_rows = [
        dict(row)
        for row in list(state.get("candidate_process_definition_rows") or [])
        if isinstance(row, dict)
    ]
    if not candidate_rows:
        return {"result": "failed_candidate_missing", "state": state}
    candidate_id = str(candidate_rows[0].get("candidate_id", "")).strip()
    if not candidate_id:
        return {"result": "failed_candidate_missing", "state": state}

    promoted = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.candidate_promote_to_defined",
        inputs={
            "candidate_id": candidate_id,
            "required_replications": 1,
            "min_qc_pass_rate": 700,
            "min_stabilization_score": 650,
        },
    )
    if str(promoted.get("result", "")).strip() != "complete":
        return {"result": "failed_promotion", "state": state}
    return {"result": "complete", "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_experiment_window import verify_experiment_replay_window
    from tools.process.tool_replay_reverse_engineering_window import (
        verify_reverse_engineering_replay_window,
    )

    first = _run_research_sequence(repo_root)
    second = _run_research_sequence(repo_root)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first research replay fixture failed"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second research replay fixture failed"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})

    experiment_report = verify_experiment_replay_window(
        state_payload=first_state,
        expected_payload=second_state,
    )
    if str(experiment_report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "experiment replay verifier reported violations: {}".format(
                list(experiment_report.get("violations") or [])
            ),
        }

    reverse_report = verify_reverse_engineering_replay_window(
        state_payload=first_state,
        expected_payload=second_state,
    )
    if str(reverse_report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "reverse replay verifier reported violations: {}".format(
                list(reverse_report.get("violations") or [])
            ),
        }

    for report, keys in (
        (
            dict(experiment_report.get("observed") or {}),
            (
                "experiment_result_hash_chain",
                "experiment_run_binding_hash_chain",
                "candidate_process_hash_chain",
                "candidate_model_binding_hash_chain",
            ),
        ),
        (
            dict(reverse_report.get("observed") or {}),
            (
                "reverse_engineering_record_hash_chain",
                "candidate_process_hash_chain",
                "candidate_model_binding_hash_chain",
                "candidate_promotion_hash_chain",
            ),
        ),
    ):
        for key in keys:
            value = str(report.get(key, "")).strip().lower()
            if not _HASH64.fullmatch(value):
                return {"status": "fail", "message": "observed {} missing/invalid".format(key)}

    return {"status": "pass", "message": "PROC-7 replay tools report stable research hash chains"}

