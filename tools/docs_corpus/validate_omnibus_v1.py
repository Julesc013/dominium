"""Validate styled v1 docs-corpus Omnibus outputs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


V1_ROOT = Path("docs/archive/docs_corpus/_omnibus_v1")
STYLE_ROOT = Path("docs/archive/docs_corpus/_style_v1")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")

REQUIRED = [
    V1_ROOT / "README.md",
    V1_ROOT / "OMNIBUS_V1_MANIFEST.yml",
    V1_ROOT / "reader_source.md",
    V1_ROOT / "reference_source.md",
    V1_ROOT / "all_in_one_source.md",
    V1_ROOT / "mobile_html_source.md",
    STYLE_ROOT / "omnibus_reader.tex",
    STYLE_ROOT / "omnibus_reference.tex",
    STYLE_ROOT / "omnibus_html.css",
    STYLE_ROOT / "omnibus_mobile.css",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Reader_v1.pdf",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Reference_v1.pdf",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_AllInOne_v1.pdf",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_HTML_v1/index.html",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Mobile_v1.html",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Style_Report_v1.md",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Build_Report_v1.md",
    EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Validation_Report_v1.md",
]

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


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 300) -> Tuple[int, str]:
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
    code, output = run_command(["pdfinfo", str(path)], repo_root)
    if code != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def has_bad_glyphs(text: str) -> bool:
    if "\ufffd" in text:
        return True
    return any(ord(ch) < 32 and ch not in "\n\r\t\f" for ch in text)


def protected_changes(repo_root: Path) -> List[str]:
    code, output = run_command(["git", "status", "--short"], repo_root)
    if code != 0:
        return [f"git status failed: {output}"]
    changes: List[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace("\\", "/")
        for prefix in PROTECTED_PREFIXES:
            if path == prefix.rstrip("/") or path.startswith(prefix):
                changes.append(line)
    return changes


def validate(repo_root: Path) -> int:
    errors: List[str] = []
    warnings: List[str] = []
    for rel_path in REQUIRED:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing required v1 output: {rel_path.as_posix()}")

    try:
        payload = json.loads((repo_root / "docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json").read_text(encoding="utf-8"))
        if payload["summary"]["file_count"] <= 0:
            errors.append("docs corpus manifest has no files")
    except Exception as exc:  # noqa: BLE001 - validation report should expose parse failure
        errors.append(f"docs corpus manifest parse failed: {exc}")

    manifest = repo_root / V1_ROOT / "OMNIBUS_V1_MANIFEST.yml"
    if manifest.exists():
        text = manifest.read_text(encoding="utf-8")
        for token in ['version: 1', 'status: "DERIVED"', 'style_profile: "readability_v1"']:
            if token not in text:
                errors.append(f"v1 manifest missing token: {token}")

    for rel_pdf in [
        EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Reader_v1.pdf",
        EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Reference_v1.pdf",
        EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_AllInOne_v1.pdf",
    ]:
        pdf = repo_root / rel_pdf
        pages = pdf_pages(repo_root, pdf)
        if pages is None:
            errors.append(f"could not read PDF page count: {rel_pdf.as_posix()}")
        elif pages <= 0:
            errors.append(f"PDF has no pages: {rel_pdf.as_posix()}")
        if shutil.which("pdftotext") and pdf.exists():
            extract = repo_root / V1_ROOT / "qa" / f"validator_{pdf.stem}.txt"
            code, _ = run_command(["pdftotext", str(pdf), str(extract)], repo_root, timeout=500)
            if code != 0 or not extract.exists() or extract.stat().st_size <= 0:
                errors.append(f"PDF text extraction failed: {rel_pdf.as_posix()}")
            elif has_bad_glyphs(extract.read_text(encoding="utf-8", errors="replace")):
                errors.append(f"PDF text extraction contains bad glyph/control characters: {rel_pdf.as_posix()}")
        else:
            warnings.append(f"pdftotext unavailable; extraction not checked for {rel_pdf.as_posix()}")

    reader_source = repo_root / V1_ROOT / "reader_source.md"
    if reader_source.exists():
        text = reader_source.read_text(encoding="utf-8")
        source_heading_count = len(re.findall(r"^## Source:", text, flags=re.MULTILINE))
        if source_heading_count:
            errors.append("reader source still contains raw Source headings")
        if text.count("Status: DERIVED") > 1:
            errors.append("reader source repeats full metadata blocks")

    html_path = repo_root / EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_HTML_v1/index.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        if "<a " not in html:
            warnings.append("HTML output has no hyperlinks")
        if "callout" not in html:
            errors.append("HTML output has no semantic callouts")

    protected = protected_changes(repo_root)
    if protected:
        errors.extend(f"protected path changed: {line}" for line in protected)

    status = "PASS" if not errors and not warnings else "PASS_WITH_WARNINGS" if not errors else "FAIL"
    print(f"omnibus v1 validation: {status}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    return 0 if status != "FAIL" else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    return validate(Path(args.repo_root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
