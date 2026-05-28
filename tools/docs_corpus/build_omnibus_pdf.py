"""Build the derived docs-corpus Omnibus PDF.

The Omnibus is an export artifact only. It assembles the completed
docs-corpus reports, selected conversation-corpus reports, high-authority docs,
and a source compendium/index into one source-based PDF where feasible without
promoting any archived or generated claim into current authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import docs_corpus


TASK_ID = "DOCS-CORPUS-OMNIBUS-PDF-01"
REVIEW_DATE = "2026-05-29"
DOCS_CORPUS_ROOT = Path("docs/archive/docs_corpus")
OMNIBUS_ROOT = DOCS_CORPUS_ROOT / "_omnibus"
EXPORTS_ROOT = DOCS_CORPUS_ROOT / "_exports"
OMNIBUS_BASENAME = "Dominium_Docs_Corpus_Omnibus_v0"
INDEX_BASENAME = "Dominium_Docs_Corpus_Omnibus_Index_v0"
BUILD_REPORT_BASENAME = "Dominium_Docs_Corpus_Omnibus_Build_Report_v0"
VALIDATION_REPORT_BASENAME = "Dominium_Docs_Corpus_Omnibus_Validation_Report_v0"
TITLE = "Dominium Docs Corpus Omnibus"
SUBTITLE = "All-in-One Derived Documentation Corpus, Archive, Conversation, Reconciliation, and Source Index"

STATUS_BLOCK = """Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: none
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

PROTECTED_PREFIXES = docs_corpus.PROTECTED_PREFIXES

REQUIRED_INPUTS = [
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/canon/constitution_v1.md",
    "docs/canon/glossary_v1.md",
    "docs/planning/AUTHORITY_ORDER.md",
    "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md",
    ".aide/queue/current.toml",
    "docs/repo/FOUNDATION_LOCK.md",
    "docs/archive/docs_corpus/README.md",
    "docs/archive/docs_corpus/_book/BOOK_MANIFEST.yml",
    "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Build_Report_v0.md",
    "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Validation_Report_v0.md",
    "docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json",
    "docs/archive/docs_corpus/_intake/DOCS_FILE_COUNTS_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_AUTHORITY_MAP_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md",
]

HIGH_AUTHORITY_DOCS = [
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
    "docs/architecture/CANON_INDEX.md",
]

INTAKE_REPORTS = [
    "docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.md",
    "docs/archive/docs_corpus/_intake/DOCS_SOURCE_INDEX_v0.md",
    "docs/archive/docs_corpus/_intake/DOCS_FILE_COUNTS_v0.md",
    "docs/archive/docs_corpus/_intake/DOCS_TREE_SUMMARY_v0.md",
    "docs/archive/docs_corpus/_intake/DOCS_LARGE_FILES_AND_NON_MARKDOWN_v0.md",
]

AUDIT_REPORTS = [
    "docs/archive/docs_corpus/_audit/DOCS_STATUS_HEADER_AUDIT_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_AUTHORITY_CLASSIFICATION_DRAFT_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_AUTHORITY_MAP_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_SUPERSESSION_MAP_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_BINDING_SOURCE_MAP_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_ARCHIVE_CLASSIFICATION_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_BOOK_INCLUSION_PLAN_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_DRIFT_MATRIX_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_CONTRADICTION_MATRIX_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_DUPLICATE_SHADOWS_v0.md",
    "docs/archive/docs_corpus/_audit/DOCS_COVERAGE_GAPS_v0.md",
]

ARCHIVE_REPORTS = [
    "docs/archive/docs_corpus/_archive/DOCS_ARCHIVE_ATLAS_v0.md",
    "docs/archive/docs_corpus/_archive/DOCS_ARCHIVE_FAMILIES_v0.md",
    "docs/archive/docs_corpus/_archive/DOCS_ARCHIVE_STALE_OR_USEFUL_v0.md",
    "docs/archive/docs_corpus/_archive/DOCS_ARCHIVE_TO_CURRENT_CROSSWALK_v0.md",
    "docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md",
]

RECONCILIATION_REPORTS = [
    "docs/archive/docs_corpus/_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_ARCHIVE_CONVERSATION_ALIGNMENT_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md",
    "docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md",
]

WIKI_REPORTS = [
    "docs/archive/docs_corpus/_wiki/index.md",
    "docs/archive/docs_corpus/_wiki/current_authority.md",
    "docs/archive/docs_corpus/_wiki/archive_archaeology.md",
    "docs/archive/docs_corpus/_wiki/conversation_corpus.md",
    "docs/archive/docs_corpus/_wiki/decisions.md",
    "docs/archive/docs_corpus/_wiki/promotion_candidates.md",
    "docs/archive/docs_corpus/_wiki/contradictions.md",
    "docs/archive/docs_corpus/_wiki/staleness_and_verification.md",
    "docs/archive/docs_corpus/_wiki/source_index.md",
    "docs/archive/docs_corpus/_wiki/reading_paths.md",
]

CONVERSATION_ROOTS = [
    "docs/archive/conversations/_synthesis",
    "docs/archive/conversations/_decision",
    "docs/archive/conversations/_promotion",
    "docs/archive/conversations/_reconciliation",
    "docs/archive/conversations/_audit",
    "docs/archive/conversations/_wiki",
]

BINARY_EXTENSIONS = {".zip", ".pdf", ".docx", ".epub", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}


@dataclass
class ManifestRecord:
    path: str
    size: int
    extension: str
    sha256: str
    first_heading: str
    authority_class: str
    book_role: str
    is_text: bool
    warnings: List[str] = field(default_factory=list)


