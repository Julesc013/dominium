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
CLASS_DOMAIN = "split_required_domain_root"
CLASS_GENERATED = "generated_or_ephemeral"
CLASS_VIOLATION = "violation"
CLASS_UNKNOWN = "unknown_needs_review"


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


def collect_roots(repo_root, contract):
    roots = []
    for name in _root_entries(repo_root):
        path = os.path.join(repo_root, name)
        kind = _entry_kind(path)
        info = _classify(name, kind, contract)
        roots.append(
            {
                "name": name,
                "path": _repo_rel(repo_root, path),
                "kind": kind,
                "classification": info.get("classification", CLASS_UNKNOWN),
                "target": info.get("target", "review"),
                "action": info.get("action", "review"),
                "notes": info.get("notes", ""),
                "present": True,
            }
        )
    return roots


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


def phase_hint_for(root):
    name = root["name"]
    cls = root["classification"]
    if name in ("archive", "attic", "legacy", "quarantine"):
        return "CONVERGE-05"
    if name in ("schema", "schemas", "compat", "locks", "contracts", "safety", "security", "specs"):
        return "CONVERGE-06"
    if name in ("runtime", "appshell", "app", "platform", "render", "ui", "input", "audio", "net", "diag", "storage", "control", "core"):
        return "CONVERGE-07"
    if name in ("client", "server", "setup", "launcher"):
        return "CONVERGE-08"
    if cls == CLASS_DOMAIN:
        return "CONVERGE-09"
    return "review"


def risk_level_for(root):
    name = root["name"]
    cls = root["classification"]
    if cls in (CLASS_CANONICAL, CLASS_METADATA, CLASS_ALLOWED_FILE, CLASS_OPTIONAL):
        return "low"
    if cls == CLASS_GENERATED:
        return "review"
    if cls == CLASS_DOMAIN:
        return "high"
    if name in ("schema", "schemas", "packs", "data", "repo", "compat", "locks", "security", "specs"):
        return "high"
    if name in ("client", "server", "setup", "launcher", "app", "appshell", "runtime", "core", "control", "net", "ui", "diag"):
        return "medium"
    if name in ("attic", "legacy", "quarantine"):
        return "low"
    return "review"


def infer_move_entry(root):
    split_required = root["classification"] == CLASS_DOMAIN
    return {
        "name": root["name"],
        "current_path": root["path"],
        "proposed_target": root["target"],
        "action": root["action"],
        "classification": root["classification"],
        "split_required": split_required,
        "risk_level": risk_level_for(root),
        "phase_hint": phase_hint_for(root),
        "notes": root["notes"],
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


def merge_move_map(existing, roots):
    entries = []
    names = sorted(set(existing.keys()) | set(root["name"] for root in roots), key=lambda item: (item.casefold(), item))
    inferred_by_name = dict((root["name"], infer_move_entry(root)) for root in roots)
    for name in names:
        inferred = inferred_by_name.get(name)
        if name in existing and inferred:
            merged = dict(inferred)
            old = existing[name]
            for key, value in old.items():
                if value not in (None, "", [], {}):
                    merged[key] = value
            for key, value in inferred.items():
                if key not in merged or merged[key] in (None, "", [], {}):
                    merged[key] = value
            entries.append(merged)
        elif name in existing:
            entries.append(existing[name])
        else:
            entries.append(inferred)
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
    inventory = {
        "generated_at_utc": generated_at,
        "repo_root": _posix(os.path.abspath(repo_root)),
        "contract_id": meta.get("id", ""),
        "contract_phase": meta.get("phase", ""),
        "head_sha": head_sha(repo_root),
        "roots": roots,
    }
    move_map = {
        "generated_at_utc": generated_at,
        "repo_root": _posix(os.path.abspath(repo_root)),
        "contract_id": meta.get("id", ""),
        "contract_phase": meta.get("phase", ""),
        "head_sha": inventory["head_sha"],
        "entries": merge_move_map(load_existing_move_map(move_map_path), roots),
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
    split_required = [root["name"] for root in roots if root["classification"] == CLASS_DOMAIN]
    transitional = [root["name"] for root in roots if root["classification"] == CLASS_TRANSITIONAL]
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
    print("Unknown/violating roots:")
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
