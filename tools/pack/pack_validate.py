import argparse
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "distribution")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fab")))

from distribution_lib import (  # noqa: E402
    discover_pack_manifests,
    extract_record,
    is_reverse_dns,
    make_refusal,
    REFUSAL_CAPABILITY,
    REFUSAL_INTEGRITY,
    REFUSAL_INVALID,
)
from fab_validate import validate_pack as validate_fab_pack  # noqa: E402
from fab_lib import add_issue, load_json  # noqa: E402


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def detect_pack_root(pack_root, pack_id, repo_root):
    if pack_root:
        return os.path.abspath(pack_root)
    if pack_id:
        return os.path.abspath(os.path.join(repo_root, "data", "packs", pack_id))
    return None


def semver_ok(value):
    return isinstance(value, str) and SEMVER_RE.match(value) is not None


def extract_capabilities(entries):
    out = []
    for entry in normalize_list(entries):
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if isinstance(cap_id, str):
            out.append(cap_id)
    return out


def manifest_round_trip_ok(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    decoded = json.loads(encoded)
    return decoded


def validate_manifest(record, pack_root, issues):
    pack_id = record.get("pack_id")
    if not isinstance(pack_id, str):
        add_issue(issues, "manifest_pack_id", "pack_id missing", "record.pack_id")
    elif not is_reverse_dns(pack_id):
        add_issue(issues, "id_shape", "pack_id must be lowercase reverse-dns", "record.pack_id")

    pack_version = record.get("pack_version")
    if not semver_ok(pack_version):
        add_issue(issues, "manifest_pack_version", "pack_version must be semver", "record.pack_version")

    if "pack_format_version" not in record:
        add_issue(issues, "manifest_pack_format", "pack_format_version missing", "record.pack_format_version")
    if "requires_engine" not in record and "required_engine_version" not in record:
        add_issue(issues, "manifest_engine", "requires_engine missing", "record.requires_engine")

    provides = extract_capabilities(record.get("provides"))
    if not provides:
        add_issue(issues, "manifest_provides", "provides missing", "record.provides")
    for idx, cap_id in enumerate(provides):
        if not is_reverse_dns(cap_id):
            add_issue(issues, "namespace_invalid", "capability_id must be reverse-dns",
                      "record.provides[{}]".format(idx))

    depends = extract_capabilities(record.get("depends"))
    for idx, cap_id in enumerate(depends):
        if not is_reverse_dns(cap_id):
            add_issue(issues, "namespace_invalid", "capability_id must be reverse-dns",
                      "record.depends[{}]".format(idx))

    deps_alias = extract_capabilities(record.get("dependencies"))
    if deps_alias:
        if sorted(depends) != sorted(deps_alias):
            add_issue(issues, "dependencies_mismatch", "depends and dependencies mismatch", "record.dependencies")

    if "extensions" not in record:
        add_issue(issues, "extensions_missing", "extensions missing", "record.extensions")

    if pack_root and isinstance(pack_id, str):
        folder = os.path.basename(pack_root.rstrip("\\/"))
        if folder != pack_id:
            add_issue(issues, "pack_id_mismatch", "pack_id must match folder name", "record.pack_id")


def validate_capability_refs(record, provider_map, issues):
    depends = extract_capabilities(record.get("depends"))
    for cap_id in depends:
        if cap_id not in provider_map:
            add_issue(issues, "capability_missing",
                      "required capability has no provider: {}".format(cap_id),
                      "record.depends")


def load_manifest(path):
    payload = load_json(path)
    return payload, extract_record(payload)


def validate_fab(pack_root, repo_root, issues):
    fab_path = os.path.join(pack_root, "data", "fab_pack.json")
    if not os.path.isfile(fab_path):
        return
    fab_data = load_json(fab_path)
    fab_issues = validate_fab_pack(fab_data, repo_root, pack_root=None)
    for issue in fab_issues:
        issues.append({
            "code": "fab_" + issue.get("code", ""),
            "message": issue.get("message", ""),
            "path": "fab_pack.{}".format(issue.get("path", "")),
        })


def main():
    parser = argparse.ArgumentParser(description="Validate pack manifests and data packs.")
    parser.add_argument("--pack-root", default=None)
    parser.add_argument("--pack-id", default=None)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    pack_root = detect_pack_root(args.pack_root, args.pack_id, repo_root)
    issues = []

    if not pack_root or not os.path.isdir(pack_root):
        add_issue(issues, "pack_root_missing", "pack root not found", "pack_root")
    else:
        manifest_path = os.path.join(pack_root, "pack_manifest.json")
        if not os.path.isfile(manifest_path):
            add_issue(issues, "manifest_missing", "pack_manifest.json missing", "pack_manifest.json")
        else:
            payload, record = load_manifest(manifest_path)
            if not record:
                add_issue(issues, "manifest_invalid", "pack_manifest.json invalid", "pack_manifest.json")
            else:
                validate_manifest(record, pack_root, issues)
                all_packs = discover_pack_manifests(["data/packs", "data/worldgen"], repo_root)
                provider_map = {}
                for pack in all_packs:
                    for cap_id in pack.get("provides") or []:
                        provider_map.setdefault(cap_id, []).append(pack.get("pack_id"))
                validate_capability_refs(record, provider_map, issues)
            if isinstance(payload, dict):
                round_trip = manifest_round_trip_ok(payload)
                if set(round_trip.keys()) != set(payload.keys()):
                    add_issue(issues, "unknown_field_loss", "unknown fields lost in round-trip", "pack_manifest")

        validate_fab(pack_root, repo_root, issues)

    issues = sorted(issues, key=lambda item: (item.get("path", ""), item.get("code", "")))
    ok = len(issues) == 0
    if ok:
        payload = {"ok": True, "issues": []}
    else:
        code_id, code = REFUSAL_INVALID
        if any(issue["code"].startswith("ref_") for issue in issues):
            code_id, code = REFUSAL_INTEGRITY
        if any(issue["code"] == "capability_missing" for issue in issues):
            code_id, code = REFUSAL_CAPABILITY
        payload = {"ok": False, "issues": issues,
                   "refusal": make_refusal(code_id, code, "pack validation failed", {})}

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0 if ok else 2

    if ok:
        print("pack_validate: ok")
        return 0
    print("pack_validate: failed")
    for issue in issues:
        print("{code} {path} {message}".format(**issue))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
