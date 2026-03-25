"""Shared OFFLINE-ARCHIVE-0 TestX helpers."""

from __future__ import annotations

import json
import os
import tarfile
import tempfile

from tools.release.offline_archive_common import (
    ARCHIVE_RECORD_FILENAME,
    OFFLINE_ARCHIVE_BASELINE_REL,
    OFFLINE_ARCHIVE_VERIFY_JSON_REL,
    _SUBCHECK_IDS,
    build_offline_archive,
    load_offline_archive_baseline,
    load_offline_archive_verify,
    verify_offline_archive,
)


def committed_verify(repo_root: str) -> dict:
    return load_offline_archive_verify(repo_root, OFFLINE_ARCHIVE_VERIFY_JSON_REL)


def committed_baseline(repo_root: str) -> dict:
    return load_offline_archive_baseline(repo_root, OFFLINE_ARCHIVE_BASELINE_REL)


def build_and_verify(repo_root: str, suffix: str) -> tuple[dict, dict]:
    output_root_rel = os.path.join("build", "tmp", "testx_omega8_archive", suffix)
    build_report = build_offline_archive(repo_root, output_root_rel=output_root_rel)
    verify_report = verify_offline_archive(repo_root, archive_path=str(build_report.get("archive_bundle_path", "")).strip(), baseline_path="")
    return build_report, verify_report


def load_archive_record_from_build(build_report: dict) -> dict:
    staging_root = str(build_report.get("staging_root_rel", "")).strip()
    if not staging_root:
        raise AssertionError("build report missing staging_root_rel")
    path = os.path.join(os.getcwd(), staging_root.replace("/", os.sep), ARCHIVE_RECORD_FILENAME)
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("archive record is not a JSON object")
    return payload


def unpack_archive(archive_path: str) -> str:
    extract_root = tempfile.mkdtemp(prefix="omega8_testx_")
    with tarfile.open(os.path.abspath(archive_path), "r:gz") as handle:
        handle.extractall(extract_root)
    roots = sorted(name for name in os.listdir(extract_root) if os.path.isdir(os.path.join(extract_root, name)))
    if not roots:
        raise AssertionError("archive extraction produced no root")
    return os.path.join(extract_root, roots[0])


def required_subcheck_ids() -> list[str]:
    return list(_SUBCHECK_IDS)