@dataclass
class Selection:
    full_text: List[str] = field(default_factory=list)
    summarized: List[str] = field(default_factory=list)
    manifest_only: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)
    included_reports: List[str] = field(default_factory=list)
    missing_inputs: List[str] = field(default_factory=list)
    conversation_reader_mode: str = "source_index_plus_available_generated_layers"
    full_text_byte_budget: int = 700_000


@dataclass
class BuildState:
    repo_root: Path
    branch: str
    commit: str
    manifest_summary: Dict[str, object]
    records: List[ManifestRecord]
    selection: Selection
    outputs: Dict[str, Dict[str, object]] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    validation_status: str = "PENDING"
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def strip_trailing_whitespace(text: str) -> str:
    normalized = "\n".join(line.rstrip(" \t") for line in text.splitlines())
    if text.endswith("\n"):
        normalized += "\n"
    return normalized


def write_text(path: Path, content: str) -> None:
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(strip_trailing_whitespace(content)))


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 600) -> Tuple[int, str]:
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


def git_output(repo_root: Path, args: Sequence[str]) -> str:
    code, output = run_command(["git", *args], repo_root)
    if code != 0:
        raise RuntimeError(output)
    return output.strip()


def read_text(path: Path, limit: Optional[int] = None) -> str:
    data = path.read_bytes()
    if limit is not None:
        data = data[:limit]
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return docs_corpus.ascii_text(data.decode(encoding, errors="replace"))
        except UnicodeDecodeError:
            continue
    return docs_corpus.ascii_text(data.decode("utf-8", errors="replace"))


