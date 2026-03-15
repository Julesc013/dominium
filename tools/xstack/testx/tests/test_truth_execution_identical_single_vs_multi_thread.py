"""FAST test: authoritative truth remains effectively single-thread and stable."""

from __future__ import annotations


TEST_ID = "test_truth_execution_identical_single_vs_multi_thread"
TEST_TAGS = ["fast", "concurrency", "truth", "determinism"]


def run(repo_root: str):
    import copy

    from tools.xstack.sessionx.scheduler import replay_intent_script_srz
    from tools.xstack.testx.tests import test_thread_count_invariance_for_collision as collision_fixture

    common = {
        "repo_root": repo_root,
        "law_profile": collision_fixture._law_profile(),
        "authority_context": collision_fixture._authority_context(),
        "navigation_indices": {},
        "policy_context": {},
        "pack_lock_hash": "0" * 64,
        "registry_hashes": {},
        "logical_shards": 1,
    }
    base_state = collision_fixture._state()
    intents = collision_fixture._intents()
    workers_1 = replay_intent_script_srz(
        universe_state=copy.deepcopy(base_state),
        intents=copy.deepcopy(intents),
        worker_count=1,
        **common,
    )
    workers_2 = replay_intent_script_srz(
        universe_state=copy.deepcopy(base_state),
        intents=copy.deepcopy(intents),
        worker_count=2,
        **common,
    )

    if str(workers_1.get("result", "")).strip() != "complete" or str(workers_2.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "truth scheduler run failed for single-vs-multi-thread request check",
        }
    srz_one = dict(workers_1.get("srz") or {})
    srz_two = dict(workers_2.get("srz") or {})
    if int(srz_one.get("worker_count_effective", 0) or 0) != 1 or int(srz_two.get("worker_count_effective", 0) or 0) != 1:
        return {
            "status": "fail",
            "message": "authoritative truth scheduler did not remain effectively single-threaded",
        }
    if str(workers_1.get("final_state_hash", "")).strip() != str(workers_2.get("final_state_hash", "")).strip():
        return {
            "status": "fail",
            "message": "final_state_hash changed across single-vs-multi-thread requests",
        }
    return {
        "status": "pass",
        "message": "authoritative truth remained stable while worker_count_effective stayed single-threaded",
    }
