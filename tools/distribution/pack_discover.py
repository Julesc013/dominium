import argparse
import json
import os

from distribution_lib import (
    discover_pack_manifests,
    make_refusal,
    pack_sort_key,
    REFUSAL_INTEGRITY,
)


def main():
    parser = argparse.ArgumentParser(description="Discover pack manifests under a root directory.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--engine-pack-format", type=int, default=0)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    roots = args.root if args.root else ["data/packs"]

    packs = discover_pack_manifests(roots, repo_root)
    incompatible = []
    if args.engine_pack_format > 0:
        for pack in packs:
            fmt = pack.get("pack_format_version")
            if isinstance(fmt, int) and fmt > args.engine_pack_format:
                pack["compat"] = "incompatible"
                pack["refusal"] = make_refusal(*REFUSAL_INTEGRITY,
                                               "unsupported pack format",
                                               {"pack_id": pack.get("pack_id"),
                                                "pack_format_version": fmt,
                                                "engine_pack_format": args.engine_pack_format})
                incompatible.append(pack)
            else:
                pack["compat"] = "ok"
                pack["refusal"] = None

    packs.sort(key=pack_sort_key)

    if args.format == "json":
        payload = {
            "ok": True,
            "packs": packs,
            "incompatible_packs": incompatible,
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("pack_discover: packs={}".format(len(packs)))
    for pack in packs:
        line = "{pack_id} {pack_version} {manifest_relpath}".format(**pack)
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
