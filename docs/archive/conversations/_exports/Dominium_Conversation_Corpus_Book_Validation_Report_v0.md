Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Dominium Conversation Corpus Book Validation Report v0

Validation status: `PASS`

## Renderer

- Quarto: unavailable
- Pandoc: unavailable
- PDF renderer: local LaTeX engine if output exists
- HTML renderer: custom static HTML
- DOCX renderer: custom OOXML fallback
- EPUB renderer: custom EPUB fallback

## Outputs

- `pdf`: created `True`, path `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Book_v0.pdf`, renderer `detected_existing`, pages `797`
- `html`: created `True`, path `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Book_v0.html`, renderer `detected_existing`, pages `None`
- `docx`: created `True`, path `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Book_v0.docx`, renderer `detected_existing`, pages `None`
- `epub`: created `True`, path `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Book_v0.epub`, renderer `detected_existing`, pages `None`
- `reference_pdf`: created `True`, path `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Reference_Appendix_v0.pdf`, renderer `detected_existing`, pages `302`
- `pdf_qa`: created `True`, path `docs/archive/conversations/_book/qa/PDF_QA_SUMMARY.md`, renderer `detected_existing`, pages `5`

## Book Source Checks

- Included source files: `38`
- Excluded reader-edition source files: `74`
- Source check errors: `0`
- Source check warnings: `0`

## Commands Run

- `py -3 tools/conversations/validate_conversation_outputs.py --repo-root .` -> exit `0`
- `py -3 -c import json; json.load(open('docs/archive/conversations/_intake/corpus_manifest.json', encoding='utf-8')); print('corpus_manifest.json ok')` -> exit `0`
- `py -3 -c import sys; sys.path.insert(0, 'tools/conversations'); import build_conversation_book as b; paths = b.parse_manifest_paths(open('docs/archive/conversations/_book/BOOK_MANIFEST.yml', encoding='utf-8').read()); assert paths; print('BOOK_MANIFEST.yml ok', len(paths))` -> exit `0`
- `py -3 -m unittest discover tests/tools/conversations` -> exit `0`
- `git diff --check` -> exit `0`
- `py -3 .aide/scripts/aide_lite.py doctor` -> exit `0`
- `py -3 .aide/scripts/aide_lite.py validate` -> exit `0`
- `py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST` -> exit `0`

## Broken Links

- Markdown/source link existence is covered by source path checks and generated conversation-output validation.

## Protected Path Check

- No protected path changes detected by `git status --short`.

## Impact Statements

- canon impact: unchanged
- contract/schema impact: unchanged
- implementation impact: unchanged
- release impact: unchanged
- queue impact: unchanged
- archive claim promotion: none

## Caveats

- Dense matrices are summarized in PDF and retained in Markdown/HTML/source outputs.
- DOCX/EPUB are fallback review copies because Quarto/Pandoc are unavailable.
