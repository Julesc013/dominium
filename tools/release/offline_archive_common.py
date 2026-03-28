"""Deterministic OFFLINE-ARCHIVE-VERIFY-0 helpers for Omega MVP freezes."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tarfile
import tempfile
from typing import Mapping, Sequence

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases
install_src_aliases(REPO_ROOT_HINT)

from compat.migration_lifecycle import load_migration_policy_registry
from governance import governance_profile_hash, load_governance_profile
from release import (
    DEFAULT_RELEASE_INDEX_REL,
    DEFAULT_RELEASE_MANIFEST_REL,
    load_release_index,
    load_release_manifest,
    release_index_hash,
    write_release_index,
)
from release.archive_policy import release_index_history_rel
from security.trust import load_trust_root_registry
from tools.compatx.core.semantic_contract_validator import (
    load_semantic_contract_registry,
    registry_hash as semantic_contract_registry_hash,
)
from tools.release.update_model_common import build_release_index_payload
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


OFFLINE_ARCHIVE_RECORD_SCHEMA_ID = "dominium.schema.release.offline_archive_record"
OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID = "dominium.schema.audit.offline_archive_verify"
OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID = "dominium.schema.governance.archive_baseline"
OFFLINE_ARCHIVE_VERSION = 0
OFFLINE_ARCHIVE_STABILITY_CLASS = "stable"
OFFLINE_ARCHIVE_REQUIRED_TAG = "ARCHIVE-REGRESSION-UPDATE"

OFFLINE_ARCHIVE_RETRO_AUDIT_REL = os.path.join("docs", "audit", "ARCHIVE_OFFLINE0_RETRO_AUDIT.md")
OFFLINE_ARCHIVE_MODEL_DOC_REL = os.path.join("docs", "release", "OFFLINE_ARCHIVE_MODEL_v0_0_0.md")
OFFLINE_ARCHIVE_VERIFY_DOC_REL = os.path.join("docs", "audit", "OFFLINE_ARCHIVE_VERIFY.md")
OFFLINE_ARCHIVE_VERIFY_JSON_REL = os.path.join("data", "audit", "offline_archive_verify.json")
OFFLINE_ARCHIVE_BASELINE_REL = os.path.join("data", "regression", "archive_baseline.json")
OFFLINE_ARCHIVE_BASELINE_DOC_REL = os.path.join("docs", "audit", "OFFLINE_ARCHIVE_BASELINE.md")
OFFLINE_ARCHIVE_BUILD_TOOL_REL = os.path.join("tools", "release", "tool_build_offline_archive")
OFFLINE_ARCHIVE_BUILD_TOOL_PY_REL = os.path.join("tools", "release", "tool_build_offline_archive.py")
OFFLINE_ARCHIVE_VERIFY_TOOL_REL = os.path.join("tools", "release", "tool_verify_offline_archive")
OFFLINE_ARCHIVE_VERIFY_TOOL_PY_REL = os.path.join("tools", "release", "tool_verify_offline_archive.py")

DEFAULT_RELEASE_ID = "v0.0.0-mock"
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_DIST_ROOT_REL = os.path.join("dist", DEFAULT_RELEASE_ID, DEFAULT_PLATFORM_TAG, "dominium")
DEFAULT_OUTPUT_ROOT_REL = os.path.join("build", "offline_archive")
DEFAULT_WORK_ROOT_REL = os.path.join("build", "tmp", "omega8_offline_archive")
ARCHIVE_RECORD_FILENAME = "archive_record.json"

ARCHIVE_ARTIFACTS_DIR = "artifacts"
ARCHIVE_BASELINES_DIR = "baselines"
ARCHIVE_FIXTURES_DIR = "fixtures"

WORLDGEN_SEED_REL = os.path.join("data", "baselines", "worldgen", "baseline_seed.txt")
WORLDGEN_SNAPSHOT_REL = os.path.join("data", "baselines", "worldgen", "baseline_worldgen_snapshot.json")
UNIVERSE_INSTANCE_REL = os.path.join("data", "baselines", "universe", "baseline_instance.manifest.json")
UNIVERSE_PACK_LOCK_REL = os.path.join("data", "baselines", "universe", "baseline_pack_lock.json")
UNIVERSE_PROFILE_BUNDLE_REL = os.path.join("data", "baselines", "universe", "baseline_profile_bundle.json")
UNIVERSE_SAVE_REL = os.path.join("data", "baselines", "universe", "baseline_save_0.save")
UNIVERSE_SNAPSHOT_REL = os.path.join("data", "baselines", "universe", "baseline_universe_snapshot.json")
GAMEPLAY_SNAPSHOT_REL = os.path.join("data", "baselines", "gameplay", "gameplay_loop_snapshot.json")
DISASTER_CASES_REL = os.path.join("data", "baselines", "disaster", "disaster_suite_cases.json")
DISASTER_BASELINE_REL = os.path.join("data", "regression", "disaster_suite_baseline.json")
ECOSYSTEM_BASELINE_REL = os.path.join("data", "regression", "ecosystem_verify_baseline.json")
UPDATE_SIM_BASELINE_REL = os.path.join("data", "regression", "update_sim_baseline.json")
TRUST_STRICT_BASELINE_REL = os.path.join("data", "regression", "trust_strict_baseline.json")
PERFORMANCE_ENVELOPE_BASELINE_REL = os.path.join("docs", "audit", "PERFORMANCE_ENVELOPE_BASELINE.md")
PERFORMX_BASELINE_REL = os.path.join("docs", "audit", "performance", "PERFORMX_BASELINE.json")
MVP_STRESS_BASELINE_REL = os.path.join("data", "regression", "mvp_stress_baseline.json")
UPDATE_FIXTURE_DIR_REL = os.path.join("data", "baselines", "update_sim")
TRUST_FIXTURE_DIR_REL = os.path.join("data", "baselines", "trust")

RELEASE_INDEX_SNAPSHOT_REL = "release_index.json"
RELEASE_MANIFEST_SNAPSHOT_REL = "release_manifest.json"
COMPONENT_GRAPH_SNAPSHOT_REL = "component_graph.json"

_JSON_SUFFIXES = (".json", ".schema")
_SUBCHECK_IDS = (
    "release_manifest_hashes",
    "release_index_history_integrity",
    "artifact_cas_hashes",
    "trust_registry_match",
    "worldgen_lock_verify",
    "baseline_universe_verify",
    "gameplay_loop_verify",
    "disaster_suite_verify",
)
_SUPPORT_SURFACES = (
    ("worldgen.seed", WORLDGEN_SEED_REL, os.path.join(ARCHIVE_BASELINES_DIR, "worldgen", "baseline_seed.txt")),
    ("worldgen.snapshot", WORLDGEN_SNAPSHOT_REL, os.path.join(ARCHIVE_BASELINES_DIR, "worldgen", "baseline_worldgen_snapshot.json")),
    ("universe.instance_manifest", UNIVERSE_INSTANCE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "universe", "baseline_instance.manifest.json")),
    ("universe.pack_lock", UNIVERSE_PACK_LOCK_REL, os.path.join(ARCHIVE_BASELINES_DIR, "universe", "baseline_pack_lock.json")),
    ("universe.profile_bundle", UNIVERSE_PROFILE_BUNDLE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "universe", "baseline_profile_bundle.json")),
    ("universe.save_0", UNIVERSE_SAVE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "universe", "baseline_save_0.save")),
    ("universe.snapshot", UNIVERSE_SNAPSHOT_REL, os.path.join(ARCHIVE_BASELINES_DIR, "universe", "baseline_universe_snapshot.json")),
    ("gameplay.snapshot", GAMEPLAY_SNAPSHOT_REL, os.path.join(ARCHIVE_BASELINES_DIR, "gameplay", "gameplay_loop_snapshot.json")),
    ("disaster.cases", DISASTER_CASES_REL, os.path.join(ARCHIVE_BASELINES_DIR, "disaster", "disaster_suite_cases.json")),
    ("disaster.baseline", DISASTER_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "disaster", "disaster_suite_baseline.json")),
    ("ecosystem.baseline", ECOSYSTEM_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "ecosystem", "ecosystem_verify_baseline.json")),
    ("update_sim.baseline", UPDATE_SIM_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "update_sim", "update_sim_baseline.json")),
    ("trust_strict.baseline", TRUST_STRICT_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "trust", "trust_strict_baseline.json")),
    ("performance.envelope_baseline", PERFORMANCE_ENVELOPE_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "performance", "PERFORMANCE_ENVELOPE_BASELINE.md")),
    ("performance.performx_baseline", PERFORMX_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "performance", "PERFORMX_BASELINE.json")),
    ("performance.mvp_stress_baseline", MVP_STRESS_BASELINE_REL, os.path.join(ARCHIVE_BASELINES_DIR, "performance", "mvp_stress_baseline.json")),
)
_FIXTURE_DIRS = (
    ("update_sim.fixtures", UPDATE_FIXTURE_DIR_REL, os.path.join(ARCHIVE_FIXTURES_DIR, "update_sim")),
    ("trust.fixtures", TRUST_FIXTURE_DIR_REL, os.path.join(ARCHIVE_FIXTURES_DIR, "trust")),
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return os.path.normpath(os.path.abspath(repo_root))
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _relative_to(repo_root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    abs_path = os.path.normpath(os.path.abspath(token))
    try:
        rel = os.path.relpath(abs_path, repo_root)
    except ValueError:
        return _norm(abs_path)
    return _norm(rel)


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _safe_rmtree(path: str) -> None:
    token = _token(path)
    if token and os.path.isdir(token):
        shutil.rmtree(token, ignore_errors=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return path


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directory_tree_hash(path: str) -> str:
    rows = []
    root = os.path.normpath(os.path.abspath(path))
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(filenames):
            abs_path = os.path.join(current_root, name)
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rows.append({"path": _norm(rel_path), "sha256": _sha256_file(abs_path)})
    return canonical_sha256({"files": rows})


def _path_hash(path: str) -> str:
    token = _token(path)
    if not token or not os.path.exists(token):
        return ""
    if os.path.isdir(token):
        return _directory_tree_hash(token)
    return _sha256_file(token)


def _copy_path(source: str, target: str) -> None:
    parent = os.path.dirname(target)
    if parent:
        _ensure_dir(parent)
    if os.path.isdir(source):
        if os.path.exists(target):
            _safe_rmtree(target)
        shutil.copytree(source, target)
        return
    shutil.copy2(source, target)


def _iter_dir_files(root: str) -> list[str]:
    rows: list[str] = []
    root_abs = os.path.normpath(os.path.abspath(root))
    for current_root, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root_abs)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(filenames):
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rows.append(_norm(rel_path))
    return sorted(rows)


def _gather_member_rows(root: str, *, exclude_rel_paths: Sequence[str] | None = None) -> list[dict]:
    excluded = {_norm(path) for path in list(exclude_rel_paths or []) if _norm(path)}
    rows: list[dict] = []
    root_abs = os.path.normpath(os.path.abspath(root))
    for current_root, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root_abs)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(filenames):
            abs_path = os.path.join(current_root, name)
            rel_path = _norm(os.path.join(rel_root, name) if rel_root else name)
            if rel_path in excluded:
                continue
            rows.append({"path": rel_path, "sha256": _sha256_file(abs_path)})
    return sorted(rows, key=lambda row: str(row.get("path", "")))


def _copy_fixture_dir(repo_root: str, source_rel: str, staging_root: str, archive_rel_root: str) -> list[dict]:
    source_root = _repo_abs(repo_root, source_rel)
    if not os.path.isdir(source_root):
        raise FileNotFoundError(source_root)
    target_root = os.path.join(staging_root, archive_rel_root.replace("/", os.sep))
    _safe_rmtree(target_root)
    shutil.copytree(source_root, target_root)
    rows = []
    for rel_file in _iter_dir_files(source_root):
        target_path = os.path.join(target_root, rel_file.replace("/", os.sep))
        rows.append(
            {
                "surface_id": "{}.{}".format(_token(source_rel).replace("/", ".").replace("\\", ".").strip("."), rel_file.replace("/", ".")),
                "source_rel": _norm(os.path.join(source_rel, rel_file)),
                "archive_rel": _norm(os.path.join(archive_rel_root, rel_file)),
                "content_hash": _path_hash(target_path),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("archive_rel", "")))


def _release_bundle_paths(repo_root: str, dist_root: str, platform_tag: str) -> tuple[str, str, str]:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    bundle_root = _repo_abs(repo_root_abs, dist_root or DEFAULT_DIST_ROOT_REL)
    release_manifest_path = os.path.join(bundle_root, DEFAULT_RELEASE_MANIFEST_REL.replace("/", os.sep))
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL.replace("/", os.sep))
    if not os.path.isfile(release_manifest_path):
        raise FileNotFoundError(release_manifest_path)
    if not os.path.isfile(release_index_path):
        release_index_payload = build_release_index_payload(
            repo_root_abs,
            dist_root=bundle_root,
            platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        )
        write_release_index(release_index_path, release_index_payload)
    return bundle_root, release_manifest_path, release_index_path


def _artifact_entry(rel_manifest_row: Mapping[str, object], *, bundle_root: str, staging_root: str, artifact_store_root: str) -> dict:
    row = _as_map(rel_manifest_row)
    rel_path = _token(row.get("artifact_name"))
    content_hash = _token(row.get("content_hash")).lower()
    artifact_kind = _token(row.get("artifact_kind"))
    if not rel_path or not content_hash:
        raise ValueError("release manifest artifact row missing artifact_name/content_hash")
    source_abs = os.path.join(bundle_root, rel_path.replace("/", os.sep))
    if not os.path.exists(source_abs) and _token(artifact_store_root):
        hash_candidate = os.path.join(artifact_store_root, content_hash)
        rel_candidate = os.path.join(artifact_store_root, rel_path.replace("/", os.sep))
        for candidate in (hash_candidate, rel_candidate):
            if os.path.exists(candidate):
                source_abs = candidate
                break
    if not os.path.exists(source_abs):
        raise FileNotFoundError(source_abs)
    cas_rel = _norm(os.path.join(ARCHIVE_ARTIFACTS_DIR, content_hash))
    cas_abs = os.path.join(staging_root, cas_rel.replace("/", os.sep))
    if os.path.exists(cas_abs):
        if os.path.isdir(cas_abs) == os.path.isdir(source_abs) and _path_hash(cas_abs) == _path_hash(source_abs):
            return {
                "artifact_kind": artifact_kind,
                "source_rel": _norm(rel_path),
                "cas_rel": cas_rel,
                "content_hash": content_hash,
                "is_directory": bool(os.path.isdir(source_abs)),
            }
        raise ValueError("CAS collision detected for '{}'".format(cas_rel))
    _copy_path(source_abs, cas_abs)
    observed_hash = _path_hash(cas_abs)
    if observed_hash != content_hash:
        raise ValueError("artifact '{}' copied to CAS with hash drift".format(rel_path))
    return {
        "artifact_kind": artifact_kind,
        "source_rel": _norm(rel_path),
        "cas_rel": cas_rel,
        "content_hash": content_hash,
        "is_directory": bool(os.path.isdir(source_abs)),
    }


def _component_graph_snapshot(release_index_payload: Mapping[str, object]) -> dict:
    return dict(_as_map(_as_map(release_index_payload.get("extensions")).get("component_graph")))


def _stage_support_surfaces(repo_root: str, staging_root: str) -> list[dict]:
    rows: list[dict] = []
    for surface_id, source_rel, archive_rel in _SUPPORT_SURFACES:
        source_abs = _repo_abs(repo_root, source_rel)
        if not os.path.exists(source_abs):
            raise FileNotFoundError(source_abs)
        target_abs = os.path.join(staging_root, archive_rel.replace("/", os.sep))
        _copy_path(source_abs, target_abs)
        rows.append(
            {
                "surface_id": surface_id,
                "source_rel": _norm(source_rel),
                "archive_rel": _norm(archive_rel),
                "content_hash": _path_hash(target_abs),
            }
        )
    for surface_prefix, source_rel, archive_rel_root in _FIXTURE_DIRS:
        for row in _copy_fixture_dir(repo_root, source_rel, staging_root, archive_rel_root):
            rows.append(
                {
                    "surface_id": "{}.{}".format(surface_prefix, _token(row.get("archive_rel")).replace("/", ".")),
                    "source_rel": _token(row.get("source_rel")),
                    "archive_rel": _token(row.get("archive_rel")),
                    "content_hash": _token(row.get("content_hash")),
                }
            )
    return sorted(rows, key=lambda row: str(row.get("archive_rel", "")))


def _stage_governance_and_release(
    repo_root: str,
    *,
    bundle_root: str,
    release_manifest_path: str,
    release_index_path: str,
    staging_root: str,
    release_id: str,
) -> dict:
    release_index = load_release_index(release_index_path)
    release_manifest = load_release_manifest(release_manifest_path)
    component_graph = _component_graph_snapshot(release_index)
    governance = load_governance_profile(repo_root, install_root=bundle_root)
    trust_roots = load_trust_root_registry(repo_root=repo_root, install_root=bundle_root)
    migration_registry = load_migration_policy_registry(repo_root)
    semantic_registry, semantic_error = load_semantic_contract_registry(repo_root)
    if semantic_error:
        raise FileNotFoundError(semantic_error)

    history_rel = _norm(release_index_history_rel(_token(release_index.get("channel")) or "mock", release_id))
    _write_canonical_json(os.path.join(staging_root, history_rel.replace("/", os.sep)), release_index)
    _write_canonical_json(os.path.join(staging_root, RELEASE_INDEX_SNAPSHOT_REL.replace("/", os.sep)), release_index)
    _write_canonical_json(os.path.join(staging_root, RELEASE_MANIFEST_SNAPSHOT_REL.replace("/", os.sep)), release_manifest)
    _write_canonical_json(os.path.join(staging_root, COMPONENT_GRAPH_SNAPSHOT_REL.replace("/", os.sep)), component_graph)
    _write_canonical_json(os.path.join(staging_root, "governance_profile.json"), governance)
    _write_canonical_json(os.path.join(staging_root, "trust_root_registry.json"), trust_roots)
    _write_canonical_json(os.path.join(staging_root, "migration_policy_registry.json"), migration_registry)
    _write_canonical_json(os.path.join(staging_root, "semantic_contract_registry.json"), semantic_registry)
    return {
        "release_index": release_index,
        "release_manifest": release_manifest,
        "component_graph": component_graph,
        "governance": governance,
        "trust_roots": trust_roots,
        "migration_registry": migration_registry,
        "semantic_registry": semantic_registry,
        "release_index_history_rel": history_rel,
    }


def _source_snapshot_rows(repo_root: str, staging_root: str, work_root: str) -> tuple[str, str]:
    source_stage = os.path.join(work_root, "source_snapshot_stage")
    _safe_rmtree(source_stage)
    _ensure_dir(source_stage)
    include_roots = [
        "AGENTS.md",
        "CMakeLists.txt",
        "docs",
        "data",
        "schema",
        "schemas",
        "src",
        "tools",
    ]
    for rel_path in include_roots:
        source_abs = _repo_abs(repo_root, rel_path)
        if not os.path.exists(source_abs):
            continue
        _copy_path(source_abs, os.path.join(source_stage, rel_path.replace("/", os.sep)))
    snapshot_rel = "source_snapshot.tar.gz"
    snapshot_abs = os.path.join(staging_root, snapshot_rel.replace("/", os.sep))
    from archive.deterministic_bundle import build_deterministic_archive_bundle

    build_deterministic_archive_bundle(
        source_stage,
        snapshot_abs,
        root_arcname="dominium-source-{}".format(DEFAULT_RELEASE_ID),
    )
    return snapshot_rel, _sha256_file(snapshot_abs)


def offline_archive_record_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def offline_archive_verify_hash(payload: Mapping[str, object]) -> str:
    body = dict(dict(payload or {}), deterministic_fingerprint="")
    body["archive_path"] = ""
    body["baseline_path"] = ""
    return canonical_sha256(body)


def offline_archive_baseline_hash(payload: Mapping[str, object]) -> str:
    body = dict(dict(payload or {}), deterministic_fingerprint="")
    body["archive_bundle_rel"] = ""
    return canonical_sha256(body)


def _render_verify_doc(report: Mapping[str, object]) -> str:
    subchecks = _as_map(report.get("subchecks"))
    lines = [
        "# Offline Archive Verify",
        "",
        "- Result: `{}`".format("PASS" if _token(report.get("result")) == "complete" else "FAIL"),
        "- Archive Bundle Hash: `{}`".format(_token(report.get("archive_bundle_hash"))),
        "- Archive Record Hash: `{}`".format(_token(report.get("archive_record_hash"))),
        "- Archive Projection Hash: `{}`".format(_token(report.get("archive_projection_hash"))),
        "- Deterministic Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Subchecks",
        "",
    ]
    for check_id in _SUBCHECK_IDS:
        row = _as_map(subchecks.get(check_id))
        lines.append("- `{}` => `{}`".format(check_id, _token(row.get("result")) or "missing"))
    return "\n".join(lines) + "\n"


def _render_baseline_doc(baseline: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-25",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: stable",
        "Future Series: DIST-7/ARCHIVE",
        "Replacement Target: signed release publication archives with retained historical channel bundles",
        "",
        "# Offline Archive Baseline",
        "",
        "## Archive Hashes",
        "",
        "- release_id: `{}`".format(_token(baseline.get("release_id"))),
        "- archive_bundle_hash: `{}`".format(_token(baseline.get("archive_bundle_hash"))),
        "- archive_record_hash: `{}`".format(_token(baseline.get("archive_record_hash"))),
        "- archive_projection_hash: `{}`".format(_token(baseline.get("archive_projection_hash"))),
        "",
        "## Verification Summary",
        "",
        "- verification_result: `{}`".format(_token(baseline.get("verification_result"))),
        "- verification_fingerprint: `{}`".format(_token(baseline.get("verification_fingerprint"))),
        "- required_update_tag: `{}`".format(_token(baseline.get("required_update_tag"))),
        "",
        "## Rebuildability",
        "",
        "- release manifest snapshot retained: yes",
        "- release index history retained: yes",
        "- governance + trust registries retained: yes",
        "- worldgen + universe + gameplay + disaster baselines retained: yes",
        "- performance baseline retained: yes",
        "- archive verifier reruns frozen Ω subchecks offline against the archived surfaces: yes",
        "",
    ]
    return "\n".join(lines)


def _bundle_output_paths(repo_root: str, release_id: str, output_root_rel: str) -> dict:
    output_root_abs = _repo_abs(repo_root, output_root_rel or DEFAULT_OUTPUT_ROOT_REL)
    work_root_abs = _repo_abs(repo_root, DEFAULT_WORK_ROOT_REL)
    archive_name = "dominium-archive-{}.tar.gz".format(_token(release_id) or DEFAULT_RELEASE_ID)
    return {
        "output_root_abs": output_root_abs,
        "work_root_abs": work_root_abs,
        "staging_root_abs": os.path.join(work_root_abs, "staging", _token(release_id) or DEFAULT_RELEASE_ID),
        "archive_bundle_abs": os.path.join(output_root_abs, archive_name),
        "archive_name": archive_name,
        "root_arcname": "dominium-archive-{}".format(_token(release_id) or DEFAULT_RELEASE_ID),
    }


def build_offline_archive(
    repo_root: str,
    *,
    release_id: str = DEFAULT_RELEASE_ID,
    dist_root: str = "",
    artifact_store_path: str = "",
    platform_tag: str = DEFAULT_PLATFORM_TAG,
    output_root_rel: str = "",
    include_source_snapshot: bool = False,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    bundle_root, release_manifest_path, release_index_path = _release_bundle_paths(repo_root_abs, dist_root, platform_tag)
    paths = _bundle_output_paths(repo_root_abs, _token(release_id) or DEFAULT_RELEASE_ID, output_root_rel)
    _ensure_dir(paths["output_root_abs"])
    _safe_rmtree(paths["staging_root_abs"])
    _ensure_dir(paths["staging_root_abs"])

    staged = _stage_governance_and_release(
        repo_root_abs,
        bundle_root=bundle_root,
        release_manifest_path=release_manifest_path,
        release_index_path=release_index_path,
        staging_root=paths["staging_root_abs"],
        release_id=_token(release_id) or DEFAULT_RELEASE_ID,
    )
    artifact_store_abs = _repo_abs(repo_root_abs, artifact_store_path) if _token(artifact_store_path) else ""
    artifact_entries = []
    for row in _as_list(_as_map(staged.get("release_manifest")).get("artifacts")):
        artifact_entries.append(
            _artifact_entry(
                row,
                bundle_root=bundle_root,
                staging_root=paths["staging_root_abs"],
                artifact_store_root=artifact_store_abs,
            )
        )
    artifact_entries = sorted(artifact_entries, key=lambda row: (str(row.get("content_hash", "")), str(row.get("source_rel", ""))))
    support_surfaces = _stage_support_surfaces(repo_root_abs, paths["staging_root_abs"])

    source_snapshot_rel = ""
    source_snapshot_hash = ""
    if include_source_snapshot:
        source_snapshot_rel, source_snapshot_hash = _source_snapshot_rows(repo_root_abs, paths["staging_root_abs"], paths["work_root_abs"])

    archive_projection_hash = canonical_sha256({"files": _gather_member_rows(paths["staging_root_abs"], exclude_rel_paths=[ARCHIVE_RECORD_FILENAME])})
    record = {
        "schema_id": OFFLINE_ARCHIVE_RECORD_SCHEMA_ID,
        "schema_version": "1.0.0",
        "offline_archive_version": OFFLINE_ARCHIVE_VERSION,
        "stability_class": OFFLINE_ARCHIVE_STABILITY_CLASS,
        "release_id": _token(release_id) or DEFAULT_RELEASE_ID,
        "manifest_release_id": _token(_as_map(staged.get("release_manifest")).get("release_id")),
        "release_manifest_hash": _token(_as_map(staged.get("release_manifest")).get("manifest_hash")).lower(),
        "release_index_hash": release_index_hash(_as_map(staged.get("release_index"))),
        "component_graph_hash": canonical_sha256(_as_map(staged.get("component_graph"))),
        "governance_profile_hash": governance_profile_hash(_as_map(staged.get("governance"))),
        "trust_root_registry_hash": canonical_sha256(_as_map(staged.get("trust_roots"))),
        "migration_policy_registry_hash": canonical_sha256(_as_map(staged.get("migration_registry"))),
        "semantic_contract_registry_hash": semantic_contract_registry_hash(_as_map(staged.get("semantic_registry"))),
        "archive_projection_hash": archive_projection_hash,
        "artifacts": artifact_entries,
        "bundled_support_surfaces": support_surfaces,
        "deterministic_fingerprint": "",
        "extensions": {
            "root_arcname": _token(paths["root_arcname"]),
            "release_index_history_rel": _token(staged.get("release_index_history_rel")),
            "release_index_rel": RELEASE_INDEX_SNAPSHOT_REL,
            "release_manifest_rel": RELEASE_MANIFEST_SNAPSHOT_REL,
            "component_graph_rel": COMPONENT_GRAPH_SNAPSHOT_REL,
            "governance_profile_rel": "governance_profile.json",
            "trust_root_registry_rel": "trust_root_registry.json",
            "migration_policy_registry_rel": "migration_policy_registry.json",
            "semantic_contract_registry_rel": "semantic_contract_registry.json",
            "source_snapshot_rel": _token(source_snapshot_rel),
            "source_snapshot_hash": _token(source_snapshot_hash),
            "required_subchecks": list(_SUBCHECK_IDS),
        },
    }
    record["deterministic_fingerprint"] = offline_archive_record_hash(record)
    _write_canonical_json(os.path.join(paths["staging_root_abs"], ARCHIVE_RECORD_FILENAME), record)

    from archive.deterministic_bundle import build_deterministic_archive_bundle

    bundle = build_deterministic_archive_bundle(
        paths["staging_root_abs"],
        paths["archive_bundle_abs"],
        root_arcname=paths["root_arcname"],
    )
    return {
        "result": "complete",
        "release_id": _token(release_id) or DEFAULT_RELEASE_ID,
        "dist_root": _relative_to(repo_root_abs, bundle_root),
        "archive_bundle_path": paths["archive_bundle_abs"],
        "archive_bundle_rel": _relative_to(repo_root_abs, paths["archive_bundle_abs"]),
        "archive_bundle_hash": _token(bundle.get("bundle_hash")).lower(),
        "archive_record": record,
        "archive_record_hash": _token(record.get("deterministic_fingerprint")),
        "archive_projection_hash": archive_projection_hash,
        "artifact_count": len(artifact_entries),
        "support_surface_count": len(support_surfaces),
        "member_count": int(bundle.get("file_count", 0) or 0),
        "source_snapshot_rel": _token(source_snapshot_rel),
        "source_snapshot_hash": _token(source_snapshot_hash),
        "staging_root_rel": _relative_to(repo_root_abs, paths["staging_root_abs"]),
        "deterministic_fingerprint": canonical_sha256(
            {
                "release_id": _token(release_id) or DEFAULT_RELEASE_ID,
                "archive_bundle_hash": _token(bundle.get("bundle_hash")).lower(),
                "archive_record_hash": _token(record.get("deterministic_fingerprint")),
                "archive_projection_hash": archive_projection_hash,
                "artifact_count": len(artifact_entries),
                "support_surface_count": len(support_surfaces),
            }
        ),
    }


def build_archive_baseline(build_report: Mapping[str, object], verify_report: Mapping[str, object]) -> dict:
    payload = {
        "schema_id": OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "baseline_id": "archive.offline.baseline.v0_0_0",
        "release_id": _token(build_report.get("release_id")) or DEFAULT_RELEASE_ID,
        "offline_archive_version": OFFLINE_ARCHIVE_VERSION,
        "stability_class": OFFLINE_ARCHIVE_STABILITY_CLASS,
        "archive_bundle_hash": _token(build_report.get("archive_bundle_hash")).lower(),
        "archive_record_hash": _token(build_report.get("archive_record_hash")).lower(),
        "archive_projection_hash": _token(build_report.get("archive_projection_hash")).lower(),
        "verification_result": _token(verify_report.get("result")),
        "verification_fingerprint": _token(verify_report.get("deterministic_fingerprint")).lower(),
        "required_update_tag": OFFLINE_ARCHIVE_REQUIRED_TAG,
        "required_subchecks": list(_SUBCHECK_IDS),
        "archive_bundle_rel": _token(build_report.get("archive_bundle_rel")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = offline_archive_baseline_hash(payload)
    return payload


def _extract_archive(archive_path: str, extract_root: str) -> str:
    _safe_rmtree(extract_root)
    _ensure_dir(extract_root)
    with tarfile.open(os.path.normpath(os.path.abspath(archive_path)), "r:gz") as handle:
        handle.extractall(extract_root)
    roots = sorted(name for name in os.listdir(extract_root) if os.path.isdir(os.path.join(extract_root, name)))
    if not roots:
        raise FileNotFoundError("archive extraction produced no root directory")
    return os.path.join(extract_root, roots[0])


def _verify_release_manifest_cas(extracted_root: str, release_manifest: Mapping[str, object], artifact_entries: Sequence[Mapping[str, object]]) -> dict:
    errors = []
    by_source = {
        (_token(_as_map(row).get("artifact_kind")), _token(_as_map(row).get("source_rel"))): _as_map(row)
        for row in artifact_entries
    }
    for row in _as_list(_as_map(release_manifest).get("artifacts")):
        item = _as_map(row)
        key = (_token(item.get("artifact_kind")), _token(item.get("artifact_name")))
        entry = _as_map(by_source.get(key))
        if not entry:
            errors.append({"code": "archive_artifact_missing", "message": "release artifact is missing from archive record", "path": _token(item.get("artifact_name"))})
            continue
        cas_rel = _token(entry.get("cas_rel"))
        cas_abs = os.path.join(extracted_root, cas_rel.replace("/", os.sep))
        if not os.path.exists(cas_abs):
            errors.append({"code": "archive_artifact_missing", "message": "release artifact CAS payload is missing from offline archive", "path": cas_rel})
            continue
        if _path_hash(cas_abs) != _token(entry.get("content_hash")).lower():
            errors.append({"code": "archive_artifact_hash_mismatch", "message": "release artifact CAS payload hash drifted inside offline archive", "path": cas_rel})
    return {"result": "complete" if not errors else "refused", "error_count": len(errors), "errors": errors}


def _verify_support_surface_presence(extracted_root: str, support_surfaces: Sequence[Mapping[str, object]]) -> list[dict]:
    errors = []
    for row in support_surfaces:
        item = _as_map(row)
        archive_rel = _token(item.get("archive_rel"))
        abs_path = os.path.join(extracted_root, archive_rel.replace("/", os.sep))
        if not os.path.exists(abs_path):
            errors.append({"code": "archive_support_surface_missing", "message": "required support surface is missing from the offline archive", "path": archive_rel})
            continue
        if _path_hash(abs_path) != _token(item.get("content_hash")).lower():
            errors.append({"code": "archive_support_surface_hash_mismatch", "message": "archived support surface hash drifted from archive record", "path": archive_rel})
    return errors


def _stable_subcheck_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(payload or {}))


def _verify_worldgen_subcheck(repo_root: str, extracted_root: str) -> dict:
    from tools.worldgen.worldgen_lock_common import verify_worldgen_lock

    seed_text = _read_text(os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "worldgen", "baseline_seed.txt")).strip()
    snapshot_path = os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "worldgen", "baseline_worldgen_snapshot.json")
    report = verify_worldgen_lock(repo_root, seed_text=seed_text, snapshot_path=snapshot_path)
    summary = {
        "result": "complete" if bool(report.get("matches_snapshot")) else "refused",
        "matches_snapshot": bool(report.get("matches_snapshot")),
        "mismatch_count": int(report.get("mismatch_count", 0) or 0),
        "baseline_seed": _token(report.get("baseline_seed")),
        "expected_snapshot_fingerprint": _token(report.get("expected_snapshot_fingerprint")),
        "observed_snapshot_fingerprint": _token(report.get("observed_snapshot_fingerprint")),
        "expected_refinement_stage_hashes": _as_map(report.get("expected_refinement_stage_hashes")),
        "observed_refinement_stage_hashes": _as_map(report.get("observed_refinement_stage_hashes")),
        "expected_sol_system_id": _token(report.get("expected_sol_system_id")),
        "observed_sol_system_id": _token(report.get("observed_sol_system_id")),
        "expected_earth_planet_id": _token(report.get("expected_earth_planet_id")),
        "observed_earth_planet_id": _token(report.get("observed_earth_planet_id")),
    }
    summary["fingerprint"] = _stable_subcheck_fingerprint(summary)
    return summary


def _verify_baseline_universe_subcheck(repo_root: str, extracted_root: str) -> dict:
    from tools.mvp.baseline_universe_common import verify_baseline_universe

    seed_text = _read_text(os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "worldgen", "baseline_seed.txt")).strip()
    snapshot_path = os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "universe", "baseline_universe_snapshot.json")
    save_path = os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "universe", "baseline_save_0.save")
    report = verify_baseline_universe(repo_root, seed_text=seed_text, snapshot_path=snapshot_path, save_path=save_path)
    summary = {
        "result": "complete" if bool(report.get("matches_snapshot")) and bool(report.get("save_reload_matches")) else "refused",
        "matches_snapshot": bool(report.get("matches_snapshot")),
        "save_reload_matches": bool(report.get("save_reload_matches")),
        "seed_matches_worldgen_lock": bool(report.get("seed_matches_worldgen_lock")),
        "pack_lock_matches_worldgen_lock": bool(report.get("pack_lock_matches_worldgen_lock")),
        "expected_snapshot_fingerprint": _token(report.get("expected_snapshot_fingerprint")),
        "observed_snapshot_fingerprint": _token(report.get("observed_snapshot_fingerprint")),
        "expected_save_rel": _token(report.get("expected_save_rel")),
        "loaded_save_hash": _token(report.get("loaded_save_hash")),
        "mismatch_count": len(_as_list(report.get("mismatched_fields"))),
        "loaded_save_error_count": len(_as_map(report.get("loaded_save_error"))),
    }
    summary["fingerprint"] = _stable_subcheck_fingerprint(summary)
    return summary


def _verify_gameplay_subcheck(repo_root: str, extracted_root: str) -> dict:
    from tools.mvp.gameplay_loop_common import verify_gameplay_loop

    seed_text = _read_text(os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "worldgen", "baseline_seed.txt")).strip()
    snapshot_path = os.path.join(extracted_root, ARCHIVE_BASELINES_DIR, "gameplay", "gameplay_loop_snapshot.json")
    report = verify_gameplay_loop(repo_root, seed_text=seed_text, snapshot_path=snapshot_path)
    return {
        "result": "complete" if _token(report.get("result")) == "complete" else "refused",
        "fingerprint": _token(report.get("deterministic_fingerprint")),
        "matches_snapshot": bool(report.get("matches_snapshot")),
        "save_reload_matches": bool(report.get("save_reload_matches")),
        "replay_matches_final_anchor": bool(report.get("replay_matches_final_anchor")),
    }


def _verify_disaster_subcheck(repo_root: str) -> dict:
    from tools.mvp.disaster_suite_common import run_disaster_suite

    report = run_disaster_suite(repo_root, output_root_rel=os.path.join("build", "tmp", "omega8_offline_archive_disaster_verify"), write_outputs=False)
    return {
        "result": "complete" if _token(report.get("result")) == "complete" else "refused",
        "fingerprint": _token(report.get("deterministic_fingerprint")),
        "case_count": int(report.get("case_count", 0) or 0),
        "matched_case_count": int(report.get("matched_case_count", 0) or 0),
        "mismatched_case_count": int(report.get("mismatched_case_count", 0) or 0),
    }


def verify_offline_archive(repo_root: str, *, archive_path: str, baseline_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    archive_abs = os.path.normpath(os.path.abspath(archive_path))
    baseline_abs = _repo_abs(repo_root_abs, baseline_path or OFFLINE_ARCHIVE_BASELINE_REL)
    extract_root = tempfile.mkdtemp(prefix="omega8_archive_verify_", dir=_repo_abs(repo_root_abs, DEFAULT_WORK_ROOT_REL))
    extracted_root = _extract_archive(archive_abs, extract_root)
    try:
        record = _load_json(os.path.join(extracted_root, ARCHIVE_RECORD_FILENAME))
        release_manifest = load_release_manifest(os.path.join(extracted_root, RELEASE_MANIFEST_SNAPSHOT_REL))
        release_index = load_release_index(os.path.join(extracted_root, RELEASE_INDEX_SNAPSHOT_REL))
        history_rel = _token(_as_map(record.get("extensions")).get("release_index_history_rel"))
        history_path = os.path.join(extracted_root, history_rel.replace("/", os.sep))
        support_surfaces = [_as_map(row) for row in _as_list(record.get("bundled_support_surfaces"))]
        artifact_entries = [_as_map(row) for row in _as_list(record.get("artifacts"))]

        errors = []
        if _token(record.get("schema_id")) != OFFLINE_ARCHIVE_RECORD_SCHEMA_ID:
            errors.append({"code": "archive_record_schema_id_mismatch", "message": "offline archive record schema_id mismatch", "path": ARCHIVE_RECORD_FILENAME})
        if _token(record.get("deterministic_fingerprint")) != offline_archive_record_hash(record):
            errors.append({"code": "archive_record_fingerprint_mismatch", "message": "offline archive record deterministic_fingerprint mismatch", "path": ARCHIVE_RECORD_FILENAME})

        archive_projection_hash = canonical_sha256({"files": _gather_member_rows(extracted_root, exclude_rel_paths=[ARCHIVE_RECORD_FILENAME])})
        if archive_projection_hash != _token(record.get("archive_projection_hash")).lower():
            errors.append({"code": "archive_projection_hash_mismatch", "message": "offline archive member projection hash drifted", "path": ARCHIVE_RECORD_FILENAME})

        manifest_check = _verify_release_manifest_cas(extracted_root, release_manifest, artifact_entries)
        if _token(manifest_check.get("result")) != "complete":
            errors.extend(list(manifest_check.get("errors") or []))

        support_errors = _verify_support_surface_presence(extracted_root, support_surfaces)
        errors.extend(support_errors)

        if not os.path.isfile(history_path):
            errors.append({"code": "release_index_history_missing", "message": "offline archive is missing retained release_index history", "path": history_rel})
        elif release_index_hash(load_release_index(history_path)) != release_index_hash(release_index):
            errors.append({"code": "release_index_history_hash_mismatch", "message": "retained release_index history drifted from current release index snapshot", "path": history_rel})

        trust_registry_hash = canonical_sha256(_load_json(os.path.join(extracted_root, "trust_root_registry.json")))
        if trust_registry_hash != _token(record.get("trust_root_registry_hash")).lower():
            errors.append({"code": "trust_registry_hash_mismatch", "message": "archived trust root registry hash drifted from archive record", "path": "trust_root_registry.json"})

        baseline_payload = _load_json(baseline_abs)
        archive_bundle_hash = _sha256_file(archive_abs)
        if baseline_payload:
            if _token(baseline_payload.get("archive_bundle_hash")).lower() != archive_bundle_hash:
                errors.append({"code": "archive_bundle_hash_mismatch", "message": "archive bundle hash drifted from committed regression baseline", "path": _relative_to(repo_root_abs, baseline_abs)})
            if _token(baseline_payload.get("archive_record_hash")).lower() != _token(record.get("deterministic_fingerprint")).lower():
                errors.append({"code": "archive_record_hash_mismatch", "message": "archive record hash drifted from committed regression baseline", "path": _relative_to(repo_root_abs, baseline_abs)})

        subchecks = {
            "release_manifest_hashes": {"result": "complete" if _token(manifest_check.get("result")) == "complete" else "refused", "error_count": int(manifest_check.get("error_count", 0) or 0)},
            "release_index_history_integrity": {"result": "complete" if os.path.isfile(history_path) and not any(_token(err.get("code")) == "release_index_history_hash_mismatch" for err in errors) else "refused", "history_rel": history_rel},
            "artifact_cas_hashes": {"result": "complete" if _token(manifest_check.get("result")) == "complete" and not support_errors else "refused", "artifact_count": len(artifact_entries), "support_surface_count": len(support_surfaces)},
            "trust_registry_match": {"result": "complete" if not any(_token(err.get("code")) == "trust_registry_hash_mismatch" for err in errors) else "refused", "trust_root_registry_hash": trust_registry_hash},
            "worldgen_lock_verify": _verify_worldgen_subcheck(repo_root_abs, extracted_root),
            "baseline_universe_verify": _verify_baseline_universe_subcheck(repo_root_abs, extracted_root),
            "gameplay_loop_verify": _verify_gameplay_subcheck(repo_root_abs, extracted_root),
            "disaster_suite_verify": _verify_disaster_subcheck(repo_root_abs),
        }
        for check_id in ("worldgen_lock_verify", "baseline_universe_verify", "gameplay_loop_verify", "disaster_suite_verify"):
            if _token(_as_map(subchecks.get(check_id)).get("result")) != "complete":
                errors.append({"code": "{}_failed".format(check_id), "message": "offline archive verification subcheck '{}' failed".format(check_id), "path": ARCHIVE_RECORD_FILENAME})

        report = {
            "schema_id": OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID,
            "schema_version": "1.0.0",
            "result": "complete" if not errors else "refused",
            "release_id": _token(record.get("release_id")) or DEFAULT_RELEASE_ID,
            "archive_bundle_hash": archive_bundle_hash,
            "archive_record_hash": _token(record.get("deterministic_fingerprint")).lower(),
            "archive_projection_hash": archive_projection_hash,
            "archive_path": _norm(archive_abs),
            "baseline_path": _relative_to(repo_root_abs, baseline_abs),
            "subchecks": subchecks,
            "errors": errors,
            "deterministic_fingerprint": "",
        }
        report["deterministic_fingerprint"] = offline_archive_verify_hash(report)
        return report
    finally:
        shutil.rmtree(extract_root, ignore_errors=True)


def write_offline_archive_verify_outputs(repo_root: str, report: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    json_target = _repo_abs(repo_root_abs, json_path or OFFLINE_ARCHIVE_VERIFY_JSON_REL)
    doc_target = _repo_abs(repo_root_abs, doc_path or OFFLINE_ARCHIVE_VERIFY_DOC_REL)
    _write_canonical_json(json_target, report)
    _write_text(doc_target, _render_verify_doc(report))
    return {"json_path": json_target, "doc_path": doc_target}


def write_offline_archive_baseline_outputs(repo_root: str, baseline: Mapping[str, object], *, baseline_path: str = "", doc_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    baseline_target = _repo_abs(repo_root_abs, baseline_path or OFFLINE_ARCHIVE_BASELINE_REL)
    doc_target = _repo_abs(repo_root_abs, doc_path or OFFLINE_ARCHIVE_BASELINE_DOC_REL)
    _write_canonical_json(baseline_target, baseline)
    _write_text(doc_target, _render_baseline_doc(baseline) + "\n")
    return {"baseline_path": baseline_target, "doc_path": doc_target}


def load_offline_archive_verify(repo_root: str, path: str = "") -> dict:
    return _load_json(_repo_abs(repo_root, path or OFFLINE_ARCHIVE_VERIFY_JSON_REL))


def load_offline_archive_baseline(repo_root: str, path: str = "") -> dict:
    return _load_json(_repo_abs(repo_root, path or OFFLINE_ARCHIVE_BASELINE_REL))


__all__ = [
    "ARCHIVE_RECORD_FILENAME",
    "DEFAULT_DIST_ROOT_REL",
    "DEFAULT_OUTPUT_ROOT_REL",
    "DEFAULT_PLATFORM_TAG",
    "DEFAULT_RELEASE_ID",
    "OFFLINE_ARCHIVE_BASELINE_DOC_REL",
    "OFFLINE_ARCHIVE_BASELINE_REL",
    "OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID",
    "OFFLINE_ARCHIVE_BUILD_TOOL_PY_REL",
    "OFFLINE_ARCHIVE_BUILD_TOOL_REL",
    "OFFLINE_ARCHIVE_MODEL_DOC_REL",
    "OFFLINE_ARCHIVE_RECORD_SCHEMA_ID",
    "OFFLINE_ARCHIVE_REQUIRED_TAG",
    "OFFLINE_ARCHIVE_RETRO_AUDIT_REL",
    "OFFLINE_ARCHIVE_VERIFY_DOC_REL",
    "OFFLINE_ARCHIVE_VERIFY_JSON_REL",
    "OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID",
    "OFFLINE_ARCHIVE_VERIFY_TOOL_PY_REL",
    "OFFLINE_ARCHIVE_VERIFY_TOOL_REL",
    "OFFLINE_ARCHIVE_VERSION",
    "build_archive_baseline",
    "build_offline_archive",
    "load_offline_archive_baseline",
    "load_offline_archive_verify",
    "offline_archive_baseline_hash",
    "offline_archive_record_hash",
    "offline_archive_verify_hash",
    "verify_offline_archive",
    "write_offline_archive_baseline_outputs",
    "write_offline_archive_verify_outputs",
]
