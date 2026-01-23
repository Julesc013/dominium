# COMPAT_TERMS — Legacy Terminology Mapping

## Purpose
Map legacy terms to canonical terminology so specs and docs remain consistent.
Canonical definitions live in `docs/architecture/TERMINOLOGY.md`.

## Mappings (selected)
- feature (permission sense) -> capability
- asset bundle -> pack (assets are pack contents)
- map/layer (authoritative sense) -> field
- entity (canonical identity sense) -> topology node
- Universe directory -> Universe bundle
- Star system -> Cosmo system anchor
- Physics -> logical mechanics unless explicitly local

## Rules
- Prefer canonical terms in new docs and comments.
- When updating legacy docs, replace mapped terms where possible.
- If a legacy term must remain, add a local note that points to the canonical
  term.
