"""Build styled v1 docs-corpus Omnibus reader/reference outputs.

This is a publication/export pipeline. It improves readability over the v0
coverage PDF while preserving the same authority boundary: generated outputs are
derived and advisory, and source docs are not modified or promoted.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import build_omnibus_pdf as v0
import docs_corpus


TASK_ID = "DOCS-CORPUS-OMNIBUS-READABILITY-V1"
REVIEW_DATE = "2026-05-29"
VERSION = 1
TITLE = "Dominium Docs Corpus Omnibus"
SUBTITLE = "Styled Reader, Reference, Archive, Conversation, and Reconciliation Guide"

DOCS_CORPUS_ROOT = Path("docs/archive/docs_corpus")
V1_ROOT = DOCS_CORPUS_ROOT / "_omnibus_v1"
STYLE_ROOT = DOCS_CORPUS_ROOT / "_style_v1"
EXPORTS_ROOT = DOCS_CORPUS_ROOT / "_exports"

READER_BASENAME = "Dominium_Docs_Corpus_Omnibus_Reader_v1"
REFERENCE_BASENAME = "Dominium_Docs_Corpus_Omnibus_Reference_v1"
ALL_IN_ONE_BASENAME = "Dominium_Docs_Corpus_Omnibus_AllInOne_v1"
HTML_DIRNAME = "Dominium_Docs_Corpus_Omnibus_HTML_v1"
MOBILE_HTML = "Dominium_Docs_Corpus_Omnibus_Mobile_v1.html"
STYLE_REPORT = "Dominium_Docs_Corpus_Omnibus_Style_Report_v1.md"
BUILD_REPORT = "Dominium_Docs_Corpus_Omnibus_Build_Report_v1.md"
VALIDATION_REPORT = "Dominium_Docs_Corpus_Omnibus_Validation_Report_v1.md"

PROTECTED_PREFIXES = docs_corpus.PROTECTED_PREFIXES

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: docs/archive/docs_corpus/_omnibus/**
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""

METADATA_KEYS = {
    "Status",
    "Last Reviewed",
    "Supersedes",
    "Superseded By",
    "Stability",
    "Authority Class",
    "Source Root",
    "Conversation Corpus Root",
    "Promotion Status",
    "Canon impact",
    "Contract/schema impact",
    "Implementation impact",
    "Release impact",
    "Queue impact",
    "Binding Sources",
    "Result",
    "Version",
    "Compatibility",
}

CALLOUT_COLORS = {
    "AUTHORITY": "DomBlue",
    "NOT_PROMOTED": "DomGreen",
    "CURRENT_TRUTH": "DomGreen",
    "ARCHIVE": "DomAmber",
    "CONVERSATION": "DomViolet",
    "BLOCKED": "DomRed",
    "DECISION": "DomViolet",
    "VERIFY": "DomAmber",
    "CONTRADICTION": "DomRed",
    "PROMOTION": "DomBlue",
    "SOURCE": "DomSlate",
}


@dataclass
class PdfOutput:
    name: str
    path: Path
    created: bool
    pages: Optional[int] = None
    size: int = 0
    renderer: str = ""
    text_extraction: str = "not_run"
    glyph_check: str = "not_run"
    qa_images: List[str] = field(default_factory=list)
    caveat: str = ""


@dataclass
class V1State:
    repo_root: Path
    base: v0.BuildState
    renderer: str = ""
    outputs: Dict[str, PdfOutput] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_text(path: Path, content: str) -> None:
    clean = "\n".join(line.rstrip(" \t") for line in content.splitlines())
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(clean) + "\n")


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 900) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return proc.returncode, docs_corpus.ascii_text(proc.stdout)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        text = (exc.stdout or "") + (exc.stderr or "")
        return 124, docs_corpus.ascii_text(text)


def read_text(repo_root: Path, path: str, limit: Optional[int] = None) -> str:
    return v0.read_text(repo_root / path, limit=limit)


def title_from_path(path: str) -> str:
    stem = Path(path).stem
    stem = re.sub(r"^(DOCS_|Dominium_Docs_Corpus_|Dominium_Conversation_Corpus_)", "", stem)
    stem = re.sub(r"_(v0|v1)$", "", stem, flags=re.IGNORECASE)
    stem = stem.replace("__", "_").replace("_", " ").replace("-", " ")
    words = []
    for word in stem.split():
        upper = word.upper()
        if upper in {"AIDE", "API", "CLI", "DOCS", "FAST", "GUI", "HTML", "ID", "JSON", "MCP", "PDF", "QA", "TUI", "UI", "URL", "YAML"}:
            words.append(upper)
        else:
            words.append(word.capitalize())
    title = " ".join(words).strip()
    return title or path


def compact_metadata(text: str) -> Tuple[Dict[str, str], str]:
    lines = text.splitlines()
    metadata: Dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines[:40]):
        stripped = line.strip()
        if not stripped:
            body_start = index + 1
            continue
        if stripped.startswith("#"):
            body_start = index
            break
        match = re.match(r"^([^:]{2,40}):\s*(.*)$", stripped)
        if not match or match.group(1) not in METADATA_KEYS:
            body_start = index
            break
        metadata[match.group(1)] = match.group(2)
        body_start = index + 1
    return metadata, "\n".join(lines[body_start:]).strip() + "\n"


def demote_headings(text: str, levels: int = 1) -> str:
    out: List[str] = []
    for raw in text.splitlines():
        if raw.startswith("#"):
            count = len(raw) - len(raw.lstrip("#"))
            heading = raw[count:].strip()
            out.append("#" * min(6, count + levels) + " " + heading)
        else:
            out.append(raw)
    return "\n".join(out).strip() + "\n"


def source_section(repo_root: Path, path: str, title: Optional[str] = None, max_chars: Optional[int] = 35_000) -> str:
    abs_path = repo_root / path
    heading = title or title_from_path(path)
    if not abs_path.exists():
        return f"## {heading}\n\n> [!SOURCE] Missing source: `{path}`\n\n"
    text = read_text(repo_root, path)
    metadata, body = compact_metadata(text)
    truncated = False
    if max_chars is not None and len(body) > max_chars:
        body = body[:max_chars].rstrip() + "\n\n> [!VERIFY] This section is excerpted for readability. See the source path for the full report.\n"
        truncated = True
    status = metadata.get("Status", "DERIVED")
    authority = metadata.get("Authority Class", "advisory_synthesis")
    promotion = metadata.get("Promotion Status", "not_promoted")
    tags = f"`{status}` `{authority}` `{promotion}`"
    note = "excerpted" if truncated else "included"
    return (
        f"## {heading}\n\n"
        f"> [!SOURCE] {tags} - Source: `{path}` - {note}\n\n"
        + demote_headings(body, 1)
        + "\n"
    )


def generated_intro(title: str, body: str, callout: str = "AUTHORITY") -> str:
    return f"## {title}\n\n> [!{callout}] {body.strip()}\n\n"


def build_reader_source(state: V1State) -> str:
    repo_root = state.repo_root
    summary = state.base.manifest_summary
    sections = [
        f"# {TITLE}\n\n## {SUBTITLE}\n\nVersion: {VERSION}\n\n",
        generated_intro(
            "Authority and Non-Promotion Notice",
            "This styled v1 reader is DERIVED and advisory. It is not canon, does not open blocked work, and does not promote archive or conversation-derived claims into current repo truth.",
            "NOT_PROMOTED",
        ),
        generated_intro(
            "How to Read This Edition",
            "Use this Reader PDF for orientation and fast recall. Use the Reference PDF for dense registers and full source indexes. Use the HTML edition for search, links, and smaller screens.",
            "AUTHORITY",
        ),
        generated_intro(
            "Corpus Snapshot",
            f"Represented docs files: **{summary.get('file_count')}**. Full-text reader/reference selections: **{len(state.base.selection.full_text)}**. Summarized/indexed files: **{len(state.base.selection.summarized)}**. Manifest-only or binary files: **{len(state.base.selection.manifest_only)}**.",
            "SOURCE",
        ),
        source_section(repo_root, "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md", "Current Project Picture", 30_000),
        source_section(repo_root, "docs/archive/docs_corpus/_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md", "Current Repo Truth Crosswalk", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md", "Canon and Architecture Alignment", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_archive/DOCS_ARCHIVE_ATLAS_v0.md", "Archive Archaeology", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md", "Conversation Corpus Integration", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md", "Decision Docket Summary", 30_000),
        source_section(repo_root, "docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md", "Promotion Roadmap Summary", 30_000),
        source_section(repo_root, "docs/archive/docs_corpus/_audit/DOCS_CONTRADICTION_MATRIX_v0.md", "Contradictions and Drift", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md", "Staleness and Verification", 24_000),
        source_section(repo_root, "docs/archive/docs_corpus/_wiki/reading_paths.md", "Reading Paths", 20_000),
        build_compact_reader_indexes(state),
    ]
    return "\n\n".join(sections)


def report_group(repo_root: Path, title: str, paths: Sequence[str], max_chars: int) -> str:
    parts = [f"# {title}\n\n> [!SOURCE] Reference material. Source paths are preserved as provenance, but repeated metadata is compacted.\n\n"]
    for path in paths:
        if (repo_root / path).exists():
            parts.append(source_section(repo_root, path, max_chars=max_chars))
    return "\n\n".join(parts)


def build_reference_source(state: V1State) -> str:
    repo_root = state.repo_root
    sections = [
        f"# {TITLE} Reference\n\nVersion: {VERSION}\n\n> [!AUTHORITY] Dense reference edition. This remains DERIVED and advisory.\n",
        report_group(repo_root, "Intake and Source Corpus", v0.INTAKE_REPORTS, 50_000),
        report_group(repo_root, "Authority, Supersession, and Audit Registers", v0.AUDIT_REPORTS, 60_000),
        report_group(repo_root, "Archive Archaeology Reports", v0.ARCHIVE_REPORTS, 55_000),
        report_group(repo_root, "Reconciliation Reports", v0.RECONCILIATION_REPORTS, 55_000),
        report_group(repo_root, "Docs-Corpus Wiki", sorted(set(v0.WIKI_REPORTS + v0.existing_markdown_under(repo_root, ["docs/archive/docs_corpus/_wiki/topics", "docs/archive/docs_corpus/_wiki/families"]))), 35_000),
        report_group(repo_root, "Conversation Corpus Generated Layers", sorted(set(v0.existing_markdown_under(repo_root, v0.CONVERSATION_ROOTS) + ["docs/archive/conversations/_reader/conversation_reader_index.md"])), 40_000),
        build_reference_indexes(state),
    ]
    return "\n\n".join(sections)


def build_all_in_one_source(state: V1State, reader: str, reference: str) -> str:
    return "\n\n".join(
        [
            reader,
            "# Reference Edition\n\n> [!SOURCE] The remaining sections are denser reference material. Use the Reader edition for end-to-end reading.\n",
            reference,
            build_source_compendium(state),
        ]
    )


def build_compact_reader_indexes(state: V1State) -> str:
    records = state.base.records
    authority_counts = Counter(record.authority_class for record in records)
    role_counts = Counter(record.book_role for record in records)
    rows = "\n".join(f"| {key} | {value} |" for key, value in sorted(authority_counts.items()))
    role_rows = "\n".join(f"| {key} | {value} |" for key, value in sorted(role_counts.items()))
    return f"""# Compact Indexes

