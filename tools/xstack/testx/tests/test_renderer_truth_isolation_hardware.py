"""STRICT test: hardware renderer backend remains truth/process isolated."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.render.renderer_truth_isolation_hardware"
TEST_TAGS = ["strict", "render", "repox"]

TARGETS = (
    "client/render/renderers/hw_renderer_gl.py",
    "client/render/snapshot_capture.py",
)
FORBIDDEN = re.compile(r"\b(truth_model|truthmodel|universe_state|process_runtime|apply_intent)\b", re.IGNORECASE)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    for rel_path in TARGETS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "renderer backend file missing: {}".format(rel_path)}
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            return {"status": "fail", "message": "unable to read renderer backend file: {}".format(rel_path)}
        for line_no, line in enumerate(lines, start=1):
            if FORBIDDEN.search(str(line).strip()):
                return {
                    "status": "fail",
                    "message": "forbidden truth/process symbol in {}:{}".format(rel_path, line_no),
                }

    return {"status": "pass", "message": "hardware renderer backend remains truth/process isolated"}
