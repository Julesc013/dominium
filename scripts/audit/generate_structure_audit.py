#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from datetime import date


TEXT_EXTS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".inl",
    ".inc",
    ".ipp",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".schema",
    ".md",
    ".txt",
    ".cmake",
}

ROOT_DOC_FILES = (
    "README.md",
    "DOMINIUM.md",
    "GOVERNANCE.md",
    "MODDING.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "CODE_CHANGE_JUSTIFICATION.md",
    "LICENSE.md",
)

LOCAL_GENERATED_HINTS = {
    ".vs",
    "build",
    "out",
    "dist",
    "tmp",
    "ci",
    "sdk",
}

CATEGORY_BY_TOP = {
    ".github": "automation",
    ".vscode": "developer_workspace",
    "app": "app_runtime",
    "client": "product_client",
    "cmake": "build_system",
    "data": "data_content",
    "docs": "documentation",
    "engine": "engine_runtime",
    "game": "game_runtime",
    "ide": "tooling_ide",
    "labs": "quarantine_experimental",
    "launcher": "product_launcher",
    "legacy": "archive_legacy",
    "libs": "shared_libraries",
    "repo": "governance_and_outputs",
    "schema": "schemas",
    "scripts": "automation_scripts",
    "server": "product_server",
    "setup": "product_setup",
    "tests": "tests",
    "tools": "tools",
    "updates": "update_metadata",
    "root": "root_file",
}

FORBIDDEN_LEGACY_GATING_TOKEN_PARTS = (
    "S" + "TAGE_",
    "requires" + "_stage",
    "provides" + "_stage",
    "stage" + "_features",
    "required" + "_stage",
    "PROGRE" + "SSION_",
    "COMPLE" + "TION_",
)
FORBIDDEN_LEGACY_GATING_TOKEN_RE = re.compile(
    r"\b(" + "|".join(re.escape(token) for token in FORBIDDEN_LEGACY_GATING_TOKEN_PARTS) + r")\b"
)
DOC_REF_RE = re.compile(r"\bdocs/[A-Za-z0-9_./-]+\.(?:md|txt|json)\b", re.IGNORECASE)


