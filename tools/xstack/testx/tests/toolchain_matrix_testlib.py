"""Shared Ω-9 toolchain matrix TestX helpers."""

from __future__ import annotations

import os

from tools.mvp.toolchain_matrix_common import (
    DEFAULT_ENV_ID,
    DEFAULT_PROFILE_ID,
    TOOLCHAIN_HASHES_SCHEMA_ID,
    TOOLCHAIN_RUN_MANIFEST_SCHEMA_ID,
    build_run_id,
    load_toolchain_matrix_registry,
    load_toolchain_test_profile_registry,
    select_env_row,
    select_profile_row,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


def committed_matrix_registry(repo_root: str) -> dict:
    return load_toolchain_matrix_registry(os.path.abspath(repo_root))


def committed_profile_registry(repo_root: str) -> dict:
    return load_toolchain_test_profile_registry(os.path.abspath(repo_root))


def default_env_row(repo_root: str) -> dict:
    return select_env_row(os.path.abspath(repo_root), DEFAULT_ENV_ID)


def default_profile_row(repo_root: str) -> dict:
    return select_profile_row(os.path.abspath(repo_root), DEFAULT_PROFILE_ID)


def deterministic_run_id(repo_root: str) -> tuple[str, dict]:
    root = os.path.abspath(repo_root)
    return build_run_id(root, default_env_row(root), default_profile_row(root))


def write_synthetic_run_root(
    run_root: str,
    *,
    env_id: str = DEFAULT_ENV_ID,
    profile_id: str = DEFAULT_PROFILE_ID,
    run_input_fingerprint: str = "same-input-fingerprint",
    build_ids: dict[str, str] | None = None,
    endpoint_semantic_hashes: dict[str, str] | None = None,
    worldgen_snapshot_hash: str = "worldgen.same",
    baseline_universe_hash: str = "universe.same",
    gameplay_snapshot_hash: str = "gameplay.same",
    proof_anchor_hashes: dict[str, str] | None = None,
) -> str:
    root = os.path.abspath(run_root)
    os.makedirs(root, exist_ok=True)
    build_ids_map = dict(build_ids or {"client": "build.client", "server": "build.server"})
    endpoint_semantics_map = dict(endpoint_semantic_hashes or {"client": "sem.client", "server": "sem.server"})
    proof_anchor_map = dict(proof_anchor_hashes or {"T0": "anchor.t0", "T1": "anchor.t1"})
    manifest = {
        "schema_id": TOOLCHAIN_RUN_MANIFEST_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": env_id,
        "profile_id": profile_id,
        "run_id": os.path.basename(root),
        "run_input_fingerprint": run_input_fingerprint,
        "source_revision_id": "synthetic-revision",
        "source_snapshot_hash": "synthetic-snapshot",
        "env_descriptor_hash": "env-hash",
        "profile_descriptor_hash": "profile-hash",
        "run_root_rel": root.replace("\\", "/"),
        "env_root_rel": os.path.dirname(root).replace("\\", "/"),
        "output_files": {},
        "deterministic_fingerprint": "",
    }
    manifest["deterministic_fingerprint"] = canonical_sha256(dict(manifest, deterministic_fingerprint=""))
    hashes = {
        "schema_id": TOOLCHAIN_HASHES_SCHEMA_ID,
        "schema_version": "1.0.0",
        "env_id": env_id,
        "profile_id": profile_id,
        "run_id": os.path.basename(root),
        "run_input_fingerprint": run_input_fingerprint,
        "source_revision_id": "synthetic-revision",
        "source_snapshot_hash": "synthetic-snapshot",
        "build_ids_hash": "build-ids-hash",
        "build_ids": build_ids_map,
        "endpoint_descriptor_hashes": dict((key, "{}.hash".format(value)) for key, value in endpoint_semantics_map.items()),
        "endpoint_descriptor_semantic_hashes": endpoint_semantics_map,
        "endpoint_descriptor_semantic_hash": "semantic-hash",
        "worldgen_snapshot_hash": worldgen_snapshot_hash,
        "baseline_universe_hash": baseline_universe_hash,
        "gameplay_snapshot_hash": gameplay_snapshot_hash,
        "proof_anchor_hashes": proof_anchor_map,
        "release_manifest_hash": "",
        "release_manifest_projection_hash": "",
        "release_manifest_verified_hash": "",
        "negotiation_record_hash": "",
        "deterministic_fingerprint": "",
    }
    hashes["deterministic_fingerprint"] = canonical_sha256(dict(hashes, deterministic_fingerprint=""))
    results = {
        "schema_id": "dominium.schema.audit.toolchain_matrix_results",
        "schema_version": "1.0.0",
        "env_id": env_id,
        "profile_id": profile_id,
        "run_id": os.path.basename(root),
        "run_input_fingerprint": run_input_fingerprint,
        "result": "complete",
        "steps": [],
        "summary": {
            "result": "complete",
        },
        "hashes_fingerprint": hashes["deterministic_fingerprint"],
        "deterministic_fingerprint": "",
    }
    results["deterministic_fingerprint"] = canonical_sha256(dict(results, deterministic_fingerprint=""))
    for filename, payload in (
        ("run_manifest.json", manifest),
        ("hashes.json", hashes),
        ("results.json", results),
    ):
        with open(os.path.join(root, filename), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json_text(payload))
            handle.write("\n")
    return root


__all__ = [
    "committed_matrix_registry",
    "committed_profile_registry",
    "default_env_row",
    "default_profile_row",
    "deterministic_run_id",
    "write_synthetic_run_root",
]
