"""FAST test: APPSHELL-4 endpoint discovery remains deterministic."""

from __future__ import annotations


TEST_ID = "test_endpoint_discovery_deterministic"
TEST_TAGS = ["fast", "appshell", "ipc", "discovery"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="discovery")
    first = list(dict(report.get("discovery_first") or {}).get("endpoints") or [])
    second = list(dict(report.get("discovery_second") or {}).get("endpoints") or [])
    if first != second:
        return {"status": "fail", "message": "IPC endpoint discovery order drifted within a deterministic run"}
    if not first:
        return {"status": "fail", "message": "no IPC endpoints were published for discovery"}
    if str(dict(first[0]).get("endpoint_id", "")).strip() != str(report.get("endpoint_id", "")).strip():
        return {"status": "fail", "message": "published endpoint id did not match discovery output"}
    return {"status": "pass", "message": "IPC endpoint discovery order remains deterministic"}
