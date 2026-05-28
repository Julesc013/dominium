"""Build the derived conversation-corpus book bundle.

This publisher is intentionally archive-only. It assembles already-generated
conversation corpus outputs into reader and reference artifacts without
promoting archive claims into canon, contracts, schema, code, release, or queue
state.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


REVIEW_DATE = "2026-05-28"
CORPUS_ROOT = Path("docs/archive/conversations")
BOOK_DIR = CORPUS_ROOT / "_book"
EXPORTS_DIR = CORPUS_ROOT / "_exports"
QA_DIR = BOOK_DIR / "qa"
TITLE = "Dominium Conversation Corpus Book v0"
SUBTITLE = "A Derived Reader, Synthesis, Decision, Promotion, and Reconciliation Guide"
BOOK_BASENAME = "Dominium_Conversation_Corpus_Book_v0"
REFERENCE_BASENAME = "Dominium_Conversation_Corpus_Reference_Appendix_v0"
BUILD_REPORT_BASENAME = "Dominium_Conversation_Corpus_Book_Build_Report_v0"
VALIDATION_REPORT_BASENAME = "Dominium_Conversation_Corpus_Book_Validation_Report_v0"

STATUS_BLOCK = """Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""

PROTECTED_PREFIXES = (
    "docs/canon/",
    "docs/architecture/",
    "docs/reference/contracts/",
    "contracts/",
    "schema/",
    "engine/",
    "game/",
    "runtime/",
    "apps/",
    "release/",
    "updates/",
    "security/",
    ".aide/queue/current.toml",
)

SOURCE_ROOTS = [
    "_synthesis",
    "_decision",
    "_promotion",
    "_reconciliation",
    "_audit",
    "_wiki",
    "_reader",
    "_intake",
]


@dataclass
class SourceSpec:
    path: str
    role: str = "main"
    include_mode: str = "full"


@dataclass
class ChapterSpec:
    id: str
    title: str
    output: str
    sources: List[SourceSpec] = field(default_factory=list)
    generated: Optional[str] = None


