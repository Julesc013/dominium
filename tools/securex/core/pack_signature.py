"""Deterministic pack signature helpers."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any, Dict, Tuple


DEFAULT_ISSUED_UTC = "1970-01-01T00:00:00Z"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sign_hash(
    payload_hash_sha256: str,
    signer_id: str,
    key_id: str,
    key_material: str,
    issued_utc: str = DEFAULT_ISSUED_UTC,
) -> Dict[str, Any]:
    signer = str(signer_id).strip()
    key = str(key_id).strip()
    material = str(key_material).strip()
    issued = str(issued_utc).strip() or DEFAULT_ISSUED_UTC
    payload_hash = str(payload_hash_sha256).strip().lower()

    canonical_blob = "|".join((payload_hash, signer, key, issued, material)).encode("utf-8")
    digest = hashlib.sha256(canonical_blob).digest()
    signature_blob = base64.b64encode(digest).decode("ascii")
    return {
        "schema_id": "dominium.schema.governance.pack_signature",  # schema_version: 1.0.0
        "schema_version": "1.0.0",
        "record": {
            "signature_id": "sig.{}.{}".format(signer or "unknown", payload_hash[:12] or "none"),
            "signer_id": signer,
            "key_id": key,
            "algorithm": "sha256+b64",
            "payload_hash_sha256": payload_hash,
            "signature_blob_b64": signature_blob,
            "issued_utc": issued,
            "extensions": {},
        },
    }


def sign_pack(
    pack_path: str,
    signer_id: str,
    key_id: str,
    key_material: str,
    issued_utc: str = DEFAULT_ISSUED_UTC,
) -> Dict[str, Any]:
    payload_hash = sha256_file(pack_path)
    return sign_hash(payload_hash, signer_id, key_id, key_material, issued_utc=issued_utc)


def verify_signature_payload(payload: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "refuse.signature.invalid_payload"
    if str(payload.get("schema_id", "")).strip() != "dominium.schema.governance.pack_signature":  # schema_version: 1.0.0
        return False, "refuse.signature.schema_id"
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        return False, "refuse.signature.schema_version"
    record = payload.get("record")
    if not isinstance(record, dict):
        return False, "refuse.signature.record"
    required = (
        "signature_id",
        "signer_id",
        "key_id",
        "algorithm",
        "payload_hash_sha256",
        "signature_blob_b64",
        "issued_utc",
        "extensions",
    )
    for key in required:
        if key not in record:
            return False, "refuse.signature.missing_{}".format(key)
    if str(record.get("algorithm", "")).strip() != "sha256+b64":
        return False, "refuse.signature.algorithm"
    return True, ""


def verify_pack_signature(
    pack_path: str,
    signature_payload: Dict[str, Any],
    key_material: str,
) -> Tuple[bool, str]:
    ok, refusal = verify_signature_payload(signature_payload)
    if not ok:
        return False, refusal

    record = signature_payload.get("record", {})
    pack_hash = sha256_file(pack_path)
    expected_hash = str(record.get("payload_hash_sha256", "")).strip().lower()
    if pack_hash != expected_hash:
        return False, "refuse.signature.payload_hash_mismatch"

    expected = sign_hash(
        payload_hash_sha256=pack_hash,
        signer_id=str(record.get("signer_id", "")),
        key_id=str(record.get("key_id", "")),
        key_material=key_material,
        issued_utc=str(record.get("issued_utc", DEFAULT_ISSUED_UTC)),
    )
    exp_blob = expected["record"]["signature_blob_b64"]
    got_blob = str(record.get("signature_blob_b64", "")).strip()
    if exp_blob != got_blob:
        return False, "refuse.signature.invalid_blob"
    return True, ""


def write_signature(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
