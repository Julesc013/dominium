Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: docs/archive/docs_corpus/_omnibus/**
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

# Dominium Human-Readable Book Validation Report

## Status

- Result: PASS

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c text=open('docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'sources:' in text; print('human source manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_human_book/HUMAN_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'outputs:' in text; print('human book manifest ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| git diff --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |


## PDF QA

| Output | Path | Created | Pages | Text Extraction | Glyph Check | QA Images |
| --- | --- | --- | --- | --- | --- | --- |
| main_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_v1.pdf | True | 43 | PASS | PASS | docs/archive/docs_corpus/_human_book/qa/main_pdf_page_1.png; docs/archive/docs_corpus/_human_book/qa/main_pdf_page_2.png; docs/archive/docs_corpus/_human_book/qa/main_pdf_page_10.png; docs/archive/docs_corpus/_human_book/qa/main_pdf_page_21.png; docs/archive/docs_corpus/_human_book/qa/main_pdf_page_43.png |
| source_reader_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Source_Reader_v1.pdf | True | 165 | PASS | PASS | docs/archive/docs_corpus/_human_book/qa/source_reader_pdf_page_1.png; docs/archive/docs_corpus/_human_book/qa/source_reader_pdf_page_2.png; docs/archive/docs_corpus/_human_book/qa/source_reader_pdf_page_41.png; docs/archive/docs_corpus/_human_book/qa/source_reader_pdf_page_82.png; docs/archive/docs_corpus/_human_book/qa/source_reader_pdf_page_165.png |


## Errors

None.

## Warnings

None.

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
