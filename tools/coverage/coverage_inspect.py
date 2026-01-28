import argparse
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "distribution")))

from distribution_lib import discover_pack_manifests  # noqa: E402


LEVEL_RE = re.compile(r"^\|\s*(C-[A-Z])\s*\|")


def extract_capabilities(entries):
    out = []
    for entry in entries or []:
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if isinstance(cap_id, str):
            out.append(cap_id)
    return out


def parse_coverage_table(text):
    levels = {}
    for raw in text.splitlines():
        if not raw.startswith("|"):
            continue
        if raw.strip().startswith("| ---"):
            continue
        match = LEVEL_RE.match(raw)
        if not match:
            continue
        parts = [p.strip() for p in raw.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        level = parts[0]
        cap_cell = parts[3]
        caps = [cap.strip() for cap in cap_cell.split("<br>") if cap.strip()]
        levels[level] = {
            "required_capabilities": sorted(caps),
        }
    return levels


def load_coverage_levels(repo_root):
    path = os.path.join(repo_root, "docs", "roadmap", "SIMULATION_COVERAGE_LADDER.md")
    if not os.path.isfile(path):
        return {}
    text = open(path, "r", encoding="utf-8", errors="replace").read()
    return parse_coverage_table(text)


def parse_maturity(pack_root):
    readme = os.path.join(pack_root, "docs", "README.md")
    if not os.path.isfile(readme):
        return None
    for raw in open(readme, "r", encoding="utf-8", errors="replace"):
        line = raw.strip()
        if line.lower().startswith("maturity:"):
            return line.split(":", 1)[1].strip().rstrip(".").upper()
    return None


def selection_from_ids(all_packs, ids):
    pack_map = {pack.get("pack_id"): pack for pack in all_packs}
    selected = []
    missing = []
    for pack_id in ids:
        pack = pack_map.get(pack_id)
        if pack:
            selected.append(pack)
        else:
            missing.append(pack_id)
    return selected, sorted(missing)


def main():
    parser = argparse.ArgumentParser(description="Inspect coverage ladder status.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pack-id", action="append", default=[])
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    levels = load_coverage_levels(repo_root)
    all_packs = discover_pack_manifests(["data/packs", "data/worldgen"], repo_root)

    if args.pack_id:
        selected, missing = selection_from_ids(all_packs, args.pack_id)
    else:
        selected = all_packs
        missing = []

    provided = sorted(set(cap for pack in selected for cap in pack.get("provides") or []))
    provider_map = {}
    for pack in selected:
        for cap in pack.get("provides") or []:
            provider_map.setdefault(cap, []).append(pack.get("pack_id"))
    for cap in provider_map:
        provider_map[cap] = sorted(set(provider_map[cap]))

    maturity_counts = {"PARAMETRIC": 0, "STRUCTURAL": 0, "BOUNDED": 0, "INCOMPLETE": 0, "UNKNOWN": 0}
    pack_roots = []
    for pack in selected:
        root = pack.get("root")
        manifest_rel = pack.get("manifest_relpath")
        if root and manifest_rel:
            pack_root = os.path.abspath(os.path.join(repo_root, root, os.path.dirname(manifest_rel)))
            pack_roots.append(pack_root)
    for pack_root in sorted(set(pack_roots)):
        label = parse_maturity(pack_root) or "UNKNOWN"
        if label not in maturity_counts:
            maturity_counts["UNKNOWN"] += 1
        else:
            maturity_counts[label] += 1

    level_status = {}
    for level, data in sorted(levels.items()):
        required = data.get("required_capabilities", [])
        missing_caps = [cap for cap in required if cap not in provided]
        status = "UNSUPPORTED"
        if required:
            if len(missing_caps) == 0:
                status = "COMPLETE"
            elif len(missing_caps) < len(required):
                status = "PARTIAL"
        level_status[level] = {
            "status": status,
            "required_capabilities": required,
            "missing_capabilities": missing_caps,
            "providers": {cap: provider_map.get(cap, []) for cap in required},
        }

    output = {
        "ok": True,
        "selection": {
            "pack_count": len(selected),
            "missing_packs": missing,
        },
        "levels": level_status,
        "provided_capabilities": provided,
        "maturity_counts": maturity_counts,
    }

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("coverage_inspect: packs={}".format(len(selected)))
    for level, data in level_status.items():
        print("{}={}".format(level, data["status"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
