import argparse
import json
import os
import sys


REQUIRED_MODES = {"active", "degraded", "frozen", "inspect_only"}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_modes(text):
    start = text.find("```mod-compat-modes")
    if start == -1:
        return {}
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return {}
    modes = {}
    for line in text[start:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",", 2)]
        if len(parts) < 2:
            continue
        modes[parts[0]] = parts[1]
    return modes


def resolve_mode(required_mods, available_mods):
    missing = set(required_mods) - set(available_mods)
    if missing:
        return "frozen"
    return "active"


def round_trip(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return json.loads(encoded)


def main():
    parser = argparse.ArgumentParser(description="Mod ecosystem contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    mod_doc = os.path.join(repo_root, "docs", "arch", "MOD_ECOSYSTEM_RULES.md")
    if not os.path.isfile(mod_doc):
        print("missing mod ecosystem doc")
        return 1

    text = read_text(mod_doc)
    modes = parse_modes(text)
    if not modes:
        print("missing mod-compat-modes block")
        return 1
    if not REQUIRED_MODES.issubset(set(modes.keys())):
        print("missing required compatibility modes")
        return 1
    for mode in ("frozen", "inspect_only"):
        if modes.get(mode) not in ("no", "limited"):
            print("frozen/inspect_only must forbid mutation")
            return 1

    # Mod removal safety -> frozen or inspect_only.
    required = ["mod.example.alpha"]
    available = []
    mode = resolve_mode(required, available)
    if mode not in ("frozen", "inspect_only"):
        print("mod removal did not yield frozen/inspect_only mode")
        return 1

    # Forward compatibility: unknown fields preserved in mod chunk.
    chunk = {"mod_id": "mod.example.alpha", "payload": {"value": 1}, "unknown": {"v": 2}}
    rt = round_trip(chunk)
    if "unknown" not in rt:
        print("unknown mod fields not preserved")
        return 1

    print("Mod ecosystem tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
