"""Shared DIST-3 clean-room TestX helpers."""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager

from tools.dist.clean_room_common import (
    DEFAULT_MODE_POLICY,
    DEFAULT_SEED,
    _scan_generated_outputs,
    build_clean_room_report,
    build_clean_room_step_plan,
    load_clean_room_report,
)
from tools.dist.dist_tree_common import DEFAULT_OUTPUT_ROOT, DEFAULT_PLATFORM_TAG, DEFAULT_RELEASE_CHANNEL


DEFAULT_BUNDLE_REL = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "v0.0.0-{}".format(DEFAULT_RELEASE_CHANNEL),
    DEFAULT_PLATFORM_TAG,
    "dominium",
)


def bundle_root(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), DEFAULT_BUNDLE_REL.replace("/", os.sep))


def load_report(repo_root: str) -> dict:
    report = load_clean_room_report(repo_root, platform_tag=DEFAULT_PLATFORM_TAG)
    if report:
        return report
    return build_clean_room_report(
        bundle_root(repo_root),
        repo_root=repo_root,
        platform_tag=DEFAULT_PLATFORM_TAG,
        seed=DEFAULT_SEED,
        mode_policy=DEFAULT_MODE_POLICY,
    )


def step_plan(seed: str = DEFAULT_SEED, mode_policy: str = DEFAULT_MODE_POLICY) -> list[dict]:
    return build_clean_room_step_plan(seed, mode_policy)


@contextmanager
def temp_bundle_fixture(repo_root: str):
    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dominium_dist3_test_", dir=temp_parent) as temp_root:
        copied_root = os.path.join(temp_root, "dominium")
        shutil.copytree(bundle_root(repo_root), copied_root)
        yield copied_root


def generated_output_hits(bundle_root_path: str) -> list[dict]:
    return _scan_generated_outputs(bundle_root_path)


__all__ = [
    "bundle_root",
    "generated_output_hits",
    "load_report",
    "step_plan",
    "temp_bundle_fixture",
]
