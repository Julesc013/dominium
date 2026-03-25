"""Deterministic XI-2 implementation scoring helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


DUPLICATE_IMPLS_REL = "data/audit/duplicate_impls.json"
DUPLICATE_CLUSTERS_REL = "data/audit/duplicate_clusters.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"
INCLUDE_GRAPH_REL = "data/audit/include_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"

IMPLEMENTATION_SCORES_REL = "data/analysis/implementation_scores.json"
DUPLICATE_CLUSTER_RANKINGS_REL = "data/analysis/duplicate_cluster_rankings.json"
IMPLEMENTATION_SCORECARD_REL = "docs/audit/IMPLEMENTATION_SCORECARD.md"
XI_2_FINAL_REL = "docs/audit/XI_2_FINAL.md"

OUTPUT_REL_PATHS = {
    IMPLEMENTATION_SCORES_REL,
    DUPLICATE_CLUSTER_RANKINGS_REL,
    IMPLEMENTATION_SCORECARD_REL,
    XI_2_FINAL_REL,
}

REQUIRED_INPUTS = {
    "architecture_graph": ARCHITECTURE_GRAPH_REL,
    "build_graph": BUILD_GRAPH_REL,
    "duplicate_clusters": DUPLICATE_CLUSTERS_REL,
    "duplicate_impls": DUPLICATE_IMPLS_REL,
    "include_graph": INCLUDE_GRAPH_REL,
    "module_registry": MODULE_REGISTRY_REL,
    "symbol_index": SYMBOL_INDEX_REL,
}

DOC_REPORT_DATE = "2026-03-26"
ENTRYPOINT_PRODUCTS = {"app", "client", "launcher", "server", "setup"}
TEST_PATH_PREFIXES = ("tests/", "game/tests/", "tools/xstack/testx/tests/", "Testing/")
SOURCE_LIKE_DIRS = {"src", "source", "Sources", "Source"}
RUNTIME_PATH_PREFIXES = ("client/", "engine/", "game/", "launcher/", "server/", "setup/", "src/", "worldgen/")
NON_RUNTIME_TOOL_PATH_PREFIXES = ("tools/auditx/", "tools/review/", "tools/xstack/testx/tests/")
HIGH_CONFIDENCE_SCORE = 78.0
MEDIUM_CONFIDENCE_SCORE = 62.0
HIGH_CONFIDENCE_GAP = 8.0
MEDIUM_CONFIDENCE_GAP = 4.0
HIGHLIGHT_FILE_CAP = 2
HIGHLIGHT_MODULE_CAP = 3

WEIGHTS = {
    "architecture": 2,
    "dependency": 2,
    "determinism": 4,
    "documentation": 1,
    "integration": 3,
    "tests": 2,
}
TOTAL_WEIGHT = sum(WEIGHTS.values())

QUERY_STOPWORDS = {
    "and",
    "apply",
    "arg",
    "args",
    "base",
    "builder",
    "build",
    "bundle",
    "bytes",
    "canonical",
    "check",
    "clean",
    "cli",
    "common",
    "config",
    "context",
    "copy",
    "core",
    "current",
    "data",
    "default",
    "descriptor",
    "deterministic",
    "diagnostic",
    "dir",
    "directory",
    "dispatch",
    "doc",
    "docs",
    "dump",
    "ensure",
    "entry",
    "event",
    "file",
    "files",
    "find",
    "fingerprint",
    "format",
    "hash",
    "helper",
    "id",
    "ids",
    "info",
    "init",
    "json",
    "kind",
    "kinds",
    "layout",
    "list",
    "load",
    "log",
    "main",
    "manifest",
    "map",
    "meta",
    "mode",
    "name",
    "names",
    "norm",
    "normalize",
    "open",
    "output",
    "path",
    "paths",
    "payload",
    "plan",
    "policy",
    "print",
    "profile",
    "read",
    "registry",
    "rel",
    "render",
    "report",
    "resolve",
    "root",
    "row",
    "rows",
    "run",
    "save",
    "schema",
    "score",
    "select",
    "set",
    "sort",
    "sorted",
    "state",
    "status",
    "store",
    "string",
    "strings",
    "surface",
    "text",
    "token",
    "tokens",
    "tool",
    "tools",
    "tree",
    "tuple",
    "ui",
    "usage",
    "value",
    "values",
    "version",
    "view",
    "window",
    "write",
}

SEMANTIC_QUERY_TERMS = {
    "anchor",
    "appshell",
    "attach",
    "bootstrap",
    "contract",
    "epoch",
    "geo",
    "handshake",
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
    "protocol",
    "rng",
    "schema",
    "seed",
    "stream",
    "supervisor",
    "time",
    "trust",
    "verify",
    "worldgen",
}

FOCUS_TAGS = (
    ("worldgen", ("worldgen", "seed", "geo", "earth", "hydrology")),
    ("contracts", ("contract", "schema", "compat", "refusal")),
    ("protocol_negotiation", ("negotiat", "protocol", "handshake", "cap_neg")),
    ("pack_verification", ("pack", "bundle", "artifact", "manifest", "compat")),
    ("trust_enforcement", ("trust", "belief", "receipt", "verify")),
    ("time_anchors", ("anchor", "epoch", "time")),
)
FOCUS_KEYWORDS = {label: keywords for label, keywords in FOCUS_TAGS}

GENERIC_HIGHLIGHT_SYMBOLS = {
    "_ensure_dir",
    "_error",
    "_load_json",
    "_norm",
    "_read",
    "_read_json",
    "_read_text",
    "_run",
    "_rows",
    "_write",
    "_write_json",
    "_write_text",
    "check_list",
    "check_version",
    "copy_dir",
    "entries",
    "ensure_dir",
    "get",
    "has",
    "is_dir",
    "list_dir",
    "load_json",
    "main",
    "norm",
    "path_join",
    "read_file_text",
    "read_json",
    "read_text",
    "report_json_path",
    "run",
    "usage",
    "validation",
    "void",
    "write_json",
    "write_text",
}

WALL_CLOCK_PATTERNS = (
    "clock_gettime",
    "datetime.now",
    "datetime.utcnow",
    "new date(",
    "perf_counter",
    "queryperformancecounter",
    "system.currenttimemillis",
    "time.monotonic",
    "time.perf_counter",
    "time.time",
)

RANDOM_PATTERNS = (
    "drand48",
    "math.random",
    "mt19937",
    "rand(",
    "random.",
    "random()",
    "srand(",
    "thread_rng",
    "uuid4",
)

NAMED_RNG_PATTERNS = (
    "named rng",
    "named_rng",
    "random_stream",
    "rng_",
    "stream_id",
    "stream_name",
)

NUMERIC_DISCIPLINE_PATTERNS = (
    "canonical",
    "deterministic",
    "fixed-point",
    "fixed_point",
    "permille",
    "q16",
    "q32",
)

TRUTH_PATH_HINTS = (
    "engine/",
    "game/",
    "src/control/",
    "src/core/",
    "src/geo/",
    "src/logic/",
    "src/process/",
    "src/signals/",
    "src/system/",
    "src/time/",
    "src/worldgen/",
)

CAMEL_RE_1 = re.compile(r"([a-z0-9])([A-Z])")
CAMEL_RE_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")


class XiInputMissingError(RuntimeError):
    """Raised when the required XI-1/XI-0 inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing XI inputs")
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


def _term_fragments(value: object) -> list[str]:
    raw = _norm_rel(value)
    if not raw:
        return []
    expanded = CAMEL_RE_1.sub(r"\1 \2", raw)
    expanded = CAMEL_RE_2.sub(r"\1 \2", expanded)
    expanded = re.sub(r"[^A-Za-z0-9]+", " ", expanded)
    return [part.lower() for part in expanded.split() if part]


