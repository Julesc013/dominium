"""STRICT test: INT-3 interior instruments stay perceived/diegetic-only."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.interior.no_truth_access_in_instruments"
TEST_TAGS = ["strict", "interior", "diegetics", "epistemic"]


FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state|registry_payloads)\b", re.IGNORECASE)
KERNEL_TARGET = "diegetics/instrument_kernel.py"
OBSERVATION_TARGET = "tools/xstack/sessionx/observation.py"
OBS_FORBIDDEN_TOKENS = (
    "compartment_states",
    "portal_flow_params",
    "interior_leak_hazards",
)
OBS_REQUIRED_TOKENS = (
    "ch.diegetic.pressure_status",
    "ch.diegetic.oxygen_status",
    "ch.diegetic.smoke_alarm",
    "ch.diegetic.flood_alarm",
    "ch.diegetic.door_indicator",
)


def _read(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    kernel_abs = os.path.join(repo_root, KERNEL_TARGET.replace("/", os.sep))
    if not os.path.isfile(kernel_abs):
        return {"status": "fail", "message": "missing required diegetic kernel {}".format(KERNEL_TARGET)}
    kernel_text = _read(repo_root, KERNEL_TARGET)
    for line_no, line in enumerate(kernel_text.splitlines(), start=1):
        if FORBIDDEN_PATTERN.search(str(line)):
            return {
                "status": "fail",
                "message": "forbidden truth token found in {}:{} ({})".format(KERNEL_TARGET, line_no, str(line).strip()),
            }

    observation_text = _read(repo_root, OBSERVATION_TARGET)
    for token in OBS_FORBIDDEN_TOKENS:
        if token in observation_text:
            return {
                "status": "fail",
                "message": "observation contains forbidden interior truth token '{}'".format(token),
            }
    for token in OBS_REQUIRED_TOKENS:
        if token not in observation_text:
            return {
                "status": "fail",
                "message": "observation missing required INT-3 diegetic channel token '{}'".format(token),
            }

    return {"status": "pass", "message": "interior instruments remain diegetic/perceived-only"}

