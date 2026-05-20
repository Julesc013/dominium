#!/usr/bin/env python3
"""Validate obvious public C API/ABI header constraints."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


CONTRACT_REL = Path("contracts/abi/c_api.contract.toml")
SURFACE_REGISTRY_REL = Path("contracts/public_surface/public_surface.contract.toml")
HEADER_EXTS = {".h", ".hh", ".hpp", ".hxx"}
STABLE_CLASSES = {"frozen_abi", "stable_api", "stable_data_contract", "stable_command_contract", "stable_protocol"}
CPP_STL_INCLUDES = {
    "string",
    "vector",
    "map",
    "set",
    "unordered_map",
    "unordered_set",
    "list",
    "deque",
    "array",
    "memory",
    "functional",
    "future",
    "thread",
    "mutex",
    "optional",
    "variant",
    "span",
    "stdexcept",
}
PLATFORM_INCLUDE_PATTERNS = (
    "windows.h",
    "winsock",
    "unistd.h",
    "pthread.h",
    "cocoa/",
    "opengl/",
    "gl/",
    "d3d",
    "direct3d",
    "vulkan",
    "metal/",
    "sdl",
)
PRIVATE_INCLUDE_MARKERS = ("/private/", "/_internal/", "source/", "sources/", "archive/", "tools/")
INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]([^\">]+)[\">]")
FUNC_DECL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*;")
TYPEDEF_RE = re.compile(r"\btypedef\b(?P<body>[^;{]+?)\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;")
STRUCT_START_RE = re.compile(r"\btypedef\s+struct\s+([A-Za-z_][A-Za-z0-9_]*)?\s*\{")
STRUCT_NAME_RE = re.compile(r"}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;")


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out = []
    for ch in line:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            out.append(ch)
            continue
        if ch == "#" and not in_quote:
            break
        out.append(ch)
    return "".join(out).strip()


def _split_array_items(raw: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    in_quote = False
    escaped = False
    for ch in raw:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            current.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            current.append(ch)
            continue
        if ch == "," and not in_quote:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue
        current.append(ch)
    item = "".join(current).strip()
    if item:
        items.append(item)
    return items


def _parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item) for item in _split_array_items(inner)]
    try:
        return int(raw)
    except ValueError:
        return raw


def _minimal_toml_load(text: str) -> dict:
    root: dict = {}
    current = root
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            current = {}
            root.setdefault(section, []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = root
            for part in section.split("."):
                current = current.setdefault(part, {})
            continue
        if "=" not in line:
            raise ValueError("invalid TOML line {0}: {1}".format(lineno, original))
        key, raw_value = line.split("=", 1)
        current[key.strip()] = _parse_value(raw_value)
    return root


def load_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def normalize(path: Path | str) -> str:
    return str(path).replace("\\", "/").strip("/")


def remove_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def finding(level: str, code: str, path: str, message: str, line: int | None = None) -> dict:
    item = {"level": level, "code": code, "path": path, "message": message}
    if line is not None:
        item["line"] = line
    return item


def load_surface_metadata(repo_root: Path, override: str | None) -> list[dict]:
    path = repo_root / (override if override else SURFACE_REGISTRY_REL)
    if not path.exists():
        return []
    try:
        data = load_toml(path)
    except Exception:
        return []
    surfaces = data.get("surface", [])
    if not isinstance(surfaces, list):
        return []
    return [item for item in surfaces if isinstance(item, dict)]


def surface_for_path(rel: str, surfaces: list[dict]) -> dict:
    best: dict = {}
    best_len = -1
    for surface in surfaces:
        surface_path = normalize(str(surface.get("path", "")))
        if surface_path and (rel == surface_path or rel.startswith(surface_path + "/")):
            if len(surface_path) > best_len:
                best = surface
                best_len = len(surface_path)
    return best


def candidate_roots(repo_root: Path) -> list[tuple[Path, str, str]]:
    roots: list[tuple[Path, str, str]] = []
    for rel, owner, namespace in [
        ("engine/include", "engine", "domino"),
        ("runtime/include", "runtime", "domino"),
        ("game/include", "game", "dominium"),
    ]:
        path = repo_root / rel
        if path.is_dir():
            roots.append((path, owner, namespace))
    apps = repo_root / "apps"
    if apps.is_dir():
        for child in sorted(apps.iterdir(), key=lambda p: p.name.lower()):
            path = child / "include"
            if path.is_dir():
                roots.append((path, "apps." + child.name, "dominium"))
    return roots


def iter_headers(root: Path, include_private: bool) -> list[Path]:
    headers: list[Path] = []
    for path in sorted(root.rglob("*"), key=lambda p: normalize(p.relative_to(root)).lower()):
        if not path.is_file() or path.suffix.lower() not in HEADER_EXTS:
            continue
        rel = normalize(path)
        if not include_private and ("/_internal/" in rel or "/private/" in rel):
            continue
        headers.append(path)
    return headers


def header_has_guard(text: str) -> bool:
    if re.search(r"^\s*#\s*pragma\s+once\b", text, flags=re.M):
        return True
    first_lines = "\n".join(text.splitlines()[:80])
    return bool(re.search(r"^\s*#\s*ifndef\s+[A-Za-z0-9_]+\s*$", first_lines, flags=re.M) and re.search(r"^\s*#\s*define\s+[A-Za-z0-9_]+\s*$", first_lines, flags=re.M))


def is_stable_surface(surface: dict) -> bool:
    return str(surface.get("stability", "")) in STABLE_CLASSES


def severity(code: str, owner: str, stable: bool, fixture_mode: bool) -> str:
    if fixture_mode:
        if code in {
            "missing_guard",
            "cpp_public_abi",
            "stl_public_abi",
            "platform_engine_header",
            "private_header_include",
            "engine_cross_boundary_include",
        }:
            return "error"
    if code in {"platform_engine_header", "engine_cross_boundary_include"}:
        return "error"
    if stable and code in {
        "missing_guard",
        "cpp_public_abi",
        "stl_public_abi",
        "private_header_include",
        "unprefixed_public_symbol",
        "unprefixed_public_typedef",
        "abi_struct_without_struct_size",
        "callback_without_user_pointer",
    }:
        return "error"
    if owner.startswith("apps.") and code in {"missing_guard", "private_header_include"}:
        return "warning"
    return "warning"


def line_number_for(text: str, token: str) -> int | None:
    for idx, line in enumerate(text.splitlines(), 1):
        if token in line:
            return idx
    return None


def includes_from_text(text: str) -> list[tuple[int, str]]:
    includes: list[tuple[int, str]] = []
    for idx, line in enumerate(text.splitlines(), 1):
        match = INCLUDE_RE.match(line)
        if match:
            includes.append((idx, match.group(1).replace("\\", "/")))
    return includes


def scan_struct_blocks(clean: str) -> list[tuple[str, str, int]]:
    blocks: list[tuple[str, str, int]] = []
    lines = clean.splitlines()
    idx = 0
    while idx < len(lines):
        if STRUCT_START_RE.search(lines[idx]):
            start = idx
            content = [lines[idx]]
            idx += 1
            while idx < len(lines):
                content.append(lines[idx])
                if "}" in lines[idx] and ";" in lines[idx]:
                    block = "\n".join(content)
                    match = STRUCT_NAME_RE.search(block)
                    if match:
                        blocks.append((match.group(1), block, start + 1))
                    break
                idx += 1
        idx += 1
    return blocks


def inspect_header(path: Path, repo_root: Path, owner: str, namespace: str, surface: dict, fixture_mode: bool) -> tuple[dict, list[dict]]:
    rel = normalize(path.relative_to(repo_root))
    text = path.read_text(encoding="utf-8", errors="ignore")
    clean = remove_comments(text)
    stable = is_stable_surface(surface)
    findings: list[dict] = []
    allowed_symbol_prefixes = ("domino_", "dominium_")
    allowed_macro_prefixes = ("DOMINO_", "DOMINIUM_")
    legacy_prefixes = ("dom_", "d_")

    def add(code: str, message: str, line: int | None = None) -> None:
        findings.append(finding(severity(code, owner, stable, fixture_mode), code, rel, message, line))

    if not header_has_guard(text):
        add("missing_guard", "public header should have include guard or #pragma once")

    for line_no, include in includes_from_text(text):
        low = include.lower()
        if low in CPP_STL_INCLUDES:
            add("stl_public_abi", "public C ABI should not include C++ standard library header <{0}>".format(include), line_no)
        if (owner == "engine" or fixture_mode) and any(pattern in low for pattern in PLATFORM_INCLUDE_PATTERNS):
            add("platform_engine_header", "engine public header must not include platform header <{0}>".format(include), line_no)
        if any(marker in "/" + low for marker in PRIVATE_INCLUDE_MARKERS):
            add("private_header_include", "public header should not include private/generated/tooling path {0}".format(include), line_no)
        if owner == "engine" and (low.startswith("dominium/") or low.startswith("launcher/") or low.startswith("dsu/") or low.startswith("dsk/") or low.startswith("domino/app/")):
            add("engine_cross_boundary_include", "engine public header must not include runtime/game/app header {0}".format(include), line_no)

    for pattern, label in [
        (r"^\s*class\s+[A-Za-z_][A-Za-z0-9_]*", "C++ class"),
        (r"^\s*template\s*<", "C++ template"),
        (r"^\s*namespace\s+[A-Za-z_][A-Za-z0-9_]*", "C++ namespace"),
        (r"^\s*(public|private|protected)\s*:", "C++ access specifier"),
    ]:
        for match in re.finditer(pattern, clean, flags=re.M):
            line = clean[: match.start()].count("\n") + 1
            add("cpp_public_abi", "public C ABI should not expose {0}".format(label), line)

    for match in FUNC_DECL_RE.finditer(clean):
        name = match.group(1)
        if name in {"if", "for", "while", "switch", "return", "sizeof", "void", "int", "unsigned", "signed", "char", "long", "short", "float", "double"}:
            continue
        if name.isupper():
            continue
        prefix_ok = name.startswith(allowed_symbol_prefixes)
        legacy_ok = name.startswith(legacy_prefixes)
        if not prefix_ok:
            line = clean[: match.start()].count("\n") + 1
            if legacy_ok:
                add("legacy_public_symbol_prefix", "legacy public symbol uses {0}; stable ABI promotion requires domino_/dominium_ or explicit exception".format(name), line)
            else:
                add("unprefixed_public_symbol", "public function-like declaration is not prefixed domino_/dominium_: {0}".format(name), line)

    for match in TYPEDEF_RE.finditer(clean):
        name = match.group("name")
        if name in {"u8", "i8", "u16", "i16", "u32", "i32", "u64", "i64", "d_bool", "size_t", "int8_t", "uint8_t", "int16_t", "uint16_t", "int32_t", "uint32_t", "int64_t", "uint64_t", "bool"}:
            continue
        prefix_ok = name.startswith(allowed_symbol_prefixes) and name.endswith("_t")
        legacy_ok = name.startswith(legacy_prefixes)
        if not prefix_ok:
            line = clean[: match.start()].count("\n") + 1
            if legacy_ok:
                add("legacy_public_typedef_prefix", "legacy public typedef uses {0}; stable ABI promotion requires domino_*_t/dominium_*_t or explicit exception".format(name), line)
            else:
                add("unprefixed_public_typedef", "public typedef is not named domino_*_t/dominium_*_t: {0}".format(name), line)

    for struct_name, block, line in scan_struct_blocks(clean):
        lowered = struct_name.lower()
        abi_like = any(token in lowered for token in ("config", "options", "option", "desc", "descriptor", "args", "params", "info", "vtable", "api"))
        if abi_like and "struct_size" not in block:
            add("abi_struct_without_struct_size", "ABI-like struct {0} should include struct_size before stable promotion".format(struct_name), line)
        if "(*" in block and "void *user" not in block and "void* user" not in block:
            add("callback_without_user_pointer", "callback-bearing struct {0} should carry void *user ownership context".format(struct_name), line)

    summary = {
        "path": rel,
        "owner": owner,
        "namespace": namespace,
        "surface_id": surface.get("id", ""),
        "stability": surface.get("stability", "unregistered"),
        "finding_count": len(findings),
        "error_count": sum(1 for item in findings if item["level"] == "error"),
        "warning_count": sum(1 for item in findings if item["level"] == "warning"),
    }
    return summary, findings


def run_fixture_checks(repo_root: Path) -> tuple[list[dict], list[dict]]:
    fixture_dir = repo_root / "tests" / "contract" / "public_headers" / "fixtures"
    summaries: list[dict] = []
    findings: list[dict] = []
    if not fixture_dir.is_dir():
        return summaries, [finding("error", "fixture_dir_missing", normalize(fixture_dir.relative_to(repo_root)), "fixture directory is missing")]
    for header in sorted(fixture_dir.glob("*.h"), key=lambda p: p.name.lower()):
        expected_valid = header.name.startswith("valid_")
        expected_invalid = header.name.startswith("invalid_")
        surface = {"id": "dominium.tests.public_header_fixtures.v1", "stability": "fixture"}
        summary, header_findings = inspect_header(header, repo_root, "tests", "domino", surface, fixture_mode=True)
        is_valid = not any(item["level"] == "error" for item in header_findings)
        if expected_valid and not is_valid:
            findings.append(finding("error", "fixture_expected_valid_failed", summary["path"], "valid fixture produced header errors"))
            findings.extend(header_findings)
        elif expected_invalid and is_valid:
            findings.append(finding("error", "fixture_expected_invalid_passed", summary["path"], "invalid fixture did not produce an error"))
        elif expected_invalid:
            pass
        else:
            findings.extend(header_findings)
        summaries.append(summary)
    return summaries, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--strict", action="store_true", help="fail on high-confidence violations")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--list", action="store_true", help="list inspected public header candidates")
    parser.add_argument("--include-private", action="store_true", help="include _internal/private headers under include roots")
    parser.add_argument("--surface-registry", help="override public surface registry path")
    parser.add_argument("--fixtures", action="store_true", help="run public-header fixture expectations")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    contract_path = repo_root / CONTRACT_REL
    findings: list[dict] = []
    summaries: list[dict] = []

    if contract_path.exists():
        try:
            load_toml(contract_path)
        except Exception as exc:  # noqa: BLE001 - report parser failure
            findings.append(finding("error", "contract_parse_failed", normalize(CONTRACT_REL), str(exc)))
    else:
        findings.append(finding("error", "contract_missing", normalize(CONTRACT_REL), "ABI C API contract is missing"))

    surfaces = load_surface_metadata(repo_root, args.surface_registry)
    if args.fixtures:
        fixture_summaries, fixture_findings = run_fixture_checks(repo_root)
        summaries.extend(fixture_summaries)
        findings.extend(fixture_findings)
    else:
        for root, owner, namespace in candidate_roots(repo_root):
            for header in iter_headers(root, include_private=args.include_private):
                rel = normalize(header.relative_to(repo_root))
                surface = surface_for_path(rel, surfaces)
                summary, header_findings = inspect_header(header, repo_root, owner, namespace, surface, fixture_mode=False)
                summaries.append(summary)
                findings.extend(header_findings)

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    status = "PASS" if not errors else "FAIL"
    result = {
        "schema_version": "dominium.abi.public_header_validation_result.v1",
        "status": status,
        "strict": bool(args.strict),
        "fixtures": bool(args.fixtures),
        "headers_inspected": len(summaries),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "by_owner": {},
        "by_stability": {},
        "findings": findings,
        "headers": summaries,
    }
    for summary in summaries:
        owner = str(summary.get("owner", "unknown"))
        stability = str(summary.get("stability", "unregistered"))
        result["by_owner"][owner] = result["by_owner"].get(owner, 0) + 1
        result["by_stability"][stability] = result["by_stability"].get(stability, 0) + 1

    if args.list:
        for summary in summaries:
            print("{0} [{1}] {2}".format(summary["path"], summary["owner"], summary["stability"]))

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif not args.list:
        print("public header ABI validation: {0}".format(status))
        print("headers: {0} errors: {1} warnings: {2}".format(len(summaries), len(errors), len(warnings)))
        for item in findings[:80]:
            location = item["path"]
            if "line" in item:
                location += ":{0}".format(item["line"])
            print("{0} {1}: {2}: {3}".format(item["level"].upper(), item["code"], location, item["message"]))
        remaining = len(findings) - 80
        if remaining > 0:
            print("... {0} additional findings omitted from text output; use --json for full detail".format(remaining))

    if args.strict and errors:
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
