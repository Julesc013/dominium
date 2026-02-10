#!/usr/bin/env python3
"""Canonical tool-path helpers shared by RepoX/TestX/dev wrappers."""

import os
import platform
import shutil


CANONICAL_TOOL_IDS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)


def _norm(path):
    return os.path.normpath(path)


def _norm_case(path):
    return os.path.normcase(_norm(path))


def _looks_like_repo_root(path):
    return (
        os.path.isfile(os.path.join(path, "CMakeLists.txt"))
        and os.path.isdir(os.path.join(path, "scripts"))
        and os.path.isdir(os.path.join(path, "docs"))
    )


def _ascend_candidates(start):
    current = _norm(os.path.abspath(start))
    while True:
        yield current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent


def detect_repo_root(cwd, exe_path):
    """Resolve repository root from cwd and script/exe location."""

    search_roots = []
    if cwd:
        search_roots.append(cwd)
    if exe_path:
        search_roots.append(os.path.dirname(exe_path))

    seen = set()
    for root in search_roots:
        for candidate in _ascend_candidates(root):
            norm = _norm_case(candidate)
            if norm in seen:
                continue
            seen.add(norm)
            if _looks_like_repo_root(candidate):
                return _norm(os.path.abspath(candidate))
    raise RuntimeError("refuse.repo_root_unresolved")


def detect_platform_arch():
    """Return canonical host platform id and preferred arch ids."""

    sys_name = platform.system().lower()
    if sys_name.startswith("win"):
        platform_id = "winnt"
    elif sys_name == "linux":
        platform_id = "linux"
    elif sys_name == "darwin":
        platform_id = "macosx"
    else:
        raise RuntimeError("refuse.platform_unsupported: {}".format(sys_name))

    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        arch_candidates = ["x64", "x86_64"]
    elif machine in ("x86", "i386", "i686"):
        arch_candidates = ["x86", "x86_32"]
    elif machine in ("arm64", "aarch64"):
        arch_candidates = ["arm64"]
    elif machine.startswith("arm"):
        arch_candidates = ["arm", "arm32"]
    else:
        arch_candidates = [machine]

    return platform_id, arch_candidates


def canonical_tools_dir_details(repo_root, platform_id="", arch_id=""):
    repo_root = _norm(os.path.abspath(repo_root))
    host_platform, host_arches = detect_platform_arch()
    use_platform = platform_id or host_platform
    candidates = [arch_id] if arch_id else list(host_arches)
    candidates = [item for item in candidates if item]
    if not candidates:
        candidates = ["x64"]

    for arch in candidates:
        candidate = _norm(
            os.path.join(repo_root, "dist", "sys", use_platform, arch, "bin", "tools")
        )
        if os.path.isdir(candidate):
            return candidate, use_platform, arch, list(candidates)

    fallback_arch = candidates[0]
    fallback = _norm(
        os.path.join(repo_root, "dist", "sys", use_platform, fallback_arch, "bin", "tools")
    )
    return fallback, use_platform, fallback_arch, list(candidates)


def canonical_tools_dir(repo_root, platform_id="", arch_id=""):
    return canonical_tools_dir_details(repo_root, platform_id, arch_id)[0]


def default_host_path():
    if os.name == "nt":
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        candidates = [
            os.path.join(system_root, "System32"),
            system_root,
            os.path.join(system_root, "System32", "Wbem"),
            os.path.join(system_root, "System32", "WindowsPowerShell", "v1.0"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Git", "cmd"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Git", "bin"),
            os.path.join(os.environ.get("ProgramW6432", ""), "Git", "cmd"),
            os.path.join(os.environ.get("ProgramW6432", ""), "Git", "bin"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Git", "cmd"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Git", "bin"),
            os.path.join(os.environ.get("ProgramFiles", ""), "CMake", "bin"),
            os.path.join(os.environ.get("ProgramW6432", ""), "CMake", "bin"),
            os.path.join(os.environ.get("LocalAppData", ""), "Microsoft", "WindowsApps"),
        ]
    else:
        candidates = [
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
        ]
    valid = []
    seen = set()
    for item in candidates:
        if not item:
            continue
        norm = _norm(item)
        key = _norm_case(norm)
        if key in seen:
            continue
        seen.add(key)
        if os.path.isdir(norm):
            valid.append(norm)
    return os.pathsep.join(valid)


def prepend_tools_to_path(env, tools_dir):
    out = dict(env or {})
    existing = out.get("PATH", "")
    items = [item for item in existing.split(os.pathsep) if item]
    norm_tools = _norm_case(tools_dir)
    dedup = []
    seen = set()
    for item in items:
        norm_item = _norm_case(item)
        if norm_item in seen or norm_item == norm_tools:
            continue
        seen.add(norm_item)
        dedup.append(item)
    out["PATH"] = os.pathsep.join([tools_dir] + dedup)
    out["DOM_TOOLS_PATH"] = tools_dir
    out["DOM_TOOLS_READY"] = "1"
    return out


def resolve_tool(name, env):
    env_map = env or {}
    path_value = env_map.get("PATH", "")
    found = shutil.which(name, path=path_value)
    if found:
        return _norm(found)

    if os.name != "nt":
        return ""

    base, ext = os.path.splitext(name)
    if ext:
        return ""
    pathext = env_map.get("PATHEXT") or os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    for suffix in pathext.split(os.pathsep if os.pathsep == ";" else ";"):
        suffix = suffix.strip()
        if not suffix:
            continue
        probe = shutil.which(name + suffix.lower(), path=path_value) or shutil.which(
            name + suffix.upper(), path=path_value
        )
        if probe:
            return _norm(probe)
    return ""
