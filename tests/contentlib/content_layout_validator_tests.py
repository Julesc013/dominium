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
        _write(os.path.join(root, rel_path), "{}\n")
    result = _run(["git", "add", "."], root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def _content_layout(repo_root, fixture_root):
    script = os.path.join(repo_root, "tools", "validators", "repo", "check_content_layout.py")
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
    parser = argparse.ArgumentParser(description="Content layout validator tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    violations = []

    with tempfile.TemporaryDirectory(prefix="content_layout_good_") as tmp:
        _init_repo(tmp, ["content/packs/core/org.example.pack/pack.json"])
        result, payload = _content_layout(repo_root, tmp)
        _assert(result.returncode == 0, "canonical category pack layout failed", violations)
        _assert(payload.get("blocker_count", 0) == 0, "canonical category pack produced blockers", violations)

    with tempfile.TemporaryDirectory(prefix="content_layout_flat_") as tmp:
        _init_repo(tmp, ["content/packs/org.example.pack/pack.json"])
        result, payload = _content_layout(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "flat content/packs/<pack_id> layout passed", violations)
        _assert("flat_pack_id" in dispositions, "flat pack layout did not report flat_pack_id", violations)

    with tempfile.TemporaryDirectory(prefix="content_layout_missing_manifest_") as tmp:
        _init_repo(tmp, ["content/packs/core/org.example.pack/data/payload.json"])
        result, payload = _content_layout(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "pack leaf without manifest passed", violations)
        _assert("missing_pack_manifest" in dispositions, "missing manifest was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="content_layout_domain_wrapper_") as tmp:
        _init_repo(tmp, ["content/domains/game/core/physics/units.json"])
        result, payload = _content_layout(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "content/domains/game/core passed", violations)
        _assert("retired_domain_wrapper" in dispositions, "game/core wrapper was not reported", violations)

    with tempfile.TemporaryDirectory(prefix="content_layout_nested_content_") as tmp:
        _init_repo(tmp, ["content/domains/worldgen/real/earth/content/terrain.json"])
        result, payload = _content_layout(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "content/domains nested content wrapper passed", violations)
        _assert("nested_content_wrapper" in dispositions, "nested content wrapper was not reported", violations)

    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Content layout validator tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
