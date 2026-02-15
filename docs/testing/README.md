Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0-draft
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Testing Substrate Notes

## Purpose
Provide a home for testing contracts and invariant-focused guidance that support the canon control substrate.

## Invariants
- Determinism checks are mandatory for authoritative behavior changes.
- Replay/hash equivalence evidence is required for simulation-affecting tasks.
- Test scope must map to changed invariants and affected contracts.

## Example Future Additions
- `docs/testing/testx_gate_map.md`
- `docs/testing/invariant_traceability.md`

## TODO
- Add canonical per-invariant test ownership map.
- Add failure artifact format template.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/ci/DETERMINISM_TEST_MATRIX.md`
