"""Deterministic ARCHIVE-POLICY-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from governance import governance_profile_hash, load_governance_profile
from release import (
    DEFAULT_RELEASE_INDEX_REL,
    DEFAULT_RELEASE_MANIFEST_REL,
    load_release_index,
    load_release_manifest,
    release_index_hash,
    write_release_index,
)
from release.archive_policy import (
    DEFAULT_ARCHIVE_BUNDLE_PREFIX,
    DEFAULT_ARCHIVE_RECORD_REL,
    DEFAULT_MIRROR_LIST,
    archive_record_hash,
    build_deterministic_archive_bundle,
    canonicalize_archive_record,
    load_archive_record,
    release_index_history_rel,
    write_archive_record,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "ARCHIVE_POLICY0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "release", "ARCHIVE_AND_RETENTION_POLICY.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "ARCHIVE_POLICY_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "archive_policy_report.json")
ARCHIVE_RECORD_SCHEMA_REL = os.path.join("schema", "release", "archive_record.schema")
ARCHIVE_RECORD_SCHEMA_JSON_REL = os.path.join("schemas", "archive_record.schema.json")
ARCHIVE_POLICY_REGISTRY_REL = os.path.join("data", "registries", "archive_policy_registry.json")
RULE_ARCHIVE_RECORD = "INV-RELEASES-MUST-GENERATE-ARCHIVE-RECORD"
RULE_INDEX_HISTORY = "INV-NO-RELEASE-INDEX-OVERWRITE"
LAST_REVIEWED = "2026-03-14"
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_RELEASE_ID = "v0.0.0-mock"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_text(repo_root: str, rel_path: str) -> str:
    try:
        with open(os.path.join(_norm(repo_root), rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(_norm(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directory_tree_hash(path: str) -> str:
    rows: list[dict[str, str]] = []
    root = _norm(path)
    for current_root, _dirs, files in os.walk(root):
        rel_root = os.path.relpath(current_root, root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(files):
            abs_path = os.path.join(current_root, name)
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rows.append({"path": _norm_rel(rel_path), "sha256": _sha256_file(abs_path)})
    return canonical_sha256({"files": rows})


def _verify_manifest_artifacts(bundle_root: str, release_manifest: Mapping[str, object]) -> dict:
    errors: list[dict] = []
    for row in _as_list(_as_map(release_manifest).get("artifacts")):
        item = _as_map(row)
        if _token(item.get("artifact_kind")) == "artifact.manifest":
            continue
        rel_path = _token(item.get("artifact_name"))
        expected_hash = _token(item.get("content_hash")).lower()
        abs_path = os.path.join(_norm(bundle_root), rel_path.replace("/", os.sep))
        if not rel_path:
            continue
        if not os.path.exists(abs_path):
            errors.append(
                {
                    "code": "archive_artifact_missing",
                    "message": "release artifact is missing from the archived distribution",
                    "path": rel_path,
                }
            )
            continue
        actual_hash = _directory_tree_hash(abs_path) if os.path.isdir(abs_path) else _sha256_file(abs_path)
        if actual_hash != expected_hash:
            errors.append(
                {
                    "code": "archive_artifact_hash_mismatch",
                    "message": "release artifact content hash does not match the archived release manifest",
                    "path": rel_path,
                }
            )
    return {"result": "complete" if not errors else "refused", "errors": errors}


def _stability_payload(
    *,
    stability_class_id: str,
    rationale: str,
    future_series: str,
    replacement_target: str,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": _token(stability_class_id),
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": "",
        "deterministic_fingerprint": "",
        "extensions": {"id_stability": "stable"},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _archive_policy_row(*, archive_policy_id: str, summary: str) -> dict:
    payload = {
        "archive_policy_id": _token(archive_policy_id),
        "deterministic_fingerprint": "",
        "extensions": {"summary": _token(summary), "id_stability": "stable"},
        "stability": _stability_payload(
            stability_class_id="provisional",
            rationale="Archive policy IDs are frozen for v0.0.0-mock while operational mirror layouts remain provider-neutral.",
            future_series="ARCHIVE-POLICY",
            replacement_target="Release-series publication bundles and signed mirror manifests.",
        ),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_archive_policy_registry() -> dict:
    rows = [
        _archive_policy_row(
            archive_policy_id="archive.immutable_release",
            summary="Published release manifests, indices, component graph hashes, and governance profile hashes are immutable.",
        ),
        _archive_policy_row(
            archive_policy_id="archive.mirror_required",
            summary="Official release archival requires at least primary and secondary mirrors plus recommended cold storage.",
        ),
        _archive_policy_row(
            archive_policy_id="archive.no_overwrite",
            summary="Historical release index snapshots are append-only and may not be overwritten once published.",
        ),
    ]
    return {
        "schema_id": "dominium.registry.archive_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.archive_policy_registry",
            "registry_version": "1.0.0",
            "archive_policies": sorted(rows, key=lambda row: _token(row.get("archive_policy_id"))),
            "extensions": {"official.source": "ARCHIVE-POLICY0-2"},
        },
    }


def write_archive_policy_registry(repo_root: str) -> str:
    root = _norm(repo_root)
    return _write_json(os.path.join(root, ARCHIVE_POLICY_REGISTRY_REL), build_archive_policy_registry())


def _bundle_root(repo_root: str, platform_tag: str) -> str:
    candidates = [
        os.path.join(_norm(repo_root), "dist", "v0.0.0-mock", _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium"),
        os.path.join(_norm(repo_root), "build", "tmp", "archive_policy_dist", "v0.0.0-mock", _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium"),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, DEFAULT_RELEASE_MANIFEST_REL)):
            return candidate
    return candidates[-1]


def _archive_root(bundle_root: str) -> str:
    return os.path.join(os.path.dirname(_norm(bundle_root)), "archive")


def _ensure_bundle(repo_root: str, platform_tag: str) -> str:
    from tools.dist.dist_tree_common import build_dist_tree
    from tools.release.update_model_common import build_release_index_payload
    import shutil

    temp_root = os.path.join(_norm(repo_root), "build", "tmp", "archive_policy_dist")
    if os.path.isdir(temp_root):
        shutil.rmtree(temp_root, ignore_errors=True)
    build_dist_tree(
        repo_root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        channel_id="mock",
        output_root=temp_root,
        install_profile_id="install.profile.full",
    )
    bundle_root = os.path.join(temp_root, "v0.0.0-mock", _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium")
    release_index_payload = build_release_index_payload(
        repo_root,
        dist_root=bundle_root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
    )
    write_release_index(os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL), release_index_payload)
    return bundle_root


def _violation(rule_id: str, code: str, message: str, *, file_path: str) -> dict:
    return {
        "rule_id": _token(rule_id),
        "code": _token(code),
        "message": _token(message),
        "file_path": _norm_rel(file_path),
    }


def archive_release(
    repo_root: str,
    *,
    dist_root: str,
    release_id: str = "",
    mirror_list: Sequence[str] | None = None,
    source_archive_path: str = "",
    archive_record_path: str = "",
    write_offline_bundle: bool = False,
) -> dict:
    root = _norm(repo_root)
    bundle_root = _norm(dist_root)
    archive_root = _archive_root(bundle_root)
    release_manifest_path = os.path.join(bundle_root, DEFAULT_RELEASE_MANIFEST_REL)
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL)
    if not os.path.isfile(release_manifest_path):
        raise FileNotFoundError(release_manifest_path)
    if not os.path.isfile(release_index_path):
        from tools.release.update_model_common import build_release_index_payload

        release_index_payload = build_release_index_payload(
            root,
            dist_root=bundle_root,
            platform_tag=DEFAULT_PLATFORM_TAG,
        )
        write_release_index(release_index_path, release_index_payload)
    release_manifest = load_release_manifest(release_manifest_path)
    release_index = load_release_index(release_index_path)
    resolved_release_id = (
        _token(release_id)
        or _token(release_manifest.get("release_id"))
        or _token(_as_map(release_index.get("extensions")).get("release_id"))
        or DEFAULT_RELEASE_ID
    )
    channel_id = _token(release_index.get("channel")) or "mock"
    history_rel = release_index_history_rel(channel_id, resolved_release_id)
    history_path = os.path.join(archive_root, history_rel.replace("/", os.sep))
    current_release_index_hash = release_index_hash(release_index)
    if os.path.isfile(history_path):
        existing_release_index = load_release_index(history_path)
        existing_hash = release_index_hash(existing_release_index)
        if existing_hash != current_release_index_hash:
            raise ValueError(
                "release index history overwrite forbidden for '{}'".format(_norm_rel(os.path.relpath(history_path, bundle_root)))
            )
    else:
        write_release_index(history_path, release_index)

    governance_hash = _token(release_index.get("governance_profile_hash")).lower()
    if not governance_hash:
        governance_hash = governance_profile_hash(load_governance_profile(root, install_root=bundle_root))
    mirrors = sorted({_token(value) for value in list(mirror_list or DEFAULT_MIRROR_LIST) if _token(value)})
    source_token = _token(source_archive_path)
    source_archive_hash = _sha256_file(source_token) if source_token and os.path.isfile(_norm(source_token)) else ""
    record_payload = canonicalize_archive_record(
        {
            "release_id": resolved_release_id,
            "release_manifest_hash": _token(release_manifest.get("manifest_hash")).lower(),
            "release_index_hash": current_release_index_hash,
            "component_graph_hash": _token(release_index.get("component_graph_hash")).lower(),
            "governance_profile_hash": governance_hash,
            "source_archive_hash": source_archive_hash,
            "mirror_list": mirrors,
            "extensions": {
                "archive_policy_ids": [
                    "archive.immutable_release",
                    "archive.mirror_required",
                    "archive.no_overwrite",
                ],
                "archive_record_rel": _norm_rel(
                    os.path.relpath(
                        archive_record_path or os.path.join(archive_root, os.path.basename(DEFAULT_ARCHIVE_RECORD_REL)),
                        archive_root,
                    )
                ),
                "release_index_history_rel": history_rel,
                "release_index_rel": _norm_rel(DEFAULT_RELEASE_INDEX_REL),
                "release_manifest_rel": _norm_rel(DEFAULT_RELEASE_MANIFEST_REL),
                "source_archive_rel": _norm_rel(os.path.basename(source_token)) if source_archive_hash else "",
            },
        }
    )
    archive_record_abs = _norm(archive_record_path or os.path.join(archive_root, os.path.basename(DEFAULT_ARCHIVE_RECORD_REL)))
    write_archive_record(archive_record_abs, record_payload)

    bundle_result = {
        "bundle_path": "",
        "bundle_hash": "",
        "deterministic_fingerprint": "",
        "file_count": 0,
    }
    if write_offline_bundle:
        bundle_name = "{}-{}.tar.gz".format(DEFAULT_ARCHIVE_BUNDLE_PREFIX, resolved_release_id)
        bundle_path = os.path.join(archive_root, bundle_name)
        extra_files = {}
        if source_archive_hash:
            source_abs = _norm(source_token)
            try:
                common_root = os.path.commonpath([bundle_root, source_abs])
            except ValueError:
                common_root = ""
            if common_root != bundle_root:
                extra_files["source/{}".format(os.path.basename(source_abs))] = source_abs
        bundle_result = build_deterministic_archive_bundle(
            bundle_root,
            bundle_path,
            root_arcname="{}-{}".format(DEFAULT_ARCHIVE_BUNDLE_PREFIX, resolved_release_id),
            extra_files=extra_files,
        )
        record_payload = canonicalize_archive_record(
            {
                **record_payload,
                "extensions": {
                    **_as_map(record_payload.get("extensions")),
                    "offline_bundle_rel": _norm_rel(os.path.relpath(_token(bundle_result.get("bundle_path")), archive_root)),
                    "offline_bundle_hash": _token(bundle_result.get("bundle_hash")).lower(),
                },
            }
        )
        write_archive_record(archive_record_abs, record_payload)

    return {
        "result": "complete",
        "release_id": resolved_release_id,
        "archive_record": record_payload,
        "archive_record_hash": archive_record_hash(record_payload),
        "archive_record_path": archive_record_abs,
        "release_index_history_path": history_path,
        "release_index_history_rel": history_rel,
        "offline_bundle": bundle_result,
    }


def verify_archive(
    repo_root: str,
    *,
    dist_root: str,
    archive_record_path: str = "",
    source_archive_path: str = "",
    check_mirrors: bool = False,
) -> dict:
    root = _norm(repo_root)
    bundle_root = _norm(dist_root)
    archive_root = _archive_root(bundle_root)
    release_manifest_path = os.path.join(bundle_root, DEFAULT_RELEASE_MANIFEST_REL)
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL)
    archive_record_abs = _norm(archive_record_path or os.path.join(archive_root, os.path.basename(DEFAULT_ARCHIVE_RECORD_REL)))
    record = load_archive_record(archive_record_abs)
    release_manifest = load_release_manifest(release_manifest_path)
    release_index = load_release_index(release_index_path)
    release_manifest_result = _verify_manifest_artifacts(bundle_root, release_manifest)

    errors: list[dict] = []
    warnings: list[dict] = []
    if _token(release_manifest_result.get("result")) != "complete":
        errors.append(
            {
                "code": "archive_release_manifest_verification_failed",
                "message": "release manifest verification must succeed before archive verification can pass",
                "path": _norm_rel(DEFAULT_RELEASE_MANIFEST_REL),
            }
        )

    expected_manifest_hash = _token(release_manifest.get("manifest_hash")).lower()
    if _token(record.get("release_manifest_hash")).lower() != expected_manifest_hash:
        errors.append(
            {
                "code": "archive_record_manifest_hash_mismatch",
                "message": "archive record must reference the current release manifest hash",
                "path": _norm_rel(DEFAULT_ARCHIVE_RECORD_REL),
            }
        )

    expected_index_hash = release_index_hash(release_index)
    if _token(record.get("release_index_hash")).lower() != expected_index_hash:
        errors.append(
            {
                "code": "archive_record_release_index_hash_mismatch",
                "message": "archive record must reference the current release index hash",
                "path": _norm_rel(DEFAULT_ARCHIVE_RECORD_REL),
            }
        )

    expected_component_graph_hash = _token(release_index.get("component_graph_hash")).lower()
    if _token(record.get("component_graph_hash")).lower() != expected_component_graph_hash:
        errors.append(
            {
                "code": "archive_record_component_graph_hash_mismatch",
                "message": "archive record must reference the component graph hash advertised by the release index",
                "path": _norm_rel(DEFAULT_ARCHIVE_RECORD_REL),
            }
        )

    expected_governance_hash = _token(release_index.get("governance_profile_hash")).lower()
    if _token(record.get("governance_profile_hash")).lower() != expected_governance_hash:
        errors.append(
            {
                "code": "archive_record_governance_hash_mismatch",
                "message": "archive record must reference the governance profile hash advertised by the release index",
                "path": _norm_rel(DEFAULT_ARCHIVE_RECORD_REL),
            }
        )

    history_rel = _token(_as_map(record.get("extensions")).get("release_index_history_rel"))
    history_path = os.path.join(archive_root, history_rel.replace("/", os.sep))
    if not history_rel or not os.path.isfile(history_path):
        errors.append(
            {
                "code": "archive_release_index_history_missing",
                "message": "release index history snapshot must be retained alongside the archived release",
                "path": history_rel or _norm_rel(release_index_history_rel(_token(release_index.get("channel")), _token(record.get("release_id")))),
            }
        )
    elif release_index_hash(load_release_index(history_path)) != expected_index_hash:
        errors.append(
            {
                "code": "archive_release_index_history_hash_mismatch",
                "message": "release index history snapshot must match the archived release index payload",
                "path": history_rel,
            }
        )

    source_recorded_hash = _token(record.get("source_archive_hash")).lower()
    source_recorded_rel = _token(_as_map(record.get("extensions")).get("source_archive_rel"))
    source_candidate = _token(source_archive_path)
    if source_recorded_hash:
        resolved_source = ""
        if source_candidate and os.path.isfile(_norm(source_candidate)):
            resolved_source = _norm(source_candidate)
        elif source_recorded_rel and os.path.isfile(os.path.join(bundle_root, source_recorded_rel.replace("/", os.sep))):
            resolved_source = os.path.join(bundle_root, source_recorded_rel.replace("/", os.sep))
        if not resolved_source:
            errors.append(
                {
                    "code": "archive_source_archive_missing",
                    "message": "archive record declares a source archive hash but no matching source archive is present",
                    "path": source_recorded_rel or "source archive",
                }
            )
        elif _sha256_file(resolved_source) != source_recorded_hash:
            errors.append(
                {
                    "code": "archive_source_archive_hash_mismatch",
                    "message": "source archive hash does not match the archive record",
                    "path": _norm_rel(os.path.relpath(resolved_source, bundle_root)),
                }
            )

    offline_bundle_rel = _token(_as_map(record.get("extensions")).get("offline_bundle_rel"))
    offline_bundle_hash = _token(_as_map(record.get("extensions")).get("offline_bundle_hash")).lower()
    if offline_bundle_rel and offline_bundle_hash:
        offline_bundle_path = os.path.join(archive_root, offline_bundle_rel.replace("/", os.sep))
        if not os.path.isfile(offline_bundle_path):
            errors.append(
                {
                    "code": "archive_bundle_missing",
                    "message": "offline archive bundle must exist when the archive record declares it",
                    "path": offline_bundle_rel,
                }
            )
        elif _sha256_file(offline_bundle_path) != offline_bundle_hash:
            errors.append(
                {
                    "code": "archive_bundle_hash_mismatch",
                    "message": "offline archive bundle hash does not match the archive record",
                    "path": offline_bundle_rel,
                }
            )

    if not _as_list(record.get("mirror_list")):
        errors.append(
            {
                "code": "archive_mirror_list_missing",
                "message": "archive record must declare mirror retention targets",
                "path": _norm_rel(DEFAULT_ARCHIVE_RECORD_REL),
            }
        )
    elif check_mirrors:
        for mirror in _as_list(record.get("mirror_list")):
            token = _token(mirror)
            if not token:
                continue
            if token.startswith(("http://", "https://")):
                warnings.append(
                    {
                        "code": "archive_mirror_remote_check_skipped",
                        "message": "remote mirror reachability is optional and was skipped offline",
                        "path": token,
                    }
                )
                continue
            if token.startswith("mirror."):
                warnings.append(
                    {
                        "code": "archive_mirror_provider_neutral",
                        "message": "provider-neutral mirror identifiers are policy declarations and not directly probeable offline",
                        "path": token,
                    }
                )
                continue
            candidate = _norm(token if os.path.isabs(token) else os.path.join(archive_root, token))
            if not os.path.exists(candidate):
                errors.append(
                    {
                        "code": "archive_mirror_unreachable",
                        "message": "local mirror path is not reachable",
                        "path": token,
                    }
                )

    return {
        "result": "complete" if not errors else "refused",
        "archive_record_hash": archive_record_hash(record),
        "release_manifest_result": _token(release_manifest_result.get("result")),
        "release_index_hash": expected_index_hash,
        "errors": errors,
        "warnings": warnings,
        "deterministic_fingerprint": canonical_sha256(
            {
                "archive_record_hash": archive_record_hash(record),
                "errors": errors,
                "warnings": warnings,
                "release_manifest_result": _token(release_manifest_result.get("result")),
                "release_index_hash": expected_index_hash,
            }
        ),
    }


def build_archive_policy_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = _norm(repo_root)
    write_archive_policy_registry(root)
    bundle_root = _ensure_bundle(root, _token(platform_tag) or DEFAULT_PLATFORM_TAG)
    archive_result = archive_release(
        root,
        dist_root=bundle_root,
        release_id=DEFAULT_RELEASE_ID,
        write_offline_bundle=True,
    )
    verify_result = verify_archive(root, dist_root=bundle_root, archive_record_path=_token(archive_result.get("archive_record_path")))

    violations: list[dict] = []
    if _token(verify_result.get("result")) != "complete":
        for row in list(verify_result.get("errors") or []):
            violations.append(
                _violation(
                    RULE_ARCHIVE_RECORD,
                    _token(_as_map(row).get("code")) or "archive_verify_failed",
                    _token(_as_map(row).get("message")) or "archive verification failed",
                    file_path=_token(_as_map(row).get("path")) or DEFAULT_ARCHIVE_RECORD_REL,
                )
            )
    try:
        history_hash = release_index_hash(load_release_index(_token(archive_result.get("release_index_history_path"))))
    except Exception as exc:
        history_hash = ""
        violations.append(
            _violation(
                RULE_INDEX_HISTORY,
                "archive_history_load_failed",
                "unable to load release index history snapshot ({})".format(str(exc)),
                file_path=_token(archive_result.get("release_index_history_rel")) or DEFAULT_RELEASE_INDEX_REL,
            )
        )
    if history_hash and history_hash != _token(verify_result.get("release_index_hash")).lower():
        violations.append(
            _violation(
                RULE_INDEX_HISTORY,
                "archive_history_hash_mismatch",
                "release index history snapshot must match the archived release index hash",
                file_path=_token(archive_result.get("release_index_history_rel")) or DEFAULT_RELEASE_INDEX_REL,
            )
        )

    report = {
        "report_id": "release.archive_policy.v1",
        "result": "complete" if not violations else "refused",
        "release_id": _token(archive_result.get("release_id")) or DEFAULT_RELEASE_ID,
        "bundle_root": _norm_rel(os.path.relpath(bundle_root, root)),
        "archive_root": _norm_rel(os.path.relpath(_archive_root(bundle_root), root)),
        "archive_record_hash": _token(archive_result.get("archive_record_hash")).lower(),
        "archive_record_rel": _norm_rel(os.path.relpath(_token(archive_result.get("archive_record_path")), root)),
        "release_index_history_rel": _token(archive_result.get("release_index_history_rel")),
        "release_index_hash": _token(verify_result.get("release_index_hash")).lower(),
        "release_manifest_hash": _token(_as_map(archive_result.get("archive_record")).get("release_manifest_hash")).lower(),
        "component_graph_hash": _token(_as_map(archive_result.get("archive_record")).get("component_graph_hash")).lower(),
        "governance_profile_hash": _token(_as_map(archive_result.get("archive_record")).get("governance_profile_hash")).lower(),
        "source_archive_hash": _token(_as_map(archive_result.get("archive_record")).get("source_archive_hash")).lower(),
        "mirror_list": list(_as_map(archive_result.get("archive_record")).get("mirror_list") or []),
        "offline_bundle_hash": _token(_as_map(_as_map(archive_result.get("archive_record")).get("extensions")).get("offline_bundle_hash")).lower(),
        "offline_bundle_rel": _token(_as_map(_as_map(archive_result.get("archive_record")).get("extensions")).get("offline_bundle_rel")),
        "verify_result": _token(verify_result.get("result")),
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_archive_policy_baseline(report: Mapping[str, object]) -> str:
    rows = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DIST-7/RELEASE",
        "Replacement Target: signed publication bundles and multi-mirror release automation",
        "",
        "# Archive Policy Baseline",
        "",
        "## Retention Guarantees",
        "",
        "- Immutable release id: `{}`".format(_token(rows.get("release_id")) or DEFAULT_RELEASE_ID),
        "- Release manifest hash retained: `{}`".format(_token(rows.get("release_manifest_hash")) or "(missing)"),
        "- Release index hash retained: `{}`".format(_token(rows.get("release_index_hash")) or "(missing)"),
        "- Component graph hash retained: `{}`".format(_token(rows.get("component_graph_hash")) or "(missing)"),
        "- Governance profile hash retained: `{}`".format(_token(rows.get("governance_profile_hash")) or "(missing)"),
        "- Release index history snapshot: `{}`".format(_token(rows.get("release_index_history_rel")) or "(missing)"),
        "- Official release retention policy: no deletion of published mock release artifacts.",
        "",
        "## Mirror Strategy",
        "",
        "- Declared mirrors: {}".format(", ".join(_as_list(rows.get("mirror_list"))) or "(none)"),
        "- Required policy: primary plus secondary mirror, with offline cold storage recommended.",
        "- Provider binding: none; mirror identifiers remain provider-neutral and offline-first.",
        "",
        "## Source Archive Policy",
        "",
        "- Source archive hash: `{}`".format(_token(rows.get("source_archive_hash")) or "(not recorded)"),
        "- Mock default: source archive recording remains optional and additive for open or partially open releases.",
        "",
        "## Readiness",
        "",
        "- Offline archive bundle hash: `{}`".format(_token(rows.get("offline_bundle_hash")) or "(not generated)"),
        "- Archive verification result: `{}`".format(_token(rows.get("verify_result")) or "(unknown)"),
        "- Ready for DIST-7 packaging: yes, with immutable release record, no-overwrite history path, and deterministic offline archive bundle generation.",
        "",
    ]
    return "\n".join(lines)


def write_archive_policy_outputs(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = _norm(repo_root)
    report = build_archive_policy_report(root, platform_tag=platform_tag)
    report_json_path = _write_json(os.path.join(root, REPORT_JSON_REL), report)
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_archive_policy_baseline(report) + "\n")
    registry_path = write_archive_policy_registry(root)
    return {
        "report": report,
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
        "registry_path": _norm_rel(os.path.relpath(registry_path, root)),
    }


def archive_policy_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations: list[dict] = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "ARCHIVE-POLICY-0 retro audit is required", RULE_ARCHIVE_RECORD),
        (DOCTRINE_DOC_REL, "archive and retention doctrine is required", RULE_ARCHIVE_RECORD),
        (ARCHIVE_RECORD_SCHEMA_REL, "archive_record schema is required", RULE_ARCHIVE_RECORD),
        (ARCHIVE_RECORD_SCHEMA_JSON_REL, "compiled archive_record schema is required", RULE_ARCHIVE_RECORD),
        (ARCHIVE_POLICY_REGISTRY_REL, "archive policy registry is required", RULE_ARCHIVE_RECORD),
        ("release/archive_policy.py", "archive-policy release helpers are required", RULE_ARCHIVE_RECORD),
        ("tools/release/archive_policy_common.py", "archive-policy helper is required", RULE_ARCHIVE_RECORD),
        ("tools/release/tool_archive_release.py", "archive release tool is required", RULE_ARCHIVE_RECORD),
        ("tools/release/tool_verify_archive.py", "archive verification tool is required", RULE_ARCHIVE_RECORD),
        ("tools/release/tool_run_archive_policy.py", "archive-policy runner is required", RULE_ARCHIVE_RECORD),
        (BASELINE_DOC_REL, "archive-policy baseline is required", RULE_ARCHIVE_RECORD),
        (REPORT_JSON_REL, "archive-policy machine report is required", RULE_ARCHIVE_RECORD),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append(_violation(rule_id, "missing_required_file", message, file_path=rel_path))

    doctrine_text = _read_text(root, DOCTRINE_DOC_REL).lower()
    for token, message in (
        ("# archive and retention policy", "archive doctrine must declare the canonical title"),
        ("## immutable release principle", "archive doctrine must define immutable release rules"),
        ("## artifact storage model", "archive doctrine must define content-addressed storage"),
        ("## release index history", "archive doctrine must define append-only release index history"),
        ("## mirror strategy", "archive doctrine must define mirror strategy"),
        ("## source archive policy", "archive doctrine must define source archive retention"),
        ("## offline archive bundle", "archive doctrine must define offline archive bundle contents"),
        ("## retention guarantees", "archive doctrine must define retention guarantees"),
    ):
        if token in doctrine_text:
            continue
        violations.append(_violation(RULE_ARCHIVE_RECORD, "doctrine_token_missing", message, file_path=DOCTRINE_DOC_REL))

    try:
        report = build_archive_policy_report(root, platform_tag=DEFAULT_PLATFORM_TAG)
    except Exception as exc:
        violations.append(
            _violation(
                RULE_ARCHIVE_RECORD,
                "archive_policy_report_failed",
                "unable to build archive-policy report ({})".format(str(exc)),
                file_path=REPORT_JSON_REL,
            )
        )
        return violations
    if _token(report.get("result")) != "complete":
        for row in _as_list(report.get("violations")):
            item = _as_map(row)
            violations.append(
                _violation(
                    _token(item.get("rule_id")) or RULE_ARCHIVE_RECORD,
                    _token(item.get("code")) or "archive_policy_refused",
                    _token(item.get("message")) or "archive policy report refused",
                    file_path=_token(item.get("file_path")) or REPORT_JSON_REL,
                )
            )
    return violations


__all__ = [
    "ARCHIVE_POLICY_REGISTRY_REL",
    "ARCHIVE_RECORD_SCHEMA_JSON_REL",
    "ARCHIVE_RECORD_SCHEMA_REL",
    "BASELINE_DOC_REL",
    "DEFAULT_PLATFORM_TAG",
    "DEFAULT_RELEASE_ID",
    "DOCTRINE_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_ARCHIVE_RECORD",
    "RULE_INDEX_HISTORY",
    "archive_policy_violations",
    "archive_release",
    "build_archive_policy_registry",
    "build_archive_policy_report",
    "render_archive_policy_baseline",
    "verify_archive",
    "write_archive_policy_outputs",
]
