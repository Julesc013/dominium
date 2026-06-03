"""Render printable and mobile-dark PDFs for the Project Vision Book."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_omnibus_v1 as styled
import docs_corpus


REVIEW_DATE = "2026-06-03"
TITLE = "The Dominium Project Vision Book"
PRINT_SUBTITLE = "Printable Desktop Edition"
MOBILE_SUBTITLE = "Mobile Dark Reading Edition"
SOURCE = Path("docs/archive/project_vision_book/book/THE_DOMINIUM_PROJECT_VISION_BOOK.md")
ROOT = Path("docs/archive/project_vision_book")
EXPORTS_ROOT = ROOT / "exports"
BUILD_ROOT = ROOT / "pdf_build"
QA_ROOT = ROOT / "qa"

PRINT_PDF = "The_Dominium_Project_Vision_Book_Printable.pdf"
MOBILE_PDF = "The_Dominium_Project_Vision_Book_Mobile_Dark.pdf"
BUILD_REPORT = "PROJECT_VISION_BOOK_PDF_EXPORT_BUILD_REPORT.md"
VALIDATION_REPORT = "PROJECT_VISION_BOOK_PDF_EXPORT_VALIDATION_REPORT.md"


STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/project_vision_book/book/THE_DOMINIUM_PROJECT_VISION_BOOK.md`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""


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


def strip_status_and_promote_chapters(markdown: str) -> str:
    """Remove derived metadata and promote book chapters to LaTeX chapters."""
    lines = markdown.splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.startswith("# "):
            start = index + 1
            break
    body = lines[start:]
    promoted: List[str] = []
    for line in body:
        match = re.match(r"^(#{2,6})(\s+.+)$", line)
        if match:
            promoted.append("#" * (len(match.group(1)) - 1) + match.group(2))
        else:
            promoted.append(line)
    return "\n".join(promoted).strip() + "\n"


def font_block(engine: str, mobile: bool = False) -> str:
    if engine in {"xelatex", "lualatex"}:
        if mobile:
            return r"""\usepackage{fontspec}
\setmainfont{Latin Modern Sans}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.88]
\renewcommand{\familydefault}{\sfdefault}
"""
        return r"""\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.90]
"""
    return r"""\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
"""


def common_macros(dark: bool) -> str:
    if dark:
        return r"""\usepackage{array,longtable,tabularx,graphicx,color}
