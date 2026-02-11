import argparse
import hashlib
import json
import os
import subprocess
import sys


CANONICAL_ARTIFACTS = (
    "docs/audit/auditx/FINDINGS.json",
    "docs/audit/auditx/INVARIANT_MAP.json",
    "docs/audit/auditx/PROMOTION_CANDIDATES.json",
    "docs/audit/auditx/TRENDS.json",
)


def _run_scan(repo_root):
    tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    result = subprocess.run(
        [sys.executable, tool, "scan", "--repo-root", repo_root, "--format", "json"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.returncode, result.stdout


def _canonical_hash(path):
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="AuditX canonical hash stability test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    rc, out = _run_scan(repo_root)
    if rc != 0:
        print(out)
        return 1

    before = {}
    for rel in CANONICAL_ARTIFACTS:
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            print("missing canonical artifact {}".format(rel))
            return 1
        before[rel] = _canonical_hash(abs_path)

    rc, out = _run_scan(repo_root)
    if rc != 0:
        print(out)
        return 1

    for rel in CANONICAL_ARTIFACTS:
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        after = _canonical_hash(abs_path)
        if before[rel] != after:
            print("canonical hash drift for {}".format(rel))
            print("before={}".format(before[rel]))
            print("after={}".format(after))
            return 1

    print("test_auditx_canonical_hash_stability=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