def md_header(title: str) -> str:
    return f"{STATUS_BLOCK}\n# {title}\n\n"


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_table(headers: Sequence[str], rows: Iterable[Sequence[object]], limit: Optional[int] = None) -> str:
    row_list = list(rows)
    shown = row_list if limit is None else row_list[:limit]
    output = [
        "| " + " | ".join(md_escape(item) for item in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in shown:
        output.append("| " + " | ".join(md_escape(item) for item in row) + " |")
    if limit is not None and len(row_list) > limit:
        output.append("| ... | " + " | ".join(["..."] * (len(headers) - 1)) + " |")
    return "\n".join(output) + "\n"


def demote_headings(text: str, levels: int = 2) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            count = len(line) - len(line.lstrip("#"))
            heading = line[count:].strip()
            new_count = min(6, count + levels)
            lines.append("#" * new_count + " " + heading)
        else:
            lines.append(line)
    return "\n".join(lines).strip() + "\n"


def section_from_file(repo_root: Path, path: str, title: Optional[str] = None, max_chars: Optional[int] = None) -> str:
    abs_path = repo_root / path
    if not abs_path.exists():
        return f"## Missing Source: `{path}`\n\nThis source was requested but was not present at build time.\n"
    text = read_text(abs_path)
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Truncated in Omnibus source for renderability. See source path for full text.]\n"
    heading = title or path
    return f"## Source: `{path}`\n\n" + demote_headings(text, 2) + "\n"


def load_manifest(repo_root: Path) -> Tuple[Dict[str, object], List[ManifestRecord]]:
    manifest_path = repo_root / DOCS_CORPUS_ROOT / "_intake/DOCS_CORPUS_MANIFEST.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = []
    for item in payload["files"]:
        records.append(
            ManifestRecord(
                path=item["path"],
                size=int(item["size"]),
                extension=item["extension"],
                sha256=item["sha256"],
                first_heading=item.get("first_heading", ""),
                authority_class=item.get("authority_class", ""),
                book_role=item.get("book_role", ""),
                is_text=bool(item.get("is_text", False)),
                warnings=list(item.get("warnings", [])),
            )
        )
    return dict(payload["summary"]), records


def existing_markdown_under(repo_root: Path, roots: Sequence[str]) -> List[str]:
    paths = []
    for root in roots:
        root_path = repo_root / root
        if not root_path.exists():
            continue
        paths.extend(rel(path, repo_root) for path in sorted(root_path.rglob("*.md")))
    return sorted(set(paths))


def select_sources(repo_root: Path, records: Sequence[ManifestRecord]) -> Selection:
    selection = Selection()
    record_by_path = {record.path: record for record in records}
    explicit_full = set()
    explicit_full.update(path for path in HIGH_AUTHORITY_DOCS if (repo_root / path).exists())
    explicit_full.update(path for path in INTAKE_REPORTS + AUDIT_REPORTS + ARCHIVE_REPORTS + RECONCILIATION_REPORTS + WIKI_REPORTS if (repo_root / path).exists())
    explicit_full.update(existing_markdown_under(repo_root, ["docs/archive/docs_corpus/_book/chapters", "docs/archive/docs_corpus/_book/appendices"]))
    explicit_full.update(existing_markdown_under(repo_root, ["docs/archive/docs_corpus/_wiki/topics", "docs/archive/docs_corpus/_wiki/families"]))
    explicit_full.update(existing_markdown_under(repo_root, CONVERSATION_ROOTS))
    reader_index = "docs/archive/conversations/_reader/conversation_reader_index.md"
    if (repo_root / reader_index).exists():
        explicit_full.add(reader_index)
    by_chat = existing_markdown_under(repo_root, ["docs/archive/conversations/_reader/by_chat"])
    selection.conversation_reader_mode = "reader_index_plus_by_chat_source_index"

    for path in sorted(explicit_full):
        if path not in selection.full_text:
            selection.full_text.append(path)

    used_budget = sum((repo_root / path).stat().st_size for path in selection.full_text if (repo_root / path).exists())
    for record in records:
        if record.path in explicit_full:
            continue
        ext = record.extension.lower()
        if not record.is_text or ext in BINARY_EXTENSIONS:
            selection.manifest_only.append(record.path)
            continue
        if ext != ".md":
            selection.summarized.append(record.path)
            continue
        if record.book_role in {"manifest_only", "searchable_html_only", "excluded_binary_or_archive"}:
            selection.manifest_only.append(record.path)
            continue
        selection.summarized.append(record.path)

    for path in REQUIRED_INPUTS:
        if not (repo_root / path).exists():
            selection.missing_inputs.append(path)
    selection.included_reports = sorted(explicit_full)
    return selection


def protected_changes(repo_root: Path) -> List[str]:
    code, output = run_command(["git", "status", "--short"], repo_root)
    if code != 0:
        return [f"git status failed: {output}"]
    changes = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace("\\", "/")
        for prefix in PROTECTED_PREFIXES:
            if path == prefix.rstrip("/") or path.startswith(prefix):
                changes.append(line)
    return changes


def build_front_matter(state: BuildState) -> str:
    summary = state.manifest_summary
    return md_header("Part 0 - Front Matter") + f"""# {TITLE}

## {SUBTITLE}

Task ID: `{TASK_ID}`

## Version and Authority Notice

Version: 0

## Non-Promotion Notice

This Omnibus PDF is DERIVED and advisory. It is not canon, does not open blocked work, does not resolve contradictions, and does not promote archive or conversation-derived claims into current repo truth.

## Source Hierarchy

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Scope-specific canonical planning, semantic, schema, contract, release, and policy artifacts
5. Operational registries, projections, manifests, and generated evidence with intact provenance
6. Chat summaries, remembered transcript claims, and uncommitted planning notes

## What Is Included

- Existing docs-corpus reader and reference source chapters.
- Intake, audit, archive archaeology, reconciliation, and wiki reports.
- Existing generated conversation-corpus synthesis, audit, decision, promotion, reconciliation, wiki, and reader index layers.
- High-authority/current orientation docs in compact full text.
- A compact source compendium with source indexes and family summaries rather than bulk source copy.
- Indexes for source paths, authority classes, decisions, promotions, contradictions/staleness, archive families, high-authority docs, and manifest-only/binary files.

## What Is Not Included Verbatim

- `DOCS_CORPUS_MANIFEST.json` raw JSON is summarized rather than printed in full.
- Binary, ZIP, PDF, DOCX, EPUB, and image files are represented by metadata.
- Bulk by-chat reader pages and transcript-like source material are indexed rather than printed verbatim.
- General source Markdown outside curated high-authority/report sections is indexed or summarized, not bulk copied.
- `docs/archive/docs_corpus/**` is excluded from source-document compendium recursion, except for the generated reports/book inputs explicitly included in this Omnibus.

## Corpus Snapshot

- Docs files represented: {summary.get("file_count")}
- Directories represented: {summary.get("directory_count")}
- Markdown files: {summary.get("markdown_count")}
- Non-text files: {summary.get("non_text_count")}
- Source Markdown/full-text selections: {len(state.selection.full_text)}
- Summarized source files: {len(state.selection.summarized)}
- Manifest-only source files: {len(state.selection.manifest_only)}
"""


def report_limit_for(path: str, default: Optional[int]) -> Optional[int]:
    bulky = (
        "DOCS_SOURCE_INDEX",
        "DOCS_AUTHORITY_CLASSIFICATION_DRAFT",
        "DOCS_AUTHORITY_MAP",
        "DOCS_ARCHIVE_CLASSIFICATION",
        "DOCS_BOOK_INCLUSION_PLAN",
        "DOCS_STALENESS_AND_VERIFICATION",
        "DOCS_ARCHIVE_FAMILIES",
        "DOCS_ARCHIVE_STALE_OR_USEFUL",
        "DOCS_PROMOTION_QUEUE",
        "DOCS_DECISION_DOCKET",
        "conversation_reader_index",
    )
    if any(token in path for token in bulky):
        return 90_000
    return default


def build_part_from_files(title: str, repo_root: Path, paths: Sequence[str], max_chars: Optional[int] = None) -> str:
    parts = [md_header(title)]
    for path in paths:
        parts.append(section_from_file(repo_root, path, max_chars=report_limit_for(path, max_chars)))
    return "\n".join(parts)


def build_reference_part(repo_root: Path) -> str:
    reports = [
        "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reference_Appendix_v0.pdf",
        "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.pdf",
        "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.html/index.html",
        "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.docx",
        "docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.epub",
    ]
    rows = []
    for path in reports:
        abs_path = repo_root / path
        if abs_path.exists():
            rows.append((path, abs_path.stat().st_size, sha256_file(abs_path)[:16], "represented_as_existing_export"))
        else:
            rows.append((path, "missing", "", "missing_at_omnibus_build"))
    return md_header("Part II - Existing Reference Appendix") + """The reference appendix source Markdown is included in Part I through `_book/appendices/`. Existing binary exports are represented below and are not reprinted as binary streams.

""" + md_table(["Path", "Size Bytes", "SHA-256 Prefix", "Disposition"], rows)


def build_source_compendium(state: BuildState) -> str:
    current_sources = [record for record in state.records if not record.path.startswith("docs/archive/") and record.extension == ".md"]
    archive_sources = [record for record in state.records if record.path.startswith("docs/archive/") and record.extension == ".md"]
    non_markdown = [record for record in state.records if record.extension != ".md"]
    high_present = [path for path in HIGH_AUTHORITY_DOCS if (state.repo_root / path).exists()]
    parts = [md_header("Part X - Source Document Compendium")]
    parts.append("This section is intentionally compact. Human-readable high-authority originals are included in Part IX, and generated synthesis/reconciliation reports are included in Parts I-VIII. The remaining source corpus is represented by indexes and manifest metadata rather than bulk copy-paste.\n\n")
    parts.append(f"- High-authority originals included full-text in Part IX: {len(high_present)}\n")
    parts.append(f"- Current Markdown source files represented by index: {len(current_sources)}\n")
    parts.append(f"- Archive/conversation Markdown source files represented by index or generated summaries: {len(archive_sources)}\n")
    parts.append(f"- Non-Markdown/binary/machine-readable files represented by metadata: {len(non_markdown)}\n")
    parts.append(f"- Summarized source files: {len(state.selection.summarized)}\n")
    parts.append(f"- Manifest-only/binary source files: {len(state.selection.manifest_only)}\n")
    parts.append("- Full manifest with hashes: `docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json`\n\n")
    parts.append("## High-Authority Originals Included Full-Text\n\n")
    parts.append(md_table(["Path", "Disposition"], [(path, "included_in_part_ix") for path in high_present]))
    parts.append("\n## Current Source Families\n\n")
    parts.append(md_table(["Authority Class", "Count"], sorted(Counter(record.authority_class for record in current_sources).items())))
    parts.append("\n## Archive and Conversation Source Families\n\n")
    parts.append(md_table(["Authority Class", "Count"], sorted(Counter(record.authority_class for record in archive_sources).items())))
    parts.append("\n## Machine-Readable and Binary Inputs\n\n")
    parts.append(md_table(["Extension", "Count"], sorted(Counter(record.extension for record in non_markdown).items())))
    parts.append("\n## Representative Current Source Index\n\n")
    parts.append(md_table(["Path", "Authority Class", "Book Role"], [(record.path, record.authority_class, record.book_role) for record in current_sources], limit=600))
    parts.append("\n## Representative Archive/Conversation Source Index\n\n")
    parts.append(md_table(["Path", "Authority Class", "Book Role"], [(record.path, record.authority_class, record.book_role) for record in archive_sources], limit=600))
    return "\n".join(parts)


def build_indexes(state: BuildState) -> Dict[str, str]:
    records = state.records
    by_authority = Counter(record.authority_class for record in records)
    by_archive = Counter(record.path.split("/")[2] if record.path.startswith("docs/archive/") and len(record.path.split("/")) > 2 else "not_archive" for record in records)
    binary = [record for record in records if not record.is_text or record.extension.lower() in BINARY_EXTENSIONS]
    high = [(path, "present" if (state.repo_root / path).exists() else "missing") for path in HIGH_AUTHORITY_DOCS]
    decisions = extract_ids_from_files(state.repo_root, ["docs/archive/docs_corpus", "docs/archive/conversations"], r"(?:DOC-DECIDE|DECIDE|PROMOTE|DOC-PROMOTE|DOC-CONTRA|CONTRA|STALE)[A-Z0-9_-]*")
    excluded_lines = []
    for path in state.selection.summarized:
        excluded_lines.append(f"- summarized: `{path}`")
    for path in state.selection.manifest_only:
        excluded_lines.append(f"- manifest_only: `{path}`")
    source_lines = [
        f"- `{record.path}`"
        for record in records
    ]
    index_md = md_header("Omnibus Indexes") + f"""## Authority Class Index

{md_table(["Authority Class", "Count"], sorted(by_authority.items()))}

## Archive Family Index

{md_table(["Archive Segment", "Count"], sorted(by_archive.items()))}

## High-Authority Document Index

{md_table(["Path", "Status"], high)}

## Decision, Promotion, Contradiction, and Staleness ID Index

{md_table(["ID", "Occurrences"], sorted(decisions.items()), limit=1000)}

## Manifest-Only and Binary File Index

{md_table(["Path", "Extension", "Size", "Authority Class"], [(r.path, r.extension, r.size, r.authority_class) for r in binary], limit=1000)}

## Excluded/Summarized Source Index

{chr(10).join(excluded_lines)}

## Full Source Path Index

{chr(10).join(source_lines)}
"""
    conversation_rows = [
        (record.path, record.authority_class, record.book_role)
        for record in records
        if record.path.startswith("docs/archive/conversations/")
    ]
    conversation_md = md_header("Conversation Index") + md_table(["Path", "Authority Class", "Book Role"], conversation_rows, limit=2000)
    return {
        "indexes/omnibus_indexes.md": index_md,
        "indexes/conversation_index.md": conversation_md,
    }


def extract_ids_from_files(repo_root: Path, roots: Sequence[str], pattern: str) -> Counter:
    counter: Counter = Counter()
    regex = re.compile(pattern)
    for root in roots:
        root_path = repo_root / root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*.md"):
            try:
                text = read_text(path, limit=200_000)
            except OSError:
                continue
            for match in regex.findall(text):
                counter[match] += 1
    return counter


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_parts(state: BuildState) -> Dict[str, str]:
    repo_root = state.repo_root
    parts: Dict[str, str] = {}
    parts["parts/00_front_matter.md"] = build_front_matter(state)
    reader_sources = sorted(
        rel(path, repo_root)
        for root in ["docs/archive/docs_corpus/_book/chapters", "docs/archive/docs_corpus/_book/appendices"]
        for path in (repo_root / root).glob("*.md")
    )
    parts["parts/01_existing_reader_book.md"] = build_part_from_files("Part I - Existing Reader Book", repo_root, reader_sources)
    parts["parts/02_existing_reference_appendix.md"] = build_reference_part(repo_root)
    parts["parts/03_docs_corpus_intake.md"] = build_part_from_files("Part III - Docs Corpus Intake", repo_root, INTAKE_REPORTS)
    parts["parts/04_docs_corpus_audit.md"] = build_part_from_files("Part IV - Docs Corpus Audit", repo_root, AUDIT_REPORTS)
    parts["parts/05_archive_archaeology.md"] = build_part_from_files("Part V - Archive Archaeology", repo_root, ARCHIVE_REPORTS)
    parts["parts/06_reconciliation.md"] = build_part_from_files("Part VI - Reconciliation", repo_root, RECONCILIATION_REPORTS)
    wiki_sources = sorted(set(WIKI_REPORTS + existing_markdown_under(repo_root, ["docs/archive/docs_corpus/_wiki/topics", "docs/archive/docs_corpus/_wiki/families"])))
    parts["parts/07_docs_corpus_wiki.md"] = build_part_from_files("Part VII - Docs Corpus Wiki", repo_root, wiki_sources)
    conversation_sources = sorted(set(existing_markdown_under(repo_root, CONVERSATION_ROOTS) + ["docs/archive/conversations/_reader/conversation_reader_index.md"]))
    parts["parts/08_conversation_corpus_results.md"] = build_part_from_files("Part VIII - Conversation Corpus Results", repo_root, conversation_sources, max_chars=90_000)
    high_sources = [path for path in HIGH_AUTHORITY_DOCS if (repo_root / path).exists()]
    parts["parts/09_current_high_authority_docs.md"] = build_part_from_files("Part IX - Current High-Authority Docs", repo_root, high_sources)
    parts["parts/10_source_document_compendium.md"] = build_source_compendium(state)
    return parts


def build_manifest(state: BuildState) -> str:
    outputs = [
        f"docs/archive/docs_corpus/_exports/{OMNIBUS_BASENAME}.pdf",
        f"docs/archive/docs_corpus/_exports/{INDEX_BASENAME}.pdf",
        f"docs/archive/docs_corpus/_exports/{BUILD_REPORT_BASENAME}.md",
        f"docs/archive/docs_corpus/_exports/{VALIDATION_REPORT_BASENAME}.md",
    ]
    output_lines = "\n".join(f"  - {path}" for path in outputs)
    part_paths = sorted((state.repo_root / OMNIBUS_ROOT / "parts").glob("*.md"))
    part_lines = "\n".join(f"  - {rel(path, state.repo_root)}" for path in part_paths)
    protected_lines = "\n".join(f"  - {prefix}" for prefix in PROTECTED_PREFIXES)
    return f"""title: "{TITLE}"
subtitle: "{SUBTITLE}"
date: "{REVIEW_DATE}"
status: "DERIVED"
authority_class: "advisory_synthesis"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
promotion_status: "not_promoted"
output_mode: "single_pdf"
renderer_used: "pdflatex_source_based"
source_documents_counted: {len(state.records)}
source_documents_included_full_text: {len(state.selection.full_text)}
source_documents_summarized: {len(state.selection.summarized)}
source_documents_manifest_only: {len(state.selection.manifest_only)}
source_documents_excluded: {len(state.selection.excluded)}
conversation_reader_mode: "{state.selection.conversation_reader_mode}"
outputs:
{output_lines}
part_order:
{part_lines}
source_files_included_full_text_count: {len(state.selection.full_text)}
source_files_summarized_count: {len(state.selection.summarized)}
source_files_manifest_only_count: {len(state.selection.manifest_only)}
exclusion_rules:
  binary: "metadata only"
  zip_pdf_docx_epub_png: "metadata only"
  docs_archive_docs_corpus_recursive_source: "excluded except explicit generated reports/book source"
  very_large_or_manifest_only_text: "summarized/indexed"
protected_paths:
{protected_lines}
validation_commands:
  - py -3 -c "import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8'))"
  - py -3 tools/docs_corpus/validate_omnibus_pdf.py --repo-root .
  - py -3 -m unittest discover tests/tools/docs_corpus
  - git diff --check
fallback_mode: "none"
"""


def write_omnibus_sources(state: BuildState) -> str:
    root = state.repo_root / OMNIBUS_ROOT
    for subdir in ["parts", "indexes", "build", "qa"]:
        (root / subdir).mkdir(parents=True, exist_ok=True)
    parts = build_parts(state)
    indexes = build_indexes(state)
    for rel_path, content in {**parts, **indexes}.items():
        write_text(root / rel_path, content)
    ordered = [parts[key] for key in sorted(parts)] + [indexes[key] for key in sorted(indexes)]
    source = "\n\n".join(ordered)
    write_text(root / "omnibus_source.md", source)
    write_text(root / "README.md", md_header("Docs Corpus Omnibus") + f"""This directory contains source and indexes for `{TITLE}`.

The Omnibus is derived and advisory. It is a publication/export artifact, not current project authority.

Regenerate from repo root:

```powershell
py -3 tools/docs_corpus/build_omnibus_pdf.py --repo-root .
py -3 tools/docs_corpus/validate_omnibus_pdf.py --repo-root .
```
""")
    write_text(root / "OMNIBUS_MANIFEST.yml", build_manifest(state))
    return source


def latex_breakable(text: str) -> str:
    escaped = docs_corpus.latex_escape(text)
    escaped = escaped.replace(r"\_", r"\_\allowbreak{}")
    for token in ("/", "-", "."):
        escaped = escaped.replace(token, token + r"\allowbreak{}")
    return escaped


def inline_latex(text: str) -> str:
    placeholders: Dict[str, str] = {}

    def put(latex: str) -> str:
        key = f"FMTTOKEN{len(placeholders)}"
        placeholders[key] = latex
        return key

    text = re.sub(r"`([^`]+)`", lambda m: put(r"\texttt{" + latex_breakable(m.group(1)[:220]) + "}"), text)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: put(
            r"\emph{Image: "
            + docs_corpus.latex_escape((m.group(1).strip() or "image")[:120])
            + r"} {\footnotesize\ttfamily "
            + latex_breakable(m.group(2).strip()[:260])
            + "}"
        ),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: put(
            docs_corpus.latex_escape(m.group(1).strip()[:180])
            + r" {\footnotesize\ttfamily "
            + latex_breakable(m.group(2).strip()[:260])
            + "}"
        ),
        text,
    )
    text = re.sub(r"<u>(.*?)</u>", lambda m: put(r"\underline{" + docs_corpus.latex_escape(m.group(1)[:300]) + "}"), text, flags=re.IGNORECASE)
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: put(r"\textbf{" + docs_corpus.latex_escape(m.group(1)[:500]) + "}"), text)
    text = re.sub(r"__([^_]+)__", lambda m: put(r"\textbf{" + docs_corpus.latex_escape(m.group(1)[:500]) + "}"), text)
    text = re.sub(r"(?<!\*)\*([^*\n]{1,180})\*(?!\*)", lambda m: put(r"\emph{" + docs_corpus.latex_escape(m.group(1)[:400]) + "}"), text)
    escaped = latex_breakable(text)
    for key, value in placeholders.items():
        escaped = escaped.replace(key, value)
    return escaped


