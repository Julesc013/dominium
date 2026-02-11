"""Workspace isolation manager for ControlX."""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict

from env_tools_lib import (
    canonical_workspace_id,
    canonical_workspace_dirs,
    canonicalize_env_for_workspace,
    sanitize_workspace_id,
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def compute_workspace_id(repo_root: str, prompt_hash: str, index: int, workspace_seed: str = "") -> str:
    seed = sanitize_workspace_id(workspace_seed)
    if not seed:
        seed = canonical_workspace_id(repo_root, env=os.environ)
    suffix = "{}{:02d}".format(prompt_hash[:6], max(index, 0))
    candidate = sanitize_workspace_id("{}-cx-{}".format(seed, suffix))
    if candidate:
        return candidate[:64]
    fallback = "controlx-" + _sha256_text(repo_root + prompt_hash + str(index))[:16]
    return sanitize_workspace_id(fallback)[:64]


def prepare_workspace(repo_root: str, prompt_hash: str, index: int, workspace_seed: str = "") -> Dict[str, Any]:
    ws_id = compute_workspace_id(repo_root, prompt_hash, index, workspace_seed=workspace_seed)
    env, ws_dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)
    dirs = canonical_workspace_dirs(repo_root, ws_id=ws_id, platform_id=ws_dirs.get("platform", ""), arch_id=ws_dirs.get("arch", ""))
    for key in ("build_root", "build_verify", "dist_root"):
        path = dirs.get(key, "")
        if path and not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
    return {
        "workspace_id": ws_id,
        "env": env,
        "dirs": dirs,
    }


def allowed_mutation_path(repo_root: str, workspace: Dict[str, Any], path: str) -> bool:
    target = os.path.normpath(os.path.abspath(path))
    dirs = workspace.get("dirs", {}) if isinstance(workspace, dict) else {}
    allowed_roots = [
        os.path.normpath(os.path.abspath(os.path.join(repo_root, "docs"))),
        os.path.normpath(os.path.abspath(os.path.join(repo_root, "schema"))),
        os.path.normpath(os.path.abspath(os.path.join(repo_root, "data"))),
    ]
    for key in ("build_root", "dist_root"):
        value = dirs.get(key, "")
        if value:
            allowed_roots.append(os.path.normpath(os.path.abspath(value)))
    for root in allowed_roots:
        if target == root or target.startswith(root + os.sep):
            return True
    return False

