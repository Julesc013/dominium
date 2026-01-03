#!/usr/bin/env python3
import argparse
import os
import re
import sys

WORD_RE = re.compile(r"\b\w+\b")

DEFAULT_ROOTS = ["src", "include"]
DEFAULT_EXCLUDES = ["third_party", "external", "build", "out", ".git", "generated"]
DEFAULT_EXTS = [".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hh", ".hxx", ".ipp", ".inl"]

DEFAULT_MIN_LINE = 0.20
DEFAULT_MAX_LINE = 0.40
DEFAULT_MIN_WORD = 0.15
DEFAULT_MAX_WORD = 0.30
DEFAULT_MIN_CHAR = 0.10
DEFAULT_MAX_CHAR = 0.25


def normalize_newlines(text):
    if "\r" in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def normalize_path(path):
    return os.path.normpath(path).replace("\\", "/").lower()


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


def strip_string_literals(text):
    out = []
    i = 0
    in_string = False
    in_char = False
    while i < len(text):
        ch = text[i]
        if in_string or in_char:
            quote = '"' if in_string else "'"
            if ch == "\n":
                out.append("\n")
                in_string = False
                in_char = False
                i += 1
                continue
            if ch == "\\":
                if i + 1 < len(text) and text[i + 1] == "\n":
                    out.append(" ")
                    out.append("\n")
                    i += 2
                else:
                    out.append(" ")
                    if i + 1 < len(text):
                        out.append(" ")
                        i += 2
                    else:
                        i += 1
                continue
            if ch == quote:
                out.append(" ")
                in_string = False
                in_char = False
                i += 1
                continue
            out.append(" ")
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue
        if ch == "'":
            in_char = True
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def extract_comment_data(text, non_blank_line_flags):
    comment_chars = 0
    comment_text = []
    comment_line_flags = [False] * len(non_blank_line_flags)
    i = 0
    line_idx = 0
    in_block = False
    while i < len(text):
        ch = text[i]
        if ch == "\n":
            if in_block:
                comment_text.append("\n")
            line_idx += 1
            i += 1
            continue
        if in_block:
            if ch == "*" and i + 1 < len(text) and text[i + 1] == "/":
                in_block = False
                i += 2
                continue
            comment_chars += 1
            comment_text.append(ch)
            if line_idx < len(comment_line_flags):
                comment_line_flags[line_idx] = True
            i += 1
            continue
        if ch == "/" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "/":
                i += 2
                while i < len(text) and text[i] != "\n":
                    comment_chars += 1
                    comment_text.append(text[i])
                    if line_idx < len(comment_line_flags):
                        comment_line_flags[line_idx] = True
                    i += 1
                continue
            if nxt == "*":
                in_block = True
                i += 2
                continue
        i += 1
    comment_words = len(WORD_RE.findall("".join(comment_text)))
    max_lines = min(len(comment_line_flags), len(non_blank_line_flags))
    comment_lines = 0
    for idx in range(max_lines):
        if comment_line_flags[idx] and non_blank_line_flags[idx]:
            comment_lines += 1
    return comment_lines, comment_words, comment_chars


def analyze_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            raw_text = handle.read()
    except OSError as exc:
        print(f"DOC-RATIO WARN unable to read {path}: {exc}", file=sys.stderr)
        return None

    raw_text = normalize_newlines(raw_text)
    original_lines = raw_text.split("\n")
    non_blank_line_flags = [bool(line.strip()) for line in original_lines]
    total_nonblank_lines = sum(1 for flag in non_blank_line_flags if flag)

    stripped_text = strip_string_literals(raw_text)
    stripped_lines = stripped_text.split("\n")
    total_words = 0
    total_chars = 0
    max_lines = min(len(stripped_lines), len(non_blank_line_flags))
    for idx in range(max_lines):
        if not non_blank_line_flags[idx]:
            continue
        line = stripped_lines[idx]
        total_chars += len(line)
        total_words += len(WORD_RE.findall(line))

    comment_lines, comment_words, comment_chars = extract_comment_data(
        stripped_text, non_blank_line_flags
    )

    return {
        "total_lines": total_nonblank_lines,
        "comment_lines": comment_lines,
        "total_words": total_words,
        "comment_words": comment_words,
        "total_chars": total_chars,
        "comment_chars": comment_chars,
    }


def format_ratio(name, ratio):
    return f"{name} {ratio:.4f} ({ratio * 100.0:.2f}%)"


