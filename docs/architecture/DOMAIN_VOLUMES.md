# Domain Volumes (DOMAIN0)

Status: draft.
Scope: canonical spatial containers for simulation, travel, and law.

## Purpose
Define where reality exists and where it does not. Domain volumes encode
arbitrary spatial boundaries without hard-coded world boxes.

## Runtime Representation
The canonical runtime format is a Signed Distance Field (SDF):
- f(x,y,z) -> signed distance
- inside if f <= 0
- deterministic evaluation and budgetable queries

Authoring formats are baked into SDF deterministically; runtime does not depend
on meshes or splines.

## Domain Identity
Each domain has:
- domain_id
- existence_state (EXIST0)
- archival_state (EXIST2)
- parent_domain_id (optional)
- precedence for overlaps

Domains do not imply fidelity, authority, ownership, or activity.

## Integration Points
- Existence: inactive domains are not resolved.
- Refinement: domains may allow/forbid refinement.
- Law: jurisdictions attach to domains.
- Travel: travel edges reference domains.
- Sharding: ownership partitions by domain.
- Interest: sampling constrained by domains.

## Determinism and Budgets
Queries are deterministic and side-effect free. Budget pressure degrades
resolution without changing correctness.

## References
- `schema/domain/README.md`
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/SPACE_TIME_EXISTENCE.md`
