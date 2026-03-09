"""FAST test: MW-3 surface generator routing remains deterministic for identical tile requests."""

from __future__ import annotations

import sys


TEST_ID = "test_surface_gen_routing_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "surface", "routing"]


def _route_signature(result: dict) -> tuple[str, str, str]:
    return (
        str(result.get("surface_routing_id", "")).strip(),
        str(result.get("surface_generator_id", "")).strip(),
        str(result.get("surface_handler_id", "")).strip(),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.mw3_testlib import generate_surface_fixture_result

    _fixture, first = generate_surface_fixture_result(repo_root)
    _fixture, second = generate_surface_fixture_result(repo_root)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-3 routing fixture did not complete"}
    first_signature = _route_signature(first)
    second_signature = _route_signature(second)
    if first_signature != second_signature:
        return {"status": "fail", "message": "MW-3 surface generator routing drifted across repeated runs"}
    if not all(first_signature):
        return {"status": "fail", "message": "MW-3 surface routing omitted routing or generator identifiers"}
    return {"status": "pass", "message": "MW-3 surface generator routing deterministic for identical tile requests"}
