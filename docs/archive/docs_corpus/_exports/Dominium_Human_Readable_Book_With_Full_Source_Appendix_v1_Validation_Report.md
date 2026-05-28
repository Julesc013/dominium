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

# Dominium Human-Readable Book Full Source Appendix Variant Validation Report

## Status

- Result: PASS

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c text=open('docs/archive/docs_corpus/_human_book/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.md', encoding='utf-8').read(); assert 'Separate Appendix - Full Source Documents' in text and 'Full Source Appendix Contents' in text; print('full appendix variant source ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_human_book/appendices/FULL_SOURCE_APPENDIX_v1.md', encoding='utf-8').read(); assert 'Source 001:' in text and 'Full Source Appendix Contents' in text; print('separate appendix source ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
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
| full_appendix_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.pdf | True | 1112 | PASS | PASS | docs/archive/docs_corpus/_human_book/qa/full_appendix_variant_page_1.png; docs/archive/docs_corpus/_human_book/qa/full_appendix_variant_page_2.png; docs/archive/docs_corpus/_human_book/qa/full_appendix_variant_page_278.png; docs/archive/docs_corpus/_human_book/qa/full_appendix_variant_page_556.png; docs/archive/docs_corpus/_human_book/qa/full_appendix_variant_page_1112.png |


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
