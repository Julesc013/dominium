"""FAST test: CHEM-3 corrosion increments are deterministic for equivalent inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_corrosion_increments_deterministic"
TEST_TAGS = ["fast", "chem", "degradation", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_degradation_testlib import execute_process, seed_degradation_state

    state = seed_degradation_state()
    result = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.degradation_tick",
        inputs={
            "target_id": "edge.fluid.main",
            "profile_id": "profile.pipe_steel_basic",
            "target_kind": "edge",
            "parameters": {
                "temperature": 37315,
                "moisture": 520,
                "radiation_intensity": 240,
                "entropy_value": 360,
                "fluid_composition_tags": ["tag.fluid.corrosive"],
            },
        },
    )
    return {"state": dict(state), "result": dict(result)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root)
    second = _run_once(repo_root)

    for label, payload in (("first", first), ("second", second)):
        if str((dict(payload.get("result") or {}).get("result", "")).strip()) != "complete":
            return {"status": "fail", "message": "{} degradation_tick refused".format(label)}

    def _corrosion_level(state: dict) -> int:
        for row in list(state.get("chem_degradation_state_rows") or []):
            if not isinstance(row, dict):
                continue
            if str(row.get("target_id", "")).strip() != "edge.fluid.main":
                continue
            if str(row.get("degradation_kind_id", "")).strip() != "corrosion":
                continue
            return int(max(0, int(row.get("level_value", 0) or 0)))
        return 0

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    level_first = _corrosion_level(first_state)
    level_second = _corrosion_level(second_state)
    if level_first <= 0:
        return {"status": "fail", "message": "corrosion level should increment above zero"}
    if level_first != level_second:
        return {"status": "fail", "message": "corrosion level drifted across equivalent runs"}

    hash_a = str(first_state.get("degradation_hash_chain", "")).strip().lower()
    hash_b = str(second_state.get("degradation_hash_chain", "")).strip().lower()
    event_a = str(first_state.get("degradation_event_hash_chain", "")).strip().lower()
    event_b = str(second_state.get("degradation_event_hash_chain", "")).strip().lower()
    for token in (hash_a, hash_b, event_a, event_b):
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing deterministic degradation hash chain"}
    if hash_a != hash_b or event_a != event_b:
        return {"status": "fail", "message": "degradation hash chains drifted across equivalent runs"}
    return {"status": "pass", "message": "corrosion increments are deterministic"}
