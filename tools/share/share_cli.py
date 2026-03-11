import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.lib.content_store import (
    ARTIFACT_MANIFEST,
    JSON_PAYLOAD,
    artifact_payload_path,
    build_store_locator,
    copy_dir as copy_tree,
    deterministic_fingerprint,
    index_file_tree,
    initialize_store_root,
    load_artifact_manifest,
    load_instance_artifact_manifest,
    load_instance_json_artifact,
    load_json as load_cas_json,
    pretty_write_json,
    resolve_instance_artifact_root,
    resolve_locator_path,
    store_add_artifact,
    store_add_tree_artifact,
)


BUNDLE_CONTAINER_NAME = "bundle.container.json"
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


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_dir(path: str) -> str:
    h = hashlib.sha256()
    for root, _dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, path).replace("\\", "/")
        for name in sorted(files):
            rel_path = (rel_root + "/" + name) if rel_root != "." else name
            h.update(rel_path.encode("utf-8"))
            with open(os.path.join(root, name), "rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    h.update(chunk)
    return h.hexdigest()


def sorted_unique(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    return sorted({value for value in values if value})


def refusal_payload(code_id: int, code: str, message: str, details: Optional[Dict[str, object]] = None) -> Dict[str, object]:
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


def parse_pack_ref(text: str) -> Dict[str, str]:
    if "@" in text:
        pack_id, version = text.split("@", 1)
        return {"pack_id": pack_id, "version_constraint": version}
    return {"pack_id": text}


def read_pack_manifest(pack_root: str) -> Tuple[str, str]:
    manifest = os.path.join(pack_root, "pack.toml")
    pack_id = os.path.basename(pack_root)
    pack_version = "unknown"
    if not os.path.isfile(manifest):
        return pack_id, pack_version
    try:
        with open(manifest, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if "pack_id" in line and "=" in line:
                    pack_id = line.split("=", 1)[1].strip().strip("\"'")
                if "pack_version" in line and "=" in line:
                    pack_version = line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return pack_id, pack_version


def copy_file(src: str, dest: str) -> None:
    ensure_dir(os.path.dirname(dest))
    shutil.copy2(src, dest)


def copy_dir(src: str, dest: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def content_entry(path: str, kind: str, source_path: Optional[str] = None) -> Dict[str, object]:
    actual_path = source_path or path
    size = os.path.getsize(actual_path)
    return {
        "content_path": path.replace("\\", "/"),
        "content_kind": kind,
        "sha256": sha256_file(actual_path),
        "size_bytes": size,
    }


def append_untracked_entries(bundle_root: str, contents: List[Dict[str, object]]) -> List[Dict[str, object]]:
    tracked = {str(entry.get("content_path", "")).replace("\\", "/") for entry in contents}
    merged = list(contents)
    for entry in index_file_tree(bundle_root, ignore_rel_paths=[BUNDLE_CONTAINER_NAME]):
        content_path = str(entry.get("content_path", "")).replace("\\", "/")
        if content_path in tracked:
            continue
        merged.append(entry)
    return sorted(merged, key=lambda item: item["content_path"])


def build_embedded_ref(category: str, artifact_hash: str, artifact_type: str, artifact_path: str, artifact_id: str = "") -> Dict[str, object]:
    payload = {
        "category": category,
        "artifact_hash": artifact_hash,
        "artifact_type": artifact_type,
        "artifact_path": artifact_path.replace("\\", "/"),
    }
    if artifact_id:
        payload["artifact_id"] = artifact_id
    return payload


def copy_instance_artifact(instance_root: str,
                           instance_manifest: Dict[str, object],
                           category: str,
                           artifact_hash: str,
                           dest_root: str) -> Tuple[str, Dict[str, object]]:
    artifact_root = resolve_instance_artifact_root(instance_root, instance_manifest, category, artifact_hash)
    manifest = load_artifact_manifest(artifact_root)
    if not manifest:
        return "", {}
    copy_tree(artifact_root, dest_root)
    return artifact_root, manifest


def export_instance_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    if os.path.exists(args.out):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "bundle output already exists",
                                  {"path": os.path.basename(args.out)})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if not os.path.isfile(args.artifact):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "artifact is required",
                                  {"artifact": args.artifact or ""})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    instance_manifest = load_json(args.artifact)
    instance_root = os.path.dirname(os.path.abspath(args.artifact))
    pack_lock_hash = str(instance_manifest.get("pack_lock_hash", "")).strip()
    profile_bundle_hash = str(instance_manifest.get("profile_bundle_hash", "")).strip()
    if not pack_lock_hash or not profile_bundle_hash:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "instance manifest is missing CAS artifact hashes",
                                  {"manifest": os.path.basename(args.artifact)})
        report = build_compat_report("update",
                                     instance_manifest.get("install_id"),
                                     instance_manifest.get("instance_id"),
                                     None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    pack_lock_payload = load_instance_json_artifact(instance_root, instance_manifest, "locks", pack_lock_hash)
    profile_bundle_payload = load_instance_json_artifact(instance_root, instance_manifest, "profiles", profile_bundle_hash)
    if not pack_lock_payload or not profile_bundle_payload:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "instance CAS artifacts are missing",
                                  {"instance_id": instance_manifest.get("instance_id") or ""})
        report = build_compat_report("update",
                                     instance_manifest.get("install_id"),
                                     instance_manifest.get("instance_id"),
                                     None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    ordered_pack_ids = sorted_unique(list(pack_lock_payload.get("ordered_pack_ids") or []))
    pack_hashes = dict(pack_lock_payload.get("pack_hashes") or {})
    missing_pack_hashes = [pack_id for pack_id in ordered_pack_ids if pack_id not in pack_hashes]
    if missing_pack_hashes:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "portable export requires pinned pack hashes",
                                  {"missing_pack_hashes": missing_pack_hashes})
        report = build_compat_report("update",
                                     instance_manifest.get("install_id"),
                                     instance_manifest.get("instance_id"),
                                     None,
                                     args.capability_baseline,
                                     [], [], missing_pack_hashes, "refuse",
                                     [refusal.get("code")], ["materialize pack artifacts before export"],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    ensure_dir(args.out)
    bundle_instance_root = os.path.join(args.out, "instance")
    ensure_dir(bundle_instance_root)

    embedded_refs: List[Dict[str, object]] = []
    embedded_packs: List[Dict[str, object]] = []

    for category, artifact_hash, artifact_type, artifact_id in (
        ("locks", pack_lock_hash, "json", str(pack_lock_payload.get("pack_lock_id", ""))),
        ("profiles", profile_bundle_hash, "json", str(profile_bundle_payload.get("profile_bundle_id", ""))),
    ):
        dest_root = os.path.join(bundle_instance_root, "embedded_artifacts", category, artifact_hash)
        _source_root, manifest = copy_instance_artifact(instance_root, instance_manifest, category, artifact_hash, dest_root)
        if not manifest:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "instance artifact missing during export",
                                      {"category": category, "artifact_hash": artifact_hash})
            shutil.rmtree(args.out, ignore_errors=True)
            report = build_compat_report("update",
                                         instance_manifest.get("install_id"),
                                         instance_manifest.get("instance_id"),
                                         None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {"bundle_type": "instance"}, refusal)
            return 3, {"result": "refused", "compat_report": report}
        embedded_refs.append(
            build_embedded_ref(category, artifact_hash, artifact_type,
                               os.path.relpath(dest_root, bundle_instance_root), artifact_id)
        )

    for pack_id in ordered_pack_ids:
        artifact_hash = str(pack_hashes.get(pack_id, "")).strip()
        dest_root = os.path.join(bundle_instance_root, "embedded_artifacts", "packs", artifact_hash)
        source_root, manifest = copy_instance_artifact(instance_root, instance_manifest, "packs", artifact_hash, dest_root)
        if not manifest:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "pack artifact missing during export",
                                      {"pack_id": pack_id, "artifact_hash": artifact_hash})
            shutil.rmtree(args.out, ignore_errors=True)
            report = build_compat_report("update",
                                         instance_manifest.get("install_id"),
                                         instance_manifest.get("instance_id"),
                                         None,
                                         args.capability_baseline,
                                         [], [], [pack_id], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {"bundle_type": "instance"}, refusal)
            return 3, {"result": "refused", "compat_report": report}
        payload_root = artifact_payload_path(dest_root, "tree")
        embedded_refs.append(
            build_embedded_ref("packs", artifact_hash, "tree",
                               os.path.relpath(dest_root, bundle_instance_root), pack_id)
        )
        embedded_packs.append({
            "pack_id": pack_id,
            "pack_version": "unknown",
            "pack_path": os.path.relpath(payload_root, args.out).replace("\\", "/"),
            "pack_hash": artifact_hash,
            "pack_size_bytes": sum(
                os.path.getsize(os.path.join(root, name))
                for root, _dirs, files in os.walk(payload_root)
                for name in files
            ),
        })

    portable_manifest = dict(instance_manifest)
    portable_manifest["mode"] = "portable"
    portable_manifest["store_root"] = {}
    portable_manifest["embedded_artifacts"] = embedded_refs
    portable_manifest["capability_lockfile"] = "lockfiles/capabilities.lock"
    portable_manifest["deterministic_fingerprint"] = ""
    portable_manifest["deterministic_fingerprint"] = deterministic_fingerprint(portable_manifest)

    manifest_dest = os.path.join(bundle_instance_root, "instance.manifest.json")
    pretty_write_json(manifest_dest, portable_manifest)

    lockfile_dest = os.path.join(bundle_instance_root, "lockfiles", "capabilities.lock")
    pretty_write_json(lockfile_dest, pack_lock_payload)

    compat_dest = os.path.join(args.out, "compat", "compat_report.json")
    compat_payload = build_compat_report(
        context="export",
        install_id=portable_manifest.get("install_id"),
        instance_id=portable_manifest.get("instance_id"),
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=[],
        missing_capabilities=[],
        compatibility_mode="full",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=args.deterministic,
        extensions={"bundle_type": "instance"},
        refusal=None,
    )
    pretty_write_json(compat_dest, compat_payload)

    contents = append_untracked_entries(args.out, [
        content_entry(os.path.relpath(manifest_dest, args.out), "instance", manifest_dest),
        content_entry(os.path.relpath(lockfile_dest, args.out), "lockfile", lockfile_dest),
        content_entry(os.path.relpath(compat_dest, args.out), "compat_report", compat_dest),
    ])
    bundle_container = {
        "bundle_type": "instance",
        "bundle_id": args.bundle_id or str(uuid.uuid4()),
        "created_at": args.created_at or now_timestamp(args.deterministic),
        "created_by": args.created_by or "unknown",
        "tool_version": args.tool_version or "unknown",
        "contents_index": contents,
        "lockfile_ref": os.path.relpath(lockfile_dest, args.out).replace("\\", "/"),
        "compat_report_ref": os.path.relpath(compat_dest, args.out).replace("\\", "/"),
        "embedded_packs": embedded_packs,
        "pack_refs": [parse_pack_ref(pack_id) for pack_id in ordered_pack_ids],
        "extensions": {},
    }
    if args.trust_tier:
        bundle_container["trust_tier"] = args.trust_tier
    if args.bundle_format_version is not None:
        bundle_container["bundle_format_version"] = args.bundle_format_version
    if args.bundle_tag:
        bundle_container["bundle_tags"] = sorted_unique(args.bundle_tag)
    write_json(os.path.join(args.out, BUNDLE_CONTAINER_NAME), bundle_container)
    report = build_compat_report("export",
                                 portable_manifest.get("install_id"),
                                 portable_manifest.get("instance_id"),
                                 args.runtime_id,
                                 args.capability_baseline,
                                 [], [], [], "full", [], [],
                                 args.deterministic,
                                 {"bundle_type": "instance", "bundle_id": bundle_container["bundle_id"]},
                                 None)
    return 0, {"result": "ok", "compat_report": report, "bundle_root": args.out.replace("\\", "/")}


