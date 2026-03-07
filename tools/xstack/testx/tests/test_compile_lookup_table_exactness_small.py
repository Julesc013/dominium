"""STRICT test: LOGIC-6 small combinational networks compile to exact lookup tables."""

from __future__ import annotations

import sys


TEST_ID = "test_compile_lookup_table_exactness_small"
TEST_TAGS = ["strict", "logic", "compile", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_eval_test_utils import compile_logic_network_fixture, make_chain_network

    _, logic_network_state = make_chain_network(network_id="net.logic.compile.lookup")
    compile_eval = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.lookup",
        logic_network_state=logic_network_state,
    )["compile_eval"]
    if str(compile_eval.get("result", "")) != "complete":
        return {"status": "fail", "message": "lookup-table compile fixture did not complete"}
    if str(compile_eval.get("compiled_type_id", "")) != "compiled.lookup_table":
        return {"status": "fail", "message": "small combinational network should compile as compiled.lookup_table"}

    payload = dict(dict(compile_eval.get("compiled_model_row") or {}).get("compiled_payload_ref") or {}).get("payload") or {}
    table_rows = list(dict(payload or {}).get("table_rows") or [])
    proof_row = dict(compile_eval.get("equivalence_proof_row") or {})
    input_slots = list(dict(payload or {}).get("input_slots") or [])
    input_bits = [str(dict(row).get("input_bits", "")).strip() for row in table_rows if isinstance(row, dict)]
    width = len([row for row in input_slots if isinstance(row, dict)])
    expected_rows = 1 << width
    expected_bits = [format(index, "0{}b".format(width)) if width else "" for index in range(expected_rows)]
    if input_bits != expected_bits:
        return {"status": "fail", "message": "lookup table enumeration drifted: {}".format(input_bits)}
    if str(proof_row.get("proof_kind", "")) != "exact":
        return {"status": "fail", "message": "lookup-table proof must be exact"}
    proof_ext = dict(proof_row.get("extensions") or {})
    if str(proof_ext.get("proof_method", "")) != "exhaustive_lookup_table":
        return {"status": "fail", "message": "lookup-table proof method should be exhaustive_lookup_table"}
    if int(proof_ext.get("enumerated_input_count", 0) or 0) != expected_rows:
        return {
            "status": "fail",
            "message": "lookup-table proof should enumerate {} input rows".format(expected_rows),
        }
    return {"status": "pass", "message": "small lookup-table compilation is exact"}
