#!/usr/bin/env python3
import hashlib
import json
import os
import re
import struct
import zlib
from typing import Dict, List, Tuple


MAGIC = b"DOMPKG10"
HEADER_SIZE = 80
FORMAT_VERSION = 1
TLV_TYPE_MANIFEST_JSON = 1
CHUNK_SIZE_V1 = 1024 * 1024
CHUNK_TABLE_RECORD = struct.Struct("<IIQIIQ32s")
HEADER_STRUCT = struct.Struct("<8sIIQQQQQQQQ")
TLV_HEAD = struct.Struct("<HI")
SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9._\\-/]+$")


class DomPkgError(Exception):
    def __init__(self, code: str, message: str, details: Dict[str, object] = None):
        Exception.__init__(self, message)
        self.code = code
        self.message = message
        self.details = details or {}


def refusal_payload(code: str, message: str, details: Dict[str, object] = None) -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_rel_path(path: str) -> str:
    norm = path.replace("\\", "/").strip("/")
    if not norm:
        raise DomPkgError("refuse.path_invalid", "empty relative path")
    if norm.startswith("../") or "/../" in norm or norm == "..":
        raise DomPkgError("refuse.path_invalid", "path escapes root", {"path": path})
    if "//" in norm:
        while "//" in norm:
            norm = norm.replace("//", "/")
    if not SAFE_PATH_RE.match(norm):
        raise DomPkgError("refuse.path_invalid", "path contains invalid characters", {"path": path})
    return norm


def collect_inputs(input_root: str, input_files: List[str]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    seen = set()
    if input_root:
        root = os.path.abspath(input_root)
        if not os.path.isdir(root):
            raise DomPkgError("refuse.invalid_input", "input root missing", {"input_root": input_root})
        for dirpath, _dirs, files in os.walk(root):
            files.sort()
            for name in files:
                abs_path = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_path, root)
                rel = normalize_rel_path(rel)
                if rel in seen:
                    raise DomPkgError("refuse.path_invalid", "duplicate normalized path", {"path": rel})
                seen.add(rel)
                pairs.append((abs_path, rel))
    for raw in input_files or []:
        abs_path = os.path.abspath(raw)
        if not os.path.isfile(abs_path):
            raise DomPkgError("refuse.invalid_input", "input file missing", {"path": raw})
        rel = normalize_rel_path(os.path.basename(abs_path))
        if rel in seen:
            raise DomPkgError("refuse.path_invalid", "duplicate normalized path", {"path": rel})
        seen.add(rel)
        pairs.append((abs_path, rel))
    pairs.sort(key=lambda item: item[1])
    if not pairs:
        raise DomPkgError("refuse.invalid_input", "no input files discovered")
    return pairs


def _compress(raw_chunk: bytes, algo: str) -> bytes:
    if algo == "deflate":
        return zlib.compress(raw_chunk, 9)
    if algo == "none":
        return raw_chunk
    if algo == "zstd":
        raise DomPkgError("refuse.invalid_compression", "zstd is not enabled in this tool build")
    raise DomPkgError("refuse.invalid_compression", "unsupported compression", {"compression": algo})


def _decompress(blob: bytes, algo: str, expected_size: int) -> bytes:
    if algo == "deflate":
        raw = zlib.decompress(blob)
    elif algo == "none":
        raw = blob
    else:
        raise DomPkgError("refuse.invalid_compression", "unsupported compression", {"compression": algo})
    if len(raw) != expected_size:
        raise DomPkgError("refuse.hash_mismatch", "chunk size mismatch", {"expected_size": expected_size, "actual_size": len(raw)})
    return raw