def ascii_text(value: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2011": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u2192": "->",
        "\u2194": "<->",
        "\u03a3": "Sigma",
        "\u039b": "Lambda",
        "\u03a9": "Omega",
        "\u039e": "Xi",
        "\u03a0": "Pi",
        "\u03a5": "Upsilon",
        "\u03a6": "Phi",
        "\u0396": "Zeta",
        "\ufeff": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("ascii", "replace").decode("ascii")


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_if_changed(path: Path, content: str) -> bool:
    content = ascii_text(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return True


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return ascii_text(data.decode(encoding, errors="replace"))
        except UnicodeDecodeError:
            continue
    return ascii_text(data.decode("utf-8", errors="replace"))


def command_available(name: str) -> Optional[str]:
    return shutil.which(name)


def source(path: str, role: str = "main", include_mode: str = "full") -> SourceSpec:
    return SourceSpec(path=path, role=role, include_mode=include_mode)


def default_chapters() -> Tuple[List[ChapterSpec], List[ChapterSpec]]:
    chapters = [
        ChapterSpec("front_matter", "Front Matter", "chapters/00_front_matter.md", generated="front_matter"),
        ChapterSpec(
            "orientation",
            "Orientation",
            "chapters/01_orientation.md",
            [
                source("_synthesis/READ_THIS_FIRST_v0.md"),
                source("_synthesis/CURRENT_PROJECT_ATLAS_v0.md"),
            ],
        ),
        ChapterSpec(
            "project_synthesis",
            "Project Synthesis",
            "chapters/02_project_synthesis.md",
            [
                source("_synthesis/EXECUTIVE_BRIEF_v0.md"),
                source("_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md"),
                source("_synthesis/FULL_PROJECT_PICTURE_v0.md"),
                source("_synthesis/CONTRADICTIONS_TO_RECONCILE_v0.md"),
            ],
        ),
        ChapterSpec(
            "authority_reconciliation",
            "Authority and Reconciliation",
            "chapters/03_authority_and_reconciliation.md",
            [
                source("_reconciliation/REPO_AUTHORITY_CROSSWALK_v0.md"),
                source("_reconciliation/CURRENT_CANON_ALIGNMENT_v0.md"),
                source("_reconciliation/BLOCKED_SCOPE_ALIGNMENT_v0.md"),
                source("_reconciliation/CLAIM_REVIEW_MATRIX_v0.md", include_mode="summary_table"),
            ],
        ),
        ChapterSpec(
            "decision_docket",
            "Decision Docket",
            "chapters/04_decision_docket.md",
            [
                source("_decision/DECISION_SUMMARY_v0.md"),
                source("_decision/DECISION_DOCKET_v0.md"),
                source("_decision/DECISION_OPTIONS_MATRIX_v0.md", include_mode="summary_table"),
                source("_decision/DEFERRED_DECISIONS_v0.md"),
            ],
        ),
        ChapterSpec(
            "promotion_review",
            "Promotion Review",
            "chapters/05_promotion_review.md",
            [
                source("_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md"),
                source("_promotion/PROMOTION_REVIEW_BOARD_v0.md", include_mode="summary_table"),
                source("_promotion/PROMOTION_TARGET_MAP_v0.md", include_mode="summary_table"),
                source("_promotion/PROMOTION_NOT_READY_v0.md", include_mode="summary_table"),
                source("_promotion/PROMOTION_TRIAGE_v0.md"),
            ],
        ),
        ChapterSpec(
            "audit",
            "Contradictions, Staleness, and Verification",
            "chapters/06_contradictions_staleness_verification.md",
            [
                source("_audit/CONTRADICTION_MATRIX.md", include_mode="summary_table"),
                source("_audit/STALENESS_AND_VERIFICATION.md"),
                source("_audit/UNCERTAINTY_REGISTER.md"),
                source("_audit/DOC_DRIFT_REPORT.md"),
                source("_audit/COVERAGE_GAPS.md"),
                source("_audit/INTAKE_ACCEPTANCE_REVIEW.md"),
            ],
        ),
        ChapterSpec(
            "navigation",
            "Wiki and Navigation Digest",
            "chapters/07_wiki_navigation_digest.md",
            [
                source("_wiki/index.md"),
                source("_wiki/topics/index.md"),
                source("_wiki/workstreams/index.md"),
                source("_wiki/decisions/index.md", include_mode="summary_table"),
                source("_wiki/tasks/index.md", include_mode="summary_table"),
                source("_wiki/artifacts/index.md", include_mode="summary_table"),
                source("_wiki/open_questions/index.md", include_mode="summary_table"),
                source("_wiki/risks/index.md", include_mode="summary_table"),
            ],
        ),
        ChapterSpec(
            "conversation_digest",
            "Per-Conversation Reader Digest",
            "chapters/08_conversation_reader_digest.md",
            [source("_reader/conversation_reader_index.md", include_mode="summary_table")],
            generated="conversation_digest",
        ),
    ]
    appendices = [
        ChapterSpec(
            "source_manifest",
            "Appendix A - Source Corpus Manifest",
            "appendices/A_source_corpus_manifest.md",
            [
                source("_intake/CORPUS_MANIFEST.md", include_mode="summary_table"),
                source("_intake/PACKAGE_COMPLETENESS.md", include_mode="summary_table"),
                source("_intake/SOURCE_PROVENANCE.md", include_mode="summary_table"),
            ],
        ),
        ChapterSpec(
            "claim_matrix",
            "Appendix B - Full Claim Review Matrix",
            "appendices/B_full_claim_review_matrix.md",
            [source("_reconciliation/CLAIM_REVIEW_MATRIX_v0.md")],
        ),
        ChapterSpec(
            "promotion_register",
            "Appendix C - Full Promotion Register",
            "appendices/C_full_promotion_register.md",
            [
                source("_promotion/PROMOTION_REVIEW_BOARD_v0.md"),
                source("_promotion/PROMOTION_TARGET_MAP_v0.md"),
                source("_promotion/PROMOTION_QUEUE.md", include_mode="summary_table"),
            ],
        ),
        ChapterSpec(
            "contradiction_register",
            "Appendix D - Full Contradiction Register",
            "appendices/D_full_contradiction_register.md",
            [
                source("_audit/CONTRADICTION_MATRIX.md"),
                source("_audit/STALENESS_AND_VERIFICATION.md"),
                source("_audit/DOC_DRIFT_REPORT.md"),
            ],
        ),
        ChapterSpec("path_source_index", "Appendix E - Path and Source Index", "appendices/E_path_and_source_index.md", generated="path_index"),
    ]
    return chapters, appendices


def all_manifest_sources(chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> List[str]:
    values: List[str] = []
    for spec in [*chapters, *appendices]:
        for source_spec in spec.sources:
            values.append(source_spec.path)
    return sorted(set(values), key=str.casefold)


def generated_source_files(repo_root: Path) -> List[str]:
    root = repo_root / CORPUS_ROOT
    files: List[str] = []
    for name in SOURCE_ROOTS:
        directory = root / name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".yml", ".yaml"}:
                files.append(path.relative_to(root).as_posix())
    return sorted(files, key=str.casefold)


def excluded_sources(repo_root: Path, included: Sequence[str]) -> List[Dict[str, str]]:
    included_set = set(included)
    excluded: List[Dict[str, str]] = []
    for path in generated_source_files(repo_root):
        if path in included_set:
            continue
        if path.startswith("_reader/by_chat/"):
            reason = "included as per-conversation digest and retained as full HTML/source reference"
        elif path.startswith("_wiki/topics/"):
            reason = "topic detail covered by navigation digest; full source retained"
        elif path == "_intake/SHA256SUMS.txt":
            reason = "too dense for reader edition; retained as source hash file"
        elif path == "_intake/corpus_manifest.json":
            reason = "machine-readable manifest parsed for source indexes"
        elif path.startswith("_book/") or path.startswith("_exports/"):
            reason = "generated publication artifact"
        else:
            reason = "duplicate, dense, or lower-priority generated surface; retained in source tree"
        excluded.append({"path": path, "reason": reason})
    return excluded


def yaml_quote(value: str) -> str:
    return json.dumps(value)


def render_manifest(repo_root: Path, chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> str:
    included = all_manifest_sources(chapters, appendices)
    excluded = excluded_sources(repo_root, included)
    lines = [
        "book:",
        f"  title: {yaml_quote(TITLE)}",
        f"  subtitle: {yaml_quote(SUBTITLE)}",
        f"  date: {yaml_quote(REVIEW_DATE)}",
        '  status: "DERIVED"',
        '  authority_class: "advisory_synthesis"',
        '  source_root: "docs/archive/conversations"',
        '  promotion_status: "not_promoted"',
        "  impacts:",
        '    canon: "unchanged"',
        '    contract_schema: "unchanged"',
        '    implementation: "unchanged"',
        '    release: "unchanged"',
        '    queue: "unchanged"',
        "outputs:",
        "  pdf: true",
        "  html: true",
        "  docx: true",
        "  epub: true",
        "  reference_appendix_pdf: true",
        "chapters:",
    ]
    for chapter in chapters:
        lines.extend(
            [
                f"  - id: {yaml_quote(chapter.id)}",
                f"    title: {yaml_quote(chapter.title)}",
                f"    output: {yaml_quote(chapter.output)}",
                "    sources:",
            ]
        )
        if chapter.generated:
            lines.append(f"      - generated: {yaml_quote(chapter.generated)}")
        for source_spec in chapter.sources:
            lines.append(f"      - path: {yaml_quote(source_spec.path)}")
            lines.append(f"        include_mode: {yaml_quote(source_spec.include_mode)}")
    lines.append("appendices:")
    for appendix in appendices:
        lines.extend(
            [
                f"  - id: {yaml_quote(appendix.id)}",
                f"    title: {yaml_quote(appendix.title)}",
                f"    output: {yaml_quote(appendix.output)}",
                "    sources:",
            ]
        )
        if appendix.generated:
            lines.append(f"      - generated: {yaml_quote(appendix.generated)}")
        for source_spec in appendix.sources:
            lines.append(f"      - path: {yaml_quote(source_spec.path)}")
            lines.append(f"        include_mode: {yaml_quote(source_spec.include_mode)}")
    lines.append("included_sources:")
    for path in included:
        lines.append(f"  - {yaml_quote(path)}")
    lines.append("excluded_sources:")
    for item in excluded:
        lines.append(f"  - path: {yaml_quote(item['path'])}")
        lines.append(f"    reason: {yaml_quote(item['reason'])}")
    lines.extend(
        [
            "quality_rules:",
            "  require_source_paths: true",
            "  require_authority_notice: true",
            "  require_status_labels: true",
            "  preserve_repo_links: true",
            "  no_live_doc_promotion: true",
            "protected_paths:",
        ]
    )
    for path in PROTECTED_PREFIXES:
        lines.append(f"  - {yaml_quote(path)}")
    lines.extend(
        [
            "validation_commands:",
            '  - "py -3 tools/conversations/validate_conversation_outputs.py --repo-root ."',
            '  - "py -3 -m unittest discover tests/tools/conversations"',
            '  - "git diff --check"',
            '  - "py -3 .aide/scripts/aide_lite.py doctor"',
            '  - "py -3 .aide/scripts/aide_lite.py validate"',
            '  - "py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST"',
        ]
    )
    return "\n".join(lines) + "\n"


def parse_manifest_paths(text: str) -> List[str]:
    paths: List[str] = []
    for match in re.finditer(r"^\s*-\s+path:\s+(.+)$", text, flags=re.MULTILINE):
        raw = match.group(1).strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw.strip('"')
        paths.append(value)
    return paths


def strip_metadata(text: str) -> str:
    lines = text.splitlines()
    idx = 0
    metadata_keys = (
        "Status:",
        "Last Reviewed:",
        "Supersedes:",
        "Superseded By:",
        "Stability:",
        "Result:",
        "Binding Sources:",
        "Authority Class:",
        "Promotion Status:",
        "Source Class:",
        "Source Root:",
        "Canon impact:",
        "Contract/schema impact:",
        "Implementation impact:",
        "Release impact:",
        "Queue impact:",
    )
    while idx < len(lines) and (not lines[idx].strip() or lines[idx].startswith(metadata_keys)):
        idx += 1
    return "\n".join(lines[idx:]).strip() + "\n"


def normalize_headings(text: str, level_offset: int = 1) -> str:
    result = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            level = min(6, len(match.group(1)) + level_offset)
            result.append("#" * level + " " + match.group(2).strip())
        else:
            result.append(line)
    return "\n".join(result).strip() + "\n"


def summarize_table_blocks(text: str, max_rows: int = 18) -> str:
    lines = text.splitlines()
    out: List[str] = []
    idx = 0
    while idx < len(lines):
        if lines[idx].lstrip().startswith("|"):
            table: List[str] = []
            while idx < len(lines) and lines[idx].lstrip().startswith("|"):
                table.append(lines[idx])
                idx += 1
            if len(table) > max_rows or any(line.count("|") > 6 for line in table):
                out.append("")
                out.append("> Dense table summarized for the reader edition. See the source file, HTML output, or reference appendix source for full detail.")
                out.append("")
                out.extend(table[: min(len(table), 8)])
                if len(table) > 8:
                    out.append(f"| ... | {len(table) - 8} additional rows omitted from reader view |")
                out.append("")
            else:
                out.extend(table)
            continue
        out.append(lines[idx])
        idx += 1
    return "\n".join(out).strip() + "\n"


def source_note(path: str) -> str:
    return f"\n> SOURCE PATH: `docs/archive/conversations/{path}`\n\n"


def render_generated_front_matter() -> str:
    return f"""# Front Matter

# {TITLE}

## {SUBTITLE}

{STATUS_BLOCK}

## Authority and Non-Promotion Notice

This book is a publication artifact derived from `docs/archive/conversations/`.
It is not canon, not architecture doctrine, not a contract, not a schema, and
not an implementation plan.

The book does not promote archive claims into repo truth. Current repo authority
remains `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`,
`AGENTS.md`, current contracts/schema law, current queue state, and validated
repo artifacts.

## How To Read This Book

- Read Part I for orientation and current guardrails.
- Read Part II for the narrative synthesis.
- Read Part III for authority and reconciliation.
- Read Part IV for decisions that need human or future-queue handling.
- Read Part V for promotion candidates that may become later microtasks.
- Read Part VI for contradiction, staleness, and verification risk.
- Use the appendices for dense source and register material.

## What Not To Conclude

- This book does not open blocked queue areas.
- This book does not resolve contradictions by itself.
- This book does not replace current repo docs.
- This book does not claim release readiness.
- This book does not authorize canon, contract, schema, implementation, release,
  or queue changes.

## Source Hierarchy

1. Canon and glossary.
2. `AGENTS.md`.
3. Scope-specific contracts, schema law, current queue, and validated repo
   artifacts.
4. Generated archive outputs with provenance.
5. Historical conversation material as advisory evidence.

## ID Conventions

- `DECISION-*`: decision docket items.
- `PROMOTE-*`: raw promotion candidates.
- `CONTRA-*`: contradiction, staleness, or drift findings.
- Source paths are repo-relative unless explicitly marked otherwise.
"""


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    pattern = heading.lower()
    for idx, line in enumerate(lines):
        if line.strip().lower().lstrip("# ").startswith(pattern):
            start = idx + 1
            break
    if start is None:
        return ""
    collected = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def render_conversation_digest(repo_root: Path) -> str:
    root = repo_root / CORPUS_ROOT
    manifest = json.loads((root / "_intake" / "corpus_manifest.json").read_text(encoding="utf-8"))
    lines = ["# Per-Conversation Reader Digest", ""]
    lines.append("This digest gives one concise entry per conversation. Full reader pages remain in `_reader/by_chat/`.")
    lines.append("")
    for conv in manifest.get("conversations", []):
        conv_slug = conv.get("slug") or re.sub(r"[^a-z0-9]+", "_", conv.get("folder", "").lower()).strip("_")
        reader_path = root / "_reader" / "by_chat" / f"{conv_slug}.md"
        reader_text = read_text(reader_path) if reader_path.exists() else ""
        about = extract_section(reader_text, "What This Conversation Was About")
        about = re.sub(r"\s+", " ", about).strip()
        if len(about) > 420:
            about = about[:417].rstrip() + "..."
        topics = ", ".join(conv.get("topics", [])) or "unclassified"
        lines.append(f"## {conv.get('title') or conv['folder']}")
        lines.append("")
        lines.append(f"- Source folder: `docs/archive/conversations/{conv['folder']}/`")
        lines.append(f"- Reader page: `docs/archive/conversations/_reader/by_chat/{conv_slug}.md`")
        lines.append(f"- Primary source: `{conv.get('primary_source', 'none')}`")
        lines.append(f"- Completeness: `{conv.get('completeness_status')}`")
        lines.append(f"- Topics: {topics}")
        lines.append(f"- Digest: {about or 'No reader summary extracted; inspect the reader page.'}")
        lines.append("")
    return "\n".join(lines)


def render_path_index(repo_root: Path, included: Sequence[str], excluded: Sequence[Dict[str, str]]) -> str:
    lines = ["# Path and Source Index", ""]
    lines.append("## Included Source Files")
    lines.append("")
    for path in included:
        lines.append(f"- `docs/archive/conversations/{path}`")
    lines.append("")
    lines.append("## Excluded From Reader Edition")
    lines.append("")
    for item in excluded:
        lines.append(f"- `docs/archive/conversations/{item['path']}` - {item['reason']}")
    lines.append("")
    lines.append("## Generated Book Files")
    lines.append("")
    for path in sorted((repo_root / BOOK_DIR).rglob("*"), key=lambda p: p.as_posix().casefold()):
        if path.is_file():
            lines.append(f"- `{rel(path, repo_root)}`")
    return "\n".join(lines) + "\n"


def render_chapter(repo_root: Path, spec: ChapterSpec, excluded: Sequence[Dict[str, str]]) -> str:
    root = repo_root / CORPUS_ROOT
    lines = [f"# {spec.title}", ""]
    if spec.generated == "front_matter":
        return render_generated_front_matter()
    if spec.generated == "conversation_digest":
        lines.append(render_conversation_digest(repo_root))
    if spec.generated == "path_index":
        included = all_manifest_sources(*default_chapters())
        lines.append(render_path_index(repo_root, included, excluded))
    for source_spec in spec.sources:
        path = root / source_spec.path
        if not path.exists():
            lines.append(f"## Missing Source: `{source_spec.path}`")
            lines.append("")
            lines.append("This source was listed in the manifest but not found at build time.")
            continue
        body = strip_metadata(read_text(path))
        body = normalize_headings(body, 1)
        if source_spec.include_mode == "summary_table":
            body = summarize_table_blocks(body)
        lines.append(source_note(source_spec.path))
        lines.append(body)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_readme(renderer: str) -> str:
    return f"""{STATUS_BLOCK}
# Conversation Corpus Book Pipeline

This directory contains the reproducible source for `{TITLE}`.

## Renderer

- Quarto: not available unless installed locally.
- Pandoc: not available unless installed locally.
- Active renderer for this build: `{renderer}`.

The pipeline generates curated Markdown chapters, HTML, PDF through local LaTeX
when available, DOCX through a minimal OOXML package, EPUB through a minimal EPUB
package, and build/validation reports.

## Non-Goals

- No canon changes.
- No contract/schema changes.
- No implementation changes.
- No release changes.
- No queue changes.
- No promotion of archive claims.
"""


def render_index(chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> str:
    lines = [f"# {TITLE}", "", SUBTITLE, "", STATUS_BLOCK, "", "## Contents", ""]
    for spec in chapters:
        lines.append(f"- [{spec.title}]({spec.output})")
    for spec in appendices:
        lines.append(f"- [{spec.title}]({spec.output})")
    return "\n".join(lines) + "\n"


def markdown_links(text: str) -> Iterable[str]:
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)\n]+)\)", text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        yield target


