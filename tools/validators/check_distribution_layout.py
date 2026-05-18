#!/usr/bin/env python3
"""Audit the Dominium distribution layout projection contract."""

from __future__ import print_function

import argparse
import ast
import json
import os
import re
import subprocess
import sys


REQUIRED_LOGICAL_ROOTS = [
    "INSTALL_ROOT",
    "BIN_ROOT",
    "DESCRIPTOR_ROOT",
    "STORE_ROOT",
    "PACK_ROOT",
    "PROFILE_ROOT",
    "INSTANCE_ROOT",
    "SAVE_ROOT",
    "EXPORT_ROOT",
    "LOG_ROOT",
    "RUNTIME_ROOT",
    "CACHE_ROOT",
    "OPS_ROOT",
    "DOC_ROOT",
    "REDIST_ROOT",
    "SYMBOL_ROOT",
    "MEDIA_ROOT",
    "STORE_LOCK_ROOT",
    "RUNTIME_LOCK_ROOT",
    "OPS_TRANSACTION_ROOT",
]

REQUIRED_PROJECTIONS = [
    "source_repo",
    "dist_output",
    "compressed_archive",
    "portable_install",
    "installed_desktop",
    "server_install",
    "media_layout",
    "package_export",
    "bundle_export",
    "cache_and_staging",
    "symbols_and_provenance",
]

OPTIONAL_INPUT_DOCS = [
    "docs/runtime/shell/VIRTUAL_PATHS.md",
    "docs/architecture/INSTALL_MODEL.md",
    "docs/architecture/CONTENT_AND_STORAGE_MODEL.md",
    "docs/distribution/DIST_TREE_CONTRACT.md",
    "docs/architecture/BUNDLE_MODEL.md",
    "docs/architecture/SAVE_MODEL.md",
    "docs/architecture/INSTANCE_MODEL.md",
    "docs/architecture/SETUP_TRANSACTION_MODEL.md",
    "docs/architecture/OPS_TRANSACTION_MODEL.md",
    "docs/architecture/UPDATE_MODEL.md",
    "docs/architecture/LOCKFILES.md",
    "docs/architecture/LOCKLIST.md",
    "docs/release/DISTRIBUTION_MODEL.md",
    "docs/release/DIST_BUNDLE_ASSEMBLY.md",
    "docs/release/DIST_VERIFICATION_RULES.md",
    "docs/release/RELEASE_MANIFEST_MODEL.md",
    "docs/release/ARTIFACT_NAMING_RULES.md",
    "docs/release/SIGNING_POLICY.md",
]

CONVERGE_REPO_DOCS = [
    "docs/repo/REPO_LAYOUT_TARGET.md",
    "docs/repo/ROOT_FILE_POLICY.md",
    "docs/repo/MOVE_MAP.md",
    "docs/repo/DISTRIBUTION_LAYOUT_CANON.md",
]


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
    return value


def set_section(root, section_name):
    current = root
    for part in section_name.split("."):
        part = part.strip().strip('"')
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
            key, value = line.split("=", 1)
            current[key.strip().strip('"')] = parse_value(value)
    return data


def load_contract(path):
    try:
        import tomllib  # type: ignore
    except ImportError:
        print(
            "WARN: tomllib is unavailable; using minimal fallback TOML parser for this contract shape.",
            file=sys.stderr,
        )
        return load_toml_fallback(path)
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def head_sha(repo_root):
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL)
    except Exception:
        return None
    return output.decode("utf-8", "replace").strip()


def posix_path(path):
    return path.replace(os.sep, "/")


def looks_like_absolute_host_path(value):
    if not isinstance(value, str):
        return False
    if value.startswith("/") or value.startswith("\\") or value.startswith("~"):
        return True
    return bool(re.match(r"^[A-Za-z]:[\\/]", value))


def validate_contract_shape(contract):
    errors = []
    for key in ["contract", "policy", "logical_roots", "projections"]:
        if key not in contract:
            errors.append("missing top-level key: {0}".format(key))
    meta = contract.get("contract", {})
    for key in ["id", "status", "enforcement", "phase"]:
        if key not in meta:
            errors.append("missing contract.{0}".format(key))
    if meta.get("id") not in ("", "dominium.distribution.layout.v1"):
        errors.append("unexpected contract.id: {0}".format(meta.get("id")))
    if not isinstance(contract.get("logical_roots", {}), dict):
        errors.append("logical_roots must be an object")
    if not isinstance(contract.get("projections", {}), dict):
        errors.append("projections must be an object")
    return errors


def missing_logical_roots(contract):
    roots = contract.get("logical_roots", {})
    return [name for name in REQUIRED_LOGICAL_ROOTS if name not in roots]


def missing_projections(contract):
    projections = contract.get("projections", {})
    return [name for name in REQUIRED_PROJECTIONS if name not in projections]


def policy_violations(contract):
    policy = contract.get("policy", {})
    violations = []
    required_true = [
        "source_repo_layout_is_not_runtime_layout",
        "dist_is_generated_output",
        "package_exports_use_logical_roots",
        "absolute_host_paths_for_packages_forbidden",
        "validators_audit_only_by_default",
    ]
    for key in required_true:
        if policy.get(key) is not True:
            violations.append("policy.{0} must be true".format(key))
    package_export = contract.get("projections", {}).get("package_export", {})
    if package_export.get("absolute_host_paths_allowed") is not False:
        violations.append("projections.package_export.absolute_host_paths_allowed must be false")
    for root in package_export.get("allowed_export_roots", []):
        if looks_like_absolute_host_path(root):
            violations.append("package export root must be logical, not host-absolute: {0}".format(root))
    return violations


