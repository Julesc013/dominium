import argparse
import hashlib
import json
import os
import subprocess
import sys


CANONICAL_REL = (
    "docs/audit/performance/PERFORMX_RESULTS.json",
    "docs/audit/performance/PERFORMX_REGRESSIONS.json",
)


def _run(cmd, cwd, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _performx_run(repo_root):
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "performx", "performx.py"),
        "run",
        "--repo-root",
        repo_root,
    ]
    return _run(cmd, cwd=repo_root)


def _canonical_hash(path):
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="PerformX determinism test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    first = _performx_run(repo_root)
    if first.returncode != 0:
        print(first.stdout)
        return 1
    before = {}
    for rel in CANONICAL_REL:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            print("missing canonical artifact {}".format(rel))
            return 1
        before[rel] = _canonical_hash(path)

    second = _performx_run(repo_root)
    if second.returncode != 0:
        print(second.stdout)
        return 1

    for rel in CANONICAL_REL:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        after = _canonical_hash(path)
        if after != before[rel]:
            print("canonical hash drift detected for {}".format(rel))
            print("before={}".format(before[rel]))
            print("after={}".format(after))
            return 1

    print("performx_determinism=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

