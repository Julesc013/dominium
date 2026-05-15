#!/usr/bin/env python3
"""Audit root-level repository entries against root_allowlist.toml."""

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
CLASS_TRANSITIONAL = "transitional"
CLASS_GENERATED = "generated_or_ephemeral"
CLASS_VIOLATION = "violation"
CLASS_UNKNOWN = "unknown_needs_review"


def utc_now():
    return _datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def posix_path(path):
    return path.replace(os.sep, "/")


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return ast.literal_eval(value)
    return value


def strip_comment(line):
    out = []
    in_string = False
    escaped = False
    for char in line:
        if escaped:
            out.append(char)
            escaped = False
            continue
        if in_string and char == "\\":
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


def split_top_level(value, delimiter=","):
    parts = []
    buf = []
    in_string = False
    escaped = False
    depth_square = 0
    depth_brace = 0
    for char in value:
        if escaped:
            buf.append(char)
            escaped = False
            continue
        if in_string and char == "\\":
            buf.append(char)
            escaped = True
            continue
        if char == '"':
            buf.append(char)
            in_string = not in_string
            continue
        if not in_string:
            if char == "[":
                depth_square += 1
            elif char == "]":
                depth_square -= 1
            elif char == "{":
                depth_brace += 1
            elif char == "}":
                depth_brace -= 1
            elif char == delimiter and depth_square == 0 and depth_brace == 0:
                parts.append("".join(buf).strip())
                buf = []
                continue
        buf.append(char)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def parse_value(value):
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    if value.startswith("{") and value.endswith("}"):
        result = {}
        inner = value[1:-1].strip()
        if not inner:
            return result
        for part in split_top_level(inner):
            if "=" not in part:
                raise ValueError("invalid inline table item: {0}".format(part))
            key, item_value = part.split("=", 1)
            result[strip_quotes(key.strip())] = parse_value(item_value)
        return result
    return value


def set_section(root, section_name):
    current = root
    for raw_part in section_name.split("."):
        part = strip_quotes(raw_part.strip())
        current = current.setdefault(part, {})
    return current


def load_toml_fallback(path):
    data = {}
    current = data
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = strip_comment(raw_line)
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current = set_section(data, line[1:-1].strip())
                continue
            if "=" not in line:
                raise ValueError("unsupported TOML line: {0}".format(raw_line.rstrip()))
            raw_key, raw_value = line.split("=", 1)
            current[strip_quotes(raw_key.strip())] = parse_value(raw_value)
    return data


def load_contract(path):
    try:
        import tomllib  # type: ignore
    except ImportError:
        print(
            "WARN: tomllib is unavailable; using minimal fallback TOML parser for this allowlist shape.",
            file=sys.stderr,
        )
        return load_toml_fallback(path)
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def validate_contract_shape(contract):
    errors = []
    required = [
        "contract",
        "policy",
        "canonical_directories",
        "optional_directories",
        "metadata_directories",
        "allowed_root_files",
        "transitional_directories",
        "forbidden_root_patterns",
    ]
    for key in required:
        if key not in contract:
            errors.append("missing top-level key: {0}".format(key))
    meta = contract.get("contract", {})
    for key in ["id", "status", "enforcement", "phase"]:
        if key not in meta:
            errors.append("missing contract.{0}".format(key))
    return errors


def normalize_exception_path(path):
    normalized = str(path or "").replace("\\", "/").strip()
    while normalized.endswith("/") and normalized != "/":
        normalized = normalized[:-1]
    return normalized


def load_exception_ledger(path):
    if not os.path.exists(path):
        return {"contract": {}, "policy": {}, "exceptions": {}}, ["missing exception ledger: {0}".format(path)]
    try:
        data = load_contract(path)
    except Exception as exc:
        return {"contract": {}, "policy": {}, "exceptions": {}}, [
            "failed to load exception ledger {0}: {1}".format(path, exc)
        ]
    return data, validate_exception_ledger_shape(data, os.path.dirname(os.path.dirname(os.path.dirname(path))))