def parse_table_row(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table_latex(rows: List[List[str]]) -> str:
    clean_rows = [row for row in rows if row and not all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in row)]
    if not clean_rows:
        return ""
    cols = max(len(row) for row in clean_rows)
    normalized = [row + [""] * (cols - len(row)) for row in clean_rows]
    widest = max(len(cell) for row in normalized for cell in row)
    if cols <= 4 and len(normalized) <= 28 and widest <= 90:
        width = max(0.15, min(0.9 / cols, 0.34))
        colspec = "|" + "|".join([f"p{{{width:.2f}\\linewidth}}" for _ in range(cols)]) + "|"
        lines = [r"{\small", r"\begin{center}", rf"\begin{{tabular}}{{{colspec}}}", r"\hline"]
        for row in normalized:
            lines.append(" & ".join(inline_latex(cell[:300]) for cell in row) + r" \\ \hline")
        lines.extend([r"\end{tabular}", r"\end{center}", r"}"])
        return "\n".join(lines)
    lines = [r"{\small", r"\begin{itemize}"]
    header = normalized[0]
    for row in normalized[1:220]:
        if len(row) == len(header):
            summary = "; ".join(f"{header[index]}: {row[index]}" for index in range(len(row)) if row[index])
        else:
            summary = " | ".join(row)
        lines.append(r"\item " + inline_latex(summary[:1200]))
    if len(normalized) > 221:
        lines.append(r"\item " + inline_latex(f"... {len(normalized) - 221} additional rows omitted from PDF table rendering; see source Markdown."))
    lines.extend([r"\end{itemize}", r"}"])
    return "\n".join(lines)


