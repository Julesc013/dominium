#!/usr/bin/env python3
import argparse
import re
import sys

from hygiene_utils import CODE_EXTS, DEFAULT_EXCLUDES, DEFAULT_ROOTS, expand_list, iter_files, read_text, strip_c_comments_and_strings, normalize_path

ENUM_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_]*(CUSTOM|OTHER|UNKNOWN|MISC|UNSPECIFIED)[A-Za-z0-9_]*\b")


def scan_file(path, text):
    stripped = strip_c_comments_and_strings(text)
    lines = stripped.split("\n")
    findings = []
    in_enum = False
    pending_enum = False
    brace_depth = 0
    for idx, line in enumerate(lines, start=1):
        if "HYGIENE_ALLOW_UNKNOWN_ENUM" in line or "PARSER_ONLY_UNKNOWN" in line:
            continue
        if not in_enum:
            if pending_enum:
                if "{" in line:
                    in_enum = True
                    pending_enum = False
                    brace_depth += line.count("{") - line.count("}")
            elif re.search(r"\benum\b", line):
                if "{" in line:
                    in_enum = True
                    brace_depth += line.count("{") - line.count("}")
                else:
                    pending_enum = True
            continue

        for match in ENUM_TOKEN_RE.finditer(line):
            findings.append((path, idx, match.group(0)))

        brace_depth += line.count("{") - line.count("}")
        if brace_depth <= 0:
            in_enum = False
            pending_enum = False
            brace_depth = 0
    return findings


def main():
    parser = argparse.ArgumentParser(description="Detect forbidden enum values.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--mode", choices=["warn", "fail"], default="fail")
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
        prefix = "FORBIDDEN-ENUM FAIL" if args.mode == "fail" else "FORBIDDEN-ENUM WARN"
        for path, line, token in findings:
            rel = normalize_path(path)
            print(f"{rel}:{line}: {prefix}: token={token}")
        if args.mode == "fail":
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
