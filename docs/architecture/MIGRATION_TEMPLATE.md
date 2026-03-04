# Migration Template

Status: Canonical Template (ARCH-REF-1)
Version: 1.0.0

Use this template for every structural refactor/migration.

## 1) Overlapping Subsystem Identification
- Existing subsystem(s):
- Overlapping files/modules:
- Overlapping schema/contracts:
- Overlap risk summary:

## 2) Replacement Abstraction
- Target abstraction(s):
- Why replacement is canonical:
- Determinism/conservation implications:

## 3) Migration Steps
1. 
2. 
3. 

## 4) Backwards Compatibility Strategy
- Adapter/shim required: yes/no
- Compatibility window:
- Removal condition:

## 5) TestX Equivalence Cases
- Determinism equivalence tests:
- Refusal-path equivalence tests:
- Ledger/hash anchor checks:

## 6) RepoX Enforcement Additions
- New/updated invariants:
- Reintroduction prevention checks:

## 7) Deprecation Registry Entry
- `deprecated_id`:
- `replacement_id`:
- `reason`:
- `removal_target_version`:
- `status`:
