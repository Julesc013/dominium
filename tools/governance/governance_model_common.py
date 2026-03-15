"""Deterministic GOVERNANCE-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from src.governance import (
    ARCHIVE_POLICY_ID,
    DEFAULT_GOVERNANCE_MODE_REGISTRY_REL,
    DEFAULT_GOVERNANCE_PROFILE_REL,
    FORK_POLICY_ID,
    GOVERNANCE_MODE_CORE_CLOSED,
    GOVERNANCE_MODE_MIXED,
    GOVERNANCE_MODE_OPEN,
    REDISTRIBUTION_POLICY_ID,
    canonicalize_governance_mode_row,
    canonicalize_governance_profile,
    governance_profile_hash,
    load_governance_profile,
    parse_release_tag,
)
from src.meta.stability import build_stability_marker
from src.release import DEFAULT_RELEASE_INDEX_REL, load_release_index
from tools.dist.dist_tree_common import build_dist_tree
from tools.release.update_model_common import write_update_model_outputs
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "GOVERNANCE0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "governance", "GOVERNANCE_MODEL.md")
TRUST_ROOT_DOC_REL = os.path.join("docs", "governance", "TRUST_ROOT_GOVERNANCE.md")
LICENSING_DOC_REL = os.path.join("docs", "governance", "LICENSING_STRATEGY.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "GOVERNANCE_POLICY_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "governance_policy_report.json")
GOVERNANCE_PROFILE_SCHEMA_REL = os.path.join("schema", "governance", "governance_profile.schema")
GOVERNANCE_PROFILE_SCHEMA_JSON_REL = os.path.join("schemas", "governance_profile.schema.json")
RULE_PROFILE = "INV-GOVERNANCE-PROFILE-PRESENT-IN-RELEASE"
LAST_REVIEWED = "2026-03-14"


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


def _file_text(repo_root: str, rel_path: str) -> str:
    try:
        with open(os.path.join(_norm(repo_root), rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _governance_mode_rows() -> list[dict]:
    return [
        canonicalize_governance_mode_row(
            {
                "governance_mode_id": GOVERNANCE_MODE_OPEN,
                "open_source_surface_ids": [
                    "surface.engine",
                    "surface.game",
                    "surface.apps",
                    "surface.schemas",
                    "surface.protocols",
                    "surface.pack_formats",
                    "surface.docs",
                ],
                "closed_source_surface_ids": [],
                "extensions": {
                    "default_trust_policy_id": "trust.default_mock",
                    "redistribution_policy_id": REDISTRIBUTION_POLICY_ID,
                    "summary": "Fully open governance mode with open schemas and protocols.",
                },
                "stability": {
                    **build_stability_marker(
                        stability_class_id="provisional",
                        rationale="Mock release defaults to the most permissive governance mode while trust remains policy-driven.",
                        future_series="GOVERNANCE/RELEASE",
                        replacement_target="Channel-specific governance bundles for released series.",
                    )
                },
            }
        ),
        canonicalize_governance_mode_row(
            {
                "governance_mode_id": GOVERNANCE_MODE_CORE_CLOSED,
                "open_source_surface_ids": [
                    "surface.apps",
                    "surface.schemas",
                    "surface.protocols",
                    "surface.pack_formats",
                    "surface.docs",
                ],
                "closed_source_surface_ids": ["surface.engine", "surface.game"],
                "extensions": {
                    "default_trust_policy_id": "trust.default_mock",
                    "redistribution_policy_id": REDISTRIBUTION_POLICY_ID,
                    "summary": "Closed core with open ecosystem surfaces and third-party pack compatibility.",
                },
                "stability": {
                    **build_stability_marker(
                        stability_class_id="provisional",
                        rationale="Supported governance option for future commercial release lines.",
                        future_series="GOVERNANCE/COMMERCIAL",
                        replacement_target="Final artifact-specific licensing bundles and official publication policy.",
                    )
                },
            }
        ),
        canonicalize_governance_mode_row(
            {
                "governance_mode_id": GOVERNANCE_MODE_MIXED,
                "open_source_surface_ids": [
                    "surface.apps",
                    "surface.schemas",
                    "surface.protocols",
                    "surface.pack_formats",
                    "surface.docs",
                ],
                "closed_source_surface_ids": ["surface.engine_or_game"],
                "extensions": {
                    "default_trust_policy_id": "trust.default_mock",
                    "redistribution_policy_id": REDISTRIBUTION_POLICY_ID,
                    "summary": "Mixed licensing model with open ecosystem surfaces and optionally commercial packs.",
                },
                "stability": {
                    **build_stability_marker(
                        stability_class_id="provisional",
                        rationale="Supported split-licensing option for later release lines.",
                        future_series="GOVERNANCE/COMMERCIAL",
                        replacement_target="Final artifact-specific licensing bundles and signed official publication policy.",
                    )
                },
            }
        ),
    ]


def _governance_mode_registry_payload() -> dict:
    return {
        "schema_id": "dominium.registry.governance.governance_mode_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.governance.governance_mode_registry",
            "registry_version": "1.0.0",
            "governance_modes": _governance_mode_rows(),
            "extensions": {"official.source": "GOVERNANCE0-2"},
        },
    }


def _default_governance_profile() -> dict:
    return canonicalize_governance_profile(
        {
            "governance_version": "1.0.0",
            "governance_mode_id": GOVERNANCE_MODE_OPEN,
            "official_signer_ids": [],
            "redistribution_policy_id": REDISTRIBUTION_POLICY_ID,
            "fork_policy_id": FORK_POLICY_ID,
            "archive_policy_id": ARCHIVE_POLICY_ID,
            "extensions": {
                "default_channel_id": "mock",
                "default_trust_policy_id": "trust.default_mock",
                "signatures_optional_for_mock": True,
                "summary": "v0.0.0-mock ships under explicit open governance while trust remains hash-mandatory and signature-optional.",
            },
        }
    )


def write_governance_registries(repo_root: str) -> dict:
    root = _norm(repo_root)
    mode_registry = _governance_mode_registry_payload()
    profile = _default_governance_profile()
    mode_registry_path = _write_json(os.path.join(root, DEFAULT_GOVERNANCE_MODE_REGISTRY_REL), mode_registry)
    profile_path = _write_json(os.path.join(root, DEFAULT_GOVERNANCE_PROFILE_REL), profile)
    return {
        "mode_registry": mode_registry,
        "profile": profile,
        "mode_registry_path": _norm_rel(os.path.relpath(mode_registry_path, root)),
        "profile_path": _norm_rel(os.path.relpath(profile_path, root)),
    }


def _bundle_root(repo_root: str, platform_tag: str) -> str:
    candidates = [
        os.path.join(_norm(repo_root), "dist", "v0.0.0-mock", _token(platform_tag) or "win64", "dominium"),
        os.path.join(_norm(repo_root), "build", "tmp", "governance_model_dist", "v0.0.0-mock", _token(platform_tag) or "win64", "dominium"),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "manifests", "release_manifest.json")):
            return candidate
    return candidates[-1]


def _ensure_bundle(repo_root: str, platform_tag: str) -> str:
    bundle_root = _bundle_root(repo_root, platform_tag)
    release_manifest_path = os.path.join(bundle_root, "manifests", "release_manifest.json")
    governance_profile_path = os.path.join(bundle_root, DEFAULT_GOVERNANCE_PROFILE_REL.replace("/", os.sep))
    if not os.path.isfile(release_manifest_path) or not os.path.isfile(governance_profile_path):
        build_dist_tree(
            repo_root,
            platform_tag=_token(platform_tag) or "win64",
            channel_id="mock",
            output_root=os.path.join(_norm(repo_root), "build", "tmp", "governance_model_dist"),
            install_profile_id="install.profile.full",
        )
        bundle_root = os.path.join(_norm(repo_root), "build", "tmp", "governance_model_dist", "v0.0.0-mock", _token(platform_tag) or "win64", "dominium")
    write_update_model_outputs(repo_root, platform_tag=_token(platform_tag) or "win64", dist_root=bundle_root, write_release_index_file=True)
    return bundle_root


def _violation(rule_id: str, code: str, message: str, *, file_path: str) -> dict:
    return {
        "rule_id": _token(rule_id),
        "code": _token(code),
        "message": _token(message),
        "file_path": _norm_rel(file_path),
    }


def build_governance_model_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    registry_outputs = write_governance_registries(root)
    bundle_root = _ensure_bundle(root, _token(platform_tag) or "win64")
    profile = load_governance_profile(root)
    bundle_profile = load_governance_profile(root, install_root=bundle_root)
    release_index = load_release_index(os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL))
    governance_hash = governance_profile_hash(profile)
    bundle_governance_hash = governance_profile_hash(bundle_profile)
    release_index_hash = _token(release_index.get("governance_profile_hash")).lower()

    violations: list[dict] = []
    if not profile:
        violations.append(
            _violation(RULE_PROFILE, "governance_profile_missing", "governance profile must exist", file_path=DEFAULT_GOVERNANCE_PROFILE_REL)
        )
    if release_index_hash != governance_hash:
        violations.append(
            _violation(RULE_PROFILE, "release_index_governance_hash_mismatch", "release index must record the active governance profile hash", file_path=DEFAULT_RELEASE_INDEX_REL)
        )
    if bundle_governance_hash != governance_hash:
        violations.append(
            _violation(RULE_PROFILE, "bundle_governance_profile_mismatch", "bundled governance profile must match the repo governance profile", file_path=DEFAULT_GOVERNANCE_PROFILE_REL)
        )
    for rel_path, token, code, message in (
        ("tools/setup/setup_cli.py", "def handle_governance(", "setup_governance_status_missing", "setup CLI must expose governance status"),
        ("tools/setup/setup_cli.py", "trust status", "setup_trust_status_missing", "setup CLI must expose trust status"),
        ("tools/release/update_model_common.py", "governance_profile_hash", "release_index_governance_hash_missing", "release index generator must record governance profile hash"),
    ):
        if token in _file_text(root, rel_path):
            continue
        violations.append(_violation(RULE_PROFILE, code, message, file_path=rel_path))

    official_tag = parse_release_tag("v0.0.0-mock")
    fork_tag = parse_release_tag("fork.example.v0.0.0-mock")
    bad_tag = parse_release_tag("example.v0.0.0-mock")

    report = {
        "report_id": "governance.policy.v1",
        "result": "complete" if not violations else "refused",
        "governance_mode_id": _token(profile.get("governance_mode_id")),
        "governance_version": _token(profile.get("governance_version")),
        "official_signer_ids": list(profile.get("official_signer_ids") or []),
        "governance_profile_hash": governance_hash,
        "release_index_governance_hash": release_index_hash,
        "bundle_governance_profile_hash": bundle_governance_hash,
        "release_index_governance_match": release_index_hash == governance_hash,
        "mode_registry_hash": canonical_sha256(registry_outputs.get("mode_registry") or {}),
        "bundle_root": _norm_rel(os.path.relpath(bundle_root, root)),
        "fork_examples": {
            "official": official_tag,
            "fork": fork_tag,
            "invalid": bad_tag,
        },
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_governance_baseline(report: Mapping[str, object]) -> str:
    rows = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: GOVERNANCE/ARCHIVE",
        "Replacement Target: signed release publication bundles and archive governance policy",
        "",
        "# Governance Policy Baseline",
        "",
        "## Default Governance Mode For v0.0.0-mock",
        "",
        "- governance_mode_id: `{}`".format(_token(rows.get("governance_mode_id"))),
        "- governance_version: `{}`".format(_token(rows.get("governance_version"))),
        "- governance_profile_hash: `{}`".format(_token(rows.get("governance_profile_hash"))),
        "- mock release remains usable under hash-mandatory, signature-optional policy.",
        "",
        "## Fork And Namespace Rules",
        "",
        "- Official tag example: `v0.0.0-mock`",
        "- Fork tag example: `fork.<org>.v0.0.0-mock`",
        "- Invalid unprefixed fork example is refused with `refusal.governance.fork_prefix_required`.",
        "",
        "## Archive Policy Summary",
        "",
        "- Primary archive plus at least one secondary mirror.",
        "- Offline cold storage recommended.",
        "- Release index must record the matching governance profile hash.",
        "",
        "## Readiness",
        "",
        "- PERFORMANCE-ENVELOPE-0: ready",
        "- ARCHIVE-POLICY-0: ready",
    ]
    if _as_list(rows.get("violations")):
        lines.extend(["", "## Open Violations", ""])
        for row in _as_list(rows.get("violations")):
            item = _as_map(row)
            lines.append("- `{}`: {}".format(_token(item.get("code")), _token(item.get("message"))))
    return "\n".join(lines) + "\n"


def write_governance_outputs(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    report = build_governance_model_report(root, platform_tag=platform_tag)
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_governance_baseline(report))
    report_json_path = _write_json(os.path.join(root, REPORT_JSON_REL), report)
    return {
        "report": report,
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
    }


def governance_model_violations(repo_root: str) -> list[dict]:
    return list(_as_list(_as_map(write_governance_outputs(repo_root).get("report")).get("violations")))


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "GOVERNANCE_PROFILE_SCHEMA_JSON_REL",
    "GOVERNANCE_PROFILE_SCHEMA_REL",
    "LICENSING_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_PROFILE",
    "TRUST_ROOT_DOC_REL",
    "build_governance_model_report",
    "governance_model_violations",
    "render_governance_baseline",
    "write_governance_outputs",
    "write_governance_registries",
]
