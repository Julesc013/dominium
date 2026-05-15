#!/usr/bin/env python3
"""Shared no-apply helpers for AIDE root recycling evidence."""

from __future__ import print_function

import json
import os
import re
import subprocess
from pathlib import Path


FATES = ("keep", "adapt", "extract", "convert", "archive", "drop", "preserve_unknown")
ACTIONS = ("keep", "move", "split", "convert", "archive", "drop", "no_action", "review")
RISKS = ("low", "medium", "high", "protected", "unknown")

SKIP_DIRS = {
    ".git",
    ".aide.local",
    ".dominium.local",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "build",
    "out",
}

TEXT_EXTENSIONS = {
    "",
    ".bat",
    ".cmd",
    ".cmake",
    ".conf",
    ".cpp",
    ".c",
    ".csv",
    ".h",
    ".hpp",
    ".ini",
    ".json",
    ".jsonl",
    ".lock",
    ".md",
    ".py",
    ".rst",
    ".schema",
    ".sh",
    ".txt",
    ".toml",
    ".tsv",
    ".xml",
    ".yaml",
    ".yml",
}

IDENTITY_MARKERS = {
    "pack_id": ["identity_sensitive", "pack_identity"],
    "profile_id": ["identity_sensitive", "profile_identity"],
    "bundle_id": ["identity_sensitive", "bundle_identity"],
    "content_id": ["identity_sensitive"],
    "schema_version": ["schema_version_sensitive"],
    "manifest": ["manifest_sensitive"],
    "sha256": ["content_hash_sensitive"],
    "hash": ["content_hash_sensitive"],
    "lock": ["lock_sensitive"],
    "capability": ["capability_sensitive"],
    "compatibility": ["compatibility_sensitive"],
    "save": ["save_instance_sensitive"],
    "instance": ["save_instance_sensitive"],
    "export": ["distribution_sensitive"],
    "projection": ["distribution_sensitive"],
    "install": ["distribution_sensitive"],
    "release": ["distribution_sensitive"],
    "dompkg": ["distribution_sensitive"],
}

AUTHORITY_MARKERS = {
    "MUST": ["authority_sensitive", "policy_or_contract"],
    "MUST NOT": ["authority_sensitive", "policy_or_contract"],
    "SHALL": ["authority_sensitive", "policy_or_contract"],
    "SHOULD": ["authority_sensitive", "policy_or_contract"],
    "canonical": ["authority_sensitive"],
    "normative": ["authority_sensitive", "spec_sensitive"],
    "authority": ["authority_sensitive"],
    "contract": ["policy_or_contract"],
    "schema": ["schema_sensitive"],
    "compatibility": ["compatibility_sensitive"],
    "migration": ["migration_sensitive"],
    "refusal": ["refusal_sensitive"],
    "lock": ["lock_sensitive"],
    "capability": ["compatibility_sensitive"],
    "security": ["security_sensitive"],
    "safety": ["safety_sensitive"],
    "signing": ["signing_sensitive"],
    "threat": ["threat_model_sensitive"],
    "trust": ["trust_sensitive"],
    "update": ["update_sensitive"],
    "release": ["release_sensitive"],
    "manifest": ["machine_readable"],
    "feed": ["update_sensitive"],
    "policy": ["policy_or_contract"],
    "governance": ["governance_sensitive"],
    "checksum": ["lock_sensitive"],
    "sha256": ["lock_sensitive"],
}

SEMANTIC_MARKERS = {
    "deterministic": ["deterministic_sensitive"],
    "fixed": ["deterministic_sensitive"],
    "rng": ["deterministic_sensitive"],
    "seed": ["deterministic_sensitive"],
    "process": ["process_mutation_sensitive"],
    "mutation": ["process_mutation_sensitive"],
    "authority": ["authority_sensitive"],
    "control": ["control_sensitive"],
    "capability": ["capability_sensitive"],
    "permission": ["capability_sensitive"],
    "entitlement": ["capability_sensitive"],
    "server": ["server_authority_sensitive"],
    "network": ["network_sensitive"],
    "protocol": ["protocol_sensitive"],
    "transport": ["network_sensitive"],
    "lockstep": ["lockstep_sensitive"],
    "replay": ["replay_sensitive"],
    "resync": ["resync_sensitive"],
    "shard": ["shard_sensitive"],
    "SRZ": ["srz_sensitive"],
    "anti-cheat": ["anti_cheat_sensitive"],
    "integrity": ["integrity_sensitive"],
    "hash": ["integrity_sensitive"],
    "proof": ["authority_sensitive"],
    "audit": ["authority_sensitive"],
    "runtime": ["runtime_sensitive"],
    "adapter": ["runtime_sensitive"],
    "contract": ["authority_sensitive"],
    "schema": ["authority_sensitive"],
    "test": ["test_or_fixture"],
}

