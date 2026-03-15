"""Shared ARCHIVE-POLICY-0 TestX helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

from tools.release.archive_policy_common import (
    BASELINE_DOC_REL,
    DEFAULT_PLATFORM_TAG,
    DOCTRINE_DOC_REL,
    REPORT_JSON_REL,
    RETRO_AUDIT_DOC_REL,
    archive_release,
    build_archive_policy_report,
    write_archive_policy_outputs,
)
from tools.xstack.compatx.canonical_json import canonical_json_text


def ensure_assets(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    return write_archive_policy_outputs(repo_root, platform_tag=platform_tag)


def build_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    return build_archive_policy_report(repo_root, platform_tag=platform_tag)


def report_json_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))


def baseline_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), BASELINE_DOC_REL.replace("/", os.sep))


def retro_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), RETRO_AUDIT_DOC_REL.replace("/", os.sep))


def doctrine_doc_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), DOCTRINE_DOC_REL.replace("/", os.sep))


def prepare_fixture_bundle(repo_root: str, fixture_name: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    report = build_report(repo_root, platform_tag=platform_tag)
    root = os.path.abspath(repo_root)
    bundle_src = os.path.join(root, str(report.get("bundle_root", "")).replace("/", os.sep))
    archive_src = os.path.join(root, str(report.get("archive_root", "")).replace("/", os.sep))
    fixture_root = os.path.join(root, "build", "tmp", "archive_policy_test", fixture_name)
    if os.path.isdir(fixture_root):
        shutil.rmtree(fixture_root, ignore_errors=True)
    bundle_dest = os.path.join(fixture_root, "dominium")
    archive_dest = os.path.join(fixture_root, "archive")
    shutil.copytree(bundle_src, bundle_dest)
    shutil.copytree(archive_src, archive_dest)
    return {
        "fixture_root": fixture_root,
        "bundle_root": bundle_dest,
        "archive_root": archive_dest,
        "archive_record_path": os.path.join(archive_dest, "archive_record.json"),
    }


def rerun_archive(repo_root: str, bundle_root: str, *, release_id: str = "v0.0.0-mock", write_offline_bundle: bool = True) -> dict:
    return archive_release(
        repo_root,
        dist_root=bundle_root,
        release_id=release_id,
        write_offline_bundle=write_offline_bundle,
    )


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("expected JSON object at {}".format(path))
    return payload


def write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def run_tool(repo_root: str, tool_name: str, *extra_args: str) -> dict:
    argv = [
        sys.executable,
        os.path.join(os.path.abspath(repo_root), "tools", "release", tool_name),
        "--repo-root",
        os.path.abspath(repo_root),
        *list(extra_args),
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
        raise AssertionError("archive tool {} returned a non-object payload".format(tool_name))
    payload["exit_code"] = int(proc.returncode)
    return payload


__all__ = [
    "baseline_doc_path",
    "build_report",
    "doctrine_doc_path",
    "ensure_assets",
    "load_json",
    "prepare_fixture_bundle",
    "report_json_path",
    "rerun_archive",
    "retro_doc_path",
    "run_tool",
    "write_json",
]
