#!/usr/bin/env python3
import argparse
import json
import os
import re
from datetime import date


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def parse_project_semver(repo_root):
    cmake_path = os.path.join(repo_root, "CMakeLists.txt")
    text = read_text(cmake_path)
    match = re.search(r'set\(DOM_PROJECT_SEMVER\s+"([^"]+)"', text)
    if match:
        return match.group(1).strip()
    return "unknown"


def parse_build_number(repo_root):
    path = os.path.join(repo_root, ".dominium_build_number")
    text = read_text(path).strip()
    return text if text else "unknown"


def iter_schema_files(repo_root):
    root = os.path.join(repo_root, "schema")
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if name.endswith(".schema"):
                yield os.path.join(dirpath, name)


def parse_schema_header(path):
    schema_id = None
    schema_version = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw.strip()
                if line.startswith("schema_id:"):
                    schema_id = line.split(":", 1)[1].strip()
                if line.startswith("schema_version:"):
                    schema_version = line.split(":", 1)[1].strip()
                if schema_id and schema_version:
                    break
    except OSError:
        return None
    return schema_id, schema_version


def load_invariants(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "VALIDATION_RULES.md")
    text = read_text(path)
    invariants = []
    for line in text.splitlines():
        line = line.strip()
        match = re.match(r"^##\\s+(INV-[A-Z0-9_-]+)\\b", line)
        if match:
            invariants.append(match.group(1))
    return sorted(set(invariants))


def load_canon_index(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "CANON_INDEX.md")
    if not os.path.isfile(path):
        return None
    canon = {"CANONICAL": [], "DERIVED": [], "HISTORICAL": []}
    current = None
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if line == "## CANONICAL":
                current = "CANONICAL"
                continue
            if line == "## DERIVED":
                current = "DERIVED"
                continue
            if line == "## HISTORICAL":
                current = "HISTORICAL"
                continue
            if line.startswith("## "):
                current = None
                continue
            if current and line.startswith("-"):
                match = re.search(r"`([^`]+)`", line)
                if match:
                    canon[current].append(match.group(1))
    return canon


def load_overrides(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "LOCKLIST_OVERRIDES.json")
    if not os.path.isfile(path):
        return [], []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return [], []
    overrides = payload.get("overrides", [])
    active = []
    expired = []
    today = date.today()
    for entry in overrides or []:
        if not isinstance(entry, dict):
            continue
        expires = entry.get("expires")
        expiry = None
        if isinstance(expires, str):
            parts = expires.split("-")
            if len(parts) == 3:
                try:
                    expiry = date(int(parts[0]), int(parts[1]), int(parts[2]))
                except ValueError:
                    expiry = None
        if expiry and expiry >= today:
            active.append(entry)
        else:
            expired.append(entry)
    return active, expired


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a compliance report.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    semver = parse_project_semver(repo_root)
    build_number = parse_build_number(repo_root)
    invariants = load_invariants(repo_root)
    active_overrides, expired_overrides = load_overrides(repo_root)
    canon_index = load_canon_index(repo_root)

    schema_entries = []
    for path in iter_schema_files(repo_root):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        header = parse_schema_header(path)
        if not header:
            continue
        schema_id, schema_version = header
        schema_entries.append((schema_id or rel, schema_version or "unknown", rel))
    schema_entries.sort()

    print("COMPLIANCE_REPORT")
    print("project_semver: {}".format(semver))
    print("engine_version: {}".format(semver))
    print("game_version: {}".format(semver))
    print("build_number: {}".format(build_number))

    print("schema_versions:")
    for schema_id, schema_version, rel in schema_entries:
        print("  - {}@{} ({})".format(schema_id, schema_version, rel))

    print("invariants_enforced: {}".format(len(invariants)))
    for inv in invariants:
        print("  - {}".format(inv))

    print("overrides_active: {}".format(len(active_overrides)))
    for entry in active_overrides:
        print("  - {} {} expires {}".format(entry.get("id"), entry.get("invariant"), entry.get("expires")))

    print("overrides_expired: {}".format(len(expired_overrides)))
    for entry in expired_overrides:
        print("  - {} {} expired {}".format(entry.get("id"), entry.get("invariant"), entry.get("expires")))

    print("CANON_COMPLIANCE_REPORT")
    if canon_index is None:
        print("canon_index: missing")
    else:
        print("canon_index: docs/architecture/CANON_INDEX.md")
        print("canon_docs: {}".format(len(canon_index.get("CANONICAL", []))))
        print("derived_docs: {}".format(len(canon_index.get("DERIVED", []))))
        print("historical_docs: {}".format(len(canon_index.get("HISTORICAL", []))))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
