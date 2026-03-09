#!/usr/bin/env python3
"""Verify EARTH-0 far-LOD surface consistency without renderer dependencies."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.worldgen.earth0_probe import verify_earth_surface_consistency  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify EARTH-0 far-LOD surface consistency.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = verify_earth_surface_consistency(repo_root)
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (
        str(report.get("result", "")).strip() == "complete"
        and bool(report.get("ocean_ratio_within_bounds"))
        and bool(report.get("polar_ice_present"))
        and bool(report.get("axial_tilt_affects_daylight"))
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
