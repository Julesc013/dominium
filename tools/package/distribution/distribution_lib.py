import json
import os
import re
import sys
try:
    import tomllib
except ImportError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None

THIS_DIR = os.path.dirname(__file__)
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.validators.compatibility.shims import redirect_legacy_path
from meta_extensions_engine import normalize_extensions_tree


REVERSE_DNS_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9][a-z0-9_-]*)+$")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return normalize_extensions_tree(json.load(handle))


def load_toml(path):
    if tomllib is None:
        raise RuntimeError("tomllib is required to read pack.toml")
    with open(path, "rb") as handle:
        return normalize_extensions_tree(tomllib.load(handle))


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
            elif isinstance(entry, str):
                caps.append(entry)
    return caps


def extract_capability_refs(record, field_name):
    caps = []
    values = record.get(field_name, [])
    if not isinstance(values, list):
        return caps
    for entry in values:
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if isinstance(cap_id, str):
            caps.append(cap_id)
    return caps


def normalize_pack_manifest(payload, root_label, manifest_relpath):
    record = extract_record(payload)
    pack = {
        "pack_id": record.get("pack_id"),
        "pack_version": record.get("pack_version") or record.get("version"),
        "pack_format_version": record.get("pack_format_version"),
        "requires_capabilities": extract_capability_refs(record, "requires_capabilities"),
        "provides_capabilities": extract_capability_refs(record, "provides_capabilities"),
        "optional_capabilities": extract_capability_refs(record, "optional_capabilities"),
        "entitlements": extract_capability_refs(record, "entitlements"),
        "root": root_label,
        "manifest_relpath": manifest_relpath,
        "provides": extract_capabilities(record),
        "depends": extract_capability_refs(record, "depends")
        or extract_capability_refs(record, "dependencies")
        or extract_capability_refs(record, "requires_capabilities"),
    }
    return pack


def _canonical_source_root(root):
    normalized = str(root).replace("\\", "/").strip().strip("/")
    if normalized in ("data/packs", "data/worldgen"):
        return "content/packs"
    return normalized


def _load_manifest_payload(path):
    if path.endswith(".toml"):
        return load_toml(path)
    return load_json(path)


def discover_pack_manifests(roots, repo_root):
    packs = []
    for root in roots:
        original_root = str(root)
        canonical_root = _canonical_source_root(original_root)
        canonical_abs = os.path.abspath(os.path.join(repo_root, canonical_root))
        if not os.path.isabs(original_root) and os.path.isdir(canonical_abs):
            root_abs = canonical_abs
            root_label = canonical_root.replace("\\", "/")
        else:
            redirected = redirect_legacy_path(
                str(root),
                repo_root=repo_root,
                product_id="tool.attach_console_stub",
                executable_path=os.path.join(repo_root, "dist", "bin", "dom"),
                emit_warning=True,
            )
            root_abs = str(redirected.get("rewritten_path", "")).strip() or os.path.abspath(os.path.join(repo_root, root))
            root_label = original_root.replace("\\", "/") if not os.path.isabs(original_root) else os.path.relpath(root_abs, repo_root)
        if not os.path.isdir(root_abs):
            continue
        for dirpath, _dirnames, filenames in os.walk(root_abs):
            manifest_name = ""
            for candidate in ("pack_manifest.json", "pack.json", "pack.toml"):
                if candidate in filenames:
                    manifest_name = candidate
                    break
            if not manifest_name:
                continue
            manifest_path = os.path.join(dirpath, manifest_name)
            try:
                payload = _load_manifest_payload(manifest_path)
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
