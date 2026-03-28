"""Deterministic store verification and GC engine for STORE-GC-0."""

from __future__ import annotations

import os
import shutil
from typing import Mapping, Sequence

from lib.install.install_validator import default_install_registry_path
from tools.xstack.compatx.canonical_json import canonical_sha256

from .reachability_engine import (
    ARTIFACT_JSON_PAYLOAD,
    ARTIFACT_MANIFEST_NAME,
    ARTIFACT_TREE_PAYLOAD,
    QUARANTINE_DIRNAME,
    STORE_CATEGORY_IDS,
    STORE_LAYOUT_DIRNAME,
    STORE_ROOT_MANIFEST,
    _discover_install_sources,
    _artifact_root,
    _as_map,
    _json_artifact_hash,
    _norm,
    _rel_from,
    _norm_rel,
    _read_json,
    _token,
    _tree_artifact_hash,
    build_store_reachability_report,
    parse_artifact_token,
    scan_store_artifacts,
    store_artifact_token,
)


GC_MODE_NONE = "none"
GC_MODE_SAFE = "safe"
GC_MODE_AGGRESSIVE = "aggressive"
DEFAULT_GC_POLICY_ID = "gc.none"
DEFAULT_GC_POLICY_REGISTRY_REL = os.path.join("data", "registries", "gc_policy_registry.json")

