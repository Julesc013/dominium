#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import re
import sys


SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".inc", ".ipp",
    ".m", ".mm",
}

SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "docs",
    "schema",
    "third_party",
    "external",
    "deps",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')

FORBIDDEN_ENGINE_REF_PREFIXES = ("game/", "launcher/", "setup/", "tools/")
FORBIDDEN_ENGINE_REF_CONTAINS = ("/game/", "/launcher/", "/setup/", "/tools/")

FORBIDDEN_PLATFORM_HEADERS = {
    "windows.h",
    "x11/xlib.h",
    "x11/xutil.h",
    "x11/x.h",
    "gl/gl.h",
    "gl/glu.h",
    "opengl/gl.h",
    "vulkan/vulkan.h",
    "metal/metal.h",
    "d3d9.h",
    "d3d11.h",
    "d3d12.h",
    "dxgi.h",
    "dxgi1_2.h",
    "sdl.h",
    "sdl2/sdl.h",
    "sdl2/sdl_opengl.h",
}

AUTHORITATIVE_DIRS = (
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
    os.path.join("game", "economy"),
)

FLOAT_TOKENS_RE = re.compile(r"\b(long\s+double|double|float)\b")
MATH_CALL_RE = re.compile(r"\b(sin|cos|tan|asin|acos|atan|atan2|sqrt|pow|exp|log)\s*\(")
FORBIDDEN_MATH_HEADERS = ("math.h", "cmath")

FORBIDDEN_TIME_HEADERS = ("time.h", "sys/time.h", "sys/timeb.h", "chrono", "ctime")
TIME_CALL_RE = re.compile(
    r"\b(time|clock_gettime|gettimeofday|QueryPerformanceCounter|GetSystemTime|"
    r"GetTickCount|GetTickCount64|mach_absolute_time)\s*\("
)
TIME_STD_RE = re.compile(r"\bstd::chrono::|\bchrono::")

FORBIDDEN_RNG_HEADERS = ("random",)
RNG_CALL_RE = re.compile(
    r"\b(rand|srand|rand_r|random|arc4random|drand48|lrand48|mrand48|getrandom|"
    r"BCryptGenRandom|RtlGenRandom|CryptGenRandom)\s*\("
)
RNG_STD_RE = re.compile(
    r"\bstd::(random_device|mt19937|mt19937_64|seed_seq|uniform_|normal_|"
    r"bernoulli|binomial|poisson)\b"
)

UNORDERED_RE = re.compile(r"\bunordered_(map|set|multimap|multiset)\b")

UI_FORBIDDEN_INCLUDES = (
    "engine/modules/",
    "domino/dsim.h",
    "domino/dworld.h",
    "domino/dspace_graph.h",
    "domino/state/",
    "domino/sim/",
)
UI_FORBIDDEN_CALL_RE = re.compile(r"\b(dg?_sim_|dg?_world_|dg?_state_)\w*\s*\(")

RENDER_TOKENS = (
    "d3d9",
    "d3d11",
    "d3d12",
    "dx9",
    "dx11",
    "dx12",
    "vulkan",
    "vk",
    "metal",
    "opengl",
    "gl1",
    "gl2",
    "gl3",
    "gl4",
    "gles",
    "gl",
    "sw",
    "soft",
    "software",
)

GLOBAL_ITER_PATTERNS = [
    re.compile(r"\bupdate_all\b"),
    re.compile(r"\btick_all\b"),
    re.compile(r"\biterate_all\b"),
    re.compile(r"\bupdate_everything\b"),
    re.compile(r"\bfor_each_entity\b"),
    re.compile(r"\biterate_all_systems\b"),
]