def import_instance_bundle(args: argparse.Namespace, container: dict) -> Tuple[int, Dict[str, object]]:
    if not args.out:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance bundle import requires --out",
                                  {"bundle_type": "instance"})
        report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if os.path.exists(args.out):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "import destination exists",
                                  {"path": os.path.basename(args.out)})
        report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    bundle_instance_root = os.path.join(args.bundle, "instance")
    manifest_path = os.path.join(bundle_instance_root, "instance.manifest.json")
    if not os.path.isfile(manifest_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "instance bundle payload missing",
                                  {"bundle_type": "instance"})
        report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    manifest = load_json(manifest_path)
    import_mode = str(args.import_mode or manifest.get("mode") or "portable").strip().lower()
    if import_mode not in ("linked", "portable"):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "instance import mode is invalid",
                                  {"import_mode": import_mode})
        report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if import_mode == "portable":
        copy_tree(bundle_instance_root, args.out)
        imported_manifest_path = os.path.join(args.out, "instance.manifest.json")
        imported_manifest = load_json(imported_manifest_path)
        if args.instance_id:
            imported_manifest["instance_id"] = args.instance_id
            imported_manifest["deterministic_fingerprint"] = ""
            imported_manifest["deterministic_fingerprint"] = deterministic_fingerprint(imported_manifest)
            pretty_write_json(imported_manifest_path, imported_manifest)
        report = build_compat_report("load",
                                     imported_manifest.get("install_id"),
                                     imported_manifest.get("instance_id"),
                                     args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "full", [], [],
                                     args.deterministic, {"bundle_type": "instance"}, None)
        return 0, {"result": "ok", "compat_report": report, "import_root": args.out.replace("\\", "/")}

    if not args.store_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "linked instance import requires --store-root",
                                  {"bundle_type": "instance"})
        report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {"bundle_type": "instance"}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    store_manifest = initialize_store_root(args.store_root)
    for ref in manifest.get("embedded_artifacts") or []:
        if not isinstance(ref, dict):
            continue
        category = str(ref.get("category", "")).strip()
        artifact_hash = str(ref.get("artifact_hash", "")).strip()
        artifact_type = str(ref.get("artifact_type", "")).strip()
        artifact_path = str(ref.get("artifact_path", "")).replace("/", os.sep)
        if not category or not artifact_hash or not artifact_type or not artifact_path:
            continue
        artifact_root = os.path.join(bundle_instance_root, artifact_path)
        if artifact_type == "json":
            payload = load_cas_json(os.path.join(artifact_root, JSON_PAYLOAD))
            result = store_add_artifact(args.store_root, category, payload)
        elif artifact_type == "tree":
            result = store_add_tree_artifact(args.store_root, category, artifact_payload_path(artifact_root, "tree"))
        else:
            continue
        if str(result.get("artifact_hash", "")).strip() != artifact_hash:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "artifact hash mismatch during import",
                                      {"category": category, "artifact_hash": artifact_hash})
            report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {"bundle_type": "instance"}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    ensure_dir(args.out)
    linked_manifest = dict(manifest)
    linked_manifest["mode"] = "linked"
    linked_manifest["store_root"] = build_store_locator(args.out, args.store_root, store_manifest)
    linked_manifest["embedded_artifacts"] = []
    linked_manifest["capability_lockfile"] = ""
    if args.instance_id:
        linked_manifest["instance_id"] = args.instance_id
    linked_manifest["deterministic_fingerprint"] = ""
    linked_manifest["deterministic_fingerprint"] = deterministic_fingerprint(linked_manifest)
    pretty_write_json(os.path.join(args.out, "instance.manifest.json"), linked_manifest)
    report = build_compat_report("load",
                                 linked_manifest.get("install_id"),
                                 linked_manifest.get("instance_id"),
                                 args.runtime_id,
                                 args.capability_baseline,
                                 [], [], [], "full", [], [],
                                 args.deterministic, {"bundle_type": "instance"}, None)
    return 0, {"result": "ok", "compat_report": report, "import_root": args.out.replace("\\", "/")}


