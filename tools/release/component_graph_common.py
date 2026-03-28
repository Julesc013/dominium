"""Deterministic COMPONENT-GRAPH-0 helpers."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Mapping

from release.component_graph_resolver import (
    COMPONENT_KIND_BINARY,
    COMPONENT_KIND_DOCS,
    COMPONENT_KIND_LOCK,
    COMPONENT_KIND_MANIFEST,
    COMPONENT_KIND_PACK,
    COMPONENT_KIND_PROFILE,
    DEFAULT_COMPONENT_GRAPH_ID,
    DEFAULT_COMPONENT_GRAPH_REGISTRY_REL,
    DEFAULT_INSTALL_PROFILE_ID,
    EDGE_KIND_PROVIDES,
    EDGE_KIND_RECOMMENDS,
    EDGE_KIND_REQUIRES,
    build_default_component_install_plan,
    canonicalize_component_descriptor,
    canonicalize_component_edge,
    canonicalize_component_graph,
    deterministic_fingerprint,
    platform_targets_for_tag,
)
from tools.import_bridge import resolve_repo_path_equivalent
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


ARCH_REGISTRY_REL = os.path.join("data", "registries", "arch_registry.json")
OS_REGISTRY_REL = os.path.join("data", "registries", "os_registry.json")
GRAPH_REGISTRY_REL = DEFAULT_COMPONENT_GRAPH_REGISTRY_REL
RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "COMPONENT_GRAPH0_RETRO_AUDIT.md")
CONSTITUTION_DOC_REL = os.path.join("docs", "release", "COMPONENT_GRAPH_CONSTITUTION.md")
RELEASE_NOTES_DOC_REL = os.path.join("docs", "release", "RELEASE_NOTES_v0_0_0_mock.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "COMPONENT_GRAPH_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "component_graph_report.json")
RULE_INSTALL = "INV-INSTALLS-RESOLVED-VIA-COMPONENT-GRAPH"
RULE_HARDCODED = "INV-NO-HARDCODED-COMPONENT-SETS"
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
    digest = hashlib.sha256()
    try:
        with open(_norm(path), "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def _release_component_hash(component_id: str) -> str:
    return canonical_sha256({"component_id": component_id, "binding_mode": "release_index_required"})


def _stability(rationale: str, future_series: str, replacement_target: str, *, contract_id: str = "") -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": "provisional" if not contract_id else "stable",
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": _token(contract_id),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _pack_lock(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), "locks", "pack_lock.mvp_default.json"))


def _profile_bundle(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), "profiles", "bundles", "bundle.mvp_default.json"))


def _pack_descriptor_rows(repo_root: str) -> list[dict]:
    rows = []
    pack_lock = _pack_lock(repo_root)
    for row in list(pack_lock.get("ordered_packs") or []):
        item = dict(row or {})
        component_id = "pack.{}".format(_token(item.get("pack_id")).replace("pack.", "", 1))
        rows.append(
            canonicalize_component_descriptor(
                {
                    "component_id": component_id,
                    "component_kind": COMPONENT_KIND_PACK,
                    "content_hash": _token(item.get("canonical_hash")).lower(),
                    "version": _token(item.get("version")) or "0.0.0",
                    "extensions": {
                        "pack_id": _token(item.get("pack_id")),
                        "distribution_rel": _token(item.get("distribution_rel")),
                        "pack_compat_hash": _token(_as_map(pack_lock.get("pack_compat_hashes")).get(_token(item.get("pack_id")))).lower(),
                    },
                }
            )
        )
    return sorted(rows, key=lambda row: _token(row.get("component_id")))


def _component_rows(repo_root: str) -> list[dict]:
    profile_bundle = _profile_bundle(repo_root)
    pack_lock = _pack_lock(repo_root)
    release_notes_hash = _sha256_file(os.path.join(_norm(repo_root), RELEASE_NOTES_DOC_REL))
    rows = [
        canonicalize_component_descriptor({"component_id": "manifest.appshell.runtime", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.appshell.runtime"), "version": "0.0.0", "extensions": {"binding_mode": "release_index_required"}}),
        canonicalize_component_descriptor({"component_id": "manifest.lib.runtime", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.lib.runtime"), "version": "0.0.0", "extensions": {"binding_mode": "release_index_required"}}),
        canonicalize_component_descriptor({"component_id": "manifest.pack_compat.runtime", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.pack_compat.runtime"), "version": "0.0.0", "extensions": {"binding_mode": "release_index_required"}}),
        canonicalize_component_descriptor({"component_id": "manifest.compat.negotiation", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.compat.negotiation"), "version": "0.0.0", "extensions": {"binding_mode": "release_index_required"}}),
        canonicalize_component_descriptor({"component_id": "manifest.release_manifest", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.release_manifest"), "version": "1.0.0", "extensions": {"binding_mode": "dist_assembly_required"}}),
        canonicalize_component_descriptor({"component_id": "manifest.instance.default", "component_kind": COMPONENT_KIND_MANIFEST, "content_hash": _release_component_hash("manifest.instance.default"), "version": "1.0.0", "extensions": {"binding_mode": "dist_assembly_required"}}),
        canonicalize_component_descriptor({"component_id": "profile.bundle.mvp_default", "component_kind": COMPONENT_KIND_PROFILE, "content_hash": _token(profile_bundle.get("profile_bundle_hash")).lower(), "version": _token(profile_bundle.get("runtime_version")) or "0.0.0", "provides_ids": ["provides.profile.bundle.v1"], "extensions": {"profile_bundle_id": _token(profile_bundle.get("profile_bundle_id")), "profile_bundle_hash": _token(profile_bundle.get("profile_bundle_hash")).lower()}}),
        canonicalize_component_descriptor({"component_id": "lock.pack_lock.mvp_default", "component_kind": COMPONENT_KIND_LOCK, "content_hash": _token(pack_lock.get("pack_lock_hash")).lower(), "version": _token(pack_lock.get("runtime_version")) or "0.0.0", "extensions": {"pack_lock_id": _token(pack_lock.get("pack_lock_id")), "pack_lock_hash": _token(pack_lock.get("pack_lock_hash")).lower()}}),
        canonicalize_component_descriptor({"component_id": "docs.release_notes", "component_kind": COMPONENT_KIND_DOCS, "content_hash": release_notes_hash, "version": "v0.0.0-mock", "extensions": {"doc_rel": RELEASE_NOTES_DOC_REL}}),
    ]
    for product_id in ("engine", "game", "client", "server", "setup", "launcher"):
        rows.append(
            canonicalize_component_descriptor(
                {
                    "component_id": "binary.{}".format(product_id),
                    "component_kind": COMPONENT_KIND_BINARY,
                    "content_hash": _release_component_hash("binary.{}".format(product_id)),
                    "version": "0.0.0",
                    "extensions": {"product_id": product_id, "binding_mode": "release_index_required"},
                }
            )
        )
    rows.extend(_pack_descriptor_rows(repo_root))
    return sorted(rows, key=lambda row: _token(row.get("component_id")))


def _edge_rows() -> list[dict]:
    rows = [
        ("binary.engine", EDGE_KIND_REQUIRES, "manifest.appshell.runtime"),
        ("binary.game", EDGE_KIND_REQUIRES, "binary.engine"),
        ("binary.game", EDGE_KIND_REQUIRES, "lock.pack_lock.mvp_default"),
        ("binary.game", EDGE_KIND_REQUIRES, "profile.bundle.mvp_default"),
        ("binary.client", EDGE_KIND_REQUIRES, "binary.engine"),
        ("binary.client", EDGE_KIND_REQUIRES, "lock.pack_lock.mvp_default"),
        ("binary.client", EDGE_KIND_REQUIRES, "profile.bundle.mvp_default"),
        ("binary.client", EDGE_KIND_REQUIRES, "manifest.compat.negotiation"),
        ("binary.client", EDGE_KIND_REQUIRES, "manifest.appshell.runtime"),
        ("binary.server", EDGE_KIND_REQUIRES, "binary.engine"),
        ("binary.server", EDGE_KIND_REQUIRES, "lock.pack_lock.mvp_default"),
        ("binary.server", EDGE_KIND_REQUIRES, "profile.bundle.mvp_default"),
        ("binary.server", EDGE_KIND_REQUIRES, "manifest.compat.negotiation"),
        ("binary.server", EDGE_KIND_REQUIRES, "manifest.appshell.runtime"),
        ("binary.setup", EDGE_KIND_REQUIRES, "manifest.pack_compat.runtime"),
        ("binary.setup", EDGE_KIND_REQUIRES, "manifest.lib.runtime"),
        ("binary.setup", EDGE_KIND_REQUIRES, "manifest.appshell.runtime"),
        ("binary.setup", EDGE_KIND_REQUIRES, "manifest.release_manifest"),
        ("binary.launcher", EDGE_KIND_REQUIRES, "binary.setup"),
        ("binary.launcher", EDGE_KIND_REQUIRES, "manifest.lib.runtime"),
        ("binary.launcher", EDGE_KIND_REQUIRES, "manifest.appshell.runtime"),
        ("binary.launcher", EDGE_KIND_REQUIRES, "manifest.compat.negotiation"),
        ("binary.launcher", EDGE_KIND_RECOMMENDS, "manifest.instance.default"),
        ("binary.launcher", EDGE_KIND_RECOMMENDS, "docs.release_notes"),
        ("manifest.instance.default", EDGE_KIND_REQUIRES, "lock.pack_lock.mvp_default"),
        ("manifest.instance.default", EDGE_KIND_REQUIRES, "profile.bundle.mvp_default"),
        ("lock.pack_lock.mvp_default", EDGE_KIND_REQUIRES, "pack.base.procedural"),
        ("lock.pack_lock.mvp_default", EDGE_KIND_REQUIRES, "pack.sol.pin_minimal"),
        ("lock.pack_lock.mvp_default", EDGE_KIND_REQUIRES, "pack.earth.procedural"),
        ("profile.bundle.mvp_default", EDGE_KIND_PROVIDES, "provides.profile.bundle.v1"),
    ]
    return [canonicalize_component_edge({"from_component_id": a, "edge_kind": b, "to_component_selector": c}) for a, b, c in rows]


def build_component_graph_registry_payload(repo_root: str) -> dict:
    graph = canonicalize_component_graph(
        {
            "graph_id": DEFAULT_COMPONENT_GRAPH_ID,
            "release_id": "release.v0.0.0-mock",
            "components": _component_rows(repo_root),
            "edges": _edge_rows(),
            "extensions": {
                "default_requested_components": [
                    "binary.client",
                    "binary.engine",
                    "binary.game",
                    "binary.launcher",
                    "binary.server",
                    "binary.setup",
                    "docs.release_notes",
                    "manifest.instance.default",
                    "manifest.release_manifest",
                ]
            },
        }
    )
    graph["stability"] = _stability(
        "Baseline release component graph is deterministic and additive, but install profiles, trust policy, and platform release indices are still evolving.",
        "DIST-REFINE/TRUST",
        "Replace the MVP baseline graph with install-profile and release-index governed component graphs.",
    )
    return {
        "schema_id": "dominium.registry.component_graph_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.component_graph_registry",
            "registry_version": "1.0.0",
            "graphs": [graph],
            "extensions": {"official.source": "COMPONENT-GRAPH0-1"},
        },
    }


def build_arch_registry_payload() -> dict:
    rows = []
    for arch_id, width in (
        ("arch.x86_32", 32),
        ("arch.x86_64", 64),
        ("arch.arm32", 32),
        ("arch.arm64", 64),
        ("arch.wasm32", 32),
        ("arch.wasm64", 64),
        ("arch.ppc32", 32),
        ("arch.ppc64", 64),
        ("arch.riscv64", 64),
    ):
        row = {"arch_id": arch_id, "word_size_bits": width, "deterministic_fingerprint": "", "extensions": {}, "stability": _stability("Architecture ids are additive distribution filters for component planning.", "DIST/PLATFORM", "Replace MVP architecture stubs with release-index governed platform availability metadata.")}
        row["deterministic_fingerprint"] = deterministic_fingerprint(dict(row, stability={}, deterministic_fingerprint=""))
        rows.append(row)
    return {"schema_id": "dominium.registry.arch_registry", "schema_version": "1.0.0", "record": {"registry_id": "dominium.registry.arch_registry", "registry_version": "1.0.0", "architectures": rows, "extensions": {"official.source": "COMPONENT-GRAPH0-1"}}}


def build_os_registry_payload() -> dict:
    rows = []
    for os_id, family in (
        ("os.msdos", "dos"),
        ("os.win9x", "windows"),
        ("os.winnt", "windows"),
        ("os.linux", "linux"),
        ("os.macos_classic", "macos"),
        ("os.macosx", "macos"),
        ("os.bsd", "bsd"),
        ("os.web", "web"),
        ("os.posix", "posix"),
    ):
        row = {"os_id": os_id, "family_id": family, "deterministic_fingerprint": "", "extensions": {}, "stability": _stability("Operating-system ids are additive distribution filters for component planning.", "DIST/PLATFORM", "Replace MVP operating-system stubs with release-index governed platform availability metadata.")}
        row["deterministic_fingerprint"] = deterministic_fingerprint(dict(row, stability={}, deterministic_fingerprint=""))
        rows.append(row)
    return {"schema_id": "dominium.registry.os_registry", "schema_version": "1.0.0", "record": {"registry_id": "dominium.registry.os_registry", "registry_version": "1.0.0", "operating_systems": rows, "extensions": {"official.source": "COMPONENT-GRAPH0-1"}}}


def build_component_graph_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    graph_registry = build_component_graph_registry_payload(root)
    graph_rows = list(_as_map(graph_registry.get("record")).get("graphs") or [])
    graph = canonicalize_component_graph(_as_map(graph_rows[0])) if graph_rows else canonicalize_component_graph({})
    target = platform_targets_for_tag(platform_tag, repo_root=root)
    resolution = build_default_component_install_plan(
        root,
        graph_id=DEFAULT_COMPONENT_GRAPH_ID,
        target_platform=_token(target.get("platform_id")),
        target_arch=_token(target.get("arch_id")),
        target_abi=_token(target.get("abi_id")),
        install_profile_id=DEFAULT_INSTALL_PROFILE_ID,
    )
    install_plan = dict(resolution.get("install_plan") or {})
    report = {
        "report_id": "release.component_graph.v1",
        "result": "complete" if _token(resolution.get("result")) == "complete" else "refused",
        "graph_registry_hash": canonical_sha256(graph_registry),
        "graph_id": _token(graph.get("graph_id")),
        "graph_hash": _token(graph.get("deterministic_fingerprint")),
        "component_count": int(len(list(graph.get("components") or []))),
        "edge_count": int(len(list(graph.get("edges") or []))),
        "selected_component_ids": list(install_plan.get("selected_components") or []),
        "resolved_provider_count": int(len(list(install_plan.get("resolved_providers") or []))),
        "install_plan_fingerprint": _token(install_plan.get("deterministic_fingerprint")),
        "target": target,
        "errors": list(resolution.get("errors") or []),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_component_graph_baseline(report: Mapping[str, object], repo_root: str) -> str:
    registry = build_component_graph_registry_payload(repo_root)
    graph = _as_map(_as_map(registry.get("record")).get("graphs")[0])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: install profiles, update-model release indices, and trust-policy resolution surfaces",
        "",
        "# Component Graph Baseline",
        "",
        "## Component List",
        "",
    ]
    for row in list(graph.get("components") or []):
        item = _as_map(row)
        lines.append("- `{}` kind=`{}` version=`{}`".format(_token(item.get("component_id")), _token(item.get("component_kind")), _token(item.get("version"))))
    lines.extend(["", "## Edge List", ""])
    for row in list(graph.get("edges") or []):
        item = _as_map(row)
        lines.append("- `{}` {} `{}`".format(_token(item.get("from_component_id")), _token(item.get("edge_kind")), _token(item.get("to_component_selector"))))
    lines.extend(
        [
            "",
            "## Resolution Algorithm",
            "",
            "- stable lexical traversal by `component_id`",
            "- expand `requires`, then `recommends`, then provider bindings",
            "- deterministic provides resolution through the LIB provider resolver",
            "- strict conflicts refuse",
            "",
            "## Readiness",
            "",
            "- DIST-REFINE-1 install profiles: ready",
            "- update-model release indices: ready",
            "",
            "## Report Fingerprints",
            "",
            "- graph hash: `{}`".format(_token(report.get("graph_hash"))),
            "- plan fingerprint: `{}`".format(_token(report.get("install_plan_fingerprint"))),
            "- report fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
            "",
        ]
    )
    return "\n".join(lines)


def write_component_graph_outputs(repo_root: str, *, platform_tag: str = "win64", write_registries: bool = False) -> dict:
    root = _norm(repo_root)
    if write_registries:
        _write_json(os.path.join(root, ARCH_REGISTRY_REL), build_arch_registry_payload())
        _write_json(os.path.join(root, OS_REGISTRY_REL), build_os_registry_payload())
        _write_json(os.path.join(root, GRAPH_REGISTRY_REL), build_component_graph_registry_payload(root))
    report = build_component_graph_report(root, platform_tag=platform_tag)
    _write_json(os.path.join(root, REPORT_JSON_REL), report)
    _write_text(os.path.join(root, BASELINE_DOC_REL), render_component_graph_baseline(report, root))
    return {"report": report, "report_json_path": REPORT_JSON_REL, "baseline_doc_path": BASELINE_DOC_REL}


def component_graph_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    report = build_component_graph_report(root)
    violations = []
    for rel_path, message, rule_id in (
        (ARCH_REGISTRY_REL, "arch registry is required", RULE_INSTALL),
        (OS_REGISTRY_REL, "os registry is required", RULE_INSTALL),
        (GRAPH_REGISTRY_REL, "component graph registry is required", RULE_INSTALL),
        (RETRO_AUDIT_DOC_REL, "retro audit doc is required", RULE_INSTALL),
        (CONSTITUTION_DOC_REL, "component graph constitution is required", RULE_INSTALL),
        (BASELINE_DOC_REL, "component graph baseline is required", RULE_INSTALL),
        (RELEASE_NOTES_DOC_REL, "release notes document is required", RULE_HARDCODED),
        (os.path.join("release", "component_graph_resolver.py"), "component graph resolver is required", RULE_INSTALL),
        (os.path.join("tools", "release", "component_graph_common.py"), "component graph helper is required", RULE_INSTALL),
        (os.path.join("tools", "release", "tool_run_component_graph.py"), "component graph runner is required", RULE_INSTALL),
    ):
        effective_rel = _equivalent_rel(root, rel_path)
        if os.path.exists(_equivalent_abs(root, rel_path)):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": effective_rel if effective_rel != _norm_rel(rel_path) else rel_path, "rule_id": rule_id})
    for rel_path, token, message, rule_id in (
        ("tools/dist/dist_tree_common.py", "build_default_component_install_plan", "dist assembly must resolve bundle composition through the component graph", RULE_HARDCODED),
        ("tools/setup/setup_cli.py", "build_default_component_install_plan", "setup must emit an install plan derived from the component graph", RULE_INSTALL),
        ("tools/launcher/launch.py", "validate_instance_against_install_plan", "launcher must validate instances against the component graph install plan", RULE_INSTALL),
        ("release/release_manifest_engine.py", "component_graph_hash", "release manifest generation must include the component graph hash", RULE_INSTALL),
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
    if _token(report.get("result")) != "complete":
        violations.append({"code": "resolver_refused", "message": "component graph resolver must complete for the baseline target", "file_path": BASELINE_DOC_REL, "rule_id": RULE_INSTALL})
    return violations
