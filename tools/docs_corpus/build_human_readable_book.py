"""Build a human-readable Dominium project book from the docs corpus.

This pipeline is intentionally different from the Omnibus renderer. It treats
the docs-corpus manifest as an inventory, selects prose-first sources for a
curated source reader, and generates a synthesized book whose main body is
readable narrative instead of a file dump.

Generated outputs are DERIVED and advisory. Source docs are not modified.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import textwrap
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape as xml_escape

import build_omnibus_v1 as styled
import docs_corpus


TASK_ID = "DOMINIUM-HUMAN-READABLE-BOOK-RESET-01"
REVIEW_DATE = "2026-05-29"
VERSION = 1
TITLE = "Dominium Human-Readable Project Book"
SUBTITLE = "A Synthesized Reader for Current Docs, Archive Context, and Conversation Evidence"

DOCS_CORPUS_ROOT = Path("docs/archive/docs_corpus")
HUMAN_SOURCE_ROOT = DOCS_CORPUS_ROOT / "_human_source"
HUMAN_BOOK_ROOT = DOCS_CORPUS_ROOT / "_human_book"
EXPORTS_ROOT = DOCS_CORPUS_ROOT / "_exports"

MAIN_PDF = "Dominium_Human_Readable_Book_v1.pdf"
MAIN_HTML_DIR = "Dominium_Human_Readable_Book_v1.html"
MAIN_DOCX = "Dominium_Human_Readable_Book_v1.docx"
SOURCE_READER_PDF = "Dominium_Human_Source_Reader_v1.pdf"
SOURCE_READER_HTML_DIR = "Dominium_Human_Source_Reader_v1.html"
BUILD_REPORT = "Dominium_Human_Readable_Book_v1_Build_Report.md"
VALIDATION_REPORT = "Dominium_Human_Readable_Book_v1_Validation_Report.md"

PROTECTED_PREFIXES = docs_corpus.PROTECTED_PREFIXES

REPORT_STATUS_BLOCK = f"""Status: DERIVED
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

BOOK_NOTICE = """Version: 1
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

HIGH_AUTHORITY_SOURCES = [
    "README.md",
    "docs/README.md",
    "AGENTS.md",
    "docs/canon/constitution_v1.md",
    "docs/canon/glossary_v1.md",
    "docs/repo/FOUNDATION_LOCK.md",
    "docs/architecture/WHAT_THIS_IS.md",
    "docs/architecture/WHAT_THIS_IS_NOT.md",
    "docs/architecture/INVARIANTS.md",
    "docs/architecture/CANONICAL_SYSTEM_MAP.md",
    "docs/architecture/CONTRACTS_INDEX.md",
]

SYNTHESIS_SOURCES = [
    "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md",
    "docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md",
    "docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md",
    "docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md",
    "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md",
    "docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md",
    "docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md",
    "docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md",
]

MACHINE_NAME_PATTERNS = [
    "manifest",
    "source_index",
    "file_counts",
    "tree_summary",
    "sha256",
    "hash",
    "integrity",
    "register",
    "matrix",
    "queue",
    "validation",
    "build_report",
    "bundle",
    "packet",
    "spec_sheet",
    "aggregator",
    "context_transfer",
    "coverage",
    "inventory",
]

READER_NAME_PATTERNS = [
    "human_readable_report",
    "reader_brief",
    "detailed_summary",
    "accompanying_report",
    "in_chat_reader",
]

TEXT_EXTENSIONS = {".md", ".txt", ".rst"}
MACHINE_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".csv", ".tsv", ".xml"}
BINARY_EXTENSIONS = {".zip", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".docx", ".epub", ".ico", ".bin"}


@dataclass
class SourceItem:
    path: str
    disposition: str
    reason: str
    title: str
    authority_class: str = "unknown"
    family: str = "unknown"
    size: int = 0
    extension: str = ""
    source_kind: str = "docs_manifest"
    first_heading: str = ""


@dataclass
class PdfInfo:
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
class BuildState:
    repo_root: Path
    records: List[dict]
    sources: List[SourceItem]
    branch: str
    commit: str
    renderer: str = ""
    outputs: Dict[str, PdfInfo] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


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


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_text(path: Path, content: str) -> None:
    clean = "\n".join(line.rstrip(" \t") for line in content.splitlines())
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(clean) + "\n")


def read_text(path: Path, limit: Optional[int] = None) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if limit is not None and len(text) > limit:
        return text[:limit]
    return text


def load_manifest(repo_root: Path) -> List[dict]:
    path = repo_root / DOCS_CORPUS_ROOT / "_intake/DOCS_CORPUS_MANIFEST.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("files", []))


def git_branch(repo_root: Path) -> str:
    code, output = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root, timeout=60)
    return output.strip() if code == 0 else "unknown"


def git_commit(repo_root: Path) -> str:
    code, output = run_command(["git", "rev-parse", "--short", "HEAD"], repo_root, timeout=60)
    return output.strip() if code == 0 else "unknown"


def title_from_path(path: str, fallback: str = "") -> str:
    if fallback and fallback not in {"Untitled", "(none)"}:
        title = fallback.strip("# ").strip()
    else:
        title = Path(path).stem
    title = re.sub(r"^(DOCS_|Dominium_Docs_Corpus_|Dominium_Conversation_Corpus_)", "", title)
    title = re.sub(r"_(v0|v1)$", "", title, flags=re.IGNORECASE)
    title = title.replace("__", "_").replace("_", " ").replace("-", " ")
    keep = {"AIDE", "API", "CLI", "DOCS", "FAST", "GUI", "HTML", "ID", "JSON", "MCP", "PDF", "QA", "TUI", "UI", "URL", "YAML"}
    words = []
    for word in title.split():
        upper = word.upper()
        words.append(upper if upper in keep else word.capitalize())
    return " ".join(words) or path


def compact_metadata(text: str) -> Tuple[Dict[str, str], str]:
    keys = {
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
    lines = text.splitlines()
    metadata: Dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines[:50]):
        stripped = line.strip()
        if not stripped:
            body_start = index + 1
            continue
        if stripped.startswith("#"):
            body_start = index
            break
        match = re.match(r"^([^:]{2,48}):\s*(.*)$", stripped)
        if not match or match.group(1) not in keys:
            body_start = index
            break
        metadata[match.group(1)] = match.group(2)
        body_start = index + 1
    return metadata, "\n".join(lines[body_start:]).strip() + "\n"


def demote_headings(text: str, levels: int = 1) -> str:
    out: List[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            count = len(line) - len(line.lstrip("#"))
            heading = line[count:].strip()
            out.append("#" * min(6, count + levels) + " " + heading)
        else:
            out.append(line)
    return "\n".join(out).strip() + "\n"


def is_machine_named(path: str) -> bool:
    lowered = path.lower()
    return any(pattern in lowered for pattern in MACHINE_NAME_PATTERNS)


def classify_record(record: dict) -> SourceItem:
    path = record["path"]
    ext = record.get("extension", "") or Path(path).suffix.lower()
    lowered = path.lower()
    title = title_from_path(path, record.get("first_heading", ""))
    authority = record.get("authority_class", "unknown")
    family = record.get("directory_family", record.get("inferred_document_family", "unknown"))
    size = int(record.get("size", 0) or 0)
    first_heading = record.get("first_heading", "")

    if path.startswith("docs/archive/docs_corpus/_human_"):
        return SourceItem(path, "exclude_generated_recursive", "generated human-book output root", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith("docs/archive/docs_corpus/_omnibus") or path.startswith("docs/archive/docs_corpus/_exports"):
        return SourceItem(path, "reference_only", "prior generated publication artifact", title, authority, family, size, ext, first_heading=first_heading)
    if path in HIGH_AUTHORITY_SOURCES:
        return SourceItem(path, "human_full_text", "current high-authority orientation source", title, authority, family, size, ext, first_heading=first_heading)
    if path in SYNTHESIS_SOURCES:
        return SourceItem(path, "human_full_text", "derived synthesis/report used as readable source", title, authority, family, size, ext, first_heading=first_heading)
    if ext in BINARY_EXTENSIONS or not record.get("is_text", True):
        return SourceItem(path, "binary_or_non_text", "binary or non-text source represented by metadata only", title, authority, family, size, ext, first_heading=first_heading)
    if ext in MACHINE_EXTENSIONS:
        return SourceItem(path, "machine_index_only", "machine-readable structured file", title, authority, family, size, ext, first_heading=first_heading)
    if ext not in TEXT_EXTENSIONS and ext != ".md":
        return SourceItem(path, "machine_index_only", "non-prose extension", title, authority, family, size, ext, first_heading=first_heading)
    if is_machine_named(path):
        return SourceItem(path, "reference_only", "register, manifest, matrix, validation, queue, or packet-like file", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith("docs/archive/conversations/_reader/by_chat/"):
        return SourceItem(path, "human_full_text", "conversation reader page", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith("docs/archive/conversations/") and any(pattern in lowered for pattern in READER_NAME_PATTERNS):
        disposition = "human_full_text" if size < 120_000 else "human_excerpt"
        return SourceItem(path, disposition, "reader-oriented conversation artifact", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith("docs/archive/conversations/"):
        return SourceItem(path, "reference_only", "conversation source package material, not main-book prose", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith("docs/archive/"):
        return SourceItem(path, "human_summarize", "archive prose summarized to avoid treating history as current truth", title, authority, family, size, ext, first_heading=first_heading)
    if path.startswith(("docs/architecture/", "docs/development/", "docs/testing/", "docs/runtime/", "docs/game/", "docs/apps/", "docs/workbench/", "docs/content/", "docs/modding/", "docs/domains/", "docs/release/", "docs/planning/", "docs/repo/", "docs/governance/")):
        return SourceItem(path, "human_summarize", "current prose family summarized into synthesized chapters", title, authority, family, size, ext, first_heading=first_heading)
    if path.endswith(".md"):
        return SourceItem(path, "human_summarize", "Markdown prose summarized or referenced", title, authority, family, size, ext, first_heading=first_heading)
    return SourceItem(path, "reference_only", "not selected for main prose", title, authority, family, size, ext, first_heading=first_heading)


def manual_source_item(repo_root: Path, path: str, reason: str, disposition: str = "human_full_text") -> SourceItem:
    full = repo_root / path
    text = read_text(full, 20_000)
    heading = ""
    for line in text.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            break
    return SourceItem(
        path=path,
        disposition=disposition,
        reason=reason,
        title=title_from_path(path, heading),
        authority_class="current_repo_truth" if not path.startswith("docs/archive/") else "advisory_synthesis",
        family=path.split("/")[0],
        size=full.stat().st_size if full.exists() else 0,
        extension=full.suffix.lower(),
        source_kind="manual_required_source",
        first_heading=heading,
    )


def select_sources(repo_root: Path, records: List[dict]) -> List[SourceItem]:
    by_path = {record["path"]: record for record in records}
    items = [classify_record(record) for record in records]
    existing = {item.path for item in items}
    for path in HIGH_AUTHORITY_SOURCES:
        if path not in existing and (repo_root / path).exists():
            items.append(manual_source_item(repo_root, path, "required high-authority orientation source"))
    for path in SYNTHESIS_SOURCES:
        if path not in existing and (repo_root / path).exists():
            items.append(manual_source_item(repo_root, path, "required synthesis source"))
    items.sort(key=lambda item: item.path)
    return items


def disposition_counts(items: Iterable[SourceItem]) -> Counter:
    return Counter(item.disposition for item in items)


def source_tag(item: SourceItem) -> str:
    status = "advisory" if "archive" in item.path or "conversations" in item.path else "current"
    return f"`{status}` `{item.disposition}` `{item.authority_class}`"


def repo_link(path: str) -> str:
    prefix = "../../../../../"
    label = path.replace("\\", "/")
    return f"[`{label}`]({prefix}{label})"


def write_source_manifest(repo_root: Path, items: List[SourceItem]) -> None:
    counts = disposition_counts(items)
    rows = []
    for item in items:
        rows.append(
            textwrap.dedent(
                f"""\
                - path: "{item.path}"
                  disposition: "{item.disposition}"
                  title: "{item.title.replace('"', "'")}"
                  authority_class: "{item.authority_class}"
                  family: "{item.family}"
                  size: {item.size}
                  reason: "{item.reason.replace('"', "'")}"
                """
            ).rstrip()
        )
    manifest = f"""title: "{TITLE} Source Manifest"
