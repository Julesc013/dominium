"""FAST test: descriptors contain no wall-clock fields."""

from __future__ import annotations


TEST_ID = "test_descriptor_no_wallclock_fields"
TEST_TAGS = ["fast", "compat", "descriptor"]


FORBIDDEN_KEY_PARTS = ("time", "date", "utc", "timestamp", "clock")


def _collect_bad_keys(payload: object, path: str = "$") -> list[str]:
    out: list[str] = []
    if isinstance(payload, dict):
        for key, value in sorted(payload.items()):
            key_token = str(key)
            lowered = key_token.lower()
            if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
                out.append("{}.{}".format(path, key_token))
            out.extend(_collect_bad_keys(value, "{}.{}".format(path, key_token)))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            out.extend(_collect_bad_keys(value, "{}[{}]".format(path, index)))
    return out


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg1_testlib import emit_descriptor

    payload = emit_descriptor(repo_root, "launcher")
    bad_keys = _collect_bad_keys(payload)
    if bad_keys:
        return {"status": "fail", "message": "descriptor contains wall-clock-like keys: {}".format(", ".join(bad_keys[:5]))}
    return {"status": "pass", "message": "descriptor output excludes wall-clock fields"}
