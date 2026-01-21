# Invariant Registry

This registry indexes invariants referenced by code comments and CI checks.
It complements (does not replace) `docs/arch/INVARIANTS.md`.

## Rules
- IDs are stable and never reused.
- Each invariant maps to an authoritative spec and enforcement location.
- New invariants must be added here and to the relevant spec.

## Core Entries (Initial)

| ID | Description | Source | Enforcement |
| --- | --- | --- | --- |
| CODEHYGIENE-CAT-A | Architectural enums are closed-world; no CUSTOM/OTHER. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_forbidden_enums.py |
| CODEHYGIENE-CAT-B | Open-world taxonomies are registry IDs (data-driven). | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_switch_on_taxonomy.py |
| CODEHYGIENE-CAT-C | Magic numbers forbidden outside constants/data. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_magic_numbers.py |
| CODEHYGIENE-CAT-D | Derived data is deterministic and non-authoritative. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_hygiene_scan.py |

## Notes
- Full invariant list lives in `docs/arch/INVARIANTS.md`.
- Update this registry when adding enforcement checks or new invariant IDs.
