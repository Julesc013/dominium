"""FAST test: THERM loss-to-heat convention document exists and includes required contract tokens."""

from __future__ import annotations

import os


TEST_ID = "test_loss_to_heat_convention_doc_present"
TEST_TAGS = ["fast", "thermal", "docs", "governance"]


_REQUIRED_TOKENS = (
    "quantity.heat_loss",
    "effect.temperature_increase_local",
    "INV-LOSS-MAPPED-TO-HEAT",
)


def run(repo_root: str):
    rel_path = "docs/thermal/LOSS_TO_HEAT_CONVENTION.md"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {"status": "fail", "message": "{} missing".format(rel_path)}
    try:
        text = open(abs_path, "r", encoding="utf-8").read()
    except OSError as exc:
        return {"status": "fail", "message": "failed reading {}: {}".format(rel_path, exc)}

    missing = [token for token in _REQUIRED_TOKENS if token not in text]
    if missing:
        return {"status": "fail", "message": "missing loss-to-heat contract tokens: {}".format(",".join(missing))}
    return {"status": "pass", "message": "loss-to-heat convention contract present"}

