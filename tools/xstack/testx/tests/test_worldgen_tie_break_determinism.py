"""TestX deterministic tie-break ordering checks for worldgen candidate ranking."""

from __future__ import annotations

import sys


TEST_ID = "testx.worldgen.tie_break_determinism"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from worldgen.core.constraint_solver import _rank_candidates

    candidates = [
        {
            "seed": "bb00",
            "seed_order": 1,
            "soft_score": 100,
            "hard_pass_count": 2,
            "metrics": {"metric.tie": 12},
        },
        {
            "seed": "aa00",
            "seed_order": 0,
            "soft_score": 100,
            "hard_pass_count": 2,
            "metrics": {"metric.tie": 12},
        },
    ]

    lexicographic = _rank_candidates(
        [dict(row) for row in candidates],
        tie_break_policy="lexicographic",
        tie_break_field="metric.tie",
    )
    if [row.get("seed") for row in lexicographic] != ["aa00", "bb00"]:
        return {"status": "fail", "message": "lexicographic tie-break ordering mismatch"}

    seed_order = _rank_candidates(
        [dict(row) for row in candidates],
        tie_break_policy="seed_order",
        tie_break_field="metric.tie",
    )
    if [row.get("seed") for row in seed_order] != ["aa00", "bb00"]:
        return {"status": "fail", "message": "seed_order tie-break ordering mismatch"}

    explicit_field = _rank_candidates(
        [
            {
                "seed": "bb00",
                "seed_order": 1,
                "soft_score": 100,
                "hard_pass_count": 2,
                "metrics": {"metric.tie": 99},
            },
            {
                "seed": "aa00",
                "seed_order": 0,
                "soft_score": 100,
                "hard_pass_count": 2,
                "metrics": {"metric.tie": 11},
            },
        ],
        tie_break_policy="explicit_field",
        tie_break_field="metric.tie",
    )
    if [row.get("seed") for row in explicit_field] != ["bb00", "aa00"]:
        return {"status": "fail", "message": "explicit_field tie-break ordering mismatch"}

    return {"status": "pass", "message": "tie-break deterministic ordering passed"}

