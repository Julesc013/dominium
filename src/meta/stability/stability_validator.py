"""META-STABILITY validator helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.compatx.validator import validate_instance  # noqa: E402

from .stability_scope import (  # noqa: E402
    ALL_REGISTRY_PATHS,
    LEGACY_TEXT_REGISTRY_PATHS,
    SCOPED_REGISTRY_PATHS,
    family_for_registry,
)


STABILITY_MARKER_SCHEMA_NAME = "stability_marker"
PACK_COMPAT_REL_SUFFIX = "pack.compat.json"
_RECORD_METADATA_KEYS = {
    "extensions",
    "registry_id",
    "registry_version",
    "schema_version_ref",
}
_LEGACY_MARKER_KEYS = {
    "schema_version",
    "stability_class_id",
    "rationale",
    "future_series",
    "replacement_target",
    "contract_id",
    "deprecated",
    "deterministic_fingerprint",
}
_LEGACY_EXTENSION_KEYS = {
    "profile_gate_id",
    "entitlement_gate_id",
    "exception_event_id",
}
_SPECIAL_ID_KEYS = (
    "reason_code",
    "extension_key",
    "message_key",
    "exit_code",
    "path_pattern",
    "keyword",
    "value",
)
_ID_KEY_PRIORITY = (
    "contract_id",
    "command_id",
    "process_id",
    "bundle_id",
    "product_id",
    "protocol_id",
    "compat_mode_id",
    "ladder_id",
    "generator_id",
    "sky_model_id",
    "wind_params_id",
    "tide_params_id",
    "illum_model_id",
    "shadow_model_id",
    "priors_id",
    "compile_policy_id",
    "behavior_model_id",
    "logic_element_id",
    "policy_id",
    "machine_id",
    "template_id",
    "platform_id",
    "abi_id",
    "event_id",
    "action_template_id",
    "instrument_type_id",
    "message_key_id",
    "field_type_id",
    "field_binding_id",
    "material_proxy_id",
    "surface_flag_id",
    "galactic_region_id",
    "emitter_kind_id",
    "receiver_kind_id",
    "occlusion_policy_id",
    "ephemeris_provider_id",
    "orbit_path_policy_id",
    "time_anchor_policy_id",
    "tick_type_id",
    "object_kind_id",
    "provider_id",
    "rule_id",
    "gate_id",
    "class_id",
    "family_id",
    "artifact_type_id",
    "mobility_reason_code_id",
    "mobility_refusal_code_id",
    "solver_id",
    "domain_id",
    "reason_code",
    "extension_key",
    "message_key",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root() -> str:
    return REPO_ROOT_HINT


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _read_text(path: str) -> tuple[list[str], str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return list(handle.readlines()), ""
    except OSError:
        return [], "invalid text"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _boolish(value: object) -> bool | None:
    token = _token(value).lower()
    if token in {"true", "1", "yes"}:
        return True
    if token in {"false", "0", "no"}:
        return False
    return None


def _error(*, code: str, path: str, message: str, item_id: str = "") -> dict:
    return {
        "code": _token(code),
        "path": _token(path),
        "message": _token(message),
        "item_id": _token(item_id),
    }


def _sorted_errors(rows: list[dict]) -> list[dict]:
    return sorted(
        [_as_map(row) for row in rows],
        key=lambda row: (
            _token(row.get("path")),
            _token(row.get("code")),
            _token(row.get("item_id")),
            _token(row.get("message")),
        ),
    )


def _marker_seed(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    seed = {
        "schema_version": _token(payload.get("schema_version")),
        "stability_class_id": _token(payload.get("stability_class_id")),
        "rationale": _token(payload.get("rationale")),
        "future_series": _token(payload.get("future_series")),
        "replacement_target": _token(payload.get("replacement_target")),
        "contract_id": _token(payload.get("contract_id")),
        "deterministic_fingerprint": "",
        "extensions": dict(sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))),
    }
    deprecated = payload.get("deprecated")
    if isinstance(deprecated, bool):
        seed["deprecated"] = bool(deprecated)
    return seed


def stability_marker_fingerprint(row: Mapping[str, object] | None) -> str:
    return canonical_sha256(_marker_seed(row))


def build_stability_marker(
    *,
    stability_class_id: str,
    rationale: str,
    future_series: str = "",
    replacement_target: str = "",
    contract_id: str = "",
    deprecated: bool | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": _token(stability_class_id),
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": _token(contract_id),
        "deterministic_fingerprint": "",
        "extensions": dict(_as_map(extensions)),
    }
    if deprecated is not None:
        payload["deprecated"] = bool(deprecated)
    payload["deterministic_fingerprint"] = stability_marker_fingerprint(payload)
    return payload


def _validate_marker_rules(marker: Mapping[str, object] | None, *, path: str, item_id: str = "") -> list[dict]:
    payload = _as_map(marker)
    errors: list[dict] = []
    schema_result = validate_instance(
        repo_root=_repo_root(),
        schema_name=STABILITY_MARKER_SCHEMA_NAME,
        payload=payload,
        strict_top_level=True,
    )
    if not bool(schema_result.get("valid", False)):
        for row in _as_list(schema_result.get("errors")):
            row_map = _as_map(row)
            errors.append(
                _error(
                    code="schema_invalid",
                    path="{}.{}".format(_token(path), _token(row_map.get("path")).lstrip("$").lstrip(".")) if _token(row_map.get("path")) else path,
                    message=_token(row_map.get("message")) or "stability marker schema invalid",
                    item_id=item_id,
                )
            )
        return _sorted_errors(errors)

    expected_fingerprint = stability_marker_fingerprint(payload)
    if _token(payload.get("deterministic_fingerprint")) != expected_fingerprint:
        errors.append(
            _error(
                code="fingerprint_mismatch",
                path="{}.deterministic_fingerprint".format(_token(path)),
                message="stability deterministic_fingerprint must match canonical metadata",
                item_id=item_id,
            )
        )

    stability_class_id = _token(payload.get("stability_class_id"))
    if stability_class_id == "stable":
        if not _token(payload.get("contract_id")):
            errors.append(
                _error(
                    code="stable_requires_contract_id",
                    path="{}.contract_id".format(_token(path)),
                    message="stable entries must declare contract_id",
                    item_id=item_id,
                )
            )
    elif stability_class_id == "provisional":
        if not _token(payload.get("future_series")):
            errors.append(
                _error(
                    code="provisional_requires_future_series",
                    path="{}.future_series".format(_token(path)),
                    message="provisional entries must declare future_series",
                    item_id=item_id,
                )
            )
        if not _token(payload.get("replacement_target")):
            errors.append(
                _error(
                    code="provisional_requires_replacement_target",
                    path="{}.replacement_target".format(_token(path)),
                    message="provisional entries must declare replacement_target",
                    item_id=item_id,
                )
            )
    elif stability_class_id == "experimental":
        extensions = _as_map(payload.get("extensions"))
        if not (_token(extensions.get("profile_gate_id")) or _token(extensions.get("entitlement_gate_id"))):
            errors.append(
                _error(
                    code="experimental_requires_gate",
                    path="{}.extensions".format(_token(path)),
                    message="experimental entries must declare profile_gate_id or entitlement_gate_id",
                    item_id=item_id,
                )
            )
        if not _token(extensions.get("exception_event_id")):
            errors.append(
                _error(
                    code="experimental_requires_exception_event",
                    path="{}.extensions.exception_event_id".format(_token(path)),
                    message="experimental entries must declare exception_event_id",
                    item_id=item_id,
                )
            )

    return _sorted_errors(errors)


def _item_id_from_key(
    row: Mapping[str, object] | None,
    primary_key: str = "",
    *,
    fallback_key: str = "",
    fallback_value: str = "",
    allow_priority_fallback: bool = True,
) -> str:
    payload = _as_map(row)
    if _token(primary_key) and _token(payload.get(primary_key)):
        return _token(payload.get(primary_key))
    if allow_priority_fallback:
        for key in _ID_KEY_PRIORITY:
            token = _token(payload.get(key))
            if token:
                return token
        for key in sorted(payload.keys(), key=lambda value: str(value)):
            if str(key).endswith("_id") and _token(payload.get(key)):
                return _token(payload.get(key))
        platform = _token(payload.get("platform"))
        arch = _token(payload.get("arch"))
        if platform or arch:
            return "{}:{}".format(platform or "unknown", arch or "unknown")
    if _token(fallback_value):
        return _token(fallback_value)
    return _token(fallback_key)


def _collection_id_key(rows: list[dict], collection_key: str) -> str:
    if not rows:
        return ""
    singular_key = _token(collection_key)
    singular_key = singular_key[:-1] if singular_key.endswith("s") else singular_key
    preferred_keys = []
    if singular_key:
        preferred_keys.append("{}_id".format(singular_key))
    preferred_keys.extend(_ID_KEY_PRIORITY)
    preferred_keys.extend(_SPECIAL_ID_KEYS)
    for key in preferred_keys:
        values = [_token(_as_map(row).get(key)) for row in rows]
        if values and all(values) and len(set(values)) == len(rows):
            return _token(key)

    candidate_keys = sorted(
        {
            str(key)
            for row in rows
            for key in _as_map(row).keys()
            if str(key).endswith("_id") or str(key) in _SPECIAL_ID_KEYS
        }
    )
    best_key = ""
    best_score: tuple[int, int, int, str] = (0, 0, 0, "")
    for key in candidate_keys:
        values = [_token(_as_map(row).get(key)) for row in rows]
        present_values = [value for value in values if value]
        if not present_values:
            continue
        unique_count = len(set(present_values))
        complete_unique = 1 if len(present_values) == len(rows) and unique_count == len(rows) else 0
        score = (complete_unique, unique_count, len(present_values), key)
        if score > best_score:
            best_key = key
            best_score = score
    if best_score[0] == 1:
        return best_key
    return ""


def _entry_row(
    *,
    item_id: str,
    row_path: str,
    row: Mapping[str, object] | None,
    collection_key: str,
    entry_key: str,
    entry_kind: str,
    line_number: int = 0,
) -> dict:
    return {
        "item_id": _token(item_id),
        "path": _token(row_path),
        "row": _as_map(row),
        "collection_key": _token(collection_key),
        "entry_key": _token(entry_key),
        "entry_kind": _token(entry_kind),
        "line_number": int(line_number or 0),
    }


def _json_registry_entry_rows(payload: Mapping[str, object] | None) -> tuple[list[dict], list[dict]]:
    root = _as_map(payload)
    entries: list[dict] = []
    errors: list[dict] = []
    collection_detected = False

    if isinstance(root.get("records"), list):
        collection_detected = True
        rows = [dict(value) for value in _as_list(root.get("records")) if isinstance(value, Mapping)]
        primary_key = _collection_id_key(rows, "records")
        for index, value in enumerate(_as_list(root.get("records"))):
            if not isinstance(value, Mapping):
                continue
            row = dict(value)
            entries.append(
                _entry_row(
                    item_id=_item_id_from_key(row, primary_key, allow_priority_fallback=bool(primary_key)),
                    row_path="$.records[{}]".format(index),
                    row=row,
                    collection_key="records",
                    entry_key="records",
                    entry_kind="root_records",
                )
            )

    record = _as_map(root.get("record"))
    for key, value in sorted(record.items(), key=lambda item: str(item[0])):
        if key in _RECORD_METADATA_KEYS:
            continue
        if isinstance(value, list):
            collection_detected = True
            rows = [dict(row) for row in list(value) if isinstance(row, Mapping)]
            if len(rows) != len(value):
                continue
            primary_key = _collection_id_key(rows, str(key))
            for index, row in enumerate(rows):
                entries.append(
                    _entry_row(
                        item_id=_item_id_from_key(row, primary_key, allow_priority_fallback=bool(primary_key)),
                        row_path="$.record.{}[{}]".format(key, index),
                        row=row,
                        collection_key=str(key),
                        entry_key=str(key),
                        entry_kind="record_list",
                    )
                )
            continue
        if isinstance(value, Mapping):
            collection_detected = True
            row = dict(value)
            entries.append(
                _entry_row(
                    item_id=_item_id_from_key(row, "", fallback_key=str(key)),
                    row_path="$.record.{}".format(key),
                    row=row,
                    collection_key=str(key),
                    entry_key=str(key),
                    entry_kind="record_singleton",
                )
            )

    if not collection_detected:
        errors.append(
            _error(
                code="collection_not_detected",
                path="$",
                message="unable to detect registry collection for stability validation",
            )
        )
    return entries, errors


def _parse_legacy_comment_value(key: str, value: str) -> object:
    if key == "deprecated":
        parsed = _boolish(value)
        if parsed is not None:
            return parsed
    return _token(value)


def _legacy_text_entry_rows(lines: list[str]) -> tuple[list[dict], list[dict]]:
    entries: list[dict] = []
    errors: list[dict] = []
    pending_marker: dict[str, object] = {}
    pending_extensions: dict[str, object] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped = str(raw_line).strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            body = stripped[1:].strip()
            if ":" not in body:
                continue
            key, _, value = body.partition(":")
            key_token = _token(key)
            if key_token in _LEGACY_MARKER_KEYS:
                pending_marker[key_token] = _parse_legacy_comment_value(key_token, value)
                continue
            if key_token in _LEGACY_EXTENSION_KEYS:
                pending_extensions[key_token] = _parse_legacy_comment_value(key_token, value)
            continue

        stability = dict(pending_marker)
        if pending_extensions:
            stability["extensions"] = dict(sorted(pending_extensions.items(), key=lambda item: str(item[0])))
        elif stability:
            stability["extensions"] = {}
        entries.append(
            _entry_row(
                item_id=_token(stripped),
                row_path="$.legacy_lines[{}]".format(len(entries)),
                row={"entry_id": _token(stripped), "stability": stability},
                collection_key="legacy_lines",
                entry_key="legacy_lines",
                entry_kind="legacy_text",
                line_number=line_number,
            )
        )
        pending_marker = {}
        pending_extensions = {}

    if not entries:
        errors.append(
            _error(
                code="collection_not_detected",
                path="$",
                message="unable to detect registry collection for stability validation",
            )
        )
    return entries, errors


def registry_entry_rows(file_path: str) -> dict:
    abs_path = os.path.normpath(os.path.abspath(str(file_path)))
    rel_path = _norm(os.path.relpath(abs_path, _repo_root())) if abs_path.startswith(_repo_root()) else _norm(abs_path)
    collection_errors: list[dict] = []
    entries: list[dict] = []
    if rel_path in LEGACY_TEXT_REGISTRY_PATHS or abs_path.endswith(".registry"):
        lines, error = _read_text(abs_path)
        if error:
            collection_errors.append(
                _error(
                    code="invalid_text",
                    path="$",
                    message="registry payload must be a readable text registry",
                )
            )
        else:
            entries, collection_errors = _legacy_text_entry_rows(lines)
        result = {
            "result": "complete" if not collection_errors else "violation",
            "file_path": rel_path,
            "family": family_for_registry(rel_path),
            "legacy_text": True,
            "collection_keys": sorted({_token(row.get("collection_key")) for row in entries if _token(row.get("collection_key"))}),
            "entry_count": len(entries),
            "entries": entries,
            "errors": _sorted_errors(collection_errors),
            "deterministic_fingerprint": "",
        }
        result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint="", entries=[]))
        return result

    payload, error = _read_json(abs_path)
    if error:
        result = {
            "result": "violation",
            "file_path": rel_path,
            "family": family_for_registry(rel_path),
            "legacy_text": False,
            "collection_keys": [],
            "entry_count": 0,
            "entries": [],
            "errors": [
                _error(
                    code="invalid_json",
                    path="$",
                    message="registry payload must be valid JSON object",
                )
            ],
            "deterministic_fingerprint": "",
        }
        result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint="", entries=[]))
        return result

    entries, collection_errors = _json_registry_entry_rows(payload)
    result = {
        "result": "complete" if not collection_errors else "violation",
        "file_path": rel_path,
        "family": family_for_registry(rel_path),
        "legacy_text": False,
        "collection_keys": sorted({_token(row.get("collection_key")) for row in entries if _token(row.get("collection_key"))}),
        "entry_count": len(entries),
        "entries": entries,
        "errors": _sorted_errors(collection_errors),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint="", entries=[]))
    return result


def validate_registry(file_path: str) -> dict:
    entry_report = registry_entry_rows(file_path)
    rel_path = _token(entry_report.get("file_path"))
    errors: list[dict] = list(_as_list(entry_report.get("errors")))
    entries = list(_as_list(entry_report.get("entries")))

    for row in entries:
        row_map = _as_map(row)
        item_id = _token(row_map.get("item_id"))
        row_path = _token(row_map.get("path"))
        entry_payload = _as_map(row_map.get("row"))
        stability = _as_map(entry_payload.get("stability"))
        if not stability:
            errors.append(
                _error(
                    code="missing_stability",
                    path="{}.stability".format(row_path),
                    message="registry entries must declare stability",
                    item_id=item_id,
                )
            )
            continue
        errors.extend(_validate_marker_rules(stability, path="{}.stability".format(row_path), item_id=item_id))

    entry_paths_by_id: dict[str, list[str]] = {}
    for row in entries:
        row_map = _as_map(row)
        item_id = _token(row_map.get("item_id"))
        if not item_id:
            continue
        entry_paths_by_id.setdefault(item_id, []).append(_token(row_map.get("path")))
    for item_id, paths in sorted(entry_paths_by_id.items(), key=lambda item: str(item[0])):
        if len(paths) < 2:
            continue
        for path in sorted(paths):
            errors.append(
                _error(
                    code="duplicate_item_id",
                    path=path,
                    message="registry item identifiers must be unique within a registry file",
                    item_id=item_id,
                )
            )

    result = {
        "result": "complete" if not errors else "violation",
        "file_path": rel_path,
        "family": family_for_registry(rel_path),
        "collection_keys": list(_as_list(entry_report.get("collection_keys"))),
        "entry_count": int(entry_report.get("entry_count", 0) or 0),
        "legacy_text": bool(entry_report.get("legacy_text", False)),
        "scoped": rel_path in SCOPED_REGISTRY_PATHS,
        "errors": _sorted_errors(errors),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def validate_pack_compat(file_path: str) -> dict:
    abs_path = os.path.normpath(os.path.abspath(str(file_path)))
    payload, error = _read_json(abs_path)
    rel_path = _norm(os.path.relpath(abs_path, _repo_root())) if abs_path.startswith(_repo_root()) else _norm(abs_path)
    errors: list[dict] = []
    if error:
        errors.append(
            _error(
                code="invalid_json",
                path="$",
                message="pack compat payload must be valid JSON object",
            )
        )
    else:
        stability = payload.get("stability")
        if isinstance(stability, Mapping):
            errors.extend(_validate_marker_rules(stability, path="$.stability"))

    result = {
        "result": "complete" if not errors else "violation",
        "file_path": rel_path,
        "optional": True,
        "stability_present": isinstance(_as_map(payload).get("stability"), Mapping),
        "errors": _sorted_errors(errors),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def validate_scoped_registries(repo_root: str | None = None) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root or _repo_root()))
    reports = [validate_registry(os.path.join(root, rel_path.replace("/", os.sep))) for rel_path in SCOPED_REGISTRY_PATHS]
    result = {
        "result": "complete" if all(_token(report.get("result")) == "complete" for report in reports) else "violation",
        "reports": reports,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def validate_all_registries(repo_root: str | None = None) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root or _repo_root()))
    reports = [validate_registry(os.path.join(root, rel_path.replace("/", os.sep))) for rel_path in ALL_REGISTRY_PATHS]
    result = {
        "result": "complete" if all(_token(report.get("result")) == "complete" for report in reports) else "violation",
        "reports": reports,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "ALL_REGISTRY_PATHS",
    "LEGACY_TEXT_REGISTRY_PATHS",
    "PACK_COMPAT_REL_SUFFIX",
    "SCOPED_REGISTRY_PATHS",
    "STABILITY_MARKER_SCHEMA_NAME",
    "build_stability_marker",
    "registry_entry_rows",
    "stability_marker_fingerprint",
    "validate_all_registries",
    "validate_pack_compat",
    "validate_registry",
    "validate_scoped_registries",
]
