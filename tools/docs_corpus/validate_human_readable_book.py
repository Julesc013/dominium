"""Validate the human-readable Dominium book outputs."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import build_human_readable_book as human
import build_omnibus_v1 as styled


REQUIRED = [
    human.HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_MANIFEST.yml",
    human.HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_SELECTION_REPORT.md",
    human.HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_COMPILATION.md",
    human.HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_INDEX.md",
    human.HUMAN_SOURCE_ROOT / "EXCLUDED_MACHINE_READABLE_MATERIAL.md",
    human.HUMAN_BOOK_ROOT / "README.md",
    human.HUMAN_BOOK_ROOT / "HUMAN_BOOK_MANIFEST.yml",
    human.HUMAN_BOOK_ROOT / "Dominium_Human_Readable_Book_v1.md",
    human.HUMAN_BOOK_ROOT / "qa/V0_FAILURE_MODES.md",
    human.HUMAN_BOOK_ROOT / "indexes/BOOK_INDEX.md",
    human.HUMAN_BOOK_ROOT / "indexes/SOURCE_TRAIL_INDEX.md",
    human.HUMAN_BOOK_ROOT / "indexes/DECISION_INDEX.md",
    human.HUMAN_BOOK_ROOT / "indexes/TOPIC_INDEX.md",
    human.EXPORTS_ROOT / human.MAIN_PDF,
    human.EXPORTS_ROOT / human.MAIN_HTML_DIR / "index.html",
    human.EXPORTS_ROOT / human.MAIN_DOCX,
    human.EXPORTS_ROOT / human.SOURCE_READER_PDF,
    human.EXPORTS_ROOT / human.BUILD_REPORT,
    human.EXPORTS_ROOT / human.VALIDATION_REPORT,
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
    target = repo_root / human.HUMAN_BOOK_ROOT / "qa" / f"validator_{path.stem}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    code, _ = run_command(["pdftotext", str(path), str(target)], repo_root, timeout=600)
    if code != 0 or not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="replace")


def protected_changes(repo_root: Path) -> List[str]:
    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
    names = output.splitlines() if code == 0 else []
    code_cached, output_cached = run_command(["git", "diff", "--cached", "--name-only"], repo_root, timeout=120)
    if code_cached == 0:
        names.extend(output_cached.splitlines())
    return sorted({name for name in names if any(name == prefix.rstrip("/") or name.startswith(prefix) for prefix in human.PROTECTED_PREFIXES)})


def validate(repo_root: Path) -> List[str]:
    errors: List[str] = []
    for rel_path in REQUIRED:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing required output: {rel_path.as_posix()}")

    book_path = repo_root / human.HUMAN_BOOK_ROOT / "Dominium_Human_Readable_Book_v1.md"
    if book_path.exists():
        text = book_path.read_text(encoding="utf-8", errors="replace")
        if text.count("Status: DERIVED") > 2:
            errors.append("main book contains repeated full metadata blocks")
        if re.search(r"^#+\s+Source:\s+docs/", text, re.MULTILINE):
            errors.append("main book uses raw source path headings")
        if "Source trail:" not in text:
            errors.append("main book has no source trails")
        if "raw JSON" not in text and "raw YAML" not in text:
            errors.append("main book does not explicitly exclude machine-readable dumps")
        if text.count("## ") < 20:
            errors.append("main book appears too skeletal")

    source_manifest = repo_root / human.HUMAN_SOURCE_ROOT / "HUMAN_SOURCE_MANIFEST.yml"
    if source_manifest.exists():
        manifest = source_manifest.read_text(encoding="utf-8", errors="replace")
        for token in ["human_full_text", "human_summarize", "machine_index_only", "binary_or_non_text"]:
            if token not in manifest:
                errors.append(f"source manifest missing disposition {token}")

    html_path = repo_root / human.EXPORTS_ROOT / human.MAIN_HTML_DIR / "index.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        if "<a " not in html:
            errors.append("HTML output has no links")
        if "Source trail" not in html:
            errors.append("HTML output has no source trails")

    for filename in [human.MAIN_PDF, human.SOURCE_READER_PDF]:
        pdf = repo_root / human.EXPORTS_ROOT / filename
        pages = pdf_pages(repo_root, pdf)
        if not pages:
            errors.append(f"PDF has no page count: {filename}")
        elif filename == human.MAIN_PDF and pages > 260:
            errors.append(f"main PDF is too long for the reader target: {pages} pages")
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
        print("human-readable book validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("human-readable book validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
