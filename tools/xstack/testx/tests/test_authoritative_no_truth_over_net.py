"""STRICT test: server-authoritative policy path does not serialize truth payload over net artifacts."""

from __future__ import annotations

import os
import re


TEST_ID = "testx.net.authoritative_no_truth_over_net"
TEST_TAGS = ["strict", "net", "repox"]


def run(repo_root: str):
    rel_path = "src/net/policies/policy_server_authoritative.py"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        text = open(abs_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "{} missing".format(rel_path)}

    required_tokens = (
        "observe_truth(",
        "schema_name=\"net_perceived_delta\"",
        "schema_name=\"net_snapshot\"",
    )
    for token in required_tokens:
        if token not in text:
            return {"status": "fail", "message": "authoritative policy missing required token '{}'".format(token)}

    forbidden_patterns = (
        r"send\([^\n]*(universe_state|truth_model)",
        r"(universe_state|truth_model)[^\n]*(socket|packet|wire|transport|payload_ref)",
        r"schema_name=\"net_delta\"",
    )
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        lower = str(line).lower()
        if "truth_snapshot_hash" in lower:
            continue
        for pattern in forbidden_patterns:
            if re.search(pattern, str(line), flags=re.IGNORECASE):
                return {
                    "status": "fail",
                    "message": "truth-over-net smell in authoritative policy at line {}".format(line_no),
                }

    return {"status": "pass", "message": "authoritative policy remains perceived-only over net transport artifacts"}
