Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: stable
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# CompatX Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


CompatX is the compatibility and migration enforcement layer.

## Scope

- Compatibility matrices for schema, pack, save, replay, protocol, API, and ABI.
- Deterministic migration specifications and execution contracts.
- Schema version policy enforcement with explicit migration links.
- Save/replay and pack compatibility validation for regression safety.

## Compatibility Philosophy

- Compatibility is declared in data registries, not implicit in tool code.
- Breaking transitions require explicit migration specs.
- Non-breaking changes remain visible and auditable.
- Forward/backward/full/none compatibility is explicit per transition.

## Determinism Contract

- Canonical outputs are deterministic and hash-stable.
- Migration transforms must be deterministic.
- Run metadata is non-canonical and excluded from determinism decisions.

## Integration

- RepoX enforces compat matrix, migration registry, and schema policy validity.
- TestX validates schema diff classification, migration determinism, save/replay compatibility, and pack compatibility.
- ControlX and automation execute through `scripts/dev/gate.py` with CompatX checks as part of verify/dist flows.
