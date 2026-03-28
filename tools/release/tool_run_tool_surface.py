#!/usr/bin/env python3
"""Generate the TOOL-SURFACE-0 registry and report artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools import sync_command_registry_with_tool_surface, write_tool_surface_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the unified Dominium tool surface.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    sync_command_registry_with_tool_surface(repo_root)
    report = write_tool_surface_outputs(repo_root)
    print(json.dumps({"result": "complete", "surface_fingerprint": report.get("surface_fingerprint", "")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
