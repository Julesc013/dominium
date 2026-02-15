"""Deterministic multiplayer handshake + compatibility gate for session pipeline net stage."""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.net.transport.loopback import LoopbackTransport
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.schema_registry import load_version_registry
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.compatx.versioning import resolve_payload_version

from .common import refusal
from .net_protocol import build_proto_message, decode_proto_message, encode_proto_message


HANDSHAKE_PROTOCOL_VERSION = "1.0.0"
HANDSHAKE_SCHEMA_VERSION = "1.0.0"

_REQUIRED_NETWORK_FIELDS = (
    "endpoint",
    "transport_id",
    "client_peer_id",
    "server_peer_id",
    "requested_replication_policy_id",
    "anti_cheat_policy_id",
    "server_policy_id",
    "securex_policy_id",
    "schema_versions",
)


def _sorted_unique_strings(values: object) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _first_registry_mismatch(expected: dict, actual: dict) -> Tuple[str, str, str]:
    expected_rows = dict(expected or {})
    actual_rows = dict(actual or {})
    for key in sorted(set(expected_rows.keys()) | set(actual_rows.keys())):
        left = str(expected_rows.get(key, "")).strip()
        right = str(actual_rows.get(key, "")).strip()
        if left != right:
            return str(key), left, right
    return "", "", ""


def _empty_refusal() -> dict:
    return {
        "reason_code": "",
        "message": "",
        "remediation_hint": "",
        "relevant_ids": {},
    }


def _handshake_payload(
    *,
    handshake_id: str,
    client_peer_id: str,
    server_peer_id: str,
    requested_replication_policy_id: str,
    negotiated_replication_policy_id: str,
    anti_cheat_policy_id: str,
    server_law_profile_id: str,
    pack_lock_hash: str,
    registry_hashes: dict,
    schema_versions: dict,
    securex_policy_id: str,
    result: str,
    refusal_payload: dict,
    server_policy_id: str,
) -> dict:
    return {
        "schema_version": HANDSHAKE_SCHEMA_VERSION,
        "handshake_id": str(handshake_id),
        "protocol_version": HANDSHAKE_PROTOCOL_VERSION,
        "client_peer_id": str(client_peer_id),
        "server_peer_id": str(server_peer_id),
        "requested_replication_policy_id": str(requested_replication_policy_id),
        "negotiated_replication_policy_id": str(negotiated_replication_policy_id),
        "anti_cheat_policy_id": str(anti_cheat_policy_id),
        "server_law_profile_id": str(server_law_profile_id),
        "pack_lock_hash": str(pack_lock_hash),
        "registry_hashes": dict(registry_hashes or {}),
        "schema_versions": dict(schema_versions or {}),
        "securex_policy_id": str(securex_policy_id),
        "result": str(result),
        "refusal": dict(refusal_payload or _empty_refusal()),
        "extensions": {
            "server_policy_id": str(server_policy_id),
        },
    }


def _validation_refusal(code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str]) -> dict:
    return {
        "reason_code": str(code),
        "message": str(message),
        "remediation_hint": str(remediation_hint),
        "relevant_ids": dict(relevant_ids or {}),
    }


