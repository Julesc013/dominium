#!/usr/bin/env python3
"""Audit Dominium top-level repository layout against a TOML contract."""

from __future__ import print_function

import argparse
import ast
import datetime as _datetime
import fnmatch
import json
import os
import subprocess
import sys


CLASS_CANONICAL = "canonical"
CLASS_OPTIONAL = "optional"
CLASS_METADATA = "metadata"
CLASS_ALLOWED_FILE = "allowed_file"
CLASS_TRANSITIONAL = "transitional_alias"
CLASS_TRANSITIONAL_PRODUCT = "transitional_product_root"
CLASS_TRANSITIONAL_RUNTIME = "transitional_runtime_root"
CLASS_TRANSITIONAL_CONTRACT = "transitional_contract_or_schema_root"
CLASS_TRANSITIONAL_CONTENT = "transitional_content_or_data_root"
CLASS_TRANSITIONAL_RELEASE = "transitional_release_or_dist_root"
CLASS_TRANSITIONAL_ARCHIVE = "transitional_archive_or_quarantine_root"
CLASS_DOMAIN = "split_required_domain_root"
CLASS_GENERATED = "generated_or_ephemeral"
CLASS_VIOLATION = "violation"
CLASS_UNKNOWN = "unknown_needs_review"

TRANSITIONAL_CLASSES = (
    CLASS_TRANSITIONAL,
    CLASS_TRANSITIONAL_PRODUCT,
    CLASS_TRANSITIONAL_RUNTIME,
    CLASS_TRANSITIONAL_CONTRACT,
    CLASS_TRANSITIONAL_CONTENT,
    CLASS_TRANSITIONAL_RELEASE,
    CLASS_TRANSITIONAL_ARCHIVE,
)

OWNERSHIP_SURFACES = set(
    [
        "apps",
        "engine",
        "game",
        "runtime",
        "contracts",
        "content",
        "docs",
        "tests",
        "tools",
        "scripts",
        "cmake",
        "external",
        "release",
        "archive",
        "metadata",
        "generated",
        "mixed_split_required",
        "unknown",
    ]
)

PRODUCT_ROOTS = set(["client", "server", "setup", "launcher"])
RUNTIME_ROOTS = set(
    [
        "app",
        "appshell",
        "audio",
        "control",
        "core",
        "diag",
        "diagnostics",
        "input",
        "net",
        "network",
        "platform",
        "render",
        "storage",
        "ui",
    ]
)
CONTRACT_ROOTS = set(
    ["compat", "locks", "registry", "registries", "repo", "safety", "schema", "schemas", "security", "specs"]
)
CONTENT_ROOTS = set(["bundles", "data", "modding", "models", "packs", "profiles", "templates"])
RELEASE_ROOTS = set(["updates"])
ARCHIVE_ALIAS_ROOTS = set(["attic", "legacy", "quarantine"])
REVIEW_ROOTS = set(["governance", "ide", "labs", "meta", "performance", "validation"])
CONTRACT_REVIEW_ROOTS = set(["lib", "libs"])
SPLIT_MIXED_ROOTS = set(
    [
        "bundles",
        "compat",
        "control",
        "core",
        "data",
        "locks",
        "modding",
        "net",
        "packs",
        "repo",
        "safety",
        "security",
        "specs",
        "templates",
        "updates",
    ]
)
SHIM_ROOTS = set(
    [
        "app",
        "appshell",
        "client",
        "compat",
        "control",
        "core",
        "diag",
        "launcher",
        "lib",
        "libs",
        "locks",
        "net",
        "repo",
        "schema",
        "schemas",
        "server",
        "setup",
        "ui",
    ]
)


def _utc_now():
    return _datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _posix(path):
    return path.replace(os.sep, "/")


def _repo_rel(repo_root, path):
    rel = os.path.relpath(path, repo_root)
    if rel == ".":
        return "."
    return _posix(rel)


def _read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_comment(line):
    in_string = False
    escaped = False
    out = []
    for char in line:
        if escaped:
            out.append(char)
            escaped = False
            continue
        if char == "\\" and in_string:
            out.append(char)
            escaped = True
            continue
        if char == '"':
            out.append(char)
            in_string = not in_string
            continue
        if char == "#" and not in_string:
            break
        out.append(char)
    return "".join(out).strip()


def _parse_simple_value(value):
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    return value


def _set_section(root, section_name):
    current = root
    for part in section_name.split("."):
        current = current.setdefault(part, {})
    return current


def _load_toml_fallback(path):
    data = {}
    current = data
    for raw_line in _read_text(path).splitlines():
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section:
                raise ValueError("empty TOML section in {0}".format(path))
            current = _set_section(data, section)
            continue
        if "=" not in line:
            raise ValueError("unsupported TOML line in {0}: {1}".format(path, raw_line))
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("empty TOML key in {0}".format(path))
        current[key] = _parse_simple_value(value)
    return data