def export_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    bundle_type = args.bundle_type
    if bundle_type == "instance":
        return export_instance_bundle(args)
    if bundle_type not in ("save", "replay", "blueprint", "modpack"):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "unknown bundle type",
                                  {"bundle_type": bundle_type})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if os.path.exists(args.out):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "bundle output already exists",
                                  {"path": os.path.basename(args.out)})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    required_artifact = args.artifact
    if not required_artifact or not os.path.isfile(required_artifact):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "artifact is required",
                                  {"artifact": required_artifact or ""})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if bundle_type in ("save", "replay", "modpack") and not args.lockfile:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "lockfile is required",
                                  {"bundle_type": bundle_type})
        report = build_compat_report("update", None, None, None,
                                     args.capability_baseline,
                                     [], [], [], "refuse",
                                     [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    ensure_dir(args.out)

    contents: List[Dict[str, object]] = []
    pack_refs = [parse_pack_ref(item) for item in (args.pack_ref or [])]

    artifact_name = os.path.basename(required_artifact)
    artifact_dest = os.path.join(args.out, "artifacts", bundle_type, artifact_name)
    copy_file(required_artifact, artifact_dest)
    contents.append(content_entry(os.path.relpath(artifact_dest, args.out), bundle_type, artifact_dest))

    if args.lockfile:
        lock_dest = os.path.join(args.out, "lockfile", os.path.basename(args.lockfile))
        copy_file(args.lockfile, lock_dest)
        contents.append(content_entry(os.path.relpath(lock_dest, args.out), "lockfile", lock_dest))
        lock_ref = os.path.relpath(lock_dest, args.out).replace("\\", "/")
    else:
        lock_ref = "lockfile/none"

    if args.compat_report:
        compat_dest = os.path.join(args.out, "compat", os.path.basename(args.compat_report))
        copy_file(args.compat_report, compat_dest)
    else:
        compat_dest = os.path.join(args.out, "compat", "compat_report.json")
        compat_payload = build_compat_report(
            context="export",
            install_id=args.install_id,
            instance_id=args.instance_id,
            runtime_id=args.runtime_id,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=[],
            missing_capabilities=[],
            compatibility_mode="full",
            refusal_codes=[],
            mitigation_hints=[],
            deterministic=args.deterministic,
            extensions={"bundle_type": bundle_type},
            refusal=None,
        )
        ensure_dir(os.path.dirname(compat_dest))
        write_json(compat_dest, compat_payload)
    contents.append(content_entry(os.path.relpath(compat_dest, args.out), "compat_report", compat_dest))
    compat_ref = os.path.relpath(compat_dest, args.out).replace("\\", "/")

    if args.instance_metadata:
        meta_dest = os.path.join(args.out, "meta", os.path.basename(args.instance_metadata))
        copy_file(args.instance_metadata, meta_dest)
        contents.append(content_entry(os.path.relpath(meta_dest, args.out), "instance_metadata", meta_dest))

    if args.runtime_metadata:
        meta_dest = os.path.join(args.out, "meta", os.path.basename(args.runtime_metadata))
        copy_file(args.runtime_metadata, meta_dest)
        contents.append(content_entry(os.path.relpath(meta_dest, args.out), "runtime_metadata", meta_dest))

    for ref_path in args.reference or []:
        if not os.path.isfile(ref_path):
            continue
        ref_dest = os.path.join(args.out, "refs", os.path.basename(ref_path))
        copy_file(ref_path, ref_dest)
        contents.append(content_entry(os.path.relpath(ref_dest, args.out), "schema_ref", ref_dest))

    embedded_packs: List[Dict[str, object]] = []
    for pack_path in args.embed_pack or []:
        if not os.path.isdir(pack_path):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "embedded pack path is invalid",
                                      {"pack_path": pack_path})
            report = build_compat_report("update", None, None, None,
                                         args.capability_baseline,
                                         [], [], [], "refuse",
                                         [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            shutil.rmtree(args.out, ignore_errors=True)
            return 3, {"result": "refused", "compat_report": report}
        pack_id, pack_version = read_pack_manifest(pack_path)
        dest = os.path.join(args.out, "packs", pack_id)
        copy_dir(pack_path, dest)
        pack_hash = sha256_dir(dest)
        embedded_packs.append({
            "pack_id": pack_id,
            "pack_version": pack_version,
            "pack_path": os.path.relpath(dest, args.out).replace("\\", "/"),
            "pack_hash": pack_hash,
            "pack_size_bytes": sum(os.path.getsize(os.path.join(root, name))
                                   for root, _dirs, files in os.walk(dest) for name in files),
        })

    contents_sorted = sorted(contents, key=lambda item: item["content_path"])
    bundle_container = {
        "bundle_type": bundle_type,
        "bundle_id": args.bundle_id or str(uuid.uuid4()),
        "created_at": args.created_at or now_timestamp(args.deterministic),
        "created_by": args.created_by or "unknown",
        "tool_version": args.tool_version or "unknown",
        "contents_index": contents_sorted,
        "lockfile_ref": lock_ref,
        "compat_report_ref": compat_ref,
        "embedded_packs": embedded_packs,
        "extensions": {},
    }
    if args.trust_tier:
        bundle_container["trust_tier"] = args.trust_tier
    if pack_refs:
        bundle_container["pack_refs"] = pack_refs
    if args.bundle_format_version is not None:
        bundle_container["bundle_format_version"] = args.bundle_format_version
    if args.bundle_tag:
        bundle_container["bundle_tags"] = sorted_unique(args.bundle_tag)

    write_json(os.path.join(args.out, BUNDLE_CONTAINER_NAME), bundle_container)

    report = build_compat_report("export", args.install_id, args.instance_id, args.runtime_id,
                                 args.capability_baseline,
                                 [], [], [], "full", [], [],
                                 args.deterministic,
                                 {"bundle_type": bundle_type, "bundle_id": bundle_container["bundle_id"]},
                                 None)
    return 0, {"result": "ok", "compat_report": report, "bundle_root": args.out.replace("\\", "/")}


def read_container(bundle_root: str) -> dict:
    path = os.path.join(bundle_root, BUNDLE_CONTAINER_NAME)
    return load_json(path)


def validate_container(bundle_root: str, container: dict) -> Tuple[bool, Optional[Dict[str, object]], Optional[str]]:
    bundle_type = container.get("bundle_type")
    if bundle_type not in ("save", "replay", "blueprint", "modpack", "instance"):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "unknown bundle type",
                                  {"bundle_type": bundle_type})
        return False, refusal, "unknown bundle type"
    contents = container.get("contents_index") or []
    kinds = {entry.get("content_kind") for entry in contents}
    if bundle_type not in kinds:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "missing primary artifact",
                                  {"bundle_type": bundle_type})
        return False, refusal, "missing primary artifact"
    if bundle_type in ("save", "replay", "modpack", "instance") and "lockfile" not in kinds:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "missing lockfile",
                                  {"bundle_type": bundle_type})
        return False, refusal, "missing lockfile"
    if "compat_report" not in kinds:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "missing compat_report",
                                  {"bundle_type": bundle_type})
        return False, refusal, "missing compat_report"
    for entry in contents:
        content_path = entry.get("content_path")
        if not content_path:
            continue
        abs_path = os.path.join(bundle_root, content_path)
        if not os.path.isfile(abs_path):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "missing content entry",
                                      {"content_path": content_path})
            return False, refusal, "missing content"
        if sha256_file(abs_path) != str(entry.get("sha256", "")).strip():
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "content hash mismatch",
                                      {"content_path": content_path})
            return False, refusal, "hash mismatch"
    return True, None, None


