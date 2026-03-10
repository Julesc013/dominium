#!/usr/bin/env python3
"""Verify EMB-1 toolbelt replay determinism."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.embodiment.emb1_probe import verify_tool_session_replay  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify EMB-1 toolbelt replay determinism.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = verify_tool_session_replay(repo_root)
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