def _validate_manifest_shape(manifest: dict) -> None:
    required = (
        "pkg_id",
        "pkg_version",
        "pkg_format_version",
        "platform",
        "arch",
        "abi",
        "requires_capabilities",
        "provides_capabilities",
        "entitlements",
        "compression",
        "chunk_size_bytes",
        "file_exports",
        "content_hash",
        "extensions",
    )
    for key in required:
        if key not in manifest:
            raise DomPkgError("refuse.manifest_missing_field", "manifest field missing", {"field": key})
    if not isinstance(manifest.get("file_exports"), list):
        raise DomPkgError("refuse.manifest_invalid_type", "file_exports must be a list")
    if not isinstance(manifest.get("requires_capabilities"), list):
        raise DomPkgError("refuse.manifest_invalid_type", "requires_capabilities must be a list")
    if not isinstance(manifest.get("provides_capabilities"), list):
        raise DomPkgError("refuse.manifest_invalid_type", "provides_capabilities must be a list")
    if not isinstance(manifest.get("entitlements"), list):
        raise DomPkgError("refuse.manifest_invalid_type", "entitlements must be a list")
    if not isinstance(manifest.get("chunk_size_bytes"), int) or manifest.get("chunk_size_bytes") <= 0:
        raise DomPkgError("refuse.manifest_invalid_value", "chunk_size_bytes must be a positive integer")


def _manifest_for_hash(manifest: dict) -> dict:
    clone = json.loads(json.dumps(manifest))
    clone["content_hash"] = ""
    return clone


def pack_package(
    input_pairs: List[Tuple[str, str]],
    output_pkg: str,
    pkg_id: str,
    pkg_version: str,
    platform: str,
    arch: str,
    abi: str,
    requires_capabilities: List[str],
    provides_capabilities: List[str],
    entitlements: List[str],
    optional_capabilities: List[str],
    compression: str,
    signature_payload: dict,
) -> Dict[str, object]:
    file_exports: List[dict] = []
    table_records: List[Tuple[int, int, int, int, int, int, bytes]] = []
    payload_chunks: List[bytes] = []
    payload_offset_rel = 0

    for file_index, (abs_path, rel_path) in enumerate(input_pairs):
        file_size = os.path.getsize(abs_path)
        file_hash = sha256_file(abs_path)
        chunk_count = 0
        raw_offset = 0
        with open(abs_path, "rb") as handle:
            chunk_index = 0
            while True:
                raw = handle.read(CHUNK_SIZE_V1)
                if not raw:
                    break
                raw_hash = hashlib.sha256(raw).digest()
                blob = _compress(raw, compression)
                payload_chunks.append(blob)
                table_records.append((
                    file_index,
                    chunk_index,
                    raw_offset,
                    len(raw),
                    len(blob),
                    payload_offset_rel,
                    raw_hash,
                ))
                payload_offset_rel += len(blob)
                raw_offset += len(raw)
                chunk_index += 1
                chunk_count += 1

        file_exports.append({
            "path": rel_path,
            "size_bytes": int(file_size),
            "sha256": file_hash,
            "mode": "0644",
            "chunk_count": chunk_count,
        })

    payload_bytes = b"".join(payload_chunks)
    chunk_table_bytes = b"".join(CHUNK_TABLE_RECORD.pack(*record) for record in table_records)

    manifest = {
        "pkg_id": pkg_id,
        "pkg_version": pkg_version,
        "pkg_format_version": 1,
        "platform": platform,
        "arch": arch,
        "abi": abi,
        "requires_capabilities": sorted(set(requires_capabilities)),
        "provides_capabilities": sorted(set(provides_capabilities)),
        "entitlements": sorted(set(entitlements)),
        "optional_capabilities": sorted(set(optional_capabilities or [])),
        "compression": compression,
        "chunk_size_bytes": CHUNK_SIZE_V1,
        "file_exports": file_exports,
        "content_hash": "",
        "extensions": {},
    }
    if signature_payload:
        manifest["signature"] = signature_payload

    manifest_for_hash = _manifest_for_hash(manifest)
    manifest_tlv = TLV_HEAD.pack(TLV_TYPE_MANIFEST_JSON, len(canonical_json_bytes(manifest_for_hash))) + canonical_json_bytes(manifest_for_hash)

    manifest_offset = HEADER_SIZE
    chunk_table_offset = manifest_offset + len(manifest_tlv)
    payload_offset = chunk_table_offset + len(chunk_table_bytes)

    signature_bytes = b""
    signature_offset = 0
    signature_size = 0
    if signature_payload:
        signature_bytes = canonical_json_bytes(signature_payload)
        signature_offset = payload_offset + len(payload_bytes)
        signature_size = len(signature_bytes)

    header_for_hash = HEADER_STRUCT.pack(
        MAGIC,
        HEADER_SIZE,
        FORMAT_VERSION,
        manifest_offset,
        len(manifest_tlv),
        chunk_table_offset,
        len(chunk_table_bytes),
        payload_offset,
        len(payload_bytes),
        0,
        0,
    )
    content_hash = sha256_bytes(header_for_hash + manifest_tlv + chunk_table_bytes + payload_bytes)
    manifest["content_hash"] = content_hash
    manifest_tlv = TLV_HEAD.pack(TLV_TYPE_MANIFEST_JSON, len(canonical_json_bytes(manifest))) + canonical_json_bytes(manifest)
    chunk_table_offset = manifest_offset + len(manifest_tlv)
    payload_offset = chunk_table_offset + len(chunk_table_bytes)
    if signature_bytes:
        signature_offset = payload_offset + len(payload_bytes)
        signature_size = len(signature_bytes)

    header = HEADER_STRUCT.pack(
        MAGIC,
        HEADER_SIZE,
        FORMAT_VERSION,
        manifest_offset,
        len(manifest_tlv),
        chunk_table_offset,
        len(chunk_table_bytes),
        payload_offset,
        len(payload_bytes),
        signature_offset,
        signature_size,
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_pkg)), exist_ok=True)
    with open(output_pkg, "wb") as handle:
        handle.write(header)
        handle.write(manifest_tlv)
        handle.write(chunk_table_bytes)
        handle.write(payload_bytes)
        if signature_bytes:
            handle.write(signature_bytes)

    return {
        "pkg_path": os.path.abspath(output_pkg).replace("\\", "/"),
        "manifest": manifest,
        "record_count": len(table_records),
        "file_count": len(file_exports),
        "payload_size": len(payload_bytes),
        "chunk_table_size": len(chunk_table_bytes),
        "signature_size": signature_size,
    }