ABI_BUILD_MARKERS = {
    "#include": ["build_sensitive"],
    "extern": ["ABI_sensitive"],
    "DOM_API": ["ABI_sensitive"],
    "ABI": ["ABI_sensitive"],
    "EXPORT": ["ABI_sensitive"],
    "__declspec": ["ABI_sensitive"],
    "CMAKE": ["cmake_sensitive"],
    "target_link_libraries": ["cmake_sensitive"],
    "add_library": ["cmake_sensitive"],
    "add_executable": ["cmake_sensitive"],
    "ui_bind": ["generated_ui_bind", "line_ending_sensitive"],
    "generated": ["generated_source"],
    "appcore": ["appcore_sensitive"],
    "namespace": ["cpp_source"],
    "struct": ["public_header_sensitive"],
    "class": ["public_header_sensitive"],
    "typedef": ["public_header_sensitive"],
    "enum": ["public_header_sensitive"],
    "extern \"C\"": ["ABI_sensitive"],
    "public": ["public_header_sensitive"],
    "private": ["internal_header"],
    "runtime": ["runtime_sensitive"],
    "contract": ["policy_or_contract"],
    "schema": ["policy_or_contract"],
    "header": ["public_header_sensitive"],
    "tool": ["executable_or_tool"],
    "third_party": ["third_party_or_external"],
    "vendor": ["vendored"],
}


def posix_path(path):
    return str(path).replace(os.sep, "/")


def relpath(path, repo_root):
    return posix_path(os.path.relpath(str(path), str(repo_root)))


def source_head(repo_root):
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root), stderr=subprocess.DEVNULL)
    except Exception:
        return None
    return out.decode("utf-8", "replace").strip()


def tracked_files(repo_root):
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=str(repo_root), stderr=subprocess.DEVNULL)
    except Exception:
        return set()
    return set(line.strip().replace("\\", "/") for line in out.decode("utf-8", "replace").splitlines() if line.strip())


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.rstrip() + "\n")


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_text(path, max_bytes=1048576):
    path = Path(path)
    try:
        if path.stat().st_size > max_bytes:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None


def first_line(path):
    text = safe_text(path, max_bytes=8192)
    if text is None:
        return None
    for line in text.splitlines():
        return line[:240]
    return ""


def likely_kind(root, rel, extension, is_dir):
    lower = rel.lower()
    name = Path(rel).name.lower()
    if is_dir:
        return "directory"
    if extension in (".md", ".rst", ".txt"):
        return "documentation"
    if extension in (".json", ".toml", ".yaml", ".yml", ".xml", ".lock"):
        return "machine_readable"
    if extension in (".py", ".sh", ".cmd", ".bat"):
        return "tool_or_script"
    if extension in (".c", ".cc", ".cpp", ".cxx"):
        return "c_cpp_source"
    if extension in (".h", ".hh", ".hpp", ".hxx"):
        return "header"
    if "test" in lower or "fixture" in lower:
        return "test_or_fixture"
    if "manifest" in name or "pack" in lower or "profile" in lower or "bundle" in lower:
        return "identity_or_manifest"
    if root in ("ide",):
        return "ide_projection"
    if root in ("performance",):
        return "performance_evidence"
    return "unknown"


