#!/usr/bin/env python3
"""Render CLI command surface for deterministic snapshot capture."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.render.tool_render_capture import run_capture


def _repo_root(value: str) -> str:
    token = str(value or "").strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Render CLI deterministic command surface.")
    parser.add_argument("command", choices=("render.capture",))
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--input", required=True, help="Path to RenderModel JSON artifact.")
    parser.add_argument("--out", default="")
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--height", type=int, default=0)
    parser.add_argument("--wireframe", action="store_true")
    parser.add_argument("--platform-id", default="")
    parser.add_argument("--disable-hw-gl", action="store_true")
    parser.add_argument("--renderer", choices=("null", "software", "hardware_gl"), default="")
    renderer_group = parser.add_mutually_exclusive_group()
    renderer_group.add_argument("--null", action="store_true")
    renderer_group.add_argument("--software", action="store_true")
    renderer_group.add_argument("--hardware-gl", action="store_true")
    args = parser.parse_args()

    renderer_id = str(args.renderer or "").strip().lower() or "null"
    if bool(args.null):
        renderer_id = "null"
    elif bool(args.software):
        renderer_id = "software"
    elif bool(args.hardware_gl):
        renderer_id = "hardware_gl"

    result = run_capture(
        repo_root=_repo_root(args.repo_root),
        renderer=renderer_id,
        input_path=str(args.input),
        out_dir=str(args.out),
        cache_dir=str(args.cache_dir),
        width=int(args.width),
        height=int(args.height),
        wireframe=bool(args.wireframe),
        platform_id=str(args.platform_id),
        disable_hw_gl=bool(args.disable_hw_gl),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
