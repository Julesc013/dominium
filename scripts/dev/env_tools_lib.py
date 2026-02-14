#!/usr/bin/env python3
"""Canonical workspace/tool helpers shared by RepoX/TestX/dev wrappers."""

import hashlib
import os
import platform
import re
import shutil
import subprocess


CANONICAL_TOOL_IDS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)

WORKSPACE_ID_ENV_KEY = "DOM_WS_ID"
LEGACY_WORKSPACE_ID = "vs2026"
WORKSPACE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def _norm(path):
    return os.path.normpath(path)


def _norm_case(path):
    return os.path.normcase(_norm(path))


def _slug(value):
    lowered = (value or "").strip().lower()
    out = []
    prev_dash = False
    for ch in lowered:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
            continue
        if ch in ("-", "_", "."):
            out.append(ch)
            prev_dash = False
            continue
        if not prev_dash:
            out.append("-")
            prev_dash = True
    slug = "".join(out).strip("-._")
    return slug


def sanitize_workspace_id(value):
    """Normalize user-provided workspace IDs into canonical deterministic IDs."""

    slug = _slug(value)
    if not slug:
        return ""
    if not WORKSPACE_ID_RE.match(slug):
        slug = slug[:64]
    return slug


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


def canonical_workspace_id(repo_root, env=None, platform_id="", arch_id=""):
    """Resolve deterministic workspace ID with optional explicit override."""

    env_map = dict(env or os.environ)
    explicit = sanitize_workspace_id(env_map.get(WORKSPACE_ID_ENV_KEY, ""))
    if explicit:
        return explicit

    repo_root = _norm(os.path.abspath(repo_root))
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
        head_sha = (proc.stdout or "").strip().lower() if int(proc.returncode) == 0 else "nogit"
    except OSError:
        head_sha = "nogit"
    seed = "{}|{}".format(repo_root.replace("\\", "/"), head_sha)
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return "ws-{}".format(digest)


def canonical_workspace_dirs(repo_root, ws_id="", platform_id="", arch_id=""):
    """Compute deterministic build/dist/remediation roots for a workspace."""

    repo_root = _norm(os.path.abspath(repo_root))
    host_platform, host_arches = detect_platform_arch()
    use_platform = platform_id or host_platform
    use_arch = arch_id or (host_arches[0] if host_arches else "x64")
    use_ws_id = sanitize_workspace_id(ws_id) or canonical_workspace_id(
        repo_root, platform_id=use_platform, arch_id=use_arch
    )

    build_root = _norm(os.path.join(repo_root, "out", "build", use_ws_id))
    dist_root = _norm(os.path.join(repo_root, "dist", "ws", use_ws_id))
    dist_sys_root = _norm(os.path.join(dist_root, "sys", use_platform, use_arch))
    dist_tools_root = _norm(os.path.join(dist_sys_root, "bin", "tools"))
    remediation_root = _norm(os.path.join(repo_root, "docs", "audit", "remediation", use_ws_id))

    legacy_build_root = _norm(os.path.join(repo_root, "out", "build", LEGACY_WORKSPACE_ID))
    legacy_verify = _norm(os.path.join(legacy_build_root, "verify"))
    shared_tools = _norm(os.path.join(repo_root, "dist", "sys", use_platform, use_arch, "bin", "tools"))

    return {
        "workspace_id": use_ws_id,
        "platform": use_platform,
        "arch": use_arch,
        "build_root": build_root,
        "build_verify": _norm(os.path.join(build_root, "verify")),
        "build_dev": _norm(os.path.join(build_root, "dev")),
        "dist_root": dist_root,
        "dist_sys_root": dist_sys_root,
        "dist_tools_root": dist_tools_root,
        "remediation_root": remediation_root,
        "legacy_build_root": legacy_build_root,
        "legacy_verify": legacy_verify,
        "shared_tools_root": shared_tools,
        "msvc_base": _norm(os.path.join(repo_root, "build", "msvc-base")),
    }


def canonical_tools_dir_details(repo_root, platform_id="", arch_id="", ws_id="", env=None):
    repo_root = _norm(os.path.abspath(repo_root))
    host_platform, host_arches = detect_platform_arch()
    use_platform = platform_id or host_platform
    candidates = [arch_id] if arch_id else list(host_arches)
    candidates = [item for item in candidates if item]
    if not candidates:
        candidates = ["x64"]

    chosen_ws = sanitize_workspace_id(ws_id) or canonical_workspace_id(
        repo_root, env=env, platform_id=use_platform, arch_id=candidates[0]
    )
    for arch in candidates:
        roots = canonical_workspace_dirs(repo_root, ws_id=chosen_ws, platform_id=use_platform, arch_id=arch)
        workspace_candidate = roots["dist_tools_root"]
        shared_candidate = roots["shared_tools_root"]
        if os.path.isdir(workspace_candidate):
            return workspace_candidate, use_platform, arch, list(candidates)
        if os.path.isdir(shared_candidate):
            return shared_candidate, use_platform, arch, list(candidates)

    fallback_arch = candidates[0]
    fallback_roots = canonical_workspace_dirs(
        repo_root, ws_id=chosen_ws, platform_id=use_platform, arch_id=fallback_arch
    )
    fallback = fallback_roots["shared_tools_root"]
    return fallback, use_platform, fallback_arch, list(candidates)


def canonical_tools_dir(repo_root, platform_id="", arch_id="", ws_id="", env=None):
    return canonical_tools_dir_details(repo_root, platform_id, arch_id, ws_id=ws_id, env=env)[0]


