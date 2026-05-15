#!/usr/bin/env python3
"""Classify Dominium tooling surfaces for AIDE recycling without execution."""

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path


DISCOVERY_ROOTS = [
    ".aide/scripts",
    ".aide/tools",
    ".aide/policies",
    ".aide/validators",
    "tools/aide",
    "tools/xstack",
    "tools/auditx",
    "tools/repox",
    "tools/testx",
    "tools/build",
    "tools/validators",
    "tools/migration",
    "tools/ui_bind",
    "tools/ui_index",
    "tools/appshell",
    "scripts/dev",
    "scripts/ci",
    "scripts",
    ".github/workflows",
    "cmake",
]

SKIP_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".dll", ".exe", ".lib", ".obj", ".pdb", ".ilk"}
TEXT_SAMPLE_BYTES = 4096

SAFE_OBSERVED_HINTS = {
    ".aide/scripts/aide_lite.py": [
        "py -3 .aide/scripts/aide_lite.py doctor",
        "py -3 .aide/scripts/aide_lite.py validate",
        "py -3 .aide/scripts/aide_lite.py tools validate",
        "py -3 .aide/scripts/aide_lite.py roots validate",
        "py -3 .aide/scripts/aide_lite.py repo validate",
    ],
    "tools/build/validate_build_contract.py": [
        "python tools/build/validate_build_contract.py --repo-root . --strict"
    ],
    "tools/validators/check_distribution_layout.py": [
        "python tools/validators/check_distribution_layout.py --repo-root . --strict"
    ],
    "tools/validators/check_component_matrices.py": [
        "python tools/validators/check_component_matrices.py --repo-root . --strict"
    ],
}


def relpath(path, repo_root):
    return str(path.relative_to(repo_root)).replace("\\", "/")


def should_skip(path):
    if any(part in SKIP_DIR_NAMES for part in path.parts):
        return True
    return path.is_file() and path.suffix.lower() in SKIP_EXTENSIONS


def is_candidate_file(path):
    if path.is_dir():
        return False
    if should_skip(path):
        return False
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in {".py", ".ps1", ".cmd", ".bat", ".sh", ".cmake", ".yaml", ".yml", ".toml", ".json", ".md"}:
        return True
    if name in {"cmakelists.txt", "makefile"}:
        return True
    if suffix == "":
        return True
    return False


def read_sample(path):
    try:
        data = path.read_bytes()[:TEXT_SAMPLE_BYTES]
    except OSError:
        return ""
    return data.decode("utf-8", errors="ignore")


def shebang(sample):
    first = sample.splitlines()[0] if sample else ""
    return first if first.startswith("#!") else ""


def executable_bit(path):
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def contains_any(text, terms):
    lower = text.lower()
    return any(term in lower for term in terms)


def infer_family(path):
    lower = path.lower()
    name = Path(path).name.lower()
    parts = set(lower.split("/"))
    if lower in {".aide/scripts", ".aide/tools", ".aide/policies", ".aide/validators", "tools/aide"}:
        return "aide"
    if lower.startswith(".aide/") or lower.startswith("tools/aide/"):
        return "aide"
    if lower == "cmake" or lower.startswith("cmake/"):
        return "build"
    if "xstack" in parts or "xstack" in lower:
        return "xstack"
    if "auditx" in parts or "auditx" in lower or "audit" in name:
        return "audit"
    if "repox" in lower or "repo_policy" in lower or name.startswith("check_repo") or name.startswith("check_root"):
        return "repo_policy"
    if "testx" in lower or name.startswith("test") or "_test" in name:
        return "test"
    if name.startswith("validate_build") or "build" in parts:
        return "build"
    if "validators" in parts or name.startswith("check_") or name.startswith("verify_") or "validate" in name:
        return "validator"
    if "package" in lower or "pack" in name or "dist" in lower:
        return "package"
    if "release" in lower:
        return "release"
    if "security" in lower or "safety" in lower or "secret" in lower:
        return "security"
    if "compat" in lower:
        return "compatibility"
    if "migration" in parts or "migrate" in name:
        return "migration"
    if "ui_bind" in lower:
        return "ui_bind"
    if "ui_index" in lower:
        return "ui_index"
    if "appshell" in lower:
        return "appshell"
    if lower.startswith(".github/workflows") or lower.startswith("scripts/ci"):
        return "ci"
    if lower.startswith("scripts/"):
        return "ci" if "ci" in parts else "unknown"
    return "unknown"


