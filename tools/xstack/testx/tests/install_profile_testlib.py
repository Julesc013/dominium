"""Shared DIST-REFINE-1 TestX helpers."""

from __future__ import annotations

import json
import os

from src.release import (
    DEFAULT_INSTALL_PROFILE_ID,
    build_default_component_install_plan,
    platform_targets_for_tag,
    select_install_profile,
)
from tools.release.install_profile_common import REGISTRY_REL, build_install_profile_report, install_profile_violations, write_install_profile_outputs


def _registry_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REGISTRY_REL.replace("/", os.sep))


def ensure_assets(repo_root: str) -> None:
    if os.path.isfile(_registry_path(repo_root)):
        return
    write_install_profile_outputs(repo_root, write_registry=True)


def load_registry(repo_root: str) -> dict:
    ensure_assets(repo_root)
    with open(_registry_path(repo_root), "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_profile(repo_root: str, install_profile_id: str) -> dict:
    return select_install_profile(load_registry(repo_root), install_profile_id=install_profile_id)


def build_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root)
    return build_install_profile_report(repo_root, platform_tag=platform_tag)


def resolve_profile(repo_root: str, install_profile_id: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root)
    target = platform_targets_for_tag(platform_tag)
    return build_default_component_install_plan(
        repo_root,
        install_profile_id=install_profile_id or DEFAULT_INSTALL_PROFILE_ID,
        target_platform=str(target.get("platform_id", "")).strip(),
        target_arch=str(target.get("arch_id", "")).strip(),
        target_abi=str(target.get("abi_id", "")).strip(),
    )


def current_violations(repo_root: str) -> list[dict]:
    ensure_assets(repo_root)
    return install_profile_violations(repo_root)


__all__ = [
    "build_report",
    "current_violations",
    "ensure_assets",
    "load_profile",
    "load_registry",
    "resolve_profile",
]
