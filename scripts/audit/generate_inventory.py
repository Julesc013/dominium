#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from pathlib import Path


SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py"}
DOC_EXTS = {".md", ".txt"}

BIN_EXTS = {".exe", ".dll", ".so", ".dylib", ".bin"}
LIB_EXTS = {".lib", ".a"}

PACK_MANIFEST = "pack_manifest.json"

STUB_PATTERNS = ("_stub.", ".stub.")
TODO_RE = re.compile(r"\bTODO\b", re.IGNORECASE)
FIXME_RE = re.compile(r"\bFIXME\b", re.IGNORECASE)
SKIP_PREFIXES = ("build/", "out/", "dist/", ".git/", "external/", "third_party/")


def repo_rel(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_json(path: Path):
    try:
        return json.loads(read_text(path))
    except ValueError:
        return None


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def should_skip(rel_path: str) -> bool:
    return rel_path.startswith(SKIP_PREFIXES)


def infer_subsystem(rel_path: str) -> str:
    for prefix in (
        "engine/",
        "game/",
        "client/",
        "server/",
        "launcher/",
        "setup/",
        "tools/",
        "libs/",
        "app/",
        "shared_ui_win32/",
    ):
        if rel_path.startswith(prefix):
            return prefix.rstrip("/")
    if rel_path.startswith("schema/"):
        return "schema"
    if rel_path.startswith("data/"):
        return "data"
    if rel_path.startswith("tests/"):
        return "tests"
    if rel_path.startswith("scripts/"):
        return "scripts"
    if rel_path.startswith("cmake/"):
        return "cmake"
    if rel_path.startswith("ci/"):
        return "ci"
    return "root"


def subsystem_docs(repo_root: Path, subsystem: str):
    docs = []
    if subsystem in ("engine", "game", "client", "server", "launcher", "setup", "tools", "app"):
        candidate = repo_root / "docs" / subsystem
        if candidate.is_dir():
            docs.append(repo_rel(repo_root, candidate))
    if subsystem == "schema":
        candidate = repo_root / "docs" / "schema"
        if candidate.is_dir():
            docs.append(repo_rel(repo_root, candidate))
    if subsystem == "data":
        candidate = repo_root / "docs" / "content"
        if candidate.is_dir():
            docs.append(repo_rel(repo_root, candidate))
    if subsystem == "tests":
        candidate = repo_root / "docs" / "ci"
        if candidate.is_dir():
            docs.append(repo_rel(repo_root, candidate))
    candidate = repo_root / "docs" / "architecture"
    if candidate.is_dir():
        docs.append(repo_rel(repo_root, candidate))
    return sorted(set(docs))


def collect_binaries(repo_root: Path, build_roots):
    binaries = []
    libraries = []
    for root in build_roots:
        if not root.exists():
            continue
        for path in iter_files(root):
            ext = path.suffix.lower()
            rel = repo_rel(repo_root, path)
            subsystem = infer_subsystem(rel)
            if ext in BIN_EXTS:
                binaries.append({
                    "path": rel,
                    "subsystem": subsystem,
                    "docs": subsystem_docs(repo_root, subsystem),
                })
            elif ext in LIB_EXTS:
                libraries.append({
                    "path": rel,
                    "subsystem": subsystem,
                    "docs": subsystem_docs(repo_root, subsystem),
                })
    binaries.sort(key=lambda item: item["path"])
    libraries.sort(key=lambda item: item["path"])
    return binaries, libraries


def collect_tools(repo_root: Path):
    tools = []
    tools_root = repo_root / "tools"
    if tools_root.is_dir():
        for path in iter_files(tools_root):
            if path.suffix.lower() in SOURCE_EXTS:
                rel = repo_rel(repo_root, path)
                tools.append({
                    "path": rel,
                    "subsystem": "tools",
                    "docs": subsystem_docs(repo_root, "tools"),
                })
    tools.sort(key=lambda item: item["path"])
    return tools


def collect_packs(repo_root: Path):
    packs = []
    pack_roots = [repo_root / "data" / "packs", repo_root / "repo" / "packs"]
    for root in pack_roots:
        if not root.is_dir():
            continue
        for path in root.rglob(PACK_MANIFEST):
            rel = repo_rel(repo_root, path)
            manifest = load_json(path) or {}
            record = manifest.get("record", {})
            if not isinstance(record, dict):
                record = {}
            pack_id = record.get("pack_id") or manifest.get("pack_id", "")
            pack_version = record.get("pack_version") or manifest.get("pack_version", "")
            packs.append({
                "path": rel,
                "pack_id": pack_id,
                "pack_version": pack_version,
                "dependencies": record.get("dependencies", manifest.get("dependencies", [])),
                "subsystem": "data",
                "docs": subsystem_docs(repo_root, "data"),
            })
    packs.sort(key=lambda item: item["path"])
    return packs


def collect_schemas(repo_root: Path):
    schemas = []
    schema_root = repo_root / "schema"
    if not schema_root.is_dir():
        return schemas
    for path in schema_root.rglob("*.schema"):
        rel = repo_rel(repo_root, path)
        schemas.append({
            "path": rel,
            "subsystem": "schema",
            "docs": subsystem_docs(repo_root, "schema"),
        })
    schemas.sort(key=lambda item: item["path"])
    return schemas


def collect_tests(repo_root: Path):
    tests = []
    tests_root = repo_root / "tests"
    if not tests_root.is_dir():
        return tests
    for path in iter_files(tests_root):
        if path.suffix.lower() in SOURCE_EXTS:
            rel = repo_rel(repo_root, path)
            tests.append({
                "path": rel,
                "subsystem": "tests",
                "docs": subsystem_docs(repo_root, "tests"),
            })
    tests.sort(key=lambda item: item["path"])
    return tests


def collect_coverage(repo_root: Path):
    coverage = []
    root = repo_root / "tests" / "coverage"
    if not root.is_dir():
        return coverage
    for path in root.rglob("coverage.json"):
        rel = repo_rel(repo_root, path)
        data = load_json(path) or {}
        coverage.append({
            "path": rel,
            "level_id": data.get("level_id", ""),
            "level_name": data.get("level_name", ""),
            "status": data.get("status", ""),
            "required_schemas": data.get("required_schemas", []),
            "required_process_families": data.get("required_process_families", []),
            "required_capabilities": data.get("required_capabilities", []),
            "required_refusals": data.get("required_refusals", []),
        })
    coverage.sort(key=lambda item: item["path"])
    return coverage


def collect_ci(repo_root: Path):
    ci = []
    for root in (repo_root / "ci", repo_root / "scripts", repo_root / "cmake"):
        if not root.is_dir():
            continue
        for path in iter_files(root):
            if path.suffix.lower() in SOURCE_EXTS or path.suffix.lower() in DOC_EXTS or path.suffix == ".json":
                rel = repo_rel(repo_root, path)
                ci.append({
                    "path": rel,
                    "subsystem": infer_subsystem(rel),
                    "docs": subsystem_docs(repo_root, infer_subsystem(rel)),
                })
    ci.sort(key=lambda item: item["path"])
    return ci


def collect_docs(repo_root: Path):
    docs = []
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return docs
    for path in iter_files(docs_root):
        if path.suffix.lower() in DOC_EXTS:
            rel = repo_rel(repo_root, path)
            docs.append(rel)
    docs.sort()
    return docs


def collect_data_domains(repo_root: Path):
    data_root = repo_root / "data"
    domains = []
    if not data_root.is_dir():
        return domains
    for entry in data_root.iterdir():
        if entry.is_dir():
            domains.append(repo_rel(repo_root, entry))
    domains.sort()
    return domains


def collect_stub_report(repo_root: Path):
    stubs = []
    todos = []
    for path in iter_files(repo_root):
        rel = repo_rel(repo_root, path)
        if should_skip(rel):
            continue
        text = ""
        is_code = path.suffix.lower() in SOURCE_EXTS
        if is_code:
            text = read_text(path)
            if TODO_RE.search(text) or FIXME_RE.search(text):
                todos.append(rel)
        if any(token in path.name for token in STUB_PATTERNS):
            if not text:
                text = read_text(path)
            classification = "temporary_stub"
            reason = "stub marker"
            if rel.startswith(("tests/", "docs/", "tools/")):
                classification = "acceptable_permanent_stub"
                reason = "non-runtime stub"
            elif "permanent stub" in text.lower() or "intentionally" in text.lower():
                classification = "acceptable_permanent_stub"
                reason = "explicitly documented stub"
            elif rel.startswith(("engine/modules/core/", "engine/modules/sim/", "engine/modules/world/",
                                 "game/core/", "game/rules/")):
                classification = "forbidden_stub"
                reason = "authoritative stub in core runtime"
            stubs.append({
                "path": rel,
                "classification": classification,
                "reason": reason,
            })
    stubs.sort(key=lambda item: item["path"])
    todos.sort()
    counts = {
        "acceptable_permanent_stub": 0,
        "temporary_stub": 0,
        "forbidden_stub": 0,
    }
    for item in stubs:
        key = item["classification"]
        if key in counts:
            counts[key] += 1
    return {"stubs": stubs, "todos": todos, "counts": counts}


def collect_name_checks(repo_root: Path, packs, schemas):
    pack_mismatches = []
    for entry in packs:
        pack_id = entry.get("pack_id", "")
        if not pack_id:
            continue
        folder = Path(entry["path"]).parent.name
        if folder != pack_id:
            pack_mismatches.append({
                "path": entry["path"],
                "pack_id": pack_id,
                "folder": folder,
            })

    schema_mismatches = []
    for entry in schemas:
        path = repo_root / entry["path"]
        text = read_text(path)
        schema_id = ""
        for line in text.splitlines():
            if line.startswith("schema_id:"):
                schema_id = line.split(":", 1)[1].strip()
                break
        if schema_id:
            filename = Path(entry["path"]).name
            stem = filename[:-len(".schema")] if filename.endswith(".schema") else filename
            expected = schema_id
            if expected.startswith("dominium.schema."):
                expected = expected[len("dominium.schema."):]
            expected = expected.replace("-", "_")
            if stem != expected:
                schema_mismatches.append({
                    "path": entry["path"],
                    "schema_id": schema_id,
                    "expected_stem": expected,
                    "actual_stem": stem,
                })

    return {"pack_id_folder_mismatches": pack_mismatches, "schema_id_name_mismatches": schema_mismatches}


def collect_stage_tokens(repo_root: Path):
    hits = []
    token_re = re.compile(r"\bSTAGE_[0-9A-Z_]+\b")
    for path in iter_files(repo_root):
        if path.suffix.lower() not in SOURCE_EXTS and path.suffix.lower() not in DOC_EXTS and path.suffix != ".schema":
            continue
        rel = repo_rel(repo_root, path)
        if should_skip(rel):
            continue
        text = read_text(path)
        if token_re.search(text):
            hits.append(rel)
    hits.sort()
    return hits


def collect_pack_families(packs):
    families = {}
    for pack in packs:
        pack_id = pack.get("pack_id", "")
        if not pack_id:
            continue
        parts = pack_id.split(".")
        if len(parts) < 3:
            family = pack_id
        else:
            family = ".".join(parts[:3])
        families.setdefault(family, 0)
        families[family] += 1
    return [{"family": key, "count": families[key]} for key in sorted(families.keys())]


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate inventory and audit reports.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-inventory", default="docs/audit/INVENTORY.json")
    parser.add_argument("--out-stubs", default="docs/audit/STUB_REPORT.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    build_roots = [repo_root / "build", repo_root / "out" / "build", repo_root / "dist"]

    binaries, libraries = collect_binaries(repo_root, build_roots)
    tools = collect_tools(repo_root)
    packs = collect_packs(repo_root)
    schemas = collect_schemas(repo_root)
    tests = collect_tests(repo_root)
    coverage = collect_coverage(repo_root)
    ci = collect_ci(repo_root)
    docs = collect_docs(repo_root)
    data_domains = collect_data_domains(repo_root)
    stubs = collect_stub_report(repo_root)
    naming = collect_name_checks(repo_root, packs, schemas)
    stage_tokens = collect_stage_tokens(repo_root)
    pack_families = collect_pack_families(packs)

    inventory = {
        "repo_root": str(repo_root),
        "summary": {
            "binaries": len(binaries),
            "libraries": len(libraries),
            "tools": len(tools),
            "packs": len(packs),
            "pack_families": len(pack_families),
            "schemas": len(schemas),
            "tests": len(tests),
            "coverage_entries": len(coverage),
            "docs": len(docs),
            "ci_entries": len(ci),
            "data_domains": len(data_domains),
            "stub_files": len(stubs["stubs"]),
            "todo_hits": len(stubs["todos"]),
            "stage_token_hits": len(stage_tokens),
            "stub_counts": stubs["counts"],
        },
        "binaries": binaries,
        "libraries": libraries,
        "tools": tools,
        "packs": packs,
        "pack_families": pack_families,
        "schemas": schemas,
        "tests": tests,
        "coverage": coverage,
        "ci": ci,
        "docs": docs,
        "data_domains": data_domains,
        "naming_checks": naming,
        "stage_tokens": stage_tokens,
    }

    write_json(repo_root / args.out_inventory, inventory)
    write_json(repo_root / args.out_stubs, stubs)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
