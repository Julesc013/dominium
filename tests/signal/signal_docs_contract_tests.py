import argparse
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def require_tokens(path, tokens):
    text = read_text(path)
    missing = [token for token in tokens if token not in text]
    if missing:
        raise AssertionError("{} missing tokens: {}".format(path, ", ".join(missing)))


def main() -> int:
    parser = argparse.ArgumentParser(description="SIGNAL-0 docs contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    arch_doc = os.path.join(repo_root, "docs", "architecture", "SIGNAL_MODEL.md")
    content_doc = os.path.join(repo_root, "docs", "content", "SIGNALS_AND_COMPUTATION.md")

    for path in (arch_doc, content_doc):
        if not os.path.isfile(path):
            raise AssertionError("missing required doc: {}".format(path))

    require_tokens(arch_doc, [
        "No continuous-time integration",
        "Process",
        "discretely sampled",
    ])
    require_tokens(content_doc, [
        "not",
        "SPICE",
        "micro-time",
        "data-driven",
    ])

    print("signal docs contracts OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
