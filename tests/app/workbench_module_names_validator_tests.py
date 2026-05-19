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


def _workbench_names(repo_root, fixture_root):
    script = os.path.join(repo_root, "tools", "validators", "repo", "check_workbench_module_names.py")
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
    repo_root = os.path.abspath(os.environ.get("DOMINIUM_REPO_ROOT", "."))
    if len(sys.argv) > 1 and sys.argv[1] == "--repo-root" and len(sys.argv) > 2:
        repo_root = os.path.abspath(sys.argv[2])
    violations = []

    passing_cases = [
        ("game_editor", ["apps/workbench/module/game/editor/game_editor.cpp"]),
        ("ui_codegen_owner", ["tools/codegen/ui/tool_editor/gen/ui_tool_editor_actions_gen.cpp"]),
        ("runtime_native_backend", ["runtime/ui/backend/win32/native_backend.cpp"]),
        ("workbench_native_preview", ["apps/workbench/module/ui/preview/native/editor_gui.c"]),
    ]
    for name, files in passing_cases:
        with tempfile.TemporaryDirectory(prefix="workbench_names_{0}_".format(name)) as tmp:
            _init_repo(tmp, files)
            result, payload = _workbench_names(repo_root, tmp)
            _assert(result.returncode == 0, "{0} failed validation".format(name), violations)
            _assert(payload.get("blocker_count", 0) == 0, "{0} produced blockers".format(name), violations)

    failing_cases = [
        ("game_edit", ["apps/workbench/module/game/edit/game_editor.cpp"]),
        ("ui_editor_gen", ["apps/workbench/module/ui/editor/gen/ui_tool_editor_actions_gen.cpp"]),
        ("ui_editor_generated", ["apps/workbench/module/ui/editor/generated/ui_tool_editor_actions_gen.cpp"]),
        ("tool_editor", ["apps/workbench/module/tool/editor/tool_editor.cpp"]),
        ("core_segment", ["apps/workbench/module/pack/core/pack_core.cpp"]),
    ]
    for name, files in failing_cases:
        with tempfile.TemporaryDirectory(prefix="workbench_names_{0}_".format(name)) as tmp:
            _init_repo(tmp, files)
            result, payload = _workbench_names(repo_root, tmp)
            _assert(result.returncode != 0, "{0} passed unexpectedly".format(name), violations)
            _assert(payload.get("blocker_count", 0) > 0, "{0} did not report blockers".format(name), violations)

    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Workbench module naming validator tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