def compute_missing_packs(container: dict, available: List[str]) -> List[str]:
    embedded = {pack.get("pack_id") for pack in (container.get("embedded_packs") or [])}
    pack_refs = container.get("pack_refs") or []
    missing = []
    for pack in pack_refs:
        pack_id = pack.get("pack_id")
        if not pack_id:
            continue
        if pack_id in embedded:
            continue
        if pack_id in available:
            continue
        missing.append(pack_id)
    return sorted_unique(missing)


def inspect_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    container = read_container(args.bundle)
    ok, refusal, reason = validate_container(args.bundle, container)
    missing = compute_missing_packs(container, args.available_pack or [])
    mode = "inspect-only" if ok else "refuse"
    report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                 args.capability_baseline,
                                 [], [], missing,
                                 mode,
                                 [refusal.get("code")] if refusal else [],
                                 ["install missing packs"] if missing else [],
                                 args.deterministic,
                                 {"bundle_type": container.get("bundle_type"), "reason": reason},
                                 refusal)
    return (3 if not ok else 0), {
        "result": "refused" if not ok else "ok",
        "compat_report": report,
        "bundle_type": container.get("bundle_type"),
        "missing_packs": missing,
    }


def import_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    container = read_container(args.bundle)
    ok, refusal, reason = validate_container(args.bundle, container)
    if ok and container.get("bundle_type") == "instance":
        if not args.confirm:
            report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                         args.capability_baseline,
                                         [], [], [], "full",
                                         [], [],
                                         args.deterministic,
                                         {"bundle_type": container.get("bundle_type")},
                                         None)
            return 0, {
                "result": "ok",
                "import_state": "confirm_required",
                "compat_report": report,
                "missing_packs": [],
            }
        return import_instance_bundle(args, container)
    missing = compute_missing_packs(container, args.available_pack or [])
    mode = "full"
    if missing:
        mode = "degraded"
    if args.require_full and missing:
        mode = "refuse"
        refusal = refusal_payload(3, "REFUSE_CAPABILITY_MISSING",
                                  "missing packs required for full import",
                                  {"missing_packs": missing})
        ok = False
        reason = "missing packs"

    report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                 args.capability_baseline,
                                 [], [], missing,
                                 "refuse" if not ok else mode,
                                 [refusal.get("code")] if refusal else [],
                                 ["install missing packs"] if missing else [],
                                 args.deterministic,
                                 {"bundle_type": container.get("bundle_type"), "reason": reason},
                                 refusal)

    if not args.confirm:
        return (3 if not ok else 0), {
            "result": "refused" if not ok else "ok",
            "import_state": "confirm_required",
            "compat_report": report,
            "missing_packs": missing,
        }

    if not ok:
        return 3, {"result": "refused", "compat_report": report, "missing_packs": missing}

    if args.out:
        if os.path.exists(args.out):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "import destination exists",
                                      {"path": os.path.basename(args.out)})
            report = build_compat_report("load", args.install_id, args.instance_id, args.runtime_id,
                                         args.capability_baseline,
                                         [], [], missing,
                                         "refuse",
                                         [refusal.get("code")],
                                         [],
                                         args.deterministic,
                                         {"bundle_type": container.get("bundle_type")},
                                         refusal)
            return 3, {"result": "refused", "compat_report": report}
        copy_dir(args.bundle, args.out)
        return 0, {"result": "ok", "compat_report": report, "import_root": args.out.replace("\\", "/")}

    return 0, {"result": "ok", "compat_report": report}