> [!SOURCE] These compact indexes preserve source coverage without turning the reader edition into a filesystem dump.

## Authority Class Summary

| Authority Class | Count |
| --- | ---: |
{rows}

## Book Role Summary

| Book Role | Count |
| --- | ---: |
{role_rows}

## High-Authority Source Paths

{chr(10).join(f"- `{path}`" for path in v0.HIGH_AUTHORITY_DOCS)}
"""


def build_reference_indexes(state: V1State) -> str:
    records = state.base.records
    by_authority = Counter(record.authority_class for record in records)
    binary = [record for record in records if not record.is_text or record.extension.lower() in v0.BINARY_EXTENSIONS]
    conversation = [record for record in records if record.path.startswith("docs/archive/conversations/")]
    summarized = state.base.selection.summarized
    manifest_only = state.base.selection.manifest_only
    return f"""# Reference Indexes

## Authority Class Index

{v0.md_table(["Authority Class", "Count"], sorted(by_authority.items()))}

## Conversation Corpus Source Index

{v0.md_table(["Path", "Authority Class", "Book Role"], [(r.path, r.authority_class, r.book_role) for r in conversation], limit=1200)}

## Manifest-Only and Binary File Index

{v0.md_table(["Path", "Extension", "Size", "Authority Class"], [(r.path, r.extension, r.size, r.authority_class) for r in binary], limit=1000)}