version: {VERSION}
date: "{REVIEW_DATE}"
status: "DERIVED"
authority_class: "advisory_synthesis"
source_root: "docs/"
promotion_status: "not_promoted"
selection_counts:
{chr(10).join(f"  {key}: {counts[key]}" for key in sorted(counts))}
sources:
{chr(10).join(rows)}
"""
    write_text(repo_root / HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_MANIFEST.yml", manifest)


def write_selection_reports(repo_root: Path, items: List[SourceItem]) -> None:
    counts = disposition_counts(items)
    full_text = [item for item in items if item.disposition == "human_full_text"]
    summarized = [item for item in items if item.disposition == "human_summarize"]
    reference = [item for item in items if item.disposition == "reference_only"]
    machine = [item for item in items if item.disposition == "machine_index_only"]
    binary = [item for item in items if item.disposition == "binary_or_non_text"]
    excerpted = [item for item in items if item.disposition == "human_excerpt"]
    recursive = [item for item in items if item.disposition == "exclude_generated_recursive"]

    def path_list(source: Sequence[SourceItem], cap: Optional[int] = None) -> str:
        selected = source if cap is None else source[:cap]
        body = "\n".join(f"- `{item.path}` - {item.title} ({item.reason})" for item in selected)
        if cap is not None and len(source) > cap:
            body += f"\n- ... {len(source) - cap} more entries listed in `HUMAN_SOURCE_MANIFEST.yml`."
        return body or "- none"

    report = REPORT_STATUS_BLOCK + f"""
# Human Source Selection Report

This report records the reset from a rendered corpus dump to a prose-first source reader and synthesized book.

## Selection Summary

- Human-readable full-text documents: {len(full_text)}
- Human-readable summarized documents: {len(summarized)}
- Human-readable excerpted documents: {len(excerpted)}
- Reference-only documents: {len(reference)}
- Machine/index-only documents: {len(machine)}
- Binary/non-text documents: {len(binary)}
- Excluded generated-recursive documents: {len(recursive)}

## Selection Rule

The main book uses current authority and readable synthesis as source material, then explains the project in coherent prose. It does not print manifests, raw file lists, validation logs, hash lists, or long registers as chapter content.

## Most Important Full-Text Sources

{path_list(full_text[:80])}

## Summarized Source Families

Summarized material includes current architecture, development, planning, domain, archive, and historical docs that are useful for synthesis but would make the main book unreadable if pasted in sequence.

## Uncertain Classification Cases

Files with prose-like Markdown under archive roots are summarized rather than promoted. Files with manifest, register, matrix, packet, source-index, or validation naming are reference-only even if they are Markdown.
"""
    write_text(repo_root / HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_SELECTION_REPORT.md", report)

    excluded = REPORT_STATUS_BLOCK + f"""
# Excluded Machine-Readable Material

The following material is intentionally kept out of the main book. It remains represented in the source manifest and reference surfaces.

## Why This Material Is Excluded From The Main Book

