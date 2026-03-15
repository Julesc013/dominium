"""Deterministic pack provides declaration and resolution helpers."""

from __future__ import annotations

import re
from typing import Dict, List, Mapping, Sequence

from src.meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256


PROVIDES_TYPE_DOMAIN = "domain"
PROVIDES_TYPE_DATASET = "dataset"
PROVIDES_TYPE_TEMPLATE_SET = "template_set"
PROVIDES_TYPE_UI_PACK = "ui_pack"
PROVIDES_TYPE_PROTOCOL_EXTENSION = "protocol_extension"

PROVIDES_TYPE_VALUES = (
    PROVIDES_TYPE_DOMAIN,
    PROVIDES_TYPE_DATASET,
    PROVIDES_TYPE_TEMPLATE_SET,
    PROVIDES_TYPE_UI_PACK,
    PROVIDES_TYPE_PROTOCOL_EXTENSION,
)

RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS = "resolve.strict_refuse_ambiguous"
RESOLUTION_POLICY_EXPLICIT_REQUIRED = "resolve.explicit_required"
RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY = "resolve.deterministic_highest_priority"
RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID = "resolve.deterministic_lowest_pack_id"

RESOLUTION_POLICY_VALUES = (
    RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    RESOLUTION_POLICY_EXPLICIT_REQUIRED,
    RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY,
    RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
)

REFUSAL_PACK_NAMESPACE_INVALID = "refusal.pack.namespace_invalid"
REFUSAL_PROVIDES_AMBIGUOUS = "refusal.provides.ambiguous"
REFUSAL_PROVIDES_MISSING_PROVIDER = "refusal.provides.missing_provider"
REFUSAL_PROVIDES_EXPLICIT_REQUIRED = "refusal.provides.explicit_required"
REFUSAL_PROVIDES_HASH_MISMATCH = "refusal.provides.hash_mismatch"

