"""Validate the authored Dominium Project Book outputs."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import List, Sequence, Tuple

import build_authored_project_book as authored
import build_omnibus_v1 as styled
import docs_corpus


ROOT = Path("docs/archive/docs_corpus/_authored_book")
EXPORTS = Path("docs/archive/docs_corpus/_exports")


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 300) -> Tuple[int, str]:
    try:
        completed = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + (exc.stderr or "") + f"\nTIMEOUT after {timeout}s"
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def validate(repo_root: Path) -> List[str]:
    errors: List[str] = []
    required = [
        ROOT / "README.md",
        ROOT / "AUTHORED_BOOK_MANIFEST.yml",
        ROOT / "AUTHORIAL_STYLE_GUIDE.md",
        ROOT / "SOURCE_TO_PROSE_MAP.yml",
        ROOT / "SOURCE_TO_PROSE_MAP.md",
        ROOT / "BOILERPLATE_REJECTION_REPORT.md",
        ROOT / "BANNED_PATTERN_REPORT.md",
        ROOT / "Dominium_Project_Book.md",
        ROOT / "endnotes" / "SOURCE_NOTES.md",
        ROOT / "indexes" / "CONTENTS_PLAN.md",
        ROOT / "indexes" / "TOPIC_INDEX.md",
        ROOT / "indexes" / "DECISION_INDEX.md",
        ROOT / "indexes" / "OPEN_QUESTIONS_INDEX.md",
        ROOT / "indexes" / "SOURCE_NOTES_INDEX.md",
        EXPORTS / "Dominium_Project_Book.pdf",
        EXPORTS / "Dominium_Project_Book.html" / "index.html",
        EXPORTS / "Dominium_Project_Book.docx",
        EXPORTS / "Dominium_Project_Book_Source_Notes.pdf",
        EXPORTS / "Dominium_Project_Book_Build_Report.md",
        EXPORTS / "Dominium_Project_Book_Validation_Report.md",
    ]
    for path in required:
        if not (repo_root / path).exists():
            errors.append(f"missing required output: {path}")

    book_path = repo_root / ROOT / "Dominium_Project_Book.md"
    if book_path.exists():
        text = read_text(book_path)
        first_page = text[:1400]
        for heading in authored.BANNED_HEADINGS:
            if heading in text:
                errors.append(f"banned heading present in main book: {heading}")
        if "EVC-" in text:
            errors.append("evidence IDs leaked into main book")
        if re.search(r"\bdocs/[A-Za-z0-9_./() -]+\.(?:md|json|yml|yaml|toml|txt)\b", text):
            errors.append("raw source path leaked into main book")
        if re.search(r"\bv[23]\b|v2|v3", first_page, re.IGNORECASE):
            errors.append("visible version marker appears in title/front matter")
        repeated = [
            "This chapter is part of the synthesized reader",
            "That historical context is still useful",
            "The practical consequence is that this topic should be read",
            "No strong evidence card was selected",
        ]
        for phrase in repeated:
            if phrase in text:
                errors.append(f"repeated machine-book phrase leaked: {phrase}")
        bullet_lines = len(re.findall(r"(?m)^\s*[-*]\s+", text))
        prose_lines = len([line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")])
        if bullet_lines / max(1, prose_lines) > 0.10:
            errors.append("main body bullet/list ratio is too high")
        chapter_count = len(re.findall(r"(?m)^## \d+\. ", text))
        if chapter_count < 23:
            errors.append(f"expected at least 23 prose chapters, found {chapter_count}")

    notes = repo_root / ROOT / "endnotes" / "SOURCE_NOTES.md"
    if notes.exists():
        note_text = read_text(notes)
        if "EVC-" not in note_text:
            errors.append("source notes do not include evidence IDs")
        if "docs/archive/conversations/" not in note_text:
            errors.append("source notes do not include conversation corpus paths")

    map_path = repo_root / ROOT / "SOURCE_TO_PROSE_MAP.yml"
    if map_path.exists():
        map_text = read_text(map_path)
        if map_text.count("relevant_source_content_to_summarize_in_prose") < 22:
            errors.append("source-to-prose map does not cover all required themes")

    pdf_path = repo_root / EXPORTS / "Dominium_Project_Book.pdf"
    if pdf_path.exists() and (repo_root / EXPORTS / "Dominium_Project_Book.pdf").stat().st_size == 0:
        errors.append("main PDF is empty")
    if pdf_path.exists():
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root)
        if code == 0:
            match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
            if match and int(match.group(1)) < 80:
                errors.append("main PDF page count is below authored-book threshold")
        code, _ = run_command(["pdftotext", str(pdf_path), str(repo_root / ROOT / "qa" / "validator_Dominium_Project_Book.txt")], repo_root, timeout=900)
        if code == 0:
            extracted = read_text(repo_root / ROOT / "qa" / "validator_Dominium_Project_Book.txt")
            if styled.has_bad_glyphs(extracted):
                errors.append("main PDF text extraction contains bad glyphs")

    code, output = run_command(["git", "diff", "--name-only"], repo_root)
    if code == 0:
        for path in output.splitlines():
            clean = path.strip()
            if any(clean == prefix.rstrip("/") or clean.startswith(prefix) for prefix in docs_corpus.PROTECTED_PREFIXES):
                errors.append(f"protected path changed: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    errors = validate(Path(args.repo_root).resolve())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("authored project book validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
