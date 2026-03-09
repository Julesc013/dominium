"""Minimal deterministic CLI/GUI/server bootstrap for MVP runtime bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.mvp.runtime_bundle import (
    MVP_PACK_LOCK_REL,
    MVP_PROFILE_BUNDLE_REL,
    build_runtime_bootstrap,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap Dominium MVP runtime entrypoints.")
    parser.add_argument("entrypoint", choices=("client", "server"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--seed", default="")
    parser.add_argument("--profile_bundle", default=MVP_PROFILE_BUNDLE_REL)
    parser.add_argument("--pack_lock", default=MVP_PACK_LOCK_REL)
    parser.add_argument("--teleport", default="")
    parser.add_argument("--authority", default="dev", choices=("dev", "release"))
    parser.add_argument("--ui", default="", choices=("", "cli", "gui", "headless"))
    return parser


def _default_ui(entrypoint: str, ui: str) -> str:
    token = str(ui).strip().lower()
    if token:
        return token
    if str(entrypoint) == "server":
        return "headless"
    return "gui"


def main() -> int:
    args = build_parser().parse_args()
    repo_root = os.path.abspath(str(args.repo_root))
    try:
        payload = build_runtime_bootstrap(
            repo_root=repo_root,
            entrypoint=str(args.entrypoint),
            ui=_default_ui(entrypoint=str(args.entrypoint), ui=str(args.ui)),
            seed=str(args.seed),
            profile_bundle_path=str(args.profile_bundle),
            pack_lock_path=str(args.pack_lock),
            teleport=str(args.teleport),
            authority_mode=str(args.authority),
        )
    except ValueError as exc:
        print(json.dumps({"reason": str(exc), "result": "refused"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
