"""Deterministic STORE-GC-0 helpers."""

from __future__ import annotations

import os
import shutil
from typing import Mapping, Sequence

from lib.bundle.bundle_manifest import build_bundle_manifest, write_json as write_bundle_json
from lib.install.install_validator import (
    build_install_registry_entry,
    deterministic_fingerprint as install_deterministic_fingerprint,
    normalize_install_manifest,
    save_install_registry,
    write_json as write_install_json,
)
from lib.instance.instance_validator import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    write_json as write_instance_json,
)
from lib.save.save_validator import (
    deterministic_fingerprint as save_deterministic_fingerprint,
    write_json as write_save_json,
)
from lib.store import (
    DEFAULT_GC_POLICY_ID,
    GC_MODE_AGGRESSIVE,
    GC_MODE_NONE,
    GC_MODE_SAFE,
    REFUSAL_GC_EXPLICIT_FLAG,
    build_store_reachability_report,
    canonicalize_gc_policy,
    load_gc_policy_registry,
    run_store_gc,
    verify_store_root,
)
from tools.lib.content_store import (
    build_pack_lock_payload,
    build_profile_bundle_payload,
    initialize_store_root,
    pretty_write_json,
    sha256_file,
    store_add_artifact,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "STORE_GC0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "lib", "STORE_INTEGRITY_AND_GC.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "STORE_GC_BASELINE.md")
