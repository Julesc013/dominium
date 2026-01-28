import argparse
import os
import re
import sys
from typing import List, Tuple


EXPECTED_CODES: List[Tuple[int, str]] = [
    (1, "REFUSE_INVALID_INTENT"),
    (2, "REFUSE_LAW_FORBIDDEN"),
    (3, "REFUSE_CAPABILITY_MISSING"),
    (4, "REFUSE_DOMAIN_FORBIDDEN"),
    (5, "REFUSE_INTEGRITY_VIOLATION"),
    (6, "REFUSE_RATE_LIMIT"),
    (7, "REFUSE_BUDGET_EXCEEDED"),
    (701, "REFUSE_ACTIVE_DOMAIN_LIMIT"),
    (702, "REFUSE_REFINEMENT_BUDGET"),
    (703, "REFUSE_MACRO_EVENT_BUDGET"),
    (704, "REFUSE_AGENT_PLANNING_BUDGET"),
    (705, "REFUSE_SNAPSHOT_BUDGET"),
    (706, "REFUSE_COLLAPSE_BUDGET"),
    (707, "REFUSE_DEFER_QUEUE_LIMIT"),
    (1001, "WD-REFUSAL-INVALID"),
    (1002, "WD-REFUSAL-SCHEMA"),
    (1003, "WD-REFUSAL-CAPABILITY"),
    (1004, "WD-REFUSAL-TEMPLATE"),
]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_refusal_block(text: str) -> List[Tuple[int, str]]:
    start = text.find("```refusal-codes")
    if start == -1:
        return []
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return []
    codes: List[Tuple[int, str]] = []
    for raw_line in text[start:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",", 2)]
        if len(parts) < 2:
            continue
        try:
            code_id = int(parts[0])
        except ValueError:
            continue
        codes.append((code_id, parts[1]))
    return codes


def extract_tokens(text: str, pattern: str) -> List[str]:
    return sorted(set(re.findall(pattern, text)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Refusal code stability checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    refusal_doc = os.path.join(repo_root, "docs", "arch", "REFUSAL_SEMANTICS.md")
    refusal_spec = os.path.join(repo_root, "schema", "integrity", "SPEC_REFUSAL_CODES.md")

    if not os.path.isfile(refusal_doc):
        print("missing refusal doc: {}".format(refusal_doc))
        return 1

    doc_text = read_text(refusal_doc)
    codes = parse_refusal_block(doc_text)
    if not codes:
        print("missing refusal-codes block")
        return 1
    if codes != EXPECTED_CODES:
        print("refusal code list mismatch")
        return 1

    ids = [code_id for code_id, _code in codes]
    if len(ids) != len(set(ids)):
        print("duplicate refusal code ids")
        return 1
    if any(code_id <= 0 or code_id > 4096 for code_id in ids):
        print("refusal code ids outside small integer range")
        return 1

    if os.path.isfile(refusal_spec):
        spec_text = read_text(refusal_spec)
        spec_codes = extract_tokens(spec_text, r"REFUSE_[A-Z0-9_]+")
        canonical_tokens = {code for _code_id, code in codes}
        for token in spec_codes:
            if token not in canonical_tokens:
                print("refusal token missing from canonical list: {}".format(token))
                return 1

    print("Refusal code stability OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
