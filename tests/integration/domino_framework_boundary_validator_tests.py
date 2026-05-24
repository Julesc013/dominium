import argparse
import json
import os
import subprocess
import sys
import tempfile


PUBLIC_SURFACE_TOML = """\
schema_version = "fixture"

[[surface]]
id = "domino.engine.public_headers.v1"
path = "{engine_path}"

[[surface]]
id = "domino.runtime.public_headers.v1"
path = "{runtime_path}"

[[surface]]
id = "dominium.game.public_headers.v1"
path = "{game_path}"
"""


BASE_FILES = {
    "contracts/abi/README.md": "fixture\n",
    "contracts/capability/capability.contract.toml": "fixture = true\n",
    "contracts/provider/provider.contract.toml": "fixture = true\n",
    "contracts/service/service.contract.toml": "fixture = true\n",
    "engine/include/domino/engine.h": "/* fixture */\n",
    "runtime/include/domino/runtime.h": "/* fixture */\n",
    "game/include/dominium/game.h": "/* fixture */\n",
    "release/profiles/README.md": "fixture\n",
    "content/profiles/README.md": "fixture\n",
}


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


def _init_repo(root, extra_files=None, engine_path="engine/include/domino", runtime_path="runtime/include/domino"):
    _run(["git", "init", "-q"], root)
    for rel_path, text in BASE_FILES.items():
        _write(os.path.join(root, rel_path), text)
    _write(
        os.path.join(root, "contracts/public_surface/public_surface.contract.toml"),
        PUBLIC_SURFACE_TOML.format(
            engine_path=engine_path,
            runtime_path=runtime_path,
            game_path="game/include/dominium",
        ),
    )
    for rel_path, text in (extra_files or {}).items():
        _write(os.path.join(root, rel_path), text)
    result = _run(["git", "add", "."], root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def _validator(repo_root, fixture_root):
    script = os.path.join(repo_root, "tools", "validators", "repo", "check_domino_framework_boundary.py")
    result = _run(
        [sys.executable, script, "--repo-root", fixture_root, "--strict", "--json"],
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


def _codes(payload):
    return {item.get("code") for item in payload.get("findings", [])}


def main():
    parser = argparse.ArgumentParser(description="Domino framework boundary validator tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    violations = []

    with tempfile.TemporaryDirectory(prefix="domino_framework_good_") as tmp:
        _init_repo(tmp)
        result, payload = _validator(repo_root, tmp)
        _assert(result.returncode == 0, "canonical framework boundary fixture failed", violations)
        _assert(payload.get("summary", {}).get("errors", 1) == 0, "canonical fixture produced errors", violations)

    with tempfile.TemporaryDirectory(prefix="domino_framework_root_") as tmp:
        _init_repo(tmp, {"framework/include/domino.h": "/* forbidden */\n"})
        result, payload = _validator(repo_root, tmp)
        _assert(result.returncode != 0, "top-level framework root passed unexpectedly", violations)
        _assert("forbidden_top_level_root" in _codes(payload), "framework root did not report forbidden_top_level_root", violations)

    with tempfile.TemporaryDirectory(prefix="domino_framework_app_provider_") as tmp:
        _init_repo(tmp, {"apps/client/rendered/raylib/main.c": "/* forbidden */\n"})
        result, payload = _validator(repo_root, tmp)
        _assert(result.returncode != 0, "provider-specific client path passed unexpectedly", violations)
        _assert("provider_variant_product_path" in _codes(payload), "provider app path was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="domino_framework_missing_runtime_") as tmp:
        files = dict(BASE_FILES)
        files.pop("runtime/include/domino/runtime.h")
        _run(["git", "init", "-q"], tmp)
        for rel_path, text in files.items():
            _write(os.path.join(tmp, rel_path), text)
        _write(
            os.path.join(tmp, "contracts/public_surface/public_surface.contract.toml"),
            PUBLIC_SURFACE_TOML.format(
                engine_path="engine/include/domino",
                runtime_path="runtime/include/domino",
                game_path="game/include/dominium",
            ),
        )
        add = _run(["git", "add", "."], tmp)
        if add.returncode != 0:
            raise RuntimeError(add.stderr)
        result, payload = _validator(repo_root, tmp)
        _assert(result.returncode != 0, "missing runtime/include/domino passed unexpectedly", violations)
        _assert("missing_framework_surface_dir" in _codes(payload), "missing runtime include dir was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="domino_framework_broad_surface_") as tmp:
        _init_repo(tmp, engine_path="engine/include", runtime_path="runtime/include")
        result, payload = _validator(repo_root, tmp)
        _assert(result.returncode != 0, "broad include public surface paths passed unexpectedly", violations)
        _assert("public_surface_path_not_canonical" in _codes(payload), "broad public surface path was not reported", violations)

    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Domino framework boundary validator tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
