"""STRICT test: renderer pipeline files must remain truth/process isolated."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.render.renderer_truth_isolation"
TEST_TAGS = ["strict", "render", "repox"]

TARGETS = (
    "runtime/render/backend/render_model_adapter.py",
    "runtime/render/backend/representation_resolver.py",
    "runtime/render/backend/snapshot_capture.py",
    "runtime/render/providers/null/null_renderer.py",
    "runtime/render/providers/software/software_renderer.py",
    "runtime/render/backend/hw_renderer_gl.py",
    "tools/validators/render/tool_render_capture.py",
    "tools/validators/render/render_cli.py",
)
FORBIDDEN = re.compile(r"\b(truth_model|truthmodel|universe_state|process_runtime)\b", re.IGNORECASE)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    for rel_path in TARGETS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "renderer boundary file missing: {}".format(rel_path)}
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            return {"status": "fail", "message": "unable to read renderer boundary file: {}".format(rel_path)}
        for line_no, line in enumerate(lines, start=1):
            if FORBIDDEN.search(str(line).strip()):
                return {"status": "fail", "message": "forbidden truth/process symbol in {}:{}".format(rel_path, line_no)}
    return {"status": "pass", "message": "renderer files remain truth/process isolated"}