def _schema_version_supported(repo_root: str, schema_versions: dict) -> Tuple[bool, dict]:
    version_registry, error = load_version_registry(repo_root=repo_root)
    if error:
        return False, _validation_refusal(
            "refusal.net.handshake_schema_version_mismatch",
            "compatx version registry is unavailable for handshake schema version checks",
            "Restore tools/xstack/compatx/version_registry.json and retry handshake.",
            {"schema_id": "version_registry"},
        )

    rows = ((version_registry.get("schemas") or {}) if isinstance(version_registry, dict) else {})
    if not isinstance(rows, dict):
        return False, _validation_refusal(
            "refusal.net.handshake_schema_version_mismatch",
            "compatx version registry has invalid schema mapping structure",
            "Repair tools/xstack/compatx/version_registry.json and retry handshake.",
            {"schema_id": "version_registry"},
        )

    for schema_name in sorted(str(key).strip() for key in (schema_versions or {}).keys() if str(key).strip()):
        payload_version = str((schema_versions or {}).get(schema_name, "")).strip()
        row = rows.get(schema_name)
        if not isinstance(row, dict):
            return False, _validation_refusal(
                "refusal.net.handshake_schema_version_mismatch",
                "handshake references unknown schema '{}'".format(schema_name),
                "Use schemas declared in compatx version registry.",
                {"schema_id": schema_name},
            )
        current_version = str(row.get("current_version", "")).strip()
        supported_versions = row.get("supported_versions")
        if not isinstance(supported_versions, list):
            supported_versions = []
        resolved = resolve_payload_version(
            schema_name=schema_name,
            payload_version=payload_version,
            current_version=current_version,
            supported_versions=list(supported_versions),
            version_field="schema_version",
        )
        if not bool(resolved.get("ok", False)):
            return False, _validation_refusal(
                "refusal.net.handshake_schema_version_mismatch",
                "schema '{}' version '{}' is not compatible".format(schema_name, payload_version or "<empty>"),
                "Use a schema version supported by compatx for '{}'".format(schema_name),
                {"schema_id": schema_name},
            )
    return True, {}


