# SPEC_LAW_SCOPES (EXEC0c)

Schema ID: LAW_SCOPES
Schema Version: 1.0.0
Status: binding.
Scope: law scope chain and resolution order.

## Purpose
Define a deterministic scope chain for law evaluation across universe,
jurisdiction, actor, and server contexts.

## Scope Types
Canonical scope identifiers:
- SCOPE.EXPLICIT_CONTEXT
- SCOPE.JURISDICTION_LOCAL
- SCOPE.JURISDICTION_PARENT
- SCOPE.UNIVERSE_DEFAULT
- SCOPE.SERVER_DEFAULT
- SCOPE.CANONICAL_FALLBACK

Optional actor/org scopes may exist within the chain and must be declared.

## Scope Chain Resolution (Deterministic)
Resolution order is fixed and deterministic:
1) explicit context (contract/session command)
2) local jurisdiction
3) parent jurisdiction chain (nearest to farthest)
4) universe default
5) server default
6) canonical fallback (refuse-first)

No silent fallback is allowed.

## Diegetic vs Meta Governance
Law sources may be:
- in-universe jurisdictions (diegetic governance)
- server/global meta policy (out-of-universe)
- explicit contracts (context)

The scope chain above resolves precedence deterministically.

## Law Scope References
Work IR and commands reference law scope via:
- law_scope_ref (stable identifier)

law_scope_ref must resolve to a scope in the active scope chain.

## Forbidden Patterns
- Dynamic or hidden scope reordering
- Scope evaluation that depends on wall-clock time or randomness
