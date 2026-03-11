import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.lib.content_store import (
    JSON_PAYLOAD,
    STORE_ROOT_MANIFEST,
    artifact_payload_path,
    build_store_locator,
    initialize_store_root,
    load_instance_json_artifact,
    resolve_instance_artifact_root,
    resolve_locator_path,
)
from src.lib.install import (
    compare_required_contract_ranges,
    compare_required_product_builds,
    normalize_contract_range,
    validate_install_manifest,
)
from src.lib.instance import (
    INSTANCE_KIND_CLIENT,
    INSTANCE_KIND_SERVER,
    INSTANCE_KIND_TOOLING,
    instance_active_modpacks,
    instance_active_profiles,
    instance_allow_read_only_fallback,
    instance_data_root,
    instance_install_id,
    instance_last_opened_save_id,
    instance_settings_payload,
    instance_ui_mode_default,
    validate_instance_manifest,
)


DEFAULT_INSTALL_MANIFEST = "install.manifest.json"
DEFAULT_INSTANCE_MANIFEST = "instance.manifest.json"
DEFAULT_ACTIVE_INSTALL = "active.install.json"
DEFAULT_ACTIVE_INSTANCE = "active.instance.json"
DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("LAUNCHER_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: str) -> None:
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


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


def resolve_install_manifest_from_instance(instance_root: str, instance_manifest: Dict[str, object]) -> str:
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


def instance_required_product_builds(instance_manifest: Dict[str, object]) -> Dict[str, str]:
    product_builds = dict(instance_manifest.get("required_product_builds") or {})
    return {
        str(key): str(value).strip()
        for key, value in sorted(product_builds.items(), key=lambda item: str(item[0]))
        if str(key).strip() and str(value).strip()
    }


def instance_required_contract_ranges(instance_manifest: Dict[str, object]) -> Dict[str, dict]:
    ranges = dict(instance_manifest.get("required_contract_ranges") or {})
    return {
        str(key): normalize_contract_range(value)
        for key, value in sorted(ranges.items(), key=lambda item: str(item[0]))
        if str(key).strip()
    }


def refusal_payload(code_id: int, code: str, message: str,
                    details: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


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
                        extensions: Optional[Dict[str, object]] = None,
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
        "extensions": extensions or {},
    }
    if refusal:
        payload["refusal"] = refusal
    return payload


def log_path(log_root: str) -> str:
    return os.path.join(log_root, "launcher.log")


def append_log(log_root: str, entry: dict) -> None:
    if not log_root:
        return
    ensure_dir(log_root)
    path = log_path(log_root)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def resolve_repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_ops_cli() -> str:
    return os.path.join(resolve_repo_root(), "tools", "ops", "ops_cli.py")


def resolve_share_cli() -> str:
    return os.path.join(resolve_repo_root(), "tools", "share", "share_cli.py")


def run_script(path: str, args: List[str]) -> Tuple[int, Dict[str, object], str]:
    cmd = [sys.executable, path] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.decode("utf-8", errors="ignore").strip()
    stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
    payload: Dict[str, object] = {}
    if stdout:
        try:
            payload = json.loads(stdout)
        except ValueError:
            payload = {}
    return proc.returncode, payload, stderr


def list_install_manifests(search_roots: List[str]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    seen = set()
    roots = search_roots or []
    if not roots:
        roots = ["."]
    for root in roots:
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
            results.append(normalize_install_entry(manifest, manifest_path))
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
                    results.append(normalize_install_entry(manifest, manifest_path))
    return sorted(results, key=lambda row: (str(row.get("install_id", "")), str(row.get("manifest_path", ""))))


def normalize_install_entry(manifest: dict, manifest_path: str) -> Dict[str, object]:
    binaries = manifest.get("binaries") or {}
    engine = binaries.get("engine") or {}
    game = binaries.get("game") or {}
    build_number = game.get("build_number")
    if build_number is None:
        build_number = engine.get("build_number")
    if build_number is None:
        build_number = manifest.get("build_identity")
    if build_number is None:
        product_builds = install_product_builds(manifest)
        if product_builds:
            build_number = next(iter(product_builds.values()))
    return {
        "install_id": manifest.get("install_id"),
        "install_root": resolve_install_root(manifest_path, manifest),
        "manifest_path": manifest_path.replace("\\", "/"),
        "engine_version": engine.get("product_version"),
        "game_version": game.get("product_version"),
        "build_number": build_number,
        "trust_tier": manifest.get("trust_tier"),
        "supported_capabilities": manifest.get("supported_capabilities") or [],
        "install_tags": manifest.get("install_tags") or [],
    }


def list_instance_manifests(search_roots: List[str], install_id: Optional[str]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    roots = search_roots or []
    if not roots:
        roots = ["."]
    for root in roots:
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
            results.append(normalize_instance_entry(manifest, manifest_path))
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
                    results.append(normalize_instance_entry(manifest, manifest_path))
    return sorted(results, key=lambda row: (str(row.get("instance_id", "")), str(row.get("manifest_path", ""))))


def normalize_instance_entry(manifest: dict, manifest_path: str) -> Dict[str, object]:
    settings = instance_settings_payload(manifest)
    return {
        "instance_id": manifest.get("instance_id"),
        "install_id": instance_install_id(manifest),
        "instance_kind": manifest.get("instance_kind"),
        "mode": manifest.get("mode", "portable"),
        "data_root": instance_data_root(manifest),
        "active_profiles": instance_active_profiles(manifest),
        "active_modpacks": instance_active_modpacks(manifest),
        "save_refs": list(manifest.get("save_refs") or []),
        "last_opened_save_id": instance_last_opened_save_id(manifest),
        "ui_mode_default": settings.get("ui_mode_default"),
        "manifest_path": manifest_path.replace("\\", "/"),
        "update_channel": settings.get("update_channel"),
    }


def discover_profiles(profile_roots: List[str]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    seen = set()
    roots = profile_roots or []
    if not roots:
        roots = [os.path.join(resolve_repo_root(), "data", "profiles")]
    for root in roots:
        if not root:
            continue
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            try:
                payload = load_json(path)
            except (OSError, ValueError):
                continue
            record = payload.get("record") if isinstance(payload, dict) else None
            if not isinstance(record, dict):
                continue
            profile_id = record.get("profile_id")
            if not profile_id or profile_id in seen:
                continue
            seen.add(profile_id)
            recommended = []
            for entry in (record.get("recommended_packs") or []):
                if isinstance(entry, dict) and entry.get("pack_id"):
                    recommended.append(entry.get("pack_id"))
                elif isinstance(entry, str):
                    recommended.append(entry)
            results.append({
                "profile_id": profile_id,
                "description": record.get("description"),
                "recommended_packs": sorted_unique(recommended),
                "ui_density": record.get("ui_density"),
                "verbosity": record.get("verbosity"),
                "warnings_level": record.get("warnings_level"),
                "profile_tags": record.get("profile_tags") or [],
                "source_path": path.replace("\\", "/"),
            })
    return results


def profile_recommendations(profile_ids: List[str], profiles: List[Dict[str, object]]) -> List[str]:
    by_id = {profile.get("profile_id"): profile for profile in profiles}
    packs: List[str] = []
    for pid in profile_ids:
        profile = by_id.get(pid)
        if not profile:
            continue
        packs.extend(profile.get("recommended_packs") or [])
    return sorted_unique(packs)


def resolve_state_root(args: argparse.Namespace) -> str:
    if getattr(args, "state_root", None):
        return args.state_root
    env = os.environ.get("LAUNCHER_STATE_ROOT")
    return env or ""


def load_state(state_root: str) -> dict:
    if not state_root:
        return {}
    path = os.path.join(state_root, "launcher_state.json")
    if not os.path.isfile(path):
        return {}
    try:
        return load_json(path)
    except (OSError, ValueError):
        return {}


def write_state(state_root: str, payload: dict) -> None:
    if not state_root:
        return
    path = os.path.join(state_root, "launcher_state.json")
    write_json(path, payload)


def resolve_data_root(instance_root: str, data_root: str) -> str:
    if not data_root:
        return instance_root
    if os.path.isabs(data_root):
        return data_root
    return os.path.join(instance_root, data_root)


def resolve_lockfile(instance_root: str, lock_ref: str) -> str:
    if not lock_ref:
        return ""
    if os.path.isabs(lock_ref):
        return lock_ref
    return os.path.join(instance_root, lock_ref)


def resolve_pack_lock(instance_root: str, instance_manifest: dict) -> Tuple[Optional[dict], str]:
    pack_lock_hash = str(instance_manifest.get("pack_lock_hash", "")).strip()
    if pack_lock_hash:
        payload = load_instance_json_artifact(instance_root, instance_manifest, "locks", pack_lock_hash)
        if payload:
            return payload, "hash"
    lockfile_path = resolve_lockfile(instance_root, instance_manifest.get("capability_lockfile") or "")
    return load_lockfile(lockfile_path), lockfile_path


def resolve_profile_bundle(instance_root: str, instance_manifest: dict) -> Tuple[Optional[dict], str]:
    profile_bundle_hash = str(instance_manifest.get("profile_bundle_hash", "")).strip()
    if not profile_bundle_hash:
        return None, ""
    payload = load_instance_json_artifact(instance_root, instance_manifest, "profiles", profile_bundle_hash)
    return payload, profile_bundle_hash


def resolve_pack_payloads(instance_root: str, instance_manifest: dict, lockfile: Optional[dict]) -> Dict[str, str]:
    payloads: Dict[str, str] = {}
    if not lockfile:
        return payloads
    for pack_id, artifact_hash in sorted((lockfile.get("pack_hashes") or {}).items()):
        pack_token = str(pack_id or "").strip()
        hash_token = str(artifact_hash or "").strip()
        if not pack_token or not hash_token:
            continue
        artifact_root = resolve_instance_artifact_root(instance_root, instance_manifest, "packs", hash_token)
        payload_root = artifact_payload_path(artifact_root, "tree")
        if os.path.isdir(payload_root):
            payloads[pack_token] = payload_root
    return payloads


def load_lockfile(path: str) -> Optional[dict]:
    if not path or not os.path.isfile(path):
        return None
    try:
        return load_json(path)
    except (OSError, ValueError):
        return None


def collect_required_capabilities(lockfile: Optional[dict]) -> List[str]:
    if not lockfile:
        return []
    required = []
    for entry in (lockfile.get("resolutions") or []):
        if isinstance(entry, dict) and entry.get("capability_id"):
            required.append(entry.get("capability_id"))
    return sorted_unique(required)


def collect_required_packs(lockfile: Optional[dict]) -> List[str]:
    packs = []
    if not lockfile:
        return packs
    for entry in (lockfile.get("ordered_pack_ids") or []):
        if entry:
            packs.append(str(entry))
    for entry in (lockfile.get("resolutions") or []):
        if isinstance(entry, dict) and entry.get("provider_pack_id"):
            packs.append(entry.get("provider_pack_id"))
    for entry in (lockfile.get("pack_refs") or []):
        if isinstance(entry, dict) and entry.get("pack_id"):
            packs.append(entry.get("pack_id"))
        elif isinstance(entry, str):
            packs.append(entry)
    return sorted_unique(packs)


def pack_roots(install_root: str, data_root: str, extra_roots: List[str]) -> List[str]:
    roots: List[str] = []
    for root in (extra_roots or []):
        if root:
            roots.append(root)
    if data_root:
        roots.append(os.path.join(data_root, "packs"))
    if install_root:
        roots.append(os.path.join(install_root, "packs"))
    return [normalize_path(root) for root in roots if root]


def pack_location(pack_id: str, roots: List[str]) -> Optional[str]:
    for root in roots:
        if os.path.isdir(root) and os.path.basename(os.path.normpath(root)) == pack_id:
            return root
        path = os.path.join(root, pack_id)
        if os.path.isdir(path):
            return path
    return None


def pack_source_for_root(root: str, install_root: str, data_root: str) -> str:
    normalized_root = normalize_path(root)
    if "embedded_artifacts" in normalized_root:
        return "embedded"
    if "/store/packs/" in normalized_root.replace("\\", "/"):
        return "shared-store"
    if install_root and normalized_root.startswith(normalize_path(install_root)):
        return "bundled"
    if data_root and normalized_root.startswith(normalize_path(data_root)):
        return "local"
    return "local"


def build_pack_status(pack_ids: List[str],
                      roots: List[str],
                      direct_payloads: Dict[str, str],
                      install_root: str,
                      data_root: str,
                      status_label: str) -> Tuple[List[Dict[str, object]], List[str]]:
    entries: List[Dict[str, object]] = []
    missing: List[str] = []
    for pack_id in sorted_unique(pack_ids):
        location = direct_payloads.get(pack_id) or pack_location(pack_id, roots)
        if location:
            entries.append({
                "pack_id": pack_id,
                "status": status_label,
                "source": pack_source_for_root(location, install_root, data_root),
                "root": location.replace("\\", "/"),
            })
        else:
            missing.append(pack_id)
            entries.append({
                "pack_id": pack_id,
                "status": "missing",
                "source": "remote",
                "root": "",
            })
    return entries, sorted_unique(missing)


def perform_preflight(args: argparse.Namespace,
                      install_manifest_path: str,
                      instance_manifest_path: str,
                      profiles: List[Dict[str, object]]) -> Tuple[int, Dict[str, object]]:
    deterministic = args.deterministic
    if not os.path.isfile(instance_manifest_path):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance manifest not found",
                                  {"manifest": os.path.basename(instance_manifest_path)})
        report = build_compat_report("run", None, None, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    instance_validation = validate_instance_manifest(
        repo_root=REPO_ROOT,
        instance_manifest_path=instance_manifest_path,
    )
    if instance_validation.get("result") != "complete":
        refusal = refusal_payload(
            5,
            str(instance_validation.get("refusal_code", "REFUSE_INSTANCE_INVALID")).upper() or "REFUSE_INSTANCE_INVALID",
            "instance manifest verification failed",
            {"manifest": os.path.basename(instance_manifest_path)},
        )
        report = build_compat_report(
            "run",
            None,
            None,
            None,
            args.capability_baseline,
            [],
            [],
            [],
            "refuse",
            [str(instance_validation.get("refusal_code", ""))],
            ["repair or recreate the selected instance"],
            deterministic,
            {"instance_validation": instance_validation},
            refusal,
        )
        return 3, {"result": "refused", "compat_report": report}
    instance_manifest = dict(instance_validation.get("instance_manifest") or {})
    instance_id = instance_manifest.get("instance_id")
    instance_kind = str(instance_manifest.get("instance_kind", INSTANCE_KIND_CLIENT)).strip() or INSTANCE_KIND_CLIENT
    instance_root = os.path.dirname(instance_manifest_path)
    data_root = resolve_data_root(instance_root, instance_data_root(instance_manifest))
    allow_read_only_fallback = instance_allow_read_only_fallback(instance_manifest)
    selected_save_id = str(getattr(args, "save", "") or "").strip() or instance_last_opened_save_id(instance_manifest)
    if selected_save_id and selected_save_id not in list(instance_manifest.get("save_refs") or []):
        refusal = refusal_payload(
            1,
            "REFUSE_INVALID_INTENT",
            "requested save is not associated with this instance",
            {"save_id": selected_save_id, "instance_id": instance_id or ""},
        )
        report = build_compat_report(
            "run",
            instance_install_id(instance_manifest),
            instance_id,
            None,
            args.capability_baseline,
            [],
            [],
            [],
            "refuse",
            [refusal.get("code")],
            [],
            deterministic,
            {"instance_validation": instance_validation},
            refusal,
        )
        return 3, {"result": "refused", "compat_report": report}

    if not install_manifest_path:
        install_manifest_path = resolve_install_manifest_from_instance(instance_root, instance_manifest)
    if not os.path.isfile(install_manifest_path):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "install manifest not found",
                                  {"manifest": os.path.basename(install_manifest_path or DEFAULT_INSTALL_MANIFEST)})
        report = build_compat_report("run", instance_install_id(instance_manifest), instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], ["select or provide a compatible install manifest"],
                                     deterministic, {"instance_validation": instance_validation}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    install_manifest = load_json(install_manifest_path)
    install_validation = validate_install_manifest(
        repo_root=REPO_ROOT,
        install_manifest_path=install_manifest_path,
        manifest_payload=install_manifest,
    )
    if install_validation.get("result") != "complete":
        refusal = refusal_payload(
            5,
            str(install_validation.get("refusal_code", "REFUSE_INSTALL_INVALID")).upper() or "REFUSE_INSTALL_INVALID",
            "install manifest verification failed",
            {"manifest": os.path.basename(install_manifest_path)},
        )
        report = build_compat_report(
            "run",
            install_manifest.get("install_id"),
            instance_id,
            None,
            args.capability_baseline,
            [],
            [],
            [],
            "refuse",
            [str(install_validation.get("refusal_code", ""))],
            ["repair or reinstall the selected build"],
            deterministic,
            {"install_validation": install_validation, "instance_validation": instance_validation},
            refusal,
        )
        return 3, {"result": "refused", "compat_report": report}
    install_manifest = dict(install_validation.get("install_manifest") or install_manifest)
    install_id = install_manifest.get("install_id")
    install_root = resolve_install_root(install_manifest_path, install_manifest)
    lockfile, lockfile_source = resolve_pack_lock(instance_root, instance_manifest)
    profile_bundle_payload, profile_bundle_source = resolve_profile_bundle(instance_root, instance_manifest)

    if not lockfile:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "capability lockfile missing",
                                  {"lockfile": os.path.basename(str(lockfile_source or "capability.lock"))})
        report = build_compat_report("run", install_id, instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], ["regenerate lockfile"],
                                     deterministic, {"instance_validation": instance_validation, "install_validation": install_validation}, refusal)
        return 3, {"result": "refused", "compat_report": report}
    if str(lockfile.get("pack_lock_hash", "")).strip() and str(lockfile.get("pack_lock_hash", "")).strip() != str(instance_manifest.get("pack_lock_hash", "")).strip():
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "pack lock hash does not match instance manifest",
                                  {"instance_pack_lock_hash": instance_manifest.get("pack_lock_hash"), "lockfile_pack_lock_hash": lockfile.get("pack_lock_hash")})
        report = build_compat_report("run", install_id, instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], ["regenerate the instance pack lock"],
                                     deterministic, {"instance_validation": instance_validation, "install_validation": install_validation}, refusal)
        return 3, {"result": "refused", "compat_report": report}
    if not profile_bundle_payload:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "profile bundle artifact missing",
                                  {"profile_bundle_hash": str(instance_manifest.get("profile_bundle_hash", "")).strip(), "source": str(profile_bundle_source or "")})
        report = build_compat_report("run", install_id, instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], ["materialize the profile bundle artifact"],
                                     deterministic, {"instance_validation": instance_validation, "install_validation": install_validation}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    required_caps = collect_required_capabilities(lockfile)
    provided_caps = sorted_unique(install_manifest.get("supported_capabilities") or [])
    missing_caps = sorted(set(required_caps) - set(provided_caps))
    required_builds = instance_required_product_builds(instance_manifest)
    build_mismatches = compare_required_product_builds(install_manifest, required_builds)
    required_contracts = instance_required_contract_ranges(instance_manifest)
    contract_mismatches = compare_required_contract_ranges(install_manifest, required_contracts)
    install_switch = {
        "instance_install_id": instance_install_id(instance_manifest),
        "selected_install_id": str(install_id or "").strip(),
        "switched": bool(instance_install_id(instance_manifest)) and str(instance_install_id(instance_manifest)).strip() != str(install_id or "").strip(),
    }

    profile_ids = args.profile or instance_active_profiles(instance_manifest)
    recommended_packs = profile_recommendations(profile_ids, profiles)
    required_packs = collect_required_packs(lockfile)
    direct_pack_payloads = resolve_pack_payloads(instance_root, instance_manifest, lockfile)
    roots = pack_roots(install_root, data_root, args.pack_root or [])

    required_entries, missing_required = build_pack_status(required_packs, roots,
                                                           direct_pack_payloads,
                                                           install_root, data_root, "required")
    optional_entries, missing_optional = build_pack_status(recommended_packs, roots,
                                                           direct_pack_payloads,
                                                           install_root, data_root, "optional")

    instance_kind_mismatch = False
    if instance_kind == INSTANCE_KIND_SERVER and args.run_mode in ("play", "client"):
        instance_kind_mismatch = True
    elif instance_kind == INSTANCE_KIND_TOOLING and args.run_mode in ("play", "client", "server"):
        instance_kind_mismatch = True
    elif instance_kind == INSTANCE_KIND_CLIENT and args.run_mode == "server":
        instance_kind_mismatch = True

    degrade_reasons: List[str] = []
    extensions = {
        "run_mode": args.run_mode,
        "instance_kind": instance_kind,
        "save_refs": list(instance_manifest.get("save_refs") or []),
        "selected_save_id": selected_save_id,
        "allow_read_only_fallback": allow_read_only_fallback,
        "ui_mode_default": instance_ui_mode_default(instance_manifest),
        "required_packs": required_packs,
        "missing_packs": missing_required,
        "optional_packs": recommended_packs,
        "optional_missing_packs": missing_optional,
        "required_product_builds": required_builds,
        "build_mismatches": build_mismatches,
        "required_contract_ranges": required_contracts,
        "contract_range_mismatches": contract_mismatches,
        "install_validation": install_validation,
        "instance_validation": instance_validation,
        "install_switch": install_switch,
        "profile_bundle_hash": str(instance_manifest.get("profile_bundle_hash", "")).strip(),
        "pack_status": required_entries + optional_entries,
    }

    refusal_codes: List[str] = []
    mitigation: List[str] = []
    refusal = None
    mode = "full"

    if instance_kind_mismatch:
        if allow_read_only_fallback or args.run_mode in ("inspect", "replay"):
            mode = "inspect-only"
            degrade_reasons.append("instance_kind_mismatch")
            mitigation = ["use a run mode compatible with the instance kind for full runtime"]
        else:
            mode = "refuse"
            refusal_codes = ["REFUSE_INSTANCE_KIND_MISMATCH"]
            refusal = refusal_payload(
                1,
                "REFUSE_INSTANCE_KIND_MISMATCH",
                "selected run mode is incompatible with this instance kind",
                {"instance_kind": instance_kind, "run_mode": args.run_mode},
            )
    elif missing_caps:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "required capabilities missing",
                                  {"missing": missing_caps})
        mitigation = ["update install capabilities"]
    elif build_mismatches or contract_mismatches:
        if args.run_mode in ("inspect", "replay") or allow_read_only_fallback:
            mode = "inspect-only"
            degrade_reasons.append("read_only_contract_fallback")
            mitigation = ["select a matching install for full runtime"]
        else:
            mode = "refuse"
            refusal_codes = ["REFUSE_INSTALL_BUILD_MISMATCH"]
            refusal = refusal_payload(
                5,
                "REFUSE_INSTALL_BUILD_MISMATCH",
                "required product builds or contract ranges are not present in this install",
                {
                    "build_mismatches": build_mismatches,
                    "contract_mismatches": contract_mismatches,
                },
            )
            mitigation = ["select a compatible install or recreate the instance against this build set"]
    elif missing_required:
        missing_mode = (lockfile.get("missing_mode") or "degraded").lower()
        if missing_mode in ("inspect-only", "inspect_only"):
            mode = "inspect-only"
        elif missing_mode in ("frozen", "freeze"):
            mode = "frozen"
        elif missing_mode in ("refuse", "reject"):
            mode = "refuse"
            refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
            refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                      "required packs missing",
                                      {"missing_packs": missing_required})
        else:
            mode = "degraded"
            degrade_reasons.append("missing_required_packs")
        mitigation = ["install missing packs"] if missing_required else []

    if args.run_mode in ("inspect", "replay") and mode != "refuse":
        mode = "inspect-only"
        if "inspect_or_replay_requested" not in degrade_reasons:
            degrade_reasons.append("inspect_or_replay_requested")

    if mode in ("degraded", "frozen", "inspect-only"):
        ui_fallbacks = {
            "rendered": "tui",
            "tui": "cli",
            "cli": "cli",
        }
        requested_ui = str(instance_ui_mode_default(instance_manifest)).strip() or "cli"
        extensions["ui_mode_effective"] = ui_fallbacks.get(requested_ui, "cli")
    else:
        extensions["ui_mode_effective"] = instance_ui_mode_default(instance_manifest)
    extensions["degrade_reasons"] = sorted_unique(degrade_reasons)
    extensions["degrade_logged"] = bool(degrade_reasons)

    report = build_compat_report("run",
                                 install_id,
                                 instance_id,
                                 None,
                                 args.capability_baseline,
                                 required_caps,
                                 provided_caps,
                                 missing_caps,
                                 mode,
                                 refusal_codes,
                                 mitigation,
                                 deterministic,
                                 extensions,
                                 refusal)

    compat_out = args.compat_out
    if not compat_out:
        compat_out = os.path.join(instance_root, "compat", "compat_report.json")
    try:
        write_json(compat_out, report)
    except OSError:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "compat_report write failed",
                                  {"output": os.path.basename(compat_out)})
        report = build_compat_report("run",
                                     install_id,
                                     instance_id,
                                     None,
                                     args.capability_baseline,
                                     required_caps,
                                     provided_caps,
                                     missing_caps,
                                     "refuse",
                                     [refusal.get("code")],
                                     ["check output permissions"],
                                     deterministic,
                                     extensions,
                                     refusal)
        return 3, {"result": "refused", "compat_report": report}

    output = {
        "result": "refused" if mode == "refuse" else "ok",
        "compat_report": report,
        "compat_report_path": compat_out.replace("\\", "/"),
    }
    return (3 if mode == "refuse" else 0), output


