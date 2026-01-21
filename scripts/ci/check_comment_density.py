#!/usr/bin/env python3
import argparse
import os
import re
import sys

from hygiene_utils import CODE_EXTS, DEFAULT_EXCLUDES, DEFAULT_ROOTS, expand_list, iter_files, read_text, normalize_path

PUBLIC_HEADER_ROOTS = [
    os.path.join("engine", "include"),
    os.path.join("game", "include"),
    os.path.join("libs", "contracts", "include"),
]

FUNC_DECL_RE = re.compile(r"^\s*[A-Za-z_][\w\s\*]*\b[A-Za-z_]\w*\s*\([^;]*\)\s*;")


def count_comment_lines(text):
    lines = text.split("\n")
    total = 0
    comment_lines = 0
    in_block = False
    for line in lines:
        if not line.strip():
            continue
        total += 1
        i = 0
        has_comment = False
        while i < len(line):
            ch = line[i]
            nxt = line[i + 1] if i + 1 < len(line) else ""
            if in_block:
                has_comment = True
                end = line.find("*/", i)
                if end == -1:
                    break
                in_block = False
                i = end + 2
                continue
            if ch == "/" and nxt == "/":
                has_comment = True
                break
            if ch == "/" and nxt == "*":
                has_comment = True
                in_block = True
                i += 2
                continue
            i += 1
        if has_comment:
            comment_lines += 1
    return total, comment_lines


def has_header_block(text):
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        return stripped.startswith("/*") or stripped.startswith("//")
    return False


def is_public_header(path):
    path_norm = normalize_path(path).lower()
    for root in PUBLIC_HEADER_ROOTS:
        root_norm = normalize_path(root).lower()
        if path_norm.startswith(root_norm):
            return True
    return False


def scan_public_function_docs(path, text):
    findings = []
    lines = text.split("\n")
    for idx, line in enumerate(lines, start=1):
        if not FUNC_DECL_RE.match(line):
            continue
        prior = "\n".join(lines[max(0, idx - 3): idx])
        if "Purpose:" in prior or "DOC:" in prior or "INVARIANT:" in prior:
            continue
        findings.append((path, idx, "MISSING_FUNC_DOC"))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Check comment density and doc blocks.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--min-ratio", type=float, default=0.30)
    parser.add_argument("--mode", choices=["warn", "fail"], default="warn")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    roots = expand_list(args.roots, DEFAULT_ROOTS)
    excludes = expand_list(args.exclude, DEFAULT_EXCLUDES)
    files = iter_files(roots, excludes, CODE_EXTS)

    findings = []
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        if not has_header_block(text):
            findings.append((path, 1, "MISSING_FILE_HEADER"))

        if is_public_header(path):
            findings.extend(scan_public_function_docs(path, text))

        if "COMMENT_DENSITY_EXCEPTION" in text:
            continue

        total, comments = count_comment_lines(text)
        ratio = (comments / total) if total else 0.0
        if not args.quiet:
            rel = normalize_path(path)
            print(f"FILE {rel} lines={total} comment_lines={comments} ratio={ratio:.4f}")
        if total and ratio < args.min_ratio:
            findings.append((path, 1, "LOW_COMMENT_RATIO"))

    if findings:
        prefix = "COMMENT-DENSITY FAIL" if args.mode == "fail" else "COMMENT-DENSITY WARN"
        for path, line, kind in findings:
            rel = normalize_path(path)
            print(f"{rel}:{line}: {prefix}: {kind}")
        if args.mode == "fail":
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
