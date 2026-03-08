"""STRICT test: GEO-5 projection adapters must not query truth directly."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "test_cli_adapter_no_truth_queries"
TEST_TAGS = ["strict", "geo", "projection", "ui"]

TARGET_FILE = "src/geo/projection/view_adapters.py"
FORBIDDEN = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    abs_path = os.path.join(repo_root, TARGET_FILE.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {"status": "fail", "message": "projection view adapter file missing"}
    try:
        text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return {"status": "fail", "message": "unable to read projection view adapter file"}
    if "render_projected_view_ascii(" not in text or "build_projected_view_layer_buffers(" not in text:
        return {"status": "fail", "message": "projection view adapter helpers missing from GEO-5 adapter file"}
    for line_no, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN.search(str(line).strip()):
            return {
                "status": "fail",
                "message": "forbidden truth symbol in {}:{}".format(TARGET_FILE, line_no),
            }
    return {"status": "pass", "message": "GEO-5 projection adapters remain truth-isolated"}
