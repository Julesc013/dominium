"""Deterministic DIST-6 version interop helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat.capability_negotiation import (
    COMPAT_MODE_FULL,
    COMPAT_MODE_READ_ONLY,
    COMPAT_MODE_REFUSE,
    build_endpoint_descriptor,
    negotiate_endpoint_descriptors,
    verify_negotiation_record,
)
from src.compat.negotiation.degrade_enforcer import build_degrade_runtime_state
from src.lib.save import (
    deterministic_fingerprint as save_deterministic_fingerprint,
    evaluate_save_open,
    normalize_save_manifest,
    write_json as write_save_json,
)
from src.platform.platform_probe import (
    PLATFORM_ID_LINUX_GTK,
    probe_platform_descriptor,
    project_feature_capabilities_for_platform,
)
from src.universe.universe_identity_builder import build_universe_contract_bundle_payload
from tools.dist.dist_tree_common import (
    DEFAULT_PLATFORM_TAG,
    DEFAULT_RELEASE_CHANNEL,
    build_dist_tree,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DIST6_CASE_IDS = (
    "same_build_same_build",
    "same_build_identical_rebuild",
    "same_version_cross_platform",
    "minor_protocol_drift",
    "pack_lock_mismatch",
    "contract_mismatch_read_only",
    "contract_mismatch_strict",
)
CASE_DOC_TEMPLATE = "docs/audit/DIST6_INTEROP_{}.md"
CASE_JSON_TEMPLATE = "data/audit/dist6_interop_{}.json"
FINAL_DOC_PATH = "docs/audit/DIST6_FINAL.md"
INTEROP_MATRIX_DOC_PATH = "docs/release/INTEROP_MATRIX_v0_0_0_mock.md"
RULE_ID = "INV-VERSION-INTEROP-MUST-PASS-BEFORE-DIST"
DEFAULT_OUTPUT_ROOT_A = os.path.join("build", "tmp", "dist6_interop_a")
DEFAULT_OUTPUT_ROOT_B = os.path.join("build", "tmp", "dist6_interop_b")
DEFAULT_WORK_ROOT = os.path.join("build", "tmp", "dist6_interop")
LAST_REVIEWED = "2026-03-14"
SIMULATED_PLATFORM_ID = PLATFORM_ID_LINUX_GTK


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/").lstrip("./")


def _repo_rel_or_abs(repo_root: str, path: str) -> str:
    abs_path = _norm(path)
    root = _norm(repo_root) if _token(repo_root) else ""
    if root:
        try:
            if os.path.commonpath([root, abs_path]) == root:
                return _norm_rel(os.path.relpath(abs_path, root))
        except ValueError:
            pass
    return _norm_rel(abs_path)


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _extract_json_objects(stdout: str) -> list[dict]:
    rows: list[dict] = []
    decoder = json.JSONDecoder()
    remaining = str(stdout or "").lstrip()
    while remaining:
        try:
            payload, index = decoder.raw_decode(remaining)
        except ValueError:
            newline_index = remaining.find("\n")
            if newline_index < 0:
                break
            remaining = remaining[newline_index + 1 :].lstrip()
            continue
        if isinstance(payload, Mapping):
            rows.append(dict(payload))
        remaining = remaining[index:].lstrip()
    return rows


def _run_bundle_product(bundle_root: str, product_id: str, argv: Sequence[str]) -> dict:
    wrapper_path = os.path.join(_norm(bundle_root), "bin", _token(product_id))
    proc = subprocess.run(
        [sys.executable, wrapper_path] + [str(item) for item in list(argv or [])],
        cwd=_norm(bundle_root),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout_rows = _extract_json_objects(proc.stdout)
    stderr_rows = _extract_json_objects(proc.stderr)
    event_rows = [
        dict(row)
        for row in stdout_rows + stderr_rows
        if _token(_as_map(row).get("event_id"))
    ]
    first_json = {}
    for row in stdout_rows + stderr_rows:
        row_map = _as_map(row)
        if row_map and "event_id" not in row_map:
            first_json = row_map
            break
    return {
        "returncode": int(proc.returncode or 0),
        "stdout": str(proc.stdout or ""),
        "stderr": str(proc.stderr or ""),
        "json_rows": stdout_rows + stderr_rows,
        "event_rows": event_rows,
        "first_json": first_json,
    }


def _bundle_root_from_input(path: str, *, platform_tag: str, channel_id: str) -> str:
    candidate = _norm(path)
    if os.path.isfile(os.path.join(candidate, "install.manifest.json")):
        return candidate
    nested = os.path.join(
        candidate,
        "v0.0.0-{}".format(_token(channel_id) or DEFAULT_RELEASE_CHANNEL),
        _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "dominium",
    )
    if os.path.isfile(os.path.join(nested, "install.manifest.json")):
        return _norm(nested)
    return candidate


def _prepare_bundle(
    repo_root: str,
    *,
    dist_root: str,
    output_root: str,
    platform_tag: str,
    channel_id: str,
) -> dict:
    if _token(dist_root):
        bundle_root = _bundle_root_from_input(dist_root, platform_tag=platform_tag, channel_id=channel_id)
        return {
            "source_kind": "provided",
            "bundle_root": bundle_root,
            "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
            "assembly_report": {},
        }
    report = build_dist_tree(
        repo_root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        channel_id=_token(channel_id) or DEFAULT_RELEASE_CHANNEL,
        output_root=output_root,
    )
    return {
        "source_kind": "built",
        "bundle_root": _norm(report.get("bundle_root_abs", "")),
        "platform_tag": _token(report.get("platform_tag")) or _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "assembly_report": report,
    }


def _load_bundle_json(bundle_root: str, rel_path: str) -> dict:
    return _read_json(os.path.join(_norm(bundle_root), rel_path.replace("/", os.sep)))


def _descriptor_from_bundle(bundle_root: str, product_id: str) -> dict:
    run = _run_bundle_product(bundle_root, product_id, ["--descriptor"])
    payload = _as_map(run.get("first_json"))
    return {
        "run": run,
        "descriptor": payload,
        "descriptor_hash": canonical_sha256(payload) if payload else "",
        "build_id": _token(_as_map(payload.get("extensions")).get("official.build_id")),
        "platform_id": _token(_as_map(payload.get("extensions")).get("official.platform_id")),
        "product_version": _token(payload.get("product_version")),
    }


def _rebuild_descriptor(
    descriptor: Mapping[str, object],
    *,
    protocol_versions_supported: Sequence[Mapping[str, object]] | None = None,
    semantic_contract_versions_supported: Sequence[Mapping[str, object]] | None = None,
    feature_capabilities: Sequence[object] | None = None,
    required_capabilities: Sequence[object] | None = None,
    optional_capabilities: Sequence[object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    base = _as_map(descriptor)
    merged_extensions = dict(_as_map(base.get("extensions")))
    merged_extensions.update(_as_map(extensions))
    return build_endpoint_descriptor(
        product_id=_token(base.get("product_id")),
        product_version=_token(base.get("product_version")),
        protocol_versions_supported=list(
            protocol_versions_supported
            if protocol_versions_supported is not None
            else _as_list(base.get("protocol_versions_supported"))
        ),
        semantic_contract_versions_supported=list(
            semantic_contract_versions_supported
            if semantic_contract_versions_supported is not None
            else _as_list(base.get("semantic_contract_versions_supported"))
        ),
        feature_capabilities=list(
            feature_capabilities if feature_capabilities is not None else _as_list(base.get("feature_capabilities"))
        ),
        required_capabilities=list(
            required_capabilities if required_capabilities is not None else _as_list(base.get("required_capabilities"))
        ),
        optional_capabilities=list(
            optional_capabilities if optional_capabilities is not None else _as_list(base.get("optional_capabilities"))
        ),
        degrade_ladders=list(_as_list(base.get("degrade_ladders"))),
        extensions=merged_extensions,
    )


def _descriptor_with_protocol_drift(descriptor: Mapping[str, object]) -> dict:
    rows = []
    for row in _as_list(_as_map(descriptor).get("protocol_versions_supported")):
        item = dict(_as_map(row))
        if _token(item.get("protocol_id")) == "protocol.loopback.session":
            item["min_version"] = "1.0.0"
            item["max_version"] = "1.1.0"
        rows.append(item)
    return _rebuild_descriptor(descriptor, protocol_versions_supported=rows)


def _descriptor_with_contract_drift(descriptor: Mapping[str, object]) -> tuple[dict, str]:
    rows = [dict(_as_map(row)) for row in _as_list(_as_map(descriptor).get("semantic_contract_versions_supported"))]
    if not rows:
        return dict(descriptor), ""
    rows = sorted(rows, key=lambda row: _token(row.get("contract_category_id")))
    first = dict(rows[0])
    category_id = _token(first.get("contract_category_id"))
    base_version = int(first.get("max_version", first.get("min_version", 1)) or 1)
    first["min_version"] = base_version + 1
    first["max_version"] = base_version + 1
    rows[0] = first
    return _rebuild_descriptor(descriptor, semantic_contract_versions_supported=rows), category_id


def _descriptor_with_platform_projection(repo_root: str, descriptor: Mapping[str, object], *, platform_id: str) -> dict:
    base = _as_map(descriptor)
    product_id = _token(base.get("product_id"))
    platform_descriptor = probe_platform_descriptor(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=False,
        native_available=False,
        rendered_available=None,
        ncurses_available=True,
    )
    extensions = dict(_as_map(base.get("extensions")))
    extensions["official.platform_id"] = _token(platform_descriptor.get("platform_id"))
    extensions["official.platform_descriptor_hash"] = _token(platform_descriptor.get("deterministic_fingerprint"))
    extensions["official.platform_capability_ids"] = list(_as_list(platform_descriptor.get("supported_capability_ids")))
    extensions["official.platform_descriptor"] = dict(platform_descriptor)
    return _rebuild_descriptor(
        base,
        feature_capabilities=project_feature_capabilities_for_platform(
            _as_list(base.get("feature_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        required_capabilities=project_feature_capabilities_for_platform(
            _as_list(base.get("required_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        optional_capabilities=project_feature_capabilities_for_platform(
            _as_list(base.get("optional_capabilities")),
            platform_descriptor=platform_descriptor,
        ),
        extensions=extensions,
    )


def _case_descriptor_dir(work_root: str, case_id: str) -> str:
    return os.path.join(_norm(work_root), "descriptor_overrides", _token(case_id))


def _write_descriptor_variant(work_root: str, case_id: str, name: str, descriptor: Mapping[str, object]) -> str:
    directory = _case_descriptor_dir(work_root, case_id)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "{}.json".format(_token(name) or "descriptor"))
    _write_json(path, dict(descriptor or {}))
    return path


def _event_message_keys(run: Mapping[str, object]) -> list[str]:
    out: list[str] = []
    for row in _as_list(_as_map(run).get("event_rows")):
        message_key = _token(_as_map(row).get("message_key"))
        if message_key and message_key not in out:
            out.append(message_key)
    return out


def _compat_status_surface(
    bundle_root: str,
    *,
    product_id: str,
    peer_descriptor_path: str,
    allow_read_only: bool,
) -> dict:
    argv = [
        "compat-status",
        "--mode",
        "cli",
        "--peer-descriptor-file",
        _norm(peer_descriptor_path),
    ]
    if allow_read_only:
        argv.append("--allow-read-only")
    run = _run_bundle_product(bundle_root, product_id, argv)
    payload = _as_map(run.get("first_json"))
    mode_selection = _as_map(payload.get("mode_selection"))
    is_refusal = bool(_token(payload.get("refusal_code")) or _token(payload.get("reason_code")))
    compatibility_mode_id = _token(payload.get("compatibility_mode_id"))
    if not compatibility_mode_id:
        compatibility_mode_id = _token(mode_selection.get("compatibility_mode_id"))
    return {
        "product_id": _token(product_id),
        "returncode": int(run.get("returncode", 0) or 0),
        "payload": payload,
        "compatibility_mode_id": compatibility_mode_id,
        "negotiation_record_hash": _token(payload.get("negotiation_record_hash")),
        "refusal_code": _token(payload.get("refusal_code")) or _token(payload.get("reason_code")),
        "selected_mode_id": _token(mode_selection.get("selected_mode_id")),
        "event_message_keys": _event_message_keys(run),
        "is_refusal": is_refusal,
        "payload_fingerprint": canonical_sha256(payload) if payload else "",
    }


def _compat_summary(status_row: Mapping[str, object]) -> dict:
    row = _as_map(status_row)
    return {
        "product_id": _token(row.get("product_id")),
        "returncode": int(row.get("returncode", 0) or 0),
        "compatibility_mode_id": _token(row.get("compatibility_mode_id")),
        "negotiation_record_hash": _token(row.get("negotiation_record_hash")),
        "refusal_code": _token(row.get("refusal_code")),
        "selected_mode_id": _token(row.get("selected_mode_id")),
        "event_message_keys": list(_as_list(row.get("event_message_keys"))),
        "is_refusal": bool(row.get("is_refusal", False)),
        "payload_fingerprint": _token(row.get("payload_fingerprint")),
    }


def _load_contract_bundle_payload(repo_root: str) -> tuple[dict, str]:
    payload, _registry, _proof, errors = build_universe_contract_bundle_payload(repo_root)
    if errors:
        raise RuntimeError("unable to build contract bundle payload: {}".format(", ".join(sorted(errors))))
    return dict(payload), canonical_sha256(payload)


def _write_save_fixture(
    repo_root: str,
    *,
    work_root: str,
    case_id: str,
    variant: str,
    install_manifest: Mapping[str, object],
    pack_lock_payload: Mapping[str, object],
    save_hash_overrides: Mapping[str, object] | None = None,
    allow_read_only_open: bool,
) -> str:
    save_root = os.path.join(_norm(work_root), "save_cases", _token(case_id), _token(variant))
    if os.path.isdir(save_root):
        shutil.rmtree(save_root)
    os.makedirs(os.path.join(save_root, "state.snapshots"), exist_ok=True)
    os.makedirs(os.path.join(save_root, "patches"), exist_ok=True)
    os.makedirs(os.path.join(save_root, "proofs"), exist_ok=True)
    contract_bundle_payload, contract_bundle_hash = _load_contract_bundle_payload(repo_root)
    _write_json(os.path.join(save_root, "universe_contract_bundle.json"), contract_bundle_payload)
    _write_json(os.path.join(save_root, "state.snapshots", "snapshot.000.json"), {"tick": 0, "state": "dist6"})
    _write_json(os.path.join(save_root, "patches", "overlay.000.json"), {"patch": 0, "source": "DIST-6"})
    _write_json(os.path.join(save_root, "proofs", "anchor.000.json"), {"anchor_id": "proof.dist6.000"})

    install_map = _as_map(install_manifest)
    product_builds = {
        str(key): str(value).strip()
        for key, value in sorted(_as_map(install_map.get("product_builds")).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    save_payload = normalize_save_manifest(
        {
            "save_id": "save.dist6.{}.{}".format(_token(case_id), _token(variant)),
            "save_format_version": "1.0.0",
            "universe_identity_hash": canonical_sha256({"case_id": _token(case_id), "variant": _token(variant)}),
            "universe_contract_bundle_hash": contract_bundle_hash,
            "semantic_contract_registry_hash": _token(install_map.get("semantic_contract_registry_hash")),
            "generator_version_id": "generator.dist6.{}".format(_token(case_id)),
            "realism_profile_id": "realism.profile.default",
            "pack_lock_hash": _token(_as_map(pack_lock_payload).get("pack_lock_hash")),
            "overlay_manifest_hash": canonical_sha256({"case_id": _token(case_id), "overlay": _token(variant)}),
            "mod_policy_id": "mod.policy.default",
            "created_by_build_id": product_builds.get("client") or product_builds.get("server") or "",
            "migration_chain": [],
            "allow_read_only_open": bool(allow_read_only_open),
            "contract_bundle_ref": "universe_contract_bundle.json",
            "state_snapshots_ref": "state.snapshots",
            "patches_ref": "patches",
            "proofs_ref": "proofs",
            "extensions": {"official.source": "DIST-6"},
            "deterministic_fingerprint": "",
        }
    )
    overrides = _as_map(save_hash_overrides)
    for key, value in sorted(overrides.items(), key=lambda item: str(item[0])):
        save_payload[str(key)] = value
        if str(key) == "universe_contract_bundle_hash":
            save_payload["contract_bundle_hash"] = value
        if str(key) == "save_format_version":
            save_payload["format_version"] = value
    save_payload["deterministic_fingerprint"] = save_deterministic_fingerprint(save_payload)
    write_save_json(os.path.join(save_root, "save.manifest.json"), save_payload)
    return os.path.join(save_root, "save.manifest.json")


def _save_open_summary(result: Mapping[str, object]) -> dict:
    row = _as_map(result)
    return {
        "result": _token(row.get("result")),
        "refusal_code": _token(row.get("refusal_code")),
        "read_only_required": bool(row.get("read_only_required", False)),
        "read_only_allowed": bool(row.get("read_only_allowed", False)),
        "migration_required": bool(row.get("migration_required", False)),
        "migration_applied": bool(row.get("migration_applied", False)),
        "degrade_reasons": sorted(_token(item) for item in _as_list(row.get("degrade_reasons")) if _token(item)),
        "contract_bundle_hash": _token(row.get("contract_bundle_hash")),
        "expected_contract_bundle_hash": _token(row.get("expected_contract_bundle_hash")),
        "save_manifest_fingerprint": _token(_as_map(row.get("save_manifest")).get("deterministic_fingerprint")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "result": _token(row.get("result")),
                "refusal_code": _token(row.get("refusal_code")),
                "read_only_required": bool(row.get("read_only_required", False)),
                "degrade_reasons": sorted(_token(item) for item in _as_list(row.get("degrade_reasons")) if _token(item)),
                "save_manifest_fingerprint": _token(_as_map(row.get("save_manifest")).get("deterministic_fingerprint")),
            }
        ),
    }


def _negotiate_pair(
    repo_root: str,
    *,
    client_descriptor: Mapping[str, object],
    server_descriptor: Mapping[str, object],
    allow_read_only: bool,
) -> dict:
    negotiated = negotiate_endpoint_descriptors(
        repo_root,
        dict(client_descriptor or {}),
        dict(server_descriptor or {}),
        allow_read_only=bool(allow_read_only),
        chosen_contract_bundle_hash="",
    )
    negotiation_record = dict(negotiated.get("negotiation_record") or {})
    verify = verify_negotiation_record(
        repo_root,
        negotiation_record,
        dict(client_descriptor or {}),
        dict(server_descriptor or {}),
        allow_read_only=bool(allow_read_only),
        chosen_contract_bundle_hash="",
    )
    runtime_state = build_degrade_runtime_state(negotiation_record)
    return {
        "result": _token(negotiated.get("result")),
        "compatibility_mode_id": _token(negotiated.get("compatibility_mode_id")),
        "negotiation_record_hash": _token(negotiated.get("negotiation_record_hash")),
        "refusal_code": _token(_as_map(negotiated.get("refusal")).get("reason_code")),
        "verify_result": _token(verify.get("result")),
        "verify_hash": _token(verify.get("negotiation_record_hash")),
        "negotiation_record": negotiation_record,
        "runtime_state": runtime_state,
        "degrade_plan": [dict(item or {}) for item in _as_list(negotiation_record.get("degrade_plan"))],
        "disabled_capabilities": [dict(item or {}) for item in _as_list(negotiation_record.get("disabled_capabilities"))],
    }


def _base_context(bundle_a: Mapping[str, object], bundle_b: Mapping[str, object]) -> dict:
    bundle_root_a = _token(bundle_a.get("bundle_root"))
    bundle_root_b = _token(bundle_b.get("bundle_root"))
    return {
        "bundle_a_root": bundle_root_a,
        "bundle_b_root": bundle_root_b,
        "install_manifest_a": _load_bundle_json(bundle_root_a, "install.manifest.json"),
        "install_manifest_b": _load_bundle_json(bundle_root_b, "install.manifest.json"),
        "instance_manifest_a": _load_bundle_json(bundle_root_a, "instances/default/instance.manifest.json"),
        "instance_manifest_b": _load_bundle_json(bundle_root_b, "instances/default/instance.manifest.json"),
        "pack_lock_a": _load_bundle_json(bundle_root_a, "store/locks/pack_lock.mvp_default.json"),
        "pack_lock_b": _load_bundle_json(bundle_root_b, "store/locks/pack_lock.mvp_default.json"),
        "client_a": _descriptor_from_bundle(bundle_root_a, "client"),
        "server_a": _descriptor_from_bundle(bundle_root_a, "server"),
        "client_b": _descriptor_from_bundle(bundle_root_b, "client"),
        "server_b": _descriptor_from_bundle(bundle_root_b, "server"),
    }


def _case_result(
    *,
    repo_root: str,
    case_id: str,
    case_label: str,
    bundle_a: Mapping[str, object],
    bundle_b: Mapping[str, object],
    client_descriptor: Mapping[str, object],
    server_descriptor: Mapping[str, object],
    allow_read_only: bool,
    surface_rows: Sequence[Mapping[str, object]],
    expected_mode: str,
    expected_refusal_code: str = "",
    expected_save_refusal_code: str = "",
    save_open_result: Mapping[str, object] | None = None,
    notes: Sequence[str] | None = None,
    extra: Mapping[str, object] | None = None,
) -> dict:
    negotiation = _negotiate_pair(
        repo_root,
        client_descriptor=client_descriptor,
        server_descriptor=server_descriptor,
        allow_read_only=allow_read_only,
    )
    save_summary = _save_open_summary(save_open_result or {}) if save_open_result else {}
    surface_summaries = [_compat_summary(row) for row in list(surface_rows or [])]
    silent_degrade = False
    negotiation_record_missing = False
    for row in surface_summaries:
        mode_id = _token(row.get("compatibility_mode_id"))
        message_keys = list(_as_list(row.get("event_message_keys")))
        if mode_id in {"compat.degraded", COMPAT_MODE_READ_ONLY} and "compat.negotiation.result" not in message_keys:
            silent_degrade = True
        if bool(row.get("is_refusal")) and "compat.negotiation.refused" not in message_keys:
            silent_degrade = True
        if not bool(row.get("is_refusal")) and not _token(row.get("negotiation_record_hash")):
            negotiation_record_missing = True

    expected_ok = True
    actual_mode = _token(negotiation.get("compatibility_mode_id"))
    if expected_mode == COMPAT_MODE_REFUSE:
        expected_ok = _token(negotiation.get("result")) == "refused" and _token(negotiation.get("refusal_code")) == _token(expected_refusal_code)
    else:
        expected_ok = (
            _token(negotiation.get("result")) == "complete"
            and actual_mode == _token(expected_mode)
            and _token(negotiation.get("verify_result")) == "complete"
        )
    if save_summary and expected_save_refusal_code:
        expected_ok = expected_ok and _token(save_summary.get("refusal_code")) == _token(expected_save_refusal_code)
    elif save_summary and expected_mode == COMPAT_MODE_READ_ONLY:
        expected_ok = expected_ok and bool(save_summary.get("read_only_required")) and bool(_as_list(save_summary.get("degrade_reasons")))
    if save_summary and expected_mode == COMPAT_MODE_REFUSE and not expected_save_refusal_code:
        expected_ok = expected_ok and _token(save_summary.get("result")) == "refused"
    if surface_summaries:
        expected_ok = expected_ok and all(int(_as_map(row).get("returncode", 1)) == 0 for row in surface_summaries if not bool(_as_map(row).get("is_refusal")))
    expected_ok = expected_ok and not silent_degrade and not negotiation_record_missing

    report = {
        "report_id": "dist.version_interop.case.v1",
        "case_id": _token(case_id),
        "case_label": _token(case_label),
        "result": "complete" if expected_ok else "refused",
        "bundle_a": {
            "source_kind": _token(bundle_a.get("source_kind")),
            "bundle_root": _repo_rel_or_abs(repo_root, _token(bundle_a.get("bundle_root"))),
            "platform_tag": _token(bundle_a.get("platform_tag")),
        },
        "bundle_b": {
            "source_kind": _token(bundle_b.get("source_kind")),
            "bundle_root": _repo_rel_or_abs(repo_root, _token(bundle_b.get("bundle_root"))),
            "platform_tag": _token(bundle_b.get("platform_tag")),
        },
        "client_descriptor": {
            "product_id": _token(_as_map(client_descriptor).get("product_id")),
            "product_version": _token(_as_map(client_descriptor).get("product_version")),
            "build_id": _token(_as_map(_as_map(client_descriptor).get("extensions")).get("official.build_id")),
            "platform_id": _token(_as_map(_as_map(client_descriptor).get("extensions")).get("official.platform_id")),
            "descriptor_hash": canonical_sha256(dict(client_descriptor or {})),
        },
        "server_descriptor": {
            "product_id": _token(_as_map(server_descriptor).get("product_id")),
            "product_version": _token(_as_map(server_descriptor).get("product_version")),
            "build_id": _token(_as_map(_as_map(server_descriptor).get("extensions")).get("official.build_id")),
            "platform_id": _token(_as_map(_as_map(server_descriptor).get("extensions")).get("official.platform_id")),
            "descriptor_hash": canonical_sha256(dict(server_descriptor or {})),
        },
        "negotiation": {
            "result": _token(negotiation.get("result")),
            "compatibility_mode_id": actual_mode,
            "refusal_code": _token(negotiation.get("refusal_code")),
            "verify_result": _token(negotiation.get("verify_result")),
            "negotiation_record_hash": _token(negotiation.get("negotiation_record_hash")),
            "verify_hash": _token(negotiation.get("verify_hash")),
            "chosen_protocol_id": _token(_as_map(negotiation.get("negotiation_record")).get("chosen_protocol_id")),
            "chosen_protocol_version": _token(_as_map(negotiation.get("negotiation_record")).get("chosen_protocol_version")),
            "degrade_plan_count": int(len(_as_list(negotiation.get("degrade_plan")))),
            "disabled_capability_count": int(len(_as_list(negotiation.get("disabled_capabilities")))),
            "runtime_state_fingerprint": _token(_as_map(negotiation.get("runtime_state")).get("deterministic_fingerprint")),
        },
        "surface_rows": surface_summaries,
        "save_open": save_summary,
        "assertions": {
            "expected_mode_observed": bool(expected_ok),
            "degrade_logged": not silent_degrade,
            "negotiation_record_present": not negotiation_record_missing,
            "save_behavior_matched": True
            if not save_summary
            else (
                _token(save_summary.get("refusal_code")) == _token(expected_save_refusal_code)
                if _token(expected_save_refusal_code)
                else bool(save_summary.get("read_only_required")) if expected_mode == COMPAT_MODE_READ_ONLY else True
            ),
        },
        "notes": sorted({_token(item) for item in list(notes or []) if _token(item)}),
        "errors": [],
        "extensions": dict(sorted(_as_map(extra).items(), key=lambda item: str(item[0]))),
        "deterministic_fingerprint": "",
    }
    if not expected_ok:
        if _token(report["negotiation"].get("verify_result")) != "complete":
            report["errors"].append(
                {
                    "code": "negotiation_record_missing",
                    "file_path": CASE_JSON_TEMPLATE.format(_token(case_id)),
                    "message": "negotiation record verification failed for {}".format(_token(case_id)),
                    "rule_id": RULE_ID,
                }
            )
        if silent_degrade:
            report["errors"].append(
                {
                    "code": "silent_degrade_not_logged",
                    "file_path": CASE_JSON_TEMPLATE.format(_token(case_id)),
                    "message": "degrade or refusal path was not logged deterministically for {}".format(_token(case_id)),
                    "rule_id": RULE_ID,
                }
            )
        if save_summary and _token(expected_save_refusal_code) and _token(save_summary.get("refusal_code")) != _token(expected_save_refusal_code):
            report["errors"].append(
                {
                    "code": "save_behavior_mismatch",
                    "file_path": CASE_JSON_TEMPLATE.format(_token(case_id)),
                    "message": "save-open result drifted for {}".format(_token(case_id)),
                    "rule_id": RULE_ID,
                }
            )
        if not report["errors"]:
            report["errors"].append(
                {
                    "code": "interop_case_failed",
                    "file_path": CASE_JSON_TEMPLATE.format(_token(case_id)),
                    "message": "DIST-6 case {} did not satisfy its expected compatibility outcome".format(_token(case_id)),
                    "rule_id": RULE_ID,
                }
            )
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_version_interop_reports(
    repo_root: str,
    *,
    dist_root_a: str = "",
    dist_root_b: str = "",
    platform_tag_a: str = DEFAULT_PLATFORM_TAG,
    platform_tag_b: str = DEFAULT_PLATFORM_TAG,
    channel_id: str = DEFAULT_RELEASE_CHANNEL,
    case_ids: Sequence[str] | None = None,
    work_root: str = DEFAULT_WORK_ROOT,
) -> list[dict]:
    bundle_a = _prepare_bundle(
        repo_root,
        dist_root=dist_root_a,
        output_root=DEFAULT_OUTPUT_ROOT_A,
        platform_tag=platform_tag_a,
        channel_id=channel_id,
    )
    bundle_b = _prepare_bundle(
        repo_root,
        dist_root=dist_root_b,
        output_root=DEFAULT_OUTPUT_ROOT_B,
        platform_tag=platform_tag_b,
        channel_id=channel_id,
    )
    context = _base_context(bundle_a, bundle_b)
    root = _norm(work_root or DEFAULT_WORK_ROOT)
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root, exist_ok=True)

    selected_case_ids = [case_id for case_id in DIST6_CASE_IDS if not case_ids or case_id in set(case_ids)]
    reports: list[dict] = []
    baseline_mode = _token(
        _negotiate_pair(
            repo_root,
            client_descriptor=context["client_a"]["descriptor"],
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
        ).get("compatibility_mode_id")
    ) or COMPAT_MODE_FULL

    case_a_server_peer = _write_descriptor_variant(root, "same_build_same_build", "server_a_peer", context["server_a"]["descriptor"])
    case_a_client_peer = _write_descriptor_variant(root, "same_build_same_build", "client_a_peer", context["client_a"]["descriptor"])
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="same_build_same_build",
            case_label="Same build ↔ same build",
            bundle_a=bundle_a,
            bundle_b=bundle_a,
            client_descriptor=context["client_a"]["descriptor"],
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[
                _compat_status_surface(bundle_a["bundle_root"], product_id="client", peer_descriptor_path=case_a_server_peer, allow_read_only=False),
                _compat_status_surface(bundle_a["bundle_root"], product_id="server", peer_descriptor_path=case_a_client_peer, allow_read_only=False),
            ],
            expected_mode=baseline_mode,
            notes=["portable client and server descriptors emitted from the same bundle negotiate without refusal"],
        )
    )

    case_b_server_peer = _write_descriptor_variant(root, "same_build_identical_rebuild", "server_a_peer", context["server_a"]["descriptor"])
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="same_build_identical_rebuild",
            case_label="Same build ↔ rebuilt identical build",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=context["client_b"]["descriptor"],
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[
                _compat_status_surface(bundle_b["bundle_root"], product_id="client", peer_descriptor_path=case_b_server_peer, allow_read_only=False),
            ],
            expected_mode=baseline_mode,
            notes=["bundle B is rebuilt from identical inputs and is expected to keep the same build_id and negotiation hash"],
            extra={
                "same_build_id": _token(context["client_a"]["build_id"]) == _token(context["client_b"]["build_id"]),
                "baseline_negotiation_hash": _token(_as_map(reports[0]).get("negotiation", {}).get("negotiation_record_hash")),
            },
        )
    )

    projected_client = _descriptor_with_platform_projection(repo_root, context["client_b"]["descriptor"], platform_id=SIMULATED_PLATFORM_ID)
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="same_version_cross_platform",
            case_label="Same version, different platform tag",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=projected_client,
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[],
            expected_mode=baseline_mode,
            notes=["cross-platform case uses a deterministic projected platform descriptor when no second built platform bundle is available"],
            extra={"simulated_platform_id": SIMULATED_PLATFORM_ID},
        )
    )

    drifted_client = _descriptor_with_protocol_drift(context["client_b"]["descriptor"])
    drifted_client_path = _write_descriptor_variant(root, "minor_protocol_drift", "client_minor_protocol", drifted_client)
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="minor_protocol_drift",
            case_label="Minor protocol drift with overlapping range",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=drifted_client,
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[
                _compat_status_surface(bundle_a["bundle_root"], product_id="server", peer_descriptor_path=drifted_client_path, allow_read_only=False),
            ],
            expected_mode=baseline_mode,
            notes=["protocol overlap remains lawful and should select the stable shared loopback version"],
        )
    )

    pack_mismatch_save = _write_save_fixture(
        repo_root,
        work_root=root,
        case_id="pack_lock_mismatch",
        variant="pack_lock_mismatch",
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        save_hash_overrides={"pack_lock_hash": "hash.pack_lock.mismatch"},
        allow_read_only_open=False,
    )
    pack_mismatch_result = evaluate_save_open(
        repo_root=repo_root,
        save_manifest_path=pack_mismatch_save,
        instance_manifest=context["instance_manifest_b"],
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        run_mode="play",
    )
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="pack_lock_mismatch",
            case_label="Pack lock mismatch",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=context["client_b"]["descriptor"],
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[],
            expected_mode=baseline_mode,
            expected_save_refusal_code="refusal.save.pack_lock_mismatch",
            save_open_result=pack_mismatch_result,
            notes=["pack mismatch is refused deterministically even when endpoint negotiation remains lawful"],
        )
    )

    drifted_contract_client, drifted_contract_category = _descriptor_with_contract_drift(context["client_b"]["descriptor"])
    drifted_contract_path = _write_descriptor_variant(root, "contract_mismatch_read_only", "client_contract_mismatch", drifted_contract_client)
    read_only_save = _write_save_fixture(
        repo_root,
        work_root=root,
        case_id="contract_mismatch_read_only",
        variant="read_only",
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        save_hash_overrides={"universe_contract_bundle_hash": "hash.contract_bundle.read_only_mismatch"},
        allow_read_only_open=True,
    )
    read_only_result = evaluate_save_open(
        repo_root=repo_root,
        save_manifest_path=read_only_save,
        instance_manifest=context["instance_manifest_b"],
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        run_mode="play",
        instance_allow_read_only_fallback=True,
    )
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="contract_mismatch_read_only",
            case_label="Contract mismatch with read-only fallback",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=drifted_contract_client,
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=True,
            surface_rows=[
                _compat_status_surface(bundle_a["bundle_root"], product_id="server", peer_descriptor_path=drifted_contract_path, allow_read_only=True),
            ],
            expected_mode=COMPAT_MODE_READ_ONLY,
            save_open_result=read_only_result,
            notes=["read-only fallback must be explicit in both negotiation output and save-open evaluation"],
            extra={"contract_category_id": drifted_contract_category},
        )
    )

    strict_save = _write_save_fixture(
        repo_root,
        work_root=root,
        case_id="contract_mismatch_strict",
        variant="strict",
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        save_hash_overrides={"universe_contract_bundle_hash": "hash.contract_bundle.strict_mismatch"},
        allow_read_only_open=False,
    )
    strict_result = evaluate_save_open(
        repo_root=repo_root,
        save_manifest_path=strict_save,
        instance_manifest=context["instance_manifest_b"],
        install_manifest=context["install_manifest_b"],
        pack_lock_payload=context["pack_lock_b"],
        run_mode="play",
    )
    strict_surface = _compat_status_surface(
        bundle_a["bundle_root"],
        product_id="server",
        peer_descriptor_path=drifted_contract_path,
        allow_read_only=False,
    )
    reports.append(
        _case_result(
            repo_root=repo_root,
            case_id="contract_mismatch_strict",
            case_label="Contract mismatch with strict refusal",
            bundle_a=bundle_a,
            bundle_b=bundle_b,
            client_descriptor=drifted_contract_client,
            server_descriptor=context["server_a"]["descriptor"],
            allow_read_only=False,
            surface_rows=[strict_surface],
            expected_mode=COMPAT_MODE_REFUSE,
            expected_refusal_code="refusal.compat.contract_mismatch",
            expected_save_refusal_code="refusal.save.contract_mismatch",
            save_open_result=strict_result,
            notes=["strict mode must refuse both endpoint interop and save-open drift without silent fallback"],
            extra={"contract_category_id": drifted_contract_category},
        )
    )

    report_by_id = {str(row.get("case_id", "")).strip(): dict(row) for row in reports}
    ordered = [report_by_id[case_id] for case_id in selected_case_ids if case_id in report_by_id]
    if report_by_id.get("same_build_identical_rebuild"):
        same_hash = _token(_as_map(report_by_id["same_build_same_build"]).get("negotiation", {}).get("negotiation_record_hash"))
        case_b = dict(report_by_id["same_build_identical_rebuild"])
        case_b.setdefault("extensions", {})
        case_b["extensions"]["baseline_negotiation_hash"] = same_hash
        case_b["assertions"]["same_build_id"] = bool(_as_map(case_b.get("extensions")).get("same_build_id", False))
        case_b["assertions"]["identical_rebuild_hash_match"] = (
            _token(_as_map(case_b).get("negotiation", {}).get("negotiation_record_hash")) == same_hash
        )
        case_b["result"] = "complete" if (
            _token(case_b.get("result")) == "complete"
            and bool(case_b["assertions"]["identical_rebuild_hash_match"])
            and bool(case_b["assertions"]["same_build_id"])
        ) else "refused"
        if _token(case_b.get("result")) == "complete":
            case_b["errors"] = []
        else:
            case_b.setdefault("errors", []).append(
                {
                    "code": "identical_rebuild_hash_mismatch",
                    "file_path": CASE_JSON_TEMPLATE.format("same_build_identical_rebuild"),
                    "message": "identical rebuild drifted from the canonical same-build hash or build_id baseline",
                    "rule_id": RULE_ID,
                }
            )
        case_b["deterministic_fingerprint"] = canonical_sha256(dict(case_b, deterministic_fingerprint=""))
        for index, row in enumerate(ordered):
            if _token(_as_map(row).get("case_id")) == "same_build_identical_rebuild":
                ordered[index] = case_b
                break
    return ordered


def render_version_interop_case(report: Mapping[str, object]) -> str:
    row = _as_map(report)
    negotiation = _as_map(row.get("negotiation"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-7 archive packaging and signed release interop notes",
        "",
        "# DIST6 Interop - {}".format(_token(row.get("case_id"))),
        "",
        "- case_label: `{}`".format(_token(row.get("case_label"))),
        "- result: `{}`".format(_token(row.get("result"))),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Bundles",
        "",
        "- bundle_a: `{}` `{}` source=`{}`".format(
            _token(_as_map(row.get("bundle_a")).get("platform_tag")),
            _token(_as_map(row.get("bundle_a")).get("bundle_root")),
            _token(_as_map(row.get("bundle_a")).get("source_kind")),
        ),
        "- bundle_b: `{}` `{}` source=`{}`".format(
            _token(_as_map(row.get("bundle_b")).get("platform_tag")),
            _token(_as_map(row.get("bundle_b")).get("bundle_root")),
            _token(_as_map(row.get("bundle_b")).get("source_kind")),
        ),
        "",
        "## Negotiation",
        "",
        "- result: `{}`".format(_token(negotiation.get("result"))),
        "- compatibility_mode_id: `{}`".format(_token(negotiation.get("compatibility_mode_id"))),
        "- refusal_code: `{}`".format(_token(negotiation.get("refusal_code")) or "none"),
        "- negotiation_record_hash: `{}`".format(_token(negotiation.get("negotiation_record_hash"))),
        "- chosen_protocol: `{}` `{}`".format(
            _token(negotiation.get("chosen_protocol_id")),
            _token(negotiation.get("chosen_protocol_version")),
        ),
        "",
        "## Surfaces",
        "",
    ]
    surface_rows = _as_list(row.get("surface_rows"))
    if not surface_rows:
        lines.append("- none")
    else:
        for item in surface_rows:
            surface = _as_map(item)
            lines.append(
                "- `{}` returncode=`{}` mode=`{}` refusal=`{}` events=`{}`".format(
                    _token(surface.get("product_id")),
                    int(surface.get("returncode", 0) or 0),
                    _token(surface.get("compatibility_mode_id")) or "none",
                    _token(surface.get("refusal_code")) or "none",
                    ", ".join(_token(event) for event in _as_list(surface.get("event_message_keys"))) or "none",
                )
            )
    lines.extend(["", "## Save Compatibility", ""])
    save_open = _as_map(row.get("save_open"))
    if not save_open:
        lines.append("- none")
    else:
        lines.append(
            "- result=`{}` refusal=`{}` read_only_required=`{}` degrade_reasons=`{}`".format(
                _token(save_open.get("result")),
                _token(save_open.get("refusal_code")) or "none",
                bool(save_open.get("read_only_required", False)),
                ", ".join(_token(item) for item in _as_list(save_open.get("degrade_reasons"))) or "none",
            )
        )
    lines.extend(["", "## Assertions", ""])
    for key in sorted(_as_map(row.get("assertions")).keys()):
        lines.append("- `{}`: `{}`".format(key, bool(_as_map(row.get("assertions")).get(key))))
    lines.extend(["", "## Notes", ""])
    notes = _as_list(row.get("notes"))
    if not notes:
        lines.append("- none")
    else:
        for note in notes:
            lines.append("- {}".format(_token(note)))
    lines.extend(["", "## Errors", ""])
    errors = _as_list(row.get("errors"))
    if not errors:
        lines.append("- none")
    else:
        for item in errors:
            error = _as_map(item)
            lines.append("- `{}`: {}".format(_token(error.get("code")), _token(error.get("message"))))
    return "\n".join(lines) + "\n"


def build_dist6_final_report(reports: Sequence[Mapping[str, object]]) -> dict:
    normalized = sorted(
        [_as_map(item) for item in list(reports or []) if _as_map(item)],
        key=lambda row: _token(row.get("case_id")),
    )
    payload = {
        "report_id": "dist.version_interop.final.v1",
        "result": "complete" if normalized and all(_token(row.get("result")) == "complete" for row in normalized) else "refused",
        "case_ids": [_token(row.get("case_id")) for row in normalized],
        "failure_count": int(sum(len(_as_list(row.get("errors"))) for row in normalized)),
        "report_fingerprints": {
            _token(row.get("case_id")): _token(row.get("deterministic_fingerprint"))
            for row in normalized
            if _token(row.get("case_id"))
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def render_dist6_final(final_report: Mapping[str, object], reports: Sequence[Mapping[str, object]]) -> str:
    row = _as_map(final_report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-7 packaging artifacts and signed release archive validation",
        "",
        "# DIST6 Final",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- case_ids: `{}`".format(", ".join(_token(item) for item in _as_list(row.get("case_ids"))) or "none"),
        "- failure_count: `{}`".format(int(row.get("failure_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Matrix Summary",
        "",
    ]
    for report in sorted([_as_map(item) for item in list(reports or []) if _as_map(item)], key=lambda item: _token(item.get("case_id"))):
        negotiation = _as_map(report.get("negotiation"))
        lines.append(
            "- `{}` result=`{}` mode=`{}` refusal=`{}` hash=`{}`".format(
                _token(report.get("case_id")),
                _token(report.get("result")),
                _token(negotiation.get("compatibility_mode_id")) or "none",
                _token(negotiation.get("refusal_code")) or _token(_as_map(report.get("save_open")).get("refusal_code")) or "none",
                _token(negotiation.get("negotiation_record_hash")) or "none",
            )
        )
    lines.extend(["", "## Refusal And Degrade Cases", ""])
    for report in sorted([_as_map(item) for item in list(reports or []) if _as_map(item)], key=lambda item: _token(item.get("case_id"))):
        negotiation = _as_map(report.get("negotiation"))
        save_open = _as_map(report.get("save_open"))
        if _token(negotiation.get("compatibility_mode_id")) == COMPAT_MODE_FULL and not _token(save_open.get("refusal_code")):
            continue
        lines.append(
            "- `{}` compat=`{}` compat_refusal=`{}` save_refusal=`{}` degrade_reasons=`{}`".format(
                _token(report.get("case_id")),
                _token(negotiation.get("compatibility_mode_id")) or "none",
                _token(negotiation.get("refusal_code")) or "none",
                _token(save_open.get("refusal_code")) or "none",
                ", ".join(_token(item) for item in _as_list(save_open.get("degrade_reasons"))) or "none",
            )
        )
    lines.extend(["", "## Readiness", "", "- DIST-7 packaging artifacts: {}".format("ready" if _token(row.get("result")) == "complete" else "blocked"), ""])
    return "\n".join(lines) + "\n"


def write_version_interop_outputs(
    repo_root: str,
    reports: Sequence[Mapping[str, object]],
    *,
    final_doc_path: str = FINAL_DOC_PATH,
) -> dict:
    root = _norm(repo_root)
    output_rows = []
    for report in sorted([_as_map(item) for item in list(reports or []) if _as_map(item)], key=lambda item: _token(item.get("case_id"))):
        case_id = _token(report.get("case_id"))
        report_path = os.path.join(root, CASE_JSON_TEMPLATE.format(case_id).replace("/", os.sep))
        doc_path = os.path.join(root, CASE_DOC_TEMPLATE.format(case_id).replace("/", os.sep))
        _write_json(report_path, report)
        _write_text(doc_path, render_version_interop_case(report))
        output_rows.append(
            {
                "case_id": case_id,
                "report_path": _repo_rel_or_abs(root, report_path),
                "doc_path": _repo_rel_or_abs(root, doc_path),
            }
        )
    final_report = build_dist6_final_report(reports)
    final_abs = os.path.join(root, final_doc_path.replace("/", os.sep))
    _write_text(final_abs, render_dist6_final(final_report, reports))
    return {
        "case_outputs": output_rows,
        "final_doc_path": _repo_rel_or_abs(root, final_abs),
        "final_report": final_report,
    }


def _load_case_report(repo_root: str, case_id: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), CASE_JSON_TEMPLATE.format(_token(case_id)).replace("/", os.sep)))


def version_interop_violations(repo_root: str, *, case_ids: Sequence[str] | None = None) -> list[dict]:
    rows: list[dict] = []
    if not os.path.isfile(os.path.join(_norm(repo_root), INTEROP_MATRIX_DOC_PATH.replace("/", os.sep))):
        rows.append(
            {
                "code": "interop_matrix_doc_missing",
                "file_path": INTEROP_MATRIX_DOC_PATH,
                "message": "DIST-6 interop matrix doctrine is missing",
                "rule_id": RULE_ID,
            }
        )
    selected = [case_id for case_id in DIST6_CASE_IDS if not case_ids or case_id in set(case_ids)]
    for case_id in selected:
        payload = _load_case_report(repo_root, case_id)
        if not payload:
            rows.append(
                {
                    "code": "dist6_case_missing",
                    "file_path": CASE_JSON_TEMPLATE.format(case_id),
                    "message": "DIST-6 case report is missing for {}".format(case_id),
                    "rule_id": RULE_ID,
                }
            )
            continue
        if _token(payload.get("result")) != "complete":
            for item in _as_list(payload.get("errors")):
                error = _as_map(item)
                rows.append(
                    {
                        "code": _token(error.get("code")) or "interop_case_failed",
                        "file_path": _token(error.get("file_path")) or CASE_JSON_TEMPLATE.format(case_id),
                        "message": _token(error.get("message")) or "DIST-6 case failed",
                        "rule_id": _token(error.get("rule_id")) or RULE_ID,
                    }
                )
        negotiation = _as_map(payload.get("negotiation"))
        if _token(negotiation.get("compatibility_mode_id")) in {"compat.degraded", COMPAT_MODE_READ_ONLY}:
            surface_rows = [_as_map(item) for item in _as_list(payload.get("surface_rows"))]
            if surface_rows and not any("compat.negotiation.result" in _as_list(row.get("event_message_keys")) for row in surface_rows):
                rows.append(
                    {
                        "code": "silent_degrade_not_logged",
                        "file_path": CASE_JSON_TEMPLATE.format(case_id),
                        "message": "degraded or read-only interop case is missing the compat.negotiation.result log event",
                        "rule_id": RULE_ID,
                    }
                )
        if _token(negotiation.get("result")) == "complete" and not _token(negotiation.get("negotiation_record_hash")):
            rows.append(
                {
                    "code": "negotiation_record_missing",
                    "file_path": CASE_JSON_TEMPLATE.format(case_id),
                    "message": "interop case is missing a negotiation record hash",
                    "rule_id": RULE_ID,
                }
            )
    if not os.path.isfile(os.path.join(_norm(repo_root), FINAL_DOC_PATH.replace("/", os.sep))):
        rows.append(
            {
                "code": "dist6_final_missing",
                "file_path": FINAL_DOC_PATH,
                "message": "DIST-6 final report is missing",
                "rule_id": RULE_ID,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("rule_id")),
            _token(row.get("code")),
            _token(row.get("file_path")),
            _token(row.get("message")),
        ),
    )


__all__ = [
    "CASE_DOC_TEMPLATE",
    "CASE_JSON_TEMPLATE",
    "DIST6_CASE_IDS",
    "FINAL_DOC_PATH",
    "INTEROP_MATRIX_DOC_PATH",
    "RULE_ID",
    "build_dist6_final_report",
    "build_version_interop_reports",
    "render_dist6_final",
    "render_version_interop_case",
    "version_interop_violations",
    "write_version_interop_outputs",
]
