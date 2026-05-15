#!/usr/bin/env python3
"""Inventory top-level repo entries against the Dominium root constitution."""

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


IGNORED_CONTROL_ROOTS = {".git"}


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _section_bodies(text, prefix):
    pattern = re.compile(r"^\[" + re.escape(prefix) + r"\.[^\]]+\]\s*$(.*?)(?=^\[|\Z)", re.M | re.S)
    return [match.group(1) for match in pattern.finditer(text)]


def _string_value(body, key):
    match = re.search(r"^\s*" + re.escape(key) + r'\s*=\s*"([^"]*)"', body, re.M)
    return match.group(1) if match else None


def _array_value(text, key):
    match = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*\[(.*?)\]", text, re.M | re.S)
    if not match:
        return []
    return re.findall(r'"([^"]*)"', match.group(1))


def load_constitution(repo_root):
    path = repo_root / "contracts" / "repo" / "root_constitution.toml"
    text = _read_text(path)
    result = {
        "path": str(path.relative_to(repo_root)),
        "present": bool(text),
        "stable": set(),
        "generated": set(),
        "local": set(),
        "transitional": set(),
    }
    if not text:
        return result
    for body in _section_bodies(text, "stable_roots"):
        value = _string_value(body, "path")
        if value:
            result["stable"].add(value)
    for body in _section_bodies(text, "generated_roots"):
        value = _string_value(body, "path")
        if value:
            result["generated"].add(value)
    for body in _section_bodies(text, "local_roots"):
        value = _string_value(body, "path")
        if value:
            result["local"].add(value)
    transitional_match = re.search(r"^\[transitional_roots\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if transitional_match:
        result["transitional"].update(_array_value(transitional_match.group(1), "roots"))
    return result


def load_allowlist(repo_root):
    path = repo_root / "contracts" / "repo" / "root_allowlist.toml"
    text = _read_text(path)
    result = {
        "allowed_files": set(),
        "allowed_file_patterns": set(),
        "metadata": set(),
        "optional": set(),
    }
    if not text:
        return result
    allowed_files_match = re.search(r"^\[allowed_root_files\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if allowed_files_match:
        body = allowed_files_match.group(1)
        result["allowed_files"].update(_array_value(body, "allowed"))
        result["allowed_file_patterns"].update(_array_value(body, "patterns"))
    result["metadata"].update(_section_keys(text, "metadata_directories"))
    result["optional"].update(_section_keys(text, "optional_directories"))
    return result


def _section_keys(text, section):
    match = re.search(r"^\[" + re.escape(section) + r"\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not match:
        return set()
    keys = set()
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip().strip('"')
        if key:
            keys.add(key)
    return keys


def load_active_exceptions(repo_root):
    path = repo_root / "contracts" / "repo" / "layout_exceptions.toml"
    text = _read_text(path)
    exceptions = set()
    if not text:
        return exceptions
    pattern = re.compile(r"^\[exceptions\.[^\]]+\]\s*$(.*?)(?=^\[|\Z)", re.M | re.S)
    for match in pattern.finditer(text):
        body = match.group(1)
        active_match = re.search(r"^\s*active\s*=\s*(true|false)", body, re.M)
        active = active_match is None or active_match.group(1) == "true"
        value = _string_value(body, "path")
        if active and value:
            exceptions.add(value)
    return exceptions


def is_allowed_file(name, allowlist):
    if name in allowlist["allowed_files"]:
        return True
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in allowlist["allowed_file_patterns"])


def classify_entry(name, is_dir, constitution, allowlist, active_exceptions):
    if name in constitution["stable"]:
        return "stable_root"
    if name in constitution["generated"]:
        return "generated_root"
    if name in constitution["local"]:
        return "local_root"
    if name in constitution["transitional"]:
        return "transitional_root"
    if name in allowlist["metadata"]:
        return "metadata_root"
    if name in allowlist["optional"]:
        return "optional_root"
    if not is_dir and is_allowed_file(name, allowlist):
        return "allowed_root_file"
    if name in active_exceptions:
        return "exception_backed"
    return "unknown"


def inventory(repo_root):
    constitution = load_constitution(repo_root)
    allowlist = load_allowlist(repo_root)
    active_exceptions = load_active_exceptions(repo_root)
    entries = []
    for child in sorted(repo_root.iterdir(), key=lambda item: (item.name.lower(), item.name)):
        if child.name in IGNORED_CONTROL_ROOTS:
            continue
        is_dir = child.is_dir()
        classification = classify_entry(child.name, is_dir, constitution, allowlist, active_exceptions)
        entries.append({
            "path": child.name,
            "kind": "directory" if is_dir else "file",
            "classification": classification,
        })
    summary = {}
    for entry in entries:
        summary[entry["classification"]] = summary.get(entry["classification"], 0) + 1
    return {
        "schema_version": "dominium.aide.root_inventory.v1",
        "repo_root": str(repo_root),
        "constitution": {
            "path": constitution["path"],
            "present": constitution["present"],
        },
        "summary": dict(sorted(summary.items())),
        "entries": entries,
    }


def emit_human(data):
    print("Root inventory")
    print("==============")
    print("constitution: {0} ({1})".format(data["constitution"]["path"], "present" if data["constitution"]["present"] else "missing"))
    print("")
    for entry in data["entries"]:
        print("{path}\t{kind}\t{classification}".format(**entry))


def write_text_lf(path, text):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON.")
    parser.add_argument("--out", help="Write deterministic JSON to this path.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    data = inventory(repo_root)
    json_text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(out_path, json_text)
    if args.json:
        sys.stdout.write(json_text)
    else:
        emit_human(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