def canonical_build_dirs(repo_root, ws_id="", platform_id="", arch_id="", env=None):
    repo_root = _norm(os.path.abspath(repo_root))
    dirs = canonical_workspace_dirs(
        repo_root,
        ws_id=ws_id or canonical_workspace_id(repo_root, env=env, platform_id=platform_id, arch_id=arch_id),
        platform_id=platform_id,
        arch_id=arch_id,
    )
    return {
        "workspace_id": dirs["workspace_id"],
        "verify": dirs["build_verify"],
        "dev": dirs["build_dev"],
        "build_root": dirs["build_root"],
        "dist_root": dirs["dist_root"],
        "legacy_verify": dirs["legacy_verify"],
        "msvc_base": dirs["msvc_base"],
    }


def canonicalize_env_for_workspace(env, repo_root, ws_id="", platform_id="", arch_id=""):
    """Return env with canonical PATH + workspace metadata applied."""

    env_out = dict(env or {})
    host_path = env_out.get("PATH", "")
    if not host_path:
        host_path = env_out.get("DOM_HOST_PATH", "")
    if not host_path:
        host_path = default_host_path()
    env_out["PATH"] = host_path
    env_out["DOM_HOST_PATH"] = host_path
    dirs = canonical_workspace_dirs(
        repo_root,
        ws_id=ws_id or canonical_workspace_id(repo_root, env=env, platform_id=platform_id, arch_id=arch_id),
        platform_id=platform_id,
        arch_id=arch_id,
    )
    tools_dir = canonical_tools_dir(
        repo_root, platform_id=dirs["platform"], arch_id=dirs["arch"], ws_id=dirs["workspace_id"], env=env_out
    )
    env_out = prepend_tools_to_path(env_out, tools_dir)
    env_out["DOM_REPO_ROOT"] = _norm(os.path.abspath(repo_root))
    env_out[WORKSPACE_ID_ENV_KEY] = dirs["workspace_id"]
    env_out["DOM_WS_BUILD_ROOT"] = dirs["build_root"]
    env_out["DOM_WS_VERIFY_BUILD_DIR"] = dirs["build_verify"]
    env_out["DOM_WS_DIST_ROOT"] = dirs["dist_root"]
    env_out["DOM_WS_REMEDIATION_ROOT"] = dirs["remediation_root"]
    env_out["DOM_CANONICAL_TOOLS_DIR"] = tools_dir
    return env_out, dirs


def select_verify_build_dir(repo_root, ws_id="", platform_id="", arch_id="", env=None):
    """Select the best available verify build dir for this workspace."""

    dirs = canonical_workspace_dirs(
        repo_root,
        ws_id=ws_id or canonical_workspace_id(repo_root, env=env, platform_id=platform_id, arch_id=arch_id),
        platform_id=platform_id,
        arch_id=arch_id,
    )
    if os.path.isdir(dirs["build_verify"]):
        return dirs["build_verify"], dirs
    if os.path.isdir(dirs["legacy_verify"]):
        return dirs["legacy_verify"], dirs
    return dirs["build_verify"], dirs


def select_dist_root(repo_root, ws_id="", platform_id="", arch_id="", env=None):
    """Select workspace dist root with deterministic fallback to canonical dist."""

    dirs = canonical_workspace_dirs(
        repo_root,
        ws_id=ws_id or canonical_workspace_id(repo_root, env=env, platform_id=platform_id, arch_id=arch_id),
        platform_id=platform_id,
        arch_id=arch_id,
    )
    if os.path.isdir(dirs["dist_root"]):
        return dirs["dist_root"], dirs
    fallback = _norm(os.path.join(repo_root, "dist"))
    return fallback, dirs


def ensure_workspace_dirs(repo_root, ws_id="", platform_id="", arch_id="", env=None):
    """Create workspace-scoped non-runtime directories used by gate artifacts."""

    dirs = canonical_workspace_dirs(
        repo_root,
        ws_id=ws_id or canonical_workspace_id(repo_root, env=env, platform_id=platform_id, arch_id=arch_id),
        platform_id=platform_id,
        arch_id=arch_id,
    )
    for key in ("build_root", "dist_root", "remediation_root"):
        path = dirs.get(key, "")
        if path and not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
    return dirs


def workspace_artifact_dir(repo_root, ws_id="", category=""):
    """Return workspace-scoped artifact directory under docs/audit."""

    dirs = canonical_workspace_dirs(repo_root, ws_id=ws_id)
    root = dirs["remediation_root"]
    if category:
        root = _norm(os.path.join(root, sanitize_workspace_id(category) or category))
    return root


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


def prepend_to_env(env, key, value):
    out = dict(env or {})
    key_name = str(key)
    prepend_value = str(value or "")
    existing = out.get(key_name, "")
    items = [item for item in existing.split(os.pathsep) if item]
    norm_prepend = _norm_case(prepend_value)
    dedup = []
    seen = set()
    for item in items:
        norm_item = _norm_case(item)
        if norm_item in seen or norm_item == norm_prepend:
            continue
        seen.add(norm_item)
        dedup.append(item)
    out[key_name] = os.pathsep.join([prepend_value] + dedup) if prepend_value else os.pathsep.join(dedup)
    return out


def prepend_tools_to_path(env, tools_dir):
    out = prepend_to_env(env, "PATH", tools_dir)
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
