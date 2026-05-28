Status: DERIVED
Last Reviewed: 2026-05-28
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

# Dominium Docs Corpus Validation Report v0

## Status

- Result: PASS
- Renderer availability/selection: built_in_html_docx_epub_plus_pdflatex_pdf

## Command Results

| Command | Result | Code |
| --- | --- | --- |
| py -3 -c import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('manifest json ok') | PASS | 0 |
| py -3 -c import sys; sys.path.insert(0, 'tools/docs_corpus'); import docs_corpus as d; text=open('docs/archive/docs_corpus/_book/BOOK_MANIFEST.yml', encoding='utf-8').read(); paths=d.parse_book_manifest_paths(text); assert paths; print('book manifest ok', len(paths)) | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| py -3 -m unittest discover tests/tools/docs_corpus | PASS | 0 |
| git diff --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |
| py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST | PASS | 0 |


## Output Files

| Output | Path | Created | Renderer |
| --- | --- | --- | --- |
| docx | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.docx | True | built_in_ooxml |
| epub | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.epub | True | built_in_epub |
| html | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.html/index.html | True | built_in_html |
| pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.pdf | True | pdflatex |
| reference_pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reference_Appendix_v0.pdf | True | pdflatex |


## Source Coverage

- Docs files represented: 5116
- Source root: `docs/`
- Excluded generated root: `docs/archive/docs_corpus/`

## Errors

None.


## Warnings

None.


## Protected Path Check

No protected path modifications were detected by the docs-corpus validator.

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
