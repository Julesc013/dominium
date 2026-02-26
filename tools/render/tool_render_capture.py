#!/usr/bin/env python3
"""Capture deterministic render snapshot artifacts from RenderModel input."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.client.render.snapshot_capture import capture_render_snapshot, load_render_model_from_artifact


def _repo_root(value: str) -> str:
    token = str(value or "").strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture deterministic render snapshots from RenderModel artifacts.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--renderer", default="null", choices=("null", "software"))
    parser.add_argument("--input", required=True, help="Path to RenderModel JSON artifact.")
    parser.add_argument("--out", default="", help="Output directory root for snapshots.")
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--height", type=int, default=0)
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    input_path = os.path.normpath(os.path.abspath(str(args.input)))
    render_model, load_err = load_render_model_from_artifact(input_path)
    if load_err:
        result = {
            "result": "refusal",
            "code": "refusal.render.capture_input_invalid",
            "message": str(load_err),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    out_root = str(args.out or "").strip()
    if not out_root:
        out_root = os.path.join(repo_root, "run_meta", "render_snapshots")
    out_root = os.path.normpath(os.path.abspath(out_root))
    os.makedirs(out_root, exist_ok=True)

    result = capture_render_snapshot(
        renderer_id=str(args.renderer),
        render_model=render_model,
        out_dir=out_root,
        width=int(max(0, int(args.width))),
        height=int(max(0, int(args.height))),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
