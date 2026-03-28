"""Deterministic RELEASE-INDEX-POLICY-0 helpers."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from typing import Mapping

from release import (
    DEFAULT_INSTALL_PROFILE_ID,
    DEFAULT_RELEASE_INDEX_REL,
    DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
    RESOLUTION_POLICY_EXACT_SUITE,
    RESOLUTION_POLICY_LAB,
    RESOLUTION_POLICY_LATEST_COMPATIBLE,
    append_install_transaction,
    canonicalize_component_descriptor,
    canonicalize_release_index,
    canonicalize_release_resolution_policy,
    load_install_profile_registry,
    load_install_transaction_log,
    load_release_index,
    resolve_update_plan,
    select_install_profile,
)
from tools.dist.dist_tree_common import build_dist_tree
from tools.release.update_model_common import build_release_index_payload
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "RELEASE_INDEX_POLICY0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "release", "RELEASE_INDEX_RESOLUTION_POLICY.md")
TAGGING_DOC_REL = os.path.join("docs", "release", "GIT_TAGGING_AND_RELEASE_POLICY.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "RELEASE_INDEX_POLICY_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "release_index_policy_report.json")
REGISTRY_REL = os.path.join("data", "registries", "release_resolution_policy_registry.json")
SCHEMA_REL = os.path.join("schema", "release", "release_resolution_policy.schema")
COMPILED_SCHEMA_REL = os.path.join("schemas", "release_resolution_policy.schema.json")
RULE_POLICY_DECLARED = "INV-RELEASE-INDEX-POLICY-DECLARED"
RULE_YANKED_EXCLUDED = "INV-YANKED-NOT-IN-LATEST_COMPAT"
RULE_ROLLBACK_RECORDED = "INV-ROLLBACK-TRANSACTION-RECORDED"
LAST_REVIEWED = "2026-03-14"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


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


def _stability(
    *,
    stability_class_id: str,
    rationale: str,
    future_series: str,
    replacement_target: str,
    contract_id: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": _token(stability_class_id),
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": _token(contract_id),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _policy_row(policy_id: str, selection_rule_id: str, allow_yanked: bool, *, cli_alias: str, description: str, stability: dict, requires_explicit_confirmation: bool = False) -> dict:
    row = canonicalize_release_resolution_policy(
        {
            "policy_id": policy_id,
            "selection_rule_id": selection_rule_id,
            "allow_yanked": bool(allow_yanked),
            "extensions": {
                "cli_alias": cli_alias,
                "description": description,
                "requires_explicit_confirmation": bool(requires_explicit_confirmation),
            },
        }
    )
    row["stability"] = dict(stability)
    return row


def build_release_resolution_policy_registry_payload() -> dict:
    rows = [
        _policy_row(
            RESOLUTION_POLICY_EXACT_SUITE,
            "selection.exact_suite_component_graph_pin",
            True,
            cli_alias="exact_suite",
            description="Select the suite-pinned descriptor for each selected component id.",
            stability=_stability(
                stability_class_id="stable",
                rationale="Exact-suite policy id is frozen for suite snapshot install, rollback, and archive semantics.",
                future_series="RELEASE-INDEX/UPDATE",
                replacement_target="Introduce a new policy id if suite-pinned semantics ever change.",
                contract_id="contract.release.resolution.exact_suite.v1",
            ),
        ),
        _policy_row(
            RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "selection.highest_semver_build_artifact",
            False,
            cli_alias="latest_compatible",
            description="Select the highest compatible non-yanked descriptor per component id.",
            stability=_stability(
                stability_class_id="stable",
                rationale="Latest-compatible policy id is frozen with deterministic tie-break semantics.",
                future_series="RELEASE-INDEX/UPDATE",
                replacement_target="Introduce a new policy id if deterministic latest-compatible ranking changes.",
                contract_id="contract.release.resolution.latest_compatible.v1",
            ),
        ),
        _policy_row(
            RESOLUTION_POLICY_LAB,
            "selection.latest_compatible_explicit_opt_in",
            True,
            cli_alias="lab",
            description="Select the highest compatible descriptor per component id, including experimental or yanked candidates only when explicitly requested.",
            stability=_stability(
                stability_class_id="provisional",
                rationale="Lab policy is intentionally opt-in and may evolve with experimental acquisition policy.",
                future_series="RELEASE-INDEX/LAB",
                replacement_target="Replace with a trust-governed experimental acquisition policy family when remote indices are formalized.",
            ),
            requires_explicit_confirmation=True,
        ),
    ]
    return {
        "schema_id": "dominium.registry.release_resolution_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.release_resolution_policy_registry",
            "registry_version": "1.0.0",
            "release_resolution_policies": rows,
            "extensions": {"official.source": "RELEASE-INDEX-POLICY0-2"},
        },
    }


def _bundle_root(repo_root: str, platform_tag: str) -> str:
    root = _norm(repo_root)
    candidates = [
        os.path.join(root, "dist", "v0.0.0-mock", platform_tag, "dominium"),
        os.path.join(root, "build", "tmp", "release_index_policy_dist", "v0.0.0-mock", platform_tag, "dominium"),
        os.path.join(root, "build", "tmp", "update_model_dist", "v0.0.0-mock", platform_tag, "dominium"),
        os.path.join(root, "build", "tmp", "update_model_test_dist", "v0.0.0-mock", platform_tag, "dominium"),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "install.manifest.json")):
            return candidate
    build_dist_tree(
        root,
        platform_tag=platform_tag,
        channel_id="mock",
        output_root=os.path.join(root, "build", "tmp", "release_index_policy_dist"),
        install_profile_id="install.profile.full",
    )
    return os.path.join(root, "build", "tmp", "release_index_policy_dist", "v0.0.0-mock", platform_tag, "dominium")


def _load_install_manifest(bundle_root: str) -> dict:
    with open(os.path.join(_norm(bundle_root), "install.manifest.json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


def _base_release_index(repo_root: str, *, platform_tag: str) -> tuple[str, dict, dict]:
    bundle_root = _bundle_root(repo_root, platform_tag)
    release_index_path = os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL)
    if os.path.isfile(release_index_path):
        release_index = load_release_index(release_index_path)
    else:
        release_index = build_release_index_payload(repo_root, dist_root=bundle_root, platform_tag=platform_tag)
    install_manifest = _load_install_manifest(bundle_root)
    return bundle_root, install_manifest, release_index


def _descriptor_variant(base_descriptor: Mapping[str, object], *, content_hash: str, version: str, build_id: str, artifact_id: str, yanked: bool = False, yank_reason: str = "", yank_policy: str = "warn") -> dict:
    base = canonicalize_component_descriptor(base_descriptor)
    extensions = dict(_as_map(base.get("extensions")))
    extensions["build_id"] = _token(build_id)
    extensions["artifact_id"] = _token(artifact_id)
    return canonicalize_component_descriptor(
        {
            **base,
            "content_hash": _token(content_hash).lower(),
            "version": _token(version),
            "yanked": bool(yanked),
            "yank_reason": _token(yank_reason),
            "yank_policy": _token(yank_policy),
            "extensions": extensions,
        }
    )


def _fixture_release_index(base_release_index: Mapping[str, object], *, exact_yanked: bool = False) -> dict:
    index = canonicalize_release_index(base_release_index)
    components = list(index.get("components") or [])
    base_client = {}
    for row in components:
        descriptor = canonicalize_component_descriptor(row)
        if _token(descriptor.get("component_id")) == "binary.client":
            base_client = descriptor
            break
    if not base_client:
        return index
    newer_valid = _descriptor_variant(
        base_client,
        content_hash="11" * 32,
        version="0.0.1",
        build_id="build.latest.compatible",
        artifact_id="artifact.binary.client.latest_compatible",
    )
    newer_yanked = _descriptor_variant(
        base_client,
        content_hash="22" * 32,
        version="0.0.2",
        build_id="build.latest.yanked",
        artifact_id="artifact.binary.client.yanked",
        yanked=True,
        yank_reason="bad regression in packaged client surface",
        yank_policy="warn",
    )
    base_variant = _descriptor_variant(
        base_client,
        content_hash=_token(base_client.get("content_hash")).lower(),
        version=_token(base_client.get("version")),
        build_id=_token(_as_map(base_client.get("extensions")).get("build_id")) or "build.exact.suite",
        artifact_id=_token(_as_map(base_client.get("extensions")).get("artifact_id")) or "artifact.binary.client.exact_suite",
        yanked=exact_yanked,
        yank_reason="suite-pinned rollback validation fixture" if exact_yanked else "",
        yank_policy="warn",
    )
    components = [row for row in components if _token(_as_map(row).get("component_id")) != "binary.client"]
    components.extend([base_variant, newer_valid, newer_yanked])
    return canonicalize_release_index({**index, "components": components})


def _resolve_fixture(repo_root: str, *, platform_tag: str, policy_id: str, release_index: Mapping[str, object]) -> dict:
    bundle_root, install_manifest, _base_index = _base_release_index(repo_root, platform_tag=platform_tag)
    platform_row = dict((list(release_index.get("platform_matrix") or [{}]) or [{}])[0])
    platform_extensions = _as_map(platform_row.get("extensions"))
    install_profile_id = _token(_as_map(install_manifest.get("extensions")).get("official.install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID
    install_profile_registry = load_install_profile_registry(bundle_root) or load_install_profile_registry(repo_root)
    install_profile = select_install_profile(install_profile_registry, install_profile_id=install_profile_id)
    return resolve_update_plan(
        install_manifest,
        release_index,
        install_profile_id=install_profile_id,
        install_profile=install_profile,
        resolution_policy_id=policy_id,
        target_platform=_token(platform_extensions.get("platform_id")) or _token(platform_row.get("os")),
        target_arch=_token(platform_row.get("arch")),
        target_abi=_token(platform_row.get("abi")),
        component_graph=dict(_as_map(release_index.get("extensions")).get("component_graph")),
        install_root=bundle_root,
        release_index_path=os.path.join(bundle_root, DEFAULT_RELEASE_INDEX_REL),
    )


def build_release_index_policy_fixture_cases(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    bundle_root, install_manifest, base_index = _base_release_index(root, platform_tag=platform_tag)
    latest_fixture = _fixture_release_index(base_index, exact_yanked=False)
    exact_fixture = _fixture_release_index(base_index, exact_yanked=True)
    return {
        "bundle_root": bundle_root,
        "install_manifest": install_manifest,
        "base_release_index": base_index,
        "latest_fixture_release_index": latest_fixture,
        "exact_fixture_release_index": exact_fixture,
        "latest_result": _resolve_fixture(
            root,
            platform_tag=platform_tag,
            policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
            release_index=latest_fixture,
        ),
        "exact_result": _resolve_fixture(
            root,
            platform_tag=platform_tag,
            policy_id=RESOLUTION_POLICY_EXACT_SUITE,
            release_index=exact_fixture,
        ),
        "lab_result": _resolve_fixture(
            root,
            platform_tag=platform_tag,
            policy_id=RESOLUTION_POLICY_LAB,
            release_index=latest_fixture,
        ),
        "rollback_transaction_fields": _rollback_fields_roundtrip(),
    }


def _git_tags(repo_root: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "tag", "--list"],
            cwd=_norm(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
    except OSError:
        return []
    return sorted(token.strip() for token in proc.stdout.splitlines() if token.strip())


def _changelog_files(repo_root: str) -> list[str]:
    root = _norm(repo_root)
    rels = []
    for rel_path in [
        "CHANGELOG.md",
        os.path.join("docs", "architecture", "CHANGELOG_ARCH.md"),
        os.path.join("docs", "engine", "CODE_1_CHANGELOG.md"),
    ]:
        abs_path = os.path.join(root, rel_path)
        if os.path.isfile(abs_path):
            rels.append(_norm_rel(rel_path))
    return sorted(rels)


def _rollback_fields_roundtrip() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, "install_transaction_log.json")
        append_install_transaction(
            log_path,
            {
                "transaction_id": "tx.release_index_policy",
                "action": "update.apply",
                "from_release_id": "release.old",
                "to_release_id": "release.new",
                "status": "complete",
                "backup_path": os.path.join(tmp, "backup"),
                "install_profile_id": "install.profile.full",
                "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
                "install_plan_hash": "33" * 32,
                "prior_component_set_hash": "44" * 32,
                "selected_component_ids": ["binary.client", "binary.setup"],
            },
        )
        payload = load_install_transaction_log(log_path)
        row = dict((list(payload.get("transactions") or [{}]) or [{}])[0])
        return {
            "resolution_policy_id": _token(row.get("resolution_policy_id")),
            "install_plan_hash": _token(row.get("install_plan_hash")),
            "prior_component_set_hash": _token(row.get("prior_component_set_hash")),
        }


def _selected_descriptor(plan: Mapping[str, object], component_id: str) -> dict:
    for row in list(_as_map(plan.get("extensions")).get("target_selected_component_descriptors") or []):
        descriptor = canonicalize_component_descriptor(row)
        if _token(descriptor.get("component_id")) == _token(component_id):
            return descriptor
    return canonicalize_component_descriptor({})


def _fixture_summary(cases: Mapping[str, object]) -> dict:
    latest_result = _as_map(cases.get("latest_result"))
    exact_result = _as_map(cases.get("exact_result"))
    lab_result = _as_map(cases.get("lab_result"))
    latest_plan = _as_map(latest_result.get("update_plan"))
    exact_plan = _as_map(exact_result.get("update_plan"))
    lab_plan = _as_map(lab_result.get("update_plan"))
    latest_client = _selected_descriptor(latest_plan, "binary.client")
    exact_client = _selected_descriptor(exact_plan, "binary.client")
    lab_client = _selected_descriptor(lab_plan, "binary.client")
    latest_policy_explanations = list(_as_map(latest_plan.get("extensions")).get("policy_explanations") or [])
    exact_warning_codes = sorted(
        {
            _token(_as_map(row).get("code"))
            for row in list(exact_result.get("warnings") or [])
            if _token(_as_map(row).get("code"))
        }
    )
    return {
        "latest_fixture": {
            "policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "selected_client_version": _token(latest_client.get("version")),
            "selected_client_build_id": _token(_as_map(latest_client.get("extensions")).get("build_id")),
            "selected_yanked_component_ids": list(_as_map(latest_plan.get("extensions")).get("selected_yanked_component_ids") or []),
            "skipped_yanked_count": int(
                sum(
                    1
                    for row in latest_policy_explanations
                    if _token(_as_map(row).get("event_id")) == "explain.component_skipped_yanked"
                )
            ),
            "plan_fingerprint": _token(latest_plan.get("deterministic_fingerprint")),
        },
        "exact_fixture": {
            "policy_id": RESOLUTION_POLICY_EXACT_SUITE,
            "selected_client_version": _token(exact_client.get("version")),
            "selected_client_build_id": _token(_as_map(exact_client.get("extensions")).get("build_id")),
            "selected_yanked_component_ids": list(_as_map(exact_plan.get("extensions")).get("selected_yanked_component_ids") or []),
            "warning_codes": exact_warning_codes,
            "plan_fingerprint": _token(exact_plan.get("deterministic_fingerprint")),
        },
        "lab_fixture": {
            "policy_id": RESOLUTION_POLICY_LAB,
            "selected_client_version": _token(lab_client.get("version")),
            "selected_client_build_id": _token(_as_map(lab_client.get("extensions")).get("build_id")),
            "selected_yanked_component_ids": list(_as_map(lab_plan.get("extensions")).get("selected_yanked_component_ids") or []),
            "plan_fingerprint": _token(lab_plan.get("deterministic_fingerprint")),
        },
        "rollback_transaction_fields": dict(cases.get("rollback_transaction_fields") or {}),
    }


def build_release_index_policy_report(repo_root: str, *, platform_tag: str = "win64") -> dict:
    root = _norm(repo_root)
    cases = build_release_index_policy_fixture_cases(root, platform_tag=platform_tag)
    bundle_root = _token(cases.get("bundle_root"))
    base_index = canonicalize_release_index(cases.get("base_release_index"))
    exact_fixture = canonicalize_release_index(cases.get("exact_fixture_release_index"))
    base_client = canonicalize_component_descriptor(
        next(
            (
                row
                for row in list(base_index.get("components") or [])
                if _token(_as_map(row).get("component_id")) == "binary.client"
            ),
            {},
        )
    )
    exact_pinned_client = canonicalize_component_descriptor(
        next(
            (
                row
                for row in list(exact_fixture.get("components") or [])
                if _token(_as_map(row).get("component_id")) == "binary.client"
                and _token(_as_map(row).get("content_hash")).lower() == _token(base_client.get("content_hash")).lower()
            ),
            {},
        )
    )
    policy_registry = build_release_resolution_policy_registry_payload()
    summary = _fixture_summary(cases)
    repeat_summary = _fixture_summary(build_release_index_policy_fixture_cases(root, platform_tag=platform_tag))
    violations = []
    if _token(_as_map(summary.get("latest_fixture")).get("selected_client_version")) != "0.0.1":
        violations.append({"code": "latest_not_highest_valid", "message": "latest-compatible did not select the highest valid non-yanked candidate"})
    if list(_as_map(summary.get("latest_fixture")).get("selected_yanked_component_ids") or []):
        violations.append({"code": "latest_selected_yanked", "message": "latest-compatible must not select yanked candidates when allow_yanked=false"})
    if int(_as_map(summary.get("latest_fixture")).get("skipped_yanked_count", 0) or 0) < 1:
        violations.append({"code": "yanked_skip_not_logged", "message": "latest-compatible must log skipped yanked candidates"})
    if _token(_as_map(summary.get("exact_fixture")).get("selected_client_build_id")) != _token(_as_map(exact_pinned_client.get("extensions")).get("build_id")):
        violations.append({"code": "exact_suite_not_pinned", "message": "exact-suite must keep the suite-pinned client descriptor even when newer candidates exist"})
    if "binary.client" not in list(_as_map(summary.get("exact_fixture")).get("selected_yanked_component_ids") or []):
        violations.append({"code": "exact_suite_yanked_not_visible", "message": "exact-suite must surface the selected yanked component id when the pinned descriptor is yanked"})
    if "warn.update.yanked_component" not in set(_as_map(summary.get("exact_fixture")).get("warning_codes") or []):
        violations.append({"code": "exact_suite_yanked_not_warned", "message": "exact-suite must warn when the pinned descriptor is yanked with yank_policy=warn"})
    rollback_fields = _as_map(summary.get("rollback_transaction_fields"))
    if _token(rollback_fields.get("resolution_policy_id")) != RESOLUTION_POLICY_LATEST_COMPATIBLE:
        violations.append({"code": "rollback_policy_not_recorded", "message": "transaction log must record resolution_policy_id"})
    if _token(rollback_fields.get("install_plan_hash")) != "33" * 32:
        violations.append({"code": "rollback_plan_hash_not_recorded", "message": "transaction log must record install_plan_hash"})
    if _token(rollback_fields.get("prior_component_set_hash")) != "44" * 32:
        violations.append({"code": "rollback_prior_set_hash_not_recorded", "message": "transaction log must record prior_component_set_hash"})
    if canonical_json_text(summary) != canonical_json_text(repeat_summary):
        violations.append({"code": "selection_nondeterministic", "message": "policy fixture resolution drifted across repeated identical runs"})
    report = {
        "report_id": "release.index_policy.v1",
        "result": "complete" if not violations else "refused",
        "platform_tag": _token(platform_tag),
        "bundle_root": _norm_rel(os.path.relpath(bundle_root, root)),
        "release_id": _token(_as_map(base_index.get("extensions")).get("release_id")),
        "default_resolution_policy_id": _token(_as_map(base_index.get("extensions")).get("release_resolution_policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
        "policy_registry_hash": canonical_sha256(policy_registry),
        "git_tags": _git_tags(root),
        "changelog_files": _changelog_files(root),
        "latest_fixture": dict(summary.get("latest_fixture") or {}),
        "exact_fixture": dict(summary.get("exact_fixture") or {}),
        "lab_fixture": dict(summary.get("lab_fixture") or {}),
        "rollback_transaction_fields": rollback_fields,
        "determinism_replay_match": canonical_json_text(summary) == canonical_json_text(repeat_summary),
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_release_index_policy_baseline(report: Mapping[str, object]) -> str:
    item = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: RELEASE-INDEX",
        "Replacement Target: signed suite and product evolution policy with explicit yanking and rollback governance",
        "",
        "# Release Index Policy Baseline",
        "",
        "## Resolution Policies Summary",
        "",
        "- default policy: `{}`".format(_token(item.get("default_resolution_policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID),
        "- latest-compatible fixture selected client version: `{}`".format(_token(_as_map(item.get("latest_fixture")).get("selected_client_version"))),
        "- exact-suite fixture selected client version: `{}`".format(_token(_as_map(item.get("exact_fixture")).get("selected_client_version"))),
        "",
        "## Yanking Behavior",
        "",
        "- latest-compatible skipped yanked candidates: `{}`".format(int(_as_map(item.get("latest_fixture")).get("skipped_yanked_count", 0) or 0)),
        "- exact-suite selected yanked components: `{}`".format(", ".join(list(_as_map(item.get("exact_fixture")).get("selected_yanked_component_ids") or [])) or "none"),
        "- exact-suite warning codes: `{}`".format(", ".join(list(_as_map(item.get("exact_fixture")).get("warning_codes") or [])) or "none"),
        "",
        "## Rollback Guarantees",
        "",
        "- recorded `resolution_policy_id`: `{}`".format(_token(_as_map(item.get("rollback_transaction_fields")).get("resolution_policy_id"))),
        "- recorded `install_plan_hash`: `{}`".format(_token(_as_map(item.get("rollback_transaction_fields")).get("install_plan_hash"))),
        "- recorded `prior_component_set_hash`: `{}`".format(_token(_as_map(item.get("rollback_transaction_fields")).get("prior_component_set_hash"))),
        "",
        "## Git Tagging Rules",
        "",
        "- suite tags follow `suite/vX.Y.Z-<channel>`",
        "- product tags are optional and product-specific",
        "- no tag rewriting",
        "- current repo tags observed during retro audit: `{}`".format(", ".join(list(item.get("git_tags") or [])) or "none"),
        "",
        "## Changelog Layering",
        "",
        "- discovered changelog files: `{}`".format(", ".join(list(item.get("changelog_files") or [])) or "none"),
        "- suite changelog remains `CHANGELOG.md`",
        "- release manifest remains the machine-readable version map",
        "",
        "## Readiness",
        "",
        "- long-term suite evolution: ready",
        "- yanked build governance: ready",
        "- deterministic rollback recording: ready",
        "",
        "## Report Fingerprints",
        "",
        "- policy registry hash: `{}`".format(_token(item.get("policy_registry_hash"))),
        "- report fingerprint: `{}`".format(_token(item.get("deterministic_fingerprint"))),
        "",
    ]
    return "\n".join(lines)


def write_release_index_policy_outputs(repo_root: str, *, platform_tag: str = "win64", write_registry: bool = False) -> dict:
    root = _norm(repo_root)
    registry_payload = build_release_resolution_policy_registry_payload()
    if write_registry:
        _write_json(os.path.join(root, REGISTRY_REL), registry_payload)
    report = build_release_index_policy_report(root, platform_tag=platform_tag)
    report_json_path = _write_json(os.path.join(root, REPORT_JSON_REL), report)
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_release_index_policy_baseline(report))
    return {
        "report": report,
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
    }


def release_index_policy_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "RELEASE-INDEX-POLICY-0 retro audit is required", RULE_POLICY_DECLARED),
        (DOCTRINE_DOC_REL, "release index resolution policy doctrine is required", RULE_POLICY_DECLARED),
        (TAGGING_DOC_REL, "git tagging and release policy doctrine is required", RULE_POLICY_DECLARED),
        (SCHEMA_REL, "release_resolution_policy schema is required", RULE_POLICY_DECLARED),
        (COMPILED_SCHEMA_REL, "compiled release_resolution_policy schema is required", RULE_POLICY_DECLARED),
        (REGISTRY_REL, "release resolution policy registry is required", RULE_POLICY_DECLARED),
        (BASELINE_DOC_REL, "release index policy baseline is required", RULE_POLICY_DECLARED),
        (REPORT_JSON_REL, "release index policy machine report is required", RULE_POLICY_DECLARED),
        (os.path.join("tools", "release", "release_index_policy_common.py"), "release-index policy helper is required", RULE_POLICY_DECLARED),
        (os.path.join("tools", "release", "tool_run_release_index_policy.py"), "release-index policy runner is required", RULE_POLICY_DECLARED),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": rel_path, "rule_id": rule_id})
    for rel_path, token, message, rule_id in (
        ("release/update_resolver.py", "resolution_policy_id", "update resolver must accept an explicit resolution policy id", RULE_POLICY_DECLARED),
        ("release/update_resolver.py", "explain.component_skipped_yanked", "latest-compatible resolution must log skipped yanked candidates", RULE_YANKED_EXCLUDED),
        ("release/update_resolver.py", "selected_yanked_component_ids", "selected yanked components must remain machine-visible", RULE_YANKED_EXCLUDED),
        ("tools/setup/setup_cli.py", "--policy", "setup install/update surfaces must expose policy selection", RULE_POLICY_DECLARED),
        ("tools/setup/setup_cli.py", "install_plan_hash", "update transactions must record install_plan_hash", RULE_ROLLBACK_RECORDED),
        ("tools/setup/setup_cli.py", "prior_component_set_hash", "update transactions must record prior_component_set_hash", RULE_ROLLBACK_RECORDED),
        ("tools/launcher/launch.py", "selected_yanked_component_ids", "launcher status surfaces must expose yanked selection state", RULE_YANKED_EXCLUDED),
    ):
        try:
            with open(os.path.join(root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            text = ""
        if token in text:
            continue
        violations.append({"code": "missing_integration_hook", "message": message, "file_path": rel_path, "rule_id": rule_id})
    try:
        report = build_release_index_policy_report(root)
    except Exception as exc:
        violations.append({"code": "release_index_policy_report_failed", "message": "unable to build release-index policy report ({})".format(str(exc)), "file_path": REPORT_JSON_REL, "rule_id": RULE_POLICY_DECLARED})
        return violations
    if _token(report.get("result")) != "complete":
        for row in list(report.get("violations") or []):
            item = _as_map(row)
            violations.append(
                {
                    "code": _token(item.get("code")) or "release_index_policy_refused",
                    "message": _token(item.get("message")) or "release-index policy report refused",
                    "file_path": REPORT_JSON_REL,
                    "rule_id": RULE_POLICY_DECLARED,
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
    "RULE_POLICY_DECLARED",
    "RULE_ROLLBACK_RECORDED",
    "RULE_YANKED_EXCLUDED",
    "TAGGING_DOC_REL",
    "build_release_index_policy_fixture_cases",
    "build_release_index_policy_report",
    "build_release_resolution_policy_registry_payload",
    "release_index_policy_violations",
    "render_release_index_policy_baseline",
    "write_release_index_policy_outputs",
]