REFUSAL_GC_VERIFY_FAILED = "refusal.store.gc.verify_failed"
REFUSAL_GC_PORTABLE = "refusal.store.gc.portable_refused"
REFUSAL_GC_EXPLICIT_FLAG = "refusal.store.gc.explicit_flag_required"
REFUSAL_GC_POLICY_UNKNOWN = "refusal.store.gc.unknown_policy"
REFUSAL_GC_QUARANTINE_CONFLICT = "refusal.store.gc.quarantine_conflict"


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def canonicalize_gc_policy(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    normalized = {
        "gc_policy_id": _token(row.get("gc_policy_id")),
        "mode": _token(row.get("mode")).lower(),
        "quarantine_enabled": bool(row.get("quarantine_enabled", False)),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
        "extensions": dict(_as_map(row.get("extensions"))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_gc_report(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    normalized = {
        "report_id": _token(row.get("report_id")),
        "gc_policy_id": _token(row.get("gc_policy_id")),
        "reachable_hashes": sorted({_token(value) for value in list(row.get("reachable_hashes") or []) if _token(value)}),
        "deleted_hashes": sorted({_token(value) for value in list(row.get("deleted_hashes") or []) if _token(value)}),
        "quarantined_hashes": sorted({_token(value) for value in list(row.get("quarantined_hashes") or []) if _token(value)}),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
        "extensions": dict(_as_map(row.get("extensions"))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def load_gc_policy_registry(repo_root: str) -> dict:
    payload = _read_json(os.path.join(_norm(repo_root), DEFAULT_GC_POLICY_REGISTRY_REL.replace("/", os.sep)))
    record = _as_map(payload.get("record"))
    rows = [
        canonicalize_gc_policy(row)
        for row in list(record.get("gc_policies") or [])
        if _token(_as_map(row).get("gc_policy_id"))
    ]
    payload["record"] = {
        "registry_id": _token(record.get("registry_id")) or "dominium.registry.gc_policy_registry",
        "registry_version": _token(record.get("registry_version")) or "1.0.0",
        "gc_policies": sorted(rows, key=lambda row: _token(row.get("gc_policy_id"))),
        "extensions": dict(_as_map(record.get("extensions"))),
    }
    return payload


def select_gc_policy(registry: Mapping[str, object] | None, gc_policy_id: str) -> dict:
    for row in list(_as_map(_as_map(registry).get("record")).get("gc_policies") or []):
        item = canonicalize_gc_policy(row)
        if _token(item.get("gc_policy_id")) == _token(gc_policy_id):
            return item
    return {}


def resolve_store_root_from_install(install_root: str, install_manifest: Mapping[str, object] | None) -> str:
    manifest = _as_map(install_manifest)
    locator = _as_map(manifest.get("store_root_ref")) or _as_map(manifest.get("store_root"))
    manifest_ref = _token(locator.get("manifest_ref"))
    root_path = _token(locator.get("root_path"))
    if manifest_ref:
        manifest_abs = manifest_ref if os.path.isabs(manifest_ref) else os.path.join(_norm(install_root), manifest_ref.replace("/", os.sep))
        return os.path.dirname(_norm(manifest_abs))
    if root_path:
        return _norm(root_path if os.path.isabs(root_path) else os.path.join(_norm(install_root), root_path.replace("/", os.sep)))
    return ""


def _portable_mode_for_store(store_root: str, install_sources: Sequence[Mapping[str, object]] | None) -> bool:
    for row in list(install_sources or []):
        install_root = _token(_as_map(row).get("install_root"))
        if not install_root:
            continue
        manifest = _read_json(os.path.join(_norm(install_root), "install.manifest.json"))
        if _token(_as_map(manifest).get("mode")).lower() == "portable":
            resolved = resolve_store_root_from_install(install_root, manifest)
            if _norm(resolved) == _norm(store_root):
                return True
    return False


def _manifest_error(code: str, path: str, message: str, *, store_root: str = "") -> dict:
    rel_path = _rel_from(path, store_root) if _token(store_root) else _norm_rel(path)
    return {"code": _token(code), "path": rel_path, "message": _token(message)}


def _quarantined_tokens(store_root: str) -> list[str]:
    root = _norm(store_root)
    rows: list[str] = []
    for category in STORE_CATEGORY_IDS:
        category_root = os.path.join(root, STORE_LAYOUT_DIRNAME, QUARANTINE_DIRNAME, category)
        if not os.path.isdir(category_root):
            continue
        for name in sorted(os.listdir(category_root)):
            abs_path = os.path.join(category_root, name)
            if not os.path.isdir(abs_path):
                continue
            rows.append(store_artifact_token(category, name))
    return sorted(rows)


def verify_store_root(store_root: str) -> dict:
    root = _norm(store_root)
    errors: list[dict] = []
    verified_tokens: list[str] = []
    root_manifest_path = os.path.join(root, STORE_ROOT_MANIFEST)
    root_manifest = _read_json(root_manifest_path)
    if not os.path.isfile(root_manifest_path):
        errors.append(_manifest_error("refusal.store.missing_root_manifest", root_manifest_path, "store.root.json is missing", store_root=root))
    for row in scan_store_artifacts(root):
        category = _token(row.get("category"))
        artifact_hash = _token(row.get("artifact_hash")).lower()
        artifact_root = _artifact_root(root, category, artifact_hash)
        manifest_path = os.path.join(artifact_root, ARTIFACT_MANIFEST_NAME)
        token = store_artifact_token(category, artifact_hash)
        if not bool(row.get("is_hash_directory")):
            errors.append(_manifest_error("refusal.store.invalid_hash_directory", artifact_root, "store artifact directory name must be a sha256 token", store_root=root))
            continue
        if not os.path.isfile(manifest_path):
            errors.append(_manifest_error("refusal.store.partial_write", manifest_path, "artifact.manifest.json is missing", store_root=root))
            continue
        manifest = _read_json(manifest_path)
        if _token(manifest.get("artifact_hash")).lower() != artifact_hash:
            errors.append(_manifest_error("refusal.store.hash_mismatch", manifest_path, "artifact manifest hash does not match directory name", store_root=root))
            continue
        if _token(manifest.get("category")).lower() != category:
            errors.append(_manifest_error("refusal.store.category_mismatch", manifest_path, "artifact manifest category does not match directory layout", store_root=root))
            continue
        artifact_type = _token(manifest.get("artifact_type")).lower()
        if artifact_type == "json":
            payload_path = os.path.join(artifact_root, ARTIFACT_JSON_PAYLOAD)
            if not os.path.isfile(payload_path):
                errors.append(_manifest_error("refusal.store.partial_write", payload_path, "json artifact payload is missing", store_root=root))
                continue
            payload = _read_json(payload_path)
            actual_hash = _json_artifact_hash(payload_path)
            declared_hash = _token(_as_map(payload).get("pack_lock_hash")).lower() if category == "locks" else ""
        elif artifact_type == "tree":
            payload_root = os.path.join(artifact_root, ARTIFACT_TREE_PAYLOAD)
            if not os.path.isdir(payload_root):
                errors.append(_manifest_error("refusal.store.partial_write", payload_root, "tree artifact payload directory is missing", store_root=root))
                continue
            actual_hash = _tree_artifact_hash(payload_root)
            declared_hash = ""
        else:
            errors.append(_manifest_error("refusal.store.unknown_artifact_type", manifest_path, "artifact type is not supported", store_root=root))
            continue
        if actual_hash != artifact_hash and declared_hash != artifact_hash:
            errors.append(_manifest_error("refusal.store.hash_mismatch", artifact_root, "artifact content does not match canonical hash", store_root=root))
            continue
        verified_tokens.append(token)
    report = {
        "report_id": "store.verify.v1",
        "result": "complete" if not errors else "refused",
        "store_id": _token(root_manifest.get("store_id")) or "store.default",
        "store_root_label": "store",
        "registry_path": os.path.basename(default_install_registry_path(root)),
        "verified_hashes": sorted(verified_tokens),
        "quarantined_hashes": _quarantined_tokens(root),
        "artifact_count": int(len(scan_store_artifacts(root))),
        "errors": sorted(errors, key=lambda row: (_token(row.get("path")), _token(row.get("code")), _token(row.get("message")))),
        "warnings": [],
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _quarantine_root(store_root: str, category: str, artifact_hash: str) -> str:
    return os.path.join(_norm(store_root), STORE_LAYOUT_DIRNAME, QUARANTINE_DIRNAME, _token(category).lower(), _token(artifact_hash).lower())


def run_store_gc(
    store_root: str,
    *,
    repo_root: str = ".",
    gc_policy_id: str = DEFAULT_GC_POLICY_ID,
    install_roots: Sequence[str] | None = None,
    registry_path: str = "",
    allow_aggressive: bool = False,
    allow_portable: bool = False,
) -> dict:
    target_root = _norm(store_root)
    install_source_rows = _discover_install_sources(repo_root, target_root, explicit_install_roots=install_roots, registry_path=registry_path)
    verify_report = verify_store_root(target_root)
    if _token(verify_report.get("result")) != "complete":
        return {
            "result": "refused",
            "refusal_code": REFUSAL_GC_VERIFY_FAILED,
            "message": "store verification failed before GC",
            "remediation": "Run `python tools/lib/tool_store_verify.py --store-root {}` and repair the reported corruption before retrying GC.".format(_norm_rel(target_root)),
            "store_verify_report": verify_report,
        }

    policy_registry = load_gc_policy_registry(repo_root)
    gc_policy = select_gc_policy(policy_registry, gc_policy_id)
    if not gc_policy:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_GC_POLICY_UNKNOWN,
            "message": "gc policy is not declared",
            "remediation": "Use one of gc.none, gc.safe, or gc.aggressive.",
            "store_verify_report": verify_report,
        }

    reachability_report = build_store_reachability_report(
        target_root,
        repo_root=repo_root,
        install_roots=install_roots,
        registry_path=registry_path,
    )
    if _portable_mode_for_store(target_root, install_source_rows) and not allow_portable:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_GC_PORTABLE,
            "message": "portable stores are protected from GC by default",
            "remediation": "Rerun with --allow-portable-store only if you intend to mutate the portable bundle store explicitly.",
            "gc_policy": gc_policy,
            "store_verify_report": verify_report,
            "reachability_report": reachability_report,
        }

    policy_mode = _token(gc_policy.get("mode")).lower()
    if policy_mode == GC_MODE_AGGRESSIVE and not allow_aggressive:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_GC_EXPLICIT_FLAG,
            "message": "aggressive GC requires an explicit flag",
            "remediation": "Rerun with --allow-aggressive if immediate deletion is intended, or use --policy gc.safe for quarantine-backed cleanup.",
            "gc_policy": gc_policy,
            "store_verify_report": verify_report,
            "reachability_report": reachability_report,
        }

    reachable_tokens = sorted(_token(value) for value in list(reachability_report.get("reachable_hashes") or []) if _token(value))
    present_tokens = sorted(_token(row.get("artifact_token")) for row in scan_store_artifacts(target_root) if _token(row.get("artifact_token")))
    candidate_tokens = sorted(set(present_tokens) - set(reachable_tokens))
    deleted_tokens: list[str] = []
    quarantined_tokens: list[str] = []
    actions: list[dict] = []

    for token in candidate_tokens:
        category, artifact_hash = parse_artifact_token(token)
        source_root = _artifact_root(target_root, category, artifact_hash)
        if not os.path.isdir(source_root):
            continue
        if policy_mode == GC_MODE_NONE:
            actions.append({"artifact_token": token, "action": "report_only"})
            continue
        if policy_mode == GC_MODE_SAFE:
            target_path = _quarantine_root(target_root, category, artifact_hash)
            if os.path.exists(target_path):
                return {
                    "result": "refused",
                    "refusal_code": REFUSAL_GC_QUARANTINE_CONFLICT,
                    "message": "quarantine target already exists",
                    "remediation": "Inspect and clear the quarantine entry at `{}` before rerunning safe GC.".format(_norm_rel(target_path)),
                    "gc_policy": gc_policy,
                    "store_verify_report": verify_report,
                    "reachability_report": reachability_report,
                }
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            os.replace(source_root, target_path)
            quarantined_tokens.append(token)
            actions.append({"artifact_token": token, "action": "quarantined", "target_path": _rel_from(target_path, target_root)})
            continue
        if policy_mode == GC_MODE_AGGRESSIVE:
            shutil.rmtree(source_root, ignore_errors=False)
            deleted_tokens.append(token)
            actions.append({"artifact_token": token, "action": "deleted"})

    report = canonicalize_gc_report(
        {
            "report_id": "store.gc.{}.{}".format(
                _token(gc_policy.get("gc_policy_id")).replace(".", "_"),
                canonical_sha256(
                    {
                        "store_id": _token(verify_report.get("store_id")) or "store.default",
                        "reachable": reachable_tokens,
                        "deleted": deleted_tokens,
                        "quarantined": quarantined_tokens,
                    }
                )[:16],
            ),
            "gc_policy_id": _token(gc_policy.get("gc_policy_id")),
            "reachable_hashes": reachable_tokens,
            "deleted_hashes": deleted_tokens,
            "quarantined_hashes": quarantined_tokens,
            "extensions": {
                "candidate_hashes": candidate_tokens,
                "store_verify_fingerprint": _token(verify_report.get("deterministic_fingerprint")),
                "reachability_fingerprint": _token(reachability_report.get("deterministic_fingerprint")),
                "actions": actions,
                "store_id": _token(verify_report.get("store_id")) or "store.default",
            },
        }
    )
    return {
        "result": "complete",
        "gc_policy": gc_policy,
        "gc_report": report,
        "reachability_report": reachability_report,
        "store_verify_report": verify_report,
    }


__all__ = [
    "DEFAULT_GC_POLICY_ID",
    "DEFAULT_GC_POLICY_REGISTRY_REL",
    "GC_MODE_AGGRESSIVE",
    "GC_MODE_NONE",
    "GC_MODE_SAFE",
    "REFUSAL_GC_EXPLICIT_FLAG",
    "REFUSAL_GC_POLICY_UNKNOWN",
    "REFUSAL_GC_PORTABLE",
    "REFUSAL_GC_QUARANTINE_CONFLICT",
    "REFUSAL_GC_VERIFY_FAILED",
    "canonicalize_gc_policy",
    "canonicalize_gc_report",
    "deterministic_fingerprint",
    "load_gc_policy_registry",
    "resolve_store_root_from_install",
    "run_store_gc",
    "select_gc_policy",
    "verify_store_root",
]
