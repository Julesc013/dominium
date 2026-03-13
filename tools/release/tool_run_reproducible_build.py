#!/usr/bin/env python3
"""Generate deterministic RELEASE-2 reproducible build outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.reproducible_build_common import (  # noqa: E402
    build_reproducible_build_report,
    write_reproducible_build_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate RELEASE-2 reproducible-build outputs.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dist-root", default="dist")
    parser.add_argument("--platform-tag", default="platform.portable")
    parser.add_argument("--channel", default="mock")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    report = build_reproducible_build_report(
        repo_root,
        dist_root=str(args.dist_root).strip() or "dist",
        platform_tag=str(args.platform_tag).strip() or "platform.portable",
        channel_id=str(args.channel).strip() or "mock",
    )
    written = write_reproducible_build_outputs(repo_root, report)
    payload = {
        "result": _result_token(report),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "violation_count": int(len(list(report.get("violations") or []))),
        "written_outputs": dict(written),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if _result_token(report) == "complete" else 2


def _result_token(report: dict) -> str:
    return str(report.get("result", "")).strip() or "complete"


if __name__ == "__main__":
    raise SystemExit(main())
