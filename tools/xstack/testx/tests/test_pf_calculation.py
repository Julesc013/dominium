"""FAST test: deterministic PF helper computes expected permille values."""

from __future__ import annotations

import sys


TEST_ID = "test_pf_calculation"
TEST_TAGS = ["fast", "electric", "pf"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.electric.power_network_engine import compute_pf_permille

    if int(compute_pf_permille(active_p=80, apparent_s=100)) != 800:
        return {"status": "fail", "message": "expected PF=800 permille for P=80,S=100"}
    if int(compute_pf_permille(active_p=0, apparent_s=0)) != 1000:
        return {"status": "fail", "message": "expected PF=1000 permille fallback when apparent power is zero"}
    if int(compute_pf_permille(active_p=150, apparent_s=120)) != 1000:
        return {"status": "fail", "message": "PF helper must clamp to 1000 permille"}
    return {"status": "pass", "message": "PF helper deterministic and clamped"}

