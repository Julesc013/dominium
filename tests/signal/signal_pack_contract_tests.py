import argparse
import json
import os
import sys


PACK_ID = "org.dominium.core.signals.basic"

REQUIRED_PROCESS_IDS = [
    "org.dominium.process.signal.sample",
    "org.dominium.process.signal.route",
    "org.dominium.process.signal.threshold",
    "org.dominium.process.signal.filter",
    "org.dominium.process.signal.integrate",
    "org.dominium.process.signal.modulate",
    "org.dominium.process.signal.demodulate",
    "org.dominium.process.signal.quantize",
    "org.dominium.process.signal.record",
    "org.dominium.process.signal.compare",
    "org.dominium.process.signal.encrypt",
    "org.dominium.process.signal.decrypt",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_numbers(value, path="root", out=None):
    if out is None:
        out = []
    if isinstance(value, dict):
        for key, val in value.items():
            collect_numbers(val, path + "." + str(key), out)
    elif isinstance(value, list):
        for idx, val in enumerate(value):
            collect_numbers(val, path + "[{}]".format(idx), out)
    elif isinstance(value, float):
        out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="SIGNAL-0 pack contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_root = os.path.join(repo_root, "data", "packs", PACK_ID)
    if not os.path.isdir(pack_root):
        print("missing pack root: {}".format(PACK_ID))
        return 1

    pack_toml = os.path.join(pack_root, "pack.toml")
    pack_manifest = os.path.join(pack_root, "pack_manifest.json")
    signals_path = os.path.join(pack_root, "data", "signals.json")
    fab_path = os.path.join(pack_root, "data", "fab_pack.json")
    docs_readme = os.path.join(pack_root, "docs", "README.md")

    for path in (pack_toml, pack_manifest, signals_path, fab_path, docs_readme):
        if not os.path.isfile(path):
            print("missing required file: {}".format(path))
            return 1

    signals = load_json(signals_path)
    if "signals" not in signals or "signal_interfaces" not in signals:
        print("signals.json missing required keys")
        return 1

    if not signals.get("signals"):
        print("signals.json missing signal entries")
        return 1

    if not signals.get("signal_interfaces"):
        print("signals.json missing signal_interfaces entries")
        return 1

    fab = load_json(fab_path)
    processes = fab.get("process_families") or []
    ids = {entry.get("process_family_id") for entry in processes if isinstance(entry, dict)}
    missing = [pid for pid in REQUIRED_PROCESS_IDS if pid not in ids]
    if missing:
        print("missing required process families: {}".format(", ".join(missing)))
        return 1

    float_hits = collect_numbers(signals)
    float_hits.extend(collect_numbers(fab))
    if float_hits:
        print("floating point literals found in signal pack:")
        for hit in float_hits:
            print("  {}".format(hit))
        return 1

    print("signal pack contracts OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
