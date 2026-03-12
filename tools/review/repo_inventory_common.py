"""Deterministic repository inventory and classification helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability import validate_all_registries, validate_pack_compat  # noqa: E402
from tools.audit.arch_audit_common import scan_duplicate_semantics  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


INVENTORY_JSON_REL = "data/audit/repo_inventory.json"
TREE_INDEX_MD_REL = "docs/audit/REPO_TREE_INDEX.md"
MODULE_DUPLICATION_REPORT_REL = "docs/audit/MODULE_DUPLICATION_REPORT.md"
ENTRYPOINT_MAP_REL = "docs/audit/ENTRYPOINT_MAP.md"
PLATFORM_RENDERER_SURFACE_REL = "docs/audit/PLATFORM_RENDERER_SURFACE.md"
VALIDATION_STACK_MAP_REL = "docs/audit/VALIDATION_STACK_MAP.md"
STABILITY_COVERAGE_REPORT_REL = "docs/audit/STABILITY_COVERAGE_REPORT.md"
FINAL_REPORT_REL = "docs/audit/REPO_REVIEW_2_FINAL.md"

SCAN_ROOTS = (
    "src",
    "tools",
    "data",
    "schema",
    "schemas",
)
TREE_ROOTS = (
    "src",
    "tools",
    "data",
    "schema",
    "schemas",
    "docs/release",
    "docs/audit",
)
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
SKIP_PREFIXES = (
    "build/",
    "docs/audit/auditx/",
)
SKIP_EXACT_PATHS = {
    INVENTORY_JSON_REL,
}
TEXT_EXTENSIONS = {
    ".cmd",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".schema",
    ".txt",
}
PRODUCT_IDS = (
    "client",
    "engine",
    "game",
    "launcher",
    "server",
    "setup",
    "tool.attach_console_stub",
)
PRODUCT_HINTS = {
    "client": ("tools/mvp/runtime_entry.py",),
    "engine": ("tools/appshell/product_stub_cli.py",),
    "game": ("tools/appshell/product_stub_cli.py",),
    "launcher": ("tools/launcher/launch.py",),
    "server": ("src/server/server_main.py", "tools/mvp/runtime_entry.py"),
    "setup": ("tools/setup/setup_cli.py",),
    "tool.attach_console_stub": ("tools/appshell/product_stub_cli.py",),
}
LEGACY_TOP_LEVEL_DIRS = {
    "ai",
    "animal",
    "autonomy",
    "economy",
    "governance",
    "knowledge",
    "mmo",
    "network",
    "risk",
    "travel",
    "vegetation",
    "weather",
}
LEGACY_TOOL_DIRS = {
    "ai",
    "animal",
    "autonomy",
    "crafting",
    "economy",
    "governance",
    "hazard",
    "history",
    "institution",
    "knowledge",
    "mining",
    "mmo",
    "network",
    "risk",
    "travel",
    "vegetation",
    "weather",
}
PLATFORM_TOKENS = (
    "win32",
    "windows",
    "gtk",
    "cocoa",
    "classic",
    "posix",
    "sdl",
)
WALLCLOCK_PATTERNS = (
    "datetime.now(",
    "datetime.utcnow(",
    "date.today(",
    "time.time(",
    "time.monotonic(",
    "time.perf_counter(",
)
FLOAT_PATTERNS = (
    "float(",
    "math.sin(",
    "math.cos(",
    "math.tan(",
    "math.acos(",
    "math.atan2(",
    "math.sqrt(",
)
DIRECT_PATH_PATTERNS = (
    "os.path.",
    "open(",
    "Path(",
    "pathlib.Path(",
    "sys.path.insert(",
    "abspath(",
    "relpath(",
    "normpath(",
)
ENTRYPOINT_DEF_PATTERN = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
IMPORT_PATTERN = re.compile(r"^\s*(?:from|import)\s+(src|tools)\.([A-Za-z0-9_\.]+)")
BUILD_TARGET_MAIN_PATTERN = re.compile(r"^\s*def\s+(?:main|appshell_main|client_main|server_main)\s*\(")
PRODUCT_PATH_PATTERN = re.compile(r'product_id\s*=\s*"([^"]+)"')


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _token(value: object) -> str:
    return str(value or "").strip()


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, rel_path.replace("/", os.sep))))


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _json_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _json_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _is_text_file(rel_path: str) -> bool:
    if rel_path.endswith("/client") or rel_path.endswith("/engine") or rel_path.endswith("/game") or rel_path.endswith("/launcher") or rel_path.endswith("/server") or rel_path.endswith("/setup"):
        return True
    _, ext = os.path.splitext(rel_path)
    return ext.lower() in TEXT_EXTENSIONS


def _iter_root_files(repo_root: str, roots: Iterable[str]) -> list[str]:
    rel_paths: list[str] = []
    for root in roots:
        abs_root = _repo_abs(repo_root, str(root))
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            rel_dir = _norm(os.path.relpath(dirpath, repo_root))
            dirnames[:] = sorted(
                [
                    name
                    for name in dirnames
                    if name not in SKIP_DIR_NAMES
                    and not any(_norm(os.path.join(rel_dir, name)).startswith(prefix) for prefix in SKIP_PREFIXES)
                ]
            )
            if any(rel_dir.startswith(prefix.rstrip("/")) for prefix in SKIP_PREFIXES):
                dirnames[:] = []
                continue
            for name in sorted(filenames):
                rel_path = _norm(os.path.join(rel_dir, name))
                if any(rel_path.startswith(prefix) for prefix in SKIP_PREFIXES):
                    continue
                if rel_path in SKIP_EXACT_PATHS:
                    continue
                if not _is_text_file(rel_path):
                    continue
                rel_paths.append(rel_path)
    return sorted(set(rel_paths))


def _derive_module_name(rel_path: str) -> str:
    rel_norm = _norm(rel_path)
    parts = rel_norm.split("/")
    stem, _ext = os.path.splitext(parts[-1])
    if len(parts) <= 1:
        return stem
    return ".".join(parts[:-1] + [stem])


def _detect_internal_imports(text: str) -> list[str]:
    imports = set()
    for line in text.splitlines():
        match = IMPORT_PATTERN.match(line)
        if not match:
            continue
        root = str(match.group(1))
        remainder = str(match.group(2))
        segments = [token for token in remainder.split(".") if token]
        imports.add("{}.{}".format(root, segments[0]) if segments else root)
    return sorted(imports)


def _detect_entrypoints(text: str) -> list[str]:
    entrypoints = set()
    if "__main__" in text:
        entrypoints.add("__main__")
    for line in text.splitlines():
        match = ENTRYPOINT_DEF_PATTERN.match(line)
        if not match:
            continue
        symbol = str(match.group(1))
        if symbol == "main" or symbol.endswith("_main") or symbol == "appshell_main":
            entrypoints.add(symbol)
    return sorted(entrypoints)


def _product_registry_rows(repo_root: str) -> dict[str, dict]:
    payload = _read_json(_repo_abs(repo_root, "data/registries/product_registry.json"))
    record = _json_map(payload.get("record"))
    rows = {}
    for row in _json_list(record.get("products")):
        item = _json_map(row)
        product_id = _token(item.get("product_id"))
        if product_id:
            rows[product_id] = item
    return rows


def _discover_product_entrypoint(repo_root: str, product_id: str, python_files: Iterable[str]) -> str:
    hints = PRODUCT_HINTS.get(product_id, ())
    for hint in hints:
        abs_path = _repo_abs(repo_root, hint)
        if not os.path.isfile(abs_path):
            continue
        text = _read_text(abs_path)
        if product_id in {"engine", "game", "tool.attach_console_stub"} and "--product-id" in text:
            return hint
        if 'product_id="{}"'.format(product_id) in text or "product_id='{}'".format(product_id) in text:
            return hint
        if product_id == "client" and "client_main" in text and "appshell_main" in text:
            return hint
    candidates: list[str] = []
    for rel_path in python_files:
        text = _read_text(_repo_abs(repo_root, rel_path))
        if 'product_id="{}"'.format(product_id) in text or "product_id='{}'".format(product_id) in text:
            candidates.append(rel_path)
    if candidates:
        return sorted(candidates)[0]
    if product_id in {"engine", "game", "tool.attach_console_stub"}:
        return "tools/appshell/product_stub_cli.py"
    return ""


def _classify_product(rel_path: str) -> str:
    rel_norm = _norm(rel_path)
    if rel_norm.startswith("tools/launcher/"):
        return "launcher"
    if rel_norm.startswith("tools/setup/"):
        return "setup"
    if rel_norm.startswith("src/server/"):
        return "server"
    if rel_norm.startswith("src/client/"):
        return "client"
    if rel_norm.startswith("tools/"):
        return "tool"
    return "engine"


def _classify_layer(rel_path: str, text: str) -> str:
    rel_norm = _norm(rel_path)
    parts = rel_norm.split("/")
    root = parts[0] if parts else ""
    top = parts[1] if len(parts) > 1 else ""
    lowered = rel_norm.lower()
    if root == "src":
        if top == "platform" or any(token in lowered for token in PLATFORM_TOKENS):
            return "platform"
        if top in LEGACY_TOP_LEVEL_DIRS:
            return "legacy"
        if top in {"client", "appshell"}:
            return "ui"
        if top in {"lib", "packs"}:
            return "packaging"
        if top in {
            "astro",
            "chem",
            "electric",
            "embodiment",
            "fluid",
            "geo",
            "logic",
            "logistics",
            "machines",
            "materials",
            "mechanics",
            "mobility",
            "pollution",
            "process",
            "system",
            "thermal",
            "worldgen",
        }:
            return "domain"
        if top in {
            "compat",
            "control",
            "core",
            "diag",
            "diegetics",
            "epistemics",
            "field",
            "fields",
            "infrastructure",
            "inspection",
            "interaction",
            "interior",
            "meta",
            "models",
            "net",
            "performance",
            "physics",
            "reality",
            "runtime",
            "safety",
            "signals",
            "specs",
            "time",
            "universe",
        }:
            return "core"
        if top == "modding":
            return "packaging"
        return "legacy"
    if root == "tools":
        if top in {"audit", "auditx", "compat", "compatx", "review", "schema_migration", "validate", "validation", "validator"}:
            return "validation"
        if top == "xstack":
            return "validation"
        if top in {"launcher", "setup", "pack", "distribution", "lib", "workspace", "share"}:
            return "packaging"
        if top in {"render", "gui", "editor_gui", "ui_bind", "ui_editor", "ui_index", "ui_preview_host", "ui_shared"}:
            return "ui"
        if top == "platform" or any(token in lowered for token in PLATFORM_TOKENS):
            return "platform"
        if top in LEGACY_TOOL_DIRS:
            return "legacy"
        return "tool"
    if root == "data":
        if top in {"audit", "registries"}:
            return "validation"
        if top == "packs":
            return "packaging"
        if top == "worldgen":
            return "domain"
        return "legacy"
    if root in {"schema", "schemas"}:
        return "validation"
    return "unknown"


def _classify_responsibility(rel_path: str, layer: str) -> str:
    rel_norm = _norm(rel_path)
    if rel_norm.startswith(("src/universe/", "src/field/", "src/fields/", "src/time/")):
        return "core.truth_time"
    if rel_norm.startswith(("src/process/", "src/system/", "src/meta/provenance/", "src/diag/")):
        return "core.proof_process"
    if rel_norm.startswith(("src/worldgen/refinement/",)):
        return "core.refinement"
    if rel_norm.startswith(("src/control/", "src/core/", "src/compat/")):
        return "game.composition_binding"
    if rel_norm.startswith(("src/appshell/", "src/client/",)):
        return "ui.shared"
    if rel_norm.startswith(("src/geo/",)):
        return "domain.geo"
    if rel_norm.startswith(("src/worldgen/mw/", "src/worldgen/galaxy/")):
        return "domain.mw"
    if rel_norm.startswith(("src/astro/",)):
        return "domain.sol"
    if rel_norm.startswith(("src/worldgen/earth/",)):
        return "domain.earth"
    if rel_norm.startswith(("src/logic/",)):
        return "domain.logic"
    if rel_norm.startswith(("src/pollution/",)):
        return "domain.poll"
    if rel_norm.startswith(("src/embodiment/",)):
        return "domain.embodiment"
    if rel_norm.startswith(("src/mobility/",)):
        return "domain.mobility"
    if rel_norm.startswith(("src/thermal/",)):
        return "domain.thermal"
    if rel_norm.startswith(("src/fluid/",)):
        return "domain.fluid"
    if rel_norm.startswith(("src/chem/", "src/materials/")):
        return "domain.materials"
    if rel_norm.startswith(("src/electric/", "src/signals/")):
        return "domain.electric"
    if rel_norm.startswith(("src/client/render/",)):
        return "ui.rendered"
    if rel_norm.startswith(("src/client/ui/", "tools/gui/", "tools/ui_")):
        return "ui.shared"
    if rel_norm.startswith(("src/platform/", "tools/platform/")):
        return "platform.adapters"
    if rel_norm.startswith(("tools/audit", "tools/auditx", "tools/compatx", "tools/xstack/", "schema/", "schemas/", "data/registries/")):
        return "validation.stack"
    if rel_norm.startswith(("tools/launcher/", "tools/setup/", "tools/pack/", "tools/distribution/", "data/packs/")):
        return "packaging.install"
    if layer == "legacy":
        return "legacy.experimental"
    if layer == "tool":
        return "tool.utility"
    if layer == "core":
        return "core.misc"
    if layer == "domain":
        return "domain.misc"
    return "unknown"


def _uses_wallclock(rel_path: str, text: str) -> bool:
    del rel_path
    return bool(text) and any(token in text.lower() for token in WALLCLOCK_PATTERNS)


def _uses_float_in_truth(rel_path: str, layer: str, text: str) -> bool:
    if layer not in {"core", "domain"} or not rel_path.endswith(".py"):
        return False
    lowered = text.lower()
    if any(token in lowered for token in FLOAT_PATTERNS):
        return True
    return bool(re.search(r"\b\d+\.\d+\b", lowered))


def _uses_direct_paths(rel_path: str, text: str) -> bool:
    if not rel_path.endswith((".py", ".cmd", ".ps1")):
        return False
    lowered = text.lower()
    return any(token.lower() in lowered for token in DIRECT_PATH_PATTERNS)


def _platform_specific(rel_path: str, text: str) -> bool:
    lowered_path = _norm(rel_path).lower()
    if any(token in lowered_path for token in PLATFORM_TOKENS):
        return True
    lowered = text.lower()
    return any(token in lowered for token in PLATFORM_TOKENS) or "import win32api" in lowered or "ctypes.windll" in lowered


def _build_target(rel_path: str, product: str, text: str, entrypoints: list[str]) -> str:
    rel_norm = _norm(rel_path)
    if rel_norm == "src/server/server_main.py":
        return "server"
    if rel_norm == "tools/launcher/launch.py":
        return "launcher"
    if rel_norm == "tools/setup/setup_cli.py":
        return "setup"
    if rel_norm == "tools/mvp/runtime_entry.py":
        return "client/server"
    if rel_norm == "tools/appshell/product_stub_cli.py":
        return "engine/game/tool.attach_console_stub"
    if entrypoints and rel_norm.startswith("tools/"):
        return os.path.splitext(os.path.basename(rel_norm))[0]
    if product in {"client", "server", "launcher", "setup"} and entrypoints:
        return product
    if BUILD_TARGET_MAIN_PATTERN.search(text):
        return os.path.splitext(os.path.basename(rel_norm))[0]
    return ""


def _inventory_entry(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    text = _read_text(abs_path)
    layer = _classify_layer(rel_path, text)
    product = _classify_product(rel_path)
    entrypoints = _detect_entrypoints(text) if rel_path.endswith(".py") else []
    payload = {
        "path": _norm(rel_path),
        "module_name": _derive_module_name(rel_path),
        "build_target": "",
        "product": product,
        "layer": layer,
        "responsibility": _classify_responsibility(rel_path, layer),
        "linked_libraries": _detect_internal_imports(text) if rel_path.endswith(".py") else [],
        "entrypoints": entrypoints,
        "platform_specific": _platform_specific(rel_path, text),
        "uses_wallclock": _uses_wallclock(rel_path, text) if rel_path.endswith(".py") else False,
        "uses_float_in_truth": _uses_float_in_truth(rel_path, layer, text),
        "uses_direct_paths": _uses_direct_paths(rel_path, text),
        "deterministic_fingerprint": "",
    }
    payload["build_target"] = _build_target(rel_path, product, text, entrypoints)
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _summary_maps(entries: list[dict]) -> dict:
    by_layer = Counter()
    by_product = Counter()
    by_responsibility = Counter()
    for row in entries:
        by_layer[str(row.get("layer", ""))] += 1
        by_product[str(row.get("product", ""))] += 1
        by_responsibility[str(row.get("responsibility", ""))] += 1
    return {
        "by_layer": dict(sorted(by_layer.items())),
        "by_product": dict(sorted(by_product.items())),
        "by_responsibility": dict(sorted(by_responsibility.items())),
        "platform_specific_count": sum(1 for row in entries if bool(row.get("platform_specific"))),
        "wallclock_heuristic_count": sum(1 for row in entries if bool(row.get("uses_wallclock"))),
        "float_in_truth_heuristic_count": sum(1 for row in entries if bool(row.get("uses_float_in_truth"))),
        "direct_path_heuristic_count": sum(1 for row in entries if bool(row.get("uses_direct_paths"))),
        "unknown_entry_count": sum(1 for row in entries if str(row.get("layer", "")).strip() == "unknown"),
    }


def _renderer_surface(repo_root: str, entries: list[dict], product_rows: Mapping[str, object]) -> dict:
    del product_rows
    backend_map = {
        "null": "src/client/render/renderers/null_renderer.py",
        "software": "src/client/render/renderers/software_renderer.py",
        "hardware_gl": "src/client/render/renderers/hw_renderer_gl.py",
    }
    python_files = [row for row in entries if str(row.get("path", "")).endswith(".py")]
    rows: list[dict] = []
    for backend_id, rel_path in sorted(backend_map.items()):
        module_name = os.path.splitext(os.path.basename(rel_path))[0]
        refs = []
        products = set()
        for entry in python_files:
            path = str(entry.get("path", "")).strip()
            if path == rel_path:
                continue
            text = _read_text(_repo_abs(repo_root, path))
            if module_name not in text and backend_id not in text:
                continue
            refs.append(path)
            products.add(str(entry.get("product", "")).strip() or "engine")
        backend_text = _read_text(_repo_abs(repo_root, rel_path))
        rows.append(
            {
                "backend_id": backend_id,
                "path": rel_path,
                "referenced_by": sorted(refs),
                "products": sorted(product for product in products if product),
                "unused": len(refs) == 0,
                "platform_gated": _platform_specific(rel_path, backend_text) or backend_id == "hardware_gl",
            }
        )
    return {
        "backends": rows,
        "deterministic_fingerprint": "",
    }


def _validation_surface(entries: list[dict]) -> dict:
    targets: list[dict] = []
    for row in entries:
        rel_path = str(row.get("path", "")).strip()
        lowered = rel_path.lower()
        if not (lowered.endswith(".py") or lowered.endswith(".json") or lowered.endswith(".schema")):
            continue
        consolidation_target = ""
        if "schema_migration" in lowered:
            consolidation_target = "PACK-COMPAT-2"
        elif "pack_validate" in lowered or "pack_compat" in lowered or "compatx" in lowered:
            consolidation_target = "PACK-COMPAT"
        elif "cap_neg" in lowered or "negotiation" in lowered or "descriptor" in lowered:
            consolidation_target = "CAP-NEG"
        elif "hygiene" in lowered or "arch_audit" in lowered or "audit" in lowered or "auditx" in lowered:
            consolidation_target = "ARCH-AUDIT"
        elif "coredata_validate" in lowered:
            consolidation_target = "CORE-DATA"
        elif "validate" in lowered or "validator" in lowered or "validation" in lowered:
            consolidation_target = "Validation Legacy"
        if not consolidation_target:
            continue
        targets.append(
            {
                "path": rel_path,
                "layer": str(row.get("layer", "")).strip(),
                "product": str(row.get("product", "")).strip(),
                "consolidation_target": consolidation_target,
            }
        )
    return {
        "rows": sorted(
            targets,
            key=lambda item: (
                str(item.get("consolidation_target", "")),
                str(item.get("path", "")),
            ),
        ),
        "deterministic_fingerprint": "",
    }


def _collect_validation_entrypoints(entries: list[dict]) -> list[dict]:
    rows = []
    for row in entries:
        rel_path = str(row.get("path", "")).strip()
        if not rel_path.endswith(".py"):
            continue
        lowered = rel_path.lower()
        if "validate" not in lowered and "validator" not in lowered and "validation" not in lowered:
            continue
        entrypoints = list(row.get("entrypoints") or [])
        if not entrypoints:
            continue
        rows.append(
            {
                "path": rel_path,
                "product": str(row.get("product", "")).strip(),
                "build_target": str(row.get("build_target", "")).strip(),
                "entrypoints": entrypoints,
            }
        )
    return sorted(rows, key=lambda item: (str(item.get("path", "")), str(item.get("build_target", ""))))


def _scan_path_resolution_candidates(entries: list[dict]) -> list[str]:
    rows = []
    for row in entries:
        rel_path = str(row.get("path", "")).strip()
        if not rel_path.endswith(".py"):
            continue
        if not bool(row.get("uses_direct_paths", False)):
            continue
        rows.append(rel_path)
    return sorted(rows)


def _scan_rng_init_candidates(repo_root: str, entries: list[dict]) -> list[str]:
    rows = []
    for row in entries:
        rel_path = str(row.get("path", "")).strip()
        if not rel_path.endswith(".py"):
            continue
        text = _read_text(_repo_abs(repo_root, rel_path)).lower()
        if "named rng" in text or "named_rng" in text:
            rows.append(rel_path)
            continue
        if "random(" in text or ".seed(" in text or "rng." in text or "rng_" in text:
            rows.append(rel_path)
    return sorted(set(rows))


def _scan_product_main_bypasses(repo_root: str, python_files: Iterable[str]) -> list[dict]:
    bypasses: list[dict] = []
    for rel_path in sorted(set(str(path) for path in python_files)):
        rel_norm = _norm(rel_path)
        if rel_norm.startswith("tools/") and not rel_norm.startswith(("tools/launcher/", "tools/setup/", "tools/mvp/", "tools/appshell/")):
            continue
        if rel_norm not in {
            "src/server/server_main.py",
            "tools/launcher/launch.py",
            "tools/setup/setup_cli.py",
            "tools/mvp/runtime_entry.py",
            "tools/appshell/product_stub_cli.py",
        } and not rel_norm.startswith(("src/client/", "src/server/")):
            continue
        text = _read_text(_repo_abs(repo_root, rel_norm))
        if "def main(" not in text and "def client_main(" not in text and "def server_main(" not in text:
            continue
        product_ids = sorted(set(PRODUCT_PATH_PATTERN.findall(text)))
        if rel_norm == "tools/appshell/product_stub_cli.py":
            product_ids = ["engine", "game", "tool.attach_console_stub"]
        if rel_norm == "tools/mvp/runtime_entry.py":
            product_ids = ["client", "server"]
        if not product_ids and rel_norm.startswith("src/server/"):
            product_ids = ["server"]
        if not product_ids:
            continue
        if "appshell_main" in text:
            continue
        bypasses.append(
            {
                "path": rel_norm,
                "product_ids": product_ids,
                "message": "product entrypoint defines main without delegating through appshell_main",
            }
        )
    return sorted(bypasses, key=lambda item: (str(item.get("path", "")), ",".join(item.get("product_ids", []))))


def _entrypoint_map(repo_root: str, entries: list[dict], product_rows: Mapping[str, object]) -> dict:
    python_files = [str(row.get("path", "")).strip() for row in entries if str(row.get("path", "")).endswith(".py")]
    rows: list[dict] = []
    for product_id in sorted(set(product_rows.keys()) | set(PRODUCT_IDS)):
        row = _json_map(product_rows.get(product_id))
        source_path = _discover_product_entrypoint(repo_root, product_id, python_files)
        source_text = _read_text(_repo_abs(repo_root, source_path)) if source_path else ""
        capabilities = sorted(
            {
                _token(item)
                for item in _json_list(row.get("default_feature_capabilities")) + _json_list(row.get("default_optional_capabilities"))
                if _token(item)
            }
        )
        dist_bin_names = sorted(_json_list(_json_map(row.get("extensions")).get("official.dist_bin_names")))
        rows.append(
            {
                "product_id": product_id,
                "executable_names": dist_bin_names,
                "source_file": source_path,
                "calls_appshell_main": bool(source_text and "appshell_main" in source_text),
                "ui_adapter_invoked": bool([cap for cap in capabilities if cap.startswith("cap.ui.")]),
                "ui_capabilities": [cap for cap in capabilities if cap.startswith("cap.ui.")],
                "ipc_endpoint_started": "cap.ipc.attach_console" in capabilities or "ipc_enabled" in source_text,
                "supervisor_involvement": product_id == "launcher" or "supervisor" in source_text.lower(),
                "entrypoints": _detect_entrypoints(source_text) if source_text else [],
            }
        )
    bypasses = _scan_product_main_bypasses(repo_root, python_files)
    return {
        "rows": rows,
        "bypasses": bypasses,
        "deterministic_fingerprint": "",
    }


def scan_product_main_bypasses(repo_root: str) -> list[dict]:
    root = _repo_root(repo_root)
    python_files = _iter_root_files(root, ("src", "tools"))
    return _scan_product_main_bypasses(root, python_files)


def _duplication_surface(repo_root: str, entries: list[dict], entrypoint_map: Mapping[str, object]) -> dict:
    semantic_scan = scan_duplicate_semantics(repo_root)
    path_resolution = _scan_path_resolution_candidates(entries)
    rng_init = _scan_rng_init_candidates(repo_root, entries)
    validation_entrypoints = _collect_validation_entrypoints(entries)
    bypasses = list(_json_list(entrypoint_map.get("bypasses")))
    semantic_rows = []
    for symbol, row in sorted(_json_map(_json_map(semantic_scan.get("inventory")).get("symbols")).items()):
        item = _json_map(row)
        semantic_rows.append(
            {
                "symbol": symbol,
                "topic": _token(item.get("topic")),
                "expected_path": _token(item.get("expected_path")),
                "occurrence_count": len(_json_list(item.get("occurrences"))),
                "occurrences": _json_list(item.get("occurrences")),
            }
        )
    return {
        "semantic_engines": semantic_rows,
        "validation_entrypoints": validation_entrypoints,
        "product_main_bypasses": bypasses,
        "path_resolution_candidates": [{"path": path} for path in path_resolution],
        "rng_initialization_candidates": [{"path": path} for path in rng_init],
        "deterministic_fingerprint": "",
    }


def _stability_coverage(repo_root: str) -> dict:
    registry_report = validate_all_registries(repo_root)
    pack_reports = []
    pack_missing = []
    artifact_missing = []
    manifest_paths = _iter_root_files(repo_root, ("data", "tools"))
    for rel_path in manifest_paths:
        if not rel_path.endswith(".json"):
            continue
        file_name = os.path.basename(rel_path)
        if file_name == "pack.compat.json":
            report = validate_pack_compat(_repo_abs(repo_root, rel_path))
            pack_reports.append(
                {
                    "path": rel_path,
                    "result": _token(report.get("result")),
                    "stability_present": bool(report.get("stability_present", False)),
                    "errors": _json_list(report.get("errors")),
                }
            )
            if not bool(report.get("stability_present", False)):
                pack_missing.append(rel_path)
            continue
        if "manifest" not in file_name.lower():
            continue
        payload = _read_json(_repo_abs(repo_root, rel_path))
        if not isinstance(payload.get("stability"), Mapping):
            artifact_missing.append(rel_path)
    registry_missing = []
    for row in _json_list(registry_report.get("reports")):
        report_row = _json_map(row)
        for error in _json_list(report_row.get("errors")):
            error_row = _json_map(error)
            if _token(error_row.get("code")) != "missing_stability":
                continue
            registry_missing.append(
                {
                    "file_path": _token(report_row.get("file_path")),
                    "path": _token(error_row.get("path")),
                    "message": _token(error_row.get("message")),
                }
            )
    return {
        "registry_validation": {
            "result": _token(registry_report.get("result")),
            "deterministic_fingerprint": _token(registry_report.get("deterministic_fingerprint")),
            "missing_entries": sorted(registry_missing, key=lambda item: (str(item.get("file_path", "")), str(item.get("path", "")))),
        },
        "pack_manifests": {
            "reports": sorted(pack_reports, key=lambda item: str(item.get("path", ""))),
            "missing_stability_paths": sorted(set(pack_missing)),
        },
        "artifact_manifests": {
            "missing_stability_paths": sorted(set(artifact_missing)),
        },
        "deterministic_fingerprint": "",
    }


def _risk_rows(report: Mapping[str, object]) -> list[dict]:
    duplication = _json_map(report.get("duplication"))
    summary = _json_map(report.get("summary"))
    stability = _json_map(report.get("stability_coverage"))
    return [
        {
            "level": "high",
            "area": "validation surface fragmentation",
            "detail": "{} validation entrypoints remain distributed across tooling surfaces".format(len(_json_list(duplication.get("validation_entrypoints")))),
        },
        {
            "level": "high",
            "area": "virtual path bypass heuristics",
            "detail": "{} scanned files still use direct path heuristics".format(int(summary.get("direct_path_heuristic_count", 0) or 0)),
        },
        {
            "level": "medium",
            "area": "platform-gated surfaces",
            "detail": "{} scanned files are platform-specific by heuristic".format(int(summary.get("platform_specific_count", 0) or 0)),
        },
        {
            "level": "medium",
            "area": "artifact stability coverage",
            "detail": "{} artifact manifests do not declare stability metadata".format(
                len(_json_list(_json_map(stability.get("artifact_manifests")).get("missing_stability_paths")))
            ),
        },
        {
            "level": "low",
            "area": "legacy-aligned modules",
            "detail": "{} entries remain classified as legacy rather than core/domain/ui/platform".format(
                int(_json_map(summary.get("by_layer")).get("legacy", 0) or 0)
            ),
        },
    ]


def build_repo_inventory(repo_root: str) -> dict:
    root = _repo_root(repo_root)
    files = _iter_root_files(root, SCAN_ROOTS)
    entries = sorted([_inventory_entry(root, rel_path) for rel_path in files], key=lambda item: (str(item.get("path", "")), str(item.get("module_name", ""))))
    product_rows = _product_registry_rows(root)
    renderer_surface = _renderer_surface(root, entries, product_rows)
    renderer_surface["deterministic_fingerprint"] = canonical_sha256(dict(renderer_surface, deterministic_fingerprint=""))
    entrypoint_map = _entrypoint_map(root, entries, product_rows)
    entrypoint_map["deterministic_fingerprint"] = canonical_sha256(dict(entrypoint_map, deterministic_fingerprint=""))
    duplication = _duplication_surface(root, entries, entrypoint_map)
    duplication["deterministic_fingerprint"] = canonical_sha256(dict(duplication, deterministic_fingerprint=""))
    validation_surface = _validation_surface(entries)
    validation_surface["deterministic_fingerprint"] = canonical_sha256(dict(validation_surface, deterministic_fingerprint=""))
    stability_coverage = _stability_coverage(root)
    stability_coverage["deterministic_fingerprint"] = canonical_sha256(dict(stability_coverage, deterministic_fingerprint=""))
    payload = {
        "inventory_id": "repo.inventory.v1",
        "result": "complete",
        "scanned_roots": list(SCAN_ROOTS),
        "entry_count": len(entries),
        "entries": entries,
        "summary": _summary_maps(entries),
        "products": {
            "registry_count": len(product_rows),
            "entrypoints": _json_list(entrypoint_map.get("rows")),
            "bypass_count": len(_json_list(entrypoint_map.get("bypasses"))),
        },
        "entrypoint_map": entrypoint_map,
        "duplication": duplication,
        "platform_renderer_surface": renderer_surface,
        "validation_surface": validation_surface,
        "stability_coverage": stability_coverage,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def load_json_if_present(repo_root: str, rel_path: str) -> dict:
    path = _repo_abs(_repo_root(repo_root), rel_path)
    if not os.path.isfile(path):
        return {}
    return _read_json(path)


def load_or_run_inventory_report(repo_root: str, *, prefer_cached: bool = True) -> dict:
    root = _repo_root(repo_root)
    if prefer_cached:
        payload = load_json_if_present(root, INVENTORY_JSON_REL)
        if payload and _token(payload.get("inventory_id")) == "repo.inventory.v1":
            return payload
    return build_repo_inventory(root)


def unknown_inventory_entries(report: Mapping[str, object] | None) -> list[dict]:
    rows = []
    for row in _json_list(_json_map(report).get("entries")):
        item = _json_map(row)
        if _token(item.get("layer")) != "unknown":
            continue
        rows.append(
            {
                "path": _token(item.get("path")),
                "module_name": _token(item.get("module_name")),
                "responsibility": _token(item.get("responsibility")),
            }
        )
    return sorted(rows, key=lambda item: (str(item.get("path", "")), str(item.get("module_name", ""))))


def _tree_node_map(repo_root: str, planned_paths: Iterable[str]) -> dict[str, set[str]]:
    tree: dict[str, set[str]] = defaultdict(set)
    for root in TREE_ROOTS:
        abs_root = _repo_abs(repo_root, root)
        if os.path.isdir(abs_root):
            for dirpath, dirnames, filenames in os.walk(abs_root):
                rel_dir = _norm(os.path.relpath(dirpath, repo_root))
                if any(rel_dir.startswith(prefix.rstrip("/")) for prefix in SKIP_PREFIXES):
                    dirnames[:] = []
                    continue
                dirnames[:] = sorted(
                    [
                        name
                        for name in dirnames
                        if name not in SKIP_DIR_NAMES
                        and not any(_norm(os.path.join(rel_dir, name)).startswith(prefix) for prefix in SKIP_PREFIXES)
                    ]
                )
                parent = "" if rel_dir == "." else rel_dir
                for name in dirnames:
                    child_rel = _norm(os.path.join(parent, name)) if parent else _norm(name)
                    tree[parent].add(child_rel)
                for name in sorted(filenames):
                    rel_path = _norm(os.path.join(parent, name)) if parent else _norm(name)
                    if any(rel_path.startswith(prefix) for prefix in SKIP_PREFIXES):
                        continue
                    tree[parent].add(rel_path)
        elif os.path.isfile(abs_root):
            tree[""].add(_norm(root))
    for rel_path in sorted(set(_norm(path) for path in planned_paths if _token(path))):
        if any(rel_path.startswith(prefix) for prefix in SKIP_PREFIXES):
            continue
        parts = rel_path.split("/")
        for index in range(len(parts)):
            parent = "/".join(parts[:index])
            child = "/".join(parts[: index + 1])
            tree[parent].add(child)
    return tree


def _render_tree(repo_root: str, planned_paths: Iterable[str]) -> str:
    tree = _tree_node_map(repo_root, planned_paths)

    def render_branch(parent: str, depth: int) -> list[str]:
        rows: list[str] = []
        for child in sorted(tree.get(parent, set())):
            name = child.split("/")[-1]
            is_dir = child in tree
            rows.append("{}{}{}".format("  " * depth, name, "/" if is_dir else ""))
            if is_dir:
                rows.extend(render_branch(child, depth + 1))
        return rows

    lines = [
        "# Repo Tree Index",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
    ]
    for root in TREE_ROOTS:
        rel_root = _norm(root)
        if rel_root not in tree and rel_root not in tree.get("", set()):
            continue
        lines.append("## `{}`".format(rel_root))
        lines.append("")
        lines.append("```text")
        lines.append(rel_root)
        lines.extend(render_branch(rel_root, 1))
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_entrypoint_map(report: Mapping[str, object]) -> str:
    entrypoint_map = _json_map(report.get("entrypoint_map"))
    rows = _json_list(entrypoint_map.get("rows"))
    bypasses = _json_list(entrypoint_map.get("bypasses"))
    lines = [
        "# Entrypoint Map",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "| Product | Executables | Source | AppShell | UI Adapter | IPC | Supervisor |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        item = _json_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("product_id")),
                "`, `".join(_json_list(item.get("executable_names"))) or "-",
                _token(item.get("source_file")) or "-",
                "yes" if bool(item.get("calls_appshell_main")) else "no",
                "yes" if bool(item.get("ui_adapter_invoked")) else "no",
                "yes" if bool(item.get("ipc_endpoint_started")) else "no",
                "yes" if bool(item.get("supervisor_involvement")) else "no",
            )
        )
    lines.extend(
        [
            "",
            "## AppShell Bypasses",
            "",
        ]
    )
    if not bypasses:
        lines.append("- None detected.")
    else:
        for row in bypasses:
            item = _json_map(row)
            lines.append(
                "- `{}`: {} [{}]".format(
                    _token(item.get("path")),
                    _token(item.get("message")),
                    ", ".join(_json_list(item.get("product_ids"))) or "unknown",
                )
            )
    lines.append("")
    return "\n".join(lines)


def _render_platform_renderer_surface(report: Mapping[str, object]) -> str:
    surface = _json_map(report.get("platform_renderer_surface"))
    lines = [
        "# Platform And Renderer Surface",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "| Backend | Path | Products | Platform Gated | Unused | References |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in _json_list(surface.get("backends")):
        item = _json_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("backend_id")),
                _token(item.get("path")),
                "`, `".join(_json_list(item.get("products"))) or "-",
                "yes" if bool(item.get("platform_gated")) else "no",
                "yes" if bool(item.get("unused")) else "no",
                "`, `".join(_json_list(item.get("referenced_by"))) or "-",
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_validation_stack(report: Mapping[str, object]) -> str:
    surface = _json_map(report.get("validation_surface"))
    lines = [
        "# Validation Stack Map",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "| Path | Layer | Product | Consolidation Target |",
        "| --- | --- | --- | --- |",
    ]
    for row in _json_list(surface.get("rows")):
        item = _json_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("path")),
                _token(item.get("layer")),
                _token(item.get("product")),
                _token(item.get("consolidation_target")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_stability_coverage(report: Mapping[str, object]) -> str:
    coverage = _json_map(report.get("stability_coverage"))
    registry_validation = _json_map(coverage.get("registry_validation"))
    pack_manifests = _json_map(coverage.get("pack_manifests"))
    artifact_manifests = _json_map(coverage.get("artifact_manifests"))
    lines = [
        "# Stability Coverage Report",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "## Registry Coverage",
        "",
        "- Result: `{}`".format(_token(registry_validation.get("result")) or "unknown"),
        "- Fingerprint: `{}`".format(_token(registry_validation.get("deterministic_fingerprint")) or "missing"),
        "- Missing registry entries: `{}`".format(len(_json_list(registry_validation.get("missing_entries")))),
        "",
    ]
    for row in _json_list(registry_validation.get("missing_entries")):
        item = _json_map(row)
        lines.append("- `{}` :: `{}` :: {}".format(_token(item.get("file_path")), _token(item.get("path")), _token(item.get("message"))))
    lines.extend(
        [
            "",
            "## Pack Manifests",
            "",
            "- Missing stability paths: `{}`".format(len(_json_list(pack_manifests.get("missing_stability_paths")))),
        ]
    )
    for path in _json_list(pack_manifests.get("missing_stability_paths")):
        lines.append("- `{}`".format(_token(path)))
    lines.extend(
        [
            "",
            "## Artifact Manifests",
            "",
            "- Missing stability paths: `{}`".format(len(_json_list(artifact_manifests.get("missing_stability_paths")))),
        ]
    )
    for path in _json_list(artifact_manifests.get("missing_stability_paths")):
        lines.append("- `{}`".format(_token(path)))
    lines.append("")
    return "\n".join(lines)


def _render_duplication_report(report: Mapping[str, object]) -> str:
    duplication = _json_map(report.get("duplication"))
    lines = [
        "# Module Duplication Report",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "## Semantic Engines",
        "",
        "| Topic | Symbol | Expected Path | Occurrences |",
        "| --- | --- | --- | --- |",
    ]
    for row in _json_list(duplication.get("semantic_engines")):
        item = _json_map(row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("topic")),
                _token(item.get("symbol")),
                _token(item.get("expected_path")),
                int(item.get("occurrence_count", 0) or 0),
            )
        )
    lines.extend(
        [
            "",
            "## Validation Entrypoints",
            "",
        ]
    )
    if not _json_list(duplication.get("validation_entrypoints")):
        lines.append("- None detected.")
    else:
        for row in _json_list(duplication.get("validation_entrypoints")):
            item = _json_map(row)
            lines.append("- `{}` :: `{}`".format(_token(item.get("path")), "`, `".join(_json_list(item.get("entrypoints"))) or "no entrypoints"))
    lines.extend(
        [
            "",
            "## Product Main Bypasses",
            "",
        ]
    )
    if not _json_list(duplication.get("product_main_bypasses")):
        lines.append("- None detected.")
    else:
        for row in _json_list(duplication.get("product_main_bypasses")):
            item = _json_map(row)
            lines.append("- `{}`: {}".format(_token(item.get("path")), _token(item.get("message"))))
    lines.extend(
        [
            "",
            "## Path Resolution Surfaces",
            "",
        ]
    )
    for row in _json_list(duplication.get("path_resolution_candidates")):
        lines.append("- `{}`".format(_token(_json_map(row).get("path"))))
    lines.extend(
        [
            "",
            "## RNG Initialization Surfaces",
            "",
        ]
    )
    for row in _json_list(duplication.get("rng_initialization_candidates")):
        lines.append("- `{}`".format(_token(_json_map(row).get("path"))))
    lines.append("")
    return "\n".join(lines)


def _render_final_report(report: Mapping[str, object]) -> str:
    summary = _json_map(report.get("summary"))
    entrypoint_map = _json_map(report.get("entrypoint_map"))
    unknown_rows = unknown_inventory_entries(report)
    lines = [
        "# Repo Review 2 Final",
        "",
        "Status: `DERIVED`",
        "Source: `tools/review/tool_repo_inventory.py`",
        "",
        "## Module Inventory Summary",
        "",
        "- Result: `{}`".format(_token(report.get("result")) or "unknown"),
        "- Inventory fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint")) or "missing"),
        "- Entries scanned: `{}`".format(int(report.get("entry_count", 0) or 0)),
        "- Unknown layer entries: `{}`".format(int(summary.get("unknown_entry_count", 0) or 0)),
        "",
        "## Product Map",
        "",
        "- Product registry entries: `{}`".format(int(_json_map(report.get("products")).get("registry_count", 0) or 0)),
        "- AppShell bypasses: `{}`".format(len(_json_list(entrypoint_map.get("bypasses")))),
        "",
        "## Platform Surface Map",
        "",
        "- Platform-specific heuristic count: `{}`".format(int(summary.get("platform_specific_count", 0) or 0)),
        "- Renderer backends indexed: `{}`".format(len(_json_list(_json_map(report.get("platform_renderer_surface")).get("backends")))),
        "",
        "## Validation Surface Map",
        "",
        "- Validation entrypoints: `{}`".format(len(_json_list(_json_map(report.get("duplication")).get("validation_entrypoints")))),
        "",
        "## Duplication/Drift Findings",
        "",
        "- Semantic surfaces indexed: `{}`".format(len(_json_list(_json_map(report.get("duplication")).get("semantic_engines")))),
        "- Path-resolution heuristic candidates: `{}`".format(len(_json_list(_json_map(report.get("duplication")).get("path_resolution_candidates")))),
        "- RNG initialization heuristic candidates: `{}`".format(len(_json_list(_json_map(report.get("duplication")).get("rng_initialization_candidates")))),
        "",
        "## Stability Coverage Status",
        "",
        "- Registry missing markers: `{}`".format(len(_json_list(_json_map(_json_map(report.get("stability_coverage")).get("registry_validation")).get("missing_entries")))),
        "- Pack manifests missing stability: `{}`".format(len(_json_list(_json_map(_json_map(report.get("stability_coverage")).get("pack_manifests")).get("missing_stability_paths")))),
        "- Artifact manifests missing stability: `{}`".format(len(_json_list(_json_map(_json_map(report.get("stability_coverage")).get("artifact_manifests")).get("missing_stability_paths")))),
        "",
        "## Convergence Risk Areas",
        "",
    ]
    for row in _risk_rows(report):
        item = _json_map(row)
        lines.append("- `{}` `{}`: {}".format(_token(item.get("level")), _token(item.get("area")), _token(item.get("detail"))))
    lines.extend(
        [
            "",
            "## Structural Unknowns",
            "",
        ]
    )
    if not unknown_rows:
        lines.append("- No fatal structural unknowns detected.")
    else:
        for row in unknown_rows:
            item = _json_map(row)
            lines.append("- `{}` :: `{}` :: `{}`".format(_token(item.get("path")), _token(item.get("module_name")), _token(item.get("responsibility"))))
    lines.append("")
    return "\n".join(lines)


def render_report_bundle(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    planned_paths = (
        INVENTORY_JSON_REL,
        TREE_INDEX_MD_REL,
        MODULE_DUPLICATION_REPORT_REL,
        ENTRYPOINT_MAP_REL,
        PLATFORM_RENDERER_SURFACE_REL,
        VALIDATION_STACK_MAP_REL,
        STABILITY_COVERAGE_REPORT_REL,
        FINAL_REPORT_REL,
    )
    return {
        TREE_INDEX_MD_REL: _render_tree(repo_root, planned_paths),
        MODULE_DUPLICATION_REPORT_REL: _render_duplication_report(report),
        ENTRYPOINT_MAP_REL: _render_entrypoint_map(report),
        PLATFORM_RENDERER_SURFACE_REL: _render_platform_renderer_surface(report),
        VALIDATION_STACK_MAP_REL: _render_validation_stack(report),
        STABILITY_COVERAGE_REPORT_REL: _render_stability_coverage(report),
        FINAL_REPORT_REL: _render_final_report(report),
    }


def write_repo_inventory_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    payload = dict(report)
    abs_inventory_path = _repo_abs(root, INVENTORY_JSON_REL)
    os.makedirs(os.path.dirname(abs_inventory_path), exist_ok=True)
    with open(abs_inventory_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")
    written = {INVENTORY_JSON_REL: abs_inventory_path}
    for rel_path, text in render_report_bundle(root, payload).items():
        abs_path = _repo_abs(root, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path
    return dict(sorted(written.items()))


__all__ = [
    "ENTRYPOINT_MAP_REL",
    "FINAL_REPORT_REL",
    "INVENTORY_JSON_REL",
    "MODULE_DUPLICATION_REPORT_REL",
    "PLATFORM_RENDERER_SURFACE_REL",
    "SCAN_ROOTS",
    "STABILITY_COVERAGE_REPORT_REL",
    "TREE_INDEX_MD_REL",
    "VALIDATION_STACK_MAP_REL",
    "build_repo_inventory",
    "load_json_if_present",
    "load_or_run_inventory_report",
    "render_report_bundle",
    "scan_product_main_bypasses",
    "unknown_inventory_entries",
    "write_repo_inventory_outputs",
]
