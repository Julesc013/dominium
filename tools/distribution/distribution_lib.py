import json
import os
import re


REVERSE_DNS_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9][a-z0-9_-]*)+$")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def is_reverse_dns(identifier):
    if not isinstance(identifier, str):
        return False
    if not identifier.isascii():
        return False
    if identifier != identifier.lower():
        return False
    return REVERSE_DNS_RE.match(identifier) is not None


def semver_tuple(value):
    parts = (value or "").split(".")
    nums = []
    for part in parts[:3]:
        try:
            nums.append(int(part))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def pack_sort_key(pack):
    major, minor, patch = semver_tuple(pack.get("pack_version", "0.0.0"))
    return (-major, -minor, -patch,
            pack.get("pack_id", ""),
            pack.get("root", ""),
            pack.get("manifest_relpath", ""))


def extract_record(payload):
    if isinstance(payload, dict) and isinstance(payload.get("record"), dict):
        return payload.get("record")
    return payload if isinstance(payload, dict) else {}


def extract_capabilities(record):
    caps = []
    provides = record.get("provides", [])
    if isinstance(provides, list):
        for entry in provides:
            if isinstance(entry, dict):
                cap_id = entry.get("capability_id")
                if isinstance(cap_id, str):
                    caps.append(cap_id)
    return caps


def normalize_pack_manifest(payload, root_label, manifest_relpath):
    record = extract_record(payload)
    pack = {
        "pack_id": record.get("pack_id"),
        "pack_version": record.get("pack_version"),
        "pack_format_version": record.get("pack_format_version"),
        "requires_stage": record.get("requires_stage"),
        "provides_stage": record.get("provides_stage"),
        "stage_features": record.get("stage_features") if isinstance(record.get("stage_features"), list) else [],
        "root": root_label,
        "manifest_relpath": manifest_relpath,
        "provides": extract_capabilities(record),
    }
    return pack


def discover_pack_manifests(roots, repo_root):
    packs = []
    for root in roots:
        root_abs = os.path.abspath(os.path.join(repo_root, root))
        root_label = os.path.relpath(root_abs, repo_root)
        if not os.path.isdir(root_abs):
            continue
        for dirpath, _dirnames, filenames in os.walk(root_abs):
            if "pack_manifest.json" not in filenames:
                continue
            manifest_path = os.path.join(dirpath, "pack_manifest.json")
            try:
                payload = load_json(manifest_path)
            except Exception:
                continue
            relpath = os.path.relpath(manifest_path, root_abs)
            packs.append(normalize_pack_manifest(payload, root_label, relpath))
    packs.sort(key=pack_sort_key)
    return packs


def make_refusal(code_id, code, message, details=None):
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


REFUSAL_INVALID = (1, "REFUSE_INVALID_INTENT")
REFUSAL_LAW = (2, "REFUSE_LAW_FORBIDDEN")
REFUSAL_CAPABILITY = (3, "REFUSE_CAPABILITY_MISSING")
REFUSAL_DOMAIN = (4, "REFUSE_DOMAIN_FORBIDDEN")
REFUSAL_INTEGRITY = (5, "REFUSE_INTEGRITY_VIOLATION")
