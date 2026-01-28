# Change Protocol (ARCH0 Binding)

This protocol is mandatory for any change that affects:
- Determinism
- Authoritative state
- Schema meaning
- Law semantics
- Execution model

## Required Artifacts
1. Written rationale (why the change is necessary).
2. Invariant impact analysis (what axioms/invariants are touched and why).
3. Migration plan (if any data or schema meaning changes).
4. Epoch bump (if sim-affecting).
5. CI rule update (new or adjusted enforcement check).

Missing any artifact is a refusal condition.

## Change Workflow
1. Define scope and classify impact (determinism, authority, schema, law, model).
2. Produce the required artifacts in the change set.
3. Update or add CI enforcement entries in `docs/ci/CI_ENFORCEMENT_MATRIX.md`.
4. Apply the epoch bump policy if the change is sim-affecting.
5. Review against ARCH0 axioms and refuse if any violation is unresolved.

## Epoch Bump Rule
Any sim-affecting change must bump the authoritative epoch identifier and
document compatibility implications. If no epoch policy exists yet, the change
must introduce one as part of the same change set.

## Refusal Conditions
Refuse changes that:
- Introduce nondeterminism in authoritative simulation.
- Bypass law/capability gates.
- Create or mutate state without provenance.
- Add silent fallbacks.
- Alter execution semantics without an epoch bump.

## Minimal Template
Use the following headings in change descriptions:
- Rationale
- Invariant Impact
- Migration Plan
- Epoch Bump
- CI Update
