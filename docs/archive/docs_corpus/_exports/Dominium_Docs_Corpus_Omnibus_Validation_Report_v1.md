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

# Dominium Docs Corpus Omnibus Validation Report v1

## Status

- Result: PASS

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('docs manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_omnibus_v1/OMNIBUS_V1_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 1' in text and 'status: "DERIVED"' in text; print('v1 manifest ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_omnibus_v1.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| git diff --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |


## PDF and Glyph Checks

| Output | Path | Created | Pages | Text Extraction | Glyph Check | QA Images |
| --- | --- | --- | --- | --- | --- | --- |
| reader | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_Reader_v1.pdf | True | 35 | PASS | PASS | docs/archive/docs_corpus/_omnibus_v1/qa/reader_page_1.png; docs/archive/docs_corpus/_omnibus_v1/qa/reader_page_2.png; docs/archive/docs_corpus/_omnibus_v1/qa/reader_page_11.png; docs/archive/docs_corpus/_omnibus_v1/qa/reader_page_23.png; docs/archive/docs_corpus/_omnibus_v1/qa/reader_page_35.png |
| reference | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_Reference_v1.pdf | True | 783 | PASS | PASS | docs/archive/docs_corpus/_omnibus_v1/qa/reference_page_1.png; docs/archive/docs_corpus/_omnibus_v1/qa/reference_page_2.png; docs/archive/docs_corpus/_omnibus_v1/qa/reference_page_261.png; docs/archive/docs_corpus/_omnibus_v1/qa/reference_page_522.png; docs/archive/docs_corpus/_omnibus_v1/qa/reference_page_783.png |
| all_in_one | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_AllInOne_v1.pdf | True | 851 | PASS | PASS | docs/archive/docs_corpus/_omnibus_v1/qa/all_in_one_page_1.png; docs/archive/docs_corpus/_omnibus_v1/qa/all_in_one_page_2.png; docs/archive/docs_corpus/_omnibus_v1/qa/all_in_one_page_283.png; docs/archive/docs_corpus/_omnibus_v1/qa/all_in_one_page_567.png; docs/archive/docs_corpus/_omnibus_v1/qa/all_in_one_page_851.png |


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
