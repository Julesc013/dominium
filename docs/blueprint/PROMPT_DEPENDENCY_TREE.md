Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored execution graph after live repository mapping

# Prompt Dependency Tree

## Critical Path

- `Σ-0`
- `Σ-1`
- `Σ-2`
- `Σ-3`
- `Σ-5`
- `Φ-0`
- `Φ-1`
- `Φ-2`
- `Φ-3`
- `Φ-4`
- `Φ-5`
- `Φ-12`
- `Φ-13`
- `Φ-14`
- `Υ-0`
- `Υ-2`
- `Υ-3`
- `Υ-6`
- `Υ-10`
- `Υ-11`
- `Υ-12`
- `Ζ-10`
- `Ζ-14`
- `Ζ-16`
- `Ζ-18`
- `Ζ-24`
- `Ζ-27`
- `Ζ-28`
- `Ζ-29`
- `Ζ-30`
- `Ζ-33`
- `Ζ-44`
- `Ζ-57`
- `Ζ-58`
- `Ζ-59`
- `Ζ-60`
- `Ζ-62`
- `Ζ-63`
- `Ζ-68`
- `Ζ-73`

## Foundation Nodes

- `XI-8`: Repository Freeze Complete. Repository convergence, architecture freeze, and structure lock are complete enough to anchor post-XI planning.
- `OMEGA-FREEZE`: Omega Runtime Freeze. OMEGA verification baselines and distribution freeze artifacts exist and remain authoritative.
- `SNAPSHOT-MAP`: Snapshot Mapping Complete. A fresh repository snapshot has been mapped against the blueprint and reconciled before implementation planning proceeds.

## Dependency Edges

