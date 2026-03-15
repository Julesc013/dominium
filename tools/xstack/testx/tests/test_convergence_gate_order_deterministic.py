"""FAST test: convergence gate order is deterministic."""

from __future__ import annotations


TEST_ID = "test_convergence_gate_order_deterministic"
TEST_TAGS = ["fast", "convergence", "release", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_gate_testlib import step_ids

    expected = [
        "validation_strict",
        "meta_stability",
        "time_anchor",
        "arch_audit",
        "cap_neg_interop",
        "pack_compat_stress",
        "lib_stress",
        "product_boot_matrix",
        "ipc_attach_smoke",
        "supervisor_hardening",
        "mvp_smoke",
        "mvp_stress",
        "mvp_cross_platform",
    ]
    actual = step_ids()
    if actual != expected:
        return {"status": "fail", "message": "convergence gate step order drifted"}
    return {"status": "pass", "message": "convergence gate order is deterministic"}
