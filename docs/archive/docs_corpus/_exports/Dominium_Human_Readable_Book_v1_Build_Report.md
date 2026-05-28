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

# Dominium Human-Readable Book Build Report

## Build

- Title: Dominium Human-Readable Project Book
- Version: 1
- Date: 2026-05-29
- Repository branch: `main`
- Repository commit at generation time: `a39fc14a8`
- Renderer: pdflatex,built_in_html,built_in_ooxml
- Source roots: `docs/`, `docs/archive/conversations/`

## Selection Method

The builder selected prose-first sources for full text, summary, or excerpt use. Machine-readable files, registers, validation logs, manifests, hash lists, and path inventories were kept out of the main book and documented as reference material.

## Source Counts

- Human-readable full-text documents: 189
- Human-readable summarized documents: 3978
- Human-readable excerpted documents: 0
- Reference-only documents: 620
- Machine/index-only documents: 268
- Binary/non-text documents: 68
- Excluded generated-recursive documents: 0

## Outputs

| Output | Path | Created | Pages | Size Bytes | Renderer |
| --- | --- | --- | --- | --- | --- |
| main_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_v1.pdf | True | 43 | 297208 | pdflatex |
| source_reader_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Source_Reader_v1.pdf | True | 165 | 722107 | pdflatex |
| main_html | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_v1.html/index.html | True |  | 170964 | built_in_html |
| source_reader_html | docs/archive/docs_corpus/_exports/Dominium_Human_Source_Reader_v1.html/index.html | True |  | 6873283 | built_in_html |
| docx | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_v1.docx | True |  | 17781 | built_in_ooxml |


## Caveats

- HTML links are the primary clickable navigation surface.
- PDF rendering uses the locally viable LaTeX engine and validates text extraction/glyph quality.
- The main book is synthesized prose; the source reader carries selected original human-readable source material.