| From | To | Type |
| --- | --- | --- |
| Σ-0 | Σ-1 | depends_on |
| Σ-0 | Σ-2 | depends_on |
| Σ-0 | Σ-5 | depends_on |
| Σ-0 | Υ-12 | depends_on |
| Σ-1 | Σ-2 | depends_on |
| Σ-1 | Ζ-24 | depends_on |
| Σ-1 | Ζ-31 | depends_on |
| Σ-1 | Ζ-35 | depends_on |
| Σ-2 | Σ-3 | depends_on |
| Σ-2 | Σ-5 | depends_on |
| Σ-2 | Ζ-4 | depends_on |
| Σ-2 | Ζ-14 | depends_on |
| Σ-3 | Σ-4 | depends_on |
| Σ-3 | Σ-6 | depends_on |
| Σ-3 | Υ-4 | depends_on |
| Σ-3 | Υ-12 | depends_on |
| Σ-3 | Ζ-15 | depends_on |
| Σ-3 | Ζ-27 | depends_on |
| Σ-4 | Σ-5 | depends_on |
| Σ-4 | Σ-6 | depends_on |
| Σ-5 | Σ-6 | depends_on |
| Σ-5 | Φ-14 | depends_on |
| Σ-5 | Υ-10 | depends_on |
| Σ-5 | Ζ-6 | depends_on |
| Σ-5 | Ζ-10 | depends_on |
| Σ-5 | Ζ-12 | depends_on |
| Σ-5 | Ζ-16 | depends_on |
| Σ-5 | Ζ-17 | depends_on |
| Σ-5 | Ζ-18 | depends_on |
| Σ-5 | Ζ-19 | depends_on |
| Σ-5 | Ζ-20 | depends_on |
| Σ-5 | Ζ-21 | depends_on |
| Σ-5 | Ζ-22 | depends_on |
| Σ-5 | Ζ-23 | depends_on |
| Σ-5 | Ζ-32 | depends_on |
| Σ-5 | Ζ-44 | depends_on |
| Σ-5 | Ζ-50 | depends_on |
| Σ-5 | Ζ-65 | depends_on |
| Φ-0 | Φ-1 | depends_on |
| Φ-0 | Φ-4 | depends_on |
| Φ-1 | Φ-2 | depends_on |
| Φ-1 | Φ-3 | depends_on |
| Φ-1 | Φ-4 | depends_on |
| Φ-1 | Φ-6 | depends_on |
| Φ-1 | Φ-7 | depends_on |
| Φ-1 | Φ-9 | depends_on |
| Φ-1 | Φ-10 | depends_on |
| Φ-1 | Φ-11 | depends_on |
| Φ-2 | Φ-3 | depends_on |
| Φ-2 | Φ-10 | depends_on |
| Φ-2 | Ζ-2 | depends_on |
| Φ-2 | Ζ-20 | depends_on |
| Φ-2 | Ζ-44 | depends_on |
| Φ-2 | Ζ-49 | depends_on |
| Φ-2 | Ζ-52 | depends_on |
| Φ-3 | Φ-5 | depends_on |
| Φ-3 | Φ-6 | depends_on |
| Φ-3 | Φ-10 | depends_on |
| Φ-3 | Ζ-1 | depends_on |
| Φ-3 | Ζ-3 | depends_on |
| Φ-3 | Ζ-24 | depends_on |
| Φ-3 | Ζ-25 | depends_on |
| Φ-3 | Ζ-42 | depends_on |
| Φ-3 | Ζ-61 | depends_on |
| Φ-4 | Φ-5 | depends_on |
| Φ-4 | Φ-11 | depends_on |
| Φ-4 | Φ-12 | depends_on |
| Φ-4 | Φ-13 | depends_on |
| Φ-4 | Ζ-5 | depends_on |
| Φ-4 | Ζ-7 | depends_on |
| Φ-5 | Φ-8 | depends_on |
| Φ-5 | Φ-12 | depends_on |
| Φ-5 | Φ-13 | depends_on |
| Φ-5 | Ζ-0 | depends_on |
| Φ-5 | Ζ-1 | depends_on |
| Φ-5 | Ζ-2 | depends_on |
| Φ-5 | Ζ-3 | depends_on |
| Φ-5 | Ζ-4 | depends_on |
| Φ-5 | Ζ-7 | depends_on |
| Φ-5 | Ζ-11 | depends_on |
| Φ-5 | Ζ-48 | depends_on |
| Φ-6 | Φ-7 | depends_on |
| Φ-6 | Φ-8 | depends_on |
| Φ-6 | Φ-9 | depends_on |
| Φ-6 | Ζ-0 | depends_on |
| Φ-6 | Ζ-33 | depends_on |
| Φ-6 | Ζ-34 | depends_on |
| Φ-6 | Ζ-37 | depends_on |
| Φ-7 | Φ-8 | depends_on |
| Φ-7 | Ζ-0 | depends_on |
| Φ-7 | Ζ-33 | depends_on |
| Φ-7 | Ζ-34 | depends_on |
| Φ-7 | Ζ-38 | depends_on |
| Φ-7 | Ζ-40 | depends_on |
| Φ-7 | Ζ-41 | depends_on |
| Φ-7 | Ζ-42 | depends_on |
| Φ-8 | Ζ-0 | depends_on |
| Φ-8 | Ζ-2 | depends_on |
| Φ-8 | Ζ-3 | depends_on |
| Φ-8 | Ζ-4 | depends_on |
| Φ-8 | Ζ-37 | depends_on |
| Φ-9 | Ζ-34 | depends_on |
| Φ-9 | Ζ-40 | depends_on |
| Φ-9 | Ζ-41 | depends_on |
| Φ-9 | Ζ-48 | depends_on |
| Φ-10 | Ζ-20 | depends_on |
| Φ-10 | Ζ-45 | depends_on |
| Φ-11 | Φ-14 | depends_on |
| Φ-11 | Ζ-2 | depends_on |
| Φ-11 | Ζ-6 | depends_on |
| Φ-11 | Ζ-44 | depends_on |
| Φ-11 | Ζ-47 | depends_on |
| Φ-11 | Ζ-49 | depends_on |
| Φ-11 | Ζ-52 | depends_on |
| Φ-11 | Ζ-56 | depends_on |
| Φ-12 | Φ-13 | depends_on |
| Φ-12 | Φ-14 | depends_on |
| Φ-12 | Ζ-29 | depends_on |
| Φ-12 | Ζ-30 | depends_on |
| Φ-12 | Ζ-57 | depends_on |
| Φ-12 | Ζ-60 | depends_on |
| Φ-13 | Φ-14 | depends_on |
| Φ-13 | Ζ-5 | depends_on |
| Φ-13 | Ζ-7 | depends_on |
| Φ-13 | Ζ-9 | depends_on |
| Φ-13 | Ζ-29 | depends_on |
| Φ-13 | Ζ-39 | depends_on |
| Φ-13 | Ζ-57 | depends_on |
| Φ-13 | Ζ-59 | depends_on |
| Φ-13 | Ζ-60 | depends_on |
| Φ-14 | Ζ-57 | depends_on |
| Φ-14 | Ζ-58 | depends_on |
| Φ-14 | Ζ-63 | depends_on |
| Φ-14 | Ζ-73 | depends_on |
| Υ-0 | Υ-1 | depends_on |
| Υ-0 | Υ-4 | depends_on |
| Υ-0 | Υ-5 | depends_on |
| Υ-0 | Ζ-28 | depends_on |
| Υ-1 | Υ-5 | depends_on |
| Υ-2 | Υ-3 | depends_on |
| Υ-2 | Υ-8 | depends_on |
| Υ-2 | Υ-11 | depends_on |
| Υ-2 | Υ-12 | depends_on |
| Υ-3 | Υ-6 | depends_on |
| Υ-3 | Υ-7 | depends_on |
| Υ-3 | Υ-8 | depends_on |
| Υ-4 | Υ-6 | depends_on |
| Υ-5 | Υ-6 | depends_on |
| Υ-5 | Ζ-34 | depends_on |
| Υ-6 | Υ-7 | depends_on |
| Υ-6 | Υ-10 | depends_on |
| Υ-7 | Υ-10 | depends_on |
| Υ-8 | Υ-9 | depends_on |
| Υ-8 | Υ-10 | depends_on |
| Υ-9 | Ζ-18 | depends_on |
| Υ-9 | Ζ-20 | depends_on |
| Υ-9 | Ζ-22 | depends_on |
| Υ-9 | Ζ-45 | depends_on |
| Υ-9 | Ζ-51 | depends_on |
| Υ-10 | Ζ-10 | depends_on |
| Υ-10 | Ζ-15 | depends_on |
| Υ-10 | Ζ-16 | depends_on |
| Υ-10 | Ζ-18 | depends_on |
| Υ-10 | Ζ-23 | depends_on |
| Υ-10 | Ζ-24 | depends_on |
| Υ-10 | Ζ-27 | depends_on |
| Υ-10 | Ζ-32 | depends_on |
| Υ-10 | Ζ-42 | depends_on |
| Υ-10 | Ζ-44 | depends_on |
| Υ-10 | Ζ-50 | depends_on |
| Υ-10 | Ζ-53 | depends_on |
| Υ-10 | Ζ-54 | depends_on |
| Υ-10 | Ζ-74 | depends_on |
| Υ-11 | Υ-10 | depends_on |
| Υ-11 | Ζ-5 | depends_on |
| Υ-11 | Ζ-10 | depends_on |
| Υ-11 | Ζ-12 | depends_on |
| Υ-11 | Ζ-43 | depends_on |
| Υ-11 | Ζ-46 | depends_on |
| Υ-11 | Ζ-62 | depends_on |
| Υ-11 | Ζ-69 | depends_on |
| Υ-11 | Ζ-70 | depends_on |
| Υ-11 | Ζ-71 | depends_on |
| Υ-11 | Ζ-74 | depends_on |
| Υ-12 | Υ-10 | depends_on |
| Υ-12 | Υ-11 | depends_on |
| Υ-12 | Ζ-0 | depends_on |
| Υ-12 | Ζ-1 | depends_on |
| Υ-12 | Ζ-2 | depends_on |
| Υ-12 | Ζ-3 | depends_on |
| Υ-12 | Ζ-4 | depends_on |
| Υ-12 | Ζ-5 | depends_on |
| Υ-12 | Ζ-9 | depends_on |
| Υ-12 | Ζ-10 | depends_on |
| Υ-12 | Ζ-11 | depends_on |
| Υ-12 | Ζ-13 | depends_on |
| Υ-12 | Ζ-14 | depends_on |
| Υ-12 | Ζ-16 | depends_on |
| Υ-12 | Ζ-28 | depends_on |
| Υ-12 | Ζ-30 | depends_on |
| Υ-12 | Ζ-46 | depends_on |
| Υ-12 | Ζ-56 | depends_on |
| Υ-12 | Ζ-57 | depends_on |
| Υ-12 | Ζ-74 | depends_on |
| Ζ-0 | Ζ-33 | depends_on |
| Ζ-0 | Ζ-37 | depends_on |
| Ζ-0 | Ζ-38 | depends_on |
| Ζ-0 | Ζ-40 | depends_on |
| Ζ-1 | Ζ-21 | depends_on |
| Ζ-5 | Ζ-6 | depends_on |
| Ζ-5 | Ζ-8 | depends_on |
| Ζ-7 | Ζ-8 | depends_on |
| Ζ-7 | Ζ-9 | depends_on |
| Ζ-10 | Ζ-11 | depends_on |
| Ζ-10 | Ζ-13 | depends_on |
| Ζ-10 | Ζ-55 | depends_on |
| Ζ-14 | Ζ-15 | depends_on |
| Ζ-14 | Ζ-26 | depends_on |
| Ζ-16 | Ζ-17 | depends_on |
| Ζ-17 | Ζ-19 | depends_on |
| Ζ-18 | Ζ-19 | depends_on |
| Ζ-18 | Ζ-21 | depends_on |
| Ζ-18 | Ζ-22 | depends_on |
| Ζ-18 | Ζ-51 | depends_on |
| Ζ-24 | Ζ-25 | depends_on |
| Ζ-24 | Ζ-26 | depends_on |
| Ζ-24 | Ζ-31 | depends_on |
| Ζ-24 | Ζ-58 | depends_on |
| Ζ-27 | Ζ-28 | depends_on |
| Ζ-27 | Ζ-29 | depends_on |
| Ζ-27 | Ζ-31 | depends_on |
| Ζ-27 | Ζ-32 | depends_on |
| Ζ-27 | Ζ-57 | depends_on |
| Ζ-28 | Ζ-32 | depends_on |
| Ζ-29 | Ζ-73 | depends_on |
| Ζ-30 | Ζ-68 | depends_on |
| Ζ-33 | Ζ-35 | depends_on |
| Ζ-33 | Ζ-36 | depends_on |
| Ζ-33 | Ζ-37 | depends_on |
| Ζ-33 | Ζ-42 | depends_on |
| Ζ-34 | Ζ-35 | depends_on |
| Ζ-34 | Ζ-36 | depends_on |
| Ζ-34 | Ζ-43 | depends_on |
| Ζ-37 | Ζ-38 | depends_on |
| Ζ-37 | Ζ-39 | depends_on |
| Ζ-42 | Ζ-43 | depends_on |
| Ζ-44 | Ζ-45 | depends_on |
| Ζ-44 | Ζ-47 | depends_on |
| Ζ-44 | Ζ-48 | depends_on |
| Ζ-44 | Ζ-50 | depends_on |
| Ζ-44 | Ζ-53 | depends_on |
| Ζ-44 | Ζ-54 | depends_on |
| Ζ-45 | Ζ-46 | depends_on |
| Ζ-45 | Ζ-49 | depends_on |
| Ζ-45 | Ζ-51 | depends_on |
| Ζ-45 | Ζ-52 | depends_on |
| Ζ-45 | Ζ-56 | depends_on |
| Ζ-50 | Ζ-55 | depends_on |
| Ζ-54 | Ζ-55 | depends_on |
| Ζ-57 | Ζ-58 | depends_on |
| Ζ-57 | Ζ-59 | depends_on |
| Ζ-57 | Ζ-60 | depends_on |
| Ζ-57 | Ζ-61 | depends_on |
| Ζ-57 | Ζ-62 | depends_on |
| Ζ-57 | Ζ-63 | depends_on |
| Ζ-57 | Ζ-64 | depends_on |
| Ζ-57 | Ζ-65 | depends_on |
| Ζ-57 | Ζ-68 | depends_on |
| Ζ-57 | Ζ-69 | depends_on |
| Ζ-57 | Ζ-70 | depends_on |
| Ζ-57 | Ζ-72 | depends_on |
| Ζ-57 | Ζ-73 | depends_on |
| Ζ-57 | Ζ-74 | depends_on |
| Ζ-58 | Ζ-59 | depends_on |
| Ζ-58 | Ζ-67 | depends_on |
| Ζ-59 | Ζ-66 | depends_on |
| Ζ-60 | Ζ-62 | depends_on |
| Ζ-60 | Ζ-68 | depends_on |
| Ζ-61 | Ζ-67 | depends_on |
| Ζ-62 | Ζ-69 | depends_on |
| Ζ-62 | Ζ-71 | depends_on |
| Ζ-63 | Ζ-62 | depends_on |
| Ζ-63 | Ζ-64 | depends_on |
| Ζ-63 | Ζ-65 | depends_on |
| Ζ-63 | Ζ-70 | depends_on |
| Ζ-64 | Ζ-66 | depends_on |
| Ζ-66 | Ζ-67 | depends_on |
| Ζ-68 | Ζ-72 | depends_on |
| Ζ-70 | Ζ-71 | depends_on |
| Ζ-70 | Ζ-72 | depends_on |
| OMEGA-FREEZE | Σ-0 | depends_on |
| OMEGA-FREEZE | Φ-0 | depends_on |
| OMEGA-FREEZE | Υ-0 | depends_on |
| OMEGA-FREEZE | Υ-2 | depends_on |
| OMEGA-FREEZE | Υ-11 | depends_on |
| OMEGA-FREEZE | Ζ-5 | depends_on |
| OMEGA-FREEZE | Ζ-12 | depends_on |
| OMEGA-FREEZE | Ζ-16 | depends_on |
| OMEGA-FREEZE | Ζ-27 | depends_on |
| OMEGA-FREEZE | Ζ-30 | depends_on |
| OMEGA-FREEZE | Ζ-57 | depends_on |
| SNAPSHOT-MAP | Σ-6 | depends_on |
| SNAPSHOT-MAP | Φ-2 | depends_on |
| SNAPSHOT-MAP | Φ-3 | depends_on |
| SNAPSHOT-MAP | Φ-5 | depends_on |
| SNAPSHOT-MAP | Φ-6 | depends_on |
| SNAPSHOT-MAP | Φ-7 | depends_on |
| SNAPSHOT-MAP | Φ-8 | depends_on |
| SNAPSHOT-MAP | Φ-9 | depends_on |
| SNAPSHOT-MAP | Φ-10 | depends_on |
| SNAPSHOT-MAP | Φ-12 | depends_on |
| SNAPSHOT-MAP | Φ-13 | depends_on |
| SNAPSHOT-MAP | Φ-14 | depends_on |
| SNAPSHOT-MAP | Υ-0 | depends_on |
| SNAPSHOT-MAP | Υ-1 | depends_on |
| SNAPSHOT-MAP | Υ-4 | depends_on |
| SNAPSHOT-MAP | Υ-5 | depends_on |
| SNAPSHOT-MAP | Υ-6 | depends_on |
| SNAPSHOT-MAP | Υ-7 | depends_on |
| SNAPSHOT-MAP | Υ-10 | depends_on |
| SNAPSHOT-MAP | Ζ-0 | depends_on |
| SNAPSHOT-MAP | Ζ-1 | depends_on |
| SNAPSHOT-MAP | Ζ-2 | depends_on |
| SNAPSHOT-MAP | Ζ-3 | depends_on |
| SNAPSHOT-MAP | Ζ-4 | depends_on |
| SNAPSHOT-MAP | Ζ-5 | depends_on |
| SNAPSHOT-MAP | Ζ-6 | depends_on |
| SNAPSHOT-MAP | Ζ-7 | depends_on |
| SNAPSHOT-MAP | Ζ-8 | depends_on |
| SNAPSHOT-MAP | Ζ-9 | depends_on |
| SNAPSHOT-MAP | Ζ-10 | depends_on |
| SNAPSHOT-MAP | Ζ-11 | depends_on |
| SNAPSHOT-MAP | Ζ-12 | depends_on |
| SNAPSHOT-MAP | Ζ-13 | depends_on |
| SNAPSHOT-MAP | Ζ-14 | depends_on |
| SNAPSHOT-MAP | Ζ-15 | depends_on |
| SNAPSHOT-MAP | Ζ-16 | depends_on |
| SNAPSHOT-MAP | Ζ-17 | depends_on |
| SNAPSHOT-MAP | Ζ-18 | depends_on |
| SNAPSHOT-MAP | Ζ-19 | depends_on |
| SNAPSHOT-MAP | Ζ-20 | depends_on |
| SNAPSHOT-MAP | Ζ-21 | depends_on |
| SNAPSHOT-MAP | Ζ-22 | depends_on |
| SNAPSHOT-MAP | Ζ-23 | depends_on |
| SNAPSHOT-MAP | Ζ-24 | depends_on |
| SNAPSHOT-MAP | Ζ-25 | depends_on |
| SNAPSHOT-MAP | Ζ-26 | depends_on |
| SNAPSHOT-MAP | Ζ-27 | depends_on |
| SNAPSHOT-MAP | Ζ-28 | depends_on |
| SNAPSHOT-MAP | Ζ-29 | depends_on |
| SNAPSHOT-MAP | Ζ-30 | depends_on |
| SNAPSHOT-MAP | Ζ-31 | depends_on |
| SNAPSHOT-MAP | Ζ-32 | depends_on |
| SNAPSHOT-MAP | Ζ-33 | depends_on |
| SNAPSHOT-MAP | Ζ-34 | depends_on |
| SNAPSHOT-MAP | Ζ-35 | depends_on |
| SNAPSHOT-MAP | Ζ-36 | depends_on |
| SNAPSHOT-MAP | Ζ-37 | depends_on |
| SNAPSHOT-MAP | Ζ-38 | depends_on |
| SNAPSHOT-MAP | Ζ-39 | depends_on |
| SNAPSHOT-MAP | Ζ-40 | depends_on |
| SNAPSHOT-MAP | Ζ-41 | depends_on |
| SNAPSHOT-MAP | Ζ-42 | depends_on |
| SNAPSHOT-MAP | Ζ-43 | depends_on |
| SNAPSHOT-MAP | Ζ-44 | depends_on |
| SNAPSHOT-MAP | Ζ-45 | depends_on |
| SNAPSHOT-MAP | Ζ-46 | depends_on |
| SNAPSHOT-MAP | Ζ-47 | depends_on |
| SNAPSHOT-MAP | Ζ-48 | depends_on |
| SNAPSHOT-MAP | Ζ-49 | depends_on |
| SNAPSHOT-MAP | Ζ-50 | depends_on |
| SNAPSHOT-MAP | Ζ-51 | depends_on |
| SNAPSHOT-MAP | Ζ-52 | depends_on |
| SNAPSHOT-MAP | Ζ-53 | depends_on |
| SNAPSHOT-MAP | Ζ-54 | depends_on |
| SNAPSHOT-MAP | Ζ-55 | depends_on |
| SNAPSHOT-MAP | Ζ-56 | depends_on |
| SNAPSHOT-MAP | Ζ-57 | depends_on |
| SNAPSHOT-MAP | Ζ-58 | depends_on |
| SNAPSHOT-MAP | Ζ-59 | depends_on |
| SNAPSHOT-MAP | Ζ-60 | depends_on |
| SNAPSHOT-MAP | Ζ-61 | depends_on |
| SNAPSHOT-MAP | Ζ-62 | depends_on |
| SNAPSHOT-MAP | Ζ-63 | depends_on |
| SNAPSHOT-MAP | Ζ-64 | depends_on |
| SNAPSHOT-MAP | Ζ-65 | depends_on |
| SNAPSHOT-MAP | Ζ-66 | depends_on |
| SNAPSHOT-MAP | Ζ-67 | depends_on |
| SNAPSHOT-MAP | Ζ-68 | depends_on |
| SNAPSHOT-MAP | Ζ-69 | depends_on |
| SNAPSHOT-MAP | Ζ-70 | depends_on |
| SNAPSHOT-MAP | Ζ-71 | depends_on |
| SNAPSHOT-MAP | Ζ-72 | depends_on |
| SNAPSHOT-MAP | Ζ-73 | depends_on |
| SNAPSHOT-MAP | Ζ-74 | depends_on |
| XI-8 | Σ-0 | depends_on |
| XI-8 | Φ-0 | depends_on |
| XI-8 | Υ-0 | depends_on |
| XI-8 | Υ-2 | depends_on |