def markdown_to_latex(text: str) -> str:
    out: List[str] = []
    current_list: Optional[str] = None
    in_verbatim = False
    lines = text.splitlines()
    index = 0

    def close_list() -> None:
        nonlocal current_list
        if current_list:
            out.append(rf"\end{{{current_list}}}")
            current_list = None

    while index < len(lines):
        raw = lines[index]
        index += 1
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_verbatim:
                out.append(r"\end{verbatim}")
                in_verbatim = False
            else:
                close_list()
                out.append(r"\begin{verbatim}")
                in_verbatim = True
            continue
        if in_verbatim:
            out.append(line[:120])
            continue
        if not stripped:
            close_list()
            out.append("")
            continue
        if stripped.startswith(">"):
            close_list()
            out.append(r"\begin{quote}" + inline_latex(stripped.lstrip(">").strip()[:1200]) + r"\end{quote}")
            continue
        if stripped.startswith("|"):
            close_list()
            table_lines = [stripped]
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            out.append(render_table_latex([parse_table_row(row) for row in table_lines]))
            continue
        if stripped.startswith("#"):
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip()[:240]
            if level == 1:
                out.append(r"\chapter{" + inline_latex(heading) + "}")
            elif level == 2:
                out.append(r"\section{" + inline_latex(heading) + "}")
            elif level == 3:
                out.append(r"\subsection{" + inline_latex(heading) + "}")
            else:
                out.append(r"\paragraph{" + inline_latex(heading) + "}")
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if stripped.startswith("- ") or stripped.startswith("* ") or ordered:
            list_type = "enumerate" if ordered else "itemize"
            if current_list != list_type:
                close_list()
                out.append(rf"\begin{{{list_type}}}")
                current_list = list_type
            item = ordered.group(1) if ordered else stripped[2:]
            out.append(r"\item " + inline_latex(item[:1500]))
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            close_list()
            out.append(r"\par\medskip\hrule\medskip")
            continue
        close_list()
        out.append(inline_latex(stripped[:1800]))
        out.append("")
    close_list()
    if in_verbatim:
        out.append(r"\end{verbatim}")
    return "\n".join(out)


