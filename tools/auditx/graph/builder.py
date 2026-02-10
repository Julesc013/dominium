"""Deterministic AuditX graph builder."""

import json
import os
import re

from .analysis_graph import AnalysisGraph


SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py", ".json", ".schema", ".md", ".txt")
SYMBOL_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py")
SKIP_DIRS_DEFAULT = {".git", ".vs", "build", "out", "dist", "tmp", "__pycache__"}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')
IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\.]+))")
SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)
SCHEMA_VERSION_RE = re.compile(r"^\s*schema_version\s*:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", re.MULTILINE)
COMMAND_ID_RE = re.compile(r"\b(?:client|launcher|setup|server|tool)\.[a-z0-9_.-]+\b")
SYMBOL_RE = re.compile(r"\b(?:void|int|bool|float|double|char|size_t|struct|class|def)\s+([A-Za-z_][A-Za-z0-9_]*)")
CTEST_NAME_RE = re.compile(r"dom_add_testx\(\s*NAME\s+([A-Za-z0-9_]+)", re.MULTILINE)


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _walk_repo_files(repo_root, skip_dirs):
    skip = {item.lower() for item in skip_dirs}
    records = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = sorted([item for item in dirs if item.lower() not in skip and not item.startswith(".git")])
        files = sorted(files)
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), repo_root).replace("\\", "/")
            ext = os.path.splitext(rel)[1].lower()
            if ext in SOURCE_EXTS:
                records.append(rel)
    return sorted(records)


def _collect_test_nodes(repo_root, graph):
    tests_root = os.path.join(repo_root, "tests")
    if not os.path.isdir(tests_root):
        return
    cmake_files = []
    for root, dirs, files in os.walk(tests_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name == "CMakeLists.txt":
                cmake_files.append(os.path.join(root, name))
    for path in sorted(cmake_files):
        text = _read_text(path)
        for match in CTEST_NAME_RE.finditer(text):
            test_name = match.group(1)
            test_node = graph.add_node("test", test_name, {"source": os.path.relpath(path, repo_root).replace("\\", "/")})
            file_node = graph.add_node("file", os.path.relpath(path, repo_root).replace("\\", "/"))
            graph.add_edge("test_declares", file_node, test_node)


def _collect_product_nodes(repo_root, graph):
    product_graph = os.path.join(repo_root, "data", "registries", "product_graph.json")
    if not os.path.isfile(product_graph):
        return
    try:
        payload = json.loads(_read_text(product_graph) or "{}")
    except ValueError:
        return
    record = payload.get("record", {})
    entries = record.get("entries", [])
    if not isinstance(entries, list):
        return
    for entry in sorted(entries, key=lambda item: str(item.get("product_id", ""))):
        product_id = str(entry.get("product_id", "")).strip()
        if not product_id:
            continue
        graph.add_node("product", product_id, {"status": str(entry.get("status", ""))})


def _collect_pack_nodes(repo_root, graph):
    packs_root = os.path.join(repo_root, "data", "packs")
    if not os.path.isdir(packs_root):
        return
    manifests = []
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name == "pack_manifest.json":
                manifests.append(os.path.join(root, name))
    for manifest in sorted(manifests):
        rel = os.path.relpath(manifest, repo_root).replace("\\", "/")
        try:
            payload = json.loads(_read_text(manifest) or "{}")
        except ValueError:
            payload = {}
        pack_id = str(payload.get("pack_id", "")).strip() or rel
        pack_node = graph.add_node("pack", pack_id, {"manifest_path": rel})
        file_node = graph.add_node("file", rel)
        graph.add_edge("pack_manifest", file_node, pack_node)
        for req in payload.get("requires", []) if isinstance(payload.get("requires"), list) else []:
            req_id = str(req)
            if req_id:
                req_node = graph.add_node("pack", req_id)
                graph.add_edge("pack_requires", pack_node, req_node)


def _collect_schema_nodes(repo_root, graph):
    schema_root = os.path.join(repo_root, "schema")
    if not os.path.isdir(schema_root):
        return
    schema_files = []
    for root, dirs, files in os.walk(schema_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name.lower().endswith(".schema"):
                schema_files.append(os.path.join(root, name))
    for path in sorted(schema_files):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        text = _read_text(path)
        schema_id_match = SCHEMA_ID_RE.search(text)
        schema_version_match = SCHEMA_VERSION_RE.search(text)
        schema_id = schema_id_match.group(1) if schema_id_match else rel
        schema_version = schema_version_match.group(1) if schema_version_match else ""
        schema_node = graph.add_node("schema", schema_id, {"schema_version": schema_version, "path": rel})
        file_node = graph.add_node("file", rel)
        graph.add_edge("schema_declared_in", schema_node, file_node)


def _collect_file_graph(repo_root, graph, files):
    schema_ids = []
    for node in graph.nodes.values():
        if node.node_type == "schema":
            schema_ids.append(node.label)
    schema_ids = sorted(schema_ids)
    for rel in sorted(files):
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        text = _read_text(path)
        file_node = graph.add_node("file", rel)
        ext = os.path.splitext(rel)[1].lower()
        if ext in SYMBOL_EXTS:
            for match in SYMBOL_RE.finditer(text):
                symbol = match.group(1)
                symbol_node = graph.add_node("symbol", symbol)
                graph.add_edge("defines_symbol", file_node, symbol_node)
        if ext in (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"):
            for match in INCLUDE_RE.finditer(text):
                include_ref = match.group(1).replace("\\", "/")
                include_node = graph.add_node("file", include_ref)
                graph.add_edge("include", file_node, include_node)
        if ext == ".py":
            for match in IMPORT_RE.finditer(text):
                mod_ref = match.group(1) or match.group(2)
                if not mod_ref:
                    continue
                import_node = graph.add_node("symbol", mod_ref)
                graph.add_edge("import", file_node, import_node)
        for match in COMMAND_ID_RE.finditer(text):
            cmd_id = match.group(0)
            cmd_node = graph.add_node("command", cmd_id)
            graph.add_edge("command_ref", file_node, cmd_node)
            if "/ui/" in rel or rel.startswith("docs/ui/"):
                graph.add_edge("command_binding", file_node, cmd_node)
        for schema_id in schema_ids:
            if schema_id and schema_id in text:
                schema_node = graph.add_node("schema", schema_id)
                graph.add_edge("schema_usage", file_node, schema_node)


def build_analysis_graph(repo_root, changed_only_paths=None, skip_dirs=None):
    graph = AnalysisGraph()
    skip = set(SKIP_DIRS_DEFAULT)
    if skip_dirs:
        skip.update(skip_dirs)

    all_files = _walk_repo_files(repo_root, skip)
    if changed_only_paths:
        selected = sorted({path.replace("\\", "/") for path in changed_only_paths if path.replace("\\", "/") in set(all_files)})
    else:
        selected = all_files

    _collect_schema_nodes(repo_root, graph)
    _collect_pack_nodes(repo_root, graph)
    _collect_product_nodes(repo_root, graph)
    _collect_test_nodes(repo_root, graph)
    _collect_file_graph(repo_root, graph, selected)
    return graph