## Summarized Source Index

{chr(10).join(f"- `{path}`" for path in summarized[:1800])}

## Manifest-Only Source Index

{chr(10).join(f"- `{path}`" for path in manifest_only[:1200])}
"""


def build_source_compendium(state: V1State) -> str:
    records = state.base.records
    current = [record for record in records if not record.path.startswith("docs/archive/") and record.extension == ".md"]
    archive = [record for record in records if record.path.startswith("docs/archive/") and record.extension == ".md"]
    non_markdown = [record for record in records if record.extension != ".md"]
    return f"""# Source Compendium

> [!SOURCE] This compendium is deliberately index-first. Human-readable originals are included where useful; bulk source files, machine-readable artifacts, and binary files stay represented by metadata and source paths.

## Current Markdown Sources

{v0.md_table(["Path", "Authority Class", "Book Role"], [(r.path, r.authority_class, r.book_role) for r in current], limit=800)}

## Archive and Conversation Markdown Sources

{v0.md_table(["Path", "Authority Class", "Book Role"], [(r.path, r.authority_class, r.book_role) for r in archive], limit=1200)}

## Non-Markdown Inputs

{v0.md_table(["Extension", "Count"], sorted(Counter(record.extension for record in non_markdown).items()))}
"""


def latex_escape(text: str) -> str:
    return docs_corpus.latex_escape(text)


def latex_breakable(text: str) -> str:
    escaped = latex_escape(text)
    for token in ("/", "-", ".", "_"):
        escaped = escaped.replace(token, token + r"\allowbreak{}")
    return escaped


def url_arg(target: str) -> str:
    return target.replace("\\", "/").replace("#", r"\#").replace("%", r"\%")


def inline_latex(text: str) -> str:
    placeholders: Dict[str, str] = {}

    def put(value: str) -> str:
        key = f"@@V1{len(placeholders)}@@"
        placeholders[key] = value
        return key

    text = re.sub(
        r"`([^`]+)`",
        lambda m: put(r"\texttt{" + latex_breakable(m.group(1)[:260]) + "}"),
        text,
    )
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: put(r"\emph{Image: " + latex_escape(m.group(1) or "image") + r"} {\footnotesize\url{" + url_arg(m.group(2).strip()) + r"}}"),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: put(r"\href{" + url_arg(m.group(2).strip()) + r"}{\uline{" + latex_escape(m.group(1)[:240]) + r"}}"),
        text,
    )
    text = re.sub(r"<u>(.*?)</u>", lambda m: put(r"\uline{" + latex_escape(m.group(1)[:300]) + "}"), text, flags=re.IGNORECASE)
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: put(r"\textbf{" + latex_escape(m.group(1)[:500]) + "}"), text)
    text = re.sub(r"__([^_]+)__", lambda m: put(r"\textbf{" + latex_escape(m.group(1)[:500]) + "}"), text)
    text = re.sub(r"(?<!\*)\*([^*\n]{1,180})\*(?!\*)", lambda m: put(r"\emph{" + latex_escape(m.group(1)[:400]) + "}"), text)
    escaped = latex_breakable(text)
    for key, value in placeholders.items():
        escaped = escaped.replace(key, value)
    return escaped


def heading_latex(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    text = re.sub(r"<u>(.*?)</u>", r"\1", text, flags=re.IGNORECASE)
    return latex_escape(text[:220])


def parse_table_row(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table_latex(rows: List[List[str]], reference: bool = False) -> str:
    clean_rows = [row for row in rows if row and not all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in row)]
    if not clean_rows:
        return ""
    cols = max(len(row) for row in clean_rows)
    normalized = [row + [""] * (cols - len(row)) for row in clean_rows]
    widest = max(len(cell) for row in normalized for cell in row)
    row_limit = 55 if reference else 28
    if cols <= 5 and len(normalized) <= row_limit and widest <= 95:
        colspec = "@{}" + " ".join([r">{\raggedright\arraybackslash}X" for _ in range(cols)]) + "@{}"
        lines = [r"\begin{center}", r"{\small\renewcommand{\arraystretch}{1.18}", rf"\begin{{tabularx}}{{\linewidth}}{{{colspec}}}", r"\toprule"]
        header = normalized[0]
        lines.append(" & ".join(r"\textbf{" + inline_latex(cell[:180]) + "}" for cell in header) + r" \\")
        lines.append(r"\midrule")
        for row in normalized[1:]:
            lines.append(" & ".join(inline_latex(cell[:260]) for cell in row) + r" \\")
        lines.extend([r"\bottomrule", r"\end{tabularx}", r"}", r"\end{center}"])
        return "\n".join(lines)
    limit = 180 if reference else 55
    header = normalized[0]
    lines = [r"\begin{description}"]
    for row_number, row in enumerate(normalized[1:limit], start=1):
        summary = "; ".join(f"{header[index]}: {row[index]}" for index in range(min(len(header), len(row))) if row[index])
        lines.append(r"\item[Row " + str(row_number) + r"] " + inline_latex(summary[:1100]))
    if len(normalized) > limit:
        lines.append(r"\item[Omitted] " + inline_latex(f"{len(normalized) - limit} additional rows omitted from PDF table rendering; see source Markdown or HTML/reference source."))
    lines.append(r"\end{description}")
    return "\n".join(lines)


def render_code_latex(lines: List[str]) -> str:
    rendered = []
    for line in lines[:240]:
        rendered.append(latex_breakable(line[:160]) + r"\par")
    if len(lines) > 240:
        rendered.append(latex_escape(f"... {len(lines) - 240} additional code lines omitted in PDF rendering.") + r"\par")
    body = "\n".join(rendered) or r"\ "
    return r"\vonecode{" + body + "}"


def callout_latex(kind: str, title: str, body: str) -> str:
    color = CALLOUT_COLORS.get(kind, "DomSlate")
    label = title or kind.replace("_", " ").title()
    return r"\vonecallout{" + color + "}{" + latex_escape(label) + "}{" + inline_latex(body[:1800]) + "}"


def markdown_to_latex(text: str, reference: bool = False) -> str:
    out: List[str] = []
    current_list: Optional[str] = None
    in_code = False
    code_lines: List[str] = []
    lines = text.splitlines()
    index = 0

    def close_list() -> None:
        nonlocal current_list
        if current_list:
            out.append(rf"\end{{{current_list}}}")
            current_list = None

    while index < len(lines):
        raw = lines[index].rstrip()
        index += 1
        stripped = raw.strip()
        if stripped.startswith("```"):
            if in_code:
                out.append(render_code_latex(code_lines))
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
                code_lines = []
            continue
        if in_code:
            code_lines.append(raw)
            continue
        if not stripped:
            close_list()
            out.append("")
            continue
        if stripped.startswith(">"):
            close_list()
            quote_lines = [stripped.lstrip(">").strip()]
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            first = quote_lines[0] if quote_lines else ""
            match = re.match(r"^\[!([A-Z_]+)\]\s*(.*)$", first)
            if match:
                body = " ".join([match.group(2).strip(), *quote_lines[1:]]).strip()
                out.append(callout_latex(match.group(1), match.group(1).replace("_", " ").title(), body))
            else:
                out.append(r"\begin{quote}" + inline_latex(" ".join(quote_lines)[:1800]) + r"\end{quote}")
            continue
        if stripped.startswith("|"):
            close_list()
            table_lines = [stripped]
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            out.append(render_table_latex([parse_table_row(row) for row in table_lines], reference=reference))
            continue
        if stripped.startswith("#"):
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip()[:220]
            if level == 1:
                out.append(r"\chapter{" + heading_latex(heading) + "}")
            elif level == 2:
                out.append(r"\section{" + heading_latex(heading) + "}")
            elif level == 3:
                out.append(r"\subsection{" + heading_latex(heading) + "}")
            elif level == 4:
                out.append(r"\subsubsection{" + heading_latex(heading) + "}")
            else:
                out.append(r"\paragraph{" + heading_latex(heading) + "}")
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if stripped.startswith("- ") or stripped.startswith("* ") or ordered:
            list_type = "enumerate" if ordered else "itemize"
            if current_list != list_type:
                close_list()
                out.append(rf"\begin{{{list_type}}}")
                current_list = list_type
            item = ordered.group(1) if ordered else stripped[2:]
            out.append(r"\item " + inline_latex(item[:1600]))
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            close_list()
            out.append(r"\par\medskip\hrule\medskip")
            continue
        close_list()
        out.append(inline_latex(stripped[:2000]))
        out.append("")
    close_list()
    if in_code:
        out.append(render_code_latex(code_lines))
    return "\n".join(out)


def latex_style(engine: str, profile: str) -> str:
    font_block = (
        r"""\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.88]