def _read_header(data: bytes) -> Dict[str, int]:
    if len(data) < HEADER_SIZE:
        raise DomPkgError("refuse.invalid_header", "header too small")
    values = HEADER_STRUCT.unpack(data[:HEADER_SIZE])
    if values[0] != MAGIC:
        raise DomPkgError("refuse.invalid_header", "magic mismatch")
    if values[1] != HEADER_SIZE:
        raise DomPkgError("refuse.invalid_header", "header size mismatch")
    if values[2] != FORMAT_VERSION:
        raise DomPkgError("refuse.invalid_header", "format version mismatch", {"format_version": values[2]})
    return {
        "manifest_offset": int(values[3]),
        "manifest_size": int(values[4]),
        "chunk_offset": int(values[5]),
        "chunk_size": int(values[6]),
        "payload_offset": int(values[7]),
        "payload_size": int(values[8]),
        "signature_offset": int(values[9]),
        "signature_size": int(values[10]),
    }


def _extract_manifest_from_tlv(manifest_block: bytes) -> dict:
    pos = 0
    manifest_json = None
    while pos + TLV_HEAD.size <= len(manifest_block):
        tlv_type, tlv_len = TLV_HEAD.unpack(manifest_block[pos: pos + TLV_HEAD.size])
        pos += TLV_HEAD.size
        if pos + tlv_len > len(manifest_block):
            raise DomPkgError("refuse.invalid_manifest_tlv", "tlv length exceeds block")
        value = manifest_block[pos: pos + tlv_len]
        pos += tlv_len
        if tlv_type == TLV_TYPE_MANIFEST_JSON:
            manifest_json = value
    if manifest_json is None:
        raise DomPkgError("refuse.invalid_manifest_tlv", "manifest tlv type missing")
    try:
        manifest = json.loads(manifest_json.decode("utf-8"))
    except Exception:
        raise DomPkgError("refuse.invalid_manifest_tlv", "manifest json parse failed")
    _validate_manifest_shape(manifest)
    return manifest


