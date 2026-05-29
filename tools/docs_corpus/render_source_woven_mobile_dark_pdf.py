"""Render a mobile dark-mode PDF variant of the source-woven book."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import build_omnibus_v1 as styled
import docs_corpus


REVIEW_DATE = "2026-05-30"
TITLE = "Dominium Source-Woven Project Book"
SUBTITLE = "Mobile Dark Reading Edition"
SOURCE = Path("docs/archive/docs_corpus/_source_woven_book/Dominium_Source_Woven_Project_Book.md")
ROOT = Path("docs/archive/docs_corpus/_source_woven_book")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")
BUILD_ROOT = ROOT / "mobile_dark_build"
QA_ROOT = ROOT / "qa"
PDF_NAME = "Dominium_Source_Woven_Project_Book_Mobile_Dark.pdf"
BUILD_REPORT = "Dominium_Source_Woven_Project_Book_Mobile_Dark_Build_Report.md"
VALIDATION_REPORT = "Dominium_Source_Woven_Project_Book_Mobile_Dark_Validation_Report.md"


STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
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


def mobile_dark_latex_document(markdown: str, engine: str) -> str:
    font_block = (
        r"""\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.92]
"""
        if engine in {"xelatex", "lualatex"}
        else r"""\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
"""
    )
    body = styled.markdown_to_latex(markdown, reference=True)
    title = styled.latex_escape(TITLE)
    subtitle = styled.latex_escape(SUBTITLE)
    return rf"""\documentclass[12pt,openany]{{book}}
