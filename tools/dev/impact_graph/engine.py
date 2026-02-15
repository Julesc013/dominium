"""Deterministic impact graph builder and impact propagation planner."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
from collections import deque
from typing import Dict, Iterable, List, Optional, Set, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


IGNORED_TOP_LEVEL_DIRS = {
    ".git",
    ".vs",
    ".xstack_cache",
    "build",
    "dist",
    "out",
    "tmp",
    "__pycache__",
}

SCANNED_ROOTS = (
    ".github/workflows",
    "bundles",
    "client",
    "data/registries",
    "docs/dev",
    "docs/testing",
    "engine",
    "game",
    "launcher",
    "packs",
    "schemas",
    "server",
    "setup",
    "tools/dev",
    "tools/xstack",
    "worldgen",
)

TEXT_FILE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yml",
    ".yaml",
}

IMPORT_FROM_RE = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+")
IMPORT_RE = re.compile(r"^\s*import\s+([a-zA-Z0-9_\. ,]+)")
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*"([^"]+)"')
TEST_ID_RE = re.compile(r'^\s*TEST_ID\s*=\s*["\']([^"\']+)["\']')
SCHEMA_NAME_TOKEN_RE = re.compile(r"[A-Za-z0-9_.-]+")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def _run_git(repo_root: str, args: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return 127, ""
    return int(proc.returncode), str(proc.stdout or "")


def _git_available(repo_root: str) -> bool:
    code, _out = _run_git(repo_root, ["git", "--version"])
    return code == 0


def detect_changed_files(repo_root: str, base_ref: str = "origin/main") -> Dict[str, object]:
    if not _git_available(repo_root):
        return {
            "result": "refused",
            "reason_code": "refusal.git_unavailable",
            "message": "git is unavailable; changed-only impact graph cannot be computed",
            "changed_files": [],
        }

    changed: List[str] = []
    diff_code, diff_out = _run_git(
        repo_root,
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "{}...HEAD".format(str(base_ref))],
    )
    if diff_code == 0:
        for line in diff_out.splitlines():
            token = _norm(line.strip())
            if token:
                changed.append(token)
    status_code, status_out = _run_git(repo_root, ["git", "status", "--porcelain", "-uall"])
    if status_code == 0:
        for line in status_out.splitlines():
            token = _norm(line[3:].strip() if len(line) >= 3 else line.strip())
            if token:
                changed.append(token)

    out = sorted(set(changed))
    return {
        "result": "complete",
        "changed_files": out,
    }


def _iter_repo_files(repo_root: str) -> Iterable[str]:
    for rel_root in SCANNED_ROOTS:
        abs_root = os.path.join(repo_root, rel_root.replace("/", os.sep))
        if not os.path.exists(abs_root):
            continue
        if os.path.isfile(abs_root):
            yield _norm(os.path.relpath(abs_root, repo_root))
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(
                token for token in dirs if token not in IGNORED_TOP_LEVEL_DIRS and not token.startswith(".")
            )
            for name in sorted(files):
                rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                _, ext = os.path.splitext(name.lower())
                if rel.endswith(".schema.json"):
                    yield rel
                    continue
                if ext in TEXT_FILE_EXTENSIONS:
                    yield rel


def _parse_test_tags(text: str) -> List[str]:
    marker = "TEST_TAGS"
    idx = text.find(marker)
    if idx < 0:
        return ["smoke"]
    assignment = text[idx:]
    eq_idx = assignment.find("=")
    if eq_idx < 0:
        return ["smoke"]
    value = assignment[eq_idx + 1 :].strip()
    line_end = value.find("\n")
    if line_end >= 0:
        value = value[:line_end].strip()
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return ["smoke"]
    if not isinstance(parsed, list):
        return ["smoke"]
    out = sorted(set(str(item).strip() for item in parsed if str(item).strip()))
    return out or ["smoke"]


def _parse_test_id(rel_path: str, text: str) -> str:
    for line in text.splitlines():
        match = TEST_ID_RE.match(line)
        if match:
            token = str(match.group(1)).strip()
            if token:
                return token
    return _norm(rel_path).replace("/", ".").replace(".py", "")


def _module_to_repo_rel(module: str) -> str:
    token = str(module or "").strip().replace(".", "/")
    if not token:
        return ""
    return token + ".py"


def _build_file_index(files: Iterable[str]) -> Dict[str, str]:
    by_rel: Dict[str, str] = {}
    for rel in files:
        by_rel[_norm(rel)] = _norm(rel)
    return by_rel


def _file_node_id(rel_path: str) -> str:
    return "file:" + _norm(rel_path)


def _schema_node_id(name: str) -> str:
    return "schema:" + str(name)


def _registry_node_id(name: str) -> str:
    return "registry:" + str(name)


def _pack_node_id(pack_id: str) -> str:
    return "pack:" + str(pack_id)


def _test_node_id(test_id: str) -> str:
    return "test:" + str(test_id)


def _product_node_id(product_id: str) -> str:
    return "product:" + str(product_id)


def _domain_node_id(domain_id: str) -> str:
    return "domain:" + str(domain_id)


def _solver_node_id(solver_id: str) -> str:
    return "solver:" + str(solver_id)


def _artifact_node_id(rel_path: str) -> str:
    return "artifact:" + _norm(rel_path)


def _command_node_id(command_id: str) -> str:
    return "command:" + str(command_id)


def _node(node_id: str, node_type: str, label: str, path: str = "", metadata: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    return {
        "node_id": str(node_id),
        "node_type": str(node_type),
        "label": str(label),
        "path": _norm(path),
        "metadata": dict(metadata or {}),
    }


def _edge(edge_type: str, from_id: str, to_id: str) -> Dict[str, str]:
    return {
        "edge_type": str(edge_type),
        "from": str(from_id),
        "to": str(to_id),
    }


def _deterministic_nodes(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("node_type", "")),
            str(item.get("node_id", "")),
            str(item.get("path", "")),
        ),
    )


def _deterministic_edges(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    unique = {
        (str(item.get("edge_type", "")), str(item.get("from", "")), str(item.get("to", ""))): item
        for item in rows
        if isinstance(item, dict)
    }
    return [unique[key] for key in sorted(unique.keys())]


def _resolve_python_import_targets(text: str, file_index: Dict[str, str]) -> List[str]:
    targets: Set[str] = set()
    for line in text.splitlines():
        match_from = IMPORT_FROM_RE.match(line)
        if match_from:
            rel = _module_to_repo_rel(match_from.group(1))
            if rel in file_index:
                targets.add(rel)
            continue
        match_import = IMPORT_RE.match(line)
        if match_import:
            modules = [token.strip() for token in str(match_import.group(1)).split(",") if token.strip()]
            for module in modules:
                rel = _module_to_repo_rel(module)
                if rel in file_index:
                    targets.add(rel)
    return sorted(targets)


def _resolve_include_targets(source_rel: str, text: str, file_index: Dict[str, str]) -> List[str]:
    source_dir = os.path.dirname(source_rel)
    targets: Set[str] = set()
    for line in text.splitlines():
        match = INCLUDE_RE.match(line)
        if not match:
            continue
        include_rel = _norm(match.group(1))
        direct = _norm(os.path.join(source_dir, include_rel)) if source_dir else include_rel
        if direct in file_index:
            targets.add(direct)
            continue
        if include_rel in file_index:
            targets.add(include_rel)
    return sorted(targets)


def _load_registry_rows(repo_root: str, rel_path: str, key: str) -> List[Dict[str, object]]:
    payload, err = _read_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
    if err or not isinstance(payload, dict):
        return []
    rows = payload.get(key)
    if not isinstance(rows, list):
        record = payload.get("record")
        if isinstance(record, dict):
            rows = record.get(key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def _collect_pack_manifests(repo_root: str) -> List[Dict[str, object]]:
    packs_root = os.path.join(repo_root, "packs")
    out: List[Dict[str, object]] = []
    if not os.path.isdir(packs_root):
        return out
    for category in sorted(os.listdir(packs_root)):
        cat_root = os.path.join(packs_root, category)
        if not os.path.isdir(cat_root):
            continue
        for pack_dir in sorted(os.listdir(cat_root)):
            manifest_path = os.path.join(cat_root, pack_dir, "pack.json")
            if not os.path.isfile(manifest_path):
                continue
            payload, err = _read_json(manifest_path)
            if err or not isinstance(payload, dict):
                continue
            pack_id = str(payload.get("pack_id", "")).strip()
            if not pack_id:
                continue
            out.append(
                {
                    "pack_id": pack_id,
                    "category": str(category),
                    "manifest_rel": _norm(os.path.relpath(manifest_path, repo_root)),
                    "dependencies": sorted(
                        set(str(item).strip() for item in (payload.get("dependencies") or []) if str(item).strip())
                    ),
                    "contributions": [dict(item) for item in (payload.get("contributions") or []) if isinstance(item, dict)],
                }
            )
    return sorted(out, key=lambda item: str(item.get("pack_id", "")))


def build_graph(repo_root: str, changed_files: Optional[List[str]] = None) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    files = sorted(set(_iter_repo_files(repo_root)))
    file_index = _build_file_index(files)

    nodes: List[Dict[str, object]] = []
    edges: List[Dict[str, str]] = []

    for rel in files:
        nodes.append(_node(_file_node_id(rel), "file", rel, rel))

    # Schema nodes and edges
    schema_names: List[str] = []
    for rel in files:
        if rel.startswith("schemas/") and rel.endswith(".schema.json"):
            schema_name = rel.split("/")[-1].replace(".schema.json", "")
            schema_names.append(schema_name)
            nodes.append(_node(_schema_node_id(schema_name), "schema", schema_name, rel))
            edges.append(_edge("references", _file_node_id(rel), _schema_node_id(schema_name)))
            edges.append(_edge("depends_on", _schema_node_id(schema_name), _file_node_id(rel)))
    schema_names = sorted(set(schema_names))

    # Registry nodes
    registry_files = [rel for rel in files if rel.startswith("data/registries/") and rel.endswith(".json")]
    for rel in sorted(registry_files):
        reg_name = rel.split("/")[-1].replace(".json", "")
        nodes.append(_node(_registry_node_id(reg_name), "registry", reg_name, rel))
        edges.append(_edge("references", _file_node_id(rel), _registry_node_id(reg_name)))

    # Pack nodes and dependency edges
    pack_rows = _collect_pack_manifests(repo_root)
    pack_ids = sorted(set(str(row.get("pack_id", "")) for row in pack_rows if str(row.get("pack_id", "")).strip()))
    for row in pack_rows:
        pack_id = str(row.get("pack_id", "")).strip()
        manifest_rel = str(row.get("manifest_rel", ""))
        if not pack_id:
            continue
        nodes.append(
            _node(
                _pack_node_id(pack_id),
                "pack",
                pack_id,
                manifest_rel,
                metadata={"category": str(row.get("category", ""))},
            )
        )
        edges.append(_edge("depends_on", _file_node_id(manifest_rel), _pack_node_id(pack_id)))
        for dep in row.get("dependencies") or []:
            dep_id = str(dep).strip()
            if not dep_id:
                continue
            edges.append(_edge("depends_on", _pack_node_id(pack_id), _pack_node_id(dep_id)))
        for contrib in row.get("contributions") or []:
            path = str(contrib.get("path", "")).strip()
            if not path:
                continue
            source_rel = _norm(
                os.path.join(os.path.dirname(manifest_rel), path).replace("\\", "/")
            )
            if source_rel in file_index:
                edges.append(_edge("generates", _pack_node_id(pack_id), _file_node_id(source_rel)))

    # Test nodes and associations
    test_rows: List[Dict[str, object]] = []
    for rel in files:
        if not rel.startswith("tools/xstack/testx/tests/test_") or not rel.endswith(".py"):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        test_id = _parse_test_id(rel, text)
        tags = _parse_test_tags(text)
        test_rows.append({"test_id": test_id, "rel_path": rel, "tags": tags, "text": text})
    for row in sorted(test_rows, key=lambda item: str(item.get("test_id", ""))):
        test_id = str(row.get("test_id", ""))
        rel = str(row.get("rel_path", ""))
        tags = list(row.get("tags") or [])
        nodes.append(_node(_test_node_id(test_id), "test", test_id, rel, metadata={"tags": tags}))
        edges.append(_edge("validates", _test_node_id(test_id), _file_node_id(rel)))
        for target_rel in _resolve_python_import_targets(str(row.get("text", "")), file_index):
            edges.append(_edge("depends_on", _test_node_id(test_id), _file_node_id(target_rel)))
        # tag-to-schema coverage links for deterministic impacted schema subseting
        if "schema" in tags:
            for schema_name in schema_names:
                edges.append(_edge("validates", _test_node_id(test_id), _schema_node_id(schema_name)))
        if "pack" in tags or "bundle" in tags:
            for pack_id in pack_ids:
                edges.append(_edge("validates", _test_node_id(test_id), _pack_node_id(pack_id)))

    # Domain + solver nodes and edges
    domain_rows = _load_registry_rows(repo_root, "data/registries/domain_registry.json", "records")
    for row in sorted(domain_rows, key=lambda item: str(item.get("domain_id", ""))):
        domain_id = str(row.get("domain_id", "")).strip()
        if not domain_id:
            continue
        nodes.append(_node(_domain_node_id(domain_id), "domain", domain_id, "data/registries/domain_registry.json"))
    solver_rows = _load_registry_rows(repo_root, "data/registries/solver_registry.json", "records")
    for row in sorted(solver_rows, key=lambda item: str(item.get("solver_id", ""))):
        solver_id = str(row.get("solver_id", "")).strip()
        if not solver_id:
            continue
        nodes.append(_node(_solver_node_id(solver_id), "solver", solver_id, "data/registries/solver_registry.json"))
        for domain_id in sorted(set(str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip())):
            edges.append(_edge("depends_on", _solver_node_id(solver_id), _domain_node_id(domain_id)))

    # Product nodes and ownership edges
    product_roots = {
        "engine": "engine/",
        "game": "game/",
        "client": "client/",
        "server": "server/",
        "launcher": "launcher/",
        "setup": "setup/",
        "tools": "tools/",
    }
    for product_id in sorted(product_roots.keys()):
        nodes.append(_node(_product_node_id(product_id), "product", product_id))
    for rel in files:
        for product_id, prefix in product_roots.items():
            if rel.startswith(prefix):
                edges.append(_edge("depends_on", _product_node_id(product_id), _file_node_id(rel)))
                break

    # Command nodes and edges
    command_rows = (
        "dev impact-graph",
        "dev impacted-tests",
        "dev impacted-build-targets",
        "dev run observer",
        "dev run galaxy",
        "dev run sol",
        "dev run earth",
        "dev audit",
        "dev verify",
        "dev profile",
    )
    for command in command_rows:
        nodes.append(_node(_command_node_id(command), "command", command, "tools/dev/dev.py"))
    edges.append(_edge("generates", _command_node_id("dev impact-graph"), _artifact_node_id("build/impact_graph.json")))
    edges.append(_edge("depends_on", _command_node_id("dev impacted-tests"), _artifact_node_id("build/impact_graph.json")))
    edges.append(_edge("depends_on", _command_node_id("dev impacted-build-targets"), _artifact_node_id("build/impact_graph.json")))

    # Artifact nodes
    artifact_rows = (
        "build/impact_graph.json",
        "build/lockfile.json",
        "build/registries/domain.registry.json",
        "build/registries/law.registry.json",
        "build/registries/experience.registry.json",
        "build/registries/lens.registry.json",
        "tools/xstack/out/fast/latest/report.json",
        "tools/xstack/out/strict/latest/report.json",
    )
    for rel in artifact_rows:
        nodes.append(_node(_artifact_node_id(rel), "artifact", rel, rel))

    # Include/import file->file edges + schema token refs
    for rel in files:
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        _, ext = os.path.splitext(rel.lower())
        if ext == ".py":
            for target_rel in _resolve_python_import_targets(text, file_index):
                edges.append(_edge("includes", _file_node_id(rel), _file_node_id(target_rel)))
        elif ext in {".c", ".cc", ".cpp", ".h", ".hh", ".hpp"}:
            for target_rel in _resolve_include_targets(rel, text, file_index):
                edges.append(_edge("includes", _file_node_id(rel), _file_node_id(target_rel)))

        lower_text = text.lower()
        for schema_name in schema_names:
            if schema_name.lower() in lower_text:
                edges.append(_edge("references", _file_node_id(rel), _schema_node_id(schema_name)))

    deterministic_nodes = _deterministic_nodes(nodes)
    deterministic_edges = _deterministic_edges(edges)
    graph_payload = {
        "schema_version": "1.0.0",
        "graph_id": "dominium.dev.impact_graph",
        "nodes": deterministic_nodes,
        "edges": deterministic_edges,
        "node_count": len(deterministic_nodes),
        "edge_count": len(deterministic_edges),
    }
    graph_payload["graph_hash"] = canonical_sha256(graph_payload)
    graph_payload["changed_files"] = sorted(set(_norm(item) for item in (changed_files or [])))
    return graph_payload


def compute_impacted_sets(graph_payload: Dict[str, object], changed_files: List[str]) -> Dict[str, object]:
    nodes = list(graph_payload.get("nodes") or [])
    edges = list(graph_payload.get("edges") or [])
    node_index: Dict[str, Dict[str, object]] = {
        str(node.get("node_id", "")): dict(node) for node in nodes if isinstance(node, dict)
    }

    reverse_adjacency: Dict[str, List[str]] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        src = str(edge.get("from", ""))
        dst = str(edge.get("to", ""))
        if not src or not dst:
            continue
        reverse_adjacency.setdefault(dst, []).append(src)
    for key in list(reverse_adjacency.keys()):
        reverse_adjacency[key] = sorted(set(reverse_adjacency[key]))

    changed_file_nodes = sorted(
        set(_file_node_id(_norm(path)) for path in changed_files if _file_node_id(_norm(path)) in node_index)
    )
    missing_changed = sorted(
        set(_norm(path) for path in changed_files if _file_node_id(_norm(path)) not in node_index)
    )

    visited: Set[str] = set(changed_file_nodes)
    queue = deque(changed_file_nodes)
    while queue:
        current = queue.popleft()
        for nxt in reverse_adjacency.get(current, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            queue.append(nxt)

    impacted_nodes = sorted(visited)
    impacted_tests: List[str] = []
    impacted_build_targets: List[str] = []
    for node_id in impacted_nodes:
        row = node_index.get(node_id) or {}
        node_type = str(row.get("node_type", ""))
        if node_type == "test":
            impacted_tests.append(str(row.get("label", "")))
        if node_type == "product":
            impacted_build_targets.append(str(row.get("label", "")))

    return {
        "result": "complete",
        "changed_file_nodes": changed_file_nodes,
        "missing_changed_files": missing_changed,
        "impacted_nodes": impacted_nodes,
        "impacted_test_ids": sorted(set(token for token in impacted_tests if token)),
        "impacted_build_targets": sorted(set(token for token in impacted_build_targets if token)),
        "complete_coverage": len(missing_changed) == 0,
    }


def build_graph_and_write(
    repo_root: str,
    changed_files: Optional[List[str]] = None,
    out_path: str = "build/impact_graph.json",
) -> Dict[str, object]:
    payload = build_graph(repo_root=repo_root, changed_files=changed_files or [])
    out_abs = os.path.join(repo_root, out_path.replace("/", os.sep))
    _ensure_dir(os.path.dirname(out_abs))
    with open(out_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")
    return {
        "result": "complete",
        "graph_path": _norm(os.path.relpath(out_abs, repo_root)),
        "graph_hash": str(payload.get("graph_hash", "")),
        "node_count": int(payload.get("node_count", 0) or 0),
        "edge_count": int(payload.get("edge_count", 0) or 0),
        "payload": payload,
    }