class Check(object):
    def __init__(self, check_id, description, remediation, severity="error"):
        self.check_id = check_id
        self.description = description
        self.remediation = remediation
        self.severity = severity
        self.violations = []

    def add_violation(self, path, line, detail):
        self.violations.append((path, line, detail))

    def has_failures(self, strict=False):
        if not self.violations:
            return False
        if self.severity == "error":
            return True
        return strict


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def normalize_include(path):
    cleaned = path.replace("\\", "/")
    while cleaned.startswith("../"):
        cleaned = cleaned[3:]
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def iter_files(root, repo_root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = repo_rel(repo_root, dirpath)
        parts = rel.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in SOURCE_EXTS:
                continue
            yield os.path.join(dirpath, filename)


def iter_include_lines(path):
    in_block = False
    try:
        with open(path, "r", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                work = line
                if in_block:
                    end = work.find("*/")
                    if end == -1:
                        continue
                    work = work[end + 2:]
                    in_block = False
                while True:
                    start = work.find("/*")
                    if start == -1:
                        break
                    end = work.find("*/", start + 2)
                    if end == -1:
                        work = work[:start]
                        in_block = True
                        break
                    work = work[:start] + work[end + 2:]
                if "//" in work:
                    work = work.split("//", 1)[0]
                yield idx, work
    except IOError:
        return


def iter_code_lines(path):
    in_block = False
    in_string = None
    try:
        with open(path, "r", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                i = 0
                out = ""
                while i < len(line):
                    ch = line[i]
                    nxt = line[i:i + 2]
                    if in_block:
                        if nxt == "*/":
                            in_block = False
                            i += 2
                            continue
                        i += 1
                        continue
                    if in_string:
                        if ch == "\\":
                            i += 2
                            continue
                        if ch == in_string:
                            in_string = None
                        i += 1
                        continue
                    if nxt == "//":
                        break
                    if nxt == "/*":
                        in_block = True
                        i += 2
                        continue
                    if ch in ("'", '"'):
                        in_string = ch
                        i += 1
                        continue
                    out += ch
                    i += 1
                yield idx, out
    except IOError:
        return


def scan_includes(root, repo_root, include_predicate, check):
    for path in iter_files(root, repo_root):
        rel = repo_rel(repo_root, path)
        for idx, code in iter_include_lines(path):
            match = INCLUDE_RE.match(code)
            if not match:
                continue
            include_path = normalize_include(match.group(1))
            if include_predicate(include_path):
                check.add_violation(rel, idx, include_path)


def scan_engine_refs(repo_root, check):
    engine_root = os.path.join(repo_root, "engine")
    for path in iter_files(engine_root, repo_root):
        rel = repo_rel(repo_root, path)
        for idx, code in iter_include_lines(path):
            match = INCLUDE_RE.match(code)
            if not match:
                continue
            include_path = normalize_include(match.group(1))
            include_norm = "/" + include_path
            if include_path.startswith(FORBIDDEN_ENGINE_REF_PREFIXES) or any(
                token in include_norm for token in FORBIDDEN_ENGINE_REF_CONTAINS
            ):
                check.add_violation(rel, idx, include_path)


def scan_cmake_for_link_edges(repo_root, check, target_name, forbidden_targets):
    cmake_files = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel = repo_rel(repo_root, dirpath)
        parts = rel.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename != "CMakeLists.txt":
                continue
            cmake_files.append(os.path.join(dirpath, filename))

    def strip_comment(line):
        if line.lstrip().startswith("#"):
            return ""
        if "#" in line:
            return line.split("#", 1)[0]
        return line

    for path in cmake_files:
        rel = repo_rel(repo_root, path)
        buffer = ""
        start_line = None
        try:
            with open(path, "r", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    cleaned = strip_comment(line)
                    if not cleaned.strip() and not buffer:
                        continue
                    if "target_link_libraries" not in cleaned and not buffer:
                        continue
                    if not buffer:
                        buffer = cleaned
                        start_line = idx
                    else:
                        buffer += " " + cleaned
                    if ")" not in cleaned:
                        continue
                    match = re.search(r"target_link_libraries\s*\(([^)]+)\)", buffer, re.IGNORECASE)
                    if match:
                        content = match.group(1)
                        tokens = [t.strip() for t in re.split(r"\s+", content) if t.strip()]
                        if tokens:
                            target = tokens[0].strip('"')
                            if target == target_name:
                                for token in tokens[1:]:
                                    token_clean = token.strip('"')
                                    if token_clean in ("PRIVATE", "PUBLIC", "INTERFACE"):
                                        continue
                                    if token_clean.startswith("$<"):
                                        continue
                                    if token_clean in forbidden_targets:
                                        detail = "target_link_libraries({0} ... {1})".format(
                                            target_name, token_clean
                                        )
                                        check.add_violation(rel, start_line or idx, detail)
                    buffer = ""
                    start_line = None
        except IOError:
            continue


def check_arch_inc_001(repo_root):
    check = Check(
        "ARCH-INC-001",
        "game includes engine/modules or platform headers (forbidden)",
        "Include engine public headers under engine/include only; remove platform headers from game.",
    )

    def predicate(include_path):
        lower = include_path.lower()
        if "engine/modules" in lower:
            return True
        return lower in FORBIDDEN_PLATFORM_HEADERS

    scan_includes(os.path.join(repo_root, "game"), repo_root, predicate, check)
    return check


def check_arch_inc_002(repo_root):
    check = Check(
        "ARCH-INC-002",
        "client/server/tools include engine/modules (forbidden)",
        "Include engine public headers under engine/include only.",
    )

    def predicate(include_path):
        return "engine/modules" in include_path.replace("\\", "/").lower()

    for root in ("client", "server", "tools"):
        scan_includes(os.path.join(repo_root, root), repo_root, predicate, check)
    return check


def check_arch_dep_001(repo_root):
    check = Check(
        "ARCH-DEP-001",
        "engine references game/launcher/setup/tools (forbidden)",
        "Remove forbidden references or route via engine public APIs only.",
    )
    scan_engine_refs(repo_root, check)
    forbidden = {
        "dominium_game",
        "game::dominium",
        "launcher_core",
        "launcher::launcher",
        "setup_core",
        "setup::setup",
        "tools_shared",
        "tools::shared",
        "dominium-tools",
        "tools::host",
    }
    scan_cmake_for_link_edges(repo_root, check, "domino_engine", forbidden)
    return check


def check_arch_dep_002(repo_root):
    check = Check(
        "ARCH-DEP-002",
        "game links launcher/setup/libs targets (forbidden)",
        "Remove forbidden links; game must link domino_engine only.",
    )
    forbidden = {
        "launcher_core",
        "launcher::launcher",
        "setup_core",
        "setup::setup",
        "libs_base",
        "libs_crypto",
        "libs_fsmodel",
        "libs_netproto",
        "libs_contracts",
        "libs::base",
        "libs::crypto",
        "libs::fsmodel",
        "libs::netproto",
        "libs::contracts",
    }
    scan_cmake_for_link_edges(repo_root, check, "dominium_game", forbidden)
    return check


def check_arch_render_001(repo_root):
    check = Check(
        "ARCH-RENDER-001",
        "render backend identifiers outside engine/render (forbidden)",
        "Move backend code under engine/render only.",
    )
    engine_render_root = os.path.join(repo_root, "engine", "render")

    def segment_has_token(segment, token):
        if token in ("gl", "sw", "vk"):
            if segment == token:
                return True
            if segment.startswith(token) and len(segment) > len(token):
                return segment[len(token)].isdigit() or segment[len(token)] in ("_", "-")
            return False
        if token == "soft":
            return segment == token or segment.startswith("soft")
        return segment == token or segment.startswith(token + "_") or segment.startswith(token + "-") or segment.startswith(token)

    def path_has_backend_token(rel_path):
        parts = re.split(r"[\\/]", rel_path.lower())
        for part in parts:
            base = part.rsplit(".", 1)[0]
            for token in RENDER_TOKENS:
                if segment_has_token(base, token):
                    return True
        return False
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel_dir = repo_rel(repo_root, dirpath)
        parts = rel_dir.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if os.path.abspath(dirpath).startswith(os.path.abspath(engine_render_root)):
            continue
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in SOURCE_EXTS:
                continue
            rel_path = repo_rel(repo_root, os.path.join(dirpath, filename))
            if path_has_backend_token(rel_path):
                check.add_violation(rel_path, 1, "backend token in path")
    return check


def check_arch_top_001(repo_root):
    check = Check(
        "ARCH-TOP-001",
        "legacy source/ or src/ directories at repo root (forbidden)",
        "Remove the directory or move contents into canonical top-level domains.",
    )
    for name in ("source", "src", "common_source"):
        path = os.path.join(repo_root, name)
        if os.path.isdir(path):
            check.add_violation(name, 1, "top-level directory present")
    return check


def check_ui_bypass_001(repo_root):
    check = Check(
        "UI-BYPASS-001",
        "UI code queries authoritative world state directly (forbidden)",
        "Use EIL/capability snapshot interfaces instead of direct sim/world access.",
    )

    def include_predicate(include_path):
        lower = include_path.lower()
        for token in UI_FORBIDDEN_INCLUDES:
            if lower.startswith(token) or token in lower:
                return True
        return False

    ui_paths = [
        os.path.join(repo_root, "game", "ui"),
        os.path.join(repo_root, "client"),
    ]
    for root in ui_paths:
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_include_lines(path):
                match = INCLUDE_RE.match(code)
                if not match:
                    continue
                include_path = normalize_include(match.group(1))
                if include_predicate(include_path):
                    check.add_violation(rel, idx, include_path)
            for idx, code in iter_code_lines(path):
                if UI_FORBIDDEN_CALL_RE.search(code):
                    check.add_violation(rel, idx, "authoritative sim/world call")
    return check


def check_det_float_003(repo_root):
    check = Check(
        "DET-FLOAT-003",
        "floating point or math intrinsics in authoritative zones (forbidden)",
        "Replace with deterministic fixed-point or approved math APIs.",
    )

    def is_forbidden_math_header(include_path):
        lower = include_path.lower()
        for header in FORBIDDEN_MATH_HEADERS:
            if lower == header or lower.endswith("/" + header):
                return True
        return False

    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_include_lines(path):
                match = INCLUDE_RE.match(code)
                if not match:
                    continue
                include_path = normalize_include(match.group(1))
                if is_forbidden_math_header(include_path):
                    check.add_violation(rel, idx, "math header include")
            for idx, code in iter_code_lines(path):
                if FLOAT_TOKENS_RE.search(code):
                    check.add_violation(rel, idx, "floating point token")
                if MATH_CALL_RE.search(code):
                    check.add_violation(rel, idx, "math intrinsic call")
    return check


def check_det_time_001(repo_root):
    check = Check(
        "DET-TIME-001",
        "OS time usage in authoritative zones (forbidden)",
        "Use ACT time and deterministic scheduling only.",
    )

    def is_forbidden_time_header(include_path):
        lower = include_path.lower()
        for header in FORBIDDEN_TIME_HEADERS:
            if lower == header or lower.endswith("/" + header):
                return True
        return False

    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_include_lines(path):
                match = INCLUDE_RE.match(code)
                if not match:
                    continue
                include_path = normalize_include(match.group(1))
                if is_forbidden_time_header(include_path):
                    check.add_violation(rel, idx, "time header include")
            for idx, code in iter_code_lines(path):
                if TIME_CALL_RE.search(code):
                    check.add_violation(rel, idx, "time API call")
                if TIME_STD_RE.search(code):
                    check.add_violation(rel, idx, "std::chrono usage")
    return check


def check_det_rng_002(repo_root):
    check = Check(
        "DET-RNG-002",
        "non-deterministic RNG usage in authoritative zones (forbidden)",
        "Use domino/core/rng.h only; pass RNG state explicitly.",
    )

    def is_forbidden_rng_header(include_path):
        lower = include_path.lower()
        for header in FORBIDDEN_RNG_HEADERS:
            if lower == header or lower.endswith("/" + header):
                return True
        return False

    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_include_lines(path):
                match = INCLUDE_RE.match(code)
                if not match:
                    continue
                include_path = normalize_include(match.group(1))
                if is_forbidden_rng_header(include_path):
                    check.add_violation(rel, idx, "random header include")
            for idx, code in iter_code_lines(path):
                if RNG_CALL_RE.search(code):
                    check.add_violation(rel, idx, "non-deterministic RNG call")
                if RNG_STD_RE.search(code):
                    check.add_violation(rel, idx, "std::random usage")
    return check


def check_det_ord_004(repo_root):
    check = Check(
        "DET-ORD-004",
        "unordered container usage in authoritative zones (forbidden)",
        "Use ordered containers or normalize iteration before use.",
    )

    def is_forbidden_unordered_header(include_path):
        lower = include_path.lower()
        return lower.endswith("unordered_map") or lower.endswith("unordered_set") or lower.endswith("unordered_multimap") or lower.endswith("unordered_multiset")

    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_include_lines(path):
                match = INCLUDE_RE.match(code)
                if not match:
                    continue
                include_path = normalize_include(match.group(1))
                if is_forbidden_unordered_header(include_path):
                    check.add_violation(rel, idx, "unordered header include")
            for idx, code in iter_code_lines(path):
                if UNORDERED_RE.search(code):
                    check.add_violation(rel, idx, "unordered container usage")
    return check


def check_perf_global_002(repo_root):
    check = Check(
        "PERF-GLOBAL-002",
        "global iteration patterns in authoritative zones (forbidden)",
        "Replace global scans with event-driven scheduling and bounded interest sets.",
    )
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = repo_rel(repo_root, path)
            for idx, code in iter_code_lines(path):
                for pattern in GLOBAL_ITER_PATTERNS:
                    if pattern.search(code):
                        check.add_violation(rel, idx, pattern.pattern)
    return check


def check_build_global_001(repo_root):
    check = Check(
        "BUILD-GLOBAL-001",
        "global include_directories/link_directories usage (forbidden)",
        "Replace with target_include_directories/target_link_directories on specific targets.",
    )
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel = repo_rel(repo_root, dirpath)
        parts = rel.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename != "CMakeLists.txt":
                continue
            path = os.path.join(dirpath, filename)
            rel_path = repo_rel(repo_root, path)
            try:
                with open(path, "r", errors="ignore") as handle:
                    for idx, line in enumerate(handle, start=1):
                        stripped = line.lstrip()
                        if stripped.startswith("#"):
                            continue
                        if re.search(r"\binclude_directories\s*\(", line):
                            check.add_violation(rel_path, idx, "include_directories()")
                        if re.search(r"\blink_directories\s*\(", line):
                            check.add_violation(rel_path, idx, "link_directories()")
            except IOError:
                continue
    return check


def run_checks(repo_root, strict=False):
    checks = [
        check_arch_inc_001(repo_root),
        check_arch_inc_002(repo_root),
        check_arch_dep_001(repo_root),
        check_arch_dep_002(repo_root),
        check_arch_render_001(repo_root),
        check_arch_top_001(repo_root),
        check_ui_bypass_001(repo_root),
        check_det_float_003(repo_root),
        check_det_time_001(repo_root),
        check_det_rng_002(repo_root),
        check_det_ord_004(repo_root),
        check_perf_global_002(repo_root),
        check_build_global_001(repo_root),
    ]
    failed = False
    for check in checks:
        if not check.violations:
            continue
        header = "{0}: {1}".format(check.check_id, check.description)
        if check.severity == "warn" and not strict:
            header = "WARN " + header
        print(header)
        for path, line, detail in sorted(check.violations):
            print("  {0}:{1}: {2}".format(path, line, detail))
        print("Fix: {0}".format(check.remediation))
        if check.has_failures(strict=strict):
            failed = True
    if not failed:
        print("Architecture checks OK.")
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(description="Architecture boundary checks")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root
    if not repo_root:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    return run_checks(repo_root, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
