"""Validate the integrated human-readable Dominium project book v2 outputs."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import build_integrated_book_v2 as integrated
import build_omnibus_v1 as styled


REQUIRED = [
    integrated.ROOT / "README.md",
    integrated.ROOT / "INTEGRATED_BOOK_MANIFEST.yml",
    integrated.ROOT / "SOURCE_EVIDENCE_CARDS.yml",
    integrated.ROOT / "SOURCE_EVIDENCE_CARDS.md",
    integrated.ROOT / "CHAPTER_EVIDENCE_MAP.yml",
    integrated.ROOT / "CHAPTER_EVIDENCE_MAP.md",
    integrated.ROOT / "BOILERPLATE_REMOVAL_REPORT.md",
    integrated.ROOT / integrated.MAIN_MD,
    integrated.ROOT / "qa/V1_FAILURE_DIAGNOSIS.md",
    integrated.ROOT / "indexes/CONTENTS_DESIGN.md",
    integrated.ROOT / "indexes/TOPIC_INDEX.md",
    integrated.ROOT / "indexes/DECISION_INDEX.md",
    integrated.ROOT / "indexes/SPECIFICATION_INDEX.md",
    integrated.ROOT / "indexes/CONSTRAINT_INDEX.md",
    integrated.ROOT / "indexes/CONTRADICTION_INDEX.md",
    integrated.ROOT / "indexes/OPEN_QUESTIONS_INDEX.md",
    integrated.ROOT / "indexes/SOURCE_TRAIL_INDEX.md",
    integrated.EXPORTS_ROOT / integrated.MAIN_PDF,
    integrated.EXPORTS_ROOT / integrated.MAIN_HTML_DIR / "index.html",
    integrated.EXPORTS_ROOT / integrated.MAIN_DOCX,
    integrated.EXPORTS_ROOT / integrated.EVIDENCE_PDF,
    integrated.EXPORTS_ROOT / integrated.BUILD_REPORT,
    integrated.EXPORTS_ROOT / integrated.VALIDATION_REPORT,
]

V1_BOILERPLATE_PATTERNS = [
    "This chapter is part of the synthesized reader",
    "That historical context is still useful",
    "Review questions.",
    "How to use this chapter.",
    "The practical consequence is that this topic should be read through the current authority model first",
]


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
        return proc.returncode, proc.stdout
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + (exc.stderr or "")


def pdf_pages(repo_root: Path, path: Path) -> Optional[int]:
    if not shutil.which("pdfinfo") or not path.exists():
        return None
    code, output = run_command(["pdfinfo", str(path)], repo_root, timeout=120)
    if code != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def extracted_text(repo_root: Path, path: Path) -> str:
    if not shutil.which("pdftotext") or not path.exists():
        return ""
    target = repo_root / integrated.QA_ROOT / f"validator_{path.stem}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    code, _ = run_command(["pdftotext", str(path), str(target)], repo_root, timeout=900)
    if code != 0 or not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="replace")


def protected_changes(repo_root: Path) -> List[str]:
    names: List[str] = []
    for cmd in (["git", "diff", "--name-only"], ["git", "diff", "--cached", "--name-only"]):
        code, output = run_command(cmd, repo_root, timeout=120)
        if code == 0:
            names.extend(output.splitlines())
    return sorted({name for name in names if any(name == prefix.rstrip("/") or name.startswith(prefix) for prefix in integrated.PROTECTED_PREFIXES)})


def validate(repo_root: Path) -> List[str]:
    errors: List[str] = []
    for rel_path in REQUIRED:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing required output: {rel_path.as_posix()}")

    book_path = repo_root / integrated.ROOT / integrated.MAIN_MD
    if book_path.exists():
        text = book_path.read_text(encoding="utf-8", errors="replace")
        for pattern in V1_BOILERPLATE_PATTERNS:
            if pattern in text:
                errors.append(f"v2 book still contains v1 boilerplate: {pattern}")
        if re.search(r"^#+\s+Source:\s+docs/", text, re.MULTILINE):
            errors.append("v2 book uses raw source path headings")
        for token in ["Decisions Already Visible", "Specifications and Requirements", "Constraints, Prohibitions, and Prerequisites", "Contradictions, Risks, and Open Ends", "Second- and Third-Order Effects", "Source Trail"]:
            if token not in text:
                errors.append(f"v2 book missing integrated section token: {token}")
        if text.count("`EVC-") < 400:
            errors.append("v2 book does not embed enough evidence card references")
        if text.count("## ") < 50:
            errors.append("v2 book appears too skeletal")
        if "Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.pdf" not in text:
            errors.append("v2 book does not reference the full source appendix as audit backup")

    cards_path = repo_root / integrated.ROOT / "SOURCE_EVIDENCE_CARDS.yml"
    if cards_path.exists():
        cards_text = cards_path.read_text(encoding="utf-8", errors="replace")
        if cards_text.count("card_id:") < 1000:
            errors.append("evidence card set is unexpectedly small")
        for claim in ["decision", "specification", "constraint", "prohibition", "unresolved_question"]:
            if f"claim_type: \"{claim}\"" not in cards_text:
                errors.append(f"evidence cards missing claim type: {claim}")

    map_path = repo_root / integrated.ROOT / "CHAPTER_EVIDENCE_MAP.yml"
    if map_path.exists():
        map_text = map_path.read_text(encoding="utf-8", errors="replace")
        if map_text.count("chapter:") < 25:
            errors.append("chapter evidence map does not cover all chapters")
        if "integrated_cards:" not in map_text:
            errors.append("chapter evidence map missing integrated card assignments")

    html_path = repo_root / integrated.EXPORTS_ROOT / integrated.MAIN_HTML_DIR / "index.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        if "<a " not in html:
            errors.append("HTML output has no links")
        if "Source Trail" not in html:
            errors.append("HTML output has no source trails")

    for filename in [integrated.MAIN_PDF, integrated.EVIDENCE_PDF]:
        pdf = repo_root / integrated.EXPORTS_ROOT / filename
        pages = pdf_pages(repo_root, pdf)
        if not pages:
            errors.append(f"PDF has no page count: {filename}")
        elif filename == integrated.MAIN_PDF and not (80 <= pages <= 420):
            errors.append(f"main PDF page count outside integrated reader target: {pages}")
        text = extracted_text(repo_root, pdf)
        if not text:
            errors.append(f"PDF text extraction failed: {filename}")
        elif styled.has_bad_glyphs(text):
            errors.append(f"PDF extracted text contains bad glyph/control characters: {filename}")

    protected = protected_changes(repo_root)
    if protected:
        errors.append("protected paths changed: " + ", ".join(protected))
    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    errors = validate(repo_root)
    if errors:
        print("integrated book v2 validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("integrated book v2 validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