def validate_exception_ledger_shape(ledger, repo_root=None):
    errors = []
    for key in ["contract", "policy", "exceptions"]:
        if key not in ledger:
            errors.append("missing top-level exception ledger key: {0}".format(key))
    meta = ledger.get("contract", {})
    for key in ["id", "status", "phase"]:
        if key not in meta:
            errors.append("missing exception contract.{0}".format(key))
    if meta.get("id") and meta.get("id") != "dominium.repo.layout_exceptions.v1":
        errors.append("unexpected exception contract id: {0}".format(meta.get("id")))
    policy = ledger.get("policy", {})
    exceptions = ledger.get("exceptions", {})
    if not isinstance(exceptions, dict):
        errors.append("exceptions must be an object")
        return errors
    required = [
        "path",
        "kind",
        "classification",
        "reason",
        "retirement_phase",
        "target",
        "risk",
        "created_phase",
        "notes",
    ]
    allowed_kinds = set(["directory", "file", "pattern"])
    allowed_classes = set(
        ["transitional", "generated_exception", "metadata_exception", "compatibility_shim", "partial_review", "blocked"]
    )
    allowed_risks = set(["low", "medium", "high", "review"])
    fail_missing = bool(policy.get("exceptions_fail_if_path_missing", False))
    fail_expired = bool(policy.get("exceptions_fail_if_expired", True))
    for exception_id, info in sorted(exceptions.items()):
        if not isinstance(info, dict):
            errors.append("exception {0} must be an object".format(exception_id))
            continue
        for key in required:
            if key not in info or info.get(key) == "":
                errors.append("exception {0} missing {1}".format(exception_id, key))
        if info.get("kind") and info.get("kind") not in allowed_kinds:
            errors.append("exception {0} has invalid kind {1}".format(exception_id, info.get("kind")))
        if info.get("classification") and info.get("classification") not in allowed_classes:
            errors.append(
                "exception {0} has invalid classification {1}".format(exception_id, info.get("classification"))
            )
        if info.get("risk") and info.get("risk") not in allowed_risks:
            errors.append("exception {0} has invalid risk {1}".format(exception_id, info.get("risk")))
        if info.get("active", True) is False and fail_expired:
            errors.append("exception {0} is inactive or expired".format(exception_id))
        if fail_missing and repo_root and info.get("kind") != "pattern":
            candidate = os.path.join(repo_root, *(normalize_exception_path(info.get("path")).split("/")))
            if not os.path.exists(candidate):
                errors.append("exception {0} path is missing: {1}".format(exception_id, info.get("path")))
    return errors


def active_exceptions(ledger):
    active = []
    for exception_id, info in sorted(ledger.get("exceptions", {}).items()):
        if not isinstance(info, dict):
            continue
        if info.get("active", True) is False:
            continue
        record = dict(info)
        record["id"] = exception_id
        record["path"] = normalize_exception_path(record.get("path", ""))
        active.append(record)
    return active


def find_exception(path, kind, exceptions):
    normalized = normalize_exception_path(path)
    for exception in exceptions:
        if exception.get("kind") == "pattern":
            if fnmatch.fnmatchcase(normalized, exception.get("path", "")):
                return exception
            continue
        if exception.get("path") == normalized:
            return exception
    return None


def violation(path, code, message):
    return {"path": path, "code": code, "message": message}


def format_violation(record):
    path = record.get("path", "")
    if path:
        return "{0}: {1}: {2}".format(record.get("code", "violation"), path, record.get("message", ""))
    return "{0}: {1}".format(record.get("code", "violation"), record.get("message", ""))


def apply_exceptions_to_violations(violations, exceptions):
    applied = []
    unexcepted = []
    for item in violations:
        path = item.get("path", "")
        exception = find_exception(path, "", exceptions) if path else None
        if exception:
            applied_item = dict(item)
            applied_item["exception_id"] = exception["id"]
            applied_item["exception_retirement_phase"] = exception.get("retirement_phase", "")
            applied_item["exception_target"] = exception.get("target", "")
            applied.append(applied_item)
        else:
            unexcepted.append(item)
    return applied, unexcepted


