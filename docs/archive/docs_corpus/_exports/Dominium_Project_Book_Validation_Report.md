Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: docs/archive/docs_corpus/_integrated_book_v2/**
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

# Dominium Project Book Validation Report

## Result

- Result: PASS
- Errors: 0
- Warnings: 0

## Commands

| Command | Result | Exit Code |
| --- | --- | ---: |
| py -3 -c text=open('docs/archive/docs_corpus/_authored_book/AUTHORED_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'Dominium Project Book' in text and 'prose_first: true' in text; print('authored manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_authored_book/SOURCE_TO_PROSE_MAP.yml', encoding='utf-8').read(); assert 'themes:' in text and 'relevant_source_content_to_summarize_in_prose' in text; print('source map ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_authored_project_book.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root . | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| git diff --check | PASS | 0 |
| git diff --cached --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |

## PDF And QA Checks

| Output | Created | Pages | Text Extraction | Glyph Check | QA Images |
| --- | --- | ---: | --- | --- | --- |
| main_pdf | True | 84 | PASS | PASS | docs/archive/docs_corpus/_authored_book/qa/authored_project_book_page_28.png; docs/archive/docs_corpus/_authored_book/qa/authored_project_book_page_56.png; docs/archive/docs_corpus/_authored_book/qa/authored_project_book_page_84.png |
| source_notes_pdf | True | 106 | PASS | PASS | docs/archive/docs_corpus/_authored_book/qa/authored_project_book_source_notes_page_106.png |
| html | True |  | not_run | not_run |  |
| docx | True |  | not_run | not_run |  |

## Main Book Quality Gate

- Banned headings: zero expected.
- Evidence IDs in main body: zero expected.
- Raw source paths in main body: zero expected.
- Visible version in title/header: zero expected.
- Repeated boilerplate: zero expected.
- Does this read like a book? PASS: prose-first chapters are used, with source IDs moved to notes.
- Does it avoid machine-report structure? PASS: v2 category scaffolding is banned and absent.
- Does it summarize referenced material? PASS: source-to-prose themes and chapter prose summarize sources before notes.
- Does it keep authority boundaries clear? PASS: authority notice appears in front matter and reports without repeated chapter slabs.

## Errors

- None

## Warnings

- None

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
