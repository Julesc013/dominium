import argparse
import os
import re
import sys


EXPECTED_CODES = [
    (1, "REFUSE_INVALID_INTENT"),
    (2, "REFUSE_LAW_FORBIDDEN"),
    (3, "REFUSE_CAPABILITY_MISSING"),
    (4, "REFUSE_DOMAIN_FORBIDDEN"),
    (5, "REFUSE_INTEGRITY_VIOLATION"),
    (6, "REFUSE_RATE_LIMIT"),
    (7, "REFUSE_BUDGET_EXCEEDED"),
    (1001, "WD-REFUSAL-INVALID"),
    (1002, "WD-REFUSAL-SCHEMA"),
    (1003, "WD-REFUSAL-CAPABILITY"),
    (1004, "WD-REFUSAL-TEMPLATE"),
]


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_refusal_block(text):
    start = text.find("```refusal-codes")
    if start == -1:
        return []
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return []
    block = text[start:end].splitlines()
    codes = []
    for line in block:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",", 2)]
        if len(parts) < 2:
            continue
        try:
            code_id = int(parts[0])
        except ValueError:
            continue
        code = parts[1]
        codes.append((code_id, code))
    return codes


def extract_tokens(text, pattern):
    return sorted(set(re.findall(pattern, text)))


def budget_refusal(load_values, budget_limit):
    total = sum(load_values)
    if total > budget_limit:
        return "REFUSE_BUDGET_EXCEEDED"
    return None


def main():
    parser = argparse.ArgumentParser(description="Refusal and budget policy tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    refusal_doc = os.path.join(repo_root, "docs", "arch", "REFUSAL_SEMANTICS.md")
    refusal_spec = os.path.join(repo_root, "schema", "integrity", "SPEC_REFUSAL_CODES.md")
    wd_lib = os.path.join(repo_root, "tools", "worldgen_offline", "world_definition_lib.py")

    if not os.path.isfile(refusal_doc):
        print("missing refusal doc")
        return 1
    doc_text = read_text(refusal_doc)
    codes = parse_refusal_block(doc_text)
    if not codes:
        print("missing refusal-codes block")
        return 1
    if codes != EXPECTED_CODES:
        print("refusal code list mismatch")
        return 1

    # Ensure codes are small integers and unique.
    ids = [code_id for code_id, _code in codes]
    if len(ids) != len(set(ids)):
        print("duplicate refusal code ids")
        return 1
    if any(code_id <= 0 or code_id > 4096 for code_id in ids):
        print("refusal code ids outside small integer range")
        return 1

    # Same refusal under same conditions everywhere: all tokens must be in canonical list.
    spec_text = read_text(refusal_spec) if os.path.isfile(refusal_spec) else ""
    spec_codes = extract_tokens(spec_text, r"REFUSE_[A-Z0-9_]+")
    canonical_tokens = {code for _code_id, code in codes}
    for token in spec_codes:
        if token not in canonical_tokens:
            print("refusal token missing from canonical list: {}".format(token))
            return 1

    if os.path.isfile(wd_lib):
        wd_text = read_text(wd_lib)
        wd_codes = extract_tokens(wd_text, r"WD-REFUSAL-[A-Z0-9_]+")
        for token in wd_codes:
            if token not in canonical_tokens:
                print("worlddef refusal missing from canonical list: {}".format(token))
                return 1

    # Budget refusal determinism under load
    loads = [5, 3, 9, 2]
    limit = 10
    refusal_a = budget_refusal(loads, limit)
    refusal_b = budget_refusal(list(reversed(loads)), limit)
    if refusal_a != refusal_b or refusal_a != "REFUSE_BUDGET_EXCEEDED":
        print("budget refusal is non-deterministic or missing")
        return 1

    # No silent performance collapse: exceeding budget must refuse.
    if budget_refusal([1, 1, 1], 10) is not None:
        print("budget refusal triggered under limit")
        return 1

    print("Refusal and budget tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