def head_sha(repo_root):
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL)
    except Exception:
        return None
    return output.decode("utf-8", "replace").strip()


def entry_kind(path):
    if os.path.islink(path):
        return "symlink"
    if os.path.isdir(path):
        return "directory"
    if os.path.isfile(path):
        return "file"
    return "other"


def root_entries(repo_root):
    entries = []
    for name in os.listdir(repo_root):
        if name == ".git":
            continue
        if is_untracked_ignored_root(repo_root, name):
            continue
        entries.append(name)
    entries.sort(key=lambda item: (item.casefold(), item))
    return entries


def is_untracked_ignored_root(repo_root, name):
    """Return true for ignored local roots that have no tracked files beneath them."""
    try:
        ignored = subprocess.call(
            ["git", "check-ignore", "-q", "--", name],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False
    if ignored != 0:
        return False
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files", "--", name],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False
    return not tracked.decode("utf-8", "replace").strip()


def allowed_files(contract):
    section = contract.get("allowed_root_files", {})
    return set(section.get("allowed", [])), list(section.get("patterns", []))


def forbidden_patterns(contract):
    section = contract.get("forbidden_root_patterns", {})
    if isinstance(section, list):
        return section
    if isinstance(section, dict):
        return list(section.get("patterns", []))
    return []


def classify_entry(name, kind, contract):
    canonical = contract.get("canonical_directories", {})
    optional = contract.get("optional_directories", {})
    metadata = contract.get("metadata_directories", {})
    transitional = contract.get("transitional_directories", {})
    allowed, patterns = allowed_files(contract)

    if kind == "directory" and name in canonical:
        return CLASS_CANONICAL, name, "", canonical[name].get("notes", "")
    if kind == "directory" and name in optional:
        return CLASS_OPTIONAL, name, "", optional[name].get("notes", "")
    if kind == "directory" and name in metadata:
        return CLASS_METADATA, name, "", metadata[name].get("notes", "")
    if kind == "file" and (name in allowed or any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)):
        return CLASS_ALLOWED_FILE, name, "", "Allowed root file."
    if kind == "directory" and name in transitional:
        info = transitional[name]
        if info.get("retired", False):
            return CLASS_VIOLATION, info.get("target_or_review", "review"), info.get("retire_by_phase", ""), info.get("notes", "")
        raw_class = info.get("classification", "transitional")
        if raw_class.startswith("generated"):
            classification = CLASS_GENERATED
        else:
            classification = CLASS_TRANSITIONAL
        return classification, info.get("target_or_review", "review"), info.get("retire_by_phase", ""), info.get("notes", "")

    default_class = contract.get("policy", {}).get("default_for_unknown_root", CLASS_VIOLATION)
    if default_class not in (CLASS_VIOLATION, CLASS_UNKNOWN):
        default_class = CLASS_VIOLATION
    return default_class, "review", "", "No root allowlist entry matched."


def collect_entries(repo_root, contract, exceptions=None):
    entries = []
    exceptions = exceptions or []
    for name in root_entries(repo_root):
        path = os.path.join(repo_root, name)
        kind = entry_kind(path)
        classification, target, retire_by_phase, notes = classify_entry(name, kind, contract)
        entry = {
            "name": name,
            "kind": kind,
            "classification": classification,
            "target_or_review": target,
            "retire_by_phase": retire_by_phase,
            "notes": notes,
        }
        exception = find_exception(name, kind, exceptions)
        if exception:
            entry["exception_id"] = exception["id"]
            entry["exception_retirement_phase"] = exception.get("retirement_phase", "")
            entry["exception_target"] = exception.get("target", "")
            entry["exception_reason"] = exception.get("reason", "")
        entries.append(entry)
    return entries