- Raw machine-readable files are better queried or validated than printed.
- Manifests, hashes, and path indexes overwhelm the reading flow.
- Long promotion, contradiction, and validation registers belong in reference material.
- Binary outputs cannot be rendered as book prose.
- Generated recursive book outputs would cause self-publication loops.

## Machine/Index-Only Files

{path_list(machine, cap=500)}

## Reference-Only Files

{path_list(reference, cap=500)}

## Binary Or Non-Text Files

{path_list(binary, cap=300)}

## Excluded Generated-Recursive Files

{path_list(recursive, cap=300)}
"""
    write_text(repo_root / HUMAN_SOURCE_ROOT / "EXCLUDED_MACHINE_READABLE_MATERIAL.md", excluded)


def source_intro(item: SourceItem) -> str:
    return f"> [!SOURCE] {source_tag(item)} Source: `{item.path}`. Reason: {item.reason}.\n"


def first_paragraphs(text: str, max_paragraphs: int = 3, max_chars: int = 1800) -> str:
    metadata, body = compact_metadata(text)
    paragraphs: List[str] = []
    current: List[str] = []
    in_code = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            if len(paragraphs) >= max_paragraphs:
                break
            continue
        if stripped.startswith("#") or stripped.startswith("|"):
            continue
        if stripped.startswith(("- ", "* ")):
            stripped = stripped[2:].strip()
        current.append(stripped)
        if sum(len(p) for p in paragraphs) + len(" ".join(current)) > max_chars:
            break
    if current and len(paragraphs) < max_paragraphs:
        paragraphs.append(" ".join(current))
    text = "\n\n".join(paragraphs).strip()
    return text[:max_chars].rstrip() or "No prose excerpt was selected; see the source path."


def render_source_section(repo_root: Path, item: SourceItem) -> str:
    full = repo_root / item.path
    text = read_text(full)
    title = item.title
    if not text:
        return f"## {title}\n\n{source_intro(item)}\nSource file could not be read during generation.\n"
    metadata, body = compact_metadata(text)
    if item.disposition == "human_full_text":
        return f"## {title}\n\n{source_intro(item)}\n{demote_headings(body, 2)}\n"
    if item.disposition == "human_excerpt":
        excerpt = body[:12_000].rstrip()
        return f"## {title}\n\n{source_intro(item)}\nThis source is excerpted because the full document is too large for the source reader.\n\n{demote_headings(excerpt, 2)}\n\n> [!VERIFY] See `{item.path}` for the complete original.\n"
    if item.disposition == "human_summarize":
        return f"## {title}\n\n{source_intro(item)}\n**Summary:** {first_paragraphs(text)}\n\nThe full document is summarized here and represented in the source index so the synthesized book can remain readable.\n"
    return f"## {title}\n\n{source_intro(item)}\nThis source is represented by metadata only in the human source reader.\n"


def write_source_reader(repo_root: Path, items: List[SourceItem]) -> None:
    selected = [item for item in items if item.disposition in {"human_full_text", "human_excerpt", "human_summarize"}]
    priority_order = {path: index for index, path in enumerate(HIGH_AUTHORITY_SOURCES + SYNTHESIS_SOURCES)}
    selected.sort(key=lambda item: (priority_order.get(item.path, 10_000), item.disposition != "human_full_text", item.path))
    chunks = [
        REPORT_STATUS_BLOCK,
        "# Human Source Compilation",
        "",
        "This source reader is not the final book. It collects the prose-oriented sources used for synthesis and keeps machine-readable material out of the reading flow.",
        "",
        "## Reading Order",
        "",
        "1. Current authority and orientation.",
        "2. Current project picture and conversation synthesis.",
        "3. Current architecture, development, and domain prose.",
        "4. Archive and conversation reader documents.",
        "5. Decisions, open questions, and promotion summaries.",
        "",
    ]
    for item in selected:
        chunks.append(render_source_section(repo_root, item))
    write_text(repo_root / HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_COMPILATION.md", "\n\n".join(chunks))

    rows = [
        "| Disposition | Source | Title | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for item in selected:
        rows.append(f"| `{item.disposition}` | `{item.path}` | {item.title} | {item.reason} |")
    write_text(repo_root / HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_INDEX.md", REPORT_STATUS_BLOCK + "\n# Human Source Index\n\n" + "\n".join(rows) + "\n")


def write_v0_failure_modes(repo_root: Path) -> None:
    v0 = repo_root / DOCS_CORPUS_ROOT / "_exports/Dominium_Docs_Corpus_Omnibus_v0.pdf"
    pages = "unknown"
    glyph_note = "not checked"
    if v0.exists() and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(v0)], repo_root, timeout=120)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            pages = match.group(1)
    if v0.exists() and shutil.which("pdftotext"):
        extract = repo_root / HUMAN_BOOK_ROOT / "qa/v0_extract.txt"
        extract.parent.mkdir(parents=True, exist_ok=True)
        code, _ = run_command(["pdftotext", str(v0), str(extract)], repo_root, timeout=600)
        if code == 0 and extract.exists():
            text = extract.read_text(encoding="utf-8", errors="replace")
            glyph_note = "broken/control glyphs detected" if styled.has_bad_glyphs(text) or "\ufffd" in text else "no control glyphs detected by smoke check"
    report = REPORT_STATUS_BLOCK + f"""
# V0 Failure Modes

This file records why the human-readable book reset exists. The v0 Omnibus remains useful as a coverage artifact, but it is not a readable project book.

## Inspected Artifact

- Path: `docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_v0.pdf`
- Page count: {pages}
- Text extraction/glyph smoke check: {glyph_note}

## Failure Modes To Avoid

- Raw `Source: docs/...` headings dominate the table of contents.
- Repeated full metadata/status blocks interrupt the reading flow.
- Dense machine tables appear in the main body.
- Long filesystem/path indexes masquerade as chapters.
- Extracted text may show broken glyphs or control characters.
- Pages can be visually sparse and dense at the same time: large whitespace around cramped machine tables.
- The old book has weak human narrative.
- The old book does not clearly separate book content from reference material.

## Acceptance Rule For This Reset

The main human-readable book must be a synthesis. It may cite source paths and use compact source trails, but it must not repeat the v0 pattern of rendering manifests, path lists, and machine registers as chapter content.
"""
    write_text(repo_root / HUMAN_BOOK_ROOT / "qa/V0_FAILURE_MODES.md", report)


def chapter(title: str, number: int, focus: str, current: str, archive: str, unresolved: str, sources: Sequence[str]) -> str:
    source_links = "; ".join(repo_link(path) for path in sources)
    return f"""## {number}. {title}

{focus}

**Current repo-backed picture.** {current}

**Historical and advisory context.** {archive}

**What remains unresolved.** {unresolved}

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

Source trail: {source_links}
"""


def build_main_book(repo_root: Path, items: List[SourceItem]) -> Tuple[str, Dict[str, List[str]]]:
    chapter_sources: Dict[str, List[str]] = {}
    chapters: List[str] = []

    front = f"""# {TITLE}

{BOOK_NOTICE}

> [!AUTHORITY] This book is **DERIVED** and advisory. It is a human-readable synthesis of current docs, archive context, and conversation evidence. It is not canon, not a contract, not schema law, not release authority, and not queue state.

## How To Read This Book

Start with Part I if you need the project in one sitting. Use Parts II through IV when you need architecture, simulation, tooling, and archive context. Use Part V to plan review work. Source trails at the end of each chapter point to the documents that support the synthesis.

## What This Book Is

This is a readable project book. It explains the project in coherent prose, draws current repo truth from the strongest authority surfaces, and uses archive and conversation material as historical evidence.

## What This Book Is Not

This book does not promote archive claims. It does not apply promotion candidates. It does not open blocked Workbench UI, renderer, gameplay, provider runtime, package runtime, native GUI, or release publication work. It does not resolve contradictions by convenience.

