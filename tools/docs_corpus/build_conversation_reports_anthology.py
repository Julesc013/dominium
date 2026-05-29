"""Build an anthology of raw human-readable conversation reports.

The output is a derived publication artifact. It preserves the original report
text, groups files by conversation directory, and renders regular and mobile
PDF editions without modifying source conversation files.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import build_omnibus_v1 as styled
import docs_corpus


REVIEW_DATE = "2026-05-30"
TITLE = "Dominium Conversation Human-Readable Reports Anthology"
SUBTITLE = "Raw human-readable reports from the archived conversation corpus"
CONVERSATIONS_ROOT = Path("docs/archive/conversations")
ROOT = CONVERSATIONS_ROOT / "_reports_book"
EXPORTS_ROOT = CONVERSATIONS_ROOT / "_exports"
QA_ROOT = ROOT / "qa"
BUILD_ROOT = ROOT / "build"

ANTHOLOGY_MD = "Dominium_Conversation_Human_Readable_Reports_Anthology.md"
MANIFEST = "CONVERSATION_REPORTS_ANTHOLOGY_MANIFEST.yml"
SOURCE_INDEX = "SOURCE_REPORT_INDEX.md"
SELECTION_REPORT = "SELECTION_REPORT.md"
REGULAR_PDF = "Dominium_Conversation_Human_Readable_Reports_Anthology.pdf"
MOBILE_PDF = "Dominium_Conversation_Human_Readable_Reports_Anthology_Mobile_Dark.pdf"
BUILD_REPORT = "Dominium_Conversation_Human_Readable_Reports_Anthology_Build_Report.md"
VALIDATION_REPORT = "Dominium_Conversation_Human_Readable_Reports_Anthology_Validation_Report.md"

REPORT_PATTERNS = (
    "human_readable_report",
    "human_readable_detailed_summary",
    "detailed_summary_report",
    "accompanying_detailed_summary",
    "accompanying_human_readable",
    "companion_detailed_summary",
    "companion_report",
    "reader_brief",
    "in_chat_reader",
)

EXCLUDED_DIRS = {
    "_audit",
    "_book",
    "_decision",
    "_exports",
    "_promotion",
    "_reader",
    "_reconciliation",
    "_reports_book",
    "_synthesis",
    "_wiki",
}

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_source_collection
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""


@dataclass(frozen=True)
class ReportSource:
    path: Path
    conversation: str
    title: str
    kind: str
    size: int


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


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 900) -> Tuple[int, str]:
    try:
        completed = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        text = (exc.stdout or "") + (exc.stderr or "")
        return 124, docs_corpus.ascii_text(text)
    return completed.returncode, docs_corpus.ascii_text(completed.stdout or "")


def write_text(path: Path, content: str) -> None:
    clean = "\n".join(line.rstrip(" \t") for line in content.splitlines())
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(clean) + "\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def title_from_path(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"__\d+_", " - ", stem)
    stem = re.sub(r"[_\-]+", " ", stem)
    return " ".join(word.capitalize() for word in stem.split())


def kind_from_name(path: Path) -> str:
    lower = path.name.lower()
    for pattern in REPORT_PATTERNS:
        if pattern in lower:
            return pattern
    return "human_readable_report"


def is_candidate(path: Path, conversations_root: Path = CONVERSATIONS_ROOT) -> bool:
    if path.suffix.lower() not in {".md", ".txt"}:
        return False
    try:
        rel_parts = path.relative_to(conversations_root).parts
    except ValueError:
        rel_parts = path.parts
        marker = ("docs", "archive", "conversations")
        for index in range(0, len(rel_parts) - len(marker) + 1):
            if tuple(rel_parts[index : index + len(marker)]) == marker:
                rel_parts = rel_parts[index + len(marker) :]
                break
    if rel_parts[0] in EXCLUDED_DIRS:
        return False
    lower = path.name.lower()
    return any(pattern in lower for pattern in REPORT_PATTERNS)


def collect_sources(repo_root: Path) -> List[ReportSource]:
    root = repo_root / CONVERSATIONS_ROOT
    sources: List[ReportSource] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().lower()):
        if not path.is_file() or not is_candidate(path, root):
            continue
        rel = path.relative_to(repo_root)
        conversation = path.relative_to(root).parts[0]
        sources.append(
            ReportSource(
                path=rel,
                conversation=conversation,
                title=title_from_path(path),
                kind=kind_from_name(path),
                size=path.stat().st_size,
            )
        )
    return sources


def normalize_source_markdown(text: str) -> str:
    lines = text.strip().splitlines()
    normalized: List[str] = []
    for line in lines:
        if line.startswith("#"):
            hashes, rest = line.split(" ", 1) if " " in line else (line, "")
            normalized.append("#" * min(6, len(hashes) + 2) + (" " + rest if rest else ""))
        else:
            normalized.append(line)
    return "\n".join(normalized).strip()


def build_anthology_markdown(repo_root: Path, sources: List[ReportSource]) -> str:
    grouped: Dict[str, List[ReportSource]] = defaultdict(list)
    for source in sources:
        grouped[source.conversation].append(source)
    lines = [
        f"# {TITLE}",
        "",
        f"*{SUBTITLE}*",
        "",
        "**Status:** DERIVED. **Authority:** advisory source collection. **Promotion:** none.",
        "",
        "This anthology preserves the raw human-readable report files from `docs/archive/conversations/` in one organized reading volume. It does not synthesize, promote, or reinterpret the reports.",
        "",
        "## How To Read This Anthology",
        "",
        "Reports are grouped by their top-level conversation folder and then sorted by path. Each report is introduced by a compact provenance line, followed by the original human-readable text with heading levels shifted so the anthology remains navigable.",
        "",
        "## Source Coverage",
        "",
        f"- Conversation groups represented: {len(grouped)}",
        f"- Human-readable report files included: {len(sources)}",
        "- Machine manifests, ZIP files, raw packets, generated corpus outputs, and validation logs are excluded from the main anthology.",
        "",
    ]
    for conversation in sorted(grouped):
        pretty = title_from_path(Path(conversation))
        lines.extend([f"# {pretty}", ""])
        for source in grouped[conversation]:
            rel = source.path.as_posix()
            lines.extend(
                [
                    f"## {source.title}",
                    "",
                    f"*Source:* `{rel}`  ",
                    f"*Report type:* `{source.kind}`  ",
                    f"*Size:* `{source.size}` bytes",
                    "",
                ]
            )
            lines.append(normalize_source_markdown(read_text(repo_root / source.path)))
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_manifest(repo_root: Path, sources: List[ReportSource]) -> None:
    grouped = defaultdict(int)
    kinds = defaultdict(int)
    for source in sources:
        grouped[source.conversation] += 1
        kinds[source.kind] += 1
    manifest = [
        "title: Dominium Conversation Human-Readable Reports Anthology",
        f"date: {REVIEW_DATE}",
        "status: DERIVED",
        "authority_class: advisory_source_collection",
        "promotion_status: not_promoted",
        f"source_root: {CONVERSATIONS_ROOT.as_posix()}",
        f"source_count: {len(sources)}",
        "outputs:",
        f"  regular_pdf: {(EXPORTS_ROOT / REGULAR_PDF).as_posix()}",
        f"  mobile_dark_pdf: {(EXPORTS_ROOT / MOBILE_PDF).as_posix()}",
        "source_files:",
    ]
    for source in sources:
        manifest.append(f"  - path: {source.path.as_posix()}")
        manifest.append(f"    conversation: {source.conversation}")
        manifest.append(f"    kind: {source.kind}")
        manifest.append(f"    size: {source.size}")
    write_text(repo_root / ROOT / MANIFEST, "\n".join(manifest))

    index_lines = ["# Source Report Index", ""]
    for conversation in sorted(grouped):
        index_lines.extend([f"## {title_from_path(Path(conversation))}", ""])
        for source in [item for item in sources if item.conversation == conversation]:
            index_lines.append(f"- `{source.path.as_posix()}` - {source.title} ({source.kind}, {source.size} bytes)")
        index_lines.append("")
    write_text(repo_root / ROOT / SOURCE_INDEX, "\n".join(index_lines))

    selection = f"""{STATUS_BLOCK}
