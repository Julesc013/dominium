"""Utility helpers for TestX tool-suite tests."""

from __future__ import annotations

import os
import shutil
import tempfile


def make_temp_repo_with_test_packs(source_repo_root: str) -> str:
    temp_root = tempfile.mkdtemp(prefix="xstack_testx_fixture_")
    src_packs = os.path.join(source_repo_root, "tools", "xstack", "testdata", "packs")
    dst_packs = os.path.join(temp_root, "packs")
    shutil.copytree(src_packs, dst_packs)
    src_bundles = os.path.join(source_repo_root, "tools", "xstack", "testdata", "bundles")
    dst_bundles = os.path.join(temp_root, "bundles")
    shutil.copytree(src_bundles, dst_bundles)
    return temp_root
