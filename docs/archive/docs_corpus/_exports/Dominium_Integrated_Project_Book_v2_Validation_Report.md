Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: docs/archive/docs_corpus/_human_book/**
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

# Dominium Integrated Project Book v2 Validation Report

## Status

- Result: PASS

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c text=open('docs/archive/docs_corpus/_integrated_book_v2/INTEGRATED_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 2' in text and 'evidence_cards:' in text; print('integrated manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_integrated_book_v2/SOURCE_EVIDENCE_CARDS.yml', encoding='utf-8').read(); assert text.count('card_id:') > 1000; print('evidence cards ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_integrated_book_v2/CHAPTER_EVIDENCE_MAP.yml', encoding='utf-8').read(); assert text.count('chapter:') >= 25; print('chapter map ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_integrated_book_v2.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root . | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| git diff --check | PASS | 0 |
| git diff --cached --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |


## PDF QA

| Output | Path | Created | Pages | Text Extraction | Glyph Check | QA Images |
| --- | --- | --- | --- | --- | --- | --- |
| main_pdf | docs/archive/docs_corpus/_exports/Dominium_Integrated_Project_Book_v2.pdf | True | 240 | PASS | PASS | docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_1.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_2.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_8.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_80.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_160.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_book_v2_page_240.png |
| evidence_map_pdf | docs/archive/docs_corpus/_exports/Dominium_Integrated_Project_Book_v2_Source_Evidence_Map.pdf | True | 118 | PASS | PASS | docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_1.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_2.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_8.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_39.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_78.png; docs/archive/docs_corpus/_integrated_book_v2/qa/integrated_evidence_map_v2_page_118.png |


## Repetition and TOC Checks

- V1 boilerplate phrase check: enforced by `validate_integrated_book_v2.py`.
- Raw source-path heading check: enforced by `validate_integrated_book_v2.py`.
- Evidence-card coverage check: enforced by generated card and chapter-map checks.
- Source trail check: enforced by `validate_integrated_book_v2.py`.

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
