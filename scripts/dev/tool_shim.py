#!/usr/bin/env python3
"""Repo-local shim that resolves canonical tool binaries by name."""

import os
import subprocess
import sys

from env_tools_lib import canonical_tools_dir_details, detect_repo_root


def _normalize(path):
    return os.path.normpath(os.path.abspath(path))


def _resolve_repo_root():
    explicit = os.environ.get("DOM_REPO_ROOT", "").strip()
    if explicit:
        return _normalize(explicit)
    return detect_repo_root(os.getcwd(), __file__)


def _resolve_tool_binary(repo_root, tool_name):
    tools_dir, platform_id, arch_id, arch_candidates = canonical_tools_dir_details(repo_root)
    suffix = ".exe" if os.name == "nt" else ""
    candidates = []
    if suffix:
        candidates.append(os.path.join(tools_dir, tool_name + suffix))
    candidates.append(os.path.join(tools_dir, tool_name))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate, tools_dir
    hint = (
        "refuse.tool_missing: {} not found under {} "
        "(platform={}, arch={}, candidates={}); build ui_bind_phase/tools target"
    ).format(
        tool_name,
        tools_dir.replace("\\", "/"),
        platform_id,
        arch_id,
        ",".join(arch_candidates),
    )
    raise RuntimeError(hint)


def main(argv):
    if len(argv) < 2:
        print("refuse.tool_name_missing: expected canonical tool id", file=sys.stderr)
        return 2

    tool_name = argv[1].strip()
    forward_args = argv[2:]
    if not tool_name:
        print("refuse.tool_name_missing: empty canonical tool id", file=sys.stderr)
        return 2

    try:
        repo_root = _resolve_repo_root()
        tool_binary, tools_dir = _resolve_tool_binary(repo_root, tool_name)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    env = dict(os.environ)
    path_items = [tools_dir]
    existing_path = env.get("PATH", "")
    if existing_path:
        path_items.append(existing_path)
    env["PATH"] = os.pathsep.join(path_items)
    env["DOM_TOOLS_PATH"] = tools_dir
    env["DOM_TOOLS_READY"] = "1"

    try:
        result = subprocess.run([tool_binary] + forward_args, env=env, check=False)
    except OSError as exc:
        print("refuse.tool_exec_failed: {} ({})".format(tool_name, exc), file=sys.stderr)
        return 2
    return int(result.returncode)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