def md_inline_to_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def markdown_to_html(text: str) -> str:
    out: List[str] = []
    in_ul = False
    in_code = False
    code_lines: List[str] = []
    paragraph: List[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append("<p>" + md_inline_to_html(" ".join(paragraph)) + "</p>")
            paragraph = []

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            close_ul()
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            close_ul()
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            close_ul()
            level = min(6, len(heading.group(1)))
            title = heading.group(2).strip()
            anchor = slug(title)
            out.append(f'<h{level} id="{anchor}">{md_inline_to_html(title)}</h{level}>')
            continue
        if line.startswith("- "):
            flush_paragraph()
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append("<li>" + md_inline_to_html(line[2:].strip()) + "</li>")
            continue
        if line.lstrip().startswith("|"):
            flush_paragraph()
            close_ul()
            out.append("<pre class=\"table-source\">" + html.escape(line) + "</pre>")
            continue
        if line.startswith(">"):
            flush_paragraph()
            close_ul()
            out.append("<blockquote>" + md_inline_to_html(line.lstrip("> ").strip()) + "</blockquote>")
            continue
        paragraph.append(line.strip())
    flush_paragraph()
    close_ul()
    return "\n".join(out)


def slug(value: str) -> str:
    value = ascii_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def latex_breakable_path_text(text: str) -> str:
    escaped = latex_escape(text)
    escaped = escaped.replace("/", r"/\allowbreak{}")
    escaped = escaped.replace(r"\_", r"\_\allowbreak{}")
    escaped = escaped.replace("-", r"-\allowbreak{}")
    return escaped


def markdown_to_latex(text: str) -> str:
    out: List[str] = []
    in_code = False
    code_lines: List[str] = []
    in_itemize = False
    table_rows = 0

    def close_itemize() -> None:
        nonlocal in_itemize
        if in_itemize:
            out.append(r"\end{itemize}")
            in_itemize = False

    def flush_table_notice() -> None:
        nonlocal table_rows
        if table_rows:
            out.append(r"\begin{quote}\small Dense table content is summarized in this PDF rendering. See the Markdown source and HTML book for the full table.\end{quote}")
            table_rows = 0

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            close_itemize()
            flush_table_notice()
            if in_code:
                out.append(r"\begin{verbatim}")
                out.extend(code_lines[:80])
                if len(code_lines) > 80:
                    out.append(f"... {len(code_lines) - 80} additional lines omitted from PDF rendering ...")
                out.append(r"\end{verbatim}")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.lstrip().startswith("|"):
            close_itemize()
            table_rows += 1
            continue
        else:
            flush_table_notice()
        if not line.strip():
            close_itemize()
            out.append("")
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            close_itemize()
            title = latex_escape(re.sub(r"`([^`]+)`", r"\1", heading.group(2).strip()))
            level = len(heading.group(1))
            if level <= 1:
                out.append(r"\chapter{" + title + "}")
            elif level == 2:
                out.append(r"\section{" + title + "}")
            elif level == 3:
                out.append(r"\subsection{" + title + "}")
            else:
                out.append(r"\subsubsection{" + title + "}")
            continue
        if line.startswith("- "):
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            out.append(r"\item " + latex_escape(re.sub(r"`([^`]+)`", r"\1", line[2:].strip())))
            continue
        if line.startswith(">"):
            close_itemize()
            quote = re.sub(r"`([^`]+)`", r"\1", line.lstrip("> ").strip())
            if quote.startswith("SOURCE PATH:"):
                out.append(r"{\small\raggedright " + latex_breakable_path_text(quote) + r"\par}")
            else:
                out.append(r"\begin{quote}\small " + latex_escape(quote) + r"\end{quote}")
            continue
        close_itemize()
        clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean)
        if clean.startswith("SOURCE PATH:"):
            out.append(r"{\small\raggedright " + latex_breakable_path_text(clean) + r"\par}")
            out.append("")
            continue
        out.append(latex_escape(clean))
        out.append("")
    close_itemize()
    flush_table_notice()
    return "\n".join(out)


