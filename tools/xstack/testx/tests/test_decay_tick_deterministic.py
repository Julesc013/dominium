"""FAST test: SIG-5 trust decay tick is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.decay_tick_deterministic"
TEST_TAGS = ["fast", "signals", "trust", "determinism"]


def _belief_registry() -> dict:
    return {
        "record": {
            "belief_policies": [
                {
                    "schema_version": "1.0.0",
                    "belief_policy_id": "belief.default",
                    "acceptance_threshold": 0.5,
                    "decay_rate_per_tick": 0.01,
                    "update_rule_id": "update.linear_adjust",
                    "extensions": {},
                }
            ]
        }
    }


def _run_once() -> dict:
    from signals import process_trust_decay_tick

    return process_trust_decay_tick(
        current_tick=200,
        trust_edge_rows=[
            {
                "from_subject_id": "subject.a",
                "to_subject_id": "subject.b",
                "trust_weight": 0.9,
                "evidence_count": 4,
                "last_updated_tick": 120,
                "extensions": {},
            },
            {
                "from_subject_id": "subject.c",
                "to_subject_id": "subject.d",
                "trust_weight": 0.4,
                "evidence_count": 1,
                "last_updated_tick": 121,
                "extensions": {},
            },
        ],
        belief_policy_registry=_belief_registry(),
        belief_policy_id="belief.default",
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "trust decay output drifted across identical runs"}
    edges = list(first.get("trust_edge_rows") or [])
    if len(edges) != 2:
        return {"status": "fail", "message": "expected trust decay to preserve edge cardinality"}
    if float(dict(edges[0]).get("trust_weight", 0.0)) >= 0.9:
        return {"status": "fail", "message": "decay tick should reduce trust weight when decay_rate_per_tick > 0"}
    return {"status": "pass", "message": "trust decay deterministic"}