PACK_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
LEGACY_PACK_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*(?:\.[a-z0-9]+(?:[._-][a-z0-9]+)*)+$")
LEGACY_SHORT_PACK_IDS = {
    "base",
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _normalize_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(name): _normalize_value(item)
            for name, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    return value


def _sorted_unique_strings(values: object) -> List[str]:
    return sorted({str(value).strip() for value in _as_list(values) if str(value).strip()})


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def classify_pack_namespace(pack_id: str) -> Dict[str, object]:
    token = str(pack_id or "").strip()
    row = {
        "pack_id": token,
        "namespace_kind": "",
        "origin_pack_id": "",
        "valid": False,
        "message": "",
    }
    if not token:
        row["message"] = "pack_id is required"
        return row
    parts = token.split(".")
    if parts[0] == "fork":
        if len(parts) < 4:
            row["message"] = "fork pack ids must use fork.<origin_pack_id>.<fork_author>.<fork_name>"
            return row
        origin_pack_id = ".".join(parts[1:-2]).strip(".")
        fork_author = str(parts[-2] or "").strip()
        fork_name = str(parts[-1] or "").strip()
        if (
            not origin_pack_id
            or not LEGACY_PACK_ID_RE.fullmatch(origin_pack_id)
            or not PACK_TOKEN_RE.fullmatch(fork_author)
            or not PACK_TOKEN_RE.fullmatch(fork_name)
        ):
            row["message"] = "fork pack ids must use fork.<origin_pack_id>.<fork_author>.<fork_name>"
            return row
        row["namespace_kind"] = "fork"
        row["origin_pack_id"] = origin_pack_id
        row["valid"] = True
        return row
    if parts[0] in {"official", "mod", "local"}:
        if len(parts) < 3 or any(not PACK_TOKEN_RE.fullmatch(str(part or "").strip()) for part in parts[1:]):
            row["message"] = "pack ids must use official.<org>.<pack>, mod.<author>.<pack>, or local.<user>.<pack>"
            return row
        row["namespace_kind"] = parts[0]
        row["valid"] = True
        return row
    if token in LEGACY_SHORT_PACK_IDS:
        row["namespace_kind"] = "legacy_short"
        row["valid"] = True
        return row
    if LEGACY_PACK_ID_RE.fullmatch(token):
        row["namespace_kind"] = "legacy"
        row["valid"] = True
        return row
    row["message"] = "pack_id must use a supported namespace or legacy reverse-DNS id"
    return row


def normalize_provides_declaration(
    payload: Mapping[str, object] | str | None,
    *,
    fallback_pack_id: str = "",
) -> dict:
    if isinstance(payload, str):
        row = {"provides_id": str(payload).strip()}
    else:
        row = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    item = _as_map(row)
    pack_id = str(item.get("pack_id", "")).strip() or str(fallback_pack_id or "").strip()
    provides_type = str(item.get("provides_type", "")).strip() or PROVIDES_TYPE_DOMAIN
    if provides_type not in PROVIDES_TYPE_VALUES:
        provides_type = PROVIDES_TYPE_DOMAIN
    try:
        priority = int(item.get("priority", 0) or 0)
    except (TypeError, ValueError):
        priority = 0
    extensions = normalize_extensions_map(_as_map(item.get("extensions")))
    compatibility_notes = str(item.get("compatibility_notes", "")).strip()
    if compatibility_notes and "compatibility_notes" not in extensions:
        extensions["compatibility_notes"] = compatibility_notes
    required_capabilities = _sorted_unique_strings(item.get("required_capabilities") or extensions.get("required_capabilities"))
    if required_capabilities:
        extensions["required_capabilities"] = required_capabilities
    required_contract_ranges = _as_map(item.get("required_contract_ranges") or extensions.get("required_contract_ranges"))
    if required_contract_ranges:
        extensions["required_contract_ranges"] = {
            str(key): _normalize_value(value)
            for key, value in sorted(required_contract_ranges.items(), key=lambda entry: str(entry[0]))
            if str(key).strip() and isinstance(value, Mapping)
        }
    normalized = {
        "pack_id": pack_id,
        "provides_id": str(item.get("provides_id", "")).strip(),
        "provides_type": provides_type,
        "priority": priority,
        "deterministic_fingerprint": str(item.get("deterministic_fingerprint", "")).strip(),
        "extensions": extensions,
    }
    return _normalize_value(normalized)


def canonicalize_provides_declaration(
    payload: Mapping[str, object] | str | None,
    *,
    fallback_pack_id: str = "",
) -> dict:
    normalized = normalize_provides_declaration(payload, fallback_pack_id=fallback_pack_id)
    normalized["deterministic_fingerprint"] = ""
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return _normalize_value(normalized)


def validate_provides_declaration(
    payload: Mapping[str, object] | str | None,
    *,
    fallback_pack_id: str = "",
) -> Dict[str, object]:
    declaration = normalize_provides_declaration(payload, fallback_pack_id=fallback_pack_id)
    errors: List[dict] = []
    if not str(declaration.get("pack_id", "")).strip():
        errors.append(
            {
                "code": "provides_declaration_missing_pack_id",
                "path": "$.pack_id",
                "message": "pack_id is required",
            }
        )
    namespace_status = classify_pack_namespace(str(declaration.get("pack_id", "")).strip())
    if str(declaration.get("pack_id", "")).strip() and not bool(namespace_status.get("valid", False)):
        errors.append(
            {
                "code": REFUSAL_PACK_NAMESPACE_INVALID,
                "path": "$.pack_id",
                "message": str(namespace_status.get("message", "")).strip() or "pack_id namespace is invalid",
            }
        )
    if not str(declaration.get("provides_id", "")).strip():
        errors.append(
            {
                "code": "provides_declaration_missing_provides_id",
                "path": "$.provides_id",
                "message": "provides_id is required",
            }
        )
    if str(declaration.get("provides_type", "")).strip() not in PROVIDES_TYPE_VALUES:
        errors.append(
            {
                "code": "provides_declaration_invalid_type",
                "path": "$.provides_type",
                "message": "provides_type must be a registered provides type",
            }
        )
    expected_fingerprint = deterministic_fingerprint(declaration)
    if str(declaration.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
        errors.append(
            {
                "code": REFUSAL_PROVIDES_HASH_MISMATCH,
                "path": "$.deterministic_fingerprint",
                "message": "provides declaration deterministic_fingerprint mismatch",
            }
        )
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": str(errors[0].get("code", "")).strip() if errors else "",
        "errors": errors,
        "provides_declaration": declaration,
        "namespace_status": namespace_status,
    }


def normalize_provides_declarations(
    values: object,
    *,
    fallback_pack_id: str = "",
) -> List[dict]:
    rows: List[dict] = []
    for row in _as_list(values):
        normalized = canonicalize_provides_declaration(row, fallback_pack_id=fallback_pack_id)
        if not str(normalized.get("provides_id", "")).strip():
            continue
        rows.append(normalized)
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("provides_id", "")),
            str(item.get("pack_id", "")),
            -int(item.get("priority", 0) or 0),
        ),
    )


