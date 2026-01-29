import argparse
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def require_tokens(path, tokens):
    text = read_text(path)
    text_l = text.lower()
    missing = [token for token in tokens if token.lower() not in text_l]
    if missing:
        raise AssertionError("{} missing tokens: {}".format(path, ", ".join(missing)))


def main() -> int:
    parser = argparse.ArgumentParser(description="SIGNAL-0 schema contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    field_schema = os.path.join(repo_root, "schema", "signal.field.schema")
    iface_schema = os.path.join(repo_root, "schema", "signal.interface.schema")
    signal_doc = os.path.join(repo_root, "docs", "architecture", "SIGNAL_MODEL.md")

    for path in (field_schema, iface_schema, signal_doc):
        if not os.path.isfile(path):
            raise AssertionError("missing required file: {}".format(path))

    require_tokens(field_schema, [
        "signal_id",
        "signal_type",
        "unit",
        "value_representation",
        "bandwidth",
        "noise_profile_ref",
        "latency_profile_ref",
        "sampling_policy",
        "unit_annotations",
        "extensions",
    ])
    require_tokens(iface_schema, [
        "interface_id",
        "signal_type",
        "directionality",
        "capacity",
        "impedance_class",
        "compatibility_rules",
        "unit_annotations",
        "extensions",
    ])
    require_tokens(signal_doc, [
        "discretely sampled",
        "Process",
        "macro capsules",
        "RNG stream",
    ])

    print("signal schema contracts OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