def resolve_instance_selection(args: argparse.Namespace, state: dict) -> str:
    manifest_path = str(getattr(args, "instance_manifest", "") or "").strip()
    if manifest_path and os.path.isfile(manifest_path):
        return os.path.abspath(manifest_path)
    token = str(getattr(args, "instance", "") or "").strip()
    if token and os.path.isfile(token):
        return os.path.abspath(token)
    active_manifest = str(state.get("active_instance_manifest", "") or "").strip()
    active_instance_id = str(state.get("active_instance_id", "") or "").strip()
    if token and active_instance_id == token and active_manifest and os.path.isfile(active_manifest):
        return os.path.abspath(active_manifest)
    search_roots = list(getattr(args, "search", []) or [])
    if active_manifest:
        search_roots.append(os.path.dirname(os.path.abspath(active_manifest)))
    candidates = list_instance_manifests(search_roots, None)
    matches = [
        os.path.abspath(path if os.path.isabs(path) else os.path.join(resolve_repo_root(), path))
        for path in [str(row.get("manifest_path", "")).strip() for row in candidates]
        if str(row.get("instance_id", "")).strip() == token and str(path).strip()
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1 and active_manifest and os.path.abspath(active_manifest) in matches:
        return os.path.abspath(active_manifest)
    return ""


def resolve_install_selection(args: argparse.Namespace, state: dict, instance_root: str, instance_manifest: dict) -> str:
    manifest_path = str(getattr(args, "install_manifest", "") or "").strip()
    if manifest_path and os.path.isfile(manifest_path):
        return os.path.abspath(manifest_path)
    active_manifest = str(state.get("active_install_manifest", "") or "").strip()
    if active_manifest and os.path.isfile(active_manifest):
        return os.path.abspath(active_manifest)
    inferred = resolve_install_manifest_from_instance(instance_root, instance_manifest)
    if inferred and os.path.isfile(inferred):
        return os.path.abspath(inferred)
    return ""


def run_with_resolved_manifests(args: argparse.Namespace, install_manifest_path: str, instance_manifest_path: str) -> Tuple[int, Dict[str, object]]:
    profiles = discover_profiles([])
    rc, payload = perform_preflight(args, install_manifest_path, instance_manifest_path, profiles)
    report = payload.get("compat_report") if isinstance(payload, dict) else None
    if rc != 0:
        return rc, payload
    mode = ""
    if isinstance(report, dict):
        mode = report.get("compatibility_mode") or ""
    if mode in ("degraded", "frozen", "inspect-only") and not args.confirm:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "confirmation required for non-full run",
                                  {"mode": mode})
        report = build_compat_report("run",
                                     report.get("install_id") if report else None,
                                     report.get("instance_id") if report else None,
                                     None,
                                     args.capability_baseline,
                                     report.get("required_capabilities") if report else [],
                                     report.get("provided_capabilities") if report else [],
                                     report.get("missing_capabilities") if report else [],
                                     mode,
                                     [refusal.get("code")],
                                     ["confirm degraded run"],
                                     args.deterministic,
                                     report.get("extensions") if report else {},
                                     refusal)
        return 3, {"result": "refused", "compat_report": report}
    run_launcher_action(args.log_root or os.path.dirname(instance_manifest_path),
                        "run", "COMMIT", "ok", args.deterministic,
                        {
                            "run_mode": args.run_mode,
                            "save_id": (
                                str(((report or {}).get("extensions") or {}).get("selected_save_id", "")).strip()
                                or str(getattr(args, "save", "") or "").strip()
                            ),
                        })
    payload["run_mode"] = args.run_mode
    payload["install_manifest"] = install_manifest_path.replace("\\", "/")
    payload["instance_manifest"] = instance_manifest_path.replace("\\", "/")
    payload["save_id"] = (
        str(((report or {}).get("extensions") or {}).get("selected_save_id", "")).strip()
        or str(getattr(args, "save", "") or "").strip()
    )
    return 0, payload


