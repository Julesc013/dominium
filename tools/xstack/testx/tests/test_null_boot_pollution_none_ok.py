"""FAST test: POLL null-boot path stays deterministic with poll.policy.none and empty pollutant registry."""

from __future__ import annotations

import sys


TEST_ID = "test_null_boot_pollution_none_ok"
TEST_TAGS = ["fast", "pollution", "null_boot"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_testlib import execute_pollution_emit, seed_pollution_state

    state = seed_pollution_state()
    out = execute_pollution_emit(
        repo_root=repo_root,
        state=state,
        inputs={
            "policy_id": "poll.policy.none",
            "origin_kind": "industrial",
            "origin_id": "stack.null",
            "pollutant_id": "pollutant.smoke_particulate",
            "emitted_mass": 10,
            "spatial_scope_id": "region.null",
        },
        policy_overrides={
            "pollutant_type_registry": {
                "record": {
                    "pollutant_types": [],
                }
            },
            "pollution_field_policy_registry": {
                "record": {
                    "pollution_field_policies": [
                        {
                            "schema_version": "1.0.0",
                            "policy_id": "poll.policy.none",
                            "tier": "P0",
                            "cell_update_rule_id": "rule.pollution.noop",
                            "wind_modifier_enabled": False,
                            "deterministic_fingerprint": "",
                            "extensions": {
                                "null_boot_safe": True,
                            },
                        }
                    ]
                }
            },
        },
    )
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pollution emit should complete in null-boot mode: {}".format(out)}
    if str(out.get("note", "")).strip() != "no_pollutant_types_registered":
        return {"status": "fail", "message": "expected null-boot note for empty pollutant registry"}
    if list(state.get("pollution_source_event_rows") or []):
        return {"status": "fail", "message": "null-boot pollution path should not emit source rows"}
    if list(state.get("pollution_total_rows") or []):
        return {"status": "fail", "message": "null-boot pollution path should not mutate totals"}
    return {"status": "pass", "message": "pollution null-boot policy path remains deterministic"}
