"""Deterministic disaster-suite generation and verification for Omega MVP freezes."""

from __future__ import annotations

import copy
import gc
import json
import os
import shutil
import sys
import time
from typing import Callable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from compat.data_format_loader import load_versioned_artifact  # noqa: E402
from geo import build_overlay_layer, build_property_patch  # noqa: E402
from lib.install.install_validator import validate_install_manifest  # noqa: E402
from lib.provides.provider_resolution import (  # noqa: E402
    RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    resolve_providers,
)
from meta.identity import IDENTITY_KIND_PACK, attach_universal_identity_block  # noqa: E402
from packs.compat.pack_compat_validator import pack_compat_manifest_fingerprint  # noqa: E402
from packs.compat.pack_verification_pipeline import verify_pack_set  # noqa: E402
from release.release_manifest_engine import build_mock_signature_block, verify_release_manifest  # noqa: E402
from release.update_resolver import (  # noqa: E402
    RESOLUTION_POLICY_LATEST_COMPATIBLE,
    append_install_transaction,
    resolve_update_plan,
    select_rollback_transaction,
)
from security.trust.trust_verifier import (  # noqa: E402
    ARTIFACT_KIND_RELEASE_MANIFEST,
    TRUST_POLICY_STRICT,
    verify_artifact_trust,
)
from universe import (  # noqa: E402
    build_universe_contract_bundle_payload,
    enforce_session_contract_bundle,
    pin_contract_bundle_metadata,
)
from tools.dist.dist_tree_common import build_dist_tree  # noqa: E402
from tools.mvp.baseline_universe_common import _baseline_context  # noqa: E402
from tools.worldgen.worldgen_lock_common import WORLDGEN_LOCK_ID, read_worldgen_baseline_seed  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


DISASTER_SUITE_CASES_SCHEMA_ID = "dominium.schema.governance.disaster_suite_cases"
DISASTER_SUITE_RUN_SCHEMA_ID = "dominium.schema.audit.disaster_suite_run"
DISASTER_SUITE_BASELINE_SCHEMA_ID = "dominium.schema.governance.disaster_suite_baseline"
DISASTER_CASES_SCHEMA_ID = DISASTER_SUITE_CASES_SCHEMA_ID
DISASTER_SUITE_VERSION = 0
DISASTER_SUITE_STABILITY_CLASS = "stable"

DISASTER_RETRO_AUDIT_REL = os.path.join("docs", "audit", "DISASTER_TEST0_RETRO_AUDIT.md")
DISASTER_MODEL_DOC_REL = os.path.join("docs", "mvp", "DISASTER_SUITE_MODEL_v0_0_0.md")
DISASTER_CASES_REL = os.path.join("data", "baselines", "disaster", "disaster_suite_cases.json")
DISASTER_RUN_JSON_REL = os.path.join("data", "audit", "disaster_suite_run.json")
DISASTER_RUN_DOC_REL = os.path.join("docs", "audit", "DISASTER_SUITE_RUN.md")
DISASTER_BASELINE_REL = os.path.join("data", "regression", "disaster_suite_baseline.json")
DISASTER_BASELINE_DOC_REL = os.path.join("docs", "audit", "DISASTER_SUITE_BASELINE.md")
DEFAULT_DISASTER_WORK_ROOT_REL = os.path.join("build", "tmp", "omega4_disaster")
DISASTER_REGRESSION_REQUIRED_TAG = "DISASTER-REGRESSION-UPDATE"
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_CHANNEL_ID = "mock"

BASELINE_INSTANCE_SRC_REL = os.path.join("data", "baselines", "universe", "baseline_instance.manifest.json")
BASELINE_PROFILE_SRC_REL = os.path.join("data", "baselines", "universe", "baseline_profile_bundle.json")
BASELINE_PACK_LOCK_SRC_REL = os.path.join("data", "baselines", "universe", "baseline_pack_lock.json")
BASELINE_SAVE_SRC_REL = os.path.join("data", "baselines", "universe", "baseline_save_0.save")

_CASE_COMPARISON_FIELDS = (
    "result",
    "exit_code",
    "refusal_code",
    "remediation_key",
    "remediation_hint",
    "ordered_log_keys",
    "logs_category",
    "details",
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


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _remove_readonly(func, path, _exc_info) -> None:
    try:
        os.chmod(path, 0o666)
    except OSError:
        pass
    try:
        func(path)
    except FileNotFoundError:
        return


def _normalize_tree_permissions(path: str) -> None:
    token = _token(path)
    if not token or not os.path.exists(token):
        return
    for root, dir_names, file_names in os.walk(token, topdown=False):
        for file_name in file_names:
            candidate = os.path.join(root, file_name)
            try:
                os.chmod(candidate, 0o666)
            except OSError:
                continue
        for dir_name in dir_names:
            candidate = os.path.join(root, dir_name)
            try:
                os.chmod(candidate, 0o777)
            except OSError:
                continue
    try:
        os.chmod(token, 0o777)
    except OSError:
        pass


def _prune_python_bytecode(path: str) -> None:
    token = _token(path)
    if not token or not os.path.isdir(token):
        return
    for root, dir_names, file_names in os.walk(token, topdown=False):
        for file_name in file_names:
            if not file_name.endswith((".pyc", ".pyo")):
                continue
            candidate = os.path.join(root, file_name)
            try:
                os.chmod(candidate, 0o666)
            except OSError:
                pass
            try:
                os.remove(candidate)
            except FileNotFoundError:
                continue
            except OSError:
                continue
        for dir_name in dir_names:
            if dir_name != "__pycache__":
                continue
            candidate = os.path.join(root, dir_name)
            try:
                shutil.rmtree(candidate, onerror=_remove_readonly)
            except FileNotFoundError:
                continue
            except OSError:
                continue


def _remove_tree_once(path: str) -> None:
    token = _token(path)
    for root, dir_names, file_names in os.walk(token, topdown=False):
        for file_name in sorted(file_names):
            candidate = os.path.join(root, file_name)
            last_error: OSError | None = None
            for _attempt in range(0, 4):
                try:
                    os.chmod(candidate, 0o666)
                except OSError:
                    pass
                try:
                    os.unlink(candidate)
                    break
                except FileNotFoundError:
                    break
                except OSError as exc:
                    last_error = exc
                    try:
                        os.chmod(os.path.dirname(candidate), 0o777)
                    except OSError:
                        pass
                    gc.collect()
            else:
                if last_error is not None:
                    raise last_error
                raise OSError("failed to remove file '{}'".format(candidate))
        for dir_name in sorted(dir_names):
            candidate = os.path.join(root, dir_name)
            last_error = None
            for _attempt in range(0, 4):
                try:
                    os.chmod(candidate, 0o777)
                except OSError:
                    pass
                try:
                    os.rmdir(candidate)
                    break
                except FileNotFoundError:
                    break
                except OSError as exc:
                    last_error = exc
                    gc.collect()
                    time.sleep(0.05 * float(_attempt + 1))
            else:
                if last_error is not None:
                    raise last_error
                raise OSError("failed to remove directory '{}'".format(candidate))
    last_error = None
    for _attempt in range(0, 4):
        try:
            os.chmod(token, 0o777)
        except OSError:
            pass
        try:
            os.rmdir(token)
            break
        except FileNotFoundError:
            break
        except OSError as exc:
            last_error = exc
            gc.collect()
            time.sleep(0.05 * float(_attempt + 1))
    else:
        if last_error is not None:
            raise last_error
        raise OSError("failed to remove directory '{}'".format(token))


def _safe_rmtree(path: str) -> None:
    token = _token(path)
    if not token or not os.path.isdir(token):
        return
    for attempt in range(0, 4):
        gc.collect()
        _normalize_tree_permissions(token)
        _prune_python_bytecode(token)
        try:
            _remove_tree_once(token)
            return
        except FileNotFoundError:
            return
        except OSError:
            if not os.path.exists(token):
                return
            if attempt >= 3:
                raise


def _copy_file(src: str, dst: str) -> str:
    _ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)
    return dst


def _copy_tree(src: str, dst: str) -> str:
    last_error: OSError | None = None
    for attempt in range(0, 4):
        _safe_rmtree(dst)
        _ensure_dir(os.path.dirname(dst))
        try:
            shutil.copytree(src, dst)
            return dst
        except shutil.Error as exc:
            rows = list(exc.args[0] or []) if exc.args else []
            missing_rows = [row for row in rows if len(row) >= 3 and "[Errno 2]" in str(row[2])]
            if rows and len(missing_rows) == len(rows):
                last_error = exc
                gc.collect()
                time.sleep(0.1 * float(attempt + 1))
                continue
            raise
        except FileNotFoundError as exc:
            last_error = exc
            gc.collect()
            time.sleep(0.1 * float(attempt + 1))
    if last_error is not None:
        raise last_error
    raise OSError("failed to copy tree '{}'".format(src))


