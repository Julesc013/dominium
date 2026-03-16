Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Unified Profile Override Architecture

Status: CANONICAL-DERIVED  
Version: 1.0.0  
Series: META-PROFILE-0

## Purpose
Replace all runtime mode semantics with explicit, composable profiles plus canonical exception ledger events.

No hidden mode flags are allowed in authoritative runtime behavior.

## Profile Types

1. `physics`
- Conservation enforcement
- Entropy policy
- Alternate physics pack routing

2. `law`
- Allowed actions/processes
- Mutation permissions
- Respawn/death policy

3. `process`
- Capsule eligibility
- QC strictness
- Drift thresholds

4. `safety`
- Mandatory interlocks
- Failure fallback severity

5. `epistemic`
- Visibility gates
- Instrumentation access bounds
- Debug scope bounds

6. `coupling`
- Coupling budget units
- Deterministic degrade priorities

7. `compute`
- Instruction/memory envelopes
- Logic/network compute ceilings

8. `topology`
- Universe topology identity
- Declared dimension and boundary behavior

9. `metric`
- Distance and geodesic policy
- Measure/tolerance policy for GEO queries

10. `partition`
- Field/world/ROI partition selection
- Stable cell-key derivation policy

11. `projection`
- Render/map/slice projection policy
- Lens-facing geometry projection defaults

## Deterministic Resolution Order
Effective profile resolution for a `rule_id` is strict and deterministic:

1. Universe baseline (`scope=universe`)
2. Session overlay (`scope=session`)
3. Authority overlay (`scope=authority`)
4. System overlay (`scope=system`)

Tie-break inside same scope:
1. `tick_applied` ascending
2. `binding_id` ascending
3. `profile_id` ascending

## Binding Points

- `UniverseIdentity`: immutable baseline profile bindings
- `SessionSpec`: session-level profile bindings
- `AuthorityContext`: authority overlays + effective profile snapshot
- `SystemTemplate`: optional profile constraints

## Exception Ledger Contract
If an overlay changes behavior relative to baseline for a governed `rule_id`, runtime must emit canonical `exception_event`:

- `profile_id`
- `rule_id`
- `owner_id`
- `tick`
- deterministic payload hash

Event emission must be deterministic, replayable, and policy-gated by law.

## No Mode Flags Rule
Forbidden behavior expression:
- hardcoded mode booleans/branches (for example legacy creative/debug/god tokens)

Required behavior expression:
- profile override row + deterministic resolution + exception event when baseline is overridden.

## Compatibility Strategy
- Existing fragmented registries remain valid.
- Unified profile registry acts as cross-cutting overlay layer.
- Missing overlay rows default to baseline or no-op (no implicit hidden default branch).

## Determinism Guarantees
- No wall-clock use.
- No unordered profile merges.
- Stable canonical hashing for profile artifacts and exception events.

## Refusal Semantics
Runtime refuses profile mutation/override when:
- referenced profile is missing
- override violates active law policy
- payload is schema-invalid

Refusals must include deterministic reason codes.