def phase_number(phase):
    prefix = "CONVERGE-"
    if not phase or not phase.startswith(prefix):
        return None
    digits = []
    for char in phase[len(prefix) :]:
        if char.isdigit():
            digits.append(char)
        else:
            break
    if not digits:
        return None
    return int("".join(digits))


def missing_expected(contract, repo_root):
    missing = []
    for name, info in sorted(contract.get("canonical_directories", {}).items()):
        if info.get("required", False) and not os.path.exists(os.path.join(repo_root, name)):
            missing.append(name)
    return missing


def summarize(entries):
    counts = {}
    for entry in entries:
        key = entry["classification"]
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def transitional_by_phase(entries):
    grouped = {}
    for entry in entries:
        if entry["classification"] != CLASS_TRANSITIONAL:
            continue
        phase = entry.get("retire_by_phase") or "review"
        grouped.setdefault(phase, []).append(entry["name"])
    return dict((phase, sorted(names, key=lambda item: (item.casefold(), item))) for phase, names in sorted(grouped.items()))


def strict_violation_records(contract, entries, contract_errors, exception_errors):
    policy = contract.get("policy", {})
    violations = []
    if contract_errors:
        for error in contract_errors:
            violations.append(violation("", "malformed_contract", error))
    if exception_errors:
        for error in exception_errors:
            violations.append(violation("", "malformed_exception_ledger", error))
    if policy.get("strict_fails_unknown_root", True):
        for entry in entries:
            if entry["classification"] in (CLASS_UNKNOWN, CLASS_VIOLATION):
                violations.append(
                    violation(entry["name"], "unknown_or_violating_root_entry", "unknown or violating root entry")
                )
    if policy.get("strict_fails_forbidden_root", True):
        for entry in entries:
            if entry["classification"] == "forbidden":
                violations.append(violation(entry["name"], "forbidden_root_entry", "forbidden root entry"))
    for entry in entries:
        if entry["classification"] == CLASS_TRANSITIONAL:
            violations.append(violation(entry["name"], "transitional_root_requires_exception", "transitional root present"))
        elif entry["classification"] == CLASS_GENERATED:
            violations.append(violation(entry["name"], "generated_root_requires_exception", "generated root present"))
    return violations


def build_report(repo_root, contract, entries, contract_errors, strict, exception_ledger, exception_errors):
    exceptions = active_exceptions(exception_ledger)
    violations = strict_violation_records(contract, entries, contract_errors, exception_errors)
    exceptions_applied, unexcepted = apply_exceptions_to_violations(violations, exceptions)
    generated = [entry["name"] for entry in entries if entry["classification"] == CLASS_GENERATED]
    unknown = [entry["name"] for entry in entries if entry["classification"] in (CLASS_UNKNOWN, CLASS_VIOLATION)]
    return {
        "contract_id": contract.get("contract", {}).get("id", ""),
        "phase": contract.get("contract", {}).get("phase", ""),
        "exception_contract_id": exception_ledger.get("contract", {}).get("id", ""),
        "active_exception_count": len(exceptions),
        "repo_root": posix_path(os.path.abspath(repo_root)),
        "head_sha": head_sha(repo_root),
        "strict": bool(strict),
        "summary": summarize(entries),
        "unknown_roots": unknown,
        "transitional_by_phase": transitional_by_phase(entries),
        "generated_or_ephemeral_roots": generated,
        "missing_expected_canonical_roots": missing_expected(contract, repo_root),
        "forbidden_root_patterns": forbidden_patterns(contract),
        "contract_errors": contract_errors,
        "exception_errors": exception_errors,
        "violations": violations,
        "exceptions_applied": exceptions_applied,
        "unexcepted_violations": unexcepted,
        "strict_violations": [format_violation(item) for item in unexcepted],
        "strict_result": "fail" if strict and unexcepted else ("pass" if strict else "not_run"),
        "result": "fail" if strict and unexcepted else ("pass" if strict else "not_run"),
        "entries": entries,
    }