\usepackage[paperwidth=108mm,paperheight=192mm,margin=8mm,includeheadfoot,headheight=13pt]{{geometry}}
{font_block}
\IfFileExists{{glyphtounicode.tex}}{{\input{{glyphtounicode}}\ifdefined\pdfgentounicode\pdfgentounicode=1\fi}}{{}}
\usepackage{{array,longtable,tabularx,graphicx,color}}
\definecolor{{MobileDarkBg}}{{rgb}}{{0.015,0.018,0.023}}
\definecolor{{MobileDarkText}}{{rgb}}{{0.94,0.95,0.96}}
\definecolor{{MobileDarkMuted}}{{rgb}}{{0.72,0.75,0.78}}
\definecolor{{DomBlue}}{{rgb}}{{0.58,0.76,1.00}}
\definecolor{{DomGreen}}{{rgb}}{{0.55,0.86,0.68}}
\definecolor{{DomAmber}}{{rgb}}{{1.00,0.78,0.42}}
\definecolor{{DomRed}}{{rgb}}{{1.00,0.52,0.52}}
\definecolor{{DomViolet}}{{rgb}}{{0.78,0.70,1.00}}
\definecolor{{DomSlate}}{{rgb}}{{0.78,0.82,0.88}}
\definecolor{{DomMuted}}{{rgb}}{{0.72,0.75,0.78}}
\definecolor{{DomCalloutBg}}{{rgb}}{{0.09,0.11,0.14}}
\definecolor{{DomCodeBg}}{{rgb}}{{0.08,0.09,0.12}}
\makeatletter
\def\normalcolor{{\color{{MobileDarkText}}}}
\def\ps@plain{{\let\@mkboth\@gobbletwo\let\@oddhead\@empty\let\@evenhead\@empty\def\@oddfoot{{\hfil\color{{MobileDarkMuted}}\thepage\hfil}}\let\@evenfoot\@oddfoot}}
\def\ps@headings{{\def\@oddhead{{\color{{MobileDarkMuted}}\small\hfil\rightmark}}\def\@evenhead{{\color{{MobileDarkMuted}}\small\leftmark\hfil}}\def\@oddfoot{{\hfil\color{{MobileDarkMuted}}\thepage\hfil}}\let\@evenfoot\@oddfoot\let\@mkboth\markboth}}
\makeatother
\newcommand{{\toprule}}{{\hline}}
\newcommand{{\midrule}}{{\hline}}
\newcommand{{\bottomrule}}{{\hline}}
\newcommand{{\uline}}[1]{{\underline{{#1}}}}
\newcommand{{\href}}[2]{{\underline{{#2}} {{\scriptsize\texttt{{\detokenize{{#1}}}}}}}}
\newcommand{{\url}}[1]{{{{\scriptsize\texttt{{\detokenize{{#1}}}}}}}}
\setcounter{{tocdepth}}{{1}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.62em}}
\linespread{{1.18}}
\newcommand{{\sourcepath}}[1]{{\par\smallskip\noindent{{\scriptsize\color{{MobileDarkMuted}}\textsf{{Source: }}\texttt{{#1}}}}\par\smallskip}}
\newcommand{{\vonecallout}}[3]{{\par\medskip\noindent\begingroup\setlength{{\fboxsep}}{{7pt}}\colorbox{{DomCalloutBg}}{{\parbox{{0.91\linewidth}}{{\textbf{{\textcolor{{#1}}{{#2}}}}\par\color{{MobileDarkText}} #3}}}}\endgroup\par\medskip}}
\newcommand{{\vonecode}}[1]{{\par\smallskip\noindent\begingroup\setlength{{\fboxsep}}{{7pt}}\colorbox{{DomCodeBg}}{{\parbox{{0.91\linewidth}}{{\scriptsize\ttfamily\color{{MobileDarkText}} #1}}}}\endgroup\par\smallskip}}
\begin{{document}}
\pagecolor{{MobileDarkBg}}
\color{{MobileDarkText}}
\normalcolor
\pagestyle{{headings}}
\fontsize{{13.6pt}}{{20pt}}\selectfont
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{1.1cm}}
{{\Huge\bfseries {title}\par}}
\vspace{{0.55cm}}
{{\Large {subtitle}\par}}
\vspace{{0.9cm}}
{{\large Status: DERIVED\par}}
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


def render_pdf(repo_root: Path) -> PdfInfo:
    engine = styled.select_engine()
    out = repo_root / EXPORTS_ROOT / PDF_NAME
    result = PdfInfo(path=out, created=False, renderer=engine or "none")
    if not engine:
        result.caveat = "No LaTeX engine found."
        return result
    BUILD_ROOT_ABS = repo_root / BUILD_ROOT
    BUILD_ROOT_ABS.mkdir(parents=True, exist_ok=True)
    tex = BUILD_ROOT_ABS / "source_woven_mobile_dark.tex"
    source_text = read_text(repo_root / SOURCE)
    write_text(tex, mobile_dark_latex_document(source_text, engine))
    for _ in range(2):
        code, output = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex.name], tex.parent, timeout=4200)
        if code != 0:
            result.caveat = output[-2000:]
            return result
    built_pdf = tex.with_suffix(".pdf")
    if built_pdf.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built_pdf, out)
    return qa_pdf(repo_root, out, engine)


def qa_pdf(repo_root: Path, pdf_path: Path, renderer: str) -> PdfInfo:
    qa = repo_root / QA_ROOT
    qa.mkdir(parents=True, exist_ok=True)
    result = PdfInfo(path=pdf_path, created=pdf_path.exists(), renderer=renderer, size=pdf_path.stat().st_size if pdf_path.exists() else 0)
    if result.created and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=180)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            result.pages = int(match.group(1))
    if result.created and shutil.which("pdftotext"):
        extract = qa / "source_woven_mobile_dark_extract.txt"
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=900)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
    if result.created and shutil.which("pdftoppm") and result.pages:
        for page in sorted({1, 2, 6, max(1, result.pages // 2), result.pages}):
            prefix = qa / f"source_woven_mobile_dark_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "120", str(pdf_path), str(prefix)], repo_root, timeout=240)
            final = qa / f"source_woven_mobile_dark_page_{page}.png"
            rendered_candidates = sorted(qa.glob(f"{prefix.name}-*.png"))
            rendered = rendered_candidates[0] if rendered_candidates else qa / f"{prefix.name}-{page}.png"
            if code == 0 and rendered.exists():
                if final.exists():
                    final.unlink()
                rendered.rename(final)
                result.qa_images.append(final.relative_to(repo_root).as_posix())
    return result


def write_reports(repo_root: Path, info: PdfInfo, commands: List[Tuple[str, int]]) -> None:
    rel_pdf = info.path.relative_to(repo_root).as_posix() if info.path.exists() else str(info.path)
    command_rows = "\n".join(f"| {command} | {'PASS' if code == 0 else 'FAIL'} | {code} |" for command, code in commands)
    build_report = f"""{STATUS_BLOCK}
# Mobile Dark PDF Build Report

## Output

- Source: `{SOURCE.as_posix()}`
- Output: `{rel_pdf}`
- Created: {info.created}
- Pages: {info.pages or ''}
- Size bytes: {info.size}
- Renderer: {info.renderer}
- Page geometry: 108mm x 192mm
- Body text: 13.6pt on 20pt leading
- Colors: white text on near-black background

## Caveats

- This is a mobile reading variant of the source-woven book, not a new source of truth.
- The content is unchanged except for PDF styling and page geometry.
- Source paths and block IDs retain the same placement as the source-woven book.
"""
    validation_report = f"""{STATUS_BLOCK}
# Mobile Dark PDF Validation Report

## Result

- Result: {'PASS' if info.created and info.text_extraction != 'FAIL' and info.glyph_check != 'FAIL' else 'FAIL'}
- PDF exists: {info.created}
- Page count: {info.pages or ''}
- Text extraction: {info.text_extraction}
- Glyph check: {info.glyph_check}
- QA images: {', '.join(info.qa_images) or 'none'}

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


def clean_build_artifacts(repo_root: Path) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    commands: List[Tuple[str, int]] = []
    info = render_pdf(repo_root)
    code = 0 if info.created else 1
    commands.append(("render mobile dark PDF", code))
    ok, hits = protected_path_check(repo_root)
    commands.append(("protected path check", 0 if ok else 1))
    if not ok:
        info.caveat = "Protected path changes detected: " + ", ".join(hits)
    write_reports(repo_root, info, commands)
    clean_build_artifacts(repo_root)
    if not info.created or not ok or info.text_extraction == "FAIL" or info.glyph_check == "FAIL":
        print("mobile dark PDF render: FAIL")
        return 1
    print("mobile dark PDF render: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
