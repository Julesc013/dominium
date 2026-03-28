"""FAST test: runtime compile helper supports deep target roots."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_runtime_compile_helper_supports_deep_target_root"
TEST_TAGS = ["fast", "dist", "windows", "regression"]


def run(repo_root: str):
    from tools.dist.runtime_compile_helper import _compile_runtime_tree, _fs_path

    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dist_runtime_helper_", dir=temp_parent) as temp_root:
        source_root = os.path.join(temp_root, "source")
        os.makedirs(os.path.join(source_root, "pkg", "nested"), exist_ok=True)
        with open(os.path.join(source_root, "pkg", "__init__.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("VALUE = 1\n")
        with open(os.path.join(source_root, "pkg", "nested", "tool.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("def meaning() -> int:\n    return 42\n")

        deep_root = os.path.join(
            temp_root,
            *["deep_target_segment_{:02d}".format(index) for index in range(16)],
            "bundle",
        )
        report = _compile_runtime_tree(
            source_root,
            deep_root,
            runtime_roots=("pkg",),
            excluded_prefixes=(),
            excluded_basenames=set(),
            excluded_files=set(),
        )
        expected = ["pkg/__init__.pyc", "pkg/nested/tool.pyc"]
        if list(report.get("compiled_files") or []) != expected:
            return {
                "status": "fail",
                "message": "runtime compile helper produced an unexpected compiled file list",
            }
        compiled_abs = os.path.join(deep_root, "pkg", "nested", "tool.pyc")
        if not os.path.isfile(_fs_path(compiled_abs)):
            return {
                "status": "fail",
                "message": "runtime compile helper did not materialize bytecode under the deep target root",
            }
    return {"status": "pass", "message": "runtime compile helper supports deep target roots"}