def load_contract(path):
    try:
        import tomllib  # type: ignore
    except ImportError:
        print(
            "WARN: tomllib is unavailable; using minimal fallback TOML parser for this contract shape.",
            file=sys.stderr,
        )
        return _load_toml_fallback(path)
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def validate_contract_shape(contract):
    required_top = [
        "contract",
        "policy",
        "canonical_roots",
        "metadata_roots",
        "allowed_root_files",
        "transitional_aliases",
        "domain_roots",
        "generated_roots",
    ]
    errors = []
    for key in required_top:
        if key not in contract:
            errors.append("missing top-level contract key: {0}".format(key))
    meta = contract.get("contract", {})
    for key in ["id", "status", "enforcement", "phase"]:
        if key not in meta:
            errors.append("missing contract.{0}".format(key))
    if not isinstance(contract.get("canonical_roots", {}), dict):
        errors.append("canonical_roots must be an object")
    if not isinstance(contract.get("transitional_aliases", {}), dict):
        errors.append("transitional_aliases must be an object")
    if not isinstance(contract.get("domain_roots", {}), dict):
        errors.append("domain_roots must be an object")
    if not isinstance(contract.get("generated_roots", {}), dict):
        errors.append("generated_roots must be an object")
    return errors


def _list_from_section(value, key):
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        maybe = value.get(key, [])
        if isinstance(maybe, list):
            return list(maybe)
    return []


def _entry_kind(path):
    if os.path.islink(path):
        return "symlink"
    if os.path.isdir(path):
        return "directory"
    if os.path.isfile(path):
        return "file"
    return "other"


def _root_entries(repo_root):
    entries = []
    for name in os.listdir(repo_root):
        if name == ".git":
            continue
        entries.append(name)
    entries.sort(key=lambda item: (item.casefold(), item))
    return entries


def _phase_number(phase):
    if not phase:
        return None
    prefix = "CONVERGE-"
    if not phase.startswith(prefix):
        return None
    suffix = phase[len(prefix) :]
    digits = []
    for char in suffix:
        if char.isdigit():
            digits.append(char)
        else:
            break
    if not digits:
        return None
    return int("".join(digits))


def _classify(name, kind, contract):
    canonical = contract.get("canonical_roots", {})
    optional = contract.get("optional_roots", {})
    metadata = set(_list_from_section(contract.get("metadata_roots", {}), "allowed"))
    allowed_files = set(_list_from_section(contract.get("allowed_root_files", {}), "allowed"))
    allowed_patterns = _list_from_section(contract.get("allowed_root_files", {}), "patterns")
    aliases = contract.get("transitional_aliases", {})
    domains = contract.get("domain_roots", {})
    generated = contract.get("generated_roots", {})
    policy = contract.get("policy", {})

    if name in canonical:
        info = canonical[name]
        return {
            "classification": CLASS_CANONICAL,
            "target": name,
            "action": "retain",
            "notes": info.get("purpose", ""),
        }
    if name in optional:
        info = optional[name]
        return {
            "classification": CLASS_OPTIONAL,
            "target": name,
            "action": "retain_optional",
            "notes": info.get("purpose", ""),
        }
    if name in metadata:
        return {
            "classification": CLASS_METADATA,
            "target": name,
            "action": "retain_metadata",
            "notes": "Allowed metadata/config root.",
        }
    if kind == "file" and (name in allowed_files or any(fnmatch.fnmatchcase(name, pat) for pat in allowed_patterns)):
        return {
            "classification": CLASS_ALLOWED_FILE,
            "target": name,
            "action": "retain_allowed_file",
            "notes": "Allowed root file.",
        }
    if name in generated:
        info = generated[name]
        return {
            "classification": CLASS_GENERATED,
            "target": info.get("target", name),
            "action": "preserve_as_generated_or_review",
            "notes": info.get("notes", info.get("purpose", "")),
        }
    if name in domains:
        info = domains[name]
        return {
            "classification": CLASS_DOMAIN,
            "target": "split_per_domain_rules",
            "action": "split_required",
            "notes": "; ".join(info.get("targets", [])),
        }
    if name in aliases:
        info = aliases[name]
        if info.get("retired", False):
            target = info.get("target", "review")
            return {
                "classification": CLASS_VIOLATION,
                "target": target,
                "action": "retired_root_must_remain_absent",
                "notes": (
                    "Retired root alias; retained material belongs under {0}. {1}".format(
                        target, info.get("notes", "")
                    )
                ).strip(),
                "retire_by_phase": info.get("retire_by_phase", ""),
            }
        return {
            "classification": info.get("classification", CLASS_TRANSITIONAL),
            "target": info.get("target", "review"),
            "action": info.get("action", "review"),
            "notes": info.get("notes", ""),
            "retire_by_phase": info.get("retire_by_phase", ""),
        }

    default_class = policy.get("default_for_unknown_root", CLASS_VIOLATION)
    if default_class not in (CLASS_VIOLATION, CLASS_UNKNOWN):
        default_class = CLASS_VIOLATION
    return {
        "classification": default_class,
        "target": "review",
        "action": "review_or_remove_from_root",
        "notes": "No matching root classification in layout contract.",
    }


