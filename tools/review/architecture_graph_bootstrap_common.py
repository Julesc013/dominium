"""Deterministic Ξ-0 repository archaeology and architecture graph helpers."""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"
MODULE_DEP_GRAPH_REL = "data/architecture/module_dependency_graph.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"
INCLUDE_GRAPH_REL = "data/audit/include_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
ARCHITECTURE_SCAN_REPORT_REL = "data/audit/architecture_scan_report.json"
ARCHITECTURE_GRAPH_REPORT_REL = "docs/audit/ARCHITECTURE_GRAPH_REPORT.md"
MODULE_DISCOVERY_REPORT_REL = "docs/audit/MODULE_DISCOVERY_REPORT.md"
ARCH_GRAPH_BOOTSTRAP_REL = "docs/audit/ARCH_GRAPH_BOOTSTRAP.md"

OUTPUT_REL_PATHS = {
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    MODULE_DEP_GRAPH_REL,
    SYMBOL_INDEX_REL,
    INCLUDE_GRAPH_REL,
    BUILD_GRAPH_REL,
    ARCHITECTURE_SCAN_REPORT_REL,
    ARCHITECTURE_GRAPH_REPORT_REL,
    MODULE_DISCOVERY_REPORT_REL,
    ARCH_GRAPH_BOOTSTRAP_REL,
}

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}

SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".inl",
    ".ipp",
    ".py",
}

PYTHON_EXTENSIONS = {".py"}
C_FAMILY_EXTENSIONS = SOURCE_EXTENSIONS - PYTHON_EXTENSIONS
BUILD_FILE_NAMES = {"CMakeLists.txt", "CMakePresets.json"}
BUILD_EXTENSIONS = {".cmake"}
GENERATED_SOURCE_PREFIXES = (
    "artifacts/toolchain_runs/",
    "build/",
    "dist/",
    "out/",
    "tmp/",
)

DOMAIN_ROOT_MAP = {
    ".github": "governance",
    ".vscode": "ide",
    "app": "apps",
    "appshell": "appshell",
    "archive": "archive",
    "artifacts": "artifacts",
    "astro": "astro",
    "attic": "attic",
    "build": "build",
    "bundles": "packs",
    "chem": "chem",
    "client": "apps",
    "cmake": "cmake",
    "compat": "compat",
    "control": "control",
    "core": "core",
    "data": "data",
    "diag": "diag",
    "diegetics": "diegetics",
    "dist": "dist",
    "docs": "docs",
    "electric": "electric",
    "embodiment": "embodiment",
    "engine": "engine",
    "epistemics": "epistemics",
    "field": "field",
    "fields": "fields",
    "fluid": "fluid",
    "game": "game",
    "geo": "geo",
    "governance": "governance",
    "ide": "ide",
    "infrastructure": "infrastructure",
    "inspection": "inspection",
    "interaction": "interaction",
    "interior": "interior",
    "launcher": "apps",
    "legacy": "legacy",
    "lib": "lib",
    "libs": "lib",
    "locks": "locks",
    "logic": "logic",
    "logistics": "logistics",
    "machines": "machines",
    "materials": "materials",
    "mechanics": "mechanics",
    "meta": "meta",
    "mobility": "mobility",
    "modding": "modding",
    "models": "models",
    "net": "net",
    "out": "build",
    "packs": "packs",
    "performance": "performance",
    "physics": "physics",
    "pollution": "pollution",
    "process": "process",
    "profiles": "profiles",
    "quarantine": "quarantine",
    "reality": "reality",
    "release": "release",
    "repo": "repo",
    "runtime": "runtime",
    "safety": "safety",
    "schema": "schemas",
    "schemas": "schemas",
    "scripts": "tools",
    "security": "security",
    "server": "apps",
    "setup": "apps",
    "signals": "signals",
    "specs": "specs",
    "system": "system",
    "templates": "templates",
    "tests": "tests",
    "thermal": "thermal",
    "time": "time",
    "tmp": "build",
    "tools": "tools",
    "ui": "ui",
    "universe": "universe",
    "updates": "updates",
    "validation": "validation",
    "worldgen": "engine",
}

LANGUAGE_MAP = {
    ".bat": "batch",
    ".c": "c",
    ".cc": "c++",
    ".cmake": "cmake",
    ".cmd": "batch",
    ".cpp": "c++",
    ".cxx": "c++",
    ".h": "c-header",
    ".hh": "c++-header",
    ".hpp": "c++-header",
    ".hxx": "c++-header",
    ".in": "cmake-template",
    ".inl": "c++-inline",
    ".ipp": "c++-inline",
    ".json": "json",
    ".manifest": "manifest",
    ".md": "markdown",
    ".py": "python",
    ".schema": "schema",
    ".sh": "shell",
    ".txt": "text",
    ".toml": "toml",
    ".vcxproj": "msbuild",
}

STOPWORD_TOKENS = {
    "",
    ".",
    "apps",
    "artifacts",
    "audit",
    "build",
    "client",
    "cmake",
    "data",
    "dist",
    "docs",
    "engine",
    "game",
    "launcher",
    "lib",
    "libs",
    "schema",
    "schemas",
    "server",
    "setup",
    "src",
    "tests",
    "tools",
    "unknown",
}