## Source Hierarchy

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Scope-specific current planning, schema, contract, release, policy, and queue artifacts
5. Operational registries, projections, mirrors, manifests, and generated evidence
6. Archive material and conversation-derived synthesis

## Reading Paths

- **Fast orientation:** chapters 1, 3, 4, 16, and 20.
- **Architecture review:** chapters 5 through 9.
- **Simulation/world review:** chapters 10 through 12.
- **Tooling and governance review:** chapters 13 through 15.
- **Decision/promotion review:** chapters 17 through 20.

## Status Labels

- **Current repo truth:** supported by current canon, glossary, AGENTS, contracts, queue, or live docs.
- **Archive/historical:** useful for provenance but not current authority.
- **Conversation advisory:** design intent from archived conversations, not promoted truth.
- **Blocked by queue:** related implementation scope remains closed.
- **Needs decision:** cannot be resolved by generated synthesis.
"""
    chapters.append(front)

    def add(part: str) -> None:
        chapters.append(f"# {part}\n")

    add("Part I - The Project In One Sitting")
    data = [
        (
            "What Dominium Is",
            "Dominium is best understood as a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate. The project is not just a game executable; it is a set of lawful simulation, validation, content, evidence, and product surfaces that have to agree about truth.",
            "The README identifies Dominium as the official game/product/domain layer on top of Domino. The canon and glossary provide binding meaning, while AGENTS defines how repo work must respect that authority. The current queue keeps broad implementation work constrained.",
            "The archive and conversations expand the picture into a long-horizon product ecosystem: Workbench, setup/launcher, content packs, portability, release identity, provider boundaries, and repo-governed assistant workflows. Those materials explain intent but do not override current repo truth.",
            "The exact product boundary between long-term vision and current allowed implementation remains queue-gated. Future work must distinguish 'what the project intends' from 'what the current queue permits'.",
            ["README.md", "docs/canon/constitution_v1.md", "docs/canon/glossary_v1.md", "AGENTS.md", "docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md"],
        ),
        (
            "Why This Project Exists",
            "The recurring project ambition is to make invention, production, logistics, economics, settlement, trust, communication, and institutional power emerge from lawful simulation rather than from one-off scripts or renderer-owned state.",
            "Current docs emphasize deterministic execution, process-only mutation, explicit refusal, pack-driven integration, and validation evidence. These are not aesthetic preferences; they are the controls that keep a large simulation explainable and replayable.",
            "Conversation material repeatedly pushes the same ambition outward: world scale, tooling, release discipline, long-term portability, and operator interfaces that make the system inspectable. The archive is valuable because it preserves why those themes mattered.",
            "The project still needs adjudication on which historical design intents become current docs, which remain history, and which are blocked until later queue phases.",
            ["README.md", "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md", "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md"],
        ),
        (
            "The Core Mental Model",
            "The clearest mental model is the command/result spine: intent becomes command, capability/refusal law checks it, a deterministic service or process produces a result, diagnostics and evidence make it inspectable, and product shells project the outcome.",
            "Current repo truth separates authoritative truth, perceived/observed views, and rendering. UI and rendering are presentation. Authoritative mutation happens only through lawful deterministic process execution.",
            "Archived conversations apply the same model to Workbench, renderer, setup, provider, and content discussions. They often differ in vocabulary, but the direction is consistent: products should project truth, not invent hidden state.",
            "Some old conversations imply future UI/editor powers that are not currently open. Those should be read as design intent and decision backlog, not implementation authorization.",
            ["README.md", "AGENTS.md", "docs/architecture/INVARIANTS.md", "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md"],
        ),
        (
            "What Is Current Repo Truth Vs Historical Context",
            "The most important reading rule is authority ordering. Repo artifacts outrank chat memory. Canon and glossary outrank lower-level prose. Current queue state controls what work is allowed now.",
            "AGENTS and the planning authority docs make this explicit. Generated outputs are evidence unless promoted by a stronger source. Archive and conversation material can orient review, but it cannot silently become doctrine.",
            "The docs corpus and conversation corpus are useful precisely because they preserve history without contaminating current authority. They create review queues, contradiction maps, and source trails.",
            "The remaining work is human adjudication: decide what to preserve as history, what to promote through narrow docs tasks, what conflicts with authority, and what needs future queue opening.",
            ["AGENTS.md", "docs/planning/AUTHORITY_ORDER.md", "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md", "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md"],
        ),
    ]
    for idx, entry in enumerate(data, start=1):
        chapters.append(chapter(entry[0], idx, entry[1], entry[2], entry[3], entry[4], entry[5]))
        chapter_sources[entry[0]] = list(entry[5])

    add("Part II - Current Architecture")
    data = [
        (
            "The System Stack",
            "The project stack separates Domino substrate, Dominium domain/product meaning, runtime/product shells, Workbench/operator surfaces, contracts/schema law, content packs, and documentation/governance.",
            "Current sources keep these roles distinct. The engine substrate owns deterministic mechanics; the game/domain layer owns official interpretation; apps compose products; contracts and schema define compatibility surfaces; docs and queue state govern allowed work.",
            "Conversation archives reinforce this layered picture but sometimes discuss future experiences as if they already exist. The book keeps those statements advisory.",
            "The current stack map needs future promotion only where current docs are thin, not where archive language merely repeats unsupported future ambition.",
            ["README.md", "docs/architecture/CANONICAL_SYSTEM_MAP.md", "docs/architecture/CONTRACTS_INDEX.md", "docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md"],
        ),
        (
            "Authority, Law, Capability, And Refusal",
            "Authority in Dominium is not convenience power. Authority permits or frames attempts; law decides whether an attempt is accepted, refused, transformed, or degraded in a deterministic and auditable way.",
            "AGENTS inherits the constitutional floor: process-only mutation, explicit refusal, no silent migrations, no hidden fallback magic, profiles over mode flags, and pack-driven integration. These rules protect replayability and semantic ownership.",
            "The archive adds many examples of why this matters: Workbench must not become a hidden truth owner, providers must not silently substitute incompatible behavior, and generated assistant outputs must not become doctrine by accident.",
            "Future promotion needs careful language around capability, refusal, and operator tools so that convenience workflows do not collapse authority boundaries.",
            ["AGENTS.md", "docs/canon/constitution_v1.md", "docs/canon/glossary_v1.md", "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md"],
        ),
        (
            "Determinism, Replay, Provenance, And Validation",
            "Determinism is the project's engineering spine. Identical canonical inputs should produce identical authoritative outputs, and evidence must make that fact reviewable.",
            "Current governance requires named RNG streams, deterministic ordering, deterministic reductions, replay-hash equivalence where applicable, and validation before success is claimed. Validation reports are evidence, not replacement authority.",
            "Conversation material extends this concern into long-term portability, world scale, release trust, and tool-assisted inspection. It treats evidence as a first-class product surface.",
            "Full validation depth and release/trust proof remain visible debt outside narrow docs publication tasks. Generated books should report validation honestly and avoid implying runtime progress.",
            ["README.md", "AGENTS.md", "docs/architecture/INVARIANTS.md", "docs/repo/FOUNDATION_LOCK.md"],
        ),
        (
            "Content, Packs, Modding, And Compatibility",
            "Content and optional capability are meant to be declared, validated, and integrated through packs, registries, contracts, and compatibility law rather than hardcoded hidden branches.",
            "Current doctrine requires explicit refusal or degradation when packs are missing. Contract and schema identity must be respected, and silent compatibility reinterpretation is forbidden.",
            "The archive contains a wide design space around providers, content packs, modding, authored data, and future runtime packaging. That material is useful but queue-sensitive.",
            "Provider runtime and package runtime remain blocked by current queue. Any promotion touching those areas should stay docs-only until the queue opens implementation scope.",
            ["AGENTS.md", "README.md", "docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md", "docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md"],
        ),
        (
            "Runtime, Product Shells, UI, Renderer, And Platform",
            "Product shells should project command/result/refusal/diagnostic/evidence truth. Rendering is presentation. UI is an operator or player surface. Neither should mutate authoritative truth directly.",
            "Current queue state blocks broad Workbench UI, renderer implementation, native GUI, gameplay, provider runtime, package runtime, runtime module loading, and release publication. That queue fact is part of current truth.",
            "Archived conversations are rich with renderer, platform, Workbench, setup, and product-shell ideas. They are valuable as future design backlog, but they cannot authorize implementation now.",
            "The next safe work in this area is review, clarification, and narrow docs-only promotion candidate preparation, not broad feature execution.",
            ["README.md", ".aide/queue/current.toml", "docs/repo/FOUNDATION_LOCK.md", "docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md"],
        ),
    ]
    for idx, entry in enumerate(data, start=5):
        chapters.append(chapter(entry[0], idx, entry[1], entry[2], entry[3], entry[4], entry[5]))
        chapter_sources[entry[0]] = list(entry[5])

    add("Part III - Simulation And World Model")
    data = [
        (
            "Reality, Existence, Space, Time, And Scale",
            "The long-horizon world model is ambitious: existence, spatial refinement, visitability, timekeeping, chronology, scale, and simulation domains recur across the docs and conversations.",
            "Current authority supports the separation of truth, perception, and render, plus deterministic process execution. It does not automatically promote every archived world-scale concept into current implementation scope.",
            "Conversation synthesis adds the richest picture: worlds, planets, celestial systems, universe explorer ideas, real-world defaults, macro/micro transitions, and 2038 resilience concerns.",
            "Each domain claim needs review against current contracts, code, and queue state before becoming current docs. The strongest near-term value is vocabulary and roadmap clarification.",
            ["docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md", "docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md", "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md"],
        ),
        (
            "Civilization, Economy, Logistics, Institutions, And Signals",
            "Dominium's product identity repeatedly points toward systems where production, logistics, economics, settlement, trust, communication, institutions, and power emerge from lawful simulation.",
            "The README directly names invention, production, logistics, economics, settlement, trust, communication, and institutional power. That makes these themes current identity, even where detailed gameplay remains blocked.",
            "The archive expands these themes into civilization simulation, infrastructure, economy, governance, signals, and long-term world dynamics. Those are design signals rather than permission to implement gameplay.",
            "The unresolved question is sequencing: which social and economic concepts need canon vocabulary, which need architecture docs, and which must wait for gameplay scope to open.",
            ["README.md", "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md", "docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md"],
        ),
        (
            "Worldgen, Astronomy, Planetary Systems, And Domains",
            "World generation and planetary/celestial systems appear as recurring domain ambitions. The material matters because scale and chronology affect determinism, storage, rendering, and simulation law.",
            "Current repo truth requires deterministic ordering, explicit constraints, and clear contract boundaries. A worldgen idea is not current authority unless supported by current docs or later promotion.",
            "Conversation material includes chronology, celestial alignment, universe-scale thinking, planetary systems, and domain-specific packs. It is a strong source of historical design intent.",
            "Future review should separate vocabulary, deterministic model requirements, data/pack boundaries, and implementation plans. Those are different promotion tracks.",
            ["docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md", "docs/archive/conversations/_synthesis/WHAT_NEEDS_DECISION_v0.md", "docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md"],
        ),
    ]
    for idx, entry in enumerate(data, start=10):
        chapters.append(chapter(entry[0], idx, entry[1], entry[2], entry[3], entry[4], entry[5]))
        chapter_sources[entry[0]] = list(entry[5])

    add("Part IV - Tools, Workbench, AIDE, Codex, And Governance")
    data = [
        (
            "Workbench As A Governed Operator Surface",
            "Workbench should be read as an operator, validation, evidence, inspection, and later editing surface. It is not an authority layer.",
            "The README says Workbench consumes the same contracts and services as other products. Current queue blocks broad Workbench UI, so even aligned Workbench ideas remain future-scoped.",
            "The conversation corpus strongly values Workbench because it makes a large deterministic system inspectable. That design intent is useful, but it must be reconciled with queue limits.",
            "Near-term Workbench work should remain narrow, validation-oriented, and contract-aware unless a later reviewed queue opens broad UI scope.",
            ["README.md", ".aide/queue/current.toml", "docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md"],
        ),
        (
            "AIDE And Codex As Repo Control-Plane Harnesses",
            "AIDE and Codex are useful because they can inventory, generate, validate, package, and patch bounded repo artifacts. They are dangerous if treated as semantic authority.",
            "AGENTS defines the role clearly: agents must consult doctrine, preserve authority ordering, avoid replacing repo truth with chat memory, and validate honestly. Generated outputs are evidence unless promoted by stronger authority.",
            "The archive shows AIDE/Codex as future control-plane and workflow helpers. That is compatible with current governance only when bounded by queue state, validation, and review gates.",
            "Future automation should improve reviewability rather than bypass review. This book itself is evidence and orientation, not authority.",
            ["AGENTS.md", "docs/planning/AUTHORITY_ORDER.md", "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md"],
        ),
        (
            "Documentation, Archive, And Conversation Corpus",
            "The docs corpus is now a navigable source map. The conversation corpus is a historical design-intent layer. The archive preserves context that would be unsafe to merge directly into canon.",
            "Current docs taxonomy and AGENTS both support the distinction: archive material may inform future work, but current repo artifacts outrank generated summaries and chat claims.",
            "The conversation pipeline created readers, wiki pages, audit reports, decision dockets, promotion queues, and synthesis books. Those are valuable review surfaces.",
            "The next step is selective adjudication, not bulk promotion. Every future doc patch should name source claims, target docs, authority support, non-goals, and validation.",
            ["docs/README.md", "AGENTS.md", "docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md", "docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md"],
        ),
    ]
    for idx, entry in enumerate(data, start=13):
        chapters.append(chapter(entry[0], idx, entry[1], entry[2], entry[3], entry[4], entry[5]))
        chapter_sources[entry[0]] = list(entry[5])

    add("Part V - What We Know, What We Do Not Know, And What Comes Next")
    data = [
        (
            "Current Confirmed Picture",
            "The strongest confirmed picture is layered and conservative: Dominium is the official simulation/product/domain layer on Domino; Domino is the deterministic substrate; truth mutation is process-only; products project command/result/evidence surfaces; archive material is advisory.",
            "This picture is supported by README, canon, glossary, AGENTS, current queue state, and docs-corpus reconciliation. It is stronger than any single archive conversation.",
            "Historical sources add breadth: world scale, Workbench aspirations, release identity, provider/content boundaries, setup, launcher, and long-term platform goals.",
            "The confirmed picture is not the same as a complete roadmap. Many details remain in decision, promotion, blocked-scope, or verification queues.",
            ["README.md", "docs/canon/constitution_v1.md", "docs/canon/glossary_v1.md", "AGENTS.md", "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md"],
        ),
        (
            "Major Open Decisions",
            "The decision backlog is now a review surface. It should be read as a set of human questions, future queue decisions, and repo-authority decisions rather than as accepted answers.",
            "Current reconciliation separates user decisions, future queue decisions, deferred items, blocked-scope decisions, and evidence gaps. That separation prevents old conversations from silently becoming live doctrine.",
            "The most important categories are architecture/boundaries, Workbench/AIDE/Codex/tooling, renderer/UI/platform, provider/content/packs, world/time/civilization simulation, release/setup/launcher, and documentation/canon/spec structure.",
            "Unresolved decisions should default to defer unless there is current authority support and a narrow task that can patch documentation without widening scope.",
            ["docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md", "docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md", "docs/archive/conversations/_decision/DECISION_DOCKET_v0.md"],
        ),
        (
            "Contradictions, Stale Material, And Archive Drift",
            "Contradictions are not defects in the book; they are review triggers. A mature corpus should show where old claims disagree with current authority, current queue state, or other archive material.",
            "Current audit reports identify stale claims, duplicate shadows, authority conflicts, and coverage gaps. The correct response is quarantine and review, not convenient synthesis.",
            "Conversation material is especially prone to drift because it was produced across many sessions and goals. The value of the audit layer is that it prevents drift from hiding inside polished prose.",
            "Future review should prioritize contradictions that touch canon, contracts, schema, queue scope, release meaning, or implementation authority.",
            ["docs/archive/docs_corpus/_audit/DOCS_CONTRADICTION_MATRIX_v0.md", "docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md", "docs/archive/conversations/_synthesis/CONTRADICTIONS_TO_RECONCILE_v0.md"],
        ),
        (
            "Promotion Candidates And Safe Next Steps",
            "Promotion candidates are leads, not instructions. A candidate becomes useful only when a later task names the exact source claim, target doc, authority compatibility, validation, and review disposition.",
            "Current promotion surfaces include docs-corpus candidates and conversation-derived candidates. Many are metadata/header hygiene rather than substantive doctrine. Some are blocked by queue or require user decision.",
            "The safest near-term promotions are narrow docs-only clarifications that do not alter canon, contracts, schema, implementation, release, or queue state. Anything broader needs explicit human review.",
            "The next practical step is to triage the promotion queue into hygiene, genuine clarification, archive-only preservation, blocked, noisy, and user-decision groups.",
            ["docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md", "docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md", "docs/archive/conversations/_promotion/PROMOTION_TRIAGE_v0.md"],
        ),
        (
            "Recommended Reading And Review Roadmap",
            "Use the HTML book for navigation and search. Use the PDF for sequential reading. Use the source reader when you need original prose. Use manifests and registers only when auditing.",
            "Start with the current authority packet, then the current project picture, then the conversation atlas, then the decision docket and promotion queue. Do not start with raw manifests.",
            "Review should proceed from comprehension to decision to promotion. Live-doc changes should remain narrow and traceable, with validation evidence and no silent authority changes.",
            "This book should be reviewed as a human artifact. The next iteration should incorporate reader feedback, improve topic indexing, and only then prepare a small docs-only promotion wave.",
            ["docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_INDEX.md", "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md", "docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md"],
        ),
    ]
    for idx, entry in enumerate(data, start=16):
        chapters.append(chapter(entry[0], idx, entry[1], entry[2], entry[3], entry[4], entry[5]))
        chapter_sources[entry[0]] = list(entry[5])

    appendices = build_book_appendices(items)
    return "\n\n".join(chapters + [appendices]), chapter_sources


def build_book_appendices(items: List[SourceItem]) -> str:
    counts = disposition_counts(items)
    full = [item for item in items if item.disposition == "human_full_text"]
    summarized = [item for item in items if item.disposition == "human_summarize"]
    machine = [item for item in items if item.disposition == "machine_index_only"]
    reference = [item for item in items if item.disposition == "reference_only"]

    def compact(items_in: Sequence[SourceItem], cap: int = 120) -> str:
        rows = []
        for item in items_in[:cap]:
            rows.append(f"- `{item.path}` - {item.title}")
        if len(items_in) > cap:
            rows.append(f"- ... {len(items_in) - cap} more entries in `HUMAN_SOURCE_MANIFEST.yml`.")
        return "\n".join(rows) or "- none"

    return f"""# Appendices

