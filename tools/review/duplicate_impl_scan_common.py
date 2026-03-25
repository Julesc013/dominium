"""Deterministic XI-1 duplicate implementation and shadow-module scan helpers."""

from __future__ import annotations

import json
import os
import re
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

DUPLICATE_IMPLS_REL = "data/audit/duplicate_impls.json"
SHADOW_MODULES_REL = "data/audit/shadow_modules.json"
DUPLICATE_CLUSTERS_REL = "data/audit/duplicate_clusters.json"
SRC_DIRECTORY_REPORT_REL = "data/audit/src_directory_report.json"

DUPLICATE_IMPLS_REPORT_REL = "docs/audit/DUPLICATE_IMPLEMENTATIONS_REPORT.md"
SRC_SHADOW_REPORT_REL = "docs/audit/SRC_SHADOW_REPORT.md"
XI_1_FINAL_REL = "docs/audit/XI_1_FINAL.md"

OUTPUT_REL_PATHS = {
    DUPLICATE_IMPLS_REL,
    SHADOW_MODULES_REL,
    DUPLICATE_CLUSTERS_REL,
    SRC_DIRECTORY_REPORT_REL,
    DUPLICATE_IMPLS_REPORT_REL,
    SRC_SHADOW_REPORT_REL,
    XI_1_FINAL_REL,
}

REQUIRED_INPUTS = {
    "architecture_graph": ARCHITECTURE_GRAPH_REL,
    "module_registry": MODULE_REGISTRY_REL,
    "symbol_index": SYMBOL_INDEX_REL,
    "include_graph": INCLUDE_GRAPH_REL,
    "build_graph": BUILD_GRAPH_REL,
    "module_dependency_graph": MODULE_DEP_GRAPH_REL,
}

ENTRYPOINT_PRODUCTS = {"app", "client", "launcher", "server", "setup"}
SRC_DIR_NAMES = {"src", "source"}
TEST_PATH_PREFIXES = ("tests/", "game/tests/", "tools/xstack/testx/tests/")
MAX_SYMBOL_WINDOW_LINES = 40
MAX_FINGERPRINT_TOKENS = 160
MAX_EVIDENCE_SYMBOLS = 12
MAX_DOC_REFS = 6
DOC_REPORT_DATE = "2026-03-26"

TOKEN_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*|0x[0-9A-Fa-f]+|\d+\.\d+|\d+|==|!=|<=|>=|::|->|=>|&&|\|\||[{}()\[\];,.:+\-*/%&|^~<>!=]"
)
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//.*?$|#.*?$", re.MULTILINE)
STRING_RE = re.compile(r"(?P<quote>['\"])(?:\\.|(?!\1).)*\1")

PYTHON_KEYWORDS = {
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "false",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "none",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "true",
    "try",
    "while",
    "with",
    "yield",
}

C_FAMILY_KEYWORDS = {
    "auto",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "constexpr",
    "continue",
    "default",
    "define",
    "delete",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "ifdef",
    "ifndef",
    "include",
    "inline",
    "int",
    "long",
    "namespace",
    "new",
    "nullptr",
    "private",
    "protected",
    "public",
    "register",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "template",
    "this",
    "throw",
    "true",
    "try",
    "typedef",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "while",
}
KEYWORD_TOKENS = PYTHON_KEYWORDS | C_FAMILY_KEYWORDS

GENERIC_SYMBOL_STOPWORDS = {
    "app",
    "build_report",
    "canonical_json_text",
    "canonical_sha256",
    "deterministic_fingerprint",
    "ensure_dir",
    "load_json",
    "main",
    "parse_kv",
    "print_usage",
    "read_json",
    "read_text",
    "require",
    "run",
    "run_cmd",
    "sha256_file",
    "usage",
    "write_text",
    "write_json",
}

UTILITY_NAME_TOKENS = {
    "app",
    "as",
    "baseline",
    "canonical",
    "clean",
    "cmd",
    "copy",
    "csv",
    "default",
    "dir",
    "dirs",
    "doc",
    "docs",
    "ensure",
    "final",
    "file",
    "files",
    "fingerprint",
    "format",
    "id",
    "ids",
    "int",
    "json",
    "kind",
    "list",
    "load",
    "main",
    "manifest",
    "map",
    "meta",
    "name",
    "norm",
    "normalize",
    "parse",
    "path",
    "paths",
    "platform",
    "policy",
    "print",
    "read",
    "registry",
    "rel",
    "repo",
    "report",
    "reports",
    "retro",
    "root",
    "run",
    "save",
    "schema",
    "sha256",
    "sort",
    "sorted",
    "str",
    "string",
    "strings",
    "suffix",
    "tag",
    "text",
    "to",
    "token",
    "tokens",
    "usage",
    "value",
    "values",
    "version",
    "write",
    "yaml",
}

DOC_TEXT_SEARCH_CACHE: dict[str, str] = {}

LOW_SIGNAL_SYMBOL_NAMES = {
    "defwindowproc",
    "defwindowproca",
    "dirent",
    "d_rng_hash_str32",
    "d_world",
    "sizeof",
    "stat",
}

LOW_SIGNAL_SUFFIXES = (
    "_DOC_REL",
    "_JSON_REL",
    "_REPORT_REL",
    "_REL",
    "_ROOT",
    "_TAG",
)

SEMANTIC_SIGNAL_TOKENS = {
    "anchor",
    "appshell",
    "attach",
    "bootstrap",
    "earth",
    "geo",
    "identity",
    "illum",
    "ipc",
    "logic",
    "negotiate",
    "negotiation",
    "orbit",
    "overlay",
    "pack",
    "probe",
    "process",
    "seed",
    "shadow",
    "signal",
    "sky",
    "supervisor",
    "time",
    "trust",
    "verify",
    "worldgen",
}

PRIORITY_BUCKETS = (
    (
        1,
        "core_semantic_engine",
        (
            "anchor",
            "build_id",
            "bundle_lock",
            "cap_neg",
            "identity",
            "negotiat",
            "overlay",
            "pack",
            "refin",
            "seed",
            "trust",
            "verify",
            "worldgen",
        ),
    ),
    (
        2,
        "product_entrypoint",
        (
            "appshell",
            "attach",
            "bootstrap",
            "client_main",
            "ipc",
            "launcher",
            "mode_selector",
            "server_main",
            "shell",
            "supervisor",
            "ui_mode",
        ),
    ),
    (
        3,
        "domain_system",
        (
            "compile",
            "earth",
            "illum",
            "logic",
            "orbit",
            "probe",
            "proc",
            "process",
            "sky",
            "sys",
            "system",
        ),
    ),
)


