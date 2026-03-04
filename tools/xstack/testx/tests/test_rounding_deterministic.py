"""FAST test: deterministic rounding helpers are stable and repeatable."""

from __future__ import annotations

import sys


TEST_ID = "test_rounding_deterministic"
TEST_TAGS = ["fast", "meta", "numeric", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.numeric import deterministic_divide, deterministic_mul_div

    sample_ops = [
        (17, 3, "truncate"),
        (17, 3, "round_half_to_even"),
        (-17, 3, "truncate"),
        (-17, 3, "floor"),
        (25, 4, "ceiling"),
        (25, 4, "round_half_to_even"),
    ]
    pass_one = [int(deterministic_divide(num, den, rounding_mode=mode)) for num, den, mode in sample_ops]
    pass_two = [int(deterministic_divide(num, den, rounding_mode=mode)) for num, den, mode in sample_ops]
    if pass_one != pass_two:
        return {"status": "fail", "message": "deterministic_divide produced inconsistent results across repeated calls"}

    load_one = []
    load_two = []
    for _ in range(2):
        values = []
        value = 123456
        for _tick in range(8192):
            value = int(deterministic_mul_div(value + 7, 997, 1000, rounding_mode="round_half_to_even"))
            value = int(deterministic_mul_div(value, 1000, 997, rounding_mode="round_half_to_even"))
            values.append(value)
        if not load_one:
            load_one = values
        else:
            load_two = values
    if load_one != load_two:
        return {"status": "fail", "message": "deterministic_mul_div load sequence diverged across repeated runs"}
    return {"status": "pass", "message": "deterministic rounding helpers are repeatable under load"}
