Status: CANONICAL
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Process Registry

## Purpose
- Provide the authoritative inventory of process IDs that can mutate state.
- Make mutation boundaries auditable, deterministic, and enforceable.

## Registry Guarantees
- Every authoritative mutation path is represented by exactly one registry entry.
- Each entry declares:
  - Inputs and outputs (typed, named)
  - Affected assemblies and fields
  - Required law checks
  - RNG streams used (explicit list)
  - Determinism notes (ordering/tie-breaks)
  - Failure modes
  - Version introduced and deprecation flag
- Process IDs are stable and immutable once published.
- Unknown fields are preserved (extension-safe).

## Registry Forbids
- Mutation without a registered process ID.
- Reuse of a process ID for a different meaning.
- Implicit defaults for inputs, outputs, RNG streams, or law checks.
- Silent mutation outside declared affected assemblies/fields.

## Operational Requirements
- New authoritative processes must add a registry entry before use.
- Registry changes must remain compatible with existing IDs.
- Tests must validate registry coverage and deterministic contract execution for every registered process ID.

## Enforcement
- RepoX rejects unregistered process IDs and registry drift.
- RepoX rejects runtime process literals used in `engine`, `game`, `server`, and `client` when not present in the registry.
- RepoX rejects mutation token usage outside process execution allowlists.
- TestX validates registry completeness and deterministic process-contract execution signatures.
