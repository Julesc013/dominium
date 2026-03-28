"""Deterministic offline update-channel simulation helpers for Omega MVP freezes."""

from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from meta.identity import UNIVERSAL_IDENTITY_FIELD  # noqa: E402
from release import (  # noqa: E402
    DEFAULT_INSTALL_PROFILE_ID,
    RESOLUTION_POLICY_EXACT_SUITE,
    RESOLUTION_POLICY_LATEST_COMPATIBLE,
    append_install_transaction,
    canonicalize_component_descriptor,
    canonicalize_release_index,
    load_install_profile_registry,
    load_release_index,
    load_release_resolution_policy_registry,
    platform_targets_for_tag,
    resolve_update_plan,
    select_install_profile,
    select_release_resolution_policy,
    select_rollback_transaction,
)
from security.trust import (  # noqa: E402
    DEFAULT_TRUST_POLICY_ID,
    REFUSAL_TRUST_SIGNATURE_MISSING,
    TRUST_POLICY_STRICT,
    load_trust_policy_registry,
    load_trust_root_registry,
    select_trust_policy,
)
from tools.release.release_index_policy_common import build_release_index_policy_fixture_cases  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


UPDATE_SIM_RUN_SCHEMA_ID = "dominium.schema.audit.update_sim_run"
UPDATE_SIM_BASELINE_SCHEMA_ID = "dominium.schema.governance.update_sim_baseline"
UPDATE_SIM_VERSION = 0
UPDATE_SIM_STABILITY_CLASS = "stable"

UPDATE_SIM_RETRO_AUDIT_REL = os.path.join("docs", "audit", "UPDATE_SIM0_RETRO_AUDIT.md")
UPDATE_SIM_MODEL_DOC_REL = os.path.join("docs", "release", "UPDATE_SIM_MODEL_v0_0_0.md")
UPDATE_SIM_FIXTURE_DIR_REL = os.path.join("data", "baselines", "update_sim")
UPDATE_SIM_BASELINE_INDEX_REL = os.path.join(UPDATE_SIM_FIXTURE_DIR_REL, "release_index_baseline.json")
UPDATE_SIM_UPGRADE_INDEX_REL = os.path.join(UPDATE_SIM_FIXTURE_DIR_REL, "release_index_upgrade.json")
UPDATE_SIM_YANKED_INDEX_REL = os.path.join(UPDATE_SIM_FIXTURE_DIR_REL, "release_index_yanked.json")
UPDATE_SIM_STRICT_INDEX_REL = os.path.join(UPDATE_SIM_FIXTURE_DIR_REL, "release_index_strict.json")
UPDATE_SIM_RUN_JSON_REL = os.path.join("data", "audit", "update_sim_run.json")
UPDATE_SIM_RUN_DOC_REL = os.path.join("docs", "audit", "UPDATE_SIM_RUN.md")
UPDATE_SIM_BASELINE_REL = os.path.join("data", "regression", "update_sim_baseline.json")
UPDATE_SIM_BASELINE_DOC_REL = os.path.join("docs", "audit", "UPDATE_SIM_BASELINE.md")
UPDATE_SIM_TOOL_REL = os.path.join("tools", "mvp", "tool_run_update_sim")
UPDATE_SIM_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_run_update_sim.py")
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_DIST_ROOT_REL = os.path.join("dist", "v0.0.0-mock", DEFAULT_PLATFORM_TAG, "dominium")
DEFAULT_INSTALL_MANIFEST_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "install.manifest.json")
DEFAULT_WORK_ROOT_REL = os.path.join("build", "tmp", "omega6_update_sim")
UPDATE_SIM_REGRESSION_REQUIRED_TAG = "UPDATE-SIM-REGRESSION-UPDATE"

_FIXTURE_PATHS = {
    "baseline": UPDATE_SIM_BASELINE_INDEX_REL,
    "upgrade": UPDATE_SIM_UPGRADE_INDEX_REL,
    "yanked": UPDATE_SIM_YANKED_INDEX_REL,
    "strict": UPDATE_SIM_STRICT_INDEX_REL,
}


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
        shutil.rmtree(token)


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


def _record_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def update_sim_report_hash(report: Mapping[str, object]) -> str:
    return _record_hash(report)


def update_sim_baseline_hash(payload: Mapping[str, object]) -> str:
    return _record_hash(payload)


def load_update_sim_report(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or UPDATE_SIM_RUN_JSON_REL))


def load_update_sim_baseline(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or UPDATE_SIM_BASELINE_REL))