def _simple_symbol_name(symbol_name: object) -> str:
    token = _token(symbol_name)
    if not token:
        return ""
    token = token.split("::")[-1]
    token = token.split(".")[-1]
    return token


def _query_terms(symbol_name: object, file_path: object, module_id: object) -> list[str]:
    terms = []
    for value in (_simple_symbol_name(symbol_name), os.path.basename(_norm_rel(file_path)), _token(module_id).split(".")[-1]):
        for term in _term_fragments(value):
            if term in SEMANTIC_QUERY_TERMS:
                terms.append(term)
                continue
            if len(term) < 3 or term in QUERY_STOPWORDS:
                continue
            terms.append(term)
    deduped = []
    seen = set()
    for term in terms:
        if term in seen:
            continue
        deduped.append(term)
        seen.add(term)
    return deduped[:5]


def _tests_only_path(path: object) -> bool:
    rel_path = _norm_rel(path)
    return any(rel_path.startswith(prefix) for prefix in TEST_PATH_PREFIXES)


def _source_like_path(path: object) -> bool:
    rel_path = _norm_rel(path).strip("/")
    parts = [part for part in rel_path.split("/") if part]
    return any(part in SOURCE_LIKE_DIRS for part in parts)


def _canonical_path_preference(file_path: str, module_row: Mapping[str, object] | None) -> bool:
    module_root = _norm_rel(dict(module_row or {}).get("module_root"))
    domain = _token(dict(module_row or {}).get("domain"))
    return bool(module_root and _norm_rel(file_path).startswith(module_root) and not _source_like_path(file_path) and domain not in {"docs", "tests", "unknown"})


def _normalized_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _final_score(axis_scores: Mapping[str, float]) -> float:
    weighted = sum(float(axis_scores.get(key, 0.0) or 0.0) * weight for key, weight in sorted(WEIGHTS.items()))
    return round((weighted / float(TOTAL_WEIGHT)) * 100.0, 2)


def _payload_with_fingerprint(payload: Mapping[str, object]) -> dict[str, object]:
    result = dict(payload)
    result["deterministic_fingerprint"] = canonical_sha256(result)
    return result


def _focus_tags_for_values(*values: object) -> list[str]:
    haystack = " ".join(_term_fragments(" ".join(_norm_rel(value) for value in values if _norm_rel(value))))
    matches = []
    for label, keywords in FOCUS_TAGS:
        if any(keyword in haystack for keyword in keywords):
            matches.append(label)
    return matches


def _cluster_candidate_keys(cluster: Mapping[str, object]) -> list[tuple[str, str, str]]:
    cluster_symbol = _token(cluster.get("symbol_name"))
    keys = []
    seen = set()
    for definition in list(cluster.get("definitions") or []):
        defn = dict(definition or {})
        key = (
            _token(defn.get("symbol_name")) or cluster_symbol,
            _norm_rel(defn.get("file_path")),
            _token(defn.get("module_id")),
        )
        if not key[1] or key in seen:
            continue
        seen.add(key)
        keys.append(key)
    return sorted(keys, key=lambda value: (value[1], value[0], value[2]))


def _build_indexes(
    architecture_graph: Mapping[str, object],
    module_registry: Mapping[str, object],
    build_graph: Mapping[str, object],
    include_graph: Mapping[str, object],
    symbol_index: Mapping[str, object],
) -> dict[str, object]:
    module_rows = sorted(
        [dict(row or {}) for row in list(architecture_graph.get("modules") or module_registry.get("modules") or [])],
        key=lambda row: (_token(row.get("module_id")), _norm_rel(row.get("module_root"))),
    )
    module_by_id = {_token(row.get("module_id")): row for row in module_rows if _token(row.get("module_id"))}
    file_to_module: dict[str, str] = {}
    for row in module_rows:
        module_id = _token(row.get("module_id"))
        for rel_path in sorted({_norm_rel(path) for path in list(row.get("owned_files") or []) if _norm_rel(path)}):
            file_to_module.setdefault(rel_path, module_id)

    target_rows = sorted(
        [dict(row or {}) for row in list(build_graph.get("targets") or [])],
        key=lambda row: (_token(row.get("target_id")), _token(row.get("product_id"))),
    )
    file_to_targets: dict[str, set[str]] = defaultdict(set)
    file_to_products: dict[str, set[str]] = defaultdict(set)
    target_to_product: dict[str, str] = {}
    for row in target_rows:
        target_id = _token(row.get("target_id"))
        product_id = _token(row.get("product_id"))
        if target_id:
            target_to_product[target_id] = product_id
        for rel_path in sorted({_norm_rel(path) for path in list(row.get("sources") or []) if _norm_rel(path)}):
            if target_id:
                file_to_targets[rel_path].add(target_id)
            if product_id:
                file_to_products[rel_path].add(product_id)

    include_rows = sorted(
        [dict(row or {}) for row in list(include_graph.get("edges") or [])],
        key=lambda row: (_norm_rel(row.get("from")), _norm_rel(row.get("to")), _token(row.get("dependency_kind"))),
    )
    outgoing_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
    incoming_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in include_rows:
        from_path = _norm_rel(row.get("from"))
        to_path = _norm_rel(row.get("to"))
        edge_row = {
            "dependency_kind": _token(row.get("dependency_kind")),
            "from": from_path,
            "raw": _token(row.get("raw")),
            "to": to_path,
        }
        if from_path:
            outgoing_edges[from_path].append(edge_row)
        if to_path:
            incoming_edges[to_path].append(edge_row)

    symbol_rows = sorted(
        [dict(row or {}) for row in list(symbol_index.get("symbols") or [])],
        key=lambda row: (
            _token(row.get("symbol_name")),
            _norm_rel(row.get("file_path")),
            int(row.get("line_number", 1) or 1),
            _token(row.get("module_id")),
        ),
    )
    symbol_files = sorted({_norm_rel(row.get("file_path")) for row in symbol_rows if _norm_rel(row.get("file_path"))})

    docs_files = sorted(
        {
            rel_path
            for row in module_rows
            if _norm_rel(row.get("module_root")).startswith("docs") or _token(row.get("domain")) == "docs"
            for rel_path in list(row.get("owned_files") or [])
            if _norm_rel(rel_path).endswith(".md")
        }
    )
    registry_schema_files = sorted(
        {
            rel_path
            for row in module_rows
            for rel_path in list(row.get("owned_files") or [])
            if _norm_rel(rel_path).startswith(("schema/", "schemas/"))
            or "registry" in os.path.basename(_norm_rel(rel_path)).lower()
            or (
                _norm_rel(rel_path).endswith((".json", ".toml", ".yaml", ".yml"))
                and _norm_rel(rel_path).startswith(("schema/", "schemas/", "data/", "packs/", "src/"))
            )
        }
    )

    return {
        "docs_files": docs_files,
        "file_to_module": {key: value for key, value in sorted(file_to_module.items())},
        "file_to_products": {key: sorted(values) for key, values in sorted(file_to_products.items())},
        "file_to_targets": {key: sorted(values) for key, values in sorted(file_to_targets.items())},
        "incoming_edges": {key: value for key, value in sorted(incoming_edges.items())},
        "module_by_id": module_by_id,
        "module_rows": module_rows,
        "outgoing_edges": {key: value for key, value in sorted(outgoing_edges.items())},
        "registry_schema_files": registry_schema_files,
        "symbol_files": symbol_files,
        "target_to_product": target_to_product,
        "target_rows": target_rows,
    }


