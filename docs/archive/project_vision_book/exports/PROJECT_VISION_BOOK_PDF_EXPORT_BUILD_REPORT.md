Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/project_vision_book/book/THE_DOMINIUM_PROJECT_VISION_BOOK.md`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Project Vision Book PDF Export Build Report

## Outputs

- Printable desktop PDF: `docs/archive/project_vision_book/exports/The_Dominium_Project_Vision_Book_Printable.pdf` (25 pages, 187689 bytes, pdflatex)
- Mobile dark PDF: `docs/archive/project_vision_book/exports/The_Dominium_Project_Vision_Book_Mobile_Dark.pdf` (26 pages, 165530 bytes, pdflatex)

## Styling

### Printable Desktop

- Paper: A4
- Color: black text on white background
- Body: 11pt document class, readable print margins
- TOC: chapter-level only
- Links: visually underlined; not clickable because this local MiKTeX install lacks `url.sty`/full `hyperref`

### Mobile Dark

- Paper: 108mm x 192mm, phone-shaped 9:16 page
- Color: white text on near-black background
- Body: 10.2pt on 14.6pt leading
- Margins: 4mm side margins
- Alignment: ragged-right
- Hyphenation: suppressed with high penalties and large hyphen minima
- TOC: chapter-level only
- Links: visually underlined; not clickable because this local MiKTeX install lacks `url.sty`/full `hyperref`

## Caveats

- These PDFs are publication exports of the derived project vision book.
- They do not create canon, contracts, implementation, release, or queue changes.