def _policy_map(rows: object, key: str = "policy_id") -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted([item for item in rows if isinstance(item, dict)], key=lambda item: str(item.get(key, ""))):
        token = str(row.get(key, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _server_response(
    *,
    repo_root: str,
    request_payload: dict,
    lock_payload: dict,
    replication_registry: dict,
    anti_cheat_registry: dict,
    server_policy_registry: dict,
    authority_context: dict,
) -> dict:
    handshake_id = str(request_payload.get("handshake_id", "")).strip()
    client_peer_id = str(request_payload.get("client_peer_id", "")).strip()
    server_peer_id = str(request_payload.get("server_peer_id", "")).strip()
    requested_policy_id = str(request_payload.get("requested_replication_policy_id", "")).strip()
    anti_cheat_policy_id = str(request_payload.get("anti_cheat_policy_id", "")).strip()
    server_policy_id = str(request_payload.get("server_policy_id", "")).strip()
    request_securex_policy_id = str(request_payload.get("securex_policy_id", "")).strip()
    requested_law_profile_id = str(request_payload.get("desired_law_profile_id", "")).strip()
    schema_versions = dict(request_payload.get("schema_versions") or {})
    request_registry_hashes = dict(request_payload.get("registry_hashes") or {})
    expected_registry_hashes = dict(lock_payload.get("registries") or {})
    pack_lock_hash = str(lock_payload.get("pack_lock_hash", "")).strip()

    def refuse(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str], law_profile_id: str = "") -> dict:
        return _handshake_payload(
            handshake_id=handshake_id,
            client_peer_id=client_peer_id,
            server_peer_id=server_peer_id,
            requested_replication_policy_id=requested_policy_id,
            negotiated_replication_policy_id=requested_policy_id,
            anti_cheat_policy_id=anti_cheat_policy_id,
            server_law_profile_id=law_profile_id,
            pack_lock_hash=pack_lock_hash,
            registry_hashes=expected_registry_hashes,
            schema_versions=schema_versions,
            securex_policy_id=request_securex_policy_id,
            result="refuse",
            refusal_payload=_validation_refusal(reason_code, message, remediation_hint, relevant_ids),
            server_policy_id=server_policy_id,
        )

    if str(request_payload.get("pack_lock_hash", "")).strip() != pack_lock_hash:
        return refuse(
            "refusal.net.handshake_pack_lock_mismatch",
            "client pack_lock_hash does not match server lock hash",
            "Use a client build generated from the same lockfile.",
            {"client_peer_id": client_peer_id, "server_peer_id": server_peer_id},
        )

    mismatch_key, mismatch_expected, mismatch_actual = _first_registry_mismatch(expected_registry_hashes, request_registry_hashes)
    if mismatch_key:
        return refuse(
            "refusal.net.handshake_registry_hash_mismatch",
            "registry hash mismatch for '{}'".format(mismatch_key),
            "Rebuild client registries from matching bundle inputs and retry handshake.",
            {
                "registry_key": mismatch_key,
                "expected_hash": mismatch_expected,
                "actual_hash": mismatch_actual,
            },
        )

    schema_ok, schema_refusal = _schema_version_supported(repo_root=repo_root, schema_versions=schema_versions)
    if not schema_ok:
        return _handshake_payload(
            handshake_id=handshake_id,
            client_peer_id=client_peer_id,
            server_peer_id=server_peer_id,
            requested_replication_policy_id=requested_policy_id,
            negotiated_replication_policy_id=requested_policy_id,
            anti_cheat_policy_id=anti_cheat_policy_id,
            server_law_profile_id="",
            pack_lock_hash=pack_lock_hash,
            registry_hashes=expected_registry_hashes,
            schema_versions=schema_versions,
            securex_policy_id=request_securex_policy_id,
            result="refuse",
            refusal_payload=schema_refusal,
            server_policy_id=server_policy_id,
        )

    replication_map = _policy_map(replication_registry.get("policies"), key="policy_id")
    anti_cheat_map = _policy_map(anti_cheat_registry.get("policies"), key="policy_id")
    server_policy_map = _policy_map(server_policy_registry.get("policies"), key="policy_id")
    server_policy = dict(server_policy_map.get(server_policy_id) or {})
    if not server_policy:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "server policy '{}' is not present in compiled server policy registry".format(server_policy_id),
            "Select a server policy declared in build/registries/net_server_policy.registry.json.",
            {"server_policy_id": server_policy_id or "<empty>"},
        )

    if requested_policy_id not in replication_map:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "requested replication policy '{}' is unknown".format(requested_policy_id),
            "Use a replication policy from net_replication_policy.registry.json.",
            {"requested_replication_policy_id": requested_policy_id or "<empty>"},
        )

    allowed_replication = _sorted_unique_strings(server_policy.get("allowed_replication_policy_ids"))
    if requested_policy_id not in allowed_replication:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "requested replication policy is not allowed by server policy",
            "Use a replication policy allowed by the selected server policy.",
            {
                "requested_replication_policy_id": requested_policy_id,
                "server_policy_id": server_policy_id,
            },
        )

    if anti_cheat_policy_id not in anti_cheat_map:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "requested anti-cheat policy '{}' is unknown".format(anti_cheat_policy_id),
            "Use an anti-cheat policy from anti_cheat_policy.registry.json.",
            {"anti_cheat_policy_id": anti_cheat_policy_id or "<empty>"},
        )
    allowed_anti_cheat = _sorted_unique_strings(server_policy.get("allowed_anti_cheat_policy_ids"))
    if anti_cheat_policy_id not in allowed_anti_cheat:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "requested anti-cheat policy is not allowed by server policy",
            "Use an anti-cheat policy allowed by the selected server policy.",
            {
                "anti_cheat_policy_id": anti_cheat_policy_id,
                "server_policy_id": server_policy_id,
            },
        )
    required_anti_cheat = str(server_policy.get("required_anti_cheat_policy_id", "")).strip()
    if required_anti_cheat and anti_cheat_policy_id != required_anti_cheat:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "server policy requires anti-cheat policy '{}'".format(required_anti_cheat),
            "Reconnect using the required anti-cheat policy.",
            {
                "required_anti_cheat_policy_id": required_anti_cheat,
                "server_policy_id": server_policy_id,
            },
        )

    server_securex_policy_id = str(server_policy.get("securex_policy_id", "")).strip()
    if server_securex_policy_id and request_securex_policy_id != server_securex_policy_id:
        return refuse(
            "refusal.net.handshake_securex_denied",
            "securex policy id does not match server requirement",
            "Set network securex policy id to the required server value.",
            {
                "required_securex_policy_id": server_securex_policy_id,
                "server_policy_id": server_policy_id,
            },
        )
    if bool(server_policy.get("securex_require_signed", False)):
        unsigned_rows = [
            str(row.get("pack_id", "")).strip()
            for row in sorted(lock_payload.get("resolved_packs") or [], key=lambda item: str((item or {}).get("pack_id", "")))
            if isinstance(row, dict) and str(row.get("signature_status", "")).strip() != "official"
        ]
        if unsigned_rows:
            return refuse(
                "refusal.net.handshake_securex_denied",
                "server policy requires signed packs but unsigned content is present",
                "Use a signed pack set or connect to a non-ranked server policy.",
                {
                    "server_policy_id": server_policy_id,
                    "unsigned_pack_id": unsigned_rows[0],
                },
            )

    allowed_law_profiles = _sorted_unique_strings(server_policy.get("allowed_law_profile_ids"))
    authority_law_profile = str(authority_context.get("law_profile_id", "")).strip()
    selected_law_profile = ""
    if requested_law_profile_id and requested_law_profile_id in allowed_law_profiles:
        selected_law_profile = requested_law_profile_id
    elif authority_law_profile in allowed_law_profiles:
        selected_law_profile = authority_law_profile
    elif allowed_law_profiles:
        selected_law_profile = allowed_law_profiles[0]
    if not selected_law_profile:
        return refuse(
            "refusal.net.handshake_policy_not_allowed",
            "server policy does not provide any compatible law profile",
            "Choose a server policy with at least one allowed law profile.",
            {"server_policy_id": server_policy_id},
        )

    return _handshake_payload(
        handshake_id=handshake_id,
        client_peer_id=client_peer_id,
        server_peer_id=server_peer_id,
        requested_replication_policy_id=requested_policy_id,
        negotiated_replication_policy_id=requested_policy_id,
        anti_cheat_policy_id=anti_cheat_policy_id,
        server_law_profile_id=selected_law_profile,
        pack_lock_hash=pack_lock_hash,
        registry_hashes=expected_registry_hashes,
        schema_versions=schema_versions,
        securex_policy_id=server_securex_policy_id or request_securex_policy_id,
        result="accept",
        refusal_payload=_empty_refusal(),
        server_policy_id=server_policy_id,
    )


