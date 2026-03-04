# Branching Timelines Policy

Status: CANONICAL  
Last Updated: 2026-03-04  
Scope: TEMP-0 branch lineage and replay authority policy.

## 1) Branching Model

Branching is explicit lineage fork:
- `branch_id`: unique branch lineage identifier
- `fork_tick`: canonical divergence tick
- `parent_branch_id` or parent save/checkpoint anchor
- new branch state is independent forward lineage

## 2) Authority Requirements

Every branch operation must declare:
- authority origin
- governing branch policy id
- lawful reason code

Branch operations without authority context are refused.

## 3) Proof Requirements

Branch creation must emit deterministic proof data:
- branch artifact with deterministic fingerprint
- lineage parent references
- fork tick and identity hash anchors
- decision/provenance log entries

## 4) Replay Contract

- replay within a branch must reproduce branch-local hashes deterministically.
- cross-branch comparisons must reference branch id + fork tick.
- branch replay does not mutate parent lineage truth.

## 5) Policy Registry

`data/registries/branch_policy_registry.json` defines baseline policy IDs:
- `branch.disabled`
- `branch.allowed_private`
- `branch.allowed_lab`
- `branch.forbidden_ranked`

## 6) Forbidden

- in-place canonical rewind/rewrite
- hidden branch creation without artifacts
- silent policy bypass for ranked/strict contexts
