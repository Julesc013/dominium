#!/usr/bin/env python3
from __future__ import print_function

import os
import re
import sys


SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".inc", ".ipp",
}

SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "docs",
    "schema",
    "third_party",
    "external",
    "deps",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')

FORBIDDEN_GAME_INCLUDES = (
    "engine/modules/",
    "execution/scheduler/",
    "execution/scheduler_iface.h",
    "scheduler_single_thread",
    "scheduler_parallel",
)

FORBIDDEN_THREAD_HEADERS = (
    "thread",
    "pthread.h",
)

THREAD_CALL_RE = re.compile(
    r"\b(std::thread|std::async|pthread_create|CreateThread|_beginthread|_beginthreadex)\b"
)

IR_ONLY_MARKER_RE = re.compile(r"\bIR_ONLY\b")
LEGACY_CALL_RE = re.compile(r"\blegacy\w*\s*\(")

TASK_NODE_TOKEN_RE = re.compile(r"\bdom_task_node\b")
REQUIRED_TASK_TOKENS = (
    ".determinism_class",
    ".access_set_id",
    ".cost_model_id",
    ".phase_id",
    ".commit_key",
)
REQUIRED_LAW_TOKEN = ".law_targets"
AUTHORITATIVE_TOKEN = "DOM_TASK_AUTHORITATIVE"


class Check(object):
    def __init__(self, check_id, description, remediation):
        self.check_id = check_id
        self.description = description
        self.remediation = remediation
        self.violations = []

    def add_violation(self, path, line, detail):
        self.violations.append((path, line, detail))

    def report(self):
        if not self.violations:
            return False
        print("{0}: {1}".format(self.check_id, self.description))
        for path, line, detail in sorted(self.violations):
            print("  {0}:{1}: {2}".format(path, line, detail))
        print("Fix: {0}".format(self.remediation))
        return True


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def read_text(path):
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except IOError:
        return ""
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = data.decode("latin-1", errors="ignore")
    if "\x00" in text:
        text = text.replace("\x00", "")
    return text


def iter_source_files(root, repo_root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = repo_rel(repo_root, dirpath)
        parts = rel.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in SOURCE_EXTS:
                continue
            yield os.path.join(dirpath, filename)


def iter_include_lines(text):
    for idx, line in enumerate(text.splitlines(), start=1):
        match = INCLUDE_RE.match(line)
        if match:
            yield idx, match.group(1).replace("\\", "/")


def iter_code_lines(text):
    in_block = False
    in_string = None
    for idx, line in enumerate(text.splitlines(), start=1):
        i = 0
        out = ""
        while i < len(line):
            ch = line[i]
            nxt = line[i:i + 2]
            if in_block:
                if nxt == "*/":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue
            if in_string:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_string:
                    in_string = None
                i += 1
                continue
            if nxt == "//":
                break
            if nxt == "/*":
                in_block = True
                i += 2
                continue
            if ch in ("'", '"'):
                in_string = ch
                i += 1
                continue
            out += ch
            i += 1
        yield idx, out


def check_bypass(repo_root):
    check = Check(
        "EXEC-AUDIT0-BYPASS-001",
        "game includes engine/modules or scheduler backends, spawns threads, or calls legacy paths",
        "Remove forbidden includes/calls and legacy execution paths; use engine public APIs only.",
    )
    game_root = os.path.join(repo_root, "game")
    for path in iter_source_files(game_root, repo_root):
        rel = repo_rel(repo_root, path)
        if rel.startswith("game/tests/"):
            continue
        text = read_text(path)
        for idx, include_path in iter_include_lines(text):
            inc = include_path.lower()
            for token in FORBIDDEN_GAME_INCLUDES:
                if token in inc:
                    check.add_violation(rel, idx, include_path)
                    break
            for header in FORBIDDEN_THREAD_HEADERS:
                if inc.endswith(header):
                    check.add_violation(rel, idx, include_path)
                    break
        for idx, code in iter_code_lines(text):
            if THREAD_CALL_RE.search(code):
                check.add_violation(rel, idx, "thread creation")
        if IR_ONLY_MARKER_RE.search(text):
            for idx, code in iter_code_lines(text):
                if LEGACY_CALL_RE.search(code):
                    check.add_violation(rel, idx, "legacy call in IR-only system")
    return check


def check_tasknode_completeness(repo_root):
    check = Check(
        "EXEC-AUDIT0-IR-REQ-002",
        "TaskNode construction missing required fields (best-effort)",
        "Ensure TaskNode sets determinism_class, AccessSet, CostModel, phase_id, and commit_key.",
    )
    game_root = os.path.join(repo_root, "game")
    for path in iter_source_files(game_root, repo_root):
        rel = repo_rel(repo_root, path)
        if rel.startswith("game/tests/") or rel.startswith("game/include/"):
            continue
        text = read_text(path)
        if not TASK_NODE_TOKEN_RE.search(text):
            continue
        if ".task_id" not in text or ".category" not in text:
            continue
        missing = []
        for token in REQUIRED_TASK_TOKENS:
            if token not in text:
                missing.append(token)
        if AUTHORITATIVE_TOKEN in text and REQUIRED_LAW_TOKEN not in text:
            missing.append(REQUIRED_LAW_TOKEN)
        if missing:
            check.add_violation(rel, 1, "missing " + ", ".join(missing))
    return check


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    checks = [
        check_bypass(repo_root),
        check_tasknode_completeness(repo_root),
    ]
    failed = False
    for check in checks:
        if check.report():
            failed = True
    if not failed:
        print("Execution contract checks OK.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