def base_flags(root, rel, kind, extension):
    lower = rel.lower()
    flags = set()
    if kind == "directory":
        return sorted(flags)
    if extension in (".md", ".rst", ".txt"):
        flags.add("documentation")
    if extension in (".json", ".toml", ".yaml", ".yml", ".xml", ".lock"):
        flags.add("machine_readable")
    if extension == ".py":
        flags.add("python_module")
    if extension in (".py", ".sh", ".cmd", ".bat"):
        flags.add("executable_or_tool")
    if extension in (".c", ".cc", ".cpp", ".cxx"):
        flags.add("cpp_source" if extension != ".c" else "c_source")
        flags.add("build_sensitive")
    if extension in (".h", ".hh", ".hpp", ".hxx"):
        flags.add("public_header_sensitive")
        flags.add("ABI_sensitive")
        flags.add("build_sensitive")
    if "test" in lower or "fixture" in lower:
        flags.add("test_or_fixture")
    if "generated" in lower or ".gen." in lower or "autogen" in lower:
        flags.add("generated")
    if "third_party" in lower or "vendor" in lower or "vendored" in lower:
        flags.add("third_party_or_external")
    if root == "ide":
        flags.add("ide_projection")
    if root == "performance":
        flags.add("performance_evidence")
    if root == "validation":
        flags.add("validation_tooling")
    if root in ("governance", "meta"):
        flags.add("policy_or_governance")
    if root in ("data", "packs", "profiles", "bundles"):
        flags.add("identity_sensitive")
        if root == "packs":
            flags.add("pack_identity")
        if root == "profiles":
            flags.add("profile_identity")
        if root == "bundles":
            flags.add("bundle_identity")
    if root in ("modding", "models", "templates"):
        flags.add({"modding": "capability_sensitive", "models": "model_asset", "templates": "template_scaffold"}[root])
    if root in ("compat", "locks", "repo", "safety", "security", "specs", "updates"):
        flags.add("authority_sensitive")
        flags.add({
            "compat": "compatibility_sensitive",
            "locks": "lock_sensitive",
            "repo": "repo_policy_sensitive",
            "safety": "safety_sensitive",
            "security": "security_sensitive",
            "specs": "spec_sensitive",
            "updates": "update_sensitive",
        }[root])
    if root in ("core", "control", "net"):
        flags.add("runtime_sensitive")
        flags.add({"core": "deterministic_sensitive", "control": "control_sensitive", "net": "network_sensitive"}[root])
    if root in ("lib", "libs"):
        flags.add("build_sensitive")
        if root == "libs":
            flags.add("ABI_sensitive")
    return sorted(flags)


def risk_for_flags(flags):
    low_flags = {"documentation", "performance_evidence", "ide_projection"}
    protected = {
        "identity_sensitive",
        "pack_identity",
        "profile_identity",
        "bundle_identity",
        "authority_sensitive",
        "security_sensitive",
        "safety_sensitive",
        "spec_sensitive",
        "runtime_sensitive",
        "deterministic_sensitive",
        "network_sensitive",
        "ABI_sensitive",
        "public_header_sensitive",
    }
    high = {
        "build_sensitive",
        "lock_sensitive",
        "compatibility_sensitive",
        "repo_policy_sensitive",
        "update_sensitive",
        "generated_ui_bind",
        "line_ending_sensitive",
    }
    if protected.intersection(flags):
        return "protected"
    if high.intersection(flags):
        return "high"
    if flags and set(flags).issubset(low_flags):
        return "low"
    if "unknown" in flags:
        return "unknown"
    if flags:
        return "medium"
    return "unknown"


def fate_for_entry(root, entry, flags):
    if entry.get("kind") == "directory":
        return "preserve_unknown", "Directories are containers; classify files before any move."
    likely = entry.get("likely_kind", "")
    if "documentation" in flags and root in ("ide", "performance"):
        return "adapt", "Documentation/evidence may be low-risk after reference review, but no move is approved."
    if "documentation" in flags:
        return "convert", "Documentation may become canonical docs or contracts after review."
    if likely == "tool_or_script" or "executable_or_tool" in flags:
        return "adapt", "Tooling may be wrapped or moved later only after references are clear."
    if "generated" in flags:
        return "preserve_unknown", "Generated-looking material requires provenance before archive/drop decisions."
    return "preserve_unknown", "Conservative default; preserve until stronger evidence exists."


