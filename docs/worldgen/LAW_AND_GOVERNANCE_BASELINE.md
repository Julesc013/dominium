Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Law and Governance Baseline (T19)

Status: baseline.  
Scope: institutional law, jurisdiction overlaps, enforcement, and inspection.

## What exists now
- Institutions are persistent entities with **authority types**, **jurisdiction scopes**, and **enforcement capacity**.
- Law is expressed as **rules over process families** (allow / forbid / conditional / license).
- Enforcement is **event-driven** and deterministic; no per-tick global scanning.
- Inspection exposes:
  - active institutions and scopes
  - capabilities and licensing requirements
  - rule decisions and enforcement events
  - explicit refusal reasons

## What does NOT exist yet
- Global omnipotent law or god-mode enforcement.
- Economy, trade, or market mechanics.
- Scripted political outcomes or hardcoded factions.
- Per-tick social simulation or compliance solvers.

## Determinism & scaling
- All evaluation is fixed-point and deterministic.
- Resolution is **interest- and budget-bounded**.
- Inactive domains do not affect cost.
- Collapse/expand stores macro capsule statistics for governance state.

## How this supports later layers
This baseline provides the constraints for:
- risk, insurance, and liability (T16)
- trust, reputation, and legitimacy (T17)
- knowledge and education (T18)
- economy and markets (T20+)

## Inspection contract
Inspection must show:
- which rule or capability constrained a process
- required license or authority
- jurisdiction overlap resolution path
- provenance and auditability metadata

## See also
- `docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`