VERIFY_REPORT_DOC_REL = os.path.join("docs", "audit", "STORE_VERIFY_REPORT.md")
VERIFY_REPORT_JSON_REL = os.path.join("data", "audit", "store_verify_report.json")
GC_REPORT_JSON_REL = os.path.join("data", "audit", "store_gc_report.json")
GC_POLICY_REGISTRY_REL = os.path.join("data", "registries", "gc_policy_registry.json")
RULE_GRAPH = "INV-GC-USES-REACHABILITY-GRAPH"
RULE_DETERMINISTIC = "INV-GC-DETERMINISTIC"
RULE_POLICY = "INV-NO-DELETE-WITHOUT-POLICY"
LAST_REVIEWED = "2026-03-14"
FIXTURE_ROOT_REL = os.path.join("build", "tmp", "store_gc_fixture")


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_text(repo_root: str, rel_path: str) -> str:
    try:
        with open(os.path.join(_norm(repo_root), rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _stability_payload(
    *,
    stability_class_id: str,
    rationale: str,
    future_series: str,
    replacement_target: str,
    contract_id: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": _token(stability_class_id) or "provisional",
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": _token(contract_id),
        "deterministic_fingerprint": "",
        "extensions": {"id_stability": "stable"},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _gc_policy_row(*, gc_policy_id: str, mode: str, quarantine_enabled: bool, summary: str) -> dict:
    row = canonicalize_gc_policy(
        {
            "gc_policy_id": _token(gc_policy_id),
            "mode": _token(mode),
            "quarantine_enabled": bool(quarantine_enabled),
            "deterministic_fingerprint": "",
            "extensions": {
                "id_stability": "stable",
                "summary": _token(summary),
            },
        }
    )
    row["schema_version"] = "1.0.0"
    row["stability"] = _stability_payload(
        stability_class_id="provisional",
        rationale="GC policy IDs are frozen for v0.0.0-mock; policy contents remain provisional while shared-store operations stay mock-only.",
        future_series="STORE-GC",
        replacement_target="Release-pinned store lifecycle policy bundles after shared install/store transactions are hardened.",
    )
    return row


def build_gc_policy_registry() -> dict:
    rows = [
        _gc_policy_row(
            gc_policy_id="gc.aggressive",
            mode=GC_MODE_AGGRESSIVE,
            quarantine_enabled=False,
            summary="Delete only unreachable artifacts immediately; requires an explicit flag and deterministic reachability proof.",
        ),
        _gc_policy_row(
            gc_policy_id="gc.none",
            mode=GC_MODE_NONE,
            quarantine_enabled=False,
            summary="Default mock policy; compute integrity and reachability but do not mutate the store.",
        ),
        _gc_policy_row(
            gc_policy_id="gc.safe",
            mode=GC_MODE_SAFE,
            quarantine_enabled=True,
            summary="Move only unreachable artifacts into quarantine using deterministic paths for rollback and inspection.",
        ),
    ]
    return {
        "schema_id": "dominium.registry.gc_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.gc_policy_registry",
            "registry_version": "1.0.0",
            "gc_policies": sorted(rows, key=lambda row: _token(row.get("gc_policy_id"))),
            "extensions": {"official.source": "STORE-GC0-2"},
        },
    }


def write_gc_policy_registry(repo_root: str) -> str:
    root = _norm(repo_root)
    return _write_json(os.path.join(root, GC_POLICY_REGISTRY_REL), build_gc_policy_registry())


def _simple_artifact_payload(*, artifact_kind_id: str, artifact_id: str, version: str, extra: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "artifact_kind_id": _token(artifact_kind_id),
        "artifact_id": _token(artifact_id),
        "version": _token(version) or "1.0.0",
        "deterministic_fingerprint": "",
        "extensions": dict(_as_map(extra)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _store_path_rel(from_root: str, to_path: str) -> str:
    try:
        rel_path = os.path.relpath(_norm(to_path), _norm(from_root))
    except ValueError:
        rel_path = os.path.basename(_norm(to_path))
    return _norm_rel(rel_path)


def build_store_gc_fixture(repo_root: str, *, fixture_root: str = "") -> dict:
    root = _norm(repo_root)
    fixture = _norm(fixture_root or os.path.join(root, FIXTURE_ROOT_REL))
    if os.path.isdir(fixture):
        shutil.rmtree(fixture, ignore_errors=True)
    os.makedirs(fixture, exist_ok=True)

    store_root = os.path.join(fixture, "shared_store")
    install_root = os.path.join(fixture, "install.shared")
    registry_path = os.path.join(fixture, "install_registry.json")
    manifests_root = os.path.join(install_root, "manifests")
    instance_root = os.path.join(install_root, "instances", "default")
    save_root = os.path.join(install_root, "saves", "save.default")
    bundle_root = os.path.join(install_root, "bundles", "pinned")
    semantic_contract_registry_hash = canonical_sha256({"fixture": "store-gc.semantic_contract_registry"})

    initialize_store_root(store_root)
    for rel_path in ("bin", "manifests", "instances/default", "saves/save.default", "bundles/pinned/content", "docs"):
        os.makedirs(os.path.join(install_root, rel_path.replace("/", os.sep)), exist_ok=True)

    pack_row = store_add_artifact(
        store_root,
        "packs",
        _simple_artifact_payload(
            artifact_kind_id="artifact.pack",
            artifact_id="pack.base.procedural",
            version="1.0.0",
        ),
    )
    orphan_pack_row = store_add_artifact(
        store_root,
        "packs",
        _simple_artifact_payload(
            artifact_kind_id="artifact.pack",
            artifact_id="pack.orphan.debug",
            version="1.0.0",
        ),
    )
    repro_row = store_add_artifact(
        store_root,
        "repro",
        _simple_artifact_payload(
            artifact_kind_id="artifact.repro_bundle",
            artifact_id="repro.fixture.bundle",
            version="1.0.0",
        ),
    )

    lock_payload, lock_hash = build_pack_lock_payload(
        instance_id="instance.default",
        pack_ids=["pack.base.procedural"],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
        source_payload={
            "pack_hashes": {"pack.base.procedural": _token(pack_row.get("artifact_hash"))},
            "pack_compat_hashes": {},
        },
    )
    lock_row = store_add_artifact(store_root, "locks", lock_payload, expected_hash=lock_hash)
    profile_payload, profile_hash = build_profile_bundle_payload(
        instance_id="instance.default",
        profile_ids=["profile.mvp.default"],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
    )
    profile_row = store_add_artifact(store_root, "profiles", profile_payload, expected_hash=profile_hash)

    install_manifest = {
        "install_id": "install.store_gc_fixture",
        "install_version": "0.0.0",
        "product_builds": {},
        "semantic_contract_registry_hash": semantic_contract_registry_hash,
        "supported_protocol_versions": {},
        "supported_contract_ranges": {},
        "default_mod_policy_id": "mod.policy.default",
        "store_root_ref": {
            "store_id": "store.default",
            "root_path": _store_path_rel(install_root, store_root),
            "manifest_ref": _store_path_rel(install_root, os.path.join(store_root, "store.root.json")),
        },
        "mode": "linked",
        "extensions": {
            "official.semantic_contract_registry_ref": "semantic_contract_registry.json",
            "official.selected_component_descriptors": [
                {
                    "component_id": "lock.pack_lock.mvp_default",
                    "component_kind": "component.lock",
                    "content_hash": _token(lock_row.get("artifact_hash")),
                    "extensions": {
                        "managed_paths": [
                            _store_path_rel(install_root, os.path.join(store_root, "store", "locks", _token(lock_row.get("artifact_hash")), "payload.json"))
                        ]
                    },
                },
                {
                    "component_id": "profile.bundle.mvp_default",
                    "component_kind": "component.profile",
                    "content_hash": _token(profile_row.get("artifact_hash")),
                    "extensions": {
                        "managed_paths": [
                            _store_path_rel(install_root, os.path.join(store_root, "store", "profiles", _token(profile_row.get("artifact_hash")), "payload.json"))
                        ]
                    },
                },
            ]
        },
        "deterministic_fingerprint": "",
    }
    install_manifest = normalize_install_manifest(install_manifest)
    install_manifest["deterministic_fingerprint"] = install_deterministic_fingerprint(install_manifest)
    install_manifest_path = write_install_json(os.path.join(install_root, "install.manifest.json"), install_manifest)
    _write_json(
        os.path.join(install_root, "semantic_contract_registry.json"),
        {"fixture": "store-gc.semantic_contract_registry"},
    )

    instance_manifest = {
        "instance_id": "instance.default",
        "install_ref": {
            "install_id": str(install_manifest.get("install_id", "")).strip(),
            "manifest_ref": "install.manifest.json",
            "root_path": ".",
        },
        "mode": "linked",
        "instance_kind": "instance.client",
        "pack_lock_hash": _token(lock_row.get("artifact_hash")),
        "profile_bundle_hash": _token(profile_row.get("artifact_hash")),
        "embedded_artifacts": [],
        "save_refs": ["../../saves/save.default/save.manifest.json"],
        "required_product_builds": {},
        "required_contract_ranges": {},
        "settings": {
            "renderer_mode": "",
            "ui_mode_default": "cli",
            "allow_read_only_fallback": False,
            "tick_budget_policy_id": "tick.budget.default",
            "compute_profile_id": "compute.profile.default",
            "data_root": ".",
            "active_profiles": [],
            "active_modpacks": [],
        },
        "provides_resolutions": [],
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    instance_manifest["deterministic_fingerprint"] = instance_deterministic_fingerprint(instance_manifest)
    write_instance_json(os.path.join(instance_root, "instance.manifest.json"), instance_manifest)

    save_manifest = {
        "save_id": "save.default",
        "save_format_version": "1.0.0",
        "universe_identity_hash": canonical_sha256({"fixture": "store-gc.universe"}),
        "universe_contract_bundle_hash": canonical_sha256({"fixture": "store-gc.contract_bundle"}),
        "generator_version_id": "build.fixture",
        "realism_profile_id": "realism.default",
        "pack_lock_hash": _token(lock_row.get("artifact_hash")),
        "overlay_manifest_hash": canonical_sha256({"fixture": "store-gc.overlay"}),
        "mod_policy_id": "mod.policy.default",
        "created_by_build_id": "build.fixture",
        "migration_chain": [],
        "allow_read_only_open": False,
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    save_manifest["deterministic_fingerprint"] = save_deterministic_fingerprint(save_manifest)
    write_save_json(os.path.join(save_root, "save.manifest.json"), save_manifest)

    release_manifest = {
        "release_id": "release.v0.0.0-mock-store_gc_fixture",
        "platform_tag": "platform.portable",
        "manifest_version": "1.0.0",
        "semantic_contract_registry_hash": semantic_contract_registry_hash,
        "artifacts": [
            {
                "artifact_kind": "lock",
                "artifact_name": _store_path_rel(install_root, os.path.join(store_root, "store", "locks", _token(lock_row.get("artifact_hash")), "payload.json")),
                "content_hash": _token(lock_row.get("artifact_hash")),
                "deterministic_fingerprint": canonical_sha256({"kind": "lock", "hash": _token(lock_row.get("artifact_hash"))}),
                "extensions": {},
            },
            {
                "artifact_kind": "profile",
                "artifact_name": _store_path_rel(install_root, os.path.join(store_root, "store", "profiles", _token(profile_row.get("artifact_hash")), "payload.json")),
                "content_hash": _token(profile_row.get("artifact_hash")),
                "deterministic_fingerprint": canonical_sha256({"kind": "profile", "hash": _token(profile_row.get("artifact_hash"))}),
                "extensions": {},
            },
        ],
        "manifest_hash": "",
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    release_manifest["manifest_hash"] = canonical_sha256(dict(release_manifest, manifest_hash="", deterministic_fingerprint=""))
    release_manifest["deterministic_fingerprint"] = canonical_sha256(dict(release_manifest, deterministic_fingerprint=""))
    pretty_write_json(os.path.join(manifests_root, "release_manifest.json"), release_manifest)

    release_index = {
        "channel": "mock",
        "release_series": "0.x",
        "semantic_contract_registry_hash": semantic_contract_registry_hash,
        "supported_protocol_ranges": {},
        "platform_matrix": [],
        "component_graph_hash": canonical_sha256({"fixture": "store-gc.component_graph"}),
        "components": [
            {
                "component_id": "lock.pack_lock.mvp_default",
                "component_kind": "lock",
                "content_hash": _token(lock_row.get("artifact_hash")),
                "extensions": {
                    "managed_paths": [
                        _store_path_rel(install_root, os.path.join(store_root, "store", "locks", _token(lock_row.get("artifact_hash")), "payload.json"))
                    ]
                },
            },
            {
                "component_id": "profile.bundle.mvp_default",
                "component_kind": "profile",
                "content_hash": _token(profile_row.get("artifact_hash")),
                "extensions": {
                    "managed_paths": [
                        _store_path_rel(install_root, os.path.join(store_root, "store", "profiles", _token(profile_row.get("artifact_hash")), "payload.json"))
                    ]
                },
            },
        ],
        "signatures": [],
        "deterministic_fingerprint": "",
        "extensions": {"release_id": str(release_manifest.get("release_id", "")).strip()},
    }
    release_index["deterministic_fingerprint"] = canonical_sha256(dict(release_index, deterministic_fingerprint=""))
    pretty_write_json(os.path.join(manifests_root, "release_index.json"), release_index)

    bundle_content_rel = os.path.join("store", "repro", _token(repro_row.get("artifact_hash")), "payload.json")
    bundle_content_path = os.path.join(bundle_root, "content", bundle_content_rel)
    os.makedirs(os.path.dirname(bundle_content_path), exist_ok=True)
    shutil.copyfile(
        os.path.join(store_root, "store", "repro", _token(repro_row.get("artifact_hash")), "payload.json"),
        bundle_content_path,
    )
    bundle_manifest = build_bundle_manifest(
        bundle_kind="bundle.instance.portable",
        created_by_build_id="build.fixture",
        contract_registry_hash=semantic_contract_registry_hash,
        included_artifacts=[
            {
                "relative_path": _norm_rel(bundle_content_rel),
                "item_kind": "artifact.repro_bundle",
                "item_id_or_hash": _token(repro_row.get("artifact_hash")),
                "content_hash": sha256_file(bundle_content_path),
                "extensions": {},
            }
        ],
        bundle_id="bundle.pinned.fixture",
    )
    write_bundle_json(os.path.join(bundle_root, "bundle.manifest.json"), bundle_manifest)

    save_install_registry(
        registry_path,
        {
            "record": {
                "installs": [
                    build_install_registry_entry(
                        registry_path=registry_path,
                        install_manifest_path=install_manifest_path,
                        install_manifest=install_manifest,
                    )
                ]
            }
        },
    )

    return {
        "fixture_root": fixture,
        "store_root": _norm(store_root),
        "install_root": _norm(install_root),
        "registry_path": _norm(registry_path),
        "reachable_pack_hash": _token(pack_row.get("artifact_hash")),
        "orphan_pack_hash": _token(orphan_pack_row.get("artifact_hash")),
        "lock_hash": _token(lock_row.get("artifact_hash")),
        "profile_hash": _token(profile_row.get("artifact_hash")),
        "repro_hash": _token(repro_row.get("artifact_hash")),
    }


def build_store_verify_report(
    repo_root: str,
    *,
    store_root: str = "",
    install_roots: Sequence[str] | None = None,
    registry_path: str = "",
) -> dict:
    root = _norm(repo_root)
    if not _token(store_root):
        fixture = build_store_gc_fixture(root)
        store_root = str(fixture.get("store_root", "")).strip()
        install_roots = [str(fixture.get("install_root", "")).strip()]
        registry_path = str(fixture.get("registry_path", "")).strip()
    verify_report = verify_store_root(store_root)
    reachability_report = build_store_reachability_report(
        store_root,
        repo_root=root,
        install_roots=install_roots,
        registry_path=registry_path,
    )
    report = {
        "report_id": "store.verify.summary.v1",
        "result": _token(verify_report.get("result")) or "refused",
        "store_verify_report": verify_report,
        "reachability_source_count": int(len(_as_list(reachability_report.get("reachability_sources")))),
        "reachability_fingerprint": _token(reachability_report.get("deterministic_fingerprint")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_store_gc_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    write_gc_policy_registry(root)
    base_fixture = build_store_gc_fixture(root, fixture_root=os.path.join(root, FIXTURE_ROOT_REL, "baseline"))
    verify_summary = build_store_verify_report(
        root,
        store_root=str(base_fixture.get("store_root", "")).strip(),
        install_roots=[str(base_fixture.get("install_root", "")).strip()],
        registry_path=str(base_fixture.get("registry_path", "")).strip(),
    )
    none_result = run_store_gc(
        str(base_fixture.get("store_root", "")).strip(),
        repo_root=root,
        gc_policy_id=DEFAULT_GC_POLICY_ID,
        install_roots=[str(base_fixture.get("install_root", "")).strip()],
        registry_path=str(base_fixture.get("registry_path", "")).strip(),
    )
    safe_fixture = build_store_gc_fixture(root, fixture_root=os.path.join(root, FIXTURE_ROOT_REL, "safe"))
    safe_result = run_store_gc(
        str(safe_fixture.get("store_root", "")).strip(),
        repo_root=root,
        gc_policy_id="gc.safe",
        install_roots=[str(safe_fixture.get("install_root", "")).strip()],
        registry_path=str(safe_fixture.get("registry_path", "")).strip(),
    )
    aggressive_fixture = build_store_gc_fixture(root, fixture_root=os.path.join(root, FIXTURE_ROOT_REL, "aggressive"))
    aggressive_refusal = run_store_gc(
        str(aggressive_fixture.get("store_root", "")).strip(),
        repo_root=root,
        gc_policy_id="gc.aggressive",
        install_roots=[str(aggressive_fixture.get("install_root", "")).strip()],
        registry_path=str(aggressive_fixture.get("registry_path", "")).strip(),
        allow_aggressive=False,
    )
    policy_registry = load_gc_policy_registry(root)
    policy_rows = list(_as_map(_as_map(policy_registry).get("record")).get("gc_policies") or [])
    violations: list[dict] = []

    if _token(verify_summary.get("result")) != "complete":
        violations.append(
            {
                "rule_id": RULE_DETERMINISTIC,
                "code": "store_verify_failed",
                "message": "store verification must pass before GC can run",
                "file_path": VERIFY_REPORT_JSON_REL,
            }
        )
    if _token(none_result.get("result")) != "complete":
        violations.append(
            {
                "rule_id": RULE_DETERMINISTIC,
                "code": "gc_none_failed",
                "message": "gc.none must compute a deterministic report without mutating the store",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    if list(_as_map(_as_map(none_result).get("gc_report")).get("deleted_hashes") or []) or list(_as_map(_as_map(none_result).get("gc_report")).get("quarantined_hashes") or []):
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "gc_none_mutated",
                "message": "gc.none must report only and may not delete or quarantine artifacts",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    if _token(safe_result.get("result")) != "complete":
        violations.append(
            {
                "rule_id": RULE_GRAPH,
                "code": "gc_safe_failed",
                "message": "gc.safe must succeed when unreachable artifacts are present",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    if not list(_as_map(_as_map(safe_result).get("gc_report")).get("quarantined_hashes") or []):
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "gc_safe_no_quarantine",
                "message": "gc.safe must move unreachable artifacts into quarantine",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    if list(_as_map(_as_map(safe_result).get("gc_report")).get("deleted_hashes") or []):
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "gc_safe_deleted",
                "message": "gc.safe must not delete artifacts directly",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    if _token(aggressive_refusal.get("refusal_code")) != REFUSAL_GC_EXPLICIT_FLAG:
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "gc_aggressive_guard_missing",
                "message": "gc.aggressive must refuse without an explicit destructive flag",
                "file_path": "lib/store/gc_engine.py",
            }
        )
    gc_engine_text = _read_text(root, "lib/store/gc_engine.py")
    if "build_store_reachability_report(" not in gc_engine_text:
        violations.append(
            {
                "rule_id": RULE_GRAPH,
                "code": "gc_reachability_hook_missing",
                "message": "GC engine must route candidate selection through the reachability graph",
                "file_path": "lib/store/gc_engine.py",
            }
        )

    report = {
        "report_id": "lib.store_gc.v1",
        "result": "complete" if not violations else "refused",
        "policy_ids": sorted(_token(_as_map(row).get("gc_policy_id")) for row in policy_rows if _token(_as_map(row).get("gc_policy_id"))),
        "gc_policy_registry_hash": canonical_sha256(policy_registry) if policy_registry else "",
        "store_verify_fingerprint": _token(_as_map(verify_summary.get("store_verify_report")).get("deterministic_fingerprint")),
        "reachability_fingerprint": _token(_as_map(_as_map(none_result).get("reachability_report")).get("deterministic_fingerprint")),
        "gc_none_fingerprint": _token(_as_map(_as_map(none_result).get("gc_report")).get("deterministic_fingerprint")),
        "gc_safe_fingerprint": _token(_as_map(_as_map(safe_result).get("gc_report")).get("deterministic_fingerprint")),
        "aggressive_refusal_code": _token(aggressive_refusal.get("refusal_code")),
        "reachable_hashes": list(_as_map(_as_map(none_result).get("gc_report")).get("reachable_hashes") or []),
        "candidate_hashes": list(_as_map(_as_map(_as_map(none_result).get("gc_report")).get("extensions")).get("candidate_hashes") or []),
        "quarantined_hashes": list(_as_map(_as_map(safe_result).get("gc_report")).get("quarantined_hashes") or []),
        "reachability_sources": list(_as_map(_as_map(none_result).get("reachability_report")).get("reachability_sources") or []),
        "violations": sorted(
            [dict(row or {}) for row in violations],
            key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_store_verify_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    verify_report = _as_map(payload.get("store_verify_report"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: STORE-GC",
        "Replacement Target: release-pinned store lifecycle bundles after shared-store transactions and rollback policies are hardened.",
        "",
        "# Store Verify Report",
        "",
        "- result: `{}`".format(_token(verify_report.get("result"))),
        "- store_id: `{}`".format(_token(verify_report.get("store_id"))),
        "- artifact_count: `{}`".format(int(verify_report.get("artifact_count", 0) or 0)),
        "- verified_hash_count: `{}`".format(int(len(_as_list(verify_report.get("verified_hashes"))))),
        "- quarantined_hash_count: `{}`".format(int(len(_as_list(verify_report.get("quarantined_hashes"))))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Errors",
        "",
    ]
    errors = list(verify_report.get("errors") or [])
    if not errors:
        lines.append("- none")
    else:
        for row in errors:
            item = _as_map(row)
            lines.append("- `{}` at `{}`: {}".format(_token(item.get("code")), _token(item.get("path")), _token(item.get("message"))))
    return "\n".join(lines).rstrip() + "\n"


def render_store_gc_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: STORE-GC",
        "Replacement Target: release-pinned store lifecycle bundles and transaction-backed shared-store cleanup after v0.0.0-mock.",
        "",
        "# Store GC Baseline",
        "",
        "## Policy Definitions",
        "",
    ]
    for policy_id in list(payload.get("policy_ids") or []):
        lines.append("- `{}`".format(_token(policy_id)))
    lines.extend(["", "## Reachability Sources", ""])
    for row in list(payload.get("reachability_sources") or []):
        item = _as_map(row)
        lines.append(
            "- `{}` `{}` -> {}".format(
                _token(item.get("source_kind")),
                _token(item.get("source_id")),
                ", ".join(_as_list(item.get("artifact_tokens"))) or "(none)",
            )
        )
    lines.extend(
        [
            "",
            "## Quarantine Behavior",
            "",
            "- `gc.none` is report-only and does not mutate the store.",
            "- `gc.safe` moves only unreachable artifacts into `store/quarantine/<category>/<hash>`.",
            "- `gc.aggressive` deletes unreachable artifacts only when `--allow-aggressive` is supplied.",
            "- Portable bundle stores refuse GC unless explicitly overridden with `--allow-portable-store`.",
            "",
            "## Readiness",
            "",
            "- DIST-7 packaging artifacts can include store health checks through `tool_store_verify` and `setup store gc --policy gc.none`.",
            "- Shared installs remain protected by deterministic reachability traversal and quarantine-first cleanup in safe mode.",
            "",
            "## Deterministic Outputs",
            "",
            "- store_verify_fingerprint: `{}`".format(_token(payload.get("store_verify_fingerprint"))),
            "- reachability_fingerprint: `{}`".format(_token(payload.get("reachability_fingerprint"))),
            "- gc_none_fingerprint: `{}`".format(_token(payload.get("gc_none_fingerprint"))),
            "- gc_safe_fingerprint: `{}`".format(_token(payload.get("gc_safe_fingerprint"))),
            "- aggressive_refusal_code: `{}`".format(_token(payload.get("aggressive_refusal_code"))),
        ]
    )
    if _as_list(payload.get("violations")):
        lines.extend(["", "## Open Violations", ""])
        for row in _as_list(payload.get("violations")):
            item = _as_map(row)
            lines.append("- `{}`: {}".format(_token(item.get("code")), _token(item.get("message"))))
    return "\n".join(lines).rstrip() + "\n"


def write_store_verify_outputs(
    repo_root: str,
    *,
    store_root: str = "",
    install_roots: Sequence[str] | None = None,
    registry_path: str = "",
) -> dict:
    root = _norm(repo_root)
    report = build_store_verify_report(
        root,
        store_root=store_root,
        install_roots=install_roots,
        registry_path=registry_path,
    )
    doc_path = _write_text(os.path.join(root, VERIFY_REPORT_DOC_REL), render_store_verify_report(report))
    json_path = _write_json(os.path.join(root, VERIFY_REPORT_JSON_REL), report)
    return {
        "report": report,
        "report_doc_path": _norm_rel(os.path.relpath(doc_path, root)),
        "report_json_path": _norm_rel(os.path.relpath(json_path, root)),
    }


def write_store_gc_outputs(repo_root: str) -> dict:
    root = _norm(repo_root)
    write_gc_policy_registry(root)
    report = build_store_gc_report(root)
    verify_outputs = write_store_verify_outputs(root)
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_store_gc_baseline(report))
    report_json_path = _write_json(os.path.join(root, GC_REPORT_JSON_REL), report)
    return {
        "report": report,
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
        "store_verify_doc_path": _token(verify_outputs.get("report_doc_path")),
        "store_verify_json_path": _token(verify_outputs.get("report_json_path")),
        "registry_path": _norm_rel(GC_POLICY_REGISTRY_REL),
    }


def store_gc_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "store GC retro audit is required", RULE_GRAPH),
        (DOCTRINE_DOC_REL, "store integrity and GC doctrine is required", RULE_GRAPH),
        ("schema/lib/gc_policy.schema", "gc_policy schema is required", RULE_POLICY),
        ("schema/lib/gc_report.schema", "gc_report schema is required", RULE_POLICY),
        ("schemas/gc_policy.schema.json", "compiled gc_policy schema is required", RULE_POLICY),
        ("schemas/gc_report.schema.json", "compiled gc_report schema is required", RULE_POLICY),
        (GC_POLICY_REGISTRY_REL, "gc policy registry is required", RULE_POLICY),
        ("lib/store/reachability_engine.py", "reachability engine is required", RULE_GRAPH),
        ("lib/store/gc_engine.py", "gc engine is required", RULE_GRAPH),
        ("tools/lib/store_gc_common.py", "STORE-GC helper is required", RULE_DETERMINISTIC),
        ("tools/lib/tool_store_verify.py", "store verification tool is required", RULE_DETERMINISTIC),
        ("tools/lib/tool_run_store_gc.py", "STORE-GC runner is required", RULE_DETERMINISTIC),
        (VERIFY_REPORT_DOC_REL, "store verification report is required", RULE_DETERMINISTIC),
        (VERIFY_REPORT_JSON_REL, "store verification machine report is required", RULE_DETERMINISTIC),
        (BASELINE_DOC_REL, "STORE-GC baseline is required", RULE_DETERMINISTIC),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"rule_id": rule_id, "code": "missing_required_file", "message": message, "file_path": rel_path})

    doctrine_text = _read_text(root, DOCTRINE_DOC_REL).lower()
    for token, message, rule_id in (
        ("# store integrity and gc", "STORE-GC doctrine must declare the canonical title", RULE_GRAPH),
        ("## store integrity checks", "STORE-GC doctrine must define integrity checks", RULE_GRAPH),
        ("## reference graph", "STORE-GC doctrine must define reachability sources", RULE_GRAPH),
        ("## gc policies", "STORE-GC doctrine must define GC policies", RULE_POLICY),
        ("## determinism", "STORE-GC doctrine must define deterministic traversal and deletion ordering", RULE_DETERMINISTIC),
        ("## portable bundles", "STORE-GC doctrine must define portable bundle restrictions", RULE_POLICY),
    ):
        if token in doctrine_text:
            continue
        violations.append({"rule_id": rule_id, "code": "missing_doctrine_section", "message": message, "file_path": DOCTRINE_DOC_REL})

    setup_text = _read_text(root, "tools/setup/setup_cli.py")
    if "handle_store(" not in setup_text or "\"store\"" not in setup_text:
        violations.append(
            {"rule_id": RULE_POLICY, "code": "setup_store_gc_missing", "message": "setup CLI must expose `setup store gc`", "file_path": "tools/setup/setup_cli.py"}
        )

    violations.extend(list(build_store_gc_report(root).get("violations") or []))
    return sorted(
        [dict(row or {}) for row in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "FIXTURE_ROOT_REL",
    "GC_POLICY_REGISTRY_REL",
    "GC_REPORT_JSON_REL",
    "LAST_REVIEWED",
    "RETRO_AUDIT_DOC_REL",
    "RULE_DETERMINISTIC",
    "RULE_GRAPH",
    "RULE_POLICY",
    "VERIFY_REPORT_DOC_REL",
    "VERIFY_REPORT_JSON_REL",
    "build_gc_policy_registry",
    "build_store_gc_fixture",
    "build_store_gc_report",
    "build_store_verify_report",
    "render_store_gc_baseline",
    "render_store_verify_report",
    "store_gc_violations",
    "write_gc_policy_registry",
    "write_store_gc_outputs",
    "write_store_verify_outputs",
]