def inventory_root(repo_root, root):
    repo_root = Path(repo_root).resolve()
    root_path = repo_root / root
    tracked = tracked_files(repo_root)
    data = {
        "schema_version": "dominium.aide.root_inventory.v1",
        "task_id": None,
        "source_head": source_head(repo_root),
        "root": root,
        "root_path": root,
        "status": "present" if root_path.exists() else "absent",
        "exists": root_path.exists(),
        "moves_applied": False,
        "deletes_applied": False,
        "renames_applied": False,
        "entries": [],
        "summary": {
            "file_count": 0,
            "directory_count": 0,
            "tracked_file_count": 0,
        },
    }
    if not root_path.exists():
        return data
    for current, dirs, files in os.walk(str(root_path)):
        dirs[:] = sorted([d for d in dirs if d not in SKIP_DIRS], key=lambda item: (item.casefold(), item))
        current_path = Path(current)
        if current_path != root_path:
            rel = relpath(current_path, repo_root)
            data["entries"].append({
                "path": rel,
                "relative_path": posix_path(os.path.relpath(str(current_path), str(root_path))),
                "kind": "directory",
                "extension": "",
                "size": 0,
                "tracked": False,
                "first_line": None,
                "likely_kind": "directory",
                "sensitivity_hints": [],
            })
            data["summary"]["directory_count"] += 1
        for filename in sorted(files, key=lambda item: (item.casefold(), item)):
            path = current_path / filename
            rel_repo = relpath(path, repo_root)
            rel_root = posix_path(os.path.relpath(str(path), str(root_path)))
            ext = path.suffix.lower()
            tracked_flag = rel_repo in tracked
            flags = base_flags(root, rel_root, "file", ext)
            data["entries"].append({
                "path": rel_repo,
                "relative_path": rel_root,
                "kind": "file",
                "extension": ext,
                "size": path.stat().st_size,
                "tracked": tracked_flag,
                "first_line": first_line(path),
                "likely_kind": likely_kind(root, rel_root, ext, False),
                "sensitivity_hints": flags,
            })
            data["summary"]["file_count"] += 1
            if tracked_flag:
                data["summary"]["tracked_file_count"] += 1
    return data


def classify_inventory(inventory):
    root = inventory.get("root", "")
    result = {
        "schema_version": "dominium.aide.root_classification.v1",
        "task_id": None,
        "source_head": inventory.get("source_head"),
        "root": root,
        "root_path": inventory.get("root_path", root),
        "status": "classified" if inventory.get("exists") else "absent",
        "moves_applied": False,
        "deletes_applied": False,
        "renames_applied": False,
        "entries": [],
        "summary": {
            "fate_counts": {},
            "risk_counts": {},
            "sensitivity_counts": {},
        },
    }
    for entry in inventory.get("entries", []):
        flags = set(entry.get("sensitivity_hints", []))
        if not flags and entry.get("kind") == "file":
            flags.add("unknown")
        fate, reason = fate_for_entry(root, entry, flags)
        risk = risk_for_flags(flags)
        out = {
            "path": entry.get("path"),
            "relative_path": entry.get("relative_path"),
            "kind": entry.get("kind"),
            "active": None,
            "fate": fate,
            "risk": risk,
            "sensitivity_flags": sorted(flags),
            "referenced_by": [],
            "target_path": None,
            "reason": reason,
            "blockers": ["no approved salvage map", "no approved move map"],
            "validators_required": ["repo_layout", "root_allowlist", "reference_scan"],
            "rollback_notes": "No move has been applied; preserve original path.",
            "drop_requires_review": fate == "drop",
        }
        result["entries"].append(out)
        result["summary"]["fate_counts"][fate] = result["summary"]["fate_counts"].get(fate, 0) + 1
        result["summary"]["risk_counts"][risk] = result["summary"]["risk_counts"].get(risk, 0) + 1
        for flag in flags:
            result["summary"]["sensitivity_counts"][flag] = result["summary"]["sensitivity_counts"].get(flag, 0) + 1
    result["summary"]["fate_counts"] = dict(sorted(result["summary"]["fate_counts"].items()))
    result["summary"]["risk_counts"] = dict(sorted(result["summary"]["risk_counts"].items()))
    result["summary"]["sensitivity_counts"] = dict(sorted(result["summary"]["sensitivity_counts"].items()))
    return result


def salvage_map_from_classification(classification):
    entries = []
    for entry in classification.get("entries", []):
        fate = entry.get("fate", "preserve_unknown")
        action = "review"
        if fate == "keep":
            action = "keep"
        elif fate == "convert":
            action = "convert"
        elif fate == "preserve_unknown":
            action = "no_action"
        entries.append({
            "path": entry.get("path"),
            "fate": fate,
            "target_path": None,
            "action": action,
            "reason": entry.get("reason", ""),
            "risk": entry.get("risk", "unknown"),
            "sensitivity_flags": entry.get("sensitivity_flags", []),
            "identity_preservation": "preserve original path and identifiers; no ID rewrite approved",
            "references_to_update": [],
            "validators_required": entry.get("validators_required", []),
            "rollback_notes": entry.get("rollback_notes", ""),
            "evidence_refs": [classification.get("root", "") + ".classification.json"],
        })
    return {
        "schema_version": "dominium.aide.salvage_map.v1",
        "task_id": None,
        "root": classification.get("root", ""),
        "source_head": classification.get("source_head"),
        "generated_from_inventory": classification.get("root", "") + ".inventory.json",
        "status": "draft",
        "approval_status": "not_approved",
        "apply_allowed": False,
        "moves_applied": False,
        "deletes_applied": False,
        "renames_applied": False,
        "entries": entries,
        "summary": {
            "entry_count": len(entries),
            "apply_allowed": False,
            "approval_status": "not_approved",
        },
    }