## Appendix A - Source Documents Used

Human-readable full-text documents: {counts['human_full_text']}.

{compact(full)}

## Appendix B - Documents Summarized But Not Printed

Summarized documents: {counts['human_summarize']}.

{compact(summarized)}

## Appendix C - Machine-Readable And Reference Material Excluded From The Main Book

Machine/index-only documents: {counts['machine_index_only']}. Reference-only documents: {counts['reference_only']}. These files remain represented in the source manifest and reference outputs.

{compact(machine + reference)}

## Appendix D - Decision Index

- Architecture and boundaries.
- Workbench, AIDE, Codex, and tooling.
- Renderer, UI, platform, and native GUI.
- Provider, content, packs, and compatibility.
- World, time, civilization, and simulation domains.
- Release, setup, launcher, and publication.
- Documentation, canon, spec structure, and archive promotion.

See `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` and `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`.

## Appendix E - Source Path Index

The full source path index is `docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_INDEX.md`. This appendix intentionally avoids reproducing thousands of paths in the main book.

## Appendix F - Glossary And Abbreviations

- **AIDE:** repo/control-plane harness and context/validation helper.
- **Archive:** historical/provenance docs that do not override current authority.
- **Canon:** binding constitutional project meaning.
- **Conversation advisory:** derived historical conversation evidence.
- **Domino:** deterministic reusable substrate.
- **Dominium:** official game/product/domain layer.
- **Process-only mutation:** authoritative truth changes only through lawful deterministic processes.
- **Queue:** current scope gate for allowed work.
"""


def write_book_sources(repo_root: Path, items: List[SourceItem]) -> Tuple[str, Dict[str, List[str]]]:
    book_md, chapter_sources = build_main_book(repo_root, items)
    write_text(repo_root / HUMAN_BOOK_ROOT / "Dominium_Human_Readable_Book_v1.md", book_md)
    chapters_dir = repo_root / HUMAN_BOOK_ROOT / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chunks = re.split(r"\n(?=## \d+\. )", book_md)
    front = chunks[0]
    write_text(chapters_dir / "00_front_matter.md", front)
    for index, chunk in enumerate(chunks[1:], start=1):
        title_match = re.match(r"## \d+\. ([^\n]+)", chunk)
        title = title_from_path(title_match.group(1) if title_match else f"chapter_{index:02d}")
        filename = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        write_text(chapters_dir / f"{index:02d}_{filename}.md", chunk)
    write_book_indexes(repo_root, items, chapter_sources)
    write_book_manifest(repo_root, items)
    write_text(
        repo_root / HUMAN_BOOK_ROOT / "README.md",
        REPORT_STATUS_BLOCK
        + f"\n# Human-Readable Dominium Book\n\nThis directory contains the source for `{TITLE}`. It is DERIVED, advisory, and publication-only.\n",
    )
    return book_md, chapter_sources


def write_book_indexes(repo_root: Path, items: List[SourceItem], chapter_sources: Dict[str, List[str]]) -> None:
    index_dir = repo_root / HUMAN_BOOK_ROOT / "indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    topics = [
        "authority",
        "archive",
        "canon",
        "capability",
        "contracts",
        "determinism",
        "Dominium",
        "Domino",
        "evidence",
        "packs",
        "process-only mutation",
        "queue",
        "refusal",
        "renderer",
        "simulation",
        "Workbench",
    ]
    write_text(repo_root / index_dir / "TOPIC_INDEX.md", REPORT_STATUS_BLOCK + "\n# Topic Index\n\n" + "\n".join(f"- **{topic}**" for topic in topics) + "\n")
    source_rows = []
    for chapter_title, paths in chapter_sources.items():
        for path in paths:
            source_rows.append(f"- **{chapter_title}:** `{path}`")
    write_text(repo_root / index_dir / "SOURCE_TRAIL_INDEX.md", REPORT_STATUS_BLOCK + "\n# Source Trail Index\n\n" + "\n".join(source_rows) + "\n")
    write_text(
        repo_root / index_dir / "DECISION_INDEX.md",
        REPORT_STATUS_BLOCK
        + "\n# Decision Index\n\n- User decisions\n- Future queue decisions\n- Deferred decisions\n- Docs-only promotion candidates\n- Blocked-scope review items\n\nSee `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md`.\n",
    )
    counts = disposition_counts(items)
    write_text(
        repo_root / index_dir / "BOOK_INDEX.md",
        REPORT_STATUS_BLOCK
        + f"\n# Book Index\n\n- Full-text sources: {counts['human_full_text']}\n- Summarized sources: {counts['human_summarize']}\n- Excerpted sources: {counts['human_excerpt']}\n- Reference-only sources: {counts['reference_only']}\n- Machine/index-only sources: {counts['machine_index_only']}\n- Binary/non-text sources: {counts['binary_or_non_text']}\n",
    )


def write_book_manifest(repo_root: Path, items: List[SourceItem]) -> None:
    counts = disposition_counts(items)
    manifest = f"""title: "{TITLE}"