def head_sha(repo_root):
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None
    return out.decode("utf-8", "replace").strip()


def source_branch(repo_root):
    try:
        out = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None
    branch = out.decode("utf-8", "replace").strip()
    return branch or None


def contract_id_from_toml(path):
    if not os.path.exists(path):
        return ""
    in_contract = False
    for raw_line in _read_text(path).splitlines():
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            in_contract = line[1:-1].strip() == "contract"
            continue
        if in_contract and line.startswith("id") and "=" in line:
            _key, value = line.split("=", 1)
            try:
                return _parse_simple_value(value)
            except Exception:
                return value.strip().strip('"')
    return ""


def missing_required_roots(repo_root, contract):
    missing = []
    for name, info in sorted(contract.get("canonical_roots", {}).items()):
        if info.get("required", False) and not os.path.exists(os.path.join(repo_root, name)):
            missing.append(name)
    return missing


def counts_by_classification(roots):
    counts = {}
    for root in roots:
        cls = root["classification"]
        counts[cls] = counts.get(cls, 0) + 1
    return dict(sorted(counts.items()))


def detailed_classification(name, kind, raw_class):
    if raw_class == CLASS_VIOLATION and kind == "file":
        return CLASS_UNKNOWN
    if raw_class == CLASS_TRANSITIONAL:
        if name in PRODUCT_ROOTS:
            return CLASS_TRANSITIONAL_PRODUCT
        if name in RUNTIME_ROOTS:
            return CLASS_TRANSITIONAL_RUNTIME
        if name in CONTRACT_ROOTS or name in CONTRACT_REVIEW_ROOTS:
            return CLASS_TRANSITIONAL_CONTRACT
        if name in CONTENT_ROOTS:
            return CLASS_TRANSITIONAL_CONTENT
        if name in RELEASE_ROOTS:
            return CLASS_TRANSITIONAL_RELEASE
        if name in ARCHIVE_ALIAS_ROOTS:
            return CLASS_TRANSITIONAL_ARCHIVE
        if name in REVIEW_ROOTS:
            return CLASS_UNKNOWN
    return raw_class


def ownership_surface_for(name, classification):
    if classification == CLASS_CANONICAL:
        return name if name in OWNERSHIP_SURFACES else "unknown"
    if classification == CLASS_OPTIONAL:
        if name == "sdk":
            return "external"
        if name == "examples":
            return "docs"
        return "unknown"
    if classification in (CLASS_METADATA, CLASS_ALLOWED_FILE):
        return "metadata"
    if classification == CLASS_GENERATED:
        return "generated"
    if classification == CLASS_DOMAIN:
        return "mixed_split_required"
    if classification == CLASS_TRANSITIONAL_PRODUCT:
        return "apps"
    if classification == CLASS_TRANSITIONAL_RUNTIME:
        return "runtime"
    if classification == CLASS_TRANSITIONAL_CONTRACT:
        return "contracts" if name not in CONTRACT_REVIEW_ROOTS else "unknown"
    if classification == CLASS_TRANSITIONAL_CONTENT:
        return "content"
    if classification == CLASS_TRANSITIONAL_RELEASE:
        return "release"
    if classification == CLASS_TRANSITIONAL_ARCHIVE:
        return "archive"
    return "unknown"


def migration_action_for(name, classification):
    if classification in (CLASS_CANONICAL, CLASS_OPTIONAL):
        return "keep"
    if classification == CLASS_METADATA:
        return "retain_metadata"
    if classification == CLASS_ALLOWED_FILE:
        return "retain_file"
    if classification == CLASS_GENERATED:
        return "ignore_generated"
    if classification == CLASS_DOMAIN:
        return "split"
    if classification == CLASS_TRANSITIONAL_PRODUCT:
        return "move"
    if classification == CLASS_TRANSITIONAL_RUNTIME:
        return "split" if name in ("control", "core", "net") else "move"
    if classification == CLASS_TRANSITIONAL_CONTRACT:
        if name in ("schema", "schemas"):
            return "merge"
        if name in ("compat", "locks"):
            return "review"
        if name in CONTRACT_REVIEW_ROOTS:
            return "review"
        return "split"
    if classification == CLASS_TRANSITIONAL_CONTENT:
        return "split" if name in SPLIT_MIXED_ROOTS else "move"
    if classification == CLASS_TRANSITIONAL_RELEASE:
        return "split"
    if classification == CLASS_TRANSITIONAL_ARCHIVE:
        return "archive"
    return "review"


def authority_status_for(classification):
    if classification in (CLASS_CANONICAL, CLASS_OPTIONAL):
        return "authoritative_current"
    if classification in (CLASS_METADATA, CLASS_ALLOWED_FILE):
        return "metadata"
    if classification == CLASS_GENERATED:
        return "generated_non_authoritative"
    if classification == CLASS_TRANSITIONAL_ARCHIVE:
        return "legacy_reference"
    if classification in TRANSITIONAL_CLASSES or classification == CLASS_DOMAIN:
        return "transitional"
    return "unknown"


