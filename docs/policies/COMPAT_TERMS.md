Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# COMPAT_TERMS — Legacy Terminology Mapping

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






## Purpose


Map legacy terms to canonical terminology so specs and docs remain consistent.


Canonical definitions live in `docs/architectureitecture/TERMINOLOGY.md`.





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
