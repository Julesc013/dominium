from __future__ import annotations

import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_sha256


EXPECTED_STAGE_ORDER = ["repox", "auditx", "testx", "validation_and_omega"]
PROFILE_IDS = ["FAST", "STRICT", "FULL"]


def _read_json(repo_root: str, rel_path: str) -> dict:
    with open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def committed_gate_definitions(repo_root: str) -> dict:
    return _read_json(repo_root, "data/xstack/gate_definitions.json")


def committed_profile(repo_root: str, profile_id: str) -> dict:
    return _read_json(repo_root, "tools/xstack/ci/profiles/{}.json".format(str(profile_id).strip().upper()))


def recompute_fingerprint(payload: dict) -> str:
    item = dict(payload or {})
    item["deterministic_fingerprint"] = ""
    return canonical_sha256(item)