BUILD_SCOPE_TOKENS = {"PRIVATE", "PUBLIC", "INTERFACE", "BEFORE", "AFTER", "FILES", "TREE", "PREFIX", "BASE_DIRS"}
EXPORT_PATTERN = re.compile(r"(?:DOMINIUM_EXPORT|__declspec\s*\(\s*dllexport\s*\)|visibility\s*\(\s*\"default\"\s*\))")
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]')
NAMESPACE_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)")
TYPE_RE = re.compile(r"^\s*(?:template\s*<[^>]+>\s*)?(class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)")
FUNCTION_RE = re.compile(
    r"^\s*(?:template\s*<[^>]+>\s*)?(?:inline\s+|static\s+|extern\s+|virtual\s+|constexpr\s+|friend\s+|typedef\s+)*"
    r"[A-Za-z_~][A-Za-z0-9_:<>\s\*&,\[\]]*?\s+([A-Za-z_~][A-Za-z0-9_:]*)\s*\(([^;{}]*)\)\s*(?:const)?\s*(?:noexcept)?\s*(?:=\s*0)?\s*(?:\{|;)"
)
TEMPLATE_RE = re.compile(r"^\s*template\s*<(.+)>")
COMMAND_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _id_token(value: object) -> str:
    token = _token(value).strip(".").lower().replace("-", "_").replace(" ", "_")
    return token


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _tracked_repo_files(repo_root: str) -> list[str]:
    root = _repo_root(repo_root)
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        proc = None
    rows: list[str] = []
    if proc and int(proc.returncode) == 0:
        for line in str(proc.stdout or "").splitlines():
            rel_path = _norm_rel(line)
            if not rel_path or rel_path in OUTPUT_REL_PATHS:
                continue
            if os.path.isfile(_repo_abs(root, rel_path)):
                rows.append(rel_path)
        if rows:
            return sorted(set(rows))
    rel_paths: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = _norm_rel(os.path.relpath(dirpath, root))
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIR_NAMES)
        for name in sorted(filenames):
            rel_path = _norm_rel(os.path.join(rel_dir, name))
            if rel_path in OUTPUT_REL_PATHS:
                continue
            rel_paths.append(rel_path)
    return sorted(set(rel_paths))


def _repo_directories(repo_root: str, tracked_files: Sequence[str]) -> list[str]:
    _ = _repo_root(repo_root)
    rows = {"."}
    for rel_path in sorted(tracked_files):
        directory = _module_root_for_path(rel_path)
        while directory not in {"", "."}:
            rows.add(directory)
            directory = _module_root_for_path(directory)
        rows.add(".")
    return sorted(rows)


def _top_level(path: str) -> str:
    rel_path = _norm_rel(path)
    if rel_path in {"", "."}:
        return ""
    return rel_path.split("/", 1)[0]


def _default_domain(path: str) -> str:
    top_level = _top_level(path)
    if not top_level:
        return "unknown"
    if top_level in DOMAIN_ROOT_MAP:
        return DOMAIN_ROOT_MAP[top_level]
    if "/" not in _norm_rel(path) and os.path.splitext(top_level)[1].lower():
        return "repo"
    token = _id_token(top_level)
    return token or "unknown"


def classify_domain(path: str) -> str:
    return _default_domain(path)


def _language_id(rel_path: str) -> str:
    base = os.path.basename(rel_path)
    if base == "CMakeLists.txt":
        return "cmake"
    return LANGUAGE_MAP.get(os.path.splitext(rel_path)[1].lower(), "unknown")


def _is_source_path(rel_path: str) -> bool:
    rel_norm = _norm_rel(rel_path)
    if rel_norm in OUTPUT_REL_PATHS:
        return False
    if rel_norm.startswith(GENERATED_SOURCE_PREFIXES):
        return False
    return os.path.splitext(rel_norm)[1].lower() in SOURCE_EXTENSIONS


def _is_build_path(rel_path: str) -> bool:
    rel_norm = _norm_rel(rel_path)
    if rel_norm in OUTPUT_REL_PATHS:
        return False
    if os.path.basename(rel_norm) in BUILD_FILE_NAMES:
        return True
    return os.path.splitext(rel_norm)[1].lower() in BUILD_EXTENSIONS and not rel_norm.startswith(("build/", "out/", "tmp/"))


def _module_root_for_path(rel_path: str) -> str:
    rel_norm = _norm_rel(rel_path)
    directory = _norm_rel(os.path.dirname(rel_norm))
    return directory or "."


def _module_id(module_root: str, domain: str) -> str:
    root = _norm_rel(module_root)
    if root in {"", "."}:
        return "unknown.root"
    parts = [part for part in root.split("/") if part]
    normalized_parts = [_id_token(part) for part in parts if _id_token(part)]
    if domain == "unknown":
        return ".".join(["unknown"] + normalized_parts)
    if parts and _default_domain(parts[0]) == domain:
        if parts[0] == domain:
            return ".".join([domain] + [_id_token(part) for part in parts[1:] if _id_token(part)])
        if parts[0] == "worldgen" and domain == "engine":
            return ".".join(normalized_parts)
        return ".".join([domain] + normalized_parts)
    return ".".join([domain] + normalized_parts)


def _confidence(domain: str, module_root: str) -> float:
    if module_root in {"", "."}:
        return 0.4
    return 0.92 if domain != "unknown" else 0.55


def _python_module_name(rel_path: str) -> str:
    rel_norm = _norm_rel(rel_path)
    if not rel_norm.endswith(".py"):
        return ""
    if os.path.basename(rel_norm) == "__init__.py":
        return _norm_rel(os.path.dirname(rel_norm)).replace("/", ".").strip(".")
    return rel_norm[:-3].replace("/", ".")


def _python_module_maps(py_paths: Sequence[str]) -> tuple[dict[str, str], dict[str, list[str]]]:
    exact: dict[str, str] = {}
    suffixes: defaultdict[str, list[str]] = defaultdict(list)
    for rel_path in sorted(py_paths):
        module_name = _python_module_name(rel_path)
        if not module_name:
            continue
        exact[module_name] = rel_path
        parts = module_name.split(".")
        for index in range(len(parts)):
            suffix = ".".join(parts[index:])
            suffixes[suffix].append(rel_path)
    return exact, {key: sorted(value) for key, value in suffixes.items()}


def _python_package_parts(rel_path: str) -> list[str]:
    module_name = _python_module_name(rel_path)
    if not module_name:
        return []
    parts = module_name.split(".")
    if os.path.basename(rel_path) == "__init__.py":
        return parts
    return parts[:-1]


