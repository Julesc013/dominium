import argparse
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.lib.content_store import (
    artifact_ref,
    build_install_ref,
    build_pack_lock_payload,
    build_profile_bundle_payload,
    build_store_locator,
    embed_json_artifact,
    embed_tree_artifact,
    embedded_artifact_root,
    initialize_store_root,
    load_json as load_cas_json,
    pretty_write_json,
    resolve_locator_path,
    store_add_artifact,
    store_add_tree_artifact,
    store_artifact_root,
)
from src.lib.install import normalize_contract_range
from src.lib.instance import (
    INSTANCE_KIND_CLIENT,
    deterministic_fingerprint as instance_deterministic_fingerprint,
    instance_active_modpacks,
    instance_active_profiles,
    instance_data_root,
    instance_install_id,
    instance_settings_payload,
    normalize_instance_manifest,
    normalize_instance_settings,
    stable_instance_id,
    validate_instance_manifest,
)


DEFAULT_INSTALL_MANIFEST = "install.manifest.json"
DEFAULT_INSTANCE_MANIFEST = "instance.manifest.json"
DEFAULT_ACTIVE_INSTANCE = "active.instance.json"
DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("OPS_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def normalize_path(path: str) -> str:
    if not path:
        return ""
    return os.path.abspath(path)


def safe_rel(path: str, base: str) -> str:
    try:
        rel = os.path.relpath(path, base)
    except ValueError:
        return os.path.basename(path)
    if rel.startswith(".."):
        return os.path.basename(path)
    return rel.replace("\\", "/")


def resolve_install_root(manifest_path: str, manifest: Dict[str, object]) -> str:
    root_token = str((manifest or {}).get("install_root", "") or "").strip()
    if not root_token or root_token == ".":
        return os.path.dirname(os.path.abspath(manifest_path))
    if os.path.isabs(root_token):
        return root_token
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(manifest_path)), root_token))


def resolve_install_manifest_path(instance_root: str, instance_manifest: Dict[str, object]) -> str:
    install_ref = dict(instance_manifest.get("install_ref") or {})
    manifest_ref = str(install_ref.get("manifest_ref", "") or "").strip()
    if manifest_ref:
        return os.path.abspath(
            manifest_ref if os.path.isabs(manifest_ref) else os.path.join(instance_root, manifest_ref)
        )
    root_path = str(install_ref.get("root_path", "") or "").strip()
    if root_path:
        install_root = os.path.abspath(
            root_path if os.path.isabs(root_path) else os.path.join(instance_root, root_path)
        )
        return os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
    return ""