## Parallelizable Prompts

- `Σ-6`
- `Υ-4`
- `Υ-5`
- `Υ-8`
- `Ζ-15`
- `Ζ-25`
- `Ζ-26`
- `Ζ-31`
- `Ζ-54`

## Should Never Run Before Snapshot Mapping

- `Σ-6`
- `Φ-2`
- `Φ-3`
- `Φ-5`
- `Φ-6`
- `Φ-7`
- `Φ-8`
- `Φ-9`
- `Φ-10`
- `Φ-12`
- `Φ-13`
- `Φ-14`
- `Υ-0`
- `Υ-1`
- `Υ-4`
- `Υ-5`
- `Υ-6`
- `Υ-7`
- `Υ-10`
- `Ζ-0`
- `Ζ-1`
- `Ζ-2`
- `Ζ-3`
- `Ζ-4`
- `Ζ-5`
- `Ζ-6`
- `Ζ-7`
- `Ζ-8`
- `Ζ-9`
- `Ζ-10`
- `Ζ-11`
- `Ζ-12`
- `Ζ-13`
- `Ζ-14`
- `Ζ-15`
- `Ζ-16`
- `Ζ-17`
- `Ζ-18`
- `Ζ-19`
- `Ζ-20`
- `Ζ-21`
- `Ζ-22`
- `Ζ-23`
- `Ζ-24`
- `Ζ-25`
- `Ζ-26`
- `Ζ-27`
- `Ζ-28`
- `Ζ-29`
- `Ζ-30`
- `Ζ-31`
- `Ζ-32`
- `Ζ-33`
- `Ζ-34`
- `Ζ-35`
- `Ζ-36`
- `Ζ-37`
- `Ζ-38`
- `Ζ-39`
- `Ζ-40`
- `Ζ-41`
- `Ζ-42`
- `Ζ-43`
- `Ζ-44`
- `Ζ-45`
- `Ζ-46`
- `Ζ-47`
- `Ζ-48`
- `Ζ-49`
- `Ζ-50`
- `Ζ-51`
- `Ζ-52`
- `Ζ-53`
- `Ζ-54`
- `Ζ-55`
- `Ζ-56`
- `Ζ-57`
- `Ζ-58`
- `Ζ-59`
- `Ζ-60`
- `Ζ-61`
- `Ζ-62`
- `Ζ-63`
- `Ζ-64`
- `Ζ-65`
- `Ζ-66`
- `Ζ-67`
- `Ζ-68`
- `Ζ-69`
- `Ζ-70`
- `Ζ-71`
- `Ζ-72`
- `Ζ-73`
- `Ζ-74`
