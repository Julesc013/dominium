#!/usr/bin/env python3
import argparse
import re
import sys

from hygiene_utils import CODE_EXTS, DEFAULT_EXCLUDES, DEFAULT_ROOTS, expand_list, iter_files, read_text, strip_c_comments_and_strings, normalize_path

NUM_RE = re.compile(r"(?<![A-Za-z0-9_])(-?(?:0x[0-9A-Fa-f]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))(?:[uUlLfF]*)")


def is_allowed_literal(raw):
    raw = raw.lower()
    if raw in ("0", "1", "-1"):
        return True
    if raw in ("0u", "1u", "-1u", "0ul", "1ul", "-1l", "-1ul"):
        return True
    if raw.startswith("0x"):
        return False
    if "." in raw or "e" in raw:
        return False
    return False


def line_allows_numbers(line):
    if "MAGIC_NUMBER_OK" in line:
        return True
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return True
    if re.search(r"\b(const|constexpr|enum)\b", line):
        return True
    if re.search(r"^\s*#\s*define\b", line):
        return True
    return False


def scan_file(path, text):
    if "MAGIC_NUMBER_FILE_OK" in text:
        return []
    clean = strip_c_comments_and_strings(text)
    lines = clean.split("\n")
    findings = []
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if line_allows_numbers(line):
            continue
        for match in NUM_RE.finditer(line):
            literal = match.group(1)
            if is_allowed_literal(literal):
                continue
            findings.append((path, idx, literal.strip()))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Detect magic numbers in code.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--mode", choices=["warn", "fail"], default="warn")
    args = parser.parse_args()

    roots = expand_list(args.roots, DEFAULT_ROOTS)
    excludes = expand_list(args.exclude, DEFAULT_EXCLUDES)

    files = iter_files(roots, excludes, CODE_EXTS)
    findings = []
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        findings.extend(scan_file(path, text))

    if findings:
        prefix = "MAGIC-NUMBER FAIL" if args.mode == "fail" else "MAGIC-NUMBER WARN"
        for path, line, literal in findings:
            rel = normalize_path(path)
            print(f"{rel}:{line}: {prefix}: literal={literal}")
        if args.mode == "fail":
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