def current_role_for(classification):
    if classification == CLASS_CANONICAL:
        return "Current canonical target root for the source repository layout."
    if classification == CLASS_OPTIONAL:
        return "Optional target root if a real external surface exists."
    if classification == CLASS_METADATA:
        return "Repository metadata or local/project configuration root."
    if classification == CLASS_ALLOWED_FILE:
        return "Allowed root-level project file."
    if classification == CLASS_TRANSITIONAL_PRODUCT:
        return "Current top-level product root retained until product entrypoint convergence."
    if classification == CLASS_TRANSITIONAL_RUNTIME:
        return "Current runtime/AppShell/platform-adjacent root retained until runtime convergence."
    if classification == CLASS_TRANSITIONAL_CONTRACT:
        return "Current contract, schema, compatibility, or adjacent root retained until contract convergence."
    if classification == CLASS_TRANSITIONAL_CONTENT:
        return "Current content, data, pack, profile, or export-adjacent root retained until split review."
    if classification == CLASS_TRANSITIONAL_RELEASE:
        return "Current release, update, or control-plane-adjacent root retained until split review."
    if classification == CLASS_TRANSITIONAL_ARCHIVE:
        return "Current historical, legacy, or quarantined root retained until archive convergence."
    if classification == CLASS_DOMAIN:
        return "Current mixed domain root that must be split by ownership."
    if classification == CLASS_GENERATED:
        return "Generated, ephemeral, or release-adjacent output root."
    return "Unclassified root entry requiring manual ownership review."


def proposed_target_for(name, classification, raw_target):
    if classification == CLASS_DOMAIN:
        return "contracts/game/content/docs/tests split"
    if classification == CLASS_GENERATED:
        if name == "dist":
            return "generated distribution output; future distribution contract review"
        if name == "artifacts":
            return "generated evidence or release artifact review"
        return "generated build output"
    return raw_target or "review"


def phase_hint_for(root):
    name = root["name"]
    cls = root["classification"]
    if cls in (CLASS_CANONICAL, CLASS_OPTIONAL, CLASS_METADATA, CLASS_ALLOWED_FILE):
        return "none"
    if cls == CLASS_TRANSITIONAL_ARCHIVE or name in ("attic", "legacy", "quarantine"):
        return "CONVERGE-05"
    if cls == CLASS_TRANSITIONAL_CONTRACT or name in ("schema", "schemas", "compat", "locks", "contracts", "safety", "security", "specs"):
        return "CONVERGE-06"
    if cls == CLASS_TRANSITIONAL_RUNTIME or name in ("appshell", "app", "platform", "render", "ui", "input", "audio", "net", "diag", "storage", "control", "core"):
        return "CONVERGE-07"
    if cls == CLASS_TRANSITIONAL_PRODUCT or name in ("client", "server", "setup", "launcher"):
        return "CONVERGE-08"
    if cls in (CLASS_DOMAIN, CLASS_TRANSITIONAL_CONTENT):
        return "CONVERGE-09"
    return "review"


def risk_level_for(root):
    name = root["name"]
    cls = root["classification"]
    if cls in (CLASS_CANONICAL, CLASS_METADATA, CLASS_ALLOWED_FILE, CLASS_OPTIONAL):
        if name == "runtime":
            return "medium"
        return "low"
    if cls == CLASS_GENERATED:
        return "review"
    if cls == CLASS_DOMAIN:
        return "high"
    if cls == CLASS_TRANSITIONAL_CONTRACT:
        return "review" if name in CONTRACT_REVIEW_ROOTS or name in ("compat", "locks") else "high"
    if cls == CLASS_TRANSITIONAL_CONTENT:
        return "high" if name in SPLIT_MIXED_ROOTS else "medium"
    if cls == CLASS_TRANSITIONAL_RUNTIME:
        return "high" if name in ("control", "core", "net") else "medium"
    if cls == CLASS_TRANSITIONAL_PRODUCT:
        return "medium"
    if cls == CLASS_TRANSITIONAL_RELEASE:
        return "high"
    if cls == CLASS_TRANSITIONAL_ARCHIVE:
        return "low"
    return "review"


def split_required_for(name, classification, action):
    if classification == CLASS_DOMAIN:
        return True
    if action == "split":
        return True
    return name in SPLIT_MIXED_ROOTS


