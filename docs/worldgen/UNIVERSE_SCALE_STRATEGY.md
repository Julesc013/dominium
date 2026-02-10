Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Universe Scale Strategy

Universe-scale data is represented lazily through index artifacts and deterministic refinement.

## Core Strategy

- Represent large-scale structures as indexed macro capsules.
- Refine only when regions enter an explicit interest set.
- Keep generation and refinement deterministic across thread counts.

## Hierarchical Scope

- Universe
- System
- Body
- Region
- Local module scope

## Refinement Triggers

- Interest set changes
- Camera focus shift
- Explicit refinement command

## Constraints

- No eager full-detail generation at universe creation.
- Collapse/expand operations preserve declared contracts.
- Refinement artifacts are reproducible from source data and seed.

