"""Shared fixtures for PACK-COMPAT-1 TestX coverage."""

from __future__ import annotations

import os

from tools.xstack.testx.tests.pack_compat0_testlib import (
    cleanup_temp_repo,
    ensure_repo_on_path,
    make_temp_pack_compat_repo,
    mutate_pack_compat,
    read_json,
    write_json,
)


def _fingerprint(payload: dict) -> str:
    from tools.xstack.compatx.canonical_json import canonical_sha256

    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _canonical_pack_hash(payload: dict) -> str:
    from tools.xstack.compatx.canonical_json import canonical_sha256

    body = dict(payload)
    body["canonical_hash"] = ""
    return canonical_sha256(body)


def _find_pack_dir(repo_root: str, pack_id: str) -> str:
    packs_root = os.path.join(repo_root, "packs")
    for root, _dirs, files in os.walk(packs_root):
        if "pack.json" not in files:
            continue
        payload = read_json(os.path.join(root, "pack.json"))
        if str(payload.get("pack_id", "")).strip() == str(pack_id).strip():
            return root
    raise FileNotFoundError("unable to locate pack {}".format(pack_id))


def _normalize_fixture_manifest_hashes(temp_repo: str) -> None:
    packs_root = os.path.join(temp_repo, "packs")
    for root, _dirs, files in os.walk(packs_root):
        if "pack.json" not in files:
            continue
        manifest_path = os.path.join(root, "pack.json")
        manifest = read_json(manifest_path)
        manifest["canonical_hash"] = _canonical_pack_hash(manifest)
        write_json(manifest_path, manifest)


def _rewrite_capability_sidecars(pack_dir: str, capability_ids: list[str]) -> None:
    capability_path = os.path.join(pack_dir, "pack.capabilities.json")
    compat_path = os.path.join(pack_dir, "pack.compat.json")
    sorted_caps = sorted(set(str(item).strip() for item in list(capability_ids or []) if str(item).strip()))
    if os.path.isfile(capability_path):
        payload = read_json(capability_path)
        payload["capability_ids"] = list(sorted_caps)
        payload["deterministic_fingerprint"] = _fingerprint(payload)
        write_json(capability_path, payload)
    if os.path.isfile(compat_path):
        payload = read_json(compat_path)
        payload["capability_ids"] = list(sorted_caps)
        payload["deterministic_fingerprint"] = _fingerprint(payload)
        write_json(compat_path, payload)


def verify_fixture_pack_set(
    source_repo_root: str,
    temp_repo: str,
    *,
    bundle_id: str = "bundle.base.lab",
    mod_policy_id: str = "mod_policy.lab",
    overlay_conflict_policy_id: str = "",
    universe_contract_bundle_path: str = "",
) -> dict:
    from src.packs.compat import verify_pack_set

    _normalize_fixture_manifest_hashes(temp_repo)
    return verify_pack_set(
        repo_root=temp_repo,
        bundle_id=str(bundle_id),
        mod_policy_id=str(mod_policy_id),
        overlay_conflict_policy_id=str(overlay_conflict_policy_id),
        schema_repo_root=source_repo_root,
        universe_contract_bundle_path=str(universe_contract_bundle_path),
    )


def report_refusal_codes(result: dict) -> list[str]:
    report = dict(result.get("report") or {})
    codes = set(str(item).strip() for item in list(report.get("refusal_codes") or []) if str(item).strip())
    for row in list(result.get("errors") or []):
        if isinstance(row, dict):
            token = str(row.get("code", "")).strip()
            if token:
                codes.add(token)
    return sorted(codes)


def add_overlay_conflict_fixture(temp_repo: str) -> None:
    pack_specs = (
        ("pack.test.base", "layer.pack_compat1.conflict.base", "registry.test.overlay.conflict.base", "Conflict Alpha"),
        ("pack.test.domain", "layer.pack_compat1.conflict.domain", "registry.test.overlay.conflict.domain", "Conflict Beta"),
    )
    for pack_id, layer_id, contrib_prefix, value in pack_specs:
        pack_dir = _find_pack_dir(temp_repo, pack_id)
        manifest_path = os.path.join(pack_dir, "pack.json")
        manifest = read_json(manifest_path)
        manifest["contribution_types"] = sorted(set(list(manifest.get("contribution_types") or []) + ["registry_entries"]))
        contributions = list(manifest.get("contributions") or [])
        layer_path = os.path.join("data", "{}.layer.json".format(contrib_prefix))
        patch_path = os.path.join("data", "{}.patch.json".format(contrib_prefix))
        contributions.append(
            {
                "type": "registry_entries",
                "id": "{}.layer".format(contrib_prefix),
                "path": layer_path.replace("\\", "/"),
            }
        )
        contributions.append(
            {
                "type": "registry_entries",
                "id": "{}.patch".format(contrib_prefix),
                "path": patch_path.replace("\\", "/"),
            }
        )
        manifest["contributions"] = contributions
        manifest["canonical_hash"] = _canonical_pack_hash(manifest)
        write_json(manifest_path, manifest)
        _rewrite_capability_sidecars(pack_dir, ["cap.overlay_patch"])

        layer_payload = {
            "schema_version": "1.0.0",
            "layer_id": layer_id,
            "layer_kind": "mod",
            "precedence_order": 200,
            "source_ref": "overlay.{}.conflict".format(pack_id),
            "extensions": {
                "pack_id": pack_id,
                "pack_hash": str(manifest.get("canonical_hash", "")).strip(),
                "signature_status": str(manifest.get("signature_status", "")).strip(),
            },
            "deterministic_fingerprint": "",
        }
        layer_payload["deterministic_fingerprint"] = _fingerprint(layer_payload)

        patch_row = {
            "schema_version": "1.0.0",
            "target_object_id": "object.test.shared",
            "property_path": "display_name",
            "operation": "set",
            "value": value,
            "originating_layer_id": layer_id,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        patch_row["deterministic_fingerprint"] = _fingerprint(patch_row)
        patch_payload = {
            "property_patches": [patch_row],
        }

        write_json(os.path.join(pack_dir, layer_path), layer_payload)
        write_json(os.path.join(pack_dir, patch_path), patch_payload)


__all__ = [
    "add_overlay_conflict_fixture",
    "cleanup_temp_repo",
    "ensure_repo_on_path",
    "make_temp_pack_compat_repo",
    "mutate_pack_compat",
    "read_json",
    "report_refusal_codes",
    "verify_fixture_pack_set",
    "write_json",
]
