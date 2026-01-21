# Visitability and Refinement (REALITY0)

Status: binding.
Scope: definitive contract for visitability and refinement.

Reachable is not visitable. Visitability is the extra contract that turns
reachability into a lawful, refinable arrival.

## Visitability contract (canonical)
A location is VISITABLE iff:
1) It is reachable via the Travel Graph.
2) The destination domain permits entry.
3) Law and capability allow the visit.
4) Existence state is REFINABLE or REALIZED.
5) A valid refinement contract exists.
6) Budget allows refinement, or defers deterministically.

If any condition fails, the outcome is explicit refusal or deferral.

## Non-negotiable rules
- If a location cannot be refined, it must be unreachable.
- Placeholder or fake micro worlds are forbidden.
- Refinement is contract-driven; collapse preserves conservation and provenance.
- Admin or tool overrides still require law-gated effects and audit.

## Refinement and collapse summary
Refinement:
- deterministic realization from macro state,
- uses declared seeds and invariants,
- produces auditable outputs.

Collapse:
- deterministic aggregation back to macro state,
- preserves pinned/observed entities and history,
- never erases provenance.

## See also
- `docs/arch/REALITY_LAYER.md`
- `docs/arch/REFINEMENT_CONTRACTS.md`
- `docs/arch/VISITABILITY_AND_REALITY.md`
- `docs/arch/VISITABILITY_CONSISTENCY.md`
- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
