#!/usr/bin/env python3
"""Validate the active C17/C++17 language baseline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


CONTRACT_REL = Path("contracts/build/language_baseline.contract.toml")
SCHEMA_REL = Path("contracts/build/language_subset.schema.json")
ACTIVE_CMAKE_EXCLUDES = ("/archive/", "/out/", "/build/", "/.dominium.local/", "/.aide.local/")
LEGACY_LANG_MODE_ALLOWED_MARKERS = (
    "vc6",
    "vc71",
    "xcode3",
    "gcc295",
    "cw_classic",
    "vs2015",
    "legacy",
    "classic",
)


def normalize(path) -> str:
    return str(path).replace("\\", "/")


def strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_quote:
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if char == "#" and not in_quote:
            return line[:index]
    return line


def parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_value(item.strip()) for item in inner.split(",")]
    try:
        return int(raw)
    except ValueError:
        return raw


def minimal_toml_load(path: Path) -> dict:
    root: dict = {}
    current = root
    for lineno, original in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_comment(original).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            raise ValueError("invalid TOML line {0}: {1}".format(lineno, original))
        key, value = line.split("=", 1)
        current[key.strip()] = parse_value(value)
    return root


def load_toml(path: Path) -> dict:
    if tomllib is not None:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    return minimal_toml_load(path)


def finding(level: str, code: str, path: str, message: str, line=None) -> dict:
    item = {"level": level, "code": code, "path": path, "message": message}
    if line is not None:
        item["line"] = line
    return item


def active_cmake_files(repo_root: Path) -> list[Path]:
    files = [repo_root / "CMakeLists.txt"]
    files.extend(repo_root.rglob("CMakeLists.txt"))
    files.extend((repo_root / "cmake").rglob("*.cmake") if (repo_root / "cmake").is_dir() else [])
    unique: list[Path] = []
    seen = set()
    for path in files:
        if not path.is_file():
            continue
        rel = "/" + normalize(path.relative_to(repo_root))
        if any(marker in rel for marker in ACTIVE_CMAKE_EXCLUDES):
            continue
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return sorted(unique, key=lambda p: normalize(p.relative_to(repo_root)).lower())


def check_contract(repo_root: Path, findings: list[dict]) -> None:
    contract_path = repo_root / CONTRACT_REL
    if not contract_path.exists():
        findings.append(finding("error", "contract_missing", normalize(CONTRACT_REL), "language baseline contract is missing"))
        return
    try:
        data = load_toml(contract_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(finding("error", "contract_parse_failed", normalize(CONTRACT_REL), str(exc)))
        return
    baseline = data.get("baseline", {})
    expected = {
        "c_standard": "c17",
        "c_standard_number": 17,
        "cxx_standard": "cpp17",
        "cxx_standard_number": 17,
        "c_extensions": False,
        "cxx_extensions": False,
        "active_lang_mode": "c17_cpp17",
    }
    for key, value in expected.items():
        if baseline.get(key) != value:
            findings.append(finding("error", "contract_baseline_mismatch", normalize(CONTRACT_REL), "baseline.{0} must be {1!r}".format(key, value)))
    schema_path = repo_root / SCHEMA_REL
    if not schema_path.exists():
        findings.append(finding("error", "schema_missing", normalize(SCHEMA_REL), "language subset schema is missing"))
    else:
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            findings.append(finding("error", "schema_parse_failed", normalize(SCHEMA_REL), str(exc)))


def check_cmake(repo_root: Path, findings: list[dict]) -> int:
    checked = 0
    root_text = (repo_root / "CMakeLists.txt").read_text(encoding="utf-8")
    for pattern, message in [
        (r"set\s*\(\s*CMAKE_C_STANDARD\s+17\s*\)", "root CMake must set CMAKE_C_STANDARD 17"),
        (r"set\s*\(\s*CMAKE_CXX_STANDARD\s+17\s*\)", "root CMake must set CMAKE_CXX_STANDARD 17"),
        (r"set\s*\(\s*CMAKE_C_EXTENSIONS\s+OFF\s*\)", "root CMake must disable C extensions"),
        (r"set\s*\(\s*CMAKE_CXX_EXTENSIONS\s+OFF\s*\)", "root CMake must disable C++ extensions"),
    ]:
        if not re.search(pattern, root_text):
            findings.append(finding("error", "root_cmake_baseline_missing", "CMakeLists.txt", message))

    old_patterns = [
        (re.compile(r"\bC_STANDARD\s+90\b"), "target C_STANDARD 90 is retired from active mainline"),
        (re.compile(r"\bCXX_STANDARD\s+98\b"), "target CXX_STANDARD 98 is retired from active mainline"),
        (re.compile(r"CMAKE_C_STANDARD[^\\n]*90"), "CMAKE_C_STANDARD 90 is retired from active mainline"),
        (re.compile(r"CMAKE_CXX_STANDARD[^\\n]*98"), "CMAKE_CXX_STANDARD 98 is retired from active mainline"),
    ]
    for path in active_cmake_files(repo_root):
        checked += 1
        rel = normalize(path.relative_to(repo_root))
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for pattern, message in old_patterns:
                if pattern.search(line):
                    findings.append(finding("error", "active_cmake_legacy_standard", rel, message, line_no))
    return checked


def check_presets(repo_root: Path, findings: list[dict]) -> None:
    path = repo_root / "CMakePresets.json"
    if not path.exists():
        findings.append(finding("error", "presets_missing", "CMakePresets.json", "CMakePresets.json is missing"))
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        findings.append(finding("error", "presets_parse_failed", "CMakePresets.json", str(exc)))
        return
    for preset in data.get("configurePresets", []):
        if not isinstance(preset, dict):
            continue
        name = str(preset.get("name", ""))
        cache = preset.get("cacheVariables", {})
        if not isinstance(cache, dict):
            continue
        c_std = cache.get("CMAKE_C_STANDARD")
        cxx_std = cache.get("CMAKE_CXX_STANDARD")
        if c_std is not None and str(c_std) != "17":
            findings.append(finding("error", "preset_c_standard_not_c17", "CMakePresets.json", "configure preset {0} sets CMAKE_C_STANDARD={1}".format(name, c_std)))
        if cxx_std is not None and str(cxx_std) != "17":
            findings.append(finding("error", "preset_cxx_standard_not_cpp17", "CMakePresets.json", "configure preset {0} sets CMAKE_CXX_STANDARD={1}".format(name, cxx_std)))
        lang_mode = cache.get("DOM_LANG_MODE")
        if lang_mode == "c89_cpp98" and not any(marker in name.lower() for marker in LEGACY_LANG_MODE_ALLOWED_MARKERS):
            findings.append(finding("error", "active_preset_legacy_lang_mode", "CMakePresets.json", "configure preset {0} uses retired DOM_LANG_MODE=c89_cpp98".format(name)))
        if lang_mode == "c89_cpp98":
            findings.append(finding("warning", "legacy_projection_lang_mode", "CMakePresets.json", "legacy projection preset {0} remains outside active mainline".format(name)))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: list[dict] = []
    check_contract(repo_root, findings)
    cmake_files_checked = check_cmake(repo_root, findings)
    check_presets(repo_root, findings)

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    result = {
        "schema_version": "dominium.build.language_baseline.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "strict": bool(args.strict),
        "cmake_files_checked": cmake_files_checked,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("language baseline validation: {0}".format(result["status"]))
        print("cmake files: {0} errors: {1} warnings: {2}".format(cmake_files_checked, len(errors), len(warnings)))
        for item in findings[:80]:
            loc = item["path"] + (":{0}".format(item["line"]) if "line" in item else "")
            print("{0} {1}: {2}: {3}".format(item["level"].upper(), item["code"], loc, item["message"]))
        if len(findings) > 80:
            print("... {0} additional findings omitted; use --json for full detail".format(len(findings) - 80))
    if args.strict and errors:
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
