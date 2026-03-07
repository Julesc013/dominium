"""STRICT test: LOGIC-6 automaton compilation explores state space deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_compile_automaton_state_exploration_deterministic"
TEST_TAGS = ["strict", "logic", "compile", "automaton"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_eval_test_utils import compile_logic_network_fixture, make_flip_flop_network

    _, logic_network_state = make_flip_flop_network(network_id="net.logic.compile.automaton")
    first = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.automaton",
        logic_network_state=logic_network_state,
    )["compile_eval"]
    second = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.automaton",
        logic_network_state=logic_network_state,
    )["compile_eval"]

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "automaton compile fixture did not complete twice"}
    if str(first.get("compiled_type_id", "")) != "compiled.automaton":
        return {"status": "fail", "message": "flip-flop network should compile as compiled.automaton"}
    first_ext = dict(dict(first.get("equivalence_proof_row") or {}).get("extensions") or {})
    second_ext = dict(dict(second.get("equivalence_proof_row") or {}).get("extensions") or {})
    for key in ("state_hash", "transition_hash", "explored_state_count", "transition_count"):
        if first_ext.get(key) != second_ext.get(key):
            return {"status": "fail", "message": "automaton proof drifted for {}".format(key)}
    if int(first_ext.get("explored_state_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "automaton proof must explore at least one state"}
    return {"status": "pass", "message": "automaton state exploration is deterministic"}
