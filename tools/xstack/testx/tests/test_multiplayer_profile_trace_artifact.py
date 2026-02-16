"""FAST test: multiplayer performance profile trace artifact is deterministic and schema-valid."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.profile.multiplayer_trace_artifact"
TEST_TAGS = ["fast", "tools", "determinism", "multiplayer", "net"]


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
            "session.testx.profile.multiplayer",
            "--scenario-id",
            "scenario.lab.galaxy_nav",
            "--multiplayer-policy-id",
            "policy.net.srz_hybrid",
            "--multiplayer-client-count",
            "3",
            "--multiplayer-shard-count",
            "2",
            "--multiplayer-resync-count",
            "1",
            "--multiplayer-message-units-per-tick",
            "24",
            "--multiplayer-perceived-delta-units",
            "12",
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
    return payload, ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    out_a = "build/testx/profile/profile_trace.multiplayer.a.json"
    out_b = "build/testx/profile/profile_trace.multiplayer.b.json"
    first, err = _run_capture(repo_root=repo_root, out_rel=out_a)
    if err:
        return {"status": "fail", "message": err}
    second, err = _run_capture(repo_root=repo_root, out_rel=out_b)
    if err:
        return {"status": "fail", "message": err}
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "multiplayer profile trace capture did not complete"}

    payload_a = json.load(open(os.path.join(repo_root, out_a.replace("/", os.sep)), "r", encoding="utf-8"))
    payload_b = json.load(open(os.path.join(repo_root, out_b.replace("/", os.sep)), "r", encoding="utf-8"))
    if payload_a != payload_b:
        return {"status": "fail", "message": "multiplayer profile trace payload differs across identical deterministic capture"}

    from tools.xstack.compatx.validator import validate_instance

    validated = validate_instance(
        repo_root=repo_root,
        schema_name="profile_trace",
        payload=payload_a,
        strict_top_level=True,
    )
    if not bool(validated.get("valid", False)):
        return {"status": "fail", "message": "multiplayer profile trace payload failed profile_trace schema validation"}
    mm = dict((payload_a.get("extensions") or {}).get("multiplayer_metrics") or {})
    if str(mm.get("policy_id", "")) != "policy.net.srz_hybrid":
        return {"status": "fail", "message": "multiplayer profile trace policy_id extension missing"}
    return {"status": "pass", "message": "multiplayer profile trace artifact structure is deterministic"}

