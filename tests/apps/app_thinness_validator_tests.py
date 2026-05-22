import argparse
import json
import os
import subprocess
import sys
import tempfile


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _init_repo(root, files):
    _run(["git", "init", "-q"], root)
    for rel_path in files:
        _write(os.path.join(root, rel_path), "placeholder\n")
    result = _run(["git", "add", "."], root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def _app_thinness(repo_root, fixture_root):
    script = os.path.join(repo_root, "tools", "validators", "repo", "check_app_thinness.py")
    result = _run(
        [sys.executable, script, "--repo-root", fixture_root, "--strict", "--json", "--max-findings", "100"],
        repo_root,
    )
    try:
        payload = json.loads(result.stdout)
    except ValueError:
        payload = {}
    return result, payload


def _assert(condition, message, violations):
    if not condition:
        violations.append(message)


def main():
    parser = argparse.ArgumentParser(description="App thinness validator tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    violations = []

    with tempfile.TemporaryDirectory(prefix="app_thinness_good_") as tmp:
        _init_repo(tmp, ["apps/client/cli/client_main.c", "apps/client/adapters/client_adapter.c"])
        result, payload = _app_thinness(repo_root, tmp)
        _assert(result.returncode == 0, "product-specific app binding failed", violations)
        _assert(payload.get("blocker_count", 0) == 0, "product-specific app binding produced blockers", violations)

    with tempfile.TemporaryDirectory(prefix="app_thinness_runtime_") as tmp:
        _init_repo(tmp, ["apps/client/storage/client_store.c"])
        result, payload = _app_thinness(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "shared runtime subsystem under app passed", violations)
        _assert("shared_subsystem_under_app" in dispositions, "shared runtime path was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="app_thinness_server_authority_") as tmp:
        _init_repo(tmp, ["apps/server/authority/dom_server_authority.cpp"])
        result, payload = _app_thinness(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "server authority implementation under app passed", violations)
        _assert("fat_app_directory" in dispositions, "server authority was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="app_thinness_workbench_") as tmp:
        _init_repo(tmp, ["apps/workbench/module/world/editor/world_editor.py"])
        result, payload = _app_thinness(repo_root, tmp)
        _assert(result.returncode == 0, "Workbench module path failed", violations)
        _assert(payload.get("blocker_count", 0) == 0, "Workbench module path produced blockers", violations)

    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("App thinness validator tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
