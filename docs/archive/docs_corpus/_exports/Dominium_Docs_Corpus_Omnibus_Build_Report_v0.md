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

# Dominium Docs Corpus Omnibus Build Report v0

## Build

- Title: Dominium Docs Corpus Omnibus
- Date: 2026-05-29
- Repository branch: `main`
- Repository commit at generation time: `6d59370d2`
- Source root: `docs/`
- Renderer used: pdflatex_source_based
- Single-PDF succeeded: True
- Volume fallback used: false

## Source Coverage

- Source documents counted: 5116
- Source documents included full-text: 147
- Source documents summarized: 4967
- Manifest-only/binary/non-text count: 77
- Explicitly excluded count: 0
- Conversation reader mode: reader_index_plus_by_chat_source_index

## Outputs

| Output | Path | Created | Pages | Size Bytes | Renderer |
| --- | --- | --- | --- | --- | --- |
| omnibus_pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_v0.pdf | True | 1255 | 2664357 | pdflatex_source_based |
| index_pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_Index_v0.pdf | True | 321 | 485132 | pdflatex_source_based |


## Exclusion and Summary Rules

- Raw `DOCS_CORPUS_MANIFEST.json` is summarized rather than printed in full.
- Binary, ZIP, PDF, DOCX, EPUB, and image files are represented by metadata.
- Files marked manifest-only/searchable-only/excluded-binary in the v0 docs-corpus manifest remain manifest/index oriented.
- Full source text is bounded by a readability and single-PDF render budget.

## Known Layout Caveats

- The PDF is intentionally dense.
- Small Markdown tables render as compact LaTeX tables; very wide or long tables are summarized as readable row lists with omission notes.
- PDF bookmarks are not available because the local LaTeX path does not use `hyperref`; the PDF has a table of contents.

## Next Recommended Review Step

Open `Dominium_Docs_Corpus_Omnibus_v0.pdf`, inspect the QA images under `_omnibus/qa/`, then decide whether a v1 split-volume edition should expand more source documents verbatim.
