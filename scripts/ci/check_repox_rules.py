#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys

from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings, normalize_path


AUTHORITATIVE_DIRS = (
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
)

FORBIDDEN_RNG_CALL_RE = re.compile(
    r"\b(rand|srand|rand_r|random|arc4random|drand48|lrand48|mrand48|getrandom|"
    r"BCryptGenRandom|RtlGenRandom|CryptGenRandom)\s*\("
)
FORBIDDEN_TIME_CALL_RE = re.compile(
    r"\b(time|clock|gettimeofday|clock_gettime|QueryPerformanceCounter|GetSystemTime|"
    r"GetTickCount|GetTickCount64|mach_absolute_time)\s*\("
)
FORBIDDEN_CHRONO_RE = re.compile(r"\bstd::chrono::|\bchrono::")
FORBIDDEN_FLOAT_RE = re.compile(r"\b(long\s+double|double|float)\b")

REVERSE_DNS_RE = re.compile(
    r'["\']([a-z][a-z0-9]+(?:\.[a-z0-9]+){2,}[a-z0-9]*)["\']',
    re.IGNORECASE,
)
ALLOWED_REVERSE_DNS_PREFIXES = (
    "noise.stream.",
    "rng.state.noise.stream.",
)

AMBIGUOUS_TOP_LEVEL = {
    "temp",
    "temps",
    "old",
    "misc",
    "stuff",
    "scratch",
    "junk",
    "backup",
    "bak",
    "unused",
}


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def load_allowed_top_level(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "REPO_INTENT.md")
    allowed = set()
    if not os.path.isfile(path):
        return allowed
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if "|" not in line:
                continue
            backticks = re.findall(r"`([^`]+)`", line)
            for item in backticks:
                name = item.strip().strip("/")
                if name:
                    allowed.add(name)
    return allowed


def check_top_level(repo_root, allowed):
    violations = []
    for entry in os.listdir(repo_root):
        if entry.startswith(".") and entry not in allowed:
            if entry in (".git",):
                continue
        full = os.path.join(repo_root, entry)
        if not os.path.isdir(full):
            continue
        if entry in AMBIGUOUS_TOP_LEVEL:
            violations.append(f"ambiguous top-level directory: {entry}")
        if entry not in allowed and not entry.startswith("."):
            violations.append(f"top-level directory not in REPO_INTENT: {entry}")
    return violations


ALLOWED_ARCHIVE_ROOTS = (
    "docs/archive",
    "legacy",
    "labs",
    "tmp",
)


def check_archived_paths(repo_root):
    manifest_path = os.path.join(repo_root, "tests", "contract", "archive_manifest.json")
    if not os.path.isfile(manifest_path):
        return ["missing archive manifest: tests/contract/archive_manifest.json"]
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    violations = []
    for entry in manifest.get("archives", []):
        rel_path = entry.get("path", "")
        if not rel_path:
            continue
        norm = normalize_path(rel_path)
        if not any(norm == root or norm.startswith(root + "/") for root in ALLOWED_ARCHIVE_ROOTS):
            violations.append(f"archived path not under archive/quarantine: {rel_path}")
    return violations


def check_forbidden_symbols(repo_root):
    violations = []
    exts = [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, exts):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                if FORBIDDEN_RNG_CALL_RE.search(line):
                    violations.append(f"{rel}:{idx}: forbidden RNG call")
                if FORBIDDEN_TIME_CALL_RE.search(line) or FORBIDDEN_CHRONO_RE.search(line):
                    violations.append(f"{rel}:{idx}: forbidden time call")
                if FORBIDDEN_FLOAT_RE.search(line):
                    violations.append(f"{rel}:{idx}: forbidden floating point")
            # content id scan on raw text (strings)
            for match in REVERSE_DNS_RE.finditer(text):
                token = match.group(1)
                token_l = token.lower()
                if token_l.startswith(ALLOWED_REVERSE_DNS_PREFIXES):
                    continue
                violations.append(f"{rel}: content id literal '{token}'")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX governance rules enforcement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    allowed = load_allowed_top_level(repo_root)
    violations.extend(check_top_level(repo_root, allowed))
    violations.extend(check_archived_paths(repo_root))
    violations.extend(check_forbidden_symbols(repo_root))

    if violations:
        for item in sorted(violations):
            print(item)
        return 1

    print("RepoX governance rules OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