def _write_text(path: str, text: str) -> str:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text).replace("\r\n", "\n"))
    return path


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _relative_to(root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    abs_path = os.path.normpath(os.path.abspath(token))
    try:
        return _norm(os.path.relpath(abs_path, root))
    except ValueError:
        return _norm(abs_path)


def _record_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def disaster_cases_record_hash(record: Mapping[str, object]) -> str:
    return _record_hash(record)


def disaster_run_report_hash(report: Mapping[str, object]) -> str:
    return _record_hash(report)


def disaster_baseline_hash(payload: Mapping[str, object]) -> str:
    return _record_hash(payload)


def load_disaster_suite_cases(repo_root: str, path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(repo_root_abs, path or DISASTER_CASES_REL))


def load_disaster_suite_baseline(repo_root: str, path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(repo_root_abs, path or DISASTER_BASELINE_REL))


def _stable_details(payload: Mapping[str, object] | None) -> dict:
    body = {}
    for key, value in sorted(_as_map(payload).items(), key=lambda item: str(item[0])):
        if isinstance(value, Mapping):
            body[str(key)] = _stable_details(value)
        elif isinstance(value, list):
            rows = []
            for item in value:
                if isinstance(item, Mapping):
                    rows.append(_stable_details(item))
                else:
                    rows.append(item)
            body[str(key)] = rows
        else:
            body[str(key)] = value
    return body


def _build_case_result(
    *,
    spec: Mapping[str, object],
    result: str,
    refusal_code: str = "",
    remediation_hint: str = "",
    details: Mapping[str, object] | None = None,
) -> dict:
    normalized_result = "refused" if _token(result) == "refused" else "complete"
    remediation_key = _token(_as_map(spec).get("remediation_key"))
    fallback_hint = _token(_as_map(spec).get("fallback_remediation_hint"))
    hint = _token(remediation_hint) or fallback_hint
    preconditions = [
        dict(item)
        for item in _as_list(_as_map(spec).get("preconditions"))
        if isinstance(item, Mapping)
    ]
    ordered_log_keys = [
        "category.{}".format(_token(_as_map(spec).get("scenario_category")) or "unknown"),
        "logcat.{}".format(_token(_as_map(spec).get("logs_category")) or "unknown"),
    ]
    ordered_log_keys.extend(
        "precondition.{}".format(_token(_as_map(row).get("action_id")))
        for row in preconditions
        if _token(_as_map(row).get("action_id"))
    )
    ordered_log_keys.append("entrypoint.{}".format(_token(_as_map(spec).get("entrypoint_id")) or "unknown"))
    ordered_log_keys.append("outcome.{}".format("refused" if normalized_result == "refused" else "complete"))
    if _token(refusal_code):
        ordered_log_keys.append("refusal.{}".format(_token(refusal_code)))
    if remediation_key:
        ordered_log_keys.append("remediation.{}".format(remediation_key))
    payload = {
        "case_id": _token(_as_map(spec).get("case_id")),
        "result": normalized_result,
        "exit_code": 1 if normalized_result == "refused" else 0,
        "refusal_code": _token(refusal_code),
        "remediation_key": remediation_key,
        "remediation_hint": hint,
        "ordered_log_keys": ordered_log_keys,
        "logs_category": _token(_as_map(spec).get("logs_category")),
        "details": _stable_details(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _record_hash(payload)
    return payload


def _comparison_payload(row: Mapping[str, object]) -> dict:
    payload = {}
    for field in _CASE_COMPARISON_FIELDS:
        value = row.get(field)
        if isinstance(value, Mapping):
            payload[field] = _stable_details(value)
        elif isinstance(value, list):
            payload[field] = copy.deepcopy(value)
        else:
            payload[field] = value
    return payload


def _first_error(result: Mapping[str, object]) -> dict:
    rows = [
        dict(item)
        for item in _as_list(_as_map(result).get("errors"))
        if isinstance(item, Mapping)
    ]
    return rows[0] if rows else {}


def _refusal_code_of(payload: Mapping[str, object] | None) -> str:
    row = _as_map(payload)
    nested = _as_map(row.get("refusal"))
    return (
        _token(row.get("refusal_code"))
        or _token(nested.get("reason_code"))
        or _token(_as_map(_first_error(row)).get("code"))
    )


def _remediation_hint_of(payload: Mapping[str, object] | None) -> str:
    row = _as_map(payload)
    nested = _as_map(row.get("refusal"))
    return _token(row.get("remediation_hint")) or _token(nested.get("remediation_hint"))


def _dist_fixture(repo_root: str, output_root: str) -> dict:
    report = build_dist_tree(
        repo_root,
        platform_tag=DEFAULT_PLATFORM_TAG,
        channel_id=DEFAULT_CHANNEL_ID,
        output_root=output_root,
        install_profile_id="install.profile.full",
    )
    bundle_root = os.path.normpath(os.path.abspath(_token(report.get("bundle_root_abs"))))
    install_manifest_path = os.path.normpath(os.path.abspath(_token(report.get("install_manifest_path"))))
    release_manifest_rel = _token(report.get("release_manifest_path"))
    release_index_rel = _token(report.get("release_index_path"))
    return {
        "report": report,
        "bundle_root": bundle_root,
        "install_manifest_path": install_manifest_path,
        "release_manifest_path": os.path.join(bundle_root, release_manifest_rel.replace("/", os.sep)),
        "release_index_path": os.path.join(bundle_root, release_index_rel.replace("/", os.sep)),
        "install_manifest": _load_json(install_manifest_path),
        "release_manifest": _load_json(os.path.join(bundle_root, release_manifest_rel.replace("/", os.sep))),
        "release_index": _load_json(os.path.join(bundle_root, release_index_rel.replace("/", os.sep))),
    }


def _base_fixture_context(repo_root: str, work_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    work_root_abs = os.path.normpath(os.path.abspath(work_root))
    _safe_rmtree(work_root_abs)
    _ensure_dir(work_root_abs)
    dist_fixture = _dist_fixture(repo_root_abs, os.path.join(work_root_abs, "dist_build"))
    seed_text = read_worldgen_baseline_seed(repo_root_abs)
    baseline_context = _baseline_context(repo_root_abs, seed_text)
    bundle_payload, _registry_payload, proof_bundle, bundle_errors = build_universe_contract_bundle_payload(repo_root_abs)
    if bundle_errors:
        raise ValueError("universe contract bundle unavailable: {}".format(", ".join(sorted(set(bundle_errors)))))
    return {
        "repo_root": repo_root_abs,
        "work_root": work_root_abs,
        "dist_fixture": dist_fixture,
        "seed_text": seed_text,
        "baseline_context": baseline_context,
        "bundle_payload": bundle_payload,
        "proof_bundle": proof_bundle,
    }


def _prepare_case_workspace(context: Mapping[str, object], case_id: str) -> dict:
    work_root = _token(_as_map(context).get("work_root"))
    case_root = os.path.join(work_root, "cases", _token(case_id).replace(".", "_"))
    fixture_root = os.path.join(case_root, "fixture")
    dist_root = os.path.join(fixture_root, "dist")
    baseline_root = os.path.join(fixture_root, "baseline")
    contract_root = os.path.join(fixture_root, "contracts")
    pack_repo_root = os.path.join(fixture_root, "pack_repo")
    dist_fixture = _as_map(context).get("dist_fixture")
    dist_bundle_root = _token(_as_map(dist_fixture).get("bundle_root"))
    install_manifest_path = _token(_as_map(dist_fixture).get("install_manifest_path"))
    release_manifest_path = _token(_as_map(dist_fixture).get("release_manifest_path"))
    release_index_path = _token(_as_map(dist_fixture).get("release_index_path"))
    repo_root = _token(_as_map(context).get("repo_root"))

    _safe_rmtree(case_root)
    _ensure_dir(case_root)
    _copy_tree(dist_bundle_root, dist_root)
    _ensure_dir(baseline_root)
    _copy_file(_repo_abs(repo_root, BASELINE_INSTANCE_SRC_REL), os.path.join(baseline_root, os.path.basename(BASELINE_INSTANCE_SRC_REL)))
    _copy_file(_repo_abs(repo_root, BASELINE_PROFILE_SRC_REL), os.path.join(baseline_root, os.path.basename(BASELINE_PROFILE_SRC_REL)))
    _copy_file(_repo_abs(repo_root, BASELINE_PACK_LOCK_SRC_REL), os.path.join(baseline_root, os.path.basename(BASELINE_PACK_LOCK_SRC_REL)))
    _copy_file(_repo_abs(repo_root, BASELINE_SAVE_SRC_REL), os.path.join(baseline_root, os.path.basename(BASELINE_SAVE_SRC_REL)))

    _ensure_dir(contract_root)
    bundle_path = _write_canonical_json(
        os.path.join(contract_root, "universe_contract_bundle.json"),
        _as_map(context).get("bundle_payload"),
    )
    identity_stub_path = _write_canonical_json(os.path.join(contract_root, "universe_identity.json"), {"case_id": _token(case_id)})
    return {
        "case_root": case_root,
        "fixture_root": fixture_root,
        "dist_root": dist_root,
        "baseline_root": baseline_root,
        "contract_root": contract_root,
        "pack_repo_root": pack_repo_root,
        "install_manifest_path": os.path.join(dist_root, os.path.basename(install_manifest_path)),
        "release_manifest_path": os.path.join(dist_root, _relative_to(dist_bundle_root, release_manifest_path).replace("/", os.sep)),
        "release_index_path": os.path.join(dist_root, _relative_to(dist_bundle_root, release_index_path).replace("/", os.sep)),
        "baseline_instance_path": os.path.join(baseline_root, os.path.basename(BASELINE_INSTANCE_SRC_REL)),
        "baseline_profile_path": os.path.join(baseline_root, os.path.basename(BASELINE_PROFILE_SRC_REL)),
        "baseline_pack_lock_path": os.path.join(baseline_root, os.path.basename(BASELINE_PACK_LOCK_SRC_REL)),
        "baseline_save_path": os.path.join(baseline_root, os.path.basename(BASELINE_SAVE_SRC_REL)),
        "bundle_path": bundle_path,
        "identity_stub_path": identity_stub_path,
    }


def _trust_root_row(*, signer_id: str, trust_level_id: str = "trust.official_signed") -> dict:
    return {
        "signer_id": _token(signer_id),
        "public_key_bytes": canonical_sha256({"signer_id": _token(signer_id), "purpose": "omega4"}),
        "trust_level_id": _token(trust_level_id),
        "extensions": {"source": "OMEGA-4"},
    }


def _write_pack_manifest(path: str, *, pack_id: str, version: str, contributions: Sequence[Mapping[str, object]]) -> None:
    payload = {
        "schema_version": "1.0.0",
        "pack_id": _token(pack_id),
        "version": _token(version),
        "compatibility": {
            "session_spec_min": "1.0.0",
            "session_spec_max": "1.0.0",
        },
        "dependencies": [],
        "contribution_types": ["registry_entries"],
        "contributions": [dict(item) for item in list(contributions or []) if isinstance(item, Mapping)],
        "canonical_hash": canonical_sha256({"pack_id": _token(pack_id), "version": _token(version)}),
        "signature_status": "signed",
    }
    _write_canonical_json(path, payload)


def _descriptor_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(dict(payload or {}), deterministic_fingerprint="")
    return canonical_sha256(body)


def _write_pack_policy_descriptors(
    pack_dir: str,
    *,
    pack_id: str,
    trust_level_id: str,
    capability_ids: Sequence[object],
    extensions_source: str,
) -> None:
    trust_payload = {
        "schema_version": "1.0.0",
        "pack_id": _token(pack_id),
        "trust_level_id": _token(trust_level_id),
        "signature_hash": "sig.{}".format(canonical_sha256({"pack_id": _token(pack_id), "purpose": "omega4"})[:16]),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": _token(extensions_source)},
    }
    trust_payload["deterministic_fingerprint"] = _descriptor_fingerprint(trust_payload)
    _write_canonical_json(os.path.join(pack_dir, "pack.trust.json"), trust_payload)
    capabilities_payload = {
        "schema_version": "1.0.0",
        "pack_id": _token(pack_id),
        "capability_ids": sorted({str(item).strip() for item in list(capability_ids or []) if str(item).strip()}),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": _token(extensions_source)},
    }
    capabilities_payload["deterministic_fingerprint"] = _descriptor_fingerprint(capabilities_payload)
    _write_canonical_json(os.path.join(pack_dir, "pack.capabilities.json"), capabilities_payload)


def _write_pack_compat(
    path: str,
    *,
    pack_id: str,
    version: str,
    source_rel: str,
    trust_level_id: str,
    proof_bundle: Mapping[str, object],
    provides_declarations: Sequence[Mapping[str, object]] | None = None,
    required_provides_ids: Sequence[object] | None = None,
    capability_ids: Sequence[object] | None = None,
) -> None:
    payload = {
        "schema_version": "1.0.0",
        "pack_id": _token(pack_id),
        "pack_version": _token(version),
        "required_contract_ranges": {},
        "required_protocol_ranges": {},
        "supported_engine_version_range": {},
        "required_registry_ids": [],
        "migration_refs": [],
        "provides": [],
        "capability_ids": [str(item).strip() for item in list(capability_ids or []) if str(item).strip()],
        "required_provides_ids": [str(item).strip() for item in list(required_provides_ids or []) if str(item).strip()],
        "provides_declarations": [
            dict(item)
            for item in list(provides_declarations or [])
            if isinstance(item, Mapping)
        ],
        "degrade_mode_id": "pack.degrade.strict_refuse",
        "trust_level_id": _token(trust_level_id),
        "extensions": {
            "official.manifest_sidecar": "pack.compat.json",
            "official.source": "OMEGA-4",
        },
    }
    payload = attach_universal_identity_block(
        payload,
        identity_kind_id=IDENTITY_KIND_PACK,
        identity_id="identity.pack.{}".format(_token(pack_id)),
        stability_class_id="provisional",
        semver=_token(version),
        schema_version="1.0.0",
        contract_bundle_hash=_token(_as_map(proof_bundle).get("universe_contract_bundle_hash")),
        extensions={"official.rel_path": _norm(source_rel)},
    )
    payload["deterministic_fingerprint"] = pack_compat_manifest_fingerprint(payload)
    _write_canonical_json(path, payload)


def _prepare_pack_repo(
    context: Mapping[str, object],
    workspace: Mapping[str, object],
    *,
    bundle_id: str,
    required_pack_ids: Sequence[object] | None = None,
    optional_pack_ids: Sequence[object] | None = None,
) -> str:
    repo_root = _token(_as_map(context).get("repo_root"))
    pack_repo_root = _token(_as_map(workspace).get("pack_repo_root"))
    _safe_rmtree(pack_repo_root)
    _ensure_dir(pack_repo_root)
    _copy_tree(_repo_abs(repo_root, os.path.join("data", "registries")), os.path.join(pack_repo_root, "data", "registries"))
    bundle_path = os.path.join(pack_repo_root, "bundles", bundle_id, "bundle.json")
    bundle_payload = {
        "schema_version": "1.0.0",
        "bundle_id": _token(bundle_id),
        "description": "Omega-4 disaster fixture bundle",
        "pack_ids": [str(item).strip() for item in list(required_pack_ids or []) if str(item).strip()],
        "optional_pack_ids": [str(item).strip() for item in list(optional_pack_ids or []) if str(item).strip()],
    }
    _write_canonical_json(bundle_path, bundle_payload)
    return pack_repo_root


def _write_overlay_conflict_pack(
    context: Mapping[str, object],
    pack_repo_root: str,
    *,
    pack_id: str,
    layer_id: str,
    patch_value: int,
) -> None:
    pack_dir = os.path.join(pack_repo_root, "packs", "core", pack_id)
    _ensure_dir(os.path.join(pack_dir, "data", "overlay"))
    contributions = [
        {
            "type": "registry_entries",
            "id": "{}.layer".format(_token(pack_id)),
            "path": "data/overlay/layer.json",
        },
        {
            "type": "registry_entries",
            "id": "{}.patches".format(_token(pack_id)),
            "path": "data/overlay/patches.json",
        },
    ]
    manifest_path = os.path.join(pack_dir, "pack.json")
    _write_pack_manifest(manifest_path, pack_id=pack_id, version="1.0.0", contributions=contributions)
    manifest_payload = _load_json(manifest_path)
    layer_payload = build_overlay_layer(
        layer_id=layer_id,
        layer_kind="official",
        precedence_order=100,
        source_ref=_token(manifest_payload.get("canonical_hash")),
        extensions={
            "pack_id": _token(pack_id),
            "pack_hash": _token(manifest_payload.get("canonical_hash")),
            "signature_status": "signed",
            "source": "OMEGA-4",
        },
    )
    patch_payload = {
        "property_patches": [
            build_property_patch(
                target_object_id="object.overlay.conflict",
                property_path="terrain.height_proxy_mm",
                operation="set",
                value=int(patch_value),
                originating_layer_id=layer_id,
                extensions={"reason": "omega4_conflict_fixture"},
            )
        ]
    }
    _write_canonical_json(os.path.join(pack_dir, "data", "overlay", "layer.json"), layer_payload)
    _write_canonical_json(os.path.join(pack_dir, "data", "overlay", "patches.json"), patch_payload)
    _write_pack_policy_descriptors(
        pack_dir,
        pack_id=pack_id,
        trust_level_id="trust.official_signed",
        capability_ids=["cap.overlay_patch"],
        extensions_source="OMEGA-4",
    )
    compat_rel = _norm(os.path.relpath(os.path.join(pack_dir, "pack.compat.json"), pack_repo_root))
    _write_pack_compat(
        os.path.join(pack_dir, "pack.compat.json"),
        pack_id=pack_id,
        version="1.0.0",
        source_rel=compat_rel,
        trust_level_id="trust.official_signed",
        proof_bundle=_as_map(context).get("proof_bundle"),
        capability_ids=["cap.overlay_patch"],
    )


def _release_platform_fields(release_index: Mapping[str, object]) -> dict:
    platform_row = _as_map((_as_list(_as_map(release_index).get("platform_matrix")) or [{}])[0])
    platform_ext = _as_map(platform_row.get("extensions"))
    return {
        "target_platform": _token(platform_ext.get("platform_id")) or _token(platform_row.get("os")) or "windows",
        "target_arch": _token(platform_row.get("arch")) or "x86_64",
        "target_abi": _token(platform_row.get("abi")) or "msvc",
    }


def _disaster_case_specs() -> list[dict]:
    return [
        {
            "case_id": "artifact_corruption.corrupted_pack_blob",
            "scenario_category": "artifact_corruption",
            "scenario_label": "corrupted pack blob",
            "entrypoint_id": "pack.verify",
            "command": "verify_pack_set(repo_root=<fixture_pack_repo>)",
            "logs_category": "artifact.integrity",
            "remediation_key": "restore_pack_blob",
            "fallback_remediation_hint": "Restore the corrupted pack payload from a verified baseline pack source before retrying verification.",
            "preconditions": [{"action_id": "corrupt_pack_manifest", "operation": "overwrite_invalid_json", "target_rel": "pack_repo/packs/core/pack.disaster.corrupted/pack.json"}],
            "executor": "_case_corrupted_pack_blob",
        },
        {
            "case_id": "artifact_corruption.corrupted_profile_bundle",
            "scenario_category": "artifact_corruption",
            "scenario_label": "corrupted profile bundle",
            "entrypoint_id": "compat.load.profile_bundle",
            "command": "load_versioned_artifact(profile_bundle)",
            "logs_category": "artifact.integrity",
            "remediation_key": "restore_profile_bundle",
            "fallback_remediation_hint": "Restore the frozen baseline profile bundle or regenerate it from the committed baseline universe artifacts.",
            "preconditions": [{"action_id": "corrupt_profile_bundle", "operation": "overwrite_invalid_json", "target_rel": "baseline/baseline_profile_bundle.json"}],
            "executor": "_case_corrupted_profile_bundle",
        },
        {
            "case_id": "artifact_corruption.corrupted_lock_file",
            "scenario_category": "artifact_corruption",
            "scenario_label": "corrupted lock file",
            "entrypoint_id": "compat.load.pack_lock",
            "command": "load_versioned_artifact(pack_lock)",
            "logs_category": "artifact.integrity",
            "remediation_key": "restore_pack_lock",
            "fallback_remediation_hint": "Restore the frozen baseline pack lock from version control before continuing.",
            "preconditions": [{"action_id": "corrupt_pack_lock", "operation": "overwrite_invalid_json", "target_rel": "baseline/baseline_pack_lock.json"}],
            "executor": "_case_corrupted_lock_file",
        },
        {
            "case_id": "artifact_corruption.corrupted_release_manifest",
            "scenario_category": "artifact_corruption",
            "scenario_label": "corrupted release manifest",
            "entrypoint_id": "release.verify_manifest",
            "command": "verify_release_manifest(dist_root=<fixture_dist>)",
            "logs_category": "artifact.integrity",
            "remediation_key": "regenerate_release_manifest",
            "fallback_remediation_hint": "Rebuild and re-sign the release manifest from the deterministic dist tree before retrying release verification.",
            "preconditions": [{"action_id": "corrupt_release_manifest_hash", "operation": "replace_field", "target_rel": "dist/manifests/release_manifest.json"}],
            "executor": "_case_corrupted_release_manifest",
        },
        {
            "case_id": "artifact_corruption.corrupted_save_snapshot",
            "scenario_category": "artifact_corruption",
            "scenario_label": "corrupted save snapshot",
            "entrypoint_id": "compat.load.save_file",
            "command": "load_versioned_artifact(save_file)",
            "logs_category": "artifact.integrity",
            "remediation_key": "restore_save_snapshot",
            "fallback_remediation_hint": "Restore the frozen baseline save snapshot from the committed baseline universe artifacts.",
            "preconditions": [{"action_id": "corrupt_save_snapshot", "operation": "overwrite_invalid_json", "target_rel": "baseline/baseline_save_0.save"}],
            "executor": "_case_corrupted_save_snapshot",
        },
        {
            "case_id": "missing_components.missing_required_pack",
            "scenario_category": "missing_components",
            "scenario_label": "missing required pack",
            "entrypoint_id": "pack.verify.bundle_selection",
            "command": "verify_pack_set(bundle_id='bundle.omega4.missing_required')",
            "logs_category": "component.presence",
            "remediation_key": "restore_required_pack",
            "fallback_remediation_hint": "Install the required pack into the deterministic pack repo or update the bundle profile explicitly.",
            "preconditions": [{"action_id": "declare_missing_required_pack", "operation": "bundle_reference_missing_pack", "target_rel": "pack_repo/bundles/bundle.omega4.missing_required/bundle.json"}],
            "executor": "_case_missing_required_pack",
        },
        {
            "case_id": "missing_components.missing_binary_referenced_by_install",
            "scenario_category": "missing_components",
            "scenario_label": "missing binary referenced by install",
            "entrypoint_id": "install.validate_manifest",
            "command": "validate_install_manifest(install_manifest)",
            "logs_category": "component.presence",
            "remediation_key": "restore_binary_from_release",
            "fallback_remediation_hint": "Restore the missing product binary from the baseline dist tree or rebuild the install bundle.",
            "preconditions": [{"action_id": "remove_product_binary", "operation": "delete_file", "target_rel": "dist/<product_binary>"}],
            "executor": "_case_missing_binary_referenced_by_install",
        },
        {
            "case_id": "missing_components.missing_store_artifact_referenced_by_instance_save",
            "scenario_category": "missing_components",
            "scenario_label": "missing store artifact referenced by instance/save",
            "entrypoint_id": "compat.load.store_artifact",
            "command": "load_versioned_artifact(save_file_missing_from_store)",
            "logs_category": "component.presence",
            "remediation_key": "restore_store_artifact",
            "fallback_remediation_hint": "Restore the missing save/store artifact referenced by the baseline instance before loading it.",
            "preconditions": [{"action_id": "remove_store_save_artifact", "operation": "delete_file", "target_rel": "baseline/baseline_save_0.save"}],
            "executor": "_case_missing_store_artifact",
        },
        {
            "case_id": "compatibility_mismatches.contract_bundle_mismatch",
            "scenario_category": "compatibility_mismatches",
            "scenario_label": "contract bundle mismatch",
            "entrypoint_id": "universe.enforce_contract_bundle",
            "command": "enforce_session_contract_bundle(replay_mode=false)",
            "logs_category": "compatibility.contract",
            "remediation_key": "run_explicit_contract_migration",
            "fallback_remediation_hint": "Run the explicit CompatX migration path or reopen the universe under a matching pinned contract bundle.",
            "preconditions": [{"action_id": "mismatch_session_contract_hash", "operation": "replace_field", "target_rel": "contracts/universe_contract_bundle.json"}],
            "executor": "_case_contract_bundle_mismatch",
        },
        {
            "case_id": "compatibility_mismatches.protocol_mismatch_no_common_range",
            "scenario_category": "compatibility_mismatches",
            "scenario_label": "protocol mismatch with no common range",
            "entrypoint_id": "update.resolve_protocol_mismatch",
            "command": "resolve_update_plan(protocol_mismatch)",
            "logs_category": "compatibility.protocol",
            "remediation_key": "select_compatible_release",
            "fallback_remediation_hint": "Select a release index whose supported protocol ranges overlap the current install manifest.",
            "preconditions": [{"action_id": "replace_protocol_range", "operation": "replace_field", "target_rel": "dist/manifests/release_index.json"}],
            "executor": "_case_protocol_mismatch",
        },
        {
            "case_id": "compatibility_mismatches.schema_format_version_too_new",
            "scenario_category": "compatibility_mismatches",
            "scenario_label": "schema or format version too new",
            "entrypoint_id": "compat.load.future_version",
            "command": "load_versioned_artifact(profile_bundle_future_version)",
            "logs_category": "compatibility.format",
            "remediation_key": "use_newer_engine_or_migration",
            "fallback_remediation_hint": "Use a newer engine build or add an explicit migration path for the future-format artifact.",
            "preconditions": [{"action_id": "bump_format_version", "operation": "replace_field", "target_rel": "baseline/baseline_profile_bundle.json"}],
            "executor": "_case_format_version_too_new",
        },
        {
            "case_id": "trust_failures.unsigned_in_strict_mode",
            "scenario_category": "trust_failures",
            "scenario_label": "unsigned in strict mode",
            "entrypoint_id": "trust.verify.unsigned_strict",
            "command": "verify_artifact_trust(strict_ranked, signatures=[])",
            "logs_category": "trust.enforcement",
            "remediation_key": "sign_artifact_or_relax_policy",
            "fallback_remediation_hint": "Provide a valid detached signature or choose a policy that explicitly permits unsigned artifacts.",
            "preconditions": [{"action_id": "omit_signatures", "operation": "drop_signatures", "target_rel": "virtual/release_manifest"}],
            "executor": "_case_unsigned_strict_mode",
        },
        {
            "case_id": "trust_failures.invalid_signature",
            "scenario_category": "trust_failures",
            "scenario_label": "invalid signature",
            "entrypoint_id": "trust.verify.invalid_signature",
            "command": "verify_artifact_trust(strict_ranked, signatures=[invalid])",
            "logs_category": "trust.enforcement",
            "remediation_key": "replace_invalid_signature",
            "fallback_remediation_hint": "Replace the invalid detached signature records with a correctly signed artifact digest.",
            "preconditions": [{"action_id": "tamper_signature_bytes", "operation": "replace_field", "target_rel": "virtual/signature_block"}],
            "executor": "_case_invalid_signature",
        },
        {
            "case_id": "trust_failures.unknown_trust_root",
            "scenario_category": "trust_failures",
            "scenario_label": "unknown trust root",
            "entrypoint_id": "trust.verify.unknown_root",
            "command": "verify_artifact_trust(strict_ranked, trusted_roots=[])",
            "logs_category": "trust.enforcement",
            "remediation_key": "import_trust_root",
            "fallback_remediation_hint": "Import the signer into the local trust root registry before accepting the artifact.",
            "preconditions": [{"action_id": "clear_trust_roots", "operation": "use_empty_roots", "target_rel": "virtual/trust_roots"}],
            "executor": "_case_unknown_trust_root",
        },
        {
            "case_id": "update_edge_cases.yanked_component_selected_under_latest_compatible",
            "scenario_category": "update_edge_cases",
            "scenario_label": "yanked component selected under latest_compatible",
            "entrypoint_id": "update.resolve_yanked_latest_compatible",
            "command": "resolve_update_plan(latest_compatible_with_yanked_target)",
            "logs_category": "update.policy",
            "remediation_key": "pin_non_yanked_release",
            "fallback_remediation_hint": "Pin a non-yanked component descriptor or publish a replacement release before updating.",
            "preconditions": [{"action_id": "mark_target_component_yanked", "operation": "replace_field", "target_rel": "dist/manifests/release_index.json"}],
            "executor": "_case_yanked_latest_compatible",
        },
        {
            "case_id": "update_edge_cases.rollback_to_prior_state",
            "scenario_category": "update_edge_cases",
            "scenario_label": "rollback to prior state",
            "entrypoint_id": "update.select_rollback_transaction",
            "command": "select_rollback_transaction(log, to_release_id='release.prior')",
            "logs_category": "update.policy",
            "remediation_key": "rollback_transaction_available",
            "fallback_remediation_hint": "Use the recorded deterministic install transaction log to restore the prior release state.",
            "preconditions": [{"action_id": "seed_install_transaction_log", "operation": "append_transaction", "target_rel": "fixture/install_transaction_log.json"}],
            "executor": "_case_rollback_prior_state",
        },
        {
            "case_id": "policy_conflicts.overlay_conflict_in_strict_policy",
            "scenario_category": "policy_conflicts",
            "scenario_label": "overlay conflict in strict policy",
            "entrypoint_id": "overlay.strict_conflict",
            "command": "verify_pack_set(mod_policy.strict, overlay.conflict.refuse)",
            "logs_category": "policy.conflict",
            "remediation_key": "resolve_overlay_conflict",
            "fallback_remediation_hint": "Adjust the conflicting overlay layers or choose an explicit non-conflicting precedence model before packing.",
            "preconditions": [{"action_id": "write_conflicting_overlay_layers", "operation": "create_conflicting_patches", "target_rel": "pack_repo/packs/core/pack.disaster.layer_*/data/overlay"}],
            "executor": "_case_overlay_conflict_strict",
        },
        {
            "case_id": "policy_conflicts.provides_ambiguity_in_strict_policy",
            "scenario_category": "policy_conflicts",
            "scenario_label": "provides ambiguity in strict policy",
            "entrypoint_id": "provides.strict_ambiguity",
            "command": "resolve_providers(strict_refuse_ambiguous)",
            "logs_category": "policy.conflict",
            "remediation_key": "declare_explicit_provider",
            "fallback_remediation_hint": "Declare an explicit provides resolution or reduce the provider set to a single deterministic choice.",
            "preconditions": [{"action_id": "declare_ambiguous_providers", "operation": "create_multiple_candidates", "target_rel": "virtual/provider_declarations"}],
            "executor": "_case_provides_ambiguity_strict",
        },
    ]


def _spec_by_id(case_id: str) -> dict:
    for row in _disaster_case_specs():
        if _token(_as_map(row).get("case_id")) == _token(case_id):
            return dict(row)
    return {}


def _case_corrupted_pack_blob(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    pack_repo_root = _prepare_pack_repo(context, workspace, bundle_id="bundle.omega4.corrupted_pack")
    pack_dir = os.path.join(pack_repo_root, "packs", "core", "pack.disaster.corrupted")
    _ensure_dir(pack_dir)
    _write_text(os.path.join(pack_dir, "pack.json"), "{ invalid json\n")
    result = verify_pack_set(repo_root=pack_repo_root, schema_repo_root=_token(_as_map(context).get("repo_root")))
    error = _first_error(result)
    return _build_case_result(
        spec=_spec_by_id("artifact_corruption.corrupted_pack_blob"),
        result="refused" if error else _token(result.get("result")),
        refusal_code=_token(error.get("code")) or _token(result.get("refusal_code")),
        remediation_hint="",
        details={
            "error_count": len(_as_list(result.get("errors"))),
            "first_error_path": _token(error.get("path")),
        },
    )


def _case_corrupted_profile_bundle(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    profile_path = _token(_as_map(workspace).get("baseline_profile_path"))
    _write_text(profile_path, "{ invalid json\n")
    _payload, _meta, refusal = load_versioned_artifact(
        repo_root=_token(_as_map(context).get("repo_root")),
        artifact_kind="profile_bundle",
        path=profile_path,
        allow_read_only=False,
    )
    return _build_case_result(
        spec=_spec_by_id("artifact_corruption.corrupted_profile_bundle"),
        result="refused" if refusal else "complete",
        refusal_code=_refusal_code_of(refusal),
        remediation_hint=_remediation_hint_of(refusal),
        details={"artifact_kind": "profile_bundle", "path": os.path.basename(profile_path)},
    )


def _case_corrupted_lock_file(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    pack_lock_path = _token(_as_map(workspace).get("baseline_pack_lock_path"))
    _write_text(pack_lock_path, "{ invalid json\n")
    _payload, _meta, refusal = load_versioned_artifact(
        repo_root=_token(_as_map(context).get("repo_root")),
        artifact_kind="pack_lock",
        path=pack_lock_path,
        allow_read_only=False,
    )
    return _build_case_result(
        spec=_spec_by_id("artifact_corruption.corrupted_lock_file"),
        result="refused" if refusal else "complete",
        refusal_code=_refusal_code_of(refusal),
        remediation_hint=_remediation_hint_of(refusal),
        details={"artifact_kind": "pack_lock", "path": os.path.basename(pack_lock_path)},
    )


def _case_corrupted_release_manifest(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    manifest_path = _token(_as_map(workspace).get("release_manifest_path"))
    dist_root = _token(_as_map(workspace).get("dist_root"))
    payload = _load_json(manifest_path)
    payload["manifest_hash"] = "00" * 32
    _write_canonical_json(manifest_path, payload)
    result = verify_release_manifest(dist_root, manifest_path, repo_root=_token(_as_map(context).get("repo_root")))
    error = _first_error(result)
    return _build_case_result(
        spec=_spec_by_id("artifact_corruption.corrupted_release_manifest"),
        result="refused" if error else _token(result.get("result")),
        refusal_code=_token(error.get("code")) or _token(result.get("refusal_code")),
        remediation_hint=_token(_as_map(_as_map(result).get("trust_result")).get("remediation_hint")),
        details={
            "verified_artifact_count": int(_as_map(result).get("verified_artifact_count", 0) or 0),
            "first_error_path": _token(error.get("path")),
        },
    )


def _case_corrupted_save_snapshot(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    save_path = _token(_as_map(workspace).get("baseline_save_path"))
    _write_text(save_path, "{ invalid json\n")
    _payload, _meta, refusal = load_versioned_artifact(
        repo_root=_token(_as_map(context).get("repo_root")),
        artifact_kind="save_file",
        path=save_path,
        semantic_contract_bundle_hash=_token(_as_map(_as_map(context).get("proof_bundle")).get("universe_contract_bundle_hash")),
        allow_read_only=False,
    )
    return _build_case_result(
        spec=_spec_by_id("artifact_corruption.corrupted_save_snapshot"),
        result="refused" if refusal else "complete",
        refusal_code=_refusal_code_of(refusal),
        remediation_hint=_remediation_hint_of(refusal),
        details={"artifact_kind": "save_file", "path": os.path.basename(save_path)},
    )


def _case_missing_required_pack(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    pack_repo_root = _prepare_pack_repo(
        context,
        workspace,
        bundle_id="bundle.omega4.missing_required",
        required_pack_ids=["pack.disaster.required_missing"],
    )
    result = verify_pack_set(
        repo_root=pack_repo_root,
        bundle_id="bundle.omega4.missing_required",
        schema_repo_root=_token(_as_map(context).get("repo_root")),
    )
    error = _first_error(result)
    return _build_case_result(
        spec=_spec_by_id("missing_components.missing_required_pack"),
        result="refused" if error else _token(result.get("result")),
        refusal_code=_token(error.get("code")) or _token(result.get("refusal_code")),
        remediation_hint="",
        details={"error_count": len(_as_list(result.get("errors"))), "bundle_id": "bundle.omega4.missing_required"},
    )


def _case_missing_binary_referenced_by_install(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    manifest_path = _token(_as_map(workspace).get("install_manifest_path"))
    manifest = _load_json(manifest_path)
    descriptors = _as_map(manifest.get("product_build_descriptors"))
    target_product_id = ""
    binary_rel = ""
    for product_id, row in sorted(descriptors.items()):
        descriptor = _as_map(row)
        candidate = _token(_as_map(descriptor.get("extensions")).get("official.binary_ref"))
        if candidate:
            target_product_id = _token(product_id)
            binary_rel = candidate
            break
    if binary_rel:
        binary_path = os.path.join(_token(_as_map(workspace).get("dist_root")), binary_rel.replace("/", os.sep))
        if os.path.isfile(binary_path):
            os.remove(binary_path)
    result = validate_install_manifest(
        repo_root=_token(_as_map(context).get("repo_root")),
        install_manifest_path=manifest_path,
    )
    error = _first_error(result)
    return _build_case_result(
        spec=_spec_by_id("missing_components.missing_binary_referenced_by_install"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")) or _token(error.get("code")),
        remediation_hint="",
        details={"product_id": target_product_id, "binary_rel": binary_rel},
    )


def _case_missing_store_artifact(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    save_path = _token(_as_map(workspace).get("baseline_save_path"))
    if os.path.isfile(save_path):
        os.remove(save_path)
    _payload, _meta, refusal = load_versioned_artifact(
        repo_root=_token(_as_map(context).get("repo_root")),
        artifact_kind="save_file",
        path=save_path,
        semantic_contract_bundle_hash=_token(_as_map(_as_map(context).get("proof_bundle")).get("universe_contract_bundle_hash")),
        allow_read_only=False,
    )
    instance_manifest = _load_json(_token(_as_map(workspace).get("baseline_instance_path")))
    return _build_case_result(
        spec=_spec_by_id("missing_components.missing_store_artifact_referenced_by_instance_save"),
        result="refused" if refusal else "complete",
        refusal_code=_refusal_code_of(refusal),
        remediation_hint=_remediation_hint_of(refusal),
        details={
            "save_ref": (_as_list(instance_manifest.get("save_refs")) or [""])[0],
            "save_rel": _token(_as_map(instance_manifest.get("extensions")).get("official.save_artifact_rel")),
        },
    )


def _case_contract_bundle_mismatch(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    baseline_context = _as_map(context).get("baseline_context")
    universe_identity_seed = dict(_as_map(_as_map(baseline_context).get("universe_identity")))
    universe_identity = pin_contract_bundle_metadata(
        universe_identity_seed,
        bundle_ref=os.path.basename(_token(_as_map(workspace).get("bundle_path"))),
        bundle_payload=_as_map(context).get("bundle_payload"),
    )
    session_spec = {
        "save_id": "save.baseline_universe_0",
        "universe_id": _token(universe_identity.get("universe_id")),
        "contract_bundle_hash": "ff" * 32,
        "semantic_contract_registry_hash": _token(_as_map(_as_map(context).get("proof_bundle")).get("semantic_contract_registry_hash")),
    }
    result = enforce_session_contract_bundle(
        repo_root=_token(_as_map(context).get("repo_root")),
        session_spec=session_spec,
        universe_identity=universe_identity,
        identity_path=_token(_as_map(workspace).get("identity_stub_path")),
        replay_mode=False,
    )
    return _build_case_result(
        spec=_spec_by_id("compatibility_mismatches.contract_bundle_mismatch"),
        result=_token(result.get("result")),
        refusal_code=_refusal_code_of(result),
        remediation_hint=_remediation_hint_of(result),
        details={"bundle_ref": _token(universe_identity.get("universe_contract_bundle_ref"))},
    )


def _case_protocol_mismatch(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    dist_root = _token(_as_map(workspace).get("dist_root"))
    install_manifest = _load_json(_token(_as_map(workspace).get("install_manifest_path")))
    install_manifest["supported_protocol_versions"] = {
        "protocol.control": {"min_version": "1.0.0", "max_version": "1.0.0"}
    }
    release_index = _load_json(_token(_as_map(workspace).get("release_index_path")))
    release_index["supported_protocol_ranges"] = {
        "protocol.control": {"min_version": "2.0.0", "max_version": "2.0.0"}
    }
    platform_fields = _release_platform_fields(release_index)
    result = resolve_update_plan(
        install_manifest,
        release_index,
        resolution_policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
        target_platform=_token(platform_fields.get("target_platform")),
        target_arch=_token(platform_fields.get("target_arch")),
        target_abi=_token(platform_fields.get("target_abi")),
        component_graph=_as_map(_as_map(release_index.get("extensions")).get("component_graph")),
        install_root=dist_root,
        release_index_path=_token(_as_map(workspace).get("release_index_path")),
    )
    return _build_case_result(
        spec=_spec_by_id("compatibility_mismatches.protocol_mismatch_no_common_range"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint="",
        details={"protocol_id": "protocol.control", "error_count": len(_as_list(result.get("errors")))},
    )


def _case_format_version_too_new(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    profile_path = _token(_as_map(workspace).get("baseline_profile_path"))
    payload = _load_json(profile_path)
    payload["format_version"] = "99.0.0"
    payload["deterministic_fingerprint"] = ""
    _write_canonical_json(profile_path, payload)
    _payload, _meta, refusal = load_versioned_artifact(
        repo_root=_token(_as_map(context).get("repo_root")),
        artifact_kind="profile_bundle",
        path=profile_path,
        allow_read_only=False,
    )
    return _build_case_result(
        spec=_spec_by_id("compatibility_mismatches.schema_format_version_too_new"),
        result="refused" if refusal else "complete",
        refusal_code=_refusal_code_of(refusal),
        remediation_hint=_remediation_hint_of(refusal),
        details={"artifact_kind": "profile_bundle", "format_version": "99.0.0"},
    )


def _case_unsigned_strict_mode(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    del workspace
    result = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash="aa" * 32,
        signatures=[],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=_token(_as_map(context).get("repo_root")),
        trust_roots=[],
    )
    return _build_case_result(
        spec=_spec_by_id("trust_failures.unsigned_in_strict_mode"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint=_token(result.get("remediation_hint")),
        details={"artifact_kind": ARTIFACT_KIND_RELEASE_MANIFEST, "verified_signature_count": int(result.get("verified_signature_count", 0) or 0)},
    )


def _case_invalid_signature(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    del workspace
    signed_hash = "bb" * 32
    signer_id = "signer.omega4.invalid"
    signature = build_mock_signature_block(signer_id=signer_id, signed_hash=signed_hash)
    signature["signature_bytes"] = "00" * 32
    result = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash=signed_hash,
        signatures=[signature],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=_token(_as_map(context).get("repo_root")),
        trust_roots=[_trust_root_row(signer_id=signer_id)],
    )
    return _build_case_result(
        spec=_spec_by_id("trust_failures.invalid_signature"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint=_token(result.get("remediation_hint")),
        details={"signer_id": signer_id, "signature_status": _token(result.get("signature_status"))},
    )


def _case_unknown_trust_root(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    del workspace
    signed_hash = "cc" * 32
    signer_id = "signer.omega4.unknown"
    signature = build_mock_signature_block(signer_id=signer_id, signed_hash=signed_hash)
    result = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash=signed_hash,
        signatures=[signature],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=_token(_as_map(context).get("repo_root")),
        trust_roots=[],
    )
    return _build_case_result(
        spec=_spec_by_id("trust_failures.unknown_trust_root"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint=_token(result.get("remediation_hint")),
        details={"signer_id": signer_id, "trusted_signer_ids": list(result.get("trusted_signer_ids") or [])},
    )


def _case_yanked_latest_compatible(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    dist_root = _token(_as_map(workspace).get("dist_root"))
    install_manifest = _load_json(_token(_as_map(workspace).get("install_manifest_path")))
    release_index = _load_json(_token(_as_map(workspace).get("release_index_path")))
    components = []
    for row in _as_list(release_index.get("components")):
        item = dict(row) if isinstance(row, Mapping) else {}
        if _token(_as_map(item).get("component_id")):
            item["yanked"] = True
            item["yank_reason"] = "omega4 deterministic disaster fixture"
            item["yank_policy"] = "refuse"
        components.append(item)
    release_index["components"] = components
    platform_fields = _release_platform_fields(release_index)
    result = resolve_update_plan(
        install_manifest,
        release_index,
        resolution_policy_id=RESOLUTION_POLICY_LATEST_COMPATIBLE,
        target_platform=_token(platform_fields.get("target_platform")),
        target_arch=_token(platform_fields.get("target_arch")),
        target_abi=_token(platform_fields.get("target_abi")),
        component_graph=_as_map(_as_map(release_index.get("extensions")).get("component_graph")),
        install_root=dist_root,
        release_index_path=_token(_as_map(workspace).get("release_index_path")),
    )
    plan = _as_map(result.get("update_plan"))
    plan_ext = _as_map(plan.get("extensions"))
    return _build_case_result(
        spec=_spec_by_id("update_edge_cases.yanked_component_selected_under_latest_compatible"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint="",
        details={
            "selected_yanked_component_ids": list(plan_ext.get("selected_yanked_component_ids") or []),
            "error_count": len(_as_list(result.get("errors"))),
        },
    )


def _case_rollback_prior_state(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    del context
    log_path = os.path.join(_token(_as_map(workspace).get("case_root")), "install_transaction_log.json")
    append_install_transaction(
        log_path,
        {
            "transaction_id": "tx.omega4.rollback",
            "action": "update.apply",
            "from_release_id": "release.prior",
            "to_release_id": "release.current",
            "status": "complete",
            "backup_path": os.path.join(_token(_as_map(workspace).get("case_root")), "backup"),
            "install_profile_id": "install.profile.full",
            "resolution_policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
            "install_plan_hash": "33" * 32,
            "prior_component_set_hash": "44" * 32,
            "selected_component_ids": ["binary.client"],
        },
    )
    row = select_rollback_transaction(log_path, to_release_id="release.prior")
    return _build_case_result(
        spec=_spec_by_id("update_edge_cases.rollback_to_prior_state"),
        result="complete" if row else "refused",
        refusal_code="" if row else "refusal.update.rollback_missing",
        remediation_hint="" if row else "Restore a completed install transaction log entry before requesting rollback.",
        details={
            "transaction_id": _token(_as_map(row).get("transaction_id")),
            "resolution_policy_id": _token(_as_map(row).get("resolution_policy_id")),
            "install_plan_hash": _token(_as_map(row).get("install_plan_hash")),
            "prior_component_set_hash": _token(_as_map(row).get("prior_component_set_hash")),
        },
    )


def _case_overlay_conflict_strict(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    pack_repo_root = _prepare_pack_repo(
        context,
        workspace,
        bundle_id="bundle.omega4.overlay_conflict",
        required_pack_ids=["pack.disaster.layer_a", "pack.disaster.layer_b"],
    )
    _write_overlay_conflict_pack(context, pack_repo_root, pack_id="pack.disaster.layer_a", layer_id="layer.omega4.a", patch_value=10)
    _write_overlay_conflict_pack(context, pack_repo_root, pack_id="pack.disaster.layer_b", layer_id="layer.omega4.b", patch_value=20)
    result = verify_pack_set(
        repo_root=pack_repo_root,
        bundle_id="bundle.omega4.overlay_conflict",
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
        schema_repo_root=_token(_as_map(context).get("repo_root")),
    )
    error = _first_error(result)
    return _build_case_result(
        spec=_spec_by_id("policy_conflicts.overlay_conflict_in_strict_policy"),
        result="refused" if error else _token(result.get("result")),
        refusal_code=_token(error.get("code")) or _token(result.get("refusal_code")),
        remediation_hint="",
        details={"error_count": len(_as_list(result.get("errors"))), "bundle_id": "bundle.omega4.overlay_conflict"},
    )


def _case_provides_ambiguity_strict(context: Mapping[str, object], workspace: Mapping[str, object]) -> dict:
    del context
    del workspace
    declarations = [
        {"provides_id": "provides.omega4.scan", "pack_id": "pack.provider.alpha", "priority": 10, "extensions": {}},
        {"provides_id": "provides.omega4.scan", "pack_id": "pack.provider.beta", "priority": 10, "extensions": {}},
    ]
    result = resolve_providers(
        instance_id="instance.omega4.disaster",
        required_provides_ids=["provides.omega4.scan"],
        provider_declarations=declarations,
        resolution_policy_id=RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
    )
    return _build_case_result(
        spec=_spec_by_id("policy_conflicts.provides_ambiguity_in_strict_policy"),
        result=_token(result.get("result")),
        refusal_code=_token(result.get("refusal_code")),
        remediation_hint="",
        details={"ambiguous_provides_ids": list(result.get("ambiguous_provides_ids") or []), "candidate_count": len(declarations)},
    )


_EXECUTOR_MAP: dict[str, Callable[[Mapping[str, object], Mapping[str, object]], dict]] = {
    "_case_corrupted_pack_blob": _case_corrupted_pack_blob,
    "_case_corrupted_profile_bundle": _case_corrupted_profile_bundle,
    "_case_corrupted_lock_file": _case_corrupted_lock_file,
    "_case_corrupted_release_manifest": _case_corrupted_release_manifest,
    "_case_corrupted_save_snapshot": _case_corrupted_save_snapshot,
    "_case_missing_required_pack": _case_missing_required_pack,
    "_case_missing_binary_referenced_by_install": _case_missing_binary_referenced_by_install,
    "_case_missing_store_artifact": _case_missing_store_artifact,
    "_case_contract_bundle_mismatch": _case_contract_bundle_mismatch,
    "_case_protocol_mismatch": _case_protocol_mismatch,
    "_case_format_version_too_new": _case_format_version_too_new,
    "_case_unsigned_strict_mode": _case_unsigned_strict_mode,
    "_case_invalid_signature": _case_invalid_signature,
    "_case_unknown_trust_root": _case_unknown_trust_root,
    "_case_yanked_latest_compatible": _case_yanked_latest_compatible,
    "_case_rollback_prior_state": _case_rollback_prior_state,
    "_case_overlay_conflict_strict": _case_overlay_conflict_strict,
    "_case_provides_ambiguity_strict": _case_provides_ambiguity_strict,
}


def _execute_case(context: Mapping[str, object], spec: Mapping[str, object]) -> dict:
    workspace = _prepare_case_workspace(context, _token(_as_map(spec).get("case_id")))
    executor = _EXECUTOR_MAP[_token(_as_map(spec).get("executor"))]
    result = executor(context, workspace)
    result["case_id"] = _token(_as_map(spec).get("case_id"))
    return result


def _case_expectation_row(spec: Mapping[str, object], result: Mapping[str, object]) -> dict:
    payload = {
        "case_id": _token(_as_map(spec).get("case_id")),
        "scenario_category": _token(_as_map(spec).get("scenario_category")),
        "scenario_label": _token(_as_map(spec).get("scenario_label")),
        "entrypoint_id": _token(_as_map(spec).get("entrypoint_id")),
        "command": _token(_as_map(spec).get("command")),
        "preconditions": [
            dict(item)
            for item in _as_list(_as_map(spec).get("preconditions"))
            if isinstance(item, Mapping)
        ],
        "logs_category": _token(_as_map(spec).get("logs_category")),
        "expected_result": _token(_as_map(result).get("result")),
        "expected_exit_code": int(_as_map(result).get("exit_code", 0) or 0),
        "expected_refusal_code": _token(_as_map(result).get("refusal_code")),
        "expected_remediation_key": _token(_as_map(result).get("remediation_key")),
        "expected_remediation_hint": _token(_as_map(result).get("remediation_hint")),
        "expected_log_keys": [str(item) for item in _as_list(_as_map(result).get("ordered_log_keys")) if _token(item)],
        "expected_details": _stable_details(_as_map(result).get("details")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _record_hash(payload)
    return payload


def render_disaster_model_doc(cases_payload: Mapping[str, object]) -> str:
    record = _as_map(_as_map(cases_payload).get("record"))
    by_category: dict[str, list[dict]] = {}
    for row in _as_list(record.get("cases")):
        case = _as_map(row)
        by_category.setdefault(_token(case.get("scenario_category")) or "unknown", []).append(case)
    category_titles = {
        "artifact_corruption": "A) Artifact Corruption",
        "missing_components": "B) Missing Components",
        "compatibility_mismatches": "C) Compatibility Mismatches",
        "trust_failures": "D) Trust Failures",
        "update_edge_cases": "E) Update Edge Cases",
        "policy_conflicts": "F) Policy Conflicts",
    }
    lines = [
        "# Disaster Suite Model v0.0.0",
        "",
        "- disaster_suite_version = `0`",
        "- stability_class = `stable`",
        "- baseline_seed = `{}`".format(_token(record.get("baseline_seed"))),
        "- worldgen_lock_id = `{}`".format(_token(record.get("worldgen_lock_id"))),
        "",
    ]
    for category in (
        "artifact_corruption",
        "missing_components",
        "compatibility_mismatches",
        "trust_failures",
        "update_edge_cases",
        "policy_conflicts",
    ):
        lines.extend([category_titles[category], ""])
        for row in by_category.get(category, []):
            case = _as_map(row)
            lines.append("## {}".format(_token(case.get("scenario_label")).title()))
            lines.append("")
            lines.append("- Case ID: `{}`".format(_token(case.get("case_id"))))
            lines.append("- Entrypoint: `{}`".format(_token(case.get("entrypoint_id"))))
            lines.append("- Command: `{}`".format(_token(case.get("command"))))
            lines.append("- Expected Result: `{}`".format(_token(case.get("expected_result"))))
            lines.append("- Expected Refusal Code: `{}`".format(_token(case.get("expected_refusal_code")) or "none"))
            lines.append("- Expected Remediation Key: `{}`".format(_token(case.get("expected_remediation_key")) or "none"))
            lines.append("- Expected Remediation Hint: `{}`".format(_token(case.get("expected_remediation_hint")) or "none"))
            lines.append("- Expected Logs: `{}`".format(", ".join(_as_list(case.get("expected_log_keys"))) or "none"))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_disaster_run_doc(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "# Disaster Suite Run",
        "",
        "- Result: `{}`".format("PASS" if _token(payload.get("result")) == "complete" else "FAIL"),
        "- Cases Match Expected: `{}`".format(bool(payload.get("cases_match_expected"))),
        "- Case Count: `{}`".format(int(payload.get("case_count", 0) or 0)),
        "- Matched Case Count: `{}`".format(int(payload.get("matched_case_count", 0) or 0)),
        "- Mismatched Case Count: `{}`".format(int(payload.get("mismatched_case_count", 0) or 0)),
        "- Silent Success Cases: `{}`".format(", ".join(_as_list(payload.get("silent_success_case_ids"))) or "none"),
        "- Missing Remediation Cases: `{}`".format(", ".join(_as_list(payload.get("remediation_missing_case_ids"))) or "none"),
        "",
        "## Cases",
        "",
    ]
    for row in _as_list(payload.get("cases")):
        case = _as_map(row)
        lines.append("### {}".format(_token(case.get("case_id"))))
        lines.append("- Result: `{}`".format(_token(case.get("result"))))
        lines.append("- Refusal Code: `{}`".format(_token(case.get("refusal_code")) or "none"))
        lines.append("- Remediation: `{}`".format(_token(case.get("remediation_hint")) or "none"))
        lines.append("- Log Keys: `{}`".format(", ".join(_as_list(case.get("ordered_log_keys"))) or "none"))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_disaster_baseline_doc(baseline: Mapping[str, object]) -> str:
    payload = _as_map(baseline)
    lines = [
        "# Disaster Suite Baseline",
        "",
        "- disaster_suite_version = `{}`".format(int(payload.get("disaster_suite_version", 0) or 0)),
        "- stability_class = `{}`".format(_token(payload.get("stability_class"))),
        "- result = `{}`".format(_token(payload.get("result"))),
        "- required_commit_tag = `{}`".format(_token(_as_map(payload.get("update_policy")).get("required_commit_tag"))),
        "",
        "## Scenarios",
        "",
    ]
    for row in _as_list(payload.get("cases")):
        case = _as_map(row)
        lines.append(
            "- `{}` -> refusal `{}` remediation `{}`".format(
                _token(case.get("case_id")),
                _token(case.get("refusal_code")) or "none",
                _token(case.get("remediation_key")) or "none",
            )
        )
    lines.extend(["", "## Readiness", "", "- Ω-5 ecosystem verify: `ready`", "- Ω-6 update simulation: `ready`"])
    return "\n".join(lines).rstrip() + "\n"


def write_disaster_case_outputs(
    repo_root: str,
    *,
    cases_payload: Mapping[str, object],
    cases_path: str = "",
    model_doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    cases_target = _repo_abs(repo_root_abs, cases_path or DISASTER_CASES_REL)
    model_target = _repo_abs(repo_root_abs, model_doc_path or DISASTER_MODEL_DOC_REL)
    _write_canonical_json(cases_target, _as_map(cases_payload))
    _write_text(model_target, render_disaster_model_doc(cases_payload))
    return {"cases_path": cases_target, "model_doc_path": model_target}


def write_disaster_run_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    baseline_payload: Mapping[str, object] | None = None,
    run_json_path: str = "",
    run_doc_path: str = "",
    baseline_path: str = "",
    baseline_doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    run_json_target = _repo_abs(repo_root_abs, run_json_path or DISASTER_RUN_JSON_REL)
    run_doc_target = _repo_abs(repo_root_abs, run_doc_path or DISASTER_RUN_DOC_REL)
    baseline_target = _repo_abs(repo_root_abs, baseline_path or DISASTER_BASELINE_REL)
    baseline_doc_target = _repo_abs(repo_root_abs, baseline_doc_path or DISASTER_BASELINE_DOC_REL)
    _write_canonical_json(run_json_target, _as_map(report))
    _write_text(run_doc_target, render_disaster_run_doc(report))
    if baseline_payload:
        _write_canonical_json(baseline_target, _as_map(baseline_payload))
        _write_text(baseline_doc_target, render_disaster_baseline_doc(baseline_payload))
    return {
        "run_json_path": run_json_target,
        "run_doc_path": run_doc_target,
        "baseline_path": baseline_target,
        "baseline_doc_path": baseline_doc_target,
    }


def generate_disaster_suite(
    repo_root: str,
    *,
    output_root_rel: str = "",
    write_outputs: bool = True,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    work_root = _repo_abs(repo_root_abs, output_root_rel or DEFAULT_DISASTER_WORK_ROOT_REL)
    context = _base_fixture_context(repo_root_abs, work_root)
    case_rows = []
    for spec in _disaster_case_specs():
        result = _execute_case(context, spec)
        case_rows.append(_case_expectation_row(spec, result))
    record = {
        "disaster_suite_version": DISASTER_SUITE_VERSION,
        "stability_class": DISASTER_SUITE_STABILITY_CLASS,
        "baseline_seed": _token(_as_map(context).get("seed_text")),
        "worldgen_lock_id": WORLDGEN_LOCK_ID,
        "case_count": len(case_rows),
        "cases": sorted(case_rows, key=lambda row: _token(_as_map(row).get("case_id"))),
        "deterministic_fingerprint": "",
    }
    record["deterministic_fingerprint"] = disaster_cases_record_hash(record)
    payload = {"schema_id": DISASTER_SUITE_CASES_SCHEMA_ID, "schema_version": "1.0.0", "record": record}
    written = write_disaster_case_outputs(repo_root_abs, cases_payload=payload) if write_outputs else {}
    return {"result": "complete", "cases_payload": payload, "written": written}


def run_disaster_suite(
    repo_root: str,
    *,
    cases_path: str = "",
    output_root_rel: str = "",
    write_outputs: bool = True,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    cases_payload = load_disaster_suite_cases(repo_root_abs, path=cases_path)
    record = _as_map(cases_payload.get("record"))
    expected_rows = {
        _token(_as_map(row).get("case_id")): _as_map(row)
        for row in _as_list(record.get("cases"))
        if _token(_as_map(row).get("case_id"))
    }
    if not expected_rows:
        report = {
            "schema_id": DISASTER_SUITE_RUN_SCHEMA_ID,
            "schema_version": "1.0.0",
            "result": "violation",
            "cases_match_expected": False,
            "case_count": 0,
            "matched_case_count": 0,
            "mismatched_case_count": 1,
            "mismatched_fields": ["cases.missing"],
            "silent_success_case_ids": [],
            "remediation_missing_case_ids": [],
            "cases": [],
            "deterministic_fingerprint": "",
        }
        report["deterministic_fingerprint"] = disaster_run_report_hash(report)
        return report
    work_root = _repo_abs(repo_root_abs, output_root_rel or DEFAULT_DISASTER_WORK_ROOT_REL)
    context = _base_fixture_context(repo_root_abs, work_root)
    actual_rows = []
    mismatched_fields: list[str] = []
    silent_success_case_ids: list[str] = []
    remediation_missing_case_ids: list[str] = []
    matched_case_count = 0
    for spec in _disaster_case_specs():
        case_id = _token(_as_map(spec).get("case_id"))
        actual = _execute_case(context, spec)
        actual_rows.append(actual)
        expected = _as_map(expected_rows.get(case_id))
        expected_payload = {
            "result": _token(expected.get("expected_result")),
            "exit_code": int(expected.get("expected_exit_code", 0) or 0),
            "refusal_code": _token(expected.get("expected_refusal_code")),
            "remediation_key": _token(expected.get("expected_remediation_key")),
            "remediation_hint": _token(expected.get("expected_remediation_hint")),
            "ordered_log_keys": [str(item) for item in _as_list(expected.get("expected_log_keys")) if _token(item)],
            "logs_category": _token(expected.get("logs_category")),
            "details": _stable_details(expected.get("expected_details")),
        }
        actual_payload = _comparison_payload(actual)
        if actual_payload == expected_payload:
            matched_case_count += 1
        else:
            for field in _CASE_COMPARISON_FIELDS:
                if actual_payload.get(field) != expected_payload.get(field):
                    mismatched_fields.append("{}.{}".format(case_id, field))
        if _token(expected.get("expected_result")) == "refused" and _token(_as_map(actual).get("result")) == "complete":
            silent_success_case_ids.append(case_id)
        if _token(_as_map(actual).get("result")) == "refused" and not _token(_as_map(actual).get("remediation_hint")):
            remediation_missing_case_ids.append(case_id)
    cases_match_expected = not mismatched_fields and not silent_success_case_ids and not remediation_missing_case_ids
    report = {
        "schema_id": DISASTER_SUITE_RUN_SCHEMA_ID,
        "schema_version": "1.0.0",
        "result": "complete" if cases_match_expected else "violation",
        "disaster_suite_version": DISASTER_SUITE_VERSION,
        "stability_class": DISASTER_SUITE_STABILITY_CLASS,
        "baseline_seed": _token(record.get("baseline_seed")),
        "worldgen_lock_id": _token(record.get("worldgen_lock_id")),
        "case_count": len(actual_rows),
        "matched_case_count": matched_case_count,
        "mismatched_case_count": len(sorted(set(mismatched_fields))),
        "cases_match_expected": cases_match_expected,
        "mismatched_fields": sorted(set(mismatched_fields)),
        "silent_success_case_ids": sorted(set(silent_success_case_ids)),
        "remediation_missing_case_ids": sorted(set(remediation_missing_case_ids)),
        "cases": sorted(actual_rows, key=lambda row: _token(_as_map(row).get("case_id"))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = disaster_run_report_hash(report)
    baseline_payload = {
        "schema_id": DISASTER_SUITE_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "baseline_id": "disaster_suite.baseline.v0",
        "disaster_suite_version": DISASTER_SUITE_VERSION,
        "stability_class": DISASTER_SUITE_STABILITY_CLASS,
        "baseline_seed": _token(record.get("baseline_seed")),
        "worldgen_lock_id": _token(record.get("worldgen_lock_id")),
        "case_count": len(actual_rows),
        "result": "complete" if cases_match_expected else "violation",
        "cases": sorted(actual_rows, key=lambda row: _token(_as_map(row).get("case_id"))),
        "update_policy": {"required_commit_tag": DISASTER_REGRESSION_REQUIRED_TAG},
        "deterministic_fingerprint": "",
    }
    baseline_payload["deterministic_fingerprint"] = disaster_baseline_hash(baseline_payload)
    if write_outputs:
        report["written"] = write_disaster_run_outputs(repo_root_abs, report=report, baseline_payload=baseline_payload)
    return dict(report, baseline_payload=baseline_payload)


__all__ = [
    "DISASTER_BASELINE_DOC_REL",
    "DISASTER_BASELINE_REL",
    "DISASTER_CASES_REL",
    "DISASTER_CASES_SCHEMA_ID",
    "DISASTER_MODEL_DOC_REL",
    "DISASTER_REGRESSION_REQUIRED_TAG",
    "DISASTER_RETRO_AUDIT_REL",
    "DISASTER_RUN_DOC_REL",
    "DISASTER_RUN_JSON_REL",
    "DISASTER_SUITE_BASELINE_SCHEMA_ID",
    "DISASTER_SUITE_RUN_SCHEMA_ID",
    "disaster_baseline_hash",
    "disaster_cases_record_hash",
    "disaster_run_report_hash",
    "generate_disaster_suite",
    "load_disaster_suite_baseline",
    "load_disaster_suite_cases",
    "render_disaster_baseline_doc",
    "render_disaster_model_doc",
    "render_disaster_run_doc",
    "run_disaster_suite",
    "write_disaster_case_outputs",
    "write_disaster_run_outputs",
]
