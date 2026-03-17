"""Shared RELEASE-INDEX-POLICY-0 TestX helpers."""

from __future__ import annotations

import os

from tools.release.release_index_policy_common import (
    REPORT_JSON_REL,
    build_release_index_policy_fixture_cases,
    build_release_index_policy_report,
    release_index_policy_violations,
    write_release_index_policy_outputs,
)


def ensure_assets(repo_root: str, *, platform_tag: str = "win64") -> None:
    if os.path.isfile(report_json_path(repo_root)):
        return
    write_release_index_policy_outputs(
        os.path.abspath(repo_root),
        platform_tag=platform_tag,
        write_registry=True,
    )


def build_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return build_release_index_policy_report(os.path.abspath(repo_root), platform_tag=platform_tag)


def build_fixture_cases(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root, platform_tag=platform_tag)
    return build_release_index_policy_fixture_cases(os.path.abspath(repo_root), platform_tag=platform_tag)


def current_violations(repo_root: str) -> list[dict]:
    ensure_assets(repo_root)
    return release_index_policy_violations(os.path.abspath(repo_root))


def report_json_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))


__all__ = [
    "build_fixture_cases",
    "build_report",
    "current_violations",
    "ensure_assets",
    "report_json_path",
]
