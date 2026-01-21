#!/usr/bin/env python3
import argparse
import re
import sys

from hygiene_utils import CODE_EXTS, DEFAULT_EXCLUDES, DEFAULT_ROOTS, expand_list, iter_files, read_text, strip_c_comments_and_strings, normalize_path

SUSPECT_TOKENS = [
    "type",
    "kind",
    "class",
    "category",
    "mode",
    "target",
    "capability",
    "resource",
    "material",
    "damage",
    "biome",
    "tech",
    "module",
    "item",
    "law",
    "_id",
]

ALLOW_TOKENS = [
    "execution_phase",
    "determinism",
    "det_class",
    "authority_layer",
    "existence_state",
    "law_result",
]


def find_switches(text):
    switches = []
    i = 0
    while i < len(text):
        m = re.search(r"\bswitch\s*\(", text[i:])
        if not m:
            break
        start = i + m.start()
        paren_start = i + m.end() - 1
        depth = 0
        j = paren_start
        while j < len(text):
            ch = text[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    expr = text[paren_start + 1 : j]
                    line = text[:start].count("\n") + 1
                    switches.append((line, expr))
                    i = j + 1
                    break
            j += 1
        else:
            break
    return switches


def is_suspect(expr):
    expr_l = expr.lower()
    for allow in ALLOW_TOKENS:
        if allow in expr_l:
            return False
    for token in SUSPECT_TOKENS:
        if token in expr_l:
            return True
    return False


def scan_file(path, text):
    clean = strip_c_comments_and_strings(text)
    lines = text.split("\n")
    findings = []
    for line, expr in find_switches(clean):
        marker_ok = False
        for idx in range(max(0, line - 2), min(len(lines), line + 1)):
            if "HYGIENE_TAXONOMY_SWITCH_OK" in lines[idx]:
                marker_ok = True
                break
        if marker_ok:
            continue
        if is_suspect(expr):
            findings.append((path, line, expr.strip()))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Detect switch statements over taxonomy ids/types.")
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
        prefix = "SWITCH-TAXONOMY FAIL" if args.mode == "fail" else "SWITCH-TAXONOMY WARN"
        for path, line, expr in findings:
            rel = normalize_path(path)
            print(f"{rel}:{line}: {prefix}: switch({expr})")
        if args.mode == "fail":
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
