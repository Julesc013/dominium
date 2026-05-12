# SPEC_JURISDICTION_PRECEDENCE (DOMAIN2)

Status: draft.
Scope: deterministic ordering of jurisdictions resolved by spatial domains.

## Purpose
Define a deterministic, auditable order for resolving jurisdictions when
domains overlap or nest.

## Resolution Order (Canonical)
Given a spatial point:
1) Explicit context jurisdiction(s) (contract/event scope)
2) Smallest containing domain’s jurisdictions
3) Higher-precedence containing domains (desc precedence, tie by domain_id)
4) Parent domain chain (increasing scale)
5) World default jurisdiction
6) Server default jurisdiction
7) Canonical fallback (refuse-first)

No ambiguity is allowed; ties must resolve deterministically.

## Binding Order Within a Domain
Jurisdictions bound to a domain are ordered by:
1) Higher binding precedence
2) Lower jurisdiction_id (stable tie-break)

## Notes
- If containment is uncertain, resolution must remain conservative and auditable.
- Fallback jurisdiction must be explicit and stable.