subtitle: "{SUBTITLE}"
version: {VERSION}
date: "{REVIEW_DATE}"
status: "DERIVED"
authority_class: "advisory_synthesis"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
promotion_status: "not_promoted"
outputs:
  - "docs/archive/docs_corpus/_exports/{MAIN_PDF}"
  - "docs/archive/docs_corpus/_exports/{MAIN_HTML_DIR}/index.html"
  - "docs/archive/docs_corpus/_exports/{MAIN_DOCX}"
  - "docs/archive/docs_corpus/_exports/{SOURCE_READER_PDF}"
selection_counts:
{chr(10).join(f"  {key}: {counts[key]}" for key in sorted(counts))}
protected_paths:
{chr(10).join(f"  - {prefix}" for prefix in PROTECTED_PREFIXES)}
validation_commands:
  - py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root .
  - py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root .
  - py -3 tools/conversations/validate_conversation_outputs.py --repo-root .
  - py -3 -m unittest discover tests/tools/docs_corpus
  - git diff --check
"""
    write_text(repo_root / HUMAN_BOOK_ROOT / "HUMAN_BOOK_MANIFEST.yml", manifest)


def html_document(title: str, body: str, css: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
  <nav class="top"><a href="#top">Top</a><a href="#contents">Contents</a><a href="#appendices">Appendices</a></nav>
  <main id="top">
    {body}
  </main>
</body>
</html>
"""


