"""FAST test: the canonical MVP profile bundle artifact validates cleanly."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_bundle.mvp_default_valid"
TEST_TAGS = ["fast", "mvp", "bundle", "profile"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.mvp.runtime_bundle import MVP_PROFILE_BUNDLE_REL, validate_profile_bundle_payload

    bundle_path = os.path.join(repo_root, MVP_PROFILE_BUNDLE_REL.replace("/", os.sep))
    if not os.path.isfile(bundle_path):
        return {"status": "fail", "message": "missing MVP profile bundle artifact"}
    try:
        payload = json.load(open(bundle_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid JSON in MVP profile bundle artifact"}

    errors = validate_profile_bundle_payload(payload)
    if errors:
        return {"status": "fail", "message": "profile bundle validation failed: {}".format("; ".join(errors))}
    return {"status": "pass", "message": "MVP profile bundle artifact validates"}
