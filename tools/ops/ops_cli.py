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
    provided_caps = capabilities_from_manifest(install_manifest)

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
    source_manifest = load_json(args.source_manifest)
    source_root = os.path.dirname(args.source_manifest)
    install_id = source_manifest.get("install_id")
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

    instance_id = args.instance_id or str(uuid.uuid4())
    target_root = args.data_root
    deterministic = args.deterministic
    tx_id = args.transaction_id or str(uuid.uuid4())
    sandbox = load_sandbox_policy(args.sandbox_policy) if args.sandbox_policy else {}

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


def activate_instance(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    install_manifest = load_json(args.install_manifest)
    install_root = install_manifest.get("install_root") or os.path.dirname(args.install_manifest)
    instance_manifest = load_json(args.instance_manifest)
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
