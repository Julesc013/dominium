"""FAST test: the MVP runtime CLI parser accepts seed, bundle, pack lock, and teleport arguments."""

from __future__ import annotations

import sys


TEST_ID = "test_cli_parses_seed_and_bundle"
TEST_TAGS = ["fast", "mvp", "cli", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.mvp.runtime_entry import build_parser

    parser = build_parser()
    args = parser.parse_args(
        [
            "client",
            "--seed",
            "42",
            "--profile_bundle",
            "profiles/bundles/bundle.mvp_default.json",
            "--pack_lock",
            "locks/pack_lock.mvp_default.json",
            "--teleport",
            "sol/earth",
        ]
    )
    if args.entrypoint != "client":
        return {"status": "fail", "message": "entrypoint parse mismatch"}
    if str(args.seed) != "42":
        return {"status": "fail", "message": "seed parse mismatch"}
    if str(args.profile_bundle) != "profiles/bundles/bundle.mvp_default.json":
        return {"status": "fail", "message": "profile_bundle parse mismatch"}
    if str(args.pack_lock) != "locks/pack_lock.mvp_default.json":
        return {"status": "fail", "message": "pack_lock parse mismatch"}
    if str(args.teleport) != "sol/earth":
        return {"status": "fail", "message": "teleport parse mismatch"}
    return {"status": "pass", "message": "MVP runtime CLI parses seed, bundle, pack lock, and teleport"}