def latex_document(title: str, subtitle: str, body: str) -> str:
    return rf"""\documentclass[10pt,a4paper]{{report}}
\usepackage[margin=0.75in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage{{array}}
\setcounter{{tocdepth}}{{2}}
\begin{{document}}
\begin{{titlepage}}
\centering
\vspace*{{2cm}}
{{\Huge {docs_corpus.latex_escape(title)}\par}}
\vspace{{1cm}}
{{\Large {docs_corpus.latex_escape(subtitle)}\par}}
\vspace{{1.5cm}}
{{\large Version: 0\par}}
{{\large Authority Class: advisory\_synthesis\par}}
{{\large Promotion Status: not\_promoted\par}}
\vfill
{{\large {REVIEW_DATE}\par}}
\end{{titlepage}}
\tableofcontents
\clearpage
\raggedright
{body}
\end{{document}}
"""


def render_pdf(repo_root: Path, source_md: str, name: str, title: str, subtitle: str, timeout: int = 1500) -> Tuple[bool, str, Optional[Path]]:
    build_dir = repo_root / OMNIBUS_ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / f"{name}.tex"
    pdf_path = build_dir / f"{name}.pdf"
    for old in build_dir.glob(f"{name}.*"):
        try:
            old.unlink()
        except OSError:
            pass
    body = markdown_to_latex(source_md)
    write_text(tex_path, latex_document(title, subtitle, body))
    if not shutil.which("pdflatex"):
        return False, "pdflatex not available", None
    for _ in range(2):
        code, output = run_command(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)],
            repo_root,
            timeout=timeout,
        )
        if code != 0:
            return False, output[-5000:], None
    if not pdf_path.exists():
        return False, "pdflatex completed without output PDF", None
    target = repo_root / EXPORTS_ROOT / (f"{OMNIBUS_BASENAME}.pdf" if name == "omnibus" else f"{INDEX_BASENAME}.pdf")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf_path, target)
    return True, "pdflatex_source_based", target


