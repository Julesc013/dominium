#!/usr/bin/env python3
import argparse
import re
import sys

from hygiene_utils import TEXT_EXTS, DEFAULT_EXCLUDES, DEFAULT_ROOTS, expand_list, iter_files, read_text, normalize_path

TODO_RE = re.compile(r"TODO_(BLOCKER|FUTURE|DOC)\(([A-Za-z0-9_.-]+)\)")


def load_known_blockers(path):
    blockers = {}
    text = read_text(path)
    if text is None:
        return blockers
    current_id = None
    for idx, line in enumerate(text.split("\n"), start=1):
        if line.startswith("ID:"):
            current_id = line.split("ID:", 1)[1].strip()
            if current_id:
                blockers[current_id] = {"line": idx, "doc_only": False}
            continue
        if current_id and "doc-only" in line.lower():
            blockers[current_id]["doc_only"] = True
    return blockers


def main():
    parser = argparse.ArgumentParser(description="Enforce TODO_BLOCKER/TODO_FUTURE/TODO_DOC policy.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--mode", choices=["warn", "fail"], default="fail")
    parser.add_argument("--known-blockers", default="docs/ci/KNOWN_BLOCKERS.md")
    args = parser.parse_args()

    roots = expand_list(args.roots, DEFAULT_ROOTS)
    excludes = expand_list(args.exclude, DEFAULT_EXCLUDES)
    files = iter_files(roots, excludes, TEXT_EXTS)

    blockers = load_known_blockers(args.known_blockers)
    referenced_blockers = set()
    findings = []

    for path in files:
        text = read_text(path)
        if text is None:
            continue
        for idx, line in enumerate(text.split("\n"), start=1):
            if "TODO" not in line:
                continue
            match = TODO_RE.search(line)
            if not match:
                findings.append((path, idx, "RAW_TODO", line.strip()))
                continue
            kind, todo_id = match.group(1), match.group(2)
            if kind == "BLOCKER":
                referenced_blockers.add(todo_id)
                if todo_id not in blockers:
                    findings.append((path, idx, "UNKNOWN_BLOCKER", todo_id))
            elif kind == "FUTURE":
                if "FUTURE_PROOFING" not in line:
                    findings.append((path, idx, "FUTURE_MISSING_REF", todo_id))
            elif kind == "DOC":
                if "docs/" not in line and ".md" not in line:
                    findings.append((path, idx, "DOC_MISSING_REF", todo_id))

    for blocker_id, meta in sorted(blockers.items()):
        if blocker_id not in referenced_blockers and not meta["doc_only"]:
            findings.append((args.known_blockers, meta["line"], "BLOCKER_NO_CODE_REF", blocker_id))

    if findings:
        prefix = "TODO FAIL" if args.mode == "fail" else "TODO WARN"
        for path, line, kind, detail in findings:
            rel = normalize_path(path)
            print(f"{rel}:{line}: {prefix}: {kind} {detail}")
        if args.mode == "fail":
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
