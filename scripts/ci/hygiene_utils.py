#!/usr/bin/env python3
import os

DEFAULT_ROOTS = [
    "engine",
    "game",
    "tools",
    "client",
    "server",
    "launcher",
    "setup",
    "libs",
    "schema",
    "docs",
    "scripts",
    "ci",
]

DEFAULT_EXCLUDES = [
    "build",
    "out",
    "dist",
    ".git",
    ".vs",
    ".vscode",
    "legacy",
    "external",
    "third_party",
    "generated",
    "autogen",
]

CODE_EXTS = [
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".hh",
    ".hxx",
    ".ipp",
    ".inl",
]

TEXT_EXTS = CODE_EXTS + [
    ".md",
    ".py",
    ".cmake",
    ".txt",
    ".bat",
    ".sh",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
]


def normalize_path(path):
    return os.path.normpath(path).replace("\\", "/")


def normalize_newlines(text):
    if "\r" in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def expand_list(values, defaults):
    items = []
    if values:
        for value in values:
            if value is None:
                continue
            for part in str(value).split(";"):
                part = part.strip()
                if part:
                    items.append(part)
    if not items:
        items = list(defaults)
    return items


def is_excluded(path_norm, exclude_norms):
    for frag in exclude_norms:
        if frag and frag in path_norm:
            return True
    return False


def iter_files(roots, excludes, exts):
    exclude_norms = [normalize_path(item).lower() for item in excludes]
    exts_set = {ext.lower() for ext in exts}
    files = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        root_norm = normalize_path(root).lower()
        if is_excluded(root_norm, exclude_norms):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(
                [d for d in dirnames if not is_excluded(normalize_path(os.path.join(dirpath, d)).lower(), exclude_norms)]
            )
            for filename in sorted(filenames):
                ext = os.path.splitext(filename)[1].lower()
                if ext not in exts_set:
                    continue
                full_path = os.path.join(dirpath, filename)
                path_norm = normalize_path(full_path).lower()
                if is_excluded(path_norm, exclude_norms):
                    continue
                if os.path.isfile(full_path):
                    files.append(full_path)
    return sorted(files, key=lambda p: normalize_path(p).lower())


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return normalize_newlines(handle.read())
    except OSError:
        return None


def strip_c_comments_and_strings(text):
    out = []
    i = 0
    in_string = False
    in_char = False
    in_block = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_string:
            if ch == "\\" and i + 1 < len(text):
                out.append(" ")
                out.append(" ")
                i += 2
                continue
            if ch == '"':
                out.append(" ")
                in_string = False
                i += 1
                continue
            out.append(" " if ch != "\n" else "\n")
            i += 1
            continue
        if in_char:
            if ch == "\\" and i + 1 < len(text):
                out.append(" ")
                out.append(" ")
                i += 2
                continue
            if ch == "'":
                out.append(" ")
                in_char = False
                i += 1
                continue
            out.append(" " if ch != "\n" else "\n")
            i += 1
            continue
        if in_block:
            if ch == "*" and nxt == "/":
                out.append(" ")
                out.append(" ")
                in_block = False
                i += 2
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
        if ch == "/" and nxt == "/":
            out.append(" ")
            out.append(" ")
            i += 2
            while i < len(text) and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == "/" and nxt == "*":
            out.append(" ")
            out.append(" ")
            in_block = True
            i += 2
            continue
        if ch == '"':
            out.append(" ")
            in_string = True
            i += 1
            continue
        if ch == "'":
            out.append(" ")
            in_char = True
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)
