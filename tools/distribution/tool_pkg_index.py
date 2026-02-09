#!/usr/bin/env python3
import argparse
import json
import os

from dompkg_lib import DomPkgError, read_manifest_only, refusal_payload, verify_package


def _iter_packages(root: str):
    for dirpath, _dirs, files in os.walk(root):
        files.sort()
        for name in files:
            if name.lower().endswith(".dompkg"):
                yield os.path.abspath(os.path.join(dirpath, name))


def _to_capability_refs(values):
    refs = []
    for value in sorted(set(values or [])):
        refs.append({"capability_id": value})
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate package index for dompkg artifacts.")
    parser.add_argument("--pkg-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--index-id", default="dominium.pkg.index")
    parser.add_argument("--index-version", default="1.0.0")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--tlv-out", default="")
    args = parser.parse_args()

    if not os.path.isdir(args.pkg_dir):
        print(json.dumps(refusal_payload("refuse.invalid_input", "pkg-dir missing", {"pkg_dir": args.pkg_dir}), indent=2))
        return 3

    entries = []
    try:
        for pkg_path in _iter_packages(args.pkg_dir):
            if args.verify:
                verify_package(pkg_path)
            manifest = read_manifest_only(pkg_path)
            file_exports = []
            for export in manifest.get("file_exports", []):
                file_exports.append({
                    "path": export.get("path"),
                    "sha256": export.get("sha256"),
                    "size_bytes": int(export.get("size_bytes", 0)),
                })
            rel_pkg = os.path.relpath(pkg_path, args.pkg_dir).replace("\\", "/")
            entries.append({
                "pkg_id": manifest.get("pkg_id"),
                "pkg_version": manifest.get("pkg_version"),
                "content_hash": manifest.get("content_hash"),
                "package_path": rel_pkg,
                "platform": manifest.get("platform"),
                "arch": manifest.get("arch"),
                "abi": manifest.get("abi"),
                "requires_capabilities": _to_capability_refs(manifest.get("requires_capabilities", [])),
                "provides_capabilities": _to_capability_refs(manifest.get("provides_capabilities", [])),
                "entitlements": _to_capability_refs(manifest.get("entitlements", [])),
                "file_exports": file_exports,
                "package_size_bytes": os.path.getsize(pkg_path),
            })
    except DomPkgError as exc:
        print(json.dumps(refusal_payload(exc.code, exc.message, exc.details), indent=2))
        return 3
    except Exception as exc:  # pragma: no cover
        print(json.dumps(refusal_payload("refuse.internal_error", "index generation failed", {"error": str(exc)}), indent=2))
        return 1

    entries.sort(key=lambda item: (item["pkg_id"], item["pkg_version"], item["content_hash"]))
    payload = {
        "index_id": args.index_id,
        "index_version": args.index_version,
        "packages": entries,
        "generated_at": "2000-01-01T00:00:00Z",
        "source_roots": [os.path.abspath(args.pkg_dir).replace("\\", "/")],
        "extensions": {},
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")

    if args.tlv_out:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        # type:u16 (1) + len:u32 + payload bytes
        tlv = (1).to_bytes(2, "little") + len(canonical).to_bytes(4, "little") + canonical
        os.makedirs(os.path.dirname(os.path.abspath(args.tlv_out)), exist_ok=True)
        with open(args.tlv_out, "wb") as handle:
            handle.write(tlv)

    print(json.dumps({
        "result": "ok",
        "index_path": os.path.abspath(args.out).replace("\\", "/"),
        "package_count": len(entries),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
