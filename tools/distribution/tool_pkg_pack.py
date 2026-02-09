#!/usr/bin/env python3
import argparse
import json
import os
import sys

from dompkg_lib import DomPkgError, collect_inputs, pack_package, refusal_payload


def load_signature(path: str):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack deterministic dompkg artifacts.")
    parser.add_argument("--input-root", default="")
    parser.add_argument("--input-file", action="append", default=[])
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest-json-out", default="")
    parser.add_argument("--pkg-id", required=True)
    parser.add_argument("--pkg-version", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--abi", default="native")
    parser.add_argument("--requires-capability", action="append", default=[])
    parser.add_argument("--provides-capability", action="append", default=[])
    parser.add_argument("--entitlement", action="append", default=[])
    parser.add_argument("--optional-capability", action="append", default=[])
    parser.add_argument("--compression", default="deflate", choices=["deflate", "none", "zstd"])
    parser.add_argument("--signature-json", default="")
    args = parser.parse_args()

    try:
        pairs = collect_inputs(args.input_root, args.input_file)
        packed = pack_package(
            input_pairs=pairs,
            output_pkg=args.out,
            pkg_id=args.pkg_id,
            pkg_version=args.pkg_version,
            platform=args.platform,
            arch=args.arch,
            abi=args.abi,
            requires_capabilities=args.requires_capability,
            provides_capabilities=args.provides_capability,
            entitlements=args.entitlement,
            optional_capabilities=args.optional_capability,
            compression=args.compression,
            signature_payload=load_signature(args.signature_json),
        )
        sidecar = args.manifest_json_out or (os.path.abspath(args.out) + ".manifest.json")
        os.makedirs(os.path.dirname(os.path.abspath(sidecar)), exist_ok=True)
        with open(sidecar, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(packed["manifest"], handle, indent=2, sort_keys=False)
            handle.write("\n")
        output = {
            "result": "ok",
            "pkg_path": packed["pkg_path"],
            "manifest_json": os.path.abspath(sidecar).replace("\\", "/"),
            "pkg_id": packed["manifest"]["pkg_id"],
            "pkg_version": packed["manifest"]["pkg_version"],
            "content_hash": packed["manifest"]["content_hash"],
            "file_count": packed["file_count"],
            "record_count": packed["record_count"],
        }
        print(json.dumps(output, indent=2))
        return 0
    except DomPkgError as exc:
        print(json.dumps(refusal_payload(exc.code, exc.message, exc.details), indent=2))
        return 3
    except Exception as exc:  # pragma: no cover
        print(json.dumps(refusal_payload("refuse.internal_error", "pack failed", {"error": str(exc)}), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