def _cluster_rows(duplicate_impls: Mapping[str, object], duplicate_clusters: Mapping[str, object]) -> list[dict[str, object]]:
    rows = []
    for cluster_kind, payload, cluster_key in (
        ("exact", duplicate_impls, "group_id"),
        ("near", duplicate_clusters, "cluster_id"),
    ):
        for row in list(payload.get("groups") or payload.get("clusters") or []):
            item = dict(row or {})
            cluster_id = _token(item.get(cluster_key))
            if not cluster_id:
                continue
            definitions = []
            seen_defs = set()
            for definition in list(item.get("definitions") or []):
                defn = dict(definition or {})
                key = (
                    _token(defn.get("symbol_name")) or _token(item.get("symbol_name")),
                    _norm_rel(defn.get("file_path")),
                    _token(defn.get("module_id")),
                    int(defn.get("line_number", 1) or 1),
                )
                if not key[1] or key in seen_defs:
                    continue
                seen_defs.add(key)
                definitions.append(
                    {
                        "build_targets": sorted({_token(target) for target in list(defn.get("build_targets") or []) if _token(target)}),
                        "file_path": key[1],
                        "line_number": key[3],
                        "module_id": key[2],
                        "products": sorted({_token(product) for product in list(defn.get("products") or []) if _token(product)}),
                        "symbol_kind": _token(defn.get("symbol_kind")),
                        "symbol_name": key[0],
                    }
                )
            rows.append(
                {
                    "build_targets": sorted({_token(target) for target in list(item.get("build_targets") or []) if _token(target)}),
                    "cluster_id": cluster_id,
                    "cluster_kind": cluster_kind,
                    "confidence": float(item.get("confidence", 1.0) or 1.0),
                    "definitions": sorted(
                        definitions,
                        key=lambda defn: (
                            _norm_rel(defn.get("file_path")),
                            _token(defn.get("symbol_name")),
                            int(defn.get("line_number", 1) or 1),
                        ),
                    ),
                    "module_ids": sorted({_token(module_id) for module_id in list(item.get("module_ids") or []) if _token(module_id)}),
                    "products": sorted({_token(product) for product in list(item.get("products") or []) if _token(product)}),
                    "symbol_name": _token(item.get("symbol_name")),
                }
            )
    return sorted(rows, key=lambda row: (_token(row.get("cluster_id")), _token(row.get("symbol_name")), _token(row.get("cluster_kind"))))


def _build_search_indexes(repo_root: str, indexes: Mapping[str, object]) -> dict[str, dict[str, set[str]]]:
    root = _repo_root(repo_root)
    symbol_files = sorted({_norm_rel(path) for path in list(indexes.get("symbol_files") or []) if _norm_rel(path)})
    docs_files = sorted({_norm_rel(path) for path in list(indexes.get("docs_files") or []) if _norm_rel(path)})
    registry_schema_files = sorted({_norm_rel(path) for path in list(indexes.get("registry_schema_files") or []) if _norm_rel(path)})

    source_files = [path for path in symbol_files if not _tests_only_path(path) and not path.startswith("docs/")]
    test_files = [path for path in symbol_files if _tests_only_path(path)]
    doc_files = docs_files
    registry_files = [path for path in registry_schema_files if not path.startswith("docs/")]

    grouped_files = {
        "docs": sorted(set(doc_files)),
        "registry": sorted(set(registry_files)),
        "source": sorted(set(source_files)),
        "tests": sorted(set(test_files)),
    }
    indexes_by_group: dict[str, dict[str, set[str]]] = {}
    for group_name, files in sorted(grouped_files.items()):
        token_to_files: dict[str, set[str]] = defaultdict(set)
        for rel_path in files:
            text = _read_text(_repo_abs(root, rel_path))
            if not text:
                continue
            for term in sorted(set(_term_fragments(text))):
                token_to_files[term].add(rel_path)
        indexes_by_group[group_name] = token_to_files
    return indexes_by_group


def _search_files(token_index: Mapping[str, set[str]], query_terms: Sequence[str], cache: dict[tuple[str, ...], list[str]]) -> list[str]:
    normalized_terms = tuple(sorted({term for term in query_terms if _token(term)}))
    if not normalized_terms:
        return []
    cached = cache.get(normalized_terms)
    if cached is not None:
        return list(cached)
    file_sets = [set(token_index.get(term) or set()) for term in normalized_terms]
    if not file_sets or any(not file_set for file_set in file_sets):
        cache[normalized_terms] = []
        return []
    ordered_sets = sorted(file_sets, key=len)
    matches = set(ordered_sets[0])
    for file_set in ordered_sets[1:]:
        matches &= file_set
        if not matches:
            break
    result = sorted(matches)
    cache[normalized_terms] = result
    return list(result)


def _determinism_score(file_path: str, module_id: str, file_text: str) -> tuple[float, list[str]]:
    normalized = file_text.lower()
    evidence = []
    truth_sensitive = _norm_rel(file_path).startswith(TRUTH_PATH_HINTS) or any(hint in module_id for hint in ("control", "geo", "logic", "process", "signal", "system", "time", "trust", "worldgen"))
    wall_clock = any(pattern in normalized for pattern in WALL_CLOCK_PATTERNS)
    random_bad = any(pattern in normalized for pattern in RANDOM_PATTERNS)
    named_rng = any(pattern in normalized for pattern in NAMED_RNG_PATTERNS)
    numeric_good = any(pattern in normalized for pattern in NUMERIC_DISCIPLINE_PATTERNS)
    float_bad = truth_sensitive and bool(re.search(r"\b(float|double)\b", normalized))
    score = 1.0
    if wall_clock:
        score -= 0.45
        evidence.append("wall_clock_detected")
    if random_bad:
        score -= 0.35
        evidence.append("anonymous_rng_detected")
    if float_bad:
        score -= 0.25
        evidence.append("float_in_truth_path")
    if named_rng:
        score += 0.10
        evidence.append("named_rng_marker")
    if numeric_good:
        score += 0.05
        evidence.append("numeric_discipline_marker")
    return _normalized_score(score), evidence


def _architecture_score(file_path: str, module_row: Mapping[str, object] | None) -> tuple[float, bool]:
    module = dict(module_row or {})
    module_root = _norm_rel(module.get("module_root"))
    domain = _token(module.get("domain"))
    aligned_root = bool(module_root and _norm_rel(file_path).startswith(module_root))
    source_like = _source_like_path(file_path)
    unknown_domain = domain == "unknown" or _token(module.get("module_id")).startswith("unknown.")
    docs_or_tests = domain in {"docs", "tests"}
    confidence = float(module.get("confidence", 0.0) or 0.0)
    score = 0.0
    score += 0.45 if aligned_root else 0.15
    score += 0.20 if confidence >= 0.9 else 0.10 if confidence >= 0.75 else 0.0
    score += 0.20 if not source_like else 0.0
    score += 0.15 if domain not in {"archive", "dist", "docs", "tests", "unknown"} else 0.0
    if source_like:
        score -= 0.20
    if unknown_domain:
        score -= 0.15
    if docs_or_tests:
        score -= 0.20
    return _normalized_score(score), _canonical_path_preference(file_path, module_row)


