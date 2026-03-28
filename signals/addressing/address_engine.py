"""SIG-2 deterministic address resolution engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def deterministic_address_id(*, address_type: str, target_id: str) -> str:
    digest = canonical_sha256(
        {
            "address_type": str(address_type or "").strip().lower() or "subject",
            "target_id": str(target_id or "").strip(),
        }
    )
    return "address.signal.{}".format(digest[:16])


def build_address(
    *,
    address_id: str,
    address_type: str,
    target_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    type_token = str(address_type or "").strip().lower() or "subject"
    if type_token not in {"subject", "group", "broadcast"}:
        type_token = "subject"
    payload = {
        "schema_version": "1.0.0",
        "address_id": str(address_id or "").strip(),
        "address_type": type_token,
        "target_id": str(target_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["address_id"] or not payload["target_id"]:
        return {}
    return _with_fingerprint(payload)


def normalize_address_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    by_id: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("address_id", ""))):
        address_id = str(row.get("address_id", "")).strip()
        if not address_id:
            continue
        built = build_address(
            address_id=address_id,
            address_type=str(row.get("address_type", "subject")).strip() or "subject",
            target_id=str(row.get("target_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if built:
            by_id[address_id] = built
    return [dict(by_id[key]) for key in sorted(by_id.keys())]


def addressing_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("addressing_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("addressing_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("addressing_policy_id", ""))):
        policy_id = str(row.get("addressing_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "addressing_policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "supported_address_types": _sorted_tokens(row.get("supported_address_types")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def address_from_recipient_address(recipient_address: Mapping[str, object]) -> dict:
    payload = _as_map(recipient_address)
    kind = str(payload.get("kind", "single")).strip().lower() or "single"
    if kind in {"single", "subject", "unicast"}:
        address_type = "subject"
        target_id = str(payload.get("subject_id", "")).strip()
    elif kind in {"group", "multicast"}:
        address_type = "group"
        target_id = str(payload.get("group_id", "")).strip()
        if (not target_id) and _sorted_tokens(payload.get("subject_ids")):
            target_id = "group.inline.{}".format(
                canonical_sha256({"subject_ids": _sorted_tokens(payload.get("subject_ids"))})[:16]
            )
    else:
        address_type = "broadcast"
        target_id = str(payload.get("broadcast_scope", "")).strip() or str(payload.get("scope_id", "")).strip()
        if (not target_id) and _sorted_tokens(payload.get("broadcast_subject_ids")):
            target_id = "scope.inline.{}".format(
                canonical_sha256({"subject_ids": _sorted_tokens(payload.get("broadcast_subject_ids"))})[:16]
            )
    if not target_id:
        target_id = "unknown.target"
    return build_address(
        address_id=deterministic_address_id(address_type=address_type, target_id=target_id),
        address_type=address_type,
        target_id=target_id,
        extensions={
            "to_node_id": str(payload.get("to_node_id", "")).strip() or "node.unknown",
            "subject_ids": _sorted_tokens(payload.get("subject_ids")),
            "broadcast_subject_ids": _sorted_tokens(payload.get("broadcast_subject_ids")),
        },
    )


def _group_members_by_id(group_membership_rows: object) -> Dict[str, List[str]]:
    if not isinstance(group_membership_rows, list):
        group_membership_rows = []
    out: Dict[str, List[str]] = {}
    for row in sorted((dict(item) for item in group_membership_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("group_id", ""))):
        group_id = str(row.get("group_id", "")).strip()
        if not group_id:
            continue
        out[group_id] = _sorted_tokens(row.get("subject_ids"))
    return dict((key, list(out[key])) for key in sorted(out.keys()))


def _broadcast_members_by_scope(broadcast_scope_rows: object) -> Dict[str, List[str]]:
    if not isinstance(broadcast_scope_rows, list):
        broadcast_scope_rows = []
    out: Dict[str, List[str]] = {}
    for row in sorted((dict(item) for item in broadcast_scope_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("broadcast_scope", ""))):
        scope = str(row.get("broadcast_scope", "")).strip() or str(row.get("scope_id", "")).strip()
        if not scope:
            continue
        out[scope] = _sorted_tokens(row.get("subject_ids"))
    return dict((key, list(out[key])) for key in sorted(out.keys()))


def resolve_address_recipients(
    *,
    address_row: Mapping[str, object],
    group_membership_rows: object = None,
    broadcast_scope_rows: object = None,
) -> dict:
    row = dict(address_row or {})
    addr_type = str(row.get("address_type", "subject")).strip().lower() or "subject"
    target_id = str(row.get("target_id", "")).strip()
    ext = _as_map(row.get("extensions"))
    to_node_id = str(ext.get("to_node_id", "")).strip() or "node.unknown"

    recipients: List[str] = []
    if addr_type == "subject":
        if target_id and target_id != "unknown.target":
            recipients = [target_id]
    elif addr_type == "group":
        group_members = _group_members_by_id(group_membership_rows)
        recipients = list(group_members.get(target_id) or _sorted_tokens(ext.get("subject_ids")))
    elif addr_type == "broadcast":
        scope_members = _broadcast_members_by_scope(broadcast_scope_rows)
        recipients = list(scope_members.get(target_id) or _sorted_tokens(ext.get("broadcast_subject_ids")))
    recipients = sorted(set(str(token).strip() for token in recipients if str(token).strip()))

    return {
        "address_row": dict(row),
        "recipient_subject_ids": list(recipients),
        "recipient_rows": [
            {
                "recipient_subject_id": subject_id,
                "to_node_id": to_node_id,
            }
            for subject_id in recipients
        ],
        "resolved_count": int(len(recipients)),
        "unresolved": bool(len(recipients) == 0),
    }


__all__ = [
    "address_from_recipient_address",
    "addressing_policy_rows_by_id",
    "build_address",
    "deterministic_address_id",
    "normalize_address_rows",
    "resolve_address_recipients",
]
