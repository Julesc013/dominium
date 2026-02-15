"""STRICT test: profile trace artifact validates against profile_trace schema."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.profile.trace_schema_valid"
TEST_TAGS = ["strict", "tools", "schema"]


def _run_capture(repo_root: str, out_rel: str):
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "dev", "tool_profile_capture.py"),
            "--repo-root",
            repo_root,
            "--bundle-id",
            "bundle.base.lab",
            "--session-id",
            "session.testx.profile.schema",
            "--scenario-id",
            "scenario.lab.galaxy_nav",
            "--out",
            out_rel,
        ],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return {}, "tool_profile_capture failed: {}".format(str(proc.stdout or "").strip()[:180])
    try:
        payload = json.loads(str(proc.stdout or ""))
    except ValueError:
        return {}, "tool_profile_capture returned non-JSON payload"
    if not isinstance(payload, dict):
        return {}, "tool_profile_capture output root must be object"
    return payload, ""


def run(repo_root: str):
    out_rel = "build/testx/profile/profile_trace.schema_valid.json"
    capture, err = _run_capture(repo_root=repo_root, out_rel=out_rel)
    if err:
        return {"status": "fail", "message": err}
    if str(capture.get("result", "")) != "complete":
        return {"status": "fail", "message": "tool_profile_capture result is not complete"}

    trace_path = os.path.join(repo_root, out_rel.replace("/", os.sep))
    if not os.path.isfile(trace_path):
        return {"status": "fail", "message": "profile trace output file is missing"}

    trace_payload = json.load(open(trace_path, "r", encoding="utf-8"))
    if not isinstance(trace_payload, dict):
        return {"status": "fail", "message": "profile trace output root must be object"}

    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.compatx.validator import validate_instance

    validated = validate_instance(
        repo_root=repo_root,
        schema_name="profile_trace",
        payload=trace_payload,
        strict_top_level=True,
    )
    if not bool(validated.get("valid", False)):
        return {"status": "fail", "message": "profile trace schema validation failed"}
    if str(trace_payload.get("artifact_class", "")) != "DERIVED":
        return {"status": "fail", "message": "profile trace artifact_class must be DERIVED"}
    if bool(trace_payload.get("deterministic", False)) is not True:
        return {"status": "fail", "message": "profile trace deterministic flag must be true"}
    return {"status": "pass", "message": "profile trace schema validation passed"}
