"""FAST test: fixed-point helpers remain deterministic."""

from __future__ import annotations


TEST_ID = "test_fixed_point_operations_deterministic"
TEST_TAGS = ["fast", "numeric", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.numeric_discipline_testlib import numeric_ops_payload

    payload_left = numeric_ops_payload()
    payload_right = numeric_ops_payload()
    if payload_left != payload_right:
        return {"status": "fail", "message": "fixed-point payload drifted across repeated evaluation"}
    divide = dict(payload_left.get("divide") or {})
    mul_div = dict(payload_left.get("mul_div") or {})
    if divide.get("5_over_2") != 2 or divide.get("7_over_2") != 4 or divide.get("minus_7_over_2") != -4:
        return {"status": "fail", "message": "deterministic_divide results changed"}
    if mul_div.get("5_times_3_over_2") != 8 or mul_div.get("11_times_7_over_3") != 26:
        return {"status": "fail", "message": "deterministic_mul_div results changed"}
    return {"status": "pass", "message": "fixed-point helpers are deterministic and stable"}