def enrich_root(repo_root, name, kind, info):
    classification = detailed_classification(name, kind, info.get("classification", CLASS_UNKNOWN))
    action = migration_action_for(name, classification)
    root = {
        "name": name,
        "path": _repo_rel(repo_root, os.path.join(repo_root, name)),
        "kind": kind,
        "present": True,
        "classification": classification,
        "ownership_surface": ownership_surface_for(name, classification),
        "current_role": current_role_for(classification),
        "proposed_target": proposed_target_for(name, classification, info.get("target", "review")),
        "migration_action": action,
        "split_required": split_required_for(name, classification, action),
        "risk_level": "review",
        "phase_hint": "review",
        "authority_status": authority_status_for(classification),
        "notes": info.get("notes", ""),
    }
    if name == "runtime" and classification == CLASS_CANONICAL:
        root["notes"] = (
            (root["notes"] + " ").strip()
            + " Present canonical target root; inspect contents before treating adjacent runtime roots as converged."
        ).strip()
    if classification == CLASS_UNKNOWN and not root["notes"]:
        root["notes"] = "No matching root classification in layout contract; manual review required."
    root["risk_level"] = risk_level_for(root)
    root["phase_hint"] = phase_hint_for(root)
    return root


def collect_roots(repo_root, contract):
    roots = []
    for name in _root_entries(repo_root):
        path = os.path.join(repo_root, name)
        kind = _entry_kind(path)
        info = _classify(name, kind, contract)
        roots.append(enrich_root(repo_root, name, kind, info))
    return roots


def dependencies_for(root):
    cls = root["classification"]
    name = root["name"]
    if cls in (CLASS_CANONICAL, CLASS_OPTIONAL, CLASS_METADATA, CLASS_ALLOWED_FILE):
        return []
    if cls == CLASS_GENERATED:
        return ["requires generated-output provenance review"]
    if cls == CLASS_DOMAIN:
        return ["requires domain split inspection", "requires contract convergence first", "requires fixtures/tests inventory"]
    if cls == CLASS_TRANSITIONAL_PRODUCT:
        return ["requires product entrypoint audit", "requires build path update", "requires docs cross-reference update"]
    if cls == CLASS_TRANSITIONAL_RUNTIME:
        return ["requires runtime boundary review", "requires build/import path update", "requires docs cross-reference update"]
    if cls == CLASS_TRANSITIONAL_CONTRACT:
        deps = ["requires contract convergence first", "requires docs cross-reference update"]
        if name in ("schema", "schemas"):
            deps.append("requires contracts/schemas/projection ownership review")
        if name in ("compat", "locks"):
            deps.append("requires mixed contract-adjacent root review")
        if name in CONTRACT_REVIEW_ROOTS:
            deps.append("requires manual library ownership review")
        return deps
    if cls == CLASS_TRANSITIONAL_CONTENT:
        return ["requires content/data ownership review", "requires pack/profile authority review"]
    if cls == CLASS_TRANSITIONAL_RELEASE:
        return ["requires release/control-plane ownership review", "requires distribution contract sequencing"]
    if cls == CLASS_TRANSITIONAL_ARCHIVE:
        return ["requires archive provenance review"]
    return ["requires manual root ownership review"]


def shim_required_for(root):
    return root["name"] in SHIM_ROOTS and root["migration_action"] in ("move", "merge", "split", "review")


def preserve_paths_for(root, shim_required):
    if shim_required:
        return "Compatibility shims or redirects may be required before changing this root path."
    if root["classification"] == CLASS_GENERATED:
        return "Do not preserve generated path as source authority; preserve only if external workflows require it."
    if root["classification"] in (CLASS_CANONICAL, CLASS_OPTIONAL, CLASS_METADATA, CLASS_ALLOWED_FILE):
        return "No compatibility shim expected because the entry is retained."
    return "Preserve current path until manual review proves no compatibility dependency."


def infer_move_entry(root):
    shim_required = shim_required_for(root)
    status = "review" if root["migration_action"] == "review" else "not_started"
    return {
        "name": root["name"],
        "current_path": root["path"],
        "proposed_target": root["proposed_target"],
        "action": root["migration_action"],
        "classification": root["classification"],
        "ownership_surface": root["ownership_surface"],
        "split_required": root["split_required"],
        "risk_level": root["risk_level"],
        "phase_hint": root["phase_hint"],
        "dependencies": dependencies_for(root),
        "preserve_paths": preserve_paths_for(root, shim_required),
        "shim_required": shim_required,
        "semantic_change_allowed": False,
        "build_change_allowed": False,
        "notes": root["notes"],
        "status": status,
        "completed_phase": "",
        "completed_target": "",
        "completed_notes": "",
    }


