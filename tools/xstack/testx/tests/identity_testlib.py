"""Shared UNIVERSAL-ID0 TestX helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from meta.identity import (
    IDENTITY_KIND_INSTALL,
    IDENTITY_KIND_PACK,
    attach_universal_identity_block,
    identity_content_hash_for_payload,
    build_universal_identity_block,
    canonicalize_universal_identity_block,
    universal_identity_block_fingerprint,
    validate_identity_block,
)
from tools.meta.identity_common import REPORT_JSON_REL, build_identity_report, write_identity_artifacts
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


def _write_json(path: str, payload: dict) -> str:
    target = os.path.normpath(os.path.abspath(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")
    return target


def ensure_assets(repo_root: str) -> dict:
    report_path = os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))
    if os.path.isfile(report_path):
        return build_identity_report(repo_root, strict_missing=False)
    return write_identity_artifacts(repo_root, strict_missing=False)


def build_report(repo_root: str) -> dict:
    return ensure_assets(repo_root)


def load_report(repo_root: str) -> dict:
    ensure_assets(repo_root)
    report_path = os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))
    with open(report_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def valid_pack_identity_block() -> dict:
    return build_universal_identity_block(
        identity_kind_id=IDENTITY_KIND_PACK,
        identity_id="identity.pack.fixture",
        stability_class_id="provisional",
        content_hash="a" * 64,
        semver="1.0.0",
        extensions={"fixture": "identity.pack"},
    )


def invalid_pack_identity_validation(repo_root: str) -> dict:
    block = build_universal_identity_block(
        identity_kind_id=IDENTITY_KIND_PACK,
        identity_id="identity.pack.fixture_invalid",
        stability_class_id="provisional",
        content_hash="b" * 64,
        semver="",
        extensions={"fixture": "identity.pack.invalid"},
    )
    block["semver"] = ""
    block["deterministic_fingerprint"] = universal_identity_block_fingerprint(block)
    return validate_identity_block(
        repo_root=repo_root,
        identity_block=block,
        expected={},
        strict_missing=False,
        path="build/tmp/identity_test/pack.compat.json",
    )


def schema_validation(repo_root: str) -> dict:
    report = validate_identity_block(
        repo_root=repo_root,
        identity_block=valid_pack_identity_block(),
        expected={},
        strict_missing=False,
        path="build/tmp/identity_test/pack.compat.json",
    )
    return {"valid": str(report.get("result", "")).strip() == "complete", "errors": list(report.get("errors") or [])}


def canonical_serialization_pair() -> tuple[dict, dict, str, str]:
    left = {
        "extensions": {"z": "last", "a": "first"},
        "contract_bundle_hash": "c" * 64,
        "stability_class_id": "provisional",
        "schema_version": "1.0.0",
        "identity_id": "identity.pack.fixture",
        "content_hash": "a" * 64,
        "identity_kind_id": IDENTITY_KIND_PACK,
        "protocol_range": {"max_version": "2", "min_version": "1", "protocol_id": "protocol.loopback.control"},
        "semver": "1.0.0",
        "build_id": "",
        "format_version": "",
        "deterministic_fingerprint": "",
    }
    right = {
        "identity_kind_id": IDENTITY_KIND_PACK,
        "identity_id": "identity.pack.fixture",
        "content_hash": "a" * 64,
        "semver": "1.0.0",
        "protocol_range": {"protocol_id": "protocol.loopback.control", "min_version": "1", "max_version": "2"},
        "schema_version": "1.0.0",
        "contract_bundle_hash": "c" * 64,
        "stability_class_id": "provisional",
        "extensions": {"a": "first", "z": "last"},
        "deterministic_fingerprint": "",
    }
    canonical_left = canonicalize_universal_identity_block(left)
    canonical_right = canonicalize_universal_identity_block(right)
    return (
        canonical_left,
        canonical_right,
        canonical_json_text(canonical_left),
        canonical_json_text(canonical_right),
    )


def sample_identity_artifact(repo_root: str) -> str:
    report = build_identity_report(repo_root, strict_missing=False)
    root = os.path.abspath(repo_root)
    for row in list(report.get("integration_rows") or []):
        item = dict(row or {})
        if not bool(item.get("identity_present")):
            continue
        rel_path = str(item.get("path", "")).replace("/", os.sep)
        abs_path = os.path.join(root, rel_path)
        if os.path.isfile(abs_path):
            return abs_path
    fixture_path = os.path.join(root, "build", "tmp", "identity_tools", "install.manifest.json")
    payload = {
        "install_id": "install.fixture.identity_tools",
        "install_version": "0.0.0",
        "schema_version": "2.0.0",
        "semantic_contract_registry_hash": "d" * 64,
        "supported_protocol_versions": {
            "protocol.loopback.control": {"min_version": "1.0.0", "max_version": "1.0.0"}
        },
        "deterministic_fingerprint": canonical_sha256({"fixture": "install.manifest.identity_tools"}),
        "extensions": {"official.source": "UNIVERSAL-ID0-7"},
    }
    payload = attach_universal_identity_block(
        payload,
        identity_kind_id=IDENTITY_KIND_INSTALL,
        identity_id="identity.install.install.fixture.identity_tools",
        stability_class_id="provisional",
        semver="0.0.0",
        schema_version="2.0.0",
        protocol_range=payload["supported_protocol_versions"],
        contract_bundle_hash=payload["semantic_contract_registry_hash"],
        content_hash=identity_content_hash_for_payload(payload),
        extensions={"official.rel_path": "build/tmp/identity_tools/install.manifest.json"},
    )
    return _write_json(fixture_path, payload)


def run_tool(repo_root: str, tool_rel: str, *args: str) -> subprocess.CompletedProcess[str]:
    tool_path = os.path.join(os.path.abspath(repo_root), tool_rel.replace("/", os.sep))
    return subprocess.run(
        [sys.executable, tool_path, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
        encoding="utf-8",
    )


def print_tool_outputs(repo_root: str) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    artifact_path = sample_identity_artifact(repo_root)
    first = run_tool(repo_root, "tools/meta/tool_print_identity.py", artifact_path, "--repo-root", repo_root, "--json")
    second = run_tool(repo_root, "tools/meta/tool_print_identity.py", artifact_path, "--repo-root", repo_root, "--json")
    return first, second


def diff_tool_outputs(repo_root: str) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    artifact_path = sample_identity_artifact(repo_root)
    first = run_tool(repo_root, "tools/meta/tool_diff_identity.py", artifact_path, artifact_path, "--repo-root", repo_root, "--json")
    second = run_tool(repo_root, "tools/meta/tool_diff_identity.py", artifact_path, artifact_path, "--repo-root", repo_root, "--json")
    return first, second


def tool_output_hash(repo_root: str) -> str:
    print_first, print_second = print_tool_outputs(repo_root)
    diff_first, diff_second = diff_tool_outputs(repo_root)
    payload = {
        "print_first": print_first.stdout,
        "print_second": print_second.stdout,
        "diff_first": diff_first.stdout,
        "diff_second": diff_second.stdout,
    }
    return canonical_sha256(payload)


__all__ = [
    "build_report",
    "canonical_serialization_pair",
    "diff_tool_outputs",
    "ensure_assets",
    "invalid_pack_identity_validation",
    "load_report",
    "print_tool_outputs",
    "sample_identity_artifact",
    "schema_validation",
    "tool_output_hash",
    "valid_pack_identity_block",
]
