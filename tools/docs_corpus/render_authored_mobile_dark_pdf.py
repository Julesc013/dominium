"""Render a mobile dark-mode PDF variant of the authored Dominium Project Book."""

from __future__ import annotations

from pathlib import Path

import render_source_woven_mobile_dark_pdf as mobile


TITLE = "Dominium Project Book"
SOURCE = Path("docs/archive/docs_corpus/_authored_book/Dominium_Project_Book.md")
ROOT = Path("docs/archive/docs_corpus/_authored_book")
PDF_NAME = "Dominium_Project_Book_Mobile_Dark.pdf"
QA_PREFIX = "authored_project_book_mobile_dark"


def configure_mobile_renderer() -> None:
    mobile.TITLE = TITLE
    mobile.SOURCE = SOURCE
    mobile.ROOT = ROOT
    mobile.BUILD_ROOT = mobile.ROOT / "mobile_dark_build"
    mobile.QA_ROOT = mobile.ROOT / "qa"
    mobile.PDF_NAME = PDF_NAME
    mobile.BUILD_REPORT = "Dominium_Project_Book_Mobile_Dark_Build_Report.md"
    mobile.VALIDATION_REPORT = "Dominium_Project_Book_Mobile_Dark_Validation_Report.md"
    mobile.SUBJECT_LABEL = "authored Dominium Project Book"
    mobile.QA_PREFIX = QA_PREFIX
    mobile.TEX_NAME = "authored_project_book_mobile_dark"


if __name__ == "__main__":
    configure_mobile_renderer()
    raise SystemExit(mobile.main())
