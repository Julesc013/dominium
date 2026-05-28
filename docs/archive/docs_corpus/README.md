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

# Dominium Docs Corpus

This directory contains derived, advisory docs-corpus inventory, audit, archive archaeology, reconciliation, wiki, and book-publication outputs for the git-tracked `docs/` tree.

This system is not canon and does not promote archive or conversation-derived claims into current project authority. It exists to make the documentation corpus readable, searchable, and reviewable while preserving the authority order defined by `AGENTS.md`, `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/planning/AUTHORITY_ORDER.md`, and `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`.

## Source Scope

- Source root: `docs/`
- Represented files: 5116
- Represented directories: 279
- Excluded source root: `docs/archive/docs_corpus/` to prevent the generated corpus from recursively republishing itself.
- Conversation corpus root: `docs/archive/conversations/`

## Output Areas

- `_intake/`: deterministic file manifest, source index, counts, tree summary, and non-Markdown inventory.
- `_audit/`: status/header audit, authority map, supersession map, drift, contradiction, staleness, duplicate-shadow, and coverage reports.
- `_archive/`: archive-family archaeology and archive-to-current crosswalks.
- `_reconciliation/`: current project picture, repo-truth crosswalk, promotion queue, decision docket, and blocked-scope alignment.
- `_wiki/`: repo-local navigation pages and reading paths.
- `_book/`: reproducible reader/reference book source.
- `_exports/`: PDF, HTML, DOCX, EPUB, build report, and validation report.

## Regeneration

From repo root:

```powershell
py -3 tools/docs_corpus/docs_corpus.py --repo-root . build
py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root .
```

If renderer prerequisites change, regenerate the exports and review `_exports/Dominium_Docs_Corpus_Build_Report_v0.md` and `_exports/Dominium_Docs_Corpus_Validation_Report_v0.md`.
