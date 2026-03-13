"""Deterministic RELEASE-1 manifest generation and verification."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Mapping, Sequence

from src.release.build_id_engine import build_build_id_input_payload, build_id_identity_from_input_payload
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_RELEASE_MANIFEST_VERSION = "1.0.0"
DEFAULT_RELEASE_CHANNEL = "mock"
DEFAULT_RELEASE_MANIFEST_REL = os.path.join("manifests", "release_manifest.json")

ARTIFACT_KIND_BINARY = "artifact.binary"
ARTIFACT_KIND_PACK = "artifact.pack"
ARTIFACT_KIND_PROFILE = "artifact.profile"
ARTIFACT_KIND_LOCK = "artifact.lock"
ARTIFACT_KIND_BUNDLE = "artifact.bundle"
ARTIFACT_KIND_MANIFEST = "artifact.manifest"

PRODUCT_BINARY_FILENAMES = (
    "client",
    "dominium_client",
    "dominium_server",
    "engine",
    "game",
    "launcher",
    "server",
    "setup",
    "tool_attach_console_stub",
)
OPTIONAL_STABILITY_REPORT_REL = os.path.join("docs", "audit", "STABILITY_TAGGING_FINAL.md")
OPTIONAL_REGRESSION_RELS = (
    os.path.join("data", "regression", "mvp_smoke_baseline.json"),
    os.path.join("data", "regression", "mvp_stress_baseline.json"),
    os.path.join("data", "regression", "mvp_cross_platform_baseline.json"),
)
DEFAULT_SIGNATURE_SCHEME_ID = "signature.mock_detached_hash.v1"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm_rel(target)


def _sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directory_tree_hash(path: str) -> str:
    rows: list[dict[str, str]] = []
    root = os.path.normpath(os.path.abspath(path))
    for current_root, _dirs, files in os.walk(root):
        rel_root = os.path.relpath(current_root, root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(files):
            abs_path = os.path.join(current_root, name)
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rows.append({"path": _norm_rel(rel_path), "sha256": _sha256_file(abs_path)})
    return canonical_sha256({"files": rows})


def _semver_without_build(version_token: str) -> str:
    token = _token(version_token)
    if "+" in token:
        token = token.split("+", 1)[0]
    return token or "0.0.0"


def _artifact_entry(
    *,
    artifact_kind: str,
    artifact_name: str,
    content_hash: str,
    build_id: str = "",
    endpoint_descriptor_hash: str = "",
    pack_compat_hash: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "artifact_kind": _token(artifact_kind),
        "artifact_name": _norm_rel(artifact_name),
        "content_hash": _token(content_hash).lower(),
        "build_id": _token(build_id),
        "endpoint_descriptor_hash": _token(endpoint_descriptor_hash).lower(),
        "pack_compat_hash": _token(pack_compat_hash).lower(),
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _signature_entry(
    *,
    signature_id: str,
    signer_id: str,
    signed_hash: str,
    signature_bytes: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "signature_id": _token(signature_id),
        "signer_id": _token(signer_id),
        "signed_hash": _token(signed_hash).lower(),
        "signature_bytes": _token(signature_bytes),
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_mock_signature_block(
    *,
    signer_id: str,
    signed_hash: str,
    signature_id: str = "",
) -> dict:
    signature_token = _token(signature_id) or "signature.{}.{}".format(_token(signer_id).replace(" ", "_") or "mock", _token(signed_hash).lower()[:16] or "unsigned")
    payload = {
        "scheme_id": DEFAULT_SIGNATURE_SCHEME_ID,
        "signature_id": signature_token,
        "signer_id": _token(signer_id),
        "signed_hash": _token(signed_hash).lower(),
    }
    return _signature_entry(
        signature_id=signature_token,
        signer_id=_token(signer_id),
        signed_hash=_token(signed_hash).lower(),
        signature_bytes=canonical_sha256(payload),
        extensions={"scheme_id": DEFAULT_SIGNATURE_SCHEME_ID},
    )


def _normalized_signature_rows(signature_rows: Sequence[Mapping[str, object]] | None) -> list[dict]:
    out: list[dict] = []
    for row in list(signature_rows or []):
        item = _as_map(row)
        if not _token(item.get("signer_id")) or not _token(item.get("signed_hash")):
            continue
        out.append(
            _signature_entry(
                signature_id=_token(item.get("signature_id"))
                or "signature.{}.{}".format(_token(item.get("signer_id")).replace(" ", "_") or "mock", _token(item.get("signed_hash")).lower()[:16] or "unsigned"),
                signer_id=_token(item.get("signer_id")),
                signed_hash=_token(item.get("signed_hash")).lower(),
                signature_bytes=_token(item.get("signature_bytes")),
                extensions=_as_map(item.get("extensions")),
            )
        )
    return sorted(
        out,
        key=lambda row: (
            _token(row.get("signed_hash")),
            _token(row.get("signer_id")),
            _token(row.get("signature_id")),
            _token(row.get("signature_bytes")),
        ),
    )


def _manifest_hash_payload(payload: Mapping[str, object]) -> dict:
    out = dict(payload or {})
    out["manifest_hash"] = ""
    out["deterministic_fingerprint"] = ""
    out.pop("signatures", None)
    return out


def _manifest_fingerprint_payload(payload: Mapping[str, object]) -> dict:
    out = dict(payload or {})
    out["deterministic_fingerprint"] = ""
    out.pop("signatures", None)
    return out


def _descriptor_json(stdout: str) -> dict:
    text = str(stdout or "").strip()
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except ValueError:
        return {}
    if not isinstance(payload, dict):
        return {}
    if isinstance(payload.get("descriptor"), Mapping):
        return dict(payload.get("descriptor") or {})
    return dict(payload)


def _looks_like_python_script(path: str) -> bool:
    try:
        with open(path, "rb") as handle:
            first = handle.readline(256)
    except OSError:
        return False
    lower = first.decode("utf-8", errors="ignore").lower()
    return lower.startswith("#!") or "python" in lower or path.lower().endswith(".py")


def _run_descriptor(binary_path: str) -> tuple[dict, str]:
    abs_path = os.path.normpath(os.path.abspath(binary_path))
    attempts: list[list[str]] = []
    if _looks_like_python_script(abs_path):
        attempts.append([sys.executable, abs_path, "--descriptor"])
    attempts.append([abs_path, "--descriptor"])
    last_error = "descriptor invocation failed"
    for command in attempts:
        try:
            proc = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                encoding="utf-8",
            )
        except OSError as exc:
            last_error = str(exc)
            continue
        if int(proc.returncode or 0) != 0:
            stderr = _token(proc.stderr)
            if stderr:
                last_error = stderr
            continue
        descriptor = _descriptor_json(proc.stdout)
        if descriptor:
            return descriptor, ""
        last_error = "descriptor command returned non-json output"
    return {}, last_error


def _pack_compat_hash_for_dir(pack_dir: str) -> str:
    local_compat = os.path.join(pack_dir, "pack.compat.json")
    if os.path.isfile(local_compat):
        return _sha256_file(local_compat)
    alias_path = os.path.join(pack_dir, "pack.alias.json")
    alias_payload, alias_error = _read_json(alias_path)
    if alias_error:
        return ""
    compat_hashes = sorted(
        {
            _token(_as_map(row).get("compat_manifest_hash")).lower()
            for row in _as_list(alias_payload.get("source_packs"))
            if _token(_as_map(row).get("compat_manifest_hash"))
        }
    )
    if not compat_hashes:
        return ""
    return canonical_sha256({"compat_manifest_hashes": compat_hashes})


def _pack_metadata_for_dir(pack_dir: str) -> dict:
    alias_path = os.path.join(pack_dir, "pack.alias.json")
    alias_payload, alias_error = _read_json(alias_path)
    if not alias_error:
        return {
            "pack_id": _token(alias_payload.get("pack_alias_id")) or os.path.basename(pack_dir),
            "pack_canonical_hash": _token(alias_payload.get("canonical_hash")).lower(),
            "distribution_channel": _token(alias_payload.get("distribution_channel")),
            "runtime_version": _token(alias_payload.get("runtime_version")),
            "pack_descriptor": "alias",
        }
    manifest_path = os.path.join(pack_dir, "pack.json")
    manifest_payload, manifest_error = _read_json(manifest_path)
    if manifest_error:
        return {"pack_id": os.path.basename(pack_dir), "pack_descriptor": "tree_only"}
    return {
        "pack_id": _token(manifest_payload.get("pack_id")) or os.path.basename(pack_dir),
        "pack_canonical_hash": _token(manifest_payload.get("canonical_hash")).lower(),
        "pack_version": _token(manifest_payload.get("version")),
        "pack_descriptor": "manifest",
    }


def _binary_entry(binary_path: str, dist_root: str) -> tuple[dict, dict]:
    descriptor, descriptor_error = _run_descriptor(binary_path)
    if not descriptor:
        raise RuntimeError("descriptor unavailable for '{}': {}".format(_norm_rel(os.path.relpath(binary_path, dist_root)), descriptor_error))
    extensions = _as_map(descriptor.get("extensions"))
    build_id = _token(extensions.get("official.build_id"))
    descriptor_hash = canonical_sha256(descriptor)
    product_version = _token(descriptor.get("product_version"))
    rel_path = _norm_rel(os.path.relpath(binary_path, dist_root))
    entry = _artifact_entry(
        artifact_kind=ARTIFACT_KIND_BINARY,
        artifact_name=rel_path,
        content_hash=_sha256_file(binary_path),
        build_id=build_id,
        endpoint_descriptor_hash=descriptor_hash,
        extensions={
            "product_id": _token(descriptor.get("product_id")) or os.path.basename(binary_path),
            "product_version": product_version,
            "release_semver": _semver_without_build(product_version),
            "semantic_contract_registry_hash": _token(extensions.get("official.semantic_contract_registry_hash")).lower(),
            "inputs_hash": _token(extensions.get("official.inputs_hash")).lower(),
            "compilation_options_hash": _token(extensions.get("official.compilation_options_hash")).lower(),
            "source_revision_id": _token(extensions.get("official.source_revision_id")),
            "explicit_build_number": _token(extensions.get("official.explicit_build_number")),
            "platform_tag": _token(extensions.get("official.platform_tag")),
            "build_configuration": _token(extensions.get("official.build_configuration")) or "release",
        },
    )
    return entry, descriptor


def _auxiliary_binary_entry(binary_path: str, dist_root: str) -> dict:
    rel_path = _norm_rel(os.path.relpath(binary_path, dist_root))
    return _artifact_entry(
        artifact_kind=ARTIFACT_KIND_BINARY,
        artifact_name=rel_path,
        content_hash=_sha256_file(binary_path),
        extensions={
            "binary_role": "auxiliary_wrapper",
            "product_id": os.path.basename(binary_path),
        },
    )


def _binary_paths(dist_root: str) -> tuple[list[str], list[str]]:
    bin_root = os.path.join(dist_root, "bin")
    if not os.path.isdir(bin_root):
        return [], []
    product_rows = []
    for name in PRODUCT_BINARY_FILENAMES:
        candidate = os.path.join(bin_root, name)
        if os.path.isfile(candidate):
            product_rows.append(candidate)
    auxiliary_rows = []
    for name in sorted(os.listdir(bin_root)):
        candidate = os.path.join(bin_root, name)
        if not os.path.isfile(candidate):
            continue
        if name in PRODUCT_BINARY_FILENAMES:
            continue
        auxiliary_rows.append(candidate)
    normalize = lambda rows: sorted(set(os.path.normpath(os.path.abspath(path)) for path in rows))
    return normalize(product_rows), normalize(auxiliary_rows)


def _pack_dirs(dist_root: str) -> list[str]:
    packs_root = os.path.join(dist_root, "packs")
    if not os.path.isdir(packs_root):
        return []
    rows = []
    for current_root, dirs, files in os.walk(packs_root):
        del dirs
        file_set = set(files)
        if "pack.alias.json" in file_set or "pack.json" in file_set:
            rows.append(os.path.normpath(os.path.abspath(current_root)))
    return sorted(set(rows))


def _simple_file_entries(dist_root: str, root_rel: str, artifact_kind: str) -> list[dict]:
    base = os.path.join(dist_root, root_rel.replace("/", os.sep))
    if not os.path.isdir(base):
        return []
    rows = []
    for current_root, _dirs, files in os.walk(base):
        rel_root = os.path.relpath(current_root, dist_root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(files):
            rel_path = os.path.join(rel_root, name) if rel_root else name
            abs_path = os.path.join(current_root, name)
            rows.append(
                _artifact_entry(
                    artifact_kind=artifact_kind,
                    artifact_name=_norm_rel(rel_path),
                    content_hash=_sha256_file(abs_path),
                )
            )
    return rows


def _bundle_entries(dist_root: str) -> list[dict]:
    base = os.path.join(dist_root, "bundles")
    if not os.path.isdir(base):
        return []
    rows = []
    for current_root, _dirs, files in os.walk(base):
        rel_root = os.path.relpath(current_root, dist_root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(files):
            if name != "bundle.json":
                continue
            rel_path = os.path.join(rel_root, name) if rel_root else name
            abs_path = os.path.join(current_root, name)
            rows.append(
                _artifact_entry(
                    artifact_kind=ARTIFACT_KIND_BUNDLE,
                    artifact_name=_norm_rel(rel_path),
                    content_hash=_sha256_file(abs_path),
                )
            )
    return rows


def _manifest_entries(dist_root: str) -> list[dict]:
    rows = []
    root_manifest = os.path.join(dist_root, "manifest.json")
    if os.path.isfile(root_manifest):
        rows.append(
            _artifact_entry(
                artifact_kind=ARTIFACT_KIND_MANIFEST,
                artifact_name="manifest.json",
                content_hash=_sha256_file(root_manifest),
            )
        )
    for current_root, _dirs, files in os.walk(dist_root):
        rel_root = os.path.relpath(current_root, dist_root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(files):
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rel_token = _norm_rel(rel_path)
            if rel_token == _norm_rel(DEFAULT_RELEASE_MANIFEST_REL):
                continue
            if name != "install.manifest.json":
                continue
            rows.append(
                _artifact_entry(
                    artifact_kind=ARTIFACT_KIND_MANIFEST,
                    artifact_name=rel_token,
                    content_hash=_sha256_file(os.path.join(current_root, name)),
                )
            )
    unique = {
        (_token(row.get("artifact_kind")), _token(row.get("artifact_name"))): dict(row)
        for row in rows
    }
    return [unique[key] for key in sorted(unique.keys())]


def _dist_manifest_payload(dist_root: str) -> dict:
    payload, error = _read_json(os.path.join(dist_root, "manifest.json"))
    if error:
        return {}
    return payload


def _release_semver(binary_descriptors: Sequence[Mapping[str, object]], dist_manifest: Mapping[str, object]) -> str:
    versions = {
        _semver_without_build(_token(_as_map(row).get("product_version")))
        for row in list(binary_descriptors or [])
        if _semver_without_build(_token(_as_map(row).get("product_version")))
    }
    for key in ("client_version", "engine_version", "server_version", "setup_version", "launcher_version"):
        token = _semver_without_build(_token(_as_map(dist_manifest).get(key)))
        if token:
            versions.add(token)
    versions.discard("")
    if len(versions) == 1:
        return sorted(versions)[0]
    if not versions:
        return "0.0.0"
    return "mixed"


def _semantic_contract_registry_hash(
    dist_root: str,
    binary_descriptors: Sequence[Mapping[str, object]],
    repo_root: str = "",
) -> str:
    dist_manifest = _dist_manifest_payload(dist_root)
    manifest_hash = _token(dist_manifest.get("semantic_contract_registry_hash")).lower()
    if manifest_hash:
        return manifest_hash
    hashes = sorted(
        {
            _token(_as_map(_as_map(row).get("extensions")).get("official.semantic_contract_registry_hash")).lower()
            for row in list(binary_descriptors or [])
            if _token(_as_map(_as_map(row).get("extensions")).get("official.semantic_contract_registry_hash"))
        }
    )
    if len(hashes) == 1:
        return hashes[0]
    if len(hashes) > 1:
        raise RuntimeError("binary descriptors disagree on semantic_contract_registry_hash")
    repo_token = _token(repo_root)
    if repo_token:
        registry_path = os.path.join(repo_token, "data", "registries", "semantic_contract_registry.json")
        if os.path.isfile(registry_path):
            return _sha256_file(registry_path)
    raise RuntimeError("semantic_contract_registry_hash is not discoverable from the distribution")


def _optional_hash(path: str) -> str:
    abs_path = os.path.normpath(os.path.abspath(path))
    if not os.path.isfile(abs_path):
        return ""
    return _sha256_file(abs_path)


def _descriptor_build_id_cross_check(descriptor: Mapping[str, object]) -> dict:
    descriptor_map = _as_map(descriptor)
    extensions = _as_map(descriptor_map.get("extensions"))
    product_id = _token(descriptor_map.get("product_id"))
    semantic_hash = _token(extensions.get("official.semantic_contract_registry_hash")).lower()
    compilation_hash = _token(extensions.get("official.compilation_options_hash")).lower()
    source_revision = _token(extensions.get("official.source_revision_id"))
    explicit_build_number = _token(extensions.get("official.explicit_build_number"))
    platform_tag = _token(extensions.get("official.platform_tag"))
    actual_build_id = _token(extensions.get("official.build_id"))
    actual_inputs_hash = _token(extensions.get("official.inputs_hash")).lower()
    if not product_id or not semantic_hash or not compilation_hash or (not source_revision and not explicit_build_number):
        return {
            "result": "insufficient_inputs",
            "product_id": product_id,
            "build_id": actual_build_id,
            "inputs_hash": actual_inputs_hash,
        }
    expected = build_id_identity_from_input_payload(
        build_build_id_input_payload(
            product_id=product_id,
            semantic_contract_registry_hash=semantic_hash,
            compilation_options_hash=compilation_hash,
            source_revision_id_value=source_revision,
            explicit_build_number=explicit_build_number,
            platform_tag=platform_tag,
        )
    )
    return {
        "result": "complete",
        "product_id": product_id,
        "build_id": actual_build_id,
        "inputs_hash": actual_inputs_hash,
        "expected_build_id": _token(expected.get("build_id")),
        "expected_inputs_hash": _token(expected.get("inputs_hash")).lower(),
        "build_id_match": actual_build_id == _token(expected.get("build_id")),
        "inputs_hash_match": not actual_inputs_hash or actual_inputs_hash == _token(expected.get("inputs_hash")).lower(),
    }


def cross_check_release_manifest_build_ids(manifest_payload: Mapping[str, object], dist_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(dist_root))
    mismatches: list[dict[str, str]] = []
    checked_binaries = 0
    for row in [_as_map(item) for item in _as_list(_as_map(manifest_payload).get("artifacts"))]:
        if _token(row.get("artifact_kind")) != ARTIFACT_KIND_BINARY:
            continue
        if _token(_as_map(row.get("extensions")).get("binary_role")) == "auxiliary_wrapper":
            continue
        artifact_name = _token(row.get("artifact_name"))
        abs_path = os.path.join(root, artifact_name.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            mismatches.append(
                {
                    "code": "missing_binary",
                    "artifact_name": artifact_name,
                    "message": "binary is missing for build-id cross-check",
                }
            )
            continue
        descriptor, descriptor_error = _run_descriptor(abs_path)
        if not descriptor:
            mismatches.append(
                {
                    "code": "descriptor_unavailable",
                    "artifact_name": artifact_name,
                    "message": descriptor_error or "descriptor unavailable",
                }
            )
            continue
        checked_binaries += 1
        status = _descriptor_build_id_cross_check(descriptor)
        if _token(status.get("result")) == "insufficient_inputs":
            mismatches.append(
                {
                    "code": "insufficient_build_inputs",
                    "artifact_name": artifact_name,
                    "message": "descriptor does not expose enough build metadata to recompute build_id",
                }
            )
            continue
        if not bool(status.get("build_id_match")):
            mismatches.append(
                {
                    "code": "build_id_mismatch",
                    "artifact_name": artifact_name,
                    "message": "descriptor build_id does not match recomputed build_id",
                }
            )
        if not bool(status.get("inputs_hash_match")):
            mismatches.append(
                {
                    "code": "inputs_hash_mismatch",
                    "artifact_name": artifact_name,
                    "message": "descriptor inputs_hash does not match recomputed inputs_hash",
                }
            )
    return {
        "result": "complete" if not mismatches else "refused",
        "checked_binaries": checked_binaries,
        "mismatches": mismatches,
    }


def load_signature_blocks(signature_path: str) -> list[dict]:
    payload, error = _read_json(signature_path)
    if error:
        raise ValueError(error)
    rows = payload.get("signatures")
    if not isinstance(rows, list):
        raise ValueError("signature file must contain a 'signatures' array")
    return _normalized_signature_rows([_as_map(row) for row in rows])


def verify_signature_blocks(signed_hash: str, signatures: Sequence[Mapping[str, object]] | None) -> dict:
    rows = _normalized_signature_rows(signatures)
    if not rows:
        return {"status": "signature_missing", "verified_count": 0, "errors": []}
    errors: list[dict[str, str]] = []
    verified_count = 0
    for row in rows:
        scheme_id = _token(_as_map(row.get("extensions")).get("scheme_id")) or DEFAULT_SIGNATURE_SCHEME_ID
        if _token(row.get("signed_hash")).lower() != _token(signed_hash).lower():
            errors.append(
                {
                    "code": "signature_signed_hash_mismatch",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "signature signed_hash does not match the manifest hash",
                }
            )
            continue
        if scheme_id != DEFAULT_SIGNATURE_SCHEME_ID:
            errors.append(
                {
                    "code": "signature_unknown_scheme",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "unsupported signature scheme '{}'".format(scheme_id),
                }
            )
            continue
        expected = build_mock_signature_block(
            signer_id=_token(row.get("signer_id")),
            signed_hash=_token(row.get("signed_hash")),
            signature_id=_token(row.get("signature_id")),
        )
        if _token(expected.get("signature_bytes")) != _token(row.get("signature_bytes")):
            errors.append(
                {
                    "code": "signature_bytes_mismatch",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "signature bytes do not match the deterministic mock signature hook",
                }
            )
            continue
        verified_count += 1
    return {
        "status": "verified" if not errors else "signature_invalid",
        "verified_count": verified_count,
        "errors": errors,
    }


def infer_dist_root_from_manifest_path(manifest_path: str) -> str:
    target = os.path.normpath(os.path.abspath(manifest_path))
    if os.path.basename(target) != "release_manifest.json":
        return os.path.dirname(target)
    parent = os.path.dirname(target)
    if os.path.basename(parent) == "manifests":
        return os.path.dirname(parent)
    return parent


def build_release_manifest(
    dist_root: str,
    *,
    platform_tag: str,
    channel_id: str = DEFAULT_RELEASE_CHANNEL,
    repo_root: str = "",
    signatures: Sequence[Mapping[str, object]] | None = None,
    verify_build_ids: bool = False,
) -> dict:
    root = os.path.normpath(os.path.abspath(dist_root))
    if not os.path.isdir(root):
        raise FileNotFoundError(root)

    binary_entries: list[dict] = []
    binary_descriptors: list[dict] = []
    product_binary_paths, auxiliary_binary_paths = _binary_paths(root)
    for binary_path in product_binary_paths:
        entry, descriptor = _binary_entry(binary_path, root)
        binary_entries.append(entry)
        binary_descriptors.append(descriptor)
    for binary_path in auxiliary_binary_paths:
        binary_entries.append(_auxiliary_binary_entry(binary_path, root))

    pack_entries: list[dict] = []
    for pack_dir in _pack_dirs(root):
        rel_path = _norm_rel(os.path.relpath(pack_dir, root))
        metadata = _pack_metadata_for_dir(pack_dir)
        pack_entries.append(
            _artifact_entry(
                artifact_kind=ARTIFACT_KIND_PACK,
                artifact_name=rel_path,
                content_hash=_directory_tree_hash(pack_dir),
                pack_compat_hash=_pack_compat_hash_for_dir(pack_dir),
                extensions=metadata,
            )
        )

    artifacts = []
    artifacts.extend(binary_entries)
    artifacts.extend(pack_entries)
    artifacts.extend(_simple_file_entries(root, "profiles", ARTIFACT_KIND_PROFILE))
    artifacts.extend(_simple_file_entries(root, "locks", ARTIFACT_KIND_LOCK))
    root_lock = os.path.join(root, "lockfile.json")
    if os.path.isfile(root_lock):
        artifacts.append(
            _artifact_entry(
                artifact_kind=ARTIFACT_KIND_LOCK,
                artifact_name="lockfile.json",
                content_hash=_sha256_file(root_lock),
            )
        )
    artifacts.extend(_bundle_entries(root))
    artifacts.extend(_manifest_entries(root))
    artifacts = sorted(
        artifacts,
        key=lambda row: (
            _token(_as_map(row).get("artifact_kind")),
            _token(_as_map(row).get("artifact_name")),
        ),
    )

    semver = _release_semver(binary_descriptors, _dist_manifest_payload(root))
    build_ids = sorted(
        {
            _token(_as_map(row).get("build_id"))
            for row in binary_entries
            if _token(_as_map(row).get("build_id"))
        }
    )
    build_set_hash = canonical_sha256({"build_ids": build_ids})
    stability_report_hash = ""
    regression_hashes: dict[str, str] = {}
    repo_token = _token(repo_root)
    if repo_token:
        stability_report_hash = _optional_hash(os.path.join(repo_token, OPTIONAL_STABILITY_REPORT_REL))
        for rel in OPTIONAL_REGRESSION_RELS:
            token = _optional_hash(os.path.join(repo_token, rel))
            if token:
                regression_hashes[_norm_rel(rel)] = token

    payload = {
        "release_id": "release.v{}-{}-{}".format(_token(semver) or "0.0.0", _token(channel_id) or DEFAULT_RELEASE_CHANNEL, build_set_hash[:16]),
        "platform_tag": _token(platform_tag),
        "manifest_version": DEFAULT_RELEASE_MANIFEST_VERSION,
        "semantic_contract_registry_hash": _semantic_contract_registry_hash(root, binary_descriptors, repo_root=repo_token),
        "stability_report_hash": stability_report_hash,
        "artifacts": artifacts,
        "manifest_hash": "",
        "deterministic_fingerprint": "",
        "extensions": {
            "channel_id": _token(channel_id) or DEFAULT_RELEASE_CHANNEL,
            "release_semver": _token(semver) or "0.0.0",
            "release_tag": "v{}-{}".format(_token(semver) or "0.0.0", _token(channel_id) or DEFAULT_RELEASE_CHANNEL),
            "build_set_hash": build_set_hash,
            "build_ids": build_ids,
            "dist_manifest_hash": _optional_hash(os.path.join(root, "manifest.json")),
            "bundle_id": _token(_dist_manifest_payload(root).get("bundle_id")),
            "regression_hashes": dict((key, regression_hashes[key]) for key in sorted(regression_hashes.keys())),
        },
    }
    normalized_signatures = _normalized_signature_rows(signatures)
    if normalized_signatures:
        payload["signatures"] = normalized_signatures
    payload["manifest_hash"] = canonical_sha256(_manifest_hash_payload(payload))
    payload["deterministic_fingerprint"] = canonical_sha256(_manifest_fingerprint_payload(payload))
    if verify_build_ids:
        build_id_report = cross_check_release_manifest_build_ids(payload, root)
        if _token(build_id_report.get("result")) != "complete":
            mismatch_codes = ", ".join(
                _token(_as_map(row).get("code"))
                for row in list(build_id_report.get("mismatches") or [])
                if _token(_as_map(row).get("code"))
            ) or "unknown_mismatch"
            raise RuntimeError("release manifest build-id cross-check failed ({})".format(mismatch_codes))
    return payload


def write_release_manifest(
    dist_root: str,
    manifest_payload: Mapping[str, object],
    *,
    manifest_path: str = "",
) -> str:
    root = os.path.normpath(os.path.abspath(dist_root))
    target = manifest_path or os.path.join(root, DEFAULT_RELEASE_MANIFEST_REL)
    return _write_canonical_json(target, manifest_payload)


def load_release_manifest(manifest_path: str) -> dict:
    payload, error = _read_json(manifest_path)
    if error:
        raise ValueError(error)
    return payload


def verify_release_manifest(
    dist_root: str,
    manifest_path: str,
    *,
    repo_root: str = "",
    signature_path: str = "",
) -> dict:
    root = os.path.normpath(os.path.abspath(dist_root))
    payload = load_release_manifest(manifest_path)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    expected_manifest_hash = canonical_sha256(_manifest_hash_payload(payload))
    if _token(payload.get("manifest_hash")).lower() != expected_manifest_hash:
        errors.append(
            {
                "code": "refusal.release_manifest.manifest_hash_mismatch",
                "path": "manifest_hash",
                "message": "manifest_hash does not match canonical serialized manifest content",
            }
        )
    expected_fingerprint = canonical_sha256(_manifest_fingerprint_payload(payload))
    if _token(payload.get("deterministic_fingerprint")).lower() != expected_fingerprint:
        errors.append(
            {
                "code": "refusal.release_manifest.fingerprint_mismatch",
                "path": "deterministic_fingerprint",
                "message": "deterministic_fingerprint does not match canonical serialized manifest content",
            }
        )

    artifact_rows = [_as_map(row) for row in _as_list(payload.get("artifacts"))]
    sorted_rows = sorted(
        artifact_rows,
        key=lambda row: (_token(row.get("artifact_kind")), _token(row.get("artifact_name"))),
    )
    if artifact_rows != sorted_rows:
        errors.append(
            {
                "code": "refusal.release_manifest.ordering",
                "path": "artifacts",
                "message": "artifact entries are not in canonical sorted order",
            }
        )

    binary_semantic_hashes: set[str] = set()
    verified_artifact_count = 0
    build_id_cross_checked = 0
    for row in artifact_rows:
        artifact_kind = _token(row.get("artifact_kind"))
        artifact_name = _token(row.get("artifact_name"))
        rel_path = artifact_name.replace("/", os.sep)
        abs_path = os.path.join(root, rel_path)
        if artifact_kind == ARTIFACT_KIND_PACK:
            if not os.path.isdir(abs_path):
                errors.append(
                    {
                        "code": "refusal.release_manifest.missing_artifact",
                        "path": artifact_name,
                        "message": "pack artifact is missing",
                    }
                )
                continue
            actual_hash = _directory_tree_hash(abs_path)
            if actual_hash != _token(row.get("content_hash")).lower():
                errors.append(
                    {
                        "code": "refusal.release_manifest.content_hash_mismatch",
                        "path": artifact_name,
                        "message": "pack content hash mismatch",
                    }
                )
            expected_pack_compat = _token(row.get("pack_compat_hash")).lower()
            actual_pack_compat = _pack_compat_hash_for_dir(abs_path)
            if expected_pack_compat and actual_pack_compat != expected_pack_compat:
                errors.append(
                    {
                        "code": "refusal.release_manifest.pack_compat_hash_mismatch",
                        "path": artifact_name,
                        "message": "pack compatibility hash mismatch",
                    }
                )
            verified_artifact_count += 1
            continue

        if not os.path.isfile(abs_path):
            errors.append(
                {
                    "code": "refusal.release_manifest.missing_artifact",
                    "path": artifact_name,
                    "message": "artifact is missing",
                }
            )
            continue

        actual_hash = _sha256_file(abs_path)
        if actual_hash != _token(row.get("content_hash")).lower():
            errors.append(
                {
                    "code": "refusal.release_manifest.content_hash_mismatch",
                    "path": artifact_name,
                    "message": "artifact content hash mismatch",
                }
            )

        if artifact_kind == ARTIFACT_KIND_BINARY:
            expected_descriptor_hash = _token(row.get("endpoint_descriptor_hash")).lower()
            expected_build_id = _token(row.get("build_id"))
            if expected_descriptor_hash or expected_build_id:
                descriptor, descriptor_error = _run_descriptor(abs_path)
                if not descriptor:
                    errors.append(
                        {
                            "code": "refusal.release_manifest.descriptor_unavailable",
                            "path": artifact_name,
                            "message": descriptor_error or "descriptor unavailable",
                        }
                    )
                else:
                    actual_descriptor_hash = canonical_sha256(descriptor)
                    if actual_descriptor_hash != expected_descriptor_hash:
                        errors.append(
                            {
                                "code": "refusal.release_manifest.descriptor_hash_mismatch",
                                "path": artifact_name,
                                "message": "endpoint descriptor hash mismatch",
                            }
                        )
                    actual_build_id = _token(_as_map(descriptor.get("extensions")).get("official.build_id"))
                    if expected_build_id and actual_build_id != expected_build_id:
                        errors.append(
                            {
                                "code": "refusal.release_manifest.build_id_mismatch",
                                "path": artifact_name,
                                "message": "binary build_id mismatch",
                            }
                        )
                    build_id_check = _descriptor_build_id_cross_check(descriptor)
                    if _token(build_id_check.get("result")) == "complete":
                        build_id_cross_checked += 1
                        if not bool(build_id_check.get("build_id_match")):
                            errors.append(
                                {
                                    "code": "refusal.release_manifest.build_id_recompute_mismatch",
                                    "path": artifact_name,
                                    "message": "recomputed build_id does not match descriptor build_id",
                                }
                            )
                        if not bool(build_id_check.get("inputs_hash_match")):
                            errors.append(
                                {
                                    "code": "refusal.release_manifest.inputs_hash_recompute_mismatch",
                                    "path": artifact_name,
                                    "message": "recomputed inputs_hash does not match descriptor inputs_hash",
                                }
                            )
                    elif expected_build_id:
                        warnings.append(
                            {
                                "code": "warn.release_manifest.build_id_inputs_unavailable",
                                "path": artifact_name,
                                "message": "descriptor does not expose enough build inputs to recompute build_id",
                            }
                        )
                    semantic_hash = _token(_as_map(_as_map(descriptor).get("extensions")).get("official.semantic_contract_registry_hash")).lower()
                    if semantic_hash:
                        binary_semantic_hashes.add(semantic_hash)
        verified_artifact_count += 1

    if len(binary_semantic_hashes) == 1:
        actual_semantic_hash = sorted(binary_semantic_hashes)[0]
        if actual_semantic_hash != _token(payload.get("semantic_contract_registry_hash")).lower():
            errors.append(
                {
                    "code": "refusal.release_manifest.semantic_contract_hash_mismatch",
                    "path": "semantic_contract_registry_hash",
                    "message": "binary-emitted semantic_contract_registry_hash does not match the manifest",
                }
            )
    elif len(binary_semantic_hashes) > 1:
        errors.append(
            {
                "code": "refusal.release_manifest.semantic_contract_hash_inconsistent",
                "path": "artifacts",
                "message": "binary descriptors disagree on semantic_contract_registry_hash",
            }
        )
    elif _token(repo_root):
        registry_path = os.path.join(_token(repo_root), "data", "registries", "semantic_contract_registry.json")
        if os.path.isfile(registry_path):
            repo_hash = _sha256_file(registry_path)
            if repo_hash != _token(payload.get("semantic_contract_registry_hash")).lower():
                errors.append(
                    {
                        "code": "refusal.release_manifest.semantic_contract_hash_mismatch",
                        "path": "semantic_contract_registry_hash",
                        "message": "repo semantic_contract_registry_hash does not match the manifest",
                    }
                )
    else:
        warnings.append(
            {
                "code": "warn.release_manifest.semantic_contract_hash_unverified",
                "path": "semantic_contract_registry_hash",
                "message": "semantic_contract_registry_hash could not be cross-checked from local descriptor outputs",
            }
        )

    signature_rows = _normalized_signature_rows(_as_list(payload.get("signatures")))
    detached_signature_path = _token(signature_path)
    signature_file_error = False
    if detached_signature_path:
        detached_abs = os.path.normpath(os.path.abspath(detached_signature_path))
        if not os.path.isfile(detached_abs):
            signature_file_error = True
            errors.append(
                {
                    "code": "refusal.release_manifest.signature_file_missing",
                    "path": detached_signature_path,
                    "message": "signature file is missing",
                }
            )
        else:
            try:
                signature_rows = load_signature_blocks(detached_abs)
            except ValueError as exc:
                signature_file_error = True
                errors.append(
                    {
                        "code": "refusal.release_manifest.signature_file_invalid",
                        "path": detached_signature_path,
                        "message": str(exc),
                    }
                )
    signature_report = (
        {"status": "signature_invalid", "verified_count": 0, "errors": []}
        if signature_file_error
        else verify_signature_blocks(expected_manifest_hash, signature_rows)
    )
    if _token(signature_report.get("status")) == "signature_invalid":
        for row in list(signature_report.get("errors") or []):
            item = _as_map(row)
            errors.append(
                {
                    "code": "refusal.release_manifest.signature_invalid",
                    "path": _token(item.get("signature_id")) or "signatures",
                    "message": _token(item.get("message")) or "signature verification failed",
                }
            )
    elif _token(signature_report.get("status")) == "signature_missing":
        warnings.append(
            {
                "code": "warn.release_manifest.signature_missing",
                "path": "signatures",
                "message": "no detached or inline signatures were provided",
            }
        )

    return {
        "result": "complete" if not errors else "refused",
        "dist_root": _norm_rel(root),
        "manifest_path": _norm_rel(os.path.normpath(os.path.abspath(manifest_path))),
        "release_id": _token(payload.get("release_id")),
        "manifest_hash": _token(payload.get("manifest_hash")).lower(),
        "verified_artifact_count": verified_artifact_count,
        "build_id_cross_checked": build_id_cross_checked,
        "signature_status": _token(signature_report.get("status")) or "signature_missing",
        "verified_signature_count": int(signature_report.get("verified_count") or 0),
        "errors": errors,
        "warnings": warnings,
    }


__all__ = [
    "ARTIFACT_KIND_BINARY",
    "ARTIFACT_KIND_BUNDLE",
    "ARTIFACT_KIND_LOCK",
    "ARTIFACT_KIND_MANIFEST",
    "ARTIFACT_KIND_PACK",
    "ARTIFACT_KIND_PROFILE",
    "DEFAULT_RELEASE_CHANNEL",
    "DEFAULT_RELEASE_MANIFEST_REL",
    "DEFAULT_RELEASE_MANIFEST_VERSION",
    "DEFAULT_SIGNATURE_SCHEME_ID",
    "PRODUCT_BINARY_FILENAMES",
    "build_release_manifest",
    "build_mock_signature_block",
    "cross_check_release_manifest_build_ids",
    "infer_dist_root_from_manifest_path",
    "load_release_manifest",
    "load_signature_blocks",
    "verify_signature_blocks",
    "verify_release_manifest",
    "write_release_manifest",
]
