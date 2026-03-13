"""Shared DIST-1 portable bundle TestX helpers."""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager

from src.release import verify_release_manifest
from tools.dist.dist_tree_common import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_PLATFORM_TAG,
    DEFAULT_RELEASE_CHANNEL,
    build_dist_minimize_report,
    build_dist_tree,
)


DEFAULT_BUNDLE_REL = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "v0.0.0-{}".format(DEFAULT_RELEASE_CHANNEL),
    DEFAULT_PLATFORM_TAG,
    "dominium",
)

REQUIRED_LAYOUT = (
    "install.manifest.json",
    "manifests/filelist.txt",
    "manifests/release_manifest.json",
    "bin/engine",
    "bin/game",
    "bin/client",
    "bin/server",
    "bin/setup",
    "bin/launcher",
    "store/store.root.json",
    "store/locks/pack_lock.mvp_default.json",
    "store/profiles/bundles/bundle.mvp_default.json",
    "instances/default/instance.manifest.json",
    "docs/COMPATIBILITY.md",
    "docs/RELEASE_NOTES_v0_0_0_mock.md",
    "README",
    "LICENSE",
)


def bundle_root(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), DEFAULT_BUNDLE_REL.replace("/", os.sep))


def filelist_text(root: str) -> str:
    with open(os.path.join(root, "manifests", "filelist.txt"), "r", encoding="utf-8") as handle:
        return handle.read()


def release_manifest_verification(repo_root: str) -> dict:
    root = bundle_root(repo_root)
    manifest_path = os.path.join(root, "manifests", "release_manifest.json")
    return verify_release_manifest(root, manifest_path, repo_root=repo_root)


def minimize_report(repo_root: str) -> dict:
    return build_dist_minimize_report(bundle_root(repo_root))


@contextmanager
def rebuilt_bundle(repo_root: str):
    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dominium_dist1_test_", dir=temp_parent) as temp_root:
        output_root = os.path.join(temp_root, "dist")
        report = build_dist_tree(
            repo_root,
            platform_tag=DEFAULT_PLATFORM_TAG,
            channel_id=DEFAULT_RELEASE_CHANNEL,
            output_root=output_root,
        )
        yield report