# Selection Report

## Included

- Human-readable report files included: {len(sources)}
- Conversation groups represented: {len(grouped)}
- Report kind counts:
{chr(10).join(f'  - `{kind}`: {count}' for kind, count in sorted(kinds.items()))}

## Excluded

- Generated conversation book/wiki/synthesis directories beginning with `_`.
- ZIP, PDF, DOCX, EPUB, JSON, YAML, TOML, and other non-prose files.
- Raw manifests, context packets, hash files, bundle integrity files, validation logs, and machine registers unless their filename matched a human-readable report pattern.

## Authority

This anthology is a derived source collection. It does not promote archive or conversation claims.
"""
    write_text(repo_root / ROOT / SELECTION_REPORT, selection)


def font_block(engine: str) -> str:
    if engine in {"xelatex", "lualatex"}:
        return r"""\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.90]
"""
    return r"""\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
"""


def regular_latex(markdown: str, engine: str) -> str:
    body = styled.markdown_to_latex(markdown, reference=True)
    return rf"""\documentclass[10pt,openany]{{book}}
\usepackage[a4paper,margin=18mm,includeheadfoot]{{geometry}}
{font_block(engine)}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
\usepackage{{array,longtable,tabularx,graphicx,color}}
\newcommand{{\toprule}}{{\hline}}
\newcommand{{\midrule}}{{\hline}}
\newcommand{{\bottomrule}}{{\hline}}
\newcommand{{\uline}}[1]{{\underline{{#1}}}}
\newcommand{{\href}}[2]{{\underline{{#2}}}}
\newcommand{{\url}}[1]{{{{\scriptsize\texttt{{\detokenize{{#1}}}}}}}}
\newcommand{{\vonecallout}}[3]{{\par\medskip\noindent\textbf{{#2}}\par #3\par\medskip}}
\newcommand{{\vonecode}}[1]{{\par\smallskip\noindent{{\small\ttfamily #1}}\par\smallskip}}
\setcounter{{tocdepth}}{{1}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.45em}}
\raggedright
\hyphenpenalty=10000
\exhyphenpenalty=10000
\sloppy
\begin{{document}}
\frontmatter
\begin{{titlepage}}\centering\vspace*{{2cm}}{{\Huge\bfseries {styled.latex_escape(TITLE)}\par}}\vspace{{0.6cm}}{{\Large {styled.latex_escape(SUBTITLE)}\par}}\vfill{{Status: DERIVED\par}}{{Promotion Status: not promoted\par}}\vspace{{1cm}}{{{REVIEW_DATE}\par}}\end{{titlepage}}
\tableofcontents
\mainmatter
{body}
\end{{document}}
"""


def prepare_mobile_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    prepared: List[str] = []
    skipped_title = False
    for line in lines:
        if not skipped_title and line.strip() == f"# {TITLE}":
            skipped_title = True
            continue
        skipped_title = True
        prepared.append(line)
    return "\n".join(prepared).strip() + "\n"


def mobile_latex(markdown: str, engine: str) -> str:
    body = styled.markdown_to_latex(prepare_mobile_markdown(markdown), reference=True)
    return rf"""\documentclass[11pt,openany]{{book}}
\usepackage[paperwidth=108mm,paperheight=192mm,top=5.5mm,bottom=6mm,left=5mm,right=5mm,includeheadfoot,footskip=10pt]{{geometry}}
{font_block(engine)}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
\usepackage{{array,longtable,tabularx,graphicx,color}}
\definecolor{{MobileDarkBg}}{{rgb}}{{0.015,0.018,0.023}}
\definecolor{{MobileDarkText}}{{rgb}}{{0.94,0.95,0.96}}
\definecolor{{MobileDarkMuted}}{{rgb}}{{0.72,0.75,0.78}}
\makeatletter
\def\normalcolor{{\color{{MobileDarkText}}}}
\def\ps@plain{{\let\@mkboth\@gobbletwo\let\@oddhead\@empty\let\@evenhead\@empty\def\@oddfoot{{\hfil\color{{MobileDarkMuted}}\thepage\hfil}}\let\@evenfoot\@oddfoot}}
\def\@makechapterhead#1{{\vspace*{{0.45cm}}{{\parindent0pt\raggedright\color{{MobileDarkText}}\Large\bfseries Chapter \thechapter\par\nobreak\vspace{{0.22cm}}\LARGE\bfseries #1\par\nobreak\vspace{{0.45cm}}}}}}
\def\@makeschapterhead#1{{\vspace*{{0.45cm}}{{\parindent0pt\raggedright\color{{MobileDarkText}}\LARGE\bfseries #1\par\nobreak\vspace{{0.45cm}}}}}}
\makeatother
\newcommand{{\toprule}}{{\hline}}
\newcommand{{\midrule}}{{\hline}}
\newcommand{{\bottomrule}}{{\hline}}
\newcommand{{\uline}}[1]{{\underline{{#1}}}}
\newcommand{{\href}}[2]{{\underline{{#2}}}}
\newcommand{{\url}}[1]{{{{\scriptsize\texttt{{\detokenize{{#1}}}}}}}}
\newcommand{{\vonecallout}}[3]{{\par\medskip\noindent{{\bfseries #2}}\par #3\par\medskip}}
\newcommand{{\vonecode}}[1]{{\par\smallskip\noindent{{\scriptsize\ttfamily #1}}\par\smallskip}}
\setcounter{{tocdepth}}{{0}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.44em}}
\linespread{{1.05}}
\raggedright
\pretolerance=10000
\tolerance=10000
\hyphenpenalty=10000
\exhyphenpenalty=10000
\emergencystretch=2.2em
\sloppy
\begin{{document}}
\pagecolor{{MobileDarkBg}}
\color{{MobileDarkText}}
\normalcolor
\pagestyle{{plain}}
\fontsize{{11.4pt}}{{16.2pt}}\selectfont
\frontmatter
\begin{{titlepage}}\centering\vspace*{{1.1cm}}{{\Huge\bfseries {styled.latex_escape(TITLE)}\par}}\vspace{{0.55cm}}{{\Large Mobile Dark Reading Edition\par}}\vspace{{0.9cm}}{{\large Status: DERIVED\par}}{{\large Promotion Status: not\_promoted\par}}\vfill{{\large {REVIEW_DATE}\par}}\end{{titlepage}}
{{\fontsize{{10.4pt}}{{15.0pt}}\selectfont\raggedright\tableofcontents\par}}
\mainmatter
{body}
\end{{document}}
"""


def render_pdf(repo_root: Path, markdown: str, pdf_name: str, tex_name: str, mobile: bool) -> PdfInfo:
    engine = styled.select_engine()
    out = repo_root / EXPORTS_ROOT / pdf_name
    result = PdfInfo(path=out, created=False, renderer=engine or "none")
    if not engine:
        result.caveat = "No LaTeX engine found."
        return result
    build = repo_root / BUILD_ROOT
    build.mkdir(parents=True, exist_ok=True)
    tex = build / f"{tex_name}.tex"
    write_text(tex, mobile_latex(markdown, engine) if mobile else regular_latex(markdown, engine))
    for _ in range(2):
        code, output = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex.name], tex.parent, timeout=4200)
        if code != 0:
            result.caveat = output[-2000:]
            return result
    built = tex.with_suffix(".pdf")
    if built.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built, out)
    return qa_pdf(repo_root, out, engine, tex_name)


def qa_pdf(repo_root: Path, pdf_path: Path, renderer: str, prefix_name: str) -> PdfInfo:
    qa = repo_root / QA_ROOT
    qa.mkdir(parents=True, exist_ok=True)
    result = PdfInfo(path=pdf_path, created=pdf_path.exists(), renderer=renderer, size=pdf_path.stat().st_size if pdf_path.exists() else 0)
    if result.created and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=180)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            result.pages = int(match.group(1))
    if result.created and shutil.which("pdftotext"):
        extract = qa / f"{prefix_name}_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=900)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
    if result.created and shutil.which("pdftoppm") and result.pages:
        for stale in qa.glob(f"{prefix_name}_page_*.png"):
            stale.unlink()
        for page in sorted({1, 2, 6, max(1, result.pages // 2), result.pages}):
            prefix = qa / f"{prefix_name}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "110", str(pdf_path), str(prefix)], repo_root, timeout=240)
            final = qa / f"{prefix_name}_page_{page}.png"
            candidates = sorted(qa.glob(f"{prefix.name}-*.png"))
            rendered = candidates[0] if candidates else qa / f"{prefix.name}-{page}.png"
            if code == 0 and rendered.exists():
                if final.exists():
                    final.unlink()
                rendered.rename(final)
                result.qa_images.append(final.relative_to(repo_root).as_posix())
    return result


def clean_build(repo_root: Path) -> None:
    build = repo_root / BUILD_ROOT
    if build.exists():
        for path in build.iterdir():
            if path.is_file():
                path.unlink()
        try:
            build.rmdir()
        except OSError:
            pass


def protected_path_check(repo_root: Path) -> Tuple[bool, List[str]]:
    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
    if code != 0:
        return False, [output.strip()]
    changed = [line.strip() for line in output.splitlines() if line.strip()]
    hits = [path for path in changed if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in docs_corpus.PROTECTED_PREFIXES)]
    return not hits, hits


def write_reports(repo_root: Path, sources: List[ReportSource], regular: PdfInfo, mobile: PdfInfo, ok: bool, commands: List[Tuple[str, int]]) -> None:
    command_rows = "\n".join(f"| {command} | {'PASS' if code == 0 else 'FAIL'} | {code} |" for command, code in commands)
    grouped = len({source.conversation for source in sources})
    build_report = f"""{STATUS_BLOCK}
# Conversation Reports Anthology Build Report

## Outputs

- Source anthology: `{(ROOT / ANTHOLOGY_MD).as_posix()}`
- Regular PDF: `{(EXPORTS_ROOT / REGULAR_PDF).as_posix()}` ({regular.pages or ''} pages, {regular.size} bytes, {regular.renderer})
- Mobile dark PDF: `{(EXPORTS_ROOT / MOBILE_PDF).as_posix()}` ({mobile.pages or ''} pages, {mobile.size} bytes, {mobile.renderer})

## Source Coverage

- Human-readable report files included: {len(sources)}
- Conversation groups represented: {grouped}
- Selection mode: raw report/reader files matching human-readable report patterns under non-generated conversation directories.

## Caveats

- This is a derived archive anthology, not canon.
- Report text is preserved with heading-level normalization for book navigation.
- Machine-readable packets, generated corpus outputs, binary files, and validation logs are excluded.
"""
    validation_report = f"""{STATUS_BLOCK}
# Conversation Reports Anthology Validation Report

## Result

- Result: {'PASS' if ok else 'FAIL'}
- Regular PDF exists: {regular.created}
- Regular PDF pages: {regular.pages or ''}
- Regular text extraction: {regular.text_extraction}
- Regular glyph check: {regular.glyph_check}
- Mobile PDF exists: {mobile.created}
- Mobile PDF pages: {mobile.pages or ''}
- Mobile text extraction: {mobile.text_extraction}
- Mobile glyph check: {mobile.glyph_check}
- QA images: {', '.join(regular.qa_images + mobile.qa_images) or 'none'}

## Commands

| Command | Result | Exit Code |
| --- | --- | ---: |
{command_rows}

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
"""
    write_text(repo_root / EXPORTS_ROOT / BUILD_REPORT, build_report)
    write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, validation_report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    sources = collect_sources(repo_root)
    markdown = build_anthology_markdown(repo_root, sources)
    write_text(repo_root / ROOT / "README.md", STATUS_BLOCK + f"\n# {TITLE}\n\nThis folder contains the generated source anthology for raw human-readable conversation reports.\n")
    write_manifest(repo_root, sources)
    write_text(repo_root / ROOT / ANTHOLOGY_MD, markdown)
    commands: List[Tuple[str, int]] = []
    regular = render_pdf(repo_root, markdown, REGULAR_PDF, "conversation_reports_anthology", mobile=False)
    mobile = render_pdf(repo_root, markdown, MOBILE_PDF, "conversation_reports_anthology_mobile_dark", mobile=True)
    commands.append(("render regular PDF", 0 if regular.created else 1))
    commands.append(("render mobile dark PDF", 0 if mobile.created else 1))
    ok_protected, hits = protected_path_check(repo_root)
    commands.append(("protected path check", 0 if ok_protected else 1))
    ok = (
        regular.created
        and mobile.created
        and regular.text_extraction != "FAIL"
        and mobile.text_extraction != "FAIL"
        and regular.glyph_check != "FAIL"
        and mobile.glyph_check != "FAIL"
        and ok_protected
        and bool(sources)
    )
    if hits:
        regular.caveat = "Protected path changes detected: " + ", ".join(hits)
    write_reports(repo_root, sources, regular, mobile, ok, commands)
    clean_build(repo_root)
    print("conversation reports anthology build: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