def load_existing_move_map(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return {}
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        return {}
    by_name = {}
    for entry in entries:
        if isinstance(entry, dict) and entry.get("name"):
            by_name[entry["name"]] = entry
    return by_name


def completed_archive_move_entries(repo_root, roots):
    present = set(root["name"] for root in roots)
    completed = []
    archive_targets = {
        "attic": "archive/historical/attic",
        "legacy": "archive/legacy",
        "quarantine": "archive/quarantine",
    }
    for name, target in sorted(archive_targets.items()):
        if name in present:
            continue
        target_path = os.path.join(repo_root, *target.split("/"))
        if not os.path.exists(target_path):
            continue
        completed.append(
            {
                "name": name,
                "current_path": name,
                "proposed_target": target,
                "action": "archive",
                "classification": CLASS_TRANSITIONAL_ARCHIVE,
                "ownership_surface": "archive",
                "split_required": False,
                "risk_level": "low",
                "phase_hint": "CONVERGE-05",
                "dependencies": [],
                "preserve_paths": "Root path retired in CONVERGE-05; do not recreate a root-level compatibility shim.",
                "shim_required": False,
                "semantic_change_allowed": False,
                "build_change_allowed": False,
                "notes": "Completed in CONVERGE-05; root-level {0}/ moved under {1}/.".format(name, target),
                "status": "completed",
                "completed_phase": "CONVERGE-05",
                "completed_target": target,
                "completed_notes": "Root-level {0}/ is retired; material is retained under {1}/.".format(name, target),
            }
        )
    return completed


def completed_contract_move_entries(repo_root, roots):
    present = set(root["name"] for root in roots)
    completed = []
    contract_targets = {
        "schema": {
            "target": "contracts/schemas",
            "action": "merge",
            "notes": "Completed in CONVERGE-06; root-level schema/ moved under contracts/schemas/.",
            "completed_notes": "Root-level schema/ is retired; retained schema law lives under contracts/schemas/.",
        },
        "schemas": {
            "target": "contracts/schemas",
            "action": "merge",
            "notes": "Completed in CONVERGE-06; root-level schemas/ merged under contracts/schemas/.",
            "completed_notes": "Root-level schemas/ is retired; retained validator-facing schema projections live under contracts/schemas/.",
        },
    }
    for name, info in sorted(contract_targets.items()):
        if name in present:
            continue
        target = info["target"]
        target_path = os.path.join(repo_root, *target.split("/"))
        if not os.path.exists(target_path):
            continue
        completed.append(
            {
                "name": name,
                "current_path": name,
                "proposed_target": target,
                "action": info["action"],
                "classification": CLASS_TRANSITIONAL_CONTRACT,
                "ownership_surface": "contracts",
                "split_required": False,
                "risk_level": "medium",
                "phase_hint": "CONVERGE-06",
                "dependencies": [],
                "preserve_paths": "Root path retired in CONVERGE-06; active references should use contracts/schemas/.",
                "shim_required": False,
                "semantic_change_allowed": False,
                "build_change_allowed": False,
                "notes": info["notes"],
                "status": "completed",
                "completed_phase": "CONVERGE-06",
                "completed_target": target,
                "completed_notes": info["completed_notes"],
            }
        )
    for name in ("registry", "registries"):
        if name in present:
            continue
        completed.append(
            {
                "name": name,
                "current_path": name,
                "proposed_target": "contracts/registries",
                "action": "review_absent",
                "classification": CLASS_TRANSITIONAL_CONTRACT,
                "ownership_surface": "contracts",
                "split_required": False,
                "risk_level": "low",
                "phase_hint": "CONVERGE-06",
                "dependencies": [],
                "preserve_paths": "Root path is absent; do not create a new root-level registry authority.",
                "shim_required": False,
                "semantic_change_allowed": False,
                "build_change_allowed": False,
                "notes": "Confirmed absent in CONVERGE-06; future registry contracts belong under contracts/registries/.",
                "status": "completed",
                "completed_phase": "CONVERGE-06",
                "completed_target": "contracts/registries",
                "completed_notes": "Root-level {0}/ was not present during CONVERGE-06.".format(name),
            }
        )
    return completed


def completed_runtime_move_entries(repo_root, roots):
    present = set(root["name"] for root in roots)
    completed = []
    runtime_targets = {
        "app": {
            "target": "runtime/app",
            "action": "move",
            "notes": "Completed in CONVERGE-07; root-level app/ moved under runtime/app/.",
            "completed_notes": "Root-level app/ is retired; retained app runtime substrate lives under runtime/app/.",
        },
        "appshell": {
            "target": "runtime/appshell",
            "action": "move",
            "notes": "Completed in CONVERGE-07; root-level appshell/ moved under runtime/appshell/.",
            "completed_notes": "Root-level appshell/ is retired; AppShell source lives under runtime/appshell/.",
        },
        "diag": {
            "target": "runtime/diagnostics",
            "action": "move",
            "notes": "Completed in CONVERGE-07; root-level diag/ moved under runtime/diagnostics/.",
            "completed_notes": "Root-level diag/ is retired; source diagnostics live under runtime/diagnostics/.",
        },
        "ui": {
            "target": "runtime/ui",
            "action": "move",
            "notes": "Completed in CONVERGE-07; root-level ui/ moved under runtime/ui/.",
            "completed_notes": "Root-level ui/ is retired; shared UI runtime source lives under runtime/ui/.",
        },
    }
    for name, info in sorted(runtime_targets.items()):
        if name in present:
            continue
        target = info["target"]
        target_path = os.path.join(repo_root, *target.split("/"))
        if not os.path.exists(target_path):
            continue
        completed.append(
            {
                "name": name,
                "current_path": name,
                "proposed_target": target,
                "action": info["action"],
                "classification": CLASS_TRANSITIONAL_RUNTIME,
                "ownership_surface": "runtime",
                "split_required": False,
                "risk_level": "medium",
                "phase_hint": "CONVERGE-07",
                "dependencies": [],
                "preserve_paths": "Root path retired in CONVERGE-07; active references should use {0}/.".format(target),
                "shim_required": False,
                "semantic_change_allowed": False,
                "build_change_allowed": False,
                "notes": info["notes"],
                "status": "completed",
                "completed_phase": "CONVERGE-07",
                "completed_target": target,
                "completed_notes": info["completed_notes"],
            }
        )
    absent_targets = {
        "audio": "runtime/audio",
        "diagnostics": "runtime/diagnostics",
        "input": "runtime/input",
        "network": "runtime/network",
        "platform": "runtime/platform",
        "render": "runtime/render",
        "storage": "runtime/storage",
    }
    for name, target in sorted(absent_targets.items()):
        if name in present:
            continue
        completed.append(
            {
                "name": name,
                "current_path": name,
                "proposed_target": target,
                "action": "review_absent",
                "classification": CLASS_TRANSITIONAL_RUNTIME,
                "ownership_surface": "runtime",
                "split_required": False,
                "risk_level": "low",
                "phase_hint": "CONVERGE-07",
                "dependencies": [],
                "preserve_paths": "Root path is absent; do not create a new root-level runtime-adapter authority.",
                "shim_required": False,
                "semantic_change_allowed": False,
                "build_change_allowed": False,
                "notes": "Confirmed absent in CONVERGE-07; future source material belongs under {0}/.".format(target),
                "status": "completed",
                "completed_phase": "CONVERGE-07",
                "completed_target": target,
                "completed_notes": "Root-level {0}/ was not present during CONVERGE-07.".format(name),
            }
        )
    return completed


def merge_move_map(repo_root, existing, roots):
    entries = []
    completed = completed_archive_move_entries(repo_root, roots)
    completed.extend(completed_contract_move_entries(repo_root, roots))
    completed.extend(completed_runtime_move_entries(repo_root, roots))
    names = sorted(set(root["name"] for root in roots), key=lambda item: (item.casefold(), item))
    inferred_by_name = dict((root["name"], infer_move_entry(root)) for root in roots)
    for name in names:
        inferred = inferred_by_name.get(name)
        if inferred:
            entries.append(inferred)
    entries.extend(completed)
    entries.sort(key=lambda item: (item.get("name", "").casefold(), item.get("name", "")))
    return entries


def write_json(path, data):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=False)
        handle.write("\n")