def normalize_provides_resolution(
    payload: Mapping[str, object] | None,
    *,
    instance_id: str = "",
    resolution_policy_id: str = "",
) -> dict:
    row = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    item = _as_map(row)
    policy_id = str(item.get("resolution_policy_id", "")).strip() or str(resolution_policy_id or "").strip()
    if policy_id and policy_id not in RESOLUTION_POLICY_VALUES:
        policy_id = RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY
    normalized = {
        "instance_id": str(item.get("instance_id", "")).strip() or str(instance_id or "").strip(),
        "provides_id": str(item.get("provides_id", "")).strip(),
        "chosen_pack_id": str(item.get("chosen_pack_id", "")).strip(),
        "resolution_policy_id": policy_id,
        "deterministic_fingerprint": str(item.get("deterministic_fingerprint", "")).strip(),
        "extensions": normalize_extensions_map(_as_map(item.get("extensions"))),
    }
    return _normalize_value(normalized)


def canonicalize_provides_resolution(
    payload: Mapping[str, object] | None,
    *,
    instance_id: str = "",
    resolution_policy_id: str = "",
) -> dict:
    normalized = normalize_provides_resolution(
        payload,
        instance_id=instance_id,
        resolution_policy_id=resolution_policy_id,
    )
    normalized["deterministic_fingerprint"] = ""
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return _normalize_value(normalized)


def validate_provides_resolution(
    payload: Mapping[str, object] | None,
    *,
    instance_id: str = "",
    resolution_policy_id: str = "",
) -> Dict[str, object]:
    resolution = normalize_provides_resolution(
        payload,
        instance_id=instance_id,
        resolution_policy_id=resolution_policy_id,
    )
    errors: List[dict] = []
    if not str(resolution.get("instance_id", "")).strip():
        errors.append(
            {
                "code": "provides_resolution_missing_instance_id",
                "path": "$.instance_id",
                "message": "instance_id is required",
            }
        )
    if not str(resolution.get("provides_id", "")).strip():
        errors.append(
            {
                "code": "provides_resolution_missing_provides_id",
                "path": "$.provides_id",
                "message": "provides_id is required",
            }
        )
    if not str(resolution.get("chosen_pack_id", "")).strip():
        errors.append(
            {
                "code": REFUSAL_PROVIDES_MISSING_PROVIDER,
                "path": "$.chosen_pack_id",
                "message": "chosen_pack_id is required",
            }
        )
    namespace_status = classify_pack_namespace(str(resolution.get("chosen_pack_id", "")).strip())
    if str(resolution.get("chosen_pack_id", "")).strip() and not bool(namespace_status.get("valid", False)):
        errors.append(
            {
                "code": REFUSAL_PACK_NAMESPACE_INVALID,
                "path": "$.chosen_pack_id",
                "message": str(namespace_status.get("message", "")).strip() or "chosen_pack_id namespace is invalid",
            }
        )
    if str(resolution.get("resolution_policy_id", "")).strip() not in RESOLUTION_POLICY_VALUES:
        errors.append(
            {
                "code": "provides_resolution_invalid_policy",
                "path": "$.resolution_policy_id",
                "message": "resolution_policy_id must be a registered resolution policy",
            }
        )
    expected_fingerprint = deterministic_fingerprint(resolution)
    if str(resolution.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
        errors.append(
            {
                "code": REFUSAL_PROVIDES_HASH_MISMATCH,
                "path": "$.deterministic_fingerprint",
                "message": "provides resolution deterministic_fingerprint mismatch",
            }
        )
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": str(errors[0].get("code", "")).strip() if errors else "",
        "errors": errors,
        "provides_resolution": resolution,
        "namespace_status": namespace_status,
    }


