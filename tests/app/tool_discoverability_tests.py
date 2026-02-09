import argparse
import os
import shutil
import subprocess
import sys


CANONICAL_TOOLS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)


def _resolve_tool_dir(repo_root):
    adapter = os.path.join(repo_root, "scripts", "dev", "env_tools.py")
    proc = subprocess.run(
        [sys.executable, adapter, "--repo-root", repo_root, "print-path"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("env_tools print-path failed: {}".format(proc.stdout))
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("env_tools print-path returned empty path")
    return os.path.normpath(lines[-1])


def _path_with_tool_dir(base_path, tool_dir):
    parts = [item for item in (base_path or "").split(os.pathsep) if item]
    norm_tool = os.path.normcase(os.path.normpath(tool_dir))
    dedup = []
    seen = set()
    for item in parts:
        norm_item = os.path.normcase(os.path.normpath(item))
        if norm_item in seen or norm_item == norm_tool:
            continue
        seen.add(norm_item)
        dedup.append(item)
    return os.pathsep.join([tool_dir] + dedup)


def _path_without_tool_dir(base_path, tool_dir):
    parts = [item for item in (base_path or "").split(os.pathsep) if item]
    norm_tool = os.path.normcase(os.path.normpath(tool_dir))
    kept = []
    for item in parts:
        norm_item = os.path.normcase(os.path.normpath(item))
        if norm_item == norm_tool:
            continue
        kept.append(item)
    return os.pathsep.join(kept)


def run_positive(repo_root):
    tool_dir = _resolve_tool_dir(repo_root)
    env = os.environ.copy()
    env["PATH"] = _path_with_tool_dir(env.get("PATH", ""), tool_dir)
    env["DOM_TOOLS_PATH"] = tool_dir
    env["DOM_TOOLS_READY"] = "1"

    for tool in CANONICAL_TOOLS:
        resolved = shutil.which(tool, path=env.get("PATH", ""))
        if not resolved and os.name == "nt":
            resolved = shutil.which(tool + ".exe", path=env.get("PATH", ""))
        if not resolved:
            raise RuntimeError("tool not discoverable by PATH: {}".format(tool))
        help_proc = subprocess.run(
            [resolved, "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            env=env,
            check=False,
        )
        if help_proc.returncode != 0:
            raise RuntimeError("tool help failed {}: {}".format(tool, help_proc.stdout))

    bind_exec = shutil.which("tool_ui_bind", path=env.get("PATH", ""))
    if not bind_exec and os.name == "nt":
        bind_exec = shutil.which("tool_ui_bind.exe", path=env.get("PATH", ""))
    if not bind_exec:
        raise RuntimeError("tool_ui_bind missing from canonical PATH")

    bind_proc = subprocess.run(
        [bind_exec, "--repo-root", repo_root, "--check"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
        check=False,
    )
    if bind_proc.returncode != 0:
        raise RuntimeError("tool_ui_bind --check failed: {}".format(bind_proc.stdout))

    print("tool_discoverability=ok")
    return 0


def run_missing_path(repo_root):
    tool_dir = _resolve_tool_dir(repo_root)
    env = os.environ.copy()
    env["PATH"] = _path_without_tool_dir(env.get("PATH", ""), tool_dir)
    env.pop("DOM_TOOLS_PATH", None)
    env.pop("DOM_TOOLS_READY", None)

    repox = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
    proc = subprocess.run(
        [sys.executable, repox, "--repo-root", repo_root],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
        check=False,
    )
    if proc.returncode == 0:
        raise RuntimeError("RepoX unexpectedly passed without canonical tools PATH")
    output = proc.stdout or ""
    if "INV-TOOLS-PATH-SET" not in output:
        raise RuntimeError("missing INV-TOOLS-PATH-SET in failure output:\n{}".format(output))
    if "INV-TOOL-UNRESOLVABLE" not in output:
        raise RuntimeError("missing INV-TOOL-UNRESOLVABLE in failure output:\n{}".format(output))
    print("tool_discoverability_missing_path=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canonical tool discoverability tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--scenario", choices=("positive", "missing_path"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.scenario == "positive":
        return run_positive(repo_root)
    return run_missing_path(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
