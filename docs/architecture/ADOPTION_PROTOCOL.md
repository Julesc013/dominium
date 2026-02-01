Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# ADOPT0 Adoption Protocol

Status: binding, non-negotiable.
Scope: migration governance for all systems adopting Work IR / Access IR.

## Purpose
ADOPT0 defines the mandatory protocol for migrating legacy systems to the
execution substrate without big-bang rewrites or unsafe partial ports.

## Adoption Philosophy (Mandatory)

Adoption MUST be:
- Incremental
- Reversible until final cutover
- Test-driven
- System-by-system

At no point may:
- More than one major system migrate in a single prompt
- Engine and game layers be refactored simultaneously
- Performance optimization precede correctness parity

## System Migration States (Only Legal States)

1) LEGACY
   - Executes directly (pre-Work IR)
   - Allowed temporarily

2) DUAL
   - Emits Work IR while legacy path still exists
   - Outputs compared in deterministic parity tests

3) IR-ONLY
   - Legacy execution removed
   - Work IR path authoritative

Transitions:
- LEGACY -> DUAL -> IR-ONLY
- Skipping states is forbidden

## Required Migration Steps

Each system migration MUST follow these steps in order:

1) Identify system boundaries
   - Inputs, outputs, and state touched
2) Define AccessSets
   - Reads, writes, reductions
3) Emit Work IR
   - Stable task_id
   - Determinism class
   - Law targets
   - Cost model
4) Dual-run validation (when applicable)
   - Deterministic parity tests: legacy vs IR output
5) Remove legacy execution
   - Only after parity proven

## Forbidden Practices

You MUST NOT:
- Migrate multiple systems at once
- Mix correctness and optimization changes
- Add performance shortcuts during migration
- Weaken law or access enforcement to "get it working"
- Add hidden fallback paths

## Required Artifacts

Every migration PR MUST include:
- Declared migration state (LEGACY/DUAL/IR-ONLY)
- AccessSet definitions for all emitted tasks
- Work IR emission for authoritative work
- Deterministic parity tests for DUAL state
- CI enforcement updates (see `docs/ci/CI_ENFORCEMENT_MATRIX.md`)

## Enforcement

ADOPT0 is enforced through CI gates:
- ADOPT0-STATE-001
- ADOPT0-DUAL-002
- ADOPT0-BYPASS-003
- ADOPT0-ACCESS-004

See `docs/ci/CI_ENFORCEMENT_MATRIX.md` for enforcement details.