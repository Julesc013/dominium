"""FAST test: congestion multiplier function is deterministic and policy-driven."""

from __future__ import annotations

import sys

TEST_ID = "testx.mobility.traffic.congestion_multiplier"
TEST_TAGS = ["fast", "mobility", "traffic", "congestion", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mobility.traffic import apply_congestion_to_speed

    policy = {
        "congestion_policy_id": "cong.default_linear",
        "extensions": {"parameters": {"k_per_over_ratio_permille": 500}},
    }
    nominal = apply_congestion_to_speed(
        base_speed_mm_per_tick=1000,
        congestion_ratio_permille=1000,
        congestion_policy_row=policy,
    )
    nominal_repeat = apply_congestion_to_speed(
        base_speed_mm_per_tick=1000,
        congestion_ratio_permille=1000,
        congestion_policy_row=policy,
    )
    overloaded = apply_congestion_to_speed(
        base_speed_mm_per_tick=1000,
        congestion_ratio_permille=2000,
        congestion_policy_row=policy,
    )
    overloaded_repeat = apply_congestion_to_speed(
        base_speed_mm_per_tick=1000,
        congestion_ratio_permille=2000,
        congestion_policy_row=policy,
    )

    if nominal != nominal_repeat or overloaded != overloaded_repeat:
        return {"status": "fail", "message": "congestion speed adjustment drifted across equivalent calls"}
    if int(nominal.get("multiplier_permille", -1)) != 1000:
        return {"status": "fail", "message": "expected multiplier 1000 at or below capacity"}
    if int(overloaded.get("multiplier_permille", -1)) != 1500:
        return {"status": "fail", "message": "expected multiplier 1500 for ratio=2000 and k=500 permille"}
    if int(overloaded.get("adjusted_speed_mm_per_tick", -1)) != 666:
        return {"status": "fail", "message": "expected adjusted speed floor(1000*1000/1500)=666"}
    return {"status": "pass", "message": "congestion multiplier deterministic and policy-consistent"}