def normalize_provides_resolutions(
    values: object,
    *,
    instance_id: str = "",
    resolution_policy_id: str = "",
) -> List[dict]:
    rows: List[dict] = []
    for row in _as_list(values):
        normalized = canonicalize_provides_resolution(
            _as_map(row),
            instance_id=instance_id,
            resolution_policy_id=resolution_policy_id,
        )
        if not str(normalized.get("provides_id", "")).strip():
            continue
        rows.append(normalized)
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("provides_id", "")),
            str(item.get("chosen_pack_id", "")),
            str(item.get("resolution_policy_id", "")),
        ),
    )


def infer_resolution_policy_id(
    *,
    mod_policy_id: str = "",
    overlay_conflict_policy_id: str = "",
    preferred_policy_id: str = "",
) -> str:
    preferred = str(preferred_policy_id or "").strip()
    if preferred in RESOLUTION_POLICY_VALUES:
        return preferred
    mod_policy = str(mod_policy_id or "").strip()
    overlay_policy = str(overlay_conflict_policy_id or "").strip()
    if mod_policy in {"mod_policy.strict", "mod.policy.strict"} or overlay_policy in {"overlay.conflict.refuse", "overlay.conflict.prompt_stub"}:
        return RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS
    if mod_policy in {"mod_policy.anarchy", "mod.policy.anarchy"}:
        return RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID
    return RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY


def resolve_providers(
    *,
    instance_id: str,
    required_provides_ids: Sequence[str] | None,
    provider_declarations: Sequence[Mapping[str, object]] | None,
    explicit_resolutions: Sequence[Mapping[str, object]] | None = None,
    resolution_policy_id: str = "",
    mod_policy_id: str = "",
    overlay_conflict_policy_id: str = "",
) -> Dict[str, object]:
    required_ids = sorted({str(value).strip() for value in list(required_provides_ids or []) if str(value).strip()})
    declarations = normalize_provides_declarations(list(provider_declarations or []))
    policy_id = infer_resolution_policy_id(
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        preferred_policy_id=resolution_policy_id,
    )
    explicit_rows = normalize_provides_resolutions(
        list(explicit_resolutions or []),
        instance_id=instance_id,
        resolution_policy_id=policy_id,
    )
    explicit_by_id = {
        str(row.get("provides_id", "")).strip(): row
        for row in explicit_rows
        if str(row.get("provides_id", "")).strip()
    }
    providers_by_id: Dict[str, List[dict]] = {}
    for row in declarations:
        provides_id = str(row.get("provides_id", "")).strip()
        if not provides_id:
            continue
        providers_by_id.setdefault(provides_id, []).append(row)
    for provides_id in list(providers_by_id.keys()):
        providers_by_id[provides_id] = sorted(
            providers_by_id[provides_id],
            key=lambda row: (
                -int(row.get("priority", 0) or 0),
                str(row.get("pack_id", "")),
            ),
        )

    errors: List[dict] = []
    chosen_resolutions: List[dict] = []
    implied_capabilities: List[str] = []
    ambiguous_ids: List[str] = []
    auto_selected_ids: List[str] = []

    for provides_id in required_ids:
        candidates = list(providers_by_id.get(provides_id, []))
        candidate_pack_ids = sorted({str(row.get("pack_id", "")).strip() for row in candidates if str(row.get("pack_id", "")).strip()})
        explicit = explicit_by_id.get(provides_id)
        chosen_pack_id = ""
        selection_mode = ""
        if not candidates:
            errors.append(
                {
                    "code": REFUSAL_PROVIDES_MISSING_PROVIDER,
                    "path": "$.required_provides_ids",
                    "message": "required provides_id '{}' has no provider".format(provides_id),
                }
            )
            continue
        if policy_id == RESOLUTION_POLICY_EXPLICIT_REQUIRED:
            if not explicit:
                errors.append(
                    {
                        "code": REFUSAL_PROVIDES_EXPLICIT_REQUIRED,
                        "path": "$.provides_resolutions",
                        "message": "required provides_id '{}' requires an explicit resolution".format(provides_id),
                    }
                )
                continue
            chosen_pack_id = str(explicit.get("chosen_pack_id", "")).strip()
            selection_mode = "explicit"
        elif policy_id == RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS:
            if len(candidates) > 1:
                ambiguous_ids.append(provides_id)
                errors.append(
                    {
                        "code": REFUSAL_PROVIDES_AMBIGUOUS,
                        "path": "$.required_provides_ids",
                        "message": "required provides_id '{}' is ambiguous".format(provides_id),
                    }
                )
                continue
            chosen_pack_id = str(candidates[0].get("pack_id", "")).strip()
            selection_mode = "strict_single"
        elif policy_id == RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY:
            chosen_pack_id = str(candidates[0].get("pack_id", "")).strip()
            selection_mode = "deterministic_highest_priority"
            if len(candidates) > 1:
                auto_selected_ids.append(provides_id)
        else:
            chosen_pack_id = sorted(candidate_pack_ids)[0]
            selection_mode = "deterministic_lowest_pack_id"
            if len(candidates) > 1:
                auto_selected_ids.append(provides_id)

        if explicit and chosen_pack_id != str(explicit.get("chosen_pack_id", "")).strip():
            chosen_pack_id = str(explicit.get("chosen_pack_id", "")).strip()
            selection_mode = "explicit_override"
        if chosen_pack_id not in candidate_pack_ids:
            errors.append(
                {
                    "code": REFUSAL_PROVIDES_MISSING_PROVIDER,
                    "path": "$.provides_resolutions",
                    "message": "chosen provider '{}' is not available for '{}'".format(chosen_pack_id or "unknown", provides_id),
                }
            )
            continue
        chosen_declaration = next(
            (
                row
                for row in candidates
                if str(row.get("pack_id", "")).strip() == chosen_pack_id
            ),
            {},
        )
        required_caps = _sorted_unique_strings(_as_map(chosen_declaration.get("extensions")).get("required_capabilities"))
        implied_capabilities.extend(required_caps)
        chosen_resolutions.append(
            canonicalize_provides_resolution(
                {
                    "instance_id": instance_id,
                    "provides_id": provides_id,
                    "chosen_pack_id": chosen_pack_id,
                    "resolution_policy_id": policy_id,
                    "extensions": {
                        "candidate_pack_ids": candidate_pack_ids,
                        "selection_logged": True,
                        "selection_mode": selection_mode,
                    },
                },
                instance_id=instance_id,
                resolution_policy_id=policy_id,
            )
        )

    refusal_code = str(errors[0].get("code", "")).strip() if errors else ""
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": refusal_code,
        "resolution_policy_id": policy_id,
        "required_provides_ids": required_ids,
        "provider_declarations": declarations,
        "provides_resolutions": sorted(
            chosen_resolutions,
            key=lambda row: (
                str(row.get("provides_id", "")),
                str(row.get("chosen_pack_id", "")),
            ),
        ),
        "implied_capabilities": sorted(set(implied_capabilities)),
        "ambiguous_provides_ids": sorted(set(ambiguous_ids)),
        "auto_selected_provides_ids": sorted(set(auto_selected_ids)),
        "selection_logged": bool(chosen_resolutions) or bool(auto_selected_ids),
        "errors": errors,
    }


