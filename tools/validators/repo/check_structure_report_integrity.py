#!/usr/bin/env python3
"""Verify tracked-only structure report bundle integrity.

The canonical finalization pass keeps task-local structure exports under the
ignored .dominium.local tree. This validator can verify such a bundle when a
manifest is supplied, and otherwise reports whether any known active tracked
dirfiles bundle artifacts are present.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile


MANIFEST_SCHEMA_VERSION = "dominium.repo.structure_report_bundle.v1"
DIR_TREE_SCHEMA_VERSION = "dominium.repo.dir_tree.v1"

KNOWN_BUNDLE_FILES = {
    "dirfiles_manifest.json",
    "dir_tree.json",
    "dir_tree.txt",
    "dirfiles.zip",
    "dirfiles_run.log",
}

TASK_EXPORT_FILES = (
    "tracked-files.txt",
    "tracked-dirs.txt",
    "tracked-roots.txt",
    "first-level-by-root.txt",
    "suspicious-active-paths.txt",
    "old-path-sweep.txt",
    "suspicious-active-paths-final.txt",
    "old-path-sweep-final.txt",
    "validation-summary.txt",
    "task-status-matrix.json",
    "report-integrity.txt",
    "report-manifest.json",
)

ALLOWED_ACTIVE_ROOTS = {
    ".aide",
    ".aide.local.example",
    ".github",
    ".vscode",
    "apps",
    "archive",
    "cmake",
    "content",
    "contracts",
    "docs",
    "engine",
    "external",
    "game",
    "release",
    "runtime",
    "scripts",
    "tests",
    "tools",
}

GENERATED_LOCAL_ROOTS = {".aide.local", ".dominium.local", "build", "out", "dist", "artifacts", "reports", "tmp", "__pycache__"}

RETIRED_ACTIVE_PREFIXES = (
    "runtime/render/soft",
    "runtime/render/stub",
    "runtime/render/client/renderers",
    "runtime/shell/commands",
    "runtime/shell/ui_backends",
    "runtime/capability/capability",
    "runtime/ui/core",
    "runtime/compatx",
    "runtime/ui/control/dui",
    "runtime/include/dui",
    "runtime/platform/win32/ui/dui",
    "runtime/platform/win32/ui/include/dui",
    "game/rules",
    "game/include/dominium/rules",
    "engine/compatx",
    "engine/include/domino/app",
    "engine/include/domino/cli",
    "engine/include/domino/gui",
    "engine/include/domino/input",
    "engine/include/domino/io",
    "engine/include/domino/pkg",
    "engine/include/domino/render",
    "engine/include/domino/tui",
    "engine/include/domino/world",
    "engine/include/render",
    "tests/ops",
    "tests/services",
)

RETIRED_SCHEMA_PREFIXES = (
    "contracts/schema/agents",
    "contracts/schema/authority",
    "contracts/schema/economy",
    "contracts/schema/law",
    "contracts/schema/life",
    "contracts/schema/session",
    "contracts/schema/time",
    "contracts/schema/ui",
    "contracts/schema/world",
    "contracts/schema/worldgen",
)

REQUIRED_MANIFEST_FIELDS = (
    "schema_version",
    "source_mode",
    "commit",
    "branch",
    "dirty",
    "generated_utc",
    "run_id",
    "files",
)

METADATA_FIELDS = (
    "source_mode",
    "commit",
    "branch",
    "dirty",
    "generated_utc",
    "run_id",
)

ZIP_REQUIRED_MEMBERS = ("dir_tree.json", "dir_tree.txt", "dirfiles_run.log")


def _configure_stdio():
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdio()


def utc_now():
    return _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def posix(path):
    return str(path).replace("\\", "/")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def git_command(repo_root, args):
    result = subprocess.run(
        ["git"] + list(args),
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def git_files(repo_root):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def tracked_dirs(paths):
    dirs = set()
    for path in paths:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]))
    return sorted(dirs)


def has_prefix(path, prefix):
    return path == prefix or path.startswith(prefix + "/")


def tracked_roots(paths):
    roots = set()
    for path in paths:
        if "/" in path:
            roots.add(path.split("/", 1)[0])
        elif path:
            roots.add(".")
    return sorted(roots)


def first_level_by_root(paths):
    mapping = {}
    for path in paths:
        parts = path.split("/")
        if len(parts) < 2:
            continue
        mapping.setdefault(parts[0], set()).add(parts[1])
    return {root: sorted(values) for root, values in sorted(mapping.items())}


def suspicious_paths(paths):
    findings = []
    prefixes = RETIRED_ACTIVE_PREFIXES + RETIRED_SCHEMA_PREFIXES
    for path in paths:
        root = path.split("/", 1)[0] if "/" in path else path
        if root in GENERATED_LOCAL_ROOTS:
            findings.append("tracked generated/local root: {0}".format(path))
            continue
        if "/" in path and root not in ALLOWED_ACTIVE_ROOTS:
            findings.append("unexpected active root: {0}".format(path))
            continue
        for prefix in prefixes:
            if has_prefix(path, prefix):
                findings.append("retired active prefix {0}: {1}".format(prefix, path))
                break
    return sorted(findings)


def old_path_sweep(paths):
    rows = []
    for prefix in RETIRED_ACTIVE_PREFIXES + RETIRED_SCHEMA_PREFIXES:
        matches = [path for path in paths if has_prefix(path, prefix)]
        if matches:
            rows.extend("active {0}: {1}".format(prefix, path) for path in matches)
        else:
            rows.append("clear {0}".format(prefix))
    return rows


def git_metadata(repo_root):
    status = git_command(repo_root, ["status", "--porcelain"])
    return {
        "source_mode": "git_tracked",
        "commit": git_command(repo_root, ["rev-parse", "HEAD"]),
        "branch": git_command(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(status),
    }


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def add(findings, severity, path, message):
    findings.append({"severity": severity, "path": posix(path), "message": message})


def normalized_metadata_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def expected_metadata(manifest):
    return {key: manifest.get(key) for key in METADATA_FIELDS}


def compare_metadata(findings, path, expected, actual, require_all):
    for key, expected_value in sorted(expected.items()):
        if key not in actual:
            if require_all:
                add(findings, "blocker", path, "missing run metadata field {0}".format(key))
            continue
        if normalized_metadata_value(actual[key]) != normalized_metadata_value(expected_value):
            add(
                findings,
                "blocker",
                path,
                "run metadata mismatch for {0}: expected {1}, found {2}".format(
                    key,
                    normalized_metadata_value(expected_value),
                    normalized_metadata_value(actual[key]),
                ),
            )


def parse_json_metadata(path):
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {}
    return {key: payload[key] for key in METADATA_FIELDS if key in payload}


def parse_text_metadata(path):
    metadata = {}
    pattern = re.compile(r"^\s*([A-Za-z0-9_]+)\s*[:=]\s*(.*?)\s*$")
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if index > 128:
                break
            match = pattern.match(line)
            if not match:
                continue
            key, value = match.group(1), match.group(2)
            if key in METADATA_FIELDS:
                metadata[key] = value
    return metadata


def validate_zip(findings, bundle_dir, entry_by_path):
    zip_entry = entry_by_path.get("dirfiles.zip")
    zip_path = os.path.join(bundle_dir, "dirfiles.zip")
    if not os.path.exists(zip_path):
        return
    if not zip_entry:
        add(findings, "blocker", "dirfiles.zip", "zip file exists but is not listed in manifest files[]")
        return

    try:
        archive = zipfile.ZipFile(zip_path, "r")
    except Exception as exc:
        add(findings, "blocker", "dirfiles.zip", "failed to open zip: {0}".format(exc))
        return

    with archive:
        seen = set()
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = posix(info.filename)
            if os.path.isabs(name) or ".." in name.split("/"):
                add(findings, "blocker", name, "zip member path must stay inside bundle")
                continue
            seen.add(name)
            member_entry = entry_by_path.get(name)
            if not member_entry:
                add(findings, "blocker", name, "zip member is not listed by manifest files[]")
                continue
            payload = archive.read(info.filename)
            if member_entry.get("size") != len(payload):
                add(findings, "blocker", name, "zip member size does not match manifest")
            if member_entry.get("sha256") != sha256_bytes(payload):
                add(findings, "blocker", name, "zip member sha256 does not match manifest")
        for required in ZIP_REQUIRED_MEMBERS:
            if required in entry_by_path and required not in seen:
                add(findings, "blocker", required, "zip is missing required report member")


def verify_manifest(manifest_path):
    manifest_path = os.path.abspath(manifest_path)
    bundle_dir = os.path.dirname(manifest_path)
    findings = []
    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:
        return {
            "bundle_dir": posix(bundle_dir),
            "manifest": posix(manifest_path),
            "status": "BLOCKED",
            "finding_count": 1,
            "findings": [{"severity": "blocker", "path": posix(manifest_path), "message": "failed to parse manifest: {0}".format(exc)}],
        }

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            add(findings, "blocker", manifest_path, "manifest is missing required field {0}".format(field))

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        add(
            findings,
            "blocker",
            manifest_path,
            "manifest schema_version must be {0}".format(MANIFEST_SCHEMA_VERSION),
        )

    if manifest.get("source_mode") != "git_tracked":
        add(findings, "blocker", manifest_path, "manifest source_mode must be git_tracked")
    if not re.match(r"^[0-9a-fA-F]{40}$", str(manifest.get("commit", ""))):
        add(findings, "blocker", manifest_path, "manifest commit must be a full git commit hash")
    if not isinstance(manifest.get("branch"), str) or not manifest.get("branch"):
        add(findings, "blocker", manifest_path, "manifest branch must be a non-empty string")
    if not isinstance(manifest.get("dirty"), bool):
        add(findings, "blocker", manifest_path, "manifest dirty must be a boolean")
    if not isinstance(manifest.get("generated_utc"), str) or not manifest.get("generated_utc"):
        add(findings, "blocker", manifest_path, "manifest generated_utc must be a non-empty string")
    if not isinstance(manifest.get("run_id"), str) or not manifest.get("run_id"):
        add(findings, "blocker", manifest_path, "manifest run_id must be a non-empty string")

    entries = manifest.get("files", [])
    if not isinstance(entries, list) or not entries:
        add(findings, "blocker", manifest_path, "manifest must contain non-empty files[]")
    seen_paths = set()
    for entry in entries if isinstance(entries, list) else []:
        rel = entry.get("path", "")
        if not rel or os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
            add(findings, "blocker", rel, "manifest entry path must be relative and stay inside bundle")
            continue
        rel = posix(rel)
        if rel in seen_paths:
            add(findings, "blocker", rel, "manifest entry path is duplicated")
            continue
        seen_paths.add(rel)
        if not isinstance(entry.get("size"), int):
            add(findings, "blocker", rel, "manifest entry size must be an integer")
        if not re.match(r"^[0-9a-fA-F]{64}$", str(entry.get("sha256", ""))):
            add(findings, "blocker", rel, "manifest entry sha256 must be a sha256 hex digest")
        candidate = os.path.join(bundle_dir, *rel.replace("\\", "/").split("/"))
        if not os.path.exists(candidate):
            add(findings, "blocker", rel, "manifest entry is missing")
            continue
        actual_hash = sha256_file(candidate)
        actual_size = os.path.getsize(candidate)
        if entry.get("sha256") != actual_hash:
            add(findings, "blocker", rel, "sha256 mismatch")
        if entry.get("size") != actual_size:
            add(findings, "blocker", rel, "size mismatch")

    entry_by_path = {posix(entry.get("path", "")): entry for entry in entries if isinstance(entry, dict)}
    manifest_abs = os.path.abspath(manifest_path)
    for filename in sorted(KNOWN_BUNDLE_FILES):
        candidate = os.path.join(bundle_dir, filename)
        if not os.path.exists(candidate):
            continue
        if os.path.abspath(candidate) == manifest_abs:
            continue
        if filename not in entry_by_path:
            add(findings, "blocker", filename, "known bundle file is present but not listed by manifest files[]")

    expected = expected_metadata(manifest)
    for filename in ("dir_tree.json", "dir_tree.txt", "dirfiles_run.log"):
        if filename not in entry_by_path:
            continue
        candidate = os.path.join(bundle_dir, filename)
        if not os.path.exists(candidate):
            continue
        try:
            metadata = parse_json_metadata(candidate) if filename.endswith(".json") else parse_text_metadata(candidate)
        except Exception as exc:
            add(findings, "blocker", filename, "failed to parse report metadata: {0}".format(exc))
            continue
        compare_metadata(findings, filename, expected, metadata, require_all=True)

    validate_zip(findings, bundle_dir, entry_by_path)

    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "bundle_dir": posix(bundle_dir),
        "manifest": posix(manifest_path),
        "schema_version": manifest.get("schema_version", ""),
        "source_mode": manifest.get("source_mode", ""),
        "commit": manifest.get("commit", ""),
        "branch": manifest.get("branch", ""),
        "run_id": manifest.get("run_id", ""),
        "status": "BLOCKED" if blocker_count else "PASS_WITH_WARNINGS" if warning_count else "PASS",
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "finding_count": len(findings),
        "findings": findings,
    }


def write_text(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, sort_keys=True, indent=2, ensure_ascii=True)
        handle.write("\n")


def file_entry(bundle_dir, filename):
    path = os.path.join(bundle_dir, filename)
    return {"path": filename, "size": os.path.getsize(path), "sha256": sha256_file(path)}


def write_zip(bundle_dir):
    zip_path = os.path.join(bundle_dir, "dirfiles.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in ZIP_REQUIRED_MEMBERS:
            path = os.path.join(bundle_dir, filename)
            info = zipfile.ZipInfo(filename)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as handle:
                archive.writestr(info, handle.read())


def write_bundle(repo_root, output_dir):
    repo_root = os.path.abspath(repo_root)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    for filename in sorted(KNOWN_BUNDLE_FILES | set(TASK_EXPORT_FILES)):
        candidate = os.path.join(output_dir, filename)
        if os.path.exists(candidate) and os.path.isfile(candidate):
            os.remove(candidate)

    tracked = sorted(git_files(repo_root))
    dirs = tracked_dirs(tracked)
    generated_utc = utc_now()
    metadata = git_metadata(repo_root)
    run_id = "structure-{0}-{1}".format(
        generated_utc.replace("-", "").replace(":", "").replace("Z", "Z"),
        metadata["commit"][:12],
    )

    common = dict(metadata)
    common["generated_utc"] = generated_utc
    common["run_id"] = run_id

    tree_payload = dict(common)
    tree_payload.update(
        {
            "schema_version": DIR_TREE_SCHEMA_VERSION,
            "directory_count": len(dirs),
            "file_count": len(tracked),
            "directories": dirs,
        }
    )
    write_json(os.path.join(output_dir, "dir_tree.json"), tree_payload)

    header = [
        "schema_version: {0}".format(DIR_TREE_SCHEMA_VERSION),
        "source_mode: {0}".format(common["source_mode"]),
        "commit: {0}".format(common["commit"]),
        "branch: {0}".format(common["branch"]),
        "dirty: {0}".format(normalized_metadata_value(common["dirty"])),
        "generated_utc: {0}".format(common["generated_utc"]),
        "run_id: {0}".format(common["run_id"]),
        "file_count: {0}".format(len(tracked)),
        "directory_count: {0}".format(len(dirs)),
        "",
    ]
    write_text(os.path.join(output_dir, "dir_tree.txt"), "\n".join(header + dirs) + "\n")

    run_log = [
        "schema_version: {0}".format(MANIFEST_SCHEMA_VERSION),
        "source_mode: {0}".format(common["source_mode"]),
        "commit: {0}".format(common["commit"]),
        "branch: {0}".format(common["branch"]),
        "dirty: {0}".format(normalized_metadata_value(common["dirty"])),
        "generated_utc: {0}".format(common["generated_utc"]),
        "run_id: {0}".format(common["run_id"]),
        "status: generated",
        "tracked_files: {0}".format(len(tracked)),
        "tracked_directories: {0}".format(len(dirs)),
        "",
    ]
    write_text(os.path.join(output_dir, "dirfiles_run.log"), "\n".join(run_log))

    roots = tracked_roots(tracked)
    first_level = first_level_by_root(tracked)
    suspicious = suspicious_paths(tracked)
    sweep = old_path_sweep(tracked)
    write_text(os.path.join(output_dir, "tracked-files.txt"), "\n".join(tracked) + "\n")
    write_text(os.path.join(output_dir, "tracked-dirs.txt"), "\n".join(dirs) + "\n")
    write_text(os.path.join(output_dir, "tracked-roots.txt"), "\n".join(roots) + "\n")
    first_level_lines = []
    for root, children in sorted(first_level.items()):
        first_level_lines.append(root + ":")
        first_level_lines.extend("  " + child for child in children)
    write_text(os.path.join(output_dir, "first-level-by-root.txt"), "\n".join(first_level_lines) + "\n")
    suspicious_text = "\n".join(suspicious) if suspicious else "none"
    sweep_text = "\n".join(sweep)
    write_text(os.path.join(output_dir, "suspicious-active-paths.txt"), suspicious_text + "\n")
    write_text(os.path.join(output_dir, "old-path-sweep.txt"), sweep_text + "\n")
    write_text(os.path.join(output_dir, "suspicious-active-paths-final.txt"), suspicious_text + "\n")
    write_text(os.path.join(output_dir, "old-path-sweep-final.txt"), sweep_text + "\n")
    write_text(
        os.path.join(output_dir, "validation-summary.txt"),
        "\n".join(
            [
                "schema_version: {0}".format(MANIFEST_SCHEMA_VERSION),
                "source_mode: {0}".format(common["source_mode"]),
                "commit: {0}".format(common["commit"]),
                "branch: {0}".format(common["branch"]),
                "dirty: {0}".format(normalized_metadata_value(common["dirty"])),
                "generated_utc: {0}".format(common["generated_utc"]),
                "run_id: {0}".format(common["run_id"]),
                "status: generated",
                "suspicious_active_paths: {0}".format(len(suspicious)),
                "",
            ]
        ),
    )
    write_json(
        os.path.join(output_dir, "task-status-matrix.json"),
        dict(
            common,
            schema_version="dominium.repo.structure_task_status_matrix.v1",
            task_id="CANON-STRUCTURE-ACTUAL-FINAL-CLEANUP-01",
            checks={
                "tracked_files": len(tracked),
                "tracked_directories": len(dirs),
                "tracked_roots": roots,
                "suspicious_active_path_count": len(suspicious),
            },
        ),
    )
    write_text(
        os.path.join(output_dir, "report-integrity.txt"),
        "\n".join(
            [
                "schema_version: {0}".format(MANIFEST_SCHEMA_VERSION),
                "source_mode: {0}".format(common["source_mode"]),
                "commit: {0}".format(common["commit"]),
                "branch: {0}".format(common["branch"]),
                "dirty: {0}".format(normalized_metadata_value(common["dirty"])),
                "generated_utc: {0}".format(common["generated_utc"]),
                "run_id: {0}".format(common["run_id"]),
                "status: generated_pending_manifest_verification",
                "",
            ]
        ),
    )
    write_json(
        os.path.join(output_dir, "report-manifest.json"),
        dict(
            common,
            schema_version="dominium.repo.structure_report_alias.v1",
            canonical_manifest="dirfiles_manifest.json",
            core_reports=list(ZIP_REQUIRED_MEMBERS),
            task_reports=list(TASK_EXPORT_FILES),
        ),
    )
    write_zip(output_dir)

    manifest_files = ("dir_tree.json", "dir_tree.txt", "dirfiles_run.log", "dirfiles.zip") + TASK_EXPORT_FILES
    manifest = dict(common)
    manifest.update(
        {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "files": [
                file_entry(output_dir, filename)
                for filename in manifest_files
            ],
        }
    )
    manifest_path = os.path.join(output_dir, "dirfiles_manifest.json")
    write_json(manifest_path, manifest)
    report = verify_manifest(manifest_path)
    report["written_bundle_dir"] = posix(output_dir)
    return report


def inspect_tracked(repo_root):
    tracked = git_files(repo_root)
    bundle_files = [path for path in tracked if path.split("/")[-1] in KNOWN_BUNDLE_FILES]
    findings = []
    for path in bundle_files:
        findings.append(
            {
                "severity": "warning",
                "path": path,
                "message": "tracked structure report artifact needs an explicit integrity manifest",
            }
        )
    return {
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "PASS_WITH_WARNINGS" if findings else "PASS",
        "tracked_bundle_file_count": len(bundle_files),
        "finding_count": len(findings),
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify structure report bundle integrity.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", help="Path to a structure bundle manifest.json.")
    parser.add_argument("--write-bundle", help="Write a fresh tracked-only structure report bundle to this directory.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on blockers.")
    args = parser.parse_args()

    if args.write_bundle:
        report = write_bundle(os.path.abspath(args.repo_root), args.write_bundle)
    elif args.manifest:
        report = verify_manifest(args.manifest)
    else:
        report = inspect_tracked(os.path.abspath(args.repo_root))
    report["generated_utc"] = utc_now()

    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("structure report integrity: {0}".format(report["status"]))
        for item in report.get("findings", []):
            print("{severity} {path}: {message}".format(**item))

    if args.strict and report["status"] == "BLOCKED":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