def _dependency_metrics(
    file_path: str,
    module_id: str,
    module_row: Mapping[str, object] | None,
    indexes: Mapping[str, object],
) -> tuple[float, int, list[str]]:
    outgoing = [dict(row or {}) for row in list(dict(indexes.get("outgoing_edges") or {}).get(_norm_rel(file_path)) or [])]
    file_to_module = dict(indexes.get("file_to_module") or {})
    candidate_domain = _token(dict(module_row or {}).get("domain"))
    dependency_edges = sorted({_norm_rel(row.get("to")) for row in outgoing if _norm_rel(row.get("to")) and not _norm_rel(row.get("to")).startswith(("external:", "module:"))})
    external_module_deps = 0
    forbidden_deps = 0
    for dep_path in dependency_edges:
        dep_module_id = _token(file_to_module.get(dep_path))
        dep_domain = _token(dict(dict(indexes.get("module_by_id") or {}).get(dep_module_id) or {}).get("domain"))
        if dep_module_id and dep_module_id != module_id:
            external_module_deps += 1
        if _tests_only_path(dep_path) or dep_domain in {"docs", "tests"}:
            forbidden_deps += 1
        elif candidate_domain not in {"docs", "tests", "tools"} and dep_path.startswith("tools/") and "compatx/canonical_json.py" not in dep_path:
            forbidden_deps += 1
    dependency_complexity = len(dependency_edges) + external_module_deps * 2 + forbidden_deps * 3
    score = 1.0
    score -= min(0.25, len(dependency_edges) / 24.0)
    score -= min(0.30, external_module_deps / 10.0)
    score -= min(0.40, forbidden_deps * 0.20)
    if not dependency_edges:
        score += 0.10
    return _normalized_score(score), dependency_complexity, dependency_edges


def _documentation_metrics(
    query_terms: Sequence[str],
    file_path: str,
    search_indexes: Mapping[str, Mapping[str, set[str]]],
    search_cache: dict[str, dict[tuple[str, ...], list[str]]],
) -> tuple[float, list[str], list[str]]:
    doc_refs = _search_files(dict(search_indexes.get("docs") or {}), query_terms, search_cache.setdefault("docs", {}))
    registry_refs = _search_files(dict(search_indexes.get("registry") or {}), query_terms, search_cache.setdefault("registry", {}))
    doc_refs = [path for path in doc_refs if path != _norm_rel(file_path)]
    registry_refs = [path for path in registry_refs if path != _norm_rel(file_path)]
    score = min(1.0, (len(doc_refs) + len(registry_refs) * 1.5) / 6.0)
    return _normalized_score(score), doc_refs[:8], registry_refs[:8]


def _test_score(
    query_terms: Sequence[str],
    file_path: str,
    search_indexes: Mapping[str, Mapping[str, set[str]]],
    search_cache: dict[str, dict[tuple[str, ...], list[str]]],
) -> tuple[float, list[str]]:
    test_refs = _search_files(dict(search_indexes.get("tests") or {}), query_terms, search_cache.setdefault("tests", {}))
    test_refs = [path for path in test_refs if path != _norm_rel(file_path)]
    score = min(1.0, len(test_refs) / 6.0)
    return _normalized_score(score), test_refs[:8]


def _integration_score(
    file_path: str,
    query_terms: Sequence[str],
    indexes: Mapping[str, object],
    search_indexes: Mapping[str, Mapping[str, set[str]]],
    search_cache: dict[str, dict[tuple[str, ...], list[str]]],
) -> tuple[float, int, list[str], list[str]]:
    source_refs = _search_files(dict(search_indexes.get("source") or {}), query_terms, search_cache.setdefault("source", {}))
    incoming = [
        _norm_rel(row.get("from"))
        for row in list(dict(indexes.get("incoming_edges") or {}).get(_norm_rel(file_path)) or [])
        if _norm_rel(row.get("from")) and not _norm_rel(row.get("from")).startswith(("external:", "module:"))
    ]
    source_refs = [path for path in source_refs if path != _norm_rel(file_path)]
    incoming_refs = [path for path in sorted(set(incoming)) if path != _norm_rel(file_path)]
    call_site_paths = sorted(set(source_refs) | set(incoming_refs))
    build_targets = sorted({_token(target) for target in list(dict(indexes.get("file_to_targets") or {}).get(_norm_rel(file_path)) or []) if _token(target)})
    build_products = sorted({_token(product) for product in list(dict(indexes.get("file_to_products") or {}).get(_norm_rel(file_path)) or []) if _token(product)})
    entrypoint_overlap = bool(set(build_products) & ENTRYPOINT_PRODUCTS)
    score = (
        min(1.0, len(call_site_paths) / 10.0) * 0.45
        + min(1.0, len(incoming_refs) / 8.0) * 0.20
        + min(1.0, len(build_targets) / 4.0) * 0.20
        + (0.15 if entrypoint_overlap else 0.0)
    )
    return _normalized_score(score), len(call_site_paths), build_targets, build_products


def _scored_candidates(
    repo_root: str,
    cluster_rows: Sequence[Mapping[str, object]],
    indexes: Mapping[str, object],
) -> dict[tuple[str, str, str], dict[str, object]]:
    root = _repo_root(repo_root)
    unique_candidates = sorted(
        {
            (
                _token(definition.get("symbol_name")) or _token(cluster.get("symbol_name")),
                _norm_rel(definition.get("file_path")),
                _token(definition.get("module_id")),
            )
            for cluster in cluster_rows
            for definition in list(cluster.get("definitions") or [])
            if _norm_rel(definition.get("file_path"))
        },
        key=lambda row: (row[1], row[0], row[2]),
    )
    search_indexes = _build_search_indexes(root, indexes)
    search_cache: dict[str, dict[tuple[str, ...], list[str]]] = {}
    module_by_id = dict(indexes.get("module_by_id") or {})
    scored: dict[tuple[str, str, str], dict[str, object]] = {}
    for symbol_name, file_path, module_id in unique_candidates:
        file_text = _read_text(_repo_abs(root, file_path))
        module_row = dict(module_by_id.get(module_id) or {})
        query_terms = _query_terms(symbol_name, file_path, module_id)
        integration_score, number_of_call_sites, build_targets, build_products = _integration_score(file_path, query_terms, indexes, search_indexes, search_cache)
        determinism_score, determinism_evidence = _determinism_score(file_path, module_id, file_text)
        test_score, test_refs = _test_score(query_terms, file_path, search_indexes, search_cache)
        architecture_score, canonical_module_path_preference = _architecture_score(file_path, module_row)
        dependency_score, dependency_complexity, dependency_edges = _dependency_metrics(file_path, module_id, module_row, indexes)
        documentation_score, docs_refs, registry_refs = _documentation_metrics(query_terms, file_path, search_indexes, search_cache)
        axis_scores = {
            "architecture": architecture_score,
            "dependency": dependency_score,
            "determinism": determinism_score,
            "documentation": documentation_score,
            "integration": integration_score,
            "tests": test_score,
        }
        scored[(symbol_name, file_path, module_id)] = {
            "architecture_score": architecture_score,
            "build_products_using_file": build_products,
            "build_targets_using_file": build_targets,
            "canonical_module_path_preference": canonical_module_path_preference,
            "dependency_complexity": dependency_complexity,
            "dependency_edges": dependency_edges,
            "dependency_score": dependency_score,
            "determinism_evidence": determinism_evidence,
            "determinism_score": determinism_score,
            "docs_referencing_symbol": docs_refs,
            "documentation_score": documentation_score,
            "file_path": file_path,
            "integration_score": integration_score,
            "module_id": module_id,
            "number_of_call_sites": number_of_call_sites,
            "query_terms": query_terms,
            "registry_references": registry_refs,
            "symbol_name": symbol_name,
            "test_references": test_refs,
            "test_score": test_score,
            "total_score": _final_score(axis_scores),
        }
    return scored