def build_outputs(repo_root, contract, roots, inventory_out, move_map_path):
    generated_at = _utc_now()
    meta = contract.get("contract", {})
    sha = head_sha(repo_root)
    branch = source_branch(repo_root)
    allowlist_id = contract_id_from_toml(os.path.join(repo_root, "contracts", "repo", "root_allowlist.toml"))
    inventory = {
        "schema_version": "1.0",
        "generated_at_utc": generated_at,
        "repo_root": ".",
        "head_sha": sha,
        "source_branch": branch,
        "contract_id": meta.get("id", ""),
        "contract_phase": meta.get("phase", ""),
        "allowlist_contract_id": allowlist_id,
        "inventory_status": "complete",
        "roots": roots,
    }
    move_map = {
        "schema_version": "1.0",
        "generated_at_utc": generated_at,
        "repo_root": ".",
        "head_sha": sha,
        "source_branch": branch,
        "map_status": "complete",
        "entries": merge_move_map(repo_root, load_existing_move_map(move_map_path), roots),
    }
    return inventory, move_map


def strict_violations(repo_root, contract, roots, contract_errors):
    policy = contract.get("policy", {})
    current_phase = _phase_number(contract.get("contract", {}).get("phase", ""))
    violations = []
    if contract_errors:
        violations.extend("malformed contract: {0}".format(error) for error in contract_errors)
    if policy.get("strict_fails_missing_required_root", True):
        for name in missing_required_roots(repo_root, contract):
            violations.append("missing required canonical root: {0}".format(name))
    if policy.get("strict_fails_unknown_root", True):
        for root in roots:
            if root["classification"] in (CLASS_UNKNOWN, CLASS_VIOLATION):
                violations.append("unknown or violating root: {0}".format(root["name"]))
    if policy.get("strict_fails_forbidden_root", True):
        for root in roots:
            if root["classification"] == "forbidden":
                violations.append("forbidden root: {0}".format(root["name"]))
    for root in roots:
        if root["classification"] == CLASS_GENERATED:
            continue
        if root["name"] in contract.get("generated_roots", {}):
            violations.append("generated root present without generated classification: {0}".format(root["name"]))
    if current_phase is not None:
        aliases = contract.get("transitional_aliases", {})
        for root in roots:
            info = aliases.get(root["name"], {})
            retire_phase = _phase_number(info.get("retire_by_phase", ""))
            if retire_phase is not None and current_phase >= retire_phase:
                violations.append("stale alias after retire phase: {0}".format(root["name"]))
    return violations


