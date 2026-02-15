import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Tuple


def _run(repo_root: str) -> Tuple[int, Dict[str, object]]:
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "xstack", "pack_loader", "pack_list.py"),
        "--repo-root",
        repo_root,
    ]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return int(proc.returncode), {}
    try:
        payload = json.loads(proc.stdout or "{}")
    except ValueError:
        return 1, {}
    return int(proc.returncode), payload if isinstance(payload, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: pack_list output is deterministic and sorted.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    rc1, payload1 = _run(repo_root)
    rc2, payload2 = _run(repo_root)
    if rc1 != 0 or rc2 != 0:
        print("pack_list failed: rc1={}, rc2={}".format(rc1, rc2))
        return 1
    if payload1 != payload2:
        print("pack_list output changed between runs")
        return 1

    packs = payload1.get("packs") or []
    if not isinstance(packs, list):
        print("pack_list payload packs must be list")
        return 1
    pack_ids = [str(row.get("pack_id", "")) for row in packs]
    if pack_ids != sorted(pack_ids):
        print("pack_list not sorted by pack_id: {}".format(pack_ids))
        return 1

    print("pack_list deterministic ordering OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