def main() -> int:
    parser = argparse.ArgumentParser(description="Share bundle CLI (export/import/inspect)")
    parser.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--install-id", default=None)
    parser.add_argument("--instance-id", default=None)
    parser.add_argument("--runtime-id", default=None)
    sub = parser.add_subparsers(dest="cmd")

    export_cmd = sub.add_parser("export")
    export_cmd.add_argument("--bundle-type", required=True)
    export_cmd.add_argument("--artifact", required=True)
    export_cmd.add_argument("--lockfile", default=None)
    export_cmd.add_argument("--compat-report", default=None)
    export_cmd.add_argument("--instance-metadata", default=None)
    export_cmd.add_argument("--runtime-metadata", default=None)
    export_cmd.add_argument("--reference", action="append", default=[])
    export_cmd.add_argument("--pack-ref", action="append", default=[])
    export_cmd.add_argument("--embed-pack", action="append", default=[])
    export_cmd.add_argument("--bundle-id", default=None)
    export_cmd.add_argument("--bundle-format-version", type=int, default=None)
    export_cmd.add_argument("--bundle-tag", action="append", default=[])
    export_cmd.add_argument("--created-at", default=None)
    export_cmd.add_argument("--created-by", default=None)
    export_cmd.add_argument("--tool-version", default=None)
    export_cmd.add_argument("--trust-tier", default=None)
    export_cmd.add_argument("--out", required=True)

    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--bundle", required=True)
    inspect_cmd.add_argument("--available-pack", action="append", default=[])

    import_cmd = sub.add_parser("import")
    import_cmd.add_argument("--bundle", required=True)
    import_cmd.add_argument("--available-pack", action="append", default=[])
    import_cmd.add_argument("--require-full", action="store_true")
    import_cmd.add_argument("--confirm", action="store_true")
    import_cmd.add_argument("--out", default=None)
    import_cmd.add_argument("--instance-id", default=None)
    import_cmd.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    import_cmd.add_argument("--store-root", default=None)

    args = parser.parse_args()

    if args.cmd == "export":
        code, output = export_bundle(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "inspect":
        code, output = inspect_bundle(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "import":
        code, output = import_bundle(args)
        print(json.dumps(output, indent=2))
        return code

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