def run_git(repo_root, args):
    proc = subprocess.run(
        ["git"] + args,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("git {} failed: {}".format(" ".join(args), proc.stderr.strip()))
    return proc.stdout.strip()


def normalize(path):
    return path.replace("\\", "/").strip("/")


def parse_repo_intent(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "REPO_INTENT.md")
    mapping = {}
    if not os.path.isfile(path):
        return mapping
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if "|" not in line or "`" not in line:
                continue
            parts = [segment.strip() for segment in line.split("|")]
            if len(parts) < 5:
                continue
            refs = re.findall(r"`([^`]+)`", parts[1])
            purpose = parts[2]
            change_scope = parts[3]
            status = parts[4]
            for ref in refs:
                name = normalize(ref)
                if not name:
                    continue
                mapping[name] = {
                    "purpose": purpose,
                    "change_scope": change_scope,
                    "status": status,
                }
    return mapping


def classify_root_file(name, tracked):
    if name == ".dominium_build_number":
        return "generated_build_counter", "remove_from_root_or_keep_ignored"
    if name.startswith("VERSION_"):
        return "version_contract", "keep_root_canonical"
    if name in ("CMakeLists.txt", "CMakePresets.json", ".gitignore", ".gitattributes"):
        return "build_governance_contract", "keep_root_canonical"
    if name in ROOT_DOC_FILES:
        return "root_entry_document", "keep_but_link_to_canonical_docs_only"
    if tracked:
        return "root_misc_tracked", "review"
    return "root_misc_local", "remove_or_move_local"


def classify_root_dir(name, tracked, listed):
    if tracked and listed:
        return "keep"
    if tracked and not listed:
        return "violation_tracked_not_in_repo_intent"
    if not tracked and name in LOCAL_GENERATED_HINTS:
        return "local_generated_ok"
    if not tracked and listed:
        return "local_untracked_listed"
    return "local_unknown_review"


def detect_shim_dirs(repo_root, tracked_dirs, tracked_files):
    shim_hits = []
    for root_dir in sorted(tracked_dirs):
        cmake_rel = root_dir + "/CMakeLists.txt"
        if cmake_rel not in tracked_files:
            continue
        files_under = [path for path in tracked_files if path.startswith(root_dir + "/")]
        if len(files_under) > 3:
            continue
        cmake_abs = os.path.join(repo_root, cmake_rel.replace("/", os.sep))
        try:
            with open(cmake_abs, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        except OSError:
            continue
        has_redirect = "add_subdirectory(" in text
        has_real_targets = ("add_library(" in text) or ("add_executable(" in text)
        starts_shared = root_dir.startswith("shared_")
        if starts_shared or (has_redirect and not has_real_targets):
            shim_hits.append(
                {
                    "dir": root_dir,
                    "cmake": cmake_rel,
                    "tracked_file_count": len(files_under),
                    "shape": "shared_prefix" if starts_shared else "redirect_only",
                }
            )
    return shim_hits


def gather_root_doc_link_issues(repo_root, root_files):
    ignore_files = {"CHANGELOG.md"}
    missing = []
    for name in root_files:
        if name in ignore_files:
            continue
        if not name.lower().endswith(".md"):
            continue
        path = os.path.join(repo_root, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        except OSError:
            continue
        for ref in sorted(set(DOC_REF_RE.findall(text))):
            ref_norm = normalize(ref)
            ref_abs = os.path.join(repo_root, ref_norm.replace("/", os.sep))
            if not os.path.isfile(ref_abs):
                missing.append({"file": name, "reference": ref_norm})
    return missing


def gather_legacy_token_hits(repo_root, tracked_files):
    hits = []
    for rel in tracked_files:
        if rel.startswith("docs/"):
            continue
        ext = os.path.splitext(rel)[1].lower()
        if ext not in TEXT_EXTS:
            continue
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        except OSError:
            continue
        if FORBIDDEN_LEGACY_GATING_TOKEN_RE.search(text):
            hits.append(rel)
    return sorted(hits)


def build_tracked_inventory(tracked_files):
    items = []
    for rel in tracked_files:
        top = rel.split("/", 1)[0] if "/" in rel else "root"
        category = CATEGORY_BY_TOP.get(top, "unknown")
        action = "keep"
        if top == "root":
            _, action = classify_root_file(rel, True)
        items.append(
            {
                "path": rel,
                "top_level": top,
                "category": category,
                "recommended_action": action,
            }
        )
    return items


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_markdown(path, report):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    lines.append("Status: DERIVED")
    lines.append("Last Reviewed: {}".format(report["meta"]["generated_on"]))
    lines.append("Supersedes: none")
    lines.append("Superseded By: none")
    lines.append("Purpose: Repository structure audit and consolidation report")
    lines.append("Authority: NON-CANONICAL")
    lines.append("")
    lines.append("# Repository Structure Audit")
    lines.append("")
    lines.append("- Date: {}".format(report["meta"]["generated_on"]))
    lines.append("- Tracked files audited: {}".format(report["summary"]["tracked_files"]))
    lines.append("- Root directories audited: {}".format(report["summary"]["root_dirs"]))
    lines.append("- Root files audited: {}".format(report["summary"]["root_files"]))
    lines.append("")
    lines.append("## Top-Level Directory Audit")
    lines.append("")
    lines.append("| Directory | Tracked | Listed In REPO_INTENT | Status | Recommendation |")
    lines.append("|---|---|---|---|---|")
    for entry in report["root_dirs"]:
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                entry["name"],
                "yes" if entry["tracked"] else "no",
                "yes" if entry["listed_in_repo_intent"] else "no",
                entry["repo_intent_status"] or "-",
                entry["recommended_action"],
            )
        )
    lines.append("")
    lines.append("## Root File Audit")
    lines.append("")
    lines.append("| File | Tracked | Kind | Recommendation |")
    lines.append("|---|---|---|---|")
    for entry in report["root_files"]:
        lines.append(
            "| `{}` | {} | {} | {} |".format(
                entry["name"],
                "yes" if entry["tracked"] else "no",
                entry["kind"],
                entry["recommended_action"],
            )
        )
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    lines.append("- Root shim candidates: {}".format(len(report["findings"]["root_shim_candidates"])))
    for hit in report["findings"]["root_shim_candidates"]:
        lines.append(
            "  - `{}` ({}, {} tracked files)".format(
                hit["dir"], hit["shape"], hit["tracked_file_count"]
            )
        )
    lines.append("- Missing root-doc references: {}".format(len(report["findings"]["missing_root_doc_refs"])))
    for hit in report["findings"]["missing_root_doc_refs"]:
        lines.append("  - `{}` references missing `{}`".format(hit["file"], hit["reference"]))
    lines.append("- Forbidden legacy gating tokens outside docs: {}".format(len(report["findings"]["legacy_token_hits"])))
    for rel in report["findings"]["legacy_token_hits"][:50]:
        lines.append("  - `{}`".format(rel))
    if len(report["findings"]["legacy_token_hits"]) > 50:
        lines.append("  - ... {} more".format(len(report["findings"]["legacy_token_hits"]) - 50))
    lines.append("")
    lines.append("## Consolidation Decisions")
    lines.append("")
    lines.append("- Root source module shims are forbidden and blocked by RepoX (`INV-ROOT-MODULE-SHIM`).")
    lines.append("- Runtime source lives under product/library roots only (`engine`, `game`, `client`, `server`, `launcher`, `setup`, `libs`, `tools`, `app`).")
    lines.append("- Root generated folders (`build`, `out`, `dist`, `tmp`, `.vs`, `ci`, `sdk`) remain local and untracked.")
    lines.append("- Root documentation must point to existing canonical docs; broken links are remediation items.")
    lines.append("")
    lines.append("## Inventory Artifact")
    lines.append("")
    lines.append("- Full per-file inventory is written to `docs/audit/REPO_STRUCTURE_AUDIT.json`.")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate full repository structure audit.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-json", default="docs/audit/REPO_STRUCTURE_AUDIT.json")
    parser.add_argument("--out-md", default="docs/audit/REPO_STRUCTURE_AUDIT.md")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    tracked_files = sorted(
        [normalize(item) for item in run_git(repo_root, ["ls-tree", "-r", "--name-only", "HEAD"]).splitlines() if item.strip()]
    )
    tracked_dirs = set(
        normalize(item) for item in run_git(repo_root, ["ls-tree", "-d", "--name-only", "HEAD"]).splitlines() if item.strip()
    )

    fs_root_dirs = sorted(
        entry
        for entry in os.listdir(repo_root)
        if os.path.isdir(os.path.join(repo_root, entry))
    )
    fs_root_files = sorted(
        entry
        for entry in os.listdir(repo_root)
        if os.path.isfile(os.path.join(repo_root, entry))
    )

    repo_intent = parse_repo_intent(repo_root)
    root_dirs = []
    for name in fs_root_dirs:
        if name == ".git":
            continue
        listed = name in repo_intent
        tracked = name in tracked_dirs
        intent = repo_intent.get(name, {})
        root_dirs.append(
            {
                "name": name,
                "tracked": tracked,
                "listed_in_repo_intent": listed,
                "repo_intent_purpose": intent.get("purpose", ""),
                "repo_intent_change_scope": intent.get("change_scope", ""),
                "repo_intent_status": intent.get("status", ""),
                "recommended_action": classify_root_dir(name, tracked, listed),
            }
        )

    root_files = []
    tracked_root_files = set(item for item in tracked_files if "/" not in item)
    for name in fs_root_files:
        tracked = name in tracked_root_files
        kind, action = classify_root_file(name, tracked)
        root_files.append(
            {
                "name": name,
                "tracked": tracked,
                "kind": kind,
                "recommended_action": action,
            }
        )

    report = {
        "meta": {
            "generated_on": str(date.today()),
            "repo_root": normalize(repo_root),
        },
        "summary": {
            "tracked_files": len(tracked_files),
            "root_dirs": len(root_dirs),
            "root_files": len(root_files),
        },
        "root_dirs": sorted(root_dirs, key=lambda item: item["name"].lower()),
        "root_files": sorted(root_files, key=lambda item: item["name"].lower()),
        "findings": {
            "root_shim_candidates": detect_shim_dirs(repo_root, tracked_dirs, tracked_files),
            "missing_root_doc_refs": gather_root_doc_link_issues(repo_root, [item["name"] for item in root_files if item["tracked"]]),
            "legacy_token_hits": gather_legacy_token_hits(repo_root, tracked_files),
        },
        "tracked_file_inventory": build_tracked_inventory(tracked_files),
    }

    json_out = os.path.join(repo_root, args.out_json.replace("/", os.sep))
    md_out = os.path.join(repo_root, args.out_md.replace("/", os.sep))
    write_json(json_out, report)
    write_markdown(md_out, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
