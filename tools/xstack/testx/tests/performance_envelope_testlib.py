"""Shared PERFORMANCE-ENVELOPE-0 TestX helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from tools.perf.performance_envelope_common import (
    BASELINE_DOC_REL,
    DEFAULT_PLATFORM_TAG,
    DOCTRINE_DOC_REL,
    REPORT_DOC_REL,
    REPORT_JSON_REL,
    RETRO_AUDIT_DOC_REL,
    build_performance_report,
    write_performance_outputs,
)


def ensure_assets(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    report_path = report_json_path(repo_root, platform_tag=platform_tag)
    report_doc = report_doc_path(repo_root, platform_tag=platform_tag)
    baseline_path = baseline_doc_path(repo_root)
    retro_path = retro_doc_path(repo_root)
    doctrine_path = doctrine_doc_path(repo_root)
    if all(os.path.isfile(path) for path in (report_path, report_doc, baseline_path, retro_path, doctrine_path)):
        return {"report": build_report(repo_root, platform_tag=platform_tag)}
    return write_performance_outputs(repo_root, platform_tag=platform_tag)


def build_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    return build_performance_report(repo_root, platform_tag=platform_tag)


def run_tool(repo_root: str, tool_name: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    argv = [
        sys.executable,
        os.path.join(os.path.abspath(repo_root), "tools", "perf", tool_name),
        "--repo-root",
        os.path.abspath(repo_root),
        "--platform-tag",
        platform_tag,
    ]
    proc = subprocess.run(
        argv,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=os.path.abspath(repo_root),
    )
    payload = json.loads(str(proc.stdout or "{}") or "{}")
    if not isinstance(payload, dict):
        raise AssertionError("performance tool {} returned a non-object payload".format(tool_name))
    payload["exit_code"] = int(proc.returncode)
    return payload


def report_json_path(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> str:
    return os.path.join(
        os.path.abspath(repo_root),
        REPORT_JSON_REL.format(platform_tag).replace("/", os.sep),
    )


def report_doc_path(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> str:
    return os.path.join(
        os.path.abspath(repo_root),
        REPORT_DOC_REL.format(platform_tag).replace("/", os.sep),
    )


def baseline_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), BASELINE_DOC_REL.replace("/", os.sep))


def retro_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), RETRO_AUDIT_DOC_REL.replace("/", os.sep))


def doctrine_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), DOCTRINE_DOC_REL.replace("/", os.sep))


__all__ = [
    "baseline_doc_path",
    "build_report",
    "doctrine_doc_path",
    "ensure_assets",
    "report_doc_path",
    "report_json_path",
    "retro_doc_path",
    "run_tool",
]