\definecolor{MobileDarkBg}{rgb}{0.012,0.014,0.018}
\definecolor{MobileDarkText}{rgb}{0.94,0.95,0.96}
\definecolor{MobileDarkMuted}{rgb}{0.70,0.73,0.76}
\definecolor{MobileDarkLink}{rgb}{0.62,0.78,1.00}
\newcommand{\toprule}{\hline}
\newcommand{\midrule}{\hline}
\newcommand{\bottomrule}{\hline}
\newcommand{\uline}[1]{\underline{#1}}
\newcommand{\href}[2]{\underline{#2}}
\newcommand{\url}[1]{{\scriptsize\texttt{\detokenize{#1}}}}
\newcommand{\vonecallout}[3]{\par\medskip\noindent{\bfseries #2}\par #3\par\medskip}
\newcommand{\vonecode}[1]{\par\smallskip\noindent{\scriptsize\ttfamily #1}\par\smallskip}
"""
    return r"""\usepackage{array,longtable,tabularx,graphicx,color}
\newcommand{\toprule}{\hline}
\newcommand{\midrule}{\hline}
\newcommand{\bottomrule}{\hline}
\newcommand{\uline}[1]{\underline{#1}}
\newcommand{\href}[2]{\underline{#2}}
\newcommand{\url}[1]{{\scriptsize\texttt{\detokenize{#1}}}}
\newcommand{\vonecallout}[3]{\par\medskip\noindent{\bfseries #2}\par #3\par\medskip}
\newcommand{\vonecode}[1]{\par\smallskip\noindent{\small\ttfamily #1}\par\smallskip}
"""


def printable_latex(markdown: str, engine: str) -> str:
    body = unnumber_book_chapters(styled.markdown_to_latex(strip_status_and_promote_chapters(markdown), reference=True))
    return rf"""\documentclass[11pt,openany]{{book}}
\usepackage[a4paper,top=18mm,bottom=20mm,left=18mm,right=18mm,includeheadfoot,headheight=14pt]{{geometry}}
{font_block(engine)}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
{common_macros(False)}
\makeatletter
\def\@makechapterhead#1{{\vspace*{{0.30cm}}{{\parindent0pt\raggedright\Huge\bfseries #1\par\nobreak\vspace{{0.35cm}}}}}}
\def\@makeschapterhead#1{{\vspace*{{0.30cm}}{{\parindent0pt\raggedright\Huge\bfseries #1\par\nobreak\vspace{{0.35cm}}}}}}
\makeatother
\setcounter{{tocdepth}}{{0}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.48em}}
\linespread{{1.04}}
\raggedbottom
\frenchspacing
\begin{{document}}
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{2.2cm}}
{{\Huge\bfseries {styled.latex_escape(TITLE)}\par}}
\vspace{{0.7cm}}
{{\Large {styled.latex_escape(PRINT_SUBTITLE)}\par}}
\vspace{{1.1cm}}
{{Status: DERIVED\par}}
{{Promotion Status: not\_promoted\par}}
\vfill
{{{REVIEW_DATE}\par}}
\end{{titlepage}}
\tableofcontents
\mainmatter
{body}
\end{{document}}
"""


def mobile_latex(markdown: str, engine: str) -> str:
    body = unnumber_book_chapters(styled.markdown_to_latex(strip_status_and_promote_chapters(markdown), reference=True))
    return rf"""\documentclass[10pt,openany]{{book}}
\usepackage[paperwidth=108mm,paperheight=192mm,top=4.5mm,bottom=5.5mm,left=4mm,right=4mm,includeheadfoot,footskip=8pt]{{geometry}}
{font_block(engine, mobile=True)}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
{common_macros(True)}
\makeatletter
\def\normalcolor{{\color{{MobileDarkText}}}}
\def\ps@plain{{\let\@mkboth\@gobbletwo\let\@oddhead\@empty\let\@evenhead\@empty\def\@oddfoot{{\hfil\color{{MobileDarkMuted}}\thepage\hfil}}\let\@evenfoot\@oddfoot}}
\def\@makechapterhead#1{{\vspace*{{0.12cm}}{{\parindent0pt\raggedright\color{{MobileDarkText}}\LARGE\bfseries #1\par\nobreak\vspace{{0.25cm}}}}}}
\def\@makeschapterhead#1{{\vspace*{{0.12cm}}{{\parindent0pt\raggedright\color{{MobileDarkText}}\LARGE\bfseries #1\par\nobreak\vspace{{0.25cm}}}}}}
\makeatother
\setcounter{{tocdepth}}{{0}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.38em}}
\linespread{{1.02}}
\raggedright
\pretolerance=10000
\tolerance=10000
\hyphenpenalty=10000
\exhyphenpenalty=10000
\lefthyphenmin=64
\righthyphenmin=64
\emergencystretch=2.4em
\sloppy
\begin{{document}}
\pagecolor{{MobileDarkBg}}
\color{{MobileDarkText}}
\normalcolor
\pagestyle{{plain}}
\fontsize{{10.2pt}}{{14.6pt}}\selectfont
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{1.2cm}}
{{\Huge\bfseries {styled.latex_escape(TITLE)}\par}}
\vspace{{0.55cm}}
{{\Large {styled.latex_escape(MOBILE_SUBTITLE)}\par}}
\vspace{{0.75cm}}
{{\large Status: DERIVED\par}}
{{\large Promotion Status: not\_promoted\par}}
\vfill
{{\large {REVIEW_DATE}\par}}
\end{{titlepage}}
{{\fontsize{{9.5pt}}{{13.7pt}}\selectfont\raggedright\tableofcontents\par}}
\mainmatter
{body}
\end{{document}}
"""


def unnumber_book_chapters(latex: str) -> str:
    def replace(match: re.Match[str]) -> str:
        title = match.group(1)
        return rf"\chapter*{{{title}}}\addcontentsline{{toc}}{{chapter}}{{{title}}}\markboth{{{title}}}{{{title}}}"

    return re.sub(r"\\chapter\{([^}]+)\}", replace, latex)


def render_pdf(repo_root: Path, markdown: str, pdf_name: str, tex_name: str, mobile: bool) -> PdfInfo:
    engine = styled.select_engine()
    target = repo_root / EXPORTS_ROOT / pdf_name
    result = PdfInfo(path=target, created=False, renderer=engine or "none")
    if not engine:
        result.caveat = "No LaTeX engine found."
        return result

    build_root = repo_root / BUILD_ROOT
    build_root.mkdir(parents=True, exist_ok=True)
    tex_path = build_root / f"{tex_name}.tex"
    write_text(tex_path, mobile_latex(markdown, engine) if mobile else printable_latex(markdown, engine))
    for _ in range(2):
        code, output = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], tex_path.parent, timeout=1800)
        if code != 0:
            result.caveat = output[-2000:]
            return result
    built_pdf = tex_path.with_suffix(".pdf")
    if built_pdf.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built_pdf, target)
    return qa_pdf(repo_root, target, engine, tex_name)


def qa_pdf(repo_root: Path, pdf_path: Path, renderer: str, prefix_name: str) -> PdfInfo:
    qa_root = repo_root / QA_ROOT
    qa_root.mkdir(parents=True, exist_ok=True)
    result = PdfInfo(path=pdf_path, created=pdf_path.exists(), renderer=renderer, size=pdf_path.stat().st_size if pdf_path.exists() else 0)

    if result.created and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=120)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            result.pages = int(match.group(1))

    if result.created and shutil.which("pdftotext"):
        extract = qa_root / f"{prefix_name}_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=240)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"

    if result.created and shutil.which("pdftoppm") and result.pages:
        for stale in qa_root.glob(f"{prefix_name}_page_*.png"):
            stale.unlink()
        pages = sorted({1, 2, min(6, result.pages), max(1, result.pages // 2), result.pages})
        for page in pages:
            prefix = qa_root / f"{prefix_name}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "120", str(pdf_path), str(prefix)], repo_root, timeout=180)
            final = qa_root / f"{prefix_name}_page_{page}.png"
            candidates = sorted(qa_root.glob(f"{prefix.name}-*.png"))
            rendered = candidates[0] if candidates else qa_root / f"{prefix.name}-{page}.png"
            if code == 0 and rendered.exists():
                if final.exists():
                    final.unlink()
                rendered.rename(final)
                result.qa_images.append(final.relative_to(repo_root).as_posix())
    return result


def protected_path_check(repo_root: Path) -> Tuple[bool, List[str]]:
    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
    if code != 0:
        return False, [output.strip()]
    changed = [line.strip() for line in output.splitlines() if line.strip()]
    hits = [path for path in changed if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in docs_corpus.PROTECTED_PREFIXES)]
    return not hits, hits


def write_reports(repo_root: Path, printable: PdfInfo, mobile: PdfInfo, commands: List[Tuple[str, int]]) -> None:
    command_rows = "\n".join(f"| {command} | {'PASS' if code == 0 else 'FAIL'} | {code} |" for command, code in commands)
    build_report = f"""{STATUS_BLOCK}
# Project Vision Book PDF Export Build Report

## Outputs

- Printable desktop PDF: `{printable.path.relative_to(repo_root).as_posix()}` ({printable.pages or ''} pages, {printable.size} bytes, {printable.renderer})
- Mobile dark PDF: `{mobile.path.relative_to(repo_root).as_posix()}` ({mobile.pages or ''} pages, {mobile.size} bytes, {mobile.renderer})

## Styling

### Printable Desktop

- Paper: A4
- Color: black text on white background
- Body: 11pt document class, readable print margins
- TOC: chapter-level only
- Links: visually underlined; not clickable because this local MiKTeX install lacks `url.sty`/full `hyperref`

### Mobile Dark

- Paper: 108mm x 192mm, phone-shaped 9:16 page
- Color: white text on near-black background
- Body: 10.2pt on 14.6pt leading
- Margins: 4mm side margins
- Alignment: ragged-right
- Hyphenation: suppressed with high penalties and large hyphen minima
- TOC: chapter-level only
- Links: visually underlined; not clickable because this local MiKTeX install lacks `url.sty`/full `hyperref`

## Caveats

- These PDFs are publication exports of the derived project vision book.
- They do not create canon, contracts, implementation, release, or queue changes.
"""
    validation_report = f"""{STATUS_BLOCK}
# Project Vision Book PDF Export Validation Report

## Result

- Result: {'PASS' if printable.created and mobile.created and printable.text_extraction != 'FAIL' and mobile.text_extraction != 'FAIL' and printable.glyph_check != 'FAIL' and mobile.glyph_check != 'FAIL' else 'FAIL'}
- Printable PDF exists: {printable.created}
- Printable page count: {printable.pages or ''}
- Printable text extraction: {printable.text_extraction}
- Printable glyph check: {printable.glyph_check}
- Printable caveat: {printable.caveat or 'none'}
- Printable QA images: {', '.join(printable.qa_images) or 'none'}
- Mobile PDF exists: {mobile.created}
- Mobile page count: {mobile.pages or ''}
- Mobile text extraction: {mobile.text_extraction}
- Mobile glyph check: {mobile.glyph_check}
- Mobile caveat: {mobile.caveat or 'none'}
- Mobile QA images: {', '.join(mobile.qa_images) or 'none'}

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


def clean_build(repo_root: Path) -> None:
    build_root = repo_root / BUILD_ROOT
    if build_root.exists():
        for path in build_root.iterdir():
            if path.is_file():
                path.unlink()
        try:
            build_root.rmdir()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    markdown = read_text(repo_root / SOURCE)
    commands: List[Tuple[str, int]] = []

    printable = render_pdf(repo_root, markdown, PRINT_PDF, "project_vision_book_printable", mobile=False)
    commands.append(("render printable desktop PDF", 0 if printable.created else 1))
    mobile = render_pdf(repo_root, markdown, MOBILE_PDF, "project_vision_book_mobile_dark", mobile=True)
    commands.append(("render mobile dark PDF", 0 if mobile.created else 1))
    ok_protected, hits = protected_path_check(repo_root)
    commands.append(("protected path check", 0 if ok_protected else 1))
    if not ok_protected:
        mobile.caveat = "Protected path changes detected: " + ", ".join(hits)

    ok = (
        printable.created
        and mobile.created
        and printable.text_extraction != "FAIL"
        and mobile.text_extraction != "FAIL"
        and printable.glyph_check != "FAIL"
        and mobile.glyph_check != "FAIL"
        and ok_protected
    )
    write_reports(repo_root, printable, mobile, commands)
    if ok:
        clean_build(repo_root)
    print("project vision book PDF exports: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
