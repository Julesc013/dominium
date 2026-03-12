"""META-STABILITY-0 validator helpers."""

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

from .stability_scope import SCOPED_REGISTRY_PATHS, family_for_registry  # noqa: E402


STABILITY_MARKER_SCHEMA_NAME = "stability_marker"
PACK_COMPAT_REL_SUFFIX = "pack.compat.json"
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


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


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


def _detect_collection(payload: Mapping[str, object] | None) -> tuple[str, list[dict]]:
    root = _as_map(payload)
    if isinstance(root.get("records"), list):
        return "records", [dict(row) for row in _as_list(root.get("records")) if isinstance(row, Mapping)]
    record = _as_map(root.get("record"))
    candidates = []
    for key, value in sorted(record.items(), key=lambda item: str(item[0])):
        if key in ("extensions",):
            continue
        if not isinstance(value, list):
            continue
        dict_rows = [dict(row) for row in list(value) if isinstance(row, Mapping)]
        if len(dict_rows) != len(value):
            continue
        candidates.append((str(key), dict_rows))
    if len(candidates) == 1:
        return candidates[0][0], candidates[0][1]
    return "", []


def _item_id(row: Mapping[str, object] | None) -> str:
    payload = _as_map(row)
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
    return ""


def validate_registry(file_path: str) -> dict:
    abs_path = os.path.normpath(os.path.abspath(str(file_path)))
    payload, error = _read_json(abs_path)
    rel_path = _norm(os.path.relpath(abs_path, _repo_root())) if abs_path.startswith(_repo_root()) else _norm(abs_path)
    if error:
        result = {
            "result": "violation",
            "file_path": rel_path,
            "family": family_for_registry(rel_path),
            "collection_key": "",
            "entry_count": 0,
            "errors": [
                _error(
                    code="invalid_json",
                    path="$",
                    message="registry payload must be valid JSON object",
                )
            ],
            "deterministic_fingerprint": "",
        }
        result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
        return result

    collection_key, rows = _detect_collection(payload)
    errors: list[dict] = []
    if not collection_key:
        errors.append(
            _error(
                code="collection_not_detected",
                path="$",
                message="unable to detect registry collection for stability validation",
            )
        )
    for index, row in enumerate(rows):
        item_id = _item_id(row)
        row_path = "$.{}[{}]".format(collection_key, index) if collection_key == "records" else "$.record.{}[{}]".format(collection_key, index)
        stability = _as_map(row.get("stability"))
        if not stability:
            errors.append(
                _error(
                    code="missing_stability",
                    path="{}.stability".format(row_path),
                    message="registry entries in the META-STABILITY-0 scope must declare stability",
                    item_id=item_id,
                )
            )
            continue
        errors.extend(_validate_marker_rules(stability, path="{}.stability".format(row_path), item_id=item_id))

    result = {
        "result": "complete" if not errors else "violation",
        "file_path": rel_path,
        "family": family_for_registry(rel_path),
        "collection_key": _token(collection_key),
        "entry_count": len(rows),
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


__all__ = [
    "PACK_COMPAT_REL_SUFFIX",
    "SCOPED_REGISTRY_PATHS",
    "STABILITY_MARKER_SCHEMA_NAME",
    "build_stability_marker",
    "stability_marker_fingerprint",
    "validate_pack_compat",
    "validate_registry",
    "validate_scoped_registries",
]