def _resolve_python_import(
    current_rel: str,
    module_token: str,
    imported_name: str,
    level: int,
    exact_map: Mapping[str, str],
    suffix_map: Mapping[str, Sequence[str]],
) -> str:
    current_package = _python_package_parts(current_rel)
    target_modules: list[str] = []
    if level > 0:
        base = current_package[: max(0, len(current_package) - (level - 1))]
        suffix = module_token.split(".") if module_token else []
        candidate = ".".join(base + suffix).strip(".")
        if candidate:
            target_modules.append(candidate)
        elif base:
            target_modules.append(".".join(base))
    elif module_token:
        target_modules.append(module_token)
    if module_token and module_token not in target_modules:
        target_modules.append(module_token)
    resolved_candidates: list[str] = []
    for target in target_modules:
        rel_path = _token(exact_map.get(target))
        if rel_path:
            resolved_candidates.append(rel_path)
            if imported_name:
                submodule = _token(exact_map.get("{}.{}".format(target, imported_name)))
                if submodule:
                    resolved_candidates.append(submodule)
        for suffix_match in list(suffix_map.get(target) or []):
            resolved_candidates.append(_norm_rel(suffix_match))
    if not resolved_candidates and imported_name:
        combined = "{}.{}".format(module_token, imported_name).strip(".")
        rel_path = _token(exact_map.get(combined))
        if rel_path:
            resolved_candidates.append(rel_path)
        for suffix_match in list(suffix_map.get(combined) or []):
            resolved_candidates.append(_norm_rel(suffix_match))
    resolved_candidates = sorted(set(path for path in resolved_candidates if path))
    if resolved_candidates:
        return resolved_candidates[0]
    unresolved = "{}{}".format("." * int(level or 0), module_token or "")
    if imported_name:
        unresolved = "{}:{}".format(unresolved or ".", imported_name)
    return "module:{}".format(unresolved.strip(":"))