def refusal_payload(code_id: int, code: str, message: str,
                    details: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


def sorted_unique(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    return sorted({value for value in values if value})


def install_product_builds(install_manifest: Dict[str, object]) -> Dict[str, str]:
    product_builds = dict(install_manifest.get("product_builds") or install_manifest.get("product_build_ids") or {})
    return {
        str(key): str(value).strip()
        for key, value in sorted(product_builds.items(), key=lambda item: str(item[0]))
        if str(key).strip() and str(value).strip()
    }


def install_supported_contract_ranges(install_manifest: Dict[str, object]) -> Dict[str, dict]:
    ranges = dict(install_manifest.get("supported_contract_ranges") or {})
    return {
        str(key): normalize_contract_range(value)
        for key, value in sorted(ranges.items(), key=lambda item: str(item[0]))
        if str(key).strip()
    }


def parse_required_product_builds(rows: Optional[List[str]]) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    for row in list(rows or []):
        token = str(row or "").strip()
        if "=" not in token:
            continue
        product_id, build_id = token.split("=", 1)
        product_id = str(product_id).strip()
        build_id = str(build_id).strip()
        if product_id and build_id:
            parsed[product_id] = build_id
    return dict((key, parsed[key]) for key in sorted(parsed.keys()))


def parse_required_contract_ranges(rows: Optional[List[str]]) -> Dict[str, dict]:
    parsed: Dict[str, dict] = {}
    for row in list(rows or []):
        token = str(row or "").strip()
        if "=" not in token:
            continue
        contract_id, range_token = token.split("=", 1)
        contract_id = str(contract_id).strip()
        range_token = str(range_token).strip()
        if not contract_id or not range_token:
            continue
        if ":" in range_token:
            min_token, max_token = range_token.split(":", 1)
        else:
            min_token = range_token
            max_token = range_token
        try:
            min_version = int(min_token)
            max_version = int(max_token)
        except ValueError:
            continue
        parsed[contract_id] = normalize_contract_range(
            {
                "contract_category_id": contract_id,
                "min_version": min_version,
                "max_version": max_version,
                "extensions": {},
            }
        )
    return dict((key, parsed[key]) for key in sorted(parsed.keys()))


def build_compat_report(context: str,
                        install_id: Optional[str],
                        instance_id: Optional[str],
                        runtime_id: Optional[str],
                        capability_baseline: Optional[str],
                        required_capabilities: Optional[List[str]],
                        provided_capabilities: Optional[List[str]],
                        missing_capabilities: Optional[List[str]],
                        compatibility_mode: str,
                        refusal_codes: Optional[List[str]],
                        mitigation_hints: Optional[List[str]],
                        deterministic: bool,
                        refusal: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    required = sorted_unique(required_capabilities)
    provided = sorted_unique(provided_capabilities)
    missing = sorted_unique(missing_capabilities)
    if missing_capabilities is None:
        missing = sorted(set(required) - set(provided))
    payload = {
        "context": context,
        "install_id": install_id or NULL_UUID,
        "instance_id": instance_id or NULL_UUID,
        "runtime_id": runtime_id or NULL_UUID,
        "capability_baseline": capability_baseline or DEFAULT_CAPABILITY_BASELINE,
        "required_capabilities": required,
        "provided_capabilities": provided,
        "missing_capabilities": missing,
        "compatibility_mode": compatibility_mode,
        "refusal_codes": sorted_unique(refusal_codes),
        "mitigation_hints": sorted_unique(mitigation_hints),
        "timestamp": now_timestamp(deterministic),
        "extensions": {},
    }
    if refusal:
        payload["refusal"] = refusal
    return payload


def ops_log_path(root: str) -> str:
    return os.path.join(root, "ops", "ops.log")


def append_ops_log(root: str, entry: dict) -> None:
    ensure_dir(os.path.join(root, "ops"))
    path = ops_log_path(root)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def begin_transaction(root: str, action: str, tx_id: str, deterministic: bool) -> None:
    append_ops_log(root, {
        "transaction_id": tx_id,
        "action": action,
        "state": "PLAN",
        "timestamp": now_timestamp(deterministic),
        "result": "pending",
    })


def stage_transaction(root: str, action: str, tx_id: str, deterministic: bool) -> None:
    append_ops_log(root, {
        "transaction_id": tx_id,
        "action": action,
        "state": "STAGE",
        "timestamp": now_timestamp(deterministic),
        "result": "pending",
    })


def commit_transaction(root: str, action: str, tx_id: str, deterministic: bool) -> None:
    append_ops_log(root, {
        "transaction_id": tx_id,
        "action": action,
        "state": "COMMIT",
        "timestamp": now_timestamp(deterministic),
        "result": "ok",
    })


def rollback_transaction(root: str, action: str, tx_id: str,
                         refusal: Optional[Dict[str, object]],
                         deterministic: bool) -> None:
    entry = {
        "transaction_id": tx_id,
        "action": action,
        "state": "ROLLBACK",
        "timestamp": now_timestamp(deterministic),
        "result": "refused",
    }
    if refusal:
        entry["refusal"] = refusal
    append_ops_log(root, entry)


def load_sandbox_policy(path: str) -> dict:
    if not path:
        return {}
    return load_json(path)


def sandbox_allows(policy: dict, candidate: str) -> bool:
    if not policy:
        return True
    allowed = policy.get("allowed_paths") or []
    denied = policy.get("denied_paths") or []
    if not allowed and not denied:
        return True
    candidate_abs = normalize_path(candidate)
    for deny in denied:
        if not deny:
            continue
        deny_abs = normalize_path(deny)
        if candidate_abs.startswith(deny_abs):
            return False
    if not allowed:
        return True
    for allow in allowed:
        if not allow:
            continue
        allow_abs = normalize_path(allow)
        if candidate_abs.startswith(allow_abs):
            return True
    return False


def list_install_manifests(search_roots: List[str]) -> List[Dict[str, object]]:
    results = []
    seen = set()
    for root in search_roots:
        if not root:
            continue
        if os.path.isfile(root):
            manifest_path = root
        else:
            manifest_path = os.path.join(root, DEFAULT_INSTALL_MANIFEST)
        if os.path.isfile(manifest_path):
            try:
                manifest = load_json(manifest_path)
            except (OSError, ValueError):
                continue
            install_id = manifest.get("install_id")
            if install_id and install_id in seen:
                continue
            if install_id:
                seen.add(install_id)
            results.append({
                "install_id": install_id,
                "install_root": resolve_install_root(manifest_path, manifest),
                "manifest_path": manifest_path.replace("\\", "/"),
            })
            continue
        if os.path.isdir(root):
            for dirpath, _dirnames, filenames in os.walk(root):
                if DEFAULT_INSTALL_MANIFEST in filenames:
                    manifest_path = os.path.join(dirpath, DEFAULT_INSTALL_MANIFEST)
                    try:
                        manifest = load_json(manifest_path)
                    except (OSError, ValueError):
                        continue
                    install_id = manifest.get("install_id")
                    if install_id and install_id in seen:
                        continue
                    if install_id:
                        seen.add(install_id)
                    results.append({
                        "install_id": install_id,
                        "install_root": resolve_install_root(manifest_path, manifest),
                        "manifest_path": manifest_path.replace("\\", "/"),
                    })
    return sorted(results, key=lambda row: (str(row.get("install_id", "")), str(row.get("manifest_path", ""))))


def list_instance_manifests(search_roots: List[str],
                            install_id: Optional[str]) -> List[Dict[str, object]]:
    results = []
    for root in search_roots:
        if not root:
            continue
        if os.path.isfile(root):
            manifest_path = root
        else:
            manifest_path = os.path.join(root, DEFAULT_INSTANCE_MANIFEST)
        if os.path.isfile(manifest_path):
            try:
                manifest = dict(validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=manifest_path).get("instance_manifest") or load_json(manifest_path))
            except (OSError, ValueError):
                continue
            if install_id and instance_install_id(manifest) != install_id:
                continue
            results.append({
                "instance_id": manifest.get("instance_id"),
                "install_id": instance_install_id(manifest),
                "instance_kind": manifest.get("instance_kind"),
                "mode": manifest.get("mode", "portable"),
                "data_root": instance_data_root(manifest),
                "save_ref_count": len(list(manifest.get("save_refs") or [])),
                "manifest_path": manifest_path.replace("\\", "/"),
            })
            continue
        if os.path.isdir(root):
            for dirpath, _dirnames, filenames in os.walk(root):
                if DEFAULT_INSTANCE_MANIFEST in filenames:
                    manifest_path = os.path.join(dirpath, DEFAULT_INSTANCE_MANIFEST)
                    try:
                        manifest = dict(validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=manifest_path).get("instance_manifest") or load_json(manifest_path))
                    except (OSError, ValueError):
                        continue
                    if install_id and instance_install_id(manifest) != install_id:
                        continue
                    results.append({
                        "instance_id": manifest.get("instance_id"),
                        "install_id": instance_install_id(manifest),
                        "instance_kind": manifest.get("instance_kind"),
                        "mode": manifest.get("mode", "portable"),
                        "data_root": instance_data_root(manifest),
                        "save_ref_count": len(list(manifest.get("save_refs") or [])),
                        "manifest_path": manifest_path.replace("\\", "/"),
                    })
    return sorted(results, key=lambda row: (str(row.get("instance_id", "")), str(row.get("manifest_path", ""))))


def capabilities_from_manifest(manifest: Optional[dict]) -> List[str]:
    if not manifest:
        return []
    return sorted_unique(manifest.get("supported_capabilities") or [])


def compat_client_server(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    client_caps = set(sorted_unique(args.client_cap))
    server_caps = set(sorted_unique(args.server_cap))
    required = sorted_unique(args.required_cap)
    overlap = sorted(client_caps & server_caps)
    missing_server = sorted(set(required) - server_caps)
    missing_client = sorted(set(required) - client_caps)
    refusal = None
    refusal_codes: List[str] = []
    mitigation: List[str] = []
    mode = "full"
    missing = sorted(set(required) - set(overlap))

    if not overlap:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "client/server capability overlap is empty",
                                  {"required": required})
        mitigation = ["install overlapping capability packs on both sides"]
    elif missing_server:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "server missing required capabilities",
                                  {"missing": missing_server})
        mitigation = ["update server capabilities to meet requirements"]
    elif missing_client:
        mode = "degraded"
        mitigation = ["update client capabilities to restore full mode"]

    report = build_compat_report(
        context=args.context,
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=required,
        provided_capabilities=overlap,
        missing_capabilities=missing,
        compatibility_mode=mode,
        refusal_codes=refusal_codes,
        mitigation_hints=mitigation,
        deterministic=args.deterministic,
        refusal=refusal,
    )
    result = "refused" if mode == "refuse" else "ok"
    return (3 if mode == "refuse" else 0), {"result": result, "compat_report": report}


