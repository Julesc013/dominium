"""Shared UPDATE-MODEL-0 TestX helpers."""

from __future__ import annotations

import json
import os

from src.release import (
    DEFAULT_INSTALL_PROFILE_ID,
    DEFAULT_RELEASE_INDEX_REL,
    load_release_index,
    resolve_update_plan,
)
from tools.dist.dist_tree_common import build_dist_tree
from tools.release.update_model_common import REPORT_JSON_REL, build_update_model_report, update_model_violations


def _bundle_root(repo_root: str, *, platform_tag: str = "win64") -> str:
    return os.path.join(
        os.path.abspath(repo_root),
        "build",
        "tmp",
        "update_model_test_dist",
        "v0.0.0-mock",
        platform_tag,
        "dominium",
    )


def ensure_assets(repo_root: str, *, platform_tag: str = "win64") -> None:
    bundle_root = _bundle_root(repo_root, platform_tag=platform_tag)
    manifest_path = os.path.join(bundle_root, "manifests", "release_manifest.json")
    if not os.path.isfile(manifest_path):
        build_dist_tree(
            repo_root,
            platform_tag=platform_tag,
            channel_id="mock",
            output_root=os.path.join(os.path.abspath(repo_root), "build", "tmp", "update_model_test_dist"),
            install_profile_id="install.profile.full",
        )
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL)
    if not os.path.isfile(release_index_path):
        build_update_model_report(
            repo_root,
            dist_root=bundle_root,
            platform_tag=platform_tag,
            write_release_index_file=True,
        )


def load_release_index_payload(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return load_release_index(os.path.join(_bundle_root(repo_root, platform_tag=platform_tag), DEFAULT_RELEASE_INDEX_REL))


def load_install_manifest(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    with open(os.path.join(_bundle_root(repo_root, platform_tag=platform_tag), "install.manifest.json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_plan(repo_root: str, *, platform_tag: str = "win64") -> dict:
    install_manifest = load_install_manifest(repo_root, platform_tag=platform_tag)
    release_index = load_release_index_payload(repo_root, platform_tag=platform_tag)
    install_profile_id = (
        str(dict(install_manifest.get("extensions") or {}).get("official.install_profile_id", "")).strip()
        or DEFAULT_INSTALL_PROFILE_ID
    )
    return resolve_update_plan(
        install_manifest,
        release_index,
        install_profile_id=install_profile_id,
        release_index_path=os.path.join(_bundle_root(repo_root, platform_tag=platform_tag), DEFAULT_RELEASE_INDEX_REL),
        component_graph=dict(dict(release_index.get("extensions") or {}).get("component_graph") or {}),
    )


def build_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return build_update_model_report(
        repo_root,
        dist_root=_bundle_root(repo_root, platform_tag=platform_tag),
        platform_tag=platform_tag,
        write_release_index_file=True,
    )


def current_violations(repo_root: str) -> list[dict]:
    ensure_assets(repo_root)
    return update_model_violations(repo_root)


def report_json_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))


__all__ = [
    "build_plan",
    "build_report",
    "current_violations",
    "ensure_assets",
    "load_install_manifest",
    "load_release_index_payload",
    "report_json_path",
]