def main():
    parser = argparse.ArgumentParser(description="Check documentation density ratios.")
    parser.add_argument("--roots", action="append", help="Root path to scan.")
    parser.add_argument("--exclude", action="append", help="Exclude path fragment.")
    parser.add_argument("--ext", action="append", help="File extension to include.")
    parser.add_argument("--min-line", type=float, default=DEFAULT_MIN_LINE)
    parser.add_argument("--max-line", type=float, default=DEFAULT_MAX_LINE)
    parser.add_argument("--min-word", type=float, default=DEFAULT_MIN_WORD)
    parser.add_argument("--max-word", type=float, default=DEFAULT_MAX_WORD)
    parser.add_argument("--min-char", type=float, default=DEFAULT_MIN_CHAR)
    parser.add_argument("--max-char", type=float, default=DEFAULT_MAX_CHAR)
    parser.add_argument("--mode", type=str.lower, choices=["warn", "fail"], default="warn")
    parser.add_argument("--format", type=str.lower, default="text")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.format != "text":
        print(f"DOC-RATIO FAIL unsupported format: {args.format}", file=sys.stderr)
        return 2

    roots = expand_list(args.roots, DEFAULT_ROOTS)
    excludes = expand_list(args.exclude, DEFAULT_EXCLUDES)
    exts = expand_list(args.ext, DEFAULT_EXTS)
    exclude_norms = [normalize_path(item) for item in excludes]
    exts_set = {ext.lower() for ext in exts}

    files = []
    excluded_paths = 0
    missing_roots = 0
    for root in roots:
        if not os.path.isdir(root):
            missing_roots += 1
            continue
        root_norm = normalize_path(root)
        if is_excluded(root_norm, exclude_norms):
            excluded_paths += 1
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            pruned = []
            for dirname in list(dirnames):
                dir_norm = normalize_path(os.path.join(dirpath, dirname))
                if is_excluded(dir_norm, exclude_norms):
                    pruned.append(dirname)
            for dirname in pruned:
                dirnames.remove(dirname)
                excluded_paths += 1
            dirnames.sort()
            filenames.sort()
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in exts_set:
                    continue
                full_path = os.path.join(dirpath, filename)
                path_norm = normalize_path(full_path)
                if is_excluded(path_norm, exclude_norms):
                    excluded_paths += 1
                    continue
                if not os.path.isfile(full_path):
                    continue
                files.append(full_path)

    scanned_files = 0
    skipped_line_files = 0
    skipped_word_files = 0
    skipped_char_files = 0
    line_total = 0
    line_comment = 0
    word_total = 0
    word_comment = 0
    char_total = 0
    char_comment = 0

    base_dir = os.getcwd()
    for path in files:
        metrics = analyze_file(path)
        if metrics is None:
            continue
        scanned_files += 1
        total_lines = metrics["total_lines"]
        comment_lines = metrics["comment_lines"]
        total_words = metrics["total_words"]
        comment_words = metrics["comment_words"]
        total_chars = metrics["total_chars"]
        comment_chars = metrics["comment_chars"]

        if not args.quiet:
            rel_path = os.path.relpath(path, start=base_dir).replace("\\", "/")
            if total_lines == 0:
                print(f"FILE {rel_path} skipped (no non-blank lines)")
            else:
                print(
                    "FILE {path} lines={lines} comment_lines={clines} "
                    "words={words} comment_words={cwords} chars={chars} comment_chars={cchars}".format(
                        path=rel_path,
                        lines=total_lines,
                        clines=comment_lines,
                        words=total_words,
                        cwords=comment_words,
                        chars=total_chars,
                        cchars=comment_chars,
                    )
                )

        if total_lines == 0:
            skipped_line_files += 1
        else:
            line_total += total_lines
            line_comment += comment_lines

        if total_words == 0:
            skipped_word_files += 1
        else:
            word_total += total_words
            word_comment += comment_words

        if total_chars == 0:
            skipped_char_files += 1
        else:
            char_total += total_chars
            char_comment += comment_chars

    line_ratio = (line_comment / line_total) if line_total else 0.0
    word_ratio = (word_comment / word_total) if word_total else 0.0
    char_ratio = (char_comment / char_total) if char_total else 0.0

    print("DOC-RATIO SUMMARY")
    print(f"Roots: {len(roots)}")
    if missing_roots:
        print(f"Missing roots: {missing_roots}")
    print(f"Scanned files: {scanned_files}")
    print(f"Excluded paths: {excluded_paths}")
    print(f"Skipped files (no non-blank lines): {skipped_line_files}")
    print(f"Skipped word files (no words): {skipped_word_files}")
    print(f"Skipped char files (no chars): {skipped_char_files}")
    print(
        "Totals: lines {lines} (comments {clines}), words {words} (comments {cwords}), "
        "chars {chars} (comments {cchars})".format(
            lines=line_total,
            clines=line_comment,
            words=word_total,
            cwords=word_comment,
            chars=char_total,
            cchars=char_comment,
        )
    )
    print(
        "Ratios: {line}, {word}, {char}".format(
            line=format_ratio("line", line_ratio),
            word=format_ratio("word", word_ratio),
            char=format_ratio("char", char_ratio),
        )
    )
    print(
        "Thresholds: line {lmin:.4f}-{lmax:.4f}, word {wmin:.4f}-{wmax:.4f}, char {cmin:.4f}-{cmax:.4f}".format(
            lmin=args.min_line,
            lmax=args.max_line,
            wmin=args.min_word,
            wmax=args.max_word,
            cmin=args.min_char,
            cmax=args.max_char,
        )
    )

    violations = []
    if line_ratio < args.min_line or line_ratio > args.max_line:
        violations.append(("line", line_ratio, args.min_line, args.max_line))
    if word_ratio < args.min_word or word_ratio > args.max_word:
        violations.append(("word", word_ratio, args.min_word, args.max_word))
    if char_ratio < args.min_char or char_ratio > args.max_char:
        violations.append(("char", char_ratio, args.min_char, args.max_char))

    if violations:
        prefix = "DOC-RATIO FAIL" if args.mode == "fail" else "DOC-RATIO WARN"
        for name, ratio, min_val, max_val in violations:
            print(
                "{prefix} {name} ratio={ratio:.4f} ({pct:.2f}%) min={minv:.4f} max={maxv:.4f}".format(
                    prefix=prefix,
                    name=name,
                    ratio=ratio,
                    pct=ratio * 100.0,
                    minv=min_val,
                    maxv=max_val,
                )
            )

    if args.mode == "fail" and violations:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
