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

# Dominium Docs Corpus Build Report v0

## Book

- Title: Dominium Documentation Corpus Book v0
- Version: v0
- Date: 2026-05-28
- Source root: `docs/`
- Source exclusion: `docs/archive/docs_corpus/**` excluded to avoid recursive self-publication
- Repository branch: `main`
- Repository commit: `8a1674f4c`
- Renderer used: built_in_html_docx_epub_plus_pdflatex_pdf

## Corpus Coverage

- Docs files represented: 5116
- Docs directories represented: 279
- Main/summarized reader count: 2418
- Reference appendix count: 2275
- HTML/manifest-only/excluded-binary count: 423

## Outputs

| Output | Path | Created | Renderer |
| --- | --- | --- | --- |
| docx | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.docx | True | built_in_ooxml |
| epub | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.epub | True | built_in_epub |
| html | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.html/index.html | True | built_in_html |
| pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reader_v0.pdf | True | pdflatex |
| reference_pdf | docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Reference_Appendix_v0.pdf | True | pdflatex |


## Chapters

- Front Matter
- Current Project Orientation
- Current Canon, Architecture, and Contracts
- Product, Runtime, Tooling, and Domains
- Archive Archaeology
- Conversation Corpus Integration
- Cross-Corpus Reconciliation
- Decisions and Promotion Roadmap
- Navigation and Reading Paths

## Appendices

- Docs Corpus Manifest Summary
- Authority and Supersession Registers
- Archive Family Listing
- Contradiction, Staleness, Promotion, and Decision Registers
- Source Path Index

## Layout Caveats

- The reader PDF is curated. It does not print all 5116 files verbatim.
- The full source index and manifest provide complete coverage.
- Wide registers are summarized in PDFs and retained in Markdown/HTML source outputs.

## Recommended Next Review Step

Review `_reconciliation/DOCS_DECISION_DOCKET_v0.md` and `_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`, then open narrow live-doc promotion tasks only where current authority allows.
