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

# V0 Failure Modes

This file records why the human-readable book reset exists. The v0 Omnibus remains useful as a coverage artifact, but it is not a readable project book.

## Inspected Artifact

- Path: `docs/archive/docs_corpus/_exports/Dominium_Docs_Corpus_Omnibus_v0.pdf`
- Page count: 1255
- Text extraction/glyph smoke check: broken/control glyphs detected

## Failure Modes To Avoid

- Raw `Source: docs/...` headings dominate the table of contents.
- Repeated full metadata/status blocks interrupt the reading flow.
- Dense machine tables appear in the main body.
- Long filesystem/path indexes masquerade as chapters.
- Extracted text may show broken glyphs or control characters.
- Pages can be visually sparse and dense at the same time: large whitespace around cramped machine tables.
- The old book has weak human narrative.
- The old book does not clearly separate book content from reference material.

## Acceptance Rule For This Reset

The main human-readable book must be a synthesis. It may cite source paths and use compact source trails, but it must not repeat the v0 pattern of rendering manifests, path lists, and machine registers as chapter content.
