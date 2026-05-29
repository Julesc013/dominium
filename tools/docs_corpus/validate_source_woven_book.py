"""Validate the Dominium Source-Woven Project Book outputs."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import List, Sequence, Tuple

import build_source_woven_book as woven
import build_omnibus_v1 as styled
import docs_corpus


ROOT = Path("docs/archive/docs_corpus/_source_woven_book")
EXPORTS = Path("docs/archive/docs_corpus/_exports")


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 300) -> Tuple[int, str]:
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main_body(text: str) -> str:
    return text.split("# Appendices", 1)[0]


def validate(repo_root: Path) -> List[str]:
    errors: List[str] = []
    required = [
        ROOT / "README.md",
        ROOT / "SOURCE_WOVEN_BOOK_MANIFEST.yml",
        ROOT / "SOURCE_BLOCKS.yml",
        ROOT / "SOURCE_BLOCKS.md",
        ROOT / "CHAPTER_BLOCK_MAP.yml",
        ROOT / "CHAPTER_BLOCK_MAP.md",
        ROOT / "DEDUPLICATION_REPORT.md",
        ROOT / "SELECTION_REPORT.md",
        ROOT / "REJECTED_MACHINE_STYLE_PATTERNS.md",
        ROOT / "Dominium_Source_Woven_Project_Book.md",
        ROOT / "indexes" / "CONTENTS_PLAN.md",
        ROOT / "indexes" / "TOPIC_INDEX.md",
        ROOT / "indexes" / "DECISION_INDEX.md",
        ROOT / "indexes" / "OPEN_QUESTIONS_INDEX.md",
        ROOT / "indexes" / "SOURCE_MAP_INDEX.md",
        EXPORTS / "Dominium_Source_Woven_Project_Book.pdf",
        EXPORTS / "Dominium_Source_Woven_Project_Book.html" / "index.html",
        EXPORTS / "Dominium_Source_Woven_Project_Book.docx",
        EXPORTS / "Dominium_Source_Woven_Project_Book_Source_Map.pdf",
    ]
    for path in required:
        if not (repo_root / path).exists():
            errors.append(f"missing required output: {path}")

    book_path = repo_root / ROOT / "Dominium_Source_Woven_Project_Book.md"
    if book_path.exists():
        text = read_text(book_path)
        body = main_body(text)
        first_page = text[:1400]
        for pattern in woven.BANNED_PATTERNS:
            if pattern in body:
                errors.append(f"banned pattern present in main body: {pattern}")
        if re.search(r"\bv[23]\b|v2|v3", first_page, re.IGNORECASE):
            errors.append("visible version marker appears in title/front matter")
        if re.search(r"(?m)^#+\s+`?docs/", body):
            errors.append("source path appears as a main heading")
        if re.search(r"\bdocs/archive/conversations/[A-Za-z0-9_./() -]+\.md\b", body):
            errors.append("raw conversation path leaked into main body")
        chapter_count = len(re.findall(r"(?m)^## \d+\. ", body))
        if chapter_count < 23:
            errors.append(f"expected 23 chapters, found {chapter_count}")
        quote_lines = len(re.findall(r"(?m)^>\s+\S", body))
        if quote_lines < 230:
            errors.append(f"too few woven source passage lines: {quote_lines}")
        source_labels = len(re.findall(r"\[Source: ", body))
        if source_labels < 120:
            errors.append(f"too few compact source attributions: {source_labels}")
        bullet_lines = len(re.findall(r"(?m)^\s*[-*]\s+", body))
        prose_lines = len([line for line in body.splitlines() if line.strip() and not line.lstrip().startswith("#")])
        if bullet_lines / max(1, prose_lines) > 0.12:
            errors.append("main body bullet/list ratio is too high")

    blocks_path = repo_root / ROOT / "SOURCE_BLOCKS.yml"
    if blocks_path.exists():
        text = read_text(blocks_path)
        if text.count("block_id:") < 1000:
            errors.append("source block manifest has too few blocks")
        if "original_text:" not in text or "cleaned_text:" not in text:
            errors.append("source block manifest does not preserve original and cleaned text")

    chapter_map = repo_root / ROOT / "CHAPTER_BLOCK_MAP.yml"
    if chapter_map.exists():
        text = read_text(chapter_map)
        if text.count("selected_block_ids:") < 23:
            errors.append("chapter block map does not cover all chapters")

    toc = repo_root / ROOT / "indexes" / "CONTENTS_PLAN.md"
    if toc.exists():
        toc_text = read_text(toc)
        if "docs/archive/" in toc_text or "SWB-" in toc_text:
            errors.append("contents plan is contaminated with source paths or block IDs")

    pdf_path = repo_root / EXPORTS / "Dominium_Source_Woven_Project_Book.pdf"
    if pdf_path.exists():
        if pdf_path.stat().st_size == 0:
            errors.append("main PDF is empty")
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=180)
        if code == 0:
            match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
            if match and int(match.group(1)) < 120:
                errors.append("main source-woven PDF is below the expected page count")
        extract = repo_root / ROOT / "qa" / "validator_source_woven_book.txt"
        code, _output = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=900)
        if code == 0 and extract.exists():
            extracted = read_text(extract)
            if styled.has_bad_glyphs(extracted):
                errors.append("main PDF text extraction contains bad glyphs")

    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
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
    print("source-woven book validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