def doc_warnings(repo_root):
    warnings = []
    for rel_path in OPTIONAL_INPUT_DOCS:
        if not os.path.exists(os.path.join(repo_root, rel_path)):
            warnings.append("optional input doc missing: {0}".format(rel_path))
    source_contract = os.path.join(repo_root, "contracts", "repo", "layout.contract.toml")
    if not os.path.exists(source_contract):
        warnings.append("source repo layout contract missing: contracts/repo/layout.contract.toml")
    for rel_path in CONVERGE_REPO_DOCS:
        path = os.path.join(repo_root, rel_path)
        if not os.path.exists(path):
            warnings.append("CONVERGE repo doc missing for distribution note: {0}".format(rel_path))
            continue
        text = open(path, "r", encoding="utf-8").read().lower()
        if "archive/generated/dist/" in text and "generated" not in text:
            warnings.append("repo doc mentions archive/generated/dist/ without generated-output wording: {0}".format(rel_path))
    return warnings


def build_report(repo_root, contract, contract_errors, strict):
    missing_roots = missing_logical_roots(contract)
    missing = missing_projections(contract)
    policy_errors = policy_violations(contract)
    warnings = doc_warnings(repo_root)
    strict_violations = []
    strict_violations.extend(contract_errors)
    strict_violations.extend("missing required logical root: {0}".format(name) for name in missing_roots)
    strict_violations.extend("missing required projection: {0}".format(name) for name in missing)
    strict_violations.extend(policy_errors)
    result = "fail" if strict and strict_violations else ("pass" if strict else "not_run")
    audit_result = "pass" if not contract_errors else "warn"
    return {
        "contract_id": contract.get("contract", {}).get("id", ""),
        "phase": contract.get("contract", {}).get("phase", ""),
        "repo_root": posix_path(os.path.abspath(repo_root)),
        "head_sha": head_sha(repo_root),
        "summary": {
            "logical_roots_declared": len(contract.get("logical_roots", {})),
            "required_logical_roots": len(REQUIRED_LOGICAL_ROOTS),
            "projections_declared": len(contract.get("projections", {})),
            "required_projections": len(REQUIRED_PROJECTIONS),
            "warnings": len(warnings),
        },
        "missing_logical_roots": missing_roots,
        "missing_projections": missing,
        "warnings": warnings,
        "contract_errors": contract_errors,
        "policy_violations": policy_errors,
        "strict": bool(strict),
        "strict_violations": strict_violations,
        "strict_result": result,
        "result": "fail" if strict and strict_violations else audit_result,
    }


def print_text_report(report):
    print("Distribution layout audit")
    print("contract_id: {0}".format(report["contract_id"]))
    print("phase: {0}".format(report["phase"]))
    print("head_sha: {0}".format(report["head_sha"]))
    print("")
    print("Summary:")
    for key, value in sorted(report["summary"].items()):
        print("- {0}: {1}".format(key, value))
    print("")
    print("Missing logical roots:")
    if report["missing_logical_roots"]:
        for name in report["missing_logical_roots"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Missing projections:")
    if report["missing_projections"]:
        for name in report["missing_projections"]:
            print("- {0}".format(name))
    else:
        print("- none")
    print("")
    print("Warnings:")
    if report["warnings"]:
        for warning in report["warnings"]:
            print("- {0}".format(warning))
    else:
        print("- none")
    print("")
    if report["contract_errors"]:
        print("Contract errors:")
        for error in report["contract_errors"]:
            print("- {0}".format(error))
        print("")
    if report["policy_violations"]:
        print("Policy violations:")
        for violation in report["policy_violations"]:
            print("- {0}".format(violation))
        print("")
    if report["strict_result"] == "not_run":
        print("Strict-mode result: not run")
        return
    print("Strict-mode result: {0}".format(report["strict_result"]))
    if report["strict_violations"]:
        print("Strict violations:")
        for violation in report["strict_violations"]:
            print("- {0}".format(violation))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Audit distribution layout contract shape and projection declarations.")
    parser.add_argument("--repo-root", default=".", help="Repository root to audit.")
    parser.add_argument("--contract", default="contracts/distribution/layout.contract.toml", help="Distribution layout contract path.")
    parser.add_argument("--strict", action="store_true", help="Fail on strict distribution contract violations.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    parser.add_argument("--no-write", action="store_true", help="Accepted for parity; this validator is read-only.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract
    if not os.path.isabs(contract_path):
        contract_path = os.path.join(repo_root, contract_path)
    if not os.path.exists(contract_path):
        print("ERROR: missing distribution layout contract: {0}".format(contract_path), file=sys.stderr)
        return 2
    try:
        contract = load_contract(contract_path)
    except Exception as exc:
        print("ERROR: failed to load distribution layout contract {0}: {1}".format(contract_path, exc), file=sys.stderr)
        return 2
    contract_errors = validate_contract_shape(contract)
    report = build_report(repo_root, contract, contract_errors, args.strict)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    if args.strict and report["strict_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