def _artifact_input_summary(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    payload = _load_json(abs_path)
    return {
        "path": _relative_to(repo_root, abs_path),
        "exists": os.path.isfile(abs_path),
        "content_hash": canonical_sha256(payload) if payload else "",
    }


def _fixture_artifact_rel(repo_root: str) -> str:
    fixture_dir = _repo_abs(repo_root, UPDATE_SIM_FIXTURE_DIR_REL)
    dist_root = _repo_abs(repo_root, DEFAULT_DIST_ROOT_REL)
    return _norm(os.path.relpath(dist_root, fixture_dir))


def _strip_identity_and_fix_paths(index: Mapping[str, object], *, artifact_rel: str, release_id: str, fixture_id: str) -> dict:
    payload = dict(index or {})
    payload.pop(UNIVERSAL_IDENTITY_FIELD, None)
    payload["signatures"] = []
    platform_rows = []
    for row in _as_list(payload.get("platform_matrix")):
        item = dict(_as_map(row))
        item["artifact_url_or_path"] = _norm(artifact_rel)
        platform_rows.append(item)
    payload["platform_matrix"] = platform_rows
    extensions = dict(_as_map(payload.get("extensions")))
    extensions["release_id"] = _token(release_id)
    extensions["official.source"] = "OMEGA-6"
    extensions["official.fixture_id"] = _token(fixture_id)
    payload["extensions"] = extensions
    return canonicalize_release_index(payload)


def _drop_yanked_candidates(index: Mapping[str, object]) -> dict:
    payload = dict(index or {})
    payload["components"] = [
        row
        for row in _as_list(payload.get("components"))
        if not (
            _token(_as_map(row).get("component_id")) == "binary.client"
            and bool(_as_map(row).get("yanked"))
        )
    ]
    return canonicalize_release_index(payload)


def build_update_sim_fixture_payloads(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    artifact_rel = _fixture_artifact_rel(root)
    cases = build_release_index_policy_fixture_cases(root, platform_tag=platform_tag)
    base = canonicalize_release_index(cases.get("base_release_index"))
    latest = canonicalize_release_index(cases.get("latest_fixture_release_index"))
    base_release_id = _token(_as_map(base.get("extensions")).get("release_id")) or "release.v0.0.0-mock"
    upgrade = _drop_yanked_candidates(latest)
    return {
        "baseline": _strip_identity_and_fix_paths(
            base,
            artifact_rel=artifact_rel,
            release_id=base_release_id,
            fixture_id="baseline",
        ),
        "upgrade": _strip_identity_and_fix_paths(
            upgrade,
            artifact_rel=artifact_rel,
            release_id="{}.upgrade_fixture".format(base_release_id),
            fixture_id="upgrade",
        ),
        "yanked": _strip_identity_and_fix_paths(
            latest,
            artifact_rel=artifact_rel,
            release_id="{}.yanked_fixture".format(base_release_id),
            fixture_id="yanked",
        ),
        "strict": _strip_identity_and_fix_paths(
            upgrade,
            artifact_rel=artifact_rel,
            release_id="{}.strict_fixture".format(base_release_id),
            fixture_id="strict",
        ),
    }


def write_update_sim_fixture_outputs(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    payloads = build_update_sim_fixture_payloads(root, platform_tag=platform_tag)
    written = {}
    for fixture_id, rel_path in sorted(_FIXTURE_PATHS.items()):
        written[fixture_id] = _write_canonical_json(_repo_abs(root, rel_path), _as_map(payloads.get(fixture_id)))
    return {"fixtures": payloads, "written": written}


def load_update_sim_fixtures(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        fixture_id: load_release_index(_repo_abs(root, rel_path))
        for fixture_id, rel_path in sorted(_FIXTURE_PATHS.items())
    }


def _current_install_manifest(repo_root: str) -> dict:
    return _load_json(_repo_abs(repo_root, DEFAULT_INSTALL_MANIFEST_REL))


def _install_profile_id(current_manifest: Mapping[str, object]) -> str:
    extensions = _as_map(current_manifest.get("extensions"))
    return _token(extensions.get("official.install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID


def _resolved_install_profile(repo_root: str, install_profile_id: str) -> dict:
    registry = load_install_profile_registry(repo_root)
    return select_install_profile(registry, install_profile_id=install_profile_id)


def _resolved_policy(repo_root: str, policy_id: str) -> dict:
    registry = load_release_resolution_policy_registry(repo_root)
    return select_release_resolution_policy(registry, policy_id=policy_id)


def _trust_bundle(repo_root: str, trust_policy_id: str) -> tuple[str, dict, list[dict]]:
    registry = load_trust_policy_registry(repo_root=repo_root)
    selected_id = _token(trust_policy_id) or DEFAULT_TRUST_POLICY_ID
    policy = select_trust_policy(registry, trust_policy_id=selected_id)
    roots = _as_list(_as_map(load_trust_root_registry(repo_root=repo_root).get("record")).get("trust_roots"))
    return selected_id, policy, [dict(row) for row in roots if isinstance(row, Mapping)]


def _resolve_fixture(
    repo_root: str,
    current_manifest: Mapping[str, object],
    fixture_payload: Mapping[str, object],
    *,
    fixture_rel_path: str,
    policy_id: str,
    trust_policy_id: str,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    install_profile_id = _install_profile_id(current_manifest)
    install_profile = _resolved_install_profile(root, install_profile_id)
    resolution_policy = _resolved_policy(root, policy_id)
    effective_trust_policy_id, trust_policy, trust_roots = _trust_bundle(root, trust_policy_id)
    target = dict(platform_targets_for_tag(DEFAULT_PLATFORM_TAG, repo_root=root) or {})
    return dict(
        resolve_update_plan(
            current_manifest,
            fixture_payload,
            install_profile_id=install_profile_id,
            install_profile=install_profile,
            resolution_policy_id=policy_id,
            resolution_policy=resolution_policy,
            target_platform=_token(target.get("platform_id")),
            target_arch=_token(target.get("arch_id")),
            target_abi=_token(target.get("abi_id")),
            component_graph=_as_map(_as_map(fixture_payload.get("extensions")).get("component_graph")),
            trust_policy=trust_policy,
            trust_policy_id=effective_trust_policy_id,
            trust_roots=trust_roots,
            install_root=_repo_abs(root, DEFAULT_DIST_ROOT_REL),
            release_index_path=_repo_abs(root, fixture_rel_path),
        )
        or {}
    )


def _repeat_resolution(
    repo_root: str,
    current_manifest: Mapping[str, object],
    fixture_payload: Mapping[str, object],
    *,
    fixture_rel_path: str,
    policy_id: str,
    trust_policy_id: str,
) -> tuple[dict, bool]:
    first = _resolve_fixture(
        repo_root,
        current_manifest,
        fixture_payload,
        fixture_rel_path=fixture_rel_path,
        policy_id=policy_id,
        trust_policy_id=trust_policy_id,
    )
    second = _resolve_fixture(
        repo_root,
        current_manifest,
        fixture_payload,
        fixture_rel_path=fixture_rel_path,
        policy_id=policy_id,
        trust_policy_id=trust_policy_id,
    )
    return first, canonical_json_text(first) == canonical_json_text(second)


def _plan_extensions(plan: Mapping[str, object]) -> dict:
    return _as_map(_as_map(plan).get("extensions"))


def _scenario_codes(resolution: Mapping[str, object], key: str) -> list[str]:
    return sorted(
        {
            _token(_as_map(row).get("code"))
            for row in _as_list(_as_map(resolution).get(key))
            if _token(_as_map(row).get("code"))
        }
    )


def _selected_descriptor(plan: Mapping[str, object], component_id: str) -> dict:
    for row in _as_list(_plan_extensions(plan).get("target_selected_component_descriptors")):
        descriptor = canonicalize_component_descriptor(row)
        if _token(descriptor.get("component_id")) == _token(component_id):
            return descriptor
    return {}


def _skipped_yanked_count(plan: Mapping[str, object]) -> int:
    return int(
        sum(
            1
            for row in _as_list(_plan_extensions(plan).get("policy_explanations"))
            if _token(_as_map(row).get("event_id")) == "explain.component_skipped_yanked"
        )
    )


def _release_id_of_current_manifest(current_manifest: Mapping[str, object]) -> str:
    return _token(_as_map(_as_map(current_manifest).get("extensions")).get("official.release_id"))


def _state_payload(*, release_id: str, component_set_hash: str, selected_component_descriptors: list[dict]) -> dict:
    rows = [dict(item) for item in selected_component_descriptors]
    return {
        "release_id": _token(release_id),
        "component_set_hash": _token(component_set_hash),
        "selected_component_descriptors": rows,
        "deterministic_fingerprint": canonical_sha256(
            {
                "release_id": _token(release_id),
                "component_set_hash": _token(component_set_hash),
                "selected_component_descriptors": rows,
            }
        ),
    }


def _managed_paths_available(repo_root: str, descriptor_rows: list[dict]) -> tuple[bool, list[str]]:
    dist_root = _repo_abs(repo_root, DEFAULT_DIST_ROOT_REL)
    missing = []
    for row in descriptor_rows:
        item = canonicalize_component_descriptor(row)
        for rel_path in _as_list(_as_map(item.get("extensions")).get("managed_paths")):
            rel_token = _token(rel_path)
            if not rel_token:
                continue
            abs_path = os.path.join(dist_root, rel_token.replace("/", os.sep))
            if not os.path.exists(abs_path):
                missing.append(_norm(rel_token))
    return not missing, sorted(set(missing))


def build_update_sim_baseline(report: Mapping[str, object]) -> dict:
    payload = _as_map(report)
    baseline = _as_map(payload.get("baseline_install"))
    upgrade = _as_map(payload.get("latest_compatible_upgrade"))
    yanked = _as_map(payload.get("yanked_candidate_exclusion"))
    strict = _as_map(payload.get("strict_trust_refusal"))
    rollback = _as_map(payload.get("rollback_restore"))
    baseline_result = "complete"
    for row in (baseline, upgrade, yanked, strict, rollback):
        if _token(_as_map(row).get("result")) != "complete":
            baseline_result = "refused"
            break
    out = {
        "schema_id": UPDATE_SIM_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "baseline_id": "update_sim.baseline.v0_0_0",
        "update_sim_version": UPDATE_SIM_VERSION,
        "stability_class": UPDATE_SIM_STABILITY_CLASS,
        "result": baseline_result,
        "scenario_order": list(_as_list(payload.get("scenario_order"))),
        "plan_hashes": {
            "baseline_plan_fingerprint": _token(baseline.get("plan_fingerprint")),
            "upgrade_plan_fingerprint": _token(upgrade.get("plan_fingerprint")),
            "yanked_plan_fingerprint": _token(yanked.get("plan_fingerprint")),
        },
        "baseline_install": {
            "release_id": _token(baseline.get("release_id")),
            "component_set_hash": _token(baseline.get("component_set_hash")),
            "selected_component_ids": list(_as_list(baseline.get("selected_component_ids"))),
        },
        "upgrade_result": {
            "release_id": _token(upgrade.get("target_release_id")),
            "upgraded_component_ids": list(_as_list(upgrade.get("upgraded_component_ids"))),
            "installed_component_set_hash": _token(upgrade.get("installed_component_set_hash")),
        },
        "yanked_exclusion": {
            "selected_client_version": _token(yanked.get("selected_client_version")),
            "selected_yanked_component_ids": list(_as_list(yanked.get("selected_yanked_component_ids"))),
            "skipped_yanked_count": int(yanked.get("skipped_yanked_count", 0) or 0),
        },
        "strict_trust": {
            "refusal_code": _token(strict.get("refusal_code")),
            "trust_policy_id": _token(strict.get("trust_policy_id")),
        },
        "rollback": {
            "rollback_transaction_id": _token(rollback.get("rollback_transaction_id")),
            "restored_component_set_hash": _token(rollback.get("restored_component_set_hash")),
            "baseline_component_set_hash": _token(rollback.get("baseline_component_set_hash")),
            "rollback_matches_baseline": bool(rollback.get("rollback_matches_baseline")),
        },
        "update_policy": {"required_commit_tag": UPDATE_SIM_REGRESSION_REQUIRED_TAG},
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = update_sim_baseline_hash(out)
    return out


def _baseline_comparison(report: Mapping[str, object], committed_baseline: Mapping[str, object]) -> dict:
    expected = build_update_sim_baseline(report)
    current = _as_map(committed_baseline)
    if not current:
        return {
            "baseline_present": False,
            "baseline_matches": False,
            "expected_baseline_fingerprint": _token(expected.get("deterministic_fingerprint")),
            "committed_baseline_fingerprint": "",
        }
    return {
        "baseline_present": True,
        "baseline_matches": canonical_json_text(expected) == canonical_json_text(current),
        "expected_baseline_fingerprint": _token(expected.get("deterministic_fingerprint")),
        "committed_baseline_fingerprint": _token(current.get("deterministic_fingerprint")),
    }


def run_update_sim(
    repo_root: str,
    *,
    output_root_rel: str = "",
    write_outputs: bool = True,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    work_root = _repo_abs(root, output_root_rel or DEFAULT_WORK_ROOT_REL)
    _safe_rmtree(work_root)
    _ensure_dir(work_root)

    current_manifest = _current_install_manifest(root)
    fixtures = load_update_sim_fixtures(root)

    baseline_resolution, baseline_repeat_match = _repeat_resolution(
        root,
        current_manifest,
        _as_map(fixtures.get("baseline")),
        fixture_rel_path=_FIXTURE_PATHS["baseline"],
        policy_id=RESOLUTION_POLICY_EXACT_SUITE,
        trust_policy_id=DEFAULT_TRUST_POLICY_ID,
    )
    baseline_plan = _as_map(baseline_resolution.get("update_plan"))
    baseline_ext = _plan_extensions(baseline_plan)
    baseline_state = _state_payload(
        release_id=_token(baseline_plan.get("to_release_id")) or _release_id_of_current_manifest(current_manifest),
        component_set_hash=_token(baseline_ext.get("target_component_set_hash")),
        selected_component_descriptors=[dict(item) for item in _as_list(baseline_ext.get("target_selected_component_descriptors"))],
    )
    baseline_manifest = dict(current_manifest)
    baseline_manifest_extensions = dict(_as_map(current_manifest.get("extensions")))
    baseline_manifest_extensions["official.release_id"] = _token(baseline_state.get("release_id"))
    baseline_manifest_extensions["official.selected_component_ids"] = list(_as_list(baseline_ext.get("target_selected_component_ids")))
    baseline_manifest_extensions["official.selected_component_descriptors"] = [
        dict(item) for item in _as_list(baseline_ext.get("target_selected_component_descriptors"))
    ]
    baseline_manifest["extensions"] = baseline_manifest_extensions
    baseline_state_path = _write_canonical_json(os.path.join(work_root, "state", "baseline_state.json"), baseline_state)
    install_state_path = _write_canonical_json(os.path.join(work_root, "state", "install_state.json"), baseline_state)

    upgrade_resolution, upgrade_repeat_match = _repeat_resolution(
        root,
        baseline_manifest,
        _as_map(fixtures.get("upgrade")),
        fixture_rel_path=_FIXTURE_PATHS["upgrade"],
        policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
        trust_policy_id=DEFAULT_TRUST_POLICY_ID,
    )
    upgrade_plan = _as_map(upgrade_resolution.get("update_plan"))
    upgrade_ext = _plan_extensions(upgrade_plan)
    upgrade_client = _selected_descriptor(upgrade_plan, "binary.client")
    upgraded_component_ids = sorted(
        {
            _token(_as_map(row).get("component_id"))
            for row in _as_list(upgrade_plan.get("components_to_upgrade"))
            if _token(_as_map(row).get("component_id"))
        }
    )
    artifact_ok, missing_paths = _managed_paths_available(
        root,
        [
            dict(item)
            for item in _as_list(upgrade_ext.get("target_selected_component_descriptors"))
            if _token(_as_map(item).get("component_id")) in set(upgraded_component_ids)
        ],
    )
    upgraded_state = _state_payload(
        release_id=_token(upgrade_plan.get("to_release_id")),
        component_set_hash=_token(upgrade_ext.get("target_component_set_hash")),
        selected_component_descriptors=[dict(item) for item in _as_list(upgrade_ext.get("target_selected_component_descriptors"))],
    )
    transaction_log_path = os.path.join(work_root, "install_root", ".dsu", "install_transaction_log.json")
    install_after_apply_path = ""
    if _token(upgrade_resolution.get("result")) == "complete" and bool(upgrade_ext.get("update_required")) and artifact_ok:
        install_after_apply_path = _write_canonical_json(install_state_path, upgraded_state)
        append_install_transaction(
            transaction_log_path,
            {
                "transaction_id": "tx.update_sim.apply",
                "action": "update.apply",
                "from_release_id": _token(baseline_state.get("release_id")),
                "to_release_id": _token(upgraded_state.get("release_id")),
                "backup_path": baseline_state_path,
                "status": "complete",
                "install_profile_id": _install_profile_id(baseline_manifest),
                "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
                "install_plan_hash": _token(upgrade_plan.get("deterministic_fingerprint")),
                "prior_component_set_hash": _token(upgrade_ext.get("prior_component_set_hash")),
                "selected_component_ids": list(_as_list(upgrade_ext.get("target_selected_component_ids"))),
            },
        )

    yanked_resolution, yanked_repeat_match = _repeat_resolution(
        root,
        baseline_manifest,
        _as_map(fixtures.get("yanked")),
        fixture_rel_path=_FIXTURE_PATHS["yanked"],
        policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
        trust_policy_id=DEFAULT_TRUST_POLICY_ID,
    )
    yanked_plan = _as_map(yanked_resolution.get("update_plan"))
    yanked_ext = _plan_extensions(yanked_plan)
    yanked_client = _selected_descriptor(yanked_plan, "binary.client")

    strict_resolution, strict_repeat_match = _repeat_resolution(
        root,
        baseline_manifest,
        _as_map(fixtures.get("strict")),
        fixture_rel_path=_FIXTURE_PATHS["strict"],
        policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
        trust_policy_id=TRUST_POLICY_STRICT,
    )
    strict_errors = _as_list(strict_resolution.get("errors"))
    strict_refusal_code = _token(strict_resolution.get("refusal_code")) or (
        _token(_as_map(strict_errors[0]).get("code")) if strict_errors else ""
    )

    rollback_row = select_rollback_transaction(
        transaction_log_path,
        to_release_id=_token(baseline_state.get("release_id")),
    )
    restored_state = {}
    rollback_transaction_id = ""
    restored_state_path = ""
    if rollback_row and os.path.isfile(_token(rollback_row.get("backup_path"))):
        restored_state = _load_json(_token(rollback_row.get("backup_path")))
        restored_state_path = _write_canonical_json(install_state_path, restored_state)
        rollback_transaction_id = "tx.update_sim.rollback"
        append_install_transaction(
            transaction_log_path,
            {
                "transaction_id": rollback_transaction_id,
                "action": "update.rollback",
                "from_release_id": _token(upgraded_state.get("release_id")),
                "to_release_id": _token(baseline_state.get("release_id")),
                "backup_path": _token(rollback_row.get("backup_path")),
                "status": "complete",
                "install_profile_id": _install_profile_id(baseline_manifest),
                "resolution_policy_id": _token(rollback_row.get("resolution_policy_id")) or RESOLUTION_POLICY_LATEST_COMPATIBLE,
                "install_plan_hash": _token(rollback_row.get("install_plan_hash")),
                "prior_component_set_hash": _token(rollback_row.get("prior_component_set_hash")),
                "selected_component_ids": list(_as_list(rollback_row.get("selected_component_ids"))),
            },
        )

    baseline_ok = _token(baseline_resolution.get("result")) == "complete" and baseline_repeat_match and bool(_token(baseline_state.get("component_set_hash")))
    upgrade_ok = (
        _token(upgrade_resolution.get("result")) == "complete"
        and bool(upgrade_ext.get("update_required"))
        and upgrade_repeat_match
        and artifact_ok
        and _token(upgraded_state.get("component_set_hash")) == _token(upgrade_ext.get("target_component_set_hash"))
    )
    yanked_ok = (
        _token(yanked_resolution.get("result")) == "complete"
        and yanked_repeat_match
        and not list(_as_list(yanked_ext.get("selected_yanked_component_ids")))
        and _skipped_yanked_count(yanked_plan) >= 1
        and _token(upgrade_client.get("version")) == _token(yanked_client.get("version"))
    )
    strict_ok = (
        _token(strict_resolution.get("result")) == "refused"
        and strict_repeat_match
        and strict_refusal_code in {REFUSAL_TRUST_SIGNATURE_MISSING, "refusal.update.trust_unmet"}
    )
    rollback_matches_baseline = canonical_json_text(restored_state) == canonical_json_text(baseline_state) if restored_state else False
    rollback_ok = bool(rollback_row) and rollback_matches_baseline

    report = {
        "schema_id": UPDATE_SIM_RUN_SCHEMA_ID,
        "schema_version": "1.0.0",
        "update_sim_version": UPDATE_SIM_VERSION,
        "stability_class": UPDATE_SIM_STABILITY_CLASS,
        "result": "complete" if all((baseline_ok, upgrade_ok, yanked_ok, strict_ok, rollback_ok)) else "refused",
        "platform_tag": DEFAULT_PLATFORM_TAG,
        "scenario_order": ["baseline_install", "latest_compatible_upgrade", "yanked_candidate_exclusion", "strict_trust_refusal", "rollback_restore"],
        "input_artifacts": {
            "install_manifest": _artifact_input_summary(root, DEFAULT_INSTALL_MANIFEST_REL),
            "release_index_baseline": _artifact_input_summary(root, _FIXTURE_PATHS["baseline"]),
            "release_index_upgrade": _artifact_input_summary(root, _FIXTURE_PATHS["upgrade"]),
            "release_index_yanked": _artifact_input_summary(root, _FIXTURE_PATHS["yanked"]),
            "release_index_strict": _artifact_input_summary(root, _FIXTURE_PATHS["strict"]),
        },
        "baseline_install": {
            "result": "complete" if baseline_ok else "refused",
            "resolution_result": _token(baseline_resolution.get("result")),
            "resolution_policy_id": RESOLUTION_POLICY_EXACT_SUITE,
            "trust_policy_id": DEFAULT_TRUST_POLICY_ID,
            "release_id": _token(baseline_state.get("release_id")),
            "plan_fingerprint": _token(baseline_plan.get("deterministic_fingerprint")),
            "component_set_hash": _token(baseline_state.get("component_set_hash")),
            "selected_component_ids": list(_as_list(baseline_ext.get("target_selected_component_ids"))),
            "update_required": bool(baseline_ext.get("update_required")),
            "deterministic_replay_match": baseline_repeat_match,
            "warning_codes": _scenario_codes(baseline_resolution, "warnings"),
            "error_codes": _scenario_codes(baseline_resolution, "errors"),
        },
        "latest_compatible_upgrade": {
            "result": "complete" if upgrade_ok else "refused",
            "resolution_result": _token(upgrade_resolution.get("result")),
            "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "trust_policy_id": DEFAULT_TRUST_POLICY_ID,
            "from_release_id": _token(upgrade_plan.get("from_release_id")),
            "target_release_id": _token(upgrade_plan.get("to_release_id")),
            "plan_fingerprint": _token(upgrade_plan.get("deterministic_fingerprint")),
            "selected_client_version": _token(upgrade_client.get("version")),
            "selected_client_build_id": _token(_as_map(upgrade_client.get("extensions")).get("build_id")),
            "upgraded_component_ids": upgraded_component_ids,
            "artifact_availability_ok": artifact_ok,
            "missing_artifact_paths": missing_paths,
            "installed_component_set_hash": _token(upgraded_state.get("component_set_hash")),
            "target_component_set_hash": _token(upgrade_ext.get("target_component_set_hash")),
            "prior_component_set_hash": _token(upgrade_ext.get("prior_component_set_hash")),
            "update_required": bool(upgrade_ext.get("update_required")),
            "deterministic_replay_match": upgrade_repeat_match,
            "warning_codes": _scenario_codes(upgrade_resolution, "warnings"),
            "error_codes": _scenario_codes(upgrade_resolution, "errors"),
        },
        "yanked_candidate_exclusion": {
            "result": "complete" if yanked_ok else "refused",
            "resolution_result": _token(yanked_resolution.get("result")),
            "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "trust_policy_id": DEFAULT_TRUST_POLICY_ID,
            "target_release_id": _token(yanked_plan.get("to_release_id")),
            "plan_fingerprint": _token(yanked_plan.get("deterministic_fingerprint")),
            "selected_client_version": _token(yanked_client.get("version")),
            "selected_client_build_id": _token(_as_map(yanked_client.get("extensions")).get("build_id")),
            "selected_yanked_component_ids": list(_as_list(yanked_ext.get("selected_yanked_component_ids"))),
            "skipped_yanked_count": _skipped_yanked_count(yanked_plan),
            "deterministic_replay_match": yanked_repeat_match,
            "warning_codes": _scenario_codes(yanked_resolution, "warnings"),
            "error_codes": _scenario_codes(yanked_resolution, "errors"),
        },
        "strict_trust_refusal": {
            "result": "complete" if strict_ok else "refused",
            "resolution_result": _token(strict_resolution.get("result")),
            "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "trust_policy_id": TRUST_POLICY_STRICT,
            "refusal_code": strict_refusal_code,
            "deterministic_replay_match": strict_repeat_match,
            "warning_codes": _scenario_codes(strict_resolution, "warnings"),
            "error_codes": _scenario_codes(strict_resolution, "errors"),
        },
        "rollback_restore": {
            "result": "complete" if rollback_ok else "refused",
            "rollback_transaction_selected": bool(rollback_row),
            "rollback_transaction_id": rollback_transaction_id,
            "baseline_component_set_hash": _token(baseline_state.get("component_set_hash")),
            "upgraded_component_set_hash": _token(upgraded_state.get("component_set_hash")),
            "restored_component_set_hash": _token(_as_map(restored_state).get("component_set_hash")),
            "rollback_matches_baseline": rollback_matches_baseline,
            "install_plan_hash": _token(_as_map(rollback_row).get("install_plan_hash")),
            "prior_component_set_hash": _token(_as_map(rollback_row).get("prior_component_set_hash")),
        },
        "transaction_log_rel": ".dsu/install_transaction_log.json",
        "simulation_state_files": {
            "baseline_state": "baseline_state.json",
            "install_state": "install_state.json",
            "restored_state": "install_state.json" if restored_state_path else "",
        },
        "verification_hashes": {
            "baseline_install_hash": canonical_sha256(_as_map(baseline_resolution)),
            "upgrade_resolution_hash": canonical_sha256(_as_map(upgrade_resolution)),
            "yanked_resolution_hash": canonical_sha256(_as_map(yanked_resolution)),
            "strict_resolution_hash": canonical_sha256(_as_map(strict_resolution)),
            "rollback_state_hash": canonical_sha256(_as_map(restored_state)),
        },
        "deterministic_fingerprint": "",
    }
    report["baseline_comparison"] = _baseline_comparison(report, load_update_sim_baseline(root))
    if bool(_as_map(report.get("baseline_comparison")).get("baseline_present")) and not bool(_as_map(report.get("baseline_comparison")).get("baseline_matches")):
        report["result"] = "refused"
    report["deterministic_fingerprint"] = update_sim_report_hash(report)
    if write_outputs:
        report["written"] = write_update_sim_outputs(root, report)
    return report


def render_update_sim_run(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    baseline = _as_map(payload.get("baseline_install"))
    upgrade = _as_map(payload.get("latest_compatible_upgrade"))
    yanked = _as_map(payload.get("yanked_candidate_exclusion"))
    strict = _as_map(payload.get("strict_trust_refusal"))
    rollback = _as_map(payload.get("rollback_restore"))
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.",
        "",
        "# Update Simulation Run",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- platform_tag: `{}`".format(_token(payload.get("platform_tag"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "- baseline_present: `{}`".format(bool(_as_map(payload.get("baseline_comparison")).get("baseline_present"))),
        "- baseline_matches: `{}`".format(bool(_as_map(payload.get("baseline_comparison")).get("baseline_matches"))),
        "",
        "## Scenario Results",
        "",
        "- baseline install: result=`{}`, plan=`{}`, component_set_hash=`{}`".format(_token(baseline.get("result")), _token(baseline.get("plan_fingerprint")), _token(baseline.get("component_set_hash"))),
        "- latest-compatible upgrade: result=`{}`, plan=`{}`, client=`{}`".format(_token(upgrade.get("result")), _token(upgrade.get("plan_fingerprint")), _token(upgrade.get("selected_client_version"))),
        "- yanked exclusion: result=`{}`, skipped_yanked_count=`{}`, selected_yanked=`{}`".format(_token(yanked.get("result")), int(yanked.get("skipped_yanked_count", 0) or 0), ", ".join(_as_list(yanked.get("selected_yanked_component_ids"))) or "none"),
        "- strict trust: result=`{}`, refusal_code=`{}`".format(_token(strict.get("result")), _token(strict.get("refusal_code"))),
        "- rollback: result=`{}`, restored_component_set_hash=`{}`".format(_token(rollback.get("result")), _token(rollback.get("restored_component_set_hash"))),
        "",
    ]
    return "\n".join(lines)


def render_update_sim_baseline(baseline: Mapping[str, object]) -> str:
    payload = _as_map(baseline)
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.",
        "",
        "# Update Simulation Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Scenario Results",
        "",
        "- baseline install component_set_hash: `{}`".format(_token(_as_map(payload.get("baseline_install")).get("component_set_hash"))),
        "- upgrade plan fingerprint: `{}`".format(_token(_as_map(payload.get("plan_hashes")).get("upgrade_plan_fingerprint"))),
        "- yanked exclusion selected_yanked_component_ids: `{}`".format(", ".join(_as_list(_as_map(payload.get("yanked_exclusion")).get("selected_yanked_component_ids"))) or "none"),
        "- strict trust refusal_code: `{}`".format(_token(_as_map(payload.get("strict_trust")).get("refusal_code"))),
        "- rollback restored_component_set_hash: `{}`".format(_token(_as_map(payload.get("rollback")).get("restored_component_set_hash"))),
        "",
        "## Readiness",
        "",
        "- Ready for Ω-7 trust strict verification and Ω-8 archive offline verification once RepoX, AuditX, TestX, and strict build remain green.",
        "",
    ]
    return "\n".join(lines)


def write_update_sim_outputs(repo_root: str, report: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or UPDATE_SIM_RUN_JSON_REL), report),
        "doc_path": _write_text(_repo_abs(root, doc_path or UPDATE_SIM_RUN_DOC_REL), render_update_sim_run(report)),
    }


def write_update_sim_baseline_outputs(repo_root: str, baseline: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or UPDATE_SIM_BASELINE_REL), baseline),
        "doc_path": _write_text(_repo_abs(root, doc_path or UPDATE_SIM_BASELINE_DOC_REL), render_update_sim_baseline(baseline)),
    }


__all__ = [
    "DEFAULT_PLATFORM_TAG",
    "UPDATE_SIM_BASELINE_DOC_REL",
    "UPDATE_SIM_BASELINE_INDEX_REL",
    "UPDATE_SIM_BASELINE_REL",
    "UPDATE_SIM_BASELINE_SCHEMA_ID",
    "UPDATE_SIM_FIXTURE_DIR_REL",
    "UPDATE_SIM_MODEL_DOC_REL",
    "UPDATE_SIM_REGRESSION_REQUIRED_TAG",
    "UPDATE_SIM_RETRO_AUDIT_REL",
    "UPDATE_SIM_RUN_DOC_REL",
    "UPDATE_SIM_RUN_JSON_REL",
    "UPDATE_SIM_RUN_SCHEMA_ID",
    "UPDATE_SIM_STRICT_INDEX_REL",
    "UPDATE_SIM_TOOL_PY_REL",
    "UPDATE_SIM_TOOL_REL",
    "UPDATE_SIM_UPGRADE_INDEX_REL",
    "UPDATE_SIM_YANKED_INDEX_REL",
    "build_update_sim_baseline",
    "build_update_sim_fixture_payloads",
    "load_update_sim_baseline",
    "load_update_sim_fixtures",
    "load_update_sim_report",
    "render_update_sim_baseline",
    "render_update_sim_run",
    "run_update_sim",
    "update_sim_baseline_hash",
    "update_sim_report_hash",
    "write_update_sim_baseline_outputs",
    "write_update_sim_fixture_outputs",
    "write_update_sim_outputs",
]