def _iter_chunk_records(chunk_table_block: bytes) -> List[Tuple[int, int, int, int, int, int, bytes]]:
    if len(chunk_table_block) % CHUNK_TABLE_RECORD.size != 0:
        raise DomPkgError("refuse.invalid_offsets", "chunk table size misaligned")
    records = []
    pos = 0
    while pos < len(chunk_table_block):
        records.append(CHUNK_TABLE_RECORD.unpack(chunk_table_block[pos: pos + CHUNK_TABLE_RECORD.size]))
        pos += CHUNK_TABLE_RECORD.size
    return records


def _check_offsets(file_size: int, offset: int, size: int, label: str) -> None:
    if offset < 0 or size < 0:
        raise DomPkgError("refuse.invalid_offsets", label + " has negative range")
    if offset + size > file_size:
        raise DomPkgError("refuse.invalid_offsets", label + " exceeds file", {"offset": offset, "size": size, "file_size": file_size})


def _load_signature_policy(path: str) -> Dict[str, object]:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_package(pkg_path: str, trust_policy_path: str = "") -> Dict[str, object]:
    with open(pkg_path, "rb") as handle:
        blob = handle.read()
    file_size = len(blob)
    header = _read_header(blob)

    _check_offsets(file_size, header["manifest_offset"], header["manifest_size"], "manifest")
    _check_offsets(file_size, header["chunk_offset"], header["chunk_size"], "chunk table")
    _check_offsets(file_size, header["payload_offset"], header["payload_size"], "payload")
    if header["signature_size"] > 0:
        _check_offsets(file_size, header["signature_offset"], header["signature_size"], "signature")

    manifest_block = blob[header["manifest_offset"]: header["manifest_offset"] + header["manifest_size"]]
    chunk_table_block = blob[header["chunk_offset"]: header["chunk_offset"] + header["chunk_size"]]
    payload_block = blob[header["payload_offset"]: header["payload_offset"] + header["payload_size"]]
    signature_block = b""
    if header["signature_size"] > 0:
        signature_block = blob[header["signature_offset"]: header["signature_offset"] + header["signature_size"]]

    manifest = _extract_manifest_from_tlv(manifest_block)
    records = _iter_chunk_records(chunk_table_block)
    compression = manifest.get("compression")
    exports = manifest.get("file_exports") or []

    file_digests = {}
    file_sizes = {}
    for idx, export in enumerate(exports):
        path = export.get("path")
        if not isinstance(path, str):
            raise DomPkgError("refuse.manifest_invalid_type", "file export path invalid")
        normalize_rel_path(path)
        file_digests[idx] = hashlib.sha256()
        file_sizes[idx] = 0

    for rec in records:
        file_index, _chunk_index, _raw_offset, raw_size, compressed_size, payload_rel_off, raw_hash = rec
        if file_index not in file_digests:
            raise DomPkgError("refuse.manifest_invalid_value", "chunk references unknown file index", {"file_index": file_index})
        if payload_rel_off + compressed_size > len(payload_block):
            raise DomPkgError("refuse.invalid_offsets", "chunk payload range invalid")
        chunk_blob = payload_block[payload_rel_off: payload_rel_off + compressed_size]
        raw = _decompress(chunk_blob, compression, raw_size)
        if hashlib.sha256(raw).digest() != raw_hash:
            raise DomPkgError("refuse.hash_mismatch", "raw chunk hash mismatch")
        file_digests[file_index].update(raw)
        file_sizes[file_index] += len(raw)

    for idx, export in enumerate(exports):
        expected_hash = export.get("sha256")
        actual_hash = file_digests[idx].hexdigest()
        if expected_hash != actual_hash:
            raise DomPkgError("refuse.hash_mismatch", "file hash mismatch", {"path": export.get("path")})
        if int(export.get("size_bytes", -1)) != file_sizes[idx]:
            raise DomPkgError("refuse.hash_mismatch", "file size mismatch", {"path": export.get("path")})

    manifest_for_hash = _manifest_for_hash(manifest)
    manifest_tlv_for_hash = TLV_HEAD.pack(TLV_TYPE_MANIFEST_JSON, len(canonical_json_bytes(manifest_for_hash))) + canonical_json_bytes(manifest_for_hash)
    header_for_hash = HEADER_STRUCT.pack(
        MAGIC,
        HEADER_SIZE,
        FORMAT_VERSION,
        header["manifest_offset"],
        len(manifest_tlv_for_hash),
        header["chunk_offset"],
        header["chunk_size"],
        header["payload_offset"],
        header["payload_size"],
        0,
        0,
    )
    actual_content_hash = sha256_bytes(header_for_hash + manifest_tlv_for_hash + chunk_table_block + payload_block)
    if manifest.get("content_hash") != actual_content_hash:
        raise DomPkgError("refuse.hash_mismatch", "content hash mismatch")

    if trust_policy_path:
        policy = _load_signature_policy(trust_policy_path)
        require_sig = bool(policy.get("signature_required"))
        trusted = set()
        for signer in policy.get("trusted_signers", []) or []:
            if isinstance(signer, dict):
                sid = signer.get("signer_id")
                if isinstance(sid, str):
                    trusted.add(sid)
        if require_sig and not signature_block:
            raise DomPkgError("refuse.signature_required", "signature required by policy")
        if signature_block:
            try:
                sig = json.loads(signature_block.decode("utf-8"))
            except Exception:
                raise DomPkgError("refuse.signature_invalid", "signature block parse failed")
            signer_id = sig.get("signer_id")
            if trusted and signer_id not in trusted:
                raise DomPkgError("refuse.signature_invalid", "signer not trusted", {"signer_id": signer_id})

    return {
        "result": "ok",
        "pkg_path": os.path.abspath(pkg_path).replace("\\", "/"),
        "pkg_id": manifest.get("pkg_id"),
        "pkg_version": manifest.get("pkg_version"),
        "content_hash": manifest.get("content_hash"),
        "record_count": len(records),
        "file_count": len(exports),
        "signature_present": bool(signature_block),
    }