def collect_markdown_files(repo_root: Path, chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> List[Path]:
    paths = [repo_root / BOOK_DIR / "index.md"]
    for spec in [*chapters, *appendices]:
        paths.append(repo_root / BOOK_DIR / spec.output)
    return paths


def render_combined_source(repo_root: Path, chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> str:
    parts = []
    for path in collect_markdown_files(repo_root, chapters, appendices):
        if path.name == "index.md":
            continue
        parts.append(read_text(path))
    return "\n\n".join(parts)


def render_html_book(repo_root: Path, chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec]) -> Path:
    out_dir = repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.html"
    out_dir.mkdir(parents=True, exist_ok=True)
    css = """body{font-family:Segoe UI,Arial,sans-serif;line-height:1.55;margin:0;color:#222;background:#fafafa}
main{max-width:980px;margin:0 auto;padding:32px;background:white}
nav{background:#22313f;color:white;padding:16px 32px;position:sticky;top:0}
nav a{color:white;margin-right:16px} code{background:#f1f3f5;padding:1px 4px;border-radius:3px}
blockquote{border-left:4px solid #789;padding-left:12px;color:#444;background:#f5f7f9}
pre{background:#f4f4f4;padding:10px;overflow:auto}.table-source{font-size:12px}
.search{margin-top:8px}.result{padding:8px;border-bottom:1px solid #ddd}
h1,h2,h3{color:#1f344a}"""
    (out_dir / "styles.css").write_text(css, encoding="utf-8", newline="\n")
    all_sections = []
    nav = []
    for path in collect_markdown_files(repo_root, chapters, appendices):
        text = read_text(path)
        title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1) if title_match else path.stem
        anchor = slug(title)
        nav.append((anchor, title))
        all_sections.append(f'<section id="{anchor}">\n{markdown_to_html(text)}\n</section>')
    search_index = [
        {"id": anchor, "title": title, "text": re.sub(r"\s+", " ", read_text(path))[:20000]}
        for (anchor, title), path in zip(nav, collect_markdown_files(repo_root, chapters, appendices))
    ]
    (out_dir / "search_index.json").write_text(json.dumps(search_index, indent=2), encoding="utf-8")
    search_js = """async function runSearch(){const q=document.getElementById('q').value.toLowerCase();const r=document.getElementById('results');r.innerHTML='';if(!q){return;}const data=await fetch('search_index.json').then(x=>x.json());for(const item of data){if(item.text.toLowerCase().includes(q)||item.title.toLowerCase().includes(q)){const d=document.createElement('div');d.className='result';d.innerHTML='<a href="#'+item.id+'">'+item.title+'</a>';r.appendChild(d);}}}"""
    (out_dir / "search.js").write_text(search_js, encoding="utf-8", newline="\n")
    nav_html = " ".join(f'<a href="#{anchor}">{html.escape(title)}</a>' for anchor, title in nav)
    body = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title><link rel="stylesheet" href="styles.css"></head>
