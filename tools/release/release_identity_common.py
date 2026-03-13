"""Deterministic reporting and enforcement helpers for RELEASE-0."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat.descriptor import build_product_descriptor  # noqa: E402
from src.release import build_product_build_metadata, DEFAULT_PRODUCT_SEMVER  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


RELEASE0_RETRO_AUDIT_PATH = "docs/audit/RELEASE0_RETRO_AUDIT.md"
RELEASE_IDENTITY_CONSTITUTION_PATH = "docs/release/RELEASE_IDENTITY_CONSTITUTION.md"
ARTIFACT_NAMING_RULES_PATH = "docs/release/ARTIFACT_NAMING_RULES.md"
RELEASE_IDENTITY_BASELINE_PATH = "docs/audit/RELEASE_IDENTITY_BASELINE.md"
RELEASE_IDENTITY_REPORT_PATH = "data/audit/release_identity_report.json"
RELEASE_CHANNEL_REGISTRY_PATH = "data/registries/release_channel_registry.json"
ARTIFACT_KIND_REGISTRY_PATH = "data/registries/artifact_kind_registry.json"
BUILD_ID_ENGINE_PATH = "src/release/build_id_engine.py"
DESCRIPTOR_ENGINE_PATH = "src/compat/descriptor/descriptor_engine.py"

REQUIRED_RELEASE_CHANNELS = ("mock", "alpha", "beta", "rc", "stable")
REQUIRED_RELEASE_ARTIFACT_KINDS = (
    "artifact.binary",
    "artifact.pack",
    "artifact.lock",
    "artifact.profile",
    "artifact.bundle",
    "artifact.manifest",
)
BUILD_ID_WALLCLOCK_TOKENS = (
    "datetime.now(",
    "datetime.utcnow(",
    "time.time(",
    "strftime(",
    "perf_counter(",
    "monotonic(",
)
BUILD_ID_HOSTNAME_TOKENS = (
    "gethostname(",
    "platform.node(",
    "computername",
    "host_name",
    "hostname",
)
HASH_PREFIX_LENGTH = 12


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _product_rows(repo_root: str) -> list[dict]:
    payload, error = _read_json(os.path.join(repo_root, "data", "registries", "product_registry.json"))
    if error:
        return []
    rows = []
    for row in _as_list(_as_map(payload.get("record")).get("products")):
        row_map = _as_map(row)
        product_id = _token(row_map.get("product_id"))
        if product_id:
            rows.append(row_map)
    return sorted(rows, key=lambda row: _token(row.get("product_id")))


def _release_channels(repo_root: str) -> list[dict]:
    payload, error = _read_json(os.path.join(repo_root, RELEASE_CHANNEL_REGISTRY_PATH.replace("/", os.sep)))
    if error:
        return []
    rows = _as_list(_as_map(payload.get("record")).get("release_channels"))
    out = [_as_map(row) for row in rows if _token(_as_map(row).get("channel_id"))]
    return sorted(out, key=lambda row: _token(row.get("channel_id")))


def artifact_hash_prefix(content_hash: str, *, length: int = HASH_PREFIX_LENGTH) -> str:
    token = "".join(ch for ch in _token(content_hash).lower() if ch in "0123456789abcdef")
    return token[: max(1, int(length))]


def build_release_tag(semver: str, channel_id: str) -> str:
    return "v{}-{}".format(_token(semver) or DEFAULT_PRODUCT_SEMVER, _token(channel_id) or "mock")


def build_artifact_identity(
    *,
    artifact_kind: str,
    content_hash: str,
    build_id: str = "",
    contract_bundle_hash: str = "",
    platform_tag: str = "",
) -> dict:
    kind_token = _token(artifact_kind) or "artifact.unknown"
    normalized_content_hash = _token(content_hash).lower()
    suffix = artifact_hash_prefix(normalized_content_hash, length=24)
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": "artifact_identity.{}.{}".format(kind_token.replace(".", "_"), suffix),
        "artifact_kind": kind_token,
        "content_hash": normalized_content_hash,
        "build_id": _token(build_id),
        "contract_bundle_hash": _token(contract_bundle_hash).lower(),
        "platform_tag": _token(platform_tag),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def binary_artifact_name(product_id: str, semver: str, build_id: str, platform_tag: str) -> str:
    return "{}-{}+{}-{}".format(
        _token(product_id),
        _token(semver) or DEFAULT_PRODUCT_SEMVER,
        _token(build_id),
        _token(platform_tag),
    )


def pack_artifact_name(pack_id: str, pack_version: str, content_hash: str) -> str:
    return "{}-{}-{}".format(_token(pack_id), _token(pack_version), artifact_hash_prefix(content_hash))


def lock_artifact_name(content_hash: str) -> str:
    return "pack_lock-{}".format(artifact_hash_prefix(content_hash))


def bundle_artifact_name(bundle_kind: str, bundle_id: str, content_hash: str) -> str:
    return "{}-{}-{}".format(_token(bundle_kind), _token(bundle_id), artifact_hash_prefix(content_hash))


def manifest_artifact_name(kind: str, content_hash: str) -> str:
    return "manifest-{}-{}".format(_token(kind), artifact_hash_prefix(content_hash))


def release_identity_violations(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    violations: list[dict] = []
    for rel_path in (BUILD_ID_ENGINE_PATH, DESCRIPTOR_ENGINE_PATH):
        text = _read_text(os.path.join(root, rel_path.replace("/", os.sep))).lower()
        for token in BUILD_ID_WALLCLOCK_TOKENS:
            if token in text:
                violations.append(
                    {
                        "code": "wallclock_build_id_token",
                        "file_path": rel_path,
                        "message": "build identity surface must not use wall-clock token '{}'".format(token),
                        "rule_id": "INV-NO-WALLCLOCK-IN-BUILD_ID",
                    }
                )
        for token in BUILD_ID_HOSTNAME_TOKENS:
            if token in text:
                violations.append(
                    {
                        "code": "hostname_build_id_token",
                        "file_path": rel_path,
                        "message": "build identity surface must not depend on host token '{}'".format(token),
                        "rule_id": "INV-NO-WALLCLOCK-IN-BUILD_ID",
                    }
                )

    for row in _product_rows(root):
        product_id = _token(row.get("product_id"))
        descriptor = build_product_descriptor(root, product_id=product_id)
        extensions = _as_map(descriptor.get("extensions"))
        if not _token(extensions.get("official.build_id")):
            violations.append(
                {
                    "code": "descriptor_missing_build_id",
                    "file_path": DESCRIPTOR_ENGINE_PATH,
                    "message": "descriptor for '{}' must include extensions.official.build_id".format(product_id),
                    "rule_id": "INV-ENDPOINT-DESCRIPTOR-INCLUDES-BUILD_ID",
                }
            )

    artifact_registry, artifact_error = _read_json(os.path.join(root, ARTIFACT_KIND_REGISTRY_PATH.replace("/", os.sep)))
    artifact_ids = {
        _token(_as_map(row).get("artifact_kind_id"))
        for row in _as_list(_as_map(artifact_registry.get("record")).get("artifact_kinds"))
    } if not artifact_error else set()
    for artifact_kind_id in REQUIRED_RELEASE_ARTIFACT_KINDS:
        if artifact_kind_id not in artifact_ids:
            violations.append(
                {
                    "code": "artifact_kind_missing",
                    "file_path": ARTIFACT_KIND_REGISTRY_PATH,
                    "message": "artifact kind '{}' is required for release identity".format(artifact_kind_id),
                    "rule_id": "INV-ARTIFACT-IDENTITY-CONTENT-ADDRESSED",
                }
            )

    channel_ids = {_token(row.get("channel_id")) for row in _release_channels(root)}
    for channel_id in REQUIRED_RELEASE_CHANNELS:
        if channel_id not in channel_ids:
            violations.append(
                {
                    "code": "release_channel_missing",
                    "file_path": RELEASE_CHANNEL_REGISTRY_PATH,
                    "message": "release channel '{}' is required".format(channel_id),
                    "rule_id": "INV-ARTIFACT-IDENTITY-CONTENT-ADDRESSED",
                }
            )

    unique = {
        (_token(row.get("code")), _token(row.get("file_path")), _token(row.get("message"))): dict(row)
        for row in violations
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))


def build_release_identity_report(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    products = []
    for row in _product_rows(root):
        product_id = _token(row.get("product_id"))
        semver = _token(_as_map(row.get("extensions")).get("official.default_semver")) or DEFAULT_PRODUCT_SEMVER
        build_meta = build_product_build_metadata(root, product_id)
        platform_tag = "platform.portable"
        products.append(
            {
                "product_id": product_id,
                "semver": semver,
                "build_id": _token(build_meta.get("build_id")),
                "inputs_hash": _token(build_meta.get("inputs_hash")),
                "semantic_contract_registry_hash": _token(build_meta.get("semantic_contract_registry_hash")),
                "compilation_options_hash": _token(build_meta.get("compilation_options_hash")),
                "source_revision_id": _token(build_meta.get("source_revision_id")),
                "binary_name_example": binary_artifact_name(product_id, semver, _token(build_meta.get("build_id")), platform_tag),
                "release_tag_example": build_release_tag(semver, "mock"),
            }
        )
    violations = release_identity_violations(root)
    report = {
        "report_id": "release.identity.v1",
        "result": "complete" if not violations else "violation",
        "retro_audit_path": RELEASE0_RETRO_AUDIT_PATH,
        "constitution_path": RELEASE_IDENTITY_CONSTITUTION_PATH,
        "naming_rules_path": ARTIFACT_NAMING_RULES_PATH,
        "baseline_doc_path": RELEASE_IDENTITY_BASELINE_PATH,
        "products": products,
        "release_channels": _release_channels(root),
        "required_release_artifact_kinds": list(REQUIRED_RELEASE_ARTIFACT_KINDS),
        "naming_templates": {
            "binary": "<product_id>-<semver>+<build_id>-<platform_tag>",
            "pack": "<pack_id>-<pack_version>-<pack_hash_prefix>",
            "lock": "pack_lock-<hash_prefix>",
            "bundle": "<bundle_kind>-<bundle_id>-<bundle_hash_prefix>",
            "manifest": "manifest-<kind>-<hash_prefix>",
        },
        "hash_prefix_length": HASH_PREFIX_LENGTH,
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def write_release_identity_outputs(repo_root: str, report: Mapping[str, object]) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    json_path = os.path.join(root, RELEASE_IDENTITY_REPORT_PATH.replace("/", os.sep))
    md_path = os.path.join(root, RELEASE_IDENTITY_BASELINE_PATH.replace("/", os.sep))
    _write_json(json_path, report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: RELEASE",
        "Replacement Target: release-pinned artifact manifest generator and packaging baseline after RELEASE-1",
        "",
        "# Release Identity Baseline",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Build ID Inputs",
        "",
        "- semantic contract registry hash",
        "- compilation options hash",
        "- source revision identifier if available, otherwise explicit build number",
        "- product_id",
        "- platform ABI tag only when unavoidable",
        "",
        "## Product Build IDs",
        "",
        "| Product | SemVer | Build ID | Inputs Hash | Example Binary Name |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in list(report.get("products") or []):
        item = _as_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("product_id")),
                _token(item.get("semver")),
                _token(item.get("build_id")),
                _token(item.get("inputs_hash")),
                _token(item.get("binary_name_example")),
            )
        )
    lines.extend(
        [
            "",
            "## Naming Templates",
            "",
            "- binary: `{}`".format(_token(_as_map(report.get("naming_templates")).get("binary"))),
            "- pack: `{}`".format(_token(_as_map(report.get("naming_templates")).get("pack"))),
            "- lock: `{}`".format(_token(_as_map(report.get("naming_templates")).get("lock"))),
            "- bundle: `{}`".format(_token(_as_map(report.get("naming_templates")).get("bundle"))),
            "- manifest: `{}`".format(_token(_as_map(report.get("naming_templates")).get("manifest"))),
            "",
            "## Guarantees",
            "",
            "- identical canonical inputs produce identical `build_id` values",
            "- endpoint descriptors continue to carry deterministic build identity",
            "- artifact names derive from content hashes and deterministic build IDs only",
            "",
            "## Non-Guarantees",
            "",
            "- bitwise-identical binaries across distinct toolchains are desirable but not guaranteed",
            "- packaging/archive layout is not frozen by `RELEASE-0`",
            "",
            "## Readiness",
            "",
            "- Ready for `RELEASE-1` artifact manifest generation once release identity enforcement and tests stay green.",
            "",
        ]
    )
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    return {
        "baseline_doc_path": RELEASE_IDENTITY_BASELINE_PATH,
        "report_json_path": RELEASE_IDENTITY_REPORT_PATH,
    }


__all__ = [
    "ARTIFACT_KIND_REGISTRY_PATH",
    "ARTIFACT_NAMING_RULES_PATH",
    "BUILD_ID_ENGINE_PATH",
    "DESCRIPTOR_ENGINE_PATH",
    "HASH_PREFIX_LENGTH",
    "RELEASE0_RETRO_AUDIT_PATH",
    "RELEASE_CHANNEL_REGISTRY_PATH",
    "RELEASE_IDENTITY_BASELINE_PATH",
    "RELEASE_IDENTITY_CONSTITUTION_PATH",
    "RELEASE_IDENTITY_REPORT_PATH",
    "artifact_hash_prefix",
    "binary_artifact_name",
    "build_artifact_identity",
    "build_release_identity_report",
    "build_release_tag",
    "bundle_artifact_name",
    "lock_artifact_name",
    "manifest_artifact_name",
    "pack_artifact_name",
    "release_identity_violations",
    "write_release_identity_outputs",
]