def read_manifest_only(pkg_path: str) -> Dict[str, object]:
    with open(pkg_path, "rb") as handle:
        blob = handle.read()
    header = _read_header(blob)
    manifest_block = blob[header["manifest_offset"]: header["manifest_offset"] + header["manifest_size"]]
    manifest = _extract_manifest_from_tlv(manifest_block)
    return manifest


def extract_package(pkg_path: str, output_root: str, overwrite: bool) -> Dict[str, object]:
    verified = verify_package(pkg_path)
    with open(pkg_path, "rb") as handle:
        blob = handle.read()
    header = _read_header(blob)
    manifest_block = blob[header["manifest_offset"]: header["manifest_offset"] + header["manifest_size"]]
    chunk_table_block = blob[header["chunk_offset"]: header["chunk_offset"] + header["chunk_size"]]
    payload_block = blob[header["payload_offset"]: header["payload_offset"] + header["payload_size"]]
    manifest = _extract_manifest_from_tlv(manifest_block)
    records = _iter_chunk_records(chunk_table_block)
    compression = manifest.get("compression")
    exports = manifest.get("file_exports") or []

    os.makedirs(output_root, exist_ok=True)
    file_buffers: Dict[int, List[bytes]] = {}
    for idx in range(len(exports)):
        file_buffers[idx] = []

    for rec in records:
        file_index, _chunk_index, _raw_offset, raw_size, compressed_size, payload_rel_off, _raw_hash = rec
        chunk_blob = payload_block[payload_rel_off: payload_rel_off + compressed_size]
        raw = _decompress(chunk_blob, compression, raw_size)
        file_buffers[file_index].append(raw)

    extracted = []
    for idx, export in enumerate(exports):
        rel = normalize_rel_path(export.get("path"))
        out_path = os.path.join(output_root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if os.path.exists(out_path) and not overwrite:
            raise DomPkgError("refuse.invalid_input", "output exists", {"path": rel})
        with open(out_path, "wb") as handle:
            for chunk in file_buffers[idx]:
                handle.write(chunk)
        extracted.append(rel)

    return {
        "result": "ok",
        "pkg_path": verified["pkg_path"],
        "content_hash": verified["content_hash"],
        "extracted_files": extracted,
    }
