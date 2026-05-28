"""Validate generated docs-corpus Omnibus PDF outputs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


OMNIBUS_ROOT = Path("docs/archive/docs_corpus/_omnibus")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")
OMNIBUS_PDF = EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_v0.pdf"
INDEX_PDF = EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Index_v0.pdf"
BUILD_REPORT = EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Build_Report_v0.md"
VALIDATION_REPORT = EXPORTS_ROOT / "Dominium_Docs_Corpus_Omnibus_Validation_Report_v0.md"

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
    required = [
        OMNIBUS_ROOT / "README.md",
        OMNIBUS_ROOT / "OMNIBUS_MANIFEST.yml",
        OMNIBUS_ROOT / "omnibus_source.md",
        OMNIBUS_ROOT / "parts/00_front_matter.md",
        OMNIBUS_ROOT / "indexes/omnibus_indexes.md",
        OMNIBUS_PDF,
        INDEX_PDF,
        BUILD_REPORT,
        VALIDATION_REPORT,
    ]
    for rel_path in required:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing required omnibus output: {rel_path.as_posix()}")
    manifest_path = repo_root / "docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if payload["summary"]["file_count"] <= 0:
            errors.append("docs corpus manifest has no files")
    except Exception as exc:  # noqa: BLE001 - validator should report parse failure
        errors.append(f"docs corpus manifest parse failed: {exc}")
    omnibus_manifest = repo_root / OMNIBUS_ROOT / "OMNIBUS_MANIFEST.yml"
    if omnibus_manifest.exists():
        text = omnibus_manifest.read_text(encoding="utf-8")
        for token in ['status: "DERIVED"', 'authority_class: "advisory_synthesis"', 'output_mode: "single_pdf"']:
            if token not in text:
                errors.append(f"omnibus manifest missing token: {token}")
    for pdf in [OMNIBUS_PDF, INDEX_PDF]:
        abs_pdf = repo_root / pdf
        pages = pdf_pages(repo_root, abs_pdf)
        if pages is None:
            errors.append(f"could not read PDF page count: {pdf.as_posix()}")
        elif pages <= 0:
            errors.append(f"PDF has no pages: {pdf.as_posix()}")
    if shutil.which("pdftotext") and (repo_root / OMNIBUS_PDF).exists():
        out = repo_root / OMNIBUS_ROOT / "qa/validator_omnibus_extract.txt"
        code, _ = run_command(["pdftotext", str(repo_root / OMNIBUS_PDF), str(out)], repo_root, timeout=300)
        if code != 0 or not out.exists() or out.stat().st_size <= 0:
            errors.append("omnibus PDF text extraction failed")
    else:
        warnings.append("pdftotext unavailable; text extraction check not run")
    protected = protected_changes(repo_root)
    if protected:
        errors.extend(f"protected path changed: {line}" for line in protected)
    status = "PASS" if not errors and not warnings else "PASS_WITH_WARNINGS" if not errors else "FAIL"
    print(f"omnibus validation: {status}")
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