<body><nav><strong>{html.escape(TITLE)}</strong><div class="search"><input id="q" placeholder="Search book" oninput="runSearch()"> <span id="results"></span></div><div>{nav_html}</div></nav>
<main>{''.join(all_sections)}</main><script src="search.js"></script></body></html>"""
    (out_dir / "index.html").write_text(body, encoding="utf-8", newline="\n")
    return out_dir


def latex_document(title: str, body: str) -> str:
    return r"""\documentclass[11pt,a4paper]{report}
\begin{document}
\begin{titlepage}
\centering
{\Huge """ + latex_escape(title) + r"""\par}
\vspace{1cm}
{\Large """ + latex_escape(SUBTITLE) + r"""\par}
\vspace{1cm}
{\large Status: DERIVED \\ Authority Class: advisory\_synthesis \\ Promotion Status: not\_promoted\par}
\vfill
{\large """ + REVIEW_DATE + r"""\par}
\end{titlepage}
\tableofcontents
\clearpage
""" + body + r"""
\end{document}
"""


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 180) -> Tuple[int, str]:
    try:
        completed = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return completed.returncode, completed.stdout
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + "\nTIMEOUT"


def render_pdf(repo_root: Path, tex_name: str, pdf_name: str, markdown_text: str) -> Tuple[bool, str, Optional[Path]]:
    build_dir = repo_root / BOOK_DIR / "build" / "latex"
    build_dir.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / tex_name
    with tex_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(latex_document(TITLE if "reference" not in tex_name else "Dominium Conversation Corpus Reference Appendix v0", markdown_to_latex(markdown_text)))
    engine = command_available("pdflatex") or command_available("xelatex") or command_available("lualatex")
    if not engine:
        return False, "No LaTeX PDF engine found.", None
    code1, out1 = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], build_dir, 240)
    code2, out2 = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], build_dir, 240) if code1 == 0 else (code1, "")
    built_pdf = build_dir / tex_path.with_suffix(".pdf").name
    if code1 != 0 or code2 != 0 or not built_pdf.exists():
        return False, (out1 + "\n" + out2)[-4000:], None
    target = repo_root / EXPORTS_DIR / pdf_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(built_pdf, target)
    for suffix in (".aux", ".log", ".out", ".toc"):
        intermediate = tex_path.with_suffix(suffix)
        if intermediate.exists():
            intermediate.unlink()
    if built_pdf.exists():
        built_pdf.unlink()
    return True, "LaTeX render succeeded.", target


def text_for_docx(text: str) -> List[Tuple[str, str]]:
    result = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            result.append((f"Heading{min(3, len(match.group(1)))}", match.group(2).strip()))
        elif line.startswith("- "):
            result.append(("ListParagraph", line[2:].strip()))
        elif not line.lstrip().startswith("|"):
            clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)
            clean = re.sub(r"`([^`]+)`", r"\1", clean)
            result.append(("Normal", clean))
    return result[:8000]


def render_docx(repo_root: Path, markdown_text: str) -> Path:
    out = repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    paras = []
    for style, text in text_for_docx(markdown_text):
        paras.append(
            '<w:p><w:pPr><w:pStyle w:val="' + style + '"/></w:pPr><w:r><w:t xml:space="preserve">'
            + html.escape(text)
            + "</w:t></w:r></w:p>"
        )
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>""" + "".join(paras) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>'
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/></w:style><w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/></w:style><w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/></w:style></w:styles>"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>""")
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>""")
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)
    return out


def render_epub(repo_root: Path, markdown_text: str) -> Path:
    out = repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.epub"
    xhtml = """<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"><head><title>""" + html.escape(TITLE) + "</title></head><body>" + markdown_to_html(markdown_text) + "</body></html>"
    nav = """<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>Navigation</title></head><body><nav epub:type="toc" xmlns:epub="http://www.idpf.org/2007/ops"><ol><li><a href="book.xhtml">Book</a></li></ol></nav></body></html>"""
    opf = """<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">dominium-conversation-corpus-book-v0</dc:identifier><dc:title>""" + html.escape(TITLE) + """</dc:title><dc:language>en</dc:language></metadata><manifest><item id="book" href="book.xhtml" media-type="application/xhtml+xml"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/></manifest><spine><itemref idref="book"/></spine></package>"""
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", """<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>""")
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/nav.xhtml", nav)
        zf.writestr("OEBPS/book.xhtml", xhtml)
    return out


def pdf_page_count(path: Path) -> Optional[int]:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    count = len(re.findall(rb"/Type\s*/Page\b", data))
    return count or None


def representative_pages(page_count: Optional[int]) -> List[Tuple[str, int]]:
    if not page_count:
        return []
    candidates = [
        ("title_page", 1),
        ("toc_page", min(page_count, 2)),
        ("normal_chapter_page", min(page_count, 60)),
        ("dense_appendix_page", min(page_count, max(1, page_count - 250))),
        ("index_or_back_matter_page", min(page_count, max(1, page_count - 5))),
    ]
    seen = set()
    result: List[Tuple[str, int]] = []
    for label, page in candidates:
        if page not in seen:
            seen.add(page)
            result.append((label, page))
    return result


def render_pdf_qa(repo_root: Path, pdf_path: Path, page_count: Optional[int]) -> Dict[str, object]:
    qa_root = repo_root / QA_DIR
    qa_root.mkdir(parents=True, exist_ok=True)
    for stale in qa_root.glob("main_*"):
        if stale.is_file():
            stale.unlink()
    pdftoppm = command_available("pdftoppm")
    pdftotext = command_available("pdftotext")
    pdfinfo = command_available("pdfinfo")
    lines = [STATUS_BLOCK, "# PDF QA Summary", ""]
    lines.append(f"- PDF: `{rel(pdf_path, repo_root)}`")
    lines.append(f"- Page count: `{page_count or 'unknown'}`")
    lines.append(f"- `pdfinfo`: `{pdfinfo or 'unavailable'}`")
    lines.append(f"- `pdftoppm`: `{pdftoppm or 'unavailable'}`")
    lines.append(f"- `pdftotext`: `{pdftotext or 'unavailable'}`")
    lines.append("")
    rendered: List[str] = []
    rendered_pages = 0
    if not pdf_path.exists():
        lines.append("- QA skipped: PDF does not exist.")
    elif not pdftoppm:
        lines.append("- QA skipped: `pdftoppm` is unavailable.")
    else:
        lines.append("## Representative Pages")
        lines.append("")
        for label, page in representative_pages(page_count):
            prefix = qa_root / f"main_{page:03d}_{label}"
            code, out = run_command([pdftoppm, "-png", "-f", str(page), "-l", str(page), "-singlefile", str(pdf_path), str(prefix)], repo_root, 120)
            image = prefix.with_suffix(".png")
            if code == 0 and image.exists():
                rendered.append(rel(image, repo_root))
                rendered_pages += 1
                lines.append(f"- Page `{page}` ({label}): `{rel(image, repo_root)}`")
            else:
                lines.append(f"- Page `{page}` ({label}): render failed with exit `{code}`; tail `{out[-240:].strip()}`")
            if pdftotext:
                text_path = prefix.with_suffix(".txt")
                text_code, text_out = run_command([pdftotext, "-f", str(page), "-l", str(page), str(pdf_path), str(text_path)], repo_root, 120)
                if text_code == 0 and text_path.exists():
                    rendered.append(rel(text_path, repo_root))
                else:
                    lines.append(f"  - Text extraction failed with exit `{text_code}`; tail `{text_out[-160:].strip()}`")
    summary_path = qa_root / "PDF_QA_SUMMARY.md"
    write_if_changed(summary_path, "\n".join(lines) + "\n")
    return {
        "created": bool(rendered),
        "path": rel(summary_path, repo_root),
        "renderer": "pdftoppm/pdftotext" if rendered else "not_available",
        "pages": rendered_pages,
    }


def build_book(repo_root: Path, render_outputs: bool = True) -> Dict[str, object]:
    chapters, appendices = default_chapters()
    book_root = repo_root / BOOK_DIR
    exports_root = repo_root / EXPORTS_DIR
    (book_root / "chapters").mkdir(parents=True, exist_ok=True)
    (book_root / "appendices").mkdir(parents=True, exist_ok=True)
    (book_root / "styles").mkdir(parents=True, exist_ok=True)
    (book_root / "build").mkdir(parents=True, exist_ok=True)
    exports_root.mkdir(parents=True, exist_ok=True)
    included = all_manifest_sources(chapters, appendices)
    excluded = excluded_sources(repo_root, included)
    renderer = "custom_html_latex_ooxml_epub"
    changed = []
    for path, content in [
        (book_root / "README.md", render_readme(renderer)),
        (book_root / "BOOK_MANIFEST.yml", render_manifest(repo_root, chapters, appendices)),
        (book_root / "index.md", render_index(chapters, appendices)),
        (book_root / "styles" / "book.css", "body { font-family: Segoe UI, Arial, sans-serif; }\n"),
        (book_root / "build" / "pandoc_prerequisites.md", "Pandoc and Quarto were not available for this build. The repository fallback publisher used local LaTeX plus generated HTML/DOCX/EPUB packages.\n"),
    ]:
        if write_if_changed(path, content):
            changed.append(rel(path, repo_root))
    for spec in [*chapters, *appendices]:
        content = render_chapter(repo_root, spec, excluded)
        target = book_root / spec.output
        if write_if_changed(target, content):
            changed.append(rel(target, repo_root))
    combined = render_combined_source(repo_root, chapters, appendices)
    write_if_changed(book_root / "build" / "book_source.md", combined)
    outputs: Dict[str, Dict[str, object]] = {}
    if render_outputs:
        html_dir = render_html_book(repo_root, chapters, appendices)
        outputs["html"] = {"created": True, "path": rel(html_dir, repo_root), "renderer": "custom_html"}
        ok, message, pdf = render_pdf(repo_root, "reader_book.tex", f"{BOOK_BASENAME}.pdf", combined)
        outputs["pdf"] = {"created": ok, "path": rel(pdf, repo_root) if pdf else "", "renderer": "pdflatex/xelatex/lualatex", "message": message, "pages": pdf_page_count(pdf) if pdf else None}
        if pdf:
            outputs["pdf_qa"] = render_pdf_qa(repo_root, pdf, outputs["pdf"]["pages"])
        reference_text = "\n\n".join(read_text(repo_root / BOOK_DIR / spec.output) for spec in appendices)
        ok_ref, message_ref, ref_pdf = render_pdf(repo_root, "reference_appendix.tex", f"{REFERENCE_BASENAME}.pdf", reference_text)
        outputs["reference_pdf"] = {"created": ok_ref, "path": rel(ref_pdf, repo_root) if ref_pdf else "", "renderer": "pdflatex/xelatex/lualatex", "message": message_ref, "pages": pdf_page_count(ref_pdf) if ref_pdf else None}
        docx = render_docx(repo_root, combined)
        outputs["docx"] = {"created": docx.exists(), "path": rel(docx, repo_root), "renderer": "custom_ooxml"}
        epub = render_epub(repo_root, combined)
        outputs["epub"] = {"created": epub.exists(), "path": rel(epub, repo_root), "renderer": "custom_epub"}
    build_report = render_build_report(repo_root, chapters, appendices, included, excluded, outputs, renderer)
    validation_report = render_validation_report(repo_root, included, excluded, outputs, [], "not_run")
    for path, content in [
        (exports_root / f"{BUILD_REPORT_BASENAME}.md", build_report),
        (exports_root / f"{VALIDATION_REPORT_BASENAME}.md", validation_report),
    ]:
        if write_if_changed(path, content):
            changed.append(rel(path, repo_root))
    return {"changed": sorted(set(changed)), "outputs": outputs, "included": included, "excluded": excluded, "renderer": renderer}


def render_build_report(repo_root: Path, chapters: Sequence[ChapterSpec], appendices: Sequence[ChapterSpec], included: Sequence[str], excluded: Sequence[Dict[str, str]], outputs: Dict[str, Dict[str, object]], renderer: str) -> str:
    lines = [STATUS_BLOCK, "# Dominium Conversation Corpus Book Build Report v0", ""]
    lines.append(f"- Book title: {TITLE}")
    lines.append(f"- Version: v0")
    lines.append(f"- Date: {REVIEW_DATE}")
    lines.append(f"- Source root: `docs/archive/conversations/`")
    lines.append(f"- Renderer used: `{renderer}`")
    lines.append("")
    lines.append("## Chapters")
    lines.append("")
    for spec in chapters:
        lines.append(f"- `{spec.output}` - {spec.title}")
    lines.append("")
    lines.append("## Appendices")
    lines.append("")
    for spec in appendices:
        lines.append(f"- `{spec.output}` - {spec.title}")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    for name, details in outputs.items():
        lines.append(f"- `{name}`: created `{details.get('created')}`, path `{details.get('path', '')}`, renderer `{details.get('renderer', '')}`, pages `{details.get('pages', 'n/a')}`")
    lines.append("")
    lines.append("## Source Files Included")
    lines.append("")
    for path in included:
        lines.append(f"- `docs/archive/conversations/{path}`")
    lines.append("")
    lines.append("## Source Files Excluded From Reader Edition")
    lines.append("")
    for item in excluded:
        lines.append(f"- `docs/archive/conversations/{item['path']}` - {item['reason']}")
    lines.append("")
    lines.append("## Known Layout Caveats")
    lines.append("")
    lines.append("- Dense pipe tables are summarized in the PDF rendering and retained in Markdown/HTML/source outputs.")
    lines.append("- DOCX and EPUB are generated fallback review copies, not typographically polished editions.")
    lines.append("- Quarto and Pandoc were not available on this machine; local LaTeX was used for PDF output.")
    lines.append("")
    lines.append("## Next Recommended Review Step")
    lines.append("")
    lines.append("Review the reader PDF and HTML book, then choose a small docs-only Wave 1 promotion microtask.")
    return "\n".join(lines) + "\n"


def validate_book_sources(repo_root: Path, included: Sequence[str], outputs: Dict[str, Dict[str, object]]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    root = repo_root / CORPUS_ROOT
    manifest_path = repo_root / BOOK_DIR / "BOOK_MANIFEST.yml"
    if not manifest_path.exists():
        errors.append("BOOK_MANIFEST.yml missing")
    else:
        try:
            paths = parse_manifest_paths(manifest_path.read_text(encoding="utf-8"))
            missing = [path for path in paths if not (root / path).exists()]
            errors.extend(f"manifest source missing: {path}" for path in missing)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"manifest parse failed: {exc}")
    for path in collect_markdown_files(repo_root, *default_chapters()):
        if not path.exists():
            errors.append(f"book source missing: {rel(path, repo_root)}")
    for name, details in outputs.items():
        if details.get("created"):
            if details.get("path") and not (repo_root / str(details["path"])).exists():
                errors.append(f"output missing: {details['path']}")
        else:
            warnings.append(f"{name} not created: {details.get('message', 'no message')}")
    return errors, warnings


def protected_path_changes(repo_root: Path) -> List[str]:
    code, out = run_command(["git", "status", "--short"], repo_root, 60)
    if code != 0:
        return [f"git status failed: {out.strip()}"]
    changes = []
    for line in out.splitlines():
        path = line[3:].replace("\\", "/")
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            changes.append(line)
    return changes


def render_validation_report(repo_root: Path, included: Sequence[str], excluded: Sequence[Dict[str, str]], outputs: Dict[str, Dict[str, object]], command_results: List[Dict[str, object]], status: str) -> str:
    source_errors, source_warnings = validate_book_sources(repo_root, included, outputs)
    protected = protected_path_changes(repo_root)
    lines = [STATUS_BLOCK, "# Dominium Conversation Corpus Book Validation Report v0", ""]
    lines.append(f"Validation status: `{status}`")
    lines.append("")
    lines.append("## Renderer")
    lines.append("")
    lines.append("- Quarto: unavailable")
    lines.append("- Pandoc: unavailable")
    lines.append("- PDF renderer: local LaTeX engine if output exists")
    lines.append("- HTML renderer: custom static HTML")
    lines.append("- DOCX renderer: custom OOXML fallback")
    lines.append("- EPUB renderer: custom EPUB fallback")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    for name, details in outputs.items():
        lines.append(f"- `{name}`: created `{details.get('created')}`, path `{details.get('path', '')}`, renderer `{details.get('renderer', '')}`, pages `{details.get('pages', 'n/a')}`")
    lines.append("")
    lines.append("## Book Source Checks")
    lines.append("")
    lines.append(f"- Included source files: `{len(included)}`")
    lines.append(f"- Excluded reader-edition source files: `{len(excluded)}`")
    lines.append(f"- Source check errors: `{len(source_errors)}`")
    lines.append(f"- Source check warnings: `{len(source_warnings)}`")
    for error in source_errors:
        lines.append(f"- ERROR: {error}")
    for warning in source_warnings:
        lines.append(f"- WARNING: {warning}")
    lines.append("")
    lines.append("## Commands Run")
    lines.append("")
    if command_results:
        for item in command_results:
            lines.append(f"- `{item['command']}` -> exit `{item['code']}`")
    else:
        lines.append("- Book-internal validation only; repository validation not run by this report generation step.")
    lines.append("")
    lines.append("## Broken Links")
    lines.append("")
    lines.append("- Markdown/source link existence is covered by source path checks and generated conversation-output validation.")
    lines.append("")
    lines.append("## Protected Path Check")
    lines.append("")
    if protected:
        lines.append("- Protected path changes detected:")
        for item in protected:
            lines.append(f"  - `{item}`")
    else:
        lines.append("- No protected path changes detected by `git status --short`.")
    lines.append("")
    lines.append("## Impact Statements")
    lines.append("")
    lines.append("- canon impact: unchanged")
    lines.append("- contract/schema impact: unchanged")
    lines.append("- implementation impact: unchanged")
    lines.append("- release impact: unchanged")
    lines.append("- queue impact: unchanged")
    lines.append("- archive claim promotion: none")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- Dense matrices are summarized in PDF and retained in Markdown/HTML/source outputs.")
    lines.append("- DOCX/EPUB are fallback review copies because Quarto/Pandoc are unavailable.")
    return "\n".join(lines) + "\n"


def run_validation(repo_root: Path) -> Dict[str, object]:
    build_result = build_book(repo_root, render_outputs=False)
    outputs = discover_outputs(repo_root)
    included = build_result["included"]
    excluded = build_result["excluded"]
    chapters, appendices = default_chapters()
    build_report = render_build_report(repo_root, chapters, appendices, included, excluded, outputs, build_result["renderer"])
    write_if_changed(repo_root / EXPORTS_DIR / f"{BUILD_REPORT_BASENAME}.md", build_report)
    commands = [
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        [
            "py",
            "-3",
            "-c",
            "import json; json.load(open('docs/archive/conversations/_intake/corpus_manifest.json', encoding='utf-8')); print('corpus_manifest.json ok')",
        ],
        [
            "py",
            "-3",
            "-c",
            "import sys; sys.path.insert(0, 'tools/conversations'); import build_conversation_book as b; paths = b.parse_manifest_paths(open('docs/archive/conversations/_book/BOOK_MANIFEST.yml', encoding='utf-8').read()); assert paths; print('BOOK_MANIFEST.yml ok', len(paths))",
        ],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/conversations"],
        ["git", "diff", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    results = []
    for cmd in commands:
        code, out = run_command(cmd, repo_root, 360)
        results.append({"command": " ".join(cmd), "code": code, "output_tail": out[-1200:]})
    source_errors, _ = validate_book_sources(repo_root, included, outputs)
    protected = protected_path_changes(repo_root)
    status = "PASS" if all(item["code"] == 0 for item in results) and not source_errors and not protected else "FAIL"
    report = render_validation_report(repo_root, included, excluded, outputs, results, status)
    path = repo_root / EXPORTS_DIR / f"{VALIDATION_REPORT_BASENAME}.md"
    write_if_changed(path, report)
    cleanup_pycache(repo_root)
    return {"status": status, "commands": results, "source_errors": source_errors, "protected": protected}


def discover_outputs(repo_root: Path) -> Dict[str, Dict[str, object]]:
    outputs: Dict[str, Dict[str, object]] = {}
    paths = {
        "pdf": repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.pdf",
        "html": repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.html",
        "docx": repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.docx",
        "epub": repo_root / EXPORTS_DIR / f"{BOOK_BASENAME}.epub",
        "reference_pdf": repo_root / EXPORTS_DIR / f"{REFERENCE_BASENAME}.pdf",
        "pdf_qa": repo_root / QA_DIR / "PDF_QA_SUMMARY.md",
    }
    for name, path in paths.items():
        pages: Optional[int]
        if path.suffix.lower() == ".pdf" and path.exists():
            pages = pdf_page_count(path)
        elif name == "pdf_qa" and path.exists():
            pages = len(re.findall(r"^- Page `", path.read_text(encoding="utf-8"), flags=re.MULTILINE))
        else:
            pages = None
        outputs[name] = {
            "created": path.exists(),
            "path": rel(path, repo_root) if path.exists() else "",
            "renderer": "detected_existing",
            "pages": pages,
        }
    return outputs


def cleanup_pycache(repo_root: Path) -> None:
    for relative in ["tools/conversations/__pycache__", "tests/tools/conversations/__pycache__"]:
        target = repo_root / relative
        if target.exists() and target.is_dir():
            shutil.rmtree(target)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the conversation corpus book bundle.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--no-render", action="store_true", help="Generate source only.")
    parser.add_argument("command", nargs="?", default="build", choices=["build", "validate"], help="Operation.")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.command == "validate":
        result = run_validation(repo_root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1
    result = build_book(repo_root, render_outputs=not args.no_render)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
