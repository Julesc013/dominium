Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Semantic Escalation Policy

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Rule

Escalation to humans is allowed only for semantic ambiguity, never for mechanical blockers.

## Mechanical Blockers (No Escalation)

- Tool discoverability
- PATH/CWD setup issues
- Missing derived artifacts
- Build output wiring
- Deterministic regeneration tasks

These must be remediated autonomously.

## Semantic Blockers (Escalation Allowed)

- Canon meaning conflicts
- Ontology interpretation disputes
- Security/trust model meaning choices
- Policy decisions requiring human authority

## Required Escalation Template

- `BLOCKER TYPE`
- `FAILED GATE`
- `ROOT CAUSE`
- `ATTEMPTED FIXES`
- `REMAINING OPTIONS`
- `RECOMMENDED OPTION`
- `RATIONALE`