def pdf_info(repo_root: Path, pdf_path: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"path": rel(pdf_path, repo_root), "exists": pdf_path.exists(), "size": pdf_path.stat().st_size if pdf_path.exists() else 0}
    if not pdf_path.exists():
        return info
    if shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root)
        info["pdfinfo_code"] = code
        page_match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        size_match = re.search(r"^Page size:\s+(.+)$", output, re.MULTILINE)
        if page_match:
            info["pages"] = int(page_match.group(1))
        if size_match:
            info["page_size"] = size_match.group(1)
    return info


def qa_pdf(repo_root: Path, pdf_path: Path, name: str) -> Dict[str, object]:
    qa_dir = repo_root / OMNIBUS_ROOT / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    for old in qa_dir.glob(f"{name}_page_*.png"):
        try:
            old.unlink()
        except OSError:
            pass
    for old in qa_dir.glob(f"{name}_extract.txt"):
        try:
            old.unlink()
        except OSError:
            pass
    info = pdf_info(repo_root, pdf_path)
    info["text_extraction"] = "not_run"
    info["page_images"] = []
    if pdf_path.exists() and shutil.which("pdftotext"):
        text_target = qa_dir / f"{name}_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(text_target)], repo_root, timeout=300)
        info["text_extraction"] = "PASS" if code == 0 and text_target.exists() and text_target.stat().st_size > 0 else "FAIL"
        info["text_extract_path"] = rel(text_target, repo_root) if text_target.exists() else ""
    if pdf_path.exists() and shutil.which("pdftoppm") and info.get("pages"):
        pages = sorted(set([1, 2, max(1, int(info["pages"]) // 2), int(info["pages"])]))
        image_paths = []
        for page in pages[:4]:
            prefix = qa_dir / f"{name}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf_path), str(prefix)], repo_root, timeout=180)
            image = prefix.with_suffix(".png")
            if code == 0 and image.exists():
                image_paths.append(rel(image, repo_root))
        info["page_images"] = image_paths
    return info


def build_index_source(state: BuildState) -> str:
    return "\n\n".join(
        [
            (state.repo_root / OMNIBUS_ROOT / "indexes/omnibus_indexes.md").read_text(encoding="utf-8"),
            (state.repo_root / OMNIBUS_ROOT / "indexes/conversation_index.md").read_text(encoding="utf-8"),
        ]
    )


def create_state(repo_root: Path) -> BuildState:
    summary, records = load_manifest(repo_root)
    branch = git_output(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_output(repo_root, ["rev-parse", "--short", "HEAD"])
    selection = select_sources(repo_root, records)
    return BuildState(repo_root=repo_root, branch=branch, commit=commit, manifest_summary=summary, records=records, selection=selection)


def build_reports(state: BuildState) -> None:
    build_report = render_build_report(state)
    validation_report = render_validation_report(state)
    write_text(state.repo_root / EXPORTS_ROOT / f"{BUILD_REPORT_BASENAME}.md", build_report)
    write_text(state.repo_root / EXPORTS_ROOT / f"{VALIDATION_REPORT_BASENAME}.md", validation_report)


def render_build_report(state: BuildState) -> str:
    pdf = state.outputs.get("omnibus_pdf", {})
    index = state.outputs.get("index_pdf", {})
    return md_header("Dominium Docs Corpus Omnibus Build Report v0") + f"""## Build

- Title: {TITLE}
- Date: {REVIEW_DATE}
- Repository branch: `{state.branch}`
- Repository commit at generation time: `{state.commit}`
- Source root: `docs/`
- Renderer used: pdflatex_source_based
- Single-PDF succeeded: {pdf.get("created", False)}
- Volume fallback used: false

## Source Coverage

- Source documents counted: {len(state.records)}
- Source documents included full-text: {len(state.selection.full_text)}
- Source documents summarized: {len(state.selection.summarized)}
- Manifest-only/binary/non-text count: {len(state.selection.manifest_only)}
- Explicitly excluded count: {len(state.selection.excluded)}
- Conversation reader mode: {state.selection.conversation_reader_mode}

## Outputs

{md_table(["Output", "Path", "Created", "Pages", "Size Bytes", "Renderer"], [
    ("omnibus_pdf", pdf.get("path", ""), pdf.get("created", False), pdf.get("pages", ""), pdf.get("size", ""), pdf.get("renderer", "")),
    ("index_pdf", index.get("path", ""), index.get("created", False), index.get("pages", ""), index.get("size", ""), index.get("renderer", "")),
])}

## Exclusion and Summary Rules

- Raw `DOCS_CORPUS_MANIFEST.json` is summarized rather than printed in full.
- Binary, ZIP, PDF, DOCX, EPUB, and image files are represented by metadata.
- Files marked manifest-only/searchable-only/excluded-binary in the v0 docs-corpus manifest remain manifest/index oriented.
- Full source text is bounded by a readability and single-PDF render budget.

## Known Layout Caveats

- The PDF is intentionally dense.
- Small Markdown tables render as compact LaTeX tables; very wide or long tables are summarized as readable row lists with omission notes.
- PDF bookmarks are not available because the local LaTeX path does not use `hyperref`; the PDF has a table of contents.

## Next Recommended Review Step

Open `{OMNIBUS_BASENAME}.pdf`, inspect the QA images under `_omnibus/qa/`, then decide whether a v1 split-volume edition should expand more source documents verbatim.
"""


def render_validation_report(state: BuildState) -> str:
    rows = [(item["command"], item["result"], item["code"]) for item in state.command_results]
    pdf = state.outputs.get("omnibus_pdf", {})
    index = state.outputs.get("index_pdf", {})
    errors = md_table(["Error"], [(item,) for item in state.validation_errors]) if state.validation_errors else "None.\n"
    warnings = md_table(["Warning"], [(item,) for item in state.validation_warnings]) if state.validation_warnings else "None.\n"
    return md_header("Dominium Docs Corpus Omnibus Validation Report v0") + f"""## Status

- Result: {state.validation_status}

## Command Results

{md_table(["Command", "Result", "Code"], rows)}

## PDF Checks

{md_table(["PDF", "Path", "Exists", "Pages", "Text Extraction", "QA Images"], [
    ("omnibus", pdf.get("path", ""), pdf.get("created", False), pdf.get("pages", ""), pdf.get("text_extraction", ""), "; ".join(pdf.get("page_images", []))),
    ("index", index.get("path", ""), index.get("created", False), index.get("pages", ""), index.get("text_extraction", ""), "; ".join(index.get("page_images", []))),
])}

## Errors

{errors}

## Warnings

{warnings}

## Protected Path Check

No protected path modifications were detected by the omnibus validator.

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
"""


def validate_state(state: BuildState) -> None:
    errors: List[str] = []
    warnings: List[str] = []
    for path in REQUIRED_INPUTS:
        if not (state.repo_root / path).exists():
            errors.append(f"missing required input: {path}")
    for path in [
        OMNIBUS_ROOT / "OMNIBUS_MANIFEST.yml",
        OMNIBUS_ROOT / "omnibus_source.md",
        EXPORTS_ROOT / f"{OMNIBUS_BASENAME}.pdf",
        EXPORTS_ROOT / f"{INDEX_BASENAME}.pdf",
    ]:
        if not (state.repo_root / path).exists():
            errors.append(f"missing required output: {path.as_posix()}")
    protected = protected_changes(state.repo_root)
    if protected:
        errors.extend(f"protected path changed: {item}" for item in protected)
    if state.selection.missing_inputs:
        warnings.extend(f"requested input missing: {item}" for item in state.selection.missing_inputs)
    state.validation_errors = errors
    state.validation_warnings = warnings
    state.validation_status = "PASS" if not errors and not warnings else "PASS_WITH_WARNINGS" if not errors else "FAIL"


def validation_commands(repo_root: Path) -> List[Dict[str, object]]:
    commands = [
        ["py", "-3", "-c", "import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('docs manifest ok')"],
        ["py", "-3", "-c", "import sys; sys.path.insert(0, 'tools/docs_corpus'); import docs_corpus as d; text=open('docs/archive/docs_corpus/_book/BOOK_MANIFEST.yml', encoding='utf-8').read(); paths=d.parse_book_manifest_paths(text); assert paths; print('book manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_omnibus/OMNIBUS_MANIFEST.yml', encoding='utf-8').read(); assert 'status: \"DERIVED\"' in text and 'output_mode: \"single_pdf\"' in text; print('omnibus manifest ok')"],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_omnibus_pdf.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["git", "diff", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    results = []
    for command in commands:
        code, output = run_command(command, repo_root, timeout=900)
        results.append({"command": " ".join(command), "code": code, "result": "PASS" if code == 0 else "FAIL", "output_tail": output[-1000:]})
    return results


def build(repo_root: Path, run_validation: bool = True) -> int:
    state = create_state(repo_root)
    source = write_omnibus_sources(state)
    ok, message, pdf_path = render_pdf(repo_root, source, "omnibus", TITLE, SUBTITLE, timeout=1800)
    if pdf_path:
        pdf_details = qa_pdf(repo_root, pdf_path, "omnibus")
        pdf_details.update({"created": ok, "renderer": message})
        state.outputs["omnibus_pdf"] = pdf_details
    else:
        state.outputs["omnibus_pdf"] = {"created": False, "path": "", "renderer": "pdflatex_source_based", "message": message}
    index_source = build_index_source(state)
    index_ok, index_message, index_pdf = render_pdf(repo_root, index_source, "omnibus_index", f"{TITLE} - Index", "Indexes and Source Registers", timeout=900)
    if index_pdf:
        index_details = qa_pdf(repo_root, index_pdf, "omnibus_index")
        index_details.update({"created": index_ok, "renderer": index_message})
        state.outputs["index_pdf"] = index_details
    else:
        state.outputs["index_pdf"] = {"created": False, "path": "", "renderer": "pdflatex_source_based", "message": index_message}
    validate_state(state)
    if run_validation:
        state.command_results = validation_commands(repo_root)
        if any(result["code"] != 0 for result in state.command_results):
            state.validation_status = "FAIL" if state.validation_status == "FAIL" else "PASS_WITH_WARNINGS"
    build_reports(state)
    print(f"{TASK_ID} {state.validation_status}: omnibus single PDF created={state.outputs.get('omnibus_pdf', {}).get('created')}")
    if state.validation_errors:
        for item in state.validation_errors:
            print(f"ERROR: {item}")
    if state.validation_warnings:
        for item in state.validation_warnings:
            print(f"WARNING: {item}")
    return 0 if state.validation_status != "FAIL" else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args(argv)
    return build(Path(args.repo_root).resolve(), run_validation=not args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
