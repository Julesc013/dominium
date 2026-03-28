"""STRICT test: renderer pipeline files must remain truth/process isolated."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "testx.render.renderer_truth_isolation"
TEST_TAGS = ["strict", "render", "repox"]

TARGETS = (
    "client/render/render_model_adapter.py",
    "client/render/representation_resolver.py",
    "client/render/snapshot_capture.py",
    "client/render/renderers/null_renderer.py",
    "client/render/renderers/software_renderer.py",
    "client/render/renderers/hw_renderer_gl.py",
    "tools/render/tool_render_capture.py",
    "tools/render/render_cli.py",
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