def _flatten_implementation_scores(
    cluster_rows: Sequence[Mapping[str, object]],
    scored_candidates: Mapping[tuple[str, str, str], Mapping[str, object]],
) -> list[dict[str, object]]:
    rows = []
    for cluster in cluster_rows:
        cluster_id = _token(cluster.get("cluster_id"))
        cluster_kind = _token(cluster.get("cluster_kind"))
        symbol_name = _token(cluster.get("symbol_name"))
        focus_tags = _focus_tags_for_values(symbol_name, " ".join(list(cluster.get("module_ids") or [])), " ".join(list(cluster.get("products") or [])))
        for key in _cluster_candidate_keys(cluster):
            score_row = dict(scored_candidates.get(key) or {})
            if not score_row:
                continue
            rows.append(
                {
                    "architecture_score": float(score_row.get("architecture_score", 0.0) or 0.0),
                    "build_targets_using_file": list(score_row.get("build_targets_using_file") or []),
                    "cluster_id": cluster_id,
                    "cluster_kind": cluster_kind,
                    "dependency_complexity": int(score_row.get("dependency_complexity", 0) or 0),
                    "dependency_edges": list(score_row.get("dependency_edges") or []),
                    "dependency_score": float(score_row.get("dependency_score", 0.0) or 0.0),
                    "determinism_evidence": list(score_row.get("determinism_evidence") or []),
                    "determinism_score": float(score_row.get("determinism_score", 0.0) or 0.0),
                    "docs_referencing_symbol": list(score_row.get("docs_referencing_symbol") or []),
                    "documentation_score": float(score_row.get("documentation_score", 0.0) or 0.0),
                    "file_path": key[1],
                    "focus_tags": focus_tags,
                    "integration_score": float(score_row.get("integration_score", 0.0) or 0.0),
                    "module_id": key[2],
                    "number_of_call_sites": int(score_row.get("number_of_call_sites", 0) or 0),
                    "symbol_name": key[0],
                    "test_score": float(score_row.get("test_score", 0.0) or 0.0),
                    "total_score": float(score_row.get("total_score", 0.0) or 0.0),
                }
            )
    return sorted(rows, key=lambda row: (_token(row.get("cluster_id")), _norm_rel(row.get("file_path")), _token(row.get("symbol_name"))))


def _rank_clusters(
    cluster_rows: Sequence[Mapping[str, object]],
    scored_candidates: Mapping[tuple[str, str, str], Mapping[str, object]],
) -> list[dict[str, object]]:
    ranked_clusters = []
    for cluster in cluster_rows:
        cluster_id = _token(cluster.get("cluster_id"))
        symbol_name = _token(cluster.get("symbol_name"))
        candidate_rows = []
        for key in _cluster_candidate_keys(cluster):
            score_row = dict(scored_candidates.get(key) or {})
            if not score_row:
                continue
            candidate_rows.append(
                {
                    "architecture_score": float(score_row.get("architecture_score", 0.0) or 0.0),
                    "build_targets_using_file": list(score_row.get("build_targets_using_file") or []),
                    "canonical_module_path_preference": bool(score_row.get("canonical_module_path_preference")),
                    "dependency_complexity": int(score_row.get("dependency_complexity", 0) or 0),
                    "dependency_score": float(score_row.get("dependency_score", 0.0) or 0.0),
                    "docs_referencing_symbol": list(score_row.get("docs_referencing_symbol") or []),
                    "file_path": key[1],
                    "integration_score": float(score_row.get("integration_score", 0.0) or 0.0),
                    "module_id": key[2],
                    "number_of_call_sites": int(score_row.get("number_of_call_sites", 0) or 0),
                    "symbol_name": key[0],
                    "total_score": float(score_row.get("total_score", 0.0) or 0.0),
                }
            )
        ranked_candidates = sorted(
            candidate_rows,
            key=lambda row: (
                -float(row.get("total_score", 0.0) or 0.0),
                int(row.get("dependency_complexity", 0) or 0),
                -int(bool(row.get("canonical_module_path_preference"))),
                _norm_rel(row.get("file_path")),
            ),
        )
        top_score = float(ranked_candidates[0].get("total_score", 0.0) or 0.0) if ranked_candidates else 0.0
        second_score = float(ranked_candidates[1].get("total_score", 0.0) or 0.0) if len(ranked_candidates) > 1 else 0.0
        score_gap = round(top_score - second_score, 2)
        if top_score >= HIGH_CONFIDENCE_SCORE and score_gap >= HIGH_CONFIDENCE_GAP:
            confidence_class = "high"
        elif top_score >= MEDIUM_CONFIDENCE_SCORE and score_gap >= MEDIUM_CONFIDENCE_GAP:
            confidence_class = "medium"
        else:
            confidence_class = "low"
        ranked_clusters.append(
            {
                "cluster_id": cluster_id,
                "cluster_kind": _token(cluster.get("cluster_kind")),
                "confidence_class": confidence_class,
                "focus_tags": _focus_tags_for_values(symbol_name, " ".join(list(cluster.get("module_ids") or [])), " ".join(_norm_rel(dict(row or {}).get("file_path")) for row in list(cluster.get("definitions") or []))),
                "ranked_candidates": ranked_candidates,
                "score_gap": score_gap,
                "symbol_name": symbol_name,
            }
        )
    return sorted(ranked_clusters, key=lambda row: _token(row.get("cluster_id")))


