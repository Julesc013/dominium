Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Semantic Escalation Policy

## Escalation Scope

Escalation to a human is allowed only when mechanical remediation cannot proceed without a semantic decision.

Allowed escalation reasons:

- canon meaning conflict
- policy/licensing decision
- trust/security model decision
- unresolved semantic ambiguity

Disallowed escalation reasons:

- build friction
- tooling path issues
- artifact freshness
- deterministic mechanical refactors
- missing regression tests

## Required Evidence

Escalation must include:

1. failing gate and exact error text
2. blocker classification
3. semantic locality
4. attempted strategy classes and outcomes
5. proof that no further mechanical strategy remains

## Required Template

- `BLOCKER TYPE:`
- `FAILED GATE:`
- `ROOT CAUSE:`
- `ATTEMPTED FIXES:`
- `REMAINING OPTIONS:`
- `RECOMMENDED OPTION:`
- `RATIONALE:`

Any escalation artifact missing these fields is invalid.

## Governance Enforcement

- RepoX enforces escalation template compliance.
- TestX covers failure cases where escalation is attempted without semantic justification.