def compat_shard_transfer(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    source_caps = set(sorted_unique(args.source_cap))
    target_caps = set(sorted_unique(args.target_cap))
    required = sorted_unique(args.required_cap)
    overlap = sorted(source_caps & target_caps)
    missing_source = sorted(set(required) - source_caps)
    missing_target = sorted(set(required) - target_caps)
    refusal = None
    refusal_codes: List[str] = []
    mitigation: List[str] = []
    mode = "full"
    missing = sorted(set(required) - set(overlap))

    if not overlap:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "shard capability overlap is empty",
                                  {"required": required})
        mitigation = ["align shard capability baselines"]
    elif missing_source or missing_target:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "shard missing required capabilities",
                                  {"missing_source": missing_source, "missing_target": missing_target})
        mitigation = ["update shards to share required capabilities"]

    report = build_compat_report(
        context=args.context,
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=required,
        provided_capabilities=overlap,
        missing_capabilities=missing,
        compatibility_mode=mode,
        refusal_codes=refusal_codes,
        mitigation_hints=mitigation,
        deterministic=args.deterministic,
        refusal=refusal,
    )
    result = "refused" if mode == "refuse" else "ok"
    return (3 if mode == "refuse" else 0), {"result": result, "compat_report": report}


def compat_tools(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    tool_caps = sorted_unique(args.tool_cap)
    required = sorted_unique(args.required_cap)
    missing = sorted(set(required) - set(tool_caps))
    mode = "full" if not missing else "inspect-only"
    mitigation = [] if not missing else ["update tools or use newer build for full support"]

    report = build_compat_report(
        context=args.context,
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=required,
        provided_capabilities=tool_caps,
        missing_capabilities=missing,
        compatibility_mode=mode,
        refusal_codes=[],
        mitigation_hints=mitigation,
        deterministic=args.deterministic,
        refusal=None,
    )
    return 0, {"result": "ok", "compat_report": report}


def resolve_data_root(instance_root: str, data_root: str) -> str:
    if not data_root:
        return instance_root
    if os.path.isabs(data_root):
        return data_root
    return os.path.join(instance_root, data_root)


def default_mod_policy_id(args: argparse.Namespace) -> str:
    return str(getattr(args, "mod_policy_id", "") or "mod.policy.default")


def default_overlay_policy_id(args: argparse.Namespace) -> str:
    return str(getattr(args, "overlay_conflict_policy_id", "") or "overlay.conflict.default")


def load_optional_json(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.isfile(path):
        return {}
    try:
        return load_cas_json(path)
    except (OSError, ValueError):
        return {}


def discover_pack_path(pack_id: str, roots: List[str]) -> str:
    for root in roots:
        if not root:
            continue
        candidate = os.path.join(root, pack_id)
        if os.path.isdir(candidate):
            return candidate
        if os.path.isdir(root) and os.path.basename(os.path.normpath(root)) == pack_id:
            return root
    return ""


def candidate_pack_roots(install_manifest_path: str,
                         instance_root: str,
                         explicit_roots: List[str]) -> List[str]:
    install_root = os.path.dirname(os.path.abspath(install_manifest_path))
    roots = list(explicit_roots or [])
    roots.append(os.path.join(install_root, "packs"))
    roots.append(os.path.join(instance_root, "packs"))
    unique: List[str] = []
    seen = set()
    for root in roots:
        token = os.path.abspath(root)
        if token in seen:
            continue
        seen.add(token)
        unique.append(token)
    return unique


def build_instance_manifest_payload(*,
                                    instance_root: str,
                                    install_manifest_path: str,
                                    install_manifest: Dict[str, object],
                                    instance_id: str,
                                    instance_kind: str,
                                    mode: str,
                                    store_root: str,
                                    store_manifest: Dict[str, object],
                                    pack_lock_payload: Dict[str, object],
                                    pack_lock_hash: str,
                                    profile_bundle_payload: Dict[str, object],
                                    profile_bundle_hash: str,
                                    mod_policy_id: str,
                                    overlay_conflict_policy_id: str,
                                    default_session_template_id: str,
                                    seed_policy: str,
                                    required_product_builds: Dict[str, str],
                                    required_contract_ranges: Dict[str, dict],
                                    pack_artifact_refs: List[Dict[str, object]],
                                    settings: Dict[str, object],
                                    save_refs: List[str],
                                    last_opened_save_id: str,
                                    capability_lockfile: str) -> Dict[str, object]:
    settings = normalize_instance_settings(settings)
    extensions = dict((settings.get("extensions") or {}))
    if last_opened_save_id:
        extensions["instance.last_opened_save_id"] = last_opened_save_id
    settings["extensions"] = extensions
    settings["deterministic_fingerprint"] = ""
    settings["deterministic_fingerprint"] = instance_deterministic_fingerprint(settings)
    payload = {
        "instance_id": instance_id,
        "instance_kind": instance_kind,
        "install_id": install_manifest.get("install_id"),
        "mode": mode,
        "install_ref": build_install_ref(instance_root, install_manifest_path, install_manifest),
        "embedded_builds": {},
        "pack_lock_hash": pack_lock_hash,
        "profile_bundle_hash": profile_bundle_hash,
        "mod_policy_id": mod_policy_id,
        "overlay_conflict_policy_id": overlay_conflict_policy_id,
        "default_session_template_id": default_session_template_id,
        "seed_policy": seed_policy,
        "required_product_builds": dict((key, required_product_builds[key]) for key in sorted(required_product_builds.keys())),
        "required_contract_ranges": dict((key, required_contract_ranges[key]) for key in sorted(required_contract_ranges.keys())),
        "instance_settings": settings,
        "save_refs": sorted_unique(save_refs),
        "store_root": build_store_locator(instance_root, store_root, store_manifest) if mode == "linked" else {},
        "embedded_artifacts": [],
        "data_root": settings.get("data_root") or ".",
        "active_profiles": settings.get("active_profiles") or [],
        "active_modpacks": settings.get("active_modpacks") or [],
        "capability_lockfile": capability_lockfile,
        "sandbox_policy_ref": settings.get("sandbox_policy_ref") or "sandbox.default",
        "update_channel": settings.get("update_channel") or "stable",
        "created_at": settings.get("created_at"),
        "last_used_at": settings.get("last_used_at"),
        "extensions": dict((settings.get("extensions") or {})),
        "deterministic_fingerprint": "",
    }
    if mode == "portable":
        lock_root = embedded_artifact_root(instance_root, "locks", pack_lock_hash)
        profile_root = embedded_artifact_root(instance_root, "profiles", profile_bundle_hash)
        payload["embedded_artifacts"] = [
            artifact_ref(
                category="locks",
                artifact_hash=pack_lock_hash,
                artifact_type="json",
                artifact_root=lock_root,
                instance_root=instance_root,
                artifact_id=str(pack_lock_payload.get("pack_lock_id", "")),
            ),
            artifact_ref(
                category="profiles",
                artifact_hash=profile_bundle_hash,
                artifact_type="json",
                artifact_root=profile_root,
                instance_root=instance_root,
                artifact_id=str(profile_bundle_payload.get("profile_bundle_id", "")),
            ),
        ] + list(pack_artifact_refs)
    if last_opened_save_id:
        payload["extensions"]["instance.last_opened_save_id"] = last_opened_save_id
    payload = normalize_instance_manifest(payload)
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    return payload


def materialize_instance_artifacts(*,
                                   instance_root: str,
                                   store_root: str,
                                   mode: str,
                                   instance_id: str,
                                   active_modpacks: List[str],
                                   active_profiles: List[str],
                                   mod_policy_id: str,
                                   overlay_conflict_policy_id: str,
                                   capability_lockfile_path: Optional[str],
                                   pack_roots: List[str]) -> Tuple[Dict[str, object], str, Dict[str, object], str, List[Dict[str, object]], str, Dict[str, object]]:
    pack_refs: List[Dict[str, object]] = []
    resolved_hashes: Dict[str, str] = {}
    target_store_manifest: Dict[str, object] = {}
    if mode == "linked":
        target_store_manifest = initialize_store_root(store_root)

    for pack_id in sorted_unique(active_modpacks):
        pack_path = discover_pack_path(pack_id, pack_roots)
        if not pack_path:
            continue
        if mode == "linked":
            result = store_add_tree_artifact(store_root, "packs", pack_path)
            artifact_root = store_artifact_root(store_root, "packs", result["artifact_hash"])
        else:
            result = embed_tree_artifact(instance_root, "packs", pack_path)
            artifact_root = embedded_artifact_root(instance_root, "packs", result["artifact_hash"])
        resolved_hashes[pack_id] = str(result["artifact_hash"])
        pack_refs.append(
            artifact_ref(
                category="packs",
                artifact_hash=str(result["artifact_hash"]),
                artifact_type="tree",
                artifact_root=artifact_root,
                instance_root=instance_root,
                artifact_id=pack_id,
            )
        )

    source_lock_payload = load_optional_json(capability_lockfile_path)
    if resolved_hashes:
        source_lock_payload["pack_hashes"] = dict(resolved_hashes)
    pack_lock_payload, pack_lock_hash = build_pack_lock_payload(
        instance_id=instance_id,
        pack_ids=active_modpacks,
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        source_payload=source_lock_payload,
    )
    profile_bundle_payload, profile_bundle_hash = build_profile_bundle_payload(
        instance_id=instance_id,
        profile_ids=active_profiles,
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )
    if mode == "linked":
        store_add_artifact(store_root, "locks", pack_lock_payload)
        store_add_artifact(store_root, "profiles", profile_bundle_payload)
    else:
        embed_json_artifact(instance_root, "locks", pack_lock_payload, expected_hash=pack_lock_hash)
        embed_json_artifact(instance_root, "profiles", profile_bundle_payload, expected_hash=profile_bundle_hash)

    legacy_lockfile = "lockfiles/capabilities.lock" if mode == "portable" else ""
    return (
        pack_lock_payload,
        pack_lock_hash,
        profile_bundle_payload,
        profile_bundle_hash,
        pack_refs,
        legacy_lockfile,
        target_store_manifest,
    )


def clone_ignore_entries(_src: str, names: List[str]) -> List[str]:
    ignored = []
    for name in list(names or []):
        if name in ("saves", "ops", "compat", DEFAULT_ACTIVE_INSTANCE):
            ignored.append(name)
    return ignored


def create_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    install_manifest = load_json(args.install_manifest)
    install_id = install_manifest.get("install_id")
    data_root = args.data_root
    instance_root = args.data_root
    if args.instance_root:
        instance_root = args.instance_root
    mode = str(getattr(args, "mode", "portable") or "portable").strip().lower()
    store_root = str(getattr(args, "store_root", "") or "").strip()
    if mode == "linked" and not store_root:
        store_root = resolve_locator_path(os.path.dirname(args.install_manifest), install_manifest.get("store_root_ref") or install_manifest.get("store_root"))
    mod_policy_id = default_mod_policy_id(args)
    overlay_conflict_policy_id = default_overlay_policy_id(args)
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}
    provided_caps = capabilities_from_manifest(install_manifest)
    required_product_builds = parse_required_product_builds(getattr(args, "required_product_build", []))
    if not required_product_builds:
        required_product_builds = install_product_builds(install_manifest)
    required_contract_ranges = parse_required_contract_ranges(getattr(args, "required_contract_range", []))
    if not required_contract_ranges:
        required_contract_ranges = install_supported_contract_ranges(install_manifest)
    instance_kind = str(getattr(args, "instance_kind", INSTANCE_KIND_CLIENT) or INSTANCE_KIND_CLIENT).strip() or INSTANCE_KIND_CLIENT
    default_session_template_id = str(
        getattr(args, "default_session_template_id", "") or "session.template.default"
    ).strip() or "session.template.default"
    seed_policy = str(getattr(args, "seed_policy", "") or "prompt").strip() or "prompt"
    save_refs = sorted_unique(getattr(args, "save_ref", []) or [])
    last_opened_save_id = str(getattr(args, "last_opened_save_id", "") or "").strip()
    if last_opened_save_id and last_opened_save_id not in save_refs:
        save_refs = sorted(set(save_refs + [last_opened_save_id]))
    if args.instance_id:
        instance_id = str(args.instance_id).strip()
    elif deterministic:
        instance_id = stable_instance_id(
            {
                "install_id": str(install_id or "").strip(),
                "instance_kind": instance_kind,
                "mode": mode,
                "mod_policy_id": mod_policy_id,
                "overlay_conflict_policy_id": overlay_conflict_policy_id,
                "active_profiles": sorted_unique(getattr(args, "active_profiles", []) or []),
                "active_modpacks": sorted_unique(getattr(args, "active_modpacks", []) or []),
                "required_product_builds": required_product_builds,
                "required_contract_ranges": required_contract_ranges,
                "default_session_template_id": default_session_template_id,
                "seed_policy": seed_policy,
            }
        )
    else:
        instance_id = str(uuid.uuid4())

    if not install_id:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "install manifest missing install_id",
                                  {"manifest": os.path.basename(args.install_manifest)})
        report = build_compat_report(
            context="update",
            install_id=None,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    if mode not in ("linked", "portable"):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance mode is invalid",
                                  {"mode": mode})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}
    if mode == "linked" and not store_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "linked instances require store_root",
                                  {"instance_id": instance_id})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=["set --store-root for linked instances"],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    if not sandbox_allows(sandbox, instance_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies instance root",
                                  {"path": os.path.basename(instance_root)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    ensure_dir(instance_root)
    begin_transaction(instance_root, "instances.create", tx_id, deterministic)
    stage_transaction(instance_root, "instances.create", tx_id, deterministic)

    manifest_path = os.path.join(instance_root, DEFAULT_INSTANCE_MANIFEST)
    if os.path.exists(manifest_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "instance manifest already exists",
                                  {"manifest": DEFAULT_INSTANCE_MANIFEST})
        rollback_transaction(instance_root, "instances.create", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    created_at = args.created_at or now_timestamp(deterministic)
    manifest_data_root = "."
    if data_root:
        candidate_data_root = os.path.abspath(data_root)
        candidate_instance_root = os.path.abspath(instance_root)
        if candidate_data_root != candidate_instance_root:
            manifest_data_root = safe_rel(candidate_data_root, candidate_instance_root)
    pack_lock_payload, pack_lock_hash, profile_bundle_payload, profile_bundle_hash, pack_artifact_refs, legacy_lockfile, store_manifest = materialize_instance_artifacts(
        instance_root=instance_root,
        store_root=store_root,
        mode=mode,
        instance_id=instance_id,
        active_modpacks=args.active_modpacks or [],
        active_profiles=args.active_profiles or [],
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        capability_lockfile_path=args.capability_lockfile,
        pack_roots=candidate_pack_roots(args.install_manifest, instance_root, getattr(args, "pack_root", [])),
    )
    payload = build_instance_manifest_payload(
        instance_root=instance_root,
        install_manifest_path=args.install_manifest,
        install_manifest=install_manifest,
        instance_id=instance_id,
        instance_kind=instance_kind,
        mode=mode,
        store_root=store_root,
        store_manifest=store_manifest,
        pack_lock_payload=pack_lock_payload,
        pack_lock_hash=pack_lock_hash,
        profile_bundle_payload=profile_bundle_payload,
        profile_bundle_hash=profile_bundle_hash,
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        default_session_template_id=default_session_template_id,
        seed_policy=seed_policy,
        required_product_builds=required_product_builds,
        required_contract_ranges=required_contract_ranges,
        pack_artifact_refs=pack_artifact_refs,
        settings={
            "renderer_mode": getattr(args, "renderer_mode", None),
            "ui_mode_default": getattr(args, "ui_mode_default", "cli"),
            "allow_read_only_fallback": bool(getattr(args, "allow_read_only_fallback", False)),
            "tick_budget_policy_id": getattr(args, "tick_budget_policy_id", "tick.budget.default"),
            "compute_profile_id": getattr(args, "compute_profile_id", "compute.profile.default"),
            "active_profiles": args.active_profiles or [],
            "active_modpacks": args.active_modpacks or [],
            "data_root": manifest_data_root,
            "sandbox_policy_ref": args.sandbox_policy_ref or "sandbox.default",
            "update_channel": args.update_channel,
            "created_at": created_at,
            "last_used_at": created_at,
        },
        save_refs=save_refs,
        last_opened_save_id=last_opened_save_id,
        capability_lockfile=legacy_lockfile,
    )
    validation = validate_instance_manifest(
        repo_root=REPO_ROOT,
        instance_manifest_path=manifest_path,
        manifest_payload=payload,
    )
    if validation.get("result") != "complete":
        refusal = refusal_payload(
            5,
            str(validation.get("refusal_code", "REFUSE_INSTANCE_INVALID")).upper() or "REFUSE_INSTANCE_INVALID",
            "instance manifest validation failed",
            {"instance_id": instance_id},
        )
        rollback_transaction(instance_root, "instances.create", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}
    payload = dict(validation.get("instance_manifest") or payload)
    tmp_path = manifest_path + ".tmp"
    pretty_write_json(tmp_path, payload)
    if legacy_lockfile:
        pretty_write_json(os.path.join(instance_root, legacy_lockfile), pack_lock_payload)

    if args.simulate_failure == "stage":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "simulated stage failure", {})
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        rollback_transaction(instance_root, "instances.create", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    os.replace(tmp_path, manifest_path)
    commit_transaction(instance_root, "instances.create", tx_id, deterministic)
    report = build_compat_report(
        context="update",
        install_id=install_id,
        instance_id=instance_id,
        runtime_id=None,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=provided_caps,
        missing_capabilities=[],
        compatibility_mode="full",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=deterministic,
        refusal=None,
    )
    return 0, {
        "result": "ok",
        "compat_report": report,
        "instance_manifest": manifest_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def clone_instance(args: argparse.Namespace, fork_only: bool) -> Tuple[int, Dict[str, object]]:
    source_manifest = dict(
        validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.source_manifest).get("instance_manifest")
        or load_json(args.source_manifest)
    )
    source_root = os.path.dirname(args.source_manifest)
    install_id = instance_install_id(source_manifest)
    source_mode = str(source_manifest.get("mode", "portable") or "portable").strip().lower()
    if not install_id:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "source instance missing install_id",
                                  {"manifest": os.path.basename(args.source_manifest)})
        report = build_compat_report(
            context="update",
            install_id=None,
            instance_id=args.instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=capabilities_from_manifest(source_manifest),
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=args.deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    target_root = args.data_root
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}
    if args.instance_id:
        instance_id = str(args.instance_id).strip()
    elif deterministic:
        instance_id = stable_instance_id(
            {
                "source_instance_id": str(source_manifest.get("instance_id", "")).strip(),
                "clone_kind": "fork" if fork_only else "clone",
                "instance_kind": str(source_manifest.get("instance_kind", "")).strip(),
                "mode": source_mode,
                "pack_lock_hash": str(source_manifest.get("pack_lock_hash", "")).strip(),
                "profile_bundle_hash": str(source_manifest.get("profile_bundle_hash", "")).strip(),
            }
        )
    else:
        instance_id = str(uuid.uuid4())

    if not sandbox_allows(sandbox, target_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies instance root",
                                  {"path": os.path.basename(target_root)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=capabilities_from_manifest(source_manifest),
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    if os.path.exists(target_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "target instance root already exists",
                                  {"path": os.path.basename(target_root)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=capabilities_from_manifest(source_manifest),
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    ensure_dir(target_root)
    begin_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)
    stage_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)

    if not fork_only:
        shutil.copytree(source_root, target_root, dirs_exist_ok=True, ignore=clone_ignore_entries)
    else:
        ensure_dir(target_root)
        if source_mode == "portable":
            for rel_path in ("embedded_artifacts", "embedded_builds", "lockfiles"):
                src_path = os.path.join(source_root, rel_path)
                dest_path = os.path.join(target_root, rel_path)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

    manifest_path = os.path.join(target_root, DEFAULT_INSTANCE_MANIFEST)
    payload = dict(source_manifest)
    payload["instance_id"] = instance_id
    payload["data_root"] = payload.get("data_root", ".")
    payload["created_at"] = args.created_at or now_timestamp(deterministic)
    payload["last_used_at"] = args.created_at or now_timestamp(deterministic)
    if source_mode == "linked":
        source_store_root = resolve_locator_path(source_root, source_manifest.get("store_root"))
        if source_store_root:
            store_manifest = initialize_store_root(source_store_root)
            payload["store_root"] = build_store_locator(target_root, source_store_root, store_manifest)
    source_install_manifest_path = resolve_install_manifest_path(source_root, source_manifest)
    if source_install_manifest_path and os.path.isfile(source_install_manifest_path):
        try:
            source_install_manifest = load_json(source_install_manifest_path)
        except (OSError, ValueError):
            source_install_manifest = {}
        if source_install_manifest:
            payload["install_ref"] = build_install_ref(target_root, source_install_manifest_path, source_install_manifest)
            payload["install_id"] = source_install_manifest.get("install_id") or payload.get("install_id")
    payload = normalize_instance_manifest(payload)
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    validation = validate_instance_manifest(
        repo_root=REPO_ROOT,
        instance_manifest_path=manifest_path,
        manifest_payload=payload,
    )
    if validation.get("result") != "complete":
        refusal = refusal_payload(
            5,
            str(validation.get("refusal_code", "REFUSE_INSTANCE_INVALID")).upper() or "REFUSE_INSTANCE_INVALID",
            "cloned instance manifest validation failed",
            {"instance_id": instance_id},
        )
        shutil.rmtree(target_root, ignore_errors=True)
        rollback_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=capabilities_from_manifest(source_manifest),
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}
    payload = dict(validation.get("instance_manifest") or payload)
    pretty_write_json(manifest_path, payload)

    if args.simulate_failure == "commit":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "simulated commit failure", {})
        shutil.rmtree(target_root, ignore_errors=True)
        rollback_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=capabilities_from_manifest(source_manifest),
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    commit_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)
    report = build_compat_report(
        context="update",
        install_id=install_id,
        instance_id=instance_id,
        runtime_id=None,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=capabilities_from_manifest(source_manifest),
        missing_capabilities=[],
        compatibility_mode="full",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=deterministic,
        refusal=None,
    )
    return 0, {
        "result": "ok",
        "compat_report": report,
        "instance_manifest": manifest_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def edit_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    deterministic = args.deterministic
    manifest_path = args.instance_manifest
    instance_root = os.path.dirname(os.path.abspath(manifest_path))
    if not os.path.isfile(manifest_path):
        install_id = ""
        instance_id = ""
        provided_caps: List[str] = []
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "instance manifest not found", {"manifest": os.path.basename(manifest_path)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    manifest = dict(
        validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=manifest_path).get("instance_manifest")
        or load_json(manifest_path)
    )
    install_id = instance_install_id(manifest)
    instance_id = str(manifest.get("instance_id", "")).strip()
    provided_caps = capabilities_from_manifest(manifest)
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}

    if not sandbox_allows(sandbox, instance_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN", "sandbox denies instance root", {"path": os.path.basename(instance_root)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    begin_transaction(instance_root, "instances.edit", tx_id, deterministic)
    stage_transaction(instance_root, "instances.edit", tx_id, deterministic)

    updated = dict(manifest)
    if getattr(args, "instance_kind", None):
        updated["instance_kind"] = str(args.instance_kind).strip()
    if getattr(args, "mode", None):
        updated["mode"] = str(args.mode).strip()
    if getattr(args, "default_session_template_id", None):
        updated["default_session_template_id"] = str(args.default_session_template_id).strip()
    if getattr(args, "seed_policy", None):
        updated["seed_policy"] = str(args.seed_policy).strip()
    if getattr(args, "mod_policy_id", None):
        updated["mod_policy_id"] = str(args.mod_policy_id).strip()
    if getattr(args, "overlay_conflict_policy_id", None):
        updated["overlay_conflict_policy_id"] = str(args.overlay_conflict_policy_id).strip()
    if getattr(args, "required_product_build", None):
        updated["required_product_builds"] = parse_required_product_builds(args.required_product_build)
    if getattr(args, "required_contract_range", None):
        updated["required_contract_ranges"] = parse_required_contract_ranges(args.required_contract_range)
    if getattr(args, "profile", None):
        updated["active_profiles"] = sorted_unique(args.profile)
    if getattr(args, "modpack", None):
        updated["active_modpacks"] = sorted_unique(args.modpack)
    if getattr(args, "save_ref", None):
        updated["save_refs"] = sorted_unique(args.save_ref)
    if getattr(args, "last_opened_save_id", None) is not None:
        updated_extensions = dict(updated.get("extensions") or {})
        last_opened_save_id = str(args.last_opened_save_id or "").strip()
        if last_opened_save_id:
            updated_extensions["instance.last_opened_save_id"] = last_opened_save_id
            updated["save_refs"] = sorted(set(list(updated.get("save_refs") or []) + [last_opened_save_id]))
        else:
            updated_extensions.pop("instance.last_opened_save_id", None)
        updated["extensions"] = updated_extensions
    if getattr(args, "install_manifest", None):
        install_manifest = load_json(args.install_manifest)
        updated["install_ref"] = build_install_ref(instance_root, args.install_manifest, install_manifest)
        updated["install_id"] = install_manifest.get("install_id")
    if getattr(args, "store_root", None):
        updated["store_root"] = {
            "store_id": str((dict(updated.get("store_root") or {})).get("store_id", "store.default")),
            "root_path": safe_rel(args.store_root, instance_root),
            "manifest_ref": safe_rel(os.path.join(args.store_root, "store.root.json"), instance_root),
        }

    settings = instance_settings_payload(updated)
    if getattr(args, "renderer_mode", None) is not None:
        settings["renderer_mode"] = args.renderer_mode
    if getattr(args, "ui_mode_default", None):
        settings["ui_mode_default"] = str(args.ui_mode_default).strip()
    if bool(getattr(args, "allow_read_only_fallback", False)):
        settings["allow_read_only_fallback"] = True
    if bool(getattr(args, "deny_read_only_fallback", False)):
        settings["allow_read_only_fallback"] = False
    if getattr(args, "tick_budget_policy_id", None):
        settings["tick_budget_policy_id"] = str(args.tick_budget_policy_id).strip()
    if getattr(args, "compute_profile_id", None):
        settings["compute_profile_id"] = str(args.compute_profile_id).strip()
    if getattr(args, "profile", None):
        settings["active_profiles"] = sorted_unique(args.profile)
    if getattr(args, "modpack", None):
        settings["active_modpacks"] = sorted_unique(args.modpack)
    updated["instance_settings"] = settings
    updated["data_root"] = str(settings.get("data_root", updated.get("data_root", "."))).strip() or "."
    updated["active_profiles"] = list(settings.get("active_profiles") or [])
    updated["active_modpacks"] = list(settings.get("active_modpacks") or [])
    updated["sandbox_policy_ref"] = str(settings.get("sandbox_policy_ref", updated.get("sandbox_policy_ref", "sandbox.default"))).strip() or "sandbox.default"
    updated["update_channel"] = str(settings.get("update_channel", updated.get("update_channel", "stable"))).strip() or "stable"
    updated["last_used_at"] = now_timestamp(deterministic)
    updated = normalize_instance_manifest(updated)
    updated["deterministic_fingerprint"] = instance_deterministic_fingerprint(updated)

    validation = validate_instance_manifest(
        repo_root=REPO_ROOT,
        instance_manifest_path=manifest_path,
        manifest_payload=updated,
    )
    if validation.get("result") != "complete":
        refusal = refusal_payload(
            5,
            str(validation.get("refusal_code", "REFUSE_INSTANCE_INVALID")).upper() or "REFUSE_INSTANCE_INVALID",
            "instance edit validation failed",
            {"instance_id": instance_id},
        )
        rollback_transaction(instance_root, "instances.edit", tx_id, refusal, deterministic)
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    pretty_write_json(manifest_path, dict(validation.get("instance_manifest") or updated))
    commit_transaction(instance_root, "instances.edit", tx_id, deterministic)
    report = build_compat_report(
        context="update",
        install_id=instance_install_id(updated),
        instance_id=instance_id,
        runtime_id=None,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=provided_caps,
        missing_capabilities=[],
        compatibility_mode="full",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=deterministic,
        refusal=None,
    )
    return 0, {"result": "ok", "compat_report": report, "instance_manifest": manifest_path.replace("\\", "/"), "transaction_id": tx_id}


def activate_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    install_manifest = load_json(args.install_manifest)
    install_root = resolve_install_root(args.install_manifest, install_manifest)
    instance_manifest = dict(
        validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.instance_manifest).get("instance_manifest")
        or load_json(args.instance_manifest)
    )
    instance_id = instance_manifest.get("instance_id")
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}
    install_id = install_manifest.get("install_id")
    provided_caps = capabilities_from_manifest(install_manifest)

    if not sandbox_allows(sandbox, install_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies install root",
                                  {"path": os.path.basename(install_root)})
        report = build_compat_report(
            context="update",
            install_id=install_id,
            instance_id=instance_id,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=provided_caps,
            missing_capabilities=[],
            compatibility_mode="refuse",
            refusal_codes=[refusal.get("code")],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    ensure_dir(install_root)
    begin_transaction(install_root, "instances.activate", tx_id, deterministic)
    stage_transaction(install_root, "instances.activate", tx_id, deterministic)

    payload = {
        "install_id": install_manifest.get("install_id"),
        "instance_id": instance_id,
        "instance_manifest": safe_rel(args.instance_manifest, install_root),
        "activated_at": now_timestamp(deterministic),
    }
    active_path = os.path.join(install_root, DEFAULT_ACTIVE_INSTANCE)
    write_json(active_path, payload)
    commit_transaction(install_root, "instances.activate", tx_id, deterministic)
    report = build_compat_report(
        context="update",
        install_id=install_id,
        instance_id=instance_id,
        runtime_id=None,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=provided_caps,
        missing_capabilities=[],
        compatibility_mode="full",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=deterministic,
        refusal=None,
    )
    return 0, {
        "result": "ok",
        "compat_report": report,
        "active_instance": active_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ops CLI (install/instance management)")
    parser.add_argument("--format", default="json", choices=["json", "text"])
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--transaction-id", default=None)
    parser.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    sub = parser.add_subparsers(dest="section")

    installs = sub.add_parser("installs")
    installs_sub = installs.add_subparsers(dest="cmd")
    installs_list = installs_sub.add_parser("list")
    installs_list.add_argument("--search", action="append", default=[])

    instances = sub.add_parser("instances")
    instances_sub = instances.add_subparsers(dest="cmd")
    instances_list = instances_sub.add_parser("list")
    instances_list.add_argument("--search", action="append", default=[])
    instances_list.add_argument("--install-id", default=None)

    instances_create = instances_sub.add_parser("create")
    instances_create.add_argument("--install-manifest", required=True)
    instances_create.add_argument("--data-root", required=True)
    instances_create.add_argument("--instance-root", default=None)
    instances_create.add_argument("--instance-id", default=None)
    instances_create.add_argument("--mode", choices=["linked", "portable"], default="portable")
    instances_create.add_argument("--instance-kind", choices=["instance.client", "instance.server", "instance.tooling"], default="instance.client")
    instances_create.add_argument("--store-root", default=None)
    instances_create.add_argument("--active-profile", action="append", default=[])
    instances_create.add_argument("--active-modpack", action="append", default=[])
    instances_create.add_argument("--pack-root", action="append", default=[])
    instances_create.add_argument("--capability-lockfile", default=None)
    instances_create.add_argument("--sandbox-policy", default=None)
    instances_create.add_argument("--sandbox-policy-ref", default=None)
    instances_create.add_argument("--mod-policy-id", default="mod.policy.default")
    instances_create.add_argument("--overlay-conflict-policy-id", default="overlay.conflict.default")
    instances_create.add_argument("--default-session-template-id", default="session.template.default")
    instances_create.add_argument("--seed-policy", choices=["fixed", "prompt", "deterministic_counter"], default="prompt")
    instances_create.add_argument("--renderer-mode", choices=["software", "hardware_stub"], default=None)
    instances_create.add_argument("--ui-mode-default", choices=["cli", "tui", "rendered"], default="cli")
    instances_create.add_argument("--allow-read-only-fallback", action="store_true")
    instances_create.add_argument("--tick-budget-policy-id", default="tick.budget.default")
    instances_create.add_argument("--compute-profile-id", default="compute.profile.default")
    instances_create.add_argument("--save-ref", action="append", default=[])
    instances_create.add_argument("--last-opened-save-id", default="")
    instances_create.add_argument("--required-product-build", action="append", default=[])
    instances_create.add_argument("--required-contract-range", action="append", default=[])
    instances_create.add_argument("--update-channel", default="stable")
    instances_create.add_argument("--created-at", default=None)
    instances_create.add_argument("--simulate-failure", default=None)

    instances_clone = instances_sub.add_parser("clone")
    instances_clone.add_argument("--source-manifest", required=True)
    instances_clone.add_argument("--data-root", required=True)
    instances_clone.add_argument("--instance-id", default=None)
    instances_clone.add_argument("--sandbox-policy", default=None)
    instances_clone.add_argument("--created-at", default=None)
    instances_clone.add_argument("--simulate-failure", default=None)

    instances_fork = instances_sub.add_parser("fork")
    instances_fork.add_argument("--source-manifest", required=True)
    instances_fork.add_argument("--data-root", required=True)
    instances_fork.add_argument("--instance-id", default=None)
    instances_fork.add_argument("--sandbox-policy", default=None)
    instances_fork.add_argument("--created-at", default=None)
    instances_fork.add_argument("--simulate-failure", default=None)

    instances_edit = instances_sub.add_parser("edit")
    instances_edit.add_argument("--instance-manifest", required=True)
    instances_edit.add_argument("--install-manifest", default=None)
    instances_edit.add_argument("--sandbox-policy", default=None)
    instances_edit.add_argument("--mode", choices=["linked", "portable"], default=None)
    instances_edit.add_argument("--instance-kind", choices=["instance.client", "instance.server", "instance.tooling"], default=None)
    instances_edit.add_argument("--store-root", default=None)
    instances_edit.add_argument("--profile", action="append", default=[])
    instances_edit.add_argument("--modpack", action="append", default=[])
    instances_edit.add_argument("--save-ref", action="append", default=[])
    instances_edit.add_argument("--last-opened-save-id", default=None)
    instances_edit.add_argument("--renderer-mode", choices=["software", "hardware_stub"], default=None)
    instances_edit.add_argument("--ui-mode-default", choices=["cli", "tui", "rendered"], default=None)
    instances_edit.add_argument("--allow-read-only-fallback", action="store_true")
    instances_edit.add_argument("--deny-read-only-fallback", action="store_true")
    instances_edit.add_argument("--tick-budget-policy-id", default=None)
    instances_edit.add_argument("--compute-profile-id", default=None)
    instances_edit.add_argument("--default-session-template-id", default=None)
    instances_edit.add_argument("--seed-policy", choices=["fixed", "prompt", "deterministic_counter"], default=None)
    instances_edit.add_argument("--mod-policy-id", default=None)
    instances_edit.add_argument("--overlay-conflict-policy-id", default=None)
    instances_edit.add_argument("--required-product-build", action="append", default=[])
    instances_edit.add_argument("--required-contract-range", action="append", default=[])

    instances_activate = instances_sub.add_parser("activate")
    instances_activate.add_argument("--install-manifest", required=True)
    instances_activate.add_argument("--instance-manifest", required=True)
    instances_activate.add_argument("--sandbox-policy", default=None)

    compat = sub.add_parser("compat")
    compat_sub = compat.add_subparsers(dest="cmd")

    compat_cs = compat_sub.add_parser("client-server")
    compat_cs.add_argument("--client-cap", action="append", default=[])
    compat_cs.add_argument("--server-cap", action="append", default=[])
    compat_cs.add_argument("--required-cap", action="append", default=[])
    compat_cs.add_argument("--context", default="join")
    compat_cs.add_argument("--install-id", default=None)
    compat_cs.add_argument("--instance-id", default=None)
    compat_cs.add_argument("--runtime-id", default=None)

    compat_shard = compat_sub.add_parser("shard-transfer")
    compat_shard.add_argument("--source-cap", action="append", default=[])
    compat_shard.add_argument("--target-cap", action="append", default=[])
    compat_shard.add_argument("--required-cap", action="append", default=[])
    compat_shard.add_argument("--context", default="update")
    compat_shard.add_argument("--install-id", default=None)
    compat_shard.add_argument("--instance-id", default=None)
    compat_shard.add_argument("--runtime-id", default=None)

    compat_tools_cmd = compat_sub.add_parser("tools")
    compat_tools_cmd.add_argument("--tool-cap", action="append", default=[])
    compat_tools_cmd.add_argument("--required-cap", action="append", default=[])
    compat_tools_cmd.add_argument("--context", default="load")
    compat_tools_cmd.add_argument("--install-id", default=None)
    compat_tools_cmd.add_argument("--instance-id", default=None)
    compat_tools_cmd.add_argument("--runtime-id", default=None)

    args = parser.parse_args()

    if args.section == "installs" and args.cmd == "list":
        installs = list_install_manifests(args.search)
        report = build_compat_report(
            context="load",
            install_id=None,
            instance_id=None,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=[],
            missing_capabilities=[],
            compatibility_mode="inspect-only",
            refusal_codes=[],
            mitigation_hints=[],
            deterministic=args.deterministic,
            refusal=None,
        )
        output = {
            "result": "ok",
            "compat_report": report,
            "installs": installs,
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "list":
        instances = list_instance_manifests(args.search, args.install_id)
        report = build_compat_report(
            context="load",
            install_id=args.install_id,
            instance_id=None,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=[],
            missing_capabilities=[],
            compatibility_mode="inspect-only",
            refusal_codes=[],
            mitigation_hints=[],
            deterministic=args.deterministic,
            refusal=None,
        )
        output = {
            "result": "ok",
            "compat_report": report,
            "instances": instances,
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "create":
        args.active_profiles = args.active_profile
        args.active_modpacks = args.active_modpack
        code, output = create_instance(args)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "instances" and args.cmd == "clone":
        code, output = clone_instance(args, fork_only=False)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "instances" and args.cmd == "fork":
        code, output = clone_instance(args, fork_only=True)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "instances" and args.cmd == "edit":
        code, output = edit_instance(args)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "instances" and args.cmd == "activate":
        code, output = activate_instance(args)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "compat" and args.cmd == "client-server":
        code, output = compat_client_server(args)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "compat" and args.cmd == "shard-transfer":
        code, output = compat_shard_transfer(args)
        print(json.dumps(output, indent=2))
        return code

    if args.section == "compat" and args.cmd == "tools":
        code, output = compat_tools(args)
        print(json.dumps(output, indent=2))
        return code

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
