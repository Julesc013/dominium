"""STRICT test: LOGIC-6 reduced-graph compilation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_compile_reduced_graph_deterministic"
TEST_TAGS = ["strict", "logic", "compile", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_eval_test_utils import (
        compile_logic_network_fixture,
        make_scalar_comparator_network,
    )

    _, logic_network_state = make_scalar_comparator_network(network_id="net.logic.compile.reduced")
    first = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.reduced",
        logic_network_state=logic_network_state,
    )["compile_eval"]
    second = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.reduced",
        logic_network_state=logic_network_state,
    )["compile_eval"]

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "reduced-graph compile fixture did not complete twice"}
    if str(first.get("compiled_type_id", "")) != "compiled.reduced_graph":
        return {"status": "fail", "message": "scalar comparator should compile as compiled.reduced_graph"}
    for key in ("compiled_model_row", "equivalence_proof_row", "validity_domain_row", "compile_result_row"):
        if dict(first.get(key) or {}) != dict(second.get(key) or {}):
            return {"status": "fail", "message": "reduced-graph compile drifted for {}".format(key)}
    return {"status": "pass", "message": "reduced-graph compilation is deterministic"}
