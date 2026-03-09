"""FAST test: the canonical MVP SessionSpec template records the pack lock hash."""

from __future__ import annotations

import json
import os


TEST_ID = "test_session_template_contains_pack_lock"
TEST_TAGS = ["fast", "mvp", "session", "lockfile"]


def run(repo_root: str):
    session_rel = os.path.join("data", "session_templates", "session.mvp_default.json")
    lock_rel = os.path.join("locks", "pack_lock.mvp_default.json")
    session_path = os.path.join(repo_root, session_rel)
    lock_path = os.path.join(repo_root, lock_rel)
    if not os.path.isfile(session_path):
        return {"status": "fail", "message": "missing MVP session template artifact"}
    if not os.path.isfile(lock_path):
        return {"status": "fail", "message": "missing MVP pack lock artifact"}

    try:
        session_payload = json.load(open(session_path, "r", encoding="utf-8"))
        lock_payload = json.load(open(lock_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid JSON in session template or pack lock artifact"}

    session_hash = str(session_payload.get("pack_lock_hash", "")).strip()
    lock_hash = str(lock_payload.get("pack_lock_hash", "")).strip()
    if not session_hash:
        return {"status": "fail", "message": "session template missing pack_lock_hash"}
    if session_hash != lock_hash:
        return {"status": "fail", "message": "session template pack_lock_hash does not match canonical pack lock"}
    return {"status": "pass", "message": "MVP session template records canonical pack lock hash"}
