"""Runtime-owned server authority helpers."""

from __future__ import annotations

from typing import Mapping


REFUSAL_CLIENT_UNAUTHORIZED = "refusal.client.unauthorized"
REFUSAL_CLIENT_READ_ONLY = "refusal.client.read_only_connection"


def _connection_entitlements(
    server_profile: Mapping[str, object] | None,
    session_authority: Mapping[str, object] | None = None,
) -> list[str]:
    rows = []
    rows.extend(list((dict(server_profile or {}).get("allowed_entitlements") or [])))
    rows.extend(list((dict(session_authority or {}).get("entitlements") or [])))
    return sorted(set(str(item).strip() for item in rows if str(item).strip()))


def build_connection_authority_context(
    *,
    session_spec: Mapping[str, object],
    server_profile: Mapping[str, object],
    connection_id: str,
    account_id: str,
    law_profile_id_override: str = "",
    entitlements_override: list[str] | None = None,
) -> dict:
    session_authority = dict((dict(session_spec or {})).get("authority_context") or {})
    selected_law_profile_id = str(law_profile_id_override or session_authority.get("law_profile_id", "")).strip()
    selected_entitlements = (
        sorted(set(str(item).strip() for item in list(entitlements_override or []) if str(item).strip()))
        if entitlements_override is not None
        else _connection_entitlements(server_profile, session_authority)
    )
    return {
        "authority_origin": "client",
        "experience_id": str(session_authority.get("experience_id", "")).strip(),
        "law_profile_id": selected_law_profile_id,
        "entitlements": selected_entitlements,
        "epistemic_scope": dict(session_authority.get("epistemic_scope") or {}),
        "privilege_level": str(session_authority.get("privilege_level", "")).strip(),
        "extensions": {
            "official.connection_id": str(connection_id).strip(),
            "official.account_id": str(account_id).strip(),
        },
    }


__all__ = [
    "REFUSAL_CLIENT_READ_ONLY",
    "REFUSAL_CLIENT_UNAUTHORIZED",
    "build_connection_authority_context",
]
