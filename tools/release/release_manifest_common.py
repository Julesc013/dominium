"""Deterministic reporting and enforcement helpers for RELEASE-1."""

from __future__ import annotations

import os
import tempfile
from typing import Mapping


from src.release import build_release_manifest, verify_release_manifest, write_release_manifest
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RELEASE1_RETRO_AUDIT_PATH = "docs/audit/RELEASE1_RETRO_AUDIT.md"
RELEASE_MANIFEST_MODEL_PATH = "docs/release/RELEASE_MANIFEST_MODEL.md"
RELEASE_MANIFEST_BASELINE_PATH = "docs/audit/RELEASE_MANIFEST_BASELINE.md"
RELEASE_MANIFEST_GENERATOR_PATH = "tools/release/tool_generate_release_manifest.py"
RELEASE_MANIFEST_VERIFIER_PATH = "tools/release/tool_verify_release_manifest.py"
RELEASE_MANIFEST_ENGINE_PATH = "src/release/release_manifest_engine.py"

DEFAULT_DIST_ROOT = "dist"
DEFAULT_PLATFORM_TAG = "platform.portable"
DEFAULT_CHANNEL_ID = "mock"

RULE_DETERMINISTIC = "INV-RELEASE-MANIFEST-DETERMINISTIC"
RULE_VERIFY_OFFLINE = "INV-VERIFY-OFFLINE"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _required_file_violations(repo_root: str) -> list[dict]:
    rows = []
    for rel_path, message, rule_id in (
        (RELEASE1_RETRO_AUDIT_PATH, "RELEASE1 retro audit is required", RULE_DETERMINISTIC),
        (RELEASE_MANIFEST_MODEL_PATH, "release manifest doctrine is required", RULE_DETERMINISTIC),
        (RELEASE_MANIFEST_ENGINE_PATH, "release manifest engine is required", RULE_DETERMINISTIC),
        (RELEASE_MANIFEST_GENERATOR_PATH, "release manifest generator is required", RULE_DETERMINISTIC),
        (RELEASE_MANIFEST_VERIFIER_PATH, "release manifest verifier is required", RULE_VERIFY_OFFLINE),
    ):
        if os.path.isfile(os.path.join(repo_root, rel_path.replace("/", os.sep))):
            continue
        rows.append(
            {
                "code": "release_manifest_required_file_missing",
                "file_path": rel_path,
                "message": message,
                "rule_id": rule_id,
            }
        )
    return rows


