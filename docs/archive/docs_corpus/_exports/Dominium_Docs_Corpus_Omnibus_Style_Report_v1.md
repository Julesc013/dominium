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

# Dominium Docs Corpus Omnibus Style Report v1

## What Changed From v0

- Split the v0 coverage artifact into Reader, Reference, All-in-One, HTML, and Mobile HTML outputs.
- Suppressed repeated full metadata blocks after front matter.
- Normalized raw source-path headings into human-readable report titles with compact provenance lines.
- Added semantic callouts for authority, not-promoted status, source provenance, verification, blocked scope, decisions, contradictions, and promotion candidates.
- Added hyperlink-aware PDF/HTML rendering with clickable TOC support where the renderer allows it.
- Reworked table handling so small tables render as clean booktabs-style tables and wide/long tables become readable row-card summaries.
- Improved typography through the locally viable LaTeX engine, Latin Modern fonts, clickable links, styled callouts, and more consistent spacing.

## Style Choices

- Reader PDF: narrative-first, larger margins, less source clutter.
- Reference PDF: denser but still styled and indexed.
- All-in-One PDF: reader material first, reference/index material second.
- HTML: responsive, searchable with browser search, sticky top navigation on desktop.
- Mobile HTML: single-column and scroll-friendly.
- PDF link labels are underlined and include their target path/URL as readable text because the local LaTeX installation is missing `url.sty`, which prevents `hyperref` from loading. HTML outputs retain native clickable links.

## Caveats

- This remains a generated book. It improves readability but does not replace editorial human review.
- Some very large tables are intentionally summarized in PDF; source Markdown and HTML preserve more navigable detail.
- The book does not promote archive or conversation claims.