def run_launcher_action(log_root: str,
                        action: str,
                        state: str,
                        result: str,
                        deterministic: bool,
                        details: Optional[Dict[str, object]] = None) -> None:
    append_log(log_root, {
        "action": action,
        "state": state,
        "result": result,
        "timestamp": now_timestamp(deterministic),
        "details": details or {},
    })


def main() -> int:
    parser = argparse.ArgumentParser(description="Launcher CLI (installs, instances, preflight, bundles)")
    parser.add_argument("--format", default="json", choices=["json"])
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--state-root", default=None)
    parser.add_argument("--log-root", default=None)
    parser.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    sub = parser.add_subparsers(dest="section")

    installs = sub.add_parser("installs")
    installs_sub = installs.add_subparsers(dest="cmd")
    installs_list = installs_sub.add_parser("list")
    installs_list.add_argument("--search", action="append", default=[])
    installs_select = installs_sub.add_parser("select")
    installs_select.add_argument("--manifest", required=True)
    installs_active = installs_sub.add_parser("active")

    instances = sub.add_parser("instances")
    instances_sub = instances.add_subparsers(dest="cmd")
    instances_list = instances_sub.add_parser("list")
    instances_list.add_argument("--search", action="append", default=[])
    instances_list.add_argument("--install-id", default=None)
    instances_select = instances_sub.add_parser("select")
    instances_select.add_argument("--manifest", required=True)

    instances_create = instances_sub.add_parser("create")
    instances_create.add_argument("--install-manifest", required=True)
    instances_create.add_argument("--data-root", required=True)
    instances_create.add_argument("--instance-root", default=None)
    instances_create.add_argument("--instance-id", default=None)
    instances_create.add_argument("--mode", choices=["linked", "portable"], default="portable")
    instances_create.add_argument("--instance-kind", choices=["instance.client", "instance.server", "instance.tooling"], default="instance.client")
    instances_create.add_argument("--store-root", default=None)
    instances_create.add_argument("--profile", action="append", default=[])
    instances_create.add_argument("--modpack", action="append", default=[])
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

    instances_clone = instances_sub.add_parser("clone")
    instances_clone.add_argument("--source-manifest", required=True)
    instances_clone.add_argument("--data-root", required=True)
    instances_clone.add_argument("--instance-id", default=None)
    instances_clone.add_argument("--created-at", default=None)

    instances_fork = instances_sub.add_parser("fork")
    instances_fork.add_argument("--source-manifest", required=True)
    instances_fork.add_argument("--data-root", required=True)
    instances_fork.add_argument("--instance-id", default=None)
    instances_fork.add_argument("--created-at", default=None)

    instances_activate = instances_sub.add_parser("activate")
    instances_activate.add_argument("--install-manifest", required=True)
    instances_activate.add_argument("--instance-manifest", required=True)

    instances_delete = instances_sub.add_parser("delete")
    instances_delete.add_argument("--instance-manifest", required=True)
    instances_delete.add_argument("--confirm", action="store_true")
    instances_delete.add_argument("--delete-data", action="store_true")

    instances_set_profiles = instances_sub.add_parser("set-profiles")
    instances_set_profiles.add_argument("--instance-manifest", required=True)
    instances_set_profiles.add_argument("--profile", action="append", default=[])
    instances_set_profiles.add_argument("--confirm", action="store_true")

    profiles = sub.add_parser("profiles")
    profiles_sub = profiles.add_subparsers(dest="cmd")
    profiles_list = profiles_sub.add_parser("list")
    profiles_list.add_argument("--profile-root", action="append", default=[])
    list_profiles = sub.add_parser("list-profiles")
    list_profiles.add_argument("--profile-root", action="append", default=[])

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--install-manifest", required=True)
    preflight.add_argument("--instance-manifest", required=True)
    preflight.add_argument("--profile", action="append", default=[])
    preflight.add_argument("--pack-root", action="append", default=[])
    preflight.add_argument("--compat-out", default=None)
    preflight.add_argument("--save", default="")
    preflight.add_argument("--run-mode", default="play",
                           choices=["play", "client", "server", "inspect", "replay"])

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("--install-manifest", required=True)
    run_cmd.add_argument("--instance-manifest", required=True)
    run_cmd.add_argument("--profile", action="append", default=[])
    run_cmd.add_argument("--pack-root", action="append", default=[])
    run_cmd.add_argument("--compat-out", default=None)
    run_cmd.add_argument("--save", default="")
    run_cmd.add_argument("--run-mode", default="play",
                         choices=["play", "client", "server", "inspect", "replay"])
    run_cmd.add_argument("--confirm", action="store_true")

    start_cmd = sub.add_parser("start")
    start_cmd.add_argument("--instance", required=True)
    start_cmd.add_argument("--instance-manifest", default=None)
    start_cmd.add_argument("--install-manifest", default=None)
    start_cmd.add_argument("--search", action="append", default=[])
    start_cmd.add_argument("--profile", action="append", default=[])
    start_cmd.add_argument("--pack-root", action="append", default=[])
    start_cmd.add_argument("--compat-out", default=None)
    start_cmd.add_argument("--save", default="")
    start_cmd.add_argument("--run-mode", default="play",
                           choices=["play", "client", "server", "inspect", "replay"])
    start_cmd.add_argument("--confirm", action="store_true")

    packs = sub.add_parser("packs")
    packs_sub = packs.add_subparsers(dest="cmd")
    packs_list = packs_sub.add_parser("list")
    packs_list.add_argument("--install-manifest", default=None)
    packs_list.add_argument("--instance-manifest", default=None)
    packs_list.add_argument("--pack-root", action="append", default=[])
    packs_list.add_argument("--profile", action="append", default=[])

    packs_add = packs_sub.add_parser("add")
    packs_add.add_argument("--pack-path", required=True)
    packs_add.add_argument("--data-root", required=True)
    packs_add.add_argument("--confirm", action="store_true")

    packs_remove = packs_sub.add_parser("remove")
    packs_remove.add_argument("--pack-id", required=True)
    packs_remove.add_argument("--data-root", required=True)
    packs_remove.add_argument("--confirm", action="store_true")

    bundles = sub.add_parser("bundles")
    bundles_sub = bundles.add_subparsers(dest="cmd")
    bundles_inspect = bundles_sub.add_parser("inspect")
    bundles_inspect.add_argument("--bundle", required=True)
    bundles_inspect.add_argument("--available-pack", action="append", default=[])

    bundles_import = bundles_sub.add_parser("import")
    bundles_import.add_argument("--bundle", required=True)
    bundles_import.add_argument("--available-pack", action="append", default=[])
    bundles_import.add_argument("--require-full", action="store_true")
    bundles_import.add_argument("--confirm", action="store_true")
    bundles_import.add_argument("--out", default=None)
    bundles_import.add_argument("--instance-id", default=None)
    bundles_import.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    bundles_import.add_argument("--store-root", default=None)
    bundles_import_save = bundles_sub.add_parser("import-save")
    bundles_import_save.add_argument("--bundle", required=True)
    bundles_import_save.add_argument("--available-pack", action="append", default=[])
    bundles_import_save.add_argument("--require-full", action="store_true")
    bundles_import_save.add_argument("--confirm", action="store_true")
    bundles_import_save.add_argument("--out", default=None)
    bundles_import_save.add_argument("--instance-id", default=None)
    bundles_import_save.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    bundles_import_save.add_argument("--store-root", default=None)
    bundles_import_replay = bundles_sub.add_parser("import-replay")
    bundles_import_replay.add_argument("--bundle", required=True)
    bundles_import_replay.add_argument("--available-pack", action="append", default=[])
    bundles_import_replay.add_argument("--require-full", action="store_true")
    bundles_import_replay.add_argument("--confirm", action="store_true")
    bundles_import_replay.add_argument("--out", default=None)
    bundles_import_replay.add_argument("--instance-id", default=None)
    bundles_import_replay.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    bundles_import_replay.add_argument("--store-root", default=None)
    bundles_import_modpack = bundles_sub.add_parser("import-modpack")
    bundles_import_modpack.add_argument("--bundle", required=True)
    bundles_import_modpack.add_argument("--available-pack", action="append", default=[])
    bundles_import_modpack.add_argument("--require-full", action="store_true")
    bundles_import_modpack.add_argument("--confirm", action="store_true")
    bundles_import_modpack.add_argument("--out", default=None)
    bundles_import_modpack.add_argument("--instance-id", default=None)
    bundles_import_modpack.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    bundles_import_modpack.add_argument("--store-root", default=None)

    bundles_export = bundles_sub.add_parser("export")
    bundles_export.add_argument("--bundle-type", required=True)
    bundles_export.add_argument("--artifact", required=True)
    bundles_export.add_argument("--lockfile", default=None)
    bundles_export.add_argument("--compat-report", default=None)
    bundles_export.add_argument("--instance-metadata", default=None)
    bundles_export.add_argument("--runtime-metadata", default=None)
    bundles_export.add_argument("--reference", action="append", default=[])
    bundles_export.add_argument("--pack-ref", action="append", default=[])
    bundles_export.add_argument("--embed-pack", action="append", default=[])
    bundles_export.add_argument("--bundle-id", default=None)
    bundles_export.add_argument("--bundle-format-version", type=int, default=None)
    bundles_export.add_argument("--bundle-tag", action="append", default=[])
    bundles_export.add_argument("--created-at", default=None)
    bundles_export.add_argument("--created-by", default=None)
    bundles_export.add_argument("--tool-version", default=None)
    bundles_export.add_argument("--trust-tier", default=None)
    bundles_export.add_argument("--out", required=True)
    bundles_export_instance = bundles_sub.add_parser("export-instance")
    bundles_export_instance.add_argument("--instance-manifest", required=True)
    bundles_export_instance.add_argument("--bundle-type", default="instance")
    bundles_export_instance.add_argument("--out", required=True)

    paths_cmd = sub.add_parser("paths")
    paths_cmd.add_argument("--instance-manifest", default=None)
    paths_cmd.add_argument("--data-root", default=None)

    args = parser.parse_args()

    log_root = args.log_root

    if args.section == "installs" and args.cmd == "list":
        installs = list_install_manifests(args.search)
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic, {}, None)
        output = {"result": "ok", "compat_report": report, "installs": installs}
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "installs" and args.cmd == "select":
        state_root = resolve_state_root(args)
        if not state_root:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "state root required for install selection", {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        if not os.path.isfile(args.manifest):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "install manifest not found",
                                      {"manifest": os.path.basename(args.manifest)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        manifest = load_json(args.manifest)
        state = load_state(state_root)
        state.update({
            "active_install_manifest": args.manifest.replace("\\", "/"),
            "active_install_id": manifest.get("install_id"),
            "updated_at": now_timestamp(args.deterministic),
        })
        write_state(state_root, state)
        run_launcher_action(log_root or state_root, "installs.select", "COMMIT", "ok",
                            args.deterministic, {"install_id": manifest.get("install_id")})
        report = build_compat_report("update", manifest.get("install_id"), None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "full", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "state_root": state_root}, indent=2))
        return 0

    if args.section == "installs" and args.cmd == "active":
        state_root = resolve_state_root(args)
        state = load_state(state_root)
        report = build_compat_report("load",
                                     state.get("active_install_id"),
                                     None,
                                     None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic,
                                     {"state_root": state_root or ""}, None)
        output = {
            "result": "ok",
            "compat_report": report,
            "active_install_manifest": state.get("active_install_manifest"),
            "active_install_id": state.get("active_install_id"),
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "list":
        instances = list_instance_manifests(args.search, args.install_id)
        report = build_compat_report("load", args.install_id, None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic, {}, None)
        output = {"result": "ok", "compat_report": report, "instances": instances}
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "select":
        state_root = resolve_state_root(args)
        if not state_root:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "state root required for instance selection", {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        if not os.path.isfile(args.manifest):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "instance manifest not found",
                                      {"manifest": os.path.basename(args.manifest)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        manifest = dict(
            validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.manifest).get("instance_manifest")
            or load_json(args.manifest)
        )
        state = load_state(state_root)
        state.update({
            "active_instance_manifest": args.manifest.replace("\\", "/"),
            "active_instance_id": manifest.get("instance_id"),
            "updated_at": now_timestamp(args.deterministic),
        })
        write_state(state_root, state)
        run_launcher_action(log_root or state_root, "instances.select", "COMMIT", "ok",
                            args.deterministic, {"instance_id": manifest.get("instance_id")})
        report = build_compat_report("update", instance_install_id(manifest), manifest.get("instance_id"), None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "full", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "state_root": state_root}, indent=2))
        return 0

    if args.section == "instances" and args.cmd in ("create", "clone", "fork", "activate"):
        ops_cli = resolve_ops_cli()
        extra: List[str] = []
        if args.deterministic:
            extra.append("--deterministic")
        if args.cmd == "create":
            extra += [
                "instances", "create",
                "--install-manifest", args.install_manifest,
                "--data-root", args.data_root,
                "--mode", args.mode,
                "--instance-kind", args.instance_kind,
                "--mod-policy-id", args.mod_policy_id,
                "--overlay-conflict-policy-id", args.overlay_conflict_policy_id,
                "--default-session-template-id", args.default_session_template_id,
                "--seed-policy", args.seed_policy,
                "--ui-mode-default", args.ui_mode_default,
                "--tick-budget-policy-id", args.tick_budget_policy_id,
                "--compute-profile-id", args.compute_profile_id,
            ]
            if args.instance_root:
                extra += ["--instance-root", args.instance_root]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            if args.store_root:
                extra += ["--store-root", args.store_root]
            for profile in args.profile:
                extra += ["--active-profile", profile]
            for modpack in args.modpack:
                extra += ["--active-modpack", modpack]
            for pack_root in args.pack_root:
                extra += ["--pack-root", pack_root]
            for product_build in args.required_product_build:
                extra += ["--required-product-build", product_build]
            for contract_range in args.required_contract_range:
                extra += ["--required-contract-range", contract_range]
            if args.capability_lockfile:
                extra += ["--capability-lockfile", args.capability_lockfile]
            if args.sandbox_policy:
                extra += ["--sandbox-policy", args.sandbox_policy]
            if args.sandbox_policy_ref:
                extra += ["--sandbox-policy-ref", args.sandbox_policy_ref]
            if args.renderer_mode:
                extra += ["--renderer-mode", args.renderer_mode]
            if args.allow_read_only_fallback:
                extra += ["--allow-read-only-fallback"]
            for save_ref in args.save_ref:
                extra += ["--save-ref", save_ref]
            if args.last_opened_save_id:
                extra += ["--last-opened-save-id", args.last_opened_save_id]
            if args.update_channel:
                extra += ["--update-channel", args.update_channel]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        elif args.cmd == "clone":
            extra += [
                "instances", "clone",
                "--source-manifest", args.source_manifest,
                "--data-root", args.data_root,
            ]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        elif args.cmd == "fork":
            extra += [
                "instances", "fork",
                "--source-manifest", args.source_manifest,
                "--data-root", args.data_root,
            ]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        else:
            extra += [
                "instances", "activate",
                "--install-manifest", args.install_manifest,
                "--instance-manifest", args.instance_manifest,
            ]
        rc, payload, _stderr = run_script(ops_cli, extra)
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "instances" and args.cmd == "delete":
        if not args.confirm:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "confirmation required to delete instance",
                                      {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        if not os.path.isfile(args.instance_manifest):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "instance manifest not found",
                                      {"manifest": os.path.basename(args.instance_manifest)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        manifest = dict(
            validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.instance_manifest).get("instance_manifest")
            or load_json(args.instance_manifest)
        )
        instance_root = os.path.dirname(args.instance_manifest)
        data_root = resolve_data_root(instance_root, instance_data_root(manifest))
        os.remove(args.instance_manifest)
        if args.delete_data:
            shutil.rmtree(data_root, ignore_errors=True)
        log_target = log_root or (os.path.dirname(instance_root) if args.delete_data else instance_root)
        run_launcher_action(log_target, "instances.delete", "COMMIT",
                            "ok", args.deterministic,
                            {"instance_id": manifest.get("instance_id")})
        report = build_compat_report("update",
                                     manifest.get("install_id"),
                                     manifest.get("instance_id"),
                                     None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "full", [], [],
                                     args.deterministic, {}, None)
        output = {
            "result": "ok",
            "compat_report": report,
            "data_deleted": bool(args.delete_data),
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "set-profiles":
        if not args.confirm:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "confirmation required to update profiles",
                                      {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        if not os.path.isfile(args.instance_manifest):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "instance manifest not found",
                                      {"manifest": os.path.basename(args.instance_manifest)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        ops_cli = resolve_ops_cli()
        extra: List[str] = []
        if args.deterministic:
            extra.append("--deterministic")
        extra += ["instances", "edit", "--instance-manifest", args.instance_manifest]
        for profile in args.profile:
            extra += ["--profile", profile]
        rc, payload, _stderr = run_script(ops_cli, extra)
        if rc == 0:
            run_launcher_action(log_root or os.path.dirname(args.instance_manifest),
                                "instances.set_profiles", "COMMIT", "ok",
                                args.deterministic,
                                {"instance_manifest": args.instance_manifest.replace("\\", "/")})
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "profiles" and args.cmd == "list":
        profiles = discover_profiles(args.profile_root)
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "profiles": profiles}, indent=2))
        return 0

    if args.section == "list-profiles":
        profiles = discover_profiles(args.profile_root)
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "profiles": profiles}, indent=2))
        return 0

    if args.section == "preflight":
        profiles = discover_profiles([])
        rc, payload = perform_preflight(args, args.install_manifest, args.instance_manifest, profiles)
        run_launcher_action(log_root or os.path.dirname(args.instance_manifest),
                            "preflight", "COMMIT",
                            "ok" if rc == 0 else "refused",
                            args.deterministic,
                            {"run_mode": args.run_mode})
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "run":
        rc, payload = run_with_resolved_manifests(args, args.install_manifest, args.instance_manifest)
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "start":
        state_root = resolve_state_root(args)
        state = load_state(state_root)
        instance_manifest_path = resolve_instance_selection(args, state)
        if not instance_manifest_path:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "instance selection could not be resolved",
                                      {"instance": str(args.instance or "")})
            report = build_compat_report("run", None, None, None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {"state_root": state_root or ""}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        instance_manifest = dict(
            validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=instance_manifest_path).get("instance_manifest")
            or load_json(instance_manifest_path)
        )
        install_manifest_path = resolve_install_selection(
            args,
            state,
            os.path.dirname(instance_manifest_path),
            instance_manifest,
        )
        if not install_manifest_path:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "install selection could not be resolved",
                                      {"instance_manifest": os.path.basename(instance_manifest_path)})
            report = build_compat_report("run", instance_install_id(instance_manifest), instance_manifest.get("instance_id"), None,
                                         args.capability_baseline,
                                         [], [], [],
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {"state_root": state_root or ""}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        rc, payload = run_with_resolved_manifests(args, install_manifest_path, instance_manifest_path)
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "packs" and args.cmd == "list":
        install_root = ""
        instance_root = ""
        data_root = ""
        profile_ids = args.profile or []
        if args.install_manifest and os.path.isfile(args.install_manifest):
            install_manifest = load_json(args.install_manifest)
            install_root = resolve_install_root(args.install_manifest, install_manifest)
        if args.instance_manifest and os.path.isfile(args.instance_manifest):
            instance_manifest = dict(
                validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.instance_manifest).get("instance_manifest")
                or load_json(args.instance_manifest)
            )
            instance_root = os.path.dirname(args.instance_manifest)
            data_root = resolve_data_root(instance_root, instance_data_root(instance_manifest))
            if not profile_ids:
                profile_ids = instance_active_profiles(instance_manifest)
        profiles = discover_profiles([])
        recommended_packs = profile_recommendations(profile_ids, profiles)
        required_packs: List[str] = []
        direct_pack_payloads: Dict[str, str] = {}
        if args.instance_manifest and os.path.isfile(args.instance_manifest):
            manifest = dict(
                validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.instance_manifest).get("instance_manifest")
                or load_json(args.instance_manifest)
            )
            lockfile, _lockfile_source = resolve_pack_lock(instance_root, manifest)
            required_packs = collect_required_packs(lockfile)
            direct_pack_payloads = resolve_pack_payloads(instance_root, manifest, lockfile)
        roots = pack_roots(install_root, data_root, args.pack_root or [])
        required_entries, missing_required = build_pack_status(required_packs, roots,
                                                               direct_pack_payloads,
                                                               install_root, data_root, "required")
        optional_entries, missing_optional = build_pack_status(recommended_packs, roots,
                                                               direct_pack_payloads,
                                                               install_root, data_root, "optional")
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "inspect-only", [], [],
                                     args.deterministic,
                                     {"missing_packs": missing_required,
                                      "optional_missing_packs": missing_optional},
                                     None)
        output = {
            "result": "ok",
            "compat_report": report,
            "packs": required_entries + optional_entries,
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "packs" and args.cmd == "add":
        if not args.confirm:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "confirmation required to add pack", {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        if not os.path.isdir(args.pack_path):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "pack path invalid",
                                      {"pack_path": os.path.basename(args.pack_path)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        pack_id = os.path.basename(args.pack_path.rstrip("/\\"))
        dest_root = os.path.join(args.data_root, "packs", pack_id)
        if os.path.exists(dest_root):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "pack already exists",
                                      {"pack_id": pack_id})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        shutil.copytree(args.pack_path, dest_root)
        run_launcher_action(log_root or args.data_root, "packs.add", "COMMIT",
                            "ok", args.deterministic, {"pack_id": pack_id})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "full", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "pack_id": pack_id}, indent=2))
        return 0

    if args.section == "packs" and args.cmd == "remove":
        if not args.confirm:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "confirmation required to remove pack", {})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        dest_root = os.path.join(args.data_root, "packs", args.pack_id)
        if not os.path.isdir(dest_root):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "pack not present",
                                      {"pack_id": args.pack_id})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        shutil.rmtree(dest_root, ignore_errors=True)
        run_launcher_action(log_root or args.data_root, "packs.remove", "COMMIT",
                            "ok", args.deterministic, {"pack_id": args.pack_id})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "full", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report, "pack_id": args.pack_id}, indent=2))
        return 0

    if args.section == "bundles" and args.cmd == "inspect":
        share_cli = resolve_share_cli()
        rc, payload, _stderr = run_script(share_cli, [
            "inspect",
            "--bundle", args.bundle,
        ] + sum([["--available-pack", p] for p in args.available_pack], []))
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "bundles" and args.cmd in ("import", "import-save", "import-replay", "import-modpack"):
        share_cli = resolve_share_cli()
        inspect_args = ["inspect", "--bundle", args.bundle]
        for pack_id in args.available_pack:
            inspect_args += ["--available-pack", pack_id]
        inspect_rc, inspect_payload, _stderr = run_script(share_cli, inspect_args)
        if not args.confirm:
            output = {
                "result": "ok" if inspect_rc == 0 else "refused",
                "import_state": "confirm_required",
                "compat_report": inspect_payload.get("compat_report") if isinstance(inspect_payload, dict) else None,
                "missing_packs": inspect_payload.get("missing_packs") if isinstance(inspect_payload, dict) else [],
            }
            print(json.dumps(output, indent=2))
            return (3 if inspect_rc != 0 else 0)
        import_args = ["import", "--bundle", args.bundle]
        for pack_id in args.available_pack:
            import_args += ["--available-pack", pack_id]
        if args.require_full:
            import_args.append("--require-full")
        import_args.append("--confirm")
        if args.out:
            import_args += ["--out", args.out]
        if args.instance_id:
            import_args += ["--instance-id", args.instance_id]
        if args.import_mode:
            import_args += ["--import-mode", args.import_mode]
        if args.store_root:
            import_args += ["--store-root", args.store_root]
        rc, payload, _stderr = run_script(share_cli, import_args)
        run_launcher_action(log_root or os.path.dirname(args.bundle),
                            "bundles.import", "COMMIT",
                            "ok" if rc == 0 else "refused",
                            args.deterministic, {"bundle": os.path.basename(args.bundle)})
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "bundles" and args.cmd == "export-instance":
        share_cli = resolve_share_cli()
        if not os.path.isfile(args.instance_manifest):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "instance manifest not found",
                                      {"manifest": os.path.basename(args.instance_manifest)})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        export_args = [
            "export",
            "--bundle-type", args.bundle_type,
            "--artifact", args.instance_manifest,
            "--out", args.out,
        ]
        rc, payload, _stderr = run_script(share_cli, export_args)
        run_launcher_action(log_root or os.path.dirname(args.out),
                            "bundles.export_instance", "COMMIT",
                            "ok" if rc == 0 else "refused",
                            args.deterministic, {"bundle_type": args.bundle_type})
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "bundles" and args.cmd == "export":
        share_cli = resolve_share_cli()
        export_args = [
            "export",
            "--bundle-type", args.bundle_type,
            "--artifact", args.artifact,
            "--out", args.out,
        ]
        if args.lockfile:
            export_args += ["--lockfile", args.lockfile]
        if args.compat_report:
            export_args += ["--compat-report", args.compat_report]
        if args.instance_metadata:
            export_args += ["--instance-metadata", args.instance_metadata]
        if args.runtime_metadata:
            export_args += ["--runtime-metadata", args.runtime_metadata]
        for ref in args.reference:
            export_args += ["--reference", ref]
        for pack_ref in args.pack_ref:
            export_args += ["--pack-ref", pack_ref]
        for pack_path in args.embed_pack:
            export_args += ["--embed-pack", pack_path]
        if args.bundle_id:
            export_args += ["--bundle-id", args.bundle_id]
        if args.bundle_format_version is not None:
            export_args += ["--bundle-format-version", str(args.bundle_format_version)]
        for tag in args.bundle_tag:
            export_args += ["--bundle-tag", tag]
        if args.created_at:
            export_args += ["--created-at", args.created_at]
        if args.created_by:
            export_args += ["--created-by", args.created_by]
        if args.tool_version:
            export_args += ["--tool-version", args.tool_version]
        if args.trust_tier:
            export_args += ["--trust-tier", args.trust_tier]
        rc, payload, _stderr = run_script(share_cli, export_args)
        run_launcher_action(log_root or os.path.dirname(args.out),
                            "bundles.export", "COMMIT",
                            "ok" if rc == 0 else "refused",
                            args.deterministic, {"bundle_type": args.bundle_type})
        print(json.dumps(payload, indent=2))
        return rc

    if args.section == "paths":
        data_root = args.data_root
        if not data_root and args.instance_manifest and os.path.isfile(args.instance_manifest):
            manifest = dict(
                validate_instance_manifest(repo_root=REPO_ROOT, instance_manifest_path=args.instance_manifest).get("instance_manifest")
                or load_json(args.instance_manifest)
            )
            instance_root = os.path.dirname(args.instance_manifest)
            data_root = resolve_data_root(instance_root, instance_data_root(manifest))
        if not data_root:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "data root required", {})
            report = build_compat_report("load", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        output = {
            "result": "ok",
            "paths": {
                "instance_data_path": data_root.replace("\\", "/"),
                "logs_path": os.path.join(data_root, "logs").replace("\\", "/"),
                "replays_path": os.path.join(data_root, "replays").replace("\\", "/"),
                "bugreports_path": os.path.join(data_root, "bugreports").replace("\\", "/"),
            }
        }
        print(json.dumps(output, indent=2))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "launcher cli failed",
                                  {"error": "unexpected"})
        report = build_compat_report("load", None, None, None,
                                     DEFAULT_CAPABILITY_BASELINE,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     True, {}, refusal)
        print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
        raise SystemExit(3)