def stable_owner_for(family, path):
    if family == "aide":
        return "tools/aide" if path.startswith("tools/aide/") else "tools/aide"
    if family == "audit":
        return "tools/audit"
    if family == "repo_policy":
        return "tools/repo"
    if family == "test":
        return "tools/test"
    if family == "build":
        return "cmake" if path.startswith("cmake/") else "tools/build"
    if family == "package":
        return "tools/package"
    if family in {"ui_bind", "ui_index", "appshell"}:
        return "tools/ui"
    if family == "migration":
        return "tools/migration"
    if family == "validator":
        return "tools/validators"
    if family == "ci":
        return ".github" if path.startswith(".github/") else "scripts"
    if family in {"release", "security", "compatibility"}:
        return "preserve_unknown"
    if family == "xstack":
        return "tools/aide"
    return "preserve_unknown"


def task_type_for(family):
    mapping = {
        "aide": "validate",
        "xstack": "validate",
        "audit": "audit",
        "repo_policy": "repo_policy",
        "test": "test",
        "build": "build",
        "package": "package",
        "ui_bind": "validate",
        "ui_index": "validate",
        "appshell": "validate",
        "migration": "migration",
        "validator": "validate",
        "ci": "ci",
        "release": "release",
        "security": "security",
        "compatibility": "compatibility",
    }
    return mapping.get(family, "unknown")


def infer_risks(path, family, sample):
    lower = (path + "\n" + sample).lower()
    writes = contains_any(lower, [
        "write_text", "write_bytes", "open(", "--out", "outfile", "mkdir", "remove", "unlink",
        "rmtree", "move", "rename", "generate", "cache", "dist", "package", "release"
    ])
    network = contains_any(lower, ["requests", "urllib", "http://", "https://", "gh ", "github", "upload", "download"])
    build = contains_any(lower, ["cmake", "build", "ctest", "msbuild", "ninja", "compile"])
    package = contains_any(lower, ["package", "pack", "dist", "bundle", "release"])
    mutates = contains_any(lower, ["git commit", "git push", "git tag", "delete", "remove", "unlink", "rmtree", "rename", "move"])
    if family in {"build"}:
        build = True
    if family in {"package", "release"}:
        package = True
    if family == "ci":
        network = network or path.startswith(".github/")
    return writes, network, build, package, mutates


def infer_fate(family, path, risk):
    if family == "unknown":
        return "preserve_unknown"
    if family == "aide":
        return "keep"
    if family in {"xstack", "audit", "repo_policy", "test"}:
        return "adapt"
    if family in {"release", "security", "compatibility"}:
        return "extract" if risk in {"high", "protected"} else "adapt"
    if family in {"build", "package", "migration", "ui_bind", "ui_index", "appshell"}:
        return "adapt"
    if family == "ci":
        return "convert" if path.endswith((".yml", ".yaml")) else "adapt"
    if family == "validator":
        return "keep"
    return "preserve_unknown"


def infer_risk(family, writes, network, build, package, mutates):
    if family == "unknown":
        return "unknown"
    if family in {"release", "security", "compatibility"}:
        return "protected"
    if mutates or network:
        return "high"
    if package or build or family in {"xstack", "audit", "repo_policy", "test", "migration", "ci"}:
        return "medium"
    if writes:
        return "medium"
    return "low"


def infer_execution_safety(path, family, risk, writes, network, build, package, mutates):
    if path in SAFE_OBSERVED_HINTS:
        return "safe_observed"
    if family == "unknown":
        return "disabled_unknown"
    if mutates or network or package or risk == "protected":
        return "dangerous_or_mutating"
    if build:
        return "blocked"
    if writes:
        return "plan_only"
    return "plan_only"


