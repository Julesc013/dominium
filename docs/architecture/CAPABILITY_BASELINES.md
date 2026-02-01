Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Capability Baselines (CAPBASE0)





Status: binding.


Scope: baseline capability sets for compatibility and SKUs.





## Baselines (locked identifiers)


- BASELINE_LEGACY_CORE (C89/C++98)


- BASELINE_MAINLINE_CORE (future C17/C++17)


- BASELINE_MODERN_UI


- BASELINE_SERVER_MIN





## Rules


- Content targets capabilities, not engine versions.


- Baselines are additive and versioned.


- Missing capabilities must yield explicit degraded/frozen modes.


- Unknown capabilities are preserved and ignored safely.





## Schema


- `schema/capability_baseline.schema`





## See also


- `docs/architecture/SKU_MATRIX.md`


- `docs/architecture/REFUSAL_SEMANTICS.md`
