"""Shared COMPONENT-GRAPH-0 TestX helpers."""

from __future__ import annotations

import json
import os

from release import (
    DEFAULT_COMPONENT_GRAPH_ID,
    build_default_component_install_plan,
    platform_targets_for_tag,
    select_component_graph,
)
from tools.release.component_graph_common import (
    ARCH_REGISTRY_REL,
    GRAPH_REGISTRY_REL,
    OS_REGISTRY_REL,
    build_component_graph_report,
    component_graph_violations,
    write_component_graph_outputs,
)


def _required_paths(repo_root: str) -> tuple[str, ...]:
    root = os.path.abspath(repo_root)
    return tuple(
        os.path.join(root, rel_path.replace("/", os.sep))
        for rel_path in (
            ARCH_REGISTRY_REL,
            OS_REGISTRY_REL,
            GRAPH_REGISTRY_REL,
        )
    )


def ensure_assets(repo_root: str) -> None:
    if all(os.path.isfile(path) for path in _required_paths(repo_root)):
        return
    write_component_graph_outputs(repo_root, write_registries=True)


def load_graph_registry(repo_root: str) -> dict:
    ensure_assets(repo_root)
    with open(os.path.join(os.path.abspath(repo_root), GRAPH_REGISTRY_REL.replace("/", os.sep)), "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_graph(repo_root: str) -> dict:
    return select_component_graph(load_graph_registry(repo_root), graph_id=DEFAULT_COMPONENT_GRAPH_ID)


def build_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root)
    return build_component_graph_report(repo_root, platform_tag=platform_tag)


def load_default_plan(repo_root: str, *, platform_tag: str = "win64") -> dict:
    ensure_assets(repo_root)
    target = platform_targets_for_tag(platform_tag)
    return build_default_component_install_plan(
        repo_root,
        target_platform=str(target.get("platform_id", "")).strip(),
        target_arch=str(target.get("arch_id", "")).strip(),
        target_abi=str(target.get("abi_id", "")).strip(),
    )


def current_violations(repo_root: str) -> list[dict]:
    ensure_assets(repo_root)
    return component_graph_violations(repo_root)


__all__ = [
    "build_report",
    "current_violations",
    "ensure_assets",
    "load_default_plan",
    "load_graph",
    "load_graph_registry",
]