def _require_network_payload(session_spec: dict) -> Tuple[dict, dict]:
    network = session_spec.get("network")
    if not isinstance(network, dict):
        return {}, refusal(
            "refusal.net.handshake_policy_not_allowed",
            "SessionSpec is missing required network handshake configuration",
            "Populate session_spec.network fields for multiplayer pipeline execution.",
            {"schema_id": "session_spec"},
            "$.network",
        )
    for field in _REQUIRED_NETWORK_FIELDS:
        value = network.get(field)
        if field == "schema_versions":
            if not isinstance(value, dict) or not value:
                return {}, refusal(
                    "refusal.net.handshake_schema_version_mismatch",
                    "SessionSpec network schema_versions must be a non-empty object",
                    "Populate network.schema_versions with supported schema versions.",
                    {"schema_id": "session_spec"},
                    "$.network.schema_versions",
                )
            continue
        if field == "securex_policy_id":
            if field not in network:
                return {}, refusal(
                    "refusal.net.envelope_invalid",
                    "SessionSpec network field '{}' is required".format(field),
                    "Set network.{} explicitly before handshake.".format(field),
                    {"schema_id": "session_spec"},
                    "$.network.{}".format(field),
                )
            continue
        if not str(value).strip():
            return {}, refusal(
                "refusal.net.envelope_invalid",
                "SessionSpec network field '{}' is required".format(field),
                "Set network.{} explicitly before handshake.".format(field),
                {"schema_id": "session_spec"},
                "$.network.{}".format(field),
            )
    return dict(network), {}


