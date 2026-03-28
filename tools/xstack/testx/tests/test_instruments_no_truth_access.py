"""STRICT test: diegetic instrument kernel remains Perceived-only (no TruthModel access)."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.diegetics.instruments_no_truth_access"
TEST_TAGS = ["strict", "diegetics", "repox", "observation"]


FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state|registry_payloads)\b", re.IGNORECASE)
TARGETS = (
    "diegetics/instrument_kernel.py",
)


def _read(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    for rel_path in TARGETS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "missing required instrument target {}".format(rel_path)}
        text = _read(repo_root, rel_path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if FORBIDDEN_PATTERN.search(str(line)):
                return {
                    "status": "fail",
                    "message": "forbidden truth token found in {}:{} ({})".format(rel_path, line_no, str(line).strip()),
                }

    observation_text = _read(repo_root, "tools/xstack/sessionx/observation.py")
    required_tokens = (
        "compute_diegetic_instruments(",
        "perceived_now=perceived_model",
        "memory_store=memory_block",
    )
    for token in required_tokens:
        if token not in observation_text:
            return {"status": "fail", "message": "observation kernel missing required diegetic integration token '{}'".format(token)}

    return {"status": "pass", "message": "diegetic instrument kernel remains perceived-only"}

