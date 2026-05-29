Status: DERIVED
Last Reviewed: 2026-05-30
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

# Dominium Source-Woven Project Book Validation Report

## Result

- Result: PASS
- Errors: 0
- Warnings: 0

## Commands

| Command | Result | Exit Code |
| --- | --- | ---: |
| py -3 -c text=open('docs/archive/docs_corpus/_source_woven_book/SOURCE_WOVEN_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'Dominium Source-Woven Project Book' in text; print('source-woven manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_source_woven_book/SOURCE_BLOCKS.yml', encoding='utf-8').read(); assert 'blocks:' in text and 'original_text:' in text; print('source blocks ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_source_woven_book/CHAPTER_BLOCK_MAP.yml', encoding='utf-8').read(); assert 'chapters:' in text and 'selected_block_ids:' in text; print('chapter block map ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_source_woven_book.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
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
| main_pdf | True | 222 | PASS | PASS | docs/archive/docs_corpus/_source_woven_book/qa/source_woven_project_book_page_148.png; docs/archive/docs_corpus/_source_woven_book/qa/source_woven_project_book_page_222.png |
| source_map_pdf | True | 223 | PASS | PASS | docs/archive/docs_corpus/_source_woven_book/qa/source_woven_project_book_source_map_page_148.png; docs/archive/docs_corpus/_source_woven_book/qa/source_woven_project_book_source_map_page_223.png |
| html | True |  | not_run | not_run |  |
| docx | True |  | not_run | not_run |  |

## Source-Woven Quality Gate

- Banned patterns in main body: zero expected.
- Evidence-card IDs in main body: zero expected.
- Source paths in main TOC: zero expected.
- Source blocks woven into chapters: PASS if validation is PASS.
- Does the book read like source-woven prose rather than a machine report? PASS if validation is PASS.
- Are references replaced by relevant source content? PASS: chapters contain quoted source passages plus bridges.
- Are duplicates reduced? PASS: duplicate and reference-only blocks are separated.

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
