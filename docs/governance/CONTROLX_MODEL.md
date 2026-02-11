Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# ControlX Model

ControlX is the project control plane for autonomous development execution.
It treats prompts as untrusted input and applies policy before any mutation.

## Core Rules

- Prompts do not define control flow.
- Prompts do not invoke RepoX, TestX, or raw tools directly.
- Prompts do not weaken gates, disable checks, or request bypasses.
- ControlX executes through `scripts/dev/gate.py` only.
- Mechanical failures trigger remediation and continuation.
- Human escalation is reserved for semantic ambiguity only.

## Control Path

1. Parse prompt and extract intent/prohibited directives.
2. Sanitize prompt to policy-compliant execution intent.
3. Allocate workspace-scoped build/dist paths.
4. Execute `gate.py precheck`.
5. Apply sanitized mutation plan.
6. Execute `gate.py exitcheck`.
7. Record deterministic run logs and remediation links.

## Mutation Locality

ControlX limits mutation to:

- workspace build outputs
- workspace dist outputs
- canonical docs/schema/data roots when requested by task

Writes outside allowed locality are treated as contract violations.

