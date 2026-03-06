"""FAST test: PROC-5 capsule execution is deterministic across equivalent runs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_capsule_execution_deterministic"
TEST_TAGS = ["fast", "proc", "proc5", "capsule", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _hash(state: dict, key: str) -> str:
    return str(state.get(key, "")).strip().lower()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc5_testlib import run_proc5_capsule_case

    first = run_proc5_capsule_case(repo_root=repo_root)
    second = run_proc5_capsule_case(repo_root=repo_root)

    for label, payload in (("first", first), ("second", second)):
        generation = dict(payload.get("generation") or {})
        execution = dict(payload.get("execution") or {})
        if str(generation.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} generation did not complete".format(label)}
        if str(execution.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} execution did not complete".format(label)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    for key in (
        "capsule_generation_hash_chain",
        "capsule_execution_hash_chain",
        "compiled_model_hash_chain",
    ):
        a_hash = _hash(first_state, key)
        b_hash = _hash(second_state, key)
        if not _HASH64.fullmatch(a_hash):
            return {"status": "fail", "message": "{} missing/invalid on first run".format(key)}
        if a_hash != b_hash:
            return {"status": "fail", "message": "{} mismatch across equivalent runs".format(key)}

    return {"status": "pass", "message": "PROC-5 capsule execution hash chains are deterministic"}

