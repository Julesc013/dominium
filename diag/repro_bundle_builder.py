"""Deterministic DIAG-0 repro bundle capture and verification."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from typing import Mapping, Sequence

from appshell.paths import VROOT_EXPORTS, get_current_virtual_paths, vpath_resolve
from meta_extensions_engine import normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import norm, write_canonical_json


REPRO_BUNDLE_VERSION = "1.0.0"
DEFAULT_CAPTURE_WINDOW = 32
_SECRET_KEY_FRAGMENTS = (
    "account_secret",
    "auth_token",
    "credential",
    "machine_id",
    "password",
    "private_key",
    "secret",
    "signing_key",
    "token",
)
_LIB6_BUNDLE_MANIFEST = "bundle.manifest.json"
_LIB6_BUNDLE_HASH_INDEX = os.path.join("hashes", "content.sha256.json")


def _sanitize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        sanitized = {}
        for raw_key, raw_item in sorted(value.items(), key=lambda pair: str(pair[0])):
            key = str(raw_key)
            lowered = key.lower()
            if any(fragment in lowered for fragment in _SECRET_KEY_FRAGMENTS):
                continue
            sanitized[key] = _sanitize_tree(raw_item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_tree(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_tree(item) for item in value]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def _normalize_tree(value: object) -> object:
    return normalize_extensions_tree(_sanitize_tree(value))


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _repo_abs(repo_root: str, value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token)))


def _find_related_bundle_roots(paths: Sequence[str]) -> list[str]:
    roots: list[str] = []
    seen = set()
    for raw_path in list(paths or []):
        token = str(raw_path or "").strip()
        if not token:
            continue
        current = os.path.normpath(os.path.abspath(token))
        if os.path.isfile(current):
            current = os.path.dirname(current)
        while current and os.path.isdir(current):
            manifest_path = os.path.join(current, _LIB6_BUNDLE_MANIFEST)
            if os.path.isfile(manifest_path):
                norm_root = os.path.normpath(os.path.abspath(current))
                if norm_root not in seen:
                    seen.add(norm_root)
                    roots.append(norm_root)
                break
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
    return sorted(roots)


def _related_bundle_files(bundle_dir: str, candidate_paths: Sequence[str]) -> list[tuple[str, str]]:
    files: list[tuple[str, str]] = []
    for index, bundle_root in enumerate(_find_related_bundle_roots(candidate_paths), start=1):
        manifest = _read_json(os.path.join(bundle_root, _LIB6_BUNDLE_MANIFEST))
        bundle_id = str(manifest.get("bundle_id", "")).strip() or "bundle.{:02d}".format(index)
        safe_id = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in bundle_id)
        rel_manifest = os.path.join("related_bundles", safe_id, _LIB6_BUNDLE_MANIFEST)
        dest_manifest = os.path.join(bundle_dir, rel_manifest)
        os.makedirs(os.path.dirname(dest_manifest), exist_ok=True)
        shutil.copyfile(os.path.join(bundle_root, _LIB6_BUNDLE_MANIFEST), dest_manifest)
        files.append((rel_manifest, dest_manifest))
        hash_index_src = os.path.join(bundle_root, _LIB6_BUNDLE_HASH_INDEX)
        if os.path.isfile(hash_index_src):
            rel_index = os.path.join("related_bundles", safe_id, _LIB6_BUNDLE_HASH_INDEX)
            dest_index = os.path.join(bundle_dir, rel_index)
            os.makedirs(os.path.dirname(dest_index), exist_ok=True)
            shutil.copyfile(hash_index_src, dest_index)
            files.append((rel_index, dest_index))
    return files


def _read_json(path: str) -> dict:
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return dict(_normalize_tree(payload))


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    abs_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    write_canonical_json(abs_path, dict(_normalize_tree(dict(payload or {}))))
    return abs_path


def _write_jsonl(path: str, rows: Sequence[Mapping[str, object]]) -> str:
    abs_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        for row in list(rows or []):
            handle.write(json.dumps(_normalize_tree(dict(row)), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            handle.write("\n")
    return abs_path


def _minimum_observability_payload(kind: str) -> dict:
    payload = {
        "result": "unavailable",
        "reason": "not_captured",
        "artifact_kind": str(kind or "").strip(),
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _file_hash(abs_path: str) -> str:
    try:
        with open(abs_path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return ""


def _collect_proof_rows(proof_anchor_dir: str, proof_anchor_rows: Sequence[Mapping[str, object]], limit: int) -> list[dict]:
    if proof_anchor_rows:
        rows = [dict(_normalize_tree(dict(row))) for row in list(proof_anchor_rows or [])]
        return rows[-max(0, int(limit or 0)) :]
    root = os.path.normpath(os.path.abspath(str(proof_anchor_dir or "")))
    if not root or not os.path.isdir(root):
        return []
    rows = []
    names = sorted(entry for entry in os.listdir(root) if entry.endswith(".json"))
    for name in names[-max(0, int(limit or 0)) :]:
        payload = _read_json(os.path.join(root, name))
        if payload:
            rows.append(payload)
    return rows


def _canonical_rows(rows: Sequence[Mapping[str, object]], limit: int) -> list[dict]:
    normalized = [dict(_normalize_tree(dict(row))) for row in list(rows or []) if isinstance(row, Mapping)]
    normalized = sorted(
        normalized,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("event_id", "")),
            str(row.get("proof_anchor_id", "")),
            canonical_sha256(row),
        ),
    )
    return normalized[-max(0, int(limit or 0)) :]


def _bundle_environment_summary() -> dict:
    version_tuple = platform.python_version_tuple()
    return {
        "cpu_arch": str(platform.machine() or "").strip(),
        "os_family": str(platform.system() or "").strip(),
        "os_version": str(platform.release() or "").strip(),
        "python_major": "{}.{}".format(version_tuple[0], version_tuple[1]),
    }


def _pack_hash_summary(pack_lock_payload: Mapping[str, object]) -> dict:
    payload = dict(_normalize_tree(dict(pack_lock_payload or {})))
    return {
        "pack_compat_hashes": dict(payload.get("pack_compat_hashes") or {}),
        "pack_hashes": dict(payload.get("pack_hashes") or {}),
        "ordered_pack_ids": list(payload.get("ordered_pack_ids") or []),
        "ordered_pack_versions": list(payload.get("ordered_pack_versions") or []),
    }


def _index_payload(*, file_rows: Sequence[Mapping[str, object]], bundle_hash: str) -> dict:
    payload = {
        "schema_version": REPRO_BUNDLE_VERSION,
        "bundle_version": REPRO_BUNDLE_VERSION,
        "file_count": int(len(list(file_rows or []))),
        "files": [dict(_normalize_tree(dict(row))) for row in list(file_rows or [])],
        "bundle_hash": str(bundle_hash).strip(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _manifest_payload(
    *,
    created_by_product_id: str,
    build_id: str,
    seed: str,
    session_template_id: str,
    session_id: str,
    contract_bundle_hash: str,
    semantic_contract_registry_hash: str,
    pack_lock_hash: str,
    overlay_manifest_hash: str,
    included_artifacts: Sequence[str],
    bundle_hash: str,
    proof_anchor_count: int,
    canonical_event_count: int,
    log_event_count: int,
    view_fingerprint_count: int,
    proof_window_hash: str,
    canonical_event_hash: str,
    log_window_hash: str,
    environment_summary: Mapping[str, object],
) -> dict:
    payload = {
        "schema_version": REPRO_BUNDLE_VERSION,
        "bundle_version": REPRO_BUNDLE_VERSION,
        "created_by_product_id": str(created_by_product_id).strip(),
        "build_id": str(build_id).strip(),
        "seed": str(seed or "").strip(),
        "session_id": str(session_id or "").strip(),
        "session_template_id": str(session_template_id or "").strip(),
        "contract_bundle_hash": str(contract_bundle_hash or "").strip(),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash or "").strip(),
        "pack_lock_hash": str(pack_lock_hash or "").strip(),
        "overlay_manifest_hash": str(overlay_manifest_hash or "").strip(),
        "proof_anchor_count": int(proof_anchor_count),
        "canonical_event_count": int(canonical_event_count),
        "log_event_count": int(log_event_count),
        "view_fingerprint_count": int(view_fingerprint_count),
        "proof_window_hash": str(proof_window_hash).strip(),
        "canonical_event_hash": str(canonical_event_hash).strip(),
        "log_window_hash": str(log_window_hash).strip(),
        "environment_summary": dict(_normalize_tree(dict(environment_summary or {}))),
        "included_artifacts": [str(item).replace("\\", "/") for item in sorted(set(str(item) for item in list(included_artifacts or [])))],
        "bundle_hash": str(bundle_hash).strip(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _replay_request_payload(*, bundle_path: str, tick_window: int, include_views: bool) -> dict:
    payload = {
        "schema_version": REPRO_BUNDLE_VERSION,
        "bundle_path": str(bundle_path).replace("\\", "/"),
        "tick_window": int(max(0, int(tick_window or 0))),
        "include_views": bool(include_views),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _replay_result_payload(
    *,
    bundle_hash: str,
    hash_match: bool,
    proof_hash_match: bool,
    mismatch_details: Sequence[Mapping[str, object]],
) -> dict:
    sorted_mismatches = sorted(
        [dict(_normalize_tree(dict(row))) for row in list(mismatch_details or [])],
        key=lambda row: (
            str(row.get("kind", "")).strip(),
            str(row.get("rel_path", "")).strip(),
            str(row.get("expected_hash", "")).strip(),
            str(row.get("actual_hash", "")).strip(),
            canonical_sha256(row),
        ),
    )
    payload = {
        "schema_version": REPRO_BUNDLE_VERSION,
        "bundle_hash": str(bundle_hash).strip(),
        "hash_match": bool(hash_match),
        "proof_hash_match": bool(proof_hash_match),
        "mismatch_details": sorted_mismatches,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def write_repro_bundle(
    *,
    repo_root: str,
    created_by_product_id: str,
    build_id: str = "",
    out_dir: str = "",
    window: int = DEFAULT_CAPTURE_WINDOW,
    include_views: bool = False,
    descriptor_payloads: Sequence[Mapping[str, object]] | None = None,
    run_manifest_payload: Mapping[str, object] | None = None,
    run_manifest_path: str = "",
    session_spec_payload: Mapping[str, object] | None = None,
    session_spec_path: str = "",
    contract_bundle_payload: Mapping[str, object] | None = None,
    contract_bundle_path: str = "",
    pack_lock_payload: Mapping[str, object] | None = None,
    pack_lock_path: str = "",
    semantic_contract_registry_hash: str = "",
    contract_bundle_hash: str = "",
    overlay_manifest_hash: str = "",
    pack_verification_report_payload: Mapping[str, object] | None = None,
    pack_verification_report_path: str = "",
    install_plan_payload: Mapping[str, object] | None = None,
    install_plan_path: str = "",
    update_plan_payload: Mapping[str, object] | None = None,
    update_plan_path: str = "",
    seed: str = "",
    session_id: str = "",
    session_template_id: str = "",
    proof_anchor_rows: Sequence[Mapping[str, object]] | None = None,
    proof_anchor_dir: str = "",
    canonical_event_rows: Sequence[Mapping[str, object]] | None = None,
    log_events: Sequence[Mapping[str, object]] | None = None,
    ipc_attach_rows: Sequence[Mapping[str, object]] | None = None,
    negotiation_records: Sequence[Mapping[str, object]] | None = None,
    view_fingerprints: Sequence[Mapping[str, object]] | None = None,
    environment_summary: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    context = get_current_virtual_paths()
    bundle_dir = os.path.normpath(
        os.path.abspath(
            str(out_dir)
            if str(out_dir or "").strip()
            else (
                vpath_resolve(VROOT_EXPORTS, os.path.join("diag", str(created_by_product_id or "product")), context)
                if context is not None and str(context.get("result", "")).strip() == "complete"
                else os.path.join(repo_root_abs, "build", "diag", str(created_by_product_id or "product"))
            )
        )
    )
    os.makedirs(bundle_dir, exist_ok=True)
    tick_window = max(0, int(window or DEFAULT_CAPTURE_WINDOW))

    session_spec_abs = _repo_abs(repo_root_abs, session_spec_path)
    pack_lock_abs = _repo_abs(repo_root_abs, pack_lock_path)
    contract_bundle_abs = _repo_abs(repo_root_abs, contract_bundle_path)
    run_manifest_abs = _repo_abs(repo_root_abs, run_manifest_path)
    pack_verification_report_abs = _repo_abs(repo_root_abs, pack_verification_report_path)
    install_plan_abs = _repo_abs(repo_root_abs, install_plan_path)
    update_plan_abs = _repo_abs(repo_root_abs, update_plan_path)

    session_spec_map = dict(_normalize_tree(dict(session_spec_payload or _read_json(session_spec_abs))))
    pack_lock_map = dict(_normalize_tree(dict(pack_lock_payload or _read_json(pack_lock_abs))))
    contract_bundle_map = dict(_normalize_tree(dict(contract_bundle_payload or _read_json(contract_bundle_abs))))
    run_manifest_map = dict(_normalize_tree(dict(run_manifest_payload or _read_json(run_manifest_abs))))
    pack_verification_report_map = dict(
        _normalize_tree(
            dict(pack_verification_report_payload or _read_json(pack_verification_report_abs) or _minimum_observability_payload("pack_verification_report"))
        )
    )
    install_plan_map = dict(
        _normalize_tree(
            dict(install_plan_payload or _read_json(install_plan_abs) or _minimum_observability_payload("install_plan"))
        )
    )
    update_plan_map = dict(
        _normalize_tree(
            dict(update_plan_payload or _read_json(update_plan_abs) or _minimum_observability_payload("update_plan"))
        )
    )

    selected_contract_bundle_hash = (
        str(contract_bundle_hash or "").strip()
        or str(session_spec_map.get("contract_bundle_hash", "")).strip()
        or str(session_spec_map.get("semantic_contract_bundle_hash", "")).strip()
        or str(contract_bundle_map.get("deterministic_fingerprint", "")).strip()
    )
    selected_semantic_registry_hash = (
        str(semantic_contract_registry_hash or "").strip()
        or str(session_spec_map.get("semantic_contract_registry_hash", "")).strip()
        or str(((dict((list(descriptor_payloads or [{}])[0]) or {}).get("descriptor") or {}).get("extensions", {}) or {}).get("official.semantic_contract_registry_hash", "")).strip()
    )
    selected_pack_lock_hash = (
        str(pack_lock_map.get("pack_lock_hash", "")).strip()
        or str(session_spec_map.get("pack_lock_hash", "")).strip()
    )
    selected_overlay_manifest_hash = (
        str(overlay_manifest_hash or "").strip()
        or str(run_manifest_map.get("overlay_manifest_hash", "")).strip()
        or str((dict(run_manifest_map.get("extensions") or {})).get("official.overlay_manifest_hash", "")).strip()
    )
    selected_seed = (
        str(seed or "").strip()
        or str(run_manifest_map.get("seed", "")).strip()
        or str(session_spec_map.get("selected_seed", "")).strip()
    )
    selected_session_id = (
        str(session_id or "").strip()
        or str(run_manifest_map.get("manifest_id", "")).strip()
        or str(session_spec_map.get("save_id", "")).strip()
    )
    selected_session_template_id = (
        str(session_template_id or "").strip()
        or str(run_manifest_map.get("session_template_id", "")).strip()
        or str(session_spec_map.get("template_id", "")).strip()
        or str(session_spec_map.get("session_template_id", "")).strip()
    )

    proof_rows = _collect_proof_rows(proof_anchor_dir, proof_anchor_rows or [], tick_window)
    canonical_rows = _canonical_rows(canonical_event_rows or [], tick_window)
    log_rows = _canonical_rows(log_events or [], tick_window)
    attach_rows = _canonical_rows(ipc_attach_rows or [], tick_window)
    negotiation_rows = _canonical_rows(negotiation_records or [], tick_window)
    view_rows = _canonical_rows(view_fingerprints or [], tick_window) if include_views else []

    bundle_files: list[tuple[str, str]] = []
    for index, descriptor_payload in enumerate(list(descriptor_payloads or []), start=1):
        rel = os.path.join("descriptors", "endpoint_descriptor.{:02d}.json".format(index))
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), descriptor_payload)))
    if session_spec_map:
        rel = os.path.join("session", "session_spec.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), session_spec_map)))
    if contract_bundle_map:
        rel = os.path.join("session", "universe_contract_bundle.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), contract_bundle_map)))
    bundle_files.append(
        (
            os.path.join("session", "session_context.json"),
            _write_json(
                os.path.join(bundle_dir, "session", "session_context.json"),
                {
                    "semantic_contract_registry_hash": selected_semantic_registry_hash,
                    "contract_bundle_hash": selected_contract_bundle_hash,
                    "seed": selected_seed,
                    "session_template_id": selected_session_template_id,
                    "overlay_manifest_hash": selected_overlay_manifest_hash,
                    "session_id": selected_session_id,
                },
            ),
        )
    )
    if pack_lock_map:
        rel = os.path.join("packs", "pack_lock.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), pack_lock_map)))
        rel = os.path.join("packs", "pack_hashes.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), _pack_hash_summary(pack_lock_map))))
    bundle_files.append(
        (
            os.path.join("packs", "pack_verification_report.json"),
            _write_json(os.path.join(bundle_dir, "packs", "pack_verification_report.json"), pack_verification_report_map),
        )
    )
    if run_manifest_map:
        rel = os.path.join("run", "run_manifest.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), run_manifest_map)))
    bundle_files.append(
        (
            os.path.join("plans", "install_plan.json"),
            _write_json(os.path.join(bundle_dir, "plans", "install_plan.json"), install_plan_map),
        )
    )
    bundle_files.append(
        (
            os.path.join("plans", "update_plan.json"),
            _write_json(os.path.join(bundle_dir, "plans", "update_plan.json"), update_plan_map),
        )
    )
    bundle_files.extend(
        _related_bundle_files(
            bundle_dir,
            [session_spec_abs, pack_lock_abs, contract_bundle_abs, run_manifest_abs],
        )
    )

    bundle_files.append(
        (
            os.path.join("proofs", "proof_anchors.json"),
            _write_json(os.path.join(bundle_dir, "proofs", "proof_anchors.json"), {"proof_anchors": proof_rows}),
        )
    )
    bundle_files.append(
        (
            os.path.join("events", "canonical_events.json"),
            _write_json(os.path.join(bundle_dir, "events", "canonical_events.json"), {"canonical_events": canonical_rows}),
        )
    )
    bundle_files.append(
        (
            os.path.join("events", "ipc_attach_records.json"),
            _write_json(os.path.join(bundle_dir, "events", "ipc_attach_records.json"), {"ipc_attach_records": attach_rows}),
        )
    )
    bundle_files.append(
        (
            os.path.join("events", "negotiation_records.json"),
            _write_json(os.path.join(bundle_dir, "events", "negotiation_records.json"), {"negotiation_records": negotiation_rows}),
        )
    )
    bundle_files.append(
        (
            os.path.join("logs", "log_events.jsonl"),
            _write_jsonl(os.path.join(bundle_dir, "logs", "log_events.jsonl"), log_rows),
        )
    )
    if view_rows:
        rel = os.path.join("views", "view_fingerprints.json")
        bundle_files.append((rel, _write_json(os.path.join(bundle_dir, rel), {"view_fingerprints": view_rows})))
    bundle_files.append(
        (
            os.path.join("replay", "replay_request.json"),
            _write_json(
                os.path.join(bundle_dir, "replay", "replay_request.json"),
                _replay_request_payload(bundle_path=".", tick_window=tick_window, include_views=include_views),
            ),
        )
    )

    file_rows = []
    for rel_path, abs_path in sorted(bundle_files, key=lambda item: item[0].replace("\\", "/")):
        file_rows.append(
            {
                "rel_path": rel_path.replace("\\", "/"),
                "content_hash": _file_hash(abs_path),
                "size_bytes": int(os.path.getsize(abs_path)),
            }
        )
    bundle_hash = canonical_sha256({"files": file_rows})
    bundle_index = _index_payload(file_rows=file_rows, bundle_hash=bundle_hash)
    bundle_index_path = _write_json(os.path.join(bundle_dir, "bundle_index.json"), bundle_index)
    manifest = _manifest_payload(
        created_by_product_id=created_by_product_id,
        build_id=build_id,
        seed=selected_seed,
        session_template_id=selected_session_template_id,
        session_id=selected_session_id,
        contract_bundle_hash=selected_contract_bundle_hash,
        semantic_contract_registry_hash=selected_semantic_registry_hash,
        pack_lock_hash=selected_pack_lock_hash,
        overlay_manifest_hash=selected_overlay_manifest_hash,
        included_artifacts=[row["rel_path"] for row in file_rows] + ["bundle_index.json"],
        bundle_hash=bundle_hash,
        proof_anchor_count=len(proof_rows),
        canonical_event_count=len(canonical_rows),
        log_event_count=len(log_rows),
        view_fingerprint_count=len(view_rows),
        proof_window_hash=canonical_sha256(proof_rows),
        canonical_event_hash=canonical_sha256(canonical_rows),
        log_window_hash=canonical_sha256(log_rows),
        environment_summary=dict(environment_summary or _bundle_environment_summary()),
    )
    manifest_path = _write_json(os.path.join(bundle_dir, "manifest.json"), manifest)
    validate_instance(repo_root=repo_root_abs, schema_name="repro_bundle_manifest", payload=manifest, strict_top_level=True)
    validate_instance(repo_root=repo_root_abs, schema_name="repro_bundle_index", payload=bundle_index, strict_top_level=True)
    return {
        "result": "complete",
        "bundle_dir": norm(bundle_dir),
        "manifest_path": norm(manifest_path),
        "bundle_index_path": norm(bundle_index_path),
        "bundle_hash": bundle_hash,
        "manifest": manifest,
        "bundle_index": bundle_index,
    }


def verify_repro_bundle(*, repo_root: str, bundle_path: str, tick_window: int = DEFAULT_CAPTURE_WINDOW) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    bundle_dir = _repo_abs(repo_root_abs, bundle_path)
    manifest = _read_json(os.path.join(bundle_dir, "manifest.json"))
    bundle_index = _read_json(os.path.join(bundle_dir, "bundle_index.json"))
    mismatches = []
    file_rows = []
    for row in list(bundle_index.get("files") or []):
        row_map = dict(row or {})
        rel_path = str(row_map.get("rel_path", "")).replace("/", os.sep)
        abs_path = os.path.join(bundle_dir, rel_path)
        actual_hash = _file_hash(abs_path)
        expected_hash = str(row_map.get("content_hash", "")).strip()
        if actual_hash != expected_hash:
            mismatches.append(
                {
                    "kind": "content_hash_mismatch",
                    "rel_path": str(row_map.get("rel_path", "")).replace("\\", "/"),
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                }
            )
        file_rows.append(
            {
                "rel_path": str(row_map.get("rel_path", "")).replace("\\", "/"),
                "content_hash": actual_hash,
                "size_bytes": int(row_map.get("size_bytes", 0) or 0),
            }
        )
    recomputed_bundle_hash = canonical_sha256({"files": sorted(file_rows, key=lambda row: row["rel_path"])})
    manifest_bundle_hash = str(manifest.get("bundle_hash", "")).strip()
    index_bundle_hash = str(bundle_index.get("bundle_hash", "")).strip()
    bundle_hash_match = bool(recomputed_bundle_hash) and recomputed_bundle_hash == manifest_bundle_hash == index_bundle_hash
    if not bundle_hash_match:
        mismatches.append(
            {
                "kind": "bundle_hash_mismatch",
                "expected_hash": manifest_bundle_hash,
                "index_hash": index_bundle_hash,
                "actual_hash": recomputed_bundle_hash,
            }
        )
    proof_payload = _read_json(os.path.join(bundle_dir, "proofs", "proof_anchors.json"))
    proof_rows = list(proof_payload.get("proof_anchors") or [])
    proof_window = proof_rows[-max(0, int(tick_window or 0)) :]
    proof_window_hash = canonical_sha256(proof_window)
    proof_hash_match = proof_window_hash == str(manifest.get("proof_window_hash", "")).strip()
    if not proof_hash_match:
        mismatches.append(
            {
                "kind": "proof_window_hash_mismatch",
                "expected_hash": str(manifest.get("proof_window_hash", "")).strip(),
                "actual_hash": proof_window_hash,
            }
        )
    canonical_payload = _read_json(os.path.join(bundle_dir, "events", "canonical_events.json"))
    canonical_rows = list(canonical_payload.get("canonical_events") or [])
    if canonical_sha256(canonical_rows) != str(manifest.get("canonical_event_hash", "")).strip():
        mismatches.append(
            {
                "kind": "canonical_event_hash_mismatch",
                "expected_hash": str(manifest.get("canonical_event_hash", "")).strip(),
                "actual_hash": canonical_sha256(canonical_rows),
            }
        )
    log_path = os.path.join(bundle_dir, "logs", "log_events.jsonl")
    log_rows = []
    try:
        with open(log_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = str(raw_line or "").strip()
                if line:
                    log_rows.append(json.loads(line))
    except (OSError, ValueError):
        pass
    if canonical_sha256(log_rows) != str(manifest.get("log_window_hash", "")).strip():
        mismatches.append(
            {
                "kind": "log_window_hash_mismatch",
                "expected_hash": str(manifest.get("log_window_hash", "")).strip(),
                "actual_hash": canonical_sha256(log_rows),
            }
        )
    all_hashes_match = bool(bundle_hash_match and proof_hash_match and not mismatches)
    replay_result = _replay_result_payload(
        bundle_hash=recomputed_bundle_hash,
        hash_match=all_hashes_match,
        proof_hash_match=proof_hash_match,
        mismatch_details=mismatches,
    )
    validate_instance(repo_root=repo_root_abs, schema_name="replay_result", payload=replay_result, strict_top_level=True)
    result = "complete" if bool(replay_result.get("hash_match", False)) else "refused"
    payload = {
        "result": result,
        "manifest": manifest,
        "bundle_index": bundle_index,
        "replay_result": replay_result,
        "bundle_hash": recomputed_bundle_hash,
    }
    if result != "complete":
        payload["refusal_code"] = "refusal.diag.bundle_hash_mismatch"
        payload["reason"] = "repro bundle replay verification detected a deterministic hash mismatch"
        payload["remediation_hint"] = "Recapture the repro bundle or verify that the replay runtime matches the captured contracts and pack lock."
    return payload


__all__ = [
    "DEFAULT_CAPTURE_WINDOW",
    "REPRO_BUNDLE_VERSION",
    "verify_repro_bundle",
    "write_repro_bundle",
]
