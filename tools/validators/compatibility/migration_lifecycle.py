"""Deterministic MIGRATION-LIFECYCLE-0 policy and decision helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


ARTIFACT_KIND_BLUEPRINT = "artifact.blueprint"
ARTIFACT_KIND_COMPONENT_GRAPH = "artifact.component_graph"
ARTIFACT_KIND_INSTALL_MANIFEST = "artifact.install_manifest"
ARTIFACT_KIND_INSTALL_PLAN = "artifact.install_plan"
ARTIFACT_KIND_INSTANCE_MANIFEST = "artifact.instance_manifest"
ARTIFACT_KIND_NEGOTIATION_RECORD = "artifact.negotiation_record"
ARTIFACT_KIND_PACK_LOCK = "artifact.pack_lock"
ARTIFACT_KIND_PROFILE_BUNDLE = "artifact.profile_bundle"
ARTIFACT_KIND_RELEASE_INDEX = "artifact.release_index"
ARTIFACT_KIND_RELEASE_MANIFEST = "artifact.release_manifest"
ARTIFACT_KIND_SAVE = "artifact.save"
ARTIFACT_KIND_SESSION_TEMPLATE = "artifact.session_template"

ARTIFACT_KIND_IDS = (
    ARTIFACT_KIND_BLUEPRINT,
    ARTIFACT_KIND_COMPONENT_GRAPH,
    ARTIFACT_KIND_INSTALL_MANIFEST,
    ARTIFACT_KIND_INSTALL_PLAN,
    ARTIFACT_KIND_INSTANCE_MANIFEST,
    ARTIFACT_KIND_NEGOTIATION_RECORD,
    ARTIFACT_KIND_PACK_LOCK,
    ARTIFACT_KIND_PROFILE_BUNDLE,
    ARTIFACT_KIND_RELEASE_INDEX,
    ARTIFACT_KIND_RELEASE_MANIFEST,
    ARTIFACT_KIND_SAVE,
    ARTIFACT_KIND_SESSION_TEMPLATE,
)

DECISION_LOAD = "decision.load"
DECISION_MIGRATE = "decision.migrate"
DECISION_READ_ONLY = "decision.read_only"
DECISION_REFUSE = "decision.refuse"

REFUSAL_MIGRATION_NO_PATH = "refusal.migration.no_path"
REFUSAL_MIGRATION_NOT_ALLOWED = "refusal.migration.not_allowed"
REFUSAL_MIGRATION_CONTRACT_INCOMPATIBLE = "refusal.migration.contract_incompatible"

MIGRATION_POLICY_REGISTRY_REL = os.path.join("data", "registries", "migration_policy_registry.json")
MIGRATION_REGISTRY_REL = os.path.join("data", "registries", "migration_registry.json")

_LEGACY_COMPONENT_TO_ARTIFACT_KIND = {
    "blueprint": ARTIFACT_KIND_BLUEPRINT,
    "pack_lock": ARTIFACT_KIND_PACK_LOCK,
    "profile": ARTIFACT_KIND_PROFILE_BUNDLE,
    "save": ARTIFACT_KIND_SAVE,
    "session_template": ARTIFACT_KIND_SESSION_TEMPLATE,
}

_ARTIFACT_VERSION_FIELD_ALIASES = {
    ARTIFACT_KIND_BLUEPRINT: ("format_version",),
    ARTIFACT_KIND_COMPONENT_GRAPH: ("format_version",),
    ARTIFACT_KIND_INSTALL_MANIFEST: ("format_version",),
    ARTIFACT_KIND_INSTALL_PLAN: ("format_version",),
    ARTIFACT_KIND_INSTANCE_MANIFEST: ("format_version",),
    ARTIFACT_KIND_NEGOTIATION_RECORD: ("schema_version", "format_version"),
    ARTIFACT_KIND_PACK_LOCK: ("format_version",),
    ARTIFACT_KIND_PROFILE_BUNDLE: ("format_version",),
    ARTIFACT_KIND_RELEASE_INDEX: ("format_version",),
    ARTIFACT_KIND_RELEASE_MANIFEST: ("manifest_version", "format_version"),
    ARTIFACT_KIND_SAVE: ("save_format_version", "format_version"),
    ARTIFACT_KIND_SESSION_TEMPLATE: ("format_version",),
}

_CONTRACT_HASH_FIELD_ALIASES = (
    "semantic_contract_bundle_hash",
    "universe_contract_bundle_hash",
    "contract_bundle_hash",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: object) -> str:
    return _token(path).replace("\\", "/")


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _semver_tuple(value: object) -> Tuple[int, int, int]:
    token = _token(value)
    parts = token.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    out = []
    for part in parts:
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return out[0], out[1], out[2]


def _version_lt(left: str, right: str) -> bool:
    return _semver_tuple(left) < _semver_tuple(right)


def _version_gt(left: str, right: str) -> bool:
    return _semver_tuple(left) > _semver_tuple(right)


def _version_in_range(version: str, range_row: Mapping[str, object] | None) -> bool:
    if not _token(version):
        return False
    item = _as_map(range_row)
    minimum = _token(item.get("min_version"))
    maximum = _token(item.get("max_version"))
    if not minimum or not maximum:
        return False
    version_tuple = _semver_tuple(version)
    return _semver_tuple(minimum) <= version_tuple <= _semver_tuple(maximum)


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _decision_record_seed(payload: Mapping[str, object]) -> dict:
    body = dict(_normalize_tree(dict(payload or {})))
    extensions = _as_map(body.get("extensions"))
    # Preserve artifact_path for operator diagnostics, but exclude it from
    # deterministic identity so temp roots and bundle mount points do not
    # perturb migration record hashes.
    if "artifact_path" in extensions:
        extensions = {key: value for key, value in extensions.items() if str(key) != "artifact_path"}
    body["extensions"] = extensions
    body["deterministic_fingerprint"] = ""
    return body


def canonicalize_version_range(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "min_version": _token(item.get("min_version")),
        "max_version": _token(item.get("max_version")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    if _version_gt(_token(normalized.get("min_version")), _token(normalized.get("max_version"))):
        normalized["max_version"] = _token(normalized.get("min_version"))
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_migration_policy(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "artifact_kind_id": _token(item.get("artifact_kind_id")),
        "backward_read_range": canonicalize_version_range(item.get("backward_read_range")),
        "forward_read_range": canonicalize_version_range(item.get("forward_read_range")),
        "migration_supported_range": canonicalize_version_range(item.get("migration_supported_range")),
        "read_only_allowed": bool(item.get("read_only_allowed", False)),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
        "stability": dict(_normalize_tree(_as_map(item.get("stability")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(
        {key: value for key, value in normalized.items() if key != "stability"}
    )
    return normalized


def canonicalize_migration_chain(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    steps = []
    for row in _as_list(item.get("steps")):
        step = _as_map(row)
        if not _token(step.get("migration_id")):
            continue
        steps.append(
            {
                "migration_id": _token(step.get("migration_id")),
                "from_version": _token(step.get("from_version")),
                "to_version": _token(step.get("to_version")),
                "artifact_kind_id": _token(step.get("artifact_kind_id")),
                "deterministic_transform_function_id": _token(step.get("deterministic_transform_function_id")),
                "extensions": dict(_normalize_tree(_as_map(step.get("extensions")))),
            }
        )
    steps = sorted(steps, key=lambda row: (_token(row.get("from_version")), _token(row.get("to_version")), _token(row.get("migration_id"))))
    normalized = {
        "chain_id": _token(item.get("chain_id")) or "migration_chain.{}".format(canonical_sha256({"steps": steps})[:24]),
        "artifact_kind_id": _token(item.get("artifact_kind_id")),
        "steps": steps,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_migration_decision_record(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    chain_rows = []
    for row in _as_list(item.get("migration_chain")):
        step = _as_map(row)
        if not _token(step.get("migration_id")):
            continue
        chain_rows.append(
            {
                "migration_id": _token(step.get("migration_id")),
                "from_version": _token(step.get("from_version")),
                "to_version": _token(step.get("to_version")),
                "artifact_kind_id": _token(step.get("artifact_kind_id")),
                "deterministic_transform_function_id": _token(step.get("deterministic_transform_function_id")),
                "extensions": dict(_normalize_tree(_as_map(step.get("extensions")))),
            }
        )
    chain_rows = sorted(chain_rows, key=lambda row: (_token(row.get("from_version")), _token(row.get("to_version")), _token(row.get("migration_id"))))
    normalized = {
        "decision_record_id": _token(item.get("decision_record_id")),
        "artifact_kind_id": _token(item.get("artifact_kind_id")),
        "observed_version": _token(item.get("observed_version")),
        "target_version": _token(item.get("target_version")),
        "decision_action_id": _token(item.get("decision_action_id")),
        "read_only_applied": bool(item.get("read_only_applied", False)),
        "migration_chain": chain_rows,
        "refusal_code": _token(item.get("refusal_code")),
        "remediation_hint": _token(item.get("remediation_hint")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    seed = _decision_record_seed(normalized)
    normalized["decision_record_id"] = _token(normalized.get("decision_record_id")) or "migration_decision.{}".format(canonical_sha256(seed)[:24])
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(seed, decision_record_id=normalized["decision_record_id"]))
    return normalized


def _read_json(path: str) -> dict:
    try:
        with open(os.path.normpath(os.path.abspath(str(path))), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_migration_policy_registry(repo_root: str) -> dict:
    payload = _read_json(os.path.join(os.path.abspath(repo_root), MIGRATION_POLICY_REGISTRY_REL))
    record = _as_map(payload.get("record"))
    policies = []
    for row in _as_list(record.get("migration_policies")):
        item = canonicalize_migration_policy(row)
        if _token(item.get("artifact_kind_id")):
            policies.append(item)
    payload["record"] = {
        "registry_id": _token(record.get("registry_id")) or "dominium.registry.compat.migration_policy_registry",
        "registry_version": _token(record.get("registry_version")) or "1.0.0",
        "migration_policies": sorted(policies, key=lambda row: _token(row.get("artifact_kind_id"))),
        "extensions": dict(_normalize_tree(_as_map(record.get("extensions")))),
    }
    return payload


def select_migration_policy(registry_payload: Mapping[str, object] | None, artifact_kind_id: str) -> dict:
    record = _as_map(_as_map(registry_payload).get("record"))
    wanted = _token(artifact_kind_id)
    for row in _as_list(record.get("migration_policies")):
        item = canonicalize_migration_policy(row)
        if _token(item.get("artifact_kind_id")) == wanted:
            return item
    return {}


def _canonicalize_migration_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    artifact_kind_id = _token(item.get("artifact_kind_id")) or _LEGACY_COMPONENT_TO_ARTIFACT_KIND.get(_token(item.get("component_type")), "")
    return {
        "migration_id": _token(item.get("migration_id")),
        "from_version": _token(item.get("from_version")),
        "to_version": _token(item.get("to_version")),
        "artifact_kind_id": artifact_kind_id,
        "component_type": _token(item.get("component_type")),
        "deterministic_required": bool(item.get("deterministic_required", True)),
        "migration_tool": _token(item.get("migration_tool")),
        "version_field": _token(item.get("version_field")),
        "deterministic_transform_function_id": _token(item.get("deterministic_transform_function_id")),
        "semantic_contract_requirements": list(_normalize_tree(_as_list(item.get("semantic_contract_requirements")))),
        "contract_requirements": dict(_normalize_tree(_as_map(item.get("contract_requirements")))),
        "notes": _token(item.get("notes")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
        "stability": dict(_normalize_tree(_as_map(item.get("stability")))),
    }


def load_migration_rows(repo_root: str) -> list[dict]:
    payload = _read_json(os.path.join(os.path.abspath(repo_root), MIGRATION_REGISTRY_REL))
    record = _as_map(payload.get("record"))
    rows = []
    for row in _as_list(record.get("migrations")):
        item = _canonicalize_migration_row(row)
        if _token(item.get("migration_id")) and _token(item.get("artifact_kind_id")):
            rows.append(item)
    return sorted(rows, key=lambda row: (_token(row.get("artifact_kind_id")), _token(row.get("from_version")), _token(row.get("to_version")), _token(row.get("migration_id"))))


def build_migration_chain(
    repo_root: str,
    *,
    artifact_kind_id: str,
    from_version: str,
    to_version: str,
) -> dict:
    target = _token(to_version)
    current = _token(from_version)
    rows = [row for row in load_migration_rows(repo_root) if _token(row.get("artifact_kind_id")) == _token(artifact_kind_id)]
    by_from = {}
    for row in rows:
        token = _token(row.get("from_version"))
        if token and token not in by_from:
            by_from[token] = row
    steps = []
    guard = set()
    while current and current != target:
        if current in guard:
            return {}
        guard.add(current)
        row = dict(by_from.get(current) or {})
        if not row:
            return {}
        steps.append(row)
        current = _token(row.get("to_version"))
    if current != target:
        return {}
    return canonicalize_migration_chain(
        {
            "chain_id": "migration_chain.{}.{}.{}".format(_token(artifact_kind_id), _token(from_version), target).replace(":", "_"),
            "artifact_kind_id": _token(artifact_kind_id),
            "steps": steps,
            "extensions": {},
        }
    )


def _current_version_from_policy(policy: Mapping[str, object]) -> str:
    return _token(_as_map(policy.get("extensions")).get("current_version")) or _token(_as_map(policy.get("backward_read_range")).get("max_version"))


def _version_field_from_policy(policy: Mapping[str, object], artifact_kind_id: str) -> str:
    return _token(_as_map(policy.get("extensions")).get("version_field")) or _ARTIFACT_VERSION_FIELD_ALIASES.get(_token(artifact_kind_id), ("format_version",))[0]


def _missing_version_treatment(policy: Mapping[str, object]) -> str:
    return _token(_as_map(policy.get("extensions")).get("missing_version_treatment")) or "assume_current"


def payload_contract_bundle_hash(payload: Mapping[str, object] | None, policy: Mapping[str, object] | None = None) -> str:
    item = _as_map(payload)
    policy_field = _token(_as_map(_as_map(policy).get("extensions")).get("contract_hash_field"))
    if policy_field and _token(item.get(policy_field)):
        return _token(item.get(policy_field))
    for field_name in _CONTRACT_HASH_FIELD_ALIASES:
        if _token(item.get(field_name)):
            return _token(item.get(field_name))
    return ""


def extract_artifact_version(
    artifact_kind_id: str,
    payload: Mapping[str, object] | None,
    *,
    policy: Mapping[str, object] | None = None,
) -> tuple[str, str]:
    item = _as_map(payload)
    field_name = _version_field_from_policy(_as_map(policy), artifact_kind_id)
    aliases = _ARTIFACT_VERSION_FIELD_ALIASES.get(_token(artifact_kind_id), (field_name,)) or (field_name,)
    for candidate in aliases:
        token = _token(item.get(candidate))
        if token:
            return token, candidate
    if _missing_version_treatment(_as_map(policy)) == "assume_current":
        return _current_version_from_policy(_as_map(policy)), field_name
    return "", field_name


def determine_migration_decision(
    repo_root: str,
    *,
    artifact_kind_id: str,
    payload: Mapping[str, object] | None,
    allow_read_only: bool = False,
    expected_contract_bundle_hash: str = "",
    artifact_path: str = "",
) -> dict:
    registry = load_migration_policy_registry(repo_root)
    policy = select_migration_policy(registry, artifact_kind_id)
    if not policy:
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": "",
                "target_version": "",
                "decision_action_id": DECISION_REFUSE,
                "read_only_applied": False,
                "migration_chain": [],
                "refusal_code": REFUSAL_MIGRATION_NO_PATH,
                "remediation_hint": "Declare a migration policy for the artifact kind before loading it.",
                "extensions": {"artifact_path": _norm(artifact_path), "policy_missing": True},
            }
        )
    current_version = _current_version_from_policy(policy)
    observed_version, version_field = extract_artifact_version(_token(artifact_kind_id), payload, policy=policy)
    actual_contract_hash = payload_contract_bundle_hash(payload, policy)
    expected_contract_hash = _token(expected_contract_bundle_hash)
    if expected_contract_hash and actual_contract_hash and expected_contract_hash != actual_contract_hash:
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": observed_version or current_version,
                "target_version": current_version,
                "decision_action_id": DECISION_REFUSE,
                "read_only_applied": False,
                "migration_chain": [],
                "refusal_code": REFUSAL_MIGRATION_CONTRACT_INCOMPATIBLE,
                "remediation_hint": "Open the artifact with a build pinned to contract bundle `{}` or run a contract-aware migration tool.".format(actual_contract_hash or "<artifact_contract_bundle_hash>"),
                "extensions": {
                    "artifact_path": _norm(artifact_path),
                    "version_field": version_field,
                    "expected_contract_bundle_hash": expected_contract_hash,
                    "actual_contract_bundle_hash": actual_contract_hash,
                },
            }
        )
    if not observed_version:
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": "",
                "target_version": current_version,
                "decision_action_id": DECISION_REFUSE,
                "read_only_applied": False,
                "migration_chain": [],
                "refusal_code": REFUSAL_MIGRATION_NOT_ALLOWED,
                "remediation_hint": "Stamp the artifact with a declared format/schema version before loading it.",
                "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field},
            }
        )
    if observed_version == current_version or _version_in_range(observed_version, _as_map(policy.get("backward_read_range"))):
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": observed_version,
                "target_version": current_version,
                "decision_action_id": DECISION_LOAD,
                "read_only_applied": False,
                "migration_chain": [],
                "refusal_code": "",
                "remediation_hint": "",
                "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field},
            }
        )
    if _version_lt(observed_version, current_version):
        chain = build_migration_chain(
            repo_root,
            artifact_kind_id=_token(artifact_kind_id),
            from_version=observed_version,
            to_version=current_version,
        )
        if chain and _version_in_range(observed_version, _as_map(policy.get("migration_supported_range"))):
            return canonicalize_migration_decision_record(
                {
                    "artifact_kind_id": _token(artifact_kind_id),
                    "observed_version": observed_version,
                    "target_version": current_version,
                    "decision_action_id": DECISION_MIGRATE,
                    "read_only_applied": False,
                    "migration_chain": list(chain.get("steps") or []),
                    "refusal_code": "",
                    "remediation_hint": "Run the deterministic migration chain before loading this artifact for write access.",
                    "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field, "chain_id": _token(chain.get("chain_id"))},
                }
            )
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": observed_version,
                "target_version": current_version,
                "decision_action_id": DECISION_REFUSE,
                "read_only_applied": False,
                "migration_chain": [],
                "refusal_code": REFUSAL_MIGRATION_NO_PATH,
                "remediation_hint": "Use an older build that supports version `{}` or install a deterministic migration chain to `{}`.".format(observed_version, current_version),
                "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field},
            }
        )
    if allow_read_only and bool(policy.get("read_only_allowed", False)) and _version_in_range(observed_version, _as_map(policy.get("forward_read_range"))):
        return canonicalize_migration_decision_record(
            {
                "artifact_kind_id": _token(artifact_kind_id),
                "observed_version": observed_version,
                "target_version": current_version,
                "decision_action_id": DECISION_READ_ONLY,
                "read_only_applied": True,
                "migration_chain": [],
                "refusal_code": "",
                "remediation_hint": "Open the artifact in read-only mode or use a newer build that supports version `{}`.".format(observed_version),
                "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field},
            }
        )
    return canonicalize_migration_decision_record(
        {
            "artifact_kind_id": _token(artifact_kind_id),
            "observed_version": observed_version,
            "target_version": current_version,
            "decision_action_id": DECISION_REFUSE,
            "read_only_applied": False,
            "migration_chain": [],
            "refusal_code": REFUSAL_MIGRATION_NOT_ALLOWED,
            "remediation_hint": "Use a newer build, open the artifact read-only if policy allows it, or install a deterministic migration path.",
            "extensions": {"artifact_path": _norm(artifact_path), "version_field": version_field},
        }
    )


def plan_migration_path(
    repo_root: str,
    *,
    artifact_kind_id: str,
    artifact_path: str,
    allow_read_only: bool = False,
    expected_contract_bundle_hash: str = "",
) -> dict:
    abs_path = os.path.normpath(os.path.abspath(str(artifact_path)))
    payload = _read_json(abs_path)
    return determine_migration_decision(
        repo_root,
        artifact_kind_id=artifact_kind_id,
        payload=payload,
        allow_read_only=allow_read_only,
        expected_contract_bundle_hash=expected_contract_bundle_hash,
        artifact_path=abs_path,
    )


__all__ = [
    "ARTIFACT_KIND_BLUEPRINT",
    "ARTIFACT_KIND_COMPONENT_GRAPH",
    "ARTIFACT_KIND_INSTALL_MANIFEST",
    "ARTIFACT_KIND_INSTALL_PLAN",
    "ARTIFACT_KIND_INSTANCE_MANIFEST",
    "ARTIFACT_KIND_NEGOTIATION_RECORD",
    "ARTIFACT_KIND_PACK_LOCK",
    "ARTIFACT_KIND_PROFILE_BUNDLE",
    "ARTIFACT_KIND_RELEASE_INDEX",
    "ARTIFACT_KIND_RELEASE_MANIFEST",
    "ARTIFACT_KIND_SAVE",
    "ARTIFACT_KIND_SESSION_TEMPLATE",
    "ARTIFACT_KIND_IDS",
    "DECISION_LOAD",
    "DECISION_MIGRATE",
    "DECISION_READ_ONLY",
    "DECISION_REFUSE",
    "MIGRATION_POLICY_REGISTRY_REL",
    "MIGRATION_REGISTRY_REL",
    "REFUSAL_MIGRATION_CONTRACT_INCOMPATIBLE",
    "REFUSAL_MIGRATION_NO_PATH",
    "REFUSAL_MIGRATION_NOT_ALLOWED",
    "build_migration_chain",
    "canonicalize_migration_chain",
    "canonicalize_migration_decision_record",
    "canonicalize_migration_policy",
    "canonicalize_version_range",
    "deterministic_fingerprint",
    "determine_migration_decision",
    "extract_artifact_version",
    "load_migration_policy_registry",
    "load_migration_rows",
    "payload_contract_bundle_hash",
    "plan_migration_path",
    "select_migration_policy",
]
