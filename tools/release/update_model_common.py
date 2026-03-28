"""Deterministic UPDATE-MODEL-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from meta.identity import (
    IDENTITY_KIND_SUITE_RELEASE,
    attach_universal_identity_block,
)
from governance import (
    DEFAULT_GOVERNANCE_PROFILE_REL,
    governance_profile_hash,
    load_governance_profile,
)
from lib.install import normalize_install_manifest
from engine.platform.target_matrix import select_target_matrix_row, target_matrix_registry_hash
from release import (
    DEFAULT_COMPONENT_GRAPH_ID,
    DEFAULT_INSTALL_PROFILE_ID,
    DEFAULT_RELEASE_INDEX_REL,
    DEFAULT_RELEASE_MANIFEST_REL,
    canonicalize_release_index,
    component_managed_paths,
    load_default_component_graph,
    load_release_manifest,
    platform_targets_for_tag,
    resolve_update_plan,
    write_release_index,
)
from release.component_graph_resolver import canonicalize_component_descriptor, canonicalize_component_graph
from security.trust import load_trust_policy_registry, load_trust_root_registry, select_trust_policy
from tools.import_bridge import resolve_repo_path_equivalent
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "UPDATE_MODEL0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "release", "RELEASE_INDEX_MODEL.md")
SELF_UPDATE_DOC_REL = os.path.join("docs", "release", "SETUP_SELF_UPDATE.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "UPDATE_MODEL_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "update_model_report.json")
RULE_USE_COMPONENT_GRAPH = "INV-UPDATE-MUST-USE-COMPONENT-GRAPH"
RULE_ROLLBACK_LOG = "INV-ROLLBACK-REQUIRES-TRANSACTION-LOG"
RULE_NO_SILENT_UPGRADE = "INV-NO-SILENT-UPGRADE"
LAST_REVIEWED = "2026-03-14"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _equivalent_rel(repo_root: str, rel_path: str) -> str:
    return _norm_rel(resolve_repo_path_equivalent(_norm(repo_root), _norm_rel(rel_path)))


def _equivalent_abs(repo_root: str, rel_path: str) -> str:
    return os.path.join(_norm(repo_root), _equivalent_rel(repo_root, rel_path).replace("/", os.sep))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


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


def _sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(_norm(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_root(repo_root: str, platform_tag: str, channel_id: str) -> str:
    return os.path.join(_norm(repo_root), "dist", "v0.0.0-{}".format(_token(channel_id) or "mock"), _token(platform_tag) or "win64", "dominium")


def _existing_bundle_root(repo_root: str, platform_tag: str) -> str:
    candidates = [
        _bundle_root(repo_root, platform_tag, "mock"),
        os.path.join(_norm(repo_root), "build", "tmp", "update_model_dist", "v0.0.0-mock", _token(platform_tag) or "win64", "dominium"),
        os.path.join(_norm(repo_root), "build", "tmp", "update_model_test_dist", "v0.0.0-mock", _token(platform_tag) or "win64", "dominium"),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "manifests", "release_manifest.json")):
            return candidate
    return candidates[0]


def _install_manifest(dist_root: str) -> dict:
    return normalize_install_manifest(_read_json(os.path.join(_norm(dist_root), "install.manifest.json")))


def _platform_os_id(platform_id: str) -> str:
    mapping = {
        "platform.winnt": "os.winnt",
        "platform.win9x": "os.win9x",
        "platform.linux_gtk": "os.linux",
        "platform.posix_min": "os.posix",
        "platform.macos_cocoa": "os.macosx",
        "platform.macos_classic": "os.macos_classic",
    }
    return mapping.get(_token(platform_id), _token(platform_id))


def _release_artifact_map(release_manifest: Mapping[str, object]) -> dict:
    rows = {}
    for row in _as_list(_as_map(release_manifest).get("artifacts")):
        item = _as_map(row)
        key = (_token(item.get("artifact_kind")), _token(item.get("artifact_name")))
        rows[key] = item
    return rows


def _actualize_graph_components(
    graph: Mapping[str, object],
    *,
    dist_root: str,
    release_manifest: Mapping[str, object],
) -> list[dict]:
    artifact_rows = _release_artifact_map(release_manifest)
    out = []
    for row in _as_list(_as_map(graph).get("components")):
        item = canonicalize_component_descriptor(row)
        component_id = _token(item.get("component_id"))
        component_kind = _token(item.get("component_kind"))
        extensions = dict(_as_map(item.get("extensions")))
        updated = dict(item)
        if component_kind == "binary":
            product_id = _token(extensions.get("product_id"))
            artifact = artifact_rows.get(("artifact.binary", "bin/{}".format(product_id)))
            if artifact:
                artifact_extensions = _as_map(artifact.get("extensions"))
                extensions.update(artifact_extensions)
                extensions["managed_paths"] = component_managed_paths(
                    {"component_id": component_id, "component_kind": component_kind, "extensions": {"product_id": product_id}}
                )
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _token(artifact.get("content_hash")).lower(),
                        "version": _token(artifact_extensions.get("product_version")) or _token(item.get("version")),
                        "extensions": extensions,
                    }
                )
        elif component_kind == "pack":
            pack_id = _token(extensions.get("pack_id"))
            for (artifact_kind, artifact_name), artifact in sorted(artifact_rows.items()):
                if artifact_kind != "artifact.pack":
                    continue
                artifact_extensions = _as_map(artifact.get("extensions"))
                if _token(artifact_extensions.get("pack_id")) != pack_id:
                    continue
                extensions.update(artifact_extensions)
                extensions["distribution_rel"] = _token(artifact.get("artifact_name"))
                extensions["managed_paths"] = component_managed_paths(
                    {"component_id": component_id, "component_kind": component_kind, "extensions": {"distribution_rel": _token(artifact.get("artifact_name"))}}
                )
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _token(artifact.get("content_hash")).lower(),
                        "extensions": extensions,
                    }
                )
                break
        elif component_id == "profile.bundle.mvp_default":
            rel_path = "store/profiles/bundles/bundle.mvp_default.json"
            abs_path = os.path.join(_norm(dist_root), rel_path.replace("/", os.sep))
            if os.path.isfile(abs_path):
                extensions["managed_paths"] = [rel_path]
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _sha256_file(abs_path),
                        "extensions": extensions,
                    }
                )
        elif component_id == "lock.pack_lock.mvp_default":
            rel_path = "store/locks/pack_lock.mvp_default.json"
            abs_path = os.path.join(_norm(dist_root), rel_path.replace("/", os.sep))
            if os.path.isfile(abs_path):
                extensions["managed_paths"] = [rel_path]
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _sha256_file(abs_path),
                        "extensions": extensions,
                    }
                )
        elif component_id == "docs.release_notes":
            rel_path = _token(extensions.get("doc_rel")) or os.path.join("docs", "RELEASE_NOTES_v0_0_0_mock.md").replace("\\", "/")
            abs_path = os.path.join(_norm(dist_root), rel_path.replace("/", os.sep))
            if os.path.isfile(abs_path):
                extensions["managed_paths"] = [rel_path]
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _sha256_file(abs_path),
                        "extensions": extensions,
                    }
                )
        elif component_id == "manifest.release_manifest":
            rel_path = _norm_rel(DEFAULT_RELEASE_MANIFEST_REL)
            abs_path = os.path.join(_norm(dist_root), rel_path.replace("/", os.sep))
            if os.path.isfile(abs_path):
                extensions["managed_paths"] = [rel_path]
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _sha256_file(abs_path),
                        "extensions": extensions,
                    }
                )
        elif component_id == "manifest.instance.default":
            rel_path = "instances/default/instance.manifest.json"
            abs_path = os.path.join(_norm(dist_root), rel_path.replace("/", os.sep))
            if os.path.isfile(abs_path):
                extensions["managed_paths"] = [rel_path]
                updated = canonicalize_component_descriptor(
                    {
                        **item,
                        "content_hash": _sha256_file(abs_path),
                        "extensions": extensions,
                    }
                )
        final_extensions = dict(_as_map(updated.get("extensions")))
        if not _token(final_extensions.get("artifact_id")):
            managed_paths = list(final_extensions.get("managed_paths") or [])
            final_extensions["artifact_id"] = (
                _token(final_extensions.get("product_id"))
                or _token(final_extensions.get("pack_id"))
                or (str(managed_paths[0]).replace("\\", "/") if managed_paths else component_id)
            )
            updated = canonicalize_component_descriptor({**updated, "extensions": final_extensions})
        out.append(updated)
    return sorted(out, key=lambda row: _token(row.get("component_id")))


def build_release_index_payload(
    repo_root: str,
    *,
    dist_root: str,
    platform_tag: str = "win64",
    channel_id: str = "mock",
    release_series: str = "0.x",
    artifact_url_or_path: str = "..",
) -> dict:
    repo_root_abs = _norm(repo_root)
    root = _norm(dist_root)
    release_manifest = load_release_manifest(os.path.join(root, DEFAULT_RELEASE_MANIFEST_REL))
    install_manifest = _install_manifest(root)
    graph = load_default_component_graph(root, graph_id=DEFAULT_COMPONENT_GRAPH_ID)
    actualized_graph = canonicalize_component_graph(
        {
            **graph,
            "components": _actualize_graph_components(graph, dist_root=root, release_manifest=release_manifest),
        }
    )
    target = platform_targets_for_tag(platform_tag, repo_root=repo_root_abs)
    target_row = select_target_matrix_row(repo_root_abs, platform_tag=_token(platform_tag).lower())
    platform_id = _token(target.get("platform_id")) or _token(_as_map(target_row.get("extensions")).get("platform_id"))
    os_id = _token(target.get("os_id")) or _token(target_row.get("os_id")) or _platform_os_id(platform_id)
    arch_id = _token(target.get("arch_id")) or _token(target_row.get("arch_id"))
    abi_id = _token(target.get("abi_id")) or _token(target_row.get("abi_id"))
    tier_value = int(target.get("tier", target_row.get("tier", 0)) or 0)
    if tier_value >= 3:
        raise ValueError("target '{}' is Tier 3 and must not appear in the default release index".format(_token(target_row.get("target_id")) or _token(platform_tag)))
    release_manifest_hash = _token(release_manifest.get("manifest_hash")).lower()
    governance_profile = load_governance_profile(repo_root_abs, install_root=root)
    governance_hash = governance_profile_hash(governance_profile)
    payload = canonicalize_release_index(
        {
            "channel": _token(channel_id) or "mock",
            "release_series": _token(release_series) or "0.x",
            "semantic_contract_registry_hash": _token(install_manifest.get("semantic_contract_registry_hash")).lower(),
            "governance_profile_hash": governance_hash,
            "supported_protocol_ranges": dict(install_manifest.get("supported_protocol_versions") or {}),
            "platform_matrix": [
                {
                    "os": os_id,
                    "arch": arch_id,
                    "abi": abi_id,
                    "artifact_url_or_path": _token(artifact_url_or_path) or "..",
                    "extensions": {
                        "platform_id": platform_id,
                        "platform_tag": _token(platform_tag),
                        "target_id": _token(target_row.get("target_id")),
                        "tier": tier_value,
                    },
                }
            ],
            "component_graph_hash": _token(actualized_graph.get("deterministic_fingerprint")).lower(),
            "components": list(actualized_graph.get("components") or []),
            "extensions": {
                "release_id": _token(_as_map(release_manifest).get("release_id")),
                "release_manifest_hash": release_manifest_hash,
                "release_manifest_ref": _norm_rel(DEFAULT_RELEASE_MANIFEST_REL),
                "install_profile_id": _token(_as_map(install_manifest.get("extensions")).get("official.install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
                "governance_profile_ref": _norm_rel(DEFAULT_GOVERNANCE_PROFILE_REL),
                "governance_mode_id": _token(governance_profile.get("governance_mode_id")),
                "governance_version": _token(governance_profile.get("governance_version")),
                "release_resolution_policy_id": "policy.exact_suite",
                "component_graph": actualized_graph,
                "target_matrix_hash": target_matrix_registry_hash(repo_root_abs),
                "target_id": _token(target_row.get("target_id")),
                "target_tier": tier_value,
            },
        }
    )
    payload = attach_universal_identity_block(
        payload,
        identity_kind_id=IDENTITY_KIND_SUITE_RELEASE,
        identity_id="identity.release_index.{}".format(_token(_as_map(payload.get("extensions")).get("release_id")) or _token(channel_id) or "unknown"),
        stability_class_id="provisional",
        format_version="1.0.0",
        schema_version="1.0.0",
        protocol_range=_as_map(payload.get("supported_protocol_ranges")),
        contract_bundle_hash=_token(payload.get("semantic_contract_registry_hash")).lower(),
        extensions={"official.rel_path": "manifests/release_index.json"},
    )
    return payload


def build_update_model_report(repo_root: str, *, dist_root: str, platform_tag: str = "win64", write_release_index_file: bool = False) -> dict:
    root = _norm(repo_root)
    bundle_root = _norm(dist_root)
    install_manifest = _install_manifest(bundle_root)
    trust_policy_id = _token(_as_map(install_manifest.get("extensions")).get("official.trust_policy_id")) or "trust.default_mock"
    trust_policy_registry = load_trust_policy_registry(repo_root=root)
    trust_roots = load_trust_root_registry(repo_root=root, install_root=bundle_root)
    release_index = build_release_index_payload(root, dist_root=bundle_root, platform_tag=platform_tag)
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL)
    if write_release_index_file:
        write_release_index(release_index_path, release_index)
    resolution = resolve_update_plan(
        install_manifest,
        release_index,
        install_profile_id=_token(_as_map(install_manifest.get("extensions")).get("official.install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
        target_platform=_token(_as_map((_as_list(release_index.get("platform_matrix")) or [{}])[0]).get("os")),
        release_index_path=release_index_path,
        component_graph=_as_map(_as_map(release_index.get("extensions")).get("component_graph")),
        trust_policy_id=trust_policy_id,
        trust_policy=select_trust_policy(trust_policy_registry, trust_policy_id=trust_policy_id),
        trust_roots=list(trust_roots.get("trust_roots") or []),
        install_root=bundle_root,
    )
    update_plan = dict(resolution.get("update_plan") or {})
    report = {
        "report_id": "release.update_model.v1",
        "result": "complete" if _token(resolution.get("result")) == "complete" else "refused",
        "dist_root": _norm_rel(os.path.relpath(bundle_root, root)),
        "platform_tag": _token(platform_tag),
        "release_index_path": _norm_rel(os.path.relpath(release_index_path, bundle_root)),
        "release_index_hash": canonical_sha256(release_index),
        "governance_profile_hash": _token(release_index.get("governance_profile_hash")).lower(),
        "release_id": _token(_as_map(release_index.get("extensions")).get("release_id")),
        "component_graph_hash": _token(release_index.get("component_graph_hash")).lower(),
        "install_profile_id": _token(update_plan.get("install_profile_id")),
        "component_count": len(list(release_index.get("components") or [])),
        "add_count": len(list(update_plan.get("components_to_add") or [])),
        "remove_count": len(list(update_plan.get("components_to_remove") or [])),
        "upgrade_count": len(list(update_plan.get("components_to_upgrade") or [])),
        "update_plan_fingerprint": _token(update_plan.get("deterministic_fingerprint")),
        "errors": list(resolution.get("errors") or []),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_update_model_baseline(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: UPDATE/TRUST",
        "Replacement Target: trust-governed remote release indices and signed acquisition policy",
        "",
        "# Update Model Baseline",
        "",
        "## Release Index Schema",
        "",
        "- channel-aware offline-first release index",
        "- embedded component graph for deterministic install/update resolution",
        "- platform matrix filtered by os/arch/abi",
        "",
        "## Update Plan Logic",
        "",
        "- compare current install manifest against target release index",
        "- resolve target components through install profile + component graph",
        "- produce add/remove/upgrade sets in deterministic order",
        "- refuse on semantic-contract or protocol incompatibility",
        "",
        "## Rollback Model",
        "",
        "- `.dsu/install_transaction_log.json` records update and rollback actions",
        "- rollback selects the latest matching transaction by `from_release_id` when `--to` is supplied",
        "- rollback falls back to the most recent successful transaction when `--to` is omitted",
        "",
        "## Report Fingerprints",
        "",
        "- release index hash: `{}`".format(_token(report.get("release_index_hash"))),
        "- governance profile hash: `{}`".format(_token(report.get("governance_profile_hash"))),
        "- update plan fingerprint: `{}`".format(_token(report.get("update_plan_fingerprint"))),
        "- report fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Readiness",
        "",
        "- ARCH-MATRIX-0: ready",
        "- TRUST-MODEL-0: ready",
        "",
    ]
    return "\n".join(lines)


def write_update_model_outputs(repo_root: str, *, platform_tag: str = "win64", dist_root: str = "", write_release_index_file: bool = False) -> dict:
    root = _norm(repo_root)
    bundle_root = _norm(dist_root) if _token(dist_root) else _existing_bundle_root(root, platform_tag)
    report = build_update_model_report(root, dist_root=bundle_root, platform_tag=platform_tag, write_release_index_file=write_release_index_file)
    _write_json(os.path.join(root, REPORT_JSON_REL), report)
    _write_text(os.path.join(root, BASELINE_DOC_REL), render_update_model_baseline(report))
    if write_release_index_file:
        payload = build_release_index_payload(root, dist_root=bundle_root, platform_tag=platform_tag)
        write_release_index(os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL), payload)
    return {"report": report, "report_json_path": REPORT_JSON_REL, "baseline_doc_path": BASELINE_DOC_REL}


def update_model_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "UPDATE-MODEL-0 retro audit is required", RULE_USE_COMPONENT_GRAPH),
        (DOCTRINE_DOC_REL, "release index doctrine is required", RULE_USE_COMPONENT_GRAPH),
        (SELF_UPDATE_DOC_REL, "setup self-update doctrine is required", RULE_USE_COMPONENT_GRAPH),
        ("schema/release/release_index.schema", "release_index schema is required", RULE_USE_COMPONENT_GRAPH),
        ("schema/release/update_plan.schema", "update_plan schema is required", RULE_USE_COMPONENT_GRAPH),
        ("schemas/release_index.schema.json", "compiled release_index schema is required", RULE_USE_COMPONENT_GRAPH),
        ("schemas/update_plan.schema.json", "compiled update_plan schema is required", RULE_USE_COMPONENT_GRAPH),
        ("release/update_resolver.py", "update resolver is required", RULE_USE_COMPONENT_GRAPH),
        ("tools/release/update_model_common.py", "update-model helper is required", RULE_USE_COMPONENT_GRAPH),
        ("tools/release/tool_run_update_model.py", "update-model runner is required", RULE_USE_COMPONENT_GRAPH),
        (BASELINE_DOC_REL, "update-model baseline is required", RULE_USE_COMPONENT_GRAPH),
        (REPORT_JSON_REL, "update-model machine report is required", RULE_USE_COMPONENT_GRAPH),
    )
    for rel_path, message, rule_id in required_paths:
        effective_rel = _equivalent_rel(root, rel_path)
        if os.path.exists(_equivalent_abs(root, rel_path)):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": effective_rel if effective_rel != _norm_rel(rel_path) else rel_path, "rule_id": rule_id})
    for rel_path, token, message, rule_id in (
        ("tools/setup/setup_cli.py", "resolve_update_plan", "setup update surfaces must resolve update plans through the release component graph", RULE_USE_COMPONENT_GRAPH),
        ("tools/setup/setup_cli.py", "install_transaction_log", "rollback must use the deterministic transaction log", RULE_ROLLBACK_LOG),
        ("tools/setup/setup_cli.py", "verify_release_manifest", "update apply must verify the target release manifest before changing the install", RULE_USE_COMPONENT_GRAPH),
        ("tools/dist/dist_tree_common.py", "release_index.json", "dist assembly must emit a release index for offline update resolution", RULE_USE_COMPONENT_GRAPH),
        ("tools/setup/setup_cli.py", "refusal.update", "setup update flows must emit explicit refusal codes instead of silent upgrade/refusal behavior", RULE_NO_SILENT_UPGRADE),
    ):
        text = ""
        try:
            effective_rel = _equivalent_rel(root, rel_path)
            with open(_equivalent_abs(root, rel_path), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            pass
        if token in text:
            continue
        violations.append({"code": "missing_integration_hook", "message": message, "file_path": effective_rel if effective_rel != _norm_rel(rel_path) else rel_path, "rule_id": rule_id})
    try:
        report = build_update_model_report(root, dist_root=_existing_bundle_root(root, "win64"), platform_tag="win64", write_release_index_file=False)
    except Exception as exc:
        violations.append({"code": "update_model_report_failed", "message": "unable to build update-model report ({})".format(str(exc)), "file_path": REPORT_JSON_REL, "rule_id": RULE_USE_COMPONENT_GRAPH})
        return violations
    if _token(report.get("result")) != "complete":
        violations.append({"code": "update_model_refused", "message": "update-model baseline must resolve successfully for the current distribution bundle", "file_path": BASELINE_DOC_REL, "rule_id": RULE_USE_COMPONENT_GRAPH})
    return violations


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_NO_SILENT_UPGRADE",
    "RULE_ROLLBACK_LOG",
    "RULE_USE_COMPONENT_GRAPH",
    "SELF_UPDATE_DOC_REL",
    "build_release_index_payload",
    "build_update_model_report",
    "render_update_model_baseline",
    "update_model_violations",
    "write_update_model_outputs",
]
