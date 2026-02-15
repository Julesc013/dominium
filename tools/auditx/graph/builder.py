"""Deterministic AuditX analysis graph builder."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .analysis_graph import AnalysisGraph


SOURCE_EXTENSIONS = (
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".py",
    ".json",
    ".md",
    ".schema",
    ".txt",
    ".yaml",
    ".yml",
)

SYMBOL_EXTENSIONS = (
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".py",
)

IGNORED_DIRECTORIES = {
    ".git",
    ".vs",
    "__pycache__",
    "build",
    "dist",
    "out",
    "tmp",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]', re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\.]+))", re.MULTILINE)
SYMBOL_RE = re.compile(r"\b(?:def|class|struct|enum|void|int|bool|float|double|char|size_t)\s+([A-Za-z_][A-Za-z0-9_]*)")
COMMAND_ID_RE = re.compile(r"\b(?:client|launcher|setup|server|tool)\.[a-z0-9_.-]+\b")
FILE_REF_RE = re.compile(r"([A-Za-z0-9_.\-/]+(?:\.json|\.md|\.py|\.schema(?:\.json)?|\.txt))")
CTEST_NAME_RE = re.compile(r"dom_add_testx\(\s*NAME\s+([A-Za-z0-9_]+)", re.MULTILINE)
SCHEMA_REF_RE = re.compile(r"\b([a-z0-9_.-]+(?:\.schema(?:\.json)?))\b|\b(dominium\.schema\.[a-z0-9_.-]+)\b", re.IGNORECASE)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid_json"


def _walk_repo_files(repo_root: str) -> List[str]:
    rows: List[str] = []
    ignored = {name.lower() for name in IGNORED_DIRECTORIES}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = sorted(
            item
            for item in dirs
            if item.lower() not in ignored and not item.startswith(".git")
        )
        for name in sorted(files):
            rel = _norm(os.path.relpath(os.path.join(root, name), repo_root))
            ext = os.path.splitext(name.lower())[1]
            if rel.startswith("docs/audit/"):
                continue
            if ext in SOURCE_EXTENSIONS:
                rows.append(rel)
    return sorted(set(rows))


def _collect_changed_paths_from_git(repo_root: str) -> Dict[str, object]:
    git_exe = shutil.which("git")
    if not git_exe:
        return {
            "result": "refusal",
            "reason_code": "refusal.git_unavailable",
            "message": "git executable unavailable",
            "paths": [],
        }
    commands = (
        [git_exe, "-C", repo_root, "diff", "--name-only", "--relative", "HEAD"],
        [git_exe, "-C", repo_root, "ls-files", "--others", "--exclude-standard"],
    )
    rows: List[str] = []
    for command in commands:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if int(proc.returncode) != 0:
            return {
                "result": "refusal",
                "reason_code": "refusal.git_unavailable",
                "message": "git command failed",
                "paths": [],
            }
        rows.extend(_norm(line.strip()) for line in (proc.stdout or "").splitlines() if line.strip())
    return {
        "result": "complete",
        "reason_code": "",
        "message": "",
        "paths": sorted(set(rows)),
    }


def resolve_changed_only_paths(repo_root: str, changed_only: bool) -> Dict[str, object]:
    if not bool(changed_only):
        return {
            "result": "complete",
            "reason_code": "",
            "message": "",
            "paths": [],
            "changed_only": False,
        }
    collected = _collect_changed_paths_from_git(repo_root)
    if collected.get("result") != "complete":
        return {
            "result": "refusal",
            "reason_code": str(collected.get("reason_code", "refusal.git_unavailable")),
            "message": str(collected.get("message", "git unavailable")),
            "paths": [],
            "changed_only": True,
        }
    return {
        "result": "complete",
        "reason_code": "",
        "message": "",
        "paths": list(collected.get("paths") or []),
        "changed_only": True,
    }


def _selected_paths(repo_root: str, changed_only_paths: Optional[Iterable[str]]) -> Tuple[List[str], Set[str], bool]:
    all_files = _walk_repo_files(repo_root)
    all_set = set(all_files)
    if not changed_only_paths:
        return all_files, all_set, False
    selected = sorted(
        _norm(path)
        for path in changed_only_paths
        if _norm(path) in all_set
    )
    selected_set = set(selected)
    return selected, selected_set, True


def _include_file(path: str, changed_only: bool, selected_set: Set[str]) -> bool:
    if not changed_only:
        return True
    return _norm(path) in selected_set


def _add_schema_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> Dict[str, str]:
    schema_nodes: Dict[str, str] = {}
    schema_roots = ["schemas", "schema"]
    for root_name in schema_roots:
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(item for item in dirs if item.lower() not in IGNORED_DIRECTORIES)
            for name in sorted(files):
                if not (name.endswith(".schema.json") or name.endswith(".schema")):
                    continue
                rel = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                if not _include_file(rel, changed_only, selected_set):
                    continue
                payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
                schema_id = ""
                schema_version = ""
                if not err and isinstance(payload, dict):
                    schema_id = str(payload.get("schema_id", "")).strip()
                    schema_version = str(payload.get("schema_version", payload.get("version", ""))).strip()
                if not schema_id:
                    schema_id = rel
                schema_node = graph.add_node(
                    "schema",
                    schema_id,
                    {
                        "schema_version": schema_version,
                        "path": rel,
                    },
                )
                file_node = graph.add_node("file", rel)
                graph.add_edge("schema_declared_in", schema_node, file_node)
                schema_nodes[schema_id] = schema_node
                schema_nodes[schema_id.lower()] = schema_node
                schema_nodes[_norm(rel)] = schema_node
                schema_nodes[_norm(rel).lower()] = schema_node
                schema_nodes[os.path.basename(rel)] = schema_node
                schema_nodes[os.path.basename(rel).lower()] = schema_node
                if rel.endswith(".schema.json"):
                    schema_nodes[os.path.basename(rel).replace(".schema.json", "")] = schema_node
                    schema_nodes[os.path.basename(rel).replace(".schema.json", "").lower()] = schema_node
                if rel.endswith(".schema"):
                    schema_nodes[os.path.basename(rel).replace(".schema", "")] = schema_node
                    schema_nodes[os.path.basename(rel).replace(".schema", "").lower()] = schema_node
    return schema_nodes


def _add_pack_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> None:
    packs_root = os.path.join(repo_root, "packs")
    if not os.path.isdir(packs_root):
        return
    manifests: List[str] = []
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(item for item in dirs if item.lower() not in IGNORED_DIRECTORIES)
        for name in sorted(files):
            if name != "pack.json":
                continue
            rel = _norm(os.path.relpath(os.path.join(root, name), repo_root))
            manifests.append(rel)
    for rel in sorted(manifests):
        if not _include_file(rel, changed_only, selected_set):
            continue
        payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
        if err or not isinstance(payload, dict):
            continue
        pack_id = str(payload.get("pack_id", "")).strip() or rel
        pack_node = graph.add_node("pack", pack_id, {"manifest_path": rel, "version": str(payload.get("version", ""))})
        file_node = graph.add_node("file", rel)
        graph.add_edge("pack_manifest", file_node, pack_node)
        deps = payload.get("dependencies")
        if isinstance(deps, list):
            for dep in sorted(str(item).strip() for item in deps if str(item).strip()):
                dep_node = graph.add_node("pack", dep)
                graph.add_edge("pack_depends_on", pack_node, dep_node)


def _add_domain_solver_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> None:
    domain_rel = "data/registries/domain_registry.json"
    solver_rel = "data/registries/solver_registry.json"
    contract_rel = "data/registries/domain_contract_registry.json"

    domain_map: Dict[str, str] = {}
    if _include_file(domain_rel, changed_only, selected_set):
        payload, err = _read_json(os.path.join(repo_root, domain_rel.replace("/", os.sep)))
        if not err and isinstance(payload, dict):
            rows = payload.get("records")
            if isinstance(rows, list):
                graph.add_node("file", domain_rel)
                for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("domain_id", ""))):
                    domain_id = str(row.get("domain_id", "")).strip()
                    if not domain_id:
                        continue
                    domain_node = graph.add_node("domain", domain_id, {"status": str(row.get("status", ""))})
                    domain_map[domain_id] = domain_node
                    graph.add_edge("registry_declares_domain", graph.add_node("file", domain_rel), domain_node)

    contract_map: Dict[str, str] = {}
    if _include_file(contract_rel, changed_only, selected_set):
        payload, err = _read_json(os.path.join(repo_root, contract_rel.replace("/", os.sep)))
        if not err and isinstance(payload, dict):
            rows = payload.get("records")
            if isinstance(rows, list):
                graph.add_node("file", contract_rel)
                for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("contract_id", ""))):
                    contract_id = str(row.get("contract_id", "")).strip()
                    if not contract_id:
                        continue
                    contract_node = graph.add_node("contract", contract_id)
                    contract_map[contract_id] = contract_node
                    graph.add_edge("registry_declares_contract", graph.add_node("file", contract_rel), contract_node)

    if _include_file(solver_rel, changed_only, selected_set):
        payload, err = _read_json(os.path.join(repo_root, solver_rel.replace("/", os.sep)))
        if err or not isinstance(payload, dict):
            return
        rows = payload.get("records")
        if not isinstance(rows, list):
            return
        solver_file = graph.add_node("file", solver_rel)
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("solver_id", ""))):
            solver_id = str(row.get("solver_id", "")).strip()
            if not solver_id:
                continue
            solver_node = graph.add_node(
                "solver",
                solver_id,
                {
                    "cost_class": str(row.get("cost_class", "")),
                    "resolution": str(row.get("resolution", "")),
                },
            )
            graph.add_edge("registry_declares_solver", solver_file, solver_node)
            for domain_id in sorted(str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip()):
                domain_node = domain_map.get(domain_id) or graph.add_node("domain", domain_id)
                graph.add_edge("solver_domain", solver_node, domain_node)
            for contract_id in sorted(str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip()):
                contract_node = contract_map.get(contract_id) or graph.add_node("contract", contract_id)
                graph.add_edge("solver_contract", solver_node, contract_node)


def _add_product_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> None:
    rel = "data/registries/product_graph.json"
    if not _include_file(rel, changed_only, selected_set):
        return
    payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
    if err or not isinstance(payload, dict):
        return
    entries = (((payload.get("record") or {}).get("entries")) or [])
    if not isinstance(entries, list):
        return
    file_node = graph.add_node("file", rel)
    for entry in sorted((item for item in entries if isinstance(item, dict)), key=lambda item: str(item.get("product_id", ""))):
        product_id = str(entry.get("product_id", "")).strip()
        if not product_id:
            continue
        product_node = graph.add_node("product", product_id, {"status": str(entry.get("status", ""))})
        graph.add_edge("registry_declares_product", file_node, product_node)


def _add_test_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> None:
    test_files: List[str] = []
    tests_root = os.path.join(repo_root, "tests")
    if os.path.isdir(tests_root):
        for root, dirs, files in os.walk(tests_root):
            dirs[:] = sorted(item for item in dirs if item.lower() not in IGNORED_DIRECTORIES)
            for name in sorted(files):
                if name == "CMakeLists.txt":
                    rel = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                    test_files.append(rel)
    for rel in sorted(test_files):
        if not _include_file(rel, changed_only, selected_set):
            continue
        file_node = graph.add_node("file", rel)
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        for match in CTEST_NAME_RE.finditer(text):
            test_id = str(match.group(1)).strip()
            if not test_id:
                continue
            test_node = graph.add_node("test", test_id, {"source": rel})
            graph.add_edge("test_declared_in", test_node, file_node)

    testx_root = os.path.join(repo_root, "tools", "xstack", "testx", "tests")
    if os.path.isdir(testx_root):
        for root, dirs, files in os.walk(testx_root):
            dirs[:] = sorted(item for item in dirs if item.lower() not in IGNORED_DIRECTORIES)
            for name in sorted(files):
                if not (name.startswith("test_") and name.endswith(".py")):
                    continue
                rel = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                if not _include_file(rel, changed_only, selected_set):
                    continue
                test_node = graph.add_node("test", rel, {"source": rel})
                file_node = graph.add_node("file", rel)
                graph.add_edge("test_declared_in", test_node, file_node)


def _command_registry_sources(repo_root: str) -> List[str]:
    roots = os.path.join(repo_root, "data", "registries")
    rows: List[str] = []
    if not os.path.isdir(roots):
        return rows
    for name in sorted(os.listdir(roots)):
        if not name.endswith(".json"):
            continue
        rows.append(_norm(os.path.join("data", "registries", name)))
    return sorted(rows)


def _add_command_nodes(graph: AnalysisGraph, repo_root: str, changed_only: bool, selected_set: Set[str]) -> Dict[str, str]:
    command_map: Dict[str, str] = {}
    registry_files = _command_registry_sources(repo_root)
    for rel in registry_files:
        if not _include_file(rel, changed_only, selected_set):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        if not text:
            continue
        file_node = graph.add_node("file", rel)
        for command_id in sorted(set(COMMAND_ID_RE.findall(text))):
            command_node = graph.add_node("command", command_id, {"source_registry": rel})
            command_map[command_id] = command_node
            graph.add_edge("command_registry_declares", file_node, command_node)
    return command_map


def _add_file_nodes_and_edges(
    graph: AnalysisGraph,
    repo_root: str,
    file_paths: List[str],
    changed_only: bool,
    selected_set: Set[str],
    command_map: Dict[str, str],
    schema_nodes: Dict[str, str],
) -> None:
    all_paths_set = set(file_paths)
    for rel in sorted(file_paths):
        if not _include_file(rel, changed_only, selected_set):
            continue
        file_node = graph.add_node("file", rel)
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        text = _read_text(abs_path)
        ext = os.path.splitext(rel)[1].lower()
        if not text:
            continue

        if ext in SYMBOL_EXTENSIONS:
            for symbol in sorted(set(SYMBOL_RE.findall(text))):
                symbol_node = graph.add_node("symbol", symbol)
                graph.add_edge("defines_symbol", file_node, symbol_node)

        for include_ref in sorted(set(INCLUDE_RE.findall(text))):
            include_node = graph.add_node("file", _norm(include_ref))
            graph.add_edge("include", file_node, include_node)

        for module_a, module_b in IMPORT_RE.findall(text):
            module_ref = module_a or module_b
            if not module_ref:
                continue
            symbol_node = graph.add_node("symbol", str(module_ref))
            graph.add_edge("import", file_node, symbol_node)

        for command_id in sorted(set(COMMAND_ID_RE.findall(text))):
            command_node = command_map.get(command_id) or graph.add_node("command", command_id)
            command_map[command_id] = command_node
            graph.add_edge("command_implemented_by", command_node, file_node)
            if "/ui/" in rel or rel.startswith("docs/ui/"):
                graph.add_edge("ui_ir_command", file_node, command_node)

        schema_refs = set()
        for left, right in SCHEMA_REF_RE.findall(text):
            token = str(left or right or "").strip()
            if token:
                schema_refs.add(token)
        for schema_ref in sorted(schema_refs):
            schema_node = schema_nodes.get(schema_ref)
            if not schema_node:
                schema_node = schema_nodes.get(schema_ref.lower())
            if not schema_node:
                continue
            graph.add_edge("file_uses_schema", file_node, schema_node)

        for match in FILE_REF_RE.findall(text):
            ref = _norm(match.strip())
            if not ref:
                continue
            if ref not in all_paths_set:
                continue
            ref_node = graph.add_node("file", ref)
            graph.add_edge("file_ref", file_node, ref_node)


def _add_schema_registry_edges(graph: AnalysisGraph, repo_root: str, schema_nodes: Dict[str, str], changed_only: bool, selected_set: Set[str]) -> None:
    registry_root = os.path.join(repo_root, "data", "registries")
    if not os.path.isdir(registry_root):
        return
    for name in sorted(os.listdir(registry_root)):
        if not name.endswith(".json"):
            continue
        rel = _norm(os.path.join("data", "registries", name))
        if not _include_file(rel, changed_only, selected_set):
            continue
        payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
        if err or not isinstance(payload, dict):
            continue
        schema_id = str(payload.get("schema_id", "")).strip()
        if not schema_id:
            continue
        schema_node = schema_nodes.get(schema_id)
        if not schema_node:
            schema_node = graph.add_node("schema", schema_id, {"schema_version": str(payload.get("schema_version", ""))})
            schema_nodes[schema_id] = schema_node
        registry_file = graph.add_node("file", rel)
        graph.add_edge("schema_registry", schema_node, registry_file)


def build_analysis_graph(repo_root: str, changed_only_paths: Optional[Iterable[str]] = None, skip_dirs: Optional[Iterable[str]] = None) -> AnalysisGraph:
    del skip_dirs  # directory policy is fixed in IGNORED_DIRECTORIES for deterministic behavior
    file_paths, selected_set, changed_only = _selected_paths(repo_root, changed_only_paths)
    graph = AnalysisGraph()

    schema_nodes = _add_schema_nodes(graph, repo_root, changed_only, selected_set)
    _add_pack_nodes(graph, repo_root, changed_only, selected_set)
    _add_domain_solver_nodes(graph, repo_root, changed_only, selected_set)
    _add_product_nodes(graph, repo_root, changed_only, selected_set)
    _add_test_nodes(graph, repo_root, changed_only, selected_set)
    command_map = _add_command_nodes(graph, repo_root, changed_only, selected_set)
    _add_file_nodes_and_edges(
        graph=graph,
        repo_root=repo_root,
        file_paths=file_paths,
        changed_only=changed_only,
        selected_set=selected_set,
        command_map=command_map,
        schema_nodes=schema_nodes,
    )
    _add_schema_registry_edges(graph, repo_root, schema_nodes, changed_only, selected_set)
    return graph