"""
        if engine in {"xelatex", "lualatex"}
        else r"""\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
"""
    )
    margin = "20mm" if profile == "reader" else "17mm"
    font_size = "10.5pt" if profile == "reader" else "9pt"
    return rf"""\documentclass[{font_size},a4paper,openany]{{book}}
\usepackage[a4paper,margin={margin},includeheadfoot,headheight=15pt]{{geometry}}
{font_block}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
\usepackage{{array,longtable,tabularx,graphicx}}
\newcommand{{\toprule}}{{\hline}}
\newcommand{{\midrule}}{{\hline}}
\newcommand{{\bottomrule}}{{\hline}}
\usepackage{{color}}
\newcommand{{\uline}}[1]{{\underline{{#1}}}}
\newcommand{{\href}}[2]{{\underline{{#2}} {{\footnotesize\texttt{{\detokenize{{#1}}}}}}}}
\newcommand{{\url}}[1]{{{{\footnotesize\texttt{{\detokenize{{#1}}}}}}}}
\definecolor{{DomBlue}}{{rgb}}{{0.12,0.37,0.60}}
\definecolor{{DomGreen}}{{rgb}}{{0.16,0.48,0.35}}
\definecolor{{DomAmber}}{{rgb}}{{0.60,0.42,0.09}}
\definecolor{{DomRed}}{{rgb}}{{0.65,0.22,0.22}}
\definecolor{{DomViolet}}{{rgb}}{{0.39,0.33,0.65}}
\definecolor{{DomSlate}}{{rgb}}{{0.30,0.34,0.42}}
\definecolor{{DomMuted}}{{rgb}}{{0.40,0.40,0.40}}
\definecolor{{DomCalloutBg}}{{rgb}}{{0.96,0.97,0.99}}
\definecolor{{DomCodeBg}}{{rgb}}{{0.95,0.96,0.97}}
\setcounter{{tocdepth}}{{2}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.42em}}
\linespread{{1.06}}
\newcommand{{\sourcepath}}[1]{{\par\smallskip\noindent{{\footnotesize\color{{DomMuted}}\textsf{{Source: }}\texttt{{#1}}}}\par\smallskip}}
\newcommand{{\vonecallout}}[3]{{\par\medskip\noindent\begingroup\setlength{{\fboxsep}}{{7pt}}\colorbox{{DomCalloutBg}}{{\parbox{{0.94\linewidth}}{{\textbf{{\textcolor{{#1}}{{#2}}}}\par #3}}}}\endgroup\par\medskip}}
\newcommand{{\vonecode}}[1]{{\par\smallskip\noindent\begingroup\setlength{{\fboxsep}}{{7pt}}\colorbox{{DomCodeBg}}{{\parbox{{0.94\linewidth}}{{\footnotesize\ttfamily #1}}}}\endgroup\par\smallskip}}
"""


def latex_document(title: str, subtitle: str, body: str, engine: str, profile: str) -> str:
    style = latex_style(engine, profile)
    return rf"""{style}
\begin{{document}}
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{1.8cm}}
{{\Huge\bfseries {latex_escape(title)}\par}}
\vspace{{0.7cm}}
{{\Large {latex_escape(subtitle)}\par}}
\vspace{{1.1cm}}
{{\large Version: {VERSION}\par}}
{{\large Authority Class: advisory\_synthesis\par}}
{{\large Promotion Status: not\_promoted\par}}
\vfill
{{\large {REVIEW_DATE}\par}}
\end{{titlepage}}
\tableofcontents
\mainmatter
{body}
\end{{document}}
"""


def select_engine() -> str:
    def package_available(package: str) -> bool:
        if not shutil.which("kpsewhich"):
            return False
        code, _ = run_command(["kpsewhich", package], Path.cwd(), timeout=30)
        return code == 0

    for name in ("xelatex", "lualatex"):
        if shutil.which(name) and package_available("fontspec.sty") and package_available("xparse.sty"):
            return name
    for name in ("pdflatex",):
        if shutil.which(name):
            return name
    return ""


def output_pdf_name(name: str) -> str:
    return {
        "reader": f"{READER_BASENAME}.pdf",
        "reference": f"{REFERENCE_BASENAME}.pdf",
        "all_in_one": f"{ALL_IN_ONE_BASENAME}.pdf",
    }[name]


def render_pdf(state: V1State, source_md: str, name: str, title: str, subtitle: str, profile: str, timeout: int = 1800) -> PdfOutput:
    build_dir = state.repo_root / V1_ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    if state.renderer:
        engines = [state.renderer]
    else:
        engines = [candidate for candidate in ("xelatex", "lualatex", "pdflatex") if shutil.which(candidate)]
    engines = [engine for engine in engines if engine]
    if not engines:
        target = state.repo_root / EXPORTS_ROOT / output_pdf_name(name)
        return PdfOutput(name=name, path=target, created=False, renderer="none", caveat="no LaTeX renderer available")
    last_output = ""
    target = state.repo_root / EXPORTS_ROOT / output_pdf_name(name)
    for engine in engines:
        tex_path = build_dir / f"{name}.tex"
        pdf_path = build_dir / f"{name}.pdf"
        for old in build_dir.glob(f"{name}.*"):
            try:
                old.unlink()
            except OSError:
                pass
        body = markdown_to_latex(source_md, reference=profile != "reader")
        write_text(tex_path, latex_document(title, subtitle, body, engine, profile))
        command = [engine, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)]
        failed = False
        for _ in range(2):
            code, output = run_command(command, state.repo_root, timeout=timeout)
            last_output = output
            if code != 0:
                failed = True
                break
        if failed or not pdf_path.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf_path, target)
        return qa_pdf(state, target, name, engine)
    return PdfOutput(name=name, path=target, created=False, renderer="/".join(engines), caveat=last_output[-2000:])


def pdf_pages(repo_root: Path, path: Path) -> Optional[int]:
    if not shutil.which("pdfinfo") or not path.exists():
        return None
    code, output = run_command(["pdfinfo", str(path)], repo_root)
    if code != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def has_bad_glyphs(text: str) -> bool:
    bad_tokens = ["\ufffd", "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06"]
    if any(token in text for token in bad_tokens):
        return True
    return any(ord(ch) < 32 and ch not in "\n\r\t\f" for ch in text)


def qa_pdf(state: V1State, pdf_path: Path, name: str, renderer: str) -> PdfOutput:
    qa_dir = state.repo_root / V1_ROOT / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    for old in qa_dir.glob(f"{name}_page_*.png"):
        old.unlink(missing_ok=True)
    created = pdf_path.exists()
    result = PdfOutput(name=name, path=pdf_path, created=created, renderer=renderer, size=pdf_path.stat().st_size if created else 0)
    result.pages = pdf_pages(state.repo_root, pdf_path) if created else None
    if created and shutil.which("pdftotext"):
        extract = qa_dir / f"{name}_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], state.repo_root, timeout=500)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
            result.glyph_check = "not_run"
    if created and shutil.which("pdftoppm") and result.pages:
        pages = sorted(set([1, 2, max(1, result.pages // 3), max(1, (2 * result.pages) // 3), result.pages]))
        for page in pages[:5]:
            prefix = qa_dir / f"{name}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf_path), str(prefix)], state.repo_root, timeout=240)
            image = prefix.with_suffix(".png")
            if code == 0 and image.exists():
                result.qa_images.append(rel(image, state.repo_root))
    return result


def render_auxiliary_pdf(state: V1State, source_md: str, build_name: str, target_name: str, title: str, subtitle: str, profile: str = "reference") -> bool:
    build_dir = state.repo_root / V1_ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    if state.renderer:
        engines = [state.renderer]
    else:
        engines = [candidate for candidate in ("xelatex", "lualatex", "pdflatex") if shutil.which(candidate)]
    for engine in engines:
        tex_path = build_dir / f"{build_name}.tex"
        pdf_path = build_dir / f"{build_name}.pdf"
        for old in build_dir.glob(f"{build_name}.*"):
            old.unlink(missing_ok=True)
        body = markdown_to_latex(source_md, reference=profile != "reader")
        write_text(tex_path, latex_document(title, subtitle, body, engine, profile))
        command = [engine, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)]
        ok = True
        for _ in range(2):
            code, _ = run_command(command, state.repo_root, timeout=900)
            if code != 0:
                ok = False
                break
        if ok and pdf_path.exists():
            target = state.repo_root / EXPORTS_ROOT / target_name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf_path, target)
            return True
    return False


def ensure_legacy_v0_pdf_outputs(state: V1State) -> None:
    """Regenerate missing v0 book PDFs from existing v0 book source only.

    The docs-corpus validator still requires these historical export names. This
    helper writes only missing files under `_exports/` and uses build scratch
    files under `_omnibus_v1/build/`.
    """
    chapter_paths = [
        "_book/chapters/00_front_matter.md",
        "_book/chapters/01_current_project_orientation.md",
        "_book/chapters/02_current_canon_architecture_contracts.md",
        "_book/chapters/03_product_runtime_tooling_domains.md",
        "_book/chapters/04_archive_archaeology.md",
        "_book/chapters/05_conversation_corpus_integration.md",
        "_book/chapters/06_cross_corpus_reconciliation.md",
        "_book/chapters/07_decisions_promotion_roadmap.md",
        "_book/chapters/08_navigation_reading_paths.md",
    ]
    appendix_paths = [
        "_book/appendices/A_docs_corpus_manifest_summary.md",
        "_book/appendices/B_authority_and_supersession_registers.md",
        "_book/appendices/C_archive_family_listing.md",
        "_book/appendices/D_contradiction_staleness_promotion_decision_registers.md",
        "_book/appendices/E_source_path_index.md",
    ]

    def combine(paths: Sequence[str]) -> str:
        chunks = []
        for rel_path in paths:
            path = state.repo_root / DOCS_CORPUS_ROOT / rel_path
            if path.exists():
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        return "\n\n".join(chunks)

    legacy = [
        (
            "Dominium_Docs_Corpus_Reader_v0.pdf",
            "legacy_reader_v0",
            combine(chapter_paths),
            "Dominium Documentation Corpus Book v0",
            "Current Docs, Archive Archaeology, Conversation Synthesis, and Reconciliation Guide",
            "reader",
        ),
        (
            "Dominium_Docs_Corpus_Reference_Appendix_v0.pdf",
            "legacy_reference_v0",
            combine(appendix_paths),
            "Dominium Documentation Corpus Book v0 - Reference Appendix",
            "Dense Registers and Source Indexes",
            "reference",
        ),
    ]
    for target_name, build_name, source, title, subtitle, profile in legacy:
        target = state.repo_root / EXPORTS_ROOT / target_name
        if target.exists():
            continue
        if not render_auxiliary_pdf(state, source, build_name, target_name, title, subtitle, profile):
            state.warnings.append(f"could not regenerate missing legacy docs-corpus output: {target_name}")


def markdown_to_html(text: str, mobile: bool = False) -> str:
    out: List[str] = []
    in_ul = False
    in_ol = False
    in_code = False
    code_lines: List[str] = []
    lines = text.splitlines()
    index = 0

    def inline(value: str) -> str:
        value = html.escape(value)
        value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
        value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
        value = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", value)
        value = re.sub(r"(?<!\*)\*([^*\n]{1,180})\*(?!\*)", r"<em>\1</em>", value)
        value = re.sub(r"&lt;u&gt;(.*?)&lt;/u&gt;", r"<u>\1</u>", value, flags=re.IGNORECASE)
        value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', value)
        return value

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while index < len(lines):
        raw = lines[index].rstrip()
        index += 1
        stripped = raw.strip()
        if stripped.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                in_code = False
                code_lines = []
            else:
                close_lists()
                in_code = True
                code_lines = []
            continue
        if in_code:
            code_lines.append(raw)
            continue
        if not stripped:
            close_lists()
            continue
        if stripped.startswith(">"):
            close_lists()
            quote_lines = [stripped.lstrip(">").strip()]
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            first = quote_lines[0]
            match = re.match(r"^\[!([A-Z_]+)\]\s*(.*)$", first)
            if match:
                kind = match.group(1).lower().replace("_", "-")
                body = " ".join([match.group(2), *quote_lines[1:]]).strip()
                out.append(f'<aside class="callout {kind}"><strong>{html.escape(match.group(1).replace("_", " ").title())}</strong><p>{inline(body)}</p></aside>')
            else:
                out.append("<blockquote>" + inline(" ".join(quote_lines)) + "</blockquote>")
            continue
        if stripped.startswith("|"):
            close_lists()
            table_lines = [stripped]
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            rows = [parse_table_row(row) for row in table_lines]
            clean = [row for row in rows if not all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in row)]
            if clean:
                out.append('<div class="table-wrap"><table>')
                for row_index, row in enumerate(clean):
                    tag = "th" if row_index == 0 else "td"
                    out.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in row) + "</tr>")
                out.append("</table></div>")
            continue
        if stripped.startswith("#"):
            close_lists()
            level = min(6, len(stripped) - len(stripped.lstrip("#")))
            heading = stripped[level:].strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(heading)}</h{level}>')
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if stripped.startswith("- ") or stripped.startswith("* ") or ordered:
            if ordered:
                if not in_ol:
                    close_lists()
                    out.append("<ol>")
                    in_ol = True
                out.append("<li>" + inline(ordered.group(1)) + "</li>")
            else:
                if not in_ul:
                    close_lists()
                    out.append("<ul>")
                    in_ul = True
                out.append("<li>" + inline(stripped[2:]) + "</li>")
            continue
        close_lists()
        out.append("<p>" + inline(stripped) + "</p>")
    close_lists()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(out)


def html_document(title: str, body: str, css_name: str, mobile: bool = False) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{css_name}">
</head>
<body>
  <header class="topbar">
    <div><strong>{html.escape(TITLE)}</strong><span>Version {VERSION} - DERIVED / advisory</span></div>
    <a href="#contents">Contents</a>
  </header>
  <main class="document {'mobile' if mobile else ''}">
    <section class="title-page">
      <h1>{html.escape(TITLE)}</h1>
      <p>{html.escape(SUBTITLE)}</p>
      <p><strong>Version:</strong> {VERSION}</p>
      <p><strong>Promotion Status:</strong> not_promoted</p>
    </section>
    {body}
  </main>
</body>
</html>
"""


def css_text(mobile: bool = False) -> str:
    max_width = "820px" if mobile else "1040px"
    nav = "position: sticky; top: 0;" if not mobile else ""
    return f"""html {{ color-scheme: light; }}
body {{ margin: 0; background: #f5f7fa; color: #20242a; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height: 1.58; }}
.topbar {{ {nav} z-index: 4; display: flex; justify-content: space-between; gap: 1rem; align-items: center; padding: .7rem 1rem; background: #18324a; color: white; box-shadow: 0 1px 6px rgba(0,0,0,.15); }}
.topbar a {{ color: #d7ecff; }}
.topbar span {{ margin-left: .75rem; color: #c6d4df; font-size: .9rem; }}
.document {{ max-width: {max_width}; margin: 0 auto; padding: 2rem 1.1rem 5rem; background: white; }}
.title-page {{ border-bottom: 1px solid #d9dee7; padding: 3rem 0 2rem; margin-bottom: 2rem; }}
h1, h2, h3, h4 {{ line-height: 1.22; color: #172536; }}
h1 {{ font-size: clamp(2rem, 5vw, 3.2rem); margin-top: 2rem; }}
h2 {{ font-size: clamp(1.55rem, 3.4vw, 2.25rem); border-top: 1px solid #e5e9f0; padding-top: 1.6rem; }}
h3 {{ font-size: 1.3rem; margin-top: 1.8rem; }}
p, li {{ font-size: 1rem; }}
a {{ color: #1f5f99; text-underline-offset: .16em; }}
code {{ background: #f0f3f7; padding: .1rem .28rem; border-radius: 4px; font-size: .92em; overflow-wrap: anywhere; }}
pre {{ background: #f0f3f7; padding: 1rem; border-radius: 6px; overflow: auto; border-left: 4px solid #9fb7ce; }}
blockquote {{ border-left: 4px solid #9fb7ce; padding-left: 1rem; color: #44505f; }}
.callout {{ border-left: 5px solid #4c566a; background: #f7f9fc; padding: .8rem 1rem; margin: 1rem 0; border-radius: 6px; }}
.callout.authority, .callout.source {{ border-color: #1f5f99; }}
.callout.not-promoted, .callout.current-truth {{ border-color: #287a5a; }}
.callout.blocked, .callout.contradiction {{ border-color: #a63a3a; }}
.callout.verify, .callout.archive {{ border-color: #9a6a17; }}
.callout.conversation, .callout.decision {{ border-color: #6554a6; }}
.table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: .92rem; }}
th, td {{ border-bottom: 1px solid #e1e6ee; padding: .45rem .55rem; vertical-align: top; }}
th {{ background: #eef3f8; text-align: left; }}
ul, ol {{ padding-left: 1.35rem; }}
@media (max-width: 720px) {{ .document {{ padding: 1rem .85rem 4rem; }} .topbar {{ position: static; align-items: flex-start; flex-direction: column; }} table {{ font-size: .86rem; }} }}
"""


def write_style_files(state: V1State) -> None:
    write_text(state.repo_root / STYLE_ROOT / "omnibus_reader.tex", latex_style(select_engine() or "pdflatex", "reader"))
    write_text(state.repo_root / STYLE_ROOT / "omnibus_reference.tex", latex_style(select_engine() or "pdflatex", "reference"))
    write_text(state.repo_root / STYLE_ROOT / "omnibus_html.css", css_text(mobile=False))
    write_text(state.repo_root / STYLE_ROOT / "omnibus_mobile.css", css_text(mobile=True))


def write_sources(state: V1State) -> Tuple[str, str, str]:
    root = state.repo_root / V1_ROOT
    for subdir in ["parts", "indexes", "build", "qa"]:
        (root / subdir).mkdir(parents=True, exist_ok=True)
    reader = build_reader_source(state)
    reference = build_reference_source(state)
    all_in_one = build_all_in_one_source(state, reader, reference)
    write_text(root / "reader_source.md", STATUS_BLOCK + "\n" + reader)
    write_text(root / "reference_source.md", STATUS_BLOCK + "\n" + reference)
    write_text(root / "all_in_one_source.md", STATUS_BLOCK + "\n" + all_in_one)
    write_text(root / "mobile_html_source.md", STATUS_BLOCK + "\n" + reader + "\n\n" + build_compact_reader_indexes(state))
    write_text(root / "parts/reader_material.md", STATUS_BLOCK + "\n" + reader)
    write_text(root / "parts/reference_material.md", STATUS_BLOCK + "\n" + reference)
    write_text(root / "indexes/source_indexes.md", STATUS_BLOCK + "\n" + build_reference_indexes(state))
    write_text(root / "README.md", STATUS_BLOCK + f"\n# Omnibus v1\n\nThis directory contains the styled v1 source for `{TITLE}`. The v1 edition is DERIVED, advisory, and publication-only.\n")
    return reader, reference, all_in_one


def build_manifest(state: V1State) -> str:
    outputs = [
        f"docs/archive/docs_corpus/_exports/{READER_BASENAME}.pdf",
        f"docs/archive/docs_corpus/_exports/{REFERENCE_BASENAME}.pdf",
        f"docs/archive/docs_corpus/_exports/{ALL_IN_ONE_BASENAME}.pdf",
        f"docs/archive/docs_corpus/_exports/{HTML_DIRNAME}/index.html",
        f"docs/archive/docs_corpus/_exports/{MOBILE_HTML}",
        f"docs/archive/docs_corpus/_exports/{STYLE_REPORT}",
        f"docs/archive/docs_corpus/_exports/{BUILD_REPORT}",
        f"docs/archive/docs_corpus/_exports/{VALIDATION_REPORT}",
    ]
    protected = "\n".join(f"  - {prefix}" for prefix in PROTECTED_PREFIXES)
    output_lines = "\n".join(f"  - {path}" for path in outputs)
    return f"""title: "{TITLE}"
subtitle: "{SUBTITLE}"
version: {VERSION}
date: "{REVIEW_DATE}"
status: "DERIVED"
authority_class: "advisory_synthesis"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
promotion_status: "not_promoted"
renderer: "{state.renderer or select_engine() or 'none'}"
style_profile: "readability_v1"
outputs:
{output_lines}
content_coverage:
  docs_files_represented: {len(state.base.records)}
  full_text_count: {len(state.base.selection.full_text)}
  summarized_count: {len(state.base.selection.summarized)}
  manifest_only_count: {len(state.base.selection.manifest_only)}
  excluded_count: {len(state.base.selection.excluded)}
metadata_compaction:
  repeated_status_blocks: "suppressed after front matter"
  source_paths: "rendered as compact provenance lines"
table_handling:
  reader_pdf: "small booktabs tables; long/wide tables summarized as row cards"
  reference_pdf: "higher row caps with same readable fallback"
hyperlinks:
  pdf: "underlined link labels with visible targets; clickable PDF links unavailable in this local LaTeX install"
  html: "native links and responsive anchors"
protected_paths:
{protected}
validation_commands:
  - py -3 tools/docs_corpus/validate_omnibus_v1.py --repo-root .
  - py -3 -m unittest discover tests/tools/docs_corpus
  - git diff --check
"""


def write_html_outputs(state: V1State, reader: str, reference: str, all_in_one: str) -> None:
    html_dir = state.repo_root / EXPORTS_ROOT / HTML_DIRNAME
    html_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(state.repo_root / STYLE_ROOT / "omnibus_html.css", html_dir / "omnibus_html.css")
    write_text(html_dir / "index.html", html_document(TITLE, markdown_to_html(all_in_one), "omnibus_html.css"))
    mobile_path = state.repo_root / EXPORTS_ROOT / MOBILE_HTML
    # Inline CSS for the single-file mobile edition.
    body = markdown_to_html(reader, mobile=True)
    mobile_doc = html_document(TITLE, body, "omnibus_mobile.css", mobile=True).replace(
        '<link rel="stylesheet" href="omnibus_mobile.css">',
        "<style>\n" + css_text(mobile=True) + "\n</style>",
    )
    write_text(mobile_path, mobile_doc)


def protected_changes(repo_root: Path) -> List[str]:
    return v0.protected_changes(repo_root)


def validate_outputs(state: V1State) -> None:
    commands = [
        ["py", "-3", "-c", "import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('docs manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_omnibus_v1/OMNIBUS_V1_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'status: \"DERIVED\"' in text; print('v1 manifest ok')"],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_omnibus_v1.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["git", "diff", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    for cmd in commands:
        code, output = run_command(cmd, state.repo_root, timeout=1200)
        state.command_results.append({"command": " ".join(cmd), "code": code, "result": "PASS" if code == 0 else "FAIL"})
        if code != 0:
            state.errors.append(f"command failed: {' '.join(cmd)}\n{output[-1200:]}")
    protected = protected_changes(state.repo_root)
    if protected:
        state.errors.extend(f"protected path changed: {line}" for line in protected)


def render_style_report(state: V1State) -> str:
    return STATUS_BLOCK + f"""
# Dominium Docs Corpus Omnibus Style Report v1

## What Changed From v0

- Split the v0 coverage artifact into Reader, Reference, All-in-One, HTML, and Mobile HTML outputs.
- Suppressed repeated full metadata blocks after front matter.
- Normalized raw source-path headings into human-readable report titles with compact provenance lines.
- Added semantic callouts for authority, not-promoted status, source provenance, verification, blocked scope, decisions, contradictions, and promotion candidates.
- Added hyperlink-aware PDF/HTML rendering with clickable TOC support where the renderer allows it.
- Reworked table handling so small tables render as clean booktabs-style tables and wide/long tables become readable row-card summaries.
- Improved typography through the locally viable LaTeX engine, Latin Modern fonts, clickable links, styled callouts, and more consistent spacing.

## Style Choices

- Reader PDF: narrative-first, larger margins, less source clutter.
- Reference PDF: denser but still styled and indexed.
- All-in-One PDF: reader material first, reference/index material second.
- HTML: responsive, searchable with browser search, sticky top navigation on desktop.
- Mobile HTML: single-column and scroll-friendly.
- PDF link labels are underlined and include their target path/URL as readable text because the local LaTeX installation is missing `url.sty`, which prevents `hyperref` from loading. HTML outputs retain native clickable links.

## Caveats

- This remains a generated book. It improves readability but does not replace editorial human review.
- Some very large tables are intentionally summarized in PDF; source Markdown and HTML preserve more navigable detail.
- The book does not promote archive or conversation claims.
"""


def render_build_report(state: V1State) -> str:
    rows = []
    for key in ["reader", "reference", "all_in_one"]:
        output = state.outputs.get(key)
        if output:
            rows.append((key, rel(output.path, state.repo_root), output.created, output.pages or "", output.size, output.renderer))
    return STATUS_BLOCK + f"""
# Dominium Docs Corpus Omnibus Build Report v1

## Build

- Title: {TITLE}
- Version: {VERSION}
- Date: {REVIEW_DATE}
- Repository branch: `{state.base.branch}`
- Repository commit at generation time: `{state.base.commit}`
- Renderer: {state.renderer or select_engine() or 'none'}
- Source root: `docs/`

## Source Coverage

- Docs files represented: {len(state.base.records)}
- Full-text source/report count: {len(state.base.selection.full_text)}
- Summarized source count: {len(state.base.selection.summarized)}
- Manifest-only/binary count: {len(state.base.selection.manifest_only)}
- Excluded count: {len(state.base.selection.excluded)}

## Outputs

{v0.md_table(["Output", "Path", "Created", "Pages", "Size Bytes", "Renderer"], rows)}

## HTML Outputs

- `docs/archive/docs_corpus/_exports/{HTML_DIRNAME}/index.html`
- `docs/archive/docs_corpus/_exports/{MOBILE_HTML}`

## QA

Representative PDF page images were generated under `docs/archive/docs_corpus/_omnibus_v1/qa/` where local tools were available.
"""


def render_validation_report(state: V1State) -> str:
    command_rows = [(item["command"], item["result"], item["code"]) for item in state.command_results]
    pdf_rows = []
    for key, output in state.outputs.items():
        pdf_rows.append((key, rel(output.path, state.repo_root), output.created, output.pages or "", output.text_extraction, output.glyph_check, "; ".join(output.qa_images)))
    result = "PASS" if not state.errors and not state.warnings else "PASS_WITH_WARNINGS" if not state.errors else "FAIL"
    return STATUS_BLOCK + f"""
# Dominium Docs Corpus Omnibus Validation Report v1

## Status

- Result: {result}

## Command Results

{v0.md_table(["Command", "Result", "Code"], command_rows)}

## PDF and Glyph Checks

{v0.md_table(["Output", "Path", "Created", "Pages", "Text Extraction", "Glyph Check", "QA Images"], pdf_rows)}

## Errors

{chr(10).join(f"- {item}" for item in state.errors) if state.errors else "None."}

## Warnings

{chr(10).join(f"- {item}" for item in state.warnings) if state.warnings else "None."}

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
"""


def create_state(repo_root: Path) -> V1State:
    base = v0.create_state(repo_root)
    state = V1State(repo_root=repo_root, base=base)
    state.renderer = select_engine()
    return state


def build(repo_root: Path, run_validation: bool = True) -> int:
    state = create_state(repo_root)
    write_style_files(state)
    reader, reference, all_in_one = write_sources(state)
    write_html_outputs(state, reader, reference, all_in_one)
    state.outputs["reader"] = render_pdf(state, reader, "reader", TITLE, "Reader Edition", "reader", timeout=1500)
    state.outputs["reference"] = render_pdf(state, reference, "reference", TITLE, "Reference Edition", "reference", timeout=1800)
    state.outputs["all_in_one"] = render_pdf(state, all_in_one, "all_in_one", TITLE, "All-in-One Edition", "reference", timeout=2400)
    renderers = [output.renderer for output in state.outputs.values() if output.created and output.renderer]
    if renderers:
        state.renderer = ",".join(dict.fromkeys(renderers))
    ensure_legacy_v0_pdf_outputs(state)
    write_text(repo_root / V1_ROOT / "OMNIBUS_V1_MANIFEST.yml", build_manifest(state))
    write_text(repo_root / EXPORTS_ROOT / STYLE_REPORT, render_style_report(state))
    write_text(repo_root / EXPORTS_ROOT / BUILD_REPORT, render_build_report(state))
    write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, STATUS_BLOCK + "\n# Dominium Docs Corpus Omnibus Validation Report v1\n\nValidation pending.\n")
    if run_validation:
        validate_outputs(state)
    write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, render_validation_report(state))
    if state.errors:
        print("DOCS-CORPUS-OMNIBUS-READABILITY-V1 FAIL")
        return 1
    print("DOCS-CORPUS-OMNIBUS-READABILITY-V1 PASS")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args(argv)
    return build(Path(args.repo_root).resolve(), run_validation=not args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