def run_loopback_handshake(
    *,
    repo_root: str,
    session_spec: dict,
    lock_payload: dict,
    replication_registry: dict,
    anti_cheat_registry: dict,
    server_policy_registry: dict,
    authority_context: dict,
    client_pack_lock_hash: str = "",
    client_registry_hashes: Dict[str, str] | None = None,
) -> Dict[str, object]:
    network_payload, network_error = _require_network_payload(session_spec=session_spec)
    if network_error:
        return network_error

    transport_id = str(network_payload.get("transport_id", "")).strip()
    if transport_id != "transport.loopback":
        return refusal(
            "refusal.not_implemented.net_transport",
            "transport '{}' is not implemented for MP-2 handshake".format(transport_id or "<empty>"),
            "Use transport.loopback for MP-2 deterministic handshake.",
            {"transport_id": transport_id or "<empty>"},
            "$.network.transport_id",
        )

    server_pack_lock_hash = str(lock_payload.get("pack_lock_hash", "")).strip()
    session_pack_lock_hash = str(session_spec.get("pack_lock_hash", "")).strip()
    client_pack_lock_hash_value = (
        str(client_pack_lock_hash).strip()
        or session_pack_lock_hash
        or server_pack_lock_hash
    )
    client_registry_hashes_value = (
        dict(client_registry_hashes or {})
        if isinstance(client_registry_hashes, dict) and client_registry_hashes
        else dict(lock_payload.get("registries") or {})
    )

    request_seed = {
        "client_peer_id": str(network_payload.get("client_peer_id", "")).strip(),
        "server_peer_id": str(network_payload.get("server_peer_id", "")).strip(),
        "requested_replication_policy_id": str(network_payload.get("requested_replication_policy_id", "")).strip(),
        "anti_cheat_policy_id": str(network_payload.get("anti_cheat_policy_id", "")).strip(),
        "server_policy_id": str(network_payload.get("server_policy_id", "")).strip(),
        "pack_lock_hash": client_pack_lock_hash_value,
        "registry_hashes": client_registry_hashes_value,
    }
    handshake_id = "hs.{}".format(canonical_sha256(request_seed)[:16])
    request_payload = {
        "schema_version": HANDSHAKE_SCHEMA_VERSION,
        "handshake_id": handshake_id,
        "protocol_version": HANDSHAKE_PROTOCOL_VERSION,
        "client_peer_id": str(network_payload.get("client_peer_id", "")).strip(),
        "server_peer_id": str(network_payload.get("server_peer_id", "")).strip(),
        "requested_replication_policy_id": str(network_payload.get("requested_replication_policy_id", "")).strip(),
        "anti_cheat_policy_id": str(network_payload.get("anti_cheat_policy_id", "")).strip(),
        "server_policy_id": str(network_payload.get("server_policy_id", "")).strip(),
        "desired_law_profile_id": str(network_payload.get("desired_law_profile_id", "")).strip(),
        "pack_lock_hash": client_pack_lock_hash_value,
        "registry_hashes": dict(client_registry_hashes_value),
        "schema_versions": dict(network_payload.get("schema_versions") or {}),
        "securex_policy_id": str(network_payload.get("securex_policy_id", "")).strip(),
        "extensions": {},
    }

    request_message = build_proto_message(
        msg_type="handshake_request",
        msg_id="msg.handshake_request.{}".format(handshake_id),
        sequence=1,
        payload_schema_id="net_handshake_request",
        payload_inline_json=request_payload,
    )

    listener = LoopbackTransport.listen(
        endpoint=str(network_payload.get("endpoint", "")).strip(),
        server_peer_id=str(network_payload.get("server_peer_id", "")).strip(),
    )
    client = LoopbackTransport(peer_id=str(network_payload.get("client_peer_id", "")).strip(), role="client")
    connected = client.connect(str(network_payload.get("endpoint", "")).strip())
    if connected.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "loopback transport connect failed for handshake",
            "Ensure network endpoint is valid and retry handshake.",
            {
                "endpoint": str(network_payload.get("endpoint", "")).strip(),
            },
            "$.network.endpoint",
        )
    accepted = listener.accept()
    if accepted.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "loopback transport accept failed for handshake",
            "Ensure server listener is bound before client connect.",
            {
                "endpoint": str(network_payload.get("endpoint", "")).strip(),
            },
            "$.network.endpoint",
        )

    sent = client.send(encode_proto_message(request_message))
    if sent.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "failed to send handshake request envelope",
            "Retry handshake after reconnecting transport.",
            {"handshake_id": handshake_id},
            "$.network",
        )

    received_by_server = listener.recv()
    if received_by_server.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "server did not receive handshake request envelope",
            "Retry handshake after reconnecting transport.",
            {"handshake_id": handshake_id},
            "$.network",
        )
    decoded_request = decode_proto_message(repo_root=repo_root, message_bytes=bytes(received_by_server.get("message_bytes") or b""))
    if decoded_request.get("result") != "complete":
        return decoded_request
    request_proto_payload = dict((decoded_request.get("proto_message") or {}).get("payload_ref", {})).get("inline_json")
    if not isinstance(request_proto_payload, dict):
        return refusal(
            "refusal.net.envelope_invalid",
            "handshake request payload_ref.inline_json must be object",
            "Encode handshake payload using canonical proto wrapper.",
            {"handshake_id": handshake_id},
            "$.payload_ref.inline_json",
        )

    response_payload = _server_response(
        repo_root=repo_root,
        request_payload=request_proto_payload,
        lock_payload=lock_payload,
        replication_registry=replication_registry,
        anti_cheat_registry=anti_cheat_registry,
        server_policy_registry=server_policy_registry,
        authority_context=authority_context,
    )
    response_validated = validate_instance(
        repo_root=repo_root,
        schema_name="net_handshake",
        payload=response_payload,
        strict_top_level=True,
    )
    if not bool(response_validated.get("valid", False)):
        return refusal(
            "refusal.net.envelope_invalid",
            "generated handshake response failed schema validation",
            "Fix server handshake payload generation.",
            {"schema_id": "net_handshake"},
            "$",
        )

    response_message = build_proto_message(
        msg_type="handshake_response",
        msg_id="msg.handshake_response.{}".format(handshake_id),
        sequence=2,
        payload_schema_id="net_handshake",
        payload_inline_json=response_payload,
    )
    sent_response = listener.send(encode_proto_message(response_message))
    if sent_response.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "failed to send handshake response envelope",
            "Retry handshake after reconnecting transport.",
            {"handshake_id": handshake_id},
            "$.network",
        )
    received_by_client = client.recv()
    if received_by_client.get("result") != "complete":
        return refusal(
            "refusal.net.envelope_invalid",
            "client did not receive handshake response envelope",
            "Retry handshake after reconnecting transport.",
            {"handshake_id": handshake_id},
            "$.network",
        )
    decoded_response = decode_proto_message(repo_root=repo_root, message_bytes=bytes(received_by_client.get("message_bytes") or b""))
    if decoded_response.get("result") != "complete":
        return decoded_response
    response_proto_payload = dict((decoded_response.get("proto_message") or {}).get("payload_ref", {})).get("inline_json")
    if not isinstance(response_proto_payload, dict):
        return refusal(
            "refusal.net.envelope_invalid",
            "handshake response payload_ref.inline_json must be object",
            "Encode handshake payload using canonical proto wrapper.",
            {"handshake_id": handshake_id},
            "$.payload_ref.inline_json",
        )

    client.close()
    listener.close()

    if str(response_proto_payload.get("result", "")) != "accept":
        refusal_payload = dict(response_proto_payload.get("refusal") or {})
        return {
            "result": "refused",
            "refusal": {
                "reason_code": str(refusal_payload.get("reason_code", "refusal.net.envelope_invalid")),
                "message": str(refusal_payload.get("message", "handshake refused")),
                "remediation_hint": str(refusal_payload.get("remediation_hint", "")),
                "relevant_ids": dict(refusal_payload.get("relevant_ids") or {}),
            },
            "errors": [
                {
                    "code": str(refusal_payload.get("reason_code", "refusal.net.envelope_invalid")),
                    "message": str(refusal_payload.get("message", "handshake refused")),
                    "path": "$.handshake",
                }
            ],
            "handshake": response_proto_payload,
            "request": request_payload,
            "handshake_artifact_hash": canonical_sha256(
                {
                    "request": request_payload,
                    "response": response_proto_payload,
                }
            ),
        }

    return {
        "result": "complete",
        "handshake": response_proto_payload,
        "request": request_payload,
        "handshake_id": handshake_id,
        "negotiated_replication_policy_id": str(response_proto_payload.get("negotiated_replication_policy_id", "")),
        "server_law_profile_id": str(response_proto_payload.get("server_law_profile_id", "")),
        "anti_cheat_policy_id": str(response_proto_payload.get("anti_cheat_policy_id", "")),
        "server_policy_id": str(network_payload.get("server_policy_id", "")),
        "handshake_artifact_hash": canonical_sha256(
            {
                "request": request_payload,
                "response": response_proto_payload,
            }
        ),
        "proto_hashes": {
            "request_proto_hash": canonical_sha256(request_message),
            "response_proto_hash": canonical_sha256(response_message),
        },
    }