def build_release_manifest_report(
    repo_root: str,
    *,
    dist_root: str = DEFAULT_DIST_ROOT,
    platform_tag: str = DEFAULT_PLATFORM_TAG,
    channel_id: str = DEFAULT_CHANNEL_ID,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    dist_abs = os.path.normpath(os.path.abspath(os.path.join(root, dist_root))) if not os.path.isabs(dist_root) else os.path.normpath(os.path.abspath(dist_root))

    violations = _required_file_violations(root)
    manifest_first = {}
    manifest_second = {}
    verification = {
        "result": "refused",
        "errors": [
            {
                "code": "refusal.release_manifest.dist_root_missing",
                "message": "distribution root is missing",
                "path": _token(dist_root),
            }
        ],
        "warnings": [],
    }
    manifest_text_match = False
    descriptor_required_count = 0
    missing_descriptor_rows: list[dict] = []

    if os.path.isdir(dist_abs):
        manifest_first = build_release_manifest(
            dist_abs,
            platform_tag=platform_tag,
            channel_id=channel_id,
            repo_root=root,
        )
        manifest_second = build_release_manifest(
            dist_abs,
            platform_tag=platform_tag,
            channel_id=channel_id,
            repo_root=root,
        )
        manifest_text_match = canonical_json_text(manifest_first) == canonical_json_text(manifest_second)
        for row in list(manifest_first.get("artifacts") or []):
            item = _as_map(row)
            if _token(item.get("artifact_kind")) != "artifact.binary":
                continue
            extensions = _as_map(item.get("extensions"))
            if _token(extensions.get("binary_role")) == "auxiliary_wrapper":
                continue
            descriptor_required_count += 1
            if not _token(item.get("endpoint_descriptor_hash")):
                missing_descriptor_rows.append(
                    {
                        "artifact_name": _token(item.get("artifact_name")),
                        "product_id": _token(extensions.get("product_id")),
                    }
                )
        with tempfile.TemporaryDirectory(prefix="dominium_release_manifest_") as tmp_dir:
            manifest_path = os.path.join(tmp_dir, "release_manifest.json")
            write_release_manifest(dist_abs, manifest_first, manifest_path=manifest_path)
            verification = verify_release_manifest(dist_abs, manifest_path, repo_root=root)
    else:
        violations.append(
            {
                "code": "release_manifest_dist_root_missing",
                "file_path": _token(dist_root),
                "message": "distribution root '{}' is required for release manifest checks".format(_token(dist_root)),
                "rule_id": RULE_VERIFY_OFFLINE,
            }
        )

    if os.path.isdir(dist_abs) and not manifest_text_match:
        violations.append(
            {
                "code": "release_manifest_nondeterministic_ordering",
                "file_path": RELEASE_MANIFEST_ENGINE_PATH,
                "message": "release manifest generation drifted across repeated in-memory builds",
                "rule_id": RULE_DETERMINISTIC,
            }
        )
    if missing_descriptor_rows:
        for row in missing_descriptor_rows:
            violations.append(
                {
                    "code": "release_manifest_missing_descriptor_hash",
                    "file_path": RELEASE_MANIFEST_ENGINE_PATH,
                    "message": "binary artifact '{}' is missing endpoint_descriptor_hash".format(_token(row.get("artifact_name"))),
                    "rule_id": RULE_VERIFY_OFFLINE,
                }
            )
    if _token(verification.get("result")) != "complete":
        error_codes = [
            _token(_as_map(row).get("code"))
            for row in list(verification.get("errors") or [])
            if _token(_as_map(row).get("code"))
        ]
        violations.append(
            {
                "code": "release_manifest_offline_verify_failed",
                "file_path": RELEASE_MANIFEST_VERIFIER_PATH,
                "message": "offline release manifest verification failed ({})".format(", ".join(error_codes) or "unknown_error"),
                "rule_id": RULE_VERIFY_OFFLINE,
            }
        )

    unique = {
        (_token(row.get("code")), _token(row.get("file_path")), _token(row.get("message"))): dict(row)
        for row in violations
    }
    ordered_violations = sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))

    report = {
        "report_id": "release.manifest.v1",
        "result": "complete" if not ordered_violations else "violation",
        "retro_audit_path": RELEASE1_RETRO_AUDIT_PATH,
        "manifest_model_path": RELEASE_MANIFEST_MODEL_PATH,
        "baseline_doc_path": RELEASE_MANIFEST_BASELINE_PATH,
        "dist_root": dist_abs.replace("\\", "/"),
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "channel_id": _token(channel_id) or DEFAULT_CHANNEL_ID,
        "manifest_hash": _token(manifest_first.get("manifest_hash")).lower(),
        "release_id": _token(manifest_first.get("release_id")),
        "artifact_count": int(len(list(manifest_first.get("artifacts") or []))),
        "descriptor_required_count": int(descriptor_required_count),
        "manifest_text_match": bool(manifest_text_match),
        "verification_result": dict(verification or {}),
        "violations": ordered_violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def release_manifest_violations(repo_root: str) -> list[dict]:
    return list(build_release_manifest_report(repo_root).get("violations") or [])


__all__ = [
    "DEFAULT_CHANNEL_ID",
    "DEFAULT_DIST_ROOT",
    "DEFAULT_PLATFORM_TAG",
    "RELEASE1_RETRO_AUDIT_PATH",
    "RELEASE_MANIFEST_BASELINE_PATH",
    "RELEASE_MANIFEST_ENGINE_PATH",
    "RELEASE_MANIFEST_GENERATOR_PATH",
    "RELEASE_MANIFEST_MODEL_PATH",
    "RELEASE_MANIFEST_VERIFIER_PATH",
    "RULE_DETERMINISTIC",
    "RULE_VERIFY_OFFLINE",
    "build_release_manifest_report",
    "release_manifest_violations",
]
