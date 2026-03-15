"""Deterministic DIST-REFINE-1 install-profile helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from src.release import (
    DEFAULT_COMPONENT_GRAPH_ID,
    DEFAULT_INSTALL_PROFILE_ID,
    DEFAULT_INSTALL_PROFILE_REGISTRY_REL,
    build_default_component_install_plan,
    canonicalize_install_profile,
    platform_targets_for_tag,
    select_install_profile,
)
from src.release.component_graph_resolver import deterministic_fingerprint
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "DIST_REFINE1_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "release", "INSTALL_PROFILES.md")
REGISTRY_REL = DEFAULT_INSTALL_PROFILE_REGISTRY_REL
BASELINE_DOC_REL = os.path.join("docs", "audit", "INSTALL_PROFILE_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "install_profile_report.json")
SCHEMA_REL = os.path.join("schema", "release", "install_profile.schema")
COMPILED_SCHEMA_REL = os.path.join("schemas", "install_profile.schema.json")
RULE_USE_PROFILES = "INV-DIST-BUNDLES-MUST-USE-INSTALL-PROFILES"
RULE_NO_HARDCODED = "INV-NO-HARDCODED-BUNDLE-CONTENTS"
LAST_REVIEWED = "2026-03-14"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


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


def _stability(*, future_series: str, replacement_target: str, rationale: str, id_stability: str = "") -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": "provisional",
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": "",
        "deterministic_fingerprint": "",
        "extensions": {"id_stability": _token(id_stability)},
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _profile_rows() -> list[dict]:
    common = {
        "default_mod_policy_id": "mod_policy.lab",
        "default_overlay_conflict_policy_id": "overlay.conflict.last_wins",
    }
    rows = [
        {
            "install_profile_id": "install.profile.full",
            "required_selectors": [
                "binary.client",
                "binary.game",
                "binary.launcher",
                "binary.server",
                "binary.setup",
                "docs.release_notes",
                "manifest.instance.default",
                "manifest.release_manifest",
            ],
            "optional_selectors": [],
            "extensions": {
                "summary": "Full MVP bundle with all default runtime products and default instance artifacts.",
                "default_mod_policy": "mods.disabled_by_default",
            },
            "stability": _stability(
                future_series="DIST/UPDATE-MODEL",
                replacement_target="Replace selector contents with release-index governed install profiles.",
                rationale="Full profile id is user-facing and frozen, but component selection stays provisional until release indices and trust policy are formalized.",
                id_stability="stable",
            ),
        },
        {
            "install_profile_id": "install.profile.client",
            "required_selectors": [
                "binary.client",
                "manifest.instance.default",
                "manifest.release_manifest",
            ],
            "optional_selectors": [
                "binary.launcher",
                "binary.setup",
                "docs.release_notes",
            ],
            "extensions": {
                "summary": "Client-centric runtime profile without dedicated server binaries by default.",
                "default_mod_policy": "mods.disabled_by_default",
            },
            "stability": _stability(
                future_series="DIST/UPDATE-MODEL",
                replacement_target="Refine client profile contents once release indices and remote acquisition are formalized.",
                rationale="Client profile id is frozen for mock release, while optional launcher/setup composition remains provisional.",
                id_stability="stable",
            ),
        },
        {
            "install_profile_id": "install.profile.server",
            "required_selectors": [
                "binary.server",
                "manifest.instance.default",
                "manifest.release_manifest",
            ],
            "optional_selectors": [
                "binary.launcher",
                "binary.setup",
                "docs.release_notes",
            ],
            "extensions": {
                "summary": "Authoritative server runtime profile with required content but no rendered client binary.",
                "default_mod_policy": "mods.disabled_by_default",
            },
            "stability": _stability(
                future_series="DIST/UPDATE-MODEL",
                replacement_target="Refine server profile contents once update model and remote acquisition are formalized.",
                rationale="Server profile id is frozen for mock release, while bundled management surfaces remain provisional.",
                id_stability="stable",
            ),
        },
        {
            "install_profile_id": "install.profile.tools",
            "required_selectors": [
                "binary.setup",
                "manifest.release_manifest",
            ],
            "optional_selectors": [
                "binary.launcher",
                "docs.release_notes",
            ],
            "extensions": {
                "summary": "Offline verification and store-management surface with no client/server runtime by default.",
                "default_mod_policy": "mods.disabled_by_default",
            },
            "stability": _stability(
                future_series="DIST/UPDATE-MODEL",
                replacement_target="Refine tools profile once dedicated tool components and update policy are formalized.",
                rationale="Tools profile id is frozen for mock release, while optional launcher/docs composition remains provisional.",
                id_stability="stable",
            ),
        },
        {
            "install_profile_id": "install.profile.sdk",
            "required_selectors": [
                "docs.release_notes",
                "manifest.release_manifest",
            ],
            "optional_selectors": [
                "binary.setup",
            ],
            "extensions": {
                "summary": "Future SDK/doc tooling profile placeholder.",
                "default_mod_policy": "mods.disabled_by_default",
            },
            "stability": _stability(
                future_series="DIST-SDK/UPDATE-MODEL",
                replacement_target="Replace the SDK placeholder with release-index governed SDK components and acquisition policy.",
                rationale="SDK profile is a forward-compatibility placeholder only and is not enabled by default in the mock release.",
                id_stability="stable",
            ),
        },
    ]
    out = []
    for row in rows:
        payload = canonicalize_install_profile({**common, **row})
        payload["stability"] = dict(row.get("stability") or {})
        out.append(payload)
    return sorted(out, key=lambda row: _token(row.get("install_profile_id")))


def build_install_profile_registry_payload() -> dict:
    return {
        "schema_id": "dominium.registry.install_profile_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.install_profile_registry",
            "registry_version": "1.0.0",
            "install_profiles": _profile_rows(),
            "extensions": {"official.source": "DIST-REFINE1-2"},
        },
    }


def build_install_profile_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    registry_payload = build_install_profile_registry_payload()
    targets = platform_targets_for_tag(platform_tag, repo_root=root)
    profiles = []
    for row in list(_as_map(registry_payload.get("record")).get("install_profiles") or []):
        profile = select_install_profile(registry_payload, install_profile_id=_token(_as_map(row).get("install_profile_id")))
        resolution = build_default_component_install_plan(
            root,
            graph_id=DEFAULT_COMPONENT_GRAPH_ID,
            install_profile_id=_token(profile.get("install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
            target_platform=_token(targets.get("platform_id")),
            target_arch=_token(targets.get("arch_id")),
            target_abi=_token(targets.get("abi_id")),
        )
        install_plan = dict(resolution.get("install_plan") or {})
        profiles.append(
            {
                "install_profile_id": _token(profile.get("install_profile_id")),
                "result": _token(resolution.get("result")),
                "selected_components": list(install_plan.get("selected_components") or []),
                "disabled_optional_components": list(_as_map(install_plan.get("extensions")).get("disabled_optional_components") or []),
                "install_plan_fingerprint": _token(install_plan.get("deterministic_fingerprint")),
                "selection_reasons": list(_as_map(install_plan.get("extensions")).get("selection_reasons") or []),
            }
        )
    report = {
        "report_id": "release.install_profiles.v1",
        "result": "complete" if all(_token(row.get("result")) == "complete" for row in profiles) else "refused",
        "install_profile_registry_hash": canonical_sha256(registry_payload),
        "platform_tag": _token(platform_tag),
        "target": dict(targets),
        "profile_count": len(profiles),
        "profiles": profiles,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_install_profile_baseline(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST/UPDATE-MODEL",
        "Replacement Target: release-index governed install profiles with trust-policy and acquisition planning",
        "",
        "# Install Profile Baseline",
        "",
        "## Profile Definitions",
        "",
    ]
    registry_payload = build_install_profile_registry_payload()
    for row in list(_as_map(registry_payload.get("record")).get("install_profiles") or []):
        item = dict(row or {})
        lines.append("- `{}` required=`{}` optional=`{}`".format(
            _token(item.get("install_profile_id")),
            ", ".join(list(item.get("required_selectors") or [])) or "none",
            ", ".join(list(item.get("optional_selectors") or [])) or "none",
        ))
    lines.extend(["", "## Resolved Component Sets", ""])
    for row in list(report.get("profiles") or []):
        item = dict(row or {})
        lines.append("- `{}` -> `{}`".format(_token(item.get("install_profile_id")), ", ".join(list(item.get("selected_components") or [])) or "none"))
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "- UPDATE-MODEL-0 release-index availability: ready",
            "- Dist assembly profile selection: ready",
            "",
            "## Report Fingerprints",
            "",
            "- install profile registry hash: `{}`".format(_token(report.get("install_profile_registry_hash"))),
            "- report fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
            "",
        ]
    )
    return "\n".join(lines)


def write_install_profile_outputs(repo_root: str, *, platform_tag: str = "win64", write_registry: bool = False) -> dict:
    root = _norm(repo_root)
    registry_payload = build_install_profile_registry_payload()
    if write_registry:
        _write_json(os.path.join(root, REGISTRY_REL), registry_payload)
    report = build_install_profile_report(root, platform_tag=platform_tag)
    _write_json(os.path.join(root, REPORT_JSON_REL), report)
    _write_text(os.path.join(root, BASELINE_DOC_REL), render_install_profile_baseline(report))
    return {"report": report, "report_json_path": REPORT_JSON_REL, "baseline_doc_path": BASELINE_DOC_REL}


def install_profile_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "DIST-REFINE-1 retro audit is required", RULE_USE_PROFILES),
        (DOCTRINE_DOC_REL, "install profile doctrine is required", RULE_USE_PROFILES),
        (SCHEMA_REL, "install_profile schema is required", RULE_USE_PROFILES),
        (COMPILED_SCHEMA_REL, "compiled install_profile schema is required", RULE_USE_PROFILES),
        (REGISTRY_REL, "install profile registry is required", RULE_USE_PROFILES),
        (BASELINE_DOC_REL, "install profile baseline is required", RULE_USE_PROFILES),
        (REPORT_JSON_REL, "install profile machine report is required", RULE_USE_PROFILES),
        (os.path.join("tools", "release", "install_profile_common.py"), "install profile helper is required", RULE_USE_PROFILES),
        (os.path.join("tools", "release", "tool_run_install_profiles.py"), "install profile runner is required", RULE_USE_PROFILES),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": rel_path, "rule_id": rule_id})
    for rel_path, token, message, rule_id in (
        ("src/release/component_graph_resolver.py", "select_install_profile(", "component resolver must load and select install profiles", RULE_USE_PROFILES),
        ("src/release/component_graph_resolver.py", "disabled_optional_components", "install plans must report disabled optional components", RULE_USE_PROFILES),
        ("tools/setup/setup_cli.py", "\"plan\"", "setup install surface must expose install-profile plan/apply commands", RULE_USE_PROFILES),
        ("tools/setup/setup_cli.py", "install_profile_id", "setup install plan/apply must thread install_profile_id through the resolver", RULE_USE_PROFILES),
        ("tools/dist/dist_tree_common.py", "install_profile_id", "dist assembly must choose bundle contents through an install profile", RULE_NO_HARDCODED),
        ("tools/dist/tool_assemble_dist_tree.py", "--install-profile-id", "dist assembly CLI must accept install_profile_id", RULE_USE_PROFILES),
        ("tools/launcher/launch.py", "install_profile_id", "launcher instance surfaces must expose instance install profile targeting", RULE_USE_PROFILES),
    ):
        try:
            with open(os.path.join(root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            text = ""
        if token in text:
            continue
        violations.append({"code": "missing_integration_hook", "message": message, "file_path": rel_path, "rule_id": rule_id})
    report = build_install_profile_report(root)
    if _token(report.get("result")) != "complete":
        violations.append(
            {
                "code": "install_profile_resolution_failed",
                "message": "install profile report must resolve all profiles on the baseline platform",
                "file_path": BASELINE_DOC_REL,
                "rule_id": RULE_USE_PROFILES,
            }
        )
    return violations


__all__ = [
    "BASELINE_DOC_REL",
    "COMPILED_SCHEMA_REL",
    "DOCTRINE_DOC_REL",
    "REGISTRY_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_NO_HARDCODED",
    "RULE_USE_PROFILES",
    "build_install_profile_registry_payload",
    "build_install_profile_report",
    "install_profile_violations",
    "render_install_profile_baseline",
    "write_install_profile_outputs",
]
