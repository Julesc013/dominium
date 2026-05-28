Status: DERIVED
Last Reviewed: 2026-05-29
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

# Dominium Docs Corpus Omnibus Validation Report v0

## Status

- Result: PASS

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('docs manifest ok') | PASS | 0 |
| py -3 -c import sys; sys.path.insert(0, 'tools/docs_corpus'); import docs_corpus as d; text=open('docs/archive/docs_corpus/_book/BOOK_MANIFEST.yml', encoding='utf-8').read(); paths=d.parse_book_manifest_paths(text); assert paths; print('book manifest ok') | PASS | 0 |
| py -3 -c text=open('docs/archive/docs_corpus/_omnibus/OMNIBUS_MANIFEST.yml', encoding='utf-8').read(); assert 'status: "DERIVED"' in text and 'output_mode: "single_pdf"' in text; print('omnibus manifest ok') | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_omnibus_pdf.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| git diff --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |


## PDF Checks

| PDF | Path | Exists | Pages | Text Extraction | QA Images |
| --- | --- | --- | --- | --- | --- |
| omnibus | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_v0.pdf | True | 1255 | PASS | docs/archive/docs_corpus/_omnibus/qa/omnibus_page_1.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_page_2.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_page_627.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_page_1255.png |
| index | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_Index_v0.pdf | True | 321 | PASS | docs/archive/docs_corpus/_omnibus/qa/omnibus_index_page_1.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_index_page_2.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_index_page_160.png; docs/archive/docs_corpus/_omnibus/qa/omnibus_index_page_321.png |


## Errors

None.


## Warnings

None.


## Protected Path Check

No protected path modifications were detected by the omnibus validator.

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
