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
        _write(os.path.join(root, rel_path), "fixture\n")
    add = _run(["git", "add", "."], root)
    if add.returncode != 0:
        raise RuntimeError(add.stderr)


def _path_terms(repo_root, fixture_root):
    script = os.path.join(repo_root, "tools", "validators", "repo", "check_path_terms.py")
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
    parser = argparse.ArgumentParser(description="Schema taxonomy path validator contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    violations = []

    with tempfile.TemporaryDirectory(prefix="schema_taxonomy_bad_") as tmp:
        _init_repo(tmp, ["contracts/schema/geo/demo.schema"])
        result, payload = _path_terms(repo_root, tmp)
        _assert(result.returncode != 0, "retired geo schema bucket did not fail strict validation", violations)
        _assert(payload.get("blocker_count", 0) > 0, "retired geo schema bucket produced no blocker", violations)

    with tempfile.TemporaryDirectory(prefix="schema_taxonomy_good_") as tmp:
        _init_repo(tmp, ["contracts/schema/domain/geology/demo.schema"])
        result, payload = _path_terms(repo_root, tmp)
        _assert(result.returncode == 0, "canonical geology schema path failed strict validation", violations)
        _assert(payload.get("blocker_count", 0) == 0, "canonical geology schema path produced blockers", violations)

    with tempfile.TemporaryDirectory(prefix="schema_taxonomy_archive_") as tmp:
        _init_repo(tmp, ["archive/legacy/contracts/schema/geo/demo.schema"])
        result, payload = _path_terms(repo_root, tmp)
        _assert(result.returncode == 0, "legacy archive schema path failed active-source validation", violations)
        _assert(payload.get("blocker_count", 0) == 0, "legacy archive schema path produced blockers", violations)

    with tempfile.TemporaryDirectory(prefix="schema_taxonomy_dup_") as tmp:
        _init_repo(
            tmp,
            [
                "contracts/schema/geo/demo.schema",
                "contracts/schema/domain/geology/demo.schema",
            ],
        )
        result, payload = _path_terms(repo_root, tmp)
        dispositions = {item.get("disposition") for item in payload.get("findings", [])}
        _assert(result.returncode != 0, "duplicate geology schema roots did not fail strict validation", violations)
        _assert(
            "schema_duplicate_spelling" in dispositions,
            "duplicate geology schema roots did not report schema_duplicate_spelling",
            violations,
        )

    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Schema taxonomy validator tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
