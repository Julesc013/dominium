"""STRICT test: render adapter/resolver path must not reference TruthModel symbols."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.render.no_truth_access"
TEST_TAGS = ["strict", "render", "representation", "repox"]

TARGETS = (
    "client/render/render_model_adapter.py",
    "client/render/representation_resolver.py",
    "tools/xstack/sessionx/render_model.py",
)
FORBIDDEN = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    for rel_path in TARGETS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "render contract file missing: {}".format(rel_path)}
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            return {"status": "fail", "message": "unable to read render contract file: {}".format(rel_path)}
        for line_no, line in enumerate(lines, start=1):
            if FORBIDDEN.search(str(line).strip()):
                return {
                    "status": "fail",
                    "message": "forbidden truth symbol in {}:{}".format(rel_path, line_no),
                }
    return {"status": "pass", "message": "render adapter/resolver path stays truth-isolated"}
