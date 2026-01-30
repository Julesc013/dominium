import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


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


def sorted_unique(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    return sorted({value for value in values if value})


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
    return results


def normalize_install_entry(manifest: dict, manifest_path: str) -> Dict[str, object]:
    binaries = manifest.get("binaries") or {}
    engine = binaries.get("engine") or {}
    game = binaries.get("game") or {}
    build_number = game.get("build_number")
    if build_number is None:
        build_number = engine.get("build_number")
    if build_number is None:
        build_number = manifest.get("build_identity")
    return {
        "install_id": manifest.get("install_id"),
        "install_root": manifest.get("install_root") or os.path.dirname(manifest_path),
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
                manifest = load_json(manifest_path)
            except (OSError, ValueError):
                continue
            if install_id and manifest.get("install_id") != install_id:
                continue
            results.append(normalize_instance_entry(manifest, manifest_path))
            continue
        if os.path.isdir(root):
            for dirpath, _dirnames, filenames in os.walk(root):
                if DEFAULT_INSTANCE_MANIFEST in filenames:
                    manifest_path = os.path.join(dirpath, DEFAULT_INSTANCE_MANIFEST)
                    try:
                        manifest = load_json(manifest_path)
                    except (OSError, ValueError):
                        continue
                    if install_id and manifest.get("install_id") != install_id:
                        continue
                    results.append(normalize_instance_entry(manifest, manifest_path))
    return results


def normalize_instance_entry(manifest: dict, manifest_path: str) -> Dict[str, object]:
    return {
        "instance_id": manifest.get("instance_id"),
        "install_id": manifest.get("install_id"),
        "data_root": manifest.get("data_root"),
        "active_profiles": manifest.get("active_profiles") or [],
        "active_modpacks": manifest.get("active_modpacks") or [],
        "manifest_path": manifest_path.replace("\\", "/"),
        "update_channel": manifest.get("update_channel"),
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
        path = os.path.join(root, pack_id)
        if os.path.isdir(path):
            return root
    return None


def pack_source_for_root(root: str, install_root: str, data_root: str) -> str:
    if install_root and normalize_path(root).startswith(normalize_path(install_root)):
        return "bundled"
    if data_root and normalize_path(root).startswith(normalize_path(data_root)):
        return "local"
    return "local"


def build_pack_status(pack_ids: List[str],
                      roots: List[str],
                      install_root: str,
                      data_root: str,
                      status_label: str) -> Tuple[List[Dict[str, object]], List[str]]:
    entries: List[Dict[str, object]] = []
    missing: List[str] = []
    for pack_id in sorted_unique(pack_ids):
        location = pack_location(pack_id, roots)
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
    if not os.path.isfile(install_manifest_path):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "install manifest not found",
                                  {"manifest": os.path.basename(install_manifest_path)})
        report = build_compat_report("run", None, None, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}
    if not os.path.isfile(instance_manifest_path):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance manifest not found",
                                  {"manifest": os.path.basename(instance_manifest_path)})
        report = build_compat_report("run", None, None, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    install_manifest = load_json(install_manifest_path)
    instance_manifest = load_json(instance_manifest_path)
    install_id = install_manifest.get("install_id")
    instance_id = instance_manifest.get("instance_id")
    if install_id and instance_manifest.get("install_id") not in (None, install_id):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance does not match install",
                                  {"install_id": install_id, "instance_id": instance_id or ""})
        report = build_compat_report("run", install_id, instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    install_root = install_manifest.get("install_root") or os.path.dirname(install_manifest_path)
    instance_root = os.path.dirname(instance_manifest_path)
    data_root = resolve_data_root(instance_root, instance_manifest.get("data_root") or "")
    lockfile_path = resolve_lockfile(instance_root, instance_manifest.get("capability_lockfile") or "")
    lockfile = load_lockfile(lockfile_path)

    if not lockfile:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "capability lockfile missing",
                                  {"lockfile": os.path.basename(lockfile_path or "capability.lock")})
        report = build_compat_report("run", install_id, instance_id, None, args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], ["regenerate lockfile"],
                                     deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    required_caps = collect_required_capabilities(lockfile)
    provided_caps = sorted_unique(install_manifest.get("supported_capabilities") or [])
    missing_caps = sorted(set(required_caps) - set(provided_caps))

    profile_ids = args.profile or (instance_manifest.get("active_profiles") or [])
    recommended_packs = profile_recommendations(profile_ids, profiles)
    required_packs = collect_required_packs(lockfile)
    roots = pack_roots(install_root, data_root, args.pack_root or [])

    required_entries, missing_required = build_pack_status(required_packs, roots,
                                                           install_root, data_root, "required")
    optional_entries, missing_optional = build_pack_status(recommended_packs, roots,
                                                           install_root, data_root, "optional")

    extensions = {
        "run_mode": args.run_mode,
        "required_packs": required_packs,
        "missing_packs": missing_required,
        "optional_packs": recommended_packs,
        "optional_missing_packs": missing_optional,
        "pack_status": required_entries + optional_entries,
    }

    refusal_codes: List[str] = []
    mitigation: List[str] = []
    refusal = None
    mode = "full"

    if missing_caps:
        mode = "refuse"
        refusal_codes = ["REFUSE_CAPABILITY_MISSING"]
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "required capabilities missing",
                                  {"missing": missing_caps})
        mitigation = ["update install capabilities"]
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
        mitigation = ["install missing packs"] if missing_required else []

    if args.run_mode in ("inspect", "replay") and mode != "refuse":
        mode = "inspect-only"

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

    instances_create = instances_sub.add_parser("create")
    instances_create.add_argument("--install-manifest", required=True)
    instances_create.add_argument("--data-root", required=True)
    instances_create.add_argument("--instance-root", default=None)
    instances_create.add_argument("--instance-id", default=None)
    instances_create.add_argument("--profile", action="append", default=[])
    instances_create.add_argument("--modpack", action="append", default=[])
    instances_create.add_argument("--capability-lockfile", default=None)
    instances_create.add_argument("--sandbox-policy", default=None)
    instances_create.add_argument("--sandbox-policy-ref", default=None)
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
    preflight.add_argument("--run-mode", default="play",
                           choices=["play", "client", "server", "inspect", "replay"])

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("--install-manifest", required=True)
    run_cmd.add_argument("--instance-manifest", required=True)
    run_cmd.add_argument("--profile", action="append", default=[])
    run_cmd.add_argument("--pack-root", action="append", default=[])
    run_cmd.add_argument("--compat-out", default=None)
    run_cmd.add_argument("--run-mode", default="play",
                         choices=["play", "client", "server", "inspect", "replay"])
    run_cmd.add_argument("--confirm", action="store_true")

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
    bundles_import_save = bundles_sub.add_parser("import-save")
    bundles_import_save.add_argument("--bundle", required=True)
    bundles_import_save.add_argument("--available-pack", action="append", default=[])
    bundles_import_save.add_argument("--require-full", action="store_true")
    bundles_import_save.add_argument("--confirm", action="store_true")
    bundles_import_save.add_argument("--out", default=None)
    bundles_import_replay = bundles_sub.add_parser("import-replay")
    bundles_import_replay.add_argument("--bundle", required=True)
    bundles_import_replay.add_argument("--available-pack", action="append", default=[])
    bundles_import_replay.add_argument("--require-full", action="store_true")
    bundles_import_replay.add_argument("--confirm", action="store_true")
    bundles_import_replay.add_argument("--out", default=None)
    bundles_import_modpack = bundles_sub.add_parser("import-modpack")
    bundles_import_modpack.add_argument("--bundle", required=True)
    bundles_import_modpack.add_argument("--available-pack", action="append", default=[])
    bundles_import_modpack.add_argument("--require-full", action="store_true")
    bundles_import_modpack.add_argument("--confirm", action="store_true")
    bundles_import_modpack.add_argument("--out", default=None)

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
    bundles_export_instance.add_argument("--bundle-type", default="modpack")
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

    if args.section == "instances" and args.cmd in ("create", "clone", "fork", "activate"):
        ops_cli = resolve_ops_cli()
        if args.cmd == "create":
            extra = [
                "instances", "create",
                "--install-manifest", args.install_manifest,
                "--data-root", args.data_root,
            ]
            if args.instance_root:
                extra += ["--instance-root", args.instance_root]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            for profile in args.profile:
                extra += ["--active-profile", profile]
            for modpack in args.modpack:
                extra += ["--active-modpack", modpack]
            if args.capability_lockfile:
                extra += ["--capability-lockfile", args.capability_lockfile]
            if args.sandbox_policy:
                extra += ["--sandbox-policy", args.sandbox_policy]
            if args.sandbox_policy_ref:
                extra += ["--sandbox-policy-ref", args.sandbox_policy_ref]
            if args.update_channel:
                extra += ["--update-channel", args.update_channel]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        elif args.cmd == "clone":
            extra = [
                "instances", "clone",
                "--source-manifest", args.source_manifest,
                "--data-root", args.data_root,
            ]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        elif args.cmd == "fork":
            extra = [
                "instances", "fork",
                "--source-manifest", args.source_manifest,
                "--data-root", args.data_root,
            ]
            if args.instance_id:
                extra += ["--instance-id", args.instance_id]
            if args.created_at:
                extra += ["--created-at", args.created_at]
        else:
            extra = [
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
        manifest = load_json(args.instance_manifest)
        instance_root = os.path.dirname(args.instance_manifest)
        data_root = resolve_data_root(instance_root, manifest.get("data_root") or "")
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
        manifest = load_json(args.instance_manifest)
        manifest["active_profiles"] = sorted_unique(args.profile)
        write_json(args.instance_manifest, manifest)
        run_launcher_action(log_root or os.path.dirname(args.instance_manifest),
                            "instances.set_profiles", "COMMIT", "ok",
                            args.deterministic,
                            {"instance_id": manifest.get("instance_id")})
        report = build_compat_report("update",
                                     manifest.get("install_id"),
                                     manifest.get("instance_id"),
                                     None,
                                     args.capability_baseline,
                                     [], [], [],
                                     "full", [], [],
                                     args.deterministic, {}, None)
        print(json.dumps({"result": "ok", "compat_report": report}, indent=2))
        return 0

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
        profiles = discover_profiles([])
        rc, payload = perform_preflight(args, args.install_manifest, args.instance_manifest, profiles)
        report = payload.get("compat_report") if isinstance(payload, dict) else None
        if rc != 0:
            print(json.dumps(payload, indent=2))
            return rc
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
            print(json.dumps({"result": "refused", "compat_report": report}, indent=2))
            return 3
        run_launcher_action(log_root or os.path.dirname(args.instance_manifest),
                            "run", "COMMIT", "ok", args.deterministic,
                            {"run_mode": args.run_mode})
        payload["run_mode"] = args.run_mode
        print(json.dumps(payload, indent=2))
        return 0

    if args.section == "packs" and args.cmd == "list":
        install_root = ""
        instance_root = ""
        data_root = ""
        profile_ids = args.profile or []
        if args.install_manifest and os.path.isfile(args.install_manifest):
            install_manifest = load_json(args.install_manifest)
            install_root = install_manifest.get("install_root") or os.path.dirname(args.install_manifest)
        if args.instance_manifest and os.path.isfile(args.instance_manifest):
            instance_manifest = load_json(args.instance_manifest)
            instance_root = os.path.dirname(args.instance_manifest)
            data_root = resolve_data_root(instance_root, instance_manifest.get("data_root") or "")
            if not profile_ids:
                profile_ids = instance_manifest.get("active_profiles") or []
        profiles = discover_profiles([])
        recommended_packs = profile_recommendations(profile_ids, profiles)
        required_packs: List[str] = []
        if args.instance_manifest and os.path.isfile(args.instance_manifest):
            lockfile_path = resolve_lockfile(instance_root,
                                             load_json(args.instance_manifest).get("capability_lockfile") or "")
            lockfile = load_lockfile(lockfile_path)
            required_packs = collect_required_packs(lockfile)
        roots = pack_roots(install_root, data_root, args.pack_root or [])
        required_entries, missing_required = build_pack_status(required_packs, roots,
                                                               install_root, data_root, "required")
        optional_entries, missing_optional = build_pack_status(recommended_packs, roots,
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
        instance_manifest = load_json(args.instance_manifest)
        instance_root = os.path.dirname(args.instance_manifest)
        lockfile_path = resolve_lockfile(instance_root,
                                         instance_manifest.get("capability_lockfile") or "")
        if not lockfile_path or not os.path.isfile(lockfile_path):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "capability lockfile missing",
                                      {"lockfile": os.path.basename(lockfile_path or "capability.lock")})
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
            "--lockfile", lockfile_path,
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
            manifest = load_json(args.instance_manifest)
            instance_root = os.path.dirname(args.instance_manifest)
            data_root = resolve_data_root(instance_root, manifest.get("data_root") or "")
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
