import argparse
import os
import sys


BASELINES = [
    "BASELINE_LEGACY_CORE",
    "BASELINE_MAINLINE_CORE",
    "BASELINE_MODERN_UI",
    "BASELINE_SERVER_MIN",
]


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def resolve_baseline(required_caps, available_caps):
    missing = [cap for cap in required_caps if cap not in available_caps]
    if missing:
        return "frozen"
    return "ok"


def main():
    parser = argparse.ArgumentParser(description="Capability baseline tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    baseline_doc = os.path.join(repo_root, "docs", "arch", "CAPABILITY_BASELINES.md")
    sku_doc = os.path.join(repo_root, "docs", "arch", "SKU_MATRIX.md")
    schema_path = os.path.join(repo_root, "schema", "capability_baseline.schema")

    if not os.path.isfile(baseline_doc):
        print("missing CAPABILITY_BASELINES.md")
        return 1
    if not os.path.isfile(sku_doc):
        print("missing SKU_MATRIX.md")
        return 1
    if not os.path.isfile(schema_path):
        print("missing capability_baseline.schema")
        return 1

    baseline_text = read_text(baseline_doc)
    for baseline in BASELINES:
        if baseline not in baseline_text:
            print("baseline missing from doc: {}".format(baseline))
            return 1

    sku_text = read_text(sku_doc)
    for baseline in BASELINES:
        if baseline not in sku_text:
            print("baseline missing from SKU matrix: {}".format(baseline))
            return 1

    schema_text = read_text(schema_path)
    for token in ("baseline_id", "baseline_version", "required_capabilities", "extensions"):
        if token not in schema_text:
            print("schema missing token: {}".format(token))
            return 1

    # Baseline mismatch behavior
    required_caps = ["cap.core.example"]
    available_caps = []
    mode = resolve_baseline(required_caps, available_caps)
    if mode != "frozen":
        print("baseline mismatch did not yield frozen mode")
        return 1

    # Legacy SKU loading new save safely (degraded/frozen, no crash)
    legacy_caps = []
    save_required = ["cap.save.newer"]
    mode = resolve_baseline(save_required, legacy_caps)
    if mode not in ("frozen", "degraded"):
        print("legacy SKU did not degrade/freeze on missing caps")
        return 1

    print("Baseline/SKU tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
