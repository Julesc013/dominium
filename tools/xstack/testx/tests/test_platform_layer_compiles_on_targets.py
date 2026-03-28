"""STRICT test: platform abstraction layer compiles and resolves deterministic target IDs."""

from __future__ import annotations

import os
import py_compile
import sys


TEST_ID = "testx.render.platform_layer_compiles_on_targets"
TEST_TAGS = ["strict", "render", "platform"]

TARGET_FILES = (
    "engine/platform/__init__.py",
    "engine/platform/platform_window.py",
    "engine/platform/platform_input.py",
    "engine/platform/platform_gfx.py",
    "engine/platform/platform_audio.py",
    "engine/platform/platform_input_routing.py",
)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    for rel_path in TARGET_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "missing platform abstraction file: {}".format(rel_path)}
        try:
            py_compile.compile(abs_path, doraise=True)
        except py_compile.PyCompileError:
            return {"status": "fail", "message": "platform abstraction file does not compile: {}".format(rel_path)}

    from engine.platform.platform_gfx import list_available_backends
    from engine.platform.platform_window import detect_platform_id

    for token in ("windows", "macos", "linux"):
        resolved = detect_platform_id(token)
        if resolved != token:
            return {
                "status": "fail",
                "message": "detect_platform_id mismatch for {} (got {})".format(token, resolved),
            }
        backends = list_available_backends(platform_id=token, backend_policy={})
        if "null" not in backends or "software" not in backends:
            return {
                "status": "fail",
                "message": "required portable backends missing for {}".format(token),
            }

    return {
        "status": "pass",
        "message": "platform abstraction files compile and resolve deterministic target backend sets",
    }