def human_css() -> str:
    return """
:root { --ink:#18202a; --muted:#5d6877; --line:#d8dee8; --soft:#f5f7fb; --accent:#1f5f99; --warn:#865700; }
* { box-sizing: border-box; }
body { margin:0; color:var(--ink); font: 17px/1.62 system-ui, -apple-system, Segoe UI, sans-serif; background:#fff; }
main { max-width: 880px; margin: 0 auto; padding: 3.5rem 1.25rem 6rem; }
.top { position: sticky; top:0; display:flex; gap:1rem; padding:.7rem 1rem; background:rgba(255,255,255,.94); border-bottom:1px solid var(--line); backdrop-filter: blur(8px); z-index:5; }
.top a { color:var(--accent); font-weight:700; text-decoration: underline; text-underline-offset: .18em; }
h1 { font-size: clamp(2.2rem, 5vw, 4.4rem); line-height:1.05; margin:1rem 0 1.25rem; }
h2 { margin-top:3rem; padding-top:1rem; border-top:3px solid var(--line); font-size:1.7rem; line-height:1.22; }
h3 { margin-top:2rem; color:#26384e; }
p { margin:.85rem 0; }
blockquote { margin:1.2rem 0; padding:1rem 1.1rem; border-left:5px solid var(--accent); background:var(--soft); border-radius:.35rem; }
code { background:#f0f3f7; padding:.08rem .25rem; border-radius:.25rem; font-size:.92em; }
pre { overflow:auto; padding:1rem; background:#101820; color:#f5f7fb; border-radius:.5rem; }
a { color:var(--accent); text-decoration: underline; text-underline-offset:.18em; }
table { border-collapse: collapse; width:100%; margin:1rem 0; font-size:.94rem; }
th, td { border:1px solid var(--line); padding:.45rem .55rem; vertical-align:top; }
th { background:var(--soft); }
ul, ol { padding-left:1.5rem; }
@media (max-width: 700px) { body { font-size:16px; } main { padding:2rem 1rem 5rem; } table { display:block; overflow-x:auto; } }
"""


def write_html_output(repo_root: Path, markdown: str, dirname: str, title: str) -> Path:
    html_dir = repo_root / EXPORTS_ROOT / dirname
    html_dir.mkdir(parents=True, exist_ok=True)
    body = styled.markdown_to_html(markdown)
    doc = html_document(title, body, human_css())
    path = html_dir / "index.html"
    write_text(path, doc)
    return path


def render_docx(repo_root: Path, markdown_text: str, target_name: str) -> Path:
    target = repo_root / EXPORTS_ROOT / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("> [!"):
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped.startswith("|"):
            stripped = " ".join(cell.strip() for cell in stripped.strip("|").split("|"))
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)
        stripped = re.sub(r"\*\*([^*]+)\*\*", r"\1", stripped)
        stripped = re.sub(r"\*([^*]+)\*", r"\1", stripped)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        paragraphs.append(stripped[:3000])
    body = "".join(f"<w:p><w:r><w:t>{xml_escape(p)}</w:t></w:r></w:p>" for p in paragraphs)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr/></w:body></w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
    return target


def pdf_output_name(kind: str) -> str:
    return {"main": MAIN_PDF, "source_reader": SOURCE_READER_PDF}[kind]


def render_pdf(repo_root: Path, markdown: str, kind: str, title: str, subtitle: str, profile: str, timeout: int) -> PdfInfo:
    build_dir = repo_root / HUMAN_BOOK_ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    target = repo_root / EXPORTS_ROOT / pdf_output_name(kind)
    renderer = styled.select_engine()
    if not renderer:
        return PdfInfo(path=target, created=False, renderer="none", caveat="No LaTeX renderer available")
    tex_path = build_dir / f"{kind}.tex"
    pdf_path = build_dir / f"{kind}.pdf"
    for old in build_dir.glob(f"{kind}.*"):
        old.unlink(missing_ok=True)
    body = styled.markdown_to_latex(markdown, reference=profile != "reader")
    write_text(tex_path, styled.latex_document(title, subtitle, body, renderer, profile))
    command = [renderer, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)]
    last_output = ""
    ok = True
    for _ in range(2):
        code, output = run_command(command, repo_root, timeout=timeout)
        last_output = output
        if code != 0:
            ok = False
            break
    if not ok or not pdf_path.exists():
        return PdfInfo(path=target, created=False, renderer=renderer, caveat=last_output[-1800:])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf_path, target)
    return qa_pdf(repo_root, target, kind, renderer)


