Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03

# Institutional Communication Model (SIG-6)

## Purpose
Define deterministic institutional communication and aggregation behavior for bulletins, dispatch operations, standards/certification workflows, and report distribution at scale.

## A) Bulletin Model

- A bulletin is a `REPORT` artifact published by an institution.
- Bulletin scope is policy-defined:
  - `local` (site)
  - `regional`
  - `global`
- Bulletins are sent only through SIG transport channels using normal envelope/address resolution.
- Bulletin publication must be event-sourced and replayable.

## B) Dispatch Office Model

- A dispatch office is an institution that coordinates timetables and schedule updates through control-plane intents.
- Dispatch outputs:
  - schedule-change control intents (no direct schedule mutation)
  - dispatch update reports (`REPORT` artifacts)
- Dispatch applies deterministic policy filters for allowed schedule kinds and priorities.

## C) Standards Body Model

- A standards body is an institution authorized to issue:
  - `SpecSheet` artifacts (SPEC domain)
  - credential/certification artifacts (SIG-4)
  - compliance reports (`REPORT`) sourced from deterministic compliance results
- Standards issuance is policy-driven; no hardcoded domain-specific authority branches.

## D) Aggregation Model

- Institutional aggregation policies are deterministic and scheduled.
- Supported baseline report patterns:
  - daily bulletins
  - incident alerts
  - maintenance summaries
- Aggregation is budgeted (RS-5):
  - deterministic degrade via coarse summaries and section reduction
  - degrade decisions must be logged.

## E) Epistemic Contract

- Institutions only know artifacts they observe or receive via SIG receipt creation.
- Institutional reports do not imply omniscient truth.
- Acceptance of institutional reports uses trust edges (SIG-5), not privileged bypass.

## F) Event, Replay, and Proof

- Bulletin generation, dispatch updates, standards issuance, and compliance report publication must emit deterministic decision/provenance rows.
- Replay must reconstruct institutional outputs from the event stream plus policy registries.

## G) Integration Points

- SIG:
  - transport, addressing, aggregation, quality, security, trust
- CTRL:
  - ControlIntent/IR for dispatch schedule actions
- MOB:
  - timetable/schedule targets and congestion/incident input feeds
- SPEC:
  - compliance inputs and standards issuance outputs
- MAT:
  - provenance/event-sourced institutional outputs

## Non-Goals (SIG-6)

- No economy pricing or market-clearing behavior.
- No full political simulation.
- No wall-clock semantics.
- No nondeterministic institutional behavior.

## Constitutional Invariants

- A1 Determinism is primary.
- A2 Process-only mutation.
- A6 Provenance is mandatory.
- A7 Observer/Renderer/Truth separation.
- A10 Explicit degradation and refusal.
