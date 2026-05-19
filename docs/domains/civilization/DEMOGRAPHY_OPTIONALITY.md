Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Demography Optionality

## Scope
- CIV-4 introduces deterministic demographic scaffolding as a process family.
- Demography is policy-driven and can run in:
  - no-agent worlds
  - single-agent worlds
  - cohort-only worlds
  - micro-only worlds
  - mixed micro + cohort worlds

## Core Doctrine
- Demography mutation is process-only and deterministic.
- Primary process is `process.demography_tick`.
- Tick cadence is registry-driven (`demography_policy.tick_rate`).
- Birth/death rates are numeric model parameters, not hardcoded logic branches.

## Procreation Optionality
- Procreation is abstract and policy-governed.
- No explicit sex, pregnancy, or detailed biology simulation in CIV-4.
- Birth enablement is controlled by:
  - `LawProfile` process permissions and birth override controls
  - `demography_policy.births_enabled`
  - `ParameterBundle` numeric multipliers/caps

## No-Procreation Worlds
- If births are disabled by law or policy:
  - births are always zero
  - migration and assimilation remain available
  - population is fixed or declines per death tuning

## Procreation-Enabled Worlds
- If births are enabled by policy and not forbidden by law:
  - cohort births are deterministic rate-derived deltas
  - pairing semantics are abstracted and non-diegetic to CIV-4
  - no individual-level reproduction simulation is introduced

## Micro Agent Extension (Intentional Stub)
- CIV-4 does not simulate individual-level reproduction.
- If micro agents are currently expanded:
  - demography still mutates parent cohort aggregates
  - new individuals appear only on later deterministic cohort expansion
- This keeps macro and micro representations consistent without adding pregnancy/sex semantics.

## Determinism Requirements
- Cohorts are processed in stable order (`cohort_id` ascending).
- Rounding is deterministic (`floor` with fixed multiplier pipeline).
- Tie breaks use configured deterministic tie-break id.
- Demography outputs must be replay-stable across worker counts.

## Non-Goals
- No survival loop semantics (hunger/thirst/injury).
- No inventory/crafting/economy solvers.
- No explicit violence model.
