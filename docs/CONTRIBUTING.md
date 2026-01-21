# Contribution Guardrails (FUTURE0)

Status: binding.
Scope: contributor requirements for FUTURE0.

This file supplements the root `CONTRIBUTING.md`. If a conflict exists, the
root document is authoritative. This document focuses on FUTURE0 guardrails.

## Required reading (minimum)
- `docs/arch/CANONICAL_SYSTEM_MAP.md`
- `docs/arch/INVARIANTS.md`
- `docs/arch/REALITY_LAYER.md`

## Required change framing
All contributions must describe:
- intent (what is being attempted)
- law/capability gates (who may act)
- effect (what changes, scheduled on ACT)

## Refusal criteria
PRs are refused if they:
- introduce implicit behavior or silent fallback
- bypass auditability or law gates
- simplify by assumption rather than explicit design

## See also
- `CONTRIBUTING.md`
- `docs/arch/FUTURE_PROOFING.md`
