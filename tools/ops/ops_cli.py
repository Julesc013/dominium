import argparse
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Tuple


DEFAULT_INSTALL_MANIFEST = "install.manifest.json"
DEFAULT_INSTANCE_MANIFEST = "instance.manifest.json"
DEFAULT_ACTIVE_INSTANCE = "active.instance.json"


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


def refusal_payload(code_id: int, code: str, message: str,
                    details: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


def compat_report(result: str, message: str = "",
                  refusal: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    payload = {
        "result": result,
        "message": message,
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
                "install_root": manifest.get("install_root"),
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
                        "install_root": manifest.get("install_root"),
                        "manifest_path": manifest_path.replace("\\", "/"),
                    })
    return results


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
                manifest = load_json(manifest_path)
            except (OSError, ValueError):
                continue
            if install_id and manifest.get("install_id") != install_id:
                continue
            results.append({
                "instance_id": manifest.get("instance_id"),
                "install_id": manifest.get("install_id"),
                "data_root": manifest.get("data_root"),
                "manifest_path": manifest_path.replace("\\", "/"),
            })
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
                    results.append({
                        "instance_id": manifest.get("instance_id"),
                        "install_id": manifest.get("install_id"),
                        "data_root": manifest.get("data_root"),
                        "manifest_path": manifest_path.replace("\\", "/"),
                    })
    return results


def resolve_data_root(instance_root: str, data_root: str) -> str:
    if not data_root:
        return instance_root
    if os.path.isabs(data_root):
        return data_root
    return os.path.join(instance_root, data_root)


def create_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    install_manifest = load_json(args.install_manifest)
    install_id = install_manifest.get("install_id")
    instance_id = args.instance_id or str(uuid.uuid4())
    data_root = args.data_root
    instance_root = args.data_root
    if args.instance_root:
        instance_root = args.instance_root
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}

    if not install_id:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "install manifest missing install_id",
                                  {"manifest": os.path.basename(args.install_manifest)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    if not sandbox_allows(sandbox, instance_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies instance root",
                                  {"path": os.path.basename(instance_root)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    ensure_dir(instance_root)
    begin_transaction(instance_root, "instances.create", tx_id, deterministic)
    stage_transaction(instance_root, "instances.create", tx_id, deterministic)

    manifest_path = os.path.join(instance_root, DEFAULT_INSTANCE_MANIFEST)
    if os.path.exists(manifest_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "instance manifest already exists",
                                  {"manifest": DEFAULT_INSTANCE_MANIFEST})
        rollback_transaction(instance_root, "instances.create", tx_id, refusal, deterministic)
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    payload = {
        "instance_id": instance_id,
        "install_id": install_id,
        "data_root": data_root or ".",
        "active_profiles": args.active_profiles or [],
        "active_modpacks": args.active_modpacks or [],
        "capability_lockfile": args.capability_lockfile or "lockfiles/capabilities.lock",
        "sandbox_policy_ref": args.sandbox_policy_ref or "sandbox.default",
        "update_channel": args.update_channel,
        "created_at": args.created_at or now_timestamp(deterministic),
        "last_used_at": args.created_at or now_timestamp(deterministic),
        "extensions": {},
    }
    tmp_path = manifest_path + ".tmp"
    write_json(tmp_path, payload)

    if args.simulate_failure == "stage":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "simulated stage failure", {})
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        rollback_transaction(instance_root, "instances.create", tx_id, refusal, deterministic)
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    os.replace(tmp_path, manifest_path)
    commit_transaction(instance_root, "instances.create", tx_id, deterministic)
    return 0, {
        "result": "ok",
        "compat_report": compat_report("ok"),
        "instance_manifest": manifest_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def clone_instance(args: argparse.Namespace, fork_only: bool) -> Tuple[int, Dict[str, object]]:
    source_manifest = load_json(args.source_manifest)
    source_root = os.path.dirname(args.source_manifest)
    install_id = source_manifest.get("install_id")
    if not install_id:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "source instance missing install_id",
                                  {"manifest": os.path.basename(args.source_manifest)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    instance_id = args.instance_id or str(uuid.uuid4())
    target_root = args.data_root
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}

    if not sandbox_allows(sandbox, target_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies instance root",
                                  {"path": os.path.basename(target_root)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    if os.path.exists(target_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "target instance root already exists",
                                  {"path": os.path.basename(target_root)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    ensure_dir(target_root)
    begin_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)
    stage_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)

    if not fork_only:
        shutil.copytree(source_root, target_root, dirs_exist_ok=True)
    else:
        ensure_dir(target_root)

    manifest_path = os.path.join(target_root, DEFAULT_INSTANCE_MANIFEST)
    payload = dict(source_manifest)
    payload["instance_id"] = instance_id
    payload["data_root"] = payload.get("data_root", ".")
    payload["created_at"] = args.created_at or now_timestamp(deterministic)
    payload["last_used_at"] = args.created_at or now_timestamp(deterministic)
    write_json(manifest_path, payload)

    if args.simulate_failure == "commit":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "simulated commit failure", {})
        shutil.rmtree(target_root, ignore_errors=True)
        rollback_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, refusal, deterministic)
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

    commit_transaction(target_root, "instances.fork" if fork_only else "instances.clone", tx_id, deterministic)
    return 0, {
        "result": "ok",
        "compat_report": compat_report("ok"),
        "instance_manifest": manifest_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def activate_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    install_manifest = load_json(args.install_manifest)
    install_root = install_manifest.get("install_root") or os.path.dirname(args.install_manifest)
    instance_manifest = load_json(args.instance_manifest)
    instance_id = instance_manifest.get("instance_id")
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}

    if not sandbox_allows(sandbox, install_root):
        refusal = refusal_payload(2, "REFUSE_LAW_FORBIDDEN",
                                  "sandbox denies install root",
                                  {"path": os.path.basename(install_root)})
        return 3, {"result": "refused", "compat_report": compat_report("refused", refusal=refusal)}

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
    return 0, {
        "result": "ok",
        "compat_report": compat_report("ok"),
        "active_instance": active_path.replace("\\", "/"),
        "transaction_id": tx_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ops CLI (install/instance management)")
    parser.add_argument("--format", default="json", choices=["json", "text"])
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--transaction-id", default=None)
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
    instances_create.add_argument("--active-profile", action="append", default=[])
    instances_create.add_argument("--active-modpack", action="append", default=[])
    instances_create.add_argument("--capability-lockfile", default=None)
    instances_create.add_argument("--sandbox-policy", default=None)
    instances_create.add_argument("--sandbox-policy-ref", default=None)
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

    instances_activate = instances_sub.add_parser("activate")
    instances_activate.add_argument("--install-manifest", required=True)
    instances_activate.add_argument("--instance-manifest", required=True)
    instances_activate.add_argument("--sandbox-policy", default=None)

    args = parser.parse_args()

    if args.section == "installs" and args.cmd == "list":
        installs = list_install_manifests(args.search)
        output = {
            "result": "ok",
            "compat_report": compat_report("ok"),
            "installs": installs,
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.section == "instances" and args.cmd == "list":
        instances = list_instance_manifests(args.search, args.install_id)
        output = {
            "result": "ok",
            "compat_report": compat_report("ok"),
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

    if args.section == "instances" and args.cmd == "activate":
        code, output = activate_instance(args)
        print(json.dumps(output, indent=2))
        return code

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
