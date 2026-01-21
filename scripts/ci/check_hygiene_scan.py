#!/usr/bin/env python3
import argparse
import hashlib
import re
import sys

from hygiene_utils import (
    CODE_EXTS,
    TEXT_EXTS,
    DEFAULT_EXCLUDES,
    DEFAULT_ROOTS,
    expand_list,
    iter_files,
    read_text,
    normalize_path,
    strip_c_comments_and_strings,
)

QUEUE_PATH = "docs/ci/HYGIENE_QUEUE.md"

ENUM_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_]*(CUSTOM|OTHER|UNKNOWN)[A-Za-z0-9_]*\b")
NUM_RE = re.compile(r"(?<![A-Za-z0-9_])(-?(?:0x[0-9A-Fa-f]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))(?:[uUlLfF]*)")
TODO_RE = re.compile(r"TODO_(BLOCKER|FUTURE|DOC)\([A-Za-z0-9_.-]+\)")

MODE_FLAG_RE = re.compile(r"\b(isAdmin|isCheat|serverType|godMode|debugMode|adminMode)\b")
STR_CMP_RE = re.compile(r"\b(strcmp|strncmp|strcasecmp|stricmp|strcmpi)\s*\(")

SUSPECT_TOKENS = [
    "type",
    "kind",
    "class",
    "category",
    "mode",
    "target",
    "capability",
    "resource",
    "material",
    "damage",
    "biome",
    "tech",
    "module",
    "item",
    "_id",
]

ALLOW_TOKENS = [
    "execution_phase",
    "determinism",
    "det_class",
    "authority_layer",
    "existence_state",
    "law_result",
]

PUBLIC_HEADER_ROOTS = [
    "engine/include",
    "game/include",
    "libs/contracts/include",
]

FUNC_DECL_RE = re.compile(r"^\s*[A-Za-z_][\w\s\*]*\b[A-Za-z_]\w*\s*\([^;]*\)\s*;")
LIST_RE = re.compile(r"\bconst\s+char\s*\*\s*\w+\s*\[.*\]\s*=")


def hygiene_id(path, line, token, kind):
    base = f"{normalize_path(path).lower()}:{line}:{token}:{kind}"
    return "HYG-" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:8]