def qa_pdf(repo_root: Path, pdf_path: Path, stem: str, renderer: str) -> PdfInfo:
    qa_dir = repo_root / HUMAN_BOOK_ROOT / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    result = PdfInfo(path=pdf_path, created=pdf_path.exists(), renderer=renderer, size=pdf_path.stat().st_size if pdf_path.exists() else 0)
    if result.created and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=180)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            result.pages = int(match.group(1))
    if result.created and shutil.which("pdftotext"):
        extract = qa_dir / f"{stem}_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=600)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
    if result.created and shutil.which("pdftoppm") and result.pages:
        for page in sorted(set([1, 2, max(1, result.pages // 4), max(1, result.pages // 2), result.pages]))[:5]:
            prefix = qa_dir / f"{stem}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf_path), str(prefix)], repo_root, timeout=240)
            image = prefix.with_suffix(".png")
            if code == 0 and image.exists():
                result.qa_images.append(rel(image, repo_root))
    return result


def render_build_report(state: BuildState) -> str:
    counts = disposition_counts(state.sources)
    output_rows = []
    for key, info in state.outputs.items():
        output_rows.append((key, rel(info.path, state.repo_root), info.created, info.pages or "", info.size, info.renderer))
    return REPORT_STATUS_BLOCK + f"""
# Dominium Human-Readable Book Build Report

## Build

- Title: {TITLE}
- Version: {VERSION}
- Date: {REVIEW_DATE}
- Repository branch: `{state.branch}`
- Repository commit at generation time: `{state.commit}`
- Renderer: {state.renderer or styled.select_engine() or 'none'}
- Source roots: `docs/`, `docs/archive/conversations/`

## Selection Method

The builder selected prose-first sources for full text, summary, or excerpt use. Machine-readable files, registers, validation logs, manifests, hash lists, and path inventories were kept out of the main book and documented as reference material.

## Source Counts

- Human-readable full-text documents: {counts['human_full_text']}
- Human-readable summarized documents: {counts['human_summarize']}
- Human-readable excerpted documents: {counts['human_excerpt']}
- Reference-only documents: {counts['reference_only']}
- Machine/index-only documents: {counts['machine_index_only']}
- Binary/non-text documents: {counts['binary_or_non_text']}
- Excluded generated-recursive documents: {counts['exclude_generated_recursive']}

## Outputs

{styled.v0.md_table(["Output", "Path", "Created", "Pages", "Size Bytes", "Renderer"], output_rows)}

## Caveats

- HTML links are the primary clickable navigation surface.
- PDF rendering uses the locally viable LaTeX engine and validates text extraction/glyph quality.
- The main book is synthesized prose; the source reader carries selected original human-readable source material.
"""


def render_validation_report(state: BuildState, pending: bool = False) -> str:
    if pending:
        return REPORT_STATUS_BLOCK + "\n# Dominium Human-Readable Book Validation Report\n\nValidation pending.\n"
    result = "PASS" if not state.errors and not state.warnings else "PASS_WITH_WARNINGS" if not state.errors else "FAIL"
    command_rows = [(item["command"], item["result"], item["code"]) for item in state.command_results]
    pdf_rows = []
    for key, info in state.outputs.items():
        if info.path.suffix.lower() == ".pdf":
            pdf_rows.append((key, rel(info.path, state.repo_root), info.created, info.pages or "", info.text_extraction, info.glyph_check, "; ".join(info.qa_images)))
    return REPORT_STATUS_BLOCK + f"""
# Dominium Human-Readable Book Validation Report

## Status

- Result: {result}

## Command Results

{styled.v0.md_table(["Command", "Result", "Code"], command_rows)}

## PDF QA

{styled.v0.md_table(["Output", "Path", "Created", "Pages", "Text Extraction", "Glyph Check", "QA Images"], pdf_rows)}

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


def protected_changes(repo_root: Path) -> List[str]:
    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
    names = output.splitlines() if code == 0 else []
    code_cached, output_cached = run_command(["git", "diff", "--cached", "--name-only"], repo_root, timeout=120)
    if code_cached == 0:
        names.extend(output_cached.splitlines())
    return sorted({name for name in names if any(name == prefix.rstrip("/") or name.startswith(prefix) for prefix in PROTECTED_PREFIXES)})


def validate_outputs(state: BuildState) -> None:
    commands = [
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'sources:' in text; print('human source manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_human_book/HUMAN_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'outputs:' in text; print('human book manifest ok')"],
        ["py", "-3", "tools/docs_corpus/validate_human_readable_book.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["git", "diff", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    for cmd in commands:
        code, output = run_command(cmd, state.repo_root, timeout=1800)
        state.command_results.append({"command": " ".join(cmd), "code": code, "result": "PASS" if code == 0 else "FAIL"})
        if code != 0:
            state.errors.append(f"command failed: {' '.join(cmd)}\n{output[-1600:]}")
    protected = protected_changes(state.repo_root)
    if protected:
        state.errors.extend(f"protected path changed: {path}" for path in protected)


def create_state(repo_root: Path) -> BuildState:
    records = load_manifest(repo_root)
    sources = select_sources(repo_root, records)
    return BuildState(
        repo_root=repo_root,
        records=records,
        sources=sources,
        branch=git_branch(repo_root),
        commit=git_commit(repo_root),
        renderer=styled.select_engine(),
    )


def build_source_phase(state: BuildState) -> None:
    write_source_manifest(state.repo_root, state.sources)
    write_selection_reports(state.repo_root, state.sources)
    write_source_reader(state.repo_root, state.sources)
    write_v0_failure_modes(state.repo_root)


def build_book_phase(state: BuildState, pending_validation: bool = True) -> None:
    source_compilation = read_text(state.repo_root / HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_COMPILATION.md")
    book_md, _ = write_book_sources(state.repo_root, state.sources)
    main_html = write_html_output(state.repo_root, book_md, MAIN_HTML_DIR, TITLE)
    source_html = write_html_output(state.repo_root, source_compilation, SOURCE_READER_HTML_DIR, f"{TITLE} Source Reader")
    docx_path = render_docx(state.repo_root, book_md, MAIN_DOCX)
    state.outputs["main_pdf"] = render_pdf(state.repo_root, book_md, "main", TITLE, SUBTITLE, "reader", timeout=1500)
    state.outputs["source_reader_pdf"] = render_pdf(state.repo_root, source_compilation, "source_reader", f"{TITLE} Source Reader", "Curated Human-Readable Source Compilation", "reference", timeout=2400)
    state.outputs["main_html"] = PdfInfo(path=main_html, created=main_html.exists(), size=main_html.stat().st_size if main_html.exists() else 0, renderer="built_in_html")
    state.outputs["source_reader_html"] = PdfInfo(path=source_html, created=source_html.exists(), size=source_html.stat().st_size if source_html.exists() else 0, renderer="built_in_html")
    state.outputs["docx"] = PdfInfo(path=docx_path, created=docx_path.exists(), size=docx_path.stat().st_size if docx_path.exists() else 0, renderer="built_in_ooxml")
    renderers = [info.renderer for info in state.outputs.values() if info.renderer]
    if renderers:
        state.renderer = ",".join(dict.fromkeys(renderers))
    write_text(state.repo_root / EXPORTS_ROOT / BUILD_REPORT, render_build_report(state))
    write_text(state.repo_root / EXPORTS_ROOT / VALIDATION_REPORT, render_validation_report(state, pending=pending_validation))


def build(repo_root: Path, phase: str, run_validation: bool) -> int:
    state = create_state(repo_root)
    if phase in {"source", "all", "book"}:
        build_source_phase(state)
    if phase in {"book", "all"}:
        build_book_phase(state, pending_validation=not run_validation)
    if phase == "validate":
        # Rehydrate known output paths for validation reporting.
        for key, filename in {"main_pdf": MAIN_PDF, "source_reader_pdf": SOURCE_READER_PDF}.items():
            path = repo_root / EXPORTS_ROOT / filename
            state.outputs[key] = qa_pdf(repo_root, path, key, styled.select_engine() or "unknown")
        for key, path in {
            "main_html": repo_root / EXPORTS_ROOT / MAIN_HTML_DIR / "index.html",
            "docx": repo_root / EXPORTS_ROOT / MAIN_DOCX,
            "source_reader_html": repo_root / EXPORTS_ROOT / SOURCE_READER_HTML_DIR / "index.html",
        }.items():
            state.outputs[key] = PdfInfo(path=path, created=path.exists(), size=path.stat().st_size if path.exists() else 0, renderer="existing")
    if run_validation or phase == "validate":
        validate_outputs(state)
        write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, render_validation_report(state, pending=False))
    if state.errors:
        print(f"{TASK_ID} FAIL")
        return 1
    print(f"{TASK_ID} PASS")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--phase", choices=["source", "book", "all", "validate"], default="all")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args(argv)
    return build(Path(args.repo_root).resolve(), args.phase, run_validation=not args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
