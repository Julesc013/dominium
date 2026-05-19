#!/usr/bin/env python3
"""Generate deterministic MIGRATION-LIFECYCLE-0 report artifacts."""

from __future__ import annotations

import argparse
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.package.compatibility.migration_lifecycle_common import write_migration_lifecycle_outputs  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Write MIGRATION-LIFECYCLE-0 baseline artifacts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    payload = write_migration_lifecycle_outputs(os.path.abspath(str(args.repo_root)))
    print(canonical_json_text(payload))
    return 0 if str(dict(payload.get("report") or {}).get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