def print_text_report(report):
    print("Root allowlist audit")
    print("contract_id: {0}".format(report["contract_id"]))
    print("phase: {0}".format(report["phase"]))
    print("exception_contract_id: {0}".format(report.get("exception_contract_id", "")))
    print("active_exception_count: {0}".format(report.get("active_exception_count", 0)))
    print("head_sha: {0}".format(report["head_sha"]))
    print("")
    print("Summary counts:")
    for key, value in report["summary"].items():
        print("- {0}: {1}".format(key, value))
    print("")
    print("Unknown roots:")
    if report["unknown_roots"]:
        for name in report["unknown_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Transitional roots by retire phase:")
    if report["transitional_by_phase"]:
        for phase, names in report["transitional_by_phase"].items():
            print("- {0}: {1}".format(phase, ", ".join(names)))
    else:
        print("- none")
    print("")
    print("Generated/ephemeral roots:")
    if report["generated_or_ephemeral_roots"]:
        for name in report["generated_or_ephemeral_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Missing expected canonical roots:")
    if report["missing_expected_canonical_roots"]:
        for name in report["missing_expected_canonical_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Forbidden root patterns:")
    for pattern in report["forbidden_root_patterns"]:
        print("- {0}".format(pattern))
    print("")
    if report["contract_errors"]:
        print("Contract errors:")
        for error in report["contract_errors"]:
            print("- {0}".format(error))
        print("")
    if report.get("exception_errors"):
        print("Exception ledger errors:")
        for error in report["exception_errors"]:
            print("- {0}".format(error))
        print("")
    print("Exceptions applied:")
    if report.get("exceptions_applied"):
        for item in report["exceptions_applied"]:
            print("- {0}: {1}".format(item.get("exception_id", ""), format_violation(item)))
    else:
        print("- none")
    print("")
    print("Unexcepted violations:")
    if report.get("unexcepted_violations"):
        for item in report["unexcepted_violations"]:
            print("- {0}".format(format_violation(item)))
    else:
        print("- none")
    print("")
    if report["strict_result"] == "not_run":
        print("Strict-mode result: not run")
        if report.get("unexcepted_violations"):
            print("Potential strict violations:")
            for item in report["unexcepted_violations"]:
                print("- {0}".format(format_violation(item)))
    else:
        print("Strict-mode result: {0}".format(report["strict_result"]))
        if report["strict_violations"]:
            print("Strict violations:")
            for violation in report["strict_violations"]:
                print("- {0}".format(violation))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Audit root-level entries against root_allowlist.toml.")
    parser.add_argument("--repo-root", default=".", help="Repository root to audit.")
    parser.add_argument("--contract", default="contracts/repo/root_allowlist.toml", help="Root allowlist contract path.")
    parser.add_argument(
        "--exceptions",
        default="contracts/repo/layout_exceptions.toml",
        help="Layout exception ledger path.",
    )
    parser.add_argument("--strict", action="store_true", help="Fail on strict allowlist violations.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    parser.add_argument("--no-write", action="store_true", help="Accepted for parity; this validator is read-only by default.")
    parser.add_argument("--include-dotfiles", action="store_true", help="Accepted for parity; metadata dot directories are included by default.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract
    if not os.path.isabs(contract_path):
        contract_path = os.path.join(repo_root, contract_path)
    exceptions_path = args.exceptions
    if not os.path.isabs(exceptions_path):
        exceptions_path = os.path.join(repo_root, exceptions_path)

    try:
        contract = load_contract(contract_path)
    except Exception as exc:
        print("ERROR: failed to load allowlist contract {0}: {1}".format(contract_path, exc), file=sys.stderr)
        return 2

    contract_errors = validate_contract_shape(contract)
    exception_ledger, exception_errors = load_exception_ledger(exceptions_path)
    if exception_errors and not args.strict:
        print("WARN: exception ledger issues detected; continuing audit mode.", file=sys.stderr)
    entries = collect_entries(repo_root, contract, active_exceptions(exception_ledger))
    report = build_report(repo_root, contract, entries, contract_errors, args.strict, exception_ledger, exception_errors)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)

    if args.strict and report["unexcepted_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
