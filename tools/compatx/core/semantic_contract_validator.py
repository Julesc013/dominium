"""Semantic contract registry and universe bundle validation helpers."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, Iterable, List, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))

if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from src.meta_extensions_engine import normalize_extensions_tree


SEMANTIC_CONTRACT_REGISTRY_REL = os.path.join("data", "registries", "semantic_contract_registry.json")
SEMANTIC_CONTRACT_BUNDLE_SCHEMA_NAME = "universe_contract_bundle"

CONTRACT_FIELD_ORDER: Tuple[Tuple[str, str], ...] = (
    ("contract_worldgen_refinement_version", "contract.worldgen.refinement.v1"),
    ("contract_overlay_merge_version", "contract.overlay.merge.v1"),
    ("contract_logic_eval_version", "contract.logic.eval.v1"),
    ("contract_proc_capsule_version", "contract.proc.capsule.v1"),
    ("contract_sys_collapse_version", "contract.sys.collapse.v1"),
    ("contract_geo_metric_version", "contract.geo.metric.v1"),
    ("contract_geo_projection_version", "contract.geo.projection.v1"),
    ("contract_geo_partition_version", "contract.geo.partition.v1"),
    ("contract_appshell_lifecycle_version", "contract.appshell.lifecycle.v1"),
)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = normalize_extensions_tree(json.load(open(path, "r", encoding="utf-8")))
    except (OSError, ValueError):
        return {}, "invalid json: {}".format(path.replace("\\", "/"))
    if not isinstance(payload, dict):
        return {}, "invalid root object: {}".format(path.replace("\\", "/"))
    return payload, ""


def _entry_fingerprint(row: Mapping[str, object]) -> str:
    body = dict(row)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def bundle_hash(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def registry_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(payload)


def load_semantic_contract_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, SEMANTIC_CONTRACT_REGISTRY_REL))


def semantic_contract_ids(payload: Mapping[str, object] | None) -> List[str]:
    record = dict((payload or {}).get("record") or {})
    rows = list(record.get("contracts") or [])
    ids = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("contract_id", "")).strip()
        if token:
            ids.append(token)
    return sorted(set(ids))


def validate_semantic_contract_registry(payload: Mapping[str, object] | None) -> List[str]:
    errors: List[str] = []
    root = dict(payload or {})
    if str(root.get("schema_id", "")).strip() != "dominium.registry.semantic_contract_registry":
        errors.append("refuse.semantic_contract_registry_schema_id")
    if str(root.get("schema_version", "")).strip() != "1.0.0":
        errors.append("refuse.semantic_contract_registry_schema_version")
    record = dict(root.get("record") or {})
    if str(record.get("registry_id", "")).strip() != "dominium.registry.semantic_contracts":
        errors.append("refuse.semantic_contract_registry_id")
    rows = list(record.get("contracts") or [])
    if not rows:
        errors.append("refuse.semantic_contract_registry_missing_rows")
        return sorted(set(errors))

    by_id: Dict[str, Dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("refuse.semantic_contract_row_type")
            continue
        contract_id = str(row.get("contract_id", "")).strip()
        if not contract_id:
            errors.append("refuse.semantic_contract_id_missing")
            continue
        by_id[contract_id] = dict(row)
        if str(row.get("version", "")).strip() != "1.0.0":
            errors.append("refuse.semantic_contract_version_missing")
        for key in ("description",):
            if not str(row.get(key, "")).strip():
                errors.append("refuse.semantic_contract_{}_missing".format(key))
        for key in ("guaranteed_invariants", "allowed_evolution", "breaking_change_requires"):
            values = row.get(key)
            if not isinstance(values, list) or not values:
                errors.append("refuse.semantic_contract_{}_missing".format(key))
        expected_fingerprint = _entry_fingerprint(row)
        if str(row.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
            errors.append("refuse.semantic_contract_fingerprint_mismatch")

    required_ids = [default_id for _field, default_id in CONTRACT_FIELD_ORDER]
    for contract_id in required_ids:
        if contract_id not in by_id:
            errors.append("refuse.semantic_contract_missing:{}".format(contract_id))
    return sorted(set(errors))


def build_default_universe_contract_bundle(registry_payload: Mapping[str, object] | None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "deterministic_fingerprint": "",
        "extensions": {
            "semantic_contract_registry_hash": registry_hash(registry_payload or {}),
            "migration_policy": "compatx.explicit_only",
        },
    }
    for field_name, contract_id in CONTRACT_FIELD_ORDER:
        payload[field_name] = contract_id
    payload["deterministic_fingerprint"] = bundle_hash(payload)
    return payload


def validate_universe_contract_bundle(repo_root: str, payload: Mapping[str, object] | None, registry_payload: Mapping[str, object] | None) -> List[str]:
    bundle = dict(payload or {})
    errors: List[str] = []
    valid = validate_instance(repo_root=repo_root, schema_name=SEMANTIC_CONTRACT_BUNDLE_SCHEMA_NAME, payload=bundle, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        errors.append("refuse.universe_contract_bundle_schema")
    registry_errors = validate_semantic_contract_registry(registry_payload)
    if registry_errors:
        errors.extend(registry_errors)
        return sorted(set(errors))
    known_ids = set(semantic_contract_ids(registry_payload))
    for field_name, _default_id in CONTRACT_FIELD_ORDER:
        token = str(bundle.get(field_name, "")).strip()
        if token not in known_ids:
            errors.append("refuse.universe_contract_bundle_unknown_contract:{}".format(field_name))
    expected_registry_hash = registry_hash(registry_payload or {})
    actual_registry_hash = str(dict(bundle.get("extensions") or {}).get("semantic_contract_registry_hash", "")).strip()
    if actual_registry_hash != expected_registry_hash:
        errors.append("refuse.universe_contract_bundle_registry_hash")
    expected_bundle_hash = bundle_hash(bundle)
    if str(bundle.get("deterministic_fingerprint", "")).strip() != expected_bundle_hash:
        errors.append("refuse.universe_contract_bundle_fingerprint")
    return sorted(set(errors))


def build_semantic_contract_proof_bundle(registry_payload: Mapping[str, object] | None, bundle_payload: Mapping[str, object] | None) -> dict:
    bundle = dict(bundle_payload or {})
    return {
        "semantic_contract_registry_hash": registry_hash(registry_payload or {}),
        "universe_contract_bundle_hash": bundle_hash(bundle),
        "pinned_contract_versions": {
            field_name: str(bundle.get(field_name, "")).strip()
            for field_name, _default_id in CONTRACT_FIELD_ORDER
        },
    }


def validate_replay_contract_match(
    *,
    expected_bundle: Mapping[str, object] | None,
    actual_bundle: Mapping[str, object] | None,
    migration_invoked: bool = False,
) -> List[str]:
    errors: List[str] = []
    expected = dict(expected_bundle or {})
    actual = dict(actual_bundle or {})
    if migration_invoked:
        return []
    for field_name, _default_id in CONTRACT_FIELD_ORDER:
        expected_token = str(expected.get(field_name, "")).strip()
        actual_token = str(actual.get(field_name, "")).strip()
        if expected_token != actual_token:
            errors.append("refuse.semantic_contract_mismatch")
            break
    expected_registry_hash = str(dict(expected.get("extensions") or {}).get("semantic_contract_registry_hash", "")).strip()
    actual_registry_hash = str(dict(actual.get("extensions") or {}).get("semantic_contract_registry_hash", "")).strip()
    if expected_registry_hash != actual_registry_hash:
        errors.append("refuse.semantic_contract_registry_mismatch")
    return sorted(set(errors))


def contract_tokens_missing_entries(repo_root: str, registry_payload: Mapping[str, object] | None, paths: Iterable[str]) -> List[str]:
    known_ids = set(semantic_contract_ids(registry_payload))
    missing = set()
    for rel_path in paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for token in sorted(set(re.findall(r"contract\.[a-z0-9_.]+\.v[0-9]+", text))):
            if token not in known_ids:
                missing.add(token)
    return sorted(missing)
