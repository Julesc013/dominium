"""Deterministic reporting and enforcement helpers for RELEASE-2."""

from __future__ import annotations

import os
import tempfile
from typing import Mapping


from release import (
    build_mock_signature_block,
    build_release_manifest,
    verify_release_manifest,
    write_release_manifest,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RELEASE2_RETRO_AUDIT_PATH = "docs/audit/RELEASE2_RETRO_AUDIT.md"
REPRODUCIBLE_BUILD_RULES_PATH = "docs/release/REPRODUCIBLE_BUILD_RULES.md"
SIGNING_POLICY_PATH = "docs/release/SIGNING_POLICY.md"
REPRODUCIBLE_BUILD_BASELINE_PATH = "docs/audit/REPRODUCIBLE_BUILD_BASELINE.md"
BUILD_ID_ENGINE_PATH = "release/build_id_engine.py"
RELEASE_MANIFEST_ENGINE_PATH = "release/release_manifest_engine.py"
RELEASE_MANIFEST_GENERATOR_PATH = "tools/release/tool_generate_release_manifest.py"
RELEASE_MANIFEST_VERIFIER_PATH = "tools/release/tool_verify_release_manifest.py"
REPRODUCIBILITY_TOOL_PATH = "tools/release/tool_verify_build_reproducibility.py"
SIGNATURE_SCHEMA_PATH = "schema/release/signature_block.schema"
SIGNATURE_SCHEMA_JSON_PATH = "schemas/signature_block.schema.json"

DEFAULT_DIST_ROOT = "dist"
DEFAULT_PLATFORM_TAG = "platform.portable"
DEFAULT_CHANNEL_ID = "mock"

RULE_NO_WALLCLOCK = "INV-NO-WALLCLOCK-IN-BUILD"
RULE_BUILD_ID_MATCHES = "INV-BUILD-ID-MATCHES-MANIFEST"

WALLCLOCK_TOKENS = (
    "datetime.now(",
    "datetime.utcnow(",
    "time.time(",
    "strftime(",
    "perf_counter(",
    "monotonic(",
    "timestamp(",
)
HOST_TOKENS = (
    "gethostname(",
    "platform.node(",
    "computername",
    "hostname",
)

KNOWN_PLATFORM_CAVEATS = (
    "bitwise-identical binaries across distinct toolchains are not guaranteed in RELEASE-2",
    "signature verification is additive and mock-channel releases may remain unsigned",
)

REPRODUCIBILITY_CHECKLIST = (
    "build_id derives only from deterministic build inputs",
    "manifest ordering is deterministic across repeated generation",
    "optional signatures do not perturb manifest identity fields",
    "offline verification succeeds without requiring a signature",
    "build_id can be recomputed from descriptor-emitted build metadata",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _required_file_violations(repo_root: str) -> list[dict]:
    rows = []
    for rel_path, message, rule_id in (
        (RELEASE2_RETRO_AUDIT_PATH, "RELEASE2 retro audit is required", RULE_BUILD_ID_MATCHES),
        (REPRODUCIBLE_BUILD_RULES_PATH, "reproducible build doctrine is required", RULE_NO_WALLCLOCK),
        (SIGNING_POLICY_PATH, "signing policy is required", RULE_BUILD_ID_MATCHES),
        (SIGNATURE_SCHEMA_PATH, "signature block schema is required", RULE_BUILD_ID_MATCHES),
        (SIGNATURE_SCHEMA_JSON_PATH, "signature block JSON schema is required", RULE_BUILD_ID_MATCHES),
        (BUILD_ID_ENGINE_PATH, "deterministic build_id engine is required", RULE_NO_WALLCLOCK),
        (RELEASE_MANIFEST_ENGINE_PATH, "release manifest engine is required", RULE_BUILD_ID_MATCHES),
        (RELEASE_MANIFEST_GENERATOR_PATH, "release manifest generator is required", RULE_BUILD_ID_MATCHES),
        (RELEASE_MANIFEST_VERIFIER_PATH, "release manifest verifier is required", RULE_BUILD_ID_MATCHES),
        (REPRODUCIBILITY_TOOL_PATH, "build reproducibility verifier is required", RULE_BUILD_ID_MATCHES),
        ("tools/auditx/analyzers/e494_non_reproducible_build_smell.py", "NonReproducibleBuildSmell analyzer is required", RULE_BUILD_ID_MATCHES),
        ("tools/auditx/analyzers/e495_embedded_timestamp_smell.py", "EmbeddedTimestampSmell analyzer is required", RULE_NO_WALLCLOCK),
    ):
        if os.path.isfile(os.path.join(repo_root, rel_path.replace("/", os.sep))):
            continue
        rows.append(
            {
                "code": "reproducible_build_required_file_missing",
                "file_path": rel_path,
                "message": message,
                "rule_id": rule_id,
            }
        )
    return rows


def reproducible_build_violations(
    repo_root: str,
    *,
    dist_root: str = DEFAULT_DIST_ROOT,
    platform_tag: str = DEFAULT_PLATFORM_TAG,
    channel_id: str = DEFAULT_CHANNEL_ID,
) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    violations = _required_file_violations(root)

    for rel_path in (BUILD_ID_ENGINE_PATH, RELEASE_MANIFEST_ENGINE_PATH, REPRODUCIBILITY_TOOL_PATH):
        text = _read_text(os.path.join(root, rel_path.replace("/", os.sep))).lower()
        for token in WALLCLOCK_TOKENS:
            if token in text:
                violations.append(
                    {
                        "code": "wallclock_build_token",
                        "file_path": rel_path,
                        "message": "reproducible build surface must not use wall-clock token '{}'".format(token),
                        "rule_id": RULE_NO_WALLCLOCK,
                    }
                )
        for token in HOST_TOKENS:
            if token in text:
                violations.append(
                    {
                        "code": "host_metadata_build_token",
                        "file_path": rel_path,
                        "message": "reproducible build surface must not use host token '{}'".format(token),
                        "rule_id": RULE_NO_WALLCLOCK,
                    }
                )

    dist_abs = os.path.join(root, dist_root.replace("/", os.sep)) if not os.path.isabs(dist_root) else dist_root
    dist_abs = os.path.normpath(os.path.abspath(dist_abs))
    if not os.path.isdir(dist_abs):
        violations.append(
            {
                "code": "reproducible_build_dist_root_missing",
                "file_path": _token(dist_root),
                "message": "distribution root '{}' is required for reproducible build checks".format(_token(dist_root)),
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )
        return sorted(violations, key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))

    try:
        manifest_first = build_release_manifest(
            dist_abs,
            platform_tag=platform_tag,
            channel_id=channel_id,
            repo_root=root,
            verify_build_ids=True,
        )
        manifest_second = build_release_manifest(
            dist_abs,
            platform_tag=platform_tag,
            channel_id=channel_id,
            repo_root=root,
            verify_build_ids=True,
        )
    except Exception as exc:
        violations.append(
            {
                "code": "build_id_cross_check_failed",
                "file_path": RELEASE_MANIFEST_ENGINE_PATH,
                "message": "release manifest build-id cross-check failed ({})".format(str(exc)),
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )
        return sorted(violations, key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))
    if canonical_json_text(manifest_first) != canonical_json_text(manifest_second):
        violations.append(
            {
                "code": "reproducible_manifest_drift",
                "file_path": RELEASE_MANIFEST_ENGINE_PATH,
                "message": "release manifest drifted across repeated builds of identical inputs",
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )

    signature = build_mock_signature_block(signer_id="signer.mock.release2", signed_hash=_token(manifest_first.get("manifest_hash")).lower())
    signed_manifest = build_release_manifest(
        dist_abs,
        platform_tag=platform_tag,
        channel_id=channel_id,
        repo_root=root,
        signatures=[signature],
        verify_build_ids=True,
    )
    if (
        _token(manifest_first.get("manifest_hash")).lower() != _token(signed_manifest.get("manifest_hash")).lower()
        or _token(manifest_first.get("deterministic_fingerprint")).lower() != _token(signed_manifest.get("deterministic_fingerprint")).lower()
    ):
        violations.append(
            {
                "code": "signature_changes_manifest_identity",
                "file_path": RELEASE_MANIFEST_ENGINE_PATH,
                "message": "optional signatures must not change manifest identity fields",
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )

    with tempfile.TemporaryDirectory(prefix="dominium_release2_verify_") as tmp_dir:
        manifest_path = os.path.join(tmp_dir, "release_manifest.json")
        write_release_manifest(dist_abs, manifest_first, manifest_path=manifest_path)
        verification = verify_release_manifest(dist_abs, manifest_path, repo_root=root)
    if _token(verification.get("result")) != "complete":
        error_codes = ", ".join(
            _token(_as_map(row).get("code")) for row in list(verification.get("errors") or []) if _token(_as_map(row).get("code"))
        ) or "unknown_error"
        violations.append(
            {
                "code": "offline_verification_failed",
                "file_path": RELEASE_MANIFEST_VERIFIER_PATH,
                "message": "offline release verification failed ({})".format(error_codes),
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )
    if _token(verification.get("signature_status")) not in {"verified", "signature_missing"}:
        violations.append(
            {
                "code": "signature_status_invalid",
                "file_path": RELEASE_MANIFEST_VERIFIER_PATH,
                "message": "verification produced an unexpected signature status '{}'" .format(_token(verification.get("signature_status"))),
                "rule_id": RULE_BUILD_ID_MATCHES,
            }
        )

    unique = {
        (_token(row.get("code")), _token(row.get("file_path")), _token(row.get("message"))): dict(row)
        for row in violations
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))


def build_reproducible_build_report(
    repo_root: str,
    *,
    dist_root: str = DEFAULT_DIST_ROOT,
    platform_tag: str = DEFAULT_PLATFORM_TAG,
    channel_id: str = DEFAULT_CHANNEL_ID,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    dist_abs = os.path.join(root, dist_root.replace("/", os.sep)) if not os.path.isabs(dist_root) else dist_root
    dist_abs = os.path.normpath(os.path.abspath(dist_abs))
    violations = reproducible_build_violations(root, dist_root=dist_root, platform_tag=platform_tag, channel_id=channel_id)
    report = {
        "report_id": "release.reproducible_build.v1",
        "result": "complete" if not violations else "violation",
        "dist_root": dist_abs.replace("\\", "/"),
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "channel_id": _token(channel_id) or DEFAULT_CHANNEL_ID,
        "checklist": list(REPRODUCIBILITY_CHECKLIST),
        "known_platform_caveats": list(KNOWN_PLATFORM_CAVEATS),
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _baseline_markdown(report: Mapping[str, object]) -> str:
    checklist_lines = "\n".join("- {}".format(item) for item in list(report.get("checklist") or []))
    caveat_lines = "\n".join("- {}".format(item) for item in list(report.get("known_platform_caveats") or []))
    return "\n".join(
        [
            "Status: DERIVED",
            "Last Reviewed: 2026-03-13",
            "Stability: provisional",
            "Future Series: RELEASE",
            "Replacement Target: stronger reproducible-build and signing enforcement after RELEASE-3",
            "",
            "# Reproducible Build Baseline",
            "",
            "## Reproducibility Checklist",
            "",
            checklist_lines,
            "",
            "## Known Platform Caveats",
            "",
            caveat_lines,
            "",
            "## Signing Behavior Summary",
            "",
            "- Signing is optional and external to the build pipeline.",
            "- Optional signatures do not change `manifest_hash` or `deterministic_fingerprint`.",
            "- Offline verification succeeds without signatures and reports `signature_missing` non-fatally for mock-channel releases.",
            "",
            "## Readiness",
            "",
            "- Ready for `RELEASE-3` final pre-DIST freeze.",
            "- Current reproducible-build rule fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint")).lower()),
            "",
        ]
    )


def write_reproducible_build_outputs(repo_root: str, report: Mapping[str, object]) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    baseline_path = os.path.join(root, REPRODUCIBLE_BUILD_BASELINE_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_baseline_markdown(report))
    return {
        "baseline_doc_path": REPRODUCIBLE_BUILD_BASELINE_PATH,
    }


__all__ = [
    "DEFAULT_CHANNEL_ID",
    "DEFAULT_DIST_ROOT",
    "DEFAULT_PLATFORM_TAG",
    "RELEASE2_RETRO_AUDIT_PATH",
    "REPRODUCIBLE_BUILD_BASELINE_PATH",
    "REPRODUCIBLE_BUILD_RULES_PATH",
    "REPRODUCIBILITY_TOOL_PATH",
    "RULE_BUILD_ID_MATCHES",
    "RULE_NO_WALLCLOCK",
    "SIGNING_POLICY_PATH",
    "build_reproducible_build_report",
    "reproducible_build_violations",
    "write_reproducible_build_outputs",
]
