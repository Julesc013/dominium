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

# Dominium Human-Readable Book Full Source Appendix Variant Build Report

## Build

- Title: Dominium Human-Readable Project Book With Full Source Appendix
- Version: 1
- Date: 2026-05-29
- Repository branch: `main`
- Repository commit at generation time: `b4366c0f4`
- Renderer: pdflatex,built_in_html,built_in_ooxml
- Source roots: `docs/`, `docs/archive/conversations/`

## Variant Shape

This variant keeps the synthesized human-readable book first. After all compact appendices, it adds a separate full-source appendix with its own contents page and formatted full text for every `human_full_text` source referenced by Appendix A.

## Source Counts

- Full source appendix documents: 189
- Summarized documents still represented outside this appendix: 3978
- Machine/index-only documents kept out of the appendix: 268

## Outputs

| Output | Path | Created | Pages | Size Bytes | Renderer |
| --- | --- | --- | --- | --- | --- |
| full_appendix_pdf | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.pdf | True | 1112 | 3422419 | pdflatex |
| full_appendix_html | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.html/index.html | True |  | 3874921 | built_in_html |
| full_appendix_docx | docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.docx | True |  | 806705 | built_in_ooxml |


## Caveats

- This is a long-form appendix variant. Use the compact book for normal reading.
- Pipe tables inside source documents are rendered as row-card lists for PDF stability and readability.
- HTML is the primary clickable navigation surface.
