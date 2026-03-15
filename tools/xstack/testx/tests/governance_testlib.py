"""Shared GOVERNANCE-0 TestX helpers."""

from __future__ import annotations

import os

from src.governance import governance_profile_hash, load_governance_profile, parse_release_tag
from src.release import DEFAULT_RELEASE_INDEX_REL, load_release_index
from tools.governance.governance_model_common import REPORT_JSON_REL, build_governance_model_report, write_governance_outputs


def ensure_assets(repo_root: str, *, platform_tag: str = "win64") -> None:
    write_governance_outputs(repo_root, platform_tag=platform_tag)


def load_profile(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return load_governance_profile(repo_root)


def bundle_root(repo_root: str, *, platform_tag: str = "win64") -> str:
    root = os.path.abspath(repo_root)
    candidates = [
        os.path.join(root, "dist", "v0.0.0-mock", platform_tag, "dominium"),
        os.path.join(root, "build", "tmp", "governance_model_dist", "v0.0.0-mock", platform_tag, "dominium"),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, DEFAULT_RELEASE_INDEX_REL)):
            return candidate
    return candidates[-1]


def load_release_index_payload(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return load_release_index(os.path.join(bundle_root(repo_root, platform_tag=platform_tag), DEFAULT_RELEASE_INDEX_REL))


def build_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return build_governance_model_report(repo_root, platform_tag=platform_tag)


def report_json_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))


def parse_tag(tag: str) -> dict:
    return parse_release_tag(tag)


def current_governance_hash(repo_root: str) -> str:
    return governance_profile_hash(load_profile(repo_root))


__all__ = [
    "build_report",
    "bundle_root",
    "current_governance_hash",
    "ensure_assets",
    "load_profile",
    "load_release_index_payload",
    "parse_tag",
    "report_json_path",
]
