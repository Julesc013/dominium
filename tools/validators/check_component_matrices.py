#!/usr/bin/env python3
"""Audit the Dominium release component matrix contract."""

from __future__ import print_function

import argparse
import ast
import json
import os
import subprocess
import sys


REQUIRED_SECTIONS = [
    "support_tiers",
    "products",
    "product_modes",
    "platform_backends",
    "render_backends",
    "native_shells",
    "toolchains",
    "packaging",
    "audio_backends",
    "input_backends",
    "network_backends",
    "storage_backends",
    "distribution_projections",
]

MATRIX_SECTIONS = [
    "products",
    "product_modes",
    "platform_backends",
    "render_backends",
    "native_shells",
    "toolchains",
    "packaging",
    "audio_backends",
    "input_backends",
    "network_backends",
    "storage_backends",
    "distribution_projections",
]

REQUIRED_DOCS = [
    "docs/release/COMPONENT_MATRIX.md",
    "docs/release/PRODUCT_MODE_MATRIX.md",
    "docs/release/PLATFORM_MATRIX.md",
    "docs/release/RENDER_BACKEND_MATRIX.md",
    "docs/release/NATIVE_APP_MATRIX.md",
    "docs/release/TOOLCHAIN_MATRIX.md",
    "docs/release/PACKAGING_MATRIX.md",
    "docs/release/AUDIO_BACKEND_MATRIX.md",
    "docs/release/INPUT_BACKEND_MATRIX.md",
    "docs/release/NETWORK_BACKEND_MATRIX.md",
    "docs/release/STORAGE_BACKEND_MATRIX.md",
    "docs/release/SUPPORT_TIERS.md",
]

NO_SUPPORT_STATUSES = set(["stub", "planned", "research", "unknown", "unsupported", "blocked"])


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


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return ast.literal_eval(value)
    return value


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
            key, value = line.split("=", 1)
            current[strip_quotes(key.strip())] = parse_value(value)
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


def validate_contract_shape(contract):
    errors = []
    for key in ["contract", "policy"]:
        if key not in contract:
            errors.append("missing top-level key: {0}".format(key))
    meta = contract.get("contract", {})
    for key in ["id", "status", "phase"]:
        if key not in meta:
            errors.append("missing contract.{0}".format(key))
    if meta.get("id") not in ("", "dominium.release.component_matrix.v1"):
        errors.append("unexpected contract.id: {0}".format(meta.get("id")))
    policy = contract.get("policy", {})
    if not isinstance(policy.get("statuses", []), list) or not policy.get("statuses"):
        errors.append("policy.statuses must be a non-empty array")
    if not isinstance(policy.get("support_tiers", []), list) or not policy.get("support_tiers"):
        errors.append("policy.support_tiers must be a non-empty array")
    return errors


def collect_matrix_issues(contract):
    statuses = set(contract.get("policy", {}).get("statuses", []))
    tiers = set(contract.get("policy", {}).get("support_tiers", []))
    missing_sections = [name for name in REQUIRED_SECTIONS if name not in contract]
    missing_statuses = []
    invalid_statuses = []
    invalid_tiers = []
    missing_evidence = []
    no_support_mislabels = []
    counts = {}

    for section_name in MATRIX_SECTIONS:
        section = contract.get(section_name, {})
        if not isinstance(section, dict):
            missing_sections.append(section_name)
            continue
        counts[section_name] = len(section)
        for item_name in sorted(section):
            item = section.get(item_name, {})
            if not isinstance(item, dict):
                missing_statuses.append("{0}.{1}".format(section_name, item_name))
                continue
            status = item.get("status")
            if not status:
                missing_statuses.append("{0}.{1}".format(section_name, item_name))
            elif status not in statuses:
                invalid_statuses.append("{0}.{1}: {2}".format(section_name, item_name, status))
            tier = item.get("tier")
            if tier and tier not in tiers:
                invalid_tiers.append("{0}.{1}: {2}".format(section_name, item_name, tier))
            if status in ("available", "implemented") and not item.get("evidence"):
                missing_evidence.append("{0}.{1}".format(section_name, item_name))
            if status in NO_SUPPORT_STATUSES and str(item.get("support", "")).lower() in ("true", "supported"):
                no_support_mislabels.append("{0}.{1}".format(section_name, item_name))

    support_tier_rows = contract.get("support_tiers", {})
    for tier in tiers:
        if tier not in support_tier_rows:
            invalid_tiers.append("policy.support_tiers missing definition: {0}".format(tier))

    return {
        "counts": counts,
        "missing_sections": sorted(set(missing_sections)),
        "missing_statuses": missing_statuses,
        "invalid_statuses": invalid_statuses,
        "invalid_tiers": invalid_tiers,
        "missing_evidence": missing_evidence,
        "no_support_mislabels": no_support_mislabels,
    }


def docs_present(repo_root):
    result = {}
    for rel_path in REQUIRED_DOCS:
        result[rel_path] = os.path.exists(os.path.join(repo_root, rel_path))
    return result