class _PythonSymbolVisitor(ast.NodeVisitor):
    def __init__(self, rel_path: str, module_id: str):
        self.rel_path = _norm_rel(rel_path)
        self.module_id = _token(module_id)
        self.symbols: list[dict] = []
        self.qual_stack: list[str] = []

    def _push_symbol(self, *, symbol_name: str, symbol_kind: str, line_number: int, signature_payload: Mapping[str, object]) -> None:
        self.symbols.append(
            {
                "symbol_name": _token(symbol_name),
                "symbol_kind": _token(symbol_kind),
                "file_path": self.rel_path,
                "module_id": self.module_id,
                "line_number": int(line_number or 1),
                "signature_hash": canonical_sha256(signature_payload),
            }
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        qualname = ".".join(self.qual_stack + [node.name]) if self.qual_stack else node.name
        self._push_symbol(
            symbol_name=qualname,
            symbol_kind="class",
            line_number=int(getattr(node, "lineno", 1) or 1),
            signature_payload={
                "kind": "class",
                "name": qualname,
                "bases": [ast.unparse(base) if hasattr(ast, "unparse") else getattr(base, "id", "") for base in list(node.bases or [])],
            },
        )
        self.qual_stack.append(node.name)
        self.generic_visit(node)
        self.qual_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_function(node, "function")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_function(node, "async_function")

    def _visit_function(self, node: ast.AST, symbol_kind: str) -> None:
        name = getattr(node, "name", "")
        qualname = ".".join(self.qual_stack + [str(name)]) if self.qual_stack else str(name)
        args = []
        node_args = getattr(node, "args", None)
        if node_args is not None:
            args.extend(getattr(arg, "arg", "") for arg in list(getattr(node_args, "posonlyargs", []) or []))
            args.extend(getattr(arg, "arg", "") for arg in list(getattr(node_args, "args", []) or []))
            if getattr(node_args, "vararg", None) is not None:
                args.append("*{}".format(getattr(node_args.vararg, "arg", "")))
            args.extend(getattr(arg, "arg", "") for arg in list(getattr(node_args, "kwonlyargs", []) or []))
            if getattr(node_args, "kwarg", None) is not None:
                args.append("**{}".format(getattr(node_args.kwarg, "arg", "")))
        self._push_symbol(
            symbol_name=qualname,
            symbol_kind=symbol_kind,
            line_number=int(getattr(node, "lineno", 1) or 1),
            signature_payload={"kind": symbol_kind, "name": qualname, "args": args},
        )
        self.qual_stack.append(str(name))
        self.generic_visit(node)
        self.qual_stack.pop()


def _extract_python_artifacts(
    rel_path: str,
    text: str,
    module_id: str,
    exact_map: Mapping[str, str],
    suffix_map: Mapping[str, Sequence[str]],
) -> tuple[list[dict], list[dict]]:
    symbols: list[dict] = []
    edges: list[dict] = []
    try:
        tree = ast.parse(text, filename=rel_path)
    except SyntaxError:
        return symbols, edges
    visitor = _PythonSymbolVisitor(rel_path, module_id)
    visitor.visit(tree)
    symbols.extend(visitor.symbols)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in list(node.names or []):
                edges.append(
                    {
                        "from": _norm_rel(rel_path),
                        "to": _resolve_python_import(rel_path, _token(alias.name), "", 0, exact_map, suffix_map),
                        "dependency_kind": "python_import",
                        "raw": _token(alias.name),
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module_token = _token(getattr(node, "module", ""))
            level = int(getattr(node, "level", 0) or 0)
            for alias in list(node.names or []):
                edges.append(
                    {
                        "from": _norm_rel(rel_path),
                        "to": _resolve_python_import(rel_path, module_token, _token(alias.name), level, exact_map, suffix_map),
                        "dependency_kind": "python_from_import",
                        "raw": "{}{}".format("." * level, module_token) or ".",
                    }
                )
        elif isinstance(node, ast.Assign):
            for target in list(node.targets or []):
                if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                    for item in list(node.value.elts or []):
                        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                            continue
                        name = _token(item.value)
                        symbols.append(
                            {
                                "symbol_name": name,
                                "symbol_kind": "exported_symbol",
                                "file_path": _norm_rel(rel_path),
                                "module_id": _token(module_id),
                                "line_number": int(getattr(node, "lineno", 1) or 1),
                                "signature_hash": canonical_sha256({"kind": "exported_symbol", "name": name}),
                            }
                        )
    return symbols, edges


def _resolve_include(rel_path: str, include_token: str, all_paths: set[str], basename_index: Mapping[str, Sequence[str]]) -> str:
    current_dir = _module_root_for_path(rel_path)
    candidate = _norm_rel(os.path.join(current_dir, include_token))
    if candidate in all_paths:
        return candidate
    if _norm_rel(include_token) in all_paths:
        return _norm_rel(include_token)
    basename = os.path.basename(include_token)
    candidates = [path for path in list(basename_index.get(basename) or []) if path.endswith(include_token)]
    if not candidates:
        candidates = list(basename_index.get(basename) or [])
    candidates = sorted(set(_norm_rel(path) for path in candidates))
    if candidates:
        return candidates[0]
    return "external:{}".format(_token(include_token))


def _extract_c_artifacts(rel_path: str, text: str, module_id: str, all_paths: set[str], basename_index: Mapping[str, Sequence[str]]) -> tuple[list[dict], list[dict]]:
    symbols: list[dict] = []
    edges: list[dict] = []
    template_line = 0
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        include_match = INCLUDE_RE.match(raw_line)
        if include_match:
            include_token = _token(include_match.group(2))
            edges.append(
                {
                    "from": _norm_rel(rel_path),
                    "to": _resolve_include(rel_path, include_token, all_paths, basename_index),
                    "dependency_kind": "include",
                    "raw": include_token,
                }
            )
        template_match = TEMPLATE_RE.match(raw_line)
        if template_match:
            template_line = line_number
            symbols.append(
                {
                    "symbol_name": "template@{}".format(line_number),
                    "symbol_kind": "template",
                    "file_path": _norm_rel(rel_path),
                    "module_id": _token(module_id),
                    "line_number": line_number,
                    "signature_hash": canonical_sha256({"kind": "template", "line": raw_line.strip()}),
                }
            )
        namespace_match = NAMESPACE_RE.match(raw_line)
        if namespace_match:
            name = _token(namespace_match.group(1))
            symbols.append(
                {
                    "symbol_name": name,
                    "symbol_kind": "namespace",
                    "file_path": _norm_rel(rel_path),
                    "module_id": _token(module_id),
                    "line_number": line_number,
                    "signature_hash": canonical_sha256({"kind": "namespace", "name": name}),
                }
            )
        type_match = TYPE_RE.match(raw_line)
        if type_match:
            kind = _token(type_match.group(1))
            name = _token(type_match.group(2))
            symbols.append(
                {
                    "symbol_name": name,
                    "symbol_kind": kind,
                    "file_path": _norm_rel(rel_path),
                    "module_id": _token(module_id),
                    "line_number": line_number,
                    "signature_hash": canonical_sha256({"kind": kind, "name": name, "template_line": template_line}),
                }
            )
        func_match = FUNCTION_RE.match(raw_line)
        if func_match:
            name = _token(func_match.group(1))
            params = _token(func_match.group(2))
            symbols.append(
                {
                    "symbol_name": name,
                    "symbol_kind": "function",
                    "file_path": _norm_rel(rel_path),
                    "module_id": _token(module_id),
                    "line_number": line_number,
                    "signature_hash": canonical_sha256({"kind": "function", "name": name, "params": params, "template_line": template_line}),
                }
            )
            if EXPORT_PATTERN.search(raw_line):
                symbols.append(
                    {
                        "symbol_name": name,
                        "symbol_kind": "exported_symbol",
                        "file_path": _norm_rel(rel_path),
                        "module_id": _token(module_id),
                        "line_number": line_number,
                        "signature_hash": canonical_sha256({"kind": "exported_symbol", "name": name, "params": params}),
                    }
                )
        if raw_line.strip().endswith(";") or raw_line.strip().endswith("{"):
            template_line = 0
    return symbols, edges


def _strip_cmake_comments(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        quote = False
        buffer: list[str] = []
        for char in raw_line:
            if char == '"':
                quote = not quote
            if char == "#" and not quote:
                break
            buffer.append(char)
        lines.append("".join(buffer))
    return "\n".join(lines)


def _cmake_commands(text: str) -> list[tuple[str, str]]:
    stripped = _strip_cmake_comments(text)
    commands: list[tuple[str, str]] = []
    index = 0
    while index < len(stripped):
        match = COMMAND_RE.search(stripped, index)
        if not match:
            break
        command = _token(match.group(1)).lower()
        pos = match.end() - 1
        depth = 0
        quote = False
        start = pos + 1
        end = start
        while end < len(stripped):
            char = stripped[end]
            if char == '"':
                quote = not quote
            elif not quote and char == "(":
                depth += 1
            elif not quote and char == ")":
                if depth == 0:
                    break
                depth -= 1
            end += 1
        commands.append((command, stripped[start:end]))
        index = end + 1
    return commands


def _cmake_tokens(text: str) -> list[str]:
    rows = re.findall(r'"[^"]*"|\$<[^>]+>|[^\s"]+', text.replace("\n", " "))
    out: list[str] = []
    for row in rows:
        token = row[1:-1] if row.startswith('"') and row.endswith('"') else row
        if token:
            out.append(token)
    return out


def _resolve_cmake_source(token: str, cmake_rel: str, all_paths: set[str], basename_index: Mapping[str, Sequence[str]]) -> str:
    value = _token(token)
    if not value or "$" in value or value.startswith("$<") or value.startswith("${"):
        return ""
    if value in BUILD_SCOPE_TOKENS:
        return ""
    current_dir = _module_root_for_path(cmake_rel)
    candidate = _norm_rel(os.path.join(current_dir, value))
    if candidate in all_paths:
        return candidate
    if _norm_rel(value) in all_paths:
        return _norm_rel(value)
    basename = os.path.basename(value)
    candidates = [path for path in list(basename_index.get(basename) or []) if path.endswith(value)]
    if not candidates:
        candidates = list(basename_index.get(basename) or [])
    candidates = sorted(set(_norm_rel(path) for path in candidates))
    return candidates[0] if candidates else ""


def _infer_product_id(target_id: str, sources: Sequence[str]) -> str:
    token = _token(target_id).lower()
    for product in ("client", "engine", "game", "launcher", "server", "setup"):
        if token == product or token.endswith("_{}".format(product)) or token.startswith("{}_".format(product)):
            return product
    source_blob = " ".join(_norm_rel(path).lower() for path in sources)
    for product in ("client", "engine", "game", "launcher", "server", "setup"):
        if "/{}/".format(product) in "/{}/".format(source_blob):
            return product
    if "tool" in token:
        return "tools"
    return ""


def _tarjan_cycles(graph: Mapping[str, Sequence[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for dep in list(graph.get(node) or []):
            if dep not in indices:
                strongconnect(dep)
                lowlinks[node] = min(lowlinks[node], lowlinks[dep])
            elif dep in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[dep])
        if lowlinks[node] != indices[node]:
            return
        component: list[str] = []
        while stack:
            top = stack.pop()
            on_stack.discard(top)
            component.append(top)
            if top == node:
                break
        component = sorted(component)
        if len(component) > 1:
            components.append(component)

    for node in sorted(graph):
        if node not in indices:
            strongconnect(node)
    return sorted(components)


def build_architecture_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    tracked_files = _tracked_repo_files(root)
    repo_dirs = _repo_directories(root, tracked_files)
    tracked_set = set(tracked_files)
    basename_index: defaultdict[str, list[str]] = defaultdict(list)
    for rel_path in tracked_files:
        basename_index[os.path.basename(rel_path)].append(rel_path)
    basename_map = {key: sorted(value) for key, value in basename_index.items()}

    directory_file_count: defaultdict[str, int] = defaultdict(int)
    for rel_path in tracked_files:
        directory_file_count[_module_root_for_path(rel_path)] += 1

    languages = Counter(_language_id(path) for path in tracked_files)
    language_rows = [{"language_id": key, "file_count": int(value)} for key, value in sorted(languages.items())]
    dir_rows = [
        {
            "path": _norm_rel(rel_dir),
            "domain": classify_domain(rel_dir),
            "file_count": int(directory_file_count.get(_norm_rel(rel_dir), 0)),
        }
        for rel_dir in repo_dirs
    ]

    module_files: defaultdict[str, list[str]] = defaultdict(list)
    for rel_path in tracked_files:
        module_files[_module_root_for_path(rel_path)].append(rel_path)

    module_rows: list[dict] = []
    file_to_module: dict[str, str] = {}
    for module_root in sorted(module_files):
        owned_files = sorted(module_files[module_root])
        domain = classify_domain(module_root)
        module_id = _module_id(module_root, domain)
        file_languages = Counter(_language_id(path) for path in owned_files)
        row = {
            "module_id": module_id,
            "module_root": _norm_rel(module_root),
            "domain": domain,
            "stability_class": "unknown",
            "confidence": _confidence(domain, module_root),
            "owned_files": owned_files,
            "file_count": len(owned_files),
            "languages": [{"language_id": key, "file_count": int(value)} for key, value in sorted(file_languages.items())],
        }
        module_rows.append(row)
        for rel_path in owned_files:
            file_to_module[rel_path] = module_id
    module_rows = sorted(module_rows, key=lambda item: (str(item.get("module_id", "")), str(item.get("module_root", ""))))

    source_paths = [path for path in tracked_files if _is_source_path(path)]
    py_paths = [path for path in source_paths if os.path.splitext(path)[1].lower() in PYTHON_EXTENSIONS]
    py_exact_map, py_suffix_map = _python_module_maps(py_paths)

    symbol_rows: list[dict] = []
    include_edges: list[dict] = []
    for rel_path in sorted(source_paths):
        text = _read_text(_repo_abs(root, rel_path))
        module_id = _token(file_to_module.get(rel_path))
        ext = os.path.splitext(rel_path)[1].lower()
        if ext in PYTHON_EXTENSIONS:
            symbols, edges = _extract_python_artifacts(rel_path, text, module_id, py_exact_map, py_suffix_map)
        else:
            symbols, edges = _extract_c_artifacts(rel_path, text, module_id, tracked_set, basename_map)
        symbol_rows.extend(symbols)
        include_edges.extend(edges)
    symbol_rows = sorted(
        (
            {
                "symbol_name": _token(row.get("symbol_name")),
                "symbol_kind": _token(row.get("symbol_kind")),
                "file_path": _norm_rel(row.get("file_path")),
                "module_id": _token(row.get("module_id")),
                "signature_hash": _token(row.get("signature_hash")),
                "line_number": int(row.get("line_number", 1) or 1),
            }
            for row in symbol_rows
            if _token(row.get("symbol_name"))
        ),
        key=lambda item: (str(item.get("symbol_name", "")), str(item.get("file_path", "")), int(item.get("line_number", 1))),
    )
    include_edges = sorted(
        (
            {
                "from": _norm_rel(row.get("from")),
                "to": _token(row.get("to")),
                "dependency_kind": _token(row.get("dependency_kind")) or "include",
                "raw": _token(row.get("raw")),
            }
            for row in include_edges
            if _token(row.get("from")) and _token(row.get("to"))
        ),
        key=lambda item: (str(item.get("from", "")), str(item.get("to", "")), str(item.get("dependency_kind", "")), str(item.get("raw", ""))),
    )

    build_files = [path for path in tracked_files if _is_build_path(path)]
    targets: dict[str, dict] = {}
    source_groups: list[dict] = []
    presets: list[dict] = []
    for rel_path in sorted(build_files):
        text = _read_text(_repo_abs(root, rel_path))
        if os.path.basename(rel_path) == "CMakePresets.json":
            try:
                payload = json.loads(text)
            except ValueError:
                payload = {}
            for row in list(dict(payload or {}).get("configurePresets") or []):
                item = dict(row or {})
                presets.append(
                    {
                        "preset_name": _token(item.get("name")),
                        "generator": _token(item.get("generator")),
                        "binary_dir": _token(item.get("binaryDir")),
                        "cache_variables": sorted(_token(key) for key in dict(item.get("cacheVariables") or {})),
                        "declared_in": _norm_rel(rel_path),
                    }
                )
            continue
        for command, args_text in _cmake_commands(text):
            tokens = _cmake_tokens(args_text)
            if not tokens:
                continue
            if command in {"add_library", "add_executable"}:
                target_id = _token(tokens[0])
                target = targets.setdefault(
                    target_id,
                    {
                        "target_id": target_id,
                        "target_kind": "library" if command == "add_library" else "executable",
                        "declared_in": _norm_rel(rel_path),
                        "sources": [],
                        "source_groups": [],
                        "compiler_flags": [],
                        "product_id": "",
                    },
                )
                for token in tokens[1:]:
                    source_path = _resolve_cmake_source(token, rel_path, tracked_set, basename_map)
                    if source_path:
                        target["sources"].append(source_path)
            elif command == "target_sources":
                target_id = _token(tokens[0])
                target = targets.setdefault(
                    target_id,
                    {
                        "target_id": target_id,
                        "target_kind": "unknown",
                        "declared_in": _norm_rel(rel_path),
                        "sources": [],
                        "source_groups": [],
                        "compiler_flags": [],
                        "product_id": "",
                    },
                )
                for token in tokens[1:]:
                    source_path = _resolve_cmake_source(token, rel_path, tracked_set, basename_map)
                    if source_path:
                        target["sources"].append(source_path)
            elif command == "target_compile_options":
                target_id = _token(tokens[0])
                target = targets.setdefault(
                    target_id,
                    {
                        "target_id": target_id,
                        "target_kind": "unknown",
                        "declared_in": _norm_rel(rel_path),
                        "sources": [],
                        "source_groups": [],
                        "compiler_flags": [],
                        "product_id": "",
                    },
                )
                for token in tokens[1:]:
                    if token in BUILD_SCOPE_TOKENS or "$" in token:
                        continue
                    target["compiler_flags"].append(_token(token))
            elif command == "source_group":
                files_index = [index for index, token in enumerate(tokens) if token == "FILES"]
                file_tokens = tokens[files_index[0] + 1 :] if files_index else []
                files = sorted(
                    {
                        resolved
                        for token in file_tokens
                        for resolved in [_resolve_cmake_source(token, rel_path, tracked_set, basename_map)]
                        if resolved
                    }
                )
                source_groups.append({"group_id": _token(tokens[0]), "declared_in": _norm_rel(rel_path), "files": files})
    build_target_rows: list[dict] = []
    file_to_targets: defaultdict[str, set[str]] = defaultdict(set)
    for target_id in sorted(targets):
        row = dict(targets[target_id])
        row["sources"] = sorted(set(_norm_rel(path) for path in list(row.get("sources") or []) if _token(path)))
        row["compiler_flags"] = sorted(set(_token(flag) for flag in list(row.get("compiler_flags") or []) if _token(flag)))
        row["source_groups"] = sorted(
            {
                _token(group.get("group_id"))
                for group in source_groups
                if set(row["sources"]) & set(list(group.get("files") or []))
            }
        )
        row["product_id"] = _infer_product_id(_token(row.get("target_id")), row["sources"])
        for source in row["sources"]:
            file_to_targets[source].add(_token(row.get("target_id")))
        build_target_rows.append(row)
    build_target_rows = sorted(build_target_rows, key=lambda item: str(item.get("target_id", "")))
    source_groups = sorted(source_groups, key=lambda item: (str(item.get("group_id", "")), str(item.get("declared_in", ""))))
    presets = sorted(presets, key=lambda item: str(item.get("preset_name", "")))

    module_edge_pairs: defaultdict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    module_graph: defaultdict[str, set[str]] = defaultdict(set)
    for edge in include_edges:
        from_path = _token(edge.get("from"))
        to_path = _token(edge.get("to"))
        if not from_path or not to_path or to_path.startswith(("external:", "module:")):
            continue
        from_module = _token(file_to_module.get(from_path))
        to_module = _token(file_to_module.get(to_path))
        if not from_module or not to_module or from_module == to_module:
            continue
        module_graph[from_module].add(to_module)
        module_edge_pairs[(from_module, to_module)].append((from_path, to_path))
    for module_row in module_rows:
        module_graph.setdefault(_token(module_row.get("module_id")), set())
    module_dep_rows: list[dict] = []
    for (from_module, to_module), via_rows in sorted(module_edge_pairs.items()):
        related_targets = sorted(
            {
                target_id
                for file_path in {left for left, _right in via_rows} | {right for _left, right in via_rows}
                for target_id in list(file_to_targets.get(file_path) or set())
            }
        )
        module_dep_rows.append(
            {
                "from_module_id": from_module,
                "to_module_id": to_module,
                "edge_count": len(via_rows),
                "via_files": [{"from": left, "to": right} for left, right in sorted(set(via_rows))],
                "related_build_targets": related_targets,
            }
        )
    module_dep_rows = sorted(module_dep_rows, key=lambda item: (str(item.get("from_module_id", "")), str(item.get("to_module_id", ""))))
    cycles = _tarjan_cycles({key: sorted(value) for key, value in module_graph.items()})

    symbols_by_module: defaultdict[str, list[str]] = defaultdict(list)
    symbols_by_name: defaultdict[str, list[dict]] = defaultdict(list)
    for row in symbol_rows:
        symbols_by_module[_token(row.get("module_id"))].append(_token(row.get("symbol_name")))
        symbols_by_name[_token(row.get("symbol_name"))].append(row)

    duplicate_symbols = []
    multi_module_symbols = []
    for symbol_name in sorted(symbols_by_name):
        rows = list(symbols_by_name[symbol_name])
        file_paths = sorted({_token(row.get("file_path")) for row in rows if _token(row.get("file_path"))})
        module_ids = sorted({_token(row.get("module_id")) for row in rows if _token(row.get("module_id"))})
        if len(file_paths) > 1:
            duplicate_symbols.append({"symbol_name": symbol_name, "file_paths": file_paths, "module_ids": module_ids, "definition_count": len(file_paths)})
        if len(module_ids) > 1:
            multi_module_symbols.append({"symbol_name": symbol_name, "module_ids": module_ids, "file_paths": file_paths})
    unknown_modules = [
        {"module_id": _token(row.get("module_id")), "module_root": _token(row.get("module_root")), "confidence": float(row.get("confidence", 0.0) or 0.0)}
        for row in module_rows
        if _token(row.get("domain")) == "unknown"
    ]
    src_directories = sorted({rel_dir for rel_dir in repo_dirs if any(segment == "src" for segment in _norm_rel(rel_dir).split("/"))})

    concepts: defaultdict[str, set[str]] = defaultdict(set)
    concept_symbols: defaultdict[str, set[str]] = defaultdict(set)
    for row in module_rows:
        module_id = _token(row.get("module_id"))
        root_parts = [part for part in _token(row.get("module_root")).split("/") if part]
        concept = ""
        for token in root_parts:
            token_norm = _id_token(token)
            if token_norm not in STOPWORD_TOKENS:
                concept = token_norm
                break
        if not concept:
            concept = _id_token(_top_level(_token(row.get("module_root")))) or "root"
        concepts[concept].add(module_id)
        for symbol_name in list(symbols_by_module.get(module_id) or []):
            concept_symbols[concept].add(symbol_name)
    concept_rows = [{"concept_id": concept_id, "modules": sorted(modules), "symbols": sorted(concept_symbols.get(concept_id) or [])} for concept_id, modules in sorted(concepts.items())]

    dependents: defaultdict[str, set[str]] = defaultdict(set)
    for from_module, targets_set in module_graph.items():
        for to_module in list(targets_set or []):
            dependents[to_module].add(from_module)

    architecture_module_rows = []
    for row in module_rows:
        module_id = _token(row.get("module_id"))
        architecture_module_rows.append(
            {
                "module_id": module_id,
                "module_root": _token(row.get("module_root")),
                "domain": _token(row.get("domain")),
                "stability_class": _token(row.get("stability_class")),
                "confidence": float(row.get("confidence", 0.0) or 0.0),
                "owned_files": list(row.get("owned_files") or []),
                "symbols": sorted(set(symbols_by_module.get(module_id) or [])),
                "dependencies": sorted(module_graph.get(module_id) or []),
                "dependents": sorted(dependents.get(module_id) or []),
                "build_targets": sorted({target_id for file_path in list(row.get("owned_files") or []) for target_id in list(file_to_targets.get(file_path) or set())}),
            }
        )

    module_registry = {
        "report_id": "architecture.module_registry.v1",
        "directory_count": len(repo_dirs),
        "file_count": len(tracked_files),
        "languages": language_rows,
        "directories": dir_rows,
        "modules": module_rows,
        "deterministic_fingerprint": "",
    }
    module_registry["deterministic_fingerprint"] = canonical_sha256(dict(module_registry, deterministic_fingerprint=""))

    symbol_index = {
        "report_id": "architecture.symbol_index.v1",
        "symbol_count": len(symbol_rows),
        "symbols": symbol_rows,
        "deterministic_fingerprint": "",
    }
    symbol_index["deterministic_fingerprint"] = canonical_sha256(dict(symbol_index, deterministic_fingerprint=""))

    include_graph = {
        "report_id": "architecture.include_graph.v1",
        "edge_count": len(include_edges),
        "edges": include_edges,
        "deterministic_fingerprint": "",
    }
    include_graph["deterministic_fingerprint"] = canonical_sha256(dict(include_graph, deterministic_fingerprint=""))

    build_graph = {
        "report_id": "architecture.build_graph.v1",
        "build_files_scanned": sorted(build_files),
        "targets": build_target_rows,
        "source_groups": source_groups,
        "presets": presets,
        "deterministic_fingerprint": "",
    }
    build_graph["deterministic_fingerprint"] = canonical_sha256(dict(build_graph, deterministic_fingerprint=""))

    module_dependency_graph = {
        "report_id": "architecture.module_dependency_graph.v1",
        "edge_count": len(module_dep_rows),
        "edges": module_dep_rows,
        "circular_dependencies": [{"cycle": cycle} for cycle in cycles],
        "deterministic_fingerprint": "",
    }
    module_dependency_graph["deterministic_fingerprint"] = canonical_sha256(dict(module_dependency_graph, deterministic_fingerprint=""))

    architecture_graph = {
        "report_id": "architecture.graph.v1",
        "concepts": concept_rows,
        "modules": architecture_module_rows,
        "deterministic_fingerprint": "",
    }
    architecture_graph["deterministic_fingerprint"] = canonical_sha256(dict(architecture_graph, deterministic_fingerprint=""))

    architecture_scan_report = {
        "report_id": "architecture.scan_report.v1",
        "repository": {
            "directory_count": len(repo_dirs),
            "file_count": len(tracked_files),
            "source_file_count": len(source_paths),
            "build_file_count": len(build_files),
            "languages": language_rows,
        },
        "duplicate_symbol_definitions": duplicate_symbols,
        "modules_outside_expected_domain": unknown_modules,
        "directories_named_src": [{"path": row, "domain": classify_domain(row)} for row in src_directories],
        "circular_dependencies": [{"cycle": cycle} for cycle in cycles],
        "symbols_in_multiple_modules": multi_module_symbols,
        "concept_candidates": [{"concept_id": row["concept_id"], "module_count": len(row["modules"])} for row in concept_rows],
        "deterministic_fingerprint": "",
    }
    architecture_scan_report["deterministic_fingerprint"] = canonical_sha256(dict(architecture_scan_report, deterministic_fingerprint=""))

    return {
        "architecture_graph": architecture_graph,
        "module_registry": module_registry,
        "module_dependency_graph": module_dependency_graph,
        "symbol_index": symbol_index,
        "include_graph": include_graph,
        "build_graph": build_graph,
        "architecture_scan_report": architecture_scan_report,
    }


def render_architecture_graph_report(snapshot: Mapping[str, object]) -> str:
    report = dict(snapshot.get("architecture_scan_report") or {})
    architecture_graph = dict(snapshot.get("architecture_graph") or {})
    duplicate_rows = list(report.get("duplicate_symbol_definitions") or [])
    unknown_rows = list(report.get("modules_outside_expected_domain") or [])
    cycle_rows = list(report.get("circular_dependencies") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-26",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-1 architectural convergence plan",
        "",
        "# Architecture Graph Report",
        "",
        "- concept_count: `{}`".format(len(list(architecture_graph.get("concepts") or []))),
        "- module_count: `{}`".format(len(list(architecture_graph.get("modules") or []))),
        "- duplicate_symbol_signal_count: `{}`".format(len(duplicate_rows)),
        "- unknown_domain_module_count: `{}`".format(len(unknown_rows)),
        "- circular_dependency_count: `{}`".format(len(cycle_rows)),
        "",
        "## Duplicate Signals",
        "",
    ]
    if not duplicate_rows:
        lines.append("- none")
    else:
        for row in duplicate_rows[:25]:
            item = dict(row or {})
            lines.append("- `{}` -> {}".format(_token(item.get("symbol_name")), ", ".join(list(item.get("file_paths") or [])[:4])))
    lines.extend(["", "## Unknown Domains", ""])
    if not unknown_rows:
        lines.append("- none")
    else:
        for row in unknown_rows[:25]:
            item = dict(row or {})
            lines.append("- `{}` :: `{}`".format(_token(item.get("module_id")), _token(item.get("module_root"))))
    lines.extend(["", "## Circular Dependencies", ""])
    if not cycle_rows:
        lines.append("- none")
    else:
        for row in cycle_rows:
            lines.append("- {}".format(" -> ".join(list(dict(row or {}).get("cycle") or []))))
    lines.append("")
    return "\n".join(lines)


def render_module_discovery_report(snapshot: Mapping[str, object]) -> str:
    registry = dict(snapshot.get("module_registry") or {})
    modules = list(registry.get("modules") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-26",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-1 module-boundary convergence planning",
        "",
        "# Module Discovery Report",
        "",
        "- directory_count: `{}`".format(int(registry.get("directory_count", 0) or 0)),
        "- file_count: `{}`".format(int(registry.get("file_count", 0) or 0)),
        "- module_count: `{}`".format(len(modules)),
        "",
        "## Modules",
        "",
    ]
    for row in modules:
        item = dict(row or {})
        lines.append(
            "- `{}` :: root=`{}` domain=`{}` files=`{}` confidence=`{:.2f}`".format(
                _token(item.get("module_id")),
                _token(item.get("module_root")),
                _token(item.get("domain")),
                int(item.get("file_count", 0) or 0),
                float(item.get("confidence", 0.0) or 0.0),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_arch_graph_bootstrap(snapshot: Mapping[str, object]) -> str:
    graph = dict(snapshot.get("architecture_graph") or {})
    report = dict(snapshot.get("architecture_scan_report") or {})
    concepts = list(graph.get("concepts") or [])
    unknown_rows = list(report.get("modules_outside_expected_domain") or [])
    duplicate_rows = list(report.get("duplicate_symbol_definitions") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-26",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-1 architecture drift and duplicate-convergence plan",
        "",
        "# ARCH Graph Bootstrap",
        "",
        "## Module List",
        "",
    ]
    for row in list(graph.get("modules") or []):
        item = dict(row or {})
        lines.append("- `{}` -> `{}`".format(_token(item.get("module_id")), _token(item.get("module_root"))))
    lines.extend(["", "## Concept Candidates", ""])
    for row in concepts[:40]:
        item = dict(row or {})
        lines.append("- `{}` -> modules=`{}`".format(_token(item.get("concept_id")), len(list(item.get("modules") or []))))
    lines.extend(["", "## Duplicate Signals", ""])
    if not duplicate_rows:
        lines.append("- none")
    else:
        for row in duplicate_rows[:30]:
            item = dict(row or {})
            lines.append("- `{}` -> {}".format(_token(item.get("symbol_name")), ", ".join(list(item.get("file_paths") or [])[:4])))
    lines.extend(["", "## Unknown Domains", ""])
    if not unknown_rows:
        lines.append("- none")
    else:
        for row in unknown_rows[:30]:
            item = dict(row or {})
            lines.append("- `{}`".format(_token(item.get("module_root"))))
    lines.extend(
        [
            "",
            "## Next-Step Recommendations",
            "",
            "- Use duplicate symbol and multi-module symbol signals to define XI-1 convergence buckets.",
            "- Treat `src`-rooted unknown-domain modules as explicit boundary-audit candidates before any refactor planning.",
            "- Compare module dependency cycles against build-target ownership before proposing boundary changes.",
            "",
        ]
    )
    return "\n".join(lines)


def write_architecture_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    json_targets = {
        ARCHITECTURE_GRAPH_REL: dict(snapshot.get("architecture_graph") or {}),
        MODULE_REGISTRY_REL: dict(snapshot.get("module_registry") or {}),
        MODULE_DEP_GRAPH_REL: dict(snapshot.get("module_dependency_graph") or {}),
        SYMBOL_INDEX_REL: dict(snapshot.get("symbol_index") or {}),
        INCLUDE_GRAPH_REL: dict(snapshot.get("include_graph") or {}),
        BUILD_GRAPH_REL: dict(snapshot.get("build_graph") or {}),
        ARCHITECTURE_SCAN_REPORT_REL: dict(snapshot.get("architecture_scan_report") or {}),
    }
    for rel_path, payload in json_targets.items():
        written[rel_path] = _write_canonical_json(_repo_abs(root, rel_path), payload)
    written[ARCHITECTURE_GRAPH_REPORT_REL] = _write_text(_repo_abs(root, ARCHITECTURE_GRAPH_REPORT_REL), render_architecture_graph_report(snapshot) + "\n")
    written[MODULE_DISCOVERY_REPORT_REL] = _write_text(_repo_abs(root, MODULE_DISCOVERY_REPORT_REL), render_module_discovery_report(snapshot) + "\n")
    written[ARCH_GRAPH_BOOTSTRAP_REL] = _write_text(_repo_abs(root, ARCH_GRAPH_BOOTSTRAP_REL), render_arch_graph_bootstrap(snapshot) + "\n")
    return written


__all__ = [
    "ARCHITECTURE_GRAPH_REL",
    "ARCHITECTURE_GRAPH_REPORT_REL",
    "ARCHITECTURE_SCAN_REPORT_REL",
    "ARCH_GRAPH_BOOTSTRAP_REL",
    "BUILD_GRAPH_REL",
    "INCLUDE_GRAPH_REL",
    "MODULE_DEP_GRAPH_REL",
    "MODULE_DISCOVERY_REPORT_REL",
    "MODULE_REGISTRY_REL",
    "OUTPUT_REL_PATHS",
    "SYMBOL_INDEX_REL",
    "build_architecture_snapshot",
    "classify_domain",
    "render_arch_graph_bootstrap",
    "render_architecture_graph_report",
    "render_module_discovery_report",
    "write_architecture_snapshot",
]