class XiInputMissingError(RuntimeError):
    """Raised when the required XI-0 inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing XI-0 inputs")
        self.missing_paths = sorted({_norm_rel(path) for path in missing_paths if _token(path)})
        self.refusal_code = "refusal.xi.missing_inputs"
        self.remediation = "Run Ξ-0 first."


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


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
        handle.write(canonical_json_text(dict(payload)))
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


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _required_inputs(repo_root: str) -> dict[str, dict]:
    root = _repo_root(repo_root)
    missing = []
    payloads: dict[str, dict] = {}
    for key, rel_path in sorted(REQUIRED_INPUTS.items()):
        abs_path = _repo_abs(root, rel_path)
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
            continue
        payload = _read_json(abs_path)
        if not payload:
            missing.append(rel_path)
            continue
        payloads[key] = payload
    if missing:
        raise XiInputMissingError(missing)
    return payloads


def _shadow_surface_path(path: str) -> bool:
    rel_path = _norm_rel(path).lower().strip("/")
    if rel_path in {"src", "source"}:
        return True
    parts = [part for part in rel_path.split("/") if part]
    return any(part in SRC_DIR_NAMES for part in parts)


def _shadow_surface_module(module_row: Mapping[str, object]) -> bool:
    return _shadow_surface_path(_token(module_row.get("module_root"))) or _token(module_row.get("domain")) == "unknown" or float(module_row.get("confidence", 0.0) or 0.0) < 0.90


def _simple_symbol_name(symbol_name: object) -> str:
    token = _token(symbol_name)
    if not token:
        return ""
    token = token.split("::")[-1]
    token = token.split(".")[-1]
    return token.lower()


def _symbol_public_name(symbol_name: object) -> str:
    token = _simple_symbol_name(symbol_name)
    if not token or token.startswith("_"):
        return ""
    return token


def _iter_term_values(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        items: list[object] = []
        for key in sorted(value):
            items.extend(_iter_term_values(key))
            items.extend(_iter_term_values(value[key]))
        return items
    if isinstance(value, (list, tuple, set)):
        items: list[object] = []
        for entry in value:
            items.extend(_iter_term_values(entry))
        return items
    return [value]


def _term_fragments(value: object) -> list[str]:
    raw = _norm_rel(value)
    if not raw:
        return []
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw)
    expanded = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", expanded)
    expanded = re.sub(r"[^A-Za-z0-9]+", " ", expanded)
    return [part.lower() for part in expanded.split() if part]


def _path_terms(*values: object) -> list[str]:
    tokens: set[str] = set()
    for value in values:
        for entry in _iter_term_values(value):
            for raw in _term_fragments(entry):
                tokens.add(raw)
    return sorted(tokens)


def _tests_only_paths(paths: Sequence[object]) -> bool:
    rel_paths = [_norm_rel(path) for path in paths if _norm_rel(path)]
    return bool(rel_paths) and all(path.startswith(TEST_PATH_PREFIXES) for path in rel_paths)


def _is_init_export_path(path: object) -> bool:
    return os.path.basename(_norm_rel(path)) == "__init__.py"


def _is_generic_symbol_name(symbol_name: object) -> bool:
    raw = _token(symbol_name)
    simple = _simple_symbol_name(symbol_name)
    if not simple:
        return True
    if simple.startswith("_") or simple in GENERIC_SYMBOL_STOPWORDS or simple in LOW_SIGNAL_SYMBOL_NAMES:
        return True
    upper_name = raw.upper()
    if any(upper_name.endswith(suffix) for suffix in LOW_SIGNAL_SUFFIXES):
        tokens = set(_term_fragments(simple))
        if not tokens & SEMANTIC_SIGNAL_TOKENS:
            return True
    tokens = _term_fragments(simple)
    if simple.startswith("d_") and not (set(tokens) & SEMANTIC_SIGNAL_TOKENS):
        return True
    if not tokens:
        return True
    return all(token in UTILITY_NAME_TOKENS or token.isdigit() for token in tokens)


def _group_terms(group: Mapping[str, object]) -> list[str]:
    definitions = [dict(row or {}) for row in list(group.get("definitions") or [])]
    symbol_names = list(group.get("symbol_names") or [])
    raw_symbol_names = [
        _simple_symbol_name(symbol_name)
        for symbol_name in symbol_names
        if _simple_symbol_name(symbol_name)
    ]
    return _path_terms(
        symbol_names,
        raw_symbol_names,
        [row.get("file_path") for row in definitions],
        list(group.get("module_ids") or []),
        list(group.get("products") or []),
    )


def _normalized_search_text(text: object) -> str:
    return " ".join(_term_fragments(text))


def _keyword_hit_count(group: Mapping[str, object], keywords: Sequence[str]) -> int:
    terms_text = " ".join(_group_terms(group))
    raw_symbol_names = " ".join(
        _simple_symbol_name(symbol_name)
        for symbol_name in list(group.get("symbol_names") or [])
        if _simple_symbol_name(symbol_name)
    )
    hits = 0
    for keyword in keywords:
        normalized = _normalized_search_text(keyword)
        if (normalized and normalized in terms_text) or keyword.lower() in raw_symbol_names:
            hits += 1
    return hits


def _doc_files(module_rows: Sequence[Mapping[str, object]]) -> list[str]:
    files = set()
    for row in module_rows:
        if _token(row.get("domain")) != "docs" and not _token(row.get("module_root")).startswith("docs"):
            continue
        for rel_path in list(row.get("owned_files") or []):
            rel_norm = _norm_rel(rel_path)
            if rel_norm.endswith(".md"):
                files.add(rel_norm)
    return sorted(files)


def _build_indexes(
    architecture_graph: Mapping[str, object],
    module_registry: Mapping[str, object],
    build_graph: Mapping[str, object],
) -> dict[str, object]:
    arch_modules = sorted(
        [dict(row or {}) for row in list(architecture_graph.get("modules") or [])],
        key=lambda row: _token(row.get("module_id")),
    )
    registry_modules = sorted(
        [dict(row or {}) for row in list(module_registry.get("modules") or [])],
        key=lambda row: _token(row.get("module_id")),
    )
    module_by_id = {_token(row.get("module_id")): row for row in arch_modules}
    registry_module_by_id = {_token(row.get("module_id")): row for row in registry_modules}
    file_to_module: dict[str, str] = {}
    all_files: set[str] = set()
    for row in registry_modules:
        module_id = _token(row.get("module_id"))
        for rel_path in list(row.get("owned_files") or []):
            rel_norm = _norm_rel(rel_path)
            if rel_norm:
                all_files.add(rel_norm)
                file_to_module.setdefault(rel_norm, module_id)

    target_rows = sorted(
        [dict(row or {}) for row in list(build_graph.get("targets") or [])],
        key=lambda row: _token(row.get("target_id")),
    )
    file_to_targets: defaultdict[str, set[str]] = defaultdict(set)
    file_to_products: defaultdict[str, set[str]] = defaultdict(set)
    target_to_product: dict[str, str] = {}
    for row in target_rows:
        target_id = _token(row.get("target_id"))
        product_id = _token(row.get("product_id"))
        target_to_product[target_id] = product_id
        for source_path in list(row.get("sources") or []):
            rel_norm = _norm_rel(source_path)
            if not rel_norm:
                continue
            file_to_targets[rel_norm].add(target_id)
            if product_id:
                file_to_products[rel_norm].add(product_id)

    docs_files = _doc_files(registry_modules)
    directories = sorted({_norm_rel(row.get("path")) for row in list(module_registry.get("directories") or []) if _token(dict(row or {}).get("path"))})
    return {
        "all_files": sorted(all_files),
        "arch_modules": arch_modules,
        "directories": directories,
        "docs_files": docs_files,
        "file_to_module": file_to_module,
        "file_to_products": {key: sorted(value) for key, value in file_to_products.items()},
        "file_to_targets": {key: sorted(value) for key, value in file_to_targets.items()},
        "module_by_id": module_by_id,
        "registry_module_by_id": registry_module_by_id,
        "target_to_product": target_to_product,
    }


def _exact_duplicate_groups(
    symbol_rows: Sequence[Mapping[str, object]],
    file_to_targets: Mapping[str, Sequence[str]],
    file_to_products: Mapping[str, Sequence[str]],
) -> tuple[list[dict], dict[str, list[str]], dict[str, list[str]], dict[str, dict[str, set[str]]]]:
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for row in symbol_rows:
        signature_hash = _token(dict(row or {}).get("signature_hash"))
        if signature_hash:
            grouped[signature_hash].append(dict(row or {}))

    duplicate_groups: list[dict] = []
    file_to_group_ids: defaultdict[str, list[str]] = defaultdict(list)
    file_to_symbol_names: defaultdict[str, set[str]] = defaultdict(set)
    module_pair_exact_names: defaultdict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for signature_hash, rows in sorted(grouped.items()):
        unique_rows = sorted(
            {
                (
                    _norm_rel(row.get("file_path")),
                    int(row.get("line_number", 1) or 1),
                    _token(row.get("module_id")),
                    _token(row.get("symbol_name")),
                    _token(row.get("symbol_kind")),
                )
                for row in rows
                if _norm_rel(row.get("file_path"))
            }
        )
        if len({item[0] for item in unique_rows}) < 2:
            continue
        definitions = []
        symbol_names = sorted({item[3] for item in unique_rows if item[3]})
        module_ids = sorted({item[2] for item in unique_rows if item[2]})
        build_targets = sorted({target for item in unique_rows for target in list(file_to_targets.get(item[0]) or [])})
        products = sorted({product for item in unique_rows for product in list(file_to_products.get(item[0]) or [])})
        primary_symbol = symbol_names[0] if symbol_names else ""
        group_id = "duplicate.sig.{}".format(canonical_sha256({"signature_hash": signature_hash, "symbol_names": symbol_names})[:16])
        for file_path, line_number, module_id, symbol_name, symbol_kind in unique_rows:
            definitions.append(
                {
                    "build_targets": sorted(list(file_to_targets.get(file_path) or [])),
                    "file_path": file_path,
                    "line_number": line_number,
                    "module_id": module_id,
                    "products": sorted(list(file_to_products.get(file_path) or [])),
                    "symbol_kind": symbol_kind,
                    "symbol_name": symbol_name,
                }
            )
            file_to_group_ids[file_path].append(group_id)
            if symbol_name:
                file_to_symbol_names[file_path].add(symbol_name)
        for left_index, left_module in enumerate(module_ids):
            for right_module in module_ids[left_index + 1 :]:
                public_names = {
                    _symbol_public_name(item[3])
                    for item in unique_rows
                    if _symbol_public_name(item[3])
                }
                module_pair_exact_names[left_module][right_module].update(public_names)
                module_pair_exact_names[right_module][left_module].update(public_names)
        duplicate_groups.append(
            {
                "build_targets": build_targets,
                "definition_count": len(definitions),
                "definitions": definitions,
                "group_id": group_id,
                "module_ids": module_ids,
                "products": products,
                "signature_hash": signature_hash,
                "symbol_name": primary_symbol,
                "symbol_names": symbol_names,
            }
        )

    duplicate_groups = sorted(
        duplicate_groups,
        key=lambda row: (
            _token(row.get("symbol_name")),
            _token(row.get("signature_hash")),
            _token(row.get("group_id")),
        ),
    )
    return (
        duplicate_groups,
        {key: sorted(value) for key, value in file_to_group_ids.items()},
        {key: sorted(value) for key, value in file_to_symbol_names.items()},
        {left: {right: set(sorted(names)) for right, names in mapping.items()} for left, mapping in module_pair_exact_names.items()},
    )


def _string_normalized_text(text: str) -> str:
    return STRING_RE.sub(" STR ", text)


def _comment_normalized_text(text: str) -> str:
    without_block = BLOCK_COMMENT_RE.sub(" ", text)
    return LINE_COMMENT_RE.sub(" ", without_block)


def _normalized_tokens(text: str) -> list[str]:
    raw = _comment_normalized_text(_string_normalized_text(text))
    tokens = TOKEN_RE.findall(raw)
    normalized = []
    for token in tokens:
        lower = token.lower()
        if re.fullmatch(r"0x[0-9a-f]+|\d+\.\d+|\d+", lower):
            normalized.append("NUM")
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            normalized.append(lower if lower in KEYWORD_TOKENS else "ID")
            continue
        normalized.append(token)
    return normalized[:MAX_FINGERPRINT_TOKENS]


def _symbol_chunk_rows(symbol_rows: Sequence[Mapping[str, object]], repo_root: str) -> dict[tuple[str, int, str, str], dict[str, object]]:
    grouped_by_file: defaultdict[str, list[dict]] = defaultdict(list)
    for row in symbol_rows:
        rel_path = _norm_rel(dict(row or {}).get("file_path"))
        if rel_path:
            grouped_by_file[rel_path].append(dict(row or {}))

    chunks: dict[tuple[str, int, str, str], dict[str, object]] = {}
    root = _repo_root(repo_root)
    for rel_path in sorted(grouped_by_file):
        abs_path = _repo_abs(root, rel_path)
        lines = _read_text(abs_path).splitlines()
        file_rows = sorted(
            grouped_by_file[rel_path],
            key=lambda row: (
                int(row.get("line_number", 1) or 1),
                _token(row.get("symbol_name")),
                _token(row.get("signature_hash")),
            ),
        )
        unique_lines = sorted({int(row.get("line_number", 1) or 1) for row in file_rows})
        next_line_map: dict[int, int] = {}
        for index, line_number in enumerate(unique_lines):
            next_line_map[line_number] = unique_lines[index + 1] if index + 1 < len(unique_lines) else 0
        for row in file_rows:
            line_number = int(row.get("line_number", 1) or 1)
            next_line = int(next_line_map.get(line_number, 0) or 0)
            end_line = line_number + MAX_SYMBOL_WINDOW_LINES - 1
            if next_line > line_number:
                end_line = min(end_line, next_line - 1)
            start_index = max(0, line_number - 1)
            end_index = min(len(lines), max(start_index + 1, end_line))
            chunk_text = "\n".join(lines[start_index:end_index])
            tokens = _normalized_tokens(chunk_text)
            token_fingerprint = canonical_sha256({"tokens": tokens})
            key = (
                rel_path,
                line_number,
                _token(row.get("symbol_name")),
                _token(row.get("signature_hash")),
            )
            chunks[key] = {
                "chunk_line_count": max(1, end_index - start_index),
                "normalized_token_count": len(tokens),
                "token_fingerprint": token_fingerprint,
                "token_preview": tokens[:24],
            }
    return chunks


def _near_duplicate_clusters(
    symbol_rows: Sequence[Mapping[str, object]],
    file_to_targets: Mapping[str, Sequence[str]],
    file_to_products: Mapping[str, Sequence[str]],
    repo_root: str,
) -> tuple[list[dict], dict[str, list[str]], dict[str, dict[str, set[str]]]]:
    chunks = _symbol_chunk_rows(symbol_rows, repo_root=repo_root)
    grouped: defaultdict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in symbol_rows:
        rel_path = _norm_rel(dict(row or {}).get("file_path"))
        line_number = int(dict(row or {}).get("line_number", 1) or 1)
        symbol_name = _token(dict(row or {}).get("symbol_name"))
        signature_hash = _token(dict(row or {}).get("signature_hash"))
        chunk = chunks.get((rel_path, line_number, symbol_name, signature_hash))
        if not chunk:
            continue
        grouped[(symbol_name, _token(chunk.get("token_fingerprint")))].append(
            {
                "build_targets": sorted(list(file_to_targets.get(rel_path) or [])),
                "chunk_line_count": int(chunk.get("chunk_line_count", 1) or 1),
                "file_path": rel_path,
                "line_number": line_number,
                "module_id": _token(dict(row or {}).get("module_id")),
                "normalized_token_count": int(chunk.get("normalized_token_count", 0) or 0),
                "products": sorted(list(file_to_products.get(rel_path) or [])),
                "signature_hash": signature_hash,
                "symbol_kind": _token(dict(row or {}).get("symbol_kind")),
                "symbol_name": symbol_name,
                "token_fingerprint": _token(chunk.get("token_fingerprint")),
                "token_preview": list(chunk.get("token_preview") or []),
            }
        )

    clusters: list[dict] = []
    file_to_cluster_ids: defaultdict[str, list[str]] = defaultdict(list)
    module_pair_near_names: defaultdict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for (symbol_name, token_fingerprint), rows in sorted(grouped.items()):
        definitions = sorted(
            rows,
            key=lambda row: (
                _token(row.get("file_path")),
                int(row.get("line_number", 1) or 1),
                _token(row.get("module_id")),
            ),
        )
        if len({(_token(row.get("file_path")), int(row.get("line_number", 1) or 1)) for row in definitions}) < 2:
            continue
        cluster_id = "duplicate.cluster.{}".format(canonical_sha256({"symbol_name": symbol_name, "token_fingerprint": token_fingerprint})[:16])
        module_ids = sorted({_token(row.get("module_id")) for row in definitions if _token(row.get("module_id"))})
        build_targets = sorted({target for row in definitions for target in list(row.get("build_targets") or [])})
        products = sorted({product for row in definitions for product in list(row.get("products") or [])})
        min_tokens = min(int(row.get("normalized_token_count", 0) or 0) for row in definitions)
        min_lines = min(int(row.get("chunk_line_count", 1) or 1) for row in definitions)
        same_signature = len({_token(row.get("signature_hash")) for row in definitions if _token(row.get("signature_hash"))}) == 1
        confidence = 0.55
        if same_signature:
            confidence += 0.20
        if min_tokens >= 16:
            confidence += 0.10
        if min_tokens >= 32:
            confidence += 0.05
        if min_lines >= 4:
            confidence += 0.05
        if len(module_ids) > 1:
            confidence += 0.05
        confidence = min(0.95, round(confidence, 2))
        for row in definitions:
            file_to_cluster_ids[_token(row.get("file_path"))].append(cluster_id)
        public_name = _symbol_public_name(symbol_name)
        if public_name:
            for left_index, left_module in enumerate(module_ids):
                for right_module in module_ids[left_index + 1 :]:
                    module_pair_near_names[left_module][right_module].add(public_name)
                    module_pair_near_names[right_module][left_module].add(public_name)
        clusters.append(
            {
                "build_targets": build_targets,
                "cluster_id": cluster_id,
                "confidence": confidence,
                "definition_count": len(definitions),
                "definitions": definitions,
                "module_ids": module_ids,
                "products": products,
                "symbol_name": symbol_name,
                "token_fingerprint": token_fingerprint,
            }
        )

    clusters = sorted(
        clusters,
        key=lambda row: (
            _token(row.get("symbol_name")),
            _token(row.get("token_fingerprint")),
            _token(row.get("cluster_id")),
        ),
    )
    return (
        clusters,
        {key: sorted(value) for key, value in file_to_cluster_ids.items()},
        {left: {right: set(sorted(names)) for right, names in mapping.items()} for left, mapping in module_pair_near_names.items()},
    )


def _build_module_symbol_sets(module_rows: Sequence[Mapping[str, object]]) -> tuple[dict[str, set[str]], set[str]]:
    frequency = Counter()
    raw_sets: dict[str, set[str]] = {}
    for row in module_rows:
        module_id = _token(row.get("module_id"))
        symbol_set = {
            _simple_symbol_name(symbol_name)
            for symbol_name in list(row.get("symbols") or [])
            if _simple_symbol_name(symbol_name)
        }
        raw_sets[module_id] = symbol_set
        for symbol_name in symbol_set:
            frequency[symbol_name] += 1

    stop_symbols = {
        symbol_name
        for symbol_name, count in frequency.items()
        if count > 20 or symbol_name in GENERIC_SYMBOL_STOPWORDS
    }
    filtered_sets = {}
    for module_id, symbol_set in raw_sets.items():
        filtered_sets[module_id] = {
            symbol_name
            for symbol_name in symbol_set
            if symbol_name not in stop_symbols and len(symbol_name) >= 4
        }
    return filtered_sets, stop_symbols


def _shadow_modules_report(
    module_rows: Sequence[Mapping[str, object]],
    module_pair_exact_names: Mapping[str, Mapping[str, set[str]]],
    module_pair_near_names: Mapping[str, Mapping[str, set[str]]],
) -> list[dict]:
    module_by_id = {_token(row.get("module_id")): dict(row or {}) for row in module_rows}
    module_symbol_sets, _ = _build_module_symbol_sets(module_rows)
    symbol_index: defaultdict[str, set[str]] = defaultdict(set)
    for module_id, symbol_set in module_symbol_sets.items():
        for symbol_name in symbol_set:
            symbol_index[symbol_name].add(module_id)

    shadow_rows: list[dict] = []
    for module_id in sorted(module_by_id):
        module_row = module_by_id[module_id]
        if not _shadow_surface_module(module_row):
            continue
        symbol_set = set(module_symbol_sets.get(module_id) or set())
        if len(symbol_set) < 3 and not dict(module_pair_exact_names.get(module_id) or {}):
            continue
        candidate_ids: set[str] = set()
        for symbol_name in symbol_set:
            candidate_ids.update(symbol_index.get(symbol_name) or set())
        candidate_ids.update(dict(module_pair_exact_names.get(module_id) or {}).keys())
        candidate_ids.update(dict(module_pair_near_names.get(module_id) or {}).keys())
        candidate_ids.discard(module_id)

        candidate_matches = []
        module_dependencies = set(module_row.get("dependencies") or [])
        for candidate_id in sorted(candidate_ids):
            candidate_row = module_by_id.get(candidate_id)
            if not candidate_row:
                continue
            if _shadow_surface_module(candidate_row) and float(candidate_row.get("confidence", 0.0) or 0.0) <= float(module_row.get("confidence", 0.0) or 0.0):
                continue
            candidate_symbols = set(module_symbol_sets.get(candidate_id) or set())
            shared_symbols = sorted(symbol_set & candidate_symbols)
            exact_symbols = sorted(set(dict(module_pair_exact_names.get(module_id) or {}).get(candidate_id) or set()))
            near_symbols = sorted(set(dict(module_pair_near_names.get(module_id) or {}).get(candidate_id) or set()) - set(exact_symbols))
            if len(shared_symbols) < 3 and len(exact_symbols) < 3 and len(near_symbols) < 3:
                continue
            candidate_dependencies = set(candidate_row.get("dependencies") or [])
            symbol_overlap = round(len(shared_symbols) / float(len(symbol_set | candidate_symbols) or 1), 4)
            dependency_overlap = round(len(module_dependencies & candidate_dependencies) / float(len(module_dependencies | candidate_dependencies) or 1), 4)
            evidence_strength = len(exact_symbols) + 0.5 * len(near_symbols)
            overlap_score = round(
                0.50 * min(1.0, evidence_strength / 8.0)
                + 0.35 * symbol_overlap
                + 0.15 * dependency_overlap
                + (0.05 if not _shadow_surface_module(candidate_row) else 0.0),
                4,
            )
            if overlap_score < 0.25 and evidence_strength < 4.0:
                continue
            impacted_build_targets = sorted(set(list(module_row.get("build_targets") or [])) | set(list(candidate_row.get("build_targets") or [])))
            candidate_matches.append(
                {
                    "architecture_placement_violation": _shadow_surface_module(module_row) and not _shadow_surface_module(candidate_row),
                    "candidate_module_id": candidate_id,
                    "candidate_module_root": _token(candidate_row.get("module_root")),
                    "dependency_overlap_ratio": dependency_overlap,
                    "exact_duplicate_symbol_count": len(exact_symbols),
                    "exact_duplicate_symbols": exact_symbols[:MAX_EVIDENCE_SYMBOLS],
                    "impacted_build_targets": impacted_build_targets,
                    "near_duplicate_symbol_count": len(near_symbols),
                    "near_duplicate_symbols": near_symbols[:MAX_EVIDENCE_SYMBOLS],
                    "overlap_score": overlap_score,
                    "shared_symbol_count": len(shared_symbols),
                    "shared_symbols": shared_symbols[:MAX_EVIDENCE_SYMBOLS],
                    "symbol_overlap_ratio": symbol_overlap,
                }
            )

        if not candidate_matches:
            continue
        candidate_matches = sorted(
            candidate_matches,
            key=lambda row: (
                -float(row.get("overlap_score", 0.0) or 0.0),
                -int(row.get("exact_duplicate_symbol_count", 0) or 0),
                -int(row.get("shared_symbol_count", 0) or 0),
                _token(row.get("candidate_module_id")),
            ),
        )
        best = candidate_matches[0]
        impacted_products = sorted(
            {
                _token(product)
                for match in candidate_matches[:3]
                for product in list(match.get("impacted_build_targets") or [])
                if _token(product)
            }
        )
        shadow_rows.append(
            {
                "architecture_placement_violation": bool(best.get("architecture_placement_violation")),
                "canonical_candidate_module_id": _token(best.get("candidate_module_id")),
                "candidate_matches": candidate_matches[:5],
                "confidence": round(min(0.97, 0.55 + min(0.25, float(best.get("overlap_score", 0.0) or 0.0) / 2.0) + min(0.17, int(best.get("exact_duplicate_symbol_count", 0) or 0) * 0.02)), 2),
                "exact_duplicate_symbol_count": int(best.get("exact_duplicate_symbol_count", 0) or 0),
                "impacted_products": impacted_products,
                "near_duplicate_symbol_count": int(best.get("near_duplicate_symbol_count", 0) or 0),
                "overlap_metrics": {
                    "dependency_overlap_ratio": float(best.get("dependency_overlap_ratio", 0.0) or 0.0),
                    "overlap_score": float(best.get("overlap_score", 0.0) or 0.0),
                    "shared_symbol_count": int(best.get("shared_symbol_count", 0) or 0),
                    "symbol_overlap_ratio": float(best.get("symbol_overlap_ratio", 0.0) or 0.0),
                },
                "shadow_module_id": module_id,
                "shadow_module_root": _token(module_row.get("module_root")),
            }
        )

    return sorted(
        shadow_rows,
        key=lambda row: (
            -float(dict(row.get("overlap_metrics") or {}).get("overlap_score", 0.0) or 0.0),
            -int(row.get("exact_duplicate_symbol_count", 0) or 0),
            _token(row.get("shadow_module_id")),
        ),
    )


def _priority_bucket(group: Mapping[str, object]) -> tuple[int, str]:
    for rank, label, keywords in PRIORITY_BUCKETS:
        if _keyword_hit_count(group, keywords) > 0:
            return rank, label
    return 4, "tools_and_docs"


def _placement_violation(group: Mapping[str, object]) -> bool:
    definitions = [dict(row or {}) for row in list(group.get("definitions") or [])]
    has_shadow = any(_shadow_surface_path(_token(row.get("file_path"))) or _token(row.get("module_id")).startswith("unknown.") for row in definitions)
    has_non_shadow = any(not (_shadow_surface_path(_token(row.get("file_path"))) or _token(row.get("module_id")).startswith("unknown.")) for row in definitions)
    return has_shadow and has_non_shadow


def _docs_refs_for_group(group: Mapping[str, object], docs_files: Sequence[str], repo_root: str) -> list[str]:
    search_terms: list[str] = []
    for symbol_name in list(group.get("symbol_names") or []):
        if _is_generic_symbol_name(symbol_name):
            continue
        symbol_phrase = _normalized_search_text(symbol_name)
        if symbol_phrase and len(symbol_phrase.replace(" ", "")) >= 8:
            search_terms.append(symbol_phrase)
    if not search_terms:
        fallback_terms = [
            term
            for term in _group_terms(group)
            if len(term) >= 5 and term not in UTILITY_NAME_TOKENS
        ]
        if len(fallback_terms) >= 2:
            search_terms.append(" ".join(fallback_terms[:3]))
        else:
            search_terms.extend(fallback_terms[:2])
    search_terms = sorted({term for term in search_terms if term})[:6]
    refs = []
    root = _repo_root(repo_root)
    for rel_path in docs_files:
        if len(refs) >= MAX_DOC_REFS:
            break
        cache_key = _norm_rel(rel_path)
        doc_text = DOC_TEXT_SEARCH_CACHE.get(cache_key)
        if doc_text is None:
            doc_text = _normalized_search_text(_read_text(_repo_abs(root, rel_path)))
            DOC_TEXT_SEARCH_CACHE[cache_key] = doc_text
        if not doc_text:
            continue
        if any(term in doc_text for term in search_terms):
            refs.append(rel_path)
    return refs


def _ranked_duplicate_groups(duplicate_groups: Sequence[Mapping[str, object]], docs_files: Sequence[str], repo_root: str) -> list[dict]:
    ranked_rows = []
    for group in duplicate_groups:
        definitions = [dict(row or {}) for row in list(group.get("definitions") or [])]
        file_paths = [_norm_rel(row.get("file_path")) for row in definitions if _norm_rel(row.get("file_path"))]
        distinct_modules = len({_token(row.get("module_id")) for row in definitions if _token(row.get("module_id"))})
        distinct_files = len(set(file_paths))
        distinct_products = len({_token(product) for product in list(group.get("products") or []) if _token(product)})
        bucket_rank, bucket_label = _priority_bucket(group)
        keyword_hits = 0
        for rank, _label, keywords in PRIORITY_BUCKETS:
            if rank == bucket_rank:
                keyword_hits = _keyword_hit_count(group, keywords)
                break
        placement_violation = _placement_violation(group)
        src_overlap = any(_shadow_surface_path(path) for path in file_paths)
        tests_only = _tests_only_paths(file_paths)
        generic_symbol = _is_generic_symbol_name(group.get("symbol_name"))
        init_export_count = sum(1 for path in file_paths if _is_init_export_path(path))
        cross_module = distinct_modules > 1
        entrypoint_overlap = bool({_token(product) for product in list(group.get("products") or []) if _token(product)} & ENTRYPOINT_PRODUCTS)
        semantic_candidate = bucket_rank <= 3
        if tests_only or generic_symbol:
            continue
        if not (semantic_candidate or placement_violation or src_overlap or entrypoint_overlap):
            continue
        if not (cross_module or src_overlap or entrypoint_overlap or distinct_files >= 3):
            continue
        score = (
            {1: 700, 2: 620, 3: 540, 4: 420}.get(bucket_rank, 360)
            + min(84, distinct_files * 14)
            + min(90, distinct_modules * 18)
            + distinct_products * 16
            + keyword_hits * 24
            + (60 if placement_violation else 0)
            + (35 if src_overlap else 0)
            + (30 if cross_module else 0)
            + (18 if entrypoint_overlap else 0)
            - (28 if init_export_count and not cross_module else 0)
        )
        ranked_rows.append(
            {
                "bucket_label": bucket_label,
                "bucket_rank": bucket_rank,
                "docs_refs": [],
                "group_id": _token(group.get("group_id")),
                "placement_violation": placement_violation,
                "score": score,
                "src_overlap": src_overlap,
                "symbol_name": _token(group.get("symbol_name")),
                "symbol_names": list(group.get("symbol_names") or []),
            }
        )
    ranked_rows = sorted(
        ranked_rows,
        key=lambda row: (
            -int(row.get("score", 0) or 0),
            int(row.get("bucket_rank", 4) or 4),
            _token(row.get("symbol_name")),
            _token(row.get("group_id")),
        ),
    )
    top_group_ids = {_token(row.get("group_id")) for row in ranked_rows[:40]}
    groups_by_id = {_token(group.get("group_id")): dict(group or {}) for group in duplicate_groups}
    for row in ranked_rows:
        group_id = _token(row.get("group_id"))
        if group_id not in top_group_ids:
            continue
        row["docs_refs"] = _docs_refs_for_group(groups_by_id[group_id], docs_files, repo_root)
        row["score"] += len(row["docs_refs"]) * 4
    return sorted(
        ranked_rows,
        key=lambda row: (
            -int(row.get("score", 0) or 0),
            int(row.get("bucket_rank", 4) or 4),
            _token(row.get("symbol_name")),
            _token(row.get("group_id")),
        ),
    )


def _src_directories_report(
    directories: Sequence[str],
    module_rows: Sequence[Mapping[str, object]],
    file_to_group_ids: Mapping[str, Sequence[str]],
    file_to_symbol_names: Mapping[str, Sequence[str]],
    file_to_cluster_ids: Mapping[str, Sequence[str]],
    file_to_products: Mapping[str, Sequence[str]],
    ranked_group_rows: Sequence[Mapping[str, object]],
) -> list[dict]:
    ranked_by_id = {_token(row.get("group_id")): dict(row or {}) for row in ranked_group_rows}
    src_directories = []
    module_rows = [dict(row or {}) for row in module_rows]
    all_files = sorted(
        {
            _norm_rel(rel_path)
            for row in module_rows
            for rel_path in list(row.get("owned_files") or [])
            if _norm_rel(rel_path)
        }
    )
    for directory in sorted(_norm_rel(path) for path in directories if _shadow_surface_path(path)):
        basename = os.path.basename(directory)
        files = [path for path in all_files if path == directory or path.startswith(directory + "/")]
        inferred_modules = sorted(
            {
                _token(row.get("module_id"))
                for row in module_rows
                if _token(row.get("module_root")) == directory or _token(row.get("module_root")).startswith(directory + "/")
            }
        )
        duplicate_group_ids = sorted(
            {
                group_id
                for file_path in files
                for group_id in list(file_to_group_ids.get(file_path) or [])
                if _token(group_id)
            }
        )
        near_cluster_ids = sorted(
            {
                cluster_id
                for file_path in files
                for cluster_id in list(file_to_cluster_ids.get(file_path) or [])
                if _token(cluster_id)
            }
        )
        duplicate_symbols = sorted(
            {
                symbol_name
                for file_path in files
                for symbol_name in list(file_to_symbol_names.get(file_path) or [])
                if _token(symbol_name)
            }
        )
        impacted_products = sorted(
            {
                product
                for file_path in files
                for product in list(file_to_products.get(file_path) or [])
                if _token(product)
            }
        )
        tests_only = _tests_only_paths(files)
        duplicate_ranks = [int(dict(ranked_by_id.get(group_id) or {}).get("bucket_rank", 4) or 4) for group_id in duplicate_group_ids]
        if tests_only:
            severity = "LOW"
            reason = "directory contains test-only sources"
        elif (set(impacted_products) & ENTRYPOINT_PRODUCTS) or any(rank <= 2 for rank in duplicate_ranks):
            severity = "HIGH"
            reason = "directory overlaps product entrypoints or high-priority duplicate groups"
        else:
            severity = "MED"
            reason = "directory contains duplicate implementations outside test-only scope"
        src_directories.append(
            {
                "directory_path": directory,
                "duplicate_cluster_count": len(near_cluster_ids),
                "duplicate_group_count": len(duplicate_group_ids),
                "duplicate_group_ids": duplicate_group_ids,
                "duplicate_symbol_names": duplicate_symbols,
                "file_count": len(files),
                "files": files,
                "impacted_products": impacted_products,
                "inferred_modules": inferred_modules,
                "match_kind": basename,
                "severity": severity,
                "severity_reason": reason,
            }
        )
    return sorted(
        src_directories,
        key=lambda row: (
            {"HIGH": 0, "MED": 1, "LOW": 2}.get(_token(row.get("severity")), 3),
            _token(row.get("directory_path")),
        ),
    )


def _report_src_directories(src_report: Mapping[str, object]) -> list[dict]:
    return sorted(
        [dict(row or {}) for row in list(src_report.get("directories") or [])],
        key=lambda row: (
            {"HIGH": 0, "MED": 1, "LOW": 2}.get(_token(row.get("severity")), 3),
            -int(row.get("duplicate_group_count", 0) or 0),
            -int(row.get("file_count", 0) or 0),
            _token(row.get("directory_path")),
        ),
    )


def build_duplicate_impl_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    payloads = _required_inputs(root)
    architecture_graph = dict(payloads["architecture_graph"] or {})
    module_registry = dict(payloads["module_registry"] or {})
    symbol_index = dict(payloads["symbol_index"] or {})
    build_graph = dict(payloads["build_graph"] or {})
    indexes = _build_indexes(architecture_graph, module_registry, build_graph)

    symbol_rows = sorted(
        [dict(row or {}) for row in list(symbol_index.get("symbols") or [])],
        key=lambda row: (
            _token(row.get("symbol_name")),
            _norm_rel(row.get("file_path")),
            int(row.get("line_number", 1) or 1),
            _token(row.get("signature_hash")),
        ),
    )

    duplicate_groups, file_to_group_ids, file_to_symbol_names, module_pair_exact_names = _exact_duplicate_groups(
        symbol_rows=symbol_rows,
        file_to_targets=dict(indexes.get("file_to_targets") or {}),
        file_to_products=dict(indexes.get("file_to_products") or {}),
    )
    duplicate_clusters, file_to_cluster_ids, module_pair_near_names = _near_duplicate_clusters(
        symbol_rows=symbol_rows,
        file_to_targets=dict(indexes.get("file_to_targets") or {}),
        file_to_products=dict(indexes.get("file_to_products") or {}),
        repo_root=root,
    )
    ranked_groups = _ranked_duplicate_groups(
        duplicate_groups=duplicate_groups,
        docs_files=list(indexes.get("docs_files") or []),
        repo_root=root,
    )
    src_directories = _src_directories_report(
        directories=list(indexes.get("directories") or []),
        module_rows=list(indexes.get("arch_modules") or []),
        file_to_group_ids=file_to_group_ids,
        file_to_symbol_names=file_to_symbol_names,
        file_to_cluster_ids=file_to_cluster_ids,
        file_to_products=dict(indexes.get("file_to_products") or {}),
        ranked_group_rows=ranked_groups,
    )
    shadow_modules = _shadow_modules_report(
        module_rows=list(indexes.get("arch_modules") or []),
        module_pair_exact_names=module_pair_exact_names,
        module_pair_near_names=module_pair_near_names,
    )

    duplicate_impls = {
        "report_id": "xi.duplicate_impls.v1",
        "group_count": len(duplicate_groups),
        "groups": duplicate_groups,
        "deterministic_fingerprint": "",
    }
    duplicate_impls["deterministic_fingerprint"] = canonical_sha256(dict(duplicate_impls, deterministic_fingerprint=""))

    duplicate_clusters_payload = {
        "report_id": "xi.duplicate_clusters.v1",
        "cluster_count": len(duplicate_clusters),
        "clusters": duplicate_clusters,
        "deterministic_fingerprint": "",
    }
    duplicate_clusters_payload["deterministic_fingerprint"] = canonical_sha256(dict(duplicate_clusters_payload, deterministic_fingerprint=""))

    shadow_modules_payload = {
        "report_id": "xi.shadow_modules.v1",
        "shadow_count": len(shadow_modules),
        "modules": shadow_modules,
        "deterministic_fingerprint": "",
    }
    shadow_modules_payload["deterministic_fingerprint"] = canonical_sha256(dict(shadow_modules_payload, deterministic_fingerprint=""))

    src_directory_report = {
        "report_id": "xi.src_directory_report.v1",
        "directory_count": len(src_directories),
        "directories": src_directories,
        "deterministic_fingerprint": "",
    }
    src_directory_report["deterministic_fingerprint"] = canonical_sha256(dict(src_directory_report, deterministic_fingerprint=""))

    return {
        "duplicate_clusters": duplicate_clusters_payload,
        "duplicate_impls": duplicate_impls,
        "ranked_groups": ranked_groups,
        "shadow_modules": shadow_modules_payload,
        "src_directory_report": src_directory_report,
    }


def _group_by_id(snapshot: Mapping[str, object]) -> dict[str, dict]:
    groups = list(dict(snapshot.get("duplicate_impls") or {}).get("groups") or [])
    return {_token(group.get("group_id")): dict(group or {}) for group in groups}


def render_duplicate_implementations_report(snapshot: Mapping[str, object]) -> str:
    duplicate_impls = dict(snapshot.get("duplicate_impls") or {})
    duplicate_clusters = dict(snapshot.get("duplicate_clusters") or {})
    shadow_modules = dict(snapshot.get("shadow_modules") or {})
    src_report = dict(snapshot.get("src_directory_report") or {})
    ranked_groups = list(snapshot.get("ranked_groups") or [])
    groups_by_id = _group_by_id(snapshot)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-3 duplicate convergence plan",
        "",
        "# Duplicate Implementations Report",
        "",
        "- exact_duplicate_groups: `{}`".format(int(duplicate_impls.get("group_count", 0) or 0)),
        "- near_duplicate_clusters: `{}`".format(int(duplicate_clusters.get("cluster_count", 0) or 0)),
        "- shadow_module_suspects: `{}`".format(int(shadow_modules.get("shadow_count", 0) or 0)),
        "- src_directory_count: `{}`".format(int(src_report.get("directory_count", 0) or 0)),
        "",
        "## Ranked Convergence Candidates",
        "",
        "_XI-1 does not choose winners; these are evidence-ranked candidates only._",
        "",
    ]
    for index, row in enumerate(ranked_groups[:20], start=1):
        group = dict(groups_by_id.get(_token(row.get("group_id"))) or {})
        docs_refs = list(row.get("docs_refs") or [])
        lines.append(
            "{}. `{}` bucket=`{}` score=`{}`".format(
                index,
                _token(row.get("symbol_name")) or _token(group.get("group_id")),
                _token(row.get("bucket_label")),
                int(row.get("score", 0) or 0),
            )
        )
        lines.append("   duplicates: `{}` definitions across `{}` modules".format(int(group.get("definition_count", 0) or 0), len(list(group.get("module_ids") or []))))
        lines.append("   build_targets/products: `{}` / `{}`".format(", ".join(list(group.get("build_targets") or [])[:8]) or "none", ", ".join(list(group.get("products") or [])[:8]) or "none"))
        lines.append("   docs_refs: `{}`".format(", ".join(docs_refs[:4]) or "none"))
        lines.append("   architecture_placement_violation: `{}`".format("yes" if bool(row.get("placement_violation")) else "no"))
    for bucket_rank, title in ((1, "Core Semantic Engines"), (2, "Product Entrypoints And Shells"), (3, "Domain Systems"), (4, "Tools And Docs")):
        lines.extend(["", "## {}".format(title), ""])
        bucket_rows = [row for row in ranked_groups if int(row.get("bucket_rank", 4) or 4) == bucket_rank][:8]
        if not bucket_rows:
            lines.append("- none")
            continue
        for row in bucket_rows:
            group = dict(groups_by_id.get(_token(row.get("group_id"))) or {})
            lines.append(
                "- `{}` files=`{}` products=`{}` docs=`{}` placement_violation=`{}`".format(
                    _token(row.get("symbol_name")) or _token(group.get("group_id")),
                    int(group.get("definition_count", 0) or 0),
                    ",".join(list(group.get("products") or [])[:4]) or "none",
                    ",".join(list(row.get("docs_refs") or [])[:2]) or "none",
                    "yes" if bool(row.get("placement_violation")) else "no",
                )
            )
    lines.extend(
        [
            "",
            "## Future RepoX Recommendations",
            "",
            "- `INV-NO-SRC-DIRECTORY` except test-only trees.",
            "- `INV-SINGLE-SEMANTIC-ENGINE` for negotiation, overlay/merge, identity, worldgen, time-anchor, pack, and trust surfaces.",
            "- `INV-NO-DUPLICATE-SYMBOL-DEFINITIONS` across production-visible modules.",
            "",
        ]
    )
    return "\n".join(lines)


def render_src_shadow_report(snapshot: Mapping[str, object]) -> str:
    src_report = dict(snapshot.get("src_directory_report") or {})
    shadow_modules = dict(snapshot.get("shadow_modules") or {})
    report_dirs = _report_src_directories(src_report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-2 shadow-boundary audit",
        "",
        "# SRC Shadow Report",
        "",
        "- src_directory_count: `{}`".format(int(src_report.get("directory_count", 0) or 0)),
        "- shadow_module_count: `{}`".format(int(shadow_modules.get("shadow_count", 0) or 0)),
        "",
        "## Source-Like Directories",
        "",
    ]
    for row in report_dirs:
        item = dict(row or {})
        lines.append(
            "- `[{}]` `{}` files=`{}` duplicates=`{}` products=`{}`".format(
                _token(item.get("severity")),
                _token(item.get("directory_path")),
                int(item.get("file_count", 0) or 0),
                int(item.get("duplicate_group_count", 0) or 0),
                ",".join(list(item.get("impacted_products") or [])[:4]) or "none",
            )
        )
    lines.extend(["", "## Shadow Module Suspects", ""])
    modules = list(shadow_modules.get("modules") or [])
    if not modules:
        lines.append("- none")
    else:
        for row in modules[:20]:
            item = dict(row or {})
            metrics = dict(item.get("overlap_metrics") or {})
            lines.append(
                "- `{}` -> `{}` score=`{:.4f}` exact=`{}` near=`{}` products=`{}`".format(
                    _token(item.get("shadow_module_root")),
                    _token(item.get("canonical_candidate_module_id")),
                    float(metrics.get("overlap_score", 0.0) or 0.0),
                    int(item.get("exact_duplicate_symbol_count", 0) or 0),
                    int(item.get("near_duplicate_symbol_count", 0) or 0),
                    ",".join(list(item.get("impacted_products") or [])[:4]) or "none",
                )
            )
    lines.extend(
        [
            "",
            "## Future RepoX Recommendations",
            "",
            "- `INV-NO-SRC-DIRECTORY` except tests and explicitly-audited generated data roots.",
            "- `INV-SINGLE-SEMANTIC-ENGINE` to prevent shadow implementations in low-confidence or generic roots.",
            "- `INV-NO-DUPLICATE-SYMBOL-DEFINITIONS` to reduce shadow drift before XI-3 winner selection.",
            "",
        ]
    )
    return "\n".join(lines)


def render_xi_1_final(snapshot: Mapping[str, object]) -> str:
    duplicate_impls = dict(snapshot.get("duplicate_impls") or {})
    duplicate_clusters = dict(snapshot.get("duplicate_clusters") or {})
    shadow_modules = dict(snapshot.get("shadow_modules") or {})
    src_report = dict(snapshot.get("src_directory_report") or {})
    ranked_groups = list(snapshot.get("ranked_groups") or [])
    report_dirs = _report_src_directories(src_report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-2 boundary audit and XI-3 duplicate convergence",
        "",
        "# XI-1 Final",
        "",
        "- exact_duplicate_groups: `{}`".format(int(duplicate_impls.get("group_count", 0) or 0)),
        "- near_duplicate_clusters: `{}`".format(int(duplicate_clusters.get("cluster_count", 0) or 0)),
        "- src_directory_count: `{}`".format(int(src_report.get("directory_count", 0) or 0)),
        "- shadow_module_suspects: `{}`".format(int(shadow_modules.get("shadow_count", 0) or 0)),
        "",
        "## SRC Directories",
        "",
    ]
    for row in report_dirs[:25]:
        item = dict(row or {})
        lines.append("- `{}` severity=`{}` duplicates=`{}`".format(_token(item.get("directory_path")), _token(item.get("severity")), int(item.get("duplicate_group_count", 0) or 0)))
    lines.extend(["", "## Suspected Shadow Modules", ""])
    for row in list(shadow_modules.get("modules") or [])[:20]:
        item = dict(row or {})
        metrics = dict(item.get("overlap_metrics") or {})
        lines.append(
            "- `{}` -> `{}` score=`{:.4f}` exact=`{}` near=`{}`".format(
                _token(item.get("shadow_module_root")),
                _token(item.get("canonical_candidate_module_id")),
                float(metrics.get("overlap_score", 0.0) or 0.0),
                int(item.get("exact_duplicate_symbol_count", 0) or 0),
                int(item.get("near_duplicate_symbol_count", 0) or 0),
            )
        )
    lines.extend(["", "## Top 20 Convergence Candidates", ""])
    for index, row in enumerate(ranked_groups[:20], start=1):
        lines.append(
            "{}. `{}` bucket=`{}` score=`{}`".format(
                index,
                _token(row.get("symbol_name")) or _token(row.get("group_id")),
                _token(row.get("bucket_label")),
                int(row.get("score", 0) or 0),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_duplicate_impl_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    json_targets = {
        DUPLICATE_IMPLS_REL: dict(snapshot.get("duplicate_impls") or {}),
        SHADOW_MODULES_REL: dict(snapshot.get("shadow_modules") or {}),
        DUPLICATE_CLUSTERS_REL: dict(snapshot.get("duplicate_clusters") or {}),
        SRC_DIRECTORY_REPORT_REL: dict(snapshot.get("src_directory_report") or {}),
    }
    for rel_path, payload in json_targets.items():
        written[rel_path] = _write_canonical_json(_repo_abs(root, rel_path), payload)
    written[DUPLICATE_IMPLS_REPORT_REL] = _write_text(_repo_abs(root, DUPLICATE_IMPLS_REPORT_REL), render_duplicate_implementations_report(snapshot) + "\n")
    written[SRC_SHADOW_REPORT_REL] = _write_text(_repo_abs(root, SRC_SHADOW_REPORT_REL), render_src_shadow_report(snapshot) + "\n")
    written[XI_1_FINAL_REL] = _write_text(_repo_abs(root, XI_1_FINAL_REL), render_xi_1_final(snapshot) + "\n")
    return written


__all__ = [
    "ARCHITECTURE_GRAPH_REL",
    "BUILD_GRAPH_REL",
    "DUPLICATE_CLUSTERS_REL",
    "DUPLICATE_IMPLS_REL",
    "DUPLICATE_IMPLS_REPORT_REL",
    "INCLUDE_GRAPH_REL",
    "MODULE_DEP_GRAPH_REL",
    "MODULE_REGISTRY_REL",
    "OUTPUT_REL_PATHS",
    "SHADOW_MODULES_REL",
    "SRC_DIRECTORY_REPORT_REL",
    "SRC_SHADOW_REPORT_REL",
    "SYMBOL_INDEX_REL",
    "XI_1_FINAL_REL",
    "XiInputMissingError",
    "build_duplicate_impl_snapshot",
    "render_duplicate_implementations_report",
    "render_src_shadow_report",
    "render_xi_1_final",
    "write_duplicate_impl_snapshot",
]
