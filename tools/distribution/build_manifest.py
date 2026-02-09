#!/usr/bin/env python3
import argparse
import datetime
import json
import os

from dompkg_lib import refusal_payload


def _canonical_bytes(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _load_index(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _timestamp_utc(deterministic: bool) -> str:
    if deterministic:
        return "2000-01-01T00:00:00Z"
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic dist build manifest from pkg index.")
    parser.add_argument("--index-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-tlv", default="")
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--abi", required=True)
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--compression-default", default="deflate")
    parser.add_argument("--compression-required", action="append", default=["deflate"])
    parser.add_argument("--compression-optional", action="append", default=[])
    parser.add_argument("--zstd-threshold-bytes", type=int, default=1073741824)
    parser.add_argument("--signature-policy", default="dev_optional")
    parser.add_argument("--trust-policy-ref", default="schema/distribution/trust_policy.schema")
    args = parser.parse_args()

    index_json = os.path.abspath(args.index_json)
    if not os.path.isfile(index_json):
        print(json.dumps(refusal_payload("refuse.invalid_input", "pkg index missing", {"index_json": index_json}), indent=2))
        return 3

    try:
        index_payload = _load_index(index_json)
    except Exception as exc:
        print(json.dumps(refusal_payload("refuse.invalid_input", "invalid pkg index json", {"error": str(exc)}), indent=2))
        return 3

    packages = []
    for entry in sorted(index_payload.get("packages", []), key=lambda item: (item.get("pkg_id", ""), item.get("pkg_version", ""), item.get("content_hash", ""))):
        packages.append({
            "pkg_id": entry.get("pkg_id", ""),
            "pkg_version": entry.get("pkg_version", ""),
            "content_hash": entry.get("content_hash", ""),
            "package_path": entry.get("package_path", ""),
            "size_bytes": int(entry.get("package_size_bytes", 0)),
            "tags": [],
        })

    manifest = {
        "schema_id": "dominium.schema.distribution.build_manifest",
        "schema_version": "1.0.0",
        "record": {
            "build_id": args.build_id,
            "build_timestamp_utc": _timestamp_utc(args.deterministic),
            "platform": args.platform,
            "arch": args.arch,
            "abi": args.abi,
            "compression_policy": {
                "default_algorithm": args.compression_default,
                "required_algorithms": sorted(set(args.compression_required)),
                "optional_algorithms": sorted(set(args.compression_optional)),
                "zstd_enable_threshold_bytes": int(args.zstd_threshold_bytes),
            },
            "signature_policy": {
                "release_requires_signature": "policy.controlled",
                "dev_allows_unsigned": "true",
                "trust_policy_ref": args.trust_policy_ref,
                "policy_mode": args.signature_policy,
            },
            "packages": packages,
            "extensions": {
                "index_ref": index_json.replace("\\", "/"),
            },
        }
    }

    out_json = os.path.abspath(args.out_json)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=False)
        handle.write("\n")

    if args.out_tlv:
        tlv_payload = _canonical_bytes(manifest)
        tlv = (1).to_bytes(2, "little") + len(tlv_payload).to_bytes(4, "little") + tlv_payload
        out_tlv = os.path.abspath(args.out_tlv)
        os.makedirs(os.path.dirname(out_tlv), exist_ok=True)
        with open(out_tlv, "wb") as handle:
            handle.write(tlv)

    print(json.dumps({
        "result": "ok",
        "build_manifest": out_json.replace("\\", "/"),
        "package_count": len(packages),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
