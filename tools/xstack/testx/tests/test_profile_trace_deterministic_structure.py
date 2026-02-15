"""STRICT test: profile trace and markdown report structures are deterministic for identical inputs."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.profile.trace_deterministic_structure"
TEST_TAGS = ["strict", "tools", "determinism"]


def _run_json(repo_root: str, argv):
    proc = subprocess.run(
        argv,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return {}, "command failed: {}".format(str(proc.stdout or "").strip()[:220])
    try:
        payload = json.loads(str(proc.stdout or ""))
    except ValueError:
        return {}, "command returned non-JSON payload"
    if not isinstance(payload, dict):
        return {}, "command output root must be object"
    return payload, ""


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_text(path: str):
    return open(path, "r", encoding="utf-8").read()


def run(repo_root: str):
    trace_a_rel = "build/testx/profile/profile_trace.det.a.json"
    trace_b_rel = "build/testx/profile/profile_trace.det.b.json"
    report_a_rel = "build/testx/profile/profile_trace.det.a.md"
    report_b_rel = "build/testx/profile/profile_trace.det.b.md"
    capture_argv = [
        sys.executable,
        os.path.join(repo_root, "tools", "dev", "tool_profile_capture.py"),
        "--repo-root",
        repo_root,
        "--bundle-id",
        "bundle.base.lab",
        "--session-id",
        "session.testx.profile.deterministic",
        "--scenario-id",
        "scenario.lab.galaxy_nav",
    ]
    capture_a, err = _run_json(repo_root=repo_root, argv=capture_argv + ["--out", trace_a_rel])
    if err:
        return {"status": "fail", "message": err}
    capture_b, err = _run_json(repo_root=repo_root, argv=capture_argv + ["--out", trace_b_rel])
    if err:
        return {"status": "fail", "message": err}
    if str(capture_a.get("result", "")) != "complete" or str(capture_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "profile capture did not complete"}

    trace_a_path = os.path.join(repo_root, trace_a_rel.replace("/", os.sep))
    trace_b_path = os.path.join(repo_root, trace_b_rel.replace("/", os.sep))
    trace_a = _load_json(trace_a_path)
    trace_b = _load_json(trace_b_path)
    if trace_a != trace_b:
        return {"status": "fail", "message": "profile trace payload differs across repeated capture"}

    report_argv = [
        sys.executable,
        os.path.join(repo_root, "tools", "dev", "tool_profile_report.py"),
        "--repo-root",
        repo_root,
    ]
    report_a, err = _run_json(repo_root=repo_root, argv=report_argv + ["--trace", trace_a_rel, "--out", report_a_rel])
    if err:
        return {"status": "fail", "message": err}
    report_b, err = _run_json(repo_root=repo_root, argv=report_argv + ["--trace", trace_a_rel, "--out", report_b_rel])
    if err:
        return {"status": "fail", "message": err}
    if str(report_a.get("result", "")) != "complete" or str(report_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "profile report did not complete"}

    report_a_path = os.path.join(repo_root, report_a_rel.replace("/", os.sep))
    report_b_path = os.path.join(repo_root, report_b_rel.replace("/", os.sep))
    if _load_text(report_a_path) != _load_text(report_b_path):
        return {"status": "fail", "message": "profile report markdown differs across repeated render"}
    return {"status": "pass", "message": "profile trace/report deterministic structure passed"}