def wrapper_candidate_for(path, family, risk, execution_safety, writes, network, package, mutates):
    if path == ".aide/scripts/aide_lite.py":
        return True, 1
    if path in {
        "tools/build/validate_build_contract.py",
        "tools/validators/check_distribution_layout.py",
        "tools/validators/check_component_matrices.py",
    }:
        return True, 2
    if path in {
        "tools/validators/check_repo_layout.py",
        "tools/validators/check_root_allowlist.py",
    }:
        return True, 3
    if family == "validator" and risk in {"low", "medium"} and not network and not package and not mutates:
        return True, 4
    if family == "aide" and execution_safety in {"safe_observed", "plan_only"}:
        return True, 4
    return False, 0


def command_surface_for(path, sample):
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".ps1":
        return "powershell"
    if suffix in {".cmd", ".bat"}:
        return "cmd"
    if suffix == ".sh":
        return "shell"
    if suffix in {".yml", ".yaml"} and path.startswith(".github/workflows/"):
        return "github_actions"
    if suffix == ".cmake" or Path(path).name.lower() == "cmakelists.txt":
        return "cmake"
    if shebang(sample):
        return "shebang"
    return "configuration_or_document"


def evidence_refs_for(path, family, wrapper_candidate):
    refs = [
        ".aide/tools/latest-tool-inventory.json",
        ".aide/reports/DOM-AIDE-02-wrapper-selection.md",
        ".aide/reports/AIDE-STRUCTURE-00-status.md",
    ]
    if family in {"xstack", "audit", "repo_policy", "test"}:
        refs.append("docs/aide/XSTACK_RECYCLING_PLAN.md")
    if wrapper_candidate:
        refs.append(".aide/reports/AIDE-STRUCTURE-01-wrapper-candidates.md")
    return refs


def known_io(family, path, writes, network, build, package):
    inputs = ["repo root"]
    outputs = []
    if path.endswith((".toml", ".json", ".yaml", ".yml", ".md")):
        inputs.append("configuration/document")
    if writes:
        outputs.append("inferred file output or cache")
    if path.startswith(".aide/"):
        outputs.append(".aide/** evidence")
    if build:
        outputs.append("build/test output risk")
    if package:
        outputs.append("package/release output risk")
    if network:
        outputs.append("external/GitHub/network risk")
    return inputs, outputs


def build_item(repo_root, path):
    full = repo_root / path
    exists = full.exists()
    kind = "directory" if full.is_dir() else "file" if full.is_file() else "missing"
    sample = read_sample(full) if full.is_file() else ""
    family = infer_family(path)
    writes, network, build, package, mutates = infer_risks(path, family, sample)
    risk = infer_risk(family, writes, network, build, package, mutates)
    execution_safety = infer_execution_safety(path, family, risk, writes, network, build, package, mutates)
    wrapper_candidate, wrapper_priority = wrapper_candidate_for(path, family, risk, execution_safety, writes, network, package, mutates)
    fate = infer_fate(family, path, risk)
    inputs, outputs = known_io(family, path, writes, network, build, package)
    blockers = []
    if family == "unknown":
        blockers.append("needs classification before execution")
    if network:
        blockers.append("network or GitHub risk")
    if mutates:
        blockers.append("repo mutation risk")
    if package:
        blockers.append("package/release output risk")
    if build:
        blockers.append("build/test output or dependency risk")
    if path in {"tools/validators/check_repo_layout.py", "tools/validators/check_root_allowlist.py"}:
        blockers.append("current local build/out ignored roots block strict runs")
    return {
        "path": path,
        "display_name": Path(path).name or path,
        "family": family,
        "current_name": Path(path).stem or Path(path).name or path,
        "stable_future_owner": stable_owner_for(family, path),
        "aide_task_type": task_type_for(family),
        "fate": fate,
        "risk": risk,
        "execution_safety": execution_safety,
        "execution_allowed_now": False,
        "apply_allowed_now": False,
        "network_allowed_now": False,
        "writes_allowed_now": False,
        "known_outputs": outputs,
        "known_inputs": inputs,
        "preservation_required": True,
        "wrapper_candidate": wrapper_candidate,
        "wrapper_priority": wrapper_priority,
        "reason": reason_for(family, fate, risk, execution_safety),
        "blockers": blockers,
        "evidence_refs": evidence_refs_for(path, family, wrapper_candidate),
        "exists": exists,
        "type": kind,
        "file_extension": full.suffix.lower() if full.is_file() else "",
        "shebang": shebang(sample),
        "executable_bit": executable_bit(full) if exists else False,
        "command_surface": command_surface_for(path, sample),
        "references": {
            "python": path.endswith(".py") or contains_any(sample, ["python"]),
            "powershell": path.endswith(".ps1") or contains_any(sample, ["powershell", "pwsh"]),
            "batch": path.endswith((".cmd", ".bat")),
            "cmake": path.endswith(".cmake") or Path(path).name.lower() == "cmakelists.txt" or contains_any(sample, ["cmake"]),
            "github_actions": path.startswith(".github/workflows/"),
        },
    }


