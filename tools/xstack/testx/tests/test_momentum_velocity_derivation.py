"""FAST test alias: velocity derivation must remain momentum-based in ROI free motion."""

from __future__ import annotations


TEST_ID = "test_momentum_velocity_derivation"
TEST_TAGS = ["fast", "physics", "mobility", "momentum"]


def run(repo_root: str):
    from tools.xstack.testx.tests import test_velocity_derived_from_momentum

    return dict(test_velocity_derived_from_momentum.run(repo_root))
