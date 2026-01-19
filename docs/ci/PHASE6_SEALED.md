# Phase 6 Sealed (LIFE + CIV Foundation)

Status: SEALED
Version: 1

This document formally seals Phase 6 (LIFE0–LIFE4, CIV0a–CIV4, MP0, GOV0)
as a stable, deterministic, and scalable foundation for future phases.

## Guarantees
- Determinism: all LIFE/CIV pipelines are batch-vs-step equivalent and
  lockstep/server-auth compatible.
- Event-driven scalability: no global iteration; all macro subsystems expose
  `next_due_tick`.
- Provenance: no fabrication of people, assets, or institutions; ledger
  conservation holds through death, salvage, and inheritance.
- Epistemic safety: UI and tools are capability-gated; no omniscient views.
- Offline + MP parity: loopback, lockstep, and server-auth share the same
  authoritative pipeline.
- Governance & validation: GOV0 validators enforce schema, provenance,
  performance, and rendering canon rules.

## Required Gates (Must Remain Enabled)
- `phase6_audit` CTest (`PH6-AUDIT-001`)
- `tools/ci/arch_checks.py` (ARCH/DET/PERF/SCALE/EPIS guards)
- `tools/validation/validate_all` (GOV-VAL-* gates)
- Phase 6 CTests from `game/tests/phase6` (LIFE/CIV/MP0 suites)

## What Future Phases May Assume
- Persons persist across death; bodies die deterministically; estates are created.
- Birth and continuation are causal, not fabricated.
- Cohorts, cities, institutions, knowledge, and logistics scale via scheduled events.
- Interest sets bound activation; fidelity transitions preserve provenance.
- Standards resolution is deterministic and policy-driven.
- Epistemic projections are the only UI-visible truth.

## Intentionally Undefined (Open for Future Phases)
- Advanced AI/agents, culture/religion, conflict/warfare.
- Detailed health/biology, courts/law procedures, deep market mechanics.
- Physical orbital mechanics and full vehicle simulation.
- Multi-galaxy narrative content and long-horizon macro policy tooling.

## Seal Declaration
Phase 6 is sealed. Any changes to LIFE/CIV/GOV MUST preserve the guarantees
above and must add or update enforcement gates in `docs/CI_ENFORCEMENT_MATRIX.md`.