def doc_claim_warnings(repo_root):
    warnings = []
    banned_phrases = [
        "stub is support",
        "stubs are support",
        "planned is support",
        "planned lanes are supported",
        "research is support",
        "research lanes are supported",
        "stub equals support",
        "planned equals support",
        "research equals support",
    ]
    for rel_path in REQUIRED_DOCS:
        path = os.path.join(repo_root, rel_path)
        if not os.path.exists(path):
            continue
        text = open(path, "r", encoding="utf-8").read().lower()
        for phrase in banned_phrases:
            if phrase in text:
                warnings.append("{0}: forbidden support wording: {1}".format(rel_path, phrase))
        if "machine-readable source" not in text and rel_path.endswith("COMPONENT_MATRIX.md"):
            warnings.append("{0}: missing machine-readable source wording".format(rel_path))
    return warnings


def build_report(repo_root, contract, contract_errors, strict):
    issues = collect_matrix_issues(contract)
    present = docs_present(repo_root)
    missing_docs = [path for path, exists in present.items() if not exists]
    warnings = doc_claim_warnings(repo_root)
    strict_violations = []
    strict_violations.extend(contract_errors)
    strict_violations.extend("missing required matrix section: {0}".format(name) for name in issues["missing_sections"])
    strict_violations.extend("matrix entry missing status: {0}".format(name) for name in issues["missing_statuses"])
    strict_violations.extend("invalid status: {0}".format(name) for name in issues["invalid_statuses"])
    strict_violations.extend("invalid support tier: {0}".format(name) for name in issues["invalid_tiers"])
    strict_violations.extend("available/implemented entry missing evidence: {0}".format(name) for name in issues["missing_evidence"])
    strict_violations.extend("non-support status mislabeled as supported: {0}".format(name) for name in issues["no_support_mislabels"])
    strict_violations.extend("missing required matrix doc: {0}".format(path) for path in missing_docs)
    strict_violations.extend("doc support claim violation: {0}".format(item) for item in warnings)
    return {
        "contract_id": contract.get("contract", {}).get("id", ""),
        "phase": contract.get("contract", {}).get("phase", ""),
        "repo_root": posix_path(os.path.abspath(repo_root)),
        "head_sha": head_sha(repo_root),
        "summary": {
            "matrix_sections": len(MATRIX_SECTIONS),
            "support_tiers": len(contract.get("support_tiers", {})),
            "matrix_counts": issues["counts"],
            "warnings": len(warnings),
        },
        "missing_sections": issues["missing_sections"],
        "missing_statuses": issues["missing_statuses"],
        "invalid_statuses": issues["invalid_statuses"],
        "invalid_tiers": issues["invalid_tiers"],
        "missing_evidence": issues["missing_evidence"],
        "docs_present": present,
        "warnings": warnings,
        "strict_violations": strict_violations,
        "result": "fail" if strict and strict_violations else ("pass" if strict else "not_run"),
    }


def print_text(report, strict):
    print("Component matrix audit")
    print("contract_id: {0}".format(report["contract_id"]))
    print("phase: {0}".format(report["phase"]))
    print("head_sha: {0}".format(report.get("head_sha") or "unknown"))
    print("")
    print("Summary:")
    print("- matrix_sections: {0}".format(report["summary"]["matrix_sections"]))
    print("- support_tiers: {0}".format(report["summary"]["support_tiers"]))
    print("- warnings: {0}".format(report["summary"]["warnings"]))
    print("")
    print("Matrix counts:")
    for section_name in sorted(report["summary"]["matrix_counts"]):
        print("- {0}: {1}".format(section_name, report["summary"]["matrix_counts"][section_name]))
    print("")
    for title, key in [
        ("Missing sections", "missing_sections"),
        ("Missing statuses", "missing_statuses"),
        ("Invalid statuses", "invalid_statuses"),
        ("Invalid tiers", "invalid_tiers"),
        ("Missing evidence", "missing_evidence"),
        ("Warnings", "warnings"),
    ]:
        print("{0}:".format(title))
        values = report.get(key, [])
        if values:
            for value in values:
                print("- {0}".format(value))
        else:
            print("- none")
        print("")
    print("Strict-mode result: {0}".format(report["result"] if strict else "not run"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--contract", default="contracts/release/component_matrix.contract.toml")
    parser.add_argument("--strict", action="store_true", help="Fail on unhandled matrix violations")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--no-write", action="store_true", help="Accepted for validator CLI parity; this validator writes no reports")
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract
    if not os.path.isabs(contract_path):
        contract_path = os.path.join(repo_root, contract_path)

    contract_errors = []
    contract = {}
    if not os.path.exists(contract_path):
        contract_errors.append("missing contract: {0}".format(posix_path(os.path.relpath(contract_path, repo_root))))
    else:
        try:
            contract = load_contract(contract_path)
        except Exception as exc:
            contract_errors.append("malformed contract: {0}".format(exc))
    if contract:
        contract_errors.extend(validate_contract_shape(contract))

    report = build_report(repo_root, contract, contract_errors, args.strict)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report, args.strict)

    if args.strict and report["strict_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
