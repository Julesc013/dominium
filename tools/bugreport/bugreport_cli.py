import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


BUNDLE_MANIFEST_NAME = "bugreport.bundle.json"
BUNDLE_CONTAINER_NAME = "bundle.container.json"
DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"
EXECUTABLE_EXTS = {".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".ps1", ".sh"}

ABS_WIN_RE = re.compile(r"[A-Za-z]:[\\/][^\\s\"']+")
ABS_UNIX_RE = re.compile(r"/(Users|home|var|etc|opt|usr)/[^\\s\"']+")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
IPV6_RE = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b")


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("OPS_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload: dict) -> None:
    dir_name = os.path.dirname(path)
    if dir_name:
        ensure_dir(dir_name)
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
    for root, dirs, files in os.walk(path):
        dirs.sort()
        rel_root = os.path.relpath(root, path).replace("\\", "/")
        for name in sorted(files):
            rel_path = (rel_root + "/" + name) if rel_root != "." else name
            h.update(rel_path.encode("utf-8"))
            with open(os.path.join(root, name), "rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    h.update(chunk)
    return h.hexdigest()


def dir_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            total += os.path.getsize(os.path.join(root, name))
    return total


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
                        compatibility_mode: str,
                        refusal_codes: Optional[List[str]],
                        mitigation_hints: Optional[List[str]],
                        deterministic: bool,
                        extensions: Optional[Dict[str, object]] = None,
                        refusal: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    payload = {
        "context": context,
        "install_id": install_id or NULL_UUID,
        "instance_id": instance_id or NULL_UUID,
        "runtime_id": runtime_id or NULL_UUID,
        "capability_baseline": capability_baseline or DEFAULT_CAPABILITY_BASELINE,
        "required_capabilities": [],
        "provided_capabilities": [],
        "missing_capabilities": [],
        "compatibility_mode": compatibility_mode,
        "refusal_codes": sorted_unique(refusal_codes),
        "mitigation_hints": sorted_unique(mitigation_hints),
        "timestamp": now_timestamp(deterministic),
        "extensions": extensions or {},
    }
    if refusal:
        payload["refusal"] = refusal
    return payload


def read_manifest_ids(install_manifest: str,
                      instance_manifest: str,
                      runtime_descriptor: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    install_id = None
    instance_id = None
    runtime_id = None
    try:
        install_id = load_json(install_manifest).get("install_id")
    except (OSError, ValueError, AttributeError):
        pass
    try:
        instance_id = load_json(instance_manifest).get("instance_id")
    except (OSError, ValueError, AttributeError):
        pass
    try:
        runtime_id = load_json(runtime_descriptor).get("runtime_id")
    except (OSError, ValueError, AttributeError):
        pass
    return install_id, instance_id, runtime_id


def copy_file(src: str, dest: str) -> None:
    ensure_dir(os.path.dirname(dest))
    shutil.copy2(src, dest)


def copy_dir(src: str, dest: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def validate_bundle_dir(path: str) -> Tuple[bool, Optional[str]]:
    if not os.path.isdir(path):
        return False, "bundle root is not a directory"
    manifest = os.path.join(path, BUNDLE_CONTAINER_NAME)
    if not os.path.isfile(manifest):
        return False, "missing bundle.container.json"
    return True, None


def contains_executables(path: str) -> Optional[str]:
    for root, _dirs, files in os.walk(path):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in EXECUTABLE_EXTS:
                return os.path.join(root, name)
    return None


def content_entry(path: str, kind: str, actual_path: str) -> Dict[str, object]:
    if os.path.isdir(actual_path):
        size = dir_size(actual_path)
        digest = sha256_dir(actual_path)
    else:
        size = os.path.getsize(actual_path)
        digest = sha256_file(actual_path)
    return {
        "content_path": path.replace("\\", "/"),
        "content_kind": kind,
        "sha256": digest,
        "size_bytes": size,
    }


def redact_text(text: str,
                redact_paths: bool,
                redact_ips: bool,
                user_tokens: List[str]) -> Tuple[str, Dict[str, int]]:
    counts = {"paths": 0, "ips": 0, "users": 0}
    if redact_paths:
        text, c1 = ABS_WIN_RE.subn("<redacted_path>", text)
        text, c2 = ABS_UNIX_RE.subn("<redacted_path>", text)
        counts["paths"] += c1 + c2
    if redact_ips:
        text, c1 = IPV4_RE.subn("<redacted_ip>", text)
        text, c2 = IPV6_RE.subn("<redacted_ip>", text)
        counts["ips"] += c1 + c2
    for token in user_tokens:
        if not token:
            continue
        pattern = re.compile(re.escape(token))
        text, c1 = pattern.subn("<redacted_user>", text)
        counts["users"] += c1
    return text, counts


def redact_json_value(value: object,
                      redact_paths: bool,
                      redact_ips: bool,
                      user_tokens: List[str],
                      totals: Dict[str, int]) -> object:
    if isinstance(value, dict):
        return {key: redact_json_value(val, redact_paths, redact_ips, user_tokens, totals)
                for key, val in value.items()}
    if isinstance(value, list):
        return [redact_json_value(val, redact_paths, redact_ips, user_tokens, totals) for val in value]
    if isinstance(value, str):
        redacted, counts = redact_text(value, redact_paths, redact_ips, user_tokens)
        totals["paths"] += counts["paths"]
        totals["ips"] += counts["ips"]
        totals["users"] += counts["users"]
        return redacted
    return value


def redact_file(path: str,
                redact_paths: bool,
                redact_ips: bool,
                user_tokens: List[str],
                totals: Dict[str, int]) -> None:
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in (".json", ".lock", ".manifest", ".descriptor"):
        try:
            payload = load_json(path)
        except (OSError, ValueError):
            return
        payload = redact_json_value(payload, redact_paths, redact_ips, user_tokens, totals)
        write_json(path, payload)
        return
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read()
    except OSError:
        return
    redacted, counts = redact_text(text, redact_paths, redact_ips, user_tokens)
    totals["paths"] += counts["paths"]
    totals["ips"] += counts["ips"]
    totals["users"] += counts["users"]
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(redacted)


def apply_redaction(bundle_root: str,
                    redact_paths: bool,
                    redact_ips: bool,
                    redact_users: bool,
                    extra_users: List[str]) -> Dict[str, object]:
    totals = {"paths": 0, "ips": 0, "users": 0}
    user_tokens = list(extra_users or [])
    if redact_users:
        env_user = os.environ.get("USERNAME") or os.environ.get("USER")
        if env_user:
            user_tokens.append(env_user)
    user_tokens = sorted_unique(user_tokens)
    for root, _dirs, files in os.walk(bundle_root):
        rel_root = os.path.relpath(root, bundle_root).replace("\\", "/")
        if rel_root.startswith("bundles"):
            continue
        for name in files:
            if name == BUNDLE_MANIFEST_NAME:
                continue
            redact_file(os.path.join(root, name),
                        redact_paths,
                        redact_ips,
                        user_tokens,
                        totals)
    return {
        "redacted_paths": totals["paths"],
        "redacted_ips": totals["ips"],
        "redacted_users": totals["users"],
        "user_tokens": user_tokens,
    }


def build_environment_summary(deterministic: bool) -> Dict[str, object]:
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "byteorder": sys.byteorder,
        "created_at": now_timestamp(deterministic),
        "extensions": {},
    }


def build_refusal_summary(source_path: Optional[str]) -> Dict[str, object]:
    if source_path and os.path.isfile(source_path):
        try:
            return load_json(source_path)
        except (OSError, ValueError):
            pass
    return {
        "refusal_count": 0,
        "refusals": [],
        "notes": "no refusal summary provided",
        "extensions": {},
    }


def create_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    if os.path.exists(args.out):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "bugreport output already exists",
                                  {"path": os.path.basename(args.out)})
        report = build_compat_report("export", None, None, None,
                                     args.capability_baseline,
                                     "refuse", [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    ok, reason = validate_bundle_dir(args.replay_bundle)
    if not ok:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "replay bundle invalid",
                                  {"reason": reason})
        report = build_compat_report("export", None, None, None,
                                     args.capability_baseline,
                                     "refuse", [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    if args.save_bundle:
        ok, reason = validate_bundle_dir(args.save_bundle)
        if not ok:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "save bundle invalid",
                                      {"reason": reason})
            report = build_compat_report("export", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    required_files = {
        "install_manifest": args.install_manifest,
        "instance_manifest": args.instance_manifest,
        "runtime_descriptor": args.runtime_descriptor,
        "compat_report": args.compat_report,
        "ops_log": args.ops_log,
    }
    for label, path in required_files.items():
        if not path or not os.path.isfile(path):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "{} is required".format(label.replace("_", " ")),
                                      {"path": path or ""})
            report = build_compat_report("export", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    if args.reporter_notes:
        if not os.path.isfile(args.reporter_notes):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                      "reporter notes missing",
                                      {"path": args.reporter_notes})
            report = build_compat_report("export", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}
        note_ext = os.path.splitext(args.reporter_notes)[1].lower()
        if note_ext in EXECUTABLE_EXTS:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "reporter notes appear executable",
                                      {"file": os.path.basename(args.reporter_notes)})
            report = build_compat_report("export", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    for bundle_path in [args.replay_bundle] + ([args.save_bundle] if args.save_bundle else []):
        bad = contains_executables(bundle_path)
        if bad:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "bundle contains executable",
                                      {"file": os.path.basename(bad)})
            report = build_compat_report("export", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    ensure_dir(args.out)
    replay_dest = os.path.join(args.out, "bundles", "replay")
    copy_dir(args.replay_bundle, replay_dest)
    save_dest = None
    if args.save_bundle:
        save_dest = os.path.join(args.out, "bundles", "save")
        copy_dir(args.save_bundle, save_dest)

    install_dest = os.path.join(args.out, "manifests", "install.manifest.json")
    instance_dest = os.path.join(args.out, "manifests", "instance.manifest.json")
    runtime_dest = os.path.join(args.out, "manifests", "runtime.descriptor.json")
    compat_dest = os.path.join(args.out, "compat", "compat_report.json")
    ops_dest = os.path.join(args.out, "ops", "ops.log")
    refusal_dest = os.path.join(args.out, "refusal", "refusal_summary.json")
    env_dest = os.path.join(args.out, "environment", "environment_summary.json")

    copy_file(args.install_manifest, install_dest)
    copy_file(args.instance_manifest, instance_dest)
    copy_file(args.runtime_descriptor, runtime_dest)
    copy_file(args.compat_report, compat_dest)

    ensure_dir(os.path.dirname(ops_dest))
    with open(args.ops_log, "r", encoding="utf-8", errors="ignore") as handle:
        lines = handle.readlines()
    if args.ops_log_lines > 0:
        lines = lines[-args.ops_log_lines:]
    with open(ops_dest, "w", encoding="utf-8") as handle:
        handle.writelines(lines)

    refusal_payload_data = build_refusal_summary(args.refusal_summary)
    write_json(refusal_dest, refusal_payload_data)

    env_payload = build_environment_summary(args.deterministic)
    write_json(env_dest, env_payload)

    notes_dest = None
    if args.reporter_notes:
        notes_dest = os.path.join(args.out, "notes", os.path.basename(args.reporter_notes))
        copy_file(args.reporter_notes, notes_dest)

    redaction_summary = None
    if args.redact_paths or args.redact_ips or args.redact_users or args.redact_user:
        redaction_summary = apply_redaction(args.out,
                                            args.redact_paths,
                                            args.redact_ips,
                                            args.redact_users,
                                            args.redact_user)
        redaction_summary["created_at"] = now_timestamp(args.deterministic)
        redaction_summary["extensions"] = {}
        redaction_dest = os.path.join(args.out, "redaction", "redaction_summary.json")
        write_json(redaction_dest, redaction_summary)
    else:
        redaction_dest = None

    install_id, instance_id, runtime_id = read_manifest_ids(install_dest, instance_dest, runtime_dest)

    contents: List[Dict[str, object]] = []
    contents.append(content_entry(os.path.relpath(replay_dest, args.out), "replay_bundle", replay_dest))
    if save_dest:
        contents.append(content_entry(os.path.relpath(save_dest, args.out), "save_bundle", save_dest))
    contents.append(content_entry(os.path.relpath(install_dest, args.out), "install_manifest", install_dest))
    contents.append(content_entry(os.path.relpath(instance_dest, args.out), "instance_manifest", instance_dest))
    contents.append(content_entry(os.path.relpath(runtime_dest, args.out), "runtime_descriptor", runtime_dest))
    contents.append(content_entry(os.path.relpath(compat_dest, args.out), "compat_report", compat_dest))
    contents.append(content_entry(os.path.relpath(ops_dest, args.out), "ops_log", ops_dest))
    contents.append(content_entry(os.path.relpath(refusal_dest, args.out), "refusal_summary", refusal_dest))
    contents.append(content_entry(os.path.relpath(env_dest, args.out), "environment_summary", env_dest))
    if notes_dest:
        contents.append(content_entry(os.path.relpath(notes_dest, args.out), "reporter_notes", notes_dest))
    if redaction_dest:
        contents.append(content_entry(os.path.relpath(redaction_dest, args.out), "redaction_summary", redaction_dest))

    contents_sorted = sorted(contents, key=lambda item: item["content_path"])
    bundle_manifest = {
        "bugreport_id": args.bugreport_id or str(uuid.uuid4()),
        "replay_bundle_ref": os.path.relpath(replay_dest, args.out).replace("\\", "/"),
        "install_manifest_ref": os.path.relpath(install_dest, args.out).replace("\\", "/"),
        "instance_manifest_ref": os.path.relpath(instance_dest, args.out).replace("\\", "/"),
        "runtime_descriptor_ref": os.path.relpath(runtime_dest, args.out).replace("\\", "/"),
        "compat_report_ref": os.path.relpath(compat_dest, args.out).replace("\\", "/"),
        "ops_log_ref": os.path.relpath(ops_dest, args.out).replace("\\", "/"),
        "refusal_summary_ref": os.path.relpath(refusal_dest, args.out).replace("\\", "/"),
        "environment_summary_ref": os.path.relpath(env_dest, args.out).replace("\\", "/"),
        "created_at": args.created_at or now_timestamp(args.deterministic),
        "extensions": {},
        "content_index": contents_sorted,
    }
    if save_dest:
        bundle_manifest["save_bundle_ref"] = os.path.relpath(save_dest, args.out).replace("\\", "/")
    if notes_dest:
        bundle_manifest["reporter_notes_ref"] = os.path.relpath(notes_dest, args.out).replace("\\", "/")
    if redaction_dest:
        bundle_manifest["redaction_summary_ref"] = os.path.relpath(redaction_dest, args.out).replace("\\", "/")
    if args.tool_version:
        bundle_manifest["tool_version"] = args.tool_version
    if args.created_by:
        bundle_manifest["created_by"] = args.created_by
    if args.bundle_format_version is not None:
        bundle_manifest["bundle_format_version"] = args.bundle_format_version
    if args.bundle_tag:
        bundle_manifest["bundle_tags"] = sorted_unique(args.bundle_tag)

    write_json(os.path.join(args.out, BUNDLE_MANIFEST_NAME), bundle_manifest)

    report = build_compat_report("export",
                                 install_id,
                                 instance_id,
                                 runtime_id,
                                 args.capability_baseline,
                                 "full",
                                 [],
                                 [],
                                 args.deterministic,
                                 {"bugreport_id": bundle_manifest["bugreport_id"]},
                                 None)
    return 0, {"result": "ok", "compat_report": report, "bundle_root": args.out.replace("\\", "/")}


def load_bundle(bundle_root: str) -> dict:
    return load_json(os.path.join(bundle_root, BUNDLE_MANIFEST_NAME))


def validate_content_entry(bundle_root: str, entry: Dict[str, object]) -> Optional[str]:
    content_path = entry.get("content_path")
    if not content_path:
        return "missing content path"
    abs_path = os.path.join(bundle_root, content_path)
    if not os.path.exists(abs_path):
        return "missing content path"
    if os.path.isdir(abs_path):
        digest = sha256_dir(abs_path)
    else:
        digest = sha256_file(abs_path)
    if digest != entry.get("sha256"):
        return "hash mismatch"
    return None


def inspect_bundle(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    bundle = load_bundle(args.bundle)
    required_refs = [
        "replay_bundle_ref",
        "install_manifest_ref",
        "instance_manifest_ref",
        "runtime_descriptor_ref",
        "compat_report_ref",
        "ops_log_ref",
        "refusal_summary_ref",
        "environment_summary_ref",
        "created_at",
    ]
    for ref in required_refs:
        if ref not in bundle:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "missing required field",
                                      {"field": ref})
            report = build_compat_report("load", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    replay_path = os.path.join(args.bundle, bundle.get("replay_bundle_ref"))
    ok, reason = validate_bundle_dir(replay_path)
    if not ok:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "invalid replay bundle",
                                  {"reason": reason})
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     "refuse", [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    save_ref = bundle.get("save_bundle_ref")
    if save_ref:
        save_path = os.path.join(args.bundle, save_ref)
        ok, reason = validate_bundle_dir(save_path)
        if not ok:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "invalid save bundle",
                                      {"reason": reason})
            report = build_compat_report("load", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    for ref_field in [
        "install_manifest_ref",
        "instance_manifest_ref",
        "runtime_descriptor_ref",
        "compat_report_ref",
        "ops_log_ref",
        "refusal_summary_ref",
        "environment_summary_ref",
    ]:
        path = os.path.join(args.bundle, bundle.get(ref_field))
        if not os.path.isfile(path):
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "missing referenced file",
                                      {"field": ref_field})
            report = build_compat_report("load", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    bad_exec = contains_executables(args.bundle)
    if bad_exec:
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "bundle contains executable",
                                  {"file": os.path.basename(bad_exec)})
        report = build_compat_report("load", None, None, None,
                                     args.capability_baseline,
                                     "refuse", [refusal.get("code")], [],
                                     args.deterministic, {}, refusal)
        return 3, {"result": "refused", "compat_report": report}

    content_index = bundle.get("content_index") or []
    for entry in content_index:
        reason = validate_content_entry(args.bundle, entry)
        if reason:
            refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                      "content entry failed integrity check",
                                      {"content_path": entry.get("content_path", ""),
                                       "reason": reason})
            report = build_compat_report("load", None, None, None,
                                         args.capability_baseline,
                                         "refuse", [refusal.get("code")], [],
                                         args.deterministic, {}, refusal)
            return 3, {"result": "refused", "compat_report": report}

    report = build_compat_report("load", None, None, None,
                                 args.capability_baseline,
                                 "inspect-only",
                                 [],
                                 [],
                                 args.deterministic,
                                 {"bugreport_id": bundle.get("bugreport_id")},
                                 None)
    return 0, {"result": "ok", "compat_report": report}


def main() -> int:
    parser = argparse.ArgumentParser(description="Bugreport bundle CLI (create/inspect)")
    parser.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    parser.add_argument("--deterministic", action="store_true")
    sub = parser.add_subparsers(dest="cmd")

    create_cmd = sub.add_parser("create")
    create_cmd.add_argument("--replay-bundle", required=True)
    create_cmd.add_argument("--save-bundle", default=None)
    create_cmd.add_argument("--install-manifest", required=True)
    create_cmd.add_argument("--instance-manifest", required=True)
    create_cmd.add_argument("--runtime-descriptor", required=True)
    create_cmd.add_argument("--compat-report", required=True)
    create_cmd.add_argument("--ops-log", required=True)
    create_cmd.add_argument("--ops-log-lines", type=int, default=200)
    create_cmd.add_argument("--refusal-summary", default=None)
    create_cmd.add_argument("--reporter-notes", default=None)
    create_cmd.add_argument("--bugreport-id", default=None)
    create_cmd.add_argument("--bundle-format-version", type=int, default=None)
    create_cmd.add_argument("--bundle-tag", action="append", default=[])
    create_cmd.add_argument("--created-at", default=None)
    create_cmd.add_argument("--created-by", default=None)
    create_cmd.add_argument("--tool-version", default=None)
    create_cmd.add_argument("--redact-paths", action="store_true")
    create_cmd.add_argument("--redact-ips", action="store_true")
    create_cmd.add_argument("--redact-users", action="store_true")
    create_cmd.add_argument("--redact-user", action="append", default=[])
    create_cmd.add_argument("--out", required=True)

    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--bundle", required=True)

    args = parser.parse_args()

    if args.cmd == "create":
        code, output = create_bundle(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "inspect":
        code, output = inspect_bundle(args)
        print(json.dumps(output, indent=2))
        return code

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
