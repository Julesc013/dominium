import argparse
import hashlib
import json
import os
import re
import sys
from typing import Dict, List


FROZEN_SECTION = "## Frozen constitutional surfaces"
NEXT_SECTION_PREFIX = "## "
PATH_RE = re.compile(r"`([^`]+)`")


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_frozen_paths(text: str) -> List[str]:
    lines = text.splitlines()
    paths: List[str] = []
    in_section = False
    for line in lines:
        if line.strip() == FROZEN_SECTION:
            in_section = True
            continue
        if in_section and line.startswith(NEXT_SECTION_PREFIX):
            break
        if not in_section:
            continue
        if "|" not in line:
            continue
        match = PATH_RE.search(line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Frozen contract hash guard.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    index_path = os.path.join(repo_root, "docs", "architecture", "CONTRACTS_INDEX.md")
    hash_path = os.path.join(repo_root, "docs", "architecture", "FROZEN_CONTRACT_HASHES.json")

    if not os.path.isfile(index_path):
        print("missing contracts index: {}".format(index_path))
        return 1
    if not os.path.isfile(hash_path):
        print("missing frozen contract hash file: {}".format(hash_path))
        return 1

    frozen_paths = parse_frozen_paths(load_text(index_path))
    if not frozen_paths:
        print("no frozen contract paths found in contracts index")
        return 1

    with open(hash_path, "r", encoding="utf-8") as handle:
        hashes = json.load(handle)
    entries = hashes.get("entries", [])
    hash_map: Dict[str, str] = {entry["path"]: entry["sha256"] for entry in entries}

    violations: List[str] = []

    for path in frozen_paths:
        abs_path = os.path.join(repo_root, path)
        if not os.path.isfile(abs_path):
            violations.append("missing frozen contract: {}".format(path))
            continue
        expected = hash_map.get(path)
        if not expected:
            violations.append("missing hash entry for frozen contract: {}".format(path))
            continue
        actual = sha256_file(abs_path)
        if actual != expected:
            violations.append("hash mismatch for frozen contract: {}".format(path))

    for path in hash_map:
        if path not in frozen_paths:
            violations.append("hash entry not in frozen index: {}".format(path))

    if violations:
        for violation in violations:
            print(violation)
        print("If this change is intentional, update FROZEN_CONTRACT_HASHES.json.")
        return 1

    print("Frozen contract hash guard OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