def parse_existing_queue(path):
    text = read_text(path)
    if text is None:
        return {}
    rows = {}
    for line in text.split("\n"):
        if not line.startswith("| HYG-"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 9:
            continue
        row = {
            "id": parts[0],
            "status": parts[1],
            "category": parts[2],
            "location": parts[3],
            "description": parts[4],
            "fix": parts[5],
            "complexity": parts[6],
            "deps": parts[7],
            "tests": parts[8],
        }
        rows[row["id"]] = row
    return rows


def line_allows_numbers(line):
    if "MAGIC_NUMBER_OK" in line:
        return True
    if "MAGIC_NUMBER_FILE_OK" in line:
        return True
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return True
    if re.search(r"\b(const|constexpr|enum)\b", line):
        return True
    if re.search(r"^\s*#\s*define\b", line):
        return True
    return False


def is_allowed_literal(raw):
    raw = raw.lower()
    if raw in ("0", "1", "-1", "0u", "1u", "-1u", "0ul", "1ul", "-1ul"):
        return True
    if raw.startswith("0x"):
        return False
    if "." in raw or "e" in raw:
        return False
    return False


def scan_forbidden_enums(path, text, findings):
    stripped = strip_c_comments_and_strings(text)
    in_enum = False
    pending_enum = False
    brace_depth = 0
    for idx, line in enumerate(stripped.split("\n"), start=1):
        if "HYGIENE_ALLOW_UNKNOWN_ENUM" in line or "PARSER_ONLY_UNKNOWN" in line:
            continue
        if not in_enum:
            if pending_enum:
                if "{" in line:
                    in_enum = True
                    pending_enum = False
                    brace_depth += line.count("{") - line.count("}")
            elif re.search(r"\benum\b", line):
                if "{" in line:
                    in_enum = True
                    brace_depth += line.count("{") - line.count("}")
                else:
                    pending_enum = True
            continue

        for match in ENUM_TOKEN_RE.finditer(line):
            token = match.group(0)
            findings.append({
                "id": hygiene_id(path, idx, token, "FORBIDDEN_ENUM"),
                "status": "OPEN",
                "category": "A",
                "location": f"{normalize_path(path)}:{idx}",
                "description": f"Enum value uses forbidden token '{token}'.",
                "fix": "Replace with registry id or remove CUSTOM/OTHER/UNKNOWN.",
                "complexity": "S",
                "deps": "REGISTRY_PATTERN",
                "tests": "contract enum hygiene",
            })

        brace_depth += line.count("{") - line.count("}")
        if brace_depth <= 0:
            in_enum = False
            pending_enum = False
            brace_depth = 0


def scan_magic_numbers(path, text, findings):
    if "MAGIC_NUMBER_FILE_OK" in text:
        return
    clean = strip_c_comments_and_strings(text)
    for idx, line in enumerate(clean.split("\n"), start=1):
        if not line.strip():
            continue
        if line_allows_numbers(line):
            continue
        for match in NUM_RE.finditer(line):
            literal = match.group(1)
            if is_allowed_literal(literal):
                continue
            findings.append({
                "id": hygiene_id(path, idx, literal, "MAGIC_NUMBER"),
                "status": "OPEN",
                "category": "C",
                "location": f"{normalize_path(path)}:{idx}",
                "description": f"Magic number literal '{literal}'.",
                "fix": "Replace with named constant or data-driven parameter.",
                "complexity": "S",
                "deps": "CODEHYGIENE_RULES",
                "tests": "unit/regression coverage",
            })


def scan_mode_flags(path, text, findings):
    for idx, line in enumerate(text.split("\n"), start=1):
        match = MODE_FLAG_RE.search(line)
        if match:
            token = match.group(1)
            findings.append({
                "id": hygiene_id(path, idx, token, "MODE_FLAG"),
                "status": "OPEN",
                "category": "B",
                "location": f"{normalize_path(path)}:{idx}",
                "description": f"Hard-coded mode flag '{token}'.",
                "fix": "Replace with law/capability gating or registry-based policy.",
                "complexity": "M",
                "deps": "LAW_TARGETS registry",
                "tests": "contract admission tests",
            })


def scan_string_comparisons(path, text, findings):
    for idx, line in enumerate(text.split("\n"), start=1):
        if STR_CMP_RE.search(line):
            findings.append({
                "id": hygiene_id(path, idx, "strcmp", "STRING_COMPARE"),
                "status": "OPEN",
                "category": "B",
                "location": f"{normalize_path(path)}:{idx}",
                "description": "String comparison in runtime path.",
                "fix": "Resolve string -> id at load time; compare ids.",
                "complexity": "M",
                "deps": "REGISTRY_PATTERN",
                "tests": "determinism + unit tests",
            })


def find_switches(text):
    switches = []
    i = 0
    while i < len(text):
        m = re.search(r"\bswitch\s*\(", text[i:])
        if not m:
            break
        start = i + m.start()
        paren_start = i + m.end() - 1
        depth = 0
        j = paren_start
        while j < len(text):
            ch = text[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    expr = text[paren_start + 1 : j]
                    line = text[:start].count("\n") + 1
                    switches.append((line, expr))
                    i = j + 1
                    break
            j += 1
        else:
            break
    return switches


def is_suspect_switch(expr):
    expr_l = expr.lower()
    for allow in ALLOW_TOKENS:
        if allow in expr_l:
            return False
    for token in SUSPECT_TOKENS:
        if token in expr_l:
            return True
    return False


def scan_switch_taxonomy(path, text, findings):
    clean = strip_c_comments_and_strings(text)
    lines = text.split("\n")
    for line, expr in find_switches(clean):
        marker_ok = False
        for idx in range(max(0, line - 2), min(len(lines), line + 1)):
            if "HYGIENE_TAXONOMY_SWITCH_OK" in lines[idx]:
                marker_ok = True
                break
        if marker_ok:
            continue
        if is_suspect_switch(expr):
            findings.append({
                "id": hygiene_id(path, line, "switch", "SWITCH_TAXONOMY"),
                "status": "OPEN",
                "category": "B",
                "location": f"{normalize_path(path)}:{line}",
                "description": "Switch on taxonomy id/type.",
                "fix": "Replace with registry dispatch table.",
                "complexity": "M",
                "deps": "REGISTRY_PATTERN",
                "tests": "contract switch hygiene",
            })

def scan_todos(path, text, findings):
    for idx, line in enumerate(text.split("\n"), start=1):
        if "TODO" not in line:
            continue
        if TODO_RE.search(line):
            continue
        findings.append({
            "id": hygiene_id(path, idx, "TODO", "RAW_TODO"),
            "status": "OPEN",
            "category": "D",
            "location": f"{normalize_path(path)}:{idx}",
            "description": "Unscoped todo comment without required prefix.",
            "fix": "Convert to standardized TODO_* and update docs.",
            "complexity": "S",
            "deps": "KNOWN_BLOCKERS",
            "tests": "todo policy scan",
        })


def scan_hardcoded_lists(path, text, findings):
    for idx, line in enumerate(text.split("\n"), start=1):
        if "HYGIENE_TAXONOMY_SWITCH_OK" in line:
            continue
        if not LIST_RE.search(line):
            continue
        if "{" in line and line.count("\"") >= 2:
            findings.append({
                "id": hygiene_id(path, idx, "list", "HARDCODED_LIST"),
                "status": "OPEN",
                "category": "B",
                "location": f"{normalize_path(path)}:{idx}",
                "description": "Hard-coded list of string types.",
                "fix": "Move to registry data file and load at init.",
                "complexity": "M",
                "deps": "REGISTRY_PATTERN",
                "tests": "registry loader tests",
            })


def has_header_block(text):
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        return stripped.startswith("/*") or stripped.startswith("//")
    return False


def is_public_header(path):
    path_norm = normalize_path(path).lower()
    for root in PUBLIC_HEADER_ROOTS:
        if path_norm.startswith(normalize_path(root).lower()):
            return True
    return False


def scan_doc_blocks(path, text, findings):
    if not has_header_block(text):
        findings.append({
            "id": hygiene_id(path, 1, "HEADER", "MISSING_HEADER"),
            "status": "OPEN",
            "category": "D",
            "location": f"{normalize_path(path)}:1",
            "description": "Missing file header doc block.",
            "fix": "Add file header with responsibility/invariants.",
            "complexity": "S",
            "deps": "CODEHYGIENE_RULES",
            "tests": "comment density scan",
        })

    if not is_public_header(path):
        return
    lines = text.split("\n")
    for idx, line in enumerate(lines, start=1):
        if not FUNC_DECL_RE.match(line):
            continue
        prior = "\n".join(lines[max(0, idx - 3): idx])
        if "Purpose:" in prior or "DOC:" in prior or "INVARIANT:" in prior:
            continue
        findings.append({
            "id": hygiene_id(path, idx, "FUNC_DOC", "MISSING_FUNC_DOC"),
            "status": "OPEN",
            "category": "D",
            "location": f"{normalize_path(path)}:{idx}",
            "description": "Missing function doc block in public header.",
            "fix": "Add Purpose/DOC/INVARIANT doc block.",
            "complexity": "S",
            "deps": "INVARIANT_REGISTRY",
            "tests": "comment density scan",
        })


def render_queue(entries):
    header = [
        "# CODEHYGIENE Queue",
        "",
        "This file is generated by scripts/ci/check_hygiene_scan.py.",
        "Do not edit by hand; use the scan tool to update.",
        "",
        "## Entries",
        "",
        "| HYGIENE-ID | Status | Category | Location | Description | Proposed Fix | Complexity | Dependencies | Tests |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines = header[:]
    for entry in entries:
        row = [
            entry["id"],
            entry["status"],
            entry["category"],
            entry["location"],
            entry["description"],
            entry["fix"],
            entry["complexity"],
            entry["deps"],
            entry["tests"],
        ]
        safe = [cell.replace("|", ";") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    lines.append("")
    return "\n".join(lines)


def write_queue(path, entries):
    content = render_queue(entries)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description="Scan repo and update hygiene queue.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--queue", default=QUEUE_PATH)
    parser.add_argument("--mode", choices=["write", "check"], default="write")
    args = parser.parse_args()

    roots = expand_list(args.roots, DEFAULT_ROOTS)
    excludes = expand_list(args.exclude, DEFAULT_EXCLUDES)

    existing = parse_existing_queue(args.queue)
    findings = []

    code_files = iter_files(roots, excludes, CODE_EXTS)
    text_files = iter_files(roots, excludes, TEXT_EXTS)

    for path in code_files:
        text = read_text(path)
        if text is None:
            continue
        scan_forbidden_enums(path, text, findings)
        scan_magic_numbers(path, text, findings)
        scan_mode_flags(path, text, findings)
        scan_string_comparisons(path, text, findings)
        scan_switch_taxonomy(path, text, findings)
        scan_hardcoded_lists(path, text, findings)
        scan_doc_blocks(path, text, findings)

    for path in text_files:
        text = read_text(path)
        if text is None:
            continue
        scan_todos(path, text, findings)

    merged = {}
    for entry in findings:
        existing_row = existing.get(entry["id"])
        if existing_row:
            entry["status"] = existing_row["status"]
        merged[entry["id"]] = entry

    for entry_id, row in existing.items():
        if entry_id not in merged:
            merged[entry_id] = row

    ordered = [merged[key] for key in sorted(merged.keys())]

    if args.mode == "write":
        write_queue(args.queue, ordered)
        return 0

    # check mode (no file mutation)
    original = read_text(args.queue) or ""
    updated = render_queue(ordered)
    if original != updated:
        sys.stderr.write("HYGIENE-SCAN FAIL: queue out of date. Run with --mode write.\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