def build_report(repo_root, contract, roots, contract_errors, strict):
    missing = missing_required_roots(repo_root, contract)
    split_required = [root["name"] for root in roots if root.get("split_required")]
    transitional = [root["name"] for root in roots if root["classification"] in TRANSITIONAL_CLASSES]
    generated = [root["name"] for root in roots if root["classification"] == CLASS_GENERATED]
    unknown = [root["name"] for root in roots if root["classification"] in (CLASS_UNKNOWN, CLASS_VIOLATION)]
    violations = strict_violations(repo_root, contract, roots, contract_errors)
    strict_result = "fail" if strict and violations else "pass"
    if not strict:
        strict_result = "not_run"
    return {
        "contract_id": contract.get("contract", {}).get("id", ""),
        "contract_phase": contract.get("contract", {}).get("phase", ""),
        "head_sha": head_sha(repo_root),
        "strict": bool(strict),
        "summary_counts": counts_by_classification(roots),
        "unknown_roots": unknown,
        "split_required_roots": split_required,
        "transitional_aliases": transitional,
        "generated_roots": generated,
        "missing_required_canonical_roots": missing,
        "contract_errors": contract_errors,
        "strict_violations": violations,
        "strict_result": strict_result,
    }


def print_text_report(report):
    print("Repo layout audit")
    print("contract_id: {0}".format(report["contract_id"]))
    print("contract_phase: {0}".format(report["contract_phase"]))
    print("head_sha: {0}".format(report["head_sha"]))
    print("")
    print("Summary counts:")
    for key, value in report["summary_counts"].items():
        print("- {0}: {1}".format(key, value))
    print("")
    print("Unknown/review roots:")
    if report["unknown_roots"]:
        for name in report["unknown_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Split-required roots:")
    if report["split_required_roots"]:
        for name in report["split_required_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Transitional aliases:")
    if report["transitional_aliases"]:
        for name in report["transitional_aliases"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Generated roots:")
    if report["generated_roots"]:
        for name in report["generated_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Missing required canonical roots:")
    if report["missing_required_canonical_roots"]:
        for name in report["missing_required_canonical_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    if report["contract_errors"]:
        print("Contract errors:")
        for error in report["contract_errors"]:
            print("- {0}".format(error))
        print("")
    if report["strict_result"] == "not_run":
        print("Strict-mode result: not run")
        if report["strict_violations"]:
            print("Potential strict violations:")
            for violation in report["strict_violations"]:
                print("- {0}".format(violation))
        return
    print("Strict-mode result: {0}".format(report["strict_result"]))
    if report["strict_violations"]:
        print("Strict violations:")
        for violation in report["strict_violations"]:
            print("- {0}".format(violation))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Audit repository root layout against layout.contract.toml.")
    parser.add_argument("--repo-root", default=".", help="Repository root to audit.")
    parser.add_argument("--contract", default="contracts/repo/layout.contract.toml", help="Layout contract path.")
    parser.add_argument("--inventory-out", default="tools/migration/root_inventory.json", help="Inventory output JSON path.")
    parser.add_argument("--move-map", default="tools/migration/root_move_map.json", help="Move-map output JSON path.")
    parser.add_argument("--strict", action="store_true", help="Fail when strict layout violations are present.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report JSON.")
    parser.add_argument("--no-write", action="store_true", help="Do not write inventory or move-map outputs.")
    parser.add_argument("--include-dotfiles", action="store_true", help="Accepted for compatibility; dot metadata roots are included by default.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract
    if not os.path.isabs(contract_path):
        contract_path = os.path.join(repo_root, contract_path)
    inventory_out = args.inventory_out
    if not os.path.isabs(inventory_out):
        inventory_out = os.path.join(repo_root, inventory_out)
    move_map_path = args.move_map
    if not os.path.isabs(move_map_path):
        move_map_path = os.path.join(repo_root, move_map_path)

    try:
        contract = load_contract(contract_path)
    except Exception as exc:
        print("ERROR: failed to load contract {0}: {1}".format(contract_path, exc), file=sys.stderr)
        return 2

    contract_errors = validate_contract_shape(contract)
    if contract_errors and args.strict:
        pass
    elif contract_errors:
        print("WARN: malformed contract shape detected; continuing audit mode.", file=sys.stderr)

    roots = collect_roots(repo_root, contract)
    inventory, move_map = build_outputs(repo_root, contract, roots, inventory_out, move_map_path)

    if not args.no_write:
        try:
            write_json(inventory_out, inventory)
            write_json(move_map_path, move_map)
        except Exception as exc:
            print("ERROR: failed to write outputs: {0}".format(exc), file=sys.stderr)
            return 2

    report = build_report(repo_root, contract, roots, contract_errors, args.strict)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)

    if args.strict and report["strict_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