__all__ = [
    "PROVIDES_TYPE_DATASET",
    "PROVIDES_TYPE_DOMAIN",
    "PROVIDES_TYPE_PROTOCOL_EXTENSION",
    "PROVIDES_TYPE_TEMPLATE_SET",
    "PROVIDES_TYPE_UI_PACK",
    "PROVIDES_TYPE_VALUES",
    "REFUSAL_PACK_NAMESPACE_INVALID",
    "REFUSAL_PROVIDES_AMBIGUOUS",
    "REFUSAL_PROVIDES_EXPLICIT_REQUIRED",
    "REFUSAL_PROVIDES_HASH_MISMATCH",
    "REFUSAL_PROVIDES_MISSING_PROVIDER",
    "RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY",
    "RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID",
    "RESOLUTION_POLICY_EXPLICIT_REQUIRED",
    "RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS",
    "RESOLUTION_POLICY_VALUES",
    "canonicalize_provides_declaration",
    "canonicalize_provides_resolution",
    "classify_pack_namespace",
    "deterministic_fingerprint",
    "infer_resolution_policy_id",
    "normalize_provides_declaration",
    "normalize_provides_declarations",
    "normalize_provides_resolution",
    "normalize_provides_resolutions",
    "resolve_providers",
    "validate_provides_declaration",
    "validate_provides_resolution",
]