def reason_for(family, fate, risk, execution_safety):
    if fate == "preserve_unknown":
        return "Insufficient evidence; preserve and do not execute."
    if family in {"xstack", "audit", "repo_policy", "test"}:
        return "Useful legacy validation surface; wrap through AIDE before rename or retirement."
    if execution_safety == "safe_observed":
        return "Prior AIDE/validation evidence shows a bounded read-only or no-apply command surface."
    if risk in {"high", "protected"}:
        return "Protected or high-risk tool surface; inventory only until wrapper evidence exists."
    return "Tooling surface is useful and should remain preserved under AIDE control-plane evidence."


def discover(repo_root):
    paths = set()
    for root in DISCOVERY_ROOTS:
        full_root = repo_root / root
        if not full_root.exists():
            paths.add(root)
            continue
        paths.add(root)
        if full_root.is_file():
            continue
        for item in full_root.rglob("*"):
            rel = relpath(item, repo_root)
            if should_skip(item):
                continue
            if item.is_file() and is_candidate_file(item):
                paths.add(rel)
    return sorted(paths, key=lambda value: (value.lower(), value))


def summarize(items):
    summary = {
        "total_items": len(items),
        "by_family": {},
        "by_fate": {},
        "by_risk": {},
        "wrapper_candidate_count": 0,
        "execution_allowed_count": 0,
    }
    for item in items:
        for key, field in [("by_family", "family"), ("by_fate", "fate"), ("by_risk", "risk")]:
            value = item[field]
            summary[key][value] = summary[key].get(value, 0) + 1
        if item["wrapper_candidate"]:
            summary["wrapper_candidate_count"] += 1
        if item["execution_allowed_now"]:
            summary["execution_allowed_count"] += 1
    for key in ["by_family", "by_fate", "by_risk"]:
        summary[key] = dict(sorted(summary[key].items()))
    return summary


def build_inventory(repo_root, source_head):
    paths = discover(repo_root)
    items = [build_item(repo_root, path) for path in paths]
    return {
        "schema_version": "dominium.aide.tool_recycling_inventory.v1",
        "task_id": "AIDE-STRUCTURE-01",
        "source_head": source_head,
        "evidence_inputs": [
            ".aide/reports/AIDE-STRUCTURE-00-status.md",
            ".aide/reports/AIDE-STRUCTURE-00-validation.md",
            ".aide/reports/AIDE-STRUCTURE-00-blockers.md",
            ".aide/tools/latest-tool-inventory.json",
            ".aide/reports/DOM-AIDE-02-wrapper-selection.md",
            "docs/aide/XSTACK_RECYCLING_PLAN.md",
            "docs/aide/AIDE_REFACTOR_FRAMEWORK.md",
        ],
        "summary": summarize(items),
        "items": items,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--source-head", default="", help="Source HEAD SHA to record.")
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON.")
    parser.add_argument("--out", help="Write deterministic JSON to this path.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    data = build_inventory(repo_root, args.source_head)
    json_text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json_text)
    if args.json:
        sys.stdout.write(json_text)
    else:
        print("tool_recycling_inventory: {0} items".format(data["summary"]["total_items"]))
        print(json.dumps(data["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