def _source_like_dir_summary(score_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    aggregates: dict[str, dict[str, object]] = {}
    for row in score_rows:
        file_path = _norm_rel(row.get("file_path"))
        if not file_path.startswith("src/"):
            continue
        parts = file_path.split("/")
        bucket = "src" if len(parts) < 2 else "/".join(parts[:2])
        entry = aggregates.setdefault(
            bucket,
            {
                "candidate_count": 0,
                "directory_path": bucket,
                "low_arch_count": 0,
                "max_score": 0.0,
                "score_total": 0.0,
            },
        )
        entry["candidate_count"] = int(entry.get("candidate_count", 0) or 0) + 1
        if float(row.get("architecture_score", 0.0) or 0.0) < 0.5:
            entry["low_arch_count"] = int(entry.get("low_arch_count", 0) or 0) + 1
        entry["score_total"] = float(entry.get("score_total", 0.0) or 0.0) + float(row.get("total_score", 0.0) or 0.0)
        entry["max_score"] = max(float(entry.get("max_score", 0.0) or 0.0), float(row.get("total_score", 0.0) or 0.0))
    rows = []
    for entry in aggregates.values():
        candidate_count = int(entry.get("candidate_count", 0) or 0)
        avg_score = round(float(entry.get("score_total", 0.0) or 0.0) / float(candidate_count or 1), 2)
        rows.append(
            {
                "average_score": avg_score,
                "candidate_count": candidate_count,
                "directory_path": _token(entry.get("directory_path")),
                "low_arch_count": int(entry.get("low_arch_count", 0) or 0),
                "max_score": round(float(entry.get("max_score", 0.0) or 0.0), 2),
            }
        )
    return sorted(rows, key=lambda row: (-int(row.get("candidate_count", 0) or 0), -float(row.get("average_score", 0.0) or 0.0), _token(row.get("directory_path"))))


def _module_relevance_rank(module_id: object) -> int:
    token = _token(module_id)
    if token.startswith("unknown.src."):
        return 4
    if token.startswith(("engine.", "game.", "client.", "server.", "apps.", "launcher.", "setup.")):
        return 3
    if token.startswith("tools.") and not token.startswith(("tools.auditx.", "tools.review", "tools.xstack.testx.tests")):
        return 2
    if token.startswith(("tests.", "game.tests.", "docs.", "tools.auditx.", "tools.review", "tools.xstack.testx.tests")):
        return 0
    return 1


def _module_duplication_summary(score_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    aggregates: dict[str, dict[str, object]] = {}
    for row in score_rows:
        module_id = _token(row.get("module_id"))
        if not module_id:
            continue
        entry = aggregates.setdefault(
            module_id,
            {
                "cluster_ids": set(),
                "focus_total": 0,
                "module_id": module_id,
                "score_total": 0.0,
                "score_rows": 0,
                "source_like_rows": 0,
                "test_rows": 0,
            },
        )
        entry["cluster_ids"].add(_token(row.get("cluster_id")))
        entry["focus_total"] = int(entry.get("focus_total", 0) or 0) + len(list(row.get("focus_tags") or []))
        entry["score_total"] = float(entry.get("score_total", 0.0) or 0.0) + float(row.get("total_score", 0.0) or 0.0)
        entry["score_rows"] = int(entry.get("score_rows", 0) or 0) + 1
        entry["source_like_rows"] = int(entry.get("source_like_rows", 0) or 0) + int(_source_like_path(row.get("file_path")))
        entry["test_rows"] = int(entry.get("test_rows", 0) or 0) + int(_tests_only_path(row.get("file_path")))
    rows = []
    for entry in aggregates.values():
        score_rows_count = int(entry.get("score_rows", 0) or 0)
        module_id = _token(entry.get("module_id"))
        rows.append(
            {
                "average_score": round(float(entry.get("score_total", 0.0) or 0.0) / float(score_rows_count or 1), 2),
                "cluster_count": len(set(entry.get("cluster_ids") or set())),
                "focus_total": int(entry.get("focus_total", 0) or 0),
                "module_id": module_id,
                "relevance_rank": _module_relevance_rank(module_id),
                "score_rows": score_rows_count,
                "source_like_rows": int(entry.get("source_like_rows", 0) or 0),
                "test_rows": int(entry.get("test_rows", 0) or 0),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -int(row.get("relevance_rank", 0) or 0),
            -int(row.get("cluster_count", 0) or 0),
            -int(row.get("focus_total", 0) or 0),
            -int(row.get("source_like_rows", 0) or 0),
            -int(row.get("score_rows", 0) or 0),
            _token(row.get("module_id")),
        ),
    )


def _winner_candidate(cluster_row: Mapping[str, object]) -> dict[str, object]:
    candidates = [dict(item or {}) for item in list(cluster_row.get("ranked_candidates") or [])]
    return candidates[0] if candidates else {}


def _confidence_rank(confidence_class: object) -> int:
    return {"high": 2, "medium": 1, "low": 0}.get(_token(confidence_class), -1)


def _non_runtime_tool_path(path: object) -> bool:
    return _norm_rel(path).startswith(NON_RUNTIME_TOOL_PATH_PREFIXES)


def _runtime_path_rank(path: object) -> int:
    rel_path = _norm_rel(path)
    if not rel_path or _tests_only_path(rel_path):
        return 0
    if rel_path.startswith(RUNTIME_PATH_PREFIXES):
        return 3
    if rel_path.startswith("tools/"):
        return 1
    return 2


def _generic_highlight_symbol(symbol_name: object) -> bool:
    token = _simple_symbol_name(symbol_name)
    lowered = token.lower()
    if not lowered or len(lowered) <= 2:
        return True
    if lowered in GENERIC_HIGHLIGHT_SYMBOLS:
        return True
    fragments = [fragment for fragment in _term_fragments(lowered) if fragment not in QUERY_STOPWORDS]
    return not fragments


def _focus_specificity_for_tag(symbol_name: object, file_path: object, module_id: object, tag: str) -> int:
    keywords = tuple(FOCUS_KEYWORDS.get(tag) or ())
    if not keywords:
        return 0
    symbol_terms = set(_term_fragments(_simple_symbol_name(symbol_name)))
    path_terms = set(_term_fragments(_norm_rel(file_path)))
    module_terms = set(_term_fragments(_token(module_id)))
    if any(any(keyword in term for term in symbol_terms) for keyword in keywords):
        return 3
    if any(any(keyword in term for term in path_terms) for keyword in keywords):
        return 2
    if any(any(keyword in term for term in module_terms) for keyword in keywords):
        return 1
    return 0


def _cluster_highlight_metrics(cluster_row: Mapping[str, object]) -> dict[str, object]:
    winner = _winner_candidate(cluster_row)
    file_path = _norm_rel(winner.get("file_path"))
    module_id = _token(winner.get("module_id"))
    symbol_name = _token(cluster_row.get("symbol_name")) or _token(winner.get("symbol_name"))
    focus_tags = [_token(tag) for tag in list(cluster_row.get("focus_tags") or []) if _token(tag)]
    focus_specificity = sum(_focus_specificity_for_tag(symbol_name, file_path, module_id, tag) for tag in focus_tags)
    return {
        "canonical_path": bool(winner.get("canonical_module_path_preference")),
        "cluster_id": _token(cluster_row.get("cluster_id")),
        "cluster_kind": _token(cluster_row.get("cluster_kind")),
        "confidence_class": _token(cluster_row.get("confidence_class")),
        "confidence_rank": _confidence_rank(cluster_row.get("confidence_class")),
        "dependency_complexity": int(winner.get("dependency_complexity", 0) or 0),
        "file_path": file_path,
        "focus_count": len(focus_tags),
        "focus_specificity": focus_specificity,
        "focus_tags": focus_tags,
        "generic_symbol": _generic_highlight_symbol(symbol_name),
        "module_id": module_id,
        "number_of_call_sites": int(winner.get("number_of_call_sites", 0) or 0),
        "non_runtime_tool": _non_runtime_tool_path(file_path),
        "runtime_rank": _runtime_path_rank(file_path),
        "score_gap": float(cluster_row.get("score_gap", 0.0) or 0.0),
        "symbol_name": symbol_name,
        "tests_only": _tests_only_path(file_path),
        "total_score": float(winner.get("total_score", 0.0) or 0.0),
        "winner_key": (symbol_name, file_path, module_id),
    }


def _highlight_sort_key(cluster_row: Mapping[str, object]) -> tuple[object, ...]:
    metrics = _cluster_highlight_metrics(cluster_row)
    return (
        -int(metrics.get("confidence_rank", -1) or -1),
        -int(_token(metrics.get("cluster_kind")) == "exact"),
        -int(metrics.get("focus_specificity", 0) or 0),
        -int(metrics.get("focus_count", 0) or 0),
        -int(metrics.get("runtime_rank", 0) or 0),
        -int(not bool(metrics.get("tests_only"))),
        -int(not bool(metrics.get("non_runtime_tool"))),
        -int(not bool(metrics.get("generic_symbol"))),
        -int(bool(metrics.get("canonical_path"))),
        -float(metrics.get("total_score", 0.0) or 0.0),
        -float(metrics.get("score_gap", 0.0) or 0.0),
        -int(metrics.get("number_of_call_sites", 0) or 0),
        int(metrics.get("dependency_complexity", 0) or 0),
        _token(metrics.get("cluster_id")),
    )


def _manual_review_sort_key(cluster_row: Mapping[str, object]) -> tuple[object, ...]:
    metrics = _cluster_highlight_metrics(cluster_row)
    return (
        -int(metrics.get("focus_specificity", 0) or 0),
        -int(metrics.get("focus_count", 0) or 0),
        -int(metrics.get("runtime_rank", 0) or 0),
        -int(not bool(metrics.get("tests_only"))),
        -int(not bool(metrics.get("non_runtime_tool"))),
        int(bool(metrics.get("generic_symbol"))),
        -float(metrics.get("total_score", 0.0) or 0.0),
        float(metrics.get("score_gap", 0.0) or 0.0),
        int(metrics.get("dependency_complexity", 0) or 0),
        _token(metrics.get("cluster_id")),
    )


def _select_highlight_clusters(
    cluster_rows: Sequence[Mapping[str, object]],
    limit: int,
    allowed_confidence: set[str] | None = None,
    manual_review: bool = False,
) -> list[dict[str, object]]:
    allowed = {_token(value) for value in set(allowed_confidence or set()) if _token(value)} or None
    ordered = sorted([dict(row or {}) for row in cluster_rows], key=_manual_review_sort_key if manual_review else _highlight_sort_key)
    selected = []
    selected_cluster_ids = set()
    selected_keys = set()
    file_counts: dict[str, int] = defaultdict(int)
    module_counts: dict[str, int] = defaultdict(int)
    for pass_index in range(2):
        for row in ordered:
            metrics = _cluster_highlight_metrics(row)
            if not metrics.get("file_path"):
                continue
            confidence_class = _token(metrics.get("confidence_class"))
            if allowed and confidence_class not in allowed:
                continue
            cluster_id = _token(metrics.get("cluster_id"))
            winner_key = tuple(metrics.get("winner_key") or ())
            file_path = _norm_rel(metrics.get("file_path"))
            module_id = _token(metrics.get("module_id"))
            if cluster_id in selected_cluster_ids or winner_key in selected_keys:
                continue
            if pass_index == 0:
                if manual_review:
                    if bool(metrics.get("generic_symbol")) and not int(metrics.get("focus_specificity", 0) or 0) and int(metrics.get("runtime_rank", 0) or 0) < 3:
                        continue
                else:
                    if bool(metrics.get("tests_only")):
                        continue
                    if bool(metrics.get("non_runtime_tool")):
                        continue
                    if bool(metrics.get("generic_symbol")) and int(metrics.get("runtime_rank", 0) or 0) < 3:
                        continue
                    if bool(metrics.get("generic_symbol")) and int(metrics.get("focus_specificity", 0) or 0) < 2:
                        continue
                if file_counts[file_path] >= HIGHLIGHT_FILE_CAP or module_counts[module_id] >= HIGHLIGHT_MODULE_CAP:
                    continue
            else:
                if file_counts[file_path] >= HIGHLIGHT_FILE_CAP + 1 or module_counts[module_id] >= HIGHLIGHT_MODULE_CAP + 1:
                    continue
            selected.append(dict(row))
            selected_cluster_ids.add(cluster_id)
            selected_keys.add(winner_key)
            file_counts[file_path] += 1
            module_counts[module_id] += 1
            if len(selected) >= limit:
                return selected
    return selected


def _build_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    payloads = _required_inputs(root)
    indexes = _build_indexes(
        architecture_graph=dict(payloads["architecture_graph"] or {}),
        module_registry=dict(payloads["module_registry"] or {}),
        build_graph=dict(payloads["build_graph"] or {}),
        include_graph=dict(payloads["include_graph"] or {}),
        symbol_index=dict(payloads["symbol_index"] or {}),
    )
    cluster_rows = _cluster_rows(
        duplicate_impls=dict(payloads["duplicate_impls"] or {}),
        duplicate_clusters=dict(payloads["duplicate_clusters"] or {}),
    )
    scored_candidates = _scored_candidates(root, cluster_rows, indexes)
    implementation_rows = _flatten_implementation_scores(cluster_rows, scored_candidates)
    ranked_clusters = _rank_clusters(cluster_rows, scored_candidates)

    implementation_scores = _payload_with_fingerprint(
        {
            "implementation_count": len(implementation_rows),
            "implementations": implementation_rows,
            "report_id": "xi.implementation_scores.v1",
            "unique_candidate_count": len(scored_candidates),
            "weights": {key: value for key, value in sorted(WEIGHTS.items())},
        }
    )
    duplicate_cluster_rankings = _payload_with_fingerprint(
        {
            "cluster_count": len(ranked_clusters),
            "clusters": ranked_clusters,
            "report_id": "xi.duplicate_cluster_rankings.v1",
        }
    )

    return {
        "duplicate_cluster_rankings": duplicate_cluster_rankings,
        "implementation_scores": implementation_scores,
    }


def _top_focus_clusters(rankings: Mapping[str, object]) -> dict[str, list[dict[str, object]]]:
    focus_map = {label: [] for label, _keywords in FOCUS_TAGS}
    cluster_rows = [dict(row or {}) for row in list(rankings.get("clusters") or [])]
    for tag, _keywords in FOCUS_TAGS:
        tagged = []
        for row in cluster_rows:
            metrics = _cluster_highlight_metrics(row)
            if tag not in set(metrics.get("focus_tags") or []):
                continue
            specificity = _focus_specificity_for_tag(metrics.get("symbol_name"), metrics.get("file_path"), metrics.get("module_id"), tag)
            if bool(metrics.get("tests_only")) and specificity < 2:
                continue
            if bool(metrics.get("generic_symbol")) and specificity < 2 and int(metrics.get("runtime_rank", 0) or 0) < 3:
                continue
            tagged.append(
                {
                    "cluster_id": _token(metrics.get("cluster_id")),
                    "confidence_class": _token(metrics.get("confidence_class")),
                    "dependency_complexity": int(metrics.get("dependency_complexity", 0) or 0),
                    "file_path": _norm_rel(metrics.get("file_path")),
                    "focus_specificity": specificity,
                    "module_id": _token(metrics.get("module_id")),
                    "score_gap": float(metrics.get("score_gap", 0.0) or 0.0),
                    "symbol_name": _token(metrics.get("symbol_name")),
                    "total_score": float(metrics.get("total_score", 0.0) or 0.0),
                    "winner_key": tuple(metrics.get("winner_key") or ()),
                }
            )
        tagged = sorted(
            tagged,
            key=lambda row: (
                -int(row.get("focus_specificity", 0) or 0),
                -_confidence_rank(row.get("confidence_class")),
                -float(row.get("total_score", 0.0) or 0.0),
                -float(row.get("score_gap", 0.0) or 0.0),
                int(row.get("dependency_complexity", 0) or 0),
                _token(row.get("cluster_id")),
            ),
        )
        file_counts: dict[str, int] = defaultdict(int)
        module_counts: dict[str, int] = defaultdict(int)
        selected = []
        seen_keys = set()
        for row in tagged:
            file_path = _norm_rel(row.get("file_path"))
            module_id = _token(row.get("module_id"))
            winner_key = tuple(row.get("winner_key") or ())
            if winner_key in seen_keys:
                continue
            if file_counts[file_path] >= HIGHLIGHT_FILE_CAP or module_counts[module_id] >= HIGHLIGHT_MODULE_CAP:
                continue
            selected.append({key: value for key, value in row.items() if key != "winner_key"})
            seen_keys.add(winner_key)
            file_counts[file_path] += 1
            module_counts[module_id] += 1
            if len(selected) >= 6:
                break
        focus_map[tag] = selected
    return focus_map


def render_implementation_scorecard(snapshot: Mapping[str, object]) -> str:
    implementation_scores = dict(snapshot.get("implementation_scores") or {})
    rankings = dict(snapshot.get("duplicate_cluster_rankings") or {})
    score_rows = [dict(row or {}) for row in list(implementation_scores.get("implementations") or [])]
    cluster_rows = [dict(row or {}) for row in list(rankings.get("clusters") or [])]
    high_rows = _select_highlight_clusters(cluster_rows, 20, allowed_confidence={"high"})
    medium_rows = _select_highlight_clusters(cluster_rows, 20, allowed_confidence={"medium"})
    low_rows = _select_highlight_clusters(cluster_rows, 20, allowed_confidence={"low"}, manual_review=True)
    src_rows = _source_like_dir_summary(score_rows)[:12]
    focus_rows = _top_focus_clusters(rankings)

    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-3 convergence winner selection",
        "",
        "# Implementation Scorecard",
        "",
        "- duplicate_clusters_ranked: `{}`".format(int(rankings.get("cluster_count", 0) or 0)),
        "- scored_implementations: `{}`".format(int(implementation_scores.get("implementation_count", 0) or 0)),
        "- unique_candidates: `{}`".format(int(implementation_scores.get("unique_candidate_count", 0) or 0)),
        "",
        "## Highest Confidence Canonical Implementations",
        "",
    ]
    if not high_rows:
        lines.append("- none")
    else:
        for row in high_rows:
            winner = dict((list(row.get("ranked_candidates") or []) or [{}])[0] or {})
            lines.append(
                "- `{}` -> `{}` score=`{}` gap=`{}` module=`{}`".format(
                    _token(row.get("symbol_name")) or _token(row.get("cluster_id")),
                    _norm_rel(winner.get("file_path")),
                    round(float(winner.get("total_score", 0.0) or 0.0), 2),
                    round(float(row.get("score_gap", 0.0) or 0.0), 2),
                    _token(winner.get("module_id")),
                )
            )

    lines.extend(["", "## Medium Confidence Merges Required", ""])
    if not medium_rows:
        lines.append("- none")
    else:
        for row in medium_rows:
            winner = dict((list(row.get("ranked_candidates") or []) or [{}])[0] or {})
            lines.append(
                "- `{}` lead=`{}` score=`{}` gap=`{}`".format(
                    _token(row.get("symbol_name")) or _token(row.get("cluster_id")),
                    _norm_rel(winner.get("file_path")),
                    round(float(winner.get("total_score", 0.0) or 0.0), 2),
                    round(float(row.get("score_gap", 0.0) or 0.0), 2),
                )
            )

    lines.extend(["", "## Low Confidence Clusters Needing Manual Review", ""])
    if not low_rows:
        lines.append("- none")
    else:
        for row in low_rows:
            winner = dict((list(row.get("ranked_candidates") or []) or [{}])[0] or {})
            lines.append(
                "- `{}` lead=`{}` score=`{}` gap=`{}`".format(
                    _token(row.get("symbol_name")) or _token(row.get("cluster_id")),
                    _norm_rel(winner.get("file_path")),
                    round(float(winner.get("total_score", 0.0) or 0.0), 2),
                    round(float(row.get("score_gap", 0.0) or 0.0), 2),
                )
            )

    lines.extend(["", "## Focus Areas", ""])
    for tag, _keywords in FOCUS_TAGS:
        lines.extend(["### {}".format(tag.replace("_", " ").title()), ""])
        rows = list(focus_rows.get(tag) or [])
        if not rows:
            lines.append("- none")
            lines.append("")
            continue
        for row in rows:
            lines.append(
                "- `{}` lead=`{}` score=`{}` confidence=`{}`".format(
                    _token(row.get("symbol_name")) or _token(row.get("cluster_id")),
                    _norm_rel(row.get("file_path")),
                    round(float(row.get("total_score", 0.0) or 0.0), 2),
                    _token(row.get("confidence_class")),
                )
            )
        lines.append("")

    lines.extend(["## src/ Directory Impact Summary", ""])
    if not src_rows:
        lines.append("- none")
    else:
        for row in src_rows:
            lines.append(
                "- `{}` candidates=`{}` avg_score=`{}` low_arch=`{}` max_score=`{}`".format(
                    _token(row.get("directory_path")),
                    int(row.get("candidate_count", 0) or 0),
                    round(float(row.get("average_score", 0.0) or 0.0), 2),
                    int(row.get("low_arch_count", 0) or 0),
                    round(float(row.get("max_score", 0.0) or 0.0), 2),
                )
            )
    lines.append("")
    return "\n".join(lines)


def render_xi_2_final(snapshot: Mapping[str, object]) -> str:
    implementation_scores = dict(snapshot.get("implementation_scores") or {})
    rankings = dict(snapshot.get("duplicate_cluster_rankings") or {})
    score_rows = [dict(row or {}) for row in list(implementation_scores.get("implementations") or [])]
    cluster_rows = [dict(row or {}) for row in list(rankings.get("clusters") or [])]
    top_clusters = _select_highlight_clusters(cluster_rows, 10)
    module_rows = _module_duplication_summary(score_rows)[:12]
    src_rows = _source_like_dir_summary(score_rows)[:12]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: XI",
        "Replacement Target: XI-3 convergence planning",
        "",
        "# XI-2 Final",
        "",
        "- duplicate_clusters: `{}`".format(int(rankings.get("cluster_count", 0) or 0)),
        "- scored_implementations: `{}`".format(int(implementation_scores.get("implementation_count", 0) or 0)),
        "- unique_candidates: `{}`".format(int(implementation_scores.get("unique_candidate_count", 0) or 0)),
        "",
        "## Highest Scoring Canonical Candidates",
        "",
    ]
    for row in top_clusters:
        winner = dict((list(row.get("ranked_candidates") or []) or [{}])[0] or {})
        lines.append(
            "- `{}` -> `{}` score=`{}` confidence=`{}` gap=`{}`".format(
                _token(row.get("symbol_name")) or _token(row.get("cluster_id")),
                _norm_rel(winner.get("file_path")),
                round(float(winner.get("total_score", 0.0) or 0.0), 2),
                _token(row.get("confidence_class")),
                round(float(row.get("score_gap", 0.0) or 0.0), 2),
            )
        )
    lines.extend(["", "## Modules Most Affected By Duplication", ""])
    for row in module_rows:
        lines.append(
            "- `{}` clusters=`{}` score_rows=`{}` avg_score=`{}`".format(
                _token(row.get("module_id")),
                int(row.get("cluster_count", 0) or 0),
                int(row.get("score_rows", 0) or 0),
                round(float(row.get("average_score", 0.0) or 0.0), 2),
            )
        )
    lines.extend(["", "## src/ Directories Most Likely To Contain Shadow Implementations", ""])
    for row in src_rows:
        lines.append(
            "- `{}` candidates=`{}` low_arch=`{}` avg_score=`{}`".format(
                _token(row.get("directory_path")),
                int(row.get("candidate_count", 0) or 0),
                int(row.get("low_arch_count", 0) or 0),
                round(float(row.get("average_score", 0.0) or 0.0), 2),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_implementation_scoring_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    written[IMPLEMENTATION_SCORES_REL] = _write_canonical_json(_repo_abs(root, IMPLEMENTATION_SCORES_REL), dict(snapshot.get("implementation_scores") or {}))
    written[DUPLICATE_CLUSTER_RANKINGS_REL] = _write_canonical_json(_repo_abs(root, DUPLICATE_CLUSTER_RANKINGS_REL), dict(snapshot.get("duplicate_cluster_rankings") or {}))
    written[IMPLEMENTATION_SCORECARD_REL] = _write_text(_repo_abs(root, IMPLEMENTATION_SCORECARD_REL), render_implementation_scorecard(snapshot) + "\n")
    written[XI_2_FINAL_REL] = _write_text(_repo_abs(root, XI_2_FINAL_REL), render_xi_2_final(snapshot) + "\n")
    return written


def build_implementation_scoring_snapshot(repo_root: str) -> dict[str, object]:
    return _build_snapshot(repo_root)


__all__ = [
    "ARCHITECTURE_GRAPH_REL",
    "BUILD_GRAPH_REL",
    "DUPLICATE_CLUSTER_RANKINGS_REL",
    "DUPLICATE_CLUSTERS_REL",
    "DUPLICATE_IMPLS_REL",
    "IMPLEMENTATION_SCORECARD_REL",
    "IMPLEMENTATION_SCORES_REL",
    "INCLUDE_GRAPH_REL",
    "MODULE_REGISTRY_REL",
    "OUTPUT_REL_PATHS",
    "SYMBOL_INDEX_REL",
    "XI_2_FINAL_REL",
    "XiInputMissingError",
    "build_implementation_scoring_snapshot",
    "render_implementation_scorecard",
    "render_xi_2_final",
    "write_implementation_scoring_snapshot",
]