def validate_salvage_map(data, strict=False):
    errors = []
    warnings = []
    if data.get("apply_allowed") and data.get("approval_status") not in ("approved",):
        errors.append("apply_allowed true without approval_status approved")
    if data.get("approval_status") == "approved":
        errors.append("approved salvage maps are not allowed in this no-apply workflow")
    for index, entry in enumerate(data.get("entries", [])):
        fate = entry.get("fate")
        action = entry.get("action")
        path = entry.get("path", "")
        target = entry.get("target_path")
        if fate not in FATES:
            errors.append("entry {0} has unknown fate {1}".format(index, fate))
        if action not in ACTIONS:
            errors.append("entry {0} has unknown action {1}".format(index, action))
        if os.path.isabs(str(path)) or (target and os.path.isabs(str(target))):
            errors.append("entry {0} contains absolute host path".format(index))
        if action == "move" and not target:
            errors.append("entry {0} move lacks target_path".format(index))
        if action == "drop" and not entry.get("evidence_refs"):
            errors.append("entry {0} drop lacks evidence_refs".format(index))
    return {
        "schema_version": "dominium.aide.salvage_map_check.v1",
        "result": "FAIL" if errors else "PASS",
        "strict": bool(strict),
        "errors": errors,
        "warnings": warnings,
    }


def classify_reference_file(path):
    rel = path.lower().replace("\\", "/")
    if rel.startswith("docs/") or "/docs/" in rel:
        return "docs"
    if rel.startswith("tests/") or "/tests/" in rel:
        return "tests"
    if rel.startswith("tools/") or rel.startswith("scripts/") or "/tools/" in rel:
        return "tools"
    if rel.startswith("archive/") or rel.startswith("artifacts/"):
        return "generated_or_archive"
    if rel.endswith((".py", ".c", ".cpp", ".h", ".hpp", ".cmake")):
        return "active_source"
    return "unknown"


def scan_references(repo_root, root):
    repo_root = Path(repo_root).resolve()
    needles = [root + "/", root + "\\"]
    references = []
    for current, dirs, files in os.walk(str(repo_root)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        current_path = Path(current)
        for filename in files:
            path = current_path / filename
            rel = relpath(path, repo_root)
            if rel.startswith(".aide/reports/"):
                continue
            if rel.startswith(root + "/"):
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            text = safe_text(path)
            if text is None:
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                if any(needle in line for needle in needles):
                    references.append({
                        "file": rel,
                        "line": line_number,
                        "snippet": line.strip()[:240],
                        "classification": classify_reference_file(rel),
                    })
    return {
        "schema_version": "dominium.aide.root_reference_scan.v1",
        "root": root,
        "source_head": source_head(repo_root),
        "references": references,
        "summary": {
            "reference_count": len(references),
        },
        "moves_applied": False,
        "references_rewritten": False,
    }


def scan_markers(repo_root, root, markers, schema_version):
    repo_root = Path(repo_root).resolve()
    root_path = repo_root / root
    findings = []
    if root_path.exists():
        for current, dirs, files in os.walk(str(root_path)):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for filename in files:
                path = Path(current) / filename
                if path.suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                text = safe_text(path)
                if text is None:
                    continue
                rel = relpath(path, repo_root)
                for line_number, line in enumerate(text.splitlines(), 1):
                    lower_line = line.lower()
                    for marker, flags in markers.items():
                        marker_cmp = marker if marker.isupper() else marker.lower()
                        haystack = line if marker.isupper() else lower_line
                        if marker_cmp in haystack:
                            findings.append({
                                "file": rel,
                                "line": line_number,
                                "marker": marker,
                                "snippet": line.strip()[:240],
                                "sensitivity_hints": sorted(set(flags)),
                            })
    return {
        "schema_version": schema_version,
        "root": root,
        "source_head": source_head(repo_root),
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
        },
        "moves_applied": False,
        "rewrites_applied": False,
    }


def count_by(items, key, default="unknown"):
    counts = {}
    for item in items:
        value = item.get(key, default)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
